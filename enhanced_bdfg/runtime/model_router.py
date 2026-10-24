"""Route assistant completions to local Ollama or cloud providers."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from enhanced_bdfg.runtime.http_util import http_json
from enhanced_bdfg.runtime.secrets import load_secrets
from enhanced_bdfg.runtime.serial import local_model_lock

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")


class ModelRouter:
    """Local Ollama + OpenAI-compatible + Anthropic + Gemini."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        self.settings = settings or {}
        secrets = load_secrets()
        self.backend = (self.settings.get("backend") or secrets.get("backend") or "local").lower()
        self.local_only = bool(self.settings.get("local_only"))
        self.local_model = self.settings.get("local_model") or ("" if self.local_only else secrets.get("local_model") or "")
        self.openai_key = secrets.get("openai_api_key") or ""
        self.openai_base = (secrets.get("openai_base_url") or "https://api.openai.com/v1").rstrip("/")
        self.openai_model = secrets.get("openai_model") or "gpt-4o-mini"
        self.anthropic_key = secrets.get("anthropic_api_key") or ""
        self.anthropic_model = secrets.get("anthropic_model") or "claude-3-5-haiku-latest"
        self.gemini_key = secrets.get("gemini_api_key") or ""
        self.gemini_model = secrets.get("gemini_model") or "gemini-2.0-flash"

    @classmethod
    def from_assistant_settings(cls, settings: Optional[Dict[str, Any]] = None) -> "ModelRouter":
        return cls(settings or {})

    def configured_backends(self) -> List[str]:
        out = []
        if self.local_model or self.backend == "local":
            out.append("local")
        if self.openai_key:
            out.append("openai")
        if self.anthropic_key:
            out.append("anthropic")
        if self.gemini_key:
            out.append("gemini")
        return out

    def complete(
        self,
        messages: List[Dict[str, str]],
        *,
        backend: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.4,
        timeout: float = 180.0,
    ) -> Optional[str]:
        if os.environ.get("BDFG_DISABLE_LLM") == "1":
            return None
        if self.local_only and not backend:
            order = ["local"]
        else:
            order = []
            chosen = (backend or self.backend or "local").lower()
            order.append(chosen)
            for name in ("local", "openai", "anthropic", "gemini"):
                if name not in order:
                    order.append(name)
        last_error = None
        for name in order:
            try:
                text = self._complete_one(name, messages, model=model, temperature=temperature, timeout=timeout)
                if text:
                    return text.strip()
            except Exception as exc:
                last_error = exc
                logger.info("backend %s failed: %s", name, exc)
        if last_error:
            logger.warning("All LLM backends failed: %s", last_error)
        return None

    def _complete_one(
        self,
        name: str,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: float,
        timeout: float,
    ) -> Optional[str]:
        if name == "local":
            tag = model or self.local_model
            if not tag:
                from enhanced_bdfg.runtime.bootstrap import get_bootstrapper

                tag = get_bootstrapper().load_state().get("model") or ""
            if not tag:
                return None
            return self._ollama(messages, tag, temperature, timeout)
        if name == "openai":
            if not self.openai_key:
                return None
            return self._openai(messages, model or self.openai_model, temperature, timeout)
        if name == "anthropic":
            if not self.anthropic_key:
                return None
            return self._anthropic(messages, model or self.anthropic_model, temperature, timeout)
        if name == "gemini":
            if not self.gemini_key:
                return None
            return self._gemini(messages, model or self.gemini_model, temperature, timeout)
        return None

    def _ollama(self, messages, model: str, temperature: float, timeout: float) -> Optional[str]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        with local_model_lock():
            status, body = http_json(
                f"{OLLAMA_HOST}/api/chat",
                method="POST",
                payload=payload,
                timeout=timeout,
            )
        if status >= 400:
            raise RuntimeError(f"Ollama HTTP {status}: {body}")
        if isinstance(body, dict):
            msg = body.get("message") or {}
            return msg.get("content") or body.get("response")
        return None

    def _openai(self, messages, model: str, temperature: float, timeout: float) -> Optional[str]:
        status, body = http_json(
            f"{self.openai_base}/chat/completions",
            method="POST",
            payload={"model": model, "messages": messages, "temperature": temperature},
            headers={"Authorization": f"Bearer {self.openai_key}"},
            timeout=timeout,
        )
        if status >= 400:
            raise RuntimeError(f"OpenAI HTTP {status}")
        if isinstance(body, dict):
            choices = body.get("choices") or []
            if choices:
                return (choices[0].get("message") or {}).get("content")
        return None

    def _anthropic(self, messages, model: str, temperature: float, timeout: float) -> Optional[str]:
        system = "\n".join(m["content"] for m in messages if m.get("role") == "system")
        conv = [{"role": m["role"], "content": m["content"]} for m in messages if m.get("role") != "system"]
        status, body = http_json(
            "https://api.anthropic.com/v1/messages",
            method="POST",
            payload={
                "model": model,
                "max_tokens": 1024,
                "temperature": temperature,
                "system": system or "You are a helpful business assistant.",
                "messages": conv,
            },
            headers={
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=timeout,
        )
        if status >= 400:
            raise RuntimeError(f"Anthropic HTTP {status}")
        if isinstance(body, dict):
            parts = body.get("content") or []
            texts = [p.get("text") for p in parts if isinstance(p, dict) and p.get("text")]
            return "\n".join(texts) if texts else None
        return None

    def _gemini(self, messages, model: str, temperature: float, timeout: float) -> Optional[str]:
        contents = []
        system = ""
        for m in messages:
            role = m.get("role")
            if role == "system":
                system += m.get("content") or ""
                continue
            contents.append(
                {
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": m.get("content") or ""}],
                }
            )
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self.gemini_key}"
        )
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        status, body = http_json(url, method="POST", payload=payload, timeout=timeout)
        if status >= 400:
            raise RuntimeError(f"Gemini HTTP {status}")
        if isinstance(body, dict):
            cands = body.get("candidates") or []
            if cands:
                parts = ((cands[0].get("content") or {}).get("parts")) or []
                return "".join(p.get("text") or "" for p in parts)
        return None


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort JSON object from a model reply."""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    chunk = text[start : end + 1]
    try:
        data = json.loads(chunk)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None

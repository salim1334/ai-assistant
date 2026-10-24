"""API keys stored locally (never logged, never committed)."""

from __future__ import annotations

import json
import logging
import os
import stat
from typing import Any, Dict, Optional

from enhanced_bdfg.runtime.paths import secrets_path

logger = logging.getLogger(__name__)

EMPTY = {
    "openai_api_key": "",
    "openai_base_url": "",
    "openai_model": "gpt-4o-mini",
    "anthropic_api_key": "",
    "anthropic_model": "claude-3-5-haiku-latest",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
}


def load_secrets() -> Dict[str, Any]:
    path = secrets_path()
    data = dict(EMPTY)
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update({k: v for k, v in loaded.items() if v is not None})
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not read secrets file: %s", exc)
    # Env vars win when the file is empty for that key
    env_map = {
        "openai_api_key": "OPENAI_API_KEY",
        "openai_base_url": "OPENAI_BASE_URL",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
    }
    for field, env_name in env_map.items():
        if not data.get(field):
            data[field] = os.environ.get(env_name, "") or ""
    return data


def save_secrets(updates: Dict[str, Any]) -> Dict[str, Any]:
    current = load_secrets()
    for key, value in updates.items():
        if key in EMPTY or key.endswith("_api_key") or key.endswith("_model") or key.endswith("_url"):
            current[key] = value if value is not None else ""
    path = secrets_path()
    path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return current


def redacted(secrets: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = dict(secrets or load_secrets())
    out: Dict[str, Any] = {}
    for key, value in data.items():
        if "key" in key and value:
            out[key] = f"...{str(value)[-4:]}" if len(str(value)) >= 4 else "(set)"
        else:
            out[key] = value
    return out

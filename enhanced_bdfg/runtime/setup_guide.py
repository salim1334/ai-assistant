"""First-run setup interview. The script is the voice; the small model does not speak."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from enhanced_bdfg.runtime.model_router import ModelRouter

logger = logging.getLogger(__name__)

STEPS = ("name", "description", "goal", "language", "confirm", "done")

_DISTRIBUTION = re.compile(
    r"\b(kiosk|kiosks|fmcg|distributor|distributors)\b|distribut\w+\s+.{0,40}\b(shops?|kiosks?)\b",
    re.I,
)
_YES = re.compile(
    r"^\s*(yes|yep|yeah|y|ok|okay|correct|right|looks good|that's right|thats right|sounds good|አዎ|awo)\s*[.!]*\s*$",
    re.I,
)
_NAME_PREFIX = re.compile(
    r"^(?:the\s+)?(?:name\s+of\s+(?:my\s+)?(?:business|company)\s+is|my\s+(?:business|company)\s+is|i(?:'m| am))\s+",
    re.I,
)
_GOAL_PREFIX = re.compile(
    r"^(?:my\s+)?(?:main\s+)?(?:goal|i want to|i'd like to|we need to|help me)\s*(?:is\s+to|to)?\s*",
    re.I,
)
_METHOD = re.compile(
    r"\s+using\s+the\s+best\s+resources\b.*$|\s+use\s+(?:the\s+)?best\s+resources\b.*$",
    re.I,
)


def local_setup_router(model: str = "") -> ModelRouter:
    """Local model for later chat. Setup does not call it."""
    return ModelRouter({"backend": "local", "local_model": model or "", "local_only": True})


class SetupGuide:
    def __init__(self, router: Optional[ModelRouter] = None, language: str = "en"):
        self.router = router or ModelRouter.from_assistant_settings({"backend": "local"})
        self.language = language if language in ("en", "am") else "en"
        self.turns: List[Dict[str, str]] = []
        self.step = "name"
        self.language_chosen = False
        self.profile: Dict[str, Any] = {
            "name": "",
            "description": "",
            "industry": "general",
            "goals": [],
            "language": self.language,
            "facts": [],
        }

    def chat(self, user_text: str) -> Dict[str, Any]:
        user_text = (user_text or "").strip()
        if not user_text and self.step == "name" and not self.turns:
            reply = self._prompt_for("name")
            self.turns.append({"role": "assistant", "content": reply})
            return {"reply": reply, "profile": dict(self.profile), "complete": False}

        if user_text:
            self.turns.append({"role": "user", "content": user_text})
            self._absorb(user_text)

        reply = self._next_reply()
        self.turns.append({"role": "assistant", "content": reply})
        complete = self.step == "done"
        return {"reply": reply, "profile": dict(self.profile), "complete": complete}

    def _absorb(self, text: str) -> None:
        self._note_language(text)
        self._note_industry(text)
        step = self.step
        if step == "name":
            name = self._parse_name(text)
            if name:
                self.profile["name"] = name
            self.step = "description"
        elif step == "description":
            self.profile["description"] = text.strip()[:400]
            self.step = "goal"
        elif step == "goal":
            goal, fact = self._parse_goal(text)
            if goal and goal not in self.profile["goals"]:
                self.profile["goals"] = [goal]
            if fact and fact not in self.profile["facts"]:
                self.profile["facts"].append(fact)
            self.step = "confirm" if self.language_chosen else "language"
        elif step == "language":
            self._note_language(text, force=True)
            self.step = "confirm"
        elif step == "confirm":
            if _YES.match(text):
                self.step = "done"
            else:
                self.step = "name"
                if _NAME_PREFIX.match(text.strip()):
                    name = self._parse_name(text)
                    if name:
                        self.profile["name"] = name
                        self.step = "description"
        elif step == "done":
            return

    def _next_reply(self) -> str:
        if self.step == "done":
            return "You're set. Press Start when you're ready."
        return self._prompt_for(self.step)

    def _prompt_for(self, step: str) -> str:
        name = self.profile.get("name") or "the business"
        if step == "name":
            return "What should I call you or the business?"
        if step == "description":
            return f"Thanks, {name}. In one sentence, what do you do?"
        if step == "goal":
            return "What is the one outcome you want help with?"
        if step == "language":
            return "Should I use English or Amharic?"
        if step == "confirm":
            return self._summary()
        return "You're set. Press Start when you're ready."

    def _summary(self) -> str:
        name = self.profile.get("name") or "your business"
        description = self.profile.get("description") or "what you do"
        goals = self.profile.get("goals") or []
        goal = goals[0] if goals else "your main goal"
        lang = "Amharic" if self.profile.get("language") == "am" else "English"
        if self.profile.get("industry") == "fmcg_distribution":
            kind = "goods distribution to shops"
        else:
            kind = "general"
        return (
            f"{name} — {description}. "
            f"You want help with: {goal}. "
            f"I'll use {lang}. This is a {kind} assistant. "
            f"Say yes if this looks right, or tell me what to change."
        )

    def _parse_name(self, text: str) -> str:
        cleaned = text.strip().strip('"').strip("'").strip()
        cleaned = _NAME_PREFIX.sub("", cleaned).strip().strip('"').strip("'").rstrip(".").strip()
        if not cleaned or cleaned.endswith("?"):
            return ""
        lower = cleaned.lower()
        if lower in ("no", "nope", "change", "wrong", "yes", "ok", "okay"):
            return ""
        if any(w in lower for w in ("i want", "help me", "english", "amharic", "አማርኛ")):
            return ""
        if len(cleaned) > 80:
            return ""
        return cleaned

    def _parse_goal(self, text: str) -> tuple:
        raw = text.strip()
        fact = ""
        method = _METHOD.search(raw)
        if method:
            fact = method.group(0).strip()
            raw = raw[: method.start()].strip().rstrip(",").strip()
        raw = _GOAL_PREFIX.sub("", raw).strip().rstrip(".").strip()
        if len(raw) > 200:
            raw = raw[:200].rstrip()
        return raw, fact

    def _note_language(self, text: str, force: bool = False) -> None:
        lower = text.lower()
        if "አማርኛ" in text or "amharic" in lower:
            self.profile["language"] = "am"
            self.language_chosen = True
        elif re.search(r"\benglish\b", lower):
            self.profile["language"] = "en"
            self.language_chosen = True
        elif force:
            self.language_chosen = True

    def _note_industry(self, text: str) -> None:
        if _DISTRIBUTION.search(text):
            self.profile["industry"] = "fmcg_distribution"

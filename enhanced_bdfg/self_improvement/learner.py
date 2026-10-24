"""Preference learning and outcome tracking from assistant sessions."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from enhanced_bdfg.self_improvement.memory import MemoryStore

logger = logging.getLogger(__name__)

try:
    from enhanced_bdfg.runtime.model_router import extract_json_object
except Exception:  # pragma: no cover
    extract_json_object = None  # type: ignore

LANG_HINTS = {
    "amharic": "am",
    "አማርኛ": "am",
    "am": "am",
    "english": "en",
}

PRIORITY_HINTS = (
    ("fuel", "cares about fuel waste first"),
    ("route", "cares about routing efficiency"),
    ("kiosk", "focused on kiosk density"),
    ("manufacturer", "focused on manufacturer acquisition"),
    ("heatmap", "wants demand heatmaps"),
    ("amharic", "prefers Amharic summaries"),
)


class PreferenceLearner:
    """Extract durable user facts from a session transcript."""

    def __init__(self, memory: MemoryStore):
        self.memory = memory

    def learn_from_turn(
        self,
        user_id: str,
        user_text: str,
        llm_text: Optional[str] = None,
        llm_fn=None,
    ) -> Dict[str, Any]:
        updates: Dict[str, Any] = {"facts": [], "preferences": {}, "goals": []}
        lower = user_text.lower()
        for hint, code in LANG_HINTS.items():
            if hint in lower:
                updates["language"] = code
                updates["preferences"]["language"] = code
        for needle, fact in PRIORITY_HINTS:
            if needle in lower:
                updates["facts"].append(fact)
        goal_match = re.search(r"(?:i want to|goal is to|we need to)\s+(.+)", lower)
        if goal_match:
            updates["goals"].append(goal_match.group(1).strip()[:200])
        remember = re.search(r"(?:remember that|note that|don't forget)\s+(.+)", lower)
        if remember:
            updates["facts"].append(remember.group(1).strip()[:240])

        extracted = None
        if llm_fn is not None:
            try:
                extracted = llm_fn(user_text)
            except Exception as exc:
                logger.debug("learner llm_fn failed: %s", exc)
        elif llm_text and extract_json_object:
            extracted = extract_json_object(llm_text)
        if isinstance(extracted, dict):
            for fact in extracted.get("facts") or []:
                fact = str(fact).strip()
                if fact and fact not in updates["facts"]:
                    updates["facts"].append(fact)
            for goal in extracted.get("goals") or []:
                goal = str(goal).strip()
                if goal and goal not in updates["goals"]:
                    updates["goals"].append(goal)
            prefs = extracted.get("preferences") or {}
            if isinstance(prefs, dict):
                updates["preferences"].update(prefs)
            lang = extracted.get("language")
            if lang in ("en", "am"):
                updates["language"] = lang
                updates["preferences"]["language"] = lang
            loops = extracted.get("open_loops") or []
            for task in loops:
                task = str(task).strip()
                if task:
                    self.memory.add_open_loop(user_id, task[:200])

        if updates["facts"] or updates["preferences"] or updates["goals"] or "language" in updates:
            self.memory.upsert_user(user_id, updates)
            logger.info("Learned preferences for %s: %s", user_id, updates)
        return updates

    def learn_from_session(self, user_id: str, turns: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        turns = turns if turns is not None else self.memory.recent_turns(user_id, limit=20)
        combined: Dict[str, Any] = {"facts": [], "preferences": {}, "goals": []}
        for turn in turns:
            if turn.get("role") != "user":
                continue
            part = self.learn_from_turn(user_id, turn.get("content") or "")
            combined["facts"].extend(part.get("facts") or [])
            combined["preferences"].update(part.get("preferences") or {})
            combined["goals"].extend(part.get("goals") or [])
            if part.get("language"):
                combined["language"] = part["language"]
        return combined


class OutcomeTracker:
    """Record whether the user accepted a recommendation."""

    ACCEPT_WORDS = ("do it", "yes", "accepted", "dispatch", "onboard", "go ahead", "approved")
    REJECT_WORDS = ("no", "skip", "reject", "don't", "do not")

    def __init__(self, memory: MemoryStore):
        self.memory = memory

    def infer_and_record(self, user_id: str, last_advice: str, user_reply: str) -> Optional[bool]:
        lower = user_reply.lower().strip()
        accepted = None
        if any(w in lower for w in self.ACCEPT_WORDS):
            accepted = True
        elif any(w in lower for w in self.REJECT_WORDS):
            accepted = False
        if accepted is None:
            return None
        self.memory.record_outcome(user_id, last_advice[:400], accepted)
        return accepted

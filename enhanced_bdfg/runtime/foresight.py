"""Unprompted next commercial moves from memory and domain data."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from enhanced_bdfg.runtime.model_router import ModelRouter, extract_json_object

logger = logging.getLogger(__name__)


class ForesightEngine:
    """Propose 2–4 next moves without waiting for the user to ask."""

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router

    def next_moves(
        self,
        memory,
        user_id: str,
        tenant_id: Optional[str] = None,
        tools=None,
        language: str = "en",
    ) -> List[Dict[str, str]]:
        moves: List[Dict[str, str]] = []
        loops = memory.open_loops(user_id) if memory else []
        for loop in loops[:2]:
            moves.append(
                {
                    "title": "Open loop",
                    "body": loop.get("task") or "Follow up on something you asked me not to drop.",
                }
            )
        if tools is not None:
            try:
                dark = tools.dark_territories()
                cities = dark.get("sub_cities") or []
                names = [c.get("sub_city") for c in cities if isinstance(c, dict)]
                if names:
                    moves.append(
                        {
                            "title": "Coverage gap",
                            "body": f"Register kiosks or send a rep in {', '.join(names[:3])}.",
                        }
                    )
            except Exception as exc:
                logger.debug("foresight tools failed: %s", exc)
        user = memory.get_user(user_id) if memory else {}
        if not (user.get("goals") or []):
            moves.append(
                {
                    "title": "Set a goal",
                    "body": "Tell me one thing you want this business to do this month.",
                }
            )
        outcomes = memory.outcome_summary(user_id) if memory else {}
        if outcomes.get("rejected"):
            moves.append(
                {
                    "title": "Try another angle",
                    "body": "Last suggestion was skipped. Say what got in the way and I will adjust.",
                }
            )
        llm_moves = self._llm_moves(memory, user_id, tenant_id, language)
        for item in llm_moves:
            if item not in moves:
                moves.append(item)
        if not moves:
            moves.append(
                {
                    "title": "Start here",
                    "body": "Tell me who you serve and what is stuck. I will propose a next step.",
                }
            )
        return moves[:4]

    def _llm_moves(self, memory, user_id, tenant_id, language) -> List[Dict[str, str]]:
        if not self.router:
            return []
        block = memory.context_block(user_id, tenant_id) if memory else ""
        text = self.router.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "You propose the next commercial moves for a small-business assistant. "
                        "Return JSON: {\"moves\": [{\"title\": \"...\", \"body\": \"...\"}]} "
                        "with 2 to 4 short plain-language items. Language: "
                        + (language or "en")
                    ),
                },
                {"role": "user", "content": block or "No memory yet."},
            ]
        )
        data = extract_json_object(text or "")
        if not data:
            return []
        raw = data.get("moves") if isinstance(data.get("moves"), list) else []
        out = []
        for item in raw:
            if isinstance(item, dict) and item.get("body"):
                out.append(
                    {
                        "title": str(item.get("title") or "Next move")[:80],
                        "body": str(item.get("body"))[:280],
                    }
                )
        return out

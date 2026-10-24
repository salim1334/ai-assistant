"""Attentive business-developer coordinator with persistent memory."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Optional

from enhanced_bdfg.runtime.agent_framework import AgentFramework
from enhanced_bdfg.runtime.foresight import ForesightEngine
from enhanced_bdfg.runtime.model_router import ModelRouter, extract_json_object
from enhanced_bdfg.self_improvement.learner import OutcomeTracker, PreferenceLearner
from enhanced_bdfg.self_improvement.memory import MemoryStore

logger = logging.getLogger(__name__)

COORDINATOR_PROMPT = """You are an attentive business-developer assistant for this company.
You remember who the user is, their language, open loops, and past decisions.
You do not ask them to repeat what they already told you.
You act as a business developer: acquisition, territory plays, routing, CRM — not a report generator.
Analytics are tools you use, not the product.
Never be amnesiac. Follow up on open loops without being asked.
Propose the next commercial move before they ask.
Speak plainly. If they are not technical, avoid jargon.
"""


class AttentiveCoordinator:
    def __init__(
        self,
        memory_path: str,
        domain=None,
        user_id: str = "default",
        tenant_id: str = "alarm",
        language: str = "en",
        persona: str = "",
        model_config: Optional[Dict[str, Any]] = None,
        router: Optional[ModelRouter] = None,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.language = language
        self.persona = persona or COORDINATOR_PROMPT
        self.memory = MemoryStore(memory_path)
        self.learner = PreferenceLearner(self.memory)
        self.outcomes = OutcomeTracker(self.memory)
        self.domain = domain
        self.tools = None
        if domain is not None:
            from enhanced_bdfg.industry_specific.fmcg_distribution.tools import AlarmCRMTools

            self.tools = AlarmCRMTools(domain, language=language)
        self.framework = AgentFramework({"name": "Business Assistant"})
        self.router = router or ModelRouter.from_assistant_settings(model_config or {})
        self.foresight = ForesightEngine(self.router)
        self._last_advice = ""
        self.offline_notice = False
        self.memory.upsert_user(user_id, {"language": language})

    def close(self) -> None:
        self.memory.close()
        if self.domain:
            self.domain.close()

    def next_moves(self):
        return self.foresight.next_moves(
            self.memory, self.user_id, self.tenant_id, tools=self.tools, language=self.language
        )

    def chat(self, user_text: str) -> str:
        user_text = (user_text or "").strip()
        if not user_text:
            return "I'm here. Tell me what you need for the business today."
        self.memory.log_turn(self.user_id, "user", user_text)
        self.learner.learn_from_turn(self.user_id, user_text, llm_fn=self._learn_llm)
        if self._last_advice:
            self.outcomes.infer_and_record(self.user_id, self._last_advice, user_text)

        ctx = self._tool_context(user_text)
        memory_block = self.memory.context_block(self.user_id, self.tenant_id)
        loops = self.memory.open_loops(self.user_id)
        followup = ""
        if loops and not re.search(r"forget|later", user_text, re.I):
            followup = f"Open loop I have not dropped: {loops[0]['task']}. "

        routed = self.framework.process_query(user_text, ctx)
        body = routed.get("response") if routed.get("success") else routed.get("error", "")
        spoken = self._accept_model_reply(self._try_llm(user_text, memory_block, body, ctx))
        reply = followup + (spoken or self._plain_line(user_text))

        if re.search(r"follow up|remind me|don't let me forget", user_text, re.I):
            self.memory.add_open_loop(self.user_id, user_text[:200])
        if ctx.get("dispatch_decision"):
            self._last_advice = ctx["dispatch_decision"].get("message", reply)
        else:
            self._last_advice = reply[:400]
        self.memory.log_turn(self.user_id, "assistant", reply)
        return reply

    def _plain_line(self, query: str) -> str:
        return f"About '{query}': tell me the next step you want, and I will stay on that."

    def _accept_model_reply(self, text: Optional[str]) -> Optional[str]:
        cleaned = re.sub(r"\{[^{}]*\}", "", text or "", flags=re.S)
        cleaned = re.sub(r"\{.*\}", "", cleaned, flags=re.S).strip()
        if not cleaned or "{" in cleaned or "}" in cleaned:
            return None
        if len(cleaned) > 400 or cleaned.count("?") > 1:
            return None
        return cleaned

    def _learn_llm(self, user_text: str) -> Optional[Dict[str, Any]]:
        text = self.router.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "Extract durable user facts as JSON only: "
                        '{"facts":[],"goals":[],"preferences":{},"language":"en","open_loops":[]}'
                    ),
                },
                {"role": "user", "content": user_text},
            ]
        )
        return extract_json_object(text or "")

    def _tool_context(self, user_text: str) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {}
        if not self.tools:
            return ctx
        q = user_text.lower()
        if any(w in q for w in ("dark", "heatmap", "territory", "sub-city", "subcity", "coverage")):
            dark = self.tools.dark_territories()
            ctx["dark_territories"] = dark.get("sub_cities")
            ctx["heatmap"] = dark.get("heatmap")
        if any(w in q for w in ("dispatch", "van", "truck", "roll", "batch")):
            mids = self.domain.conn.execute("SELECT id FROM manufacturers").fetchall()
            if mids:
                ctx["dispatch_decision"] = self.tools.maybe_dispatch(int(mids[0]["id"]))
        if "adapter" in q or "erp" in q:
            ctx["adapters"] = self.tools.ping_adapters()
        if "forecast" in q or "restock" in q:
            cycle = "weekly" if "water" in q else "monthly"
            ctx["forecast"] = self.tools.forecast_restock(cycle)
        if any(w in q for w in ("onboard kiosk", "register kiosk", "new kiosk")):
            ctx["hint"] = "Ask for kiosk name, sub-city, and GPS if they want to register one."
        return ctx

    def _try_llm(self, user_text: str, memory_block: str, fallback: str, ctx: Dict[str, Any]) -> Optional[str]:
        if os.environ.get("BDFG_DISABLE_LLM") == "1":
            return None
        tool_note = ""
        if ctx:
            tool_note = f"\nTool results: {ctx}\n"
        return self.router.complete(
            [
                {"role": "system", "content": self.persona + "\n\n" + COORDINATOR_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Memory:\n{memory_block}\n{tool_note}\n"
                        f"Rule-based draft (you may improve it):\n{fallback}\n\n"
                        f"User: {user_text}"
                    ),
                },
            ]
        )


def default_memory_path(root: str) -> str:
    return os.path.join(root, "memory", "assistant.sqlite")

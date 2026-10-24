"""Finished agent runtime: BaseAgent, domain agents, and coordinator framework."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseAgent:
    """Shared agent surface: tools, metrics, and query handling."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.name = self.config.get("name", "Base Agent")
        self.description = self.config.get("description", "")
        self.domain = self.config.get("domain", "general")
        self.prompt = self.config.get("prompt", "")
        self.tool_registry: Dict[str, Callable] = {}
        self.knowledge_base: Any = None
        self.metrics = {
            "queries_processed": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0,
        }

    def register_tool(self, tool_name: str, tool_function: Callable) -> None:
        self.tool_registry[tool_name] = tool_function

    def set_knowledge_base(self, knowledge_base: Any) -> None:
        self.knowledge_base = knowledge_base

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.time()
        self.metrics["queries_processed"] += 1
        context = context or {}
        try:
            response = self._handle(query, context)
            elapsed = time.time() - start
            self.metrics["successful_responses"] += 1
            self.metrics["total_response_time"] += elapsed
            self.metrics["average_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["successful_responses"]
            )
            return {
                "success": True,
                "response": response,
                "domain": self.domain,
                "response_time": elapsed,
                "tools_used": list(self.tool_registry.keys()),
            }
        except Exception as exc:
            logger.exception("Agent %s failed", self.name)
            elapsed = time.time() - start
            self.metrics["failed_responses"] += 1
            return {"success": False, "error": str(exc), "domain": self.domain, "response_time": elapsed}

    def _handle(self, query: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError

    def get_metrics(self) -> Dict[str, Any]:
        return dict(self.metrics)

    def update_prompt(self, new_prompt: str) -> None:
        self.prompt = new_prompt


class DescriptiveAnalyticsAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        config = dict(config)
        config["domain"] = "descriptive"
        super().__init__(config)

    def _handle(self, query: str, context: Dict[str, Any]) -> str:
        data = context.get("heatmap") or context.get("summary")
        if data:
            return f"Descriptive summary: {data}"
        return f"Descriptive view of '{query}': look at recent orders, kiosk counts, and volume by sub-city."


class BusinessDeveloperAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = dict(config or {})
        cfg.setdefault("name", "Business Developer")
        cfg["domain"] = "business_developer"
        super().__init__(cfg)

    def _handle(self, query: str, context: Dict[str, Any]) -> str:
        dark = context.get("dark_territories") or []
        names = [d.get("sub_city") for d in dark] if isinstance(dark, list) else []
        if names:
            return (
                f"Business developer play: prioritize field registration in {', '.join(names)}. "
                "Offer 10-day featured listing to the first manufacturer who staffs those neighborhoods, "
                "and print QR codes on cartons so kiosks self-enroll."
            )
        if re.search(r"outreach|pitch|manufacturer", query, re.I):
            return (
                "Draft outreach: lead with fuel waste from knock-and-hope vans, then the dual "
                "marketplace + private CRM so they keep customer data when a rep leaves."
            )
        return f"Business-development take on '{query}': acquire density first, then manufacturers follow the kiosk network."


class DemandIntelligenceAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = dict(config or {})
        cfg["domain"] = "demand"
        super().__init__(cfg)

    def _handle(self, query: str, context: Dict[str, Any]) -> str:
        heatmap = context.get("heatmap") or []
        if heatmap:
            lines = [f"{r.get('sub_city')}: {r.get('qty', 0)} units / {r.get('kiosks', 0)} kiosks" for r in heatmap]
            return "Demand heatmap (synthetic sample unless live data is connected):\n" + "\n".join(lines)
        return "No demand rows yet. Register kiosks and take orders to build the heatmap."


class AgentFramework:
    """Orchestrates domain agents and optional self-improvement."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.config.get("name", "Business Assistant Framework")
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        self.self_improvement_enabled = (
            self.config.get("configuration", {}).get("self_improvement", {}).get("enabled", True)
        )

    def _initialize_agents(self) -> None:
        defaults = [
            DescriptiveAnalyticsAgent({"name": "Descriptive"}),
            BusinessDeveloperAgent(),
            DemandIntelligenceAgent(),
        ]
        for agent in defaults:
            self.agents[agent.domain] = agent

    def classify_query(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ("heatmap", "demand", "forecast", "spike", "dark")):
            return "demand"
        if any(w in q for w in ("outreach", "pitch", "onboard manufacturer", "acquire", "featured")):
            return "business_developer"
        return "descriptive"

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        domain = self.classify_query(query)
        agent = self.agents.get(domain) or next(iter(self.agents.values()))
        return agent.process_query(query, context or {})

    def improve(self, recorded: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze recorded queries; used by PreferenceLearner in the coordinator."""
        return {"analyzed": len(recorded), "enabled": self.self_improvement_enabled}


class KnowledgeBase:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.topics: Dict[str, Dict[str, str]] = {}
        for topic_id, topic_data in self.config.items():
            if isinstance(topic_data, dict):
                self.topics[topic_id] = {
                    "title": topic_data.get("title", ""),
                    "content": topic_data.get("content", ""),
                }

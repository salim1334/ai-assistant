"""Tool orchestration — register and invoke assistant tools with error wrapping."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class ToolOrchestrator:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable) -> None:
        self.tools[name] = fn

    def invoke(self, name: str, **kwargs) -> Dict[str, Any]:
        if name not in self.tools:
            return {"ok": False, "error": f"unknown tool {name}"}
        try:
            result = self.tools[name](**kwargs)
            return {"ok": True, "result": result}
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return {"ok": False, "error": str(exc)}

"""Create a personalized assistant package (generic or Alarm CRM)."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

from enhanced_bdfg.runtime.implement import implement_alarm_crm
from enhanced_bdfg.runtime.paths import assistants_root

README_GENERIC = """# {name} assistant (created by BDFG)

This folder is your personal business assistant. It remembers what you tell it
and suggests next steps. It runs on this computer.

Talk to it: open BDFG (`bdfg start`) and use Your assistant.

Not included: live payment capture, hosted cloud apps, or phone apps.
"""

PERSONA = """You are {name}'s attentive business-developer assistant.
Business: {business_name}
What they do: {description}
Industry: {industry}
Goals: {goals}
Language: {language}

You remember who they are, open loops, and past decisions. Never ask them to
repeat what they already told you. Propose the next commercial move before they
ask. Analytics are tools you use, not the product. Speak plainly. If they are
not technical, avoid jargon.
"""


_ALARM_CODES = {"fmcg_distribution", "fmcg", "alarm", "alarm-crm", "alarm_crm"}
_DISTRIBUTION = re.compile(
    r"\b(kiosk|kiosks|fmcg|distributor|distributors)\b|distribut\w+\s+.{0,40}\b(shops?|kiosks?)\b",
    re.I,
)
_OTHER_WORK = re.compile(
    r"economic development|develop(?:ing)?\s+(?:the\s+)?country|develop\s+haiti",
    re.I,
)


def profile_text(profile: Dict[str, Any]) -> str:
    goals = profile.get("goals") or []
    facts = profile.get("facts") or []
    parts = [
        str(profile.get("name") or ""),
        str(profile.get("description") or profile.get("what_they_do") or ""),
        " ".join(str(g) for g in goals),
        " ".join(str(f) for f in facts),
    ]
    return " ".join(parts)


def use_alarm_pack(profile: Dict[str, Any], industry: str) -> bool:
    """Alarm CRM only for goods-to-shop distribution, not a stray industry code."""
    blob = profile_text(profile)
    if _DISTRIBUTION.search(blob):
        return True
    if _OTHER_WORK.search(blob):
        return False
    return industry in _ALARM_CODES


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "assistant").lower()).strip("-")
    return slug or "assistant"


def create_assistant(
    profile: Dict[str, Any],
    output_dir: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    seed: bool = True,
) -> Dict[str, Any]:
    """Write a runnable assistant folder with persona, memory, and settings."""
    profile = dict(profile or {})
    name = profile.get("name") or profile.get("business_name") or "My business"
    industry = (profile.get("industry") or "general").lower()
    if isinstance(industry, dict):
        industry = (industry.get("code") or "general").lower()
    language = profile.get("language") or "en"
    model_config = dict(model_config or {})

    if not output_dir:
        output_dir = str(assistants_root() / slugify(name))
    os.makedirs(output_dir, exist_ok=True)
    mem_dir = os.path.join(output_dir, "memory")
    os.makedirs(mem_dir, exist_ok=True)

    alarm = use_alarm_pack(profile, industry)
    if not alarm and industry in _ALARM_CODES:
        industry = "general"
    sample: Dict[str, Any] = {}
    db_path = None
    if alarm:
        packed = implement_alarm_crm(output_dir, seed=seed)
        sample = packed.get("sample") or {}
        db_path = packed.get("db_path")

    persona = PERSONA.format(
        name=name,
        business_name=name,
        description=profile.get("description") or profile.get("what_they_do") or "(not told yet)",
        industry=industry,
        goals=", ".join(profile.get("goals") or []) or "(not told yet)",
        language=language,
    )
    persona_path = os.path.join(output_dir, "persona.md")
    with open(persona_path, "w", encoding="utf-8") as fh:
        fh.write(persona)

    memory_path = os.path.join(mem_dir, "assistant.sqlite")
    config = {
        "name": f"{name} assistant",
        "industry": "fmcg_distribution" if alarm else industry,
        "pack": "alarm-crm" if alarm else "generic",
        "language": language,
        "profile": profile,
        "db_path": db_path,
        "memory_path": memory_path,
        "persona_path": persona_path,
        "self_improvement": {"enabled": True},
        "model": {
            "backend": model_config.get("backend") or "local",
            "local_model": model_config.get("local_model") or model_config.get("tag") or "",
        },
        "sample": sample,
    }
    cfg_path = os.path.join(output_dir, "assistant.json")
    existing: Dict[str, Any] = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, encoding="utf-8") as fh:
                existing = json.load(fh) or {}
        except json.JSONDecodeError:
            existing = {}
    existing.update(config)
    with open(cfg_path, "w", encoding="utf-8") as fh:
        json.dump(existing, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(README_GENERIC.format(name=name))

    from enhanced_bdfg.self_improvement.memory import MemoryStore

    store = MemoryStore(memory_path)
    store.upsert_user(
        "default",
        {
            "language": language,
            "goals": list(profile.get("goals") or []),
            "facts": list(profile.get("facts") or []),
            "preferences": dict(profile.get("preferences") or {}),
        },
    )
    store.close()
    return {
        "output_dir": output_dir,
        "config": cfg_path,
        "memory_path": memory_path,
        "pack": config["pack"],
        "profile": profile,
    }


# Imported by implement; keep a late alias to avoid circular import at module load
def default_memory_path_for(root: str) -> str:
    return os.path.join(root, "memory", "assistant.sqlite")

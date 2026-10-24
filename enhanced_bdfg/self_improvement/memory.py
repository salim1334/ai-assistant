"""Persistent user, firm, and conversation memory for BDFG assistants."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profile (
    user_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS firm_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at REAL NOT NULL,
    UNIQUE(tenant_id, key)
);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS open_loops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS advice_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    advice TEXT NOT NULL,
    accepted INTEGER NOT NULL,
    created_at REAL NOT NULL
);
"""


class MemoryStore:
    """SQLite-backed user/firm/episodic memory."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        parent = os.path.dirname(os.path.abspath(db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # --- user profile ---

    def get_user(self, user_id: str) -> Dict[str, Any]:
        row = self._conn.execute(
            "SELECT payload FROM user_profile WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            return {
                "user_id": user_id,
                "language": "en",
                "goals": [],
                "preferences": {},
                "facts": [],
            }
        data = json.loads(row["payload"])
        data.setdefault("user_id", user_id)
        data.setdefault("preferences", {})
        data.setdefault("facts", [])
        data.setdefault("goals", [])
        return data

    def upsert_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_user(user_id)
        prefs = dict(current.get("preferences") or {})
        prefs.update(updates.get("preferences") or {})
        facts = list(current.get("facts") or [])
        for fact in updates.get("facts") or []:
            if fact and fact not in facts:
                facts.append(fact)
        goals = list(current.get("goals") or [])
        for goal in updates.get("goals") or []:
            if goal and goal not in goals:
                goals.append(goal)
        merged = {**current, **{k: v for k, v in updates.items() if k not in ("preferences", "facts", "goals")}}
        merged["preferences"] = prefs
        merged["facts"] = facts
        merged["goals"] = goals
        self._conn.execute(
            "INSERT INTO user_profile(user_id, payload, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
            (user_id, json.dumps(merged, ensure_ascii=False), time.time()),
        )
        self._conn.commit()
        return merged

    # --- firm ---

    def set_firm_fact(self, tenant_id: str, key: str, value: Any) -> None:
        self._conn.execute(
            "INSERT INTO firm_facts(tenant_id, key, value, updated_at) VALUES(?,?,?,?) "
            "ON CONFLICT(tenant_id, key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (tenant_id, key, json.dumps(value, ensure_ascii=False), time.time()),
        )
        self._conn.commit()

    def get_firm_facts(self, tenant_id: str) -> Dict[str, Any]:
        rows = self._conn.execute(
            "SELECT key, value FROM firm_facts WHERE tenant_id = ?", (tenant_id,)
        ).fetchall()
        out: Dict[str, Any] = {}
        for row in rows:
            try:
                out[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                out[row["key"]] = row["value"]
        return out

    # --- conversation ---

    def log_turn(self, user_id: str, role: str, content: str) -> None:
        self._conn.execute(
            "INSERT INTO conversations(user_id, role, content, created_at) VALUES(?,?,?,?)",
            (user_id, role, content, time.time()),
        )
        self._conn.commit()

    def recent_turns(self, user_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT role, content, created_at FROM conversations WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [
            {"role": r["role"], "content": r["content"], "created_at": r["created_at"]}
            for r in reversed(list(rows))
        ]

    # --- open loops ---

    def add_open_loop(self, user_id: str, task: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO open_loops(user_id, task, status, created_at) VALUES(?,?, 'open', ?)",
            (user_id, task, time.time()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def open_loops(self, user_id: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id, task, status FROM open_loops WHERE user_id = ? AND status = 'open'",
            (user_id,),
        ).fetchall()
        return [{"id": r["id"], "task": r["task"], "status": r["status"]} for r in rows]

    def close_loop(self, loop_id: int) -> None:
        self._conn.execute("UPDATE open_loops SET status = 'done' WHERE id = ?", (loop_id,))
        self._conn.commit()

    # --- outcomes ---

    def record_outcome(self, user_id: str, advice: str, accepted: bool) -> None:
        self._conn.execute(
            "INSERT INTO advice_outcomes(user_id, advice, accepted, created_at) VALUES(?,?,?,?)",
            (user_id, advice, 1 if accepted else 0, time.time()),
        )
        self._conn.commit()

    def outcome_summary(self, user_id: str) -> Dict[str, Any]:
        rows = self._conn.execute(
            "SELECT advice, accepted FROM advice_outcomes WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        accepted = [r["advice"] for r in rows if r["accepted"]]
        rejected = [r["advice"] for r in rows if not r["accepted"]]
        return {"accepted": accepted, "rejected": rejected}

    def context_block(self, user_id: str, tenant_id: Optional[str] = None, limit: int = 8) -> str:
        """Compact memory for the coordinator prompt."""
        user = self.get_user(user_id)
        loops = self.open_loops(user_id)
        turns = self.recent_turns(user_id, limit=limit)
        outcomes = self.outcome_summary(user_id)
        lines = [
            f"User id: {user_id}",
            f"Language: {user.get('language', 'en')}",
            f"Goals: {', '.join(user.get('goals') or []) or '(none yet)'}",
            f"Known facts: {'; '.join(user.get('facts') or []) or '(none yet)'}",
            f"Preferences: {json.dumps(user.get('preferences') or {}, ensure_ascii=False)}",
            f"Open loops: {'; '.join(l['task'] for l in loops) or '(none)'}",
            f"Accepted advice: {'; '.join(outcomes['accepted'][-5:]) or '(none)'}",
            f"Rejected advice: {'; '.join(outcomes['rejected'][-5:]) or '(none)'}",
        ]
        if tenant_id:
            facts = self.get_firm_facts(tenant_id)
            if facts:
                lines.append(f"Firm facts: {json.dumps(facts, ensure_ascii=False)[:800]}")
        if turns:
            lines.append("Recent conversation:")
            for t in turns:
                lines.append(f"  {t['role']}: {t['content'][:400]}")
        return "\n".join(lines)


# Back-compat names used in the plan
UserMemoryStore = MemoryStore
FirmMemoryStore = MemoryStore
ConversationLog = MemoryStore

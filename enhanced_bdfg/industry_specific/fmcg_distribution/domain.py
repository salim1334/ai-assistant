"""SQLite domain for Alarm CRM: kiosks, manufacturers, orders, deliveries, visits."""

from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS manufacturers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    language TEXT DEFAULT 'en',
    isolated INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS kiosks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sub_city TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    language TEXT DEFAULT 'am',
    photo_meta TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    cycle TEXT NOT NULL,
    unit_etb REAL NOT NULL,
    FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kiosk_id INTEGER NOT NULL,
    manufacturer_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL,
    advance_paid INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS dispatches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id INTEGER NOT NULL,
    created_at REAL NOT NULL,
    status TEXT DEFAULT 'scheduled',
    payload TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispatch_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    lat REAL,
    lon REAL,
    proof TEXT,
    delivered_at REAL
);
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id INTEGER NOT NULL,
    kiosk_id INTEGER NOT NULL,
    lat REAL,
    lon REAL,
    note TEXT,
    visited_at REAL NOT NULL
);
"""

BATCH_THRESHOLD = 8


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class AlarmCRMDomain:
    """In-process Alarm CRM ecosystem store."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        parent = os.path.dirname(os.path.abspath(db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def onboard_manufacturer(self, name: str, category: str, lat: float, lon: float, language: str = "en") -> int:
        cur = self.conn.execute(
            "INSERT INTO manufacturers(name, category, lat, lon, language) VALUES(?,?,?,?,?)",
            (name, category, lat, lon, language),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def register_kiosk(
        self, name: str, sub_city: str, lat: float, lon: float, language: str = "am", photo_meta: Optional[dict] = None
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO kiosks(name, sub_city, lat, lon, language, photo_meta) VALUES(?,?,?,?,?,?)",
            (name, sub_city, lat, lon, language, json.dumps(photo_meta or {})),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_sku(self, manufacturer_id: int, sku: str, name: str, cycle: str, unit_etb: float) -> int:
        cur = self.conn.execute(
            "INSERT INTO catalog(manufacturer_id, sku, name, cycle, unit_etb) VALUES(?,?,?,?,?)",
            (manufacturer_id, sku, name, cycle, unit_etb),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def proximity_catalog(self, kiosk_id: int, max_km: float = 8.0) -> List[Dict[str, Any]]:
        kiosk = self.conn.execute("SELECT * FROM kiosks WHERE id = ?", (kiosk_id,)).fetchone()
        if not kiosk:
            return []
        rows = self.conn.execute(
            "SELECT c.*, m.name AS manufacturer_name, m.lat AS mlat, m.lon AS mlon "
            "FROM catalog c JOIN manufacturers m ON m.id = c.manufacturer_id"
        ).fetchall()
        out = []
        for row in rows:
            dist = haversine_km(kiosk["lat"], kiosk["lon"], row["mlat"], row["mlon"])
            if dist <= max_km:
                item = dict(row)
                item["distance_km"] = round(dist, 2)
                out.append(item)
        out.sort(key=lambda x: x["distance_km"])
        return out

    def place_order(self, kiosk_id: int, manufacturer_id: int, sku: str, qty: int, advance_paid: bool = True) -> int:
        cur = self.conn.execute(
            "INSERT INTO orders(kiosk_id, manufacturer_id, sku, qty, advance_paid, status, created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (kiosk_id, manufacturer_id, sku, qty, 1 if advance_paid else 0, "pending", time.time()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def pending_qty(self, manufacturer_id: int) -> int:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(qty), 0) AS q FROM orders WHERE manufacturer_id = ? AND status = 'pending'",
            (manufacturer_id,),
        ).fetchone()
        return int(row["q"] if row else 0)

    def should_dispatch(self, manufacturer_id: int, threshold: int = BATCH_THRESHOLD) -> bool:
        return self.pending_qty(manufacturer_id) >= threshold

    def schedule_dispatch(self, manufacturer_id: int, threshold: int = BATCH_THRESHOLD) -> Optional[int]:
        if not self.should_dispatch(manufacturer_id, threshold):
            return None
        pending = self.conn.execute(
            "SELECT id FROM orders WHERE manufacturer_id = ? AND status = 'pending'",
            (manufacturer_id,),
        ).fetchall()
        ids = [r["id"] for r in pending]
        cur = self.conn.execute(
            "INSERT INTO dispatches(manufacturer_id, created_at, status, payload) VALUES(?,?,?,?)",
            (manufacturer_id, time.time(), "scheduled", json.dumps({"order_ids": ids})),
        )
        self.conn.execute(
            "UPDATE orders SET status = 'dispatched' WHERE manufacturer_id = ? AND status = 'pending'",
            (manufacturer_id,),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def gps_handoff(self, dispatch_id: int, order_id: int, lat: float, lon: float, proof: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO deliveries(dispatch_id, order_id, lat, lon, proof, delivered_at) VALUES(?,?,?,?,?,?)",
            (dispatch_id, order_id, lat, lon, proof, time.time()),
        )
        self.conn.execute("UPDATE orders SET status = 'delivered' WHERE id = ?", (order_id,))
        self.conn.commit()
        return int(cur.lastrowid)

    def log_visit(self, manufacturer_id: int, kiosk_id: int, lat: float, lon: float, note: str = "") -> int:
        cur = self.conn.execute(
            "INSERT INTO visits(manufacturer_id, kiosk_id, lat, lon, note, visited_at) VALUES(?,?,?,?,?,?)",
            (manufacturer_id, kiosk_id, lat, lon, note, time.time()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def demand_by_subcity(self, manufacturer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = (
            "SELECT k.sub_city, COUNT(DISTINCT k.id) AS kiosks, COALESCE(SUM(o.qty), 0) AS qty "
            "FROM kiosks k LEFT JOIN orders o ON o.kiosk_id = k.id"
        )
        params: Tuple = ()
        if manufacturer_id:
            sql += " AND o.manufacturer_id = ?"
            params = (manufacturer_id,)
        sql += " GROUP BY k.sub_city"
        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def dark_territories(self, manufacturer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Sub-cities with kiosks but relatively low order volume."""
        rows = self.demand_by_subcity(manufacturer_id)
        if not rows:
            return []
        scored = []
        for r in rows:
            kiosks = max(1, int(r["kiosks"]))
            qty = int(r["qty"] or 0)
            intensity = qty / kiosks
            scored.append({**r, "intensity": round(intensity, 2)})
        mean = sum(s["intensity"] for s in scored) / len(scored)
        return [s for s in scored if s["intensity"] < mean]

    def forecast_cycle(self, sku_cycle: str) -> Dict[str, Any]:
        """Weekly water vs monthly hygiene restock cycles from the proposal."""
        if sku_cycle == "weekly":
            return {"horizon_days": 7, "label": "weekly hydration restock"}
        return {"horizon_days": 30, "label": "monthly hygiene restock"}

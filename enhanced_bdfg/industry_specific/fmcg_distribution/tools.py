"""Assistant-callable tools wrapping Alarm CRM domain workflows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from enhanced_bdfg.industry_specific.fmcg_distribution.adapters import get_adapter
from enhanced_bdfg.industry_specific.fmcg_distribution.domain import AlarmCRMDomain, BATCH_THRESHOLD
from enhanced_bdfg.industry_specific.fmcg_distribution.localization import format_etb, t, to_ethiopian_date


class AlarmCRMTools:
    def __init__(self, domain: AlarmCRMDomain, language: str = "en"):
        self.domain = domain
        self.language = language

    def geo_register_kiosk(self, name: str, sub_city: str, lat: float, lon: float) -> Dict[str, Any]:
        kid = self.domain.register_kiosk(name, sub_city, lat, lon)
        return {"kiosk_id": kid, "name": name, "sub_city": sub_city}

    def proximity_catalog(self, kiosk_id: int) -> List[Dict[str, Any]]:
        return self.domain.proximity_catalog(kiosk_id)

    def batch_order(self, kiosk_id: int, manufacturer_id: int, sku: str, qty: int) -> Dict[str, Any]:
        oid = self.domain.place_order(kiosk_id, manufacturer_id, sku, qty, advance_paid=True)
        pay = get_adapter("telebirr").capture_advance(0, f"order-{oid}")
        return {"order_id": oid, "payment": pay.as_dict()}

    def maybe_dispatch(self, manufacturer_id: int) -> Dict[str, Any]:
        pending = self.domain.pending_qty(manufacturer_id)
        if not self.domain.should_dispatch(manufacturer_id):
            return {
                "dispatched": False,
                "pending_qty": pending,
                "threshold": BATCH_THRESHOLD,
                "message": t("do_not_roll", self.language),
            }
        did = self.domain.schedule_dispatch(manufacturer_id)
        return {
            "dispatched": True,
            "dispatch_id": did,
            "pending_qty": pending,
            "message": t("dispatch_ok", self.language),
        }

    def gps_handoff(self, dispatch_id: int, order_id: int, lat: float, lon: float, proof: str) -> Dict[str, Any]:
        hid = self.domain.gps_handoff(dispatch_id, order_id, lat, lon, proof)
        return {"delivery_id": hid, "ethiopian_date": to_ethiopian_date()}

    def dark_territories(self, manufacturer_id: Optional[int] = None) -> Dict[str, Any]:
        return {
            "label": t("dark_territory", self.language),
            "sub_cities": self.domain.dark_territories(manufacturer_id),
            "heatmap": self.domain.demand_by_subcity(manufacturer_id),
        }

    def forecast_restock(self, cycle: str) -> Dict[str, Any]:
        return self.domain.forecast_cycle(cycle)

    def price(self, amount: float) -> str:
        return format_etb(amount)

    def ping_adapters(self) -> Dict[str, Any]:
        keys = ["alarm_stock", "smart_bono", "et_property", "telebirr", "chapa", "sms"]
        return {k: get_adapter(k).ping().as_dict() for k in keys}

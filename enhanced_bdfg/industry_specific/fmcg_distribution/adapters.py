"""Adapter contracts for Alarm products and Ethiopian rails. v1 is stubbed."""

from __future__ import annotations

from typing import Any, Dict, Optional


class AdapterResult:
    def __init__(self, ok: bool, message: str, payload: Optional[Dict[str, Any]] = None):
        self.ok = ok
        self.message = message
        self.payload = payload or {}

    def as_dict(self) -> Dict[str, Any]:
        return {"ok": self.ok, "message": self.message, "payload": self.payload}


class BaseAdapter:
    name = "base"

    def ping(self) -> AdapterResult:
        return AdapterResult(True, f"{self.name} adapter ready (stub)", {"live": False})

    def publish_catalog(self, items: list) -> AdapterResult:
        return AdapterResult(True, f"{self.name}: catalog publish queued (stub)", {"count": len(items)})

    def pull_inventory(self) -> AdapterResult:
        return AdapterResult(True, f"{self.name}: no live inventory in v1", {"items": []})


class AlarmStockERPAdapter(BaseAdapter):
    name = "alarm_stock_erp"


class SmartBonoAdapter(BaseAdapter):
    name = "smart_bono_cafe"


class ETPropertyAdapter(BaseAdapter):
    name = "et_property"


class TelebirrAdapter(BaseAdapter):
    name = "telebirr"

    def capture_advance(self, amount_etb: float, reference: str) -> AdapterResult:
        return AdapterResult(
            True,
            "Advance payment recorded locally; Telebirr capture is a v1 stub",
            {"amount_etb": amount_etb, "reference": reference, "captured": False},
        )


class ChapaAdapter(BaseAdapter):
    name = "chapa"

    def capture_advance(self, amount_etb: float, reference: str) -> AdapterResult:
        return AdapterResult(
            True,
            "Advance payment recorded locally; Chapa capture is a v1 stub",
            {"amount_etb": amount_etb, "reference": reference, "captured": False},
        )


class EthioTelecomSMSAdapter(BaseAdapter):
    name = "ethio_telecom_sms"

    def send(self, to: str, body: str) -> AdapterResult:
        return AdapterResult(True, "SMS queued locally (stub)", {"to": to, "body": body, "sent": False})


ADAPTERS = {
    "alarm_stock": AlarmStockERPAdapter(),
    "smart_bono": SmartBonoAdapter(),
    "et_property": ETPropertyAdapter(),
    "telebirr": TelebirrAdapter(),
    "chapa": ChapaAdapter(),
    "sms": EthioTelecomSMSAdapter(),
}


def get_adapter(key: str) -> BaseAdapter:
    if key not in ADAPTERS:
        raise KeyError(f"Unknown adapter: {key}")
    return ADAPTERS[key]

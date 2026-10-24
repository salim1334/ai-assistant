"""Named workflows from Alarm CRM proposal section 6."""

from __future__ import annotations

from typing import Any, Dict

from enhanced_bdfg.industry_specific.fmcg_distribution.tools import AlarmCRMTools

WORKFLOW_STEPS = (
    "geo_register",
    "proximity_catalog",
    "batch_order",
    "scheduled_dispatch",
    "gps_handoff",
)


def run_order_to_delivery(
    tools: AlarmCRMTools,
    kiosk_id: int,
    manufacturer_id: int,
    sku: str,
    qty: int,
) -> Dict[str, Any]:
    """Place an order and dispatch only if the batch threshold is met."""
    order = tools.batch_order(kiosk_id, manufacturer_id, sku, qty)
    dispatch = tools.maybe_dispatch(manufacturer_id)
    return {"order": order, "dispatch": dispatch, "steps": WORKFLOW_STEPS}

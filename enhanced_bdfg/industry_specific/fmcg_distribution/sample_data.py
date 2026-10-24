"""Synthetic Addis Ababa sample data for Alarm CRM demos. Not real demand."""

from __future__ import annotations

from enhanced_bdfg.industry_specific.fmcg_distribution.domain import AlarmCRMDomain

# Approximate Addis sub-city centroids for demo only
SUBCITIES = {
    "Bole": (8.9806, 38.7990),
    "Mercato": (9.0300, 38.7400),
    "Piassa": (9.0370, 38.7520),
    "Kazanchis": (9.0105, 38.7700),
}


def seed_sample_addis(domain: AlarmCRMDomain) -> dict:
    water_id = domain.onboard_manufacturer("Abyssinia Springs", "water", 9.01, 38.76, language="en")
    hygiene_id = domain.onboard_manufacturer("Addis Care Hygiene", "hygiene", 9.02, 38.75, language="am")
    domain.add_sku(water_id, "WATER-20L", "20L bottled water carton", "weekly", 180.0)
    domain.add_sku(hygiene_id, "PAD-PACK", "Sanitary pad bale", "monthly", 420.0)
    domain.add_sku(hygiene_id, "DIAPER-M", "Baby diaper bale M", "monthly", 650.0)

    kiosk_ids = []
    for i, (name, (lat, lon)) in enumerate(SUBCITIES.items()):
        kid = domain.register_kiosk(
            f"{name} kiosk {i + 1}",
            name,
            lat + 0.002,
            lon - 0.001,
            language="am",
            photo_meta={"note": "synthetic shop front"},
        )
        kiosk_ids.append((kid, name))
        extra = domain.register_kiosk(
            f"{name} kiosk {i + 1}b",
            name,
            lat - 0.0015,
            lon + 0.0012,
            language="am",
        )
        kiosk_ids.append((extra, name))

    # Uneven demand: Bole/Mercato busy, Kazanchis dark
    for kid, sub in kiosk_ids:
        if sub in ("Bole", "Mercato"):
            domain.place_order(kid, water_id, "WATER-20L", qty=4, advance_paid=True)
        elif sub == "Piassa":
            domain.place_order(kid, water_id, "WATER-20L", qty=1, advance_paid=True)
        # Kazanchis: registered, almost no orders
        if sub == "Bole":
            domain.place_order(kid, hygiene_id, "PAD-PACK", qty=1, advance_paid=True)

    return {
        "water_manufacturer_id": water_id,
        "hygiene_manufacturer_id": hygiene_id,
        "kiosk_count": len(kiosk_ids),
        "sub_cities": list(SUBCITIES.keys()),
        "note": "Synthetic Addis sample — not claimed as real demand",
    }

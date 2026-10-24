"""Tests for Alarm CRM pack, memory, and truncated-file completions."""

import os
import tempfile

import pytest

os.environ["BDFG_DISABLE_LLM"] = "1"

from enhanced_bdfg.core.business_profiler import BusinessProfiler
from enhanced_bdfg.core.hardware_manager import HardwareManager
from enhanced_bdfg.industry_specific.fmcg_distribution.domain import (
    BATCH_THRESHOLD,
    AlarmCRMDomain,
    haversine_km,
)
from enhanced_bdfg.industry_specific.fmcg_distribution.sample_data import seed_sample_addis
from enhanced_bdfg.runtime.implement import implement_alarm_crm, load_coordinator
from enhanced_bdfg.self_improvement.memory import MemoryStore


def test_profiler_imports_and_fmcg():
    profiler = BusinessProfiler()
    profile = profiler.create_profile_from_info(
        {
            "name": "Abyssinia Springs",
            "industry": "fmcg_distribution",
            "description": "bottled water kiosk distribution",
            "goals": ["cut fuel waste"],
            "employees": 12,
        }
    )
    assert profile["industry"]["code"] == "fmcg_distribution"
    assert any(ds["type"] == "crm" for ds in profile["data_sources"])


def test_interactive_profiler():
    answers = iter(
        ["Cafe Lemma", "restaurant", "small", "8", "100000", "Addis Ababa", "cafeteria", "cut waste", "am"]
    )
    profiler = BusinessProfiler()
    info = profiler.collect_interactive_info(input_fn=lambda _: next(answers))
    assert info["name"] == "Cafe Lemma"
    assert info["language"] == "am"
    assert info["employees"] == 8


def test_hardware_detect():
    hw = HardwareManager()
    info = hw.detect_hardware()
    assert "device_type" in info
    assert "ram" in info
    rec = hw.get_recommended_models()
    assert rec["recommended_models"]


def test_haversine_and_proximity():
    assert haversine_km(9.03, 38.74, 9.03, 38.74) < 0.01
    with tempfile.TemporaryDirectory() as tmp:
        domain = AlarmCRMDomain(os.path.join(tmp, "t.sqlite"))
        mid = domain.onboard_manufacturer("M", "water", 9.03, 38.74)
        domain.add_sku(mid, "W", "water", "weekly", 10)
        kid = domain.register_kiosk("K", "Mercato", 9.031, 38.741)
        cat = domain.proximity_catalog(kid, max_km=5)
        assert cat and cat[0]["sku"] == "W"
        domain.close()


def test_batch_dispatch_threshold():
    with tempfile.TemporaryDirectory() as tmp:
        domain = AlarmCRMDomain(os.path.join(tmp, "t.sqlite"))
        mid = domain.onboard_manufacturer("M", "water", 9.0, 38.7)
        domain.add_sku(mid, "W", "water", "weekly", 10)
        kid = domain.register_kiosk("K", "Bole", 9.01, 38.8)
        assert domain.should_dispatch(mid) is False
        for _ in range(BATCH_THRESHOLD):
            domain.place_order(kid, mid, "W", 1)
        assert domain.should_dispatch(mid) is True
        did = domain.schedule_dispatch(mid)
        assert did is not None
        domain.close()


def test_weekly_vs_monthly_forecast():
    with tempfile.TemporaryDirectory() as tmp:
        domain = AlarmCRMDomain(os.path.join(tmp, "t.sqlite"))
        assert domain.forecast_cycle("weekly")["horizon_days"] == 7
        assert domain.forecast_cycle("monthly")["horizon_days"] == 30
        domain.close()


def test_memory_round_trip_and_session_recall():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "mem.sqlite")
        store = MemoryStore(path)
        store.upsert_user("salim", {"language": "am", "facts": ["cares about fuel waste first"]})
        store.log_turn("salim", "user", "Remember that we sell water in Bole")
        store.close()
        store2 = MemoryStore(path)
        user = store2.get_user("salim")
        assert user["language"] == "am"
        assert "cares about fuel waste first" in user["facts"]
        turns = store2.recent_turns("salim")
        assert turns and "Bole" in turns[0]["content"]
        store2.close()


def test_golden_path_dark_subcities_and_memory():
    with tempfile.TemporaryDirectory() as tmp:
        result = implement_alarm_crm(os.path.join(tmp, "alarm_crm"), seed=True)
        coord = load_coordinator(result["output_dir"], user_id="operator")
        reply = coord.chat("which sub-cities are dark?")
        assert reply
        coord.chat("Remember that I prefer Amharic summaries")
        coord.close()
        coord2 = load_coordinator(result["output_dir"], user_id="operator")
        block = coord2.memory.context_block("operator")
        assert "Amharic" in block or "am" in block.lower() or "prefers" in block.lower()
        reply2 = coord2.chat("what did I just tell you about language?")
        assert reply2
        coord2.close()

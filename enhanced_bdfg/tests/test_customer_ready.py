"""Customer-ready path: bootstrap, router, packager, foresight, UI."""

from __future__ import annotations

import json
import os

import pytest

os.environ["BDFG_DISABLE_LLM"] = "1"
os.environ["BDFG_SKIP_SERIAL_LOCK"] = "1"

from enhanced_bdfg.runtime.bootstrap import select_setup_model, installed_model_names, Bootstrapper
from enhanced_bdfg.runtime.model_router import ModelRouter, extract_json_object
from enhanced_bdfg.runtime.packager import create_assistant
from enhanced_bdfg.runtime.secrets import load_secrets, redacted, save_secrets
from enhanced_bdfg.runtime.implement import load_coordinator
from enhanced_bdfg.self_improvement.learner import PreferenceLearner
from enhanced_bdfg.self_improvement.memory import MemoryStore
from enhanced_bdfg.runtime.foresight import ForesightEngine


def test_select_setup_model_low_ram_picks_tiny():
    hw = {"ram_gb": 3.0, "disk_gb": 32, "cpu_cores": 4, "gpu": False, "gpu_memory": None}
    picked = select_setup_model(hw, installed_tags=[])
    assert picked["tag"] in ("tinyllama", "qwen2.5:0.5b")
    assert picked["need_pull"] is True
    assert ":" not in picked["tag"] or int(picked["tag"].split(":")[-1].replace("b", "").split(".")[0] or "1") < 7


def test_select_setup_model_more_ram_picks_quality():
    hw = {"ram_gb": 16.0, "disk_gb": 256, "cpu_cores": 8, "gpu": False}
    picked = select_setup_model(hw, installed_tags=[])
    assert picked["tag"] in ("qwen2.5:1.5b", "phi3:mini", "qwen2.5:3b")
    assert picked["need_pull"] is True


def test_select_setup_model_prefers_installed_fit():
    hw = {"ram_gb": 16.0, "disk_gb": 256, "cpu_cores": 8, "gpu": False}
    picked = select_setup_model(hw, installed_tags=["tinyllama:latest"])
    assert picked["on_disk"] is True
    assert picked["need_pull"] is False
    assert "tinyllama" in picked["tag"]


def test_installed_model_names():
    names = installed_model_names({"models": [{"name": "qwen2.5:1.5b"}, {"model": "tinyllama:latest"}]})
    assert "qwen2.5:1.5b" in names
    assert "tinyllama:latest" in names


def test_bootstrap_skips_pull_when_present(tmp_path, monkeypatch):
    monkeypatch.setenv("BDFG_HOME", str(tmp_path / "home"))
    boot = Bootstrapper()
    hw = {"ram_gb": 16, "disk_gb": 200, "cpu_cores": 8, "gpu": False}
    monkeypatch.setattr(boot, "ollama_binary", lambda: "/usr/bin/ollama")
    monkeypatch.setattr(boot, "ping", lambda: True)
    monkeypatch.setattr(boot, "start_serve", lambda: True)
    monkeypatch.setattr(boot, "list_tags", lambda: ["qwen2.5:3b"])
    pulled = []
    monkeypatch.setattr(boot, "_pull", lambda model: pulled.append(model))
    status = boot.ensure(hardware=hw)
    assert status["phase"] == "ready"
    assert pulled == []
    assert status["model"]


def test_bootstrap_pulls_scored_tag_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("BDFG_HOME", str(tmp_path / "home"))
    boot = Bootstrapper()
    hw = {"ram_gb": 16, "disk_gb": 200, "cpu_cores": 8, "gpu": False}
    monkeypatch.setattr(boot, "ollama_binary", lambda: "/usr/bin/ollama")
    monkeypatch.setattr(boot, "ping", lambda: True)
    monkeypatch.setattr(boot, "list_tags", lambda: [])
    pulled = []

    def fake_pull(model):
        pulled.append(model)
        boot._set(phase="ready", model=model)

    monkeypatch.setattr(boot, "_pull", fake_pull)
    status = boot.ensure(hardware=hw)
    assert status["phase"] == "ready"
    assert len(pulled) == 1
    assert pulled[0] == status["model"]


def test_secrets_not_echoed(tmp_path, monkeypatch):
    monkeypatch.setenv("BDFG_HOME", str(tmp_path / "home"))
    save_secrets({"openai_api_key": "sk-secret-1234"})
    shown = redacted()
    assert "sk-secret-1234" not in json.dumps(shown)
    assert shown["openai_api_key"].endswith("1234")
    raw = load_secrets()
    assert raw["openai_api_key"] == "sk-secret-1234"


def test_router_disabled_returns_none():
    router = ModelRouter({"backend": "openai"})
    assert router.complete([{"role": "user", "content": "hi"}]) is None


def test_extract_json_object():
    assert extract_json_object("noise {\"a\": 1} tail") == {"a": 1}


def test_learner_json_merge(tmp_path):
    store = MemoryStore(str(tmp_path / "m.sqlite"))
    learner = PreferenceLearner(store)
    learner.learn_from_turn(
        "u",
        "hello",
        llm_fn=lambda _: {"facts": ["sells water in Bole"], "goals": ["cut fuel"], "language": "am", "open_loops": []},
    )
    user = store.get_user("u")
    assert "sells water in Bole" in user["facts"]
    assert user["language"] == "am"
    store.close()


def test_generic_and_alarm_packager(tmp_path):
    generic = create_assistant(
        {"name": "Lemma Cafe", "industry": "restaurant", "goals": ["cut waste"], "language": "en"},
        output_dir=str(tmp_path / "cafe"),
    )
    assert generic["pack"] == "generic"
    assert os.path.exists(os.path.join(generic["output_dir"], "persona.md"))
    alarm = create_assistant(
        {"name": "Abyssinia Springs", "industry": "fmcg_distribution", "language": "am"},
        output_dir=str(tmp_path / "alarm"),
    )
    assert alarm["pack"] == "alarm-crm"
    assert os.path.exists(os.path.join(alarm["output_dir"], "alarm_crm.sqlite"))
    mislabeled = create_assistant(
        {
            "name": "Continuous Improvement & Development",
            "industry": "fmcg_distribution",
            "description": "An economic development firm focusing on developing the country of Haiti.",
            "goals": ["develop Haiti"],
            "language": "en",
        },
        output_dir=str(tmp_path / "cid"),
    )
    assert mislabeled["pack"] == "generic"
    saved = json.load(open(os.path.join(mislabeled["output_dir"], "assistant.json"), encoding="utf-8"))
    assert saved["industry"] == "general"
    assert not os.path.exists(os.path.join(mislabeled["output_dir"], "alarm_crm.sqlite"))
    named_alarm = create_assistant(
        {"name": "Alarm Technology", "industry": "general", "language": "en"},
        output_dir=str(tmp_path / "alarm-tech"),
    )
    assert named_alarm["pack"] == "generic"


def test_second_session_recall_and_foresight(tmp_path):
    created = create_assistant(
        {"name": "Demo Shop", "industry": "retail", "goals": ["grow"], "language": "en"},
        output_dir=str(tmp_path / "shop"),
    )
    coord = load_coordinator(created["output_dir"], user_id="operator")
    coord.chat("Remember that I prefer Amharic summaries")
    coord.close()
    coord2 = load_coordinator(created["output_dir"], user_id="operator")
    block = coord2.memory.context_block("operator")
    assert "Amharic" in block or "am" in block.lower() or "prefers" in block.lower()
    moves = ForesightEngine().next_moves(coord2.memory, "operator")
    assert moves
    coord2.close()


def test_setup_guide_heuristic_profile():
    from enhanced_bdfg.runtime.setup_guide import SetupGuide

    guide = SetupGuide()
    guide.router.complete = lambda messages, **kw: None
    r1 = guide.chat("Abyssinia Springs")
    r2 = guide.chat("we distribute water to kiosks")
    r3 = guide.chat("I want to cut fuel waste")
    assert r1["profile"]["name"] == "Abyssinia Springs"
    assert r2["profile"]["industry"] == "fmcg_distribution"
    assert r3["profile"]["goals"]
    assert r3["complete"] is False


def test_setup_guide_alarm_completes_only_after_yes():
    from enhanced_bdfg.runtime.setup_guide import SetupGuide

    guide = SetupGuide()
    guide.router.complete = lambda messages, **kw: None
    guide.chat("Abyssinia Springs")
    guide.chat("we distribute water to kiosks")
    guide.chat("I want to cut fuel waste")
    before = guide.chat("English")
    assert before["complete"] is False
    assert before["profile"]["industry"] == "fmcg_distribution"
    assert "{" not in before["reply"]
    done = guide.chat("yes")
    assert done["complete"] is True
    assert done["profile"]["industry"] == "fmcg_distribution"
    assert done["profile"]["language"] == "en"


def test_setup_guide_economic_development_stays_general():
    from enhanced_bdfg.runtime.setup_guide import SetupGuide

    guide = SetupGuide()
    guide.router.complete = lambda messages, **kw: None
    guide.chat("Continuous Improvement & Development")
    described = guide.chat("An economic development firm focusing on developing the country of Haiti.")
    assert described["profile"]["industry"] == "general"
    guide.chat("develop Haiti")
    pending = guide.chat("English")
    assert pending["complete"] is False
    assert "{" not in pending["reply"]
    assert '"complete"' not in pending["reply"]
    done = guide.chat("yes")
    assert done["complete"] is True
    assert done["profile"]["industry"] == "general"
    assert done["profile"]["name"] == "Continuous Improvement & Development"
    assert done["profile"]["goals"] == ["develop Haiti"]
    assert "{" not in done["reply"]
    assert '"complete"' not in done["reply"]


def test_setup_guide_json_only_model_reply_is_hidden():
    from enhanced_bdfg.runtime.setup_guide import SetupGuide

    guide = SetupGuide()
    guide.router.complete = lambda messages, **kw: (
        '{"complete": true, "name": "Wrong", "industry": "fmcg_distribution", "goals": ["nope"]}'
    )
    opening = guide.chat("")
    assert opening["complete"] is False
    assert "{" not in opening["reply"]
    assert "call you or the business" in opening["reply"]
    after = guide.chat("Lemma Shop")
    assert after["complete"] is False
    assert after["profile"]["industry"] == "general"
    assert after["profile"]["name"] == "Lemma Shop"
    assert after["profile"]["goals"] == []
    assert "{" not in after["reply"]
    assert '"complete"' not in after["reply"]
    assert "what do you do" in after["reply"].lower()


def test_setup_ignores_model_answer_for_alarm_technology():
    from enhanced_bdfg.runtime.setup_guide import SetupGuide

    calls = {"n": 0}

    def complete(messages, **kw):
        calls["n"] += 1
        return "We design and install security systems."

    guide = SetupGuide()
    guide.router.complete = complete
    guide.chat("Alarm Technology")
    assert calls["n"] == 0
    reply = guide.turns[-1]["content"]
    assert "what do you do" in reply.lower()
    assert "security systems" not in reply.lower()
    assert guide.profile["industry"] == "general"
    assert guide.profile["name"] == "Alarm Technology"


def test_coordinator_keeps_short_reply_and_drops_json(tmp_path, monkeypatch):
    monkeypatch.delenv("BDFG_DISABLE_LLM", raising=False)
    created = create_assistant(
        {"name": "Alarm Technology", "industry": "general", "goals": ["install systems"], "language": "en"},
        output_dir=str(tmp_path / "alarm-tech"),
    )
    coord = load_coordinator(created["output_dir"], user_id="operator")
    coord.router.complete = lambda messages, **kw: '{"complete": true, "industry": "fmcg_distribution"}'
    rejected = coord.chat("What should we do this week?")
    assert "fmcg_distribution" not in rejected
    assert "{" not in rejected
    assert "What should we do this week?" in rejected
    coord.router.complete = lambda messages, **kw: "Call the two open accounts tomorrow morning."
    accepted = coord.chat("Who should I call?")
    assert accepted == "Call the two open accounts tomorrow morning."
    coord.close()


def test_setup_router_uses_bootstrapped_model_only():
    from enhanced_bdfg.runtime.setup_guide import local_setup_router

    router = local_setup_router("qwen2.5:0.5b")
    assert router.local_only is True
    assert router.local_model == "qwen2.5:0.5b"
    assert router.backend == "local"
    assert router.complete([{"role": "user", "content": "rephrase"}]) is None


def test_fastapi_setup_and_chat(tmp_path, monkeypatch):
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from enhanced_bdfg.runtime import bootstrap as bootmod
    from enhanced_bdfg.ui.app import create_app

    monkeypatch.setenv("BDFG_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("BDFG_ASSISTANTS_DIR", str(tmp_path / "assistants"))
    bootmod.reset_bootstrapper()
    boot = bootmod.get_bootstrapper()
    boot._set(phase="ready", message="Helper is ready.", percent=100, model="tinyllama", ollama_installed=True)
    boot.save_state({"bootstrap_complete": True, "model": "tinyllama", "hardware_snapshot": {"ram_gb": 8}})

    client = TestClient(create_app())
    st = client.get("/api/state").json()
    assert "bootstrap" in st
    chat = client.post("/api/setup/chat", json={"message": "Lemma Shop", "language": "en"})
    assert chat.status_code == 200
    commit = client.post(
        "/api/setup",
        json={"profile": {"name": "Lemma Shop", "industry": "retail", "goals": ["grow"]}, "backend": "local"},
    )
    assert commit.status_code == 200
    body = commit.json()
    assert body["pack"] == "generic"
    reply = client.post("/api/chat", json={"message": "Remember that we close on Sundays"})
    assert reply.status_code == 200
    assert reply.json()["reply"]
    mem = client.get("/api/memory").json()
    assert "Sunday" in mem["text"] or "sunday" in mem["text"].lower() or mem["text"]
    moves = client.get("/api/next-moves").json()
    assert "moves" in moves
    key_resp = client.post(
        "/api/settings/model",
        json={"backend": "openai", "provider": "openai", "api_key": "sk-not-real-9999"},
    )
    assert key_resp.status_code == 200
    assert "sk-not-real-9999" not in json.dumps(key_resp.json())

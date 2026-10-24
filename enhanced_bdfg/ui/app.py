"""Customer browser app — FastAPI + static files."""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from enhanced_bdfg.runtime.bootstrap import get_bootstrapper
from enhanced_bdfg.runtime.packager import create_assistant
from enhanced_bdfg.runtime.paths import assistants_root, bdfg_home
from enhanced_bdfg.runtime.secrets import redacted, save_secrets
from enhanced_bdfg.ui.copy import STRINGS, t

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"

_guide = None
_guide_lock = threading.Lock()
_coord = None
_coord_root: Optional[str] = None
_language = "en"


def _current_assistant_dir() -> Optional[str]:
    marker = bdfg_home() / "current_assistant"
    if marker.exists():
        path = marker.read_text(encoding="utf-8").strip()
        if path and os.path.isdir(path):
            return path
    root = assistants_root()
    kids = [p for p in root.iterdir() if p.is_dir() and (p / "assistant.json").exists()]
    if kids:
        return str(sorted(kids, key=lambda p: p.stat().st_mtime, reverse=True)[0])
    return None


def _set_current(path: str) -> None:
    marker = bdfg_home() / "current_assistant"
    marker.write_text(path, encoding="utf-8")


def _get_coord():
    global _coord, _coord_root
    root = _current_assistant_dir()
    if not root:
        return None
    if _coord is None or _coord_root != root:
        from enhanced_bdfg.runtime.implement import load_coordinator

        if _coord is not None:
            try:
                _coord.close()
            except Exception:
                pass
        _coord = load_coordinator(root)
        _coord_root = root
    return _coord


def create_app():
    from fastapi import FastAPI, Body
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles

    app = FastAPI(title="BDFG", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/copy")
    def copy(language: str = "en"):
        lang = "am" if language in ("am", "amh", "amharic") else "en"
        return {"language": lang, "strings": STRINGS.get(lang, STRINGS["en"])}

    @app.get("/api/bootstrap")
    def bootstrap_start():
        boot = get_bootstrapper()

        def run():
            try:
                boot.ensure()
            except Exception as exc:
                logger.exception("bootstrap")
                boot._set(phase="error", error=str(exc), message="Could not finish getting ready.")

        phase = boot.snapshot().get("phase")
        if phase in ("idle", "need_ollama", "error", "ready"):
            if phase != "ready":
                threading.Thread(target=run, daemon=True).start()
        elif phase in ("checking", "starting", "selecting", "pulling", "installing"):
            pass
        else:
            threading.Thread(target=run, daemon=True).start()
        return boot.snapshot()

    @app.get("/api/bootstrap/status")
    def bootstrap_status():
        return get_bootstrapper().snapshot()

    @app.post("/api/bootstrap/confirm-install")
    def confirm_install():
        return get_bootstrapper().confirm_install_ollama()

    @app.get("/api/state")
    def state():
        root = _current_assistant_dir()
        pack = None
        if root and os.path.exists(os.path.join(root, "assistant.json")):
            with open(os.path.join(root, "assistant.json"), encoding="utf-8") as fh:
                pack = json.load(fh)
        boot = get_bootstrapper().snapshot()
        return {
            "assistant_dir": root,
            "pack": pack,
            "bootstrap": boot,
            "has_assistant": bool(root),
            "secrets": redacted(),
        }

    @app.post("/api/setup/chat")
    def setup_chat(payload: dict = Body(default={})):
        global _guide, _language
        _language = payload.get("language") or _language
        with _guide_lock:
            if _guide is None:
                from enhanced_bdfg.runtime.setup_guide import SetupGuide, local_setup_router

                model = get_bootstrapper().load_state().get("model") or ""
                _guide = SetupGuide(router=local_setup_router(model), language=_language)
            result = _guide.chat(payload.get("message") or "")
        return result

    @app.post("/api/setup")
    def setup_commit(payload: dict = Body(default={})):
        global _guide, _coord, _coord_root
        profile = dict(payload.get("profile") or {})
        if _guide is not None:
            for key, value in _guide.profile.items():
                if value not in ("", [], {}, None):
                    profile[key] = value
        boot = get_bootstrapper().load_state()
        model_config = {
            "backend": payload.get("backend") or "local",
            "local_model": boot.get("model") or "",
        }
        created = create_assistant(profile, model_config=model_config)
        _set_current(created["output_dir"])
        _coord = None
        _coord_root = None
        _guide = None
        return created

    @app.post("/api/chat")
    def chat(payload: dict = Body(default={})):
        coord = _get_coord()
        language = payload.get("language") or "en"
        if coord is None:
            return JSONResponse(
                {"reply": t("setup_title", language), "error": "no_assistant"},
                status_code=400,
            )
        reply = coord.chat(payload.get("message") or "")
        return {"reply": reply}

    @app.get("/api/memory")
    def memory():
        coord = _get_coord()
        if coord is None:
            return {"text": ""}
        return {"text": coord.memory.context_block(coord.user_id, coord.tenant_id)}

    @app.get("/api/next-moves")
    def next_moves():
        coord = _get_coord()
        if coord is None:
            return {"moves": []}
        return {"moves": coord.next_moves()}

    @app.get("/api/chips")
    def chips(language: str = "en"):
        root = _current_assistant_dir()
        pack = "generic"
        if root and os.path.exists(os.path.join(root, "assistant.json")):
            with open(os.path.join(root, "assistant.json"), encoding="utf-8") as fh:
                cfg = json.load(fh)
            pack = cfg.get("pack") or "generic"
        items = []
        if pack == "alarm-crm":
            items = [
                t("chips_dark", language),
                t("chips_restock", language),
                t("chips_dispatch", language),
                t("chips_kiosk", language),
            ]
        return {"pack": pack, "chips": items}

    @app.post("/api/settings/model")
    def settings_model(payload: dict = Body(default={})):
        global _coord, _coord_root
        updates: Dict[str, Any] = {}
        backend = payload.get("backend") or "local"
        provider = (payload.get("provider") or backend or "openai").lower()
        api_key = payload.get("api_key") or ""
        if api_key:
            if provider == "anthropic":
                updates["anthropic_api_key"] = api_key
            elif provider == "gemini":
                updates["gemini_api_key"] = api_key
            else:
                updates["openai_api_key"] = api_key
                if payload.get("openai_base_url"):
                    updates["openai_base_url"] = payload.get("openai_base_url")
        if payload.get("local_model"):
            updates["local_model"] = payload.get("local_model")
        if backend:
            updates["backend"] = backend
        saved = save_secrets(updates)
        root = _current_assistant_dir()
        if root:
            cfg_path = os.path.join(root, "assistant.json")
            cfg: Dict[str, Any] = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, encoding="utf-8") as fh:
                    cfg = json.load(fh)
            cfg.setdefault("model", {})
            cfg["model"]["backend"] = backend or cfg["model"].get("backend") or "local"
            if payload.get("local_model"):
                cfg["model"]["local_model"] = payload.get("local_model")
            with open(cfg_path, "w", encoding="utf-8") as fh:
                json.dump(cfg, fh, indent=2)
            _coord = None
            _coord_root = None
        return {"ok": True, "secrets": redacted(saved)}

    return app


def serve(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    import uvicorn
    import webbrowser

    app = create_app()
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://{host}:{port}/")).start()
    uvicorn.run(app, host=host, port=port, log_level="info")

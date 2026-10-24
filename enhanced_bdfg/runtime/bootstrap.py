"""First-run Ollama bootstrap: pick a small model that fits this machine."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import threading
import time
from typing import Any, Dict, List, Optional

from enhanced_bdfg.runtime.http_util import http_json, http_stream_json_lines
from enhanced_bdfg.runtime.paths import state_path
from enhanced_bdfg.runtime.serial import local_model_lock

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
INSTALL_HINT = "curl -fsSL https://ollama.com/install.sh | sh"

# Setup-class only (tiny → ~4B). Never 7B+ on first run.
SETUP_CATALOG: List[Dict[str, Any]] = [
    {"tag": "tinyllama", "ram_gb": 2.0, "disk_gb": 0.7, "quality": 2, "ollama": "tinyllama"},
    {"tag": "qwen2.5:0.5b", "ram_gb": 1.5, "disk_gb": 0.4, "quality": 3, "ollama": "qwen2.5:0.5b"},
    {"tag": "qwen2.5:1.5b", "ram_gb": 3.0, "disk_gb": 1.2, "quality": 6, "ollama": "qwen2.5:1.5b"},
    {"tag": "phi3:mini", "ram_gb": 4.0, "disk_gb": 2.3, "quality": 7, "ollama": "phi3:mini"},
    {"tag": "qwen2.5:3b", "ram_gb": 5.0, "disk_gb": 2.0, "quality": 8, "ollama": "qwen2.5:3b"},
]


def hardware_snapshot(hardware: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if hardware is None:
        from enhanced_bdfg.core.hardware_manager import HardwareManager

        hardware = HardwareManager().detect_hardware()
    ram = hardware.get("ram_gb")
    if ram is None:
        ram = hardware.get("ram")
    if isinstance(ram, dict):
        ram = ram.get("total") or ram.get("gb") or 0
    gpu = hardware.get("gpu") or {}
    cpu = hardware.get("cpu") or {}
    return {
        "ram_gb": float(ram or 0),
        "disk_gb": float(hardware.get("disk") or 0),
        "cpu_cores": int(cpu.get("cores") or 0),
        "gpu": bool(gpu.get("available")),
        "gpu_memory": gpu.get("memory"),
        "device_type": hardware.get("device_type"),
    }


def available_ram_gb(snapshot: Dict[str, Any]) -> float:
    ram = float(snapshot.get("ram_gb") or 0)
    return max(0.5, ram - 2.0)  # leave ~2 GB for the OS


def _tag_matches(installed: str, wanted: str) -> bool:
    inst = (installed or "").split(":")[0]
    want = (wanted or "").split(":")[0]
    if installed == wanted or inst == wanted or installed.startswith(wanted):
        return True
    return inst == want and (":" not in wanted or wanted in installed)


def installed_model_names(tags_payload: Any) -> List[str]:
    names: List[str] = []
    models = []
    if isinstance(tags_payload, dict):
        models = tags_payload.get("models") or []
    elif isinstance(tags_payload, list):
        models = tags_payload
    for item in models:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            name = item.get("name") or item.get("model") or ""
            if name:
                names.append(name)
    return names


def select_setup_model(
    hardware: Optional[Dict[str, Any]] = None,
    installed_tags: Optional[List[str]] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Score setup-class models for this machine.

    Prefers an already-installed catalog member that fits. Never returns 7B+.
    """
    snapshot = hardware if hardware and "ram_gb" in (hardware or {}) else hardware_snapshot(hardware)
    installed = list(installed_tags or [])
    catalog = catalog or SETUP_CATALOG
    ram = available_ram_gb(snapshot)
    disk = float(snapshot.get("disk_gb") or 0)
    gpu_mem = snapshot.get("gpu_memory")
    vram = float(gpu_mem) if gpu_mem else 0.0
    headroom = ram + (vram * 0.5 if snapshot.get("gpu") else 0.0)

    scored = []
    for entry in catalog:
        need = float(entry["ram_gb"])
        fits = need <= headroom + 0.25
        on_disk = any(_tag_matches(name, entry["ollama"]) for name in installed)
        if not fits and not on_disk:
            score = 0.0
        else:
            score = float(entry["quality"]) * 10.0
            if on_disk:
                score += 30.0
            if fits:
                score += 10.0
            else:
                score -= 15.0  # installed but tight
            leftover = headroom - need
            score += max(-8.0, min(8.0, leftover))
            if disk and disk < float(entry["disk_gb"]) + 1 and not on_disk:
                score -= 20.0
        scored.append({**entry, "fits": fits, "on_disk": on_disk, "score": score})

    usable = [s for s in scored if s["score"] > 0]
    installed_fit = [s for s in usable if s.get("on_disk") and s.get("fits")]
    if installed_fit:
        winner = max(installed_fit, key=lambda s: s["score"])
    elif not usable:
        smallest = min(catalog, key=lambda e: e["ram_gb"])
        winner = {**smallest, "fits": False, "on_disk": False, "score": 1.0}
    else:
        winner = max(usable, key=lambda s: s["score"])

    need_pull = not winner.get("on_disk")
    return {
        "tag": winner["ollama"],
        "quality": winner["quality"],
        "ram_gb": winner["ram_gb"],
        "fits": bool(winner.get("fits")),
        "on_disk": bool(winner.get("on_disk")),
        "need_pull": need_pull,
        "score": winner.get("score", 0),
        "hardware": snapshot,
        "candidates": [
            {"tag": s["ollama"], "score": s["score"], "on_disk": s["on_disk"], "fits": s["fits"]}
            for s in sorted(scored, key=lambda x: -x["score"])
        ],
    }


class Bootstrapper:
    """Tracks first-run Ollama detect / select / pull for the UI."""

    def __init__(self):
        self._lock = threading.Lock()
        self.status: Dict[str, Any] = {
            "phase": "idle",
            "message": "Not started yet.",
            "percent": 0,
            "model": None,
            "ollama_installed": False,
            "ollama_running": False,
            "install_command": INSTALL_HINT,
            "error": None,
            "need_pull": False,
        }

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.status)

    def _set(self, **kwargs) -> None:
        with self._lock:
            self.status.update(kwargs)

    def ollama_binary(self) -> Optional[str]:
        return shutil.which("ollama")

    def ping(self) -> bool:
        try:
            status, _ = http_json(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
            return 200 <= status < 300
        except Exception:
            return False

    def list_tags(self) -> List[str]:
        try:
            status, body = http_json(f"{OLLAMA_HOST}/api/tags", timeout=8.0)
            if 200 <= status < 300:
                return installed_model_names(body)
        except Exception as exc:
            logger.debug("list tags failed: %s", exc)
        return []

    def start_serve(self) -> bool:
        binary = self.ollama_binary()
        if not binary:
            return False
        if self.ping():
            return True
        try:
            subprocess.Popen(
                [binary, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            logger.warning("Could not start ollama serve: %s", exc)
            return False
        deadline = time.time() + 20
        while time.time() < deadline:
            if self.ping():
                return True
            time.sleep(0.4)
        return self.ping()

    def load_state(self) -> Dict[str, Any]:
        path = state_path()
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save_state(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        current = self.load_state()
        current.update(updates)
        path = state_path()
        path.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return current

    def hardware_changed(self, saved: Dict[str, Any], now: Dict[str, Any]) -> bool:
        if not saved:
            return False
        old_ram = float(saved.get("ram_gb") or 0)
        new_ram = float(now.get("ram_gb") or 0)
        if old_ram and abs(old_ram - new_ram) / max(old_ram, 1) > 0.35:
            return True
        if bool(saved.get("gpu")) != bool(now.get("gpu")):
            return True
        return False

    def ensure(self, hardware: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect Ollama, pick a fitting small model, pull if missing."""
        self._set(phase="checking", message="Checking this computer…", percent=5, error=None)
        binary = self.ollama_binary()
        running = self.ping()
        self._set(ollama_installed=bool(binary), ollama_running=running)
        if not binary and not running:
            self._set(
                phase="need_ollama",
                message="I can still take notes without a live model. Install Ollama to talk with a helper on this computer.",
                percent=0,
            )
            return self.snapshot()

        self._set(phase="starting", message="Starting the local helper…", percent=15)
        if not running:
            ok = self.start_serve()
            self._set(ollama_running=ok)
            if not ok:
                self._set(
                    phase="error",
                    error="Ollama is installed but did not start. Try opening a terminal and running: ollama serve",
                    message="Could not start the local helper.",
                )
                return self.snapshot()

        self._set(phase="selecting", message="Finding a helper that fits this computer…", percent=30)
        snap = hardware_snapshot(hardware)
        saved = self.load_state()
        tags = self.list_tags()
        selection = select_setup_model(snap, tags)
        model = selection["tag"]

        saved_model = saved.get("model")
        if (
            saved_model
            and not self.hardware_changed(saved.get("hardware_snapshot") or {}, snap)
            and any(_tag_matches(name, saved_model) for name in tags)
        ):
            model = saved_model
            selection["need_pull"] = False
            selection["on_disk"] = True
            selection["tag"] = model

        self._set(model=model, need_pull=bool(selection["need_pull"]))
        if selection["need_pull"]:
            self._set(
                phase="pulling",
                message="Downloading a helper that fits this computer… this happens once.",
                percent=40,
            )
            try:
                with local_model_lock():
                    self._pull(model)
            except Exception as exc:
                logger.exception("pull failed")
                self._set(
                    phase="error",
                    error=str(exc),
                    message="Could not download the helper. You can keep going without a live model.",
                )
                return self.snapshot()
        else:
            self._set(phase="ready", message="Helper is ready.", percent=100, model=model)

        self.save_state(
            {
                "bootstrap_complete": True,
                "model": model,
                "hardware_snapshot": snap,
                "updated_at": time.time(),
            }
        )
        self._set(phase="ready", message="Helper is ready.", percent=100, model=model, need_pull=False)
        return self.snapshot()

    def _pull(self, model: str) -> None:
        url = f"{OLLAMA_HOST}/api/pull"
        last_percent = 40
        for event in http_stream_json_lines(url, {"name": model, "stream": True}, timeout=900.0):
            status = str(event.get("status") or "")
            completed = event.get("completed") or 0
            total = event.get("total") or 0
            if total:
                pct = 40 + int(55 * (float(completed) / float(total)))
                last_percent = min(95, pct)
            if event.get("error"):
                raise RuntimeError(str(event["error"]))
            self._set(
                phase="pulling",
                percent=last_percent,
                message=status or "Downloading a helper that fits this computer… this happens once.",
                model=model,
            )
        # confirm it listed
        tags = self.list_tags()
        if tags and not any(_tag_matches(name, model) for name in tags):
            logger.warning("Pull finished but %s not in tags yet: %s", model, tags)

    def confirm_install_ollama(self) -> Dict[str, Any]:
        """Run the official Linux install only after an explicit UI confirm."""
        self._set(phase="installing", message="Installing Ollama…", percent=10)
        try:
            subprocess.run(
                ["bash", "-lc", INSTALL_HINT],
                check=True,
                timeout=600,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            self._set(
                phase="need_ollama",
                error=str(exc),
                message="Install did not finish. You can paste the command in a terminal, then press Continue.",
            )
            return self.snapshot()
        return self.ensure()


_BOOTSTRAP: Optional[Bootstrapper] = None
_BOOTSTRAP_LOCK = threading.Lock()


def get_bootstrapper() -> Bootstrapper:
    global _BOOTSTRAP
    with _BOOTSTRAP_LOCK:
        if _BOOTSTRAP is None:
            _BOOTSTRAP = Bootstrapper()
        return _BOOTSTRAP


def reset_bootstrapper() -> None:
    global _BOOTSTRAP
    with _BOOTSTRAP_LOCK:
        _BOOTSTRAP = None

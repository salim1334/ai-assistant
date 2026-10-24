"""Local data paths for BDFG customer installs."""

from __future__ import annotations

import os
from pathlib import Path


def bdfg_home() -> Path:
    override = (os.environ.get("BDFG_HOME") or "").strip()
    if override:
        path = Path(override).expanduser()
    else:
        path = Path.home() / ".bdfg"
    path.mkdir(parents=True, exist_ok=True)
    return path


def assistants_root() -> Path:
    override = (os.environ.get("BDFG_ASSISTANTS_DIR") or "").strip()
    if override:
        path = Path(override).expanduser()
    else:
        path = Path.home() / "BDFG" / "assistants"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path() -> Path:
    return bdfg_home() / "state.json"


def secrets_path() -> Path:
    return bdfg_home() / "secrets.json"

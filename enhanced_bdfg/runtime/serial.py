"""Optional CID serial lock around local-model work on this host."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager, nullcontext
from typing import Iterator

logger = logging.getLogger(__name__)


def _lock_context():
    if os.environ.get("BDFG_SKIP_SERIAL_LOCK") == "1":
        return nullcontext()
    cid_home = os.environ.get("CID_HOME") or "/home/c/Documents/CID"
    lock_dir = os.path.join(
        cid_home,
        "09 - Templates & Automation System",
        "Scripts",
        "local_models",
    )
    lock_file = os.path.join(lock_dir, "serial_lock.py")
    if not os.path.isfile(lock_file):
        return nullcontext()
    if lock_dir not in sys.path:
        sys.path.insert(0, lock_dir)
    try:
        from serial_lock import serial_model_lock  # type: ignore
    except Exception as exc:
        logger.debug("serial_lock unavailable: %s", exc)
        return nullcontext()
    return serial_model_lock()


@contextmanager
def local_model_lock() -> Iterator[None]:
    """Acquire the CID local-model lock when that toolkit is present."""
    ctx = _lock_context()
    with ctx:
        yield

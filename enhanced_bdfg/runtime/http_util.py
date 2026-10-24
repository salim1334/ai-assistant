"""Small HTTP helpers (stdlib first) so Ollama/cloud calls work without extra deps."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterator, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def http_json(
    url: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 60.0,
) -> Tuple[int, Any]:
    """POST/GET JSON. Returns (status, parsed-or-text)."""
    body = None
    hdrs = {"Accept": "application/json", **(headers or {})}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = Request(url, data=body, headers=hdrs, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, _parse(raw)
    except URLError as exc:
        logger.debug("HTTP failed %s: %s", url, exc)
        raise
    return status, _parse(raw)


def http_stream_json_lines(
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 600.0,
) -> Iterator[Dict[str, Any]]:
    """Yield JSON objects from a streamed NDJSON response."""
    body = json.dumps(payload).encode("utf-8")
    hdrs = {"Content-Type": "application/json", "Accept": "application/json", **(headers or {})}
    req = Request(url, data=body, headers=hdrs, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        while True:
            line = resp.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError:
                continue


def _parse(raw: str) -> Any:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw

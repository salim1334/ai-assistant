"""Data integration layer — connectors used by generated assistants."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


class CSVConnector:
    """Load tabular business data from CSV without requiring live POS APIs."""

    def load(self, path: str) -> List[Dict[str, Any]]:
        import csv

        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))


class MemoryConnector:
    """In-memory rows for tests and offline Ethiopia demos."""

    def __init__(self, rows: Iterable[Dict[str, Any]] = ()):
        self.rows = list(rows)

    def load(self) -> List[Dict[str, Any]]:
        return list(self.rows)

from __future__ import annotations

from collections import UserDict
from collections.abc import AsyncGenerator, AsyncIterator, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from braidpipe.telemetry.spool import Spool


@dataclass(frozen=True)
class _SpoolRef:
    """Lightweight marker stored in the dict. The real payload lives in SQLite."""
    key: str


class BraidContext(UserDict):
    """
    A dict-like namespace. Scalars live in RAM.
    Collections, large strings, and extension responses auto-spill to SQLite.
    """

    def __init__(self, spool: Spool, run_id: str | None = None):
        super().__init__()
        self._spool = spool
        self.run_id: str = run_id or str(uuid4())
        self.started_at: str = datetime.now(UTC).isoformat()

    def __setitem__(self, key: str, value: Any) -> None:
        # Reject generators/streams immediately
        if isinstance(value, (Iterator, AsyncIterator, AsyncGenerator)):
            raise TypeError(
                f"Cannot store {type(value).__name__} in BraidContext. "
                "Streams must be consumed or passed through the pipeline."
            )

        # Reject raw bytes too (they have their own spool path)
        if isinstance(value, bytes):
            raise TypeError(
                "Raw bytes must be written via spool.write_bytes(), not stored in context."
            )
        if isinstance(value, (list, dict, set, tuple)):
            # Always spill collections to SQLite
            self._spool.write(self.run_id, key, value)
            super().__setitem__(key, _SpoolRef(key))
        elif isinstance(value, str) and len(value) > 1024:
            # Spill large strings (SQL queries, JSON blobs, etc.)
            self._spool.write(self.run_id, key, value)
            super().__setitem__(key, _SpoolRef(key))
        elif isinstance(value, bytes):
            self._spool.write(self.run_id, key, value)
            super().__setitem__(key, _SpoolRef(key))
        else:
            # Scalars: int, float, bool, short str, datetime
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        value = super().__getitem__(key)
        if isinstance(value, _SpoolRef):
            return self._spool.read(self.run_id, value.key)
        return value

    def __delitem__(self, key: str) -> None:
        if key in self.data and isinstance(self.data[key], _SpoolRef):
            self._spool.delete(self.run_id, key)
        super().__delitem__(key)

    def now_iso(self):
        return datetime.now(UTC).isoformat()

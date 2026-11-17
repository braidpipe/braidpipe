from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class _SpoolRef:
    """Lightweight marker stored in BraidContext. The payload lives in SQLite."""
    key: str


class Spool:
    """
    Temporary SQLite-backed storage for collections and large values.
    Scoped per Braid run. Deleted after clean execution.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spool (
                    run_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT,
                    value_bytes BLOB,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    PRIMARY KEY (run_id, key)
                ) WITHOUT ROWID
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_spool_lookup
                ON spool(run_id, key)
            """)
            conn.commit()

    def write(self, run_id: str, key: str, value: Any) -> None:
        """
        Serialize and store a value.
        Collections and scalars go to JSON. Raw bytes go to BLOB.
        """
        if isinstance(value, bytes):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO spool (run_id, key, value_bytes)
                    VALUES (?, ?, ?)
                    ON CONFLICT(run_id, key) DO UPDATE SET
                        value_json = excluded.value_json,
                        value_bytes = excluded.value_bytes,
                        created_at = datetime('now')
                    """,
                    (run_id, key, value),
                )
                conn.commit()
        else:
            # JSON encode everything else (list, dict, int, str, float, bool)
            payload = json.dumps(value, default=str)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO spool (run_id, key, value_json)
                    VALUES (?, ?, ?)
                    ON CONFLICT(run_id, key) DO UPDATE SET
                        value_json = excluded.value_json,
                        value_bytes = excluded.value_bytes,
                        created_at = datetime('now')
                    """,
                    (run_id, key, payload),
                )
                conn.commit()

    def read(self, run_id: str, key: str) -> Any | None:
        """Hydrate a value from SQLite. Returns None if missing."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value_json, value_bytes FROM spool WHERE run_id = ? AND key = ?",
                (run_id, key),
            ).fetchone()

        if row is None:
            return None

        value_json, value_bytes = row

        if value_bytes is not None:
            return value_bytes

        if value_json is not None:
            return json.loads(value_json)

        return None

    def delete(self, run_id: str, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM spool WHERE run_id = ? AND key = ?",
                (run_id, key),
            )
            conn.commit()

    def clear_run(self, run_id: str) -> None:
        """Wipe all entries for a given run_id. Call after successful execution."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM spool WHERE run_id = ?", (run_id,))
            conn.commit()

    def close(self) -> None:
        """No persistent connection to close (we use context managers), but kept for symmetry."""
        pass

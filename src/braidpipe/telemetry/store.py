import json
import sqlite3
from datetime import UTC, datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / ".braidpipe" / "events.db"


LEVEL_INFO = "INFO"
LEVEL_WARNING = "WARNING"
LEVEL_ERROR = "ERROR"

STEP_ENGINE = "engine"

EVENT_TYPE_RUN_START = "run_start"
EVENT_TYPE_FETCH_START = "fetch_start"
EVENT_TYPE_PUSH_COMPLETE = "push_complete"
EVENT_TYPE_RUN_FAILED = "run_failed"


class TelemetryStore:
    def __init__(self, db_path: Path, run_id: str):
        self.run_id = run_id
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    level TEXT,
                    step TEXT,
                    event_type TEXT,
                    payload_json TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs (run_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_run ON events(run_id)
            """)
            conn.commit()

    def log_event(self, level: str, step: str | None,
                  event_type: str, payload: dict):
        ts = datetime.now(UTC).isoformat()
        # SQLite insert
        self.conn.execute(
            "INSERT INTO events (run_id, ts, level, step, event_type, payload_json) VALUES (?,?,?,?,?,?)",
            (self.run_id, ts, level, step, event_type, json.dumps(payload))
        )
        self.conn.commit()
        # Also emit JSON line to stdout for the TUI / external pipes
        print(json.dumps({
            "ts": ts, "run_id": self.run_id, "level": level,
            "step": step, "event_type": event_type, **payload
        }), flush=True)

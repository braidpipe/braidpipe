from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from braidpipe.telemetry.store import TelemetryStore


@pytest.fixture
def store(tmp_path: Path) -> TelemetryStore:
    return TelemetryStore(db_path=tmp_path / "events.db", run_id="run-test-001")


def test_log_event_creates_record(store: TelemetryStore, tmp_path: Path) -> None:
    store.log_event(level="INFO", step="generator", event_type="fetch_start", payload={"count": 10})

    conn = sqlite3.connect(tmp_path / "events.db")
    rows = conn.execute("SELECT * FROM events").fetchall()
    assert len(rows) == 1
    conn.close()


def test_event_has_run_id(store: TelemetryStore, tmp_path: Path) -> None:
    store.log_event(level="INFO", step="engine", event_type="run_start", payload={})

    conn = sqlite3.connect(tmp_path / "events.db")
    row = conn.execute("SELECT run_id, level, event_type FROM events").fetchone()
    assert row[0] == "run-test-001"
    assert row[1] == "INFO"
    assert row[2] == "run_start"
    conn.close()

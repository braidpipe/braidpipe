from __future__ import annotations

import sqlite3
from pathlib import Path

from braidpipe.migrations import MigrationManager


def test_migrations_create_schema_tables(db_conn: sqlite3.Connection) -> None:
    """
    After migration, core tables must exist.

    Args:
        db_conn:

    Returns:

    """
    tables = {row[0] for row in db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    assert "runs" in tables
    assert "events" in tables
    assert "spool" in tables
    assert "checkpoints" in tables
    assert "_schema_migrations" in tables


def test_migration_tracking_populated(db_conn: sqlite3.Connection) -> None:
    """
    Migration manager records applied IDs.

    Args:
        db_conn:

    Returns:

    """
    rows = db_conn.execute("SELECT id FROM _schema_migrations").fetchall()
    ids = {r[0] for r in rows}
    assert len(ids) >= 1


def test_migrations_are_idempotent(tmp_path: Path) -> None:
    """
    Running migrate twice must not crash.

    Args:
        tmp_path:

    Returns:

    """
    db_path = tmp_path / "idempotent.db"
    mgr = MigrationManager(db_path)
    mgr.migrate()
    mgr.migrate()  # second call should be harmless
    conn = sqlite3.connect(db_path)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    assert "events" in tables

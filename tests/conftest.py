from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest

from braidpipe.migrations import MigrationManager


@pytest.fixture(scope="session")
def test_db_path() -> Path:
    """
    Path to a shared test database. Wiped before session, kept for debugging.

    Returns: path to test database

    """
    path = Path(__file__).parent / ".braidpipe" / "test.db"
    path.parent.mkdir(parents=True, exist_ok=True)

    # Clean slate for each test session
    if path.exists():
        path.unlink()

    return path


@pytest.fixture(scope="function")
def db_conn(test_db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """
    Fresh connection per test, with migrated schema.

    Args:
        test_db_path:

    Returns: sqlite connection

    """

    # Wipe and remigrate for test isolation (fast enough for SQLite)
    if test_db_path.exists():
        test_db_path.unlink()

    MigrationManager(test_db_path).migrate()

    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

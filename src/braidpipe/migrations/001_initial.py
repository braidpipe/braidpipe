import sqlite3

"""Create events and runs tables."""


def up(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            playbook_path TEXT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT CHECK(status IN ('running', 'success', 'partial', 'failed', 'waiting')),
            records_in INTEGER,
            records_out INTEGER,
            error_summary TEXT
        )
    """)

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


def down(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS events")
    conn.execute("DROP TABLE IF EXISTS runs")

import sqlite3

"""Add spool and checkpoints tables for auto-spill context."""


def up(conn: sqlite3.Connection) -> None:
    # Temporary spill storage for collections and large values between steps
    conn.execute("""
        CREATE TABLE IF NOT EXISTS spool (
            run_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (run_id, key)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_spool_lookup 
        ON spool(run_id, key)
    """)

    # Source-specific resume state for checkpoint/restart
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            step TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(run_id, step, key)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_checkpoint_run 
        ON checkpoints(run_id)
    """)


def down(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS checkpoints")
    conn.execute("DROP TABLE IF EXISTS spool")

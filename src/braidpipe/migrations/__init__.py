from __future__ import annotations

import importlib
import pkgutil
import sqlite3
from pathlib import Path
from types import ModuleType


class MigrationManager:
    """Embedded SQLite migrations for Braidpipe. No external tools."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_migrations_table()

    def _ensure_migrations_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _schema_migrations (
                    id INTEGER PRIMARY KEY,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _applied(self, conn: sqlite3.Connection) -> set[int]:
        rows = conn.execute("SELECT id FROM _schema_migrations").fetchall()
        return {row[0] for row in rows}

    def migrate(self, direction: str = "up") -> None:
        migrations = self._load_migrations()
        if direction == "down":
            migrations.reverse()

        with sqlite3.connect(self.db_path) as conn:
            applied = self._applied(conn)

            for migration_id, module in migrations:
                is_applied = migration_id in applied

                if direction == "up" and not is_applied:
                    module.up(conn)
                    conn.execute(
                        "INSERT INTO _schema_migrations (id) VALUES (?)", (migration_id,))
                    conn.commit()

                elif direction == "down" and is_applied:
                    module.down(conn)
                    conn.execute(
                        "DELETE FROM _schema_migrations WHERE id = ?", (migration_id,))
                    conn.commit()

    def _load_migrations(self) -> list[tuple[int, ModuleType]]:
        """Auto-discover migration files: 001_name.py, 002_name.py, ..."""
        from braidpipe import migrations as pkg

        items: list[tuple[int, ModuleType]] = []
        for _, name, _ in pkgutil.iter_modules(pkg.__path__):
            if name[0].isdigit():
                mod = importlib.import_module(f"braidpipe.migrations.{name}")
                items.append((int(name.split("_")[0]), mod))

        items.sort(key=lambda item: item[0])
        return items

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"


class Checkpoint:
    """
    Simple JSON checkpoint per Braid directory.
    v0.1.0: Stores one entry per playbook (last run state).
    v0.2+: Will store per-step, per-source resume tokens.
    """

    def __init__(self, checkpoint_dir: Path) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, playbook_name: str) -> Path:
        """Named checkpoint file: my_braid.json"""
        return self.checkpoint_dir / f"{playbook_name}.json"

    def read(self, playbook_name: str) -> dict[str, Any] | None:
        path = self._path(playbook_name)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def write(self, playbook_name: str, data: dict[str, Any]) -> None:
        """Overwrite with latest run state."""
        path = self._path(playbook_name)
        payload = {
            "version": "v0.1.0",
            **data,
        }
        path.write_text(json.dumps(payload, indent=2))

    def clear(self, playbook_name: str) -> None:
        path = self._path(playbook_name)
        if path.exists():
            path.unlink()

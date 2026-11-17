from __future__ import annotations

import json
from pathlib import Path

import pytest

from braidpipe.engine.checkpoint import Checkpoint


@pytest.fixture
def checkpoint(tmp_path: Path) -> Checkpoint:
    return Checkpoint(tmp_path / "checkpoints")


def test_write_and_read(checkpoint: Checkpoint) -> None:
    checkpoint.write("stripe-sync", {"status": "success", "run_id": "abc"})
    data = checkpoint.read("stripe-sync")
    assert data is not None
    assert data["status"] == "success"
    assert data["version"] == "v0.1.0"


def test_read_missing_returns_none(checkpoint: Checkpoint) -> None:
    assert checkpoint.read("nonexistent") is None


def test_clear_removes_file(checkpoint: Checkpoint) -> None:
    checkpoint.write("tmp", {"status": "running"})
    assert (checkpoint.checkpoint_dir / "tmp.json").exists()
    checkpoint.clear("tmp")
    assert not (checkpoint.checkpoint_dir / "tmp.json").exists()


def test_playbook_name_used_for_filename(checkpoint: Checkpoint) -> None:
    checkpoint.write("my_braid", {"run_id": "x"})
    expected = checkpoint.checkpoint_dir / "my_braid.json"
    assert expected.exists()
    raw = json.loads(expected.read_text())
    assert raw["run_id"] == "x"

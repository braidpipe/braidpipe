from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
import yaml

from braidpipe.engine import runner


class _FakeSource:
    def __init__(self, config: Any, context: Any) -> None:
        self.config = config

    async def setup(self) -> None:
        pass

    async def teardown(self) -> None:
        pass

    async def fetch(self) -> AsyncIterator[dict[str, Any]]:
        for i in range(3):
            yield {"id": i, "name": f"item-{i}"}


class _FakeDest:
    def __init__(self, config: Any, context: Any) -> None:
        self.config = config
        self.received: list[dict[str, Any]] = []

    async def setup(self) -> None:
        pass

    async def teardown(self) -> None:
        pass

    async def push(self, records: AsyncIterator[dict[str, Any]]) -> None:
        async for r in records:
            self.received.append(r)


@pytest.fixture
def braid_dir(tmp_path: Path) -> Path:
    d = tmp_path / "hello_braid"
    d.mkdir()
    (d / ".braidpipe").mkdir()
    pb = {
        "version": "1",
        "sources": {"demo": {"connector": "fake_source", "config": {}}},
        "destinations": {"out": {"connector": "fake_dest", "config": {}}},
    }
    (d / "playbook.yml").write_text(yaml.dump(pb))
    return d


def test_runner_executes_end_to_end(braid_dir: Path) -> None:
    # Patch registry with fakes
    original = runner.REGISTRY
    runner.REGISTRY = {
        "connectors": {
            "fake_source": _FakeSource,
            "fake_dest": _FakeDest,
        }
    }

    try:
        playbook = braid_dir / "playbook.yml"
        asyncio.run(runner.execute(playbook))

        # Assert checkpoint written
        ckpt_path = braid_dir / ".braidpipe" / "checkpoints" / "hello_braid.json"
        assert ckpt_path.exists()

        import json
        ckpt = json.loads(ckpt_path.read_text())
        assert ckpt["status"] == "SUCCESS"
    finally:
        runner.REGISTRY = original


def test_runner_creates_events_db(braid_dir: Path) -> None:
    original = runner.REGISTRY
    runner.REGISTRY = {
        "connectors": {
            "fake_source": _FakeSource,
            "fake_dest": _FakeDest,
        }
    }

    try:
        playbook = braid_dir / "playbook.yml"
        asyncio.run(runner.execute(playbook))

        events_db = braid_dir / ".braidpipe" / "events.db"
        assert events_db.exists()
    finally:
        runner.REGISTRY = original

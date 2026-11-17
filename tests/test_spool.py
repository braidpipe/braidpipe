from __future__ import annotations

from pathlib import Path

import pytest

from braidpipe.telemetry.spool import Spool


@pytest.fixture
def spool(tmp_path: Path) -> Spool:
    return Spool(tmp_path / "spool.db")


def test_roundtrip_dict(spool: Spool) -> None:
    payload = {"a": 1, "b": [2, 3]}
    spool.write("run-1", "meta", payload)
    result = spool.read("run-1", "meta")
    assert result == payload


def test_roundtrip_list(spool: Spool) -> None:
    payload = [{"id": 1}, {"id": 2}]
    spool.write("run-1", "rows", payload)
    assert spool.read("run-1", "rows") == payload


def test_roundtrip_bytes(spool: Spool) -> None:
    raw = b"binary-payload"
    spool.write("run-1", "blob", raw)
    result = spool.read("run-1", "blob")
    assert result == raw
    assert isinstance(result, bytes)


def test_overwrite(spool: Spool) -> None:
    spool.write("run-1", "key", "first")
    spool.write("run-1", "key", "second")
    assert spool.read("run-1", "key") == "second"


def test_clear_run_removes_all(spool: Spool) -> None:
    spool.write("run-1", "a", 1)
    spool.write("run-1", "b", 2)
    spool.write("run-2", "c", 3)

    spool.clear_run("run-1")

    assert spool.read("run-1", "a") is None
    assert spool.read("run-1", "b") is None
    assert spool.read("run-2", "c") == 3


def test_read_missing_returns_none(spool: Spool) -> None:
    assert spool.read("run-x", "missing") is None

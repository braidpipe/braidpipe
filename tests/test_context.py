from __future__ import annotations

from pathlib import Path

import pytest

from braidpipe.engine.context import BraidContext
from braidpipe.telemetry.spool import Spool


@pytest.fixture
def ctx(tmp_path: Path) -> BraidContext:
    spool = Spool(tmp_path / "ctx.db")
    return BraidContext(spool=spool)


def test_scalar_stays_in_memory(ctx: BraidContext) -> None:
    ctx["token"] = "abc123"
    # Access should return directly without SQLite roundtrip for small scalars
    assert ctx["token"] == "abc123"


def test_list_auto_spills(ctx: BraidContext) -> None:
    ctx["customers"] = [{"id": 1}, {"id": 2}]
    # Internally should be a _SpoolRef, but user sees hydrated list
    assert ctx["customers"] == [{"id": 1}, {"id": 2}]


def test_large_string_auto_spills(ctx: BraidContext) -> None:
    big = "x" * 3000
    ctx["query"] = big
    assert ctx["query"] == big


def test_read_back_spilled_value(ctx: BraidContext) -> None:
    ctx["rows"] = [1, 2, 3]
    first_read = ctx["rows"]
    second_read = ctx["rows"]
    assert first_read == [1, 2, 3]
    assert second_read == [1, 2, 3]


def test_del_removes_from_spool(ctx: BraidContext) -> None:
    ctx["temp"] = [1, 2, 3]
    del ctx["temp"]
    assert "temp" not in ctx


def test_generator_rejected(ctx: BraidContext) -> None:
    async def gen():
        yield 1

    with pytest.raises(TypeError):
        ctx["bad"] = gen()

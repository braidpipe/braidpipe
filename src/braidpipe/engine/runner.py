from __future__ import annotations

import os
from pathlib import Path
from string import Template
from rich.console import Console
import typer

import yaml
from pydantic import ValidationError

from braidpipe.engine.checkpoint import Checkpoint, STATUS_SUCCESS, STATUS_FAILED
from braidpipe.engine.context import BraidContext
from braidpipe.extensions.connectors.generator import GeneratorSource
from braidpipe.extensions.connectors.stdin import StdinSource
from braidpipe.extensions.connectors.stdout import StdoutDestination
from braidpipe.extensions.sdk import DestinationConnector, SourceConnector
from braidpipe.telemetry.spool import Spool
from braidpipe.telemetry.store import (TelemetryStore, LEVEL_ERROR, LEVEL_INFO, STEP_ENGINE, EVENT_TYPE_RUN_START,
                                       EVENT_TYPE_FETCH_START, EVENT_TYPE_PUSH_COMPLETE, EVENT_TYPE_RUN_FAILED)
from braidpipe.engine.playbook import Playbook

REGISTRY = {
    "connectors": {
        "generator": GeneratorSource,
        "stdin": StdinSource,
        "stdout": StdoutDestination,
    }
}


async def execute(playbook_path: Path, follow: bool = False) -> None:
    """
    Execute a single Braid.
    v0.1.0 scope:
      - Multiple sources/destinations allowed in YAML grammar
      - Engine processes first source → first destination as a pure stream
      - No transforms yet
      - One checkpoint per playbook (run-level only)
    """
    braid_dir = playbook_path.parent
    state_dir = braid_dir / ".braidpipe"
    state_dir.mkdir(exist_ok=True)

    # --- Load & interpolate env vars ---
    raw_text = playbook_path.read_text()
    expanded = Template(raw_text).safe_substitute(os.environ)
    raw = yaml.safe_load(expanded)

    # --- Normalize playbook ---
    try:
        playbook = Playbook(**raw)
        sources_cfg = playbook.sources
        destinations_cfg = playbook.destinations
        playbook_name = playbook.name or braid_dir.name
    except ValidationError as e:
        console = Console(stderr=True)
        console.print("[bold red]Braid validation error[/bold red]")
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            msg = error["msg"]
            console.print(f"  [red]•[/red] [yellow]{loc}[/yellow]: {msg}")
        raise typer.Exit(code=1)

    # --- Infrastructure per run ---
    spool = Spool(state_dir / "spool.db")
    ctx = BraidContext(spool=spool)
    checkpoint = Checkpoint(state_dir / "checkpoints")
    store = TelemetryStore(db_path=state_dir / "events.db", run_id=ctx.run_id)

    # Log start
    store.log_event(level=LEVEL_INFO, step=STEP_ENGINE, event_type=EVENT_TYPE_RUN_START,
                    payload={"playbook": str(playbook_path)})

    # --- Instantiate connectors ---
    source_instances: list[tuple[str, SourceConnector]] = []
    for name, cfg in sources_cfg.items():
        cls = REGISTRY["connectors"][cfg.connector]
        instance = cls(config=cfg.config, context=ctx)
        await instance.setup()
        source_instances.append((name, instance))

    dest_instances: list[tuple[str, DestinationConnector]] = []
    for name, cfg in destinations_cfg.items():
        cls = REGISTRY["connectors"][cfg.connector]
        instance = cls(config=cfg.config, context=ctx)
        await instance.setup()
        dest_instances.append((name, instance))

    try:
        # --- v0.1.0: Stream first source to first destination ---
        # Future v0.2: async tee for multi-destination, transforms, joins
        if not source_instances:
            raise ValueError("No sources defined")
        if not dest_instances:
            raise ValueError("No destinations defined")

        src_name, source = source_instances[0]
        dst_name, dest = dest_instances[0]

        store.log_event(
            level=LEVEL_INFO, step=src_name, event_type=EVENT_TYPE_FETCH_START, payload={}
        )

        stream = source.fetch()
        await dest.push(stream)

        store.log_event(
            level=LEVEL_INFO, step=dst_name, event_type=EVENT_TYPE_PUSH_COMPLETE, payload={}
        )

        # Mark success
        checkpoint.write(
            playbook_name,
            {
                "run_id": ctx.run_id,
                "status": STATUS_SUCCESS,
                "finished_at": ctx.now_iso(),
            },
        )

    except Exception as exc:
        store.log_event(
            level=LEVEL_ERROR,
            step=STEP_ENGINE,
            event_type=EVENT_TYPE_RUN_FAILED,
            payload={"error": str(exc)},
        )
        checkpoint.write(
            playbook_name,
            {
                "run_id": ctx.run_id,
                "status": STATUS_FAILED,
                "error": str(exc),
            },
        )
        raise

    finally:
        # --- Teardown in reverse order ---
        for name, dest in dest_instances:
            await dest.teardown()

        for name, source in source_instances:
            await source.teardown()

        spool.clear_run(ctx.run_id)

        console = Console()
        console.print(f"[green]Braid completed:[/green] {ctx.run_id}")

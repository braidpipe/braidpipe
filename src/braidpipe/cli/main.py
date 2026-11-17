from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from braidpipe.engine import runner
from braidpipe.utils.platform import get_braidpipe_home, get_braids_dir

app = typer.Typer(
    name="braidpipe",
    help="Async data orchestration in YAML. One playbook, one Braid.",
    no_args_is_help=True,
)
console = Console()


def _get_playbook_path(path_str: str) -> Path:
    p = Path(path_str).expanduser().resolve()
    if not p.exists():
        console.print(f"[red]Playbook not found:[/red] {p}")
        raise typer.Exit(code=1)
    return p


@app.command()
def run(
    playbook: Annotated[str, typer.Argument(help="Path to playbook YAML")],
    follow: Annotated[
        bool, typer.Option("--follow", "-f", help="Continuous/streaming mode")
    ] = False,
) -> None:
    """
    Execute a single Braid

    Args:
        playbook: path to playbook
        follow: Whether run continuously or streaming

    Returns: None

    """
    pb_path = _get_playbook_path(playbook)
    asyncio.run(runner.execute(pb_path, follow=follow))


@app.command()
def init(
    name: Annotated[str, typer.Argument(help="Name of the new Braid")],
    path: Annotated[
        str | None, typer.Option("--path", "-p", help="Parent directory")
    ] = None,
) -> None:
    """

    Args:
        name: Name of the new Braid
        path: Parent directory

    Returns: None

    """
    root = Path(path).expanduser().resolve() if path else get_braids_dir()
    console.print(f"[green]root: {root}[/green]")
    braid_dir = root / name

    if braid_dir.exists():
        console.print(f"[red]Already exists:[/red] {braid_dir}")
        raise typer.Exit(code=1)

    braid_dir.mkdir(parents=True)
    (braid_dir / ".braidpipe").mkdir()
    (braid_dir / ".env").touch()
    (braid_dir / "playbook.yml").write_text(
        f'version: "1"\nname: "{name}"\n\nsource:\n  connector: generator\n  config:\n    '
        'count: 10\n\ndestination:\n  connector: stdout\n'
    )

    console.print(f"[green]Created Braid:[/green] {braid_dir}")


@app.callback(invoke_without_command=True)
def main(
    _version: Annotated[
        bool, typer.Option("--version", "-v", help="Show version")
    ] = False,
) -> None:
    """
    Main console

    Args:
        _version: Bool whether to show the version

    Returns: None

    """
    if _version:
        from braidpipe import __version__

        console.print(__version__)
        raise typer.Exit()


if __name__ == "__main__":
    app()

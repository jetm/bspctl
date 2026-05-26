"""bspctl doctor subcommand - pre-flight checks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import typer

import bspctl.commands._app as _state
from bspctl.commands._app import app, console
from bspctl.commands._helpers import (
    _bbsetup_workspace,
    _dispatch_bsp,
    _dispatch_from_yaml,
    _print_diagnosis,
    _resolve_workspace,
)
from bspctl.config import resolve
from bspctl.diagnostics import any_blocking_failure, run_all

if TYPE_CHECKING:
    from pathlib import Path


@app.command()
def doctor(
    kas_yaml: Annotated[
        Path | None,
        typer.Argument(
            exists=False,
            help="Optional kas YAML; when supplied, BSP family is inferred from it instead of --manifest.",
        ),
    ] = None,
    manifest: Annotated[
        str | None,
        typer.Option("--manifest", "-f", help="Manifest filename used to dispatch BSP family"),
    ] = None,
    workspace: Annotated[
        Path | None,
        typer.Option("--workspace", "-w", help="Workspace root; auto-detected if omitted"),
    ] = None,
) -> None:
    """Run every diagnostic check and exit non-zero on BLOCK failures."""
    if kas_yaml is not None and manifest is not None:
        console.print("[red]choose either a positional kas YAML or --manifest, not both[/]")
        raise typer.Exit(code=2)

    setup_dir = _bbsetup_workspace(workspace) if kas_yaml is None and manifest is None else None
    if setup_dir is not None:
        cfg = resolve(
            workspace=setup_dir,
            bsp_family="bbsetup",
            user_config=_state._USER_CONFIG,
        )
        results = run_all(cfg, None)
        _print_diagnosis(results)
        if any_blocking_failure(results):
            raise typer.Exit(code=2)
        return

    if kas_yaml is not None:
        family, bsp = _dispatch_from_yaml(kas_yaml)
    else:
        family, bsp = _dispatch_bsp(manifest)

    cfg = resolve(
        workspace=_resolve_workspace(workspace, kas_yaml=kas_yaml, family=family),
        bsp_family=family,
        manifest=manifest,
        kas_yaml=kas_yaml,
        user_config=_state._USER_CONFIG,
    )
    results = run_all(cfg, bsp)
    _print_diagnosis(results)
    if any_blocking_failure(results):
        raise typer.Exit(code=2)

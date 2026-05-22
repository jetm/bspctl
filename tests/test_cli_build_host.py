"""Tests for the ``bspctl build --host`` flag.

Covers CLI parsing only: invoking ``bspctl build <yaml> --host`` must
flip ``BuildConfig.host_mode`` to ``True`` through the existing
``resolve()`` plumbing, and omitting the flag must default to ``False``.

The actual kas/kas-container invocation is short-circuited via
``--dry-run`` plus ``--skip-doctor`` so these tests stay at the
argument-parsing layer, mirroring the pattern in
``tests/test_cli_build_yaml.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

import bspctl.cli as cli_module
from bspctl.cli import app
from bspctl.config import BuildConfig
from bspctl.config import resolve as real_resolve

if TYPE_CHECKING:
    from pathlib import Path


def _make_generic_yaml(tmp_path: Path) -> Path:
    """Write a minimal generic kas YAML and return its path."""
    pilots = tmp_path / "pilot"
    pilots.mkdir()
    kas_yaml = pilots / "kas.yml"
    kas_yaml.write_text("machine: qemux86-64\n")
    return kas_yaml


def _capturing_resolve(captured: list[BuildConfig]):
    """Build a resolve wrapper that records the produced BuildConfig."""

    def _wrapper(**kwargs: object) -> BuildConfig:
        cfg = real_resolve(**kwargs)  # type: ignore[arg-type]
        captured.append(cfg)
        return cfg

    return _wrapper


@pytest.fixture(autouse=True)
def _reset_vendors() -> None:
    """Vendor cache leaks across tests; reset it before each run."""
    cli_module._VENDORS = None


def test_build_host_flag_sets_host_mode(tmp_path: Path) -> None:
    """``bspctl build <yaml> --host`` must produce ``host_mode=True``."""
    kas_yaml = _make_generic_yaml(tmp_path)
    captured: list[BuildConfig] = []
    runner = CliRunner()

    with (
        patch("bspctl.cli.load_vendors", return_value=[]),
        patch("bspctl.cli.resolve", side_effect=_capturing_resolve(captured)),
    ):
        result = runner.invoke(
            app,
            ["build", str(kas_yaml), "--host", "--skip-doctor", "--dry-run"],
        )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    assert captured[0].host_mode is True


def test_build_no_host_flag_defaults_false(tmp_path: Path) -> None:
    """Without ``--host`` the resolved BuildConfig keeps ``host_mode=False``."""
    kas_yaml = _make_generic_yaml(tmp_path)
    captured: list[BuildConfig] = []
    runner = CliRunner()

    with (
        patch("bspctl.cli.load_vendors", return_value=[]),
        patch("bspctl.cli.resolve", side_effect=_capturing_resolve(captured)),
    ):
        result = runner.invoke(
            app,
            ["build", str(kas_yaml), "--skip-doctor", "--dry-run"],
        )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    assert captured[0].host_mode is False

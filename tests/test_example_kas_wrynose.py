"""Tests for examples/kas-qemux86-64-wrynose.yml.

Validates the YAML structure and expected fields without running a live build.
The integration test (dry-run) is marked as such and skipped in CI where
the local yocto repo checkouts are absent.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

import bspctl.cli as cli_module
from bspctl.cli import app

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_YAML = REPO_ROOT / "examples" / "kas-qemux86-64-wrynose.yml"

_REQUIRED_REPOS = ("openembedded-core", "meta-openembedded")
_OE_CORE_PATH = Path("/home/tiamarin/repos/personal/yocto/openembedded-core")
_META_OE_PATH = Path("/home/tiamarin/repos/personal/yocto/meta-openembedded")

_local_repos_present = pytest.mark.skipif(
    not (_OE_CORE_PATH.is_dir() and _META_OE_PATH.is_dir()),
    reason="local Yocto repos not present",
)


@pytest.fixture(autouse=True)
def _reset_vendors() -> None:
    cli_module._VENDORS = None


@pytest.fixture
def kas_doc() -> dict:
    assert EXAMPLE_YAML.is_file(), f"example YAML missing: {EXAMPLE_YAML}"
    return yaml.safe_load(EXAMPLE_YAML.read_text(encoding="utf-8"))


def test_example_yaml_parses(kas_doc: dict) -> None:
    assert isinstance(kas_doc, dict)


def test_example_yaml_has_kas_header(kas_doc: dict) -> None:
    assert kas_doc.get("header", {}).get("version") == 3


def test_example_yaml_targets_qemux86_64(kas_doc: dict) -> None:
    assert kas_doc.get("machine") == "qemux86-64"


def test_example_yaml_targets_core_image_minimal(kas_doc: dict) -> None:
    assert kas_doc.get("target") == "core-image-minimal"


def test_example_yaml_has_required_repos(kas_doc: dict) -> None:
    repos = kas_doc.get("repos") or {}
    for name in _REQUIRED_REPOS:
        assert name in repos, f"missing repo: {name!r}"


def test_example_yaml_no_explicit_bitbake_repo(kas_doc: dict) -> None:
    """bitbake is found by oe-init-build-env at ../bitbake; no kas repo entry needed."""
    repos = kas_doc.get("repos") or {}
    assert "bitbake" not in repos, "bitbake must not be listed as a kas repo"


def test_example_yaml_oe_core_uses_local_path(kas_doc: dict) -> None:
    repo = kas_doc["repos"]["openembedded-core"]
    assert repo.get("url") is None, "openembedded-core must use a local path (url: null)"
    assert Path(repo["path"]) == _OE_CORE_PATH


def test_example_yaml_meta_oe_uses_local_path(kas_doc: dict) -> None:
    repo = kas_doc["repos"]["meta-openembedded"]
    assert repo.get("url") is None, "meta-openembedded must use a local path (url: null)"
    assert Path(repo["path"]) == _META_OE_PATH


def test_example_yaml_oe_core_includes_meta_layer(kas_doc: dict) -> None:
    layers = kas_doc["repos"]["openembedded-core"].get("layers") or {}
    assert "meta" in layers


def test_example_yaml_meta_oe_includes_core_layers(kas_doc: dict) -> None:
    layers = kas_doc["repos"]["meta-openembedded"].get("layers") or {}
    assert "meta-oe" in layers


@_local_repos_present
def test_example_yaml_dry_run_succeeds(tmp_path: Path, monkeypatch) -> None:
    """Dry-run bspctl build with the wrynose example YAML.

    Applies the generic tuning overlay and exits before invoking kas.
    Requires the local Yocto repo checkouts to be present.
    """
    monkeypatch.delenv("KAS_CONTAINER_IMAGE", raising=False)
    runner = CliRunner()
    with patch("bspctl.cli.load_vendors", return_value=[]):
        result = runner.invoke(
            app,
            ["build", str(EXAMPLE_YAML), "--skip-doctor", "--dry-run"],
        )
    assert result.exit_code == 0, result.output

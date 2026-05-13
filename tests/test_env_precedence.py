"""Tests for env var precedence rules (spec: env-var-namespace).

Verifies the three-level stack in :func:`bspctl.config.resolve`:

1. CLI flag (explicit arg) beats env var.
2. Env var beats BSP-family default.
3. Legacy ``VARIS_*`` env vars are silently ignored once task 4.1
   (VARIS_ -> BSPCTL_ rename) is complete.

NOTE: The source currently reads ``VARIS_*`` env vars (task 4.1 not yet
landed). Tests 1 and 2 use the current ``VARIS_*`` names so they pass
against the current source and document correct precedence behaviour.
Tests in group 3 are marked ``xfail`` and will pass (xpass -> pass) once
task 4.1 flips the source to ``BSPCTL_*``. At that point, also update
the ``ENV_VAR`` constant at the top of each group to use ``BSPCTL_*``.
"""

from __future__ import annotations

import pytest

from bspctl.config import (
    DEFAULT_NXP_MACHINE,
    DEFAULT_NXP_MANIFEST,
    resolve,
)

# ---------------------------------------------------------------------------
# Switch these to "BSPCTL_*" once task 4.1 lands.
# ---------------------------------------------------------------------------
_MACHINE_VAR = "VARIS_MACHINE"
_MANIFEST_VAR = "VARIS_MANIFEST"
_DISTRO_VAR = "VARIS_DISTRO"
_IMAGE_VAR = "VARIS_IMAGE"
_BSPCTL_MACHINE_VAR = "BSPCTL_MACHINE"  # target name (post-4.1)
_BSPCTL_MANIFEST_VAR = "BSPCTL_MANIFEST"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _workspace(tmp_path):
    """Return a workspace path with the nxp subdir present."""
    (tmp_path / "nxp").mkdir(parents=True, exist_ok=True)
    return tmp_path


# ---------------------------------------------------------------------------
# 1. CLI flag beats env var
#
# These tests pass now because resolve() honours the explicit arg
# regardless of which env var name the source reads.
# ---------------------------------------------------------------------------


def test_cli_machine_beats_env(tmp_path, monkeypatch):
    """Explicit machine arg must win over the active machine env var."""
    monkeypatch.setenv(_MACHINE_VAR, "env-board")

    cfg = resolve(
        workspace=_workspace(tmp_path),
        bsp_family="nxp",
        machine="my-board",  # CLI flag
    )

    assert cfg.machine == "my-board", f"CLI flag 'machine' must override {_MACHINE_VAR}"


def test_cli_manifest_beats_env(tmp_path, monkeypatch):
    """Explicit manifest arg must win over the active manifest env var."""
    monkeypatch.setenv(_MANIFEST_VAR, "imx-6.12.49-2.2.0.xml")

    cfg = resolve(
        workspace=_workspace(tmp_path),
        bsp_family="nxp",
        manifest="imx-6.6.52-2.2.2.xml",  # CLI flag
    )

    assert cfg.manifest == "imx-6.6.52-2.2.2.xml", f"CLI flag 'manifest' must override {_MANIFEST_VAR}"


def test_cli_distro_beats_env(tmp_path, monkeypatch):
    """Explicit distro arg must win over the active distro env var."""
    monkeypatch.setenv(_DISTRO_VAR, "fsl-imx-wayland")

    cfg = resolve(
        workspace=_workspace(tmp_path),
        bsp_family="nxp",
        distro="fsl-imx-xwayland",  # CLI flag
    )

    assert cfg.distro == "fsl-imx-xwayland", f"CLI flag 'distro' must override {_DISTRO_VAR}"


# ---------------------------------------------------------------------------
# 2. Env var beats default
#
# Uses the current VARIS_* names.  After task 4.1, update _MACHINE_VAR etc.
# ---------------------------------------------------------------------------


def test_env_machine_beats_default(tmp_path, monkeypatch):
    """Active machine env var must override the BSP-family default machine."""
    monkeypatch.setenv(_MACHINE_VAR, "imx8mm-var-dart")

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.machine == "imx8mm-var-dart", f"{_MACHINE_VAR} env var must beat default ({DEFAULT_NXP_MACHINE!r})"
    assert cfg.machine != DEFAULT_NXP_MACHINE


def test_env_manifest_beats_default(tmp_path, monkeypatch):
    """Active manifest env var must override the BSP-family default manifest."""
    monkeypatch.setenv(_MANIFEST_VAR, "imx-6.12.49-2.2.0.xml")

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.manifest == "imx-6.12.49-2.2.0.xml", (
        f"{_MANIFEST_VAR} env var must beat default ({DEFAULT_NXP_MANIFEST!r})"
    )


def test_env_image_beats_default(tmp_path, monkeypatch):
    """Active image env var must override the BSP-family default image."""
    monkeypatch.setenv(_IMAGE_VAR, "fsl-image-qt5")

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.image == "fsl-image-qt5", f"{_IMAGE_VAR} env var must beat the NXP default image"


def test_no_env_yields_default(tmp_path, monkeypatch):
    """Without CLI flags or env vars the BSP-family default is used."""
    monkeypatch.delenv(_MACHINE_VAR, raising=False)
    monkeypatch.delenv(_BSPCTL_MACHINE_VAR, raising=False)

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.machine == DEFAULT_NXP_MACHINE, "Absent env + no CLI flag must fall back to BSP-family default"


# ---------------------------------------------------------------------------
# 3. Legacy VARIS_* env vars are silently ignored  (post-task-4.1)
#
# These are the spec's intended invariants once the source is renamed to
# BSPCTL_*.  Marked xfail so they document intent today and auto-promote to
# passing after task 4.1 ships.
# ---------------------------------------------------------------------------

_REASON_PRE_41 = "task 4.1 not yet landed: source still reads VARIS_* instead of BSPCTL_*"


@pytest.mark.xfail(reason=_REASON_PRE_41, strict=True)
def test_legacy_varis_machine_is_ignored(tmp_path, monkeypatch):
    """VARIS_MACHINE must have no effect once source uses BSPCTL_MACHINE."""
    monkeypatch.setenv("VARIS_MACHINE", "legacy-board")
    monkeypatch.delenv("BSPCTL_MACHINE", raising=False)

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.machine == DEFAULT_NXP_MACHINE, (
        "VARIS_MACHINE must be silently ignored; default should be used when BSPCTL_MACHINE is absent"
    )


@pytest.mark.xfail(reason=_REASON_PRE_41, strict=True)
def test_legacy_varis_manifest_is_ignored(tmp_path, monkeypatch):
    """VARIS_MANIFEST must have no effect once source uses BSPCTL_MANIFEST."""
    monkeypatch.setenv("VARIS_MANIFEST", "imx-6.12.49-2.2.0.xml")
    monkeypatch.delenv("BSPCTL_MANIFEST", raising=False)

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.manifest == DEFAULT_NXP_MANIFEST, (
        "VARIS_MANIFEST must be silently ignored; default should be used when BSPCTL_MANIFEST is absent"
    )


@pytest.mark.xfail(reason=_REASON_PRE_41, strict=True)
def test_bspctl_env_wins_over_varis_env(tmp_path, monkeypatch):
    """When both BSPCTL_MACHINE and VARIS_MACHINE are set, BSPCTL_ wins."""
    monkeypatch.setenv("BSPCTL_MACHINE", "bspctl-board")
    monkeypatch.setenv("VARIS_MACHINE", "varis-board")

    cfg = resolve(workspace=_workspace(tmp_path), bsp_family="nxp")

    assert cfg.machine == "bspctl-board", "BSPCTL_MACHINE must win over VARIS_MACHINE when both are set"

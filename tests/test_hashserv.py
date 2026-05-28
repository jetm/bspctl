"""Unit tests for bspctl.hashserv pure helpers and is_running predicate.

Covers the deterministic port derivation, the workspace-pinned binary
lookup (which explicitly must NOT fall through to host PATH), and the
PID-file + cmdline-based liveness probe in ``is_running``. The cmdline
check is what guards against PID recycling - a stale PID file pointing
at a now-unrelated process must not look "running" to the rest of the
pipeline.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from bspctl.hashserv import _find_binary, _workspace_port, is_running

pytestmark = pytest.mark.unit


def test_workspace_port_is_deterministic(tmp_path: Path) -> None:
    """Same workspace path must always derive the same port."""
    assert _workspace_port(tmp_path) == _workspace_port(tmp_path)


def test_workspace_port_in_ephemeral_range(tmp_path: Path) -> None:
    """Derived port must fall in the IANA ephemeral range (49152-65534)."""
    port = _workspace_port(tmp_path)
    assert 49152 <= port < 65535


def test_workspace_port_differs_across_paths(tmp_path: Path) -> None:
    """Two distinct workspace paths should generally yield different ports.

    Collision probability is ~1-in-16383; two adjacent tmp_path siblings
    are independent SHA-256 inputs so a collision here would be a real
    bug, not just bad luck.
    """
    workspace_a = tmp_path / "wsA"
    workspace_b = tmp_path / "wsB"
    workspace_a.mkdir()
    workspace_b.mkdir()
    assert _workspace_port(workspace_a) != _workspace_port(workspace_b)


def test_find_binary_workspace_hit(tmp_path: Path) -> None:
    """When the workspace binary exists, its path is returned."""
    binary_path = tmp_path / "sources" / "poky" / "bitbake" / "bin" / "bitbake-hashserv"
    binary_path.parent.mkdir(parents=True)
    binary_path.write_text("#!/bin/sh\n")
    binary_path.chmod(0o755)

    result = _find_binary(tmp_path)

    assert result == binary_path


def test_find_binary_returns_none_when_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the workspace binary is absent, return None - never PATH.

    Booby-trap ``shutil.which`` so any host-PATH fallback raises; the
    spec pins the workspace path and a PATH-mismatch daemon would speak
    a different protocol than the workspace bitbake.
    """

    def _explode(*_args: object, **_kwargs: object) -> None:
        msg = "shutil.which must not be consulted - hashserv is workspace-pinned"
        raise AssertionError(msg)

    monkeypatch.setattr(shutil, "which", _explode)

    result = _find_binary(tmp_path)

    assert result is None


def _write_pid_file(workspace: Path, pid: int) -> Path:
    """Helper: write ``<workspace>/.bspctl/hashserv.pid`` with ``pid``."""
    state_dir = workspace / ".bspctl"
    state_dir.mkdir(parents=True, exist_ok=True)
    pid_file = state_dir / "hashserv.pid"
    pid_file.write_text(f"{pid}\n")
    return pid_file


def test_is_running_pid_file_absent(tmp_path: Path) -> None:
    """No PID file under .bspctl/ - the daemon cannot be running."""
    assert is_running(tmp_path) is False


def test_is_running_pid_dead(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PID file exists, but the PID itself is gone (ProcessLookupError)."""
    _write_pid_file(tmp_path, 999999)

    def _kill_raises(_pid: int, _sig: int) -> None:
        raise ProcessLookupError

    monkeypatch.setattr(os, "kill", _kill_raises)

    assert is_running(tmp_path) is False


def test_is_running_pid_recycled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PID is alive but its cmdline does not mention bitbake-hashserv.

    Simulates the post-reboot scenario where the recorded PID has been
    handed to an unrelated process (here, a shell). Without the cmdline
    guard, ``is_running`` would mistakenly report True.
    """
    _write_pid_file(tmp_path, 12345)

    monkeypatch.setattr(os, "kill", lambda _pid, _sig: None)

    real_read_bytes = Path.read_bytes

    def _fake_read_bytes(self: Path) -> bytes:
        if str(self).startswith("/proc/"):
            # NUL-separated argv for a shell process - no bitbake-hashserv.
            return b"/bin/bash\x00-l\x00"
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _fake_read_bytes)

    assert is_running(tmp_path) is False


def test_is_running_pid_alive_correct_cmdline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PID alive AND its cmdline contains bitbake-hashserv - True."""
    _write_pid_file(tmp_path, 12345)

    monkeypatch.setattr(os, "kill", lambda _pid, _sig: None)

    real_read_bytes = Path.read_bytes

    def _fake_read_bytes(self: Path) -> bytes:
        if str(self).startswith("/proc/"):
            return (
                b"/usr/bin/python3\x00"
                b"/workspace/sources/poky/bitbake/bin/bitbake-hashserv\x00"
                b"--bind\x00ws://localhost:50000\x00"
            )
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _fake_read_bytes)

    assert is_running(tmp_path) is True

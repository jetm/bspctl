"""Layer git-hash collection.

Enumerates the repos backing the layers in a build's ``bblayers.conf``
and reports each repo's short git hash and current branch. Discovery
reuses :func:`bspctl.kas.parse_bblayers` rather than re-parsing the
bblayers file. Git invocations never raise: a repo whose checkout is
missing or whose ``git`` command fails is silently skipped (or, for the
branch query, reported with an empty branch - a valid detached HEAD).
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from bspctl.kas import parse_bblayers

if TYPE_CHECKING:
    from bspctl.config import BuildConfig


@dataclass
class LayerHash:
    repo: str
    short_hash: str
    branch: str  # empty string for a detached HEAD


def _resolve_bblayers_paths(bblayers_conf: Path) -> dict[str, Path]:
    """Resolve TOPDIR-relative paths in bblayers.conf to {repo_name: git_root}.

    Used for generic BYO builds where BBLAYERS uses ``${TOPDIR}/../layers/``
    rather than the ``/work/sources/`` convention of NXP/TI container builds.
    Deduplicates by git root so multiple sublayers from one repo produce a
    single entry keyed on the repo directory basename.
    """
    build_dir = bblayers_conf.parent.parent  # build/conf/bblayers.conf -> build/
    topdir = str(build_dir)
    text = bblayers_conf.read_text()
    joined = " ".join(line.split("#", 1)[0] for line in text.splitlines()).replace("\\", " ")
    matches = re.findall(r'BBLAYERS\s*(?:\?\??|\+)?=\s*"([^"]*)"', joined)
    seen: set[Path] = set()
    result: dict[str, Path] = {}
    for body in matches:
        for token in body.split():
            token = token.strip().replace("${TOPDIR}", topdir)
            if not token:
                continue
            layer_path = Path(token).resolve()
            if not layer_path.is_dir():
                continue
            try:
                root_out = subprocess.run(
                    ["git", "-C", str(layer_path), "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                )
            except OSError:
                continue
            if root_out.returncode != 0:
                continue
            git_root = Path(root_out.stdout.strip())
            if git_root in seen:
                continue
            seen.add(git_root)
            result[git_root.name] = git_root
    return result


def collect_layer_hashes(cfg: BuildConfig) -> list[LayerHash]:
    """Return a :class:`LayerHash` for each repo in ``bblayers.conf``.

    Returns ``[]`` when ``bblayers.conf`` does not exist (pre-first-build).
    The branch is an empty string when the repo is on a detached HEAD.
    Never raises on git failure. The result is sorted by repo name.

    Supports two BBLAYERS path conventions:

    - NXP/TI container builds: ``/work/sources/<repo>/...`` paths where the
      repo's host path is ``cfg.bsp_root/sources/<repo>``.
    - Generic BYO builds: ``${TOPDIR}/../layers/<repo>/...`` paths resolved
      from the build directory via git root discovery.
    """
    if not cfg.bblayers_conf.is_file():
        return []

    # Strategy 1: /sources/ convention (NXP/TI container builds).
    repo_paths: dict[str, Path] = {}
    for repo in parse_bblayers(cfg.bblayers_conf):
        path = cfg.bsp_root / "sources" / repo
        if path.is_dir():
            repo_paths[repo] = path

    # Strategy 2: resolve TOPDIR-relative paths (generic/BYO builds).
    if not repo_paths:
        repo_paths = _resolve_bblayers_paths(cfg.bblayers_conf)

    results: list[LayerHash] = []
    for repo, path in repo_paths.items():
        try:
            rev = subprocess.run(
                ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
            )
        except OSError:
            continue
        if rev.returncode != 0:
            continue
        short_hash = rev.stdout.strip()
        try:
            branch_out = subprocess.run(
                ["git", "-C", str(path), "branch", "--show-current"],
                capture_output=True,
                text=True,
            )
            branch = branch_out.stdout.strip() if branch_out.returncode == 0 else ""
        except OSError:
            branch = ""
        results.append(LayerHash(repo=repo, short_hash=short_hash, branch=branch))
    return sorted(results, key=lambda lh: lh.repo)

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VendorEntry:
    name: str
    family: str
    manifest_regex: str
    repo_url: str | None = None
    container_image: str | None = None
    default_machine: str | None = None
    default_distro: str | None = None
    default_image: str | None = None
    default_manifest: str | None = None
    default_branch: str | None = None
    branch_by_manifest_prefix: dict[str, str] | None = None
    tuning_overlay: str | None = None


def load_vendors(path: Path | None = None) -> list[VendorEntry]:
    """Load vendor entries from a TOML config file.

    Returns an empty list if the file does not exist.
    """
    if path is None:
        path = Path.home() / ".config" / "bspctl" / "vendors.toml"

    if not path.exists():
        return []

    with path.open("rb") as f:
        data = tomllib.load(f)

    entries = []
    for item in data.get("vendors", []):
        entries.append(VendorEntry(**item))

    return entries

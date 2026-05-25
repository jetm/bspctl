from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

_STR_FIELDS = {
    "nxp_machine",
    "nxp_distro",
    "nxp_image",
    "nxp_manifest",
    "nxp_repo_url",
    "ti_machine",
    "ti_distro",
    "ti_image",
    "ti_manifest",
    "container_image",
}
_BOOL_FIELDS = {"doctor", "show_hashes"}


@dataclass
class UserConfig:
    # [defaults.nxp]
    nxp_machine: str | None = None
    nxp_distro: str | None = None
    nxp_image: str | None = None
    nxp_manifest: str | None = None
    nxp_repo_url: str | None = None
    # [defaults.ti]
    ti_machine: str | None = None
    ti_distro: str | None = None
    ti_image: str | None = None
    ti_manifest: str | None = None
    # [build]
    container_image: str | None = None
    doctor: bool = True
    # [layers]
    show_hashes: bool = False


# Maps a (section, key) pair onto a UserConfig field name. The nxp_/ti_ prefixes
# keep the dataclass flat (one field per TOML key) so config.resolve()'s pick()
# calls map one-to-one without restructuring.
_NXP_KEYS = {
    "machine": "nxp_machine",
    "distro": "nxp_distro",
    "image": "nxp_image",
    "manifest": "nxp_manifest",
    "repo_url": "nxp_repo_url",
}
_TI_KEYS = {
    "machine": "ti_machine",
    "distro": "ti_distro",
    "image": "ti_image",
    "manifest": "ti_manifest",
}
_BUILD_KEYS = {
    "container_image": "container_image",
    "doctor": "doctor",
}
_LAYERS_KEYS = {
    "show_hashes": "show_hashes",
}


def _check_type(field: str, value: object, path: Path) -> None:
    if field in _STR_FIELDS and not isinstance(value, str):
        raise ValueError(f"{path}: '{field}' must be a string, got {type(value).__name__}")
    # bool is a subclass of int; reject ints that are not bools explicitly.
    if field in _BOOL_FIELDS and not isinstance(value, bool):
        raise ValueError(f"{path}: '{field}' must be a boolean, got {type(value).__name__}")


def load_user_config(path: Path | None = None) -> UserConfig:
    """Load ``~/.config/bspctl/config.toml`` into a :class:`UserConfig`.

    Returns an all-defaults ``UserConfig()`` when the file is absent. Raises
    ``ValueError`` (with the config path in the message) on a TOML parse error
    or a type mismatch (e.g. a string field given a non-string value).
    """
    if path is None:
        path = Path.home() / ".config" / "bspctl" / "config.toml"

    if not path.exists():
        return UserConfig()

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{path}: invalid TOML: {exc}") from exc

    values: dict[str, object] = {}

    defaults = data.get("defaults", {})
    if isinstance(defaults, dict):
        for section, mapping in (("nxp", _NXP_KEYS), ("ti", _TI_KEYS)):
            section_data = defaults.get(section, {})
            if not isinstance(section_data, dict):
                continue
            for key, field in mapping.items():
                if key in section_data:
                    _check_type(field, section_data[key], path)
                    values[field] = section_data[key]

    for section, mapping in (("build", _BUILD_KEYS), ("layers", _LAYERS_KEYS)):
        section_data = data.get(section, {})
        if not isinstance(section_data, dict):
            continue
        for key, field in mapping.items():
            if key in section_data:
                _check_type(field, section_data[key], path)
                values[field] = section_data[key]

    return UserConfig(**values)

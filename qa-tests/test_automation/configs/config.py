#
# SPDX-FileCopyrightText: <text>Copyright 2025-2026 Arm Limited and/or its
# affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: MIT

"""
Central loader for config, with optional BUILD_IMAGE_DIR and FVP_BINARY
substitution. Supports both list- and mapping-style 'platforms' sections
in YAML.
"""
import os
from types import SimpleNamespace
from typing import Any, Dict, Optional
import yaml


def _expand(obj: Any) -> Any:
    """
    Expand ${ENV} in all strings.

    :param obj: Python objects like strings, lists, and dictionaries are
        transformed.
    :returns: The environment variables and user-home markers expanded
        wherever applicable.
    """
    if isinstance(obj, str):
        return os.path.expanduser(os.path.expandvars(obj))
    if isinstance(obj, list):
        return [_expand(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _expand(v) for k, v in obj.items()}
    return obj


def _set_env_vars(build_dir: Optional[str], fvp_binary: Optional[str]) -> None:
    """
    Set process environment variables for FVP configuration.

    :param build_dir: Path to set as ``BUILD_DIR``. If ``None``,
        the variable is not set.
    :param fvp_binary: Path to set as ``FVP_BINARY``. If ``None``,
        the variable is not set.
    :returns: None
    """
    if build_dir:
        os.environ["BUILD_DIR"] = build_dir.rstrip(os.sep)
    if fvp_binary:
        os.environ["FVP_BINARY"] = fvp_binary.rstrip(os.sep)


def _load_yaml_expanded(path: str) -> Dict[str, Any]:
    """
    Load YAML configuration from a file and expand environment variables.

    :param path: Path to a YAML configuration file.
    :returns: Parsed and expanded YAML content as a dictionary.
    :raises FileNotFoundError: If the YAML file cannot be found.
    :raises yaml.YAMLError: If the YAML content cannot be parsed.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return _expand(data)


def _normalize_platforms(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Normalize the ``platforms`` section of the YAML configuration.

    Ensures platforms are returned as a dictionary keyed by platform name,
    regardless of whether the YAML used mapping or list style.

    :param data: Parsed and expanded YAML configuration.
    :returns: Mapping of platform name to platform configuration dictionary.
    """
    platforms = data.get("platforms", {})
    if isinstance(platforms, dict):
        return {
            name: {**(body or {}), "name": name}
            for name, body in platforms.items()
        }
    # list style
    return {
        p["name"]: dict(p)
        for p in platforms
        if isinstance(p, dict) and "name" in p
    }


def _dict_to_obj(obj: Any) -> Any:
    """
    Recursively convert dictionaries to SimpleNamespace and lists to lists
    of converted entries. Scalars are returned unchanged.

    :param obj: object to convert (dict/list/scalar).
    :returns: converted object: SimpleNamespace for dicts, lists for lists.
    """
    if isinstance(obj, dict):
        converted = {k: _dict_to_obj(v) for k, v in obj.items()}
        return SimpleNamespace(**converted)
    if isinstance(obj, list):
        return [_dict_to_obj(x) for x in obj]
    return obj


class Config:
    """
    Central config loader to load YAML, set environment variable and expose
    platforms as a dict keyed by name.
    """

    def __init__(
        self,
        path: str,
        build_dir: Optional[str] = None,
        fvp_binary: Optional[str] = None,
    ) -> None:
        """Create a configuration loader and normalize the YAML structure.

        :param path: Path to a YAML file containing framework configuration.
        :param build_dir: Sets ``BUILD_DIR`` in the process environment.
        :param fvp_binary: Sets ``FVP_BINARY`` in the process environment.
        :returns: ``None``
        :raises FileNotFoundError: If the provided ``path`` does not exist.
        :raises yaml.YAMLError: If the YAML content cannot be parsed.
        """
        _set_env_vars(build_dir, fvp_binary)
        data = _load_yaml_expanded(path)
        self.platforms: Dict[str, Dict[str, Any]] = _normalize_platforms(data)

        self._raw = data
        self.path = path
        self.build_dir = build_dir
        self.fvp_binary = fvp_binary

    def get_platform(self, name: str) -> Dict[str, Any]:
        """
        Return the configuration dictionary for a specific platform.

        :param name: Platform name key as defined in the YAML ``platforms``.
        :returns: The platform configuration mapping for ``name``.
        :raises KeyError: If ``name`` is not present in :attr:`platforms`.
        """
        if name not in self.platforms:
            raise KeyError(f"Platform '{name}' not found")
        return self.platforms[name]

    def to_dict(self) -> Dict[str, Any]:
        """
        Return the full expanded YAML content as a dictionary.

        :returns: A shallow copy of the expanded YAML content.
        """
        return dict(self._raw)

    def get_platform_object(self, name: str) -> Any:
        """
        Return an object (attributes) of the platform config.

        :param name: Platform key under 'platforms' in the YAML.
        :returns: SimpleNamespace (recursive) representing the platform.
        :raises KeyError: If platform not present.
        """
        platform_dict = self.get_platform(name)
        return _dict_to_obj(platform_dict)

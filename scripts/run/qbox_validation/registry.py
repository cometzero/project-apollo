from __future__ import annotations

import json
from pathlib import Path
from typing import TypeAlias

from .builtins import PROFILE_REGISTRATIONS
from .types import CoverageKind, ProfileProbeSpec, SpecError


JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
ProfileRegistryError = SpecError
def canonical_matrix_path() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
    )


def _matrix_profiles(path: Path) -> dict[str, tuple[CoverageKind, tuple[str, ...]]]:
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ProfileRegistryError(f"validation_matrix_missing:{path}") from error
    except json.JSONDecodeError as error:
        raise ProfileRegistryError(f"validation_matrix_invalid:{path}") from error
    if not isinstance(loaded, dict):
        raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
    raw_profiles = loaded.get("profiles")
    if not isinstance(raw_profiles, list):
        raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
    profiles: dict[str, tuple[CoverageKind, tuple[str, ...]]] = {}
    for raw in raw_profiles:
        if not isinstance(raw, dict):
            raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
        profile_id = raw.get("id")
        coverage = raw.get("coverage_kind")
        assertions = raw.get("qbox_assertions")
        if not isinstance(profile_id, str) or not isinstance(assertions, list):
            raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
        coverage_values: dict[str, CoverageKind] = {
            "identical": "identical",
            "semantic": "semantic",
        }
        parsed_coverage = (
            coverage_values.get(coverage)
            if isinstance(coverage, str)
            else None
        )
        if parsed_coverage is None:
            raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
        if not all(isinstance(item, str) for item in assertions):
            raise ProfileRegistryError(f"validation_matrix_invalid:{path}")
        parsed_assertions = tuple(item for item in assertions if isinstance(item, str))
        profiles[profile_id] = (parsed_coverage, parsed_assertions)
    return profiles


def enabled_profile_ids(matrix_path: Path) -> tuple[str, ...]:
    profiles = _matrix_profiles(matrix_path)
    return tuple(
        registration.profile_id
        for registration in PROFILE_REGISTRATIONS
        if registration.profile_id in profiles
    )


def resolve_profile(profile_id: str, matrix_path: Path) -> ProfileProbeSpec:
    profiles = _matrix_profiles(matrix_path)
    contract = profiles.get(profile_id)
    if contract is None:
        raise ProfileRegistryError(f"unknown_validation_profile:{profile_id}")
    registration = next(
        (
            item
            for item in PROFILE_REGISTRATIONS
            if item.profile_id == profile_id
        ),
        None,
    )
    if registration is None:
        raise ProfileRegistryError(f"validation_profile_unavailable:{profile_id}")
    coverage, assertions = contract
    spec = registration.factory(profile_id, assertions, coverage)
    spec.validate()
    return spec


def resolve_profile_selection(
    requested_profile: str | None,
    active_legacy_flags: tuple[str, ...],
    matrix_path: Path,
) -> ProfileProbeSpec | None:
    if len(active_legacy_flags) > 1:
        raise ProfileRegistryError("conflicting_validation_profile_adapters")
    selected = (
        resolve_profile(requested_profile, matrix_path)
        if requested_profile is not None
        else None
    )
    if not active_legacy_flags:
        return selected
    legacy_flag = active_legacy_flags[0]
    enabled = tuple(
        resolve_profile(profile_id, matrix_path)
        for profile_id in enabled_profile_ids(matrix_path)
    )
    legacy_spec = next(
        (item for item in enabled if item.legacy_flag == legacy_flag),
        None,
    )
    if legacy_spec is None:
        raise ProfileRegistryError(f"unknown_validation_profile_adapter:{legacy_flag}")
    if selected is not None and selected.profile_id != legacy_spec.profile_id:
        raise ProfileRegistryError("conflicting_validation_profile_adapters")
    return legacy_spec

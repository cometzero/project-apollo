from __future__ import annotations

import json
from pathlib import Path
from typing import Final, Iterable, TypeAlias

from .validation_types import (
    CoverageKind,
    ExcludedAction,
    ImageProfile,
    ValidationAction,
    ValidationArea,
    ValidationMatrix,
    ValidationProfile,
)


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

EXPECTED_AREA_COUNT: Final = 15
EXPECTED_PROFILE_COUNT: Final = 14
EXPECTED_ACTION_COUNT: Final = 100
XEN_SELECTOR: Final = "test_40_virtualization"


class MatrixError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        return self.reason


def _mapping(value: JsonValue, field: str) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise MatrixError(f"matrix field {field} must be an object")
    return value


def _list(value: JsonValue, field: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise MatrixError(f"matrix field {field} must be an array")
    return value


def _string(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise MatrixError(f"matrix field {field} must be a non-empty string")
    return value


def _positive_int(value: JsonValue, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise MatrixError(f"matrix field {field} must be a positive integer")
    return value


def _strings(
    value: JsonValue,
    field: str,
    empty_reason: str = "",
) -> tuple[str, ...]:
    items = tuple(_string(item, field) for item in _list(value, field))
    if not items:
        if empty_reason:
            raise MatrixError(empty_reason)
        raise MatrixError(f"matrix field {field} must be non-empty")
    _ensure_unique(items, field)
    return items


def _ensure_unique(items: Iterable[str], field: str) -> None:
    seen: set[str] = set()
    for item in items:
        if item in seen:
            raise MatrixError(f"duplicate {field}: {item}")
        seen.add(item)


def _coverage_kind(value: JsonValue, field: str) -> CoverageKind:
    kind = _string(value, field)
    kinds: dict[str, CoverageKind] = {
        "identical": "identical",
        "semantic": "semantic",
    }
    parsed = kinds.get(kind)
    if parsed is None:
        raise MatrixError(f"invalid coverage kind: {kind}")
    return parsed


def _image(value: JsonValue, field: str) -> ImageProfile:
    image = _string(value, field)
    images: dict[str, ImageProfile] = {"bsp": "bsp", "product": "product"}
    parsed = images.get(image)
    if parsed is None:
        raise MatrixError(f"invalid image profile: {image}")
    return parsed


def _parse_profiles(raw_profiles: JsonValue) -> tuple[ValidationProfile, ...]:
    profiles: list[ValidationProfile] = []
    for index, raw_profile in enumerate(_list(raw_profiles, "profiles")):
        field = f"profiles[{index}]"
        profile = _mapping(raw_profile, field)
        profiles.append(
            ValidationProfile(
                profile_id=_string(profile.get("id"), f"{field}.id"),
                image=_image(profile.get("image"), f"{field}.image"),
                cpu_count=_positive_int(profile.get("cpu_count"), f"{field}.cpu_count"),
                coverage_kind=_coverage_kind(
                    profile.get("coverage_kind"), f"{field}.coverage_kind"
                ),
                fvp_selectors=_strings(
                    profile.get("fvp_selectors"), f"{field}.fvp_selectors"
                ),
                qbox_assertions=_strings(
                    profile.get("qbox_assertions"),
                    f"{field}.qbox_assertions",
                    "empty expected assertion set",
                ),
            )
        )
    _ensure_unique((profile.profile_id for profile in profiles), "profile id")
    return tuple(profiles)


def _parse_areas(raw_areas: JsonValue) -> tuple[ValidationArea, ...]:
    areas: list[ValidationArea] = []
    for area_index, raw_area in enumerate(_list(raw_areas, "areas")):
        field = f"areas[{area_index}]"
        area = _mapping(raw_area, field)
        actions: list[ValidationAction] = []
        for action_index, raw_action in enumerate(_list(area.get("actions"), f"{field}.actions")):
            action_field = f"{field}.actions[{action_index}]"
            action = _mapping(raw_action, action_field)
            actions.append(
                ValidationAction(
                    action_id=_string(action.get("id"), f"{action_field}.id"),
                    assertion_id=_string(
                        action.get("assertion_id"), f"{action_field}.assertion_id"
                    ),
                )
            )
        if not actions:
            raise MatrixError(f"matrix field {field}.actions must be non-empty")
        areas.append(
            ValidationArea(
                area_id=_string(area.get("id"), f"{field}.id"),
                heading=_string(area.get("heading"), f"{field}.heading"),
                profile_id=_string(area.get("profile_id"), f"{field}.profile_id"),
                actions=tuple(actions),
            )
        )
    _ensure_unique((area.area_id for area in areas), "area id")
    return tuple(areas)


def _parse_excluded_actions(raw_actions: JsonValue) -> tuple[ExcludedAction, ...]:
    actions: list[ExcludedAction] = []
    for index, raw_action in enumerate(_list(raw_actions, "excluded_actions")):
        field = f"excluded_actions[{index}]"
        action = _mapping(raw_action, field)
        actions.append(
            ExcludedAction(
                action_id=_string(action.get("id"), f"{field}.id"),
                profile_id=_string(
                    action.get("profile_id"), f"{field}.profile_id"
                ),
                reason=_string(action.get("reason"), f"{field}.reason"),
            )
        )
    if not actions:
        raise MatrixError("matrix field excluded_actions must be non-empty")
    _ensure_unique((action.action_id for action in actions), "excluded action id")
    return tuple(actions)


def _excluded_xen_selector_count(raw_exclusions: JsonValue) -> int:
    count = 0
    for index, raw_exclusion in enumerate(_list(raw_exclusions, "exclusions")):
        field = f"exclusions[{index}]"
        exclusion = _mapping(raw_exclusion, field)
        exclusion_id = _string(exclusion.get("id"), f"{field}.id")
        _string(exclusion.get("reason"), f"{field}.reason")
        selectors = _strings(exclusion.get("selectors"), f"{field}.selectors")
        if exclusion_id == "xen":
            count += sum(selector == XEN_SELECTOR for selector in selectors)
    return count


def _validate_contract(matrix: ValidationMatrix) -> None:
    if matrix.area_count != EXPECTED_AREA_COUNT:
        raise MatrixError(f"expected {EXPECTED_AREA_COUNT} areas, found {matrix.area_count}")
    if matrix.profile_count != EXPECTED_PROFILE_COUNT:
        raise MatrixError(
            f"expected {EXPECTED_PROFILE_COUNT} profiles, found {matrix.profile_count}"
        )
    if matrix.action_count != EXPECTED_ACTION_COUNT:
        raise MatrixError(
            f"expected {EXPECTED_ACTION_COUNT} actions, found {matrix.action_count}"
        )
    if matrix.excluded_xen_selector_count != 1:
        raise MatrixError("Xen must be explicitly excluded exactly once")
    if matrix.xen_selector_count:
        raise MatrixError("Xen selector must not be in scope")
    if matrix.semantic_qbox_area_count != 2:
        raise MatrixError("expected exactly two semantic QBox areas")
    profile_by_id = {profile.profile_id: profile for profile in matrix.profiles}
    action_ids: list[str] = []
    assertion_ids: list[str] = []
    profile_assertions: dict[str, list[str]] = {
        profile.profile_id: [] for profile in matrix.profiles
    }
    for area in matrix.areas:
        profile = profile_by_id.get(area.profile_id)
        if profile is None:
            raise MatrixError(f"unknown profile: {area.profile_id}")
        for action in area.actions:
            action_ids.append(action.action_id)
            assertion_ids.append(action.assertion_id)
            profile_assertions[area.profile_id].append(action.assertion_id)
    for action in matrix.excluded_actions:
        profile = profile_by_id.get(action.profile_id)
        if profile is None:
            raise MatrixError(f"unknown profile: {action.profile_id}")
        if action.action_id in profile.qbox_assertions:
            raise MatrixError(
                f"excluded action is a runtime assertion: {action.action_id}"
            )
    _ensure_unique(action_ids, "action id")
    _ensure_unique(
        [*action_ids, *(action.action_id for action in matrix.excluded_actions)],
        "documented action id",
    )
    _ensure_unique(assertion_ids, "assertion id")
    for profile_id, assertions in profile_assertions.items():
        profile = profile_by_id[profile_id]
        if not assertions:
            raise MatrixError(f"profile has no mapped actions: {profile_id}")
        if set(assertions) != set(profile.qbox_assertions):
            raise MatrixError(f"profile assertion set mismatch: {profile_id}")


def parse_validation_matrix(value: JsonValue, path: Path) -> ValidationMatrix:
    root = _mapping(value, "root")
    if root.get("version") != 1:
        raise MatrixError(f"unsupported matrix version in {path}")
    matrix = ValidationMatrix(
        profiles=_parse_profiles(root.get("profiles")),
        areas=_parse_areas(root.get("areas")),
        excluded_actions=_parse_excluded_actions(root.get("excluded_actions")),
        excluded_xen_selector_count=_excluded_xen_selector_count(root.get("exclusions")),
    )
    _validate_contract(matrix)
    return matrix


def load_validation_matrix(path: Path) -> ValidationMatrix:
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise MatrixError(f"unknown validation matrix: {path}") from error
    except json.JSONDecodeError as error:
        raise MatrixError(f"invalid validation matrix {path}: {error}") from error
    return parse_validation_matrix(loaded, path)

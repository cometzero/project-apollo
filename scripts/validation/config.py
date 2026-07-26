from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Final


SELECTOR_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){0,2}$")


@dataclass(frozen=True, slots=True)
class Profile:
    controller: str
    image: str
    distro: str
    default_suite: str


@dataclass(frozen=True, slots=True)
class Suite:
    selectors: tuple[str, ...]
    cases: dict[str, tuple[str, ...]]


class SelectionError(Exception):
    pass


def _read_mapping(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SelectionError(f"configuration must be an object: {path}")
    return raw


def _strings(value: object, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SelectionError(f"{context} must be a list of strings")
    return tuple(value)


def load_profiles(path: Path) -> dict[str, Profile]:
    profiles: dict[str, Profile] = {}
    for name, value in _read_mapping(path).items():
        if not isinstance(value, dict):
            raise SelectionError(f"profile {name} must be an object")
        fields = tuple(value.get(key) for key in ("controller", "image", "distro", "default_suite"))
        if not all(isinstance(field, str) and field for field in fields):
            raise SelectionError(f"profile {name} has invalid fields")
        controller, image, distro, default_suite = fields
        profiles[name] = Profile(controller, image, distro, default_suite)
    return profiles


def load_suites(path: Path) -> dict[str, Suite]:
    suites: dict[str, Suite] = {}
    for name, value in _read_mapping(path).items():
        if not isinstance(value, dict):
            raise SelectionError(f"suite {name} must be an object")
        raw_cases = value.get("cases", {})
        if not isinstance(raw_cases, dict):
            raise SelectionError(f"suite {name} cases must be an object")
        cases = {case: _strings(selectors, f"suite {name} case {case}") for case, selectors in raw_cases.items() if isinstance(case, str)}
        if len(cases) != len(raw_cases):
            raise SelectionError(f"suite {name} case names must be strings")
        suites[name] = Suite(_strings(value.get("selectors"), f"suite {name} selectors"), cases)
    return suites


def resolve_selectors(suite: Suite, case: str | None, raw: tuple[str, ...]) -> tuple[str, ...]:
    if raw:
        invalid = next((selector for selector in raw if SELECTOR_RE.fullmatch(selector) is None), None)
        if invalid is not None:
            raise SelectionError(f"invalid OEQA selector: {invalid}")
        return raw
    if case is None:
        return suite.selectors
    selected = suite.cases.get(case)
    if selected is None:
        raise SelectionError(f"unknown test case '{case}'")
    return selected

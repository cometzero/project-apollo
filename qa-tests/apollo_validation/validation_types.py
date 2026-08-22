from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, TypeAlias


CoverageKind: TypeAlias = Literal["identical", "semantic"]
ImageProfile: TypeAlias = Literal["bsp", "product"]


@dataclass(frozen=True, slots=True)
class ValidationProfile:
    profile_id: str
    image: ImageProfile
    cpu_count: int
    coverage_kind: CoverageKind
    fvp_selectors: tuple[str, ...]
    qbox_assertions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationAction:
    action_id: str
    assertion_id: str


@dataclass(frozen=True, slots=True)
class ExcludedAction:
    action_id: str
    profile_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class ValidationArea:
    area_id: str
    heading: str
    profile_id: str
    actions: tuple[ValidationAction, ...]


@dataclass(frozen=True, slots=True)
class ActionMapping:
    area_id: str
    profile_id: str
    action_id: str
    assertion_id: str
    qbox_assertions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationMatrix:
    profiles: tuple[ValidationProfile, ...]
    areas: tuple[ValidationArea, ...]
    excluded_actions: tuple[ExcludedAction, ...]
    excluded_xen_selector_count: int

    @property
    def area_count(self) -> int:
        return len(self.areas)

    @property
    def profile_count(self) -> int:
        return len(self.profiles)

    @property
    def action_count(self) -> int:
        return self.required_action_count + self.excluded_action_count

    @property
    def required_action_count(self) -> int:
        return sum(len(area.actions) for area in self.areas)

    @property
    def excluded_action_count(self) -> int:
        return len(self.excluded_actions)

    @property
    def semantic_qbox_area_count(self) -> int:
        semantic_profiles = {
            profile.profile_id
            for profile in self.profiles
            if profile.coverage_kind == "semantic"
        }
        return sum(area.profile_id in semantic_profiles for area in self.areas)

    @property
    def xen_selector_count(self) -> int:
        return sum(
            selector == "test_40_virtualization"
            for profile in self.profiles
            for selector in profile.fvp_selectors
        )

    def action_mappings(self) -> Iterable[ActionMapping]:
        profile_by_id = {profile.profile_id: profile for profile in self.profiles}
        for area in self.areas:
            profile = profile_by_id[area.profile_id]
            for action in area.actions:
                yield ActionMapping(
                    area_id=area.area_id,
                    profile_id=area.profile_id,
                    action_id=action.action_id,
                    assertion_id=action.assertion_id,
                    qbox_assertions=profile.qbox_assertions,
                )

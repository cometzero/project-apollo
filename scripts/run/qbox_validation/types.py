from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Literal, NewType, Protocol, TypedDict, assert_never


ProfileId = NewType("ProfileId", str)
AssertionStatus = Literal["PASS", "FAIL", "BLOCKED"]
CoverageKind = Literal["identical", "semantic"]
Verdict = Literal["PASS", "FAIL", "BLOCKED"]


class Console(StrEnum):
    PRIMARY = "primary"
    SI0 = "si0"
    SI1 = "si1"


class SpecError(Exception):
    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        return self.reason


class EvaluationError(Exception):
    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class ProbeStep:
    console: Console
    command: str
    prompt_pattern: str
    timeout_s: float


@dataclass(frozen=True, slots=True)
class AssertionObservation:
    assertion_id: str
    status: AssertionStatus


@dataclass(frozen=True, slots=True)
class CleanupReceipt:
    passed: bool
    detail: str


class ProfileEvaluator(Protocol):
    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]: ...


class ProfileCleanup(Protocol):
    def cleanup(self) -> CleanupReceipt: ...


@dataclass(frozen=True, slots=True)
class ProfileProbeSpec:
    profile_id: str
    required_consoles: frozenset[Console]
    steps: tuple[ProbeStep, ...]
    expected_assertion_ids: tuple[str, ...]
    coverage_kind: CoverageKind
    evaluator: ProfileEvaluator
    cleanup: ProfileCleanup
    legacy_flag: str | None
    launcher_flags: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.required_consoles:
            raise SpecError(f"profile_required_consoles_empty:{self.profile_id}")
        if not self.steps:
            raise SpecError(f"profile_steps_empty:{self.profile_id}")
        if not self.expected_assertion_ids:
            raise SpecError(f"profile_assertions_empty:{self.profile_id}")
        if len(set(self.expected_assertion_ids)) != len(
            self.expected_assertion_ids
        ):
            raise SpecError(f"profile_assertions_duplicate:{self.profile_id}")
        if len(set(self.launcher_flags)) != len(self.launcher_flags):
            raise SpecError(f"profile_launcher_flags_duplicate:{self.profile_id}")
        if any(
            not item.startswith("--") or "\x00" in item
            for item in self.launcher_flags
        ):
            raise SpecError(f"profile_launcher_flag_invalid:{self.profile_id}")
        for index, step in enumerate(self.steps):
            if step.console not in self.required_consoles:
                raise SpecError(
                    "profile_step_console_unbound:"
                    f"{self.profile_id}:{step.console.value}"
                )
            if not step.command:
                raise SpecError(
                    f"profile_step_command_empty:{self.profile_id}:{index}"
                )
            if "\x00" in step.command:
                raise SpecError(
                    f"profile_step_command_nul:{self.profile_id}:{index}"
                )
            if not step.prompt_pattern:
                raise SpecError(
                    f"profile_step_prompt_empty:{self.profile_id}:{index}"
                )
            try:
                re.compile(step.prompt_pattern)
            except re.error as error:
                raise SpecError(
                    f"profile_step_prompt_invalid:{self.profile_id}:{index}"
                ) from error
            if step.timeout_s <= 0:
                raise SpecError(
                    f"profile_step_timeout_invalid:{self.profile_id}:{index}"
                )


class ProfileSpecFactory(Protocol):
    def __call__(
        self,
        profile_id: str,
        expected: tuple[str, ...],
        coverage_kind: CoverageKind,
    ) -> ProfileProbeSpec: ...


@dataclass(frozen=True, slots=True)
class ProfileRegistration:
    profile_id: str
    factory: ProfileSpecFactory


@dataclass(frozen=True, slots=True)
class ConsoleSnapshot:
    primary: str = ""
    si0: str = ""
    si1: str = ""
    secure: str = ""
    rse: str = ""
    eof: frozenset[Console] = frozenset()

    @classmethod
    def from_pairs(
        cls,
        pairs: tuple[tuple[Console, str], ...],
    ) -> ConsoleSnapshot:
        primary = ""
        si0 = ""
        si1 = ""
        for console, value in pairs:
            match console:
                case Console.PRIMARY:
                    primary = value
                case Console.SI0:
                    si0 = value
                case Console.SI1:
                    si1 = value
                case unexpected:
                    assert_never(unexpected)
        return cls(primary, si0, si1)

    def content(self, console: Console) -> str:
        match console:
            case Console.PRIMARY:
                return self.primary
            case Console.SI0:
                return self.si0
            case Console.SI1:
                return self.si1
            case unexpected:
                assert_never(unexpected)


@dataclass(frozen=True, slots=True)
class Dispatch:
    console: Console
    payload: str
    step_index: int


class AssertionJson(TypedDict):
    id: str
    status: AssertionStatus
    coverage_kind: CoverageKind


class NormalizedResultJson(TypedDict):
    version: int
    profile_id: str
    backend: Literal["qbox"]
    verdict: Verdict
    expected: list[str]
    assertions: list[AssertionJson]


class CompatibilityCheckJson(TypedDict):
    status: AssertionStatus


class SafetyDiagnosticsCompatibilityJson(TypedDict):
    requested: bool
    passed: bool
    diagnostics: dict[str, CompatibilityCheckJson]
    failed_checks: list[str]
    source: Literal["validation_profile"]

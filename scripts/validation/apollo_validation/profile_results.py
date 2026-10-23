from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias, TypedDict, assert_never

from .validation_types import CoverageKind, ValidationProfile


Backend: TypeAlias = Literal["fvp", "qbox"]
AssertionStatus: TypeAlias = Literal["PASS", "FAIL", "BLOCKED", "SKIPPED"]
Verdict: TypeAlias = Literal["PASS", "FAIL", "BLOCKED"]
class AssertionJson(TypedDict):
    id: str
    status: AssertionStatus
    coverage_kind: CoverageKind


class ProfileResultJson(TypedDict):
    version: int
    profile_id: str
    backend: Backend
    verdict: Verdict
    expected: list[str]
    assertions: list[AssertionJson]


class ProfileCountsJson(TypedDict):
    passed: int
    failed: int
    blocked: int
    skipped: int
    total: int


@dataclass(frozen=True, slots=True)
class ObservedAssertion:
    assertion_id: str
    status: AssertionStatus
    coverage_kind: CoverageKind


@dataclass(frozen=True, slots=True)
class ProfileResult:
    profile_id: str
    backend: Backend
    verdict: Verdict
    expected: tuple[str, ...]
    assertions: tuple[ObservedAssertion, ...]


@dataclass(frozen=True, slots=True)
class ProfileCounts:
    passed: int
    failed: int
    blocked: int
    skipped: int
    total: int


@dataclass(frozen=True, slots=True)
class NormalizedProfile:
    result: ProfileResult
    counts: ProfileCounts
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProfileResultError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def parse_backend(value: str) -> Backend:
    backends: dict[str, Backend] = {"fvp": "fvp", "qbox": "qbox"}
    backend = backends.get(value)
    if backend is None:
        raise ProfileResultError(f"unsupported profile backend: {value}")
    return backend


def verdict_exit_code(verdict: Verdict) -> int:
    match verdict:
        case "PASS":
            return 0
        case "FAIL":
            return 1
        case "BLOCKED":
            return 2
        case unexpected:
            assert_never(unexpected)


def evaluate_profile(
    profile: ValidationProfile,
    backend: Backend,
    observed: tuple[ObservedAssertion, ...],
) -> NormalizedProfile:
    expected = profile.qbox_assertions
    id_counts = Counter(item.assertion_id for item in observed)
    missing = tuple(item for item in expected if id_counts[item] == 0)
    duplicates = tuple(item for item, count in id_counts.items() if count > 1)
    unexpected = tuple(item for item in id_counts if item not in expected)
    failed = tuple(item for item in observed if item.status == "FAIL")
    blocked = tuple(item for item in observed if item.status == "BLOCKED")
    skipped = tuple(item for item in observed if item.status == "SKIPPED")
    coverage_mismatch = tuple(
        item for item in observed if item.coverage_kind != profile.coverage_kind
    )
    reasons: list[str] = []
    if not observed:
        reasons.append("blocked_profile_zero_assertions")
    if observed and len(skipped) == len(observed):
        reasons.append("blocked_profile_all_skipped")
    if failed:
        reasons.append("failed_profile_assertions")
    if blocked:
        reasons.append("blocked_profile_assertions")
    if skipped:
        reasons.append("blocked_profile_assertions_skipped")
    if missing:
        reasons.append("missing_profile_assertions")
    if duplicates:
        reasons.append("duplicate_profile_assertion_ids")
    if unexpected:
        reasons.append("unexpected_profile_assertion_ids")
    if coverage_mismatch:
        reasons.append("mismatched_profile_coverage_kind")
    normalized = observed + tuple(
        ObservedAssertion(item, "BLOCKED", profile.coverage_kind) for item in missing
    )
    fatal = bool(failed or duplicates or unexpected or coverage_mismatch)
    verdict: Verdict = "FAIL" if fatal else "BLOCKED" if reasons else "PASS"
    counts = ProfileCounts(
        passed=sum(item.status == "PASS" for item in normalized),
        failed=sum(item.status == "FAIL" for item in normalized),
        blocked=sum(item.status == "BLOCKED" for item in normalized),
        skipped=sum(item.status == "SKIPPED" for item in normalized),
        total=len(normalized),
    )
    return NormalizedProfile(
        result=ProfileResult(profile.profile_id, backend, verdict, expected, normalized),
        counts=counts,
        reasons=tuple(reasons),
    )


def normalize_profile_run(
    run_dir: Path,
    profile_id: str,
    backend: Backend,
) -> NormalizedProfile:
    from .profile_result_io import normalize_profile_run as normalize

    return normalize(run_dir, profile_id, backend)


def profile_result_json(result: ProfileResult) -> ProfileResultJson:
    return {
        "version": 1,
        "profile_id": result.profile_id,
        "backend": result.backend,
        "verdict": result.verdict,
        "expected": list(result.expected),
        "assertions": [
            {
                "id": item.assertion_id,
                "status": item.status,
                "coverage_kind": item.coverage_kind,
            }
            for item in result.assertions
        ],
    }


def profile_counts_json(counts: ProfileCounts) -> ProfileCountsJson:
    return {
        "passed": counts.passed,
        "failed": counts.failed,
        "blocked": counts.blocked,
        "skipped": counts.skipped,
        "total": counts.total,
    }

from __future__ import annotations

from collections import Counter

from .types import (
    AssertionJson,
    AssertionObservation,
    AssertionStatus,
    CompatibilityCheckJson,
    ConsoleSnapshot,
    EvaluationError,
    NormalizedResultJson,
    ProfileProbeSpec,
    SafetyDiagnosticsCompatibilityJson,
    Verdict,
)


def normalize_profile_result(
    spec: ProfileProbeSpec,
    observed: tuple[AssertionObservation, ...],
) -> NormalizedResultJson:
    counts = Counter(item.assertion_id for item in observed)
    duplicate = any(count > 1 for count in counts.values())
    unexpected = any(
        item.assertion_id not in spec.expected_assertion_ids for item in observed
    )
    missing = tuple(
        item for item in spec.expected_assertion_ids if counts[item] == 0
    )
    assertions: list[AssertionJson] = [
        {
            "id": item.assertion_id,
            "status": item.status,
            "coverage_kind": spec.coverage_kind,
        }
        for item in observed
    ]
    assertions.extend(
        {
            "id": item,
            "status": "BLOCKED",
            "coverage_kind": spec.coverage_kind,
        }
        for item in missing
    )
    failed = any(item.status == "FAIL" for item in observed)
    blocked = any(item.status == "BLOCKED" for item in observed)
    verdict: Verdict = (
        "FAIL"
        if duplicate or unexpected or failed
        else "BLOCKED"
        if missing or blocked
        else "PASS"
    )
    return {
        "version": 1,
        "profile_id": spec.profile_id,
        "backend": "qbox",
        "verdict": verdict,
        "expected": list(spec.expected_assertion_ids),
        "assertions": assertions,
    }


def blocked_profile_result(spec: ProfileProbeSpec) -> NormalizedResultJson:
    return normalize_profile_result(
        spec,
        tuple(
            AssertionObservation(item, "BLOCKED")
            for item in spec.expected_assertion_ids
        ),
    )


def evaluate_profile_result(
    spec: ProfileProbeSpec,
    snapshot: ConsoleSnapshot,
    outputs: tuple[str, ...] = (),
) -> NormalizedResultJson:
    try:
        observed = spec.evaluator.evaluate(snapshot, outputs)
    except EvaluationError:
        return blocked_profile_result(spec)
    return normalize_profile_result(spec, observed)


def safety_diagnostics_compatibility(
    result: NormalizedResultJson | None,
    *,
    requested: bool,
) -> SafetyDiagnosticsCompatibilityJson:
    statuses: dict[str, AssertionStatus] = (
        {item["id"]: item["status"] for item in result["assertions"]}
        if result is not None
        else {}
    )
    names = (
        ("ssu", "safety-island-ssu"),
        ("fmu", "safety-island-fmu"),
    )
    diagnostics: dict[str, CompatibilityCheckJson] = {
        name: CompatibilityCheckJson(
            status=statuses.get(assertion_id, "BLOCKED")
        )
        for name, assertion_id in names
    }
    failed = [
        name
        for name, assertion_id in names
        if statuses.get(assertion_id) != "PASS"
    ]
    return {
        "requested": requested,
        "passed": bool(requested and result is not None and result["verdict"] == "PASS"),
        "diagnostics": diagnostics,
        "failed_checks": failed,
        "source": "validation_profile",
    }

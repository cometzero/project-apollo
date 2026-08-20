from __future__ import annotations

import re
from typing import Final, TypedDict


DIAGNOSTIC_NAMES: Final = ("ssu", "fmu")


class DiagnosticResult(TypedDict):
    started: bool
    ended: bool
    total: int
    passed: int
    failures: int
    ignored: int
    ok: bool
    result: str


class SafetyDiagnosticsResult(TypedDict):
    passed: bool
    diagnostics: dict[str, DiagnosticResult]
    failed_checks: list[str]


def safety_diagnostics_commands() -> list[str]:
    return [f"test {name}" for name in DIAGNOSTIC_NAMES]


def _diagnostic_result(console: str, name: str) -> DiagnosticResult:
    start = re.search(
        rf"\[INTEGRATION_TEST\]\s+Start:\s*{re.escape(name)}\b",
        console,
    )
    end = (
        re.search(
            rf"\[INTEGRATION_TEST\]\s+End:\s*{re.escape(name)}\b",
            console[start.end() :],
        )
        if start is not None
        else None
    )
    body = (
        console[start.end() : start.end() + end.start()]
        if start is not None and end is not None
        else ""
    )
    summary = re.search(
        r"(?P<total>\d+)\s+Tests\s+"
        r"(?P<failures>\d+)\s+Failures\s+"
        r"(?P<ignored>\d+)\s+Ignored",
        body,
    )
    total = int(summary.group("total")) if summary is not None else 0
    failures = int(summary.group("failures")) if summary is not None else 0
    ignored = int(summary.group("ignored")) if summary is not None else 0
    passed = total - failures - ignored
    ok = re.search(r"\bOK\b", body) is not None
    success = bool(
        start is not None
        and end is not None
        and summary is not None
        and total > 0
        and failures == 0
        and ignored == 0
        and ok
    )
    return {
        "started": start is not None,
        "ended": end is not None,
        "total": total,
        "passed": passed,
        "failures": failures,
        "ignored": ignored,
        "ok": ok,
        "result": "PASS" if success else "FAIL",
    }


def evaluate_safety_diagnostics(
    console: str,
) -> SafetyDiagnosticsResult:
    diagnostics: dict[str, DiagnosticResult] = {
        name: _diagnostic_result(console, name)
        for name in DIAGNOSTIC_NAMES
    }
    failed_checks = [
        name
        for name, result in diagnostics.items()
        if result["result"] != "PASS"
    ]
    return {
        "passed": not failed_checks,
        "diagnostics": diagnostics,
        "failed_checks": failed_checks,
    }

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final

from .types import (
    AssertionObservation,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
)


PRIMARY_PROMPT: Final = r"(?m)(?:nexios-bsp#|root@apollo-qvp[^\n]*[#>])\s*$"
TOTAL_PATTERN: Final = re.compile(
    r"TOTAL[ \t]+(TESTS|PASSED|SIM ERROR|FAILED|SKIPPED)[ \t]*:[ \t]*(\d+)[ \t]*$"
)
TOTAL_NAMES: Final = (
    ("TESTS", "tests"),
    ("PASSED", "passed"),
    ("SIM ERROR", "sim_error"),
    ("FAILED", "failed"),
    ("SKIPPED", "skipped"),
)
SECURE_FAILURE_MARKERS: Final = ("E/TC", "FF-A: error", "FF-A: failed")


@dataclass(frozen=True, slots=True)
class PsaTotals:
    tests: int
    passed: int
    sim_error: int
    failed: int
    skipped: int


@dataclass(frozen=True, slots=True)
class PsaSuite:
    key: str
    binary: str
    assertion_id: str
    expected: PsaTotals


SUITES: Final = (
    PsaSuite(
        "crypto",
        "psa-crypto-api-test",
        "ts-psa-crypto-api-test",
        PsaTotals(60, 57, 0, 0, 3),
    ),
    PsaSuite(
        "ps",
        "psa-ps-api-test",
        "ts-psa-ps-api-test",
        PsaTotals(17, 11, 0, 0, 6),
    ),
    PsaSuite(
        "its",
        "psa-its-api-test",
        "ts-psa-its-api-test",
        PsaTotals(10, 10, 0, 0, 0),
    ),
    PsaSuite(
        "iat",
        "psa-iat-api-test",
        "ts-psa-iat-api-test",
        PsaTotals(1, 1, 0, 0, 0),
    ),
)


def _parse_totals(output: str) -> PsaTotals | None:
    field_names = dict(TOTAL_NAMES)
    values: dict[str, int] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line.upper().startswith("TOTAL"):
            continue
        match = TOTAL_PATTERN.fullmatch(line)
        if match is None:
            return None
        label, raw_value = match.groups()
        name = field_names[label]
        if name in values:
            return None
        values[name] = int(raw_value)
    if set(values) != set(field_names.values()):
        return None
    return PsaTotals(
        values["tests"],
        values["passed"],
        values["sim_error"],
        values["failed"],
        values["skipped"],
    )


def _suite_passes(output: str, suite: PsaSuite) -> bool:
    lines = tuple(line.strip() for line in output.splitlines())
    begin = f"__QBOX_TS_BEGIN__:{suite.key}"
    end = f"__QBOX_TS_END__:{suite.key}"
    rc_pattern = re.compile(rf"__QBOX_TS_RC__:{re.escape(suite.key)}:(\d+)")
    return_codes = tuple(
        int(match.group(1))
        for line in lines
        if (match := rc_pattern.fullmatch(line)) is not None
    )
    totals = _parse_totals(output)
    return bool(
        lines.count(begin) == 1
        and lines.count(end) == 1
        and return_codes == (0,)
        and totals is not None
        and totals.tests > 0
        and totals.failed == 0
        and totals.sim_error == 0
        and totals.passed + totals.skipped == totals.tests
        and totals == suite.expected
    )


def _suite_command(suite: PsaSuite) -> str:
    return (
        f"printf '\n__QBOX_TS_BEGIN__:{suite.key}\n'; "
        f"timeout 1200s {suite.binary} 2>&1; rc=$?; "
        f"printf '\n__QBOX_TS_RC__:{suite.key}:%s\n' \"$rc\"; "
        f"printf '__QBOX_TS_END__:{suite.key}\n'"
    )


@dataclass(frozen=True, slots=True)
class TrustedServicesEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        secure_clean = all(
            marker not in snapshot.secure for marker in SECURE_FAILURE_MARKERS
        )
        by_id = {
            suite.assertion_id: bool(
                secure_clean
                and index < len(outputs)
                and _suite_passes(outputs[index], suite)
            )
            for index, suite in enumerate(SUITES)
        }
        return tuple(
            AssertionObservation(item, "PASS" if by_id[item] else "FAIL")
            for item in self.expected
        )


@dataclass(frozen=True, slots=True)
class TrustedServicesCleanup:
    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(True, "guest_timeout_owns_suite_processes")


def trusted_services_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(
            ProbeStep(Console.PRIMARY, _suite_command(suite), PRIMARY_PROMPT, 1230.0)
            for suite in SUITES
        ),
        expected,
        coverage_kind,
        TrustedServicesEvaluator(expected),
        TrustedServicesCleanup(),
        None,
        ("--cc3xx-qemu-native-backend",),
    )

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final

from scripts.run.qbox_si_cl1_pfdi_catalog import si_cl1_pfdi_checks
from scripts.run.qbox_si_cl1_pfdi_probe import evaluate_si_cl1_pfdi_records

from .reuse_common import (
    NoopCleanup,
    SI1_PROMPT,
    current_scp_segment,
    status,
)
from .types import (
    AssertionObservation,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
)


SMCF_SENSOR_RE: Final = re.compile(
    r"\[SMCF_CLIENT\]\s+Values for MGI\s+[A-Z0-9_]+\s+MLI\s+\d+\s+"
    r"\(Sensor\)\s*$\n.*\[SMCF_CLIENT\]\s+Value\[\d+\]\s+data\s+=\s+"
    r"0x[0-9a-fA-F]+",
    re.MULTILINE,
)
MONITOR_FAILURE_RE: Final = re.compile(
    r"\[PFDI_MONITOR\].*(?:timeout|fail(?:ed|ure)?)",
    re.IGNORECASE,
)
SMCF_PROMPT: Final = (
    r"(?m)(?:\[FWK\] Module initialization complete!|"
    r"\[INTEGRATION_TEST\]\s+End:\s*smcf)\s*$"
)


def _smcf_run_complete(output: str) -> bool:
    patterns = (
        r"\[INTEGRATION_TEST\]\s+Start:\s*smcf",
        r"[1-9]\d*\s+Tests\s+0\s+Failures\s+0\s+Ignored",
        r"(?m)^\s*OK\s*$",
        r"\[INTEGRATION_TEST\]\s+End:\s*smcf",
    )
    return all(len(re.findall(pattern, output)) == 1 for pattern in patterns)


@dataclass(frozen=True, slots=True)
class SmcfEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        segment = current_scp_segment(snapshot.si0)
        complete = tuple(_smcf_run_complete(output) for output in outputs)
        checks = (
            bool(segment)
            and re.search(
                r"\[SMCF_CLIENT\]\s+start data_sampling for MGI\[\d+\]",
                segment,
            )
            is not None,
            len(complete) == 4 and complete[0],
            len(complete) == 4 and all(complete[1:]),
            bool(SMCF_SENSOR_RE.search(segment)),
        )
        return tuple(
            AssertionObservation(assertion_id, status(passed))
            for assertion_id, passed in zip(self.expected, checks, strict=True)
        )


def _monitor_complete(text: str) -> bool:
    segment = current_scp_segment(text)
    if not segment or MONITOR_FAILURE_RE.search(segment) is not None:
        return False
    for core in range(4):
        patterns = (
            rf"\[PFDI_MONITOR\] Started PFDI monitoring for SI cluster 1 core {core}\s*$",
            rf"\[PFDI_MONITOR\] SI cluster 1 core {core} has been turned on, "
            r"switching on PFDI monitoring\s*$",
        )
        if any(
            len(re.findall(pattern, segment, re.MULTILINE)) != 1
            for pattern in patterns
        ):
            return False
    return True


@dataclass(frozen=True, slots=True)
class SiCl1PfdiEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        checks = si_cl1_pfdi_checks()
        result = evaluate_si_cl1_pfdi_records(checks, list(outputs))
        records = result["records"]
        prefix_groups: Final = tuple(
            (f"test_{index:02d}_",) for index in range(1, 17)
        )
        passed_by_group = tuple(
            bool(group_records)
            and all(record["passed"] for record in group_records)
            for prefixes in prefix_groups
            for group_records in (
                tuple(
                    record
                    for record in records
                    if record["name"].startswith(prefixes)
                ),
            )
        )
        passed = (*passed_by_group, _monitor_complete(snapshot.si0))
        return tuple(
            AssertionObservation(assertion_id, status(group_passed))
            for assertion_id, group_passed in zip(
                self.expected,
                passed,
                strict=True,
            )
        )


def smcf_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.SI0}),
        tuple(
            ProbeStep(Console.SI0, "test smcf", SMCF_PROMPT, 120.0)
            for _run in range(4)
        ),
        expected,
        coverage_kind,
        SmcfEvaluator(expected),
        NoopCleanup(),
        None,
    )


def si_cl1_pfdi_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.SI1}),
        tuple(
            ProbeStep(Console.SI1, item.command, SI1_PROMPT, 60.0)
            for item in si_cl1_pfdi_checks()
        ),
        expected,
        coverage_kind,
        SiCl1PfdiEvaluator(expected),
        NoopCleanup(),
        "--pfdi-si-cl1-probe",
    )

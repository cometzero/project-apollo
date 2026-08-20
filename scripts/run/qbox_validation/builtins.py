from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from scripts.run.qbox_pfdi_probe import evaluate_pfdi_probe, pfdi_probe_commands
from scripts.run.qbox_ras_cpu_probe import evaluate_ras_cpu_probe, ras_cpu_probe_commands
from scripts.run.qbox_safety_diagnostics_probe import (
    evaluate_safety_diagnostics,
    safety_diagnostics_commands,
)
from scripts.run.qbox_si_cl1_pfdi_catalog import si_cl1_pfdi_checks
from scripts.run.qbox_si_cl1_pfdi_probe import evaluate_si_cl1_pfdi_records

from .types import (
    AssertionObservation,
    AssertionStatus,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
    ProfileRegistration,
)


PRIMARY_PROMPT: Final = r"(?m)(?:nexios-bsp#|root@apollo-qvp[^\n]*[#>])\s*$"
SI0_PROMPT: Final = (
    r"(?m)(?:\[FWK\] Module initialization complete!|"
    r"\[INTEGRATION_TEST\]\s+End:\s*(?:ssu|fmu))\s*$"
)
SI1_PROMPT: Final = r"(?m)(?:^|\n)(?:(?:uart:)?~\$\s*)+$"


@dataclass(frozen=True, slots=True)
class NoopCleanup:
    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(True, "no_resources")


def _status(passed: bool) -> AssertionStatus:
    return "PASS" if passed else "FAIL"


@dataclass(frozen=True, slots=True)
class PfdiEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        result = evaluate_pfdi_probe(snapshot.primary, snapshot.si0)
        failed = set(result["failed_checks"])
        cpu_results = tuple(result["cpu_results"].values())
        checks = (
            "service" not in failed,
            "prerequisites" not in failed and "online" not in failed,
            "cli" not in failed and all(item["count"] for item in cpu_results),
            all(item["force_error"] for item in cpu_results),
            all(item["monitor_started"] for item in cpu_results),
            all(
                item["online_failure"] and item["monitor_failure"]
                for item in cpu_results
            ),
            all(item["sbistc"] for item in cpu_results)
            and result["fmu_fault_count"] >= len(cpu_results),
        )
        return tuple(
            AssertionObservation(assertion_id, _status(passed))
            for assertion_id, passed in zip(self.expected, checks, strict=True)
        )


@dataclass(frozen=True, slots=True)
class SafetyDiagnosticsEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        result = evaluate_safety_diagnostics(snapshot.si0)
        diagnostics = result["diagnostics"]
        by_id = {
            "safety-island-fmu": diagnostics["fmu"]["result"] == "PASS",
            "safety-island-ssu": diagnostics["ssu"]["result"] == "PASS",
        }
        return tuple(
            AssertionObservation(item, _status(by_id[item]))
            for item in self.expected
        )


@dataclass(frozen=True, slots=True)
class RasCpuEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        result = evaluate_ras_cpu_probe(
            snapshot.primary,
            snapshot.secure,
            snapshot.si0,
        )
        checks = result["checks"]
        by_id = {
            "ras-inject-list": checks["list"],
            "ras-inject-invalid-cpu-error": checks["invalid"],
            "ras-inject-usage": checks["usage"],
            "ras-inject-correctable-cpu-error": checks["correctable"],
            "ras-inject-deferred-cpu-error": checks["deferred"],
            "ras-inject-correctable-cpu-error-10x": checks["repeat"],
            "ras-inject-uncorrectable-cpu-error": checks["uncorrectable"],
            "ras-inject-correctable-deferred-cpu-error": checks["combined"],
            "ras-journalctl-service": checks["journal"],
        }
        return tuple(
            AssertionObservation(item, _status(by_id[item]))
            for item in self.expected
        )


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
        prefix_groups: Final = (
            ("test_01_",),
            ("test_02_",),
            ("test_03_invalid_", "test_03_valid_"),
            ("test_04_",),
            ("test_05_",),
            ("test_06_",),
            ("test_07_",),
            ("test_08_",),
            ("test_09_",),
            ("test_10_",),
            ("test_11_",),
            ("test_12_",),
            ("test_13_",),
            ("test_14_",),
            ("test_15_",),
            ("test_16_",),
        )
        passed_by_group = tuple(
            all(
                record["passed"]
                for record in records
                if record["name"].startswith(prefixes)
            )
            for prefixes in prefix_groups
        )
        passed_by_group = (*passed_by_group, result["passed"])
        return tuple(
            AssertionObservation(item, _status(passed))
            for item, passed in zip(
                self.expected,
                passed_by_group,
                strict=True,
            )
        )


def _pfdi_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(
            ProbeStep(Console.PRIMARY, item, PRIMARY_PROMPT, 240.0)
            for item in pfdi_probe_commands()
        ),
        expected,
        coverage_kind,
        PfdiEvaluator(expected),
        NoopCleanup(),
        "--pfdi-probe",
    )


def _si_cl1_pfdi_spec(
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


def _ras_cpu_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(
            ProbeStep(Console.PRIMARY, item, PRIMARY_PROMPT, 240.0)
            for item in ras_cpu_probe_commands()
        ),
        expected,
        coverage_kind,
        RasCpuEvaluator(expected),
        NoopCleanup(),
        "--ras-cpu-probe",
    )


def _safety_diagnostics_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.SI0}),
        tuple(
            ProbeStep(Console.SI0, item, SI0_PROMPT, 60.0)
            for item in safety_diagnostics_commands()
        ),
        expected,
        coverage_kind,
        SafetyDiagnosticsEvaluator(expected),
        NoopCleanup(),
        "--safety-diagnostics-probe",
    )


PROFILE_REGISTRATIONS: Final = (
    ProfileRegistration("pfdi", _pfdi_spec),
    ProfileRegistration("pfdi-si-cl1", _si_cl1_pfdi_spec),
    ProfileRegistration("ras_cpu", _ras_cpu_spec),
    ProfileRegistration("safety-diagnostics-tests", _safety_diagnostics_spec),
)

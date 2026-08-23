from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from scripts.run.qbox_pfdi_probe import evaluate_pfdi_probe, pfdi_probe_commands
from scripts.run.qbox_ras_cpu_probe import evaluate_ras_cpu_probe, ras_cpu_probe_commands
from scripts.run.qbox_safety_diagnostics_probe import (
    evaluate_safety_diagnostics,
    safety_diagnostics_commands,
)
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
from .reuse_bsp import bsp_core_spec, si_cl1_spec
from .reuse_cpuidle import cpuidle_spec
from .reuse_cpufreq import cpufreq_spec
from .reuse_si import si_cl1_pfdi_spec, smcf_spec
from .reuse_platform_devices import platform_devices_spec
from .reuse_trusted_services import trusted_services_spec


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
    ProfileRegistration("bsp-core", bsp_core_spec),
    ProfileRegistration("cpuidle", cpuidle_spec),
    ProfileRegistration("cpufreq", cpufreq_spec),
    ProfileRegistration("pfdi", _pfdi_spec),
    ProfileRegistration("pfdi-si-cl1", si_cl1_pfdi_spec),
    ProfileRegistration("platform-devices", platform_devices_spec),
    ProfileRegistration("ras_cpu", _ras_cpu_spec),
    ProfileRegistration("safety-diagnostics-tests", _safety_diagnostics_spec),
    ProfileRegistration("si-cl1", si_cl1_spec),
    ProfileRegistration("smcf", smcf_spec),
    ProfileRegistration("trusted-services", trusted_services_spec),
)

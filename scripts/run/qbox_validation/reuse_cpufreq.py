from __future__ import annotations

from dataclasses import dataclass

from scripts.run.qbox_cpufreq_commands import cpufreq_probe_commands
from scripts.run.qbox_cpufreq_probe import evaluate_cpufreq_probe

from .reuse_common import NoopCleanup, PRIMARY_PROMPT, status
from .types import (
    AssertionObservation,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
)


@dataclass(frozen=True, slots=True)
class CpuFreqEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        checks = evaluate_cpufreq_probe(outputs)
        return tuple(
            AssertionObservation(assertion_id, status(passed))
            for assertion_id, passed in zip(self.expected, checks, strict=True)
        )


def cpufreq_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(
            ProbeStep(Console.PRIMARY, command, PRIMARY_PROMPT, 300.0)
            for command in cpufreq_probe_commands()
        ),
        expected,
        coverage_kind,
        CpuFreqEvaluator(expected),
        NoopCleanup(),
        None,
    )

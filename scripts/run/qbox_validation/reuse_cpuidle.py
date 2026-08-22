from __future__ import annotations

from dataclasses import dataclass

from scripts.run.qbox_cpuidle_commands import cpuidle_probe_commands
from scripts.run.qbox_cpuidle_probe import evaluate_cpuidle_probe

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
class CpuIdleEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        checks = evaluate_cpuidle_probe(outputs)
        return tuple(
            AssertionObservation(assertion_id, status(passed))
            for assertion_id, passed in zip(self.expected, checks, strict=True)
        )


def cpuidle_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(
            ProbeStep(Console.PRIMARY, command, PRIMARY_PROMPT, 600.0)
            for command in cpuidle_probe_commands()
        ),
        expected,
        coverage_kind,
        CpuIdleEvaluator(expected),
        NoopCleanup(),
        None,
    )

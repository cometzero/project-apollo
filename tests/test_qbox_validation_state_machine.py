from __future__ import annotations

from dataclasses import dataclass

from scripts.run.qbox_validation.engine import advance_profile, new_profile_state
from scripts.run.qbox_validation.types import (
    AssertionObservation,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    EvaluationError,
    ProbeStep,
    ProfileProbeSpec,
)


PROMPT = r"(?m)^READY> $"


@dataclass(frozen=True, slots=True)
class MarkerEvaluator:
    assertion_ids: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        joined = "\n".join(outputs)
        return tuple(
            AssertionObservation(item, "PASS" if item in joined else "FAIL")
            for item in self.assertion_ids
        )


@dataclass(frozen=True, slots=True)
class RaisingEvaluator:
    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        raise EvaluationError(reason="evaluator_error")


@dataclass(frozen=True, slots=True)
class FixedCleanup:
    passed: bool

    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(self.passed, "cleanup_receipt")


def spec_for(
    consoles: tuple[Console, ...],
    *,
    evaluator: MarkerEvaluator | RaisingEvaluator | None = None,
    cleanup: FixedCleanup | None = None,
) -> ProfileProbeSpec:
    ids = tuple(f"assert-{index}" for index in range(len(consoles)))
    return ProfileProbeSpec(
        profile_id="fake-profile",
        required_consoles=frozenset(consoles),
        steps=tuple(
            ProbeStep(console, f"command-{index}", PROMPT, 5.0)
            for index, console in enumerate(consoles)
        ),
        expected_assertion_ids=ids,
        coverage_kind="identical",
        evaluator=evaluator or MarkerEvaluator(ids),
        cleanup=cleanup or FixedCleanup(True),
        legacy_flag=None,
    )


def drive_success(spec: ProfileProbeSpec) -> tuple[list[Console], str]:
    state = new_profile_state(spec, spec.required_consoles, now=0.0)
    dispatched: list[Console] = []
    logs = {console: "READY> " for console in spec.required_consoles}
    now = 0.0
    while state.phase == "running":
        snapshot = ConsoleSnapshot.from_pairs(tuple(logs.items()))
        result = advance_profile(spec, state, snapshot, now=now)
        state = result.state
        if result.dispatch is None:
            break
        dispatched.append(result.dispatch.console)
        index = len(dispatched) - 1
        logs[result.dispatch.console] += (
            f"command-{index}\nassert-{index}\nREADY> "
        )
        now += 1.0
    assert state.result is not None
    return dispatched, state.result["verdict"]


def test_each_supported_console_shape_completes_in_order() -> None:
    # Given: specs for every required QBox console shape.
    shapes = (
        (Console.PRIMARY,),
        (Console.SI0,),
        (Console.SI1,),
        (Console.PRIMARY, Console.SI1),
    )

    # When: each state machine receives prompt-owned command responses.
    observed = [drive_success(spec_for(shape)) for shape in shapes]

    # Then: routing order and normalized verdicts are deterministic.
    assert observed == [(list(shape), "PASS") for shape in shapes]


def test_repeated_or_stale_prompt_does_not_advance() -> None:
    # Given: a primary-only probe after its first command was dispatched.
    spec = spec_for((Console.PRIMARY,))
    state = new_profile_state(spec, spec.required_consoles, now=0.0)
    first = advance_profile(
        spec,
        state,
        ConsoleSnapshot(primary="READY> "),
        now=0.0,
    )

    # When: the identical prompt snapshot is observed again.
    repeated = advance_profile(
        spec,
        first.state,
        ConsoleSnapshot(primary="READY> "),
        now=1.0,
    )

    # Then: it cannot be mistaken for command completion.
    assert repeated.dispatch is None
    assert repeated.state == first.state


def test_partial_output_waits_and_command_timeout_blocks() -> None:
    # Given: a dispatched command with output lacking a fresh prompt.
    spec = spec_for((Console.PRIMARY,))
    initial = new_profile_state(spec, spec.required_consoles, now=0.0)
    sent = advance_profile(
        spec,
        initial,
        ConsoleSnapshot(primary="READY> "),
        now=0.0,
    ).state

    # When: partial output persists past the command deadline.
    waiting = advance_profile(
        spec,
        sent,
        ConsoleSnapshot(primary="READY> partial"),
        now=4.0,
    ).state
    expired = advance_profile(
        spec,
        waiting,
        ConsoleSnapshot(primary="READY> partial"),
        now=5.1,
    ).state

    # Then: partial output does not advance and the timeout is bounded.
    assert waiting.phase == "running"
    assert expired.phase == "blocked"
    assert expired.blocker == "command_timeout:0:primary"


def test_fifo_eof_blocks_before_profile_completion() -> None:
    # Given: a required SI1 console before its command completes.
    spec = spec_for((Console.SI1,))
    state = new_profile_state(spec, spec.required_consoles, now=0.0)

    # When: its transport reports EOF.
    result = advance_profile(
        spec,
        state,
        ConsoleSnapshot(si1="READY> ", eof=frozenset({Console.SI1})),
        now=0.0,
    )

    # Then: the run is blocked with stable console attribution.
    assert result.state.phase == "blocked"
    assert result.state.blocker == "fifo_eof:si1"


def test_unavailable_required_console_rejects_preflight() -> None:
    # Given: a dual-console profile with only its primary console bound.
    spec = spec_for((Console.PRIMARY, Console.SI1))

    # When: the immutable state is created before any process starts.
    state = new_profile_state(spec, frozenset({Console.PRIMARY}), now=0.0)

    # Then: the missing console is rejected with stable attribution.
    assert state.phase == "blocked"
    assert state.blocker == "unbound_console:si1"


def test_duplicate_assertion_blocks_normalization() -> None:
    # Given: an evaluator returning the same stable assertion twice.
    duplicate = MarkerEvaluator(("assert-0", "assert-0"))
    spec = spec_for((Console.PRIMARY,), evaluator=duplicate)

    # When: the profile completes.
    _, verdict = drive_success(spec)

    # Then: duplicate evidence cannot become PASS.
    assert verdict == "FAIL"


def test_evaluator_error_and_cleanup_failure_become_blockers() -> None:
    # Given: independently failing evaluation and cleanup adapters.
    evaluator_spec = spec_for((Console.PRIMARY,), evaluator=RaisingEvaluator())
    cleanup_spec = spec_for(
        (Console.PRIMARY,),
        cleanup=FixedCleanup(False),
    )

    # When: each profile reaches finalization.
    evaluator_state = _completed_state(evaluator_spec)
    cleanup_state = _completed_state(cleanup_spec)

    # Then: both failures are explicit blockers with cleanup receipts.
    assert evaluator_state.blocker == "evaluator_error"
    assert evaluator_state.result is not None
    assert evaluator_state.result["verdict"] == "BLOCKED"
    assert all(
        item["status"] == "BLOCKED"
        for item in evaluator_state.result["assertions"]
    )
    assert cleanup_state.blocker == "cleanup_failed:cleanup_receipt"
    assert cleanup_state.cleanup == CleanupReceipt(False, "cleanup_receipt")


def test_evaluator_error_preserves_cleanup_failure_precedence() -> None:
    # Given: evaluation raises and its mandatory cleanup also reports failure.
    spec = spec_for(
        (Console.PRIMARY,),
        evaluator=RaisingEvaluator(),
        cleanup=FixedCleanup(False),
    )

    # When: the live state reaches evaluator finalization.
    state = _completed_state(spec)

    # Then: cleanup owns the blocker and evaluator evidence remains normalized.
    assert state.blocker == "cleanup_failed:cleanup_receipt"
    assert state.cleanup == CleanupReceipt(False, "cleanup_receipt")
    assert state.result is not None
    assert state.result["verdict"] == "BLOCKED"
    assert all(item["status"] == "BLOCKED" for item in state.result["assertions"])


def _completed_state(spec: ProfileProbeSpec):
    state = new_profile_state(spec, spec.required_consoles, now=0.0)
    sent = advance_profile(
        spec,
        state,
        ConsoleSnapshot(primary="READY> "),
        now=0.0,
    ).state
    return advance_profile(
        spec,
        sent,
        ConsoleSnapshot(primary="READY> output\nassert-0\nREADY> "),
        now=1.0,
    ).state


def test_cancel_resume_and_repeated_interruption_are_deterministic() -> None:
    # Given: an immutable state captured after dispatch.
    spec = spec_for((Console.PRIMARY,))
    initial = new_profile_state(spec, spec.required_consoles, now=0.0)
    sent = advance_profile(
        spec,
        initial,
        ConsoleSnapshot(primary="READY> "),
        now=0.0,
    ).state
    resumed_snapshot = ConsoleSnapshot(
        primary="READY> output\nassert-0\nREADY> ",
    )

    # When: two resumed executions consume the same saved state and snapshot.
    first = advance_profile(spec, sent, resumed_snapshot, now=1.0).state
    second = advance_profile(spec, sent, resumed_snapshot, now=1.0).state

    # Then: interruption and resume cannot perturb state transitions.
    assert first == second
    assert first.phase == "passed"

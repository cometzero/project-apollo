from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import Literal

from .result import blocked_profile_result, normalize_profile_result
from .types import (
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    Dispatch,
    EvaluationError,
    NormalizedResultJson,
    ProfileProbeSpec,
)


Phase = Literal["running", "passed", "blocked"]


@dataclass(frozen=True, slots=True)
class ConsoleCursor:
    console: Console
    prompt_end: int


@dataclass(frozen=True, slots=True)
class ProfileState:
    phase: Phase
    next_step: int
    command_sent: bool
    deadline: float | None
    cursors: tuple[ConsoleCursor, ...]
    outputs: tuple[str, ...]
    blocker: str | None
    cleanup: CleanupReceipt | None
    result: NormalizedResultJson | None


@dataclass(frozen=True, slots=True)
class AdvanceResult:
    state: ProfileState
    dispatch: Dispatch | None


def new_profile_state(
    spec: ProfileProbeSpec,
    bound_consoles: frozenset[Console],
    *,
    now: float,
) -> ProfileState:
    spec.validate()
    missing = sorted(spec.required_consoles - bound_consoles)
    if missing:
        names = ",".join(item.value for item in missing)
        return ProfileState(
            phase="blocked",
            next_step=0,
            command_sent=False,
            deadline=None,
            cursors=(),
            outputs=(),
            blocker=f"unbound_console:{names}",
            cleanup=None,
            result=None,
        )
    return ProfileState(
        phase="running",
        next_step=0,
        command_sent=False,
        deadline=now,
        cursors=tuple(
            ConsoleCursor(item, 0) for item in sorted(bound_consoles)
        ),
        outputs=(),
        blocker=None,
        cleanup=None,
        result=None,
    )


def block_profile(
    spec: ProfileProbeSpec,
    state: ProfileState,
    reason: str,
) -> ProfileState:
    if state.phase != "running":
        return state
    cleanup = spec.cleanup.cleanup()
    blocker = reason if cleanup.passed else f"cleanup_failed:{cleanup.detail}"
    result = blocked_profile_result(spec)
    return replace(
        state,
        phase="blocked",
        blocker=blocker,
        cleanup=cleanup,
        result=result,
    )


def _prompt_end(step_pattern: str, content: str) -> int:
    matches = tuple(re.finditer(step_pattern, content))
    return matches[-1].end() if matches else 0


def _cursor(state: ProfileState, console: Console) -> int:
    return next(
        item.prompt_end for item in state.cursors if item.console == console
    )


def _update_cursor(
    state: ProfileState,
    console: Console,
    prompt_end: int,
) -> tuple[ConsoleCursor, ...]:
    return tuple(
        ConsoleCursor(item.console, prompt_end)
        if item.console == console
        else item
        for item in state.cursors
    )


def _finalize(
    spec: ProfileProbeSpec,
    state: ProfileState,
    snapshot: ConsoleSnapshot,
) -> ProfileState:
    try:
        observed = spec.evaluator.evaluate(snapshot, state.outputs)
    except EvaluationError as error:
        cleanup = spec.cleanup.cleanup()
        blocker = (
            error.reason
            if cleanup.passed
            else f"cleanup_failed:{cleanup.detail}"
        )
        return replace(
            state,
            phase="blocked",
            blocker=blocker,
            cleanup=cleanup,
            result=blocked_profile_result(spec),
        )
    result = normalize_profile_result(spec, observed)
    cleanup = spec.cleanup.cleanup()
    if not cleanup.passed:
        return replace(
            state,
            phase="blocked",
            blocker=f"cleanup_failed:{cleanup.detail}",
            cleanup=cleanup,
            result=result,
        )
    phase: Phase = "passed" if result["verdict"] == "PASS" else "blocked"
    return replace(state, phase=phase, cleanup=cleanup, result=result)


def advance_profile(
    spec: ProfileProbeSpec,
    state: ProfileState,
    snapshot: ConsoleSnapshot,
    *,
    now: float,
) -> AdvanceResult:
    if state.phase != "running":
        return AdvanceResult(state, None)
    eof = sorted(spec.required_consoles & snapshot.eof)
    if eof:
        return AdvanceResult(
            block_profile(spec, state, f"fifo_eof:{eof[0].value}"),
            None,
        )
    step = spec.steps[state.next_step]
    content = snapshot.content(step.console)
    prompt_end = _prompt_end(step.prompt_pattern, content)
    previous_prompt_end = _cursor(state, step.console)
    if state.command_sent:
        if prompt_end <= previous_prompt_end:
            if state.deadline is not None and now > state.deadline:
                reason = f"command_timeout:{state.next_step}:{step.console.value}"
                return AdvanceResult(
                    block_profile(spec, state, reason),
                    None,
                )
            return AdvanceResult(state, None)
        output = content[previous_prompt_end:prompt_end]
        if (
            step.completion_pattern is not None
            and re.search(step.completion_pattern, output) is None
        ):
            reason = (
                f"command_record_missing:{state.next_step}:"
                f"{step.console.value}"
            )
            return AdvanceResult(block_profile(spec, state, reason), None)
        progressed = replace(
            state,
            next_step=state.next_step + 1,
            command_sent=False,
            deadline=None,
            cursors=_update_cursor(state, step.console, prompt_end),
            outputs=(*state.outputs, output),
        )
        if progressed.next_step == len(spec.steps):
            return AdvanceResult(_finalize(spec, progressed, snapshot), None)
        next_step = spec.steps[progressed.next_step]
        if next_step.console == step.console:
            dispatched = Dispatch(
                next_step.console,
                next_step.command + "\n",
                progressed.next_step,
            )
            sent = replace(
                progressed,
                command_sent=True,
                deadline=now + next_step.timeout_s,
            )
            return AdvanceResult(sent, dispatched)
        return advance_profile(spec, progressed, snapshot, now=now)
    if prompt_end <= previous_prompt_end:
        return AdvanceResult(state, None)
    dispatched = Dispatch(step.console, step.command + "\n", state.next_step)
    sent = replace(
        state,
        command_sent=True,
        deadline=now + step.timeout_s,
        cursors=_update_cursor(state, step.console, prompt_end),
    )
    return AdvanceResult(sent, dispatched)

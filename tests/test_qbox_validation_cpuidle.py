from __future__ import annotations

from pathlib import Path

import pytest

from scripts.run.qbox_validation.engine import advance_profile, new_profile_state
from scripts.run.qbox_validation.registry import resolve_profile
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
ASSERTIONS = (
    "cpuidle-ensure",
    "cpuidle-c-states",
    "cpuidle-default-status",
    "cpuidle-disable-state",
    "cpuidle-residency-latency",
    "cpuidle-governors",
    "cpuidle-governor-switching",
    "cpuidle-invalid-governor",
)
STATES = (
    ("state0", "WFI", 1, 1),
    ("state1", "cpu-sleep", 4200, 4000),
    ("state2", "cluster-sleep", 4500, 4200),
)


def _state_lines(prefix: str, fields: str) -> str:
    return "\n".join(
        f"CPUIDLE_{prefix} cpu={cpu} state={state} {fields.format(name=name, residency=residency, latency=latency, cpu=cpu)}"
        for cpu in range(4)
        for state, name, residency, latency in STATES
    )


def _passing_outputs() -> tuple[str, ...]:
    cstates = _state_lines("CSTATE", "name={name}")
    defaults = _state_lines("DEFAULT", "value=enabled")
    disabled = _state_lines(
        "DISABLE",
        "before=0 after_write=1 baseline_usage={cpu}0 baseline_time={cpu}00 "
        "sample0_usage={cpu}0 sample0_time={cpu}00 sample1_usage={cpu}0 "
        "sample1_time={cpu}00 restored=0",
    )
    residency = _state_lines(
        "RESIDENCY",
        "residency={residency} latency={latency} usage_before={cpu}0 "
        "usage_after={cpu}1 time_before={cpu}00 time_after={cpu}01 restored=1",
    )
    return (
        "CPUIDLE_ENSURE cpu_count=4 states=12",
        cstates,
        defaults,
        disabled,
        residency,
        "CPUIDLE_GOVERNORS available=menu,teo current=menu current_ro=menu",
        "\n".join(
            (
                "CPUIDLE_SWITCH requested=menu current=menu current_ro=menu",
                "CPUIDLE_SWITCH requested=teo current=teo current_ro=teo",
                "CPUIDLE_SWITCH_RESTORE original=menu current=menu current_ro=menu restored=1",
            )
        ),
        "CPUIDLE_INVALID rejected=1 original=menu current=menu current_ro=menu restored=1",
    )


def _statuses(outputs: tuple[str, ...]) -> dict[str, str]:
    spec = resolve_profile("cpuidle", MATRIX)
    result = evaluate_profile_result(
        spec, ConsoleSnapshot(primary="nexios-bsp# "), outputs
    )
    return {item["id"]: item["status"] for item in result["assertions"]}


def test_cpuidle_registry_uses_ordered_primary_console_contract() -> None:
    spec = resolve_profile("cpuidle", MATRIX)

    assert spec.expected_assertion_ids == ASSERTIONS
    assert spec.required_consoles == frozenset({Console.PRIMARY})
    assert tuple(step.console for step in spec.steps) == (Console.PRIMARY,) * 8
    assert spec.legacy_flag is None


def test_cpuidle_evaluator_accepts_complete_numeric_snapshots() -> None:
    spec = resolve_profile("cpuidle", MATRIX)
    result = evaluate_profile_result(
        spec,
        ConsoleSnapshot(primary="nexios-bsp# "),
        _passing_outputs(),
    )

    assert result["verdict"] == "PASS"
    assert tuple(item["id"] for item in result["assertions"]) == ASSERTIONS
    assert {item["status"] for item in result["assertions"]} == {"PASS"}


@pytest.mark.parametrize(
    ("index", "old", "new", "failed_assertion"),
    (
        (0, "states=12", "states=11", "cpuidle-ensure"),
        (0, "states=12", "states=12 extra=1", "cpuidle-ensure"),
        (1, "cpu=3 state=state2", "cpu=4 state=state2", "cpuidle-c-states"),
        (1, "name=cluster-sleep", "name=wrong", "cpuidle-c-states"),
        (2, "value=enabled", "value=disabled", "cpuidle-default-status"),
        (3, "sample1_time=300", "sample1_time=301", "cpuidle-disable-state"),
        (4, "usage_after=31", "usage_after=30", "cpuidle-residency-latency"),
        (4, "usage_before=00 ", "", "cpuidle-residency-latency"),
        (4, "latency=4200", "latency=4199", "cpuidle-residency-latency"),
        (5, "current_ro=menu", "current_ro=ghost", "cpuidle-governors"),
        (6, "current=teo", "current=menu", "cpuidle-governor-switching"),
        (7, "rejected=1", "rejected=0", "cpuidle-invalid-governor"),
        (7, "restored=1", "restored=0", "cpuidle-invalid-governor"),
    ),
)
def test_cpuidle_evaluator_rejects_contract_drift(
    index: int,
    old: str,
    new: str,
    failed_assertion: str,
) -> None:
    outputs = list(_passing_outputs())
    assert old in outputs[index]
    outputs[index] = outputs[index].replace(old, new, 1)

    statuses = _statuses(tuple(outputs))

    assert statuses[failed_assertion] == "FAIL"


def test_cpuidle_evaluator_rejects_missing_and_malformed_records() -> None:
    outputs = list(_passing_outputs())
    outputs[3] = outputs[3].replace(" baseline_usage=00", " baseline_usage=oops", 1)
    outputs[4] = "\n".join(outputs[4].splitlines()[:-1])

    statuses = _statuses(tuple(outputs))

    assert statuses["cpuidle-disable-state"] == "FAIL"
    assert statuses["cpuidle-residency-latency"] == "FAIL"


def test_cpuidle_timeout_and_eof_are_blocked_with_cleanup() -> None:
    spec = resolve_profile("cpuidle", MATRIX)
    state = new_profile_state(spec, frozenset({Console.PRIMARY}), now=0.0)
    sent = advance_profile(
        spec,
        state,
        ConsoleSnapshot(primary="nexios-bsp# "),
        now=0.0,
    ).state

    timed_out = advance_profile(
        spec,
        sent,
        ConsoleSnapshot(primary="nexios-bsp# partial"),
        now=spec.steps[0].timeout_s + 1.0,
    ).state
    eof = advance_profile(
        spec,
        state,
        ConsoleSnapshot(primary="nexios-bsp# ", eof=frozenset({Console.PRIMARY})),
        now=0.0,
    ).state

    assert timed_out.phase == "blocked"
    assert timed_out.blocker == "command_timeout:0:primary"
    assert timed_out.cleanup is not None and timed_out.cleanup.passed
    assert eof.phase == "blocked"
    assert eof.blocker == "fifo_eof:primary"
    assert eof.cleanup is not None and eof.cleanup.passed

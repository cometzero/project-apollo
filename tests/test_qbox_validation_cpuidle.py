from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import re
import subprocess

import pytest

from scripts.run.qbox_validation.engine import advance_profile, new_profile_state
from scripts.run.qbox_validation.registry import resolve_profile
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot
from scripts.run.qbox_cpuidle_guest import (
    GUEST_PROBE,
    GUEST_PROBE_PATH,
    guest_probe_install_commands,
)


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
        "sample1_time={cpu}00 peer_disable_before=0 peer_disable_after=0 "
        "restored=0",
    )
    residency = _state_lines(
        "RESIDENCY",
        "residency={residency} latency={latency} usage_before={cpu}0 "
        "usage_after={cpu}1 time_before={cpu}00 time_after={cpu}01 "
        "wake=natural-timer restored=1",
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
        "CPUIDLE_INVALID rejected=1 original=menu current=menu current_ro=menu "
        "disable_zero=12 restored=1",
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
    assert all(step.console == Console.PRIMARY for step in spec.steps)
    assert max(len(step.command.encode("utf-8")) for step in spec.steps) <= 700
    assert all("\n" not in step.command for step in spec.steps)
    assert all("sleep " not in step.command for step in spec.steps)
    assert "read -r _wake" not in GUEST_PROBE
    assert "sleep 0.5" in GUEST_PROBE
    assert "sleep 1" in GUEST_PROBE
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


def test_cpuidle_guest_install_chunks_reconstruct_exact_payload() -> None:
    commands = guest_probe_install_commands()
    encoded = "".join(item.split("'", maxsplit=2)[1] for item in commands[1:-1])
    octets = encoded.removeprefix("\\").split("\\")

    decoded = bytes(int(item, 8) for item in octets).decode("utf-8")

    assert decoded == GUEST_PROBE
    assert commands[0] == f": > {GUEST_PROBE_PATH}"
    assert commands[-1] == f"chmod 700 {GUEST_PROBE_PATH}"


def test_cpuidle_evaluator_accepts_fragmented_runtime_records() -> None:
    spec = resolve_profile("cpuidle", MATRIX)
    lines = "\n".join(_passing_outputs()).splitlines()

    result = evaluate_profile_result(
        spec,
        ConsoleSnapshot(primary="nexios-bsp# "),
        tuple(lines),
    )

    assert result["verdict"] == "PASS"
    assert {item["status"] for item in result["assertions"]} == {"PASS"}


def test_cpuidle_identical_residency_rejects_host_uart_wake() -> None:
    outputs = tuple(
        item.replace("wake=natural-timer", "wake=host-uart")
        for item in _passing_outputs()
    )
    statuses = _statuses(outputs)

    assert statuses["cpuidle-residency-latency"] == "FAIL"


def test_cpuidle_prompt_echo_cannot_complete_operation_without_record() -> None:
    spec = resolve_profile("cpuidle", MATRIX)
    ensure_step = next(
        step
        for step in spec.steps
        if step.command == f"{GUEST_PROBE_PATH} ensure"
    )
    framing_spec = replace(spec, steps=(ensure_step,))
    state = new_profile_state(
        framing_spec,
        frozenset({Console.PRIMARY}),
        now=0.0,
    )
    sent = advance_profile(
        framing_spec,
        state,
        ConsoleSnapshot(primary="nexios-bsp# "),
        now=0.0,
    ).state

    advanced = advance_profile(
        framing_spec,
        sent,
        ConsoleSnapshot(
            primary=f"nexios-bsp# {ensure_step.command}\nnexios-bsp# ",
        ),
        now=0.1,
    )

    assert advanced.dispatch is None
    assert advanced.state.next_step == 0
    assert advanced.state.phase == "blocked"
    assert advanced.state.blocker == "command_record_missing:0:primary"


@pytest.mark.parametrize("outputs", ((), _passing_outputs()[:2]))
def test_cpuidle_zero_or_two_of_eight_records_never_pass(
    outputs: tuple[str, ...],
) -> None:
    spec = resolve_profile("cpuidle", MATRIX)

    result = evaluate_profile_result(
        spec,
        ConsoleSnapshot(primary="nexios-bsp# "),
        outputs,
    )

    assert result["verdict"] != "PASS"
    assert {item["status"] for item in result["assertions"]} != {"PASS"}


@pytest.mark.parametrize(
    ("index", "old", "new", "failed_assertion"),
    (
        (0, "states=12", "states=11", "cpuidle-ensure"),
        (0, "states=12", "states=12 extra=1", "cpuidle-ensure"),
        (1, "cpu=3 state=state2", "cpu=4 state=state2", "cpuidle-c-states"),
        (1, "name=cluster-sleep", "name=wrong", "cpuidle-c-states"),
        (2, "value=enabled", "value=disabled", "cpuidle-default-status"),
        (2, "value=enabled", "value=absent", "cpuidle-default-status"),
        (3, "sample1_time=300", "sample1_time=301", "cpuidle-disable-state"),
        (4, "usage_after=31", "usage_after=30", "cpuidle-residency-latency"),
        (4, "usage_before=00 ", "", "cpuidle-residency-latency"),
        (4, "latency=4200", "latency=4199", "cpuidle-residency-latency"),
        (5, "current_ro=menu", "current_ro=ghost", "cpuidle-governors"),
        (5, "available=menu,teo", "available=menu,teo,ladder", "cpuidle-governors"),
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


def _unsupported_outputs() -> tuple[str, ...]:
    commands = (
        *((mode, "all", "all") for mode in
          ("ensure", "cstates", "defaults", "governors", "switch", "invalid")),
        *((mode, str(cpu), state) for mode in ("disable", "residency")
          for cpu in range(4) for state in ("state0", "state1", "state2")),
    )
    return tuple(
        "CPUIDLE_UNSUPPORTED reason=psci_powerdown_wakeup_unmodeled "
        "compatible=arm,apollo-qvp driver=none cpu_count=4 "
        f"dt_idle_states=0 sysfs_states=0 mode={mode} cpu={cpu} state={state}"
        for mode, cpu, state in commands
    )


def test_cpuidle_actual_unsupported_records_are_blocked_with_reason() -> None:
    spec = resolve_profile("cpuidle", MATRIX)
    ensure_step = next(step for step in spec.steps
                       if step.command == f"{GUEST_PROBE_PATH} ensure")
    framing = replace(spec, steps=(ensure_step,))
    state = new_profile_state(framing, frozenset({Console.PRIMARY}), now=0.0)
    state = advance_profile(framing, state, ConsoleSnapshot(primary="nexios-bsp# "),
                            now=0.0).state
    state = advance_profile(
        framing, state,
        ConsoleSnapshot(primary="nexios-bsp# \n" + "\n".join(_unsupported_outputs())
                        + "\nnexios-bsp# "), now=0.1,
    ).state
    assert state.phase == "blocked"
    assert state.blocker == "unsupported:psci_powerdown_wakeup_unmodeled"
    assert state.result is not None and state.result["verdict"] == "BLOCKED"
    assert {item["status"] for item in state.result["assertions"]} == {"BLOCKED"}


@pytest.mark.parametrize("mutation", (
    "missing", "duplicate", "driver", "compatible", "dt", "sysfs", "reason", "mixed",
))
def test_cpuidle_forged_or_partial_unsupported_evidence_fails(mutation: str) -> None:
    outputs = list(_unsupported_outputs())
    replacements = {
        "driver": ("driver=none", "driver=psci"),
        "compatible": ("compatible=arm,apollo-qvp", "compatible=arm,apollo-fvp"),
        "dt": ("dt_idle_states=0", "dt_idle_states=2"),
        "sysfs": ("sysfs_states=0", "sysfs_states=1"),
        "reason": ("reason=psci_powerdown_wakeup_unmodeled", "reason=unknown"),
    }
    if mutation == "missing":
        outputs.pop()
    elif mutation == "duplicate":
        outputs[-1] = outputs[0]
    elif mutation == "mixed":
        outputs.extend(_passing_outputs())
    else:
        old, new = replacements[mutation]
        outputs[0] = outputs[0].replace(old, new)
    assert set(_statuses(tuple(outputs)).values()) == {"FAIL"}


def _guest_capabilities(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, str]]:
    cpu_root, dt_root, bin_dir = (tmp_path / name for name in ("cpu", "dt", "bin"))
    (cpu_root / "cpuidle").mkdir(parents=True)
    (cpu_root / "cpuidle/current_driver").write_text("none\n")
    (cpu_root / "online").write_text("0-3\n")
    (dt_root / "cpus").mkdir(parents=True)
    (dt_root / "compatible").write_bytes(b"arm,apollo-qvp\0arm,zena-css\0")
    for cpu in range(16):
        (cpu_root / f"cpu{cpu}").mkdir()
        (dt_root / f"cpus/cpu@{cpu:x}").mkdir()
    bin_dir.mkdir()
    (bin_dir / "nproc").write_text("#!/bin/sh\nprintf '16\\n'\n")
    (bin_dir / "nproc").chmod(0o755)
    probe = tmp_path / "probe.sh"
    probe.write_text(GUEST_PROBE.replace("cpu_root=/sys/devices/system/cpu",
                                         f"cpu_root='{cpu_root}'")
                     .replace("dt_root=/proc/device-tree", f"dt_root='{dt_root}'"))
    return cpu_root, dt_root, probe, {**os.environ, "PATH": f"{bin_dir}:{os.defpath}"}


def test_cpuidle_guest_wfi_only_guard_completes_every_mode(tmp_path: Path) -> None:
    cpu_root, _dt_root, probe, env = _guest_capabilities(tmp_path)
    spec = resolve_profile("cpuidle", MATRIX)
    outputs = []
    for step in spec.steps:
        if not step.command.startswith(GUEST_PROBE_PATH + " "):
            continue
        arguments = step.command.split()[1:]
        result = subprocess.run(["sh", str(probe), *arguments], env=env,
                                capture_output=True, text=True, timeout=5)
        assert result.returncode == 0, result.stderr
        assert step.completion_pattern and re.search(step.completion_pattern, result.stdout)
        outputs.append(result.stdout)
    assert not probe.exists()  # The final operation removes the installed probe.
    assert (cpu_root / "cpuidle/current_driver").read_text() == "none\n"
    assert set(_statuses(tuple(outputs)).values()) == {"BLOCKED"}


@pytest.mark.parametrize("mismatch", ("fvp", "driver", "dt-node", "dt-reference", "sysfs-state"))
def test_cpuidle_guest_does_not_skip_inconsistent_capabilities(
    tmp_path: Path, mismatch: str,
) -> None:
    cpu_root, dt_root, probe, env = _guest_capabilities(tmp_path)
    if mismatch == "fvp":
        (dt_root / "compatible").write_bytes(b"arm,apollo-fvp\0")
    elif mismatch == "driver":
        (cpu_root / "cpuidle/current_driver").write_text("psci\n")
    elif mismatch == "dt-node":
        (dt_root / "cpus/idle-states").mkdir()
    elif mismatch == "dt-reference":
        (dt_root / "cpus/cpu@2/cpu-idle-states").write_bytes(b"\0\0\0\1")
    else:
        (cpu_root / "cpu2/cpuidle/state0").mkdir(parents=True)
    result = subprocess.run(["sh", str(probe), "ensure"], env=env,
                            capture_output=True, text=True, timeout=5)
    assert result.returncode != 0
    assert "CPUIDLE_UNSUPPORTED" not in result.stdout


def test_cpuidle_accepts_only_advertised_menu_governor() -> None:
    outputs = list(_passing_outputs())
    outputs[5] = outputs[5].replace("menu,teo", "menu")
    outputs[6] = "\n".join(line for line in outputs[6].splitlines()
                           if "requested=teo" not in line)
    assert set(_statuses(tuple(outputs)).values()) == {"PASS"}


@pytest.mark.parametrize("available", ["menu,menu", "menu,", ",menu", ""])
def test_cpuidle_rejects_malformed_governor_list(available: str) -> None:
    outputs = list(_passing_outputs())
    outputs[5] = outputs[5].replace("menu,teo", available)
    assert _statuses(tuple(outputs))["cpuidle-governors"] == "FAIL"


def test_cpuidle_guest_accepts_sysfs_governor_whitespace(tmp_path: Path) -> None:
    cpu_root, _dt_root, probe, env = _guest_capabilities(tmp_path)
    idle = cpu_root / "cpuidle"
    (idle / "current_driver").write_text("psci\n")
    for name, value in (("available_governors", "menu \n"),
                        ("current_governor", "menu\n"),
                        ("current_governor_ro", "menu\n")):
        (idle / name).write_text(value)
    result = subprocess.run(["sh", str(probe), "governors"], env=env,
                            capture_output=True, text=True, check=True)
    assert result.stdout.strip() == (
        "CPUIDLE_GOVERNORS available=menu current=menu current_ro=menu")

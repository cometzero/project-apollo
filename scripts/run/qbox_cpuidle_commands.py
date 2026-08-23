from __future__ import annotations

from dataclasses import dataclass

from scripts.run.qbox_cpuidle_guest import (
    GUEST_PROBE_PATH,
    guest_probe_install_commands,
)


@dataclass(frozen=True, slots=True)
class CpuIdleProbeCommand:
    command: str
    timeout_s: float = 60.0
    completion_pattern: str | None = None


def _command(arguments: str, marker: str) -> CpuIdleProbeCommand:
    return CpuIdleProbeCommand(
        f"{GUEST_PROBE_PATH} {arguments}",
        completion_pattern=rf"(?m)^{marker} ",
    )


def _disable_command(cpu: int, state: str) -> CpuIdleProbeCommand:
    return CpuIdleProbeCommand(
        f"{GUEST_PROBE_PATH} disable {cpu} {state}",
        30.0,
        completion_pattern=r"(?m)^CPUIDLE_DISABLE ",
    )


def _residency_command(
    cpu: int,
    state: str,
    residency: int,
    latency: int,
) -> CpuIdleProbeCommand:
    limit = 90 if state == "state2" else 30
    return CpuIdleProbeCommand(
        f"{GUEST_PROBE_PATH} residency {cpu} {state} "
        f"{residency} {latency} {limit}",
        float(limit + 15),
        completion_pattern=r"(?m)^CPUIDLE_RESIDENCY ",
    )


def cpuidle_probe_commands() -> tuple[CpuIdleProbeCommand, ...]:
    install = tuple(
        CpuIdleProbeCommand(item) for item in guest_probe_install_commands()
    )
    disabled = tuple(
        _disable_command(cpu, state)
        for cpu in range(4)
        for state in ("state0", "state1", "state2")
    )
    residency = tuple(
        _residency_command(cpu, state, expected_res, expected_lat)
        for cpu in range(4)
        for state, expected_res, expected_lat in (
            ("state0", 1, 1),
            ("state1", 4200, 4000),
            ("state2", 4500, 4200),
        )
    )
    return (
        *install,
        _command("ensure", "CPUIDLE_ENSURE"),
        _command("cstates", "CPUIDLE_CSTATE"),
        _command("defaults", "CPUIDLE_DEFAULT"),
        *disabled,
        *residency,
        _command("governors", "CPUIDLE_GOVERNORS"),
        _command("switch", "CPUIDLE_SWITCH_RESTORE"),
        _command("invalid", "CPUIDLE_INVALID"),
    )

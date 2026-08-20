from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final, Literal


SI_CL1_CPU_COUNT: Final = 4
Observation = Literal[
    "status_seen",
    "run_success_seen",
    "success_result_seen",
    "force_error_seen",
    "failed_result_seen",
]


@dataclass(frozen=True, slots=True)
class SiCl1PFDICheck:
    name: str
    command: str
    patterns: tuple[str, ...]
    pattern_examples: tuple[str, ...]
    cpu: int | None = None
    observations: tuple[Observation, ...] = ()


@dataclass(frozen=True, slots=True)
class RunCheckSpec:
    name: str
    command: str
    description: str
    cpu: int
    observations: tuple[Observation, ...] = ()


def _stats() -> tuple[str, str]:
    return (
        r"scheduled:\s*\d+,\s*success:\s*\d+,\s*skipped:\s*\d+",
        "scheduled: 4, success: 4, skipped: 0",
    )


def _run_check(spec: RunCheckSpec) -> SiCl1PFDICheck:
    stats_pattern, stats_example = _stats()
    description_example = (
        spec.description.replace(r"\s+", " ").replace(r"\s*", "").replace(".*", " ")
    )
    return SiCl1PFDICheck(
        name=spec.name,
        command=spec.command,
        patterns=(r"rc=0", spec.description, stats_pattern),
        pattern_examples=("rc=0", description_example, stats_example),
        cpu=spec.cpu,
        observations=spec.observations,
    )


def si_cl1_pfdi_checks() -> list[SiCl1PFDICheck]:
    checks: list[SiCl1PFDICheck] = []
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_01_status_cpu{cpu}",
                f"pfdi get-status {cpu}",
                (rf"cpu{cpu}.*(running|stopped|disabled)",),
                (f"pfdi: cpu{cpu} running",),
                cpu=cpu,
                observations=("status_seen",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            _run_check(
                RunCheckSpec(
                    f"test_02_run_all_cpu{cpu}",
                    f"pfdi run {cpu}",
                    rf"cpu{cpu}.*all blocks",
                    cpu,
                    ("run_success_seen",),
                )
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_03_invalid_block_cpu{cpu}",
                f"pfdi run {cpu} 0",
                (r"(invalid|error|block id)",),
                ("invalid block id",),
            )
        )
        checks.append(
            SiCl1PFDICheck(
                f"test_03_valid_block_cpu{cpu}",
                f"pfdi run {cpu} 1",
                (r"rc=0",),
                ("rc=0",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        invalid_commands = (
            f"pfdi run {cpu} -2",
            f"pfdi run {cpu} 1 -2 -1",
            f"pfdi run {cpu} 1 -1 -2",
            f"pfdi run {cpu} 1 2 1",
            f"pfdi run {cpu} -1 1 2",
        )
        for index, command in enumerate(invalid_commands):
            checks.append(
                SiCl1PFDICheck(
                    f"test_04_invalid_{index}_cpu{cpu}",
                    command,
                    (r"(invalid|error|argument)",),
                    ("invalid argument",),
                )
            )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            _run_check(
                RunCheckSpec(
                    f"test_05_all_cpu{cpu}",
                    f"pfdi run {cpu}",
                    rf"cpu{cpu}.*all blocks",
                    cpu,
                )
            )
        )
        checks.append(
            _run_check(
                RunCheckSpec(
                    f"test_05_block_cpu{cpu}",
                    f"pfdi run {cpu} 1",
                    rf"cpu{cpu}.*block id\s+1.*all parts",
                    cpu,
                )
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            _run_check(
                RunCheckSpec(
                    f"test_06_range_cpu{cpu}",
                    f"pfdi run {cpu} 1 1 2",
                    r"block id\s+1.*part range:\s*1->2",
                    cpu,
                )
            )
        )
    checks.append(SiCl1PFDICheck("test_07_invalid_cpu", "pfdi run all", (r"(invalid|error)",), ("invalid cpu",)))
    checks.append(SiCl1PFDICheck("test_08_cpu_out_of_range", f"pfdi run {SI_CL1_CPU_COUNT}", (r"(invalid|range|error)",), ("cpu out of range",)))
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_09_count_cpu{cpu}",
                f"pfdi count {cpu}",
                (rf"cpu{cpu}.*\d+",),
                (f"pfdi: cpu{cpu} count 4",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_10_count_block_cpu{cpu}",
                f"pfdi count {cpu} 1",
                (rf"cpu{cpu}.*\d+",),
                (f"pfdi: cpu{cpu} block 1 count 4",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_11_result_cpu{cpu}",
                f"pfdi result {cpu}",
                (rf"cpu{cpu}.*SUCCESS",),
                (f"pfdi: cpu{cpu} result SUCCESS",),
                cpu=cpu,
                observations=("success_result_seen",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_12_disable_cpu{cpu}", f"pfdi set-status {cpu} 0", (), ()
            )
        )
        checks.append(
            SiCl1PFDICheck(
                f"test_12_disabled_cpu{cpu}",
                f"pfdi get-status {cpu}",
                (r"(disabled|stopped)",),
                (f"pfdi: cpu{cpu} disabled",),
            )
        )
        checks.append(
            SiCl1PFDICheck(
                f"test_12_enable_cpu{cpu}", f"pfdi set-status {cpu} 1", (), ()
            )
        )
        checks.append(
            SiCl1PFDICheck(
                f"test_12_running_cpu{cpu}",
                f"pfdi get-status {cpu}",
                (r"running",),
                (f"pfdi: cpu{cpu} running",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        checks.append(
            SiCl1PFDICheck(
                f"test_13_force_error_cpu{cpu}",
                f"pfdi force-error {cpu} 1",
                (r"(forced|error-id)",),
                (f"pfdi: forced error-id: 1 on cpu{cpu}",),
                cpu=cpu,
                observations=("force_error_seen",),
            )
        )
        checks.append(
            SiCl1PFDICheck(
                f"test_13_failed_result_cpu{cpu}",
                f"pfdi result {cpu}",
                (rf"cpu{cpu}.*FAILED",),
                (f"pfdi: cpu{cpu} result FAILED",),
                cpu=cpu,
                observations=("failed_result_seen",),
            )
        )
    for cpu in range(SI_CL1_CPU_COUNT):
        for run in range(3):
            checks.append(
                _run_check(
                    RunCheckSpec(
                        f"test_14_run_{run}_cpu{cpu}",
                        f"pfdi run {cpu}",
                        rf"cpu{cpu}.*all blocks",
                        cpu,
                    )
                )
            )
    for cpu in range(SI_CL1_CPU_COUNT):
        for run in range(5):
            checks.append(
                _run_check(
                    RunCheckSpec(
                        f"test_15_run_{run}_cpu{cpu}",
                        f"pfdi run {cpu}",
                        rf"cpu{cpu}.*all blocks",
                        cpu,
                    )
                )
            )
    firmware = "pfdi: cpu0 firmware: stub implementation detected (no vendor library)"
    checks.append(SiCl1PFDICheck("test_16_info", "pfdi info 0", (re.escape(firmware),), (firmware,)))
    return checks

from __future__ import annotations

import re
from typing import Final, TypedDict

from qbox_si_cl1_pfdi_catalog import (
    SI_CL1_CPU_COUNT,
    SiCl1PFDICheck,
    si_cl1_pfdi_checks,
)


SI_CL1_PROMPT_RE: Final = re.compile(
    r"(?m)(?:^|\n)(?:(?:uart:)?~\$\s*)+$"
)


class SiCl1PFDICpuResult(TypedDict):
    cpu: int
    status_seen: bool
    run_success_seen: bool
    success_result_seen: bool
    force_error_seen: bool
    failed_result_seen: bool


class SiCl1PFDIRecord(TypedDict):
    name: str
    command: str
    output: str
    passed: bool
    missing_patterns: list[str]


class SiCl1PFDIProbeResult(TypedDict):
    passed: bool
    complete: bool
    checks_total: int
    checks_passed: int
    failed_checks: list[str]
    records: list[SiCl1PFDIRecord]
    cpus: list[SiCl1PFDICpuResult]
    firmware_info_seen: bool


class SiCl1PFDIProbeState(TypedDict):
    checks: list[SiCl1PFDICheck]
    outputs: list[str]
    command_index: int
    last_prompt_end: int
    sent_probe: bool
    complete: bool


def new_si_cl1_pfdi_state() -> SiCl1PFDIProbeState:
    return {
        "checks": si_cl1_pfdi_checks(),
        "outputs": [],
        "command_index": 0,
        "last_prompt_end": 0,
        "sent_probe": False,
        "complete": False,
    }


def advance_si_cl1_pfdi_probe(
    state: SiCl1PFDIProbeState,
    console: str,
) -> str | None:
    prompts = list(SI_CL1_PROMPT_RE.finditer(console))
    if not prompts or state["complete"]:
        return None
    prompt_end = prompts[-1].end()
    if state["sent_probe"] and prompt_end <= state["last_prompt_end"]:
        return None
    if state["sent_probe"]:
        state["outputs"].append(console[state["last_prompt_end"] : prompt_end])
    if len(state["outputs"]) == len(state["checks"]):
        state["complete"] = True
        return None
    check = state["checks"][state["command_index"]]
    state["command_index"] += 1
    state["last_prompt_end"] = prompt_end
    state["sent_probe"] = True
    return check.command + "\n"


def evaluate_si_cl1_pfdi_records(
    checks: list[SiCl1PFDICheck],
    outputs: list[str],
) -> SiCl1PFDIProbeResult:
    cpus: list[SiCl1PFDICpuResult] = [
        {
            "cpu": cpu,
            "status_seen": False,
            "run_success_seen": False,
            "success_result_seen": False,
            "force_error_seen": False,
            "failed_result_seen": False,
        }
        for cpu in range(SI_CL1_CPU_COUNT)
    ]
    records: list[SiCl1PFDIRecord] = []
    failed_checks: list[str] = []
    for index, check in enumerate(checks):
        output = outputs[index] if index < len(outputs) else ""
        missing = [
            pattern
            for pattern in check.patterns
            if re.search(pattern, output) is None
        ]
        passed = not missing and index < len(outputs)
        if not passed:
            failed_checks.append(check.name)
        elif check.cpu is not None:
            for observation in check.observations:
                cpus[check.cpu][observation] = True
        records.append(
            {
                "name": check.name,
                "command": check.command,
                "output": output,
                "passed": passed,
                "missing_patterns": missing,
            }
        )
    return {
        "passed": not failed_checks and len(outputs) == len(checks),
        "complete": len(outputs) == len(checks),
        "checks_total": len(checks),
        "checks_passed": sum(record["passed"] for record in records),
        "failed_checks": failed_checks,
        "records": records,
        "cpus": cpus,
        "firmware_info_seen": bool(records and records[-1]["passed"]),
    }

#!/usr/bin/env python3
"""Verify Apollo FVP full-system QBox completion evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
EXPECTED_AP_CPUS = 4
AP_CPU_COUNT_RE = re.compile(r"^ap cpus:\s*(?P<count>\d+)\s*$", re.MULTILINE)
FINAL_OUTPUT_NAME = "final-verification.json"
REQUIRED_FULL_LOGS = [
    "rse",
    "si_cl0",
    "si_cl1",
    "secure_console",
    "primary_console",
]
GOAL_ID = "qbox-apollo-fvp-full-system-g0-g5"
REQUIRED_MARKER_GROUPS = [
    "rse",
    "si_cl0",
    "si_cl1",
    "ap_firmware",
    "linux",
    "post_login",
    "maps_and_interrupts",
]
FINAL_EVIDENCE_BUNDLE = [
    "result.json",
    "comparison.json",
    "map-comparison.json",
    "coverage-audit.json",
    FINAL_OUTPUT_NAME,
]
GOAL_DEFINITION = {
    "goal_id": GOAL_ID,
    "objective": (
        "Boot local Apollo FVP artifacts in QBox through the FVP-equivalent "
        "subsystem chain: RSE TF-M, SI CL0 SCP-firmware, SI CL1 Zephyr, "
        "and AP TF-A/OP-TEE/U-Boot/Linux."
    ),
    "target_machine": "apollo-fvp",
    "subsystem_chain": [
        "RSE TF-M",
        "SI CL0 SCP-firmware",
        "SI CL1 Zephyr",
        "AP TF-A",
        "AP OP-TEE",
        "AP U-Boot",
        "AP Linux",
    ],
    "required_live_domains_for_completion": [
        "RSE",
        "SI CL0",
        "SI CL1",
        "Primary Compute",
    ],
    "not_completion_points": [
        "AP Linux direct boot reaches login",
        "RSE-first service-model boot reaches Linux",
        "isolated SI CL0 or CL1 firmware boots without AP integration",
        "live CL1 integration without live CL0 SCP-firmware",
        "tmux-only console output without saved result.json and UART logs",
    ],
    "completion_point": (
        "Strict final verification passes after one integrated live CL0/CL1 "
        "run plus FVP comparison, map comparison, and coverage audit evidence."
    ),
}
COMPLETION_POLICY = {
    "required_gates": {gate: "pass" for gate in GATES},
    "strict_final_required": True,
    "required_final_run": "full-live-cl0-cl1",
    "required_final_logs": REQUIRED_FULL_LOGS,
    "required_marker_groups": REQUIRED_MARKER_GROUPS,
    "required_final_sidecars": FINAL_EVIDENCE_BUNDLE,
    "required_final_output": (
        "build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json"
    ),
    "completion_claim_allowed_when": (
        "strict_final is true, the final output path is canonical, "
        "completion_ready is true, and all G0..G5 gates are pass."
    ),
    "failure_policy": (
        "Any missing required marker, absent boot-critical block, or "
        "unclassified fidelity gap is fail for strict final completion."
    ),
}
COMPLETION_LEVELS = {
    "G0": {
        "name": "Contract readiness",
        "objective": (
            "Local artifacts, Cortex-R82 support, map ledger, and coverage "
            "contract are available."
        ),
        "completion_role": "required precondition",
    },
    "G1": {
        "name": "Direct-boot guardrail",
        "objective": "The existing AP Linux direct-boot path has not regressed.",
        "completion_role": "required regression guardrail",
    },
    "G2": {
        "name": "Service-model full boot",
        "objective": (
            "RSE-first QBox boot reaches AP Linux while Safety Island CPU "
            "fidelity debt is explicit."
        ),
        "completion_role": "required milestone, not final completion",
    },
    "G3": {
        "name": "Live CL1 integration",
        "objective": (
            "Zephyr CL1 runs live on Cortex-R82 and AP Linux HIPC/RPMsg or "
            "PFDI evidence uses live CL1 behavior."
        ),
        "completion_role": "required milestone, not final completion",
    },
    "G4": {
        "name": "Live CL0/CL1 integration",
        "objective": (
            "RSE, live CL0 SCP-firmware, live CL1 Zephyr, AP firmware, "
            "U-Boot, Linux, and post-login marker groups pass in one run."
        ),
        "completion_role": "final runtime candidate",
    },
    "G5": {
        "name": "FVP equivalence closure",
        "objective": (
            "The full live QBox run matches required FVP markers, documented "
            "maps, and boot-critical hardware coverage."
        ),
        "completion_role": "final acceptance gate",
    },
}
GOAL_VERIFICATION_PLAN = [
    {
        "gate": "G0",
        "name": "Contract readiness",
        "required_evidence": [
            "full-check-only/result.json",
            "full-check-only/map-validation.json",
            "full-check-only/coverage-audit.json",
            "Cortex-R82 and platforms-vp build evidence",
        ],
        "completion_role": "required precondition",
    },
    {
        "gate": "G1",
        "name": "Direct-boot guardrail",
        "required_evidence": [
            "direct-guardrail/result.json",
            "direct AP console log",
            "post-login probe markers",
        ],
        "completion_role": "required regression guardrail",
    },
    {
        "gate": "G2",
        "name": "Service-model full boot",
        "required_evidence": [
            "full-service-model/result.json",
            "full-service-model/comparison.json",
            "file-backed RSE, SI, secure, and primary console logs",
        ],
        "completion_role": "required milestone, not final completion",
    },
    {
        "gate": "G3",
        "name": "Live CL1 integration",
        "required_evidence": [
            "full-live-cl1/result.json",
            "CL1 Zephyr markers",
            "AP Linux HIPC/RPMsg/PFDI post-login markers",
        ],
        "completion_role": "required milestone, not final completion",
    },
    {
        "gate": "G4",
        "name": "Live CL0/CL1 integration",
        "required_evidence": [
            "full-live-cl0-cl1/result.json",
            "RSE, SI CL0, SI CL1, AP firmware, Linux, and post-login marker groups",
            "file-backed subsystem logs",
        ],
        "completion_role": "final runtime candidate",
    },
    {
        "gate": "G5",
        "name": "FVP equivalence closure",
        "required_evidence": [
            "full-live-cl0-cl1/comparison.json",
            "full-live-cl0-cl1/map-comparison.json",
            "full-live-cl0-cl1/coverage-audit.json",
            "full-live-cl0-cl1/final-verification.json",
        ],
        "completion_role": "final acceptance gate",
    },
]
FINAL_ACCEPTANCE_ARTIFACTS = {
    "evidence_directory": "build/qbox-apollo-fvp/full-live-cl0-cl1",
    "required_files": FINAL_EVIDENCE_BUNDLE,
    "required_logs": REQUIRED_FULL_LOGS,
    "required_marker_groups": REQUIRED_MARKER_GROUPS,
    "not_accepted_as_completion": GOAL_DEFINITION["not_completion_points"],
}
REVIEW_RULES = [
    "Final completion is authorized only by --strict-final verifier success.",
    "All G0..G5 gates must be pass in the same final verification output.",
    "Service-model and isolated live-domain runs are milestone evidence only.",
    "Every runtime claim must cite result.json and file-backed subsystem logs.",
    "Unclassified missing markers or absent boot-critical hardware are failures.",
]
SI_CL1_ISOLATED_REQUIRED = [
    "cpu0_oor",
    "zephyr_boot",
    "shell",
    "pfdi_agent",
    "pfdi_service",
]
SI_CL1_ISOLATED_SECONDARIES = [
    "cpu1_up",
    "cpu2_up",
    "cpu3_up",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def file_presence(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path.resolve()),
        "exists": exists,
        "size": path.stat().st_size if exists and path.is_file() else None,
    }


def final_bundle_contract(live_dir: Path, output_path: Path) -> dict[str, Any]:
    expected_output = live_dir / FINAL_OUTPUT_NAME
    output_is_canonical = output_path.resolve() == expected_output.resolve()
    required_files: dict[str, Any] = {}
    for filename in FINAL_EVIDENCE_BUNDLE:
        if filename == FINAL_OUTPUT_NAME:
            required_files[filename] = {
                "path": str(output_path.resolve()),
                "expected_path": str(expected_output.resolve()),
                "created_by_this_command": True,
                "output_is_canonical": output_is_canonical,
            }
        else:
            required_files[filename] = file_presence(live_dir / filename)
    return {
        "evidence_directory": str(live_dir.resolve()),
        "expected_final_output": str(expected_output.resolve()),
        "actual_output": str(output_path.resolve()),
        "output_is_canonical": output_is_canonical,
        "required_files": required_files,
    }


def all_marker_hits_pass(marker_groups: Any) -> bool:
    if not isinstance(marker_groups, dict) or not marker_groups:
        return False
    for markers in marker_groups.values():
        if not isinstance(markers, dict) or not markers:
            return False
        if not all(bool(value) for value in markers.values()):
            return False
    return True


def required_marker_groups_pass(marker_groups: Any) -> bool:
    if not isinstance(marker_groups, dict):
        return False
    for group in REQUIRED_MARKER_GROUPS:
        markers = marker_groups.get(group)
        if not isinstance(markers, dict) or not markers:
            return False
        if not all(bool(value) for value in markers.values()):
            return False
    return True


def log_files_present(result: dict[str, Any], names: list[str]) -> bool:
    logs = result.get("console_logs")
    if not isinstance(logs, dict):
        return False
    for name in names:
        path = Path(str(logs.get(name, "")))
        if not path.exists() or path.stat().st_size == 0:
            return False
    return True


def console_log_path(result: dict[str, Any], name: str) -> Path:
    logs = result.get("console_logs")
    if not isinstance(logs, dict):
        return Path("")
    return Path(str(logs.get(name, "")))


def read_log(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def ap_cpu_count(result: dict[str, Any]) -> int | None:
    observations = result.get("platform_observations")
    if isinstance(observations, dict) and isinstance(observations.get("ap_cpus"), int):
        return int(observations["ap_cpus"])
    platform_text = read_log(console_log_path(result, "platform"))
    match = AP_CPU_COUNT_RE.search(platform_text)
    return int(match.group("count")) if match else None


def ap_cpus_enabled(result: dict[str, Any]) -> bool:
    return ap_cpu_count(result) == EXPECTED_AP_CPUS


def secure_console_has_ap_bl2(result: dict[str, Any]) -> bool:
    observations = result.get("secure_console_observations")
    if isinstance(observations, dict) and observations.get("ap_bl2_console") is not None:
        return bool(observations.get("ap_bl2_console"))
    secure_text = read_log(console_log_path(result, "secure_console"))
    return "NOTICE:  BL2:" in secure_text


def secure_console_has_bl31(result: dict[str, Any]) -> bool:
    observations = result.get("secure_console_observations")
    if isinstance(observations, dict) and observations.get("bl31_console") is not None:
        return bool(observations.get("bl31_console"))
    secure_text = read_log(console_log_path(result, "secure_console"))
    return "NOTICE:  BL31:" in secure_text


def secure_console_has_optee(result: dict[str, Any]) -> bool:
    observations = result.get("secure_console_observations")
    if isinstance(observations, dict) and observations.get("optee_console") is not None:
        return bool(observations.get("optee_console"))
    secure_text = read_log(console_log_path(result, "secure_console"))
    return "OP-TEE version:" in secure_text


def primary_console_log_path(result: dict[str, Any]) -> Path:
    return console_log_path(result, "primary_console")


def primary_console_has_u_boot(result: dict[str, Any]) -> bool:
    observations = result.get("primary_console_observations")
    if isinstance(observations, dict) and observations.get("u_boot_console") is not None:
        return bool(observations.get("u_boot_console"))
    primary_text = read_log(primary_console_log_path(result))
    return "U-Boot " in primary_text


def gate_value(result: dict[str, Any], gate: str) -> str | None:
    gates = result.get("completion_gates")
    if not isinstance(gates, dict):
        return None
    value = gates.get(gate)
    return value if isinstance(value, str) else None


def choose_existing(root: Path, preferred: str, fallback: str | None = None) -> Path:
    preferred_path = root / preferred
    if preferred_path.exists() or fallback is None:
        return preferred_path
    fallback_path = root / fallback
    return fallback_path if fallback_path.exists() else preferred_path


def choose_result_dir(root: Path, preferred: str, fallback: str | None = None) -> Path:
    preferred_path = root / preferred
    if (preferred_path / "result.json").exists() or fallback is None:
        return preferred_path
    fallback_path = root / fallback
    if (fallback_path / "result.json").exists():
        return fallback_path
    return choose_existing(root, preferred, fallback)


def result_json_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    if path.name == "result.json":
        return path
    return path / "result.json"


def add_check(
    checks: list[dict[str, Any]],
    gate: str,
    name: str,
    passed: bool,
    *,
    path: Path | None = None,
    status: str | None = None,
    detail: str | None = None,
) -> None:
    entry: dict[str, Any] = {
        "gate": gate,
        "name": name,
        "passed": bool(passed),
    }
    if path is not None:
        entry["path"] = str(path.resolve())
    if status is not None:
        entry["status"] = status
    if detail is not None:
        entry["detail"] = detail
    checks.append(entry)


def verify_g0(checks: list[dict[str, Any]], check_dir: Path) -> str:
    result_path = check_dir / "result.json"
    map_path = check_dir / "map-validation.json"
    coverage_path = check_dir / "coverage-audit.json"
    result = read_json(result_path)
    map_result = read_json(map_path)
    coverage = read_json(coverage_path)
    expected_gates = all(
        gate_value(result, gate) == ("pass" if gate == "G0" else "not_run")
        for gate in GATES
    )
    add_check(checks, "G0", "check-only result exists", bool(result), path=result_path)
    add_check(checks, "G0", "check-only passed", bool(result.get("passed")), path=result_path)
    add_check(checks, "G0", "check-only gate contract", expected_gates, path=result_path)
    add_check(checks, "G0", "map validation passed", bool(map_result.get("passed")), path=map_path)
    add_check(
        checks,
        "G0",
        "coverage audit passed",
        bool(coverage.get("passed")),
        path=coverage_path,
    )
    return "pass" if all(check["passed"] for check in checks if check["gate"] == "G0") else "fail"


def verify_g1(checks: list[dict[str, Any]], direct_dir: Path) -> str:
    result_path = direct_dir / "result.json"
    result = read_json(result_path)
    log_path = Path(str(result.get("log_path", "")))
    add_check(checks, "G1", "direct boot result exists", bool(result), path=result_path)
    add_check(checks, "G1", "direct boot passed", bool(result.get("passed")), path=result_path)
    add_check(
        checks,
        "G1",
        "direct post-login probe completed",
        bool(result.get("post_login_probe") and result.get("probe_complete")),
        path=result_path,
    )
    add_check(
        checks,
        "G1",
        "direct boot log present",
        log_path.exists() and log_path.stat().st_size > 0,
        path=log_path,
    )
    return "pass" if all(check["passed"] for check in checks if check["gate"] == "G1") else "fail"


def verify_g2(checks: list[dict[str, Any]], service_dir: Path) -> str:
    result_path = service_dir / "result.json"
    comparison_path = service_dir / "comparison.json"
    result = read_json(result_path)
    comparison = read_json(comparison_path)
    add_check(checks, "G2", "service-model result exists", bool(result), path=result_path)
    add_check(checks, "G2", "service-model result passed", bool(result.get("passed")), path=result_path)
    add_check(
        checks,
        "G2",
        "service-model mode recorded",
        result.get("safety_island_mode") == "service-model",
        path=result_path,
    )
    add_check(
        checks,
        "G2",
        "service-model gate passed",
        gate_value(result, "G2") == "pass",
        path=result_path,
    )
    add_check(
        checks,
        "G2",
        "service-model marker groups passed",
        all_marker_hits_pass(result.get("marker_groups")),
        path=result_path,
    )
    add_check(
        checks,
        "G2",
        "service-model subsystem logs present",
        log_files_present(result, REQUIRED_FULL_LOGS),
        path=result_path,
    )
    add_check(
        checks,
        "G2",
        "service-model FVP comparison passed",
        bool(comparison.get("passed")),
        path=comparison_path,
    )
    return "pass" if all(check["passed"] for check in checks if check["gate"] == "G2") else "fail"


def verify_live_gate(
    checks: list[dict[str, Any]],
    gate: str,
    run_dir: Path,
    *,
    mode: str,
    accepted_blocker_prefixes: list[str],
    strict_final: bool,
) -> str:
    result_path = run_dir / "result.json"
    result = read_json(result_path)
    add_check(checks, gate, f"{mode} result exists", bool(result), path=result_path)
    if not result:
        return "fail"
    blocker = result.get("blocker")
    recorded_gate = gate_value(result, gate)
    add_check(
        checks,
        gate,
        f"{mode} mode recorded",
        result.get("safety_island_mode") == mode,
        path=result_path,
        status=str(result.get("safety_island_mode")),
    )
    if bool(result.get("passed")) and recorded_gate == "pass":
        add_check(checks, gate, f"{mode} gate passed", True, path=result_path)
        add_check(
            checks,
            gate,
            f"{mode} marker groups passed",
            all_marker_hits_pass(result.get("marker_groups")),
            path=result_path,
        )
        add_check(
            checks,
            gate,
            f"{mode} subsystem logs present",
            log_files_present(result, REQUIRED_FULL_LOGS),
            path=result_path,
        )
        if gate == "G4":
            add_check(
                checks,
                gate,
                "live-cl0-cl1 AP CPUs enabled",
                ap_cpus_enabled(result),
                path=console_log_path(result, "platform"),
                status=f"ap_cpus={ap_cpu_count(result)}",
            )
            add_check(
                checks,
                gate,
                "live-cl0-cl1 AP BL2 ran on secure console",
                secure_console_has_ap_bl2(result),
                path=console_log_path(result, "secure_console"),
            )
            add_check(
                checks,
                gate,
                "live-cl0-cl1 BL31 ran on secure console",
                secure_console_has_bl31(result),
                path=console_log_path(result, "secure_console"),
            )
            add_check(
                checks,
                gate,
                "live-cl0-cl1 OP-TEE ran on secure console",
                secure_console_has_optee(result),
                path=console_log_path(result, "secure_console"),
            )
            add_check(
                checks,
                gate,
                "live-cl0-cl1 U-Boot ran on primary console",
                primary_console_has_u_boot(result),
                path=primary_console_log_path(result),
            )
        return "pass" if all(check["passed"] for check in checks if check["gate"] == gate) else "fail"

    blocked = (
        recorded_gate == "blocked"
        and isinstance(blocker, str)
        and any(blocker.startswith(prefix) for prefix in accepted_blocker_prefixes)
    )
    add_check(
        checks,
        gate,
        f"{mode} blocked classification recorded",
        blocked,
        path=result_path,
        status=str(blocker),
    )
    if strict_final and blocked:
        add_check(
            checks,
            gate,
            f"{mode} must pass for strict final completion",
            False,
            path=result_path,
            status=str(blocker),
        )
    return "fail" if strict_final else ("blocked" if blocked else "fail")


def verify_g5(
    checks: list[dict[str, Any]],
    live_dir: Path,
    *,
    strict_final: bool,
) -> str:
    result_path = live_dir / "result.json"
    comparison_path = live_dir / "comparison.json"
    map_path = live_dir / "map-comparison.json"
    coverage_path = live_dir / "coverage-audit.json"
    result = read_json(result_path)
    comparison = read_json(comparison_path)
    map_result = read_json(map_path)
    coverage = read_json(coverage_path)
    runtime_gate_contract = (
        bool(result)
        and gate_value(result, "G0") == "pass"
        and gate_value(result, "G4") == "pass"
    )
    checks_to_add = [
        (
            "full live result passed in live-cl0-cl1 mode",
            bool(result.get("passed"))
            and result.get("verdict") == "pass"
            and result.get("safety_island_mode") == "live-cl0-cl1",
            result_path,
        ),
        (
            "full live result runtime gate contract",
            runtime_gate_contract,
            result_path,
        ),
        (
            "full live required marker groups passed",
            required_marker_groups_pass(result.get("marker_groups")),
            result_path,
        ),
        (
            "full live subsystem logs present",
            log_files_present(result, REQUIRED_FULL_LOGS),
            result_path,
        ),
        ("full live AP CPUs enabled", ap_cpus_enabled(result), console_log_path(result, "platform")),
        (
            "full live AP BL2 ran on secure console",
            secure_console_has_ap_bl2(result),
            console_log_path(result, "secure_console"),
        ),
        (
            "full live BL31 ran on secure console",
            secure_console_has_bl31(result),
            console_log_path(result, "secure_console"),
        ),
        (
            "full live OP-TEE ran on secure console",
            secure_console_has_optee(result),
            console_log_path(result, "secure_console"),
        ),
        (
            "full live U-Boot ran on primary console",
            primary_console_has_u_boot(result),
            primary_console_log_path(result),
        ),
        ("full live FVP comparison passed", bool(comparison.get("passed")), comparison_path),
        ("full live map comparison passed", bool(map_result.get("passed")), map_path),
        ("full live coverage audit passed", bool(coverage.get("passed")), coverage_path),
    ]
    for name, passed, path in checks_to_add:
        add_check(checks, "G5", name, passed, path=path)
    gate_checks = [check for check in checks if check["gate"] == "G5"]
    if all(check["passed"] for check in gate_checks):
        return "pass"
    return "fail" if strict_final else "not_run"


def verify_si_cl1_isolated(path: Path | None) -> dict[str, Any]:
    result_path = result_json_path(path)
    if result_path is None:
        return {
            "task": "QAP-FULL-020",
            "status": "not_configured",
            "counts_for_completion_gate": False,
            "detail": "Use --si-cl1-isolated-dir to attach isolated CL1 evidence.",
        }

    result = read_json(result_path)
    marker_groups = result.get("marker_groups")
    required = marker_groups.get("required", {}) if isinstance(marker_groups, dict) else {}
    optional = marker_groups.get("optional", {}) if isinstance(marker_groups, dict) else {}
    fail = marker_groups.get("fail", {}) if isinstance(marker_groups, dict) else {}
    checks = {
        "result_exists": bool(result),
        "task_matches": result.get("task") == "QAP-FULL-020",
        "passed": bool(result.get("passed")),
        "isolated_milestone_only": (
            result.get("completion_gate_effect") == "isolated_milestone_only"
        ),
        "required_markers": all(bool(required.get(name)) for name in SI_CL1_ISOLATED_REQUIRED),
        "secondary_cpu_markers": all(
            bool(optional.get(name)) for name in SI_CL1_ISOLATED_SECONDARIES
        ),
        "no_fail_patterns": not any(bool(value) for value in fail.values()),
    }
    return {
        "task": "QAP-FULL-020",
        "status": "pass" if all(checks.values()) else "fail",
        "counts_for_completion_gate": False,
        "path": str(result_path.resolve()),
        "completion_gate_effect": result.get("completion_gate_effect"),
        "checks": checks,
        "blocker": result.get("blocker"),
    }


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=root / "build/qbox-apollo-fvp",
    )
    parser.add_argument("--check-only-dir", default="full-check-only")
    parser.add_argument("--direct-dir", default="direct-guardrail")
    parser.add_argument("--service-model-dir")
    parser.add_argument("--live-cl1-dir", default="full-live-cl1")
    parser.add_argument("--live-cl0-cl1-dir", default="full-live-cl0-cl1")
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-apollo-fvp/full-completion-verification.json",
    )
    parser.add_argument(
        "--strict-final",
        action="store_true",
        help="Return success only when G0 through G5 are complete.",
    )
    parser.add_argument(
        "--si-cl1-isolated-dir",
        type=Path,
        help=(
            "Optional QAP-FULL-020 isolated CL1 evidence directory. "
            "This is reported as milestone evidence only and never counts "
            "toward final completion."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence_root = args.evidence_root.resolve()
    service_dir = (
        evidence_root / args.service_model_dir
        if args.service_model_dir
        else choose_result_dir(
            evidence_root,
            "full-service-model",
            "full-service-model-apollo-profile",
        )
    )
    dirs = {
        "G0": evidence_root / args.check_only_dir,
        "G1": evidence_root / args.direct_dir,
        "G2": service_dir,
        "G3": evidence_root / args.live_cl1_dir,
        "G4": evidence_root / args.live_cl0_cl1_dir,
        "G5": evidence_root / args.live_cl0_cl1_dir,
    }
    checks: list[dict[str, Any]] = []
    overall_gates = {
        "G0": verify_g0(checks, dirs["G0"]),
        "G1": verify_g1(checks, dirs["G1"]),
        "G2": verify_g2(checks, dirs["G2"]),
        "G3": verify_live_gate(
            checks,
            "G3",
            dirs["G3"],
            mode="live-cl1",
            accepted_blocker_prefixes=[
                "live_cl1_not_implemented:",
                "live_cl1_map_blocked:",
                "live_cl1_marker_blocked:",
                "live_cl1_hipc_rpmsg_blocked:",
                "qbox_platform_timeout",
                "qbox_post_login_probe_not_reached",
            ],
            strict_final=args.strict_final,
        ),
        "G4": verify_live_gate(
            checks,
            "G4",
            dirs["G4"],
            mode="live-cl0-cl1",
            accepted_blocker_prefixes=[
                "live_cl0_cl1_not_implemented:",
                "live_cl0_cl1_map_blocked:",
                "live_cl0_cl1_marker_blocked:",
                "live_cl0_cl1_hipc_rpmsg_blocked:",
                "qbox_platform_timeout",
                "qbox_post_login_probe_not_reached",
            ],
            strict_final=args.strict_final,
        ),
        "G5": verify_g5(checks, dirs["G5"], strict_final=args.strict_final),
    }
    final_bundle = final_bundle_contract(dirs["G5"], args.output)
    if args.strict_final:
        canonical_live_dir = (evidence_root / "full-live-cl0-cl1").resolve()
        final_run_is_canonical = dirs["G5"].resolve() == canonical_live_dir
        add_check(
            checks,
            "G5",
            "strict final live directory is canonical full-live-cl0-cl1",
            final_run_is_canonical,
            path=dirs["G5"],
            detail=f"expected {canonical_live_dir}",
        )
        if not final_run_is_canonical:
            overall_gates["G5"] = "fail"
        add_check(
            checks,
            "G5",
            "strict final output is canonical final-verification.json",
            bool(final_bundle["output_is_canonical"]),
            path=args.output,
            detail=f"expected {final_bundle['expected_final_output']}",
        )
        if not final_bundle["output_is_canonical"]:
            overall_gates["G5"] = "fail"
        for filename, record in final_bundle["required_files"].items():
            if filename == FINAL_OUTPUT_NAME:
                continue
            exists = bool(record.get("exists"))
            add_check(
                checks,
                "G5",
                f"strict final bundle contains {filename}",
                exists,
                path=Path(str(record.get("path", ""))),
            )
            if not exists:
                overall_gates["G5"] = "fail"

    gate_blockers = {
        str(check["gate"]): str(check["status"])
        for check in checks
        if check.get("passed")
        and isinstance(check.get("status"), str)
        and "blocked classification recorded" in str(check.get("name", ""))
    }
    first_incomplete_gate = next(
        (gate for gate in GATES if overall_gates.get(gate) != "pass"),
        None,
    )
    first_failed_check = next((check for check in checks if not check["passed"]), None)
    if first_incomplete_gate is None:
        completion_rejection_reason = None
    elif first_incomplete_gate in gate_blockers:
        completion_rejection_reason = gate_blockers[first_incomplete_gate]
    elif first_failed_check is not None:
        completion_rejection_reason = (
            f"{first_failed_check['gate']}:{first_failed_check['name']}"
        )
    else:
        completion_rejection_reason = (
            f"{first_incomplete_gate}:{overall_gates[first_incomplete_gate]}"
        )

    final_complete = all(overall_gates.get(gate) == "pass" for gate in GATES)
    completion_claim_allowed = bool(args.strict_final and final_complete)
    current_progress_ok = all(
        overall_gates.get(gate) == "pass" for gate in ["G0", "G1", "G2"]
    ) and overall_gates.get("G3") in {"blocked", "pass"}
    if args.strict_final:
        verdict = "pass" if final_complete else "fail"
    else:
        verdict = "pass" if final_complete else ("blocked" if current_progress_ok else "fail")
    result = {
        "goal_definition": GOAL_DEFINITION,
        "completion_policy": COMPLETION_POLICY,
        "goal_verification_plan": GOAL_VERIFICATION_PLAN,
        "passed": final_complete if args.strict_final else current_progress_ok,
        "strict_final": args.strict_final,
        "verdict": verdict,
        "completion_ready": final_complete,
        "completion_claim_allowed": completion_claim_allowed,
        "first_incomplete_gate": first_incomplete_gate,
        "gate_blockers": gate_blockers,
        "first_blocker": completion_rejection_reason,
        "completion_rejection_reason": completion_rejection_reason,
        "first_failed_check": first_failed_check,
        "completion_levels": COMPLETION_LEVELS,
        "milestone_evidence": {
            "QAP-FULL-020": verify_si_cl1_isolated(args.si_cl1_isolated_dir),
        },
        "final_acceptance_artifacts": FINAL_ACCEPTANCE_ARTIFACTS,
        "final_bundle_contract": final_bundle,
        "review_rules": REVIEW_RULES,
        "overall_gates": overall_gates,
        "evidence_directories": {gate: str(path.resolve()) for gate, path in dirs.items()},
        "checks": checks,
        "required_final_result": {
            "verdict": "pass",
            "safety_island_mode": "live-cl0-cl1",
            "completion_gates": {"G0": "pass", "G4": "pass"},
            "sidecar_gates": {
                "comparison.json": "pass",
                "map-comparison.json": "pass",
                "coverage-audit.json": "pass",
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    print(f"verdict: {result['verdict']}")
    print("overall_gates:")
    for gate in GATES:
        print(f"  {gate}: {overall_gates[gate]}")
    if args.strict_final and not final_complete:
        for check in checks:
            if not check["passed"]:
                print(
                    f"FAIL {check['gate']} {check['name']}: "
                    f"{check.get('status', check.get('path', ''))}",
                    file=sys.stderr,
                )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

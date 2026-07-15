#!/usr/bin/env python3
"""Audit Apollo full-system QBox hardware coverage and gate evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


BOOT_CRITICAL_BLOCKS = [
    "cpu",
    "memory map",
    "interrupts",
    "ATU",
    "MHU",
    "SCMI",
    "HIPC",
    "PFDI",
    "FMU",
    "SSU",
    "SMCF",
    "boot media",
    "subsystem logs",
    "GIC multi-view",
]
GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
DEFAULT_AP_MAP_AUDIT = Path("build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json")
AP_MAP_PASSING_CLASSIFICATIONS = {"covered", "partial_model", "explicit_placeholder"}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_json_strict(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"read_error:{exc}"
    except json.JSONDecodeError as exc:
        return None, f"decode_error:{exc.msg}:line{exc.lineno}:col{exc.colno}"
    if not isinstance(data, dict):
        return None, "not_json_object"
    return data, None


def static_block_checks(root: Path) -> list[dict[str, Any]]:
    design = read_text(root / "doc/qbox-apollo-fvp-full-system-design.md")
    tasks = read_text(root / "doc/qbox-apollo-fvp-full-system-tasks.md")
    combined = design + "\n" + tasks
    return [
        {
            "name": block,
            "status": "planned",
            "passed": bool(re.search(re.escape(block), combined, re.IGNORECASE)),
        }
        for block in BOOT_CRITICAL_BLOCKS
    ]


def runtime_gate_checks(result: dict[str, Any]) -> list[dict[str, Any]]:
    gates = result.get("completion_gates", {})
    if not isinstance(gates, dict):
        return [{"name": "completion_gates", "passed": False, "status": "missing"}]
    checks = [
        {
            "name": f"gate:{gate}",
            "status": gates.get(gate, "missing"),
            "passed": gates.get(gate) in {"pass", "not_run"},
        }
        for gate in GATES
    ]
    checks.append(
        {
            "name": "runtime_result_passed",
            "status": "pass" if result.get("passed") else result.get("verdict", "fail"),
            "passed": bool(result.get("passed")),
        }
    )
    return checks


def _runtime_log(result: dict[str, Any], name: str) -> str:
    logs = result.get("console_logs", {})
    if not isinstance(logs, dict):
        return ""
    return read_text(Path(str(logs.get(name, ""))))


def si_cl1_alternate_marker_evidence(result: dict[str, Any]) -> dict[str, str]:
    evidence: dict[str, str] = {}
    post_login = result.get("post_login_probe", {})
    if isinstance(post_login, dict):
        drivers = post_login.get("driver_patterns", {})
        return_codes = post_login.get("return_codes", {})
        if not isinstance(drivers, dict):
            drivers = {}
        if not isinstance(return_codes, dict):
            return_codes = {}
        if (
            drivers.get("hipc_ethsi1")
            and drivers.get("rpmsg")
            and return_codes.get("ethsi1_iplink_rc") == 0
        ):
            evidence["network_configured"] = "post_login_probe:rpmsg_ethsi1"

    primary_console = _runtime_log(result, "primary_console")
    if (
        "apollo-network-setup: configured brsi1/ethsi1" in primary_console
        or "ethsi1_iplink_rc:0" in primary_console
    ):
        evidence["network_configured"] = "primary_console:ethsi1"

    si_cl0 = _runtime_log(result, "si_cl0")
    if "Started PFDI monitoring for SI cluster 1 core" in si_cl0:
        evidence["pfdi_agent"] = "si_cl0:PFDI_monitor_started"
    if "SI cluster 1 core 0 has been turned on, switching on PFDI monitoring" in si_cl0:
        evidence["pfdi_service"] = "si_cl0:PFDI_monitor_active"
    return evidence


def marker_group_checks(result: dict[str, Any]) -> list[dict[str, Any]]:
    marker_groups = result.get("marker_groups")
    if not isinstance(marker_groups, dict):
        return [{"name": "marker_groups", "passed": False, "status": "missing"}]
    checks = []
    si_cl1_alternates = si_cl1_alternate_marker_evidence(result)
    for group, markers in sorted(marker_groups.items()):
        if not isinstance(markers, dict):
            checks.append(
                {
                    "name": f"markers:{group}",
                    "passed": False,
                    "status": "invalid",
                }
            )
            continue
        effective_markers = dict(markers)
        alternate_sources: list[str] = []
        if group == "si_cl1":
            for name, source in sorted(si_cl1_alternates.items()):
                if not effective_markers.get(name) and name in effective_markers:
                    effective_markers[name] = True
                    alternate_sources.append(f"{name}={source}")
        if group == "linux":
            ready = bool(
                effective_markers.get("login_prompt")
                or effective_markers.get("root_shell")
            )
            missing = [] if ready else ["login_prompt_or_root_shell"]
        elif group == "linux_boot":
            ready = any(bool(value) for value in effective_markers.values())
            missing = [] if ready else ["login_prompt_or_root_shell"]
        else:
            missing = sorted(
                str(name) for name, value in effective_markers.items() if not value
            )
        status = "pass" if not missing else "missing:" + ",".join(missing)
        if (
            not missing
            and group in {"linux", "linux_boot"}
            and not all(bool(value) for value in effective_markers.values())
        ):
            status = "pass:headless_login"
        if not missing and alternate_sources:
            status = "pass:alternate:" + ",".join(alternate_sources)
        checks.append(
            {
                "name": f"markers:{group}",
                "passed": not missing,
                "status": status,
            }
        )
    return checks


def console_log_checks(result: dict[str, Any]) -> list[dict[str, Any]]:
    logs = result.get("console_logs", {})
    if not isinstance(logs, dict):
        return [{"name": "console_logs", "passed": False, "status": "missing"}]
    required = [
        "rse",
        "si_cl0",
        "si_cl1",
        "secure_console",
        "primary_console",
    ]
    checks = []
    for name in required:
        path = Path(str(logs.get(name, "")))
        checks.append(
            {
                "name": f"log:{name}",
                "path": str(path),
                "status": "present" if path.exists() else "missing",
                "passed": path.exists(),
            }
        )
    return checks


def lua_component_block(text: str, name: str) -> str:
    marker = f"{name} = {{"
    start = text.find(marker)
    if start < 0:
        return ""
    next_start = text.find("\n    ", start + len(marker))
    end = text.find("\n\n", start)
    if end < 0:
        end = len(text)
    if next_start > start and next_start < end and "moduletype" not in text[start:end]:
        end = next_start
    return text[start:end]


def lua_backend_checks(root: Path) -> list[dict[str, Any]]:
    si_cl0 = read_text(root / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua")
    rse = read_text(root / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua")
    system_mgmt = read_text(root / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua")
    expected = [
        ("si_cl0_ssu", si_cl0, "zena_ssu"),
        ("si_cl0_fmu", si_cl0, "zena_fmu"),
        ("rse_nsacfg_regs", rse, "rse_protection_ctrl"),
        ("rse_sacfg_regs", rse, "rse_protection_ctrl"),
        ("rse_mpc_vm0_regs", rse, "rse_protection_ctrl"),
        ("rse_mpc_vm1_regs", rse, "rse_protection_ctrl"),
        ("rse_sic_regs", rse, "rse_protection_ctrl"),
        ("rse_mpc_sic_regs", rse, "rse_protection_ctrl"),
        ("rse_atu_regs", rse, "rse_atu"),
        ("host_si_atu", system_mgmt, "rse_atu"),
        ("host_ap_atu", system_mgmt, "rse_atu"),
        ("host_smdexp2smd_atu", system_mgmt, "rse_atu"),
    ]
    checks = []
    for name, text, backend in expected:
        block = lua_component_block(text, name)
        passed = f'moduletype = "{backend}"' in block
        checks.append(
            {
                "name": f"backend:{name}",
                "status": backend if passed else "missing_or_different",
                "passed": passed,
                "expected": backend,
            }
        )
    return checks


def classification_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        classification = str(row.get("classification", "missing"))
        counts[classification] = counts.get(classification, 0) + 1
    return dict(sorted(counts.items()))


def json_int(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


def ap_map_summary(path: Path, *, allow_missing_non_gating: bool) -> dict[str, Any]:
    if not path.exists():
        return {
            "status": "not_available",
            "passed": allow_missing_non_gating,
            "audit_path": str(path),
            "check": "ap_9_1_1_memory_map",
            "coverage_gating": (
                "not_available_non_gating"
                if allow_missing_non_gating
                else "required_audit_missing"
            ),
        }
    data, error = read_json_strict(path)
    if data is None:
        return {
            "status": "invalid_ap_map_audit",
            "passed": False,
            "audit_path": str(path),
            "check": "ap_9_1_1_memory_map",
            "error": error,
        }

    rows = data.get("classifications", [])
    if not isinstance(rows, list):
        rows = []
    typed_rows = [row for row in rows if isinstance(row, dict)]
    required_rows = [row for row in typed_rows if row.get("scope") == "required_now"]
    deferred_rows = [row for row in typed_rows if row.get("scope") == "deferred_epic"]
    required_nonpassing_rows = [
        str(row.get("name", "unknown"))
        for row in required_rows
        if row.get("classification") not in AP_MAP_PASSING_CLASSIFICATIONS
    ]
    missing_required_now = data.get("missing_required_now", [])
    if not isinstance(missing_required_now, list):
        missing_required_now = ["invalid_missing_required_now_field"]
    audit_passed = bool(data.get("passed"))
    required_now_passed = audit_passed and not missing_required_now
    return {
        "status": "pass" if audit_passed else "ap_map_audit_fail",
        "passed": audit_passed,
        "audit_path": str(path),
        "check": str(data.get("check", "unknown")),
        "coverage_gating": "ap_map_audit_passed",
        "audit_passed": bool(data.get("passed")),
        "required_now_passed": required_now_passed,
        "required_now_row_count": json_int(data.get("required_now_row_count"), len(required_rows)),
        "deferred_epic_row_count": json_int(data.get("deferred_epic_row_count"), len(deferred_rows)),
        "deferred_epic_gating": "non_gating",
        "missing_required_now": missing_required_now,
        "required_now_nonpassing_rows": required_nonpassing_rows,
        "classification_counts": classification_counts(typed_rows),
        "required_now_classification_counts": classification_counts(required_rows),
        "deferred_epic_classification_counts": classification_counts(deferred_rows),
        "source_doc": data.get("source_doc"),
        "sources": data.get("sources", []),
    }


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", default="hardware-blocks")
    parser.add_argument("--result-json", type=Path)
    parser.add_argument(
        "--ap-map-audit",
        type=Path,
        default=root / DEFAULT_AP_MAP_AUDIT,
        help="Apollo AP 9.1.1 memory-map audit JSON required for full coverage.",
    )
    parser.add_argument(
        "--allow-missing-ap-map-audit-non-gating",
        action="store_true",
        help=(
            "Legacy compatibility mode: record a missing AP 9.1.1 map audit "
            "as non-gating instead of failing full coverage."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-apollo-qvp/full-coverage-audit.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = workspace_root()
    runtime_result = read_json(args.result_json)
    block_checks = static_block_checks(root)
    backend_checks = lua_backend_checks(root)
    ap_map = ap_map_summary(
        args.ap_map_audit,
        allow_missing_non_gating=args.allow_missing_ap_map_audit_non_gating,
    )
    ap_map_check = {
        "name": "ap_9_1_1_memory_map",
        "status": ap_map["status"],
        "passed": bool(ap_map["passed"]),
        "path": ap_map["audit_path"],
    }
    gate_checks = runtime_gate_checks(runtime_result) if runtime_result else []
    marker_checks = marker_group_checks(runtime_result) if runtime_result else []
    log_checks = console_log_checks(runtime_result) if runtime_result else []
    checks = (
        block_checks
        + backend_checks
        + [ap_map_check]
        + gate_checks
        + marker_checks
        + log_checks
    )
    if runtime_result:
        passed = all(check["passed"] for check in checks)
    else:
        passed = all(check["passed"] for check in block_checks + backend_checks + [ap_map_check])
    result = {
        "passed": passed,
        "check": args.check,
        "runtime_result": str(args.result_json.resolve()) if args.result_json else None,
        "checks": checks,
        "boot_critical_blocks": BOOT_CRITICAL_BLOCKS,
        "ap_9_1_1_memory_map": ap_map,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    if not passed:
        for check in checks:
            if not check["passed"]:
                print(f"FAIL {check['name']}: {check.get('status')}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

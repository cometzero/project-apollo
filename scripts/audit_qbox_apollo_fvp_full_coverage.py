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


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


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


def marker_group_checks(result: dict[str, Any]) -> list[dict[str, Any]]:
    marker_groups = result.get("marker_groups")
    if not isinstance(marker_groups, dict):
        return [{"name": "marker_groups", "passed": False, "status": "missing"}]
    checks = []
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
        missing = sorted(str(name) for name, value in markers.items() if not value)
        checks.append(
            {
                "name": f"markers:{group}",
                "passed": not missing,
                "status": "pass" if not missing else "missing:" + ",".join(missing),
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
    si_cl0 = read_text(root / "tools/qbox/platforms/apollo/hw-block/si_cl0.lua")
    rse = read_text(root / "tools/qbox/platforms/apollo/hw-block/rse.lua")
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
        ("host_si_atu", rse, "rse_atu"),
        ("host_ap_atu", rse, "rse_atu"),
        ("host_smdexp2smd_atu", rse, "rse_atu"),
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


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", default="hardware-blocks")
    parser.add_argument("--result-json", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-apollo-fvp/full-coverage-audit.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = workspace_root()
    runtime_result = read_json(args.result_json)
    block_checks = static_block_checks(root)
    backend_checks = lua_backend_checks(root)
    gate_checks = runtime_gate_checks(runtime_result) if runtime_result else []
    marker_checks = marker_group_checks(runtime_result) if runtime_result else []
    log_checks = console_log_checks(runtime_result) if runtime_result else []
    checks = block_checks + backend_checks + gate_checks + marker_checks + log_checks
    if runtime_result:
        passed = all(check["passed"] for check in checks)
    else:
        passed = all(check["passed"] for check in block_checks + backend_checks)
    result = {
        "passed": passed,
        "check": args.check,
        "runtime_result": str(args.result_json.resolve()) if args.result_json else None,
        "checks": checks,
        "boot_critical_blocks": BOOT_CRITICAL_BLOCKS,
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

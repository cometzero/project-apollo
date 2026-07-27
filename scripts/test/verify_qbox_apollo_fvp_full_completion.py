#!/usr/bin/env python3
"""Verify the canonical Apollo QBox full-system evidence bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


GATES = ("G0", "G1", "G2", "G3")
REQUIRED_LOGS = ("rse", "si_cl0", "si_cl1", "secure_console", "primary_console")
REQUIRED_MARKER_GROUPS = (
    "rse", "si_cl0", "si_cl1", "ap_firmware", "linux", "post_login",
    "maps_and_interrupts",
)
FINAL_SIDECARS = ("result.json", "comparison.json", "map-comparison.json", "coverage-audit.json")
LINUX_CPU_ONLINE_RE = re.compile(r"^online=(?P<online>\S+)\s*$", re.MULTILINE)
LINUX_CPUINFO_RE = re.compile(r"^cpuinfo_processors=(?P<count>\d+)\s*$", re.MULTILINE)


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_log(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def add_check(checks: list[dict[str, Any]], gate: str, name: str, passed: bool,
              *, path: Path, status: str | None = None) -> None:
    check: dict[str, Any] = {
        "gate": gate,
        "name": name,
        "passed": passed,
        "path": str(path),
    }
    if status is not None:
        check["status"] = status
    checks.append(check)


def gate_value(result: dict[str, Any], gate: str) -> str:
    gates = result.get("completion_gates")
    if not isinstance(gates, dict):
        return "missing"
    return str(gates.get(gate, "missing"))


def marker_groups_pass(result: dict[str, Any], groups: tuple[str, ...]) -> bool:
    marker_groups = result.get("marker_groups")
    if not isinstance(marker_groups, dict):
        return False
    for group in groups:
        markers = marker_groups.get(group)
        if not isinstance(markers, dict) or not markers:
            return False
        if not all(bool(value) for value in markers.values()):
            return False
    return True


def console_log_path(result: dict[str, Any], name: str) -> Path:
    logs = result.get("console_logs")
    if not isinstance(logs, dict):
        return Path()
    return Path(str(logs.get(name, "")))


def logs_present(result: dict[str, Any], names: tuple[str, ...]) -> bool:
    return all(console_log_path(result, name).is_file() for name in names)


def configured_cpu_count(result: dict[str, Any]) -> tuple[int | None, int | None]:
    observations = result.get("platform_observations")
    if not isinstance(observations, dict):
        return None, None
    actual = observations.get("ap_cpus")
    expected = observations.get("expected_ap_cpus")
    if not isinstance(actual, int) or not isinstance(expected, int):
        return None, None
    return actual, expected


def linux_cpu_topology(result: dict[str, Any]) -> tuple[bool, str]:
    actual, expected = configured_cpu_count(result)
    text = read_log(console_log_path(result, "primary_console"))
    online_match = LINUX_CPU_ONLINE_RE.search(text)
    cpuinfo_match = LINUX_CPUINFO_RE.search(text)
    online = online_match.group("online") if online_match else "missing"
    cpuinfo = int(cpuinfo_match.group("count")) if cpuinfo_match else None
    expected_online = "missing" if expected is None else (
        "0" if expected == 1 else f"0-{expected - 1}"
    )
    passed = (
        actual is not None
        and expected is not None
        and actual == expected
        and online == expected_online
        and cpuinfo == expected
    )
    status = f"ap_cpus={actual} expected={expected} online={online} cpuinfo_processors={cpuinfo}"
    return passed, status


def verify_g0(checks: list[dict[str, Any]], check_dir: Path) -> str:
    result_path = check_dir / "result.json"
    result = read_json(result_path)
    candidates = (
        ("check-only result passed", bool(result.get("passed")), result_path),
        ("check-only gate contract", gate_value(result, "G0") == "pass", result_path),
        ("static map validation passed",
         bool(read_json(check_dir / "map-validation.json").get("passed")),
         check_dir / "map-validation.json"),
        ("static coverage audit passed",
         bool(read_json(check_dir / "coverage-audit.json").get("passed")),
         check_dir / "coverage-audit.json"),
    )
    for name, passed, path in candidates:
        add_check(checks, "G0", name, passed, path=path)
    return "pass" if all(passed for _, passed, _ in candidates) else "fail"


def verify_g1(checks: list[dict[str, Any]], full_dir: Path) -> str:
    path = full_dir / "result.json"
    result = read_json(path)
    probe = result.get("post_login_probe")
    candidates = (
        ("full-system result passed", bool(result.get("passed")), path),
        ("full-system topology recorded",
         result.get("safety_island_topology") == "full-system", path),
        ("full-system AP gate passed", gate_value(result, "G1") == "pass", path),
        ("full-system AP marker groups passed",
         marker_groups_pass(result, ("ap_firmware", "linux", "post_login")), path),
        ("full-system AP post-login probe passed",
         isinstance(probe, dict) and bool(probe.get("requested"))
         and bool(probe.get("passed")), path),
        ("full-system AP logs present",
         logs_present(result, ("secure_console", "primary_console")), path),
    )
    for name, passed, source in candidates:
        add_check(checks, "G1", name, passed, path=source)
    return "pass" if all(passed for _, passed, _ in candidates) else "fail"


def verify_g2(checks: list[dict[str, Any]], full_dir: Path) -> str:
    path = full_dir / "result.json"
    result = read_json(path)
    actual, expected = configured_cpu_count(result)
    linux_ok, linux_status = linux_cpu_topology(result)
    secure = result.get("secure_console_observations")
    primary = result.get("primary_console_observations")
    candidates = (
        ("full-system runtime gate passed", gate_value(result, "G2") == "pass", None),
        ("full-system required marker groups passed",
         marker_groups_pass(result, REQUIRED_MARKER_GROUPS), None),
        ("full-system subsystem logs present", logs_present(result, REQUIRED_LOGS), None),
        ("full-system AP CPU topology", actual is not None and actual == expected,
         f"ap_cpus={actual}"),
        ("full-system Linux CPU topology", linux_ok, linux_status),
        ("full-system secure firmware observed",
         isinstance(secure, dict) and all(
             bool(secure.get(name))
             for name in ("ap_bl2_console", "bl31_console", "optee_console")
         ), None),
        ("full-system U-Boot observed",
         isinstance(primary, dict) and bool(primary.get("u_boot_console")), None),
    )
    for name, passed, status in candidates:
        add_check(checks, "G2", name, passed, path=path, status=status)
    return "pass" if all(passed for _, passed, _ in candidates) else "fail"


def verify_g3(checks: list[dict[str, Any]], full_dir: Path, output: Path,
              *, strict_final: bool) -> str:
    candidates = [
        (
            f"full-system bundle contains {name}",
            bool(read_json(full_dir / name).get("passed")),
            full_dir / name,
        )
        for name in FINAL_SIDECARS[1:]
    ]
    if strict_final:
        candidates.append((
            "strict final output is canonical",
            output.resolve() == (full_dir / "final-verification.json").resolve(),
            output,
        ))
    for name, passed, path in candidates:
        add_check(checks, "G3", name, passed, path=path)
    return "pass" if all(passed for _, passed, _ in candidates) else "fail"


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path,
                        default=root / "build/qbox-apollo-fvp")
    parser.add_argument("--check-only-dir", default="full-check-only")
    parser.add_argument("--full-system-dir", default="full-system")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict-final", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence_root = args.evidence_root.resolve()
    check_dir = evidence_root / args.check_only_dir
    full_dir = evidence_root / args.full_system_dir
    output = args.output.resolve() if args.output is not None else (
        full_dir / "final-verification.json"
    ).resolve()
    checks: list[dict[str, Any]] = []
    overall = {
        "G0": verify_g0(checks, check_dir),
        "G1": verify_g1(checks, full_dir),
        "G2": verify_g2(checks, full_dir),
        "G3": verify_g3(checks, full_dir, output, strict_final=args.strict_final),
    }
    complete = all(overall[gate] == "pass" for gate in GATES)
    status = {
        "verdict": "pass" if complete else "fail",
        "completion_ready": complete,
        "completion_claim_allowed": bool(args.strict_final and complete),
        "strict_final": bool(args.strict_final),
        "overall_gates": overall,
        "checks": checks,
        "evidence_root": str(evidence_root),
        "full_system_dir": str(full_dir),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(output)
    print(f"verdict: {status['verdict']}")
    for gate in GATES:
        print(f"  {gate}: {overall[gate]}")
    for check in checks:
        if not check["passed"]:
            print(
                f"FAIL {check['gate']} {check['name']}: "
                f"{check.get('status', check['path'])}",
                file=sys.stderr,
            )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())

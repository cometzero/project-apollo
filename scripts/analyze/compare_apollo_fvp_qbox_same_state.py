#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


FVP_DOMAIN_MARKERS = (
    "rse",
    "safety_island_cl0",
    "safety_island_cl1",
    "tf_a",
    "u_boot_linux",
)
QBOX_DOMAIN_MARKERS = ("rse", "si_cl0", "si_cl1", "ap_firmware", "linux")
DOMAIN_NAMES = ("rse", "si_cl0", "si_cl1", "secure", "primary")
CANONICAL_MARKERS = (
    "rse_bl1_1",
    "rse_scp_power_on_ap",
    "measured_boot_bl33",
    "primary_linux_cpu",
)
STRICT_STATE_ARTIFACTS = {
    "rse_rom",
    "rse_flash",
    "rse_otp",
    "ap_flash",
    "rootfs",
    "provisioning_bundle",
}
DRIVER_PATTERNS = {
    "smmu_v3": re.compile(r"arm-smmu-v3", re.IGNORECASE),
    "gic_its": re.compile(r"ITS \[mem ", re.IGNORECASE),
    "pfdi_4cpu": re.compile(
        r"CPU0: Out of Reset \(OoR\) test OK.*"
        r"CPU1: Out of Reset \(OoR\) test OK.*"
        r"CPU2: Out of Reset \(OoR\) test OK.*"
        r"CPU3: Out of Reset \(OoR\) test OK",
        re.IGNORECASE | re.DOTALL,
    ),
}
FAILED_UNITS_RE = re.compile(r"failed_units_count:(\d+)")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def qbox_artifact_state(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = result.get("input_artifacts", {})
    if not isinstance(records, dict):
        return {}
    state: dict[str, dict[str, Any]] = {}
    for name, record in records.items():
        if not isinstance(record, dict) or record.get("exists") is not True:
            continue
        path_text = record.get("path")
        if not isinstance(path_text, str):
            continue
        path = Path(path_text)
        if path.is_file():
            state[str(name)] = {
                "path": str(path.resolve()),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
    return state


def all_true(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(bool(item) for item in value.values())


def fvp_console_text(result: dict[str, Any]) -> str:
    status = result.get("status", {})
    consoles = status.get("consoles", {}) if isinstance(status, dict) else {}
    paths = [
        Path(str(record.get("path", "")))
        for record in consoles.values()
        if isinstance(record, dict)
    ]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in paths
        if path.is_file()
    )


def qbox_console_text(result: dict[str, Any]) -> str:
    logs = result.get("console_logs", {})
    if not isinstance(logs, dict):
        return ""
    paths = [Path(str(path)) for path in logs.values()]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in paths
        if path.is_file()
    )


def marker_checks(
    fvp_result: dict[str, Any], qbox_result: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    fvp_hits = fvp_result.get("progress_marker_first_hits", {})
    qbox_hits = qbox_result.get("progress_marker_first_hits", {})
    if not isinstance(fvp_hits, dict):
        fvp_hits = {}
    if not isinstance(qbox_hits, dict):
        qbox_hits = {}
    return {
        name: {
            "fvp_elapsed_s": (fvp_hits.get(name) or {}).get("elapsed_s"),
            "qbox_elapsed_s": (qbox_hits.get(name) or {}).get("elapsed_s"),
            "passed": name in fvp_hits and name in qbox_hits,
        }
        for name in CANONICAL_MARKERS
    }


def compare(
    fvp_result_path: Path,
    qbox_result_path: Path,
    map_validation_path: Path,
) -> dict[str, Any]:
    fvp_result = read_json(fvp_result_path)
    qbox_result = read_json(qbox_result_path)
    map_validation = read_json(map_validation_path)
    fvp_state = fvp_result.get("initial_state", {})
    if not isinstance(fvp_state, dict):
        fvp_state = {}
    qbox_manifest_path = qbox_result_path.parent / "initial-state.json"
    qbox_state = (
        read_json(qbox_manifest_path)
        if qbox_manifest_path.is_file()
        else qbox_artifact_state(qbox_result)
    )
    common_names = sorted(
        STRICT_STATE_ARTIFACTS & set(fvp_state) & set(qbox_state)
    )
    artifact_state = {
        name: {
            "fvp": fvp_state[name],
            "qbox": qbox_state[name],
            "matched": fvp_state[name].get("sha256")
            == qbox_state[name].get("sha256"),
        }
        for name in common_names
    }

    fvp_domains = fvp_result.get("domains", {})
    qbox_groups = qbox_result.get("marker_groups", {})
    if not isinstance(fvp_domains, dict):
        fvp_domains = {}
    if not isinstance(qbox_groups, dict):
        qbox_groups = {}
    domains = {}
    for name, fvp_key, qbox_key in zip(
        DOMAIN_NAMES, FVP_DOMAIN_MARKERS, QBOX_DOMAIN_MARKERS
    ):
        fvp_passed = bool((fvp_domains.get(fvp_key) or {}).get("passed"))
        qbox_passed = all_true(qbox_groups.get(qbox_key))
        domains[name] = {
            "fvp_passed": fvp_passed,
            "qbox_passed": qbox_passed,
            "passed": fvp_passed and qbox_passed,
        }

    fvp_text = fvp_console_text(fvp_result)
    qbox_text = qbox_console_text(qbox_result)
    drivers = {}
    for name, pattern in DRIVER_PATTERNS.items():
        fvp_seen = bool(pattern.search(fvp_text))
        qbox_seen = bool(pattern.search(qbox_text))
        drivers[name] = {
            "fvp_seen": fvp_seen,
            "qbox_seen": qbox_seen,
            "passed": fvp_seen and qbox_seen,
        }

    fvp_failed = FAILED_UNITS_RE.search(fvp_text)
    qbox_failed = FAILED_UNITS_RE.search(qbox_text)
    failed_services = {
        "fvp_count": int(fvp_failed.group(1)) if fvp_failed else None,
        "qbox_count": int(qbox_failed.group(1)) if qbox_failed else None,
    }
    failed_services["passed"] = (
        fvp_failed is not None
        and qbox_failed is not None
        and failed_services["fvp_count"] == failed_services["qbox_count"] == 0
    )

    markers = marker_checks(fvp_result, qbox_result)
    rse_state = qbox_result.get("rse_flash_state", {})
    qbox_fresh_state = isinstance(rse_state, dict) and rse_state.get("action") in {
        "ephemeral",
        "initialized",
    }
    checks = {
        "runtime_results": bool(fvp_result.get("passed") and qbox_result.get("passed")),
        "common_artifacts_present": bool(common_names),
        "artifact_hashes": bool(artifact_state)
        and all(record["matched"] for record in artifact_state.values()),
        "qbox_fresh_state": qbox_fresh_state,
        "domains": all(record["passed"] for record in domains.values()),
        "canonical_markers": all(record["passed"] for record in markers.values()),
        "memory_map_contract": bool(map_validation.get("passed")),
        "drivers_and_irqs": all(record["passed"] for record in drivers.values()),
        "failed_services": bool(failed_services["passed"]),
    }
    return {
        "schema_version": 1,
        "passed": all(checks.values()),
        "fvp_result": str(fvp_result_path.resolve()),
        "qbox_result": str(qbox_result_path.resolve()),
        "qbox_initial_state": str(qbox_manifest_path.resolve())
        if qbox_manifest_path.is_file()
        else None,
        "map_validation": str(map_validation_path.resolve()),
        "checks": checks,
        "artifact_state": artifact_state,
        "qbox_rse_flash_state": rse_state,
        "domains": domains,
        "canonical_markers": markers,
        "drivers": drivers,
        "failed_services": failed_services,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fvp-result", type=Path, required=True)
    parser.add_argument("--qbox-result", type=Path, required=True)
    parser.add_argument("--map-validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = compare(args.fvp_result, args.qbox_result, args.map_validation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output)
    if not result["passed"]:
        for name, passed in result["checks"].items():
            if not passed:
                print(f"FAIL {name}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

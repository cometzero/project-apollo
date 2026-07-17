#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY_VALIDATOR = ROOT / "scripts/test/validate_qbox_apollo_topology.py"
DEFAULT_TOPOLOGY_DIR = ROOT / "build/qbox-apollo-qvp/topology"
DEFAULT_OUTPUT = ROOT / "build/qbox-apollo-qvp/fidelity-contract-4cpu.json"

BOOT_SEQUENCE = (
    "rse_bl1_start",
    "rse_auth_images",
    "rse_program_atu_apu",
    "rse_release_si_cl0",
    "si_cl0_verify_rse_config",
    "si_cl0_init_system",
    "rse_scp_boot_confirm",
    "rse_release_ap_primary",
    "tfa_release_ap_secondary",
)

FIDELITY_LEDGER = (
    ("I0", "4cpu-contract", "complete"),
    ("I1", "request-context", "complete"),
    ("I2", "ni710ae-apu", "complete"),
    ("I3", "mmu720ae-smmuv3", "complete"),
    ("I4", "gpex-msi-its-lpi", "complete"),
    ("I5", "fault-safety-watchdog", "complete"),
    ("I6", "software-abi-recovery", "complete"),
    ("I7", "local-yocto-fvp-validation", "complete"),
    ("I8", "architecture-closeout", "complete"),
)

STAGE_EVIDENCE = {
    "I0": "build/qbox-apollo-qvp/fidelity-contract-4cpu.json",
    "I1": (
        "doc/apollo-qvp-fidelity-stages/"
        "i1-request-context-completion-2026-07-16-ko.md"
    ),
    "I2": (
        "doc/apollo-qvp-fidelity-stages/"
        "i2-ni710ae-apu-completion-2026-07-16-ko.md"
    ),
    "I3": (
        "doc/apollo-qvp-fidelity-stages/"
        "i3-mmu720ae-smmuv3-completion-2026-07-16-ko.md"
    ),
    "I4": (
        "doc/apollo-qvp-fidelity-stages/"
        "i4-gpex-msi-lpi-completion-2026-07-16-ko.md"
    ),
    "I5": (
        "doc/apollo-qvp-fidelity-stages/"
        "i5-fault-safety-completion-2026-07-16-ko.md"
    ),
    "I6": (
        "doc/apollo-qvp-fidelity-stages/"
        "i6-software-abi-recovery-completion-2026-07-16-ko.md"
    ),
    "I7": (
        "doc/apollo-qvp-fidelity-stages/"
        "i7-integration-validation-completion-2026-07-17-ko.md"
    ),
    "I8": (
        "doc/apollo-qvp-fidelity-stages/"
        "i8-closeout-completion-2026-07-17-ko.md"
    ),
}

CPU_ID_LIST_KEYS = {
    "online_cpu_ids",
    "linux_online_cpu_ids",
    "enabled_cpu_ids",
    "released_cpu_ids",
    "interrupt_cpu_ids",
    "ap_online_cpu_ids",
    "ap_released_cpu_ids",
}
CPU_COUNT_KEYS = {
    "ap_cpus",
    "expected_ap_cpus",
    "resolved_ap_cpus",
    "linux_online_cpu_count",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def result(name: str, passed: bool, expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "id": name,
        "status": "pass" if passed else "fail",
        "expected": expected,
        "observed": observed,
    }


def skip(name: str, reason: str) -> dict[str, Any]:
    return {"id": name, "status": "skip", "reason": reason}


def refresh_topology(topology_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(TOPOLOGY_VALIDATOR),
            "--emit",
            str(topology_dir / "topology.json"),
            "--hash-artifacts",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def boot_sequence_is_valid(boot: dict[str, Any]) -> tuple[bool, list[str]]:
    steps = {
        str(item.get("id")): item
        for item in boot.get("sequence", [])
        if isinstance(item, dict) and item.get("id")
    }
    observed: list[str] = []
    previous: str | None = None
    for step_id in BOOT_SEQUENCE:
        step = steps.get(step_id)
        if step is None:
            return False, observed
        if previous is not None and step.get("after") != previous:
            return False, observed + [step_id]
        observed.append(step_id)
        previous = step_id
    orders = [steps[step_id].get("order") for step_id in BOOT_SEQUENCE]
    integer_orders: list[int] = []
    for order in orders:
        if not isinstance(order, int):
            return False, observed
        integer_orders.append(order)
    return integer_orders == sorted(integer_orders), observed


def source_hashes_are_valid(artifacts: dict[str, Any]) -> tuple[bool, list[str]]:
    required = {
        "local_conf",
        "bblayers_conf",
        "templateconf",
        "contract_topology",
        "contract_address_map",
        "contract_transaction_routes",
        "contract_signal_routes",
        "contract_boot_control",
        "contract_software_contract",
    }
    valid: set[str] = set()
    for item in artifacts.get("artifacts", []):
        if not isinstance(item, dict) or item.get("name") not in required:
            continue
        digest = item.get("sha256")
        if item.get("exists") is True and isinstance(digest, str) and re.fullmatch(
            r"[0-9a-f]{64}", digest
        ):
            valid.add(str(item["name"]))
    return valid == required, sorted(valid)


def source_revisions_are_valid(artifacts: dict[str, Any]) -> tuple[bool, list[str]]:
    revisions = artifacts.get("source_revisions", {})
    required = ("workspace", "qbox", "qbox_platform", "qemu")
    valid = [
        name
        for name in required
        if isinstance(revisions.get(name), str)
        and re.fullmatch(r"[0-9a-f]{40,64}", revisions[name])
    ]
    return len(valid) == len(required), valid


def _as_cpu_ids(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    result_ids: list[int] = []
    for item in value:
        if isinstance(item, int) and not isinstance(item, bool):
            result_ids.append(item)
        elif isinstance(item, str):
            match = re.fullmatch(r"(?:cpu)?(\d+)", item.lower())
            if match:
                result_ids.append(int(match.group(1)))
    return result_ids


def collect_runtime_cpu_evidence(value: Any) -> tuple[set[int], dict[str, int]]:
    cpu_ids: set[int] = set()
    counts: dict[str, int] = {}

    def visit(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                child_path = f"{path}.{key}" if path else key
                if key in CPU_ID_LIST_KEYS:
                    cpu_ids.update(_as_cpu_ids(child))
                elif key in CPU_COUNT_KEYS and isinstance(child, int) and not isinstance(
                    child, bool
                ):
                    counts[child_path] = child
                elif key == "ap_cpu_markers" and isinstance(child, dict):
                    for marker, seen in child.items():
                        match = re.fullmatch(r"(?:cpu)?(\d+)", str(marker).lower())
                        if match and seen is True:
                            cpu_ids.add(int(match.group(1)))
                visit(child, child_path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{path}[{index}]")

    visit(value)
    return cpu_ids, counts


def validate(
    topology_dir: Path,
    *,
    cpus: int,
    maximum_cpu_id: int,
    machine: str,
    variant: str,
    backend: str,
    runtime_result: Path | None,
) -> dict[str, Any]:
    topology = load_json(topology_dir / "topology.json")
    boot = load_json(topology_dir / "boot-routes.json")
    artifacts = load_json(topology_dir / "artifacts.json")
    validation = load_json(topology_dir / "validation.json")
    checks: list[dict[str, Any]] = []

    configuration = artifacts.get("configuration", {})
    checks.extend(
        (
            result("topology-validation", validation.get("status") == "pass", "pass", validation.get("status")),
            result("machine-topology", topology.get("machine") == machine, machine, topology.get("machine")),
            result("machine-config", configuration.get("machine") == machine, machine, configuration.get("machine")),
            result("variant-topology", topology.get("variant") == variant, variant, topology.get("variant")),
            result("variant-config", configuration.get("rd_aspen_variant") == variant, variant, configuration.get("rd_aspen_variant")),
            result("ap-cpu-count", configuration.get("pc_cpus_count_default") == cpus, cpus, configuration.get("pc_cpus_count_default")),
        )
    )

    reset_defaults = boot.get("reset_defaults", {})
    expected_reset = {
        "ap_primary": "reset_asserted",
        "ap_secondary": "reset_asserted_powered_off",
        "atu_apu": "default_deny_unlocked",
        "cross_domain_access": "rse_only",
    }
    observed_reset = {key: reset_defaults.get(key) for key in expected_reset}
    checks.append(result("reset-defaults", observed_reset == expected_reset, expected_reset, observed_reset))

    boot_valid, observed_boot = boot_sequence_is_valid(boot)
    checks.append(result("boot-owner-sequence", boot_valid, list(BOOT_SEQUENCE), observed_boot))

    hashes_valid, observed_hashes = source_hashes_are_valid(artifacts)
    checks.append(result("source-artifact-hashes", hashes_valid, "all required source inputs", observed_hashes))
    revisions_valid, observed_revisions = source_revisions_are_valid(artifacts)
    checks.append(result("source-revisions", revisions_valid, ["workspace", "qbox", "qbox_platform", "qemu"], observed_revisions))

    runtime_evidence: dict[str, Any] | None = None
    if runtime_result is None:
        checks.append(skip("runtime-four-cpu-boundary", "runtime result was not supplied"))
    else:
        runtime_evidence = load_json(runtime_result)
        cpu_ids, counts = collect_runtime_cpu_evidence(runtime_evidence)
        count_ok = all(count == cpus for count in counts.values()) if counts else False
        id_ok = all(0 <= cpu_id <= maximum_cpu_id for cpu_id in cpu_ids)
        checks.append(
            result(
                "runtime-four-cpu-boundary",
                count_ok and id_ok,
                {"count": cpus, "maximum_cpu_id": maximum_cpu_id},
                {"counts": counts, "cpu_ids": sorted(cpu_ids)},
            )
        )

    failures = [check for check in checks if check["status"] == "fail"]
    ledger = [
        {
            "stage": stage,
            "feature": feature,
            "status": "failed" if stage == "I0" and failures else status,
            "evidence": STAGE_EVIDENCE.get(stage),
        }
        for stage, feature, status in FIDELITY_LEDGER
    ]
    return {
        "schema_version": 1,
        "status": "pass" if not failures else "fail",
        "contract": {
            "machine": machine,
            "variant": variant,
            "ap_cpus": cpus,
            "enabled_cpu_ids": list(range(cpus)),
            "fail_on_enabled_cpu_above": maximum_cpu_id,
            "performance_acceptance": "not-required",
        },
        "provenance": {
            "topology_dir": str(topology_dir.resolve()),
            "runtime_result": str(runtime_result.resolve()) if runtime_result else None,
            "backend": backend,
            "cci_overrides": {},
            "source_revisions": artifacts.get("source_revisions", {}),
            "source_artifacts": artifacts.get("artifacts", []),
        },
        "checks": checks,
        "ledger": ledger,
        "errors": [check["id"] for check in failures],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Apollo QVP four-CPU fidelity baseline contract"
    )
    parser.add_argument("--cpus", type=int, default=4)
    parser.add_argument("--fail-on-enabled-cpu-above", type=int, default=3)
    parser.add_argument("--machine", default="apollo-qvp")
    parser.add_argument("--variant", default="cfg2")
    parser.add_argument("--backend", default="systemc-mmu720ae")
    parser.add_argument("--topology-dir", type=Path, default=DEFAULT_TOPOLOGY_DIR)
    parser.add_argument("--runtime-result", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-refresh", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.cpus <= 0 or args.fail_on_enabled_cpu_above != args.cpus - 1:
        print("CPU boundary must be exactly cpus - 1", file=sys.stderr)
        return 2

    topology_dir = args.topology_dir.resolve()
    if not args.no_refresh:
        refresh = refresh_topology(topology_dir)
        if refresh.returncode:
            print(refresh.stdout, end="", file=sys.stderr)
            print(refresh.stderr, end="", file=sys.stderr)
            return refresh.returncode

    try:
        report = validate(
            topology_dir,
            cpus=args.cpus,
            maximum_cpu_id=args.fail_on_enabled_cpu_above,
            machine=args.machine,
            variant=args.variant,
            backend=args.backend,
            runtime_result=args.runtime_result.resolve() if args.runtime_result else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"fidelity contract input error: {error}", file=sys.stderr)
        return 2

    output = args.output.resolve()
    write_json(output, report)
    print(output)
    if report["status"] != "pass":
        for error in report["errors"]:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

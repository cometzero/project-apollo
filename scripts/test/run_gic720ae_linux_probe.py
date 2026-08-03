#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_result(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "linux-probe-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def negative_fixture(path: Path, out_dir: Path) -> int:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    rows = fixture.get("gic_rows")
    rows_valid = (
        isinstance(rows, dict)
        and set(rows) == {"sgi", "ppi", "spi"}
        and all(value == "PASS" for value in rows.values())
    )
    if (
        fixture.get("spi_target") is not None
        and fixture.get("spi_observed_cpu") != fixture.get("spi_target")
    ):
        payload = {
            "format_version": 1,
            "verdict": "FAIL",
            "reason": "wrong_target_cpu",
            "gic_rows": {"sgi": "PASS", "ppi": "PASS", "spi": "FAIL"},
            "unrelated_probe": "NOT_REQUESTED",
        }
        code = 1
    elif fixture.get("present") is False and rows_valid:
        payload = {
            "format_version": 1,
            "verdict": "PASS",
            "reason": "gic_probe_passed",
            "gic_rows": rows,
            "unrelated_probe": "BLOCKED",
        }
        code = 0
    else:
        payload = {
            "format_version": 1,
            "verdict": "FAIL",
            "reason": "malformed_fixture",
            "gic_rows": {},
            "unrelated_probe": "NOT_REQUESTED",
        }
        code = 1
    write_result(out_dir, payload)
    return code


def artifact_map(profile: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {item["role"]: item for item in profile.get("artifacts", [])}


def verify_artifact(record: dict[str, str], expected: Path) -> None:
    if Path(record["path"]).resolve() != expected.resolve():
        raise ValueError("profile_artifact_path_mismatch")
    if sha256(expected) != record["sha256"]:
        raise ValueError("profile_artifact_hash_mismatch")


def operation_records(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    direct = runtime.get("post_login_probe", {})
    if isinstance(direct, dict) and isinstance(direct.get("operation_records"), list):
        return direct["operation_records"]
    child = runtime.get("runtime_child_result", {})
    if isinstance(child, dict):
        probe = child.get("post_login_probe", {})
        if isinstance(probe, dict) and isinstance(probe.get("operation_records"), list):
            return probe["operation_records"]
    return []


def parse_timer_counts(text: str) -> list[int] | None:
    for line in text.splitlines():
        if "arch_timer" not in line:
            continue
        fields = line.split()
        counts: list[int] = []
        for field in fields[1:]:
            if field.isdigit():
                counts.append(int(field))
            else:
                break
        if counts:
            return counts
    return None


def evaluate_runtime(
    runtime: dict[str, Any], required_cpus: list[int], hotplug_cpu: int,
) -> tuple[dict[str, str], str, list[dict[str, Any]]]:
    records = operation_records(runtime)
    if len(records) != 9 or not all(record.get("completed") for record in records):
        return (
            {"sgi": "FAIL", "ppi": "FAIL", "spi": "FAIL"},
            "operation_manifest_incomplete",
            records,
        )
    failed_output = any(
        re.search(
            r"(No such file|not found|Invalid argument|Operation not permitted|failed)",
            str(record.get("stdout", "")),
            re.IGNORECASE,
        )
        for record in records
    )
    hotplug_values = [
        record.get("operation", {}).get("value")
        for record in records
        if record.get("operation", {}).get("path")
        == f"/sys/devices/system/cpu/cpu{hotplug_cpu}/online"
    ]
    hotplug = hotplug_values == ["0\n", "1\n"] and not failed_output
    reads = [
        str(record.get("stdout", ""))
        for record in records
        if record.get("operation", {}).get("op") == "read"
    ]
    console = json.dumps(runtime)
    ipi = bool(re.search(r"ipi target=1 count=[1-9]", console))
    spi = bool(re.search(r"spi target=1 cpu=1 count=[1-9]", console))
    snapshots = {
        int(cpu): int(timer)
        for cpu, timer in re.findall(
            r"snapshot cpu=(\d+) ipi=\d+ timer=(\d+)", console
        )
    }
    ppi = all(snapshots.get(cpu, 0) > 0 for cpu in required_cpus)
    if len(reads) >= 2:
        before = parse_timer_counts(reads[0])
        after = parse_timer_counts(reads[1])
        ppi = (
            ppi
            and before is not None
            and after is not None
            and all(
                cpu < len(before)
                and cpu < len(after)
                and after[cpu] > before[cpu]
                for cpu in required_cpus
            )
        )
    else:
        ppi = False
    ppi = ppi and hotplug and snapshots.get(hotplug_cpu, 0) > 0
    rows = {
        "sgi": "PASS" if ipi and not failed_output else "FAIL",
        "ppi": "PASS" if ppi else "FAIL",
        "spi": "PASS" if spi and not failed_output else "FAIL",
    }
    reason = "linux_gic_probe_passed" if all(
        value == "PASS" for value in rows.values()
    ) else "linux_gic_probe_failed"
    return rows, reason, records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--runner", type=Path)
    parser.add_argument("--yocto-provenance", type=Path)
    parser.add_argument("--linux-probe-profile-provenance", type=Path)
    parser.add_argument("--primary-kernel", type=Path)
    parser.add_argument("--primary-dtb", type=Path)
    parser.add_argument("--primary-rootfs", type=Path)
    parser.add_argument("--primary-qboxconf", type=Path)
    parser.add_argument("--require-default-image-exclusion", action="store_true")
    parser.add_argument("--primary-operation-manifest", type=Path)
    parser.add_argument("--primary-operation-schema", type=Path)
    parser.add_argument("--record-artifact-hashes", action="store_true")
    parser.add_argument("--cpu-hotplug", type=int)
    parser.add_argument("--require-cpus", default="0,1,2,3")
    parser.add_argument("--require-irq-delta", default="sgi,ppi,spi")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test_negative is not None:
        return negative_fixture(args.self_test_negative, args.out_dir)
    required = (
        args.runner,
        args.yocto_provenance,
        args.linux_probe_profile_provenance,
        args.primary_kernel,
        args.primary_dtb,
        args.primary_rootfs,
        args.primary_qboxconf,
        args.primary_operation_manifest,
        args.primary_operation_schema,
    )
    if any(path is None for path in required):
        write_result(args.out_dir, {
            "format_version": 1,
            "verdict": "FAIL",
            "reason": "missing_input",
            "gic_rows": {},
            "unrelated_probe": "NOT_REQUESTED",
        })
        return 1
    try:
        provenance = json.loads(args.yocto_provenance.read_text())
        profile = json.loads(args.linux_probe_profile_provenance.read_text())
        if provenance.get("verdict") != "PASS" or profile.get("verdict") != "PASS":
            raise ValueError("provenance_failed")
        if args.cpu_hotplug != 1:
            raise ValueError("unsupported_hotplug_cpu")
        required_rows = args.require_irq_delta.split(",")
        if required_rows != ["sgi", "ppi", "spi"]:
            raise ValueError("unsupported_irq_delta")
        if args.require_default_image_exclusion:
            exclusion = profile.get("configuration", {}).get(
                "default_image_exclusion", {}
            )
            if set(exclusion) != {
                "gic720ae-selftest", "gic720ae_test.ko", "overlay"
            } or not all(exclusion.values()):
                raise ValueError("default_image_exclusion_failed")
        artifacts = artifact_map(profile)
        for role, path in (
            ("kernel", args.primary_kernel),
            ("merged_dtb", args.primary_dtb),
            ("wic", args.primary_rootfs),
            ("qboxconf", args.primary_qboxconf),
        ):
            verify_artifact(artifacts[role], path)
        module = Path(artifacts["gic720ae_test"]["path"])
        verify_artifact(artifacts["gic720ae_test"], module)
        module_parts = module.parts
        modules_index = module_parts.index("modules")
        guest_module = Path("/") / Path(*module_parts[modules_index - 1:])
        qboxconf = json.loads(args.primary_qboxconf.read_text())
        provider = qboxconf["provider"]
        images = qboxconf["images"]
        deploy = args.primary_qboxconf.parent
        conf = Path(provider["data_dir"]) / qboxconf["config"]
        runtime_dir = args.out_dir / "qbox-runtime"
        command = [
            sys.executable,
            str(args.runner.resolve()),
            "--conf", str(conf),
            "--qbox-build-dir", provider["bindir"],
            "--rootfs", str(args.primary_rootfs.resolve()),
            "--ap-dtb", str(args.primary_dtb.resolve()),
            "--rse-rom", str((deploy / images["rse_rom"]).resolve()),
            "--rse-flash", str((deploy / images["rse_flash"]).resolve()),
            "--rse-otp", str((deploy / images["rse_otp"]).resolve()),
            "--ap-flash", str((deploy / images["ap_flash"]).resolve()),
            "--si-cl0-image", str((deploy / images["si0_ramfw"]).resolve()),
            "--si-cl1-image", str((deploy / images["si_cl1"]).resolve()),
            "--skip-build",
            "--no-post-login-probe",
            "--primary-operation-manifest",
            str(args.primary_operation_manifest.resolve()),
            "--primary-operation-schema",
            str(args.primary_operation_schema.resolve()),
            "--primary-operation-module-path", str(guest_module),
            "--timeout", str(args.timeout),
            "--out-dir", str(runtime_dir),
        ]
        completed = subprocess.run(command, check=False, timeout=args.timeout + 120)
        runtime_path = runtime_dir / "result.json"
        runtime = json.loads(runtime_path.read_text())
        cpus = [int(value) for value in args.require_cpus.split(",")]
        if cpus != [0, 1, 2, 3]:
            raise ValueError("unsupported_required_cpus")
        rows, reason, records = evaluate_runtime(runtime, cpus, args.cpu_hotplug)
        passed = completed.returncode == 0 and all(
            value == "PASS" for value in rows.values()
        )
        payload = {
            "format_version": 1,
            "verdict": "PASS" if passed else "FAIL",
            "reason": reason,
            "gic_rows": rows,
            "unrelated_probe": "NOT_REQUESTED",
            "runtime_result": str(runtime_path.resolve()),
            "runtime_result_sha256": sha256(runtime_path),
            "command": command,
            "operation_records": records,
            "artifact_hashes": (
                {
                    role: record["sha256"]
                    for role, record in sorted(artifacts.items())
                }
                if args.record_artifact_hashes
                else {}
            ),
            "default_image_exclusion": profile.get(
                "configuration", {}
            ).get("default_image_exclusion", {}),
            "cpu_hotplug": {
                "cpu": args.cpu_hotplug,
                "offline_online_completed": rows["ppi"] == "PASS",
            },
        }
        code = 0 if passed else 1
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as error:
        payload = {
            "format_version": 1,
            "verdict": "FAIL",
            "reason": str(error) or "linux_gic_probe_failed",
            "gic_rows": {},
            "unrelated_probe": "NOT_REQUESTED",
        }
        code = 1
    write_result(args.out_dir, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

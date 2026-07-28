"""Internal fidelity orchestration for the canonical Apollo QBox runner."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LOCAL_ROOT = ROOT / "build/local-apollo-qvp"
YOCTO_ROOT = ROOT / "build/tmp_baremetal"
FULL_RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
YOCTO_RUNNER = ROOT / "run_qbox_yocto.sh"
COVERAGE_AUDITOR = ROOT / "scripts/test/audit_qbox_apollo_fvp_full_coverage.py"
CONTRACT_VALIDATOR = ROOT / "scripts/test/validate_qbox_apollo_fidelity_contract.py"
SOURCE_REPOSITORIES = {
    "workspace": ROOT,
    "qbox": ROOT / "hsoc-stack/tools/qbox",
    "qbox_platform": ROOT / "hsoc-stack/tools/qbox-platform",
    "qemu": ROOT / "hsoc-stack/tools/qemu",
}
CPU_RE = re.compile(r"Detected PIPT I-cache on CPU(?P<cpu>\d+)")


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Apollo four-CPU fidelity smoke with local or Yocto artifacts."
    )
    parser.add_argument("--artifacts", choices=("local", "yocto"), required=True)
    parser.add_argument("--cpus", type=int, default=4)
    parser.add_argument("--profile", choices=("smoke",), default="smoke")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.cpus != 4:
        parser.error("this phase accepts exactly four CPUs (CPU0-CPU3)")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.jobs <= 0:
        parser.error("--jobs must be positive")
    if args.out_dir is None:
        args.out_dir = (
            ROOT
            / "build/qbox-apollo-qvp"
            / f"fidelity-4cpu-{args.artifacts}-{timestamp()}"
        )
    args.out_dir = args.out_dir.resolve()
    return args


def runtime_command(args: argparse.Namespace) -> list[str]:
    if args.artifacts == "local":
        return [
            sys.executable,
            str(FULL_RUNNER),
            "--local-build-dir",
            str(LOCAL_ROOT),
            "--qbox-build-dir",
            str(LOCAL_ROOT / "work/qbox-platform"),
            "--out-dir",
            str(args.out_dir),
            "--timeout",
            str(args.timeout),
            "--jobs",
            str(args.jobs),
            "--skip-build",
            "--no-post-login-probe",
            "--rootfs-bootargs-profile",
            "none",
        ]
    return [
        str(YOCTO_RUNNER),
        "--headless",
        "--exit-after-pass",
        "--no-copy-disks",
        "--out-dir",
        str(args.out_dir),
        "--timeout",
        str(args.timeout),
        "--jobs",
        str(args.jobs),
        "--rootfs-bootargs-profile",
        "none",
    ]


def run_git(repo: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout if completed.returncode == 0 else b""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_state(name: str, repo: Path) -> dict[str, Any]:
    revision = run_git(repo, "rev-parse", "HEAD").decode().strip()
    status = run_git(repo, "status", "--porcelain=v1", "-z")
    digest = hashlib.sha256()
    digest.update(run_git(repo, "diff", "--binary", "HEAD", "--"))
    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    for raw_path in sorted(item for item in untracked.split(b"\0") if item):
        path = repo / os.fsdecode(raw_path)
        digest.update(raw_path)
        if path.is_file():
            digest.update(bytes.fromhex(sha256_file(path)))
    return {
        "name": name,
        "path": str(repo.resolve()),
        "revision": revision or None,
        "dirty": bool(status),
        "source_state_sha256": digest.hexdigest(),
    }


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def existing_input_paths(result: dict[str, Any]) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    records = result.get("input_artifacts", {})
    if isinstance(records, dict):
        for name, record in records.items():
            if not isinstance(record, dict) or record.get("exists") is not True:
                continue
            value = record.get("path")
            if isinstance(value, str):
                paths.append((str(name), Path(value)))
    for name in ("qbox_executable", "qbox_conf"):
        value = result.get(name)
        if isinstance(value, str) and Path(value).is_file():
            paths.append((name, Path(value)))
    return paths


def artifact_family_errors(family: str, result: dict[str, Any]) -> list[str]:
    allowed = LOCAL_ROOT if family == "local" else YOCTO_ROOT
    errors: list[str] = []
    for name, path in existing_input_paths(result):
        if name in {"conf", "qbox_conf"} and family == "local" and is_relative_to(
            path, ROOT / "hsoc-stack/tools/qbox-platform"
        ):
            continue
        if not is_relative_to(path, allowed):
            errors.append(f"mixed_artifact:{name}:{path}")
    return errors


def artifact_hashes(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    hashes: dict[str, dict[str, Any]] = {}
    for name, path in existing_input_paths(result):
        resolved = path.resolve()
        if not resolved.is_file():
            continue
        hashes[name] = {
            "path": str(resolved),
            "size": resolved.stat().st_size,
            "sha256": sha256_file(resolved),
        }
    return hashes


def linux_cpu_ids(out_dir: Path) -> list[int]:
    log = out_dir / "qbox-primary-console.log"
    if not log.is_file():
        return []
    text = log.read_text(encoding="utf-8", errors="replace")
    return sorted({int(match.group("cpu")) for match in CPU_RE.finditer(text)})


def read_optional(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def marker_pass(result: dict[str, Any], group: str, marker: str) -> bool:
    groups = result.get("marker_groups", {})
    if not isinstance(groups, dict):
        return False
    entries = groups.get(group, {})
    return isinstance(entries, dict) and entries.get(marker) is True


def fidelity_markers(
    result: dict[str, Any], cpus: list[int], out_dir: Path
) -> dict[str, Any]:
    rse_log = read_optional(out_dir / "qbox-rse.log")
    primary_log = read_optional(out_dir / "qbox-primary-console.log")
    return {
        "I0_4cpu": {
            "executed": True,
            "passed": cpus == [0, 1, 2, 3],
            "observed_cpu_ids": cpus,
        },
        "I1_request_context": {
            "executed": True,
            "passed": bool(result.get("passed")),
            "scope": "normal full-system transaction path",
        },
        "I2_apu_atu": {
            "executed": True,
            "passed": "AP ATU region 0:" in rse_log,
            "scope": "firmware-programmed ATU normal path; APU deny remains targeted evidence",
        },
        "I3_smmuv3": {
            "executed": False,
            "passed": None,
            "normal_path_observed": "smmu" in primary_log.lower(),
            "reason": "mapped DMA and fault recovery remain targeted component evidence",
        },
        "I4_gic_its": {
            "executed": True,
            "passed": "ITS [mem " in primary_log and "LPI pending table" in primary_log,
            "scope": "normal GIC/ITS path; paired MSI-X/INTx remains targeted evidence",
        },
        "I5_fault_event": {
            "executed": False,
            "passed": None,
            "reason": "smoke profile does not inject a safety fault",
        },
        "I6_abi_recovery": {
            "executed": True,
            "passed": marker_pass(result, "si_cl1", "pfdi_agent"),
            "negative_path_executed": False,
            "normal_path_passed": marker_pass(result, "si_cl1", "pfdi_agent"),
            "reason": "malformed input remains targeted component evidence",
        },
    }


def run_json_tool(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    output = Path(command[-1])
    return {
        "command": command,
        "returncode": completed.returncode,
        "output": str(output.resolve()),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    command = runtime_command(args)
    if args.dry_run:
        print(json.dumps({"artifacts": args.artifacts, "command": command}, indent=2))
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["QBOX_APOLLO_NUM_CPUS"] = str(args.cpus)
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    result_path = args.out_dir / "result.json"
    if not result_path.is_file():
        print(f"missing runtime result: {result_path}", file=sys.stderr)
        return completed.returncode or 1

    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        print(f"runtime result is not an object: {result_path}", file=sys.stderr)
        return 1

    family_errors = artifact_family_errors(args.artifacts, result)
    cpus = linux_cpu_ids(args.out_dir)
    if cpus != [0, 1, 2, 3]:
        family_errors.append(f"linux_cpu_ids:{cpus}")
    manifest = {
        "schema_version": 1,
        "artifact_family": args.artifacts,
        "profile": args.profile,
        "expected_cpu_ids": [0, 1, 2, 3],
        "linux_online_cpu_ids": cpus,
        "source_revisions": {
            name: source_state(name, repo)
            for name, repo in SOURCE_REPOSITORIES.items()
        },
        "artifacts": artifact_hashes(result),
        "backend": {
            "smmu": result.get("smmu_backend"),
            "mhu": result.get("mhu_backend"),
            "ap_tcg_mode": result.get("ap_tcg_mode"),
            "si_cl0_tcg_mode": result.get("si_cl0_tcg_mode"),
            "si_cl1_tcg_mode": result.get("si_cl1_tcg_mode"),
            "si_cl1_sync_policy": result.get("si_cl1_sync_policy"),
        },
        "resolved_topology": {
            "machine": "apollo-qvp",
            "variant": "cfg2",
            "ap_cpu_ids": [0, 1, 2, 3],
            "safety_island_topology": result.get("safety_island_topology"),
        },
        "fidelity_markers": fidelity_markers(result, cpus, args.out_dir),
        "artifact_family_errors": family_errors,
        "runtime_command": command,
        "runtime_returncode": completed.returncode,
    }
    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    result["artifact_family"] = args.artifacts
    result["profile"] = args.profile
    result["linux_online_cpu_ids"] = cpus
    result["fidelity_manifest"] = str(manifest_path.resolve())
    result["fidelity_markers"] = manifest["fidelity_markers"]
    if family_errors:
        result["passed"] = False
        result["verdict"] = "blocked"
        result["blocker"] = ";".join(family_errors)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    coverage = run_json_tool(
        [
            sys.executable,
            str(COVERAGE_AUDITOR),
            "--result-json",
            str(result_path),
            "--output",
            str(args.out_dir / "full-coverage-audit.json"),
        ]
    )
    contract = run_json_tool(
        [
            sys.executable,
            str(CONTRACT_VALIDATOR),
            "--cpus",
            "4",
            "--fail-on-enabled-cpu-above",
            "3",
            "--runtime-result",
            str(result_path),
            "--output",
            str(args.out_dir / "fidelity-contract.json"),
        ]
    )
    manifest["validation"] = {"coverage": coverage, "contract": contract}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    passed = bool(
        result.get("passed")
        and completed.returncode == 0
        and coverage["returncode"] == 0
        and contract["returncode"] == 0
        and not family_errors
    )
    summary = {
        "passed": passed,
        "artifact_family": args.artifacts,
        "runtime_result": str(result_path.resolve()),
        "manifest": str(manifest_path.resolve()),
        "coverage": coverage,
        "contract": contract,
    }
    (args.out_dir / "fidelity-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(args.out_dir)
    return 0 if passed else 1

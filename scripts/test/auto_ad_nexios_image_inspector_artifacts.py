#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import hashlib
import json
from pathlib import Path

from auto_ad_nexios_image_inspector_lib import (
    InspectError,
    blkid_probe,
    find_deploy_artifact,
)


def inspect_verity(deploy_dir, image_base):
    names = [f"{image_base}.ext4.verity", "nexios-image-apollo-fvp.ext4.verity"]
    env_names = [
        f"{image_base}.ext4.verity.env",
        "nexios-image-apollo-fvp.ext4.verity.env",
    ]
    artifact = find_deploy_artifact(deploy_dir, names)
    env = find_deploy_artifact(deploy_dir, env_names)
    if artifact is None:
        raise InspectError(
            "missing appended dm-verity image artifact in deploy dir: "
            + ", ".join(names)
        )
    if env is None:
        raise InspectError("missing dm-verity env artifact in deploy dir: " + ", ".join(env_names))
    if artifact.stat().st_size == 0:
        raise InspectError(f"empty dm-verity artifact: {artifact}")
    if env.stat().st_size == 0:
        raise InspectError(f"empty dm-verity env artifact: {env}")
    return {
        "artifact": str(artifact),
        "artifact_size": artifact.stat().st_size,
        "env": str(env),
        "env_size": env.stat().st_size,
    }


def sha256_path(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path):
    return {
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256_path(path),
    }


def newest_match(deploy_dir, pattern):
    matches = sorted(deploy_dir.glob(pattern), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise InspectError(f"missing deploy artifact matching {pattern}")
    path = matches[-1]
    if path.stat().st_size == 0:
        raise InspectError(f"empty deploy artifact: {path}")
    return path


def inspect_uboot_artifacts(deploy_dir):
    return {
        "u_boot_bin": artifact_record(newest_match(deploy_dir, "u-boot-apollo-fvp-*.bin")),
        "initial_env": artifact_record(newest_match(deploy_dir, "u-boot-initial-env-apollo-fvp-*")),
    }


def load_json_evidence(path):
    evidence = Path(path)
    if not evidence.exists():
        return None, evidence
    if evidence.stat().st_size == 0:
        raise InspectError(f"empty evidence artifact: {evidence}")
    try:
        return json.loads(evidence.read_text()), evidence
    except json.JSONDecodeError as exc:
        raise InspectError(f"invalid JSON evidence artifact {evidence}: {exc}") from exc


def inspect_host_fixture_evidence(path):
    data, evidence = load_json_evidence(path)
    missing = {
        "status": "EXTERNAL_EVIDENCE_REQUIRED",
        "evidence_required": str(evidence),
    }
    if data is None:
        return missing, missing
    boot = data.get("bootcommand_fixture", {})
    load_attempts = boot.get("load_attempts", [])
    booted_path = boot.get("booted_path")
    fallback_ok = (
        data.get("status") == "PASS"
        and len(load_attempts) >= 2
        and load_attempts[0].get("path") == "EFI/Linux/auto-ad-nexios-a.efi"
        and load_attempts[1].get("path") == "EFI/Linux/auto-ad-nexios-b.efi"
        and booted_path == "EFI/Linux/auto-ad-nexios-b.efi"
    )
    c_fixture = data.get("c_fixture", {})
    stdout_value = c_fixture.get("stdout")
    stdout = Path(stdout_value) if stdout_value else None
    stdout_text = stdout.read_text() if stdout and stdout.exists() else ""
    corrupt_ok = (
        data.get("status") == "PASS"
        and "CASE corrupt-crc-default-a" in stdout_text
        and "ENV aanx_slot=A" in stdout_text
        and "SUMMARY PASS" in stdout_text
    )
    corrupt = {
        "status": "PASS" if corrupt_ok else "EXTERNAL_EVIDENCE_INVALID",
        "evidence": str(evidence),
        "stdout": str(stdout) if stdout else None,
    }
    fallback = {
        "status": "PASS" if fallback_ok else "EXTERNAL_EVIDENCE_INVALID",
        "evidence": str(evidence),
        "load_attempts": load_attempts,
        "booted_path": booted_path,
    }
    return corrupt, fallback


def inspect_runtime_evidence(path):
    data, evidence = load_json_evidence(path)
    if data is None:
        return {"status": "RUNTIME_REQUIRED", "evidence_required": str(evidence)}
    runtime = data.get("bad_rootro_runtime_status", {})
    markers = runtime.get("markers", {})
    required = (
        "verity_corruption",
        "verity_detected_corruption",
        "mapper_mount_failed",
        "kernel_panic_before_login",
        "no_login_prompt",
        "no_root_shell",
        "no_verified_root_mount",
    )
    passed = runtime.get("status") == "PASS" and all(markers.get(name) for name in required)
    return {
        "status": "PASS" if passed else "EXTERNAL_EVIDENCE_INVALID",
        "evidence": str(evidence),
        "result_json": runtime.get("result_json"),
        "primary_uart": runtime.get("primary_uart"),
        "markers": markers,
        "verdict": runtime.get("verdict"),
    }


def inspect_secure_boot_parse_log(path):
    log = Path(path)
    if not log.exists():
        return {"status": "EXTERNAL_EVIDENCE_REQUIRED", "evidence_required": str(log)}
    if log.stat().st_size == 0:
        raise InspectError(f"empty evidence artifact: {log}")
    text = log.read_text()
    exit_code = None
    for line in text.splitlines():
        if line.startswith("[secure-boot-parse-exit] "):
            exit_code = int(line.rsplit(" ", 1)[1])
    failed_for_keys = (
        exit_code != 0
        and "requires UKI_SB_KEY and UKI_SB_CERT" in text
        and "Parsing halted due to errors" in text
    )
    return {
        "status": "PASS" if failed_for_keys else "EXTERNAL_EVIDENCE_INVALID",
        "parse_log": str(log),
        "exit_code": exit_code,
    }


def check_filesystems(wic, by_name):
    expected = {
        "boot_a": ("vfat", "boot_a"),
        "boot_b": ("vfat", "boot_b"),
        "rootro_a": ("ext4", None),
        "rootro_b": ("ext4", None),
        "rootrw": ("ext4", "rootrw"),
        "data": ("ext4", "data"),
    }
    result = {}
    for name, (fstype, label) in expected.items():
        info = blkid_probe(wic, by_name[name])
        if not info.get("probed"):
            raise InspectError(f"partition {name} has no filesystem: {info['error']}")
        actual_label = info.get("LABEL") or info.get("LABEL_FATBOOT")
        if info.get("TYPE") != fstype:
            raise InspectError(
                f"partition {name} filesystem mismatch: expected {fstype}, got {info.get('TYPE')}"
            )
        if label is not None and actual_label != label:
            raise InspectError(
                f"partition {name} label mismatch: expected {label}, got {actual_label}"
            )
        result[name] = info
    return result

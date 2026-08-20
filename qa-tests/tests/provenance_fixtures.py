from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import subprocess
from typing import TypeAlias

import pytest

from apollo_validation import qbox_runner
from apollo_validation.qbox_entry import run_qbox_root
from apollo_validation.qbox_runner import ProcessResult


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

SELECTORS = ("test_00_bsp_boot", "test_64_bsp_pfdi")
SOURCE_ROOT = Path(__file__).resolve().parents[2]
EXPECTED = (
    "pfdi-systemd-service",
    "pfdi-app",
    "pfdi-cli",
    "pfdi-cli-force-error",
    "pfdi-app-monitoring",
    "pfdi-app-monitoring-error",
    "pfdi-sbistc",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def make_workspace(root: Path) -> None:
    profile = SOURCE_ROOT / "qa-tests/profiles/pfdi.yaml"
    matrix = SOURCE_ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
    _write(root / "qa-tests/profiles/pfdi.yaml", profile.read_bytes())
    _write(
        root / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml",
        matrix.read_bytes(),
    )
    for selector, layer in (
        (SELECTORS[0], "meta-hsoc-bsp"),
        (SELECTORS[1], "meta-hsoc-bsp"),
    ):
        _write(
            root / f"hsoc-stack/yocto/{layer}/lib/oeqa/runtime/cases/{selector}.py",
            f"# {selector}\n".encode(),
        )
    for relative in (
        "hsoc-stack/yocto/meta-hsoc-auto-solutions/.fixture",
        "hsoc-stack/tools/qbox/.fixture",
        "hsoc-stack/tools/qbox-platform/.fixture",
        "hsoc-stack/tools/qemu/.fixture",
    ):
        _write(root / relative, b"fixture\n")
    _write(root / "build/conf/local.conf", b'PC_CPUS_COUNT_DEFAULT = "4"\n')
    _write(root / "build/conf/bblayers.conf", b'BBLAYERS = ""\n')
    _write(root / "build/conf/templateconf.cfg", b"fixture\n")
    for machine, runtime in (("apollo-fvp", "fvpconf"), ("apollo-qvp", "qboxconf")):
        deploy = root / f"build/tmp_baremetal/deploy/images/{machine}"
        stem = f"nexios-bsp-initramfs-{machine}"
        _write(deploy / f"{stem}.testdata.json", b'{"PC_CPUS_COUNT_DEFAULT":"4"}\n')
        _write(deploy / f"{stem}.{runtime}", b'{"exe":"fixture"}\n')
        _write(deploy / f"{stem}.wic", f"image-{machine}\n".encode())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.com"], cwd=root, check=True
    )
    subprocess.run(["git", "add", "qa-tests", "hsoc-stack"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
    _write(root / "fixture-marker.txt", b"current\n")
    subprocess.run(["git", "add", "fixture-marker.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "current fixture"], cwd=root, check=True)


def _blob_identity(root: Path, path: Path) -> dict[str, JsonValue]:
    relative = path.relative_to(root)
    blob = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return {
        "path": str(relative),
        "git_blob_sha256": sha256_bytes(blob),
    }


def _runtime_identity(kind: str, path: Path) -> dict[str, JsonValue]:
    return {"kind": kind, "path": str(path), "sha256": sha256_bytes(path.read_bytes())}


def reference_summary(root: Path) -> dict[str, JsonValue]:
    profile_path = root / "qa-tests/profiles/pfdi.yaml"
    shared_paths = (
        root / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml",
        profile_path,
        root
        / "hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/runtime/cases/test_00_bsp_boot.py",
        root
        / "hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/runtime/cases/test_64_bsp_pfdi.py",
    )
    shared: list[JsonValue] = [_blob_identity(root, path) for path in shared_paths]
    semantic: dict[str, JsonValue] = {
        "profile_id": "pfdi",
        "image_profile": "bsp",
        "cpu_count": 4,
        "selectors": list(SELECTORS),
        "expected_assertion_ids": list(EXPECTED),
        "coverage_kind": "identical",
        "shared_inputs": shared,
    }
    digest = sha256_bytes(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    )
    deploy = root / "build/tmp_baremetal/deploy/images/apollo-fvp"
    stem = "nexios-bsp-initramfs-apollo-fvp"
    runtime: list[JsonValue] = [
        _runtime_identity("testdata", deploy / f"{stem}.testdata.json"),
        _runtime_identity("runtime_config", deploy / f"{stem}.fvpconf"),
        _runtime_identity("image_artifact", deploy / f"{stem}.wic"),
    ]
    assertions: list[JsonValue] = [
        {"id": assertion_id, "status": "PASS", "coverage_kind": "identical"}
        for assertion_id in EXPECTED
    ]
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    summary: dict[str, JsonValue] = {
        "schema_version": 1,
        "run_id": "fvp-pfdi-run",
        "run_dir": str(root / "build/tests/fvp-pfdi-run"),
        "status": "PASS",
        "exit_code": 0,
        "backend": "fvp",
        "machine": "apollo-fvp",
        "image": "nexios-bsp-initramfs",
        "image_profile": "bsp",
        "test_profile": "pfdi",
        "counts": {
            "passed": len(EXPECTED),
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "total": len(EXPECTED),
        },
        "profile_result": {
            "version": 1,
            "profile_id": "pfdi",
            "backend": "fvp",
            "verdict": "PASS",
            "expected": list(EXPECTED),
            "assertions": assertions,
        },
        "provenance": {
            "version": 1,
            "profile_id": "pfdi",
            "profile_snapshot_sha256": sha256_bytes(profile_path.read_bytes()),
            "semantic_profile_digest": digest,
            "selectors": list(SELECTORS),
            "expected_assertion_ids": list(EXPECTED),
            "coverage_kind": "identical",
            "machine": "apollo-fvp",
            "image": "nexios-bsp-initramfs",
            "image_profile": "bsp",
            "cpu_count": 4,
            "shared_inputs": shared,
            "runtime_inputs": runtime,
            "source_revisions": {
                "workspace": revision,
                "qa_runner": revision,
                "bsp_layer": revision,
                "platform_layer": revision,
            },
        },
    }
    return summary


def write_reference(
    root: Path,
    mutate: Callable[[dict[str, JsonValue]], None] | None = None,
) -> Path:
    summary = reference_summary(root)
    if mutate is not None:
        mutate(summary)
    path = root / "build/tests/fvp-pfdi-run/summary.json"
    _write(path, (json.dumps(summary, sort_keys=True) + "\n").encode())
    return path


def run_qbox_profile(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    reference: Path | None,
    out_name: str = "qbox-pfdi-run",
) -> tuple[int, list[list[str]]]:
    calls: list[list[str]] = []

    def completed(
        command: list[str],
        request: qbox_runner.QBoxRunRequest,
        stdout_path: Path,
        stderr_path: Path,
    ) -> ProcessResult:
        calls.append(command)
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("preflight pass\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return ProcessResult(0, 0.0)

    monkeypatch.setattr(qbox_runner, "_run_process", completed)
    argv = [
        "--machine",
        "apollo-qvp",
        "--bsp",
        "--test-profile",
        "pfdi",
        "--dry-run",
        "--out-dir",
        f"build/tests/{out_name}",
    ]
    if reference is not None:
        argv.extend(["--fvp-reference", str(reference)])
    return run_qbox_root(root, argv), calls

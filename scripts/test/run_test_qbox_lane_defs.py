from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True, slots=True)
class QboxInputs:
    root: Path
    run_dir: Path
    commands_file: Path
    dry_run: bool
    include_runtime: bool
    skip_runtime: bool
    timeout_fvp: str


@dataclass(frozen=True, slots=True)
class QboxLane:
    name: str
    argv: list[str]
    command: list[str]
    cwd: Path
    stdout_log: Path
    stderr_log: Path
    artifact_path: Path | None
    required: bool


def qbox_build_dir(inputs: QboxInputs) -> Path:
    override = os.environ.get("RUN_TEST_QBOX_BUILD_DIR")
    if override:
        path = Path(override)
        return path if path.is_absolute() else inputs.root / path
    return inputs.root / "build/local-apollo-fvp/work/qbox-platform"


def qbox_build_arg() -> str:
    return os.environ.get("RUN_TEST_QBOX_BUILD_DIR") or "build/local-apollo-fvp/work/qbox-platform"


def static_lanes(inputs: QboxInputs) -> list[QboxLane]:
    static_dir = inputs.run_dir / "extra/qbox-static"
    full_map = static_dir / "full-map.json"
    core_boundary = static_dir / "core-boundary.json"
    ap_memory = static_dir / "ap-memory-map.json"
    boot_sequence = static_dir / "boot-sequence.json"
    return [
        QboxLane(
            "qbox-static-full-map",
            ["python3", "scripts/test/validate_qbox_apollo_fvp_full_map.py", "--out", str(full_map)],
            ["python3", "scripts/test/validate_qbox_apollo_fvp_full_map.py", "--out", str(full_map)],
            inputs.root,
            static_dir / "full-map.stdout.log",
            static_dir / "full-map.stderr.log",
            full_map,
            True,
        ),
        QboxLane(
            "qbox-static-core-boundary",
            ["python3", "scripts/test/audit_qbox_core_boundary.py", "--json", ">", str(core_boundary)],
            ["python3", "scripts/test/audit_qbox_core_boundary.py", "--json"],
            inputs.root,
            core_boundary,
            static_dir / "core-boundary.stderr.log",
            core_boundary,
            True,
        ),
        QboxLane(
            "qbox-static-ap-memory-map",
            [
                "python3",
                "scripts/test/audit_qbox_apollo_ap_memory_map.py",
                "--check",
                "coverage",
                "--output",
                str(ap_memory),
            ],
            [
                "python3",
                "scripts/test/audit_qbox_apollo_ap_memory_map.py",
                "--check",
                "coverage",
                "--output",
                str(ap_memory),
            ],
            inputs.root,
            static_dir / "ap-memory-map.stdout.log",
            static_dir / "ap-memory-map.stderr.log",
            ap_memory,
            True,
        ),
        QboxLane(
            "qbox-static-boot-sequence",
            [
                "python3",
                "scripts/test/validate_qbox_apollo_fvp_boot_sequence.py",
                "--static-only",
                "--output",
                str(boot_sequence),
            ],
            [
                "python3",
                "scripts/test/validate_qbox_apollo_fvp_boot_sequence.py",
                "--static-only",
                "--output",
                str(boot_sequence),
            ],
            inputs.root,
            static_dir / "boot-sequence.stdout.log",
            static_dir / "boot-sequence.stderr.log",
            boot_sequence,
            True,
        ),
    ]


def ctest_lanes(inputs: QboxInputs) -> list[QboxLane]:
    ctest_dir = inputs.run_dir / "extra/qbox-ctest"
    build_arg = qbox_build_arg()
    return [
        QboxLane(
            "qbox-ctest-list",
            ["ctest", "--test-dir", build_arg, "-N"],
            ["ctest", "--test-dir", build_arg, "-N"],
            inputs.root,
            ctest_dir / "list.stdout.log",
            ctest_dir / "list.stderr.log",
            None,
            True,
        ),
        QboxLane(
            "qbox-ctest-rse-components",
            [
                "ctest",
                "--test-dir",
                build_arg,
                "-R",
                "zena_(fmu|ssu)|rse_atu|rse_protection_ctrl",
                "--output-on-failure",
            ],
            [
                "ctest",
                "--test-dir",
                build_arg,
                "-R",
                "zena_(fmu|ssu)|rse_atu|rse_protection_ctrl",
                "--output-on-failure",
            ],
            inputs.root,
            ctest_dir / "rse-components.stdout.log",
            ctest_dir / "rse-components.stderr.log",
            None,
            True,
        ),
    ]


def runtime_lanes(inputs: QboxInputs) -> list[QboxLane]:
    check_dir = inputs.run_dir / "extra/qbox-full/check-only"
    live_dir = inputs.run_dir / "extra/qbox-full/live-cl0-cl1"
    return [
        QboxLane(
            "qbox-full-check-only",
            [
                "python3",
                "scripts/run/run_qbox_apollo_fvp_full.py",
                "--check-only",
                "--si-mode",
                "live-cl0-cl1",
                "--out-dir",
                str(check_dir),
            ],
            [
                "python3",
                "scripts/run/run_qbox_apollo_fvp_full.py",
                "--check-only",
                "--si-mode",
                "live-cl0-cl1",
                "--out-dir",
                str(check_dir),
            ],
            inputs.root,
            check_dir / "stdout.log",
            check_dir / "stderr.log",
            check_dir,
            True,
        ),
        QboxLane(
            "qbox-full-live-cl0-cl1",
            [
                "python3",
                "scripts/run/run_qbox_apollo_fvp_full.py",
                "--skip-build",
                "--si-mode",
                "live-cl0-cl1",
                "--timeout",
                inputs.timeout_fvp,
                "--out-dir",
                str(live_dir),
            ],
            [
                "python3",
                "scripts/run/run_qbox_apollo_fvp_full.py",
                "--skip-build",
                "--si-mode",
                "live-cl0-cl1",
                "--timeout",
                inputs.timeout_fvp,
                "--out-dir",
                str(live_dir),
            ],
            inputs.root,
            live_dir / "stdout.log",
            live_dir / "stderr.log",
            live_dir,
            True,
        ),
    ]

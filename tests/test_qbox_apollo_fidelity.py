from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
MODULE = ROOT / "scripts/run/qbox_apollo_fidelity.py"


def load_module():
    spec = importlib.util.spec_from_file_location("qbox_apollo_fidelity", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_dry_run_selects_only_local_full_system_runner(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fidelity",
            "--artifacts",
            "local",
            "--cpus",
            "4",
            "--profile",
            "smoke",
            "--out-dir",
            str(tmp_path),
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert completed.returncode == 0, completed.stderr
    assert "run_qbox_apollo_fvp_full.py" in completed.stdout
    assert "build/local-apollo-qvp" in completed.stdout
    assert '"--rootfs-bootargs-profile",\n    "none"' in completed.stdout
    assert "quiet-console" not in completed.stdout
    assert "--no-post-login-probe" in completed.stdout
    assert "run_qbox_yocto.sh" not in completed.stdout


def test_yocto_dry_run_selects_provider_aware_launcher(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fidelity",
            "--artifacts",
            "yocto",
            "--out-dir",
            str(tmp_path),
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert completed.returncode == 0, completed.stderr
    assert "run_qbox_yocto.sh" in completed.stdout
    assert "--headless" in completed.stdout
    assert "--exit-after-pass" in completed.stdout


def test_artifact_family_rejects_cross_family_inputs(tmp_path: Path) -> None:
    module = load_module()
    local_file = module.LOCAL_ROOT / "deploy/firmware/rse-rom-image.img"
    yocto_file = module.YOCTO_ROOT / "deploy/images/apollo-qvp/rse-rom-image.img"

    local_result = {
        "input_artifacts": {
            "rse_rom": {"exists": True, "path": str(local_file)},
            "rootfs": {"exists": True, "path": str(yocto_file)},
        }
    }
    yocto_result = {
        "input_artifacts": {
            "rse_rom": {"exists": True, "path": str(yocto_file)},
            "rootfs": {"exists": True, "path": str(local_file)},
        }
    }

    assert module.artifact_family_errors("local", local_result) == [
        f"mixed_artifact:rootfs:{yocto_file}"
    ]
    assert module.artifact_family_errors("yocto", yocto_result) == [
        f"mixed_artifact:rootfs:{local_file}"
    ]


def test_non_four_cpu_request_is_rejected(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fidelity",
            "--artifacts",
            "local",
            "--cpus",
            "5",
            "--out-dir",
            str(tmp_path),
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert completed.returncode == 2
    assert "exactly four CPUs" in completed.stderr

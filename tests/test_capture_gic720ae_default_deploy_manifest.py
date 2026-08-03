from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/capture_gic720ae_default_deploy_manifest.py"
SCHEMA = ROOT / "tests/schemas/gic720ae-default-deploy-manifest.schema.json"


def run_capture(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def populate(root: Path, suffix: str) -> None:
    root.mkdir()
    (root / f"Image-{suffix}.bin").write_bytes(b"kernel")
    (root / "Image").symlink_to(f"Image-{suffix}.bin")
    (root / "apollo-qvp.dtb").write_bytes(b"dtb")
    (root / f"nexios-bsp-initramfs-{suffix}.wic").write_bytes(b"wic")
    (root / "nexios-bsp-initramfs-apollo-qvp.wic").symlink_to(
        f"nexios-bsp-initramfs-{suffix}.wic"
    )
    (root / f"nexios-bsp-initramfs-{suffix}.qboxconf").write_bytes(b"conf")
    (root / "nexios-bsp-initramfs-apollo-qvp.qboxconf").symlink_to(
        f"nexios-bsp-initramfs-{suffix}.qboxconf"
    )
    (root / "si0_ramfw.bin").write_bytes(b"si0")
    (root / "zephyr-demos-cl1.bin").write_bytes(b"si1")
    (root / "nexios-bsp-initramfs-apollo-qvp.manifest").write_text(
        "base-package arm64 1\n", encoding="utf-8"
    )


def test_complete_instance_detects_any_default_deploy_change(tmp_path: Path) -> None:
    deploy = tmp_path / "deploy"
    populate(deploy, "20260730010101")
    before = tmp_path / "before.json"
    assert run_capture(
        "--root", str(deploy), "--mode", "complete-instance",
        "--schema", str(SCHEMA), "--output", str(before),
    ).returncode == 0
    (deploy / "apollo-qvp.dtb").write_bytes(b"changed")
    after = tmp_path / "after.json"
    result = run_capture(
        "--root", str(deploy), "--mode", "complete-instance",
        "--compare", str(before), "--schema", str(SCHEMA),
        "--output", str(after),
    )
    assert result.returncode != 0
    assert json.loads(after.read_text())["reason"] == "default_deploy_contaminated"


def test_stable_contract_ignores_datetime_names_and_symlink_text(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    populate(first, "20260730010101")
    populate(second, "20260730020202")
    baseline = tmp_path / "stable.json"
    assert run_capture(
        "--root", str(first), "--mode", "stable-contract",
        "--schema", str(SCHEMA), "--output", str(baseline),
    ).returncode == 0
    output = tmp_path / "compared.json"
    result = run_capture(
        "--root", str(second), "--mode", "stable-contract",
        "--compare-stable-contract", str(baseline),
        "--schema", str(SCHEMA), "--output", str(output),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text())
    assert payload["verdict"] == "PASS"
    assert "20260730" not in json.dumps(payload)

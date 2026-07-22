from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/package.sh"


def write_file(path: Path, content: str | bytes = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def create_local_package_inputs(local_build: Path) -> None:
    for rel in (
        "deploy/firmware/rse-rom-image.img",
        "deploy/firmware/rse-flash-image.img",
        "deploy/firmware/rse-otp-image.img",
        "deploy/firmware/ap-flash-image.img",
        "deploy/firmware/fip.bin",
        "deploy/firmware/init_fwu_metadata.bin",
        "deploy/firmware/combined_provisioning_message.bin",
        "deploy/firmware/si0_ramfw.bin",
        "deploy/firmware/zephyr-demos-cl1.bin",
        "deploy/firmware/zephyr-demos-cl1.elf",
        "deploy/boot/apollo-fvp-local-disk.img",
        "deploy/boot/boot-fat.img",
        "deploy/boot/apollo-fvp.dtb",
        "work/signing/deploy/signed_bl2.bin",
        "work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf",
        "work/trusted-firmware-m/bin/bl1_2.elf",
        "work/trusted-firmware-m/bin/bl2.elf",
        "debug/symbols.json",
    ):
        write_file(local_build / rel)


def test_package_readme_and_manifest_use_qvp_machine_paths(tmp_path: Path) -> None:
    local_build = tmp_path / "build/local-apollo-qvp"
    package_dir = tmp_path / "package"
    qbox_build = tmp_path / "build/local-apollo-qvp/work/qbox-platform"
    qbox_conf = tmp_path / "qbox-platform/platforms/apollo/apollo-qvp.lua"
    yocto_deploy = tmp_path / "build/tmp_baremetal/deploy/images/apollo-qvp"
    qboxconf = yocto_deploy / "nexios-image-apollo-qvp.qboxconf"
    create_local_package_inputs(local_build)
    write_file(qbox_build / "platforms-vp")
    write_file(qbox_conf, "return {}\n")
    write_file(qboxconf, "{}\n")

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=ROOT,
        env={
            **os.environ,
            "MACHINE": "apollo-qvp",
            "LOCAL_BUILD_DIR": str(local_build),
            "PACKAGE_DIR": str(package_dir),
            "QBOX_PLATFORM_BUILD_DIR": str(qbox_build),
            "QBOX_CONF": str(qbox_conf),
            "YOCTO_DEPLOY_DIR": str(yocto_deploy),
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    readme = (package_dir / "README.md").read_text(encoding="utf-8")
    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    assert "build/local-apollo-fvp" not in readme
    assert "--machine apollo-qvp" in readme
    assert f"--qboxconf {qboxconf}" in readme
    assert "--machine" in manifest["run_command"]
    assert "apollo-qvp" in manifest["run_command"]
    assert "--qboxconf" in manifest["run_command"]
    assert str(qboxconf) in manifest["run_command"]

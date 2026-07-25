from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
RUNNER: Final = ROOT / "run_qbox_local.sh"


def write_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_launch_fixture(tmp_path: Path, *, include_ukis: bool) -> tuple[Path, Path]:
    yocto_build = tmp_path / "build"
    local_build = yocto_build / "local-apollo-qvp"
    provider = (
        yocto_build
        / "tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr"
    )
    provider_bin = provider / "bin"
    provider_lib = provider / "lib"
    provider_data = provider / "share/qbox"
    native_sysroot = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0"
        / "recipe-sysroot-native"
    )
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"

    write_file(provider_bin / "platforms-vp")
    (provider_bin / "platforms-vp").chmod(0o755)
    write_file(provider_data / "platforms/apollo/apollo-qvp.lua", "return {}\n")
    (provider_lib / "qbox/modules").mkdir(parents=True)
    native_sysroot.mkdir(parents=True)
    write_file(deploy / "rse-rom.img")
    qboxconf.parent.mkdir(parents=True, exist_ok=True)
    qboxconf.write_text(
        json.dumps(
            {
                "provider": {
                    "name": "qbox-apollo-qvp-native",
                    "bindir": str(provider_bin),
                    "libdir": str(provider_lib),
                    "module_dir": str(provider_lib / "qbox/modules"),
                    "data_dir": str(provider_data),
                },
                "sysroot": {
                    "components_dir": str(
                        yocto_build / "tmp_baremetal/sysroots-components"
                    ),
                    "recipe_sysroot_native": str(native_sysroot),
                },
                "exe": "platforms-vp",
                "config": "platforms/apollo/apollo-qvp.lua",
                "images": {"rse_rom": "rse-rom.img"},
            }
        ),
        encoding="utf-8",
    )

    artifacts = (
        "deploy/boot/apollo-qvp-local-disk.img",
        "deploy/boot/boot-fat.img",
        "deploy/boot/apollo-qvp.dtb",
        "deploy/firmware/rse-rom-image.img",
        "deploy/firmware/rse-flash-image.img",
        "deploy/firmware/rse-otp-image.img",
        "deploy/firmware/ap-flash-image.img",
        "deploy/firmware/combined_provisioning_message.bin",
        "deploy/firmware/si0_ramfw.bin",
        "deploy/firmware/zephyr-demos-cl1.bin",
        "deploy/firmware/zephyr-demos-cl1.elf",
        "work/trusted-firmware-a/apollo_qvp/debug/bl2/bl2.elf",
        "work/trusted-firmware-m/bin/bl1_2.elf",
        "work/trusted-firmware-m/bin/bl2.elf",
        "debug/symbols.json",
    )
    for artifact in artifacts:
        write_file(local_build / artifact)
    if include_ukis:
        write_file(local_build / "deploy/boot/auto-ad-nexios-a.efi")
        write_file(local_build / "deploy/boot/auto-ad-nexios-b.efi")
    local_build.mkdir(parents=True, exist_ok=True)
    (local_build / "yocto-local-build-vars.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "recipes": {
                    "nexios-image": {
                        "variables": {
                            "MACHINE": "apollo-qvp",
                            "PC_CPUS_COUNT_DEFAULT": "4",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return yocto_build, local_build


def run_local_qbox(
    yocto_build: Path,
    *,
    dry_run: bool,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(RUNNER),
        "--build-dir",
        str(yocto_build),
        "--no-attach",
    ]
    if dry_run:
        command.append("--dry-run")
    env = {
        **os.environ,
        "MACHINE": "apollo-qvp",
        "TMUX_SESSION": "pytest-local-uki",
        "SSH_PORT_START": "24900",
        "SSH_PORT_END": "24999",
    }
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_runner_reports_local_uki_boot_profile(tmp_path: Path) -> None:
    yocto_build, local_build = create_launch_fixture(tmp_path, include_ukis=True)

    result = run_local_qbox(yocto_build, dry_run=True)

    assert result.returncode == 0, result.stderr
    assert "  boot_profile: local-uki-bsp" in result.stdout
    assert f"  uki_slot_a: {local_build}/deploy/boot/auto-ad-nexios-a.efi" in (
        result.stdout
    )
    assert f"  uki_slot_b: {local_build}/deploy/boot/auto-ad-nexios-b.efi" in (
        result.stdout
    )


def test_runner_rejects_missing_local_uki(tmp_path: Path) -> None:
    yocto_build, local_build = create_launch_fixture(tmp_path, include_ukis=False)

    result = run_local_qbox(yocto_build, dry_run=False)

    assert result.returncode != 0
    assert f"missing local slot A UKI: {local_build}" in result.stderr

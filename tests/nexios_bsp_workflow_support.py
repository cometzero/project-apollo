from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "yocto_build.sh"
RUN_SCRIPT = ROOT / "run_qbox_yocto.sh"


def run_build_dry_run(
    tmp_path: Path,
    args: list[str],
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "BUILD_DIR": str(tmp_path / "build"),
        }
    )
    return subprocess.run(
        [str(BUILD_SCRIPT), "--dry-run", *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_qbox_bsp_tree(tmp_path: Path) -> Path:
    yocto_build = tmp_path / "build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    work = yocto_build / "tmp_baremetal/work/apollo_qvp-poky-linux"
    components = yocto_build / "tmp_baremetal/sysroots-components"
    provider = components / "x86_64/qbox-apollo-qvp-native/usr"
    bindir = provider / "bin"
    data_dir = provider / "share/qbox"
    recipe_sysroot = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/"
        "recipe-sysroot-native"
    )

    for path in (
        deploy / "nexios-bsp-initramfs-apollo-qvp.wic",
        deploy / "efi-capsule-update-disk-image-apollo-qvp.img",
        deploy / "rse-rom-image.img",
        deploy / "rse-flash-image.img",
        deploy / "ap-flash-image.img",
        deploy / "bl2.elf",
        deploy / "combined_provisioning_message.bin",
        deploy / "apollo-qvp.dtb",
        deploy / "si0_ramfw.bin",
        deploy / "zephyr-demos-cl1.bin",
        deploy / "zephyr-demos-cl1.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl1_2.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl2.elf",
        bindir / "platforms-vp",
        data_dir / "platforms/apollo/apollo-qvp.lua",
    ):
        touch_file(path)
    (bindir / "platforms-vp").chmod(0o755)
    (deploy / "rse-otp-image.img").write_bytes(b"otp")
    (provider / "lib/qbox/modules").mkdir(parents=True)
    recipe_sysroot.mkdir(parents=True)

    qboxconf = deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    qboxconf.write_text(
        json.dumps(
            {
                "provider": {
                    "name": "qbox-apollo-qvp-native",
                    "bindir": str(bindir),
                    "libdir": str(provider / "lib"),
                    "module_dir": str(provider / "lib/qbox/modules"),
                    "data_dir": str(data_dir),
                },
                "sysroot": {
                    "components_dir": str(components),
                    "recipe_sysroot_native": str(recipe_sysroot),
                },
                "exe": "platforms-vp",
                "config": "platforms/apollo/apollo-qvp.lua",
                "images": {
                    "rootfs_wic": "nexios-bsp-initramfs-apollo-qvp.wic",
                },
                "env": {"QBOX_APOLLO_NUM_CPUS": "4"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return yocto_build


def run_qbox_bsp_dry_run(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    yocto_build = create_qbox_bsp_tree(tmp_path)
    env = os.environ.copy()
    for name in (
        "DEPLOY_DIR",
        "IMAGE_BASENAME",
        "LOCAL_BUILD_DIR",
        "QBOX_BUILD_DIR",
        "QBOX_CONF",
        "QBOX_CONF_FILE",
        "YOCTO_BUILD_DIR",
        "YOCTO_WORK_DIR",
    ):
        env.pop(name, None)
    return subprocess.run(
        [
            str(RUN_SCRIPT),
            "--build-dir",
            str(yocto_build),
            "--bsp",
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def runner_argv(output: str) -> list[str]:
    lines = output.splitlines()
    marker_index = lines.index("Headless QBox runner command:")
    return shlex.split(lines[marker_index + 1])

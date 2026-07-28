from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_yocto.sh"


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_yocto_tree(tmp_path: Path) -> tuple[Path, Path]:
    yocto_build = tmp_path / "build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    work = yocto_build / "tmp_baremetal/work/apollo_qvp-poky-linux"
    provider = (
        yocto_build
        / "tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr"
    )
    bindir = provider / "bin"
    libdir = provider / "lib"
    data_dir = provider / "share/qbox"
    module_dir = libdir / "qbox/modules"
    recipe_sysroot = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0"
        / "recipe-sysroot-native"
    )

    for path in (
        deploy / "nexios-bsp-initramfs-apollo-qvp.wic",
        deploy / "efi-capsule-update-disk-image-apollo-qvp.img",
        deploy / "rse-rom-image.img",
        deploy / "rse-flash-image.img",
        deploy / "rse-otp-image.img",
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
    (deploy / "rse-otp-image.img").write_bytes(b"otp")
    (bindir / "platforms-vp").chmod(0o755)
    module_dir.mkdir(parents=True)
    recipe_sysroot.mkdir(parents=True)

    qboxconf = deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    qboxconf.write_text(
        json.dumps(
            {
                "provider": {
                    "name": "qbox-apollo-qvp-native",
                    "bindir": str(bindir),
                    "libdir": str(libdir),
                    "module_dir": str(module_dir),
                    "data_dir": str(data_dir),
                },
                "sysroot": {
                    "components_dir": str(
                        yocto_build / "tmp_baremetal/sysroots-components"
                    ),
                    "recipe_sysroot_native": str(recipe_sysroot),
                },
                "exe": "platforms-vp",
                "config": "platforms/apollo/apollo-qvp.lua",
                "images": {
                    "rootfs_wic": "nexios-bsp-initramfs-apollo-qvp.wic",
                },
            }
        ),
        encoding="utf-8",
    )

    cc = shutil.which("cc")
    if cc is None:
        pytest.skip("C compiler is required for the debug ELF fixture")
    source = tmp_path / "linux.c"
    packaged_vmlinux = (
        work
        / "linux-yocto-rt/6.18.5+git/image/boot"
        / "vmlinux-6.18.5-rt3-yocto-preempt-rt"
    )
    touch_file(source, "void start_kernel(void) {}\nint main(void) { return 0; }\n")
    packaged_vmlinux.parent.mkdir(parents=True)
    subprocess.run(
        [cc, "-g", "-o", str(packaged_vmlinux), str(source)],
        check=True,
    )
    return yocto_build, packaged_vmlinux


def create_fake_tools(tmp_path: Path) -> tuple[Path, Path]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    for name in ("gdb-multiarch", "ss"):
        tool = fake_bin / name
        touch_file(tool, "#!/usr/bin/env bash\nexit 0\n")
        tool.chmod(0o755)
    fake_tmux = fake_bin / "tmux"
    touch_file(
        fake_tmux,
        "#!/usr/bin/env bash\n"
        "case \"$1\" in\n"
        "  has-session) exit 1 ;;\n"
        "  new-session) printf '%%0\\n' ;;\n"
        "  split-window) printf '%%1\\n' ;;\n"
        "esac\n",
    )
    fake_tmux.chmod(0o755)
    return fake_bin, fake_tmux


def test_linux_debug_uses_packaged_vmlinux_when_build_output_is_absent(
    tmp_path: Path,
) -> None:
    # Given: a completed QVP BSP package tree whose transient build ELF is absent.
    yocto_build, packaged_vmlinux = create_yocto_tree(tmp_path)
    fake_bin, fake_tmux = create_fake_tools(tmp_path)
    env = os.environ.copy()
    for name in (
        "DEPLOY_DIR",
        "YOCTO_WORK_DIR",
        "LOCAL_BUILD_DIR",
        "QBOX_TOOL_DIR",
        "QBOX_BUILD_DIR",
        "QBOX_CONF",
        "QBOX_CONF_FILE",
        "OUT_DIR",
    ):
        env.pop(name, None)
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "TMUX_BIN": str(fake_tmux),
            "OUT_DIR": str(tmp_path / "out"),
            "SSH_PORT_START": "25500",
            "SSH_PORT_END": "25599",
        }
    )

    # When: Linux debugging is prepared through the real Yocto launcher.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--build-dir",
            str(yocto_build),
            "--bsp",
            "--debug",
            "linux",
            "--multi-session",
            "--no-attach",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the packaged debug ELF is selected instead of rejecting the run.
    assert result.returncode == 0, result.stderr
    assert f"  debug ELF:     {packaged_vmlinux}" in result.stdout

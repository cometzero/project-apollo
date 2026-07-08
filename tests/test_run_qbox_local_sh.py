from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_local.sh"


REMOVED_SURFACES = (
    "rse_cpu_mode",
    "--rse-cpu-mode",
    "--remotepass-dmi-cache",
    "--rse-hotpath-tlm-fallback",
    "RSE_CPU_MODE",
    "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK",
    "REMOTEPASS_DMI_CACHE",
)


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    local_build_dir = tmp_path / "local-build"
    out_dir = tmp_path / "out"
    qbox_platform_dir = tmp_path / "qbox-platform"
    conf = qbox_platform_dir / "platforms/apollo/apollo-qvp.lua"
    local_build_dir.mkdir()
    conf.parent.mkdir(parents=True)
    conf.write_text("return {}\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "LOCAL_BUILD_DIR": str(local_build_dir),
            "OUT_DIR": str(out_dir),
            "QBOX_PLATFORM_DIR": str(qbox_platform_dir),
            "QBOX_CONF": str(conf),
            "MACHINE": "apollo-fvp",
            "TMUX_SESSION": "pytest-run-qbox",
            "SSH_PORT_START": "24500",
            "SSH_PORT_END": "24599",
        }
    )
    if extra_env:
        env.update(extra_env)

    command = [str(SCRIPT), "--dry-run", "--no-attach", *(extra_args or [])]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def touch_file(path: Path, content: str | bytes = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def create_qvp_qboxconf(yocto_build: Path, deploy: Path) -> Path:
    provider_root = (
        yocto_build
        / "tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr"
    )
    bindir = provider_root / "bin"
    libdir = provider_root / "lib"
    module_dir = libdir / "qbox/modules"
    data_dir = provider_root / "share/qbox"
    recipe_sysroot_native = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/recipe-sysroot-native"
    )
    touch_file(bindir / "platforms-vp")
    (bindir / "platforms-vp").chmod(0o755)
    touch_file(data_dir / "platforms/apollo/apollo-qvp.lua", "return {}\n")
    module_dir.mkdir(parents=True, exist_ok=True)
    recipe_sysroot_native.mkdir(parents=True, exist_ok=True)

    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    payload = {
        "provider": {
            "name": "qbox-apollo-qvp-native",
            "bindir": str(bindir),
            "libdir": str(libdir),
            "module_dir": str(module_dir),
            "data_dir": str(data_dir),
        },
        "sysroot": {
            "components_dir": str(yocto_build / "tmp_baremetal/sysroots-components"),
            "recipe_sysroot_native": str(recipe_sysroot_native),
        },
        "exe": "platforms-vp",
        "config": "platforms/apollo/apollo-qvp.lua",
        "images": {
            "rse_rom": "qboxconf-rse-rom.img",
        },
    }
    qboxconf.parent.mkdir(parents=True, exist_ok=True)
    qboxconf.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    touch_file(deploy / "qboxconf-rse-rom.img")
    return qboxconf


def create_local_artifacts(local_build_dir: Path) -> None:
    for path in (
        local_build_dir / "deploy/boot/apollo-fvp-local-disk.img",
        local_build_dir / "deploy/boot/boot-fat.img",
        local_build_dir / "deploy/boot/apollo-fvp.dtb",
        local_build_dir / "deploy/firmware/rse-rom-image.img",
        local_build_dir / "deploy/firmware/rse-flash-image.img",
        local_build_dir / "deploy/firmware/rse-otp-image.img",
        local_build_dir / "deploy/firmware/ap-flash-image.img",
        local_build_dir / "deploy/firmware/combined_provisioning_message.bin",
        local_build_dir / "deploy/firmware/si0_ramfw.bin",
        local_build_dir / "deploy/firmware/zephyr-demos-cl1.bin",
        local_build_dir / "deploy/firmware/zephyr-demos-cl1.elf",
        local_build_dir / "work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf",
        local_build_dir / "work/trusted-firmware-m/bin/bl1_2.elf",
        local_build_dir / "work/trusted-firmware-m/bin/bl2.elf",
        local_build_dir / "debug/symbols.json",
    ):
        touch_file(path)


def run_qvp_local_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    yocto_build = tmp_path / "build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    local_build_dir = yocto_build / "local-apollo-qvp"
    create_qvp_qboxconf(yocto_build, deploy)
    create_local_artifacts(local_build_dir)

    env = os.environ.copy()
    for name in (
        "LOCAL_BUILD_DIR",
        "QBOX_PLATFORM_DIR",
        "QBOX_CONF",
        "QBOX_CONF_FILE",
        "QBOX_BUILD_DIR",
        "QBOX_PLATFORM_BUILD_DIR",
        "ROOTFS",
        "EFI_CAPSULE_DISK",
    ):
        env.pop(name, None)
    env.update(
        {
            "MACHINE": "apollo-qvp",
            "TMUX_SESSION": "pytest-run-qbox-local-qvp",
            "SSH_PORT_START": "24700",
            "SSH_PORT_END": "24799",
        }
    )
    if extra_env:
        env.update(extra_env)

    command = [
        str(SCRIPT),
        "--build-dir",
        str(yocto_build),
        "--dry-run",
        "--no-attach",
        *(extra_args or []),
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def dry_run_command_argv(output: str) -> list[str]:
    for line in output.splitlines():
        if line.strip().startswith("command: "):
            return shlex.split(line.split("command: ", maxsplit=1)[1])
    raise AssertionError(output)


def test_run_qbox_dry_run_omits_removed_remote_surfaces(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    for surface in REMOVED_SURFACES:
        assert surface not in result.stdout
        assert surface not in result.stderr


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (
            ["--rse-cpu-mode", "remote"],
            "unsupported removed option: --rse-cpu-mode",
        ),
        (
            ["--rse-hotpath-tlm-fallback"],
            "unsupported removed option: --rse-hotpath-tlm-fallback",
        ),
        (
            ["--no-rse-hotpath-tlm-fallback"],
            "unsupported removed option: --no-rse-hotpath-tlm-fallback",
        ),
        (
            ["--remotepass-dmi-cache"],
            "unsupported removed option: --remotepass-dmi-cache",
        ),
    ],
)
def test_run_qbox_rejects_removed_options(
    tmp_path: Path,
    args: list[str],
    message: str,
) -> None:
    result = run_dry_run(tmp_path, extra_args=args)

    assert result.returncode != 0
    assert message in result.stderr


@pytest.mark.parametrize(
    "name",
    [
        "RSE_CPU_MODE",
        "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK",
        "REMOTEPASS_DMI_CACHE",
    ],
)
def test_run_qbox_rejects_removed_environment_overrides(tmp_path: Path, name: str) -> None:
    result = run_dry_run(tmp_path, extra_env={name: "1"})

    assert result.returncode != 0
    assert f"unsupported removed environment override: {name}" in result.stderr


def test_run_qbox_rejects_unrelated_invalid_option(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, extra_args=["--not-a-real-option"])

    assert result.returncode != 0
    assert "unknown argument: --not-a-real-option" in result.stderr


def test_run_qbox_local_qvp_uses_qboxconf_provider_and_local_initramfs_disk(
    tmp_path: Path,
) -> None:
    result = run_qvp_local_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    yocto_build = tmp_path / "build"
    local_build_dir = yocto_build / "local-apollo-qvp"
    provider_root = (
        yocto_build
        / "tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr"
    )
    argv = dry_run_command_argv(result.stdout)
    assert f"qboxconf: {yocto_build / 'tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.qboxconf'}" in result.stdout
    assert argv[argv.index("--qbox-build-dir") + 1] == str(provider_root / "bin")
    assert argv[argv.index("--conf") + 1] == str(
        provider_root / "share/qbox/platforms/apollo/apollo-qvp.lua"
    )
    assert argv[argv.index("--rootfs") + 1] == str(
        local_build_dir / "deploy/boot/apollo-fvp-local-disk.img"
    )
    assert "nexios-image-apollo-qvp.wic" not in result.stdout
    assert ".verity" not in result.stdout
    assert "tmux_layout: fvp-like" in result.stdout
    assert argv[argv.index("--primary-login-prompt") + 1] == "apollo-qvp login:"
    assert "--rse-rom" in argv
    assert "--rse-flash" in argv
    assert "--rse-otp" in argv
    assert "--ap-flash" in argv
    assert "--ap-bl2-elf" in argv
    assert "--rse-bl1-2-elf" in argv
    assert "--rse-bl2-elf" in argv
    assert "--provisioning-bundle" in argv
    assert "--ap-dtb" in argv
    assert "--si-cl0-image" in argv
    assert "--si-cl1-image" in argv
    assert "--si-cl1-symbols" in argv
    assert "--rse-symbols" in argv


def test_run_qbox_local_qvp_rejects_missing_qboxconf(tmp_path: Path) -> None:
    yocto_build = tmp_path / "build"
    (yocto_build / "tmp_baremetal/deploy/images/apollo-qvp").mkdir(parents=True)
    (yocto_build / "local-apollo-qvp").mkdir(parents=True)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--dry-run",
            "--no-attach",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-local-qvp-missing",
            "SSH_PORT_START": "24800",
            "SSH_PORT_END": "24899",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "missing required QBox qboxconf" in result.stderr


def test_run_qbox_local_explicit_rootfs_and_efi_override_qboxconf_defaults(
    tmp_path: Path,
) -> None:
    explicit_rootfs = tmp_path / "explicit-rootfs.img"
    explicit_efi = tmp_path / "explicit-efi.img"
    touch_file(explicit_rootfs)
    touch_file(explicit_efi)

    result = run_qvp_local_dry_run(
        tmp_path,
        extra_args=[
            "--rootfs",
            str(explicit_rootfs),
            "--efi-capsule-disk",
            str(explicit_efi),
        ],
    )

    assert result.returncode == 0, result.stderr
    argv = dry_run_command_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1] == str(explicit_rootfs)
    assert argv[argv.index("--efi-capsule-disk") + 1] == str(explicit_efi)

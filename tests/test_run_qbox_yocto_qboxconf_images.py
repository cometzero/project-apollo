from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_yocto.sh"


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_provider(yocto_build: Path) -> dict[str, str]:
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
    return {
        "bindir": str(bindir),
        "libdir": str(libdir),
        "module_dir": str(module_dir),
        "data_dir": str(data_dir),
        "recipe_sysroot_native": str(recipe_sysroot_native),
    }


def create_deploy_artifacts(deploy: Path, work: Path) -> None:
    for path in (
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
    ):
        touch_file(path)
    (deploy / "rse-otp-image.img").write_bytes(b"otp")


def write_qboxconf(
    qboxconf: Path,
    yocto_build: Path,
    images: dict[str, str],
) -> None:
    provider = create_provider(yocto_build)
    payload = {
        "provider": {
            "name": "qbox-apollo-qvp-native",
            "bindir": provider["bindir"],
            "libdir": provider["libdir"],
            "module_dir": provider["module_dir"],
            "data_dir": provider["data_dir"],
        },
        "sysroot": {
            "components_dir": str(yocto_build / "tmp_baremetal/sysroots-components"),
            "recipe_sysroot_native": provider["recipe_sysroot_native"],
        },
        "exe": "platforms-vp",
        "config": "platforms/apollo/apollo-qvp.lua",
        "images": images,
    }
    qboxconf.parent.mkdir(parents=True, exist_ok=True)
    qboxconf.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def create_tree(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    yocto_build = tmp_path / "build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    work = yocto_build / "tmp_baremetal/work/apollo_qvp-poky-linux"
    imgdeploy = work / "nexios-image/1.0/deploy-nexios-image-image-complete"
    create_deploy_artifacts(deploy, work)
    return yocto_build, deploy, work, imgdeploy


def run_script(
    yocto_build: Path,
    *,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    clean_env = os.environ.copy()
    for name in (
        "DEPLOY_DIR",
        "YOCTO_WORK_DIR",
        "LOCAL_BUILD_DIR",
        "QBOX_TOOL_DIR",
        "QBOX_BUILD_DIR",
        "QBOX_CONF",
        "QBOX_CONF_FILE",
        "ROOTFS",
        "EFI_CAPSULE_DISK",
    ):
        clean_env.pop(name, None)
    clean_env.update(
        {
            "TMUX_SESSION": "pytest-qboxconf-images",
            "SSH_PORT_START": "25500",
            "SSH_PORT_END": "25599",
        }
    )
    if env:
        clean_env.update(env)
    command = [
        str(SCRIPT),
        "--machine",
        "apollo-qvp",
        "--build-dir",
        str(yocto_build),
        "--headless",
        "--dry-run",
        *(args or []),
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=clean_env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def dry_run_argv(output: str) -> list[str]:
    lines = output.splitlines()
    index = lines.index("Headless QBox runner command:")
    return shlex.split(lines[index + 1])


def test_qboxconf_images_with_non_default_names_are_used_by_dry_run(
    tmp_path: Path,
) -> None:
    # Given: qboxconf names a WIC artifact that does not match deploy defaults.
    yocto_build, deploy, _work, _imgdeploy = create_tree(tmp_path)
    custom_rootfs = deploy / "custom-rootfs.wic"
    touch_file(custom_rootfs)
    write_qboxconf(
        deploy / "nexios-image-apollo-qvp.qboxconf",
        yocto_build,
        {"wic": custom_rootfs.name},
    )

    # When: the runner is driven through the public dry-run surface.
    result = run_script(yocto_build)

    # Then: the qboxconf image contract supplies the rootfs path.
    assert result.returncode == 0, result.stderr
    argv = dry_run_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1] == str(custom_rootfs)


def test_explicit_cli_and_env_overrides_win_over_qboxconf_images(
    tmp_path: Path,
) -> None:
    # Given: qboxconf image defaults and explicit operator overrides.
    yocto_build, deploy, _work, _imgdeploy = create_tree(tmp_path)
    qboxconf_rootfs = deploy / "qboxconf-rootfs.wic"
    explicit_rootfs = deploy / "explicit-rootfs.wic"
    env_efi = deploy / "env-efi.img"
    for path in (qboxconf_rootfs, explicit_rootfs, env_efi):
        touch_file(path)
    write_qboxconf(
        deploy / "nexios-image-apollo-qvp.qboxconf",
        yocto_build,
        {
            "rootfs_wic": qboxconf_rootfs.name,
            "efi_capsule_disk": "qboxconf-efi.img",
        },
    )

    # When: CLI rootfs and environment EFI overrides are supplied.
    result = run_script(
        yocto_build,
        args=["--rootfs", str(explicit_rootfs)],
        env={"EFI_CAPSULE_DISK": str(env_efi)},
    )

    # Then: explicit values are passed to the child runner.
    assert result.returncode == 0, result.stderr
    argv = dry_run_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1] == str(explicit_rootfs)
    assert argv[argv.index("--efi-capsule-disk") + 1] == str(env_efi)


def test_default_qvp_dry_run_discovers_imgdeploy_qboxconf_fallback(
    tmp_path: Path,
) -> None:
    # Given: final deploy has no qboxconf, but targeted do_write_qboxboot_conf output exists.
    yocto_build, _deploy, _work, imgdeploy = create_tree(tmp_path)
    timestamped_rootfs = imgdeploy / "nexios-image-apollo-qvp-20260707142156.wic"
    touch_file(timestamped_rootfs)
    qboxconf = imgdeploy / "nexios-image-apollo-qvp-20260707142156.qboxconf"
    write_qboxconf(
        qboxconf,
        yocto_build,
        {"rootfs_wic": "nexios-image-apollo-qvp.wic"},
    )

    # When: no --qboxconf override is supplied.
    result = run_script(yocto_build)

    # Then: default discovery finds IMGDEPLOYDIR qboxconf and timestamped WIC.
    assert result.returncode == 0, result.stderr
    assert f"qboxconf:      {qboxconf}" in result.stdout
    argv = dry_run_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1] == str(timestamped_rootfs)


def test_imgdeploy_timestamped_rootfs_wins_over_stale_final_deploy_fixed(
    tmp_path: Path,
) -> None:
    # Given: IMGDEPLOYDIR qboxconf names the fixed rootfs, but only its
    # timestamped sibling exists there while final deploy has a stale fixed WIC.
    yocto_build, deploy, _work, imgdeploy = create_tree(tmp_path)
    timestamped_rootfs = imgdeploy / "nexios-image-apollo-qvp-20260707142156.wic"
    stale_rootfs = deploy / "nexios-image-apollo-qvp.wic"
    for path in (timestamped_rootfs, stale_rootfs):
        touch_file(path)
    write_qboxconf(
        imgdeploy / "nexios-image-apollo-qvp.qboxconf",
        yocto_build,
        {"rootfs_wic": "nexios-image-apollo-qvp.wic"},
    )

    # When: the default qboxconf image resolver runs through dry-run.
    result = run_script(yocto_build)

    # Then: qboxconf-local timestamped WIC is exhausted before final deploy.
    assert result.returncode == 0, result.stderr
    argv = dry_run_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1] == str(timestamped_rootfs)


def test_explicit_missing_qboxconf_fails_clearly(tmp_path: Path) -> None:
    # Given: an operator points directly at a missing qboxconf.
    yocto_build, _deploy, _work, _imgdeploy = create_tree(tmp_path)
    missing = tmp_path / "missing.qboxconf"

    # When: the runner is invoked with the explicit missing file.
    result = run_script(yocto_build, args=["--qboxconf", str(missing)])

    # Then: it fails on that file instead of falling back to defaults.
    assert result.returncode != 0
    assert f"qboxconf not found: {missing}" in result.stderr

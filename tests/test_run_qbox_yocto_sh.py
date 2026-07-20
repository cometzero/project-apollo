from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_yocto.sh"
TMUX_SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
QBOX_YOCTO_ENV_OVERRIDES = (
    "YOCTO_BUILD_DIR",
    "DEPLOY_DIR",
    "YOCTO_WORK_DIR",
    "LOCAL_BUILD_DIR",
    "QBOX_TOOL_DIR",
    "QBOX_BUILD_DIR",
    "QBOX_PLATFORM_BUILD_DIR",
    "QBOX_CONF",
    "QBOX_CONF_FILE",
    "QBOX_APOLLO_NUM_CPUS",
    "OUT_DIR",
    "QBOX_RSE_STATE_DIR",
    "QBOX_PERSIST_RSE_STATE",
)


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_qboxconf(
    yocto_build: Path,
    deploy: Path,
    *,
    machine: str = "apollo-qvp",
    basename: str = "nexios-image",
    include_debug_symbols: bool = False,
    ap_cpu_count: str | None = None,
) -> Path:
    components_dir = yocto_build / "tmp_baremetal/sysroots-components/x86_64"
    provider_root = components_dir / "qbox-apollo-qvp-native/usr"
    bindir = provider_root / "bin"
    libdir = provider_root / "lib"
    module_dir = libdir / "qbox"
    data_dir = provider_root / "share/qbox"
    recipe_sysroot_native = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/recipe-sysroot-native"
    )

    touch_file(bindir / "platforms-vp")
    (bindir / "platforms-vp").chmod(0o755)
    touch_file(module_dir / "libqbox-apollo.so")
    touch_file(data_dir / "platforms/apollo/apollo-qvp.lua", "return {}\n")
    recipe_sysroot_native.mkdir(parents=True)

    qboxconf = deploy / f"{basename}-{machine}.qboxconf"
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
            "wic": f"{basename}-{machine}.wic",
            "efi_capsule_disk": f"efi-capsule-update-disk-image-{machine}.img",
        },
        "env": {
            "LD_LIBRARY_PATH": "${provider.libdir}:${provider.module_dir}",
        },
    }
    if ap_cpu_count is not None:
        payload["env"]["QBOX_APOLLO_NUM_CPUS"] = ap_cpu_count
    if include_debug_symbols:
        touch_file(data_dir / "debug/symbols.json", "{}\n")
        payload["debug_symbols"] = str(data_dir / "debug/symbols.json")
    qboxconf.parent.mkdir(parents=True, exist_ok=True)
    qboxconf.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return qboxconf


def rewrite_qboxconf(qboxconf: Path, payload: dict) -> None:
    qboxconf.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def create_yocto_tree(
    tmp_path: Path,
    *,
    machine: str = "apollo-fvp",
    build_dir_name: str = "yocto-build",
    include_qboxconf: bool = False,
) -> tuple[Path, Path, Path, Path, Path]:
    yocto_build = tmp_path / "yocto-build"
    if build_dir_name != "yocto-build":
        yocto_build = tmp_path / build_dir_name
    deploy = yocto_build / f"tmp_baremetal/deploy/images/{machine}"
    work = yocto_build / f"tmp_baremetal/work/{machine.replace('-', '_')}-poky-linux"
    local_build = tmp_path / "local-build"
    qbox_build = local_build / "work/qbox-platform"

    for path in (
        deploy / f"nexios-image-{machine}.wic",
        deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        deploy / "rse-rom-image.img",
        deploy / "rse-flash-image.img",
        deploy / "rse-otp-image.img",
        deploy / "ap-flash-image.img",
        deploy / "bl2.elf",
        deploy / "combined_provisioning_message.bin",
        deploy / f"{machine}.dtb",
        deploy / "si0_ramfw.bin",
        deploy / "zephyr-demos-cl1.bin",
        deploy / "zephyr-demos-cl1.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl1_2.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl2.elf",
        local_build / "debug/symbols.json",
    ):
        touch_file(path)
    if machine != "apollo-fvp":
        touch_file(deploy / f"efi-capsule-update-disk-image-{machine}.img")
    if machine == "apollo-qvp":
        (deploy / "rse-otp-image.img").write_bytes(b"otp")
    else:
        (deploy / "rse-otp-image.img").write_bytes(b"")
    qbox_build.mkdir(parents=True)

    conf = tmp_path / "qbox-platform/platforms/apollo/apollo-qvp.lua"
    touch_file(conf, "return {}\n")
    if include_qboxconf:
        create_qboxconf(yocto_build, deploy, machine=machine)
    return yocto_build, deploy, work, local_build, conf


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    yocto_build, _deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    out_dir = tmp_path / "out"

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "MACHINE": "apollo-fvp",
            "OUT_DIR": str(out_dir),
            "TMUX_SESSION": "pytest-run-qbox-yocto",
            "SSH_PORT_START": "24600",
            "SSH_PORT_END": "24699",
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


def run_qvp_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
    ap_cpu_count: str | None = None,
) -> subprocess.CompletedProcess[str]:
    yocto_build, _deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )

    if ap_cpu_count is not None:
        qboxconf = _deploy / "nexios-image-apollo-qvp.qboxconf"
        payload = json.loads(qboxconf.read_text(encoding="utf-8"))
        payload["env"]["QBOX_APOLLO_NUM_CPUS"] = ap_cpu_count
        rewrite_qboxconf(qboxconf, payload)

    env = os.environ.copy()
    for name in QBOX_YOCTO_ENV_OVERRIDES:
        env.pop(name, None)
    env.update(
        {
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp",
            "SSH_PORT_START": "24900",
            "SSH_PORT_END": "24999",
        }
    )
    if extra_env:
        env.update(extra_env)

    command = [
        str(SCRIPT),
        "--build-dir",
        str(yocto_build),
        "--headless",
        "--dry-run",
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
    lines = output.splitlines()
    marker = "Headless QBox runner command:"
    index = lines.index(marker)
    return shlex.split(lines[index + 1])


def test_run_qbox_yocto_dry_run_maps_yocto_artifacts(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Apollo QBox Yocto launch" in result.stdout
    assert "tmux_layout: fvp-like" in result.stdout
    assert f"qbox_core_dir: {ROOT / 'hsoc-stack/tools/qbox'}" in result.stdout
    assert (
        f"qbox_platform_dir: {ROOT / 'hsoc-stack/tools/qbox-platform'}"
        in result.stdout
    )
    assert "ap cpus:       4" in result.stdout
    assert "--rootfs" in result.stdout
    assert "nexios-image-apollo-fvp.wic" in result.stdout
    assert "--efi-capsule-disk" in result.stdout
    assert "efi-capsule-update-disk-image-fvp-rd-aspen.img" in result.stdout
    assert "--rse-rom" in result.stdout
    assert "rse-rom-image.img" in result.stdout
    assert "input-images/rse-otp-image.img" in result.stdout
    assert "--ap-flash" in result.stdout
    assert "ap-flash-image.img" in result.stdout
    assert "--rse-symbols" in result.stdout
    assert "debug/symbols.json" in result.stdout
    assert "--qbox-performance-preset" in result.stdout
    assert "--cc3xx-qemu-native-backend" in result.stdout
    assert "type=user,hostfwd=tcp::" in result.stdout


def test_run_qbox_yocto_qvp_uses_qboxconf_sysroot_defaults(tmp_path: Path) -> None:
    # Given: Yocto-style apollo-qvp deploy artifacts with qboxconf/sysroot provider paths.
    result = run_qvp_dry_run(tmp_path)

    # Then: the launcher uses qvp deploy names and the qboxconf provider paths.
    assert result.returncode == 0, result.stderr
    deploy = tmp_path / "build/tmp_baremetal/deploy/images/apollo-qvp"
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    provider_root = (
        tmp_path
        / "build/tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr"
    )
    bindir = provider_root / "bin"
    data_dir = provider_root / "share/qbox"
    assert f"deploy dir:    {deploy}" in result.stdout
    assert f"qboxconf:      {qboxconf}" in result.stdout
    assert f"qbox tools:    {bindir}" in result.stdout
    assert f"qbox conf:     {data_dir / 'platforms/apollo/apollo-qvp.lua'}" in result.stdout
    argv = dry_run_command_argv(result.stdout)
    assert argv[argv.index("--qbox-build-dir") + 1] == str(bindir)
    assert "build/qbox-apollo-qvp/yocto-apollo-qvp-" in result.stdout
    assert "nexios-image-apollo-qvp.wic" in result.stdout
    assert "efi-capsule-update-disk-image-apollo-qvp.img" in result.stdout
    assert "apollo-qvp.dtb" in result.stdout
    assert "--rse-symbols" not in argv
    state_index = argv.index("--rse-flash-state")
    assert argv[state_index + 1] == str(
        ROOT / "build/qbox-apollo-fvp/state/yocto-apollo-qvp/rse-flash-image.img"
    )


def test_run_qbox_yocto_qvp_uses_qboxconf_ap_cpu_count(tmp_path: Path) -> None:
    result = run_qvp_dry_run(tmp_path, ap_cpu_count="16")

    assert result.returncode == 0, result.stderr
    assert "ap cpus:       16" in result.stdout


def test_run_qbox_yocto_qvp_explicit_ap_cpu_count_wins(tmp_path: Path) -> None:
    result = run_qvp_dry_run(
        tmp_path,
        extra_env={"QBOX_APOLLO_NUM_CPUS": "8"},
        ap_cpu_count="16",
    )

    assert result.returncode == 0, result.stderr
    assert "ap cpus:       8" in result.stdout


def test_run_qbox_yocto_qvp_rejects_invalid_qboxconf_ap_cpu_count(
    tmp_path: Path,
) -> None:
    result = run_qvp_dry_run(tmp_path, ap_cpu_count="17")

    assert result.returncode != 0
    assert "env.QBOX_APOLLO_NUM_CPUS must be in range 1..16" in result.stderr


def test_run_qbox_yocto_skips_initial_state_manifest_by_default(
    tmp_path: Path,
) -> None:
    result = run_qvp_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "initial state:  skipped" in result.stdout


def test_run_qbox_yocto_can_record_initial_state_manifest(tmp_path: Path) -> None:
    result = run_qvp_dry_run(tmp_path, extra_args=["--record-initial-state"])

    assert result.returncode == 0, result.stderr
    assert "initial state:  SHA-256 manifest" in result.stdout
    assert "--record-initial-state" not in dry_run_command_argv(result.stdout)


def test_run_qbox_yocto_qvp_can_reset_custom_rse_state(tmp_path: Path) -> None:
    state_dir = tmp_path / "qbox-state"
    result = run_qvp_dry_run(
        tmp_path,
        extra_args=["--rse-state-dir", str(state_dir), "--reset-rse-state"],
    )

    assert result.returncode == 0, result.stderr
    argv = dry_run_command_argv(result.stdout)
    state_index = argv.index("--rse-flash-state")
    assert argv[state_index + 1] == str(state_dir / "rse-flash-image.img")
    assert "--reset-rse-flash-state" in argv


def test_run_qbox_yocto_qvp_uses_latest_qboxconf_when_link_is_absent(
    tmp_path: Path,
) -> None:
    # Given: versioned deploy qboxconf files without the image-link qboxconf.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    fixed = deploy / "nexios-image-apollo-qvp.qboxconf"
    older = deploy / "nexios-image-apollo-qvp-20260101000000.qboxconf"
    newer = deploy / "nexios-image-apollo-qvp-20260201000000.qboxconf"
    older.write_text(fixed.read_text(encoding="utf-8"), encoding="utf-8")
    newer.write_text(fixed.read_text(encoding="utf-8"), encoding="utf-8")
    fixed.unlink()
    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    # When: the QVP runner resolves qboxconf from deploy defaults.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-latest-qboxconf",
            "SSH_PORT_START": "25300",
            "SSH_PORT_END": "25399",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the newest versioned qboxconf is selected.
    assert result.returncode == 0, result.stderr
    assert f"qboxconf:      {newer}" in result.stdout


def test_run_qbox_yocto_qvp_requires_qvp_efi_capsule_name(
    tmp_path: Path,
) -> None:
    # Given: a QVP deploy tree with only the inherited RD-Aspen EFI disk name.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    (deploy / "efi-capsule-update-disk-image-apollo-qvp.img").unlink()

    # When: the QVP runner resolves artifacts from the deploy directory.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-missing-efi",
            "SSH_PORT_START": "25000",
            "SSH_PORT_END": "25099",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the missing QVP deploy-visible name is not masked by an FVP alias.
    assert result.returncode != 0
    assert "missing required EFI capsule update disk" in result.stderr
    assert "efi-capsule-update-disk-image-apollo-qvp.img" in result.stderr


def test_run_qbox_yocto_qvp_uses_qboxconf_debug_symbols_when_present(
    tmp_path: Path,
) -> None:
    # Given: a qboxconf that explicitly names a deployed RSE debug manifest.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
    )
    qboxconf = create_qboxconf(
        yocto_build,
        deploy,
        machine="apollo-qvp",
        include_debug_symbols=True,
    )
    payload = json.loads(qboxconf.read_text(encoding="utf-8"))

    # When: the QVP runner resolves artifacts from qboxconf metadata.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-debug-symbols",
            "SSH_PORT_START": "25000",
            "SSH_PORT_END": "25099",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the explicit debug manifest remains part of the child command.
    assert result.returncode == 0, result.stderr
    argv = dry_run_command_argv(result.stdout)
    assert argv[argv.index("--rse-symbols") + 1] == payload["debug_symbols"]


def test_run_qbox_yocto_qvp_allows_explicit_efi_override(tmp_path: Path) -> None:
    # Given: a QVP deploy tree with an explicit compatibility artifact override.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    qvp_efi = deploy / "efi-capsule-update-disk-image-apollo-qvp.img"
    qvp_efi.unlink()
    explicit_efi = deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img"

    # When: the operator explicitly provides the alternate EFI disk.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--efi-capsule-disk",
            str(explicit_efi),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-explicit-efi",
            "SSH_PORT_START": "25000",
            "SSH_PORT_END": "25099",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: explicit operator override is accepted and visible in the command.
    assert result.returncode == 0, result.stderr
    assert str(explicit_efi) in result.stdout


def test_run_qbox_yocto_qvp_rejects_missing_qboxconf(tmp_path: Path) -> None:
    # Given: QVP image artifacts without a deployed qboxconf.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
    )

    # When: the QVP runner resolves its default QBox tools.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-missing-qboxconf",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it fails on the missing qboxconf instead of falling back to local FVP QBox.
    assert result.returncode != 0
    assert "missing required QBox qboxconf" in result.stderr
    assert str(deploy / "nexios-image-apollo-qvp.qboxconf") in result.stderr


def test_run_qbox_yocto_qvp_rejects_malformed_qboxconf(tmp_path: Path) -> None:
    # Given: QVP image artifacts and a malformed qboxconf.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
    )
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    touch_file(qboxconf, '{"provider": ')

    # When: the QVP runner parses qboxconf before resolving provider paths.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-bad-qboxconf",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: malformed JSON is reported clearly and no stale provider fallback is used.
    assert result.returncode != 0
    assert f"invalid qboxconf JSON: {qboxconf}" in result.stderr


def test_run_qbox_yocto_qvp_rejects_provider_path_outside_build(
    tmp_path: Path,
) -> None:
    # Given: an otherwise valid QVP qboxconf whose provider paths point outside the Yocto build.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    payload = json.loads(qboxconf.read_text(encoding="utf-8"))
    evil_root = tmp_path / "evil/qbox-apollo-qvp-native/usr"
    touch_file(evil_root / "bin/platforms-vp")
    (evil_root / "bin/platforms-vp").chmod(0o755)
    touch_file(evil_root / "share/qbox/platforms/apollo/apollo-qvp.lua", "return {}\n")
    (evil_root / "lib/qbox").mkdir(parents=True)
    payload["provider"]["bindir"] = str(evil_root / "bin")
    payload["provider"]["libdir"] = str(evil_root / "lib")
    payload["provider"]["module_dir"] = str(evil_root / "lib/qbox")
    payload["provider"]["data_dir"] = str(evil_root / "share/qbox")
    rewrite_qboxconf(qboxconf, payload)

    # When: the QVP runner parses qboxconf before command emission.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-evil-provider",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the qboxconf is rejected before the child runner command is printed.
    assert result.returncode != 0
    assert "qboxconf trust error" in result.stderr
    assert "provider.bindir" in result.stderr
    assert "Headless QBox runner command:" not in result.stdout


def test_run_qbox_yocto_qvp_rejects_provider_symlink_escape(
    tmp_path: Path,
) -> None:
    # Given: provider paths appear under sysroots-components but resolve outside via symlink.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    component_root = (
        yocto_build
        / "tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native"
    )
    evil_component = tmp_path / "evil-component"
    touch_file(evil_component / "usr/bin/platforms-vp")
    (evil_component / "usr/bin/platforms-vp").chmod(0o755)
    touch_file(evil_component / "usr/share/qbox/platforms/apollo/apollo-qvp.lua", "return {}\n")
    (evil_component / "usr/lib/qbox").mkdir(parents=True)
    shutil.rmtree(component_root)
    component_root.symlink_to(evil_component, target_is_directory=True)

    # When: the QVP runner parses qboxconf before command emission.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-symlink-provider",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: realpath validation rejects the symlink escape before command print.
    assert result.returncode != 0
    assert "qboxconf trust error" in result.stderr
    assert "provider.bindir" in result.stderr
    assert "Headless QBox runner command:" not in result.stdout


def test_run_qbox_yocto_qvp_rejects_sysroot_path_outside_build(
    tmp_path: Path,
) -> None:
    # Given: an otherwise valid QVP qboxconf with a recipe sysroot outside tmp_baremetal/work.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    payload = json.loads(qboxconf.read_text(encoding="utf-8"))
    evil_sysroot = tmp_path / "evil-recipe-sysroot-native"
    evil_sysroot.mkdir()
    payload["sysroot"]["recipe_sysroot_native"] = str(evil_sysroot)
    rewrite_qboxconf(qboxconf, payload)

    # When: the QVP runner parses qboxconf before command emission.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-evil-sysroot",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: sysroot trust validation rejects it before the child runner command is printed.
    assert result.returncode != 0
    assert "qboxconf trust error" in result.stderr
    assert "sysroot.recipe_sysroot_native" in result.stderr
    assert "Headless QBox runner command:" not in result.stdout


def test_run_qbox_yocto_qvp_rejects_missing_provider_executable(
    tmp_path: Path,
) -> None:
    # Given: QVP deploy artifacts with a qboxconf whose provider executable is missing.
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    qboxconf = deploy / "nexios-image-apollo-qvp.qboxconf"
    payload = json.loads(qboxconf.read_text(encoding="utf-8"))
    provider_exe = Path(payload["provider"]["bindir"]) / payload["exe"]
    provider_exe.unlink()

    # When: the QVP runner resolves provider paths from qboxconf.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-missing-provider",
            "SSH_PORT_START": "25100",
            "SSH_PORT_END": "25199",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the missing sysroot provider is fatal before the runner command is emitted.
    assert result.returncode != 0
    assert "QBox executable not found or not executable" in result.stderr
    assert str(provider_exe) in result.stderr


def test_run_qbox_yocto_qvp_rejects_empty_rse_otp(tmp_path: Path) -> None:
    yocto_build, deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    (deploy / "rse-otp-image.img").write_bytes(b"")

    result = subprocess.run(
        [
            str(SCRIPT),
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(yocto_build),
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-empty-otp",
            "SSH_PORT_START": "25200",
            "SSH_PORT_END": "25299",
        },
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "RSE OTP image is empty" in result.stderr
    assert "Rebuild firmware-apollo-qvp" in result.stderr


def test_run_qbox_yocto_passes_child_args_after_separator(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, extra_args=["--", "--check-only"])

    assert result.returncode == 0, result.stderr
    assert "--check-only" in result.stdout


def test_run_qbox_yocto_uses_fvp_like_tmux_splits(tmp_path: Path) -> None:
    yocto_build, deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    out_dir = tmp_path / "out"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    fake_bin_dir.mkdir()
    (deploy / "rse-otp-image.img").write_bytes(b"otp")

    fake_tmux = fake_bin_dir / "tmux"
    fake_tmux.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"\n"
        "case \"$1\" in\n"
        "  has-session) exit 1 ;;\n"
        "  new-session) printf '%%0\\n' ;;\n"
        "  split-window)\n"
        "    counter_file=\"${TMUX_LOG}.counter\"\n"
        "    counter=0\n"
        "    [[ -f \"$counter_file\" ]] && counter=\"$(<\"$counter_file\")\"\n"
        "    counter=$((counter + 1))\n"
        "    printf '%s\\n' \"$counter\" > \"$counter_file\"\n"
        "    printf '%%%s\\n' \"$counter\"\n"
        "    ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_tmux.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "MACHINE": "apollo-fvp",
            "OUT_DIR": str(out_dir),
            "TMUX_SESSION": "pytest-run-qbox-yocto-layout",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "SSH_PORT_START": "24800",
            "SSH_PORT_END": "24899",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--no-attach"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    tmux_lines = tmux_log.read_text(encoding="utf-8").splitlines()
    split_lines = [line for line in tmux_lines if line.startswith("split-window ")]
    assert len(split_lines) == 6
    assert any(" -v -b -l 70% -t %0 " in f" {line} " for line in split_lines)
    assert any(" -h -l 40% -t %1 " in f" {line} " for line in split_lines)
    assert any(" -v -l 75% -t %2 " in f" {line} " for line in split_lines)
    assert any(" -v -l 67% -t %3 " in f" {line} " for line in split_lines)
    assert any(" -v -l 50% -t %4 " in f" {line} " for line in split_lines)
    assert any(" -h -l 50% -t %0 " in f" {line} " for line in split_lines)
    assert any(line == "select-pane -t %1 -T primary_console" for line in tmux_lines)
    assert any(line == "select-pane -t %2 -T rse" for line in tmux_lines)
    assert any(line == "select-pane -t %3 -T safety_island_cl0" for line in tmux_lines)
    assert any(line == "select-pane -t %4 -T safety_island_cl1" for line in tmux_lines)
    assert any(line == "select-pane -t %5 -T secure_console" for line in tmux_lines)
    assert any(line == "select-pane -t %0 -T platform" for line in tmux_lines)
    assert any(line == "select-pane -t %6 -T shell" for line in tmux_lines)
    assert sum("--uart-console" in line for line in split_lines) == 5
    assert any("QBOX_RDASPEN_PRIMARY_UART_READ_FILE=" in line for line in tmux_lines)
    assert any("QBOX_RDASPEN_UART_READ_FILE=" in line for line in tmux_lines)
    assert any("QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE=" in line for line in tmux_lines)
    assert any("QBOX_APOLLO_FULL_SI_CL1_UART_READ_FILE=" in line for line in tmux_lines)
    assert any("QBOX_RDASPEN_SECURE_UART_READ_FILE=" in line for line in tmux_lines)
    assert any("primary-uart-input.fifo" in line for line in tmux_lines)
    assert any("rse-uart-input.fifo" in line for line in tmux_lines)
    assert any(f"QBOX_CORE_DIR={ROOT / 'hsoc-stack/tools/qbox'}" in line for line in tmux_lines)
    assert any(
        line.startswith("set-hook ")
        and "client-attached" in line
        and "--rebalance-fvp-like-log-panes" in line
        for line in tmux_lines
    )
    assert any(
        line.startswith("set-hook ")
        and "client-resized" in line
        and "--rebalance-fvp-like-log-panes" in line
        for line in tmux_lines
    )
    assert not any(line.startswith("select-layout ") for line in tmux_lines)
    assert any("QBOX_APOLLO_NUM_CPUS=4" in line for line in tmux_lines)


def test_run_qbox_yocto_qvp_tmux_preserves_machine_console_prompts(
    tmp_path: Path,
) -> None:
    # Given: a QVP Yocto deploy tree and a fake tmux binary that records commands.
    yocto_build, _deploy, _work, _local_build, _conf = create_yocto_tree(
        tmp_path,
        machine="apollo-qvp",
        build_dir_name="build",
        include_qboxconf=True,
    )
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    fake_bin_dir.mkdir()

    fake_tmux = fake_bin_dir / "tmux"
    fake_tmux.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"\n"
        "case \"$1\" in\n"
        "  has-session) exit 1 ;;\n"
        "  new-session) printf '%%0\\n' ;;\n"
        "  split-window) printf '%%1\\n' ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_tmux.chmod(0o755)

    env = os.environ.copy()
    for name in QBOX_YOCTO_ENV_OVERRIDES:
        env.pop(name, None)
    env.update(
        {
            "TMUX_SESSION": "pytest-run-qbox-yocto-qvp-prompts",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "SSH_PORT_START": "25400",
            "SSH_PORT_END": "25499",
        }
    )

    # When: run_qbox_yocto.sh starts the tmux path for apollo-qvp.
    result = subprocess.run(
        [
            str(SCRIPT),
            "--build-dir",
            str(yocto_build),
            "--no-attach",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the in-tmux supervisor keeps the QVP login/shell prompt overrides.
    assert result.returncode == 0, result.stderr
    tmux_output = tmux_log.read_text(encoding="utf-8")
    assert r"PRIMARY_LOGIN_PROMPT=apollo-qvp\ login:" in tmux_output
    assert r"PRIMARY_SHELL_PROMPT_RE=\(\?:root@apollo-qvp" in tmux_output
    assert r"PRIMARY_LOGIN_PROMPT=apollo-fvp\ login:" not in tmux_output


def test_run_qbox_yocto_can_disable_tmux_uart_input_fifos(tmp_path: Path) -> None:
    result = run_dry_run(
        tmp_path,
        extra_env={"TMUX_UART_INPUT_FIFOS": "0"},
    )

    assert result.returncode == 0, result.stderr
    assert "UART input FIFOs disabled; logs use /dev/null input." in result.stdout
    assert "QBOX_RDASPEN_PRIMARY_UART_READ_FILE=" not in result.stdout
    assert "QBOX_RDASPEN_UART_READ_FILE=" not in result.stdout


def test_fvp_like_rebalance_keeps_right_stack_even_after_resize() -> None:
    tmux_bin = shutil.which("tmux")
    if tmux_bin is None:
        pytest.skip("tmux is not installed")
    assert tmux_bin is not None

    session = f"pytest-qbox-layout-{os.getpid()}"

    def tmux(*args: str) -> str:
        result = subprocess.run(
            [tmux_bin, *args],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.strip()

    try:
        subprocess.run(
            [tmux_bin, "new-session", "-d", "-x", "80", "-y", "24", "-s", session, "-n", "qbox", "sleep", "600"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        runner = tmux("display-message", "-p", "-t", f"{session}:qbox", "#{pane_id}")
        primary = tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-b",
            "-l",
            "70%",
            "-t",
            runner,
            "sleep",
            "600",
        )
        rse = tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-h",
            "-l",
            "40%",
            "-t",
            primary,
            "sleep",
            "600",
        )
        si0 = tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "75%",
            "-t",
            rse,
            "sleep",
            "600",
        )
        si1 = tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "67%",
            "-t",
            si0,
            "sleep",
            "600",
        )
        secure = tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "50%",
            "-t",
            si1,
            "sleep",
            "600",
        )
        tmux(
            "split-window",
            "-P",
            "-F",
            "#{pane_id}",
            "-h",
            "-l",
            "50%",
            "-t",
            runner,
            "sleep",
            "600",
        )
        tmux("resize-window", "-t", f"{session}:qbox", "-x", "240", "-y", "80")

        subprocess.run(
            [
                str(TMUX_SCRIPT),
                "--rebalance-fvp-like-log-panes",
                rse,
                si0,
                si1,
                secure,
            ],
            check=True,
            env={**os.environ, "TMUX_BIN": tmux_bin},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        heights = [
            int(tmux("display-message", "-p", "-t", pane, "#{pane_height}"))
            for pane in (rse, si0, si1, secure)
        ]
        assert max(heights) - min(heights) <= 1
    finally:
        subprocess.run(
            [tmux_bin, "kill-session", "-t", session],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def test_tmux_uart_console_filters_terminal_status_response() -> None:
    tmux_script = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
    script_text = tmux_script.read_text(encoding="utf-8")

    assert "is_terminal_status_response_line" in script_text
    assert "sanitize_uart_input_line" in script_text
    assert "is_raw_terminal_status_response_prefix" in script_text
    assert "stdin_tty_state" in script_text
    assert "stty -echo -icanon" in script_text
    assert "read -r -s -N 1" in script_text
    assert '"${clean_line}" != "$1"' in script_text
    assert r"^[[:space:]]*$" in script_text
    assert r"\^\[\[{0,1}[0-9]{1,5};[0-9]{1,5}R" in script_text
    assert r"\[{1,2}[0-9]{1,5};[0-9]{1,5}R" in script_text
    assert 'line="$(sanitize_uart_input_line "${line}")"' in script_text
    assert "write_fifo_line \"${fifo_path}\" \"${line}\"" in script_text
    assert "--uart-console" in script_text
    assert "primary-uart-input.fifo" in script_text
    assert "si-cl0-uart-input.fifo" in script_text


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (
            ["--enable-test-device"],
            "is no longer supported",
        ),
        (
            ["--mock-cc3xx"],
            "is no longer supported",
        ),
    ],
)
def test_run_qbox_yocto_rejects_removed_options(
    tmp_path: Path,
    args: list[str],
    message: str,
) -> None:
    result = run_dry_run(tmp_path, extra_args=args)

    assert result.returncode != 0
    assert message in result.stderr


def test_run_qbox_yocto_rejects_missing_rootfs(tmp_path: Path) -> None:
    yocto_build, deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    (deploy / "nexios-image-apollo-fvp.wic").unlink()

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "MACHINE": "apollo-fvp",
            "OUT_DIR": str(tmp_path / "out"),
            "TMUX_SESSION": "pytest-run-qbox-yocto-missing-rootfs",
            "SSH_PORT_START": "24700",
            "SSH_PORT_END": "24799",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--dry-run", "--no-attach"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "missing required Yocto rootfs WIC image" in result.stderr

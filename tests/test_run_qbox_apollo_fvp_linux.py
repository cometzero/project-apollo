from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_qbox_apollo_fvp_linux.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("apollo_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_local_build_artifacts_are_resolved_from_deploy_root(tmp_path):
    runner = load_runner()
    local_build = tmp_path / "build/local-apollo-fvp"
    deploy_boot = local_build / "deploy/boot"
    deploy_boot.mkdir(parents=True)
    for name in ("Image", "initramfs.cpio.gz"):
        (deploy_boot / name).write_bytes(b"x")

    artifacts = runner.resolve_local_build_artifacts(local_build)

    assert artifacts.kernel == deploy_boot / "Image"
    assert artifacts.initramfs == deploy_boot / "initramfs.cpio.gz"
    assert artifacts.disk == deploy_boot / "apollo-fvp-local-disk.img"


def test_default_bootargs_match_local_fvp_boot_script():
    runner = load_runner()

    assert runner.DEFAULT_LOCAL_BOOTARGS == (
        "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 "
        "root=/dev/ram0 rw rdinit=/init loglevel=7 "
        "cpuidle.governor=menu maxcpus=4 mem=4064M"
    )


def test_qbox_env_exports_initramfs_path_without_rootfs(tmp_path, monkeypatch):
    runner = load_runner()
    root = tmp_path
    kernel = tmp_path / "Image"
    dtb = tmp_path / "apollo.dtb"
    initramfs = tmp_path / "initramfs.cpio.gz"
    for path in (kernel, dtb, initramfs):
        path.write_bytes(b"x")
    monkeypatch.delenv("QBOX_APOLLO_ROOTFS", raising=False)

    args = type(
        "Args",
        (),
        {
            "kernel": kernel,
            "dtb": dtb,
            "initramfs": initramfs,
            "accel": "tcg",
            "netdev": "type=user",
        },
    )()

    env = runner.qbox_env(root, args, None, [])

    assert env["QBOX_APOLLO_KERNEL"] == str(kernel.resolve())
    assert env["QBOX_APOLLO_DTB"] == str(dtb.resolve())
    assert env["QBOX_APOLLO_INITRAMFS"] == str(initramfs.resolve())
    assert "QBOX_APOLLO_ROOTFS" not in env


def test_qbox_env_removes_stale_rootfs_env(tmp_path, monkeypatch):
    runner = load_runner()
    kernel = tmp_path / "Image"
    dtb = tmp_path / "apollo.dtb"
    for path in (kernel, dtb):
        path.write_bytes(b"x")
    monkeypatch.setenv("QBOX_APOLLO_ROOTFS", "/stale/rootfs.img")
    monkeypatch.setenv("QBOX_APOLLO_INITRAMFS", "/stale/initramfs.cpio.gz")

    args = type(
        "Args",
        (),
        {
            "kernel": kernel,
            "dtb": dtb,
            "initramfs": None,
            "accel": "tcg",
            "netdev": "type=user",
        },
    )()

    env = runner.qbox_env(tmp_path, args, None, [])

    assert "QBOX_APOLLO_ROOTFS" not in env
    assert "QBOX_APOLLO_INITRAMFS" not in env


def test_apollo_shell_prompt_accepts_local_initramfs_prompt():
    runner = load_runner()

    assert runner.apollo_shell_prompt_ready(
        "apollo-fvp login:\n/bin/sh: can't access tty; job control turned off\n~ # "
    )
    assert runner.apollo_shell_prompt_ready("root@apollo-fvp:~# ")
    assert not runner.apollo_shell_prompt_ready("apollo-fvp login:")


def test_probe_done_requires_output_marker_line():
    runner = load_runner()

    assert not runner.probe_complete_from_log(
        "~ # printf '\\n__QBOX_APOLLO_PROBE_DONE__:%s\\n' \"$?\"\n"
    )
    assert not runner.probe_complete_from_log("__QBOX_APOLLO_PROBE_DONE__:1\n")
    assert runner.probe_complete_from_log(
        "~ # printf '\\n__QBOX_APOLLO_PROBE_DONE__:%s\\n' \"$?\"\n"
        "__QBOX_APOLLO_PROBE_DONE__:0\n"
    )


def test_initramfs_end_is_computed_from_size(tmp_path):
    runner = load_runner()
    initramfs = tmp_path / "initramfs.cpio.gz"
    initramfs.write_bytes(b"12345678")

    assert runner.initramfs_range(initramfs, 0x94000000) == (
        0x94000000,
        0x94000008,
    )


def test_fdtput_commands_include_bootargs_and_initrd(tmp_path):
    runner = load_runner()
    dtb = tmp_path / "apollo.dtb"
    bootargs = "console=ttyAMA0 root=/dev/ram0"

    commands = runner.fdt_patch_commands(
        dtb=dtb,
        bootargs=bootargs,
        initrd_start=0x94000000,
        initrd_end=0x94001000,
    )

    assert commands == [
        ["fdtput", "-t", "s", str(dtb), "/chosen", "bootargs", bootargs],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-start",
            "0x94000000",
        ],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-end",
            "0x94001000",
        ],
    ]


def test_fdtput_commands_disable_primary_disk_when_missing(tmp_path):
    runner = load_runner()
    dtb = tmp_path / "apollo.dtb"

    commands = runner.fdt_patch_commands(
        dtb=dtb,
        bootargs="console=ttyAMA0",
        initrd_start=0x94000000,
        initrd_end=0x94001000,
        primary_disk_enabled=False,
    )

    assert commands[-1] == [
        "fdtput",
        "-t",
        "s",
        str(dtb),
        "/soc/virtio-block@30020000",
        "status",
        "disabled",
    ]

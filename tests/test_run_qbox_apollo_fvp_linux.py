from pathlib import Path
import importlib.util
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_linux.py"


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
    for name in ("Image", "initramfs.cpio.gz", "apollo-fvp.dtb"):
        (deploy_boot / name).write_bytes(b"x")

    artifacts = runner.resolve_local_build_artifacts(local_build)

    assert artifacts.kernel == deploy_boot / "Image"
    assert artifacts.initramfs == deploy_boot / "initramfs.cpio.gz"
    assert artifacts.disk == deploy_boot / "apollo-fvp-local-disk.img"
    assert artifacts.dtb == deploy_boot / "apollo-fvp.dtb"


def test_default_bootargs_match_local_fvp_boot_script():
    runner = load_runner()

    assert runner.DEFAULT_LOCAL_BOOTARGS == (
        "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 "
        "root=/dev/ram0 rw rdinit=/init loglevel=7 "
        "cpuidle.governor=menu maxcpus=16 mem=4064M"
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
    assert env["QBOX_APOLLO_NUM_CPUS"] == "16"
    assert "QBOX_APOLLO_ROOTFS" not in env


def test_qbox_env_leaves_direct_pc_trace_disabled_by_default(tmp_path, monkeypatch):
    runner = load_runner()
    kernel = tmp_path / "Image"
    dtb = tmp_path / "apollo.dtb"
    for path in (kernel, dtb):
        path.write_bytes(b"x")
    monkeypatch.delenv("QBOX_APOLLO_PC_TRACE", raising=False)
    monkeypatch.delenv("QBOX_APOLLO_PC_TRACE_FILE", raising=False)

    args = type(
        "Args",
        (),
        {
            "kernel": kernel,
            "dtb": dtb,
            "initramfs": None,
            "accel": "tcg",
            "netdev": "type=user",
            "out_dir": tmp_path / "out",
        },
    )()

    env = runner.qbox_env(tmp_path, args, None, [])

    assert "QBOX_APOLLO_PC_TRACE" not in env
    assert "QBOX_APOLLO_PC_TRACE_FILE" not in env


def test_qbox_env_defaults_direct_pc_trace_file_to_out_dir(tmp_path, monkeypatch):
    runner = load_runner()
    kernel = tmp_path / "Image"
    dtb = tmp_path / "apollo.dtb"
    for path in (kernel, dtb):
        path.write_bytes(b"x")
    monkeypatch.setenv("QBOX_APOLLO_PC_TRACE", "true")
    monkeypatch.delenv("QBOX_APOLLO_PC_TRACE_FILE", raising=False)

    args = type(
        "Args",
        (),
        {
            "kernel": kernel,
            "dtb": dtb,
            "initramfs": None,
            "accel": "tcg",
            "netdev": "type=user",
            "out_dir": tmp_path / "trace-run",
        },
    )()

    env = runner.qbox_env(tmp_path, args, None, [])

    assert env["QBOX_APOLLO_PC_TRACE"] == "true"
    assert env["QBOX_APOLLO_PC_TRACE_FILE"] == str(
        (tmp_path / "trace-run/cpu-pc-trace.log").resolve()
    )


def test_prepare_debug_outputs_rejects_external_trace_file_without_deleting(
    tmp_path, monkeypatch
):
    runner = load_runner()
    out_dir = tmp_path / "trace-run"
    external = tmp_path / "outside-trace.log"
    external.write_text("keep me\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    args = type("Args", (), {"out_dir": out_dir})()
    env = {
        "QBOX_APOLLO_PC_TRACE": "true",
        "QBOX_APOLLO_PC_TRACE_FILE": str(external),
    }

    with pytest.raises(ValueError, match="QBOX_APOLLO_PC_TRACE_FILE"):
        runner.prepare_debug_outputs(args, env)

    assert external.read_text(encoding="utf-8") == "keep me\n"


def test_prepare_debug_outputs_allows_trace_file_under_out_dir(tmp_path):
    runner = load_runner()
    out_dir = tmp_path / "trace-run"
    trace_file = out_dir / "cpu-pc-trace.log"
    trace_file.parent.mkdir(parents=True)
    trace_file.write_text("stale\n", encoding="utf-8")
    args = type("Args", (), {"out_dir": out_dir})()
    env = {
        "QBOX_APOLLO_PC_TRACE": "true",
        "QBOX_APOLLO_PC_TRACE_FILE": str(trace_file),
    }

    runner.prepare_debug_outputs(args, env)

    assert not trace_file.exists()


def test_validate_debug_env_rejects_zero_cpu_direct_boot(tmp_path):
    runner = load_runner()
    args = type("Args", (), {"netdev": "type=user", "out_dir": tmp_path})()
    env = {"QBOX_APOLLO_NUM_CPUS": "0"}

    with pytest.raises(ValueError, match="QBOX_APOLLO_NUM_CPUS"):
        runner.validate_debug_env(args, env)


def test_validate_debug_env_rejects_malformed_gdb_base(tmp_path):
    runner = load_runner()
    args = type("Args", (), {"netdev": "type=user", "out_dir": tmp_path})()
    env = {
        "QBOX_APOLLO_GDB_PORT_BASE": "not-a-port",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    with pytest.raises(ValueError, match="QBOX_APOLLO_GDB_PORT_BASE"):
        runner.validate_debug_env(args, env)


def test_validate_debug_env_rejects_nonzero_gdb_base(tmp_path):
    runner = load_runner()
    args = type(
        "Args",
        (),
        {
            "netdev": "type=user,hostfwd=tcp::24316-:22",
            "out_dir": tmp_path,
        },
    )()
    env = {
        "QBOX_APOLLO_GDB_PORT_BASE": "25000",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    with pytest.raises(ValueError, match="QBOX_APOLLO_GDB_PORT_BASE"):
        runner.validate_debug_env(args, env)


def test_validate_debug_env_allows_selected_gdb_cpu(tmp_path):
    runner = load_runner()
    args = type(
        "Args",
        (),
        {
            "netdev": "type=user,hostfwd=tcp::24316-:22",
            "out_dir": tmp_path,
        },
    )()
    env = {
        "QBOX_APOLLO_GDB_CPU_INDEX": "2",
        "QBOX_APOLLO_GDB_PORT": "25002",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    runner.validate_debug_env(args, env)


def test_validate_debug_env_rejects_selected_gdb_hostfwd_collision(tmp_path):
    runner = load_runner()
    args = type(
        "Args",
        (),
        {
            "netdev": "type=user,hostfwd=tcp::25002-:22",
            "out_dir": tmp_path,
        },
    )()
    env = {
        "QBOX_APOLLO_GDB_CPU_INDEX": "2",
        "QBOX_APOLLO_GDB_PORT": "25002",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    with pytest.raises(ValueError, match="hostfwd"):
        runner.validate_debug_env(args, env)


def test_validate_debug_env_rejects_selected_gdb_cpu_out_of_range(tmp_path):
    runner = load_runner()
    args = type("Args", (), {"netdev": "type=user", "out_dir": tmp_path})()
    env = {
        "QBOX_APOLLO_GDB_CPU_INDEX": "16",
        "QBOX_APOLLO_GDB_PORT": "25002",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    with pytest.raises(ValueError, match="QBOX_APOLLO_GDB_CPU_INDEX"):
        runner.validate_debug_env(args, env)


def test_validate_debug_env_rejects_selected_gdb_port_without_cpu(tmp_path):
    runner = load_runner()
    args = type("Args", (), {"netdev": "type=user", "out_dir": tmp_path})()
    env = {
        "QBOX_APOLLO_GDB_PORT": "25002",
        "QBOX_APOLLO_NUM_CPUS": "16",
    }

    with pytest.raises(ValueError, match="QBOX_APOLLO_GDB_CPU_INDEX"):
        runner.validate_debug_env(args, env)


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


def test_direct_boot_overlay_includes_bootargs_and_initrd():
    runner = load_runner()
    bootargs = "console=ttyAMA0 root=/dev/ram0"

    overlay = runner.direct_boot_overlay_dts(
        bootargs=bootargs,
        initrd_start=0x94000000,
        initrd_end=0x94001000,
    )

    assert "/plugin/;" in overlay
    assert 'target-path = "/chosen";' in overlay
    assert 'bootargs = "console=ttyAMA0 root=/dev/ram0";' in overlay
    assert "linux,initrd-start = <0x94000000>;" in overlay
    assert "linux,initrd-end = <0x94001000>;" in overlay


def test_direct_boot_overlay_disables_primary_disk_when_missing():
    runner = load_runner()

    overlay = runner.direct_boot_overlay_dts(
        bootargs="console=ttyAMA0",
        initrd_start=0x94000000,
        initrd_end=0x94001000,
        primary_disk_enabled=False,
    )

    assert 'target-path = "/soc/virtio@30020000";' in overlay
    assert 'status = "disabled";' in overlay

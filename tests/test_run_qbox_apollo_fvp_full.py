from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
from types import SimpleNamespace
import sys

import pytest  # pyright: ignore[reportMissingImports]


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
COVERAGE_SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_fvp_full_coverage.py"
AP_COMPUTE_LUA = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua"
)
SI_CL0_LUA = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua"
)
SI_CL1_LUA = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua"
)
APOLLO_QVP_CONFIG = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua"
)


def load_runner():
    spec = importlib.util.spec_from_file_location("apollo_full_runner", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_coverage_auditor():
    spec = importlib.util.spec_from_file_location("apollo_coverage_auditor", COVERAGE_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_args(tmp_path, *, post_login_probe=True):
    return SimpleNamespace(
        out_dir=tmp_path,
        post_login_probe=post_login_probe,
        primary_login_prompt="apollo-qvp login:",
        primary_shell_marker="~ #",
        si_mode="live-cl0-cl1",
    )


def make_child_command_args(tmp_path):
    return SimpleNamespace(
        cc3xx_local_mmio_fastpath=False,
        cc3xx_qemu_native_backend=False,
        cc3xx_stats=False,
        cc3xx_stats_interval=1024,
        cc3xx_status_read_fastpath=False,
        conf=tmp_path / "apollo-qvp.lua",
        forward_args=[],
        jobs=1,
        keep_running_after_pass=False,
        local_build_dir=tmp_path / "local-apollo-fvp",
        no_copy_writable_flash=False,
        out_dir=tmp_path,
        platform_param=[],
        post_login_probe=False,
        primary_login_prompt="apollo-qvp login:",
        primary_shell_marker="~ #",
        primary_shell_prompt_re=r"(?:root@apollo-qvp[^\n]*[#>]|\S+ #)\s*$",
        provision_blank_rse_otp=False,
        qbox_build_dir=tmp_path / "work/qbox-platform",
        qbox_perf_profile=False,
        qbox_perf_profile_interval=1024,
        range_limited_flash_dmi=False,
        rootfs_bootargs_profile="shell",
        rse_bl2_boot_enc_accel=False,
        rse_bl2_delay_accel=False,
        rse_bl2_delay_expected_hits=0,
        rse_bl2_delay_max_cycles=0,
        rse_bl2_img_hash_accel=False,
        rse_bl2_img_hash_max_bytes=0,
        rse_bl2_img_hash_max_seed_bytes=0,
        rse_bl2_libc_hotpath=False,
        rse_bl2_load_accel=False,
        rse_bl2_load_accel_max_bytes=0,
        rse_bl2_verify_sig_accel=False,
        rse_bl2_verify_sig_max_key_bytes=0,
        rse_bl2_verify_sig_max_sig_bytes=0,
        rse_bl2_verify_sig_skip=False,
        rse_fast_boot_aliases=False,
        rse_fast_boot_sram_dmi=False,
        rse_flash_backend="systemc-strata",
        rse_flash_state=None,
        reset_rse_flash_state=False,
        rse_hotpath_accel=True,
        rse_hotpath_max_bytes=0,
        rse_hotpath_memcpy_addr=None,
        rse_hotpath_memset_addr=None,
        rse_lms_accel=True,
        rse_lms_max_data_bytes=0,
        rse_lms_verify_addr=None,
        si_mode="live-cl0-cl1",
        skip_build=False,
        smmu_backend="systemc-mmu720ae",
        timeout=60,
        uboot_only=False,
        build_only=False,
    )


def make_child_artifacts(tmp_path):
    names = (
        "ap_bl2_elf",
        "ap_flash",
        "efi_capsule_disk",
        "provisioning_bundle",
        "rootfs",
        "rse_bl1_2_elf",
        "rse_bl2_elf",
        "rse_flash",
        "rse_otp",
        "rse_rom",
    )
    return {name: tmp_path / name for name in names}


def test_child_command_omits_removed_rse_remote_flags(tmp_path):
    runner = load_runner()

    cmd = runner.child_command(
        make_child_command_args(tmp_path),
        make_child_artifacts(tmp_path),
    )

    removed_flags = (
        "--rse-cpu-mode",
        "--remotepass-dmi-cache",
        "--rse-hotpath-tlm-fallback",
    )
    for flag in removed_flags:
        assert flag not in cmd
    assert "--rse-hotpath-accel" in cmd
    assert "--rse-lms-accel" in cmd


def test_child_command_forwards_persistent_rse_flash_state(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.rse_flash_state = tmp_path / "state/rse-flash-image.img"
    args.reset_rse_flash_state = True

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    state_index = cmd.index("--rse-flash-state")
    assert cmd[state_index + 1] == str(args.rse_flash_state)
    assert "--reset-rse-flash-state" in cmd


def test_child_command_forwards_opt_in_post_login_probe(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.post_login_probe = True

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "--post-login-probe" in cmd


def test_child_command_forwards_qemu_local_cfi_backend(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.rse_flash_backend = "qemu-cfi-local"

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert cmd[cmd.index("--rse-flash-backend") + 1] == "qemu-cfi-local"


def test_child_runtime_evidence_keeps_runtime_fields():
    runner = load_runner()
    expected_hits = {
        "rse_runtime_handoff": {
            "elapsed_s": 19.5,
            "marker": "Jumping to the first image slot",
        }
    }
    evidence = runner.child_runtime_evidence(
        {
            "runtime_elapsed_s": 52.25,
            "progress_marker_first_hits": expected_hits,
        }
    )

    assert evidence == {
        "runtime_elapsed_s": 52.25,
        "progress_marker_first_hits": expected_hits,
    }


def test_child_command_uboot_only_skips_live_cl1_completion_markers(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.uboot_only = True
    args.post_login_probe = True

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "--required-pass-marker" not in cmd
    assert "--post-login-probe" not in cmd


def test_clear_run_outputs_preserves_tmux_primary_uart_fifo(tmp_path):
    runner = load_runner()
    fifo_path = tmp_path / "primary-uart-input.fifo"
    stale_result = tmp_path / "result.json"
    os.mkfifo(fifo_path)
    stale_result.write_text("{}", encoding="utf-8")

    runner.clear_run_outputs(tmp_path)

    assert fifo_path.is_fifo()
    assert not stale_result.exists()


def test_child_command_requires_live_cl1_readiness(tmp_path):
    runner = load_runner()

    cmd = runner.child_command(
        make_child_command_args(tmp_path),
        make_child_artifacts(tmp_path),
    )

    cl1_log = str((tmp_path / "qbox-safety-island-cl1.log").resolve())
    assert cmd.count("--required-pass-marker") == len(
        runner.LIVE_CL1_REQUIRED_MARKERS
    )
    assert cl1_log in cmd
    for marker in runner.LIVE_CL1_REQUIRED_MARKERS.values():
        assert marker in cmd


def test_child_command_presets_full_system_qemu_modes(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "platform.ap_qemu_inst.tcg_mode=MULTI" in cmd
    assert "platform.si_cl0_qemu_inst.tcg_mode=MULTI" in cmd
    assert "platform.si_cl1_qemu_inst.tcg_mode=MULTI" in cmd
    assert "platform.si_cl1_qemu_inst.sync_policy=multithread-quantum" in cmd
    maxcpus_index = cmd.index("--rootfs-maxcpus")
    assert cmd[maxcpus_index + 1] == "4"


def test_child_command_aligns_rootfs_maxcpus_with_environment(
    tmp_path, monkeypatch
):
    runner = load_runner()
    monkeypatch.setenv("QBOX_APOLLO_NUM_CPUS", "8")

    cmd = runner.child_command(
        make_child_command_args(tmp_path), make_child_artifacts(tmp_path)
    )

    maxcpus_index = cmd.index("--rootfs-maxcpus")
    assert cmd[maxcpus_index + 1] == "8"


def test_child_command_preserves_explicit_qemu_mode_override(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.platform_param = ["platform.ap_qemu_inst.tcg_mode=SINGLE"]

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "platform.ap_qemu_inst.tcg_mode=SINGLE" in cmd
    assert "platform.ap_qemu_inst.tcg_mode=MULTI" not in cmd


def test_child_command_forwards_range_limited_flash_dmi_disable(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.range_limited_flash_dmi = False

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "--no-range-limited-flash-dmi" in cmd
    assert "--range-limited-flash-dmi" not in cmd


def test_full_system_qemu_defaults_use_per_cpu_wake_conditions():
    ap_text = AP_COMPUTE_LUA.read_text(encoding="utf-8")
    assert (
        'tcg_mode = ctx.getenv_or("QBOX_APOLLO_FULL_AP_TCG_MODE", "MULTI")'
        in ap_text
    )

    text = SI_CL1_LUA.read_text(encoding="utf-8")
    assert (
        'tcg_mode = ctx.getenv_or("QBOX_APOLLO_FULL_SI_CL1_TCG_MODE", "MULTI")'
        in text
    )
    assert '"QBOX_APOLLO_FULL_SI_CL1_SYNC_POLICY", "multithread-quantum"' in text
    assert "managed_start_in_reset_release = true" in ap_text
    assert "managed_start_in_reset_release = true" in text

    si_cl0_text = SI_CL0_LUA.read_text(encoding="utf-8")
    assert (
        '"QBOX_APOLLO_FULL_SI_CL0_TCG_MODE", "MULTI"' in si_cl0_text
    )

def test_live_cl1_gate_requires_pfdi_readiness():
    runner = load_runner()
    marker_groups = {
        "maps_and_interrupts": {"map_ok": True},
        "si_cl0": {"cl0_ok": True},
        "si_cl1": {
            name: name != "pfdi_agent"
            for name in runner.LIVE_CL1_REQUIRED_MARKERS
        },
    }

    blocker = runner.live_cl1_gate_blocker(
        SimpleNamespace(si_mode="live-cl0-cl1"),
        marker_groups,
        {"passed": True},
    )

    assert blocker == "live_cl0_cl1_marker_blocked:pfdi_agent"


@pytest.mark.parametrize(
    "bridge",
    (
        "ap_system_bridge",
        "si_cl0_system_bridge",
        "si_cl1_system_bridge",
    ),
)
def test_removed_migration_bridge_shadow_warnings_are_rejected(bridge):
    runner = load_runner()
    log = (
        "addressMap: Region 'platform."
        f"{bridge}.target_socket' is completely shadowed"
    )

    assert runner.has_unexpected_shadowed_range(log) is True


def test_removed_atu_check_shadow_warnings_are_rejected():
    runner = load_runner()
    log = (
        "addressMap: Region 'platform.ap_atu_check_0.target_socket' "
        "is completely shadowed"
    )

    assert runner.has_unexpected_shadowed_range(log) is True


def test_coverage_accepts_headless_login_without_guest_injection(tmp_path):
    auditor = load_coverage_auditor()
    result = {
        "marker_groups": {
            "linux": {"login_prompt": True, "root_shell": False},
            "linux_boot": {"apollo-qvp login:": True, "~ #": False},
        },
        "console_logs": {
            "primary_console": str(tmp_path / "primary.log"),
            "si_cl0": str(tmp_path / "si-cl0.log"),
        },
    }

    checks = {item["name"]: item for item in auditor.marker_group_checks(result)}

    assert checks["markers:linux"]["passed"] is True
    assert checks["markers:linux_boot"]["passed"] is True


def test_apollo_qvp_config_rejects_enabled_zero_ap_cpus():
    lua = shutil.which("lua")
    if lua is None:
        pytest.skip("lua is not installed")
    assert lua is not None
    env = os.environ.copy()
    env["QBOX_RDASPEN_ENABLE_AP_CPUS"] = "true"
    env["QBOX_APOLLO_NUM_CPUS"] = "0"

    result = subprocess.run(
        [lua, str(APOLLO_QVP_CONFIG)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "QBOX_APOLLO_NUM_CPUS must be 1..16" in result.stderr


@pytest.mark.parametrize(
    "child_args",
    [
        ["--allow-blank-rse-otp"],
        ["--qemu-trace"],
        ["--secure-service-probe"],
        ["--rse-direct-file-aliases", "0x1000:0x10:0:ro:/tmp/qbox-alias.bin"],
        ["--rse-bl2-load-profile"],
    ],
)
def test_parse_args_forwards_supported_child_options(tmp_path, monkeypatch, child_args):
    runner = load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_qbox_apollo_fvp_full.py",
            "--check-only",
            "--out-dir",
            str(tmp_path / "out"),
            *child_args,
        ],
    )

    args = runner.parse_args()
    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert args.forward_args == child_args
    for item in child_args:
        assert item in cmd


def test_parse_args_and_artifacts_default_to_active_apollo_qvp(monkeypatch):
    runner = load_runner()
    monkeypatch.setattr(sys, "argv", ["run_qbox_apollo_fvp_full.py", "--check-only"])

    args = runner.parse_args()
    artifacts = runner.default_artifacts(args.local_build_dir)

    assert args.local_build_dir == ROOT / "build/local-apollo-qvp"
    assert args.out_dir.parent == ROOT / "build/qbox-apollo-qvp"
    assert args.rse_flash_backend == "qemu-cfi-local"
    assert artifacts["rootfs"].name == "apollo-qvp-local-disk.img"
    assert artifacts["ap_dtb"].name == "apollo-qvp.dtb"
    assert "apollo_qvp" in artifacts["ap_bl2_elf"].parts


def test_timer_probe_without_model_snapshot_is_a_hard_nonpass(tmp_path):
    # Given: timer evidence was requested but no model-side producer exists.
    runner = load_runner()
    args = SimpleNamespace(out_dir=tmp_path, timer_probe=True, timer_probe_run_id="current-run")

    # When: the runner records timer evidence.
    evidence = runner.timer_probe_evidence(args)

    # Then: it writes an explicit unavailable artifact rather than inferring success.
    assert evidence["status"] == "unavailable"
    assert evidence["strict_gate"] is True
    assert (tmp_path / "timer-probe-status.json").exists()


def test_timer_probe_rejects_a_stale_pass_snapshot(tmp_path):
    # Given: a successful snapshot from a different runner invocation.
    runner = load_runner()
    (tmp_path / "timer-snapshot.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "pass",
                "source": {"run_id": "prior-run"},
            }
        ),
        encoding="utf-8",
    )
    args = SimpleNamespace(out_dir=tmp_path, timer_probe=True, timer_probe_run_id="current-run")

    # When: the current runner evaluates the old artifact.
    evidence = runner.timer_probe_evidence(args)

    # Then: stale evidence cannot satisfy the strict timer gate.
    assert evidence["status"] == "unavailable"
    assert evidence["reason"] == "model_side_timer_snapshot_run_id_mismatch"


@pytest.mark.parametrize(
    "forward_args",
    [
        ["--rse-cpu-mode", "remote"],
        ["--remotepass-dmi-cache"],
        ["--rse-hotpath-tlm-fallback"],
        ["--isolated"],
        ["--definitely-invalid-option"],
    ],
)
def test_parse_args_rejects_removed_or_unknown_forwarded_options(
    tmp_path,
    monkeypatch,
    forward_args,
):
    runner = load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_qbox_apollo_fvp_full.py",
            "--check-only",
            "--out-dir",
            str(tmp_path / "out"),
            *forward_args,
        ],
    )

    try:
        runner.parse_args()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("unknown forwarded option was accepted")


def write_passing_logs(tmp_path):
    (tmp_path / "qbox-rse.log").write_text(
        "\n".join(
            [
                "Starting TF-M BL1_1",
                "Init SCMI comm to SCP succeeded",
                "RSE to SCP SCMI power on AP succeeded",
                "SCMI Comms subscribed to power state notifications",
                "Measured boot: BL1_2 BL2 SI_CL0 AP_BL2 RT_0 "
                "SECURE_RT_EL3 SECURE_RT_EL1_SPMD BL_33",
                "Jumping to the first image slot",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-secure-console.log").write_text(
        "NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-primary-console.log").write_text(
        "\n".join(
            [
                "apollo-qvp login:",
                "~ # echo __QBOX_PROBE_START__",
                "__QBOX_PROBE_START__",
                "arm_si_rproc_modprobe_rc:0",
                "remoteproc_state_after:si-cl1:attached",
                "virtio_rpmsg_bus_modprobe_rc:0",
                "rpmsg_net_modprobe_rc:0",
                "rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1",
                "ethsi1_iplink_rc:0",
                "virtio_blk virtio_rng",
                "ttyAMA0 uart-pl011",
                "arm-smmu-v3 1c0000000.iommu",
                "dsu_pmu_event_source:arm_dsu_0",
                "dsu_pmu_event_source_rc:0",
                "pfdi_misc_modprobe_rc:0",
                "pfdi_info_rc:0",
                "libPFDI version: 1.0",
                "pfdi_firmware_info_rc:0",
                "CPU0: Firmware reports 41 available diagnostic tests",
                "pfdi_count_rc:0",
                "CPU0: Out of Reset (OoR) test OK",
                "pfdi_cpu0_result_rc:0",
                "CPU1: Out of Reset (OoR) test OK",
                "pfdi_cpu1_result_rc:0",
                "CPU2: Out of Reset (OoR) test OK",
                "pfdi_cpu2_result_rc:0",
                "CPU3: Out of Reset (OoR) test OK",
                "pfdi_cpu3_result_rc:0",
                "~ # echo __QBOX_PROBE_DONE__",
                "__QBOX_PROBE_DONE__",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-safety-island-cl0.log").write_text(
        "\n".join(
            [
                "[SI0_PLATFORM] SCP started",
                "[FWK] Module initialization complete!",
                "GIC-multiview configured successfully",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-safety-island-cl1.log").write_text(
        "\n".join(
            [
                "Out of Reset (OoR) completed on CPU: 0",
                "Booting Zephyr OS",
                "PFDI Agent setup complete",
                "PFDI service ready",
                "si_net_init: Network interface configured",
                "RPMSG Endpoint: ATTACHED",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_keep_running_child_status_requires_live_cl1_rpmsg_endpoint(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    cl1_log = tmp_path / "qbox-safety-island-cl1.log"
    cl1_log.write_text(
        cl1_log.read_text(encoding="utf-8").replace(
            "RPMSG Endpoint: ATTACHED\n",
            "",
        ),
        encoding="utf-8",
    )

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False
    assert (
        status["marker_hits"]["si_cl1"]["RPMSG Endpoint: ATTACHED"]
        is False
    )


def test_keep_running_child_status_waits_for_live_cl1(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    (tmp_path / "qbox-safety-island-cl1.log").unlink()

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False
    assert not all(status["marker_hits"]["si_cl1"].values())


def test_keep_running_child_status_does_not_read_cl1_fifo(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    cl1_log = tmp_path / "qbox-safety-island-cl1.log"
    cl1_log.unlink()
    os.mkfifo(cl1_log)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False


def test_keep_running_child_status_does_not_follow_cl1_symlink(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    cl1_log = tmp_path / "qbox-safety-island-cl1.log"
    target = tmp_path / "complete-cl1.log"
    cl1_log.rename(target)
    cl1_log.symlink_to(target)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False


def test_keep_running_child_status_passes_with_complete_post_login_probe(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True, status["post_login_probe"]
    assert status["marker_hits"]["linux_boot"]["apollo-qvp login:"] is True
    assert status["post_login_probe"]["requested"] is True
    assert status["post_login_probe"]["complete"] is True
    assert "rse_cpu_mode" not in status
    assert "remotepass_dmi_cache" not in status
    assert all(status["post_login_probe"]["driver_patterns"].values())
    profile = status["rse_boot_timing_profile"]
    assert profile["markers"][-1] == {
        "name": "primary_login_prompt",
        "label": "Linux login prompt",
        "marker": "apollo-qvp login:",
        "seen": True,
        "elapsed_s": None,
    }
    assert status["progress_marker_first_hits"]["primary_login_prompt"] == {
        "elapsed_s": None,
        "marker": "apollo-qvp login:",
    }
    assert status["scp_service_model"]["strategy"] == "real-si-scp"


def test_keep_running_child_status_propagates_rse_flash_state(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    expected = {
        "enabled": True,
        "action": "storage-preserved",
        "path": str(tmp_path / "state.img"),
    }
    (tmp_path / "rse-flash-state.json").write_text(
        json.dumps(expected) + "\n",
        encoding="utf-8",
    )

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["rse_flash_state"] == expected


def test_keep_running_child_status_rejects_pfdi_timeout(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    cl1_log = tmp_path / "qbox-safety-island-cl1.log"
    cl1_log.write_text(
        cl1_log.read_text(encoding="utf-8")
        + "<err> PFDI status timed out on CPU 0\n"
        + "<err> PFDI request failed ret=-116\n",
        encoding="utf-8",
    )

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=0,
    )

    assert status["passed"] is False
    assert status["fail_patterns"]["PFDI status timed out"] is True
    assert status["fail_patterns"]["ret=-116"] is True


def test_live_cl1_gate_rejects_pfdi_timeout(tmp_path):
    runner = load_runner()
    (tmp_path / "qbox-safety-island-cl1.log").write_text(
        "PFDI Agent setup complete\n"
        "PFDI service ready\n"
        "<err> PFDI status timed out on CPU 0\n",
        encoding="utf-8",
    )
    marker_groups = {
        "maps_and_interrupts": {"map_ok": True},
        "si_cl0": {"cl0_ok": True},
        "si_cl1": {name: True for name in runner.LIVE_CL1_REQUIRED_MARKERS},
    }

    blocker = runner.live_cl1_gate_blocker(
        SimpleNamespace(si_mode="live-cl0-cl1", out_dir=tmp_path),
        marker_groups,
        {"passed": True},
    )

    assert blocker == "live_cl0_cl1_error:pfdi_status_timeout"


def test_live_cl1_gate_rejects_pfdi_initialization_failure(tmp_path):
    runner = load_runner()
    (tmp_path / "qbox-safety-island-cl1.log").write_text(
        "PFDI Agent setup complete\n"
        "PFDI service ready\n"
        "<err> PROTOCOL_VERSION timed out (core=1)\n"
        "<err> PFDI Agent device not ready\n",
        encoding="utf-8",
    )
    marker_groups = {
        "maps_and_interrupts": {"map_ok": True},
        "si_cl0": {"cl0_ok": True},
        "si_cl1": {name: True for name in runner.LIVE_CL1_REQUIRED_MARKERS},
    }

    blocker = runner.live_cl1_gate_blocker(
        SimpleNamespace(si_mode="live-cl0-cl1", out_dir=tmp_path),
        marker_groups,
        {"passed": True},
    )

    assert blocker == (
        "live_cl0_cl1_error:pfdi_protocol_version_timeout,"
        "pfdi_agent_not_ready"
    )


def test_keep_running_child_status_requires_requested_probe_marker(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    primary = tmp_path / "qbox-primary-console.log"
    primary.write_text(
        primary.read_text(encoding="utf-8").replace("__QBOX_PROBE_DONE__", ""),
        encoding="utf-8",
    )

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False
    assert status["post_login_probe"]["complete"] is False


def test_gate_status_records_post_login_qualification():
    runner = load_runner()
    args = SimpleNamespace(
        build_only=False,
        post_login_probe=True,
        si_mode="live-cl0-cl1",
        uboot_only=False,
    )
    child_status = {
        "passed": True,
        "post_login_probe": {
            "requested": True,
            "sent_probe": True,
            "complete": True,
            "passed": True,
        },
    }

    gates = runner.gate_status(
        args=args,
        child_status=child_status,
        blocker=None,
        check_only=False,
    )

    assert gates["G1"] == "pass"
    assert gates["G4"] == "pass"


def test_post_login_probe_promotes_root_shell_marker(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    child_status = {
        "marker_hits": {
            "linux_boot": {
                "apollo-qvp login:": True,
                "~ #": False,
            }
        },
        "post_login_probe": {
            "requested": True,
            "sent_probe": True,
            "complete": True,
            "passed": True,
        },
    }

    groups = runner.build_marker_groups(make_args(tmp_path), child_status)

    assert groups["linux"]["root_shell"] is True
    assert groups["post_login"]["probe"] is True
    assert groups["linux_boot"]["~ #"] is True


def test_post_login_probe_rejects_incomplete_driver_contract():
    runner = load_runner()

    probe = runner.post_login_probe(
        {
            "post_login_probe": {
                "requested": True,
                "sent_probe": True,
                "complete": True,
                "driver_patterns": {"pfdi_4cpu": False},
            }
        }
    )

    assert probe["passed"] is False


def test_keep_running_child_status_uses_configured_legacy_login_prompt(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    primary = tmp_path / "qbox-primary-console.log"
    primary.write_text(
        primary.read_text(encoding="utf-8").replace(
            "apollo-qvp login:",
            "apollo-fvp login:",
        ),
        encoding="utf-8",
    )
    args = make_args(tmp_path)
    args.primary_login_prompt = "apollo-fvp login:"

    status = runner.synthesize_keep_running_child_status(
        args,
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True
    assert status["marker_hits"]["linux_boot"]["apollo-fvp login:"] is True
    assert "apollo-qvp login:" not in status["marker_hits"]["linux_boot"]
    assert status["post_login_probe"]["sent_login"] is True
    assert status["progress_marker_first_hits"]["primary_login_prompt"] == {
        "elapsed_s": None,
        "marker": "apollo-fvp login:",
    }

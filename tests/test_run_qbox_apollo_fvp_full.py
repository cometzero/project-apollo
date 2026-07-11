from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
from types import SimpleNamespace
import sys

import pytest  # pyright: ignore[reportMissingImports]


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
AP_COMPUTE_LUA = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua"
)
SI_CL1_LUA = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua"
)
SI_CL1_ISOLATED_LUA = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1_isolated.lua"
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


def make_args(tmp_path, *, post_login_probe=True):
    return SimpleNamespace(
        out_dir=tmp_path,
        post_login_probe=post_login_probe,
        primary_login_prompt="apollo-fvp login:",
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
        primary_login_prompt="apollo-fvp login:",
        primary_shell_marker="~ #",
        primary_shell_prompt_re=r"(?:root@apollo-fvp[^\n]*[#>]|\S+ #)\s*$",
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
    assert "platform.si_cl1_qemu_inst.tcg_mode=MULTI" in cmd
    assert "platform.si_cl1_qemu_inst.sync_policy=multithread-quantum" in cmd


def test_child_command_preserves_explicit_qemu_mode_override(tmp_path):
    runner = load_runner()
    args = make_child_command_args(tmp_path)
    args.platform_param = ["platform.ap_qemu_inst.tcg_mode=SINGLE"]

    cmd = runner.child_command(args, make_child_artifacts(tmp_path))

    assert "platform.ap_qemu_inst.tcg_mode=SINGLE" in cmd
    assert "platform.ap_qemu_inst.tcg_mode=MULTI" not in cmd


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

    isolated_text = SI_CL1_ISOLATED_LUA.read_text(encoding="utf-8")
    assert 'getenv_or("QBOX_APOLLO_SI_CL1_TCG_MODE", "SINGLE")' in isolated_text


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


@pytest.mark.parametrize(
    "forward_args",
    [
        ["--rse-cpu-mode", "remote"],
        ["--remotepass-dmi-cache"],
        ["--rse-hotpath-tlm-fallback"],
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
                "apollo-fvp login:",
                "~ # echo __QBOX_PROBE_START__",
                "__QBOX_PROBE_START__",
                "arm_si_rproc_modprobe_rc:0",
                "virtio_rpmsg_bus_modprobe_rc:0",
                "rpmsg_net_modprobe_rc:0",
                "rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1",
                "ethsi1_iplink_rc:0",
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
            ]
        )
        + "\n",
        encoding="utf-8",
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


def test_keep_running_child_status_passes_with_login_and_probe_output_ignored(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True
    assert status["marker_hits"]["linux_boot"]["apollo-fvp login:"] is True
    assert status["post_login_probe"]["requested"] is False
    assert status["post_login_probe"]["complete"] is False
    assert "rse_cpu_mode" not in status
    assert "remotepass_dmi_cache" not in status
    assert status["post_login_probe"]["driver_patterns"] == {}
    profile = status["rse_boot_timing_profile"]
    assert profile["markers"][-1] == {
        "name": "primary_login_prompt",
        "label": "Linux login prompt",
        "marker": "apollo-fvp login:",
        "seen": True,
        "elapsed_s": None,
    }
    assert status["progress_marker_first_hits"]["primary_login_prompt"] == {
        "elapsed_s": None,
        "marker": "apollo-fvp login:",
    }
    assert status["scp_service_model"]["strategy"] == "real-si-scp"


def test_keep_running_child_status_does_not_require_removed_probe_marker(tmp_path):
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

    assert status["passed"] is True
    assert status["post_login_probe"]["complete"] is False


def test_keep_running_child_status_uses_configured_qvp_login_prompt(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    primary = tmp_path / "qbox-primary-console.log"
    primary.write_text(
        primary.read_text(encoding="utf-8").replace(
            "apollo-fvp login:",
            "apollo-qvp login:",
        ),
        encoding="utf-8",
    )
    args = make_args(tmp_path)
    args.primary_login_prompt = "apollo-qvp login:"

    status = runner.synthesize_keep_running_child_status(
        args,
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True
    assert status["marker_hits"]["linux_boot"]["apollo-qvp login:"] is True
    assert "apollo-fvp login:" not in status["marker_hits"]["linux_boot"]
    assert status["post_login_probe"]["sent_login"] is True
    assert status["progress_marker_first_hits"]["primary_login_prompt"] == {
        "elapsed_s": None,
        "marker": "apollo-qvp login:",
    }

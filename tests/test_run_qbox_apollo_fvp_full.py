from pathlib import Path
import importlib.util
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("apollo_full_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_args(tmp_path, *, post_login_probe=True):
    return type(
        "Args",
        (),
        {
            "out_dir": tmp_path,
            "post_login_probe": post_login_probe,
            "si_mode": "live-cl0-cl1",
            "remotepass_dmi_cache": True,
            "rse_cpu_mode": "remote",
        },
    )()


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
        provision_blank_rse_otp=False,
        qbox_build_dir=tmp_path / "work/qbox-platform",
        qbox_perf_profile=False,
        qbox_perf_profile_interval=1024,
        range_limited_flash_dmi=False,
        remotepass_dmi_cache=False,
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
        rse_cpu_mode="inprocess",
        rse_fast_boot_aliases=False,
        rse_fast_boot_sram_dmi=False,
        rse_hotpath_accel=False,
        rse_hotpath_max_bytes=0,
        rse_hotpath_memcpy_addr=None,
        rse_hotpath_memset_addr=None,
        rse_hotpath_tlm_fallback=False,
        rse_lms_accel=False,
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


def test_child_command_forwards_rse_cpu_mode(tmp_path):
    runner = load_runner()

    cmd = runner.child_command(
        make_child_command_args(tmp_path),
        make_child_artifacts(tmp_path),
    )

    assert "--rse-cpu-mode" in cmd
    assert cmd[cmd.index("--rse-cpu-mode") + 1] == "inprocess"


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
        "[SI0_PLATFORM] SCP started\n",
        encoding="utf-8",
    )


def test_keep_running_child_status_passes_after_probe_marker(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True
    assert status["marker_hits"]["linux_boot"]["apollo-fvp login:"] is True
    assert status["post_login_probe"]["complete"] is True
    assert status["post_login_probe"]["driver_patterns"] == {
        "arm_si_rproc": True,
        "rpmsg": True,
        "hipc_ethsi1": True,
    }
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


def test_keep_running_child_status_waits_for_probe_done_marker(tmp_path):
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

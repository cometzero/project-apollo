from pathlib import Path
import importlib.util
import os
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_fvp_rd_aspen_rse.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("rd_aspen_runner", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_strip_runner_control_env_keeps_paths_out_of_qbox_env():
    runner = load_runner()
    env = {
        "QBOX_RDASPEN_RESULT_PATH": "result.json",
        "QBOX_RDASPEN_SUMMARY_PATH": "summary.txt",
        "QBOX_RDASPEN_RSE_ROM": "rse-rom-image.img",
    }

    stripped = runner.strip_runner_control_env(env)

    assert stripped is env
    assert "QBOX_RDASPEN_RESULT_PATH" not in stripped
    assert "QBOX_RDASPEN_SUMMARY_PATH" not in stripped
    assert stripped["QBOX_RDASPEN_RSE_ROM"] == "rse-rom-image.img"


def test_required_targets_use_local_rse_cpu_only():
    runner = load_runner()

    assert "cpu_arm_cortexM55" in runner.REQUIRED_TARGETS
    assert all("remote" not in target.lower() for target in runner.REQUIRED_TARGETS)


def test_missing_required_pass_markers_reports_incomplete_file(tmp_path):
    runner = load_runner()
    cl1_log = tmp_path / "qbox-safety-island-cl1.log"
    cl1_log.write_text("Booting Zephyr OS\n", encoding="utf-8")
    requirements = [
        [str(cl1_log), "Booting Zephyr OS"],
        [str(cl1_log), "PFDI service ready"],
    ]

    missing = runner.missing_required_pass_markers(requirements)

    assert missing == [f"{cl1_log}:PFDI service ready"]


def test_missing_required_pass_markers_rejects_special_files(tmp_path):
    runner = load_runner()
    fifo = tmp_path / "cl1.fifo"
    os.mkfifo(fifo)

    missing = runner.missing_required_pass_markers(
        [[str(fifo), "PFDI service ready"]]
    )

    assert missing == [f"{fifo}:PFDI service ready"]


def test_missing_required_pass_markers_does_not_follow_symlinks(tmp_path):
    runner = load_runner()
    target = tmp_path / "cl1.log"
    target.write_text("PFDI service ready\n", encoding="utf-8")
    symlink = tmp_path / "cl1-link.log"
    symlink.symlink_to(target)

    missing = runner.missing_required_pass_markers(
        [[str(symlink), "PFDI service ready"]]
    )

    assert missing == [f"{symlink}:PFDI service ready"]


def test_required_pass_marker_arguments_reject_control_characters():
    runner = load_runner()

    error = runner.required_pass_marker_argument_error(
        [["cl1.log", "PFDI service ready\nforged"]]
    )

    assert error == "--required-pass-marker arguments must not contain control characters"

    error = runner.required_pass_marker_argument_error(
        [["cl1.log", "PFDI service ready\u0085forged"]]
    )

    assert error == "--required-pass-marker arguments must not contain control characters"


def test_required_pass_marker_blocker_needs_base_pass():
    runner = load_runner()
    missing = ["cl1.log:PFDI service ready"]

    assert runner.required_pass_marker_blocker(False, missing, True) is None
    assert runner.required_pass_marker_blocker(True, missing, True) == (
        "qbox_required_pass_marker_timeout:cl1.log:PFDI service ready"
    )


def make_qbox_env_args(tmp_path):
    return SimpleNamespace(
        ap_bl2_elf=None,
        boot_enc_trace=False,
        cc3xx_local_mmio_fastpath=False,
        cc3xx_qemu_native_backend=True,
        cc3xx_stats=True,
        cc3xx_stats_interval=1024,
        cc3xx_status_read_fastpath=False,
        exception_trace=False,
        flash_stats=False,
        flash_stats_interval=1024,
        fwu_probe=False,
        no_copy_writable_flash=False,
        out_dir=tmp_path,
        pc_trace=False,
        pc_trace_interval=1024,
        pc_trace_limit=0,
        platform_param=[],
        post_login_probe=False,
        qbox_initiator_addr_profile=False,
        qbox_initiator_addr_profile_limit=64,
        qbox_initiator_addr_profile_shift=12,
        qbox_perf_profile=True,
        qbox_perf_profile_interval=1024,
        qemu_trace=False,
        qemu_trace_events="in_asm",
        qemu_trace_filter=None,
        range_limited_flash_dmi=False,
        rootfs=None,
        rse_bl2_boot_enc_accel=False,
        rse_bl2_delay_accel=False,
        rse_bl2_img_hash_accel=False,
        rse_bl2_load_accel=False,
        rse_bl2_load_profile=False,
        rse_bl2_verify_sig_accel=False,
        rse_bl2_verify_sig_skip=False,
        rse_direct_ap_bl2_alias=False,
        rse_direct_ap_bl2_code_alias_size=0,
        rse_direct_ap_fip_alias=False,
        rse_direct_file_aliases="",
        rse_direct_rse_flash_alias=False,
        rse_direct_si_sram_alias=False,
        rse_direct_si_sram_code_alias_size=0,
        rse_fast_boot_sram_dmi=False,
        rse_hotpath_accel=True,
        rse_hotpath_max_bytes=4096,
        rse_hotpath_memcpy_addr=None,
        rse_hotpath_memset_addr=None,
        rse_lms_accel=True,
        rse_lms_max_data_bytes=2048,
        rse_lms_verify_addr=0x11009BAD,
        rse_storage_direct_fastpath=False,
        scp_strategy="service-model",
        secure_service_probe=False,
        smmu_backend="systemc-mmu720ae",
    )


def make_qbox_env_artifacts(tmp_path):
    return {
        "ap_flash": tmp_path / "ap-flash.img",
        "provisioning_bundle": tmp_path / "bundle.zip",
        "rootfs": tmp_path / "rootfs.ext4",
        "rse_flash": tmp_path / "rse-flash.img",
        "rse_otp": tmp_path / "rse-otp.img",
        "rse_rom": tmp_path / "rse-rom.img",
    }


def test_qbox_env_omits_removed_remote_fields_and_keeps_accelerators(
    tmp_path, monkeypatch
):
    runner = load_runner()
    removed_envs = (
        "QBOX_RSE_CPU_MODE",
        "QBOX_REMOTE_CPU_EXEC",
        "QBOX_RDASPEN_REMOTEPASS_DMI_CACHE",
        "QBOX_RDASPEN_RSE_HOTPATH_TLM_FALLBACK",
    )
    for name in removed_envs:
        monkeypatch.setenv(name, "true")

    env = runner.qbox_env(Path("/repo"), make_qbox_env_args(tmp_path), make_qbox_env_artifacts(tmp_path))

    for name in removed_envs:
        assert name not in env
    assert "QBOX_REMOTEPASS_PROFILE_DIR" not in env
    assert env["QBOX_RDASPEN_RSE_HOTPATH_ACCEL"] == "true"
    assert env["QBOX_RDASPEN_RSE_LMS_ACCEL"] == "true"
    assert "QBOX_RDASPEN_RSE_HOTPATH_PROFILE_FILE" in env


def test_qbox_perf_profile_result_omits_remotepass_fields(tmp_path):
    runner = load_runner()
    result = runner.parse_qbox_perf_profile(make_qbox_env_args(tmp_path))

    assert result["enabled"] is True
    assert "remotepass_dir" not in result
    assert "remotepass_profiles" not in result

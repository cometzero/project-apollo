from pathlib import Path
import importlib.util
import os
from types import SimpleNamespace
import sys

import pytest  # pyright: ignore[reportMissingImports]


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


def test_patched_bootargs_replaces_maxcpus_for_modeled_topology():
    runner = load_runner()

    options = runner.patched_bootargs(
        "root=/dev/ram0 maxcpus=16 console=ttyAMA1,115200",
        profile="quiet-console",
        maxcpus=4,
    )

    assert options.split().count("maxcpus=4") == 1
    assert "maxcpus=16" not in options.split()
    assert "console=ttyAMA0,115200" in options.split()


def test_fast_boot_sram_dmi_preserves_explicit_flash_dmi_disable(monkeypatch):
    runner = load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_qbox_fvp_rd_aspen_rse.py",
            "--build-only",
            "--rse-fast-boot-sram-dmi",
            "--no-range-limited-flash-dmi",
        ],
    )

    args = runner.parse_args()

    assert args.rse_fast_boot_sram_dmi is True
    assert args.range_limited_flash_dmi is False
    assert args.rse_flash_backend == "qemu-cfi-local"


def test_post_login_probe_commands_finish_after_four_cpu_pfdi_checks():
    runner = load_runner()
    args = SimpleNamespace(
        fwu_probe=False,
        secure_service_probe=False,
    )

    commands = runner.post_login_probe_commands(args)

    assert commands[-1] == f"echo {runner.PROBE_DONE_MARKER}"
    assert "pfdi-cli --info; echo pfdi_info_rc:$?" in commands
    assert "pfdi-cli --pfdi_info 0; echo pfdi_firmware_info_rc:$?" in commands
    assert "pfdi-cli --count 0; echo pfdi_count_rc:$?" in commands
    assert (
        "echo failed_units_count:$(systemctl --failed --no-legend --plain "
        "2>/dev/null | wc -l)"
        in commands
    )
    for cpu in range(4):
        assert (
            f"pfdi-cli --result {cpu}; echo pfdi_cpu{cpu}_result_rc:$?"
            in commands
        )


def test_dsu_probe_does_not_fail_when_only_one_supported_glob_matches():
    runner = load_runner()
    args = SimpleNamespace(
        fwu_probe=False,
        secure_service_probe=False,
    )

    commands = runner.post_login_probe_commands(args)
    status_command = next(
        command
        for command in commands
        if "dsu_pmu_event_source_rc:" in command
    )

    assert "ls -d" not in status_command


def test_secure_service_probe_enables_post_login_driver(monkeypatch):
    runner = load_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_qbox_fvp_rd_aspen_rse.py",
            "--build-only",
            "--secure-service-probe",
        ],
    )

    args = runner.parse_args()

    assert args.post_login_probe is True


def test_drive_post_login_probe_paces_commands_on_shell_prompts(monkeypatch):
    runner = load_runner()
    writes = []
    monkeypatch.setattr(runner, "write_primary_uart", lambda _fd, text: writes.append(text))
    args = SimpleNamespace(
        fwu_probe=False,
        login_user="root",
        post_login_probe=True,
        primary_login_prompt="apollo-qvp login:",
        primary_shell_prompt_re=r"~ #\s*$",
        secure_service_probe=False,
    )
    state = runner.make_probe_state(args)

    runner.drive_post_login_probe(
        args,
        {"primary_console": "apollo-qvp login:\n"},
        state,
        1,
    )
    runner.drive_post_login_probe(
        args,
        {"primary_console": "apollo-qvp login:\n~ #\n"},
        state,
        1,
    )
    runner.drive_post_login_probe(
        args,
        {"primary_console": "apollo-qvp login:\n~ #\n__QBOX_PROBE_START__\n~ #\n"},
        state,
        1,
    )

    assert writes[0] == "root\n"
    assert writes[1] == "echo __QBOX_PROBE_START__\n"
    assert writes[2] == "uname -a\n"
    assert state["sent_login"] is True
    assert state["sent_probe"] is True
    assert state["command_index"] == 2


def test_active_apollo_storage_layout_covers_ps_and_its():
    runner = load_runner()

    assert runner.RSE_FLASH_PS_SIZE == 0x00100000
    assert runner.RSE_FLASH_ITS_SIZE == 0x00040000
    assert runner.RSE_BOOT_FLASH_STORAGE_SIZE == 0x00140000
    assert runner.rse_storage_direct_fastpath_spec() == "0xb3000000:0x140000"


def test_persistent_rse_flash_records_ps_and_its_before_after_hashes(
    tmp_path, monkeypatch
):
    runner = load_runner()
    monkeypatch.setattr(runner, "RSE_FLASH_IMG_SIZE", 8)
    monkeypatch.setattr(runner, "RSE_FLASH_PS_SIZE", 4)
    monkeypatch.setattr(runner, "RSE_FLASH_ITS_SIZE", 2)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_OFFSET", 8)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_SIZE", 6)
    source = tmp_path / "source.img"
    otp = tmp_path / "otp.img"
    state = tmp_path / "state.img"
    source.write_bytes(b"firmware")
    otp.write_bytes(b"identity")

    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=runner.rse_storage_compatibility(otp),
    )
    lock.close()

    assert status["storage_regions"]["ps"]["before_sha256"] == runner.sha256_file_region(
        state, offset=8, size=4
    )
    assert status["storage_regions"]["its"]["before_sha256"] == runner.sha256_file_region(
        state, offset=12, size=2
    )
    with state.open("r+b") as flash:
        flash.seek(8)
        flash.write(b"PS!!IT")

    finalized = runner.finalize_rse_flash_state_status(status)

    assert finalized["storage_regions"]["ps"]["after_sha256"] == runner.sha256_file_region(
        state, offset=8, size=4
    )
    assert finalized["storage_regions"]["its"]["after_sha256"] == runner.sha256_file_region(
        state, offset=12, size=2
    )
    assert finalized["storage_regions"]["ps"]["changed"] is True
    assert finalized["storage_regions"]["its"]["changed"] is True


def test_qbox_and_fvp_cold_marker_schema_matches():
    runner = load_runner()
    fvp_script = ROOT / "scripts/run/runfvp_log_boot.py"
    spec = importlib.util.spec_from_file_location("runfvp_log_boot", fvp_script)
    assert spec is not None
    assert spec.loader is not None
    fvp_runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = fvp_runner
    spec.loader.exec_module(fvp_runner)

    expected = {
        "rse_runtime_handoff",
        "tf_a_mboot_fw_config",
        "tf_a_mboot_secure_rt_el3",
        "tf_a_mboot_hw_config",
        "tf_a_mboot_secure_rt_el1_spmd",
        "tf_a_mboot_bl33",
        "uboot_mm_partition",
        "fwu_regular_state",
    }

    assert expected <= runner.PROGRESS_MARKERS.keys()
    assert {
        name: runner.PROGRESS_MARKERS[name] for name in expected
    } == {
        name: fvp_runner.PROGRESS_MARKERS[name] for name in expected
    }


def test_persistent_rse_flash_create_reuse_reset_and_preserve_storage(
    tmp_path, monkeypatch
):
    runner = load_runner()
    monkeypatch.setattr(runner, "RSE_FLASH_IMG_SIZE", 8)
    monkeypatch.setattr(runner, "RSE_FLASH_PS_SIZE", 4)
    monkeypatch.setattr(runner, "RSE_FLASH_ITS_SIZE", 2)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_OFFSET", 8)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_SIZE", 6)
    source = tmp_path / "source.img"
    otp = tmp_path / "otp.img"
    state = tmp_path / "state/rse-flash-image.img"
    source.write_bytes(b"firmware")
    otp.write_bytes(b"device-identity")
    compatibility = runner.rse_storage_compatibility(otp)

    path, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert path == state
    assert status["action"] == "created"
    assert state.stat().st_size == 16

    with state.open("r+b") as flash:
        flash.seek(8)
        flash.write(b"STORE!")
    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert status["action"] == "reused"
    assert state.read_bytes()[8:14] == b"STORE!"

    source.write_bytes(b"new-fw!!")
    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert status["action"] == "storage-preserved"
    assert status["storage_preserved"] is True
    assert state.read_bytes()[:8] == b"new-fw!!"
    assert state.read_bytes()[8:14] == b"STORE!"

    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=True,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert status["action"] == "reset"
    assert state.read_bytes()[8:14] == bytes([runner.FLASH_ERASED_VALUE]) * 6


def test_persistent_rse_flash_refreshes_when_otp_identity_changes(
    tmp_path, monkeypatch
):
    runner = load_runner()
    monkeypatch.setattr(runner, "RSE_FLASH_IMG_SIZE", 8)
    monkeypatch.setattr(runner, "RSE_FLASH_PS_SIZE", 4)
    monkeypatch.setattr(runner, "RSE_FLASH_ITS_SIZE", 2)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_OFFSET", 8)
    monkeypatch.setattr(runner, "RSE_BOOT_FLASH_STORAGE_SIZE", 6)
    source = tmp_path / "source.img"
    otp = tmp_path / "otp.img"
    state = tmp_path / "state.img"
    source.write_bytes(b"firmware")
    otp.write_bytes(b"identity-a")
    compatibility = runner.rse_storage_compatibility(otp)
    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert status["action"] == "created"
    with state.open("r+b") as flash:
        flash.seek(8)
        flash.write(b"STORE!")

    otp.write_bytes(b"identity-b")
    compatibility = runner.rse_storage_compatibility(otp)
    _, status, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=16,
        storage_compatibility=compatibility,
    )
    lock.close()
    assert status["action"] == "refreshed"
    assert status["storage_preserved"] is False
    assert state.read_bytes()[8:14] == bytes([runner.FLASH_ERASED_VALUE]) * 6


def test_persistent_rse_flash_rejects_concurrent_use(tmp_path):
    runner = load_runner()
    source = tmp_path / "source.img"
    otp = tmp_path / "otp.img"
    state = tmp_path / "state.img"
    source.write_bytes(b"image")
    otp.write_bytes(b"identity")
    compatibility = runner.rse_storage_compatibility(otp)
    _, _, lock = runner.prepare_persistent_rse_flash(
        source,
        state,
        reset=False,
        minimum_size=runner.RSE_BOOT_FLASH_SIZE,
        storage_compatibility=compatibility,
    )
    try:
        with pytest.raises(RuntimeError, match="rse_flash_state_in_use"):
            runner.prepare_persistent_rse_flash(
                source,
                state,
                reset=False,
                minimum_size=runner.RSE_BOOT_FLASH_SIZE,
                storage_compatibility=compatibility,
            )
    finally:
        lock.close()


def test_fast_boot_sram_dmi_uses_real_atu_ap_fip_path():
    runner = load_runner()
    args = SimpleNamespace(
        rse_fast_boot_sram_dmi=True,
        rse_direct_ap_fip_alias=False,
    )

    result = runner.ap_fip_logical_aperture_result(args)
    ap_compute = (
        ROOT
        / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua"
    ).read_text(encoding="utf-8")

    assert result["enabled"] is False
    assert result["mode"] == "atu_systemc_route"
    assert "platform.rse_ap_fip_logical" not in ap_compute


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
        fwu_probe=False,
        no_copy_writable_flash=False,
        out_dir=tmp_path,
        pc_trace=False,
        pc_trace_interval=1024,
        pc_trace_limit=0,
        platform_param=[],
        post_login_probe=False,
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
        rse_flash_backend="qemu-cfi-local",
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
    assert env["QBOX_RDASPEN_RSE_FLASH_BACKEND"] == "qemu-cfi-local"
    assert "QBOX_RDASPEN_RSE_HOTPATH_PROFILE_FILE" in env


def test_qbox_env_adds_installed_libqemu_from_cmake_cache(tmp_path, monkeypatch):
    runner = load_runner()
    build_dir = tmp_path / "qbox-build"
    libqemu_dir = (
        tmp_path
        / "tmp/sysroots-components/x86_64/qbox-libqemu-native/usr/lib"
    )
    dependency_dir = (
        tmp_path
        / "tmp/work/x86_64-linux/qbox-libqemu-native/1.0/"
        "recipe-sysroot-native/usr/lib"
    )
    (libqemu_dir / "cmake/libqemu").mkdir(parents=True)
    dependency_dir.mkdir(parents=True)
    build_dir.mkdir()
    (build_dir / "CMakeCache.txt").write_text(
        f"libqemu_DIR:UNINITIALIZED={libqemu_dir}/cmake/libqemu\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("QBOX_PLATFORM_BUILD_DIR", str(build_dir))

    env = runner.qbox_env(
        tmp_path,
        make_qbox_env_args(tmp_path),
        make_qbox_env_artifacts(tmp_path),
    )

    assert str(libqemu_dir) in env["LD_LIBRARY_PATH"].split(":")
    assert str(dependency_dir) in env["LD_LIBRARY_PATH"].split(":")


def test_qbox_env_adds_libqemu_for_installed_yocto_provider(
    tmp_path, monkeypatch
):
    runner = load_runner()
    components_dir = tmp_path / "tmp/sysroots-components/x86_64"
    build_dir = components_dir / "qbox-apollo-qvp-native/usr/bin"
    provider_lib_dir = build_dir.parent / "lib"
    module_dir = provider_lib_dir / "qbox/modules"
    libqemu_dir = components_dir / "qbox-libqemu-native/usr/lib"
    recipe_lib_dir = (
        tmp_path
        / "tmp/work/x86_64-linux/qbox-apollo-qvp-native/1.0/"
        "recipe-sysroot-native/usr/lib"
    )
    build_dir.mkdir(parents=True)
    module_dir.mkdir(parents=True)
    libqemu_dir.mkdir(parents=True)
    recipe_lib_dir.mkdir(parents=True)
    monkeypatch.setenv("QBOX_PLATFORM_BUILD_DIR", str(build_dir))

    env = runner.qbox_env(
        tmp_path,
        make_qbox_env_args(tmp_path),
        make_qbox_env_artifacts(tmp_path),
    )

    library_paths = env["LD_LIBRARY_PATH"].split(":")
    assert str(provider_lib_dir) in library_paths
    assert str(module_dir) in library_paths
    assert str(recipe_lib_dir) in library_paths
    assert str(libqemu_dir) in library_paths


def test_qbox_perf_profile_result_omits_remotepass_fields(tmp_path):
    runner = load_runner()
    result = runner.parse_qbox_perf_profile(make_qbox_env_args(tmp_path))

    assert result["enabled"] is True
    assert "remotepass_dir" not in result
    assert "remotepass_profiles" not in result

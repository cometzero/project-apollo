from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
COMPONENTS: Final[tuple[str, ...]] = (
    "qbox",
    "tf-m",
    "scp-firmware",
    "zephyr",
    "optee",
    "u-boot",
    "tf-a",
    "linux",
    "buildroot",
    "flash-images",
    "boot-disk",
    "fvpconf",
    "debug-manifest",
)
KCONFIG_ACTIONS: Final[tuple[str, ...]] = (
    "defconfig",
    "menuconfig",
    "savedefconfig",
)


def run_local_build(
    *argv: str, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": "/usr/bin:/bin",
        "RUN_STAMP": "pytest",
        "HOME": "/nonexistent",
    }
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ("./local_build.sh", *argv),
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def output_of(result: subprocess.CompletedProcess[str]) -> str:
    return f"{result.stdout}\n{result.stderr}"


def component_step_lines(output: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if line.startswith("  ")
        and not line.startswith("    ")
        and ":" in line
        and not line.lstrip().startswith("package:")
    ]


def write_meminfo(path: Path, mem_total_kib: int) -> None:
    path.write_text(f"MemTotal:       {mem_total_kib} kB\n", encoding="utf-8")


def test_help_documents_local_fvp_contract() -> None:
    # Given: the new underscore local build entrypoint.
    # When: the user asks for CLI help.
    result = run_local_build("--help")

    # Then: help exposes the local build contract.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "Usage: ./local_build.sh" in output
    assert "--dry-run" in output
    assert "--package" in output
    assert "--no-package" in output
    assert "--qbox-unit-tests" in output
    assert "--qbox-systemc-tests" in output
    assert "--ccache-report" in output
    assert "--refresh-sdk" in output
    for component in COMPONENTS:
        assert component in output
    for action in ("build", "clean", "clean-build", *KCONFIG_ACTIONS):
        assert action in output


def test_help_includes_operational_examples_with_existing_script_paths() -> None:
    # Given: the new underscore local build entrypoint.
    # When: the user asks for CLI help.
    result = run_local_build("--help")

    # Then: help shows the requested local FVP workflow examples.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    for example in (
        "./local_build.sh",
        "./local_build.sh qbox",
        "./local_build.sh qbox --qbox-unit-tests",
        "./local_build.sh --qbox-unit-tests",
        "./local_build.sh linux clean-build --no-package",
        "./local_build.sh linux menuconfig --no-package",
        "./local_build.sh --refresh-sdk",
        "./local_build.sh --package",
    ):
        assert example in output

    example_lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("./")
    ]
    assert example_lines
    for line in example_lines:
        script = line.split()[0]
        assert (ROOT / script.removeprefix("./")).exists(), line


def test_dry_run_defaults_to_all_components_plus_package() -> None:
    # Given: no selected components or actions.
    # When: a dry-run build is requested.
    result = run_local_build("--dry-run")

    # Then: the default plan builds every supported component needed by QBox local boot.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == [
        f"{component}: build" for component in COMPONENTS
    ]
    assert "order: qbox tf-m scp-firmware zephyr optee u-boot tf-a linux buildroot flash-images boot-disk fvpconf debug-manifest" in output
    assert "package: local FVP deploy" not in output


def test_refresh_sdk_dry_run_is_sdk_only() -> None:
    result = run_local_build("--refresh-sdk", "--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "order: sdk-refresh" in output
    assert "sdk-refresh: force populate and reinstall" in output
    assert "bitbake nexios-image -c populate_sdk -f" in output
    assert "Yocto SDK generation can take a long time" in output
    assert "qbox: build" not in output


def test_sdk_dir_defaults_to_active_machine(tmp_path: Path) -> None:
    # Given: local_build_common.sh is sourced for the active apollo-qvp machine.
    command = (
        "set -euo pipefail; "
        "source scripts/build/local_build_common.sh; "
        "printf '%s\\n' \"${SDK_DIR}\""
    )
    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "MACHINE": "apollo-qvp",
            "PATH": "/usr/bin:/bin",
            "YOCTO_BUILD_DIR": str(tmp_path / "build"),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the default SDK install root cannot reuse another machine's SDK.
    assert result.returncode == 0, output_of(result)
    assert result.stdout.strip() == str(tmp_path / "build/local-sdk-apollo-qvp")


def test_ccache_report_covers_every_component_when_available(tmp_path: Path) -> None:
    tools_dir = tmp_path / "tools"
    write_file(
        tools_dir / "ccache",
        "#!/usr/bin/env bash\n"
        "printf 'ccache fixture\\n'\n",
    )
    (tools_dir / "ccache").chmod(0o755)

    result = run_local_build(
        "--ccache-report",
        extra_env={"PATH": f"{tools_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "status enabled" in output
    assert f"detail {tools_dir / 'ccache'}" in output
    lines = output.splitlines()
    for component in COMPONENTS:
        assert any(
            line.split()[:2] == [component, "yes"] for line in lines
        ), component
    assert "CMake C/CXX compiler launcher" in output
    assert "Kbuild CC and HOSTCC overrides" in output
    assert "TF-A CC and HOSTCC overrides" in output


def test_ccache_report_can_be_disabled(tmp_path: Path) -> None:
    tools_dir = tmp_path / "tools"
    write_file(
        tools_dir / "ccache",
        "#!/usr/bin/env bash\n"
        "printf 'ccache fixture\\n'\n",
    )
    (tools_dir / "ccache").chmod(0o755)

    result = run_local_build(
        "--ccache-report",
        extra_env={
            "APOLLO_LOCAL_BUILD_CCACHE": "0",
            "PATH": f"{tools_dir}:/usr/bin:/bin",
        },
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "status disabled" in output
    lines = output.splitlines()
    for component in COMPONENTS:
        assert any(
            line.split()[:2] == [component, "no"] for line in lines
        ), component


def test_ccache_required_fails_when_missing(tmp_path: Path) -> None:
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir(parents=True)
    for command in ("bash", "dirname"):
        (tools_dir / command).symlink_to(Path("/bin") / command)

    result = run_local_build(
        "--ccache-report",
        extra_env={
            "APOLLO_LOCAL_BUILD_CCACHE": "required",
            "PATH": str(tools_dir),
        },
    )

    assert result.returncode != 0
    output = output_of(result)
    assert "ccache was not found" in output
    assert "APOLLO_LOCAL_BUILD_CCACHE=required" in output


def test_dry_run_local_config_defaults_use_4_pc_cpus() -> None:
    result = run_local_build("--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "pc cpus: 4" in output
    assert "tfa linux dts: 1" in output
    assert "maxcpus=4" in output
    assert "maxcpus=16" not in output


def test_dry_run_defaults_to_six_jobs_at_16gb_or_less(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    write_meminfo(meminfo, 16 * 1024 * 1024)

    result = run_local_build(
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "APOLLO_HOST_CPUS": "32",
            "APOLLO_MEMINFO_PATH": str(meminfo),
        },
    )

    assert result.returncode == 0, output_of(result)
    assert "jobs: 6" in output_of(result)


def test_dry_run_defaults_to_all_cpus_above_16gb(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    write_meminfo(meminfo, 32 * 1024 * 1024)

    result = run_local_build(
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "APOLLO_HOST_CPUS": "32",
            "APOLLO_MEMINFO_PATH": str(meminfo),
        },
    )

    assert result.returncode == 0, output_of(result)
    assert "jobs: 32" in output_of(result)


def test_explicit_components_and_action_skip_package_when_requested() -> None:
    # Given: selected components, an explicit action, and package disabled.
    # When: dry-run resolves the command.
    result = run_local_build(
        "u-boot",
        "linux",
        "--action",
        "clean-build",
        "--no-package",
        "--dry-run",
    )

    # Then: only the selected component actions are planned.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "u-boot" in output
    assert "linux" in output
    assert "clean-build" in output
    assert "package: local FVP deploy" not in output
    planned_components = {
        line.split(":", maxsplit=1)[0] for line in component_step_lines(output)
    }
    assert planned_components == {"u-boot", "linux"}


def test_package_flag_is_package_only_when_no_components_are_selected() -> None:
    # Given: the package flag without component selection.
    # When: dry-run resolves the command.
    result = run_local_build("--package", "--dry-run")

    # Then: only the local FVP package step is planned.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "package" in output
    assert component_step_lines(output) == []
    assert "qbox" not in output.lower()
    assert "buildroot" not in output.lower()


def test_package_local_linux_preflights_missing_mtools(tmp_path: Path) -> None:
    # Given: local Linux outputs require WIC ESP patching, but mtools are absent.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build, modules=False)
    tools_dir = tmp_path / "host-tools"
    tools_dir.mkdir(parents=True)
    for command in ("bash", "dirname", "mkdir", "python3", "realpath"):
        (tools_dir / command).symlink_to(Path("/bin") / command)
    write_file(
        tools_dir / "sgdisk",
        "#!/usr/bin/env bash\n"
        "printf 'unexpected sgdisk execution\\n' >&2\n"
        "exit 99\n",
    )
    (tools_dir / "sgdisk").chmod(0o755)
    hook_log = tmp_path / "package-flash-hook.log"

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            env | {"JOBS": "1", "PATH": str(tools_dir)},
            hook_log,
        ),
    )

    # Then: the command fails before flash generation mutates the package tree.
    assert result.returncode != 0
    output = output_of(result)
    assert "missing required command: mdir" in output
    assert "unexpected sgdisk execution" not in output
    assert not hook_log.exists()


def test_no_package_removes_default_package_step() -> None:
    # Given: the default all-component dry-run with package disabled.
    # When: dry-run resolves the command.
    result = run_local_build("--no-package", "--dry-run")

    # Then: every component is planned and package is omitted.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    for component in COMPONENTS:
        assert component in output
    assert "package: local FVP deploy" not in output


def test_buildroot_dry_run_resolves_initramfs_output() -> None:
    result = run_local_build("buildroot", "--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["buildroot: build"]
    assert "function: build_buildroot_initramfs" in output
    assert "initramfs.cpio.gz" in output
    assert "build/local-apollo-qvp/deploy/boot" in output


def test_boot_artifact_components_dry_run_resolve_existing_module_functions() -> None:
    result = run_local_build(
        "flash-images",
        "boot-disk",
        "fvpconf",
        "debug-manifest",
        "--dry-run",
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == [
        "flash-images: build",
        "boot-disk: build",
        "fvpconf: build",
        "debug-manifest: build",
    ]
    assert "function: package_flash_images" in output
    assert "function: create_boot_disk" in output
    assert "function: create_fvpconf" in output
    assert "function: generate_debug_manifest" in output


def test_component_stage_logs_start_and_completion(tmp_path: Path) -> None:
    result = run_local_build(
        "linux",
        "clean",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "Starting linux-clean" in output
    assert "Completed linux-clean in " in output
    assert output.index("Starting linux-clean") < output.index("Completed linux-clean")


def test_qbox_build_dry_run_resolves_qbox_target() -> None:
    # Given: QBox is selected as an underscore local build component.
    # When: dry-run resolves the command.
    result = run_local_build("qbox", "--dry-run")

    # Then: the command plans only the QBox platform build by default.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["qbox: build"]
    assert "function: build_qbox" in output
    assert "qbox core: hsoc-stack/tools/qbox" in output
    assert "qbox patches:" not in output
    assert "apollo_fvp_full_system" in output
    assert "package: local FVP deploy" not in output


def test_qbox_libqemu_timer_abi_probe_rejects_stale_package(
    tmp_path: Path,
) -> None:
    prefix = tmp_path / "libqemu"
    cmake_dir = prefix / "lib/cmake/libqemu"
    header = prefix / "include/libqemu/libqemu/libqemu.h"
    write_file(cmake_dir / "libqemuConfig.cmake", "# fixture\n")
    write_file(header, "#define LIBQEMU_ABI_VERSION 1U\n")

    result = subprocess.run(
        (
            "bash",
            "-c",
            "source scripts/build/modules/build_qbox.sh; "
            "qbox_libqemu_supports_arm_timer_abi \"${QBOX_TEST_LIBQEMU_DIR}\"",
        ),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_COMMON_SOURCED": "1",
            "PATH": "/usr/bin:/bin",
            "QBOX_TEST_LIBQEMU_DIR": str(cmake_dir),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0, output_of(result)


def test_qbox_libqemu_timer_abi_probe_accepts_current_package(
    tmp_path: Path,
) -> None:
    prefix = tmp_path / "libqemu"
    cmake_dir = prefix / "lib/cmake/libqemu"
    header = prefix / "include/libqemu/libqemu/libqemu.h"
    write_file(cmake_dir / "libqemuConfig.cmake", "# fixture\n")
    write_file(
        header,
        "#define LIBQEMU_ABI_VERSION 2U\n"
        "#define LIBQEMU_ARM_TIMER_REQUIRED_STRUCT_SIZE 2248U\n",
    )

    result = subprocess.run(
        (
            "bash",
            "-c",
            "source scripts/build/modules/build_qbox.sh; "
            "qbox_libqemu_supports_arm_timer_abi \"${QBOX_TEST_LIBQEMU_DIR}\"",
        ),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_COMMON_SOURCED": "1",
            "PATH": "/usr/bin:/bin",
            "QBOX_TEST_LIBQEMU_DIR": str(cmake_dir),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, output_of(result)


def test_qbox_source_libqemu_rebuilds_incrementally_by_default() -> None:
    build_script = ROOT / "scripts/build/modules/build_qbox.sh"

    assert 'QBOX_LIBQEMU_BUILD_ALWAYS:-ON' in build_script.read_text()


def test_qbox_nested_qemu_build_preserves_make_jobserver() -> None:
    qemu_cmake = ROOT / "hsoc-stack/tools/qemu/qemu.cmake"
    contents = qemu_cmake.read_text()

    assert 'set(_qemu_build_command "$(MAKE)")' in contents
    assert "BUILD_COMMAND ${_qemu_build_command}" in contents
    assert "INSTALL_COMMAND ${_qemu_build_command} install" in contents


def test_qbox_unit_tests_dry_run_selects_qbox_only() -> None:
    result = run_local_build("--qbox-unit-tests", "--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["qbox: build"]
    assert "test target: qbox_platform_systemc_component_tests" in output
    assert "ctest: -L qbox-platform-systemc-components" in output
    assert "package: local FVP deploy" not in output


def test_qbox_systemc_tests_dry_run_remains_alias() -> None:
    result = run_local_build("--qbox-systemc-tests", "--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["qbox: build"]
    assert "test target: qbox_platform_systemc_component_tests" in output


def test_unknown_action_fails_with_actionable_error() -> None:
    # Given: a valid component and invalid action.
    # When: the action is requested.
    result = run_local_build("linux", "rebuild", "--dry-run")

    # Then: the command reports the invalid action.
    assert result.returncode != 0
    output = output_of(result).lower()
    assert "unknown action" in output or "unsupported action" in output
    assert "rebuild" in output


def test_kconfig_actions_are_rejected_for_unsupported_components() -> None:
    # Given: a non-Kconfig component.
    # When: a Kconfig action is requested.
    result = run_local_build("tf-a", "menuconfig", "--dry-run")

    # Then: the error names the unsupported component/action combination.
    assert result.returncode != 0
    output = output_of(result).lower()
    assert "unsupported action for component" in output
    assert "tf-a" in output
    assert "menuconfig" in output


def test_uboot_defconfig_dry_run_resolves_make_kconfig_command() -> None:
    # Given: U-Boot is selected for a Kconfig defconfig action.
    # When: dry-run resolves the command.
    result = run_local_build("u-boot", "defconfig", "--dry-run")

    # Then: the existing out-of-tree make flow and cross context are shown.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "u-boot: defconfig" in output
    assert "make -C" in output
    assert "hsoc-stack/components/primary_compute/u-boot" in output
    assert "O=build/local-apollo-qvp/work/u-boot" in output
    assert "ARCH=arm" in output
    assert "CROSS_COMPILE=aarch64-poky-linux-" in output
    assert "RD_ASPEN_VARIANT=cfg2" in output
    assert "apollo_qvp_defconfig" in output


def test_linux_menuconfig_dry_run_resolves_make_kconfig_command() -> None:
    # Given: Linux is selected for a Kconfig menuconfig action.
    # When: dry-run resolves the command.
    result = run_local_build("linux", "menuconfig", "--dry-run")

    # Then: the existing out-of-tree make flow and cross context are shown.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "linux: menuconfig" in output
    assert "make -C" in output
    assert "hsoc-stack/components/primary_compute/linux" in output
    assert "O=build/local-apollo-qvp/work/linux" in output
    assert "ARCH=arm64" in output
    assert "CROSS_COMPILE=aarch64-poky-linux-" in output
    assert "menuconfig" in output


def test_zephyr_savedefconfig_dry_run_resolves_cmake_target() -> None:
    # Given: Zephyr is selected for a Kconfig savedefconfig action.
    # When: dry-run resolves the command.
    result = run_local_build("zephyr", "savedefconfig", "--dry-run")

    # Then: the CMake build context target and generated output path are shown.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "zephyr: savedefconfig" in output
    assert "cmake -S" in output
    assert "arm-zena-css/components/safety_island/zephyr/src/apps/sample" in output
    assert "-B" in output
    assert "build/local-apollo-qvp/work/zephyr-demos-cl1" in output
    assert "cmake --build" in output
    assert "--target savedefconfig" in output
    assert "generated defconfig: build/local-apollo-qvp/work/zephyr-demos-cl1/zephyr/defconfig" in output


def test_zephyr_kconfig_missing_deps_fail_with_recovery_message(
    tmp_path: Path,
) -> None:
    # Given: a non-dry Zephyr Kconfig action without SDK/dependency artifacts.
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        "ZEPHYR_SDK_INSTALL_DIR": "",
    }

    # When: the action tries to prepare the Zephyr CMake context.
    result = run_local_build("zephyr", "savedefconfig", extra_env=env)

    # Then: it fails before any interactive UI and names the recovery path.
    assert result.returncode != 0
    output = output_of(result)
    assert "ZEPHYR_SDK_INSTALL_DIR" in output
    assert "zephyr-demos-cl1" in output
    assert "Yocto" in output


def test_zephyr_deps_root_cache_skips_bitbake_env_on_warm_lookup(
    tmp_path: Path,
) -> None:
    # Given: Yocto dependency sources were discovered once for Zephyr.
    deps_root = tmp_path / "sources-unpack" / "git"
    for module in (
        "modules/hal/cmsis",
        "modules/hal/libmetal",
        "modules/lib/open-amp",
    ):
        (deps_root / module).mkdir(parents=True)
    modules_list = tmp_path / "apollo-modules.list"
    write_file(
        modules_list,
        "\n".join(
            (
                "modules/hal/cmsis",
                "modules/hal/libmetal",
                "modules/lib/open-amp",
                "arm_zena_safety_island",
                "zephyr_hsoc_src",
                "",
            )
        ),
    )
    lookup_log = tmp_path / "bitbake-getvar.log"
    local_build = tmp_path / "local-build"

    # When: the dependency root is requested twice in one local build tree.
    result = subprocess.run(
        (
            "bash",
            "-c",
            "\n".join(
                (
                    "set -euo pipefail",
                    'source "${ROOT_DIR}/scripts/build/local_build_common.sh"',
                    'source "${ROOT_DIR}/scripts/build/modules/build_zephyr.sh"',
                    "bitbake_zephyr_getvar() {",
                    '    printf "%s\\n" "$1" >> "${APOLLO_TEST_LOOKUP_LOG}"',
                    '    [[ "$1" == "UNPACKDIR" ]]',
                    '    printf "%s\\n" "${APOLLO_TEST_DEPS_ROOT%/git}"',
                    "}",
                    'first="$(prepare_yocto_zephyr_deps_root)"',
                    'second="$(prepare_yocto_zephyr_deps_root)"',
                    '[[ "${first}" == "${APOLLO_TEST_DEPS_ROOT}" ]]',
                    '[[ "${second}" == "${APOLLO_TEST_DEPS_ROOT}" ]]',
                )
            ),
        ),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "ROOT_DIR": str(ROOT),
            "LOCAL_BUILD_DIR": str(local_build),
            "ZEPHYR_MODULES_LIST": str(modules_list),
            "APOLLO_TEST_DEPS_ROOT": str(deps_root),
            "APOLLO_TEST_LOOKUP_LOG": str(lookup_log),
            "PATH": "/usr/bin:/bin",
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the warm lookup uses the cached root instead of bitbake -e.
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert lookup_log.read_text(encoding="utf-8").splitlines() == ["UNPACKDIR"]
    marker = local_build / "work" / "zephyr-demos-cl1" / ".apollo-zephyr-deps-root"
    assert marker.read_text(encoding="utf-8").strip() == str(deps_root)


def test_missing_sdk_is_populated_and_installed_by_local_build(
    tmp_path: Path,
) -> None:
    # Given: the new entrypoint is run without a populated Yocto SDK.
    tools_dir = tmp_path / "host-tools"
    bitbake_log = tmp_path / "bitbake.log"
    make_log = tmp_path / "make.log"
    sdk_dir = tmp_path / "missing-sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    for command in (
        "cmake",
        "ninja",
        "git",
        "openssl",
        "fiptool",
        "mkimage",
        "cert-to-efi-sig-list",
        "cpio",
        "gzip",
        "depmod",
        "sgdisk",
        "mkfs.vfat",
        "mcopy",
        "arm-none-eabi-gcc",
        "aarch64-none-elf-gcc",
        "aarch64-poky-linux-gcc",
    ):
        write_file(tools_dir / command, "#!/usr/bin/env bash\nexit 0\n")
        (tools_dir / command).chmod(0o755)
    write_file(
        tools_dir / "make",
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_MAKE_LOG}\"\n"
        "exit 0\n",
    )
    (tools_dir / "make").chmod(0o755)
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_BITBAKE_LOG}\"\n"
        "sdk_deploy=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk\"\n"
        "mkdir -p \"${sdk_deploy}\"\n"
        "installer=\"${sdk_deploy}/auto-ad-nexios-apollo-fvp-toolchain-test.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "dest=\"\"\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in\n"
        "        -d) dest=\"$2\"; shift 2 ;;\n"
        "        *) shift ;;\n"
        "    esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "cat > \"${dest}/environment-setup-apollo-test\" <<'ENV'\n"
        "export PATH=\"${APOLLO_TEST_TOOLS_DIR}:${PATH}\"\n"
        "export TARGET_PREFIX=\"aarch64-poky-linux-\"\n"
        "export OECORE_NATIVE_SYSROOT=\"${APOLLO_TEST_NATIVE_SYSROOT}\"\n"
        "export SDKTARGETSYSROOT=\"${APOLLO_TEST_TARGET_SYSROOT}\"\n"
        "ENV\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
        "APOLLO_TEST_MAKE_LOG": str(make_log),
        "APOLLO_TEST_NATIVE_SYSROOT": str(tmp_path / "native-sysroot"),
        "APOLLO_TEST_TARGET_SYSROOT": str(tmp_path / "target-sysroot"),
        "APOLLO_TEST_TOOLS_DIR": str(tools_dir),
        "BITBAKE": str(tools_dir / "bitbake"),
        "PATH": f"{tools_dir}:/usr/bin:/bin",
        "SDK_DIR": str(sdk_dir),
        "YOCTO_BUILD_DIR": str(yocto_build),
        "LOCAL_BUILD_DIR": str(local_build),
        "MACHINE": "apollo-fvp",
    }

    # When: a real Kconfig command reaches SDK setup.
    result = run_local_build("linux", "defconfig", "--no-package", extra_env=env)

    # Then: local_build.sh populates and installs the SDK before continuing.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "build_sdk: command not found" not in output
    assert "Yocto SDK not found" in output
    assert "populate and install it automatically" in output
    assert "can take a long time" in output
    assert output.index("Yocto SDK not found") < output.index("Starting linux-defconfig")
    assert (sdk_dir / "environment-setup-apollo-test").is_file()
    assert "nexios-image -c populate_sdk" in bitbake_log.read_text(
        encoding="utf-8"
    )
    make_args = make_log.read_text(encoding="utf-8")
    assert "ARCH=arm64" in make_args
    assert "CROSS_COMPILE=aarch64-poky-linux-" in make_args
    assert "defconfig" in make_args


def test_build_sdk_selects_installer_for_active_machine(tmp_path: Path) -> None:
    # Given: an old apollo-fvp SDK installer exists before an apollo-qvp SDK build.
    tools_dir = tmp_path / "host-tools"
    sdk_dir = tmp_path / "sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    deploy_sdk = yocto_build / "tmp_baremetal/deploy/sdk"
    bitbake_log = tmp_path / "bitbake.log"
    for path in (tools_dir, deploy_sdk):
        path.mkdir(parents=True)
    write_file(
        deploy_sdk / "auto-ad-nexios-apollo-fvp-toolchain-test.sh",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in -d) dest=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "printf 'old-fvp\\n' > \"${dest}/environment-setup-old-fvp\"\n",
    )
    (deploy_sdk / "auto-ad-nexios-apollo-fvp-toolchain-test.sh").chmod(0o755)
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_BITBAKE_LOG}\"\n"
        "installer=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk/"
        "auto-ad-nexios-apollo-qvp-toolchain-test.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in -d) dest=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "printf 'qvp\\n' > \"${dest}/environment-setup-apollo-qvp\"\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)

    command = "source scripts/build/local_build_common.sh; source scripts/build/modules/build_sdk.sh; build_sdk"
    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
            "BITBAKE": str(tools_dir / "bitbake"),
            "HOME": str(tmp_path),
            "MACHINE": "apollo-qvp",
            "PATH": f"{tools_dir}:/usr/bin:/bin",
            "SDK_DIR": str(sdk_dir),
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: build_sdk ignores the stale fvp installer and installs qvp.
    assert result.returncode == 0, output_of(result)
    assert (sdk_dir / "environment-setup-apollo-qvp").read_text(
        encoding="utf-8"
    ) == "qvp\n"
    assert not (sdk_dir / "environment-setup-old-fvp").exists()
    assert "nexios-image -c populate_sdk" in bitbake_log.read_text(
        encoding="utf-8"
    )


def test_build_sdk_forces_populate_sdk_when_stamp_kept_but_installer_deleted(
    tmp_path: Path,
) -> None:
    # Given: populate_sdk is stamped complete, but its deploy/sdk installer was removed.
    tools_dir = tmp_path / "host-tools"
    sdk_dir = tmp_path / "sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    bitbake_log = tmp_path / "bitbake.log"
    tools_dir.mkdir(parents=True)
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_BITBAKE_LOG}\"\n"
        "case \" $* \" in\n"
        "    *' -f '*) ;;\n"
        "    *) exit 0 ;;\n"
        "esac\n"
        "sdk_deploy=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk\"\n"
        "mkdir -p \"${sdk_deploy}\"\n"
        "installer=\"${sdk_deploy}/auto-ad-nexios-apollo-qvp-toolchain-forced.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in -d) dest=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "printf 'forced-qvp\\n' > \"${dest}/environment-setup-apollo-qvp\"\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)

    command = "source scripts/build/local_build_common.sh; source scripts/build/modules/build_sdk.sh; build_sdk"
    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        check=False,
        env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
            "BITBAKE": str(tools_dir / "bitbake"),
            "HOME": str(tmp_path),
            "MACHINE": "apollo-qvp",
            "PATH": f"{tools_dir}:/usr/bin:/bin",
            "SDK_DIR": str(sdk_dir),
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: build_sdk retries with -f and installs the regenerated qvp SDK.
    assert result.returncode == 0, output_of(result)
    assert (sdk_dir / "environment-setup-apollo-qvp").read_text(
        encoding="utf-8"
    ) == "forced-qvp\n"
    bitbake_calls = bitbake_log.read_text(encoding="utf-8").splitlines()
    assert bitbake_calls[0].endswith("nexios-image -c populate_sdk")
    assert bitbake_calls[1].endswith("nexios-image -c populate_sdk -f")


def test_refresh_sdk_forces_populate_and_clean_reinstall(tmp_path: Path) -> None:
    tools_dir = tmp_path / "host-tools"
    sdk_dir = tmp_path / "sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    bitbake_log = tmp_path / "bitbake.log"
    tools_dir.mkdir(parents=True)
    sdk_dir.mkdir()
    write_file(sdk_dir / "environment-setup-old", "old-sdk\n")
    write_file(sdk_dir / "stale-sdk-file", "stale\n")
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_BITBAKE_LOG}\"\n"
        "deploy=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk\"\n"
        "mkdir -p \"${deploy}\"\n"
        "installer=\"${deploy}/auto-ad-nexios-apollo-qvp-toolchain-refresh.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "dest=''\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in -d) dest=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "printf 'refreshed-sdk\\n' > \"${dest}/environment-setup-refreshed\"\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)

    result = run_local_build(
        "--refresh-sdk",
        extra_env={
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
            "BITBAKE": str(tools_dir / "bitbake"),
            "MACHINE": "apollo-qvp",
            "PATH": f"{tools_dir}:/usr/bin:/bin",
            "SDK_DIR": str(sdk_dir),
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
        },
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "Yocto SDK generation can take a long time" in output
    assert "Reinstalling Yocto SDK" in output
    assert "Starting qbox-build" not in output
    assert bitbake_log.read_text(encoding="utf-8").strip().endswith(
        "nexios-image -c populate_sdk -f"
    )
    assert (sdk_dir / "environment-setup-refreshed").read_text(
        encoding="utf-8"
    ) == "refreshed-sdk\n"
    assert not (sdk_dir / "environment-setup-old").exists()
    assert not (sdk_dir / "stale-sdk-file").exists()
    assert not list(tmp_path.glob("sdk.refresh-backup.*"))


def test_refresh_sdk_restores_previous_sdk_when_install_fails(tmp_path: Path) -> None:
    tools_dir = tmp_path / "host-tools"
    sdk_dir = tmp_path / "sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    tools_dir.mkdir(parents=True)
    sdk_dir.mkdir()
    write_file(sdk_dir / "environment-setup-old", "old-sdk\n")
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "deploy=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk\"\n"
        "mkdir -p \"${deploy}\"\n"
        "installer=\"${deploy}/auto-ad-nexios-apollo-qvp-toolchain-refresh.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "dest=''\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in -d) dest=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "printf 'partial-sdk\\n' > \"${dest}/partial\"\n"
        "exit 42\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)

    result = run_local_build(
        "--refresh-sdk",
        extra_env={
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "BITBAKE": str(tools_dir / "bitbake"),
            "MACHINE": "apollo-qvp",
            "PATH": f"{tools_dir}:/usr/bin:/bin",
            "SDK_DIR": str(sdk_dir),
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
        },
    )

    assert result.returncode == 42, output_of(result)
    assert "restoring the previous SDK" in output_of(result)
    assert (sdk_dir / "environment-setup-old").read_text(encoding="utf-8") == (
        "old-sdk\n"
    )
    assert not (sdk_dir / "partial").exists()
    assert not list(tmp_path.glob("sdk.refresh-backup.*"))


def test_qbox_build_checks_sdk_before_cmake(tmp_path: Path) -> None:
    # Given: QBox is requested and the Yocto SDK is not installed yet.
    tools_dir = tmp_path / "host-tools"
    bitbake_log = tmp_path / "bitbake.log"
    cmake_log = tmp_path / "cmake.log"
    sdk_dir = tmp_path / "missing-sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    qbox_core = tmp_path / "qbox"
    qbox_platform = tmp_path / "qbox-platform"
    qbox_qemu = tmp_path / "qemu"
    for path in (tools_dir, qbox_core, qbox_platform, qbox_qemu):
        path.mkdir(parents=True)
    write_file(
        tools_dir / "cmake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_CMAKE_LOG}\"\n"
        "build_dir=\"\"\n"
        "prev=\"\"\n"
        "for arg in \"$@\"; do\n"
        "    if [[ \"${prev}\" == \"-B\" ]]; then\n"
        "        build_dir=\"${arg}\"\n"
        "    fi\n"
        "    prev=\"${arg}\"\n"
        "done\n"
        "if [[ -n \"${build_dir}\" ]]; then\n"
        "    mkdir -p \"${build_dir}\"\n"
        "    printf 'CMAKE_HOME_DIRECTORY:INTERNAL=%s\\n' "
        "\"${QBOX_PLATFORM_DIR}\" > \"${build_dir}/CMakeCache.txt\"\n"
        "    : > \"${build_dir}/build.ninja\"\n"
        "fi\n",
    )
    (tools_dir / "cmake").chmod(0o755)
    write_file(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"${APOLLO_TEST_BITBAKE_LOG}\"\n"
        "sdk_deploy=\"${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/sdk\"\n"
        "mkdir -p \"${sdk_deploy}\"\n"
        "installer=\"${sdk_deploy}/auto-ad-nexios-apollo-fvp-toolchain-test.sh\"\n"
        "cat > \"${installer}\" <<'SDK'\n"
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "dest=\"\"\n"
        "while (($# > 0)); do\n"
        "    case \"$1\" in\n"
        "        -d) dest=\"$2\"; shift 2 ;;\n"
        "        *) shift ;;\n"
        "    esac\n"
        "done\n"
        "mkdir -p \"${dest}\"\n"
        "cat > \"${dest}/environment-setup-apollo-test\" <<'ENV'\n"
        "export PATH=\"${APOLLO_TEST_TOOLS_DIR}:${PATH}\"\n"
        "export TARGET_PREFIX=\"aarch64-poky-linux-\"\n"
        "ENV\n"
        "SDK\n"
        "chmod +x \"${installer}\"\n",
    )
    (tools_dir / "bitbake").chmod(0o755)
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
        "APOLLO_TEST_CMAKE_LOG": str(cmake_log),
        "APOLLO_TEST_TOOLS_DIR": str(tools_dir),
        "BITBAKE": str(tools_dir / "bitbake"),
        "PATH": f"{tools_dir}:/usr/bin:/bin",
        "SDK_DIR": str(sdk_dir),
        "YOCTO_BUILD_DIR": str(yocto_build),
        "LOCAL_BUILD_DIR": str(local_build),
        "MACHINE": "apollo-fvp",
        "QBOX_CORE_DIR": str(qbox_core),
        "QBOX_PLATFORM_DIR": str(qbox_platform),
        "QBOX_QEMU_DIR": str(qbox_qemu),
    }

    # When: QBox is built through local_build.sh.
    result = run_local_build("qbox", extra_env=env)

    # Then: SDK installation is checked before the QBox CMake build starts.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert output.index("Yocto SDK not found") < output.index("Starting qbox-build")
    assert "Starting package" not in output
    assert (sdk_dir / "environment-setup-apollo-test").is_file()
    assert "nexios-image -c populate_sdk" in bitbake_log.read_text(
        encoding="utf-8"
    )
    cmake_args = cmake_log.read_text(encoding="utf-8")
    assert f"-S {qbox_platform}" in cmake_args
    assert "--target apollo_fvp_full_system" in cmake_args


def test_qbox_systemc_tests_option_runs_ctest_after_qbox_build(tmp_path: Path) -> None:
    tools_dir = tmp_path / "host-tools"
    call_log = tmp_path / "calls.log"
    sdk_dir = tmp_path / "sdk"
    yocto_build = tmp_path / "yocto-build"
    local_build = tmp_path / "local-build"
    qbox_core = tmp_path / "qbox"
    qbox_platform = tmp_path / "qbox-platform"
    qbox_qemu = tmp_path / "qemu"
    native_bin = sdk_dir / "sysroots/x86_64-pokysdk-linux/usr/bin"
    for path in (tools_dir, sdk_dir, qbox_core, qbox_platform, qbox_qemu):
        path.mkdir(parents=True)
    native_bin.mkdir(parents=True)
    write_file(sdk_dir / "environment-setup-apollo-test", "export TARGET_PREFIX=aarch64-test-\n")
    for tool in ("python3", "meson", "meson.real"):
        write_file(native_bin / tool, "#!/bin/sh\nexit 0\n")
        (native_bin / tool).chmod(0o755)
    write_file(
        tools_dir / "cmake",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'cmake path=%s python-no-user-site=%s args=%s\\n' \"${PATH%%:*}\" \"${PYTHONNOUSERSITE:-}\" \"$*\" >> \"${APOLLO_TEST_CALL_LOG}\"\n"
        "build_dir=''\n"
        "prev=''\n"
        "for arg in \"$@\"; do\n"
        "    if [[ \"${prev}\" == '-B' ]]; then build_dir=\"${arg}\"; fi\n"
        "    prev=\"${arg}\"\n"
        "done\n"
        "if [[ -n \"${build_dir}\" ]]; then\n"
        "    mkdir -p \"${build_dir}\"\n"
        "    printf 'CMAKE_HOME_DIRECTORY:INTERNAL=%s\\n' \"${QBOX_PLATFORM_DIR}\" > \"${build_dir}/CMakeCache.txt\"\n"
        "    : > \"${build_dir}/build.ninja\"\n"
        "fi\n",
    )
    write_file(
        tools_dir / "ctest",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'ctest path=%s python-no-user-site=%s args=%s\\n' \"${PATH%%:*}\" \"${PYTHONNOUSERSITE:-}\" \"$*\" >> \"${APOLLO_TEST_CALL_LOG}\"\n",
    )
    write_file(
        tools_dir / "ccache",
        "#!/usr/bin/env bash\n"
        "exec \"$@\"\n",
    )
    (tools_dir / "cmake").chmod(0o755)
    (tools_dir / "ctest").chmod(0o755)
    (tools_dir / "ccache").chmod(0o755)

    result = run_local_build(
        "qbox",
        "--qbox-unit-tests",
        extra_env={
            "APOLLO_TEST_CALL_LOG": str(call_log),
            "PATH": f"{tools_dir}:/usr/bin:/bin",
            "SDK_DIR": str(sdk_dir),
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_CORE_DIR": str(qbox_core),
            "QBOX_PLATFORM_DIR": str(qbox_platform),
            "QBOX_QEMU_DIR": str(qbox_qemu),
        },
    )

    assert result.returncode == 0, output_of(result)
    calls = call_log.read_text(encoding="utf-8")
    assert f"-DCMAKE_C_COMPILER_LAUNCHER={tools_dir / 'ccache'}" in calls
    assert f"-DCMAKE_CXX_COMPILER_LAUNCHER={tools_dir / 'ccache'}" in calls
    assert "--target apollo_fvp_full_system" in calls
    assert "--target qbox_platform_systemc_component_tests" in calls
    assert "--test-dir" in calls
    assert "-L qbox-platform-systemc-components" in calls
    assert calls.index("--target apollo_fvp_full_system") < calls.index("ctest ")
    tool_shim = local_build / "work/qbox-platform/.qbox-sdk-native-tools"
    build_lines = [
        line
        for line in calls.splitlines()
        if line.startswith("cmake ") and "--build" in line
    ]
    assert len(build_lines) == 2
    ctest_line = next(
        line for line in calls.splitlines() if line.startswith("ctest ")
    )
    for line in (*build_lines, ctest_line):
        assert f"path={tool_shim}" in line
        assert "python-no-user-site=1" in line
    timing = (local_build / "logs" / "local-build-timings.tsv").read_text(
        encoding="utf-8"
    )
    assert "kind\tname\tstatus\tseconds\telapsed\tlog" in timing
    rows = [line.split("\t") for line in timing.splitlines()[1:]]
    assert ["command", "qbox-build", "0"] in [row[:3] for row in rows]
    assert ["command", "qbox-unit-test-build", "0"] in [row[:3] for row in rows]
    assert ["command", "qbox-unit-tests", "0"] in [row[:3] for row in rows]
    assert ["step", "qbox-build", "0"] in [row[:3] for row in rows]


def test_linux_clean_dry_run_shows_only_linux_owned_outputs() -> None:
    # Given: a scoped Linux clean request.
    # When: dry-run resolves the cleanup.
    result = run_local_build("linux", "clean", "--dry-run")

    # Then: only Linux work/deploy ownership is listed.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["linux: clean"]
    assert "work/linux" in output
    assert "deploy/boot/Image" in output
    assert "deploy/boot/apollo-qvp.dtb" in output
    assert "work/trusted-firmware-m" not in output
    assert "work/scp-firmware" not in output
    assert "work/zephyr-demos-cl1" not in output
    assert "work/optee-os" not in output
    assert "work/u-boot" not in output
    assert "work/trusted-firmware-a" not in output
    assert "build/tmp_baremetal/deploy/images/apollo-fvp" not in output


def test_tfa_build_dry_run_documents_local_firmware_dependencies() -> None:
    # Given: TF-A needs local BL32/BL33 inputs from earlier components.
    # When: dry-run resolves a scoped TF-A build.
    result = run_local_build("tf-a", "build", "--dry-run")

    # Then: the dependency note names the required local artifacts.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "requires existing local U-Boot and OP-TEE artifacts" in output
    assert "deploy/u-boot/u-boot.bin" in output
    assert "deploy/optee/tee-pager_v2.bin" in output


def test_scp_firmware_dry_run_documents_bare_metal_cmake_probes() -> None:
    # Given: SCP firmware uses an aarch64-none-elf bare-metal compiler.
    # When: dry-run resolves a scoped SCP firmware build.
    result = run_local_build("scp-firmware", "build", "--dry-run")

    # Then: configure metadata states which bare-metal CMake probes are controlled.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "scp-firmware: build" in output
    assert "-DCMAKE_SYSTEM_NAME=Generic" in output
    assert "-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY" in output
    assert "SCP cross-compile IPO executable probe is skipped" in output
    assert "benign executable-link fallback" in output


def test_tfm_clean_dry_run_invalidates_package_manifest_without_yocto_deploy() -> None:
    # Given: TF-M contributes local firmware consumed by downstream packaging.
    # When: dry-run resolves a scoped TF-M clean.
    result = run_local_build("tf-m", "clean", "--dry-run")

    # Then: local package manifests are invalidated and Yocto deploy is untouched.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == ["tf-m: clean"]
    assert "invalidate package manifests:" in output
    assert "deploy/local-package-manifest.json" in output
    assert "deploy/firmware/.apollo-flash-images.manifest" in output
    assert "build/tmp_baremetal/deploy/images/apollo-fvp" not in output


def write_file(path: Path, content: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def symlink_force(target: str, link: Path) -> None:
    try:
        link.symlink_to(target)
    except OSError:
        write_file(link, (link.parent / target).read_bytes())


def tree_snapshot(root: Path) -> dict[str, bytes | str]:
    snapshot: dict[str, bytes | str] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            snapshot[relative] = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            snapshot[relative] = path.read_bytes()
        elif path.is_dir():
            snapshot[relative] = "dir"
    return snapshot


def make_package_fixture(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    yocto_deploy = tmp_path / "yocto-deploy"
    local_build = tmp_path / "local-build"
    local_fw = local_build / "deploy" / "firmware"
    machine = "apollo-fvp"
    timestamp = "20260102030405"

    for name in (
        "rse-rom-image.img",
        "rse-flash-image.img",
        "rse-otp-image.img",
        "ap-flash-image.img",
        "combined_provisioning_message.bin",
    ):
        write_file(yocto_deploy / name, f"yocto-{name}\n")
        write_file(local_fw / name, f"local-{name}\n")

    write_file(yocto_deploy / f"nexios-image-{machine}-{timestamp}.wic", b"yocto-wic\n")
    write_file(
        yocto_deploy / f"nexios-image-{machine}-{timestamp}.manifest",
        "yocto manifest\n",
    )
    write_file(
        yocto_deploy / f"nexios-image-{machine}-{timestamp}.testdata.json",
        "{}\n",
    )
    write_file(
        yocto_deploy / f"nexios-image-{machine}-{timestamp}.ext4.verity",
        b"verity\n",
    )
    write_file(
        yocto_deploy / f"nexios-image-{machine}-{timestamp}.ext4.verity.env",
        "verity env\n",
    )
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.wic",
        yocto_deploy / f"nexios-image-{machine}.wic",
    )
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.manifest",
        yocto_deploy / f"nexios-image-{machine}.manifest",
    )
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.testdata.json",
        yocto_deploy / f"nexios-image-{machine}.testdata.json",
    )
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.ext4.verity",
        yocto_deploy / f"nexios-image-{machine}.ext4.verity",
    )
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.ext4.verity.env",
        yocto_deploy / f"nexios-image-{machine}.ext4.verity.env",
    )

    for name in (
        "auto-ad-nexios-a.efi",
        "auto-ad-nexios-b.efi",
        f"nexios-initramfs-image-{machine}.cpio.gz",
        "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        "efi-capsule-update-image.img.json",
        "efi-capsule-update-image.img.uefi.capsule",
        "nexios-image.env",
    ):
        write_file(yocto_deploy / name, f"yocto-{name}\n")
    write_file(
        yocto_deploy / f"u-boot-{machine}-2026.01+git-r0.bin",
        b"yocto-u-boot\n",
    )
    write_file(
        yocto_deploy / f"u-boot-initial-env-{machine}-2026.01+git-r0",
        b"yocto-u-boot-env\n",
    )

    fvpconf_timestamp = yocto_deploy / f"nexios-image-{machine}-{timestamp}.fvpconf"
    fvpconf = {
        "parameters": {
            "css.smb.rseil.rse.rom.raw_image": str(yocto_deploy / "rse-rom-image.img"),
            "css.smb.rseil.rse_flashloader.fname": str(
                yocto_deploy / "rse-flash-image.img"
            ),
            "css.smb.rseil.rse_flashloader.fnameWrite": str(
                yocto_deploy / "rse-flash-image.img"
            ),
            "css.smb.rseil.rse.lcm_nvm.raw_image": str(
                yocto_deploy / "rse-otp-image.img"
            ),
            "ros.flash_loader.fname": str(yocto_deploy / "ap-flash-image.img"),
            "ros.flash_loader.fnameWrite": str(yocto_deploy / "ap-flash-image.img"),
            "ros.virtio_block0.image_path": str(
                yocto_deploy / f"nexios-image-{machine}.wic"
            ),
            "ros.virtio_block1.image_path": str(
                yocto_deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img"
            ),
        },
        "data": [
            f"css.smb.rseil.rse.sram1={yocto_deploy / 'combined_provisioning_message.bin'}@0x20000"
        ],
    }
    write_file(fvpconf_timestamp, json.dumps(fvpconf, indent=2) + "\n")
    symlink_force(
        f"nexios-image-{machine}-{timestamp}.fvpconf",
        yocto_deploy / f"nexios-image-{machine}.fvpconf",
    )

    env = {
        "YOCTO_DEPLOY_DIR": str(yocto_deploy),
        "LOCAL_BUILD_DIR": str(local_build),
        "KERNEL_DEVICETREE": "arm/apollo-fvp.dtb",
        "MACHINE": machine,
    }
    return yocto_deploy, local_build, env


def write_yocto_vars(path: Path, variables: dict[str, str]) -> None:
    write_yocto_recipe_vars(path, {"nexios-image": variables})


def write_yocto_recipe_vars(
    path: Path,
    recipe_variables: dict[str, dict[str, str]],
) -> None:
    write_file(
        path,
        json.dumps(
            {
                "schema_version": 1,
                "recipes": {
                    recipe: {
                        "command": f"fixture bitbake -e {recipe}",
                        "variables": variables,
                    }
                    for recipe, variables in recipe_variables.items()
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def test_tfm_build_dry_run_resolves_platform_from_local_build_conf(
    tmp_path: Path,
) -> None:
    # Given: a reviewed local build configuration selects the FVP TF-M platform.
    config_path = tmp_path / "local_build.conf"
    write_file(
        config_path,
        'MACHINE="${MACHINE-apollo-fvp}"\n'
        'TFM_PLATFORM="${TFM_PLATFORM-arm/rse/automotive_rd/apollo-fvp}"\n',
    )

    # When: the local TF-M build plan is resolved from that configuration.
    result = run_local_build(
        "tf-m",
        "--dry-run",
        extra_env={"LOCAL_BUILD_CONFIG": str(config_path)},
    )

    # Then: the configure metadata carries a non-empty Apollo platform.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "tf-m: build" in output
    assert "-DTFM_PLATFORM=arm/rse/automotive_rd/apollo-fvp" in output
    assert "-DCROSS_COMPILE=arm-none-eabi" in output


def test_local_build_conf_is_loaded_without_yocto_cache_refresh(
    tmp_path: Path,
) -> None:
    # Given: obsolete cache inputs and a reviewed local build configuration.
    vars_path = tmp_path / "yocto-local-build-vars.json"
    write_yocto_recipe_vars(
        vars_path,
        {"nexios-image": {"MACHINE": "stale-machine"}},
    )
    config_path = tmp_path / "local_build.conf"
    write_file(
        config_path,
        'MACHINE="${MACHINE-apollo-qvp}"\n'
        'RD_ASPEN_VARIANT="${RD_ASPEN_VARIANT-reviewed-cfg}"\n'
        'UBOOT_MACHINE="${UBOOT_MACHINE-reviewed_defconfig}"\n',
    )
    tools_dir = tmp_path / "tools"
    collector_log = add_fake_collector_python(
        tools_dir,
        tmp_path,
        {
            "nexios-image": {
                "MACHINE": "apollo-fvp",
                "RD_ASPEN_VARIANT": "fresh-cfg",
                "PC_CPUS_COUNT_DEFAULT": "4",
            },
            "u-boot": {
                "MACHINE": "apollo-fvp",
                "UBOOT_MACHINE": "fresh_defconfig",
            },
        },
    )

    # When: obsolete cache controls are present during a dry-run.
    result = run_local_build(
        "u-boot",
        "defconfig",
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "1",
            "APOLLO_LOCAL_BUILD_YOCTO_VARS": str(vars_path),
            "LOCAL_BUILD_CONFIG": str(config_path),
            "PATH": f"{tools_dir}:/usr/bin:/bin",
        },
    )

    # Then: only local_build.conf affects the plan and no collector runs.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "refreshing stale Yocto local-build vars" not in output
    assert "stale-machine" not in output
    assert "RD_ASPEN_VARIANT=reviewed-cfg reviewed_defconfig defconfig" in output
    assert not collector_log.exists()


def test_tfm_build_dry_run_rejects_unresolved_platform() -> None:
    # Given: the caller overrides TF-M to a platform that cannot be resolved.
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "TFM_PLATFORM": "missing/platform",
    }

    # When: the local TF-M build plan is resolved.
    result = run_local_build("tf-m", "--dry-run", extra_env=env)

    # Then: the CLI fails before configure with an actionable recovery hint.
    assert result.returncode != 0
    output = output_of(result)
    assert "TFM_PLATFORM" in output
    assert "missing/platform" in output
    assert "local_build.conf" in output


def add_local_linux_fixture(
    local_build: Path,
    *,
    dtb_name: str = "apollo-fvp.dtb",
    modules: bool = True,
) -> None:
    write_file(local_build / "deploy" / "boot" / "Image", b"local-linux-image\n")
    write_file(local_build / "deploy" / "boot" / dtb_name, b"local-dtb\n")
    if modules:
        linux_build = local_build / "work" / "linux"
        write_file(linux_build / "include" / "config" / "kernel.release", "6.6.1-local\n")
        write_file(linux_build / "drivers" / "net" / "pfdi_misc.ko", b"module-ko\n")
        write_file(linux_build / "modules.order", "drivers/net/pfdi_misc.ko\n")


def add_uki_source_fixture(yocto_deploy: Path) -> None:
    write_file(yocto_deploy / "linuxaa64.efi.stub", b"stub\n")
    write_file(yocto_deploy / "nexios-initramfs-image-apollo-fvp.cpio.gz", b"initrd\n")


def add_local_initramfs_fixture(local_build: Path) -> None:
    write_file(local_build / "deploy" / "boot" / "initramfs.cpio.gz", b"local-initrd\n")


def add_stub_uki_tools(tmp_path: Path) -> tuple[Path, Path, Path]:
    tools_dir = tmp_path / "stub-tools"
    ukify_log = tmp_path / "ukify.log"
    wic_log = tmp_path / "wic-tools.log"
    write_file(
        tools_dir / "ukify",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'ukify %q' \"$0\" >> \"${UKIFY_LOG}\"\n"
        "for arg in \"$@\"; do printf ' %q' \"$arg\" >> \"${UKIFY_LOG}\"; done\n"
        "printf '\\n' >> \"${UKIFY_LOG}\"\n"
        "out=''\n"
        "cmd=''\n"
        "for arg in \"$@\"; do\n"
        "  case \"$arg\" in\n"
        "    --output=*) out=\"${arg#--output=}\" ;;\n"
        "    --cmdline=*) cmd=\"${arg#--cmdline=}\" ;;\n"
        "  esac\n"
        "done\n"
        "mkdir -p \"$(dirname \"$out\")\"\n"
        "printf 'stub-uki\\ncmdline=%s\\n' \"$cmd\" > \"$out\"\n",
    )
    write_file(
        tools_dir / "sgdisk",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'sgdisk %s\\n' \"$*\" >> \"${WIC_TOOL_LOG}\"\n"
        "cat <<'OUT'\n"
        "Number  Start (sector)    End (sector)  Size       Code  Name\n"
        "   1            2048          264191   128.0 MiB   EF00  boot_a\n"
        "   2          264192          526335   128.0 MiB   EF00  boot_b\n"
        "   4          534528        17311743   8192.0 MiB  8300  rootro_a\n"
        "   5        17311744        34088959   8192.0 MiB  8300  rootro_b\n"
        "OUT\n",
    )
    write_file(
        tools_dir / "mdir",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'mdir %s\\n' \"$*\" >> \"${WIC_TOOL_LOG}\"\n"
        "exit \"${APOLLO_STUB_MDIR_RC:-1}\"\n",
    )
    write_file(
        tools_dir / "mmd",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'mmd %s\\n' \"$*\" >> \"${WIC_TOOL_LOG}\"\n",
    )
    write_file(
        tools_dir / "mcopy",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf 'mcopy %s\\n' \"$*\" >> \"${WIC_TOOL_LOG}\"\n"
        "if [[ \"${APOLLO_STUB_MCOPY_FAIL:-0}\" == '1' ]]; then\n"
        "  printf 'stub mcopy failure\\n' >&2\n"
        "  exit 9\n"
        "fi\n"
        "image=''\n"
        "source=''\n"
        "prev=''\n"
        "for arg in \"$@\"; do\n"
        "  if [[ \"$prev\" == '-i' ]]; then image=\"${arg%%@@*}\"; fi\n"
        "  if [[ -f \"$arg\" ]]; then source=\"$arg\"; fi\n"
        "  prev=\"$arg\"\n"
        "done\n"
        "printf '\\npatched:%s\\n' \"$(basename \"$source\")\" >> \"$image\"\n",
    )
    for tool in ("ukify", "sgdisk", "mdir", "mmd", "mcopy"):
        (tools_dir / tool).chmod(0o755)
    return tools_dir, ukify_log, wic_log


def add_fake_collector_python(
    tools_dir: Path,
    tmp_path: Path,
    recipe_variables: dict[str, dict[str, str]],
) -> Path:
    collector_log = tmp_path / "collector.log"
    payload = json.dumps(
        {
            "schema_version": 1,
            "recipes": {
                recipe: {
                    "command": f"fixture refreshed bitbake -e {recipe}",
                    "variables": variables,
                }
                for recipe, variables in recipe_variables.items()
            },
        },
        indent=2,
        sort_keys=True,
    )
    write_file(
        tools_dir / "python3",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ \"${1:-}\" == */scripts/build/collect_yocto_local_build_vars.py ]]; then\n"
        f"  printf 'collector %q' \"$1\" > {str(collector_log)!r}\n"
        "  out=''\n"
        "  while (($# > 0)); do\n"
        "    if [[ \"$1\" == '--output' ]]; then\n"
        "      out=\"$2\"\n"
        "      shift 2\n"
        "      continue\n"
        "    fi\n"
        "    shift\n"
        "  done\n"
        "  if [[ -z \"$out\" ]]; then\n"
        "    printf 'missing --output\\n' >&2\n"
        "    exit 2\n"
        "  fi\n"
        "  mkdir -p \"$(dirname \"$out\")\"\n"
        "  cat > \"$out\" <<'JSON'\n"
        f"{payload}\n"
        "JSON\n"
        "  exit 0\n"
        "fi\n"
        "exec /usr/bin/python3 \"$@\"\n",
    )
    (tools_dir / "python3").chmod(0o755)
    return collector_log


def local_uki_env(
    base_env: dict[str, str],
    vars_path: Path,
    tools_dir: Path,
    ukify_log: Path,
    wic_log: Path,
) -> dict[str, str]:
    raw = json.loads(vars_path.read_text(encoding="utf-8"))
    variables = raw["recipes"]["nexios-image"]["variables"]
    return base_env | variables | {
        "PATH": f"{tools_dir}:/usr/bin:/bin",
        "UKIFY_LOG": str(ukify_log),
        "WIC_TOOL_LOG": str(wic_log),
    }


def default_uki_variables(ukify: Path) -> dict[str, str]:
    return {
        "MACHINE": "apollo-fvp",
        "KERNEL_CONSOLE": "ttyAMA0",
        "EFI_ARCH": "aa64",
        "INITRD_ARCHIVE": "nexios-initramfs-image-apollo-fvp.cpio.gz",
        "AUTO_AD_NEXIOS_UKI_A": "auto-ad-nexios-a.efi",
        "AUTO_AD_NEXIOS_UKI_B": "auto-ad-nexios-b.efi",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_A": "rootwait root=PARTLABEL=rootro_a ro console=ttyAMA0",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_B": "rootwait root=PARTLABEL=rootro_b ro console=ttyAMA0",
        "UKIFY_CMD": str(ukify),
        "UEFI_SECURE_BOOT": "0",
    }


def with_fixture_flash_hook(env: dict[str, str], log_path: Path) -> dict[str, str]:
    return env | {
        "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE": "fixture",
        "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_LOG": str(log_path),
    }


def test_package_dry_run_resolves_without_mutation_claim() -> None:
    result = run_local_build("--package", "--dry-run")

    assert result.returncode == 0, output_of(result)
    output = output_of(result).lower()
    assert "package: local fvp deploy" in output
    assert "todo 6" not in output
    assert "complete" not in output
    assert "success" not in output
    assert "package_flash_images" in output


def test_package_fixture_writes_local_fvpconf_and_manifest(tmp_path: Path) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    hook_log = tmp_path / "package-flash-hook.log"

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, hook_log),
    )

    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "Starting package" in output
    assert "Completed package in " in output
    assert output.index("Starting package") < output.index("Completed package")
    assert hook_log.read_text(encoding="utf-8").splitlines() == ["package_flash_images"]
    local_deploy = local_build / "deploy"
    local_fvpconf = local_deploy / "apollo-fvp-local.fvpconf"
    manifest_path = local_deploy / "local-package-manifest.json"
    assert local_fvpconf.is_file()
    assert manifest_path.is_file()
    assert (local_deploy / "images" / "nexios-image-apollo-fvp.wic").read_bytes() == b"yocto-wic\n"
    assert (local_deploy / "firmware" / "ap-flash-image.img").read_text(
        encoding="utf-8"
    ) == "local-ap-flash-image.img\n"

    rewritten = json.loads(local_fvpconf.read_text(encoding="utf-8"))
    rewritten_text = json.dumps(rewritten)
    assert str(yocto_deploy) not in rewritten_text
    assert str(local_deploy / "firmware") in rewritten_text
    assert str(local_deploy / "images") in rewritten_text
    assert (
        rewritten["parameters"]["ros.virtio_block0.image_path"]
        == str(local_deploy / "images" / "nexios-image-apollo-fvp.wic")
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["source_preservation"]["all_sources_preserved"] is True
    entries = {entry["local_path"]: entry for entry in manifest["artifacts"]}
    wic_entry = entries[str(local_deploy / "images" / "nexios-image-apollo-fvp.wic")]
    assert wic_entry["source_path"] == str(yocto_deploy / "nexios-image-apollo-fvp.wic")
    assert wic_entry["component_provenance"] == "yocto-copied"
    assert wic_entry["size"] == len(b"yocto-wic\n")
    assert len(wic_entry["sha256"]) == 64
    fw_entry = entries[str(local_deploy / "firmware" / "ap-flash-image.img")]
    assert fw_entry["component_provenance"] == "local-firmware-overlay"
    assert fw_entry["source_preserved"] is True


def test_package_deduplicates_repeated_copied_artifacts_in_manifest(
    tmp_path: Path,
) -> None:
    # Given: the default FVP config references artifacts also copied as side files.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)

    # When: the local FVP package is generated.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: repeated source/destination copies are recorded once.
    assert result.returncode == 0, output_of(result)
    local_deploy = local_build / "deploy"
    manifest = json.loads(
        (local_deploy / "local-package-manifest.json").read_text(encoding="utf-8")
    )
    artifact_paths = [entry["local_path"] for entry in manifest["artifacts"]]
    for name in (
        "nexios-image-apollo-fvp.wic",
        "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        "nexios-initramfs-image-apollo-fvp.cpio.gz",
    ):
        assert artifact_paths.count(str(local_deploy / "images" / name)) == 1


def test_package_copies_every_fvp_image_path_reference(tmp_path: Path) -> None:
    # Given: Yocto fvpconf references an extra image_path outside the old allowlist.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    extra_image = yocto_deploy / "pcie-extra-disk.img"
    write_file(extra_image, b"extra disk\n")
    fvpconf_path = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["pcie_group_0.test_device.image_path"] = str(extra_image)
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: the local FVP package is generated.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: every image_path in the final fvpconf points at a copied local file.
    assert result.returncode == 0, output_of(result)
    local_deploy = local_build / "deploy"
    local_fvpconf = local_deploy / "apollo-fvp-local.fvpconf"
    rewritten = json.loads(local_fvpconf.read_text(encoding="utf-8"))
    image_parameters = {
        key: value
        for key, value in rewritten["parameters"].items()
        if key.endswith(".image_path")
    }
    assert image_parameters
    for key, value in image_parameters.items():
        assert str(local_deploy / "images") in value, key
        assert Path(value).is_file(), key
    assert (local_deploy / "images" / "pcie-extra-disk.img").read_bytes() == b"extra disk\n"


def test_package_skips_empty_image_path_ahci_placeholder(tmp_path: Path) -> None:
    # Given: Apollo fvpconf contains an AHCI placeholder image_path with an
    # empty value.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    fvpconf_path = (
        tmp_path
        / "yocto-deploy"
        / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    )
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["ros.ahci0.image_path"] = ""
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: the local FVP package is generated.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: the empty placeholder is preserved and not treated as Path(".").
    assert result.returncode == 0, output_of(result)
    local_fvpconf = local_build / "deploy" / "apollo-fvp-local.fvpconf"
    rewritten = json.loads(local_fvpconf.read_text(encoding="utf-8"))
    assert rewritten["parameters"]["ros.ahci0.image_path"] == ""
    assert not (local_build / "deploy" / "images" / ".").is_file()


def test_package_rejects_missing_relative_image_path_without_preserving_it(
    tmp_path: Path,
) -> None:
    # Given: Apollo fvpconf contains a non-empty relative image_path that is not
    # a real Yocto deploy artifact.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    fvpconf_path = (
        tmp_path
        / "yocto-deploy"
        / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    )
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["ros.ahci0.image_path"] = "missing-relative.img"
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: the local FVP package is generated.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: the bad reference fails instead of being preserved in a local fvpconf.
    assert result.returncode != 0
    output = output_of(result)
    assert "missing Yocto deploy source" in output
    assert "missing-relative.img" in output
    assert not (local_build / "deploy" / "apollo-fvp-local.fvpconf").exists()


def test_package_rejects_missing_absolute_image_path_without_preserving_it(
    tmp_path: Path,
) -> None:
    # Given: Apollo fvpconf contains a non-empty absolute image_path outside
    # YOCTO_DEPLOY_DIR that does not exist.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    bad_path = tmp_path / "outside-missing.img"
    fvpconf_path = (
        tmp_path
        / "yocto-deploy"
        / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    )
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["ros.ahci0.image_path"] = str(bad_path)
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: the local FVP package is generated.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: the bad reference fails instead of being preserved in a local fvpconf.
    assert result.returncode != 0
    output = output_of(result)
    assert "missing Yocto deploy source" in output
    assert str(bad_path) in output
    assert not (local_build / "deploy" / "apollo-fvp-local.fvpconf").exists()


def test_package_rejects_fvpconf_references_outside_yocto_deploy(
    tmp_path: Path,
) -> None:
    # Given: Yocto fvpconf points at an arbitrary host file outside deploy/images.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    outside_file = tmp_path / "host-secret.bin"
    write_file(outside_file, b"host secret\n")
    fvpconf_path = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["pcie_group_0.test_device.image_path"] = str(outside_file)
    fvpconf["data"].append(f"pcie_group_0.test_device.data={outside_file}@0x0")
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: local FVP packaging validates the referenced artifacts.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it fails instead of copying host files into the local deploy.
    assert result.returncode != 0
    output = output_of(result)
    assert "outside YOCTO_DEPLOY_DIR" in output
    assert not (local_build / "deploy" / "images" / outside_file.name).exists()
    assert not (
        local_build / "deploy" / "images" / "yocto-firmware" / outside_file.name
    ).exists()


def test_package_rejects_copied_artifact_symlink_destination(
    tmp_path: Path,
) -> None:
    # Given: a generic copied FVP image artifact would overwrite a symlink target.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    extra_image = yocto_deploy / "pcie-extra-disk.img"
    write_file(extra_image, b"extra disk\n")
    fvpconf_path = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["pcie_group_0.test_device.image_path"] = str(extra_image)
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")
    destination = local_build / "deploy" / "images" / "pcie-extra-disk.img"
    destination.parent.mkdir(parents=True, exist_ok=True)
    outside_target = tmp_path / "outside-destination"
    write_file(outside_target, b"outside original\n")
    destination.symlink_to(outside_target)

    # When: local FVP packaging reaches the generic copied artifact.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it refuses instead of following the destination symlink.
    assert result.returncode != 0
    output = output_of(result)
    assert "refusing to write" in output
    assert str(destination) in output
    assert destination.is_symlink()
    assert outside_target.read_bytes() == b"outside original\n"


def test_package_rejects_side_artifact_source_symlink_escape(
    tmp_path: Path,
) -> None:
    # Given: a Yocto side artifact copied outside fvpconf reference handling
    # resolves to a host file outside YOCTO_DEPLOY_DIR.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    escaped_capsule = tmp_path / "outside-host-secret.capsule"
    write_file(escaped_capsule, b"outside capsule secret\n")
    capsule = yocto_deploy / "efi-capsule-update-image.img.uefi.capsule"
    capsule.unlink()
    capsule.symlink_to(escaped_capsule)

    # When: local FVP packaging reaches the side artifact copy list.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it rejects the escaped source instead of copying host data.
    assert result.returncode != 0
    output = output_of(result)
    assert "outside YOCTO_DEPLOY_DIR" in output
    assert str(capsule) in output
    assert not (
        local_build / "deploy" / "images" / "efi-capsule-update-image.img.uefi.capsule"
    ).exists()


def test_package_rejects_images_parent_symlink_destination(
    tmp_path: Path,
) -> None:
    # Given: deploy/images is a symlink to a host directory outside LOCAL_BUILD_DIR.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    images_dir = local_build / "deploy" / "images"
    outside_images = tmp_path / "outside-images-target"
    images_dir.parent.mkdir(parents=True, exist_ok=True)
    outside_images.mkdir()
    images_dir.symlink_to(outside_images, target_is_directory=True)

    # When: local FVP packaging tries to copy Yocto images.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it refuses before writing through the symlinked parent directory.
    assert result.returncode != 0
    output = output_of(result)
    assert "refusing to write" in output
    assert str(images_dir) in output
    assert not (outside_images / "nexios-image-apollo-fvp.wic").exists()


def test_package_rejects_deploy_root_symlink_before_outside_mutation(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_DIR/deploy itself is a symlink to an outside tree.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    deploy_dir = local_build / "deploy"
    outside_deploy = tmp_path / "outside-deploy-target"
    deploy_dir.rename(outside_deploy)
    missing_flash = outside_deploy / "firmware" / "ap-flash-image.img"
    missing_flash.unlink()
    deploy_dir.symlink_to(outside_deploy, target_is_directory=True)
    before = tree_snapshot(outside_deploy)

    # When: package mode starts.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it refuses before cleanup, mkdir, or package writes mutate the target.
    assert result.returncode != 0
    assert tree_snapshot(outside_deploy) == before
    assert not missing_flash.exists()
    output = output_of(result)
    assert "deploy root" in output
    assert str(deploy_dir) in output


def test_package_rejects_firmware_dir_symlink_before_flash_artifact_creation(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_DIR/deploy/firmware points at a host directory.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    firmware_dir = local_build / "deploy" / "firmware"
    outside_firmware = tmp_path / "outside-firmware-target"
    firmware_dir.rename(outside_firmware)
    missing_flash = outside_firmware / "ap-flash-image.img"
    missing_flash.unlink()
    firmware_dir.symlink_to(outside_firmware, target_is_directory=True)
    before = tree_snapshot(outside_firmware)

    # When: package mode starts.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it refuses before package_flash_images creates artifacts outside.
    assert result.returncode != 0
    assert tree_snapshot(outside_firmware) == before
    assert not missing_flash.exists()
    output = output_of(result)
    assert "firmware" in output
    assert str(firmware_dir) in output


def test_linux_clean_rejects_deploy_root_symlink_without_deleting_outside_data(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_DIR/deploy points at a host directory with clean targets.
    local_build = tmp_path / "local-build"
    outside_deploy = tmp_path / "outside-deploy-target"
    boot_image = outside_deploy / "boot" / "Image"
    manifest = outside_deploy / "local-package-manifest.json"
    firmware_manifest = outside_deploy / "firmware" / ".apollo-flash-images.manifest"
    write_file(boot_image, b"outside Image\n")
    write_file(outside_deploy / "boot" / "apollo-fvp.dtb", b"outside dtb\n")
    write_file(manifest, "{}\n")
    write_file(firmware_manifest, "outside firmware manifest\n")
    local_build.mkdir()
    (local_build / "work").mkdir()
    (local_build / "deploy").symlink_to(outside_deploy, target_is_directory=True)

    # When: Linux clean is requested without package mode.
    result = run_local_build(
        "linux",
        "clean",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it fails before deploy-side rm -f follows the symlink.
    assert result.returncode != 0
    output = output_of(result)
    assert "deploy root" in output
    assert str(local_build / "deploy") in output
    assert boot_image.read_bytes() == b"outside Image\n"
    assert manifest.read_text(encoding="utf-8") == "{}\n"
    assert firmware_manifest.read_text(encoding="utf-8") == "outside firmware manifest\n"


def test_linux_clean_rejects_boot_dir_symlink_without_deleting_outside_image(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_DIR/deploy/boot points at a host directory.
    local_build = tmp_path / "local-build"
    outside_boot = tmp_path / "outside-boot-target"
    boot_image = outside_boot / "Image"
    write_file(boot_image, b"outside Image\n")
    local_build.mkdir()
    (local_build / "work").mkdir()
    (local_build / "deploy").mkdir()
    (local_build / "deploy" / "boot").symlink_to(
        outside_boot,
        target_is_directory=True,
    )

    # When: Linux clean is requested without package mode.
    result = run_local_build(
        "linux",
        "clean",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it fails before deploy-side rm -f follows BOOT_DIR.
    assert result.returncode != 0
    output = output_of(result)
    assert "boot" in output
    assert str(local_build / "deploy" / "boot") in output
    assert boot_image.read_bytes() == b"outside Image\n"


def test_boot_disk_clean_rejects_boot_disk_path_outside_boot_dir(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_BOOT_DISK points outside the generated boot directory.
    local_build = tmp_path / "local-build"
    outside_disk = tmp_path / "outside-disk.img"
    write_file(outside_disk, b"outside disk\n")
    (local_build / "work").mkdir(parents=True)
    (local_build / "deploy" / "boot").mkdir(parents=True)

    # When: boot-disk clean is requested.
    result = run_local_build(
        "boot-disk",
        "clean",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "LOCAL_BUILD_BOOT_DISK": str(outside_disk),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it rejects the override before deleting the outside file.
    assert result.returncode != 0
    output = output_of(result)
    assert "boot disk" in output
    assert str(outside_disk) in output
    assert outside_disk.read_bytes() == b"outside disk\n"


def test_boot_disk_clean_dry_run_rejects_boot_disk_path_outside_boot_dir(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_BOOT_DISK points outside the generated boot directory.
    local_build = tmp_path / "local-build"
    outside_disk = tmp_path / "outside-disk.img"

    # When: boot-disk clean dry-run is requested.
    result = run_local_build(
        "boot-disk",
        "clean",
        "--dry-run",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "LOCAL_BUILD_BOOT_DISK": str(outside_disk),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it rejects the unsafe override before rendering a misleading plan.
    assert result.returncode != 0
    output = output_of(result)
    assert "boot disk" in output
    assert str(outside_disk) in output


def test_linux_clean_rejects_work_symlink_without_deleting_outside_data(
    tmp_path: Path,
) -> None:
    # Given: LOCAL_BUILD_DIR/work is a symlink to a host directory outside the
    # local build root.
    local_build = tmp_path / "local-build"
    outside_work = tmp_path / "outside-work-target"
    sentinel = outside_work / "linux" / "keep.txt"
    write_file(sentinel, "outside component data\n")
    local_build.mkdir()
    (local_build / "work").symlink_to(outside_work, target_is_directory=True)

    # When: a component clean is requested.
    result = run_local_build(
        "linux",
        "clean",
        "--no-package",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it refuses before rm -rf can follow the work symlink.
    assert result.returncode != 0
    output = output_of(result)
    assert "work root" in output
    assert str(local_build / "work") in output
    assert sentinel.read_text(encoding="utf-8") == "outside component data\n"


def test_tfa_rejects_unsafe_platform_token_before_build(
    tmp_path: Path,
) -> None:
    # Given: TF_A_PLATFORM contains a parent traversal segment.
    local_build = tmp_path / "local-build"

    # When: local_build.sh resolves configuration.
    result = run_local_build(
        "tf-a",
        "build",
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "TF_A_PLATFORM": "../../outside",
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it fails before a TF-A clean/build path can be formed.
    assert result.returncode != 0
    output = output_of(result)
    assert "TF_A_PLATFORM must be a safe token" in output
    assert "../../outside" in output


def test_rejects_unsafe_machine_token_before_deriving_paths(
    tmp_path: Path,
) -> None:
    # Given: MACHINE contains a parent traversal segment.
    local_build = tmp_path / "local-build"

    # When: local_build.sh resolves configuration.
    result = run_local_build(
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "LOCAL_BUILD_DIR": str(local_build),
            "MACHINE": "../../escape",
            "TF_A_PLATFORM": "apollo_qvp",
            "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        },
    )

    # Then: it rejects the machine before deriving build/deploy paths.
    assert result.returncode != 0
    output = output_of(result)
    assert "MACHINE must be a safe token" in output
    assert "local-../../escape" not in output


def test_package_rejects_nested_parent_symlink_before_mkdir(
    tmp_path: Path,
) -> None:
    # Given: a nested copied-artifact parent would be created under a symlinked
    # deploy/images directory if mkdir ran before destination validation.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    images_dir = local_build / "deploy" / "images"
    outside_images = tmp_path / "outside-images-target"
    images_dir.parent.mkdir(parents=True, exist_ok=True)
    outside_images.mkdir()
    images_dir.symlink_to(outside_images, target_is_directory=True)

    # When: package mode reaches the nested yocto-firmware copy target.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it refuses before creating nested directories under the symlink target.
    assert result.returncode != 0
    output = output_of(result)
    assert "refusing to write" in output
    assert str(images_dir) in output
    assert not (outside_images / "yocto-firmware").exists()


def test_package_rejects_local_firmware_source_symlink_escape(
    tmp_path: Path,
) -> None:
    # Given: a local firmware overlay source resolves outside LOCAL_BUILD_DIR.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    outside_firmware = tmp_path / "outside-ap-flash-image.img"
    write_file(outside_firmware, b"outside firmware\n")
    local_firmware = local_build / "deploy" / "firmware" / "ap-flash-image.img"
    local_firmware.unlink()
    local_firmware.symlink_to(outside_firmware)

    # When: package mode records local firmware overlay provenance.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it rejects the escaped local source before manifest success.
    assert result.returncode != 0
    output = output_of(result)
    assert "local firmware overlay" in output
    assert "source is a symlink" in output
    assert str(local_firmware) in output
    assert not (local_build / "deploy" / "local-package-manifest.json").exists()


def test_package_rejects_stable_fvpconf_source_escape(tmp_path: Path) -> None:
    # Given: the stable Yocto fvpconf deploy name is a symlink outside deploy.
    yocto_deploy, _local_build, env = make_package_fixture(tmp_path)
    outside_fvpconf = tmp_path / "outside-fvpconf.json"
    source_text = (
        yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    ).read_text(encoding="utf-8")
    write_file(outside_fvpconf, source_text)
    stable_fvpconf = yocto_deploy / "nexios-image-apollo-fvp.fvpconf"
    stable_fvpconf.unlink()
    stable_fvpconf.symlink_to(outside_fvpconf)

    # When: local FVP packaging resolves the stable fvpconf.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it rejects the fvpconf source before trusting its contents.
    assert result.returncode != 0
    output = output_of(result)
    assert "outside YOCTO_DEPLOY_DIR" in output
    assert str(stable_fvpconf) in output


def test_package_rejects_timestamped_fvpconf_source_escape(tmp_path: Path) -> None:
    # Given: the timestamped Yocto fvpconf deploy name is a symlink outside deploy.
    yocto_deploy, _local_build, env = make_package_fixture(tmp_path)
    outside_fvpconf = tmp_path / "outside-fvpconf.json"
    timestamped_fvpconf = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    write_file(outside_fvpconf, timestamped_fvpconf.read_text(encoding="utf-8"))
    (yocto_deploy / "nexios-image-apollo-fvp.fvpconf").unlink()
    timestamped_fvpconf.unlink()
    timestamped_fvpconf.symlink_to(outside_fvpconf)

    # When: local FVP packaging falls back to the timestamped fvpconf.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it rejects the escaped timestamped fvpconf source.
    assert result.returncode != 0
    output = output_of(result)
    assert "outside YOCTO_DEPLOY_DIR" in output
    assert str(timestamped_fvpconf) in output


def test_package_rejects_final_symlink_destinations(tmp_path: Path) -> None:
    # Given: final local package destinations are symlinks inside deploy.
    for destination_name in (
        "apollo-fvp-local.fvpconf",
        "local-package-manifest.json",
    ):
        case_root = tmp_path / destination_name
        _yocto_deploy, local_build, env = make_package_fixture(case_root)
        destination = local_build / "deploy" / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(case_root / "outside-destination")

        # When: local FVP packaging tries to write final outputs.
        result = run_local_build(
            "--package",
            extra_env=with_fixture_flash_hook(
                env,
                case_root / "package-flash-hook.log",
            ),
        )

        # Then: it refuses instead of overwriting or following the symlink.
        assert result.returncode != 0
        output = output_of(result)
        assert "refusing to write" in output
        assert str(destination) in output
        assert destination.is_symlink()


def test_package_rejects_pending_symlink_destinations(tmp_path: Path) -> None:
    # Given: local Linux packaging makes the FVP package write pending outputs.
    for destination_name in (
        "apollo-fvp-local.fvpconf.tmp",
        "local-package-manifest.json.tmp",
    ):
        case_root = tmp_path / destination_name
        yocto_deploy, local_build, env = make_package_fixture(case_root)
        add_local_linux_fixture(local_build)
        add_uki_source_fixture(yocto_deploy)
        tools_dir, ukify_log, wic_log = add_stub_uki_tools(case_root)
        vars_path = case_root / "yocto-vars.json"
        write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))
        destination = local_build / "deploy" / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(case_root / "outside-destination")

        # When: local FVP packaging tries to prepare pending outputs.
        result = run_local_build(
            "--package",
            extra_env=with_fixture_flash_hook(
                local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
                case_root / "package-flash-hook.log",
            ),
        )

        # Then: it refuses instead of deleting, overwriting, or following the symlink.
        assert result.returncode != 0
        output = output_of(result)
        assert "refusing to write" in output
        assert str(destination) in output
        assert destination.is_symlink()


def test_package_rewrites_non_requirement_data_to_existing_local_copy(
    tmp_path: Path,
) -> None:
    # Given: Yocto fvpconf has a data entry that is not a local firmware overlay.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    diagnostic = yocto_deploy / "diagnostic-seed.bin"
    write_file(diagnostic, b"diagnostic\n")
    fvpconf_path = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["data"].append(f"diagnostic.loader={diagnostic}@0x4000")
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")

    # When: local FVP packaging rewrites data paths.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: every rewritten data path points at an artifact that exists locally.
    assert result.returncode == 0, output_of(result)
    local_fvpconf = local_build / "deploy" / "apollo-fvp-local.fvpconf"
    rewritten = json.loads(local_fvpconf.read_text(encoding="utf-8"))
    data_paths = []
    for entry in rewritten["data"]:
        parsed = entry.split("=", 1)[1].rsplit("@", 1)[0]
        data_paths.append(Path(parsed))
    assert data_paths
    for path in data_paths:
        assert path.is_file(), path
    assert (
        local_build / "deploy" / "images" / "yocto-firmware" / diagnostic.name
    ).read_bytes() == b"diagnostic\n"


def test_package_flash_hook_runs_before_composite_validation(tmp_path: Path) -> None:
    # Given: one local composite flash image is absent before package mode starts.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    hook_log = tmp_path / "package-flash-hook.log"
    (local_build / "deploy" / "firmware" / "ap-flash-image.img").unlink()

    # When: actual package mode runs with the fixture flash hook.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, hook_log),
    )

    # Then: the hook creates the composite before package validation reads it.
    assert result.returncode == 0, output_of(result)
    assert hook_log.read_text(encoding="utf-8").splitlines() == ["package_flash_images"]
    assert (local_build / "deploy" / "firmware" / "ap-flash-image.img").read_text(
        encoding="utf-8"
    ) == "fixture-package_flash_images:ap-flash-image.img\n"


def test_package_missing_yocto_fvpconf_or_wic_fails(tmp_path: Path) -> None:
    yocto_deploy, _local_build, env = make_package_fixture(tmp_path)
    hook_log = tmp_path / "missing-fvpconf-package-flash-hook.log"
    os.unlink(yocto_deploy / "nexios-image-apollo-fvp.fvpconf")
    os.unlink(yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf")

    result = run_local_build(
        "--package",
        extra_env=env
        | {
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE": "record-only",
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_LOG": str(hook_log),
        },
    )

    assert result.returncode != 0
    assert "Run ./yocto_build.sh first" in output_of(result)

    yocto_deploy, _local_build, env = make_package_fixture(tmp_path / "missing-wic")
    hook_log = tmp_path / "missing-wic-package-flash-hook.log"
    os.unlink(yocto_deploy / "nexios-image-apollo-fvp.wic")
    os.unlink(yocto_deploy / "nexios-image-apollo-fvp-20260102030405.wic")

    result = run_local_build(
        "--package",
        extra_env=env
        | {
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE": "record-only",
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_LOG": str(hook_log),
        },
    )

    assert result.returncode != 0
    assert "Run ./yocto_build.sh first" in output_of(result)


def test_package_missing_local_flash_dependency_fails(tmp_path: Path) -> None:
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    hook_log = tmp_path / "package-flash-hook.log"
    (local_build / "deploy" / "firmware" / "ap-flash-image.img").unlink()

    result = run_local_build(
        "--package",
        extra_env=env
        | {
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE": "record-only",
            "APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_LOG": str(hook_log),
        },
    )

    assert result.returncode != 0
    output = output_of(result)
    assert hook_log.read_text(encoding="utf-8").splitlines() == ["package_flash_images"]
    assert "Run ./local_build.sh --package" in output
    assert "ap-flash-image.img" in output


def test_package_local_linux_generates_slot_ukis_and_manifest(tmp_path: Path) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    local_deploy = local_build / "deploy"
    manifest = json.loads(
        (local_deploy / "local-package-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["linux_source"] == "local-uki"
    local_paths = [artifact["local_path"] for artifact in manifest["artifacts"]]
    assert local_paths.count(str(local_deploy / "images" / "auto-ad-nexios-a.efi")) == 1
    assert local_paths.count(str(local_deploy / "images" / "auto-ad-nexios-b.efi")) == 1
    ukify_lines = ukify_log.read_text(encoding="utf-8").splitlines()
    assert len(ukify_lines) == 2
    assert "--linux=" + str(local_deploy / "boot" / "Image") in ukify_lines[0]
    assert "--stub " + str(local_deploy / "images" / "linuxaa64.efi.stub") in ukify_lines[0]
    assert "--devicetree" in ukify_lines[0]
    assert "root=PARTLABEL=rootro_a" in ukify_lines[0]
    assert "root=PARTLABEL=rootro_b" in ukify_lines[1]
    assert "root=PARTLABEL=rootro_a" in (
        local_deploy / "images" / "auto-ad-nexios-a.efi"
    ).read_text(encoding="utf-8")
    assert "root=PARTLABEL=rootro_b" in (
        local_deploy / "images" / "auto-ad-nexios-b.efi"
    ).read_text(encoding="utf-8")
    wic_lines = wic_log.read_text(encoding="utf-8").splitlines()
    assert any("boot_a" in line or "@@1048576" in line for line in wic_lines)
    assert any("boot_b" in line or "@@135266304" in line for line in wic_lines)


def test_package_local_linux_uses_kernel_devicetree_basename(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build, dtb_name="custom-apollo.dtb")
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {"KERNEL_DEVICETREE": "arm/custom-apollo.dtb"},
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    local_deploy = local_build / "deploy"
    ukify_lines = ukify_log.read_text(encoding="utf-8").splitlines()
    assert "--devicetree " + str(
        local_deploy / "boot" / "custom-apollo.dtb"
    ) in ukify_lines[0]
    assert "--devicetree " + str(
        local_deploy / "boot" / "custom-apollo.dtb"
    ) in ukify_lines[1]


def test_package_local_linux_rejects_unsafe_uki_and_initrd_names(
    tmp_path: Path,
) -> None:
    # Given: BitBake-derived UKI/initrd names contain absolute, parent, or nested paths.
    unsafe_cases = (
        ("AUTO_AD_NEXIOS_UKI_A", str(tmp_path / "absolute.efi")),
        ("AUTO_AD_NEXIOS_UKI_A", "../escape.efi"),
        ("AUTO_AD_NEXIOS_UKI_A", "subdir/file.efi"),
        ("INITRD_ARCHIVE", "../escape.cpio.gz"),
    )

    for index, (variable, unsafe_name) in enumerate(unsafe_cases):
        case_root = tmp_path / f"unsafe-{index}"
        yocto_deploy, local_build, env = make_package_fixture(case_root)
        add_local_linux_fixture(local_build)
        add_uki_source_fixture(yocto_deploy)
        if variable == "INITRD_ARCHIVE":
            write_file(yocto_deploy.parent / "escape.cpio.gz", b"escape initrd\n")
        tools_dir, ukify_log, wic_log = add_stub_uki_tools(case_root)
        vars_path = case_root / "yocto-vars.json"
        variables = default_uki_variables(tools_dir / "ukify")
        variables[variable] = unsafe_name
        write_yocto_vars(vars_path, variables)

        # When: local Linux packaging parses the cached Yocto variables.
        result = run_local_build(
            "--package",
            extra_env=with_fixture_flash_hook(
                local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
                case_root / "package-flash-hook.log",
            ),
        )

        # Then: it rejects the name before writing outside deploy/images.
        assert result.returncode != 0, unsafe_name
        output = output_of(result)
        assert variable in output
        assert "unsafe file name" in output
        assert not (local_build / "deploy" / "escape.efi").exists()
        assert not (local_build / "deploy" / "escape.cpio.gz").exists()
        assert not (local_build / "deploy" / "images" / "subdir").exists()


def test_package_local_linux_prefers_local_initramfs_bootargs(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_local_initramfs_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))
    local_bootargs = (
        "console=ttyAMA0,115200 root=/dev/ram0 rw rdinit=/init "
        "cpuidle.governor=menu maxcpus=4 mem=4064M"
    )

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {
                "APOLLO_LOCAL_BUILD_UKI_INITRD": "local",
                "LOCAL_BUILD_BOOTARGS": local_bootargs,
            },
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    local_deploy = local_build / "deploy"
    ukify_lines = ukify_log.read_text(encoding="utf-8").splitlines()
    assert "--initrd=" + str(local_deploy / "boot" / "initramfs.cpio.gz") in ukify_lines[0]
    assert "--initrd=" + str(local_deploy / "boot" / "initramfs.cpio.gz") in ukify_lines[1]
    assert "root=PARTLABEL=rootro_a" not in ukify_lines[0]
    assert "root=PARTLABEL=rootro_b" not in ukify_lines[1]
    assert local_bootargs in (
        local_deploy / "images" / "auto-ad-nexios-a.efi"
    ).read_text(encoding="utf-8")
    assert local_bootargs in (
        local_deploy / "images" / "auto-ad-nexios-b.efi"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (local_deploy / "local-package-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["local_linux"]["initrd"] == str(
        local_deploy / "boot" / "initramfs.cpio.gz"
    )
    assert manifest["local_linux"]["initrd_provenance"] == "local-initramfs"
    assert manifest["local_linux"]["cmdline_a"] == local_bootargs
    assert manifest["local_linux"]["cmdline_b"] == local_bootargs


def test_package_local_linux_ignores_stale_yocto_vars_without_collecting(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    stale_variables = default_uki_variables(tools_dir / "ukify")
    del stale_variables["INITRD_ARCHIVE"]
    write_yocto_vars(vars_path, stale_variables)
    write_file(
        yocto_deploy / "nexios-initramfs-image-apollo-qvp.cpio.gz",
        b"reviewed config initrd\n",
    )
    collector_log = add_fake_collector_python(
        tools_dir,
        tmp_path,
        {"nexios-image": default_uki_variables(tools_dir / "ukify")},
    )

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    captured = json.loads(vars_path.read_text(encoding="utf-8"))
    assert "INITRD_ARCHIVE" not in captured["recipes"]["nexios-image"]["variables"]
    assert not collector_log.exists()
    assert len(ukify_log.read_text(encoding="utf-8").splitlines()) == 2


def test_package_local_linux_uses_native_ukify_from_local_config(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    native_ukify = (
        tmp_path
        / "yocto-tmp"
        / "work"
        / "apollo_fvp-poky-linux"
        / "nexios-image"
        / "1.0"
        / "recipe-sysroot-native"
        / "usr"
        / "bin"
        / "ukify"
    )
    native_site = (
        native_ukify.parents[2]
        / "usr"
        / "lib"
        / "python3.13"
        / "site-packages"
    )
    write_file(native_site / "fake_yocto_native_dependency.py", "VALUE = 'native'\n")
    write_file(
        native_ukify,
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import os\n"
        "import sys\n"
        "import fake_yocto_native_dependency\n"
        "log = Path(os.environ['UKIFY_LOG'])\n"
        "log.parent.mkdir(parents=True, exist_ok=True)\n"
        "with log.open('a', encoding='utf-8') as stream:\n"
        "    stream.write('ukify ' + sys.argv[0])\n"
        "    for arg in sys.argv[1:]:\n"
        "        stream.write(' ' + arg)\n"
        "    stream.write(' dep=' + fake_yocto_native_dependency.VALUE + '\\n')\n"
        "output = ''\n"
        "cmdline = ''\n"
        "for arg in sys.argv[1:]:\n"
        "    if arg.startswith('--output='):\n"
        "        output = arg.removeprefix('--output=')\n"
        "    if arg.startswith('--cmdline='):\n"
        "        cmdline = arg.removeprefix('--cmdline=')\n"
        "Path(output).parent.mkdir(parents=True, exist_ok=True)\n"
        "Path(output).write_text('stub-uki\\ncmdline=' + cmdline + '\\n', encoding='utf-8')\n",
    )
    native_ukify.chmod(0o755)
    (tools_dir / "ukify").unlink()
    vars_path = tmp_path / "yocto-vars.json"
    variables = default_uki_variables(Path("ukify"))
    variables["UKIFY_CMD"] = "ukify build"
    write_yocto_vars(vars_path, variables)
    collector_log = add_fake_collector_python(
        tools_dir,
        tmp_path,
        {"nexios-image": variables},
    )

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {"YOCTO_TMP": str(tmp_path / "yocto-tmp")},
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    assert not collector_log.exists()
    ukify_lines = ukify_log.read_text(encoding="utf-8").splitlines()
    assert len(ukify_lines) == 2
    assert str(native_ukify) in ukify_lines[0]


def test_package_local_linux_prefers_native_ukify_when_host_ukify_lacks_pefile(
    tmp_path: Path,
) -> None:
    # Given: host PATH has a broken ukify, while Yocto native ukify has pefile.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    native_ukify = (
        tmp_path
        / "yocto-tmp"
        / "work"
        / "apollo_fvp-poky-linux"
        / "nexios-image"
        / "1.0"
        / "recipe-sysroot-native"
        / "usr"
        / "bin"
        / "ukify"
    )
    native_site = (
        native_ukify.parents[2]
        / "usr"
        / "lib"
        / "python3.13"
        / "site-packages"
    )
    write_file(native_site / "pefile.py", "VALUE = 'native-pefile'\n")
    write_file(
        native_ukify,
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import os\n"
        "import sys\n"
        "import pefile\n"
        "log = Path(os.environ['UKIFY_LOG'])\n"
        "log.parent.mkdir(parents=True, exist_ok=True)\n"
        "output = ''\n"
        "cmdline = ''\n"
        "for arg in sys.argv[1:]:\n"
        "    if arg.startswith('--output='):\n"
        "        output = arg.removeprefix('--output=')\n"
        "    if arg.startswith('--cmdline='):\n"
        "        cmdline = arg.removeprefix('--cmdline=')\n"
        "with log.open('a', encoding='utf-8') as stream:\n"
        "    stream.write('ukify ' + sys.argv[0] + ' dep=' + pefile.VALUE + '\\n')\n"
        "Path(output).parent.mkdir(parents=True, exist_ok=True)\n"
        "Path(output).write_text('stub-uki\\ncmdline=' + cmdline + '\\n', encoding='utf-8')\n",
    )
    native_ukify.chmod(0o755)
    write_file(
        tools_dir / "ukify",
        "#!/usr/bin/env python3\n"
        "raise ModuleNotFoundError(\"No module named 'pefile'\")\n",
    )
    (tools_dir / "ukify").chmod(0o755)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(Path("ukify")))

    # When: local Linux packaging resolves UKIFY_CMD.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {"YOCTO_TMP": str(tmp_path / "yocto-tmp")},
            tmp_path / "package-flash-hook.log",
        ),
    )

    # Then: native ukify is used, so host pefile packaging does not matter.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "No module named 'pefile'" not in output
    ukify_lines = ukify_log.read_text(encoding="utf-8").splitlines()
    assert len(ukify_lines) == 2
    assert str(native_ukify) in ukify_lines[0]
    assert "dep=native-pefile" in ukify_lines[0]


def test_package_local_linux_rejects_empty_initrd_in_local_config(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    stale_variables = default_uki_variables(tools_dir / "ukify")
    del stale_variables["INITRD_ARCHIVE"]
    write_yocto_vars(vars_path, stale_variables)
    collector_log = add_fake_collector_python(
        tools_dir,
        tmp_path,
        {"nexios-image": stale_variables},
    )

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {"INITRD_ARCHIVE": ""},
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode != 0
    output = output_of(result)
    assert "INITRD_ARCHIVE" in output
    assert "local_build.conf" in output
    assert not collector_log.exists()
    assert not ukify_log.exists()
    assert not wic_log.exists()


def test_package_local_linux_patches_only_local_wic_copy(tmp_path: Path) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))
    source_wic = yocto_deploy / "nexios-image-apollo-fvp.wic"
    source_wic_before = source_wic.read_bytes()

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    local_wic = local_build / "deploy" / "images" / "nexios-image-apollo-fvp.wic"
    assert source_wic.read_bytes() == source_wic_before
    assert local_wic.read_bytes() != source_wic_before
    assert str(yocto_deploy) not in wic_log.read_text(encoding="utf-8")
    manifest = json.loads(
        (local_build / "deploy" / "local-package-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    wic_entry = next(
        entry for entry in manifest["artifacts"] if entry["local_path"] == str(local_wic)
    )
    assert wic_entry["source_path"] == str(source_wic)
    assert wic_entry["source_sha256_before"] == wic_entry["source_sha256_after"]
    assert wic_entry["source_preserved"] is True


def test_package_local_linux_reuses_current_wic_patch_stamp(
    tmp_path: Path,
) -> None:
    # Given: local Linux packaging already patched the WIC with current UKIs.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))
    package_env = with_fixture_flash_hook(
        local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
        tmp_path / "package-flash-hook.log",
    )
    first = run_local_build("--package", extra_env=package_env)
    assert first.returncode == 0, output_of(first)
    local_wic = local_build / "deploy" / "images" / "nexios-image-apollo-fvp.wic"
    first_wic = local_wic.read_bytes()
    assert "mcopy" in wic_log.read_text(encoding="utf-8")
    wic_log.unlink()

    # When: packaging runs again with the same WIC and UKI inputs.
    second = run_local_build("--package", extra_env=package_env)

    # Then: it preserves the patched WIC and skips WIC mutation tools.
    assert second.returncode == 0, output_of(second)
    assert local_wic.read_bytes() == first_wic
    assert not wic_log.exists()


def test_package_rejects_wic_side_artifact_source_symlink_escape(
    tmp_path: Path,
) -> None:
    # Given: the copied Yocto WIC side artifact resolves through a symlink to a
    # host file outside YOCTO_DEPLOY_DIR, while fvpconf leaves the image defaulted.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    outside_wic = tmp_path / "outside-host-secret.wic"
    write_file(outside_wic, b"outside wic secret\n")
    source_wic = yocto_deploy / "nexios-image-apollo-fvp.wic"
    fvpconf_path = yocto_deploy / "nexios-image-apollo-fvp-20260102030405.fvpconf"
    fvpconf = json.loads(fvpconf_path.read_text(encoding="utf-8"))
    fvpconf["parameters"]["ros.virtio_block0.image_path"] = "<default>"
    write_file(fvpconf_path, json.dumps(fvpconf, indent=2) + "\n")
    source_wic.unlink()
    source_wic.symlink_to(outside_wic)

    # When: package mode reaches the Yocto WIC side artifact copy.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: it rejects the escaped Yocto WIC source instead of copying host data.
    assert result.returncode != 0
    output = output_of(result)
    assert "outside YOCTO_DEPLOY_DIR" in output
    assert str(source_wic) in output
    assert not (
        local_build / "deploy" / "images" / "nexios-image-apollo-fvp.wic"
    ).exists()


def test_package_local_linux_wic_apply_failure_leaves_no_broken_fvpconf(
    tmp_path: Path,
) -> None:
    # Given: local Linux inputs force local WIC patching and the WIC tool fails.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    # When: package mode reaches the local WIC apply step.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log)
            | {"APOLLO_STUB_MCOPY_FAIL": "1"},
            tmp_path / "package-flash-hook.log",
        ),
    )

    # Then: no final fvpconf is left pointing at the missing local WIC.
    assert result.returncode != 0
    output = output_of(result)
    assert "stub mcopy failure" in output
    local_deploy = local_build / "deploy"
    assert not (local_deploy / "images" / "nexios-image-apollo-fvp.wic").exists()
    assert not (local_deploy / "apollo-fvp-local.fvpconf").exists()


def test_package_local_linux_preserves_dm_verity_artifacts(tmp_path: Path) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))
    verity_sources = [
        yocto_deploy / "nexios-image-apollo-fvp.ext4.verity",
        yocto_deploy / "nexios-image-apollo-fvp.ext4.verity.env",
    ]
    source_bytes = {path: path.read_bytes() for path in verity_sources}

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    for source, content in source_bytes.items():
        local_path = local_build / "deploy" / "images" / source.name
        assert source.read_bytes() == content
        assert local_path.read_bytes() == content
    assert "rootro_a" not in wic_log.read_text(encoding="utf-8")
    assert "rootro_b" not in wic_log.read_text(encoding="utf-8")


def test_package_exports_inspector_required_uboot_artifacts(tmp_path: Path) -> None:
    # Given: local U-Boot was built and Yocto deploy has the initial environment.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    write_file(local_build / "deploy" / "u-boot" / "u-boot.bin", b"local-u-boot\n")
    write_file(
        yocto_deploy / "u-boot-initial-env-apollo-fvp-2026.01+git-r0",
        b"yocto-u-boot-env\n",
    )

    # When: local FVP deploy packaging runs.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "package-flash-hook.log"),
    )

    # Then: the copied deploy images satisfy the WIC inspector's U-Boot patterns.
    assert result.returncode == 0, output_of(result)
    images_dir = local_build / "deploy" / "images"
    assert (
        images_dir / "u-boot-apollo-fvp-local.bin"
    ).read_bytes() == b"local-u-boot\n"
    assert (
        images_dir / "u-boot-initial-env-apollo-fvp-2026.01+git-r0"
    ).read_bytes() == b"yocto-u-boot-env\n"
    manifest = json.loads(
        (local_build / "deploy" / "local-package-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    artifact_paths = {
        Path(entry["local_path"]).name: entry["component_provenance"]
        for entry in manifest["artifacts"]
    }
    assert artifact_paths["u-boot-apollo-fvp-local.bin"] == "local-u-boot-overlay"
    assert (
        artifact_paths["u-boot-initial-env-apollo-fvp-2026.01+git-r0"]
        == "yocto-copied"
    )


def test_linux_build_config_policy_does_not_force_dm_verity_by_default() -> None:
    # Given: local Linux boots from the Buildroot initramfs path by default.
    script = (ROOT / "scripts/build/modules/build_linux.sh").read_text(
        encoding="utf-8"
    )

    # When: the local kernel config is generated.
    # Then: dm-verity is not unconditionally forced built-in.
    assert "LOCAL_LINUX_DM_VERITY=y" not in script
    assert 'LOCAL_LINUX_DM_VERITY:-0}" == "1"' in script
    assert 'LOCAL_LINUX_DM_VERITY:-0}" != "0"' in script
    assert "LOCALVERSION=" in script


def test_package_local_linux_missing_ukify_or_keys_preserves_previous_wic(
    tmp_path: Path,
) -> None:
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    first = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(env, tmp_path / "first-package-flash.log"),
    )
    assert first.returncode == 0, output_of(first)
    local_wic = local_build / "deploy" / "images" / "nexios-image-apollo-fvp.wic"
    previous_wic = local_wic.read_bytes()

    yocto_deploy = tmp_path / "yocto-deploy"
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    variables = default_uki_variables(tmp_path / "missing-ukify")
    variables["UEFI_SECURE_BOOT"] = "1"
    variables["UKI_SB_KEY"] = str(tmp_path / "missing-db.key")
    variables["UKI_SB_CERT"] = str(tmp_path / "missing-db.crt")
    write_yocto_vars(vars_path, variables)

    failed = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "failed-package-flash.log",
        ),
    )

    assert failed.returncode != 0
    output = output_of(failed)
    assert "UKIFY_CMD" in output or "UKI_SB_KEY" in output or "UKI_SB_CERT" in output
    assert local_wic.read_bytes() == previous_wic
    assert not wic_log.exists() or wic_log.read_text(encoding="utf-8") == ""


def test_package_local_linux_stages_modules_without_rootfs_injection(
    tmp_path: Path,
) -> None:
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build)
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode == 0, output_of(result)
    modules_dir = local_build / "deploy" / "modules" / "6.6.1-local"
    assert (modules_dir / "drivers" / "net" / "pfdi_misc.ko").read_bytes() == b"module-ko\n"
    manifest = json.loads(
        (local_build / "deploy" / "local-package-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["local_linux_modules"]["kernel_release"] == "6.6.1-local"
    assert manifest["local_linux_modules"]["staged_dir"] == str(modules_dir)
    assert manifest["local_linux_modules"]["injected_into_rootfs"] is False
    assert "not injected into rootfs" in manifest["local_linux_modules"]["limitation"]


def test_package_local_linux_rejects_modules_order_path_escape(
    tmp_path: Path,
) -> None:
    # Given: modules.order contains a parent-directory module path.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build, modules=False)
    linux_build = local_build / "work" / "linux"
    write_file(linux_build / "include" / "config" / "kernel.release", "6.6.1-local\n")
    write_file(linux_build / ".." / "escape.ko", b"escaped module\n")
    write_file(linux_build / "modules.order", "../escape.ko\n")
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    # When: local Linux packaging stages modules.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    # Then: it rejects the unsafe entry before writing outside the release dir.
    assert result.returncode != 0
    output = output_of(result)
    assert "unsafe modules.order entry" in output
    assert "../escape.ko" in output
    assert not (local_build / "deploy" / "modules" / "escape.ko").exists()


def test_package_local_linux_rejects_kernel_release_path_escape(
    tmp_path: Path,
) -> None:
    # Given: kernel.release contains a traversal string that would place staged
    # modules outside LOCAL_BUILD_DIR/deploy/modules if used directly.
    yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build, modules=False)
    linux_build = local_build / "work" / "linux"
    write_file(
        linux_build / "include" / "config" / "kernel.release",
        "../../../outside-release\n",
    )
    write_file(linux_build / "drivers" / "net" / "pfdi_misc.ko", b"module-ko\n")
    write_file(linux_build / "modules.order", "drivers/net/pfdi_misc.ko\n")
    add_uki_source_fixture(yocto_deploy)
    tools_dir, ukify_log, wic_log = add_stub_uki_tools(tmp_path)
    vars_path = tmp_path / "yocto-vars.json"
    write_yocto_vars(vars_path, default_uki_variables(tools_dir / "ukify"))

    # When: local Linux packaging stages modules.
    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    # Then: it rejects the release before writing outside deploy/modules.
    assert result.returncode != 0
    output = output_of(result)
    assert "unsafe kernel.release" in output
    assert "../../../outside-release" in output
    assert not (local_build / "outside-release").exists()

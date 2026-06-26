from __future__ import annotations

import hashlib
from pathlib import Path
import json
import os
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
COMPONENTS: Final[tuple[str, ...]] = (
    "tf-m",
    "scp-firmware",
    "zephyr",
    "optee",
    "u-boot",
    "tf-a",
    "linux",
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

    # Then: help exposes the FVP-only local build contract.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "Usage: ./local_build.sh" in output
    assert "--dry-run" in output
    assert "--package" in output
    assert "--no-package" in output
    for component in COMPONENTS:
        assert component in output
    for action in ("build", "clean", "clean-build", *KCONFIG_ACTIONS):
        assert action in output
    assert "qbox" not in output.lower()
    assert "buildroot" not in output.lower()


def test_help_includes_operational_examples_with_existing_script_paths() -> None:
    # Given: the new underscore local build entrypoint.
    # When: the user asks for CLI help.
    result = run_local_build("--help")

    # Then: help shows the requested local FVP workflow examples.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    for example in (
        "./local_build.sh",
        "./local_build.sh linux clean-build --no-package",
        "./local_build.sh linux menuconfig --no-package",
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

    # Then: the default plan builds every supported component and packages FVP.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert component_step_lines(output) == [
        f"{component}: build" for component in COMPONENTS
    ]
    assert "package" in output
    assert "qbox" not in output.lower()
    assert "buildroot" not in output.lower()


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
    for component in ("tf-m", "scp-firmware", "zephyr", "optee", "tf-a"):
        assert component not in output


def test_package_flag_is_package_only_when_no_components_are_selected() -> None:
    # Given: the package flag without component selection.
    # When: dry-run resolves the command.
    result = run_local_build("--package", "--dry-run")

    # Then: only the local FVP package step is planned.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "package" in output
    for component in COMPONENTS:
        assert component not in output
    assert "qbox" not in output.lower()
    assert "buildroot" not in output.lower()


def test_package_local_linux_preflights_missing_mtools(tmp_path: Path) -> None:
    # Given: local Linux outputs require WIC ESP patching, but mtools are absent.
    _yocto_deploy, local_build, env = make_package_fixture(tmp_path)
    add_local_linux_fixture(local_build, modules=False)
    tools_dir = tmp_path / "host-tools"
    tools_dir.mkdir(parents=True)
    for command in ("bash", "dirname", "python3", "realpath"):
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
    assert "package" not in output.lower()


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


def test_unknown_component_fails_with_actionable_error() -> None:
    # Given: a component owned by the old dashed workflow, not this entrypoint.
    # When: the component is requested.
    result = run_local_build("qbox", "--dry-run")

    # Then: the command rejects it instead of silently building QBox.
    assert result.returncode != 0
    output = output_of(result).lower()
    assert "unknown component" in output or "unsupported component" in output
    assert "qbox" in output


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
    assert "O=build/local-apollo-fvp/work/u-boot" in output
    assert "ARCH=arm" in output
    assert "CROSS_COMPILE=aarch64-poky-linux-" in output
    assert "RD_ASPEN_VARIANT=cfg2" in output
    assert "apollo_fvp_defconfig" in output


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
    assert "O=build/local-apollo-fvp/work/linux" in output
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
    assert "build/local-apollo-fvp/work/zephyr-demos-cl1" in output
    assert "cmake --build" in output
    assert "--target savedefconfig" in output
    assert "generated defconfig: build/local-apollo-fvp/work/zephyr-demos-cl1/zephyr/defconfig" in output


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


def test_missing_sdk_fails_with_recovery_text_not_unresolved_build_sdk(
    tmp_path: Path,
) -> None:
    # Given: the new entrypoint is run without a populated Yocto SDK.
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "SDK_DIR": str(tmp_path / "missing-sdk"),
        "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
    }

    # When: a real component build reaches SDK setup.
    result = run_local_build("linux", "--no-package", extra_env=env)

    # Then: it fails with SDK recovery text, not an unresolved shell function.
    assert result.returncode != 0
    output = output_of(result)
    assert "build_sdk: command not found" not in output
    assert "Yocto SDK" in output
    assert "./local-build.sh sdk" in output or "populate_sdk" in output


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
    assert "deploy/boot/apollo-fvp.dtb" in output
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
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "YOCTO_DEPLOY_DIR": str(yocto_deploy),
        "LOCAL_BUILD_DIR": str(local_build),
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


def test_tfm_build_dry_run_resolves_platform_from_yocto_vars(tmp_path: Path) -> None:
    # Given: Yocto collected the Apollo TF-M platform from trusted-firmware-m.
    vars_path = tmp_path / "yocto-local-build-vars.json"
    write_yocto_recipe_vars(
        vars_path,
        {
            "nexios-image": {"MACHINE": "apollo-fvp"},
            "trusted-firmware-m": {
                "MACHINE": "apollo-fvp",
                "TFM_PLATFORM": "arm/rse/automotive_rd/apollo-fvp",
            },
        },
    )

    # When: the local TF-M build plan is resolved from the Yocto cache.
    result = run_local_build(
        "tf-m",
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "1",
            "APOLLO_LOCAL_BUILD_YOCTO_VARS": str(vars_path),
        },
    )

    # Then: the configure metadata carries a non-empty Apollo platform.
    assert result.returncode == 0, output_of(result)
    output = output_of(result)
    assert "tf-m: build" in output
    assert "-DTFM_PLATFORM=arm/rse/automotive_rd/apollo-fvp" in output
    assert "-DCROSS_COMPILE=arm-none-eabi" in output


def test_stale_yocto_vars_cache_rejected_before_default_loading(
    tmp_path: Path,
) -> None:
    # Given: the cache claims a hash for live config that no longer matches.
    live_config = tmp_path / "build/conf/local.conf"
    write_file(live_config, 'MACHINE = "apollo-fvp"\n')
    vars_path = tmp_path / "yocto-local-build-vars.json"
    write_file(
        vars_path,
        json.dumps(
            {
                "schema_version": 1,
                "config_paths": {
                    "local_conf": {
                        "path": str(live_config),
                        "sha256": hashlib.sha256(b"old config\n").hexdigest(),
                    },
                },
                "recipes": {
                    "nexios-image": {
                        "command": "fixture bitbake -e nexios-image",
                        "variables": {
                            "MACHINE": "stale-machine",
                            "RD_ASPEN_VARIANT": "stale-cfg",
                            "PC_CPUS_COUNT_DEFAULT": "99",
                        },
                    },
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    # When: dry-run would otherwise apply build/Kconfig defaults from cache.
    result = run_local_build(
        "u-boot",
        "defconfig",
        "--dry-run",
        extra_env={
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "1",
            "APOLLO_LOCAL_BUILD_YOCTO_VARS": str(vars_path),
        },
    )

    # Then: stale values are rejected before they affect the resolved plan.
    assert result.returncode != 0
    output = output_of(result)
    assert "stale config hash" in output
    assert "stale-machine" not in output
    assert "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS=0" in output


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
    assert "trusted-firmware-m" in output


def add_local_linux_fixture(local_build: Path, *, modules: bool = True) -> None:
    write_file(local_build / "deploy" / "boot" / "Image", b"local-linux-image\n")
    write_file(local_build / "deploy" / "boot" / "apollo-fvp.dtb", b"local-dtb\n")
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
    return base_env | {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "1",
        "APOLLO_LOCAL_BUILD_YOCTO_VARS": str(vars_path),
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


def test_package_local_linux_refreshes_stale_yocto_vars_missing_initrd(
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
    refreshed = json.loads(vars_path.read_text(encoding="utf-8"))
    assert refreshed["recipes"]["nexios-image"]["variables"]["INITRD_ARCHIVE"] == (
        "nexios-initramfs-image-apollo-fvp.cpio.gz"
    )
    assert "collect_yocto_local_build_vars.py" in collector_log.read_text(
        encoding="utf-8"
    )
    assert len(ukify_log.read_text(encoding="utf-8").splitlines()) == 2


def test_package_local_linux_refreshes_component_cache_and_uses_native_ukify(
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
    write_yocto_recipe_vars(
        vars_path,
        {
            "nexios-image": {
                "MACHINE": "apollo-fvp",
                "BOOTLOADER_LINUX_APPEND": "cpuidle.governor=menu",
            },
            "linux-yocto-rt": {
                "MACHINE": "apollo-fvp",
                "KBUILD_DEFCONFIG": "apollo_fvp_defconfig",
                "KERNEL_DEVICETREE": "arm/apollo-fvp.dtb",
            },
        },
    )
    refreshed_variables = default_uki_variables(Path("ukify"))
    refreshed_variables["UKIFY_CMD"] = "ukify build"
    collector_log = add_fake_collector_python(
        tools_dir,
        tmp_path,
        {"nexios-image": refreshed_variables},
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
    refreshed = json.loads(vars_path.read_text(encoding="utf-8"))
    variables = refreshed["recipes"]["nexios-image"]["variables"]
    for name in (
        "INITRD_ARCHIVE",
        "UKIFY_CMD",
        "EFI_ARCH",
        "AUTO_AD_NEXIOS_UKI_A",
        "AUTO_AD_NEXIOS_UKI_B",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_A",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_B",
        "UEFI_SECURE_BOOT",
    ):
        assert variables[name]
    assert "collect_yocto_local_build_vars.py" in collector_log.read_text(
        encoding="utf-8"
    )
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


def test_package_local_linux_rejects_refreshed_vars_still_missing_initrd(
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
    add_fake_collector_python(tools_dir, tmp_path, {"nexios-image": stale_variables})

    result = run_local_build(
        "--package",
        extra_env=with_fixture_flash_hook(
            local_uki_env(env, vars_path, tools_dir, ukify_log, wic_log),
            tmp_path / "package-flash-hook.log",
        ),
    )

    assert result.returncode != 0
    output = output_of(result)
    assert "INITRD_ARCHIVE" in output
    assert "refresh" in output
    assert "missing captured Yocto variable" not in output
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


def test_linux_build_config_policy_requires_builtin_dm_verity() -> None:
    # Given: local Linux boots a Yocto dm-verity rootfs from the initramfs.
    script = (ROOT / "scripts/build/modules/build_linux.sh").read_text(
        encoding="utf-8"
    )

    # When: the local kernel config is generated.
    # Then: dm-verity is forced built-in and tracked in the config marker.
    assert "LOCAL_LINUX_DM_VERITY=y" in script
    assert "--enable BLK_DEV_DM" in script
    assert "--enable DM_BUFIO" in script
    assert "--enable DM_VERITY" in script
    assert "--enable CRYPTO_SHA256" in script
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

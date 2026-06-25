from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build/collect_yocto_local_build_vars.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "collect_yocto_local_build_vars",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_bitbake_env_keeps_allowlisted_values_when_extra_lines_present() -> None:
    module = load_module()
    raw = (
        'BB_VERSION="2.12.0"\n'
        'MACHINE="apollo-fvp"\n'
        'BOOTLOADER_LINUX_APPEND="cpuidle.governor=menu maxcpus=4 mem=4064M"\n'
        'UBOOT_MACHINE="apollo_fvp_defconfig"\n'
        'SECRET_TOKEN="do-not-capture"\n'
        'KBUILD_DEFCONFIG="apollo_fvp_defconfig"\n'
        'KERNEL_DEVICETREE="arm/apollo-fvp.dtb"\n'
        'PLATFORM="automotive_rd-rdaspen"\n'
        'TFA_PLATFORM="apollo_fvp"\n'
    )

    variables = module.parse_bitbake_env(raw)

    assert variables == {
        "BB_VERSION": "2.12.0",
        "BOOTLOADER_LINUX_APPEND": "cpuidle.governor=menu maxcpus=4 mem=4064M",
        "KBUILD_DEFCONFIG": "apollo_fvp_defconfig",
        "KERNEL_DEVICETREE": "arm/apollo-fvp.dtb",
        "MACHINE": "apollo-fvp",
        "PLATFORM": "automotive_rd-rdaspen",
        "TF_A_PLATFORM": "apollo_fvp",
        "UBOOT_MACHINE": "apollo_fvp_defconfig",
    }


def test_parse_bitbake_env_rejects_unterminated_assignment() -> None:
    module = load_module()

    with pytest.raises(module.BitBakeEnvParseError, match="MACHINE"):
        module.parse_bitbake_env('MACHINE="apollo-fvp\n')


def test_parse_bitbake_env_derives_platform_from_extra_oemake() -> None:
    module = load_module()
    raw = (
        'MACHINE="apollo-fvp"\n'
        'EXTRA_OEMAKE="COMPILER=gcc PLATFORM=automotive_rd-rdaspen CFG_ARM64_core=y"\n'
    )

    variables = module.parse_bitbake_env(raw)

    assert variables == {
        "MACHINE": "apollo-fvp",
        "PLATFORM": "automotive_rd-rdaspen",
    }


def test_required_recipe_variables_are_reported_when_missing() -> None:
    module = load_module()

    with pytest.raises(module.MissingVariablesError, match="UBOOT_MACHINE"):
        module.require_recipe_variables("u-boot", {"MACHINE": "apollo-fvp"})


def test_parse_args_uses_default_output_when_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    monkeypatch.setattr("sys.argv", [str(SCRIPT)])

    args = module.parse_args()

    assert args.output == Path("build/local-apollo-fvp/yocto-local-build-vars.json")
    assert args.build_dir == Path("build")
    assert args.timeout == 600


def test_default_recipes_match_apollo_parity_scope() -> None:
    module = load_module()

    assert module.DEFAULT_RECIPES == (
        "nexios-image",
        "u-boot",
        "linux-yocto-rt",
        "firmware-apollo-fvp",
        "trusted-firmware-m",
        "scp-firmware",
        "trusted-firmware-a",
        "optee-os",
        "zephyr-demos-cl1",
    )


def test_allowlisted_variables_match_contract() -> None:
    module = load_module()

    assert module.ALLOWLISTED_VARIABLES == {
        "MACHINE",
        "DISTRO",
        "BB_VERSION",
        "TEMPLATECONF",
        "RD_ASPEN_VARIANT",
        "PC_CPUS_COUNT_DEFAULT",
        "IMAGE_FSTYPES",
        "IMAGE_ROOTFS_SIZE",
        "IMAGE_INSTALL",
        "BOOTLOADER_LINUX_APPEND",
        "UBOOT_MACHINE",
        "UBOOT_CONFIG",
        "KBUILD_DEFCONFIG",
        "KERNEL_DEVICETREE",
        "KERNEL_FEATURES",
        "KERNEL_DEBUG_INFO",
        "OPTEEMACHINE",
        "PLATFORM",
        "TF_A_PLATFORM",
        "TFM_PLATFORM",
        "SCP_PLATFORM",
        "ZEPHYR_BOARD",
        "ZEPHYR_APPLICATION",
    }


def test_parse_recipe_list_rejects_malformed_recipe_name() -> None:
    module = load_module()

    with pytest.raises(argparse.ArgumentTypeError, match="bad recipe"):
        module.parse_recipe_list("nexios-image,bad recipe")

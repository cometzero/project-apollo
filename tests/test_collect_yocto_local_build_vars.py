from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build/collect_yocto_local_build_vars.py"
REQUIRED_UKI_VARIABLES = {
    "KERNEL_CONSOLE",
    "INITRD_ARCHIVE",
    "EFI_ARCH",
    "AUTO_AD_NEXIOS_UKI_A",
    "AUTO_AD_NEXIOS_UKI_B",
    "AUTO_AD_NEXIOS_SLOT_DIR_A",
    "AUTO_AD_NEXIOS_SLOT_DIR_B",
    "AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME",
    "AUTO_AD_NEXIOS_UKI_CMDLINE_A",
    "AUTO_AD_NEXIOS_UKI_CMDLINE_B",
    "UKIFY_CMD",
    "UEFI_SECURE_BOOT",
    "UKI_SB_KEY",
    "UKI_SB_CERT",
}
REQUIRED_QBOX_VARIABLES = {
    "QBOX_APOLLO_BUILD_TARGET",
    "HSOC_APOLLO_QBOX_SRC",
    "HSOC_APOLLO_QBOX_PLATFORM_SRC",
    "HSOC_APOLLO_QEMU_SRC",
    "EXTERNALSRC",
    "EXTERNALSRC_BUILD",
}


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


def test_parse_bitbake_env_keeps_auto_ad_nexios_uki_package_values() -> None:
    module = load_module()
    raw = (
        'MACHINE="apollo-fvp"\n'
        'KERNEL_CONSOLE="ttyAMA0"\n'
        'INITRD_ARCHIVE="nexios-image-apollo-fvp.rootfs.cpio.gz"\n'
        'EFI_ARCH="aa64"\n'
        'AUTO_AD_NEXIOS_UKI_A="auto-ad-nexios-a.efi"\n'
        'AUTO_AD_NEXIOS_UKI_B="auto-ad-nexios-b.efi"\n'
        'AUTO_AD_NEXIOS_SLOT_DIR_A="EFI/Linux/a-slot"\n'
        'AUTO_AD_NEXIOS_SLOT_DIR_B="EFI/Linux/b-slot"\n'
        'AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME="metadata"\n'
        'AUTO_AD_NEXIOS_UKI_CMDLINE_A="rootwait root=PARTLABEL=rootro_a ro console=ttyAMA0"\n'
        'AUTO_AD_NEXIOS_UKI_CMDLINE_B="rootwait root=PARTLABEL=rootro_b ro console=ttyAMA0"\n'
        'UKIFY_CMD="/build/tmp/sysroots-components/x86_64/systemd/usr/lib/systemd/ukify"\n'
        'UEFI_SECURE_BOOT="1"\n'
        'UKI_SB_KEY="/secure/path/DB.key"\n'
        'UKI_SB_CERT="/secure/path/DB.crt"\n'
        'SECRET_TOKEN="do-not-capture"\n'
        'AUTH_HEADER="Bearer do-not-capture"\n'
        'COOKIE="session=do-not-capture"\n'
    )

    variables = module.parse_bitbake_env(raw)

    assert variables == {
        "AUTO_AD_NEXIOS_UKI_A": "auto-ad-nexios-a.efi",
        "AUTO_AD_NEXIOS_UKI_B": "auto-ad-nexios-b.efi",
        "AUTO_AD_NEXIOS_SLOT_DIR_A": "EFI/Linux/a-slot",
        "AUTO_AD_NEXIOS_SLOT_DIR_B": "EFI/Linux/b-slot",
        "AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME": "metadata",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_A": (
            "rootwait root=PARTLABEL=rootro_a ro console=ttyAMA0"
        ),
        "AUTO_AD_NEXIOS_UKI_CMDLINE_B": (
            "rootwait root=PARTLABEL=rootro_b ro console=ttyAMA0"
        ),
        "EFI_ARCH": "aa64",
        "INITRD_ARCHIVE": "nexios-image-apollo-fvp.rootfs.cpio.gz",
        "KERNEL_CONSOLE": "ttyAMA0",
        "MACHINE": "apollo-fvp",
        "UEFI_SECURE_BOOT": "1",
        "UKIFY_CMD": "/build/tmp/sysroots-components/x86_64/systemd/usr/lib/systemd/ukify",
        "UKI_SB_CERT": "/secure/path/DB.crt",
        "UKI_SB_KEY": "/secure/path/DB.key",
    }


def test_parse_bitbake_env_keeps_qbox_provider_values() -> None:
    module = load_module()
    raw = (
        'MACHINE="apollo-qvp"\n'
        'QBOX_APOLLO_BUILD_TARGET="apollo_fvp_full_system"\n'
        'HSOC_APOLLO_QBOX_SRC="/repo/hsoc-stack/tools/qbox"\n'
        'HSOC_APOLLO_QBOX_PLATFORM_SRC="/repo/hsoc-stack/tools/qbox-platform"\n'
        'HSOC_APOLLO_QEMU_SRC="/repo/hsoc-stack/tools/qemu"\n'
        'EXTERNALSRC="/repo/hsoc-stack/tools/qbox-platform"\n'
        'EXTERNALSRC_BUILD="/work/qbox-apollo-qvp-native/build"\n'
        'SECRET_TOKEN="do-not-capture"\n'
    )

    variables = module.parse_bitbake_env(raw)

    assert variables == {
        "EXTERNALSRC": "/repo/hsoc-stack/tools/qbox-platform",
        "EXTERNALSRC_BUILD": "/work/qbox-apollo-qvp-native/build",
        "HSOC_APOLLO_QBOX_PLATFORM_SRC": "/repo/hsoc-stack/tools/qbox-platform",
        "HSOC_APOLLO_QBOX_SRC": "/repo/hsoc-stack/tools/qbox",
        "HSOC_APOLLO_QEMU_SRC": "/repo/hsoc-stack/tools/qemu",
        "MACHINE": "apollo-qvp",
        "QBOX_APOLLO_BUILD_TARGET": "apollo_fvp_full_system",
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

    assert args.output == Path("build/local-apollo-qvp/yocto-local-build-vars.json")
    assert args.build_dir == Path("build")
    assert args.timeout == 600


def test_parse_args_derives_default_output_from_explicit_build_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    build_dir = tmp_path / "custom-build"
    conf_dir = build_dir / "conf"
    conf_dir.mkdir(parents=True)
    (conf_dir / "local.conf").write_text('MACHINE ??= "apollo-qvp"\n', encoding="utf-8")
    monkeypatch.setattr("sys.argv", [str(SCRIPT), "--build-dir", str(build_dir)])

    args = module.parse_args()

    assert args.output == build_dir / "local-apollo-qvp/yocto-local-build-vars.json"


def test_default_recipes_match_apollo_fvp_parity_scope() -> None:
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
        "qbox-apollo-qvp-native",
    )


def test_parse_args_uses_machine_specific_firmware_recipe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    build_dir = tmp_path / "custom-build"
    conf_dir = build_dir / "conf"
    conf_dir.mkdir(parents=True)
    (conf_dir / "local.conf").write_text('MACHINE ??= "apollo-qvp"\n', encoding="utf-8")
    monkeypatch.setattr("sys.argv", [str(SCRIPT), "--build-dir", str(build_dir)])

    args = module.parse_args()

    recipes = module.parse_recipe_list(args.recipes)
    assert "firmware-apollo-qvp" in recipes
    assert "firmware-apollo-fvp" not in recipes


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
        *REQUIRED_UKI_VARIABLES,
        *REQUIRED_QBOX_VARIABLES,
    }


def test_allowlist_includes_only_explicit_auto_ad_nexios_uki_variables() -> None:
    module = load_module()

    assert REQUIRED_UKI_VARIABLES <= module.ALLOWLISTED_VARIABLES
    assert "SECRET_TOKEN" not in module.ALLOWLISTED_VARIABLES
    assert "AUTH_HEADER" not in module.ALLOWLISTED_VARIABLES
    assert "COOKIE" not in module.ALLOWLISTED_VARIABLES


def test_allowlist_includes_qbox_provider_variables() -> None:
    module = load_module()

    assert REQUIRED_QBOX_VARIABLES <= module.ALLOWLISTED_VARIABLES


def test_parse_recipe_list_rejects_malformed_recipe_name() -> None:
    module = load_module()

    with pytest.raises(argparse.ArgumentTypeError, match="bad recipe"):
        module.parse_recipe_list("nexios-image,bad recipe")

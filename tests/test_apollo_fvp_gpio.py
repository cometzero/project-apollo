from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FVP_HW_CONFIG = (
    ROOT
    / "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/"
    "apollo_fvp_fvp.dts"
)
QVP_HW_CONFIG = (
    ROOT
    / "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/"
    "apollo_qvp_fvp.dts"
)
QVP_LINUX_DTS = (
    ROOT
    / "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/"
    "apollo-qvp.dtsi"
)
QVP_DEFCONFIG = (
    ROOT
    / "hsoc-stack/components/primary_compute/linux/arch/arm64/configs/"
    "apollo_qvp_defconfig"
)
QVP_BSP_IMAGE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
    "nexios-bsp-initramfs.bb"
)
QVP_TFM_PLATFORM = (
    ROOT
    / "hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/"
    "arm/rse/automotive_rd/apollo-qvp"
)


def test_fvp_hw_config_exposes_smd_pl061_to_linux() -> None:
    hw_config = FVP_HW_CONFIG.read_text(encoding="utf-8")

    assert "gpio@40750000" in hw_config
    assert 'compatible = "arm,pl061", "arm,primecell";' in hw_config
    assert "interrupts = <GIC_SPI 193 IRQ_TYPE_LEVEL_HIGH>;" in hw_config


def test_qvp_hw_config_exposes_smd_pl061_to_linux() -> None:
    hw_config = QVP_HW_CONFIG.read_text(encoding="utf-8")

    assert "gpio@40750000" in hw_config
    assert 'compatible = "arm,pl061", "arm,primecell";' in hw_config
    assert "interrupts = <GIC_SPI 193 IRQ_TYPE_LEVEL_HIGH>;" in hw_config


def test_qvp_kernel_enables_smd_pl061() -> None:
    dts = QVP_LINUX_DTS.read_text(encoding="utf-8")
    defconfig = QVP_DEFCONFIG.read_text(encoding="utf-8")

    assert "gpio@40750000" in dts
    assert 'compatible = "arm,pl061", "arm,primecell";' in dts
    assert "interrupts = <GIC_SPI 193 IRQ_TYPE_LEVEL_HIGH>;" in dts
    assert "CONFIG_GPIO_PL061=y" in defconfig


def test_qvp_bsp_installs_gpio_tools() -> None:
    image = QVP_BSP_IMAGE.read_text(encoding="utf-8")

    assert 'PACKAGE_INSTALL:append:apollo-qvp = " libgpiod-tools"' in image


def test_qvp_tfm_enables_gpio_self_test_and_ap_atu() -> None:
    config = (QVP_TFM_PLATFORM / "config.cmake").read_text(encoding="utf-8")
    cmake = (QVP_TFM_PLATFORM / "CMakeLists.txt").read_text(encoding="utf-8")
    header = (QVP_TFM_PLATFORM / "device/host_device_definition.h").read_text(
        encoding="utf-8"
    )
    devices = (QVP_TFM_PLATFORM / "device/host_device_definition.c").read_text(
        encoding="utf-8"
    )

    assert "RSE_GPIO_SELF_TEST" in config
    assert "$<$<BOOL:${RSE_GPIO_SELF_TEST}>:RSE_GPIO_SELF_TEST>" in cmake
    assert "AP_ATU_REGION_IDX_SMD_GPIO" in header
    assert ".log_addr = 0x40750000UL" in devices
    assert ".phy_addr = 0x20000D0310000ULL" in devices
    assert ".bus_attr = ATU_ENCODE_ATTRIBUTES_NON_SECURE_PAS" in devices

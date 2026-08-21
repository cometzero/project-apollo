from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BSP_LAYER = ROOT / "hsoc-stack/yocto/meta-hsoc-bsp"
FVP_MACHINE = BSP_LAYER / "conf/machine/apollo-fvp.conf"
FVP_BOOT_CONFIG = (
    BSP_LAYER
    / "recipes-bsp/u-boot/files/apollo-fvp-auto-ad-nexios.cfg"
)
QVP_BOOT_CONFIG = (
    BSP_LAYER
    / "recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg"
)
SYSTEMD_BOOT_SCRIPT = (
    BSP_LAYER
    / "recipes-bsp/u-boot/files/auto-ad-nexios-systemd-boot.cmd"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_product_esp_exposes_systemd_discoverable_slot_ukis() -> None:
    # Given: the BSP and product images share one Apollo FVP machine.
    # When: product ESP additions are inspected.
    machine = read(FVP_MACHINE)

    # Then: only nexios-image exposes non-auto Type #2 UKI aliases and script.
    assert "IMAGE_EFI_BOOT_FILES:append:pn-nexios-image" in machine
    assert "${AUTO_AD_NEXIOS_UKI_A};EFI/Linux/nexios-a.efi" in machine
    assert "${AUTO_AD_NEXIOS_UKI_B};EFI/Linux/nexios-b.efi" in machine
    assert "auto-ad-nexios-systemd-boot.scr" in machine
    assert "WKS_FILE_DEPENDS:append:pn-nexios-image" in machine


def test_fvp_bootcommand_preserves_bsp_direct_uki_fallback() -> None:
    # Given: one U-Boot binary boots both product and BSP WIC images.
    # When: the FVP auto-ad-nexios boot command is inspected.
    fvp = read(FVP_BOOT_CONFIG)
    qvp = read(QVP_BOOT_CONFIG)

    # Then: product can source systemd policy while a missing script retains
    # the direct selected-then-fallback UKI path used by the BSP image.
    assert "auto-ad-nexios-systemd-boot.scr" in fvp
    assert "source ${scriptaddr}" in fvp
    assert "load virtio 0:${aanx_boot_part} ${loadaddr} ${aanx_uki}" in fvp
    assert "auto-ad-nexios: trying fallback ${aanx_fallback_uki}" in fvp
    assert "auto-ad-nexios-systemd-boot.scr" not in qvp


def test_systemd_script_selects_the_matching_ab_entry() -> None:
    # Given: aanxbootselect exports selected and fallback A/B slot names.
    # When: the product systemd-boot handoff policy is inspected.
    script = read(SYSTEMD_BOOT_SCRIPT)

    # Then: U-Boot supplies a UTF-16 LoaderEntryOneShot under systemd's GUID,
    # chainloads systemd-boot, and retries the validated alternate slot.
    assert "4a67b082-0a4c-41cf-b6c7-440b29bb8c4f" in script
    assert "LoaderEntryOneShot" in script
    assert "EFI/Linux/nexios-a.efi" in script
    assert "EFI/Linux/nexios-b.efi" in script
    assert "EFI/BOOT/bootaa64.efi" in script
    assert "auto-ad-nexios: chainloading systemd-boot for slot" in script
    assert "auto-ad-nexios: trying fallback" in script
    assert "\\\n        -nv -bs -rt LoaderEntryOneShot" not in script

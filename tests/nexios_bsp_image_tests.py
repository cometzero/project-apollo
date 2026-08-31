from __future__ import annotations

from nexios_bsp_workflow_support import ROOT


def test_bsp_metadata_contract_files_exist() -> None:
    # Given: the two owning Yocto layers.
    auto_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    bsp_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-bsp"

    # When: the BSP image contract is inspected.
    expected = (
        auto_layer / "recipes-core/images/nexios-bsp-initramfs.bb",
        auto_layer / "recipes-core/initrdscripts/nexios-bsp-init_1.0.bb",
        auto_layer / "recipes-core/initrdscripts/nexios-bsp-init/init",
        auto_layer
        / "recipes-core/initrdscripts/nexios-bsp-init/nexios-bsp-selftest",
        auto_layer / "lib/oeqa/runtime/cases/test_01_bsp_ssh.py",
        bsp_layer / "wic/apollo-fvp-nexios-bsp-initramfs.wks.in",
        bsp_layer / "wic/apollo-qvp-nexios-bsp-initramfs.wks.in",
    )

    # Then: every BitBake-consumed metadata input exists.
    assert all(path.is_file() for path in expected)


def test_bsp_image_and_init_provide_ssh_over_user_networking() -> None:
    auto_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    image = (auto_layer / "recipes-core/images/nexios-bsp-initramfs.bb").read_text(
        encoding="utf-8"
    )
    init = (
        auto_layer / "recipes-core/initrdscripts/nexios-bsp-init/init"
    ).read_text(encoding="utf-8")

    assert "dropbear" in image
    assert "allow-empty-password" in image
    assert "allow-root-login" in image
    assert "empty-root-password" in image
    assert "udhcpc" in init
    assert "dropbearkey -t rsa" in init
    assert 'dropbear -r "${dropbear_key}" -p 22 -B' in init
    assert "NEXIOS_BSP_NETWORK" in init
    assert "NEXIOS_BSP_SSH" in init


def test_local_buildroot_defconfig_enables_dropbear_for_bsp_init() -> None:
    # Given: the local BSP /init requires dropbearkey and dropbear before ready.
    module = (ROOT / "scripts/build/modules/build_buildroot.sh").read_text(
        encoding="utf-8"
    )
    defconfig = module.split("write_buildroot_defconfig()\n{\n", 1)[1].split(
        "\n}\n\nbuildroot_defconfig_digest", 1
    )[0]

    # When: the generated Buildroot defconfig contract is inspected.
    # Then: the daemon required by /init is selected for the target image.
    assert "BR2_PACKAGE_DROPBEAR=y" in defconfig
    assert 'mkdir -p "${BUILDROOT_OVERLAY}/var/run/dropbear"' in module
    assert 'require_file "${BUILDROOT_BUILD_DIR}/target/usr/sbin/dropbear"' in module
    assert 'require_file "${BUILDROOT_BUILD_DIR}/target/usr/bin/dropbearkey"' in module
    assert 'require_dir "${BUILDROOT_BUILD_DIR}/target/var/run/dropbear"' in module


def test_bsp_default_oeqa_suite_requires_ssh_uname() -> None:
    auto_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    distro = (auto_layer / "conf/distro/auto-ad-nexios.conf").read_text(
        encoding="utf-8"
    )
    controller = (auto_layer / "lib/oeqa/controllers/hsocfvp.py").read_text(
        encoding="utf-8"
    )
    ssh_case = (
        auto_layer / "lib/oeqa/runtime/cases/test_01_bsp_ssh.py"
    ).read_text(encoding="utf-8")

    assert (
        'HSOC_APOLLO_BSP_TEST_SUITES = '
        '"test_00_bsp_boot test_01_bsp_ssh"'
    ) in distro
    assert "def run_ssh(" in controller
    assert "self.target.run_ssh(\"uname -a\"" in ssh_case
    assert "test_00_bsp_boot.BspBootTest.test_bsp_boot" in ssh_case


def test_bsp_uki_uses_timestamp_stable_initramfs_link() -> None:
    # Given: image tasks may remain stamped while BitBake reparses DATETIME.
    image_recipe = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
        "nexios-bsp-initramfs.bb"
    ).read_text(encoding="utf-8")

    # When: the UKI input path is resolved after a later parse.
    # Then: it uses the stable image link, not the timestamped IMAGE_NAME.
    assert (
        'AUTO_AD_NEXIOS_UKI_INITRD = '
        '"${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.cpio.gz"'
    ) in image_recipe
    assert '${IMGDEPLOYDIR}/${IMAGE_NAME}.cpio.gz' not in image_recipe


def test_bsp_uki_uses_single_esp_slot_directories_and_metadata() -> None:
    # Given: product and BSP UKIs share DEPLOY_DIR_IMAGE but U-Boot uses one
    # stable A/B filename contract inside each image's single ESP.
    layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    uki_class = (layer / "classes/auto-ad-nexios-uki-ab.bbclass").read_text(
        encoding="utf-8"
    )
    bsp_image = (
        layer / "recipes-core/images/nexios-bsp-initramfs.bb"
    ).read_text(encoding="utf-8")

    # When: the class maps deploy artifacts into per-slot ESP directories.
    # Then: source names remain unique while UKIs and identity metadata follow
    # the U-Boot single-partition contract.
    assert (
        'AUTO_AD_NEXIOS_UKI_ESP_A ?= "${AUTO_AD_NEXIOS_UKI_A}"'
        in uki_class
    )
    assert (
        'AUTO_AD_NEXIOS_UKI_ESP_B ?= "${AUTO_AD_NEXIOS_UKI_B}"'
        in uki_class
    )
    assert (
        'AUTO_AD_NEXIOS_SLOT_DIR_A ?= "EFI/Linux/a-slot"'
        in uki_class
    )
    assert (
        'AUTO_AD_NEXIOS_SLOT_DIR_B ?= "EFI/Linux/b-slot"'
        in uki_class
    )
    assert (
        'AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME ?= "metadata"'
        in uki_class
    )
    assert (
        "${AUTO_AD_NEXIOS_UKI_A};"
        "${AUTO_AD_NEXIOS_SLOT_DIR_A}/${AUTO_AD_NEXIOS_UKI_ESP_A}"
        in uki_class
    )
    assert (
        "${AUTO_AD_NEXIOS_UKI_B};"
        "${AUTO_AD_NEXIOS_SLOT_DIR_B}/${AUTO_AD_NEXIOS_UKI_ESP_B}"
        in uki_class
    )
    assert (
        "${AUTO_AD_NEXIOS_SLOT_METADATA_A};"
        "${AUTO_AD_NEXIOS_SLOT_DIR_A}/"
        "${AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME}"
        in uki_class
    )
    assert 'stream.write("slot=%s\\n" % slot)' in uki_class
    assert "IMAGE_EFI_BOOT_FILES_label-boot_a" not in uki_class
    assert "IMAGE_EFI_BOOT_FILES_label-boot_b" not in uki_class
    assert "auto_ad_nexios_install_slot_uki" not in uki_class
    assert (
        'AUTO_AD_NEXIOS_UKI_A = "nexios-bsp-initramfs-a.efi"'
        in bsp_image
    )
    assert (
        'AUTO_AD_NEXIOS_UKI_B = "nexios-bsp-initramfs-b.efi"'
        in bsp_image
    )
    assert (
        'AUTO_AD_NEXIOS_UKI_ESP_A = "auto-ad-nexios-a.efi"'
        in bsp_image
    )
    assert (
        'AUTO_AD_NEXIOS_UKI_ESP_B = "auto-ad-nexios-b.efi"'
        in bsp_image
    )

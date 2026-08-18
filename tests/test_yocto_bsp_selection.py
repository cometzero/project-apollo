from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISTRO_CONFIG = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/auto-ad-nexios.conf"
)
BSP_RECIPE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
    "nexios-bsp-initramfs.bb"
)
PRODUCT_RECIPE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
    "nexios-image.bbappend"
)
INITRAMFS_INCLUDE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/include/"
    "auto-ad-nexios-initramfs.inc"
)
INITRAMFS_RECIPE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
    "nexios-initramfs-image.bb"
)


def test_bsp_recipe_owns_non_verity_policy() -> None:
    distro = DISTRO_CONFIG.read_text(encoding="utf-8")
    recipe = BSP_RECIPE.read_text(encoding="utf-8")

    assert "APOLLO_BSP_BUILD_ONLY" not in distro
    assert 'APOLLO_DM_VERITY = "0"' in recipe


def test_product_recipe_owns_initramfs_policy() -> None:
    recipe = PRODUCT_RECIPE.read_text(encoding="utf-8")
    initramfs_recipe = INITRAMFS_RECIPE.read_text(encoding="utf-8")

    assert not INITRAMFS_INCLUDE.exists()
    assert 'INITRAMFS_IMAGE:auto-ad-nexios = "nexios-initramfs-image"' in recipe
    assert 'INITRAMFS_FSTYPES = "cpio.gz"' in initramfs_recipe

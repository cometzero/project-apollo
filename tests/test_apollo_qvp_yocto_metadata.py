from __future__ import annotations

from pathlib import Path
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]

AUTO_SOLUTIONS: Final = Path("hsoc-stack/yocto/meta-hsoc-auto-solutions")
BSP: Final = Path("hsoc-stack/yocto/meta-hsoc-bsp")

REQUIRED_QVP_PATHS: Final = (
    AUTO_SOLUTIONS / "conf/templates/apollo-qvp/local.conf.sample",
    AUTO_SOLUTIONS / "conf/templates/apollo-qvp/bblayers.conf.sample",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-qvp-dm-verity.conf",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-qvp-no-dm-verity.conf",
    BSP / "conf/machine/apollo-qvp.conf",
    BSP / "conf/machine/include/apollo-qvp-cassini-extra-settings.inc",
    BSP / "recipes-bsp/images/firmware-apollo-qvp.bb",
    BSP / "recipes-bsp/images/uefi-capsule-apollo-qvp.bb",
    BSP / "wic/apollo-qvp-auto-ad-nexios-ab.wks.in",
    BSP / "wic/apollo-qvp-auto-ad-nexios-ab-plain.wks.in",
)

APOLLO_FVP_ORIGINAL_PATHS: Final = (
    AUTO_SOLUTIONS / "conf/templates/apollo-fvp/local.conf.sample",
    AUTO_SOLUTIONS / "conf/templates/apollo-fvp/bblayers.conf.sample",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-fvp-dm-verity.conf",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-fvp-no-dm-verity.conf",
    BSP / "conf/machine/apollo-fvp.conf",
    BSP / "conf/machine/include/apollo-fvp-cassini-extra-settings.inc",
    BSP / "recipes-bsp/images/firmware-apollo-fvp.bb",
    BSP / "recipes-bsp/images/uefi-capsule-apollo-fvp.bb",
    BSP / "wic/apollo-fvp-auto-ad-nexios-ab.wks.in",
    BSP / "wic/apollo-fvp-auto-ad-nexios-ab-plain.wks.in",
)

QVP_DEPLOY_VISIBLE_PATHS: Final = (
    AUTO_SOLUTIONS / "conf/templates/apollo-qvp/local.conf.sample",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-qvp-dm-verity.conf",
    AUTO_SOLUTIONS / "conf/multiconfig/apollo-qvp-no-dm-verity.conf",
    BSP / "conf/machine/apollo-qvp.conf",
    BSP / "conf/machine/include/apollo-qvp-cassini-extra-settings.inc",
    BSP / "recipes-bsp/images/firmware-apollo-qvp.bb",
    BSP / "recipes-bsp/images/uefi-capsule-apollo-qvp.bb",
    BSP / "wic/apollo-qvp-auto-ad-nexios-ab.wks.in",
    BSP / "wic/apollo-qvp-auto-ad-nexios-ab-plain.wks.in",
)

QBOX_NATIVE_UI_PATHS: Final = (
    BSP / "recipes-devtools/qbox/qbox-libqemu-native.bb",
    BSP / "recipes-graphics/libepoxy/libepoxy_%.bbappend",
    BSP / "recipes-graphics/mesa/mesa.bbappend",
)

QBOX_HEADLESS_REMOVAL_PATHS: Final = (
    Path("hsoc-stack/tools/qbox/CMakeLists.txt"),
    Path("hsoc-stack/tools/qbox/qemu-components/CMakeLists.txt"),
    Path("hsoc-stack/tools/qbox/qemu-components/common/include/libqemu-cxx/libqemu-cxx.h"),
    Path("hsoc-stack/tools/qbox/qemu-components/common/src/libqemu-cxx/console.cc"),
    Path("hsoc-stack/tools/qbox/qemu-components/common/src/libqemu-cxx/libqemu-cxx.cc"),
    Path("hsoc-stack/tools/qemu/qemu.cmake"),
    Path("hsoc-stack/tools/qemu/libqemu/exports.py"),
    Path("hsoc-stack/tools/qemu/libqemu/wrappers/console.c"),
    Path("hsoc-stack/tools/qemu/libqemu/wrappers/meson.build"),
    Path("hsoc-stack/tools/qemu/scripts/libqemu-wrappers.py"),
    BSP / "recipes-devtools/qbox/qbox-libqemu-native.bb",
)

QBOX_NATIVE_RUNTIME_PATHS: Final = (
    Path("run_qbox_yocto.sh"),
    BSP / "recipes-devtools/qbox/qbox-apollo-qvp-native.bb",
)

REQUIRED_SNIPPETS: Final = {
    AUTO_SOLUTIONS
    / "conf/templates/apollo-qvp/local.conf.sample": (
        'MACHINE ??= "apollo-qvp"',
        'DISTRO ??= "auto-ad-nexios"',
    ),
    AUTO_SOLUTIONS
    / "conf/multiconfig/apollo-qvp-dm-verity.conf": (
        'MACHINE = "apollo-qvp"',
        'APOLLO_DM_VERITY = "1"',
    ),
    AUTO_SOLUTIONS
    / "conf/multiconfig/apollo-qvp-no-dm-verity.conf": (
        'MACHINE = "apollo-qvp"',
        'APOLLO_DM_VERITY = "0"',
    ),
    AUTO_SOLUTIONS / "conf/distro/auto-ad-nexios.conf": (
        "WKS_FILE:apollo-qvp:auto-ad-nexios",
        "WKS_FILE_DEPENDS:append:apollo-qvp:auto-ad-nexios",
    ),
    AUTO_SOLUTIONS / "recipes-core/images/nexios-image.bbappend": (
        'HSOC_WRITABLE_FLASH_MACHINES = "apollo-fvp apollo-qvp"',
    ),
    BSP / "conf/machine/apollo-qvp.conf": (
        'KMACHINE = "apollo-qvp"',
        'ARM_SYSTEMREADY_FIRMWARE = "firmware-apollo-qvp:do_deploy"',
    ),
    BSP / "recipes-bsp/images/firmware-apollo-qvp.bb": (
        'APOLLO_FIRMWARE_MACHINE = "apollo-qvp"',
        "require firmware-apollo-common.inc",
        "do_generate_rse_otp_image",
        "provision_rse_otp_image.py",
        "rse-otp-image.img",
    ),
    BSP / "recipes-bsp/images/firmware-apollo-common.inc": (
        "require recipes-bsp/images/firmware-fvp-rd-aspen.bb",
        'SUMMARY = "The firmware images for ${APOLLO_FIRMWARE_MACHINE}"',
        'COMPATIBLE_MACHINE = "${APOLLO_FIRMWARE_MACHINE}"',
    ),
    BSP / "recipes-bsp/images/uefi-capsule-apollo-qvp.bb": (
        'APOLLO_UEFI_CAPSULE_MACHINE = "apollo-qvp"',
        "require uefi-capsule-apollo-common.inc",
    ),
    BSP / "recipes-bsp/images/uefi-capsule-apollo-common.inc": (
        "require recipes-bsp/images/uefi-capsule-fvp-rd-aspen.bb",
        'SUMMARY = "The UEFI capsule generation for ${APOLLO_UEFI_CAPSULE_MACHINE}"',
        'COMPATIBLE_MACHINE = "${APOLLO_UEFI_CAPSULE_MACHINE}"',
    ),
    BSP / "conf/layer.conf": (
        'HSOC_APOLLO_QEMU_SRC ?= "${HSOC_APOLLO_BASE}/tools/qemu"',
        'HSOC_APOLLO_QBOX_SRC ?= "${HSOC_APOLLO_BASE}/tools/qbox"',
        'HSOC_APOLLO_QBOX_PLATFORM_SRC ?= "${HSOC_APOLLO_BASE}/tools/qbox-platform"',
    ),
}

REQUIRED_QBOX_NATIVE_UI_SNIPPETS: Final = {
    BSP / "recipes-devtools/qbox/qbox-libqemu-native.bb": (
        'QBOX_LIBQEMU_NATIVE_PACKAGECONFIG ?= "opengl sdl vnc vnc-jpeg"',
        'PACKAGECONFIG ??= "${QBOX_LIBQEMU_NATIVE_PACKAGECONFIG}"',
        'PACKAGECONFIG[opengl] = ",,libepoxy-native"',
        'PACKAGECONFIG[sdl] = ",,libsdl2-native"',
        'PACKAGECONFIG[vnc-jpeg] = ",,jpeg-native"',
    ),
    BSP / "recipes-graphics/libepoxy/libepoxy_%.bbappend": (
        'DISTRO_FEATURES:append:class-native = " opengl"',
        'PACKAGECONFIG:class-native = "egl"',
    ),
    BSP / "recipes-graphics/mesa/mesa.bbappend": (
        'DISTRO_FEATURES:append:class-native = " opengl"',
        'PACKAGECONFIG:class-native = "opengl egl gallium"',
        'PACKAGECONFIG:remove:class-native = "gallium-llvm r600"',
    ),
}

REQUIRED_QBOX_HEADLESS_REMOVAL_SNIPPETS: Final = {
    Path("hsoc-stack/tools/qemu/qemu.cmake"): (
        "--enable-opengl",
        "--enable-sdl",
        "--enable-vnc",
        "--enable-vnc-jpeg",
    ),
}

REQUIRED_QBOX_NATIVE_RUNTIME_SNIPPETS: Final = {
    AUTO_SOLUTIONS / "classes/qboxboot.bbclass": (
        "addtask do_write_qboxboot_conf after do_image before do_image_complete",
    ),
    Path("run_qbox_yocto.sh"): (
        'recipe_sysroot_native_path / "usr" / "lib"',
        "ld_entries.append(str(recipe_sysroot_native_libdir))",
    ),
    BSP / "recipes-devtools/qbox/qbox-apollo-qvp-native.bb": (
        "qbox_apollo_install_runtime_libraries",
        '${B}/_deps/report-build',
        '${B}/_deps/systemclanguage-build/src',
        "libreporting.so",
        "libsystemc.so.3.0",
        "librpc.so",
        'QBOX_APOLLO_RUN_UNIT_TESTS ?= "0"',
        'PACKAGECONFIG[unit-tests] = "-DBUILD_TESTING=ON,-DBUILD_TESTING=OFF"',
        "do_check",
        "cmake_runcmake_build --target ${QBOX_APOLLO_UNIT_TEST_TARGET}",
        'ctest --test-dir "${B}" -L "${QBOX_APOLLO_UNIT_TEST_LABEL}" --output-on-failure',
        "addtask check after do_compile before do_install",
    ),
}

FORBIDDEN_QBOX_HEADLESS_SNIPPETS: Final = (
    "QBOX_LIBQEMU_HAS_SDL",
    "LIBQEMU_HEADLESS",
    "SDL_COND",
    "cond = SDL_COND",
    "cond=SDL_COND",
    "#ifdef CONFIG_SDL",
    "#ifndef CONFIG_OPENGL",
    "-DLIBQEMU_ENABLE_OPENGL=ON",
    "-DLIBQEMU_ENABLE_OPENGL=OFF",
    "-DLIBQEMU_ENABLE_SDL=ON",
    "-DLIBQEMU_ENABLE_SDL=OFF",
    "-DLIBQEMU_ENABLE_VNC=ON",
    "-DLIBQEMU_ENABLE_VNC=OFF",
    "-DLIBQEMU_ENABLE_VNC_JPEG=ON",
    "-DLIBQEMU_ENABLE_VNC_JPEG=OFF",
    "libqemu_ss.add(when: 'CONFIG_SDL'",
)

REQUIRED_DOC_SNIPPETS: Final = {
    Path("README.md"): (
        "build/tmp_baremetal/deploy/images/apollo-qvp/",
        "nexios-image-apollo-qvp.qboxconf",
        "native sysroot provider",
        "qbox-apollo-qvp-native",
        "To run the default Apollo QVP Yocto deploy image",
    ),
    Path("doc/apollo-qvp-yocto-qbox-runbook.md"): (
        "build/tmp_baremetal/deploy/images/apollo-qvp",
        "QBox Native Sysroot/qboxconf",
        "provider.bindir",
        "sysroot.recipe_sysroot_native",
        "apollo_fvp_full_system",
        "fvp-rd-aspen",
        "blocked_disk_space_stoptasks",
        "runtime_blocked_missing_artifacts",
    ),
    Path("doc/source-structure-ko.md"): (
        "conf/templates/apollo-qvp/",
        "recipes-devtools/qbox/",
        "qbox-libqemu-native",
        "qbox-apollo-qvp-native",
        ".qboxconf",
        "native sysroot provider",
    ),
}

FVP_RD_ASPEN_ALLOWLIST: Final = (
    (
        BSP / "conf/machine/apollo-qvp.conf",
        "# Keep the fvp-rd-aspen override visible so existing non-kernel BSP",
    ),
    (BSP / "conf/machine/apollo-qvp.conf", 'MACHINEOVERRIDES =. "fvp-rd-aspen:"'),
    (BSP / "conf/machine/apollo-qvp.conf", 'NATIVE_MACHINE = "fvp-rd-aspen"'),
    (BSP / "conf/machine/apollo-qvp.conf", "require conf/machine/fvp-rd-aspen.conf"),
    (
        BSP / "conf/machine/apollo-qvp.conf",
        'EXTRA_IMAGEDEPENDS:remove = "efi-capsule-update-disk-image-fvp-rd-aspen:do_deploy"',
    ),
    (
        BSP / "conf/machine/include/apollo-qvp-cassini-extra-settings.inc",
        "require conf/machine/include/fvp-rd-aspen-cassini-extra-settings.inc",
    ),
)


def missing_paths(root: Path, paths: tuple[Path, ...]) -> list[str]:
    return [path.as_posix() for path in paths if not (root / path).exists()]


def missing_snippets(root: Path, snippets: dict[Path, tuple[str, ...]]) -> list[str]:
    missing: list[str] = []
    for path, required in snippets.items():
        text = (root / path).read_text(encoding="utf-8")
        missing.extend(
            f"{path.as_posix()}: {snippet}"
            for snippet in required
            if snippet not in text
        )
    return missing


def fvp_rd_aspen_occurrences(root: Path) -> list[tuple[Path, str]]:
    occurrences: list[tuple[Path, str]] = []
    for path in QVP_DEPLOY_VISIBLE_PATHS:
        for line in (root / path).read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if "fvp-rd-aspen" in stripped:
                occurrences.append((path, stripped))
    return occurrences


def test_required_qvp_and_fvp_metadata_files_exist() -> None:
    missing = missing_paths(
        ROOT,
        REQUIRED_QVP_PATHS
        + APOLLO_FVP_ORIGINAL_PATHS
        + QBOX_NATIVE_UI_PATHS
        + QBOX_NATIVE_RUNTIME_PATHS,
    )

    assert missing == []


def test_missing_qvp_wic_is_reported_by_helper(tmp_path: Path) -> None:
    wic = BSP / "wic/apollo-qvp-auto-ad-nexios-ab.wks.in"

    missing = missing_paths(tmp_path, (wic,))

    assert missing == [wic.as_posix()]


def test_qvp_identity_and_source_variable_snippets_are_present() -> None:
    missing = missing_snippets(ROOT, REQUIRED_SNIPPETS)

    assert missing == []


def test_apollo_kernel_defconfig_preserves_yocto_fragments() -> None:
    # Given an explicit defconfig task shared by the Apollo kernel recipes.
    metadata = (
        ROOT / BSP / "recipes-kernel/linux/linux-yocto-apollo-common.inc"
    ).read_text(encoding="utf-8")
    task = metadata.split("do_defconfig() {", 1)[1].split("\n}", 1)[0]

    # When the task prepares the kernel configuration.
    uses_kernel_configme = "do_kernel_configme" in task
    applies_raw_defconfig = (
        "oe_runmake -C ${S} O=${B} ${APOLLO_KERNEL_DEFCONFIG}" in task
    )

    # Then it must retain kernel-yocto features such as dm-verity.
    assert uses_kernel_configme
    assert not applies_raw_defconfig


def test_auto_ad_nexios_uki_tracks_deployed_kernel_content() -> None:
    metadata = (
        ROOT / AUTO_SOLUTIONS / "classes/auto-ad-nexios-uki-ab.bbclass"
    ).read_text(encoding="utf-8")

    assert "do_uki[file-checksums]" in metadata
    assert "${DEPLOY_DIR_IMAGE}/${UKI_KERNEL_FILENAME}" in metadata


def test_qbox_native_ui_options_are_native_scoped() -> None:
    missing = missing_snippets(ROOT, REQUIRED_QBOX_NATIVE_UI_SNIPPETS)

    assert missing == []


def test_qbox_libqemu_headless_build_mode_is_removed() -> None:
    missing = missing_snippets(ROOT, REQUIRED_QBOX_HEADLESS_REMOVAL_SNIPPETS)
    assert missing == []

    offenders = [
        (path, snippet)
        for path in QBOX_HEADLESS_REMOVAL_PATHS
        for snippet in FORBIDDEN_QBOX_HEADLESS_SNIPPETS
        if snippet in (ROOT / path).read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_qbox_native_runtime_libraries_are_resolved_from_provider_and_sysroot() -> None:
    missing = missing_snippets(ROOT, REQUIRED_QBOX_NATIVE_RUNTIME_SNIPPETS)

    assert missing == []


def test_bad_apollo_qvp_override_is_reported_by_helper(tmp_path: Path) -> None:
    distro = AUTO_SOLUTIONS / "conf/distro/auto-ad-nexios.conf"
    (tmp_path / distro.parent).mkdir(parents=True)
    (tmp_path / distro).write_text(
        'WKS_FILE:apollo-fvp:auto-ad-nexios = "apollo-qvp-auto-ad-nexios-ab.wks.in"\n',
        encoding="utf-8",
    )

    missing = missing_snippets(
        tmp_path,
        {distro: ("WKS_FILE:apollo-qvp:auto-ad-nexios",)},
    )

    assert missing == [f"{distro.as_posix()}: WKS_FILE:apollo-qvp:auto-ad-nexios"]


def test_deploy_visible_qvp_metadata_does_not_point_to_apollo_fvp() -> None:
    offenders = [
        path.as_posix()
        for path in QVP_DEPLOY_VISIBLE_PATHS
        if "apollo-fvp" in (ROOT / path).read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_fvp_rd_aspen_compatibility_strings_match_allowlist() -> None:
    assert sorted(fvp_rd_aspen_occurrences(ROOT)) == sorted(FVP_RD_ASPEN_ALLOWLIST)


def test_apollo_qvp_documentation_contract_is_present() -> None:
    missing = missing_snippets(ROOT, REQUIRED_DOC_SNIPPETS)

    assert missing == []

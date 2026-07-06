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

REQUIRED_SNIPPETS: Final = {
    AUTO_SOLUTIONS
    / "conf/templates/apollo-qvp/local.conf.sample": (
        'MACHINE = "apollo-qvp"',
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
        'SUMMARY = "The firmware images for apollo-qvp"',
        'COMPATIBLE_MACHINE = "apollo-qvp"',
    ),
    BSP / "recipes-bsp/images/uefi-capsule-apollo-qvp.bb": (
        'SUMMARY = "The UEFI capsule generation for apollo-qvp"',
        'COMPATIBLE_MACHINE = "apollo-qvp"',
    ),
    BSP / "conf/layer.conf": (
        'HSOC_APOLLO_QEMU_SRC ?= "${HSOC_APOLLO_BASE}/tools/qemu"',
        'HSOC_APOLLO_QBOX_SRC ?= "${HSOC_APOLLO_BASE}/tools/qbox"',
        'HSOC_APOLLO_QBOX_PLATFORM_SRC ?= "${HSOC_APOLLO_BASE}/tools/qbox-platform"',
    ),
}

REQUIRED_DOC_SNIPPETS: Final = {
    Path("README.md"): (
        "build/tmp_baremetal/deploy/images/apollo-qvp/",
        "qbox-apollo-qvp/qbox-apollo-qvp-env.sh",
        "qbox-apollo-qvp-native",
        "./run_qbox_yocto.sh --machine apollo-qvp",
    ),
    Path("doc/apollo-qvp-yocto-qbox-runbook.md"): (
        "build/tmp_baremetal/deploy/images/apollo-qvp",
        "qbox-apollo-qvp-env.sh",
        "qbox-apollo-qvp-manifest.json",
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
        "qbox-apollo-qvp/",
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
        BSP / "conf/machine/include/apollo-qvp-cassini-extra-settings.inc",
        "require conf/machine/include/fvp-rd-aspen-cassini-extra-settings.inc",
    ),
    (
        BSP / "recipes-bsp/images/firmware-apollo-qvp.bb",
        "require recipes-bsp/images/firmware-fvp-rd-aspen.bb",
    ),
    (
        BSP / "recipes-bsp/images/uefi-capsule-apollo-qvp.bb",
        "require recipes-bsp/images/uefi-capsule-fvp-rd-aspen.bb",
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
    missing = missing_paths(ROOT, REQUIRED_QVP_PATHS + APOLLO_FVP_ORIGINAL_PATHS)

    assert missing == []


def test_missing_qvp_wic_is_reported_by_helper(tmp_path: Path) -> None:
    wic = BSP / "wic/apollo-qvp-auto-ad-nexios-ab.wks.in"

    missing = missing_paths(tmp_path, (wic,))

    assert missing == [wic.as_posix()]


def test_qvp_identity_and_source_variable_snippets_are_present() -> None:
    missing = missing_snippets(ROOT, REQUIRED_SNIPPETS)

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

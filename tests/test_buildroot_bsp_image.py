from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
BUILDROOT_SCRIPT: Final = ROOT / "scripts/build/modules/build_buildroot.sh"
PFDI_PACKAGE: Final = (
    ROOT
    / "scripts/build/buildroot-external/package/apollo-pfdi-bsp"
    / "apollo-pfdi-bsp.mk"
)
BUILDROOT_EXTERNAL_MK: Final = (
    ROOT / "scripts/build/buildroot-external/external.mk"
)
BOOT_DISK_SCRIPT: Final = (
    ROOT / "scripts/build/modules/build_boot_disk.sh"
)


def run_buildroot_function(
    command: str,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        env={**os.environ, **env},
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_overlay_uses_meta_hsoc_bsp_init_scripts(tmp_path: Path) -> None:
    init_source = tmp_path / "nexios-bsp-init"
    overlay = tmp_path / "overlay"
    init_source.mkdir()
    (init_source / "init").write_text("#!/bin/sh\necho init\n", encoding="utf-8")
    (init_source / "nexios-bsp-selftest").write_text(
        "#!/bin/sh\necho selftest\n",
        encoding="utf-8",
    )
    config_pack = tmp_path / "pfdi_test_config_0.pack"
    config_pack.write_bytes(b"pfdi config")
    result = run_buildroot_function(
        """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh
BUILDROOT_OVERLAY="${TEST_OVERLAY}"
BUILDROOT_BUILD_DIR="${TEST_BUILD_DIR}"
WORK_DIR="${TEST_WORK_DIR}"
NEXIOS_BSP_INIT_DIR="${TEST_INIT_SOURCE}"
PFDI_BSP_CONFIG_PACK="${TEST_CONFIG_PACK}"
prepare_buildroot_overlay
""",
        {
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
            "PC_CPUS_COUNT": "4",
            "TEST_BUILD_DIR": str(tmp_path / "buildroot"),
            "TEST_CONFIG_PACK": str(config_pack),
            "TEST_INIT_SOURCE": str(init_source),
            "TEST_OVERLAY": str(overlay),
            "TEST_WORK_DIR": str(tmp_path / "work"),
        },
    )

    assert result.returncode == 0, result.stderr
    assert (overlay / "init").read_text(encoding="utf-8") == (
        "#!/bin/sh\necho init\n"
    )
    assert (overlay / "usr/libexec/nexios-bsp/selftest").read_text(
        encoding="utf-8"
    ) == "#!/bin/sh\necho selftest\n"
    assert (overlay / "etc/nexios-bsp-machine").read_text(
        encoding="utf-8"
    ) == "apollo-qvp\n"
    assert (overlay / "etc/nexios-bsp-cpus").read_text(encoding="utf-8") == "4\n"
    assert (overlay / "etc/pfdi/pfdi_test_config_0.pack").read_bytes() == (
        b"pfdi config"
    )


def test_defconfig_selects_bsp_packages_without_replacing_mount(
    tmp_path: Path,
) -> None:
    headers = tmp_path / "sdk/usr/include/linux/version.h"
    headers.parent.mkdir(parents=True)
    headers.write_text(
        "#define LINUX_VERSION_MAJOR 6\n"
        "#define LINUX_VERSION_PATCHLEVEL 18\n",
        encoding="utf-8",
    )
    result = run_buildroot_function(
        """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh
SDK_TARGET_SYSROOT="${TEST_SDK}"
BUILDROOT_BUILD_DIR="${TEST_BUILD_DIR}"
BUILDROOT_TOOLCHAIN_DIR="${TEST_TOOLCHAIN}"
LINUX_BUILD_DIR="${TEST_LINUX_BUILD}"
write_buildroot_defconfig
""",
        {
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
            "TEST_BUILD_DIR": str(tmp_path / "buildroot"),
            "TEST_LINUX_BUILD": str(tmp_path / "linux-build"),
            "TEST_SDK": str(tmp_path / "sdk"),
            "TEST_TOOLCHAIN": str(tmp_path / "toolchain"),
        },
    )

    assert result.returncode == 0, result.stderr
    config = Path(result.stdout.strip()).read_text(encoding="utf-8")
    for symbol in (
        "BR2_PACKAGE_UTIL_LINUX=y",
        "BR2_PACKAGE_UTIL_LINUX_BINARIES=y",
        "BR2_LINUX_KERNEL=y",
        "BR2_PACKAGE_LINUX_TOOLS_PERF=y",
        "BR2_PACKAGE_ZSTD=y",
        "BR2_PACKAGE_APOLLO_PFDI_BSP=y",
    ):
        assert symbol in config
    assert "BR2_PACKAGE_UTIL_LINUX_MOUNT=y" not in config


def test_buildroot_finalize_forces_busybox_mount() -> None:
    external_makefile = BUILDROOT_EXTERNAL_MK.read_text(encoding="utf-8")

    assert "UTIL_LINUX_CONF_OPTS += --without-tinfo" in external_makefile
    assert "ln -sf busybox $(TARGET_DIR)/bin/mount" in external_makefile
    for library in (
        "libblkid.so.1",
        "libfdisk.so.1",
        "libmount.so.1",
        "libsmartcols.so.1",
        "libuuid.so.1",
    ):
        assert library in external_makefile


def test_local_boot_disk_matches_bsp_misc_partition() -> None:
    boot_disk_script = BOOT_DISK_SCRIPT.read_text(encoding="utf-8")

    assert '"${LOCAL_BUILD_MISC_IMAGE}"' in boot_disk_script
    assert "--new=2:" in boot_disk_script
    assert "--change-name=2:misc" in boot_disk_script


def test_tmp_baremetal_sources_feed_non_buildroot_packages(tmp_path: Path) -> None:
    work = tmp_path / "tmp_baremetal/work"
    for recipe in ("arm-si-rproc-mod", "rpmsg-net-mod", "pfdi-misc-mod"):
        (work / f"apollo_qvp-poky-linux/{recipe}/1.0/sources-unpack/src").mkdir(
            parents=True
        )
    pfdi = (
        work
        / "cortexa720-poky-linux/platform-fault-detection/1.0/sources-unpack/git"
    )
    pfdi.mkdir(parents=True)
    result = run_buildroot_function(
        """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh
resolve_buildroot_bsp_sources
printf '%s\n' "${ARM_SI_RPROC_SRC}" "${RPMSG_NET_SRC}" \
    "${PFDI_MISC_SRC}" "${PFDI_BSP_SRC}"
""",
        {
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
            "YOCTO_TMP": str(tmp_path / "tmp_baremetal"),
        },
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        str(
            work
            / "apollo_qvp-poky-linux/arm-si-rproc-mod/1.0/sources-unpack/src"
        ),
        str(work / "apollo_qvp-poky-linux/rpmsg-net-mod/1.0/sources-unpack/src"),
        str(work / "apollo_qvp-poky-linux/pfdi-misc-mod/1.0/sources-unpack/src"),
        str(pfdi),
    ]


def test_pfdi_external_package_uses_buildroot_cmake() -> None:
    package = PFDI_PACKAGE.read_text(encoding="utf-8")

    assert "APOLLO_PFDI_BSP_SOURCE_DIR" in package
    assert "pfdi-sample-app" in package
    assert "pfdi_test_config_0.pack" in package
    assert "$(eval $(cmake-package))" in package

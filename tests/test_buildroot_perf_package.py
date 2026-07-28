from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
PERF_PACKAGE_DIR: Final = (
    ROOT / "scripts/build/buildroot-external/package/apollo-perf"
)
PERF_PACKAGE: Final = PERF_PACKAGE_DIR / "apollo-perf.mk"
PERF_CONFIG: Final = PERF_PACKAGE_DIR / "Config.in"
BUILDROOT_EXTERNAL_CONFIG: Final = (
    ROOT / "scripts/build/buildroot-external/Config.in"
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


def test_buildroot_make_passes_linux_source_only_to_apollo_package(
    tmp_path: Path,
) -> None:
    result = run_buildroot_function(
        """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh
buildroot_env() {
    printf '<%s>\\n' "$@"
}
BUILDROOT_SRC="${TEST_BUILDROOT_SRC}"
BUILDROOT_BUILD_DIR="${TEST_BUILDROOT_BUILD}"
BUILDROOT_EXTERNAL="${TEST_BUILDROOT_EXTERNAL}"
LINUX_SRC="${TEST_LINUX_SRC}"
PFDI_BSP_SRC="${TEST_PFDI_SRC}"
PFDI_BSP_CONFIG_PACK="${TEST_PFDI_CONFIG}"
buildroot_make apollo-perf
""",
        {
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
            "TEST_BUILDROOT_BUILD": str(tmp_path / "buildroot-build"),
            "TEST_BUILDROOT_EXTERNAL": str(tmp_path / "buildroot-external"),
            "TEST_BUILDROOT_SRC": str(tmp_path / "buildroot"),
            "TEST_LINUX_SRC": str(tmp_path / "linux"),
            "TEST_PFDI_CONFIG": str(tmp_path / "pfdi.pack"),
            "TEST_PFDI_SRC": str(tmp_path / "pfdi"),
        },
    )

    assert result.returncode == 0, result.stderr
    assert f"<APOLLO_LINUX_SOURCE_DIR={tmp_path / 'linux'}>" in result.stdout
    assert "LINUX_OVERRIDE_SRCDIR" not in result.stdout


def test_apollo_perf_package_uses_isolated_output_and_license() -> None:
    package = PERF_PACKAGE.read_text(encoding="utf-8")
    package_config = PERF_CONFIG.read_text(encoding="utf-8")
    external_config = BUILDROOT_EXTERNAL_CONFIG.read_text(encoding="utf-8")

    assert "BR2_PACKAGE_APOLLO_PERF" in package_config
    assert "package/apollo-perf/Config.in" in external_config
    assert "APOLLO_PERF_LICENSE = GPL-2.0" in package
    assert "APOLLO_PERF_LICENSE_FILES = COPYING" in package
    assert "-C $(APOLLO_LINUX_SOURCE_DIR)/tools/perf" in package
    assert "APOLLO_PERF_OUTPUT = $(@D)/perf-output" in package
    assert "O=$(APOLLO_PERF_OUTPUT)/" in package
    assert "PYTHONDONTWRITEBYTECODE=1" in package
    assert "DESTDIR=$(TARGET_DIR)" in package
    assert "prefix=/usr" in package
    assert "SITE_METHOD = local" not in package
    assert "$(eval $(generic-package))" in package


def test_perf_source_change_invalidates_only_perf_package(
    tmp_path: Path,
) -> None:
    linux = tmp_path / "linux"
    perf_source = linux / "tools/perf/perf.c"
    perf_source.parent.mkdir(parents=True)
    perf_source.write_text("one\n", encoding="utf-8")
    (linux / "COPYING").write_text("GPL-2.0\n", encoding="utf-8")
    subprocess.run(
        ("git", "init", "-q", str(linux)),
        check=True,
    )
    subprocess.run(
        ("git", "-C", str(linux), "add", "."),
        check=True,
    )
    subprocess.run(
        (
            "git",
            "-C",
            str(linux),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "fixture",
        ),
        check=True,
    )
    marker = tmp_path / "buildroot/.apollo-perf-source.manifest"
    command = """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh
LINUX_SRC="${TEST_LINUX_SRC}"
BUILDROOT_BUILD_DIR="${TEST_BUILDROOT_BUILD}"
run_logged() {
    local label="$1"
    shift
    printf '%s' "${label}"
    printf ' <%s>' "$@"
    printf '\\n'
    "$@"
}
buildroot_make() {
    printf 'make-target <%s>\\n' "$1"
}
refresh_buildroot_perf_source
"""
    env = {
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        "TEST_BUILDROOT_BUILD": str(marker.parent),
        "TEST_LINUX_SRC": str(linux),
    }

    first = run_buildroot_function(command, env)
    assert first.returncode == 0, first.stderr
    assert "make-target <apollo-perf-dirclean>" in first.stdout
    first_manifest = marker.read_text(encoding="utf-8")

    second = run_buildroot_function(command, env)
    assert second.returncode == 0, second.stderr
    assert "make-target" not in second.stdout

    perf_source.write_text("two\n", encoding="utf-8")
    third = run_buildroot_function(command, env)
    assert third.returncode == 0, third.stderr
    assert "make-target <apollo-perf-dirclean>" in third.stdout
    assert marker.read_text(encoding="utf-8") != first_manifest

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]


def test_rootfs_module_copy_is_stripped_before_signing(tmp_path: Path) -> None:
    # Given: an isolated Buildroot overlay and a captured command runner.
    command = """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh

kernel_release() { printf 'test-release\\n'; }
kernel_modules_overlay_manifest() { printf 'manifest\\n'; }
validate_zena_kernel_modules_overlay() { :; }
run_logged()
{
    local label="$1"
    shift
    printf '%s' "${label}"
    printf ' <%s>' "$@"
    printf '\\n'
    if [[ "${label}" == linux-modules-install ]]; then
        mkdir -p "${BUILDROOT_OVERLAY}/lib/modules/test-release"
    fi
}

KERNEL_MODULES_AUTOLOAD=bridge
install_kernel_modules_overlay
"""

    # When: the rootfs module overlay installation is requested.
    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        check=False,
        env={
            **os.environ,
            "AARCH64_PREFIX": "aarch64-test-",
            "APOLLO_KERNEL_MODULES_REFRESH": "1",
            "LINUX_SRC": str(tmp_path / "linux"),
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: modules_install strips only its installed module copies.
    assert result.returncode == 0, result.stderr
    install_lines = [
        line
        for line in result.stdout.splitlines()
        if line.startswith("linux-modules-install ")
    ]
    assert len(install_lines) == 1
    assert "<INSTALL_MOD_STRIP=1>" in install_lines[0]


def test_external_rootfs_module_copy_is_stripped_before_signing(
    tmp_path: Path,
) -> None:
    # Given: a built external module and captured strip/sign operations.
    source_dir = tmp_path / "external-source"
    source_dir.mkdir()
    (source_dir / "fixture.ko").write_bytes(b"module-with-debug-info")
    command = """
set -euo pipefail
source scripts/build/local_build_common.sh
source scripts/build/modules/build_buildroot.sh

run_logged()
{
    local label="$1"
    shift
    printf '%s' "${label}"
    printf ' <%s>' "$@"
    printf '\\n'
}
sign_kernel_module() { printf 'sign <%s>\\n' "$1"; }
require_command() { :; }

build_external_kernel_module fixture \
    "${FIXTURE_SOURCE}" "${FIXTURE_BUILD}" fixture test-release
"""

    # When: the external module is installed into the rootfs overlay.
    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        check=False,
        env={
            **os.environ,
            "AARCH64_PREFIX": "aarch64-test-",
            "FIXTURE_BUILD": str(tmp_path / "external-build"),
            "FIXTURE_SOURCE": str(source_dir),
            "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: only the installed copy is stripped and it is signed afterwards.
    assert result.returncode == 0, result.stderr
    installed = (
        tmp_path
        / "local-build/work/buildroot-overlay/lib/modules/test-release/updates"
        / "fixture.ko"
    )
    operations = [
        line
        for line in result.stdout.splitlines()
        if line.startswith(("strip-fixture.ko ", "sign "))
    ]
    assert operations == [
        f"strip-fixture.ko <aarch64-test-strip> <--strip-debug> <{installed}>",
        f"sign <{installed}>",
    ]

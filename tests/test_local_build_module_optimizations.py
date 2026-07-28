from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
import subprocess
from textwrap import dedent
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]


def run_bash(script: str, env: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("bash", "-c", script),
        cwd=ROOT,
        check=False,
        env=os.environ | env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_fake_make(path: Path) -> None:
    path.write_text(
        dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail

            printf 'CALL' >> "${MAKE_ARGS_LOG}"
            printf '\\t%s' "$@" >> "${MAKE_ARGS_LOG}"
            printf '\\n' >> "${MAKE_ARGS_LOG}"

            build_dir=""
            tfa_build=0
            for arg in "$@"; do
                case "${arg}" in
                    O=*) build_dir="${arg#O=}" ;;
                    BUILD_BASE=*)
                        build_dir="${arg#BUILD_BASE=}"
                        tfa_build=1
                        ;;
                esac
            done

            if [[ " $* " == *" Image "* ]]; then
                mkdir -p "${build_dir}/arch/arm64/boot"
                printf 'image\\n' > "${build_dir}/arch/arm64/boot/Image"
            fi
            for arg in "$@"; do
                case "${arg}" in
                    *.dtb)
                        mkdir -p "${build_dir}/arch/arm64/boot/dts/$(dirname "${arg}")"
                        printf 'dtb\\n' > "${build_dir}/arch/arm64/boot/dts/${arg}"
                        ;;
                esac
            done
            if [[ "${tfa_build}" -eq 1 ]]; then
                mkdir -p "${build_dir}/apollo_qvp/debug"
                printf 'bl2\\n' > "${build_dir}/apollo_qvp/debug/bl2.bin"
                printf 'fip\\n' > "${build_dir}/apollo_qvp/debug/fip.bin"
            fi
            """
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def make_calls(path: Path) -> list[list[str]]:
    return [
        line.split("\t")[1:]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("CALL\t")
    ]


def make_jobs(call: list[str]) -> str | None:
    for index, argument in enumerate(call):
        if argument == "-j":
            return call[index + 1]
        if argument.startswith("-j"):
            return argument.removeprefix("-j")
    return None


def test_linux_config_and_selected_dtb_share_minimal_make_invocations(
    tmp_path: Path,
) -> None:
    # Given: a forced local Linux config refresh and one selected DTB.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    write_fake_make(fake_bin / "make")
    linux_src = tmp_path / "linux"
    linux_src.mkdir()
    linux_config = tmp_path / "linux.config"
    linux_config.write_text("CONFIG_MODULES=y\n", encoding="utf-8")
    make_args_log = tmp_path / "linux-make-args.tsv"
    env = {
        "AARCH64_PREFIX": "aarch64-test-",
        "APOLLO_LINUX_FORCE_CONFIG": "1",
        "BOOT_DIR": str(tmp_path / "deploy" / "boot"),
        "JOBS": "7",
        "KERNEL_DEBUG_INFO": "0",
        "KERNEL_DEVICETREE": "arm/apollo-qvp.dtb",
        "LINUX_BUILD_DIR": str(tmp_path / "work" / "linux"),
        "LINUX_CONFIG": str(linux_config),
        "LINUX_DEFCONFIG": "apollo_qvp_defconfig",
        "LINUX_SRC": str(linux_src),
        "LOCAL_MACHINE_WORK_PREFIX": "apollo_qvp",
        "LOCAL_BUILD_DTB_BASENAME": "apollo-qvp.dtb",
        "MAKE_ARGS_LOG": str(make_args_log),
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "YOCTO_TMP": str(tmp_path / "yocto-tmp"),
    }

    # When: the real build_linux function runs against a recording make.
    result = run_bash(
        dedent(
            """\
            set -euo pipefail
            APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
            require_dir() { [[ -d "$1" ]]; }
            require_file() { [[ -f "$1" ]]; }
            local_build_kbuild_ccache_args() { local -n out="$1"; out=(); }
            fingerprint_file_hash() { sha256sum "$1"; }
            write_file_if_changed() { cat > "$1"; }
            copy_file_if_changed() { cp "$1" "$2"; chmod "$3" "$2"; }
            run_logged() { shift; "$@"; }
            install_artifact() { mkdir -p "$(dirname "$2")"; cp "$1" "$2"; }
            log() { printf '%s\\n' "$*"; }
            die() { printf 'error: %s\\n' "$*" >&2; return 1; }
            source scripts/build/modules/build_linux.sh
            build_linux
            """
        ),
        env,
    )

    # Then: config normalization and all consumed kernel outputs take two calls.
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    calls = make_calls(make_args_log)
    assert len(calls) == 2
    assert sum("olddefconfig" in call for call in calls) == 1
    build_call = next(call for call in calls if "Image" in call)
    assert "modules" in build_call
    assert "arm/apollo-qvp.dtb" in build_call
    assert "dtbs" not in build_call
    assert make_jobs(build_call) == "7"


def test_tfa_build_uses_configured_parallel_jobs(tmp_path: Path) -> None:
    # Given: a stale TF-A build and seven configured local-build jobs.
    tfa_build_dir = tmp_path / "work" / "trusted-firmware-a"
    tfa_src = tmp_path / "trusted-firmware-a"
    tfa_src.mkdir()
    deploy_dir = tmp_path / "deploy"
    (deploy_dir / "u-boot").mkdir(parents=True)
    (deploy_dir / "optee").mkdir()
    (deploy_dir / "u-boot" / "u-boot.bin").write_bytes(b"u-boot\n")
    (deploy_dir / "optee" / "tee-pager_v2.bin").write_bytes(b"optee\n")
    recipe_native = (
        tmp_path
        / "yocto-tmp"
        / "work"
        / "apollo_qvp-poky-linux"
        / "trusted-firmware-a"
        / "1.0"
        / "recipe-sysroot-native"
        / "usr"
        / "bin"
    )
    recipe_native.mkdir(parents=True)
    write_fake_make(recipe_native / "make")
    (
        recipe_native.parent
        / "lib"
        / "python3.13"
        / "site-packages"
    ).mkdir(parents=True)
    make_args_log = tmp_path / "tfa-make-args.tsv"
    env = {
        "AARCH64_PREFIX": "aarch64-test-",
        "DEPLOY_DIR": str(deploy_dir),
        "FW_DIR": str(deploy_dir / "firmware"),
        "JOBS": "7",
        "LOCAL_MACHINE_WORK_PREFIX": "apollo_qvp",
        "MAKE_ARGS_LOG": str(make_args_log),
        "NR_IMAGES_PER_FWU_BANK": "5",
        "PC_CPUS_COUNT": "4",
        "PFDI_MONITOR_SUPPORT": "1",
        "PFDI_SUPPORT": "1",
        "TFA_BUILD_DIR": str(tfa_build_dir),
        "TFA_LINUX_DTS": "1",
        "TFA_PLATFORM_BUILD_DIR": str(tfa_build_dir / "apollo_qvp"),
        "TFA_SRC": str(tfa_src),
        "TF_A_PLATFORM": "apollo_qvp",
        "VARIANT": "cfg2",
        "YOCTO_TMP": str(tmp_path / "yocto-tmp"),
    }

    # When: the real build_tfa function runs against a recording make.
    result = run_bash(
        dedent(
            """\
            set -euo pipefail
            APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
            require_dir() { [[ -d "$1" ]]; }
            require_file() { [[ -f "$1" ]]; }
            first_existing_glob() {
                local candidate
                for candidate in $1; do
                    [[ -e "${candidate}" ]] || continue
                    printf '%s\\n' "${candidate}"
                    return 0
                done
                return 1
            }
            local_build_ccache_manifest() { printf 'ccache=disabled\\n'; }
            fingerprint_file_hash() { sha256sum "$1"; }
            canonical_dir() { realpath "$1"; }
            local_build_tfa_ccache_args() { local -n out="$1"; out=(); }
            path_prepend() { PATH="$1:${PATH}"; export PATH; }
            run_logged() { shift; "$@"; }
            install_artifact() { mkdir -p "$(dirname "$2")"; cp "$1" "$2"; }
            log() { printf '%s\\n' "$*"; }
            die() { printf 'error: %s\\n' "$*" >&2; return 1; }
            source scripts/build/modules/build_tfa.sh
            build_tfa
            """
        ),
        env,
    )

    # Then: TF-A receives the shared job count while retaining both targets.
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    calls = make_calls(make_args_log)
    assert len(calls) == 1
    assert make_jobs(calls[0]) == "7"
    assert "--jobserver-style=pipe" in calls[0]
    assert "bl2" in calls[0]
    assert "fip" in calls[0]
    assert (deploy_dir / "firmware" / "bl2.bin").read_bytes() == b"bl2\n"
    assert (deploy_dir / "firmware" / "fip.bin").read_bytes() == b"fip\n"

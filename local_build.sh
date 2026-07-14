#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${ROOT_DIR}/scripts/build/local_build_common.sh"
source "${ROOT_DIR}/scripts/build/modules/build_qbox.sh"
source "${ROOT_DIR}/scripts/build/modules/build_sdk.sh"
source "${ROOT_DIR}/scripts/build/modules/build_tfm.sh"
source "${ROOT_DIR}/scripts/build/modules/build_scp.sh"
source "${ROOT_DIR}/scripts/build/modules/build_zephyr.sh"
source "${ROOT_DIR}/scripts/build/modules/build_optee.sh"
source "${ROOT_DIR}/scripts/build/modules/build_uboot.sh"
source "${ROOT_DIR}/scripts/build/modules/build_tfa.sh"
source "${ROOT_DIR}/scripts/build/modules/build_linux.sh"
source "${ROOT_DIR}/scripts/build/modules/build_buildroot.sh"
source "${ROOT_DIR}/scripts/build/modules/build_flash_images.sh"
source "${ROOT_DIR}/scripts/build/modules/build_boot_disk.sh"
source "${ROOT_DIR}/scripts/build/modules/build_fvpconf.sh"
source "${ROOT_DIR}/scripts/build/modules/build_debug_manifest.sh"
source "${ROOT_DIR}/scripts/build/modules/package_fvp_local.sh"

COMPONENTS=(qbox tf-m scp-firmware zephyr optee u-boot tf-a linux buildroot flash-images boot-disk fvpconf debug-manifest)
ACTIONS=(build clean clean-build defconfig menuconfig savedefconfig)
KCONFIG_COMPONENTS=(u-boot linux zephyr)

DRY_RUN=0
CCACHE_REPORT_ONLY=0
REFRESH_SDK=0
PACKAGE_MODE=auto
ACTION=build
JOBS_ARG="${JOBS}"
SELECTED_COMPONENTS=()
ACTION_SET=0
COMPONENT_SET=0

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

contains_word()
{
    local needle="$1"
    shift
    local item
    for item in "$@"; do
        [[ "${item}" == "${needle}" ]] && return 0
    done
    return 1
}

usage()
{
    cat <<EOF
Usage: ./local_build.sh [OPTIONS] [COMPONENT ...] [ACTION]

Build the Apollo local component set and generated QBox boot artifacts.

Components:
  qbox tf-m scp-firmware zephyr optee u-boot tf-a linux
  buildroot flash-images boot-disk fvpconf debug-manifest

Actions:
  build clean clean-build defconfig menuconfig savedefconfig

Options:
  --component NAME     select a component; may be repeated
  --action ACTION      action for selected components (default: build)
  --qbox-unit-tests    run qbox-platform unit tests after qbox build
  --qbox-systemc-tests alias for --qbox-unit-tests
  --package           package local FVP deploy output; package-only if no component is selected
  --no-package        skip the default package step
  --refresh-sdk       force-populate and reinstall the Yocto SDK; SDK-only if no component is selected
  --jobs N            parallel build jobs (default: ${JOBS})
  --dry-run           print resolved actions without changing files
  --ccache-report     print ccache status for every component and exit
  APOLLO_LOCAL_BUILD_CCACHE=0 disables ccache; default is auto-detect
  QBOX_CMAKE_BUILD_TYPE overrides QBox type; default is RelWithDebInfo
  -h, --help          show this help

Examples:
  ./local_build.sh
  ./local_build.sh qbox
  ./local_build.sh qbox --qbox-unit-tests
  ./local_build.sh qbox debug-manifest --no-package
  ./local_build.sh --qbox-unit-tests
  ./local_build.sh linux clean-build --no-package
  ./local_build.sh linux menuconfig --no-package
  ./local_build.sh --refresh-sdk
  ./local_build.sh --package
  ./local_build.sh --dry-run
EOF
}

add_component()
{
    local component="$1"
    contains_word "${component}" "${COMPONENTS[@]}" ||
        die "unsupported component for ./local_build.sh: ${component}"
    SELECTED_COMPONENTS+=("${component}")
    COMPONENT_SET=1
}

set_action()
{
    local action="$1"
    contains_word "${action}" "${ACTIONS[@]}" ||
        die "unsupported action for ./local_build.sh: ${action}"
    ACTION="${action}"
    ACTION_SET=1
}

parse_args()
{
    while (($# > 0)); do
        case "$1" in
            --component)
                (($# >= 2)) || die "--component requires a value"
                add_component "$2"
                shift 2
                ;;
            --action)
                (($# >= 2)) || die "--action requires a value"
                set_action "$2"
                shift 2
                ;;
            --qbox-unit-tests|--qbox-systemc-tests)
                QBOX_RUN_UNIT_TESTS=1
                QBOX_RUN_SYSTEMC_COMPONENT_TESTS=1
                if [[ "${COMPONENT_SET}" == 0 ]]; then
                    add_component qbox
                fi
                shift
                ;;
            --package)
                [[ "${PACKAGE_MODE}" != "disabled" ]] ||
                    die "--package and --no-package are mutually exclusive"
                PACKAGE_MODE=enabled
                shift
                ;;
            --no-package)
                [[ "${PACKAGE_MODE}" != "enabled" ]] ||
                    die "--package and --no-package are mutually exclusive"
                PACKAGE_MODE=disabled
                shift
                ;;
            --refresh-sdk)
                REFRESH_SDK=1
                shift
                ;;
            --jobs)
                (($# >= 2)) || die "--jobs requires a value"
                [[ "$2" =~ ^[1-9][0-9]*$ ]] || die "--jobs must be a positive integer"
                JOBS_ARG="$2"
                JOBS="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            --ccache-report)
                CCACHE_REPORT_ONLY=1
                shift
                ;;
            -h|--help|help)
                usage
                exit 0
                ;;
            --*)
                die "unknown option: $1"
                ;;
            *)
                if contains_word "$1" "${COMPONENTS[@]}"; then
                    add_component "$1"
                elif contains_word "$1" "${ACTIONS[@]}"; then
                    [[ "${ACTION_SET}" == 0 ]] || die "multiple actions requested"
                    set_action "$1"
                elif [[ "${COMPONENT_SET}" == 1 ]]; then
                    die "unsupported action for ./local_build.sh: $1"
                else
                    die "unsupported component for ./local_build.sh: $1"
                fi
                shift
                ;;
        esac
    done
}

validate_action_component()
{
    local component="$1"
    local action="$2"
    if contains_word "${action}" defconfig menuconfig savedefconfig &&
        ! contains_word "${component}" "${KCONFIG_COMPONENTS[@]}"; then
        die "unsupported action for component ${component}: ${action}"
    fi
}

component_function()
{
    case "$1" in
        tf-m) printf 'build_tfm\n' ;;
        qbox) printf 'build_qbox\n' ;;
        scp-firmware) printf 'build_scp\n' ;;
        zephyr) printf 'build_zephyr\n' ;;
        optee) printf 'build_optee\n' ;;
        u-boot) printf 'build_uboot\n' ;;
        tf-a) printf 'build_tfa\n' ;;
        linux) printf 'build_linux\n' ;;
        buildroot) printf 'build_buildroot_initramfs\n' ;;
        flash-images) printf 'package_flash_images\n' ;;
        boot-disk) printf 'create_boot_disk\n' ;;
        fvpconf) printf 'create_fvpconf\n' ;;
        debug-manifest) printf 'generate_debug_manifest\n' ;;
        *) return 1 ;;
    esac
}

component_work_dir()
{
    case "$1" in
        tf-m) printf '%s\n' "${TFM_BUILD_DIR}" ;;
        qbox) printf '%s\n' "${QBOX_PLATFORM_BUILD_DIR}" ;;
        scp-firmware) printf '%s\n' "${SCP_BUILD_DIR}" ;;
        zephyr) printf '%s\n' "${ZEPHYR_BUILD_DIR}" ;;
        optee) printf '%s\n' "${OPTEE_BUILD_DIR}" ;;
        u-boot) printf '%s\n' "${UBOOT_BUILD_DIR}" ;;
        tf-a) printf '%s\n' "${TFA_BUILD_DIR}" ;;
        linux) printf '%s\n' "${LINUX_BUILD_DIR}" ;;
        buildroot) printf '%s\n' "${BUILDROOT_BUILD_DIR}" ;;
        flash-images) printf '%s\n' "${SIGN_DIR}" ;;
        boot-disk) printf '%s\n' "${BOOT_DIR}" ;;
        fvpconf) printf '%s\n' "${DEPLOY_DIR}/${MACHINE}-local.fvpconf" ;;
        debug-manifest) printf '%s\n' "${LOCAL_BUILD_DIR}/debug" ;;
        *) return 1 ;;
    esac
}

component_ccache_method()
{
    case "$1" in
        qbox) printf 'CMake C/CXX compiler launcher\n' ;;
        tf-m) printf 'CMake C/CXX compiler launcher\n' ;;
        scp-firmware) printf 'CMake C/CXX compiler launcher\n' ;;
        zephyr) printf 'CMake C/CXX compiler launcher\n' ;;
        optee) printf 'OP-TEE CCcore/CCldelf/CCta_arm64 overrides\n' ;;
        u-boot) printf 'Kbuild CC and HOSTCC overrides\n' ;;
        tf-a) printf 'TF-A CC and HOSTCC overrides\n' ;;
        linux) printf 'Kbuild CC and HOSTCC overrides\n' ;;
        buildroot) printf 'Buildroot external toolchain wrappers\n' ;;
        flash-images|boot-disk|fvpconf|debug-manifest) printf 'generated artifact step; no compiler cache\n' ;;
        *) return 1 ;;
    esac
}

print_ccache_report()
{
    local ccache_bin=""
    local status="disabled"
    local detail
    local component

    if local_build_ccache_disabled; then
        detail="APOLLO_LOCAL_BUILD_CCACHE=${APOLLO_LOCAL_BUILD_CCACHE:-auto}"
    elif local_build_ccache_resolve ccache_bin; then
        status="enabled"
        detail="${ccache_bin}"
    else
        detail="ccache not found; build continues without compiler cache"
    fi

    printf 'ccache\n'
    printf '  mode %s\n' "${APOLLO_LOCAL_BUILD_CCACHE:-auto}"
    printf '  status %s\n' "${status}"
    printf '  detail %s\n' "${detail}"
    printf 'ccache component usage\n'
    for component in "${COMPONENTS[@]}"; do
        if [[ "${status}" == enabled ]]; then
            printf '  %-13s yes  %s\n' "${component}" "$(component_ccache_method "${component}")"
        else
            printf '  %-13s no   %s\n' "${component}" "${detail}"
        fi
    done
    if [[ -n "${CCACHE_DIR:-}" ]]; then
        printf '  %-13s %s\n' "cache-dir" "${CCACHE_DIR}"
    fi
}

print_component_dry_run()
{
    local component="$1"
    local action="$2"
    printf '  %s: %s\n' "${component}" "${action}"
    case "${action}" in
        build)
            printf '    function: %s\n' "$(component_function "${component}")"
            case "${component}" in
                tf-m)
                    printf '    cmake: -DTFM_PLATFORM=%s -DCROSS_COMPILE=%s\n' \
                        "${TFM_PLATFORM}" \
                        "${ARM_NONE_EABI_PREFIX%-}"
                    ;;
                qbox)
                    printf '    cmake: -S %s -B %s\n' \
                        "${QBOX_PLATFORM_DIR#"${ROOT_DIR}"/}" \
                        "${QBOX_PLATFORM_BUILD_DIR#"${ROOT_DIR}"/}"
                    printf '    qbox core: %s\n' \
                        "${QBOX_CORE_DIR#"${ROOT_DIR}"/}"
                    printf '    target: %s\n' "${QBOX_APOLLO_BUILD_TARGET:-apollo_fvp_full_system}"
                    if [[ "${QBOX_RUN_UNIT_TESTS:-0}" == 1 ||
                        "${QBOX_RUN_SYSTEMC_COMPONENT_TESTS:-0}" == 1 ]]; then
                        printf '    test target: qbox_platform_systemc_component_tests\n'
                        printf '    ctest: -L qbox-platform-systemc-components\n'
                    fi
                    ;;
                scp-firmware)
                    printf '    cmake: -DCMAKE_SYSTEM_NAME=Generic -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY\n'
                    printf '    note: SCP cross-compile IPO executable probe is skipped; benign executable-link fallback is documented\n'
                    ;;
                tf-a)
                    printf '    note: requires existing local U-Boot and OP-TEE artifacts\n'
                    printf '    inputs: %s %s\n' "${DEPLOY_DIR}/u-boot/u-boot.bin" "${DEPLOY_DIR}/optee/tee-pager_v2.bin"
                    ;;
                buildroot)
                    printf '    output: %s\n' "${BOOT_DIR}/initramfs.cpio.gz"
                    printf '    work: %s\n' "${BUILDROOT_BUILD_DIR#"${ROOT_DIR}"/}"
                    ;;
                flash-images)
                    printf '    outputs: %s %s %s\n' \
                        "${FW_DIR}/rse-rom-image.img" \
                        "${FW_DIR}/rse-flash-image.img" \
                        "${FW_DIR}/ap-flash-image.img"
                    ;;
                boot-disk)
                    validate_local_build_file_under_dir "boot disk" "${LOCAL_BUILD_BOOT_DISK}" "${BOOT_DIR}"
                    printf '    outputs: %s %s\n' \
                        "${LOCAL_BUILD_BOOT_DISK}" \
                        "${BOOT_DIR}/boot-fat.img"
                    ;;
                fvpconf)
                    printf '    output: %s\n' "${DEPLOY_DIR}/${MACHINE}-local.fvpconf"
                    ;;
                debug-manifest)
                    printf '    output: %s\n' "${LOCAL_BUILD_DIR}/debug/symbols.json"
                    ;;
            esac
            ;;
        clean)
            printf '    remove work: %s\n' "$(component_work_dir "${component}")"
            case "${component}" in
                linux)
                    printf '    remove deploy: %s %s\n' "${BOOT_DIR}/Image" "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}"
                    ;;
                qbox)
                    printf '    remove qbox platform build directory\n'
                    return 0
                    ;;
                boot-disk)
                    validate_local_build_file_under_dir "boot disk" "${LOCAL_BUILD_BOOT_DISK}" "${BOOT_DIR}"
                    validate_local_build_file_under_dir "legacy boot disk" "${LOCAL_BUILD_LEGACY_BOOT_DISK}" "${BOOT_DIR}"
                    printf '    remove local deploy outputs for %s only\n' "${component}"
                    ;;
                tf-m|scp-firmware|zephyr|optee|u-boot|tf-a|buildroot|flash-images|fvpconf|debug-manifest)
                    printf '    remove local deploy outputs for %s only\n' "${component}"
                    ;;
            esac
            printf '    invalidate package manifests: %s %s\n' \
                "${DEPLOY_DIR}/local-package-manifest.json" \
                "${FW_DIR}/.apollo-flash-images.manifest"
            ;;
        clean-build)
            print_component_dry_run "${component}" clean
            print_component_dry_run "${component}" build
            ;;
        defconfig|menuconfig|savedefconfig)
            case "${component}" in
                u-boot)
                    printf '    command: make -C %s O=%s ARCH=arm CROSS_COMPILE=%s RD_ASPEN_VARIANT=%s %s %s\n' \
                        "${UBOOT_SRC#"${ROOT_DIR}"/}" "${UBOOT_BUILD_DIR#"${ROOT_DIR}"/}" "${AARCH64_PREFIX}" "${RD_ASPEN_VARIANT}" "${UBOOT_MACHINE}" "${action}"
                    ;;
                linux)
                    printf '    command: make -C %s O=%s ARCH=arm64 CROSS_COMPILE=%s %s\n' \
                        "${LINUX_SRC#"${ROOT_DIR}"/}" "${LINUX_BUILD_DIR#"${ROOT_DIR}"/}" "${AARCH64_PREFIX}" "${action}"
                    ;;
                zephyr)
                    printf '    command: cmake -S %s -B %s && cmake --build %s --target %s\n' \
                        "${ZEPHYR_SAFETY_ISLAND_SRC#"${ROOT_DIR}"/}/apps/sample" \
                        "${ZEPHYR_BUILD_DIR#"${ROOT_DIR}"/}" "${ZEPHYR_BUILD_DIR#"${ROOT_DIR}"/}" "${action}"
                    printf '    generated defconfig: %s/zephyr/defconfig\n' "${ZEPHYR_BUILD_DIR#"${ROOT_DIR}"/}"
                    ;;
            esac
            ;;
    esac
}

dry_run()
{
    local order="${SELECTED_COMPONENTS[*]}"
    if ((REFRESH_SDK)); then
        order="sdk-refresh${order:+ ${order}}"
    fi
    cat <<EOF
DRY-RUN: ./local_build.sh
jobs: ${JOBS_ARG}
pc cpus: ${PC_CPUS_COUNT}
tfa linux dts: ${TFA_LINUX_DTS}
bootargs tail: ${BOOTLOADER_LINUX_APPEND}
order: ${order}$([[ "${PACKAGE_MODE}" != disabled ]] && printf ' package')
component steps:
EOF
    if ((REFRESH_SDK)); then
        printf '  sdk-refresh: force populate and reinstall\n'
        printf '    command: bitbake nexios-image -c populate_sdk -f\n'
        printf '    install: %s\n' "${SDK_DIR}"
        printf '    warning: Yocto SDK generation can take a long time\n'
    fi
    local component
    for component in "${SELECTED_COMPONENTS[@]}"; do
        print_component_dry_run "${component}" "${ACTION}"
    done
    if [[ "${PACKAGE_MODE}" != disabled ]]; then
        printf '  package: local FVP deploy\n'
        printf '    function: package_flash_images then package_local_fvp_outputs\n'
    fi
}

SDK_INSTALL_CHECKED=0
SDK_ENV_READY=0

ensure_yocto_sdk_installed()
{
    if [[ "${SDK_INSTALL_CHECKED}" == 1 ]]; then
        return 0
    fi

    shopt -s nullglob
    local env_files=("${SDK_DIR}"/environment-setup-*)
    shopt -u nullglob

    if ((${#env_files[@]} == 0)); then
        log "WARNING: Yocto SDK not found under ${SDK_DIR}; local_build.sh will populate and install it automatically."
        log "WARNING: Running bitbake nexios-image -c populate_sdk can take a long time."
        build_sdk
    else
        log "Yocto SDK already installed at ${SDK_DIR}"
    fi
    SDK_INSTALL_CHECKED=1
}

ensure_sdk_available()
{
    if [[ "${SDK_ENV_READY}" == 1 ]]; then
        return 0
    fi
    ensure_yocto_sdk_installed
    setup_build_environment
    SDK_ENV_READY=1
}

needs_initial_sdk_check()
{
    ((${#SELECTED_COMPONENTS[@]} > 0)) || return 1

    case "${ACTION}" in
        build|clean-build) return 0 ;;
        defconfig|menuconfig|savedefconfig)
            local component
            for component in "${SELECTED_COMPONENTS[@]}"; do
                [[ "${component}" == zephyr ]] && continue
                return 0
            done
            ;;
    esac
    return 1
}

run_clean()
{
    local component="$1"
    local work_dir
    work_dir="$(component_work_dir "${component}")"

    [[ ! -L "${LOCAL_BUILD_DIR}" ]] ||
        die "refusing to clean through local build root symlink: ${LOCAL_BUILD_DIR}"
    [[ ! -L "${WORK_DIR}" ]] ||
        die "refusing to clean through work root symlink: ${WORK_DIR}"
    [[ ! -L "${work_dir}" ]] ||
        die "refusing to clean component work symlink: ${work_dir}"
    case "${component}" in
        buildroot)
            rm -rf "${BUILDROOT_BUILD_DIR}" "${BUILDROOT_EXTERNAL}" \
                "${BUILDROOT_OVERLAY}" "${BUILDROOT_TOOLCHAIN_DIR}" \
                "${WORK_DIR}/pfdi-local-agent"
            validate_local_build_write_dir "boot dir" "${BOOT_DIR}"
            rm -f "${BOOT_DIR}/initramfs.cpio.gz"
            return 0
            ;;
        flash-images)
            rm -rf "${SIGN_DIR}"
            validate_local_build_write_dir "firmware dir" "${FW_DIR}"
            rm -f "${FW_DIR}/rse-rom-image.img" \
                "${FW_DIR}/rse-flash-image.img" \
                "${FW_DIR}/rse-otp-image.img" \
                "${FW_DIR}/ap-flash-image.img" \
                "${FW_DIR}/init_fwu_metadata.bin" \
                "${FW_DIR}/.apollo-flash-images.manifest"
            return 0
            ;;
        boot-disk)
            validate_local_build_write_dir "boot dir" "${BOOT_DIR}"
            validate_local_build_file_under_dir "boot disk" "${LOCAL_BUILD_BOOT_DISK}" "${BOOT_DIR}"
            validate_local_build_file_under_dir "legacy boot disk" "${LOCAL_BUILD_LEGACY_BOOT_DISK}" "${BOOT_DIR}"
            rm -f "${BOOT_DIR}/boot.cmd" \
                "${BOOT_DIR}/boot.scr" \
                "${BOOT_DIR}/boot-fat.img" \
                "${LOCAL_BUILD_BOOT_DISK}" \
                "${LOCAL_BUILD_LEGACY_BOOT_DISK}"
            return 0
            ;;
        fvpconf)
            validate_local_build_write_dir "deploy root" "${DEPLOY_DIR}"
            rm -f "${DEPLOY_DIR}/${MACHINE}-local.fvpconf" \
                "${DEPLOY_DIR}/apollo-fvp-local.fvpconf"
            return 0
            ;;
        debug-manifest)
            rm -rf "${LOCAL_BUILD_DIR}/debug"
            return 0
            ;;
    esac
    if [[ "${component}" == qbox ]]; then
        local work_root_real
        local work_dir_parent_real
        case "${work_dir}" in
            "${WORK_DIR}"/*) ;;
            *) die "refusing to clean qbox build outside work root: ${work_dir}" ;;
        esac
        mkdir -p "${WORK_DIR}" "$(dirname "${work_dir}")"
        work_root_real="$(canonical_dir "${WORK_DIR}")"
        work_dir_parent_real="$(canonical_dir "$(dirname "${work_dir}")")"
        case "${work_dir_parent_real}/$(basename "${work_dir}")" in
            "${work_root_real}"/*) ;;
            *) die "refusing to clean qbox build outside work root: ${work_dir}" ;;
        esac
        rm -rf "${work_dir}"
        return 0
    fi
    if [[ -d "${WORK_DIR}" && -d "${work_dir}" ]]; then
        local work_root_real
        local work_dir_real
        work_root_real="$(canonical_dir "${WORK_DIR}")"
        work_dir_real="$(canonical_dir "${work_dir}")"
        case "${work_dir_real}" in
            "${work_root_real}"/*) ;;
            *) die "refusing to clean component work outside work root: ${work_dir}" ;;
        esac
    fi

    rm -rf "${work_dir}"
    validate_local_build_write_dir "deploy root" "${DEPLOY_DIR}"
    validate_local_build_write_dir "firmware dir" "${FW_DIR}"
    case "${component}" in
        linux)
            validate_local_build_write_dir "boot dir" "${BOOT_DIR}"
            rm -f "${BOOT_DIR}/Image" "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}"
            ;;
    esac
    rm -f "${DEPLOY_DIR}/local-package-manifest.json" \
        "${FW_DIR}/.apollo-flash-images.manifest"
}

run_kconfig()
{
    local component="$1"
    local action="$2"
    case "${component}" in
        zephyr)
            [[ -n "${ZEPHYR_SDK_INSTALL_DIR:-}" && -d "${ZEPHYR_SDK_INSTALL_DIR}" ]] ||
                die "ZEPHYR_SDK_INSTALL_DIR is required for Zephyr ${action}; build or unpack zephyr-demos-cl1 with Yocto first."
            ;;
        *)
            ensure_sdk_available
            ;;
    esac
    case "${component}" in
        u-boot)
            mkdir -p "${UBOOT_BUILD_DIR}"
            local uboot_ccache_args=()
            local_build_kbuild_ccache_args uboot_ccache_args "${AARCH64_PREFIX}"
            make -C "${UBOOT_SRC}" O="${UBOOT_BUILD_DIR}" ARCH=arm \
                CROSS_COMPILE="${AARCH64_PREFIX}" "${uboot_ccache_args[@]}" \
                "${action}"
            ;;
        linux)
            mkdir -p "${LINUX_BUILD_DIR}"
            local linux_ccache_args=()
            local_build_kbuild_ccache_args linux_ccache_args "${AARCH64_PREFIX}"
            make -C "${LINUX_SRC}" O="${LINUX_BUILD_DIR}" ARCH=arm64 \
                CROSS_COMPILE="${AARCH64_PREFIX}" "${linux_ccache_args[@]}" \
                "${action}"
            ;;
        zephyr)
            cmake --build "${ZEPHYR_BUILD_DIR}" --target "${action}"
            [[ "${action}" != savedefconfig ]] ||
                printf 'generated defconfig: %s/zephyr/defconfig\n' "${ZEPHYR_BUILD_DIR}"
            ;;
    esac
}

run_component()
{
    local component="$1"
    local action="$2"
    local fn
    case "${action}" in
        build)
            fn="$(component_function "${component}")"
            if [[ "${component}" != qbox ]]; then
                ensure_sdk_available
            fi
            "${fn}"
            ;;
        clean)
            run_clean "${component}"
            ;;
        clean-build)
            run_clean "${component}"
            fn="$(component_function "${component}")"
            if [[ "${component}" != qbox ]]; then
                ensure_sdk_available
            fi
            "${fn}"
            ;;
        defconfig|menuconfig|savedefconfig)
            run_kconfig "${component}" "${action}"
            ;;
    esac
}

parse_args "$@"

if [[ "${APOLLO_LOCAL_BUILD_USE_YOCTO_VARS:-1}" != 0 &&
    -f "${APOLLO_LOCAL_BUILD_YOCTO_VARS}" ]]; then
    python3 - "${APOLLO_LOCAL_BUILD_YOCTO_VARS}" <<'PY'
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

cache = Path(sys.argv[1])
raw = json.loads(cache.read_text(encoding="utf-8"))
for entry in raw.get("config_paths", {}).values():
    path = Path(str(entry.get("path", "")))
    expected = entry.get("sha256")
    if not expected or not path.is_file():
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        print(
            f"error: stale config hash for {path}; "
            "refresh Yocto local-build vars or set APOLLO_LOCAL_BUILD_USE_YOCTO_VARS=0",
            file=sys.stderr,
        )
        raise SystemExit(1)
PY
fi

if [[ "${COMPONENT_SET}" == 0 ]]; then
    if [[ "${PACKAGE_MODE}" == enabled || "${REFRESH_SDK}" == 1 ]]; then
        SELECTED_COMPONENTS=()
    else
        SELECTED_COMPONENTS=("${COMPONENTS[@]}")
    fi
fi

if [[ "${PACKAGE_MODE}" == auto ]]; then
    PACKAGE_MODE=disabled
fi

for component in "${SELECTED_COMPONENTS[@]}"; do
    validate_action_component "${component}" "${ACTION}"
done

if [[ "${QBOX_RUN_UNIT_TESTS:-0}" == 1 ||
    "${QBOX_RUN_SYSTEMC_COMPONENT_TESTS:-0}" == 1 ]]; then
    contains_word qbox "${SELECTED_COMPONENTS[@]}" ||
        die "--qbox-unit-tests requires the qbox component"
    [[ "${ACTION}" == build || "${ACTION}" == clean-build ]] ||
        die "--qbox-unit-tests requires qbox build or clean-build"
fi

if [[ "${ACTION}" == build && "${APOLLO_LOCAL_BUILD_USE_YOCTO_VARS:-1}" == 0 &&
    "${TFM_PLATFORM:-}" == missing/* ]]; then
    die "TFM_PLATFORM ${TFM_PLATFORM} is unresolved; refresh trusted-firmware-m Yocto variables."
fi

if ((CCACHE_REPORT_ONLY)); then
    print_ccache_report
    exit 0
fi

if ((DRY_RUN)); then
    dry_run
    exit 0
fi

if ((REFRESH_SDK)); then
    run_step "sdk-refresh" refresh_sdk
    SDK_INSTALL_CHECKED=1
elif needs_initial_sdk_check; then
    run_step "sdk-check" ensure_yocto_sdk_installed
fi

print_ccache_report

for component in "${SELECTED_COMPONENTS[@]}"; do
    run_step "${component}-${ACTION}" run_component "${component}" "${ACTION}"
done

if [[ "${PACKAGE_MODE}" == enabled ]]; then
    run_step "package" package_local_fvp_outputs
fi

print_local_build_timing_summary

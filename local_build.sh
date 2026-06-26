#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${ROOT_DIR}/scripts/build/local_build_common.sh"
source "${ROOT_DIR}/scripts/build/modules/build_sdk.sh"
source "${ROOT_DIR}/scripts/build/modules/build_tfm.sh"
source "${ROOT_DIR}/scripts/build/modules/build_scp.sh"
source "${ROOT_DIR}/scripts/build/modules/build_zephyr.sh"
source "${ROOT_DIR}/scripts/build/modules/build_optee.sh"
source "${ROOT_DIR}/scripts/build/modules/build_uboot.sh"
source "${ROOT_DIR}/scripts/build/modules/build_tfa.sh"
source "${ROOT_DIR}/scripts/build/modules/build_linux.sh"
source "${ROOT_DIR}/scripts/build/modules/build_flash_images.sh"
source "${ROOT_DIR}/scripts/build/modules/package_fvp_local.sh"

COMPONENTS=(tf-m scp-firmware zephyr optee u-boot tf-a linux)
ACTIONS=(build clean clean-build defconfig menuconfig savedefconfig)
KCONFIG_COMPONENTS=(u-boot linux zephyr)

DRY_RUN=0
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

Build and package the Apollo FVP local component set.

Components:
  tf-m scp-firmware zephyr optee u-boot tf-a linux

Actions:
  build clean clean-build defconfig menuconfig savedefconfig

Options:
  --component NAME     select a component; may be repeated
  --action ACTION      action for selected components (default: build)
  --package           package local FVP deploy output; package-only if no component is selected
  --no-package        skip the default package step
  --jobs N            parallel build jobs (default: ${JOBS})
  --dry-run           print resolved actions without changing files
  -h, --help          show this help

Examples:
  ./local_build.sh
  ./local_build.sh linux clean-build --no-package
  ./local_build.sh linux menuconfig --no-package
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
        scp-firmware) printf 'build_scp\n' ;;
        zephyr) printf 'build_zephyr\n' ;;
        optee) printf 'build_optee\n' ;;
        u-boot) printf 'build_uboot\n' ;;
        tf-a) printf 'build_tfa\n' ;;
        linux) printf 'build_linux\n' ;;
        *) return 1 ;;
    esac
}

component_work_dir()
{
    case "$1" in
        tf-m) printf '%s\n' "${TFM_BUILD_DIR}" ;;
        scp-firmware) printf '%s\n' "${SCP_BUILD_DIR}" ;;
        zephyr) printf '%s\n' "${ZEPHYR_BUILD_DIR}" ;;
        optee) printf '%s\n' "${OPTEE_BUILD_DIR}" ;;
        u-boot) printf '%s\n' "${UBOOT_BUILD_DIR}" ;;
        tf-a) printf '%s\n' "${TFA_BUILD_DIR}" ;;
        linux) printf '%s\n' "${LINUX_BUILD_DIR}" ;;
        *) return 1 ;;
    esac
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
                        "${TFM_PLATFORM:-arm/rse/automotive_rd/apollo-fvp}" \
                        "${ARM_NONE_EABI_PREFIX%-}"
                    ;;
                scp-firmware)
                    printf '    cmake: -DCMAKE_SYSTEM_NAME=Generic -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY\n'
                    printf '    note: SCP cross-compile IPO executable probe is skipped; benign executable-link fallback is documented\n'
                    ;;
                tf-a)
                    printf '    note: requires existing local U-Boot and OP-TEE artifacts\n'
                    printf '    inputs: %s %s\n' "${DEPLOY_DIR}/u-boot/u-boot.bin" "${DEPLOY_DIR}/optee/tee-pager_v2.bin"
                    ;;
            esac
            ;;
        clean)
            printf '    remove work: %s\n' "$(component_work_dir "${component}")"
            case "${component}" in
                linux)
                    printf '    remove deploy: %s %s\n' "${BOOT_DIR}/Image" "${BOOT_DIR}/apollo-fvp.dtb"
                    ;;
                tf-m|scp-firmware|zephyr|optee|u-boot|tf-a)
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
                    printf '    command: make -C %s O=%s ARCH=arm CROSS_COMPILE=%s RD_ASPEN_VARIANT=%s apollo_fvp_defconfig %s\n' \
                        "${UBOOT_SRC#${ROOT_DIR}/}" "${UBOOT_BUILD_DIR#${ROOT_DIR}/}" "${AARCH64_PREFIX}" "${RD_ASPEN_VARIANT}" "${action}"
                    ;;
                linux)
                    printf '    command: make -C %s O=%s ARCH=arm64 CROSS_COMPILE=%s %s\n' \
                        "${LINUX_SRC#${ROOT_DIR}/}" "${LINUX_BUILD_DIR#${ROOT_DIR}/}" "${AARCH64_PREFIX}" "${action}"
                    ;;
                zephyr)
                    printf '    command: cmake -S %s -B %s && cmake --build %s --target %s\n' \
                        "${ZEPHYR_SAFETY_ISLAND_SRC#${ROOT_DIR}/}/apps/sample" \
                        "${ZEPHYR_BUILD_DIR#${ROOT_DIR}/}" "${ZEPHYR_BUILD_DIR#${ROOT_DIR}/}" "${action}"
                    printf '    generated defconfig: %s/zephyr/defconfig\n' "${ZEPHYR_BUILD_DIR#${ROOT_DIR}/}"
                    ;;
            esac
            ;;
    esac
}

dry_run()
{
    cat <<EOF
DRY-RUN: ./local_build.sh
jobs: ${JOBS_ARG}
order: ${SELECTED_COMPONENTS[*]}$([[ "${PACKAGE_MODE}" != disabled ]] && printf ' package')
component steps:
EOF
    local component
    for component in "${SELECTED_COMPONENTS[@]}"; do
        print_component_dry_run "${component}" "${ACTION}"
    done
    if [[ "${PACKAGE_MODE}" != disabled ]]; then
        printf '  package: local FVP deploy\n'
        printf '    function: package_flash_images then package_local_fvp_outputs\n'
    fi
}

ensure_sdk_available()
{
    shopt -s nullglob
    local env_files=("${SDK_DIR}"/environment-setup-*)
    shopt -u nullglob

    if ((${#env_files[@]} == 0)); then
        log "WARNING: Yocto SDK not found under ${SDK_DIR}; local_build.sh will populate and install it automatically."
        log "WARNING: Running bitbake nexios-image -c populate_sdk can take a long time."
        build_sdk
    fi

    setup_build_environment
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
            rm -f "${BOOT_DIR}/Image" "${BOOT_DIR}/apollo-fvp.dtb"
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
            make -C "${UBOOT_SRC}" O="${UBOOT_BUILD_DIR}" ARCH=arm \
                CROSS_COMPILE="${AARCH64_PREFIX}" "${action}"
            ;;
        linux)
            mkdir -p "${LINUX_BUILD_DIR}"
            make -C "${LINUX_SRC}" O="${LINUX_BUILD_DIR}" ARCH=arm64 \
                CROSS_COMPILE="${AARCH64_PREFIX}" "${action}"
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
            ensure_sdk_available
            fn="$(component_function "${component}")"
            "${fn}"
            ;;
        clean)
            run_clean "${component}"
            ;;
        clean-build)
            run_clean "${component}"
            ensure_sdk_available
            fn="$(component_function "${component}")"
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
    if [[ "${PACKAGE_MODE}" == enabled ]]; then
        SELECTED_COMPONENTS=()
    else
        SELECTED_COMPONENTS=("${COMPONENTS[@]}")
    fi
fi

if [[ "${PACKAGE_MODE}" == auto ]]; then
    PACKAGE_MODE=enabled
fi

for component in "${SELECTED_COMPONENTS[@]}"; do
    validate_action_component "${component}" "${ACTION}"
done

if [[ "${ACTION}" == build && "${APOLLO_LOCAL_BUILD_USE_YOCTO_VARS:-1}" == 0 &&
    "${TFM_PLATFORM:-}" == missing/* ]]; then
    die "TFM_PLATFORM ${TFM_PLATFORM} is unresolved; refresh trusted-firmware-m Yocto variables."
fi

if ((DRY_RUN)); then
    dry_run
    exit 0
fi

for component in "${SELECTED_COMPONENTS[@]}"; do
    run_step "${component}-${ACTION}" run_component "${component}" "${ACTION}"
done

if [[ "${PACKAGE_MODE}" == enabled ]]; then
    run_step "package" package_local_fvp_outputs
fi

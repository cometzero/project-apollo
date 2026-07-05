#!/usr/bin/env bash
# shellcheck disable=SC2034

set -euo pipefail

APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
LOCAL_BUILD_SCRIPT_DIR="${LOCAL_BUILD_SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
LOCAL_BUILD_MODULE_DIR="${LOCAL_BUILD_MODULE_DIR:-${LOCAL_BUILD_SCRIPT_DIR}/modules}"
ROOT_DIR="${ROOT_DIR:-$(cd "${LOCAL_BUILD_SCRIPT_DIR}/../.." && pwd)}"
APOLLO_LOCAL_BUILD_USE_YOCTO_VARS="${APOLLO_LOCAL_BUILD_USE_YOCTO_VARS:-1}"
APOLLO_LOCAL_BUILD_YOCTO_VARS="${APOLLO_LOCAL_BUILD_YOCTO_VARS:-${ROOT_DIR}/build/local-apollo-fvp/yocto-local-build-vars.json}"
if [[ "${APOLLO_LOCAL_BUILD_YOCTO_VARS}" != /* ]]; then
    APOLLO_LOCAL_BUILD_YOCTO_VARS="${ROOT_DIR}/${APOLLO_LOCAL_BUILD_YOCTO_VARS}"
fi

apollo_local_build_help_requested()
{
    case "${1:-}" in
        -h|--help|help) return 0 ;;
        *) return 1 ;;
    esac
}

apollo_local_build_generate_yocto_vars()
{
    local output="$1"
    local collector="${ROOT_DIR}/scripts/build/collect_yocto_local_build_vars.py"

    [[ -f "${collector}" ]] ||
        return 1
    command -v python3 >/dev/null 2>&1 ||
        return 1
    python3 "${collector}" --output "${output}" >/dev/null
}

apollo_local_build_apply_default()
{
    local name="$1"
    local value="$2"

    case "${name}" in
        MACHINE|RD_ASPEN_VARIANT|PC_CPUS_COUNT|LINUX_DEFCONFIG|BOOTLOADER_LINUX_APPEND|OPTEE_PLATFORM) ;;
        *) return 0 ;;
    esac
    if [[ -z "${!name+x}" ]]; then
        printf -v "${name}" '%s' "${value}"
    fi
}

apollo_local_build_load_yocto_vars()
{
    local cache="${APOLLO_LOCAL_BUILD_YOCTO_VARS}"
    local assignments line name value

    [[ "${APOLLO_LOCAL_BUILD_USE_YOCTO_VARS}" != "0" ]] || return 0
    apollo_local_build_help_requested "${1:-}" && return 0
    if [[ ! -f "${cache}" ]]; then
        apollo_local_build_generate_yocto_vars "${cache}" ||
            return 1
    fi

    if ! assignments="$(
        python3 - "${cache}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final


SCHEMA_VERSION: Final = 1
MAPPINGS: Final = (
    ("MACHINE", "nexios-image", "MACHINE"),
    ("RD_ASPEN_VARIANT", "nexios-image", "RD_ASPEN_VARIANT"),
    ("PC_CPUS_COUNT", "nexios-image", "PC_CPUS_COUNT_DEFAULT"),
    ("LINUX_DEFCONFIG", "linux-yocto-rt", "KBUILD_DEFCONFIG"),
    ("BOOTLOADER_LINUX_APPEND", "nexios-image", "BOOTLOADER_LINUX_APPEND"),
    ("OPTEE_PLATFORM", "optee-os", "PLATFORM"),
)


def fail(message: str) -> None:
    print(f"error: {Path(sys.argv[1])}: {message}", file=sys.stderr)
    raise SystemExit(1)


try:
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
except OSError as exc:
    fail(str(exc))
except json.JSONDecodeError as exc:
    fail(f"invalid JSON: {exc.msg}")

if not isinstance(raw, dict):
    fail("top-level JSON value must be an object")
if raw.get("schema_version") != SCHEMA_VERSION:
    fail(f"schema_version must be {SCHEMA_VERSION}")
recipes = raw.get("recipes")
if not isinstance(recipes, dict):
    fail("missing recipes object")

for local_name, recipe, bitbake_name in MAPPINGS:
    entry = recipes.get(recipe)
    if entry is None:
        continue
    if not isinstance(entry, dict):
        fail(f"{recipe}: recipe entry must be an object")
    variables = entry.get("variables")
    if not isinstance(variables, dict):
        fail(f"{recipe}: missing variables object")
    value = str(variables.get(bitbake_name, "")).strip()
    if value:
        print(f"{local_name}={value}")
PY
    )"; then
        return 1
    fi
    [[ -n "${assignments}" ]] ||
        return 0
    while IFS= read -r line; do
        name="${line%%=*}"
        value="${line#*=}"
        apollo_local_build_apply_default "${name}" "${value}"
    done <<< "${assignments}"
}

if ! apollo_local_build_load_yocto_vars "${1:-}"; then
    printf 'error: could not load Yocto local-build vars from %s with APOLLO_LOCAL_BUILD_USE_YOCTO_VARS=1\n' \
        "${APOLLO_LOCAL_BUILD_YOCTO_VARS}" >&2
    printf 'error: set APOLLO_LOCAL_BUILD_USE_YOCTO_VARS=0 to use built-in local-build defaults intentionally\n' >&2
    return 1 2>/dev/null || exit 1
fi
MACHINE="${MACHINE:-apollo-fvp}"
RD_ASPEN_VARIANT="${RD_ASPEN_VARIANT:-cfg2}"
VARIANT="${VARIANT:-${RD_ASPEN_VARIANT}}"
JOBS="${JOBS:-}"
HOST_PATH="${HOST_PATH:-${PATH}}"

YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
YOCTO_TMP="${YOCTO_TMP:-${YOCTO_BUILD_DIR}/tmp_baremetal}"
YOCTO_DEPLOY_DIR="${YOCTO_DEPLOY_DIR:-${YOCTO_TMP}/deploy/images/${MACHINE}}"

SDK_DIR="${SDK_DIR:-${YOCTO_BUILD_DIR}/local-sdk}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${YOCTO_BUILD_DIR}/local-${MACHINE}}"
WORK_DIR="${LOCAL_BUILD_DIR}/work"
DEPLOY_DIR="${LOCAL_BUILD_DIR}/deploy"
LOG_DIR="${LOCAL_BUILD_DIR}/logs"
QBOX_CORE_DIR="${QBOX_CORE_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox}"
QBOX_PLATFORM_DIR="${QBOX_PLATFORM_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox-platform}"
QBOX_QEMU_DIR="${QBOX_QEMU_DIR:-${ROOT_DIR}/hsoc-stack/tools/qemu}"
if [[ -n "${QBOX_PLATFORM_BUILD_DIR:-}" ]]; then
    :
elif [[ -n "${QBOX_BUILD_DIR:-}" ]]; then
    QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
else
    QBOX_PLATFORM_BUILD_DIR="${WORK_DIR}/qbox-platform"
fi
QBOX_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR}"

TFM_SRC="${TFM_SRC:-${ROOT_DIR}/hsoc-stack/components/system_mgmt/trusted-firmware-m}"
SCP_SRC="${SCP_SRC:-${ROOT_DIR}/hsoc-stack/components/system_mgmt/scp-firmware}"
ZEPHYRPROJECT_SRC="${ZEPHYRPROJECT_SRC:-${ROOT_DIR}/hsoc-stack/components/system_mgmt/zephyrproject}"
ZEPHYR_SAFETY_ISLAND_SRC="${ZEPHYR_SAFETY_ISLAND_SRC:-${ROOT_DIR}/arm-zena-css/components/safety_island/zephyr/src}"
ZEPHYR_HSOC_SRC="${ZEPHYR_HSOC_SRC:-${ZEPHYRPROJECT_SRC}/zephyr_hsoc_src}"
ZEPHYR_MODULES_LIST="${ZEPHYR_MODULES_LIST:-${ZEPHYRPROJECT_SRC}/apollo-modules.list}"
ZEPHYR_DEPS_SRC="${ZEPHYR_DEPS_SRC:-}"
TFA_SRC="${TFA_SRC:-${ROOT_DIR}/hsoc-stack/components/primary_compute/trusted-firmware-a}"
OPTEE_SRC="${OPTEE_SRC:-${ROOT_DIR}/hsoc-stack/components/primary_compute/optee_os}"
UBOOT_SRC="${UBOOT_SRC:-${ROOT_DIR}/hsoc-stack/components/primary_compute/u-boot}"
LINUX_SRC="${LINUX_SRC:-${ROOT_DIR}/hsoc-stack/components/primary_compute/linux}"
LINUX_DEFCONFIG="${LINUX_DEFCONFIG:-apollo_fvp_defconfig}"
BUILDROOT_SRC="${BUILDROOT_SRC:-${ROOT_DIR}/hsoc-stack/components/primary_compute/buildroot}"
ARM_SI_RPROC_SRC="${ARM_SI_RPROC_SRC:-${ROOT_DIR}/sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src}"
RPMSG_NET_SRC="${RPMSG_NET_SRC:-${ROOT_DIR}/sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src}"
PFDI_MISC_SRC="${PFDI_MISC_SRC:-${ROOT_DIR}/sw-ref-stack/components/primary_compute/linux_drivers/pfdi_misc_mod/src}"
PFDI_LOCAL_AGENT_SRC="${PFDI_LOCAL_AGENT_SRC:-${ROOT_DIR}/tools/pfdi-local-agent/pfdi-local-agent.c}"

AARCH64_PREFIX="${AARCH64_PREFIX:-aarch64-poky-linux-}"
ARM_NONE_EABI_PREFIX="${ARM_NONE_EABI_PREFIX:-arm-none-eabi-}"
AARCH64_NONE_ELF_PREFIX="${AARCH64_NONE_ELF_PREFIX:-aarch64-none-elf-}"
AARCH64_ZEPHYR_ELF_PREFIX="${AARCH64_ZEPHYR_ELF_PREFIX:-aarch64-zephyr-elf-}"

PC_CPUS_COUNT="${PC_CPUS_COUNT:-16}"
TFA_LINUX_DTS="${TFA_LINUX_DTS:-1}"
BOOTLOADER_LINUX_APPEND="${BOOTLOADER_LINUX_APPEND:-cpuidle.governor=menu maxcpus=${PC_CPUS_COUNT} mem=4064M}"
LOCAL_BUILD_BOOTARGS_PREFIX="${LOCAL_BUILD_BOOTARGS_PREFIX:-console=ttyAMA0,115200 earlycon=pl011,0x1A400000 root=/dev/ram0 rw rdinit=/init loglevel=7}"
LOCAL_BUILD_BOOTARGS="${LOCAL_BUILD_BOOTARGS:-${LOCAL_BUILD_BOOTARGS_PREFIX}${BOOTLOADER_LINUX_APPEND:+ ${BOOTLOADER_LINUX_APPEND}}}"
OPTEE_PLATFORM="${OPTEE_PLATFORM:-automotive_rd-rdaspen}"
NR_IMAGES_PER_FWU_BANK="${NR_IMAGES_PER_FWU_BANK:-5}"
PFDI_SUPPORT="${PFDI_SUPPORT:-1}"
PFDI_MONITOR_SUPPORT="${PFDI_MONITOR_SUPPORT:-1}"
KERNEL_MODULES_AUTOLOAD="${KERNEL_MODULES_AUTOLOAD:-bridge openvswitch virtio_rpmsg_bus rpmsg_net arm_si_rproc pfdi_misc}"
KERNEL_DEBUG_INFO="${KERNEL_DEBUG_INFO:-1}"

TFM_BUILD_DIR="${WORK_DIR}/trusted-firmware-m"
SCP_BUILD_DIR="${WORK_DIR}/scp-firmware"
ZEPHYR_BUILD_DIR="${WORK_DIR}/zephyr-demos-cl1"
UBOOT_BUILD_DIR="${WORK_DIR}/u-boot"
OPTEE_BUILD_DIR="${WORK_DIR}/optee-os"
TFA_BUILD_DIR="${WORK_DIR}/trusted-firmware-a"
LINUX_BUILD_DIR="${WORK_DIR}/linux"
BUILDROOT_BUILD_DIR="${WORK_DIR}/buildroot"
BUILDROOT_EXTERNAL="${WORK_DIR}/buildroot-external"
BUILDROOT_OVERLAY="${WORK_DIR}/buildroot-overlay"
BUILDROOT_TOOLCHAIN_DIR="${WORK_DIR}/buildroot-toolchain"
BUILDROOT_TOOLCHAIN_SYSROOT="${BUILDROOT_TOOLCHAIN_DIR}/sysroot"
ARM_SI_RPROC_BUILD_DIR="${WORK_DIR}/arm-si-rproc-mod"
RPMSG_NET_BUILD_DIR="${WORK_DIR}/rpmsg-net-mod"
PFDI_MISC_BUILD_DIR="${WORK_DIR}/pfdi-misc-mod"
PFDI_LOCAL_AGENT_BUILD_DIR="${WORK_DIR}/pfdi-local-agent"
SIGN_DIR="${WORK_DIR}/signing"
FW_DIR="${DEPLOY_DIR}/firmware"
BOOT_DIR="${DEPLOY_DIR}/boot"

TFM_BL2_IMAGE_GUID="4b312051-850a-5b17-a3cf-2995baa4bed4"
TFM_RUNTIME_IMAGE_GUID="b181e748-c362-55e6-852c-662d1544f414"
SCP_FIRMWARE_IMAGE_GUID="771ceff3-f186-5d56-80cb-15a2a06dfe81"
AP_FIP_IMAGE_GUID="5d904717-0904-53cd-b240-df7c91ef4918"
SAFETY_ISLAND_CL1_IMAGE_GUID="46083fc9-3d43-5766-a583-ae8e0a199a85"
PRIVATE_METADATA_GUID="07cf7b93-3ce2-52cc-af43-5b0f8690ba73"
FWU_METADATA_GUID="8a7a84a0-8387-40f6-ab41-a8b9a5a60d23"

log()
{
    printf '[%(%Y-%m-%d %H:%M:%S)T] %s\n' -1 "$*"
}

timer_now()
{
    printf '%(%s)T\n' -1
}

format_elapsed()
{
    local elapsed="$1"
    printf '%02d:%02d:%02d' \
        $((elapsed / 3600)) \
        $(((elapsed % 3600) / 60)) \
        $((elapsed % 60))
}

local_build_ccache_disabled()
{
    case "${APOLLO_LOCAL_BUILD_CCACHE:-auto}" in
        0|false|FALSE|no|NO|off|OFF|disable|disabled|DISABLED)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

local_build_ccache_required()
{
    case "${APOLLO_LOCAL_BUILD_CCACHE:-auto}" in
        1|true|TRUE|yes|YES|on|ON|enable|enabled|ENABLED|required|REQUIRED)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

local_build_ccache_bin()
{
    local resolved

    local_build_ccache_resolve resolved || return 1
    printf '%s\n' "${resolved}"
}

local_build_ccache_resolve()
{
    local -n out="$1"
    local tool="${APOLLO_LOCAL_BUILD_CCACHE_BIN:-ccache}"
    local resolved

    out=""
    local_build_ccache_disabled && return 1
    if resolved="$(command -v "${tool}" 2>/dev/null)"; then
        out="${resolved}"
        return 0
    fi
    if local_build_ccache_required; then
        die "APOLLO_LOCAL_BUILD_CCACHE=${APOLLO_LOCAL_BUILD_CCACHE} but ccache was not found: ${tool}"
    fi
    return 1
}

local_build_ccache_manifest()
{
    local tool="${APOLLO_LOCAL_BUILD_CCACHE_BIN:-ccache}"
    local resolved

    printf 'APOLLO_LOCAL_BUILD_CCACHE=%s\n' "${APOLLO_LOCAL_BUILD_CCACHE:-auto}"
    printf 'APOLLO_LOCAL_BUILD_CCACHE_BIN=%s\n' "${tool}"
    if local_build_ccache_disabled; then
        printf 'CCACHE_STATUS=disabled\n'
    elif resolved="$(command -v "${tool}" 2>/dev/null)"; then
        printf 'CCACHE_STATUS=enabled\n'
        printf 'CCACHE_RESOLVED=%s\n' "${resolved}"
    else
        if local_build_ccache_required; then
            die "APOLLO_LOCAL_BUILD_CCACHE=${APOLLO_LOCAL_BUILD_CCACHE} but ccache was not found: ${tool}"
        fi
        printf 'CCACHE_STATUS=missing\n'
    fi
}

local_build_ccache_wrap()
{
    local compiler="$1"
    local ccache_bin

    if local_build_ccache_resolve ccache_bin; then
        printf '%s %s\n' "${ccache_bin}" "${compiler}"
    else
        printf '%s\n' "${compiler}"
    fi
}

local_build_cmake_ccache_args()
{
    local -n out="$1"
    local ccache_bin

    out=()
    local_build_ccache_resolve ccache_bin || return 0
    out+=(
        "-DCMAKE_C_COMPILER_LAUNCHER=${ccache_bin}"
        "-DCMAKE_CXX_COMPILER_LAUNCHER=${ccache_bin}"
    )
}

local_build_kbuild_ccache_args()
{
    local -n out="$1"
    local cross_prefix="$2"
    local ccache_bin

    out=()
    local_build_ccache_resolve ccache_bin || return 0
    out+=(
        "CC=${ccache_bin} ${cross_prefix}gcc"
        "HOSTCC=${ccache_bin} gcc"
    )
}

local_build_tfa_ccache_args()
{
    local -n out="$1"

    out=()
    out+=(
        "CC=$(local_build_ccache_wrap "${AARCH64_PREFIX}gcc")"
        "HOSTCC=$(local_build_ccache_wrap gcc)"
    )
}

local_build_optee_ccache_args()
{
    local -n out="$1"
    local ccache_bin

    out=()
    local_build_ccache_resolve ccache_bin || return 0
    out+=(
        "CCcore=${ccache_bin} ${AARCH64_PREFIX}gcc"
        "CCldelf=${ccache_bin} ${AARCH64_PREFIX}gcc"
        "CCta_arm64=${ccache_bin} ${AARCH64_PREFIX}gcc"
    )
}

local_build_timing_report()
{
    printf '%s\n' "${LOCAL_BUILD_TIMING_REPORT:-${LOG_DIR}/local-build-timings.tsv}"
}

local_build_timing_init()
{
    local report

    report="$(local_build_timing_report)"
    mkdir -p "$(dirname "${report}")"
    if [[ "${LOCAL_BUILD_TIMING_INITIALIZED:-0}" != 1 ]]; then
        printf 'kind\tname\tstatus\tseconds\telapsed\tlog\n' > "${report}"
        LOCAL_BUILD_TIMING_INITIALIZED=1
    fi
}

local_build_record_timing()
{
    local kind="$1"
    local name="$2"
    local status="$3"
    local seconds="$4"
    local log_path="${5:-}"
    local report

    local_build_timing_init
    report="$(local_build_timing_report)"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
        "${kind}" "${name}" "${status}" "${seconds}" \
        "$(format_elapsed "${seconds}")" "${log_path}" >> "${report}"
}

print_local_build_timing_summary()
{
    local report

    report="$(local_build_timing_report)"
    [[ -f "${report}" ]] || return 0

    log "Timing report: ${report}"
    awk -F '\t' '
        NR == 1 { next }
        {
            printf "  %-8s %-36s %s exit=%s", $1, $2, $5, $3
            if ($6 != "") {
                printf " log=%s", $6
            }
            printf "\n"
        }
    ' "${report}"
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

usage()
{
    cat <<'EOF'
Usage: ./local_build.sh [OPTIONS] [COMPONENT ...] [ACTION]

Build and package the Apollo FVP local component set.

Components:
  qbox tf-m scp-firmware zephyr optee u-boot tf-a linux

Actions:
  build clean clean-build defconfig menuconfig savedefconfig

Options:
  --qbox-systemc-tests run qbox-platform SystemC component CTests after qbox build
  --package           package local FVP deploy output; package-only if no component is selected
  --no-package        skip the default package step
  --jobs N            parallel build jobs
  --dry-run           print resolved actions without changing files

Useful overrides:
  SDK_DIR=/path/to/sdk LOCAL_BUILD_DIR=/path/to/output QBOX_PLATFORM_BUILD_DIR=/path/to/qbox-platform-build JOBS=16 ./local_build.sh
  QBOX_BUILD_DIR=/path/to/qbox-platform-build ./local_build.sh qbox
  ./local_build.sh qbox --qbox-systemc-tests
  QBOX_CORE_DIR=/path/to/qbox QBOX_PLATFORM_DIR=/path/to/qbox-platform ./local_build.sh qbox
  ZEPHYR_SDK_INSTALL_DIR=/path/to/zephyr-sdk ./local_build.sh zephyr
  ZEPHYR_DEPS_SRC=/path/to/yocto/work/.../sources-unpack/git ./local_build.sh zephyr
  SAFETY_ISLAND_CL1_BIN=/path/to/zephyr-demos-cl1.bin ./local_build.sh
  LINUX_DEFCONFIG=apollo_fvp_defconfig ./local_build.sh linux
  LINUX_CONFIG=/path/to/.config ./local_build.sh linux
  KERNEL_MODULES_AUTOLOAD="bridge virtio_rpmsg_bus rpmsg_net arm_si_rproc pfdi_misc" ./local_build.sh linux
  KERNEL_DEBUG_INFO=0 ./local_build.sh linux
  RSE_OTP_RESET=1 ./local_build.sh
  RSE_OTP_HOST_PROVISION=0 RSE_OTP_RESET=1 ./local_build.sh
EOF
}

run_logged()
{
    local name="$1"
    shift
    mkdir -p "${LOG_DIR}"
    local start
    local end
    local status
    start="$(timer_now)"
    log "Running ${name}; log: ${LOG_DIR}/${name}.log"
    set +e
    "$@" 2>&1 | tee "${LOG_DIR}/${name}.log"
    status="${PIPESTATUS[0]}"
    set -e
    end="$(timer_now)"
    local elapsed="$((end - start))"
    if [[ "${status}" == 0 ]]; then
        log "Completed ${name} in $(format_elapsed "${elapsed}")"
    else
        log "Failed ${name} after $(format_elapsed "${elapsed}") (exit ${status})"
    fi
    local_build_record_timing command "${name}" "${status}" "${elapsed}" \
        "${LOG_DIR}/${name}.log"
    return "${status}"
}

run_step()
{
    local name="$1"
    shift
    local start
    local end
    local status
    start="$(timer_now)"
    log "Starting ${name}"
    set +e
    "$@"
    status="$?"
    set -e
    end="$(timer_now)"
    local elapsed="$((end - start))"
    if [[ "${status}" == 0 ]]; then
        log "Completed ${name} in $(format_elapsed "${elapsed}")"
    else
        log "Failed ${name} after $(format_elapsed "${elapsed}") (exit ${status})"
    fi
    local_build_record_timing step "${name}" "${status}" "${elapsed}"
    return "${status}"
}

write_file_if_changed()
{
    local dst="$1"
    local tmp

    mkdir -p "$(dirname "${dst}")"
    tmp="$(mktemp "${dst}.tmp.XXXXXX")"
    cat > "${tmp}"
    if [[ -f "${dst}" ]] && cmp -s "${tmp}" "${dst}"; then
        rm -f "${tmp}"
    else
        mv "${tmp}" "${dst}"
    fi
}

copy_file_if_changed()
{
    local src="$1"
    local dst="$2"
    local mode="${3:-0644}"

    require_file "${src}"
    mkdir -p "$(dirname "${dst}")"
    if [[ -f "${dst}" ]] && cmp -s "${src}" "${dst}"; then
        chmod "${mode}" "${dst}"
    else
        install -m "${mode}" "${src}" "${dst}"
    fi
}

command_digest()
{
    local arg

    for arg in "$@"; do
        printf '%s\0' "${arg}"
    done | sha256sum | awk '{print $1}'
}

git_tree_manifest()
{
    local root="$1"
    local label="$2"

    [[ -d "${root}/.git" ]] || return 0
    printf '%s-dir=%s\n' "${label}" "$(canonical_dir "${root}")"
    printf '%s-head=' "${label}"
    git -C "${root}" rev-parse HEAD 2>/dev/null || true
    printf '%s-status\n' "${label}"
    git -C "${root}" status --porcelain=v1 --untracked-files=no 2>/dev/null || true
    printf '%s-diff=' "${label}"
    git -C "${root}" diff --no-ext-diff --binary 2>/dev/null |
        sha256sum | awk '{print $1}'
}

cmake_configure_current()
{
    local name="$1"
    local build_dir="$2"
    shift 2
    local marker="${build_dir}/.apollo-${name}.sha256"
    local digest

    [[ "${APOLLO_FORCE_CONFIGURE:-0}" != "1" ]] || return 1
    [[ -f "${build_dir}/CMakeCache.txt" ]] || return 1
    [[ -f "${build_dir}/build.ninja" ]] || return 1
    [[ -f "${marker}" ]] || return 1

    digest="$(command_digest "$@")"
    [[ "$(cat "${marker}")" == "${digest}" ]]
}

run_cmake_configure_if_needed()
{
    local name="$1"
    local build_dir="$2"
    shift 2
    local marker="${build_dir}/.apollo-${name}.sha256"
    local digest

    reset_cmake_build_if_cache_paths_missing "${name}" "${build_dir}"

    digest="$(command_digest "$@")"
    if cmake_configure_current "${name}" "${build_dir}" "$@"; then
        log "${name} is up to date"
        return 0
    fi

    run_logged "${name}" "$@"
    printf '%s\n' "${digest}" > "${marker}"
}

require_file()
{
    [[ -f "$1" ]] || die "missing required file: $1"
}

require_dir()
{
    [[ -d "$1" ]] || die "missing required directory: $1"
}

require_command()
{
    command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

source_local_build_module()
{
    local module="$1"
    local path="${LOCAL_BUILD_MODULE_DIR}/${module}"

    require_file "${path}"
    # shellcheck source=/dev/null
    source "${path}"
}

source_local_build_modules()
{
    local module

    for module in "$@"; do
        source_local_build_module "${module}"
    done
}

canonical_dir()
{
    (cd "$1" && pwd -P)
}

reset_cmake_build_if_source_changed()
{
    local build_dir="$1"
    local source_dir="$2"
    local cache="${build_dir}/CMakeCache.txt"
    local recorded
    local expected

    [[ -f "${cache}" ]] || return 0

    recorded="$(sed -n 's/^CMAKE_HOME_DIRECTORY:INTERNAL=//p' "${cache}" | tail -n 1)"
    [[ -n "${recorded}" ]] || return 0

    expected="$(canonical_dir "${source_dir}")"
    if [[ "${recorded}" != "${expected}" ]]; then
        log "Removing stale CMake build directory for ${build_dir}"
        log "  previous source: ${recorded}"
        log "  current source:  ${expected}"
        rm -rf "${build_dir}"
    fi
}

cmake_cache_missing_tmp_paths()
{
    local cache="$1"
    local name path

    [[ -f "${cache}" ]] || return 0

    while IFS=$'\t' read -r name path; do
        [[ -n "${path}" ]] || continue
        case "${path}" in
            "${YOCTO_BUILD_DIR}"/tmp*|"${ROOT_DIR}"/build/tmp*) ;;
            *) continue ;;
        esac
        [[ -e "${path}" ]] && continue
        printf '%s\t%s\n' "${name}" "${path}"
    done < <(
        awk '
            /^[#/]/ { next }
            /^[^=]+:[^=]+=\// {
                name = $0
                sub(/:.*/, "", name)
                value = $0
                sub(/^[^=]*=/, "", value)
                count = split(value, paths, ";")
                for (i = 1; i <= count; i++) {
                    if (paths[i] ~ /^\//) {
                        print name "\t" paths[i]
                    }
                }
            }
        ' "${cache}"
    )
}

reset_cmake_configure_state()
{
    local name="$1"
    local build_dir="$2"
    local marker="${build_dir}/.apollo-${name}.sha256"

    rm -rf \
        "${build_dir}/CMakeCache.txt" \
        "${build_dir}/CMakeFiles" \
        "${build_dir}/build.ninja" \
        "${build_dir}/compile_commands.json" \
        "${build_dir}/.ninja_deps" \
        "${build_dir}/.ninja_log" \
        "${marker}"
    if [[ -d "${build_dir}" ]]; then
        find "${build_dir}" -name cmake_install.cmake -type f -delete
    fi
}

reset_cmake_build_if_cache_paths_missing()
{
    local name="$1"
    local build_dir="$2"
    local cache="${build_dir}/CMakeCache.txt"
    local missing=()
    local entry
    local shown=0

    [[ -f "${cache}" ]] || return 0
    mapfile -t missing < <(cmake_cache_missing_tmp_paths "${cache}" | sort -u)
    [[ "${#missing[@]}" -gt 0 ]] || return 0

    log "Removing stale CMake configure state for ${name}: ${build_dir}"
    for entry in "${missing[@]}"; do
        [[ "${shown}" -lt 8 ]] || break
        log "  missing cache path: ${entry}"
        shown=$((shown + 1))
    done
    if [[ "${#missing[@]}" -gt "${shown}" ]]; then
        log "  and $((${#missing[@]} - shown)) more missing cache paths"
    fi
    reset_cmake_configure_state "${name}" "${build_dir}"
}


path_prepend()
{
    [[ -d "$1" ]] || return 0
    case ":${PATH}:" in
        *:"$1":*) ;;
        *) PATH="$1:${PATH}" ;;
    esac
}

first_existing_glob()
{
    local pattern="$1"
    local item
    shopt -s nullglob
    for item in ${pattern}; do
        printf '%s\n' "${item}"
        shopt -u nullglob
        return 0
    done
    shopt -u nullglob
    return 1
}


find_first_file()
{
    local root="$1"
    local name="$2"
    [[ -d "${root}" ]] || return 1
    find "${root}" -name "${name}" -type f -print -quit
}

yocto_native_component_roots()
{
    local candidate
    local canonical
    local -A seen=()

    for candidate in \
        "${YOCTO_TMP}/sysroots-components/x86_64" \
        "${YOCTO_BUILD_DIR}/tmp_baremetal-${MACHINE}-no-dm-verity/sysroots-components/x86_64" \
        "${YOCTO_BUILD_DIR}/tmp_baremetal-${MACHINE}-dm-verity/sysroots-components/x86_64"
    do
        [[ -d "${candidate}" ]] || continue
        canonical="$(canonical_dir "${candidate}")"
        [[ -n "${seen[${canonical}]+x}" ]] && continue
        seen["${canonical}"]=1
        printf '%s\n' "${candidate}"
    done

    shopt -s nullglob
    for candidate in "${YOCTO_BUILD_DIR}"/tmp_baremetal-*/sysroots-components/x86_64; do
        [[ -d "${candidate}" ]] || continue
        canonical="$(canonical_dir "${candidate}")"
        [[ -n "${seen[${canonical}]+x}" ]] && continue
        seen["${canonical}"]=1
        printf '%s\n' "${candidate}"
    done
    shopt -u nullglob
}

install_artifact()
{
    local src="$1"
    local dst="$2"
    copy_file_if_changed "${src}" "${dst}" 0644
}

host_cpus()
{
    if [[ -n "${APOLLO_HOST_CPUS:-}" ]]; then
        printf '%s\n' "${APOLLO_HOST_CPUS}"
        return 0
    fi
    nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1
}

host_mem_mib()
{
    local meminfo="${APOLLO_MEMINFO_PATH:-/proc/meminfo}"
    awk '/^MemTotal:/ { print int($2 / 1024); exit }' "${meminfo}" 2>/dev/null || echo 0
}

auto_build_threads()
{
    local cpus mem_mib

    cpus="$(host_cpus)"
    if [[ ! "${cpus}" =~ ^[1-9][0-9]*$ ]]; then
        cpus=1
    fi
    mem_mib="$(host_mem_mib)"
    if [[ ! "${mem_mib}" =~ ^[0-9]+$ ]]; then
        mem_mib=0
    fi

    if [[ "${mem_mib}" -gt 16384 ]]; then
        echo "${cpus}"
    else
        echo 6
    fi
}

JOBS="${JOBS:-$(auto_build_threads)}"

bitbake_network_sandbox_supported()
{
    python3 - <<'PY'
import ctypes
import os
import sys

libc = ctypes.CDLL("libc.so.6")
clone_newuser = 0x10000000
clone_newnet = 0x40000000

ret = libc.unshare(clone_newnet | clone_newuser)
if ret != 0:
    sys.exit(1)

try:
    with open("/proc/self/uid_map", "w", encoding="utf-8") as uid_map:
        uid_map.write(f"{os.getuid()} {os.getuid()} 1")
    with open("/proc/self/setgroups", "w", encoding="utf-8") as setgroups:
        setgroups.write("deny")
    with open("/proc/self/gid_map", "w", encoding="utf-8") as gid_map:
        gid_map.write(f"{os.getgid()} {os.getgid()} 1")
except OSError:
    sys.exit(1)
PY
}

clear_sdk_env_for_yocto()
{
    local var

    export PATH="${HOST_PATH}"
    for var in ${!OECORE_@}; do
        unset "${var}"
    done
    for var in SDKTARGETSYSROOT SDKPATH CONFIG_SITE PKG_CONFIG_SYSROOT_DIR \
        PKG_CONFIG_PATH PKG_CONFIG_LIBDIR OECORE_ACLOCAL_OPTS TARGET_PREFIX \
        CONFIGURE_FLAGS CC CXX CPP LD AR AS STRIP OBJCOPY OBJDUMP READELF \
        NM RANLIB CFLAGS CXXFLAGS CPPFLAGS LDFLAGS KCFLAGS; do
        unset "${var}" 2>/dev/null || true
    done
}

prepare_bitbake_extra_args()
{
    BITBAKE_EXTRA_ARGS=()
    mkdir -p "${YOCTO_BUILD_DIR}/conf"

    if [[ "${APOLLO_AUTO_RESOURCE_LIMITS:-1}" != "0" ||
        -n "${APOLLO_BUILD_THREADS:-}" ||
        -n "${BB_NUMBER_THREADS:-}" ||
        -n "${BB_NUM_THREADS:-}" ||
        -n "${APOLLO_PARALLEL_MAKE:-}" ||
        -n "${PARALLEL_MAKE:-}" ]]; then
        local auto_threads build_threads parallel_make resource_conf

        auto_threads="$(auto_build_threads)"
        build_threads="${APOLLO_BUILD_THREADS:-${BB_NUMBER_THREADS:-${BB_NUM_THREADS:-${auto_threads}}}}"
        parallel_make="${APOLLO_PARALLEL_MAKE:-${PARALLEL_MAKE:--j${auto_threads}}}"
        resource_conf="${YOCTO_BUILD_DIR}/conf/apollo-bitbake-resources.conf"
        {
            echo "#"
            echo "# Generated by local_build.sh."
            echo "# Set APOLLO_AUTO_RESOURCE_LIMITS=0 to use BitBake defaults."
            echo "#"
            echo "BB_NUMBER_THREADS = \"${build_threads}\""
            echo "PARALLEL_MAKE = \"${parallel_make}\""
        } >"${resource_conf}"
        BITBAKE_EXTRA_ARGS+=(-R "${resource_conf}")
        log "Using BitBake resource limits from ${resource_conf}"
        log "BB_NUMBER_THREADS=${build_threads} PARALLEL_MAKE=${parallel_make}"
    fi

    if ! bitbake_network_sandbox_supported; then
        local host_conf

        host_conf="${YOCTO_BUILD_DIR}/conf/apollo-bitbake-host.conf"
        cat >"${host_conf}" <<'EOF'
#
# Generated by local_build.sh for hosts where bitbake-worker cannot write
# /proc/self/uid_map after unshare(CLONE_NEWUSER | CLONE_NEWNET).
#
INHERIT += "apollo-bitbake-network-sandbox"
APOLLO_BITBAKE_DISABLE_NETWORK_SANDBOX = "1"
EOF
        BITBAKE_EXTRA_ARGS+=(-R "${host_conf}")
        log "BitBake worker network sandbox is unsupported; using ${host_conf}"
    fi
}


source_sdk()
{
    local env_file
    env_file="$(first_existing_glob "${SDK_DIR}/environment-setup-*" || true)"
    if [[ -z "${env_file}" ]]; then
        build_sdk
        env_file="$(first_existing_glob "${SDK_DIR}/environment-setup-*" || true)"
    fi
    require_file "${env_file}"

    log "Sourcing SDK environment: ${env_file}"
    set +u
    # shellcheck disable=SC1090
    source "${env_file}"
    set -u

    AARCH64_PREFIX="${TARGET_PREFIX:-${AARCH64_PREFIX}}"
    SDK_NATIVE_SYSROOT="${OECORE_NATIVE_SYSROOT:-}"
    SDK_TARGET_SYSROOT="${SDKTARGETSYSROOT:-}"

    # Component build systems receive explicit cross prefixes. Yocto SDK flags
    # are useful for recipes but can pollute bare-metal CMake projects.
    unset ARCH CROSS_COMPILE
    unset CC CXX CPP LD AR AS STRIP OBJCOPY OBJDUMP READELF NM RANLIB
    unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS

    require_command "${AARCH64_PREFIX}gcc"
}

add_yocto_native_paths()
{
    local native
    local native_roots=()
    local index
    local arm_none
    local aarch64_none

    while IFS= read -r native; do
        native_roots+=("${native}")
    done < <(yocto_native_component_roots)

    for ((index = ${#native_roots[@]} - 1; index >= 0; index--)); do
        native="${native_roots[${index}]}"
        path_prepend "${native}/python3-native/usr/bin"
        path_prepend "${native}/fiptool-native/usr/bin"
        path_prepend "${native}/cot-dt2c-native/usr/bin"
        path_prepend "${native}/efitools-native/usr/bin"

        arm_none="$(find_first_file "${native}/gcc-arm-none-eabi-native" "arm-none-eabi-gcc" || true)"
        [[ -n "${arm_none}" ]] && path_prepend "$(dirname "${arm_none}")"

        aarch64_none="$(find_first_file "${native}/gcc-aarch64-none-elf-native" "aarch64-none-elf-gcc" || true)"
        [[ -n "${aarch64_none}" ]] && path_prepend "$(dirname "${aarch64_none}")"
    done

    return 0
}

setup_build_environment()
{
    source_sdk
    add_yocto_native_paths

    require_command cmake
    require_command ninja
    require_command make
    require_command git
    require_command python3
    require_command openssl
    require_command fiptool
    require_command mkimage
    require_command cert-to-efi-sig-list
    require_command cpio
    require_command gzip
    require_command depmod
    require_command sgdisk
    require_command mkfs.vfat
    require_command mcopy
    require_command "${ARM_NONE_EABI_PREFIX}gcc"
    require_command "${AARCH64_NONE_ELF_PREFIX}gcc"
}

setup_zephyr_build_environment()
{
    add_yocto_native_paths

    require_command cmake
    require_command ninja
    require_command git
    require_command python3
}


fingerprint_tree_metadata()
{
    local root="$1"
    local label="$2"

    [[ -d "${root}" ]] || return 0
    find "${root}" -type f -printf "${label}/%P|%s|%T@\n" | LC_ALL=C sort
}

fingerprint_file_hash()
{
    local path="$1"
    local label="$2"

    [[ -f "${path}" ]] || return 0
    printf '%s|' "${label}"
    sha256sum "${path}"
}


if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    usage
    die "scripts/build/local_build_common.sh is a shared library; run ./local_build.sh or scripts/build/build_*.sh"
fi

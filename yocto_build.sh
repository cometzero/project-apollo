#!/usr/bin/env bash
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POKY_DIR="${WORKSPACE_DIR}/layers/poky"

BUILD_DIR="${BUILD_DIR:-}"
TEMPLATECONF="${TEMPLATECONF:-}"

DEFAULT_APOLLO_MACHINE="apollo-qvp"
DM_VERITY_MODE="${APOLLO_DM_VERITY:-}"
APOLLO_MACHINE="${MACHINE:-${DEFAULT_APOLLO_MACHINE}}"
DRY_RUN=0
KEEP_CONF=0
BSP_ONLY=0

usage() {
    cat <<'EOF'
Usage: ./yocto_build.sh [options]

Build the Apollo Yocto product and BSP validation images.

Options:
  --machine apollo-fvp|apollo-qvp
                          Select the Apollo Yocto machine.
  --bsp                   Build only nexios-bsp-initramfs.
  --keep-conf             Preserve the existing BUILD_DIR/conf directory.
  --dm-verity=on|off      Build through the matching Yocto multiconfig.
  --dm-verity on|off      Same as --dm-verity=on|off.
  --with-dm-verity        Alias for --dm-verity=on.
  --without-dm-verity     Alias for --dm-verity=off.
  --dry-run               Print the BitBake command without running it.
  -h, --help              Show this help.

Environment:
  MACHINE=apollo-fvp|apollo-qvp
                          Select the Apollo Yocto machine.
  BUILD_DIR=PATH          Select the Yocto build directory (default: build).
  APOLLO_DM_VERITY=on|off Select the same multiconfig as --dm-verity.
EOF
}

normalize_machine() {
    local machine="$1"

    case "${machine}" in
        apollo-fvp|apollo-qvp)
            echo "${machine}"
            ;;
        *)
            echo "error: invalid-machine '${machine}' (expected apollo-fvp or apollo-qvp)" >&2
            exit 2
            ;;
    esac
}

normalize_dm_verity_mode() {
    local mode="$1"

    case "${mode}" in
        ""|default)
            echo ""
            ;;
        1|on|true|yes|enabled|enable)
            echo "on"
            ;;
        0|off|false|no|disabled|disable)
            echo "off"
            ;;
        *)
            echo "error: invalid dm-verity mode '${mode}'" >&2
            exit 2
            ;;
    esac
}

while (($#)); do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --machine)
            [[ $# -ge 2 ]] || {
                echo "error: --machine requires apollo-fvp or apollo-qvp" >&2
                exit 2
            }
            APOLLO_MACHINE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --bsp)
            BSP_ONLY=1
            shift
            ;;
        --keep-conf)
            KEEP_CONF=1
            shift
            ;;
        --dm-verity=*)
            DM_VERITY_MODE="${1#*=}"
            shift
            ;;
        --dm-verity)
            [[ $# -ge 2 ]] || {
                echo "error: --dm-verity requires on or off" >&2
                exit 2
            }
            DM_VERITY_MODE="$2"
            shift 2
            ;;
        --with-dm-verity)
            DM_VERITY_MODE="on"
            shift
            ;;
        --without-dm-verity)
            DM_VERITY_MODE="off"
            shift
            ;;
        *)
            echo "error: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

APOLLO_MACHINE="$(normalize_machine "${APOLLO_MACHINE}")"
DM_VERITY_MODE="$(normalize_dm_verity_mode "${DM_VERITY_MODE}")"

if [[ -z "${BUILD_DIR}" ]]; then
    BUILD_DIR="${WORKSPACE_DIR}/build"
fi

if [[ -z "${TEMPLATECONF}" ]]; then
    TEMPLATECONF="${WORKSPACE_DIR}/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/${APOLLO_MACHINE}"
fi

host_cpus() {
    if [[ -n "${APOLLO_HOST_CPUS:-}" ]]; then
        printf '%s\n' "${APOLLO_HOST_CPUS}"
        return 0
    fi
    nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1
}

host_mem_mib() {
    local meminfo="${APOLLO_MEMINFO_PATH:-/proc/meminfo}"
    awk '/^MemTotal:/ { print int($2 / 1024); exit }' "${meminfo}" 2>/dev/null || echo 0
}

auto_build_threads() {
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

deactivate_virtualenv() {
    local virtualenv_bin="${VIRTUAL_ENV:-}"
    local path_entry
    local -a clean_path=() path_entries=()

    [[ -n "${virtualenv_bin}" ]] || return 0
    virtualenv_bin="${virtualenv_bin%/}/bin"
    IFS=: read -r -a path_entries <<<"${PATH}"
    for path_entry in "${path_entries[@]}"; do
        [[ "${path_entry}" == "${virtualenv_bin}" ]] || clean_path+=("${path_entry}")
    done
    PATH="$(IFS=:; printf '%s' "${clean_path[*]}")"
    unset VIRTUAL_ENV
    export PATH
    hash -r
}

if [[ ! -f "${POKY_DIR}/oe-init-build-env" ]]; then
    echo "error: missing ${POKY_DIR}/oe-init-build-env" >&2
    exit 1
fi

if [[ ! -d "${TEMPLATECONF}" ]]; then
    echo "error: missing TEMPLATECONF directory: ${TEMPLATECONF}" >&2
    exit 1
fi

export TEMPLATECONF
export MACHINE="${APOLLO_MACHINE}"
deactivate_virtualenv

if [[ "${KEEP_CONF}" == "1" ]]; then
    echo "notice: preserving existing configuration in ${BUILD_DIR}/conf" >&2
else
    echo "notice: removing ${BUILD_DIR}/conf and recreating it from TEMPLATECONF" >&2
    rm -rf -- "${BUILD_DIR}/conf"
fi

# shellcheck source=/dev/null
set +u
source "${POKY_DIR}/oe-init-build-env" "${BUILD_DIR}"
set -u

BITBAKE_ARGS=()
if [[ "${BSP_ONLY}" == "1" ]]; then
    BITBAKE_TARGETS=("nexios-bsp-initramfs")
else
    BITBAKE_TARGETS=("nexios-bsp-initramfs" "nexios-image")
fi
export APOLLO_BSP_BUILD_ONLY="${BSP_ONLY}"
export BB_ENV_PASSTHROUGH_ADDITIONS="${BB_ENV_PASSTHROUGH_ADDITIONS:-} APOLLO_BSP_BUILD_ONLY"

echo "notice: machine '${APOLLO_MACHINE}' uses shared build directory ${PWD}" >&2

case "${DM_VERITY_MODE}" in
    on)
        DM_VERITY_MC="${APOLLO_MACHINE}-dm-verity"
        ;;
    off)
        DM_VERITY_MC="${APOLLO_MACHINE}-no-dm-verity"
        ;;
    *)
        DM_VERITY_MC=""
        ;;
esac

if [[ -n "${DM_VERITY_MC}" ]]; then
    MULTICONFIG_CONF="${PWD}/conf/apollo-dm-verity-multiconfig.conf"
    {
        echo "#"
        echo "# Generated by yocto_build.sh."
        echo "# Select the Apollo dm-verity Yocto multiconfig."
        echo "#"
        echo "BBMULTICONFIG = \"${DM_VERITY_MC}\""
    } >"${MULTICONFIG_CONF}"
    BITBAKE_ARGS+=(-R "${MULTICONFIG_CONF}")
    for target_index in "${!BITBAKE_TARGETS[@]}"; do
        BITBAKE_TARGETS[${target_index}]="mc:${DM_VERITY_MC}:${BITBAKE_TARGETS[${target_index}]}"
    done
    echo "notice: dm-verity mode '${DM_VERITY_MODE}' uses multiconfig ${DM_VERITY_MC}" >&2
fi

if [[ "${APOLLO_AUTO_RESOURCE_LIMITS:-1}" != "0" ||
    -n "${APOLLO_BUILD_THREADS:-}" ||
    -n "${BB_NUMBER_THREADS:-}" ||
    -n "${BB_NUM_THREADS:-}" ||
    -n "${APOLLO_PARALLEL_MAKE:-}" ||
    -n "${PARALLEL_MAKE:-}" ]]; then
    AUTO_THREADS="$(auto_build_threads)"
    BUILD_THREADS="${APOLLO_BUILD_THREADS:-${BB_NUMBER_THREADS:-${BB_NUM_THREADS:-${AUTO_THREADS}}}}"
    PARALLEL_MAKE_VALUE="${APOLLO_PARALLEL_MAKE:-${PARALLEL_MAKE:--j${AUTO_THREADS}}}"
    RESOURCE_CONF="${PWD}/conf/apollo-bitbake-resources.conf"
    {
        echo "#"
        echo "# Generated by yocto_build.sh."
        echo "# Set APOLLO_AUTO_RESOURCE_LIMITS=0 to use BitBake defaults."
        echo "#"
        echo "BB_NUMBER_THREADS = \"${BUILD_THREADS}\""
        echo "PARALLEL_MAKE = \"${PARALLEL_MAKE_VALUE}\""
    } >"${RESOURCE_CONF}"
    BITBAKE_ARGS+=(-R "${RESOURCE_CONF}")
    echo "notice: using BitBake resource limits from ${RESOURCE_CONF}" >&2
    echo "notice: BB_NUMBER_THREADS=${BUILD_THREADS} PARALLEL_MAKE=${PARALLEL_MAKE_VALUE}" >&2
fi

if [[ "${DRY_RUN}" == "1" ]]; then
    printf 'APOLLO_BSP_BUILD_ONLY=%q\n' "${APOLLO_BSP_BUILD_ONLY}"
    printf 'MACHINE=%q bitbake' "${APOLLO_MACHINE}"
    printf ' %q' "${BITBAKE_ARGS[@]}" "${BITBAKE_TARGETS[@]}"
    printf '\n'
    exit 0
fi

MACHINE="${APOLLO_MACHINE}" \
APOLLO_BSP_BUILD_ONLY="${APOLLO_BSP_BUILD_ONLY}" \
    bitbake "${BITBAKE_ARGS[@]}" "${BITBAKE_TARGETS[@]}"

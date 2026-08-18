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
APOLLO_MACHINE="${MACHINE:-${DEFAULT_APOLLO_MACHINE}}"
DRY_RUN=0
KEEP_CONF=0
BSP_ONLY=0
BITBAKE_TASK=""
REQUESTED_TARGETS=()

usage() {
    cat <<'EOF'
Usage: ./yocto_build.sh [options] [target ...]

Build the Apollo Yocto product and BSP validation images.

Options:
  --machine apollo-fvp|apollo-qvp
                          Select the Apollo Yocto machine.
  --bsp                   Build only nexios-bsp-initramfs.
  -c TASK                 Run a BitBake task for the explicit targets.
  --keep-conf             Preserve the existing BUILD_DIR/conf directory.
  --dry-run               Print the BitBake command without running it.
  -h, --help              Show this help.

Environment:
  MACHINE=apollo-fvp|apollo-qvp
                          Select the Apollo Yocto machine.
  BUILD_DIR=PATH          Select the Yocto build directory (default: build).
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
        -c)
            [[ $# -ge 2 ]] || {
                echo "error: -c requires a BitBake task" >&2
                exit 2
            }
            [[ -z "${BITBAKE_TASK}" ]] || {
                echo "error: -c may be specified only once" >&2
                exit 2
            }
            BITBAKE_TASK="$2"
            shift 2
            ;;
        --keep-conf)
            KEEP_CONF=1
            shift
            ;;
        -*)
            echo "error: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            REQUESTED_TARGETS+=("$1")
            shift
            ;;
    esac
done

APOLLO_MACHINE="$(normalize_machine "${APOLLO_MACHINE}")"

if [[ -n "${BITBAKE_TASK}" && ${#REQUESTED_TARGETS[@]} -eq 0 ]]; then
    echo "error: -c requires at least one explicit target" >&2
    exit 2
elif [[ "${BSP_ONLY}" == "1" && ${#REQUESTED_TARGETS[@]} -gt 0 ]]; then
    echo "error: --bsp cannot be combined with explicit targets" >&2
    exit 2
elif [[ -n "${BITBAKE_TASK}" || ${#REQUESTED_TARGETS[@]} -gt 0 ]]; then
    KEEP_CONF=1
fi

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

set +u
# shellcheck source=/dev/null
source "${POKY_DIR}/oe-init-build-env" "${BUILD_DIR}"
set -u

BITBAKE_ARGS=()
BITBAKE_TASK_ARGS=()
if ((${#REQUESTED_TARGETS[@]})); then
    BITBAKE_TARGETS=("${REQUESTED_TARGETS[@]}")
elif [[ "${BSP_ONLY}" == "1" ]]; then
    BITBAKE_TARGETS=("nexios-bsp-initramfs")
else
    BITBAKE_TARGETS=("nexios-bsp-initramfs" "nexios-image")
fi
if [[ -n "${BITBAKE_TASK}" ]]; then
    BITBAKE_TASK_ARGS=(-c "${BITBAKE_TASK}")
fi
export APOLLO_BSP_BUILD_ONLY="${BSP_ONLY}"
export BB_ENV_PASSTHROUGH_ADDITIONS="${BB_ENV_PASSTHROUGH_ADDITIONS:-} APOLLO_BSP_BUILD_ONLY"

echo "notice: machine '${APOLLO_MACHINE}' uses shared build directory ${PWD}" >&2

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
    printf ' %q' "${BITBAKE_ARGS[@]}" "${BITBAKE_TARGETS[@]}" \
        "${BITBAKE_TASK_ARGS[@]}"
    printf '\n'
    exit 0
fi

MACHINE="${APOLLO_MACHINE}" \
APOLLO_BSP_BUILD_ONLY="${APOLLO_BSP_BUILD_ONLY}" \
    bitbake "${BITBAKE_ARGS[@]}" "${BITBAKE_TARGETS[@]}" \
        "${BITBAKE_TASK_ARGS[@]}"

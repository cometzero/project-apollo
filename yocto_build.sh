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
KERNEL_CONFIG_REQUESTS=()
REQUESTED_TARGETS=()

usage() {
    cat <<'EOF'
Usage: ./yocto_build.sh [options] [target ...]

Build the Apollo Yocto product and BSP validation images.

Options:
  --machine apollo-fvp|apollo-qvp
                          Select the Apollo Yocto machine.
  --bsp                   Build only nexios-bsp-initramfs.
  --enable-config CONFIG_NAME=y|m|n
                          Update the kernel defconfig. Repeat for each symbol.
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
        --enable-config)
            [[ $# -ge 2 ]] || {
                echo "error: $1 requires CONFIG_NAME=y, m, or n" >&2
                exit 2
            }
            KERNEL_CONFIG_REQUESTS+=("$2")
            shift 2
            ;;
        --enable-config=*)
            KERNEL_CONFIG_REQUESTS+=("${1#*=}")
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

normalize_kernel_config_requests() {
    local request symbol value existing
    local -a normalized=()

    for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
        if [[ ! "${request}" =~ ^(CONFIG_[A-Z0-9_]+)=(y|m|n)$ ]]; then
            echo "error: invalid kernel config '${request}' (expected CONFIG_NAME=y, m, or n)" >&2
            exit 2
        fi
        symbol="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        for existing in "${normalized[@]}"; do
            if [[ "${existing%%=*}" == "${symbol}" ]]; then
                echo "error: duplicate kernel config '${symbol}'" >&2
                exit 2
            fi
        done
        normalized+=("${symbol}=${value}")
    done

    KERNEL_CONFIG_REQUESTS=("${normalized[@]}")
}

normalize_kernel_config_requests

if ((${#KERNEL_CONFIG_REQUESTS[@]})); then
    if [[ "${BSP_ONLY}" == "1" || -n "${BITBAKE_TASK}" ||
        ${#REQUESTED_TARGETS[@]} -gt 0 ]]; then
        echo "error: --enable-config cannot be combined with --bsp, -c, or targets" >&2
        exit 2
    fi
    KEEP_CONF=1
elif [[ -n "${BITBAKE_TASK}" && ${#REQUESTED_TARGETS[@]} -eq 0 ]]; then
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

run_kernel_config_update() {
    local request symbol value action actual env_assignments
    local kernel_s kernel_b kernel_arch kernel_path kernel_cflags
    local kernel_toolchain_options kernel_build_cc kernel_build_cpp
    local kernel_build_cflags kernel_build_ldflags kernel_cc kernel_ld
    local kernel_objcopy kernel_strip kernel_defconfig kernel_defconfig_rel
    local candidate backup dry_s dry_b host_path="${PATH}"

    if [[ "${DRY_RUN}" == "1" ]]; then
        printf -v dry_s '\044S'
        printf -v dry_b '\044B'
        printf 'MACHINE=%q bitbake virtual/kernel -c defconfig -f\n' \
            "${APOLLO_MACHINE}"
        for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
            symbol="${request%%=*}"
            value="${request#*=}"
            case "${value}" in
                y) action="enable" ;;
                m) action="module" ;;
                n) action="disable" ;;
            esac
            printf 'scripts/config --file "%s/.config" --%s %q\n' \
                "${dry_b}" "${action}" "${symbol}"
        done
        printf 'make -C "%s" O="%s" olddefconfig\n' \
            "${dry_s}" "${dry_b}"
        printf 'make -C "%s" O="%s" savedefconfig\n' \
            "${dry_s}" "${dry_b}"
        printf 'MACHINE=%q bitbake virtual/kernel -c defconfig -f\n' \
            "${APOLLO_MACHINE}"
        return 0
    fi

    MACHINE="${APOLLO_MACHINE}" bitbake virtual/kernel -c defconfig -f

    env_assignments="$(
        MACHINE="${APOLLO_MACHINE}" bitbake -e virtual/kernel |
            sed -n -E '/^(export )?(S|B|ARCH|PATH|CFLAGS|TOOLCHAIN_OPTIONS|BUILD_CC|BUILD_CPP|BUILD_CFLAGS|BUILD_LDFLAGS|KERNEL_CC|KERNEL_LD|KERNEL_OBJCOPY|KERNEL_STRIP|APOLLO_KERNEL_DEFCONFIG_PATH)=/p'
    )"

    local S='' B='' ARCH='' PATH='' CFLAGS='' TOOLCHAIN_OPTIONS=''
    local BUILD_CC='' BUILD_CPP='' BUILD_CFLAGS='' BUILD_LDFLAGS=''
    local KERNEL_CC='' KERNEL_LD='' KERNEL_OBJCOPY='' KERNEL_STRIP=''
    local APOLLO_KERNEL_DEFCONFIG_PATH=''
    eval "${env_assignments}"

    kernel_s="${S}"
    kernel_b="${B}"
    kernel_arch="${ARCH}"
    kernel_path="${PATH}"
    PATH="${host_path}"
    kernel_cflags="${CFLAGS}"
    kernel_toolchain_options="${TOOLCHAIN_OPTIONS}"
    kernel_build_cc="${BUILD_CC}"
    kernel_build_cpp="${BUILD_CPP}"
    kernel_build_cflags="${BUILD_CFLAGS}"
    kernel_build_ldflags="${BUILD_LDFLAGS}"
    kernel_cc="${KERNEL_CC}"
    kernel_ld="${KERNEL_LD}"
    kernel_objcopy="${KERNEL_OBJCOPY}"
    kernel_strip="${KERNEL_STRIP}"
    kernel_defconfig="${APOLLO_KERNEL_DEFCONFIG_PATH}"

    [[ -x "${kernel_s}/scripts/config" ]] || {
        echo "error: missing kernel scripts/config: ${kernel_s}/scripts/config" >&2
        return 1
    }
    [[ -f "${kernel_b}/.config" ]] || {
        echo "error: missing effective kernel config: ${kernel_b}/.config" >&2
        return 1
    }
    [[ -f "${kernel_defconfig}" ]] || {
        echo "error: missing kernel defconfig: ${kernel_defconfig}" >&2
        return 1
    }
    [[ "${kernel_defconfig}" == "${kernel_s}/"* ]] || {
        echo "error: kernel defconfig is outside the kernel source: ${kernel_defconfig}" >&2
        return 1
    }
    kernel_defconfig_rel="${kernel_defconfig#"${kernel_s}/"}"
    if [[ -n "$(git -C "${kernel_s}" status --short -- "${kernel_defconfig_rel}")" ]]; then
        echo "error: kernel defconfig already has changes: ${kernel_defconfig}" >&2
        return 1
    fi

    for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
        symbol="${request%%=*}"
        value="${request#*=}"
        if ! rg -q "^[[:space:]]*(menu)?config[[:space:]]+${symbol#CONFIG_}([[:space:]]|$)" \
            "${kernel_s}" --glob 'Kconfig*'; then
            echo "error: unknown kernel config symbol '${symbol}'" >&2
            return 1
        fi
        case "${value}" in
            y)
                "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                    --enable "${symbol}"
                ;;
            m)
                "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                    --module "${symbol}"
                ;;
            n)
                "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                    --disable "${symbol}"
                ;;
        esac
    done

    kernel_make() {
        env PATH="${kernel_path}" \
            make -C "${kernel_s}" O="${kernel_b}" \
                "ARCH=${kernel_arch}" \
                "CFLAGS=${kernel_cflags} ${kernel_toolchain_options}" \
                "HOSTCC=${kernel_build_cc} ${kernel_build_cflags} ${kernel_build_ldflags}" \
                "HOSTCPP=${kernel_build_cpp}" \
                "CC=${kernel_cc}" \
                "LD=${kernel_ld}" \
                "OBJCOPY=${kernel_objcopy}" \
                "STRIP=${kernel_strip}" \
                "$@"
    }

    verify_kernel_config_requests() {
        local verify_request verify_symbol expected
        for verify_request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
            verify_symbol="${verify_request%%=*}"
            expected="${verify_request#*=}"
            actual="$(
                "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                    --state "${verify_symbol}"
            )"
            case "${expected}:${actual}" in
                y:y|m:m|n:n|n:undef)
                    ;;
                *)
                    printf 'error: %s requested=%s resolved=%s; add its Kconfig dependencies and retry\n' \
                        "${verify_symbol}" "${expected}" "${actual}" >&2
                    return 1
                    ;;
            esac
        done
    }

    kernel_make olddefconfig
    verify_kernel_config_requests

    kernel_make savedefconfig
    candidate="${kernel_b}/defconfig"
    [[ -f "${candidate}" ]] || {
        echo "error: savedefconfig did not create ${candidate}" >&2
        return 1
    }

    backup="$(mktemp "${kernel_b}/apollo-defconfig.backup.XXXXXX")"
    install -m 0644 "${kernel_defconfig}" "${backup}"
    install -m 0644 "${candidate}" "${kernel_defconfig}"
    rm -f -- "${candidate}"

    if ! MACHINE="${APOLLO_MACHINE}" bitbake virtual/kernel -c defconfig -f ||
        ! verify_kernel_config_requests; then
        install -m 0644 "${backup}" "${kernel_defconfig}"
        rm -f -- "${backup}"
        echo "error: saved defconfig failed regeneration; restored the original" >&2
        return 1
    fi
    rm -f -- "${backup}"

    echo "notice: updated ${kernel_defconfig}" >&2
    git -C "${kernel_s}" diff -- "${kernel_defconfig_rel}"
}

if ((${#KERNEL_CONFIG_REQUESTS[@]})); then
    run_kernel_config_update
    exit $?
fi

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

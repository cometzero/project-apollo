#!/usr/bin/env bash
#
# Launch the Apollo FVP full-system QBox demo from the workspace top directory.
#
# The script keeps the user-facing tmux layout from
# scripts/run/run_qbox_apollo_fvp_full_tmux.sh, selects a free SSH host-forward
# port, and applies the current default RSE/QBox performance options.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
TMUX_SESSION="${TMUX_SESSION:-apollo-qbox-demo-${RUN_STAMP}}"
OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/full-user-demo-${RUN_STAMP}}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-apollo-fvp}"
QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-}"
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-}"
QBOX_PLATFORM_DIR="${QBOX_PLATFORM_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox-platform}"
QBOX_CONF="${QBOX_CONF:-${QBOX_PLATFORM_DIR}/platforms/apollo/apollo-qvp.lua}"
SI_MODE="${SI_MODE:-live-cl0-cl1}"
TIMEOUT="${TIMEOUT:-0}"
JOBS="${JOBS:-$(( ($(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2) + 1) / 2 ))}"
SSH_PORT_START="${SSH_PORT_START:-2222}"
SSH_PORT_END="${SSH_PORT_END:-2299}"
RUN_QBOX_COPY_DISKS="${RUN_QBOX_COPY_DISKS:-0}"
DRY_RUN=0
LEGACY_FILE_BACKED_SRAM=0
TMUX_RUNNER_ARGS=()
REMOVED_ENV_OVERRIDES=()
REMOVED_ENV_NAMES=(
    "RSE_CPU_MODE"
    "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK"
    "REMOTEPASS_DMI_CACHE"
)

for name in "${REMOVED_ENV_NAMES[@]}"; do
    [[ -v ${name} ]] && REMOVED_ENV_OVERRIDES+=("${name}")
done

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

reject_removed_option()
{
    die "unsupported removed option: --$1"
}

usage()
{
    cat <<EOF
Usage: ./run_qbox.sh [tmux-runner options]

Build local boot artifacts first:
  ./local_build.sh

Then launch QBox in tmux:
  ./run_qbox.sh

Common overrides:
  TMUX_SESSION=apollo-demo ./run_qbox.sh
  OUT_DIR=build/qbox-apollo-fvp/my-run ./run_qbox.sh
  QBOX_PLATFORM_BUILD_DIR=build/local-apollo-fvp/work/qbox-platform ./run_qbox.sh
  QBOX_BUILD_DIR=/path/to/qbox-platform-build ./run_qbox.sh
  QBOX_PLATFORM_DIR=hsoc-stack/tools/qbox-platform ./run_qbox.sh
  QBOX_CONF=hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua ./run_qbox.sh
  SSH_PORT=2225 ./run_qbox.sh
  ./run_qbox.sh --copy-disks
  ./run_qbox.sh --no-attach
  ./run_qbox.sh --legacy-file-backed-sram
  ./run_qbox.sh --dry-run

Defaults:
  session: ${TMUX_SESSION}
  out_dir: ${OUT_DIR}
  local_build_dir: ${LOCAL_BUILD_DIR}
  qbox_platform_dir: ${QBOX_PLATFORM_DIR}
  qbox_conf: ${QBOX_CONF}
  qbox_build_dir: ${QBOX_PLATFORM_BUILD_DIR:-${QBOX_BUILD_DIR:-<local-build-dir>/work/qbox-platform}}
  si_mode: ${SI_MODE}
  timeout: ${TIMEOUT}

The selected SSH host-forward port is exposed as host port <port> -> guest :22.
By default, the local rootfs and EFI capsule disks are used directly. Use
--copy-disks to create per-run writable copies under <out_dir>/input-images.
The default RSE fast-boot SRAM path uses DMI/shared memory. Use
--legacy-file-backed-sram to select the older direct file-backed SRAM aliases.
EOF
}

abspath()
{
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "$PWD" "$1" ;;
    esac
}

port_in_use()
{
    local port="$1"

    if command -v ss >/dev/null 2>&1; then
        ss -H -ltn 2>/dev/null | awk '{print $4}' |
            grep -Eq "(^|[:.])${port}$|\\]:${port}$"
        return $?
    fi

    python3 - "${port}" <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.2)
    try:
        sock.connect(("127.0.0.1", port))
    except OSError:
        sys.exit(1)
sys.exit(0)
PY
}

find_free_port()
{
    local port

    if [[ -n "${SSH_PORT:-}" ]]; then
        port="${SSH_PORT}"
        [[ "${port}" =~ ^[0-9]+$ ]] || die "SSH_PORT must be numeric: ${port}"
        if port_in_use "${port}"; then
            die "requested SSH_PORT is already in use: ${port}"
        fi
        printf '%s\n' "${port}"
        return 0
    fi

    [[ "${SSH_PORT_START}" =~ ^[0-9]+$ ]] ||
        die "SSH_PORT_START must be numeric: ${SSH_PORT_START}"
    [[ "${SSH_PORT_END}" =~ ^[0-9]+$ ]] ||
        die "SSH_PORT_END must be numeric: ${SSH_PORT_END}"
    ((SSH_PORT_START <= SSH_PORT_END)) ||
        die "SSH_PORT_START must be <= SSH_PORT_END"

    for ((port = SSH_PORT_START; port <= SSH_PORT_END; port++)); do
        if ! port_in_use "${port}"; then
            printf '%s\n' "${port}"
            return 0
        fi
    done

    die "no free SSH host-forward port in ${SSH_PORT_START}-${SSH_PORT_END}"
}

preparse_args()
{
    local -a args=("$@")
    local i=0
    local arg

    while ((i < ${#args[@]})); do
        arg="${args[$i]}"
        case "${arg}" in
            --session)
                ((i + 1 < ${#args[@]})) || die "--session requires a value"
                TMUX_SESSION="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --out-dir)
                ((i + 1 < ${#args[@]})) || die "--out-dir requires a value"
                OUT_DIR="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --local-build-dir)
                ((i + 1 < ${#args[@]})) || die "--local-build-dir requires a value"
                LOCAL_BUILD_DIR="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --qbox-build-dir)
                ((i + 1 < ${#args[@]})) || die "--qbox-build-dir requires a value"
                QBOX_BUILD_DIR="${args[$((i + 1))]}"
                QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --si-mode)
                ((i + 1 < ${#args[@]})) || die "--si-mode requires a value"
                SI_MODE="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --timeout)
                ((i + 1 < ${#args[@]})) || die "--timeout requires a value"
                TIMEOUT="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --jobs)
                ((i + 1 < ${#args[@]})) || die "--jobs requires a value"
                JOBS="${args[$((i + 1))]}"
                TMUX_RUNNER_ARGS+=("${arg}" "${args[$((i + 1))]}")
                i=$((i + 2))
                ;;
            --rse-cpu-mode|--rse-cpu-mode=*)
                reject_removed_option "rse-cpu-mode"
                ;;
            --copy-disks)
                RUN_QBOX_COPY_DISKS=1
                i=$((i + 1))
                ;;
            --no-copy-disks)
                RUN_QBOX_COPY_DISKS=0
                i=$((i + 1))
                ;;
            --dry-run)
                DRY_RUN=1
                TMUX_RUNNER_ARGS+=("${arg}")
                i=$((i + 1))
                ;;
            --legacy-file-backed-sram)
                LEGACY_FILE_BACKED_SRAM=1
                i=$((i + 1))
                ;;
            --rse-hotpath-tlm-fallback)
                reject_removed_option "rse-hotpath-tlm-fallback"
                ;;
            --no-rse-hotpath-tlm-fallback)
                reject_removed_option "no-rse-hotpath-tlm-fallback"
                ;;
            --remotepass-dmi-cache|--remotepass-dmi-cache=*)
                reject_removed_option "remotepass-dmi-cache"
                ;;
            --)
                while ((i < ${#args[@]})); do
                    TMUX_RUNNER_ARGS+=("${args[$i]}")
                    i=$((i + 1))
                done
                break
                ;;
            *)
                TMUX_RUNNER_ARGS+=("${arg}")
                i=$((i + 1))
                ;;
        esac
    done
}

reject_removed_environment_overrides()
{
    local name

    for name in "${REMOVED_ENV_OVERRIDES[@]}"; do
        die "unsupported removed environment override: ${name}"
    done
}

arg_present()
{
    local name="$1"
    shift
    local arg

    for arg in "$@"; do
        if [[ "${arg}" == "${name}" || "${arg}" == "${name}="* ]]; then
            return 0
        fi
    done
    return 1
}

copy_image()
{
    local src="$1"
    local dst="$2"

    [[ -f "${src}" ]] || die "missing input image: ${src}"
    mkdir -p "$(dirname "${dst}")"
    cp --reflink=auto --sparse=always -- "${src}" "${dst}"
}

prepare_run_disks()
{
    local rootfs_src="${LOCAL_BUILD_DIR}/deploy/boot/apollo-fvp-local-disk.img"
    local efi_src="${LOCAL_BUILD_DIR}/deploy/boot/boot-fat.img"
    local image_dir="${OUT_DIR}/input-images"

    RUN_ROOTFS="${image_dir}/apollo-fvp-local-disk.img"
    RUN_EFI_CAPSULE_DISK="${image_dir}/boot-fat.img"

    if [[ "${RUN_QBOX_COPY_DISKS}" != "1" ]]; then
        RUN_ROOTFS="${rootfs_src}"
        RUN_EFI_CAPSULE_DISK="${efi_src}"
        return 0
    fi

    if ((DRY_RUN)); then
        return 0
    fi

    copy_image "${rootfs_src}" "${RUN_ROOTFS}"
    copy_image "${efi_src}" "${RUN_EFI_CAPSULE_DISK}"
}

main()
{
    case "${1:-}" in
        -h|--help|help)
            usage
            return 0
            ;;
    esac

    reject_removed_environment_overrides
    preparse_args "$@"
    if ((LEGACY_FILE_BACKED_SRAM)) &&
        arg_present "--rse-fast-boot-sram-dmi" "$@"; then
        die "--legacy-file-backed-sram conflicts with --rse-fast-boot-sram-dmi"
    fi
    if ((! LEGACY_FILE_BACKED_SRAM)) &&
        arg_present "--rse-fast-boot-aliases" "$@"; then
        die "--rse-fast-boot-aliases conflicts with the default --rse-fast-boot-sram-dmi; use --legacy-file-backed-sram"
    fi
    OUT_DIR="$(abspath "${OUT_DIR}")"
    LOCAL_BUILD_DIR="$(abspath "${LOCAL_BUILD_DIR}")"
    QBOX_PLATFORM_DIR="$(abspath "${QBOX_PLATFORM_DIR}")"
    QBOX_CONF="$(abspath "${QBOX_CONF}")"
    if [[ -z "${QBOX_PLATFORM_BUILD_DIR}" ]]; then
        if [[ -n "${QBOX_BUILD_DIR}" ]]; then
            QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
        else
            QBOX_PLATFORM_BUILD_DIR="${LOCAL_BUILD_DIR}/work/qbox-platform"
        fi
    fi
    QBOX_PLATFORM_BUILD_DIR="$(abspath "${QBOX_PLATFORM_BUILD_DIR}")"
    QBOX_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR}"

    [[ -d "${LOCAL_BUILD_DIR}" ]] ||
        die "missing local build directory: ${LOCAL_BUILD_DIR}. Run ./local_build.sh build first."

    local ssh_port
    local netdev
    ssh_port="$(find_free_port)"
    netdev="${QBOX_NETDEV:-type=user,hostfwd=tcp::${ssh_port}-:22}"
    prepare_run_disks

    printf 'Apollo QBox full-system launch\n'
    printf '  session: %s\n' "${TMUX_SESSION}"
    printf '  out_dir: %s\n' "${OUT_DIR}"
    printf '  ssh: host port %s -> guest port 22\n' "${ssh_port}"
    printf '  netdev: %s\n' "${netdev}"
    printf '  qbox_platform_dir: %s\n' "${QBOX_PLATFORM_DIR}"
    printf '  qbox_conf: %s\n' "${QBOX_CONF}"
    printf '  qbox_build_dir: %s\n' "${QBOX_BUILD_DIR}"
    printf '  rootfs: %s\n' "${RUN_ROOTFS}"
    printf '  efi_capsule_disk: %s\n' "${RUN_EFI_CAPSULE_DISK}"
    printf '  copy_disks: %s\n' "${RUN_QBOX_COPY_DISKS}"

    local rse_fast_boot_mode
    rse_fast_boot_mode="--rse-fast-boot-sram-dmi"
    if ((LEGACY_FILE_BACKED_SRAM)); then
        rse_fast_boot_mode="--rse-fast-boot-aliases"
    fi
    export QBOX_PLATFORM_DIR QBOX_CONF QBOX_PLATFORM_BUILD_DIR QBOX_BUILD_DIR

    exec "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full_tmux.sh" \
        --session "${TMUX_SESSION}" \
        --out-dir "${OUT_DIR}" \
        --local-build-dir "${LOCAL_BUILD_DIR}" \
        --qbox-build-dir "${QBOX_BUILD_DIR}" \
        --si-mode "${SI_MODE}" \
        --timeout "${TIMEOUT}" \
        --jobs "${JOBS}" \
        --skip-build \
        --keep-running-after-pass \
        --qbox-performance-preset \
        --cc3xx-qemu-native-backend \
        --netdev "${netdev}" \
        --tmux-layout fvp-like \
        "${TMUX_RUNNER_ARGS[@]}" \
        -- \
        --rootfs "${RUN_ROOTFS}" \
        --efi-capsule-disk "${RUN_EFI_CAPSULE_DISK}" \
        --rse-hotpath-accel \
        --rse-lms-accel \
        "${rse_fast_boot_mode}" \
        --rse-bl2-libc-hotpath \
        --rse-bl2-delay-accel \
        --rse-bl2-load-accel \
        --rse-bl2-boot-enc-accel \
        --rse-bl2-img-hash-accel \
        --rse-bl2-verify-sig-accel
}

main "$@"

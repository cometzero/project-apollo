#!/usr/bin/env bash
#
# Run the Apollo FVP full-system QBox target in a tmux session.
#
# The runner pane keeps the QBox wrapper output visible. Each known subsystem
# UART log is tailed in its own tmux pane so the same run is useful for a
# user-facing demo and for file-backed analysis.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/$(basename "${BASH_SOURCE[0]}")"

PYTHON_BIN="${PYTHON:-python3}"
TMUX_BIN="${TMUX_BIN:-tmux}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
TMUX_SESSION="${TMUX_SESSION:-apollo-qbox-full-${RUN_STAMP}}"
OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/full-tmux-${RUN_STAMP}}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-apollo-fvp}"
QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-}"
QBOX_CONF="${QBOX_CONF:-${ROOT_DIR}/tools/qbox/platforms/apollo/apollo-qvp.lua}"
SI_MODE="${SI_MODE:-live-cl0-cl1}"
TIMEOUT="${TIMEOUT:-0}"
JOBS="${JOBS:-$(( ($(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2) + 1) / 2 ))}"
ROOTFS_BOOTARGS_PROFILE="${ROOTFS_BOOTARGS_PROFILE:-none}"
QBOX_PERFORMANCE_PRESET="${QBOX_PERFORMANCE_PRESET:-1}"
LEGACY_FILE_BACKED_SRAM="${LEGACY_FILE_BACKED_SRAM:-0}"
RANGE_LIMITED_FLASH_DMI="${RANGE_LIMITED_FLASH_DMI:-1}"
CC3XX_STATS="${CC3XX_STATS:-0}"
CC3XX_STATS_INTERVAL="${CC3XX_STATS_INTERVAL:-1024}"
CC3XX_STATUS_READ_FASTPATH="${CC3XX_STATUS_READ_FASTPATH:-0}"
CC3XX_QEMU_NATIVE_BACKEND="${CC3XX_QEMU_NATIVE_BACKEND:-0}"
CC3XX_LOCAL_MMIO_FASTPATH="${CC3XX_LOCAL_MMIO_FASTPATH:-0}"
REMOTEPASS_DMI_CACHE="${REMOTEPASS_DMI_CACHE:-0}"
NETDEV="${NETDEV:-${QBOX_RDASPEN_NETDEV:-${QBOX_APOLLO_NETDEV:-}}}"
SKIP_BUILD="${SKIP_BUILD:-1}"
POST_LOGIN_PROBE="${POST_LOGIN_PROBE:-1}"
KEEP_RUNNING_AFTER_PASS="${KEEP_RUNNING_AFTER_PASS:-1}"
NO_ATTACH=0
DRY_RUN=0

RUNNER_ARGS_FILE="${RUNNER_ARGS_FILE:-}"

usage()
{
    cat <<EOF
Usage: scripts/run/run_qbox_apollo_fvp_full_tmux.sh [options] [-- runner args]

Run the Apollo FVP full-system QBox path in tmux and tail subsystem logs.

Options:
  --session NAME       tmux session name (default: ${TMUX_SESSION})
  --out-dir PATH       log/output directory (default: ${OUT_DIR})
  --local-build-dir P  local build directory (default: ${LOCAL_BUILD_DIR})
  --qbox-build-dir P   QBox CMake build directory
                       (default: <local-build-dir>/work/qbox)
  --conf PATH          QBox Lua config (default: ${QBOX_CONF})
  --si-mode MODE       service-model, live-cl1, or live-cl0-cl1
                       (default: ${SI_MODE})
  --timeout SECONDS    runner timeout, 0 means no timeout (default: ${TIMEOUT})
  --jobs N             build jobs passed to the runner (default: ${JOBS})
  --build              build QBox targets before running
  --skip-build         skip QBox build before running (default)
  --post-login-probe   run Linux post-login probes (default)
  --no-post-login-probe
  --keep-running-after-pass
                       keep QBox alive after Linux boot/probes pass (default)
  --exit-after-pass    stop QBox when the normal pass condition is reached
  --rootfs-bootargs-profile NAME
                       runner bootargs profile (default: ${ROOTFS_BOOTARGS_PROFILE})
  --qbox-performance-preset
                       enable default QBox boot acceleration preset (default;
                       uses SRAM DMI/shared-memory fast boot)
  --no-qbox-performance-preset
                       disable default QBox boot acceleration preset
  --legacy-file-backed-sram
                       use legacy direct file-backed SRAM aliases instead of
                       the default SRAM DMI/shared-memory fast boot preset
  --range-limited-flash-dmi
                       enable range-limited flash DMI fast path (default)
  --no-range-limited-flash-dmi
                       disable range-limited flash DMI
  --cc3xx-stats        collect RSE CC3XX aggregate statistics
  --cc3xx-stats-interval N
                       CC3XX stats write interval (default: ${CC3XX_STATS_INTERVAL})
  --cc3xx-status-read-fastpath
                       enable QEMU-side CC3XX ready/status read fast path
  --cc3xx-qemu-native-backend
                       use QEMU-native CC3XX and direct MMIO fast path
  --cc3xx-local-mmio-fastpath
                       enable QEMU-local CC3XX direct MMIO fast path
  --remotepass-dmi-cache
                       enable RemotePass shared-memory DMI cache
  --netdev SPEC        QEMU user-net specification forwarded to the AP virtio
                       net device, for example type=user,hostfwd=tcp::2223-:22
  --no-attach          start tmux but do not attach
  --dry-run            print the run command and log layout only
  -h, --help           show this help

The default performance preset is expanded by the Python runner into the
RemotePass DMI cache, QEMU-native CC3XX backend, RSE hotpaths, BL2 semantic
accelerators, and RSE fast-boot SRAM DMI/shared-memory mode. Use
--legacy-file-backed-sram for the older direct file-backed SRAM alias mode.

Environment overrides:
  PYTHON TMUX_BIN TMUX_SESSION OUT_DIR RUN_STAMP LOCAL_BUILD_DIR QBOX_BUILD_DIR QBOX_CONF
  SI_MODE TIMEOUT JOBS SKIP_BUILD POST_LOGIN_PROBE KEEP_RUNNING_AFTER_PASS
  ROOTFS_BOOTARGS_PROFILE QBOX_PERFORMANCE_PRESET LEGACY_FILE_BACKED_SRAM
  RANGE_LIMITED_FLASH_DMI CC3XX_STATS
  CC3XX_STATS_INTERVAL CC3XX_STATUS_READ_FASTPATH CC3XX_QEMU_NATIVE_BACKEND
  CC3XX_LOCAL_MMIO_FASTPATH REMOTEPASS_DMI_CACHE
  NETDEV QBOX_RDASPEN_NETDEV QBOX_APOLLO_NETDEV

Inside tmux:
  F12                  kill the whole session
  mouse                enabled

Subsystem UART logs:
  rse                  RSE / TF-M
  safety_island_cl0    Safety Island CL0 / SCP-firmware
  safety_island_cl1    Safety Island CL1 / Zephyr
  secure_console       TF-A / OP-TEE secure AP console
  primary_console      U-Boot / Linux primary console
EOF
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_command()
{
    command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

abspath()
{
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "$PWD" "$1" ;;
    esac
}

quote_args()
{
    local arg
    (($# > 0)) || return 0
    printf '%q' "$1"
    shift || true
    for arg in "$@"; do
        printf ' %q' "$arg"
    done
}

validate_tmux_name()
{
    [[ "$1" =~ ^[A-Za-z0-9_.-]+$ ]] ||
        die "tmux session name must contain only letters, numbers, dot, underscore, or dash: $1"
}

validate_bool()
{
    case "$2" in
        0|1) ;;
        *) die "$1 must be 0 or 1: $2" ;;
    esac
}

validate_si_mode()
{
    case "$1" in
        service-model|live-cl1|live-cl0-cl1) ;;
        *) die "invalid --si-mode: $1" ;;
    esac
}

tmux_cmd()
{
    env -u TMUX "${TMUX_BIN}" "$@"
}

runner_command()
{
    local -n _out="$1"
    shift
    local -a extra_args=("$@")

    _out=(
        "${PYTHON_BIN}"
        "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full.py"
        --conf "${QBOX_CONF}"
        --local-build-dir "${LOCAL_BUILD_DIR}"
        --qbox-build-dir "${QBOX_BUILD_DIR}"
        --si-mode "${SI_MODE}"
        --out-dir "${OUT_DIR}"
        --timeout "${TIMEOUT}"
        --jobs "${JOBS}"
        --rootfs-bootargs-profile "${ROOTFS_BOOTARGS_PROFILE}"
    )

    if [[ "${RANGE_LIMITED_FLASH_DMI}" == "1" ]]; then
        _out+=(--range-limited-flash-dmi)
    fi
    if [[ "${QBOX_PERFORMANCE_PRESET}" == "1" ]]; then
        _out+=(--qbox-performance-preset)
    else
        _out+=(--no-qbox-performance-preset)
    fi
    if [[ "${LEGACY_FILE_BACKED_SRAM}" == "1" ]]; then
        _out+=(--legacy-file-backed-sram)
    fi
    if [[ "${CC3XX_STATS}" == "1" ]]; then
        _out+=(--cc3xx-stats --cc3xx-stats-interval "${CC3XX_STATS_INTERVAL}")
    fi
    if [[ "${CC3XX_STATUS_READ_FASTPATH}" == "1" ]]; then
        _out+=(--cc3xx-status-read-fastpath)
    fi
    if [[ "${CC3XX_QEMU_NATIVE_BACKEND}" == "1" ]]; then
        _out+=(--cc3xx-qemu-native-backend)
    fi
    if [[ "${CC3XX_LOCAL_MMIO_FASTPATH}" == "1" ]]; then
        _out+=(--cc3xx-local-mmio-fastpath)
    fi
    if [[ "${REMOTEPASS_DMI_CACHE}" == "1" ]]; then
        _out+=(--remotepass-dmi-cache)
    fi
    if [[ "${SKIP_BUILD}" == "1" ]]; then
        _out+=(--skip-build)
    fi
    if [[ "${POST_LOGIN_PROBE}" == "1" ]]; then
        _out+=(--post-login-probe)
    fi
    if [[ "${KEEP_RUNNING_AFTER_PASS}" == "1" ]]; then
        _out+=(--keep-running-after-pass)
    fi
    if ((${#extra_args[@]} > 0)); then
        _out+=("${extra_args[@]}")
    fi
}

known_logs()
{
    cat <<EOF
platform:qbox-platform.log:QBox platform stdout
rse:qbox-rse.log:RSE / TF-M
safety_island_cl0:qbox-safety-island-cl0.log:Safety Island CL0 / SCP-firmware
safety_island_cl1:qbox-safety-island-cl1.log:Safety Island CL1 / Zephyr
secure_console:qbox-secure-console.log:TF-A / OP-TEE secure AP
primary_console:qbox-primary-console.log:U-Boot / Linux
EOF
}

prepare_log_files()
{
    mkdir -p "${OUT_DIR}"
    local spec
    local domain
    local file
    local title
    : >"${OUT_DIR}/tmux-log-layout.tsv"
    printf 'domain\tfile\ttitle\n' >"${OUT_DIR}/tmux-log-layout.tsv"
    while IFS=: read -r domain file title; do
        : >"${OUT_DIR}/${file}"
        printf '%s\t%s\t%s\n' "${domain}" "${OUT_DIR}/${file}" "${title}" \
            >>"${OUT_DIR}/tmux-log-layout.tsv"
    done < <(known_logs)
}

tail_supports_pid()
{
    tail --help 2>&1 | grep -q -- '--pid'
}

tail_log()
{
    (($# == 3)) || die "--tail-log requires DOMAIN TITLE LOG_PATH"

    local domain="$1"
    local title="$2"
    local log_path="$3"
    local pid_file="${OUT_DIR}/qbox-run.pid"
    local done_file="${OUT_DIR}/.qbox-run.done"
    local pid=""

    mkdir -p "$(dirname "${log_path}")"
    : >>"${log_path}"

    printf 'Subsystem: %s\n' "${title}"
    printf 'Domain: %s\n' "${domain}"
    printf 'Log: %s\n\n' "${log_path}"

    while [[ ! -e "${pid_file}" && ! -e "${done_file}" ]]; do
        sleep 0.2
    done

    if [[ -s "${pid_file}" ]]; then
        pid="$(<"${pid_file}")"
    fi

    if [[ -n "${pid}" ]] && tail_supports_pid; then
        tail --pid="${pid}" -n +1 -F "${log_path}" || true
    elif [[ ! -e "${done_file}" ]]; then
        tail -n +1 -F "${log_path}" || true
    else
        tail -n +1 "${log_path}" || true
    fi

    printf '\nLog pane exited. Press Enter to close this pane, or F12 to kill the session.\n'
    read -r _ || true
}

supervise_run()
{
    require_command "${PYTHON_BIN}"

    mapfile -t EXTRA_RUNNER_ARGS <"${RUNNER_ARGS_FILE}"
    local -a cmd=()
    runner_command cmd "${EXTRA_RUNNER_ARGS[@]}"

    prepare_log_files
    : >"${OUT_DIR}/qbox-runner.log"
    : >"${OUT_DIR}/qbox-run.status"
    rm -f "${OUT_DIR}/.qbox-run.done" "${OUT_DIR}/qbox-run.pid"
    quote_args "${cmd[@]}" >"${OUT_DIR}/qbox-run.cmd"

    printf 'QBox Apollo full-system tmux run\n'
    printf 'Logs: %s\n' "${OUT_DIR}"
    printf 'Runner log: %s\n' "${OUT_DIR}/qbox-runner.log"
    printf 'Command: %s\n\n' "$(quote_args "${cmd[@]}")"
    printf 'F12 kills the tmux session.\n\n'

    local status_file="${OUT_DIR}/qbox-run.status.tmp"
    rm -f "${status_file}"

    set +e
    if command -v stdbuf >/dev/null 2>&1; then
        (
            stdbuf -oL -eL "${cmd[@]}"
            printf '%s\n' "$?" >"${status_file}"
        ) 2>&1 | tee -a "${OUT_DIR}/qbox-runner.log" &
    else
        (
            "${cmd[@]}"
            printf '%s\n' "$?" >"${status_file}"
        ) 2>&1 | tee -a "${OUT_DIR}/qbox-runner.log" &
    fi
    local run_pid=$!
    printf '%s\n' "${run_pid}" >"${OUT_DIR}/qbox-run.pid"
    wait "${run_pid}"
    local pipeline_status=$?
    set -e

    local status="${pipeline_status}"
    if [[ -s "${status_file}" ]]; then
        status="$(<"${status_file}")"
    fi
    printf '%s\n' "${status}" >"${OUT_DIR}/qbox-run.status"
    rm -f "${status_file}"
    : >"${OUT_DIR}/.qbox-run.done"

    printf '\nQBox runner exited with status %s.\n' "${status}" |
        tee -a "${OUT_DIR}/qbox-runner.log"
    printf 'Logs remain under: %s\n' "${OUT_DIR}" |
        tee -a "${OUT_DIR}/qbox-runner.log"
    printf 'Press Enter to close this pane, or F12 to kill the session.\n'
    read -r _ || true
    return "${status}"
}

print_dry_run()
{
    mapfile -t EXTRA_RUNNER_ARGS <"${RUNNER_ARGS_FILE}"
    local -a cmd=()
    runner_command cmd "${EXTRA_RUNNER_ARGS[@]}"
    local effective_cc3xx_qemu_native_backend="${CC3XX_QEMU_NATIVE_BACKEND}"
    local effective_cc3xx_local_mmio_fastpath="${CC3XX_LOCAL_MMIO_FASTPATH}"
    local effective_remotepass_dmi_cache="${REMOTEPASS_DMI_CACHE}"
    local explicit_sram_dmi=0
    local explicit_legacy_file_backed_sram="${LEGACY_FILE_BACKED_SRAM}"
    local rse_fast_boot_mode="disabled"
    local rse_fast_boot_summary="disabled: no SRAM fast-boot mode selected"
    local arg

    if [[ "${QBOX_PERFORMANCE_PRESET}" == "1" ]]; then
        effective_cc3xx_qemu_native_backend=1
        effective_cc3xx_local_mmio_fastpath=1
        effective_remotepass_dmi_cache=1
    elif [[ "${CC3XX_QEMU_NATIVE_BACKEND}" == "1" ]]; then
        effective_cc3xx_local_mmio_fastpath=1
    fi

    for arg in "${EXTRA_RUNNER_ARGS[@]}"; do
        case "${arg}" in
            --rse-fast-boot-sram-dmi)
                explicit_sram_dmi=1
                ;;
            --legacy-file-backed-sram|--rse-fast-boot-aliases)
                explicit_legacy_file_backed_sram=1
                ;;
            --rse-direct-si-sram-alias|--rse-direct-ap-bl2-alias)
                explicit_legacy_file_backed_sram=1
                ;;
            --rse-direct-file-aliases|--rse-direct-file-aliases=*)
                explicit_legacy_file_backed_sram=1
                ;;
        esac
    done

    if [[ "${explicit_sram_dmi}" == "1" &&
          "${explicit_legacy_file_backed_sram}" == "1" ]]; then
        rse_fast_boot_mode="conflict"
        rse_fast_boot_summary="conflict: both SRAM DMI and legacy file-backed SRAM requested"
    elif [[ "${explicit_legacy_file_backed_sram}" == "1" ]]; then
        rse_fast_boot_mode="legacy_file_backed_sram"
        rse_fast_boot_summary="legacy file-backed SRAM aliases active"
    elif [[ "${QBOX_PERFORMANCE_PRESET}" == "1" ||
            "${explicit_sram_dmi}" == "1" ]]; then
        rse_fast_boot_mode="sram_dmi"
        rse_fast_boot_summary="SRAM DMI/shared-memory fast boot active"
    fi

    cat <<EOF
Apollo QBox full-system tmux run
  session: ${TMUX_SESSION}
  si_mode: ${SI_MODE}
  qbox_performance_preset: ${QBOX_PERFORMANCE_PRESET}
  legacy_file_backed_sram: ${explicit_legacy_file_backed_sram}
  explicit_rse_fast_boot_sram_dmi: ${explicit_sram_dmi}
  effective_rse_fast_boot_mode: ${rse_fast_boot_mode}
  sram_fast_boot_summary: ${rse_fast_boot_summary}
  range_limited_flash_dmi: ${RANGE_LIMITED_FLASH_DMI}
  cc3xx_stats: ${CC3XX_STATS}
  cc3xx_status_read_fastpath: ${CC3XX_STATUS_READ_FASTPATH}
  cc3xx_qemu_native_backend: ${CC3XX_QEMU_NATIVE_BACKEND}
  cc3xx_local_mmio_fastpath: ${CC3XX_LOCAL_MMIO_FASTPATH}
  remotepass_dmi_cache: ${REMOTEPASS_DMI_CACHE}
  effective_cc3xx_qemu_native_backend: ${effective_cc3xx_qemu_native_backend}
  effective_cc3xx_local_mmio_fastpath: ${effective_cc3xx_local_mmio_fastpath}
  effective_remotepass_dmi_cache: ${effective_remotepass_dmi_cache}
  netdev: ${NETDEV:-default}
  out_dir: ${OUT_DIR}
  qbox_build_dir: ${QBOX_BUILD_DIR}
  command: $(quote_args "${cmd[@]}")

file-backed logs
EOF
    local domain
    local file
    local title
    while IFS=: read -r domain file title; do
        printf '  %-18s %s/%s (%s)\n' "${domain}" "${OUT_DIR}" "${file}" "${title}"
    done < <(known_logs)
}

start_log_pane()
{
    local domain="$1"
    local file="$2"
    local title="$3"
    local log_path="${OUT_DIR}/${file}"
    local pane_body
    local pane_id

    pane_body=$(
        printf 'cd %q || exit 1; ' "${ROOT_DIR}"
        printf 'OUT_DIR=%q exec %q --tail-log %q %q %q' \
            "${OUT_DIR}" "${SCRIPT_PATH}" "${domain}" "${title}" "${log_path}"
    )

    pane_id="$(tmux_cmd split-window -P -F '#{pane_id}' -t "${TMUX_SESSION}:qbox" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T "${domain}"
    tmux_cmd select-layout -t "${TMUX_SESSION}:qbox" tiled >/dev/null
}

start_tmux()
{
    validate_tmux_name "${TMUX_SESSION}"
    validate_si_mode "${SI_MODE}"
    validate_bool "QBOX_PERFORMANCE_PRESET" "${QBOX_PERFORMANCE_PRESET}"
    validate_bool "LEGACY_FILE_BACKED_SRAM" "${LEGACY_FILE_BACKED_SRAM}"
    validate_bool "RANGE_LIMITED_FLASH_DMI" "${RANGE_LIMITED_FLASH_DMI}"
    validate_bool "CC3XX_STATS" "${CC3XX_STATS}"
    validate_bool "CC3XX_STATUS_READ_FASTPATH" "${CC3XX_STATUS_READ_FASTPATH}"
    validate_bool "CC3XX_QEMU_NATIVE_BACKEND" "${CC3XX_QEMU_NATIVE_BACKEND}"
    validate_bool "CC3XX_LOCAL_MMIO_FASTPATH" "${CC3XX_LOCAL_MMIO_FASTPATH}"
    validate_bool "REMOTEPASS_DMI_CACHE" "${REMOTEPASS_DMI_CACHE}"
    validate_bool "SKIP_BUILD" "${SKIP_BUILD}"
    validate_bool "POST_LOGIN_PROBE" "${POST_LOGIN_PROBE}"
    validate_bool "KEEP_RUNNING_AFTER_PASS" "${KEEP_RUNNING_AFTER_PASS}"
    require_command "${TMUX_BIN}"
    require_command "${PYTHON_BIN}"

    [[ -f "${QBOX_CONF}" ]] || die "QBox config not found: ${QBOX_CONF}"
    [[ -d "${LOCAL_BUILD_DIR}" ]] ||
        die "local build directory not found: ${LOCAL_BUILD_DIR}. Run ./local-build.sh build first."

    ROOT_DIR="$(abspath "${ROOT_DIR}")"
    SCRIPT_PATH="$(abspath "${SCRIPT_PATH}")"
    OUT_DIR="$(abspath "${OUT_DIR}")"
    LOCAL_BUILD_DIR="$(abspath "${LOCAL_BUILD_DIR}")"
    if [[ -z "${QBOX_BUILD_DIR}" ]]; then
        QBOX_BUILD_DIR="${LOCAL_BUILD_DIR}/work/qbox"
    fi
    QBOX_BUILD_DIR="$(abspath "${QBOX_BUILD_DIR}")"
    QBOX_CONF="$(abspath "${QBOX_CONF}")"
    mkdir -p "${OUT_DIR}"

    local runner_args_file="${OUT_DIR}/extra-runner-args.txt"
    : >"${runner_args_file}"
    local arg
    for arg in "${EXTRA_RUNNER_ARGS[@]}"; do
        printf '%s\n' "${arg}" >>"${runner_args_file}"
    done
    RUNNER_ARGS_FILE="${runner_args_file}"

    prepare_log_files

    if ((DRY_RUN)); then
        print_dry_run
        return 0
    fi

    if tmux_cmd has-session -t "${TMUX_SESSION}" 2>/dev/null; then
        die "tmux session already exists: ${TMUX_SESSION}"
    fi

    local supervisor_body
    supervisor_body=$(
        printf 'cd %q || exit 1; ' "${ROOT_DIR}"
        printf 'ROOT_DIR=%q SCRIPT_PATH=%q PYTHON_BIN=%q QBOX_CONF=%q ' \
            "${ROOT_DIR}" "${SCRIPT_PATH}" "${PYTHON_BIN}" "${QBOX_CONF}"
        printf 'LOCAL_BUILD_DIR=%q QBOX_BUILD_DIR=%q OUT_DIR=%q SI_MODE=%q TIMEOUT=%q JOBS=%q ' \
            "${LOCAL_BUILD_DIR}" "${QBOX_BUILD_DIR}" "${OUT_DIR}" "${SI_MODE}" "${TIMEOUT}" "${JOBS}"
        printf 'ROOTFS_BOOTARGS_PROFILE=%q ' "${ROOTFS_BOOTARGS_PROFILE}"
        printf 'QBOX_PERFORMANCE_PRESET=%q ' "${QBOX_PERFORMANCE_PRESET}"
        printf 'LEGACY_FILE_BACKED_SRAM=%q ' "${LEGACY_FILE_BACKED_SRAM}"
        printf 'RANGE_LIMITED_FLASH_DMI=%q CC3XX_STATS=%q ' \
            "${RANGE_LIMITED_FLASH_DMI}" "${CC3XX_STATS}"
        printf 'CC3XX_STATS_INTERVAL=%q CC3XX_STATUS_READ_FASTPATH=%q ' \
            "${CC3XX_STATS_INTERVAL}" "${CC3XX_STATUS_READ_FASTPATH}"
        printf 'CC3XX_QEMU_NATIVE_BACKEND=%q ' "${CC3XX_QEMU_NATIVE_BACKEND}"
        printf 'CC3XX_LOCAL_MMIO_FASTPATH=%q ' "${CC3XX_LOCAL_MMIO_FASTPATH}"
        printf 'REMOTEPASS_DMI_CACHE=%q ' "${REMOTEPASS_DMI_CACHE}"
        if [[ -n "${NETDEV}" ]]; then
            printf 'NETDEV=%q QBOX_RDASPEN_NETDEV=%q QBOX_APOLLO_NETDEV=%q ' \
                "${NETDEV}" "${NETDEV}" "${NETDEV}"
        fi
        printf 'SKIP_BUILD=%q POST_LOGIN_PROBE=%q ' \
            "${SKIP_BUILD}" "${POST_LOGIN_PROBE}"
        printf 'KEEP_RUNNING_AFTER_PASS=%q ' "${KEEP_RUNNING_AFTER_PASS}"
        printf 'RUNNER_ARGS_FILE=%q exec %q --supervise' \
            "${RUNNER_ARGS_FILE}" "${SCRIPT_PATH}"
    )

    local runner_pane_id
    runner_pane_id="$(tmux_cmd new-session -d -P -F '#{pane_id}' -s "${TMUX_SESSION}" -n qbox bash -lc "${supervisor_body}")"
    tmux_cmd set-option -t "${TMUX_SESSION}" mouse on
    tmux_cmd set-window-option -t "${TMUX_SESSION}:qbox" pane-border-status top
    tmux_cmd set-window-option -t "${TMUX_SESSION}:qbox" pane-border-format '#{pane_index}: #{pane_title}'
    tmux_cmd select-pane -t "${runner_pane_id}" -T qbox-runner
    tmux_cmd bind-key -n F12 kill-session -t "${TMUX_SESSION}"

    local domain
    local file
    local title
    while IFS=: read -r domain file title; do
        start_log_pane "${domain}" "${file}" "${title}"
    done < <(known_logs)
    tmux_cmd select-pane -t "${runner_pane_id}"
    tmux_cmd select-layout -t "${TMUX_SESSION}:qbox" tiled >/dev/null

    printf 'started tmux session: %s\n' "${TMUX_SESSION}"
    printf 'logs: %s\n' "${OUT_DIR}"
    printf 'attach command: %s attach-session -t %s\n' "${TMUX_BIN}" "${TMUX_SESSION}"
    printf 'F12 kills the session.\n'

    if ((NO_ATTACH)); then
        return 0
    fi

    if [[ -n "${TMUX:-}" ]]; then
        tmux_cmd switch-client -t "${TMUX_SESSION}:qbox"
    else
        tmux_cmd attach-session -t "${TMUX_SESSION}"
    fi
}

if [[ "${1:-}" == "--supervise" ]]; then
    supervise_run
    exit $?
fi

if [[ "${1:-}" == "--tail-log" ]]; then
    shift
    tail_log "$@"
    exit $?
fi

EXTRA_RUNNER_ARGS=()
while (($# > 0)); do
    case "$1" in
        --session)
            (($# >= 2)) || die "--session requires a value"
            TMUX_SESSION="$2"
            shift 2
            ;;
        --out-dir)
            (($# >= 2)) || die "--out-dir requires a value"
            OUT_DIR="$2"
            shift 2
            ;;
        --local-build-dir)
            (($# >= 2)) || die "--local-build-dir requires a value"
            LOCAL_BUILD_DIR="$2"
            shift 2
            ;;
        --qbox-build-dir)
            (($# >= 2)) || die "--qbox-build-dir requires a value"
            QBOX_BUILD_DIR="$2"
            shift 2
            ;;
        --conf)
            (($# >= 2)) || die "--conf requires a value"
            QBOX_CONF="$2"
            shift 2
            ;;
        --si-mode)
            (($# >= 2)) || die "--si-mode requires a value"
            SI_MODE="$2"
            shift 2
            ;;
        --timeout)
            (($# >= 2)) || die "--timeout requires a value"
            TIMEOUT="$2"
            shift 2
            ;;
        --jobs)
            (($# >= 2)) || die "--jobs requires a value"
            JOBS="$2"
            shift 2
            ;;
        --build)
            SKIP_BUILD=0
            shift
            ;;
        --skip-build)
            SKIP_BUILD=1
            shift
            ;;
        --post-login-probe)
            POST_LOGIN_PROBE=1
            shift
            ;;
        --no-post-login-probe)
            POST_LOGIN_PROBE=0
            shift
            ;;
        --keep-running-after-pass)
            KEEP_RUNNING_AFTER_PASS=1
            shift
            ;;
        --exit-after-pass)
            KEEP_RUNNING_AFTER_PASS=0
            shift
            ;;
        --rootfs-bootargs-profile)
            (($# >= 2)) || die "--rootfs-bootargs-profile requires a value"
            ROOTFS_BOOTARGS_PROFILE="$2"
            shift 2
            ;;
        --qbox-performance-preset)
            QBOX_PERFORMANCE_PRESET=1
            shift
            ;;
        --no-qbox-performance-preset)
            QBOX_PERFORMANCE_PRESET=0
            shift
            ;;
        --legacy-file-backed-sram)
            LEGACY_FILE_BACKED_SRAM=1
            shift
            ;;
        --range-limited-flash-dmi)
            RANGE_LIMITED_FLASH_DMI=1
            shift
            ;;
        --no-range-limited-flash-dmi)
            RANGE_LIMITED_FLASH_DMI=0
            shift
            ;;
        --cc3xx-stats)
            CC3XX_STATS=1
            shift
            ;;
        --cc3xx-stats-interval)
            (($# >= 2)) || die "--cc3xx-stats-interval requires a value"
            CC3XX_STATS_INTERVAL="$2"
            shift 2
            ;;
        --cc3xx-status-read-fastpath)
            CC3XX_STATUS_READ_FASTPATH=1
            shift
            ;;
        --cc3xx-qemu-native-backend)
            CC3XX_QEMU_NATIVE_BACKEND=1
            shift
            ;;
        --cc3xx-local-mmio-fastpath)
            CC3XX_LOCAL_MMIO_FASTPATH=1
            shift
            ;;
        --remotepass-dmi-cache)
            REMOTEPASS_DMI_CACHE=1
            shift
            ;;
        --netdev)
            (($# >= 2)) || die "--netdev requires a value"
            NETDEV="$2"
            shift 2
            ;;
        --no-attach)
            NO_ATTACH=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            EXTRA_RUNNER_ARGS=("$@")
            break
            ;;
        *)
            die "unknown argument: $1"
            ;;
    esac
done

start_tmux

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
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-}"
QBOX_PLATFORM_DIR="${QBOX_PLATFORM_DIR:-${ROOT_DIR}/tools/qbox-platform}"
QBOX_CONF="${QBOX_CONF:-${QBOX_PLATFORM_DIR}/platforms/apollo/apollo-qvp.lua}"
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
NETDEV="${NETDEV:-${QBOX_APOLLO_NETDEV:-}}"
SKIP_BUILD="${SKIP_BUILD:-1}"
POST_LOGIN_PROBE="${POST_LOGIN_PROBE:-1}"
KEEP_RUNNING_AFTER_PASS="${KEEP_RUNNING_AFTER_PASS:-1}"
TMUX_LAYOUT="${TMUX_LAYOUT:-tiled}"
NO_ATTACH=0
DRY_RUN=0

RUNNER_ARGS_FILE="${RUNNER_ARGS_FILE:-}"
REMOVED_ENV_OVERRIDES=()
REMOVED_ENV_NAMES=(
    "RSE_CPU_MODE"
    "REMOTEPASS_DMI_CACHE"
)

for name in "${REMOVED_ENV_NAMES[@]}"; do
    [[ -v ${name} ]] && REMOVED_ENV_OVERRIDES+=("${name}")
done

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
                       (default: <local-build-dir>/work/qbox-platform)
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
  --netdev SPEC        QEMU user-net specification forwarded to the AP virtio
                       net device, for example type=user,hostfwd=tcp::2223-:22
  --tmux-layout MODE   pane layout: tiled or fvp-like
                       (default: ${TMUX_LAYOUT})
  --no-attach          start tmux but do not attach
  --dry-run            print the run command and log layout only
  -h, --help           show this help

The default performance preset is expanded by the Python runner into the
QEMU-native CC3XX backend, RSE hotpaths, BL2 semantic accelerators, and RSE
fast-boot SRAM DMI/shared-memory mode. Use
--legacy-file-backed-sram for the older direct file-backed SRAM alias mode.

Environment overrides:
  PYTHON TMUX_BIN TMUX_SESSION OUT_DIR RUN_STAMP LOCAL_BUILD_DIR QBOX_PLATFORM_DIR
  QBOX_PLATFORM_BUILD_DIR QBOX_BUILD_DIR QBOX_CONF
  SI_MODE TIMEOUT JOBS SKIP_BUILD POST_LOGIN_PROBE KEEP_RUNNING_AFTER_PASS
  TMUX_LAYOUT
  ROOTFS_BOOTARGS_PROFILE
  QBOX_PERFORMANCE_PRESET LEGACY_FILE_BACKED_SRAM
  RANGE_LIMITED_FLASH_DMI CC3XX_STATS
  CC3XX_STATS_INTERVAL CC3XX_STATUS_READ_FASTPATH CC3XX_QEMU_NATIVE_BACKEND
  CC3XX_LOCAL_MMIO_FASTPATH
  NETDEV QBOX_APOLLO_NETDEV

Inside tmux:
  F12                  stop QBox and kill the whole session
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

reject_removed_option()
{
    die "unsupported removed option: --$1"
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

validate_tmux_layout()
{
    case "$1" in
        tiled|fvp-like) ;;
        *) die "invalid --tmux-layout: $1" ;;
    esac
}

reject_removed_environment_overrides()
{
    local name

    for name in "${REMOVED_ENV_OVERRIDES[@]}"; do
        die "unsupported removed environment override: ${name}"
    done
}

tmux_cmd()
{
    env -u TMUX "${TMUX_BIN}" "$@"
}

is_positive_int()
{
    [[ "${1:-}" =~ ^[0-9]+$ ]] && (($1 > 0))
}

detect_tmux_window_size_args()
{
    local -n _size_args="$1"
    _size_args=()

    local rows="${LINES:-}"
    local cols="${COLUMNS:-}"
    if ! is_positive_int "${rows}" || ! is_positive_int "${cols}"; then
        rows=""
        cols=""
        if [[ -t 0 ]]; then
            read -r rows cols < <(stty size 2>/dev/null || true)
        fi
    fi

    is_positive_int "${rows}" || return 0
    is_positive_int "${cols}" || return 0
    ((rows >= 24 && cols >= 80)) || return 0
    _size_args=(-x "${cols}" -y "${rows}")
}

rebalance_fvp_like_log_panes()
{
    (($# == 4)) || return 0

    local -a panes=("$@")
    local total_height=0
    local pane
    local height
    for pane in "${panes[@]}"; do
        height="$(tmux_cmd display-message -p -t "${pane}" '#{pane_height}' 2>/dev/null || true)"
        is_positive_int "${height}" || return 0
        total_height=$((total_height + height))
    done

    local target_height=$((total_height / ${#panes[@]}))
    is_positive_int "${target_height}" || return 0

    local i
    for ((i = 0; i < ${#panes[@]} - 1; i++)); do
        tmux_cmd resize-pane -t "${panes[$i]}" -y "${target_height}" >/dev/null 2>&1 || return 0
    done
}

install_fvp_like_rebalance_hooks()
{
    local hook_body
    hook_body="$(
        printf 'TMUX_BIN=%q exec %q --rebalance-fvp-like-log-panes' \
            "${TMUX_BIN}" "${SCRIPT_PATH}"
        printf ' %q' "$@"
    )"

    local hook_command
    hook_command="$(printf 'run-shell -b %q' "${hook_body}")"
    tmux_cmd set-hook -t "${TMUX_SESSION}" client-attached "${hook_command}" >/dev/null
    tmux_cmd set-hook -t "${TMUX_SESSION}" client-resized "${hook_command}" >/dev/null
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

    if [[ "${KEEP_RUNNING_AFTER_PASS:-0}" == "1" ]]; then
        printf 'Keep-running demo mode is active; this pane follows the log until F12 stops the session.\n\n'
        tail -n +1 -F "${log_path}" || true
    elif [[ -n "${pid}" ]] && tail_supports_pid; then
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
    rm -f "${OUT_DIR}/.qbox-run.done" "${OUT_DIR}/qbox-run.pid"
    printf 'running\n' >"${OUT_DIR}/qbox-run.status"
    quote_args "${cmd[@]}" >"${OUT_DIR}/qbox-run.cmd"

    printf 'QBox Apollo full-system tmux run\n'
    printf 'Logs: %s\n' "${OUT_DIR}"
    printf 'Runner log: %s\n' "${OUT_DIR}/qbox-runner.log"
    printf 'Command: %s\n\n' "$(quote_args "${cmd[@]}")"
    printf 'F12 stops QBox and kills the tmux session.\n\n'

    local status_file="${OUT_DIR}/qbox-run.status.tmp"
    rm -f "${status_file}"

    set +e
    if command -v stdbuf >/dev/null 2>&1; then
        stdbuf -oL -eL "${cmd[@]}" > >(tee -a "${OUT_DIR}/qbox-runner.log") 2>&1 &
    else
        "${cmd[@]}" > >(tee -a "${OUT_DIR}/qbox-runner.log") 2>&1 &
    fi
    local run_pid=$!
    printf '%s\n' "${run_pid}" >"${OUT_DIR}/qbox-run.pid"
    wait "${run_pid}"
    local pipeline_status=$?
    printf '%s\n' "${pipeline_status}" >"${status_file}"
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
    if [[ "${KEEP_RUNNING_AFTER_PASS}" == "1" && "${status}" == "0" ]]; then
        printf 'Boot pass condition was reached; QBox is still running for the interactive demo.\n' |
            tee -a "${OUT_DIR}/qbox-runner.log"
        printf 'Use F12 to stop QBox and kill the tmux session.\n' |
            tee -a "${OUT_DIR}/qbox-runner.log"
    fi
    printf 'Logs remain under: %s\n' "${OUT_DIR}" |
        tee -a "${OUT_DIR}/qbox-runner.log"
    printf 'Press Enter to close this pane, or F12 to kill the session.\n'
    read -r _ || true
    return "${status}"
}

child_pids()
{
    local parent="$1"

    if command -v pgrep >/dev/null 2>&1; then
        pgrep -P "${parent}" 2>/dev/null || true
        return 0
    fi

    ps -e -o pid= -o ppid= |
        awk -v parent="${parent}" '$2 == parent {print $1}'
}

process_tree_pids()
{
    local parent="$1"
    local child

    while IFS= read -r child; do
        [[ -n "${child}" ]] || continue
        process_tree_pids "${child}"
        printf '%s\n' "${child}"
    done < <(child_pids "${parent}")
}

process_tree_snapshot()
{
    local root_pid="$1"

    [[ "${root_pid}" =~ ^[0-9]+$ ]] || return 0
    kill -0 "${root_pid}" 2>/dev/null || return 0
    process_tree_pids "${root_pid}"
    printf '%s\n' "${root_pid}"
}

signal_pids()
{
    local signal="$1"
    shift
    local pid

    for pid in "$@"; do
        [[ "${pid}" =~ ^[0-9]+$ ]] || continue
        kill "-${signal}" "${pid}" 2>/dev/null || true
    done
}

wait_pids_exit()
{
    local timeout_s="$1"
    shift
    local deadline=$((SECONDS + timeout_s))
    local pid
    local alive

    while ((SECONDS < deadline)); do
        alive=0
        for pid in "$@"; do
            if [[ "${pid}" =~ ^[0-9]+$ ]] && kill -0 "${pid}" 2>/dev/null; then
                alive=1
                break
            fi
        done
        ((alive)) || return 0
        sleep 0.2
    done
    return 1
}

process_matches_out_dir()
{
    local pid="$1"
    local cmdline=""
    local env_lines=""
    local line
    local value

    [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
    [[ -r "/proc/${pid}/cmdline" && -r "/proc/${pid}/environ" ]] || return 1

    cmdline="$(tr '\0' '\n' <"/proc/${pid}/cmdline" 2>/dev/null || true)"
    case "${cmdline}" in
        *"/platforms-vp"*|*"platforms-vp"*) ;;
        *) return 1 ;;
    esac

    env_lines="$(tr '\0' '\n' <"/proc/${pid}/environ" 2>/dev/null || true)"
    while IFS= read -r line; do
        value="${line#*=}"
        case "${line}" in
            OUT_DIR=*)
                [[ "${value}" == "${OUT_DIR}" ]] && return 0
                ;;
            QBOX_*=*|RUNNER_ARGS_FILE=*)
                [[ "${value}" == "${OUT_DIR}" || "${value}" == "${OUT_DIR}/"* ]] &&
                    return 0
                ;;
        esac
    done <<<"${env_lines}"

    return 1
}

qbox_runtime_pids_for_out_dir()
{
    local proc
    local pid

    for proc in /proc/[0-9]*; do
        [[ -d "${proc}" ]] || continue
        pid="${proc##*/}"
        if process_matches_out_dir "${pid}"; then
            printf '%s\n' "${pid}"
        fi
    done | sort -n -u
}

qbox_runtime_pgids_for_pids()
{
    local pid
    local pgid

    for pid in "$@"; do
        [[ "${pid}" =~ ^[0-9]+$ ]] || continue
        pgid="$(ps -o pgid= -p "${pid}" 2>/dev/null | tr -d '[:space:]')"
        [[ "${pgid}" =~ ^[0-9]+$ ]] || continue
        printf '%s\n' "${pgid}"
    done | sort -n -u
}

signal_pgids()
{
    local signal="$1"
    shift
    local pgid

    for pgid in "$@"; do
        [[ "${pgid}" =~ ^[0-9]+$ ]] || continue
        kill "-${signal}" -"${pgid}" 2>/dev/null || true
    done
}

stop_session()
{
    (($# == 1)) || die "--stop-session requires SESSION"

    local session="$1"
    local pid_file="${OUT_DIR}/qbox-run.pid"
    local done_file="${OUT_DIR}/.qbox-run.done"
    local pid=""
    local -a pids=()
    local -a runtime_pids=()
    local -a runtime_pgids=()

    if [[ -s "${pid_file}" ]]; then
        pid="$(<"${pid_file}")"
    fi

    if [[ "${pid}" =~ ^[0-9]+$ ]] && kill -0 "${pid}" 2>/dev/null; then
        mapfile -t pids < <(process_tree_snapshot "${pid}")
    fi
    mapfile -t runtime_pids < <(qbox_runtime_pids_for_out_dir)
    mapfile -t runtime_pgids < <(qbox_runtime_pgids_for_pids "${runtime_pids[@]}")

    signal_pids INT "${pids[@]}"
    signal_pgids TERM "${runtime_pgids[@]}"
    wait_pids_exit 5 "${pids[@]}" "${runtime_pids[@]}" || {
        signal_pids TERM "${pids[@]}"
        signal_pgids TERM "${runtime_pgids[@]}"
    }
    wait_pids_exit 2 "${pids[@]}" "${runtime_pids[@]}" || {
        mapfile -t runtime_pids < <(qbox_runtime_pids_for_out_dir)
        mapfile -t runtime_pgids < <(qbox_runtime_pgids_for_pids "${runtime_pids[@]}")
        signal_pids KILL "${pids[@]}"
        signal_pgids KILL "${runtime_pgids[@]}"
    }

    : >"${done_file}"
    tmux_cmd kill-session -t "${session}" 2>/dev/null || true
}

print_dry_run()
{
    mapfile -t EXTRA_RUNNER_ARGS <"${RUNNER_ARGS_FILE}"
    local -a cmd=()
    runner_command cmd "${EXTRA_RUNNER_ARGS[@]}"
    local effective_cc3xx_qemu_native_backend="${CC3XX_QEMU_NATIVE_BACKEND}"
    local effective_cc3xx_local_mmio_fastpath="${CC3XX_LOCAL_MMIO_FASTPATH}"
    local explicit_sram_dmi=0
    local explicit_legacy_file_backed_sram="${LEGACY_FILE_BACKED_SRAM}"
    local rse_fast_boot_mode="disabled"
    local rse_fast_boot_summary="disabled: no SRAM fast-boot mode selected"
    local arg

    if [[ "${QBOX_PERFORMANCE_PRESET}" == "1" ]]; then
        effective_cc3xx_qemu_native_backend=1
        effective_cc3xx_local_mmio_fastpath=1
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
  effective_cc3xx_qemu_native_backend: ${effective_cc3xx_qemu_native_backend}
  effective_cc3xx_local_mmio_fastpath: ${effective_cc3xx_local_mmio_fastpath}
  netdev: ${NETDEV:-default}
  tmux_layout: ${TMUX_LAYOUT}
  out_dir: ${OUT_DIR}
  qbox_platform_dir: ${QBOX_PLATFORM_DIR}
  qbox_conf: ${QBOX_CONF}
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

is_terminal_status_response_line()
{
    (($# == 1)) || die "is_terminal_status_response_line requires LINE"

    local clean_line="${1//$'\033'/}"

    [[ "${clean_line}" =~ ^\[[0-9]{1,5}\;[0-9]{1,5}R$ ]]
}

write_fifo_line()
{
    (($# == 2)) || die "write_fifo_line requires FIFO_PATH LINE"

    local fifo_path="$1"
    local line="$2"

    if command -v timeout >/dev/null 2>&1; then
        # shellcheck disable=SC2016
        timeout 1 bash -c 'printf "%s\n" "$1" >"$2"' _ "${line}" "${fifo_path}"
    else
        printf '%s\n' "${line}" >"${fifo_path}"
    fi
}

interactive_primary_console()
{
    (($# == 3)) || die "--primary-console requires DOMAIN TITLE LOG_PATH"

    local domain="$1"
    local title="$2"
    local log_path="$3"
    local fifo_path="${OUT_DIR}/primary-uart-input.fifo"
    local tail_pid=""
    local line
    local fifo_ready=0

    cleanup_primary_console()
    {
        local status="${1:-0}"

        trap - EXIT INT TERM HUP
        if [[ -n "${tail_pid}" ]]; then
            kill "${tail_pid}" 2>/dev/null || true
            wait "${tail_pid}" 2>/dev/null || true
        fi
        exit "${status}"
    }

    mkdir -p "$(dirname "${log_path}")"
    : >>"${log_path}"

    printf 'Subsystem: %s\n' "${title}"
    printf 'Domain: %s\n' "${domain}"
    printf 'Log: %s\n' "${log_path}"
    printf 'UART input FIFO: %s\n\n' "${fifo_path}"

    tail -n +1 -F "${log_path}" &
    tail_pid=$!
    trap 'cleanup_primary_console $?' EXIT
    trap 'cleanup_primary_console 130' INT
    trap 'cleanup_primary_console 143' TERM HUP

    printf '\nWaiting for primary UART input FIFO. F12 stops QBox.\n'
    while true; do
        if [[ -p "${fifo_path}" && "${fifo_ready}" == 0 ]]; then
            printf '\nPrimary UART is interactive. Type commands here; F12 stops QBox.\n'
            fifo_ready=1
        elif [[ ! -p "${fifo_path}" && "${fifo_ready}" == 1 ]]; then
            printf '\nPrimary UART input FIFO is unavailable; waiting for it to return.\n'
            fifo_ready=0
        fi

        if IFS= read -r -t 0.2 line; then
            if [[ ! -p "${fifo_path}" ]]; then
                printf 'UART input FIFO is not ready; dropped input line.\n'
                continue
            fi
            if is_terminal_status_response_line "${line}"; then
                continue
            fi
            write_fifo_line "${fifo_path}" "${line}" ||
                printf 'UART input FIFO write timed out; dropped input line.\n'
        fi
    done

    cleanup_primary_console 0
}

start_log_pane()
{
    local domain="$1"
    local file="$2"
    local title="$3"
    shift 3
    local log_path="${OUT_DIR}/${file}"
    local pane_body
    local pane_id
    local -a split_args=("$@")

    if [[ "${domain}" == "primary_console" ]]; then
        pane_body=$(
            printf 'cd %q || exit 1; ' "${ROOT_DIR}"
            printf 'OUT_DIR=%q exec %q --primary-console %q %q %q' \
                "${OUT_DIR}" "${SCRIPT_PATH}" "${domain}" "${title}" "${log_path}"
        )
    else
        pane_body=$(
            printf 'cd %q || exit 1; ' "${ROOT_DIR}"
            printf 'OUT_DIR=%q KEEP_RUNNING_AFTER_PASS=%q exec %q --tail-log %q %q %q' \
                "${OUT_DIR}" "${KEEP_RUNNING_AFTER_PASS}" "${SCRIPT_PATH}" \
                "${domain}" "${title}" "${log_path}"
        )
    fi

    if ((${#split_args[@]} == 0)); then
        split_args=(-t "${TMUX_SESSION}:qbox")
    fi

    pane_id="$(tmux_cmd split-window -P -F '#{pane_id}' "${split_args[@]}" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T "${domain}"
    if [[ "${TMUX_LAYOUT}" == "tiled" ]]; then
        tmux_cmd select-layout -t "${TMUX_SESSION}:qbox" tiled >/dev/null
    fi
    START_LOG_PANE_ID="${pane_id}"
}

start_domain_log_pane()
{
    local requested="$1"
    shift
    local domain
    local file
    local title

    while IFS=: read -r domain file title; do
        if [[ "${domain}" == "${requested}" ]]; then
            start_log_pane "${domain}" "${file}" "${title}" "$@"
            return 0
        fi
    done < <(known_logs)

    die "unknown log domain: ${requested}"
}

start_tiled_log_panes()
{
    local domain
    local file
    local title

    while IFS=: read -r domain file title; do
        start_log_pane "${domain}" "${file}" "${title}"
    done < <(known_logs)
}

start_fvp_like_log_panes()
{
    local primary_pane_id
    local rse_pane_id
    local si0_pane_id
    local si1_pane_id
    local secure_pane_id

    start_domain_log_pane primary_console -v -b -l 70% -t "${RUNNER_PANE_ID}"
    primary_pane_id="${START_LOG_PANE_ID}"
    start_domain_log_pane rse -h -l 40% -t "${primary_pane_id}"
    rse_pane_id="${START_LOG_PANE_ID}"
    start_domain_log_pane safety_island_cl0 -v -l 75% -t "${rse_pane_id}"
    si0_pane_id="${START_LOG_PANE_ID}"
    start_domain_log_pane safety_island_cl1 -v -l 67% -t "${si0_pane_id}"
    si1_pane_id="${START_LOG_PANE_ID}"
    start_domain_log_pane secure_console -v -l 50% -t "${si1_pane_id}"
    secure_pane_id="${START_LOG_PANE_ID}"
    start_domain_log_pane platform -h -l 50% -t "${RUNNER_PANE_ID}"
    rebalance_fvp_like_log_panes "${rse_pane_id}" "${si0_pane_id}" "${si1_pane_id}" "${secure_pane_id}"
    install_fvp_like_rebalance_hooks "${rse_pane_id}" "${si0_pane_id}" "${si1_pane_id}" "${secure_pane_id}"
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
    validate_bool "SKIP_BUILD" "${SKIP_BUILD}"
    validate_bool "POST_LOGIN_PROBE" "${POST_LOGIN_PROBE}"
    validate_bool "KEEP_RUNNING_AFTER_PASS" "${KEEP_RUNNING_AFTER_PASS}"
    validate_tmux_layout "${TMUX_LAYOUT}"
    require_command "${TMUX_BIN}"
    require_command "${PYTHON_BIN}"

    [[ -f "${QBOX_CONF}" ]] || die "QBox config not found: ${QBOX_CONF}"
    [[ -d "${LOCAL_BUILD_DIR}" ]] ||
        die "local build directory not found: ${LOCAL_BUILD_DIR}. Run ./local-build.sh build first."

    ROOT_DIR="$(abspath "${ROOT_DIR}")"
    SCRIPT_PATH="$(abspath "${SCRIPT_PATH}")"
    OUT_DIR="$(abspath "${OUT_DIR}")"
    LOCAL_BUILD_DIR="$(abspath "${LOCAL_BUILD_DIR}")"
    QBOX_PLATFORM_DIR="$(abspath "${QBOX_PLATFORM_DIR}")"
    if [[ -z "${QBOX_PLATFORM_BUILD_DIR}" ]]; then
        if [[ -n "${QBOX_BUILD_DIR}" ]]; then
            QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
        else
            QBOX_PLATFORM_BUILD_DIR="${LOCAL_BUILD_DIR}/work/qbox-platform"
        fi
    fi
    QBOX_PLATFORM_BUILD_DIR="$(abspath "${QBOX_PLATFORM_BUILD_DIR}")"
    QBOX_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR}"
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
        printf 'QBOX_PLATFORM_DIR=%q QBOX_PLATFORM_BUILD_DIR=%q ' \
            "${QBOX_PLATFORM_DIR}" "${QBOX_PLATFORM_BUILD_DIR}"
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
        if [[ -n "${NETDEV}" ]]; then
            printf 'NETDEV=%q QBOX_APOLLO_NETDEV=%q ' \
                "${NETDEV}" "${NETDEV}"
        fi
        if [[ -n "${QBOX_APOLLO_NUM_CPUS:-}" ]]; then
            printf 'QBOX_APOLLO_NUM_CPUS=%q ' "${QBOX_APOLLO_NUM_CPUS}"
        fi
        printf 'SKIP_BUILD=%q POST_LOGIN_PROBE=%q ' \
            "${SKIP_BUILD}" "${POST_LOGIN_PROBE}"
        printf 'KEEP_RUNNING_AFTER_PASS=%q ' "${KEEP_RUNNING_AFTER_PASS}"
        printf 'TMUX_LAYOUT=%q ' "${TMUX_LAYOUT}"
        printf 'RUNNER_ARGS_FILE=%q exec %q --supervise' \
            "${RUNNER_ARGS_FILE}" "${SCRIPT_PATH}"
    )

    local -a new_session_size_args=()
    detect_tmux_window_size_args new_session_size_args

    local runner_pane_id
    runner_pane_id="$(tmux_cmd new-session -d "${new_session_size_args[@]}" -P -F '#{pane_id}' -s "${TMUX_SESSION}" -n qbox bash -lc "${supervisor_body}")"
    RUNNER_PANE_ID="${runner_pane_id}"
    tmux_cmd set-option -t "${TMUX_SESSION}" mouse on
    tmux_cmd set-window-option -t "${TMUX_SESSION}:qbox" pane-border-status top
    tmux_cmd set-window-option -t "${TMUX_SESSION}:qbox" pane-border-format '#{pane_index}: #{pane_title}'
    tmux_cmd select-pane -t "${runner_pane_id}" -T qbox-runner
    local stop_body
    stop_body=$(
        printf 'OUT_DIR=%q TMUX_BIN=%q exec %q --stop-session %q' \
            "${OUT_DIR}" "${TMUX_BIN}" "${SCRIPT_PATH}" "${TMUX_SESSION}"
    )
    tmux_cmd bind-key -n F12 run-shell -b "${stop_body}"

    if [[ "${TMUX_LAYOUT}" == "fvp-like" ]]; then
        start_fvp_like_log_panes
    else
        start_tiled_log_panes
    fi
    tmux_cmd select-pane -t "${runner_pane_id}"
    if [[ "${TMUX_LAYOUT}" == "tiled" ]]; then
        tmux_cmd select-layout -t "${TMUX_SESSION}:qbox" tiled >/dev/null
    fi

    printf 'started tmux session: %s\n' "${TMUX_SESSION}"
    printf 'logs: %s\n' "${OUT_DIR}"
    printf 'attach command: %s attach-session -t %s\n' "${TMUX_BIN}" "${TMUX_SESSION}"
    printf 'F12 stops QBox and kills the session.\n'

    if ((NO_ATTACH)); then
        return 0
    fi

    if [[ -n "${TMUX:-}" ]]; then
        tmux_cmd switch-client -t "${TMUX_SESSION}:qbox"
    else
        tmux_cmd attach-session -t "${TMUX_SESSION}"
    fi
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

reject_removed_environment_overrides

if [[ "${1:-}" == "--supervise" ]]; then
    supervise_run
    exit $?
fi

if [[ "${1:-}" == "--tail-log" ]]; then
    shift
    tail_log "$@"
    exit $?
fi

if [[ "${1:-}" == "--primary-console" ]]; then
    shift
    interactive_primary_console "$@"
    # shellcheck disable=SC2317
    exit $?
fi

if [[ "${1:-}" == "--stop-session" ]]; then
    shift
    stop_session "$@"
    exit $?
fi

if [[ "${1:-}" == "--rebalance-fvp-like-log-panes" ]]; then
    shift
    rebalance_fvp_like_log_panes "$@"
    exit 0
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
            QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
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
        --rse-cpu-mode|--rse-cpu-mode=*)
            reject_removed_option "rse-cpu-mode"
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
        --remotepass-dmi-cache|--remotepass-dmi-cache=*)
            reject_removed_option "remotepass-dmi-cache"
            ;;
        --netdev)
            (($# >= 2)) || die "--netdev requires a value"
            NETDEV="$2"
            shift 2
            ;;
        --tmux-layout)
            (($# >= 2)) || die "--tmux-layout requires a value"
            TMUX_LAYOUT="$2"
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

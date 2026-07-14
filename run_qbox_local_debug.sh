#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_QBOX_LOCAL_SH="${RUN_QBOX_LOCAL_SH:-${ROOT_DIR}/run_qbox_local.sh}"
TMUX_BIN="${TMUX_BIN:-tmux}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-apollo-qvp}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
SESSION="apollo-qbox-debug-${RUN_STAMP}"
OUT_DIR="${ROOT_DIR}/build/qbox-apollo-fvp/debug-${RUN_STAMP}"
DEBUG_DIR=""
MANIFEST="${LOCAL_DEBUG_MANIFEST:-}"
NO_ATTACH=0
VSCODE=0
DRY_RUN=0
AP_EARLY_ATTACH=0
FIRMWARE_EARLY_ATTACH=0
RUNNER_ARGS=()
CHILD_ARGS=()

HOST_ENDPOINT="127.0.0.1:12339"
RSE_ENDPOINT="127.0.0.1:12340"
SI0_ENDPOINT="127.0.0.1:12341"
SI1_ENDPOINT="127.0.0.1:12342"
AP_ENDPOINT="127.0.0.1:12343"
AP_SAFE_MARKER="PFDI: OoR tests on core 3 succeeded."

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

usage()
{
    cat <<EOF
Usage: ./run_qbox_local_debug.sh [options] [-- extra-qbox-runner-options]

Launch the normal Apollo QBox tmux view with GDB in the interactive pane.

Options:
  --session NAME          tmux session name
  --out-dir DIR           runtime evidence directory
  --local-build-dir DIR   local Apollo build directory
  --vscode                leave GDB endpoints for VS Code instead of CLI panes
  --ap-early-attach       attach AP GDB before TF-A starts (CLI only)
  --firmware-early-attach attach RSE/SI GDB before firmware starts (CLI only)
  --no-attach             start tmux without attaching this terminal
  --dry-run               print the underlying QBox launch plan
  --help

The fixed endpoints are host 12339, RSE 12340, SI0 12341, SI1 12342,
and AP 12343 on 127.0.0.1.
EOF
}

abspath()
{
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "${PWD}" "$1" ;;
    esac
}

port_in_use()
{
    local port="$1"
    ss -H -ltn 2>/dev/null | awk '{print $4}' |
        grep -Eq "(^|[:.])${port}$|\\]:${port}$"
}

gdb_body()
{
    local component="$1"
    local endpoint="$2"
    local resume="${3:-0}"
    local wait_log="${4:-}"
    printf 'cd %q || exit 1; ' "${ROOT_DIR}"
    if [[ -n "${wait_log}" ]]; then
        printf '%q --wait-log-marker-only %q %q --wait-seconds 600 || exit 1; ' \
            "${ROOT_DIR}/scripts/debug/run_local_gdb.py" \
            "${wait_log}" "${AP_SAFE_MARKER}"
    fi
    printf 'exec %q --manifest %q %q --remote %q --wait-remote' \
        "${ROOT_DIR}/scripts/debug/run_local_gdb.py" "${MANIFEST}" \
        "${component}" "${endpoint}"
    ((resume)) && printf ' --continue'
}

configure_cli_panes()
{
    local ap_wait_log=""
    local firmware_wait_log=""
    if ((AP_EARLY_ATTACH == 0)); then
        ap_wait_log="${OUT_DIR}/qbox-secure-console.log"
    fi
    if ((FIRMWARE_EARLY_ATTACH == 0)); then
        firmware_wait_log="${OUT_DIR}/qbox-secure-console.log"
    fi
    local shell_pane
    shell_pane="$(${TMUX_BIN} list-panes -t "${SESSION}:qbox" \
        -F '#{pane_id} #{pane_title}' | awk '$2 == "shell" {print $1; exit}')"
    [[ -n "${shell_pane}" ]] || die "interactive shell pane was not found"

    "${TMUX_BIN}" respawn-pane -k -t "${shell_pane}" \
        bash -lc "$(gdb_body qbox-host "${HOST_ENDPOINT}" 1)"
    "${TMUX_BIN}" select-pane -t "${shell_pane}" -T gdb-host

    local pane
    pane="$(${TMUX_BIN} new-window -d -P -F '#{pane_id}' \
        -t "${SESSION}" -n gdb-targets \
        bash -lc "$(gdb_body domain-rse "${RSE_ENDPOINT}" 0 "${firmware_wait_log}")")"
    "${TMUX_BIN}" select-pane -t "${pane}" -T gdb-rse
    pane="$(${TMUX_BIN} split-window -d -P -F '#{pane_id}' -t "${pane}" \
        bash -lc "$(gdb_body domain-si0 "${SI0_ENDPOINT}" 0 "${firmware_wait_log}")")"
    "${TMUX_BIN}" select-pane -t "${pane}" -T gdb-si0
    pane="$(${TMUX_BIN} split-window -d -P -F '#{pane_id}' -t "${pane}" \
        bash -lc "$(gdb_body domain-si1 "${SI1_ENDPOINT}" 0 "${firmware_wait_log}")")"
    "${TMUX_BIN}" select-pane -t "${pane}" -T gdb-si1
    pane="$(${TMUX_BIN} split-window -d -P -F '#{pane_id}' -t "${pane}" \
        bash -lc "$(gdb_body domain-ap "${AP_ENDPOINT}" 0 "${ap_wait_log}")")"
    "${TMUX_BIN}" select-pane -t "${pane}" -T gdb-ap
    "${TMUX_BIN}" select-layout -t "${SESSION}:gdb-targets" tiled >/dev/null
}

while (($#)); do
    case "$1" in
        --session)
            (($# >= 2)) || die "--session requires a value"
            SESSION="$2"
            shift 2
            ;;
        --out-dir)
            (($# >= 2)) || die "--out-dir requires a value"
            OUT_DIR="$(abspath "$2")"
            shift 2
            ;;
        --local-build-dir)
            (($# >= 2)) || die "--local-build-dir requires a value"
            LOCAL_BUILD_DIR="$(abspath "$2")"
            shift 2
            ;;
        --vscode)
            VSCODE=1
            NO_ATTACH=1
            shift
            ;;
        --ap-early-attach)
            AP_EARLY_ATTACH=1
            shift
            ;;
        --firmware-early-attach)
            FIRMWARE_EARLY_ATTACH=1
            shift
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
            CHILD_ARGS=("$@")
            break
            ;;
        *)
            RUNNER_ARGS+=("$1")
            shift
            ;;
    esac
done

DEBUG_DIR="${LOCAL_BUILD_DIR}/debug"
[[ -n "${MANIFEST}" ]] || MANIFEST="${DEBUG_DIR}/symbols.json"
if [[ "${LOCAL_DEBUG_SKIP_MANIFEST:-0}" != "1" ]]; then
    python3 "${ROOT_DIR}/scripts/setup/setup_local_debug_env.py" \
        --local-build-dir "${LOCAL_BUILD_DIR}" --out-dir "${DEBUG_DIR}"
    for script in qbox-host domain-rse domain-si0 domain-si1 domain-ap; do
        [[ -f "${DEBUG_DIR}/gdb/${script}.gdb" ]] ||
            die "missing generated GDB script: ${script}.gdb"
    done
fi

if ((DRY_RUN == 0)) && [[ "${LOCAL_DEBUG_SKIP_PORT_CHECK:-0}" != "1" ]]; then
    command -v ss >/dev/null 2>&1 || die "ss is required"
    for port in 12339 12340 12341 12342 12343; do
        port_in_use "${port}" && die "GDB port is already in use: ${port}"
    done
fi

export QBOX_HOST_GDB_EXEC="${ROOT_DIR}/scripts/debug/gdbserver_gdb_wrapper.sh"
export QBOX_HOST_GDBSERVER_ENDPOINT="${HOST_ENDPOINT}"

command=(
    "${RUN_QBOX_LOCAL_SH}"
    --session "${SESSION}"
    --out-dir "${OUT_DIR}"
    --local-build-dir "${LOCAL_BUILD_DIR}"
    --no-attach
    "${RUNNER_ARGS[@]}"
)
((DRY_RUN)) && command+=(--dry-run)
command+=(
    --
    --host-gdb-script "${DEBUG_DIR}/gdb/qbox-host.gdb"
    --ignore-fail-patterns
    --platform-param "platform.rse_cpu_pass.cpu_0.gdb_port=12340"
    --platform-param "platform.si_cl0_cpu_0.gdb_port=12341"
    --platform-param "platform.si_cl1_cpu_0.gdb_port=12342"
    --platform-param "platform.ap_cpu_0.gdb_port=12343"
    "${CHILD_ARGS[@]}"
)
"${command[@]}"

if ((DRY_RUN)); then
    exit 0
fi
if ((VSCODE)); then
    "${ROOT_DIR}/scripts/debug/run_local_gdb.py" \
        --wait-remote-only "${HOST_ENDPOINT}" --wait-seconds 600
    printf 'QBox debug servers started for VS Code in tmux session %s.\n' "${SESSION}"
elif ((NO_ATTACH)); then
    configure_cli_panes
else
    configure_cli_panes
    exec "${TMUX_BIN}" attach-session -t "${SESSION}"
fi

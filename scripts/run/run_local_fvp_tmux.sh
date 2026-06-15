#!/usr/bin/env bash
#
# Run the locally built Apollo FVP image in a tmux session.
#
# The FVP stdout pane is kept for model/runtime messages. Each known subsystem
# UART is opened in its own tmux pane and mirrored to a log file so the same run
# can be used both for a user-facing demo and for file-backed agent analysis.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/$(basename "${BASH_SOURCE[0]}")"

MACHINE="${MACHINE:-apollo-fvp}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-${MACHINE}}"
DEPLOY_DIR="${DEPLOY_DIR:-${LOCAL_BUILD_DIR}/deploy}"
SDK_DIR="${SDK_DIR:-${ROOT_DIR}/build/local-sdk}"
RUNFVP_BIN="${RUNFVP_BIN:-${ROOT_DIR}/layers/meta-arm/scripts/runfvp}"
FVP_CONF="${FVP_CONF:-${DEPLOY_DIR}/${MACHINE}-local.fvpconf}"
TMUX_BIN="${TMUX_BIN:-tmux}"

RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
TMUX_SESSION="${TMUX_SESSION:-apollo-fvp-local-${RUN_STAMP}}"
OUT_DIR="${OUT_DIR:-${LOCAL_BUILD_DIR}/tmux-run/${RUN_STAMP}}"
NO_ATTACH=0
DRY_RUN=0

usage()
{
    cat <<EOF
Usage: scripts/run/run_local_fvp_tmux.sh [options] [-- extra FVP args]

Run the local Apollo FVP build in tmux and mirror subsystem UARTs to files.

Options:
  --session NAME       tmux session name (default: ${TMUX_SESSION})
  --out-dir PATH       log/output directory (default: ${OUT_DIR})
  --fvpconf PATH       local FVP config (default: ${FVP_CONF})
  --runfvp-bin PATH    runfvp executable (default: ${RUNFVP_BIN})
  --no-attach          start tmux but do not attach
  --dry-run            print the run command and log layout only
  -h, --help           show this help

Environment overrides:
  MACHINE LOCAL_BUILD_DIR DEPLOY_DIR SDK_DIR RUNFVP_BIN FVP_CONF
  TMUX_BIN TMUX_SESSION OUT_DIR RUN_STAMP

Inside tmux:
  F12                  kill the whole session
  mouse                enabled

Subsystem UART logs:
  rse                  RSE / TF-M
  safety_island_cl0    Safety Island CL0 / SCP-firmware
  safety_island_cl1    Safety Island CL1 / Zephyr
  tf_a                 TF-A / secure-world AP console
  u_boot_linux         U-Boot / Linux console
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

source_sdk_if_present()
{
    local env_file
    env_file="$(first_existing_glob "${SDK_DIR}/environment-setup-*" || true)"
    [[ -n "${env_file}" ]] || return 0

    printf 'Sourcing SDK environment: %s\n' "${env_file}"
    set +u
    # shellcheck disable=SC1090
    source "${env_file}"
    set -u
}

prepare_auto_fvp_args()
{
    local fvpconf="$1"
    local out_dir="$2"
    local args_file="$3"
    local layout_file="$4"

    python3 - "$fvpconf" "$out_dir" "$args_file" "$layout_file" <<'PY'
import json
import pathlib
import shutil
import sys

fvpconf, out_dir, args_file, layout_file = [pathlib.Path(p) for p in sys.argv[1:]]
cfg = json.loads(fvpconf.read_text(encoding="utf-8"))
args = []

for terminal_path in sorted(cfg.get("terminals", {})):
    args.extend(["--parameter", f"{terminal_path}.start_telnet=1"])

image_dir = out_dir / "writable-images"
for key, value in sorted(cfg.get("parameters", {}).items()):
    if not key.endswith(".fnameWrite") or not value:
        continue
    src = pathlib.Path(value)
    if not src.exists():
        continue
    image_dir.mkdir(parents=True, exist_ok=True)
    dst = image_dir / src.name
    shutil.copy2(src, dst)
    args.extend(["--parameter", f"{key}={dst}"])

args_file.write_text("".join(f"{arg}\n" for arg in args), encoding="utf-8")

with layout_file.open("w", encoding="utf-8") as f:
    f.write("terminal_path\tterminal\tlabel\n")
    for terminal_path, label in sorted(cfg.get("terminals", {}).items()):
        terminal = terminal_path.rsplit(".", 1)[-1]
        f.write(f"{terminal_path}\t{terminal}\t{label}\n")
PY
}

terminal_domain()
{
    case "$1" in
        terminal_uart) printf 'rse\n' ;;
        terminal_uart_si_cluster0) printf 'safety_island_cl0\n' ;;
        terminal_uart_si_cluster1) printf 'safety_island_cl1\n' ;;
        terminal_sec_uart) printf 'tf_a\n' ;;
        terminal_ns_uart0) printf 'u_boot_linux\n' ;;
        *) return 1 ;;
    esac
}

terminal_title()
{
    case "$1" in
        terminal_uart) printf 'RSE / TF-M\n' ;;
        terminal_uart_si_cluster0) printf 'Safety Island CL0 / SCP-firmware\n' ;;
        terminal_uart_si_cluster1) printf 'Safety Island CL1 / Zephyr\n' ;;
        terminal_sec_uart) printf 'TF-A / secure-world AP\n' ;;
        terminal_ns_uart0) printf 'U-Boot / Linux\n' ;;
        *) return 1 ;;
    esac
}

tmux_cmd()
{
    env -u TMUX "${TMUX_BIN}" "$@"
}

start_uart_pane()
{
    local term="$1"
    local port="$2"
    local domain
    local title
    local marker
    local log_path
    local pane_body
    local pane_id

    domain="$(terminal_domain "${term}")" || return 0
    title="$(terminal_title "${term}")" || return 0

    marker="${OUT_DIR}/.pane-${domain}"
    [[ ! -e "${marker}" ]] || return 0
    : >"${marker}"

    log_path="${OUT_DIR}/uarts/${domain}.log"
    mkdir -p "$(dirname "${log_path}")"
    : >"${log_path}"
    printf '%s\t%s\t%s\t%s\n' "${domain}" "${term}" "${port}" "${log_path}" >>"${OUT_DIR}/ports.tsv"

    printf 'UART %s is listening on port %s; log: %s\n' "${domain}" "${port}" "${log_path}" |
        tee -a "${OUT_DIR}/tmux-supervisor.log"

    printf -v pane_body \
        'printf "Subsystem: %%s\nUART: %%s\nPort: %%s\nLog: %%s\n\n" %q %q %q %q; if command -v stdbuf >/dev/null 2>&1; then stdbuf -o0 -e0 telnet localhost %q 2>&1 | tee -a %q; else telnet localhost %q 2>&1 | tee -a %q; fi; printf "\nUART pane exited. Press Enter to close this pane.\n"; read -r _' \
        "${title}" "${term}" "${port}" "${log_path}" "${port}" "${log_path}" "${port}" "${log_path}"

    pane_id="$(tmux_cmd split-window -P -F '#{pane_id}' -t "${TMUX_SESSION}:fvp" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T "${domain}"
    tmux_cmd select-layout -t "${TMUX_SESSION}:fvp" tiled >/dev/null
}

supervise_run()
{
    source_sdk_if_present
    require_command telnet

    mkdir -p "${OUT_DIR}/uarts"
    : >"${OUT_DIR}/ports.tsv"
    printf 'domain\tterminal\tport\tlog\n' >"${OUT_DIR}/ports.tsv"
    : >"${OUT_DIR}/tmux-supervisor.log"

    mapfile -t EXTRA_ARGS <"${EXTRA_ARGS_FILE}"
    local -a cmd=("${RUNFVP_BIN}" "-t" "none" "${FVP_CONF}")
    if ((${#EXTRA_ARGS[@]} > 0)); then
        cmd+=("--" "${EXTRA_ARGS[@]}")
    fi

    quote_args "${cmd[@]}" >"${OUT_DIR}/runfvp.cmd"
    printf '\nLogs: %s\n' "${OUT_DIR}"
    printf 'FVP stdout log: %s\n' "${OUT_DIR}/fvp_stdout.log"
    printf 'UART logs: %s/uarts\n' "${OUT_DIR}"
    printf 'Command: %s\n\n' "$(quote_args "${cmd[@]}")"
    printf 'Waiting for FVP UART ports...\n\n'

    local line
    local term
    local port
    set +e
    local status
    if command -v stdbuf >/dev/null 2>&1; then
        stdbuf -oL -eL "${cmd[@]}" 2>&1 | while IFS= read -r line; do
            printf '%s\n' "${line}" | tee -a "${OUT_DIR}/fvp_stdout.log"
            if [[ "${line}" =~ (terminal_[A-Za-z0-9_]+):\ Listening\ for\ serial\ connection\ on\ port\ ([0-9]+) ]]; then
                term="${BASH_REMATCH[1]}"
                port="${BASH_REMATCH[2]}"
                start_uart_pane "${term}" "${port}"
            fi
        done
        status=${PIPESTATUS[0]}
    else
        "${cmd[@]}" 2>&1 | while IFS= read -r line; do
            printf '%s\n' "${line}" | tee -a "${OUT_DIR}/fvp_stdout.log"
            if [[ "${line}" =~ (terminal_[A-Za-z0-9_]+):\ Listening\ for\ serial\ connection\ on\ port\ ([0-9]+) ]]; then
                term="${BASH_REMATCH[1]}"
                port="${BASH_REMATCH[2]}"
                start_uart_pane "${term}" "${port}"
            fi
        done
        status=${PIPESTATUS[0]}
    fi
    set -e

    printf '\nrunfvp exited with status %s.\n' "${status}" | tee -a "${OUT_DIR}/tmux-supervisor.log"
    printf 'Logs remain under: %s\n' "${OUT_DIR}" | tee -a "${OUT_DIR}/tmux-supervisor.log"
    printf 'Press Enter to close this pane, or F12 to kill the session.\n'
    read -r _ || true
    return "${status}"
}

print_dry_run()
{
    mapfile -t EXTRA_ARGS <"${EXTRA_ARGS_FILE}"
    local -a cmd=("${RUNFVP_BIN}" "-t" "none" "${FVP_CONF}")
    if ((${#EXTRA_ARGS[@]} > 0)); then
        cmd+=("--" "${EXTRA_ARGS[@]}")
    fi

    cat <<EOF
local Apollo FVP tmux run
  session: ${TMUX_SESSION}
  fvpconf: ${FVP_CONF}
  out_dir: ${OUT_DIR}
  command: $(quote_args "${cmd[@]}")

file-backed UART logs
  ${OUT_DIR}/uarts/rse.log
  ${OUT_DIR}/uarts/safety_island_cl0.log
  ${OUT_DIR}/uarts/safety_island_cl1.log
  ${OUT_DIR}/uarts/tf_a.log
  ${OUT_DIR}/uarts/u_boot_linux.log
EOF
}

start_tmux()
{
    validate_tmux_name "${TMUX_SESSION}"
    require_command "${TMUX_BIN}"
    require_command python3

    [[ -x "${RUNFVP_BIN}" ]] || die "runfvp not executable: ${RUNFVP_BIN}"
    [[ -f "${FVP_CONF}" ]] ||
        die "FVP config not found: ${FVP_CONF}. Run ./local-build.sh build first."

    FVP_CONF="$(abspath "${FVP_CONF}")"
    OUT_DIR="$(abspath "${OUT_DIR}")"
    RUNFVP_BIN="$(abspath "${RUNFVP_BIN}")"
    SDK_DIR="$(abspath "${SDK_DIR}")"
    mkdir -p "${OUT_DIR}/uarts"

    local auto_args_file="${OUT_DIR}/auto-fvp-args.txt"
    local extra_args_file="${OUT_DIR}/extra-fvp-args.txt"
    local layout_file="${OUT_DIR}/terminal-layout.tsv"
    prepare_auto_fvp_args "${FVP_CONF}" "${OUT_DIR}" "${auto_args_file}" "${layout_file}"

    mapfile -t AUTO_ARGS <"${auto_args_file}"
    : >"${extra_args_file}"
    local arg
    for arg in "${AUTO_ARGS[@]}" "${EXTRA_FVP_ARGS[@]}"; do
        printf '%s\n' "${arg}" >>"${extra_args_file}"
    done
    EXTRA_ARGS_FILE="${extra_args_file}"

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
        printf 'ROOT_DIR=%q MACHINE=%q LOCAL_BUILD_DIR=%q DEPLOY_DIR=%q SDK_DIR=%q ' \
            "${ROOT_DIR}" "${MACHINE}" "${LOCAL_BUILD_DIR}" "${DEPLOY_DIR}" "${SDK_DIR}"
        printf 'RUNFVP_BIN=%q FVP_CONF=%q OUT_DIR=%q EXTRA_ARGS_FILE=%q ' \
            "${RUNFVP_BIN}" "${FVP_CONF}" "${OUT_DIR}" "${EXTRA_ARGS_FILE}"
        printf 'TMUX_BIN=%q TMUX_SESSION=%q ' "${TMUX_BIN}" "${TMUX_SESSION}"
        printf 'exec %q --supervise' "${SCRIPT_PATH}"
    )

    local fvp_pane_id
    fvp_pane_id="$(tmux_cmd new-session -d -P -F '#{pane_id}' -s "${TMUX_SESSION}" -n fvp bash -lc "${supervisor_body}")"
    tmux_cmd set-option -t "${TMUX_SESSION}" mouse on
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" pane-border-status top
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" pane-border-format '#{pane_index}: #{pane_title}'
    tmux_cmd select-pane -t "${fvp_pane_id}" -T fvp
    tmux_cmd bind-key -n F12 kill-session -t "${TMUX_SESSION}"

    printf 'started tmux session: %s\n' "${TMUX_SESSION}"
    printf 'logs: %s\n' "${OUT_DIR}"
    printf 'attach command: %s attach-session -t %s\n' "${TMUX_BIN}" "${TMUX_SESSION}"
    printf 'F12 kills the session.\n'

    if ((NO_ATTACH)); then
        return 0
    fi

    if [[ -n "${TMUX:-}" ]]; then
        tmux_cmd switch-client -t "${TMUX_SESSION}:fvp"
    else
        tmux_cmd attach-session -t "${TMUX_SESSION}"
    fi
}

if [[ "${1:-}" == "--supervise" ]]; then
    supervise_run
    exit $?
fi

EXTRA_FVP_ARGS=()
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
        --fvpconf)
            (($# >= 2)) || die "--fvpconf requires a value"
            FVP_CONF="$2"
            shift 2
            ;;
        --runfvp-bin)
            (($# >= 2)) || die "--runfvp-bin requires a value"
            RUNFVP_BIN="$2"
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
            EXTRA_FVP_ARGS=("$@")
            break
            ;;
        *)
            die "unknown argument: $1"
            ;;
    esac
done

start_tmux

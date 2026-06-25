#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${ROOT_DIR}/run_fvp.sh"

MACHINE="${MACHINE:-apollo-fvp}"
YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
DEPLOY_DIR="${DEPLOY_DIR:-}"
SDK_DIR="${SDK_DIR:-${ROOT_DIR}/build/local-sdk}"
RUNFVP_BIN="${RUNFVP_BIN:-${ROOT_DIR}/layers/meta-arm/scripts/runfvp}"
FVP_CONF="${FVP_CONF:-}"
TMUX_BIN="${TMUX_BIN:-tmux}"
TMUX_SESSION="${TMUX_SESSION:-}"
FVP_ROOT_PANE="${FVP_ROOT_PANE:-}"
UART_PORT_DIR="${UART_PORT_DIR:-}"
FVP_START_FILE="${FVP_START_FILE:-}"
OUT_DIR="${OUT_DIR:-}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
NO_ATTACH=0
DRY_RUN=0
LOCAL_MODE=0

usage()
{
    cat <<EOF
Usage: ./run_fvp.sh [options] [-- extra FVP args]

Run the Yocto-built or local-packaged Apollo FVP image in tmux and mirror
subsystem UARTs to file-backed logs.

Options:
  --machine NAME       Yocto machine (default: ${MACHINE})
  --local              run the local FVP package from build/local-apollo-fvp/deploy
  --build-dir PATH     Yocto build directory (default: ${YOCTO_BUILD_DIR})
  --deploy-dir PATH    image deploy directory
                       (default: <build-dir>/tmp_baremetal/deploy/images/<machine>)
  --fvpconf PATH       FVP config to run
                       (default: <deploy-dir>/nexios-image-<machine>.fvpconf)
  --session NAME       tmux session name
                       (default: apollo-fvp-yocto-<timestamp>)
  --out-dir PATH       log/output directory
                       (default: <build-dir>/fvp-tmux/<machine>-<timestamp>)
  --runfvp-bin PATH    runfvp executable (default: ${RUNFVP_BIN})
  --no-attach          start tmux but do not attach
  --dry-run            print the resolved command and log layout only
  -h, --help           show this help

Environment overrides:
  MACHINE YOCTO_BUILD_DIR DEPLOY_DIR RUNFVP_BIN FVP_CONF TMUX_SESSION OUT_DIR
  RUN_STAMP TMUX_BIN SDK_DIR

Examples:
  ./yocto_build.sh
  ./local_build.sh --package
  Missing local package recovery: ./local_build.sh --package first.
  ./run_fvp.sh
  ./run_fvp.sh --local
  ./run_fvp.sh --no-attach
  ./run_fvp.sh --dry-run
  ./run_fvp.sh --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp.fvpconf

Inside tmux, F12 kills the whole session.
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
    source "${env_file}"
    set -u
}

resolve_deploy_dir()
{
    if [[ -n "${DEPLOY_DIR}" ]]; then
        printf '%s\n' "${DEPLOY_DIR}"
        return 0
    fi

    if ((LOCAL_MODE)); then
        printf '%s/local-apollo-fvp/deploy\n' "${YOCTO_BUILD_DIR}"
    else
        printf '%s/tmp_baremetal/deploy/images/%s\n' "${YOCTO_BUILD_DIR}" "${MACHINE}"
    fi
}

resolve_fvpconf()
{
    local deploy_dir="$1"
    local stable="${deploy_dir}/nexios-image-${MACHINE}.fvpconf"
    local latest

    if [[ -n "${FVP_CONF}" ]]; then
        printf '%s\n' "${FVP_CONF}"
        return 0
    fi

    if ((LOCAL_MODE)); then
        stable="${deploy_dir}/apollo-fvp-local.fvpconf"
        [[ -f "${stable}" ]] || return 1
        printf '%s\n' "${stable}"
        return 0
    fi

    if [[ -f "${stable}" ]]; then
        printf '%s\n' "${stable}"
        return 0
    fi

    latest="$(
        find "${deploy_dir}" -maxdepth 1 -type f \
            -name "nexios-image-${MACHINE}-*.fvpconf" \
            -printf '%T@ %p\n' 2>/dev/null |
            sort -nr |
            sed -n '1s/^[^ ]* //p'
    )"
    [[ -n "${latest}" ]] || return 1
    printf '%s\n' "${latest}"
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

with layout_file.open("w", encoding="utf-8") as f:
    f.write("terminal_path\tterminal\tlabel\n")
    for terminal_path, label in sorted(cfg.get("terminals", {}).items()):
        if not label:
            continue
        terminal = terminal_path.rsplit(".", 1)[-1]
        args.extend(["--parameter", f"{terminal_path}.start_telnet=1"])
        f.write(f"{terminal_path}\t{terminal}\t{label}\n")

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

domain_title()
{
    case "$1" in
        rse) printf 'RSE / TF-M\n' ;;
        safety_island_cl0) printf 'Safety Island CL0 / SCP-firmware\n' ;;
        safety_island_cl1) printf 'Safety Island CL1 / Zephyr\n' ;;
        tf_a) printf 'TF-A / secure-world AP\n' ;;
        u_boot_linux) printf 'U-Boot / Linux\n' ;;
        *) return 1 ;;
    esac
}

tmux_cmd()
{
    env -u TMUX "${TMUX_BIN}" "$@"
}

uart_telnet_bridge_code()
{
    cat <<'PY'
import errno
import fcntl
import os
import pty
import select
import subprocess
import sys
import termios
import tty

log_path = sys.argv[1]
port = sys.argv[2]
stdin_fd = sys.stdin.fileno()
stdout_fd = sys.stdout.fileno()
previous = -1

def display_bytes(data):
    global previous
    display = bytearray()
    for byte in data:
        if byte == 10 and previous != 13:
            display.append(13)
        display.append(byte)
        previous = byte
    os.write(stdout_fd, display)

master_fd, slave_fd = pty.openpty()
try:
    size = fcntl.ioctl(stdout_fd, termios.TIOCGWINSZ, b"\0" * 8)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, size)
except OSError:
    pass

proc = subprocess.Popen(
    ["telnet", "127.0.0.1", port],
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    close_fds=True,
)
os.close(slave_fd)
old_termios = None
stdin_open = True

try:
    if os.isatty(stdin_fd):
        old_termios = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)

    with open(log_path, "ab", buffering=0) as log:
        while True:
            read_fds = [master_fd]
            if stdin_open:
                read_fds.append(stdin_fd)

            ready, _, _ = select.select(read_fds, [], [], 0.1)

            if master_fd in ready:
                try:
                    data = os.read(master_fd, 4096)
                except OSError as exc:
                    if exc.errno == errno.EIO:
                        break
                    raise
                if not data:
                    break
                log.write(data)
                display_bytes(data)

            if stdin_fd in ready:
                data = os.read(stdin_fd, 4096)
                if data:
                    os.write(master_fd, data)
                else:
                    stdin_open = False

            if proc.poll() is not None:
                ready, _, _ = select.select([master_fd], [], [], 0)
                if master_fd not in ready:
                    break
finally:
    if old_termios is not None:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_termios)
    try:
        os.close(master_fd)
    except OSError:
        pass
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

sys.exit(proc.returncode or 0)
PY
}

start_waiting_uart_pane()
{
    local domain="$1"
    shift
    local title
    local log_path
    local port_file
    local term_file
    local pane_body
    local pane_id
    local bridge_code

    title="$(domain_title "${domain}")"
    log_path="${OUT_DIR}/uarts/${domain}.log"
    port_file="${UART_PORT_DIR}/${domain}.port"
    term_file="${UART_PORT_DIR}/${domain}.terminal"
    : >"${log_path}"
    bridge_code="$(uart_telnet_bridge_code)"

    printf -v pane_body \
        'printf "Subsystem: %%s\r\nLog: %%s\r\nWaiting for FVP UART port...\r\n\r\n" %q %q; while [[ ! -s %q ]]; do sleep 0.2; done; port="$(<%q)"; term="$(<%q 2>/dev/null || true)"; printf "UART: %%s\r\nPort: %%s\r\n\r\n" "${term:-unknown}" "${port}"; python3 -c %q %q "${port}"; printf "\r\nUART pane exited. Press Enter to close this pane.\r\n"; read -r _' \
        "${title}" "${log_path}" "${port_file}" "${port_file}" "${term_file}" \
        "${bridge_code}" "${log_path}"

    pane_id="$(tmux_cmd split-window -d -P -F '#{pane_id}' "$@" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T "${domain}"
    printf '%s\n' "${pane_id}"
}

start_shell_pane()
{
    local pane_body
    local pane_id

    pane_body='printf "Interactive shell\r\n\r\n"; exec "${SHELL:-bash}" -l'
    pane_id="$(tmux_cmd split-window -d -P -F '#{pane_id}' "$@" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T shell
    printf '%s\n' "${pane_id}"
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
    local split_target
    local bridge_code

    if ! domain="$(terminal_domain "${term}")"; then
        printf 'Ignoring unmanaged FVP terminal %s on port %s\n' "${term}" "${port}" |
            tee -a "${OUT_DIR}/tmux-supervisor.log"
        return 0
    fi
    title="$(terminal_title "${term}")"

    marker="${OUT_DIR}/.pane-${domain}"
    [[ ! -e "${marker}" ]] || return 0
    : >"${marker}"

    log_path="${OUT_DIR}/uarts/${domain}.log"
    mkdir -p "$(dirname "${log_path}")"
    : >"${log_path}"
    bridge_code="$(uart_telnet_bridge_code)"
    printf '%s\t%s\t%s\t%s\n' "${domain}" "${term}" "${port}" "${log_path}" >>"${OUT_DIR}/ports.tsv"

    printf 'UART %s is listening on port %s; log: %s\n' "${domain}" "${port}" "${log_path}" |
        tee -a "${OUT_DIR}/tmux-supervisor.log"

    if [[ -n "${UART_PORT_DIR}" ]]; then
        mkdir -p "${UART_PORT_DIR}"
        printf '%s\n' "${term}" >"${UART_PORT_DIR}/${domain}.terminal"
        printf '%s\n' "${port}" >"${UART_PORT_DIR}/${domain}.port.tmp"
        mv "${UART_PORT_DIR}/${domain}.port.tmp" "${UART_PORT_DIR}/${domain}.port"
        return 0
    fi

    printf -v pane_body \
        'printf "Subsystem: %%s\r\nUART: %%s\r\nPort: %%s\r\nLog: %%s\r\n\r\n" %q %q %q %q; python3 -c %q %q %q; printf "\r\nUART pane exited. Press Enter to close this pane.\r\n"; read -r _' \
        "${title}" "${term}" "${port}" "${log_path}" \
        "${bridge_code}" "${log_path}" "${port}"

    split_target="${FVP_ROOT_PANE:-${TMUX_SESSION}:fvp}"
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" synchronize-panes off >/dev/null
    pane_id="$(tmux_cmd split-window -d -P -F '#{pane_id}' -t "${split_target}" bash -lc "${pane_body}")"
    tmux_cmd select-pane -t "${pane_id}" -T "${domain}"
    if [[ -n "${FVP_ROOT_PANE}" ]]; then
        tmux_cmd select-pane -t "${FVP_ROOT_PANE}"
    fi
    tmux_cmd select-layout -t "${TMUX_SESSION}:fvp" tiled >/dev/null
}

supervise_run()
{
    if [[ -z "${FVP_ROOT_PANE}" && -n "${TMUX_PANE:-}" ]]; then
        FVP_ROOT_PANE="${TMUX_PANE}"
    fi

    if [[ -n "${FVP_START_FILE}" ]]; then
        printf 'Waiting for tmux UART panes...\n'
        while [[ ! -e "${FVP_START_FILE}" ]]; do
            sleep 0.1
        done
    fi

    source_sdk_if_present
    require_command telnet
    require_command python3

    mkdir -p "${OUT_DIR}/uarts"
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
    if [[ -n "${FVP_ROOT_PANE}" ]]; then
        printf 'Supervisor pane: %s\n\n' "${FVP_ROOT_PANE}"
    fi
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
Apollo FVP tmux run
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
        die "FVP config not found: ${FVP_CONF}. Run ./yocto_build.sh first or pass --fvpconf."

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
    local control_dir="${OUT_DIR}/control"
    UART_PORT_DIR="${control_dir}/ports"
    FVP_START_FILE="${control_dir}/start"
    supervisor_body=$(
        printf 'cd %q || exit 1; ' "${ROOT_DIR}"
        printf 'ROOT_DIR=%q MACHINE=%q YOCTO_BUILD_DIR=%q DEPLOY_DIR=%q SDK_DIR=%q ' \
            "${ROOT_DIR}" "${MACHINE}" "${YOCTO_BUILD_DIR}" "${DEPLOY_DIR}" "${SDK_DIR}"
        printf 'RUNFVP_BIN=%q FVP_CONF=%q OUT_DIR=%q EXTRA_ARGS_FILE=%q ' \
            "${RUNFVP_BIN}" "${FVP_CONF}" "${OUT_DIR}" "${EXTRA_ARGS_FILE}"
        printf 'UART_PORT_DIR=%q FVP_START_FILE=%q ' \
            "${UART_PORT_DIR}" "${FVP_START_FILE}"
        printf 'TMUX_BIN=%q TMUX_SESSION=%q ' "${TMUX_BIN}" "${TMUX_SESSION}"
        printf 'exec %q --supervise' "${SCRIPT_PATH}"
    )

    local fvp_pane_id
    mkdir -p "${UART_PORT_DIR}"
    fvp_pane_id="$(tmux_cmd new-session -d -x 160 -y 48 -P -F '#{pane_id}' -s "${TMUX_SESSION}" -n fvp bash -lc "${supervisor_body}")"
    FVP_ROOT_PANE="${fvp_pane_id}"
    tmux_cmd set-option -t "${TMUX_SESSION}" mouse on
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" synchronize-panes off
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" pane-border-status top
    tmux_cmd set-window-option -t "${TMUX_SESSION}:fvp" pane-border-format '#{pane_index}: #{pane_title}'
    tmux_cmd select-pane -t "${fvp_pane_id}" -T fvp

    local u_boot_pane_id
    local rse_pane_id
    local si0_pane_id
    local si1_pane_id

    u_boot_pane_id="$(start_waiting_uart_pane u_boot_linux -v -b -l 70% -t "${FVP_ROOT_PANE}")"
    rse_pane_id="$(start_waiting_uart_pane rse -h -l 40% -t "${u_boot_pane_id}")"
    si0_pane_id="$(start_waiting_uart_pane safety_island_cl0 -v -l 75% -t "${rse_pane_id}")"
    si1_pane_id="$(start_waiting_uart_pane safety_island_cl1 -v -l 67% -t "${si0_pane_id}")"
    start_waiting_uart_pane tf_a -v -l 50% -t "${si1_pane_id}" >/dev/null
    start_shell_pane -h -l 50% -t "${FVP_ROOT_PANE}" >/dev/null

    tmux_cmd select-pane -t "${FVP_ROOT_PANE}"
    : >"${FVP_START_FILE}"
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
        --machine)
            (($# >= 2)) || die "--machine requires a value"
            MACHINE="$2"
            shift 2
            ;;
        --local)
            LOCAL_MODE=1
            shift
            ;;
        --build-dir)
            (($# >= 2)) || die "--build-dir requires a value"
            YOCTO_BUILD_DIR="$2"
            shift 2
            ;;
        --deploy-dir)
            (($# >= 2)) || die "--deploy-dir requires a value"
            DEPLOY_DIR="$2"
            shift 2
            ;;
        --fvpconf)
            (($# >= 2)) || die "--fvpconf requires a value"
            FVP_CONF="$2"
            shift 2
            ;;
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

FVP_CONF_REQUESTED=0
if [[ -n "${FVP_CONF}" ]]; then
    FVP_CONF_REQUESTED=1
fi

YOCTO_BUILD_DIR="$(abspath "${YOCTO_BUILD_DIR}")"
DEPLOY_DIR="$(abspath "$(resolve_deploy_dir)")"
resolved_fvpconf="$(resolve_fvpconf "${DEPLOY_DIR}" || true)"
if [[ -n "${resolved_fvpconf}" ]]; then
    FVP_CONF="$(abspath "${resolved_fvpconf}")"
else
    FVP_CONF=""
fi
RUNFVP_BIN="$(abspath "${RUNFVP_BIN}")"

if ((LOCAL_MODE)); then
    [[ "${FVP_CONF_REQUESTED}" == 1 || -d "${DEPLOY_DIR}" ]] ||
        die "local deploy directory not found: ${DEPLOY_DIR}. Run ./local_build.sh --package first."
    [[ -n "${FVP_CONF}" && -f "${FVP_CONF}" ]] ||
        die "FVP config not found under ${DEPLOY_DIR}. Run ./local_build.sh --package first or pass --fvpconf."
else
    [[ "${FVP_CONF_REQUESTED}" == 1 || -d "${DEPLOY_DIR}" ]] ||
        die "Yocto deploy directory not found: ${DEPLOY_DIR}. Run ./yocto_build.sh first."
    [[ -n "${FVP_CONF}" && -f "${FVP_CONF}" ]] ||
        die "FVP config not found under ${DEPLOY_DIR}. Run ./yocto_build.sh first or pass --fvpconf."
fi

if [[ -z "${TMUX_SESSION}" ]]; then
    if ((LOCAL_MODE)); then
        TMUX_SESSION="apollo-fvp-local-${RUN_STAMP}"
    else
        TMUX_SESSION="apollo-fvp-yocto-${RUN_STAMP}"
    fi
fi
if [[ -z "${OUT_DIR}" ]]; then
    if ((LOCAL_MODE)); then
        OUT_DIR="${YOCTO_BUILD_DIR}/local-apollo-fvp/tmux-run/${RUN_STAMP}"
    else
        OUT_DIR="${YOCTO_BUILD_DIR}/fvp-tmux/${MACHINE}-${RUN_STAMP}"
    fi
fi
OUT_DIR="$(abspath "${OUT_DIR}")"

start_tmux

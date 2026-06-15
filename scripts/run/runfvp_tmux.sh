#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TMUX_BIN="${TMUX_BIN:-tmux}"
TMUX_SESSION="${FVP_TMUX_SESSION:-arm-auto-solutions}"
TMUX_SOCKET="${FVP_TMUX_SOCKET:-}"
TMUX_ATTACH="${FVP_TMUX_ATTACH:-1}"
TMUX_SOCKET_LABEL="${TMUX_SOCKET:-default}"
TMUX_WRAPPER_DIR="${FVP_TMUX_WRAPPER_DIR:-${WORKSPACE_DIR}/build/runfvp-tmux/${TMUX_SOCKET_LABEL}/${TMUX_SESSION}/bin}"
RUNFVP_BIN="${RUNFVP_BIN:-${WORKSPACE_DIR}/layers/meta-arm/scripts/runfvp}"
DEFAULT_TARGET="${RUNFVP_TARGET:-${WORKSPACE_DIR}/build/tmp_baremetal/deploy/images/apollo-fvp/baremetal-image-apollo-fvp.fvpconf}"

usage() {
    cat <<EOF
Usage: $0 [runfvp-config-or-machine] [-- extra FVP args]

Start runfvp inside the Arm Auto Solutions tmux session.

Defaults:
  session: ${TMUX_SESSION}
  socket:  ${TMUX_SOCKET_LABEL}
  target:  ${DEFAULT_TARGET}

Environment overrides:
  FVP_TMUX_SESSION  tmux session name
  FVP_TMUX_SOCKET   tmux socket name, empty means default socket
  FVP_TMUX_ATTACH   attach after starting session, 1 or 0
  FVP_TMUX_WRAPPER_DIR
                   directory for the generated tmux wrapper
  RUNFVP_BIN        runfvp executable path
  RUNFVP_TARGET     default runfvp config or machine

Inside tmux:
  mouse             enabled
  F12               kill the whole runfvp tmux session
EOF
}

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

quote_args() {
    local arg
    printf '%q' "$1"
    shift || true
    for arg in "$@"; do
        printf ' %q' "$arg"
    done
}

validate_tmux_name() {
    local name="$1"
    local value="$2"

    [[ "${value}" =~ ^[A-Za-z0-9_.-]+$ ]] ||
        die "${name} must contain only letters, numbers, dot, underscore, or dash: ${value}"
}

tmux_cmd() {
    if [[ -n "${TMUX_SOCKET}" ]]; then
        env -u TMUX "${TMUX_BIN}" -L "${TMUX_SOCKET}" "$@"
    else
        env -u TMUX "${TMUX_BIN}" "$@"
    fi
}

prepare_tmux_wrapper() {
    local real_tmux
    local socket_args

    real_tmux="$(command -v "${TMUX_BIN}")" ||
        die "tmux not found. Install tmux or set TMUX_BIN."
    if [[ -n "${TMUX_SOCKET}" ]]; then
        socket_args="-L $(quote_args "${TMUX_SOCKET}")"
    else
        socket_args=""
    fi
    mkdir -p "${TMUX_WRAPPER_DIR}"
    {
        printf '#!/usr/bin/env bash\n'
        printf 'set -euo pipefail\n'
        printf 'real_tmux=%s\n' "$(quote_args "${real_tmux}")"
        printf 'target_session=%s\n' "$(quote_args "${TMUX_SESSION}")"
        printf 'socket_args=(%s)\n' "${socket_args}"
        printf 'if [[ "${1:-}" == "new-window" || "${1:-}" == "neww" ]]; then\n'
        printf '    for arg in "$@"; do\n'
        printf '        [[ "${arg}" == "-t" || "${arg}" == -t* ]] && exec "${real_tmux}" "${socket_args[@]}" "$@"\n'
        printf '    done\n'
        printf '    command="$1"\n'
        printf '    shift\n'
        printf '    exec "${real_tmux}" "${socket_args[@]}" "${command}" -t "${target_session}:" "$@"\n'
        printf 'fi\n'
        printf 'exec "${real_tmux}" "${socket_args[@]}" "$@"\n'
    } >"${TMUX_WRAPPER_DIR}/tmux"
    chmod +x "${TMUX_WRAPPER_DIR}/tmux"
}

attach_tmux_session() {
    if [[ "${TMUX_ATTACH}" == "0" ]]; then
        exit 0
    fi

    if [[ -n "${TMUX:-}" && -z "${TMUX_SOCKET}" ]]; then
        "${TMUX_BIN}" switch-client -t "${TMUX_SESSION}:runfvp" 2>/dev/null || true
        exit 0
    fi

    if [[ -n "${TMUX_SOCKET}" ]]; then
        exec env -u TMUX "${TMUX_BIN}" -L "${TMUX_SOCKET}" attach-session -t "${TMUX_SESSION}"
    else
        exec env -u TMUX "${TMUX_BIN}" attach-session -t "${TMUX_SESSION}"
    fi
}

print_attach_command() {
    if [[ -n "${TMUX_SOCKET}" ]]; then
        printf 'attach command: %s -L %s attach-session -t %s\n' "${TMUX_BIN}" "${TMUX_SOCKET}" "${TMUX_SESSION}"
    else
        printf 'attach command: %s attach-session -t %s\n' "${TMUX_BIN}" "${TMUX_SESSION}"
    fi
}

main() {
    if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
        usage
        exit 0
    fi

    command -v "${TMUX_BIN}" >/dev/null 2>&1 ||
        die "tmux not found. Install tmux or set TMUX_BIN."
    [[ -x "${RUNFVP_BIN}" ]] ||
        die "runfvp not executable: ${RUNFVP_BIN}"

    validate_tmux_name "FVP_TMUX_SESSION" "${TMUX_SESSION}"
    if [[ -n "${TMUX_SOCKET}" ]]; then
        validate_tmux_name "FVP_TMUX_SOCKET" "${TMUX_SOCKET}"
    fi
    [[ "${TMUX_ATTACH}" == "0" || "${TMUX_ATTACH}" == "1" ]] ||
        die "FVP_TMUX_ATTACH must be 1 or 0: ${TMUX_ATTACH}"
    prepare_tmux_wrapper

    local -a runfvp_args
    if (($# == 0)); then
        [[ -e "${DEFAULT_TARGET}" ]] ||
            die "default runfvp target not found: ${DEFAULT_TARGET}. Pass a .fvpconf path or set RUNFVP_TARGET."
        runfvp_args=("-t" "tmux" "${DEFAULT_TARGET}")
    elif [[ "${1}" == "--" ]]; then
        [[ -e "${DEFAULT_TARGET}" ]] ||
            die "default runfvp target not found: ${DEFAULT_TARGET}. Pass a .fvpconf path or set RUNFVP_TARGET."
        runfvp_args=("-t" "tmux" "${DEFAULT_TARGET}" "$@")
    else
        runfvp_args=("-t" "tmux" "$@")
    fi

    local runfvp_command
    local pane_command
    runfvp_command="$(quote_args "${RUNFVP_BIN}" "${runfvp_args[@]}")"
    pane_command=$(
        printf 'cd %s || exit 1; ' "$(quote_args "${WORKSPACE_DIR}")"
        printf 'export PATH=%s:"$PATH"; ' "$(quote_args "${TMUX_WRAPPER_DIR}")"
        printf 'printf "runfvp tmux session: %s\\n"; ' "${TMUX_SESSION}"
        printf 'printf "F12 kills this session. Mouse support is enabled.\\n\\n"; '
        printf 'printf "Command: %%s\\n\\n" %s; ' "$(quote_args "${runfvp_command}")"
        printf '%s; ' "${runfvp_command}"
        printf 'status=$?; '
        printf 'printf "\\nrunfvp exited with status %%s. Press Enter to close this pane, or F12 to kill the session.\\n" "$status"; '
        printf 'read -r _; '
        printf 'exit "$status"'
    )

    if tmux_cmd has-session -t "${TMUX_SESSION}" 2>/dev/null; then
        tmux_cmd set-option -g mouse on
        tmux_cmd bind-key -n F12 kill-session -t "${TMUX_SESSION}"
        if tmux_cmd list-windows -t "${TMUX_SESSION}" -F "#{window_name}" | grep -Fxq runfvp; then
            printf 'attaching to existing tmux session: %s\n' "${TMUX_SESSION}"
        else
            tmux_cmd new-window -t "${TMUX_SESSION}:" -n runfvp "${pane_command}"
            printf 'added runfvp window to existing tmux session: %s\n' "${TMUX_SESSION}"
        fi
        print_attach_command
        attach_tmux_session
    fi

    tmux_cmd new-session -d -s "${TMUX_SESSION}" -n runfvp "${pane_command}"
    tmux_cmd set-option -g mouse on
    tmux_cmd bind-key -n F12 kill-session -t "${TMUX_SESSION}"
    printf 'started tmux session: %s\n' "${TMUX_SESSION}"
    print_attach_command
    attach_tmux_session
}

main "$@"

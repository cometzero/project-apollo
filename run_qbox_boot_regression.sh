#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
PYTHON="${PYTHON:-python3}"
REGRESSION_SCRIPT="${REGRESSION_SCRIPT:-${ROOT_DIR}/scripts/test/run_qbox_yocto_boot_regression.py}"
RESULT_ROOT="${RESULT_ROOT:-${ROOT_DIR}/build/qbox-apollo-fvp}"
BASELINE="${BASELINE:-${RESULT_ROOT}/run_qbox_yocto_baseline.json}"
OUT_DIR="${OUT_DIR:-${RESULT_ROOT}/regression-${RUN_STAMP}}"
TIMEOUT="${TIMEOUT:-900}"
THRESHOLD="${THRESHOLD:-0.20}"
POLL_INTERVAL="${POLL_INTERVAL:-0.5}"
CONTEXT_LINES="${CONTEXT_LINES:-3}"
RESULT_WAIT_TIMEOUT="${RESULT_WAIT_TIMEOUT:-}"
DRY_RUN=0
CHILD_PID=""

die()
{
    printf 'run_qbox_boot_regression.sh: error: %s\n' "$*" >&2
    exit 1
}

usage()
{
    cat <<EOF
Usage: ./run_qbox_boot_regression.sh [regression-options] [-- runner-options]

Run the default Apollo QBox Yocto boot regression test in headless mode.
The underlying Python regression runner always stops the QBox process when
the test exits, fails, or is interrupted.

Defaults:
  baseline:      ${BASELINE}
  out_dir:       ${OUT_DIR}
  timeout:       ${TIMEOUT}
  threshold:     ${THRESHOLD}
  poll_interval: ${POLL_INTERVAL}

Common overrides:
  TIMEOUT=600 ./run_qbox_boot_regression.sh
  OUT_DIR=build/qbox-apollo-fvp/regression-test ./run_qbox_boot_regression.sh
  BASELINE=build/qbox-apollo-fvp/run_qbox_yocto_baseline.json ./run_qbox_boot_regression.sh
  ./run_qbox_boot_regression.sh --threshold 0.10
  ./run_qbox_boot_regression.sh --dry-run
  ./run_qbox_boot_regression.sh -- --copy-disks

Wrapper options:
  --dry-run      Print the command without running it
  -h, --help     Show this help

All other arguments are passed to scripts/test/run_qbox_yocto_boot_regression.py.
Arguments after "--" are passed through to run_qbox_yocto.sh by that script.
EOF
}

contains_arg()
{
    local wanted="$1"
    shift
    local arg
    for arg in "$@"; do
        [[ "${arg}" == "${wanted}" ]] && return 0
    done
    return 1
}

quote_command()
{
    local arg
    for arg in "$@"; do
        printf '%q ' "${arg}"
    done
    printf '\n'
}

terminate_child()
{
    local sig="$1"
    local status="$2"

    trap - INT TERM EXIT
    if [[ -n "${CHILD_PID}" ]] && kill -0 "${CHILD_PID}" 2>/dev/null; then
        printf 'run_qbox_boot_regression.sh: caught SIG%s, waiting for QBox cleanup...\n' "${sig}" >&2
        kill "-${sig}" "${CHILD_PID}" 2>/dev/null || true
        wait "${CHILD_PID}" 2>/dev/null || true
        CHILD_PID=""
    fi
    exit "${status}"
}

cleanup_on_exit()
{
    local status=$?

    trap - INT TERM EXIT
    if [[ -n "${CHILD_PID}" ]] && kill -0 "${CHILD_PID}" 2>/dev/null; then
        printf 'run_qbox_boot_regression.sh: terminating regression runner...\n' >&2
        kill -INT "${CHILD_PID}" 2>/dev/null || true
        wait "${CHILD_PID}" 2>/dev/null || true
        CHILD_PID=""
    fi
    exit "${status}"
}

main()
{
    local -a extra_args=()
    while (($# > 0)); do
        case "$1" in
            -h|--help)
                usage
                return 0
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            --)
                extra_args+=("$@")
                break
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    [[ -f "${REGRESSION_SCRIPT}" ]] ||
        die "missing regression script: ${REGRESSION_SCRIPT}"
    if ! contains_arg "--record-baseline" "${extra_args[@]}"; then
        [[ -f "${BASELINE}" ]] ||
            die "missing baseline: ${BASELINE}; create it with --record-baseline first"
    fi

    local -a command=(
        "${PYTHON}"
        "${REGRESSION_SCRIPT}"
        "--run"
        "--baseline" "${BASELINE}"
        "--out-dir" "${OUT_DIR}"
        "--timeout" "${TIMEOUT}"
        "--threshold" "${THRESHOLD}"
        "--poll-interval" "${POLL_INTERVAL}"
        "--context-lines" "${CONTEXT_LINES}"
    )
    if [[ -n "${RESULT_WAIT_TIMEOUT}" ]]; then
        command+=("--result-wait-timeout" "${RESULT_WAIT_TIMEOUT}")
    fi
    command+=("${extra_args[@]}")

    printf 'Running QBox boot regression:\n  '
    quote_command "${command[@]}"

    if ((DRY_RUN)); then
        return 0
    fi

    trap 'terminate_child INT 130' INT
    trap 'terminate_child TERM 143' TERM
    trap cleanup_on_exit EXIT

    (
        trap - INT TERM
        exec "${command[@]}"
    ) &
    CHILD_PID=$!
    set +e
    wait "${CHILD_PID}"
    local status=$?
    set -e
    CHILD_PID=""
    trap - INT TERM EXIT
    return "${status}"
}

main "$@"

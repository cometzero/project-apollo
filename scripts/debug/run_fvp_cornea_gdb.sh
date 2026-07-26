#!/usr/bin/env bash

set -euo pipefail

IRIS_PORT=""
IRIS_INSTANCE=""
GDB_SCRIPT=""
CORNEA_BIN=""
WAIT_TIMEOUT=60

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

while (($# > 0)); do
    case "$1" in
        --iris-port)
            (($# >= 2)) || die "--iris-port requires a value"
            IRIS_PORT="$2"
            shift 2
            ;;
        --iris-instance)
            (($# >= 2)) || die "--iris-instance requires a value"
            IRIS_INSTANCE="$2"
            shift 2
            ;;
        --gdb-script)
            (($# >= 2)) || die "--gdb-script requires a value"
            GDB_SCRIPT="$2"
            shift 2
            ;;
        --cornea)
            (($# >= 2)) || die "--cornea requires a value"
            CORNEA_BIN="$2"
            shift 2
            ;;
        --wait-timeout)
            (($# >= 2)) || die "--wait-timeout requires a value"
            WAIT_TIMEOUT="$2"
            shift 2
            ;;
        *)
            die "unknown argument: $1"
            ;;
    esac
done

[[ "${IRIS_PORT}" =~ ^[0-9]+$ ]] || die "invalid Iris port: ${IRIS_PORT}"
[[ -n "${IRIS_INSTANCE}" ]] || die "--iris-instance is required"
[[ -f "${GDB_SCRIPT}" ]] || die "GDB command file not found: ${GDB_SCRIPT}"
[[ -x "${CORNEA_BIN}" ]] || die "lite-cornea executable not found: ${CORNEA_BIN}"
command -v gdb-multiarch >/dev/null 2>&1 || die "gdb-multiarch is required"

printf 'FVP debugger: lite-cornea over Iris\n'
printf 'Iris target: %s\n' "${IRIS_INSTANCE}"
printf 'Waiting for Iris port: 127.0.0.1:%s\n\n' "${IRIS_PORT}"

python3 - "${IRIS_PORT}" "${WAIT_TIMEOUT}" <<'PY'
import socket
import sys
import time

port = int(sys.argv[1])
deadline = time.monotonic() + float(sys.argv[2])
while time.monotonic() < deadline:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            raise SystemExit(0)
    time.sleep(0.2)
raise SystemExit(f"timed out waiting for Iris port {port}")
PY

"${CORNEA_BIN}" --port "${IRIS_PORT}" \
    register-read "${IRIS_INSTANCE}" PC >/dev/null
target_command="target remote | ${CORNEA_BIN} --port ${IRIS_PORT} gdb-proxy ${IRIS_INSTANCE}"
exec gdb-multiarch -q -x "${GDB_SCRIPT}" \
    -ex "set remote noack-packet off" \
    -ex "${target_command}" \
    -ex continue

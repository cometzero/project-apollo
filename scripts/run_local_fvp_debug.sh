#!/usr/bin/env bash
#
# Start the local Apollo FVP image with an Iris debug server enabled.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MACHINE="${MACHINE:-apollo-fvp}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-${MACHINE}}"
DEBUG_DIR="${DEBUG_DIR:-${LOCAL_BUILD_DIR}/debug}"
IRIS_PORT="${IRIS_PORT:-7100}"
BREAK_TIMEOUT="${BREAK_TIMEOUT:-60}"
RUN_IMMEDIATELY=0
NO_ATTACH=0
DRY_RUN=0
TMUX_ARGS=()
BREAKPOINTS=()

usage()
{
    cat <<EOF
Usage: scripts/run_local_fvp_debug.sh [options] [-- extra FVP args]

Start local Apollo FVP in tmux with Iris debugging enabled. By default the
model starts halted so an Iris-capable debugger can attach before boot.

Options:
  --iris-port PORT        Iris TCP port (default: ${IRIS_PORT})
  --break COMP[:SYMBOL]   Set breakpoint from symbols.json and run to it
  --break-timeout SEC     Timeout for --break run (default: ${BREAK_TIMEOUT})
  --run                   Let the model run immediately after launch
  --session NAME          tmux session name forwarded to run_local_fvp_tmux.sh
  --out-dir PATH          output directory forwarded to run_local_fvp_tmux.sh
  --fvpconf PATH          FVP config forwarded to run_local_fvp_tmux.sh
  --no-attach             start tmux but do not attach
  --dry-run               print setup without launching
  -h, --help              show this help

Examples:
  scripts/run_local_fvp_debug.sh --no-attach --iris-port 7100
  scripts/run_local_fvp_debug.sh --no-attach --iris-port 7100 \\
      --break tfm-bl1_1:Reset_Handler
  scripts/local_debug_iris.py --port 7100 --break u-boot:board_init_f \\
      --run --timeout 120
EOF
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

wait_for_iris()
{
    local port="$1"
    local timeout="$2"
    python3 - "$port" "$timeout" <<'PY'
import socket
import sys
import time

port = int(sys.argv[1])
deadline = time.time() + float(sys.argv[2])
while time.time() < deadline:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect(("127.0.0.1", port))
        except OSError:
            time.sleep(0.5)
            continue
        sys.exit(0)
print(f"timed out waiting for Iris port {port}", file=sys.stderr)
sys.exit(1)
PY
}

EXTRA_FVP_ARGS=()
while (($# > 0)); do
    case "$1" in
        --iris-port)
            (($# >= 2)) || die "--iris-port requires a value"
            IRIS_PORT="$2"
            shift 2
            ;;
        --break)
            (($# >= 2)) || die "--break requires a value"
            BREAKPOINTS+=("$2")
            NO_ATTACH=1
            shift 2
            ;;
        --break-timeout)
            (($# >= 2)) || die "--break-timeout requires a value"
            BREAK_TIMEOUT="$2"
            shift 2
            ;;
        --run)
            RUN_IMMEDIATELY=1
            shift
            ;;
        --session|--out-dir|--fvpconf)
            (($# >= 2)) || die "$1 requires a value"
            TMUX_ARGS+=("$1" "$2")
            shift 2
            ;;
        --no-attach)
            NO_ATTACH=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            TMUX_ARGS+=("--dry-run")
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

if ((${#BREAKPOINTS[@]} > 0)) && ((RUN_IMMEDIATELY)); then
    die "--run cannot be combined with --break; --break runs after installing breakpoints"
fi

mkdir -p "${DEBUG_DIR}"
python3 "${SCRIPT_DIR}/setup_local_debug_env.py" \
    --local-build-dir "${LOCAL_BUILD_DIR}" \
    --out-dir "${DEBUG_DIR}"

FVP_DEBUG_ARGS=(--iris-server --iris-port "${IRIS_PORT}" --print-port-number)
if ((RUN_IMMEDIATELY)); then
    FVP_DEBUG_ARGS+=(--run)
fi

if ((NO_ATTACH)); then
    TMUX_ARGS+=("--no-attach")
fi

"${SCRIPT_DIR}/run_local_fvp_tmux.sh" \
    "${TMUX_ARGS[@]}" \
    -- "${FVP_DEBUG_ARGS[@]}" "${EXTRA_FVP_ARGS[@]}"

if ((${#BREAKPOINTS[@]} == 0)) || ((DRY_RUN)); then
    printf 'Iris debug server port: %s\n' "${IRIS_PORT}"
    printf 'Debug manifest: %s\n' "${DEBUG_DIR}/symbols.json"
    exit 0
fi

wait_for_iris "${IRIS_PORT}" 30

IRIS_ARGS=(--port "${IRIS_PORT}" --manifest "${DEBUG_DIR}/symbols.json")
for bp in "${BREAKPOINTS[@]}"; do
    IRIS_ARGS+=(--break "${bp}")
done
IRIS_ARGS+=(--run --timeout "${BREAK_TIMEOUT}")

python3 "${SCRIPT_DIR}/local_debug_iris.py" "${IRIS_ARGS[@]}"

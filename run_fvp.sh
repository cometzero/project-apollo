#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMUX_RUNNER="${TMUX_RUNNER:-${ROOT_DIR}/scripts/run/run_local_fvp_tmux.sh}"

MACHINE="${MACHINE:-apollo-fvp}"
YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
DEPLOY_DIR="${DEPLOY_DIR:-}"
RUNFVP_BIN="${RUNFVP_BIN:-${ROOT_DIR}/layers/meta-arm/scripts/runfvp}"
FVP_CONF="${FVP_CONF:-}"
TMUX_SESSION="${TMUX_SESSION:-}"
OUT_DIR="${OUT_DIR:-}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
NO_ATTACH=0
DRY_RUN=0

usage()
{
    cat <<EOF
Usage: ./run_fvp.sh [options] [-- extra FVP args]

Run the Yocto-built Apollo FVP image in tmux and mirror subsystem UARTs to
file-backed logs.

Options:
  --machine NAME       Yocto machine (default: ${MACHINE})
  --build-dir PATH     Yocto build directory (default: ${YOCTO_BUILD_DIR})
  --deploy-dir PATH    image deploy directory
                       (default: <build-dir>/tmp_baremetal/deploy/images/<machine>)
  --fvpconf PATH       FVP config to run
                       (default: <deploy-dir>/baremetal-image-<machine>.fvpconf)
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
  RUN_STAMP TMUX_RUNNER TMUX_BIN

Examples:
  ./build.sh
  ./run_fvp.sh
  ./run_fvp.sh --no-attach
  ./run_fvp.sh --dry-run
  ./run_fvp.sh --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/baremetal-image-apollo-fvp.fvpconf

Inside tmux, F12 kills the whole session.
EOF
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

abspath()
{
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "$PWD" "$1" ;;
    esac
}

resolve_deploy_dir()
{
    if [[ -n "${DEPLOY_DIR}" ]]; then
        printf '%s\n' "${DEPLOY_DIR}"
        return 0
    fi

    printf '%s/tmp_baremetal/deploy/images/%s\n' "${YOCTO_BUILD_DIR}" "${MACHINE}"
}

resolve_fvpconf()
{
    local deploy_dir="$1"
    local stable="${deploy_dir}/baremetal-image-${MACHINE}.fvpconf"
    local latest

    if [[ -n "${FVP_CONF}" ]]; then
        printf '%s\n' "${FVP_CONF}"
        return 0
    fi

    if [[ -f "${stable}" ]]; then
        printf '%s\n' "${stable}"
        return 0
    fi

    latest="$(
        find "${deploy_dir}" -maxdepth 1 -type f \
            -name "baremetal-image-${MACHINE}-*.fvpconf" \
            -printf '%T@ %p\n' 2>/dev/null |
            sort -nr |
            sed -n '1s/^[^ ]* //p'
    )"
    [[ -n "${latest}" ]] || return 1
    printf '%s\n' "${latest}"
}

EXTRA_FVP_ARGS=()
while (($# > 0)); do
    case "$1" in
        --machine)
            (($# >= 2)) || die "--machine requires a value"
            MACHINE="$2"
            shift 2
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
TMUX_RUNNER="$(abspath "${TMUX_RUNNER}")"

[[ -x "${TMUX_RUNNER}" ]] || die "tmux runner not executable: ${TMUX_RUNNER}"
[[ "${FVP_CONF_REQUESTED}" == 1 || -d "${DEPLOY_DIR}" ]] ||
    die "Yocto deploy directory not found: ${DEPLOY_DIR}. Run ./build.sh first."
[[ -n "${FVP_CONF}" && -f "${FVP_CONF}" ]] ||
    die "FVP config not found under ${DEPLOY_DIR}. Run ./build.sh first or pass --fvpconf."

if [[ -z "${TMUX_SESSION}" ]]; then
    TMUX_SESSION="apollo-fvp-yocto-${RUN_STAMP}"
fi
if [[ -z "${OUT_DIR}" ]]; then
    OUT_DIR="${YOCTO_BUILD_DIR}/fvp-tmux/${MACHINE}-${RUN_STAMP}"
fi
OUT_DIR="$(abspath "${OUT_DIR}")"

runner_args=(
    "--session" "${TMUX_SESSION}"
    "--out-dir" "${OUT_DIR}"
    "--fvpconf" "${FVP_CONF}"
    "--runfvp-bin" "${RUNFVP_BIN}"
)

if ((NO_ATTACH)); then
    runner_args+=("--no-attach")
fi
if ((DRY_RUN)); then
    runner_args+=("--dry-run")
fi
if ((${#EXTRA_FVP_ARGS[@]} > 0)); then
    runner_args+=("--" "${EXTRA_FVP_ARGS[@]}")
fi

exec env MACHINE="${MACHINE}" DEPLOY_DIR="${DEPLOY_DIR}" "${TMUX_RUNNER}" "${runner_args[@]}"

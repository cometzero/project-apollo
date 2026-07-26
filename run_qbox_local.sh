#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${ROOT_DIR}/scripts/run/qbox_qboxconf_common.sh"

RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M%S)}"
MACHINE="${MACHINE:-apollo-qvp}"
YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
IMAGE_BASENAME="${IMAGE_BASENAME:-nexios-image}"
DEPLOY_DIR="${DEPLOY_DIR:-}"
QBOX_CONF_FILE="${QBOX_CONF_FILE:-}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-}"
OUT_DIR="${OUT_DIR:-}"
QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-${QBOX_PLATFORM_BUILD_DIR:-}}"
QBOX_PLATFORM_DIR="${QBOX_PLATFORM_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox-platform}"
QBOX_CONF="${QBOX_CONF:-}"
SI_MODE="${SI_MODE:-live-cl0-cl1}"
TIMEOUT="${TIMEOUT:-0}"
JOBS="${JOBS:-$(( ($(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2) + 1) / 2 ))}"
SSH_PORT_START="${SSH_PORT_START:-2222}"
SSH_PORT_END="${SSH_PORT_END:-2299}"
RUN_QBOX_COPY_DISKS="${RUN_QBOX_COPY_DISKS:-1}"
KEEP_RUNNING_AFTER_PASS="${KEEP_RUNNING_AFTER_PASS:-1}"
UBOOT_ONLY="${UBOOT_ONLY:-0}"
DRY_RUN="${DRY_RUN:-0}"
LEGACY_FILE_BACKED_SRAM=0
RSE_STATE_DIR="${QBOX_RSE_STATE_DIR:-}"
PERSIST_RSE_STATE="${QBOX_PERSIST_RSE_STATE:-1}"
RESET_RSE_STATE=0
PRIMARY_LOGIN_PROMPT="${PRIMARY_LOGIN_PROMPT:-}"
PRIMARY_SHELL_MARKER="${PRIMARY_SHELL_MARKER:-}"
PRIMARY_SHELL_PROMPT_RE="${PRIMARY_SHELL_PROMPT_RE:-}"
QBOX_APOLLO_NUM_CPUS="${QBOX_APOLLO_NUM_CPUS:-}"
DEBUG_TARGET=""
DEBUG_COMPONENT=""
DEBUG_ENTRYPOINT=""
DEBUG_ENTRY_ADDRESS=""
DEBUG_ENDPOINT=""
DEBUG_MANIFEST=""
DEBUG_GDB_SCRIPT=""
DEBUG_WAIT_LOG=""
DEBUG_WAIT_MARKER=""
DEBUG_CPU_PARAM=""
DEBUG_PLATFORM_PARAMS=()

QBOX_BUILD_DIR_EXPLICIT=0
QBOX_CONF_EXPLICIT=0
[[ -n "${QBOX_BUILD_DIR}" ]] && QBOX_BUILD_DIR_EXPLICIT=1
[[ -n "${QBOX_CONF}" ]] && QBOX_CONF_EXPLICIT=1

ROOTFS_OVERRIDE="${ROOTFS:-}"
EFI_CAPSULE_DISK_OVERRIDE="${EFI_CAPSULE_DISK:-}"
RSE_ROM_OVERRIDE="${RSE_ROM:-}"
RSE_FLASH_OVERRIDE="${RSE_FLASH:-}"
RSE_OTP_OVERRIDE="${RSE_OTP:-}"
AP_FLASH_OVERRIDE="${AP_FLASH:-}"
AP_BL2_ELF_OVERRIDE="${AP_BL2_ELF:-}"
RSE_BL1_2_ELF_OVERRIDE="${RSE_BL1_2_ELF:-}"
RSE_BL2_ELF_OVERRIDE="${RSE_BL2_ELF:-}"
PROVISIONING_BUNDLE_OVERRIDE="${PROVISIONING_BUNDLE:-}"
AP_DTB_OVERRIDE="${AP_DTB:-}"
RSE_SYMBOLS_OVERRIDE="${RSE_SYMBOLS:-}"
SI_CL0_IMAGE_OVERRIDE="${SI_CL0_IMAGE:-}"
SI_CL1_IMAGE_OVERRIDE="${SI_CL1_IMAGE:-}"
SI_CL1_SYMBOLS_OVERRIDE="${SI_CL1_SYMBOLS:-}"

TMUX_RUNNER_ARGS=()
EXTRA_CHILD_ARGS=()
REMOVED_ENV_OVERRIDES=()
REMOVED_ENV_NAMES=(
    "RSE_CPU_MODE"
    "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK"
    "REMOTEPASS_DMI_CACHE"
)

for name in "${REMOVED_ENV_NAMES[@]}"; do
    [[ -v ${name} ]] && REMOVED_ENV_OVERRIDES+=("${name}")
done

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_safe_token()
{
    local name="$1"
    local value="$2"

    [[ "${value}" =~ ^[A-Za-z0-9_-]+$ ]] ||
        die "${name} must be a safe token containing only letters, digits, '_' or '-': ${value}"
}

usage()
{
    cat <<EOF
Usage: ./run_qbox_local.sh [options] [-- extra-qbox-runner-options]

Build local boot artifacts first:
  ./local_build.sh

Then launch QBox in tmux:
  ./run_qbox_local.sh

Options:
  --machine NAME
  --build-dir DIR
  --deploy-dir DIR
  --image-basename NAME
  --qboxconf FILE
  --local-build-dir DIR
  --qbox-build-dir DIR
  --conf FILE
  --session NAME
  --out-dir DIR
  --si-mode MODE
  --timeout SECONDS
  --jobs N
  --copy-disks
  --no-copy-disks
  --legacy-file-backed-sram
  --rse-state-dir DIR
  --reset-rse-state
  --no-persistent-rse-state
  --uboot-only
  --keep-running-after-pass
  --exit-after-pass
  --debug TARGET
                   run GDB in the interactive shell pane; TARGET is one of
                   qbox, rse, si_cl0, si_cl1, tf-a, u-boot, or linux
  --no-attach
  --dry-run
  --help

Artifact overrides:
  --rootfs FILE
  --efi-capsule-disk FILE
  --rse-rom FILE
  --rse-flash FILE
  --rse-otp FILE
  --ap-flash FILE
  --ap-bl2-elf FILE
  --rse-bl1-2-elf FILE
  --rse-bl2-elf FILE
  --provisioning-bundle FILE
  --ap-dtb FILE
  --rse-symbols FILE
  --si-cl0-image FILE
  --si-cl1-image FILE
  --si-cl1-symbols FILE
EOF
}

debug_usage()
{
    cat <<'EOF'
Available --debug targets:
  qbox, rse, si_cl0, si_cl1, tf-a, u-boot, linux
EOF
}

abspath()
{
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "$PWD" "$1" ;;
    esac
}

port_in_use()
{
    local port="$1"
    if command -v ss >/dev/null 2>&1; then
        ss -H -ltn 2>/dev/null | awk '{print $4}' |
            grep -Eq "(^|[:.])${port}$|\\]:${port}$"
        return $?
    fi
    python3 - "${port}" <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.2)
    try:
        sock.connect(("127.0.0.1", port))
    except OSError:
        sys.exit(1)
sys.exit(0)
PY
}

find_free_port()
{
    local port
    if [[ -n "${SSH_PORT:-}" ]]; then
        port="${SSH_PORT}"
        [[ "${port}" =~ ^[0-9]+$ ]] || die "SSH_PORT must be numeric: ${port}"
        port_in_use "${port}" && die "requested SSH_PORT is already in use: ${port}"
        printf '%s\n' "${port}"
        return 0
    fi
    [[ "${SSH_PORT_START}" =~ ^[0-9]+$ ]] ||
        die "SSH_PORT_START must be numeric: ${SSH_PORT_START}"
    [[ "${SSH_PORT_END}" =~ ^[0-9]+$ ]] ||
        die "SSH_PORT_END must be numeric: ${SSH_PORT_END}"
    ((SSH_PORT_START <= SSH_PORT_END)) ||
        die "SSH_PORT_START must be <= SSH_PORT_END"
    for ((port = SSH_PORT_START; port <= SSH_PORT_END; port++)); do
        if ! port_in_use "${port}"; then
            printf '%s\n' "${port}"
            return 0
        fi
    done
    die "no free SSH host-forward port in ${SSH_PORT_START}-${SSH_PORT_END}"
}

reject_removed_option()
{
    die "unsupported removed option: --$1"
}

reject_removed_environment_overrides()
{
    local name
    for name in "${REMOVED_ENV_OVERRIDES[@]}"; do
        die "unsupported removed environment override: ${name}"
    done
}

configure_debug_target()
{
    case "${DEBUG_TARGET}" in
        qbox)
            DEBUG_COMPONENT="qbox-host"
            DEBUG_ENTRYPOINT="sc_main"
            DEBUG_ENDPOINT="127.0.0.1:12339"
            ;;
        rse)
            DEBUG_COMPONENT="tfm-bl1_1"
            DEBUG_ENTRYPOINT="Reset_Handler"
            DEBUG_ENDPOINT="127.0.0.1:12340"
            DEBUG_CPU_PARAM="platform.rse_cpu_pass.cpu_0.cpu"
            DEBUG_PLATFORM_PARAMS=(
                "platform.rse_cpu_pass.cpu_0.gdb_port=12340"
            )
            ;;
        si_cl0)
            DEBUG_COMPONENT="scp-si0"
            DEBUG_ENTRYPOINT="arch_exception_reset"
            DEBUG_ENDPOINT="127.0.0.1:12341"
            DEBUG_CPU_PARAM="platform.si_cl0_cpu_0"
            DEBUG_PLATFORM_PARAMS=(
                "platform.si_cl0_cpu_0.gdb_port=12341"
            )
            ;;
        si_cl1)
            DEBUG_COMPONENT="si-cl1-zephyr"
            DEBUG_ENTRYPOINT="z_cstart"
            DEBUG_ENDPOINT="127.0.0.1:12342"
            DEBUG_CPU_PARAM="platform.si_cl1_cpu_0"
            DEBUG_PLATFORM_PARAMS=(
                "platform.si_cl1_cpu_0.gdb_port=12342"
            )
            ;;
        tf-a)
            DEBUG_COMPONENT="tfa-bl2"
            DEBUG_ENTRYPOINT="bl2_main"
            DEBUG_ENDPOINT="127.0.0.1:12343"
            DEBUG_CPU_PARAM="platform.ap_cpu_0"
            DEBUG_PLATFORM_PARAMS=(
                "platform.ap_cpu_0.gdb_port=12343"
            )
            ;;
        u-boot)
            DEBUG_COMPONENT="u-boot"
            DEBUG_ENTRYPOINT="_start"
            DEBUG_ENDPOINT="127.0.0.1:12343"
            DEBUG_CPU_PARAM="platform.ap_cpu_0"
            DEBUG_PLATFORM_PARAMS=(
                "platform.ap_cpu_0.gdb_port=12343"
            )
            ;;
        linux)
            DEBUG_COMPONENT="linux"
            DEBUG_ENTRYPOINT="start_kernel"
            DEBUG_ENDPOINT="127.0.0.1:12343"
            DEBUG_CPU_PARAM="platform.ap_cpu_0"
            DEBUG_PLATFORM_PARAMS=(
                "platform.ap_cpu_0.gdb_port=12343"
            )
            ;;
        *)
            die "invalid --debug target: ${DEBUG_TARGET}"
            ;;
    esac
    if [[ -n "${DEBUG_CPU_PARAM}" ]]; then
        DEBUG_WAIT_LOG="qbox-platform.log"
        DEBUG_WAIT_MARKER="QBox GDB entry breakpoint reached:"
    fi
}

validate_debug_manifest()
{
    local component="$1"
    local entrypoint="$2"

    python3 - "${DEBUG_MANIFEST}" "${component}" "${entrypoint}" <<'PY'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
component_name = sys.argv[2]
entrypoint = sys.argv[3]
try:
    decoded = json.loads(manifest.read_text(encoding="utf-8"))
    component = decoded["components"][component_name]
except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
    raise SystemExit(
        f"error: debug manifest has no usable {component_name} record: {error}"
    )

for field in ("elf", "gdb_script"):
    path = Path(component.get(field, ""))
    if not path.is_file():
        raise SystemExit(
            f"error: debug manifest {component_name}.{field} is missing: {path}"
        )
if component.get("has_debug_info") is not True:
    raise SystemExit(f"error: {component_name} ELF has no DWARF debug info")
if component.get("has_debug_line") is not True:
    raise SystemExit(f"error: {component_name} ELF has no DWARF source lines")
if entrypoint not in component.get("symbols", {}):
    raise SystemExit(
        f"error: {component_name} ELF has no {entrypoint} entrypoint symbol"
    )
if entrypoint not in component.get("source_locations", {}):
    raise SystemExit(
        f"error: {component_name} ELF has no source line for {entrypoint}"
    )
address = int(component["symbols"][entrypoint], 0)
if component.get("arch") == "arm":
    address &= ~1
print(hex(address))
PY
}

parse_args()
{
    while (($#)); do
        case "$1" in
            -h|--help|help)
                usage
                exit 0
                ;;
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
            --image-basename)
                (($# >= 2)) || die "--image-basename requires a value"
                IMAGE_BASENAME="$2"
                shift 2
                ;;
            --qboxconf)
                (($# >= 2)) || die "--qboxconf requires a value"
                QBOX_CONF_FILE="$2"
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
                QBOX_BUILD_DIR_EXPLICIT=1
                shift 2
                ;;
            --conf)
                (($# >= 2)) || die "--conf requires a value"
                QBOX_CONF="$2"
                QBOX_CONF_EXPLICIT=1
                shift 2
                ;;
            --session)
                (($# >= 2)) || die "--session requires a value"
                TMUX_SESSION="$2"
                TMUX_RUNNER_ARGS+=("$1" "$2")
                shift 2
                ;;
            --out-dir)
                (($# >= 2)) || die "--out-dir requires a value"
                OUT_DIR="$2"
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
            --copy-disks)
                RUN_QBOX_COPY_DISKS=1
                shift
                ;;
            --no-copy-disks)
                RUN_QBOX_COPY_DISKS=0
                shift
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            --legacy-file-backed-sram)
                LEGACY_FILE_BACKED_SRAM=1
                shift
                ;;
            --rse-state-dir)
                (($# >= 2)) || die "--rse-state-dir requires a value"
                RSE_STATE_DIR="$2"
                shift 2
                ;;
            --reset-rse-state)
                RESET_RSE_STATE=1
                shift
                ;;
            --no-persistent-rse-state)
                PERSIST_RSE_STATE=0
                shift
                ;;
            --uboot-only)
                UBOOT_ONLY=1
                KEEP_RUNNING_AFTER_PASS=0
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
            --debug)
                if (($# < 2)) || [[ "$2" == --* ]]; then
                    debug_usage
                    exit 0
                fi
                DEBUG_TARGET="$2"
                shift 2
                ;;
            --no-attach)
                TMUX_RUNNER_ARGS+=("$1")
                shift
                ;;
            --rootfs)
                (($# >= 2)) || die "--rootfs requires a value"
                ROOTFS_OVERRIDE="$2"
                shift 2
                ;;
            --efi-capsule-disk)
                (($# >= 2)) || die "--efi-capsule-disk requires a value"
                EFI_CAPSULE_DISK_OVERRIDE="$2"
                shift 2
                ;;
            --rse-rom)
                (($# >= 2)) || die "--rse-rom requires a value"
                RSE_ROM_OVERRIDE="$2"
                shift 2
                ;;
            --rse-flash)
                (($# >= 2)) || die "--rse-flash requires a value"
                RSE_FLASH_OVERRIDE="$2"
                shift 2
                ;;
            --rse-otp)
                (($# >= 2)) || die "--rse-otp requires a value"
                RSE_OTP_OVERRIDE="$2"
                shift 2
                ;;
            --ap-flash)
                (($# >= 2)) || die "--ap-flash requires a value"
                AP_FLASH_OVERRIDE="$2"
                shift 2
                ;;
            --ap-bl2-elf)
                (($# >= 2)) || die "--ap-bl2-elf requires a value"
                AP_BL2_ELF_OVERRIDE="$2"
                shift 2
                ;;
            --rse-bl1-2-elf)
                (($# >= 2)) || die "--rse-bl1-2-elf requires a value"
                RSE_BL1_2_ELF_OVERRIDE="$2"
                shift 2
                ;;
            --rse-bl2-elf)
                (($# >= 2)) || die "--rse-bl2-elf requires a value"
                RSE_BL2_ELF_OVERRIDE="$2"
                shift 2
                ;;
            --provisioning-bundle)
                (($# >= 2)) || die "--provisioning-bundle requires a value"
                PROVISIONING_BUNDLE_OVERRIDE="$2"
                shift 2
                ;;
            --ap-dtb)
                (($# >= 2)) || die "--ap-dtb requires a value"
                AP_DTB_OVERRIDE="$2"
                shift 2
                ;;
            --rse-symbols)
                (($# >= 2)) || die "--rse-symbols requires a value"
                RSE_SYMBOLS_OVERRIDE="$2"
                shift 2
                ;;
            --si-cl0-image)
                (($# >= 2)) || die "--si-cl0-image requires a value"
                SI_CL0_IMAGE_OVERRIDE="$2"
                shift 2
                ;;
            --si-cl1-image)
                (($# >= 2)) || die "--si-cl1-image requires a value"
                SI_CL1_IMAGE_OVERRIDE="$2"
                shift 2
                ;;
            --si-cl1-symbols)
                (($# >= 2)) || die "--si-cl1-symbols requires a value"
                SI_CL1_SYMBOLS_OVERRIDE="$2"
                shift 2
                ;;
            --rse-cpu-mode|--rse-cpu-mode=*)
                reject_removed_option "rse-cpu-mode"
                ;;
            --rse-hotpath-tlm-fallback)
                reject_removed_option "rse-hotpath-tlm-fallback"
                ;;
            --no-rse-hotpath-tlm-fallback)
                reject_removed_option "no-rse-hotpath-tlm-fallback"
                ;;
            --remotepass-dmi-cache|--remotepass-dmi-cache=*)
                reject_removed_option "remotepass-dmi-cache"
                ;;
            --)
                shift
                EXTRA_CHILD_ARGS+=("$@")
                break
                ;;
            *)
                TMUX_RUNNER_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

require_override_file()
{
    local label="$1"
    local path="$2"
    [[ -f "${path}" ]] || die "${label} not found: ${path}"
    printf '%s\n' "${path}"
}

artifact_path()
{
    local label="$1"
    local override="$2"
    local local_path="$3"
    local qboxconf_path="$4"
    if [[ -n "${override}" ]]; then
        require_override_file "${label}" "${override}"
        return 0
    fi
    if [[ -f "${local_path}" || "${DRY_RUN}" == "1" ]]; then
        printf '%s\n' "${local_path}"
        return 0
    fi
    if [[ -n "${qboxconf_path}" && -f "${qboxconf_path}" ]]; then
        printf '%s\n' "${qboxconf_path}"
        return 0
    fi
    die "missing ${label}: ${local_path}"
}

read_yocto_local_build_var()
{
    local recipe="$1"
    local variable="$2"
    local cache="${LOCAL_BUILD_DIR}/yocto-local-build-vars.json"

    [[ -f "${cache}" ]] || return 1
    "${PYTHON:-python3}" - "${cache}" "${recipe}" "${variable}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path


cache = Path(sys.argv[1])
recipe = sys.argv[2]
variable = sys.argv[3]
try:
    data = json.loads(cache.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
recipes = data.get("recipes")
if not isinstance(recipes, dict):
    raise SystemExit(1)
entry = recipes.get(recipe)
if not isinstance(entry, dict):
    raise SystemExit(1)
variables = entry.get("variables")
if not isinstance(variables, dict):
    raise SystemExit(1)
value = str(variables.get(variable, "")).strip()
if not value:
    raise SystemExit(1)
print(value)
PY
}

copy_image()
{
    local src="$1"
    local dst="$2"
    [[ -f "${src}" ]] || die "missing input image: ${src}"
    mkdir -p "$(dirname "${dst}")"
    cp --reflink=auto --sparse=always -- "${src}" "${dst}"
}

main()
{
    reject_removed_environment_overrides
    parse_args "$@"
    require_safe_token MACHINE "${MACHINE}"
    if [[ -n "${DEBUG_TARGET}" ]]; then
        configure_debug_target
    fi

    YOCTO_BUILD_DIR="$(abspath "${YOCTO_BUILD_DIR}")"
    WORK_PREFIX="$(machine_to_work_prefix "${MACHINE}")"
    DEPLOY_DIR="${DEPLOY_DIR:-${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/images/${MACHINE}}"
    DEPLOY_DIR="$(abspath "${DEPLOY_DIR}")"
    LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${YOCTO_BUILD_DIR}/local-${MACHINE}}"
    LOCAL_BUILD_DIR="$(abspath "${LOCAL_BUILD_DIR}")"
    OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-${MACHINE}/full-user-demo-${RUN_STAMP}}"
    OUT_DIR="$(abspath "${OUT_DIR}")"
    QBOX_PLATFORM_DIR="$(abspath "${QBOX_PLATFORM_DIR}")"
    LOCAL_QBOX_BUILD_DIR="${LOCAL_BUILD_DIR}/work/qbox-platform"
    LOCAL_QBOX_CONF="${QBOX_PLATFORM_DIR}/platforms/apollo/${MACHINE}.lua"
    LOCAL_QBOX_AVAILABLE=0
    if [[ -x "${LOCAL_QBOX_BUILD_DIR}/platforms-vp" ]]; then
        LOCAL_QBOX_AVAILABLE=1
    fi

    if [[ "${MACHINE}" == "apollo-qvp" ]]; then
        QBOX_CONF_FILE="${QBOX_CONF_FILE:-$(resolve_qboxconf_default)}"
        qboxconf_assignments="$(read_qboxconf_shell_assignments "${QBOX_CONF_FILE}")" ||
            die "failed to read qboxconf: ${QBOX_CONF_FILE}"
        eval "${qboxconf_assignments}"
        if [[ "${QBOX_BUILD_DIR_EXPLICIT}" == "0" ]]; then
            if [[ "${LOCAL_QBOX_AVAILABLE}" == "1" ]]; then
                QBOX_BUILD_DIR="${LOCAL_QBOX_BUILD_DIR}"
            else
                QBOX_BUILD_DIR="${QBOXCONF_PROVIDER_BINDIR}"
            fi
        fi
        if [[ "${QBOX_CONF_EXPLICIT}" == "0" ]]; then
            if [[ "${QBOX_BUILD_DIR}" == "${LOCAL_QBOX_BUILD_DIR}" && -f "${LOCAL_QBOX_CONF}" ]]; then
                QBOX_CONF="${LOCAL_QBOX_CONF}"
            else
                QBOX_CONF="${QBOXCONF_CONFIG}"
            fi
        fi
        if [[ -n "${QBOXCONF_LD_LIBRARY_PATH:-}" ]]; then
            export LD_LIBRARY_PATH="${QBOXCONF_LD_LIBRARY_PATH}"
        fi
    else
        QBOX_CONF="${QBOX_CONF:-${QBOX_PLATFORM_DIR}/platforms/apollo/apollo-qvp.lua}"
        QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-${LOCAL_QBOX_BUILD_DIR}}"
    fi

    QBOX_CONF="$(abspath "${QBOX_CONF}")"
    QBOX_BUILD_DIR="$(abspath "${QBOX_BUILD_DIR}")"
    QBOX_PLATFORM_BUILD_DIR="${QBOX_BUILD_DIR}"
    export QBOX_PLATFORM_DIR QBOX_CONF QBOX_PLATFORM_BUILD_DIR QBOX_BUILD_DIR

    if [[ "${DRY_RUN}" != "1" ]]; then
        [[ -d "${LOCAL_BUILD_DIR}" ]] ||
            die "missing local build directory: ${LOCAL_BUILD_DIR}. Run ./local_build.sh build first."
    fi
    [[ -f "${QBOX_CONF}" ]] || die "QBox config not found: ${QBOX_CONF}"
    if [[ "${DRY_RUN}" != "1" ]]; then
        [[ -d "${QBOX_BUILD_DIR}" ]] || die "QBox build directory not found: ${QBOX_BUILD_DIR}. Build QBox first with ./local_build.sh qbox or set --qbox-build-dir."
        [[ -x "${QBOX_BUILD_DIR}/platforms-vp" ]] ||
            die "QBox executable not found or not executable: ${QBOX_BUILD_DIR}/platforms-vp"
    fi
    if [[ -n "${DEBUG_TARGET}" ]]; then
        DEBUG_MANIFEST="${LOCAL_BUILD_DIR}/debug/symbols.json"
        DEBUG_GDB_SCRIPT="${LOCAL_BUILD_DIR}/debug/gdb/${DEBUG_COMPONENT}.gdb"
        if [[ "${DRY_RUN}" != "1" ]]; then
            command -v python3 >/dev/null 2>&1 || die "python3 is required for --debug"
            command -v gdb-multiarch >/dev/null 2>&1 ||
                die "gdb-multiarch is required for --debug"
            if [[ "${DEBUG_TARGET}" == "qbox" ]]; then
                command -v gdb >/dev/null 2>&1 || die "gdb is required for --debug qbox"
                command -v gdbserver >/dev/null 2>&1 ||
                    die "gdbserver is required for --debug qbox"
            fi
            python3 "${ROOT_DIR}/scripts/setup/setup_local_debug_env.py" \
                --local-build-dir "${LOCAL_BUILD_DIR}" \
                --out-dir "${LOCAL_BUILD_DIR}/debug"
            DEBUG_ENTRY_ADDRESS="$(
                validate_debug_manifest \
                    "${DEBUG_COMPONENT}" "${DEBUG_ENTRYPOINT}"
            )"
            if [[ -n "${DEBUG_CPU_PARAM}" ]]; then
                DEBUG_PLATFORM_PARAMS+=(
                    "${DEBUG_CPU_PARAM}.gdb_breakpoint=${DEBUG_ENTRY_ADDRESS}"
                )
            fi
            debug_port="${DEBUG_ENDPOINT##*:}"
            port_in_use "${debug_port}" &&
                die "GDB port is already in use: ${debug_port}"
        fi
    fi

    if [[ -z "${QBOX_APOLLO_NUM_CPUS}" ]]; then
        QBOX_APOLLO_NUM_CPUS="$(
            read_yocto_local_build_var nexios-image PC_CPUS_COUNT_DEFAULT || true
        )"
    fi
    if [[ -n "${QBOX_APOLLO_NUM_CPUS}" ]]; then
        [[ "${QBOX_APOLLO_NUM_CPUS}" =~ ^[0-9]+$ ]] ||
            die "QBOX_APOLLO_NUM_CPUS must be numeric: ${QBOX_APOLLO_NUM_CPUS}"
        ((QBOX_APOLLO_NUM_CPUS >= 1 && QBOX_APOLLO_NUM_CPUS <= 16)) ||
            die "QBOX_APOLLO_NUM_CPUS must be in range 1..16: ${QBOX_APOLLO_NUM_CPUS}"
        export QBOX_APOLLO_NUM_CPUS
    fi

    PRIMARY_LOGIN_PROMPT="${PRIMARY_LOGIN_PROMPT:-NEXIOS_BSP_INITRAMFS_READY}"
    PRIMARY_SHELL_MARKER="${PRIMARY_SHELL_MARKER:-nexios-bsp#}"
    PRIMARY_SHELL_PROMPT_RE="${PRIMARY_SHELL_PROMPT_RE:-(?:^|\\n)nexios-bsp#\\s*$}"
    RSE_STATE_DIR="${RSE_STATE_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/state/local-${MACHINE}}"
    if [[ "${RESET_RSE_STATE}" == "1" && "${PERSIST_RSE_STATE}" != "1" ]]; then
        die "--reset-rse-state cannot be used with --no-persistent-rse-state"
    fi

    local rootfs_src="${LOCAL_BUILD_DIR}/deploy/boot/${MACHINE}-local-disk.img"
    local efi_src="${LOCAL_BUILD_DIR}/deploy/boot/boot-fat.img"
    local uki_a="${LOCAL_BUILD_DIR}/deploy/boot/auto-ad-nexios-a.efi"
    local uki_b="${LOCAL_BUILD_DIR}/deploy/boot/auto-ad-nexios-b.efi"
    local boot_profile="local-uki-bsp"
    if [[ -n "${ROOTFS_OVERRIDE}" ]]; then
        boot_profile="custom-rootfs"
    elif [[ "${DRY_RUN}" != "1" ]]; then
        [[ -f "${uki_a}" ]] ||
            die "missing local slot A UKI: ${uki_a}. Run ./local_build.sh boot-disk first."
        [[ -f "${uki_b}" ]] ||
            die "missing local slot B UKI: ${uki_b}. Run ./local_build.sh boot-disk first."
    fi
    RUN_ROOTFS="$(artifact_path "local Buildroot boot disk" "${ROOTFS_OVERRIDE}" "${rootfs_src}" "")"
    RUN_EFI_CAPSULE_DISK="$(artifact_path "local EFI capsule disk" "${EFI_CAPSULE_DISK_OVERRIDE}" "${efi_src}" "${QBOXCONF_IMAGE_EFI_CAPSULE_DISK:-}")"
    RSE_ROM="$(artifact_path "RSE ROM image" "${RSE_ROM_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/rse-rom-image.img" "${QBOXCONF_IMAGE_RSE_ROM:-}")"
    RSE_FLASH="$(artifact_path "RSE flash image" "${RSE_FLASH_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/rse-flash-image.img" "${QBOXCONF_IMAGE_RSE_FLASH:-}")"
    RSE_OTP="$(artifact_path "RSE OTP image" "${RSE_OTP_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/rse-otp-image.img" "${QBOXCONF_IMAGE_RSE_OTP:-}")"
    AP_FLASH="$(artifact_path "AP flash image" "${AP_FLASH_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/ap-flash-image.img" "${QBOXCONF_IMAGE_AP_FLASH:-}")"
    AP_BL2_ELF="$(artifact_path "AP TF-A BL2 ELF" "${AP_BL2_ELF_OVERRIDE}" "${LOCAL_BUILD_DIR}/work/trusted-firmware-a/${WORK_PREFIX}/debug/bl2/bl2.elf" "${QBOXCONF_IMAGE_AP_BL2_ELF:-}")"
    RSE_BL1_2_ELF="$(artifact_path "RSE TF-M BL1_2 ELF" "${RSE_BL1_2_ELF_OVERRIDE}" "${LOCAL_BUILD_DIR}/work/trusted-firmware-m/bin/bl1_2.elf" "${QBOXCONF_IMAGE_RSE_BL1_2_ELF:-}")"
    RSE_BL2_ELF="$(artifact_path "RSE TF-M BL2 ELF" "${RSE_BL2_ELF_OVERRIDE}" "${LOCAL_BUILD_DIR}/work/trusted-firmware-m/bin/bl2.elf" "${QBOXCONF_IMAGE_RSE_BL2_ELF:-}")"
    PROVISIONING_BUNDLE="$(artifact_path "combined provisioning bundle" "${PROVISIONING_BUNDLE_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/combined_provisioning_message.bin" "${QBOXCONF_IMAGE_PROVISIONING_BUNDLE:-}")"
    AP_DTB="$(artifact_path "AP device tree" "${AP_DTB_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/boot/${MACHINE}.dtb" "${QBOXCONF_IMAGE_AP_DTB:-}")"
    SI_CL0_IMAGE="$(artifact_path "Safety Island CL0 SCP image" "${SI_CL0_IMAGE_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/si0_ramfw.bin" "${QBOXCONF_IMAGE_SI_CL0:-}")"
    SI_CL1_IMAGE="$(artifact_path "Safety Island CL1 Zephyr image" "${SI_CL1_IMAGE_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/zephyr-demos-cl1.bin" "${QBOXCONF_IMAGE_SI_CL1:-}")"
    SI_CL1_SYMBOLS="$(artifact_path "Safety Island CL1 Zephyr symbols" "${SI_CL1_SYMBOLS_OVERRIDE}" "${LOCAL_BUILD_DIR}/deploy/firmware/zephyr-demos-cl1.elf" "${QBOXCONF_IMAGE_SI_CL1_SYMBOLS:-}")"
    RSE_SYMBOLS=""
    if [[ -n "${RSE_SYMBOLS_OVERRIDE}" ]]; then
        RSE_SYMBOLS="$(require_override_file "QBox RSE debug symbol manifest" "${RSE_SYMBOLS_OVERRIDE}")"
    elif [[ -f "${LOCAL_BUILD_DIR}/debug/symbols.json" || "${DRY_RUN}" == "1" ]]; then
        RSE_SYMBOLS="${LOCAL_BUILD_DIR}/debug/symbols.json"
    elif [[ -n "${QBOXCONF_DEBUG_SYMBOLS:-}" && -f "${QBOXCONF_DEBUG_SYMBOLS}" ]]; then
        RSE_SYMBOLS="${QBOXCONF_DEBUG_SYMBOLS}"
    fi

    if [[ "${RUN_QBOX_COPY_DISKS}" == "1" ]]; then
        local image_dir="${OUT_DIR}/input-images"
        local copied_rootfs
        local copied_efi
        copied_rootfs="${image_dir}/$(basename "${RUN_ROOTFS}")"
        copied_efi="${image_dir}/$(basename "${RUN_EFI_CAPSULE_DISK}")"
        if [[ "${DRY_RUN}" != "1" ]]; then
            copy_image "${RUN_ROOTFS}" "${copied_rootfs}"
            copy_image "${RUN_EFI_CAPSULE_DISK}" "${copied_efi}"
        fi
        RUN_ROOTFS="${copied_rootfs}"
        RUN_EFI_CAPSULE_DISK="${copied_efi}"
    fi

    local ssh_port
    local netdev
    ssh_port="$(find_free_port)"
    netdev="${QBOX_NETDEV:-type=user,hostfwd=tcp::${ssh_port}-:22}"

    printf 'Apollo QBox local launch\n'
    printf '  machine: %s\n' "${MACHINE}"
    printf '  qboxconf: %s\n' "${QBOX_CONF_FILE:-}"
    printf '  session: %s\n' "${TMUX_SESSION:-apollo-qbox-demo-${RUN_STAMP}}"
    printf '  out_dir: %s\n' "${OUT_DIR}"
    printf '  local_build_dir: %s\n' "${LOCAL_BUILD_DIR}"
    printf '  qbox_platform_dir: %s\n' "${QBOX_PLATFORM_DIR}"
    printf '  qbox_conf: %s\n' "${QBOX_CONF}"
    printf '  qbox_build_dir: %s\n' "${QBOX_BUILD_DIR}"
    printf '  ap_cpus: %s\n' "${QBOX_APOLLO_NUM_CPUS:-default}"
    printf '  boot_profile: %s\n' "${boot_profile}"
    printf '  rootfs: %s\n' "${RUN_ROOTFS}"
    printf '  uki_slot_a: %s\n' "${uki_a}"
    printf '  uki_slot_b: %s\n' "${uki_b}"
    printf '  efi_capsule_disk: %s\n' "${RUN_EFI_CAPSULE_DISK}"
    if [[ "${PERSIST_RSE_STATE}" == "1" ]]; then
        printf '  rse_flash_state: %s\n' "${RSE_STATE_DIR}/rse-flash-image.img"
    else
        printf '  rse_flash_state: ephemeral\n'
    fi
    printf '  ssh: host port %s -> guest port 22\n' "${ssh_port}"
    printf '  netdev: %s\n' "${netdev}"
    if [[ -n "${DEBUG_TARGET}" ]]; then
        printf '  debug_target: %s\n' "${DEBUG_TARGET}"
        printf '  debug_component: %s\n' "${DEBUG_COMPONENT}"
        printf '  debug_entrypoint: %s\n' "${DEBUG_ENTRYPOINT}"
        [[ -n "${DEBUG_ENTRY_ADDRESS}" ]] &&
            printf '  debug_entry_address: %s\n' "${DEBUG_ENTRY_ADDRESS}"
        printf '  debug_endpoint: %s\n' "${DEBUG_ENDPOINT}"
        printf '  debug_manifest: %s\n' "${DEBUG_MANIFEST}"
        if [[ -n "${DEBUG_WAIT_LOG}" ]]; then
            printf '  debug_attach_gate: %s contains %s\n' \
                "${DEBUG_WAIT_LOG}" "${DEBUG_WAIT_MARKER}"
        fi
    fi

    local rse_fast_boot_mode="--rse-fast-boot-sram-dmi"
    if ((LEGACY_FILE_BACKED_SRAM)); then
        rse_fast_boot_mode="--rse-fast-boot-aliases"
    fi

    local runner_cmd=(
        "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
        --session "${TMUX_SESSION:-apollo-qbox-demo-${RUN_STAMP}}"
        --out-dir "${OUT_DIR}"
        --local-build-dir "${LOCAL_BUILD_DIR}"
        --qbox-build-dir "${QBOX_BUILD_DIR}"
        --conf "${QBOX_CONF}"
        --si-mode "${SI_MODE}"
        --timeout "${TIMEOUT}"
        --jobs "${JOBS}"
        --skip-build
        --rootfs-bootargs-profile none
        --primary-login-prompt "${PRIMARY_LOGIN_PROMPT}"
        --primary-shell-marker "${PRIMARY_SHELL_MARKER}"
        --primary-shell-prompt-re "${PRIMARY_SHELL_PROMPT_RE}"
        --qbox-performance-preset
        --cc3xx-qemu-native-backend
        --netdev "${netdev}"
        --tmux-layout fvp-like
    )
    if [[ -n "${DEBUG_TARGET}" ]]; then
        runner_cmd+=(
            --debug-target "${DEBUG_TARGET}"
            --debug-component "${DEBUG_COMPONENT}"
            --debug-endpoint "${DEBUG_ENDPOINT}"
            --debug-manifest "${DEBUG_MANIFEST}"
        )
        if [[ -n "${DEBUG_WAIT_LOG}" ]]; then
            runner_cmd+=(
                --debug-wait-log "${OUT_DIR}/${DEBUG_WAIT_LOG}"
                --debug-wait-marker "${DEBUG_WAIT_MARKER}"
            )
        fi
    fi
    if [[ "${KEEP_RUNNING_AFTER_PASS}" == "1" ]]; then
        runner_cmd+=(--keep-running-after-pass)
    else
        runner_cmd+=(--exit-after-pass)
    fi
    if [[ "${DRY_RUN}" == "1" ]]; then
        runner_cmd+=(--dry-run)
    fi
    runner_cmd+=("${TMUX_RUNNER_ARGS[@]}")
    runner_cmd+=(--)
    runner_cmd+=(
        --no-post-login-probe
        --rse-rom "${RSE_ROM}"
        --rse-flash "${RSE_FLASH}"
        --rse-otp "${RSE_OTP}"
        --ap-flash "${AP_FLASH}"
        --ap-bl2-elf "${AP_BL2_ELF}"
        --rse-bl1-2-elf "${RSE_BL1_2_ELF}"
        --rse-bl2-elf "${RSE_BL2_ELF}"
        --rootfs "${RUN_ROOTFS}"
        --efi-capsule-disk "${RUN_EFI_CAPSULE_DISK}"
        --provisioning-bundle "${PROVISIONING_BUNDLE}"
        --ap-dtb "${AP_DTB}"
        --si-cl0-image "${SI_CL0_IMAGE}"
        --si-cl1-image "${SI_CL1_IMAGE}"
        --si-cl1-symbols "${SI_CL1_SYMBOLS}"
    )
    if [[ "${PERSIST_RSE_STATE}" == "1" ]]; then
        runner_cmd+=(
            --rse-flash-state "${RSE_STATE_DIR}/rse-flash-image.img"
        )
        if [[ "${RESET_RSE_STATE}" == "1" ]]; then
            runner_cmd+=(--reset-rse-flash-state)
        fi
    fi
    if [[ "${UBOOT_ONLY}" == "1" ]]; then
        runner_cmd+=(--uboot-only)
    fi
    if [[ -n "${RSE_SYMBOLS}" ]]; then
        runner_cmd+=(--rse-symbols "${RSE_SYMBOLS}")
    fi
    if [[ -n "${DEBUG_TARGET}" ]]; then
        runner_cmd+=(--ignore-fail-patterns)
        if [[ "${DEBUG_TARGET}" == "qbox" ]]; then
            export QBOX_HOST_GDB_EXEC="${ROOT_DIR}/scripts/debug/gdbserver_gdb_wrapper.sh"
            export QBOX_HOST_GDBSERVER_ENDPOINT="${DEBUG_ENDPOINT}"
            runner_cmd+=(--host-gdb-script "${DEBUG_GDB_SCRIPT}")
        fi
        local debug_param
        for debug_param in "${DEBUG_PLATFORM_PARAMS[@]}"; do
            runner_cmd+=(--platform-param "${debug_param}")
        done
    fi
    runner_cmd+=(
        --rse-hotpath-accel
        --rse-lms-accel
        "${rse_fast_boot_mode}"
        --rse-bl2-libc-hotpath
        --rse-bl2-delay-accel
        --rse-bl2-load-accel
        --rse-bl2-boot-enc-accel
        --rse-bl2-img-hash-accel
        --rse-bl2-verify-sig-accel
    )
    runner_cmd+=("${EXTRA_CHILD_ARGS[@]}")

    exec "${runner_cmd[@]}"
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}"
source "${ROOT_DIR}/scripts/run/qbox_qboxconf_common.sh"
source "${ROOT_DIR}/scripts/run/qbox_debug_common.sh"

die() {
    echo "run_qbox_yocto.sh: error: $*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage: ./run_qbox_yocto.sh [options] [-- extra-qbox-runner-options]

Run the Apollo Yocto image on QBox using the Apollo full-system runner.
The default tmux panes use the same primary-console-focused split pattern as
run_fvp.sh. Use --headless for file-backed regression runs without tmux.

Options:
  --machine NAME              Yocto machine name (default: apollo-qvp)
  --bsp                       Boot nexios-bsp-initramfs from its boot-only WIC
  --build-dir DIR             Yocto build directory (default: ./build)
  --deploy-dir DIR            Yocto deploy image directory
  --work-dir DIR              Yocto machine work directory
  --image-basename NAME       Yocto image recipe basename (default: nexios-image)
  --qboxconf FILE             Yocto-deployed QBox JSON configuration
  --local-build-dir DIR       Local-build directory used for QBox build/debug files
  --qbox-tool-dir DIR         Yocto QBox provider executable directory
  --qbox-build-dir DIR        QBox platform build directory
  --conf FILE                 QBox Lua configuration
  --session NAME              tmux session name
  --out-dir DIR               Runtime output directory
  --timeout SECONDS           Runner timeout, 0 keeps interactive run alive
  --jobs N                    Build jobs when the QBox runner builds dependencies
  --rootfs-bootargs-profile P Rootfs bootargs profile (default: none)
  --copy-disks                Copy writable rootfs/EFI disks into --out-dir first
  --no-copy-disks             Use Yocto deploy disk images in place (default)
  --record-initial-state      Write a pre-run SHA-256 artifact manifest (slow)
  --no-record-initial-state   Skip full-image hashing before launch (default)
  --legacy-file-backed-sram   Disable RSE SRAM fast-boot DMI accelerator
  --rse-state-dir DIR         Persistent RSE flash state directory
  --reset-rse-state           Reset persistent state from the selected image
  --no-persistent-rse-state   Use a pristine per-run RSE flash copy
  --uboot-only                Validate only through U-Boot FWU Regular State
  --headless                  Run without tmux and write logs under --out-dir
  --keep-running-after-pass   Keep QBox alive after the pass condition (default)
  --exit-after-pass           Stop QBox after the pass condition
  --debug TARGET              Run GDB in the interactive pane; TARGET is one of
                              qbox, rse, si_cl0, si_cl1, tf-a, u-boot, or linux
  --debug-mode MODE           interactive, probe, or server
                              (default: interactive)
  --debug-timeout SEC         probe/server deadline in seconds (default: 600)
  --debug-result PATH         probe/server JSON result path
  --no-attach                 Start tmux session without attaching
  --multi-session             Preserve existing QBox and tmux sessions
  --dry-run                   Print the underlying QBox runner command
  --help                      Show this help

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

Useful environment variables:
  MACHINE, YOCTO_BUILD_DIR, DEPLOY_DIR, YOCTO_WORK_DIR, IMAGE_BASENAME,
  QBOX_CONF_FILE, LOCAL_BUILD_DIR, QBOX_TOOL_DIR, QBOX_BUILD_DIR, QBOX_CONF,
  OUT_DIR, TMUX_SESSION, TIMEOUT, JOBS, RUN_QBOX_COPY_DISKS, SSH_PORT,
  RUN_QBOX_RECORD_INITIAL_STATE, QBOX_RSE_STATE_DIR, QBOX_PERSIST_RSE_STATE
EOF
}

machine_to_work_prefix() {
    local machine="$1"
    printf '%s\n' "${machine//-/_}"
}

latest_glob() {
    local pattern="$1"
    local matches=()
    local path
    while IFS= read -r path; do
        [[ -f "${path}" ]] || continue
        matches+=("${path}")
    done < <(compgen -G "${pattern}" || true)

    ((${#matches[@]} > 0)) || return 1
    printf '%s\n' "${matches[@]}" \
        | while IFS= read -r path; do
            printf '%s\t%s\n' "$(stat -c '%Y' "${path}")" "${path}"
        done \
        | sort -nr \
        | sed -n '1s/^[^	]*	//p'
}

resolve_file() {
    local label="$1"
    shift

    local tried=()
    local candidate
    for candidate in "$@"; do
        [[ -n "${candidate}" ]] || continue
        tried+=("${candidate}")
        if [[ -f "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done

    {
        echo "missing required ${label}"
        for candidate in "${tried[@]}"; do
            echo "  tried: ${candidate}"
        done
    } >&2
    exit 1
}

resolve_file_with_glob() {
    local label="$1"
    local fixed="$2"
    local pattern="$3"

    if [[ -n "${fixed}" && -f "${fixed}" ]]; then
        printf '%s\n' "${fixed}"
        return 0
    fi

    local latest=""
    if [[ -n "${pattern}" ]]; then
        latest="$(latest_glob "${pattern}" || true)"
    fi
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    {
        echo "missing required ${label}"
        [[ -n "${fixed}" ]] && echo "  tried: ${fixed}"
        [[ -n "${pattern}" ]] && echo "  tried glob: ${pattern}"
    } >&2
    exit 1
}

resolve_file_with_two_globs() {
    local label="$1"
    local fixed_primary="$2"
    local pattern_primary="$3"
    local fixed_fallback="$4"
    local pattern_fallback="$5"

    if [[ -n "${fixed_primary}" && -f "${fixed_primary}" ]]; then
        printf '%s\n' "${fixed_primary}"
        return 0
    fi

    local latest=""
    if [[ -n "${pattern_primary}" ]]; then
        latest="$(latest_glob "${pattern_primary}" || true)"
        if [[ -n "${latest}" ]]; then
            printf '%s\n' "${latest}"
            return 0
        fi
    fi

    if [[ -n "${fixed_fallback}" && -f "${fixed_fallback}" ]]; then
        printf '%s\n' "${fixed_fallback}"
        return 0
    fi

    if [[ -n "${pattern_fallback}" ]]; then
        latest="$(latest_glob "${pattern_fallback}" || true)"
        if [[ -n "${latest}" ]]; then
            printf '%s\n' "${latest}"
            return 0
        fi
    fi

    {
        echo "missing required ${label}"
        [[ -n "${fixed_primary}" ]] && echo "  tried: ${fixed_primary}"
        [[ -n "${pattern_primary}" ]] && echo "  tried glob: ${pattern_primary}"
        [[ -n "${fixed_fallback}" ]] && echo "  tried: ${fixed_fallback}"
        [[ -n "${pattern_fallback}" ]] && echo "  tried glob: ${pattern_fallback}"
    } >&2
    exit 1
}

resolve_qboxconf_default() {
    local fixed="${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}.qboxconf"
    if [[ -f "${fixed}" ]]; then
        printf '%s\n' "${fixed}"
        return 0
    fi

    local latest=""
    latest="$(latest_glob "${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    local imgdeploy_pattern="${YOCTO_BUILD_DIR}/tmp_baremetal/work/${WORK_PREFIX}-poky-linux/${IMAGE_BASENAME}/*/deploy-${IMAGE_BASENAME}-image-complete"
    latest="$(latest_glob "${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    latest="$(latest_glob "${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    {
        echo "missing required QBox qboxconf"
        echo "  tried: ${fixed}"
        echo "  tried glob: ${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf"
        echo "  tried glob: ${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}.qboxconf"
        echo "  tried glob: ${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf"
    } >&2
    exit 1
}

read_qboxconf_shell_assignments() {
    local qboxconf="$1"
    local current_ld_library_path="${LD_LIBRARY_PATH:-}"

    "${PYTHON:-python3}" - "${qboxconf}" "${current_ld_library_path}" "${YOCTO_BUILD_DIR}" <<'PY'
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import shlex
import sys
from typing import TypeAlias


class QBoxConfError(Exception):
    pass


JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
EXPECTED_PROVIDER = "qbox-apollo-qvp-native"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def require_object(value: JsonObject, field: str) -> JsonObject:
    item = value.get(field)
    if not isinstance(item, dict):
        raise QBoxConfError(f"qboxconf field {field} must be an object")
    return item


def require_string(value: JsonObject, field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or item == "":
        raise QBoxConfError(f"qboxconf field {field} must be a non-empty string")
    return item


def require_safe_relative(value: str, field: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise QBoxConfError(f"qboxconf field {field} must be a safe relative path")
    return value


def resolve_existing_dir(value: str, field: str) -> Path:
    try:
        resolved = Path(value).resolve(strict=True)
    except OSError as error:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to an existing directory: {value}: {error}"
        ) from error
    if not resolved.is_dir():
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to an existing directory: {value}"
        )
    return resolved


def relative_to_trusted(path: Path, root: Path, field: str) -> tuple[str, ...]:
    try:
        return path.relative_to(root).parts
    except ValueError as error:
        raise QBoxConfError(
            f"qboxconf trust error: {field} resolves outside trusted Yocto path {root}: {path}"
        ) from error


def validate_provider_dir(
    value: str,
    field: str,
    components_root: Path,
    provider_usr: Path | None,
) -> tuple[Path, Path]:
    resolved = resolve_existing_dir(value, field)
    relative_parts = relative_to_trusted(resolved, components_root, field)
    if (
        len(relative_parts) < 4
        or relative_parts[1] != EXPECTED_PROVIDER
        or relative_parts[2] != "usr"
    ):
        raise QBoxConfError(
            f"qboxconf trust error: {field} must be under "
            f"{components_root}/<arch>/{EXPECTED_PROVIDER}/usr: {resolved}"
        )
    candidate_provider_usr = components_root.joinpath(
        relative_parts[0],
        EXPECTED_PROVIDER,
        "usr",
    )
    if provider_usr is not None and candidate_provider_usr != provider_usr:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must use provider subtree {provider_usr}: {resolved}"
        )
    return resolved, candidate_provider_usr


def require_exact_path(path: Path, expected: Path, field: str) -> None:
    if path != expected:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to {expected}: {path}"
        )


def require_under(path: Path, root: Path, field: str) -> None:
    relative_to_trusted(path, root, field)


def validate_trusted_paths(
    provider: JsonObject,
    sysroot: JsonObject,
    yocto_build_dir: Path,
) -> tuple[Path, Path, Path, Path, Path]:
    provider_name = require_string(provider, "name")
    if provider_name != EXPECTED_PROVIDER:
        raise QBoxConfError(
            f"qboxconf trust error: provider.name must be {EXPECTED_PROVIDER}: {provider_name}"
        )

    tmpdir = yocto_build_dir / "tmp_baremetal"
    expected_components_root = (tmpdir / "sysroots-components").resolve(strict=True)
    expected_work_root = (tmpdir / "work").resolve(strict=True)
    configured_components_root = resolve_existing_dir(
        require_string(sysroot, "components_dir"),
        "sysroot.components_dir",
    )
    require_exact_path(
        configured_components_root,
        expected_components_root,
        "sysroot.components_dir",
    )

    provider_usr: Path | None = None
    bindir, provider_usr = validate_provider_dir(
        require_string(provider, "bindir"),
        "provider.bindir",
        expected_components_root,
        provider_usr,
    )
    libdir, provider_usr = validate_provider_dir(
        require_string(provider, "libdir"),
        "provider.libdir",
        expected_components_root,
        provider_usr,
    )
    module_dir, provider_usr = validate_provider_dir(
        require_string(provider, "module_dir"),
        "provider.module_dir",
        expected_components_root,
        provider_usr,
    )
    data_dir, provider_usr = validate_provider_dir(
        require_string(provider, "data_dir"),
        "provider.data_dir",
        expected_components_root,
        provider_usr,
    )
    require_exact_path(bindir, provider_usr / "bin", "provider.bindir")
    require_exact_path(libdir, provider_usr / "lib", "provider.libdir")
    require_under(module_dir, provider_usr / "lib" / "qbox", "provider.module_dir")
    require_exact_path(data_dir, provider_usr / "share" / "qbox", "provider.data_dir")

    recipe_sysroot_native = resolve_existing_dir(
        require_string(sysroot, "recipe_sysroot_native"),
        "sysroot.recipe_sysroot_native",
    )
    require_under(
        recipe_sysroot_native,
        expected_work_root,
        "sysroot.recipe_sysroot_native",
    )
    return bindir, libdir, module_dir, data_dir, recipe_sysroot_native


def quote_assignment(name: str, value: str) -> str:
    return f"{name}={shlex.quote(value)}"


def image_path(images: JsonObject, qboxconf_dir: Path, *keys: str) -> str:
    for key in keys:
        item = images.get(key)
        if isinstance(item, str) and item:
            return str(qboxconf_dir / require_safe_relative(item, f"images.{key}"))
    return ""


raw_qboxconf = Path(sys.argv[1])
current_ld_library_path = sys.argv[2]
raw_yocto_build_dir = Path(sys.argv[3])
if not raw_qboxconf.is_file():
    fail(f"qboxconf not found: {raw_qboxconf}")
qboxconf = raw_qboxconf.resolve()
try:
    yocto_build_dir = raw_yocto_build_dir.resolve(strict=True)
except OSError as error:
    fail(f"Yocto build directory not found: {raw_yocto_build_dir}: {error}")

try:
    loaded = json.loads(qboxconf.read_text(encoding="utf-8"))
except json.JSONDecodeError as error:
    fail(f"invalid qboxconf JSON: {qboxconf}: line {error.lineno} column {error.colno}: {error.msg}")
except OSError as error:
    fail(f"unable to read qboxconf: {qboxconf}: {error}")

if not isinstance(loaded, dict):
    fail(f"invalid qboxconf schema: {qboxconf}: root must be an object")

try:
    provider = require_object(loaded, "provider")
    sysroot = require_object(loaded, "sysroot")
    bindir_path, libdir_path, module_dir_path, data_dir_path, recipe_sysroot_native_path = (
        validate_trusted_paths(provider, sysroot, yocto_build_dir)
    )
    bindir = str(bindir_path)
    libdir = str(libdir_path)
    module_dir = str(module_dir_path)
    data_dir = str(data_dir_path)
    recipe_sysroot_native = str(recipe_sysroot_native_path)
    exe = require_safe_relative(require_string(loaded, "exe"), "exe")
    config = require_safe_relative(require_string(loaded, "config"), "config")
except QBoxConfError as error:
    fail(f"invalid qboxconf schema: {qboxconf}: {error}")

debug_symbols_value = loaded.get("debug_symbols")
debug_symbols = debug_symbols_value if isinstance(debug_symbols_value, str) else ""
images_value = loaded.get("images")
images = images_value if isinstance(images_value, dict) else {}
qboxconf_dir = qboxconf.parent
ld_entries = [libdir, module_dir]
recipe_sysroot_native_libdir = recipe_sysroot_native_path / "usr" / "lib"
if recipe_sysroot_native_libdir.is_dir():
    ld_entries.append(str(recipe_sysroot_native_libdir))
if current_ld_library_path:
    ld_entries.append(current_ld_library_path)

assignments = {
    "QBOXCONF_PROVIDER_BINDIR": bindir,
    "QBOXCONF_PROVIDER_LIBDIR": libdir,
    "QBOXCONF_PROVIDER_MODULE_DIR": module_dir,
    "QBOXCONF_PROVIDER_DATA_DIR": data_dir,
    "QBOXCONF_RECIPE_SYSROOT_NATIVE": recipe_sysroot_native,
    "QBOXCONF_EXE": str(Path(bindir) / exe),
    "QBOXCONF_CONFIG": str(Path(data_dir) / config),
    "QBOXCONF_DEBUG_SYMBOLS": debug_symbols,
    "QBOXCONF_LD_LIBRARY_PATH": ":".join(ld_entries),
    "QBOXCONF_IMAGE_ROOTFS_WIC": image_path(images, qboxconf_dir, "rootfs_wic", "wic"),
    "QBOXCONF_IMAGE_EFI_CAPSULE_DISK": image_path(images, qboxconf_dir, "efi_capsule_disk"),
    "QBOXCONF_IMAGE_RSE_ROM": image_path(images, qboxconf_dir, "rse_rom"),
    "QBOXCONF_IMAGE_RSE_FLASH": image_path(images, qboxconf_dir, "rse_flash"),
    "QBOXCONF_IMAGE_RSE_OTP": image_path(images, qboxconf_dir, "rse_otp"),
    "QBOXCONF_IMAGE_AP_FLASH": image_path(images, qboxconf_dir, "ap_flash"),
    "QBOXCONF_IMAGE_AP_BL2_ELF": image_path(images, qboxconf_dir, "ap_bl2_elf"),
    "QBOXCONF_IMAGE_RSE_BL1_2_ELF": image_path(images, qboxconf_dir, "rse_bl1_2_elf"),
    "QBOXCONF_IMAGE_RSE_BL2_ELF": image_path(images, qboxconf_dir, "rse_bl2_elf"),
    "QBOXCONF_IMAGE_PROVISIONING_BUNDLE": image_path(images, qboxconf_dir, "provisioning_bundle"),
    "QBOXCONF_IMAGE_AP_DTB": image_path(images, qboxconf_dir, "ap_dtb", "dtb"),
    "QBOXCONF_IMAGE_SI_CL0": image_path(images, qboxconf_dir, "si_cl0_image", "si0_ramfw"),
    "QBOXCONF_IMAGE_SI_CL1": image_path(images, qboxconf_dir, "si_cl1_image", "si_cl1"),
    "QBOXCONF_IMAGE_SI_CL1_SYMBOLS": image_path(images, qboxconf_dir, "si_cl1_symbols"),
}
for name, value in assignments.items():
    print(quote_assignment(name, value))
PY
}

copy_sparse() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "${dst}")"
    cp --reflink=auto --sparse=always "${src}" "${dst}"
}

default_ssh_port_range() {
    local start="${SSH_PORT_START:-8022}"
    local end="${SSH_PORT_END:-8122}"
    local port
    for ((port = start; port <= end; port++)); do
        if ! ss -ltn "( sport = :${port} )" | grep -q ":${port}"; then
            printf '%s\n' "${port}"
            return 0
        fi
    done
    die "no free SSH host port in range ${start}-${end}"
}

reject_removed_env() {
    local removed=(
        QBOX_ENABLE_TESTDEV
        QBOX_GIC_USE_QEMU
        QBOX_RSE_TIMER_MODEL
        QBOX_SOC_UART_MODEL
        QBOX_CC3XX_FAST_RANDOM
    )
    local name
    for name in "${removed[@]}"; do
        if [[ -n "${!name-}" ]]; then
            die "${name} is no longer supported; use the default production-capable QBox models"
        fi
    done
}

default_ap_cpu_count() {
    local local_conf="${YOCTO_BUILD_DIR}/conf/local.conf"
    [[ -f "${local_conf}" ]] || return 1

    sed -nE \
        's/^[[:space:]]*PC_CPUS?_COUNT_DEFAULT[[:space:]]*[?+:.]*=[[:space:]]*"([^"]+)".*/\1/p' \
        "${local_conf}" | tail -n 1
}

validate_ap_cpu_count() {
    local value="$1"

    [[ "${value}" =~ ^[0-9]+$ ]] ||
        die "QBOX_APOLLO_NUM_CPUS must be numeric: ${value}"
    ((value >= 1 && value <= 16)) ||
        die "QBOX_APOLLO_NUM_CPUS must be in range 1..16: ${value}"
}

debug_port_in_use() {
    local port="$1"

    ss -H -ltn 2>/dev/null |
        awk '{print $4}' |
        grep -Eq "(^|[:.])${port}$|\\]:${port}$"
}

resolve_yocto_debug_elf() {
    local work_root
    work_root="$(dirname "${YOCTO_WORK_DIR}")"

    case "${DEBUG_TARGET}" in
        qbox)
            if [[ "${MACHINE}" == "apollo-qvp" ]]; then
                resolve_file_with_glob \
                    "Yocto QBox host debug ELF" \
                    "" \
                    "$(dirname "${QBOXCONF_RECIPE_SYSROOT_NATIVE}")/build/platforms-vp"
            else
                resolve_file \
                    "QBox host debug ELF" \
                    "${QBOX_BUILD_DIR}/platforms-vp"
            fi
            ;;
        rse)
            resolve_file_with_glob \
                "Yocto RSE TF-M BL1_1 debug ELF" \
                "" \
                "${YOCTO_WORK_DIR}/trusted-firmware-m/*/build/bin/bl1_1.elf"
            ;;
        si_cl0)
            resolve_file_with_glob \
                "Yocto SI CL0 SCP debug ELF" \
                "" \
                "${YOCTO_WORK_DIR}/scp-firmware/*/build/ramfw/si0/bin/*-si0-bl2.elf"
            ;;
        si_cl1)
            resolve_file_with_glob \
                "Yocto SI CL1 Zephyr debug ELF" \
                "" \
                "${work_root}/${WORK_PREFIX}_safety_island_c1-zephyr/zephyr-demos-cl1/*/build/zephyr/zephyr.elf"
            ;;
        tf-a)
            resolve_file_with_glob \
                "Yocto TF-A BL2 debug ELF" \
                "" \
                "${YOCTO_WORK_DIR}/trusted-firmware-a/*/build/${WORK_PREFIX}/debug/bl2/bl2.elf"
            ;;
        u-boot)
            resolve_file_with_glob \
                "Yocto U-Boot debug ELF" \
                "" \
                "${YOCTO_WORK_DIR}/u-boot/*/build/u-boot"
            ;;
        linux)
            resolve_file_with_two_globs \
                "Yocto Linux debug ELF" \
                "" \
                "${YOCTO_WORK_DIR}/linux-*/*/image/boot/vmlinux-*" \
                "" \
                "${YOCTO_WORK_DIR}/linux-*/*/build/vmlinux"
            ;;
    esac
}

validate_qbox_debug_build_id() {
    local runtime_elf="$1"
    local debug_elf="$2"

    python3 - "${runtime_elf}" "${debug_elf}" <<'PY'
import re
import subprocess
import sys
from pathlib import Path


def build_id(path: Path) -> str:
    result = subprocess.run(
        ["readelf", "-n", str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    match = re.search(r"Build ID:\s*([0-9a-fA-F]+)", result.stdout)
    if match is None:
        raise SystemExit(f"error: ELF has no build ID: {path}")
    return match.group(1).lower()


runtime = Path(sys.argv[1])
debug = Path(sys.argv[2])
if build_id(runtime) != build_id(debug):
    raise SystemExit(
        "error: Yocto QBox runtime/debug ELF build IDs differ: "
        f"{runtime} != {debug}"
    )
PY
}

RUN_STAMP="$(date +%Y%m%d-%H%M%S)"
MACHINE="${MACHINE:-apollo-qvp}"
YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-}"
DEPLOY_DIR="${DEPLOY_DIR:-}"
YOCTO_WORK_DIR="${YOCTO_WORK_DIR:-}"
IMAGE_BASENAME_FROM_ENV="${IMAGE_BASENAME:-}"
IMAGE_BASENAME="${IMAGE_BASENAME_FROM_ENV:-nexios-image}"
QBOX_CONF_FILE="${QBOX_CONF_FILE:-}"

LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-}"
QBOX_CORE_DIR="${QBOX_CORE_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox}"
QBOX_PLATFORM_DIR="${QBOX_PLATFORM_DIR:-${ROOT_DIR}/hsoc-stack/tools/qbox-platform}"
QBOX_TOOL_DIR="${QBOX_TOOL_DIR:-}"
QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-${QBOX_PLATFORM_BUILD_DIR:-}}"
QBOX_CONF="${QBOX_CONF:-}"
export QBOX_CORE_DIR QBOX_PLATFORM_DIR

LOCAL_BUILD_DIR_EXPLICIT=0
QBOX_TOOL_DIR_EXPLICIT=0
QBOX_BUILD_DIR_EXPLICIT=0
QBOX_CONF_EXPLICIT=0
IMAGE_BASENAME_EXPLICIT=0
RSE_SYMBOLS_EXPLICIT=0
[[ -n "${LOCAL_BUILD_DIR}" ]] && LOCAL_BUILD_DIR_EXPLICIT=1
[[ -n "${QBOX_TOOL_DIR}" ]] && QBOX_TOOL_DIR_EXPLICIT=1
[[ -n "${QBOX_BUILD_DIR}" ]] && QBOX_BUILD_DIR_EXPLICIT=1
[[ -n "${QBOX_CONF}" ]] && QBOX_CONF_EXPLICIT=1
[[ -n "${IMAGE_BASENAME_FROM_ENV}" ]] && IMAGE_BASENAME_EXPLICIT=1
[[ -n "${RSE_SYMBOLS:-}" ]] && RSE_SYMBOLS_EXPLICIT=1

TMUX_SESSION="${TMUX_SESSION:-apollo-qbox-yocto-${RUN_STAMP}}"
OUT_DIR="${OUT_DIR:-}"
TIMEOUT="${TIMEOUT:-0}"
JOBS="${JOBS:-$(nproc)}"
ROOTFS_BOOTARGS_PROFILE="${ROOTFS_BOOTARGS_PROFILE:-none}"
PRIMARY_LOGIN_PROMPT="${PRIMARY_LOGIN_PROMPT:-}"
PRIMARY_SHELL_MARKER="${PRIMARY_SHELL_MARKER:-}"
PRIMARY_SHELL_PROMPT_RE="${PRIMARY_SHELL_PROMPT_RE:-}"
RUN_QBOX_COPY_DISKS="${RUN_QBOX_COPY_DISKS:-0}"
RUN_QBOX_RECORD_INITIAL_STATE="${RUN_QBOX_RECORD_INITIAL_STATE:-0}"
LEGACY_FILE_BACKED_SRAM="${LEGACY_FILE_BACKED_SRAM:-0}"
HEADLESS="${HEADLESS:-0}"
KEEP_RUNNING_AFTER_PASS="${KEEP_RUNNING_AFTER_PASS:-1}"
UBOOT_ONLY="${UBOOT_ONLY:-0}"
NO_ATTACH="${NO_ATTACH:-0}"
DRY_RUN="${DRY_RUN:-0}"
MULTI_SESSION="${MULTI_SESSION:-0}"
RSE_OTP_IMAGE_SIZE="${RSE_OTP_IMAGE_SIZE:-65536}"
RSE_STATE_DIR="${QBOX_RSE_STATE_DIR:-}"
PERSIST_RSE_STATE="${QBOX_PERSIST_RSE_STATE:-1}"
RESET_RSE_STATE=0
BSP_MODE=0
DEBUG_TARGET=""
DEBUG_COMPONENT=""
DEBUG_ENTRYPOINT=""
DEBUG_ENTRY_ADDRESS=""
DEBUG_ENDPOINT=""
DEBUG_MANIFEST=""
DEBUG_GDB_SCRIPT=""
DEBUG_ARTIFACT_ELF=""
DEBUG_WAIT_LOG=""
DEBUG_WAIT_MARKER=""
DEBUG_CPU_PARAM=""
DEBUG_GDB_THREAD=""
DEBUG_MPIDR=""
DEBUG_TOPOLOGY_OPTION=""
DEBUG_PLATFORM_PARAMS=()
DEBUG_MODE="${DEBUG_MODE:-interactive}"
DEBUG_MODE_SET=0
DEBUG_TIMEOUT="${DEBUG_TIMEOUT:-600}"
DEBUG_RESULT="${DEBUG_RESULT:-}"

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

while (($#)); do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --machine)
            [[ $# -ge 2 ]] || die "--machine requires a value"
            MACHINE="$2"
            shift 2
            ;;
        --bsp)
            BSP_MODE=1
            shift
            ;;
        --build-dir)
            [[ $# -ge 2 ]] || die "--build-dir requires a value"
            YOCTO_BUILD_DIR="$2"
            shift 2
            ;;
        --deploy-dir)
            [[ $# -ge 2 ]] || die "--deploy-dir requires a value"
            DEPLOY_DIR="$2"
            shift 2
            ;;
        --work-dir)
            [[ $# -ge 2 ]] || die "--work-dir requires a value"
            YOCTO_WORK_DIR="$2"
            shift 2
            ;;
        --image-basename)
            [[ $# -ge 2 ]] || die "--image-basename requires a value"
            IMAGE_BASENAME="$2"
            IMAGE_BASENAME_EXPLICIT=1
            shift 2
            ;;
        --qboxconf)
            [[ $# -ge 2 ]] || die "--qboxconf requires a value"
            QBOX_CONF_FILE="$2"
            shift 2
            ;;
        --local-build-dir)
            [[ $# -ge 2 ]] || die "--local-build-dir requires a value"
            LOCAL_BUILD_DIR="$2"
            LOCAL_BUILD_DIR_EXPLICIT=1
            shift 2
            ;;
        --qbox-tool-dir)
            [[ $# -ge 2 ]] || die "--qbox-tool-dir requires a value"
            QBOX_TOOL_DIR="$2"
            QBOX_TOOL_DIR_EXPLICIT=1
            shift 2
            ;;
        --qbox-build-dir)
            [[ $# -ge 2 ]] || die "--qbox-build-dir requires a value"
            QBOX_BUILD_DIR="$2"
            QBOX_BUILD_DIR_EXPLICIT=1
            shift 2
            ;;
        --conf)
            [[ $# -ge 2 ]] || die "--conf requires a value"
            QBOX_CONF="$2"
            QBOX_CONF_EXPLICIT=1
            shift 2
            ;;
        --session)
            [[ $# -ge 2 ]] || die "--session requires a value"
            TMUX_SESSION="$2"
            shift 2
            ;;
        --out-dir)
            [[ $# -ge 2 ]] || die "--out-dir requires a value"
            OUT_DIR="$2"
            shift 2
            ;;
        --timeout)
            [[ $# -ge 2 ]] || die "--timeout requires a value"
            TIMEOUT="$2"
            shift 2
            ;;
        --jobs)
            [[ $# -ge 2 ]] || die "--jobs requires a value"
            JOBS="$2"
            shift 2
            ;;
        --rootfs-bootargs-profile)
            [[ $# -ge 2 ]] || die "--rootfs-bootargs-profile requires a value"
            ROOTFS_BOOTARGS_PROFILE="$2"
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
        --record-initial-state)
            RUN_QBOX_RECORD_INITIAL_STATE=1
            shift
            ;;
        --no-record-initial-state)
            RUN_QBOX_RECORD_INITIAL_STATE=0
            shift
            ;;
        --legacy-file-backed-sram)
            LEGACY_FILE_BACKED_SRAM=1
            shift
            ;;
        --rse-state-dir)
            [[ $# -ge 2 ]] || die "--rse-state-dir requires a value"
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
        --headless)
            HEADLESS=1
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
            if [[ $# -lt 2 || "$2" == --* ]]; then
                qbox_debug_usage
                exit 0
            fi
            DEBUG_TARGET="$2"
            shift 2
            ;;
        --debug-mode)
            [[ $# -ge 2 ]] || die "--debug-mode requires a value"
            DEBUG_MODE="$2"
            DEBUG_MODE_SET=1
            shift 2
            ;;
        --debug-timeout)
            [[ $# -ge 2 ]] || die "--debug-timeout requires a value"
            DEBUG_TIMEOUT="$2"
            shift 2
            ;;
        --debug-result)
            [[ $# -ge 2 ]] || die "--debug-result requires a value"
            DEBUG_RESULT="$2"
            shift 2
            ;;
        --no-attach)
            NO_ATTACH=1
            shift
            ;;
        --multi-session)
            MULTI_SESSION=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --rootfs)
            [[ $# -ge 2 ]] || die "--rootfs requires a value"
            ROOTFS_OVERRIDE="$2"
            shift 2
            ;;
        --efi-capsule-disk)
            [[ $# -ge 2 ]] || die "--efi-capsule-disk requires a value"
            EFI_CAPSULE_DISK_OVERRIDE="$2"
            shift 2
            ;;
        --rse-rom)
            [[ $# -ge 2 ]] || die "--rse-rom requires a value"
            RSE_ROM_OVERRIDE="$2"
            shift 2
            ;;
        --rse-flash)
            [[ $# -ge 2 ]] || die "--rse-flash requires a value"
            RSE_FLASH_OVERRIDE="$2"
            shift 2
            ;;
        --rse-otp)
            [[ $# -ge 2 ]] || die "--rse-otp requires a value"
            RSE_OTP_OVERRIDE="$2"
            shift 2
            ;;
        --ap-flash)
            [[ $# -ge 2 ]] || die "--ap-flash requires a value"
            AP_FLASH_OVERRIDE="$2"
            shift 2
            ;;
        --ap-bl2-elf)
            [[ $# -ge 2 ]] || die "--ap-bl2-elf requires a value"
            AP_BL2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --rse-bl1-2-elf)
            [[ $# -ge 2 ]] || die "--rse-bl1-2-elf requires a value"
            RSE_BL1_2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --rse-bl2-elf)
            [[ $# -ge 2 ]] || die "--rse-bl2-elf requires a value"
            RSE_BL2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --provisioning-bundle)
            [[ $# -ge 2 ]] || die "--provisioning-bundle requires a value"
            PROVISIONING_BUNDLE_OVERRIDE="$2"
            shift 2
            ;;
        --ap-dtb)
            [[ $# -ge 2 ]] || die "--ap-dtb requires a value"
            AP_DTB_OVERRIDE="$2"
            shift 2
            ;;
        --rse-symbols)
            [[ $# -ge 2 ]] || die "--rse-symbols requires a value"
            RSE_SYMBOLS_OVERRIDE="$2"
            RSE_SYMBOLS_EXPLICIT=1
            shift 2
            ;;
        --si-cl0-image)
            [[ $# -ge 2 ]] || die "--si-cl0-image requires a value"
            SI_CL0_IMAGE_OVERRIDE="$2"
            shift 2
            ;;
        --si-cl1-image)
            [[ $# -ge 2 ]] || die "--si-cl1-image requires a value"
            SI_CL1_IMAGE_OVERRIDE="$2"
            shift 2
            ;;
        --si-cl1-symbols)
            [[ $# -ge 2 ]] || die "--si-cl1-symbols requires a value"
            SI_CL1_SYMBOLS_OVERRIDE="$2"
            shift 2
            ;;
        --enable-test-device|--use-qemu-gic|--rse-qemu-timer|--soc-uart-qemu|--cc3xx-fast-random|--mock-cc3xx)
            die "$1 is no longer supported; use the default production-capable QBox models"
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

reject_removed_env

if [[ "${DRY_RUN}" == "0" && "${MULTI_SESSION}" == "0" ]]; then
    "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full_tmux.sh" \
        --stop-existing-sessions
fi

if [[ -n "${DEBUG_TARGET}" ]]; then
    qbox_debug_configure_target
    if [[ -n "${DEBUG_TOPOLOGY_OPTION}" ]]; then
        TMUX_RUNNER_ARGS+=("${DEBUG_TOPOLOGY_OPTION}")
    fi
    case "${DEBUG_MODE}" in
        interactive|probe|server) ;;
        *) die "invalid --debug-mode: ${DEBUG_MODE}" ;;
    esac
    [[ "${DEBUG_TIMEOUT}" =~ ^[0-9]+([.][0-9]+)?$ ]] &&
        [[ "${DEBUG_TIMEOUT}" != "0" && "${DEBUG_TIMEOUT}" != "0.0" ]] ||
        die "invalid --debug-timeout: ${DEBUG_TIMEOUT}"
    if [[ "${DEBUG_MODE}" == "interactive" ]]; then
        [[ "${HEADLESS}" == "0" ]] ||
            die "--debug requires the interactive tmux layout; remove --headless"
    else
        HEADLESS=1
    fi
elif [[ "${DEBUG_MODE_SET}" == "1" ]]; then
    die "--debug-mode requires --debug TARGET"
fi

BOOT_PROFILE="product"
if [[ "${BSP_MODE}" == "1" ]]; then
    if [[ "${IMAGE_BASENAME_EXPLICIT}" == "1" &&
        "${IMAGE_BASENAME}" != "nexios-bsp-initramfs" ]]; then
        die "--bsp conflicts with image basename '${IMAGE_BASENAME}'"
    fi
    BOOT_PROFILE="bsp-initramfs"
    IMAGE_BASENAME="nexios-bsp-initramfs"
fi

source "${ROOT_DIR}/scripts/run/qbox_qboxconf_common.sh"

if [[ -z "${YOCTO_BUILD_DIR}" ]]; then
    YOCTO_BUILD_DIR="${ROOT_DIR}/build"
fi
WORK_PREFIX="$(machine_to_work_prefix "${MACHINE}")"
DEPLOY_DIR="${DEPLOY_DIR:-${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/images/${MACHINE}}"
YOCTO_WORK_DIR="${YOCTO_WORK_DIR:-${YOCTO_BUILD_DIR}/tmp_baremetal/work/${WORK_PREFIX}-poky-linux}"
if [[ "${MACHINE}" == "apollo-qvp" ]]; then
    QBOX_CONF_FILE="${QBOX_CONF_FILE:-$(resolve_qboxconf_default)}"
    qboxconf_assignments="$(read_qboxconf_shell_assignments "${QBOX_CONF_FILE}")" ||
        die "failed to read qboxconf: ${QBOX_CONF_FILE}"
    eval "${qboxconf_assignments}"
    if [[ "${QBOX_TOOL_DIR_EXPLICIT}" == "0" ]]; then
        QBOX_TOOL_DIR="${QBOXCONF_PROVIDER_BINDIR}"
    fi
    if [[ "${LOCAL_BUILD_DIR_EXPLICIT}" == "0" ]]; then
        LOCAL_BUILD_DIR="${QBOXCONF_RECIPE_SYSROOT_NATIVE}"
    fi
    if [[ "${QBOX_BUILD_DIR_EXPLICIT}" == "0" ]]; then
        QBOX_BUILD_DIR="${QBOXCONF_PROVIDER_BINDIR}"
    fi
    if [[ "${QBOX_CONF_EXPLICIT}" == "0" ]]; then
        QBOX_CONF="${QBOXCONF_CONFIG}"
    fi
    if [[ "${RSE_SYMBOLS_EXPLICIT}" == "0" && -n "${QBOXCONF_DEBUG_SYMBOLS}" ]]; then
        RSE_SYMBOLS_OVERRIDE="${QBOXCONF_DEBUG_SYMBOLS}"
    fi
    export LD_LIBRARY_PATH="${QBOXCONF_LD_LIBRARY_PATH}"
    OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-apollo-qvp/yocto-${MACHINE}-${RUN_STAMP}}"
else
    LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-apollo-fvp}"
    QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-${LOCAL_BUILD_DIR}/work/qbox-platform}"
    QBOX_CONF="${QBOX_CONF:-${QBOX_PLATFORM_DIR}/platforms/apollo/apollo-qvp.lua}"
    OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/yocto-${MACHINE}-${RUN_STAMP}}"
    QBOX_TOOL_DIR="${QBOX_TOOL_DIR:-${QBOX_BUILD_DIR}}"
fi
export QBOX_TOOL_DIR

[[ -d "${DEPLOY_DIR}" ]] || die "Yocto deploy directory not found: ${DEPLOY_DIR}"
[[ -d "${YOCTO_WORK_DIR}" ]] || die "Yocto work directory not found: ${YOCTO_WORK_DIR}"
[[ -d "${LOCAL_BUILD_DIR}" ]] || die "local build directory not found: ${LOCAL_BUILD_DIR}. Build QBox first with ./local_build.sh qbox or set --local-build-dir."
[[ -f "${QBOX_CONF}" ]] || die "QBox config not found: ${QBOX_CONF}"
[[ -d "${QBOX_BUILD_DIR}" ]] || die "QBox build directory not found: ${QBOX_BUILD_DIR}. Build QBox first with ./local_build.sh qbox or set --qbox-build-dir."
if [[ "${MACHINE}" == "apollo-qvp" ]]; then
    [[ -x "${QBOXCONF_EXE}" ]] || die "QBox executable not found or not executable: ${QBOXCONF_EXE}"
fi

if [[ -z "${QBOX_APOLLO_NUM_CPUS:-}" ]]; then
    QBOX_APOLLO_NUM_CPUS="${QBOXCONF_APOLLO_NUM_CPUS:-}"
fi
if [[ -z "${QBOX_APOLLO_NUM_CPUS}" ]]; then
    QBOX_APOLLO_NUM_CPUS="$(default_ap_cpu_count || true)"
fi
if [[ -z "${QBOX_APOLLO_NUM_CPUS}" ]]; then
    QBOX_APOLLO_NUM_CPUS=4
fi
validate_ap_cpu_count "${QBOX_APOLLO_NUM_CPUS}"
export QBOX_APOLLO_NUM_CPUS

if [[ "${BSP_MODE}" == "1" ]]; then
    PRIMARY_LOGIN_PROMPT="${PRIMARY_LOGIN_PROMPT:-NEXIOS_BSP_INITRAMFS_READY}"
    PRIMARY_SHELL_MARKER="${PRIMARY_SHELL_MARKER:-nexios-bsp#}"
    PRIMARY_SHELL_PROMPT_RE="${PRIMARY_SHELL_PROMPT_RE:-(?:^|\\n)nexios-bsp#\\s*$}"
else
    PRIMARY_LOGIN_PROMPT="${PRIMARY_LOGIN_PROMPT:-${MACHINE} login:}"
    PRIMARY_SHELL_MARKER="${PRIMARY_SHELL_MARKER:-~ #}"
    PRIMARY_SHELL_PROMPT_RE="${PRIMARY_SHELL_PROMPT_RE:-(?:root@${MACHINE}[^\\n]*[#>]|\\S+ #)\\s*$}"
fi
RSE_STATE_DIR="${RSE_STATE_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/state/yocto-${MACHINE}}"
if [[ "${RESET_RSE_STATE}" == "1" && "${PERSIST_RSE_STATE}" != "1" ]]; then
    die "--reset-rse-state cannot be used with --no-persistent-rse-state"
fi

ROOTFS_DEFAULT="${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}.wic"
ROOTFS_GLOB="${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.wic"
ROOTFS_QBOXCONF_DEFAULT=""
ROOTFS_QBOXCONF_GLOB=""
if [[ "${MACHINE}" == "apollo-qvp" && -n "${QBOXCONF_IMAGE_ROOTFS_WIC:-}" ]]; then
    ROOTFS_QBOXCONF_DEFAULT="${QBOXCONF_IMAGE_ROOTFS_WIC}"
    ROOTFS_QBOXCONF_GLOB="${QBOXCONF_IMAGE_ROOTFS_WIC%.wic}-*.wic"
fi
if [[ -n "${ROOTFS_OVERRIDE}" ]]; then
    ROOTFS="$(resolve_file "Yocto rootfs WIC image" "${ROOTFS_OVERRIDE}")"
else
    ROOTFS="$(resolve_file_with_two_globs \
        "Yocto rootfs WIC image" \
        "${ROOTFS_QBOXCONF_DEFAULT}" \
        "${ROOTFS_QBOXCONF_GLOB}" \
        "${ROOTFS_DEFAULT}" \
        "${ROOTFS_GLOB}")"
fi
if [[ "${MACHINE}" == "apollo-qvp" ]]; then
    if [[ -n "${EFI_CAPSULE_DISK_OVERRIDE}" ]]; then
        EFI_CAPSULE_DISK="$(resolve_file "EFI capsule update disk" "${EFI_CAPSULE_DISK_OVERRIDE}")"
    else
        EFI_CAPSULE_DISK="$(resolve_file \
            "EFI capsule update disk" \
            "${QBOXCONF_IMAGE_EFI_CAPSULE_DISK:-}" \
            "${DEPLOY_DIR}/efi-capsule-update-disk-image-${MACHINE}.img")"
    fi
else
    EFI_CAPSULE_DISK="$(resolve_file \
        "EFI capsule update disk" \
        "${EFI_CAPSULE_DISK_OVERRIDE:-${DEPLOY_DIR}/efi-capsule-update-disk-image-${MACHINE}.img}" \
        "${DEPLOY_DIR}/efi-capsule-update-disk-image-fvp-rd-aspen.img")"
fi
if [[ -n "${RSE_ROM_OVERRIDE}" ]]; then
    RSE_ROM="$(resolve_file "RSE ROM image" "${RSE_ROM_OVERRIDE}")"
else
    RSE_ROM="$(resolve_file "RSE ROM image" "${QBOXCONF_IMAGE_RSE_ROM:-}" "${DEPLOY_DIR}/rse-rom-image.img")"
fi
if [[ -n "${RSE_FLASH_OVERRIDE}" ]]; then
    RSE_FLASH="$(resolve_file "RSE flash image" "${RSE_FLASH_OVERRIDE}")"
else
    RSE_FLASH="$(resolve_file "RSE flash image" "${QBOXCONF_IMAGE_RSE_FLASH:-}" "${DEPLOY_DIR}/rse-flash-image.img")"
fi
if [[ -n "${RSE_OTP_OVERRIDE}" ]]; then
    RSE_OTP="$(resolve_file "RSE OTP image" "${RSE_OTP_OVERRIDE}")"
else
    RSE_OTP="$(resolve_file "RSE OTP image" "${QBOXCONF_IMAGE_RSE_OTP:-}" "${DEPLOY_DIR}/rse-otp-image.img")"
fi
if [[ -n "${AP_FLASH_OVERRIDE}" ]]; then
    AP_FLASH="$(resolve_file "AP flash image" "${AP_FLASH_OVERRIDE}")"
else
    AP_FLASH="$(resolve_file "AP flash image" "${QBOXCONF_IMAGE_AP_FLASH:-}" "${DEPLOY_DIR}/ap-flash-image.img")"
fi
AP_BL2_DEFAULT="${DEPLOY_DIR}/bl2.elf"
AP_BL2_GLOB="${YOCTO_WORK_DIR}/trusted-firmware-a/*/build/${WORK_PREFIX}/debug/bl2/bl2.elf"
if [[ "${MACHINE}" == "apollo-qvp" && -n "${QBOXCONF_IMAGE_AP_BL2_ELF:-}" ]]; then
    AP_BL2_DEFAULT="${QBOXCONF_IMAGE_AP_BL2_ELF}"
    AP_BL2_GLOB=""
fi
if [[ -n "${AP_BL2_ELF_OVERRIDE}" ]]; then
    AP_BL2_ELF="$(resolve_file "AP TF-A BL2 ELF" "${AP_BL2_ELF_OVERRIDE}")"
else
    AP_BL2_ELF="$(resolve_file_with_glob \
        "AP TF-A BL2 ELF" \
        "${AP_BL2_DEFAULT}" \
        "${AP_BL2_GLOB}")"
fi
RSE_BL1_2_DEFAULT="${RSE_BL1_2_ELF_OVERRIDE}"
RSE_BL1_2_GLOB="${YOCTO_WORK_DIR}/trusted-firmware-m/*/build/bin/bl1_2.elf"
if [[ "${MACHINE}" == "apollo-qvp" && -n "${QBOXCONF_IMAGE_RSE_BL1_2_ELF:-}" ]]; then
    RSE_BL1_2_DEFAULT="${QBOXCONF_IMAGE_RSE_BL1_2_ELF}"
    RSE_BL1_2_GLOB=""
fi
if [[ -n "${RSE_BL1_2_ELF_OVERRIDE}" ]]; then
    RSE_BL1_2_ELF="$(resolve_file "RSE TF-M BL1_2 ELF" "${RSE_BL1_2_ELF_OVERRIDE}")"
else
    RSE_BL1_2_ELF="$(resolve_file_with_glob \
        "RSE TF-M BL1_2 ELF" \
        "${RSE_BL1_2_DEFAULT}" \
        "${RSE_BL1_2_GLOB}")"
fi
RSE_BL2_DEFAULT="${RSE_BL2_ELF_OVERRIDE}"
RSE_BL2_GLOB="${YOCTO_WORK_DIR}/trusted-firmware-m/*/build/bin/bl2.elf"
if [[ "${MACHINE}" == "apollo-qvp" && -n "${QBOXCONF_IMAGE_RSE_BL2_ELF:-}" ]]; then
    RSE_BL2_DEFAULT="${QBOXCONF_IMAGE_RSE_BL2_ELF}"
    RSE_BL2_GLOB=""
fi
if [[ -n "${RSE_BL2_ELF_OVERRIDE}" ]]; then
    RSE_BL2_ELF="$(resolve_file "RSE TF-M BL2 ELF" "${RSE_BL2_ELF_OVERRIDE}")"
else
    RSE_BL2_ELF="$(resolve_file_with_glob \
        "RSE TF-M BL2 ELF" \
        "${RSE_BL2_DEFAULT}" \
        "${RSE_BL2_GLOB}")"
fi
if [[ -n "${PROVISIONING_BUNDLE_OVERRIDE}" ]]; then
    PROVISIONING_BUNDLE="$(resolve_file "combined provisioning bundle" "${PROVISIONING_BUNDLE_OVERRIDE}")"
else
    PROVISIONING_BUNDLE="$(resolve_file "combined provisioning bundle" "${QBOXCONF_IMAGE_PROVISIONING_BUNDLE:-}" "${DEPLOY_DIR}/combined_provisioning_message.bin")"
fi
if [[ -n "${AP_DTB_OVERRIDE}" ]]; then
    AP_DTB="$(resolve_file "AP device tree" "${AP_DTB_OVERRIDE}")"
else
    AP_DTB="$(resolve_file "AP device tree" "${QBOXCONF_IMAGE_AP_DTB:-}" "${DEPLOY_DIR}/${MACHINE}.dtb")"
fi
RSE_SYMBOLS=""
if [[ -n "${RSE_SYMBOLS_OVERRIDE:-}" ]]; then
    RSE_SYMBOLS="$(resolve_file \
        "QBox RSE debug symbol manifest" \
        "${RSE_SYMBOLS_OVERRIDE}")"
elif [[ "${MACHINE}" != "apollo-qvp" ]]; then
    RSE_SYMBOLS="$(resolve_file \
        "QBox RSE debug symbol manifest" \
        "${LOCAL_BUILD_DIR}/debug/symbols.json")"
elif [[ -f "${LOCAL_BUILD_DIR}/debug/symbols.json" ]]; then
    RSE_SYMBOLS="${LOCAL_BUILD_DIR}/debug/symbols.json"
fi
if [[ -n "${SI_CL0_IMAGE_OVERRIDE}" ]]; then
    SI_CL0_IMAGE="$(resolve_file "Safety Island CL0 SCP image" "${SI_CL0_IMAGE_OVERRIDE}")"
else
    SI_CL0_IMAGE="$(resolve_file "Safety Island CL0 SCP image" "${QBOXCONF_IMAGE_SI_CL0:-}" "${DEPLOY_DIR}/si0_ramfw.bin")"
fi
if [[ -n "${SI_CL1_IMAGE_OVERRIDE}" ]]; then
    SI_CL1_IMAGE="$(resolve_file "Safety Island CL1 Zephyr image" "${SI_CL1_IMAGE_OVERRIDE}")"
else
    SI_CL1_IMAGE="$(resolve_file "Safety Island CL1 Zephyr image" "${QBOXCONF_IMAGE_SI_CL1:-}" "${DEPLOY_DIR}/zephyr-demos-cl1.bin")"
fi
if [[ -n "${SI_CL1_SYMBOLS_OVERRIDE}" ]]; then
    SI_CL1_SYMBOLS="$(resolve_file "Safety Island CL1 Zephyr symbols" "${SI_CL1_SYMBOLS_OVERRIDE}")"
else
    SI_CL1_SYMBOLS="$(resolve_file "Safety Island CL1 Zephyr symbols" "${QBOXCONF_IMAGE_SI_CL1_SYMBOLS:-}" "${DEPLOY_DIR}/zephyr-demos-cl1.elf")"
fi

if [[ -n "${DEBUG_TARGET}" ]]; then
    DEBUG_MANIFEST="${OUT_DIR}/debug/symbols.json"
    DEBUG_GDB_SCRIPT="${OUT_DIR}/debug/gdb/${DEBUG_COMPONENT}.gdb"
    if [[ "${DRY_RUN}" != "1" ]]; then
        command -v python3 >/dev/null 2>&1 ||
            die "python3 is required for --debug"
        command -v gdb-multiarch >/dev/null 2>&1 ||
            die "gdb-multiarch is required for --debug"
        if [[ "${DEBUG_TARGET}" == "qbox" ]]; then
            command -v gdb >/dev/null 2>&1 ||
                die "gdb is required for --debug qbox"
            command -v gdbserver >/dev/null 2>&1 ||
                die "gdbserver is required for --debug qbox"
        fi

        DEBUG_ARTIFACT_ELF="$(resolve_yocto_debug_elf)"
        debug_setup=(
            python3
            "${ROOT_DIR}/scripts/setup/setup_local_debug_env.py"
            --local-build-dir "${YOCTO_BUILD_DIR}"
            --out-dir "${OUT_DIR}/debug"
            --component "${DEBUG_COMPONENT}"
            --elf "${DEBUG_COMPONENT}=${DEBUG_ARTIFACT_ELF}"
        )
        if [[ -d "${QBOXCONF_PROVIDER_LIBDIR:-}" ]]; then
            debug_setup+=(--solib-dir "${QBOXCONF_PROVIDER_LIBDIR}")
        fi
        "${debug_setup[@]}"

        DEBUG_ENTRY_ADDRESS="$(
            qbox_debug_validate_manifest \
                "${DEBUG_MANIFEST}" \
                "${DEBUG_COMPONENT}" \
                "${DEBUG_ENTRYPOINT}"
        )"
        if [[ "${DEBUG_TARGET}" == "qbox" ]]; then
            validate_qbox_debug_build_id \
                "${QBOXCONF_EXE}" "${DEBUG_ARTIFACT_ELF}"
        fi
        if [[ -n "${DEBUG_CPU_PARAM}" ]]; then
            DEBUG_PLATFORM_PARAMS+=(
                "${DEBUG_CPU_PARAM}.gdb_breakpoint=${DEBUG_ENTRY_ADDRESS}"
            )
        fi
        debug_port="${DEBUG_ENDPOINT##*:}"
        debug_port_in_use "${debug_port}" &&
            die "GDB port is already in use: ${debug_port}"
    else
        DEBUG_ENTRY_ADDRESS="<resolved-from-manifest>"
    fi
    if [[ -n "${DEBUG_CPU_PARAM}" ]]; then
        DEBUG_PLATFORM_PARAMS+=("${DEBUG_CPU_PARAM}.gdb_pause_all=true")
    fi
fi

RUN_ROOTFS="${ROOTFS}"
RUN_EFI_CAPSULE_DISK="${EFI_CAPSULE_DISK}"
RUN_RSE_OTP="${RSE_OTP}"
if [[ "${DRY_RUN}" == "0" && "${RUN_QBOX_RECORD_INITIAL_STATE}" == "1" ]]; then
    python3 "${ROOT_DIR}/scripts/inspect/write_apollo_initial_state_manifest.py" \
        --output "${OUT_DIR}/initial-state.json" \
        --artifact "rse_rom=${RSE_ROM}" \
        --artifact "rse_flash=${RSE_FLASH}" \
        --artifact "rse_otp=${RSE_OTP}" \
        --artifact "ap_flash=${AP_FLASH}" \
        --artifact "rootfs=${ROOTFS}" \
        --artifact "efi_capsule_disk=${EFI_CAPSULE_DISK}" \
        --artifact "provisioning_bundle=${PROVISIONING_BUNDLE}"
fi
if [[ "${RUN_QBOX_COPY_DISKS}" == "1" ]]; then
    RUN_ROOTFS="${OUT_DIR}/input-images/$(basename "${ROOTFS}")"
    RUN_EFI_CAPSULE_DISK="${OUT_DIR}/input-images/$(basename "${EFI_CAPSULE_DISK}")"
    if [[ "${DRY_RUN}" == "0" ]]; then
        copy_sparse "${ROOTFS}" "${RUN_ROOTFS}"
        copy_sparse "${EFI_CAPSULE_DISK}" "${RUN_EFI_CAPSULE_DISK}"
    fi
fi
if [[ -z "${RSE_OTP_OVERRIDE}" && ! -s "${RSE_OTP}" ]]; then
    if [[ "${MACHINE}" == "apollo-qvp" ]]; then
        die "RSE OTP image is empty: ${RSE_OTP}. Rebuild firmware-apollo-qvp so Yocto generates the provisioned OTP image."
    fi
    RUN_RSE_OTP="${OUT_DIR}/input-images/$(basename "${RSE_OTP}")"
    if [[ "${DRY_RUN}" == "0" ]]; then
        python3 "${ROOT_DIR}/scripts/setup/provision_rse_otp_image.py" \
            --root "${ROOT_DIR}" \
            --tfm-build-dir "$(cd "$(dirname "${RSE_BL2_ELF}")/.." && pwd)" \
            --output "${RUN_RSE_OTP}" \
            --size "${RSE_OTP_IMAGE_SIZE}"
    fi
fi

SSH_PORT_VALUE="${SSH_PORT:-$(default_ssh_port_range)}"
NETDEV="type=user,hostfwd=tcp::${SSH_PORT_VALUE}-:22"
export QBOX_APOLLO_NETDEV="${NETDEV}"

RSE_FAST_BOOT_MODE="--rse-fast-boot-sram-dmi"
if [[ "${LEGACY_FILE_BACKED_SRAM}" != "0" ]]; then
    RSE_FAST_BOOT_MODE="--rse-fast-boot-aliases"
fi

QBOX_ACCEL_ARGS=(
    --rse-hotpath-accel
    --rse-lms-accel
    "${RSE_FAST_BOOT_MODE}"
    --rse-bl2-libc-hotpath
    --rse-bl2-delay-accel
    --rse-bl2-load-accel
    --rse-bl2-boot-enc-accel
    --rse-bl2-img-hash-accel
    --rse-bl2-verify-sig-accel
)

if [[ "${HEADLESS}" == "1" ]]; then
    RUNNER_CMD=(
        "${PYTHON:-python3}"
        "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full.py"
        --conf "${QBOX_CONF}"
        --local-build-dir "${LOCAL_BUILD_DIR}"
        --qbox-build-dir "${QBOX_BUILD_DIR}"
        --out-dir "${OUT_DIR}"
        --timeout "${TIMEOUT}"
        --jobs "${JOBS}"
        --skip-build
        --rootfs-bootargs-profile "${ROOTFS_BOOTARGS_PROFILE}"
        --primary-login-prompt "${PRIMARY_LOGIN_PROMPT}"
        --primary-shell-marker "${PRIMARY_SHELL_MARKER}"
        --primary-shell-prompt-re "${PRIMARY_SHELL_PROMPT_RE}"
        --range-limited-flash-dmi
        --qbox-performance-preset
        --cc3xx-qemu-native-backend
    )
else
    RUNNER_CMD=(
        "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
        --session "${TMUX_SESSION}"
        --out-dir "${OUT_DIR}"
        --local-build-dir "${LOCAL_BUILD_DIR}"
        --qbox-build-dir "${QBOX_BUILD_DIR}"
        --conf "${QBOX_CONF}"
        --timeout "${TIMEOUT}"
        --jobs "${JOBS}"
        --skip-build
        --rootfs-bootargs-profile "${ROOTFS_BOOTARGS_PROFILE}"
        --primary-login-prompt "${PRIMARY_LOGIN_PROMPT}"
        --primary-shell-marker "${PRIMARY_SHELL_MARKER}"
        --primary-shell-prompt-re "${PRIMARY_SHELL_PROMPT_RE}"
        --qbox-performance-preset
        --cc3xx-qemu-native-backend
        --netdev "${NETDEV}"
        --tmux-layout fvp-like
    )
    if [[ -n "${DEBUG_TARGET}" ]]; then
        RUNNER_CMD+=(
            --debug-target "${DEBUG_TARGET}"
            --debug-component "${DEBUG_COMPONENT}"
            --debug-endpoint "${DEBUG_ENDPOINT}"
            --debug-manifest "${DEBUG_MANIFEST}"
        )
        if [[ -n "${DEBUG_WAIT_LOG}" ]]; then
            RUNNER_CMD+=(
                --debug-wait-log "${OUT_DIR}/${DEBUG_WAIT_LOG}"
                --debug-wait-marker "${DEBUG_WAIT_MARKER}"
            )
        fi
    fi
fi

if [[ "${KEEP_RUNNING_AFTER_PASS}" == "1" ]]; then
    RUNNER_CMD+=(--keep-running-after-pass)
elif [[ "${HEADLESS}" == "0" ]]; then
    RUNNER_CMD+=(--exit-after-pass)
fi
if [[ "${HEADLESS}" == "0" && "${NO_ATTACH}" == "1" ]]; then
    RUNNER_CMD+=(--no-attach)
fi
if [[ "${HEADLESS}" == "0" && "${DRY_RUN}" == "1" ]]; then
    RUNNER_CMD+=(--dry-run)
fi
if [[ "${HEADLESS}" == "0" && "${MULTI_SESSION}" == "1" ]]; then
    RUNNER_CMD+=(--multi-session)
fi
RUNNER_CMD+=("${TMUX_RUNNER_ARGS[@]}")
if [[ "${HEADLESS}" == "0" ]]; then
    RUNNER_CMD+=(--)
fi
RUNNER_CMD+=(
    --no-post-login-probe
    --rse-rom "${RSE_ROM}"
    --rse-flash "${RSE_FLASH}"
    --rse-otp "${RUN_RSE_OTP}"
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
if [[ -n "${RSE_SYMBOLS}" ]]; then
    RUNNER_CMD+=(--rse-symbols "${RSE_SYMBOLS}")
fi
if [[ "${PERSIST_RSE_STATE}" == "1" ]]; then
    RUNNER_CMD+=(--rse-flash-state "${RSE_STATE_DIR}/rse-flash-image.img")
    if [[ "${RESET_RSE_STATE}" == "1" ]]; then
        RUNNER_CMD+=(--reset-rse-flash-state)
    fi
fi
if [[ "${UBOOT_ONLY}" == "1" ]]; then
    RUNNER_CMD+=(--uboot-only)
fi
if [[ -n "${DEBUG_TARGET}" ]]; then
    if [[ "${DEBUG_TARGET}" == "qbox" ]]; then
        export QBOX_HOST_GDB_EXEC="${ROOT_DIR}/scripts/debug/gdbserver_gdb_wrapper.sh"
        export QBOX_HOST_GDBSERVER_ENDPOINT="${DEBUG_ENDPOINT}"
        RUNNER_CMD+=(--host-gdb-script "${DEBUG_GDB_SCRIPT}")
    fi
    for debug_param in "${DEBUG_PLATFORM_PARAMS[@]}"; do
        RUNNER_CMD+=(--platform-param "${debug_param}")
    done
fi
RUNNER_CMD+=("${QBOX_ACCEL_ARGS[@]}")
RUNNER_CMD+=("${EXTRA_CHILD_ARGS[@]}")

if [[ -z "${DEBUG_RESULT}" ]]; then
    DEBUG_RESULT="${OUT_DIR}/debug-result.json"
elif [[ "${DEBUG_RESULT}" != /* ]]; then
    DEBUG_RESULT="${PWD}/${DEBUG_RESULT}"
fi

AGENT_CMD=()
if [[ -n "${DEBUG_TARGET}" && "${DEBUG_MODE}" != "interactive" ]]; then
    AGENT_CMD=(
        "${PYTHON:-python3}"
        "${ROOT_DIR}/scripts/debug/run_agent_qbox_debug.py"
        --mode "${DEBUG_MODE}"
        --target "${DEBUG_TARGET}"
        --component "${DEBUG_COMPONENT}"
        --breakpoint "${DEBUG_ENTRYPOINT}"
        --expected-pc "${DEBUG_ENTRY_ADDRESS}"
        --endpoint "${DEBUG_ENDPOINT}"
        --manifest "${DEBUG_MANIFEST}"
        --out-dir "${OUT_DIR}"
        --result "${DEBUG_RESULT}"
        --timeout "${DEBUG_TIMEOUT}"
        --runner-cwd "${ROOT_DIR}"
    )
    if [[ -n "${DEBUG_WAIT_LOG}" ]]; then
        AGENT_CMD+=(
            --wait-log "${OUT_DIR}/${DEBUG_WAIT_LOG}"
            --wait-marker "${DEBUG_WAIT_MARKER}"
        )
    fi
    AGENT_CMD+=(-- "${RUNNER_CMD[@]}")
fi

cat <<EOF
Apollo QBox Yocto launch
  machine:       ${MACHINE}
  boot profile:  ${BOOT_PROFILE}
  deploy dir:    ${DEPLOY_DIR}
  work dir:      ${YOCTO_WORK_DIR}
  output dir:    ${OUT_DIR}
  session:       ${TMUX_SESSION}
  multi session: ${MULTI_SESSION}
  headless:      ${HEADLESS}
  qboxconf:      ${QBOX_CONF_FILE:-}
  qbox tools:    ${QBOX_TOOL_DIR}
  qbox conf:     ${QBOX_CONF}
  ap cpus:       ${QBOX_APOLLO_NUM_CPUS}
  rootfs:        ${RUN_ROOTFS}
  efi disk:      ${RUN_EFI_CAPSULE_DISK}
  rse otp:       ${RUN_RSE_OTP}
  rse state:     $([[ "${PERSIST_RSE_STATE}" == "1" ]] && printf '%s' "${RSE_STATE_DIR}/rse-flash-image.img" || printf '%s' ephemeral)
  initial state:  $([[ "${RUN_QBOX_RECORD_INITIAL_STATE}" == "1" ]] && printf '%s' 'SHA-256 manifest' || printf '%s' skipped)
  ssh port:      ${SSH_PORT_VALUE}
EOF

if [[ -n "${DEBUG_TARGET}" ]]; then
    cat <<EOF
  debug target:  ${DEBUG_TARGET}
  debug mode:    ${DEBUG_MODE}
  component:     ${DEBUG_COMPONENT}
  entrypoint:    ${DEBUG_ENTRYPOINT}
  gdb endpoint:  ${DEBUG_ENDPOINT}
  manifest:      ${DEBUG_MANIFEST}
  debug timeout: ${DEBUG_TIMEOUT}
  debug result:  ${DEBUG_RESULT}
EOF
    if [[ -n "${DEBUG_ARTIFACT_ELF}" ]]; then
        printf '  debug ELF:     %s\n' "${DEBUG_ARTIFACT_ELF}"
    fi
    if [[ -n "${DEBUG_WAIT_LOG}" ]]; then
        printf '  debug attach:  %s contains %s\n' \
            "${DEBUG_WAIT_LOG}" "${DEBUG_WAIT_MARKER}"
    fi
fi

if [[ "${HEADLESS}" == "1" && "${DRY_RUN}" == "1" ]]; then
    printf 'Headless QBox runner command:\n  '
    if ((${#AGENT_CMD[@]} > 0)); then
        printf '%q ' "${AGENT_CMD[@]}"
    else
        printf '%q ' "${RUNNER_CMD[@]}"
    fi
    printf '\n'
    exit 0
fi

if [[ "${HEADLESS}" == "1" ]]; then
    export QBOX_MANAGED_SESSION=1
    export QBOX_SESSION_OWNER_UID
    export QBOX_SESSION_OUT_DIR="${OUT_DIR}"
    QBOX_SESSION_OWNER_UID="$(id -u)"
fi

if ((${#AGENT_CMD[@]} > 0)); then
    exec "${AGENT_CMD[@]}"
fi
exec "${RUNNER_CMD[@]}"

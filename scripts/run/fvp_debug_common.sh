#!/usr/bin/env bash

fvp_debug_usage()
{
    cat <<'EOF'
Available --debug targets:
  rse, si_cl0, si_cl1, tf-a, u-boot, linux
EOF
}

fvp_debug_configure_target()
{
    case "${DEBUG_TARGET}" in
        rse)
            DEBUG_COMPONENT="tfm-bl1_1"
            DEBUG_ENTRYPOINT="Reset_Handler"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.smb.rseil.rse.cpu"
            ;;
        si_cl0)
            DEBUG_COMPONENT="scp-si0"
            DEBUG_ENTRYPOINT="arch_exception_reset"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.smb.si.cluster0.cpu0"
            ;;
        si_cl1)
            DEBUG_COMPONENT="si-cl1-zephyr"
            DEBUG_ENTRYPOINT="z_cstart"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.smb.si.cluster1.cpu0"
            ;;
        tf-a)
            DEBUG_COMPONENT="tfa-bl2"
            DEBUG_ENTRYPOINT="bl2_main"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.app00.cluster.cpu0"
            ;;
        u-boot)
            DEBUG_COMPONENT="u-boot"
            DEBUG_ENTRYPOINT="_start"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.app00.cluster.cpu0"
            ;;
        linux)
            DEBUG_COMPONENT="linux"
            DEBUG_ENTRYPOINT="start_kernel"
            DEBUG_IRIS_INSTANCE="component.RD_ASD.css.app00.cluster.cpu0"
            ;;
        *)
            die "invalid --debug target: ${DEBUG_TARGET}"
            ;;
    esac
    export DEBUG_COMPONENT DEBUG_ENTRYPOINT DEBUG_IRIS_INSTANCE
}

fvp_debug_latest_file()
{
    local pattern="$1"
    local path
    local -a matches=()

    while IFS= read -r path; do
        [[ -f "${path}" ]] && matches+=("${path}")
    done < <(compgen -G "${pattern}" || true)
    ((${#matches[@]} > 0)) || return 1
    printf '%s\n' "${matches[@]}" |
        while IFS= read -r path; do
            printf '%s\t%s\n' "$(stat -c '%Y' "${path}")" "${path}"
        done |
        sort -nr |
        sed -n '1s/^[^	]*	//p'
}

fvp_debug_resolve_elf()
{
    local machine_prefix="${MACHINE//-/_}"
    local machine_work="${YOCTO_BUILD_DIR}/tmp_baremetal/work/${machine_prefix}-poky-linux"
    local pattern

    case "${DEBUG_COMPONENT}" in
        tfm-bl1_1)
            pattern="${machine_work}/trusted-firmware-m/*/build/bin/bl1_1.elf"
            ;;
        scp-si0)
            pattern="${machine_work}/scp-firmware/*/build/ramfw/si0/bin/${MACHINE}-si0-bl2.elf"
            ;;
        si-cl1-zephyr)
            pattern="${YOCTO_BUILD_DIR}/tmp_baremetal/work/${machine_prefix}_safety_island_c1-zephyr/zephyr-demos-cl1/*/build/zephyr/zephyr.elf"
            ;;
        tfa-bl2)
            pattern="${machine_work}/trusted-firmware-a/*/build/${machine_prefix}/debug/bl2/bl2.elf"
            ;;
        u-boot)
            pattern="${machine_work}/u-boot/*/build/u-boot"
            ;;
        linux)
            pattern="${machine_work}/linux-yocto-rt/*/build/vmlinux"
            ;;
        *)
            die "no Yocto ELF resolver for ${DEBUG_COMPONENT}"
            ;;
    esac

    DEBUG_ELF="$(fvp_debug_latest_file "${pattern}" || true)"
    [[ -n "${DEBUG_ELF}" ]] ||
        die "debug ELF not found for ${DEBUG_TARGET}; tried: ${pattern}"
}

fvp_debug_validate_manifest()
{
    python3 - "${DEBUG_MANIFEST}" "${DEBUG_COMPONENT}" "${DEBUG_ENTRYPOINT}" <<'PY'
import json
from pathlib import Path
import sys

manifest_path = Path(sys.argv[1])
component_name = sys.argv[2]
entrypoint = sys.argv[3]
try:
    component = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )["components"][component_name]
except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
    raise SystemExit(
        f"error: debug manifest has no usable {component_name} record: {error}"
    )
for field in ("elf", "gdb_script"):
    path = Path(component.get(field, ""))
    if not path.is_file():
        raise SystemExit(f"error: missing {component_name}.{field}: {path}")
if not component.get("has_debug_info") or not component.get("has_debug_line"):
    raise SystemExit(f"error: {component_name} ELF has no usable DWARF")
if entrypoint not in component.get("source_locations", {}):
    raise SystemExit(
        f"error: {component_name} has no source line for {entrypoint}"
    )
PY
}

fvp_debug_prepare_manifest()
{
    fvp_debug_resolve_elf
    mkdir -p "${DEBUG_DIR}"
    python3 "${ROOT_DIR}/scripts/setup/setup_local_debug_env.py" \
        --local-build-dir "${YOCTO_BUILD_DIR}" \
        --out-dir "${DEBUG_DIR}" \
        --elf "${DEBUG_COMPONENT}=${DEBUG_ELF}"
    fvp_debug_validate_manifest
}

fvp_debug_resolve_cornea()
{
    local required="${1:-1}"
    local components_dir="${YOCTO_BUILD_DIR}/tmp_baremetal/sysroots-components"

    if [[ -z "${CORNEA_BIN}" ]]; then
        CORNEA_BIN="$(
            fvp_debug_latest_file \
                "${components_dir}/*/lite-cornea-native/usr/bin/cornea" ||
                true
        )"
    fi
    if [[ -z "${CORNEA_BIN}" ]]; then
        CORNEA_BIN="${components_dir}/$(uname -m)/lite-cornea-native/usr/bin/cornea"
    fi

    if [[ "${required}" == "1" && ! -x "${CORNEA_BIN}" ]]; then
        die "Yocto lite-cornea-native executable not found: ${CORNEA_BIN}; run ./yocto_build.sh first"
    fi
}

fvp_debug_port_in_use()
{
    python3 - "${IRIS_PORT}" <<'PY'
import socket
import sys

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    raise SystemExit(sock.connect_ex(("127.0.0.1", int(sys.argv[1]))) != 0)
PY
}

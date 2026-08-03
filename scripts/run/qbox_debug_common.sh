#!/usr/bin/env bash

# The target mapper intentionally populates globals consumed by sourcing launchers.
# shellcheck disable=SC2034

qbox_debug_usage()
{
    cat <<'EOF'
Available --debug targets:
  qbox, rse, si_cl0, si_cl1, tf-a, u-boot, linux
EOF
}

qbox_debug_configure_target()
{
    DEBUG_COMPONENT=""
    DEBUG_ENTRYPOINT=""
    DEBUG_ENDPOINT=""
    DEBUG_WAIT_LOG=""
    DEBUG_WAIT_MARKER=""
    DEBUG_CPU_PARAM=""
    DEBUG_GDB_THREAD=""
    DEBUG_MPIDR=""
    DEBUG_TOPOLOGY_OPTION=""
    DEBUG_PLATFORM_PARAMS=()

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
            DEBUG_GDB_THREAD="1"
            DEBUG_MPIDR="0x0"
            DEBUG_TOPOLOGY_OPTION="--si-single-gic"
            DEBUG_PLATFORM_PARAMS=(
                "platform.si_cl0_cpu_0.gdb_port=12341"
            )
            ;;
        si_cl1)
            DEBUG_COMPONENT="si-cl1-zephyr"
            DEBUG_ENTRYPOINT="z_cstart"
            DEBUG_ENDPOINT="127.0.0.1:12341"
            DEBUG_CPU_PARAM="platform.si_cl1_cpu_0"
            DEBUG_GDB_THREAD="2"
            DEBUG_MPIDR="0x10000"
            DEBUG_TOPOLOGY_OPTION="--si-single-gic"
            DEBUG_PLATFORM_PARAMS=(
                "platform.si_cl0_cpu_0.gdb_port=12341"
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

qbox_debug_validate_manifest()
{
    local manifest="$1"
    local component="$2"
    local entrypoint="$3"

    python3 - "${manifest}" "${component}" "${entrypoint}" <<'PY'
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

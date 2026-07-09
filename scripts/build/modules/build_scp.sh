#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

build_scp()
{
    require_dir "${SCP_SRC}"
    reset_cmake_build_if_source_changed "${SCP_BUILD_DIR}" "${SCP_SRC}"
    local toolchain="${SCP_SRC}/product/automotive-rd/${SCP_PLATFORM}/si0_ramfw/Toolchain-GNU.cmake"
    require_file "${toolchain}"
    local cmake_ccache_args=()
    local_build_cmake_ccache_args cmake_ccache_args

    run_cmake_configure_if_needed scp-configure "${SCP_BUILD_DIR}" cmake \
        -S "${SCP_SRC}" \
        -B "${SCP_BUILD_DIR}" \
        -G Ninja \
        "${cmake_ccache_args[@]}" \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_TOOLCHAIN_FILE="${toolchain}" \
        -DCMAKE_C_COMPILER="$(command -v "${AARCH64_NONE_ELF_PREFIX}gcc")" \
        -DCMAKE_ASM_COMPILER="$(command -v "${AARCH64_NONE_ELF_PREFIX}gcc")" \
        -DSCP_TOOLCHAIN:STRING=GNU \
        -DSCP_FIRMWARE_SOURCE_DIR:PATH="automotive-rd/${SCP_PLATFORM}/si0_ramfw" \
        -DSCP_ENABLE_DEBUGGER=1 \
        -DSCP_ENABLE_SCMI_PFDI_MONITOR="${PFDI_MONITOR_SUPPORT}" \
        -DSCP_PC_CONFIGURED_CORES_COUNT="${PC_CPUS_COUNT}" \
        -DSCP_PFDI_ONLINE_TIMEOUT_US=100000UL \
        -DSCP_SICL1_PFDI_ONLINE_TIMEOUT_US=60000UL \
        -DSCP_PLATFORM_VARIANT="${SCP_PLATFORM_VARIANT}" \
        -DSCP_RD_ASPEN_VARIANT_CFG1=0 \
        -DSCP_APOLLO_FVP_VARIANT_CFG1=0

    run_logged scp-build cmake --build "${SCP_BUILD_DIR}" --parallel "${JOBS}"

    local scp_bin
    scp_bin="$(find "${SCP_BUILD_DIR}" \
        \( -path '*/bin/si0_ramfw.bin' -o -path "*/bin/${SCP_PLATFORM}-si0-bl2.bin" \) \
        -print -quit)"
    require_file "${scp_bin}"
    install_artifact "${scp_bin}" "${FW_DIR}/si0_ramfw.bin"
}

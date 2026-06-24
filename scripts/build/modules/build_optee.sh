#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

detect_optee_sp_paths()
{
    local sp_dir="${YOCTO_TMP}/work/apollo_fvp-poky-linux/optee-os/4.7.0/recipe-sysroot/usr/opteesp/bin"
    [[ -d "${sp_dir}" ]] || return 0
    find "${sp_dir}" -maxdepth 1 -type f -name '[0-9a-fA-F]*.stripped.elf' | sort | xargs -r printf '%s '
}

build_optee()
{
    require_dir "${OPTEE_SRC}"
    mkdir -p "${OPTEE_BUILD_DIR}" "${DEPLOY_DIR}/optee"
    local optee_work="${YOCTO_TMP}/work/apollo_fvp-poky-linux/optee-os/4.7.0"
    local optee_sysroot="${optee_work}/recipe-sysroot"
    local optee_native_python="${optee_work}/recipe-sysroot-native/usr/bin/python3-native/python3"
    require_file "${optee_native_python}"

    local sp_paths
    sp_paths="$(detect_optee_sp_paths || true)"
    local cmd=(
        make -C "${OPTEE_SRC}" -j "${JOBS}" V=1
        PYTHON3="${optee_native_python}"
        LIBGCC_LOCATE_CFLAGS="--sysroot=${optee_sysroot}"
        CFLAGS64="--sysroot=${optee_sysroot}"
        CXXFLAGS64="--sysroot=${optee_sysroot}"
        OPTEE_CLIENT_EXPORT="${optee_sysroot}/usr"
        TEEC_EXPORT="${optee_sysroot}/usr"
        COMPILER=gcc
        PLATFORM=automotive_rd-rdaspen
        CFG_ARM64_core=y
        CROSS_COMPILE_core="${AARCH64_PREFIX}"
        CROSS_COMPILE_ta_arm64="${AARCH64_PREFIX}"
        ta-targets=ta_arm64
        O="${OPTEE_BUILD_DIR}"
        HOST_PREFIX="${AARCH64_PREFIX}"
        CROSS_COMPILE64="${AARCH64_PREFIX}"
        CFG_CORE_FFA=y
        CFG_WITH_SP=y
        CFG_DT=y
        CFG_TEE_BENCHMARK=n
        CFG_TEE_CORE_LOG_LEVEL=3
        CFG_SECURE_PARTITION=y
        CFG_MAP_EXT_DT_SECURE=y
        CFG_RAS_LSP_PLAT_RDASPEN=y
        CFG_RAS_LSP=y
    )
    if [[ -n "${sp_paths}" ]]; then
        cmd+=("SP_PATHS=${sp_paths}")
    else
        log "No OP-TEE secure partitions found in Yocto sysroot; building without SP_PATHS"
    fi

    local saved_path="${PATH}"
    path_prepend "$(dirname "${optee_native_python}")"
    run_logged optee-build "${cmd[@]}"
    PATH="${saved_path}"
    install_artifact "${OPTEE_BUILD_DIR}/core/tee-pager_v2.bin" "${DEPLOY_DIR}/optee/tee-pager_v2.bin"
}

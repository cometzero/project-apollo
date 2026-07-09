#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

resolve_optee_yocto_workdir()
{
    local root="${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/optee-os"
    local candidate

    [[ -d "${root}" ]] || return 1
    candidate="$(
        find "${root}" -mindepth 1 -maxdepth 1 -type d -print |
            LC_ALL=C sort |
            tail -n 1
    )"
    [[ -n "${candidate}" ]] || return 1
    printf '%s\n' "${candidate}"
}

detect_optee_sp_paths()
{
    local optee_work="$1"
    local sp_dir="${optee_work}/recipe-sysroot/usr/opteesp/bin"
    [[ -d "${sp_dir}" ]] || return 0
    find "${sp_dir}" -maxdepth 1 -type f -name '[0-9a-fA-F]*.stripped.elf' | sort | xargs -r printf '%s '
}

build_optee()
{
    require_dir "${OPTEE_SRC}"
    mkdir -p "${OPTEE_BUILD_DIR}" "${DEPLOY_DIR}/optee"
    local optee_work
    optee_work="$(resolve_optee_yocto_workdir)" ||
        die "could not find Yocto optee-os workdir under ${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/optee-os"
    local optee_sysroot="${optee_work}/recipe-sysroot"
    local optee_native_python="${optee_work}/recipe-sysroot-native/usr/bin/python3-native/python3"
    require_file "${optee_native_python}"

    local sp_paths
    sp_paths="$(detect_optee_sp_paths "${optee_work}" || true)"
    local optee_ccache_args=()
    local_build_optee_ccache_args optee_ccache_args
    local cmd=(
        make -C "${OPTEE_SRC}" -j "${JOBS}" V=1
        "${optee_ccache_args[@]}"
        PYTHON3="${optee_native_python}"
        LIBGCC_LOCATE_CFLAGS="--sysroot=${optee_sysroot}"
        CFLAGS64="--sysroot=${optee_sysroot}"
        CXXFLAGS64="--sysroot=${optee_sysroot}"
        OPTEE_CLIENT_EXPORT="${optee_sysroot}/usr"
        TEEC_EXPORT="${optee_sysroot}/usr"
        COMPILER=gcc
        PLATFORM="${OPTEE_PLATFORM}"
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

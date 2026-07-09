#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

tfa_recipe_workdir()
{
    local root
    root="$(first_existing_glob "${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/trusted-firmware-a"/* || true)"
    [[ -n "${root}" ]] || die "could not find TF-A Yocto workdir under ${YOCTO_TMP}"
    printf '%s\n' "${root}"
}

build_tfa()
{
    require_dir "${TFA_SRC}"
    require_file "${DEPLOY_DIR}/u-boot/u-boot.bin"
    require_file "${DEPLOY_DIR}/optee/tee-pager_v2.bin"
    mkdir -p "${TFA_BUILD_DIR}" "${DEPLOY_DIR}/tf-a"

    local tfa_marker="${TFA_BUILD_DIR}/.apollo-tfa-build.sha256"
    local tfa_digest
    tfa_digest="$(
        {
            printf 'AARCH64_PREFIX=%s\n' "${AARCH64_PREFIX}"
            printf 'PC_CPUS_COUNT=%s\n' "${PC_CPUS_COUNT}"
            printf 'TF_A_PLATFORM=%s\n' "${TF_A_PLATFORM}"
            printf 'LINUX_DTS=%s\n' "${TFA_LINUX_DTS}"
            printf 'NR_IMAGES_PER_FWU_BANK=%s\n' "${NR_IMAGES_PER_FWU_BANK}"
            printf 'PFDI_SUPPORT=%s\n' "${PFDI_SUPPORT}"
            printf 'PFDI_MONITOR_SUPPORT=%s\n' "${PFDI_MONITOR_SUPPORT}"
            printf 'VARIANT=%s\n' "${VARIANT}"
            local_build_ccache_manifest
            git -C "${TFA_SRC}" rev-parse HEAD 2>/dev/null || true
            git -C "${TFA_SRC}" status --porcelain=v1 --untracked-files=no 2>/dev/null || true
            fingerprint_file_hash "${DEPLOY_DIR}/u-boot/u-boot.bin" tfa-bl33
            fingerprint_file_hash "${DEPLOY_DIR}/optee/tee-pager_v2.bin" tfa-bl32
            fingerprint_file_hash "${BASH_SOURCE[0]}" tfa-build-module
        } | sha256sum | awk '{print $1}'
    )"
    if [[ "${APOLLO_TFA_REFRESH:-0}" != "1" ]] &&
        [[ -f "${TFA_PLATFORM_BUILD_DIR}/debug/bl2.bin" ]] &&
        [[ -f "${TFA_PLATFORM_BUILD_DIR}/debug/fip.bin" ]] &&
        [[ -f "${tfa_marker}" ]] &&
        [[ "$(cat "${tfa_marker}")" == "${tfa_digest}" ]]; then
        log "TF-A build outputs are up to date"
        install_artifact "${TFA_PLATFORM_BUILD_DIR}/debug/bl2.bin" "${FW_DIR}/bl2.bin"
        install_artifact "${TFA_PLATFORM_BUILD_DIR}/debug/fip.bin" "${FW_DIR}/fip.bin"
        return 0
    fi
    local tfa_build_root_real
    local tfa_platform_parent_real
    tfa_build_root_real="$(canonical_dir "${TFA_BUILD_DIR}")"
    tfa_platform_parent_real="$(canonical_dir "$(dirname "${TFA_PLATFORM_BUILD_DIR}")")"
    case "${tfa_platform_parent_real}/$(basename "${TFA_PLATFORM_BUILD_DIR}")" in
        "${tfa_build_root_real}"/*) ;;
        *) die "refusing to reset TF-A build outside TF-A work root: ${TFA_PLATFORM_BUILD_DIR}" ;;
    esac
    [[ ! -L "${TFA_BUILD_DIR}" ]] ||
        die "refusing to reset TF-A build through symlink: ${TFA_BUILD_DIR}"
    [[ ! -L "${TFA_PLATFORM_BUILD_DIR}" ]] ||
        die "refusing to reset TF-A platform build symlink: ${TFA_PLATFORM_BUILD_DIR}"
    rm -rf "${TFA_PLATFORM_BUILD_DIR}"

    local tfa_work
    tfa_work="$(tfa_recipe_workdir)"
    local saved_path="${PATH}"
    local had_pythonpath=0
    [[ -v PYTHONPATH ]] && had_pythonpath=1
    local saved_pythonpath="${PYTHONPATH:-}"
    local tfa_ccache_args=()
    local_build_tfa_ccache_args tfa_ccache_args
    path_prepend "${tfa_work}/recipe-sysroot-native/usr/bin"
    PYTHONPATH="${tfa_work}/recipe-sysroot-native/usr/lib/python3.13/site-packages${PYTHONPATH:+:${PYTHONPATH}}"
    export PYTHONPATH

    run_logged tfa-build make -C "${TFA_SRC}" -j1 \
        LD="${AARCH64_PREFIX}ld" \
        "${tfa_ccache_args[@]}" \
        BUILD_BASE="${TFA_BUILD_DIR}" \
        PLAT="${TF_A_PLATFORM}" \
        SPD=spmd \
        SPMD_SPM_AT_SEL2=0 \
        DEBUG=1 \
        MBEDTLS_DIR=mbedtls \
        BL33="${DEPLOY_DIR}/u-boot/u-boot.bin" \
        BL32="${DEPLOY_DIR}/optee/tee-pager_v2.bin" \
        host-poetry= \
        PLATFORM_CORE_COUNT="${PC_CPUS_COUNT}" \
        LINUX_DTS="${TFA_LINUX_DTS}" \
        MEASURED_BOOT=1 \
        TRUSTED_BOARD_BOOT=1 \
        GENERATE_COT=1 \
        COT=tbbr \
        FAULT_INJECTION_SUPPORT=1 \
        LOG_LEVEL=40 \
        ARM_ROTPK_LOCATION=devel_rsa \
        ARM_ROTPK_LOCATION_ID=ARM_ROTPK_DEVEL_RSA_ID \
        ROT_KEY=plat/arm/board/common/rotpk/arm_rotprivk_rsa.pem \
        PFDI_SUPPORT="${PFDI_SUPPORT}" \
        SCMI_PFDI_MONITOR="${PFDI_MONITOR_SUPPORT}" \
        ARM_GPT_SUPPORT=1 \
        NR_OF_FW_BANKS=2 \
        NR_OF_IMAGES_IN_FW_BANK="${NR_IMAGES_PER_FWU_BANK}" \
        PSA_FWU_SUPPORT=1 \
        RD_ASPEN_VARIANT="${VARIANT}" \
        APOLLO_FVP_VARIANT="${VARIANT}" \
        APOLLO_QVP_VARIANT="${VARIANT}" \
        bl2 fip

    PATH="${saved_path}"
    if [[ "${had_pythonpath}" -eq 1 ]]; then
        PYTHONPATH="${saved_pythonpath}"
        export PYTHONPATH
    else
        unset PYTHONPATH
    fi
    install_artifact "${TFA_PLATFORM_BUILD_DIR}/debug/bl2.bin" "${FW_DIR}/bl2.bin"
    install_artifact "${TFA_PLATFORM_BUILD_DIR}/debug/fip.bin" "${FW_DIR}/fip.bin"
    printf '%s\n' "${tfa_digest}" > "${tfa_marker}"
}

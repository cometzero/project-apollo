#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

apply_git_patch_dir()
{
    local input_dir="$1"
    local dest_dir="$2"
    local patch

    [[ -d "${input_dir}" ]] || die "missing local patch directory: ${input_dir}"
    [[ -d "${dest_dir}" ]] || die "missing patch destination directory: ${dest_dir}"

    shopt -s nullglob
    for patch in "${input_dir}"/*.patch "${input_dir}"/*.diff; do
        if git -C "${dest_dir}" apply --check "${patch}" >/dev/null 2>&1; then
            log "Applying $(basename "${patch}") to ${dest_dir}"
            git -C "${dest_dir}" apply "${patch}"
        elif git -C "${dest_dir}" apply --reverse --check "${patch}" >/dev/null 2>&1; then
            log "Patch already applied: $(basename "${patch}")"
        else
            die "failed to apply patch $(basename "${patch}") to ${dest_dir}"
        fi
    done
    shopt -u nullglob
}

reset_generated_git_tree()
{
    local dest_dir="$1"

    [[ -d "${dest_dir}/.git" ]] || die "missing generated git tree: ${dest_dir}"
    git -C "${dest_dir}" reset --hard >/dev/null
    git -C "${dest_dir}" clean -fd >/dev/null
}

patch_dirs_manifest()
{
    local dest_dir="$1"
    shift
    local patch_dir
    local patch

    printf 'dest=%s\n' "$(canonical_dir "${dest_dir}")"
    git -C "${dest_dir}" rev-parse HEAD
    for patch_dir in "$@"; do
        printf 'patch_dir=%s\n' "$(canonical_dir "${patch_dir}")"
        shopt -s nullglob
        for patch in "${patch_dir}"/*.patch "${patch_dir}"/*.diff; do
            sha256sum "${patch}"
        done
        shopt -u nullglob
    done
}

apply_git_patch_dirs_cached()
{
    local name="$1"
    local dest_dir="$2"
    shift 2
    local marker_dir="${TFM_BUILD_DIR}/patch-stamps"
    local marker="${marker_dir}/${name}.sha256"
    local manifest
    local digest
    local patch_dir

    mkdir -p "${marker_dir}"
    manifest="$(patch_dirs_manifest "${dest_dir}" "$@")"
    digest="$(printf '%s\n' "${manifest}" | sha256sum | awk '{print $1}')"

    if [[ -f "${marker}" ]] && [[ "$(cat "${marker}")" == "${digest}" ]]; then
        log "Patch set is up to date for ${dest_dir}"
        return 0
    fi

    reset_generated_git_tree "${dest_dir}"
    for patch_dir in "$@"; do
        apply_git_patch_dir "${patch_dir}" "${dest_dir}"
    done
    printf '%s\n' "${digest}" > "${marker}"
}

remove_tfm_signed_outputs()
{
    rm -f \
        "${TFM_BUILD_DIR}/bin/bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bin/fwu_test_bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" \
        "${TFM_BUILD_DIR}/bin/fwu_test_tfm_s_signed.bin" \
        "${TFM_BUILD_DIR}/bl1/bl1_2/bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bl1/bl1_2/fwu_test_bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bl2/ext/mcuboot/tfm_s_signed.bin" \
        "${TFM_BUILD_DIR}/bl2/ext/mcuboot/fwu_test_tfm_s_signed.bin"
}

tfm_signed_outputs_stale()
{
    local bl2="${TFM_BUILD_DIR}/bin/bl2.bin"
    local tfm_s="${TFM_BUILD_DIR}/bin/tfm_s.bin"
    local output

    for output in \
        "${TFM_BUILD_DIR}/bin/bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bin/fwu_test_bl2_signed.bin"; do
        [[ -f "${output}" ]] || return 0
        [[ -f "${bl2}" && "${bl2}" -nt "${output}" ]] && return 0
    done

    for output in \
        "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" \
        "${TFM_BUILD_DIR}/bin/fwu_test_tfm_s_signed.bin"; do
        [[ -f "${output}" ]] || return 0
        [[ -f "${tfm_s}" && "${tfm_s}" -nt "${output}" ]] && return 0
    done

    return 1
}

tfm_build_outputs_present()
{
    local file

    for file in \
        "${TFM_BUILD_DIR}/bin/bl1_1.bin" \
        "${TFM_BUILD_DIR}/bin/bl2_signed.bin" \
        "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" \
        "${TFM_BUILD_DIR}/bin/rom_dma_ics.bin" \
        "${TFM_BUILD_DIR}/bin/enc_key_s.b64" \
        "${TFM_BUILD_DIR}/bin/provisioning/combined_provisioning_message.bin"; do
        [[ -f "${file}" ]] || return 1
    done
}

tfm_build_manifest()
{
    local tfm_deps="$1"
    local dep

    printf 'ARM_NONE_EABI_PREFIX=%s\n' "${ARM_NONE_EABI_PREFIX}"
    printf 'ARM_NONE_EABI_GCC=%s\n' "$(command -v "${ARM_NONE_EABI_PREFIX}gcc")"
    printf 'NR_IMAGES_PER_FWU_BANK=%s\n' "${NR_IMAGES_PER_FWU_BANK}"
    printf 'TFM_PLATFORM=arm/rse/automotive_rd/apollo-fvp\n'
    printf 'TFM_PLATFORM_VARIANT=fvp\n'
    printf 'TFM_RTL_VARIANT=emu\n'
    git_tree_manifest "${TFM_SRC}" tfm-src
    for dep in tfm-extras qcbor mbedtls t_cose mcuboot cmsis tf-m-tests; do
        git_tree_manifest "${tfm_deps}/${dep}" "tfm-dep-${dep}"
    done
    fingerprint_file_hash "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.prv" tfm-rotpk-prv
    fingerprint_file_hash "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.pub" tfm-rotpk-pub
    fingerprint_file_hash "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.prv" tfm-rotpk-1-prv
    fingerprint_file_hash "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.pub" tfm-rotpk-1-pub
    fingerprint_file_hash "${TFM_BUILD_DIR}/patch-stamps/tfm-extras.sha256" tfm-patch-tfm-extras
    fingerprint_file_hash "${TFM_BUILD_DIR}/patch-stamps/qcbor.sha256" tfm-patch-qcbor
    fingerprint_file_hash "${TFM_BUILD_DIR}/patch-stamps/mbedtls.sha256" tfm-patch-mbedtls
    fingerprint_file_hash "${TFM_BUILD_DIR}/patch-stamps/t-cose.sha256" tfm-patch-t-cose
}

tfm_recipe_workdir()
{
    local root
    root="$(first_existing_glob "${YOCTO_TMP}/work/apollo_fvp-poky-linux/trusted-firmware-m"/* || true)"
    [[ -n "${root}" ]] || die "could not find TF-M Yocto workdir under ${YOCTO_TMP}"
    printf '%s\n' "${root}"
}

tfm_dependency_root()
{
    local root
    root="$(tfm_recipe_workdir)/sources-unpack/git"
    require_dir "${root}"
    printf '%s\n' "${root}"
}

build_tfm()
{
    require_dir "${TFM_SRC}"
    reset_cmake_build_if_source_changed "${TFM_BUILD_DIR}" "${TFM_SRC}"
    mkdir -p "${TFM_BUILD_DIR}/externalsrc-keys" "${FW_DIR}"
    local tfm_work
    tfm_work="$(tfm_recipe_workdir)"
    local tfm_deps
    tfm_deps="$(tfm_dependency_root)"
    local cmake_bin
    cmake_bin="$(command -v cmake)"
    local saved_path="${PATH}"
    local tfm_native_bin="${tfm_work}/recipe-sysroot-native/usr/bin"

    apply_git_patch_dirs_cached tfm-extras "${tfm_deps}/tfm-extras" \
        "${ROOT_DIR}/arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/files/tf-m-extras/fvp-rd-aspen" \
        "${TFM_SRC}/lib/ext/tf-m-extras"
    apply_git_patch_dirs_cached qcbor "${tfm_deps}/qcbor" \
        "${TFM_SRC}/lib/ext/qcbor"
    apply_git_patch_dirs_cached mbedtls "${tfm_deps}/mbedtls" \
        "${TFM_SRC}/lib/ext/mbedcrypto"
    apply_git_patch_dirs_cached t-cose "${tfm_deps}/t_cose" \
        "${TFM_SRC}/lib/ext/t_cose"

    copy_file_if_changed "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.prv" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.prv" 0600
    copy_file_if_changed "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.pub" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.pub" 0644
    copy_file_if_changed "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.prv" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.prv" 0600
    copy_file_if_changed "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.pub" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.pub" 0644

    local tfm_marker="${TFM_BUILD_DIR}/.apollo-tfm-build.sha256"
    local tfm_digest
    tfm_digest="$(tfm_build_manifest "${tfm_deps}" | sha256sum | awk '{print $1}')"
    if [[ "${APOLLO_TFM_REFRESH:-0}" != "1" ]] &&
        [[ -f "${tfm_marker}" ]] &&
        [[ "$(cat "${tfm_marker}")" == "${tfm_digest}" ]] &&
        tfm_build_outputs_present; then
        log "TF-M build outputs are up to date"
        install_artifact "${TFM_BUILD_DIR}/bin/bl1_1.bin" "${FW_DIR}/bl1_1.bin"
        install_artifact "${TFM_BUILD_DIR}/bin/bl2_signed.bin" "${FW_DIR}/bl2_signed.bin"
        install_artifact "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" "${FW_DIR}/tfm_s_signed.bin"
        install_artifact "${TFM_BUILD_DIR}/bin/rom_dma_ics.bin" "${FW_DIR}/rom_dma_ics.bin"
        install_artifact "${TFM_BUILD_DIR}/bin/enc_key_s.b64" "${FW_DIR}/enc_key_s.b64"
        install_artifact "${TFM_BUILD_DIR}/bin/provisioning/combined_provisioning_message.bin" \
            "${FW_DIR}/combined_provisioning_message.bin"
        return 0
    fi

    run_cmake_configure_if_needed tfm-configure "${TFM_BUILD_DIR}" "${cmake_bin}" \
        -S "${TFM_SRC}" \
        -B "${TFM_BUILD_DIR}" \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_COMPILER="$(command -v "${ARM_NONE_EABI_PREFIX}gcc")" \
        -DCMAKE_CXX_COMPILER="$(command -v "${ARM_NONE_EABI_PREFIX}g++")" \
        -DCMAKE_OBJCOPY="$(command -v "${ARM_NONE_EABI_PREFIX}objcopy")" \
        -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
        -DPython3_EXECUTABLE="${tfm_work}/recipe-sysroot-native/usr/bin/python3-native/python3" \
        -DTFM_PLATFORM=arm/rse/automotive_rd/apollo-fvp \
        -DTFM_TOOLCHAIN_FILE="${TFM_SRC}/toolchain_GNUARM.cmake" \
        -DMBEDCRYPTO_PATH="${tfm_deps}/mbedtls" \
        -DTFM_TEST_REPO_PATH="${tfm_deps}/tf-m-tests" \
        -DTFM_EXTRAS_REPO_PATH="${tfm_deps}/tfm-extras" \
        -DMCUBOOT_PATH="${tfm_deps}/mcuboot" \
        -DQCBOR_PATH="${tfm_deps}/qcbor" \
        -DCMSIS_PATH="${tfm_deps}/cmsis" \
        -DT_COSE_PATH="${tfm_deps}/t_cose" \
        -DTFM_SPM_LOG_LEVEL=LOG_LEVEL_INFO \
        -DTFM_PARTITION_LOG_LEVEL=LOG_LEVEL_INFO \
        -DCONFIG_TFM_FWU_GEN_TEST_IMAGES=ON \
        -DRSE_ENABLE_TRAM:BOOL=ON \
        -DNR_OF_IMAGES_IN_FW_BANK="${NR_IMAGES_PER_FWU_BANK}" \
        -DTFM_PLATFORM_VARIANT=fvp \
        -DTFM_RTL_VARIANT=emu \
        -DPLATFORM_HAS_STRATA_FLASH=ON \
        -DTFM_BL1_2_CM_SIGNING_KEY_PATH="${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.pub" \
        -DTFM_BL1_2_DM_SIGNING_KEY_PATH="${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.pub"

    PATH="${tfm_native_bin}:${saved_path}"
    run_logged tfm-build "${cmake_bin}" --build "${TFM_BUILD_DIR}" --target install --parallel "${JOBS}"
    if tfm_signed_outputs_stale; then
        log "Refreshing stale TF-M signed outputs"
        remove_tfm_signed_outputs
        run_logged tfm-build-resign "${cmake_bin}" --build "${TFM_BUILD_DIR}" --target install --parallel "${JOBS}"
    fi
    PATH="${saved_path}"

    install_artifact "${TFM_BUILD_DIR}/bin/bl1_1.bin" "${FW_DIR}/bl1_1.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/bl2_signed.bin" "${FW_DIR}/bl2_signed.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" "${FW_DIR}/tfm_s_signed.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/rom_dma_ics.bin" "${FW_DIR}/rom_dma_ics.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/enc_key_s.b64" "${FW_DIR}/enc_key_s.b64"
    install_artifact "${TFM_BUILD_DIR}/bin/provisioning/combined_provisioning_message.bin" \
        "${FW_DIR}/combined_provisioning_message.bin"
    printf '%s\n' "${tfm_digest}" > "${tfm_marker}"
}

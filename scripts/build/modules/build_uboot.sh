#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

build_uboot()
{
    require_dir "${UBOOT_SRC}"
    local key="${ROOT_DIR}/arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/u-boot/files/fvp-rd-aspen/capsule_dev_priv_key.pem"
    require_file "${key}"
    mkdir -p "${UBOOT_BUILD_DIR}" "${DEPLOY_DIR}/u-boot"

    copy_file_if_changed "${key}" "${UBOOT_BUILD_DIR}/CRT.key" 0600
    if [[ ! -f "${UBOOT_BUILD_DIR}/CRT.crt" ]] ||
        [[ "${UBOOT_BUILD_DIR}/CRT.key" -nt "${UBOOT_BUILD_DIR}/CRT.crt" ]]; then
        run_logged u-boot-capsule-cert openssl req -new -x509 \
            -key "${UBOOT_BUILD_DIR}/CRT.key" \
            -out "${UBOOT_BUILD_DIR}/CRT.crt" \
            -days 365 \
            -subj /CN=CRT/
    else
        log "u-boot-capsule-cert is up to date"
    fi

    local crt_rel
    crt_rel="$(realpath --relative-to="${UBOOT_SRC}" "${UBOOT_BUILD_DIR}/CRT.crt")"
    local kbuild_ccache_args=()
    local_build_kbuild_ccache_args kbuild_ccache_args "${AARCH64_PREFIX}"
    local config_marker="${UBOOT_BUILD_DIR}/.apollo-config.sha256"
    local config_digest
    config_digest="$(
        {
            printf 'AARCH64_PREFIX=%s\n' "${AARCH64_PREFIX}"
            printf 'VARIANT=%s\n' "${VARIANT}"
            printf 'UBOOT_MACHINE=%s\n' "${UBOOT_MACHINE}"
            printf 'EFI_CAPSULE_CRT_FILE=%s\n' "${crt_rel}"
            fingerprint_file_hash "${key}" u-boot-capsule-key
            fingerprint_file_hash "${UBOOT_SRC}/configs/${UBOOT_MACHINE}" u-boot-defconfig
            find "${UBOOT_SRC}" \( -name Kconfig -o -name 'Kconfig.*' \) \
                -type f -printf 'u-boot-kconfig/%P|%s|%T@\n' | LC_ALL=C sort
        } | sha256sum | awk '{print $1}'
    )"
    if [[ "${APOLLO_UBOOT_FORCE_CONFIG:-0}" != "1" ]] &&
        [[ -f "${UBOOT_BUILD_DIR}/.config" ]] &&
        [[ -f "${config_marker}" ]] &&
        [[ "$(cat "${config_marker}")" == "${config_digest}" ]]; then
        log "U-Boot config is up to date"
    else
        run_logged u-boot-defconfig make -C "${UBOOT_SRC}" \
            O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
            "${kbuild_ccache_args[@]}" \
            RD_ASPEN_VARIANT="${VARIANT}" "${UBOOT_MACHINE}"
        "${UBOOT_SRC}/scripts/config" --file "${UBOOT_BUILD_DIR}/.config" \
            --set-str EFI_CAPSULE_CRT_FILE "${crt_rel}"
        run_logged u-boot-olddefconfig make -C "${UBOOT_SRC}" \
            O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
            "${kbuild_ccache_args[@]}" \
            RD_ASPEN_VARIANT="${VARIANT}" olddefconfig
        printf '%s\n' "${config_digest}" > "${config_marker}"
    fi

    run_logged u-boot-build env \
        SOURCE_DATE_EPOCH="${APOLLO_SOURCE_DATE_EPOCH:-${SOURCE_DATE_EPOCH:-0}}" \
        make -C "${UBOOT_SRC}" \
        O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
        "${kbuild_ccache_args[@]}" \
        RD_ASPEN_VARIANT="${VARIANT}" -j "${JOBS}"

    install_artifact "${UBOOT_BUILD_DIR}/u-boot.bin" "${DEPLOY_DIR}/u-boot/u-boot.bin"
}

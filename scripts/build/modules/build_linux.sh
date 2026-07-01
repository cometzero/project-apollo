#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

find_linux_config()
{
    if [[ -n "${LINUX_CONFIG:-}" ]]; then
        printf '%s\n' "${LINUX_CONFIG}"
        return 0
    fi
    printf '%s\n' "${LINUX_SRC}/arch/arm64/configs/${LINUX_DEFCONFIG}"
}

build_linux()
{
    require_dir "${LINUX_SRC}"
    mkdir -p "${LINUX_BUILD_DIR}" "${BOOT_DIR}"

    local config
    config="$(find_linux_config || true)"
    require_file "${config}"
    local use_config_file=0
    [[ -n "${LINUX_CONFIG:-}" ]] && use_config_file=1
    local kbuild_ccache_args=()
    local_build_kbuild_ccache_args kbuild_ccache_args "${AARCH64_PREFIX}"

    local modsign_key
    modsign_key="$(find "${YOCTO_TMP}/work/apollo_fvp-poky-linux/linux-yocto-rt" \
        -path '*/build/modsign_key.pem' -type f -print -quit 2>/dev/null || true)"

    local config_marker="${LINUX_BUILD_DIR}/.apollo-config.sha256"
    local config_digest
    config_digest="$(
        {
            printf 'AARCH64_PREFIX=%s\n' "${AARCH64_PREFIX}"
            printf 'KERNEL_DEBUG_INFO=%s\n' "${KERNEL_DEBUG_INFO}"
            printf 'LINUX_DEFCONFIG=%s\n' "${LINUX_DEFCONFIG}"
            printf 'LINUX_CONFIG=%s\n' "${LINUX_CONFIG:-}"
            fingerprint_file_hash "${config}" linux-input-config
            [[ -z "${modsign_key}" ]] || fingerprint_file_hash "${modsign_key}" linux-input-modsign-key
            find "${LINUX_SRC}" \( -name Kconfig -o -name 'Kconfig.*' \) \
                -type f -printf 'linux-kconfig/%P|%s|%T@\n' | LC_ALL=C sort
        } | sha256sum | awk '{print $1}'
    )"

    if [[ "${APOLLO_LINUX_FORCE_CONFIG:-0}" != "1" ]] &&
        [[ -f "${LINUX_BUILD_DIR}/.config" ]] &&
        [[ -f "${config_marker}" ]] &&
        [[ "$(cat "${config_marker}")" == "${config_digest}" ]]; then
        log "Linux kernel config is up to date"
    else
        if [[ "${use_config_file}" == "1" ]]; then
            write_file_if_changed "${LINUX_BUILD_DIR}/.config" < "${config}"
        else
            run_logged linux-defconfig make -C "${LINUX_SRC}" \
                O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
                "${kbuild_ccache_args[@]}" \
                "${LINUX_DEFCONFIG}"
        fi

        if [[ "${KERNEL_DEBUG_INFO}" == "1" ]]; then
            "${LINUX_SRC}/scripts/config" --file "${LINUX_BUILD_DIR}/.config" \
                --enable DEBUG_KERNEL \
                --disable DEBUG_INFO_NONE \
                --enable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT \
                --enable GDB_SCRIPTS \
                --enable KALLSYMS_ALL
        fi
        LOCAL_LINUX_DM_VERITY=y
        "${LINUX_SRC}/scripts/config" --file "${LINUX_BUILD_DIR}/.config" \
            --enable BLK_DEV_DM \
            --enable DM_BUFIO \
            --enable DM_VERITY \
            --enable CRYPTO_SHA256
        make -C "${LINUX_SRC}" O="${LINUX_BUILD_DIR}" ARCH=arm64 \
            CROSS_COMPILE="${AARCH64_PREFIX}" "${kbuild_ccache_args[@]}" \
            LOCALVERSION= olddefconfig

        if [[ -n "${modsign_key}" ]]; then
            copy_file_if_changed "${modsign_key}" "${LINUX_BUILD_DIR}/modsign_key.pem" 0600
        elif grep -q '^CONFIG_MODULE_SIG_KEY="modsign_key.pem"' "${LINUX_BUILD_DIR}/.config"; then
            if [[ ! -f "${LINUX_BUILD_DIR}/modsign_key.pem" ]]; then
                require_file "${LINUX_SRC}/certs/x509.genkey"
                openssl req -new -nodes -utf8 -sha256 -days 36500 -batch -x509 \
                    -config "${LINUX_SRC}/certs/x509.genkey" \
                    -outform PEM -out "${LINUX_BUILD_DIR}/modsign_key.pem" \
                    -keyout "${LINUX_BUILD_DIR}/modsign_key.pem"
                chmod 0600 "${LINUX_BUILD_DIR}/modsign_key.pem"
            fi
        fi

        run_logged linux-olddefconfig make -C "${LINUX_SRC}" \
            O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
            "${kbuild_ccache_args[@]}" \
            olddefconfig
        printf '%s\n' "${config_digest}" > "${config_marker}"
    fi

    run_logged linux-build env \
        KBUILD_BUILD_TIMESTAMP="${APOLLO_KBUILD_BUILD_TIMESTAMP:-Thu Jan 1 00:00:00 UTC 1970}" \
        KBUILD_BUILD_VERSION="${APOLLO_KBUILD_BUILD_VERSION:-1}" \
        make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        "${kbuild_ccache_args[@]}" \
        Image dtbs modules -j "${JOBS}"

    local image="${LINUX_BUILD_DIR}/arch/arm64/boot/Image"
    local dtb="${LINUX_BUILD_DIR}/arch/arm64/boot/dts/arm/apollo-fvp.dtb"
    require_file "${image}"
    require_file "${dtb}"
    install_artifact "${image}" "${BOOT_DIR}/Image"
    install_artifact "${dtb}" "${BOOT_DIR}/apollo-fvp.dtb"
}

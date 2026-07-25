#!/usr/bin/env bash

# shellcheck disable=SC2153,SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

boot_disk_manifest()
{
    sha256sum \
        "${BOOT_DIR}/Image" \
        "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}" \
        "${BOOT_DIR}/initramfs.cpio.gz" \
        "${LOCAL_BUILD_UKI_STUB}" \
        "${LOCAL_BUILD_UKI_A}" \
        "${LOCAL_BUILD_UKI_B}" \
        "${LOCAL_BUILD_SLOT_METADATA_A}" \
        "${LOCAL_BUILD_SLOT_METADATA_B}" \
        "${LOCAL_BUILD_MISC_IMAGE}"
}

resolve_local_ukify()
{
    local -a configured
    local candidate
    local tool

    read -r -a configured <<<"${UKIFY_CMD:-ukify build}"
    ((${#configured[@]} >= 1 && ${#configured[@]} <= 2)) ||
        die "unsupported UKIFY_CMD arguments: ${UKIFY_CMD:-}"
    if ((${#configured[@]} == 2)) && [[ "${configured[1]}" != "build" ]]; then
        die "unsupported UKIFY_CMD arguments: ${UKIFY_CMD}"
    fi

    tool="${configured[0]}"
    if [[ "${tool}" == "ukify" ]]; then
        candidate="$(first_existing_glob \
            "${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/nexios-bsp-initramfs/*/recipe-sysroot-native/usr/bin/ukify" ||
            true)"
        if [[ -z "${candidate}" ]]; then
            candidate="$(first_existing_glob \
                "${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/nexios-image/*/recipe-sysroot-native/usr/bin/ukify" ||
                true)"
        fi
        if [[ -z "${candidate}" ]]; then
            candidate="$(command -v ukify 2>/dev/null || true)"
        fi
        tool="${candidate}"
    fi

    [[ -n "${tool}" && -x "${tool}" ]] ||
        die "UKIFY_CMD not found or not executable: ${configured[0]}"
    LOCAL_BUILD_UKIFY="${tool}"
    LOCAL_BUILD_UKIFY_PYTHONPATH=""
    LOCAL_BUILD_UKIFY_OS_RELEASE="$(first_existing_glob \
        "${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/nexios-bsp-initramfs/*/recipe-sysroot/usr/lib/os-release" ||
        true)"
    if [[ -z "${LOCAL_BUILD_UKIFY_OS_RELEASE}" ]]; then
        LOCAL_BUILD_UKIFY_OS_RELEASE="$(first_existing_glob \
            "${YOCTO_TMP}/work/${LOCAL_MACHINE_WORK_PREFIX}-poky-linux/nexios-image/*/recipe-sysroot/usr/lib/os-release" ||
            true)"
    fi
    if [[ "${tool}" == */usr/bin/ukify ]]; then
        local native_root="${tool%/usr/bin/ukify}"
        LOCAL_BUILD_UKIFY_PYTHONPATH="$(first_existing_glob \
            "${native_root}/usr/lib/python*/site-packages" || true)"
    fi
    [[ -n "${LOCAL_BUILD_UKIFY_OS_RELEASE}" ]] ||
        die "Yocto target os-release not found for local UKI"
}

build_local_uki()
{
    local slot="$1"
    local output="$2"
    local cmdline="$3"
    local marker="${output}.manifest"
    local tmp="${output}.tmp.$$"
    local manifest
    local kernel_release
    local -a command=(
        "${LOCAL_BUILD_UKIFY}"
        build
        --efi-arch "${EFI_ARCH}"
        "--linux=${BOOT_DIR}/Image"
        --devicetree "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}"
        "--initrd=${BOOT_DIR}/initramfs.cpio.gz"
        --stub "${LOCAL_BUILD_UKI_STUB}"
        "--os-release=@${LOCAL_BUILD_UKIFY_OS_RELEASE}"
        "--cmdline=${cmdline}"
        "--output=${tmp}"
    )

    require_file "${LINUX_BUILD_DIR}/include/config/kernel.release"
    kernel_release="$(<"${LINUX_BUILD_DIR}/include/config/kernel.release")"
    command+=(--uname "${kernel_release}")

    case "${UEFI_SECURE_BOOT}" in
        0) ;;
        1)
            require_file "${UKI_SB_KEY}"
            require_file "${UKI_SB_CERT}"
            command+=(
                --sign-kernel
                "--secureboot-private-key=${UKI_SB_KEY}"
                "--secureboot-certificate=${UKI_SB_CERT}"
            )
            ;;
        *) die "UEFI_SECURE_BOOT must be 0 or 1: ${UEFI_SECURE_BOOT}" ;;
    esac

    manifest="$(
        sha256sum \
            "${BOOT_DIR}/Image" \
            "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}" \
            "${BOOT_DIR}/initramfs.cpio.gz" \
            "${LOCAL_BUILD_UKI_STUB}" \
            "${LOCAL_BUILD_UKIFY_OS_RELEASE}" \
            "${LINUX_BUILD_DIR}/include/config/kernel.release" \
            "${LOCAL_BUILD_UKIFY}"
        printf 'EFI_ARCH=%s\n' "${EFI_ARCH}"
        printf 'CMDLINE=%s\n' "${cmdline}"
        printf 'UEFI_SECURE_BOOT=%s\n' "${UEFI_SECURE_BOOT}"
        if [[ "${UEFI_SECURE_BOOT}" == "1" ]]; then
            sha256sum "${UKI_SB_KEY}" "${UKI_SB_CERT}"
        fi
    )"
    if [[ -f "${output}" && -f "${marker}" ]] &&
        [[ "$(cat "${marker}")" == "${manifest}" ]]; then
        log "Local slot ${slot} UKI is up to date"
        return 0
    fi

    rm -f "${tmp}"
    if [[ -n "${LOCAL_BUILD_UKIFY_PYTHONPATH}" ]]; then
        if ! run_logged "local-uki-${slot}" env \
            "PYTHONPATH=${LOCAL_BUILD_UKIFY_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}" \
            "${command[@]}"; then
            rm -f "${tmp}"
            return 1
        fi
    elif ! run_logged "local-uki-${slot}" "${command[@]}"; then
        rm -f "${tmp}"
        return 1
    fi
    mv "${tmp}" "${output}"
    printf '%s\n' "${manifest}" > "${marker}"
}

ensure_fat_dir()
{
    local fat="$1"
    local relative="$2"
    local component
    local current=""
    local -a components

    [[ -n "${relative}" && "${relative}" != /* ]] ||
        die "invalid EFI directory: ${relative}"
    IFS="/" read -r -a components <<<"${relative}"
    for component in "${components[@]}"; do
        [[ -n "${component}" && "${component}" != "." && "${component}" != ".." ]] ||
            die "invalid EFI directory: ${relative}"
        current="${current}/${component}"
        if ! mdir -i "${fat}" "::${current}" >/dev/null 2>&1; then
            mmd -i "${fat}" "::${current}"
        fi
    done
}

create_boot_disk()
{
    require_file "${BOOT_DIR}/Image"
    require_file "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}"
    require_file "${BOOT_DIR}/initramfs.cpio.gz"
    require_file "${LOCAL_BUILD_UKI_STUB}"
    require_file "${LOCAL_BUILD_MISC_IMAGE}"
    validate_local_build_file_under_dir "boot disk" "${LOCAL_BUILD_BOOT_DISK}" "${BOOT_DIR}"
    validate_local_build_file_under_dir "slot A UKI" "${LOCAL_BUILD_UKI_A}" "${BOOT_DIR}"
    validate_local_build_file_under_dir "slot B UKI" "${LOCAL_BUILD_UKI_B}" "${BOOT_DIR}"

    resolve_local_ukify
    build_local_uki A "${LOCAL_BUILD_UKI_A}" "${LOCAL_BUILD_BOOTARGS}"
    build_local_uki B "${LOCAL_BUILD_UKI_B}" "${LOCAL_BUILD_BOOTARGS}"

    write_file_if_changed "${LOCAL_BUILD_SLOT_METADATA_A}" <<'EOF'
slot=A
EOF
    write_file_if_changed "${LOCAL_BUILD_SLOT_METADATA_B}" <<'EOF'
slot=B
EOF
    rm -f "${BOOT_DIR}/boot.cmd" "${BOOT_DIR}/boot.scr"

    local fat="${BOOT_DIR}/boot-fat.img"
    local disk="${LOCAL_BUILD_BOOT_DISK}"
    local marker="${disk}.manifest"
    local manifest
    manifest="$(boot_disk_manifest)"
    if [[ "${APOLLO_BOOT_DISK_REFRESH:-0}" != "1" ]] &&
        [[ -f "${fat}" ]] &&
        [[ -f "${disk}" ]] &&
        [[ -f "${marker}" ]] &&
        [[ "$(cat "${marker}")" == "${manifest}" ]]; then
        log "${MACHINE} boot disk is up to date"
        return 0
    fi

    rm -f "${fat}" "${disk}"
    truncate -s 256M "${fat}"
    mkfs.vfat "${fat}" >/dev/null
    ensure_fat_dir "${fat}" "${AUTO_AD_NEXIOS_SLOT_DIR_A}"
    ensure_fat_dir "${fat}" "${AUTO_AD_NEXIOS_SLOT_DIR_B}"
    mcopy -i "${fat}" "${LOCAL_BUILD_UKI_A}" \
        "::/${AUTO_AD_NEXIOS_SLOT_DIR_A}/${AUTO_AD_NEXIOS_UKI_A}"
    mcopy -i "${fat}" "${LOCAL_BUILD_UKI_B}" \
        "::/${AUTO_AD_NEXIOS_SLOT_DIR_B}/${AUTO_AD_NEXIOS_UKI_B}"
    mcopy -i "${fat}" "${LOCAL_BUILD_SLOT_METADATA_A}" \
        "::/${AUTO_AD_NEXIOS_SLOT_DIR_A}/${AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME}"
    mcopy -i "${fat}" "${LOCAL_BUILD_SLOT_METADATA_B}" \
        "::/${AUTO_AD_NEXIOS_SLOT_DIR_B}/${AUTO_AD_NEXIOS_SLOT_METADATA_FILENAME}"

    truncate -s 300M "${disk}"
    local misc_start_sector=$((2048 + 256 * 1024 * 1024 / 512))
    sgdisk --clear --set-alignment=1 \
        --new=1:2048:+256M \
        --typecode=1:ef00 \
        --change-name=1:boot \
        --new=2:"${misc_start_sector}":+4M \
        --typecode=2:8300 \
        --change-name=2:misc \
        "${disk}" >/dev/null
    dd if="${fat}" of="${disk}" bs=512 seek=2048 conv=notrunc status=none
    dd if="${LOCAL_BUILD_MISC_IMAGE}" of="${disk}" bs=512 \
        seek="${misc_start_sector}" conv=notrunc status=none
    printf '%s\n' "${manifest}" > "${marker}"
}

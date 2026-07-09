#!/usr/bin/env bash

# shellcheck disable=SC2154

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
        "${BOOT_DIR}/boot.scr"
}

create_boot_disk()
{
    require_file "${BOOT_DIR}/Image"
    require_file "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}"
    require_file "${BOOT_DIR}/initramfs.cpio.gz"
    validate_local_build_file_under_dir "boot disk" "${LOCAL_BUILD_BOOT_DISK}" "${BOOT_DIR}"

    write_file_if_changed "${BOOT_DIR}/boot.cmd" <<EOF
setenv kernel_addr_r 0x80080000
setenv fdt_addr_r 0x8fc00000
setenv ramdisk_addr_r 0x94000000
setenv bootargs "${LOCAL_BUILD_BOOTARGS}"
load virtio 0:1 \${kernel_addr_r} Image
load virtio 0:1 \${fdt_addr_r} ${LOCAL_BUILD_DTB_BASENAME}
load virtio 0:1 \${ramdisk_addr_r} initramfs.cpio.gz
setenv initrd_size \${filesize}
echo "Booting ${MACHINE} local Linux"
booti \${kernel_addr_r} \${ramdisk_addr_r}:\${initrd_size} \${fdt_addr_r}
EOF
    if [[ ! -f "${BOOT_DIR}/boot.scr" ]] || [[ "${BOOT_DIR}/boot.cmd" -nt "${BOOT_DIR}/boot.scr" ]]; then
        run_logged boot-script mkimage -A arm64 -T script -C none \
            -n "${MACHINE} local boot" \
            -d "${BOOT_DIR}/boot.cmd" "${BOOT_DIR}/boot.scr"
    else
        log "U-Boot boot script is up to date"
    fi

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
    mcopy -i "${fat}" "${BOOT_DIR}/Image" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/${LOCAL_BUILD_DTB_BASENAME}" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/initramfs.cpio.gz" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/boot.scr" ::/

    truncate -s 300M "${disk}"
    sgdisk --clear --set-alignment=1 \
        --new=1:2048:+256M \
        --typecode=1:ef00 \
        --change-name=1:boot \
        "${disk}" >/dev/null
    dd if="${fat}" of="${disk}" bs=512 seek=2048 conv=notrunc status=none
    printf '%s\n' "${manifest}" > "${marker}"
}

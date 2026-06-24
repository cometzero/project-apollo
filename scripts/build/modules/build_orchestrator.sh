#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

build_all()
{
    mkdir -p "${WORK_DIR}" "${DEPLOY_DIR}" "${FW_DIR}" "${BOOT_DIR}" "${LOG_DIR}"
    run_step build-tfm build_tfm
    run_step build-scp build_scp
    run_step build-zephyr build_zephyr
    run_step build-u-boot build_uboot
    run_step build-optee build_optee
    run_step build-tfa build_tfa
    run_step build-linux build_linux
    run_step build-buildroot-initramfs build_buildroot_initramfs
    run_step package-flash-images package_flash_images
    run_step create-boot-disk create_boot_disk
    run_step create-fvpconf create_fvpconf
    run_step generate-debug-manifest generate_debug_manifest
}

clean()
{
    rm -rf "${LOCAL_BUILD_DIR}"
}

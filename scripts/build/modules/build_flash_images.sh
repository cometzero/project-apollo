#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

normalize_image_version()
{
    local version="$1"

    version="${version%%+git*}"
    version="${version%%+AUTOINC*}"
    version="${version%%-*}"

    if [[ "${version}" =~ ^[0-9]+(\.[0-9]+){0,2}(\+[0-9]+)?$ ]]; then
        printf '%s\n' "${version}"
        return
    fi

    if [[ "${version}" =~ ^([0-9]+)(\.([0-9]+))?(\.([0-9]+))? ]]; then
        printf '%s\n' "${BASH_REMATCH[0]}"
        return
    fi

    printf '0.0.7\n'
}

pv_version()
{
    local name="$1"
    local f="${YOCTO_TMP}/work/apollo_fvp-poky-linux/firmware-apollo-fvp/1.0/recipe-sysroot/pv_tracker/${name}.pv"
    if [[ -f "${f}" ]]; then
        normalize_image_version "$(tr -d '\n' < "${f}")"
    else
        printf '0.0.7\n'
    fi
}

firmware_recipe_workdir()
{
    first_existing_glob "${YOCTO_TMP}/work/apollo_fvp-poky-linux/firmware-apollo-fvp/*"
}

sign_host_image()
{
    local input="$1"
    local load_addr="$2"
    local sign_size="$3"
    local version="$4"
    local output="$5"
    require_file "${input}"

    local fw_work
    fw_work="$(firmware_recipe_workdir)"
    local native_sysroot="${fw_work}/recipe-sysroot-native"
    local wrapper="${native_sysroot}/usr/lib/tfm-scripts/wrapper/wrapper.py"
    local python="${native_sysroot}/usr/bin/python3-native/python3"
    local key="${native_sysroot}/usr/share/tfm/root-EC-P256.pem"
    require_file "${wrapper}"
    require_file "${python}"
    require_file "${key}"
    require_file "${FW_DIR}/enc_key_s.b64"

    mkdir -p "${SIGN_DIR}/layouts" "$(dirname "${output}")"
    local layout
    layout="${SIGN_DIR}/layouts/$(basename -s .bin "${input}")_ns"
    cat > "${layout}" <<EOF
enum image_attributes {
    RE_IMAGE_LOAD_ADDRESS = ${load_addr},
    RE_SIGN_BIN_SIZE = ${sign_size},
};
EOF

    OPENSSL_MODULES="${native_sysroot}/usr/lib/ossl-modules" \
    LD_LIBRARY_PATH="${native_sysroot}/usr/lib:${LD_LIBRARY_PATH:-}" \
    CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 \
        run_logged "sign-$(basename "${output}")" "${python}" "${wrapper}" \
        -v "${version}" \
        -s 1 \
        --layout "${layout}" \
        -k "${key}" \
        --public-key-format full \
        --align 1 \
        --pad \
        --pad-header \
        --measured-boot-record \
        -H 0x400 \
        -L 128 \
        -d "(1,0.0.0+0)" \
        -E "${FW_DIR}/enc_key_s.b64" \
        "${input}" \
        "${output}"
}

create_init_fwu_metadata()
{
    local script="${ROOT_DIR}/arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/init_fwu_metadata.py"
    require_file "${script}"
    run_logged init-fwu-metadata python3 "${script}" \
        --binary "${FW_DIR}/init_fwu_metadata.bin" \
        --nr_image "${NR_IMAGES_PER_FWU_BANK}" \
        --image_type_uuids \
        "${TFM_BL2_IMAGE_GUID}" \
        "${TFM_RUNTIME_IMAGE_GUID}" \
        "${SCP_FIRMWARE_IMAGE_GUID}" \
        "${AP_FIP_IMAGE_GUID}" \
        "${SAFETY_ISLAND_CL1_IMAGE_GUID}"
}

raw_image()
{
    local image="$1"
    local size="$2"
    mkdir -p "$(dirname "${image}")"
    rm -f "${image}"
    truncate -s "${size}" "${image}"
}

create_rse_otp_image()
{
    local image="$1"
    local size="$2"
    local host_provision="${RSE_OTP_HOST_PROVISION:-1}"

    case "${host_provision}" in
        0|false|FALSE|no|NO|off|OFF)
            raw_image "${image}" "${size}"
            return
            ;;
    esac

    local tfm_work
    tfm_work="$(tfm_recipe_workdir)"
    local native_python="${tfm_work}/recipe-sysroot-native/usr/bin/python3-native/python3"
    local tfm_common_scripts="${TFM_SRC}/platform/ext/target/arm/rse/common/scripts"
    local native_site
    native_site="$(first_existing_glob "${tfm_work}/recipe-sysroot-native/usr/lib/python*/site-packages" || true)"
    require_file "${native_python}"
    require_dir "${tfm_common_scripts}"
    [[ -n "${native_site}" ]] || \
        die "could not find TF-M native Python site-packages under ${tfm_work}"

    local had_pythonpath=0
    [[ -v PYTHONPATH ]] && had_pythonpath=1
    local saved_pythonpath="${PYTHONPATH:-}"
    local status
    PYTHONPATH="${native_site}:${tfm_common_scripts}${PYTHONPATH:+:${PYTHONPATH}}"
    export PYTHONPATH

    set +e
    run_logged rse-otp-host-provision "${native_python}" \
        "${ROOT_DIR}/scripts/setup/provision_rse_otp_image.py" \
        --root "${ROOT_DIR}" \
        --tfm-build-dir "${TFM_BUILD_DIR}" \
        --output "${image}" \
        --size "${size}"
    status="$?"
    set -e

    if [[ "${had_pythonpath}" -eq 1 ]]; then
        PYTHONPATH="${saved_pythonpath}"
        export PYTHONPATH
    else
        unset PYTHONPATH
    fi
    return "${status}"
}

rse_otp_fingerprint()
{
    local files=(
        "${FW_DIR}/combined_provisioning_message.bin"
        "${FW_DIR}/enc_key_s.b64"
        "${FW_DIR}/bl2_signed.bin"
        "${FW_DIR}/tfm_s_signed.bin"
    )
    local file

    for file in "${files[@]}"; do
        require_file "${file}"
    done

    sha256sum "${files[@]}" | sha256sum | awk '{print $1}'
}

ensure_rse_otp_image()
{
    local image="$1"
    local size="$2"
    local reset="${RSE_OTP_RESET:-0}"
    local fingerprint_file="${image}.fingerprint"
    local fingerprint

    fingerprint="$(rse_otp_fingerprint)"

    case "${reset}" in
        1|true|TRUE|yes|YES|on|ON)
            create_rse_otp_image "${image}" "${size}"
            printf '%s\n' "${fingerprint}" > "${fingerprint_file}"
            log "Reset RSE OTP image: ${image}"
            return
            ;;
    esac

    if [[ ! -f "${image}" ]]; then
        create_rse_otp_image "${image}" "${size}"
        printf '%s\n' "${fingerprint}" > "${fingerprint_file}"
        log "Created RSE OTP image: ${image}"
        return
    fi

    local actual
    actual="$(stat -c '%s' "${image}")"
    [[ "${actual}" == "${size}" ]] || \
        die "existing RSE OTP image ${image} is ${actual} bytes, expected ${size}; set RSE_OTP_RESET=1 to recreate it"

    if [[ ! -f "${fingerprint_file}" ]] ||
       [[ "$(cat "${fingerprint_file}")" != "${fingerprint}" ]]; then
        create_rse_otp_image "${image}" "${size}"
        printf '%s\n' "${fingerprint}" > "${fingerprint_file}"
        log "Reset RSE OTP image because TF-M provisioning artifacts changed: ${image}"
        return
    fi

    log "Preserving RSE OTP image: ${image}"
}

gpt_add()
{
    local image="$1"
    local index="$2"
    local name="$3"
    local offset="$4"
    local size="$5"
    local guid="$6"
    local start=$((offset / 512))
    local end=$(((offset + size) / 512 - 1))
    sgdisk --set-alignment=1 \
        --new="${index}:${start}:${end}" \
        --typecode="${index}:${guid}" \
        --change-name="${index}:${name}" \
        "${image}" >/dev/null
}

write_at()
{
    local image="$1"
    local offset="$2"
    local input="$3"
    local max_size="${4:-0}"
    require_file "${input}"
    if (( max_size > 0 )); then
        local actual
        actual="$(stat -c '%s' "${input}")"
        (( actual <= max_size )) || die "${input} is ${actual} bytes, exceeds slot size ${max_size}"
    fi
    dd if="${input}" of="${image}" bs=1 seek="${offset}" conv=notrunc status=none
}

package_flash_manifest()
{
    local si_cl1="$1"
    local fw_work
    fw_work="$(firmware_recipe_workdir)"

    printf 'NR_IMAGES_PER_FWU_BANK=%s\n' "${NR_IMAGES_PER_FWU_BANK}"
    printf 'RSE_OTP_HOST_PROVISION=%s\n' "${RSE_OTP_HOST_PROVISION:-1}"
    printf 'trusted-firmware-a-pv=%s\n' "$(pv_version trusted-firmware-a)"
    printf 'scp-firmware-pv=%s\n' "$(pv_version scp-firmware)"
    printf 'zephyr-demos-cl1-pv=%s\n' "$(pv_version zephyr-demos-cl1)"
    fingerprint_file_hash "${FW_DIR}/bl1_1.bin" package-bl1-1
    fingerprint_file_hash "${FW_DIR}/bl2.bin" package-tfa-bl2
    fingerprint_file_hash "${FW_DIR}/fip.bin" package-fip
    fingerprint_file_hash "${FW_DIR}/bl2_signed.bin" package-tfm-bl2
    fingerprint_file_hash "${FW_DIR}/tfm_s_signed.bin" package-tfm-runtime
    fingerprint_file_hash "${FW_DIR}/si0_ramfw.bin" package-si0
    fingerprint_file_hash "${si_cl1}" package-si-cl1
    fingerprint_file_hash "${FW_DIR}/rom_dma_ics.bin" package-rom-dma-ics
    fingerprint_file_hash "${FW_DIR}/enc_key_s.b64" package-enc-key
    fingerprint_file_hash "${FW_DIR}/combined_provisioning_message.bin" package-provisioning-message
    fingerprint_file_hash "${ROOT_DIR}/scripts/setup/provision_rse_otp_image.py" package-rse-otp-tool
    fingerprint_file_hash "${ROOT_DIR}/arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/init_fwu_metadata.py" package-fwu-metadata-tool
    fingerprint_file_hash "${fw_work}/recipe-sysroot-native/usr/share/tfm/root-EC-P256.pem" package-root-key
}

rse_otp_image_current()
{
    local image="${FW_DIR}/rse-otp-image.img"
    local fingerprint_file="${image}.fingerprint"
    local fingerprint

    [[ -f "${image}" ]] || return 1
    [[ -f "${fingerprint_file}" ]] || return 1
    fingerprint="$(rse_otp_fingerprint)"
    [[ "$(cat "${fingerprint_file}")" == "${fingerprint}" ]]
}

package_flash_outputs_present()
{
    local signed="$1"
    local file

    for file in \
        "${signed}/signed_bl2.bin" \
        "${signed}/fip_with_bl2.bin" \
        "${signed}/signed_si0_ramfw.bin" \
        "${signed}/signed_safety_island_cl1.bin" \
        "${FW_DIR}/init_fwu_metadata.bin" \
        "${FW_DIR}/rse-rom-image.img" \
        "${FW_DIR}/rse-flash-image.img" \
        "${FW_DIR}/ap-flash-image.img"; do
        [[ -f "${file}" ]] || return 1
    done
    rse_otp_image_current
}

package_flash_images()
{
    mkdir -p "${FW_DIR}" "${BOOT_DIR}"
    local signed="${SIGN_DIR}/deploy"
    mkdir -p "${signed}"

    local si_cl1="${SAFETY_ISLAND_CL1_BIN:-${FW_DIR}/zephyr-demos-cl1.bin}"
    if [[ ! -f "${si_cl1}" && -z "${SAFETY_ISLAND_CL1_BIN:-}" ]]; then
        si_cl1="${YOCTO_DEPLOY_DIR}/zephyr-demos-cl1.bin"
    fi
    require_file "${si_cl1}"

    local package_marker="${FW_DIR}/.apollo-flash-images.manifest"
    local package_manifest
    package_manifest="$(package_flash_manifest "${si_cl1}")"
    if [[ "${APOLLO_FLASH_IMAGES_REFRESH:-0}" != "1" ]] &&
        [[ "${RSE_OTP_RESET:-0}" != "1" ]] &&
        [[ -f "${package_marker}" ]] &&
        [[ "$(cat "${package_marker}")" == "${package_manifest}" ]] &&
        package_flash_outputs_present "${signed}"; then
        log "Apollo flash images are up to date"
        return 0
    fi

    sign_host_image "${FW_DIR}/bl2.bin" 0x70001c00 0x80000 \
        "$(pv_version trusted-firmware-a)" "${signed}/signed_bl2.bin"
    cp "${FW_DIR}/fip.bin" "${signed}/fip_with_bl2.bin"
    run_logged fip-update fiptool update --tb-fw "${signed}/signed_bl2.bin" "${signed}/fip_with_bl2.bin"

    sign_host_image "${FW_DIR}/si0_ramfw.bin" 0x70083C00 0x100000 \
        "$(pv_version scp-firmware)" "${signed}/signed_si0_ramfw.bin"

    sign_host_image "${si_cl1}" 0x70185C00 0x100000 \
        "$(pv_version zephyr-demos-cl1)" "${signed}/signed_safety_island_cl1.bin"

    create_init_fwu_metadata

    local rse_rom="${FW_DIR}/rse-rom-image.img"
    raw_image "${rse_rom}" $((0x1f290))
    write_at "${rse_rom}" $((0x0)) "${FW_DIR}/bl1_1.bin"
    write_at "${rse_rom}" $((0x1f000)) "${FW_DIR}/rom_dma_ics.bin" $((0x400))

    ensure_rse_otp_image "${FW_DIR}/rse-otp-image.img" $((0x10000))

    local rse_flash="${FW_DIR}/rse-flash-image.img"
    raw_image "${rse_flash}" $((0x4cd000))
    sgdisk --clear --set-alignment=1 "${rse_flash}" >/dev/null
    gpt_add "${rse_flash}" 1 reserved_1 0x4400 0x0c00 8300
    gpt_add "${rse_flash}" 2 private_metadata_replica_1 0x5000 0x1000 "${PRIVATE_METADATA_GUID}"
    gpt_add "${rse_flash}" 3 private_metadata_replica_2 0x6000 0x1000 "${PRIVATE_METADATA_GUID}"
    gpt_add "${rse_flash}" 4 tfm_bl2_primary 0x7000 0x20000 "${TFM_BL2_IMAGE_GUID}"
    gpt_add "${rse_flash}" 5 tfm_s_primary 0x27000 0x40000 "${TFM_RUNTIME_IMAGE_GUID}"
    gpt_add "${rse_flash}" 6 si_cl0_primary 0x67000 0x100000 "${SCP_FIRMWARE_IMAGE_GUID}"
    gpt_add "${rse_flash}" 7 si_cl1_primary 0x167000 0x100000 "${SAFETY_ISLAND_CL1_IMAGE_GUID}"
    gpt_add "${rse_flash}" 8 tfm_bl2_secondary 0x267000 0x20000 "${TFM_BL2_IMAGE_GUID}"
    gpt_add "${rse_flash}" 9 tfm_s_secondary 0x287000 0x40000 "${TFM_RUNTIME_IMAGE_GUID}"
    gpt_add "${rse_flash}" 10 si_cl0_secondary 0x2c7000 0x100000 "${SCP_FIRMWARE_IMAGE_GUID}"
    gpt_add "${rse_flash}" 11 si_cl1_secondary 0x3c7000 0x100000 "${SAFETY_ISLAND_CL1_IMAGE_GUID}"
    gpt_add "${rse_flash}" 12 reserved_2 0x4c7000 0x1000 8300
    write_at "${rse_flash}" $((0x7000)) "${FW_DIR}/bl2_signed.bin" $((0x20000))
    write_at "${rse_flash}" $((0x27000)) "${FW_DIR}/tfm_s_signed.bin" $((0x40000))
    write_at "${rse_flash}" $((0x67000)) "${signed}/signed_si0_ramfw.bin" $((0x100000))
    write_at "${rse_flash}" $((0x167000)) "${signed}/signed_safety_island_cl1.bin" $((0x100000))
    write_at "${rse_flash}" $((0x267000)) "${FW_DIR}/bl2_signed.bin" $((0x20000))
    write_at "${rse_flash}" $((0x287000)) "${FW_DIR}/tfm_s_signed.bin" $((0x40000))
    write_at "${rse_flash}" $((0x2c7000)) "${signed}/signed_si0_ramfw.bin" $((0x100000))
    write_at "${rse_flash}" $((0x3c7000)) "${signed}/signed_safety_island_cl1.bin" $((0x100000))

    local ap_flash="${FW_DIR}/ap-flash-image.img"
    local fip_a_size
    fip_a_size="$(stat -c '%s' "${signed}/fip_with_bl2.bin")"
    fip_a_size=$(( ((fip_a_size + 511) / 512) * 512 ))
    raw_image "${ap_flash}" $((0x48d000))
    sgdisk --clear --set-alignment=1 "${ap_flash}" >/dev/null
    gpt_add "${ap_flash}" 1 reserved_1 0x4400 0x0c00 8300
    gpt_add "${ap_flash}" 2 FWU-Metadata 0x5000 0x0200 "${FWU_METADATA_GUID}"
    gpt_add "${ap_flash}" 3 Bkup-FWU-Metadata 0x6000 0x0200 "${FWU_METADATA_GUID}"
    gpt_add "${ap_flash}" 4 FIP_A 0x7000 "${fip_a_size}" "${AP_FIP_IMAGE_GUID}"
    gpt_add "${ap_flash}" 5 FIP_B 0x247000 0x240000 "${AP_FIP_IMAGE_GUID}"
    gpt_add "${ap_flash}" 6 reserved_2 0x487000 0x1000 8300
    write_at "${ap_flash}" $((0x5000)) "${FW_DIR}/init_fwu_metadata.bin" $((0x0200))
    write_at "${ap_flash}" $((0x6000)) "${FW_DIR}/init_fwu_metadata.bin" $((0x0200))
    write_at "${ap_flash}" $((0x7000)) "${signed}/fip_with_bl2.bin" "${fip_a_size}"
    write_at "${ap_flash}" $((0x247000)) "${signed}/fip_with_bl2.bin" $((0x240000))
    printf '%s\n' "${package_manifest}" > "${package_marker}"
}

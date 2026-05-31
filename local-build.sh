#!/usr/bin/env bash
#
# Build Apollo FVP firmware and Linux locally, using the Yocto SDK only as the
# cross-toolchain/provider of native helper tools.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MACHINE="${MACHINE:-apollo-fvp}"
VARIANT="${RD_ASPEN_VARIANT:-cfg2}"
JOBS="${JOBS:-$(nproc)}"

YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
YOCTO_TMP="${YOCTO_TMP:-${YOCTO_BUILD_DIR}/tmp_baremetal}"
YOCTO_DEPLOY_DIR="${YOCTO_DEPLOY_DIR:-${YOCTO_TMP}/deploy/images/${MACHINE}}"

SDK_DIR="${SDK_DIR:-${YOCTO_BUILD_DIR}/local-sdk}"
LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${YOCTO_BUILD_DIR}/local-${MACHINE}}"
WORK_DIR="${LOCAL_BUILD_DIR}/work"
DEPLOY_DIR="${LOCAL_BUILD_DIR}/deploy"
LOG_DIR="${LOCAL_BUILD_DIR}/logs"

TFM_SRC="${TFM_SRC:-${ROOT_DIR}/hsoc-apollo/components/system_mgmt/trusted-firmware-m}"
SCP_SRC="${SCP_SRC:-${ROOT_DIR}/hsoc-apollo/components/system_mgmt/scp-firmware}"
TFA_SRC="${TFA_SRC:-${ROOT_DIR}/hsoc-apollo/components/primary_compute/trusted-firmware-a}"
OPTEE_SRC="${OPTEE_SRC:-${ROOT_DIR}/hsoc-apollo/components/primary_compute/optee-os}"
UBOOT_SRC="${UBOOT_SRC:-${ROOT_DIR}/hsoc-apollo/components/primary_compute/u-boot}"
LINUX_SRC="${LINUX_SRC:-${ROOT_DIR}/hsoc-apollo/components/primary_compute/linux}"
BUILDROOT_SRC="${BUILDROOT_SRC:-${ROOT_DIR}/hsoc-apollo/components/primary_compute/buildroot}"
PFDI_MISC_SRC="${PFDI_MISC_SRC:-${ROOT_DIR}/sw-ref-stack/components/primary_compute/linux_drivers/pfdi_misc_mod/src}"

AARCH64_PREFIX="${AARCH64_PREFIX:-aarch64-poky-linux-}"
ARM_NONE_EABI_PREFIX="${ARM_NONE_EABI_PREFIX:-arm-none-eabi-}"
AARCH64_NONE_ELF_PREFIX="${AARCH64_NONE_ELF_PREFIX:-aarch64-none-elf-}"

PC_CPUS_COUNT="${PC_CPUS_COUNT:-4}"
NR_IMAGES_PER_FWU_BANK="${NR_IMAGES_PER_FWU_BANK:-5}"
PFDI_SUPPORT="${PFDI_SUPPORT:-1}"
PFDI_MONITOR_SUPPORT="${PFDI_MONITOR_SUPPORT:-1}"
KERNEL_MODULES_AUTOLOAD="${KERNEL_MODULES_AUTOLOAD:-openvswitch pfdi_misc}"

TFM_BUILD_DIR="${WORK_DIR}/trusted-firmware-m"
SCP_BUILD_DIR="${WORK_DIR}/scp-firmware"
UBOOT_BUILD_DIR="${WORK_DIR}/u-boot"
OPTEE_BUILD_DIR="${WORK_DIR}/optee-os"
TFA_BUILD_DIR="${WORK_DIR}/trusted-firmware-a"
LINUX_BUILD_DIR="${WORK_DIR}/linux"
BUILDROOT_BUILD_DIR="${WORK_DIR}/buildroot"
BUILDROOT_EXTERNAL="${WORK_DIR}/buildroot-external"
BUILDROOT_OVERLAY="${WORK_DIR}/buildroot-overlay"
BUILDROOT_TOOLCHAIN_DIR="${WORK_DIR}/buildroot-toolchain"
BUILDROOT_TOOLCHAIN_SYSROOT="${BUILDROOT_TOOLCHAIN_DIR}/sysroot"
PFDI_MISC_BUILD_DIR="${WORK_DIR}/pfdi-misc-mod"
SIGN_DIR="${WORK_DIR}/signing"
FW_DIR="${DEPLOY_DIR}/firmware"
BOOT_DIR="${DEPLOY_DIR}/boot"

FVP_TIMEOUT="${FVP_TIMEOUT:-900}"

TFM_BL2_IMAGE_GUID="4b312051-850a-5b17-a3cf-2995baa4bed4"
TFM_RUNTIME_IMAGE_GUID="b181e748-c362-55e6-852c-662d1544f414"
SCP_FIRMWARE_IMAGE_GUID="771ceff3-f186-5d56-80cb-15a2a06dfe81"
AP_FIP_IMAGE_GUID="5d904717-0904-53cd-b240-df7c91ef4918"
SAFETY_ISLAND_CL1_IMAGE_GUID="46083fc9-3d43-5766-a583-ae8e0a199a85"
PRIVATE_METADATA_GUID="07cf7b93-3ce2-52cc-af43-5b0f8690ba73"
FWU_METADATA_GUID="8a7a84a0-8387-40f6-ab41-a8b9a5a60d23"

log()
{
    printf '[%(%Y-%m-%d %H:%M:%S)T] %s\n' -1 "$*"
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

usage()
{
    cat <<'EOF'
Usage: ./local-build.sh [command]

Commands:
  all       Build/install SDK if needed, build local images, and boot FVP.
  sdk       Build and install the Yocto SDK under build/local-sdk.
  build     Build local TF-M/SCP/OP-TEE/U-Boot/TF-A/Linux/Buildroot images.
  boot      Boot the latest local images on apollo-fvp and validate logs.
  clean     Remove build/local-apollo-fvp.

Useful overrides:
  SDK_DIR=/path/to/sdk LOCAL_BUILD_DIR=/path/to/output JOBS=16 ./local-build.sh all
  SAFETY_ISLAND_CL1_BIN=/path/to/zephyr-demos-cl1.bin ./local-build.sh build
  KERNEL_MODULES_AUTOLOAD="openvswitch pfdi_misc" ./local-build.sh build
EOF
}

run_logged()
{
    local name="$1"
    shift
    mkdir -p "${LOG_DIR}"
    log "Running ${name}; log: ${LOG_DIR}/${name}.log"
    "$@" 2>&1 | tee "${LOG_DIR}/${name}.log"
}

require_file()
{
    [[ -f "$1" ]] || die "missing required file: $1"
}

require_dir()
{
    [[ -d "$1" ]] || die "missing required directory: $1"
}

require_command()
{
    command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

path_prepend()
{
    [[ -d "$1" ]] || return 0
    case ":${PATH}:" in
        *:"$1":*) ;;
        *) PATH="$1:${PATH}" ;;
    esac
}

first_existing_glob()
{
    local pattern="$1"
    local item
    shopt -s nullglob
    for item in ${pattern}; do
        printf '%s\n' "${item}"
        shopt -u nullglob
        return 0
    done
    shopt -u nullglob
    return 1
}

find_first_file()
{
    local root="$1"
    local name="$2"
    [[ -d "${root}" ]] || return 1
    find "${root}" -name "${name}" -type f -print -quit
}

install_artifact()
{
    local src="$1"
    local dst="$2"
    require_file "${src}"
    install -D -m 0644 "${src}" "${dst}"
}

build_sdk()
{
    mkdir -p "${LOG_DIR}"

    if first_existing_glob "${SDK_DIR}/environment-setup-*" >/dev/null; then
        log "Yocto SDK already installed at ${SDK_DIR}"
        return 0
    fi

    local installer
    installer="$(find "${YOCTO_TMP}/deploy/sdk" -maxdepth 1 -type f -name '*.sh' 2>/dev/null | sort | tail -n 1 || true)"
    if [[ -z "${installer}" ]]; then
        log "Creating Yocto SDK with bitbake baremetal-image -c populate_sdk"
        (
            cd "${ROOT_DIR}"
            # shellcheck disable=SC1091
            source layers/poky/oe-init-build-env build >/dev/null
            bitbake baremetal-image -c populate_sdk
        ) 2>&1 | tee "${LOG_DIR}/yocto-populate-sdk.log"
        installer="$(find "${YOCTO_TMP}/deploy/sdk" -maxdepth 1 -type f -name '*.sh' | sort | tail -n 1)"
    fi

    require_file "${installer}"
    log "Installing Yocto SDK: ${installer} -> ${SDK_DIR}"
    sh "${installer}" -y -d "${SDK_DIR}" 2>&1 | tee "${LOG_DIR}/yocto-sdk-install.log"
}

source_sdk()
{
    local env_file
    env_file="$(first_existing_glob "${SDK_DIR}/environment-setup-*" || true)"
    if [[ -z "${env_file}" ]]; then
        build_sdk
        env_file="$(first_existing_glob "${SDK_DIR}/environment-setup-*" || true)"
    fi
    require_file "${env_file}"

    log "Sourcing SDK environment: ${env_file}"
    set +u
    # shellcheck disable=SC1090
    source "${env_file}"
    set -u

    AARCH64_PREFIX="${TARGET_PREFIX:-${AARCH64_PREFIX}}"
    SDK_NATIVE_SYSROOT="${OECORE_NATIVE_SYSROOT:-}"
    SDK_TARGET_SYSROOT="${SDKTARGETSYSROOT:-}"

    # Component build systems receive explicit cross prefixes. Yocto SDK flags
    # are useful for recipes but can pollute bare-metal CMake projects.
    unset ARCH CROSS_COMPILE
    unset CC CXX CPP LD AR AS STRIP OBJCOPY OBJDUMP READELF NM RANLIB
    unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS

    require_command "${AARCH64_PREFIX}gcc"
}

add_yocto_native_paths()
{
    local native="${YOCTO_TMP}/sysroots-components/x86_64"
    path_prepend "${native}/python3-native/usr/bin"
    path_prepend "${native}/fiptool-native/usr/bin"
    path_prepend "${native}/cot-dt2c-native/usr/bin"

    local arm_none
    arm_none="$(find_first_file "${native}/gcc-arm-none-eabi-native" "arm-none-eabi-gcc" || true)"
    [[ -n "${arm_none}" ]] && path_prepend "$(dirname "${arm_none}")"

    local aarch64_none
    aarch64_none="$(find_first_file "${native}/gcc-aarch64-none-elf-native" "aarch64-none-elf-gcc" || true)"
    [[ -n "${aarch64_none}" ]] && path_prepend "$(dirname "${aarch64_none}")"
}

setup_build_environment()
{
    source_sdk
    add_yocto_native_paths

    require_command cmake
    require_command ninja
    require_command make
    require_command git
    require_command python3
    require_command openssl
    require_command fiptool
    require_command mkimage
    require_command cpio
    require_command gzip
    require_command depmod
    require_command sgdisk
    require_command mkfs.vfat
    require_command mcopy
    require_command "${ARM_NONE_EABI_PREFIX}gcc"
    require_command "${AARCH64_NONE_ELF_PREFIX}gcc"
}

build_tfm()
{
    require_dir "${TFM_SRC}"
    mkdir -p "${TFM_BUILD_DIR}/externalsrc-keys" "${FW_DIR}"
    local tfm_work
    tfm_work="$(tfm_recipe_workdir)"
    local tfm_deps
    tfm_deps="$(tfm_dependency_root)"
    local cmake_bin
    cmake_bin="$(command -v cmake)"
    local saved_path="${PATH}"
    local tfm_native_bin="${tfm_work}/recipe-sysroot-native/usr/bin"

    install -m 0600 "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.prv" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.prv"
    install -m 0644 "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk.pub" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.pub"
    install -m 0600 "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.prv" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.prv"
    install -m 0644 "${TFM_SRC}/bl1/bl1_2/bl1_dummy_rotpk_1.pub" \
        "${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.pub"

    run_logged tfm-configure "${cmake_bin}" \
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
        -DTFM_BL1_2_CM_SIGNING_KEY_PATH="${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk.pub" \
        -DTFM_BL1_2_DM_SIGNING_KEY_PATH="${TFM_BUILD_DIR}/externalsrc-keys/bl1_dummy_rotpk_1.pub"

    PATH="${tfm_native_bin}:${saved_path}"
    run_logged tfm-build "${cmake_bin}" --build "${TFM_BUILD_DIR}" --target install --parallel "${JOBS}"
    PATH="${saved_path}"

    install_artifact "${TFM_BUILD_DIR}/bin/bl1_1.bin" "${FW_DIR}/bl1_1.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/bl2_signed.bin" "${FW_DIR}/bl2_signed.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/tfm_s_signed.bin" "${FW_DIR}/tfm_s_signed.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/rom_dma_ics.bin" "${FW_DIR}/rom_dma_ics.bin"
    install_artifact "${TFM_BUILD_DIR}/bin/enc_key_s.b64" "${FW_DIR}/enc_key_s.b64"
    install_artifact "${TFM_BUILD_DIR}/bin/provisioning/combined_provisioning_message.bin" \
        "${FW_DIR}/combined_provisioning_message.bin"
}

build_scp()
{
    require_dir "${SCP_SRC}"
    local toolchain="${SCP_SRC}/product/automotive-rd/apollo-fvp/si0_ramfw/Toolchain-GNU.cmake"
    require_file "${toolchain}"

    run_logged scp-configure cmake \
        -S "${SCP_SRC}" \
        -B "${SCP_BUILD_DIR}" \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_TOOLCHAIN_FILE="${toolchain}" \
        -DCMAKE_C_COMPILER="$(command -v "${AARCH64_NONE_ELF_PREFIX}gcc")" \
        -DCMAKE_ASM_COMPILER="$(command -v "${AARCH64_NONE_ELF_PREFIX}gcc")" \
        -DSCP_TOOLCHAIN:STRING=GNU \
        -DSCP_FIRMWARE_SOURCE_DIR:PATH=automotive-rd/apollo-fvp/si0_ramfw \
        -DSCP_ENABLE_DEBUGGER=1 \
        -DSCP_ENABLE_SCMI_PFDI_MONITOR="${PFDI_MONITOR_SUPPORT}" \
        -DSCP_PC_CONFIGURED_CORES_COUNT="${PC_CPUS_COUNT}" \
        -DSCP_PFDI_ONLINE_TIMEOUT_US=100000UL \
        -DSCP_SICL1_PFDI_ONLINE_TIMEOUT_US=60000UL \
        -DSCP_PLATFORM_VARIANT=fvp \
        -DSCP_RD_ASPEN_VARIANT_CFG1=0 \
        -DSCP_APOLLO_FVP_VARIANT_CFG1=0

    run_logged scp-build cmake --build "${SCP_BUILD_DIR}" --parallel "${JOBS}"

    local scp_bin
    scp_bin="$(find "${SCP_BUILD_DIR}" \
        \( -path '*/bin/si0_ramfw.bin' -o -path '*/bin/apollo-fvp-si0-bl2.bin' \) \
        -print -quit)"
    require_file "${scp_bin}"
    install_artifact "${scp_bin}" "${FW_DIR}/si0_ramfw.bin"
}

build_uboot()
{
    require_dir "${UBOOT_SRC}"
    local key="${ROOT_DIR}/arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/u-boot/files/fvp-rd-aspen/capsule_dev_priv_key.pem"
    require_file "${key}"
    mkdir -p "${UBOOT_BUILD_DIR}" "${DEPLOY_DIR}/u-boot"

    install -m 0600 "${key}" "${UBOOT_BUILD_DIR}/CRT.key"
    run_logged u-boot-capsule-cert openssl req -new -x509 \
        -key "${UBOOT_BUILD_DIR}/CRT.key" \
        -out "${UBOOT_BUILD_DIR}/CRT.crt" \
        -days 365 \
        -subj /CN=CRT/

    run_logged u-boot-defconfig make -C "${UBOOT_SRC}" \
        O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
        apollo_fvp_defconfig

    local crt_rel
    crt_rel="$(realpath --relative-to="${UBOOT_SRC}" "${UBOOT_BUILD_DIR}/CRT.crt")"
    "${UBOOT_SRC}/scripts/config" --file "${UBOOT_BUILD_DIR}/.config" \
        --set-str EFI_CAPSULE_CRT_FILE "${crt_rel}"
    run_logged u-boot-olddefconfig make -C "${UBOOT_SRC}" \
        O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
        olddefconfig

    run_logged u-boot-build make -C "${UBOOT_SRC}" \
        O="${UBOOT_BUILD_DIR}" ARCH=arm CROSS_COMPILE="${AARCH64_PREFIX}" \
        RD_ASPEN_VARIANT="${VARIANT}" -j "${JOBS}"

    install_artifact "${UBOOT_BUILD_DIR}/u-boot.bin" "${DEPLOY_DIR}/u-boot/u-boot.bin"
}

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

build_tfa()
{
    require_dir "${TFA_SRC}"
    require_file "${DEPLOY_DIR}/u-boot/u-boot.bin"
    require_file "${DEPLOY_DIR}/optee/tee-pager_v2.bin"
    mkdir -p "${TFA_BUILD_DIR}" "${DEPLOY_DIR}/tf-a"

    local tfa_work
    tfa_work="$(tfa_recipe_workdir)"
    local saved_path="${PATH}"
    local had_pythonpath=0
    [[ -v PYTHONPATH ]] && had_pythonpath=1
    local saved_pythonpath="${PYTHONPATH:-}"
    path_prepend "${tfa_work}/recipe-sysroot-native/usr/bin"
    PYTHONPATH="${tfa_work}/recipe-sysroot-native/usr/lib/python3.13/site-packages${PYTHONPATH:+:${PYTHONPATH}}"
    export PYTHONPATH

    run_logged tfa-build make -C "${TFA_SRC}" -j1 \
        LD="${AARCH64_PREFIX}ld" \
        CC="${AARCH64_PREFIX}gcc" \
        BUILD_BASE="${TFA_BUILD_DIR}" \
        PLAT=apollo_fvp \
        SPD=spmd \
        SPMD_SPM_AT_SEL2=0 \
        DEBUG=1 \
        MBEDTLS_DIR=mbedtls \
        BL33="${DEPLOY_DIR}/u-boot/u-boot.bin" \
        BL32="${DEPLOY_DIR}/optee/tee-pager_v2.bin" \
        HOSTCC=gcc \
        host-poetry= \
        PLATFORM_CORE_COUNT="${PC_CPUS_COUNT}" \
        LINUX_DTS=0 \
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
        bl2 fip

    PATH="${saved_path}"
    if [[ "${had_pythonpath}" -eq 1 ]]; then
        PYTHONPATH="${saved_pythonpath}"
        export PYTHONPATH
    else
        unset PYTHONPATH
    fi
    install_artifact "${TFA_BUILD_DIR}/apollo_fvp/debug/bl2.bin" "${FW_DIR}/bl2.bin"
    install_artifact "${TFA_BUILD_DIR}/apollo_fvp/debug/fip.bin" "${FW_DIR}/fip.bin"
}

find_linux_config()
{
    if [[ -n "${LINUX_CONFIG:-}" ]]; then
        printf '%s\n' "${LINUX_CONFIG}"
        return 0
    fi
    find "${YOCTO_TMP}/work/apollo_fvp-poky-linux/linux-yocto-rt" \
        -path '*/build/.config' -type f -print -quit 2>/dev/null
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

tfa_recipe_workdir()
{
    local root
    root="$(first_existing_glob "${YOCTO_TMP}/work/apollo_fvp-poky-linux/trusted-firmware-a"/* || true)"
    [[ -n "${root}" ]] || die "could not find TF-A Yocto workdir under ${YOCTO_TMP}"
    printf '%s\n' "${root}"
}

build_linux()
{
    require_dir "${LINUX_SRC}"
    mkdir -p "${LINUX_BUILD_DIR}" "${BOOT_DIR}"

    local config
    config="$(find_linux_config || true)"
    require_file "${config}"
    install -m 0644 "${config}" "${LINUX_BUILD_DIR}/.config"

    local modsign_key
    modsign_key="$(find "${YOCTO_TMP}/work/apollo_fvp-poky-linux/linux-yocto-rt" \
        -path '*/build/modsign_key.pem' -type f -print -quit 2>/dev/null || true)"
    if [[ -n "${modsign_key}" ]]; then
        install -m 0600 "${modsign_key}" "${LINUX_BUILD_DIR}/modsign_key.pem"
    elif grep -q '^CONFIG_MODULE_SIG_KEY="modsign_key.pem"' "${LINUX_BUILD_DIR}/.config"; then
        require_file "${LINUX_SRC}/certs/x509.genkey"
        openssl req -new -nodes -utf8 -sha256 -days 36500 -batch -x509 \
            -config "${LINUX_SRC}/certs/x509.genkey" \
            -outform PEM -out "${LINUX_BUILD_DIR}/modsign_key.pem" \
            -keyout "${LINUX_BUILD_DIR}/modsign_key.pem"
        chmod 0600 "${LINUX_BUILD_DIR}/modsign_key.pem"
    fi

    run_logged linux-olddefconfig make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        olddefconfig
    run_logged linux-build make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        Image dtbs modules -j "${JOBS}"

    local image="${LINUX_BUILD_DIR}/arch/arm64/boot/Image"
    local dtb="${LINUX_BUILD_DIR}/arch/arm64/boot/dts/arm/apollo-fvp.dtb"
    require_file "${image}"
    require_file "${dtb}"
    install_artifact "${image}" "${BOOT_DIR}/Image"
    install_artifact "${dtb}" "${BOOT_DIR}/apollo-fvp.dtb"
}

prepare_buildroot_toolchain()
{
    [[ -n "${SDK_NATIVE_SYSROOT:-}" ]] ||
        die "OECORE_NATIVE_SYSROOT is not set; source the Yocto SDK first"
    [[ -n "${SDK_TARGET_SYSROOT:-}" ]] ||
        die "SDKTARGETSYSROOT is not set; source the Yocto SDK first"

    local tuple="${AARCH64_PREFIX%-}"
    local real_bin="${SDK_NATIVE_SYSROOT}/usr/bin/${tuple}"
    require_dir "${real_bin}"

    rm -rf "${BUILDROOT_TOOLCHAIN_DIR}"
    mkdir -p "${BUILDROOT_TOOLCHAIN_DIR}/bin" "${BUILDROOT_TOOLCHAIN_SYSROOT}"
    cp -al "${SDK_TARGET_SYSROOT}/." "${BUILDROOT_TOOLCHAIN_SYSROOT}/"
    rm -f "${BUILDROOT_TOOLCHAIN_SYSROOT}/etc/ld.so.conf"
    rm -rf "${BUILDROOT_TOOLCHAIN_SYSROOT}/etc/ld.so.conf.d"
    rm -f "${BUILDROOT_TOOLCHAIN_SYSROOT}/usr/bin/sudo"

    # The Yocto SDK used here ships dynamic glibc development files but omits
    # libc.a. Buildroot's external-toolchain sysroot detection still keys off
    # `gcc -print-file-name=libc.a`, so provide an empty archive marker in the
    # generated Buildroot-only sysroot without changing the SDK contents.
    local libc_a="${BUILDROOT_TOOLCHAIN_SYSROOT}/usr/lib/libc.a"
    if [[ ! -e "${libc_a}" ]]; then
        mkdir -p "$(dirname "${libc_a}")"
        "${AARCH64_PREFIX}ar" rcs "${libc_a}"
    fi

    local src
    local name
    shopt -s nullglob
    for src in "${real_bin}/${AARCH64_PREFIX}"*; do
        name="$(basename "${src}")"
        case "${name}" in
            "${AARCH64_PREFIX}gcc"|\
            "${AARCH64_PREFIX}g++"|\
            "${AARCH64_PREFIX}c++"|\
            "${AARCH64_PREFIX}cpp")
                continue
                ;;
        esac
        ln -sf "${src}" "${BUILDROOT_TOOLCHAIN_DIR}/bin/${name}"
    done
    shopt -u nullglob

    local tool
    local real
    for tool in gcc g++ c++ cpp; do
        real="${real_bin}/${AARCH64_PREFIX}${tool}"
        [[ -x "${real}" ]] || continue
        rm -f "${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}${tool}"
        {
            printf '#!/usr/bin/env bash\n'
            printf 'exec %q --sysroot=%q "$@"\n' "${real}" "${BUILDROOT_TOOLCHAIN_SYSROOT}"
        } > "${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}${tool}"
        chmod +x "${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}${tool}"
    done

    require_file "${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}gcc"
}

buildroot_env()
{
    env \
        -u CONFIG_SITE \
        -u PKG_CONFIG_PATH \
        -u PKG_CONFIG_SYSROOT_DIR \
        -u PKG_CONFIG_LIBDIR \
        -u PERL5LIB \
        -u PERL_LOCAL_LIB_ROOT \
        -u PERL_MB_OPT \
        -u PERL_MM_OPT \
        PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}" \
        "$@"
}

prepare_buildroot_overlay()
{
    rm -rf "${BUILDROOT_OVERLAY}"
    mkdir -p "${BUILDROOT_OVERLAY}"/{dev,proc,sys,tmp,run,etc/modules-load.d}
    chmod 1777 "${BUILDROOT_OVERLAY}/tmp"

    local module
    for module in ${KERNEL_MODULES_AUTOLOAD}; do
        printf '%s\n' "${module}"
    done > "${BUILDROOT_OVERLAY}/etc/modules-load.d/apollo-fvp.conf"

    cat > "${BUILDROOT_OVERLAY}/init" <<'EOF'
#!/bin/sh
mount -t devtmpfs devtmpfs /dev 2>/dev/null || mount -t tmpfs devtmpfs /dev
if [ -e /dev/console ]; then
    exec </dev/console >/dev/console 2>&1
fi
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t tmpfs tmpfs /run 2>/dev/null || true

echo "Apollo FVP local Buildroot initramfs"
echo "local-initramfs: booted"
cat /proc/cmdline

load_modules()
{
    local conf
    local module
    local args

    for conf in /etc/modules-load.d/*.conf /usr/lib/modules-load.d/*.conf; do
        [ -e "${conf}" ] || continue
        while read -r module args; do
            case "${module}" in
                ""|\#*) continue ;;
            esac
            echo "local-initramfs: modprobe ${module}"
            modprobe "${module}" ${args} ||
                echo "local-initramfs: modprobe ${module} failed"
        done < "${conf}"
    done
}

load_modules
lsmod 2>/dev/null || true

echo "apollo-fvp login:"
exec /bin/sh -i
EOF
    chmod 0755 "${BUILDROOT_OVERLAY}/init"
}

prepare_buildroot_external()
{
    rm -rf "${BUILDROOT_EXTERNAL}"
    mkdir -p "${BUILDROOT_EXTERNAL}"

    cat > "${BUILDROOT_EXTERNAL}/external.desc" <<'EOF'
name: APOLLO_FVP
desc: Apollo FVP local Buildroot customizations
EOF

    cat > "${BUILDROOT_EXTERNAL}/Config.in" <<'EOF'
# Apollo FVP does not currently add Buildroot packages.
EOF

    cat > "${BUILDROOT_EXTERNAL}/external.mk" <<'EOF'
define APOLLO_FVP_REMOVE_LDCONF
	rm -f $(TARGET_DIR)/etc/ld.so.conf
	rm -rf $(TARGET_DIR)/etc/ld.so.conf.d
endef
TARGET_FINALIZE_HOOKS += APOLLO_FVP_REMOVE_LDCONF
EOF
}

write_buildroot_defconfig()
{
    mkdir -p "${BUILDROOT_BUILD_DIR}"
    local tuple="${AARCH64_PREFIX%-}"
    local defconfig="${BUILDROOT_BUILD_DIR}/apollo-fvp-buildroot_defconfig"
    local headers_major
    local headers_patchlevel
    headers_major="$(sed -n 's/^#define LINUX_VERSION_MAJOR //p' \
        "${SDK_TARGET_SYSROOT}/usr/include/linux/version.h")"
    headers_patchlevel="$(sed -n 's/^#define LINUX_VERSION_PATCHLEVEL //p' \
        "${SDK_TARGET_SYSROOT}/usr/include/linux/version.h")"
    [[ -n "${headers_major}" && -n "${headers_patchlevel}" ]] ||
        die "could not read SDK kernel headers version"

    cat > "${defconfig}" <<EOF
BR2_aarch64=y
BR2_cortex_a720=y
BR2_TOOLCHAIN_EXTERNAL=y
BR2_TOOLCHAIN_EXTERNAL_CUSTOM=y
BR2_TOOLCHAIN_EXTERNAL_PREINSTALLED=y
BR2_TOOLCHAIN_EXTERNAL_PATH="${BUILDROOT_TOOLCHAIN_DIR}"
BR2_TOOLCHAIN_EXTERNAL_CUSTOM_PREFIX="${tuple}"
BR2_TOOLCHAIN_EXTERNAL_GCC_14=y
BR2_TOOLCHAIN_EXTERNAL_HEADERS_${headers_major}_${headers_patchlevel}=y
BR2_TOOLCHAIN_EXTERNAL_CUSTOM_GLIBC=y
BR2_TOOLCHAIN_EXTERNAL_CXX=y
BR2_TOOLCHAIN_EXTERNAL_HAS_SSP=y
BR2_TOOLCHAIN_EXTERNAL_HAS_SSP_STRONG=y
# BR2_TOOLCHAIN_EXTERNAL_INET_RPC is not set
BR2_TARGET_GENERIC_HOSTNAME="apollo-fvp"
BR2_TARGET_GENERIC_ISSUE="Apollo FVP Buildroot"
BR2_INIT_NONE=y
BR2_SYSTEM_BIN_SH_BUSYBOX=y
BR2_ROOTFS_DEVICE_CREATION_DYNAMIC_DEVTMPFS=y
BR2_ROOTFS_OVERLAY="${BUILDROOT_OVERLAY}"
BR2_PACKAGE_BUSYBOX=y
BR2_PACKAGE_BUSYBOX_SHOW_OTHERS=y
BR2_PACKAGE_KMOD=y
BR2_PACKAGE_KMOD_TOOLS=y
BR2_TARGET_ROOTFS_CPIO=y
BR2_TARGET_ROOTFS_CPIO_GZIP=y
# BR2_TARGET_ROOTFS_TAR is not set
# BR2_LINUX_KERNEL is not set
EOF
    printf '%s\n' "${defconfig}"
}

kernel_release()
{
    make -s -C "${LINUX_SRC}" O="${LINUX_BUILD_DIR}" \
        ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" kernelrelease
}

kernel_module_sig_hash()
{
    sed -n 's/^CONFIG_MODULE_SIG_HASH="\(.*\)"$/\1/p' "${LINUX_BUILD_DIR}/.config"
}

sign_kernel_module()
{
    local module="$1"
    local hash
    hash="$(kernel_module_sig_hash)"
    [[ -n "${hash}" ]] || hash="sha256"

    local sign_file="${LINUX_BUILD_DIR}/scripts/sign-file"
    local key="${LINUX_BUILD_DIR}/modsign_key.pem"
    local cert="${LINUX_BUILD_DIR}/certs/signing_key.x509"
    require_file "${sign_file}"
    require_file "${key}"
    require_file "${cert}"
    require_file "${module}"

    run_logged "sign-$(basename "${module}")" \
        "${sign_file}" "${hash}" "${key}" "${cert}" "${module}"
}

build_pfdi_misc_module()
{
    local release="$1"
    require_dir "${PFDI_MISC_SRC}"

    rm -rf "${PFDI_MISC_BUILD_DIR}"
    mkdir -p "${PFDI_MISC_BUILD_DIR}"
    cp -a "${PFDI_MISC_SRC}/." "${PFDI_MISC_BUILD_DIR}/"

    run_logged pfdi-misc-build make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        M="${PFDI_MISC_BUILD_DIR}" modules

    sign_kernel_module "${PFDI_MISC_BUILD_DIR}/pfdi_misc.ko"

    install_artifact "${PFDI_MISC_BUILD_DIR}/pfdi_misc.ko" \
        "${BUILDROOT_OVERLAY}/lib/modules/${release}/updates/pfdi_misc.ko"
}

install_kernel_modules_overlay()
{
    local release
    release="$(kernel_release)"
    [[ -n "${release}" ]] || die "could not determine kernel release"

    rm -rf "${BUILDROOT_OVERLAY}/lib/modules/${release}"
    run_logged linux-modules-install make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        INSTALL_MOD_PATH="${BUILDROOT_OVERLAY}" modules_install

    if [[ " ${KERNEL_MODULES_AUTOLOAD} " == *" pfdi_misc "* ]]; then
        build_pfdi_misc_module "${release}"
    fi

    run_logged linux-depmod depmod -b "${BUILDROOT_OVERLAY}" "${release}"
    find "${BUILDROOT_OVERLAY}/lib/modules/${release}" \
        \( -name build -o -name source \) -type l -delete
}

build_buildroot_initramfs()
{
    require_dir "${BUILDROOT_SRC}"
    mkdir -p "${BUILDROOT_BUILD_DIR}" "${BOOT_DIR}"

    prepare_buildroot_toolchain
    prepare_buildroot_external
    prepare_buildroot_overlay
    install_kernel_modules_overlay

    local defconfig
    defconfig="$(write_buildroot_defconfig)"
    run_logged buildroot-defconfig buildroot_env make -C "${BUILDROOT_SRC}" \
        O="${BUILDROOT_BUILD_DIR}" BR2_EXTERNAL="${BUILDROOT_EXTERNAL}" \
        BR2_DEFCONFIG="${defconfig}" defconfig
    rm -rf "${BUILDROOT_BUILD_DIR}/build/toolchain" \
        "${BUILDROOT_BUILD_DIR}/build/toolchain-external" \
        "${BUILDROOT_BUILD_DIR}/build/toolchain-external-custom"
    rm -f "${BUILDROOT_BUILD_DIR}/target/etc/ld.so.conf"
    rm -rf "${BUILDROOT_BUILD_DIR}/target/etc/ld.so.conf.d"
    run_logged buildroot-build buildroot_env make -C "${BUILDROOT_SRC}" \
        O="${BUILDROOT_BUILD_DIR}" BR2_EXTERNAL="${BUILDROOT_EXTERNAL}" \
        -j "${JOBS}"

    require_file "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz"
    install_artifact "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz" \
        "${BOOT_DIR}/initramfs.cpio.gz"
}

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

    export OPENSSL_MODULES="${native_sysroot}/usr/lib/ossl-modules"
    export LD_LIBRARY_PATH="${native_sysroot}/usr/lib:${LD_LIBRARY_PATH:-}"
    export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1

    mkdir -p "${SIGN_DIR}/layouts" "$(dirname "${output}")"
    local layout="${SIGN_DIR}/layouts/$(basename -s .bin "${input}")_ns"
    cat > "${layout}" <<EOF
enum image_attributes {
    RE_IMAGE_LOAD_ADDRESS = ${load_addr},
    RE_SIGN_BIN_SIZE = ${sign_size},
};
EOF

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

package_flash_images()
{
    mkdir -p "${FW_DIR}" "${BOOT_DIR}"
    local signed="${SIGN_DIR}/deploy"
    mkdir -p "${signed}"

    sign_host_image "${FW_DIR}/bl2.bin" 0x70001c00 0x80000 \
        "$(pv_version trusted-firmware-a)" "${signed}/signed_bl2.bin"
    cp "${FW_DIR}/fip.bin" "${signed}/fip_with_bl2.bin"
    run_logged fip-update fiptool update --tb-fw "${signed}/signed_bl2.bin" "${signed}/fip_with_bl2.bin"

    sign_host_image "${FW_DIR}/si0_ramfw.bin" 0x70083C00 0x100000 \
        "$(pv_version scp-firmware)" "${signed}/signed_si0_ramfw.bin"

    local si_cl1="${SAFETY_ISLAND_CL1_BIN:-${YOCTO_DEPLOY_DIR}/zephyr-demos-cl1.bin}"
    require_file "${si_cl1}"
    sign_host_image "${si_cl1}" 0x70185C00 0x100000 \
        "$(pv_version zephyr-demos-cl1)" "${signed}/signed_safety_island_cl1.bin"

    create_init_fwu_metadata

    local rse_rom="${FW_DIR}/rse-rom-image.img"
    raw_image "${rse_rom}" $((0x1f290))
    write_at "${rse_rom}" $((0x0)) "${FW_DIR}/bl1_1.bin"
    write_at "${rse_rom}" $((0x1f000)) "${FW_DIR}/rom_dma_ics.bin" $((0x400))

    raw_image "${FW_DIR}/rse-otp-image.img" $((0x10000))

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
}

create_boot_disk()
{
    require_file "${BOOT_DIR}/Image"
    require_file "${BOOT_DIR}/apollo-fvp.dtb"
    require_file "${BOOT_DIR}/initramfs.cpio.gz"

    cat > "${BOOT_DIR}/boot.cmd" <<'EOF'
setenv kernel_addr_r 0x80080000
setenv fdt_addr_r 0x8fc00000
setenv ramdisk_addr_r 0x94000000
setenv bootargs "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 root=/dev/ram0 rw rdinit=/init loglevel=7 cpuidle.governor=menu maxcpus=4 mem=4064M"
load virtio 0:1 ${kernel_addr_r} Image
load virtio 0:1 ${fdt_addr_r} apollo-fvp.dtb
load virtio 0:1 ${ramdisk_addr_r} initramfs.cpio.gz
setenv initrd_size ${filesize}
echo "Booting Apollo FVP local Linux"
booti ${kernel_addr_r} ${ramdisk_addr_r}:${initrd_size} ${fdt_addr_r}
EOF
    run_logged boot-script mkimage -A arm64 -T script -C none \
        -n "Apollo FVP local boot" \
        -d "${BOOT_DIR}/boot.cmd" "${BOOT_DIR}/boot.scr"

    local fat="${BOOT_DIR}/boot-fat.img"
    local disk="${BOOT_DIR}/apollo-fvp-local-disk.img"
    rm -f "${fat}" "${disk}"
    truncate -s 256M "${fat}"
    mkfs.vfat "${fat}" >/dev/null
    mcopy -i "${fat}" "${BOOT_DIR}/Image" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/apollo-fvp.dtb" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/initramfs.cpio.gz" ::/
    mcopy -i "${fat}" "${BOOT_DIR}/boot.scr" ::/

    truncate -s 300M "${disk}"
    sgdisk --clear --set-alignment=1 \
        --new=1:2048:+256M \
        --typecode=1:ef00 \
        --change-name=1:boot \
        "${disk}" >/dev/null
    dd if="${fat}" of="${disk}" bs=512 seek=2048 conv=notrunc status=none
}

create_fvpconf()
{
    local base="${YOCTO_DEPLOY_DIR}/baremetal-image-${MACHINE}.fvpconf"
    require_file "${base}"
    local out="${DEPLOY_DIR}/${MACHINE}-local.fvpconf"
    mkdir -p "${DEPLOY_DIR}"

    python3 - "$base" "$out" "$FW_DIR" "$BOOT_DIR" <<'PY'
import json
import pathlib
import sys

base, out, fw, boot = [pathlib.Path(p) for p in sys.argv[1:]]
cfg = json.loads(base.read_text(encoding="utf-8"))
p = cfg.setdefault("parameters", {})
p["css.smb.rseil.rse.rom.raw_image"] = str(fw / "rse-rom-image.img")
p["css.smb.rseil.rse_flashloader.fname"] = str(fw / "rse-flash-image.img")
p["css.smb.rseil.rse_flashloader.fnameWrite"] = str(fw / "rse-flash-image.img")
p["css.smb.rseil.rse.lcm_nvm.raw_image"] = str(fw / "rse-otp-image.img")
p["ros.flash_loader.fname"] = str(fw / "ap-flash-image.img")
p["ros.flash_loader.fnameWrite"] = str(fw / "ap-flash-image.img")
p["ros.virtio_block0.image_path"] = str(boot / "apollo-fvp-local-disk.img")
cfg["data"] = [f"css.smb.rseil.rse.sram1={fw / 'combined_provisioning_message.bin'}@0x20000"]
out.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

validate_boot_result()
{
    local result="$1"
    python3 - "$result" <<'PY'
import json
import sys

result = json.load(open(sys.argv[1], encoding="utf-8"))
required = ["rse", "safety_island_cl0", "safety_island_cl1", "tf_a", "u_boot_linux"]
missing = [name for name in required if not result.get("domains", {}).get(name, {}).get("passed")]
if missing:
    print("missing boot domains: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)
print("boot domains passed: " + ", ".join(required))
PY
}

boot_fvp()
{
    create_fvpconf
    local fvpconf="${DEPLOY_DIR}/${MACHINE}-local.fvpconf"
    local out_dir="${LOCAL_BUILD_DIR}/fvp-boot"
    rm -rf "${out_dir}"

    run_logged fvp-boot python3 "${ROOT_DIR}/scripts/runfvp_log_boot.py" \
        --machine "${MACHINE}" \
        --fvpconf "${fvpconf}" \
        --out-dir "${out_dir}" \
        --timeout "${FVP_TIMEOUT}" \
        --require all \
        --no-login

    validate_boot_result "${out_dir}/result.json" | tee "${LOG_DIR}/fvp-boot-validate.log"
}

build_all()
{
    mkdir -p "${WORK_DIR}" "${DEPLOY_DIR}" "${FW_DIR}" "${BOOT_DIR}" "${LOG_DIR}"
    build_tfm
    build_scp
    build_uboot
    build_optee
    build_tfa
    build_linux
    build_buildroot_initramfs
    package_flash_images
    create_boot_disk
    create_fvpconf
}

clean()
{
    rm -rf "${LOCAL_BUILD_DIR}"
}

main()
{
    local cmd="${1:-all}"
    case "${cmd}" in
        all)
            build_sdk
            setup_build_environment
            build_all
            boot_fvp
            ;;
        sdk)
            build_sdk
            setup_build_environment
            ;;
        build)
            setup_build_environment
            build_all
            ;;
        boot)
            setup_build_environment
            boot_fvp
            ;;
        clean)
            clean
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            usage >&2
            die "unknown command: ${cmd}"
            ;;
    esac
}

main "$@"

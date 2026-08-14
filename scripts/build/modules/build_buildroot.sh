#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

buildroot_toolchain_manifest()
{
    local tuple="${AARCH64_PREFIX%-}"
    local real_bin="${SDK_NATIVE_SYSROOT}/usr/bin/${tuple}"
    local item

    printf 'SDK_NATIVE_SYSROOT=%s\n' "$(canonical_dir "${SDK_NATIVE_SYSROOT}")"
    printf 'SDK_TARGET_SYSROOT=%s\n' "$(canonical_dir "${SDK_TARGET_SYSROOT}")"
    printf 'AARCH64_PREFIX=%s\n' "${AARCH64_PREFIX}"
    for item in \
        "${real_bin}/${AARCH64_PREFIX}gcc" \
        "${real_bin}/${AARCH64_PREFIX}g++" \
        "${SDK_TARGET_SYSROOT}/usr/include/linux/version.h"; do
        [[ -e "${item}" ]] || continue
        stat -Lc '%n|%s|%Y' "${item}"
    done
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

    local manifest="${BUILDROOT_TOOLCHAIN_DIR}/.apollo-toolchain.manifest"
    local current_manifest
    current_manifest="$(buildroot_toolchain_manifest)"
    BUILDROOT_TOOLCHAIN_REFRESHED=0
    if [[ "${APOLLO_BUILDROOT_TOOLCHAIN_REFRESH:-0}" != "1" ]] &&
        [[ -f "${manifest}" ]] &&
        [[ -x "${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}gcc" ]] &&
        [[ -d "${BUILDROOT_TOOLCHAIN_SYSROOT}" ]] &&
        [[ -e "${BUILDROOT_TOOLCHAIN_SYSROOT}/lib/ld-linux-aarch64.so.1" ]] &&
        [[ "$(cat "${manifest}")" == "${current_manifest}" ]]; then
        log "Buildroot toolchain cache is up to date"
        return 0
    fi

    log "Refreshing Buildroot toolchain cache"
    BUILDROOT_TOOLCHAIN_REFRESHED=1
    rm -rf "${BUILDROOT_TOOLCHAIN_DIR}"
    mkdir -p "${BUILDROOT_TOOLCHAIN_DIR}/bin" "${BUILDROOT_TOOLCHAIN_SYSROOT}"
    cp -al "${SDK_TARGET_SYSROOT}/." "${BUILDROOT_TOOLCHAIN_SYSROOT}/"
    # Yocto recipe sysroots use usrmerge, while Buildroot's external-toolchain
    # validation and library importer expect the dynamic loader below /lib.
    if [[ ! -e "${BUILDROOT_TOOLCHAIN_SYSROOT}/lib" ]]; then
        ln -s usr/lib "${BUILDROOT_TOOLCHAIN_SYSROOT}/lib"
    fi
    rm -f "${BUILDROOT_TOOLCHAIN_SYSROOT}/etc/ld.so.conf"
    rm -rf "${BUILDROOT_TOOLCHAIN_SYSROOT}/etc/ld.so.conf.d"
    rm -f "${BUILDROOT_TOOLCHAIN_SYSROOT}/usr/bin/sudo"
    rm -rf "${BUILDROOT_TOOLCHAIN_SYSROOT}/usr/lib/debug"
    find "${BUILDROOT_TOOLCHAIN_SYSROOT}" -type d -name .debug -prune \
        -exec rm -rf {} +

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
    printf '%s\n' "${current_manifest}" > "${manifest}"
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

resolve_yocto_recipe_source()
{
    local recipe="$1"
    local architecture="$2"
    local source_subdir="$3"
    local source

    source="$(first_existing_glob \
        "${YOCTO_TMP}/work/${architecture}-poky-linux/${recipe}/*/sources-unpack/${source_subdir}" \
        || true)"
    [[ -n "${source}" ]] ||
        die "Yocto source for ${recipe} was not found below ${YOCTO_TMP}/work"
    require_dir "${source}"
    printf '%s\n' "${source}"
}

resolve_buildroot_bsp_sources()
{
    ARM_SI_RPROC_SRC="${ARM_SI_RPROC_SRC:-$(
        resolve_yocto_recipe_source arm-si-rproc-mod \
            "${LOCAL_MACHINE_WORK_PREFIX}" src
    )}"
    RPMSG_NET_SRC="${RPMSG_NET_SRC:-$(
        resolve_yocto_recipe_source rpmsg-net-mod \
            "${LOCAL_MACHINE_WORK_PREFIX}" src
    )}"
    PFDI_MISC_SRC="${PFDI_MISC_SRC:-$(
        resolve_yocto_recipe_source pfdi-misc-mod \
            "${LOCAL_MACHINE_WORK_PREFIX}" src
    )}"
    PFDI_BSP_SRC="${PFDI_BSP_SRC:-$(
        resolve_yocto_recipe_source platform-fault-detection \
            "cortexa720" git
    )}"
}

prepare_pfdi_bsp_config()
{
    local default_pack="${PFDI_BSP_CONFIG_DIR}/pfdi_test_config_0.pack"
    if [[ "${PFDI_BSP_CONFIG_PACK}" != "${default_pack}" ]]; then
        require_file "${PFDI_BSP_CONFIG_PACK}"
        return 0
    fi

    local pfdi_tool_dir="${PFDI_BSP_SRC}/pfdi-demo/pfdi-tool"
    local host_python3
    require_dir "${pfdi_tool_dir}/pfdi_tool"
    host_python3="$(PATH="${HOST_PATH}" command -v python3 || true)"
    [[ -n "${host_python3}" ]] ||
        die "host python3 was not found in the original host PATH"

    rm -rf "${PFDI_BSP_CONFIG_DIR}"
    mkdir -p "${PFDI_BSP_CONFIG_DIR}"
    run_logged pfdi-config-generate env PYTHONPATH="${pfdi_tool_dir}" \
        "${host_python3}" -m pfdi_tool.run generate 0 40 60 1 \
        "${PC_CPUS_COUNT}" \
        "${PFDI_BSP_CONFIG_DIR}"
    run_logged pfdi-config-pack env PYTHONPATH="${pfdi_tool_dir}" \
        "${host_python3}" -m pfdi_tool.run pack "${PFDI_BSP_CONFIG_DIR}"
    require_file "${PFDI_BSP_CONFIG_PACK}"
}

prepare_buildroot_overlay()
{
    require_file "${NEXIOS_BSP_INIT_DIR}/init"
    require_file "${NEXIOS_BSP_INIT_DIR}/nexios-bsp-selftest"
    require_file "${PFDI_BSP_CONFIG_PACK}"

    mkdir -p "${BUILDROOT_OVERLAY}"/{dev,proc,sys,tmp,run,etc}
    mkdir -p "${BUILDROOT_OVERLAY}/etc/pfdi"
    mkdir -p "${BUILDROOT_OVERLAY}/usr/libexec/nexios-bsp"
    rm -f \
        "${BUILDROOT_OVERLAY}/usr/bin/apollo-network-setup" \
        "${BUILDROOT_OVERLAY}/usr/bin/pfdi-local-agent" \
        "${BUILDROOT_BUILD_DIR}/target/usr/bin/apollo-network-setup" \
        "${BUILDROOT_BUILD_DIR}/target/usr/bin/pfdi-local-agent"
    rm -rf "${BUILDROOT_OVERLAY}/etc/modules-load.d"
    rm -rf "${WORK_DIR}/pfdi-local-agent"
    chmod 1777 "${BUILDROOT_OVERLAY}/tmp"

    install -m 0755 "${NEXIOS_BSP_INIT_DIR}/init" \
        "${BUILDROOT_OVERLAY}/init"
    install -m 0755 "${NEXIOS_BSP_INIT_DIR}/nexios-bsp-selftest" \
        "${BUILDROOT_OVERLAY}/usr/libexec/nexios-bsp/selftest"
    install -m 0644 "${PFDI_BSP_CONFIG_PACK}" \
        "${BUILDROOT_OVERLAY}/etc/pfdi/pfdi_test_config_0.pack"
    printf '%s\n' "${MACHINE}" |
        write_file_if_changed "${BUILDROOT_OVERLAY}/etc/nexios-bsp-machine"
    printf '%s\n' "${PC_CPUS_COUNT}" |
        write_file_if_changed "${BUILDROOT_OVERLAY}/etc/nexios-bsp-cpus"
}

prepare_buildroot_external()
{
    require_file "${BUILDROOT_EXTERNAL}/external.desc"
    require_file "${BUILDROOT_EXTERNAL}/Config.in"
    require_file "${BUILDROOT_EXTERNAL}/external.mk"
    require_file \
        "${BUILDROOT_EXTERNAL}/package/apollo-perf/apollo-perf.mk"
    require_file \
        "${BUILDROOT_EXTERNAL}/package/apollo-pfdi-bsp/apollo-pfdi-bsp.mk"
}

write_buildroot_defconfig()
{
    mkdir -p "${BUILDROOT_BUILD_DIR}"
    local tuple="${AARCH64_PREFIX%-}"
    local defconfig="${BUILDROOT_BUILD_DIR}/${MACHINE}-buildroot_defconfig"
    local headers_major
    local headers_patchlevel
    headers_major="$(sed -n 's/^#define LINUX_VERSION_MAJOR //p' \
        "${SDK_TARGET_SYSROOT}/usr/include/linux/version.h")"
    headers_patchlevel="$(sed -n 's/^#define LINUX_VERSION_PATCHLEVEL //p' \
        "${SDK_TARGET_SYSROOT}/usr/include/linux/version.h")"
    [[ -n "${headers_major}" && -n "${headers_patchlevel}" ]] ||
        die "could not read SDK kernel headers version"

    write_file_if_changed "${defconfig}" <<EOF
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
BR2_TOOLCHAIN_EXTERNAL_OPENMP=y
BR2_TOOLCHAIN_EXTERNAL_HAS_SSP=y
BR2_TOOLCHAIN_EXTERNAL_HAS_SSP_STRONG=y
BR2_ENABLE_DEBUG=y
BR2_DEBUG_2=y
# BR2_STRIP_strip is not set
BR2_OPTIMIZE_G=y
# BR2_TOOLCHAIN_EXTERNAL_INET_RPC is not set
BR2_TARGET_GENERIC_HOSTNAME="${MACHINE}"
BR2_TARGET_GENERIC_ISSUE="${MACHINE} Buildroot"
BR2_INIT_NONE=y
BR2_SYSTEM_BIN_SH_BUSYBOX=y
BR2_ROOTFS_DEVICE_CREATION_DYNAMIC_DEVTMPFS=y
BR2_ROOTFS_OVERLAY="${BUILDROOT_OVERLAY}"
BR2_PACKAGE_BUSYBOX=y
BR2_PACKAGE_BUSYBOX_SHOW_OTHERS=y
BR2_PACKAGE_KMOD=y
BR2_PACKAGE_KMOD_TOOLS=y
BR2_PACKAGE_IPROUTE2=y
BR2_PACKAGE_UTIL_LINUX=y
BR2_PACKAGE_UTIL_LINUX_BINARIES=y
BR2_PACKAGE_LIBMNL=y
BR2_PACKAGE_LIBCAP=y
BR2_PACKAGE_ELFUTILS=y
BR2_PACKAGE_ZSTD=y
BR2_PACKAGE_IPERF=y
BR2_PACKAGE_APOLLO_PFDI_BSP=y
BR2_TARGET_ROOTFS_CPIO=y
BR2_TARGET_ROOTFS_CPIO_GZIP=y
# BR2_TARGET_ROOTFS_TAR is not set
BR2_PACKAGE_APOLLO_PERF=y
EOF
    printf '%s\n' "${defconfig}"
}

buildroot_defconfig_digest()
{
    local defconfig="$1"

    {
        sha256sum "${defconfig}"
        fingerprint_tree_metadata "${BUILDROOT_EXTERNAL}" buildroot-external
    } | sha256sum | awk '{print $1}'
}

configure_buildroot_if_needed()
{
    local defconfig="$1"
    local marker="${BUILDROOT_BUILD_DIR}/.apollo-defconfig.sha256"
    local digest
    digest="$(buildroot_defconfig_digest "${defconfig}")"

    if [[ "${APOLLO_BUILDROOT_FORCE_DEFCONFIG:-0}" != "1" ]] &&
        [[ -f "${BUILDROOT_BUILD_DIR}/.config" ]] &&
        [[ -f "${marker}" ]] &&
        [[ "$(cat "${marker}")" == "${digest}" ]]; then
        log "Buildroot defconfig is up to date"
        return 0
    fi

    run_logged buildroot-defconfig buildroot_make \
        BR2_DEFCONFIG="${defconfig}" defconfig
    printf '%s\n' "${digest}" > "${marker}"
}

buildroot_make()
{
    buildroot_env make -C "${BUILDROOT_SRC}" \
        O="${BUILDROOT_BUILD_DIR}" \
        BR2_EXTERNAL="${BUILDROOT_EXTERNAL}" \
        APOLLO_LINUX_SOURCE_DIR="${LINUX_SRC}" \
        APOLLO_PFDI_BSP_SOURCE_DIR="${PFDI_BSP_SRC}" \
        APOLLO_PFDI_BSP_CONFIG_PACK="${PFDI_BSP_CONFIG_PACK}" \
        "$@"
}

validate_buildroot_zena_packages()
{
    local config="${BUILDROOT_BUILD_DIR}/.config"
    require_file "${config}"

    local required=(
        "BR2_PACKAGE_KMOD=y"
        "BR2_PACKAGE_KMOD_TOOLS=y"
        "BR2_PACKAGE_IPROUTE2=y"
        "BR2_PACKAGE_UTIL_LINUX=y"
        "BR2_PACKAGE_APOLLO_PERF=y"
        "BR2_PACKAGE_APOLLO_PFDI_BSP=y"
        "BR2_PACKAGE_LIBMNL=y"
        "BR2_PACKAGE_LIBCAP=y"
        "BR2_PACKAGE_ELFUTILS=y"
        "BR2_PACKAGE_ZSTD=y"
        "BR2_PACKAGE_IPERF=y"
    )

    local symbol
    for symbol in "${required[@]}"; do
        grep -qxF "${symbol}" "${config}" ||
            die "Buildroot is missing required Arm Zena CSS package: ${symbol}"
    done

    log "Validated Buildroot Arm Zena CSS package selection"
}

buildroot_perf_source_manifest()
{
    local -a source_paths=(
        COPYING
        Makefile
        arch/arm64/include
        include
        scripts
        tools/arch
        tools/build
        tools/include
        tools/lib
        tools/perf
        tools/scripts
    )

    require_dir "${LINUX_SRC}/tools/perf"
    require_file "${LINUX_SRC}/COPYING"
    printf 'LINUX_SRC=%s\n' "$(canonical_dir "${LINUX_SRC}")"

    if git -C "${LINUX_SRC}" rev-parse --is-inside-work-tree \
        >/dev/null 2>&1; then
        git -C "${LINUX_SRC}" rev-parse HEAD
        git -C "${LINUX_SRC}" diff --no-ext-diff --binary HEAD -- \
            "${source_paths[@]}" |
            sha256sum |
            awk '{print "tracked-diff=" $1}'
        while IFS= read -r -d '' source; do
            fingerprint_file_hash "${LINUX_SRC}/${source}" \
                "untracked/${source}"
        done < <(
            git -C "${LINUX_SRC}" ls-files -z --others \
                --exclude-standard -- "${source_paths[@]}" |
                LC_ALL=C sort -z
        )
    else
        local source
        for source in "${source_paths[@]}"; do
            if [[ -d "${LINUX_SRC}/${source}" ]]; then
                fingerprint_tree_metadata "${LINUX_SRC}/${source}" \
                    "linux/${source}"
            else
                fingerprint_file_hash "${LINUX_SRC}/${source}" \
                    "linux/${source}"
            fi
        done
    fi
}

refresh_buildroot_perf_source()
{
    local marker="${BUILDROOT_BUILD_DIR}/.apollo-perf-source.manifest"
    local manifest

    mkdir -p "${BUILDROOT_BUILD_DIR}"
    manifest="$(buildroot_perf_source_manifest)"
    if [[ -f "${marker}" ]] &&
        [[ "$(cat "${marker}")" == "${manifest}" ]]; then
        log "Buildroot perf source is up to date"
        return 0
    fi

    run_logged buildroot-perf-dirclean buildroot_make apollo-perf-dirclean
    printf '%s\n' "${manifest}" > "${marker}"
}

validate_buildroot_runtime_files()
{
    require_file "${BUILDROOT_BUILD_DIR}/target/sbin/ip"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/bin/iperf"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/bin/perf"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/bin/pfdi-cli"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/bin/pfdi-sample-app"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/lib/libpfdi.so.1.0"
    require_file \
        "${BUILDROOT_BUILD_DIR}/target/etc/pfdi/pfdi_test_config_0.pack"
    require_file "${BUILDROOT_BUILD_DIR}/target/usr/libexec/nexios-bsp/selftest"

    local lib
    for lib in libmnl.so.0 libcap.so.2 libelf.so.1 libzstd.so.1; do
        find "${BUILDROOT_BUILD_DIR}/target" -name "${lib}" -print -quit |
            grep -q . ||
            die "Buildroot target is missing runtime dependency: ${lib}"
    done

    log "Validated Buildroot Arm Zena CSS runtime files"
}

buildroot_cross_prefix()
{
    local prefix="${BUILDROOT_TOOLCHAIN_DIR}/bin/${AARCH64_PREFIX}"

    if [[ -x "${prefix}gcc" ]]; then
        printf '%s\n' "${prefix}"
    else
        printf '%s\n' "${AARCH64_PREFIX}"
    fi
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

build_external_kernel_module()
{
    local name="$1"
    local src="$2"
    local build_dir="$3"
    local module="$4"
    local release="$5"
    local installed_module="${BUILDROOT_OVERLAY}/lib/modules/${release}/updates/${module}.ko"
    local cross_prefix
    cross_prefix="$(buildroot_cross_prefix)"
    require_dir "${src}"
    require_command "${cross_prefix}strip"

    rm -rf "${build_dir}"
    mkdir -p "${build_dir}"
    cp -a "${src}/." "${build_dir}/"

    run_logged "${name}-build" make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${cross_prefix}" \
        M="${build_dir}" modules

    install_artifact "${build_dir}/${module}.ko" \
        "${installed_module}"
    run_logged "strip-${module}.ko" "${cross_prefix}strip" \
        --strip-debug "${installed_module}"
    sign_kernel_module "${installed_module}"
}

build_arm_si_rproc_module()
{
    build_external_kernel_module arm-si-rproc "${ARM_SI_RPROC_SRC}" \
        "${ARM_SI_RPROC_BUILD_DIR}" arm_si_rproc "$1"
}

build_rpmsg_net_module()
{
    build_external_kernel_module rpmsg-net "${RPMSG_NET_SRC}" \
        "${RPMSG_NET_BUILD_DIR}" rpmsg_net "$1"
}

build_pfdi_misc_module()
{
    build_external_kernel_module pfdi-misc "${PFDI_MISC_SRC}" \
        "${PFDI_MISC_BUILD_DIR}" pfdi_misc "$1"
}

validate_zena_kernel_modules_overlay()
{
    local release="$1"
    local module

    for module in arm_si_rproc rpmsg_net pfdi_misc; do
        if [[ " ${KERNEL_MODULES_AUTOLOAD} " == *" ${module} "* ]]; then
            require_file "${BUILDROOT_OVERLAY}/lib/modules/${release}/updates/${module}.ko"
        fi
    done

    log "Validated Buildroot overlay Arm Zena CSS kernel modules"
}

kernel_modules_overlay_manifest()
{
    local release="$1"

    printf 'release=%s\n' "${release}"
    printf 'KERNEL_MODULES_AUTOLOAD=%s\n' "${KERNEL_MODULES_AUTOLOAD}"
    printf 'PFDI_MONITOR_SUPPORT=%s\n' "${PFDI_MONITOR_SUPPORT}"
    printf 'INSTALL_MOD_STRIP=1\n'
    fingerprint_file_hash "${LINUX_BUILD_DIR}/.config" linux-config
    fingerprint_file_hash "${LINUX_BUILD_DIR}/Module.symvers" linux-module-symvers
    fingerprint_file_hash "${LINUX_BUILD_DIR}/modules.order" linux-modules-order
    fingerprint_file_hash "${LINUX_BUILD_DIR}/modsign_key.pem" linux-modsign-key
    fingerprint_file_hash "${LINUX_BUILD_DIR}/certs/signing_key.x509" linux-modsign-cert
    fingerprint_tree_metadata "${LINUX_BUILD_DIR}" linux-build |
        grep '\.ko|' || true
    fingerprint_tree_metadata "${ARM_SI_RPROC_SRC}" arm-si-rproc-src
    fingerprint_tree_metadata "${RPMSG_NET_SRC}" rpmsg-net-src
    fingerprint_tree_metadata "${PFDI_MISC_SRC}" pfdi-misc-src
}

install_kernel_modules_overlay()
{
    local release
    release="$(kernel_release)"
    [[ -n "${release}" ]] || die "could not determine kernel release"

    mkdir -p "${BUILDROOT_OVERLAY}/lib/modules"
    find "${BUILDROOT_OVERLAY}/lib/modules" -mindepth 1 -maxdepth 1 \
        ! -name "${release}" -exec rm -rf {} +

    local modules_dir="${BUILDROOT_OVERLAY}/lib/modules/${release}"
    local marker="${modules_dir}/.apollo-modules.manifest"
    local manifest
    manifest="$(kernel_modules_overlay_manifest "${release}")"
    if [[ "${APOLLO_KERNEL_MODULES_REFRESH:-0}" != "1" ]] &&
        [[ -f "${marker}" ]] &&
        [[ "$(cat "${marker}")" == "${manifest}" ]]; then
        validate_zena_kernel_modules_overlay "${release}"
        log "Buildroot kernel module overlay is up to date"
        return 0
    fi

    rm -rf "${BUILDROOT_OVERLAY}/lib/modules/${release}"
    run_logged linux-modules-install make -C "${LINUX_SRC}" \
        O="${LINUX_BUILD_DIR}" ARCH=arm64 CROSS_COMPILE="${AARCH64_PREFIX}" \
        INSTALL_MOD_PATH="${BUILDROOT_OVERLAY}" INSTALL_MOD_STRIP=1 \
        modules_install

    if [[ " ${KERNEL_MODULES_AUTOLOAD} " == *" arm_si_rproc "* ]]; then
        build_arm_si_rproc_module "${release}"
    fi
    if [[ " ${KERNEL_MODULES_AUTOLOAD} " == *" rpmsg_net "* ]]; then
        build_rpmsg_net_module "${release}"
    fi
    if [[ " ${KERNEL_MODULES_AUTOLOAD} " == *" pfdi_misc "* ]]; then
        build_pfdi_misc_module "${release}"
    fi

    run_logged linux-depmod depmod -b "${BUILDROOT_OVERLAY}" "${release}"
    validate_zena_kernel_modules_overlay "${release}"
    find "${BUILDROOT_OVERLAY}/lib/modules/${release}" \
        \( -name build -o -name source \) -type l -delete
    printf '%s\n' "${manifest}" > "${marker}"
}

buildroot_initramfs_manifest()
{
    local release="$1"

    printf 'BUILDROOT_SRC=%s\n' "$(canonical_dir "${BUILDROOT_SRC}")"
    git -C "${BUILDROOT_SRC}" rev-parse HEAD 2>/dev/null || true
    git -C "${BUILDROOT_SRC}" status --porcelain=v1 --untracked-files=no 2>/dev/null || true
    printf 'release=%s\n' "${release}"
    printf 'KERNEL_MODULES_AUTOLOAD=%s\n' "${KERNEL_MODULES_AUTOLOAD}"
    printf 'PFDI_MONITOR_SUPPORT=%s\n' "${PFDI_MONITOR_SUPPORT}"
    fingerprint_file_hash "${BUILDROOT_BUILD_DIR}/.config" buildroot-config
    fingerprint_file_hash "${BUILDROOT_BUILD_DIR}/.apollo-defconfig.sha256" buildroot-defconfig
    fingerprint_file_hash "${BUILDROOT_BUILD_DIR}/.apollo-perf-source.manifest" buildroot-perf-source
    fingerprint_file_hash "${BUILDROOT_TOOLCHAIN_DIR}/.apollo-toolchain.manifest" buildroot-toolchain
    fingerprint_file_hash "${BUILDROOT_OVERLAY}/lib/modules/${release}/.apollo-modules.manifest" kernel-modules-overlay
    fingerprint_tree_metadata "${NEXIOS_BSP_INIT_DIR}" nexios-bsp-init
    fingerprint_tree_metadata "${PFDI_BSP_SRC}" pfdi-bsp-src
    fingerprint_file_hash "${PFDI_BSP_CONFIG_PACK}" pfdi-bsp-config
    fingerprint_tree_metadata "${BUILDROOT_EXTERNAL}" buildroot-external
    find "${BUILDROOT_OVERLAY}" \
        -path "${BUILDROOT_OVERLAY}/lib/modules" -prune -o \
        -type f -printf 'buildroot-overlay/%P|%s|%T@\n' |
        LC_ALL=C sort
}

build_buildroot_initramfs()
{
    local compressor

    require_dir "${BUILDROOT_SRC}"
    require_command pigz
    mkdir -p "${BUILDROOT_BUILD_DIR}" "${BOOT_DIR}"
    compressor="$(buildroot_cpio_compress_cmd)"

    resolve_buildroot_bsp_sources
    prepare_buildroot_toolchain
    prepare_pfdi_bsp_config
    prepare_buildroot_external
    prepare_buildroot_overlay
    install_kernel_modules_overlay

    local defconfig
    defconfig="$(write_buildroot_defconfig)"
    configure_buildroot_if_needed "${defconfig}"
    validate_buildroot_zena_packages
    refresh_buildroot_perf_source

    local release
    release="$(kernel_release)"
    local image_marker="${BUILDROOT_BUILD_DIR}/images/.apollo-initramfs.manifest"
    local image_manifest
    mkdir -p "${BUILDROOT_BUILD_DIR}/images"
    image_manifest="$(buildroot_initramfs_manifest "${release}")"
    if [[ "${APOLLO_BUILDROOT_IMAGE_REFRESH:-0}" != "1" ]] &&
        [[ -f "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz" ]] &&
        [[ -f "${image_marker}" ]] &&
        [[ "$(cat "${image_marker}")" == "${image_manifest}" ]]; then
        validate_buildroot_runtime_files
        install_artifact "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz" \
            "${BOOT_DIR}/initramfs.cpio.gz"
        log "Buildroot initramfs is up to date"
        return 0
    fi

    if [[ "${BUILDROOT_TOOLCHAIN_REFRESHED:-0}" == "1" ]]; then
        rm -rf "${BUILDROOT_BUILD_DIR}/build/toolchain" \
            "${BUILDROOT_BUILD_DIR}/build/toolchain-external" \
            "${BUILDROOT_BUILD_DIR}/build/toolchain-external-custom"
    fi
    rm -f "${BUILDROOT_BUILD_DIR}/target/etc/ld.so.conf"
    rm -rf "${BUILDROOT_BUILD_DIR}/target/etc/ld.so.conf.d"
    rm -rf "${BUILDROOT_BUILD_DIR}/target/lib/modules"
    run_logged buildroot-build buildroot_make \
        ROOTFS_CPIO_COMPRESS_CMD="${compressor}" \
        -j "${JOBS}" ||
        return $?
    validate_buildroot_runtime_files

    require_file "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz"
    install_artifact "${BUILDROOT_BUILD_DIR}/images/rootfs.cpio.gz" \
        "${BOOT_DIR}/initramfs.cpio.gz"
    printf '%s\n' "${image_manifest}" > "${image_marker}"
}

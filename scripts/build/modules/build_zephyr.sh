#!/usr/bin/env bash

# shellcheck disable=SC2154,SC1091

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

reset_zephyr_generated_links()
{
    rm -rf "${ZEPHYR_BUILD_DIR}/zephyr/misc/generated/syscalls_links"
    rm -f "${ZEPHYR_BUILD_DIR}/zephyr/misc/generated/syscalls_subdirs.trigger" \
        "${ZEPHYR_BUILD_DIR}/zephyr/misc/generated/syscalls_subdirs.txt"
}

reset_zephyr_build_if_hsoc_source_changed()
{
    local marker="${ZEPHYR_BUILD_DIR}/.apollo-zephyr-hsoc-src"
    local expected
    local recorded

    expected="$(canonical_dir "${ZEPHYR_HSOC_SRC}")"
    if [[ -f "${marker}" ]]; then
        recorded="$(cat "${marker}")"
    elif [[ -f "${ZEPHYR_BUILD_DIR}/CMakeCache.txt" ]]; then
        recorded=""
    else
        mkdir -p "${ZEPHYR_BUILD_DIR}"
        printf '%s\n' "${expected}" > "${marker}"
        return 0
    fi

    if [[ "${recorded}" != "${expected}" ]]; then
        log "Removing stale Zephyr build directory for ${ZEPHYR_BUILD_DIR}"
        log "  previous HSOC source: ${recorded:-unknown}"
        log "  current HSOC source:  ${expected}"
        rm -rf "${ZEPHYR_BUILD_DIR}"
    fi

    mkdir -p "${ZEPHYR_BUILD_DIR}"
    printf '%s\n' "${expected}" > "${marker}"
}

find_zephyr_sdk_dir()
{
    if [[ -n "${ZEPHYR_SDK_INSTALL_DIR:-}" ]]; then
        require_dir "${ZEPHYR_SDK_INSTALL_DIR}"
        printf '%s\n' "${ZEPHYR_SDK_INSTALL_DIR}"
        return 0
    fi

    local sdk="${YOCTO_TMP}/sysroots-components/x86_64/zephyr-sdk-native/usr/zephyr-sdk"
    if [[ -d "${sdk}" ]]; then
        printf '%s\n' "${sdk}"
        return 0
    fi

    sdk="$(find "${YOCTO_TMP}/work" -path '*/recipe-sysroot-native/usr/zephyr-sdk' \
        -type d -print -quit 2>/dev/null || true)"
    [[ -n "${sdk}" ]] ||
        die "could not find Zephyr SDK; set ZEPHYR_SDK_INSTALL_DIR or build zephyr-demos-cl1 once with Yocto"
    printf '%s\n' "${sdk}"
}

yocto_native_python()
{
    local python="${YOCTO_TMP}/sysroots-components/x86_64/python3-native/usr/bin/python3-native/python3"
    if [[ -x "${python}" ]]; then
        printf '%s\n' "${python}"
        return 0
    fi

    python="$(find "${YOCTO_TMP}/work" -path '*/recipe-sysroot-native/usr/bin/python3-native/python3' \
        -type f -perm -111 -print -quit 2>/dev/null || true)"
    if [[ -n "${python}" ]]; then
        printf '%s\n' "${python}"
        return 0
    fi

    command -v python3
}

yocto_native_pythonpath()
{
    local root="${YOCTO_TMP}/sysroots-components/x86_64"
    [[ -d "${root}" ]] || return 0
    find "${root}" -path '*/usr/lib/python3.13/site-packages' -type d -print |
        paste -sd:
}

bitbake_zephyr_getvar()
{
    local var="$1"

    (
        cd "${ROOT_DIR}" || exit
        clear_sdk_env_for_yocto
        set +u
        source layers/poky/oe-init-build-env build >/dev/null
        set -u
        bitbake -e zephyr-demos-cl1
    ) | sed -n "s/^${var}=\"\\(.*\\)\"$/\\1/p" | tail -n 1
}

zephyr_deps_root_valid()
{
    local root="$1"
    local rel

    [[ -d "${root}" ]] || return 1
    [[ -f "${ZEPHYR_MODULES_LIST}" ]] || return 1

    while IFS= read -r rel; do
        case "${rel}" in
            ""|\#*|arm_zena_safety_island|zephyr_hsoc_src) continue ;;
        esac
        [[ -d "${root}/${rel}" ]] || return 1
    done < "${ZEPHYR_MODULES_LIST}"
}

find_zephyr_yocto_deps_root()
{
    local root
    local candidate

    if [[ -n "${ZEPHYR_DEPS_SRC}" ]]; then
        zephyr_deps_root_valid "${ZEPHYR_DEPS_SRC}" ||
            die "ZEPHYR_DEPS_SRC does not look like a Yocto Zephyr source root: ${ZEPHYR_DEPS_SRC}"
        printf '%s\n' "${ZEPHYR_DEPS_SRC}"
        return 0
    fi

    root="$(bitbake_zephyr_getvar UNPACKDIR 2>/dev/null || true)"
    for candidate in "${root}/git" "${root}"; do
        if [[ -n "${root}" ]] && zephyr_deps_root_valid "${candidate}"; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done

    root="$(bitbake_zephyr_getvar S 2>/dev/null || true)"
    if [[ -n "${root}" ]] && zephyr_deps_root_valid "${root}"; then
        printf '%s\n' "${root}"
        return 0
    fi

    root="$(bitbake_zephyr_getvar WORKDIR 2>/dev/null || true)"
    for candidate in "${root}/sources-unpack/git" "${root}/git"; do
        if [[ -n "${root}" ]] && zephyr_deps_root_valid "${candidate}"; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done

    return 1
}

prepare_yocto_zephyr_deps_root()
{
    local root

    if root="$(find_zephyr_yocto_deps_root)"; then
        printf '%s\n' "${root}"
        return 0
    fi

    log "Preparing Yocto Zephyr dependency sources with bitbake zephyr-demos-cl1 -c unpack"
    (
        cd "${ROOT_DIR}" || exit
        clear_sdk_env_for_yocto
        set +u
        source layers/poky/oe-init-build-env build >/dev/null
        set -u
        prepare_bitbake_extra_args
        bitbake "${BITBAKE_EXTRA_ARGS[@]}" zephyr-demos-cl1 -c unpack
    )

    root="$(find_zephyr_yocto_deps_root)" ||
        die "could not find Yocto Zephyr dependency source root after unpack"
    printf '%s\n' "${root}"
}

find_yocto_native_imgtool()
{
    local root="${YOCTO_TMP}/work/x86_64-linux/python3-imgtool-tfm-native"
    local candidate

    [[ -d "${root}" ]] || return 1
    candidate="$(
        find "${root}" -path '*/scripts/imgtool.py' -type f -print |
            sort |
            tail -n 1
    )"
    if [[ -n "${candidate}" ]]; then
        printf '%s\n' "${candidate}"
    fi
}

zephyr_modules_arg()
{
    local deps_root="$1"
    local modules=()
    local rel
    local module_path

    require_file "${ZEPHYR_MODULES_LIST}"
    while IFS= read -r rel; do
        case "${rel}" in
            ""|\#*) continue ;;
            tools/bsim|tools/bsim/*)
                if [[ ! -d "${deps_root}/${rel}" ]]; then
                    printf 'notice: skipping optional Zephyr BabbleSim module: %s\n' \
                        "${rel}" >&2
                    continue
                fi
                ;;
        esac
        case "${rel}" in
            arm_zena_safety_island) module_path="${ZEPHYR_SAFETY_ISLAND_SRC}" ;;
            zephyr_hsoc_src) module_path="${ZEPHYR_HSOC_SRC}" ;;
            *) module_path="${deps_root}/${rel}" ;;
        esac
        [[ -d "${module_path}" ]] ||
            die "missing Zephyr module directory listed in ${ZEPHYR_MODULES_LIST}: ${rel}"
        modules+=("${module_path}")
    done < "${ZEPHYR_MODULES_LIST}"

    local IFS=";"
    printf '%s\n' "${modules[*]}"
}

validate_zephyr_cl1_features()
{
    local config="${ZEPHYR_BUILD_DIR}/zephyr/.config"
    require_file "${config}"

    local required=(
        "CONFIG_MBOX_MHUV3=y"
        "CONFIG_OPENAMP=y"
        "CONFIG_VETH_RPMSG=y"
        "CONFIG_NETWORKING=y"
        "CONFIG_NET_IPV4=y"
        "CONFIG_NET_ZPERF=y"
        "CONFIG_NET_CONFIG_MY_IPV4_ADDR=\"192.168.1.1\""
        "CONFIG_NET_CONFIG_PEER_IPV4_ADDR=\"192.168.1.2\""
        "CONFIG_PFDI_MODULE=y"
        "CONFIG_PFDI_MGMT=y"
    )

    if [[ "${PFDI_MONITOR_SUPPORT}" == "1" ]]; then
        required+=("CONFIG_PFDI_AGENT=y")
    fi

    local symbol
    for symbol in "${required[@]}"; do
        grep -qxF "${symbol}" "${config}" ||
            die "Safety Island CL1 is missing required Zephyr config: ${symbol}"
    done

    log "Validated Safety Island CL1 HIPC/zperf/PFDI Zephyr config"
}

build_zephyr()
{
    require_dir "${ZEPHYRPROJECT_SRC}"
    require_dir "${ZEPHYRPROJECT_SRC}/zephyr"
    require_dir "${ZEPHYR_SAFETY_ISLAND_SRC}"
    require_dir "${ZEPHYR_HSOC_SRC}"
    reset_cmake_build_if_source_changed "${ZEPHYR_BUILD_DIR}" "${ZEPHYR_SAFETY_ISLAND_SRC}/apps/sample"
    reset_zephyr_build_if_hsoc_source_changed
    mkdir -p "${ZEPHYR_BUILD_DIR}" "${FW_DIR}"

    local board="apollo_fvp_safety_island_c1"
    local zephyr_sdk
    local zephyr_base="${ZEPHYRPROJECT_SRC}/zephyr"
    local zephyr_dir="${zephyr_base}/share/zephyr-package/cmake"
    local zephyr_deps_root
    local imgtool
    local imgtool_args=()
    local python
    local pythonpath
    local modules
    local overlay_config
    local dtc_overlay
    local saved_path="${PATH}"
    local had_pythonpath=0
    [[ -v PYTHONPATH ]] && had_pythonpath=1
    local saved_pythonpath="${PYTHONPATH:-}"
    local had_zephyr_base=0
    [[ -v ZEPHYR_BASE ]] && had_zephyr_base=1
    local saved_zephyr_base="${ZEPHYR_BASE:-}"

    require_file "${zephyr_dir}/ZephyrConfig.cmake"
    zephyr_sdk="$(find_zephyr_sdk_dir)"
    zephyr_deps_root="$(prepare_yocto_zephyr_deps_root)"
    imgtool="${zephyr_deps_root}/bootloader/mcuboot/scripts/imgtool.py"
    if [[ -f "${imgtool}" ]]; then
        imgtool_args=(-DIMGTOOL:FILEPATH="${imgtool}")
    elif imgtool="$(find_yocto_native_imgtool)"; then
        imgtool_args=(-DIMGTOOL:FILEPATH="${imgtool}")
    else
        imgtool_args=(-DIMGTOOL:FILEPATH=IMGTOOL-NOTFOUND)
    fi
    python="$(yocto_native_python)"
    pythonpath="$(yocto_native_pythonpath)"
    modules="$(zephyr_modules_arg "${zephyr_deps_root}")"
    dtc_overlay="${ZEPHYR_HSOC_SRC}/overlays/hipc/${board}.overlay"
    overlay_config="${ZEPHYR_HSOC_SRC}/overlays/hipc/${board}.conf;${ZEPHYR_HSOC_SRC}/overlays/zperf/${board}.conf;${ZEPHYR_HSOC_SRC}/overlays/pfdi/${board}.conf"
    if [[ "${PFDI_MONITOR_SUPPORT}" == "1" ]]; then
        dtc_overlay="${dtc_overlay};${ZEPHYR_HSOC_SRC}/overlays/pfdi_agent/${board}.overlay"
        overlay_config="${overlay_config};${ZEPHYR_HSOC_SRC}/overlays/pfdi_agent/${board}.conf"
    fi

    export ZEPHYR_SDK_INSTALL_DIR="${zephyr_sdk}"
    export ZEPHYR_BASE="${zephyr_base}"
    path_prepend "${zephyr_sdk}/aarch64-zephyr-elf/bin"
    path_prepend "${zephyr_sdk}/sysroots/x86_64-pokysdk-linux/usr/bin"
    if [[ -n "${pythonpath}" ]]; then
        PYTHONPATH="${pythonpath}${PYTHONPATH:+:${PYTHONPATH}}"
        export PYTHONPATH
    fi
    require_command "${AARCH64_ZEPHYR_ELF_PREFIX}gcc"

    local zephyr_configure_cmd=(
        cmake
        -S "${ZEPHYR_SAFETY_ISLAND_SRC}/apps/sample" \
        -B "${ZEPHYR_BUILD_DIR}" \
        -G Ninja \
        -DCMAKE_MAKE_PROGRAM=ninja \
        -DPYTHON_EXECUTABLE:PATH="${python}" \
        -DPython_EXECUTABLE:PATH="${python}" \
        -DPython3_EXECUTABLE:PATH="${python}" \
        -DCMAKE_TOOLCHAIN_FILE= \
        -DZephyr_DIR:PATH="${zephyr_dir}" \
        -DZEPHYR_BASE:PATH="${zephyr_base}" \
        -DBOARD="${board}" \
        -DZEPHYR_TOOLCHAIN_VARIANT=zephyr \
        -DZEPHYR_MODULES="${modules}" \
        -DZEPHYR_EXTRA_MODULES= \
        "${imgtool_args[@]}" \
        -DUSER_CACHE_DIR="${ZEPHYR_BUILD_DIR}/.cache" \
        -DDTC_OVERLAY_FILE="${dtc_overlay}" \
        -DOVERLAY_CONFIG="${overlay_config}" \
        -Wno-dev
    )
    if ! cmake_configure_current zephyr-configure "${ZEPHYR_BUILD_DIR}" \
        "${zephyr_configure_cmd[@]}"; then
        reset_zephyr_generated_links
    fi
    run_cmake_configure_if_needed zephyr-configure "${ZEPHYR_BUILD_DIR}" \
        "${zephyr_configure_cmd[@]}"

    run_logged zephyr-build cmake --build "${ZEPHYR_BUILD_DIR}" --parallel "${JOBS}"
    validate_zephyr_cl1_features

    install_artifact "${ZEPHYR_BUILD_DIR}/zephyr/zephyr.bin" "${FW_DIR}/zephyr-demos-cl1.bin"
    install_artifact "${ZEPHYR_BUILD_DIR}/zephyr/zephyr.elf" "${FW_DIR}/zephyr-demos-cl1.elf"

    PATH="${saved_path}"
    if [[ "${had_pythonpath}" -eq 1 ]]; then
        PYTHONPATH="${saved_pythonpath}"
        export PYTHONPATH
    else
        unset PYTHONPATH
    fi
    if [[ "${had_zephyr_base}" -eq 1 ]]; then
        ZEPHYR_BASE="${saved_zephyr_base}"
        export ZEPHYR_BASE
    else
        unset ZEPHYR_BASE
    fi
}

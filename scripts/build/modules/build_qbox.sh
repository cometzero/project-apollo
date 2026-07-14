#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

build_qbox()
{
    require_dir "${QBOX_CORE_DIR}"
    require_dir "${QBOX_PLATFORM_DIR}"
    mkdir -p "${LOG_DIR}"

    reset_cmake_build_if_source_changed "${QBOX_PLATFORM_BUILD_DIR}" "${QBOX_PLATFORM_DIR}"

    local cmake_ccache_args=()
    local qbox_tool_env=()
    local qbox_cmake_args=()
    local qbox_libqemu_args=()
    local qbox_build_testing
    local qbox_run_unit_tests
    local qbox_use_system_libqemu
    local qbox_libqemu_dir
    local qbox_libqemu_prefix
    local cmake_cmd
    local_build_cmake_ccache_args cmake_ccache_args
    qbox_sdk_native_tool_args qbox_tool_env qbox_cmake_args
    cmake_cmd="$(command -v cmake)" ||
        die "missing required command: cmake"

    qbox_run_unit_tests="${QBOX_RUN_UNIT_TESTS:-0}"
    if [[ "${QBOX_RUN_SYSTEMC_COMPONENT_TESTS:-0}" == 1 ]]; then
        qbox_run_unit_tests=1
    fi

    qbox_build_testing="${QBOX_BUILD_TESTING:-}"
    if [[ -z "${qbox_build_testing}" ]]; then
        if [[ "${qbox_run_unit_tests}" == 1 ]]; then
            qbox_build_testing=ON
        else
            qbox_build_testing=OFF
        fi
    fi

    qbox_libqemu_dir="$(qbox_yocto_libqemu_dir || true)"
    qbox_use_system_libqemu="${QBOX_USE_SYSTEM_LIBQEMU:-auto}"
    case "${qbox_use_system_libqemu}" in
        auto)
            if [[ -n "${qbox_libqemu_dir}" ]]; then
                qbox_use_system_libqemu=ON
            else
                qbox_use_system_libqemu=OFF
            fi
            ;;
        1|ON|on|true|TRUE|yes|YES)
            qbox_use_system_libqemu=ON
            ;;
        0|OFF|off|false|FALSE|no|NO)
            qbox_use_system_libqemu=OFF
            ;;
        *)
            die "QBOX_USE_SYSTEM_LIBQEMU must be auto, ON, or OFF: ${qbox_use_system_libqemu}"
            ;;
    esac

    qbox_libqemu_args=(-DQBOX_USE_SYSTEM_LIBQEMU="${qbox_use_system_libqemu}")
    if [[ "${qbox_use_system_libqemu}" == "ON" ]]; then
        [[ -n "${qbox_libqemu_dir}" ]] ||
            die "QBOX_USE_SYSTEM_LIBQEMU=ON but libqemuConfig.cmake was not found under ${YOCTO_TMP}; build qbox-libqemu-native or set QBOX_LIBQEMU_DIR"
        log "Using Yocto qbox-libqemu-native for QBox: ${qbox_libqemu_dir}"
        qbox_cmake_args=()
        qbox_libqemu_prefix="${qbox_libqemu_dir%/lib/cmake/libqemu}"
        qbox_libqemu_args+=(
            -Dlibqemu_DIR="${qbox_libqemu_dir}"
        )
        if [[ "${qbox_libqemu_prefix}" != "${qbox_libqemu_dir}" ]]; then
            qbox_libqemu_args+=(-DCMAKE_PREFIX_PATH="${qbox_libqemu_prefix}")
        fi
    else
        require_dir "${QBOX_QEMU_DIR}"
        qbox_libqemu_args+=(
            -DQBOX_QEMU_SOURCE_DIR="${QBOX_QEMU_DIR}"
            -DLIBQEMU_GIT="file://${QBOX_QEMU_DIR}"
            -DFETCHCONTENT_SOURCE_DIR_LIBQEMU="${QBOX_QEMU_DIR}"
            -DLIBQEMU_BUILD_ALWAYS="${QBOX_LIBQEMU_BUILD_ALWAYS:-OFF}"
        )
    fi

    run_cmake_configure_if_needed qbox-configure "${QBOX_PLATFORM_BUILD_DIR}" \
        "${cmake_cmd}" \
        -S "${QBOX_PLATFORM_DIR}" \
        -B "${QBOX_PLATFORM_BUILD_DIR}" \
        "${cmake_ccache_args[@]}" \
        -DCMAKE_BUILD_TYPE="${QBOX_CMAKE_BUILD_TYPE:-RelWithDebInfo}" \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_INSTALL_PREFIX="${QBOX_PLATFORM_BUILD_DIR}/install" \
        -DQBOX_CORE_SOURCE_DIR="${QBOX_CORE_DIR}" \
        -DBUILD_TESTING="${qbox_build_testing}" \
        -DENABLE_PYTHON_BINDER="${QBOX_ENABLE_PYTHON_BINDER:-OFF}" \
        -DGS_ENABLE_VIRCLRENDERER="${QBOX_GS_ENABLE_VIRCLRENDERER:-OFF}" \
        -DGS_ENABLE_VIRGLRENDERER="${QBOX_GS_ENABLE_VIRGLRENDERER:-OFF}" \
        "${qbox_libqemu_args[@]}" \
        "${qbox_cmake_args[@]}" \
        -DQBOX_APOLLO_BUILD_TARGET="${QBOX_APOLLO_BUILD_TARGET:-apollo_fvp_full_system}"

    run_logged qbox-build \
        "${qbox_tool_env[@]}" \
        "${cmake_cmd}" \
        --build "${QBOX_PLATFORM_BUILD_DIR}" \
        --target "${QBOX_APOLLO_BUILD_TARGET:-apollo_fvp_full_system}" \
        --parallel "${JOBS}"

    if [[ "${qbox_run_unit_tests}" == 1 ]]; then
        run_logged qbox-unit-test-build \
            "${cmake_cmd}" \
            --build "${QBOX_PLATFORM_BUILD_DIR}" \
            --target qbox_platform_systemc_component_tests \
            --parallel "${JOBS}"

        run_logged qbox-unit-tests \
            ctest \
            --test-dir "${QBOX_PLATFORM_BUILD_DIR}" \
            -L qbox-platform-systemc-components \
            --output-on-failure
    fi
}

qbox_sdk_native_sysroot()
{
    local native

    if [[ -n "${QBOX_NATIVE_SDK_SYSROOT:-}" && -d "${QBOX_NATIVE_SDK_SYSROOT}" ]]; then
        printf '%s\n' "${QBOX_NATIVE_SDK_SYSROOT}"
        return 0
    fi

    if [[ -n "${SDK_NATIVE_SYSROOT:-}" && -d "${SDK_NATIVE_SYSROOT}" ]]; then
        printf '%s\n' "${SDK_NATIVE_SYSROOT}"
        return 0
    fi

    [[ -d "${SDK_DIR}/sysroots" ]] || return 1
    native="$(find "${SDK_DIR}/sysroots" -mindepth 1 -maxdepth 1 -type d \
        -name '*-pokysdk-linux' 2>/dev/null | sort | head -n 1)"
    [[ -n "${native}" ]] || return 1
    printf '%s\n' "${native}"
}

qbox_yocto_libqemu_dir()
{
    local candidate

    if [[ -n "${QBOX_LIBQEMU_DIR:-}" ]]; then
        candidate="${QBOX_LIBQEMU_DIR}"
        if [[ -f "${candidate}/libqemuConfig.cmake" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
        if [[ -f "${candidate}/usr/lib/cmake/libqemu/libqemuConfig.cmake" ]]; then
            printf '%s\n' "${candidate}/usr/lib/cmake/libqemu"
            return 0
        fi
        die "QBOX_LIBQEMU_DIR does not contain libqemuConfig.cmake: ${QBOX_LIBQEMU_DIR}"
    fi

    candidate="${YOCTO_TMP}/sysroots-components/x86_64/qbox-libqemu-native/usr/lib/cmake/libqemu"
    if [[ -f "${candidate}/libqemuConfig.cmake" ]]; then
        printf '%s\n' "${candidate}"
        return 0
    fi

    candidate="$(
        find "${YOCTO_TMP}/work/x86_64-linux/qbox-libqemu-native" \
            -path '*/recipe-sysroot-native/usr/lib/cmake/libqemu/libqemuConfig.cmake' \
            -print -quit 2>/dev/null || true
    )"
    if [[ -n "${candidate}" ]]; then
        printf '%s\n' "${candidate%/libqemuConfig.cmake}"
        return 0
    fi

    return 1
}

qbox_sdk_native_tool_args()
{
    local -n env_args="$1"
    local -n cmake_args="$2"
    local native_sysroot
    local native_bin
    local tool_shim

    env_args=()
    cmake_args=()

    native_sysroot="$(qbox_sdk_native_sysroot || true)"
    [[ -n "${native_sysroot}" ]] || return 0

    native_bin="${native_sysroot}/usr/bin"
    [[ -x "${native_bin}/python3" ]] || return 0
    [[ -x "${native_bin}/meson" ]] || return 0
    [[ -x "${native_bin}/meson.real" ]] || return 0

    tool_shim="${QBOX_PLATFORM_BUILD_DIR}/.qbox-sdk-native-tools"
    mkdir -p "${tool_shim}"
    ln -sfn "${native_bin}/python3" "${tool_shim}/python3"
    ln -sfn "${native_bin}/meson" "${tool_shim}/meson"
    ln -sfn "${native_bin}/meson.real" "${tool_shim}/meson.real"

    log "Using Yocto SDK native Python/Meson for QBox: ${tool_shim}"
    env_args=(
        env
        -u OECORE_NATIVE_SYSROOT
        -u OECORE_TARGET_SYSROOT
        -u SDKTARGETSYSROOT
        -u SDKPATH
        -u CONFIG_SITE
        -u PKG_CONFIG_SYSROOT_DIR
        -u PKG_CONFIG_PATH
        -u PKG_CONFIG_LIBDIR
        -u OECORE_ACLOCAL_OPTS
        -u TARGET_PREFIX
        -u CONFIGURE_FLAGS
        -u CC
        -u CXX
        -u CPP
        -u LD
        -u AR
        -u AS
        -u STRIP
        -u OBJCOPY
        -u OBJDUMP
        -u READELF
        -u NM
        -u RANLIB
        -u CFLAGS
        -u CXXFLAGS
        -u CPPFLAGS
        -u LDFLAGS
        -u KCFLAGS
        "PATH=${tool_shim}:${HOST_PATH}"
        PYTHONNOUSERSITE=1
    )
    cmake_args=(
        -DLIBQEMU_PYTHON="${native_bin}/python3"
    )
}

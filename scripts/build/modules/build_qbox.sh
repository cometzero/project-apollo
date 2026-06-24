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
    require_dir "${QBOX_QEMU_DIR}"
    mkdir -p "${LOG_DIR}"

    reset_cmake_build_if_source_changed "${QBOX_PLATFORM_BUILD_DIR}" "${QBOX_PLATFORM_DIR}"

    run_cmake_configure_if_needed qbox-configure "${QBOX_PLATFORM_BUILD_DIR}" \
        cmake \
        -S "${QBOX_PLATFORM_DIR}" \
        -B "${QBOX_PLATFORM_BUILD_DIR}" \
        -DCMAKE_BUILD_TYPE="${QBOX_CMAKE_BUILD_TYPE:-Release}" \
        -DCMAKE_INSTALL_PREFIX="${QBOX_PLATFORM_BUILD_DIR}/install" \
        -DQBOX_CORE_SOURCE_DIR="${QBOX_CORE_DIR}" \
        -DQBOX_QEMU_SOURCE_DIR="${QBOX_QEMU_DIR}" \
        -DLIBQEMU_GIT="file://${QBOX_QEMU_DIR}" \
        -DFETCHCONTENT_SOURCE_DIR_LIBQEMU="${QBOX_QEMU_DIR}" \
        -DLIBQEMU_BUILD_ALWAYS="${QBOX_LIBQEMU_BUILD_ALWAYS:-OFF}" \
        -DQBOX_APOLLO_BUILD_TARGET="${QBOX_APOLLO_BUILD_TARGET:-apollo_fvp_full_system}"

    run_logged qbox-build \
        cmake \
        --build "${QBOX_PLATFORM_BUILD_DIR}" \
        --target "${QBOX_APOLLO_BUILD_TARGET:-apollo_fvp_full_system}" \
        --parallel "${JOBS}"
}

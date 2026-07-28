#!/usr/bin/env bash

# Variables assigned here are consumed by functions sourced from sibling
# modules in the same shell.
# shellcheck disable=SC2034,SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

component_recipe_toolchain_recipe()
{
    case "$1" in
        tf-m) printf 'trusted-firmware-m\n' ;;
        scp-firmware) printf 'scp-firmware\n' ;;
        optee) printf 'optee-os\n' ;;
        u-boot) printf 'u-boot\n' ;;
        tf-a) printf 'trusted-firmware-a\n' ;;
        linux|buildroot) printf 'virtual/kernel\n' ;;
        qbox|zephyr|flash-images|boot-disk|fvpconf|debug-manifest) return 1 ;;
        *) die "no recipe toolchain mapping for component: $1" ;;
    esac
}

recipe_toolchain_manifest()
{
    printf '%s/%s.env\n' "${LOCAL_BUILD_DIR}/toolchains" "$1"
}

recipe_toolchain_init_bitbake_env()
{
    clear_sdk_env_for_yocto
    export MACHINE
    export TEMPLATECONF="${TEMPLATECONF:-${ROOT_DIR}/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/${MACHINE}}"
    set +u
    # shellcheck disable=SC1091
    source "${ROOT_DIR}/layers/poky/oe-init-build-env" \
        "${YOCTO_BUILD_DIR}" >/dev/null
    set -u
    prepare_bitbake_extra_args
}

prepare_selected_component_toolchains()
{
    local components=("$@")
    local component
    local recipe
    local -a recipes=()
    local -A recipe_seen=()

    for component in "${components[@]}"; do
        recipe="$(component_recipe_toolchain_recipe "${component}" || true)"
        [[ -n "${recipe}" ]] || continue
        if [[ -z "${recipe_seen[${recipe}]+x}" ]]; then
            recipe_seen["${recipe}"]=1
            recipes+=("${recipe}")
        fi
    done
    ((${#recipes[@]} > 0)) || return 0

    mkdir -p "${LOCAL_BUILD_DIR}/toolchains" "${LOG_DIR}"
    (
        local bitbake_cmd="${BITBAKE:-bitbake}"
        local manifest
        local workdir
        local target_prefix
        local query_cmd="${RECIPE_TOOLCHAIN_QUERY:-${ROOT_DIR}/scripts/build/query_recipe_sysroots.py}"
        local query_output
        local -A recipe_workdirs=()
        local -A recipe_target_prefixes=()
        local -A queried_recipes=()

        recipe_toolchain_init_bitbake_env
        log "Preparing recipe sysroots: ${recipes[*]}"
        "${bitbake_cmd}" "${BITBAKE_EXTRA_ARGS[@]}" \
            "${recipes[@]}" -c prepare_recipe_sysroot 2>&1 |
            tee "${LOG_DIR}/yocto-prepare-recipe-toolchains.log"

        query_output="$("${query_cmd}" "${recipes[@]}")"
        while IFS=$'\t' read -r recipe workdir target_prefix; do
            [[ -n "${recipe}" && -n "${workdir}" && -n "${target_prefix}" ]] ||
                die "invalid recipe sysroot query output: $(printf '%q' "${recipe}")"
            require_dir "${workdir}/recipe-sysroot-native"
            require_dir "${workdir}/recipe-sysroot"
            recipe_workdirs["${recipe}"]="${workdir}"
            recipe_target_prefixes["${recipe}"]="${target_prefix}"
            queried_recipes["${recipe}"]=1
        done <<< "${query_output}"
        for recipe in "${recipes[@]}"; do
            [[ -n "${queried_recipes[${recipe}]+x}" ]] ||
                die "recipe sysroot query omitted ${recipe}"
        done

        for component in "${components[@]}"; do
            recipe="$(component_recipe_toolchain_recipe "${component}" || true)"
            [[ -n "${recipe}" ]] || continue
            workdir="${recipe_workdirs[${recipe}]}"
            target_prefix="${recipe_target_prefixes[${recipe}]}"
            manifest="$(recipe_toolchain_manifest "${component}")"
            {
                printf 'RECIPE_TOOLCHAIN_RECIPE=%q\n' "${recipe}"
                printf 'RECIPE_TOOLCHAIN_WORKDIR=%q\n' "${workdir}"
                printf 'SDK_NATIVE_SYSROOT=%q\n' \
                    "${workdir}/recipe-sysroot-native"
                printf 'SDK_TARGET_SYSROOT=%q\n' \
                    "${workdir}/recipe-sysroot"
                printf 'AARCH64_PREFIX=%q\n' "${target_prefix}"
            } | write_file_if_changed "${manifest}"
        done
    )
}

deactivate_component_recipe_toolchain()
{
    export PATH="${HOST_PATH}"
    unset RECIPE_TOOLCHAIN_RECIPE RECIPE_TOOLCHAIN_WORKDIR
    unset RECIPE_TOOLCHAIN_SYSROOT_FLAG SDK_NATIVE_SYSROOT SDK_TARGET_SYSROOT
    unset OPENSSL_MODULES TARGET_PREFIX
}

activate_component_recipe_toolchain()
{
    local component="$1"
    local recipe
    local manifest
    local tuple
    local compiler
    local arm_none
    local aarch64_none

    deactivate_component_recipe_toolchain
    recipe="$(component_recipe_toolchain_recipe "${component}" || true)"
    [[ -n "${recipe}" ]] || return 0
    manifest="$(recipe_toolchain_manifest "${component}")"
    require_file "${manifest}"
    # shellcheck disable=SC1090
    source "${manifest}"

    [[ "${RECIPE_TOOLCHAIN_RECIPE}" == "${recipe}" ]] ||
        die "recipe toolchain manifest mismatch for ${component}: ${RECIPE_TOOLCHAIN_RECIPE}"
    require_dir "${SDK_NATIVE_SYSROOT}"
    require_dir "${SDK_TARGET_SYSROOT}"
    if [[ -d "${SDK_NATIVE_SYSROOT}/usr/lib/ossl-modules" ]]; then
        export OPENSSL_MODULES="${SDK_NATIVE_SYSROOT}/usr/lib/ossl-modules"
    fi

    TARGET_PREFIX="${AARCH64_PREFIX}"
    RECIPE_TOOLCHAIN_SYSROOT_FLAG="--sysroot=${SDK_TARGET_SYSROOT}"
    tuple="${AARCH64_PREFIX%-}"
    path_prepend "${SDK_NATIVE_SYSROOT}/usr/bin"
    path_prepend "${SDK_NATIVE_SYSROOT}/usr/bin/${tuple}"
    arm_none="$(find_first_file "${SDK_NATIVE_SYSROOT}" "arm-none-eabi-gcc" || true)"
    [[ -z "${arm_none}" ]] || path_prepend "$(dirname "${arm_none}")"
    aarch64_none="$(
        find_first_file "${SDK_NATIVE_SYSROOT}" "aarch64-none-elf-gcc" || true
    )"
    [[ -z "${aarch64_none}" ]] || path_prepend "$(dirname "${aarch64_none}")"
    case "${component}" in
        optee|u-boot|tf-a|linux|buildroot)
            compiler="${SDK_NATIVE_SYSROOT}/usr/bin/${tuple}/${AARCH64_PREFIX}gcc"
            require_file "${compiler}"
            ;;
    esac

    unset ARCH CROSS_COMPILE
    unset CC CXX CPP LD AR AS STRIP OBJCOPY OBJDUMP READELF NM RANLIB
    unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS
    log "Using ${recipe} recipe sysroots for ${component}: ${RECIPE_TOOLCHAIN_WORKDIR}"
}

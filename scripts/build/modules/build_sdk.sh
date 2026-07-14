#!/usr/bin/env bash

# shellcheck disable=SC2154,SC1091

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

build_sdk()
{
    local bitbake_cmd="${BITBAKE:-bitbake}"

    mkdir -p "${LOG_DIR}"

    if first_existing_glob "${SDK_DIR}/environment-setup-*" >/dev/null; then
        log "Yocto SDK already installed at ${SDK_DIR}"
        return 0
    fi

    local installer
    installer="$(find_sdk_installer || true)"
    if [[ -z "${installer}" ]]; then
        run_populate_sdk_task "${bitbake_cmd}" 0
        installer="$(find_sdk_installer)"
        if [[ -z "${installer}" ]]; then
            log "SDK installer is still missing; forcing bitbake nexios-image -c populate_sdk"
            run_populate_sdk_task "${bitbake_cmd}" 1
            installer="$(find_sdk_installer)"
        fi
    fi

    require_file "${installer}"
    log "Installing Yocto SDK: ${installer} -> ${SDK_DIR}"
    sh "${installer}" -y -d "${SDK_DIR}" 2>&1 | tee "${LOG_DIR}/yocto-sdk-install.log"
}

refresh_sdk()
{
    local bitbake_cmd="${BITBAKE:-bitbake}"
    local installer

    mkdir -p "${LOG_DIR}"
    run_populate_sdk_task "${bitbake_cmd}" 1
    installer="$(find_sdk_installer)"
    require_file "${installer}"
    reinstall_sdk "${installer}"
}

reinstall_sdk()
{
    local installer="$1"
    local backup="${SDK_DIR}.refresh-backup.$$"
    local had_existing=0
    local status

    [[ -n "${SDK_DIR}" && "${SDK_DIR}" != / ]] ||
        die "refusing to replace unsafe SDK directory: ${SDK_DIR}"
    [[ ! -e "${backup}" && ! -L "${backup}" ]] ||
        die "SDK refresh backup already exists: ${backup}"

    if [[ -e "${SDK_DIR}" || -L "${SDK_DIR}" ]]; then
        log "Preserving existing Yocto SDK until the refreshed SDK is installed: ${backup}"
        mv -- "${SDK_DIR}" "${backup}"
        had_existing=1
    fi

    log "Reinstalling Yocto SDK: ${installer} -> ${SDK_DIR}"
    if sh "${installer}" -y -d "${SDK_DIR}" 2>&1 |
        tee "${LOG_DIR}/yocto-sdk-install.log"; then
        if ((had_existing)); then
            rm -rf -- "${backup}"
        fi
        return 0
    else
        status=$?
    fi

    log "ERROR: Yocto SDK reinstall failed; restoring the previous SDK."
    rm -rf -- "${SDK_DIR}"
    if ((had_existing)); then
        mv -- "${backup}" "${SDK_DIR}"
    fi
    return "${status}"
}

run_populate_sdk_task()
{
    local bitbake_cmd="$1"
    local force="$2"
    local force_args=()
    local tee_args=("${LOG_DIR}/yocto-populate-sdk.log")

    if [[ "${force}" == 1 ]]; then
        force_args=(-f)
        tee_args=(-a "${LOG_DIR}/yocto-populate-sdk.log")
        log "Forcing Yocto SDK regeneration with bitbake nexios-image -c populate_sdk -f"
    else
        log "Creating Yocto SDK with bitbake nexios-image -c populate_sdk"
    fi
    log "WARNING: Yocto SDK generation can take a long time."

    (
        cd "${ROOT_DIR}" || exit
        clear_sdk_env_for_yocto
        set +u
        # shellcheck disable=SC1091
        source layers/poky/oe-init-build-env "${YOCTO_BUILD_DIR}" >/dev/null
        set -u
        prepare_bitbake_extra_args
        "${bitbake_cmd}" "${BITBAKE_EXTRA_ARGS[@]}" nexios-image -c populate_sdk \
            "${force_args[@]}"
    ) 2>&1 | tee "${tee_args[@]}"
}

find_sdk_installer()
{
    [[ -d "${YOCTO_TMP}/deploy/sdk" ]] || return 0
    find "${YOCTO_TMP}/deploy/sdk" -maxdepth 1 -type f \
        -name "*${MACHINE}*toolchain*.sh" 2>/dev/null | sort | tail -n 1
}

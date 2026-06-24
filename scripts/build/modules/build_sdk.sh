#!/usr/bin/env bash

# shellcheck disable=SC2154,SC1091

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

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
        log "Creating Yocto SDK with bitbake nexios-image -c populate_sdk"
        (
            cd "${ROOT_DIR}" || exit
            clear_sdk_env_for_yocto
            set +u
            # shellcheck disable=SC1091
            source layers/poky/oe-init-build-env build >/dev/null
            set -u
            prepare_bitbake_extra_args
            bitbake "${BITBAKE_EXTRA_ARGS[@]}" nexios-image -c populate_sdk
        ) 2>&1 | tee "${LOG_DIR}/yocto-populate-sdk.log"
        installer="$(find "${YOCTO_TMP}/deploy/sdk" -maxdepth 1 -type f -name '*.sh' | sort | tail -n 1)"
    fi

    require_file "${installer}"
    log "Installing Yocto SDK: ${installer} -> ${SDK_DIR}"
    sh "${installer}" -y -d "${SDK_DIR}" 2>&1 | tee "${LOG_DIR}/yocto-sdk-install.log"
}

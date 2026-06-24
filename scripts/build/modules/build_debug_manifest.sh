#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

generate_debug_manifest()
{
    run_logged local-debug-manifest python3 "${ROOT_DIR}/scripts/setup/setup_local_debug_env.py" \
        --local-build-dir "${LOCAL_BUILD_DIR}" \
        --out-dir "${LOCAL_BUILD_DIR}/debug"
    require_file "${LOCAL_BUILD_DIR}/debug/symbols.json"
}

#!/usr/bin/env bash
#
# Bootstrap a clean Apollo workspace checkout.
#
# Do not use a blanket "git submodule update --recursive" here. Some Zephyr
# HAL repositories contain optional nested gitlinks without .gitmodules URL
# entries, which makes a full recursive update fail before the Apollo build can
# start. The Apollo build only needs the root submodules plus a small set of
# known nested dependencies.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JOBS="${JOBS:-8}"
WITH_QEMU_ROMS=0
FORCE=0

usage()
{
    cat <<EOF
Usage: scripts/setup/bootstrap_project.sh [options]

Options:
  --root DIR          Workspace root to initialize (default: ${ROOT_DIR})
  --jobs N           Parallel submodule jobs (default: ${JOBS})
  --with-qemu-roms   Also initialize QEMU ROM/test submodules
  --force            Force checkout of pinned submodule revisions
  -h, --help         Show this help

This script is intended for clean clones. It initializes all submodules listed
in the root .gitmodules file, then recursively initializes only the nested
submodules required by the Apollo Yocto/local/QBox build flows.
EOF
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

run()
{
    local -a cmd=("$@")

    printf '+'
    printf ' %q' "${cmd[@]}"
    printf '\n'
    "${cmd[@]}"
}

while (($#)); do
    case "$1" in
        --root)
            (($# >= 2)) || die "--root requires a value"
            ROOT_DIR="$2"
            shift 2
            ;;
        --jobs)
            (($# >= 2)) || die "--jobs requires a value"
            JOBS="$2"
            shift 2
            ;;
        --with-qemu-roms)
            WITH_QEMU_ROMS=1
            shift
            ;;
        --force)
            FORCE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1"
            ;;
    esac
done

ROOT_DIR="$(cd "${ROOT_DIR}" && pwd)"
[[ -f "${ROOT_DIR}/.gitmodules" ]] ||
    die "missing .gitmodules under ${ROOT_DIR}"
[[ "${JOBS}" =~ ^[0-9]+$ ]] && ((JOBS > 0)) ||
    die "--jobs must be a positive integer: ${JOBS}"

required_recursive_paths=(
    "hsoc-stack/components/primary_compute/trusted-firmware-a"
    "hsoc-stack/components/system_mgmt/scp-firmware"
    "hsoc-stack/components/system_mgmt/zephyrproject/zephyr"
)

if ((WITH_QEMU_ROMS)); then
    required_recursive_paths+=("tools/qemu" "hsoc-stack/tools/qemu")
fi

submodule_update_args=(submodule update --init --checkout --jobs "${JOBS}")
if ((FORCE)); then
    submodule_update_args+=(--force)
fi

run git -C "${ROOT_DIR}" submodule sync
run git -C "${ROOT_DIR}" "${submodule_update_args[@]}"

for path in "${required_recursive_paths[@]}"; do
    [[ -d "${ROOT_DIR}/${path}" ]] ||
        die "submodule path was not initialized: ${path}"
    recursive_args=("${submodule_update_args[@]}" --recursive -- "${path}")
    run git -C "${ROOT_DIR}" "${recursive_args[@]}"
done

printf '\nBootstrap complete: %s\n' "${ROOT_DIR}"

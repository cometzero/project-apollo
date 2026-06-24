#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=scripts/build/local_build_common.sh
source "${SCRIPT_DIR}/local_build_common.sh"
source_local_build_modules \
    build_qbox.sh \
    build_tfm.sh \
    build_scp.sh \
    build_zephyr.sh \
    build_uboot.sh \
    build_optee.sh \
    build_tfa.sh \
    build_linux.sh \
    build_buildroot.sh \
    build_flash_images.sh \
    build_boot_disk.sh \
    build_fvpconf.sh \
    build_debug_manifest.sh \
    build_orchestrator.sh

case "${1:-}" in
    -h|--help|help)
        usage
        exit 0
        ;;
esac

(($# == 0)) || die "build_images.sh does not accept arguments"

build_qbox
setup_build_environment
build_all

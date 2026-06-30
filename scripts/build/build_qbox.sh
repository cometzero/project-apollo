#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=scripts/build/local_build_common.sh
source "${SCRIPT_DIR}/local_build_common.sh"
source_local_build_modules build_qbox.sh

case "${1:-}" in
    -h|--help|help)
        usage
        printf '\nQBox options:\n'
        printf '  --systemc-component-tests  run qbox-platform SystemC component CTests after build\n'
        exit 0
        ;;
    --systemc-component-tests)
        QBOX_RUN_SYSTEMC_COMPONENT_TESTS=1
        shift
        ;;
esac

(($# == 0)) || die "build_qbox.sh does not accept arguments"

build_qbox

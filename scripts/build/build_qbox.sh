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
        printf '  --unit-tests               run qbox-platform unit tests after build\n'
        printf '  --systemc-component-tests  alias for --unit-tests\n'
        exit 0
        ;;
    --unit-tests)
        QBOX_RUN_UNIT_TESTS=1
        shift
        ;;
    --systemc-component-tests)
        QBOX_RUN_UNIT_TESTS=1
        QBOX_RUN_SYSTEMC_COMPONENT_TESTS=1
        shift
        ;;
esac

(($# == 0)) || die "build_qbox.sh does not accept arguments"

build_qbox

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=scripts/build/local_build_common.sh
source "${SCRIPT_DIR}/local_build_common.sh"
source_local_build_modules build_orchestrator.sh

case "${1:-}" in
    -h|--help|help)
        usage
        exit 0
        ;;
esac

(($# == 0)) || die "build_clean.sh does not accept arguments"

clean

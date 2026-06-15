#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
source "${SCRIPT_DIR}/local_build_common.sh"

case "${1:-}" in
    -h|--help|help)
        usage
        exit 0
        ;;
esac

(($# == 0)) || die "build_qbox.sh does not accept arguments"

build_qbox

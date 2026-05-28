#!/usr/bin/env bash
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POKY_DIR="${WORKSPACE_DIR}/layers/poky"

BUILD_DIR="${BUILD_DIR:-${WORKSPACE_DIR}/build}"
TEMPLATECONF="${TEMPLATECONF:-${WORKSPACE_DIR}/hsoc-apollo/yocto/meta-hsoc-apollo/conf/templates/apollo-fvp}"

if [[ ! -f "${POKY_DIR}/oe-init-build-env" ]]; then
    echo "error: missing ${POKY_DIR}/oe-init-build-env" >&2
    exit 1
fi

if [[ ! -d "${TEMPLATECONF}" ]]; then
    echo "error: missing TEMPLATECONF directory: ${TEMPLATECONF}" >&2
    exit 1
fi

export TEMPLATECONF

# shellcheck source=/dev/null
set +u
source "${POKY_DIR}/oe-init-build-env" "${BUILD_DIR}"
set -u

bitbake baremetal-image

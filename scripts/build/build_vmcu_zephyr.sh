#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Compatibility entry point: use the shared hsoc-stack Zephyr Yocto recipe.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
if [[ "${1:-}" == "--bootstrap" ]]; then
    echo "--bootstrap is obsolete; Yocto provides the toolchain and dependencies." >&2
    shift
fi
exec "$root/yocto_build.sh" --keep-conf "$@" zephyr-vmcu

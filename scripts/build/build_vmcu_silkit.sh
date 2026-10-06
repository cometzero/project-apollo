#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Compatibility entry point: Yocto owns SDK and participant builds.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
if [[ "${1:-}" == "--bootstrap" ]]; then
    echo "--bootstrap is obsolete; Yocto builds SIL Kit and its dependencies." >&2
    shift
fi
exec "$root/yocto_build.sh" --keep-conf "$@" vmcu-silkit-native

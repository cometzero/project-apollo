#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/../.." && pwd)"
python_bin="${PYTHON:-python3}"
jobs="${QBOX_APOLLO_FULL_JOBS:-}"

args=(--build-only --local-build-dir "${workspace_root}/build/local-apollo-fvp")
if [[ -n "${jobs}" ]]; then
    args+=(--jobs "${jobs}")
fi

exec "${python_bin}" \
    "${workspace_root}/scripts/run/run_qbox_apollo_fvp_full.py" \
    "${args[@]}" \
    "$@"

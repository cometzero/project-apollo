#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON:-python3}"
jobs="${QBOX_RDASPEN_JOBS:-}"

args=(--build-only)
if [[ -n "${jobs}" ]]; then
    args+=(--jobs "${jobs}")
fi

exec "${python_bin}" \
    "${workspace_root}/scripts/run_qbox_fvp_rd_aspen_linux.py" \
    "${args[@]}" \
    "$@"

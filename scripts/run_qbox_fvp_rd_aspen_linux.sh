#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON:-python3}"
timeout="${QBOX_RDASPEN_TIMEOUT:-0}"

exec "${python_bin}" \
    "${workspace_root}/scripts/run_qbox_fvp_rd_aspen_linux.py" \
    --skip-build \
    --skip-dtb \
    --interactive \
    --timeout "${timeout}" \
    "$@"

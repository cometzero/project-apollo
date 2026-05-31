#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON:-python3}"
timeout="${QBOX_APOLLO_TIMEOUT:-0}"

exec "${python_bin}" \
    "${workspace_root}/scripts/run_qbox_apollo_fvp_linux.py" \
    --skip-build \
    --interactive \
    --timeout "${timeout}" \
    --local-build-dir "${workspace_root}/build/local-apollo-fvp" \
    "$@"

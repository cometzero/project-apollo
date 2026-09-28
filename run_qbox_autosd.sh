#!/usr/bin/env bash
# AutoSD UKIBoot through the Apollo RSE/SI/AP firmware boot chain.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "${ROOT_DIR}/scripts/run/run_qbox_autosd.py" "$@"

#!/usr/bin/env bash
# Launch AP Linux through the SRAM reset payload with mocked firmware services.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "${ROOT_DIR}/scripts/run/run_qbox_linux.py" "$@"

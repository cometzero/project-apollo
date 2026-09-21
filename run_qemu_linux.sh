#!/usr/bin/env bash
# Boot the Apollo Linux images on standalone QEMU.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "${ROOT_DIR}/scripts/run/run_qemu_linux.py" "$@"

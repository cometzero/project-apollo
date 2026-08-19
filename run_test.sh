#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="${ROOT_DIR}/qa-tests${PYTHONPATH:+:${PYTHONPATH}}" \
    python3 -m apollo_validation.cli root-run --root "${ROOT_DIR}" -- "$@"

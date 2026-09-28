#!/usr/bin/env bash
# Read-only startup readiness, not recovery. Keep transient output in evidence.
set -euo pipefail
timeout --kill-after=10 180 bash -euo pipefail -c '
    until bluechictl status qm.host | grep -q online; do sleep 3; done
    until podman exec qm systemctl is-active --quiet apollo-qm-container; do sleep 3; done
'
echo AUTOMOTIVE_STARTUP_READY

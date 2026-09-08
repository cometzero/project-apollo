#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run a local shell script in the active QBox guest over its SSH forward.

set -euo pipefail

usage() {
    echo "Usage: $0 <guest-shell-script>" >&2
    echo "Defaults: root@127.0.0.1:8022" >&2
}

if [[ $# -ne 1 || ! -f $1 || ! -r $1 ]]; then
    usage
    exit 2
fi

guest_script=$1
guest_host=${QBOX_SSH_HOST:-127.0.0.1}
guest_user=${QBOX_SSH_USER:-root}
guest_port=${QBOX_SSH_PORT:-${SSH_PORT:-8022}}
connect_timeout=${QBOX_SSH_CONNECT_TIMEOUT:-5}

exec ssh \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout="$connect_timeout" \
    -p "$guest_port" \
    "$guest_user@$guest_host" sh -s < "$guest_script"

#!/bin/sh
# Execute only in the private AutoSD guest after HIPC_ENDPOINT_READY.
# Optional first argument overrides the uploaded probe path.
set -eu
probe_path=${1:-/var/tmp/apollo-hipc-ping.py}
test "$(id -u)" = 0
command -v nmcli >/dev/null
command -v python3 >/dev/null
test -r /sys/class/net/ethsi1/ifindex
test ! -e /sys/class/net/ethsi1.200
test -f "$probe_path"
trial_uuid=$(python3 -c 'import uuid; print(uuid.uuid4())')
trial_name=apollo-hipc-trial-$trial_uuid
trial_created=0
cleanup() {
    trial_rc=$?
    trap - EXIT HUP INT TERM
    # Query failures must not be mistaken for successful cleanup. Once add
    # succeeds, delete our exact UUID directly and report any failure.
    if [ "$trial_created" = 1 ]; then
        if ! nmcli --wait 15 connection delete uuid "$trial_uuid"; then
            echo "HIPC_TRIAL_CLEANUP_FAILED uuid=$trial_uuid" >&2
            trial_rc=1
        fi
    fi
    exit "$trial_rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM
printf 'HIPC_TRIAL_START uuid=%s boot_id=%s\n' "$trial_uuid" "$(cat /proc/sys/kernel/random/boot_id)"
# save no makes the profile transient; no changes to eth0 or existing profiles.
nmcli --wait 15 connection add save no type vlan con-name "$trial_name" \
    ifname ethsi1.200 dev ethsi1 id 200 connection.uuid "$trial_uuid" \
    connection.autoconnect no ipv4.method manual ipv4.addresses 192.168.1.2/24 \
    ipv4.never-default yes ipv6.method disabled || {
        echo "HIPC_TRIAL_CREATE_UNCONFIRMED inspect_uuid=$trial_uuid" >&2
        exit 1
    }
trial_created=1
nmcli --wait 30 connection up uuid "$trial_uuid"
python3 "$probe_path" --interface ethsi1.200 \
    --source 192.168.1.2 --peer 192.168.1.1 --timeout 10
printf 'HIPC_TRIAL_COMPLETE boot_id=%s\n' "$(cat /proc/sys/kernel/random/boot_id)"

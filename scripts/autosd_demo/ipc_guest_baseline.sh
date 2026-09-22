#!/usr/bin/env bash
# Root-domain substrate test, NOT qualification of QM, containers or policy.
set -euo pipefail
payload=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
evidence=$(mktemp -d /var/tmp/apollo-ipc-baseline.XXXXXX)
shared=$(mktemp -d /dev/shm/apollo-ipc-baseline.XXXXXX)
server_pid=
cleanup() {
    if [[ -n "$server_pid" ]]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM
trap 'printf "RESULT root_ipc_substrate FAIL\n"' ERR
printf 'EVIDENCE=%s\nSHARED=%s\n' "$evidence" "$shared"
id
getenforce
findmnt -T /dev/shm
for name in uds-server uds-client shm-server shm-client; do
    [[ -x "$payload/$name" ]] || {
        printf 'RESULT root_ipc_substrate BLOCKED missing_binary=%s\n' "$name"
        exit 2
    }
done
wait_socket() {
    for ((i=0; i<100; i++)); do
        [[ -S "$1" ]] && return 0
        sleep 0.1
    done
    return 1
}
timeout --kill-after=2 20 "$payload/uds-server" --uds-path "$evidence/uds.socket" \
    > "$evidence/uds-server.log" 2>&1 &
server_pid=$!
wait_socket "$evidence/uds.socket"
rc=0
timeout --kill-after=2 4 "$payload/uds-client" --uds-path "$evidence/uds.socket" \
    > "$evidence/uds-client.log" 2>&1 || rc=$?
[[ "$rc" == 124 ]]
cleanup
server_pid=
grep -q 'Data received (' "$evidence/uds-server.log"
grep -q 'Data received: Got message:' "$evidence/uds-client.log"
printf 'RESULT root_uds_substrate PASS\n'

timeout --kill-after=2 42 "$payload/shm-server" --uds-path "$evidence/shm.socket" \
    --shm-name "$shared/data" > "$evidence/shm-server.log" 2>&1 &
server_pid=$!
wait_socket "$evidence/shm.socket"
timeout --kill-after=2 38 "$payload/shm-client" --uds-path "$evidence/shm.socket" \
    --shm-name "$shared/data" > "$evidence/shm-client.log" 2>&1
wait "$server_pid"
server_pid=
grep -q 'Shared memory content:' "$evidence/shm-server.log"
grep -q 'Sent read command' "$evidence/shm-client.log"
grep -q 'Exit command received' "$evidence/shm-server.log"
printf 'RESULT root_shared_memory_substrate PASS\n'
printf 'SCOPE unchanged_official_programs_root_only; QM/container/custom_SELinux_policy_unverified\n'

#!/usr/bin/env bash
# Require real Enforcing denials and a successful 30-message root/QM exchange.
set -euo pipefail
out=${1:-/root/selinux-demo/evidence}
mkdir "$out"
test "$(getenforce)" = Enforcing
rpm -q custom-policy-selinux
systemctl is-active --quiet qm
cursor=$(journalctl -k -n1 --show-cursor --no-pager | sed -n 's/^-- cursor: //p')
test -n "$cursor"
audit_offset=0
test ! -f /var/log/audit/audit.log || audit_offset=$(stat -c %s /var/log/audit/audit.log)
capture_avc() {
    journalctl -k --after-cursor "$cursor" --no-pager > "$out/avc.log"
    if test -f /var/log/audit/audit.log; then
        tail -c +$((audit_offset+1)) /var/log/audit/audit.log >> "$out/avc.log"
    fi
}
unit() {
    local where=$1; shift
    if test "$where" = root; then systemctl "$@"; else podman exec qm systemctl "$@"; fi
}
deny() {
    local where=$1 name=$2 domain=$3 state=
    unit "$where" reset-failed "$name" || true
    unit "$where" start "$name" || true
    for ((i=0; i<30; i++)); do
        state=$(unit "$where" show -p ActiveState --value "$name")
        test "$state" != failed || break
        sleep 1
    done
    test "$state" = failed
    test "$(unit "$where" show -p ExecMainStatus --value "$name")" != 0
    capture_avc
    # A denial at /dev/null or generic QM-rootfs traversal is not IPC isolation proof.
    grep -E "avc:.*denied.*scontext=[^ ]*:${domain}:.*tcontext=[^ ]*:(shared_uds_uds_t|named_shm_shm_t):.*permissive=0" \
        "$out/avc.log" > "$out/$domain.denied.log"
    printf '%s %s DENY_PASS (%s)\n' "$where" "$name" "$domain"
}
finish() {
    capture_avc || true
    journalctl -u server -u server-other -u client --no-pager > "$out/root-services.log" || true
    podman exec qm journalctl -u server -u client -u client-other --no-pager > "$out/qm-services.log" || true
}
trap finish EXIT
systemctl stop server server-other client || true
podman exec qm systemctl stop server client client-other || true
rm -f /run/nshm_demo/sock.socket /dev/shm/qm/shared
deny root server-other root_server_other_t
deny qm server qm_qm_server_t

systemctl start server
server_pid=$(systemctl show -p MainPID --value server)
tr -d '\000' < "/proc/$server_pid/attr/current" | grep ':root_server_t:' | tee "$out/root-server-domain.log"
for ((i=0; i<30; i++)); do test ! -S /run/nshm_demo/sock.socket || break; sleep 1; done
test -S /run/nshm_demo/sock.socket
deny root client root_client_t
deny qm client-other qm_qm_client_other_t

podman exec qm systemctl start client
qm_client_pid=$(podman exec qm systemctl show -p MainPID --value client)
podman exec qm cat "/proc/$qm_client_pid/attr/current" | tr -d '\000' | grep ':qm_qm_client_t:' | tee "$out/qm-client-domain.log"
for ((i=0; i<90; i++)); do
    state=$(podman exec qm systemctl show -p ActiveState --value client)
    test "$state" != inactive || break
    test "$state" != failed
    sleep 1
done
test "$state" = inactive
test "$(podman exec qm systemctl show -p ExecMainStatus --value client)" = 0
test "$(systemctl show -p ExecMainStatus --value server)" = 0
journalctl -u server --after-cursor "$cursor" --no-pager > "$out/root-transfer.log"
test "$(grep -c 'Read command received' "$out/root-transfer.log")" = 30
test "$(grep -c 'Shared memory content:' "$out/root-transfer.log")" = 30
capture_avc
if grep -E 'avc:.*denied.*scontext=[^ ]*:(root_server_t|qm_qm_client_t):' "$out/avc.log"; then
    echo 'Unexpected denial in allowed domains' >&2
    exit 1
fi
test "$(getenforce)" = Enforcing
echo 'CUSTOM_SELINUX_MATRIX_PASS (4 denied domains, root_server_t to qm_qm_client_t, 30 messages)'

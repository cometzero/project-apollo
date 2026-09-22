#!/usr/bin/env bash
# Unchanged official static IPC programs, run across root and nested QM containers.
set -euo pipefail
payload=${1:?Usage: qm_ipc_guest_check.sh PAYLOAD_DIR}
evidence=$(mktemp -d /var/tmp/apollo-qm-ipc.XXXXXX)
image=localhost/apollo-ipc-tools:followup
cleanup() {
    podman exec qm podman rm -f apollo-uds-client >/dev/null 2>&1 || true
    podman rm -f apollo-uds-server >/dev/null 2>&1 || true
}
trap cleanup EXIT
test "$(getenforce)" = Enforcing
command -v tar
if test -e /etc/containers/systemd/qm.container.d/20-apollo-ipc.conf; then
    test "$(cat /etc/containers/systemd/qm.container.d/20-apollo-ipc.conf)" = $'[Container]\nVolume=/run/ipc:/run/ipc'
fi
install -d /run/ipc /etc/containers/systemd/qm.container.d
install -d /etc/tmpfiles.d
printf 'd /run/ipc 0755 root root -\nd /tmp/iceoryx2 0755 root root -\nd /tmp/iceoryx2/services 0755 root root -\nd /tmp/iceoryx2/nodes 0755 root root -\n' > /etc/tmpfiles.d/apollo-qm-shared-paths.conf
printf '[Container]\nVolume=/run/ipc:/run/ipc\n' > /etc/containers/systemd/qm.container.d/20-apollo-ipc.conf
restorecon -RF /run/ipc /etc/containers/systemd
systemctl daemon-reload
systemctl restart qm
tar -C "$payload" -cf "$evidence/tools.tar" uds-server uds-client shm-server shm-client
podman import "$evidence/tools.tar" "$image"
podman save -o "$evidence/tools-image.tar" "$image"
podman cp "$evidence/tools-image.tar" qm:/var/tmp/apollo-ipc-tools.tar
podman exec qm podman load -i /var/tmp/apollo-ipc-tools.tar
podman exec qm podman info
podman run -d --name apollo-uds-server --network none \
    --security-opt label=type:ipc_t -v /run/ipc:/run/ipc \
    "$image" /uds-server --uds-path /run/ipc/apollo-uds.socket
for ((i=0; i<60; i++)); do
    test -S /run/ipc/apollo-uds.socket && break
    sleep 1
done
test -S /run/ipc/apollo-uds.socket
podman exec qm test -S /run/ipc/apollo-uds.socket
podman exec qm podman run -d --name apollo-uds-client --network none --cpuset-cpus 0 \
    --security-opt label=type:qm_container_ipc_t -v /run/ipc:/run/ipc \
    "$image" /uds-client --uds-path /run/ipc/apollo-uds.socket
sleep 5
podman logs apollo-uds-server > "$evidence/server.log" 2>&1
podman exec qm podman logs apollo-uds-client > "$evidence/client.log" 2>&1
cat "$evidence/server.log" "$evidence/client.log"
grep -q 'Data received (' "$evidence/server.log"
grep -q 'Data received: Got message:' "$evidence/client.log"
client_pid=$(podman exec qm podman inspect --format '{{.State.Pid}}' apollo-uds-client)
[[ $client_pid =~ ^[1-9][0-9]*$ ]]
podman exec qm cat "/proc/$client_pid/status" > "$evidence/client-status.txt"
grep 'Cpus_allowed_list:' "$evidence/client-status.txt"
test "$(awk '/^Cpus_allowed_list:/ {print $2}' "$evidence/client-status.txt")" = 0
ps -eZ | grep -E 'uds-|conmon'
getenforce
test "$(getenforce)" = Enforcing
echo "QM_NESTED_UDS_CPUSET_PASS evidence=$evidence"

#!/usr/bin/env bash
# Verify minimal QM in an already booted, disposable AutoSD guest.
set -euo pipefail
test "$(id -u)" = 0
rpm -q qm
test "$(getenforce)" = Enforcing
ready=false
for ((attempt = 0; attempt < 60; attempt++)); do
    if systemctl is-active --quiet qm &&
       test "$(podman inspect --format '{{.State.Running}}' qm 2>/dev/null)" = true; then
        ready=true
        break
    fi
    sleep 2
done
systemctl status qm --no-pager || true
if test "$ready" != true; then
    journalctl -b -u qm --no-pager -n 100
    exit 1
fi
podman inspect --format '{{.Name}} pid={{.State.Pid}} running={{.State.Running}}' qm
qm_pid=$(podman inspect --format '{{.State.Pid}}' qm)
[[ $qm_pid =~ ^[1-9][0-9]*$ ]]
host_namespace=$(readlink /proc/1/ns/pid)
qm_namespace=$(readlink "/proc/$qm_pid/ns/pid")
printf 'root PID namespace=%s; QM PID namespace=%s\n' "$host_namespace" "$qm_namespace"
test "$host_namespace" != "$qm_namespace"
podman exec qm /bin/sh -ec 'uname -r; cat /etc/os-release; test -d /proc/1; cat /proc/1/comm'
test "$(getenforce)" = Enforcing
echo 'MINIMAL_QM_RUNTIME_PASS (not IPC, isolation, OTA or timing qualification)'

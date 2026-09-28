#!/usr/bin/env bash
# Read-only healthy-state gate; run in the private four-CPU AutoSD guest.
set -euo pipefail
test "$(getenforce)" = Enforcing
for unit in bluechi-controller bluechi-agent qm apollo-adas apollo-safety-monitor; do
    systemctl is-active --quiet "$unit"
done
bluechictl status host
bluechictl status qm.host
bluechictl status host | grep -q online
bluechictl status qm.host | grep -q online
podman exec apollo-adas /workload health /run/heartbeat
for unit in apollo-qm-app apollo-qm-container bluechi-agent; do
    podman exec qm systemctl is-active --quiet "$unit"
done
podman exec qm /usr/libexec/apollo/workload health /run/apollo-qm/heartbeat
podman exec qm podman exec apollo-qm-container /workload health /run/heartbeat
python3 -c 'import json; assert json.load(open("/run/apollo-safety/state.json"))["state"] == "HEALTHY"'
adas_pid=$(podman inspect --format '{{.State.Pid}}' apollo-adas)
qm_pid=$(podman inspect --format '{{.State.Pid}}' qm)
grep -E '^Cpus_allowed_list:[[:space:]]+1$' "/proc/$adas_pid/status"
grep -E '^Cpus_allowed_list:[[:space:]]+2-3$' "/proc/$qm_pid/status"
systemctl show apollo-asil-b.slice qm.service -p AllowedCPUs -p MemoryMax -p CPUWeight
ps -eZ | grep -E '(workload|bluechi)'
cat /run/apollo-safety/state.json
echo AUTOMOTIVE_SCENARIO_HEALTHY_PASS

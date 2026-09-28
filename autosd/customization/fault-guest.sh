#!/usr/bin/env bash
# Destructive to the DEMO workload only. Explicitly invoked on a private guest.
set -euo pipefail
systemctl is-active --quiet apollo-safety-monitor
podman exec apollo-adas /workload health /run/heartbeat
podman kill --signal STOP apollo-adas
for ((i=0; i<90; i++)); do
    if python3 -c 'import json,sys; sys.exit(json.load(open("/run/apollo-safety/state.json"))["state"] != "FAULT_LATCHED")'; then
        break
    fi
    sleep 1
done
python3 -c 'import json; assert json.load(open("/run/apollo-safety/state.json"))["state"] == "FAULT_LATCHED"'
for ((i=0; i<60; i++)); do
    state=$(systemctl show apollo-adas -p ActiveState --value)
    [[ "$state" = inactive || "$state" = failed ]] && break
    sleep 1
done
[[ "$state" = inactive || "$state" = failed ]]
# SIGSTOP prevents graceful termination: exit-code/failed is expected after
# Podman's bounded stop escalates to SIGKILL. Prove no ADAS container survives.
test -z "$(podman ps -q --filter 'name=^apollo-adas$')"
systemctl show apollo-adas -p ActiveState -p SubState -p Result
podman exec qm systemctl is-active --quiet apollo-qm-app
podman exec qm systemctl is-active --quiet apollo-qm-container
test "$(getenforce)" = Enforcing
journalctl -b -u apollo-safety-monitor -u apollo-adas --no-pager -n 60
cat /run/apollo-safety/state.json
echo AUTOMOTIVE_SCENARIO_FAULT_PASS

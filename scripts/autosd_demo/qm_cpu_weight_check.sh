#!/usr/bin/env bash
# Read back cgroup v2 scheduler controls; does not measure bandwidth or latency.
set -euo pipefail
systemctl is-active --quiet qm
previous=$(systemctl show qm -p CPUWeight --value)
case "$previous" in idle|[0-9]*) ;; *) echo "Unexpected CPUWeight: $previous"; exit 1;; esac
trap 'systemctl set-property --runtime qm.service "CPUWeight=$previous"' EXIT
systemctl set-property --runtime qm.service CPUWeight=50
test "$(systemctl show qm -p CPUWeight --value)" = 50
cgroup=$(systemctl show qm -p ControlGroup --value)
test "$cgroup" = /qm.service
printf 'CPUWeight=%s cpu.weight=%s cpu.idle=%s\n' \
    "$(systemctl show qm -p CPUWeight --value)" \
    "$(cat "/sys/fs/cgroup$cgroup/cpu.weight")" \
    "$(cat "/sys/fs/cgroup$cgroup/cpu.idle")"
test "$(cat "/sys/fs/cgroup$cgroup/cpu.weight")" = 50
test "$(cat "/sys/fs/cgroup$cgroup/cpu.idle")" = 0
echo 'QM_CPU_WEIGHT_READBACK_PASS (not a 50-percent CPU quota or timing qualification)'

#!/usr/bin/env bash
# Check actual root Podman task placement, not QM real-time isolation.
set -euo pipefail
trap 'printf "RESULT root_container_cpu_affinity FAIL\n"' ERR
image=${1:-docker.io/library/alpine:3.22}
printf 'ONLINE_CPUS='
cat /sys/devices/system/cpu/online
getenforce
podman image exists "$image" || {
    printf 'RESULT root_container_cpu_affinity BLOCKED image_missing\n'
    exit 2
}
timeout --kill-after=5 60 podman run --rm --pull=never --network=none \
    --cpuset-cpus=0 "$image" sh -ec '
        cat /proc/self/status
        cpus=$(sed -n "s/^Cpus_allowed_list:[[:space:]]*//p" /proc/self/status)
        test "$cpus" = 0
        echo RESULT root_container_cpu_affinity PASS
    '
printf 'SCOPE root_Podman_cpuset_only; QM_CPUWeight_deadlines_interference_unverified\n'

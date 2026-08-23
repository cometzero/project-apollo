from __future__ import annotations

from typing import Final


GUEST_PROBE_PATH: Final = "/tmp/qbox-cpuidle-probe"
CHUNK_SIZE: Final = 480
GUEST_PROBE: Final = r"""#!/bin/sh
set -eu
cpu_root=/sys/devices/system/cpu
idle_root=$cpu_root/cpuidle
cpus='0 1 2 3'
entries='state0:WFI:1:1 state1:cpu-sleep:4200:4000 state2:cluster-sleep:4500:4200'
mode=$1
case $mode in
ensure)
    test -d $idle_root
    test -r $idle_root/available_governors
    test -r $idle_root/current_governor_ro
    test -r $idle_root/current_governor
    test $(nproc --all) -eq 4
    test $(cat /etc/nexios-bsp-cpus) -eq 4
    count=0
    for cpu in $cpus; do
        for entry in $entries; do
            state=${entry%%:*}
            base=$cpu_root/cpu$cpu/cpuidle/$state
            test -d $base
            for node in name residency latency usage time disable; do
                test -r $base/$node
            done
            count=$((count+1))
        done
    done
    printf 'CPUIDLE_ENSURE cpu_count=4 states=%s\n' $count
    ;;
cstates)
    for cpu in $cpus; do
        for entry in $entries; do
            state=${entry%%:*}; rest=${entry#*:}; name=${rest%%:*}
            base=$cpu_root/cpu$cpu/cpuidle/$state
            actual=$(cat $base/name); test x$actual = x$name
            printf 'CPUIDLE_CSTATE cpu=%s state=%s name=%s\n' $cpu $state $actual
        done
    done
    ;;
defaults)
    for cpu in $cpus; do
        for entry in $entries; do
            state=${entry%%:*}; base=$cpu_root/cpu$cpu/cpuidle/$state
            test -r $base/default_status
            value=$(cat $base/default_status); test x$value = xenabled
            printf 'CPUIDLE_DEFAULT cpu=%s state=%s value=%s\n' $cpu $state $value
        done
    done
    ;;
disable)
    cpu=$2; state=$3; peer=$(((cpu+1)%4))
    base=$cpu_root/cpu$cpu/cpuidle/$state
    peer_base=$cpu_root/cpu$peer/cpuidle/$state
    before=$(cat $base/disable); peer_before=$(cat $peer_base/disable)
    test x$before = x0; test x$peer_before = x0
    restore_one() {
        rc=$?; set +e; printf '%s\n' $before > $base/disable
        actual=$(cat $base/disable); trap - EXIT
        test x$actual = x$before || exit 97; exit $rc
    }
    trap restore_one EXIT
    printf '1\n' > $base/disable
    after_write=$(cat $base/disable); test x$after_write = x1
    sleep 0.5; base_u=$(cat $base/usage); base_t=$(cat $base/time)
    sleep 0.5; s0u=$(cat $base/usage); s0t=$(cat $base/time)
    sleep 0.5; s1u=$(cat $base/usage); s1t=$(cat $base/time)
    test $s0u -eq $base_u -a $s0t -eq $base_t
    test $s1u -eq $base_u -a $s1t -eq $base_t
    peer_after=$(cat $peer_base/disable); test x$peer_after = x$peer_before
    trap - EXIT; printf '%s\n' $before > $base/disable
    restored=$(cat $base/disable); test x$restored = x$before
    printf 'CPUIDLE_DISABLE cpu=%s state=%s before=%s after_write=%s baseline_usage=%s baseline_time=%s sample0_usage=%s sample0_time=%s sample1_usage=%s sample1_time=%s peer_disable_before=%s peer_disable_after=%s restored=%s\n' $cpu $state $before $after_write $base_u $base_t $s0u $s0t $s1u $s1t $peer_before $peer_after $restored
    ;;
residency)
    cpu=$2; state=$3; expected_res=$4; expected_lat=$5; limit=$6
    base=$cpu_root/cpu$cpu/cpuidle/$state
    test x$(cat $base/residency) = x$expected_res
    test x$(cat $base/latency) = x$expected_lat
    save=/tmp/qbox-cpuidle-disable.$$
    : > $save
    for c in $cpus; do
        for entry in $entries; do
            s=${entry%%:*}; b=$cpu_root/cpu$c/cpuidle/$s
            printf '%s %s %s\n' $c $s $(cat $b/disable) >> $save
        done
    done
    restore_all() {
        while read c s value; do
            b=$cpu_root/cpu$c/cpuidle/$s
            printf '%s\n' $value > $b/disable
            test x$(cat $b/disable) = x$value
        done < $save
    }
    cleanup_all() {
        rc=$?; set +e; restore_all; rm -f $save; trap - EXIT; exit $rc
    }
    trap cleanup_all EXIT
    case $state in
    state0)
        printf '0\n' > $cpu_root/cpu$cpu/cpuidle/state0/disable
        printf '1\n' > $cpu_root/cpu$cpu/cpuidle/state1/disable
        printf '1\n' > $cpu_root/cpu$cpu/cpuidle/state2/disable
        ;;
    state1)
        printf '1\n' > $cpu_root/cpu$cpu/cpuidle/state0/disable
        printf '0\n' > $cpu_root/cpu$cpu/cpuidle/state1/disable
        printf '1\n' > $cpu_root/cpu$cpu/cpuidle/state2/disable
        ;;
    state2)
        cluster=$(cat $cpu_root/cpu$cpu/topology/cluster_id)
        for c in $cpus; do
            test x$(cat $cpu_root/cpu$c/topology/cluster_id) = x$cluster || continue
            printf '1\n' > $cpu_root/cpu$c/cpuidle/state0/disable
            printf '1\n' > $cpu_root/cpu$c/cpuidle/state1/disable
            printf '0\n' > $cpu_root/cpu$c/cpuidle/state2/disable
        done
        ;;
    esac
    before_u=$(cat $base/usage); before_t=$(cat $base/time)
    tries=0; after_u=$before_u; after_t=$before_t
    while test $tries -lt $limit; do
        sleep 1
        after_u=$(cat $base/usage); after_t=$(cat $base/time)
        test $after_u -le $before_u -o $after_t -le $before_t || break
        tries=$((tries+1))
    done
    restore_all; trap - EXIT; rm -f $save
    printf 'CPUIDLE_RESIDENCY cpu=%s state=%s residency=%s latency=%s usage_before=%s usage_after=%s time_before=%s time_after=%s wake=natural-timer restored=1\n' $cpu $state $expected_res $expected_lat $before_u $after_u $before_t $after_t
    test $after_u -gt $before_u; test $after_t -gt $before_t
    ;;
governors)
    available=$(cat $idle_root/available_governors)
    current=$(cat $idle_root/current_governor)
    current_ro=$(cat $idle_root/current_governor_ro)
    test x"$available" = x"menu teo"; test x$current = x$current_ro
    csv=$(printf '%s' "$available" | tr ' ' ',')
    printf 'CPUIDLE_GOVERNORS available=%s current=%s current_ro=%s\n' $csv $current $current_ro
    ;;
switch)
    path=$idle_root/current_governor; original=$(cat $path)
    restore_gov() {
        rc=$?; set +e; printf '%s\n' $original > $path
        actual=$(cat $path); actual_ro=$(cat $idle_root/current_governor_ro)
        trap - EXIT
        test x$actual = x$original -a x$actual_ro = x$original || exit 97
        exit $rc
    }
    trap restore_gov EXIT
    for requested in $(cat $idle_root/available_governors); do
        printf '%s\n' $requested > $path
        current=$(cat $path); current_ro=$(cat $idle_root/current_governor_ro)
        test x$current = x$requested -a x$current_ro = x$requested
        printf 'CPUIDLE_SWITCH requested=%s current=%s current_ro=%s\n' $requested $current $current_ro
    done
    trap - EXIT; printf '%s\n' $original > $path
    current=$(cat $path); current_ro=$(cat $idle_root/current_governor_ro)
    test x$current = x$original -a x$current_ro = x$original
    printf 'CPUIDLE_SWITCH_RESTORE original=%s current=%s current_ro=%s restored=1\n' $original $current $current_ro
    ;;
invalid)
    path=$idle_root/current_governor; original=$(cat $path)
    restore_gov() {
        rc=$?; set +e; printf '%s\n' $original > $path; trap - EXIT; exit $rc
    }
    trap restore_gov EXIT; rejected=0
    printf '%s\n' invalid-governor-name > $path 2>/dev/null || rejected=1
    current=$(cat $path); current_ro=$(cat $idle_root/current_governor_ro)
    test $rejected -eq 1; test x$current = x$original; test x$current_ro = x$original
    disable_zero=0
    for c in $cpus; do
        for entry in $entries; do
            state=${entry%%:*}
            test x$(cat $cpu_root/cpu$c/cpuidle/$state/disable) = x0
            disable_zero=$((disable_zero+1))
        done
    done
    test $disable_zero -eq 12
    trap - EXIT; printf '%s\n' $original > $path
    printf 'CPUIDLE_INVALID rejected=1 original=%s current=%s current_ro=%s disable_zero=%s restored=1\n' $original $(cat $path) $(cat $idle_root/current_governor_ro) $disable_zero
    rm -f "$0"
    ;;
esac
"""


def guest_probe_install_commands() -> tuple[str, ...]:
    encoded = "".join(f"\\{byte:03o}" for byte in GUEST_PROBE.encode("utf-8"))
    chunks = tuple(
        encoded[offset : offset + CHUNK_SIZE]
        for offset in range(0, len(encoded), CHUNK_SIZE)
    )
    create = f": > {GUEST_PROBE_PATH}"
    append = tuple(
        f"printf %b '{chunk}' >> {GUEST_PROBE_PATH}" for chunk in chunks
    )
    finish = f"chmod 700 {GUEST_PROBE_PATH}"
    return (create, *append, finish)

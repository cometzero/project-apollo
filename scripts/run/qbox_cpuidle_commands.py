from __future__ import annotations

from typing import Final


CPU_ROOT: Final = "/sys/devices/system/cpu"
IDLE_ROOT: Final = f"{CPU_ROOT}/cpuidle"
CPUS: Final = "0 1 2 3"
ENTRIES: Final = (
    "state0:WFI:1:1 state1:cpu-sleep:4200:4000 state2:cluster-sleep:4500:4200"
)


def _wrap(body: str) -> str:
    return (
        f"( set -eu; cpu_root={CPU_ROOT}; idle_root={IDLE_ROOT}; "
        f"cpus='{CPUS}'; entries='{ENTRIES}'; {body} )"
    )


def _read_only_commands() -> tuple[str, str, str]:
    ensure = _wrap(
        "test -d $idle_root; test -r $idle_root/available_governors; "
        "test -r $idle_root/current_governor_ro; "
        "test -r $idle_root/current_governor; test $(nproc --all) -eq 4; "
        "test $(cat /etc/nexios-bsp-cpus) -eq 4; count=0; "
        "for cpu in $cpus; do for entry in $entries; do "
        "state=${entry%%:*}; base=$cpu_root/cpu$cpu/cpuidle/$state; "
        "test -d $base; for node in name residency latency usage time disable; "
        "do test -r $base/$node; done; count=$((count+1)); done; done; "
        "printf 'CPUIDLE_ENSURE cpu_count=4 states=%s\\n' $count"
    )
    cstates = _wrap(
        "for cpu in $cpus; do for entry in $entries; do "
        "state=${entry%%:*}; rest=${entry#*:}; name=${rest%%:*}; "
        "base=$cpu_root/cpu$cpu/cpuidle/$state; actual=$(cat $base/name); "
        "test x$actual = x$name; "
        "printf 'CPUIDLE_CSTATE cpu=%s state=%s name=%s\\n' "
        "$cpu $state $actual; done; done"
    )
    defaults = _wrap(
        "for cpu in $cpus; do for entry in $entries; do "
        "state=${entry%%:*}; base=$cpu_root/cpu$cpu/cpuidle/$state; "
        "value=absent; if test -e $base/default_status; then "
        "value=$(cat $base/default_status); test x$value = xenabled; fi; "
        "printf 'CPUIDLE_DEFAULT cpu=%s state=%s value=%s\\n' "
        "$cpu $state $value; done; done"
    )
    return ensure, cstates, defaults


def _disable_command() -> str:
    return _wrap(
        "for cpu in $cpus; do for entry in $entries; do "
        "state=${entry%%:*}; base=$cpu_root/cpu$cpu/cpuidle/$state; "
        "before=$(cat $base/disable); test x$before = x0; "
        "restore_one() { rc=$?; set +e; printf '%s\\n' $before > $base/disable; "
        "actual=$(cat $base/disable); trap - EXIT; test x$actual = x$before "
        "|| exit 97; exit $rc; }; trap restore_one EXIT; "
        "printf '1\\n' > $base/disable; after_write=$(cat $base/disable); "
        "test x$after_write = x1; prev_u=$(cat $base/usage); "
        "prev_t=$(cat $base/time); stable=0; tries=0; "
        "while test $stable -lt 2 -a $tries -lt 40; do sleep 0.25; "
        "cur_u=$(cat $base/usage); cur_t=$(cat $base/time); "
        "if test $cur_u -eq $prev_u -a $cur_t -eq $prev_t; then "
        "stable=$((stable+1)); else stable=0; fi; prev_u=$cur_u; "
        "prev_t=$cur_t; tries=$((tries+1)); done; test $stable -eq 2; "
        "base_u=$prev_u; base_t=$prev_t; sleep 0.25; "
        "s0u=$(cat $base/usage); s0t=$(cat $base/time); sleep 0.25; "
        "s1u=$(cat $base/usage); s1t=$(cat $base/time); "
        "test $s0u -eq $base_u -a $s0t -eq $base_t; "
        "test $s1u -eq $base_u -a $s1t -eq $base_t; trap - EXIT; "
        "printf '%s\\n' $before > $base/disable; restored=$(cat $base/disable); "
        "test x$restored = x$before; printf 'CPUIDLE_DISABLE cpu=%s "
        "state=%s before=%s after_write=%s baseline_usage=%s "
        "baseline_time=%s sample0_usage=%s sample0_time=%s "
        "sample1_usage=%s sample1_time=%s restored=%s\\n' $cpu $state "
        "$before $after_write $base_u $base_t $s0u $s0t $s1u $s1t "
        "$restored; done; done"
    )


def _residency_command() -> str:
    return _wrap(
        "save=/tmp/qbox-cpuidle-disable.$$; : > $save; "
        "snapshot_all() { : > $save; for c in $cpus; do for e in $entries; "
        "do s=${e%%:*}; b=$cpu_root/cpu$c/cpuidle/$s; "
        "printf '%s %s %s\\n' $c $s $(cat $b/disable) >> $save; "
        "done; done; }; restore_all() { while read c s value; do "
        "b=$cpu_root/cpu$c/cpuidle/$s; printf '%s\\n' $value > $b/disable; "
        "test x$(cat $b/disable) = x$value; done < $save; : > $save; }; "
        "cleanup_all() { rc=$?; set +e; restore_all; rm -f $save; "
        "trap - EXIT; exit $rc; }; trap cleanup_all EXIT; "
        "for cpu in $cpus; do for entry in $entries; do "
        "state=${entry%%:*}; rest=${entry#*:}; name=${rest%%:*}; "
        "rest=${rest#*:}; expected_res=${rest%%:*}; expected_lat=${rest#*:}; "
        "base=$cpu_root/cpu$cpu/cpuidle/$state; "
        "test x$(cat $base/residency) = x$expected_res; "
        "test x$(cat $base/latency) = x$expected_lat; snapshot_all; "
        "case $state in state0) limit=30 ;; state1) limit=30; "
        "printf '1\\n' > $cpu_root/cpu$cpu/cpuidle/state0/disable; "
        "printf '0\\n' > $cpu_root/cpu$cpu/cpuidle/state1/disable; "
        "printf '1\\n' > $cpu_root/cpu$cpu/cpuidle/state2/disable ;; "
        "state2) limit=90; cluster=$(cat $cpu_root/cpu$cpu/topology/cluster_id); "
        "for c in $cpus; do test x$(cat $cpu_root/cpu$c/topology/cluster_id) "
        "= x$cluster || continue; printf '1\\n' > "
        "$cpu_root/cpu$c/cpuidle/state0/disable; printf '1\\n' > "
        "$cpu_root/cpu$c/cpuidle/state1/disable; printf '0\\n' > "
        "$cpu_root/cpu$c/cpuidle/state2/disable; done ;; esac; "
        "before_u=$(cat $base/usage); before_t=$(cat $base/time); tries=0; "
        "after_u=$before_u; after_t=$before_t; while test $tries -lt $limit; "
        "do sleep 1; after_u=$(cat $base/usage); after_t=$(cat $base/time); "
        "test $after_u -le $before_u -o $after_t -le $before_t || break; "
        "tries=$((tries+1)); done; restore_all; "
        "printf 'CPUIDLE_RESIDENCY cpu=%s state=%s residency=%s latency=%s "
        "usage_before=%s usage_after=%s time_before=%s time_after=%s "
        "restored=1\\n' $cpu $state $expected_res $expected_lat $before_u "
        "$after_u $before_t $after_t; test $after_u -gt $before_u; "
        "test $after_t -gt $before_t; done; done; trap - EXIT; rm -f $save"
    )


def _governor_commands() -> tuple[str, str, str]:
    governors = _wrap(
        "available=$(cat $idle_root/available_governors); "
        "current=$(cat $idle_root/current_governor); "
        "current_ro=$(cat $idle_root/current_governor_ro); "
        "case ' '$available' ' in *' '$current' '*) ;; *) exit 1 ;; esac; "
        "test x$current = x$current_ro; csv=$(printf '%s' \"$available\" | tr ' ' ','); "
        "printf 'CPUIDLE_GOVERNORS available=%s current=%s current_ro=%s\\n' "
        "$csv $current $current_ro"
    )
    switching = _wrap(
        "path=$idle_root/current_governor; original=$(cat $path); "
        "restore_gov() { rc=$?; set +e; printf '%s\\n' $original > $path; "
        "actual=$(cat $path); actual_ro=$(cat $idle_root/current_governor_ro); "
        "trap - EXIT; test x$actual = x$original -a x$actual_ro = x$original "
        "|| exit 97; exit $rc; }; trap restore_gov EXIT; "
        "for requested in $(cat $idle_root/available_governors); do "
        "printf '%s\\n' $requested > $path; current=$(cat $path); "
        "current_ro=$(cat $idle_root/current_governor_ro); "
        "test x$current = x$requested -a x$current_ro = x$requested; "
        "printf 'CPUIDLE_SWITCH requested=%s current=%s current_ro=%s\\n' "
        "$requested $current $current_ro; done; trap - EXIT; "
        "printf '%s\\n' $original > $path; current=$(cat $path); "
        "current_ro=$(cat $idle_root/current_governor_ro); "
        "test x$current = x$original -a x$current_ro = x$original; "
        "printf 'CPUIDLE_SWITCH_RESTORE original=%s current=%s "
        "current_ro=%s restored=1\\n' $original $current $current_ro"
    )
    invalid = _wrap(
        "path=$idle_root/current_governor; original=$(cat $path); "
        "restore_gov() { rc=$?; set +e; printf '%s\\n' $original > $path; "
        "trap - EXIT; exit $rc; }; trap restore_gov EXIT; rejected=0; "
        "printf '%s\\n' invalid-governor-name > $path 2>/dev/null || rejected=1; "
        "current=$(cat $path); current_ro=$(cat $idle_root/current_governor_ro); "
        "test $rejected -eq 1; test x$current = x$original; "
        "test x$current_ro = x$original; trap - EXIT; "
        "printf '%s\\n' $original > $path; "
        "printf 'CPUIDLE_INVALID rejected=1 original=%s current=%s "
        "current_ro=%s restored=1\\n' $original $(cat $path) "
        "$(cat $idle_root/current_governor_ro)"
    )
    return governors, switching, invalid


def cpuidle_probe_commands() -> tuple[str, ...]:
    return (
        *_read_only_commands(),
        _disable_command(),
        _residency_command(),
        *_governor_commands(),
    )

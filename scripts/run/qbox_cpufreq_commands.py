from __future__ import annotations

from typing import Final


CPUFREQ_ROOT: Final = "/sys/devices/system/cpu/cpufreq"
GOVERNORS: Final = "ondemand performance powersave schedutil"
OPPS: Final = "1800000 2000000 2500000"


def _wrap(body: str) -> str:
    return (
        f"( set -eu; root={CPUFREQ_ROOT}; governors='{GOVERNORS}'; "
        f"opps='{OPPS}'; cpu_count=$(nproc --all); "
        "test $cpu_count -eq 4 -o $cpu_count -eq 16; "
        "policies=$(for first in $(seq 0 4 $((cpu_count-1))); do "
        "printf 'policy%s ' $first; done); "
        f"{body} )"
    )


def _mutate(body: str) -> str:
    return _wrap(
        "snapshots=$(for policy in $policies; do path=$root/$policy; "
        "printf '%s|%s|%s|%s\\n' $policy $(cat $path/scaling_governor) "
        "$(cat $path/scaling_min_freq) $(cat $path/scaling_max_freq); done); "
        "cleanup() { printf '%s\\n' \"$snapshots\" | "
        "while IFS='|' read policy governor minimum maximum; do "
        "path=$root/$policy; printf '%s\\n' $maximum > $path/scaling_max_freq; "
        "printf '%s\\n' $minimum > $path/scaling_min_freq; "
        "printf '%s\\n' $governor > $path/scaling_governor; "
        "test x$(cat $path/scaling_governor) = x$governor; "
        "test x$(cat $path/scaling_min_freq) = x$minimum; "
        "test x$(cat $path/scaling_max_freq) = x$maximum; "
        "printf 'CPUFREQ_RESTORE policy=%s governor=%s min=%s max=%s restored=1\\n' "
        "$policy $governor $minimum $maximum; done; }; "
        "trap 'body_rc=$?; set +e; cleanup; cleanup_rc=$?; trap - EXIT; "
        "test $body_rc -eq 0 || exit $body_rc; exit $cleanup_rc' EXIT; " + body
    )


def cpufreq_probe_commands() -> tuple[str, ...]:
    policy = _wrap(
        "test -d $root; actual=$(for path in $root/policy*; do "
        "test -d $path && basename $path; done | sort -V | xargs); "
        "test x$actual = x$(printf '%s\\n' $policies | xargs); "
        "for policy in $policies; do path=$root/$policy; "
        "available=$(cat $path/scaling_available_governors | xargs | tr ' ' ','); "
        "freqs=$(cat $path/scaling_available_frequencies | xargs | tr ' ' ','); "
        "affected=$(cat $path/affected_cpus | xargs | tr ' ' ','); "
        "printf 'CPUFREQ_POLICY policy=%s governors=%s frequencies=%s "
        "driver=%s affected=%s min=%s max=%s current=%s\\n' $policy "
        "$available $freqs $(cat $path/scaling_driver) $affected "
        "$(cat $path/scaling_min_freq) $(cat $path/scaling_max_freq) "
        "$(cat $path/scaling_cur_freq); done; "
        "printf 'CPUFREQ_META cpu_count=%s guest_contract=identical "
        "performance_coupling=unsupported\\n' $cpu_count"
    )
    defaults = _wrap(
        "for policy in $policies; do value=$(cat $root/$policy/scaling_governor); "
        "test x$value = xschedutil; printf 'CPUFREQ_DEFAULT policy=%s "
        "governor=%s\\n' $policy $value; done"
    )
    set_governors = _mutate(
        "for policy in $policies; do path=$root/$policy; for governor in "
        "$governors; do printf '%s\\n' $governor > $path/scaling_governor; "
        "actual=$(cat $path/scaling_governor); test x$actual = x$governor; "
        "printf 'CPUFREQ_GOVERNOR policy=%s requested=%s actual=%s\\n' "
        "$policy $governor $actual; done; done"
    )
    driver = _wrap(
        "for policy in $policies; do value=$(cat $root/$policy/scaling_driver); "
        "test x$value = xscmi; printf 'CPUFREQ_DRIVER policy=%s driver=%s\\n' "
        "$policy $value; done"
    )
    current = _mutate(
        "for policy in $policies; do path=$root/$policy; for governor in "
        "$governors; do printf '%s\\n' $governor > $path/scaling_governor; "
        'frequency=$(cat $path/scaling_cur_freq); case " $opps " in '
        '*" $frequency "*) ;; *) exit 1;; esac; printf \'CPUFREQ_CURRENT '
        "policy=%s governor=%s frequency=%s\\n' $policy $governor $frequency; "
        "done; done"
    )
    affected = _wrap(
        "for policy in $policies; do first=${policy#policy}; expected=$(seq "
        "$first $((first+3)) | xargs | tr ' ' ','); actual=$(cat "
        "$root/$policy/affected_cpus | xargs | tr ' ' ','); "
        "test x$actual = x$expected; printf 'CPUFREQ_AFFECTED policy=%s "
        "cpus=%s\\n' $policy $actual; done"
    )
    invalid_governor = _mutate(
        "for policy in $policies; do path=$root/$policy; before=$(cat "
        "$path/scaling_governor); rejected=0; printf '%s\\n' invalid-governor "
        "> $path/scaling_governor || rejected=1; after=$(cat "
        "$path/scaling_governor); test $rejected -eq 1 -a x$after = x$before; "
        "printf 'CPUFREQ_INVALID_GOVERNOR policy=%s rejected=%s unchanged=1\\n' "
        "$policy $rejected; done"
    )
    minimum = _mutate(
        "for policy in $policies; do path=$root/$policy; for frequency in "
        "$opps; do printf '%s\\n' 2500000 > $path/scaling_max_freq; "
        "printf '%s\\n' $frequency > $path/scaling_min_freq; "
        "test x$(cat $path/scaling_min_freq) = x$frequency; printf "
        "'CPUFREQ_MIN policy=%s frequency=%s applied=1\\n' $policy $frequency; "
        "done; done"
    )
    maximum = _mutate(
        "for policy in $policies; do path=$root/$policy; for frequency in "
        "$opps; do printf '%s\\n' 1800000 > $path/scaling_min_freq; "
        "printf '%s\\n' $frequency > $path/scaling_max_freq; "
        "test x$(cat $path/scaling_max_freq) = x$frequency; printf "
        "'CPUFREQ_MAX policy=%s frequency=%s applied=1\\n' $policy $frequency; "
        "done; done"
    )
    negative = _mutate(
        "for policy in $policies; do path=$root/$policy; minimum=$(cat "
        "$path/scaling_min_freq); maximum=$(cat $path/scaling_max_freq); "
        "rejected_min=0; rejected_max=0; printf '%s\\n' $((maximum+100000)) "
        "> $path/scaling_min_freq || rejected_min=1; printf '%s\\n' "
        "$((minimum-100000)) > $path/scaling_max_freq || rejected_max=1; "
        "test $(cat $path/scaling_min_freq) -le $(cat "
        "$path/scaling_max_freq); printf 'CPUFREQ_NEGATIVE policy=%s "
        "rejected_min=%s rejected_max=%s unchanged=1\\n' $policy "
        "$rejected_min $rejected_max; done"
    )
    return (
        policy,
        defaults,
        set_governors,
        driver,
        current,
        affected,
        invalid_governor,
        minimum,
        maximum,
        negative,
    )

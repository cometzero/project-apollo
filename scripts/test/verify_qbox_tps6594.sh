#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Guest-side TPS6594 board-component qualification for Apollo QVP/QBox.
# Run as root after the QBox BSP has booted:
#   ./scripts/run/ssh_run.sh scripts/test/verify_qbox_tps6594.sh

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

prefix=APOLLO_TPS6594
bus=0
client=0-0048
smd_label=40750000.gpio
smd_hwirq=2

buck_output=/sys/bus/platform/devices/tps6594-buck1-output
ldo_output=/sys/bus/platform/devices/tps6594-ldo1-output
rtc_sys=
tps_chip=
parent_virq=
alarm_virq=
pmic_irq_chip=
buck_initial=
ldo_initial=
loopback_pid=

emit()
{
    printf '%s|v=1|%s\n' "$prefix" "$*"
}

die()
{
    code=$1
    shift
    emit "event=fail|code=$code|reason=$*"
    exit "$code"
}

driver_name()
{
    basename "$(readlink -f "$1/driver")"
}

irq_total()
{
    virq=$1
    cpus=$(grep -c '^processor' /proc/cpuinfo)
    awk -v virq="$virq" -v cpus="$cpus" '
        $1 == virq ":" {
            total = 0
            for (i = 2; i <= cpus + 1; i++) total += $i
            print total
            exit
        }
    ' /proc/interrupts
}

find_parent_irq()
{
    awk -v chip="$smd_label" -v hwirq="$smd_hwirq" '
        {
            for (i = 2; i < NF; i++)
                if ($i == chip && $(i + 1) == hwirq) {
                    if ($NF !~ /^tps6594-.*-0x48$/)
                        next
                    sub(/:$/, "", $1)
                    print $1 "|" $NF
                    exit
                }
        }
    ' /proc/interrupts
}

find_alarm_virq()
{
    chip=$1
    awk -v chip="$chip" '
        $NF == "alarm" {
            for (i = 2; i < NF; i++)
                if ($i == chip) {
                    sub(/:$/, "", $1)
                    print $1
                    exit
                }
        }
    ' \
        /proc/interrupts
}

find_gpiochip()
{
    gpiodetect | awk -v label="[$client]" '$2 == label { print $1; exit }'
}

find_pinctrl()
{
    for candidate in /sys/bus/platform/devices/tps6594-pinctrl*; do
        [ -d "$candidate" ] || continue
        [ "$(driver_name "$candidate")" = tps6594-pinctrl ] || continue
        printf '%s\n' "$candidate"
        return 0
    done
    return 1
}

find_rtc()
{
    for candidate in /sys/class/rtc/rtc*; do
        [ -d "$candidate" ] || continue
        [ "$(driver_name "$candidate/device" 2>/dev/null)" = tps6594-rtc ] ||
            continue
        printf '%s\n' "$candidate"
        return 0
    done
    return 1
}

find_regulator()
{
    wanted=$1
    for candidate in /sys/class/regulator/regulator*; do
        [ -r "$candidate/name" ] || continue
        [ "$(cat "$candidate/name")" = "$wanted" ] || continue
        printf '%s\n' "$candidate"
        return 0
    done
    return 1
}

require_regulators()
{
    required='tps6594-buck1 BUCK2 BUCK3 BUCK4 BUCK5 tps6594-ldo1 LDO2 LDO3 LDO4'
    names=
    for name in $required; do
        path=$(find_regulator "$name") || return 1
        names="${names}${names:+,}$name"
        [ -r "$path/state" ] && [ -r "$path/microvolts" ] || return 1
    done
    emit "event=regulator-inventory|count=9|names=$names"
}

set_output_state()
{
    path=$1
    state=$2
    printf '%s\n' "$state" > "$path/state"
}

test_output()
{
    output=$1
    regulator_name=$2
    expected_uv=$3
    regulator=$(find_regulator "$regulator_name") || return 1

    set_output_state "$output" enabled || return 1
    [ "$(cat "$output/state")" = enabled ] || return 1
    [ "$(cat "$regulator/state")" = enabled ] || return 1
    actual_uv=$(cat "$regulator/microvolts") || return 1
    [ "$actual_uv" = "$expected_uv" ] || return 1
    emit "event=regulator-enable|output=$(basename "$output")|regulator=$regulator_name|state=enabled|microvolts=$actual_uv"

    set_output_state "$output" disabled || return 1
    [ "$(cat "$output/state")" = disabled ] || return 1
    [ "$(cat "$regulator/state")" = disabled ] || return 1
    emit "event=regulator-disable|output=$(basename "$output")|regulator=$regulator_name|state=disabled"
}

wait_for_alarm()
{
    parent_before=$1
    alarm_before=$2
    deadline=$(( $(date +%s) + 10 ))
    while [ "$(date +%s)" -le "$deadline" ]; do
        parent_after=$(irq_total "$parent_virq")
        alarm_after=$(irq_total "$alarm_virq")
        if [ -n "$parent_after" ] && [ -n "$alarm_after" ] &&
                [ "$parent_after" -gt "$parent_before" ] &&
                [ "$alarm_after" -gt "$alarm_before" ]; then
            emit "event=rtc-alarm|parent_before=$parent_before|parent_after=$parent_after|alarm_before=$alarm_before|alarm_after=$alarm_after"
            return 0
        fi
        sleep 1
    done
    return 1
}

arm_alarm()
{
    now=$(cat "$rtc_sys/since_epoch") || return 1
    alarm=$((now + 3))
    printf '%s\n' 0 > "$rtc_sys/wakealarm" || return 1
    printf '%s\n' "$alarm" > "$rtc_sys/wakealarm" || return 1
    emit "event=rtc-alarm-armed|rtc=$(basename "$rtc_sys")|epoch=$alarm"
}

clear_alarm()
{
    printf '%s\n' 0 > "$rtc_sys/wakealarm" || return 1
    [ -z "$(cat "$rtc_sys/wakealarm")" ] || return 1
    emit "event=rtc-alarm-clear|rtc=$(basename "$rtc_sys")"
}

# shellcheck disable=SC2317 # Invoked by the EXIT trap cleanup handler.
stop_loopback()
{
    [ -n "$loopback_pid" ] || return 0
    kill "$loopback_pid" 2>/dev/null || true
    wait "$loopback_pid" 2>/dev/null || true
    loopback_pid=
}

# shellcheck disable=SC2317 # Registered as the EXIT trap handler.
cleanup()
{
    rc=0
    stop_loopback
    [ -z "$rtc_sys" ] || clear_alarm || rc=1
    [ -z "$buck_initial" ] || set_output_state "$buck_output" "$buck_initial" || rc=1
    [ -z "$ldo_initial" ] || set_output_state "$ldo_output" "$ldo_initial" || rc=1
    emit "event=cleanup|rc=$rc"
    return "$rc"
}

# shellcheck disable=SC2317 # Registered as the EXIT trap handler.
on_exit()
{
    status=$?
    trap - EXIT HUP INT TERM
    cleanup || [ "$status" -ne 0 ] || status=1
    if [ "$status" -eq 0 ]; then
        emit "event=final|status=PASS"
    else
        emit "event=final|status=FAIL|rc=$status"
    fi
    exit "$status"
}

trap on_exit EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

for tool in awk basename cat date find gpiodetect gpioget gpioset grep hwclock readlink sleep; do
    command -v "$tool" >/dev/null 2>&1 || die 10 "missing-$tool"
done

[ -d "/sys/bus/i2c/devices/i2c-$bus" ] || die 11 "missing-i2c-$bus"
[ -d "/sys/bus/i2c/devices/$client" ] || die 12 "missing-client-$client"
adapter_path=$(readlink -f "/sys/bus/i2c/devices/i2c-$bus")
adapter_driver=$(driver_name "$(dirname "$adapter_path")")
[ "$adapter_driver" = i2c_designware ] || die 13 "unexpected-i2c-driver-$adapter_driver"
[ "$(driver_name "/sys/bus/i2c/devices/$client")" = tps6594 ] ||
    die 14 "tps6594-not-bound"

tps_chip=$(find_gpiochip)
[ -n "$tps_chip" ] || die 15 "missing-tps6594-gpiochip"
tps_lines=$(gpiodetect | awk -v chip="$tps_chip" '$1 == chip { value = $3; sub(/^\(/, "", value); print value; exit }')
[ "$tps_lines" = 11 ] || die 16 "unexpected-tps6594-gpio-lines-$tps_lines"
pinctrl_device=$(find_pinctrl) || die 17 "missing-tps6594-pinctrl"

if ! [ -d "$buck_output" ] || ! [ -r "$buck_output/state" ]; then
    die 18 "missing-buck1-output"
fi
if ! [ -d "$ldo_output" ] || ! [ -r "$ldo_output/state" ]; then
    die 19 "missing-ldo1-output"
fi
require_regulators || die 20 "missing-tps6594-regulators"
buck_initial=$(cat "$buck_output/state")
ldo_initial=$(cat "$ldo_output/state")

rtc_sys=$(find_rtc) || die 21 "missing-tps6594-rtc"
if ! [ -r "$rtc_sys/since_epoch" ] || ! [ -w "$rtc_sys/wakealarm" ]; then
    die 22 "missing-rtc-sysfs"
fi
parent_info=$(find_parent_irq)
[ -n "$parent_info" ] || die 23 "missing-pl061-hwirq-$smd_hwirq"
parent_virq=${parent_info%%|*}
pmic_irq_chip=${parent_info#*|}
alarm_virq=$(find_alarm_virq "$pmic_irq_chip")
[ -n "$alarm_virq" ] || die 24 "missing-tps6594-alarm-irq"

emit "event=inventory|adapter=i2c-$bus|adapter_driver=$adapter_driver|client=$client|driver=tps6594|gpiochip=$tps_chip|gpio_lines=$tps_lines|pinctrl=$(basename "$pinctrl_device")|pl061_chip=$smd_label|pl061_hwirq=$smd_hwirq|pl061_virq=$parent_virq|pmic_irq_chip=$pmic_irq_chip|rtc=$(basename "$rtc_sys")|rtc_driver=tps6594-rtc|alarm_virq=$alarm_virq"

test_output "$buck_output" tps6594-buck1 900000 ||
    die 24 "buck1-regulator-output-failed"
test_output "$ldo_output" tps6594-ldo1 1800000 ||
    die 25 "ldo1-regulator-output-failed"

gpioset -c "$tps_chip" -C qbox-tps6594-loopback -t 0 -p 500ms 0=1 8=1 &
loopback_pid=$!
sleep 0.1
loopback_value=$(gpioget -c "$tps_chip" --numeric 1 9 2>&1) ||
    die 26 "gpio-loopback-read-failed"
wait "$loopback_pid" 2>/dev/null || die 27 "gpio-loopback-write-failed"
loopback_pid=
[ "$loopback_value" = '1 1' ] || die 28 "gpio-loopback-high-mismatch-$loopback_value"
emit "event=gpio-loopback|outputs=0,8|inputs=1,9|value=$loopback_value"

gpioset -c "$tps_chip" -C qbox-tps6594-loopback -t 0 -p 500ms 0=0 8=0 &
loopback_pid=$!
sleep 0.1
loopback_value=$(gpioget -c "$tps_chip" --numeric 1 9 2>&1) ||
    die 29 "gpio-loopback-low-read-failed"
wait "$loopback_pid" 2>/dev/null || die 30 "gpio-loopback-low-write-failed"
loopback_pid=
[ "$loopback_value" = '0 0' ] || die 31 "gpio-loopback-low-mismatch-$loopback_value"
emit "event=gpio-loopback-low|outputs=0,8|inputs=1,9|value=$loopback_value"

hwclock -w -u -f "/dev/$(basename "$rtc_sys")" || die 32 "rtc-write-failed"
rtc_before=$(cat "$rtc_sys/since_epoch") || die 33 "rtc-read-before-failed"
sleep 2
rtc_after=$(cat "$rtc_sys/since_epoch") || die 34 "rtc-read-after-failed"
[ "$rtc_after" -gt "$rtc_before" ] || die 35 "rtc-did-not-advance"
emit "event=rtc-tick|before=$rtc_before|after=$rtc_after"

parent_before=$(irq_total "$parent_virq")
alarm_before=$(irq_total "$alarm_virq")
if [ -z "$parent_before" ] || [ -z "$alarm_before" ]; then
    die 36 "missing-irq-counters"
fi
arm_alarm || die 37 "rtc-alarm-arm-failed"
wait_for_alarm "$parent_before" "$alarm_before" || die 38 "rtc-alarm-no-irq"
clear_alarm || die 39 "rtc-alarm-clear-failed"

parent_before=$(irq_total "$parent_virq")
alarm_before=$(irq_total "$alarm_virq")
arm_alarm || die 40 "rtc-alarm-rearm-failed"
wait_for_alarm "$parent_before" "$alarm_before" || die 41 "rtc-alarm-repeat-no-irq"
clear_alarm || die 42 "rtc-alarm-repeat-clear-failed"

exit 0

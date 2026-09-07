#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Guest-side PCA9539 board-component qualification for Apollo QVP/QBox.
# Run as root after the QBox BSP has booted:
#   ssh root@<guest> 'sh -s' < scripts/test/verify_qbox_pca9539.sh

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

prefix=APOLLO_PCA9539
bus=0
address=0x74
client=0-0074
eeprom=/sys/bus/i2c/devices/0-0050/eeprom
pca_label=0-0074
smd_label=40750000.gpio
parent_hwirq=1

pca_chip=
smd_chip=
parent_virq=
reset_pid=
monitor_pid=
readback_pid=
monitor_log=/tmp/qbox-pca9539-gpiomon.$$
driver_was_bound=0

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

pca_is_bound()
{
    [ -L "/sys/bus/i2c/devices/$client/driver" ] &&
        [ "$(driver_name "/sys/bus/i2c/devices/$client")" = pca953x ]
}

stop_process()
{
    pid=$1
    [ -n "$pid" ] || return 0
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
}

stop_reset()
{
    stop_process "$reset_pid"
    reset_pid=
}

discover_pca_chip()
{
    pca_detect=$(gpiodetect | awk -v label="[$pca_label]" '$2 == label { print; exit }')
    [ -n "$pca_detect" ] || return 1
    pca_chip=$(printf '%s\n' "$pca_detect" | awk '{ print $1 }')
    pca_lines=$(printf '%s\n' "$pca_detect" | awk '{ value = $3; sub(/^\(/, "", value); print value }')
    [ "$pca_lines" = 16 ]
}

read_eeprom()
{
    od -An -tx1 -N 16 "$eeprom" | tr -d '[:space:]'
}

set_reset()
{
    level=$1
    stop_reset
    gpioset -c "$smd_chip" -C qbox-pca9539-reset "0=$level" &
    reset_pid=$!
    sleep 0.1
    kill -0 "$reset_pid" 2>/dev/null || return 1
    emit "event=reset|level=$level|chip=$smd_chip|line=0"
}

unbind_pca()
{
    pca_is_bound || return 0
    printf '%s\n' "$client" > /sys/bus/i2c/drivers/pca953x/unbind || return 1
    tries=0
    while pca_is_bound && [ "$tries" -lt 10 ]; do
        sleep 0.1
        tries=$((tries + 1))
    done
    ! pca_is_bound
}

bind_pca()
{
    pca_is_bound && return 0
    printf '%s\n' "$client" > /sys/bus/i2c/drivers/pca953x/bind || return 1
    tries=0
    while ! pca_is_bound && [ "$tries" -lt 10 ]; do
        sleep 0.1
        tries=$((tries + 1))
    done
    pca_is_bound
}

find_parent_virq()
{
    # The chained GIC parent is not listed; observe the PL061 IRQ serving PCA9539.
    awk -v chip="$smd_label" -v hwirq="$parent_hwirq" -v client="$client" '
        $NF == client {
            for (i = 2; i < NF; i++)
                if ($i == chip && $(i + 1) == hwirq) {
                    sub(/:$/, "", $1)
                    print $1
                    found = 1
                    exit
                }
        }
        END { exit !found }
    ' /proc/interrupts
}

irq_raw()
{
    awk -v virq="$parent_virq" '$1 == virq ":" { print; exit }' /proc/interrupts
}

irq_total()
{
    cpus=$(grep -c '^processor' /proc/cpuinfo)
    awk -v virq="$parent_virq" -v cpus="$cpus" '
        $1 == virq ":" {
            total = 0
            for (i = 2; i <= cpus + 1; i++) total += $i
            print total
            exit
        }
    ' /proc/interrupts
}

show_monitor()
{
    [ -r "$monitor_log" ] || return 0
    sed "s/^/$prefix|v=1|event=gpiomon|/" "$monitor_log"
}

# shellcheck disable=SC2317 # Invoked from the EXIT trap.
restore_normal()
{
    cleanup_rc=0

    stop_process "$monitor_pid"
    monitor_pid=
    stop_process "$readback_pid"
    readback_pid=

    if [ "$driver_was_bound" -eq 1 ]; then
        unbind_pca || cleanup_rc=1
        set_reset 0 || cleanup_rc=1
        sleep 0.1
        set_reset 1 || cleanup_rc=1
        stop_reset
        bind_pca || cleanup_rc=1
    else
        stop_reset
    fi

    rm -f "$monitor_log"
    emit "event=cleanup|driver_bound=$(pca_is_bound && echo 1 || echo 0)|reset=high|rc=$cleanup_rc"
    return "$cleanup_rc"
}

# shellcheck disable=SC2317 # Registered as the EXIT trap handler.
on_exit()
{
    status=$?
    trap - EXIT HUP INT TERM
    restore_normal || [ "$status" -ne 0 ] || status=1
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

for tool in gpiodetect gpioinfo gpioget gpioset gpiomon i2ctransfer awk od; do
    command -v "$tool" >/dev/null 2>&1 || die 10 "missing-$tool"
done

[ -d "/sys/bus/i2c/devices/i2c-$bus" ] || die 11 "missing-i2c-$bus"
[ -d "/sys/bus/i2c/devices/$client" ] || die 12 "missing-client-$client"
adapter_path=$(readlink -f "/sys/bus/i2c/devices/i2c-$bus")
adapter_driver=$(driver_name "$(dirname "$adapter_path")")
case "$adapter_driver" in
    i2c_designware) ;;
    *) die 13 "unexpected-i2c-driver-$adapter_driver" ;;
esac

discover_pca_chip || die 14 "missing-pca-gpiochip-label-$pca_label"
smd_chip=$(gpiodetect | awk -v label="[$smd_label]" '$2 == label { print $1; exit }')
[ -n "$smd_chip" ] || die 15 "missing-pl061-gpiochip-label-$smd_label"
[ "$pca_lines" = 16 ] || die 16 "pca-gpio-count-$pca_lines"
[ -r "$eeprom" ] || die 17 "missing-eeprom-$eeprom"
eeprom_before=$(read_eeprom) || die 18 "eeprom-read-before-failed"
[ -n "$eeprom_before" ] || die 19 "empty-eeprom-before"

pca_is_bound || die 20 "pca953x-not-bound"
driver_was_bound=1
emit "event=inventory|adapter=i2c-$bus|adapter_driver=$adapter_driver|client=$client|address=$address|driver=pca953x|pca_chip=$pca_chip|pca_lines=$pca_lines|smd_chip=$smd_chip|smd_address=0x40750000|reset_line=0|int_line=1|eeprom=0-0050"

pl061_line=$(gpioinfo -c "$smd_chip" 1 2>&1) || die 18 "pl061-int-line-unavailable"
emit "event=pl061-int-line|raw=$pl061_line"

unbind_pca || die 21 "pca953x-unbind-failed"
set_reset 0 || die 22 "reset-assert-failed"
if i2ctransfer -y "$bus" w1@"$address" 0x00 r2 >/dev/null 2>&1; then
    die 23 "reset-did-not-nack"
fi
emit "event=reset-nack|bus=$bus|address=$address|rc=expected-nack"

set_reset 1 || die 24 "reset-deassert-failed"
stop_reset

check_default()
{
    register=$1
    expected=$2
    actual=$(i2ctransfer -y "$bus" w1@"$address" "$register" r2 2>&1) || return 1
    normalized=$(printf '%s' "$actual" | tr 'A-F' 'a-f' | tr -s ' ')
    emit "event=reset-default|register=$register|expected=$expected|actual=$normalized"
    [ "$normalized" = "$expected" ]
}

check_default 0x02 '0xff 0xff' || die 25 "output-default-mismatch"
check_default 0x04 '0x00 0x00' || die 26 "polarity-default-mismatch"
check_default 0x06 '0xff 0xff' || die 27 "direction-default-mismatch"

bind_pca || die 28 "pca953x-rebind-failed"
discover_pca_chip || die 29 "pca-gpiochip-not-recreated"
eeprom_after=$(read_eeprom) || die 30 "eeprom-read-after-failed"
emit "event=eeprom-readonly|client=0-0050|bytes=16|before=$eeprom_before|after=$eeprom_after"
[ "$eeprom_after" = "$eeprom_before" ] || die 31 "eeprom-content-changed"
emit "event=driver-rebind|client=$client|driver=$(driver_name "/sys/bus/i2c/devices/$client")"

gpioset -c "$pca_chip" -C qbox-pca9539-readback -t 0 -p 500ms 0=1 8=1 &
readback_pid=$!
sleep 0.1
values=$(gpioget -c "$pca_chip" --numeric 1 9 2>&1) || die 32 "loopback-readback-failed"
wait "$readback_pid" 2>/dev/null || die 33 "loopback-output-failed"
readback_pid=
normalized=$(printf '%s' "$values" | tr -s ' ')
emit "event=loopback-readback|outputs=0,8|inputs=1,9|expected=1 1|actual=$normalized"
[ "$normalized" = '1 1' ] || die 34 "loopback-high-mismatch"

gpioset -c "$pca_chip" -C qbox-pca9539-baseline -t 0 -p 100ms 0=0 8=0 ||
    die 35 "loopback-baseline-failed"
sleep 0.1
values=$(gpioget -c "$pca_chip" --numeric 1 9 2>&1) || die 36 "loopback-baseline-read-failed"
normalized=$(printf '%s' "$values" | tr -s ' ')
emit "event=loopback-baseline|outputs=0,8|inputs=1,9|expected=0 0|actual=$normalized"
[ "$normalized" = '0 0' ] || die 37 "loopback-low-mismatch"

parent_virq=$(find_parent_virq) || die 39 "missing-pl061-hwirq-$parent_hwirq"
before_raw=$(irq_raw)
before_total=$(irq_total)
if [ -z "$before_raw" ] || [ -z "$before_total" ]; then
    die 40 "missing-parent-irq-counter"
fi
emit "event=irq-counter|phase=before|chip=$smd_label|virq=$parent_virq|hwirq=$parent_hwirq|total=$before_total|raw=$before_raw"

gpiomon -c "$pca_chip" -C qbox-pca9539-monitor -e both -n 4 \
    --idle-timeout 3s -F 'chip=%c;line=%o;edge=%E;time=%S' 1 9 >"$monitor_log" 2>&1 &
monitor_pid=$!
sleep 0.1
gpioset -c "$pca_chip" -C qbox-pca9539-toggle -t 100ms,100ms,0 0=0 8=0 ||
    die 41 "loopback-toggle-failed"
wait "$monitor_pid" 2>/dev/null || die 42 "gpiomon-failed"
monitor_pid=
show_monitor
edge_count=$(grep -c '^chip=' "$monitor_log" 2>/dev/null || true)
rising_count=$(grep -c 'edge=rising' "$monitor_log" 2>/dev/null || true)
falling_count=$(grep -c 'edge=falling' "$monitor_log" 2>/dev/null || true)
emit "event=gpiomon-summary|expected=4|events=$edge_count|rising=$rising_count|falling=$falling_count"
if [ "$edge_count" -ne 4 ] || [ "$rising_count" -ne 2 ] ||
        [ "$falling_count" -ne 2 ]; then
    die 43 "gpiomon-edge-mismatch"
fi

after_raw=$(irq_raw)
after_total=$(irq_total)
if [ -z "$after_raw" ] || [ -z "$after_total" ]; then
    die 44 "missing-parent-irq-counter-after"
fi
emit "event=irq-counter|phase=after|chip=$smd_label|virq=$parent_virq|hwirq=$parent_hwirq|total=$after_total|raw=$after_raw"
[ "$after_total" -gt "$before_total" ] || die 45 "parent-irq-no-progress"

exit 0

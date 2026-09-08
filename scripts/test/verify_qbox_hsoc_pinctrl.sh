#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Guest-side HSOC PERI0/PERI1 pinctrl qualification for Apollo QVP/QBox.
# Run after a BSP boot with:
#   ./scripts/run/ssh_run.sh scripts/test/verify_qbox_hsoc_pinctrl.sh

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

prefix=APOLLO_HSOC_PINCTRL
base=0x301e0000
bank_base=0x1000
bank_stride=0x1000
pin_config_base=0x40
irq_enable=0x14
irq_pending=0x18
irq_rising=0x1c
irq_falling=0x20
irq_chip=hsoc-peri0
gic_base=366

monitor_pid=
writer_pid=
monitor_log=/tmp/qbox-hsoc-pinctrl-gpiomon.$$
mux_restore_addr=
mux_restore_value=
mmio_tool=
bank1_chip=
bank6_chip=
bank7_chip=
bank12_chip=
bank13_chip=

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

check_contiguous_pins()
{
    pinctrl_instance=$1
    pinctrl_expected=$2
    pinctrl_debug_file=/sys/kernel/debug/pinctrl/$pinctrl_instance/pins
    [ -r "$pinctrl_debug_file" ] || return 1
    awk -v expected="$pinctrl_expected" '
        /^pin [0-9]+ / { if ($2 != count) bad = 1; count++ }
        END { exit bad || count != expected }
    ' "$pinctrl_debug_file" || return 1
    emit "event=logical-pin-ids|controller=$pinctrl_instance|first=0|last=$((pinctrl_expected - 1))|status=PASS"
}

stop_process()
{
    [ -n "$1" ] || return 0
    kill "$1" 2>/dev/null || true
    wait "$1" 2>/dev/null || true
}

read32()
{
    if [ "$mmio_tool" = devmem ]; then
        devmem "$1" 32
    else
        output=$(devmem2 "$1" w) || return 1
        printf '%s\n' "$output" |
            awk '/^(Read|Value) at address/ { print $NF; found = 1; exit }
                 END { exit !found }'
    fi
}

write32()
{
    if [ "$mmio_tool" = devmem ]; then
        devmem "$1" 32 "$2" >/dev/null
    else
        devmem2 "$1" w "$2" >/dev/null
    fi
}

bank_addr()
{
    printf '0x%x\n' "$((base + bank_base + $1 * bank_stride + $2))"
}

pin_addr()
{
    bank_addr "$1" "$((pin_config_base + $2 * 4))"
}

field()
{
    value=$1
    shift=$2
    mask=$3
    printf '%u\n' "$(((value >> shift) & mask))"
}

find_chip()
{
    gpiodetect | awk -v label="[$1]" '$2 == label { print $1; exit }'
}

chip_lines()
{
    gpiodetect | awk -v chip="$1" '$1 == chip { n = $3; sub(/^\(/, "", n); print n; exit }'
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

find_gpio_irq()
{
    chip=$1
    offset=$2
    awk -v chip="$chip" -v offset="$offset" -v controller="$irq_chip" '
        {
            for (i = 2; i < NF; i++)
                if (($i == chip || $i == controller) &&
                    $(i + 1) == offset) {
                    sub(/:$/, "", $1)
                    print $1
                    exit
                }
        }
    ' /proc/interrupts
}

find_gic_irq()
{
    hwirq=$1
    awk -v hwirq="$hwirq" '
        {
            for (i = 2; i < NF; i++)
                if ($(i - 1) ~ /^GIC/ && $i == hwirq) {
                    sub(/:$/, "", $1)
                    print $1
                    exit
                }
        }
    ' /proc/interrupts
}

check_pin_config()
{
    bank=$1
    pin=$2
    expected_mux=$3
    expected_drive=$4
    expected_slew=$5
    addr=$(pin_addr "$bank" "$pin")
    value=$(read32 "$addr") || return 1
    mux=$(field "$value" 0 7)
    drive=$(field "$value" 8 255)
    slew=$(field "$value" 4 1)
    emit "event=pin-config|bank=$bank|pin=$pin|address=$addr|mux=$mux|drive=$drive|slew=$slew"
    [ "$mux" = "$expected_mux" ] && [ "$drive" = "$expected_drive" ] &&
        [ "$slew" = "$expected_slew" ]
}

check_group()
{
    bank=$1
    first=$2
    count=$3
    drive=$4
    slew=$5
    pin=$first
    last=$((first + count))
    while [ "$pin" -lt "$last" ]; do
        check_pin_config "$bank" "$pin" 2 "$drive" "$slew" || return 1
        pin=$((pin + 1))
    done
}

eeprom_read()
{
    od -An -tx1 -N 1 "/sys/bus/i2c/devices/$1-0050/eeprom"
}

test_loopback()
{
    out_chip=$1
    out_line=$2
    in_chip=$3
    in_line=$4
    name=$5

    gpioset -c "$out_chip" -C qbox-hsoc-pinctrl-loop -t 0 -p 500ms \
        "$out_line=1" &
    writer_pid=$!
    writer=$writer_pid
    sleep 0.1
    high=$(gpioget -c "$in_chip" --numeric "$in_line" 2>&1) || {
        stop_process "$writer"
        writer_pid=
        return 1
    }
    wait "$writer" 2>/dev/null || return 1
    writer_pid=
    [ "$high" = 1 ] || return 1

    gpioset -c "$out_chip" -C qbox-hsoc-pinctrl-loop -t 0 -p 500ms \
        "$out_line=0" &
    writer_pid=$!
    writer=$writer_pid
    sleep 0.1
    low=$(gpioget -c "$in_chip" --numeric "$in_line" 2>&1) || {
        stop_process "$writer"
        writer_pid=
        return 1
    }
    wait "$writer" 2>/dev/null || return 1
    writer_pid=
    [ "$low" = 0 ] || return 1
    emit "event=gpio-loopback|name=$name|output=$out_chip:$out_line|input=$in_chip:$in_line|high=$high|low=$low"
}

test_mux_gate()
{
    addr=$(pin_addr 1 2)
    original=$(read32 "$addr") || return 1
    original_number=$((original))
    [ "$(field "$original_number" 0 7)" = 2 ] || return 1
    mux_restore_addr=$addr
    mux_restore_value=$original

    for mux in 0 3 4; do
        modified=$(((original_number & ~7) | mux))
        write32 "$addr" "$(printf '0x%x' "$modified")" || return 1
        if eeprom_read 5 >/dev/null; then
            return 1
        fi
        emit "event=mux-gate|bus=5|bank=1|pin=2|mux=$mux|result=expected-eio"
    done

    write32 "$addr" "$original" || return 1
    mux_restore_addr=
    mux_restore_value=
    eeprom_read 5 >/dev/null
}

test_bank_irq()
{
    bank=$1
    input_chip=$2
    input_line=$3
    output_chip=$4
    output_line=$5
    gic_hwirq=$((gic_base + bank))
    bit=$((1 << input_line))

    gpiomon -c "$input_chip" -C qbox-hsoc-pinctrl-monitor -e both \
        --idle-timeout 3s -F 'chip=%c;line=%o;edge=%E;time=%S' "$input_line" \
        >"$monitor_log" 2>&1 &
    monitor_pid=$!
    sleep 0.1
    leaf_virq=$(find_gpio_irq "$input_chip" "$input_line")
    irq_source=child-gpio
    if [ -z "$leaf_virq" ]; then
        leaf_virq=$(find_gic_irq "$gic_hwirq")
        irq_source=parent-gic
    fi
    [ -n "$leaf_virq" ] || return 1
    before=$(irq_total "$leaf_virq")
    [ -n "$before" ] || return 1
    enable=$(read32 "$(bank_addr "$bank" "$irq_enable")") || return 1
    rising=$(read32 "$(bank_addr "$bank" "$irq_rising")") || return 1
    falling=$(read32 "$(bank_addr "$bank" "$irq_falling")") || return 1
    [ $((enable & bit)) = "$bit" ] || return 1
    [ $((rising & bit)) = "$bit" ] || return 1
    [ $((falling & bit)) = "$bit" ] || return 1

    gpioset -c "$output_chip" -C qbox-hsoc-pinctrl-toggle -t 100ms,100ms,0 \
        "$output_line=0" || return 1
    # The child IRQ disappears from /proc/interrupts when gpiomon closes it.
    tries=0
    while [ "$tries" -lt 20 ]; do
        after=$(irq_total "$leaf_virq")
        pending=$(read32 "$(bank_addr "$bank" "$irq_pending")") || return 1
        if [ -n "$after" ] && [ "$after" -ge "$((before + 2))" ] &&
                [ $((pending & bit)) = 0 ]; then
            break
        fi
        sleep 0.1
        tries=$((tries + 1))
    done
    [ "$tries" -lt 20 ] || return 1
    wait "$monitor_pid" 2>/dev/null || return 1
    monitor_pid=
    edge_count=$(grep -c '^chip=' "$monitor_log" 2>/dev/null || true)
    rising_count=$(grep -c 'edge=rising' "$monitor_log" 2>/dev/null || true)
    falling_count=$(grep -c 'edge=falling' "$monitor_log" 2>/dev/null || true)
    if ! [ "$edge_count" = 2 ] || ! [ "$rising_count" = 1 ] ||
            ! [ "$falling_count" = 1 ]; then
        return 1
    fi
    if [ -z "$after" ] || ! [ "$after" -gt "$before" ]; then
        return 1
    fi
    [ $((pending & bit)) = 0 ] || return 1
    emit "event=irq-config|bank=$bank|pin=$input_line|gic_hwirq=$gic_hwirq|source=$irq_source|virq=$leaf_virq|enable=$enable|rising=$rising|falling=$falling"
    emit "event=irq-ack|bank=$bank|pin=$input_line|source=$irq_source|virq=$leaf_virq|before=$before|after=$after|pending=$pending"
    sed "s/^/$prefix|v=1|event=gpiomon|/" "$monitor_log"
    rm -f "$monitor_log"
}

# shellcheck disable=SC2317 # Registered as the EXIT trap handler.
cleanup()
{
    stop_process "$monitor_pid"
    monitor_pid=
    stop_process "$writer_pid"
    writer_pid=
    if [ -n "$mux_restore_addr" ]; then
        write32 "$mux_restore_addr" "$mux_restore_value" || return 1
    fi
    rm -f "$monitor_log"
}

# shellcheck disable=SC2317 # Registered as the EXIT trap handler.
on_exit()
{
    status=$?
    trap - EXIT HUP INT TERM
    cleanup || [ "$status" -ne 0 ] || status=1
    if [ "$status" -eq 0 ]; then
        emit 'event=final|status=PASS'
    else
        emit "event=final|status=FAIL|rc=$status"
    fi
    exit "$status"
}

trap on_exit EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

for tool in awk gpiodetect gpioget gpioset gpiomon grep od printf rm sleep; do
    command -v "$tool" >/dev/null 2>&1 || die 10 "missing-$tool"
done
if command -v devmem >/dev/null 2>&1; then
    mmio_tool=devmem
elif command -v devmem2 >/dev/null 2>&1; then
    mmio_tool=devmem2
else
    die 10 'missing-devmem-or-devmem2'
fi

id=$(read32 "$base") || die 11 'missing-pinctrl-id'
version=$(read32 "$((base + 4))") || die 12 'missing-pinctrl-version'
banks=$(read32 "$((base + 8))") || die 13 'missing-bank-count'
pins=$(read32 "$((base + 12))") || die 14 'missing-pin-count'
[ "$((id))" = "$((0x48535043))" ] || die 11 'invalid-pinctrl-id'
[ "$((version))" = "$((0x00010000))" ] || die 12 'invalid-pinctrl-version'
[ "$((banks))" = 14 ] || die 13 'invalid-bank-count'
[ "$((pins))" = 56 ] || die 14 'invalid-pin-count'

bank=0
total_pins=0
while [ "$bank" -lt 14 ]; do
    label=peri0_bank$bank
    chip=$(find_chip "$label")
    [ -n "$chip" ] || die 15 "missing-gpiochip-$label"
    actual=$(chip_lines "$chip")
    if [ "$bank" -lt 6 ]; then expected=8; else expected=1; fi
    [ "$actual" = "$expected" ] || die 16 "unexpected-lines-$label-$actual"
    mmio_pins=$(read32 "$(bank_addr "$bank" 0)") || die 17 "missing-bank-mmio-$bank"
    [ "$((mmio_pins))" = "$expected" ] || die 18 "unexpected-bank-mmio-pins-$bank"
    total_pins=$((total_pins + actual))
    emit "event=bank-inventory|bank=$bank|chip=$chip|lines=$actual|mmio_pins=$mmio_pins|gic_hwirq=$((366 + bank))"
    case "$bank" in
        1) bank1_chip=$chip ;;
        6) bank6_chip=$chip ;;
        7) bank7_chip=$chip ;;
        12) bank12_chip=$chip ;;
        13) bank13_chip=$chip ;;
    esac
    bank=$((bank + 1))
done
[ "$total_pins" = 56 ] || die 19 "unexpected-total-pins-$total_pins"

# Default peripheral states from pinctrl.dtsi.
if [ ! -d /sys/kernel/debug/pinctrl ]; then
    mount -t debugfs debugfs /sys/kernel/debug || die 41 'debugfs-unavailable'
fi
check_contiguous_pins 301e0000.pinctrl-hsoc-peri0-pinctrl 56 || die 41 'peri0-pin-ids-not-contiguous'
check_contiguous_pins 301f0000.pinctrl-hsoc-peri1-pinctrl 36 || die 41 'peri1-pin-ids-not-contiguous'
check_group 0 0 8 4 0 || die 20 'i2c0-3-default-pinmux-mismatch'
check_group 1 0 4 4 0 || die 21 'i2c4-5-default-pinmux-mismatch'
check_group 2 0 8 8 1 || die 22 'spi0-1-default-pinmux-mismatch'
check_group 4 0 4 4 0 || die 24 'uart0-1-default-pinmux-mismatch'
for pin in 0 1 2 3 4 5 6 7; do
    check_pin_config 3 "$pin" 0 4 0 || die 23 'peri0-old-spi-pins-not-released'
done
for pin in 4 5 6 7; do
    check_pin_config 4 "$pin" 0 4 0 || die 24 'peri0-old-uart-pins-not-released'
done

bus=0
while [ "$bus" -lt 6 ]; do
    [ -r "/sys/bus/i2c/devices/$bus-0050/eeprom" ] ||
        die 25 "missing-i2c-eeprom-$bus"
    value=$(eeprom_read "$bus") || die 26 "i2c-eeprom-transfer-failed-$bus"
    [ -n "$value" ] || die 27 "empty-i2c-eeprom-transfer-$bus"
    emit "event=i2c-eeprom|bus=$bus|address=0x50|value=$value"
    bus=$((bus + 1))
done

test_mux_gate || die 28 'i2c5-mux-gating-failed'
emit 'event=i2c-mux-restore|bus=5|bank=1|pin=2|mux=2'

test_loopback "$bank1_chip" 4 "$bank1_chip" 5 bank1_4_to_5 ||
    die 29 'gpio-loopback-bank1-4-to-5-failed'
test_loopback "$bank1_chip" 6 "$bank1_chip" 7 bank1_6_to_7 ||
    die 30 'gpio-loopback-bank1-6-to-7-failed'
test_loopback "$bank6_chip" 0 "$bank7_chip" 0 bank6_to_7 ||
    die 31 'gpio-loopback-bank6-to-7-failed'
test_loopback "$bank12_chip" 0 "$bank13_chip" 0 bank12_to_13 ||
    die 32 'gpio-loopback-bank12-to-13-failed'

test_bank_irq 1 "$bank1_chip" 5 "$bank1_chip" 4 ||
    die 33 'bank1-pin5-irq-failed'
test_bank_irq 7 "$bank7_chip" 0 "$bank6_chip" 0 ||
    die 34 'bank7-pin0-irq-failed'
test_bank_irq 13 "$bank13_chip" 0 "$bank12_chip" 0 ||
    die 35 'bank13-pin0-irq-failed'

# PERI1 has independent registers, GPIO ranges, IRQs and peripheral routes.
base=0x301f0000
irq_chip=hsoc-peri1
gic_base=380
count=$(read32 "$((base + 8))") || die 36 'missing-peri1'
[ "$((count))" = 8 ] || die 36 'invalid-peri1-bank-count'
count=$(read32 "$((base + 12))") || die 36 'missing-peri1-pin-count'
[ "$((count))" = 36 ] || die 36 'invalid-peri1-pin-count'
for bank in 0 1 2 3 4 5 6 7; do
    chip=$(find_chip "peri1_bank$bank")
    [ -n "$chip" ] || die 37 "missing-peri1-bank-$bank"
    if [ "$bank" -lt 4 ]; then expected=8; else expected=1; fi
    [ "$(chip_lines "$chip")" = "$expected" ] || die 37 'invalid-peri1-gpio-count'
    count=$(read32 "$(bank_addr "$bank" 0)") || die 37 'missing-peri1-bank-mmio'
    [ "$((count))" = "$expected" ] || die 37 'invalid-peri1-bank-mmio'
    emit "event=bank-inventory|controller=peri1|bank=$bank|chip=$chip|lines=$expected|gic_hwirq=$((gic_base + bank))"
done
check_group 0 0 8 8 1 || die 38 'peri1-spi2-3-default-pinmux-mismatch'
check_group 1 0 4 4 0 || die 38 'peri1-uart2-3-default-pinmux-mismatch'
peri1_bank3=$(find_chip peri1_bank3)
peri1_bank6=$(find_chip peri1_bank6)
peri1_bank7=$(find_chip peri1_bank7)
test_loopback "$peri1_bank3" 0 "$peri1_bank3" 1 peri1_bank3 || die 39 'peri1-bank3-loopback-failed'
test_loopback "$peri1_bank6" 0 "$peri1_bank7" 0 peri1_bank6_to_7 || die 39 'peri1-single-bank-loopback-failed'
test_bank_irq 3 "$peri1_bank3" 1 "$peri1_bank3" 0 || die 40 'peri1-bank3-irq-failed'
test_bank_irq 7 "$peri1_bank7" 0 "$peri1_bank6" 0 || die 40 'peri1-bank7-irq-failed'
emit 'event=unperformed|scope=spi-uart-runtime|reason=covered-by-dedicated-dwc-regression-not-this-pinctrl-gpio-test'
exit 0

#!/bin/sh
# SPDX-License-Identifier: MIT
# Guest-side data checks. Pair this log with AP DMA350 host traces to prove DMA use.
set -eu
export LC_ALL=C

work=$(mktemp -d /tmp/qbox-dma350.XXXXXX)
reader=
spi_owned=0
dma_owned=0
changed_i2c=
saved_margin=
dma_channels=

cleanup()
{
    if [ -n "$reader" ]; then
        kill "$reader" 2>/dev/null || true
        wait "$reader" 2>/dev/null || true
    fi
    exec 3>&- 4>&- 5>&- 6>&-
    for bus in $changed_i2c; do
        cat "$work/i2c-$bus.original" > "/sys/bus/i2c/devices/$bus-0050/eeprom" || return 1
    done
    [ "$spi_owned" = 0 ] || modprobe -r spi_loopback_test
    [ "$dma_owned" = 0 ] || modprobe -r dmatest
    if [ -n "$saved_margin" ]; then
        echo "$saved_margin" > /sys/module/spi/parameters/transfer_timeout_margin_ms
    fi
}

finish()
{
    rc=$?
    trap - EXIT HUP INT TERM
    cleanup || rc=1
    echo "APOLLO_DMA350|result=$rc|artifacts=$work"
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

pattern()
{
    awk -v count="$1" -v salt="$2" 'BEGIN {
        for (i = 0; i < count; i++) printf "%c", (37 * i + salt) % 256;
    }'
}

irq_count()
{
    awk -v channels="$dma_channels" 'BEGIN {
        n = split(channels, names, " ");
        for (i = 1; i <= n; i++) selected[names[i]] = 1;
    }
    /31000000|dma350/ || ($NF in selected) {
        for (i = 2; i <= NF && $i ~ /^[0-9]+$/; i++) total += $i;
    } END { print total + 0; }' /proc/interrupts
}

# Verify the dedicated topology before opening UARTs or borrowing a free
# channel for memory-only self-tests. No peripheral channel is reassigned.
for address in 30100000.i2c 30110000.i2c 30120000.i2c 30130000.i2c \
               30140000.i2c 30150000.i2c 30180000.spi 30190000.spi \
               301c0000.serial 301d0000.serial; do
    node="/sys/bus/platform/devices/$address/of_node"
    [ -d "$node" ]
    [ ! -e "$node/dmas" ]
done
for address in 30160000.spi 30170000.spi 301a0000.serial 301b0000.serial; do
    [ -e "/sys/bus/platform/devices/$address/of_node/dmas" ]
done
channel_count=0
memory_channel=
for channel in /sys/class/dma/dma*chan*; do
    [ -d "$channel" ] || continue
    device=$(readlink -f "$channel/device")
    case "$device" in
        *31000000*)
            channel_count=$((channel_count + 1))
            dma_channels="$dma_channels $(basename "$channel")"
            if [ -z "$memory_channel" ] && [ "$(cat "$channel/in_use")" = 0 ]; then
                memory_channel=$(basename "$channel")
            fi
            ;;
    esac
done
[ "$channel_count" = 8 ]
echo "APOLLO_DMA350|topology=dedicated|channels=8|status=PASS"
[ -n "$memory_channel" ]
[ ! -d /sys/module/dmatest ]
for dma_kind in 0 1; do
    before=$(irq_count)
    dmesg > "$work/dmesg.before"
    modprobe dmatest dmatest="$dma_kind" channel="$memory_channel" iterations=5 test_buf_size=65536 timeout=10000 run=1
    dma_owned=1
    cat /sys/module/dmatest/parameters/wait > "$work/dmatest-$dma_kind.wait"
    dmesg > "$work/dmatest-$dma_kind.log"
    before_lines=$(wc -l < "$work/dmesg.before")
    [ "$(wc -l < "$work/dmatest-$dma_kind.log")" -ge "$before_lines" ]
    tail -n "+$((before_lines + 1))" "$work/dmatest-$dma_kind.log" > "$work/dmatest-$dma_kind.new"
    grep -E "$memory_channel.*summary" "$work/dmatest-$dma_kind.new" > "$work/dmatest-$dma_kind.summary"
    cat "$work/dmatest-$dma_kind.summary"
    if grep -Ev 'summary [1-9][0-9]* tests, 0 failures .*\(0\)$' "$work/dmatest-$dma_kind.summary"; then
        exit 1
    fi
    after=$(irq_count)
    [ "$after" -gt "$before" ]
    echo "APOLLO_DMA350|memory=$memory_channel|mode=$dma_kind|irq_before=$before|irq_after=$after|status=PASS"
    modprobe -r dmatest
    dma_owned=0
done

# at24 keeps the real eight-byte EEPROM page geometry. Reads exceed FIFO depth.
for bus in 0 1 2 3 4 5; do
    eeprom="/sys/bus/i2c/devices/$bus-0050/eeprom"
    [ -r "$eeprom" ] && [ -w "$eeprom" ]
    dd if="$eeprom" of="$work/i2c-$bus.original" bs=128 count=1 2>/dev/null
    [ "$(wc -c < "$work/i2c-$bus.original")" -eq 128 ]
    changed_i2c="$changed_i2c $bus"
    pattern 128 "$((13 + bus))" > "$work/i2c-$bus.tx"
    before=$(irq_count)
    cat "$work/i2c-$bus.tx" > "$eeprom"
    dd if="$eeprom" of="$work/i2c-$bus.rx" bs=128 count=1 2>/dev/null
    cmp "$work/i2c-$bus.tx" "$work/i2c-$bus.rx"
    after=$(irq_count)
    [ "$after" -eq "$before" ]
    echo "APOLLO_DMA350|i2c_pio=$bus|bytes=128|irq_before=$before|irq_after=$after|status=PASS"
done

# 64-byte loopback transfers exceed each SSI FIFO; the driver checks every byte.
[ ! -d /sys/module/spi_loopback_test ]
if [ -r /sys/module/spi/parameters/transfer_timeout_margin_ms ]; then
    saved_margin=$(cat /sys/module/spi/parameters/transfer_timeout_margin_ms)
    echo 30000 > /sys/module/spi/parameters/transfer_timeout_margin_ms
fi
for length in 64 4099; do
    vmalloc=0
    if [ "$length" = 4099 ]; then
        vmalloc=1
    fi
    before=$(irq_count)
    modprobe spi_loopback_test run_only_test=0 run_only_iter_len="$length" use_vmalloc="$vmalloc" loopback=1 loop_req=1 delay_ms=0
    spi_owned=1
    for bus in 0 1 2 3; do
        driver=$(basename "$(readlink -f "/sys/bus/spi/devices/spi$bus.0/driver")")
        [ "$driver" = spi-loopback-test ]
        if [ "$bus" -lt 2 ]; then
            echo "APOLLO_DMA350|spi=$bus|bytes=$length|vmalloc=$vmalloc|status=PASS"
        else
            echo "APOLLO_DMA350|spi_pio=$bus|bytes=$length|status=PASS"
        fi
    done
    after=$(irq_count)
    [ "$after" -gt "$before" ]
    echo "APOLLO_DMA350|spi_irq_before=$before|spi_irq_after=$after"
    modprobe -r spi_loopback_test
    spi_owned=0
done

find_uart()
{
    for tty in /sys/class/tty/ttyS*; do
        device=$(readlink -f "$tty/device")
        case "$device" in
            */"$1".serial/*|*/"$1".serial) basename "$tty"; return 0;;
        esac
    done
    return 1
}

uart_transfer()
{
    tx=$(find_uart "$1")
    rx=$(find_uart "$2")
    length=$3
    tag="$tx-$rx-$length"
    stty -F "/dev/$tx" 115200 raw -echo clocal -crtscts min 1 time 0
    stty -F "/dev/$rx" 115200 raw -echo clocal -crtscts min 1 time 0
    exec 3<>"/dev/$tx" 4<>"/dev/$rx"
    pattern "$length" 71 > "$work/$tag.tx"
    before=$(irq_count)
    dd if="/dev/$rx" of="$work/$tag.rx" bs=1 count="$length" 2>/dev/null &
    reader=$!
    sleep 0.1
    cat "$work/$tag.tx" >&3
    attempt=0
    while kill -0 "$reader" 2>/dev/null; do
        [ "$attempt" -lt 300 ] || return 1
        sleep 0.1
        attempt=$((attempt + 1))
    done
    wait "$reader"
    reader=
    cmp "$work/$tag.tx" "$work/$tag.rx"
    after=$(irq_count)
    [ "$after" -gt "$before" ]
    exec 3>&- 4>&-
    echo "APOLLO_DMA350|uart=$1->$2|bytes=$length|irq_before=$before|irq_after=$after|status=PASS"
}

# Keep both ports open so the TX ring position survives between transfers.
# The final transfer crosses its 4K boundary and exercises a multi-entry SG.
paired_tx=$(find_uart 301a0000)
paired_rx=$(find_uart 301b0000)
exec 5<>"/dev/$paired_tx" 6<>"/dev/$paired_rx"
for length in 17 128 512 4099; do
    uart_transfer 301a0000 301b0000 "$length"
    uart_transfer 301b0000 301a0000 "$length"
done
exec 5>&- 6>&-

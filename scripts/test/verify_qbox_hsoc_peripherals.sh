#!/bin/sh
# SPDX-License-Identifier: MIT
# Bounded SPI/UART traffic after Linux applies HSOC pinctrl states.
set -eu

reader=
spi_owned=0
capture=/tmp/hsoc-uart.$$

cleanup()
{
    if [ -n "$reader" ]; then
        kill "$reader" 2>/dev/null || true
        wait "$reader" 2>/dev/null || true
    fi
    rm -f "$capture"
    if [ "$spi_owned" = 1 ]; then
        modprobe -r spi_loopback_test
    fi
}

finish()
{
    rc=$?
    trap - EXIT HUP INT TERM
    cleanup || rc=1
    if [ "$rc" = 0 ]; then
        echo 'APOLLO_HSOC_PERIPHERALS|status=PASS'
    else
        echo "APOLLO_HSOC_PERIPHERALS|status=FAIL|rc=$rc"
    fi
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

find_uart()
{
    for tty in /sys/class/tty/ttyS*; do
        node=$(readlink -f "$tty/device")
        case "$node" in
            */"$1".serial/*|*/"$1".serial)
                basename "$tty"
                return 0
                ;;
        esac
    done
    return 1
}

uart_transfer()
{
    tx=$1
    rx=$2
    payload="HSOC-$tx-to-$rx-pinctrl-test"
    dd if="/dev/$rx" of="$capture" bs=1 count="${#payload}" 2>/dev/null &
    reader=$!
    sleep 0.1
    printf '%s' "$payload" > "/dev/$tx"
    tries=0
    while kill -0 "$reader" 2>/dev/null; do
        [ "$tries" -lt 50 ] || return 1
        sleep 0.1
        tries=$((tries + 1))
    done
    wait "$reader"
    reader=
    [ "$(cat "$capture")" = "$payload" ]
    echo "APOLLO_HSOC_PERIPHERALS|uart=$tx->$rx|bytes=${#payload}|status=PASS"
}

# These are board test endpoints, never the PL011 boot console.
uart0=$(find_uart 301a0000)
uart1=$(find_uart 301b0000)
uart2=$(find_uart 301c0000)
uart3=$(find_uart 301d0000)
for uart in "$uart0" "$uart1" "$uart2" "$uart3"; do
    stty -F "/dev/$uart" 115200 raw -echo clocal -crtscts min 1 time 0
done
uart_transfer "$uart0" "$uart1"
uart_transfer "$uart1" "$uart0"
uart_transfer "$uart2" "$uart3"
uart_transfer "$uart3" "$uart2"

# Require a fresh module so these bounded parameters actually take effect.
[ ! -d /sys/module/spi_loopback_test ]
modprobe spi_loopback_test run_only_test=0 run_only_iter_len=16 loopback=1 loop_req=1
spi_owned=1
for bus in 0 1 2 3; do
    driver=$(basename "$(readlink -f "/sys/bus/spi/devices/spi$bus.0/driver")")
    [ "$driver" = spi-loopback-test ]
    echo "APOLLO_HSOC_PERIPHERALS|spi=spi$bus.0|test=0|length=16|driver=$driver|status=PASS"
done

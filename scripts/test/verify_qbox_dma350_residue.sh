#!/bin/sh
# SPDX-License-Identifier: MIT
# Exercise both residue paths through DMAengine's live status polling.
set -eu
[ ! -d /sys/module/dmatest ]
channel=
for node in /sys/class/dma/dma*chan*; do
    [ -d "$node" ] || continue
    case "$(readlink -f "$node/device")" in
        *31000000*)
            if [ "$(cat "$node/in_use")" = 0 ]; then
                channel=$(basename "$node")
                break
            fi
            ;;
    esac
done
[ -n "$channel" ]
work=$(mktemp -d /tmp/dma350-residue.XXXXXX)
owned=0
cleanup()
{
    if [ "$owned" = 1 ]; then modprobe -r dmatest; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
for bytes in 65536 2097152; do
    for kind in 0 1; do
        dmesg > "$work/before"
        lines=$(wc -l < "$work/before")
        # Adding a channel creates its test threads immediately. Select the
        # operation and parameters first, otherwise mode 1 can still run copy.
        modprobe dmatest dmatest="$kind" test_buf_size="$bytes" \
            norandom=1 polled=1 iterations=5 channel="$channel" run=1
        owned=1
        [ "$(cat /sys/module/dmatest/parameters/dmatest)" = "$kind" ]
        [ "$(cat /sys/module/dmatest/parameters/test_buf_size)" = "$bytes" ]
        [ "$(cat /sys/module/dmatest/parameters/polled)" = Y ]
        cat /sys/module/dmatest/parameters/wait > "$work/wait-$bytes-$kind"
        dmesg > "$work/after"
        [ "$(wc -l < "$work/after")" -ge "$lines" ]
        tail -n "+$((lines + 1))" "$work/after" > "$work/test-$bytes-$kind.log"
        mode=copy
        [ "$kind" = 0 ] || mode=set
        grep -E "$channel-$mode[0-9]+: summary" "$work/test-$bytes-$kind.log" > "$work/summary"
        cat "$work/summary"
        if grep -Ev 'summary 5 tests, 0 failures .*\(0\)$' "$work/summary"; then
            exit 1
        fi
        modprobe -r dmatest
        owned=0
        echo "DMA350_RESIDUE|channel=$channel|bytes=$bytes|kind=$kind|polled=1|result=PASS"
    done
done
echo "DMA350_RESIDUE|result=PASS|artifacts=$work"

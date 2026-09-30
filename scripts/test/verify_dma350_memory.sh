#!/bin/sh
# SPDX-License-Identifier: MIT
# Guest-side DMA350 memory checks, leaving peripheral channel owners intact.
set -eu
export LC_ALL=C

work=$(mktemp -d /tmp/dma350-memory.XXXXXX)
dma_owned=0

finish()
{
    rc=$?
    trap - EXIT HUP INT TERM
    if [ "$dma_owned" = 1 ]; then
        modprobe -r dmatest || rc=1
    fi
    echo "DMA350_MEMORY_RESULT rc=$rc artifacts=$work"
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

# Match the GIC hardware INTID, not the Linux virtual IRQ or another DMA block.
irq_count()
{
    awk -v intid="$1" -v allow_absent="${2:-0}" '
        {
            matched = 0;
            for (i = 2; i < NF; i++)
                if ($i == "GICv3" && $(i + 1) == intid) matched = 1;
            if (matched) {
                lines++;
                for (i = 2; i <= NF && $i ~ /^[0-9]+$/; i++) total += $i;
            }
        }
        END {
            if (lines != 1 && !(allow_absent && lines == 0)) exit 1;
            print total + 0;
        }
    ' /proc/interrupts
}

# An existing dmatest instance belongs to someone else; do not modify it.
[ ! -d /sys/module/dmatest ]
for base in 31000000 31010000; do
    case "$base" in
        31000000) intid=311 ;;
        31010000) intid=390 ;;
    esac
    channels=0
    memory_channel=
    for channel in /sys/class/dma/dma*chan*; do
        [ -d "$channel" ] || continue
        device=$(readlink -f "$channel/device")
        case "$device" in
            */"$base".*|*/"$base".*/*)
                channels=$((channels + 1))
                if [ -z "$memory_channel" ] && [ "$(cat "$channel/in_use")" = 0 ]; then
                    memory_channel=$(basename "$channel")
                fi
                ;;
        esac
    done
    [ "$channels" -eq 8 ]
    [ -n "$memory_channel" ]
    echo "DMA350_MEMORY_TOPOLOGY base=$base channels=$channels selected=$memory_channel intid=$intid"
    for dma_kind in 0 1; do
        case "$dma_kind" in
            0) mode=memcpy ;;
            1) mode=memset ;;
        esac
        prefix="$work/$base-$mode"
        # With no peripheral DMA clients the driver requests its IRQ only
        # when dmatest allocates the first channel.
        before=$(irq_count "$intid" 1)
        dmesg > "$prefix.before"
        # Set ownership first so a partially failed insertion is cleaned up.
        dma_owned=1
        modprobe dmatest dmatest="$dma_kind" channel="$memory_channel" \
            iterations=5 test_buf_size=65536 timeout=10000 run=1
        cat /sys/module/dmatest/parameters/wait > "$prefix.wait"
        dmesg > "$prefix.log"
        before_lines=$(wc -l < "$prefix.before")
        head -n "$before_lines" "$prefix.log" > "$prefix.head"
        cmp "$prefix.before" "$prefix.head"
        tail -n "+$((before_lines + 1))" "$prefix.log" > "$prefix.new"
        grep -E "$memory_channel.*summary" "$prefix.new" > "$prefix.summary"
        cat "$prefix.summary"
        [ "$(wc -l < "$prefix.summary")" -eq 1 ]
        grep -Eq 'summary 5 tests, 0 failures .*\(0\)$' "$prefix.summary"
        after=$(irq_count "$intid")
        [ "$after" -gt "$before" ]
        modprobe -r dmatest
        dma_owned=0
        echo "DMA350_MEMORY_PASS base=$base mode=$mode channel=$memory_channel iterations=5 bytes=65536 intid=$intid irq_before=$before irq_after=$after"
    done
done
echo DMA350_MEMORY_ALL_PASS

#!/bin/sh
# SPDX-License-Identifier: MIT
# Run with scripts/run/ssh_run.sh scripts/test/verify_qbox_i2s.sh.
set -eu

command -v i2s-loopback >/dev/null
for base in 31000000 31010000; do
    test ! -e "/sys/bus/platform/devices/$base.dma-controller/of_node/dma-coherent"
    count=0
    for channel in /sys/class/dma/dma*chan*; do
        test -d "$channel" || continue
        case $(readlink -f "$channel/device") in
            *"$base"*) count=$((count + 1)) ;;
        esac
    done
    test "$count" -eq 8
    echo "I2S_DMA_CONTROLLER base=$base channels=$count coherency=non-coherent"
done
mode=pio
if [ -e /sys/bus/platform/devices/30200000.i2s/of_node/dmas ]; then
    test -e /sys/bus/platform/devices/30210000.i2s/of_node/dmas
    mode=dma
fi
echo "I2S_TEST mode=$mode"
cat /proc/asound/cards
aplay -l
arecord -l
pcm() {
    "$1" -l | sed -n "/$2/s/^card \([0-9][0-9]*\):.*device \([0-9][0-9]*\):.*/hw:\1,\2/p" | head -n 1
}
tx0=$(pcm aplay 30200000)
rx0=$(pcm arecord 30200000)
tx1=$(pcm aplay 30210000)
rx1=$(pcm arecord 30210000)
test -n "$tx0" && test -n "$rx0" && test -n "$tx1" && test -n "$rx1"
grep -E '30200000.i2s|30210000.i2s|GICv3[[:space:]]+(311|390)[[:space:]]' /proc/interrupts
echo "I2S_DIRECTION 0->1 playback=$tx0 capture=$rx1"
i2s-loopback "$tx0" "$rx1"
echo "I2S_DIRECTION 1->0 playback=$tx1 capture=$rx0"
i2s-loopback "$tx1" "$rx0"
echo "I2S_SIMULTANEOUS_DUPLEX"
i2s-loopback "$tx0" "$rx1" &
forward=$!
i2s-loopback "$tx1" "$rx0" &
reverse=$!
result=0
wait "$forward" || result=1
wait "$reverse" || result=1
test "$result" -eq 0
grep -E '30200000.i2s|30210000.i2s|GICv3[[:space:]]+(311|390)[[:space:]]' /proc/interrupts
echo "I2S_DRIVER_TEST_PASS mode=$mode"

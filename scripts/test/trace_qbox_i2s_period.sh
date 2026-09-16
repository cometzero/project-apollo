#!/bin/sh
# Guest-side bounded DMA/PIO service trace; use a dedicated trace instance.
set -eu
duration=${1:-60}
mode=${2:-dma}
case "$mode" in
    dma) irq_symbol=d350_irq; program_pattern='^d350_program_cmd(\.isra\.[0-9]+)?$'; callback_symbol=dmaengine_pcm_dma_complete ;;
    pio) irq_symbol=i2s_irq_handler; program_pattern='^dw_pcm_tx_16(\.isra\.[0-9]+)?$'; callback_symbol=snd_pcm_period_elapsed_under_stream_lock ;;
    *) echo 'mode must be dma or pio' >&2; exit 2 ;;
esac
case "$duration" in
    ''|*[!0-9]*) echo 'duration must be 1..600 seconds' >&2; exit 2 ;;
esac
test "$duration" -ge 1 && test "$duration" -le 600 || exit 2
trace_root=/sys/kernel/tracing
if ! mountpoint -q "$trace_root"; then
    mount -t tracefs tracefs "$trace_root"
fi
group="i2speriod_$$"
instance="$trace_root/instances/$group"
mkdir "$instance"
cleanup()
{
    echo 0 > "$instance/tracing_on"
    echo 0 > "$instance/events/$group/enable" 2>/dev/null || true
    for event in irq_enter irq_exit program_enter program_exit receive_enter receive_exit trigger_enter trigger_exit callback; do
        echo "-:$group/$event" >> "$trace_root/kprobe_events" 2>/dev/null || true
    done
    rmdir "$instance"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
echo 0 > "$instance/tracing_on"
echo 4096 > "$instance/buffer_size_kb"
echo "p:$group/irq_enter $irq_symbol channel=\$arg2:x64" >> "$trace_root/kprobe_events"
echo "r:$group/irq_exit $irq_symbol" >> "$trace_root/kprobe_events"
program_symbol=$(awk -v pattern="$program_pattern" '$3 ~ pattern {print $3; exit}' /proc/kallsyms)
test -n "$program_symbol"
# An optimized .isra function may have a different argument ABI; time it only.
echo "p:$group/program_enter $program_symbol" >> "$trace_root/kprobe_events"
echo "r:$group/program_exit $program_symbol" >> "$trace_root/kprobe_events"
if [ "$mode" = pio ]; then
    receive_symbol=$(awk '$3 ~ /^dw_pcm_rx_16(\.isra\.[0-9]+)?$/ {print $3; exit}' /proc/kallsyms)
    test -n "$receive_symbol"
    echo "p:$group/receive_enter $receive_symbol" >> "$trace_root/kprobe_events"
    echo "r:$group/receive_exit $receive_symbol" >> "$trace_root/kprobe_events"
    echo "p:$group/trigger_enter dw_i2s_trigger substream=\$arg1:x64 cmd=\$arg2:s32" >> "$trace_root/kprobe_events"
    echo "r:$group/trigger_exit dw_i2s_trigger" >> "$trace_root/kprobe_events"
fi
echo "p:$group/callback $callback_symbol" >> "$trace_root/kprobe_events"
echo 1 > "$instance/events/$group/enable"
echo 1 > "$instance/tracing_on"
echo PERIOD_TRACE_READY >&2
sleep "$duration"
echo 0 > "$instance/tracing_on"
cat "$instance/trace"

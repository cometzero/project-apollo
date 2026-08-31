#!/bin/sh

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

platform=${1:?platform required}
mode=${2:?mode required}
input_sha256=${3:?input sha256 required}
prefix='APOLLO_IRQ|v=1'
dev=
target=
virq=
original_affinity=
original_cpu1_online=
cleanup_ready=0

emit()
{
    printf '%s|%s\n' "$prefix" "$*"
}

cleanup()
{
    rc=0
    if [ "$cleanup_ready" -eq 1 ]; then
        printf '%s\n' "$original_affinity" > "/proc/irq/$virq/smp_affinity_list" 2>/dev/null || rc=1
        if [ -w /sys/devices/system/cpu/cpu1/online ]; then
            printf '%s\n' "$original_cpu1_online" > /sys/devices/system/cpu/cpu1/online 2>/dev/null || rc=1
        fi
    else
        rc=1
    fi
    restored_affinity=0
    restored_cpu=0
    [ "$rc" -eq 0 ] && restored_affinity=1
    if [ ! -r /sys/devices/system/cpu/cpu1/online ] || [ "$(cat /sys/devices/system/cpu/cpu1/online)" = "$original_cpu1_online" ]; then
        restored_cpu=1
    fi
    emit "event=cleanup|affinity_restored=$restored_affinity|cpu1_restored=$restored_cpu|rc=$rc"
}

trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

driver_name()
{
    basename "$(readlink -f "$1/driver")"
}

discover_endpoint()
{
    case "$platform:$mode" in
        fvp:msix)
            candidate=/sys/bus/pci/devices/0004:00:1f.0
            [ -d "$candidate" ] || return 1
            [ "$(cat "$candidate/vendor")" = 0x13b5 ] || return 1
            case "$(cat "$candidate/class")" in 0x0106*) ;; *) return 1 ;; esac
            [ "$(driver_name "$candidate")" = ahci ] || return 1
            dev=$candidate
            for block in /sys/class/block/*; do
                [ -e "$block/partition" ] && continue
                case "$(readlink -f "$block/device")" in *0004:00:1f.0*) target=/dev/${block##*/}; break ;; esac
            done
            ;;
        qbox:msix|qbox:intx)
            dev=/sys/bus/pci/devices/0000:00:01.0
            [ -d "$dev" ] || return 1
            [ "$(driver_name "$dev")" = virtio-pci ] || return 1
            for net in /sys/class/net/*; do
                [ "$(cat "$net/address" 2>/dev/null)" = 52:54:00:12:34:56 ] || continue
                case "$(readlink -f "$net/device")" in *0000:00:01.0*) target=${net##*/}; break ;; esac
            done
            ;;
        qbox:spi)
            dev=/sys/bus/platform/devices/30060000.virtio
            [ -d "$dev" ] || return 1
            [ "$(driver_name "$dev")" = virtio-mmio ] || return 1
            [ "$(tr -d '\000' < "$dev/of_node/compatible")" = virtio,mmio ] || return 1
            for net in /sys/class/net/*; do
                case "$(readlink -f "$net/device")" in "$dev"/*) target=${net##*/}; break ;; esac
            done
            ;;
        *) return 1 ;;
    esac
    [ -n "$target" ]
}

per_cpu_count()
{
    tr -d ' \t\n' < "/sys/kernel/irq/$virq/per_cpu_count"
}

effective_cpu()
{
    cat "/proc/irq/$virq/effective_affinity_list"
}

workload()
{
    phase=$1
    rc=0
    case "$platform:$mode" in
        fvp:msix) timeout 30 dd if="$target" of=/dev/null bs=4096 count=64 >/dev/null 2>&1 || rc=$? ;;
        qbox:msix|qbox:intx) timeout 15 ping -I "$target" -c 2 -W 2 10.0.2.2 >/dev/null 2>&1 || rc=$? ;;
        qbox:spi) timeout 15 ping -I "$target" -c 2 -W 2 10.0.2.2 >/dev/null 2>&1 || rc=$? ;;
    esac
    emit "event=workload|phase=$phase|target=$target|rc=$rc"
    [ "$rc" -eq 0 ]
}

set_affinity()
{
    phase=$1
    cpu=$2
    rc=0
    printf '%s\n' "$cpu" > "/proc/irq/$virq/smp_affinity_list" 2>/dev/null || rc=$?
    effective=$(effective_cpu)
    emit "event=affinity|phase=$phase|requested=$cpu|effective=$effective|rc=$rc"
    [ "$rc" -eq 0 ] && [ "$effective" = "$cpu" ]
}

run_phase()
{
    phase=$1
    cpu=$2
    set_affinity "$phase" "$cpu" || return 1
    emit "event=count|phase=$phase-before|values=$(per_cpu_count)"
    workload "$phase" || return 1
    emit "event=count|phase=$phase-after|values=$(per_cpu_count)"
}

emit_chain()
{
    awk -v p="$prefix" -v v="$virq" '
        /^[[:space:]]*domain:/ { domain=$0; sub(/^[[:space:]]*domain:[[:space:]]*/, "", domain) }
        /^[[:space:]]*hwirq:/ { hwirq=$0; sub(/^[[:space:]]*hwirq:[[:space:]]*/, "", hwirq) }
        /^[[:space:]]*chip:/ {
            chip=$0; sub(/^[[:space:]]*chip:[[:space:]]*/, "", chip)
            printf "%s|event=chain|virq=%s|index=%d|domain=%s|hwirq=%s|chip=%s\n", p, v, index, domain, hwirq, chip
            index++
        }
    ' "/sys/kernel/debug/irq/irqs/$virq"
}

discover_endpoint || exit 20
action='net-io'
[ "$platform" = fvp ] && action='disk-io'
[ "$mode" = spi ] && action=control
emit "event=contract|input_sha256=$input_sha256|platform=$platform|mode=$mode|action=$action"

bdf=${dev##*/}
vendor=- class=- driver=- compatible=- mac=-
case "$mode" in
    spi) bdf=-; driver=$(driver_name "$dev"); compatible=$(tr -d '\000' < "$dev/of_node/compatible") ;;
    *)
        vendor=$(cat "$dev/vendor")
        class=$(cat "$dev/class")
        driver=$(driver_name "$dev")
        [ "$platform" = qbox ] && mac=$(cat "/sys/class/net/$target/address")
        ;;
esac
emit "event=endpoint|bdf=$bdf|vendor=$vendor|class=$class|driver=$driver|compatible=$compatible|devpath=$dev|target=$target|mac=$mac"

case "$mode" in
    msix)
        set -- "$dev"/msi_irqs/*
        [ -e "$1" ] || exit 21
        virq=${1##*/}
        emit "event=msi_irq|virq=$virq|owner=$1"
        ;;
    intx) virq=$(cat "$dev/irq"); emit "event=line_irq|virq=$virq|owner=$dev" ;;
    spi)
        virtio_name=$(basename "$(readlink -f "/sys/class/net/$target/device")")
        virq=
        for irq_path in /sys/kernel/debug/irq/irqs/*; do
            grep -Eq "^device:[[:space:]]+$virtio_name$" "$irq_path" || continue
            grep -Eq "^[[:space:]]*hwirq:[[:space:]]+0x125$" "$irq_path" || continue
            virq=${irq_path##*/}
            break
        done
        [ -n "$virq" ] || exit 21
        emit "event=line_irq|virq=$virq|owner=$dev"
        ;;
esac

[ -r "/sys/kernel/debug/irq/irqs/$virq" ] || exit 22
[ -r "/sys/kernel/irq/$virq/per_cpu_count" ] || exit 23
emit_chain
original_affinity=$(cat "/proc/irq/$virq/smp_affinity_list")
original_cpu1_online=1
[ ! -r /sys/devices/system/cpu/cpu1/online ] || original_cpu1_online=$(cat /sys/devices/system/cpu/cpu1/online)
cleanup_ready=1

run_phase cpu0 0 || exit 30
run_phase cpu1 1 || exit 31
printf '0\n' > /sys/devices/system/cpu/cpu1/online || exit 32
emit "event=hotplug|phase=cpu1-offline|cpu=1|online=0|effective=$(effective_cpu)|rc=0"
emit "event=count|phase=offline-before|values=$(per_cpu_count)"
workload offline || exit 33
emit "event=count|phase=offline-after|values=$(per_cpu_count)"
printf '1\n' > /sys/devices/system/cpu/cpu1/online || exit 34
emit "event=hotplug|phase=cpu1-online|cpu=1|online=1|rc=0"
run_phase replay 1 || exit 35
trap - EXIT HUP INT TERM
cleanup
emit "event=final|input_sha256=$input_sha256|status=complete"

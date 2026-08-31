#!/bin/sh

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

mode=${1:?mode required}
input_sha256=${2:?input sha256 required}
probe_sha256=${3:?probe sha256 required}
prefix=APOLLO_IRQ
dev=/sys/bus/pci/devices/0000:00:01.0
target=
virq=
original_affinity=
original_cpu1_online=
cleanup_ready=0
debugfs_owned=0

emit()
{
    printf '%s|v=1|%s\n' "$prefix" "$*"
}

driver_name()
{
    basename "$(readlink -f "$1/driver")"
}

per_cpu_count()
{
    tr -d ' \t\n' < "/sys/kernel/irq/$virq/per_cpu_count"
}

effective_cpu()
{
    cat "/proc/irq/$virq/effective_affinity_list"
}

ensure_debugfs()
{
    [ -d /sys/kernel/debug/irq/irqs ] && return 0
    [ -d /sys/kernel/debug ] || return 1
    mount -t debugfs debugfs /sys/kernel/debug 2>/dev/null || true
    [ -d /sys/kernel/debug/irq/irqs ]
}

cleanup()
{
    rc=0
    affinity_restored=0
    cpu1_restored=0
    if [ "$cleanup_ready" -eq 1 ]; then
        if [ -w /sys/devices/system/cpu/cpu1/online ]; then
            printf '%s\n' "$original_cpu1_online" > /sys/devices/system/cpu/cpu1/online 2>/dev/null || rc=1
        fi
        printf '%s\n' "$original_affinity" > "/proc/irq/$virq/smp_affinity_list" 2>/dev/null || rc=1
        [ "$(cat "/proc/irq/$virq/smp_affinity_list")" = "$original_affinity" ] && affinity_restored=1
        if [ ! -r /sys/devices/system/cpu/cpu1/online ] || [ "$(cat /sys/devices/system/cpu/cpu1/online)" = "$original_cpu1_online" ]; then
            cpu1_restored=1
        fi
    else
        rc=1
    fi
    [ "$affinity_restored" -eq 1 ] || rc=1
    [ "$cpu1_restored" -eq 1 ] || rc=1
    emit "event=cleanup|affinity_restored=$affinity_restored|cpu1_restored=$cpu1_restored|rc=$rc"
    return "$rc"
}

cleanup_debugfs()
{
    if [ "$debugfs_owned" -eq 1 ]; then
        umount /sys/kernel/debug 2>/dev/null || return 1
        debugfs_owned=0
    fi
}

abort()
{
    rc=$1
    cleanup
    cleanup_debugfs
    exit "$rc"
}

trap 'abort 129' HUP
trap 'abort 130' INT
trap 'abort 143' TERM
trap 'cleanup; cleanup_debugfs' EXIT

workload()
{
    phase=$1
    rc=0
    ping -I "$target" -c 2 -W 2 10.0.2.2 >/dev/null 2>&1 || rc=$?
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
            raw_chip=$0; sub(/^[[:space:]]*chip:[[:space:]]*/, "", raw_chip)
            raw_domain=domain
            chip=raw_chip
            if (raw_chip ~ /^ITS-PCI-MSIX-/) {
                chip="PCI-MSIX"; domain="PCI-MSIX-0000:00:01.0"
            } else if (raw_chip == "ITS") {
                chip="ITS-MSI"; domain="ITS-MSI"
            } else if (raw_chip == "GICv3") {
                domain="GICv3"
            }
            printf "%s|v=1|event=chain|virq=%s|index=%d|domain=%s|hwirq=%s|chip=%s|raw_domain=%s|raw_chip=%s\n", p, v, level, domain, hwirq, chip, raw_domain, raw_chip
            level++
        }
    ' "/sys/kernel/debug/irq/irqs/$virq"
}

discover_pci_target()
{
    [ -d "$dev" ] || return 1
    [ "$(driver_name "$dev")" = virtio-pci ] || return 1
    for net in /sys/class/net/*; do
        [ "$(cat "$net/address" 2>/dev/null)" = 52:54:00:12:34:56 ] || continue
        case "$(readlink -f "$net/device")" in *0000:00:01.0*) target=${net##*/}; break ;; esac
    done
    [ -n "$target" ] || return 1
    ip link set "$target" up
    udhcpc -n -q -t 3 -T 1 -i "$target" >/dev/null 2>&1
}

select_msix_vector()
{
    virtio_name=$(basename "$(readlink -f "/sys/class/net/$target/device")")
    while IFS= read -r line; do
        case "$line" in
            *"ITS-PCI-MSIX-0000:00:01.0"*"$virtio_name-input.0"*) ;;
            *) continue ;;
        esac
        candidate=${line%%:*}
        candidate=$(printf '%s' "$candidate" | tr -d ' ')
        [ -e "$dev/msi_irqs/$candidate" ] || continue
        virq=$candidate
        break
    done < /proc/interrupts
    [ -n "$virq" ]
}

run_pci()
{
    discover_pci_target || return 20
    actual_manifest_sha=$(sha256sum /usr/share/apollo-pcie-its/input-manifest.json)
    actual_manifest_sha=${actual_manifest_sha%% *}
    actual_probe_sha=$(sha256sum /usr/bin/apollo-pcie-its-guest)
    actual_probe_sha=${actual_probe_sha%% *}
    [ "$actual_manifest_sha" = "$input_sha256" ] || return 21
    [ "$actual_probe_sha" = "$probe_sha256" ] || return 22
    emit "event=contract|input_sha256=$input_sha256|platform=qbox|mode=$mode|action=net-io"
    emit "event=embedded_probe|path=/usr/bin/apollo-pcie-its-guest|sha256=$actual_probe_sha|bounded_commands=ping-udhcpc"
    emit "event=endpoint|bdf=0000:00:01.0|vendor=$(cat "$dev/vendor")|class=$(cat "$dev/class")|driver=$(driver_name "$dev")|compatible=-|devpath=$dev|target=$target|mac=$(cat "/sys/class/net/$target/address")"
    msi_count=$(find "$dev/msi_irqs" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l)
    emit "event=msi_state|count=$msi_count|path=$dev/msi_irqs"
    case "$mode" in
        msix)
            [ "$msi_count" -gt 0 ] || return 23
            select_msix_vector || return 24
            emit "event=msi_irq|virq=$virq|owner=$dev/msi_irqs/$virq"
            ;;
        intx)
            [ "$msi_count" -eq 0 ] || return 25
            virq=$(cat "$dev/irq")
            emit "event=line_irq|virq=$virq|owner=$dev"
            ;;
        *) return 26 ;;
    esac
    debugfs_ready=0
    ensure_debugfs && debugfs_ready=1
    debugfs_entries=
    for debugfs_path in /sys/kernel/debug/*; do
        [ -e "$debugfs_path" ] || continue
        debugfs_entries="$debugfs_entries${debugfs_path##*/},"
    done
    emit "event=debugfs_mount|ready=$debugfs_ready|entries=${debugfs_entries:--}"
    [ "$debugfs_ready" -eq 1 ] || return 27
    irq_entries=
    for irq_path in /sys/kernel/debug/irq/irqs/*; do
        [ -e "$irq_path" ] || continue
        irq_entries="$irq_entries${irq_path##*/},"
    done
    irq_readable=0
    [ -r "/sys/kernel/debug/irq/irqs/$virq" ] && irq_readable=1
    emit "event=debugfs|virq=$virq|readable=$irq_readable|entries=${irq_entries:--}"
    [ -r "/sys/kernel/debug/irq/irqs/$virq" ] || return 27
    [ -r "/sys/kernel/irq/$virq/per_cpu_count" ] || return 28
    emit_chain
    original_affinity=$(cat "/proc/irq/$virq/smp_affinity_list")
    original_cpu1_online=$(cat /sys/devices/system/cpu/cpu1/online)
    cleanup_ready=1
    run_phase cpu0 0 || return 30
    run_phase cpu1 1 || return 31
    printf '0\n' > /sys/devices/system/cpu/cpu1/online || return 32
    printf '0\n' > "/proc/irq/$virq/smp_affinity_list" || return 32
    emit "event=hotplug|phase=cpu1-offline|cpu=1|online=0|effective=$(effective_cpu)|rc=0"
    emit "event=count|phase=offline-before|values=$(per_cpu_count)"
    workload offline || return 33
    emit "event=count|phase=offline-after|values=$(per_cpu_count)"
    printf '1\n' > /sys/devices/system/cpu/cpu1/online || return 34
    emit "event=hotplug|phase=cpu1-online|cpu=1|online=1|rc=0"
    run_phase replay 1 || return 35
    cleanup || return 36
    cleanup_ready=0
}

run_spi()
{
    prefix=APOLLO_SPI
    spi_dev=/sys/bus/platform/devices/30060000.virtio
    [ -d "$spi_dev" ] || return 40
    [ "$(driver_name "$spi_dev")" = virtio-mmio ] || return 41
    [ "$(tr -d '\000' < "$spi_dev/of_node/compatible")" = virtio,mmio ] || return 42
    spi_real=$(readlink -f "$spi_dev")
    target=
    for net in /sys/class/net/*; do
        case "$(readlink -f "$net/device")" in "$spi_real"/*) target=${net##*/}; break ;; esac
    done
    [ -n "$target" ] || return 43
    ip link set "$target" up
    udhcpc -n -q -t 3 -T 1 -i "$target" >/dev/null 2>&1 || return 44
    ensure_debugfs || return 45
    virtio_name=$(basename "$(readlink -f "/sys/class/net/$target/device")")
    spi_virq=$(awk -v device="$virtio_name" '
        $NF == device && $0 ~ /GICv3[[:space:]]+293[[:space:]]/ {
            gsub(":", "", $1); print $1; exit
        }
    ' /proc/interrupts)
    [ -n "$spi_virq" ] || return 45
    pci_virq=$virq
    emit "event=contract|input_sha256=$input_sha256|platform=qbox|mode=spi"
    emit "event=endpoint|bdf=-|driver=virtio-mmio|compatible=virtio,mmio|devpath=$spi_dev|target=$target"
    emit "event=pci_vector|virq=$pci_virq|owner=$dev/msi_irqs/$pci_virq"
    virq=$spi_virq
    emit "event=line_irq|virq=$virq|owner=$spi_dev"
    emit_chain
    original_affinity=$(cat "/proc/irq/$virq/smp_affinity_list")
    original_cpu1_online=$(cat /sys/devices/system/cpu/cpu1/online)
    cleanup_ready=1
    printf '0\n' > "/proc/irq/$virq/smp_affinity_list" || return 46
    [ "$(effective_cpu)" = 0 ] || return 47
    emit "event=count|phase=spi-before|values=$(per_cpu_count)"
    virq=$pci_virq
    emit "event=count|phase=pci-before|values=$(per_cpu_count)"
    virq=$spi_virq
    workload isolated || return 48
    emit "event=count|phase=spi-after|values=$(per_cpu_count)"
    virq=$pci_virq
    emit "event=count|phase=pci-after|values=$(per_cpu_count)"
    virq=$spi_virq
    cleanup || return 49
    cleanup_ready=0
    emit "event=final|input_sha256=$input_sha256|status=complete"
    prefix=APOLLO_IRQ
}

if ! grep -q ' /sys/kernel/debug debugfs ' /proc/mounts; then
    mount -t debugfs debugfs /sys/kernel/debug || exit 11
    debugfs_owned=1
fi
run_pci || exit $?
if [ "$mode" = msix ]; then
    run_spi || exit $?
fi
trap - EXIT HUP INT TERM
cleanup_debugfs || exit 50
emit "event=final|input_sha256=$input_sha256|status=complete"

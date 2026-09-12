#!/bin/sh
#
# Validate the Apollo QBox generic-QEMU PCIe lane topology from the guest.
#
# The root-port LinkCap advertises the modelled maximum speed and width.
# Link Status is recorded for diagnosis only: a virtio endpoint can negotiate
# a narrower, slower link than its parent root port advertises.

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH

mode=${1:-default}
prefix=APOLLO_PCIE_LANES
gateway=${APOLLO_PCIE_GATEWAY:-10.0.2.2}
protected_iface=${APOLLO_PCIE_PROTECTED_IFACE:-eth0}
active_iface=
active_addr=
active_was_up=0
cleanup_done=0

emit()
{
    printf '%s|v=1|%s\n' "$prefix" "$*"
}

die()
{
    code=$1
    reason=$2
    cleanup || true
    emit "event=final|mode=$mode|status=FAIL|code=$code|reason=$reason"
    trap - EXIT HUP INT TERM
    exit "$code"
}

cleanup()
{
    [ "$cleanup_done" -eq 0 ] || return 0
    cleanup_done=1
    [ -n "$active_iface" ] || return 0

    rc=0
    address_restored=0
    link_restored=0
    ip addr del "$active_addr/24" dev "$active_iface" 2>/dev/null || rc=1
    [ "$rc" -eq 0 ] && address_restored=1
    if [ "$active_was_up" -eq 0 ]; then
        ip link set dev "$active_iface" down 2>/dev/null || rc=1
    fi
    if [ "$active_was_up" -eq 1 ]; then
        ip link show dev "$active_iface" | grep -Eq '<[^>]*,UP(,|>)' && link_restored=1
    else
        ip link show dev "$active_iface" | grep -Eq '<[^>]*,UP(,|>)' || link_restored=1
    fi
    emit "event=cleanup|iface=$active_iface|address=$active_addr|address_restored=$address_restored|link_restored=$link_restored|rc=$rc"
    active_iface=
    active_addr=
    return "$rc"
}

trap 'cleanup' EXIT
trap 'die 130 signal_INT' INT
trap 'die 143 signal_TERM' TERM
trap 'die 129 signal_HUP' HUP

expected_ports()
{
    case "$mode" in
        default) printf '%s\n' '1:4 2:4 3:2 4:2' ;;
        port2)  printf '%s\n' '1:4 2:4 3:1 4:2 5:1' ;;
        *) return 1 ;;
    esac
}

slot_from_bdf()
{
    case "$1" in
        ????:00:01.0) printf '%s\n' 1 ;;
        ????:00:02.0) printf '%s\n' 2 ;;
        ????:00:03.0) printf '%s\n' 3 ;;
        ????:00:04.0) printf '%s\n' 4 ;;
        ????:00:05.0) printf '%s\n' 5 ;;
        *) return 1 ;;
    esac
}

width_for_slot()
{
    wanted=$1
    for item in $expected; do
        slot=${item%%:*}
        width=${item#*:}
        [ "$slot" = "$wanted" ] && {
            printf '%s\n' "$width"
            return 0
        }
    done
    return 1
}

byte_at()
{
    value=$(od -An -j "$2" -N 1 -t u1 "$1" 2>/dev/null | tr -d '[:space:]')
    case "$value" in
        ''|*[!0-9]*) return 1 ;;
        *) printf '%s\n' "$value" ;;
    esac
}

pcie_capability()
{
    config=$1/config
    pointer=$(byte_at "$config" 52) || return 1
    hops=0
    while [ "$pointer" -ne 0 ] && [ "$hops" -lt 48 ]; do
        cap_id=$(byte_at "$config" "$pointer") || return 1
        next=$(byte_at "$config" $((pointer + 1))) || return 1
        [ "$cap_id" -eq 16 ] && {
            printf '%s\n' "$pointer"
            return 0
        }
        pointer=$next
        hops=$((hops + 1))
    done
    return 1
}

counter_for_irq()
{
    awk -v irq="$1" '
        $1 == irq ":" {
            total = 0
            for (i = 2; i <= NF; i++) {
                if ($i !~ /^[0-9]+$/) break
                total += $i
            }
            print total
            found = 1
            exit
        }
        END { if (!found) exit 1 }
    ' /proc/interrupts
}

sum_irq_counters()
{
    total=0
    for irq in $1; do
        count=$(counter_for_irq "$irq") || return 1
        total=$((total + count))
    done
    printf '%s\n' "$total"
}

stat_for_iface()
{
    value=$(cat "/sys/class/net/$1/statistics/$2" 2>/dev/null) || return 1
    case "$value" in
        ''|*[!0-9]*) return 1 ;;
        *) printf '%s\n' "$value" ;;
    esac
}

driver_name()
{
    driver=$(readlink -f "$1/driver" 2>/dev/null) || return 1
    basename "$driver"
}

is_link_up()
{
    ip link show dev "$1" | grep -Eq '<[^>]*,UP(,|>)'
}

find_leaf()
{
    root_bdf=$1
    leaf=
    leaf_count=0
    for candidate in /sys/bus/pci/devices/*; do
        [ -r "$candidate/class" ] || continue
        candidate_real=$(readlink -f "$candidate") || continue
        [ "$(basename "$(dirname "$candidate_real")")" = "$root_bdf" ] || continue
        [ "$(driver_name "$candidate")" = virtio-pci ] || continue
        leaf=$candidate
        leaf_count=$((leaf_count + 1))
    done
    [ "$leaf_count" -eq 1 ] || return 1
    printf '%s\n' "$leaf"
}

find_netif()
{
    leaf_real=$(readlink -f "$1") || return 1
    iface=
    iface_count=0
    for net in /sys/class/net/*; do
        [ -e "$net/device" ] || continue
        net_device=$(readlink -f "$net/device") || continue
        case "$net_device" in
            "$leaf_real"/*) ;;
            *) continue ;;
        esac
        [ "$(driver_name "$net/device")" = virtio_net ] || continue
        iface=${net##*/}
        iface_count=$((iface_count + 1))
    done
    [ "$iface_count" -eq 1 ] || return 1
    printf '%s\n' "$iface"
}

validate_root_port()
{
    slot=$1
    width=$2
    root_bdf=$3
    root=/sys/bus/pci/devices/$root_bdf
    [ "$(driver_name "$root")" = pcieport ] || return 1
    cap=$(pcie_capability "$root") || return 1
    max_speed_byte=$(byte_at "$root/config" $((cap + 12))) || return 1
    max_width_byte=$(byte_at "$root/config" $((cap + 13))) || return 1
    current_speed_byte=$(byte_at "$root/config" $((cap + 18))) || return 1
    current_width_byte=$(byte_at "$root/config" $((cap + 19))) || return 1
    max_speed=$((max_speed_byte & 15))
    max_width=$(((max_speed_byte >> 4) | ((max_width_byte & 3) << 4)))
    current_speed=$((current_speed_byte & 15))
    current_width=$(((current_speed_byte >> 4) | ((current_width_byte & 3) << 4)))
    emit "event=root_port|slot=$slot|bdf=$root_bdf|class=$(cat "$root/class")|driver=pcieport|pcie_cap=0x$(printf '%02x' "$cap")|linkcap_max_speed=$max_speed|linkcap_max_width=$max_width|current_speed=$current_speed|current_width=$current_width|expected_max_speed=5|expected_max_width=$width|assertion=linkcap_only"
    [ "$max_speed" -eq 5 ] && [ "$max_width" -eq "$width" ]
}

validate_leaf_traffic()
{
    slot=$1
    root_bdf=$2
    leaf=$(find_leaf "$root_bdf") || return 1
    [ "$(cat "$leaf/class")" = 0x020000 ] || return 1
    [ -L "$leaf/iommu_group" ] || return 1
    iommu_group=$(basename "$(readlink -f "$leaf/iommu_group")")
    iface=$(find_netif "$leaf") || return 1
    virtio_device=$(readlink -f "/sys/class/net/$iface/device") || return 1
    access_platform=$(cut -c 34 "$virtio_device/features") || return 1
    [ "$access_platform" = 1 ] || return 1
    [ "$iface" != "$protected_iface" ] || return 1
    ip -4 addr show dev "$iface" scope global | grep -q 'inet ' && return 1

    irq_list=
    for irq_path in "$leaf"/msi_irqs/*; do
        [ -e "$irq_path" ] || continue
        irq_list="$irq_list ${irq_path##*/}"
    done
    irq_list=${irq_list# }
    [ -n "$irq_list" ] || return 1
    irq_before=$(sum_irq_counters "$irq_list") || return 1
    tx_before=$(stat_for_iface "$iface" tx_packets) || return 1
    rx_before=$(stat_for_iface "$iface" rx_packets) || return 1
    leaf_bdf=${leaf##*/}
    emit "event=leaf|slot=$slot|root_port=$root_bdf|bdf=$leaf_bdf|class=$(cat "$leaf/class")|pci_driver=$(driver_name "$leaf")|netif=$iface|net_driver=$(driver_name "/sys/class/net/$iface/device")|msi_irqs=$irq_list|parent=$root_bdf|iommu_group=$iommu_group|access_platform=$access_platform"

    active_iface=$iface
    active_addr=10.0.2.$((100 + slot))
    cleanup_done=0
    is_link_up "$active_iface" && active_was_up=1 || active_was_up=0
    ip link set dev "$active_iface" up || return 1
    ip addr add "$active_addr/24" dev "$active_iface" || return 1
    ping -I "$active_iface" -c 3 -W 2 "$gateway" || return 1
    tx_after=$(stat_for_iface "$iface" tx_packets) || return 1
    rx_after=$(stat_for_iface "$iface" rx_packets) || return 1
    irq_after=$(sum_irq_counters "$irq_list") || return 1
    tx_delta=$((tx_after - tx_before))
    rx_delta=$((rx_after - rx_before))
    irq_delta=$((irq_after - irq_before))
    emit "event=traffic|slot=$slot|bdf=$leaf_bdf|netif=$iface|gateway=$gateway|ping_rc=0|tx_before=$tx_before|tx_after=$tx_after|tx_delta=$tx_delta|rx_before=$rx_before|rx_after=$rx_after|rx_delta=$rx_delta|irq_before=$irq_before|irq_after=$irq_after|irq_delta=$irq_delta"
    [ "$tx_delta" -gt 0 ] && [ "$rx_delta" -gt 0 ] && [ "$irq_delta" -gt 0 ] || return 1
    cleanup
}

expected=$(expected_ports) || die 2 invalid_mode
command -v ip >/dev/null 2>&1 || die 3 missing_ip
command -v ping >/dev/null 2>&1 || die 4 missing_ping
command -v od >/dev/null 2>&1 || die 5 missing_od

emit "event=contract|mode=$mode|ecam=0x43b50000|expected_ports=$(printf '%s' "$expected" | tr ' ' ',')|gateway=$gateway|protected_iface=$protected_iface|interface_policy=initially_unconfigured_pci_only"

root_1=
root_2=
root_3=
root_4=
root_5=
root_count=0
for root in /sys/bus/pci/devices/*; do
    [ -r "$root/class" ] || continue
    [ "$(cat "$root/class")" = 0x060400 ] || continue
    bdf=${root##*/}
    slot=$(slot_from_bdf "$bdf") || die 10 unexpected_host_bus_root_port
    width_for_slot "$slot" >/dev/null || die 11 unexpected_root_port_slot
    case "$slot" in
        1) [ -z "$root_1" ] || die 12 duplicate_root_port; root_1=$bdf ;;
        2) [ -z "$root_2" ] || die 12 duplicate_root_port; root_2=$bdf ;;
        3) [ -z "$root_3" ] || die 12 duplicate_root_port; root_3=$bdf ;;
        4) [ -z "$root_4" ] || die 12 duplicate_root_port; root_4=$bdf ;;
        5) [ -z "$root_5" ] || die 12 duplicate_root_port; root_5=$bdf ;;
    esac
    root_count=$((root_count + 1))
done

expected_count=0
for item in $expected; do
    slot=${item%%:*}
    width=${item#*:}
    case "$slot" in
        1) root_bdf=$root_1 ;;
        2) root_bdf=$root_2 ;;
        3) root_bdf=$root_3 ;;
        4) root_bdf=$root_4 ;;
        5) root_bdf=$root_5 ;;
    esac
    [ -n "$root_bdf" ] || die 13 missing_root_port
    validate_root_port "$slot" "$width" "$root_bdf" || die 14 invalid_root_port_linkcap
    validate_leaf_traffic "$slot" "$root_bdf" || die 15 leaf_functional_validation_failed
    expected_count=$((expected_count + 1))
done
[ "$root_count" -eq "$expected_count" ] || die 16 root_port_count_mismatch

emit "event=final|mode=$mode|status=PASS|ports=$expected_count|leaves=$expected_count"
trap - EXIT HUP INT TERM
exit 0

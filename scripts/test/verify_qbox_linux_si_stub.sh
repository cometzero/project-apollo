#!/bin/sh
# SPDX-License-Identifier: MIT
# Run inside an isolated AP-only guest. This configures ethsi1 for the test.
set -eu

iface=ethsi1
vlan=ethsi1.200
peer=192.168.1.1
address=192.168.1.2/24

test -d "/sys/class/net/${iface}"
if ip -o -4 addr show dev "${iface}" | grep -q ' inet '; then
    echo "SI_STUB_TEST: ethsi1 already has an IPv4 address; use a fresh guest" >&2
    exit 1
fi
if test -d "/sys/class/net/${vlan}"; then
    echo "SI_STUB_TEST: ethsi1.200 already exists; use a fresh guest" >&2
    exit 1
fi

attached=0
for state in /sys/class/remoteproc/remoteproc*/state; do
    test -f "${state}" || continue
    value=$(cat "${state}")
    echo "SI_STUB_REMOTEPROC path=${state} state=${value}"
    case "${value}" in attached|running) attached=1 ;; esac
done
test "${attached}" -eq 1
ls /sys/bus/rpmsg/devices

old_mtu=$(cat "/sys/class/net/${iface}/mtu")
# The vendor driver may initially expose Ethernet's default MTU 1500 even
# though ndo_change_mtu enforces its smaller RPMsg maximum. Keep a legal MTU.
if test "${old_mtu}" -gt 478; then old_mtu=478; fi
old_flags=$(cat "/sys/class/net/${iface}/flags")
cleanup() {
    ip link delete "${vlan}" 2>/dev/null || true
    ip addr del "${address}" dev "${iface}" 2>/dev/null || true
    ip link set "${iface}" mtu "${old_mtu}" || true
    if test "$((old_flags & 1))" -eq 0; then
        ip link set "${iface}" down || true
    fi
}
trap cleanup EXIT

# Linux virtio_rpmsg uses 512-byte buffers: 16 RPMsg + 18 tagged Ethernet
# header bytes leave 478 bytes for an IP packet.
ip link set "${iface}" mtu 478
ip link set "${iface}" up
before_rx=$(cat "/sys/class/net/${iface}/statistics/rx_packets")
before_tx=$(cat "/sys/class/net/${iface}/statistics/tx_packets")

check_ping() {
    if output=$(ping -I "$1" -c "$2" -i 0.05 -W 2 -s "$3" "${peer}" 2>&1); then
        printf '%s\n' "${output}"
        printf '%s\n' "${output}" | grep -Eq '[ ,]0% packet loss'
    else
        printf '%s\n' "${output}"
        return 1
    fi
}

ip addr add "${address}" dev "${iface}"
check_ping "${iface}" 40 56
check_ping "${iface}" 4 450
echo 'SI_STUB_TEST name=untagged_icmp result=PASS'
ip addr del "${address}" dev "${iface}"

ip link add link "${iface}" name "${vlan}" type vlan id 200
ip link set "${vlan}" mtu 478
ip addr add "${address}" dev "${vlan}"
ip link set "${vlan}" up
check_ping "${vlan}" 40 56
check_ping "${vlan}" 4 450
echo 'SI_STUB_TEST name=vlan200_icmp result=PASS'

after_rx=$(cat "/sys/class/net/${iface}/statistics/rx_packets")
after_tx=$(cat "/sys/class/net/${iface}/statistics/tx_packets")
test "$((after_rx - before_rx))" -ge 88
test "$((after_tx - before_tx))" -ge 88
echo "SI_STUB_COUNTERS rx_delta=$((after_rx - before_rx)) tx_delta=$((after_tx - before_tx))"
grep -E 'mhu|mailbox' /proc/interrupts || true
echo 'QBOX_SI_STUB_TRAFFIC_PASS'

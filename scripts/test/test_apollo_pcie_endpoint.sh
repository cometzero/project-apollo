#!/bin/sh
# SPDX-License-Identifier: MIT
#
# Configure the QBox EP loopback function and run the upstream RC kselftest.
# The caller must impose a host-side timeout: RC read/write/copy ioctls wait
# for the EP completion interrupt.

set -eu

CFG=/sys/kernel/config/pci_ep
CONTROLLER=${APOLLO_PCIE_EP_CONTROLLER:-30300000.pcie-epc}
FUNCTION=apollo_epf_test_0
VENDOR=0x16c3
DEVICE=0xedda
TOOL=${APOLLO_PCIE_EP_TEST_TOOL:-/usr/bin/pci_endpoint_test}
FUNCTION_DIR=$CFG/functions/pci_epf_test/$FUNCTION
CONTROLLER_DIR=$CFG/controllers/$CONTROLLER
LINK=$CONTROLLER_DIR/$FUNCTION
RC_PARENT=0000:00:01.0
EP_SYSFS=
STARTED=0
FUNCTION_CREATED=0
LINK_CREATED=0
OWNED_ENDPOINT=0
ENDPOINT_COUNT=0
FOUND_ENDPOINT=
RC_RESCAN=
RC_RESCAN_COUNT=0
FINAL_BDF=
FINAL_IRQ_BEFORE=
FINAL_IRQ_AFTER=

mark()
{
	printf 'APOLLO_PCIE_EP|v=1|%s\n' "$*"
}

fail()
{
	mark "event=fail|reason=$1"
	exit 1
}

id_matches()
{
	[ "$(cat "$1/vendor")" = "$VENDOR" ] &&
		[ "$(cat "$1/device")" = "$DEVICE" ]
}

scan_endpoints()
{
	ENDPOINT_COUNT=0
	FOUND_ENDPOINT=
	for candidate in /sys/bus/pci/devices/*; do
		[ -e "$candidate/vendor" ] || continue
		if id_matches "$candidate"; then
			ENDPOINT_COUNT=$((ENDPOINT_COUNT + 1))
			FOUND_ENDPOINT=$candidate
		fi
	done
}

find_rc_rescan()
{
	RC_RESCAN=
	RC_RESCAN_COUNT=0
	for candidate in /sys/bus/pci/devices/"$RC_PARENT"/pci_bus/*/rescan; do
		[ -e "$candidate" ] || continue
		RC_RESCAN_COUNT=$((RC_RESCAN_COUNT + 1))
		RC_RESCAN=$candidate
	done
}

endpoint_parent()
{
	basename "$(dirname "$(readlink -f "$1")")"
}

endpoint_is_owned()
{
	[ "$OWNED_ENDPOINT" -eq 1 ] && [ -n "$EP_SYSFS" ] &&
		[ -e "$EP_SYSFS/vendor" ] && id_matches "$EP_SYSFS" &&
		[ "$(endpoint_parent "$EP_SYSFS")" = "$RC_PARENT" ]
}

irq_total()
{
	total=0
	for irq in "$EP_SYSFS"/msi_irqs/*; do
		[ -e "$irq" ] || continue
		value=$(awk -v needle="$(basename "$irq"):" '
			$1 == needle {
				for (i = 2; i <= NF && $i ~ /^[0-9]+$/; i++)
					total += $i
			}
			END { print total + 0 }
		' /proc/interrupts)
		total=$((total + value))
	done
	printf '%s\n' "$total"
}

cleanup()
{
	test_rc=$1
	cleanup_rc=0
	set +e
	if endpoint_is_owned; then
		if ! printf 1 > "$EP_SYSFS/remove"; then
			mark "event=cleanup_error|step=endpoint_remove"
			cleanup_rc=1
		fi
		EP_SYSFS=
	fi
	if [ "$STARTED" -eq 1 ] && [ -e "$CONTROLLER_DIR/start" ]; then
		if ! printf 0 > "$CONTROLLER_DIR/start"; then
			mark "event=cleanup_error|step=controller_stop"
			cleanup_rc=1
		fi
	fi
	if [ "$LINK_CREATED" -eq 1 ] && [ -L "$LINK" ]; then
		if ! rm "$LINK"; then
			mark "event=cleanup_error|step=unlink_function"
			cleanup_rc=1
		fi
	fi
	if [ "$FUNCTION_CREATED" -eq 1 ] && [ -d "$FUNCTION_DIR" ]; then
		if ! rmdir "$FUNCTION_DIR"; then
			mark "event=cleanup_error|step=remove_function"
			cleanup_rc=1
		fi
	fi
	mark "event=cleanup|test_rc=$test_rc|cleanup_rc=$cleanup_rc"
	if [ "$test_rc" -eq 0 ] && [ "$cleanup_rc" -eq 0 ]; then
		mark "event=final|status=PASS|bdf=$FINAL_BDF|irq_before=$FINAL_IRQ_BEFORE|irq_after=$FINAL_IRQ_AFTER"
		return 0
	fi
	[ "$cleanup_rc" -eq 0 ] || return "$cleanup_rc"
	return "$test_rc"
}

on_exit()
{
	rc=$?
	trap - EXIT
	set +e
	cleanup "$rc"
	exit $?
}

on_signal()
{
	trap - EXIT HUP INT TERM
	mark "event=interrupted|signal=$1"
	set +e
	cleanup 1
	exit $?
}

trap on_exit EXIT
trap 'on_signal HUP' HUP
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM

[ "$(id -u)" -eq 0 ] || fail not_root
command -v "$TOOL" >/dev/null 2>&1 || fail missing_tool

modprobe configfs 2>/dev/null || :
modprobe pci_epf_test 2>/dev/null || :
modprobe pci_endpoint_test 2>/dev/null || :
if ! grep -qs ' /sys/kernel/config ' /proc/mounts; then
	mount -t configfs none /sys/kernel/config || fail configfs_mount
fi
[ -d "$CFG/functions/pci_epf_test" ] || fail missing_epf_test_configfs
[ -d "$CONTROLLER_DIR" ] || fail "missing_controller_$CONTROLLER"
[ ! -e "$FUNCTION_DIR" ] || fail existing_function
[ ! -e "$LINK" ] || fail existing_link
find_rc_rescan
[ "$RC_RESCAN_COUNT" -eq 1 ] || fail missing_or_ambiguous_rc_rescan
scan_endpoints
[ "$ENDPOINT_COUNT" -eq 0 ] || fail existing_test_endpoint

mkdir "$FUNCTION_DIR"
FUNCTION_CREATED=1
printf '%s\n' "$VENDOR" > "$FUNCTION_DIR/vendorid"
printf '%s\n' "$DEVICE" > "$FUNCTION_DIR/deviceid"
printf '%s\n' 32 > "$FUNCTION_DIR/msi_interrupts"
ln -s "$FUNCTION_DIR" "$LINK"
LINK_CREATED=1
printf 1 > "$CONTROLLER_DIR/start"
STARTED=1
mark "event=configured|controller=$CONTROLLER|function=$FUNCTION|vendor=$VENDOR|device=$DEVICE|msi=32|rescan=$RC_RESCAN"

attempt=0
while [ "$attempt" -lt 30 ]; do
	printf 1 > "$RC_RESCAN"
	scan_endpoints
	if [ "$ENDPOINT_COUNT" -eq 1 ] && [ -e /dev/pci-endpoint-test.0 ]; then
		EP_SYSFS=$FOUND_ENDPOINT
		OWNED_ENDPOINT=1
		break
	fi
	attempt=$((attempt + 1))
	sleep 1
done
[ -n "$EP_SYSFS" ] || fail endpoint_enumeration_timeout
[ -e /dev/pci-endpoint-test.0 ] || fail missing_endpoint_test_device

BDF=$(basename "$EP_SYSFS")
PARENT=$(endpoint_parent "$EP_SYSFS")
BUS=${BDF#*:}
BUS=${BUS%%:*}
DEVFN=${BDF##*:}
DEV=${DEVFN%%.*}
FN=${DEVFN#*.}
RID=$(printf '0x%04x' $((0x$BUS * 256 + 0x$DEV * 8 + 0x$FN)))
DRIVER=none
[ -L "$EP_SYSFS/driver" ] && DRIVER=$(basename "$(readlink -f "$EP_SYSFS/driver")")
IOMMU_GROUP=none
[ -L "$EP_SYSFS/iommu_group" ] && IOMMU_GROUP=$(basename "$(readlink -f "$EP_SYSFS/iommu_group")")
[ "$PARENT" = "$RC_PARENT" ] || fail unexpected_parent
[ "$DRIVER" = pci-endpoint-test ] || fail unexpected_driver
[ "$IOMMU_GROUP" != none ] || fail missing_iommu_group
IRQ_BEFORE=$(irq_total)
mark "event=endpoint|bdf=$BDF|parent=$PARENT|rid=$RID|driver=$DRIVER|iommu_group=$IOMMU_GROUP|irq_before=$IRQ_BEFORE|msi_allocation=by_kselftest"

run_tap()
{
	name=$1
	shift
	mark "event=tap_start|test=$name"
	"$TOOL" "$@"
	mark "event=tap_done|test=$name"
}

# BAR0 is the only implemented BAR.  The memcpy variant covers sizes
# 1, 1024, 1025, 1024000, and 1024001 without requiring EP DMA.
run_tap bar0 -r pci_ep_bar.BAR0.BAR_TEST
run_tap consecutive_bars -r pci_ep_basic.CONSECUTIVE_BAR_TEST
run_tap msi -r pci_ep_basic.MSI_TEST
set -- "$EP_SYSFS"/msi_irqs/*
[ -e "$1" ] || fail missing_msi_irqs
mark "event=msi_configured|vectors=$#"
run_tap read -r pci_ep_data_transfer.memcpy.READ_TEST
run_tap write -r pci_ep_data_transfer.memcpy.WRITE_TEST
run_tap copy -r pci_ep_data_transfer.memcpy.COPY_TEST

IRQ_AFTER=$(irq_total)
[ "$IRQ_AFTER" -gt "$IRQ_BEFORE" ] || fail no_msi_irq_delta
FINAL_BDF=$BDF
FINAL_IRQ_BEFORE=$IRQ_BEFORE
FINAL_IRQ_AFTER=$IRQ_AFTER

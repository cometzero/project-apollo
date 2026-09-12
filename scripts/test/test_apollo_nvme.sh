#!/bin/sh
# Validate the test-only QEMU NVMe SSD attached to Apollo PCIe root port 4.

set -u

PATH=/sbin:/usr/sbin:/bin:/usr/bin
LC_ALL=C
export PATH LC_ALL

mode=${1:-verify-only}
prefix=APOLLO_NVME
expected_serial=APOLLO-NVME-TEST
expected_root=0000:00:04.0
expected_sectors=524288
workdir=
preserve_workdir=0

emit()
{
	printf '%s|v=1|%s\n' "$prefix" "$*"
}

die()
{
	code=$1
	reason=$2
	emit "event=final|mode=$mode|status=FAIL|code=$code|reason=$reason"
	exit "$code"
}

cleanup()
{
	[ "$preserve_workdir" -eq 0 ] || return 0
	[ -n "$workdir" ] && [ -d "$workdir" ] || return 0
	rm -f "$workdir/page_4k.expected" "$workdir/page_4k.actual" \
		"$workdir/unaligned_8704.expected" \
		"$workdir/unaligned_8704.actual" \
		"$workdir/large_4m.expected" "$workdir/large_4m.actual"
	rmdir "$workdir"
}

trap cleanup EXIT
trap 'die 129 signal_HUP' HUP
trap 'die 130 signal_INT' INT
trap 'die 143 signal_TERM' TERM

driver_name()
{
	driver=$(readlink -f "$1/driver" 2>/dev/null) || return 1
	basename "$driver"
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

make_pattern()
{
	output=$1
	sectors=$2
	seed=$3
	awk -v sectors="$sectors" -v seed="$seed" 'BEGIN {
		for (sector = 0; sector < sectors; sector++)
			for (line = 0; line < 8; line++)
				printf "APOLLO-NVME|seed=%08x|sector=%08u|line=%u|0123456789abcd\n",
				       seed + sector, sector, line
	}' > "$output" || return 1
	[ "$(wc -c < "$output")" -eq $((sectors * 512)) ]
}

run_case()
{
	name=$1
	offset=$2
	block_size=$3
	blocks=$4
	seed=$5
	bytes=$((block_size * blocks))
	sectors=$((bytes / 512))
	payload=$workdir/$name.expected
	actual=$workdir/$name.actual

	make_pattern "$payload" "$sectors" "$seed" || return 1
	expected_hash=$(sha256sum "$payload" | awk '{ print $1 }') || return 1

	if [ "$mode" = write-read ]; then
		"$dd_tool" if="$payload" of="$device" bs="$block_size" \
			count="$blocks" seek="${offset}B" conv=fsync \
			oflag=direct status=none || return 1
	fi

	sync
	"$dd_tool" if="$device" of="$actual" bs="$block_size" \
		count="$blocks" skip="${offset}B" iflag=direct \
		status=none || return 1
	actual_hash=$(sha256sum "$actual" | awk '{ print $1 }') || return 1
	emit "event=data|mode=$mode|case=$name|offset_bytes=$offset|size_bytes=$bytes|actual_bytes=$(wc -c < "$actual")|io_block_size=$block_size|io_blocks=$blocks|expected_sha256=$expected_hash|actual_sha256=$actual_hash|direct_io=1"
	if [ "$actual_hash" != "$expected_hash" ]; then
		preserve_workdir=1
		emit "event=mismatch|expected_path=$payload|actual_path=$actual"
		return 1
	fi
}

case "$mode" in
	write-read|verify-only) ;;
	*) die 2 invalid_mode ;;
esac

[ "$(id -u)" -eq 0 ] || die 3 root_required
for command in awk dd.coreutils grep mktemp readlink sha256sum stat sync wc; do
	command -v "$command" >/dev/null 2>&1 || die 4 missing_command_$command
done
dd_tool=$(command -v dd.coreutils)
dd_help=$("$dd_tool" --help 2>&1) || die 6 dd_help_failed
printf '%s\n' "$dd_help" | grep -q "ends in 'B'" || die 7 dd_missing_byte_offsets
printf '%s\n' "$dd_help" | grep -q direct || die 8 dd_missing_direct_io
workdir=$(mktemp -d /tmp/apollo-nvme.XXXXXX) || die 9 temporary_directory_failed

controller=
controller_count=0
for candidate in /sys/class/nvme/nvme*; do
	[ -r "$candidate/serial" ] || continue
	serial=$(sed 's/[[:space:]]*$//' "$candidate/serial")
	[ "$serial" = "$expected_serial" ] || continue
	controller=$candidate
	controller_count=$((controller_count + 1))
done
[ "$controller_count" -eq 1 ] || die 10 expected_controller_not_unique

controller_name=${controller##*/}
controller_device=$(readlink -f "$controller/device") || die 11 controller_device_unresolved
endpoint_bdf=${controller_device##*/}
endpoint=/sys/bus/pci/devices/$endpoint_bdf
[ -d "$endpoint" ] || die 12 pci_endpoint_missing
[ "$(cat "$endpoint/class")" = 0x010802 ] || die 13 pci_class_mismatch
[ "$(driver_name "$endpoint")" = nvme ] || die 14 pci_driver_mismatch
case "$controller_device" in
	*/$expected_root/*) ;;
	*) die 15 root_port_mismatch ;;
esac
root_port=/sys/bus/pci/devices/$expected_root
[ "$(driver_name "$root_port")" = pcieport ] || die 60 root_port_driver_mismatch
[ "$(cat "$root_port/max_link_width")" = 2 ] || die 61 root_port_width_mismatch
[ "$(cat "$root_port/max_link_speed")" = "32.0 GT/s PCIe" ] || \
	die 62 root_port_speed_mismatch
[ -L "$endpoint/iommu_group" ] || die 16 iommu_group_missing
iommu_group=$(basename "$(readlink -f "$endpoint/iommu_group")")

irq_list=
for irq_path in "$endpoint"/msi_irqs/*; do
	[ -e "$irq_path" ] || continue
	irq_list="$irq_list ${irq_path##*/}"
done
irq_list=${irq_list# }
[ -n "$irq_list" ] || die 17 msi_irq_missing

namespace=
namespace_count=0
controller_real=$(readlink -f "$controller") || die 18 controller_unresolved
for candidate in /sys/class/block/"${controller_name}"n*; do
	[ -r "$candidate/size" ] || continue
	candidate_real=$(readlink -f "$candidate") || continue
	case "$candidate_real" in
		"$controller_real"/*) ;;
		*) continue ;;
	esac
	namespace=$candidate
	namespace_count=$((namespace_count + 1))
done
[ "$namespace_count" -eq 1 ] || die 19 expected_namespace_not_unique

namespace_name=${namespace##*/}
namespace_real=$(readlink -f "$namespace") || die 20 namespace_unresolved
device=/dev/$namespace_name
[ -b "$device" ] || die 21 namespace_device_missing
[ "$(cat "$namespace/size")" -eq "$expected_sectors" ] || die 22 namespace_size_mismatch
[ "$(cat "$namespace/queue/logical_block_size")" -eq 512 ] || die 23 logical_block_size_mismatch
[ "$(cat "$namespace/ro")" -eq 0 ] || die 24 namespace_read_only

devno=$(cat "$namespace/dev") || die 25 namespace_devno_missing
node_dev=$(stat -c '%t:%T' "$device") || die 26 namespace_node_stat_failed
node_major=${node_dev%%:*}
node_minor=${node_dev#*:}
if [ $((0x$node_major)) -ne "${devno%%:*}" ] || \
	[ $((0x$node_minor)) -ne "${devno#*:}" ]; then
	die 27 namespace_node_mismatch
fi
[ "$(readlink -f "/sys/dev/block/$devno")" = "$namespace_real" ] || die 28 namespace_devno_mismatch

for partition in "$namespace"/"${namespace_name}"p*; do
	[ -e "$partition" ] || continue
	die 29 namespace_has_partitions
done
for holder in "$namespace/holders"/*; do
	[ -e "$holder" ] || continue
	die 30 namespace_has_holders
done
awk -v dev="$devno" '$3 == dev { found = 1 } END { exit !found }' \
	/proc/self/mountinfo && die 31 namespace_is_mounted
while read -r swap _rest; do
	[ "$swap" = Filename ] && continue
	[ "$(readlink -f "$swap" 2>/dev/null)" = "$(readlink -f "$device")" ] && \
		die 32 namespace_is_swap
done < /proc/swaps

emit "event=contract|mode=$mode|serial=$expected_serial|root_port=$expected_root|expected_size_bytes=$((expected_sectors * 512))|write_limit_bytes=67108864|safety=unmounted_unpartitioned_no_holders"
current_link_speed=$(tr ' ' '_' < "$root_port/current_link_speed")
current_link_width=$(cat "$root_port/current_link_width")
emit "event=root_port|bdf=$expected_root|driver=pcieport|max_link_speed=32.0_GT/s_PCIe|max_link_width=2|current_link_speed=$current_link_speed|current_link_width=$current_link_width"
if [ "$current_link_speed" != 32.0_GT/s_PCIe ] || [ "$current_link_width" != 2 ]; then
	die 48 root_link_not_gen5_x2
fi
endpoint_max_speed=$(tr ' ' '_' < "$endpoint/max_link_speed")
endpoint_max_width=$(cat "$endpoint/max_link_width")
endpoint_speed=$(tr ' ' '_' < "$endpoint/current_link_speed")
endpoint_width=$(cat "$endpoint/current_link_width")
emit "event=endpoint_link|bdf=$endpoint_bdf|max_link_speed=$endpoint_max_speed|max_link_width=$endpoint_max_width|current_link_speed=$endpoint_speed|current_link_width=$endpoint_width"
if [ "$endpoint_max_speed" != 32.0_GT/s_PCIe ] || [ "$endpoint_max_width" != 2 ] || \
	[ "$endpoint_speed" != 32.0_GT/s_PCIe ] || [ "$endpoint_width" != 2 ]; then
	die 49 endpoint_link_not_gen5_x2
fi
emit "event=identify|controller=$controller_name|endpoint=$endpoint_bdf|class=0x010802|driver=nvme|namespace=$namespace_name|size_bytes=$((expected_sectors * 512))|logical_block_size=512|iommu_group=$iommu_group|msi_irqs=$(printf '%s' "$irq_list" | tr ' ' ',')"

read -r read_ios_before _ read_sectors_before _ \
	write_ios_before _ write_sectors_before _ \
	< "$namespace/stat" || die 33 initial_block_stats_failed
irq_before=$(sum_irq_counters "$irq_list") || die 34 initial_irq_stats_failed

# The three regions are non-overlapping and remain below the 64 MiB limit.
run_case page_4k 4194304 4096 1 101 || die 40 page_4k_failed
run_case unaligned_8704 1049088 8704 1 202 || die 41 unaligned_8704_failed
run_case large_4m 33554432 131072 32 303 || die 42 large_4m_failed

read -r read_ios_after _ read_sectors_after _ \
	write_ios_after _ write_sectors_after _ \
	< "$namespace/stat" || die 43 final_block_stats_failed
irq_after=$(sum_irq_counters "$irq_list") || die 44 final_irq_stats_failed
read_ios_delta=$((read_ios_after - read_ios_before))
read_sectors_delta=$((read_sectors_after - read_sectors_before))
write_ios_delta=$((write_ios_after - write_ios_before))
write_sectors_delta=$((write_sectors_after - write_sectors_before))
irq_delta=$((irq_after - irq_before))

[ "$read_ios_delta" -gt 0 ] || die 45 read_stats_not_advanced
if [ "$mode" = write-read ]; then
	[ "$write_ios_delta" -gt 0 ] || die 46 write_stats_not_advanced
fi
[ "$irq_delta" -gt 0 ] || die 47 msi_irq_not_advanced

emit "event=io_stats|read_ios_delta=$read_ios_delta|read_sectors_delta=$read_sectors_delta|write_ios_delta=$write_ios_delta|write_sectors_delta=$write_sectors_delta|irq_before=$irq_before|irq_after=$irq_after|irq_delta=$irq_delta"
emit "event=final|mode=$mode|status=PASS|controller=$controller_name|namespace=$namespace_name|endpoint=$endpoint_bdf"
trap - EXIT HUP INT TERM
cleanup
exit 0

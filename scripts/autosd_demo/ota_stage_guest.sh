#!/usr/bin/env bash
# Stage an official demo update on the dedicated OTA target; never reboot here.
set -euo pipefail
variant=${1:?good or bad}
expected_sha=${2:?expected archive SHA256}
case "$variant" in good) previous=0;; bad) previous=1;; *) exit 2;; esac
[[ "$expected_sha" =~ ^[0-9a-f]{64}$ ]]
test "$(uname -r)" = 6.18.5-rt3-yocto-preempt-rt
test -d /sys/firmware/efi
test -e /run/ostree-booted
test "$(getenforce)" = Enforcing
test "$(ukibootctl get-booted)" = "$previous"
test "$(ukibootctl get-active)" = "$previous"
systemctl is-active sysboot-health.target
systemctl is-active ukiboot-set-success.service
archive="/var/tmp/apollo-ota-$variant.oci.tar"
printf '%s  %s\n' "$expected_sha" "$archive" | sha256sum --check
printf 'OTA_STAGE_BEFORE=%s\n' "$variant"
cat /proc/sys/kernel/random/boot_id
bootc status --json
ukibootctl dump
sha256sum /boot/efi/EFI/BOOT/BOOTAA64.EFI
bootc switch --transport oci-archive "$archive"
printf 'OTA_STAGE_AFTER=%s\n' "$variant"
bootc status --json
ukibootctl dump
sha256sum /boot/efi/EFI/BOOT/BOOTAA64.EFI
printf 'APOLLO_OTA_%s_STAGING_COMMAND_COMPLETE_NOT_BOOT_VERIFIED\n' "$variant"

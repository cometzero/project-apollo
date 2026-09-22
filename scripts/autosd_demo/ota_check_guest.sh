#!/usr/bin/env bash
# Read-only acceptance probe after base/good/rollback boot has settled.
set -euo pipefail
require_active_units() {
    local unit
    for unit in "$@"; do
        systemctl is-active "$unit" || return
    done
}
phase=${1:?base, good, or rollback}
case "$phase" in base) expected=0;; good|rollback) expected=1;; *) exit 2;; esac
printf 'OTA_PHASE=%s\n' "$phase"
cat /proc/sys/kernel/random/boot_id
uname -a
test "$(uname -r)" = 6.18.5-rt3-yocto-preempt-rt
test -d /sys/firmware/efi
test -e /run/ostree-booted
test "$(getenforce)" = Enforcing
rpm -q kernel-apollo sysboot bootc
bootc status --json
cat /proc/cmdline
sha256sum /boot/efi/EFI/BOOT/BOOTAA64.EFI
findmnt /boot/efi
# Compare installed firmware and the packaged bootupd payload across updates.
find /usr/lib/bootupd/updates/EFI -type f -exec sha256sum {} \;
for attempt in $(seq 1 120); do
    systemctl is-active --quiet sysboot-health.target && break
    sleep 1
done
require_active_units sysboot-health.target ukiboot-set-success.service
journalctl -b -u sysboot-check@success.service -u sysboot-health.target -u ukiboot-set-success.service --no-pager
ukibootctl dump
test "$(ukibootctl get-booted)" = "$expected"
test "$(ukibootctl get-active)" = "$expected"
if test "$phase" != base; then
    systemctl is-active httpd.service
    rpm -q httpd
    if rpm -q gcc; then
        echo 'Bad-update-only gcc unexpectedly remains in the accepted deployment' >&2
        exit 1
    fi
    test ! -e /usr/lib/systemd/system/sysboot-check@failure.service.d/failure.conf
fi
printf 'APOLLO_OTA_%s_STATE_PASS\n' "$phase"

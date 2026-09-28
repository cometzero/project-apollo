#!/bin/bash
# Read-only current-boot diagnostics (only the evidence directory is written).
set -eu
out=${1:?usage: collect_boot_diagnostics.sh NEW_OUTPUT_DIRECTORY}
mkdir "$out"
timeout -k 5s 30s systemd-analyze time > "$out/time.txt" 2>&1 || true
timeout -k 5s 30s systemd-analyze blame --no-pager > "$out/blame.txt" 2>&1 || true
journalctl -b --no-pager -o short-monotonic > "$out/journal.txt"
journalctl -b -p warning --no-pager -o short-monotonic > "$out/warnings.txt"
journalctl -b -k --no-pager -o short-monotonic > "$out/kernel.txt"
systemctl --failed --no-pager > "$out/failed.txt"
systemctl show systemd-udevd systemd-udev-trigger systemd-journald \
    NetworkManager-wait-online apollo-pfdi qm apollo-adas > "$out/services.txt"
{ uname -a; cat /proc/cmdline; cat /proc/uptime; if test -f /etc/fstab; then cat /etc/fstab; fi; lsmod; } > "$out/platform.txt"
{ systemctl cat systemd-udevd systemd-udev-trigger systemd-journald; \
  cat /etc/udev/udev.conf; } > "$out/udev-config.txt" 2>&1 || true
timeout -k 5s 30s systemd-analyze critical-chain --no-pager > "$out/critical-chain.txt" 2>&1 || true
timeout -k 5s 30s systemd-analyze plot > "$out/boot.svg" 2>&1 || true
tar -czf "$out.tar.gz" -C "$out" .
cat "$out/time.txt" "$out/critical-chain.txt" "$out/failed.txt"

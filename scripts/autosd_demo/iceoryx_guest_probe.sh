#!/usr/bin/env bash
# Run only after the caller installs the same payload/config in root and QM,
# and provisions the official shared /tmp/iceoryx2 volume. Enforcing is preferred;
# an explicitly requested private-guest comparison restores the original mode.
set -euo pipefail
permissive=0
if test "${1:-}" = --private-guest-permissive; then
  permissive=1
  shift
fi
payload=${1:?Usage: iceoryx_guest_probe.sh [--private-guest-permissive] ABSOLUTE_PAYLOAD_DIR NEW_LOG_DIR}
logs=${2:?Usage: iceoryx_guest_probe.sh ABSOLUTE_PAYLOAD_DIR NEW_LOG_DIR}
case "$payload" in /*) ;; *) echo 'payload must be absolute' >&2; exit 2;; esac
mkdir -- "$logs"
logs=$(realpath -- "$logs")
started=$(date +%s)
initial_mode=$(getenforce)
publisher_pid=
restore_mode=0
cleanup() {
  result=$?
  trap - EXIT INT TERM
  if test -n "$publisher_pid"; then
    kill -INT "$publisher_pid" 2>/dev/null || true
    wait "$publisher_pid" 2>/dev/null || true
  fi
  if test "$restore_mode" -eq 1; then
    setenforce 1 || result=1
  fi
  getenforce > "$logs/selinux-final.txt" || result=1
  journalctl -k --since "@$started" --no-pager > "$logs/kernel-journal.log" 2>&1 || true
  if command -v ausearch >/dev/null; then
    ausearch -m AVC,USER_AVC -ts recent > "$logs/audit-recent.log" 2>&1 || true
  fi
  printf 'exit_code=%s initial_selinux=%s permissive_comparison=%s\n' \
    "$result" "$initial_mode" "$permissive" > "$logs/result.txt"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%s\n' "$initial_mode" > "$logs/selinux-initial.txt"
if test "$permissive" -eq 1 && test "$initial_mode" = Enforcing; then
  echo 'Explicit temporary permissive comparison: use only a private demo VM.'
  # Set restoration intent first so even an interrupt during setenforce restores.
  restore_mode=1
  setenforce 0
fi
test -x "$payload/publisher"
test -f "$payload/config/iceoryx2.toml"
systemctl is-active qm
podman exec qm test -x "$payload/subscriber"
podman exec qm test -r "$payload/config/iceoryx2.toml"
getenforce | tee "$logs/selinux-mode.txt"
podman inspect qm > "$logs/qm-inspect.json"
cd -- "$payload"
timeout -s INT -k 3 30 ./publisher > "$logs/publisher.log" 2>&1 &
publisher_pid=$!
sleep 2
subscriber_rc=0
podman exec --workdir "$payload" qm timeout -s INT -k 3 15 ./subscriber \
  > "$logs/subscriber.log" 2>&1 || subscriber_rc=$?
cat "$logs/publisher.log" "$logs/subscriber.log"
test "$subscriber_rc" -eq 0 || test "$subscriber_rc" -eq 124
test "$(grep -c 'Send sample' "$logs/publisher.log")" -ge 3
test "$(grep -c 'received: TransmissionData' "$logs/subscriber.log")" -ge 3
printf 'ICEORYX_ROOT_QM_TRAFFIC_PASS selinux=%s\n' "$(cat "$logs/selinux-mode.txt")"
printf 'permissive_comparison=%s\n' "$permissive"
printf '%s\n' 'No latency, safety certification, or complete SELinux policy qualification.'

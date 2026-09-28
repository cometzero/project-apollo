#!/bin/bash
# Validate the real flightrecorder and udev reload using an isolated trace buffer.
set -euo pipefail
unit=trace-cmd.service
instance=apollo-policy-validation
trace_root=/sys/kernel/tracing
instance_path=$trace_root/instances/$instance
dropin=/run/systemd/system/trace-cmd.service.d/99-apollo-policy-validation.conf
marker=/run/apollo-trace-cmd-flightrecorder
module=/sys/module/virtio_net

test "$(id -u)" = 0
test "$(systemctl show "$unit" -p ActiveState --value)" = inactive
test ! -e "$dropin" && test ! -L "$dropin"
test ! -e "$instance_path" && test ! -e "$marker"
test -e "$module/uevent"
test "$(cat "$trace_root/current_tracer")" = nop
test "$(cat "$trace_root/events/enable")" = 0
if grep -q '^[^#[:space:]]' "$trace_root/trace"; then
    echo 'SKIP: existing global trace data must be preserved'
    exit 77
fi
global_state=$(cat "$trace_root/current_tracer" "$trace_root/events/enable" \
    "$trace_root/tracing_on" "$trace_root/buffer_size_kb")
owned=0
cleanup() {
    result=$?
    trap - EXIT
    if test "$owned" = 1; then
        timeout 30s systemctl stop "$unit" || result=1
        rm -f -- "$dropin"
        timeout 30s systemctl daemon-reload || result=1
        if test -d "$instance_path"; then
            rmdir -- "$instance_path" || result=1
        fi
        test ! -e "$marker" || result=1
        test "$(systemctl show "$unit" -p ActiveState --value)" = inactive || result=1
        test "$(cat "$trace_root/current_tracer" "$trace_root/events/enable" \
            "$trace_root/tracing_on" "$trace_root/buffer_size_kb")" = "$global_state" || result=1
    fi
    echo "TRACE_POLICY_CLEANUP_RC=$result"
    exit "$result"
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
mkdir -p -- "${dropin%/*}"
set -o noclobber
cat > "$dropin" <<'EOF'
[Service]
EnvironmentFile=
Environment="OPTS=-B apollo-policy-validation -b 64 -e sched:sched_switch"
ExecStop=
ExecStop=/usr/bin/trace-cmd reset -B apollo-policy-validation
EOF
owned=1
restorecon "$dropin"
timeout 30s systemctl daemon-reload
timeout 30s systemctl start "$unit"
test "$(systemctl show "$unit" -p ActiveState --value)" = active
test -d "$marker" && test -d "$instance_path"
test "$(cat "$instance_path/events/sched/sched_switch/enable")" = 1
before=$(systemctl show "$unit" -p ExecReload --value)
timeout 30s udevadm trigger --action=add --settle "$module"
after=$(systemctl show "$unit" -p ExecReload --value)
test "$before" != "$after"
printf 'ACTIVE_RELOAD_BEFORE=%s\nACTIVE_RELOAD_AFTER=%s\n' "$before" "$after"
test "$(systemctl show "$unit" -p ActiveState --value)" = active
timeout 30s systemctl stop "$unit"
test ! -e "$marker"
before=$(systemctl show "$unit" -p ExecReload --value)
timeout 30s udevadm trigger --action=add --settle "$module"
after=$(systemctl show "$unit" -p ExecReload --value)
test "$before" = "$after"
test "$(systemctl show "$unit" -p ActiveState --value)" = inactive
echo 'TRACE_POLICY_ACTIVE_RELOAD_AND_INACTIVE_GUARD_PASS'

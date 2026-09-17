#!/bin/sh
# SPDX-License-Identifier: MIT
# Three bound at24 slaves on one adapter, with concurrent guest clients.
# Linux serializes bus transfers; this tests target isolation under contention,
# not physically simultaneous transfers on the SDA/SCL pair.
set -u
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH
prefix=APOLLO_I2C_MULTI_SLAVE
clients='0-0050 0-0051 0-0052'
bytes=256
rounds=8
work=
pids=

emit()
{
    printf '%s|v=1|%s\n' "$prefix" "$*"
}

die()
{
    emit "event=fail|reason=$*"
    exit 1
}

read_image()
{
    dd if="/sys/bus/i2c/devices/$1/eeprom" of="$2" bs="$bytes" count=1 2> "$2.dd-stderr" &&
        [ "$(wc -c < "$2")" -eq "$bytes" ]
}

# shellcheck disable=SC2317 # EXIT trap handler.
cleanup()
{
    status=$?
    trap - EXIT HUP INT TERM
    for pid in $pids; do kill "$pid" 2>/dev/null || true; done
    for pid in $pids; do wait "$pid" 2>/dev/null || true; done
    restore_ok=1
    if [ -n "$work" ]; then
        for client in $clients; do
            [ -f "$work/$client.saved" ] || continue
            if cat "$work/$client.original" > "/sys/bus/i2c/devices/$client/eeprom" &&
                read_image "$client" "$work/$client.restored" &&
                cmp -s "$work/$client.original" "$work/$client.restored"; then
                emit "event=restore|client=$client|status=PASS"
            else
                emit "event=restore|client=$client|status=FAIL|backup=$work/$client.original"
                restore_ok=0
                status=1
            fi
        done
        if [ "$restore_ok" -eq 1 ] && [ "$status" -eq 0 ]; then
            rm -rf "$work"
        else
            emit "event=artifacts|path=$work|reason=failure-evidence"
        fi
    fi
    if [ "$status" -eq 0 ]; then
        emit "event=final|status=PASS|clients=3|rounds=$rounds|bytes=$bytes"
    else
        emit "event=final|status=FAIL|rc=$status"
    fi
    exit "$status"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

worker_failure()
{
    phase=$1
    phase_rc=$2
    expected_size=missing
    actual_size=missing
    [ ! -f "$work/$worker_client.expected" ] ||
        expected_size=$(wc -c < "$work/$worker_client.expected")
    [ ! -f "$work/$worker_client.actual" ] ||
        actual_size=$(wc -c < "$work/$worker_client.actual")
    emit "event=worker-fail|client=$worker_client|round=$round|phase=$phase|rc=$phase_rc|expected_bytes=$expected_size|actual_bytes=$actual_size|artifacts=$work" > "$work/$worker_client.failure"
    cat "$work/$worker_client.failure"
    if [ "$phase" = compare ] || [ "$phase" = read ]; then
        cmp -l "$work/$worker_client.expected" "$work/$worker_client.actual" > "$work/$worker_client.diff" 2>&1 || true
        # cmp offsets are one-based; byte values are octal. Retain the full diff.
        awk -v prefix="$prefix" -v client="$worker_client" -v round="$round" '
            NR <= 16 { printf "%s|v=1|event=byte-diff|client=%s|round=%s|offset1_expectedOct_actualOct=%s\n", prefix, client, round, $0 }
        ' "$work/$worker_client.diff"
    fi
    if [ -f "$work/$worker_client.actual.dd-stderr" ]; then
        cat "$work/$worker_client.actual.dd-stderr"
    fi
    if [ -f "$work/$worker_client.write-stderr" ]; then
        cat "$work/$worker_client.write-stderr"
    fi
    return 1
}

worker()
{
    worker_client=$1
    seed=$2
    : > "$work/$worker_client.ready" || return 1
    while [ ! -f "$work/start" ]; do sleep 0.01; done
    round=1
    while [ "$round" -le "$rounds" ]; do
        # Distinct byte sequences per target and round cover all 32 EEPROM pages.
        awk -v seed="$seed" -v round="$round" -v bytes="$bytes" 'BEGIN {
            for (i = 0; i < bytes; i++)
                printf "%c", 33 + ((i * 17 + seed * 23 + round * 7) % 94)
        }' > "$work/$worker_client.expected" || {
            worker_failure pattern "$?"; return 1;
        }
        rm -f "$work/$worker_client.actual" "$work/$worker_client.actual.dd-stderr"
        cat "$work/$worker_client.expected" > "/sys/bus/i2c/devices/$worker_client/eeprom" 2> "$work/$worker_client.write-stderr" || {
            worker_failure write "$?"; return 1;
        }
        read_image "$worker_client" "$work/$worker_client.actual" || {
            worker_failure read "$?"; return 1;
        }
        cmp -s "$work/$worker_client.expected" "$work/$worker_client.actual" || {
            worker_failure compare "$?"; return 1;
        }
        emit "event=transfer|client=$worker_client|round=$round|bytes=$bytes|status=PASS"
        round=$((round + 1))
    done
}

for tool in awk basename cat cmp dd mktemp readlink rm sleep wc; do
    command -v "$tool" >/dev/null 2>&1 || die "missing-$tool"
done
work=$(mktemp -d /tmp/qbox-i2c-multi.XXXXXX) || die "mktemp-failed"
for client in $clients; do
    device=/sys/bus/i2c/devices/$client
    [ "$(basename "$(readlink -f "$device/driver")")" = at24 ] || die "at24-not-bound-$client"
    if ! [ -r "$device/eeprom" ] || ! [ -w "$device/eeprom" ]; then
        die "eeprom-not-accessible-$client"
    fi
    read_image "$client" "$work/$client.original" || die "backup-failed-$client"
    : > "$work/$client.saved" || die "backup-marker-failed-$client"
done

seed=0
for client in $clients; do
    # Clear parent traps in workers so only the parent restores the EEPROMs.
    (trap - EXIT HUP INT TERM; worker "$client" "$seed") &
    pids="$pids $!"
    seed=$((seed + 1))
done
attempt=0
while :; do
    ready=0
    for client in $clients; do
        [ ! -f "$work/$client.ready" ] || ready=$((ready + 1))
    done
    [ "$ready" -lt 3 ] || break
    attempt=$((attempt + 1))
    [ "$attempt" -le 500 ] || die "worker-barrier-timeout"
    sleep 0.01
done
emit 'event=concurrency|adapter=i2c-0|clients=0-0050,0-0051,0-0052|workers=3|bus_access=serialized'
: > "$work/start" || die "start-marker-failed"
worker_failed=0
for pid in $pids; do
    wait "$pid" || worker_failed=1
done
pids=
[ "$worker_failed" -eq 0 ] || die "concurrent-worker-failed"
for client in $clients; do
    read_image "$client" "$work/$client.final" || die "final-read-failed-$client"
    cmp -s "$work/$client.expected" "$work/$client.final" || die "target-isolation-failed-$client"
    emit "event=isolation|client=$client|status=PASS"
done
exit 0

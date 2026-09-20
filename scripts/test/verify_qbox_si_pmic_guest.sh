#!/bin/sh
# SPDX-License-Identifier: MIT
# Read-only Linux ownership check with one SI CL0-owned PMIC at 0x48.
# SCP boot validation and EEPROM concurrent traffic are separate checks.
set -eu
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH
prefix=APOLLO_SI_PMIC_GUEST
emit() { printf '%s|v=1|%s\n' "$prefix" "$*"; }
fail() { emit "event=final|status=FAIL|reason=$*"; exit 1; }

for device in /sys/bus/i2c/devices/*; do
    [ -r "$device/name" ] || continue
    case "$(cat "$device/name")" in
        *tps6594*) fail "linux-pmic-present-$(basename "$device")" ;;
    esac
done
for device in /sys/class/regulator/regulator*; do
    [ -r "$device/name" ] || continue
    case "$(cat "$device/name")" in
        *tps6594*) fail "linux-pmic-regulator-present" ;;
    esac
done
for device in /sys/bus/platform/devices/*; do
    case "$(basename "$device")" in
        *tps6594*) fail "linux-pmic-child-present" ;;
    esac
done
emit 'event=ownership|pmics=0|regulators=0|children=0|status=PASS'

pl031=0
for device in /sys/class/rtc/rtc*; do
    [ -e "$device/device/driver" ] || continue
    driver=$(basename "$(readlink -f "$device/device/driver")")
    [ "$driver" != rtc-pl031 ] || pl031=$((pl031 + 1))
    [ "$driver" != tps6594-rtc ] || fail linux-pmic-rtc-present
done
[ "$pl031" -ge 1 ] || fail missing-pl031
emit "event=rtc|driver=rtc-pl031|count=$pl031|status=PASS"

for client in 0-0050 0-0051 0-0052; do
    device=/sys/bus/i2c/devices/$client
    [ -r "$device/eeprom" ] || fail "missing-eeprom-$client"
    [ "$(basename "$(readlink -f "$device/driver")")" = at24 ] ||
        fail "unexpected-eeprom-driver-$client"
    emit "event=eeprom|client=$client|driver=at24|status=PASS"
done
emit 'event=final|status=PASS|pmics=0|eeproms=3|rtc=pl031'

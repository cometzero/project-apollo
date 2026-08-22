from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final

from .types import (
    AssertionObservation,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
)


NETWORK_ENDPOINT: Final = "http://10.0.2.100:18080/apollo-qbox-net"
PRIMARY_PROMPT: Final = r"(?m)(?:nexios-bsp#|root@apollo-qvp[^\n]*[#>])\s*$"

TRANSPORT_COMMAND: Final = (
    "printf 'transport_uname='; uname -a; "
    "printf 'transport_possible='; cat /sys/devices/system/cpu/possible; "
    "printf 'transport_present='; cat /sys/devices/system/cpu/present; "
    "printf 'transport_online='; cat /sys/devices/system/cpu/online; "
    "printf 'transport_dt_cpu_count='; find /sys/firmware/devicetree/base/cpus "
    "-maxdepth 1 -name 'cpu@*' | wc -l; "
    "printf 'transport_nproc='; nproc --all; "
    "printf 'transport_dsu_size='; cat "
    "/sys/devices/system/cpu/cpu0/cache/index3/size; "
    "printf 'transport_dsu_shared='; cat "
    "/sys/devices/system/cpu/cpu0/cache/index3/shared_cpu_list; "
    "out=$(perf stat -e arm_dsu_0/event=0x002a/ -- true 2>&1); "
    "counter=$(printf '%s\\n' \"$out\" | tr -d ',' | sed -n "
    "'s/^[[:space:]]*\\([0-9][0-9]*\\)[[:space:]].*/\\1/p' | head -1); "
    "printf 'transport_dsu_counter=%s\\n' \"${counter:-none}\"; "
    "printf 'transport_rc=0\\n'"
)

NETWORK_COMMAND: Final = (
    "printf 'network_interface=eth0\\n'; "
    "driver=$(basename \"$(readlink -f /sys/class/net/eth0/device/driver "
    "2>/dev/null)\" 2>/dev/null || true); "
    "printf 'network_driver=%s\\n' \"${driver:-none}\"; "
    "route_iface=; for retry in $(seq 1 20); do route_iface=$(ip route show "
    "default 2>/dev/null | awk 'NR==1 {for (i=1; i<=NF; i++) if "
    "($i == \"dev\") print $(i+1)}'); [ -n \"$route_iface\" ] && break; "
    "sleep 1; done; printf 'network_route_interface=%s\\n' "
    "\"${route_iface:-none}\"; "
    "addr=$(ip -4 -o addr show dev \"$route_iface\" 2>/dev/null | "
    "awk 'NR==1 {print $4}'); printf 'network_ipv4=%s\\n' \"${addr:-none}\"; "
    "route=$(ip route show default dev \"$route_iface\" 2>/dev/null | "
    "awk 'NR==1 {print $3}'); "
    "printf 'network_default_route=%s\\n' \"${route:-none}\"; "
    f"body=$(wget -qO- '{NETWORK_ENDPOINT}'); status=$?; "
    "printf 'network_http_status=%s\\n' \"$status\"; "
    "printf 'network_http_body=%s\\n' \"$body\""
)

RTC_COMMAND: Final = (
    "rtc=$(basename \"$(find /sys/class/rtc -maxdepth 1 -type l | head -1)\"); "
    "printf 'rtc_device=%s\\n' \"${rtc:-none}\"; "
    "driver=$(basename \"$(readlink -f /sys/class/rtc/$rtc/device/driver "
    "2>/dev/null)\" 2>/dev/null || true); "
    "printf 'rtc_driver=%s\\n' \"${driver:-none}\"; "
    "hwclock >/dev/null 2>&1; printf 'rtc_hwclock_status=%s\\n' \"$?\""
)

HOTPLUG_COMMAND: Final = (
    "initial=$(cat /sys/devices/system/cpu/online); status=0; "
    "restore() { for cpu in 1 2 3; do echo 1 > "
    "/sys/devices/system/cpu/cpu$cpu/online 2>/dev/null || status=1; done; }; "
    "trap restore EXIT; printf 'hotplug_initial=%s\\n' \"$initial\"; "
    "for cpu in 1 2 3; do echo 0 > /sys/devices/system/cpu/cpu$cpu/online "
    "2>/dev/null || status=1; printf 'hotplug_cpu%s_offline=' \"$cpu\"; "
    "cat /sys/devices/system/cpu/cpu$cpu/online; echo 1 > "
    "/sys/devices/system/cpu/cpu$cpu/online 2>/dev/null || status=1; "
    "printf 'hotplug_cpu%s_online=' \"$cpu\"; cat "
    "/sys/devices/system/cpu/cpu$cpu/online; done; restore; trap - EXIT; "
    "printf 'hotplug_restored='; cat /sys/devices/system/cpu/online; "
    "printf 'hotplug_status=%s\\n' \"$status\""
)

RNG_COMMAND: Final = (
    "printf 'rng_available='; cat "
    "/sys/devices/virtual/misc/hw_random/rng_available; "
    "printf 'rng_current='; cat "
    "/sys/devices/virtual/misc/hw_random/rng_current; "
    "bytes=$(dd if=/dev/hwrng bs=32 count=1 2>/dev/null | wc -c); "
    "printf 'rng_bytes=%s\\n' \"$bytes\"; "
    "test \"$bytes\" -eq 32; printf 'rng_status=%s\\n' \"$?\""
)

WATCHDOG_COMMAND: Final = (
    "watchdog=$(basename \"$(find /sys/class/watchdog -maxdepth 1 -type l | "
    "head -1)\"); printf 'watchdog_device=%s\\n' \"${watchdog:-none}\"; "
    "driver=$(basename \"$(readlink -f /sys/class/watchdog/$watchdog/device/driver "
    "2>/dev/null)\" 2>/dev/null || true); "
    "printf 'watchdog_driver=%s\\n' \"${driver:-none}\"; "
    "test -c /dev/watchdog0; printf 'watchdog_status=%s\\n' \"$?\""
)


def _all(output: str, patterns: tuple[str, ...]) -> bool:
    return all(re.search(pattern, output) is not None for pattern in patterns)


@dataclass(frozen=True, slots=True)
class PlatformDevicesEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        padded = (*outputs, "", "", "", "", "", "")[:6]
        transport, network, rtc, hotplug, rng, watchdog = padded
        checks = {
            "primary-ssh": _all(
                transport,
                (
                    r"transport_uname=Linux apollo-qvp .+ aarch64",
                    r"transport_possible=0-3",
                    r"transport_present=0-3",
                    r"transport_online=0-3",
                    r"transport_dt_cpu_count=4",
                    r"transport_nproc=4",
                    r"transport_dsu_size=4096K",
                    r"transport_dsu_shared=0-3",
                    r"transport_dsu_counter=[0-9]+",
                    r"transport_rc=0",
                ),
            ),
            "platform-device-networking": _all(
                network,
                (
                    r"network_interface=[^\s]+",
                    r"network_driver=virtio_net",
                    r"network_route_interface=ovsbr0",
                    r"network_ipv4=10\.0\.2\.[0-9]+/[0-9]+",
                    r"network_default_route=10\.0\.2\.2",
                    r"network_http_status=0",
                    r"network_http_body=APOLLO_QBOX_NET_OK(?:\r?$)",
                ),
            ),
            "platform-device-rtc": _all(
                rtc,
                (r"rtc_device=rtc[0-9]+", r"rtc_driver=rtc-pl031", r"rtc_hwclock_status=0"),
            ),
            "platform-device-cpu-hotplug": _all(
                hotplug,
                (
                    r"hotplug_initial=0-3",
                    r"hotplug_cpu1_offline=0",
                    r"hotplug_cpu1_online=1",
                    r"hotplug_cpu2_offline=0",
                    r"hotplug_cpu2_online=1",
                    r"hotplug_cpu3_offline=0",
                    r"hotplug_cpu3_online=1",
                    r"hotplug_restored=0-3",
                    r"hotplug_status=0",
                ),
            ),
            "platform-device-virtiorng": _all(
                rng,
                (r"rng_available=.*virtio_rng\.0", r"rng_current=virtio_rng\.0", r"rng_bytes=32", r"rng_status=0"),
            ),
            "platform-device-watchdog": _all(
                watchdog,
                (r"watchdog_device=watchdog[0-9]+", r"watchdog_driver=(?:sp805-wdt|sbsa-gwdt)", r"watchdog_status=0"),
            ),
            "systemd-boot-message": _all(
                snapshot.primary,
                (r"chainloading systemd-boot for slot [AB]", r"Boot in [0-9]+"),
            ),
        }
        return tuple(
            AssertionObservation(item, "PASS" if checks[item] else "FAIL")
            for item in self.expected
        )


@dataclass(frozen=True, slots=True)
class PlatformDevicesCleanup:
    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(True, "guest_commands_restored_cpus")


def platform_devices_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    commands = (
        TRANSPORT_COMMAND,
        NETWORK_COMMAND,
        RTC_COMMAND,
        HOTPLUG_COMMAND,
        RNG_COMMAND,
        WATCHDOG_COMMAND,
    )
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        tuple(ProbeStep(Console.PRIMARY, item, PRIMARY_PROMPT, 240.0) for item in commands),
        expected,
        coverage_kind,
        PlatformDevicesEvaluator(expected),
        PlatformDevicesCleanup(),
        None,
    )

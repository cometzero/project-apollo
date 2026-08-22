from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from scripts.run.qbox_validation.registry import (
    canonical_matrix_path,
    resolve_profile,
)
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot


ROOT = Path(__file__).resolve().parents[1]


def _outputs() -> tuple[str, ...]:
    return (
        """
transport_uname=Linux apollo-qvp 6.18.5 aarch64 GNU/Linux
transport_possible=0-3
transport_present=0-3
transport_online=0-3
transport_dt_cpu_count=4
transport_nproc=4
transport_dsu_size=4096K
transport_dsu_shared=0-3
transport_dsu_counter=23
transport_rc=0
""",
        """
network_interface=eth0
network_driver=virtio_net
network_route_interface=ovsbr0
network_ipv4=10.0.2.15/24
network_default_route=10.0.2.2
network_http_status=0
network_http_body=APOLLO_QBOX_NET_OK
""",
        """
rtc_device=rtc0
rtc_driver=rtc-pl031
rtc_hwclock_status=0
""",
        """
hotplug_initial=0-3
hotplug_cpu1_offline=0
hotplug_cpu1_online=1
hotplug_cpu2_offline=0
hotplug_cpu2_online=1
hotplug_cpu3_offline=0
hotplug_cpu3_online=1
hotplug_restored=0-3
hotplug_status=0
""",
        """
rng_available=virtio_rng.0
rng_current=virtio_rng.0
rng_bytes=32
rng_status=0
""",
        """
watchdog_device=watchdog0
watchdog_driver=sbsa-gwdt
watchdog_status=0
""",
    )


def _snapshot() -> ConsoleSnapshot:
    return ConsoleSnapshot(
        primary=(
            "auto-ad-nexios: chainloading systemd-boot for slot A\n"
            "systemd-boot: Boot in 3 s\n"
            "root@apollo-qvp:~# "
        )
    )


def _statuses(
    snapshot: ConsoleSnapshot,
    outputs: tuple[str, ...],
) -> dict[str, str]:
    spec = resolve_profile("platform-devices", canonical_matrix_path())
    result = evaluate_profile_result(spec, snapshot, outputs)
    return {item["id"]: item["status"] for item in result["assertions"]}


def test_platform_device_profile_uses_real_guest_surfaces() -> None:
    spec = resolve_profile("platform-devices", canonical_matrix_path())

    assert spec.coverage_kind == "semantic"
    assert spec.required_consoles == frozenset({Console.PRIMARY})
    assert len(spec.steps) == 6
    commands = "\n".join(step.command for step in spec.steps)
    assert "/sys/class/net/eth0/device/driver" in commands
    assert "route_iface=$(ip route show default" in commands
    assert "network_route_interface=%s" in commands
    assert "10.0.2.100:18080/apollo-qbox-net" in commands
    assert "/sys/class/rtc" in commands
    assert "/sys/devices/system/cpu" in commands
    assert "trap" in commands
    assert "/dev/hwrng" in commands
    assert "/sys/class/watchdog" in commands


def test_platform_device_evaluator_accepts_complete_evidence() -> None:
    statuses = _statuses(_snapshot(), _outputs())

    assert statuses == {
        "platform-device-networking": "PASS",
        "platform-device-rtc": "PASS",
        "platform-device-cpu-hotplug": "PASS",
        "platform-device-virtiorng": "PASS",
        "platform-device-watchdog": "PASS",
        "primary-ssh": "PASS",
        "systemd-boot-message": "PASS",
    }


@pytest.mark.parametrize(
    ("index", "old", "new", "assertion_id"),
    (
        (0, "transport_dsu_counter=23", "transport_dsu_counter=none", "primary-ssh"),
        (1, "APOLLO_QBOX_NET_OK", "WRONG", "platform-device-networking"),
        (1, "network_driver=virtio_net", "network_driver=none", "platform-device-networking"),
        (1, "network_route_interface=ovsbr0", "network_route_interface=brsi1", "platform-device-networking"),
        (2, "rtc_driver=rtc-pl031", "rtc_driver=none", "platform-device-rtc"),
        (3, "hotplug_restored=0-3", "hotplug_restored=0-2", "platform-device-cpu-hotplug"),
        (4, "rng_bytes=32", "rng_bytes=0", "platform-device-virtiorng"),
        (5, "watchdog_driver=sbsa-gwdt", "watchdog_driver=none", "platform-device-watchdog"),
    ),
)
def test_platform_device_evaluator_rejects_malformed_output(
    index: int,
    old: str,
    new: str,
    assertion_id: str,
) -> None:
    outputs = list(_outputs())
    outputs[index] = outputs[index].replace(old, new)

    assert _statuses(_snapshot(), tuple(outputs))[assertion_id] == "FAIL"


def test_platform_device_evaluator_requires_actual_systemd_boot_marker() -> None:
    snapshot = replace(
        _snapshot(),
        primary="Booting Linux on physical CPU 0\nroot@apollo-qvp:~# ",
    )

    assert _statuses(snapshot, _outputs())["systemd-boot-message"] == "FAIL"

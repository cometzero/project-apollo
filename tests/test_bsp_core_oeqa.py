from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
for module_path in (
    ROOT / "hsoc-stack/yocto/meta-hsoc-bsp/lib",
    ROOT / "layers/poky/meta/lib",
):
    sys.path.insert(0, str(module_path))

from oeqa.runtime.cases.test_10_bsp_core import BSPCoreTest  # noqa: E402

setattr(BSPCoreTest, "__test__", False)


class FakeTarget:
    DEFAULT_CONSOLE: str = "default"

    def __init__(
        self,
        responses: dict[str, tuple[int, str]],
        expect_status: int = 0,
    ) -> None:
        self.responses = responses
        self.expect_status = expect_status
        self.commands: list[str] = []
        self.expected: list[tuple[str, str]] = []

    def run(self, command: str, timeout: int | None = None) -> tuple[int, str]:
        del timeout
        self.commands.append(command)
        for marker, response in sorted(
            self.responses.items(), key=lambda item: len(item[0]), reverse=True
        ):
            if marker in command:
                return response
        return 1, "unexpected command"

    def expect(self, terminal: str, pattern: str, timeout: int) -> int:
        del timeout
        self.expected.append((terminal, pattern))
        return self.expect_status


def _case(target: FakeTarget, method: str = "test_linux_topology_and_devices") -> BSPCoreTest:
    case = BSPCoreTest(method)
    case.target = target
    case.td = {"PC_CPUS_COUNT": "4"}
    return case


def test_bsp_core_rejects_non_numeric_dsu_counter() -> None:
    # Given: a BSP target whose DSU PMU command emits an unusable counter.
    target = FakeTarget({"perf stat": (0, "not-a-number arm_dsu_0/event=0x002A/")})

    # When/Then: the BSP core assertion refuses to normalize invalid PMU output.
    with pytest.raises(AssertionError):
        _case(target).test_linux_topology_and_devices()


def test_bsp_core_accepts_numeric_zero_from_deterministic_dsu_workload() -> None:
    # Given: both DSU events return the plan-approved numeric zero value.
    target = FakeTarget(
        {
            "nproc --all": (0, "1"),
            "find /sys/firmware/devicetree/base/cpus": (0, "1"),
            "index3/size": (0, "4096K"),
            "index3/shared_cpu_list": (0, "0-0"),
            "event=0x002A": (0, "0 arm_dsu_0/event=0x002A/"),
            "event=0x002B": (0, "0 arm_dsu_0/event=0x002B/"),
            "test -e /dev/rtc0": (0, ""),
            "test -e /dev/watchdog0": (0, ""),
            "rng_available": (0, "virtio_rng.0"),
            "rng_current": (0, "virtio_rng.0"),
            "hexdump -n 32 /dev/hwrng": (0, "00112233"),
            "sh -c 'cpus": (0, ""),
            "cat /sys/devices/system/cpu/online": (0, "0-0"),
        }
    )

    # When: BSP topology qualification drives the PMU.
    case = _case(target)
    case.td = {"PC_CPUS_COUNT": "1"}
    case.test_linux_topology_and_devices()

    # Then: perf used a real bounded memory workload rather than `true`.
    perf_commands = [command for command in target.commands if "perf stat" in command]
    assert len(perf_commands) == 2
    assert all("dd if=/dev/zero of=/dev/null" in command for command in perf_commands)
    assert all("-- true" not in command for command in perf_commands)


def test_firmware_handoff_uses_runtime_efi_and_systemd_evidence() -> None:
    # Given: firmware consoles match and the running BSP reports its handoff state.
    target = FakeTarget(
        {
            "dmesg": (
                0,
                "efi: EFI v2.11 by Das U-Boot",
            )
        }
    )

    # When: the firmware assertion runs after BSP boot consumed console output.
    _case(target, "test_firmware_boot_chain").test_firmware_boot_chain()

    # Then: the default console is not consumed again and runtime evidence is used.
    assert all(terminal != target.DEFAULT_CONSOLE for terminal, _ in target.expected)
    assert any("dmesg" in command for command in target.commands)


def test_bsp_core_rejects_a_missing_firmware_marker() -> None:
    # Given: the RSE console cannot match a required handoff marker.
    target = FakeTarget({}, expect_status=1)

    # When/Then: firmware validation cannot pass from a later boot marker.
    with pytest.raises(AssertionError):
        _case(target, "test_firmware_boot_chain").test_firmware_boot_chain()


def test_bsp_core_rejects_a_missing_required_device() -> None:
    # Given: the BSP command boundary reports an absent RTC device.
    target = FakeTarget({"test -e /dev/rtc0": (1, "not found")})

    # When/Then: the device assertion rejects the non-zero guest status.
    with pytest.raises(AssertionError):
        _case(target)._run("test -e /dev/rtc0 && hwclock")


def test_bsp_core_restores_all_configured_cpus_after_hotplug_failure() -> None:
    # Given: CPU 2 fails to go offline after CPU 1 was already changed.
    target = FakeTarget(
        {
            "nproc --all": (0, "4"),
            "find /sys/firmware/devicetree/base/cpus": (0, "4"),
            "index3/size": (0, "4096K"),
            "index3/shared_cpu_list": (0, "0-3"),
            "perf stat -e arm_dsu_0/event=0x002A": (0, "12 arm_dsu_0/event=0x002A/"),
            "perf stat -e arm_dsu_0/event=0x002B": (0, "12 arm_dsu_0/event=0x002B/"),
            "test -e /dev/rtc0": (0, ""),
            "test -e /dev/watchdog0": (0, ""),
            "rng_available": (0, "virtio_rng.0"),
            "rng_current": (0, "virtio_rng.0"),
            "hexdump -n 32 /dev/hwrng": (0, "00112233"),
            "sh -c 'cpus": (1, "cpu2 write failed"),
        }
    )

    # When/Then: the hotplug failure is raised and final restoration is attempted.
    with pytest.raises(AssertionError):
        _case(target).test_linux_topology_and_devices()
    hotplug = next(command for command in target.commands if "sh -c 'cpus" in command)
    assert 'cpus="1 2 3"' in hotplug
    assert "for cpu in $cpus; do echo 1 >" in hotplug
    assert "trap \"restore || rc=1" in hotplug
    subprocess.run(["sh", "-n", "-c", hotplug], check=True)


def test_safety_island_cl1_requires_zephyr_boot_and_secondary_cores() -> None:
    # Given: the dedicated Safety Island target console.
    target = FakeTarget({})

    # When: the SI CL1 profile method runs.
    _case(target, "test_safety_island_cl1").test_safety_island_cl1()

    # Then: Zephyr boot and every non-boot secondary core are required once.
    assert target.expected == [
        ("safety_island_c1", r"Booting Zephyr OS build"),
        ("safety_island_c1", r"Secondary CPU core 1 \(MPID:0x10100\) is up"),
        ("safety_island_c1", r"Secondary CPU core 2 \(MPID:0x10200\) is up"),
        ("safety_island_c1", r"Secondary CPU core 3 \(MPID:0x10300\) is up"),
    ]

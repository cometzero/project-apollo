from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .reuse_common import NoopCleanup, PRIMARY_PROMPT, SI1_PROMPT, contains_all, status
from .types import (
    AssertionObservation,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
)


BSP_CORE_PROBE: Final = (
    "set -eu; count=4; "
    "test \"$(nproc --all)\" -eq $count; "
    "test \"$(find /sys/firmware/devicetree/base/cpus -maxdepth 1 "
    "-name 'cpu@*' | wc -l)\" -eq $count; "
    "for cpu in 0 1 2 3; do "
    "test \"$(cat /sys/devices/system/cpu/cpu$cpu/cache/index3/size)\" = 4096K; "
    "test \"$(cat /sys/devices/system/cpu/cpu$cpu/cache/index3/shared_cpu_list)\" "
    "= 0-3; done; echo __QBOX_BSP_CORE_TOPOLOGY_OK__; "
    "for event in 0x002A 0x002B; do "
    "out=$(perf stat -e arm_dsu_0/event=$event/ -- dd if=/dev/zero "
    "of=/dev/null bs=1M count=64 2>&1); printf '%s\\n' \"$out\"; "
    "printf '%s\\n' \"$out\" | grep -Eq '[0-9]+[[:space:]]+arm_dsu_0/'; done; "
    "echo __QBOX_BSP_CORE_DSU_OK__; "
    "test -e /dev/rtc0; hwclock >/dev/null; test -e /dev/watchdog0; "
    "grep -qw virtio_rng.0 /sys/devices/virtual/misc/hw_random/rng_available; "
    "grep -qw virtio_rng.0 /sys/devices/virtual/misc/hw_random/rng_current; "
    "hexdump -n 32 /dev/hwrng | grep -q '[0-9a-f]'; "
    "echo __QBOX_BSP_CORE_DEVICES_OK__"
)
BSP_HOTPLUG_PROBE: Final = (
    "rc=0; cpus='1 2 3'; restore() { restore_rc=0; for cpu in $cpus; do "
    "echo 1 > /sys/devices/system/cpu/cpu$cpu/online || restore_rc=1; done; "
    "return $restore_rc; }; trap 'restore || rc=1' EXIT; "
    "for cpu in $cpus; do echo 0 > /sys/devices/system/cpu/cpu$cpu/online || "
    "{ rc=1; break; }; test \"$(cat /sys/devices/system/cpu/cpu$cpu/online)\" = 0 "
    "|| { rc=1; break; }; done; restore || rc=1; trap - EXIT; "
    "test \"$(cat /sys/devices/system/cpu/online)\" = 0-3 || rc=1; "
    "test $rc -eq 0; echo __QBOX_BSP_CORE_HOTPLUG_RESTORED__"
)


def si1_boot_complete(text: str) -> bool:
    return contains_all(
        text,
        (
            "Booting Zephyr OS build",
            "Secondary CPU core 1 (MPID:0x10100) is up",
            "Secondary CPU core 2 (MPID:0x10200) is up",
            "Secondary CPU core 3 (MPID:0x10300) is up",
        ),
    )


@dataclass(frozen=True, slots=True)
class BspCoreEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        output = "\n".join(outputs)
        checks = (
            contains_all(
                snapshot.si0,
                (
                    "[SI0_PLATFORM] SCP started",
                    "[FWK] Module initialization complete!",
                    "CMN Discovery complete",
                ),
            ),
            contains_all(
                snapshot.primary,
                ("U-Boot ", "efi: EFI v2.11 by Das U-Boot"),
            )
            and "__QBOX_BSP_CORE_DEVICES_OK__" in output,
            si1_boot_complete(snapshot.si1),
            contains_all(
                snapshot.rse,
                (
                    "Starting TF-M BL1_1",
                    "Init SCMI comm to SCP succeeded",
                    "RSE to SCP SCMI power on AP succeeded",
                    "Jumping to the first image slot",
                ),
            ),
            contains_all(
                snapshot.rse,
                (
                    "MeasuredBoot: Extending measurement for sw_type: BL2",
                    "MeasuredBoot: Extending measurement for sw_type: BL_33",
                ),
            ),
            contains_all(
                snapshot.primary,
                ("Booting Linux on physical CPU", "nexios-bsp#"),
            )
            and "__QBOX_BSP_CORE_PROBE_START__" in output,
            "__QBOX_BSP_CORE_DSU_OK__" in output,
            contains_all(
                snapshot.secure,
                tuple(
                    f"I/TC: Secondary CPU {cpu} switching to normal world boot"
                    for cpu in range(1, 4)
                ),
            ),
            contains_all(
                output,
                (
                    "__QBOX_BSP_CORE_TOPOLOGY_OK__",
                    "__QBOX_BSP_CORE_HOTPLUG_RESTORED__",
                ),
            ),
            contains_all(
                snapshot.secure,
                (
                    "Loading SP: SE Proxy",
                    "Loading SP: SMM Gateway",
                    "OP-TEE version:",
                    "I/TC: Primary CPU switching to normal world boot",
                ),
            ),
        )
        return tuple(
            AssertionObservation(assertion_id, status(passed))
            for assertion_id, passed in zip(self.expected, checks, strict=True)
        )


@dataclass(frozen=True, slots=True)
class SiCl1Evaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        passed = (
            len(outputs) == 1
            and "Zephyr version" in outputs[0]
            and si1_boot_complete(snapshot.si1)
        )
        return (AssertionObservation(self.expected[0], status(passed)),)


def bsp_core_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.PRIMARY}),
        (
            ProbeStep(
                Console.PRIMARY,
                "echo __QBOX_BSP_CORE_PROBE_START__",
                PRIMARY_PROMPT,
                60.0,
            ),
            ProbeStep(Console.PRIMARY, BSP_CORE_PROBE, PRIMARY_PROMPT, 500.0),
            ProbeStep(
                Console.PRIMARY,
                BSP_HOTPLUG_PROBE,
                PRIMARY_PROMPT,
                500.0,
            ),
        ),
        expected,
        coverage_kind,
        BspCoreEvaluator(expected),
        NoopCleanup(),
        None,
    )


def si_cl1_spec(
    profile_id: str,
    expected: tuple[str, ...],
    coverage_kind: CoverageKind,
) -> ProfileProbeSpec:
    return ProfileProbeSpec(
        profile_id,
        frozenset({Console.SI1}),
        (ProbeStep(Console.SI1, "kernel version", SI1_PROMPT, 60.0),),
        expected,
        coverage_kind,
        SiCl1Evaluator(expected),
        NoopCleanup(),
        None,
    )

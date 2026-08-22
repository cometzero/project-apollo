from __future__ import annotations

from pathlib import Path
import re

import pytest

from scripts.run.qbox_validation.registry import resolve_profile
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"


def _statuses(profile_id: str, snapshot: ConsoleSnapshot, outputs: tuple[str, ...]):
    spec = resolve_profile(profile_id, MATRIX)
    result = evaluate_profile_result(spec, snapshot, outputs)
    return spec, result, {item["id"]: item["status"] for item in result["assertions"]}


def _si1_boot() -> str:
    return "\n".join(
        (
            "*** Booting Zephyr OS build v4.1.0 ***",
            "Secondary CPU core 1 (MPID:0x10100) is up",
            "Secondary CPU core 2 (MPID:0x10200) is up",
            "Secondary CPU core 3 (MPID:0x10300) is up",
            "uart:~$ ",
        )
    )


def _bsp_snapshot() -> ConsoleSnapshot:
    return ConsoleSnapshot(
        primary="\n".join(
            (
                "U-Boot 2025.01",
                "Booting Linux on physical CPU 0x0",
                "efi: EFI v2.11 by Das U-Boot",
                "__QBOX_BSP_CORE_LINUX_OK__",
                "__QBOX_BSP_CORE_HOTPLUG_RESTORED__",
                "nexios-bsp# ",
            )
        ),
        si0="\n".join(
            (
                "[SI0_PLATFORM] SCP started",
                "[FWK] Module initialization complete!",
                "CMN Discovery complete",
            )
        ),
        si1=_si1_boot(),
        secure="\n".join(
            (
                "Loading SP: SE Proxy",
                "Loading SP: SMM Gateway",
                "NOTICE:  BL31:",
                "I/TC: OP-TEE version: test",
                "I/TC: Primary CPU switching to normal world boot",
                "I/TC: Secondary CPU 1 switching to normal world boot",
                "I/TC: Secondary CPU 2 switching to normal world boot",
                "I/TC: Secondary CPU 3 switching to normal world boot",
            )
        ),
        rse="\n".join(
            (
                "Starting TF-M BL1_1",
                "Init SCMI comm to SCP succeeded",
                "RSE to SCP SCMI power on AP succeeded",
                "MeasuredBoot: Extending measurement for sw_type: BL2",
                "MeasuredBoot: Extending measurement for sw_type: BL_33",
                "Jumping to the first image slot",
            )
        ),
    )


def _smcf_output() -> str:
    return "\n".join(
        (
            "[INTEGRATION_TEST] Start: smcf",
            "23 Tests 0 Failures 0 Ignored",
            "OK",
            "[INTEGRATION_TEST] End: smcf",
            ">",
        )
    )


def _monitor_log() -> str:
    lines = ["stale PFDI monitor timeout", "[SI0_PLATFORM] SCP started"]
    for core in range(4):
        lines.extend(
            (
                f"[PFDI_MONITOR] Started PFDI monitoring for SI cluster 1 core {core}",
                f"[PFDI_MONITOR] SI cluster 1 core {core} has been turned on, "
                "switching on PFDI monitoring",
            )
        )
    return "\n".join(lines)


def _pfdi_outputs() -> tuple[str, ...]:
    spec = resolve_profile("pfdi-si-cl1", MATRIX)
    checks = spec.steps
    from scripts.run.qbox_si_cl1_pfdi_catalog import si_cl1_pfdi_checks

    catalog = si_cl1_pfdi_checks()
    assert len(checks) == len(catalog)
    return tuple("\n".join(item.pattern_examples) + "\nuart:~$ " for item in catalog)


@pytest.mark.parametrize(
    ("profile_id", "consoles", "steps"),
    (
        ("bsp-core", frozenset({Console.PRIMARY}), 3),
        ("si-cl1", frozenset({Console.SI1}), 1),
        ("smcf", frozenset({Console.SI0}), 4),
        ("pfdi-si-cl1", frozenset({Console.SI1}), 119),
    ),
)
def test_reuse_profile_registry_routes_existing_consoles(
    profile_id: str,
    consoles: frozenset[Console],
    steps: int,
) -> None:
    # Given: a reuse-only profile in the canonical matrix.
    # When: the production registry resolves it.
    spec = resolve_profile(profile_id, MATRIX)

    # Then: it uses the expected existing console route and ordered steps.
    assert spec.required_consoles == consoles
    assert len(spec.steps) == steps
    assert spec.legacy_flag is None or profile_id == "pfdi-si-cl1"


def test_bsp_core_requires_every_cross_domain_observable() -> None:
    # Given: complete QBox firmware, SI, secure, and Linux observations.
    snapshot = _bsp_snapshot()
    outputs = (
        "__QBOX_BSP_CORE_PROBE_START__\nnexios-bsp# ",
        "__QBOX_BSP_CORE_TOPOLOGY_OK__\n__QBOX_BSP_CORE_DSU_OK__\n"
        "__QBOX_BSP_CORE_DEVICES_OK__\nnexios-bsp# ",
        "__QBOX_BSP_CORE_HOTPLUG_RESTORED__\nnexios-bsp# ",
    )

    # When: the BSP evaluator consumes the current run.
    spec, result, statuses = _statuses("bsp-core", snapshot, outputs)

    # Then: all ten exact matrix assertions pass with no boot-only shortcut.
    assert result["verdict"] == "PASS"
    assert tuple(statuses) == spec.expected_assertion_ids
    assert set(statuses.values()) == {"PASS"}

    incomplete = ConsoleSnapshot(
        primary=snapshot.primary,
        si0=snapshot.si0,
        si1=snapshot.si1,
        secure=snapshot.secure.replace("Secondary CPU 3", "missing CPU 3"),
        rse=snapshot.rse,
    )
    _, failed, failed_statuses = _statuses("bsp-core", incomplete, outputs)
    assert failed["verdict"] == "FAIL"
    assert failed_statuses["pc-cpus-tfa"] == "FAIL"


def test_si_cl1_requires_boot_and_all_secondary_cores() -> None:
    # Given: a fresh SI1 shell response and complete boot log.
    snapshot = ConsoleSnapshot(si1=_si1_boot())

    # When/Then: complete evidence passes and one absent core fails.
    _, passed, _ = _statuses("si-cl1", snapshot, ("Zephyr version\nuart:~$ ",))
    assert passed["verdict"] == "PASS"
    missing = ConsoleSnapshot(si1=snapshot.si1.replace("Secondary CPU core 2", "missing"))
    _, failed, _ = _statuses("si-cl1", missing, ("Zephyr version\nuart:~$ ",))
    assert failed["verdict"] == "FAIL"


def test_smcf_requires_startup_four_distinct_runs_and_sensor_format() -> None:
    # Given: complete startup, four command outputs, and a sensor sample.
    snapshot = ConsoleSnapshot(
        si0="\n".join(
            (
                "[SI0_PLATFORM] SCP started",
                "[SMCF_CLIENT] start data_sampling for MGI[0]",
                "[SMCF_CLIENT] Values for MGI TEMP MLI 1 (Sensor)",
                "[SMCF_CLIENT] Value[0] data = 0x1a",
                ">",
            )
        )
    )
    outputs = (_smcf_output(),) * 4

    # When/Then: complete evidence passes; partial and duplicate runs fail.
    _, passed, _ = _statuses("smcf", snapshot, outputs)
    assert passed["verdict"] == "PASS"
    _, partial, _ = _statuses("smcf", snapshot, outputs[:3])
    assert partial["verdict"] != "PASS"
    duplicate = outputs[:-1] + (_smcf_output().replace("OK", "OK\nOK"),)
    _, repeated, _ = _statuses("smcf", snapshot, duplicate)
    assert repeated["verdict"] == "FAIL"


def test_smcf_waits_for_integration_end_not_cli_prompt() -> None:
    # Given: SMCF enters its CLI before the integration test finishes.
    spec = resolve_profile("smcf", MATRIX)
    prompt = re.compile(spec.steps[0].prompt_pattern)
    initial = "[FWK] Module initialization complete!"
    partial = initial + "\n[CLI_DEBUGGER_MODULE] Entering CLI\n>\n[INTEGRATION_TEST] Start: smcf"
    complete = partial + "\n1 Tests 0 Failures 0 Ignored\nOK\n[INTEGRATION_TEST] End: smcf"

    # When: the state machine searches for a fresh completion prompt.
    partial_matches = tuple(prompt.finditer(partial))
    complete_matches = tuple(prompt.finditer(complete))

    # Then: the transient CLI prompt cannot complete the command.
    assert partial_matches[-1].end() == len(initial)
    assert complete_matches[-1].end() == len(complete)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "timeout"])
def test_pfdi_si_cl1_requires_current_complete_monitor_matrix(mutation: str) -> None:
    # Given: all SI1 CLI outputs and a current-run four-core monitor matrix.
    monitor = _monitor_log()
    if mutation == "missing":
        monitor = monitor.replace(
            "[PFDI_MONITOR] Started PFDI monitoring for SI cluster 1 core 2",
            "missing core 2 start",
        )
    elif mutation == "duplicate":
        monitor += "\n[PFDI_MONITOR] Started PFDI monitoring for SI cluster 1 core 2"
    else:
        monitor += "\n[PFDI_MONITOR] PFDI monitor timeout"

    # When: the existing CLI evaluator is extended with SI0 monitoring.
    _, result, statuses = _statuses(
        "pfdi-si-cl1",
        ConsoleSnapshot(si0=monitor, si1="uart:~$ "),
        _pfdi_outputs(),
    )

    # Then: only a complete, duplicate-free, timeout-free matrix may pass.
    assert result["verdict"] == "FAIL"
    assert statuses["si-pfdi-monitoring"] == "FAIL"


def test_pfdi_si_cl1_accepts_stale_failure_before_current_anchor() -> None:
    # Given: a stale failure before the last current-run SCP boot anchor.
    snapshot = ConsoleSnapshot(si0=_monitor_log(), si1="uart:~$ ")

    # When/Then: current complete CLI and monitor evidence passes.
    _, result, statuses = _statuses("pfdi-si-cl1", snapshot, _pfdi_outputs())
    assert result["verdict"] == "PASS"
    assert statuses["si-pfdi-monitoring"] == "PASS"

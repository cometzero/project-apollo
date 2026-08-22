from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from scripts.run.qbox_cpufreq_commands import cpufreq_probe_commands
from scripts.run.qbox_validation.registry import resolve_profile
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
ASSERTIONS = (
    "cpufreq-policy",
    "cpufreq-default-governors",
    "cpufreq-set-governors",
    "cpufreq-scaling-driver",
    "cpufreq-current-frequency-per-governor",
    "cpufreq-affected-cpus-per-policy",
    "cpufreq-invalid-governor",
    "cpufreq-scaling-min-frequencies",
    "cpufreq-scaling-max-frequencies",
    "cpufreq-min-max-negative",
)
GOVERNORS = ("ondemand", "performance", "powersave", "schedutil")
OPPS = (1800000, 2000000, 2500000)


def _policies(cpu_count: int) -> tuple[str, ...]:
    return tuple(f"policy{cpu}" for cpu in range(0, cpu_count, 4))


def _restore(policies: tuple[str, ...]) -> str:
    return "\n".join(
        f"CPUFREQ_RESTORE policy={policy} governor=schedutil "
        "min=1800000 max=2500000 restored=1"
        for policy in policies
    )


def _passing_outputs(cpu_count: int) -> tuple[str, ...]:
    policies = _policies(cpu_count)
    policy_lines = [
        "CPUFREQ_META "
        f"cpu_count={cpu_count} guest_contract=identical "
        "performance_coupling=unsupported"
    ]
    for policy in policies:
        first = int(policy.removeprefix("policy"))
        affected = ",".join(str(cpu) for cpu in range(first, first + 4))
        policy_lines.append(
            f"CPUFREQ_POLICY policy={policy} "
            "governors=ondemand,performance,powersave,schedutil "
            "frequencies=1800000,2000000,2500000 driver=scmi "
            f"affected={affected} min=1800000 max=2500000 current=2500000"
        )
    defaults = "\n".join(
        f"CPUFREQ_DEFAULT policy={policy} governor=schedutil" for policy in policies
    )
    governors = "\n".join(
        f"CPUFREQ_GOVERNOR policy={policy} requested={governor} actual={governor}"
        for policy in policies
        for governor in GOVERNORS
    )
    drivers = "\n".join(
        f"CPUFREQ_DRIVER policy={policy} driver=scmi" for policy in policies
    )
    current = "\n".join(
        f"CPUFREQ_CURRENT policy={policy} governor={governor} frequency=2000000"
        for policy in policies
        for governor in GOVERNORS
    )
    affected = "\n".join(
        f"CPUFREQ_AFFECTED policy={policy} cpus="
        + ",".join(
            str(cpu)
            for cpu in range(
                int(policy.removeprefix("policy")),
                int(policy.removeprefix("policy")) + 4,
            )
        )
        for policy in policies
    )
    invalid = "\n".join(
        f"CPUFREQ_INVALID_GOVERNOR policy={policy} rejected=1 unchanged=1"
        for policy in policies
    )
    minimum = "\n".join(
        f"CPUFREQ_MIN policy={policy} frequency={frequency} applied=1"
        for policy in policies
        for frequency in OPPS
    )
    maximum = "\n".join(
        f"CPUFREQ_MAX policy={policy} frequency={frequency} applied=1"
        for policy in policies
        for frequency in OPPS
    )
    negative = "\n".join(
        f"CPUFREQ_NEGATIVE policy={policy} rejected_min=1 rejected_max=1 unchanged=1"
        for policy in policies
    )
    restored = _restore(policies)
    return (
        "\n".join(policy_lines),
        defaults,
        governors + "\n" + restored,
        drivers,
        current + "\n" + restored,
        affected,
        invalid + "\n" + restored,
        minimum + "\n" + restored,
        maximum + "\n" + restored,
        negative + "\n" + restored,
    )


def _statuses(outputs: tuple[str, ...]) -> dict[str, str]:
    result = evaluate_profile_result(
        resolve_profile("cpufreq", MATRIX),
        ConsoleSnapshot(primary="nexios-bsp# "),
        outputs,
    )
    return {item["id"]: item["status"] for item in result["assertions"]}


@pytest.mark.parametrize("cpu_count", (4, 16))
def test_cpufreq_evaluator_accepts_cluster_aligned_contract(cpu_count: int) -> None:
    assert set(_statuses(_passing_outputs(cpu_count)).values()) == {"PASS"}


@pytest.mark.parametrize(
    ("index", "old", "new", "assertion"),
    (
        (0, "2500000 driver", "2400000 driver", "cpufreq-policy"),
        (0, "1800000,2000000,2500000", "1800000,bad,2500000", "cpufreq-policy"),
        (0, "affected=4,5,6,7", "affected=0,1,2,3", "cpufreq-policy"),
        (
            0,
            "performance_coupling=unsupported",
            "performance_coupling=supported",
            "cpufreq-policy",
        ),
        (2, "actual=ondemand", "actual=powersave", "cpufreq-set-governors"),
        (6, "rejected=1", "rejected=0", "cpufreq-invalid-governor"),
        (9, "rejected_max=1", "rejected_max=0", "cpufreq-min-max-negative"),
        (9, "restored=1", "restored=0", "cpufreq-min-max-negative"),
    ),
)
def test_cpufreq_evaluator_rejects_adversarial_drift(
    index: int,
    old: str,
    new: str,
    assertion: str,
) -> None:
    outputs = list(_passing_outputs(16))
    assert old in outputs[index]
    outputs[index] = outputs[index].replace(old, new, 1)

    assert _statuses(tuple(outputs))[assertion] == "FAIL"


def test_cpufreq_commands_are_ten_primary_console_steps() -> None:
    spec = resolve_profile("cpufreq", MATRIX)

    assert spec.expected_assertion_ids == ASSERTIONS
    assert tuple(step.console for step in spec.steps) == (Console.PRIMARY,) * 10
    assert spec.legacy_flag is None
    for command in cpufreq_probe_commands():
        assert subprocess.run(["sh", "-n", "-c", command], check=False).returncode == 0

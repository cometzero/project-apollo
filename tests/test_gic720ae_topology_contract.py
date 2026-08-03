from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import assert_never, Literal

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/gic720ae"
HW_BLOCK = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
DEBUG_COMMON = ROOT / "scripts/run/qbox_debug_common.sh"
FUTURE_SINGLE_FLAG = "QBOX_APOLLO_FULL_SI_SINGLE_GIC"
type TopologyMode = Literal["split", "single"]


@dataclass(frozen=True, slots=True)
class Gic:
    name: str
    qemu_instance: str
    cpu_count: int


@dataclass(frozen=True, slots=True)
class Topology:
    mode: TopologyMode
    future_opt_in_flag: str
    qemu_instances: tuple[str, ...]
    gics: tuple[Gic, ...]
    cpu_count: int
    reset_targets: tuple[str, ...]
    runner_fields: tuple[tuple[str, str], ...]
    debug_endpoints: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class TopologyContractError(Exception):
    reasons: tuple[str, ...]

    def __str__(self) -> str:
        return "; ".join(self.reasons)


def load_fixture(path: Path) -> Topology:
    decoded = json.loads(path.read_text(encoding="utf-8"))
    return Topology(
        mode=decoded["mode"],
        future_opt_in_flag=decoded["future_opt_in_flag"],
        qemu_instances=tuple(decoded["qemu_instances"]),
        gics=tuple(Gic(**item) for item in decoded["gics"]),
        cpu_count=decoded["cpu_count"],
        reset_targets=tuple(decoded["reset_targets"]),
        runner_fields=tuple(sorted(decoded["runner_fields"].items())),
        debug_endpoints=tuple(sorted(decoded["debug_endpoints"].items())),
    )


def validate_topology(topology: Topology) -> None:
    reasons: list[str] = []
    if topology.future_opt_in_flag != FUTURE_SINGLE_FLAG:
        reasons.append("future opt-in flag name changed")
    if topology.cpu_count != sum(gic.cpu_count for gic in topology.gics):
        reasons.append("CPU and GIC cardinality disagree")
    if any(gic.qemu_instance not in topology.qemu_instances for gic in topology.gics):
        reasons.append("GIC references an unknown QEMU instance")
    match topology.mode:
        case "split":
            if len(topology.qemu_instances) != 2 or len(topology.gics) != 2:
                reasons.append("split mode requires two instances and two GICs")
            if len({gic.qemu_instance for gic in topology.gics}) != 2:
                reasons.append("split mode requires one instance per GIC")
        case "single":
            if len(topology.qemu_instances) != 1 or len(topology.gics) != 1:
                reasons.append("single mode requires one instance and one GIC")
        case unreachable:
            assert_never(unreachable)
    if reasons:
        raise TopologyContractError(tuple(reasons))


def source_topology() -> Topology:
    topology_lua = (HW_BLOCK / "topology.lua").read_text(encoding="utf-8")
    cl0 = (HW_BLOCK / "si_cl0.lua").read_text(encoding="utf-8")
    cl1 = (HW_BLOCK / "si_cl1.lua").read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    debug = DEBUG_COMMON.read_text(encoding="utf-8")
    instances = tuple(
        sorted(
            set(
                re.findall(
                    r"platform\.(si_cl[01]_qemu_inst)\s*=\s*\{",
                    cl0 + cl1,
                )
            )
        )
    )
    cl1_count_match = re.search(r"SI_CL1_CPU_COUNT\s*=\s*(\d+)", cl1)
    assert cl1_count_match is not None
    cl1_count = int(cl1_count_match.group(1))
    gics = (
        Gic("si_cl0_gic", "si_cl0_qemu_inst", 1),
        Gic("si_cl1_gic", "si_cl1_qemu_inst", cl1_count),
    )
    reset_targets = tuple(
        sorted(
            set(
                re.findall(
                    r'power_on_(?:load|reset)\s*=\s*\{bind\s*=\s*"&'
                    r'(si_cl[01]_[^"]+\.reset)"\}',
                    cl0 + cl1,
                )
            )
        )
    )
    runner_fields = (
        ("safety_island_topology", "full-system"),
        ("si_cl0_tcg_mode", "platform.si_cl0_qemu_inst.tcg_mode"),
        ("si_cl1_tcg_mode", "platform.si_cl1_qemu_inst.tcg_mode"),
        ("si_cl1_sync_policy", "platform.si_cl1_qemu_inst.sync_policy"),
    )
    debug_endpoints = tuple(
        (cluster, "127.0.0.1:12341")
        for cluster in ("si_cl0", "si_cl1")
        if 'DEBUG_ENDPOINT="127.0.0.1:12341"' in debug
    )
    assert '"safety_island_topology": "full-system"' in runner
    assert "si_cl0_qemu_inst" in topology_lua
    assert "si_cl1_qemu_inst" in topology_lua
    return Topology(
        mode="split",
        future_opt_in_flag=FUTURE_SINGLE_FLAG,
        qemu_instances=instances,
        gics=gics,
        cpu_count=1 + cl1_count,
        reset_targets=reset_targets,
        runner_fields=tuple(sorted(runner_fields)),
        debug_endpoints=tuple(sorted(debug_endpoints)),
    )


def test_split_si_default_matches_frozen_contract() -> None:
    # Given: the checked-in split-SI fixture and current Apollo Lua/runner sources.
    expected = load_fixture(FIXTURES / "split-si-topology.json")

    # When: the source topology is structurally characterized.
    observed = source_topology()
    validate_topology(observed)

    # Then: instance, CPU, GIC, reset, runner, and debug contracts remain exact.
    assert observed == expected


def test_same_instance_with_two_gics_is_rejected() -> None:
    # Given: a misleading single-instance fixture that still contains two GICs.
    invalid = load_fixture(FIXTURES / "same-instance-two-gics.json")

    # When: the fixture is validated as a topology contract.
    with pytest.raises(TopologyContractError) as error:
        validate_topology(invalid)

    # Then: it hard-fails instead of being accepted as future single-SI mode.
    assert "single mode requires one instance and one GIC" in str(error.value)


@pytest.mark.xfail(
    reason="Task 7 has not added the opt-in single-SI fixture or Lua flag",
    strict=True,
)
def test_future_single_si_fixture_is_explicitly_pending() -> None:
    # Given: the future fixture path and planned opt-in flag name.
    fixture = FIXTURES / "single-si-topology.json"

    # When: Task 6 asks whether the future product mode exists.
    single = load_fixture(fixture)
    validate_topology(single)

    # Then: only Task 7 may turn this XFAIL into a real passing contract.
    assert single.future_opt_in_flag == FUTURE_SINGLE_FLAG

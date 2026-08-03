from __future__ import annotations
# noqa: SIZE_OK — one focused file owns the exact dual-topology data contract.

import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import TypedDict

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"
TMUX_WRAPPER = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
SINGLE_ENV = "QBOX_APOLLO_FULL_SI_SINGLE_GIC"
ROLLBACK_COMMAND = (
    "python3 scripts/run/run_qbox_apollo_fvp_full.py --si-split-gic"
)
SPLIT_RESETS = [
    "&si_cl0_qemu_inst.reset",
    "&si_cl1_qemu_inst.reset",
]
SINGLE_RESETS = [
    "&si_cl0_cpu_0_reset.reset",
    *[f"&si_cl1_cpu_{cpu}_reset.reset" for cpu in range(4)],
]


class PeExpected(TypedDict):
    pe: int
    name: str
    cluster: str
    qemu_instance: str
    mp_affinity: int
    affinity: str
    image: str
    image_loader: str
    router: str
    reset: str


type JsonValue = (
    str
    | int
    | float
    | bool
    | None
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)


class RunnerStatus(TypedDict, total=False):
    safety_island_gic_topology: dict[str, JsonValue]
    si_gic_topology_mode: str
    si_qemu_instance_count: int
    si_pe_map: list[PeExpected]
    si_reset_fanout: list[str]
    si_trace_targets: list[dict[str, JsonValue]]
    si_rollback_command: str
    si_topology_source: str
    si_topology_source_sha256: str
    si_topology_contract_sha256: str
    runner_source_sha256: str
    dry_run: bool
    automated_contract_only: bool
    child_environment: dict[str, str]
    platform_params: list[str]
    runner_argv: list[str]
    passed: bool
    blocker: str | None


def expected_pes(single: bool) -> list[PeExpected]:
    instance = "si_qemu_inst" if single else "si_cl1_qemu_inst"
    return [
        {
            "pe": 0,
            "name": "si_cl0_cpu_0",
            "cluster": "si_cl0",
            "qemu_instance": (
                "si_qemu_inst" if single else "si_cl0_qemu_inst"
            ),
            "mp_affinity": 0,
            "affinity": "0.0.0.0",
            "image": "CL0",
            "image_loader": "si_cl0_loader",
            "router": "si_cl0_ni710ae_primary_nci.protected_target_socket",
            "reset": (
                "si_cl0_cpu_0_reset" if single else "si_cl0_qemu_inst"
            ),
        },
        *[
            {
                "pe": cpu + 1,
                "name": f"si_cl1_cpu_{cpu}",
                "cluster": "si_cl1",
                "qemu_instance": instance,
                "mp_affinity": 0x10000 + (cpu * 0x100),
                "affinity": f"0.1.{cpu}.0",
                "image": "CL1",
                "image_loader": "si_cl1_loader",
                "router": "si_cl1_router.target_socket",
                "reset": (
                    f"si_cl1_cpu_{cpu}_reset"
                    if single
                    else "si_cl1_qemu_inst"
                ),
            }
            for cpu in range(4)
        ],
    ]


def run_runner(
    tmp_path: Path,
    *args: str,
    inherited_mode: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    out_dir = tmp_path / "result"
    env = os.environ.copy()
    if inherited_mode is not None:
        env[SINGLE_ENV] = inherited_mode
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--out-dir",
            str(out_dir),
            *args,
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return result, out_dir


def assert_graph(status: RunnerStatus, *, single: bool) -> None:
    mode = "single" if single else "split"
    contract = status["safety_island_gic_topology"]
    assert contract["env_var"] == SINGLE_ENV
    assert contract["mode"] == mode
    assert contract["enabled"] is single
    assert contract["pes"] == expected_pes(single)
    instances = contract["qemu_instances"]
    assert [
        (
            item["name"],
            item["domain"],
            item["architecture"],
            item["cpu"],
            item["acceleration"],
            item["tcg_mode"],
            item["sync_policy"],
            item["ram_owner"],
            item.get("scope"),
        )
        for item in instances
    ] == (
        [("si_qemu_inst", "si", "AARCH64", "cortex-r82", "tcg", "MULTI",
          "multithread-quantum", "systemc", None)]
        if single
        else [
            ("si_cl0_qemu_inst", "si_cl0", "AARCH64", "cortex-r82", "tcg",
             "MULTI", "multithread-quantum", "systemc", None),
            ("si_cl1_qemu_inst", "si_cl1", "AARCH64", "cortex-r82", "tcg",
             "MULTI", "multithread-quantum", "systemc", "fvp_cfg2_extension"),
        ]
    )
    assert [
        (
            item["name"],
            item["qemu_instance"],
            item["redistributor_regions"],
            item["cpu_interfaces"],
            item["normal_spi_count"],
            item["state_owner"],
            item.get("canonical"),
            item.get("scope"),
        )
        for item in contract["gics"]
    ] == (
        [("si_cl0_gic", "si_qemu_inst", [1, 4], 5, 960, "qemu", True, None)]
        if single
        else [
            ("si_cl0_gic", "si_cl0_qemu_inst", [1], 1, 384, "qemu", None, None),
            ("si_cl1_gic", "si_cl1_qemu_inst", [1, 1, 1, 1], 4, 128,
             "qemu", None, "fvp_cfg2_extension"),
        ]
    )
    assert contract["reset_targets"] == (
        SINGLE_RESETS if single else SPLIT_RESETS
    )
    traces = contract["trace_targets"]
    assert [
        (item["name"], item["domain"])
        for item in traces
        if item["kind"] == "qemu_instance"
    ] == (
        [("si_qemu_inst", "si")]
        if single
        else [("si_cl0_qemu_inst", "si_cl0"), ("si_cl1_qemu_inst", "si_cl1")]
    )
    assert [
        (item["name"], item["qemu_instance"], item["pe"], item["affinity"], item["image"])
        for item in traces
        if item["kind"] == "pe"
    ] == [
        (pe["name"], pe["qemu_instance"], pe["pe"], pe["affinity"], pe["image"])
        for pe in expected_pes(single)
    ]
    assert [
        (item["name"], item["qemu_instance"], item["cpu_interfaces"])
        for item in traces
        if item["kind"] == "gic"
    ] == (
        [("si_cl0_gic", "si_qemu_inst", 5)]
        if single
        else [
            ("si_cl0_gic", "si_cl0_qemu_inst", 1),
            ("si_cl1_gic", "si_cl1_qemu_inst", 4),
        ]
    )
    assert len(traces) == (7 if single else 9)
    assert contract["rollback_command"] == ROLLBACK_COMMAND
    assert status["si_gic_topology_mode"] == mode
    assert status["si_qemu_instance_count"] == (1 if single else 2)
    assert status["si_pe_map"] == expected_pes(single)
    assert status["si_reset_fanout"] == contract["reset_targets"]
    assert status["si_trace_targets"] == contract["trace_targets"]
    assert status["si_rollback_command"] == ROLLBACK_COMMAND


@pytest.mark.parametrize(
    ("flag", "single"),
    [("--si-single-gic", True), ("--si-split-gic", False)],
)
def test_check_only_records_hashed_topology_contract(
    tmp_path: Path,
    flag: str,
    single: bool,
) -> None:
    # Given: the non-dry-run validation surface for either topology.
    # When: check-only validates inputs without starting the runtime child.
    result, out_dir = run_runner(tmp_path, "--check-only", flag)

    # Then: it passes with the exact graph and reproducible source provenance.
    assert result.returncode == 0
    status = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
    assert status["passed"] is True
    assert status["blocker"] is None
    assert_graph(status, single=single)
    topology_source = Path(status["si_topology_source"])
    assert topology_source == (
        ROOT
        / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/topology.lua"
    )
    assert status["si_topology_source_sha256"] == hashlib.sha256(
        topology_source.read_bytes()
    ).hexdigest()
    contract_json = json.dumps(
        status["safety_island_gic_topology"],
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    assert status["si_topology_contract_sha256"] == hashlib.sha256(
        contract_json
    ).hexdigest()
    assert status["runner_source_sha256"] == hashlib.sha256(
        RUNNER.read_bytes()
    ).hexdigest()


def test_topology_options_are_mutually_exclusive() -> None:
    # Given: both topology selectors on one canonical runner invocation.
    # When: argparse resolves the contradictory selection.
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--dry-run",
            "--si-single-gic",
            "--si-split-gic",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: the CLI rejects the conflict with argparse's usage status.
    assert result.returncode == 2
    assert "not allowed with argument --si-single-gic" in result.stderr


@pytest.mark.parametrize(
    ("flag", "single"),
    [(None, False), ("--si-split-gic", False), ("--si-single-gic", True)],
)
def test_dry_run_records_exact_topology_graph(
    tmp_path: Path,
    flag: str | None,
    single: bool,
) -> None:
    # Given: default, explicit rollback, or explicit canonical topology input.
    args = ["--dry-run", *([flag] if flag is not None else [])]

    # When: the public runner serializes its automated-only dry-run result.
    result, out_dir = run_runner(tmp_path, *args)

    # Then: argv, env, platform parameters, graph, resets, and traces are exact.
    assert result.returncode == 0
    status = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
    assert_graph(status, single=single)
    assert status["dry_run"] is True
    assert status["automated_contract_only"] is True
    assert status["child_environment"][SINGLE_ENV] == (
        "true" if single else "false"
    )
    params = status["platform_params"]
    assert ("platform.si_qemu_inst.tcg_mode=MULTI" in params) is single
    assert ("platform.si_cl0_qemu_inst.tcg_mode=MULTI" in params) is not single
    if not single:
        assert "--si-single-gic" not in status["runner_argv"]


def test_malformed_inherited_mode_cannot_override_default_split(
    tmp_path: Path,
) -> None:
    # Given: malformed inherited mode input and no CLI selector.
    # When: the public runner creates the default dry-run graph.
    result, out_dir = run_runner(
        tmp_path,
        "--dry-run",
        inherited_mode="malformed",
    )

    # Then: the runner explicitly reconstructs the legacy split graph.
    assert result.returncode == 0
    status = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
    assert_graph(status, single=False)
    assert status["child_environment"][SINGLE_ENV] == "false"


def test_single_startup_failure_records_split_rollback(
    tmp_path: Path,
) -> None:
    # Given: single mode with a deliberately absent local build.
    # When: startup preflight fails before the QBox child can launch.
    result, out_dir = run_runner(
        tmp_path,
        "--check-only",
        "--si-single-gic",
        "--local-build-dir",
        str(tmp_path / "missing-build"),
    )

    # Then: failure evidence preserves the graph and explicit rollback.
    assert result.returncode != 0
    status = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
    assert status["passed"] is False
    assert status["blocker"]
    assert_graph(status, single=True)
    assert "--si-split-gic" in status["si_rollback_command"]


@pytest.mark.parametrize("flag", ["--si-single-gic", "--si-split-gic"])
def test_tmux_wrapper_forwards_topology_selection(
    tmp_path: Path,
    flag: str,
) -> None:
    # Given: a topology selection at the tmux wrapper surface.
    # When: the wrapper prints its canonical runner command.
    result = subprocess.run(
        [
            str(TMUX_WRAPPER),
            "--dry-run",
            "--no-attach",
            "--out-dir",
            str(tmp_path / flag.removeprefix("--")),
            flag,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: exactly one matching selector reaches the runner.
    assert result.returncode == 0
    command = next(
        line.removeprefix("  command: ")
        for line in result.stdout.splitlines()
        if line.startswith("  command: ")
    )
    argv = shlex.split(command)
    other = (
        "--si-split-gic" if flag == "--si-single-gic" else "--si-single-gic"
    )
    assert argv.count(flag) == 1
    assert other not in argv

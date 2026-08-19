from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from scripts.run import run_qbox_apollo_fvp_full as full_runner


ROOT = Path(__file__).resolve().parents[1]
REQUESTED_QEMU_PARAMS = (
    "platform.ap_qemu_inst.accel=tcg",
    "platform.ap_qemu_inst.tcg_mode=MULTI",
    "platform.ap_qemu_inst.sync_policy=multithread-freerunning",
    "platform.ap_qemu_inst.time_sync_strategy=quantum_keeper",
    "platform.qemu_inst.accel=tcg",
    "platform.qemu_inst.tcg_mode=SINGLE",
    "platform.qemu_inst.sync_policy=multithread-freerunning",
    "platform.qemu_inst.time_sync_strategy=quantum_keeper",
    "platform.si_cl0_qemu_inst.accel=tcg",
    "platform.si_cl0_qemu_inst.tcg_mode=SINGLE",
    "platform.si_cl0_qemu_inst.sync_policy=multithread-freerunning",
    "platform.si_cl0_qemu_inst.time_sync_strategy=quantum_keeper",
    "platform.si_cl1_qemu_inst.accel=tcg",
    "platform.si_cl1_qemu_inst.tcg_mode=MULTI",
    "platform.si_cl1_qemu_inst.sync_policy=multithread-freerunning",
    "platform.si_cl1_qemu_inst.time_sync_strategy=quantum_keeper",
)


@pytest.mark.parametrize(
    "relative_path",
    (
        "platforms/apollo/hw-block/ap_compute.lua",
        "platforms/apollo/hw-block/rse.lua",
        "platforms/apollo/hw-block/si_cl0.lua",
        "platforms/apollo/hw-block/si_cl1.lua",
    ),
)
def test_lua_qemu_defaults_use_freerunning(relative_path: str) -> None:
    path = ROOT / "hsoc-stack/tools/qbox-platform" / relative_path

    assert 'sync_policy = "multithread-freerunning";' in path.read_text(
        encoding="utf-8"
    )


def test_full_system_uses_requested_qemu_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: no environment or command-line override of the QEMU defaults.
    for _, env_name, _ in (
        *full_runner.FULL_SYSTEM_AP_QEMU_DEFAULTS,
        *full_runner.FULL_SYSTEM_RSE_QEMU_DEFAULTS,
        *full_runner.FULL_SYSTEM_SI_SPLIT_QEMU_DEFAULTS,
    ):
        monkeypatch.delenv(env_name, raising=False)
    args = argparse.Namespace(platform_param=[], build_only=False)

    # When: the canonical full-system runner assembles platform parameters.
    params = tuple(full_runner.full_system_platform_params(args))

    # Then: all four QEMU instances use the requested explicit configuration.
    assert params == REQUESTED_QEMU_PARAMS


def test_ap_quantum_override_replaces_freerunning_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the AP sync policy is overridden for a bounded comparison boot.
    override = "platform.ap_qemu_inst.sync_policy=multithread-quantum"
    monkeypatch.delenv("QBOX_APOLLO_FULL_AP_SYNC_POLICY", raising=False)
    args = argparse.Namespace(platform_param=[override], build_only=False)

    # When: the canonical full-system runner assembles platform parameters.
    params = full_runner.full_system_platform_params(args)

    # Then: only the explicit quantum policy is sent for the AP instance.
    assert params.count(override) == 1
    assert "platform.ap_qemu_inst.sync_policy=multithread-freerunning" not in params

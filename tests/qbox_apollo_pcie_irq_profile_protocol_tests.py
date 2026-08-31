"""Shared-protocol mutation outcome tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from qbox_apollo_pcie_irq_profile_support import (
    ROOT,
    load_module,
    materialize_fixture,
)

VALIDATOR_PATH = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"


@pytest.mark.parametrize(
    ("fixture", "reason"),
    [
        ("workload-failed.json", "workload_rc"),
        ("affinity-mismatch.json", "affinity_effective"),
        ("offline-stall.json", "offline_delta"),
        ("missing-cleanup.json", "cleanup_missing"),
        ("replay-failed.json", "replay_delta"),
    ],
)
def test_qbox_wrapper_fails_closed_on_shared_protocol_errors(
    tmp_path: Path, fixture: str, reason: str
) -> None:
    validator = load_module(VALIDATOR_PATH, f"qbox_negative_{fixture}")
    fixture_root = ROOT / "tests/fixtures/gic720ae/pcie-its/negative"
    log = tmp_path / "input.log"
    log.write_text(materialize_fixture(fixture_root / fixture), encoding="utf-8")
    payload = validator.run_shared(log, "msix", "b" * 64, tmp_path / "out.json")
    assert payload["status"] == "fail"
    assert payload["reason"] == reason


@pytest.mark.parametrize(
    ("fixture", "mode"), [("qbox-msix.log", "msix"), ("qbox-intx.json", "intx")]
)
def test_qbox_wrapper_accepts_complete_shared_protocol(
    tmp_path: Path, fixture: str, mode: str
) -> None:
    validator = load_module(VALIDATOR_PATH, f"qbox_happy_{mode}")
    fixture_root = ROOT / "tests/fixtures/gic720ae/pcie-its"
    log = tmp_path / f"{mode}.log"
    log.write_text(materialize_fixture(fixture_root / fixture), encoding="utf-8")
    payload = validator.run_shared(log, mode, "b" * 64, tmp_path / "out.json")
    assert payload["status"] == "pass"
    assert payload["reason"] == "ok"

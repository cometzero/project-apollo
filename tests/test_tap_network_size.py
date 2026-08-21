from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "scripts/test/run_test_conf.py",
    "scripts/test/run_test_fvp_tap_contract.py",
    "scripts/test/run_test_fvp_tap_attestation.py",
    "scripts/test/run_test_fvp_tap_state.py",
    "scripts/test/run_test_fvp_tap_network.py",
    "scripts/setup/fvp_tap_network.sh",
    "scripts/setup/fvp_tap_admin.py",
    "scripts/setup/fvp_tap_lifecycle.py",
)


def _pure_lines(path: Path) -> int:
    return sum(
        bool(line.strip()) and not line.lstrip().startswith("#")
        for line in path.read_text(encoding="utf-8").splitlines()
    )


@pytest.mark.parametrize("relative_path", MODULES)
def test_tap_network_module_stays_within_the_pure_line_budget(
    relative_path: str,
) -> None:
    # Given: each cohesive TAP contract module in the public runner path.
    path = ROOT / relative_path

    # When: comments and blank lines are excluded from its source size.
    pure_lines = _pure_lines(path)

    # Then: the bounded module remains below the programming size gate.
    assert pure_lines <= 250, f"{relative_path} has {pure_lines} pure lines"

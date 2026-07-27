from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_fvp_full_coverage.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "audit_qbox_apollo_fvp_full_coverage", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_optional_probe_gate_not_run_is_not_reported_as_pass() -> None:
    module = load_module()
    checks = module.runtime_gate_checks(
        {
            "passed": True,
            "safety_island_topology": "full-system",
            "post_login_probe": {"requested": False},
            "completion_gates": {
                "G0": "pass",
                "G1": "not_run",
                "G2": "pass",
            },
        }
    )

    by_name = {check["name"]: check for check in checks}
    assert by_name["gate:G1"]["passed"] is False
    assert by_name["gate:G1"]["gating"] is False
    assert by_name["gate:G2"]["passed"] is True
    assert by_name["gate:G2"]["gating"] is True


def test_full_system_not_run_gate_is_gating_failure() -> None:
    module = load_module()
    checks = module.runtime_gate_checks(
        {
            "passed": True,
            "safety_island_topology": "full-system",
            "post_login_probe": {"requested": True},
            "completion_gates": {
                "G0": "pass",
                "G1": "pass",
                "G2": "not_run",
            },
        }
    )

    active = next(check for check in checks if check["name"] == "gate:G2")
    assert active["passed"] is False
    assert active["gating"] is True

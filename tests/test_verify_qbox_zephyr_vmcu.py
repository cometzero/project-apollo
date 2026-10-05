"""Expected PFDI injection must not conceal unrelated full-system failures."""
import copy
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "vmcu_safety_verify", Path(__file__).resolve().parents[1] /
    "scripts/test/verify_qbox_zephyr_vmcu.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def injected_result():
    return {
        "passed": False,
        "blocker": "si_error:pfdi_monitor_timeout",
        "completion_gate_blocker": "si_error:pfdi_monitor_timeout",
        "si_error_hits": {"pfdi_monitor_timeout": True},
        "marker_groups": {"si_cl0": {"init": True}, "linux": {"shell": True}},
        "assertions": [], "first_failing_marker": None,
        "child_status": {"blocker": None, "fail_patterns": {"Kernel panic": False}},
    }


def test_explicit_injection_preserves_canonical_failed_result():
    result = injected_result()
    before = copy.deepcopy(result)
    module.validate_boot_result(result, True)
    assert result == before and result["passed"] is False
    with pytest.raises(RuntimeError):
        module.validate_boot_result(result, False)


@pytest.mark.parametrize("damage", [
    lambda r: r.update(blocker="different_failure"),
    lambda r: r["si_error_hits"].update(pfdi_agent_not_ready=True),
    lambda r: r["marker_groups"]["linux"].update(shell=False),
    lambda r: r.update(marker_groups={}),
    lambda r: r["child_status"]["fail_patterns"].update({"Kernel panic": True}),
    lambda r: r["child_status"].update(blocker="abort"),
    lambda r: r.update(assertions=["failed"]),
    lambda r: r.update(first_failing_marker="other"),
])
def test_injected_fault_never_masks_unrelated_failure(damage):
    result = injected_result()
    damage(result)
    with pytest.raises(RuntimeError):
        module.validate_boot_result(result, True)

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_qbox_apollo_fvp_full_map.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_qbox_apollo_fvp_full_map", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_check_passes_when_forbidden_timer_irq_alias_is_absent(tmp_path: Path, monkeypatch) -> None:
    # Given: an RSE timer map with only the architected IRQ assignments.
    module = load_module()
    platform = tmp_path / "platform"
    rse = platform / "platforms/apollo/hw-block/rse.lua"
    rse.parent.mkdir(parents=True)
    rse.write_text("RSE_TIMER0_IRQ = 3\n", encoding="utf-8")
    monkeypatch.setenv("QBOX_PLATFORM_DIR", str(platform))

    # When: the negative static check runs.
    result = module.run_check(
        ROOT,
        "irq",
        ("timer:no-legacy", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/rse.lua", r"NOT:RSE_TIMER0_IRQ\s*=\s*39"),
    )

    # Then: absence of the forbidden legacy alias passes.
    assert result["passed"] is True


def test_run_check_fails_when_forbidden_timer_irq_alias_is_present(tmp_path: Path, monkeypatch) -> None:
    # Given: an RSE timer map that incorrectly restores a legacy IRQ alias.
    module = load_module()
    platform = tmp_path / "platform"
    rse = platform / "platforms/apollo/hw-block/rse.lua"
    rse.parent.mkdir(parents=True)
    rse.write_text("RSE_TIMER0_IRQ = 39\n", encoding="utf-8")
    monkeypatch.setenv("QBOX_PLATFORM_DIR", str(platform))

    # When: the negative static check runs.
    result = module.run_check(
        ROOT,
        "irq",
        ("timer:no-legacy", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/rse.lua", r"NOT:RSE_TIMER0_IRQ\s*=\s*39"),
    )

    # Then: the forbidden alias is rejected.
    assert result["passed"] is False

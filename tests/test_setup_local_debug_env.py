from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/setup/setup_local_debug_env.py"


def load_debug_env_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("setup_local_debug_env", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_si_cl1_zephyr_debug_symbols_prefer_local_deploy() -> None:
    module = load_debug_env_module()

    component = next(
        item for item in module.COMPONENTS if item.name == "si-cl1-zephyr"
    )

    assert component.elf_candidates[0] == "deploy/firmware/zephyr-demos-cl1.elf"

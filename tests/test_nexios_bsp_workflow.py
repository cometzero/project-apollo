from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


TESTS_DIR = Path(__file__).parent
SUPPORT_NAME = "nexios_bsp_workflow_support"
TEST_MODULES = (
    "nexios_bsp_build_tests",
    "nexios_bsp_image_tests",
    "nexios_bsp_network_tests",
    "nexios_bsp_pfdi_tests",
)


def load_test_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, TESTS_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_test_module(SUPPORT_NAME)
for test_module in TEST_MODULES:
    for name, value in vars(load_test_module(test_module)).items():
        if name.startswith("test_"):
            globals()[name] = value

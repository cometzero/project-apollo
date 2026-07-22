from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/debug/capture_fvp_timer_snapshot.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("capture_fvp_timer_snapshot", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_view_accepts_register_and_memory_forms() -> None:
    # Given: explicit Iris register and memory view specifications.
    module = load_module()

    # When: their boundary parser is called.
    register = module.parse_view("ap_cpu0=ap-cpu0:register:CNTPCT_EL0")
    memory = module.parse_view("smd=ref-counter:memory:0x20000d0100008:8")

    # Then: stable IDs and read locations are retained without guessed values.
    assert register.view_id == "ap_cpu0"
    assert register.kind == "register"
    assert memory.address == 0x20000D0100008
    assert memory.width == 8


def test_parse_view_rejects_malformed_memory_width() -> None:
    # Given: an unsupported MMIO width.
    module = load_module()

    # When/Then: parsing rejects it before any Iris connection is attempted.
    with pytest.raises(ValueError, match="width"):
        module.parse_view("smd=ref-counter:memory:0x10:3")


def test_new_runnable_model_selects_async_iris_api() -> None:
    # Given: Iris exposes run() only on its asynchronous model wrapper.
    module = load_module()
    calls: list[dict[str, object]] = []

    class RunnableModel:
        def run(self) -> None:
            pass

    class ModelApi:
        @staticmethod
        def NewNetworkModel(host: str, port: int, **kwargs: object) -> RunnableModel:
            calls.append({"host": host, "port": port, **kwargs})
            return RunnableModel()

    # When: the capture helper opens the live model.
    model = module.new_runnable_model(ModelApi, "localhost", 7100, 5000)

    # Then: it chooses AsyncModel and verifies the required run surface.
    assert callable(model.run)
    assert calls == [
        {
            "host": "localhost",
            "port": 7100,
            "timeoutInMs": 5000,
            "synchronous": False,
        }
    ]


def test_add_program_breakpoint_uses_explicit_memory_space() -> None:
    module = load_module()
    calls: list[tuple[int, str | None]] = []

    class Target:
        def add_bpt_prog(self, address: int, memory_space: str | None = None) -> int:
            calls.append((address, memory_space))
            return 7

    breakpoint = module.add_program_breakpoint(Target(), 0xE0003084, "Hyp")

    assert breakpoint == 7
    assert calls == [(0xE0003084, "Hyp")]

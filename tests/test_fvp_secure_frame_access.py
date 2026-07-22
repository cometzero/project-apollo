from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/debug/fvp_secure_frame_access.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fvp_secure_frame_access", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Target:
    def __init__(self) -> None:
        self.value = 0
        self.writes: list[int] = []
        self.memory_write_shapes: list[tuple[int, int]] = []

    def read_register(self, _: str) -> int:
        return self.value

    def write_register(self, _: str, value: int) -> None:
        self.value = value
        self.writes.append(value)

    def read_memory(self, *_: object, **__: object) -> bytearray:
        return bytearray(self.value.to_bytes(4, "little"))

    def write_memory(self, _: int, value: bytearray, **kwargs: object) -> None:
        self.value = int.from_bytes(value, "little")
        self.memory_write_shapes.append((int(kwargs["size"]), int(kwargs["count"])))


def test_enabled_secure_frame_restores_original_control_value() -> None:
    module = load_module()
    target = Target()
    target.value = 0x12
    with module.enabled_secure_frame(target, "CNTACR1") as original:
        assert original == 0x12
        assert target.value == 0x3F
    assert target.value == 0x12
    assert target.writes == [0x3F, 0x12]


def test_enabled_secure_frame_restores_when_capture_raises() -> None:
    module = load_module()
    target = Target()
    with pytest.raises(RuntimeError, match="capture"):
        with module.enabled_secure_frame(target, "CNTACR1"):
            raise RuntimeError("capture")
    assert target.value == 0


def test_enabled_secure_frame_memory_restores_when_capture_raises() -> None:
    module = load_module()
    target = Target()
    target.value = 0x12
    with pytest.raises(RuntimeError, match="capture"):
        with module.enabled_secure_frame_memory(target, "SP", 0x1A810044):
            assert target.value == 0x3F
            raise RuntimeError("capture")
    assert target.value == 0x12
    assert target.memory_write_shapes == [(4, 1), (4, 1)]

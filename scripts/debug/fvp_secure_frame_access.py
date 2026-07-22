"""Opt-in, reversible Iris access control for the AP secure timer frame."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Protocol


class IrisRegisterTarget(Protocol):
    def read_register(self, name: str) -> int: ...

    def write_register(self, name: str, value: int) -> None: ...

    def read_memory(self, address: int, *, memory_space: str, size: int, count: int) -> bytearray: ...

    def write_memory(
        self,
        address: int,
        value: bytearray,
        *,
        memory_space: str,
        size: int,
        count: int,
    ) -> None: ...


@contextmanager
def enabled_secure_frame(target: IrisRegisterTarget, register: str) -> Iterator[int]:
    """Enable CNTACR1 for one halted capture and restore its exact original value."""
    original = target.read_register(register)
    if not isinstance(original, int):
        raise RuntimeError("CNTACR1 read did not return an integer")
    target.write_register(register, 0x3F)
    try:
        yield original
    finally:
        target.write_register(register, original)


@contextmanager
def enabled_secure_frame_memory(
    target: IrisRegisterTarget, memory_space: str, address: int
) -> Iterator[int]:
    original = int.from_bytes(
        target.read_memory(address, memory_space=memory_space, size=4, count=1), "little"
    )
    target.write_memory(
        address,
        bytearray((0x3F).to_bytes(4, "little")),
        memory_space=memory_space,
        size=4,
        count=1,
    )
    try:
        yield original
    finally:
        target.write_memory(
            address,
            bytearray(original.to_bytes(4, "little")),
            memory_space=memory_space,
            size=4,
            count=1,
        )

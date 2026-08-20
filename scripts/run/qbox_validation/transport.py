from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path
from typing import Iterator

from .types import Console, Dispatch


class WriterOwner(StrEnum):
    RUNTIME = "runtime"
    OUTER_CHILD = "outer-child"


class TransportError(Exception):
    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class ConsolePipe:
    console: Console
    path: Path
    owner: WriterOwner
    env_key: str = ""


@dataclass(frozen=True, slots=True)
class OpenWriter:
    console: Console
    fd: int


@dataclass(frozen=True, slots=True)
class ProfileWriters:
    writers: tuple[OpenWriter, ...]
    bound_consoles: frozenset[Console]

    def fd(self, console: Console) -> int | None:
        writer = next(
            (item for item in self.writers if item.console == console),
            None,
        )
        return writer.fd if writer is not None else None

    def write(self, dispatch: Dispatch) -> None:
        writer = next(
            (item for item in self.writers if item.console == dispatch.console),
            None,
        )
        if writer is None:
            raise TransportError(f"console_writer_unbound:{dispatch.console.value}")
        payload = dispatch.payload.encode("utf-8")
        if dispatch.console == Console.SI0:
            payload = b"\x05" + payload + b"\x04"
        os.write(writer.fd, payload)


@contextmanager
def managed_profile_writers(
    bindings: tuple[ConsolePipe, ...],
    active_owner: WriterOwner = WriterOwner.RUNTIME,
) -> Iterator[ProfileWriters]:
    consoles = tuple(item.console for item in bindings)
    if len(set(consoles)) != len(consoles):
        raise TransportError("duplicate_console_binding")
    for binding in bindings:
        if binding.console == Console.SI0 and binding.owner == WriterOwner.RUNTIME:
            raise TransportError("si0_writer_must_use_outer_child_transport")
    opened: list[OpenWriter] = []
    created: list[Path] = []
    try:
        for binding in bindings:
            if binding.owner != active_owner:
                continue
            if binding.path.exists():
                raise TransportError(f"fifo_path_exists:{binding.path}")
            os.mkfifo(binding.path, mode=0o600)
            created.append(binding.path)
            fd = os.open(binding.path, os.O_RDWR | os.O_NONBLOCK)
            opened.append(OpenWriter(binding.console, fd))
        yield ProfileWriters(
            tuple(opened),
            frozenset(item.console for item in opened),
        )
    finally:
        for writer in opened:
            os.close(writer.fd)
        for path in created:
            path.unlink(missing_ok=True)


def outer_si0_commands(dispatches: tuple[Dispatch, ...]) -> tuple[str, ...]:
    commands: list[str] = []
    for dispatch in dispatches:
        if dispatch.console != Console.SI0:
            raise TransportError(
                f"outer_child_console_unsupported:{dispatch.console.value}"
            )
        commands.append(dispatch.payload.removesuffix("\n"))
    return tuple(commands)

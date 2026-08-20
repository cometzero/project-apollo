from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.run.qbox_validation.transport import (
    ConsolePipe,
    TransportError,
    WriterOwner,
    managed_profile_writers,
    outer_si0_commands,
)
from scripts.run.qbox_validation.types import Console, Dispatch


def read_fifo(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        return os.read(fd, 4096)
    finally:
        os.close(fd)


def test_primary_and_si1_dual_console_use_distinct_fifo_writers(
    tmp_path: Path,
) -> None:
    # Given: two runtime-owned FIFO bindings.
    primary = tmp_path / "primary.fifo"
    si1 = tmp_path / "si1.fifo"
    bindings = (
        ConsolePipe(Console.PRIMARY, primary, WriterOwner.RUNTIME),
        ConsolePipe(Console.SI1, si1, WriterOwner.RUNTIME),
    )

    # When: ordered dispatches are written through the managed transport.
    with managed_profile_writers(bindings) as writers:
        writers.write(Dispatch(Console.PRIMARY, "primary-command\n", 0))
        writers.write(Dispatch(Console.SI1, "si1-command\n", 1))
        observed = (read_fifo(primary), read_fifo(si1))

    # Then: each command reaches only its bound FIFO and cleanup removes both.
    assert observed == (b"primary-command\n", b"si1-command\n")
    assert not primary.exists()
    assert not si1.exists()


def test_si0_is_bridged_to_outer_child_without_runtime_writer(
    tmp_path: Path,
) -> None:
    # Given: an SI0 binding owned by the existing outer child transport.
    path = tmp_path / "si0.fifo"
    binding = ConsolePipe(Console.SI0, path, WriterOwner.OUTER_CHILD)

    # When: the runtime transport context is entered.
    with managed_profile_writers((binding,)) as writers:
        commands = outer_si0_commands(
            (
                Dispatch(Console.SI0, "test ssu\n", 0),
                Dispatch(Console.SI0, "test fmu\n", 1),
            )
        )

        # Then: no competing FIFO is created and ordered outer commands remain.
        assert writers.bound_consoles == frozenset()
        assert commands == ("test ssu", "test fmu")
        assert not path.exists()


def test_runtime_cannot_claim_si0_writer_ownership(tmp_path: Path) -> None:
    # Given: an unsafe SI0 runtime-writer request.
    binding = ConsolePipe(
        Console.SI0,
        tmp_path / "si0.fifo",
        WriterOwner.RUNTIME,
    )

    # When/Then: parallel SI0 writers are rejected before FIFO creation.
    with pytest.raises(
        TransportError,
        match="^si0_writer_must_use_outer_child_transport$",
    ):
        with managed_profile_writers((binding,)):
            pass


def test_fifo_eof_is_observable_on_real_pipe(tmp_path: Path) -> None:
    # Given: a FIFO whose sole writer has closed.
    path = tmp_path / "eof.fifo"
    os.mkfifo(path)
    reader = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    writer = os.open(path, os.O_WRONLY | os.O_NONBLOCK)

    # When: the writer closes and the reader consumes the empty stream.
    os.close(writer)
    observed = os.read(reader, 1)
    os.close(reader)
    path.unlink()

    # Then: the actual FIFO seam reports EOF as an empty read.
    assert observed == b""

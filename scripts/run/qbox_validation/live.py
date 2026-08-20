from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import assert_never

from .engine import ProfileState, advance_profile, block_profile, new_profile_state
from .transport import (
    ConsolePipe,
    ProfileWriters,
    TransportError,
    WriterOwner,
)
from .types import Console, ConsoleSnapshot, ProfileProbeSpec


@dataclass(frozen=True, slots=True)
class LiveProfileSession:
    spec: ProfileProbeSpec
    state: ProfileState
    writers: ProfileWriters


def console_pipe(console: Console, out_dir: Path) -> ConsolePipe:
    match console:
        case Console.PRIMARY:
            return ConsolePipe(
                console,
                out_dir / "primary-uart-input.fifo",
                WriterOwner.RUNTIME,
                "QBOX_RDASPEN_PRIMARY_UART_READ_FILE",
            )
        case Console.SI0:
            return ConsolePipe(
                console,
                out_dir / "si-cl0-uart-input.fifo",
                WriterOwner.OUTER_CHILD,
                "QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE",
            )
        case Console.SI1:
            return ConsolePipe(
                console,
                out_dir / "si-cl1-uart-input.fifo",
                WriterOwner.RUNTIME,
                "QBOX_APOLLO_FULL_SI_CL1_UART_READ_FILE",
            )
        case unexpected:
            assert_never(unexpected)


def profile_pipes(
    spec: ProfileProbeSpec,
    out_dir: Path,
) -> tuple[ConsolePipe, ...]:
    return tuple(
        console_pipe(console, out_dir)
        for console in sorted(spec.required_consoles)
    )


def start_live_profile(
    spec: ProfileProbeSpec,
    writers: ProfileWriters,
    *,
    now: float,
) -> LiveProfileSession:
    state = new_profile_state(spec, writers.bound_consoles, now=now)
    return LiveProfileSession(spec, state, writers)


def drive_live_profile(
    session: LiveProfileSession,
    snapshot: ConsoleSnapshot,
    *,
    now: float,
) -> LiveProfileSession:
    advanced = advance_profile(session.spec, session.state, snapshot, now=now)
    state = advanced.state
    if advanced.dispatch is not None:
        try:
            session.writers.write(advanced.dispatch)
        except TransportError:
            state = block_profile(
                session.spec,
                state,
                f"fifo_eof:{advanced.dispatch.console.value}",
            )
    return replace(session, state=state)


def abort_live_profile(
    session: LiveProfileSession,
    reason: str,
) -> LiveProfileSession:
    return replace(
        session,
        state=block_profile(session.spec, session.state, reason),
    )


def profile_environment(
    pipes: tuple[ConsolePipe, ...],
) -> tuple[tuple[str, str], ...]:
    return tuple((pipe.env_key, str(pipe.path)) for pipe in pipes)

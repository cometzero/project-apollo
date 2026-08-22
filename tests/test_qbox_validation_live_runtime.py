from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import pytest

from scripts.run import qbox_apollo_runtime as runtime
from scripts.run.qbox_validation.live import (
    profile_pipes,
    start_live_profile,
)
from scripts.run.qbox_validation.transport import (
    WriterOwner,
    managed_profile_writers,
)
from scripts.run.qbox_validation.types import (
    AssertionObservation,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    ProbeStep,
    ProfileProbeSpec,
)


PROMPT = r"(?m)^READY> $"


@dataclass(frozen=True, slots=True)
class LiveEvaluator:
    expected: tuple[str, ...]

    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        joined = "\n".join(outputs)
        return tuple(
            AssertionObservation(item, "PASS" if item in joined else "FAIL")
            for item in self.expected
        )


@dataclass(frozen=True, slots=True)
class ReceiptCleanup:
    path: Path

    def cleanup(self) -> CleanupReceipt:
        self.path.write_text("cleanup-called\n", encoding="utf-8")
        return CleanupReceipt(True, "cleanup-called")


def live_spec(
    tmp_path: Path,
    shape: tuple[Console, ...],
) -> ProfileProbeSpec:
    expected = tuple(f"live-{index}" for index in range(len(shape)))
    return ProfileProbeSpec(
        "live-test",
        frozenset(shape),
        tuple(
            ProbeStep(console, f"command-{index}", PROMPT, 2.0)
            for index, console in enumerate(shape)
        ),
        expected,
        "identical",
        LiveEvaluator(expected),
        ReceiptCleanup(tmp_path / "cleanup.txt"),
        None,
    )


def test_production_runtime_owns_live_registry_driver() -> None:
    # Given: the private runtime module used by the canonical QBox launcher.
    # When: its production profile-driving seam is inspected.
    driver = getattr(runtime, "drive_runtime_validation_profile", None)

    # Then: the live loop, not tests alone, must own registry advancement.
    assert callable(driver)


def test_validation_profile_requires_probe_completion_before_boot_exit() -> None:
    args = runtime.argparse.Namespace(
        post_login_probe=False,
        primary_operation_manifest=None,
        validation_profile="platform-devices",
    )

    required = getattr(runtime, "probe_completion_required", None)

    assert callable(required)
    assert required(args) is True


def test_validation_profile_login_driver_writes_root_to_primary_fifo(
    tmp_path: Path,
) -> None:
    args = runtime.parse_args(
        [
            "--out-dir",
            str(tmp_path),
            "--validation-profile",
            "platform-devices",
        ]
    )
    state = runtime.make_probe_state(args)
    assert state["requested"] is True
    read_fd, write_fd = os.pipe()
    os.set_blocking(read_fd, False)
    try:
        runtime.drive_post_login_probe(
            args,
            {"primary_console": f"booted\n{args.primary_login_prompt}\n"},
            state,
            write_fd,
        )
        try:
            written = os.read(read_fd, 64)
        except BlockingIOError:
            written = b""
    finally:
        os.close(read_fd)
        os.close(write_fd)

    assert written == b"root\n"
    assert state["login_attempts"] == 1


@pytest.mark.parametrize(
    ("shape", "owner"),
    (
        ((Console.PRIMARY,), WriterOwner.RUNTIME),
        ((Console.SI0,), WriterOwner.OUTER_CHILD),
        ((Console.SI1,), WriterOwner.RUNTIME),
        ((Console.PRIMARY, Console.SI1), WriterOwner.RUNTIME),
    ),
)
def test_live_runtime_drives_each_console_shape_through_real_fifos(
    tmp_path: Path,
    shape: tuple[Console, ...],
    owner: WriterOwner,
) -> None:
    # Given: a repository spec bound to production FIFO ownership.
    spec = live_spec(tmp_path, shape)
    pipes = profile_pipes(spec, tmp_path)
    observed: list[bytes] = []

    # When: the production driver advances every command from live prompts.
    with managed_profile_writers(pipes, owner) as writers:
        session = start_live_profile(spec, writers, now=0.0)
        logs = {console: "READY> " for console in shape}
        now = 0.0
        while session.state.phase == "running":
            previous = session.state.next_step
            session = runtime.drive_runtime_validation_profile(
                session,
                ConsoleSnapshot.from_pairs(tuple(logs.items())),
                now,
            )
            if session.state.command_sent and session.state.next_step == previous:
                console = spec.steps[previous].console
                pipe = next(item for item in pipes if item.console == console)
                reader = os.open(pipe.path, os.O_RDONLY | os.O_NONBLOCK)
                try:
                    observed.append(os.read(reader, 1024))
                finally:
                    os.close(reader)
                logs[console] += (
                    f"command-{previous}\nlive-{previous}\nREADY> "
                )
            now += 0.5

    # Then: routing, evaluation, spec cleanup, and FIFO cleanup all complete.
    assert session.state.phase == "passed"
    assert session.state.result is not None
    assert session.state.result["verdict"] == "PASS"
    assert (tmp_path / "cleanup.txt").read_text() == "cleanup-called\n"
    assert all(not item.path.exists() for item in pipes)
    assert len(observed) == len(shape)
    if shape == (Console.SI0,):
        assert observed == [b"\x05command-0\n\x04"]


def test_live_runtime_rejects_unbound_owner_before_process() -> None:
    # Given: an SI0 profile incorrectly offered to the inner runtime owner.
    spec = live_spec(Path("/tmp"), (Console.SI0,))
    pipes = profile_pipes(spec, Path("/tmp/live-unbound-owner"))

    # When: only runtime-owned writers are opened.
    with managed_profile_writers(pipes, WriterOwner.RUNTIME) as writers:
        session = start_live_profile(spec, writers, now=0.0)

    # Then: preflight blocks before a platform process can be launched.
    assert session.state.phase == "blocked"
    assert session.state.blocker == "unbound_console:si0"


@pytest.mark.parametrize(
    ("snapshot", "now", "blocker"),
    (
        (ConsoleSnapshot(primary="READY> partial"), 3.0, "command_timeout:0:primary"),
        (
            ConsoleSnapshot(
                primary="READY> ",
                eof=frozenset({Console.PRIMARY}),
            ),
            0.5,
            "fifo_eof:primary",
        ),
    ),
)
def test_live_runtime_failure_cleans_profile_and_fifo(
    tmp_path: Path,
    snapshot: ConsoleSnapshot,
    now: float,
    blocker: str,
) -> None:
    # Given: a live primary command with bounded transport ownership.
    spec = live_spec(tmp_path, (Console.PRIMARY,))
    pipes = profile_pipes(spec, tmp_path)

    # When: timeout or EOF interrupts the production driver.
    with managed_profile_writers(pipes) as writers:
        session = start_live_profile(spec, writers, now=0.0)
        session = runtime.drive_runtime_validation_profile(
            session,
            ConsoleSnapshot(primary="READY> "),
            0.0,
        )
        session = runtime.drive_runtime_validation_profile(session, snapshot, now)

    # Then: failure is normalized and both cleanup layers run.
    assert session.state.phase == "blocked"
    assert session.state.blocker == blocker
    assert session.state.cleanup == CleanupReceipt(True, "cleanup-called")
    assert session.state.result is not None
    assert session.state.result["verdict"] == "BLOCKED"
    assert all(not item.path.exists() for item in pipes)

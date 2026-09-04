from __future__ import annotations

import base64
import gzip
import hashlib
import os
import shlex
import signal
import stat
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import FrameType
from typing import Final

try:
    import qbox_apollo_pcie_irq_task9_validate as mode_validator
    from validate_qbox_apollo_pcie_irq_runtime import validate_profile
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_task9_validate as mode_validator
    from scripts.test.validate_qbox_apollo_pcie_irq_runtime import validate_profile


ROOT: Final = Path(__file__).resolve().parents[2]
CANONICAL_GATE: Final = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
CANONICAL_GATE_SHA256: Final = (
    "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
)
SOURCE_PROFILE: Final = (
    ROOT / ".omo/evidence/apollo-gic-its/task-8/remediation-3/profile/manifest.json"
)
SOURCE_PROFILE_SHA256: Final = (
    "50a0b28f0e9879e04ccb7ace444f8ab99eff0470f7f341f1b138aa152e788cb8"
)
CANONICAL_PROFILE: Final = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "canonical-profile-v4/manifest.json"
)
CANONICAL_PROFILE_SHA256: Final = (
    "d0fd532fc4e07edbe02d62ae06cb6afb84663b69cdf0f139729bc3a3f65cf03b"
)
GUEST_STAGING_PATH: Final = "/tmp/apollo-qbox-pcie-irq-task9.sh"
GUEST_BASE64_PATH: Final = "/tmp/apollo-qbox-pcie-irq-task9.b64"
RUNNER: Final = "./run_qbox_yocto.sh"


@dataclass(frozen=True, slots=True)
class Task9Error(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class Task9Signal(Exception):
    signum: int


def signal_handler(signum: int, _frame: FrameType | None) -> None:
    raise Task9Signal(signum)


@dataclass(frozen=True, slots=True)
class ModeInput:
    disk: Path
    disk_sha256: str
    input_sha256: str


@dataclass(frozen=True, slots=True)
class PinClosure:
    gate_sha256: str
    source_profile_sha256: str
    profile_sha256: str
    msix: ModeInput
    intx: ModeInput
    guest_probe_sha256: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def injection_command(guest: bytes, arguments: Sequence[str]) -> bytes:
    compressed = gzip.compress(guest, compresslevel=9, mtime=0)
    encoded = base64.b64encode(compressed).decode("ascii")
    argv = " ".join(shlex.quote(argument) for argument in arguments)
    command = (
        f"printf %s '{encoded}'|base64 -d|gzip -d >{GUEST_STAGING_PATH};"
        f"sh {GUEST_STAGING_PATH} {argv};rc=$?;"
        f"rm -f {GUEST_STAGING_PATH};echo __APOLLO_TASK9_RC__$rc\n"
    ).encode()
    return command


def injection_commands(guest: bytes, arguments: Sequence[str]) -> list[bytes]:
    compressed = gzip.compress(guest, compresslevel=9, mtime=0)
    encoded = base64.b64encode(compressed).decode("ascii")
    commands = [f": >{GUEST_BASE64_PATH}\n".encode()]
    commands.extend(
        f"printf %s '{encoded[offset : offset + 512]}' >>{GUEST_BASE64_PATH}\n".encode()
        for offset in range(0, len(encoded), 512)
    )
    argv = " ".join(shlex.quote(argument) for argument in arguments)
    commands.append(
        (
            f"base64 -d <{GUEST_BASE64_PATH}|gzip -d >{GUEST_STAGING_PATH};"
            f"sh {GUEST_STAGING_PATH} {argv};rc=$?;"
            f"rm -f {GUEST_BASE64_PATH} {GUEST_STAGING_PATH};"
            f"echo __APOLLO_TASK9_RC__$rc\n"
        ).encode()
    )
    return commands


def inject_fifo(fifo: Path, guest: bytes, arguments: Sequence[str]) -> int:
    command = injection_command(guest, arguments)
    pipe_buffer = os.pathconf(fifo, "PC_PIPE_BUF")
    if len(command) > pipe_buffer:
        raise Task9Error("guest_injection_exceeds_pipe_buf")
    descriptor = os.open(fifo, os.O_WRONLY)
    try:
        written = os.write(descriptor, command)
    finally:
        os.close(descriptor)
    if written != len(command):
        raise Task9Error("guest_injection_short_write")
    return written


def inject_fifo_stream(fifo: Path, guest: bytes, arguments: Sequence[str]) -> int:
    commands = injection_commands(guest, arguments)
    pipe_buffer = os.pathconf(fifo, "PC_PIPE_BUF")
    if any(len(command) > pipe_buffer for command in commands):
        raise Task9Error("guest_injection_exceeds_pipe_buf")
    descriptor = os.open(fifo, os.O_WRONLY)
    total = 0
    try:
        for command in commands:
            written = os.write(descriptor, command)
            if written != len(command):
                raise Task9Error("guest_injection_short_write")
            total += written
    finally:
        os.close(descriptor)
    return total


def inject_fifo_paused(
    pgid: int, fifo: Path, guest: bytes, arguments: Sequence[str]
) -> int:
    os.killpg(pgid, signal.SIGSTOP)
    try:
        return inject_fifo_stream(fifo, guest, arguments)
    finally:
        os.killpg(pgid, signal.SIGCONT)


def cleanup_uart_fifo(out_dir: Path) -> None:
    fifo = out_dir / "primary-uart-input.fifo"
    try:
        mode = fifo.stat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISFIFO(mode):
        raise Task9Error("uart_input_not_fifo")
    fifo.unlink()


def canonical_command(mode: str, rootfs: Path, out_dir: Path) -> list[str]:
    if mode not in ("msix", "intx"):
        raise Task9Error("mode")
    return [
        RUNNER,
        "--headless",
        "--keep-running-after-pass",
        "--timeout",
        "900",
        "--rootfs",
        str(rootfs),
        "--rootfs-bootargs-profile",
        "none",
        "--out-dir",
        str(out_dir),
    ]


def validate_mode_extras(log: Path, mode: str, probe_sha256: str) -> None:
    try:
        mode_validator.validate(log, mode, probe_sha256)
    except mode_validator.ModeValidationError as error:
        raise Task9Error(str(error)) from error


def pin_closure(gate: Path, profile: Path) -> PinClosure:
    if gate.resolve() != CANONICAL_GATE:
        raise Task9Error("fvp_reference_gate_path")
    if profile.resolve() != CANONICAL_PROFILE:
        raise Task9Error("profile_manifest_path")
    gate_digest = sha256(gate)
    profile_digest = sha256(profile)
    source_profile_digest = sha256(SOURCE_PROFILE)
    if gate_digest != CANONICAL_GATE_SHA256:
        raise Task9Error("fvp_reference_gate_sha256")
    if profile_digest != CANONICAL_PROFILE_SHA256:
        raise Task9Error("profile_manifest_sha256")
    if source_profile_digest != SOURCE_PROFILE_SHA256:
        raise Task9Error("source_profile_manifest_sha256")
    payload, input_hashes = validate_profile(profile)
    artifacts = payload["artifacts"]
    inputs = payload["inputs"]
    if not isinstance(artifacts, dict) or not isinstance(inputs, dict):
        raise Task9Error("profile_shape")

    def mode_input(mode: str) -> ModeInput:
        disk = artifacts.get(f"{mode}_disk")
        if not isinstance(disk, dict):
            raise Task9Error(f"profile_disk:{mode}")
        path = disk.get("path")
        digest = disk.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise Task9Error(f"profile_disk:{mode}")
        disk_path = Path(path)
        if sha256(disk_path) != digest:
            raise Task9Error(f"profile_disk_sha256:{mode}")
        return ModeInput(disk_path, digest, input_hashes[mode])

    guest_probe = inputs.get("guest_probe")
    if not isinstance(guest_probe, dict):
        raise Task9Error("guest_probe_identity")
    probe_digest = guest_probe.get("sha256")
    if not isinstance(probe_digest, str):
        raise Task9Error("guest_probe_identity")
    return PinClosure(
        gate_digest,
        source_profile_digest,
        profile_digest,
        mode_input("msix"),
        mode_input("intx"),
        probe_digest,
    )

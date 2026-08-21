from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import subprocess


@dataclass(frozen=True, slots=True)
class ChildIdentity:
    pid: int
    start_time: str
    executable: Path
    argv: tuple[str, ...]
    argv_sha256: str


StateFactory = Callable[[ChildIdentity], str]
FailureHook = Callable[[str], None]


class ManagedChild:
    def __init__(
        self,
        argv: list[str],
        pid_path: Path,
        lease_path: Path,
        state_path: Path,
    ) -> None:
        self.argv = argv
        self.pid_path = pid_path
        self.lease_path = lease_path
        self.state_path = state_path
        self.process: subprocess.Popen[str] | None = None

    def run(self, state_factory: StateFactory, failure_hook: FailureHook) -> ChildIdentity:
        self.process = subprocess.Popen(self.argv, text=True, start_new_session=True)
        try:
            self.pid_path.write_text(f"{self.process.pid}\n", encoding="utf-8")
            self.lease_path.touch()
            failure_hook("spawn")
            identity = self._identity()
            self._write_state(state_factory(identity))
            failure_hook("provisional")
            return identity
        except (OSError, RuntimeError, UnicodeDecodeError):
            self.cleanup()
            raise

    def cleanup(self) -> None:
        process = self.process
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for path in (self.pid_path, self.lease_path, self.state_path):
            try:
                path.unlink()
            except FileNotFoundError:
                continue

    def _identity(self) -> ChildIdentity:
        process = self.process
        if process is None:
            raise RuntimeError("child was not started")
        pid = process.pid
        start_time = self._start_time(pid)
        executable = Path(f"/proc/{pid}/exe").resolve(strict=True)
        argv = self._argv(pid)
        digest = hashlib.sha256(b"\0".join(item.encode("utf-8") for item in argv)).hexdigest()
        return ChildIdentity(pid, start_time, executable, argv, digest)

    @staticmethod
    def _start_time(pid: int) -> str:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        marker = raw.rfind(")")
        fields = raw[marker + 2 :].split() if marker >= 0 else []
        if len(fields) <= 19 or not fields[19].isdigit():
            raise RuntimeError("child start time is unavailable")
        return fields[19]

    @staticmethod
    def _argv(pid: int) -> tuple[str, ...]:
        entries = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        if not entries or entries[-1] != b"":
            raise RuntimeError("child argv is unavailable")
        return tuple(entry.decode("utf-8") for entry in entries[:-1])

    def _write_state(self, content: str) -> None:
        temporary = self.state_path.with_name(f"{self.state_path.name}.{os.getpid()}.tmp")
        temporary.write_text(content, encoding="utf-8")
        os.chmod(temporary, 0o644)
        os.replace(temporary, self.state_path)

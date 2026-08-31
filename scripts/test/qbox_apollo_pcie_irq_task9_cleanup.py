from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import time

QBOX_PROCESS_MARKERS = (
    "scripts/run/run_qbox_apollo_fvp_full.py",
    "run_qbox_apollo_fvp_full.py",
    "--runtime-child",
    "platforms-vp",
)
RUN_ARTIFACT_NAMES = (
    "primary-uart-input.fifo",
    "si-cl0-uart-input.fifo",
    "si-cl1-uart-input.fifo",
    "qbox-platform.log",
    "qbox-primary-console.log",
    "qbox-rse.log",
    "qbox-safety-island-cl0.log",
    "qbox-safety-island-cl1.log",
    "qbox-secure-console.log",
    "qbox-scp.log",
    "rse-flash-state.json",
)


@dataclass(frozen=True, slots=True)
class CleanupError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def group_members(pgid: int) -> list[int]:
    current_uid = os.getuid()
    members: list[int] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if (
                entry.stat().st_uid == current_uid
                and os.getpgid(int(entry.name)) == pgid
            ):
                members.append(int(entry.name))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return members


def qbox_process_identity(cmdline: str, exe: str) -> bool:
    exe_name = Path(exe).name if exe else ""
    return exe_name == "platforms-vp" or any(
        marker in cmdline for marker in QBOX_PROCESS_MARKERS
    )


def run_artifact_fd(path: str, out_dir: Path) -> bool:
    prefix = str(out_dir.resolve())
    if not path.startswith(prefix):
        return False
    clean_path = path.removesuffix(" (deleted)")
    relative = clean_path[len(prefix) :].lstrip("/")
    name = Path(relative).name
    return (
        name in RUN_ARTIFACT_NAMES
        or name.startswith("extra-blk")
        or relative.startswith("writable-images/")
    )


def task_owned_processes(out_dir: Path) -> list[int]:
    prefix = str(out_dir.resolve())
    current_uid = os.getuid()
    owned: list[int] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            if entry.stat().st_uid != current_uid:
                continue
            cmdline = (
                (entry / "cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode(errors="replace")
            )
            fd_paths = [str(fd.readlink()) for fd in (entry / "fd").iterdir()]
            exe = str((entry / "exe").readlink())
        except (FileNotFoundError, PermissionError, ProcessLookupError, OSError):
            continue
        run_bound = prefix in cmdline or any(
            run_artifact_fd(path, out_dir) for path in fd_paths
        )
        if run_bound and qbox_process_identity(cmdline, exe):
            owned.append(int(entry.name))
    return sorted(owned)


def terminate_task_owned(out_dir: Path) -> None:
    pids = task_owned_processes(out_dir)
    pgids = {os.getpgid(pid) for pid in pids if Path(f"/proc/{pid}").exists()}
    for pgid in pgids:
        os.killpg(pgid, signal.SIGTERM)
    deadline = time.monotonic() + 10
    while task_owned_processes(out_dir) and time.monotonic() < deadline:
        time.sleep(0.05)
    remaining = task_owned_processes(out_dir)
    for pid in remaining:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    if task_owned_processes(out_dir):
        raise CleanupError("task_owned_process_cleanup")


def write_registry(out_dir: Path, pid: int, pgid: int) -> None:
    payload = {
        "schema_version": 1,
        "uid": os.getuid(),
        "runner_pid": pid,
        "runner_pgid": pgid,
        "uart_fifo": str(out_dir / "primary-uart-input.fifo"),
        "out_dir": str(out_dir),
    }
    out_dir.joinpath("task9-process-registry.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_cleanup(out_dir: Path, pid: int, pgid: int) -> None:
    payload = {
        "schema_version": 1,
        "status": "PASS",
        "runner_pid": pid,
        "runner_pid_exists": Path(f"/proc/{pid}").exists(),
        "runner_pgid": pgid,
        "runner_pgid_members": group_members(pgid),
        "task_owned_pids": task_owned_processes(out_dir),
        "uart_fifo_exists": (out_dir / "primary-uart-input.fifo").exists(),
    }
    if (
        payload["runner_pid_exists"]
        or payload["runner_pgid_members"]
        or payload["task_owned_pids"]
        or payload["uart_fifo_exists"]
    ):
        payload["status"] = "FAIL"
    out_dir.joinpath("task9-process-cleanup.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

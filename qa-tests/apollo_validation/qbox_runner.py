from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import subprocess
from time import monotonic
from typing import assert_never

from .backend import ImageProfile
from .evidence import JsonObject, append_record, now, run_log, write_reports


@dataclass(frozen=True, slots=True)
class QBoxRunRequest:
    root: Path
    build_dir: Path
    machine: str
    image: str
    image_profile: ImageProfile
    timeout: int
    out_dir: Path
    dry_run: bool
    preflight_only: bool


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    duration_s: float


def qbox_launcher_command(
    request: QBoxRunRequest,
    *,
    dry_run: bool,
) -> list[str]:
    command = [
        str(request.root / "run_qbox_yocto.sh"),
        "--machine",
        request.machine,
        "--build-dir",
        str(request.build_dir),
        "--out-dir",
        str(request.out_dir / "qbox"),
        "--timeout",
        str(request.timeout),
        "--headless",
        "--exit-after-pass",
        "--copy-disks",
        "--no-persistent-rse-state",
    ]
    match request.image_profile:
        case "bsp":
            command.append("--bsp")
        case "product":
            command.extend(["--image-basename", request.image])
        case unexpected:
            assert_never(unexpected)
    if dry_run:
        command.append("--dry-run")
    return command


def _run_process(
    command: list[str],
    request: QBoxRunRequest,
    stdout_path: Path,
    stderr_path: Path,
) -> ProcessResult:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    started = monotonic()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w",
        encoding="utf-8",
    ) as stderr:
        process = subprocess.Popen(
            command,
            cwd=request.root,
            text=True,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            returncode = process.wait()
        except KeyboardInterrupt:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise
    return ProcessResult(returncode, round(monotonic() - started, 6))


def _read_result(path: Path) -> JsonObject:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _qbox_artifacts(request: QBoxRunRequest) -> list[JsonObject]:
    qbox_dir = request.out_dir / "qbox"
    artifacts: list[JsonObject] = [
        {"kind": "qbox_result", "path": str(qbox_dir / "result.json")},
        {"kind": "qbox_summary", "path": str(qbox_dir / "summary.txt")},
    ]
    for name in (
        "qbox-platform.log",
        "qbox-rse.log",
        "qbox-safety-island-cl0.log",
        "qbox-safety-island-cl1.log",
        "qbox-secure-console.log",
        "qbox-primary-console.log",
    ):
        artifacts.append({"kind": "qbox_console", "path": str(qbox_dir / name)})
    return artifacts


def run_qbox_category(request: QBoxRunRequest, category: str) -> int:
    request.out_dir.mkdir(parents=True, exist_ok=True)
    commands_path = request.out_dir / "commands.jsonl"
    if category != "basic":
        timestamp = now()
        append_record(
            commands_path,
            {
                "name": "qbox-category",
                "argv": ["run_test.sh", "--qbox", "--category", category],
                "required": True,
                "status": "blocked",
                "started_at": timestamp,
                "finished_at": timestamp,
                "duration_s": 0.0,
                "blockers": [
                    {"reason": "blocked_qbox_oeqa_controller_unavailable"}
                ],
            },
        )
        return write_reports(request.out_dir)[1]

    preflight_command = qbox_launcher_command(request, dry_run=True)
    preflight_stdout = request.out_dir / "logs/qbox-preflight.stdout.log"
    preflight_stderr = request.out_dir / "logs/qbox-preflight.stderr.log"
    run_log("START qbox-preflight")
    started_at = now()
    preflight = _run_process(
        preflight_command,
        request,
        preflight_stdout,
        preflight_stderr,
    )
    preflight_status = "pass" if preflight.returncode == 0 else "blocked"
    preflight_record: JsonObject = {
        "name": "qbox-preflight",
        "argv": preflight_command,
        "required": True,
        "status": preflight_status,
        "exit_code": preflight.returncode,
        "started_at": started_at,
        "finished_at": now(),
        "duration_s": preflight.duration_s,
        "stdout_log": str(preflight_stdout),
        "stderr_log": str(preflight_stderr),
    }
    if preflight.returncode != 0:
        preflight_record["blockers"] = [{"reason": "blocked_qbox_preflight"}]
    append_record(commands_path, preflight_record)
    run_log(f"DONE qbox-preflight ({preflight_status})")
    if preflight.returncode != 0 or request.preflight_only:
        return write_reports(request.out_dir)[1]

    boot_command = qbox_launcher_command(request, dry_run=False)
    if request.dry_run:
        timestamp = now()
        append_record(
            commands_path,
            {
                "name": "qbox-boot",
                "argv": boot_command,
                "required": True,
                "status": "skipped",
                "started_at": timestamp,
                "finished_at": timestamp,
                "duration_s": 0.0,
                "artifacts": _qbox_artifacts(request),
            },
        )
        return write_reports(request.out_dir)[1]

    boot_stdout = request.out_dir / "logs/qbox-boot.stdout.log"
    boot_stderr = request.out_dir / "logs/qbox-boot.stderr.log"
    run_log("START qbox-boot")
    started_at = now()
    boot = _run_process(boot_command, request, boot_stdout, boot_stderr)
    result_path = request.out_dir / "qbox/result.json"
    result = _read_result(result_path)
    blocker = result.get("blocker")
    passed = boot.returncode == 0 and result.get("passed") is True
    status = "pass" if passed else "blocked" if blocker else "fail"
    record: JsonObject = {
        "name": "qbox-boot",
        "argv": boot_command,
        "required": True,
        "status": status,
        "exit_code": boot.returncode,
        "started_at": started_at,
        "finished_at": now(),
        "duration_s": boot.duration_s,
        "stdout_log": str(boot_stdout),
        "stderr_log": str(boot_stderr),
        "artifacts": _qbox_artifacts(request),
    }
    if blocker:
        record["blockers"] = [
            blocker if isinstance(blocker, dict) else {"reason": str(blocker)}
        ]
    append_record(commands_path, record)
    run_log(f"DONE qbox-boot ({status})")
    return write_reports(request.out_dir)[1]

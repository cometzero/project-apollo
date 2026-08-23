from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic
from typing import assert_never

from .backend import ImageProfile
from .evidence import JsonObject, append_record, now, run_log, write_reports
from .qbox_artifacts import qbox_artifacts
from .qbox_network import NetworkForward, platform_network_server

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
RUN_SCRIPT_DIR = WORKSPACE_ROOT / "scripts/run"

def _profile_adapter(
    profile_id: str,
) -> tuple[str, str | None, tuple[str, ...]]:
    for import_path in (WORKSPACE_ROOT, RUN_SCRIPT_DIR):
        if str(import_path) not in sys.path:
            sys.path.insert(0, str(import_path))
    from scripts.run.qbox_validation.registry import (
        canonical_matrix_path,
        resolve_profile,
    )

    spec = resolve_profile(profile_id, canonical_matrix_path())
    return spec.profile_id, spec.legacy_flag, spec.launcher_flags


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
    test_profile: str | None


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    duration_s: float


def qbox_launcher_command(
    request: QBoxRunRequest,
    *,
    dry_run: bool,
    validation_http_port: int | None = None,
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
    if request.test_profile is not None:
        profile_id, legacy_flag, launcher_flags = _profile_adapter(
            request.test_profile
        )
        command.extend(["--validation-profile", profile_id])
        if legacy_flag is not None:
            command.append(legacy_flag)
        command.extend(launcher_flags)
    if validation_http_port is not None:
        command.extend(["--validation-http-port", str(validation_http_port)])
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


def run_qbox_category(request: QBoxRunRequest, category: str) -> int:
    request.out_dir.mkdir(parents=True, exist_ok=True)
    commands_path = request.out_dir / "commands.jsonl"
    if category != "basic" and request.test_profile is None:
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

    network_log = request.out_dir / "logs/platform-network.jsonl"
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
                "artifacts": qbox_artifacts(
                    request.out_dir,
                    request.test_profile,
                ),
            },
        )
        return write_reports(request.out_dir)[1]

    boot_stdout = request.out_dir / "logs/qbox-boot.stdout.log"
    boot_stderr = request.out_dir / "logs/qbox-boot.stderr.log"
    run_log("START qbox-boot")
    started_at = now()
    network: NetworkForward | None = None
    if request.test_profile == "platform-devices":
        with platform_network_server(network_log) as network:
            boot_command = qbox_launcher_command(
                request,
                dry_run=False,
                validation_http_port=network.host_port,
            )
            boot = _run_process(boot_command, request, boot_stdout, boot_stderr)
    else:
        boot_command = qbox_launcher_command(request, dry_run=False)
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
        "artifacts": qbox_artifacts(
            request.out_dir,
            request.test_profile,
        ),
    }
    if blocker:
        record["blockers"] = [
            blocker if isinstance(blocker, dict) else {"reason": str(blocker)}
        ]
    append_record(commands_path, record)
    run_log(f"DONE qbox-boot ({status})")
    return write_reports(request.out_dir)[1]

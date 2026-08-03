#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
from typing import Final, TypedDict

import jsonschema


ROOT: Final = Path(__file__).resolve().parents[2]
COMMANDS: Final = ("--version", "--list-instances", "--list-params")
TIMEOUT_SECONDS: Final = 30


class InputError(RuntimeError):
    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(detail)


class CommandReceipt(TypedDict):
    argv: list[str]
    exec_argv: list[str]
    cwd: str
    env: dict[str, str]
    started_at_utc: str
    ended_at_utc: str
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str
    stdout_path: str
    stderr_path: str


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provenance_digest(executable: dict[str, str], descriptor_exec_path: str, commands: list[CommandReceipt]) -> str:
    value = {"executable": executable, "descriptor_exec_path": descriptor_exec_path, "commands": commands}
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def open_executable(path: Path) -> tuple[int, os.stat_result, str, str]:
    try:
        before = path.lstat()
    except FileNotFoundError as exc:
        raise InputError("missing_executable", f"FVP executable does not exist: {path}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise InputError("invalid_executable", f"FVP executable must be a regular non-symlink file: {path}")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise InputError("invalid_executable", f"cannot no-follow open FVP executable: {path}") from exc
    descriptor = os.fstat(fd)
    if not stat.S_ISREG(descriptor.st_mode) or (descriptor.st_dev, descriptor.st_ino) != (before.st_dev, before.st_ino):
        os.close(fd)
        raise InputError("executable_drift", f"FVP executable changed during descriptor acquisition: {path}")
    executable = str(path.resolve())
    sha = digest(os.read(fd, descriptor.st_size))
    os.lseek(fd, 0, os.SEEK_SET)
    return fd, descriptor, executable, sha


def command_environment() -> dict[str, str]:
    return {"LC_ALL": "C", "LANG": "C", "PATH": os.environ.get("PATH", "")}


def run_command(fd: int, executable: str, argument: str) -> tuple[CommandReceipt, bytes, bytes]:
    env = command_environment()
    exec_path = f"/proc/self/fd/{fd}"
    started = timestamp()
    process = subprocess.Popen(
        [exec_path, argument],
        cwd=ROOT,
        env=env,
        pass_fds=(fd,),
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise InputError("command_timeout", f"FVP command timed out after {TIMEOUT_SECONDS}s: {argument}") from exc
    ended = timestamp()
    receipt: CommandReceipt = {
        "argv": [executable, argument],
        "exec_argv": [exec_path, argument],
        "cwd": str(ROOT),
        "env": env,
        "started_at_utc": started,
        "ended_at_utc": ended,
        "exit_code": process.returncode,
        "stdout_sha256": digest(stdout),
        "stderr_sha256": digest(stderr),
    }
    if process.returncode != 0:
        raise InputError("command_failed", f"FVP command failed ({argument}) with exit {process.returncode}")
    if not stdout.strip():
        raise InputError("empty_output", f"FVP command produced empty stdout: {argument}")
    return receipt, stdout, stderr


def verify_unchanged(path: Path, descriptor: os.stat_result, expected_sha: str) -> None:
    after = path.lstat()
    if stat.S_ISLNK(after.st_mode) or (after.st_dev, after.st_ino, after.st_size) != (descriptor.st_dev, descriptor.st_ino, descriptor.st_size):
        raise InputError("executable_drift", f"FVP executable path drifted during capture: {path}")
    with path.open("rb") as handle:
        actual_sha = digest(handle.read())
    if actual_sha != expected_sha:
        raise InputError("executable_drift", f"FVP executable SHA drifted during capture: {path}")


def capture(fvp: Path, output_dir: Path, schema_path: Path) -> dict[str, object]:
    if output_dir.exists() or output_dir.is_symlink():
        raise InputError("invalid_output", f"output directory must not already exist: {output_dir}")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise InputError("invalid_schema", f"invalid capture schema: {schema_path}") from exc
    fd, descriptor, executable, executable_sha = open_executable(fvp)
    try:
        records: list[CommandReceipt] = []
        output: dict[str, bytes] = {}
        errors: dict[str, bytes] = {}
        for argument in COMMANDS:
            record, stdout, stderr = run_command(fd, executable, argument)
            name = argument.removeprefix("--")
            record["stdout_path"] = f"{name}.stdout"
            record["stderr_path"] = f"{name}.stderr"
            records.append(record)
            output[argument] = stdout
            errors[argument] = stderr
        verify_unchanged(fvp, descriptor, executable_sha)
    finally:
        os.close(fd)
    combined = output["--list-instances"].rstrip(b"\n") + b"\n" + output["--list-params"]
    executable_identity = {"input_path": str(fvp), "realpath": executable, "sha256": executable_sha}
    descriptor_exec_path = records[0]["exec_argv"][0]
    receipt: dict[str, object] = {
        "format_version": 1,
        "captured_at_utc": timestamp(),
        "executable": executable_identity,
        "descriptor_exec_path": descriptor_exec_path,
        "commands": records,
        "provenance_sha256": provenance_digest(executable_identity, descriptor_exec_path, records),
        "version": output["--version"].decode("utf-8", errors="replace"),
        "introspection": {"path": "fvp-gic-introspection.txt", "sha256": digest(combined), "bytes": len(combined)},
    }
    try:
        jsonschema.validate(receipt, schema)
    except jsonschema.ValidationError as exc:
        raise InputError("receipt_schema_error", exc.message) from exc
    output_dir.mkdir(parents=True)
    (output_dir / "fvp-gic-introspection.txt").write_bytes(combined)
    for argument in COMMANDS:
        name = argument.removeprefix("--")
        (output_dir / f"{name}.stdout").write_bytes(output[argument])
        (output_dir / f"{name}.stderr").write_bytes(errors[argument])
    write_json(output_dir / "receipt.json", receipt)
    return receipt


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture fresh cfg2 FVP GIC-720AE introspection.")
    parser.add_argument("--fvp-executable", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        receipt = capture(args.fvp_executable, args.output_dir, args.schema)
    except InputError as exc:
        print(json.dumps({"reason": exc.reason, "detail": exc.detail}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps({"status": "pass", "receipt": str(args.output_dir / "receipt.json"), "sha256": receipt["introspection"]["sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

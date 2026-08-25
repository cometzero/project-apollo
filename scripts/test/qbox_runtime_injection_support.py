from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Final, TypeAlias


JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]
TERMINAL_STATES: Final = frozenset({"completed", "cancelled", "failed"})
POST_ACTION_FAILURE_PATTERNS: Final = (
    "Unhandled exception",
    "Kernel panic",
    "No error record found",
    "[ERROR]",
    "[ERR]",
)
RUNTIME_CONSOLE_LOGS: Final = (
    "qbox-platform.log",
    "qbox-rse.log",
    "qbox-safety-island-cl0.log",
    "qbox-safety-island-cl1.log",
    "qbox-secure-console.log",
    "qbox-primary-console.log",
)


@dataclass(frozen=True, slots=True)
class ScenarioError(ValueError):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class RuntimeFailure(RuntimeError):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    body: JsonObject


@dataclass(frozen=True, slots=True)
class HttpRequest:
    method: str
    path: str
    payload: JsonObject | None = None
    timeout_seconds: float = 2.0


def parse_json_object(raw: str, source: str) -> JsonObject:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ScenarioError(f"{source}: invalid JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise ScenarioError(f"{source}: expected JSON object")
    return value


def capture_log_offsets(directory: Path) -> dict[str, int]:
    return {
        name: (directory / name).stat().st_size
        if (directory / name).exists()
        else 0
        for name in RUNTIME_CONSOLE_LOGS
    }


def post_action_failures(
    directory: Path, offsets: dict[str, int]
) -> list[JsonObject]:
    failures: list[JsonObject] = []
    for name in RUNTIME_CONSOLE_LOGS:
        path = directory / name
        if not path.exists():
            continue
        with path.open("rb") as stream:
            stream.seek(offsets.get(name, 0))
            appended = stream.read().decode("utf-8", errors="replace")
        for pattern in POST_ACTION_FAILURE_PATTERNS:
            if pattern in appended:
                failures.append({"log": str(path), "pattern": pattern})
    return failures


def artifact_verdict(
    canonical_result: Path,
    actions: list[JsonObject],
    runtime_failures: list[JsonObject] | None = None,
) -> JsonObject:
    canonical = (
        parse_json_object(
            canonical_result.read_text(encoding="utf-8"),
            str(canonical_result),
        )
        if canonical_result.exists()
        else {}
    )
    states = [
        record["status"].get("state")
        for record in actions
        if isinstance(record.get("status"), dict)
    ]
    actions_passed = bool(actions) and all(
        state in {"active", "completed"} for state in states
    )
    canonical_passed = canonical.get("passed") is True
    failures = runtime_failures or []
    return {
        "passed": actions_passed and canonical_passed and not failures,
        "runtime_actions_passed": actions_passed,
        "canonical_passed": canonical_passed,
        "canonical_result": str(canonical_result),
        "canonical_blocker": canonical.get("blocker"),
        "post_action_failures": failures,
    }


@dataclass(frozen=True, slots=True)
class ApiClient:
    base_url: str

    def request(self, request: HttpRequest) -> HttpResponse:
        command = [
            "curl",
            "--silent",
            "--show-error",
            "--request",
            request.method,
            "--connect-timeout",
            "2",
            "--max-time",
            str(request.timeout_seconds),
            "--header",
            "Accept: application/json",
        ]
        if request.payload is not None:
            command.extend(
                [
                    "--header",
                    "Content-Type: application/json",
                    "--data",
                    json.dumps(request.payload, separators=(",", ":")),
                ]
            )
        command.extend(
            [
                "--write-out",
                "\n%{http_code}",
                self.base_url + request.path,
            ]
        )
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip()
            raise RuntimeFailure(
                f"{request.method} {request.path}: "
                f"curl exited {completed.returncode}: {detail}"
            )
        body, separator, status = completed.stdout.rpartition("\n")
        if not separator or not status.isdecimal():
            raise RuntimeFailure(
                f"{request.method} {request.path}: curl did not return an HTTP status"
            )
        return HttpResponse(
            int(status),
            parse_json_object(body or "{}", request.path),
        )


@dataclass(frozen=True, slots=True)
class RuntimeSession:
    process_group: int
    client: ApiClient
    timeout_seconds: float

    def live(self) -> bool:
        try:
            os.killpg(self.process_group, 0)
        except ProcessLookupError:
            return False
        return True


def terminate_owned_process_group(process: subprocess.Popen[str]) -> None:
    terminate_owned_process_groups(process, None)


def _owned_process_groups_with_token(token: str) -> set[int]:
    marker = f"QBOX_RUNTIME_INJECTION_RUN_TOKEN={token}".encode()
    groups: set[int] = set()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            environment = (entry / "environ").read_bytes().split(b"\0")
            if marker not in environment:
                continue
            groups.add(os.getpgid(int(entry.name)))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return groups


def _terminate_process_group(group: int) -> None:
    try:
        os.killpg(group, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        try:
            os.killpg(group, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    try:
        os.killpg(group, signal.SIGKILL)
    except ProcessLookupError:
        return


def terminate_owned_process_groups(
    process: subprocess.Popen[str], run_token: str | None
) -> None:
    groups = [process.pid]
    if run_token is not None:
        groups.extend(
            group
            for group in sorted(_owned_process_groups_with_token(run_token))
            if group != process.pid
        )
    for group in groups:
        _terminate_process_group(group)

#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import signal
import shlex
import subprocess
import sys
import time
from time import monotonic
from typing import Final

from run_test_conf import ConfRequest, write_conf
from run_test_oeqa_result import OeqaResultState, classify_oeqa_result_path


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
OEQA_STATUS_LABELS: Final[dict[str, str]] = {
    "PASSED": "pass",
    "PASS": "pass",
    "OK": "pass",
    "FAILED": "fail",
    "FAIL": "fail",
    "ERROR": "fail",
    "SKIPPED": "skipped",
    "SKIP": "skipped",
}
TEST_START_RE: Final = re.compile(r"^NOTE: (?P<method>test_\S+) \((?P<class>[^)]+)\)")
TEST_DONE_RE: Final = re.compile(r"^NOTE:\s+\.\.\. (?P<status>ok|FAIL|ERROR|skipped.*)\s*$")

@dataclass(frozen=True, slots=True)
class OeqaInputs:
    root: Path
    build_dir: Path
    image: str
    run_dir: Path
    commands_file: Path
    timeout_oeqa: int
    dry_run: bool
    host_python_bin: Path | None = None
    kinds: tuple[str, ...] = ("current", "extended")


@dataclass(frozen=True, slots=True)
class OeqaLane:
    name: str
    kind: str
    argv: list[str]
    command: list[str]
    conf_path: Path
    stdout_log: Path
    stderr_log: Path
    output_dir: Path


@dataclass(slots=True)
class OeqaProgressTail:
    inputs: OeqaInputs
    lane: OeqaLane
    min_mtime: float
    log_path: Path | None = None
    offset: int = 0
    active_test: str | None = None
    completed: set[str] = field(default_factory=set)


class OeqaConfRejectedError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def _read_json(path: Path) -> JsonObject:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _json_strings(values: list[str]) -> list[JsonValue]:
    return [value for value in values]


def _json_objects(values: list[JsonObject]) -> list[JsonValue]:
    return [value for value in values]


def _int_positive(value: str) -> int:
    return int(value) if value.isdigit() and int(value) > 0 else 10800


def _append(inputs: OeqaInputs, record: JsonObject) -> None:
    inputs.commands_file.parent.mkdir(parents=True, exist_ok=True)
    with inputs.commands_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _conf_path(inputs: OeqaInputs, kind: str, manifest: JsonObject) -> Path:
    result = write_conf(
        ConfRequest(
            inputs.root,
            inputs.build_dir,
            "apollo-fvp",
            inputs.run_dir,
            kind,
            str(inputs.timeout_oeqa),
        ),
        manifest,
    )
    if result.conf_path is None:
        raise OeqaConfRejectedError(result.message)
    return result.conf_path


def _lane(inputs: OeqaInputs, kind: str, manifest: JsonObject) -> OeqaLane | None:
    conf_path = _conf_path(inputs, kind, manifest)
    if conf_path is None:
        return None
    lane_dir = inputs.run_dir / "oeqa" / kind
    script = _bitbake_env_script(inputs, f"bitbake -R {shlex.quote(str(conf_path))} {shlex.quote(inputs.image)} -c testimage")
    argv = ["timeout", str(inputs.timeout_oeqa), "bash", "-lc", script]
    return OeqaLane(
        name=f"oeqa-{kind}",
        kind=kind,
        argv=argv,
        command=argv,
        conf_path=conf_path,
        stdout_log=lane_dir / "bitbake.stdout.log",
        stderr_log=lane_dir / "bitbake.stderr.log",
        output_dir=lane_dir,
    )


def _bitbake_env_script(inputs: OeqaInputs, command: str) -> str:
    host_python_prefix = ""
    if inputs.host_python_bin is not None:
        host_python_prefix = f"export PATH={shlex.quote(str(inputs.host_python_bin.parent))}:$PATH && "
    return f"{host_python_prefix}source layers/poky/oe-init-build-env {shlex.quote(str(inputs.build_dir))} >/dev/null && {command}"


def build_lanes(inputs: OeqaInputs) -> list[OeqaLane]:
    manifest = _read_json(inputs.run_dir / "manifest.json")
    lanes = [_lane(inputs, kind, manifest) for kind in inputs.kinds]
    return [lane for lane in lanes if lane is not None]


def _result_paths(lane: OeqaLane) -> list[Path]:
    results_dir = lane.output_dir / "results"
    if not results_dir.is_dir():
        return []
    return sorted(path for path in results_dir.rglob("*.json") if path.is_file())


def _artifacts(inputs: OeqaInputs, lane: OeqaLane) -> list[JsonObject]:
    artifacts: list[JsonObject] = [{"kind": "conf", "path": _rel(lane.conf_path, inputs.run_dir)}]
    roots = ((lane.output_dir / "logs", "oeqa_log"), (lane.output_dir / "results", "oeqa_result_artifact"), (lane.output_dir / "artifacts", "oeqa_artifact"))
    for root, kind in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            artifact_kind = "oeqa_result" if root == lane.output_dir / "results" and path.suffix == ".json" else kind
            artifacts.append({"kind": artifact_kind, "path": _rel(path, inputs.run_dir)})
    return artifacts


def _oeqa_status_label(status: str) -> str:
    return OEQA_STATUS_LABELS.get(status.upper(), status.lower())


def _oeqa_note_status_label(status: str) -> str:
    if status.lower().startswith("skipped"):
        return "skipped"
    return _oeqa_status_label(status)


def _iter_oeqa_result_tests(data: JsonObject) -> list[tuple[str, str]]:
    tests: list[tuple[str, str]] = []
    for image_data in data.values():
        match image_data:
            case {"result": dict() as results}:
                for test_name, outcome in results.items():
                    match outcome:
                        case {"status": str() as status}:
                            tests.append((test_name, _oeqa_status_label(status)))
                        case _:
                            continue
            case _:
                continue
    return tests


def _emit_test_start(lane: OeqaLane, test_name: str) -> None:
    print(f"[run_test] START {lane.name}:{test_name}", flush=True)


def _emit_test_done(lane: OeqaLane, test_name: str, status: str) -> None:
    print(f"[run_test] DONE {lane.name}:{test_name} ({status})", flush=True)


def _emit_result_progress(
    lane: OeqaLane,
    result_paths: list[Path],
    completed: set[str],
) -> None:
    for result_path in result_paths:
        for test_name, status in _iter_oeqa_result_tests(_read_json(result_path)):
            key = f"{lane.name}:{test_name}"
            if key in completed:
                continue
            completed.add(key)
            _emit_test_start(lane, test_name)
            _emit_test_done(lane, test_name, status)


def _latest_testimage_log(inputs: OeqaInputs, min_mtime: float) -> Path | None:
    work_root = inputs.root / inputs.build_dir / "tmp_baremetal" / "work"
    newest: tuple[float, Path] | None = None
    for path in work_root.glob(f"*-poky-linux/{inputs.image}/1.0/temp/log.do_testimage.*"):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime < min_mtime:
            continue
        if newest is None or mtime > newest[0]:
            newest = (mtime, path)
    return None if newest is None else newest[1]


def _emit_do_testimage_line(progress: OeqaProgressTail, line: str) -> None:
    start_match = TEST_START_RE.match(line)
    if start_match is not None:
        class_path = start_match.group("class")
        method = start_match.group("method")
        test_name = class_path if class_path.endswith(f".{method}") else f"{class_path}.{method}"
        key = f"{progress.lane.name}:{test_name}"
        if key not in progress.completed:
            _emit_test_start(progress.lane, test_name)
        progress.active_test = test_name
        return

    done_match = TEST_DONE_RE.match(line)
    if done_match is None or progress.active_test is None:
        return
    test_name = progress.active_test
    key = f"{progress.lane.name}:{test_name}"
    if key not in progress.completed:
        progress.completed.add(key)
        _emit_test_done(
            progress.lane,
            test_name,
            _oeqa_note_status_label(done_match.group("status")),
        )
    progress.active_test = None


def _poll_progress(progress: OeqaProgressTail) -> None:
    if progress.log_path is None:
        progress.log_path = _latest_testimage_log(progress.inputs, progress.min_mtime)
    if progress.log_path is None:
        return
    try:
        with progress.log_path.open("r", encoding="utf-8", errors="replace") as stream:
            stream.seek(progress.offset)
            for line in stream:
                _emit_do_testimage_line(progress, line.rstrip("\n"))
            progress.offset = stream.tell()
    except OSError:
        return


def _record_dry_run(inputs: OeqaInputs, lane: OeqaLane) -> None:
    now = _now()
    print(f"[run_test] SKIP {lane.name} (dry-run)", flush=True)
    _append(
        inputs,
        {
            "name": lane.name,
            "argv": _json_strings(lane.argv),
            "required": True,
            "status": "skipped",
            "started_at": now,
            "finished_at": now,
            "duration_s": 0.0,
            "artifacts": _json_objects(_artifacts(inputs, lane)),
        },
    )


def _cleanup_process_group(pid: int) -> None:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return
        time.sleep(0.2)


def _kill_bitbake_server(inputs: OeqaInputs, lane: OeqaLane) -> None:
    cleanup_log = lane.output_dir / "logs" / "bitbake-kill-server.log"
    cleanup_log.parent.mkdir(parents=True, exist_ok=True)
    script = _bitbake_env_script(inputs, "bitbake -m")
    print(f"[run_test] START {lane.name} bitbake-kill-server", flush=True)
    with cleanup_log.open("a", encoding="utf-8") as stream:
        stream.write(f"[run_test] START {lane.name} bitbake-kill-server\n")
        stream.flush()
        result = subprocess.run(
            ["timeout", "60", "bash", "-lc", script],
            cwd=inputs.root,
            check=False,
            text=True,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
        stream.write(f"[run_test] DONE {lane.name} bitbake-kill-server ({result.returncode})\n")
    print(f"[run_test] DONE {lane.name} bitbake-kill-server ({result.returncode})", flush=True)


def _run_command(inputs: OeqaInputs, lane: OeqaLane) -> tuple[int, set[str]]:
    with lane.stdout_log.open("w", encoding="utf-8") as stdout, lane.stderr_log.open("w", encoding="utf-8") as stderr:
        try:
            process = subprocess.Popen(
                lane.command,
                cwd=inputs.root,
                text=True,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
        except OSError as exc:
            stderr.write(f"{exc}\n")
            return 127, set()
        returncode = 127
        progress = OeqaProgressTail(inputs, lane, time.time())
        try:
            while True:
                returncode = process.poll()
                _poll_progress(progress)
                if returncode is not None:
                    break
                time.sleep(1.0)
            _poll_progress(progress)
        except KeyboardInterrupt:
            _cleanup_process_group(process.pid)
            _kill_bitbake_server(inputs, lane)
            raise
        finally:
            _cleanup_process_group(process.pid)
        if returncode == 124:
            _kill_bitbake_server(inputs, lane)
        return returncode, progress.completed


def _record_run(inputs: OeqaInputs, lane: OeqaLane) -> str:
    lane.stdout_log.parent.mkdir(parents=True, exist_ok=True)
    lane.stderr_log.parent.mkdir(parents=True, exist_ok=True)
    started_at = _now()
    started = monotonic()
    print(f"[run_test] START {lane.name}", flush=True)
    returncode, live_tests = _run_command(inputs, lane)
    result_paths = _result_paths(lane)
    _emit_result_progress(lane, result_paths, live_tests)
    json_states = [(path, classify_oeqa_result_path(path).state) for path in result_paths]
    failed_json = any(state == OeqaResultState.FAIL for _, state in json_states)
    malformed_json = [_rel(path, inputs.run_dir) for path, state in json_states if state == OeqaResultState.MALFORMED]
    artifacts = _artifacts(inputs, lane)
    record: JsonObject = {
        "name": lane.name,
        "argv": _json_strings(lane.argv),
        "required": True,
        "started_at": started_at,
        "finished_at": _now(),
        "duration_s": round(monotonic() - started, 6),
        "stdout_log": _rel(lane.stdout_log, inputs.run_dir),
        "stderr_log": _rel(lane.stderr_log, inputs.run_dir),
        "artifacts": _json_objects(artifacts),
    }
    if failed_json or returncode not in {0, 124}:
        record["status"] = "fail"
        record["exit_code"] = returncode
        state = "fail"
    elif malformed_json:
        record["status"] = "blocked"
        record["blockers"] = _json_objects(
            [
                {
                    "reason": "blocked_malformed_oeqa_result",
                    "paths": _json_strings(malformed_json),
                }
            ]
        )
        state = "blocked"
    elif returncode == 124:
        record["status"] = "blocked"
        record["blockers"] = _json_objects([{"reason": "blocked_timeout", "lane": lane.kind}])
        state = "blocked"
    else:
        record["status"] = "pass"
        record["exit_code"] = 0
        state = "pass"
    _append(inputs, record)
    print(f"[run_test] DONE {lane.name} ({state})", flush=True)
    return state


def run_lanes(inputs: OeqaInputs) -> int:
    states: list[str] = []
    try:
        lanes = build_lanes(inputs)
    except OeqaConfRejectedError as exc:
        print(exc.message, file=sys.stderr)
        return 2
    for lane in lanes:
        if inputs.dry_run:
            _record_dry_run(inputs, lane)
            states.append("pass")
            continue
        states.append(_record_run(inputs, lane))
    if "fail" in states:
        return 1
    if "blocked" in states:
        return 2
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Apollo OEQA validation lanes.")
    parser.add_argument("--build-dir", type=Path, default=Path("build"))
    parser.add_argument("--image", default="nexios-image")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--commands-file", type=Path, required=True)
    parser.add_argument("--timeout-oeqa", default="10800")
    parser.add_argument("--host-python-bin", type=Path)
    parser.add_argument(
        "--kind",
        action="append",
        choices=("current", "functional", "power", "extended"),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_lanes(
        OeqaInputs(
            Path.cwd(),
            args.build_dir,
            args.image,
            args.run_dir,
            args.commands_file,
            _int_positive(args.timeout_oeqa),
            args.dry_run,
            args.host_python_bin,
            tuple(args.kind or ("current", "extended")),
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())

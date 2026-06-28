#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import signal
import shlex
import subprocess
import sys
import time
from time import monotonic

from run_test_conf import ConfRequest, write_conf
from run_test_oeqa_result import OeqaResultState, classify_oeqa_result_path


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

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


def _int_positive(value: str) -> int:
    return int(value) if value.isdigit() and int(value) > 0 else 10800


def _append(inputs: OeqaInputs, record: JsonObject) -> None:
    inputs.commands_file.parent.mkdir(parents=True, exist_ok=True)
    with inputs.commands_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _conf_path(inputs: OeqaInputs, kind: str, manifest: JsonObject) -> Path:
    result = write_conf(
        ConfRequest(inputs.root, inputs.build_dir, "apollo-fvp", inputs.run_dir, kind),
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
    lanes = [_lane(inputs, "current", manifest), _lane(inputs, "extended", manifest)]
    return [lane for lane in lanes if lane is not None]


def _result_paths(lane: OeqaLane) -> list[Path]:
    results_dir = lane.output_dir / "results"
    if not results_dir.is_dir():
        return []
    return sorted(path for path in results_dir.rglob("*.json") if path.is_file())


def _artifacts(inputs: OeqaInputs, lane: OeqaLane) -> list[JsonObject]:
    artifacts: list[JsonObject] = [{"kind": "conf", "path": _rel(lane.conf_path, inputs.run_dir)}]
    roots = ((lane.output_dir / "logs", "oeqa_log"), (lane.output_dir / "results", "oeqa_result"), (lane.output_dir / "artifacts", "oeqa_artifact"))
    for root, kind in roots:
        if not root.is_dir():
            continue
        artifacts.extend({"kind": kind, "path": _rel(path, inputs.run_dir)} for path in sorted(root.rglob("*")) if path.is_file())
    return artifacts


def _record_dry_run(inputs: OeqaInputs, lane: OeqaLane) -> None:
    now = _now()
    print(f"[run_test] SKIP {lane.name} (dry-run)", flush=True)
    _append(inputs, {"name": lane.name, "argv": lane.argv, "required": True, "status": "skipped", "started_at": now, "finished_at": now, "duration_s": 0.0, "artifacts": _artifacts(inputs, lane)})


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


def _run_command(inputs: OeqaInputs, lane: OeqaLane) -> int:
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
            return 127
        returncode = 127
        try:
            returncode = process.wait()
        finally:
            _cleanup_process_group(process.pid)
        if returncode == 124:
            _kill_bitbake_server(inputs, lane)
        return returncode


def _record_run(inputs: OeqaInputs, lane: OeqaLane) -> str:
    lane.stdout_log.parent.mkdir(parents=True, exist_ok=True)
    lane.stderr_log.parent.mkdir(parents=True, exist_ok=True)
    started_at = _now()
    started = monotonic()
    print(f"[run_test] START {lane.name}", flush=True)
    returncode = _run_command(inputs, lane)
    result_paths = _result_paths(lane)
    json_states = [(path, classify_oeqa_result_path(path).state) for path in result_paths]
    failed_json = any(state == OeqaResultState.FAIL for _, state in json_states)
    malformed_json = [_rel(path, inputs.run_dir) for path, state in json_states if state == OeqaResultState.MALFORMED]
    artifacts = _artifacts(inputs, lane)
    record: JsonObject = {"name": lane.name, "argv": lane.argv, "required": True, "started_at": started_at, "finished_at": _now(), "duration_s": round(monotonic() - started, 6), "stdout_log": _rel(lane.stdout_log, inputs.run_dir), "stderr_log": _rel(lane.stderr_log, inputs.run_dir), "artifacts": artifacts}
    if failed_json or returncode not in {0, 124}:
        record.update({"status": "fail", "exit_code": returncode})
        state = "fail"
    elif malformed_json:
        record.update({"status": "blocked", "blockers": [{"reason": "blocked_malformed_oeqa_result", "paths": malformed_json}]})
        state = "blocked"
    elif returncode == 124:
        record.update({"status": "blocked", "blockers": [{"reason": "blocked_timeout", "lane": lane.kind}]})
        state = "blocked"
    else:
        record.update({"status": "pass", "exit_code": 0})
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
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())

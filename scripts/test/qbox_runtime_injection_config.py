from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Final

if __package__:
    from .qbox_runtime_injection_support import (
        JsonObject,
        JsonValue,
        ScenarioError,
        parse_json_object,
    )
else:
    from qbox_runtime_injection_support import (
        JsonObject,
        JsonValue,
        ScenarioError,
        parse_json_object,
    )


DEFAULT_PORT: Final = 18080
PROTECTED_RUNNER_ARGS: Final = (
    "--monitor",
    "--monitor-port",
    "--out-dir",
    "--timeout",
    "--keep-running-after-pass",
)
PERSISTENT_ACTIONS: Final = frozenset({"drive-high", "drive-low", "set-control"})


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    requests: tuple[JsonObject, ...]
    release_requests: tuple[JsonObject, ...]
    targets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    workspace: Path
    output_dir: Path
    monitor_port: int
    timeout_seconds: int
    runner_args: tuple[str, ...]


def parse_requests(
    value: JsonValue | None,
    source: str,
    required: bool,
) -> tuple[JsonObject, ...]:
    if value is None and not required:
        return ()
    if not isinstance(value, list) or (required and not value):
        raise ScenarioError(f"{source}: requests must be a non-empty array")
    records: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ScenarioError(f"{source}: request {index} must be an object")
        target, action = item.get("target"), item.get("action")
        if (
            not isinstance(target, str)
            or not target
            or not isinstance(action, str)
            or not action
        ):
            raise ScenarioError(
                f"{source}: request {index} needs non-empty target and action"
            )
        records.append(item)
    return tuple(records)


def load_scenario(path: Path) -> Scenario:
    source = str(path)
    document = parse_json_object(path.read_text(encoding="utf-8"), source)
    requests = parse_requests(document.get("requests"), source, True)
    releases = parse_requests(document.get("release_requests"), source, False)
    release_targets = {str(record["target"]) for record in releases}
    missing_release = [
        str(record["target"])
        for record in requests
        if record.get("action") in PERSISTENT_ACTIONS
        and str(record["target"]) not in release_targets
    ]
    if missing_release:
        raise ScenarioError(
            f"{path}: persistent targets require release_requests: "
            + ", ".join(missing_release)
        )
    name = document.get("name", path.stem)
    if not isinstance(name, str) or not name:
        raise ScenarioError(f"{path}: name must be a non-empty string")
    targets = tuple(
        dict.fromkeys(str(record["target"]) for record in (*requests, *releases))
    )
    return Scenario(name, requests, releases, targets)


def build_runner_command(
    config: RuntimeConfig,
) -> tuple[tuple[str, ...], dict[str, str]]:
    command = (
        sys.executable,
        str(config.workspace / "scripts/run/run_qbox_apollo_fvp_full.py"),
        "--out-dir",
        str(config.output_dir / "canonical"),
        "--timeout",
        str(config.timeout_seconds),
        "--monitor",
        "--monitor-port",
        str(config.monitor_port),
        "--keep-running-after-pass",
        *config.runner_args,
    )
    environment = os.environ.copy()
    environment.update(
        {
            "QBOX_APOLLO_RUNTIME_INJECTION": "true",
            "QBOX_RUNTIME_INJECTION_RUN_TOKEN": str(config.output_dir),
            "QBOX_APOLLO_MONITOR_BIND_ADDRESS": "127.0.0.1",
            "QBOX_APOLLO_MONITOR": "true",
            "QBOX_APOLLO_MONITOR_PORT": str(config.monitor_port),
        }
    )
    return command, environment


def parse_cli(
    argv: list[str] | None,
    workspace: Path,
) -> tuple[RuntimeConfig, tuple[Scenario, ...]]:
    parser = argparse.ArgumentParser(
        description="Run QBox runtime-injection scenarios."
    )
    parser.add_argument("scenario", type=Path, nargs="+")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=workspace / "build/qbox-apollo-qvp/runtime-injection",
    )
    parser.add_argument("--monitor-port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--runner-arg", action="append", default=[])
    args = parser.parse_args(argv)
    if not 1 <= args.monitor_port <= 65535:
        parser.error("--monitor-port must be in range 1..65535")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if any(
        value == name or value.startswith(name + "=")
        for value in args.runner_arg
        for name in PROTECTED_RUNNER_ARGS
    ):
        parser.error(
            "--runner-arg cannot override harness monitor, output, "
            "timeout, or child-lifetime settings"
        )
    config = RuntimeConfig(
        workspace,
        args.out_dir.resolve(),
        args.monitor_port,
        args.timeout,
        tuple(args.runner_arg),
    )
    return config, tuple(load_scenario(path) for path in args.scenario)

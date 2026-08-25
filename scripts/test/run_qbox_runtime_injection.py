#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import quote

if __package__:
    from .qbox_runtime_injection_config import (
        RuntimeConfig,
        Scenario,
        PERSISTENT_ACTIONS,
        build_runner_command,
        parse_cli,
    )
    from .qbox_runtime_injection_support import (
        ApiClient,
        HttpRequest,
        JsonObject,
        RuntimeFailure,
        RuntimeSession,
        ScenarioError,
        TERMINAL_STATES,
        artifact_verdict,
        capture_log_offsets,
        parse_json_object,
        post_action_failures,
        terminate_owned_process_groups,
    )
else:
    from qbox_runtime_injection_config import (
        RuntimeConfig,
        Scenario,
        PERSISTENT_ACTIONS,
        build_runner_command,
        parse_cli,
    )
    from qbox_runtime_injection_support import (
        ApiClient,
        HttpRequest,
        JsonObject,
        RuntimeFailure,
        RuntimeSession,
        ScenarioError,
        TERMINAL_STATES,
        artifact_verdict,
        capture_log_offsets,
        parse_json_object,
        post_action_failures,
        terminate_owned_process_groups,
    )


def wait_for_ready(session: RuntimeSession) -> None:
    deadline = time.monotonic() + min(session.timeout_seconds, 120.0)
    while time.monotonic() < deadline:
        if not session.live():
            raise RuntimeFailure("canonical runner exited before monitor readiness")
        try:
            response = session.client.request(
                HttpRequest("GET", "/sc_time", timeout_seconds=1.0)
            )
            if 200 <= response.status < 300:
                return
        except RuntimeFailure:
            time.sleep(0.2)
            continue
        time.sleep(0.2)
    raise RuntimeFailure("monitor /sc_time did not become ready before timeout")


def poll_terminal(session: RuntimeSession, request_id: int) -> JsonObject:
    deadline = time.monotonic() + 30.0
    endpoint = f"/api/v1/injections/{request_id}"
    while time.monotonic() < deadline:
        if not session.live():
            raise RuntimeFailure(
                f"canonical runner exited while injection {request_id} was pending"
            )
        response = session.client.request(
            HttpRequest("GET", endpoint, timeout_seconds=1.0)
        )
        state = response.body.get("state")
        if (
            response.status == 200
            and isinstance(state, str)
            and state in TERMINAL_STATES
        ):
            return response.body
        time.sleep(0.1)
    raise RuntimeFailure(f"injection {request_id} did not reach a terminal state")


def capture_targets(client: ApiClient, targets: tuple[str, ...]) -> JsonObject:
    return {
        target: client.request(
            HttpRequest(
                "GET",
                f"/api/v1/injection/targets/{quote(target, safe='')}",
            )
        ).body
        for target in targets
    }


def execute_actions(
    session: RuntimeSession,
    requests: tuple[JsonObject, ...],
) -> list[JsonObject]:
    records: list[JsonObject] = []
    for payload in requests:
        accepted = session.client.request(
            HttpRequest("POST", "/api/v1/injections", payload)
        )
        request_id = accepted.body.get("id")
        if accepted.status != 202 or not isinstance(request_id, int):
            raise RuntimeFailure(
                f"injection rejected: HTTP {accepted.status}: {accepted.body}"
            )
        action = payload.get("action")
        accepted_state = accepted.body.get("state")
        status = (
            accepted.body
            if action in PERSISTENT_ACTIONS and accepted_state == "active"
            else poll_terminal(session, request_id)
        )
        records.append(
            {
                "request": payload,
                "accepted": accepted.body,
                "status": status,
            }
        )
    return records


def wait_for_canonical_pass(session: RuntimeSession, result_path: Path) -> None:
    deadline = time.monotonic() + session.timeout_seconds
    while time.monotonic() < deadline:
        if result_path.exists():
            result = parse_json_object(
                result_path.read_text(encoding="utf-8"), str(result_path)
            )
            if result.get("passed") is True:
                return
            if result.get("blocker") is not None:
                raise RuntimeFailure(
                    f"canonical runtime failed: {result.get('blocker')}"
                )
        if not session.live():
            raise RuntimeFailure("canonical runner process group exited before PASS")
        time.sleep(0.2)
    raise RuntimeFailure("canonical runtime did not reach PASS before timeout")


def run(config: RuntimeConfig, scenarios: tuple[Scenario, ...]) -> JsonObject:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    command, environment = build_runner_command(config)
    base_url = f"http://127.0.0.1:{config.monitor_port}"
    runner_log = config.output_dir / "canonical-runner.log"
    with runner_log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            command,
            cwd=config.workspace,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
    session = RuntimeSession(
        process.pid, ApiClient(base_url), float(config.timeout_seconds)
    )
    try:
        wait_for_ready(session)
        canonical_dir = config.output_dir / "canonical"
        wait_for_canonical_pass(session, canonical_dir / "result.json")
        log_offsets = capture_log_offsets(canonical_dir)
        capabilities = session.client.request(
            HttpRequest("GET", "/api/v1/injection/capabilities")
        ).body
        capability_path = config.output_dir / "capabilities.json"
        capability_path.write_text(
            json.dumps(capabilities, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        records: list[JsonObject] = []
        for scenario in scenarios:
            pre = capture_targets(session.client, scenario.targets)
            actions = execute_actions(session, scenario.requests)
            post = capture_targets(session.client, scenario.targets)
            releases = execute_actions(session, scenario.release_requests)
            records.append(
                {
                    "scenario": scenario.name,
                    "pre": pre,
                    "actions": actions,
                    "post": post,
                    "release_actions": releases,
                    "released": capture_targets(session.client, scenario.targets),
                }
            )
        all_actions = [
            action
            for record in records
            for action in [*record["actions"], *record["release_actions"]]
            if isinstance(action, dict)
        ]
        time.sleep(0.5)
        runtime_failures = post_action_failures(canonical_dir, log_offsets)
        result: JsonObject = {
            "schema_version": 1,
            "command": list(command),
            "base_url": base_url,
            "capabilities": str(capability_path),
            "canonical_artifacts": {
                "result": str(canonical_dir / "result.json"),
                "summary": str(canonical_dir / "summary.txt"),
            },
            "scenarios": records,
            "verdict": artifact_verdict(
                canonical_dir / "result.json", all_actions, runtime_failures
            ),
        }
        (config.output_dir / "runtime-injection-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return result
    finally:
        terminate_owned_process_groups(process, str(config.output_dir))


def main(argv: list[str] | None = None) -> int:
    try:
        workspace = Path(__file__).resolve().parents[2]
        config, scenarios = parse_cli(argv, workspace)
        result = run(config, scenarios)
    except (OSError, RuntimeFailure, ScenarioError) as error:
        print(f"runtime-injection harness failed: {error}", file=sys.stderr)
        return 1
    verdict = result["verdict"]
    print(json.dumps(verdict, sort_keys=True))
    return 0 if isinstance(verdict, dict) and verdict.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())

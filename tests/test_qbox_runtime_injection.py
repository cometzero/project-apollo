from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess

import pytest

from scripts.test import run_qbox_runtime_injection as harness
from scripts.test import qbox_runtime_injection_config as runtime_config
from scripts.test import qbox_runtime_injection_support as runtime_support
from scripts.test.qbox_runtime_injection_support import HttpResponse


def test_load_scenario_requires_nonempty_request_list(tmp_path: Path) -> None:
    # Given: a malformed scenario with no injection request.
    scenario_path = tmp_path / "invalid.json"
    scenario_path.write_text(json.dumps({"name": "empty", "requests": []}))

    # When/Then: parsing fails before a runtime process is started.
    with pytest.raises(harness.ScenarioError, match="requests"):
        runtime_config.load_scenario(scenario_path)


def test_load_scenario_collects_release_requests_and_targets(tmp_path: Path) -> None:
    # Given: one GPIO action and its explicit release action.
    scenario_path = tmp_path / "gpio.json"
    scenario_path.write_text(
        json.dumps(
            {
                "name": "gpio-release",
                "requests": [
                    {"target": "apollo.gpio.rse0.pin3", "action": "drive-high"}
                ],
                "release_requests": [
                    {"target": "apollo.gpio.rse0.pin3", "action": "release"}
                ],
            }
        )
    )

    # When: the scenario crosses the JSON boundary.
    scenario = runtime_config.load_scenario(scenario_path)

    # Then: the harness retains the typed action groups and target snapshot set.
    assert scenario.name == "gpio-release"
    assert len(scenario.requests) == 1
    assert len(scenario.release_requests) == 1
    assert scenario.targets == ("apollo.gpio.rse0.pin3",)


def test_load_scenario_requires_release_for_persistent_action(
    tmp_path: Path,
) -> None:
    scenario_path = tmp_path / "gpio.json"
    scenario_path.write_text(
        json.dumps(
            {
                "requests": [
                    {
                        "target": "apollo.gpio.rse0.pin3",
                        "action": "drive-high",
                    }
                ],
            }
        )
    )

    with pytest.raises(harness.ScenarioError, match="release_requests"):
        runtime_config.load_scenario(scenario_path)


def test_build_runner_command_enables_loopback_runtime_actions(tmp_path: Path) -> None:
    # Given: a bounded runner configuration with an additional platform parameter.
    config = runtime_config.RuntimeConfig(
        workspace=Path("/workspace"),
        output_dir=tmp_path,
        monitor_port=19081,
        timeout_seconds=600,
        runner_args=("--platform-param", "apollo.runtime_actions=true"),
    )

    # When: the canonical child command and environment are constructed.
    command, environment = runtime_config.build_runner_command(config)

    # Then: monitor, retained child mode, and fail-closed runtime feature values are set.
    assert command[:2] == (
        harness.sys.executable,
        "/workspace/scripts/run/run_qbox_apollo_fvp_full.py",
    )
    assert "--monitor" in command
    assert command[command.index("--monitor-port") + 1] == "19081"
    assert "--keep-running-after-pass" in command
    assert command[-2:] == ("--platform-param", "apollo.runtime_actions=true")
    assert environment["QBOX_APOLLO_RUNTIME_INJECTION"] == "true"
    assert environment["QBOX_RUNTIME_INJECTION_RUN_TOKEN"] == str(tmp_path)
    assert environment["QBOX_APOLLO_MONITOR_BIND_ADDRESS"] == "127.0.0.1"
    assert environment["QBOX_APOLLO_MONITOR"] == "true"
    assert environment["QBOX_APOLLO_MONITOR_PORT"] == "19081"


def test_parse_args_rejects_runner_override_of_monitor_endpoint(tmp_path: Path) -> None:
    # Given: a valid scenario and an attempt to move the child monitor port.
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text(
        json.dumps({"requests": [{"target": "x", "action": "read"}]})
    )

    # When/Then: endpoint ownership remains with the harness configuration.
    with pytest.raises(SystemExit):
        runtime_config.parse_cli(
            [str(scenario_path), "--runner-arg=--monitor-port=19082"],
            Path("/workspace"),
        )


def test_request_json_preserves_curl_http_error_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the monitor rejects a request with its JSON error contract.
    captured: list[str] = []

    def run_curl(command: list[str], **kwargs: str) -> subprocess.CompletedProcess[str]:
        captured.extend(command)
        return subprocess.CompletedProcess(
            command, 0, '{"code":"mutation-disabled"}\n403', ""
        )

    monkeypatch.setattr(subprocess, "run", run_curl)

    # When: the HTTP boundary posts an injection.
    client = harness.ApiClient("http://127.0.0.1:18080")
    response = client.request(
        harness.HttpRequest("POST", "/api/v1/injections", {"target": "x"}, 1.0)
    )

    # Then: the service status and JSON error body are preserved for the artifact.
    assert response.status == 403
    assert response.body == {"code": "mutation-disabled"}
    assert captured[:5] == ["curl", "--silent", "--show-error", "--request", "POST"]


def test_poll_terminal_waits_for_completed_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: an accepted injection that becomes completed on the second poll.
    bodies = iter(({"state": "active"}, {"state": "completed", "result": "ok"}))
    monkeypatch.setattr(
        harness.ApiClient,
        "request",
        lambda _client, _request: HttpResponse(status=200, body=next(bodies)),
    )
    monkeypatch.setattr(harness.RuntimeSession, "live", lambda _session: True)
    monkeypatch.setattr(harness.time, "sleep", lambda _: None)
    session = harness.RuntimeSession(
        123, harness.ApiClient("http://127.0.0.1:18080"), 1.0
    )

    # When: status polling runs with a live child predicate.
    status = harness.poll_terminal(session, 7)

    # Then: it returns the first terminal record rather than treating active as pass.
    assert status["state"] == "completed"


def test_execute_actions_accepts_persistent_active_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        harness.ApiClient,
        "request",
        lambda _client, _request: HttpResponse(
            status=202,
            body={"id": 11, "state": "active", "result": "active"},
        ),
    )
    session = harness.RuntimeSession(
        123, harness.ApiClient("http://127.0.0.1:18080"), 1.0
    )

    records = harness.execute_actions(
        session,
        ({"target": "apollo.gpio.rse0.pin3", "action": "drive-high"},),
    )

    assert records[0]["status"]["state"] == "active"


def test_artifact_verdict_requires_terminal_actions_and_canonical_pass(
    tmp_path: Path,
) -> None:
    # Given: all action records complete but the canonical boot result fails.
    result_path = tmp_path / "canonical" / "result.json"
    result_path.parent.mkdir()
    result_path.write_text(json.dumps({"passed": False, "blocker": "boot"}))

    # When: the final artifact verdict is assembled.
    verdict = harness.artifact_verdict(
        result_path,
        [{"status": {"state": "completed"}}],
    )

    # Then: action success cannot mask a failed canonical runtime.
    assert verdict["runtime_actions_passed"] is True
    assert verdict["canonical_passed"] is False
    assert verdict["passed"] is False


def test_wait_for_canonical_pass_accepts_preserved_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"passed": True, "blocker": None}))
    monkeypatch.setattr(harness.RuntimeSession, "live", lambda _session: True)
    session = harness.RuntimeSession(
        123, harness.ApiClient("http://127.0.0.1:18080"), 1.0
    )

    harness.wait_for_canonical_pass(session, result_path)


def test_artifact_verdict_accepts_active_action_with_completed_release(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"passed": True, "blocker": None}))

    verdict = harness.artifact_verdict(
        result_path,
        [
            {"status": {"state": "active"}},
            {"status": {"state": "completed"}},
        ],
    )

    assert verdict["passed"] is True


def test_artifact_verdict_rejects_post_action_runtime_failure(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps({"passed": True, "blocker": None}))

    verdict = harness.artifact_verdict(
        result_path,
        [{"status": {"state": "completed"}}],
        [{"log": "qbox-safety-island-cl0.log", "pattern": "Unhandled exception"}],
    )

    assert verdict["runtime_actions_passed"] is True
    assert verdict["passed"] is False


def test_terminate_owned_groups_stops_runner_and_lingering_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals: list[tuple[int, int]] = []

    def kill_group(group: int, sent_signal: int) -> None:
        signals.append((group, sent_signal))
        if sent_signal == 0:
            raise ProcessLookupError

    monkeypatch.setattr(os, "killpg", kill_group)
    monkeypatch.setattr(
        runtime_support,
        "_owned_process_groups_with_token",
        lambda _token: {456},
    )
    process = subprocess.Popen(
        ["/bin/true"],
        text=True,
        start_new_session=True,
    )
    process.wait()

    harness.terminate_owned_process_groups(process, "runtime-test")

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, 0),
        (456, signal.SIGTERM),
        (456, 0),
    ]

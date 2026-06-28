from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/test"))

from run_test_qbox_lane_defs import QboxInputs, QboxLane
import run_test_qbox_lanes
from run_test_summary import summarize_run


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run_test.sh"

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


def run_runner(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(RUNNER), *args],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_commands(run_dir: Path) -> list[JsonObject]:
    return [
        json.loads(line)
        for line in (run_dir / "commands.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def command_texts(run_dir: Path) -> list[str]:
    return [" ".join(command.get("argv", [])) for command in load_commands(run_dir)]


def load_json(path: Path) -> JsonObject:
    return json.loads(path.read_text(encoding="utf-8"))


def fake_runtime_script(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "from pathlib import Path",
                "result = Path(sys.argv[1])",
                "mode = sys.argv[2]",
                "marker = Path(sys.argv[3])",
                "result.parent.mkdir(parents=True, exist_ok=True)",
                "if mode == 'blocked':",
                "    result.write_text(json.dumps({'passed': False, 'blocker': 'blocked_missing_runtime_artifact'}))",
                "    raise SystemExit(1)",
                "if mode == 'fail':",
                "    result.write_text(json.dumps({'passed': False}))",
                "    raise SystemExit(1)",
                "marker.write_text('live ran')",
                "result.write_text(json.dumps({'passed': True, 'blocker': None}))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def fake_lane(tmp_path: Path, name: str, mode: str) -> QboxLane:
    lane_dir = tmp_path / "lanes" / name
    script = tmp_path / "fake_runtime.py"
    marker = tmp_path / f"{name}-ran.txt"
    fake_runtime_script(script)
    result = lane_dir / "result.json"
    return QboxLane(
        name,
        [sys.executable, str(script), str(result), mode, str(marker)],
        [sys.executable, str(script), str(result), mode, str(marker)],
        ROOT,
        lane_dir / "stdout.log",
        lane_dir / "stderr.log",
        lane_dir,
        True,
    )


def command_by_name(commands: list[JsonObject], name: str) -> JsonObject:
    return next(command for command in commands if command.get("name") == name)


def qbox_inputs(
    tmp_path: Path,
    include_runtime: bool = True,
    skip_runtime: bool = False,
) -> QboxInputs:
    return QboxInputs(
        root=ROOT,
        run_dir=tmp_path / "run",
        commands_file=tmp_path / "run/commands.jsonl",
        dry_run=False,
        include_runtime=include_runtime,
        skip_runtime=skip_runtime,
        timeout_fvp="600",
    )


def patch_qbox_lanes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, check_mode: str) -> None:
    build_dir = tmp_path / "qbox-platform"
    build_dir.mkdir()
    monkeypatch.setenv("RUN_TEST_QBOX_BUILD_DIR", str(build_dir))
    monkeypatch.setattr(run_test_qbox_lanes, "static_lanes", lambda inputs: [])
    monkeypatch.setattr(run_test_qbox_lanes, "ctest_lanes", lambda inputs: [])
    monkeypatch.setattr(
        run_test_qbox_lanes,
        "runtime_lanes",
        lambda inputs: [
            fake_lane(tmp_path, "qbox-full-check-only", check_mode),
            fake_lane(tmp_path, "qbox-full-live-cl0-cl1", "pass"),
        ],
    )


def test_qbox_lanes_are_planned() -> None:
    # Given: the default Apollo validation dry-run output directory.
    out_dir = Path("build/tests/task-8-pytest-dry")

    # When: dry-run mode plans extra QBox lanes.
    result = run_runner("--dry-run", "--stamp", "task-8-pytest-dry", "--out-dir", str(out_dir))

    # Then: QBox static, CTest, and runtime command records are present.
    assert result.returncode == 0, result.stderr
    commands = command_texts(ROOT / out_dir)
    assert any("validate_qbox_apollo_fvp_full_map.py --out" in command for command in commands)
    assert any("audit_qbox_core_boundary.py --json >" in command for command in commands)
    assert any("audit_qbox_apollo_ap_memory_map.py --check coverage --output" in command for command in commands)
    assert any("validate_qbox_apollo_fvp_boot_sequence.py --static-only --output" in command for command in commands)
    assert any("ctest --test-dir build/local-apollo-fvp/work/qbox-platform -N" in command for command in commands)
    assert any("ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R" in command for command in commands)
    assert any("run_qbox_apollo_fvp_full.py --check-only --si-mode live-cl0-cl1" in command for command in commands)
    assert any("run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl0-cl1" in command for command in commands)


def test_timeout_fvp_updates_planned_qbox_live_command() -> None:
    # Given: a dry-run with a non-default FVP timeout.
    out_dir = Path("build/tests/task-8-pytest-timeout-fvp")

    # When: dry-run mode plans extra QBox lanes.
    result = run_runner(
        "--dry-run",
        "--timeout-fvp",
        "321",
        "--stamp",
        "task-8-pytest-timeout-fvp",
        "--out-dir",
        str(out_dir),
    )

    # Then: the live QBox runtime record carries the selected timeout.
    assert result.returncode == 0, result.stderr
    commands = load_commands(ROOT / out_dir)
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert "--timeout 321" in " ".join(live["argv"])


def test_include_qbox_runtime_missing_build_blocks() -> None:
    # Given: an explicit QBox runtime request with the QBox build directory forced missing.
    out_dir = Path("build/tests/task-8-pytest-missing-qbox")
    missing_qbox_build = ROOT / "build/tests/task-8-fixture/missing-qbox-platform"

    # When: dry-run mode evaluates the QBox runtime prerequisite.
    result = run_runner(
        "--dry-run",
        "--include-qbox-runtime",
        "--stamp",
        "task-8-pytest-missing-qbox",
        "--out-dir",
        str(out_dir),
        extra_env={"RUN_TEST_QBOX_BUILD_DIR": str(missing_qbox_build)},
    )

    # Then: explicit runtime is BLOCKED with the QBox missing-build reason.
    assert result.returncode == 2
    summary = load_json(ROOT / out_dir / "summary.json")
    assert summary["status"] == "BLOCKED"
    assert any(
        blocker["reason"] == "blocked_missing_qbox_build"
        for blocker in summary["blockers"]
    )


def test_live_runtime_is_blocked_when_check_only_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build directory exists but check-only reports a runtime prerequisite blocker.
    patch_qbox_lanes(monkeypatch, tmp_path, "blocked")

    # When: QBox runtime lanes execute through the non-dry-run lane runner.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path))

    # Then: live runtime is not launched and the run is BLOCKED, not FAIL.
    assert rc == 2
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "blocked"
    assert check["blockers"] == [{"reason": "blocked_missing_runtime_artifact"}]
    assert "exit_code" not in check
    assert live["status"] == "blocked"
    assert live["reason"] == "blocked_qbox_check_only_preflight"
    summary, exit_code = summarize_run(tmp_path / "run")
    assert summary["status"] == "BLOCKED"
    assert exit_code == 2


def test_live_runtime_is_skipped_when_check_only_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build directory exists but check-only fails without a blocker.
    patch_qbox_lanes(monkeypatch, tmp_path, "fail")

    # When: QBox runtime lanes execute through the non-dry-run lane runner.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path))

    # Then: live runtime is not launched and the run remains a normal FAIL.
    assert rc == 1
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "fail"
    assert check["exit_code"] == 1
    assert live["status"] == "skipped"
    assert live["reason"] == "skipped_failed_qbox_check_only"
    summary, exit_code = summarize_run(tmp_path / "run")
    assert summary["status"] == "FAIL"
    assert exit_code == 1


def test_live_runtime_runs_by_default_when_build_exists_and_check_only_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build exists and check-only passes without an explicit runtime request.
    patch_qbox_lanes(monkeypatch, tmp_path, "pass")

    # When: QBox lanes execute in the default mode.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path, include_runtime=False))

    # Then: the live runtime process is launched by default.
    assert rc == 0
    assert (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert live["status"] == "pass"
    assert live["exit_code"] == 0


def test_live_runtime_is_skipped_when_runtime_is_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build exists and runtime lanes are otherwise runnable.
    patch_qbox_lanes(monkeypatch, tmp_path, "pass")

    # When: QBox lanes execute with the public skip-runtime policy.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path, skip_runtime=True))

    # Then: neither check-only nor live runtime is launched.
    assert rc == 0
    assert not (tmp_path / "qbox-full-check-only-ran.txt").exists()
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "skipped"
    assert check["reason"] == "skipped_runtime_requested"
    assert live["status"] == "skipped"
    assert live["reason"] == "skipped_runtime_requested"

from __future__ import annotations

from collections.abc import Iterator
import os
import signal
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from run_test_helpers import (
    ROOT,
    command_texts,
    latest_target,
    load_commands,
    load_json,
    nonempty_lines,
    preserve_latest_link,
    run_runner,
    write_fake_pytest,
    write_fake_python,
)


@pytest.fixture(autouse=True)
def restore_latest_link() -> Iterator[None]:
    with preserve_latest_link():
        yield


def test_help_documents_runner_options() -> None:
    # Given: the root validation runner CLI.
    # When: help is requested.
    result = run_runner("--help")

    # Then: it documents the runner defaults, outputs, exclusions, results, and unblock steps.
    assert result.returncode == 0, result.stderr
    for option in (
        "--build-dir",
        "--machine",
        "--image",
        "--out-dir",
        "--stamp",
        "--list",
        "--dry-run",
        "--preflight-only",
        "--skip-runtime",
        "--include-qbox-runtime",
        "--timeout-oeqa",
        "--timeout-fvp",
        "--help",
    ):
        assert option in result.stdout
    for required_text in (
        "build/tests",
        "Xen",
        "PASS",
        "FAIL",
        "BLOCKED",
        "0",
        "1",
        "2",
        "64",
        "70",
        "FVP executable",
        "Crypto",
        "port",
    ):
        assert required_text in result.stdout


def test_list_prints_pass_and_summary_as_final_lines() -> None:
    # Given: an explicit list-mode output directory under build/tests.
    out_dir = Path("build/tests/task-5-pytest-list")

    # When: list mode resolves the current Apollo validation manifest.
    result = run_runner("--list", "--stamp", "task-5-pytest-list", "--out-dir", str(out_dir))

    # Then: it exits PASS and the final two non-empty lines are machine-readable.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert lines[-2:] == [
        "RESULT: PASS",
        "SUMMARY: build/tests/task-5-pytest-list/summary.json",
    ]
    assert load_json(ROOT / out_dir / "summary.json")["status"] == "PASS"


def test_dry_run_records_oeqa_bitbake_commands() -> None:
    # Given: an explicit dry-run output directory under build/tests.
    out_dir = Path("build/tests/task-5-pytest-dry")

    # When: dry-run mode plans the wrapper records.
    result = run_runner("--dry-run", "--stamp", "task-5-pytest-dry", "--out-dir", str(out_dir))

    # Then: it writes artifacts and records both OEQA BitBake lanes.
    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    for name in ("manifest.json", "excluded.json", "commands.jsonl", "summary.json"):
        assert (run_dir / name).is_file()
    commands = load_commands(run_dir)
    assert commands
    command_text = "\n".join(" ".join(command.get("argv", [])) for command in commands)
    assert "bitbake -R " in command_text
    assert "oeqa-current.conf nexios-image -c testimage" in command_text
    assert "oeqa-extended.conf nexios-image -c testimage" in command_text


def test_dry_run_rejects_project_root_out_dir_before_writing_artifacts() -> None:
    # Given: the public runner is pointed at the project root as its output directory.
    root_artifacts = [
        ROOT / name
        for name in ("commands.jsonl", "manifest.json", "plan.json", "excluded.json", "summary.json", "conf")
    ]
    latest_before = latest_target()

    # When: dry-run mode is requested.
    result = run_runner("--out-dir", ".", "--dry-run")

    # Then: it fails as a CLI usage error before root artifacts or latest are changed.
    assert result.returncode == 64
    assert "project root" in result.stderr
    assert all(not path.exists() for path in root_artifacts)
    assert latest_target() == latest_before


def test_dry_run_rejects_build_conf_out_dir_before_writing_artifacts() -> None:
    # Given: the public runner is pointed under protected build/conf.
    out_dir = ROOT / "build/conf/task-f2-pytest"

    # When: dry-run mode is requested.
    result = run_runner("--out-dir", "build/conf/task-f2-pytest", "--dry-run")

    # Then: it fails as a CLI usage error without creating anything under build/conf.
    assert result.returncode == 64
    assert "protected" in result.stderr
    assert not out_dir.exists()


def test_dry_run_rejects_public_out_dirs_outside_build_tests_before_writing_artifacts() -> None:
    # Given: public runner output paths outside build/tests.
    cases = (
        ("build/not-tests/bad", ROOT / "build/not-tests/bad"),
        ("/tmp/aas-outside-build-tests", Path("/tmp/aas-outside-build-tests")),
        (".omo/evidence/bad", ROOT / ".omo/evidence/bad"),
    )
    latest_before = latest_target()

    for out_arg, artifact_dir in cases:
        # When: dry-run mode is requested for a forbidden public path.
        result = run_runner("--out-dir", out_arg, "--dry-run")

        # Then: it fails before creating artifacts or mutating latest.
        assert result.returncode == 64
        assert "outside" in result.stderr
        assert not artifact_dir.exists()
        assert latest_target() == latest_before


def test_dry_run_rejects_active_build_conf_build_dir_before_writing_artifacts() -> None:
    # Given: the selected build directory is the protected active build/conf tree.
    out_dir = ROOT / "build/conf/tests/task-f2-pytest"
    latest = ROOT / "build/conf/tests/latest"

    # When: dry-run mode would otherwise derive build/conf/tests.
    result = run_runner("--build-dir", "build/conf", "--dry-run", "--stamp", "task-f2-pytest")

    # Then: it fails before creating artifacts or a protected latest link.
    assert result.returncode == 64
    assert "protected build directory" in result.stderr
    assert not out_dir.exists()
    assert not latest.exists()


def test_dry_run_accepts_public_out_dir_under_build_tests() -> None:
    # Given: an explicit public runner output path under build/tests.
    out_dir = Path("build/tests/ok")

    # When: dry-run mode is requested.
    result = run_runner("--out-dir", str(out_dir), "--dry-run")

    # Then: it succeeds and writes the standard public artifacts there.
    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    assert (run_dir / "commands.jsonl").is_file()
    assert (run_dir / "summary.json").is_file()


def test_latest_snapshot_helper_restores_after_runner_invocation() -> None:
    # Given: the runner normally updates build/tests/latest for public runs.
    latest_before = latest_target()

    # When: a real runner invocation is wrapped by the test snapshot helper.
    with preserve_latest_link():
        result = run_runner(
            "--list",
            "--stamp",
            "task-5-pytest-latest-helper",
            "--out-dir",
            "build/tests/task-5-pytest-latest-helper",
        )
        assert result.returncode == 0, result.stderr
        assert latest_target() == "task-5-pytest-latest-helper"

    # Then: the helper restores the public latest pointer for the caller.
    assert latest_target() == latest_before


def test_extra_static_lanes_are_planned() -> None:
    # Given: an explicit Todo 7 dry-run output directory.
    out_dir = Path("build/tests/task-7-pytest-dry")

    # When: dry-run mode plans the enabled extra static/project lanes.
    result = run_runner("--dry-run", "--stamp", "task-7-pytest-dry", "--out-dir", str(out_dir))

    # Then: all required extra commands are recorded but not executed.
    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    commands = command_texts(run_dir)
    assert any(
        "PYTHONPYCACHEPREFIX=build/tests/task-7-pytest-dry/extra/static/pycache "
        "python3 -m compileall scripts tests sw-ref-stack/test_automation" in command
        for command in commands
    )
    assert any(
        "pytest tests -o cache_dir=build/tests/task-7-pytest-dry/extra/project-pytest/cache "
        "--junitxml build/tests/task-7-pytest-dry/extra/project-pytest/junit.xml" in command
        for command in commands
    )
    assert not any("pytest unittests" in command for command in commands)
    extra_records = [command for command in load_commands(run_dir) if command["name"].startswith("extra-")]
    assert extra_records
    assert all("stdout_log" not in command and "stderr_log" not in command for command in extra_records)


def test_extra_lane_failure_makes_summary_fail(tmp_path: Path) -> None:
    # Given: a fake python3 that fails only the compileall lane.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    write_fake_python(fake_bin / "python3")
    write_fake_pytest(fake_bin / "pytest")
    out_dir = Path("build/tests/task-7-pytest-fail")

    # When: normal mode runs extra lanes and skips not-yet-implemented runtime lanes.
    result = run_runner(
        "--skip-runtime",
        "--stamp",
        "task-7-pytest-fail",
        "--out-dir",
        str(out_dir),
        extra_env={
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "REAL_PYTHON": sys.executable,
        },
    )

    # Then: the failing extra lane makes the overall summary FAIL.
    assert result.returncode == 1
    run_dir = ROOT / out_dir
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "FAIL"
    static_step = next(step for step in summary["steps"] if step["name"] == "extra-static-compileall")
    assert static_step["exit_code"] == 9
    assert (run_dir / "extra/static/stderr.log").read_text(encoding="utf-8").strip() == (
        "fake compileall failure"
    )


def test_stale_pass_summary_is_not_reused_when_command_record_init_fails() -> None:
    # Given: a stale PASS summary and a non-regular commands.jsonl path.
    run_dir = ROOT / "build/tests/task-5-pytest-stale"
    shutil.rmtree(run_dir, ignore_errors=True)
    run_dir.mkdir(parents=True)
    (run_dir / "commands.jsonl").mkdir()
    (run_dir / "summary.json").write_text(
        '{"exit_code": 0, "status": "PASS"}\n',
        encoding="utf-8",
    )

    # When: dry-run mode attempts to initialize command recording.
    result = run_runner(
        "--dry-run",
        "--stamp",
        "task-5-pytest-stale",
        "--out-dir",
        "build/tests/task-5-pytest-stale",
    )

    # Then: the final result is an internal BLOCKED error, not the stale PASS.
    assert result.returncode != 0
    assert "RESULT: PASS" not in result.stdout
    lines = nonempty_lines(result.stdout)
    assert lines[-2:] == [
        "RESULT: BLOCKED",
        "SUMMARY: build/tests/task-5-pytest-stale/summary.json",
    ]
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "BLOCKED"
    assert summary["blockers"][0]["reason"] == "blocked_command_record_init_failed"


def test_lock_held_blocks_with_exit_2() -> None:
    # Given: another process holds the fixed FVP/OEQA lock.
    tests_dir = ROOT / "build/tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    lock_path = tests_dir / ".run_test.lock"
    holder = subprocess.Popen(
        ["bash", "-c", f"exec 9>{lock_path}; flock 9; sleep 30"],
        cwd=ROOT,
        start_new_session=True,
    )
    try:
        # When: preflight-only mode attempts to enter the serialized section.
        result = run_runner(
            "--preflight-only",
            "--stamp",
            "task-5-pytest-lock",
            "--out-dir",
            "build/tests/task-5-pytest-lock",
        )
    finally:
        os.killpg(holder.pid, signal.SIGTERM)
        holder.wait(timeout=5)

    # Then: the runner reports BLOCKED and exits with the blocked code.
    assert result.returncode == 2
    lines = nonempty_lines(result.stdout)
    assert lines[-2:] == [
        "RESULT: BLOCKED",
        "SUMMARY: build/tests/task-5-pytest-lock/summary.json",
    ]
    summary = load_json(ROOT / "build/tests/task-5-pytest-lock/summary.json")
    assert summary["status"] == "BLOCKED"
    assert summary["blockers"][0]["reason"] == "blocked_lock_held"

from __future__ import annotations

import os
import signal
import shutil
import subprocess
from pathlib import Path

from run_test_helpers import (
    LATEST,
    ROOT,
    latest_target,
    load_commands,
    load_json,
    nonempty_lines,
    preserve_latest_link,
    run_runner,
)


LATEST_BEFORE = latest_target()


def teardown_module() -> None:
    if LATEST.is_symlink() or LATEST.is_file():
        LATEST.unlink()
    elif LATEST.exists():
        shutil.rmtree(LATEST)
    if LATEST_BEFORE is not None:
        LATEST.parent.mkdir(parents=True, exist_ok=True)
        LATEST.symlink_to(LATEST_BEFORE)


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
        "--category",
        "--test",
        "--tui",
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
        "headless",
        "dependency",
        "F12",
    ):
        assert required_text in result.stdout


def test_default_mode_is_headless() -> None:
    # Given: no interactive display option is requested.
    out_dir = Path("build/tests/ulw-pytest-headless")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: a category that completes without launching FVP is run.
    result = run_runner(
        "--category",
        "extended",
        "--stamp",
        "ulw-pytest-headless",
        "--out-dir",
        str(out_dir),
    )

    # Then: the direct runner identifies headless mode and returns its result.
    assert result.returncode == 0, result.stderr
    assert "[run_test]   mode: headless" in nonempty_lines(result.stdout)
    assert load_json(ROOT / out_dir / "summary.json")["status"] == "PASS"


def test_list_prints_pass_and_summary_as_final_lines() -> None:
    # Given: an explicit full-list-mode output directory under build/tests.
    out_dir = Path("build/tests/task-5-pytest-list")

    # When: list mode resolves the current Apollo validation manifest without a category filter.
    result = run_runner("--list", "--stamp", "task-5-pytest-list", "--out-dir", str(out_dir))

    # Then: it exits PASS, prints every category, and ends with machine-readable result lines.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    for category in ("basic:", "functional:", "power:", "extended:", "stress:"):
        assert category in lines
    assert "[run_test] START category-all-list" in lines
    assert "[run_test] DONE category-all-list (pass)" in lines
    assert lines[-2:] == [
        "RESULT: PASS",
        "SUMMARY: build/tests/task-5-pytest-list/summary.json",
    ]
    suite = load_json(ROOT / out_dir / "suite.json")
    assert set(suite["categories"]) == {"basic", "functional", "power", "extended", "stress"}
    assert load_json(ROOT / out_dir / "summary.json")["status"] == "PASS"
    command_names = {record["name"] for record in load_commands(ROOT / out_dir)}
    assert "category-all-list" in command_names


def test_list_category_filters_to_named_category() -> None:
    # Given: an explicit category-filtered list-mode output directory under build/tests.
    out_dir = Path("build/tests/task-list-category-extended")

    # When: list mode is requested with a category filter.
    result = run_runner(
        "--list",
        "--category",
        "extended",
        "--stamp",
        "task-list-category-extended",
        "--out-dir",
        str(out_dir),
    )

    # Then: it lists only the selected category.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "extended:" in lines
    assert "basic:" not in lines
    assert "functional:" not in lines
    assert "stress:" not in lines
    assert "[run_test] START category-extended-list" in lines
    assert "[run_test] DONE category-extended-list (pass)" in lines
    suite = load_json(ROOT / out_dir / "suite.json")
    assert set(suite["categories"]) == {"extended"}
    command_names = {record["name"] for record in load_commands(ROOT / out_dir)}
    assert "category-extended-list" in command_names


def test_category_option_runs_named_category_with_progress() -> None:
    # Given: an explicit category run that does not need to launch FVP.
    out_dir = Path("build/tests/task-category-extended")

    # When: the root runner is asked to run only the extended category.
    result = run_runner(
        "--category",
        "extended",
        "--stamp",
        "task-category-extended",
        "--out-dir",
        str(out_dir),
    )

    # Then: stdout reports the selected category and per-test progress.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "[run_test]   category: extended" in lines
    assert "[run_test] START category-extended" in lines
    assert "[run_test] START extended-list" in lines
    assert "[run_test] DONE extended-list (pass)" in lines
    assert "[run_test] DONE category-extended (pass)" in lines
    assert lines[-2:] == [
        "RESULT: PASS",
        "SUMMARY: build/tests/task-category-extended/summary.json",
    ]
    summary = load_json(ROOT / out_dir / "summary.json")
    assert summary["status"] == "PASS"
    command_names = {record["name"] for record in load_commands(ROOT / out_dir)}
    assert "extended-list" in command_names


def test_dry_run_records_oeqa_bitbake_commands() -> None:
    # Given: an explicit basic-category dry-run output directory under build/tests.
    out_dir = Path("build/tests/task-5-pytest-dry")

    # When: dry-run mode plans the basic boot lane.
    result = run_runner("--dry-run", "--stamp", "task-5-pytest-dry", "--out-dir", str(out_dir))

    # Then: it writes artifacts and records preflight plus skipped boot.
    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    for name in ("manifest.json", "commands.jsonl", "summary.json"):
        assert (run_dir / name).is_file()
    command_names = {command["name"] for command in load_commands(run_dir)}
    assert {"context", "runtime-preflight", "basic-boot"}.issubset(command_names)


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


def test_basic_dry_run_records_skipped_boot_lane() -> None:
    # Given: an explicit basic category dry-run output directory.
    out_dir = Path("build/tests/task-7-pytest-dry")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: dry-run mode plans the selected category.
    result = run_runner("--dry-run", "--stamp", "task-7-pytest-dry", "--out-dir", str(out_dir))

    # Then: the boot lane is recorded but not executed.
    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    boot_record = next(command for command in load_commands(run_dir) if command["name"] == "basic-boot")
    assert boot_record["status"] == "skipped"
    assert "planned_command" in str(boot_record["artifacts"])
    assert "--min-runtime" in boot_record["argv"]
    assert "70" in boot_record["argv"]
    assert "--no-login" not in boot_record["argv"]
    assert ["--post-login-command", "true"] == boot_record["argv"][-2:]


def test_qvp_basic_boot_uses_headless_fvp_runtime() -> None:
    out_dir = Path("build/tests/task-qvp-basic-dry-run")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = run_runner(
        "--machine",
        "apollo-qvp",
        "--category",
        "basic",
        "--dry-run",
        "--stamp",
        "task-qvp-basic-dry-run",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    boot_record = next(
        command
        for command in load_commands(ROOT / out_dir)
        if command["name"] == "basic-boot"
    )
    assert boot_record["argv"][:2] == ["python3", "scripts/run/runfvp_log_boot.py"]
    assert ["--machine", "apollo-qvp"] == boot_record["argv"][2:4]
    assert "--min-runtime" in boot_record["argv"]
    assert str(ROOT / out_dir / "fvp") in boot_record["argv"]


def test_functional_dry_run_records_boot_and_oeqa_lanes() -> None:
    # Given: a functional category dry-run output directory.
    out_dir = Path("build/tests/task-functional-dry-run")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: the functional category is requested in dry-run mode.
    result = run_runner(
        "--category",
        "functional",
        "--dry-run",
        "--stamp",
        "task-functional-dry-run",
        "--out-dir",
        str(out_dir),
    )

    # Then: it plans preflight plus one OEQA-owned FVP session, without a separate boot.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "[run_test] START category-functional" in lines
    assert "[run_test] START runtime-preflight" in lines
    assert "[run_test] SKIP basic-boot (dry-run)" not in lines
    assert "[run_test] START oeqa-lanes" in lines
    assert "[run_test] SKIP oeqa-functional (dry-run)" in lines
    assert "[run_test] DONE category-functional (pass)" in lines
    run_dir = ROOT / out_dir
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "PASS"
    command_names = {command["name"] for command in load_commands(run_dir)}
    assert {"runtime-preflight", "oeqa-functional"}.issubset(command_names)
    assert "basic-boot" not in command_names


def test_power_dry_run_records_power_oeqa_lane() -> None:
    # Given: a power category dry-run output directory.
    out_dir = Path("build/tests/task-power-dry-run")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: the power category is requested in dry-run mode.
    result = run_runner(
        "--category",
        "power",
        "--dry-run",
        "--stamp",
        "task-power-dry-run",
        "--out-dir",
        str(out_dir),
    )

    # Then: the runner records preflight and the skipped power OEQA lane.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "[run_test] START category-power" in lines
    assert "[run_test] START runtime-preflight" in lines
    assert "[run_test] START oeqa-lanes" in lines
    assert "[run_test] SKIP oeqa-power (dry-run)" in lines
    assert "[run_test] DONE category-power (pass)" in lines
    run_dir = ROOT / out_dir
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "PASS"
    command_names = {command["name"] for command in load_commands(run_dir)}
    assert {"runtime-preflight", "oeqa-power"}.issubset(command_names)


def test_power_preflight_only_stops_before_oeqa() -> None:
    # Given: a power category preflight-only output directory.
    out_dir = Path("build/tests/task-power-preflight-only")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: preflight-only is requested for the power category.
    result = run_runner(
        "--category",
        "power",
        "--preflight-only",
        "--stamp",
        "task-power-preflight-only",
        "--out-dir",
        str(out_dir),
    )

    # Then: the runner stops after preflight and does not plan the power OEQA lane.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "[run_test] START category-power" in lines
    assert "[run_test] START runtime-preflight" in lines
    assert "[run_test] START oeqa-lanes" not in lines
    run_dir = ROOT / out_dir
    command_names = {command["name"] for command in load_commands(run_dir)}
    assert "runtime-preflight" in command_names
    assert "oeqa-power" not in command_names


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

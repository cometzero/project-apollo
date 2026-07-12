from __future__ import annotations

from pathlib import Path
import re

from run_test_helpers import nonempty_lines, run_runner


def test_preflight_prints_environment_and_step_progress() -> None:
    # Given: a preflight-only Apollo FVP validation run.
    out_dir = Path("build/tests/task-progress-preflight")

    # When: the wrapper checks runtime prerequisites.
    result = run_runner(
        "--preflight-only",
        "--stamp",
        "task-progress-preflight",
        "--out-dir",
        str(out_dir),
    )

    # Then: stdout exposes the environment and step progress before the result.
    assert result.returncode == 0, result.stderr
    lines = nonempty_lines(result.stdout)
    assert "[run_test] Environment" in lines
    assert "[run_test]   machine: apollo-fvp" in lines
    assert "[run_test]   category: basic" in lines
    assert "[run_test] START context" in lines
    assert "[run_test] DONE context (pass)" in lines
    assert "[run_test] START runtime-preflight" in lines
    assert "[run_test] DONE runtime-preflight (pass)" in lines
    assert lines[-2:] == [
        "RESULT: PASS",
        "SUMMARY: build/tests/task-progress-preflight/summary.json",
    ]

    run_test_lines = [
        line for line in result.stdout.splitlines() if "[run_test]" in line
    ]
    assert run_test_lines
    timestamp = re.compile(
        r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z\] \[run_test\]"
    )
    assert all(timestamp.match(line) for line in run_test_lines)

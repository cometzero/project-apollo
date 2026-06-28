from __future__ import annotations

from pathlib import Path

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
    assert "[run_test] START manifest" in lines
    assert "[run_test] DONE manifest (pass)" in lines
    assert "[run_test] START preflight" in lines
    assert "[run_test] DONE preflight (pass)" in lines
    assert lines[-2:] == [
        "RESULT: PASS",
        "SUMMARY: build/tests/task-progress-preflight/summary.json",
    ]

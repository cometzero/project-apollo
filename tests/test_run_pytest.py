from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from scripts.test.run_pytest import write_report


ROOT = Path(__file__).resolve().parents[1]


def prepare_isolated(tmp_path: Path, source: str) -> tuple[Path, dict[str, str]]:
    runner = tmp_path / "scripts/test/run_pytest.py"
    runner.parent.mkdir(parents=True)
    runner.write_bytes((ROOT / "scripts/test/run_pytest.py").read_bytes())
    (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text(source, encoding="utf-8")
    env = os.environ.copy()
    env.pop("PYTEST_ADDOPTS", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return runner, env


def run_isolated(tmp_path: Path, source: str) -> tuple[subprocess.CompletedProcess[str], Path]:
    runner, env = prepare_isolated(tmp_path, source)
    result = subprocess.run(
        [sys.executable, str(runner), "-q"], cwd=tmp_path, env=env,
        text=True, capture_output=True, timeout=30, check=False,
    )
    reports = list((tmp_path / "build/qbox-apollo-qvp").glob("pytest-*/report.md"))
    assert len(reports) == 1, result.stdout + result.stderr
    return result, reports[0]


@pytest.mark.parametrize("failure", [False, True])
def test_runner_retains_report_counts_output_and_exit_code(tmp_path: Path, failure: bool) -> None:
    result, report = run_isolated(tmp_path, f"""
import pytest

def test_pass():
    assert True

def test_skip():
    pytest.skip("missing optional hardware")

def test_result():
    assert {not failure}, "regression detected"
""")
    assert result.returncode == int(failure)
    text = report.read_text()
    assert f"**Status: {'FAIL' if failure else 'PASS'}**" in text
    assert "| Total | 3 |" in text
    assert f"| Passed | {1 if failure else 2} |" in text
    assert f"| Failed | {int(failure)} |" in text
    assert "| Skipped | 1 |" in text
    assert "missing optional hardware" in text
    assert "test_example" in text
    assert "--junitxml=" in text
    assert "does not establish QBox/FVP boot" in text
    log = (report.parent / "console.log").read_text()
    assert "1 skipped" in log
    assert log in result.stdout
    assert (report.parent / "junit.xml").is_file()


@pytest.mark.parametrize(
    ("source", "exit_code", "status", "detail"),
    [
        ('raise RuntimeError("collection failed")\n', 2, "FAIL", "collection failed"),
        ("# No tests here\n", 5, "FAIL", "| Total | 0 |"),
        ('import pytest\ndef test_skip(): pytest.skip("unavailable")\n', 0, "NO PASSING TESTS", "unavailable"),
    ],
)
def test_runner_never_claims_pass_without_successful_tests(
    tmp_path: Path, source: str, exit_code: int, status: str, detail: str
) -> None:
    result, report = run_isolated(tmp_path, source)
    assert result.returncode == exit_code
    text = report.read_text()
    assert f"**Status: {status}**" in text
    assert "| Passed | 0 |" in text
    assert detail in text


@pytest.mark.parametrize("xml", [None, "<not-xml", "<unrelated />", "<testsuites />"])
def test_report_never_claims_pass_without_junit_case_results(tmp_path: Path, xml: str | None) -> None:
    if xml is not None:
        (tmp_path / "junit.xml").write_text(xml, encoding="utf-8")
    write_report(tmp_path, ["python", "-m", "pytest"], "start", "finish", 0)
    assert "**Status: PASS**" not in (tmp_path / "report.md").read_text()


def test_report_records_python_and_only_the_named_opt_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APOLLO_RUN_BITBAKE_MATRIX_TESTS", "1")
    monkeypatch.setenv("APOLLO_UNRELATED_SECRET", "must-not-appear")
    write_report(tmp_path, ["python", "-m", "pytest"], "start", "finish", 5)
    report = (tmp_path / "report.md").read_text()
    assert f"Python version: `{sys.version.split()[0]}`" in report
    assert "`APOLLO_RUN_BITBAKE_MATRIX_TESTS`: `1`" in report
    assert "APOLLO_UNRELATED_SECRET" not in report
    assert "must-not-appear" not in report


@pytest.mark.parametrize("ignore_sigint", [False, True])
def test_interrupt_reports_exit_130_and_reaps_pytest(tmp_path: Path, ignore_sigint: bool) -> None:
    runner, env = prepare_isolated(tmp_path, f"""
import os
from pathlib import Path
import signal
import time
import pytest

@pytest.fixture
def sleeper():
    if {ignore_sigint}:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    Path("pytest-child.pid").write_text(str(os.getpid()))
    time.sleep(60)
    yield

def test_sleep(sleeper):
    pass
""")
    process = subprocess.Popen(
        [sys.executable, str(runner), "-q"], cwd=tmp_path, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        start_new_session=True,
    )
    child_pid = None
    try:
        pid_file = tmp_path / "pytest-child.pid"
        deadline = time.monotonic() + 10
        while not pid_file.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert pid_file.exists(), "sleep fixture did not start"
        child_pid = int(pid_file.read_text())
        process.send_signal(signal.SIGINT)
        output, _ = process.communicate(timeout=15)
        assert process.returncode == 130, output
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)
        reports = list((tmp_path / "build/qbox-apollo-qvp").glob("pytest-*/report.md"))
        assert len(reports) == 1, output
        report = reports[0]
        text = report.read_text()
        assert "**Status: INTERRUPTED**" in text
        assert "Exit code: `130`" in text
        assert "| Passed | 0 |" in text
        assert "interrupted" in (report.parent / "console.log").read_text()
        if not ignore_sigint:
            assert (report.parent / "junit.xml").is_file()
    finally:
        if child_pid is not None:
            try:
                os.killpg(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)

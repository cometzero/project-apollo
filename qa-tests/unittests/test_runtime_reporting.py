from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest


QA_ROOT = Path(__file__).resolve().parents[1]


def _project(tmp_path: Path, sources: dict[str, str]) -> tuple[Path, dict[str, str]]:
    package = tmp_path / "test_automation"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "reporting.py").write_bytes((QA_ROOT / "test_automation/reporting.py").read_bytes())
    (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests\npythonpath = .\n")
    (tmp_path / "conftest.py").write_text('''
from pathlib import Path
import pytest
from test_automation import reporting

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config._apollo_run_dir = Path(__file__).parent / "report"
    config._apollo_run_dir.mkdir()
    target = config._apollo_run_dir / "target" / "uart"
    target.mkdir(parents=True)
    (target / "ap <uart>.log").write_text("UART log")
    (config._apollo_run_dir / "platform.json").write_text('{}')
    (config._apollo_run_dir / "invocation.json").write_text('{}')
    if not config.option.xmlpath:
        config.option.xmlpath = str(config._apollo_run_dir / "junit.xml")
    reporting.configure(config)
''')
    for relative, source in sources.items():
        path = tmp_path / "tests" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
    env = os.environ.copy()
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTHONPATH", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return tmp_path, env


def _run(tmp_path: Path, sources: dict[str, str], *args: str) -> tuple[subprocess.CompletedProcess, dict]:
    directory, env = _project(tmp_path, sources)
    process = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *args], cwd=directory,
        env=env, text=True, capture_output=True, timeout=30, check=False,
    )
    report = directory / "report/results.json"
    assert report.is_file(), process.stdout + process.stderr
    return process, json.loads(report.read_text())


def test_report_groups_real_results_and_preserves_failure_phases(tmp_path: Path) -> None:
    source = '''
import logging
import time
import pytest

def test_pass():
    time.sleep(0.02)

def test_fail():
    print("UART <script>alert(1)</script>")
    logging.warning("UART failure context")
    assert False, "bad <script>result</script>"

@pytest.fixture
def broken_setup():
    raise ValueError("setup failed")

def test_setup_error(broken_setup):
    pass

@pytest.fixture
def broken_teardown():
    yield
    raise ValueError("teardown failed")

def test_teardown_error(broken_teardown):
    pass

def test_skip():
    pytest.skip("unsupported target feature")

@pytest.mark.xfail(reason="known issue")
def test_xfail():
    assert False

@pytest.mark.xfail(reason="unexpected success")
def test_xpass():
    pass
'''
    process, report = _run(tmp_path, {
        "ap/boot/test_ap.py": source,
        "rse/boot/test_rse.py": "def test_rse(): pass\n",
        "si_cl0/diagnostics/test_scp.py": "def test_scp(): pass\n",
        "si_cl1/pfdi/test_cl1.py": "def test_cl1(): pass\n",
    })
    assert process.returncode == 1
    assert report["status"] == "ERROR"
    assert report["counts"] == {
        "selected": 10, "executed": 10, "not_run": 0, "passed": 5,
        "failed": 1, "skipped": 2, "errors": 2, "xfailed": 1,
        "xpassed": 1, "deselected": 0, "collection_errors": 0, "collection_skipped": 0,
    }
    cases = {case["nodeid"].split("::")[-1]: case for case in report["tests"]}
    teardown = cases["test_teardown_error"]
    assert teardown["status"] == "ERROR"
    assert teardown["phases"]["call"]["status"] == "PASS"
    assert teardown["phases"]["teardown"]["status"] == "ERROR"
    assert cases["test_pass"]["phases"]["call"]["duration_s"] >= 0.01
    for case in cases.values():
        assert case["duration_s"] == pytest.approx(sum(phase["duration_s"] for phase in case["phases"].values()))
    assert report["duration_s"] >= cases["test_pass"]["duration_s"]
    assert cases["test_xfail"]["expected_outcome"] == "xfail"
    assert cases["test_xpass"]["expected_outcome"] == "xpass"
    html = (tmp_path / "report/report.html").read_text()
    markdown = (tmp_path / "report/report.md").read_text()
    for domain in ("ap", "rse", "si_cl0", "si_cl1"):
        assert f'<h2 id="{domain}">' in html
        assert f"## {domain}\n" in markdown
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "UART failure context" in html
    assert "teardown failed" in html
    assert "target/uart/ap%20%3Cuart%3E.log" in html
    assert "Runtime report:" in process.stdout
    assert (tmp_path / "report/junit.xml").is_file()
    for name in ("platform.json", "invocation.json", "target/uart/ap <uart>.log"):
        assert name in report["artifacts"]
    assert 'href="platform.json"' in html
    assert 'href="invocation.json"' in html


def test_profile_properties_are_preserved_without_phase_double_counting(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/power/test_profiles.py": '''
import json
import pytest

@pytest.fixture
def cleanup_property(record_property):
    yield
    record_property("cleanup", 1.25)

def test_profile_pass(record_property, cleanup_property):
    record_property("validation_profile", "cpuidle")
    record_property("assertions", json.dumps([
        {"id": "idle-state", "status": "PASS"},
        {"id": "idle-governor", "status": "PASS"},
    ]))

def test_profile_fail(record_property):
    record_property("validation_profile", "pfdi")
    record_property("assertions", json.dumps([
        {"id": "pfdi-start", "status": "PASS"},
        {"id": "pfdi-monitor", "status": "FAIL"},
    ]))
    assert False, "monitor failure"
'''})
    assert process.returncode == 1
    assert report["assertion_counts"] == {"total": 4, "FAIL": 1, "PASS": 3}
    case = report["tests"][0]
    assert case["status"] == "PASS"
    assert case["validation_profile"] == "cpuidle"
    assert [entry["id"] for entry in case["assertions"]] == ["idle-state", "idle-governor"]
    assert dict(case["user_properties"])["cleanup"] == 1.25
    assert dict(case["user_properties"])["validation_profile"] == "cpuidle"
    assert case["assertion_error"] is None
    for name in ("report.html", "report.md"):
        text = (tmp_path / "report" / name).read_text()
        assert "cpuidle: total=2, PASS=2" in text
        assert "pfdi: total=2, FAIL=1, PASS=1" in text


def test_invalid_assertion_metadata_is_visible_and_not_counted(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/power/test_bad_metadata.py": '''
def test_bad_metadata(record_property):
    record_property("validation_profile", "broken <profile>")
    record_property("assertions", "{invalid json")
'''})
    assert process.returncode == 0
    case = report["tests"][0]
    assert case["assertion_error"]
    assert dict(case["user_properties"])["assertions"] == "{invalid json"
    assert report["assertion_counts"] == {"total": 0}
    assert report["assertion_metadata_errors"] == 1
    assert report["status"] == "ERROR"
    html = (tmp_path / "report/report.html").read_text()
    assert "broken &lt;profile&gt;: invalid assertion metadata" in html


def test_artifact_link_uses_the_configured_junit_destination(tmp_path: Path) -> None:
    junit_path = tmp_path / "custom.xml"
    process, report = _run(tmp_path, {"ap/boot/test_pass.py": "def test_pass(): pass\n"},
                           f"--junitxml={junit_path}")
    assert process.returncode == 0
    assert junit_path.is_file()
    assert "../custom.xml" in report["artifacts"]
    assert "junit.xml" not in report["artifacts"]


def test_collect_only_records_selection_without_executing_fixture(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/boot/test_collect.py": '''
from pathlib import Path
import pytest

@pytest.fixture
def boot():
    Path("booted").touch()

def test_boot(boot): pass
'''}, "--collect-only")
    assert process.returncode == 0
    assert report["status"] == "NO_EXECUTION"
    assert report["collect_only"] is True
    assert report["counts"]["selected"] == report["counts"]["not_run"] == 1
    assert report["counts"]["executed"] == 0
    assert not (tmp_path / "booted").exists()


def test_report_counts_deselection_separately_from_skip(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/boot/test_select.py":
        "def test_kept(): pass\ndef test_omitted(): pass\n"}, "-k", "kept")
    assert process.returncode == 0
    assert report["counts"]["selected"] == 1
    assert report["counts"]["deselected"] == 1
    assert report["counts"]["skipped"] == 0


def test_maxfail_keeps_unexecuted_selected_cases_visible(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/boot/test_stop.py":
        "def test_first(): assert False\ndef test_remaining(): pass\n"}, "--maxfail=1")
    assert process.returncode == 1
    assert report["status"] == "FAIL"
    assert report["counts"]["selected"] == 2
    assert report["counts"]["executed"] == report["counts"]["not_run"] == 1
    assert report["tests"][1]["status"] == "NOT_RUN"


def test_module_level_skip_cannot_claim_pass(tmp_path: Path) -> None:
    process, report = _run(tmp_path, {"ap/boot/test_skip_module.py":
        'import pytest\npytest.skip("optional module", allow_module_level=True)\n'})
    assert process.returncode == 5
    assert report["status"] == "NO_EXECUTION"
    assert report["counts"]["collection_skipped"] == 1
    assert report["counts"]["passed"] == 0


@pytest.mark.parametrize(
    ("path", "source", "exit_status"),
    [
        ("ap/boot/test_bad.py", 'print("collection UART context")\nraise RuntimeError("collection broke")\n', 2),
        ("unknown/boot/test_bad.py", "def test_bad(): pass\n", 4),
    ],
)
def test_collection_errors_are_reported(tmp_path: Path, path: str, source: str, exit_status: int) -> None:
    process, report = _run(tmp_path, {path: source})
    assert process.returncode == exit_status
    assert report["status"] == "ERROR"
    assert report["counts"]["collection_errors"] == 1
    assert report["counts"]["passed"] == 0
    assert report["collection_errors"][0]["longrepr"]
    if exit_status == 2:
        assert "collection UART context" in (tmp_path / "report/report.html").read_text()


@pytest.mark.parametrize("strict", [False, True])
def test_unexpected_pass_is_explicit(tmp_path: Path, strict: bool) -> None:
    process, report = _run(tmp_path, {"ap/boot/test_xpass.py": f'''
import pytest
@pytest.mark.xfail(strict={strict}, reason="known failure")
def test_unexpected(): pass
'''})
    assert process.returncode == int(strict)
    assert report["counts"]["xpassed"] == 1
    assert report["status"] == ("FAIL" if strict else "XPASS")


def test_keyboard_interrupt_retains_partial_report(tmp_path: Path) -> None:
    directory, env = _project(tmp_path, {"ap/boot/test_interrupt.py": '''
from pathlib import Path
import time
def test_interrupt():
    Path("started").touch()
    time.sleep(60)
'''})
    process = subprocess.Popen(
        [sys.executable, "-m", "pytest", "-q"], cwd=directory, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True,
    )
    try:
        deadline = time.monotonic() + 10
        while not (tmp_path / "started").exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert (tmp_path / "started").exists()
        process.send_signal(signal.SIGINT)
        output, _ = process.communicate(timeout=15)
        assert process.returncode == 2, output
        report = json.loads((tmp_path / "report/results.json").read_text())
        assert report["status"] == "INTERRUPTED"
        assert report["exit_status"] == 2
        assert report["counts"]["passed"] == 0
        assert report["counts"]["not_run"] == 1
        assert (tmp_path / "report/report.html").is_file()
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=5)

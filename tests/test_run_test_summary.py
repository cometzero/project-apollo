from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"


def run_manifest(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_command(run_dir: Path, record: dict) -> None:
    with (run_dir / "commands.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def make_summary_fixture(run_dir: Path) -> None:
    write_json(
        run_dir / "manifest.json",
        {
            "machine": "apollo-fvp",
            "distro": "auto-ad-nexios",
            "rd_aspen_variant": "cfg2",
            "pc_cpus_count_default": 16,
        },
    )
    write_json(
        run_dir / "plan.json",
        {
            "included": {
                "validation_current": ["ping"],
                "validation_extended": ["test_10_pfdi"],
                "extra": [],
            },
            "excluded": [
                {
                    "name": "test_40_virtualization",
                    "reason": "excluded_baremetal_no_xen",
                }
            ],
        },
    )


def run_summary(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return run_manifest(
        "summarize",
        "--run-dir",
        str(run_dir),
        "--out",
        str(run_dir / "summary.json"),
    )


def test_summary_pass_when_required_steps_pass_and_optional_step_is_skipped(
    tmp_path: Path,
) -> None:
    # Given: a synthetic run with one required pass and one optional skipped step.
    run_dir = tmp_path / "summary-pass"
    make_summary_fixture(run_dir)
    log_path = run_dir / "logs/static.stdout.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("ok\n", encoding="utf-8")
    append_command(
        run_dir,
        {
            "name": "static",
            "argv": ["python3", "-m", "py_compile"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "started_at": "2026-06-28T00:00:00Z",
            "finished_at": "2026-06-28T00:00:01Z",
            "duration_s": 1.0,
            "stdout_log": "logs/static.stdout.log",
        },
    )
    append_command(
        run_dir,
        {
            "name": "qbox-runtime",
            "argv": ["python3", "scripts/run/run_qbox_apollo_fvp_full.py"],
            "required": False,
            "status": "skipped",
            "reason": "skipped_optional_missing_qbox_build",
        },
    )

    # When: the summarize command aggregates the run.
    result = run_summary(run_dir)

    # Then: it writes a PASS summary and exits with the PASS code.
    assert result.returncode == 0, result.stderr
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "PASS"
    assert summary["exit_code"] == 0
    assert summary["active_config"]["machine"] == "apollo-fvp"
    assert summary["included"]["validation_current"] == ["ping"]
    assert summary["excluded"][0]["reason"] == "excluded_baremetal_no_xen"
    assert "commands.jsonl" in summary["run_note"]
    assert summary["blockers"] == []
    assert [step["status"] for step in summary["steps"]] == ["PASS", "SKIPPED"]


def test_summary_fail_when_oeqa_result_records_failure(tmp_path: Path) -> None:
    # Given: a command that exits zero but points at a failing OEQA JSON result.
    run_dir = tmp_path / "summary-fail"
    make_summary_fixture(run_dir)
    oeqa_path = run_dir / "oeqa/current/results.json"
    write_json(
        oeqa_path,
        {"tests": [{"name": "test_10_linuxboot", "status": "FAILED"}]},
    )
    append_command(
        run_dir,
        {
            "name": "oeqa-current",
            "argv": ["bitbake", "-c", "testimage"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "artifacts": [{"kind": "oeqa_result", "path": "oeqa/current/results.json"}],
        },
    )

    # When: the summarize command aggregates the run.
    result = run_summary(run_dir)

    # Then: the failed OEQA test makes the whole summary fail.
    assert result.returncode == 1
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "FAIL"
    assert summary["exit_code"] == 1
    assert summary["steps"][0]["status"] == "FAIL"
    assert summary["steps"][0]["oeqa_failed"] == ["test_10_linuxboot"]


def test_summary_blocks_when_oeqa_result_json_is_malformed(tmp_path: Path) -> None:
    # Given: a passing command record that points at malformed OEQA result evidence.
    run_dir = tmp_path / "summary-malformed-oeqa"
    make_summary_fixture(run_dir)
    oeqa_path = run_dir / "oeqa/current/results.json"
    oeqa_path.parent.mkdir(parents=True, exist_ok=True)
    oeqa_path.write_text("{not-json", encoding="utf-8")
    append_command(
        run_dir,
        {
            "name": "oeqa-current",
            "argv": ["bitbake", "-c", "testimage"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "artifacts": [{"kind": "oeqa_result", "path": "oeqa/current/results.json"}],
        },
    )

    # When: the summarize command aggregates the run.
    result = run_summary(run_dir)

    # Then: malformed evidence blocks the summary instead of producing PASS.
    assert result.returncode == 2
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "BLOCKED"
    assert summary["blockers"][0]["reason"] == "blocked_malformed_oeqa_result"
    assert summary["steps"][0]["status"] == "BLOCKED"


def assert_parseable_malformed_oeqa_summary_blocks(run_dir: Path, data: dict) -> None:
    make_summary_fixture(run_dir)
    oeqa_path = run_dir / "oeqa/current/results.json"
    write_json(oeqa_path, data)
    append_command(
        run_dir,
        {
            "name": "oeqa-current",
            "argv": ["bitbake", "-c", "testimage"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "artifacts": [{"kind": "oeqa_result", "path": "oeqa/current/results.json"}],
        },
    )

    result = run_summary(run_dir)

    assert result.returncode == 2
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "BLOCKED"
    assert summary["blockers"][0]["reason"] == "blocked_malformed_oeqa_result"
    assert summary["steps"][0]["status"] == "BLOCKED"


def test_summary_blocks_parseable_malformed_oeqa_json(tmp_path: Path) -> None:
    # Given/When/Then: parseable but empty OEQA result shapes cannot certify a passing run.
    for name, data in (("summary-empty-oeqa", {}), ("summary-empty-tests", {"tests": []})):
        assert_parseable_malformed_oeqa_summary_blocks(tmp_path / name, data)


def test_summary_keeps_run_dir_prefixed_artifact_paths_faithful() -> None:
    # Given: a relative build/tests run dir and a record with a run-dir-prefixed artifact path.
    run_dir = ROOT / "build/tests/task-11-summary-artifact-path"
    shutil.rmtree(run_dir, ignore_errors=True)
    make_summary_fixture(run_dir)
    append_command(
        run_dir,
        {
            "name": "manifest",
            "argv": ["python3", "scripts/test/run_test_manifest.py", "inspect"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "artifacts": [
                {
                    "kind": "json",
                    "path": "build/tests/task-11-summary-artifact-path/manifest.json",
                }
            ],
        },
    )

    # When: the summarize command aggregates artifact existence.
    result = run_summary(Path("build/tests/task-11-summary-artifact-path"))

    # Then: the summary does not duplicate the run dir prefix.
    assert result.returncode == 0, result.stderr
    summary = load_json(run_dir / "summary.json")
    assert summary["artifacts"] == [
        {
            "kind": "json",
            "path": "build/tests/task-11-summary-artifact-path/manifest.json",
            "exists": True,
        }
    ]


def test_summary_blocked_when_required_runtime_prerequisite_is_blocked(
    tmp_path: Path,
) -> None:
    # Given: a required runtime preflight step with an explicit blocker.
    run_dir = tmp_path / "summary-blocked"
    make_summary_fixture(run_dir)
    append_command(
        run_dir,
        {
            "name": "preflight",
            "argv": ["python3", "scripts/test/run_test_manifest.py", "preflight"],
            "required": True,
            "status": "blocked",
            "blockers": [
                {
                    "reason": "blocked_missing_fvp_executable",
                    "path": "/opt/FVP/FVP_Zena_CSS_Cfg2",
                }
            ],
        },
    )

    # When: the summarize command aggregates the run.
    result = run_summary(run_dir)

    # Then: the summary is BLOCKED and carries the blocker forward.
    assert result.returncode == 2
    summary = load_json(run_dir / "summary.json")
    assert summary["status"] == "BLOCKED"
    assert summary["exit_code"] == 2
    assert summary["blockers"][0]["reason"] == "blocked_missing_fvp_executable"


def test_summary_blocks_missing_required_command_log(tmp_path: Path) -> None:
    # Given: a required command record that references a missing stdout log.
    run_dir = tmp_path / "summary-missing-log"
    make_summary_fixture(run_dir)
    append_command(
        run_dir,
        {
            "name": "static",
            "argv": ["python3", "-m", "py_compile"],
            "required": True,
            "status": "pass",
            "exit_code": 0,
            "stdout_log": "logs/missing.stdout.log",
        },
    )

    # When: the summarize command aggregates the run.
    result = run_summary(run_dir)

    # Then: it does not allow the incomplete record to become PASS.
    assert result.returncode in {2, 70}
    if (run_dir / "summary.json").exists():
        assert load_json(run_dir / "summary.json")["status"] != "PASS"

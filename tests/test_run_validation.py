from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def _run_validation(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["./run_validation.sh", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_dry_run_rse_boot_writes_safe_oeqa_evidence() -> None:
    out_dir = Path("build/tests/validation-pytest-rse")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = _run_validation(
        "--machine",
        "apollo-qvp",
        "--test-suite",
        "boot",
        "--test-case",
        "rse-boot",
        "--dry-run",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    assert "RESULT: PASS" in result.stdout
    for name in ("runner.log", "commands.jsonl", "manifest.json", "summary.json", "summary.txt", "report.md"):
        assert (run_dir / name).is_file()
    conf = (run_dir / "conf/oeqa-selected.conf").read_text(encoding="utf-8")
    assert 'TEST_SUITES = "test_00_rse_boot"' in conf
    assert 'TEST_SUITES:apollo-qvp:auto-ad-nexios = "test_00_rse_boot"' in conf
    assert 'TEST_TARGET = "HSOCOEFVPTarget"' in conf
    assert 'TEST_TARGET:apollo-qvp:auto-ad-nexios = "HSOCOEFVPTarget"' in conf
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["selectors"] == ["test_00_rse_boot"]
    commands = [json.loads(line) for line in (run_dir / "commands.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [command["name"] for command in commands] == ["parse", "testimage"]
    assert all(command["status"] == "planned" for command in commands)
    assert " -e nexios-image" in commands[0]["command"]
    assert "MACHINE=apollo-qvp bitbake" in commands[0]["command"]
    assert "MACHINE=apollo-qvp bitbake" in commands[1]["command"]


def test_list_and_invalid_case_are_deterministic() -> None:
    listed = _run_validation("--list")
    rejected = _run_validation("--test-suite", "boot", "--test-case", "missing")

    assert listed.returncode == 0
    assert "boot:" in listed.stdout
    assert "rse-boot" in listed.stdout
    assert rejected.returncode == 64
    assert "unknown test case 'missing' for suite 'boot'" in rejected.stderr


def test_parse_only_records_parse_without_testimage() -> None:
    out_dir = Path("build/tests/validation-pytest-parse")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = _run_validation(
        "--test-suite",
        "boot",
        "--test-case",
        "rse-boot",
        "--parse-only",
        "--dry-run",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    commands = [
        json.loads(line)
        for line in (ROOT / out_dir / "commands.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [command["name"] for command in commands] == ["parse"]

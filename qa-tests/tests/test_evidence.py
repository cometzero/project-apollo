from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

import json
import pytest

from apollo_validation.evidence import append_record, summarize_records, write_reports
from apollo_validation.reporting import _write_junit


def test_summary_maps_failure_status(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    append_record(commands, {"name": "a", "status": "pass"})
    append_record(commands, {"name": "b", "status": "fail"})

    summary, exit_code = summarize_records(tmp_path)

    assert summary["status"] == "FAIL"
    assert exit_code == 1


def test_summary_maps_empty_run_to_blocked(tmp_path: Path) -> None:
    summary, exit_code = summarize_records(tmp_path)

    assert summary["status"] == "BLOCKED"
    assert exit_code == 2


def test_legacy_category_summary_allows_passing_commands_without_tests(
    tmp_path: Path,
) -> None:
    # Given: a legacy category run with one successful command and no profile.
    append_record(tmp_path / "commands.jsonl", {"name": "basic", "status": "pass"})

    # When: the category-only result is summarized.
    summary, exit_code = summarize_records(tmp_path)

    # Then: the established command-derived PASS contract remains unchanged.
    assert exit_code == 0
    assert summary["status"] == "PASS"
    assert summary["counts"]["total"] == 0


def test_final_reports_include_human_json_and_junit_results(
    tmp_path: Path,
) -> None:
    # Given: one passing OEQA PFDI result and its command record.
    result_path = tmp_path / "oeqa/pfdi/results/result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "nexios-bsp-initramfs": {
                    "result": {
                        "test_64_bsp_pfdi.PFDIBspTest.test_cli": {
                            "status": "PASSED",
                            "duration": 0.25,
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    append_record(
        tmp_path / "commands.jsonl",
        {
            "name": "oeqa-pfdi",
            "status": "pass",
            "duration_s": 1.0,
            "artifacts": [{"kind": "oeqa_result", "path": str(result_path)}],
        },
    )

    # When: the public final-report contract is rendered.
    summary, exit_code = write_reports(tmp_path)

    # Then: human, machine, and CI surfaces agree on the passing test.
    assert exit_code == 0
    assert summary["counts"]["passed"] == 1
    assert (tmp_path / "summary.txt").is_file()
    assert (tmp_path / "summary.json").is_file()
    assert (tmp_path / "junit.xml").is_file()
    assert "RESULT: PASS" in (tmp_path / "summary.txt").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(("profile", "normalized", "raw"), [("smcf", 4, 5), ("pfdi-si-cl1", 17, 18)])
def test_profile_junit_uses_normalized_assertion_counts(
    tmp_path: Path,
    profile: str,
    normalized: int,
    raw: int,
) -> None:
    # Given: a profile summary whose raw OEQA cases include one prerequisite.
    summary = {
        "test_profile": profile,
        "duration_s": 1.0,
        "counts": {"passed": normalized, "failed": 0, "blocked": 0, "skipped": 0, "total": normalized},
        "tests": [{"name": f"raw-{index}", "status": "PASS", "duration_s": 0.0} for index in range(raw)],
        "profile_result": {"assertions": [{"id": f"assertion-{index}", "status": "PASS"} for index in range(normalized)]},
    }
    path = tmp_path / "junit.xml"

    # When: profile-mode JUnit is rendered.
    _write_junit(path, summary)
    root = ET.parse(path).getroot()

    # Then: CI counts and testcase children match normalized assertions only.
    assert root.attrib["tests"] == str(normalized)
    assert len(root.findall("testcase")) == normalized

from __future__ import annotations

import json
from pathlib import Path

from apollo_validation.evidence import append_record, write_reports
from apollo_validation.validation_matrix import load_validation_matrix


WORKSPACE = Path(__file__).resolve().parents[2]
MATRIX_PATH = WORKSPACE / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"


def _named_run(tmp_path: Path) -> None:
    (tmp_path / "selection.json").write_text(
        json.dumps({"profile_name": "pfdi"}),
        encoding="utf-8",
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps({"backend": "qbox", "test_profile": "pfdi"}),
        encoding="utf-8",
    )


def test_unknown_required_command_status_fails_closed(tmp_path: Path) -> None:
    # Given: complete PASS assertions beside an unknown required command status.
    _named_run(tmp_path)
    profile = next(
        profile
        for profile in load_validation_matrix(MATRIX_PATH).profiles
        if profile.profile_id == "pfdi"
    )
    result_path = tmp_path / "qbox/result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "assertions": [
                    {
                        "id": assertion_id,
                        "status": "PASS",
                        "coverage_kind": profile.coverage_kind,
                    }
                    for assertion_id in profile.qbox_assertions
                ]
            }
        ),
        encoding="utf-8",
    )
    append_record(
        tmp_path / "commands.jsonl",
        {
            "name": "qbox-profile",
            "required": True,
            "status": "garbage",
            "artifacts": [{"kind": "qbox_result", "path": str(result_path)}],
        },
    )

    # When: the public reporting surface parses the run.
    summary, exit_code = write_reports(tmp_path)

    # Then: unknown evidence cannot preserve the assertion-derived PASS.
    assert exit_code != 0
    assert summary["status"] == "BLOCKED"
    assert {item["reason"] for item in summary["blockers"]} >= {
        "blocked_malformed_profile_evidence"
    }
    assert (tmp_path / "profile-result.json").is_file()


def test_malformed_command_json_writes_blocked_reports(tmp_path: Path) -> None:
    # Given: a named profile with a truncated commands.jsonl record.
    _named_run(tmp_path)
    (tmp_path / "commands.jsonl").write_text("{\n", encoding="utf-8")

    # When: the public reporting surface summarizes malformed evidence.
    summary, exit_code = write_reports(tmp_path)

    # Then: it fails closed without traceback and writes both JSON surfaces.
    assert exit_code != 0
    assert summary["status"] == "BLOCKED"
    assert {item["reason"] for item in summary["blockers"]} >= {
        "blocked_malformed_profile_evidence"
    }
    assert (tmp_path / "summary.json").is_file()
    assert (tmp_path / "profile-result.json").is_file()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_fvp_full_coverage.py"
AP_MAP_SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_ap_memory_map.py"


@pytest.fixture(scope="module")
def ap_map_audit(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Use current evaluated map evidence, independent of archived .omo runs."""
    output = tmp_path_factory.mktemp("apollo-ap-map") / "ap-map.json"
    result = subprocess.run(
        [sys.executable, str(AP_MAP_SCRIPT), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(output.read_text())["passed"] is True
    return output


def run_audit(
    tmp_path: Path,
    result_path: Path | None = None,
    *,
    ap_map_audit: Path,
) -> subprocess.CompletedProcess[str]:
    output = tmp_path / "coverage-audit.json"
    command = [
        sys.executable,
        str(SCRIPT),
        "--ap-map-audit",
        str(ap_map_audit),
        "--output",
        str(output),
    ]
    if result_path is not None:
        command.extend(("--result-json", str(result_path)))
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return completed


@pytest.mark.parametrize(
    ("input_text", "expected_reason"),
    [
        (None, "runtime_result_missing"),
        ("{not-json\n", "runtime_result_invalid_json"),
        ("[]\n", "runtime_result_not_object"),
        ("true\n", "runtime_result_not_object"),
    ],
)
def test_explicit_invalid_runtime_result_fails_closed(
    tmp_path: Path,
    input_text: str | None,
    expected_reason: str,
    ap_map_audit: Path,
) -> None:
    result_path = tmp_path / "runtime-result.json"
    if input_text is not None:
        result_path.write_text(input_text, encoding="utf-8")

    completed = run_audit(tmp_path, result_path, ap_map_audit=ap_map_audit)
    payload = json.loads(
        (tmp_path / "coverage-audit.json").read_text(encoding="utf-8")
    )

    assert completed.returncode != 0
    assert payload["passed"] is False
    input_check = next(
        check for check in payload["checks"] if check["name"] == "runtime_result_input"
    )
    assert input_check["passed"] is False
    assert input_check["reason"] == expected_reason


def test_omitting_runtime_result_retains_static_audit_mode(
    tmp_path: Path, ap_map_audit: Path,
) -> None:
    completed = run_audit(tmp_path, ap_map_audit=ap_map_audit)
    payload = json.loads(
        (tmp_path / "coverage-audit.json").read_text(encoding="utf-8")
    )

    assert completed.returncode == 0
    assert payload["passed"] is True
    assert not any(
        check["name"] == "runtime_result_input" for check in payload["checks"]
    )


def test_explicit_incomplete_runtime_object_fails_runtime_gates(
    tmp_path: Path, ap_map_audit: Path,
) -> None:
    result_path = tmp_path / "runtime-result.json"
    result_path.write_text('{"passed": true}\n', encoding="utf-8")

    completed = run_audit(tmp_path, result_path, ap_map_audit=ap_map_audit)
    payload = json.loads(
        (tmp_path / "coverage-audit.json").read_text(encoding="utf-8")
    )

    assert completed.returncode != 0
    assert payload["passed"] is False
    assert any(
        check["name"] == "gate:G0" and check["passed"] is False
        for check in payload["checks"]
    )


def test_missing_ap_map_audit_still_fails_static_coverage(tmp_path: Path) -> None:
    completed = run_audit(tmp_path, ap_map_audit=tmp_path / "missing-ap-map.json")
    payload = json.loads((tmp_path / "coverage-audit.json").read_text())
    assert completed.returncode != 0
    assert payload["passed"] is False
    check = next(item for item in payload["checks"] if item["name"] == "ap_9_1_1_memory_map")
    assert check["passed"] is False
    assert check["status"] == "not_available"

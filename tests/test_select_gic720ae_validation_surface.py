from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/select_gic720ae_validation_surface.py"
MATRIX = ROOT / "doc/validation/gic-720ae/validation-surfaces.yaml"
SCHEMA = ROOT / "tests/schemas/gic720ae-validation-surfaces.schema.json"
STAGE4_ONLY = ROOT / "tests/fixtures/gic720ae/validation-surface-stage4-only.yaml"


def test_selects_one_stage_and_records_skip_evidence_for_every_active_feature(tmp_path: Path) -> None:
    # Given: the tracked decision ledger and its fail-closed schema.
    output = tmp_path / "positive.json"

    # When: the validation-surface selector consumes the ledger.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--matrix",
            str(MATRIX),
            "--schema",
            str(SCHEMA),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: every active feature has exactly one selected stage and prior-stage evidence.
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["reason"] == "validation_surfaces_selected"
    assert report["active_feature_count"] == 4
    assert all(feature["selected_stage_count"] == 1 for feature in report["features"])
    assert all(feature["prior_stage_evidence_complete"] for feature in report["features"])


def test_rejects_stage4_selection_without_evidence_for_stages_one_through_three(tmp_path: Path) -> None:
    # Given: a stage-4-only fixture that attempts to bypass the ordered ladder.
    output = tmp_path / "negative.json"

    # When: the selector runs its explicit negative path.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--self-test-negative",
            str(STAGE4_ONLY),
            "--schema",
            str(SCHEMA),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the machine-readable failure names the missing earlier-stage evidence.
    assert result.returncode != 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["reason"] == "missing-stage-1..3-evidence"


def test_rejects_out_of_range_source_line_when_evidence_cannot_be_grounded(tmp_path: Path) -> None:
    # Given: the valid ledger with its first source citation changed to line 999999.
    matrix = tmp_path / "out-of-range.yaml"
    matrix.write_text(MATRIX.read_text(encoding="utf-8").replace("lines: 249-421,993-1029,1608-1672", 'lines: "999999"', 1), encoding="utf-8")
    output = tmp_path / "out-of-range.json"

    # When: the selector validates the source evidence.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--matrix",
            str(matrix),
            "--schema",
            str(SCHEMA),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it fails closed instead of accepting an ungrounded citation.
    assert result.returncode != 0
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "invalid-source-evidence"


def test_rejects_bare_metal_label_when_stage_one_requires_production_driver(tmp_path: Path) -> None:
    # Given: the valid ledger with the stage-1 canonical type changed to bare-metal.
    matrix = tmp_path / "order-label-bypass.yaml"
    matrix.write_text(MATRIX.read_text(encoding="utf-8").replace("surface_type: production-driver", "surface_type: minimal-bare-metal", 1), encoding="utf-8")
    output = tmp_path / "order-label-bypass.json"

    # When: the selector checks the canonical stage identity.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--matrix",
            str(matrix),
            "--schema",
            str(SCHEMA),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: a bare-metal proposal cannot masquerade as the production-driver stage.
    assert result.returncode != 0
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "schema-validation-failed"

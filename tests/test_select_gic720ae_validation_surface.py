from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/select_gic720ae_validation_surface.py"
SCHEMA = ROOT / "tests/schemas/gic720ae-validation-surfaces.schema.json"


@pytest.fixture
def selector_inputs(tmp_path: Path) -> tuple[Path, Path]:
    # These citations describe only this generated host fixture, not runtime evidence.
    workspace = tmp_path / "workspace"
    script = workspace / "scripts/test" / SCRIPT.name
    script.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, script)
    source = workspace / "fixture.c"
    source.write_text("".join(f"void stage_{stage}(void);\n" for stage in range(1, 5)))
    surface_types = (
        "production-driver", "safe-guarded-knob", "opt-in-test-driver", "minimal-bare-metal",
    )
    features = []
    for selected in range(1, 5):
        stages = []
        for stage, surface_type in enumerate(surface_types, start=1):
            item = {
                "stage": stage,
                "status": "selected" if stage == selected else "unavailable",
                "surface_type": surface_type,
                "rationale": "Host test fixture for ordered stage selection.",
                "source_evidence": [{
                    "source": "fixture", "lines": str(stage), "anchor": f"stage_{stage}",
                }],
            }
            if stage == selected == 4:
                item["bare_metal"] = {
                    "minimal_scope": "Host fixture", "opt_in_package": "fixture-probe",
                    "timeout_seconds": 1, "cleanup": "Host fixture cleanup",
                }
            stages.append(item)
        features.append({"id": f"fixture-stage-{selected}", "active": True, "stages": stages})
    matrix = workspace / "matrix.yaml"
    matrix.write_text(yaml.safe_dump({
        "format_version": 1,
        "sources": {"fixture": {
            "path": "fixture.c", "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }},
        "features": features,
    }), encoding="utf-8")
    return script, matrix


def run_selector(script: Path, matrix: Path, output: Path, *, negative: bool = False):
    return subprocess.run(
        [sys.executable, str(script), "--self-test-negative" if negative else "--matrix",
         str(matrix), "--schema", str(SCHEMA), "--output", str(output)],
        cwd=script.parents[2], check=False, text=True, capture_output=True,
    )


def test_selects_one_stage_and_records_skip_evidence_for_every_active_feature(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    output = tmp_path / "positive.json"

    result = run_selector(script, matrix, output)

    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["reason"] == "validation_surfaces_selected"
    assert report["active_feature_count"] == 4
    assert [feature["selected_stage"] for feature in report["features"]] == [1, 2, 3, 4]
    assert all(feature["selected_stage_count"] == 1 for feature in report["features"])
    assert all(feature["prior_stage_evidence_complete"] for feature in report["features"])


def test_rejects_stage4_selection_without_evidence_for_stages_one_through_three(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    data = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    for stage in data["features"][3]["stages"][:3]:
        stage["source_evidence"] = []
    matrix.write_text(yaml.safe_dump(data), encoding="utf-8")
    output = tmp_path / "negative.json"

    result = run_selector(script, matrix, output, negative=True)

    assert result.returncode == 1
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "missing-stage-1..3-evidence"


def test_rejects_out_of_range_source_line_when_evidence_cannot_be_grounded(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    data = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    data["features"][0]["stages"][0]["source_evidence"][0]["lines"] = "999999"
    matrix.write_text(yaml.safe_dump(data), encoding="utf-8")
    output = tmp_path / "out-of-range.json"

    result = run_selector(script, matrix, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "invalid-source-evidence"


def test_rejects_bare_metal_label_when_stage_one_requires_production_driver(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    data = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    data["features"][0]["stages"][0]["surface_type"] = "minimal-bare-metal"
    matrix.write_text(yaml.safe_dump(data), encoding="utf-8")
    output = tmp_path / "order-label-bypass.json"

    result = run_selector(script, matrix, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "schema-validation-failed"


def test_rejects_stale_source_hash(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    (matrix.parent / "fixture.c").write_text("changed source\n", encoding="utf-8")
    output = tmp_path / "stale.json"

    result = run_selector(script, matrix, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "stale-source-evidence"


def test_rejects_source_anchor_outside_cited_lines(
    tmp_path: Path, selector_inputs: tuple[Path, Path],
) -> None:
    script, matrix = selector_inputs
    data = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    data["features"][0]["stages"][0]["source_evidence"][0]["anchor"] = "stage_2"
    matrix.write_text(yaml.safe_dump(data), encoding="utf-8")
    output = tmp_path / "ungrounded.json"

    result = run_selector(script, matrix, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "invalid-source-evidence"

from __future__ import annotations

from pathlib import Path
import json

from apollo_validation.run_inputs import JsonObject, capture_run_inputs


WORKSPACE = Path(__file__).resolve().parents[2]


def test_qa_runner_revision_tracks_the_workspace(tmp_path: Path) -> None:
    # Given: the QA runner is owned by the top-level workspace.
    context: JsonObject = {}

    # When: run inputs capture their source revisions.
    capture_run_inputs(WORKSPACE, tmp_path, context)

    # Then: the QA runner and workspace resolve to the same commit.
    revisions = context["input_revisions"]
    assert isinstance(revisions, dict)
    assert revisions["qa_runner"]
    assert (
        revisions["qa_runner"]
        == revisions["workspace"]
    )


def test_standalone_comparison_mode_reaches_input_manifest(
    tmp_path: Path,
) -> None:
    context: JsonObject = {"comparison_mode": "standalone"}

    manifest_path = capture_run_inputs(WORKSPACE, tmp_path, context)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["comparison_mode"] == "standalone"
    assert "accepted_fvp_reference" not in manifest

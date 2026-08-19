from __future__ import annotations

from pathlib import Path

from apollo_validation.run_inputs import JsonObject, capture_run_inputs


WORKSPACE = Path(__file__).resolve().parents[2]


def test_qa_runner_revision_tracks_the_workspace(tmp_path: Path) -> None:
    # Given: the QA runner is owned by the top-level workspace.
    context: JsonObject = {}

    # When: run inputs capture their source revisions.
    capture_run_inputs(WORKSPACE, tmp_path, context)

    # Then: the QA runner and workspace resolve to the same commit.
    assert context["input_revisions"]["qa_runner"]
    assert (
        context["input_revisions"]["qa_runner"]
        == context["input_revisions"]["workspace"]
    )

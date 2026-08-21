from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import assert_never, Literal, TypeAlias

import pytest

from apollo_validation.provenance import sha256_file

from tests.provenance_fixtures import (
    JsonValue,
    make_workspace,
    run_qbox_profile,
    write_reference,
)


Mutation: TypeAlias = Literal["skipped", "missing", "duplicate", "xen"]


def test_runtime_input_hashing_reads_files_in_bounded_chunks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"apollo-runtime-input\n" * (1024 * 512)
    artifact = tmp_path / "image.wic"
    artifact.write_bytes(payload)

    def fail_if_buffered(_: Path) -> bytes:
        pytest.fail("runtime artifact hashing must not call read_bytes")

    monkeypatch.setattr(Path, "read_bytes", fail_if_buffered)

    assert sha256_file(artifact) == hashlib.sha256(payload).hexdigest()


def test_named_qbox_profile_requires_reference_before_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: a valid named QBox profile with no FVP reference.
    make_workspace(tmp_path)

    # When: the public root runner handles the request.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, None)

    # Then: it rejects with a stable reason before any launcher subprocess.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_required"


def test_matching_fvp_reference_reaches_qbox_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: complete matching PASS evidence from the FVP backend.
    make_workspace(tmp_path)
    reference = write_reference(tmp_path)

    # When: the named QBox dry-run consumes it.
    _, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: preflight executes and the accepted identity reaches the input manifest.
    assert len(calls) == 1
    manifest = json.loads(
        (tmp_path / "build/tests/qbox-pfdi-run/evidence/input-manifest.json").read_text()
    )
    accepted = manifest["accepted_fvp_reference"]
    assert accepted["run_id"] == "fvp-pfdi-run"
    assert accepted["path"] == str(reference)
    assert len(accepted["summary_sha256"]) == 64
    assert len(accepted["semantic_profile_digest"]) == 64


def _set(mapping: dict[str, JsonValue], path: tuple[str, ...], value: JsonValue) -> None:
    current = mapping
    for key in path[:-1]:
        child = current[key]
        assert isinstance(child, dict)
        current = child
    current[path[-1]] = value


@pytest.mark.parametrize(
    ("path", "value", "reason"),
    [
        (("status",), "FAIL", "blocked_fvp_reference_status"),
        (("backend",), "qbox", "blocked_fvp_reference_backend"),
        (("test_profile",), "ras_cpu", "blocked_fvp_reference_profile_mismatch"),
        (("image_profile",), "product", "blocked_fvp_reference_image_mismatch"),
        (("provenance", "cpu_count"), 8, "blocked_fvp_reference_cpu_mismatch"),
        (("provenance", "selectors"), ["wrong"], "blocked_fvp_reference_selector_mismatch"),
        (("profile_result", "expected"), ["wrong"], "blocked_fvp_reference_expected_mismatch"),
        (("provenance", "profile_snapshot_sha256"), "0" * 64, "blocked_fvp_reference_profile_snapshot_drift"),
        (("provenance", "semantic_profile_digest"), "0" * 64, "blocked_fvp_reference_semantic_drift"),
    ],
)
def test_reference_contract_mismatch_rejects_with_stable_reason(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    path: tuple[str, ...],
    value: JsonValue,
    reason: str,
) -> None:
    # Given: one contract identity differs from the selected QBox profile.
    make_workspace(tmp_path)
    reference = write_reference(tmp_path, lambda summary: _set(summary, path, value))

    # When: provenance is checked.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: the exact mismatch rejects before preflight.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == f"error: {reason}"


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("skipped", "blocked_fvp_reference_assertions_incomplete"),
        ("missing", "blocked_fvp_reference_assertions_incomplete"),
        ("duplicate", "blocked_fvp_reference_assertions_incomplete"),
        ("xen", "blocked_fvp_reference_xen"),
    ],
)
def test_incomplete_or_xen_fvp_evidence_rejects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: Mutation,
    reason: str,
) -> None:
    # Given: all-green-looking evidence with a hidden completeness violation.
    make_workspace(tmp_path)

    def mutate(summary: dict[str, JsonValue]) -> None:
        profile_result = summary["profile_result"]
        provenance = summary["provenance"]
        assert isinstance(profile_result, dict)
        assert isinstance(provenance, dict)
        assertions = profile_result["assertions"]
        assert isinstance(assertions, list)
        match mutation:
            case "skipped":
                first = assertions[0]
                assert isinstance(first, dict)
                first["status"] = "SKIPPED"
            case "missing":
                assertions.pop()
            case "duplicate":
                assertions.append(assertions[0])
            case "xen":
                selectors = provenance["selectors"]
                assert isinstance(selectors, list)
                provenance["selectors"] = [*selectors, "test_40_virtualization"]
            case unexpected:
                assert_never(unexpected)

    reference = write_reference(tmp_path, mutate)

    # When: the QBox profile gate parses the reference.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: it fails closed before subprocess execution.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == f"error: {reason}"


@pytest.mark.parametrize(
    ("kind", "reason"),
    [
        ("testdata", "blocked_fvp_reference_testdata_drift"),
        ("runtime_config", "blocked_fvp_reference_runtime_config_drift"),
        ("image_artifact", "blocked_fvp_reference_image_artifact_drift"),
    ],
)
def test_stale_runtime_input_rejects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    reason: str,
) -> None:
    # Given: a reference whose recorded runtime input changed afterward.
    make_workspace(tmp_path)
    reference = write_reference(tmp_path)
    summary = json.loads(reference.read_text())
    entry = next(item for item in summary["provenance"]["runtime_inputs"] if item["kind"] == kind)
    Path(entry["path"]).write_bytes(b"drifted\n")

    # When: the stale reference is consumed.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: the changed input is rejected before preflight.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == f"error: {reason}"


def test_shared_git_blob_drift_rejects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: shared OEQA source changed after FVP evidence was recorded.
    make_workspace(tmp_path)
    reference = write_reference(tmp_path)
    shared = tmp_path / "hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/runtime/cases/test_64_bsp_pfdi.py"
    shared.write_text("# drifted\n", encoding="utf-8")

    # When: the QBox gate compares current committed inputs.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: dirty shared input is rejected.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_shared_input_drift"


def test_missing_malformed_duplicate_and_symlink_references_reject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: explicit invalid reference path variants.
    make_workspace(tmp_path)
    missing = tmp_path / "build/tests/missing/summary.json"

    # When/Then: a missing reference is classified precisely.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, missing, "qbox-missing")
    assert result == 64 and calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_missing"

    malformed = tmp_path / "build/tests/malformed/summary.json"
    malformed.parent.mkdir(parents=True)
    malformed.write_text("{", encoding="utf-8")
    result, calls = run_qbox_profile(tmp_path, monkeypatch, malformed, "qbox-malformed")
    assert result == 64 and calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_malformed"

    reference = write_reference(tmp_path)
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference, "fvp-pfdi-run")
    assert result == 64 and calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_duplicate_run_id"

    symlink = tmp_path / "build/tests/reference-link.json"
    symlink.symlink_to(reference)
    result, calls = run_qbox_profile(tmp_path, monkeypatch, symlink, "qbox-symlink")
    assert result == 64 and calls == []
    assert capsys.readouterr().err.strip() == "error: blocked_fvp_reference_path"

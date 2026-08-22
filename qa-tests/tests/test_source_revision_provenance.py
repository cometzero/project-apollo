from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal, TypeAlias, assert_never

import pytest

from apollo_validation.source_revisions import (
    SourceRevisionError,
    capture_source_revisions,
    validate_fvp_source_revisions,
)
from tests.provenance_fixtures import (
    JsonValue,
    make_workspace,
    run_qbox_profile,
    write_reference,
)


Mutation: TypeAlias = Literal[
    "missing",
    "unexpected",
    "malformed",
    "nonstring",
    "uppercase",
    "nonexistent",
    "nonancestor",
    "bsp-drift",
    "platform-drift",
]


def _revision(root: Path, revision: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", revision],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def _unrelated_commit(root: Path) -> str:
    tree = _revision(root, "HEAD^{tree}")
    return subprocess.run(
        ["git", "commit-tree", tree],
        cwd=root,
        check=True,
        input="unrelated\n",
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def _mutate_revisions(
    summary: dict[str, JsonValue],
    root: Path,
    mutation: Mutation,
) -> None:
    provenance = summary["provenance"]
    assert isinstance(provenance, dict)
    revisions = provenance["source_revisions"]
    assert isinstance(revisions, dict)
    parent = _revision(root, "HEAD^")
    match mutation:
        case "missing":
            revisions.pop("workspace")
        case "unexpected":
            revisions["qbox_core"] = _revision(root, "HEAD")
        case "malformed":
            revisions["workspace"] = "not-a-revision"
        case "nonstring":
            revisions["workspace"] = 7
        case "uppercase":
            revisions["workspace"] = _revision(root, "HEAD").upper()
        case "nonexistent":
            revisions["workspace"] = "0" * 40
        case "nonancestor":
            revisions["workspace"] = _unrelated_commit(root)
        case "bsp-drift":
            revisions["bsp_layer"] = parent
        case "platform-drift":
            revisions["platform_layer"] = parent
        case unexpected:
            assert_never(unexpected)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("missing", "blocked_fvp_reference_source_revision_missing"),
        ("unexpected", "blocked_fvp_reference_source_revision_unexpected"),
        ("malformed", "blocked_fvp_reference_source_revision_malformed"),
        ("nonstring", "blocked_fvp_reference_source_revision_malformed"),
        ("uppercase", "blocked_fvp_reference_source_revision_malformed"),
        ("nonexistent", "blocked_fvp_reference_source_revision_nonexistent"),
        ("nonancestor", "blocked_fvp_reference_source_revision_non_ancestor"),
        ("bsp-drift", "blocked_fvp_reference_source_revision_shared_drift"),
        ("platform-drift", "blocked_fvp_reference_source_revision_shared_drift"),
    ],
)
def test_invalid_source_revision_rejects_before_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: Mutation,
    reason: str,
) -> None:
    # Given: one invalid or unauthorized FVP source revision identity.
    make_workspace(tmp_path)
    reference = write_reference(
        tmp_path,
        lambda summary: _mutate_revisions(summary, tmp_path, mutation),
    )

    # When: the named QBox profile consumes the reference.
    result, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: the stable revision reason rejects before launcher preflight.
    assert result == 64
    assert calls == []
    assert capsys.readouterr().err.strip() == f"error: {reason}"


def test_real_ancestor_workspace_revision_is_allowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: FVP ran at a real ancestor while every shared blob still matches.
    make_workspace(tmp_path)

    def use_parent(summary: dict[str, JsonValue]) -> None:
        provenance = summary["provenance"]
        assert isinstance(provenance, dict)
        revisions = provenance["source_revisions"]
        assert isinstance(revisions, dict)
        parent = _revision(tmp_path, "HEAD^")
        revisions["workspace"] = parent
        revisions["qa_runner"] = parent

    reference = write_reference(tmp_path, use_parent)

    # When: the explicit ancestor reference is consumed.
    _, calls = run_qbox_profile(tmp_path, monkeypatch, reference)

    # Then: backend-only top-level evolution may reach QBox preflight.
    assert len(calls) == 1


def test_backend_revision_key_policy_is_explicit(tmp_path: Path) -> None:
    # Given: mapped repositories for shared, mixed, and QBox-only sources.
    make_workspace(tmp_path)

    # When: source identities are captured for both backends.
    fvp_keys = dict(capture_source_revisions(tmp_path, "fvp"))
    qbox_keys = dict(capture_source_revisions(tmp_path, "qbox"))

    # Then: FVP omits QBox-only keys while QBox records the explicit allowlist.
    assert set(fvp_keys) == {
        "workspace",
        "qa_runner",
        "bsp_layer",
        "platform_layer",
    }
    assert set(qbox_keys) == {
        *fvp_keys,
        "qbox_core",
        "qbox_platform",
        "qemu",
    }


def test_qvp_only_bsp_revision_is_allowed_when_shared_contract_matches(
    tmp_path: Path,
) -> None:
    make_workspace(tmp_path)
    reference = dict(capture_source_revisions(tmp_path, "fvp"))
    qvp_machine = tmp_path / "hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf"
    qvp_machine.parent.mkdir(parents=True, exist_ok=True)
    qvp_machine.write_text('MACHINE = "apollo-qvp"\n', encoding="utf-8")
    subprocess.run(["git", "add", str(qvp_machine)], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "qvp-only metadata"],
        cwd=tmp_path,
        check=True,
    )

    current = tuple(
        (key, reference["platform_layer"])
        if key == "platform_layer"
        else (key, revision)
        for key, revision in capture_source_revisions(tmp_path, "qbox")
    )

    validate_fvp_source_revisions(tmp_path, reference, current, True)


def test_fvp_bsp_revision_change_remains_rejected(tmp_path: Path) -> None:
    make_workspace(tmp_path)
    reference = dict(capture_source_revisions(tmp_path, "fvp"))
    fvp_machine = tmp_path / "hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-fvp.conf"
    fvp_machine.parent.mkdir(parents=True, exist_ok=True)
    fvp_machine.write_text('MACHINE = "apollo-fvp"\n', encoding="utf-8")
    subprocess.run(["git", "add", str(fvp_machine)], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "fvp metadata drift"],
        cwd=tmp_path,
        check=True,
    )
    current = tuple(
        (key, reference["platform_layer"])
        if key == "platform_layer"
        else (key, revision)
        for key, revision in capture_source_revisions(tmp_path, "qbox")
    )

    with pytest.raises(
        SourceRevisionError,
        match="blocked_fvp_reference_source_revision_shared_drift",
    ):
        validate_fvp_source_revisions(tmp_path, reference, current, True)

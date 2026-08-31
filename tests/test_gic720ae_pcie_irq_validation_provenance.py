from __future__ import annotations

from pathlib import Path
import json
import subprocess

import jsonschema
import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
from scripts.test import gic720ae_pcie_irq_validation_repository as repository


def git(repo: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *arguments], capture_output=True, check=True
    )


def initialized_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Task11 Test")
    git(repo, "config", "user.email", "task11@example.invalid")
    (repo / "scope").mkdir()
    (repo / "scope/tracked.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "scope/tracked.txt")
    git(repo, "commit", "-qm", "base")
    return repo


def field(payload: contract.JsonObject, key: str) -> contract.JsonObject:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def items(payload: contract.JsonObject, key: str) -> list[contract.JsonValue]:
    value = payload[key]
    assert isinstance(value, list)
    return value


def text(payload: contract.JsonObject, key: str) -> str:
    value = payload[key]
    assert isinstance(value, str)
    return value


def test_repository_state_attributes_staged_worktree_and_untracked(
    tmp_path: Path,
) -> None:
    # Given: each dirty class exists inside one explicit source scope.
    repo = initialized_repo(tmp_path)
    (repo / "scope/tracked.txt").write_text("staged\n", encoding="utf-8")
    git(repo, "add", "scope/tracked.txt")
    (repo / "scope/tracked.txt").write_text("worktree\n", encoding="utf-8")
    (repo / "scope/new.txt").write_text("untracked\n", encoding="utf-8")

    # When: provenance is captured from the real repository.
    state = repository.capture(repo, ("scope",))

    # Then: all three states have deterministic, attributed observables.
    assert field(state, "staged_diff")["size"] != 0
    assert field(state, "worktree_diff")["size"] != 0
    untracked = items(state, "untracked_sources")
    assert (
        untracked and field({"entry": untracked[0]}, "entry")["path"] == "scope/new.txt"
    )
    codes = {
        text(field({"entry": entry}, "entry"), "code")
        for entry in items(state, "status_entries")
    }
    assert codes == {"MM", "??"}


def test_repository_state_changes_for_scoped_untracked_drift(tmp_path: Path) -> None:
    # Given: a clean real repository and a pinned scoped capture.
    repo = initialized_repo(tmp_path)
    before = repository.capture(repo, ("scope",))

    # When: an untracked source appears in that scope.
    (repo / "scope/new.py").write_text("value = 1\n", encoding="utf-8")
    after = repository.capture(repo, ("scope",))

    # Then: HEAD is stale but source-state provenance changes.
    assert after["head"] == before["head"]
    assert after != before
    assert after["untracked_manifest_sha256"] != before["untracked_manifest_sha256"]
    with pytest.raises(contract.ValidationError, match="provenance_changed"):
        repository.assert_same(repo, ("scope",), before)


def test_repository_scope_rejects_escape_and_symlink(tmp_path: Path) -> None:
    # Given: a real repository plus unsafe scope inputs.
    repo = initialized_repo(tmp_path)
    (repo / "scope/link").symlink_to(repo / "scope/tracked.txt")

    # When/Then: neither path escape nor symlink source can enter provenance.
    with pytest.raises(contract.ValidationError, match="repository_scope"):
        repository.capture(repo, ("../outside",))
    with pytest.raises(contract.ValidationError, match="repository_untracked"):
        repository.capture(repo, ("scope",))


def test_repository_expected_clean_rejects_dirty_scope(tmp_path: Path) -> None:
    # Given: an expected-clean source scope with a tracked modification.
    repo = initialized_repo(tmp_path)
    (repo / "scope/tracked.txt").write_text("dirty\n", encoding="utf-8")

    # When/Then: provenance refuses to label that QBox/QEMU-style scope clean.
    with pytest.raises(contract.ValidationError, match="repository_expected_clean"):
        repository.capture(repo, ("scope",), expected_clean=True)


def test_task11_scope_ignores_publication_docs_but_detects_tooling(
    tmp_path: Path,
) -> None:
    # Given: a temporary superproject with tracked tooling and publication docs.
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Task11 Test")
    git(repo, "config", "user.email", "task11@example.invalid")
    tooling = repo / "scripts/test/tool.py"
    tooling.parent.mkdir(parents=True)
    tooling.write_text("tool = 'base'\n", encoding="utf-8")
    roadmap = repo / "doc/qbox-fvp-emulation-project.md"
    roadmap.parent.mkdir(parents=True)
    roadmap.write_text("publication base\n", encoding="utf-8")
    validation = repo / "doc/validation/gic-720ae/result.md"
    validation.parent.mkdir(parents=True)
    validation.write_text("result base\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    _, scope = provenance.REPOSITORIES["superproject"]
    before = repository.capture(repo, scope)

    # When: Task12/F4 publication content changes without executable drift.
    roadmap.write_text("publication result hash edit\n", encoding="utf-8")
    validation.write_text("validation result hash edit\n", encoding="utf-8")
    after_docs = repository.capture(repo, scope)

    # Then: Task11's frozen source capture remains stable for publication-only edits.
    assert "doc/qbox-fvp-emulation-project.md" not in scope
    assert "doc/validation/gic-720ae" not in scope
    assert after_docs == before
    repository.assert_same(repo, scope, before)

    # When: a scoped executable changes after the same document edits.
    tooling.write_text("tool = 'changed'\n", encoding="utf-8")

    # Then: Task11 still fails closed for executable provenance drift.
    with pytest.raises(contract.ValidationError, match="provenance_changed"):
        repository.assert_same(repo, scope, before)


@pytest.mark.parametrize(
    "repository_name",
    (
        "superproject",
        "linux",
        "trusted_firmware_a",
        "scp_firmware",
        "meta_hsoc_bsp",
        "qbox_platform",
        "qbox_core",
        "qemu",
    ),
)
def test_task11_repository_scopes_detect_tracked_source_drift(
    tmp_path: Path, repository_name: str
) -> None:
    # Given: a pinned temporary owner repository with one scoped source file.
    repo = tmp_path / repository_name
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Task11 Test")
    git(repo, "config", "user.email", "task11@example.invalid")
    _, scope = provenance.REPOSITORIES[repository_name]
    source = repo / scope[0]
    if source.suffix:
        source.parent.mkdir(parents=True, exist_ok=True)
    else:
        source.mkdir(parents=True)
        source = source / "tracked-source"
    source.write_text("base\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    before = repository.capture(repo, scope)

    # When: a tracked source in the Task11 owner scope changes.
    source.write_text("changed\n", encoding="utf-8")

    # Then: every executable and hardware owner scope fails closed.
    with pytest.raises(contract.ValidationError, match="provenance_changed"):
        repository.assert_same(repo, scope, before)


@pytest.mark.parametrize(
    ("field_name", "invalid"),
    [
        ("path", ""),
        ("staged_diff", {"sha256": "bad", "size": 1}),
        ("status_entries", [{"code": "BAD", "path": "scope/a"}]),
        ("untracked_manifest_sha256", "bad"),
        ("untracked_sources", [{"path": "scope/a", "sha256": "bad", "size": 1}]),
    ],
)
def test_repository_schema_rejects_malformed_state(
    tmp_path: Path, field_name: str, invalid: contract.JsonValue
) -> None:
    # Given: a valid capture and the repository boundary schema.
    state = repository.capture(initialized_repo(tmp_path), ("scope",))
    schema = json.loads(contract.PROVENANCE_SCHEMA.read_text(encoding="utf-8"))
    repository_schema = {**schema["$defs"]["repository"], "$defs": schema["$defs"]}

    # When: one source-state observable is malformed.
    state[field_name] = invalid

    # Then: schema validation fails closed.
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(repository_schema).validate(state)

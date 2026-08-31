from __future__ import annotations

import copy
from pathlib import Path
from typing import Literal, assert_never

import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
from gic720ae_frozen_ap_map_support import bound_closure


def test_frozen_comparison_accepts_validated_run_local_ap_map_relocation(
    tmp_path: Path,
) -> None:
    # Given: independently contained closures bind byte-identical AP-map receipts.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    frozen_closure = bound_closure(tmp_path / "build-only", binary)
    current_closure = bound_closure(tmp_path / "run-current", binary)
    frozen_path = tmp_path / "build-only/provenance.json"
    provenance.atomic_write(frozen_path, frozen_closure)

    # When/Then: the sole validated run-local path relocation is accepted.
    provenance.compare_frozen(
        current_closure, frozen_path, tmp_path / "run-current"
    )


def test_frozen_comparison_accepts_same_run_local_ap_map_path(tmp_path: Path) -> None:
    # Given: one canonical bound closure and its exact frozen bytes.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    closure = bound_closure(tmp_path / "run", binary)
    frozen_path = tmp_path / "run/provenance.json"
    provenance.atomic_write(frozen_path, closure)

    # When/Then: strict same-path comparison remains accepted.
    provenance.compare_frozen(closure, frozen_path, tmp_path / "run")


ApMapMutation = Literal["hash", "size", "status"]


@pytest.mark.parametrize("mutation", ("hash", "size", "status"))
def test_frozen_comparison_rejects_ap_map_identity_drift(
    tmp_path: Path, mutation: ApMapMutation
) -> None:
    # Given: two valid closures before one frozen AP-map identity is changed.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    frozen = bound_closure(tmp_path / "build-only", binary)
    current = bound_closure(tmp_path / "run-current", binary)
    binding = contract.object_value(frozen["ap_memory_map_audit"], "test_binding")
    match mutation:
        case "hash":
            binding["sha256"] = "1" * 64
        case "size":
            size = binding["size"]
            assert isinstance(size, int)
            binding["size"] = size + 1
        case "status":
            audit = tmp_path / "build-only/ap-map-audit.json"
            audit.write_text('{"passed": false}\n', encoding="utf-8")
            binding["sha256"] = contract.digest(audit)
            binding["size"] = audit.stat().st_size
        case unreachable:
            assert_never(unreachable)
    frozen_path = tmp_path / "build-only/provenance.json"
    provenance.atomic_write(frozen_path, frozen)

    # When/Then: path normalization cannot hide content identity drift.
    with pytest.raises(contract.ValidationError, match="ap_map_identity"):
        provenance.compare_frozen(current, frozen_path, tmp_path / "run-current")


UnsafePath = Literal["nonlocal", "traversal", "symlink"]


@pytest.mark.parametrize("mutation", ("nonlocal", "traversal", "symlink"))
def test_frozen_comparison_rejects_unsafe_ap_map_path(
    tmp_path: Path, mutation: UnsafePath
) -> None:
    # Given: a frozen closure whose AP-map binding escapes its exact sibling role.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    frozen = bound_closure(tmp_path / "build-only", binary)
    current = bound_closure(tmp_path / "run-current", binary)
    binding = contract.object_value(frozen["ap_memory_map_audit"], "test_binding")
    audit = tmp_path / "build-only/ap-map-audit.json"
    match mutation:
        case "nonlocal":
            binding["path"] = str(tmp_path / "run-current/ap-map-audit.json")
        case "traversal":
            binding["path"] = str(tmp_path / "build-only/sub/../ap-map-audit.json")
        case "symlink":
            content = audit.read_bytes()
            audit.unlink()
            target = tmp_path / "outside-ap-map-audit.json"
            target.write_bytes(content)
            audit.symlink_to(target)
        case unreachable:
            assert_never(unreachable)
    frozen_path = tmp_path / "build-only/provenance.json"
    provenance.atomic_write(frozen_path, frozen)

    # When/Then: every nonlocal or indirect binding fails as a path error.
    with pytest.raises(contract.ValidationError, match="frozen_ap_map_path"):
        provenance.compare_frozen(current, frozen_path, tmp_path / "run-current")


OtherDrift = Literal["source", "repository", "binary", "gate", "profile", "path"]


@pytest.mark.parametrize(
    "mutation", ("source", "repository", "binary", "gate", "profile", "path")
)
def test_frozen_comparison_rejects_every_non_ap_map_drift(
    tmp_path: Path, mutation: OtherDrift
) -> None:
    # Given: closures differ in exactly one non-AP-map provenance field.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    frozen = bound_closure(tmp_path / "build-only", binary)
    current = copy.deepcopy(frozen)
    current_binding = contract.object_value(current["ap_memory_map_audit"], "binding")
    current_binding["path"] = str(tmp_path / "run-current/ap-map-audit.json")
    (tmp_path / "run-current").mkdir()
    (tmp_path / "run-current/ap-map-audit.json").write_bytes(
        (tmp_path / "build-only/ap-map-audit.json").read_bytes()
    )
    files = contract.object_value(current["files"], "files")
    repositories = contract.object_value(current["repositories"], "repositories")
    match mutation:
        case "source" | "path":
            source = contract.object_value(files["source_contract"], "source")
            source["path"] = contract.string_value(source["path"], "path") + ".x"
        case "gate":
            contract.object_value(files["fvp_reference_gate"], "gate")["size"] = 2
        case "profile":
            contract.object_value(files["qbox_profile_manifest"], "profile")[
                "sha256"
            ] = "2" * 64
        case "repository":
            contract.object_value(repositories["superproject"], "repository")[
                "head"
            ] = "3" * 40
        case "binary":
            current_binary = contract.object_value(current["qbox_binary"], "binary")
            current_binary["path"] = (
                contract.string_value(current_binary["path"], "path") + ".x"
            )
        case unreachable:
            assert_never(unreachable)
    frozen_path = tmp_path / "build-only/provenance.json"
    provenance.atomic_write(frozen_path, frozen)

    # When/Then: only the validated AP-map path is projected away.
    with pytest.raises(contract.ValidationError, match="frozen_provenance_drift"):
        provenance.compare_frozen(current, frozen_path, tmp_path / "run-current")


SchemaMutation = Literal["extra", "missing"]


@pytest.mark.parametrize("mutation", ("extra", "missing"))
def test_frozen_comparison_rejects_schema_drift(
    tmp_path: Path, mutation: SchemaMutation
) -> None:
    # Given: one frozen closure with an extra or missing top-level field.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    closure = bound_closure(tmp_path / "run", binary)
    frozen_path = tmp_path / "run/provenance.json"
    invalid = dict(closure)
    match mutation:
        case "extra":
            invalid["extra"] = True
        case "missing":
            del invalid["repositories"]
        case unreachable:
            assert_never(unreachable)
    provenance.atomic_write(frozen_path, invalid)

    # When/Then: schema shape drift is rejected before comparison.
    with pytest.raises(contract.ValidationError, match="frozen_provenance_schema"):
        provenance.compare_frozen(closure, frozen_path, tmp_path / "run")


def test_frozen_comparison_rejects_whitespace_byte_drift(tmp_path: Path) -> None:
    # Given: one schema-valid closure serialized with an extra newline.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    closure = bound_closure(tmp_path / "run", binary)
    frozen_path = tmp_path / "run/provenance.json"
    provenance.atomic_write(frozen_path, closure)
    frozen_path.write_bytes(frozen_path.read_bytes() + b"\n")

    # When/Then: semantic equality cannot override frozen byte drift.
    with pytest.raises(contract.ValidationError, match="frozen_provenance_bytes"):
        provenance.compare_frozen(closure, frozen_path, tmp_path / "run")


def test_same_ap_map_basename_with_different_bytes_is_rejected(tmp_path: Path) -> None:
    # Given: both run-local receipts have the expected name but different bytes.
    binary = tmp_path / "platforms-vp"
    binary.write_text("qbox\n", encoding="utf-8")
    frozen = bound_closure(tmp_path / "build-only", binary)
    current = bound_closure(
        tmp_path / "run-current", binary, '{"generation": 2, "passed": true}\n'
    )
    frozen_path = tmp_path / "build-only/provenance.json"
    provenance.atomic_write(frozen_path, frozen)

    # When/Then: basename equality cannot substitute for content identity.
    with pytest.raises(contract.ValidationError, match="ap_map_identity"):
        provenance.compare_frozen(current, frozen_path, tmp_path / "run-current")

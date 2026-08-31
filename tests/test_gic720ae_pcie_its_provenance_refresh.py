from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/build_gic720ae_pcie_its_profile.py"
REMEDIATION_ROLES = (
    "scripts/test/build_gic720ae_pcie_its_profile.py",
    "scripts/test/gic720ae_pcie_its_profile/contract.py",
    "scripts/test/gic720ae_pcie_its_profile/finalize.py",
    "scripts/test/gic720ae_pcie_its_profile/provenance.py",
    "scripts/test/gic720ae_pcie_its_profile/workflow.py",
    "tests/schemas/gic720ae-pcie-its-profile.schema.json",
)


def load_builder():
    spec = importlib.util.spec_from_file_location(SCRIPT.stem, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stale_records(tmp_path: Path, roles: tuple[str, ...]) -> list[dict[str, str]]:
    records = []
    for index, role in enumerate(roles):
        path = tmp_path / f"source-{index}"
        path.write_text(f"current-{index}", encoding="utf-8")
        records.append({"role": role, "path": str(path), "sha256": "0" * 64})
    return records


def test_old_pass_with_live_source_delta_is_not_launchable(tmp_path: Path) -> None:
    builder = load_builder()
    records = stale_records(tmp_path, (REMEDIATION_ROLES[0],))
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_launchable_source_closure(records)
    assert error.value.reason == "stale_source_hashes"


def test_stale_tool_source_cannot_keep_valid_claim(tmp_path: Path) -> None:
    builder = load_builder()
    records = stale_records(tmp_path, (REMEDIATION_ROLES[0],))
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_source_hash_claim(records, claimed_valid=True)
    assert error.value.reason == "false_source_hashes_valid_claim"


def test_authoritative_refresh_accepts_exact_path_remediation(tmp_path: Path) -> None:
    builder = load_builder()
    records = stale_records(tmp_path, REMEDIATION_ROLES)
    deltas = builder.authorize_path_containment_refresh(records)
    assert [item["role"] for item in deltas] == list(REMEDIATION_ROLES)
    assert {item["classification"] for item in deltas} == {"tool_postprocessor"}
    assert {item["reason"] for item in deltas} == {"path_containment_remediation"}


def test_authoritative_refresh_rejects_arbitrary_tool_delta(tmp_path: Path) -> None:
    builder = load_builder()
    roles = (*REMEDIATION_ROLES, "scripts/test/gic720ae_pcie_its_profile/build.py")
    records = stale_records(tmp_path, roles)
    with pytest.raises(builder.ProfileError) as error:
        builder.authorize_path_containment_refresh(records)
    assert error.value.reason == "unauthorized_source_delta"


def test_authoritative_refresh_rejects_real_build_input_delta(tmp_path: Path) -> None:
    builder = load_builder()
    roles = (
        *REMEDIATION_ROLES,
        "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc",
    )
    records = stale_records(tmp_path, roles)
    with pytest.raises(builder.ProfileError) as error:
        builder.authorize_path_containment_refresh(records)
    assert error.value.reason == "immutable_build_input_changed"


@pytest.mark.parametrize(
    ("validator", "reason"),
    (("validate_task_sigdata_records", "stale_task_sigdata"),
     ("validate_artifact_records", "stale_artifact")),
)
def test_authoritative_refresh_rejects_immutable_hash_mutation(
    tmp_path: Path,
    validator: str,
    reason: str,
) -> None:
    builder = load_builder()
    path = tmp_path / validator
    path.write_text("current", encoding="utf-8")
    record = {"role": validator, "path": str(path), "sha256": "0" * 64}
    with pytest.raises(builder.ProfileError) as error:
        getattr(builder, validator)([record])
    assert error.value.reason == reason


def test_refreshed_live_source_closure_accepts_current_hash(tmp_path: Path) -> None:
    builder = load_builder()
    path = tmp_path / "current"
    path.write_text("current", encoding="utf-8")
    records = [{"role": "tool", "path": str(path), "sha256": digest(path)}]
    builder.validate_launchable_source_closure(records)

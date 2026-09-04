from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Final, NoReturn

try:
    import gic720ae_pcie_irq_validation_ap_map as ap_map
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_inventory as inventory
    import gic720ae_pcie_irq_validation_repository as repository
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_inventory as inventory
    from scripts.test import gic720ae_pcie_irq_validation_repository as repository


SOURCE_PATHS = inventory.SOURCE_PATHS
REPOSITORIES = inventory.REPOSITORIES
COMMANDS: Final = (
    "./yocto_build.sh --bsp",
    "python3 scripts/test/audit_qbox_apollo_ap_memory_map.py --output ${RUN_ROOT}/ap-map-audit.json",
    "python3 scripts/test/run_gic720ae_pcie_irq_validation_task9.py --fvp-reference-gate ${FVP_GATE} --qbox-profile-manifest ${QBOX_PROFILE} --run-root ${RUN_ROOT}/task9 --ap-map-audit ${RUN_ROOT}/ap-map-audit.json --ap-map-audit-sha256 ${AP_MAP_SHA256} --ap-map-audit-size ${AP_MAP_SIZE}",
    "python3 scripts/test/run_gic720ae_pcie_irq_validation_task10.py --fvp-reference-gate ${FVP_GATE} --qbox-profile-manifest ${QBOX_PROFILE} --qbox-run-root ${RUN_ROOT}/task9 --output ${RUN_ROOT}/boundary-comparison.json",
)
AP_MAP_ROLE: Final = "${RUN_LOCAL_AP_MAP}"


def file_entry(path: Path, expected: str | None = None) -> contract.JsonObject:
    actual = contract.digest(path)
    if expected is not None and actual != expected:
        raise contract.ValidationError(f"provenance_file_sha256:{path}")
    return {"path": str(path.resolve()), "sha256": actual, "size": path.stat().st_size}


def binary_identity(path: Path) -> contract.JsonObject:
    absolute = path.absolute()
    if path.is_symlink():
        raise contract.ValidationError("qbox_binary_symlink")
    if not path.is_file():
        return {"status": "MISSING", "path": str(absolute)}
    return {
        "status": "PRESENT",
        "path": str(absolute),
        "sha256": contract.digest(path),
    }


def build(config: contract.RunConfig) -> contract.JsonObject:
    contract.validate_gate(config.gate)
    _, profile_files = contract.profile_bindings(config.profile)
    files: dict[str, contract.JsonValue] = {
        "fvp_reference_gate": file_entry(config.gate, contract.GATE_SHA256),
        "qbox_profile_manifest": file_entry(config.profile, contract.PROFILE_SHA256),
    }
    for name, (path, expected) in sorted(profile_files.items()):
        files[name] = file_entry(path, expected)
    for relative in SOURCE_PATHS:
        files[f"source_{relative.replace('/', '_')}"] = file_entry(
            contract.ROOT / relative
        )
    files["qbox_config"] = file_entry(contract.QBOX_CONFIG)
    repositories: dict[str, contract.JsonValue] = {}
    for name, (relative, scopes) in REPOSITORIES.items():
        repositories[name] = repository.capture(
            contract.ROOT / relative,
            scopes,
            expected_clean=name in ("qbox_core", "qemu"),
        )
    payload: contract.JsonObject = {
        "schema_version": 1,
        "status": "PASS",
        "closure_state": "PRE_AUDIT",
        "fvp_qualification": "UNSUPPORTED",
        "files": files,
        "repositories": repositories,
        "qbox_binary": binary_identity(config.qbox_binary),
        "ap_memory_map_audit": {"status": "NOT_RUN"},
        "command_order": list(COMMANDS),
    }
    contract.validate_schema(payload, contract.PROVENANCE_SCHEMA, "provenance_schema")
    return payload


def bind_ap_map_audit(
    payload: contract.JsonObject,
    config: contract.RunConfig,
    artifact: ap_map.ApMapArtifact,
) -> contract.JsonObject:
    if artifact.path != ap_map.expected_path(config.run_root):
        raise contract.ValidationError("ap_memory_map_audit_path")
    ap_map.require_current(artifact, config.run_root, "ap_memory_map_audit")
    bound = dict(payload)
    bound["closure_state"] = "AUDIT_BOUND"
    bound["ap_memory_map_audit"] = artifact.binding()
    contract.validate_schema(bound, contract.PROVENANCE_SCHEMA, "provenance_schema")
    return bound


def raise_frozen_mismatch(
    reason: str, current_bytes: bytes, frozen_bytes: bytes
) -> NoReturn:
    current_sha = hashlib.sha256(current_bytes).hexdigest()
    frozen_sha = hashlib.sha256(frozen_bytes).hexdigest()
    raise contract.ValidationError(
        f"{reason}:"
        f"current_sha256={current_sha}:current_size={len(current_bytes)}:"
        f"frozen_sha256={frozen_sha}:frozen_size={len(frozen_bytes)}"
    )


def validated_ap_map_binding(
    payload: contract.JsonObject, root: Path, role: str
) -> ap_map.ApMapArtifact | None:
    if payload.get("closure_state") == "PRE_AUDIT":
        return None
    entry = contract.object_value(
        payload.get("ap_memory_map_audit"), f"{role}_ap_map_identity"
    )
    artifact_path = Path(
        contract.string_value(entry.get("path"), f"{role}_ap_map_path")
    )
    if artifact_path.absolute() != ap_map.expected_path(root):
        raise contract.ValidationError(f"{role}_ap_map_path")
    try:
        artifact = ap_map.load(artifact_path, root, f"{role}_ap_map_path")
    except contract.ValidationError as error:
        if str(error).endswith("_passed"):
            raise contract.ValidationError(f"{role}_ap_map_identity") from error
        raise
    expected_sha = contract.string_value(
        entry.get("sha256"), f"{role}_ap_map_identity"
    )
    expected_size = entry.get("size")
    if not isinstance(expected_size, int) or isinstance(expected_size, bool):
        raise contract.ValidationError(f"{role}_ap_map_identity")
    if artifact.sha256 != expected_sha or artifact.size != expected_size:
        raise contract.ValidationError(f"{role}_ap_map_identity")
    return artifact


def ap_map_role_projection(payload: contract.JsonObject) -> contract.JsonObject:
    binding = contract.object_value(
        payload.get("ap_memory_map_audit"), "provenance_ap_map_identity"
    )
    projected = dict(payload)
    projected["ap_memory_map_audit"] = {**binding, "path": AP_MAP_ROLE}
    return projected


def compare_frozen(
    payload: contract.JsonObject, path: Path, current_root: Path
) -> None:
    contract.validate_schema(
        payload, contract.PROVENANCE_SCHEMA, "current_provenance_schema"
    )
    frozen = contract.load_object(path, "frozen_provenance_json")
    contract.validate_schema(
        frozen, contract.PROVENANCE_SCHEMA, "frozen_provenance_schema"
    )
    frozen_bytes = path.read_bytes()
    canonical_frozen = canonical_bytes(frozen)
    if frozen_bytes != canonical_frozen:
        raise_frozen_mismatch(
            "frozen_provenance_bytes", canonical_frozen, frozen_bytes
        )
    current_state = payload.get("closure_state")
    frozen_state = frozen.get("closure_state")
    current_ap_map = validated_ap_map_binding(payload, current_root, "current")
    frozen_ap_map = validated_ap_map_binding(frozen, path.parent, "frozen")
    current_projection = payload
    frozen_projection = frozen
    if current_state == "PRE_AUDIT" and frozen_state == "AUDIT_BOUND":
        preaudit_frozen = dict(frozen)
        preaudit_frozen["closure_state"] = "PRE_AUDIT"
        preaudit_frozen["ap_memory_map_audit"] = {"status": "NOT_RUN"}
        frozen_projection = preaudit_frozen
    elif current_state == "AUDIT_BOUND" and frozen_state == "AUDIT_BOUND":
        if current_ap_map is None or frozen_ap_map is None:
            raise contract.ValidationError("frozen_provenance_ap_map_identity")
        if (
            current_ap_map.sha256 != frozen_ap_map.sha256
            or current_ap_map.size != frozen_ap_map.size
        ):
            raise contract.ValidationError("frozen_provenance_ap_map_identity")
        current_projection = ap_map_role_projection(payload)
        frozen_projection = ap_map_role_projection(frozen)
    elif current_state != frozen_state:
        raise contract.ValidationError("frozen_provenance_transition")
    current_bytes = canonical_bytes(current_projection)
    projected_frozen_bytes = canonical_bytes(frozen_projection)
    if projected_frozen_bytes != current_bytes:
        raise_frozen_mismatch(
            "frozen_provenance_drift", current_bytes, projected_frozen_bytes
        )


def canonical_bytes(payload: contract.JsonObject) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: contract.JsonObject) -> None:
    if path.is_symlink():
        raise contract.ValidationError("output_path_symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
        stream.write(canonical_bytes(payload))
        temporary = Path(stream.name)
    os.replace(temporary, path)


def empty_for_test(qbox_binary: Path) -> contract.JsonObject:
    return {"schema_version": 1, "qbox_binary": binary_identity(qbox_binary)}


def assert_unchanged(config: contract.RunConfig, expected: contract.JsonObject) -> None:
    current = build(config)
    entry = contract.object_value(
        expected.get("ap_memory_map_audit"), "ap_memory_map_audit_binding"
    )
    if entry.get("status") != "NOT_RUN":
        path = Path(
            contract.string_value(entry.get("path"), "ap_memory_map_audit_path")
        )
        size = entry.get("size")
        if not isinstance(size, int) or isinstance(size, bool):
            raise contract.ValidationError("ap_memory_map_audit_size")
        expected_digest = ap_map.ExpectedDigest(
            contract.string_value(entry.get("sha256"), "ap_memory_map_audit_sha256"),
            size,
        )
        artifact = ap_map.task11_artifact(config.run_root, path, expected_digest)
        current = bind_ap_map_audit(current, config, artifact)
    if current != expected:
        raise contract.ValidationError("provenance_changed")
    if config.frozen_provenance is not None:
        compare_frozen(current, config.frozen_provenance, config.run_root)

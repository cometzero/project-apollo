from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import gic720ae_pcie_irq_validation_contract as contract
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract


@dataclass(frozen=True, slots=True)
class ApMapArtifact:
    path: Path
    sha256: str
    size: int

    def binding(self) -> contract.JsonObject:
        return {
            "path": str(self.path),
            "sha256": self.sha256,
            "size": self.size,
        }


@dataclass(frozen=True, slots=True)
class ExpectedDigest:
    sha256: str
    size: int


def expected_path(evidence_root: Path) -> Path:
    return evidence_root.absolute() / "ap-map-audit.json"


def contained_file(path: Path, root: Path, reason: str) -> Path:
    if ".." in path.parts or path.is_symlink():
        raise contract.ValidationError(reason)
    absolute = path.absolute()
    boundary = root.absolute()
    try:
        absolute.relative_to(boundary)
    except ValueError as error:
        raise contract.ValidationError(reason) from error
    current = absolute.parent
    while current != boundary:
        if current.is_symlink():
            raise contract.ValidationError(reason)
        parent = current.parent
        if parent == current:
            raise contract.ValidationError(reason)
        current = parent
    if boundary.is_symlink():
        raise contract.ValidationError(reason)
    if not absolute.is_file():
        raise contract.ValidationError(f"{reason}_json")
    resolved = absolute.resolve()
    if resolved != absolute:
        raise contract.ValidationError(reason)
    return resolved


def load(path: Path, root: Path, reason: str) -> ApMapArtifact:
    resolved = contained_file(path, root, reason)
    payload = contract.load_object(resolved, f"{reason}_json")
    if payload.get("passed") is not True:
        raise contract.ValidationError(f"{reason}_passed")
    return ApMapArtifact(resolved, contract.digest(resolved), resolved.stat().st_size)


def task11_artifact(
    evidence_root: Path,
    path: Path,
    expected: ExpectedDigest | None = None,
) -> ApMapArtifact:
    expected_receipt = expected_path(evidence_root)
    if path.absolute() != expected_receipt:
        raise contract.ValidationError("task9_ap_map_path")
    artifact = load(path, evidence_root, "task9_ap_map")
    if expected is not None and artifact.sha256 != expected.sha256:
        raise contract.ValidationError("task9_ap_map_sha256")
    if expected is not None and artifact.size != expected.size:
        raise contract.ValidationError("task9_ap_map_size")
    return artifact


def require_current(artifact: ApMapArtifact, root: Path, reason: str) -> None:
    current = load(artifact.path, root, reason)
    if current.sha256 != artifact.sha256:
        raise contract.ValidationError(f"{reason}_sha256")
    if current.size != artifact.size:
        raise contract.ValidationError(f"{reason}_size")


def validate_coverage(
    coverage_path: Path, artifact: ApMapArtifact
) -> contract.JsonObject:
    coverage = contract.load_object(coverage_path, "task9_coverage_json")
    memory = contract.object_value(coverage.get("ap_9_1_1_memory_map"), "task9_ap_map")
    cited = Path(contract.string_value(memory.get("audit_path"), "task9_ap_map"))
    if coverage.get("passed") is not True or memory.get("passed") is not True:
        raise contract.ValidationError("task9_ap_map_passed")
    if cited.absolute() != artifact.path:
        raise contract.ValidationError("task9_ap_map_path")
    require_current(artifact, artifact.path.parent, "task9_ap_map")
    return coverage

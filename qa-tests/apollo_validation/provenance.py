from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Literal, TypeAlias, TypedDict

from .backend import Backend, ImageProfile
from .source_revisions import capture_source_revisions
from .validation_matrix import load_validation_matrix
from .validation_types import CoverageKind


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
RuntimeKind: TypeAlias = Literal["testdata", "runtime_config", "image_artifact"]
MATRIX_RELATIVE = Path("qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml")


class SharedInputJson(TypedDict):
    path: str
    git_blob_sha256: str


class RuntimeInputJson(TypedDict):
    kind: RuntimeKind
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class ProvenanceError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class SharedInput:
    path: str
    git_blob_sha256: str

    def as_json(self) -> SharedInputJson:
        return {"path": self.path, "git_blob_sha256": self.git_blob_sha256}


@dataclass(frozen=True, slots=True)
class RuntimeInput:
    kind: RuntimeKind
    path: Path
    sha256: str

    def as_json(self) -> RuntimeInputJson:
        return {"kind": self.kind, "path": str(self.path), "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class ProfileProvenance:
    profile_id: str
    profile_snapshot_sha256: str
    semantic_profile_digest: str
    selectors: tuple[str, ...]
    expected_assertion_ids: tuple[str, ...]
    coverage_kind: CoverageKind
    machine: str
    image: str
    image_profile: ImageProfile
    cpu_count: int
    shared_inputs: tuple[SharedInput, ...]
    runtime_inputs: tuple[RuntimeInput, ...]
    source_revisions: tuple[tuple[str, str], ...]

    def as_json(self) -> dict[str, JsonValue]:
        shared_inputs: list[JsonValue] = []
        runtime_inputs: list[JsonValue] = []
        for item in self.shared_inputs:
            shared_inputs.append(
                {"path": item.path, "git_blob_sha256": item.git_blob_sha256}
            )
        for item in self.runtime_inputs:
            runtime_inputs.append(
                {"kind": item.kind, "path": str(item.path), "sha256": item.sha256}
            )
        return {
            "version": 1,
            "profile_id": self.profile_id,
            "profile_snapshot_sha256": self.profile_snapshot_sha256,
            "semantic_profile_digest": self.semantic_profile_digest,
            "selectors": list(self.selectors),
            "expected_assertion_ids": list(self.expected_assertion_ids),
            "coverage_kind": self.coverage_kind,
            "machine": self.machine,
            "image": self.image,
            "image_profile": self.image_profile,
            "cpu_count": self.cpu_count,
            "shared_inputs": shared_inputs,
            "runtime_inputs": runtime_inputs,
            "source_revisions": dict(self.source_revisions),
        }


@dataclass(frozen=True, slots=True)
class ProvenanceRequest:
    root: Path
    build_dir: Path
    backend: Backend
    machine: str
    image: str
    image_profile: ImageProfile
    profile_id: str
    selectors: tuple[str, ...]
    cpu_count: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_output(path: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise ProvenanceError("blocked_fvp_reference_shared_input_drift")
    return result.stdout


def _shared_input(root: Path, path: Path) -> SharedInput:
    repository = Path(_git_output(path.parent, "rev-parse", "--show-toplevel").decode().strip())
    relative_to_repository = path.relative_to(repository)
    blob = _git_output(repository, "show", f"HEAD:{relative_to_repository}")
    current = path.read_bytes()
    if current != blob:
        raise ProvenanceError("blocked_fvp_reference_shared_input_drift")
    relative_to_root = str(path.relative_to(root))
    return SharedInput(relative_to_root, sha256_bytes(blob))


def _selector_path(root: Path, selector: str) -> Path:
    module = selector.split(".", maxsplit=1)[0]
    candidates = tuple(
        path
        for layer in ("meta-hsoc-bsp", "meta-hsoc-auto-solutions")
        if (
            path := root
            / f"hsoc-stack/yocto/{layer}/lib/oeqa/runtime/cases/{module}.py"
        ).is_file()
    )
    if len(candidates) != 1:
        raise ProvenanceError("blocked_fvp_reference_shared_input_drift")
    return candidates[0]


def _runtime_path(request: ProvenanceRequest, suffix: str) -> Path:
    build_dir = request.build_dir if request.build_dir.is_absolute() else request.root / request.build_dir
    deploy = build_dir / "tmp_baremetal/deploy/images" / request.machine
    return deploy / f"{request.image}-{request.machine}.{suffix}"


def _runtime_inputs(request: ProvenanceRequest) -> tuple[RuntimeInput, ...]:
    runtime_suffix = "fvpconf" if request.backend == "fvp" else "qboxconf"
    paths: tuple[tuple[RuntimeKind, Path], ...] = (
        ("testdata", _runtime_path(request, "testdata.json")),
        ("runtime_config", _runtime_path(request, runtime_suffix)),
        ("image_artifact", _runtime_path(request, "wic")),
    )
    identities: list[RuntimeInput] = []
    for kind, path in paths:
        try:
            resolved = path.resolve(strict=True)
            data = resolved.read_bytes()
        except (FileNotFoundError, OSError) as error:
            raise ProvenanceError(f"blocked_fvp_reference_{kind}_drift") from error
        identities.append(RuntimeInput(kind, resolved, sha256_bytes(data)))
    return tuple(identities)


def capture_profile_provenance(request: ProvenanceRequest) -> ProfileProvenance:
    matrix_path = request.root / MATRIX_RELATIVE
    matrix = load_validation_matrix(matrix_path)
    profile = next(
        (item for item in matrix.profiles if item.profile_id == request.profile_id),
        None,
    )
    if profile is None:
        raise ProvenanceError("blocked_fvp_reference_profile_mismatch")
    if profile.image != request.image_profile:
        raise ProvenanceError("blocked_fvp_reference_image_mismatch")
    if profile.cpu_count != request.cpu_count:
        raise ProvenanceError("blocked_fvp_reference_cpu_mismatch")
    profile_path = request.root / f"qa-tests/profiles/{request.profile_id}.yaml"
    shared_paths = (
        matrix_path,
        profile_path,
        *(_selector_path(request.root, item) for item in request.selectors),
    )
    shared: list[SharedInput] = []
    for path in shared_paths:
        shared.append(_shared_input(request.root, path))
    shared_json: list[JsonValue] = []
    for item in shared:
        shared_json.append(
            {"path": item.path, "git_blob_sha256": item.git_blob_sha256}
        )
    semantic: dict[str, JsonValue] = {
        "profile_id": request.profile_id,
        "image_profile": request.image_profile,
        "cpu_count": request.cpu_count,
        "selectors": list(request.selectors),
        "expected_assertion_ids": list(profile.qbox_assertions),
        "coverage_kind": profile.coverage_kind,
        "shared_inputs": shared_json,
    }
    semantic_bytes = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    return ProfileProvenance(
        request.profile_id,
        sha256_bytes(profile_path.read_bytes()),
        sha256_bytes(semantic_bytes),
        request.selectors,
        profile.qbox_assertions,
        profile.coverage_kind,
        request.machine,
        request.image,
        request.image_profile,
        request.cpu_count,
        tuple(shared),
        _runtime_inputs(request),
        capture_source_revisions(request.root, request.backend),
    )

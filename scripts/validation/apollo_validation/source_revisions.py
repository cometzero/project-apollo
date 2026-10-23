from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Final

from .backend import Backend


MIXED_KEYS: Final = ("workspace", "qa_runner")
SHARED_KEYS: Final = ("bsp_layer", "platform_layer")
QBOX_ONLY_KEYS: Final = ("qbox_core", "qbox_platform", "qemu")
QVP_ONLY_BSP_PATHS: Final = frozenset(
    {
        "conf/machine/apollo-qvp.conf",
        "recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg",
        "hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf",
        "hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/"
        "apollo-qvp-auto-ad-nexios.cfg",
    }
)
FVP_KEYS: Final = frozenset((*MIXED_KEYS, *SHARED_KEYS))
QBOX_KEYS: Final = frozenset((*FVP_KEYS, *QBOX_ONLY_KEYS))
REVISION_PATTERN: Final = re.compile(r"[0-9a-f]{40}")
REPOSITORIES: Final = {
    "workspace": Path("."),
    "qa_runner": Path("."),
    "bsp_layer": Path("hsoc-stack/yocto/meta-hsoc-bsp"),
    "platform_layer": Path("hsoc-stack/yocto/meta-hsoc-auto-solutions"),
    "qbox_core": Path("hsoc-stack/tools/qbox"),
    "qbox_platform": Path("hsoc-stack/tools/qbox-platform"),
    "qemu": Path("hsoc-stack/tools/qemu"),
}


@dataclass(frozen=True, slots=True)
class SourceRevisionError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def _git(repository: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )


def _head(root: Path, key: str) -> str:
    repository = root / REPOSITORIES[key]
    result = _git(repository, "rev-parse", "HEAD")
    revision = result.stdout.decode().strip()
    if result.returncode != 0 or REVISION_PATTERN.fullmatch(revision) is None:
        raise SourceRevisionError("blocked_fvp_reference_source_revision_nonexistent")
    return revision


def capture_source_revisions(
    root: Path,
    backend: Backend,
) -> tuple[tuple[str, str], ...]:
    keys_by_backend: dict[Backend, frozenset[str]] = {
        "fvp": FVP_KEYS,
        "qbox": QBOX_KEYS,
    }
    keys = keys_by_backend[backend]
    return tuple((key, _head(root, key)) for key in sorted(keys))


def _require_commit(root: Path, key: str, revision: str) -> None:
    repository = root / REPOSITORIES[key]
    result = _git(repository, "cat-file", "-e", f"{revision}^{{commit}}")
    if result.returncode != 0:
        raise SourceRevisionError("blocked_fvp_reference_source_revision_nonexistent")


def _require_ancestor(root: Path, key: str, older: str, current: str) -> None:
    repository = root / REPOSITORIES[key]
    result = _git(repository, "merge-base", "--is-ancestor", older, current)
    if result.returncode != 0:
        raise SourceRevisionError("blocked_fvp_reference_source_revision_non_ancestor")


def _require_allowlisted_ancestor(
    root: Path,
    key: str,
    older: str,
    current: str,
    allowed_paths: frozenset[str],
) -> None:
    _require_ancestor(root, key, older, current)
    repository = root / REPOSITORIES[key]
    result = _git(repository, "diff", "--name-only", f"{older}..{current}")
    changed = frozenset(result.stdout.decode().splitlines())
    if result.returncode != 0 or not changed <= allowed_paths:
        raise SourceRevisionError(
            "blocked_fvp_reference_source_revision_shared_drift"
        )


def validate_fvp_source_revisions(
    root: Path,
    reference: dict[str, str],
    current: tuple[tuple[str, str], ...],
    shared_contract_matches: bool,
) -> None:
    reference_keys = set(reference)
    missing = FVP_KEYS - reference_keys
    if missing:
        raise SourceRevisionError("blocked_fvp_reference_source_revision_missing")
    unexpected = reference_keys - FVP_KEYS
    if unexpected:
        raise SourceRevisionError("blocked_fvp_reference_source_revision_unexpected")
    if any(REVISION_PATTERN.fullmatch(value) is None for value in reference.values()):
        raise SourceRevisionError("blocked_fvp_reference_source_revision_malformed")
    current_by_key = dict(current)
    if not QBOX_KEYS <= set(current_by_key):
        raise SourceRevisionError("blocked_fvp_reference_source_revision_missing")
    for key, revision in reference.items():
        _require_commit(root, key, revision)
    for key in SHARED_KEYS:
        revision = reference[key]
        current_revision = current_by_key[key]
        if revision == current_revision:
            continue
        if key == "bsp_layer" and shared_contract_matches:
            _require_allowlisted_ancestor(
                root,
                key,
                revision,
                current_revision,
                QVP_ONLY_BSP_PATHS,
            )
            continue
        raise SourceRevisionError(
            "blocked_fvp_reference_source_revision_shared_drift"
        )
    for key in MIXED_KEYS:
        revision = reference[key]
        current_revision = current_by_key[key]
        if revision == current_revision:
            continue
        if not shared_contract_matches:
            raise SourceRevisionError(
                "blocked_fvp_reference_source_revision_shared_drift"
            )
        _require_ancestor(root, key, revision, current_revision)

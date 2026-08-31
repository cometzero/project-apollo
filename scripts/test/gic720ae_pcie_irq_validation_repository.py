from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Final

try:
    import gic720ae_pcie_irq_validation_contract as contract
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract


HEAD_RE: Final = re.compile(r"^[0-9a-f]{40}$")


def _git(root: Path, arguments: tuple[str, ...]) -> bytes:
    result = subprocess.run(
        ("git", "-C", str(root), *arguments), capture_output=True, check=False
    )
    if result.returncode != 0:
        raise contract.ValidationError(
            f"repository_git:{root}:{arguments[0]}:{result.returncode}"
        )
    return result.stdout


def _scope(root: Path, scope_paths: tuple[str, ...]) -> tuple[str, ...]:
    if not scope_paths:
        raise contract.ValidationError("repository_scope:empty")
    checked: list[str] = []
    for raw in scope_paths:
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts or raw in ("", "."):
            raise contract.ValidationError(f"repository_scope:{raw}")
        candidate = root / relative
        if candidate.exists() and not candidate.resolve().is_relative_to(root):
            raise contract.ValidationError(f"repository_scope:{raw}")
        checked.append(relative.as_posix())
    return tuple(sorted(set(checked)))


def _binding(data: bytes) -> contract.JsonObject:
    return {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def _decode_paths(data: bytes, reason: str) -> list[str]:
    try:
        return sorted(entry.decode("utf-8") for entry in data.split(b"\0") if entry)
    except UnicodeDecodeError as error:
        raise contract.ValidationError(reason) from error


def _untracked(root: Path, paths: tuple[str, ...]) -> list[contract.JsonValue]:
    names = _decode_paths(
        _git(root, ("ls-files", "--others", "--exclude-standard", "-z", "--", *paths)),
        "repository_untracked_encoding",
    )
    entries: list[contract.JsonValue] = []
    for name in names:
        source = root / name
        if source.is_symlink() or not source.is_file():
            raise contract.ValidationError(f"repository_untracked:{name}")
        entries.append(
            {
                "path": name,
                "sha256": contract.digest(source),
                "size": source.stat().st_size,
            }
        )
    return entries


def _status(root: Path, paths: tuple[str, ...]) -> list[contract.JsonValue]:
    raw = _git(
        root,
        ("status", "--porcelain=v1", "-z", "--untracked-files=all", "--", *paths),
    )
    records = [record for record in raw.split(b"\0") if record]
    entries: list[contract.JsonValue] = []
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4 or record[2:3] != b" ":
            raise contract.ValidationError("repository_status_format")
        try:
            code = record[:2].decode("ascii")
            path = record[3:].decode("utf-8")
        except UnicodeDecodeError as error:
            raise contract.ValidationError("repository_status_encoding") from error
        entry: contract.JsonObject = {"code": code, "path": path}
        if code[0] in ("R", "C") or code[1] in ("R", "C"):
            index += 1
            if index >= len(records):
                raise contract.ValidationError("repository_status_rename")
            try:
                entry["original_path"] = records[index].decode("utf-8")
            except UnicodeDecodeError as error:
                raise contract.ValidationError("repository_status_encoding") from error
        entries.append(entry)
        index += 1
    return entries


def capture(
    root: Path, scope_paths: tuple[str, ...], *, expected_clean: bool = False
) -> contract.JsonObject:
    resolved = root.resolve(strict=True)
    paths = _scope(resolved, scope_paths)
    head = _git(resolved, ("rev-parse", "HEAD")).decode("ascii").strip()
    if HEAD_RE.fullmatch(head) is None:
        raise contract.ValidationError(f"repository_sha:{root}")
    staged = _git(
        resolved, ("diff", "--cached", "--binary", "--no-ext-diff", "--", *paths)
    )
    worktree = _git(resolved, ("diff", "--binary", "--no-ext-diff", "--", *paths))
    untracked = _untracked(resolved, paths)
    manifest = (
        json.dumps(untracked, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    status = _status(resolved, paths)
    if expected_clean and status:
        raise contract.ValidationError(f"repository_expected_clean:{root}")
    return {
        "path": str(resolved),
        "head": head,
        "scope_paths": list(paths),
        "expected_state": "CLEAN" if expected_clean else "DIRTY_ALLOWED",
        "staged_diff": _binding(staged),
        "worktree_diff": _binding(worktree),
        "untracked_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "untracked_sources": untracked,
        "status_entries": status,
    }


def assert_same(
    root: Path, scope_paths: tuple[str, ...], expected: contract.JsonObject
) -> None:
    if capture(root, scope_paths) != expected:
        raise contract.ValidationError("provenance_changed")

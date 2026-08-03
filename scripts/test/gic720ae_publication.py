#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
# ─── How to run ───
# 1. Run: python3 scripts/test/gic720ae_publication.py
# 2. This module is imported by run_gic720ae_github_push.py.
# ──────────────────
"""Structural remote identity and publication-order policy."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import subprocess
from urllib.parse import urlparse

from gic720ae_contract import ContractError, JsonValue


def git(cwd: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *arguments],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("git_failed", result.stderr.strip())
    return result.stdout.strip()


def remote_identity(remote_url: str) -> tuple[str, str, str]:
    if "://" in remote_url:
        parsed = urlparse(remote_url)
        if parsed.hostname is None:
            raise ContractError("third_party_remote", remote_url)
        host = parsed.hostname.lower()
        path = parsed.path
    elif ":" in remote_url and not remote_url.startswith("/"):
        authority, path = remote_url.split(":", 1)
        host = authority.rsplit("@", 1)[-1].lower()
    else:
        remote_path = Path(remote_url).resolve()
        return "local", str(remote_path.parent), remote_path.name.removesuffix(".git")
    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ContractError("third_party_remote", remote_url)
    return host, parts[-2], parts[-1].removesuffix(".git")


def validate_repository_policy(
    repositories: Sequence[JsonValue],
    owner: str,
    *,
    resolve_remote_url: bool,
) -> None:
    selected = [
        item for item in repositories
        if isinstance(item, dict) and item.get("selected")
    ]
    for item in selected:
        if not item.get("changed"):
            raise ContractError(
                "unchanged_repository_selected", str(item.get("path"))
            )
    orders = [item.get("order") for item in selected]
    if orders != list(range(len(selected))):
        raise ContractError("invalid_publication_order", str(orders))
    top_indexes = [
        index for index, item in enumerate(selected) if item.get("path") == "."
    ]
    if top_indexes and top_indexes != [len(selected) - 1]:
        raise ContractError("top_repository_not_last", ".")
    for item in selected:
        remote_url = (
            git(
                Path(str(item.get("path"))), "remote", "get-url",
                str(item.get("remote")),
            )
            if resolve_remote_url
            else str(item.get("remote_url", ""))
        )
        identity = remote_identity(remote_url)
        recorded = (
            item.get("remote_host"), item.get("remote_owner"),
            item.get("remote_repo"),
        )
        if not owner or identity[1] != owner or recorded != identity:
            raise ContractError("third_party_remote", str(item.get("path")))
        if item.get("remote_url") != remote_url:
            raise ContractError("stale_manifest", str(item.get("path")))


if __name__ == "__main__":
    raise SystemExit(0)

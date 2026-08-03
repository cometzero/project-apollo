#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/run_gic720ae_github_push.py --help
# 3. Or: python3 scripts/test/run_gic720ae_github_push.py --help
# ──────────────────
"""Publish only changed owned repositories in nested-before-top order."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

from gic720ae_contract import (
    ContractError, JsonArray, JsonObject, json_object, validate, write_json,
)
from gic720ae_publication import (
    git, remote_identity, validate_repository_policy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--self-test-bare-remote", action="store_true")
    parser.add_argument("--mode", choices=("audit", "dry-run", "push"))
    parser.add_argument("--owner")
    parser.add_argument("--helper-audit-log", type=Path)
    parser.add_argument("--initial-state", type=Path)
    parser.add_argument("--source-freeze", type=Path)
    parser.add_argument("--report-only-digest", type=Path)
    parser.add_argument("--commit-audit", type=Path)
    parser.add_argument("--verify-remote-sha", action="store_true")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("tests/schemas/gic720ae-publication.schema.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def negative(path: Path) -> str:
    fixture = json_object(path)
    repositories = fixture.get("repositories")
    owner = fixture.get("owner", "owner")
    if not isinstance(repositories, list) or not isinstance(owner, str):
        return "malformed_fixture"
    try:
        validate_repository_policy(repositories, owner, resolve_remote_url=False)
        for item in repositories:
            if (
                isinstance(item, dict)
                and item.get("selected")
                and item.get("remote_sha")
                and item.get("remote_sha") != item.get("local_sha")
            ):
                raise ContractError("remote_sha_mismatch", str(item.get("path")))
    except ContractError as error:
        return error.reason
    return "malformed_fixture"


def init_repo(path: Path, remote: Path, content: str) -> str:
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.name", "Task Five")
    git(path, "config", "user.email", "task5@example.invalid")
    (path / "state").write_text(content, encoding="utf-8")
    git(path, "add", "state")
    git(path, "commit", "-q", "-m", "initial")
    git(path, "remote", "add", "owned", str(remote))
    return git(path, "rev-parse", "HEAD")


def bare_remote_self_test() -> JsonObject:
    with tempfile.TemporaryDirectory(prefix="gic720ae-publication-") as temporary:
        root = Path(temporary)
        nested_remote = root / "nested.git"
        top_remote = root / "top.git"
        unchanged_remote = root / "unchanged.git"
        for remote in (nested_remote, top_remote, unchanged_remote):
            remote.mkdir()
            git(remote, "init", "-q", "--bare")
        nested = root / "nested"
        top = root / "top"
        unchanged = root / "unchanged"
        init_repo(nested, nested_remote, "nested")
        init_repo(top, top_remote, "top")
        unchanged_sha = init_repo(unchanged, unchanged_remote, "unchanged")
        before = {
            "nested": git(nested, "ls-remote", "owned", "refs/heads/main"),
            "top": git(top, "ls-remote", "owned", "refs/heads/main"),
        }
        order: list[tuple[str, Path]] = [("nested", nested), ("top", top)]
        dry_repositories: JsonArray = [
            {
                "path": str(repo), "changed": True, "selected": True,
                "order": index, "local_sha": git(repo, "rev-parse", "HEAD"),
                "remote_sha": "", "remote": "owned",
                "remote_url": str((nested_remote, top_remote)[index]),
                "remote_host": "local", "remote_owner": str(root),
                "remote_repo": name, "branch": "main",
            }
            for index, (name, repo) in enumerate(order)
        ]
        dry_manifest = root / "dry-manifest.json"
        write_json(dry_manifest, {
            "format_version": 1, "verdict": "PASS",
            "reason": "manifest_audited", "mode": "audit",
            "repositories": dry_repositories,
        })
        dry_args = argparse.Namespace(
            manifest=dry_manifest, mode="dry-run", owner=str(root),
            schema=Path("tests/schemas/gic720ae-publication.schema.json"),
            verify_remote_sha=False,
        )
        manifest_run(dry_args)
        after_dry_run = {
            "nested": git(nested, "ls-remote", "owned", "refs/heads/main"),
            "top": git(top, "ls-remote", "owned", "refs/heads/main"),
        }
        if before != after_dry_run:
            raise ContractError("dry_run_modified_remote", "remote state")
        repositories: JsonArray = []
        for index, (name, repo) in enumerate(order):
            local_sha = git(repo, "rev-parse", "HEAD")
            git(repo, "push", "owned", "HEAD:main")
            remote_sha = git(repo, "ls-remote", "owned", "refs/heads/main").split()[0]
            if local_sha != remote_sha:
                raise ContractError("remote_sha_mismatch", name)
            repositories.append({
                "path": name, "changed": True, "selected": True, "order": index,
                "local_sha": local_sha, "remote_sha": remote_sha,
                "remote": "owned", "remote_url": str((nested_remote, top_remote)[index]),
                "remote_host": "local", "remote_owner": str(root),
                "remote_repo": name, "branch": "main",
            })
        repositories.append({
            "path": "unchanged", "changed": False, "selected": False, "order": 2,
            "local_sha": unchanged_sha, "remote_sha": "",
            "remote": "owned", "remote_url": str(unchanged_remote),
            "remote_host": "local", "remote_owner": str(root),
            "remote_repo": "unchanged", "branch": "main",
        })
        return {
            "format_version": 1, "verdict": "PASS", "reason": "offline_publish_verified",
            "mode": "self-test", "repositories": repositories,
        }


def audit_manifest(args: argparse.Namespace) -> JsonObject:
    inputs = (
        args.helper_audit_log, args.initial_state, args.source_freeze,
        args.report_only_digest, args.commit_audit,
    )
    if args.manifest is None or args.owner is None or any(
        path is None or not path.is_file() for path in inputs
    ):
        raise ContractError("missing_input", "publication audit")
    audit = json_object(args.commit_audit)
    raw = audit.get("repositories")
    if not isinstance(raw, list):
        raise ContractError("malformed_input", "commit audit repositories")
    changed = [
        str(item.get("path"))
        for item in raw if isinstance(item, dict) and item.get("changed")
    ]
    changed.sort(key=lambda path: (path == ".", path))
    repositories: JsonArray = []
    for order, path in enumerate(changed):
        if git(Path(path), "status", "--porcelain"):
            raise ContractError("dirty_changed_repository", path)
        branch = git(Path(path), "symbolic-ref", "--short", "HEAD")
        remote = git(Path(path), "remote").splitlines()
        owned = next(
            (
                name for name in remote
                if args.owner in git(Path(path), "remote", "get-url", name)
            ),
            "",
        )
        if not owned:
            raise ContractError("third_party_remote", path)
        remote_url = git(Path(path), "remote", "get-url", owned)
        remote_host, remote_owner_name, remote_repo = remote_identity(remote_url)
        if remote_owner_name != args.owner:
            raise ContractError("third_party_remote", path)
        repositories.append({
            "path": path, "changed": True, "selected": True, "order": order,
            "local_sha": git(Path(path), "rev-parse", "HEAD"), "remote_sha": "",
            "remote": owned, "remote_url": remote_url,
            "remote_host": remote_host, "remote_owner": remote_owner_name,
            "remote_repo": remote_repo, "branch": branch,
        })
    manifest: JsonObject = {
        "format_version": 1, "verdict": "PASS", "reason": "manifest_audited",
        "mode": "audit", "repositories": repositories,
    }
    validate(manifest, args.schema)
    write_json(args.manifest, manifest)
    return manifest


def manifest_run(args: argparse.Namespace) -> tuple[int, JsonObject]:
    if args.manifest is None or args.mode is None:
        raise ContractError("missing_input", "manifest and mode")
    if args.mode == "audit":
        return 0, audit_manifest(args)
    manifest = json_object(args.manifest)
    validate(manifest, args.schema)
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        raise ContractError("malformed_input", "repositories")
    if args.owner is None:
        raise ContractError("missing_input", "owner")
    validate_repository_policy(
        repositories, args.owner, resolve_remote_url=True,
    )
    output_repositories: JsonArray = []
    for item in repositories:
        if not isinstance(item, dict) or not item.get("selected"):
            continue
        path = Path(str(item.get("path")))
        local_sha = git(path, "rev-parse", "HEAD")
        if local_sha != item.get("local_sha"):
            raise ContractError("stale_manifest", str(path))
        remote_sha = ""
        if args.mode == "push":
            remote = str(item.get("remote"))
            branch = str(item.get("branch"))
            git(path, "push", remote, f"HEAD:{branch}")
            query = git(path, "ls-remote", remote, f"refs/heads/{branch}")
            remote_sha = query.split()[0] if query else ""
            if args.verify_remote_sha and remote_sha != local_sha:
                raise ContractError("remote_sha_mismatch", str(path))
        output_repositories.append({**item, "remote_sha": remote_sha})
    return 0, {
        "format_version": 1, "verdict": "PASS", "reason": "manifest_valid",
        "mode": args.mode, "repositories": output_repositories,
    }


def main() -> int:
    args = parse_args()
    try:
        if args.self_test_negative is not None:
            code = 1
            payload = {
                "format_version": 1, "verdict": "FAIL",
                "reason": negative(args.self_test_negative),
                "mode": "self-test", "repositories": [],
            }
        elif args.self_test_bare_remote:
            code, payload = 0, bare_remote_self_test()
        else:
            code, payload = manifest_run(args)
        validate(payload, args.schema)
    except ContractError as error:
        code = 1
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "mode": "self-test", "repositories": [],
        }
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

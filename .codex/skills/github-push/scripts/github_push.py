#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


GITHUB_URL_RE = re.compile(
    r"^(?:git@github\.com:|ssh://git@github\.com/|https://github\.com/|"
    r"http://github\.com/|git://github\.com/)(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Remote:
    name: str
    url: str


@dataclass(frozen=True)
class Repo:
    path: Path
    relpath: str
    depth: int


def run_git(repo: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def project_root() -> Path:
    result = run_git(Path.cwd(), ["rev-parse", "--show-toplevel"])
    root = Path(result.stdout.strip()).resolve()
    while True:
        result = run_git(root, ["rev-parse", "--show-superproject-working-tree"], check=False)
        parent = result.stdout.strip()
        if result.returncode != 0 or not parent:
            return root
        root = Path(parent).resolve()


def relpath(root: Path, path: Path) -> str:
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return str(path)
    return "." if not rel.parts else rel.as_posix()


def discover_repos(root: Path) -> list[Repo]:
    paths = {root.resolve()}
    result = run_git(
        root,
        ["submodule", "foreach", "--recursive", "--quiet", "git rev-parse --show-toplevel"],
        check=False,
    )
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.strip():
                paths.add(Path(line.strip()).resolve())

    repos = [
        Repo(path=path, relpath=relpath(root, path), depth=0 if path == root else len(relpath(root, path).split("/")))
        for path in paths
    ]
    return sorted(repos, key=lambda item: (item.depth, item.relpath), reverse=True)


def github_owner(url: str) -> str | None:
    match = GITHUB_URL_RE.match(url.strip())
    if not match:
        return None
    return match.group("owner").lower()


def remote_urls(repo: Path, name: str) -> list[str]:
    result = run_git(repo, ["remote", "get-url", "--push", "--all", name], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        result = run_git(repo, ["remote", "get-url", "--all", name], check=False)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def owned_remotes(repo: Path, owner: str) -> list[Remote]:
    names = run_git(repo, ["remote"], check=False).stdout.split()
    remotes: list[Remote] = []
    for name in names:
        for url in remote_urls(repo, name):
            if github_owner(url) == owner.lower():
                remotes.append(Remote(name=name, url=url))
                break

    def priority(remote: Remote) -> tuple[int, str]:
        if remote.name == "github":
            return (0, remote.name)
        if remote.name == "origin":
            return (1, remote.name)
        return (2, remote.name)

    return sorted(remotes, key=priority)


def current_branch(repo: Path) -> str | None:
    result = run_git(repo, ["symbolic-ref", "--quiet", "--short", "HEAD"], check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_dirty(repo: Path) -> bool:
    result = run_git(repo, ["status", "--porcelain"], check=False)
    return bool(result.stdout.strip())


def ahead_count(repo: Path, remote: str, branch: str) -> str:
    remote_ref = f"refs/remotes/{remote}/{branch}"
    exists = run_git(repo, ["show-ref", "--verify", "--quiet", remote_ref], check=False)
    if exists.returncode != 0:
        return "unknown"
    result = run_git(repo, ["rev-list", "--count", f"{remote_ref}..HEAD"], check=False)
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def print_remotes(repo: Repo) -> None:
    result = run_git(repo.path, ["remote", "-v"], check=False)
    for line in result.stdout.splitlines():
        print(f"    {line}")


def push_command(remote: Remote, branch: str, dry_run: bool) -> list[str]:
    command = ["git", "push"]
    if dry_run:
        command.append("--dry-run")
    command.extend([remote.name, f"HEAD:{branch}"])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit, dry-run, or push GitHub-owned project repositories."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="run git push --dry-run")
    mode.add_argument("--push", action="store_true", help="run git push")
    parser.add_argument("--owner", default=os.environ.get("GITHUB_OWNER", "cometzero"))
    parser.add_argument("--remote", help="use this remote name only if its URL is owned")
    parser.add_argument("--allow-dirty", action="store_true", help="do not skip dirty repos")
    args = parser.parse_args()

    root = project_root()
    repos = discover_repos(root)
    action = "push" if args.push else "dry-run" if args.dry_run else "audit"
    print(f"project_root={relpath(root, root)}")
    print(f"owner={args.owner}")
    print(f"action={action}")

    for repo in repos:
        branch = current_branch(repo.path)
        remotes = owned_remotes(repo.path, args.owner)
        if args.remote:
            remotes = [remote for remote in remotes if remote.name == args.remote]

        print(f"\n[{repo.relpath}]")
        if branch is None:
            print("  skip: detached-head")
            continue
        if not remotes:
            print("  skip: no-owned-remote")
            print_remotes(repo)
            continue
        if is_dirty(repo.path) and not args.allow_dirty:
            print("  skip: dirty")
            continue

        remote = remotes[0]
        ahead = ahead_count(repo.path, remote.name, branch)
        command = push_command(remote, branch, dry_run=args.dry_run)
        quoted = " ".join(shlex.quote(part) for part in command)
        print(f"  branch: {branch}")
        print(f"  remote: {remote.name} {remote.url}")
        print(f"  ahead: {ahead}")
        print(f"  command: {quoted}")

        if action == "audit":
            continue

        result = subprocess.run(
            command,
            cwd=repo.path,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.stdout.strip():
            for line in result.stdout.splitlines():
                print(f"    {line}")
        if result.returncode != 0:
            print(f"  failed: exit {result.returncode}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

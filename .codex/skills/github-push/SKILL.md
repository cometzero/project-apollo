---
name: github-push
description: Push this project's top Git repository and recursive submodules to the user's own GitHub remotes. Use when the user asks for $github-push, asks to push committed changes to GitHub, asks to upload changed submodules, or asks to publish all eligible project repositories while avoiding upstream/non-user remotes.
---

# GitHub Push

## Core Rule

Push only repositories whose selected remote URL belongs to the user's GitHub
owner. For this project, default the owner to `cometzero`. Never push to
upstream, GitLab, Yocto, Arm, Qualcomm, Zephyr, TF-A, or other third-party
remotes unless the user explicitly changes the owner and the remote URL
matches that owner.

Use `scripts/github_push.py` from this skill to enumerate the top repository
and recursive submodules. The helper chooses a GitHub-owned remote by URL, not
by remote name. It prefers `github`, then `origin`, then any other owned remote.

## Workflow

1. Confirm the current directory is the project top or inside this project.
2. Inspect status before pushing:
   ```bash
   git status --short --branch
   git submodule foreach --recursive 'git status --short --branch'
   ```
3. Ensure intended changes are committed. Do not push dirty repositories unless
   the user explicitly asks to push committed refs while leaving local worktree
   changes untouched.
4. Run an audit first:
   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py
   ```
5. If the audit shows only intended eligible repositories, run a remote dry-run:
   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py --dry-run
   ```
6. Push only after the dry-run succeeds:
   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py --push
   ```
7. Report each pushed repository, branch, remote name, and remote URL. Also
   report skipped repositories and the reason, especially `dirty`,
   `no-owned-remote`, or `detached-head`.

## Safety Rules

- Push submodules before the top repository so recorded submodule commits are
  available on GitHub before the superproject commit is published.
- Treat dirty repositories as blockers by default. Use `--allow-dirty` only
  when the user explicitly accepts that uncommitted changes remain local.
- Do not change remote URLs in this skill. If a repository lacks a GitHub-owned
  remote, skip it and report the current remotes.
- Do not use `git push --all` or `git push --mirror`. Push only the current
  branch with `HEAD:<branch>`.
- If a push fails, stop and report the failing repository and exact command.

## Owner Override

Use `GITHUB_OWNER=<owner>` or `--owner <owner>` only when the user explicitly
requests a different GitHub account or organization.

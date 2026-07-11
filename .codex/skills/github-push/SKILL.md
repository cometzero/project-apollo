---
name: github-push
description: Push this project's top-level Git repository and recursive submodules to user-owned GitHub remotes. Use for $github-push, publishing committed project refs, auditing eligible remotes, or pushing changed submodules without touching upstream remotes.
---

# GitHub Push

Push only remote URLs owned by the requested GitHub account. The default owner
is `cometzero`. Never push Arm, Yocto, Qualcomm, Zephyr, upstream, GitLab, or
other third-party remotes unless the user explicitly changes the owner and the
URL matches it.

The helper resolves the top-level superproject even when invoked from inside a
recursive submodule. It pushes recursive submodules before the top-level
repository and stops on the first failed push.

## Model Routing

Run this external-write workflow with the project default `gpt-5.6-sol` at
high reasoning effort. Do not delegate the final push decision to a lightweight
read-only or QA agent.

## Workflow

1. Inspect the top-level repository and recursive submodules:

   ```bash
   git status --short --branch
   git submodule foreach --recursive 'git status --short --branch'
   ```

2. Ensure intended refs are committed. Dirty repositories are skipped unless
   the user explicitly accepts `--allow-dirty`.

3. Audit selected remotes and branches:

   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py
   ```

4. Prove the remote operation without updating refs:

   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py --dry-run
   ```

5. Push after the dry-run succeeds:

   ```bash
   python3 .codex/skills/github-push/scripts/github_push.py --push
   ```

## Safety Contract

- Remote ownership is determined from the URL, not the remote name.
- Preferred owned remotes are `github`, then `origin`, then another matching
  remote.
- Push only `HEAD:<current-branch>`; never use `--all` or `--mirror`.
- Skip detached heads, dirty repositories, and repositories with no owned
  remote, reporting the reason.
- Stop immediately on the first failed dry-run or push.
- Do not rewrite remote URLs.
- Use `--owner` or `GITHUB_OWNER` only when the user requests another owner.

Report repository path, branch, selected remote and URL, result, and every
skipped repository with its reason.

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPT_DIR = ROOT / ".codex/skills/github-push/scripts"


def run_git(path: Path, args: list[str]) -> None:
    subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def initialize_repo(path: Path) -> None:
    path.mkdir(parents=True)
    run_git(path, ["init", "-q"])
    run_git(path, ["config", "user.name", "Skill Test"])
    run_git(path, ["config", "user.email", "skill-test@example.com"])
    (path / "README").write_text("fixture\n", encoding="utf-8")
    run_git(path, ["add", "README"])
    run_git(path, ["commit", "-q", "-m", "fixture"])


def test_project_root_reaches_top_superproject_from_submodule(
    tmp_path: Path,
) -> None:
    # Given: a top-level repository with a checked-out submodule.
    source = tmp_path / "source"
    top = tmp_path / "top"
    initialize_repo(source)
    initialize_repo(top)
    run_git(top, ["-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "nested"])
    run_git(top, ["commit", "-q", "-am", "add submodule"])
    # When: the helper discovers the project from inside the submodule.
    program = (
        "import sys; "
        f"sys.path.insert(0, {str(SKILL_SCRIPT_DIR)!r}); "
        "import github_push; "
        "print(github_push.project_root())"
    )
    result = subprocess.run(
        ["python3", "-c", program],
        cwd=top / "nested",
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    # Then: it returns the top-level superproject, not the nested repository.
    assert Path(result.stdout.strip()) == top.resolve()


def test_push_stops_after_first_repository_failure(tmp_path: Path) -> None:
    # Given: two eligible repositories and a git push command that always fails.
    source = tmp_path / "source"
    top = tmp_path / "top"
    initialize_repo(source)
    initialize_repo(top)
    run_git(top, ["-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "nested"])
    run_git(top, ["commit", "-q", "-am", "add submodule"])
    run_git(top, ["remote", "add", "github", "https://github.com/cometzero/top.git"])
    run_git(top / "nested", ["remote", "add", "github", "https://github.com/cometzero/nested.git"])
    real_git = shutil.which("git")
    assert real_git is not None
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    push_log = tmp_path / "push.log"
    fake_git = fake_bin / "git"
    fake_git.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "push" ]; then pwd >> "$PUSH_LOG"; exit 9; fi\n'
        f'exec "{real_git}" "$@"\n',
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    # When: the helper pushes the recursive repository set.
    result = subprocess.run(
        ["python3", str(SKILL_SCRIPT_DIR / "github_push.py"), "--push"],
        cwd=top,
        env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}", "PUSH_LOG": str(push_log)},
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Then: it returns failure without attempting the top-level repository.
    assert result.returncode == 1
    assert push_log.read_text(encoding="utf-8").splitlines() == [str(top / "nested")]

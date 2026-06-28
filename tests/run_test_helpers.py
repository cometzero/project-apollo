from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run_test.sh"
LATEST = ROOT / "build/tests/latest"


def run_runner(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(RUNNER), *args],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_commands(run_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (run_dir / "commands.jsonl").read_text(encoding="utf-8").splitlines()]


def command_texts(run_dir: Path) -> list[str]:
    return [" ".join(command.get("argv", [])) for command in load_commands(run_dir)]


def write_fake_python(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "$1" == "-m" && "$2" == "compileall" ]]; then\n'
        "  printf 'fake compileall failure\\n' >&2\n"
        "  exit 9\n"
        "fi\n"
        'exec "${REAL_PYTHON}" "$@"\n',
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_pytest(path: Path) -> None:
    path.write_text("#!/usr/bin/env bash\nprintf 'fake pytest pass\\n'\n", encoding="utf-8")
    path.chmod(0o755)


def latest_target() -> str | None:
    return os.readlink(LATEST) if LATEST.is_symlink() else None


@contextmanager
def preserve_latest_link() -> Iterator[None]:
    target = latest_target()
    try:
        yield
    finally:
        LATEST.parent.mkdir(parents=True, exist_ok=True)
        if LATEST.is_symlink() or LATEST.is_file():
            LATEST.unlink()
        elif LATEST.exists():
            shutil.rmtree(LATEST)
        if target is not None:
            LATEST.symlink_to(target)

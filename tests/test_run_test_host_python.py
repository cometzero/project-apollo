from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_oeqa_lanes.py"


def write_json(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_commands(path: Path) -> list[JsonObject]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_host_python_bin_is_used_for_bitbake_env_python(tmp_path: Path) -> None:
    # Given: a host Python that provides OEQA FVP controller dependencies.
    run_dir = tmp_path / "task-host-python"
    commands_file = run_dir / "commands.jsonl"
    write_json(run_dir / "manifest.json", {"status": "ok", "test_suites": ["ping", "ssh"]})
    commands_file.write_text("", encoding="utf-8")

    # When: OEQA lanes are planned with an explicit host Python.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--run-dir",
            str(run_dir),
            "--commands-file",
            str(commands_file),
            "--build-dir",
            "build",
            "--image",
            "nexios-image",
            "--host-python-bin",
            "/usr/bin/python3",
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the shell script puts that Python's bin directory before BitBake.
    assert result.returncode == 0, result.stderr
    command_text = "\n".join(" ".join(record["argv"]) for record in load_commands(commands_file))
    assert "export PATH=/usr/bin:$PATH && source layers/poky/oe-init-build-env build" in command_text

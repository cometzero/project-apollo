from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_local_fvp_tmux.sh"


def make_executable(path: Path, body: str = "exit 0\n") -> Path:
    path.write_text(f"#!/usr/bin/env bash\n{body}", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_fvpconf(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "parameters": {},
                "terminals": {
                    "css.smb.si.terminal_uart_si_cluster0": "SI C0",
                    "css.smb.si.terminal_uart_si_cluster1": "SI C1",
                },
            }
        ),
        encoding="utf-8",
    )


def test_tmux_runner_disables_synchronized_panes(tmp_path: Path) -> None:
    fvpconf = tmp_path / "apollo-fvp-local.fvpconf"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    fake_bin_dir.mkdir()
    write_fvpconf(fvpconf)

    fake_tmux = make_executable(
        fake_bin_dir / "tmux",
        "\n".join(
            [
                "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"",
                "if [[ \"$1\" == \"has-session\" ]]; then",
                "    exit 1",
                "fi",
                "if [[ \"$1\" == \"new-session\" ]]; then",
                "    printf '%%0\\n'",
                "fi",
                "exit 0",
                "",
            ]
        ),
    )
    fake_runfvp = make_executable(fake_bin_dir / "runfvp")

    env = os.environ.copy()
    env.update(
        {
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "RUN_STAMP": "pytest",
        }
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            "--no-attach",
            "--session",
            "apollo-fvp-test",
            "--out-dir",
            str(tmp_path / "out"),
            "--fvpconf",
            str(fvpconf),
            "--runfvp-bin",
            str(fake_runfvp),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    assert (
        "set-window-option -t apollo-fvp-test:fvp synchronize-panes off"
        in tmux_log.read_text(encoding="utf-8").splitlines()
    )

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_local_debug.sh"


def make_tool(path: Path, body: str) -> None:
    path.write_text("#!/usr/bin/env bash\nset -eu\n" + body)
    path.chmod(0o755)


def test_debug_launcher_replaces_shell_and_adds_domain_panes(tmp_path: Path) -> None:
    runner_log = tmp_path / "runner.log"
    tmux_log = tmp_path / "tmux.log"
    runner = tmp_path / "runner"
    tmux = tmp_path / "tmux"
    manifest = tmp_path / "symbols.json"
    manifest.write_text(json.dumps({"components": {}}))
    make_tool(runner, f'printf "%s\\n" "$@" >"{runner_log}"\n')
    make_tool(
        tmux,
        f'printf "%s\\n" "$@" >>"{tmux_log}"\n'
        'if [[ "${1:-}" == "list-panes" ]]; then printf "%%7 shell\\n"; fi\n'
        'if [[ "${1:-}" == "new-window" ]]; then printf "%%8\\n"; fi\n'
        'if [[ "${1:-}" == "split-window" ]]; then printf "%%9\\n"; fi\n',
    )
    env = os.environ | {
        "RUN_QBOX_LOCAL_SH": str(runner),
        "TMUX_BIN": str(tmux),
        "LOCAL_DEBUG_SKIP_MANIFEST": "1",
        "LOCAL_DEBUG_SKIP_PORT_CHECK": "1",
        "LOCAL_DEBUG_MANIFEST": str(manifest),
    }

    result = subprocess.run(
        [
            str(SCRIPT),
            "--session",
            "debug-test",
            "--out-dir",
            str(tmp_path / "out"),
            "--no-attach",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    runner_args = runner_log.read_text()
    assert "--host-gdb-script" in runner_args
    assert "platform.rse_cpu_pass.cpu_0.gdb_port=12340" in runner_args
    assert "platform.si_cl0_cpu_0.gdb_port=12341" in runner_args
    assert "platform.si_cl1_cpu_0.gdb_port=12342" in runner_args
    assert "platform.ap_cpu_0.gdb_port=12343" in runner_args
    tmux_args = tmux_log.read_text()
    assert "respawn-pane" in tmux_args
    assert "domain-rse" in tmux_args
    assert "domain-si0" in tmux_args
    assert "domain-si1" in tmux_args
    assert "domain-ap" in tmux_args
    assert "--wait-log-marker-only" in tmux_args
    assert str(tmp_path / "out/qbox-secure-console.log") in tmux_args
    assert r"PFDI:\ OoR\ tests\ on\ core\ 3\ succeeded." in tmux_args
    assert tmux_args.count("--wait-log-marker-only") == 4
    assert tmux_args.count("--continue") == 1

    tmux_log.unlink()
    result = subprocess.run(
        [
            str(SCRIPT),
            "--session",
            "debug-early-test",
            "--out-dir",
            str(tmp_path / "early-out"),
            "--no-attach",
            "--ap-early-attach",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert tmux_log.read_text().count("--wait-log-marker-only") == 3


def test_debug_launcher_help_is_available() -> None:
    result = subprocess.run(
        [str(SCRIPT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--vscode" in result.stdout
    assert "--ap-early-attach" in result.stdout
    assert "--firmware-early-attach" in result.stdout

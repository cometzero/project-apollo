from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys_path = str(Path(__file__).resolve().parents[1] / "scripts/test")
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from run_test_oeqa_lanes import OeqaInputs, run_lanes
from test_run_test_oeqa_lanes import load_commands, make_run_dir, run_oeqa, write_fake_timeout


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def wait_for_process_exit(pid: int) -> bool:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if not process_exists(pid):
            return True
        try:
            state = subprocess.check_output(
                ["ps", "-o", "stat=", "-p", str(pid)],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return True
        if state.startswith("Z"):
            return True
        time.sleep(0.1)
    return False


def test_timed_out_oeqa_process_group_is_cleaned_up(tmp_path: Path) -> None:
    # Given: a fake timeout process that leaves a same-session child behind.
    run_dir = tmp_path / "cleanup-timeout"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    child_pid_file = tmp_path / "child.pid"
    write_fake_timeout(
        fake_bin / "timeout",
        f"[ \"$1\" = 60 ] && exit 0; sleep 120 & echo $! > {child_pid_file}; exit 124",
    )

    # When: the OEQA lane runner observes the timeout status.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "1",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: the process-group cleanup removes the leftover child too.
    assert result.returncode == 2
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    assert wait_for_process_exit(child_pid)
    records = load_commands(commands_file)
    assert records[0]["status"] == "blocked"
    assert records[0]["blockers"][0]["reason"] == "blocked_timeout"
    try:
        os.kill(child_pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def test_timeout_kills_bitbake_server_for_lane_build_dir(tmp_path: Path) -> None:
    # Given: a minimal fake Yocto tree and fake timeout/bitbake commands.
    root = tmp_path / "workspace"
    fake_bin = tmp_path / "bin"
    env_dir = root / "layers/poky"
    run_dir = root / "build/tests/cleanup-bitbake"
    commands_file = make_run_dir(run_dir)
    kill_log = tmp_path / "kill-server.argv"
    fake_bin.mkdir(parents=True)
    env_dir.mkdir(parents=True)
    (env_dir / "oe-init-build-env").write_text(
        f"export PATH={fake_bin}:$PATH\n",
        encoding="utf-8",
    )
    write_fake_timeout(
        fake_bin / "bitbake",
        f"printf '%s\\n' \"$*\" >> {kill_log}; [ \"$1\" = -m ] && exit 0; exit 124",
    )

    # When: OEQA reports timeout from the fake bitbake command.
    result = run_lanes(
        OeqaInputs(
            root=root,
            build_dir=Path("build"),
            image="nexios-image",
            run_dir=run_dir,
            commands_file=commands_file,
            timeout_oeqa=1,
            dry_run=False,
        )
    )

    # Then: each timed-out lane asks BitBake to kill its server.
    assert result == 2
    kill_server_calls = [line for line in kill_log.read_text(encoding="utf-8").splitlines() if line == "-m"]
    assert kill_server_calls == ["-m", "-m"]
    assert (run_dir / "oeqa/current/logs/bitbake-kill-server.log").is_file()

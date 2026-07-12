from __future__ import annotations

from contextlib import ExitStack
import os
import pty
import shutil
import subprocess
import sys
import time
from pathlib import Path

from run_test_helpers import ROOT, load_json, nonempty_lines, preserve_latest_link, run_runner


TARGET_LOG_SCRIPT = ROOT / "hsoc-stack/tests/apollo_validation/tui_target.py"


def _wait_for(predicate, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return False


def test_tui_builds_test_and_target_log_panes() -> None:
    # Given: a unique tmux-backed runner invocation with captured stdout.
    out_dir = Path("build/tests/ulw-pytest-tui")
    session = "run-test-ulw-pytest-tui"
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)
    subprocess.run(["tmux", "kill-session", "-t", session], check=False)

    try:
        # When: TUI mode runs a category that completes without launching FVP.
        with preserve_latest_link():
            result = run_runner(
                "--tui",
                "--category",
                "extended",
                "--stamp",
                "ulw-pytest-tui",
                "--out-dir",
                str(out_dir),
                extra_env={"RUN_TEST_TMUX_SESSION": session},
            )

        # Then: test progress and FVP target panes are durable and TUI is not recursive.
        assert result.returncode == 0, result.stderr
        outer_lines = nonempty_lines(result.stdout)
        assert "RESULT: PASS" in outer_lines
        assert f"SUMMARY: {out_dir}/summary.json" in outer_lines
        tui_dir = ROOT / out_dir / "tui"
        command = (tui_dir / "command.txt").read_text(encoding="utf-8")
        assert "run_test.sh" in command
        assert "--category extended" in command
        assert "--tui" not in command
        assert (tui_dir / "console.log").is_file()
        assert (tui_dir / "status").read_text(encoding="utf-8").strip() == "0"
        layout = load_json(tui_dir / "layout.json")
        assert [pane["title"] for pane in layout["panes"]] == [
            "platform",
            "u_boot_linux",
            "rse",
            "safety_island_cl0",
            "safety_island_cl1",
            "tf_a",
            "tests",
        ]
        assert subprocess.run(
            ["tmux", "has-session", "-t", session],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode != 0
    finally:
        subprocess.run(["tmux", "kill-session", "-t", session], check=False)


def test_target_log_streamer_reads_boot_and_oeqa_logs(tmp_path: Path) -> None:
    # Given: one Primary Compute log from the boot lane and one from an OEQA lane.
    run_dir = tmp_path / "run"
    boot_log = run_dir / "fvp/terminal_ns_uart0_5004.log"
    oeqa_log = run_dir / "oeqa/functional/logs/default_log.20260712"
    status = run_dir / "tui/status"
    boot_log.parent.mkdir(parents=True)
    oeqa_log.parent.mkdir(parents=True)
    status.parent.mkdir(parents=True)
    boot_log.write_text("U-Boot target output\n", encoding="utf-8")
    oeqa_log.write_text("OEQA Linux target output\n", encoding="utf-8")
    (oeqa_log.parent / "default_log").symlink_to(oeqa_log.name)
    status.write_text("0\n", encoding="utf-8")

    # When: the FVP target pane streamer drains the completed run.
    result = subprocess.run(
        [sys.executable, str(TARGET_LOG_SCRIPT), str(run_dir), "u_boot_linux"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    # Then: it shows real target output from both FVP execution phases once.
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("U-Boot target output") == 1
    assert result.stdout.count("OEQA Linux target output") == 1


def test_target_log_streamer_reads_qbox_target_log(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    target_log = run_dir / "qvp/qbox-primary-console.log"
    status = run_dir / "tui/status"
    target_log.parent.mkdir(parents=True)
    status.parent.mkdir(parents=True)
    target_log.write_text("QBox Linux target output\n", encoding="utf-8")
    status.write_text("0\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TARGET_LOG_SCRIPT), str(run_dir), "u_boot_linux"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.count("QBox Linux target output") == 1


def test_tui_default_timestamp_session_name_is_tmux_safe() -> None:
    # Given: TUI mode derives its session name from the default timestamped run directory.
    before_result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    before = set(before_result.stdout.splitlines())

    try:
        # When: functional TUI planning runs without an explicit stamp or output directory.
        with preserve_latest_link():
            result = run_runner("--tui", "--category", "functional", "--dry-run")

        # Then: tmux can target the created session and the child completes successfully.
        assert result.returncode == 0, result.stderr
        session_line = next(
            line for line in nonempty_lines(result.stdout) if "[run_test] TUI session:" in line
        )
        assert "." not in session_line
    finally:
        after_result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        for session in set(after_result.stdout.splitlines()) - before:
            if session.startswith("run-test-"):
                subprocess.run(["tmux", "kill-session", "-t", session], check=False)


def test_tui_f12_stops_runner_process_tree_and_session(tmp_path: Path) -> None:
    out_dir = Path("build/tests/ulw-pytest-tui-f12")
    session = "run-test-ulw-pytest-tui-f12"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    timeout_pid = tmp_path / "timeout.pid"
    fake_timeout = fake_bin / "timeout"
    fake_timeout.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$*\" == *'bitbake -m'* ]]; then exit 0; fi\n"
        "printf '%s\\n' \"$$\" > \"$RUN_TEST_FAKE_TIMEOUT_PID\"\n"
        "trap 'exit 143' INT TERM HUP\n"
        "while :; do sleep 1; done\n",
        encoding="utf-8",
    )
    fake_timeout.chmod(0o755)
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)
    subprocess.run(["tmux", "kill-session", "-t", session], check=False)
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "RUN_TEST_FAKE_TIMEOUT_PID": str(timeout_pid),
            "RUN_TEST_HOST_PYTHON_BIN": sys.executable,
            "RUN_TEST_TMUX_SESSION": session,
        }
    )
    resources = ExitStack()
    resources.enter_context(preserve_latest_link())
    process = subprocess.Popen(
        [
            str(ROOT / "run_test.sh"),
            "--tui",
            "--machine",
            "apollo-qvp",
            "--category",
            "functional",
            "--stamp",
            out_dir.name,
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client: subprocess.Popen[bytes] | None = None
    master_fd: int | None = None

    try:
        assert _wait_for(timeout_pid.is_file), "fake OEQA timeout process did not start"
        timeout_process_pid = int(timeout_pid.read_text(encoding="utf-8").strip())
        master_fd, slave_fd = pty.openpty()
        client = subprocess.Popen(
            ["tmux", "attach-session", "-t", session],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)
        time.sleep(0.5)
        os.write(master_fd, b"\x1b[24~")
        stdout, stderr = process.communicate(timeout=15)

        assert process.returncode == 130, (stdout, stderr)
        assert (ROOT / out_dir / "tui/status").read_text(encoding="utf-8").strip() == "130"
        stop_path = ROOT / out_dir / "tui/stop.json"
        assert _wait_for(stop_path.is_file)
        stop = load_json(stop_path)
        assert stop["status"] == 130
        assert timeout_process_pid in stop["process_tree"]
        assert stop["detached_remaining"] == []
        assert not Path(f"/proc/{timeout_process_pid}").exists()
        assert subprocess.run(
            ["tmux", "has-session", "-t", session],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode != 0
    finally:
        subprocess.run(["tmux", "kill-session", "-t", session], check=False)
        if client is not None and client.poll() is None:
            client.terminate()
            client.wait(timeout=5)
        if master_fd is not None:
            os.close(master_fd)
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        if timeout_pid.is_file():
            pid = timeout_pid.read_text(encoding="utf-8").strip()
            subprocess.run(["kill", "-KILL", pid], check=False)
        resources.close()

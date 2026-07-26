from __future__ import annotations

import os
from pathlib import Path
import signal
import shlex
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_boot_regression.sh"


def make_fake_python(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


def wait_for_file(path: Path, timeout_s: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {path}")


def test_run_qbox_boot_regression_wrapper_defaults(tmp_path: Path) -> None:
    args_file = tmp_path / "args.txt"
    fake_python = make_fake_python(
        tmp_path / "python3",
        f"printf '%s\\n' \"$@\" > {shlex.quote(str(args_file))}\n",
    )
    result_root = tmp_path / "results"
    result_root.mkdir()
    baseline = result_root / "run_qbox_yocto_baseline.json"
    baseline.write_text("{}\n", encoding="utf-8")
    regression_script = tmp_path / "run_qbox_yocto_boot_regression.py"
    regression_script.write_text("# fake\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "PYTHON": str(fake_python),
            "REGRESSION_SCRIPT": str(regression_script),
            "RESULT_ROOT": str(result_root),
            "RUN_STAMP": "20260701-120000",
            "TIMEOUT": "123",
        }
    )
    result = subprocess.run(
        [str(SCRIPT), "--threshold", "0.10", "--", "--copy-disks"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    args = args_file.read_text(encoding="utf-8").splitlines()
    assert args[:2] == [str(regression_script), "--run"]
    assert "--baseline" in args
    assert str(baseline) in args
    assert "--out-dir" in args
    assert str(result_root / "regression-20260701-120000") in args
    assert "--timeout" in args
    assert "123" in args
    assert "--threshold" in args
    assert "0.20" in args
    assert "--poll-interval" in args
    assert "0.5" in args
    assert args[-4:] == ["--threshold", "0.10", "--", "--copy-disks"]


def test_run_qbox_boot_regression_forwards_multi_session(tmp_path: Path) -> None:
    args_file = tmp_path / "args.txt"
    fake_python = make_fake_python(
        tmp_path / "python3",
        f"printf '%s\\n' \"$@\" > {shlex.quote(str(args_file))}\n",
    )
    result_root = tmp_path / "results"
    result_root.mkdir()
    (result_root / "run_qbox_yocto_baseline.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    regression_script = tmp_path / "run_qbox_yocto_boot_regression.py"
    regression_script.write_text("# fake\n", encoding="utf-8")

    result = subprocess.run(
        [str(SCRIPT), "--multi-session"],
        cwd=ROOT,
        env={
            **os.environ,
            "PYTHON": str(fake_python),
            "REGRESSION_SCRIPT": str(regression_script),
            "RESULT_ROOT": str(result_root),
        },
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert args_file.read_text(encoding="utf-8").splitlines()[-2:] == [
        "--",
        "--multi-session",
    ]


def test_run_qbox_boot_regression_wrapper_forwards_ctrl_c(tmp_path: Path) -> None:
    pid_file = tmp_path / "child.pid"
    int_file = tmp_path / "child.interrupted"
    fake_python = make_fake_python(
        tmp_path / "python3",
        (
            f"printf '%s\\n' \"$$\" > {shlex.quote(str(pid_file))}\n"
            f"trap 'printf interrupted > {shlex.quote(str(int_file))}; exit 130' INT\n"
            "while :; do sleep 0.1; done\n"
        ),
    )
    result_root = tmp_path / "results"
    result_root.mkdir()
    (result_root / "run_qbox_yocto_baseline.json").write_text("{}\n", encoding="utf-8")
    regression_script = tmp_path / "run_qbox_yocto_boot_regression.py"
    regression_script.write_text("# fake\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "PYTHON": str(fake_python),
            "REGRESSION_SCRIPT": str(regression_script),
            "RESULT_ROOT": str(result_root),
            "RUN_STAMP": "20260701-120001",
        }
    )
    proc = subprocess.Popen(
        [str(SCRIPT)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        wait_for_file(pid_file)
        os.kill(proc.pid, signal.SIGINT)
        stdout, stderr = proc.communicate(timeout=5)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    assert proc.returncode == 130, (stdout, stderr)
    assert int_file.read_text(encoding="utf-8") == "interrupted"

"""Stats options survive launcher boundaries without starting a VM."""
from collections import defaultdict
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/run"))
import run_qbox_apollo_fvp_full as full


@pytest.mark.parametrize("options, interval", [
    ([], None), (["--stats"], 5.0),
    (["--stats-interval", "2.5"], 2.5),
    (["--stats-interval", "2.5", "--stats"], 2.5),
])
def test_full_runner_forwards_stats_to_runtime_child(options, interval, tmp_path):
    args = full.parse_args(["--out-dir", str(tmp_path), *options])
    command = full.child_command(args, defaultdict(lambda: tmp_path / "artifact"))
    assert command[2] == "--runtime-child"
    if interval is None:
        assert not args.monitor
        assert "--stats-interval" not in command
    else:
        assert args.monitor
        assert full.full_system_child_environment(args)["QBOX_APOLLO_MONITOR"] == "true"
        index = command.index("--stats-interval")
        assert float(command[index + 1]) == interval


@pytest.mark.parametrize("script", [
    "run_qbox_yocto.sh", "scripts/run/run_qbox_apollo_fvp_full_tmux.sh",
])
@pytest.mark.parametrize("options, interval", [
    ([], None), (["--stats"], "5"),
    (["--stats-interval=2.5"], "2.5"),
])
def test_shell_dry_run_forwards_stats(script, options, interval):
    result = subprocess.run(
        ["bash", str(ROOT / script), "--dry-run", *options,
         "--", "--foreground-runtime"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert "--foreground-runtime" in result.stdout
    if interval is None:
        assert "--stats-interval" not in result.stdout
    else:
        assert f"--stats-interval {interval}" in result.stdout
        assert "--monitor --monitor-port" in result.stdout


@pytest.mark.parametrize("script", [
    "run_qbox_yocto.sh", "scripts/run/run_qbox_apollo_fvp_full_tmux.sh",
])
@pytest.mark.parametrize("interval", ["0", "-1", "nan", "inf", "", "bad"])
def test_shell_rejects_invalid_interval_before_launch(script, interval):
    result = subprocess.run(
        ["bash", str(ROOT / script), "--stats-interval", interval, "--dry-run"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "--stats-interval" in result.stderr

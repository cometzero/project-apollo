from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from test_run_qbox_yocto_sh import dry_run_command_argv, run_qvp_dry_run


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"


def test_debug_launcher_uses_supported_runner_options(tmp_path: Path) -> None:
    # Given: the options accepted by the canonical full-system runner.
    help_result = subprocess.run(
        [sys.executable, str(RUNNER), "--help"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    supported_options = set(re.findall(r"--[a-z0-9-]+", help_result.stdout))

    # When: the QBox Yocto debug launcher builds its child runner command.
    result = run_qvp_dry_run(
        tmp_path,
        extra_args=["--debug", "u-boot", "--debug-mode", "probe"],
    )
    argv = dry_run_command_argv(result.stdout)
    runner_index = next(
        index
        for index, value in enumerate(argv)
        if value.endswith("run_qbox_apollo_fvp_full.py")
    )
    launcher_options = {
        value.partition("=")[0]
        for value in argv[runner_index + 1 :]
        if value.startswith("--")
    }

    # Then: every generated option belongs to the runner's CLI contract.
    assert help_result.returncode == 0, help_result.stderr
    assert result.returncode == 0, result.stderr
    assert launcher_options <= supported_options, sorted(
        launcher_options - supported_options
    )


def test_guest_debug_pauses_the_full_simulation(tmp_path: Path) -> None:
    # Given: an interactive U-Boot debug launch on the AP CPU.
    result = run_qvp_dry_run(
        tmp_path,
        extra_args=["--debug", "u-boot", "--debug-mode", "probe"],
    )

    # When: the launcher builds the full-system platform parameters.
    argv = dry_run_command_argv(result.stdout)
    platform_params = {
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "--platform-param"
    }

    # Then: the AP debugger also freezes SystemC time for peer domains.
    assert result.returncode == 0, result.stderr
    assert "platform.ap_cpu_0.gdb_pause_all=true" in platform_params

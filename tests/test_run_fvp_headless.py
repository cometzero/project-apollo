from __future__ import annotations

import json
from pathlib import Path
import shlex
import subprocess

from scripts.run import runfvp_log_boot


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_fvp.sh"


def test_bsp_ready_marker_satisfies_primary_console() -> None:
    text = "\n".join(
        [
            "U-Boot 2026.01",
            "Booting Linux on physical CPU 0x0000000000 [0x410fd8f0]",
            "Linux version 6.12.0",
            "NEXIOS_BSP_INITRAMFS_READY machine=apollo-fvp",
        ]
    )

    status = runfvp_log_boot.check_console("terminal_ns_uart0", text)

    assert status["passed"] is True


def test_fvp_headless_routes_to_log_runner(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "tmp_baremetal/deploy/images/apollo-fvp"
    deploy_dir.mkdir(parents=True)
    fvpconf = deploy_dir / "nexios-bsp-initramfs-apollo-fvp.fvpconf"
    fvpconf.write_text(
        json.dumps({"terminals": {"uart0": {"port": 5000}}}),
        encoding="utf-8",
    )
    runfvp = tmp_path / "runfvp"
    runfvp.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    runfvp.chmod(0o755)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--bsp",
            "--headless",
            "--dry-run",
            "--build-dir",
            str(build_dir),
            "--runfvp-bin",
            str(runfvp),
            "--out-dir",
            str(tmp_path / "out"),
            "--timeout",
            "900",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    marker = lines.index("Headless FVP runner command:")
    command = shlex.split(lines[marker + 1])
    assert command[1].endswith("scripts/run/runfvp_log_boot.py")
    assert command[command.index("--fvpconf") + 1] == str(fvpconf)
    assert command[command.index("--timeout") + 1] == "900"
    assert command[command.index("--require") + 1] == "all"

from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox.sh"


def run_dry_run(tmp_path: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    local_build_dir = tmp_path / "local-build"
    out_dir = tmp_path / "out"
    qbox_platform_dir = tmp_path / "qbox-platform"
    conf = qbox_platform_dir / "platforms/apollo/apollo-qvp.lua"
    local_build_dir.mkdir()
    conf.parent.mkdir(parents=True)
    conf.write_text("return {}\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "LOCAL_BUILD_DIR": str(local_build_dir),
            "OUT_DIR": str(out_dir),
            "QBOX_PLATFORM_DIR": str(qbox_platform_dir),
            "QBOX_CONF": str(conf),
            "TMUX_SESSION": "pytest-run-qbox",
            "SSH_PORT_START": "24500",
            "SSH_PORT_END": "24599",
        }
    )
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [str(SCRIPT), "--dry-run", "--no-attach"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_run_qbox_dry_run_defaults_to_inprocess(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "rse_cpu_mode: inprocess" in result.stdout
    assert "--rse-cpu-mode inprocess" in result.stdout


def test_run_qbox_dry_run_allows_remote_override(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, {"RSE_CPU_MODE": "remote"})

    assert result.returncode == 0, result.stderr
    assert "rse_cpu_mode: remote" in result.stdout
    assert "--rse-cpu-mode remote" in result.stdout


def test_run_qbox_rejects_invalid_rse_cpu_mode(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, {"RSE_CPU_MODE": "local"})

    assert result.returncode != 0
    assert "RSE_CPU_MODE must be remote or inprocess" in result.stderr

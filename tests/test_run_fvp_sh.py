from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_fvp.sh"


def make_executable(path: Path) -> Path:
    path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_fvpconf(path: Path, flash_image: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.rse.flash_loader.fnameWrite": str(flash_image),
                },
                "terminals": {
                    "css.rse.terminal_uart": "RSE",
                },
            }
        ),
        encoding="utf-8",
    )


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "tmp_baremetal/deploy/images/apollo-fvp"
    fake_bin_dir = tmp_path / "bin"
    deploy_dir.mkdir(parents=True, exist_ok=True)
    fake_bin_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "RUN_STAMP": "pytest",
            "TMUX_BIN": str(make_executable(fake_bin_dir / "tmux")),
        }
    )

    command = [
        str(SCRIPT),
        "--dry-run",
        "--no-attach",
        "--build-dir",
        str(build_dir),
        "--runfvp-bin",
        str(make_executable(fake_bin_dir / "runfvp")),
        *(extra_args or []),
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_run_fvp_uses_stable_yocto_fvpconf(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "local Apollo FVP tmux run" in result.stdout
    assert f"session: apollo-fvp-yocto-pytest" in result.stdout
    assert f"fvpconf: {fvpconf}" in result.stdout
    assert f"out_dir: {tmp_path}/build/fvp-tmux/apollo-fvp-pytest" in result.stdout


def test_run_fvp_falls_back_to_latest_timestamped_fvpconf(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    older = deploy_dir / "nexios-image-apollo-fvp-20260101000000.fvpconf"
    newer = deploy_dir / "nexios-image-apollo-fvp-20260202000000.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(older, flash_image)
    write_fvpconf(newer, flash_image)
    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert f"fvpconf: {newer}" in result.stdout


def test_run_fvp_forwards_extra_fvp_args(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(
        tmp_path,
        extra_args=["--", "--parameter", "css.test_parameter=1"],
    )

    assert result.returncode == 0, result.stderr
    assert "--parameter css.test_parameter=1" in result.stdout

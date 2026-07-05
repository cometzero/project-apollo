from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_local.sh"


REMOVED_SURFACES = (
    "rse_cpu_mode",
    "--rse-cpu-mode",
    "--remotepass-dmi-cache",
    "--rse-hotpath-tlm-fallback",
    "RSE_CPU_MODE",
    "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK",
    "REMOTEPASS_DMI_CACHE",
)


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
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

    command = [str(SCRIPT), "--dry-run", "--no-attach", *(extra_args or [])]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_run_qbox_dry_run_omits_removed_remote_surfaces(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    for surface in REMOVED_SURFACES:
        assert surface not in result.stdout
        assert surface not in result.stderr


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (
            ["--rse-cpu-mode", "remote"],
            "unsupported removed option: --rse-cpu-mode",
        ),
        (
            ["--rse-hotpath-tlm-fallback"],
            "unsupported removed option: --rse-hotpath-tlm-fallback",
        ),
        (
            ["--no-rse-hotpath-tlm-fallback"],
            "unsupported removed option: --no-rse-hotpath-tlm-fallback",
        ),
        (
            ["--remotepass-dmi-cache"],
            "unsupported removed option: --remotepass-dmi-cache",
        ),
    ],
)
def test_run_qbox_rejects_removed_options(
    tmp_path: Path,
    args: list[str],
    message: str,
) -> None:
    result = run_dry_run(tmp_path, extra_args=args)

    assert result.returncode != 0
    assert message in result.stderr


@pytest.mark.parametrize(
    "name",
    [
        "RSE_CPU_MODE",
        "RUN_QBOX_RSE_HOTPATH_TLM_FALLBACK",
        "REMOTEPASS_DMI_CACHE",
    ],
)
def test_run_qbox_rejects_removed_environment_overrides(tmp_path: Path, name: str) -> None:
    result = run_dry_run(tmp_path, extra_env={name: "1"})

    assert result.returncode != 0
    assert f"unsupported removed environment override: {name}" in result.stderr


def test_run_qbox_rejects_unrelated_invalid_option(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, extra_args=["--not-a-real-option"])

    assert result.returncode != 0
    assert "unknown argument: --not-a-real-option" in result.stderr

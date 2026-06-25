from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "yocto_build.sh"


def run_build_dry_run(
    tmp_path: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "BUILD_DIR": str(tmp_path / "build"),
        }
    )
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [str(SCRIPT), "--dry-run", *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_yocto_build_sh_keeps_legacy_target_without_dm_verity_option(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(tmp_path, [])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith(" nexios-image")
    assert "mc:apollo-fvp" not in result.stdout
    assert not (
        tmp_path / "build/conf/apollo-dm-verity-multiconfig.conf"
    ).exists()


def test_yocto_build_sh_selects_no_dm_verity_multiconfig(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["--dm-verity=off"])

    assert result.returncode == 0, result.stderr
    assert "mc:apollo-fvp-no-dm-verity:nexios-image" in result.stdout
    assert "mode 'off' uses multiconfig apollo-fvp-no-dm-verity" in result.stderr

    multiconfig = tmp_path / "build/conf/apollo-dm-verity-multiconfig.conf"
    assert multiconfig.read_text(encoding="utf-8").splitlines()[-1] == (
        'BBMULTICONFIG = "apollo-fvp-no-dm-verity"'
    )


def test_yocto_build_sh_selects_dm_verity_multiconfig_from_env(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, [], {"APOLLO_DM_VERITY": "on"})

    assert result.returncode == 0, result.stderr
    assert "mc:apollo-fvp-dm-verity:nexios-image" in result.stdout
    assert "mode 'on' uses multiconfig apollo-fvp-dm-verity" in result.stderr


def test_yocto_build_sh_rejects_invalid_dm_verity_mode(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["--dm-verity=maybe"])

    assert result.returncode == 2
    assert "invalid dm-verity mode 'maybe'" in result.stderr

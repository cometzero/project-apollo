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


def write_meminfo(path: Path, mem_total_kib: int) -> None:
    path.write_text(f"MemTotal:       {mem_total_kib} kB\n", encoding="utf-8")


def test_yocto_build_sh_sets_six_threads_at_16gb_or_less(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    write_meminfo(meminfo, 16 * 1024 * 1024)

    result = run_build_dry_run(
        tmp_path,
        [],
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "1",
            "APOLLO_HOST_CPUS": "32",
            "APOLLO_MEMINFO_PATH": str(meminfo),
        },
    )

    assert result.returncode == 0, result.stderr
    resource_conf = tmp_path / "build/conf/apollo-bitbake-resources.conf"
    resource_text = resource_conf.read_text(encoding="utf-8")
    assert 'BB_NUMBER_THREADS = "6"' in resource_text
    assert 'PARALLEL_MAKE = "-j6"' in resource_text


def test_yocto_build_sh_uses_all_cpus_above_16gb(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    write_meminfo(meminfo, 32 * 1024 * 1024)

    result = run_build_dry_run(
        tmp_path,
        [],
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "1",
            "APOLLO_HOST_CPUS": "32",
            "APOLLO_MEMINFO_PATH": str(meminfo),
        },
    )

    assert result.returncode == 0, result.stderr
    resource_conf = tmp_path / "build/conf/apollo-bitbake-resources.conf"
    resource_text = resource_conf.read_text(encoding="utf-8")
    assert 'BB_NUMBER_THREADS = "32"' in resource_text
    assert 'PARALLEL_MAKE = "-j32"' in resource_text


def test_yocto_build_sh_accepts_bb_num_threads_alias(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    write_meminfo(meminfo, 32 * 1024 * 1024)

    result = run_build_dry_run(
        tmp_path,
        [],
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "APOLLO_HOST_CPUS": "32",
            "APOLLO_MEMINFO_PATH": str(meminfo),
            "BB_NUM_THREADS": "9",
            "PARALLEL_MAKE": "-j11",
        },
    )

    assert result.returncode == 0, result.stderr
    resource_conf = tmp_path / "build/conf/apollo-bitbake-resources.conf"
    resource_text = resource_conf.read_text(encoding="utf-8")
    assert 'BB_NUMBER_THREADS = "9"' in resource_text
    assert 'PARALLEL_MAKE = "-j11"' in resource_text


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


def test_yocto_build_sh_selects_qvp_no_dm_verity_multiconfig(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(
        tmp_path,
        ["--machine", "apollo-qvp", "--dm-verity=off"],
    )

    assert result.returncode == 0, result.stderr
    assert "mc:apollo-qvp-no-dm-verity:nexios-image" in result.stdout
    assert "mode 'off' uses multiconfig apollo-qvp-no-dm-verity" in result.stderr

    multiconfig = tmp_path / "build/conf/apollo-dm-verity-multiconfig.conf"
    assert multiconfig.read_text(encoding="utf-8").splitlines()[-1] == (
        'BBMULTICONFIG = "apollo-qvp-no-dm-verity"'
    )


def test_yocto_build_sh_defaults_qvp_to_shared_build_dir(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(
        tmp_path,
        ["--machine", "apollo-qvp"],
        {"APOLLO_AUTO_RESOURCE_LIMITS": "1", "BUILD_DIR": ""},
    )

    assert result.returncode == 0, result.stderr
    expected = ROOT / "build/conf/apollo-bitbake-resources.conf"
    assert str(expected) in result.stderr


def test_yocto_build_sh_selects_qvp_dm_verity_multiconfig(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(
        tmp_path,
        ["--machine", "apollo-qvp", "--dm-verity=on"],
    )

    assert result.returncode == 0, result.stderr
    assert "mc:apollo-qvp-dm-verity:nexios-image" in result.stdout
    assert "mode 'on' uses multiconfig apollo-qvp-dm-verity" in result.stderr


def test_yocto_build_sh_accepts_machine_from_env(tmp_path: Path) -> None:
    result = run_build_dry_run(
        tmp_path,
        ["--dm-verity=on"],
        {"MACHINE": "apollo-qvp"},
    )

    assert result.returncode == 0, result.stderr
    assert "mc:apollo-qvp-dm-verity:nexios-image" in result.stdout


def test_yocto_build_sh_rejects_invalid_machine(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["--machine", "invalid-qvp"])

    assert result.returncode == 2
    assert "invalid-machine 'invalid-qvp'" in result.stderr


def test_yocto_build_sh_rejects_invalid_dm_verity_mode(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["--dm-verity=maybe"])

    assert result.returncode == 2
    assert "invalid dm-verity mode 'maybe'" in result.stderr

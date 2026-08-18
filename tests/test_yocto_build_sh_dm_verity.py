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


def test_yocto_build_sh_uses_default_qvp(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, [])

    assert result.returncode == 0, result.stderr
    assert "MACHINE=apollo-qvp bitbake " in result.stdout
    assert result.stdout.strip().endswith(" nexios-image")
    assert "mc:apollo-qvp" not in result.stdout


def test_yocto_build_sh_keeps_network_sandbox_by_default(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(tmp_path, [])

    assert result.returncode == 0, result.stderr
    assert "apollo-bitbake-host.conf" not in result.stdout
    assert "network sandbox" not in result.stderr
    assert not (tmp_path / "build/conf/apollo-bitbake-host.conf").exists()


def test_yocto_build_sh_ignores_removed_network_sandbox_env(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(
        tmp_path,
        [],
        {"APOLLO_BITBAKE_DISABLE_NETWORK_SANDBOX": "1"},
    )

    assert result.returncode == 0, result.stderr
    host_conf = tmp_path / "build/conf/apollo-bitbake-host.conf"
    assert str(host_conf) not in result.stdout
    assert "network sandbox" not in result.stderr
    assert not host_conf.exists()


def test_yocto_build_sh_uses_requested_build_dir(
    tmp_path: Path,
) -> None:
    result = run_build_dry_run(
        tmp_path,
        [],
        {"APOLLO_AUTO_RESOURCE_LIMITS": "1"},
    )

    assert result.returncode == 0, result.stderr
    expected = tmp_path / "build/conf/apollo-bitbake-resources.conf"
    assert str(expected) in result.stderr


def test_yocto_build_sh_recreates_conf_from_qvp_template(
    tmp_path: Path,
) -> None:
    conf_dir = tmp_path / "build/conf"
    conf_dir.mkdir(parents=True)
    stale_file = conf_dir / "stale.conf"
    stale_file.write_text("stale\n", encoding="utf-8")

    result = run_build_dry_run(tmp_path, [])

    assert result.returncode == 0, result.stderr
    assert not stale_file.exists()
    assert 'MACHINE ??= "apollo-qvp"' in (
        conf_dir / "local.conf"
    ).read_text(encoding="utf-8")
    assert (conf_dir / "bblayers.conf").is_file()
    assert (conf_dir / "templateconf.cfg").read_text(encoding="utf-8").strip() == (
        str(
            ROOT
            / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp"
        )
    )
    assert "recreating it from TEMPLATECONF" in result.stderr


def test_yocto_build_sh_recreates_conf_from_fvp_template(
    tmp_path: Path,
) -> None:
    conf_dir = tmp_path / "build/conf"
    conf_dir.mkdir(parents=True)
    (conf_dir / "local.conf").write_text(
        'MACHINE ??= "apollo-qvp"\n', encoding="utf-8"
    )

    result = run_build_dry_run(tmp_path, ["--machine", "apollo-fvp"])

    assert result.returncode == 0, result.stderr
    assert "MACHINE=apollo-fvp bitbake " in result.stdout
    assert 'MACHINE ??= "apollo-fvp"' in (
        conf_dir / "local.conf"
    ).read_text(encoding="utf-8")
    assert (conf_dir / "templateconf.cfg").read_text(encoding="utf-8").strip() == (
        str(
            ROOT
            / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp"
        )
    )


def test_yocto_build_sh_keep_conf_preserves_existing_configuration(
    tmp_path: Path,
) -> None:
    init_result = run_build_dry_run(tmp_path, [])
    assert init_result.returncode == 0, init_result.stderr

    local_conf = tmp_path / "build/conf/local.conf"
    local_conf.write_text("# user configuration\n", encoding="utf-8")
    sentinel = tmp_path / "build/conf/user.conf"
    sentinel.write_text("preserve\n", encoding="utf-8")

    result = run_build_dry_run(tmp_path, ["--keep-conf"])

    assert result.returncode == 0, result.stderr
    assert local_conf.read_text(encoding="utf-8") == "# user configuration\n"
    assert sentinel.read_text(encoding="utf-8") == "preserve\n"
    assert "preserving existing configuration" in result.stderr


def test_yocto_build_sh_accepts_machine_from_env(tmp_path: Path) -> None:
    result = run_build_dry_run(
        tmp_path,
        [],
        {"MACHINE": "apollo-fvp"},
    )

    assert result.returncode == 0, result.stderr
    assert "MACHINE=apollo-fvp bitbake " in result.stdout
    assert result.stdout.strip().endswith(" nexios-image")


def test_yocto_build_sh_rejects_invalid_machine(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["--machine", "invalid-qvp"])

    assert result.returncode == 2
    assert "invalid-machine 'invalid-qvp'" in result.stderr


def test_yocto_build_sh_forwards_kernel_menuconfig_task(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["virtual/kernel", "-c", "menuconfig"])

    assert result.returncode == 0, result.stderr
    command = result.stdout.splitlines()[-1].split()
    assert command[-3:] == ["virtual/kernel", "-c", "menuconfig"]
    assert "preserving existing configuration" in result.stderr


def test_yocto_build_sh_forwards_bootloader_cleansstate_task(tmp_path: Path) -> None:
    result = run_build_dry_run(tmp_path, ["virtual/bootloader", "-c", "cleansstate"])

    assert result.returncode == 0, result.stderr
    command = result.stdout.splitlines()[-1].split()
    assert command[-3:] == ["virtual/bootloader", "-c", "cleansstate"]

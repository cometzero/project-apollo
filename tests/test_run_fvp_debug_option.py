from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_fvp.sh"


def make_executable(path: Path, body: str = "exit 0") -> Path:
    path.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def run_qvp_dry_run(
    tmp_path: Path,
    *extra_args: str,
) -> subprocess.CompletedProcess[str]:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "tmp_baremetal/deploy/images/apollo-qvp"
    cornea = (
        build_dir
        / "tmp_baremetal/sysroots-components/x86_64"
        / "lite-cornea-native/usr/bin/cornea"
    )
    fake_bin_dir = tmp_path / "bin"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-qvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    fake_bin_dir.mkdir()
    cornea.parent.mkdir(parents=True)
    make_executable(cornea)
    flash_image.write_bytes(b"flash")
    fvpconf.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.rse.flash_loader.fnameWrite": str(flash_image),
                },
                "terminals": {"css.rse.terminal_uart": "RSE"},
            }
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env.update(
        {
            "RUN_STAMP": "pytest",
            "TMUX_BIN": str(make_executable(fake_bin_dir / "tmux")),
        }
    )
    return subprocess.run(
        (
            str(SCRIPT),
            "--dry-run",
            "--no-attach",
            "--machine",
            "apollo-qvp",
            "--build-dir",
            str(build_dir),
            "--runfvp-bin",
            str(make_executable(fake_bin_dir / "runfvp")),
            *extra_args,
        ),
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_debug_without_target_lists_supported_targets() -> None:
    result = subprocess.run(
        (str(SCRIPT), "--machine", "apollo-qvp", "--debug"),
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    assert "Available --debug targets:" in result.stdout
    assert "rse, si_cl0, si_cl1, tf-a, u-boot, linux" in result.stdout


@pytest.mark.parametrize(
    ("target", "component", "entrypoint"),
    (
        ("rse", "tfm-bl1_1", "Reset_Handler"),
        ("si_cl0", "scp-si0", "arch_exception_reset"),
        ("si_cl1", "si-cl1-zephyr", "z_cstart"),
        ("tf-a", "tfa-bl2", "bl2_main"),
        ("u-boot", "u-boot", "_start"),
        ("linux", "linux", "start_kernel"),
    ),
)
def test_debug_enables_lite_cornea_and_starts_halted(
    tmp_path: Path,
    target: str,
    component: str,
    entrypoint: str,
) -> None:
    result = run_qvp_dry_run(tmp_path, "--debug", target)

    assert result.returncode == 0, result.stderr
    assert "debug backend: lite-cornea" in result.stdout
    assert f"debug target: {target}" in result.stdout
    assert f"component: {component}" in result.stdout
    assert f"entrypoint: {entrypoint}" in result.stdout
    assert "iris port: 7100" in result.stdout
    assert "lite-cornea-native/usr/bin/cornea" in result.stdout
    assert "--iris-server --iris-port 7100 --print-port-number" in result.stdout
    assert " --run" not in result.stdout


def test_non_debug_run_does_not_enable_iris(tmp_path: Path) -> None:
    result = run_qvp_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "lite-cornea" not in result.stdout
    assert "--iris-server" not in result.stdout


def test_debug_rejects_unknown_target(tmp_path: Path) -> None:
    result = run_qvp_dry_run(tmp_path, "--debug", "si-cl0")

    assert result.returncode != 0
    assert "invalid --debug target: si-cl0" in result.stderr


def test_debug_rejects_user_managed_iris_arguments(tmp_path: Path) -> None:
    result = run_qvp_dry_run(
        tmp_path,
        "--debug",
        "rse",
        "--",
        "--run",
    )

    assert result.returncode != 0
    assert "--run is managed by --debug" in result.stderr


def test_debug_accepts_custom_iris_port(tmp_path: Path) -> None:
    result = run_qvp_dry_run(
        tmp_path,
        "--debug",
        "linux",
        "--iris-port",
        "7110",
    )

    assert result.returncode == 0, result.stderr
    assert "iris port: 7110" in result.stdout
    assert "debug target: linux" in result.stdout
    assert "entrypoint: start_kernel" in result.stdout
    assert "--iris-server --iris-port 7110 --print-port-number" in result.stdout


def test_cornea_gdb_primes_iris_before_remote_attach(tmp_path: Path) -> None:
    fake_bin_dir = tmp_path / "bin"
    fake_bin_dir.mkdir()
    invocation_log = tmp_path / "invocations.log"
    gdb_script = tmp_path / "component.gdb"
    gdb_script.write_text("set pagination off\n", encoding="utf-8")
    cornea = make_executable(
        fake_bin_dir / "cornea",
        f'printf "cornea %s\\\\n" "$*" >> {invocation_log!s}',
    )
    make_executable(
        fake_bin_dir / "gdb-multiarch",
        f'printf "gdb %s\\\\n" "$*" >> {invocation_log!s}',
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin_dir}:{env['PATH']}"
        result = subprocess.run(
            (
                str(ROOT / "scripts/debug/run_fvp_cornea_gdb.sh"),
                "--iris-port",
                str(port),
                "--iris-instance",
                "component.test.cpu",
                "--gdb-script",
                str(gdb_script),
                "--cornea",
                str(cornea),
            ),
            cwd=ROOT,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    assert result.returncode == 0, result.stderr
    invocations = invocation_log.read_text(encoding="utf-8").splitlines()
    assert invocations[0] == (
        f"cornea --port {port} register-read component.test.cpu PC"
    )
    assert "set remote noack-packet off" in invocations[1]
    assert "target remote |" in invocations[1]
    assert invocations[1].endswith("-ex continue")

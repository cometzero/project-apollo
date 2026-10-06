"""BSP companion selection and tmux lifecycle entrypoint contracts."""

import json
import os
import shlex
import subprocess

import pytest

from test_run_qbox_yocto_sh import (
    ROOT, SCRIPT, TMUX_SCRIPT, QBOX_YOCTO_ENV_OVERRIDES,
    create_qboxconf, create_yocto_tree, touch_file,
)


@pytest.mark.parametrize("args,external,enabled", [
    ([], False, True),
    (["--no-vmcu"], False, False),
    (["--headless"], False, False),
    ([], True, False),
    (["--sil-kit"], False, True),
    (["--sil-kit", "--sil-kit-registry", "silkit://127.0.0.1:8500",
      "--sil-kit-allow-actuation", "--sil-kit-echo-fixture"], False, True),
])
def test_bsp_companion_selection(tmp_path, args, external, enabled):
    build, deploy, *_ = create_yocto_tree(tmp_path, machine="apollo-qvp")
    create_qboxconf(build, deploy, basename="nexios-bsp-initramfs")
    touch_file(deploy / "nexios-bsp-initramfs-apollo-qvp.wic")
    env = os.environ.copy()
    for key in (*QBOX_YOCTO_ENV_OVERRIDES, "QBOX_APOLLO_VMCU_UART_ENDPOINT"):
        env.pop(key, None)
    env.update(MACHINE="apollo-qvp", YOCTO_BUILD_DIR=str(build),
               OUT_DIR=str(tmp_path / "out"), SSH_PORT="24888",
               QBOX_TC397_QEMU=str(tmp_path / "tc397 with space/qemu-system-tricore"),
               QBOX_TC397_FIRMWARE=str(tmp_path / "firmware with space.elf"))
    if external:
        env["QBOX_APOLLO_VMCU_UART_ENDPOINT"] = "127.0.0.1:23456"
    result = subprocess.run(
        [str(SCRIPT), "--bsp", "--dry-run", "--no-attach", *args],
        cwd=ROOT, env=env, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert ("qbox_tc397.py" in result.stdout) == enabled
    assert ("tc397-uart.log" in result.stdout) == enabled
    if enabled:
        command = next(line.split("command: ", 1)[1] for line in result.stdout.splitlines()
                       if line.startswith("  command: "))
        argv = shlex.split(command)
        assert argv[argv.index("--qemu") + 1] == env["QBOX_TC397_QEMU"]
        assert argv[argv.index("--firmware") + 1] == env["QBOX_TC397_FIRMWARE"]
        assert "--foreground-runtime" in argv
        for option in ("--sil-kit", "--sil-kit-registry", "--sil-kit-allow-actuation", "--sil-kit-echo-fixture"):
            assert (option in argv) == (option in args)
        if "--sil-kit-registry" in args:
            assert argv[argv.index("--sil-kit-registry") + 1] == "silkit://127.0.0.1:8500"


def test_missing_companion_fails_before_stopping_existing_sessions(tmp_path):
    env = dict(os.environ, QBOX_TC397_QEMU=str(tmp_path / "missing"))
    env.pop("QBOX_APOLLO_VMCU_UART_ENDPOINT", None)
    result = subprocess.run([str(SCRIPT), "--bsp", "--no-attach"],
                            cwd=ROOT, env=env, text=True, capture_output=True,
                            timeout=10)
    assert result.returncode != 0
    assert "TC397 QEMU not executable" in result.stderr
    assert "Stopping" not in result.stdout


def test_tc397_pair_required(tmp_path):
    result = subprocess.run(
        [str(TMUX_SCRIPT), "--dry-run", "--tc397-qemu", str(tmp_path / "qemu")],
        cwd=ROOT, text=True, capture_output=True, timeout=10,
    )
    assert result.returncode != 0
    assert "must be used together" in result.stderr


@pytest.mark.parametrize('args,message', [
    (['--bsp', '--sil-kit', '--headless'], 'requires the local TC397'),
    (['--bsp', '--sil-kit', '--no-vmcu'], 'requires the local TC397'),
    (['--bsp', '--sil-kit-echo-fixture'], 'options require --sil-kit'),
    (['--bsp', '--sil-kit', '--sil-kit-registry', 'http://bad'], 'must be a silkit:// URI'),
])
def test_silkit_invalid_selection_fails_before_stopping_sessions(args, message):
    result = subprocess.run([str(SCRIPT), '--dry-run', *args], cwd=ROOT,
                            text=True, capture_output=True, timeout=10)
    assert result.returncode != 0
    assert message in result.stderr
    assert 'Stopping' not in result.stdout


def test_missing_silkit_fails_before_stopping_sessions(tmp_path):
    qemu = tmp_path / 'qemu'
    qemu.touch()
    qemu.chmod(0o755)
    fw = tmp_path / 'firmware'
    fw.touch()
    env = dict(os.environ, QBOX_TC397_QEMU=str(qemu), QBOX_TC397_FIRMWARE=str(fw),
               QBOX_SILKIT_BINARY=str(tmp_path / 'missing'))
    env.pop('QBOX_APOLLO_VMCU_UART_ENDPOINT', None)
    result = subprocess.run([str(SCRIPT), '--bsp', '--sil-kit'], cwd=ROOT,
                            env=env, text=True, capture_output=True, timeout=10)
    assert result.returncode != 0
    assert 'SIL Kit participant unavailable' in result.stderr
    assert 'Stopping' not in result.stdout


@pytest.mark.parametrize("explicit_deploy", [False, True])
def test_bsp_companion_uses_yocto_deploy(tmp_path, explicit_deploy):
    build, deploy, *_ = create_yocto_tree(tmp_path, machine="apollo-qvp")
    create_qboxconf(build, deploy, basename="nexios-bsp-initramfs")
    touch_file(deploy / "nexios-bsp-initramfs-apollo-qvp.wic")
    provider = deploy.parent.parent / "qemu-apollo-native/qemu-apollo-native.json"
    provider.parent.mkdir(parents=True)
    qemu = tmp_path / "native sysroot/usr/libexec/qemu-apollo/qemu-system-tricore"
    provider.write_text(json.dumps({"tricore_executable": str(qemu),
                                    "library_path": [str(tmp_path / "native libs")]}))
    env = os.environ.copy()
    for key in (*QBOX_YOCTO_ENV_OVERRIDES, "QBOX_APOLLO_VMCU_UART_ENDPOINT",
                "QBOX_TC397_QEMU", "QBOX_TC397_FIRMWARE"):
        env.pop(key, None)
    env.update(MACHINE="apollo-qvp", YOCTO_BUILD_DIR=str(build),
               OUT_DIR=str(tmp_path / "out"), SSH_PORT="24888")
    options = ["--deploy-dir", str(deploy)] if explicit_deploy else []
    if explicit_deploy:
        env["DEPLOY_DIR"] = str(tmp_path / "wrong-deploy")
    result = subprocess.run([str(SCRIPT), "--bsp", "--dry-run", "--no-attach", *options],
                            cwd=ROOT, env=env, text=True, capture_output=True,
                            timeout=30)
    assert result.returncode == 0, result.stderr
    command = next(line.split("command: ", 1)[1] for line in result.stdout.splitlines()
                   if line.startswith("  command: "))
    argv = shlex.split(command)
    assert argv[argv.index("--qemu") + 1] == str(qemu)
    assert argv[argv.index("--firmware") + 1] == str(deploy / "zephyr-vmcu-tc397.elf")


@pytest.mark.parametrize("manifest,expected", [
    (None, "TC397 provider missing"),
    ({"executable": "/old-aarch64"}, "invalid TC397 provider manifest"),
    ({"tricore_executable": "/missing-tricore"}, "TC397 QEMU not executable"),
])
def test_provider_errors_preserve_existing_sessions(tmp_path, manifest, expected):
    deploy = tmp_path / "deploy/images/apollo-qvp"
    deploy.mkdir(parents=True)
    if manifest is not None:
        provider = deploy.parent.parent / "qemu-apollo-native/qemu-apollo-native.json"
        provider.parent.mkdir()
        provider.write_text(json.dumps(manifest))
    env = os.environ.copy()
    for key in ("QBOX_TC397_QEMU", "QBOX_TC397_FIRMWARE", "QBOX_APOLLO_VMCU_UART_ENDPOINT"):
        env.pop(key, None)
    result = subprocess.run([str(SCRIPT), "--bsp", "--deploy-dir", str(deploy)],
                            cwd=ROOT, env=env, text=True, capture_output=True, timeout=10)
    assert result.returncode != 0
    assert expected in result.stderr
    assert "Stopping" not in result.stdout

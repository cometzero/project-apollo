from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_local.sh"


def run_dry_run(
    tmp_path: Path,
    target: str | None,
    *extra_args: str,
) -> subprocess.CompletedProcess[str]:
    conf = tmp_path / "apollo-qvp.lua"
    conf.write_text("return {}\n", encoding="utf-8")
    command = [str(SCRIPT), "--dry-run", "--no-attach", "--no-copy-disks"]
    if target is not None:
        command.extend(("--debug", target))
        command.extend(extra_args)
    else:
        command.append("--debug")
    env = os.environ | {
        "MACHINE": "apollo-fvp",
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        "OUT_DIR": str(tmp_path / "out"),
        "QBOX_CONF": str(conf),
        "TMUX_SESSION": "pytest-qbox-debug",
        "SSH_PORT_START": "24800",
        "SSH_PORT_END": "24899",
    }
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("target", "component", "entrypoint", "endpoint", "platform_params"),
    [
        (
            "qbox",
            "qbox-host",
            "sc_main",
            "127.0.0.1:12339",
            (),
        ),
        (
            "rse",
            "tfm-bl1_1",
            "Reset_Handler",
            "127.0.0.1:12340",
            (
                "platform.rse_cpu_pass.cpu_0.gdb_port=12340",
            ),
        ),
        (
            "si_cl0",
            "scp-si0",
            "arch_exception_reset",
            "127.0.0.1:12341",
            (
                "platform.si_cl0_cpu_0.gdb_port=12341",
            ),
        ),
        (
            "si_cl1",
            "si-cl1-zephyr",
            "z_cstart",
            "127.0.0.1:12342",
            (
                "platform.si_cl1_cpu_0.gdb_port=12342",
            ),
        ),
        (
            "tf-a",
            "tfa-bl2",
            "bl2_main",
            "127.0.0.1:12343",
            (
                "platform.ap_cpu_0.gdb_port=12343",
            ),
        ),
        (
            "u-boot",
            "u-boot",
            "_start",
            "127.0.0.1:12343",
            (
                "platform.ap_cpu_0.gdb_port=12343",
            ),
        ),
        (
            "linux",
            "linux",
            "start_kernel",
            "127.0.0.1:12343",
            (
                "platform.ap_cpu_0.gdb_port=12343",
            ),
        ),
    ],
)
def test_debug_target_selects_entrypoint_and_pauses_its_cpu(
    tmp_path: Path,
    target: str,
    component: str,
    entrypoint: str,
    endpoint: str,
    platform_params: tuple[str, ...],
) -> None:
    result = run_dry_run(tmp_path, target)

    assert result.returncode == 0, result.stderr
    assert f"  debug_target: {target}" in result.stdout
    assert f"  debug_component: {component}" in result.stdout
    assert f"  debug_entrypoint: {entrypoint}" in result.stdout
    assert f"  debug_endpoint: {endpoint}" in result.stdout
    assert f"  interactive_pane: gdb-{target}" in result.stdout
    for param in platform_params:
        assert param.replace('"', '\\"') in result.stdout
    if target == "qbox":
        assert "  debug_attach_gate: \n" in result.stdout
    else:
        assert (
            "  debug_attach_gate: qbox-platform.log contains "
            "QBox GDB entry breakpoint reached:"
        ) in result.stdout
    if target == "qbox":
        assert "--host-gdb-script" in result.stdout
        assert "time_sync_strategy=mcips" not in result.stdout
    else:
        assert "--host-gdb-script" not in result.stdout


@pytest.mark.parametrize("target", ["invalid", "si-cl0", "tf_a"])
def test_debug_rejects_unknown_target(tmp_path: Path, target: str) -> None:
    result = run_dry_run(tmp_path, target)

    assert result.returncode != 0
    assert "invalid --debug target" in result.stderr


def test_debug_without_target_lists_supported_targets(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, None)

    assert result.returncode == 0
    assert result.stderr == ""
    assert "Available --debug targets:" in result.stdout
    for target in ("qbox", "rse", "si_cl0", "si_cl1", "tf-a", "u-boot", "linux"):
        assert target in result.stdout


def test_probe_mode_uses_headless_agent_runner(tmp_path: Path) -> None:
    result = run_dry_run(
        tmp_path,
        "tf-a",
        "--debug-mode",
        "probe",
        "--debug-timeout",
        "90",
    )

    assert result.returncode == 0, result.stderr
    assert "  headless: 1" in result.stdout
    assert "  debug_mode: probe" in result.stdout
    assert "run_agent_qbox_debug.py" in result.stdout
    assert "--breakpoint bl2_main" in result.stdout
    assert "--timeout 90" in result.stdout
    assert "gdb_snapshot_hold" not in result.stdout
    assert "--wait-marker QBox\\ GDB\\ entry\\ breakpoint\\ reached:" in result.stdout
    assert "run_qbox_apollo_fvp_full_tmux.sh" not in result.stdout

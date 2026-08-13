from __future__ import annotations
# noqa: SIZE_OK — one focused file owns the QBox SI debug contract.

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

import pytest

from scripts.debug import run_gic720ae_si_gdb_smoke as si_gdb_smoke
from scripts.run import run_qbox_apollo_fvp_full as full_runner


ROOT = Path(__file__).resolve().parents[1]
DEBUG_COMMON = ROOT / "scripts/run/qbox_debug_common.sh"
LOCAL_LAUNCHER = ROOT / "run_qbox_local.sh"
MULTI_DEBUG_LAUNCHER = ROOT / "run_qbox_local_debug.sh"
SMOKE = ROOT / "scripts/debug/run_gic720ae_si_gdb_smoke.py"
SYMBOLS = ROOT / "build/local-apollo-qvp/debug/symbols.json"
FULL_RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"


def configured_selector(target: str) -> tuple[str, ...]:
    command = f"""
set -euo pipefail
die() {{ printf 'error: %s\\n' "$*" >&2; exit 1; }}
source {shlex.quote(str(DEBUG_COMMON))}
DEBUG_TARGET={shlex.quote(target)}
qbox_debug_configure_target
printf '%s|%s|%s|%s|%s\\n' \
  "$DEBUG_COMPONENT" "$DEBUG_ENTRYPOINT" "$DEBUG_ENDPOINT" \
  "$DEBUG_CPU_PARAM" "${{DEBUG_PLATFORM_PARAMS[*]}}"
"""
    result = subprocess.run(
        ["bash", "-c", command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(result.stdout.strip().split("|"))


def platform_params_from_dry_run(stdout: str) -> tuple[str, ...]:
    command_line = next(
        line.removeprefix("  command: ")
        for line in stdout.splitlines()
        if line.startswith("  command: ")
    )
    argv = shlex.split(command_line)
    return tuple(
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "--platform-param"
    )


def command_from_dry_run(stdout: str) -> list[str]:
    command_line = next(
        line.removeprefix("  command: ")
        for line in stdout.splitlines()
        if line.startswith("  command: ")
    )
    return shlex.split(command_line)


def supported_options(command: list[str]) -> set[str]:
    result = subprocess.run(
        [*command, "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(re.findall(r"--[a-z0-9][a-z0-9-]*", result.stdout))


def produced_options(command: list[str]) -> set[str]:
    return {
        argument.partition("=")[0]
        for argument in command
        if argument.startswith("--")
    }


def selector_surface(target: str) -> tuple[str, str]:
    command = f"""
set -euo pipefail
die() {{ printf 'error: %s\\n' "$*" >&2; exit 1; }}
source {shlex.quote(str(DEBUG_COMMON))}
DEBUG_TARGET={shlex.quote(target)}
qbox_debug_configure_target
printf '%s|%s\\n' "$DEBUG_ENDPOINT" "${{DEBUG_PLATFORM_PARAMS[*]}}"
"""
    result = subprocess.run(
        ["bash", "-c", command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    endpoint, params = result.stdout.strip().split("|")
    return endpoint, params


def test_si_selectors_use_distinct_firmware_and_endpoints() -> None:
    # Given: the unchanged shared target mapper used by local and Yocto launchers.
    # When: both Safety Island selectors are configured through the real shell API.
    cl0 = configured_selector("si_cl0")
    cl1 = configured_selector("si_cl1")

    # Then: each ELF, CPU, and QEMU endpoint remains distinct.
    assert cl0 == (
        "scp-si0",
        "arch_exception_reset",
        "127.0.0.1:12341",
        "platform.si_cl0_cpu_0",
        "platform.si_cl0_cpu_0.gdb_port=12341",
    )
    assert cl1 == (
        "si-cl1-zephyr",
        "z_cstart",
        "127.0.0.1:12342",
        "platform.si_cl1_cpu_0",
        "platform.si_cl1_cpu_0.gdb_port=12342",
    )


def test_multi_debug_launcher_opens_one_five_pe_si_endpoint(
    tmp_path: Path,
) -> None:
    # Given: the current real multi-domain launcher with manifest generation disabled.
    env = os.environ.copy()
    env.update({"LOCAL_DEBUG_SKIP_MANIFEST": "1", "RUN_STAMP": "pin-task16"})

    # When: its dry-run surface resolves the canonical runner command.
    result = subprocess.run(
        [
            str(MULTI_DEBUG_LAUNCHER),
            "--dry-run",
            "--no-attach",
            "--multi-session",
            "--out-dir",
            str(tmp_path / "multi-debug"),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: the launcher requests one listener for each split-SI instance.
    assert result.returncode == 0, result.stderr
    params = platform_params_from_dry_run(result.stdout)
    assert "platform.si_cl0_cpu_0.gdb_port=12341" in params
    assert "platform.si_cl1_cpu_0.gdb_port=12342" in params


def test_pin_headless_interactive_debug_is_rejected() -> None:
    # Given: a local interactive Safety Island debug selection.
    # When: the user combines it with the headless layout.
    result = subprocess.run(
        [
            str(LOCAL_LAUNCHER),
            "--headless",
            "--debug",
            "si_cl0",
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: the launcher rejects the incompatible surface before any runtime starts.
    assert result.returncode != 0
    assert "--debug requires the interactive tmux layout" in result.stderr


def test_noninteractive_si_debug_uses_normal_full_system(tmp_path: Path) -> None:
    # Given: the public SI CL0 debug selector in noninteractive server mode.
    result = subprocess.run(
        [
            str(LOCAL_LAUNCHER),
            "--debug",
            "si_cl0",
            "--debug-mode",
            "server",
            "--debug-timeout",
            "1",
            "--out-dir",
            str(tmp_path / "server"),
            "--no-persistent-rse-state",
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: the child runner uses the normal full-system topology.
    assert result.returncode == 0, result.stderr


def test_split_si_selectors_use_distinct_endpoints() -> None:
    # Given: the real selector mapper for the normal split-SI topology.
    # When: CL0 and CL1 are selected independently.
    observed = {
        "cl0": selector_surface("si_cl0"),
        "cl1": selector_surface("si_cl1"),
    }

    # Then: each QEMU instance uses its own endpoint and CPU parameter.
    expected = {
        "cl0": (
            "127.0.0.1:12341",
            "platform.si_cl0_cpu_0.gdb_port=12341",
        ),
        "cl1": (
            "127.0.0.1:12342",
            "platform.si_cl1_cpu_0.gdb_port=12342",
        ),
    }
    assert observed == expected, (
        f"expected distinct split-SI endpoints; observed={observed!r}"
    )


def test_generated_manifest_carries_single_si_selector_metadata() -> None:
    # Given: the non-empty manifest generated by the required local-build entrypoint.
    decoded = json.loads(SYMBOLS.read_text(encoding="utf-8"))

    # When: consumers read both generated Safety Island domain records.
    components = decoded["components"]
    observed = {
        name: {
            key: components[name].get(key)
            for key in ("remote", "gdb_thread", "mpidr")
        }
        for name in ("domain-si0", "domain-si1")
    }

    # Then: both selectors are complete and share one remote without aliasing PEs.
    expected = {
        "domain-si0": {
            "remote": "127.0.0.1:12341",
            "gdb_thread": 1,
            "mpidr": "0x0",
        },
        "domain-si1": {
            "remote": "127.0.0.1:12341",
            "gdb_thread": 2,
            "mpidr": "0x10000",
        },
    }
    assert observed == expected, (
        "expected generated endpoint/thread/MPIDR selector metadata; "
        f"observed={observed!r}"
    )


def test_smoke_cli_exposes_required_real_attach_arguments() -> None:
    # Given: the planned Task 16 real-attach smoke entrypoint.
    # When: a consumer asks the executable for its argument contract.
    result = subprocess.run(
        [sys.executable, str(SMOKE), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: every required launcher, selector, endpoint, and evidence input exists.
    assert result.returncode == 0, result.stderr
    for option in (
        "--launcher",
        "--symbols-json",
        "--require-manifest-hash",
        "--endpoint",
        "--cl0-symbol",
        "--cl1-symbol",
        "--expect-threads",
        "--timeout",
        "--out-dir",
    ):
        assert option in result.stdout


def test_smoke_rejects_retired_endpoint_before_launch(tmp_path: Path) -> None:
    # Given: a complete smoke request using the retired split-SI endpoint.
    command = [
        sys.executable,
        str(SMOKE),
        "--launcher",
        str(MULTI_DEBUG_LAUNCHER),
        "--symbols-json",
        str(SYMBOLS),
        "--endpoint",
        "127.0.0.1:12342",
        "--cl0-symbol",
        "arch_exception_reset",
        "--cl1-symbol",
        "z_cstart",
        "--expect-threads",
        "5",
        "--timeout",
        "1",
        "--out-dir",
        str(tmp_path / "legacy"),
    ]

    # When: the smoke validates the endpoint before starting QBox.
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    # Then: it reports the canonical endpoint and selector migration path.
    assert result.returncode == 2
    assert "12342 is retired" in result.stderr
    assert "12341" in result.stderr
    assert "thread 1" in result.stderr
    assert "thread 2" in result.stderr


def test_smoke_rejects_unknown_endpoint_before_launch(tmp_path: Path) -> None:
    # Given: a complete smoke request using an unrelated endpoint.
    command = [
        sys.executable,
        str(SMOKE),
        "--launcher",
        str(MULTI_DEBUG_LAUNCHER),
        "--symbols-json",
        str(SYMBOLS),
        "--endpoint",
        "127.0.0.1:22341",
        "--cl0-symbol",
        "arch_exception_reset",
        "--cl1-symbol",
        "z_cstart",
        "--expect-threads",
        "5",
        "--timeout",
        "1",
        "--out-dir",
        str(tmp_path / "unknown"),
    ]

    # When: the smoke validates the endpoint before starting QBox.
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    # Then: it rejects the endpoint and names the only supported address.
    assert result.returncode == 2
    assert "unsupported SI GDB endpoint" in result.stderr
    assert "127.0.0.1:12341" in result.stderr


def test_debug_argv_schema_matches_both_runner_consumers(tmp_path: Path) -> None:
    # Given: the exact debug launcher command produced at the public boundary.
    env = os.environ.copy()
    env.update({"LOCAL_DEBUG_SKIP_MANIFEST": "1", "RUN_STAMP": "task16-schema"})
    dry_run = subprocess.run(
        [
            str(MULTI_DEBUG_LAUNCHER),
            "--dry-run",
            "--no-attach",
            "--multi-session",
            "--out-dir",
            str(tmp_path / "schema"),
        ],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    front_command = command_from_dry_run(dry_run.stdout)
    interpreter = Path(shutil.which(front_command[0]) or "").resolve()

    # When: both producer argv vectors are compared with their parser help.
    front_missing = produced_options(front_command[2:]) - supported_options(
        [sys.executable, str(FULL_RUNNER)]
    )
    front_args = full_runner.parse_args(front_command[2:])
    artifacts = full_runner.resolved_artifacts(front_args)
    child_command = full_runner.child_command(front_args, artifacts)
    child_missing = produced_options(child_command[3:]) - supported_options(
        [sys.executable, str(FULL_RUNNER), "--runtime-child"]
    )

    # Then: executable/module identity and every produced option are accepted.
    assert interpreter == Path(sys.executable).resolve()
    assert Path(front_command[1]).resolve() == FULL_RUNNER
    assert child_command[:3] == [sys.executable, str(FULL_RUNNER), "--runtime-child"]
    assert front_missing == set()
    assert child_missing == set()


def test_host_release_requires_observed_sc_main_stop() -> None:
    # Given: a successful host GDB detach that never stopped in sc_main.
    transcript = "0x00007ffff7fe4540 in ld-linux\nInferior detached\n"

    # When: the smoke qualifies the host handoff transcript.
    with pytest.raises(RuntimeError, match="sc_main"):
        si_gdb_smoke.validate_host_release(transcript, 0)

    # Then: an explicit controlled sc_main stop marker is accepted.
    si_gdb_smoke.validate_host_release(
        "Temporary breakpoint, sc_main\nTASK16_HOST_SC_MAIN_REACHED=1\n",
        0,
    )


def test_terminal_child_failure_overrides_listener_readiness(tmp_path: Path) -> None:
    # Given: a listener observation paired with a terminal child failure.
    platform_out = tmp_path / "platform"
    platform_out.mkdir()
    (platform_out / "qbox-run.status").write_text("1\n", encoding="utf-8")
    (platform_out / "result.json").write_text(
        json.dumps({"blocker": "child_failed:1", "child_returncode": 1}),
        encoding="utf-8",
    )

    # When: the smoke validates liveness before the first SI connection.
    with pytest.raises(RuntimeError, match="child_failed:1"):
        si_gdb_smoke.require_live_child(platform_out, listener_ready=True)

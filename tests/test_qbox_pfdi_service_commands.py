from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scripts.run.qbox_pfdi_probe import pfdi_probe_commands


MOCK_GUEST = r'''
pidof() { test -f "$PFDI_STATE" && echo 123; }
od() { echo 600; }
sleep() { /bin/sleep 0.001; }
kill() { echo kill >> "$PFDI_TRACE"; rm -f "$PFDI_STATE"; }
systemctl() {
    echo "systemctl $*" >> "$PFDI_TRACE"
    if [ "$1" = "$PFDI_FAILURE" ]; then
        echo "systemctl $1 failed" >&2; return 1
    fi
    case "$1" in
        stop) rm -f "$PFDI_STATE";;
        start) touch "$PFDI_STATE";;
        is-active) test -f "$PFDI_STATE";;
        *) return 2;;
    esac
}
journalctl() {
    echo "journalctl $*" >> "$PFDI_TRACE"
    cat "$PFDI_LOG"
    if [ "$PFDI_FAILURE" = journal ]; then
        echo 'journal read failed' >&2; return 1
    fi
}
pfdi-sample-app() {
    case " $* " in
        *' -m single '*)
            echo single >> "$PFDI_TRACE"
            if [ -f "$PFDI_STATE" ]; then
                echo 'concurrent app detected' >&2; return 1
            fi
            if [ "$PFDI_FAILURE" = single ]; then
                echo 'single diagnostic failed' >&2; return 1
            fi;;
        *) echo restart >> "$PFDI_TRACE"; touch "$PFDI_STATE";;
    esac
}
pfdi-cli() {
    if [ "$PFDI_FAILURE" = force ]; then
        echo 'force injection failed' >&2; return 1
    fi
    echo "CPU$2: injected force error"
    echo "CPU$2: PFDI Online (OnL) test failed: Input/output error (errno=5)" >> "$PFDI_LOG"
}
'''


def run_guest_commands(
    tmp_path: Path, systemd: bool, failure: str = ""
) -> tuple[str, str]:
    systemd_dir = tmp_path / "systemd"
    if systemd:
        systemd_dir.mkdir()
    state = tmp_path / "active"
    state.touch()
    log = tmp_path / ("journal" if systemd else "pfdi-sample-app.log")
    log.write_text("Loading config V1.0: running 4 tasks every 600 ms\n")
    trace = tmp_path / "commands"
    commands = pfdi_probe_commands()
    script = "\n".join(commands[index] for index in (1, 3, 4, 7))
    script = script.replace("/run/systemd/system", str(systemd_dir))
    script = script.replace("/run/pfdi-sample-app.log", str(log))
    result = subprocess.run(
        ["bash", "-c", MOCK_GUEST + script],
        env={
            **os.environ, "PFDI_STATE": str(state), "PFDI_LOG": str(log),
            "PFDI_TRACE": str(trace), "PFDI_FAILURE": failure,
        },
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    if failure != "start":
        assert state.exists(), "the original service must be restored"
    return result.stdout + result.stderr, trace.read_text()


@pytest.mark.parametrize("systemd", [False, True], ids=["bsp", "product"])
def test_pfdi_commands_use_native_service_and_log(tmp_path: Path, systemd: bool) -> None:
    output, trace = run_guest_commands(tmp_path, systemd)
    for marker in ("service", "online", "force_error_cpu0", "force_error_cpu3"):
        assert f"pfdi_{marker}_rc:0" in output
    assert "concurrent app" not in output
    if systemd:
        assert "systemctl stop pfdi-app.service\nsingle\nsystemctl start" in trace
        assert "journalctl --no-pager -b -u pfdi-app.service -o cat" in trace
        assert "kill\n" not in trace and "restart\n" not in trace
    else:
        assert trace == "kill\nsingle\nrestart\n"


@pytest.mark.parametrize("systemd", [False, True], ids=["bsp", "product"])
def test_pfdi_commands_restore_service_after_diagnostic_failure(
    tmp_path: Path, systemd: bool
) -> None:
    output, _ = run_guest_commands(tmp_path, systemd, "single")
    assert "pfdi_online_rc:1" in output
    assert "single diagnostic failed" in output


@pytest.mark.parametrize("failure", ["stop", "start"])
def test_pfdi_commands_reject_service_control_failure(tmp_path: Path, failure: str) -> None:
    output, trace = run_guest_commands(tmp_path, True, failure)
    assert "pfdi_online_rc:1" in output
    assert f"systemctl {failure} failed" in output
    assert "systemctl start pfdi-app.service" in trace
    if failure == "stop":
        assert "single\n" not in trace


def test_pfdi_commands_reject_failed_journal_read_even_with_matching_text(tmp_path: Path) -> None:
    output, _ = run_guest_commands(tmp_path, True, "journal")
    assert "pfdi_service_rc:1" in output
    assert "pfdi_force_error_cpu0_rc:1" in output
    assert "journal read failed" in output


@pytest.mark.parametrize("systemd", [False, True], ids=["bsp", "product"])
def test_pfdi_commands_reject_failed_fault_injection(tmp_path: Path, systemd: bool) -> None:
    output, _ = run_guest_commands(tmp_path, systemd, "force")
    assert "pfdi_force_error_cpu0_rc:1" in output
    assert "force injection failed" in output


def test_pfdi_commands_remain_posix_shell_syntax() -> None:
    subprocess.run(["sh", "-n"], input="\n".join(pfdi_probe_commands()), text=True, check=True)

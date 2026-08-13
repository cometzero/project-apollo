from __future__ import annotations
# noqa: SIZE_OK — one focused file owns the SI0 runner contract.

import argparse
import importlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
from typing import TypedDict

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
full_runner = importlib.import_module("scripts.run.run_qbox_apollo_fvp_full")


ENTER_CLI = b"\x05"
EXIT_CLI = b"\x04"
COMMAND = "test gic_power"


class FakeChildReceipt(TypedDict):
    fifo: str
    fifo_mode: int
    payload_hex: str
    pid: int
    process_group: int


class CommandRecord(TypedDict):
    command: str
    sha256: str
    started_at: str
    done_at: str | None
    exit_at: str | None
    timed_out: bool
    transport_returncode: int


class TransportReceipt(TypedDict):
    fifo_created_before_child: bool
    stale_fifo_removed: bool
    fifo_cleaned: bool
    child_returncode: int | None
    commands: list[CommandRecord]


def transport_args(tmp_path: Path, command: str, timeout: float = 2.0) -> argparse.Namespace:
    return argparse.Namespace(
        out_dir=tmp_path,
        si_cl0_command=[command],
        si_cl0_command_timeout=timeout,
    )


def fake_reader_command(receipt_path: Path, expected_bytes: int) -> list[str]:
    script = """
import json
import os
from pathlib import Path
import stat

fifo = os.environ["QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE"]
payload = b""
with open(fifo, "rb", buffering=0) as stream:
    while len(payload) < int(os.environ["EXPECTED_BYTES"]):
        chunk = stream.read(4096)
        if not chunk:
            break
        payload += chunk
Path(os.environ["FAKE_RECEIPT"]).write_text(json.dumps({
    "fifo": fifo,
    "fifo_mode": os.stat(fifo).st_mode,
    "payload_hex": payload.hex(),
    "pid": os.getpid(),
    "process_group": os.getpgrp(),
}), encoding="utf-8")
"""
    return [sys.executable, "-c", script]


def run_fake_reader(
    tmp_path: Path,
    command: str = COMMAND,
) -> tuple[int, FakeChildReceipt, TransportReceipt]:
    payload = ENTER_CLI + command.encode("ascii") + b"\n" + EXIT_CLI
    receipt_path = tmp_path / "fake-child.json"
    env = os.environ.copy()
    env["EXPECTED_BYTES"] = str(len(payload))
    env["FAKE_RECEIPT"] = str(receipt_path)
    args = transport_args(tmp_path, command)

    rc = full_runner.run_child_with_si_cl0_transport(
        args,
        fake_reader_command(receipt_path, len(payload)),
        env,
    )

    child_receipt: FakeChildReceipt = json.loads(receipt_path.read_text())
    return rc, child_receipt, args.si_cl0_command_transport


def test_real_child_reads_exact_ordered_scp_cli_bytes(tmp_path: Path) -> None:
    # Given: a real child process that opens the runner-provided named FIFO.
    # When: the SI0 command transport runs one SCP CLI command.
    rc, child, transport = run_fake_reader(tmp_path)

    # Then: raw UART bytes and the structured lifecycle receipt are exact.
    expected = ENTER_CLI + b"test gic_power\n" + EXIT_CLI
    assert rc == 0
    assert stat.S_ISFIFO(child["fifo_mode"])
    assert bytes.fromhex(child["payload_hex"]) == expected
    assert child["process_group"] == child["pid"]
    assert not Path(child["fifo"]).exists()
    assert transport["fifo_created_before_child"] is True
    assert transport["fifo_cleaned"] is True
    [record] = transport["commands"]
    assert record["command"] == COMMAND
    assert record["sha256"] == full_runner.hashlib.sha256(COMMAND.encode()).hexdigest()
    assert record["started_at"]
    assert record["done_at"]
    assert record["exit_at"]
    assert record["timed_out"] is False
    assert record["transport_returncode"] == 0


def test_metacharacters_are_uart_data_and_never_shell_code(tmp_path: Path) -> None:
    # Given: printable shell metacharacters and a path that must not be created.
    sentinel = tmp_path / "must-not-exist"
    command = f"test gic_power; touch {sentinel}"

    # When: the command crosses the SI0 boundary.
    rc, child, _transport = run_fake_reader(tmp_path, command)

    # Then: the exact text is UART data and no shell evaluates it.
    assert rc == 0
    assert bytes.fromhex(child["payload_hex"]) == (
        ENTER_CLI + command.encode("ascii") + b"\n" + EXIT_CLI
    )
    assert not sentinel.exists()


@pytest.mark.parametrize("command", ["", "test\ngic_power", "\x05test", "café"])
def test_command_boundary_rejects_empty_multiline_control_or_non_ascii(
    tmp_path: Path,
    command: str,
) -> None:
    # Given: malformed or control-bearing untrusted command text.
    args = transport_args(tmp_path, command)

    # When/Then: validation rejects it before any FIFO or child exists.
    with pytest.raises(full_runner.SiCl0CommandValidationError):
        full_runner.run_child_with_si_cl0_transport(args, ["/bin/true"], os.environ.copy())
    assert not (tmp_path / "si-cl0-uart-input.fifo").exists()


def test_timeout_fails_and_terminates_child_and_cleans_fifo(tmp_path: Path) -> None:
    # Given: a real child that records its PID but never opens the FIFO.
    pid_path = tmp_path / "child.pid"
    script = (
        "import os,time; "
        f"open({str(pid_path)!r},'w').write(str(os.getpid())); "
        "time.sleep(60)"
    )
    args = transport_args(tmp_path, COMMAND, timeout=0.2)

    # When: the per-command FIFO-open deadline expires.
    rc = full_runner.run_child_with_si_cl0_transport(
        args,
        [sys.executable, "-c", script],
        os.environ.copy(),
    )

    # Then: the run fails, reports timeout, reaps the child, and removes FIFO.
    assert rc != 0
    pid = int(pid_path.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    [record] = args.si_cl0_command_transport["commands"]
    assert record["timed_out"] is True
    assert record["transport_returncode"] == 124
    assert args.si_cl0_command_transport["fifo_cleaned"] is True
    assert not (tmp_path / "si-cl0-uart-input.fifo").exists()


def test_child_early_exit_is_not_reported_as_transport_success(tmp_path: Path) -> None:
    # Given: a child that exits successfully before opening the input FIFO.
    args = transport_args(tmp_path, COMMAND)

    # When: the transport observes that early exit.
    rc = full_runner.run_child_with_si_cl0_transport(
        args,
        [sys.executable, "-c", "raise SystemExit(0)"],
        os.environ.copy(),
    )

    # Then: transport failure overrides the misleading child zero status.
    assert rc != 0
    [record] = args.si_cl0_command_transport["commands"]
    assert record["timed_out"] is False
    assert record["transport_returncode"] == 125
    assert record["exit_at"] is None
    assert args.si_cl0_command_transport["child_returncode"] == 0
    assert args.si_cl0_command_transport["fifo_cleaned"] is True


def test_stale_fifo_is_replaced_and_recorded(tmp_path: Path) -> None:
    # Given: a stale FIFO left by an interrupted prior run.
    fifo_path = tmp_path / "si-cl0-uart-input.fifo"
    os.mkfifo(fifo_path)

    # When: a new real child transport run starts.
    rc, _child, transport = run_fake_reader(tmp_path)

    # Then: only the stale FIFO is replaced and the cleanup receipt records it.
    assert rc == 0
    assert transport["stale_fifo_removed"] is True
    assert transport["fifo_cleaned"] is True
    assert not fifo_path.exists()


def test_non_fifo_collision_is_preserved_and_rejected(tmp_path: Path) -> None:
    # Given: a regular file at the managed FIFO path.
    fifo_path = tmp_path / "si-cl0-uart-input.fifo"
    fifo_path.write_text("user-owned", encoding="utf-8")
    args = transport_args(tmp_path, COMMAND)

    # When/Then: the boundary refuses destructive replacement.
    with pytest.raises(full_runner.SiCl0CommandValidationError):
        full_runner.run_child_with_si_cl0_transport(
            args,
            ["/bin/true"],
            os.environ.copy(),
        )
    assert fifo_path.read_text(encoding="utf-8") == "user-owned"


def test_no_command_keeps_uart_read_file_unset(tmp_path: Path) -> None:
    # Given/When: the existing no-command CLI is parsed.
    args = full_runner.parse_args(["--out-dir", str(tmp_path)])

    # Then: the legacy child environment and behavior remain opt-in free.
    assert args.si_cl0_command == []
    assert "QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE" not in (
            full_runner.full_system_child_environment(args)
    )


def test_command_rejects_keep_running_child_lifecycle(tmp_path: Path) -> None:
    # Given: mutually incompatible command cleanup and keep-running requests.
    argv = [
        "--out-dir",
        str(tmp_path),
        "--si-cl0-command",
        COMMAND,
        "--keep-running-after-pass",
    ]

    # When/Then: the CLI rejects an unbounded child lifecycle.
    with pytest.raises(SystemExit):
        full_runner.parse_args(argv)


def test_sigterm_cancels_child_group_and_cleans_fifo(tmp_path: Path) -> None:
    # Given: a transport harness whose real child never opens the FIFO.
    child_script = (
        "import json,os,time; "
        "print(json.dumps({'pid':os.getpid(),'pgid':os.getpgrp()}),flush=True); "
        "time.sleep(60)"
    )
    harness_script = f"""
import argparse
import json
import os
from pathlib import Path
import sys
from scripts.run import run_qbox_apollo_fvp_full as runner
args = argparse.Namespace(
    out_dir=Path({str(tmp_path)!r}),
    si_cl0_command=[{COMMAND!r}],
    si_cl0_command_timeout=30.0,
)
rc = runner.run_child_with_si_cl0_transport(
    args,
    [sys.executable, "-c", {child_script!r}],
    os.environ.copy(),
)
print(json.dumps({{"rc": rc, "transport": args.si_cl0_command_transport}}), flush=True)
"""
    harness = subprocess.Popen(
        [sys.executable, "-c", harness_script],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert harness.stdout is not None
    child = json.loads(harness.stdout.readline())

    # When: the canonical runner process receives SIGTERM.
    os.kill(harness.pid, signal.SIGTERM)
    receipt = json.loads(harness.stdout.readline())
    harness_rc = harness.wait(timeout=5)

    # Then: signal handling returns failure, reaps the child group, and cleans FIFO.
    assert harness_rc == 0
    assert receipt["rc"] == 130
    assert receipt["transport"]["cancelled"] is True
    assert receipt["transport"]["fifo_cleaned"] is True
    assert child["pid"] == child["pgid"]
    with pytest.raises(ProcessLookupError):
        os.kill(child["pid"], 0)
    assert not (tmp_path / "si-cl0-uart-input.fifo").exists()

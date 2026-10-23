"""Host-only transport/lifecycle regressions; no real launcher or DUT runs."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import select
import shutil
import socket
import subprocess
import sys
import threading
import time

import pytest

from test_automation.targets.qbox import controller
from test_automation.targets.qbox.networking import FIFOS, QBoxNetworkManager
from test_automation.targets.qbox.plugin import make_qbox_bundle
from test_automation.targets.registry import get_factory


@pytest.fixture
def manager(tmp_path):
    result = QBoxNetworkManager({"port_map": {"default_console": "ap", "scp": "si_cl0"}})
    result.bind(tmp_path, 22222, lambda: True)
    result.connect()
    yield result
    result.disconnect()


def append(manager, domain, text):
    with manager.log_path(domain).open("a") as stream:
        stream.write(text)


@contextmanager
def uart_peer(manager, domain, respond):
    """One real FIFO exchange with a bounded, harmless host peer."""
    path = manager.log_dir / FIFOS[domain]
    os.mkfifo(path, 0o600)
    fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    received, errors = [], []
    stop = threading.Event()

    def run():
        try:
            while not stop.is_set():
                if select.select([fd], [], [], .02)[0]:
                    payload = os.read(fd, 65536)
                    received.append(payload)
                    respond(payload)
                    return
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=run)
    thread.start()
    try:
        yield received
    finally:
        stop.set()
        thread.join(timeout=2)
        os.close(fd)
        assert not thread.is_alive(), "host UART peer did not stop"
        if errors:
            raise errors[0]


def test_ap_command_uses_live_shell_output_and_real_nonzero_exit(manager):
    append(manager, "ap", "__QBOX_BEGIN_old\nSTALE PASS\n__QBOX_END_old:0\n")

    def shell(payload):
        # Only a fixed, harmless test command is executed by this local shell.
        result = subprocess.run(["bash", "-c", payload.decode()], capture_output=True, timeout=2)
        append(manager, "ap", payload.decode() + result.stdout.decode())

    with uart_peer(manager, "ap", shell):
        rc, output = manager.execute_command_with_prompt_capture(
            manager.get_port("ap"), "cat <<< 'LIVE RESPONSE'; exit 7", timeout=1)
    assert (rc, output) == (7, "LIVE RESPONSE")
    record = json.loads((manager.log_dir / "commands.jsonl").read_text())
    assert record["status_semantics"] == "guest_exit_code"
    assert record["output"] == "LIVE RESPONSE"


def test_ap_echo_and_stale_pass_cannot_complete_command(manager):
    append(manager, "ap", "__QBOX_BEGIN_old\nPASS\n__QBOX_END_old:0\n")
    with uart_peer(manager, "ap", lambda payload: append(manager, "ap", payload.decode())):
        rc, output = manager.execute_command_with_prompt_capture(5, "echo PASS", timeout=.1)
    assert rc == 124
    assert "__QBOX_END_old" not in output


def test_uart_regular_file_is_not_modified(manager):
    path = manager.log_dir / FIFOS["ap"]
    path.write_text("keep this")
    with pytest.raises(ValueError, match="not a FIFO"):
        manager.run_cmd(5, "true", timeout=.1)
    assert path.read_text() == "keep this"


@pytest.mark.parametrize("before_exit", ["End\r\n", ""])
def test_si0_frames_command_and_waits_for_later_completion(manager, before_exit):
    port, command = manager.get_port("si_cl0"), "test smcf"
    manager.command_completion_patterns[(port, command)] = r"sample: 42"
    append(manager, "si_cl0", "[CLI_DEBUGGER_MODULE] Entering CLI\nEnd\nsample: 42\n"
                              "[CLI_DEBUGGER_MODULE] Exiting CLI\n")

    def reply(payload):
        append(manager, "si_cl0", "[CLI_DEBUGGER_MODULE] Entering CLI\r\n> test smcf\r\n"
                                  + before_exit + "[CLI_DEBUGGER_MODULE] Exiting CLI\r\n")
        time.sleep(.08)
        append(manager, "si_cl0", "sample: 42\r\n")

    with uart_peer(manager, "si_cl0", reply) as received:
        rc, output = manager.execute_command_with_prompt_capture(port, command, timeout=1)
    assert received == [b"\x05test smcf\n\x04"]
    assert rc == 0 and output.count("sample: 42") == 1
    assert manager.command_records[-1]["status_semantics"] == "firmware_response"


@pytest.mark.parametrize("response,expected", [
    ("uart:~$ version\nZephyr version 4.1\nuart:~$ ", 0),
    ("uart:~$ version\nuart:~$ ", 1),
    ("uart:~$ version\nError: invalid argument\nuart:~$ ", 1),
])
def test_si1_response_status_is_distinct_from_guest_exit_code(manager, response, expected):
    with uart_peer(manager, "si_cl1", lambda payload: append(manager, "si_cl1", response)):
        rc, output = manager.execute_command_with_prompt_capture(3, "version", timeout=.3)
    assert rc == expected
    assert output == response
    assert manager.command_records[-1]["status_semantics"] == "firmware_response"


def test_stopped_runtime_is_transport_error_not_firmware_rejection(manager):
    with uart_peer(manager, "si_cl0", lambda payload: None):
        manager.is_running = lambda: False
        rc, _ = manager.execute_command_with_prompt_capture(2, "test smcf", timeout=1)
    assert rc == 125


def test_fresh_log_cursor_and_prompt_search_share_normalization(manager):
    append(manager, "si_cl0", "\x1b[32mOLD\x1b[0m\r\n")
    before = len(manager.read_log("si_cl0"))
    append(manager, "si_cl0", "\x1b[32mNEW\x1b[0m\r\n")
    assert manager.wait_for_prompt_in_log(2, rf"\A[\s\S]{{{before}}}NEW", .1, regex=True)
    assert "\x1b" in manager.log_path(2).read_text()  # Raw artifact is preserved.


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_direct_timeout_apis_reject_nonpositive_and_nonfinite(manager, fake_workspace, timeout):
    with pytest.raises(ValueError, match="finite and positive"):
        manager.execute_command_with_prompt_capture(5, "true", timeout)
    with pytest.raises(ValueError, match="finite and positive"):
        manager.wait_for_prompt_in_log(5, "prompt", timeout)
    fake_workspace["boot_timeout"] = timeout
    with pytest.raises(ValueError, match="finite and positive"):
        make_qbox_bundle(fake_workspace).driver.wait_ready()
    assert manager.command_records == []


@pytest.fixture
def fake_workspace(tmp_path):
    """Copy ownership supervisor, but never copy/execute the actual launcher."""
    root = tmp_path / "workspace"
    scripts = root / "scripts/run"
    scripts.mkdir(parents=True)
    source = Path(__file__).resolve().parents[2] / "scripts/run"
    for name in ("qbox_board_session.py", "qbox_tc397.py"):
        shutil.copy2(source / name, scripts / name)
    launcher = root / "run_qbox_yocto.sh"
    launcher.write_text(f"#!{sys.executable}\n" + """
import pathlib, sys, time
out = pathlib.Path(sys.argv[sys.argv.index('--out-dir') + 1])
(out / 'qbox-primary-console.log').write_text('NEXIOS_BSP_INITRAMFS_READY\\nnexios-bsp# ')
time.sleep(60)
""")
    launcher.chmod(0o700)
    build = root / "build"
    deploy = build / "tmp_baremetal/deploy/images/apollo-qvp"
    deploy.mkdir(parents=True)
    provider = root / "fake-provider"
    provider.mkdir()
    executable = provider / "platforms-vp"
    executable.write_text("#!/bin/sh\nexit 99\n")
    executable.chmod(0o700)
    (provider / "platform.lua").write_text("-- host fixture only\n")
    images = {name: name + ".img" for name in
              ("rse_rom", "rse_flash", "rse_otp", "ap_flash", "dtb", "si0_ramfw", "si_cl1", "rootfs_wic")}
    for filename in images.values():
        (deploy / filename).write_bytes(b"host fixture, not a boot image")
    (deploy / "nexios-bsp-initramfs-apollo-qvp.wic").write_bytes(b"host BSP fixture")
    (deploy / "nexios-image-apollo-qvp.qboxconf").write_text(json.dumps({
        "provider": {"bindir": str(provider), "data_dir": str(provider)},
        "exe": "platforms-vp", "config": "platform.lua", "images": images,
    }))
    return {"workspace_root": str(root), "build_dir": str(build),
            "log_dir": str(tmp_path / "logs"), "image": "bsp", "boot_timeout": 2}


def test_missing_prebuilt_input_errors_without_launching(fake_workspace, monkeypatch):
    config = fake_workspace
    (Path(config["build_dir"]) / "tmp_baremetal/deploy/images/apollo-qvp/rse_rom.img").unlink()
    monkeypatch.setattr(controller.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch"))
    with pytest.raises(FileNotFoundError, match="rse_rom"):
        make_qbox_bundle(config).driver.init()
    assert not Path(config["log_dir"]).exists()


def test_bsp_provider_fallback_still_requires_bsp_wic(fake_workspace):
    deploy = Path(fake_workspace["build_dir"]) / "tmp_baremetal/deploy/images/apollo-qvp"
    (deploy / "nexios-bsp-initramfs-apollo-qvp.wic").unlink()
    with pytest.raises(FileNotFoundError, match="bsp rootfs WIC"):
        make_qbox_bundle(fake_workspace).driver.init()


def test_explicit_rootfs_is_validated_and_pinned_in_launch_spec(fake_workspace):
    deploy = Path(fake_workspace["build_dir"]) / "tmp_baremetal/deploy/images/apollo-qvp"
    preserved = Path(fake_workspace["workspace_root"]) / "preserved-bsp.wic"
    (deploy / "nexios-bsp-initramfs-apollo-qvp.wic").rename(preserved)
    fake_workspace["rootfs"] = str(preserved)
    bundle = make_qbox_bundle(fake_workspace)
    try:
        bundle.driver.start()
        bundle.driver.wait_ready()
        spec = json.loads((bundle.driver.run_dir / "launch-spec.json").read_text())
        assert spec["command"][spec["command"].index("--rootfs") + 1] == str(preserved)
        assert "--copy-disks" in spec["command"]
        assert preserved.read_bytes() == b"host BSP fixture"
    finally:
        bundle.driver.stop()
    preserved.unlink()
    with pytest.raises(FileNotFoundError, match="rootfs WIC"):
        make_qbox_bundle(fake_workspace).driver.init()


def test_board_lifecycle_owns_only_its_processes_and_resets_fresh_logs(fake_workspace):
    bundle = get_factory("qbox")(fake_workspace)
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        bundle.driver.init()
        bundle.driver.start()
        bundle.driver.wait_ready()
        first = bundle.driver.run_dir
        first_pid = bundle.driver.process.pid
        spec = json.loads((first / "launch-spec.json").read_text())
        assert "--foreground-runtime" in spec["command"]
        assert "--multi-session" in spec["command"]
        assert "--copy-disks" in spec["command"]
        assert "--no-persistent-rse-state" in spec["command"]
        assert "--no-vmcu" in spec["command"]
        assert "--validation-profile" not in spec["command"]
        assert "--validation-http-port" not in spec["command"]
        assert "nexios-image-apollo-qvp.qboxconf" in spec["command"][spec["command"].index("--qboxconf") + 1]
        assert "nexios-bsp-initramfs-apollo-qvp.wic" in spec["command"][spec["command"].index("--rootfs") + 1]
        assert spec["env"]["QBOX_APOLLO_NETDEV"].startswith("type=user,hostfwd=tcp:127.0.0.1:")
        assert all((first / name).is_fifo() for name in FIFOS.values())
        append(bundle.manager, "ap", "STALE GENERATION\n")
        bundle.driver.reset()
        bundle.driver.wait_ready()
        assert bundle.driver.process.pid != first_pid
        assert bundle.driver.run_dir != first
        assert "STALE GENERATION" not in bundle.manager.read_log("ap")
        assert bundle.manager.log_dir == bundle.driver.run_dir
        assert json.loads((first / "target-cleanup.json").read_text())["residual_pids"] == []
    finally:
        bundle.driver.stop()
        assert unrelated.poll() is None
        unrelated.terminate()
        unrelated.wait(timeout=2)
    assert bundle.driver.cleanup_result["status"] == "PASS"
    assert not bundle.driver.is_running()


def test_validation_http_port_reaches_launcher_without_duplicate_guest_forward(fake_workspace):
    fake_workspace.update(image="product", validation_http_port=18081)
    bundle = make_qbox_bundle(fake_workspace)
    try:
        bundle.driver.start()
        # The host fixture only emits the BSP readiness marker. Wait for that
        # directly; this test checks launcher transport wiring, not guest boot.
        assert bundle.manager.wait_for_prompt_in_log(5, "NEXIOS_BSP_INITRAMFS_READY", 2)
        spec = json.loads((bundle.driver.run_dir / "launch-spec.json").read_text())
        command = spec["command"]
        assert command.count("--validation-http-port") == 1
        assert command[command.index("--validation-http-port") + 1] == "18081"
        assert "--validation-profile" not in command
        # run_qbox_yocto.sh appends the HTTP guestfwd from the CLI option.
        # Supplying it here too would duplicate the forwarding endpoint.
        assert spec["env"]["QBOX_APOLLO_NETDEV"] == (
            f"type=user,hostfwd=tcp:127.0.0.1:{bundle.driver.ssh_port}-:22"
        )
    finally:
        bundle.driver.stop()


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_validation_http_port_fails_before_launch(fake_workspace, monkeypatch, port):
    fake_workspace["validation_http_port"] = port
    monkeypatch.setattr(controller.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch"))
    with pytest.raises(ValueError, match="validation_http_port"):
        make_qbox_bundle(fake_workspace).driver.start()
    assert not Path(fake_workspace["log_dir"]).exists()


def test_partial_start_cleans_owned_supervisor(fake_workspace, monkeypatch):
    bundle = make_qbox_bundle(fake_workspace)
    monkeypatch.setattr(bundle.manager, "connect", lambda: (_ for _ in ()).throw(RuntimeError("connect failed")))
    with pytest.raises(RuntimeError, match="connect failed"):
        bundle.driver.start()
    assert not bundle.driver.is_running()
    assert bundle.driver.cleanup_result["residual_pids"] == []


@pytest.mark.parametrize("failure", ["status", "cleanup", "identity", "missing"])
def test_board_receipt_failure_is_not_hidden_by_outer_cleanup(fake_workspace, monkeypatch, failure):
    bundle = make_qbox_bundle(fake_workspace)
    bundle.driver.start()
    bundle.driver.wait_ready()
    original_stop = bundle.driver.owner.stop

    def finish_with_failed_receipt(timeout):
        result = original_stop(timeout)
        assert result["status"] == "PASS"
        path = bundle.driver.run_dir / "board-session.json"
        board = json.loads(path.read_text())
        if failure == "missing":
            path.unlink()
        else:
            if failure == "status":
                board["status"] = "FAILED"
            elif failure == "cleanup":
                board["cleanup"]["status"] = "FAIL"
            else:
                board["run_id"] = "unrelated-run"
            path.write_text(json.dumps(board))
        return result

    monkeypatch.setattr(bundle.driver.owner, "stop", finish_with_failed_receipt)
    with pytest.raises(RuntimeError, match="owned-process cleanup failed"):
        bundle.driver.stop()
    assert not bundle.driver.is_running()
    assert bundle.driver.cleanup_result["status"] == "FAIL"
    assert bundle.driver.cleanup_result["residual_pids"] == []


def test_disconnect_error_does_not_prevent_owned_process_cleanup(fake_workspace, monkeypatch):
    bundle = make_qbox_bundle(fake_workspace)
    bundle.driver.start()
    bundle.driver.wait_ready()
    monkeypatch.setattr(bundle.manager, "disconnect", lambda: (_ for _ in ()).throw(RuntimeError("disconnect failed")))
    with pytest.raises(RuntimeError, match="disconnect failed"):
        bundle.driver.stop()
    assert not bundle.driver.is_running()
    assert bundle.driver.cleanup_result["status"] == "PASS"


@contextmanager
def ssh_peer(returncode=7, wait=False, key=None, stall_exec=False,
             expected_pre_auth_disconnect=False):
    """A real loopback Paramiko server tests auth, host key, rc, and timeout."""
    import paramiko

    key = key or paramiko.RSAKey.generate(1024)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    listener.settimeout(3)
    stop, command_received = threading.Event(), threading.Event()
    received, errors, transports = [], [], []

    class Server(paramiko.ServerInterface):
        def check_auth_none(self, username):
            received.append(("user", username))
            return paramiko.AUTH_SUCCESSFUL

        def check_channel_request(self, kind, channel_id):
            return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

        def check_channel_exec_request(self, channel, command):
            received.append(("command", command))
            if stall_exec:
                stop.wait(3)
            command_received.set()
            return True

    def serve():
        try:
            conn, _ = listener.accept()
            transport = paramiko.Transport(conn)
            transports.append(transport)
            transport.add_server_key(key)
            transport.start_server(server=Server())
            channel = transport.accept(2)
            if channel and command_received.wait(2):
                channel.sendall(b"SSH LIVE RESPONSE\n")
                channel.sendall_stderr(b"SSH STDERR\n")
                if not wait:
                    channel.send_exit_status(returncode)
                    channel.shutdown_write()
            stop.wait(3)
        except (EOFError, OSError, paramiko.SSHException) as error:
            # Host-key rejection deliberately closes the client before auth.
            # Only that negative case may accept EOF/reset at this phase;
            # protocol/auth errors and disconnects after auth still fail.
            expected_disconnect = (expected_pre_auth_disconnect and not received
                                   and isinstance(error, (EOFError, ConnectionResetError)))
            if not stop.is_set() and not expected_disconnect:
                errors.append(error)
        finally:
            for transport in transports:
                transport.close()

    thread = threading.Thread(target=serve)
    thread.start()
    try:
        yield listener.getsockname()[1], received
    finally:
        stop.set()
        listener.close()
        for transport in transports:
            transport.close()
        thread.join(timeout=4)
        assert not thread.is_alive()
        assert not errors


def test_ssh_executes_authenticated_command_and_preserves_exit_status(manager):
    with ssh_peer() as (port, received):
        manager.ssh_port = port
        rc, output = manager.execute_command_with_prompt_capture(6, "uname -a", timeout=2)
    assert rc == 7
    assert "SSH LIVE RESPONSE" in output and "SSH STDERR" in output
    assert received == [("user", "root"), ("command", b"uname -a")]
    known = manager.log_dir / "ssh-known-hosts"
    assert known.stat().st_mode & 0o777 == 0o600
    assert f"[127.0.0.1]:{port}" in known.read_text()
    assert manager.command_records[-1]["status_semantics"] == "guest_exit_code"


def test_ssh_deadline_closes_connection_and_does_not_claim_command_pass(manager):
    with ssh_peer(wait=True) as (port, _):
        manager.ssh_port = port
        rc, _ = manager.execute_command_with_prompt_capture(6, "sleep 60", timeout=.25)
    assert rc == 124
    assert manager._ssh_transport is None


def test_ssh_deadline_also_bounds_unanswered_exec_request(manager):
    with ssh_peer(stall_exec=True) as (port, _):
        manager.ssh_port = port
        start = time.monotonic()
        rc, _ = manager.execute_command_with_prompt_capture(6, "uname -a", timeout=.25)
        elapsed = time.monotonic() - start
    assert rc == 124
    assert elapsed < 1


def test_ssh_rejects_changed_host_key_before_authentication(manager):
    import paramiko

    with ssh_peer(expected_pre_auth_disconnect=True) as (port, received):
        manager.ssh_port = port
        keys = paramiko.HostKeys()
        keys.add(f"[127.0.0.1]:{port}", "ssh-rsa", paramiko.RSAKey.generate(1024))
        keys.save(str(manager.log_dir / "ssh-known-hosts"))
        rc, output = manager.execute_command_with_prompt_capture(6, "uname -a", timeout=2)
    assert rc == 125 and "host key changed" in output
    assert received == []

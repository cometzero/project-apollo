"""Watchdog tooling tests never open a real watchdog or request a reset."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/watchdog_guest.py"
spec = importlib.util.spec_from_file_location("watchdog_guest", SOURCE)
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)


class Recorder:
    def __init__(self):
        self.events = []

    def emit(self, event, **fields):
        self.events.append((event, fields))


def fake_device(monkeypatch, command="keepalive"):
    calls = []
    elapsed = [0.0]
    monkeypatch.setattr(wd, "preflight", lambda *_: {"state": "inactive"})
    monkeypatch.setattr(wd, "snapshot", lambda: {"state": "inactive"})
    monkeypatch.setattr(wd.os, "open", lambda *_: 77)
    monkeypatch.setattr(wd.os, "close", lambda fd: calls.append(("close", fd)))
    monkeypatch.setattr(wd.os, "write", lambda fd, data: calls.append(("write", data)))
    monkeypatch.setattr(wd.time, "monotonic", lambda: elapsed[0])
    monkeypatch.setattr(wd.time, "sleep", lambda value: elapsed.__setitem__(0, elapsed[0] + value))

    def ioctl(fd, request, value=0):
        calls.append((request, value))
        return 4 if request in (wd.SETTIMEOUT, wd.GETTIMEOUT) else 0

    monkeypatch.setattr(wd, "ioctl_int", ioctl)
    args = SimpleNamespace(device="/dev/watchdog0", timeout=4, duration=5,
                           grace=1, command=command)
    return args, calls


def test_default_is_read_only_inspection():
    assert wd.parser().parse_args([]).command == "inspect"


def test_expiry_requires_explicit_reset_ack(tmp_path):
    with pytest.raises(SystemExit) as result:
        wd.main(["expiry", "--output", str(tmp_path / "uncreated")])
    assert result.value.code == 2
    assert not (tmp_path / "uncreated").exists()


def test_inspection_never_opens_watchdog(monkeypatch, tmp_path):
    monkeypatch.setattr(wd.os, "open", lambda *_: pytest.fail("device opened"))
    monkeypatch.setattr(wd, "snapshot", lambda: {"state": "inactive"})
    monkeypatch.setattr(wd.subprocess, "check_output", lambda *a, **kw:
                        "RuntimeWatchdogUSec=0\nRebootWatchdogUSec=10min\n")
    assert wd.main(["inspect", "--output", str(tmp_path / "evidence")]) == 0
    result = json.loads((tmp_path / "evidence/result.json").read_text())
    assert result["systemd_policy"] == {"RuntimeWatchdogUSec": "0", "RebootWatchdogUSec": "10min"}
    assert result["device_opened"] is False


def test_policy_query_is_bounded_and_read_only(monkeypatch):
    def query(argv, **kwargs):
        assert argv == ["systemctl", "show", "--property=RuntimeWatchdogUSec",
                        "--property=RebootWatchdogUSec"]
        assert kwargs == {"text": True, "timeout": 5}
        return "RebootWatchdogUSec=10min\nRuntimeWatchdogUSec=0\n"
    monkeypatch.setattr(wd.subprocess, "check_output", query)
    assert wd.systemd_policy()["RuntimeWatchdogUSec"] == "0"


def test_missing_policy_is_not_silently_successful(monkeypatch):
    monkeypatch.setattr(wd.subprocess, "check_output", lambda *a, **kw:
                        "RuntimeWatchdogUSec=0\n")
    with pytest.raises(RuntimeError, match="incomplete"):
        wd.systemd_policy()


def test_policy_timeout_is_reported_without_opening_device(monkeypatch, tmp_path):
    monkeypatch.setattr(wd.os, "open", lambda *_: pytest.fail("device opened"))
    monkeypatch.setattr(wd, "snapshot", lambda: {"state": "inactive"})
    def timeout(*args, **kwargs):
        raise wd.subprocess.TimeoutExpired("systemctl show", 5)
    monkeypatch.setattr(wd.subprocess, "check_output", timeout)
    output = tmp_path / "evidence"
    assert wd.main(["inspect", "--output", str(output)]) == 1
    result = json.loads((output / "result.json").read_text())
    assert result["status"] == "FAIL"
    assert "timed out" in result["error"]


def test_keepalive_sets_queries_feeds_and_disables(monkeypatch):
    args, calls = fake_device(monkeypatch)
    record = Recorder()
    assert wd.run_active(args, record)["status"] == "PASS"
    assert calls[:3] == [(wd.SETTIMEOUT, 4), (wd.GETTIMEOUT, 0), (wd.KEEPALIVE, 0)]
    assert calls[-2:] == [(wd.SETOPTIONS, 1), ("close", 77)]
    assert sum(call[0] == wd.KEEPALIVE for call in calls) > 1


def test_expiry_holds_descriptor_and_never_fakes_reset_pass(monkeypatch):
    args, calls = fake_device(monkeypatch, "expiry")
    record = Recorder()
    result = wd.run_active(args, record)
    assert result["status"] == "NOT_OBSERVED"
    assert sum(call[0] == wd.KEEPALIVE for call in calls) == 1
    ready = dict(record.events)["ready"]
    assert ready["ws0_expected_after_s"] == 2
    assert ready["ws1_expected_after_s"] == 4
    assert dict(record.events)["ws0-expected"]["observed"] is False
    assert calls[-2:] == [(wd.SETOPTIONS, 1), ("close", 77)]


def test_stop_must_be_confirmed(monkeypatch):
    args, _ = fake_device(monkeypatch)
    monkeypatch.setattr(wd, "snapshot", lambda: {"state": "active"})
    assert wd.run_active(args, Recorder())["status"] == "FAIL"


def test_missing_sysfs_is_reported_not_opened(tmp_path):
    result = wd.snapshot(tmp_path)
    assert "unavailable" in result["state"]
    assert result["timeleft"]["valid"] is False


def test_inactive_snapshot_never_reads_stale_hardware_deadline(tmp_path, monkeypatch):
    (tmp_path / "state").write_text("inactive\n")
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        if path == tmp_path / "timeleft":
            pytest.fail("inactive hardware countdown must not be read")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    result = wd.snapshot(tmp_path)
    assert result["timeleft"]["valid"] is False
    assert "active" in result["timeleft"]["reason"]


def test_active_snapshot_retains_observed_countdown(tmp_path):
    (tmp_path / "state").write_text("active\n")
    (tmp_path / "timeleft").write_text("19\n")
    assert wd.snapshot(tmp_path)["timeleft"] == "19"


def test_ioctl_uses_mutable_integer_buffer(monkeypatch):
    def ioctl(fd, request, buffer, mutate):
        assert (fd, request, mutate) == (77, wd.GETTIMEOUT, True)
        buffer[0] = 20

    monkeypatch.setattr(wd.fcntl, "ioctl", ioctl)
    assert wd.ioctl_int(77, wd.GETTIMEOUT) == 20


def test_exception_after_open_still_disarms(monkeypatch):
    args, calls = fake_device(monkeypatch)
    original = wd.ioctl_int

    def ioctl(fd, request, value=0):
        if request == wd.GETTIMEOUT:
            raise OSError("injected")
        return original(fd, request, value)

    monkeypatch.setattr(wd, "ioctl_int", ioctl)
    with pytest.raises(OSError, match="injected"):
        wd.run_active(args, Recorder())
    assert calls[-2:] == [(wd.SETOPTIONS, 1), ("close", 77)]


@pytest.mark.parametrize("bad_timeleft", [-1, 5, 2147483647])
@pytest.mark.parametrize("bad_read", [1, 2])
def test_timeleft_out_of_range_fails_and_disarms(monkeypatch, bad_timeleft, bad_read):
    args, calls = fake_device(monkeypatch)
    original = wd.ioctl_int
    reads = [0]

    def ioctl(fd, request, value=0):
        result = original(fd, request, value)
        if request == wd.GETTIMELEFT:
            reads[0] += 1
            if reads[0] == bad_read:
                return bad_timeleft
        return result

    monkeypatch.setattr(wd, "ioctl_int", ioctl)
    record = Recorder()
    with pytest.raises(RuntimeError, match="outside timeout range"):
        wd.run_active(args, record)
    assert calls[-2:] == [(wd.SETOPTIONS, 1), ("close", 77)]
    assert dict(record.events)["after"]["snapshot"]["state"] == "inactive"


def test_preflight_rejects_nowayout_before_open(monkeypatch):
    monkeypatch.setattr(wd.os, "geteuid", lambda: 0)
    monkeypatch.setattr(wd, "snapshot", lambda: {
        "identity": "SBSA Generic Watchdog", "state": "inactive", "nowayout": "1"})
    monkeypatch.setattr(wd.os, "open", lambda *_: pytest.fail("device opened"))
    with pytest.raises(RuntimeError, match="stoppable"):
        wd.preflight("/dev/watchdog0", 20)


def test_output_cannot_overwrite_previous_evidence(tmp_path):
    with pytest.raises(FileExistsError):
        wd.Recorder(tmp_path)


def test_sysfs_config_and_driver_timing_contract():
    kernel = SOURCE.parents[2] / "hsoc-stack/components/primary_compute/linux"
    assert "CONFIG_WATCHDOG_SYSFS=y" in (kernel / "arch/arm64/configs/apollo_qvp_defconfig").read_text()
    driver = (kernel / "drivers/watchdog/sbsa_gwdt.c").read_text()
    assert "((u64)gwdt->clk / 2) * timeout" in driver

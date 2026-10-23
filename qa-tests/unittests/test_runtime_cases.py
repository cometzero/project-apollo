from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace

import pytest

from scripts.run.qbox_validation.reuse_common import NoopCleanup
from scripts.run.qbox_validation.types import (
    AssertionObservation, CleanupReceipt, Console, EvaluationError,
    ProbeStep, ProfileProbeSpec,
)
from test_automation.checks import profiles


class Manager:
    def __init__(self, replies=(), logs=None):
        self.logs = {name: "" for name in ("ap", "secure", "rse", "si_cl0", "si_cl1", "ssh")}
        self.logs.update(logs or {})
        self.replies = iter(replies)
        self.commands = []
        self.waits = []
        self.command_completion_patterns = {}
        self.completions = []

    def get_port(self, name):
        return name

    def read_log(self, port):
        return self.logs[port]

    def execute_command_with_prompt_capture(self, port, command, timeout):
        self.commands.append((port, command, timeout))
        self.completions.append(self.command_completion_patterns.get((port, command)))
        rc, output = next(self.replies)
        self.logs[port] += output
        return rc, output

    def wait_for_prompt_in_log(self, port, prompt, timeout, regex=False, ignore_case=False):
        self.waits.append((port, prompt, timeout))
        if regex:
            return re.search(prompt, self.logs[port], re.I if ignore_case else 0) is not None
        return prompt in self.logs[port]


class Evaluator:
    def evaluate(self, snapshot, outputs):
        return (AssertionObservation("observed", "PASS" if outputs == ("OK\n",) else "FAIL"),)


def spec(console=Console.PRIMARY, command="check", completion=None):
    return ProfileProbeSpec(
        "host-fixture", frozenset({console}),
        (ProbeStep(console, command, r"(?m)^OK$", 7, completion),),
        ("observed",), "identical", Evaluator(), NoopCleanup(), None,
    )


def install_spec(monkeypatch, value):
    monkeypatch.setattr(profiles, "resolve_profile", lambda *_: value)


def test_profile_uses_manager_raw_commands_and_reports_real_assertions(monkeypatch):
    install_spec(monkeypatch, spec())
    manager = Manager([(0, "OK\n")])
    properties = []
    result = profiles.execute_profile(
        SimpleNamespace(mgr=manager), "host-fixture", lambda *item: properties.append(item),
    )
    assert manager.commands == [("ap", "check", 7)]
    assert result["verdict"] == "PASS"
    assert properties[0] == ("validation_profile", "host-fixture")
    assert '"id": "observed"' in properties[1][1]
    assert not any("duration" in key for key, _ in properties)


@pytest.mark.parametrize("rc", [1, 124, 125])
def test_ap_command_failure_cannot_be_hidden_by_success_output(monkeypatch, rc):
    install_spec(monkeypatch, spec())
    manager = Manager([(rc, "OK\n")])
    properties = []
    with pytest.raises(AssertionError, match="command rc="):
        profiles.execute_profile(
            SimpleNamespace(mgr=manager), "host-fixture", lambda *item: properties.append(item),
        )
    assert properties == [("validation_profile", "host-fixture")]


def test_missing_completion_record_fails_before_evaluation(monkeypatch):
    install_spec(monkeypatch, spec(completion="REQUIRED_RECORD"))
    with pytest.raises(AssertionError, match="completion record missing"):
        profiles.execute_profile(SimpleNamespace(mgr=Manager([(0, "OK\n")])), "host-fixture")


def test_si0_does_not_reuse_old_firmware_completion_or_add_control_bytes(monkeypatch):
    install_spec(monkeypatch, spec(Console.SI0, "test smcf"))
    manager = Manager([(0, "new command without completion\n")], {"si_cl0": "OK\n"})
    with pytest.raises(AssertionError, match="fresh firmware completion missing"):
        profiles.execute_profile(SimpleNamespace(mgr=manager), "host-fixture")
    assert manager.commands == [("si_cl0", "test smcf", 7)]
    assert manager.completions == [r"(?m)^OK$"]
    assert manager.command_completion_patterns == {}


def test_si0_accepts_only_current_firmware_completion(monkeypatch):
    install_spec(monkeypatch, spec(Console.SI0, "test smcf"))
    manager = Manager([(0, "OK\n")], {"si_cl0": "previous boot\n"})
    assert profiles.execute_profile(SimpleNamespace(mgr=manager), "host-fixture")["verdict"] == "PASS"


def test_zephyr_expected_error_output_is_evaluated_not_treated_as_transport_failure(monkeypatch):
    class ExpectedError:
        def evaluate(self, snapshot, outputs):
            return (AssertionObservation("observed", "PASS" if outputs == ("invalid cpu\n",) else "FAIL"),)

    install_spec(monkeypatch, replace(spec(Console.SI1), evaluator=ExpectedError()))
    manager = Manager([(1, "invalid cpu\n")])
    assert profiles.execute_profile(SimpleNamespace(mgr=manager), "host-fixture")["verdict"] == "PASS"


@pytest.mark.parametrize("rc", [124, 125])
def test_zephyr_transport_failure_is_not_an_expected_negative(monkeypatch, rc):
    install_spec(monkeypatch, spec(Console.SI1))
    with pytest.raises(AssertionError, match="command rc="):
        profiles.execute_profile(SimpleNamespace(mgr=Manager([(rc, "OK\n")])), "host-fixture")


def test_normalized_failed_assertion_fails_the_pytest_case(monkeypatch):
    install_spec(monkeypatch, spec())
    with pytest.raises(AssertionError, match="failed assertions.*observed"):
        profiles.execute_profile(SimpleNamespace(mgr=Manager([(0, "wrong\n")])), "host-fixture")


@pytest.mark.parametrize("cleanup_ok", [True, False])
def test_unsupported_is_skip_only_after_successful_cleanup(monkeypatch, cleanup_ok):
    class Unsupported:
        def evaluate(self, snapshot, outputs):
            raise EvaluationError("unsupported:psci_powerdown_wakeup_unmodeled")

    class Cleanup:
        def cleanup(self):
            return CleanupReceipt(cleanup_ok, "fixture-cleanup")

    install_spec(monkeypatch, replace(spec(), evaluator=Unsupported(), cleanup=Cleanup()))
    error = pytest.skip.Exception if cleanup_ok else AssertionError
    reason = "unsupported:" if cleanup_ok else "cleanup failed"
    with pytest.raises(error, match=reason):
        profiles.execute_profile(SimpleNamespace(mgr=Manager([(0, "OK\n")])), "host-fixture")


def test_cleanup_runs_after_failed_command(monkeypatch):
    called = []

    class Cleanup:
        def cleanup(self):
            called.append(True)
            return CleanupReceipt(True, "released")

    install_spec(monkeypatch, replace(spec(), cleanup=Cleanup()))
    with pytest.raises(AssertionError, match="command rc=125"):
        profiles.execute_profile(SimpleNamespace(mgr=Manager([(125, "")])), "host-fixture")
    assert called == [True]


def test_current_safety_failure_cannot_reuse_a_prior_success(monkeypatch):
    class Safety:
        def evaluate(self, snapshot, outputs):
            assert "old success" not in snapshot.si0
            return (AssertionObservation("observed", "FAIL"),)

    install_spec(monkeypatch, replace(spec(Console.SI0), evaluator=Safety()))
    manager = Manager([(0, "OK\n")], {"si_cl0": "old success\n"})
    with pytest.raises(AssertionError, match="failed assertions"):
        profiles.execute_profile(SimpleNamespace(mgr=manager), "safety-diagnostics-tests")


def test_complete_zephyr_profile_requires_secondary_cpu_boot_logs():
    logs = {"si_cl1": "Booting Zephyr OS build\n" + "\n".join(
        f"Secondary CPU core {cpu} (MPID:0x10{cpu}00) is up" for cpu in range(1, 4)
    ) + "\n"}
    manager = Manager([(0, "Zephyr version 4.1\n")], logs)
    assert profiles.execute_profile(SimpleNamespace(mgr=manager), "si-cl1")["verdict"] == "PASS"
    manager = Manager([(0, "Zephyr version 4.1\n")], {"si_cl1": "Booting Zephyr OS build\n"})
    with pytest.raises(AssertionError, match="safety-island-cluster1"):
        profiles.execute_profile(SimpleNamespace(mgr=manager), "si-cl1")


def load_case(relative):
    path = Path(__file__).resolve().parents[1] / "tests" / relative
    definition = importlib.util.spec_from_file_location("runtime_case_under_test", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module


@pytest.mark.parametrize("rc,output,passes", [
    (0, "APOLLO_SSH_OK\nLinux\naarch64\n0\n", True),
    (255, "APOLLO_SSH_OK\nLinux\naarch64\n0\n", False),
    (0, "APOLLO_SSH_OK\nLinux\nx86_64\n0\n", False),
])
def test_ssh_runtime_case_uses_the_ssh_transport(rc, output, passes):
    case = load_case("ap/network/test_ssh.py")
    manager = Manager([(rc, output)])
    if passes:
        case.test_primary_ssh_executes_guest_command(SimpleNamespace(mgr=manager))
    else:
        with pytest.raises(AssertionError):
            case.test_primary_ssh_executes_guest_command(SimpleNamespace(mgr=manager))
    assert manager.commands[0][0] == "ssh"


def test_missing_boot_marker_fails_with_domain_context():
    with pytest.raises(AssertionError, match="rse: boot marker missing"):
        profiles.require_log_markers(SimpleNamespace(mgr=Manager()), "rse", ("TF-M",))


def test_smcf_profile_with_real_manager_waits_for_samples_and_preserves_uart_framing(tmp_path, monkeypatch):
    from test_automation.targets.qbox.networking import QBoxNetworkManager

    manager = QBoxNetworkManager({})
    manager.bind(tmp_path, 8022, lambda: True)
    path = manager.log_path("si_cl0")
    path.write_text("[SI0_PLATFORM] SCP started\r\n[SMCF_CLIENT] start data_sampling for MGI[0]\r\n")
    sent = []

    def respond(domain, payload, deadline):
        sent.append((domain, payload))
        transcript = (
            "[CLI_DEBUGGER_MODULE] Entering CLI\r\n"
            "[INTEGRATION_TEST] Start: smcf\r\n"
            "4 Tests 0 Failures 0 Ignored\r\nOK\r\n"
            "[INTEGRATION_TEST] End: smcf\r\n"
            "[CLI_DEBUGGER_MODULE] Exiting CLI\r\n"
        )
        if len(sent) == 1:
            transcript += "[SMCF_CLIENT] start data_sampling for MGI[0]\r\n"
        if len(sent) in (1, 3):
            transcript += (
                "[SMCF_CLIENT] Values for MGI SYSTEM MLI 0 (Sensor)\r\n"
                "[SMCF_CLIENT] Value[0] data = 0x01\r\n"
            )
        with path.open("a") as stream:
            stream.write(transcript)

    monkeypatch.setattr(manager, "_write", respond)
    result = profiles.execute_profile(SimpleNamespace(mgr=manager), "smcf")
    assert result["verdict"] == "PASS"
    assert sent == [("si_cl0", b"\x05test smcf\n\x04")] * 4
    assert manager.command_completion_patterns == {}


def test_si0_completion_override_is_restored_even_on_transport_failure(monkeypatch):
    install_spec(monkeypatch, spec(Console.SI0, "test smcf"))
    manager = Manager([(125, "")])
    manager.command_completion_patterns[("si_cl0", "test smcf")] = "previous rule"
    with pytest.raises(AssertionError, match="command rc=125"):
        profiles.execute_profile(SimpleNamespace(mgr=manager), "host-fixture")
    assert manager.completions == [r"(?m)^OK$"]
    assert manager.command_completion_patterns == {("si_cl0", "test smcf"): "previous rule"}


@pytest.mark.parametrize("dt_cpus", [4, 16])
def test_topology_command_reports_actual_values_without_hiding_failure(tmp_path, dt_cpus):
    from test_automation.checks.bsp import TOPOLOGY_COMMAND

    dt = tmp_path / "cpus"
    dt.mkdir()
    for cpu in range(dt_cpus):
        (dt / f"cpu@{cpu:x}").mkdir()
    sysfs = tmp_path / "sysfs"
    sysfs.mkdir()
    for name in ("possible", "present", "online"):
        (sysfs / name).write_text("0-3\n")
    for cpu in range(4):
        cache = sysfs / f"cpu{cpu}" / "cache" / "index3"
        cache.mkdir(parents=True)
        (cache / "size").write_text("4096K\n")
        (cache / "shared_cpu_list").write_text("0-3\n")
    command = (TOPOLOGY_COMMAND.replace("nproc --all", "printf '4\\n'")
               .replace("/sys/firmware/devicetree/base/cpus", str(dt))
               .replace("/sys/devices/system/cpu", str(sysfs)))
    result = subprocess.run(["sh", "-c", command], text=True, capture_output=True)
    assert result.returncode == (0 if dt_cpus == 4 else 1)
    assert f"field=dt_cpu_nodes actual={dt_cpus} expected=4" in result.stdout
    assert "field=cpu3_cache_shared actual=0-3 expected=0-3" in result.stdout
    assert ("__QBOX_BSP_CORE_TOPOLOGY_OK__" in result.stdout) == (dt_cpus == 4)


def test_dsu_command_keeps_perf_failure_output(tmp_path):
    from test_automation.checks.bsp import DSU_COMMAND

    perf = tmp_path / "perf"
    perf.write_text("#!/bin/sh\nprintf 'fixture PMU unavailable\\n' >&2\nexit 17\n")
    perf.chmod(0o700)
    result = subprocess.run(
        ["sh", "-c", DSU_COMMAND.replace("perf stat", f"{perf} stat")],
        text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "DSU event=0x002A rc=17" in result.stdout
    assert "fixture PMU unavailable" in result.stdout
    assert "__QBOX_BSP_CORE_DSU_OK__" not in result.stdout

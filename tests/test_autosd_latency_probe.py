"""Native unprivileged checks of the bounded guest latency probe."""
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "autosd/customization/apps/latency-probe.c"


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    compiler = shutil.which("cc")
    if not compiler:
        pytest.skip("native C compiler unavailable")
    binary = tmp_path_factory.mktemp("latency-probe") / "probe"
    subprocess.run([compiler, "-O2", "-Wall", "-Wextra", "-Werror", str(SOURCE),
                    "-o", str(binary)], check=True)
    return binary


def command(probe, output, *extra):
    return [str(probe), "--cpu", str(min(os.sched_getaffinity(0))),
            "--duration", "1", "--output", str(output), *extra]


@pytest.mark.parametrize("options", [
    ["--duration", "0"], ["--duration", "601"], ["--period-us", "99"],
    ["--priority", "81"], ["--cpu", "-1"], ["--duration", "1x"],
    ["--period-us", "184467440737095516160"], ["--threshold-us", "-1"],
    ["--load", "--priority", "1"], ["--load", "--inject-us", "1"],
    ["--mlock", "--unknown", "x"],
])
def test_rejects_invalid_options(probe, tmp_path, options):
    output = tmp_path / "result.json"
    result = subprocess.run(command(probe, output, *options), capture_output=True, timeout=3)
    assert result.returncode == 2
    assert not output.exists()


def test_other_measurement_and_exclusive_evidence(probe, tmp_path):
    output = tmp_path / "result.json"
    subprocess.run(command(probe, output), check=True, timeout=5)
    evidence = output.read_bytes()
    data = json.loads(evidence)
    assert data["completed"] and data["count"] > 0
    assert data["policy"] == "SCHED_OTHER" and data["priority"] == 0
    assert data["affinity"] == [min(os.sched_getaffinity(0))]
    assert data["count"] + data["missed_periods"] == 1000
    assert not data["mlock_success"] and not data["synthetic"]
    assert data["latency_us"]["min"] <= data["latency_us"]["p50"] <= data["latency_us"]["max"]
    assert data["max_latency_monotonic_ns"] > 0
    result = subprocess.run(command(probe, output), capture_output=True, timeout=3)
    assert result.returncode != 0 and b"exclusive output" in result.stderr
    assert output.read_bytes() == evidence


def test_synthetic_delay_is_detected_without_timing_pass_claim(probe, tmp_path):
    output = tmp_path / "synthetic.json"
    subprocess.run(command(probe, output, "--inject-us", "30000", "--threshold-us", "20000"),
                   check=True, timeout=5)
    data = json.loads(output.read_text())
    assert data["synthetic"] and data["completed"]
    assert data["threshold_exceedances"] >= 1 and data["missed_periods"] >= 29
    assert data["latency_us"]["max"] >= 30000
    assert data["first_threshold_monotonic_ns"] > 0


def test_load_is_bounded_and_normal_scheduler(probe, tmp_path):
    output = tmp_path / "load.json"
    subprocess.run(command(probe, output, "--load"), check=True, timeout=5)
    data = json.loads(output.read_text())
    assert data["completed"] and data["mode"] == "load"
    assert data["policy"] == "SCHED_OTHER" and data["count"] == 0


def test_interrupt_does_not_report_completed(probe, tmp_path):
    output = tmp_path / "interrupted.json"
    process = subprocess.Popen(command(probe, output, "--duration", "10", "--load"))
    try:
        time.sleep(.15)
        process.send_signal(signal.SIGTERM)
        assert process.wait(timeout=3) == 143
        assert not json.loads(output.read_text())["completed"]
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def restricted_setup(lock=False):
    """Drop root privilege if present and force a zero resource limit."""
    if os.geteuid() == 0:
        os.setgroups([])
        os.setgid(65534)
        os.setuid(65534)
    resource.setrlimit(resource.RLIMIT_MEMLOCK if lock else resource.RLIMIT_RTPRIO, (0, 0))


@pytest.mark.parametrize("option,error", [
    ("--mlock", b"mlockall requested"),
    ("--priority", b"sched_setscheduler requested policy"),
])
def test_privileged_features_never_silently_downgrade(probe, option, error):
    # /proc/self/fd keeps the executable reachable after a root privilege drop,
    # even when pytest's temporary directory has mode 0700. Load permits stdout.
    with probe.open("rb") as binary:
        args = [f"/proc/self/fd/{binary.fileno()}", "--cpu", str(min(os.sched_getaffinity(0))),
                "--duration", "1"]
        if option == "--mlock":
            args += ["--load", "--mlock"]
        else:
            # /dev/stdout exists, so cannot be used with exclusive output.
            # Reserve a unique pathname in the world-writable temporary area.
            import tempfile
            with tempfile.TemporaryDirectory(prefix="apollo-probe-permissions-") as work:
                os.chmod(work, 0o777)
                result = subprocess.run(args + ["--output", work + "/result.json", "--priority", "1"],
                    pass_fds=(binary.fileno(),), capture_output=True, timeout=3,
                    preexec_fn=restricted_setup)
                assert result.returncode != 0 and error in result.stderr
                return
        result = subprocess.run(args, pass_fds=(binary.fileno(),), capture_output=True, timeout=3,
                                preexec_fn=lambda: restricted_setup(lock=True))
        assert result.returncode != 0 and error in result.stderr

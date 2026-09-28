"""Trace wrapper checks without host tracefs writes or privileged tracing."""
import importlib.util
import json
from pathlib import Path
import signal
import shutil
import sys

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "autosd/customization/rt/trace-guest.py"


@pytest.fixture
def trace(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("rt_trace", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path / "tracefs"
    (root / "instances").mkdir(parents=True)
    (root / "events").mkdir()
    for name, value in {"current_tracer": "nop", "tracing_on": "1", "tracing_thresh": "0",
                        "events/enable": "0", "available_tracers": "nop osnoise timerlat"}.items():
        (root / name).write_text(value)
    monkeypatch.setattr(module, "TRACE", root)
    monkeypatch.setattr(module, "LOCK", tmp_path / "trace.lock")
    monkeypatch.setattr(module.os, "geteuid", lambda: 0)
    monkeypatch.setattr(module.os, "sched_getaffinity", lambda _: {0, 1})
    monkeypatch.setattr(module.platform, "machine", lambda: "aarch64")
    monkeypatch.setattr(module.shutil, "which", lambda _: "/usr/bin/rtla")
    original = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda self, *a, **k:
                        "NAME=Automotive" if str(self) == "/etc/os-release" else original(self, *a, **k))
    # Emulate only our tracefs instance's virtual files, never touch host tracefs.
    mkdir, rmdir = Path.mkdir, Path.rmdir
    def trace_mkdir(path, *args, **kwargs):
        result = mkdir(path, *args, **kwargs)
        if path.parent == root / "instances" and path.name.startswith("apollo-osnoise-"):
            (path / "events/osnoise/sample_threshold").mkdir(parents=True)
            (path / "per_cpu/cpu1").mkdir(parents=True)
            for name, value in {"tracing_on": "0", "buffer_size_kb": "0", "tracing_cpumask": "",
                                "events/osnoise/sample_threshold/enable": "0", "trace": "",
                                "per_cpu/cpu1/stats": "overrun: 0\ncommit overrun: 0\ndropped events: 0\n"}.items():
                (path / name).write_text(value)
        return result
    def trace_rmdir(path, *args, **kwargs):
        if path.parent == root / "instances" and path.name.startswith("apollo-osnoise-"):
            shutil.rmtree(path)
        else:
            rmdir(path, *args, **kwargs)
    monkeypatch.setattr(Path, "mkdir", trace_mkdir)
    monkeypatch.setattr(Path, "rmdir", trace_rmdir)
    return module


def raw(mode="timerlat", count=5, duration=1):
    name = "IRQ-001" if mode == "timerlat" else "CPU-001"
    return (f"# RTLA {mode} histogram\n# Time unit is microseconds (us)\n"
            f"# Duration: 0 00:00:{duration:02d}\nIndex {name}\n0 {count}\n"
            f"over: 0\ncount: {count}\nmin: 0\navg: 0\nmax: 1\n")


@pytest.mark.parametrize("target,expected", [(None, 35), ("tcg", 35), ("hardware", 35), ("qbox", 125)])
def test_collection_timeout_preserves_sampling_interval(trace, target, expected):
    assert trace.collection_timeout(5, target) == expected


@pytest.mark.parametrize("mode,count,duration,valid", [
    ("timerlat", 0, 1, False), ("timerlat", 5, 0, True),
    ("osnoise", 0, 1, True), ("osnoise", 0, 0, False),
])
def test_histogram_validity(trace, mode, count, duration, valid):
    assert trace.histogram(raw(mode, count, duration), mode, 1)["valid"] is valid
    assert not trace.histogram("count: 100\n", mode, 1)["valid"]


def test_all_summary_does_not_double_count(trace):
    text = ("# RTLA timerlat histogram\n# Time unit is microseconds (us)\n"
            "# Duration: 0 00:00:01\nIndex IRQ-001 Thr-001 Usr-001\n"
            "0 1 1 0\nover: 0 0 0\ncount: 1 1 0\nmin: 0 0 -\navg: 0 0 -\nmax: 1 1 -\n")
    text += "ALL: IRQ Thr Usr\ncount: 1 1 0\nmin: 0 0 -\navg: 0 0 -\nmax: 1 1 -\n"
    data = trace.histogram(text, "timerlat", 2)
    assert data["sample_count"] == 2 and data["sample_counts"] == [1, 1, 0]
    assert [entry["name"] for entry in data["series"]] == ["IRQ-001", "Thr-001", "Usr-001"]
    assert data["series"][2]["min"] is None


def test_osnoise_overflow_and_decimal_average(trace):
    text = raw("osnoise", 2).replace("over: 0", "over: 1").replace("count: 2", "count: 3")
    text = text.replace("avg: 0", "avg: 7.01").replace("max: 1", "max: 1846")
    data = trace.histogram(text, "osnoise", 1)
    assert data["valid"]
    assert data["series"] == [{"name": "CPU-001", "count": 3, "over": 1,
                               "min": 0, "avg": 7.01, "max": 1846,
                               "buckets": [{"value": 0, "count": 2}]}]


@pytest.mark.parametrize("old,new", [("over: 0", "over: nope"), ("count: 5", "count: 6"),
                                    ("avg: 0", "avg: nan"), ("0 5", "0 5 0"),
                                    ("Index IRQ-001", "Index UNKNOWN"),
                                    ("microseconds (us)", "nanoseconds (ns)"),
                                    ("max: 1", "max:"), ("min: 0", "min: -")])
def test_malformed_histograms_have_no_partial_statistics(trace, old, new):
    data = trace.histogram(raw().replace(old, new), "timerlat", 1)
    assert not data["valid"] and data["series"] == []


def test_zero_noise_is_not_zero_latency(trace):
    data = trace.histogram(raw("osnoise", 0), "osnoise", 1)
    assert data["valid"] and data["observation"] == "NO_NOISE_OBSERVED"
    assert all(data["series"][0][key] is None for key in ("min", "avg", "max"))


def test_multiple_cpu_columns_and_summary_are_separate(trace):
    text = ("# RTLA osnoise histogram\n# Time unit is microseconds (us)\n"
            "# Duration: 0 00:00:10\nIndex CPU-001 CPU-002\n"
            "4 2 1\n8 0 1\nover: 1 0\ncount: 3 2\n"
            "min: 4 4\navg: 90 6\nmax: 262 8\n"
            "ALL: CPU\ncount: 5\nmin: 4\navg: 56.4\nmax: 262\n")
    data = trace.histogram(text, "osnoise", 10)
    assert data["valid"] and data["sample_count"] == 5
    assert [item["name"] for item in data["series"]] == ["CPU-001", "CPU-002"]
    assert data["series"][1]["buckets"] == [{"value": 4, "count": 1}, {"value": 8, "count": 1}]


def invoke(trace, monkeypatch, tmp_path, mode="timerlat"):
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", [str(SOURCE), "--allow-private-guest", "--out", str(out),
                                    "--duration", "1", "--mode", mode])
    code = trace.main()
    return code, json.loads((out / "result.json").read_text())


def test_osnoise_threshold_and_zero_observation(trace, monkeypatch, tmp_path):
    def run(argv, log, timeout, interrupted):
        assert argv[argv.index("-s") + 1] == "1000"
        assert any(arg.startswith("--trace=") for arg in argv)
        log.write(raw("osnoise", 0))
        (tmp_path / "out/threshold-trace.txt").touch()
        return {"returncode": 0, "elapsed_seconds": 1, "termination_reason": None}
    monkeypatch.setattr(trace, "owned_run", run)
    code, report = invoke(trace, monkeypatch, tmp_path, "osnoise")
    assert code == 0 and report["histogram"]["observation"] == "NO_NOISE_OBSERVED"
    assert not report["trace_collected"]
    assert report["settings"] == {"threshold_us": 1000, "cpu": 1, "duration": 1, "priority": 50}
    assert report["platform"] is None


@pytest.mark.parametrize("marker,trace_content,rc,expected", [
    (True, "saved threshold trace", 2, "PASS"),
    (False, "saved threshold trace", 2, "FAIL"),
    (True, "", 2, "FAIL"),
    (True, "saved threshold trace", 1, "FAIL"),
])
def test_threshold_stop_requires_combined_evidence(trace, monkeypatch, tmp_path,
                                                  marker, trace_content, rc, expected):
    def run(argv, log, timeout, interrupted):
        log.write(raw() + ("timerlat hit stop tracing\n" if marker else ""))
        (tmp_path / "out/threshold-trace.txt").write_text(trace_content)
        return {"returncode": rc, "elapsed_seconds": 1, "termination_reason": None}
    monkeypatch.setattr(trace, "owned_run", run)
    code, report = invoke(trace, monkeypatch, tmp_path)
    assert report["status"] == expected
    assert code == (0 if expected == "PASS" else 1)
    assert report["latency_status"] == ("EXCEEDED" if expected == "PASS" else "NOT_EVALUATED")


@pytest.mark.parametrize("change", ["tracing_thresh", "empty", "timeout", "cancel"])
def test_no_false_pass_and_preserves_result(trace, monkeypatch, tmp_path, change):
    def run(argv, log, timeout, interrupted):
        log.write("" if change == "empty" else raw())
        if change == "tracing_thresh":
            (trace.TRACE / "tracing_thresh").write_text("100")
        if change == "cancel":
            interrupted[0] = signal.SIGTERM
        return {"returncode": 0, "elapsed_seconds": 1,
                "termination_reason": "timeout" if change == "timeout" else None}
    monkeypatch.setattr(trace, "owned_run", run)
    code, report = invoke(trace, monkeypatch, tmp_path)
    assert code == 1 and report["status"] != "PASS"
    if change == "tracing_thresh":
        assert not report["settings_restored"]
        assert (trace.TRACE / "tracing_thresh").read_text() == "100"  # No blind reset.


@pytest.mark.parametrize("foreign", ["instance", "events", "tracer", "trigger"])
def test_foreign_session_untouched(trace, monkeypatch, tmp_path, foreign):
    if foreign == "instance":
        (trace.TRACE / "instances/foreign").mkdir()
    elif foreign == "events":
        (trace.TRACE / "events/enable").write_text("X")
    elif foreign == "tracer":
        (trace.TRACE / "current_tracer").write_text("function")
    else:
        path = trace.TRACE / "events/osnoise/sample/trigger"
        path.parent.mkdir(parents=True)
        path.write_text("hist:keys=duration\n")
    monkeypatch.setattr(trace, "owned_run", lambda *a: pytest.fail("must not execute"))
    code, report = invoke(trace, monkeypatch, tmp_path)
    assert code == 77 and report["status"] == "UNSUPPORTED"


def test_host_guard(trace, monkeypatch, tmp_path):
    monkeypatch.setattr(trace.platform, "machine", lambda: "x86_64")
    code, report = invoke(trace, monkeypatch, tmp_path)
    assert code == 77 and "private AArch64" in report["reason"]


def test_owned_timeout_gracefully_signals_only_child_group(trace, tmp_path):
    # Real subprocess, harmless Python sleeper, no tracefs or host controls.
    with (tmp_path / "log").open("w") as log:
        result = trace.owned_run([sys.executable, "-c", "import time; time.sleep(30)"], log, .1, [0])
    assert result["termination_reason"] == "timeout"
    assert result["elapsed_seconds"] < 5 and result["returncode"] != 0


def sample(start="100.000000001", duration=1500, cpu=1):
    return f" osnoise/1-123 [00{cpu}] d..2. 100.001000: sample_threshold: start {start} duration {duration} ns interference 1\n"


def test_time_series_units_event_start_order_and_cpu(trace):
    data = trace.osnoise_time_series(sample("100.500000001", 2345, 2) + sample())
    assert data["valid"] and data["status"] == "SAMPLES_OBSERVED"
    assert data["unit"] == "us" and data["x_unit"] == "s"
    assert data["samples"] == [{"time_s": 0, "latency_us": 1.5, "cpu": 1},
                               {"time_s": .5, "latency_us": 2.345, "cpu": 2}]


@pytest.mark.parametrize("old,new", [(" ns ", " us "), ("1500", "-1"),
                                     ("100.000000001", "100.1"), ("interference 1", "interference invalid")])
def test_time_series_malformed_never_exposes_partial_plot(trace, old, new):
    data = trace.osnoise_time_series(sample() + sample().replace(old, new))
    assert not data["valid"] and data["samples"] == [] and data["malformed_events"] == 1


def test_time_series_bounded_and_loss_labelled(trace, monkeypatch):
    monkeypatch.setattr(trace, "MAX_TIME_SAMPLES", 2)
    data = trace.osnoise_time_series(sample() + sample("101.000000001") + sample("102.000000001"),
                                    dropped_events=4)
    assert data["valid"] and data["status"] == "PARTIAL"
    assert data["truncated"] and data["sample_count"] == 2
    assert data["captured_sample_count"] == 3 and data["dropped_events"] == 4


def test_time_series_downsampling_retains_late_peak_and_entire_origin(trace, monkeypatch):
    monkeypatch.setattr(trace, "MAX_TIME_SAMPLES", 4)
    dense = "".join(sample(f"100.{index:09d}", index + 1000) for index in range(100))
    data = trace.osnoise_time_series(dense + sample("110.000000000", 99000))
    assert data["downsampled"] and data["aggregation"] == "per_cpu_time_bucket_max"
    assert not data["truncated"] and data["dropped_events"] == 0
    assert data["captured_sample_count"] == 101 and data["sample_count"] <= 4
    assert data["origin_timestamp_s"] == 100 and data["end_time_s"] == 10
    assert data["samples"][-1] == {"time_s": 10, "latency_us": 99, "cpu": 1,
                                   "min_latency_us": 99, "event_count": 1}
    assert data["samples"][0]["latency_us"] == 1.099  # Dense first bin peak retained.
    assert data["samples"][0]["min_latency_us"] == 1
    assert data["samples"][0]["event_count"] == 100
    assert sum(entry["event_count"] for entry in data["samples"]) == data["captured_sample_count"]


def test_time_series_peak_buckets_are_per_cpu_and_total_bound(trace, monkeypatch):
    monkeypatch.setattr(trace, "MAX_TIME_SAMPLES", 6)
    text = "".join(sample(f"{100 + index}.000000000", 1000 + cpu * 100 + index, cpu)
                   for cpu in (1, 2) for index in range(10))
    data = trace.osnoise_time_series(text)
    assert data["sample_count"] <= 6 and data["aggregation_bins_per_cpu"] == 3
    assert {entry["cpu"] for entry in data["samples"]} == {1, 2}
    assert sum(entry["event_count"] for entry in data["samples"]) == 20
    assert min(entry["min_latency_us"] for entry in data["samples"]) == 1.1
    assert all(any(entry["cpu"] == cpu and entry["latency_us"] == (1000 + cpu * 100 + 9) / 1000
                   for entry in data["samples"]) for cpu in (1, 2))


def test_time_series_empty_does_not_invent_zero_samples(trace):
    data = trace.osnoise_time_series("# empty trace\n")
    assert data["valid"] and data["status"] == "NO_NOISE_OBSERVED" and data["samples"] == []


def test_owned_capture_bound_controls_counters_and_cleanup(trace, tmp_path, monkeypatch):
    capture = trace.OsnoiseCapture(33)
    capture.start()
    assert (capture.path / "tracing_cpumask").read_text() == "2,00000000"
    assert (capture.path / "buffer_size_kb").read_text() == "4096"
    (capture.path / "per_cpu/cpu33").mkdir()
    (capture.path / "per_cpu/cpu33/stats").write_text("overrun: 0\ncommit overrun: 0\ndropped events: 0\n")
    (capture.path / "trace").write_text(sample() * 3)
    (capture.path / "per_cpu/cpu1/stats").write_text("overrun: 3\ncommit overrun: 1\ndropped events: 2\n")
    monkeypatch.setattr(trace, "MAX_TRACE_BYTES", len(sample().encode()) + 5)
    result = capture.finish(tmp_path)
    assert result["read_truncated"] and result["dropped_events"] == 6
    assert result["status"] == "PARTIAL" and result["sample_count"] == 1
    capture.close()
    assert not capture.path.exists()


@pytest.mark.parametrize("failure", [False, True])
def test_osnoise_capture_cleanup_success_and_failure(trace, monkeypatch, tmp_path, failure):
    def run(argv, log, timeout, interrupted):
        instance, = list((trace.TRACE / "instances").iterdir())
        (instance / "trace").write_text(sample())
        if failure:
            raise OSError("RTLA launch failed")
        log.write(raw("osnoise", 1))
        return {"returncode": 0, "elapsed_seconds": 1, "termination_reason": None}
    monkeypatch.setattr(trace, "owned_run", run)
    code, report = invoke(trace, monkeypatch, tmp_path, "osnoise")
    assert code == (1 if failure else 0)
    assert report["settings_restored"] and report["remaining_instances"] == []
    assert report["time_series"]["samples"][0]["latency_us"] == 1.5


def test_timerlat_histogram_range_metadata(trace, monkeypatch, tmp_path):
    def run(argv, log, timeout, interrupted):
        assert argv[argv.index("-b") + 1] == "10"
        assert argv[argv.index("-E") + 1] == "100"
        log.write(raw())
        return {"returncode": 0, "elapsed_seconds": 1, "termination_reason": None}
    monkeypatch.setattr(trace, "owned_run", run)
    code, report = invoke(trace, monkeypatch, tmp_path)
    assert code == 0 and report["histogram"]["bucket_size_us"] == 10
    assert report["histogram"]["entries"] == 100 and "time_series" not in report


def test_missing_loss_counters_not_silently_reported_zero(trace, tmp_path):
    capture = trace.OsnoiseCapture(1)
    capture.start()
    (capture.path / "per_cpu/cpu1/stats").write_text("entries: 1\n")
    try:
        with pytest.raises(ValueError, match="Missing trace loss counter"):
            capture.finish(tmp_path)
    finally:
        capture.close()
    assert not capture.path.exists()


def test_capture_setup_failure_removes_only_owned_instance(trace, monkeypatch, tmp_path):
    original = Path.write_text
    def fail_event(path, value, *args, **kwargs):
        if path.name == "enable" and value == "1":
            raise OSError("event unavailable")
        return original(path, value, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", fail_event)
    monkeypatch.setattr(trace, "owned_run", lambda *args: pytest.fail("must not execute"))
    code, report = invoke(trace, monkeypatch, tmp_path, "osnoise")
    assert code == 1 and report["settings_restored"]
    assert report["remaining_instances"] == [] and "event unavailable" in report["reason"]

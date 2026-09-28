#!/usr/bin/env python3
"""Bounded RTLA capture on an idle private guest; no timing qualification."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import time
import uuid

TRACE = Path("/sys/kernel/tracing")
LOCK = Path("/run/apollo-rt-trace.lock")
MAX_TIME_SAMPLES = 5000
MAX_TRACE_BYTES = 16 * 1024 * 1024
TRACE_BUFFER_KB = 4096


def osnoise_time_series(text, dropped_events=0, read_truncated=False):
    """Parse actual sample start/duration, not histogram bucket ordering.

    include/trace/events/osnoise.h defines both start and duration in ns.
    The event's printed start is seconds with nine fractional digits.
    """
    samples = []
    malformed = 0
    observed = 0
    event = re.compile(r"\[(\d+)\].*?sample_threshold:\s+start (\d+)\.(\d{9}) "
                       r"duration (\d+) ns interference (\d+)\s*$")
    for line in text.splitlines():
        if "sample_threshold:" not in line:
            continue
        match = event.search(line)
        if not match:
            malformed += 1
            continue
        cpu, seconds, nanos, duration, _ = map(int, match.groups())
        observed += 1
        samples.append({"timestamp_ns": seconds * 1000000000 + nanos,
                        "latency_us": duration / 1000, "cpu": cpu})
    # Trace records across CPUs can be interleaved; sort by event start, not
    # the trace header timestamp (which describes emission after the noise).
    samples.sort(key=lambda sample: sample["timestamp_ns"])
    origin = samples[0]["timestamp_ns"] if samples else None
    end = samples[-1]["timestamp_ns"] if samples else None
    downsampled = len(samples) > MAX_TIME_SAMPLES
    bins = None
    if downsampled:
        cpus = {sample["cpu"] for sample in samples}
        bins = MAX_TIME_SAMPLES // len(cpus)
        if not bins:
            # Cannot retain even one observation for every CPU truthfully.
            malformed += 1
            samples = []
        else:
            span = end - origin + 1
            peaks = {}
            for sample in samples:
                bucket = (sample["timestamp_ns"] - origin) * bins // span
                key = (sample["cpu"], bucket)
                previous = peaks.get(key)
                minimum = min(sample["latency_us"], previous["min_latency_us"]) if previous else sample["latency_us"]
                count = previous["event_count"] + 1 if previous else 1
                peak = sample if previous is None or sample["latency_us"] > previous["latency_us"] else previous
                peak.update({"min_latency_us": minimum, "event_count": count})
                peaks[key] = peak
            samples = sorted(peaks.values(), key=lambda sample: sample["timestamp_ns"])
    for sample in samples:
        sample["time_s"] = (sample.pop("timestamp_ns") - origin) / 1000000000
    truncated = read_truncated or dropped_events > 0
    valid = not malformed
    return {"valid": valid, "status": "INVALID" if not valid else "PARTIAL" if
            truncated or dropped_events else "SAMPLES_OBSERVED" if samples else "NO_NOISE_OBSERVED",
            "unit": "us", "x_unit": "s", "time_origin": "first_captured_sample",
            "origin_timestamp_s": origin / 1000000000 if origin is not None else None,
            "end_time_s": (end - origin) / 1000000000 if origin is not None else None,
            "samples": samples if valid else [], "sample_count": len(samples) if valid else 0,
            "captured_sample_count": observed, "malformed_events": malformed,
            "truncated": truncated, "dropped_events": dropped_events,
            "downsampled": downsampled,
            "aggregation": "per_cpu_time_bucket_max" if downsampled else "none",
            "aggregation_bins_per_cpu": bins,
            "max_samples": MAX_TIME_SAMPLES,
            "source_event": "osnoise:sample_threshold",
            "observation_note": "Noise events at the kernel sampling threshold; not periodic zero-latency samples"}


class OsnoiseCapture:
    """Bounded event-only private instance; never reset another owner's tracer."""

    def __init__(self, cpu):
        self.path = TRACE / "instances" / ("apollo-osnoise-" + uuid.uuid4().hex)
        self.cpu = cpu
        self.created = False

    def start(self):
        self.path.mkdir()
        self.created = True
        (self.path / "tracing_on").write_text("0")
        (self.path / "buffer_size_kb").write_text(str(TRACE_BUFFER_KB))
        # cpumask uses comma-separated 32-bit hexadecimal words.
        mask = f"{1 << self.cpu:x}"
        words = []
        while mask:
            words.insert(0, mask[-8:])
            mask = mask[:-8]
        (self.path / "tracing_cpumask").write_text(",".join(words))
        (self.path / "events/osnoise/sample_threshold/enable").write_text("1")
        (self.path / "tracing_on").write_text("1")

    def finish(self, out):
        (self.path / "tracing_on").write_text("0")
        counters = {}
        for stats in (self.path / "per_cpu").glob("cpu*/stats"):
            values = {}
            raw_stats = stats.read_text()
            for key in ("overrun", "commit overrun", "dropped events"):
                match = re.search(r"^" + key + r":\s*(\d+)\s*$", raw_stats, re.M)
                if not match:
                    raise ValueError(f"Missing trace loss counter {key}: {stats}")
                values[key] = int(match.group(1))
            counters[stats.parent.name] = values
        if f"cpu{self.cpu}" not in counters:
            raise ValueError("Selected CPU trace loss counters are unavailable")
        dropped = sum(sum(values.values()) for values in counters.values())
        with (self.path / "trace").open("rb") as stream:
            data = stream.read(MAX_TRACE_BYTES + 1)
        truncated = len(data) > MAX_TRACE_BYTES
        data = data[:MAX_TRACE_BYTES]
        if truncated:
            data = data.rsplit(b"\n", 1)[0] + b"\n"
        (out / "osnoise-samples.txt").write_bytes(data)
        result = osnoise_time_series(data.decode("utf-8", errors="replace"), dropped, truncated)
        result.update({"ring_buffer_kb_per_cpu": TRACE_BUFFER_KB, "ring_buffer_stats": counters,
                       "raw_trace": "osnoise-samples.txt", "read_truncated": truncated})
        return result

    def close(self):
        if self.created:
            try:
                (self.path / "tracing_on").write_text("0")
                (self.path / "events/osnoise/sample_threshold/enable").write_text("0")
            finally:
                # tracefs rmdir releases its virtual controls. Never recurse or
                # remove RTLA/foreign instances, even if restoration failed.
                self.path.rmdir()
                self.created = False


def settings():
    names = ["current_tracer", "tracing_on", "tracing_thresh", "events/enable"]
    names += ["osnoise/" + name for name in ("cpus", "period_us", "runtime_us", "timerlat_period_us",
              "stop_tracing_us", "stop_tracing_total_us", "print_stack", "options")]
    return {n: (TRACE / n).read_text().strip() for n in names if (TRACE / n).exists()}


def idle_tracefs():
    if any((TRACE / "instances").iterdir()):
        raise RuntimeError("Existing trace instances must be stopped by their owner first")
    if (TRACE / "current_tracer").read_text().strip() != "nop":
        raise RuntimeError("An existing tracer is active; leave it untouched")
    if (TRACE / "events/enable").read_text().strip() != "0":
        raise RuntimeError("Existing root event recording is enabled; leave it untouched")
    triggers = list((TRACE / "events/osnoise").glob("*/trigger"))
    triggers += [TRACE / "events/ftrace" / name / "trigger" for name in ("timerlat", "osnoise")]
    for path in triggers:
        if path.exists() and any(line.strip() and not line.lstrip().startswith("#")
                                 for line in path.read_text().splitlines()):
            raise RuntimeError(f"Existing event trigger: {path}; leave it untouched")


def histogram(text, mode, elapsed):
    """Default RTLA hist format, including its legitimate zero-noise footer."""
    # ALL repeats per-CPU IRQ/thread/user counts; it is not another observation.
    per_cpu = re.split(r"^ALL:", text, maxsplit=1, flags=re.M)[0]
    duration = re.search(r"^# Duration:\s*(\d+)\s+(\d+):(\d+):(\d+)\s*$", text, re.M)
    headers = re.findall(r"^Index[ \t]+([^\n]+)$", per_cpu, re.M)
    series = []
    formatted = False
    try:
        if len(headers) != 1 or f"# RTLA {mode} histogram" not in text or not duration:
            raise ValueError("Missing histogram header")
        if "# Time unit is microseconds (us)" not in text:
            raise ValueError("Unknown histogram units")
        names = headers[0].split()
        pattern = r"(?:IRQ|Thr|Usr)-\d+" if mode == "timerlat" else r"CPU-\d+"
        if not names or len(names) != len(set(names)) or not all(re.fullmatch(pattern, n) for n in names):
            raise ValueError("Invalid histogram columns")
        summary = {}
        for key in ("count", "over", "min", "avg", "max"):
            rows = re.findall(r"^" + key + r":[ \t]*([^\n]+)$", per_cpu, re.M)
            if len(rows) != 1 or len(rows[0].split()) != len(names):
                raise ValueError("Incomplete histogram summary")
            values = rows[0].split()
            pattern = r"\d+" if key in ("count", "over") else r"(?:\d+(?:\.\d+)?|-)"
            if not all(re.fullmatch(pattern, value) for value in values):
                raise ValueError("Invalid histogram summary value")
            summary[key] = [None if v == "-" else float(v) if "." in v else int(v) for v in values]
        buckets = []
        for row in per_cpu.splitlines():
            if not re.match(r"^\d", row):
                continue
            values = row.split()
            if len(values) != len(names) + 1 or not all(re.fullmatch(r"\d+", v) for v in values):
                raise ValueError("Invalid histogram bucket")
            buckets.append([int(v) for v in values])
        if len({row[0] for row in buckets}) != len(buckets):
            raise ValueError("Duplicate histogram bucket")
        for index, name in enumerate(names):
            count = summary["count"][index]
            stats = {key: summary[key][index] if count else None for key in ("min", "avg", "max")}
            if count and (any(v is None for v in stats.values()) or not stats["min"] <= stats["avg"] <= stats["max"]):
                raise ValueError("Invalid histogram statistics")
            if sum(row[index + 1] for row in buckets) + summary["over"][index] != count:
                raise ValueError("Histogram counts do not match")
            series.append({"name": name, "count": count, **stats, "over": summary["over"][index],
                           "buckets": [{"value": row[0], "count": row[index + 1]} for row in buckets]})
        formatted = True
    except ValueError:
        series = []  # Do not publish plausible-looking partial statistics.
    counts = [entry["count"] for entry in series]
    total = sum(counts)
    runtime = 0
    if duration:
        days, hours, minutes, seconds = map(int, duration.groups())
        runtime = days * 86400 + hours * 3600 + minutes * 60 + seconds
    valid = formatted and (total > 0 or (mode == "osnoise" and runtime > 0 and elapsed >= .5))
    return {"formatted": bool(formatted), "sample_count": total, "reported_runtime_seconds": runtime,
            "sample_counts": counts, "unit": "us", "series": series,
            "valid": bool(valid), "observation": "SAMPLES_OBSERVED" if total else "NO_NOISE_OBSERVED"
            if valid else "NO_VALID_SAMPLES"}


def owned_run(argv, log, timeout, interrupted):
    """Signal only our new child group, giving RTLA time to restore controls."""
    start = time.monotonic()
    reason = None
    with subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True) as child:
        while child.poll() is None:
            if interrupted[0] or time.monotonic() - start >= timeout:
                reason = "interrupted" if interrupted[0] else "timeout"
                try:
                    os.killpg(child.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait(timeout=5)
                break
            time.sleep(.1)
        return {"returncode": child.wait(), "termination_reason": reason,
                "elapsed_seconds": time.monotonic() - start}


def collection_timeout(duration, target):
    # QBox tracefs instance/event setup can exceed the 30s startup allowance.
    # Keep the requested sampling interval and latency thresholds unchanged.
    return duration + (120 if target == "qbox" else 30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-private-guest", required=True, action="store_true")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--threshold-us", type=int, default=1000)
    parser.add_argument("--priority", type=int, default=50)
    parser.add_argument("--mode", choices=["timerlat", "osnoise"], default="timerlat")
    parser.add_argument("--platform", choices=["tcg", "qbox", "hardware"], default=None)
    args = parser.parse_args()
    if not (1 <= args.duration <= 120 and 1 <= args.priority <= 80 and 1 <= args.threshold_us <= 100000):
        parser.error("duration 1..120s, priority 1..80, threshold 1..100000us")
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    report = {"status": "UNSUPPORTED", "mode": args.mode,
              "qualification": "TRACE_COLLECTION_ONLY_NOT_LATENCY_BUDGET_PASS",
              "platform": args.platform,
              "settings": {"threshold_us": args.threshold_us, "cpu": args.cpu,
                           "duration": args.duration, "priority": args.priority}}
    interrupted = [0]
    lock = None
    capture = None
    previous = {}
    def on_signal(signum, _frame):
        interrupted[0] = signum
    for sig in (signal.SIGINT, signal.SIGTERM):
        previous[sig] = signal.signal(sig, on_signal)
    try:
        if (os.geteuid() or platform.machine() != "aarch64"
                or "Automotive" not in Path("/etc/os-release").read_text()):
            raise RuntimeError("Run only as root inside the explicitly selected private AArch64 AutoSD guest")
        lock = LOCK.open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not shutil.which("rtla") or not (TRACE / "available_tracers").exists():
            raise RuntimeError("rtla and mounted tracefs are required")
        if args.cpu not in os.sched_getaffinity(0):
            raise RuntimeError("CPU is outside allowed affinity")
        if args.mode not in (TRACE / "available_tracers").read_text().split():
            raise RuntimeError("Requested tracer missing from running kernel")
        idle_tracefs()
        report["before"] = settings()
        report["before_instances"] = []
        argv = ["rtla", args.mode, "hist", "-c", str(args.cpu), "-d", str(args.duration) + "s",
                "-P", "f:" + str(args.priority), "--trace=" + str(args.out / "threshold-trace.txt")]
        if args.mode == "timerlat":
            bucket_size = (args.threshold_us + 99) // 100
            argv += ["-T", str(args.threshold_us), "-b", str(bucket_size), "-E", "100"]
        else:
            # Verified tools/tracing/rtla/src/osnoise_hist.c: -s is per-sample stop.
            argv += ["-r", "10000", "-p", "100000", "-s", str(args.threshold_us)]
        report["command"] = argv
        if interrupted[0]:
            raise RuntimeError("Interrupted before starting RTLA")
        report["status"] = "FAIL"
        if args.mode == "osnoise":
            capture = OsnoiseCapture(args.cpu)
            capture.start()
        report["collection_timeout_seconds"] = collection_timeout(args.duration, args.platform)
        with (args.out / "rtla.log").open("x") as log:
            report.update(owned_run(argv, log, report["collection_timeout_seconds"], interrupted))
        raw = (args.out / "rtla.log").read_text()
        report["histogram"] = histogram(raw, args.mode, report["elapsed_seconds"])
        if args.mode == "timerlat":
            report["histogram"].update({"bucket_size_us": bucket_size, "entries": 100})
        report["threshold_stop_marker"] = bool(re.search(
            r"^" + re.escape(args.mode) + r" hit stop tracing\s*$", raw, re.M))
        report["raw_histogram"] = "rtla.log"
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        report["reason"] = str(error)
    finally:
        if capture is not None:
            try:
                report["time_series"] = capture.finish(args.out)
            except (OSError, ValueError) as error:
                report["time_series"] = {"valid": False, "status": "CAPTURE_FAILED",
                                         "samples": [], "reason": str(error)}
            finally:
                try:
                    capture.close()
                except OSError as error:
                    report["capture_cleanup_error"] = str(error)
        trace = args.out / "threshold-trace.txt"
        report["trace_collected"] = trace.is_file() and trace.stat().st_size > 0
        # RTLA FAILED=2 denotes a threshold stop, not necessarily a tool error.
        # Require its explicit marker, real samples and saved trace, never rc=2 alone.
        threshold_stop = (report.get("returncode") == 2 and report.get("threshold_stop_marker", False)
                          and report.get("histogram", {}).get("valid", False)
                          and report["histogram"]["sample_count"] > 0 and report["trace_collected"])
        report["threshold_stop_confirmed"] = bool(threshold_stop)
        if "before" in report:
            try:
                report["after"] = settings()
                report["remaining_instances"] = [p.name for p in (TRACE / "instances").iterdir()]
                report["settings_restored"] = (report["before"] == report["after"]
                                               and not report["remaining_instances"])
            except OSError as error:
                report["settings_restored"] = False
                report["restore_check_error"] = str(error)
            # Never reset controls or remove instances that could belong to another session.
            report["status"] = "PASS" if ((report.get("returncode") == 0 or threshold_stop)
                and not report.get("termination_reason") and not interrupted[0]
                and report.get("histogram", {}).get("valid") and report["settings_restored"]
                and (args.mode != "osnoise" or report.get("time_series", {}).get("valid", False))
                and not report.get("capture_cleanup_error")) else "FAIL"
        report["signal"] = interrupted[0]
        if interrupted[0]:
            report["status"] = "CANCELLED"
        elif report.get("termination_reason") == "timeout":
            report["status"] = "TIMEOUT"
        report["latency_status"] = ("EXCEEDED" if threshold_stop else "NO_THRESHOLD_STOP_OBSERVED") \
            if report["status"] == "PASS" else "NOT_EVALUATED"
        (args.out / "result.json").write_text(json.dumps(report, indent=2) + "\n")
        if lock is not None:
            lock.close()
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    print(json.dumps(report))
    return 0 if report["status"] == "PASS" else 77 if report["status"] == "UNSUPPORTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

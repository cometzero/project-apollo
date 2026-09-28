#!/usr/bin/env python3
"""Bounded, opt-in AutoSD RT wakeup experiments; never a timing certification."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import time
import uuid


def command(argv, timeout=30):
    """Kill only this invocation's process group on timeout; retain stderr."""
    if not shutil.which(argv[0]):
        return {"command": argv, "returncode": 127, "output": "UNAVAILABLE: executable not found"}
    with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, start_new_session=True) as child:
        try:
            output, _ = child.communicate(timeout=timeout)
            return {"command": argv, "returncode": child.returncode, "output": output}
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                output, _ = child.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                output, _ = child.communicate()
            if isinstance(error, KeyboardInterrupt):
                raise
            return {"command": argv, "returncode": 124, "output": output}


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError as error:
        return f"UNAVAILABLE: {error}"


def snapshot():
    files = ["/proc/cmdline", "/proc/interrupts", "/proc/softirqs", "/proc/pressure/cpu",
             "/sys/kernel/realtime", "/proc/sys/kernel/sched_rt_runtime_us",
             "/proc/sys/kernel/sched_rt_period_us", "/sys/devices/system/cpu/online",
             "/sys/kernel/tracing/available_tracers"]
    tools = ("cyclictest", "oslat", "rtla", "trace-cmd", "stress-ng", "chrt", "taskset")
    return {"uname": list(platform.uname()), "files": {p: read(p) for p in files},
            "tools": {t: shutil.which(t) for t in tools},
            "packages": command(["rpm", "-q", "realtime-tests", "rtla", "trace-cmd", "stress-ng"]),
            "selinux": command(["getenforce"]),
            "resources": command(["systemctl", "show", "qm.service", "apollo-asil-b.slice",
                                   "-p", "AllowedCPUs", "-p", "CPUWeight", "-p", "MemoryMax"])}


def probe_command(args, case, priority, inject=0):
    argv = [str(args.probe), "--cpu", str(args.cpu), "--duration", str(args.duration),
            "--period-us", str(args.period_us), "--priority", str(priority),
            "--threshold-us", str(args.threshold_us), "--output", str(args.out / (case + ".json"))]
    if priority:
        argv += ["--mlock"]
    if inject:
        argv += ["--inject-us", str(inject)]
    return argv


def classify(result, measurement, synthetic=False):
    if result["returncode"] or not measurement.get("completed") or not measurement.get("count", 0):
        return "ERROR"
    if synthetic:
        return "DETECTION_PASS" if measurement.get("synthetic") and measurement["threshold_exceedances"] else "ERROR"
    return "EXCEEDED" if measurement["threshold_exceedances"] else "WITHIN_OBSERVED_THRESHOLD"


def default_threshold(platform_name):
    # TCG demo observation limit, not an automotive timing requirement.
    return 5000 if platform_name == "tcg" else 1000


def aggregate_latency(report):
    """Do not grade the SCHED_OTHER baseline or synthetic detection as RT timing."""
    measured = [case for case in report["cases"]
                if case.get("evaluation_role") not in ("baseline", "detection")]
    statuses = [case["latency_status"] for case in measured]
    if report.get("cyclictest"):
        statuses.append(report["cyclictest"].get("latency_status"))
    if "EXCEEDED" in statuses:
        return "EXCEEDED"
    if statuses:
        return "WITHIN_OBSERVED_THRESHOLD"
    return "BASELINE_OBSERVATION" if any(c.get("evaluation_role") == "baseline" for c in report["cases"]) else "DETECTION_PASS"


def cyclic_result(result, path, threshold):
    """Some cyclictest option errors exit zero: require actual sampled JSON."""
    try:
        threads = json.loads(path.read_text())["thread"]
        valid = (result["returncode"] == 0 and bool(threads)
                 and all(t["cycles"] > 0 and 0 <= t["min"] <= t["max"]
                         for t in threads.values()))
        result["status"] = "PASS" if valid else "FAIL"
        result["threads"] = threads
        result["latency_status"] = ("EXCEEDED" if any(t["max"] > threshold for t in threads.values())
                                    else "WITHIN_OBSERVED_THRESHOLD") if valid else "NOT_EVALUATED"
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result.update(status="FAIL", latency_status="NOT_EVALUATED", validation_error=str(error))
    return result


@contextmanager
def loads(args, qm):
    """Owned transient units ensure cleanup also reaches processes inside QM."""
    units = []
    prefix = ["podman", "exec", "qm"] if qm else []
    probe = "/usr/libexec/apollo/latency-probe" if qm else str(args.probe)
    try:
        for cpu in args.qm_cpus if qm else [args.cpu]:
            unit = "apollo-rt-load-" + uuid.uuid4().hex[:12]
            units.append(unit)
            result = command(prefix + ["systemd-run", "--quiet", "--collect", "--unit", unit,
                             "-p", f"RuntimeMaxSec={args.duration + 90}", "-p", "KillMode=control-group",
                             "-p", "CPUAccounting=yes", probe, "--load", "--cpu", str(cpu),
                             "--duration", str(args.duration + 80)])
            if result["returncode"]:
                raise RuntimeError(result["output"])
            result = command(prefix + ["systemctl", "is-active", unit])
            if result["returncode"]:
                raise RuntimeError(f"Load unit did not remain active: {unit}: {result['output']}")
        yield
        for unit in units:
            state = command(prefix + ["systemctl", "is-active", unit])
            usage = command(prefix + ["systemctl", "show", unit, "-p", "CPUUsageNSec",
                                     "-p", "ExecMainStatus", "-p", "Result"])
            (args.out / (unit + "-load.json")).write_text(json.dumps(usage, indent=2) + "\n")
            fields = dict(line.split("=", 1) for line in usage["output"].splitlines() if "=" in line)
            if state["returncode"] or not fields.get("CPUUsageNSec", "").isdigit() or int(fields["CPUUsageNSec"]) <= 0:
                raise RuntimeError(f"Load did not stay active/use CPU: {unit}: {usage['output']}")
    finally:
        errors = []
        for unit in units:
            result = command(prefix + ["systemctl", "stop", unit], timeout=30)
            (args.out / (unit + "-cleanup.json")).write_text(json.dumps(result, indent=2) + "\n")
            # A failed stop is not silently treated as clean. RuntimeMaxSec remains a backstop.
            state = command(prefix + ["systemctl", "is-active", unit])
            if state["output"].strip() not in ("inactive", "failed", "unknown"):
                errors.append(f"Load cleanup not confirmed: {unit}: {state['output']}")
        if errors:
            raise RuntimeError("; ".join(errors))


def run_probe(args, case, priority, inject=0):
    result = command(probe_command(args, case, priority, inject), timeout=args.duration + 30)
    path = args.out / (case + ".json")
    payload = path.read_text() if path.exists() else ""
    measurement = json.loads(payload) if payload.strip() else {}
    result.update(id=case, latency_status=classify(result, measurement, bool(inject)))
    (args.out / (case + "-command.json")).write_text(json.dumps(result, indent=2) + "\n")
    return {"id": case, "returncode": result["returncode"],
            "latency_status": result["latency_status"], "measurement": measurement}


def run_cases(args, report):
    cases = [("R01-other", 0), ("R02-fifo", args.priority),
             ("R03-qm-load", args.priority), ("R04-shared-cpu", args.priority),
             ("R05-injected", args.priority)]
    for case, priority in cases:
        token = case.split("-")[0]
        if args.case not in ("all", token):
            continue
        print(json.dumps({"event": "case-start", "id": case, "status": "RUNNING"}), flush=True)
        try:
            if token in ("R03", "R04"):
                with loads(args, qm=token == "R03"):
                    result = run_probe(args, case, priority)
            else:
                result = run_probe(args, case, priority,
                                   args.threshold_us * 2 + 1000 if token == "R05" else 0)
        except (OSError, RuntimeError, ValueError, KeyboardInterrupt):
            print(json.dumps({"event": "case-complete", "id": case, "status": "FAIL"}), flush=True)
            raise
        result["evaluation_role"] = "baseline" if token == "R01" else "detection" if token == "R05" else "rt_observation"
        report["cases"].append(result)
        print(json.dumps({"event": "case-complete", "id": case,
                          "status": result["latency_status"]}), flush=True)
        if token == "R02" and result["latency_status"] == "ERROR":
            raise RuntimeError("FIFO/mlock probe failed; do not silently fall back to SCHED_OTHER")
    if args.case == "R06" or (args.case == "all" and args.external_tools):
        print(json.dumps({"event": "case-start", "id": "R06-cyclictest", "status": "RUNNING"}), flush=True)
        if shutil.which("cyclictest"):
            result = command(["cyclictest", "-a", str(args.cpu), "-t1", "-p", str(args.priority), "-m",
                              "-D", str(args.duration) + "s", "-i", str(args.period_us), "-q", "-h10000",
                              "--json=" + str(args.out / "cyclictest.json")], args.duration + 30)
            report["cyclictest"] = cyclic_result(result, args.out / "cyclictest.json", args.threshold_us)
        else:
            report["cyclictest"] = {"status": "UNSUPPORTED", "reason": "realtime-tests not installed"}
        print(json.dumps({"event": "case-complete", "id": "R06-cyclictest",
                          "status": report["cyclictest"]["status"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-private-guest", action="store_true", required=True)
    parser.add_argument("--platform", choices=["tcg", "qbox", "hardware"], required=True)
    parser.add_argument("--probe", type=Path, default=Path("/usr/libexec/apollo/latency-probe"))
    parser.add_argument("--health-check", type=Path, default=Path("/usr/libexec/apollo/check-automotive.sh"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--qm-cpus", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--period-us", type=int, default=1000)
    parser.add_argument("--threshold-us", type=int, default=None,
                        help="Observation limit: TCG default 5000us, other platforms 1000us; not a safety budget")
    parser.add_argument("--priority", type=int, default=50)
    parser.add_argument("--external-tools", action="store_true", help="Also run cyclictest if installed")
    parser.add_argument("--case", choices=["all"] + [f"R{i:02d}" for i in range(1, 7)], default="all")
    args = parser.parse_args()
    explicit_threshold = args.threshold_us is not None
    if args.threshold_us is None:
        args.threshold_us = default_threshold(args.platform)
    if not (1 <= args.duration <= 120 and 100 <= args.period_us <= 1000000
            and 1 <= args.threshold_us <= 100000 and 1 <= args.priority <= 80):
        parser.error("duration 1..120s, period 100..1000000us, threshold 1..100000us, priority 1..80")
    if os.geteuid() or platform.machine() != "aarch64" or "Automotive" not in read("/etc/os-release"):
        parser.error("Run only as root inside the explicitly selected private AArch64 AutoSD guest")
    if read("/sys/kernel/realtime") != "1":
        parser.error("Running kernel is not PREEMPT_RT; no RT result may be claimed")
    if args.cpu not in os.sched_getaffinity(0) or args.cpu in args.qm_cpus:
        parser.error("Measurement CPU must be allowed and separate from QM load CPUs")
    args.out = args.out.resolve()
    args.probe = args.probe.resolve(strict=args.case != "R06")
    args.out.mkdir(parents=True, exist_ok=False)
    def interrupted(signum, _frame):
        raise KeyboardInterrupt(f"Interrupted by signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    report = {"platform": args.platform, "qualification": "FUNCTIONAL_MEASUREMENT_ONLY" if args.platform != "hardware"
              else "OBSERVATION_NOT_WCET_OR_SAFETY_PROOF", "settings": vars(args).copy(), "cases": []}
    report["settings"] = {k: str(v) if isinstance(v, Path) else v for k, v in report["settings"].items()}
    report["threshold_policy"] = {
        "profile": "explicit-observation" if explicit_threshold else args.platform + "-observation-v1",
        "threshold_us": args.threshold_us, "hardware_budget": False,
        "baseline_is_gate": False, "synthetic_is_gate": False,
        "note": "Provisional observation limit; not WCET, FTTI or hardware qualification"}
    if args.case != "R06":
        report["probe_sha256"] = hashlib.sha256(args.probe.read_bytes()).hexdigest()
    report["before"] = snapshot()
    started = time.monotonic()
    try:
        report["scenario_before"] = command(["bash", str(args.health_check)], timeout=90)
        if report["scenario_before"]["returncode"]:
            raise RuntimeError("Automotive scenario is not healthy before measurement")
        run_cases(args, report)
    except (OSError, RuntimeError, ValueError, KeyboardInterrupt) as error:
        report["error"] = str(error)
    finally:
        report["scenario_after"] = command(["bash", str(args.health_check)], timeout=90)
        report["scenario_status"] = "PASS" if report["scenario_after"]["returncode"] == 0 else "FAIL"
        report["after"] = snapshot()
        report["elapsed_seconds"] = time.monotonic() - started
        invalid = "error" in report or any(c["latency_status"] == "ERROR" for c in report["cases"])
        invalid |= (args.case == "R06" or (args.case == "all" and args.external_tools)) and report.get("cyclictest", {}).get("status") != "PASS"
        invalid |= report["scenario_status"] != "PASS"
        report["measurement_status"] = "FAIL" if invalid else "PASS"
        report["latency_status"] = aggregate_latency(report)
        if invalid:
            report["latency_status"] = "NOT_EVALUATED"
        (args.out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: report[k] for k in ("measurement_status", "latency_status", "qualification")}))
    return 1 if invalid else 2 if report["latency_status"] == "EXCEEDED" else 0


if __name__ == "__main__":
    raise SystemExit(main())

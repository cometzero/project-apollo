#!/usr/bin/env python3
"""Bounded functional mixed-criticality demos; NOT an ASIL/FFI certification."""
import argparse
import json
import math
import os
from pathlib import Path
import selectors
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid

QUALIFICATION = (
    "Functional observations on one shared Linux kernel, not certified ASIL-B "
    "partitions, freedom-from-interference proof, physical latency or FTTI guarantees."
)
# Existing monitor allows a 10 s Podman probe, then sleeps 1 s. One more
# interval is a functional observation margin, not a safety/FTTI budget.
MONITOR_MAX_AGE = 12.0


def healthy_monitor(now=None):
    now = time.monotonic() if now is None else now
    state = json.loads(Path("/run/apollo-safety/state.json").read_text())
    stamp = float(state["monotonic"])
    age = now - stamp
    require(state["state"] == "HEALTHY" and math.isfinite(stamp)
            and -.1 <= age < MONITOR_MAX_AGE,
            "Safety monitor is unhealthy or stale (12 second observation budget)")
    return state, age


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def event(kind, **fields):
    print(json.dumps({"event": kind, **fields}), flush=True)


class Runner:
    def __init__(self, output):
        self.log = (output / "commands.log").open("w")

    def write(self, text):
        self.log.write(text)
        self.log.flush()
        print(text, end="", flush=True)

    def run(self, *args, timeout=60, check=True):
        self.write("$ " + shlex.join(args) + "\n")
        chunks = []
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              start_new_session=True) as child:
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ)
                    deadline = time.monotonic() + timeout
                    while selector.get_map():
                        require(time.monotonic() < deadline, "Command deadline exceeded")
                        for key, _ in selector.select(min(.2, max(0, deadline - time.monotonic()))):
                            data = os.read(key.fileobj.fileno(), 4096)
                            if not data:
                                selector.unregister(key.fileobj)
                                continue
                            text = data.decode(errors="replace")
                            chunks.append(text)
                            self.write(text)
                    code = child.wait(timeout=max(.01, deadline - time.monotonic()))
            except BaseException:
                # Only our newly-created process group; no process-name kill.
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()
                raise
        self.write(f"[exit={code}]\n")
        require(not check or code == 0, f"Command failed ({code}): {shlex.join(args)}")
        return "".join(chunks).strip()

    def qm(self, *args, **kwargs):
        return self.run("podman", "exec", "qm", *args, **kwargs)


def process_info(pid):
    root = Path(f"/proc/{pid}")
    status = dict(line.split(":", 1) for line in (root / "status").read_text().splitlines()
                  if ":" in line)
    cgroup = next(line[3:] for line in (root / "cgroup").read_text().splitlines()
                  if line.startswith("0::"))
    base = Path("/sys/fs/cgroup") / cgroup.lstrip("/")
    chain = []
    while True:
        entry = {"path": str(base)}
        for name in ("cpuset.cpus.effective", "memory.max", "memory.high", "cpu.max", "cpu.weight"):
            file = base / name
            if file.exists():
                entry[name] = file.read_text().strip()
        chain.append(entry)
        if base == Path("/sys/fs/cgroup"):
            break
        base = base.parent
    return {"pid": pid, "cpus": status["Cpus_allowed_list"].strip(),
            "label": (root / "attr/current").read_text().strip(),
            "cgroup": cgroup, "limits": chain,
            "pid_namespace": os.readlink(root / "ns/pid")}


def finite_memory(info):
    values = [int(row["memory.max"]) for row in info["limits"]
              if row.get("memory.max", "max").isdigit()]
    require(values, "No effective finite memory.max")
    return min(values)


def placement(run):
    require(run.run("getenforce") == "Enforcing", "SELinux must be Enforcing")
    for unit in ("bluechi-controller", "bluechi-agent", "qm", "apollo-adas", "apollo-safety-monitor"):
        run.run("systemctl", "is-active", "--quiet", unit)
    adas = process_info(int(run.run("podman", "inspect", "--format", "{{.State.Pid}}", "apollo-adas")))
    qm = process_info(int(run.run("podman", "inspect", "--format", "{{.State.Pid}}", "qm")))
    monitor = process_info(int(run.run("systemctl", "show", "--value", "-p", "MainPID", "apollo-safety-monitor")))
    require(adas["cpus"] == "1" and qm["cpus"] == "2-3" and monitor["cpus"] == "0",
            "Unexpected ADAS/QM/root-monitor CPU placement")
    for item, expected in ((adas, "1"), (qm, "2-3")):
        require(item["limits"][0].get("cpuset.cpus.effective") == expected,
                "Actual effective cpuset differs from expected placement")
    require("apollo-asil-b.slice" in adas["cgroup"], "ADAS outside designated slice")
    require(finite_memory(adas) <= 384 * 1024**2, "ADAS memory limit exceeds configured 384 MiB")
    require(len({adas["pid_namespace"], qm["pid_namespace"], monitor["pid_namespace"]}) == 3,
            "Root, ADAS and QM PID namespaces are not distinct")
    require("container_t" in adas["label"] and "qm" in qm["label"], "Unexpected SELinux domains")
    run.qm("systemctl", "is-active", "--quiet", "apollo-qm-app", "apollo-qm-container", "bluechi-agent")
    run.qm("/usr/libexec/apollo/workload", "health", "/run/apollo-qm/heartbeat")
    run.qm("podman", "exec", "apollo-qm-container", "/workload", "health", "/run/heartbeat")
    # Synchronous mutation gate: sampler startup alone does not establish
    # a healthy baseline before submitting the load/container-kill command.
    run.run("podman", "exec", "apollo-adas", "/workload", "health", "/run/heartbeat")
    state, age = healthy_monitor()
    return {"root_monitor": monitor, "adas": adas, "qm": qm,
            "safety_monitor": state, "safety_monitor_age_seconds": age}


class Heartbeats:
    """Read the actual workload timestamp during commands, not only before/after."""
    def __init__(self, pid):
        self.pid = pid
        self.samples = []
        self.errors = []
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.collect, daemon=True)

    def collect(self):
        while not self.stop_event.is_set():
            try:
                now = time.monotonic()
                stamp = float(Path(f"/proc/{self.pid}/root/run/heartbeat").read_text())
                state, monitor_age = healthy_monitor(now)
                cpus = next(line.split(":", 1)[1].strip() for line in
                            Path(f"/proc/{self.pid}/status").read_text().splitlines()
                            if line.startswith("Cpus_allowed_list:"))
                sample = {"monotonic": now, "heartbeat": stamp, "age_seconds": now - stamp,
                          "monitor_state": state["state"], "monitor_monotonic": state["monotonic"],
                          "monitor_age_seconds": monitor_age, "cpus": cpus}
                self.samples.append(sample)
                require(math.isfinite(stamp) and -.1 <= now - stamp < 1.0,
                        "ADAS heartbeat stale (existing workload health budget: 1 second)")
                require(state["state"] == "HEALTHY" and cpus == "1", "ADAS health/placement changed")
            except Exception as error:
                self.errors.append(str(error))
            self.stop_event.wait(.25)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=2)

    def wait_for_monitor_update(self):
        deadline = time.monotonic() + MONITOR_MAX_AGE
        while time.monotonic() < deadline and not self.errors:
            if (len(self.samples) >= 4 and
                    self.samples[-1]["monitor_monotonic"] > self.samples[0]["monitor_monotonic"]):
                break
            time.sleep(.25)

    def metrics(self):
        require(not self.errors, "; ".join(self.errors[:5]))
        require(len(self.samples) >= 4, "Insufficient concurrent ADAS samples")
        advances = sum(b["heartbeat"] > a["heartbeat"] for a, b in zip(self.samples, self.samples[1:]))
        monitor_advances = sum(b["monitor_monotonic"] > a["monitor_monotonic"]
                               for a, b in zip(self.samples, self.samples[1:]))
        require(advances > 0, "ADAS heartbeat did not advance")
        require(monitor_advances > 0, "Safety monitor timestamp did not advance")
        return [{"name": "adas_samples", "value": len(self.samples), "unit": "count"},
                {"name": "adas_heartbeat_advances", "value": advances, "unit": "count"},
                {"name": "adas_max_observed_age", "value": max(s["age_seconds"] for s in self.samples), "unit": "s"},
                {"name": "monitor_timestamp_advances", "value": monitor_advances, "unit": "count"},
                {"name": "monitor_max_observed_age", "value": max(s["monitor_age_seconds"] for s in self.samples), "unit": "s"}]


def scenario(case, run, output):
    result = {"id": case, "status": "RUNNING", "metrics": [], "observations": {}}
    sampler = None
    load_unit = None
    replacement_requested = False
    event("case-start", id=case, status="RUNNING")
    try:
        before = placement(run)
        result["observations"]["before"] = before
        sampler = Heartbeats(before["adas"]["pid"])
        sampler.start()
        event("progress", id=case, message="Sampling live ADAS heartbeat and safety monitor")
        if case == "MC01":
            time.sleep(2)
        elif case == "MC02":
            load_unit = "apollo-mc-load-" + uuid.uuid4().hex + ".service"
            # Set the name before submission: a timed-out D-Bus request may have
            # created it. A UUID is our ownership token, never a shared unit name.
            run.qm("systemd-run", "--unit", load_unit, "--property=RuntimeMaxSec=30",
                   "--property=CPUAccounting=yes", "--property=CPUQuota=100%", "--property=MemoryMax=32M",
                   "--property=TasksMax=4", "/bin/sh", "-c", "while :; do :; done")
            run.qm("systemctl", "is-active", "--quiet", load_unit)
            load_cgroup = run.qm("systemctl", "show", "--value", "-p", "ControlGroup", load_unit)
            require(load_cgroup.startswith("/") and ".." not in load_cgroup.split("/"),
                    "Invalid load cgroup path")
            load_cpus = run.qm("cat", "/sys/fs/cgroup" + load_cgroup + "/cpuset.cpus.effective")
            require(load_cpus == "2-3", "Load escaped QM CPU placement")
            result["observations"]["load_effective_cpus"] = load_cpus
            time.sleep(8)
            run.qm("systemctl", "is-active", "--quiet", load_unit)
            usage = run.qm("systemctl", "show", "--value", "-p", "CPUUsageNSec", load_unit)
            require(usage.isdigit() and int(usage) > 0, "QM load did not consume measured CPU time")
            result["metrics"].append({"name": "qm_load_cpu_time", "value": int(usage) / 1e9, "unit": "s"})
            result["observations"]["owned_load_unit"] = load_unit
        elif case == "MC03":
            old = run.qm("podman", "inspect", "--format", "{{.Id}}", "apollo-qm-container")
            require(bool(old), "No existing QM container")
            replacement_requested = True
            run.qm("podman", "kill", "--signal", "KILL", "apollo-qm-container")
            deadline = time.monotonic() + 90
            new = old
            while time.monotonic() < deadline:
                new = run.qm("podman", "inspect", "--format", "{{.Id}}", "apollo-qm-container", check=False)
                if new and new != old and len(new) == 64 and all(c in "0123456789abcdef" for c in new):
                    try:
                        run.qm("podman", "exec", "apollo-qm-container", "/workload", "health", "/run/heartbeat")
                    except RuntimeError:
                        # ID allocation precedes application readiness.
                        pass
                    else:
                        break
                event("progress", id=case, message="Waiting for systemd to recreate QM container")
                time.sleep(1)
            else:
                raise RuntimeError("QM container was not recreated within 90 seconds")
            result["observations"].update(old_container_id=old, new_container_id=new)
            time.sleep(2)
        after = placement(run)
        result["observations"]["after"] = after
        require(after["adas"]["pid"] == before["adas"]["pid"], "ADAS restarted during QM experiment")
        result["status"] = "PASS"
    except Exception as error:
        result.update(status="FAIL", reason=str(error))
    finally:
        if load_unit:
            try:
                run.qm("systemctl", "stop", load_unit)
                active = run.qm("systemctl", "is-active", load_unit, check=False)
                require(active in ("inactive", "failed", "unknown"), "Owned load still active")
                if active == "failed":
                    run.qm("systemctl", "reset-failed", load_unit)
                result["observations"]["load_cleanup"] = "PASS"
            except Exception as error:
                result.update(status="FAIL", cleanup_error=str(error))
        if replacement_requested:
            try:
                # Restore only the previously healthy selected demo service.
                run.qm("systemctl", "start", "apollo-qm-container")
                run.qm("podman", "exec", "apollo-qm-container", "/workload", "health", "/run/heartbeat")
                result["observations"]["qm_cleanup"] = "PASS"
            except Exception as error:
                result.update(status="FAIL", cleanup_error=str(error))
        if sampler:
            sampler.wait_for_monitor_update()
            sampler.stop()
            result["observations"]["heartbeat_samples"] = sampler.samples
            result["observations"]["heartbeat_errors"] = sampler.errors
            try:
                result["metrics"].extend(sampler.metrics())
            except Exception as error:
                result.update(status="FAIL", heartbeat_error=str(error))
        (output / (case + ".json")).write_text(json.dumps(result, indent=2) + "\n")
        event("case-complete", id=case, status=result["status"], metrics=result["metrics"],
              reason=result.get("reason", result.get("heartbeat_error", result.get("cleanup_error", ""))))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("MC01", "MC02", "MC03", "all"), default="all")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--allow-disruptive-demo", action="store_true", required=True)
    args = parser.parse_args(argv)
    require(os.geteuid() == 0, "Run only as root inside the explicitly selected disposable AutoSD guest")
    def interrupted(number, _frame):
        raise RuntimeError(f"Demo interrupted by signal {number}")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    args.out.mkdir(parents=True, exist_ok=False)
    run = Runner(args.out)
    report = {"kind": "mixed-criticality", "status": "RUNNING", "scenarios": [], "qualification": QUALIFICATION}
    try:
        for case in (("MC01", "MC02", "MC03") if args.case == "all" else (args.case,)):
            report["scenarios"].append(scenario(case, run, args.out))
            report["status"] = "PASS" if all(c["status"] == "PASS" for c in report["scenarios"]) else "FAIL"
            (args.out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
            if report["status"] != "PASS":
                break
    finally:
        run.log.close()
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Measure a running full QBox using existing host and guest counters.

QMP identifies domain vCPU host threads. /proc CPU accounting measures their
host cost, while SystemC time lets runs at different speeds be compared.
Guest snapshots are outside the timed windows. PFDI count commands report
available tests, not completed iterations, and are deliberately not used.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "autosd_dashboard"))
from qbox_diagnostics import QBoxDiagnostics
from qbox_monitor import QBoxMonitorCollector, process_identity


def proc_stat(path):
    raw = path.read_text()
    fields = raw.rsplit(")", 1)[1].split()
    return {
        "comm": raw[raw.index("(") + 1:raw.rindex(")")],
        "cpu_ticks": int(fields[11]) + int(fields[12]),
        "user_ticks": int(fields[11]),
        "system_ticks": int(fields[12]),
        "start_ticks": int(fields[19]),
    }


def host_snapshot(pid):
    base = Path("/proc") / str(pid)
    threads = {}
    for task in (base / "task").iterdir():
        try:
            value = proc_stat(task / "stat")
            value.update({key: int(number) for key, number in re.findall(
                r"^(voluntary_ctxt_switches|nonvoluntary_ctxt_switches):\s+(\d+)$",
                (task / "status").read_text(), re.M)})
            threads[task.name] = value
        except FileNotFoundError:
            continue
    return {"monotonic": time.monotonic(), "process": proc_stat(base / "stat"),
            "threads": threads, "loadavg": Path("/proc/loadavg").read_text().strip()}


def guest_snapshot(run_dir, tag):
    """Collect process and scheduler accounting; do not enable tracing."""
    console = run_dir / "qbox-primary-console.log"
    offset = console.stat().st_size
    command = (
        f"printf '\\nPFDI_LOAD_{tag}_%s\\n' BEGIN; "
        "echo UPTIME; cat /proc/uptime; echo CPU; cat /proc/stat; "
        "echo INTERRUPTS; cat /proc/interrupts; "
        "echo PFDI_CONFIG; if [ -r /run/pfdi-sample-app.log ]; then "
        "head -n 8 /run/pfdi-sample-app.log; else "
        "journalctl -b -u pfdi-app --no-pager -n 8; fi; "
        "for p in $(pidof pfdi-sample-app); do "
        "for t in /proc/$p/task/*; do echo TASK:$t; "
        "cat $t/stat; if [ -r $t/schedstat ]; then cat $t/schedstat; fi; "
        "grep ctxt_switches $t/status; done; done; "
        "for c in /proc/[0-9]*/comm; do read -r name < $c; "
        "case $name in pfdi_worker*) t=${c%/comm}; echo TASK:$t; "
        "cat $t/stat; if [ -r $t/schedstat ]; then cat $t/schedstat; fi; "
        "grep ctxt_switches $t/status;; "
        "esac; done; "
        f"printf 'PFDI_LOAD_{tag}_%s\\n' END\n"
    )
    fd = os.open(run_dir / "primary-uart-input.fifo", os.O_WRONLY | os.O_NONBLOCK)
    try:
        os.write(fd, command.encode())
    finally:
        os.close(fd)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        with console.open("rb") as stream:
            stream.seek(offset)
            text = stream.read().decode(errors="replace").replace("\r", "")
        match = re.search(rf"^PFDI_LOAD_{tag}_BEGIN\n(.*?)^PFDI_LOAD_{tag}_END$",
                          text, re.M | re.S)
        if match:
            return match[1]
        time.sleep(.2)
    raise RuntimeError("guest snapshot timed out: " + tag)


def summarize(before, after, sim_seconds, domain_threads, ticks_per_second):
    elapsed = after["monotonic"] - before["monotonic"]
    if elapsed <= 0 or sim_seconds <= 0:
        raise RuntimeError("host and simulation clocks must advance")
    if before["process"]["start_ticks"] != after["process"]["start_ticks"]:
        raise RuntimeError("QBox process identity changed")
    def cost(ticks):
        cpu_seconds = ticks / ticks_per_second
        return {"cpu_seconds": cpu_seconds,
                "host_cpu_percent": 100 * cpu_seconds / elapsed,
                "cpu_seconds_per_sim_second": cpu_seconds / sim_seconds}
    domains = {}
    for domain, tids in domain_threads.items():
        ticks = voluntary = involuntary = 0
        for tid in tids:
            start, end = before["threads"][str(tid)], after["threads"][str(tid)]
            if start["start_ticks"] != end["start_ticks"]:
                raise RuntimeError("vCPU thread identity changed")
            ticks += end["cpu_ticks"] - start["cpu_ticks"]
            voluntary += end["voluntary_ctxt_switches"] - start["voluntary_ctxt_switches"]
            involuntary += end["nonvoluntary_ctxt_switches"] - start["nonvoluntary_ctxt_switches"]
        domains[domain] = {**cost(ticks), "voluntary_context_switches": voluntary,
                           "involuntary_context_switches": involuntary}
    return {"host_seconds": elapsed, "sim_seconds": sim_seconds,
            "sim_seconds_per_host_second": sim_seconds / elapsed,
            "process": cost(after["process"]["cpu_ticks"] - before["process"]["cpu_ticks"]),
            "domains": domains}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--monitor-port", type=int, default=18110)
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--windows", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.seconds <= 0 or args.windows < 1:
        parser.error("seconds and windows must be positive")
    domains = [{"domain_id": domain, "qmp_biflow": path + ".qmp_socket.qmp_socket_router"}
               for domain, path in (("rse", "platform.rse_cpu_pass.rse_qmp"),
                                    ("si-cl0", "platform.si_cl0_qmp"),
                                    ("si-cl1", "platform.si_cl1_qmp"),
                                    ("ap", "platform.ap_qmp"))]
    manifest = {"run_id": args.run_dir.name, "backend": "qbox-full", "domains": domains,
                "monitor": {"host": "127.0.0.1", "port": args.monitor_port,
                            "owner_pid": args.pid,
                            "owner_start_ticks": process_identity(args.pid)[1]}}
    collector = QBoxMonitorCollector(manifest, timeout=5)
    diagnostics = QBoxDiagnostics(collector, timeout=5)
    cpus = {d["domain_id"]: diagnostics.query(d["domain_id"], "query-cpus-fast")
            for d in domains}
    tids = {domain: [cpu["thread-id"] for cpu in response["result"]]
            for domain, response in cpus.items()}
    flat = [tid for group in tids.values() for tid in group]
    if len(set(flat)) != len(flat):
        raise RuntimeError("shared QMP thread IDs prevent domain attribution")
    record = {"schema_version": 1, "status": "INCOMPLETE", "manifest": manifest,
              "qmp_cpus": cpus, "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"),
              "windows": [], "notes": [
                  "100 percent is one host CPU; a domain sum may exceed 100 percent.",
                  "Domain cost includes all guest work, not only PFDI.",
                  "SystemC timestamps bracket host snapshots; endpoints are not atomic.",
                  "No monitor or guest commands run inside each measurement window.",
                  "Guest accounting includes Linux time only, not firmware execution.",
              ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        for index in range(args.windows):
            guest_before = guest_snapshot(args.run_dir, f"{index}_BEFORE")
            sim_before = collector._get("/sc_time")
            before = host_snapshot(args.pid)
            deadline = time.monotonic() + args.seconds
            while time.monotonic() < deadline:
                time.sleep(min(1, max(0, deadline - time.monotonic())))
            after = host_snapshot(args.pid)
            sim_after = collector._get("/sc_time")
            guest_after = guest_snapshot(args.run_dir, f"{index}_AFTER")
            summary = summarize(before, after,
                                sim_after["sc_time_stamp"] - sim_before["sc_time_stamp"],
                                tids, record["clock_ticks_per_second"])
            record["windows"].append({"summary": summary, "host_before": before,
                                      "host_after": after, "sim_before": sim_before,
                                      "sim_after": sim_after, "guest_before": guest_before,
                                      "guest_after": guest_after})
            print(json.dumps({"window": index, **summary}), flush=True)
        record["status"] = "PASS"
    finally:
        args.output.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()

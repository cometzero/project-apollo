"""Private-guest watchdog scenarios with independent host reset evidence."""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def run_command(dashboard, directory, log, command, uploads=(), downloads=(), timeout=180):
    argv = [sys.executable, str(ROOT / "scripts/autosd_demo/guest_exec.py"),
            "--port", str(dashboard.ssh_port), "--out", str(directory),
            "--timeout", str(timeout), "--connect-timeout", "30", "--command", command]
    for source, dest in uploads:
        argv += ["--upload", str(source) + ":" + dest]
    for source, dest in downloads:
        argv += ["--download", source + ":" + dest]
    process = subprocess.Popen(argv, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                               start_new_session=True)
    try:
        return process.wait(timeout=timeout + 40)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        return 124


def trace_evidence(platform, si0):
    events = []
    expected = [(1, 0), (1, 1), (0, 0)]
    for match in re.finditer(r"platform\.ap_watchdog_0 ws0=(\d) ws1=(\d) sc_time=([\d.]+) (ps|ns|us|ms|s)", platform):
        pair = (int(match[1]), int(match[2]))
        if len(events) < 3 and pair == expected[len(events)]:
            events.append({"event": ("WS0", "WS1", "reset-clear")[len(events)],
                           "clock": "SystemC", "value": float(match[3]), "unit": match[4]})
    rearm = bool(re.search(r"AP watchdog IRQ 321 snapshot: enabled=1 pending=0 recovery=0", si0)
                 and re.search(r"Watchdog rearm attempt=\d+ before=0 after=0 status=0", si0))
    return {"status": "PASS" if len(events) == 3 and rearm else "FAIL",
            "timeline": events, "si0_irq_rearmed": rearm}


def descendants(pid):
    """PID plus starttime prevents a recycled PID satisfying continuity."""
    found, pending = {}, [pid]
    while pending:
        current = pending.pop()
        try:
            raw = Path(f"/proc/{current}/stat").read_text()
            fields = raw[raw.rindex(")") + 2:].split()
            cmd = Path(f"/proc/{current}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            if "qbox" in cmd:
                found[str(current)] = {"starttime": fields[19], "command": cmd}
            pending += [int(value) for value in Path(f"/proc/{current}/task/{current}/children").read_text().split()]
        except (OSError, ValueError):
            continue
    return found


def read_since(path, offset):
    with path.open("rb") as stream:
        if path.stat().st_size < offset:
            raise RuntimeError("Reset evidence log was truncated")
        stream.seek(offset)
        data = stream.read(16 * 1024 * 1024 + 1)
        if len(data) > 16 * 1024 * 1024:
            raise RuntimeError("Reset evidence exceeded bounded log limit")
        return data.decode(errors="replace")


def boot_snapshot(dashboard, directory, log):
    code = run_command(dashboard, directory, log,
                       "cat /proc/sys/kernel/random/boot_id", timeout=30)
    if code == 0:
        try:
            value = (directory / "console.log").read_text().strip()
            if re.fullmatch(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", value):
                return {"status": "ONLINE", "boot_id": value}
        except OSError:
            pass
    return {"status": "UNAVAILABLE"}


def expiry(dashboard, job, log, directory, remote):
    job["phase"] = "WD04 reset 전 boot ID · 앱 health · HIPC 기준 상태 검사"
    dashboard.persist(job)
    before = boot_snapshot(dashboard, directory / "before-boot", log)
    domains = dashboard.domain_boot()
    boot = next(j for j in dashboard.jobs if j["id"] == dashboard.vm_job)
    vm = Path(boot["evidence_path"]) / "vm"
    trace = vm / "full-system/qbox-platform.log"
    si0 = vm / "si-cl0-uart.log"
    if (dashboard.backend != "qbox-full" or before.get("status") != "ONLINE"
            or not before.get("boot_id") or domains.get("status") != "PASS"):
        raise RuntimeError("WD04 requires a healthy owned QBox full guest")
    launch = load(vm / "launch.json")
    if launch.get("environment", {}).get("QBOX_APOLLO_RESET_TRACE") != "1":
        raise RuntimeError("WD04 requires a new --reset-trace boot; reset not issued")
    uploads = [(ROOT / "autosd/customization/check-guest.sh", remote + "-check.sh"),
               (ROOT / "scripts/autosd_demo/check_hipc_link.sh", remote + "-hipc.sh"),
               (ROOT / "scripts/autosd_demo/hipc_ping.py", remote + "-ping.py")]
    check = "set -e; bash " + remote + "-check.sh; bash " + remote + "-hipc.sh " + remote + "-ping.py"
    if run_command(dashboard, directory / "baseline", log, check, uploads, timeout=300):
        raise RuntimeError("Baseline Automotive health/HIPC failed; reset not issued")
    paths = (trace, si0)
    offsets = [path.stat().st_size for path in paths]
    processes = descendants(dashboard.vm_process.pid)
    if not processes:
        raise RuntimeError("Cannot establish host process continuity")
    result = {"id": "WD04", "status": "FAIL", "before": {"boot_id": before["boot_id"],
              "domains": domains, "processes": processes}, "offsets": dict(zip(map(str, paths), offsets))}
    with dashboard.lock:
        uart = vm / "linux-uart.log"
        dashboard.guest_log_offset = uart.stat().st_size
        dashboard.log_session = job["id"]
        job["log_session"] = job["id"]
        dashboard.persist(job)
    job["phase"] = "WD04 feeding 중단 · WS0/WS1 및 AP reset 대기 (Guest UART 확인)"
    dashboard.persist(job)
    code = run_command(dashboard, directory / "expiry", log,
                       "python3 " + remote + "-watchdog.py expiry --timeout 20 --acknowledge-reset --output " + remote,
                       [(ROOT / "scripts/autosd_demo/watchdog_guest.py", remote + "-watchdog.py")], timeout=180)
    result["expiry_ssh_returncode"] = code  # Disconnect/124 is not a verdict.
    deadline = time.monotonic() + dashboard.boot_timeout
    after = {}
    attempt = 0
    while time.monotonic() < deadline and dashboard.running():
        job["phase"] = "WS1 이후 AP boot ID / firmware / module 복구 대기"
        dashboard.persist(job)
        log.write(b"[WD04] Waiting for new AP boot and current provision evidence\n")
        attempt += 1
        after = boot_snapshot(dashboard, directory / ("recovery-boot-%03d" % attempt), log)
        if dashboard.reboot_verified(before, after, domains):
            break
        time.sleep(3)
    after_domains = dashboard.domain_boot()
    after_processes = descendants(dashboard.vm_process.pid)
    snippets = [read_since(path, offset) for path, offset in zip(paths, offsets)]
    for name, snippet in zip(("watchdog-trace.log", "si0-reset.log"), snippets):
        (directory / name).write_text(snippet)
    proof = trace_evidence(*snippets)
    result.update(after={"boot_id": after.get("boot_id"), "domains": after_domains,
                         "processes": after_processes}, trace=proof, timeline=proof["timeline"])
    continuous = all(after_processes.get(pid) == value for pid, value in processes.items())
    old_epochs = {r["id"]: r.get("boot_epoch") for r in domains["domains"]}
    preserved = all(r.get("boot_epoch") == old_epochs[r["id"]]
                    for r in after_domains["domains"] if r["id"] != "ap")
    result.update(host_process_continuity=continuous, retained_si_rse_epochs=preserved)
    result["observations"] = {"host_process_continuity": continuous,
                              "retained_si_rse_epochs": preserved,
                              "ordered_WS0_WS1_reset_clear": proof["status"] == "PASS",
                              "si0_irq_rearmed": proof["si0_irq_rearmed"]}
    if dashboard.reboot_verified(before, after, domains):
        job["phase"] = "WD04 새 AP 부팅 확인 · 앱 health 및 HIPC 복구 검사"
        dashboard.persist(job)
        health = run_command(dashboard, directory / "recovery", log,
                             check, uploads, timeout=300)
        result["health_hipc_returncode"] = health
        result["observations"]["health_HIPC_3_of_3"] = health == 0
        if health == 0 and continuous and preserved and proof["status"] == "PASS":
            result["status"] = "PASS"
            dashboard.monitoring = dict(dashboard.monitoring, **after)
    return result


def run(dashboard, job, log):
    directory = Path(job["evidence_path"])
    action = job["action"]
    cases = [action.rsplit("-", 1)[1].upper()] if action != "watchdog" else ["WD01", "WD02", "WD03"]
    rows = []
    result = {"kind": "watchdog", "status": "FAIL", "scenarios": rows,
              "qualification": "Functional QVP observation, not ASIL/FTTI or physical timing qualification"}
    for case in cases:
        log.write((json.dumps({"event": "case-start", "id": case, "status": "RUNNING"}) + "\n").encode())
        job["phase"] = case + " 실행 중"
        dashboard.persist(job)
        remote = "/var/tmp/apollo-watchdog-" + job["id"] + "-" + case.lower()
        try:
            if case == "WD04":
                row = expiry(dashboard, job, log, directory, remote)
                result.update(after_boot_id=row["after"].get("boot_id"), timeline=row["timeline"],
                              before=row["before"], after=row["after"])
            else:
                source = "watchdog_process_demo.py" if case == "WD03" else "watchdog_guest.py"
                options = "--out " if case == "WD03" else ("inspect --output " if case == "WD01" else "keepalive --timeout 20 --duration 30 --output ")
                downloads = [(remote + "/result.json", "scenario.json")]
                if case != "WD03":
                    downloads.append((remote + "/events.jsonl", "events.jsonl"))
                code = run_command(dashboard, directory / case, log,
                                   "python3 " + remote + ".py " + options + remote,
                                   [(ROOT / "scripts/autosd_demo" / source, remote + ".py")],
                                   downloads, timeout=300)
                data = load(directory / case / "scenario.json")
                row = dict(data, id=case, status="PASS" if code == 0 and data.get("status") in ("PASS", "INSPECTED") else "FAIL")
                row["observations"] = {key: value for key, value in data.items() if key != "status"}
                if case == "WD02":
                    try:
                        events = [json.loads(line) for line in (directory / case / "events.jsonl").read_text().splitlines()]
                        row["samples"] = [event for event in events if event.get("event") == "keepalive"]
                        row["observations"]["ioctl_keepalive_samples"] = len(row["samples"])
                        row["observations"]["timeleft_after_ping_s"] = [event["timeleft_s"] for event in row["samples"]]
                        if not row["samples"]:
                            row["status"] = "FAIL"
                    except (OSError, ValueError, KeyError):
                        row["status"] = "FAIL"
        except Exception as error:
            row = {"id": case, "status": "FAIL", "error": str(error)}
        rows.append(row)
        log.write((json.dumps({"event": "case-end", **row}) + "\n").encode())
        if row["status"] != "PASS":
            break
    result["status"] = "PASS" if len(rows) == len(cases) and all(row["status"] == "PASS" for row in rows) else "FAIL"
    job["phase"] = "완료 · " + result["status"]
    (directory / "scenarios.json").write_text(json.dumps(result, indent=2) + "\n")
    return result

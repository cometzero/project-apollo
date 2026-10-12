#!/usr/bin/env python3
"""Measure one full-QBox SCP idle configuration without guest probes.

Repeat this command with a fresh output directory for independent boots.
CPU percentages describe host vCPU thread cost, not physical SI utilization.
"""

import argparse
from contextlib import suppress
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

from measure_qbox_pfdi_load import (
    QBoxDiagnostics, QBoxMonitorCollector, host_snapshot, process_identity,
    summarize,
)

ROOT = Path(__file__).resolve().parents[2]


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return number


def read(path):
    return path.read_text(errors="replace") if path.exists() else ""


def owned_native(out, launcher):
    """Use the runner's PID record, checking ancestry and process lifetime."""
    path = out / "board-launch.json"
    if not path.exists():
        return None
    record = json.loads(path.read_text())
    pid = record.get("pid")
    if pid is None:
        return None
    try:
        ancestor, ticks = process_identity(pid)
        if ticks != record["start_ticks"]:
            return None
        while ancestor > 1 and ancestor != launcher.pid:
            ancestor = process_identity(ancestor)[0]
        return pid if ancestor == launcher.pid else None
    except (OSError, ValueError):
        return None


def stop(out, launcher):
    # platforms-vp creates its own session. Stop it first so the runner can
    # finish its result.json; killing just the wrapper would orphan QBox.
    pid = owned_native(out, launcher)
    if pid is not None:
        with suppress(ProcessLookupError):
            os.killpg(pid, signal.SIGTERM)
    try:
        return launcher.wait(timeout=20)
    except subprocess.TimeoutExpired:
        pid = owned_native(out, launcher)
        if pid is not None:
            with suppress(ProcessLookupError):
                os.killpg(pid, signal.SIGKILL)
        with suppress(ProcessLookupError):
            os.killpg(launcher.pid, signal.SIGTERM)
        try:
            return launcher.wait(timeout=10)
        except subprocess.TimeoutExpired:
            with suppress(ProcessLookupError):
                os.killpg(launcher.pid, signal.SIGKILL)
            return launcher.wait(timeout=5)


def launch_command(args):
    return [str(ROOT / "run_qbox_yocto.sh"), "--bsp", "--headless",
               "--no-vmcu", "--multi-session", "--copy-disks",
               "--no-persistent-rse-state", "--timeout", "0",
               "--keep-running-after-pass", "--foreground-runtime",
               "--monitor-port", str(args.monitor_port),
               "--out-dir", str(args.out_dir.resolve()),
               "--si-cl0-image", str(args.si_cl0_image.resolve()),
               "--rse-flash", str(args.rse_flash.resolve())]


def execute(args, record):
    out = args.out_dir.resolve()
    command = launch_command(args)
    record.update(command=command, inputs={})
    for key, path in (("si_cl0", args.si_cl0_image), ("rse_flash", args.rse_flash)):
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        record["inputs"][key] = {"path": str(path.resolve()), "sha256": digest}
    with tempfile.TemporaryDirectory(prefix="scp-idle-") as qmp_dir, \
            (out / "launcher.log").open("w") as log:
        env = dict(os.environ, QBOX_APOLLO_QMP_DIR=qmp_dir,
                   QBOX_DASHBOARD_RUN_ID=args.name)
        launcher = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + args.boot_timeout
            while time.monotonic() < deadline:
                if launcher.poll() is not None:
                    raise RuntimeError("launcher exited before BSP readiness")
                console = read(out / "qbox-primary-console.log")
                if "Kernel panic - not syncing" in console:
                    raise RuntimeError("guest kernel panic")
                if "NEXIOS_BSP_INITRAMFS_READY" in console and "nexios-bsp#" in console:
                    break
                time.sleep(.5)
            else:
                raise TimeoutError("BSP readiness deadline expired")
            time.sleep(args.settle)
            pid = owned_native(out, launcher)
            if pid is None:
                raise RuntimeError("owned QBox process missing")
            launch = json.loads((out / "board-launch.json").read_text())
            manifest = {"run_id": args.name, "monitor": launch["monitor"],
                        "domains": launch["monitor"]["domains"]}
            collector = QBoxMonitorCollector(manifest, timeout=5)
            diagnostics = QBoxDiagnostics(collector, timeout=5)
            cpus = {d["domain_id"]: diagnostics.query(d["domain_id"], "query-cpus-fast")
                    for d in manifest["domains"]}
            tids = {name: [cpu["thread-id"] for cpu in response["result"]]
                    for name, response in cpus.items()}
            flat = [tid for group in tids.values() for tid in group]
            if not tids.get("si-cl0") or len(set(flat)) != len(flat):
                raise RuntimeError("missing or ambiguous domain vCPU identities")
            record.update(manifest=manifest, qmp_cpus=cpus,
                          clock_ticks_per_second=os.sysconf("SC_CLK_TCK"))
            for index in range(args.windows):
                sim_before = collector._get("/sc_time")
                before = host_snapshot(pid)
                time.sleep(args.seconds)
                after = host_snapshot(pid)
                sim_after = collector._get("/sc_time")
                summary = summarize(before, after,
                                    sim_after["sc_time_stamp"] - sim_before["sc_time_stamp"],
                                    tids, record["clock_ticks_per_second"])
                record["windows"].append(dict(summary=summary, host_before=before,
                                               host_after=after, sim_before=sim_before,
                                               sim_after=sim_after))
                print(json.dumps({"window": index, **summary}), flush=True)
            if launcher.poll() is not None:
                raise RuntimeError("launcher exited during measurement")
        finally:
            record["runner_returncode"] = stop(out, launcher)
    result_path = out / "result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    record["boot_passed"] = result.get("passed", False)
    if record["runner_returncode"] != 0 or not record["boot_passed"]:
        raise RuntimeError("canonical boot validation failed; inspect result.json")
    record["status"] = "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--si-cl0-image", type=Path, required=True)
    parser.add_argument("--rse-flash", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seconds", type=positive, default=30)
    parser.add_argument("--windows", type=int, default=2)
    parser.add_argument("--settle", type=positive, default=20)
    parser.add_argument("--boot-timeout", type=positive, default=900)
    parser.add_argument("--monitor-port", type=int, default=18110)
    args = parser.parse_args()
    if args.windows < 1 or not 1 <= args.monitor_port <= 65535:
        parser.error("windows must be positive and monitor port must be 1..65535")
    for path in (args.si_cl0_image, args.rse_flash):
        if not path.is_file():
            parser.error(f"missing input: {path}")
    args.out_dir.mkdir(parents=True, exist_ok=False)
    record = dict(schema_version=1, name=args.name, status="FAIL", windows=[],
                  seconds=args.seconds, settle_seconds=args.settle,
                  notes=["100 percent is one host logical CPU, not physical SI utilization.",
                         "No guest or monitor commands inside measurement windows.",
                         "Normal PFDI and firmware background work remain enabled."])
    try:
        execute(args, record)
    except (Exception, KeyboardInterrupt) as exc:
        record["error"] = str(exc) or type(exc).__name__
        print(record["error"], flush=True)
    finally:
        (args.out_dir / "idle-load.json").write_text(json.dumps(record, indent=2) + "\n")
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

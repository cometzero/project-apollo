#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Boot and validate Apollo CL1 Zephyr benchmarks on standalone gem5."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time

from run_linux import ROOT, SOURCE, required, run, sha256, stop_requested


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--gem5", type=Path)
    p.add_argument("--elf", type=Path)
    p.add_argument("--out-dir", "--outdir", type=Path)
    p.add_argument("--cpu", choices=("atomic", "timing", "minor"), default="minor")
    p.add_argument("--clock", default="1GHz")
    p.add_argument("--sram-latency", default="20ns")
    p.add_argument("--tcm-latency", default="1ns")
    p.add_argument("--max-ticks", type=int, default=200_000_000_000)
    p.add_argument("--timeout", type=float, default=1200)
    p.add_argument("--roi-schedule", type=Path)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--session", default="apollo-gem5-zephyr")
    p.add_argument("--no-attach", action="store_true")
    p.add_argument("--direct", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true")
    return p


def resolve(args):
    deploy = (args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp").resolve()
    native = deploy.parent.parent / "gem5-native"
    binary = required(args.gem5 or native / "gem5.opt")
    metadata = native / "gem5-native.json"
    return {
        "gem5": str(binary),
        "elf": str(required(args.elf or deploy / "zephyr-si-cl1-bench.elf")),
        "configuration": str(required(SOURCE / "configs/zena_si_cl1/run.py")),
        "native_manifest": str(metadata) if metadata.is_file() and binary == (native / "gem5.opt").resolve() else None,
    }


def main():
    p = parser()
    args = p.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.max_ticks <= 0:
        p.error("timeout must be finite and positive; max-ticks must be positive")
    if args.roi_schedule:
        args.roi_schedule = required(args.roi_schedule)
    inputs = resolve(args)
    if args.dry_run:
        print(json.dumps(inputs, indent=2))
        return 0
    out = (args.out_dir or ROOT / "build/qbox-apollo-qvp/gem5-zephyr" / time.strftime("%Y%m%d-%H%M%S")).resolve()
    if out.exists():
        raise ValueError(f"output directory already exists: {out}")
    if not args.headless and not args.direct:
        if not shutil.which("tmux"):
            raise ValueError("tmux is required; use --headless otherwise")
        sys.path.insert(0, str(ROOT / "scripts/run"))
        from run_qbox_linux import start_tmux
        start_tmux(args, out, program="gem5 CL1", log_name="gem5.log", key_prefix="gem5-zephyr-",
                   console_command=[sys.executable, str(Path(__file__).resolve()),
                                    *sys.argv[1:], "--direct", "--out-dir", str(out)])
        return 0
    out.mkdir(parents=True, exist_ok=False)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    settings = {key: getattr(args, key) for key in
                ("cpu", "clock", "sram_latency", "tcm_latency", "max_ticks")}
    command = [inputs["gem5"], "--listener-mode=on", f"--outdir={out}",
               inputs["configuration"], "--elf", inputs["elf"], "--terminal-port", str(port)]
    for name, value in settings.items():
        command.extend(["--" + name.replace("_", "-"), str(value)])
    if args.roi_schedule:
        command.extend(["--roi-schedule", str(args.roi_schedule)])
    env = os.environ.copy()
    if inputs["native_manifest"]:
        metadata = json.loads(Path(inputs["native_manifest"]).read_text())
        env["LD_LIBRARY_PATH"] = os.pathsep.join(metadata["library_path"])
        env["PYTHONHOME"] = metadata["python_home"]
    manifest = {"command": command, "inputs": inputs, "configuration_args": settings,
                "elf_sha256": sha256(inputs["elf"]), "gem5_sha256": sha256(inputs["gem5"]),
                "configuration_sha256": sha256(inputs["configuration"]),
                "roi_schedule_sha256": sha256(args.roi_schedule) if args.roi_schedule else None,
                "limitations": "Experimental PMSA64; uncalibrated generic CPU timing; no silicon WCET qualification"}
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"gem5 CL1 output: {out}", flush=True)
    args.workload = "zephyr"
    rc, timed_out, elapsed = run(command, env, out, port, args)
    rc = 124 if timed_out else (128 - rc if rc < 0 else rc)
    manifest.update(returncode=rc, host_seconds=elapsed, timeout=timed_out)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if rc == 0:
        report = subprocess.run([sys.executable, str(Path(__file__).with_name("report_si_cl1.py")),
                                 str(out / "system.platform.terminal"), "--backend", "gem5",
                                 "--gem5-dir", str(out), "--output", str(out / "report")], check=False)
        rc = report.returncode
    result = {"status": "PASS" if rc == 0 else "FAIL", "returncode": rc,
              "timeout": timed_out, "host_seconds": elapsed}
    if rc == 0:
        metrics = json.loads((out / "report/metrics.json").read_text())
        result.update(schedulability_status=metrics["schedulability_status"],
                      qualification=metrics["qualification"])
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(out), **result}, indent=2))
    return rc


if __name__ == "__main__":
    signal.signal(signal.SIGHUP, stop_requested)
    signal.signal(signal.SIGTERM, stop_requested)
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"gem5 Zephyr launcher: {exc}")
    except KeyboardInterrupt:
        sys.exit(130)

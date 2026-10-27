#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Boot the integrated Apollo CL1 Zephyr image or run explicit benchmarks."""

import argparse
import json
import math
import os
import re
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time

from run_linux import ROOT, SOURCE, required, run, sha256, stop_requested

sys.path.insert(0, str(ROOT / "scripts/run"))
from run_qbox_zephyr import boot_complete
from run_qbox_apollo_fvp_full import si_cl1_boot_config


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--gem5", type=Path)
    p.add_argument("--elf", type=Path)
    p.add_argument("--image", type=Path, help="matching CRC-patched integrated Zephyr binary")
    p.add_argument("--mode", choices=("integrated", "benchmark"), default="integrated")
    p.add_argument("--exit-after-pass", action="store_true", help="stop after integrated four-core boot and shell")
    p.add_argument("--out-dir", "--outdir", type=Path)
    p.add_argument("--cpu", choices=("atomic", "timing", "minor"), help="default atomic for integrated boot, minor for benchmarks")
    p.add_argument("--clock", default="1GHz")
    p.add_argument("--sram-latency", default="20ns")
    p.add_argument("--tcm-latency", default="1ns")
    p.add_argument("--max-ticks", type=int, help="simulation tick limit; 0 is unlimited in integrated mode")
    p.add_argument("--timeout", type=float, help="host seconds; default 1200 headless/benchmark, 0 interactive boot")
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
    elf = required(args.elf or deploy / (
        "zephyr-demos-cl1.elf" if args.mode == "integrated" else "zephyr-si-cl1-bench.elf"))
    image = required(args.image or elf.with_suffix(".bin")) if args.mode == "integrated" else None
    boot = si_cl1_boot_config(argparse.Namespace(platform_param=[]), {
        "si_cl1_symbols": elf, "si_cl1_image": image}) if image else None
    return {
        "gem5": str(binary),
        "elf": str(elf), "image": str(image) if image else None, "boot": boot,
        "configuration": str(required(SOURCE / "configs/zena_si_cl1/run.py")),
        "native_manifest": str(metadata) if metadata.is_file() and binary == (native / "gem5.opt").resolve() else None,
    }


def main():
    p = parser()
    args = p.parse_args()
    integrated = args.mode == "integrated"
    if args.cpu is None:
        args.cpu = "atomic" if integrated else "minor"
    if args.timeout is None:
        args.timeout = 1200 if args.headless or not integrated else 0
    if args.max_ticks is None:
        args.max_ticks = 0 if integrated else 200_000_000_000
    if (not math.isfinite(args.timeout) or args.timeout < 0 or args.max_ticks < 0
            or (not integrated and (args.timeout == 0 or args.max_ticks == 0))):
        p.error("timeout and max-ticks must be nonnegative (positive for benchmark)")
    if integrated and args.roi_schedule:
        p.error("--roi-schedule requires --mode benchmark")
    if not integrated and (args.image or args.exit_after_pass):
        p.error("--image and --exit-after-pass require --mode integrated")
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
                ("mode", "cpu", "clock", "sram_latency", "tcm_latency", "max_ticks")}
    command = [inputs["gem5"], "--listener-mode=on", f"--outdir={out}",
               inputs["configuration"], "--elf", inputs["elf"], "--terminal-port", str(port)]
    for name, value in settings.items():
        command.extend(["--" + name.replace("_", "-"), str(value)])
    if inputs["image"]:
        command.extend(["--image", inputs["image"]])
    if args.roi_schedule:
        command.extend(["--roi-schedule", str(args.roi_schedule)])
    env = os.environ.copy()
    if inputs["native_manifest"]:
        metadata = json.loads(Path(inputs["native_manifest"]).read_text())
        env["LD_LIBRARY_PATH"] = os.pathsep.join(metadata["library_path"])
        env["PYTHONHOME"] = metadata["python_home"]
    manifest = {"command": command, "inputs": inputs, "configuration_args": settings,
                "elf_sha256": sha256(inputs["elf"]), "gem5_sha256": sha256(inputs["gem5"]),
                "image_sha256": sha256(inputs["image"]) if inputs["image"] else None,
                "mode": args.mode,
                "configuration_sha256": sha256(inputs["configuration"]),
                "roi_schedule_sha256": sha256(args.roi_schedule) if args.roi_schedule else None,
                "limitations": "Experimental PMSA64; uncalibrated generic CPU timing; no silicon WCET qualification"}
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"gem5 CL1 output: {out}", flush=True)
    args.workload = "zephyr"
    stopped_after_boot = False
    def stop_integrated():
        nonlocal stopped_after_boot
        terminal = out / "system.platform.terminal"
        serial = terminal.read_bytes() if terminal.exists() else b""
        if re.search(rb"ZEPHYR FATAL ERROR|ASSERTION FAIL|Kernel panic", serial):
            return True
        if args.exit_after_pass and boot_complete(serial):
            stopped_after_boot = True
            return True
        return False
    if integrated:
        rc, timed_out, elapsed = run(command, env, out, port, args, stop_when=stop_integrated)
    else:
        rc, timed_out, elapsed = run(command, env, out, port, args)
    native_rc = rc
    rc = 124 if timed_out else (128 - rc if rc < 0 else rc)
    manifest.update(returncode=rc, host_seconds=elapsed, timeout=timed_out)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if not integrated and rc == 0:
        report = subprocess.run([sys.executable, str(Path(__file__).with_name("report_si_cl1.py")),
                                 str(out / "system.platform.terminal"), "--backend", "gem5",
                                 "--gem5-dir", str(out), "--output", str(out / "report")], check=False)
        rc = report.returncode
    if integrated:
        terminal = out / "system.platform.terminal"
        serial = terminal.read_bytes() if terminal.exists() else b""
        fatal = bool(re.search(rb"ZEPHYR FATAL ERROR|ASSERTION FAIL|Kernel panic", serial))
        passed = (stopped_after_boot and native_rc in (0, -signal.SIGTERM)
                  and not timed_out and boot_complete(serial) and not fatal)
        # A simulation limit or host timeout is not successful bounded boot.
        rc = 0 if passed else (rc or 1)
    result = {"status": "PASS" if rc == 0 else "FAIL", "returncode": rc,
              "native_returncode": native_rc, "mode": args.mode,
              "timeout": timed_out, "host_seconds": elapsed}
    if integrated:
        result.update(boot_marker_observed=boot_complete(serial),
                      stopped_after_boot=stopped_after_boot,
                      qualification="MODEL_BOOT_ONLY",
                      scope="Integrated image; synthetic PFDI SCMI; no AP/RSE/SCP peers")
    if not integrated and rc == 0:
        metrics = json.loads((out / "report/metrics.json").read_text())
        result.update(schedulability_status=metrics["schedulability_status"],
                      qualification=metrics["qualification"])
    manifest.update(returncode=rc, native_returncode=native_rc,
                    stopped_after_boot=stopped_after_boot)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
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

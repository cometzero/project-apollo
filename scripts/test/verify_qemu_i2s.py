#!/usr/bin/env python3
"""Qualify standalone Apollo I2S with the existing QBox PCM comparison workload."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
GUEST_TEST = ROOT / "scripts/test/verify_qbox_i2s.sh"


def interrupt_counts(text: str) -> dict[str, int]:
    """Sum per-CPU counters using the GIC hardware INTID, not Linux IRQ numbers."""
    counts = {}
    for line in text.splitlines():
        match = re.match(r"\s*\d+:\s+((?:\d+\s+)+)GICv3\s+(\d+)\s", line)
        if match:
            counts[match[2]] = sum(map(int, match[1].split()))
    return counts


def assess(text: str, mode: str) -> dict:
    text = text.replace("\r", "")
    snapshots = {}
    for name in ("BEFORE", "AFTER"):
        match = re.search(rf"^QEMU_I2S_IRQ_{name}\n(.*?)^QEMU_I2S_IRQ_END$",
                          text, re.MULTILINE | re.DOTALL)
        snapshots[name] = interrupt_counts(match[1]) if match else {}
    deltas = {irq: count - snapshots["BEFORE"].get(irq, 0)
              for irq, count in snapshots["AFTER"].items()}
    passes = re.findall(r"^I2S_LOOPBACK_PASS playback=(\S+) capture=(\S+) "
                        r"frames=65536 bytes=262144 format=S16_LE rate=48000 idle=\d+$",
                        text, re.MULTILINE)
    # Each cross-wired direction must complete both alone and during duplex.
    directions = {pair: passes.count(pair) for pair in set(passes)}
    pcm_pass = len(passes) == 4 and len(directions) == 2 and all(
        count == 2 and pair[0] != pair[1] for pair, count in directions.items())
    required_irqs = ("390",) if mode == "dma" else ("388", "389")
    irq_pass = all(irq in snapshots["BEFORE"] and deltas.get(irq, 0) > 0
                   for irq in required_irqs)
    completed = bool(re.search(r"^QEMU_I2S_DONE=0$", text, re.MULTILINE))
    driver_pass = bool(re.search(rf"^I2S_DRIVER_TEST_PASS mode={mode}$", text, re.MULTILINE))
    return {"status": "PASS" if completed and driver_pass and pcm_pass and irq_pass else "FAIL",
            "mode": mode, "guest_completed": completed, "driver_pass": driver_pass,
            "pcm_sequence_comparison": "PASS" if pcm_pass else "FAIL",
            "pcm_pass_count": len(passes), "interrupt_progress": "PASS" if irq_pass else "FAIL",
            "interrupts_before": snapshots["BEFORE"], "interrupts_after": snapshots["AFTER"],
            "interrupt_deltas": deltas,
            "qualification": "S16_LE stereo 48 kHz, both directions and simultaneous duplex; "
                             "functional sample comparison, not physical I2S or timing parity"}


def guest_command() -> bytes:
    payload = base64.b64encode(GUEST_TEST.read_bytes()).decode()
    command = (
        f"printf '%s' '{payload}' | base64 -d > /tmp/verify-qemu-i2s.sh; "
        "printf 'QEMU_I2S_DTB_%s\\n' BEGIN; base64 /sys/firmware/fdt; "
        "printf 'QEMU_I2S_DTB_%s\\n' END; "
        "printf 'QEMU_I2S_IRQ_%s\\n' BEFORE; cat /proc/interrupts; "
        "printf 'QEMU_I2S_IRQ_%s\\n' END; "
        "sha256sum /tmp/verify-qemu-i2s.sh /usr/bin/i2s-loopback; "
        "sh /tmp/verify-qemu-i2s.sh; rc=$?; "
        "printf 'QEMU_I2S_IRQ_%s\\n' AFTER; cat /proc/interrupts; "
        "printf 'QEMU_I2S_IRQ_%s\\n' END; "
        "printf 'QEMU_I2S_DONE=%s\\n' \"$rc\"\n"
    )
    return command.encode()


def run_mode(args: argparse.Namespace, mode: str, output: Path) -> dict:
    out = output / mode
    provider = args.provider or ROOT / "build/tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json"
    executable = args.qemu or Path(json.loads(provider.read_text())["executable"])
    with executable.open("rb") as binary:
        executable_sha256 = hashlib.file_digest(binary, "sha256").hexdigest()
    command = [str(ROOT / "run_qemu_linux.sh"), "--bsp", "--headless",
               "--i2s-mode", mode, "--netdev", "user,id=net0", "--out-dir", str(out),
               "--timeout", str(args.timeout)]
    for option in ("qemu", "provider", "deploy_dir", "kernel", "initrd", "rootfs"):
        if value := getattr(args, option):
            command += ["--" + option.replace("_", "-"), str(value)]
    started = time.monotonic()
    sent = False
    with (output / f"{mode}-launcher.log").open("wb") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        try:
            while process.poll() is None and time.monotonic() - started < args.timeout + 10:
                uart = out / "linux-uart.log"
                text = uart.read_text(errors="replace") if uart.exists() else ""
                if not sent and re.search(r"nexios-bsp(?:-failed)?#\s*$", text):
                    with (out / "linux-uart.in").open("ab") as stream:
                        stream.write(guest_command())
                    sent = True
                if re.search(r"(?:^|\n)QEMU_I2S_DONE=\d+\r?\n", text):
                    break
                time.sleep(0.2)
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    uart = out / "linux-uart.log"
    text = uart.read_text(errors="replace") if uart.exists() else ""
    result = assess(text, mode)
    result.update(command=command, guest_test_sent=sent, elapsed_seconds=time.monotonic() - started,
                  uart_sha256=hashlib.sha256(uart.read_bytes()).hexdigest() if uart.exists() else None,
                  guest_script_sha256=hashlib.sha256(GUEST_TEST.read_bytes()).hexdigest())
    dtb_match = re.search(r"^QEMU_I2S_DTB_BEGIN\n(.*?)^QEMU_I2S_DTB_END$",
                          text.replace("\r", ""), re.MULTILINE | re.DOTALL)
    if dtb_match:
        try:
            dtb = base64.b64decode("".join(dtb_match[1].split()), validate=True)
            if dtb[:4] != bytes.fromhex("d00dfeed"):
                raise ValueError("guest DTB has no FDT magic")
            (out / "live.dtb").write_bytes(dtb)
            result["live_dtb"] = str(out / "live.dtb")
            result["live_dtb_sha256"] = hashlib.sha256(dtb).hexdigest()
        except ValueError as error:
            result["live_dtb_error"] = str(error)
    if "live_dtb" not in result:
        result["status"] = "FAIL"
        result.setdefault("live_dtb_error", "guest DTB snapshot not observed")
    launch = out / "launch.json"
    if launch.exists():
        plan = json.loads(launch.read_text())
        result["artifact_sha256"] = {}
        for name, path in (("qemu", plan["command"][0]), ("kernel", plan["kernel"]),
                           ("initrd", plan["initrd"]), ("source_rootfs", plan["source_rootfs"])):
            if path:
                if name == "qemu":
                    result["artifact_sha256"][name] = executable_sha256
                    continue
                with Path(path).open("rb") as source:
                    result["artifact_sha256"][name] = hashlib.file_digest(source, "sha256").hexdigest()
        result["artifact_paths"] = {"qemu": plan["command"][0], "kernel": plan["kernel"],
                                    "initrd": plan["initrd"], "source_rootfs": plan["source_rootfs"]}
    (output / f"{mode}-result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dma", "pio", "both"), default="both")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "build/qbox-apollo-qvp" /
                        ("qemu-i2s-" + time.strftime("%Y%m%d-%H%M%S")))
    parser.add_argument("--timeout", type=float, default=900)
    for option in ("qemu", "provider", "deploy-dir", "kernel", "initrd", "rootfs"):
        parser.add_argument("--" + option, type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    output = args.out_dir.absolute()
    output.mkdir(parents=True, exist_ok=False)
    modes = ("dma", "pio") if args.mode == "both" else (args.mode,)
    results = [run_mode(args, mode, output) for mode in modes]
    summary = {"status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL",
               "results": results}
    (output / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

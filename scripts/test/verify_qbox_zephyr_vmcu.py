#!/usr/bin/env python3
"""Exercise the TC397 shell, existing SI0 PFDI safety reports and board GPIO."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
TMUX_RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def read(path):
    return ANSI.sub("", path.read_text(errors="replace")).replace("\r", "") if path.exists() else ""


def wait_for(path, pattern, offset=0, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        text = read(path)
        match = re.search(pattern, text[offset:])
        if match:
            return match.group()
        time.sleep(.1)
    raise TimeoutError(f"{path.name}: missing {pattern!r}")


def tmux(*args):
    return subprocess.check_output(["tmux", *args], text=True).strip()


def execute(args, result):
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    session = f"apollo-qbox-zephyr-vmcu-{os.getpid()}"
    command = [str(ROOT / "run_qbox_yocto.sh"), "--bsp", "--no-attach",
               "--multi-session", "--copy-disks", "--no-persistent-rse-state",
               "--session", session, "--out-dir", str(out),
               "--timeout", str(args.timeout)]
    result.update(command=command, session=session, checks={})
    env = dict(os.environ, LINES="60", COLUMNS="180")
    env.pop("QBOX_APOLLO_VMCU_UART_ENDPOINT", None)
    started = False
    with (out / "launcher.log").open("w") as log:
        try:
            started = True
            subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=45)
            uart = out / "tc397-uart.log"
            wait_for(uart, "VMCU_INIT result=PASS", timeout=30)
            result["checks"]["zephyr-app-boot"] = "PASS"
            wait_for(out / "qbox-primary-console.log", "NEXIOS_BSP_INITRAMFS_READY",
                     timeout=args.timeout)
            wait_for(uart, r"VMCU_STATE source=SI0_PFDI state=RUN fault=NONE[^\n]*\n", timeout=60)
            wait_for(out / "qbox-safety-island-cl0.log", r"\[VMCU_SAFETY\] INIT[^\n]*source=PFDI", timeout=5)
            result["checks"]["si0-pfdi-report-and-soc-error"] = "PASS"
            rows = tmux("list-panes", "-t", f"{session}:qbox", "-F",
                        "#{pane_id} #{pane_title}").splitlines()
            pane = next((row.split()[0] for row in rows if row.endswith(" tc397")), None)
            if pane is None:
                raise RuntimeError("TC397 shell pane missing")
            (out / "panes.txt").write_text("\n".join(rows) + "\n")

            def cli(command, response):
                offset = len(read(uart))
                tmux("send-keys", "-t", pane, "-l", command)
                tmux("send-keys", "-t", pane, "Enter")
                observed = wait_for(uart, response + r"\n", offset)
                result["checks"][command] = {"status": "PASS", "response": observed}
                return offset

            # Observe a quiet healthy interval. No host-side decoder is a monitor.
            before = read(uart)
            time.sleep(2)
            assert read(uart) == before, "healthy console emitted unsolicited output"
            assert "[host +" not in before and "type=STATUS" not in before
            result["checks"]["quiet-healthy-console"] = "PASS"
            cli("vmcu-cli status", r"VMCU_STATUS source=SI0_PFDI state=RUN fault=NONE[^\n]*")
            cli("vmcu-cli apollo ping", r"VMCU_RPC peer=AP operation=1[^\n]*result=OK[^\n]*")
            cli("vmcu-cli apollo status", r"VMCU_RPC peer=AP operation=2[^\n]*result=OK[^\n]*")
            cli("vmcu-cli safety ping", r"VMCU_RPC peer=SI0 operation=1[^\n]*result=OK[^\n]*")
            cli("vmcu-cli safety status", r"VMCU_RPC peer=SI0 operation=2[^\n]*result=OK[^\n]*")
            cli("vmcu-cli gpio status", r"VMCU_GPIO[^\n]*IST_DONE_N=1 SOC_RESET_N=1 MCU_SOC_WAKE=0")
            cli("vmcu-cli gpio wake on", r"VMCU_GPIO wake on[^\n]*")
            time.sleep(.3)
            cli("vmcu-cli safety gpio", r"VMCU_RPC peer=SI0 operation=6[^\n]*result=OK value=0x0000001[cd]")
            cli("vmcu-cli gpio wake off", r"VMCU_GPIO wake off[^\n]*")
            time.sleep(.3)
            cli("vmcu-cli safety gpio", r"VMCU_RPC peer=SI0 operation=6[^\n]*result=OK value=0x0000000[cd]")
            result["checks"]["gpio-bidirectional-and-safe-defaults"] = "PASS"
            # AP management service loss must not change the SI0 PFDI decision.
            primary = out / "qbox-primary-console.log"
            def ap(command, marker):
                offset = len(read(primary))
                fd = os.open(out / "primary-uart-input.fifo", os.O_WRONLY | os.O_NONBLOCK)
                try:
                    os.write(fd, (command + "\n").encode())
                finally:
                    os.close(fd)
                return wait_for(primary, marker, offset, timeout=10)
            ap("kill $(cat /run/vmcu-ap.pid); echo AP_MANAGEMENT_STOPPED", r"\nAP_MANAGEMENT_STOPPED")
            samples = []
            for _ in range(3):
                time.sleep(6)
                mark = cli("vmcu-cli status", r"VMCU_STATUS source=SI0_PFDI state=RUN fault=NONE[^\n]*")
                line = wait_for(uart, r"VMCU_STATUS[^\n]*", mark)
                fields = dict(re.findall(r"(sequence|interval_ms|gpio_edges)=(\d+)", line))
                samples.append({key: int(value) for key, value in fields.items()})
            assert all(4000 <= item["interval_ms"] <= 8000 for item in samples), samples
            assert samples[-1]["sequence"] > samples[0]["sequence"], samples
            assert samples[-1]["gpio_edges"] > samples[0]["gpio_edges"], samples
            result["checks"]["5-second-reports-independent-of-ap-management"] = samples
            mark = cli("vmcu-cli heartbeat off", r"VMCU_RPC peer=SI0 operation=3[^\n]*result=OK value=0x00000000")
            wait_for(uart, "VMCU_STATE source=SI0_PFDI state=DEGRADED fault=LINK_TIMEOUT", mark, timeout=22)
            mark = cli("vmcu-cli heartbeat on", r"VMCU_RPC peer=SI0 operation=3[^\n]*result=OK value=0x00000001")
            wait_for(uart, r"VMCU_STATE source=SI0_PFDI state=RUN fault=NONE[^\n]*\n", mark, timeout=10)
            result["checks"]["safety-uart-timeout-recovery"] = "PASS"
            cli("vmcu-cli workload stall", r"VMCU_RPC result=UNSUPPORTED[^\n]*")
            if args.inject_pfdi_timeout:
                # Exercise the existing real PFDI online watchdog, without shortening it.
                assert "PFDI monitor timeout" not in read(out / "qbox-safety-island-cl0.log")
                mark = len(read(uart))
                ap("kill -STOP $(pidof pfdi-sample-app); echo PFDI_AGENT_STOPPED", r"\nPFDI_AGENT_STOPPED")
                result["injected_pfdi_timeout"] = True
                wait_for(uart, r"VMCU_STATE source=SI0_PFDI state=DEGRADED fault=PFDI_FAULT[^\n]*pfdi_fault=0x[0-9a-f]*[1-9a-f][0-9a-f]*", mark, timeout=80)
                cli("vmcu-cli status", r"VMCU_STATUS source=SI0_PFDI state=DEGRADED fault=PFDI_FAULT[^\n]*")
                ap("kill -CONT $(pidof pfdi-sample-app); echo PFDI_AGENT_RESUMED", r"\nPFDI_AGENT_RESUMED")
                time.sleep(6)
                cli("vmcu-cli status", r"VMCU_STATUS source=SI0_PFDI state=DEGRADED fault=PFDI_FAULT[^\n]*")
                result["checks"]["existing-pfdi-timeout-and-latched-fault"] = "PASS"
            # Explicit reset is deliberately last: UART/GPIO health above must
            # remain observable even while the AP reset output is asserted.
            cli("vmcu-cli gpio reset assert", r"VMCU_GPIO reset assert output=0x0000")
            time.sleep(.3)
            cli("vmcu-cli safety gpio", r"VMCU_RPC peer=SI0 operation=6[^\n]*result=OK value=0x0000000[45]")
            cli("vmcu-cli gpio reset release", r"VMCU_GPIO reset release output=0x0008")
            time.sleep(.3)
            cli("vmcu-cli safety gpio", r"VMCU_RPC peer=SI0 operation=6[^\n]*result=OK value=0x0000000[cd]")
            result["checks"]["explicit-reset-wire-and-si0-survival"] = "PASS"
            (out / "tc397-pane.txt").write_text(tmux("capture-pane", "-p", "-S", "-200", "-t", pane))
            result["status"] = "PASS"
        finally:
            if started:
                cleanup = subprocess.run([str(TMUX_RUNNER), "--stop-session", session],
                                         cwd=ROOT, env=dict(os.environ, OUT_DIR=str(out)),
                                         stdout=log, stderr=subprocess.STDOUT, timeout=45)
                result["stop_returncode"] = cleanup.returncode
                status_file = out / "tc397-status.json"
                if status_file.exists():
                    result["companion"] = json.loads(status_file.read_text())
                    receipts = result["companion"].get("cleanup", [])
                    if not receipts or any(item["status"] != "PASS" for item in receipts):
                        raise RuntimeError("TC397 cleanup incomplete")
                if cleanup.returncode:
                    raise RuntimeError("tmux session cleanup failed")
                if result["status"] == "PASS":
                    boot_file = out / "result.json"
                    if not boot_file.exists():
                        raise RuntimeError("QBox runner result missing")
                    result["boot"] = json.loads(boot_file.read_text())
                    validate_boot_result(result["boot"], result.get("injected_pfdi_timeout", False))
                    if result.get("injected_pfdi_timeout"):
                        result["expected_runner_blocker"] = "si_error:pfdi_monitor_timeout"


def validate_boot_result(boot, injected):
    """Keep canonical failure intact; allow only the fault this test injected."""
    if not injected:
        if not boot.get("passed"):
            raise RuntimeError("QBox runner did not pass boot checks")
        return
    child = boot.get("child_status", {})
    hits = {key for key, value in boot.get("si_error_hits", {}).items() if value}
    groups = boot.get("marker_groups", {})
    markers_pass = bool(groups) and all(
        bool(group) and all(value is True for value in group.values())
        for group in groups.values())
    if (boot.get("blocker") != "si_error:pfdi_monitor_timeout" or
            boot.get("completion_gate_blocker") != "si_error:pfdi_monitor_timeout" or
            hits != {"pfdi_monitor_timeout"} or not markers_pass or
            boot.get("assertions") or boot.get("first_failing_marker") or
            child.get("blocker") or any(child.get("fail_patterns", {}).values())):
        raise RuntimeError("unexpected failure beyond the injected PFDI timeout")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--inject-pfdi-timeout", action="store_true",
                        help="Stop the real PFDI agent; retain the expected canonical failure")
    args = parser.parse_args()
    if args.out_dir.exists() or args.timeout <= 0:
        parser.error("a new output directory and positive timeout are required")
    result = {"status": "FAIL", "scope": "SI0 existing PFDI, 5-second safety UART, TC397 Zephyr and board GPIO",
              "not_evaluated": ["AP recovery", "PMIC power sequencing", "SC7", "CAN", "physical timing"]}
    started = time.monotonic()
    try:
        execute(args, result)
    except (OSError, ValueError, AssertionError, RuntimeError, subprocess.SubprocessError) as error:
        result.update(status="FAIL", error=str(error))
    result["elapsed_seconds"] = time.monotonic() - started
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, path in (("firmware", ROOT / "build/qbox-apollo-qvp/zephyr-vmcu/app/zephyr/zephyr.elf"),
                       ("runner", Path(__file__))):
        if path.exists():
            with path.open("rb") as stream:
                result[name + "_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    (args.out_dir / "vmcu-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "error": result.get("error"),
                      "result": str((args.out_dir / "vmcu-result.json").resolve())}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

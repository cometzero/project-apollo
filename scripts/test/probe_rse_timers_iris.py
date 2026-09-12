#!/usr/bin/env python3
"""Observe booted TF-M timer state and exercise unused RSE timers via Iris.

Run only against a disposable, paused FVP instance. IRQ delivery stays disabled
in the NVIC; this tests timer expiry and pending, not TF-M ISR execution.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "debug"))
import local_debug_iris


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--boot-seconds", type=float, default=75)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = local_debug_iris.load_manifest(args.manifest)
    local_debug_iris.add_iris_python(manifest)
    from iris.debug import Model
    model = Model.NewNetworkModel("localhost", args.port, synchronous=False)
    target = local_debug_iris.resolve_target(model, manifest["components"]["tfm-s"]["target"])
    result = {"manifest": str(args.manifest), "tests": [], "samples": []}

    def read(addr):
        return int.from_bytes(target.read_memory(addr, memory_space="SP", size=4, count=1), "little")

    def write(addr, value):
        target.write_memory(addr, value, memory_space="SP", size=4, count=1)

    def advance(seconds):
        model.run(blocking=False, timeout=30)
        time.sleep(seconds)
        model.stop(timeout=30)

    def snapshot():
        timers = []
        for i in range(4):
            base = 0x58000000 + i * 0x1000
            timers.append({"base": hex(base), "count": read(base) | read(base + 4) << 32,
                           "freq": read(base + 0x10), "control": read(base + 0x2c),
                           "cval": read(base + 0x20) | read(base + 0x24) << 32})
        return {"simulation_time": model.client.irisCall().simulationTime_get(instId=1),
                "pc": target.get_pc(), "timers": timers,
                "systick_ctrl": read(0xe000e010), "systick_load": read(0xe000e014),
                "systick_value": read(0xe000e018), "nvic_enable": read(0xe000e100),
                "nvic_pending": read(0xe000e200)}

    try:
        model.stop(timeout=30)
        advance(args.boot_seconds)
        result["samples"].append(snapshot())
        original = result["samples"][0]
        if original["systick_ctrl"] & 1:
            result["systick_reload_test"] = {"status": "SKIP", "reason": "in use"}
        else:
            try:
                write(0xe000e014, 999)
                observed = read(0xe000e014)
                result["systick_reload_test"] = {
                    "status": "PASS" if observed == 999 else "FAIL",
                    "written": 999, "observed": observed}
            finally:
                write(0xe000e014, original["systick_load"])
        advance(0.2)
        result["samples"].append(snapshot())
        for i, irq in enumerate((3, 4, 5, 27)):
            base = 0x58000000 + i * 0x1000
            initial = result["samples"][1]["timers"][i]
            if initial["control"] & 1 or read(0xe000e100) & (1 << irq):
                result["tests"].append({"timer": i, "status": "SKIP", "reason": "timer or NVIC IRQ in use"})
                continue
            try:
                write(0xe000e280, 1 << irq)
                write(base + 0x28, 125000)
                write(base + 0x2c, 1)
                advance(0.2)
                expired = read(base + 0x2c)
                pending = read(0xe000e200)
                write(base + 0x2c, 0)
                write(0xe000e280, 1 << irq)
                cleared = read(0xe000e200)
                passed = bool(expired & 4 and pending & (1 << irq) and not cleared & (1 << irq))
                result["tests"].append({"timer": i, "status": "PASS" if passed else "FAIL",
                                        "expired_control": expired, "pending": pending, "cleared": cleared})
            finally:
                write(base + 0x2c, 0)
                write(base + 0x20, initial["cval"] & 0xffffffff)
                write(base + 0x24, initial["cval"] >> 32)
                write(base + 0x2c, initial["control"] & 3)
                write(0xe000e280, 1 << irq)
        result["counter_progress"] = all(b["count"] > a["count"] for a, b in
                zip(result["samples"][0]["timers"], result["samples"][1]["timers"]))
        result["timer_irq_passed"] = all(t["status"] == "PASS" for t in result["tests"])
        result["passed"] = result["counter_progress"] and result["timer_irq_passed"] and result["systick_reload_test"]["status"] == "PASS"
    except Exception as error:
        result["error"] = repr(error)
        result["traceback"] = traceback.format_exc()
        result["passed"] = False
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        model.release()
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())

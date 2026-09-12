"""GDB Python probe for a disposable QVP after normal TF-M boot.

Load with `source` after connecting RSE GDB. Set RSE_TIMER_RESULT to a JSON
output path. Tests use an already-expired comparator with NVIC IRQ disabled;
they do not execute a firmware timer ISR or measure interrupt latency.
"""
import json
import os
from pathlib import Path
import gdb


def main():
    inferior = gdb.selected_inferior()
    def read(address):
        return int.from_bytes(inferior.read_memory(address, 4), "little")
    def write(address, value):
        inferior.write_memory(address, value.to_bytes(4, "little"))
    result = {"pc": int(gdb.parse_and_eval("$pc")), "tests": [], "timers": [],
              "systick_ctrl": read(0xe000e010), "systick_load": read(0xe000e014),
              "systick_value": read(0xe000e018), "nvic_enable": read(0xe000e100),
              "nvic_pending": read(0xe000e200)}
    if result["systick_ctrl"] & 1:
        result["systick_reload_test"] = {"status": "SKIP", "reason": "in use"}
    else:
        try:
            write(0xe000e014, 999)
            observed = read(0xe000e014)
            result["systick_reload_test"] = {
                "status": "PASS" if observed == 999 else "FAIL",
                "written": 999, "observed": observed}
        finally:
            write(0xe000e014, result["systick_load"])
    for i, irq in enumerate((3, 4, 5, 27)):
        base = 0x58000000 + i * 0x1000
        initial = {"base": hex(base), "control": read(base + 0x2c),
                   "cval_low": read(base + 0x20), "cval_high": read(base + 0x24),
                   "count": read(base) | read(base + 4) << 32, "freq": read(base + 0x10)}
        result["timers"].append(initial)
        if initial["control"] & 1 or result["nvic_enable"] & (1 << irq):
            result["tests"].append({"timer": i, "status": "SKIP", "reason": "in use"})
            continue
        try:
            write(0xe000e280, 1 << irq)
            write(base + 0x20, 0)
            write(base + 0x24, 0)
            write(base + 0x2c, 1)
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
            write(base + 0x20, initial["cval_low"])
            write(base + 0x24, initial["cval_high"])
            write(base + 0x2c, initial["control"] & 3)
            write(0xe000e280, 1 << irq)
    result["timer_irq_passed"] = all(t["status"] == "PASS" for t in result["tests"])
    result["passed"] = result["timer_irq_passed"] and result["systick_reload_test"]["status"] == "PASS"
    Path(os.environ["RSE_TIMER_RESULT"]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise gdb.GdbError("RSE timer probe failed; see JSON")


main()

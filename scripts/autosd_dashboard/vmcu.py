"""Typed Zephyr console/CAN operations. A single caller owns the command queue."""
import json
import socket
import struct
import time

from board_io import fields, fifo_write, load, position, records, wait_match
from qbox_monitor import process_identity


class UnknownOutcome(RuntimeError):
    """A mutation may have reached firmware; it must not be retried automatically."""


class Vmcu:
    def __init__(self, directory, stopped=lambda: False):
        self.directory = directory
        self.log = directory / "tc397-uart.log"
        self.primary = directory / "qbox-primary-console.log"
        self.stopped = stopped

    def cli(self, command, pattern, timeout=15):
        mark = position(self.log)
        fifo_write(self.directory / "tc397-uart-input.fifo", "vmcu-cli " + command + "\n")
        try:
            return wait_match(self.log, pattern + r"[^\n]*\n", mark, timeout, self.stopped).strip()
        except TimeoutError as error:
            raise UnknownOutcome(str(error)) from error

    def rpc(self, command, peer, operation, timeout=15):
        line = self.cli(command, rf"VMCU_RPC peer={peer} operation={operation}\b", timeout)
        value = fields(line)
        if value.get("result") != "OK":
            raise RuntimeError(line)
        return value

    def status(self):
        value = fields(self.cli("status", r"VMCU_STATUS source=SI0_PFDI"))
        value["gpio"] = fields(self.cli("gpio status", "VMCU_GPIO in="))
        value["observed_monotonic"] = time.monotonic()
        return value

    def telemetry(self):
        for item in reversed(records(self.directory / "vehicle-can.jsonl")):
            try:
                data = bytes.fromhex(item.get("data", ""))
                if item.get("event") == "silkit_rx" and item.get("id") == 0x510 and len(data) == 32:
                    return {"state": data[1], "fault": data[2], "gpio": data[3],
                            "epoch": struct.unpack_from("<I", data, 4)[0],
                            "cookie": struct.unpack_from("<I", data, 8)[0], "event": item}
            except (ValueError, KeyError):
                pass
        return {}

    def pmic(self):
        rails = []
        for index in range(9):
            raw = int(self.rpc(f"pmic rail {index}", "SI0", 8)["value"], 0)
            rails.append({"index": index, "enabled": bool(raw >> 31), "programmed_uv": raw & 0x7fffffff})
        return {"rails": rails, "live_stat": [int(self.rpc(f"pmic fault {i}", "SI0", 9)["value"], 0)
                                                 for i in range(11)],
                "owner": "SI_CL0", "scope": "programmed settings; not measured voltage or power gating"}

    def power_off(self):
        si = self.directory / "qbox-safety-island-cl0.log"
        mark = position(si)
        receipt = self.rpc("power off", "SI0", 13)
        return self._off_complete(mark, receipt)

    def _off_complete(self, mark, receipt):
        si = self.directory / "qbox-safety-island-cl0.log"
        wait_match(si, "AP cores OFF verified", mark, 35, self.stopped)
        state = self.rpc("power status", "SI0", 13)
        if int(state["value"], 0) != 3:
            raise RuntimeError("AP_OFF not observed")
        observed = self.status()
        if observed["gpio"].get("IST_DONE_N") != "0":
            raise RuntimeError("AP OFF completion GPIO missing")
        self.rpc("safety ping", "SI0", 1)
        return {"request_receipt": receipt, "power": state, "observations": observed}

    def boot_ap(self, recover=False):
        before = position(self.primary)
        command = "recover start" if recover else "power on"
        receipt = self.rpc(command, "SI0", 10 if recover else 13)
        return self._boot_complete(before, receipt)

    def _boot_complete(self, before, receipt):
        wait_match(self.primary, "NEXIOS_BSP_INITRAMFS_READY", before, 150, self.stopped)
        deadline = time.monotonic() + 50
        while time.monotonic() < deadline:
            value = self.status()
            if value.get("state") == "RUN" and value.get("fault") == "NONE":
                self.rpc("apollo ping", "AP", 1)
                return {"request_receipt": receipt, "observations": value, "linux_new_boot": True}
            time.sleep(.5)
        raise TimeoutError("AP Linux booted but SI PFDI RUN was not observed")

    def reset(self, owner_pid):
        status = load(self.directory / "tc397-status.json")
        pid = int(status["tc397_pid"])
        start = process_identity(pid)[1]
        current = pid
        while current > 1 and current != owner_pid:
            current = process_identity(current)[0]
        if current != owner_pid:
            raise RuntimeError("TC397 is outside owned board process tree")
        argv = status["qemu_command"]
        path = argv[argv.index("-qmp") + 1].split("unix:", 1)[1].split(",", 1)[0]
        before = self.status()
        can_before = self.telemetry()
        mark = position(self.log)
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(5)
            sock.connect(path)
            stream = sock.makefile("rwb", buffering=0)
            def response():
                for _ in range(64):
                    row = stream.readline(65537)
                    if not row or len(row) > 65536:
                        raise RuntimeError("invalid QMP response")
                    data = json.loads(row)
                    if "error" in data:
                        raise RuntimeError(str(data["error"]))
                    if "return" in data or "QMP" in data:
                        return data
                raise RuntimeError("QMP event quota exceeded")
            if "QMP" not in response():
                raise RuntimeError("QMP greeting missing")
            for operation in ("qmp_capabilities", "system_reset"):
                if process_identity(pid)[1] != start:
                    raise RuntimeError("MCU process changed")
                stream.write(json.dumps({"execute": operation}).encode() + b"\n")
                response()
        wait_match(self.log, "VMCU_INIT result=PASS", mark, 25, self.stopped)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            after = self.status()
            can_after = self.telemetry()
            if (after.get("epoch") == before.get("epoch") and after.get("state") == "RUN"
                    and (not can_before or can_after.get("cookie") not in (None, 0, can_before["cookie"]))):
                self.rpc("apollo ping", "AP", 1)
                return {"before": before, "after": after, "can_before": can_before, "can_after": can_after}
            time.sleep(.5)
        raise TimeoutError("MCU session renegotiation incomplete")

    def vehicle_command(self, op, arg):
        if type(op) is not int or type(arg) is not int or not 1 <= op <= 7:
            raise ValueError("vehicle op must be 1..7 and arg an integer")
        if not (0 <= arg <= (8 if op == 3 else 10 if op == 4 else 0)):
            raise ValueError("invalid vehicle argument")
        path = self.directory / "vehicle-can.jsonl"
        mark = position(path)
        boot_mark = position(self.primary)
        off_mark = position(self.directory / "qbox-safety-island-cl0.log")
        fifo_write(self.directory / "vehicle-can.in", f"command {op} {arg}\n")
        deadline = time.monotonic() + 20
        request = None
        while time.monotonic() < deadline:
            if self.stopped():
                raise InterruptedError("board stopped")
            for event in records(path, mark):
                data = bytes.fromhex(event.get("data", ""))
                if len(data) != 24:
                    continue
                if (event.get("event") == "silkit_tx" and event.get("id") == 0x600 and
                        data[1] == op and struct.unpack_from("<I", data, 16)[0] == arg):
                    request = data
                if (request and event.get("event") == "silkit_rx" and event.get("id") == 0x601 and
                        data[:2] == request[:2] and data[4:16] == request[4:16]):
                    if data[2] != 0:
                        raise RuntimeError(f"vehicle response result={data[2]}")
                    receipt = {"request": request.hex(), "response": data.hex(),
                               "value": struct.unpack_from("<I", data, 16)[0]}
                    if op == 6:
                        return self._off_complete(off_mark, receipt)
                    if op in (5, 7):
                        return self._boot_complete(boot_mark, receipt)
                    return receipt
            time.sleep(.05)
        raise UnknownOutcome("CAN command response not observed; do not retry automatically")

    def can_roundtrip(self):
        receipts = []
        self.cli("can trace on", "VMCU_CAN_TRACE on")
        try:
            for ident, reply, flags, count in [(0x123, 0x321, 0, 8), (0x1abcde, 0x1abcdf, 13, 64)]:
                payload = bytes(range(count)).hex()
                mark = position(self.log)
                self.cli(f"can send {ident:#x} {flags} {payload}", r"VMCU_CAN_SEND[^\n]*errno=0")
                receipts.append(wait_match(self.log,
                    rf"VMCU_CAN_RX id={reply:#x} flags={flags:#x}[^\n]*data={payload}", mark, 15, self.stopped))
            return {"frames": receipts, "status": fields(self.cli("can status", "VMCU_CAN_STATUS"))}
        finally:
            self.cli("can trace off", "VMCU_CAN_TRACE off")

    def safety_loss(self):
        mark = position(self.log)
        try:
            self.rpc("heartbeat off", "SI0", 3)
            fault = wait_match(self.log, r"state=DEGRADED fault=LINK_TIMEOUT\b", mark, 35, self.stopped)
        finally:
            self.rpc("heartbeat on", "SI0", 3)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            value = self.status()
            if value.get("state") == "RUN" and value.get("fault") == "NONE":
                return {"fault_observed": fault, "recovered": value}
            time.sleep(.5)
        raise TimeoutError("Safety report recovery not observed")

    def pfdi_fault(self):
        mark = position(self.log)
        fifo_write(self.directory / "primary-uart-input.fifo",
                   "kill -STOP $(pidof pfdi-sample-app); echo DASHBOARD_PFDI_STOPPED\n")
        fault = wait_match(self.log, "state=DEGRADED fault=PFDI_FAULT", mark, 90, self.stopped)
        return {"fault_observed": fault, "recovery": self.boot_ap(recover=True),
                "expected_runner_failure": "si_error:pfdi_monitor_timeout"}

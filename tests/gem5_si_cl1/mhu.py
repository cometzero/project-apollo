# SPDX-License-Identifier: BSD-3-Clause
"""Directed MHUv3/PFDI MMIO probe on native gem5 SI CL1 wiring.

This checks functional MMIO and GIC pending state, not interrupt exception
entry, full SCP firmware, MHU safety extensions or hardware timing.
"""

import argparse
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import m5
from m5.objects import ArmSPI, Root, SiCl1Mhu

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--elf", type=Path, required=True)
parser.add_argument("--gem5-source", type=Path, required=True)
parser.add_argument("--cpu", choices=["atomic", "timing", "minor"], default="atomic")
args = parser.parse_args()
config = args.gem5_source.resolve() / "configs/zena_si_cl1/run.py"
spec = importlib.util.spec_from_file_location("si_cl1", config)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
m5.ticks.setGlobalFrequency("1THz")
system = module.build(SimpleNamespace(
    elf=args.elf.resolve(), mode="benchmark", cpu=args.cpu, clock="1GHz",
    sram_latency="20ns", tcm_latency="1ns",
))
system.platform.mhu = SiCl1Mhu(
    hipc_tx_irq=ArmSPI(num=72),
    hipc_rx_irq=ArmSPI(num=73),
    pfdi_irq=ArmSPI(num=82),
)
system.platform.mhu.pio = system.fabric.mem_side_ports
root = Root(full_system=True, system=system)
result_path = Path(m5.options.outdir) / "result.json"
result_path.unlink(missing_ok=True)
m5.instantiate()
event = m5.simulate(1_000_000_000)
result = {
    "status": "PASS" if event.getCause() == "m5_exit instruction encountered"
    and event.getCode() == 0 else "FAIL",
    "cause": event.getCause(), "code": event.getCode(),
    "tick": int(m5.curTick()), "cpu": args.cpu,
    "coverage": ["four_channel_pfdi", "bounded_malformed_requests",
                 "unsupported_protocol_and_message", "slot_guards",
                 "tx_completion", "rx_masks", "gic_pending", "hipc_offline"],
    "qualification": "NATIVE_MMIO_NOT_SCP_OR_SILICON",
}
result_path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
assert result["status"] == "PASS", result

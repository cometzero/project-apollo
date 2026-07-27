---
name: apollo-platform-debug
description: Run bounded, headless source-level breakpoint probes against Apollo FVP Iris or QBox GDB and judge the generated JSON and log evidence. Use for AI-agent debugging of RSE, Safety Island CL0/CL1, TF-A, U-Boot, Linux, or QBox host code when an interactive tmux GDB pane is unsuitable.
---

# Apollo Platform Debug

Use the root launchers' `probe` mode for unattended debugging. It starts the
platform directly, observes one configured entrypoint, writes a stable result,
and terminates only the launched runner tree. FVP captures a live Iris/GDB
snapshot. QBox records its runtime PC-entry event and resolves that address
against the exact ELF with offline GDB, avoiding a live remote connection that
would perturb co-simulation timing.

Read `doc/ai-agent-headless-debug-plan-ko.md` before changing the debug
contract. Read `build/conf/local.conf`, `build/conf/bblayers.conf`, and
`build/conf/templateconf.cfg` before making a Yocto artifact claim.

## Select the probe

Use logs to find the earliest failing firmware or handoff before attaching a
debugger. Select one target:

| Target | Component | Default breakpoint |
| --- | --- | --- |
| `rse` | TF-M BL1_1 | `Reset_Handler` |
| `si_cl0` | SCP-firmware | `arch_exception_reset` |
| `si_cl1` | Zephyr | `z_cstart` |
| `tf-a` | TF-A BL2 | `bl2_main` |
| `u-boot` | U-Boot | `_start` |
| `linux` | Linux | `start_kernel` |
| `qbox` | QBox host, QBox only | `sc_main` |

Compare the same target on FVP and QBox when deciding whether a failure belongs
to firmware or the QBox model. Do not start with Linux when an earlier RSE,
Safety Island, TF-A, or U-Boot log already identifies the failing handoff.

## Run a bounded probe

Choose a unique output directory and a deadline long enough to reach the
breakpoint. Preserve an existing QBox session with `--multi-session` when
needed.

FVP reference probe:

```bash
./run_fvp.sh --machine apollo-qvp \
  --debug tf-a --debug-mode probe --debug-timeout 600 \
  --out-dir build/agent-debug/fvp-tfa
```

Yocto QBox BSP probe:

```bash
./run_qbox_yocto.sh --bsp \
  --debug tf-a --debug-mode probe --debug-timeout 600 \
  --out-dir build/agent-debug/qbox-yocto-tfa
```

Local-build QBox probe:

```bash
./run_qbox_local.sh \
  --debug tf-a --debug-mode probe --debug-timeout 600 \
  --out-dir build/agent-debug/qbox-local-tfa
```

Use `--debug-result PATH` when the result must live outside the output
directory. Use `--debug-mode server` only when another bounded automation step
will attach to the published endpoint and later terminate the launcher.
Interactive mode is for a human tmux session, not an unattended agent.
Do not test a QBox GDB endpoint with `nc`, `connect_ex`, or another plain TCP
health check. QEMU consumes that first connection as a debugger session. QBox
firmware probes use the fresh `QBox GDB entry breakpoint reached:` event and
offline GDB symbolization instead. Server mode checks the local listening
socket without opening it.

## Judge the evidence

Read the result before interpreting console output:

```bash
python3 - <<'PY' build/agent-debug/fvp-tfa/debug-result.json
import json
from pathlib import Path
import sys

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for key in (
    "status",
    "passed",
    "breakpoint_hit",
    "expected_pc",
    "observed_pc",
    "timed_out",
    "cleanup_completed",
    "message",
):
    print(f"{key}: {result[key]}")
PY
```

A successful probe requires all of:

- launcher exit status `0`;
- `status` equal to `passed`;
- `breakpoint_hit` and `passed` equal to `true`;
- expected and observed PCs equal after the Arm Thumb-bit normalization;
- `cleanup_completed` equal to `true`;
- `gdb.log` containing the selected source location;
- for FVP, a usable live backtrace or register snapshot;
- for QBox, the entry symbol and disassembly resolved from the exact ELF.

QBox probe mode intentionally does not claim live register or backtrace
evidence. Use `--debug-mode server` with a bounded client, or interactive mode,
when live state is required. Record that attaching QEMU GDB can perturb
power-management and firmware timeout behavior.

Interpret nonzero exits as:

- `2`: invalid input, manifest, ELF, or debugger setup;
- `3`: endpoint or breakpoint deadline expired;
- `4`: debugger failure or PC mismatch.

Inspect `gdb.log`, `agent-runner.log` or `fvp_stdout.log`, and the platform/UART
logs in the same output directory. Report exact paths, command, elapsed time,
PCs, source line, cleanup state, and any unverified domain. Do not report a
configuration or manifest as runtime proof.

## Escalate only after a failed probe

For an endpoint timeout, identify the earliest missing platform marker in the
runner and UART logs. For a PC mismatch, compare the manifest symbol with
`gdb.log` and confirm that the ELF belongs to the launched image. For an FVP
Iris success followed by a GDB failure, inspect `iris-probe.log`,
`cornea-prime.log`, and `gdb.log` separately.

Change source only after the evidence identifies an owning component. Re-run
the same probe after the change, then broaden to the normal boot validation
ladder in `AGENTS.md`.

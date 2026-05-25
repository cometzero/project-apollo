# RSE-QBox T019F Team Task

Workspace: `/build/arm/arm-auto-solutions`.

This is a kas-composed Arm Auto Solutions/QBox workspace, not a single root Git
repository. Read `.config.yaml` before any build/runtime claim. Active baseline:
`MACHINE = "fvp-rd-aspen"`, `RD_ASPEN_VARIANT = "cfg2"`,
`PC_CPUS_COUNT_DEFAULT = "4"`, `ARCHITECTURE_BAREMETAL = true`.

Use the project-local `$arm-auto-solutions`, `$qbox-dev`, `$systemc-dev`, and
`$spec-kit` workflows. Preserve user changes; do not reset nested repos.

## Current State

The current spec/task source of truth is under `doc/spec/rse-qbox/`.
T019F is open:

> Identify the next post-system-control no-console blocker after the
> `reset_mask` write. Use trace/source mapping to separate missing
> boot-media/provisioning, LCM/OTP, ATU/MPC, and reset lifecycle effects before
> adding more compatibility registers.

T019E is complete. It added `rse_sysctrl` and removed the previous
`0x58021100` reset-syndrome Data Abort. Latest evidence:

- `build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v2/`
- `result.json`: `passed=false`, `blocker=qbox_platform_timeout`,
  `first_failing_register_access=null`,
  `fidelity_labels.rse_sysctrl="touched-register-model"`
- `qbox-platform.log` shows:
  - `platform.rse_sysctrl read offset=0x100 len=0x4 value=0x80000000`
  - `platform.rse_sysctrl read offset=0x104 len=0x4 value=0x0`
  - `platform.rse_sysctrl write offset=0x104 len=0x4 value=0x100`

## Team Lanes

1. Trace/source-mapping lane:
   - Inspect existing `rse-sysctrl` runtime artifacts.
   - Run the narrowest useful additional trace only if needed.
   - Map the repeating PC/source location after `reset_mask = 0x100`.
   - Avoid broad recursive scans of `build/`; inspect targeted TF-M files and
     logs only.

2. Model-gap lane:
   - From local TF-M, FVP config, and existing QBox components, determine
     whether the next blocker is boot media/provisioning, LCM/OTP, ATU/MPC,
     reset lifecycle side effects, or another touched register.
   - Propose the smallest SystemC/TLM increment that moves the blocker without
     hiding fidelity gaps.
   - If the root cause is clear and the edit is narrow, implement it; otherwise
     report exact evidence and stop before speculative modeling.

3. Verification/documentation lane:
   - Keep file-backed evidence under `build/qbox-fvp-rd-aspen/`.
   - Run focused checks only:
     - `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
     - `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
     - `git -C tools/qbox diff --check`
     - relevant `cmake --build tools/qbox/build --target ...`
     - relevant `ctest --test-dir tools/qbox/build -R ... --output-on-failure`
   - Update `doc/spec/rse-qbox/task.md`, `evidence.md`, `design.md`, and
     `plan.md` only when behavior or blockers change.

## Reporting Requirements

Report:

- files inspected
- files changed
- commands run
- generated artifact roots
- runtime result and exact blocker
- remaining fidelity gaps
- any commits created by team runtime or workers

Do not claim MVP success unless the required RSE boot, RSE-SCP, measured boot,
AP release, and Linux login markers are present.

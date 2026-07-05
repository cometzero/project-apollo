# QBox Apollo FVP Full-System Tasks

Generated: 2026-06-03

Status: implemented and verified

The authoritative goal and completion-verification contract is
`doc/qbox-apollo-fvp-full-system-goal-verification.md`. This task list tracks
implementation work against that contract.

## Success Criteria

- Local Apollo artifacts under `build/local-apollo-fvp/deploy/` are the default
  inputs.
- Existing direct boot through `scripts/run/run_qbox_apollo_fvp_linux.py` remains
  unchanged and usable.
- A new full-system path boots RSE first, releases AP through the modeled
  system-management path, and records per-subsystem logs.
- Safety Island service-model and live Cortex-R82 modes are both explicit in
  command-line options and `result.json`.
- Live SI CL0/CL1 work does not hide remaining fidelity gaps behind Linux-only
  pass criteria.
- Memory maps, interrupt maps, ATU windows, MHU channels, and hardware block
  coverage are validated against both documentation and local source code.
- A single verifier command can reject premature completion claims from the
  saved evidence directories.

## Goal And Completion Gates

The full-system task is complete only when QBox can boot the Apollo FVP local
artifacts through the same subsystem chain used by FVP:

```text
RSE TF-M -> SI CL0 SCP-firmware -> SI CL1 Zephyr -> AP TF-A/OP-TEE/U-Boot/Linux
```

Linux login alone is not a completion point. It is only one marker inside the
full-system gate because the direct-boot path can reach Linux without proving
RSE, Safety Island CL0, Safety Island CL1, SCMI, HIPC, PFDI, ATU, or GIC
multiview fidelity.

The expected final objective is a file-backed QBox run that proves these
properties together:

- RSE TF-M starts from the local RSE ROM/flash/OTP images and drives the boot
  handoff instead of being bypassed.
- SI CL0 SCP-firmware and SI CL1 Zephyr run as live Cortex-R82 domains, not as
  service-model placeholders.
- AP TF-A, OP-TEE, U-Boot, and Linux boot from the Apollo firmware/rootfs
  artifacts after the modeled system-management release path.
- AP Linux post-login probes show the expected HIPC/RPMsg, PFDI, module, and
  device evidence without unclassified failures.
- FVP-vs-QBox boot markers, normalized memory/interrupt/ATU maps, and hardware
  coverage checks all pass.

### Goal Statement

The goal is to prove an FVP-equivalent Apollo system boot in QBox, using the
same locally built artifacts that are used for `apollo-fvp` FVP validation. The
proof must cover the complete system-management and application-processor boot
path, not just an AP Linux end state:

| Scope | Required completion condition |
| --- | --- |
| Boot ownership | RSE starts first from local TF-M images and initiates the downstream SI/AP handoff. |
| Safety Island | SI CL0 SCP-firmware and SI CL1 Zephyr run as live Cortex-R82 domains in the final gate. |
| Primary Compute | AP TF-A, OP-TEE, U-Boot, and Linux boot from the firmware/rootfs artifacts after the modeled release path. |
| Cross-domain services | SCMI, MHU, HIPC/RPMsg, PFDI, ATU/ATW, and GIC multiview evidence is present or classified by gate. |
| Equivalence evidence | FVP and QBox logs, normalized maps, and hardware coverage reports agree with no unclassified boot-critical gaps. |

The final completion point is not a command starting successfully. It is the
saved evidence bundle under `build/qbox-apollo-fvp/full-live-cl0-cl1/` passing
the strict verifier after a fresh full live run and FVP comparison.

### Completion Evidence Bundle

The final evidence bundle must contain these files before a completion claim is
allowed:

| Artifact | Purpose |
| --- | --- |
| `result.json` | Records the full live run command, artifact inputs, `safety_island_mode`, marker groups, logs, blockers, and `completion_gates`. |
| `comparison.json` | Compares required FVP boot markers against the full live QBox run. |
| `map-comparison.json` | Checks AP, RSE, SMD, SI CL0, SI CL1 memory, interrupt, and ATU views. |
| `coverage-audit.json` | Confirms boot-critical hardware blocks are live, service-modeled with accepted debt, or stubbed with rationale. |
| `final-verification.json` | Machine-readable final verdict written by `scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`. |
| Per-subsystem UART/log files | Provide raw evidence for RSE, SI CL0, SI CL1, secure AP firmware, U-Boot, and Linux marker decisions. |

Completion can be claimed only when `final-verification.json` records
`completion_claim_allowed: true`, `completion_ready: true`, and every gate from
`G0` through `G5` is `pass`.

### Completion Levels

| Level | Name | Objective | Exit Evidence |
| --- | --- | --- | --- |
| G0 | Contract readiness | Local artifacts, build targets, map ledger, and hardware coverage contract are available. | `--check-only`, source probes, map validator, and coverage audit all pass. |
| G1 | Direct-boot guardrail | Existing AP Linux direct boot still works after full-system changes. | Existing `scripts/run/run_qbox_apollo_fvp_linux.py` pass result and logs. |
| G2 | Service-model full boot | RSE-first QBox boot reaches AP Linux with explicit SI service-model debt. | `full-service-model/result.json`, subsystem logs, and FVP comparison with service-model gaps classified. |
| G3 | Live CL1 integration | Zephyr CL1 runs on Cortex-R82 and AP Linux HIPC/RPMsg probes use live CL1 behavior. | `full-live-cl1/result.json`, CL1 log markers, Linux probe markers, and no unclassified PFDI/IPC failure. |
| G4 | Live CL0/CL1 integration | SCP-firmware CL0 and Zephyr CL1 both run live while AP reaches Linux. | `full-live-cl0-cl1/result.json` with RSE, CL0, CL1, AP firmware, U-Boot, Linux, and post-login marker groups passing. |
| G5 | FVP equivalence closure | QBox full live behavior matches required FVP boot markers and documented maps. | `comparison.json`, `map-comparison.json`, and coverage audit show no missing required marker or absent boot-critical block. |

### Reviewer Acceptance Contract

Review and completion decisions should use the following contract:

1. The full-system objective is the integrated `live-cl0-cl1` run, not a
   successful direct Linux boot or a single-domain Safety Island boot.
2. `G0`, `G1`, `G2`, and `G3` are mandatory regression and integration
   milestones. They can prove progress, but they cannot authorize completion.
3. `G4` is the first runtime completion candidate because it requires RSE,
   live SI CL0, live SI CL1, AP firmware, U-Boot, Linux, and post-login marker
   groups to pass in one run.
4. `G5` is the final equivalence gate. It must close FVP log comparison,
   memory/interrupt/ATU map comparison, and hardware coverage audit gaps.
5. The only accepted completion verdict is `completion_claim_allowed: true`
   from `scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`.
6. Any missing sidecar artifact, missing subsystem log, `not_run` gate,
   unclassified marker failure, or absent boot-critical hardware block keeps
   the task incomplete.

The reviewable completion target is therefore:

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/
  result.json
  comparison.json
  map-comparison.json
  coverage-audit.json
  final-verification.json
```

### Completion Claim Policy

Only the strict final verifier can authorize a full-system completion claim.
Intermediate runs are milestone evidence and must stay labeled as such:

- `scripts/run/run_qbox_apollo_fvp_linux.py` is a direct-boot guardrail, not the
  full-system target.
- `service-model` proves the RSE-first AP boot path but keeps Safety Island
  CPU fidelity debt.
- Isolated CL0 or CL1 runs prove Cortex-R82 firmware bring-up only; they do
  not prove AP integration.
- `live-cl1` proves Zephyr integration while CL0 remains modeled; it is not the
  final completion point.
- `live-cl0-cl1` becomes a completion candidate only after G5 comparison,
  map-validation, coverage audit, and strict verifier checks pass.

The authoritative final verdict is:

```bash
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

The output JSON must contain `goal_definition`, `completion_policy`,
`completion_levels`, `final_acceptance_artifacts`, `review_rules`,
`completion_claim_allowed: true`, `completion_ready: true`, and
`overall_gates.G0..G5 == "pass"`. If any gate is `blocked`, `fail`, or
`not_run`, the final report must not claim completion.

### Gate Commands

Gate G0:

```bash
python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --check-only \
  --out-dir build/qbox-apollo-fvp/full-check-only
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-check-only/map-validation.json
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-check-only/coverage-audit.json
cmake --build build/local-apollo-fvp/work/qbox-platform --target cpu_arm_cortexR82 remote_cpu addrtr platforms-vp --parallel 8
```

Gate G1:

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build \
  --timeout 600 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/direct-guardrail
```

Gate G2:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode service-model \
  --timeout 900 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-service-model
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-service-model \
  --output build/qbox-apollo-fvp/full-service-model/comparison.json
```

Gate G3:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl1 \
  --timeout 900 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl1
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl1/coverage-audit.json
```

Gate G4:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 1200 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
```

Gate G5:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-live-cl0-cl1 \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

### Required Marker Groups

Every runtime gate must write marker status into `result.json` and keep the
raw logs that produced the status. A marker group is complete only when all
required markers in that group pass or the failure is classified as an
accepted fidelity gap for that gate.

| Group | Required evidence |
| --- | --- |
| RSE | TF-M BL1_1 starts, BL1_2/BL2 handoff occurs, RSE flash/OTP access is visible, SI and AP images are loaded or released through the modeled path. |
| SI CL0 | SCP-firmware starts, UART log is captured, GIC multiview configuration succeeds, SCMI/AP release path progresses, PFDI monitor has no unclassified timeout. |
| SI CL1 | Zephyr starts, UART log is captured, timer/GIC activity is visible, OpenAMP/RPMsg or HIPC markers progress, PFDI agent/service markers are classified. |
| AP firmware | AP BL2, BL31, OP-TEE, and U-Boot markers appear in order from the AP firmware boot path, not the direct Linux boot shortcut. |
| Linux | Kernel boots to login, required modules load or failures are classified, post-login RPMsg/HIPC/PFDI probes pass or record a reviewed fidelity gap. |
| Maps and interrupts | AP, RSE, SMD, SI CL0, and SI CL1 memory and IRQ views match the normalized ledger or list reviewed exceptions. |

### Completion Verdict Rules

Use these verdicts in `result.json`, `summary.txt`, and final reports:

| Verdict | Meaning |
| --- | --- |
| `pass` | The gate command exited successfully, all required marker groups passed, and generated comparison/audit artifacts have no unclassified missing requirement. |
| `blocked` | Execution reached an external or not-yet-implemented dependency that prevents the gate from running to completion; the blocker has a specific owner and next action. |
| `fail` | The command ran, but a required marker, map, interrupt, or coverage condition failed without an accepted fidelity-gap classification. |
| `not_run` | The gate was intentionally skipped; final reports must say why and must not claim completion for that level. |

The full-system task is not complete if any of these are true:

- G1 direct boot regresses.
- G4 live CL0/CL1 has not passed.
- G5 FVP comparison has missing required markers.
- AP firmware is only present as RSE measured-boot markers. Final G4/G5
  evidence must also show `platform_observations.ap_cpus == 16`, Linux-side
  primary-console enumeration `online=0-15` and `cpuinfo_processors=16` without
  stale `maxcpus=4`,
  `secure_console_observations.ap_bl2_console == true`,
  `secure_console_observations.bl31_console == true`,
  `secure_console_observations.optee_console == true`, and
  `primary_console_observations.u_boot_console == true`.
- A boot-critical hardware block is `absent` without a reviewed service-model
  or register-stub rationale.
- The only evidence is tmux screen output without file-backed logs and
  `result.json`.
- A failure is described in prose but not classified in machine-readable
  output.

### Definition Of Done

The full-system task is done when the QBox Apollo FVP target proves the same
boot shape as the Apollo FVP local build with file-backed evidence:

1. `G0` passes with all required local artifacts resolved, Cortex-R82 support
   built, and memory/IRQ/ATU/hardware coverage contracts validated.
2. `G1` passes after the full-system changes, proving the existing direct
   Linux boot path did not regress.
3. `G2` passes with an RSE-first service-model full boot and explicit
   machine-readable Safety Island fidelity debt.
4. `G3` passes with live SI CL1 Zephyr HIPC/RPMsg integration and explicit
   evidence that CL0 remains outside the final live-domain scope for that gate.
5. `G4` passes with live RSE TF-M, live SI CL0 SCP-firmware, live SI CL1
   Zephyr, and AP TF-A/OP-TEE/U-Boot/Linux marker groups all passing in one
   integrated run.
6. `G5` passes with FVP-to-QBox comparison, map comparison, and coverage audit
   showing no missing boot-critical requirement and no unclassified fidelity
   gap.
7. Every generated `result.json` records `completion_gates`, `verdict`,
   `safety_island_mode`, `marker_groups`, `console_logs`, `blocker`, and the
   command used to create the evidence.
8. `python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`
   exits 0 and writes `completion_ready: true`.

`G2` service-model full boot and `G3` live-CL1 boot are required milestones,
but neither is a completion point. They exist to isolate regressions before the
final live CL0/CL1 integration gate.

### End-State Verification Plan

Run the gates in order and keep each output directory. A later gate must not
overwrite evidence from an earlier gate.

| Step | Command group | Required output | Pass condition |
| --- | --- | --- | --- |
| 1 | G0 contract readiness commands | `build/qbox-apollo-fvp/full-check-only/result.json`, map validation JSON, coverage audit JSON, targeted QBox build logs | All commands exit 0; `completion_gates.G0 == "pass"` and `G1..G5 == "not_run"`. |
| 2 | G1 direct-boot guardrail | `build/qbox-apollo-fvp/direct-guardrail/result.json` plus AP console logs | Existing direct boot reaches login and post-login probes; no full-system change is allowed to weaken this check. |
| 3 | Fresh FVP baseline | `build/local-apollo-fvp/fvp-boot/result.json` plus per-UART logs | FVP run passes and logs contain RSE, SI CL0, SI CL1, AP firmware, U-Boot, Linux, HIPC/RPMsg, and PFDI markers used for comparison. |
| 4 | G2 service-model full boot | `build/qbox-apollo-fvp/full-service-model/result.json` and `comparison.json` | RSE-first boot reaches AP Linux; service-modeled SI debt is explicit and machine-readable. |
| 5 | G3 live CL1 boot | `build/qbox-apollo-fvp/full-live-cl1/result.json` | CL1 Zephyr markers, Linux HIPC/RPMsg probes, and PFDI classification pass without hiding CL0 service-model debt. |
| 6 | G4 live CL0/CL1 boot | `build/qbox-apollo-fvp/full-live-cl0-cl1/result.json` | RSE, SI CL0, SI CL1, AP firmware, U-Boot, Linux, and post-login marker groups pass in the same run. |
| 7 | G5 equivalence closure | `comparison.json`, `map-comparison.json`, coverage audit JSON in `full-live-cl0-cl1/` | FVP comparison, map validation, and coverage audit pass with no absent boot-critical block or unclassified marker gap. |
| 8 | Completion verifier | `build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json` | `completion_ready == true`; `overall_gates.G0..G5 == "pass"`; strict verifier exits 0. |

The final acceptance report must cite these artifact paths and the exact
commands used. The final `full-live-cl0-cl1/result.json` must prove the
runtime G4 candidate:

```json
{
  "verdict": "pass",
  "safety_island_mode": "live-cl0-cl1",
  "completion_gates": {
    "G0": "pass",
    "G4": "pass"
  }
}
```

G5 is proven by `comparison.json`, `map-comparison.json`, and
`coverage-audit.json` in the same final directory. Full-system completion can
be claimed only after `final-verification.json` records
`overall_gates.G0..G5 == "pass"` and `completion_claim_allowed: true`.

If a gate cannot run, the report must say `blocked`, not `pass`, and name the
specific missing model, artifact, host dependency, or hardware fidelity gap.

The current implementation can also be assessed without claiming completion:

```bash
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --si-cl1-isolated-dir \
    build/qbox-apollo-fvp/si-cl1-allcpus-20260603-125931 \
  --output build/qbox-apollo-fvp/full-completion-verification.json
```

This non-strict form is useful during development. It may return `blocked`
while `G3` or `G4` are still intentionally classified as not implemented. It
does not authorize a full-system completion claim; only `--strict-final` does.
The optional `--si-cl1-isolated-dir` input records Phase 2 milestone evidence
in `milestone_evidence`; it never changes the G0-G5 completion gates.

### Current Gate Status

As of the current saved evidence, the full-system G0-G5 contract passes:

```bash
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

The verifier reports:

| Gate | Current status | Meaning |
| --- | --- | --- |
| G0 | `pass` | Contract readiness evidence is present. |
| G1 | `pass` | Direct AP Linux boot guardrail is still passing. |
| G2 | `pass` | Canonical service-model full boot evidence is present. |
| G3 | `pass` | Canonical live CL1 Zephyr HIPC/RPMsg integration is present. |
| G4 | `pass` | Canonical live CL0/CL1 reaches RSE TF-M, CL0 SCP-firmware, CL1 Zephyr, AP firmware, Linux, and post-login probing. |
| G5 | `pass` | FVP comparison, map comparison, coverage audit, and strict final verification pass in the canonical final directory. |

This means the current correct project verdict is `pass`. The latest
completion artifacts are:

```text
build/qbox-apollo-fvp/full-check-only/result.json
build/qbox-apollo-fvp/direct-guardrail/result.json
build/qbox-apollo-fvp/full-service-model/result.json
build/qbox-apollo-fvp/full-service-model/comparison.json
build/qbox-apollo-fvp/full-live-cl1/result.json
build/qbox-apollo-fvp/full-live-cl1/coverage-audit.json
build/qbox-apollo-fvp/full-live-cl0-cl1/result.json
build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json
build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json
build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

`final-verification.json` records:

```text
verdict: pass
completion_ready: true
completion_claim_allowed: true
overall_gates.G0..G5: pass
first_incomplete_gate: null
first_blocker: null
completion_rejection_reason: null
```

The G4 AP-SI HIPC/RPMsg blocker from rt43 is resolved by the final canonical
run: Linux creates `virtio6.ethsi1.-1.1024`, `ip link show ethsi1` returns 0,
and the CL1 Zephyr log records `veth_rpmsg: RPMSG Endpoint: ATTACHED`.

## Phase 0: Baseline And Contracts

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-001 | Define Apollo full artifact resolver. | `scripts/run/run_qbox_apollo_fvp_full.py --check-only` records all local firmware, boot, rootfs, and symbol inputs. | Missing files fail with `missing_artifact:<name>`; present files record path and size in `result.json`. |
| QAP-FULL-002 | Preserve direct Linux boot as a guardrail. | Existing `scripts/run/run_qbox_apollo_fvp_linux.py` remains untouched except shared helper extraction if reviewed. | `python3 scripts/run/run_qbox_apollo_fvp_linux.py --skip-build --timeout 600 --post-login-probe` still reaches the existing pass criteria. |
| QAP-FULL-003 | Capture fresh FVP baseline logs. | A local FVP run under `build/local-apollo-fvp/fvp-boot/` with RSE, SI CL0, SI CL1, TF-A, and U-Boot/Linux logs. | `result.json` passes and logs include subsystem markers used by QBox comparison. |
| QAP-FULL-004 | Confirm Cortex-R82 source and build support. | Source probe and targeted QBox build evidence. | `python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .` passes; `cmake --build build/local-apollo-fvp/work/qbox-platform --target cpu_arm_cortexR82 --parallel 8` passes. |
| QAP-FULL-005 | Build normalized map and IRQ ledger. | Source-backed data file or script output consumed by the validator. | AP, RSE, SMD, SI CL0, and SI CL1 memory views and interrupt views include source references from programmer model, Lua, DTS, SCP headers, and Zephyr DTS. |
| QAP-FULL-006 | Classify hardware block coverage. | Initial coverage report for CPU, GIC, MHU, ATU, PPU/SCR/RGM, FMU, SSU, SMCF, RAS, timers, watchdogs, UARTs, boot security blocks, and AP I/O. | Each block is marked `live`, `service-modeled`, `register-stub`, or `absent`; unknown ownership is treated as a blocker. |

## Phase 1: Apollo Full Service-Model Boot

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-010 | Add Apollo full Lua platform. | `tools/qbox-platform/platforms/apollo/apollo-qvp.lua`. | Derived from `fvp-rd-aspen-rse/conf.lua`; uses Apollo artifact defaults and `QBOX_APOLLO_FULL_` variables; direct `conf.lua` is unchanged. |
| QAP-FULL-011 | Add full-system runner. | `scripts/run/run_qbox_apollo_fvp_full.py`. | Supports `--check-only`, `--si-mode`, `--post-login-probe`, `--out-dir`, artifact overrides, per-run writable flash/OTP copies, and structured `result.json`. |
| QAP-FULL-012 | Use local QBox build command. | `./local_build.sh qbox`. | Builds `platforms-vp`, `remote_cpu`, `cpu_arm_cortexM55`, `cpu_arm_cortexA720AE`, `cpu_arm_cortexR82`, MHU, RSE, flash, UART, GIC, SMMU, and virtio targets needed by full boot. |
| QAP-FULL-013 | Add static map validator. | `scripts/test/validate_qbox_apollo_fvp_full_map.py`. | Checks AP, RSE, SMD, SI CL0, SI CL1 memory views; AP GIC, RSE NVIC, SI CL0 GIC view, SI CL1 GIC view; ATU/ATW windows; AP-RSE/RSE-SI/AP-SI/CL1-CL0 MHU channels; UART, timers, watchdogs, HIPC, PFDI, FMU, SSU, and SMCF evidence. |
| QAP-FULL-014 | Run service-model full boot. | `build/qbox-apollo-fvp/full-service-model/`. | RSE boot, RSE/SI SCMI handoff, AP firmware, Linux login, and post-login probes pass; `result.json` states SI CL0/CL1 are service-modeled. |
| QAP-FULL-015 | Compare service-model boot with FVP. | `comparison.json` in the same run directory. | Missing FVP markers are reported explicitly; service-model-only gaps are not counted as hidden passes. |
| QAP-FULL-016 | Add ATU trace and policy reporting. | Apollo full mode exposes ATU trace controls and writes ATU summary into `result.json`. | Translation hits, misses, seeded windows, firmware-programmed windows, and default-closed failures are visible in logs. |
| QAP-FULL-017 | Add hardware coverage audit. | `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`. | Coverage report fails if a boot-critical block is absent without an explicit service-model or stub rationale. |

## Phase 2: Isolated Live Safety Island Bring-Up

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-020 | Add isolated SI CL1 Zephyr QBox mode. | Minimal platform or `--si-mode live-cl1 --isolated` path. | Cortex-R82 CL1 starts Zephyr, emits CL1 UART markers, and reaches the expected OpenAMP/RPMsg initialization point without AP integration. |
| QAP-FULL-021 | Add isolated SI CL0 SCP-firmware QBox mode. | Minimal platform or `--si-mode live-cl0 --isolated` path. | Cortex-R82 CL0 starts SCP-firmware, initializes timers/interrupts/UART, and reaches early platform module markers. |
| QAP-FULL-022 | Add SI UART/log backends. | `qbox-safety-island-cl0.log` and `qbox-safety-island-cl1.log`. | Logs are file-backed and also usable from the tmux viewing script without relying on screen-only output. |
| QAP-FULL-023 | Validate R82 timer/GIC/MPU behavior with firmware. | Runtime evidence plus blocker classification. | Failures are classified as CPU model, MPU, GIC/timer, UART, memory map, or firmware artifact blockers. |
| QAP-FULL-024 | Validate Safety Island local maps. | Isolated CL0/CL1 runs with map probes or trace logs. | CL0 reaches GIC view0, UART, timers, SSU/FMU, MHU frames, and ATW windows; CL1 reaches GIC view, UART, HIPC MHU, PFDI MHU, and shared SRAM. |
| QAP-FULL-025 | Add SystemC SI GIC multiview controller. | `tools/qbox/systemc-components/gicx00_multiview/`. | Dynamic module builds, exposes `view0_dist`, `view0_redist[]`, `spi_in[]`, `view1_spi_out[]`, and `view2_spi_out[]`, and does not patch the existing QEMU GICv3 wrapper. |
| QAP-FULL-026 | Implement SI GIC multiview register model. | `GICD_CTLR`, `GICD_CFGID`, `GICD_IVIEWR`, `GICR_PWRR`, and `GICR_VIEWR` behavior. | SCP-firmware can read the view capability bit, program redistributor and SPI views, and poll `GICR_PWRR` without unsupported-access traps. |
| QAP-FULL-027 | Wire SI CL0/CL1 QEMU GICv3 backends. | Apollo full Lua wiring with `si_cl0_gic`, `si_cl1_gic`, and `gicx00_multiview`. | View-0 MMIO reaches SystemC; CL0 view-1 MMIO reaches the CL0 QEMU GICv3 backend; CL1 view-2 MMIO reaches the CL1 QEMU GICv3 backend. |
| QAP-FULL-028 | Route SI SPIs through the multiview controller. | MHU, UART, timer, FMU/SSU/SMCF, and other shared SI SPI bindings in `apollo-qvp.lua`. | CL0 and CL1 interrupts are delivered through the firmware-configured local view without collapsing CL1 Zephyr SPIs into CL0 SCP-firmware IRQ names. |
| QAP-FULL-029 | Validate SI GIC multiview routing. | Unit tests plus isolated and integrated runtime evidence. | `cmake --build build/local-apollo-fvp/work/qbox-platform --target gicx00_multiview --parallel 8`, `ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R gicx00_multiview`, and `python3 scripts/run/run_qbox_apollo_fvp_full.py --si-mode live-cl0-cl1 --timeout 600 --post-login-probe --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1` pass or record a classified blocker. |

### Current Phase 2 Evidence

QAP-FULL-020 isolated CL1 is currently proven by:

```text
build/qbox-apollo-fvp/si-cl1-allcpus-20260603-125931/result.json
```

That run records `verdict: pass`, `task: QAP-FULL-020`, and
`completion_gate_effect: isolated_milestone_only`. The required CL1 markers
`cpu0_oor`, `zephyr_boot`, `shell`, `pfdi_agent`, and `pfdi_service` are all
true, and the secondary CPU markers for CPU1 through CPU3 are also true.

This is milestone evidence only. AP/CL1 HIPC RPMsg attach, live CL0/PFDI
monitor peer behavior, integrated `full-live-cl1`, final `full-live-cl0-cl1`,
and G5 FVP equivalence closure remain outside this isolated run and must still
be proven by their own gates.

## Phase 3: Live CL1 HIPC/RPMsg Integration

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-030 | Replace CL1 RPMsg name-service model with live Zephyr. | `--si-mode live-cl1` integrated with AP Linux. | Linux `arm_si_rproc`, `rpmsg_ns`, `virtio_rpmsg_bus`, `rpmsg_net`, and `ethsi1` markers pass using Zephyr-generated messages. |
| QAP-FULL-031 | Wire AP-SI CL1 MHU doorbells to live CL1. | MHU routing in `apollo-qvp.lua` plus tests/log markers. | AP kicks reach CL1, CL1 kicks reach AP, and vring/shared-buffer ownership is visible in logs or trace. |
| QAP-FULL-032 | Validate CL1 PFDI local behavior. | CL1 log and Linux probe evidence. | No AP core PFDI monitor timeout is observed; PFDI agent/service markers match the FVP baseline where applicable. |
| QAP-FULL-033 | Validate HIPC shared memory layout. | AP Linux and CL1 Zephyr traces for resource table, vrings, and RPMsg buffers. | The 512 KiB HIPC layout is shared by AP and CL1 without overlapping SCMI/PFDI monitor payloads. |

### Current Phase 3 Evidence

QAP-FULL-030 through QAP-FULL-033 are currently proven by:

```text
build/qbox-apollo-fvp/full-live-cl1-bridge-20260603-134602/result.json
build/qbox-apollo-fvp/full-live-cl1-bridge-20260603-134602/coverage-audit.json
build/qbox-apollo-fvp/full-live-cl1-bridge-20260603-134602/progress-verification.json
```

That run records `safety_island_mode: live-cl1`, `verdict: pass`, and
`completion_gates.G3: pass`. The CL1 log contains Zephyr boot, CPU0 OoR,
PFDI agent setup, PFDI service ready, network configuration, and
`veth_rpmsg: RPMSG Endpoint: ATTACHED`. The AP Linux post-login probe records
`arm_si_rproc`, `rpmsg`, and `hipc_ethsi1` driver patterns as true, with
`remoteproc_state:si-cl1:attached`,
`rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1`, and `ethsi1_iplink_rc:0`.

The root cause of the previous live-CL1 blocker was that the service-model
`doorbell` MHU protocol did not forward AP postbox doorbells to a paired live
CL1 mailbox when synthetic auto-ack/RPMsg name-service injection was disabled.
The live CL1 path now uses the existing `doorbell-bridge` protocol for the
AP-to-CL1 and CL1-to-AP HIPC pairs, and the run keeps MHU traces under:

```text
build/qbox-apollo-fvp/full-live-cl1-bridge-20260603-134602/ap-si-mhuv3-trace.log
build/qbox-apollo-fvp/full-live-cl1-bridge-20260603-134602/si-cl1-mhuv3-trace.log
```

This bridge run originally advanced the project to `G3: pass` while `G4` and
`G5` were still incomplete. The current canonical evidence now extends that
progress through live CL0/CL1 integration and G5 equivalence closure.

## Phase 4: Live CL0 SCP/System-Management Integration

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-040 | Replace RSE-SI CL0 SCMI service model with live SCP-firmware. | `--si-mode live-cl0-cl1` starts CL0 SCP-firmware. | RSE-SI SCMI init succeeds through live CL0 and AP power-on/reset release still occurs. |
| QAP-FULL-041 | Wire CL0 power/reset/PPU/SCR interactions. | Live CL0 controls AP release path. | AP CPU0 reset release is caused by the live CL0 path, not the service model. |
| QAP-FULL-042 | Integrate CL0 and CL1 together. | Shared SI memory, MHU, and interrupt routing for both clusters. | CL0 SCP and CL1 Zephyr logs both progress while AP reaches Linux. |
| QAP-FULL-043 | Wire SI ATW windows for CL0 management. | CL0-visible translations for AP GIC, AP shared SRAM, SMD timers, SYSTOP PIK, SID, SMCF, SMD SRAM, and NI-710AE FMU windows. | SCP-firmware accesses these targets through ATW-backed routes, not hard-coded local aliases. |
| QAP-FULL-044 | Add CL0 safety and diagnostics block behavior. | FMU, SSU, SMCF, SBISTC/RAS handling strategy and implemented boot-critical registers. | SCP-firmware initializes FMU/SSU/SMCF paths without unsupported access traps; remaining diagnostic fidelity gaps are reported. |
| QAP-FULL-045 | Validate PFDI monitor path end to end. | AP, CL0, and CL1 logs plus Linux probe evidence. | AP core and CL1 PFDI monitor doorbells use the documented MHU channels and no monitor timeout appears in CL0 logs. |

### Current Phase 4 Evidence

The canonical live CL0/CL1 integration path starts SCP-firmware on a CL0
Cortex-R82 CPU and Zephyr on the CL1 Cortex-R82 cluster in the same QBox run.
It uses the normal boot-flash path, not the diagnostic boot-flash DMI
accelerator. The platform includes the boot-critical CL0 register surfaces
needed for the final pass: SI GIC multiview, SCR/PPU, generic timer, PLL,
System ID/PCID, SMCF MGI, NI-710AE NCI/APU programming windows, CMN-Cyprus,
AP GIC multiview, AP/CL1 PPUs, AP cluster-control windows, FMU/SSU, and the
CL0-visible ATW self-check windows.

```text
tools/qbox-platform/platforms/apollo/apollo-qvp.lua
tools/qbox/systemc-components/gicx00_multiview/
tools/qbox/systemc-components/host_ni710ae_nci/
tools/qbox/systemc-components/host_cmn_cyprus/
tools/qbox/systemc-components/host_ppu/
tools/qbox/systemc-components/host_smcf_mgi/
tools/qbox/systemc-components/reset_fanout/
build/qbox-apollo-fvp/full-live-cl0-cl1/result.json
build/qbox-apollo-fvp/full-live-cl0-cl1/summary.txt
build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-rse.log
build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-safety-island-cl0.log
build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-safety-island-cl1.log
build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-secure-console.log
build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-primary-console.log
```

The saved canonical run proves that CL0 reaches SCP-firmware banner output,
configures the SI and AP GIC multiview controllers, initializes
SBISTC/SSU/RAS FFH service, discovers and programs all three NI-710AE
elements, completes CMN-Cyprus discovery/configuration, initializes AP
cluster-control windows, starts AP/CL1 PFDI monitoring, and reaches SMCF data
sampling. CL1 Zephyr boots all four CPUs and reports PFDI agent/service,
network configuration, and `veth_rpmsg: RPMSG Endpoint: ATTACHED`. RSE loads
SI CL1, SI CL0, AP BL2, and RT_0 images, completes RSE-to-SCP SCMI, powers on
AP, and jumps to the TF-M first image slot.

The AP console reaches TF-A BL2, BL31, OP-TEE, U-Boot, Linux, login, root
shell, and the post-login probe. The post-login probe loads `arm_si_rproc`,
`rpmsg_ns`, `virtio_rpmsg_bus`, and `rpmsg_net` with return code 0, attaches
Linux `remoteproc0` to `si-cl1`, creates RPMsg device
`virtio6.ethsi1.-1.1024`, and `ip link show ethsi1` returns 0. The final G4
result records:

```text
verdict: pass
completion_gates.G4: pass
blocker: none
```

## Phase 5: Full-System Equivalence Closure

| ID | Task | Deliverable | Acceptance |
| --- | --- | --- | --- |
| QAP-FULL-050 | Run full live CL0/CL1 boot. | `build/qbox-apollo-fvp/full-live-cl0-cl1/`. | RSE, SI CL0, SI CL1, TF-A, OP-TEE, U-Boot, and Linux all reach required markers. |
| QAP-FULL-051 | Compare full live QBox against FVP. | `comparison.json` and updated summary. | No required FVP boot markers are missing; remaining differences are classified as fidelity gaps. |
| QAP-FULL-052 | Add coverage/audit reporting. | Updated audit script or report section. | Result covers CPU, memory map, interrupts, ATU/ATW, MHU, SCMI, HIPC/RPMsg, PFDI, FMU, SSU, SMCF, boot media, and subsystem logs. |
| QAP-FULL-053 | Document debug workflow. | README/AGENTS updates if workflow changes. | Logs remain first triage; GDB is used after the failing component or handoff is identified. |
| QAP-FULL-054 | Retire or narrow service-model debt. | Updated docs and mode defaults. | Service model remains available for regression, but full live mode is the equivalence target once stable. |
| QAP-FULL-055 | Compare normalized maps against FVP evidence. | `map-comparison.json` in the full live run directory. | QBox AP/RSE/SMD/SI maps and interrupts match FVP-derived logs, generated DTB/DTS, and local source evidence or list reviewed exceptions. |
| QAP-FULL-056 | Add final completion verifier. | `scripts/test/verify_qbox_apollo_fvp_full_completion.py`. | Non-strict mode reports current progress without overclaiming; `--strict-final` fails until G0 through G5 are all proven by saved evidence. |

### Current Phase 5 Evidence

The canonical final evidence bundle passes G5 and the strict final verifier:

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/result.json
build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json
build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json
build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

`comparison.json`, `map-comparison.json`, and `coverage-audit.json` all record
`passed: true`. `final-verification.json` records `verdict: pass`,
`completion_ready: true`, `completion_claim_allowed: true`, and
`overall_gates.G0..G5 == "pass"`.

## Review Checklist

- [x] The proposed new full-system path does not alter the existing direct boot
      contract.
- [x] G0 through G5 gate status is recorded as `pass`, `blocked`, `fail`, or
      `not_run`.
- [x] The artifact resolver uses local Apollo build outputs by default.
- [x] `service-model`, `live-cl1`, and `live-cl0-cl1` modes are explicit.
- [x] Cortex-R82 source support is treated as necessary but not sufficient for
      live SI runtime pass.
- [x] ATU/ATW and SI GIC multi-view behavior are treated as first-class boot
      requirements.
- [x] Every runtime claim has file-backed logs and `result.json` evidence.
- [x] FVP comparison is required before claiming equivalence.
- [x] `scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`
      exits 0 before any final completion report.
- [x] Remaining safety, PFDI, FMU, SSU, SMCF, RAS, reset, power, and diagnostic
      gaps are tracked as fidelity debt.

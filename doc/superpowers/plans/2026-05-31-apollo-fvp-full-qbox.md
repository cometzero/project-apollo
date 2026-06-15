# Apollo FVP Full QBox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development for implementation execution, or
> superpowers:executing-plans when working as a single agent. Keep this file as
> the source of task state by updating checkbox status as each step is completed.

**Goal:** Add a full-firmware Apollo FVP QBox path that integrates RSE,
Safety Island service-model behavior, TF-A, OP-TEE, U-Boot, and Linux around
the existing primary-compute Apollo platform.

**Architecture:** Keep `tools/qbox/platforms/apollo-fvp/conf.lua` as the direct
Linux primary-compute target. Add a separate Apollo full platform derived from
`tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`, with Apollo artifact
resolution, Apollo environment names, file-backed multi-console logs, and a
runner that validates RSE-first boot through Linux post-login probes. Use the
existing Safety Island service model for the first integrated boot, then add
live Safety Island CPU execution as a separate fidelity milestone.

**Tech Stack:** Python 3, Bash, Lua QBox platform config, QBox `platforms-vp`,
SystemC/TLM components, local Apollo build artifacts, Yocto Apollo deploy
fallbacks, and file-backed UART/platform logs.

---

## Success Criteria

- Direct primary-compute boot remains available through
  `scripts/run/run_qbox_apollo_fvp_linux.py`.
- New full boot entrypoint exists:
  `scripts/run/run_qbox_apollo_fvp_full.py`.
- New full platform config exists:
  `tools/qbox/platforms/apollo-fvp/full.lua`.
- `--check-only` validates Apollo local-build firmware artifacts and writes a
  machine-readable `result.json`.
- The full runner can build required QBox targets and launch an RSE-first boot.
- Runtime evidence is written under `build/qbox-apollo-fvp/full-<run-id>/`.
- Safety Island service-model fidelity debt and Cortex-R82 live-CPU dependency
  are documented in QBox project docs.

## Commit Policy

Do not commit as part of this plan unless the user explicitly requests
`$commit-atomic`. Keep changes atomic by task so a later commit can separate
tests, runner/platform implementation, validation docs, and project docs.

## Task 1: Add Apollo Full Runner Tests

**Files:**
- Create `tests/test_run_qbox_apollo_fvp_full.py`
- Create `scripts/run/run_qbox_apollo_fvp_full.py`

- [ ] Create tests that import `scripts/run/run_qbox_apollo_fvp_full.py` through
  `importlib.util.spec_from_file_location`.
- [ ] Test default local-build artifact resolution from
  `build/local-apollo-fvp/deploy/firmware` and
  `build/local-apollo-fvp/deploy/boot`.
- [ ] Test Yocto fallback resolution for
  `build/tmp_baremetal/deploy/images/apollo-fvp/bl2-apollo_fvp.elf` when the
  local deploy ELF is absent.
- [ ] Test that generated QBox environment keys use the
  `QBOX_APOLLO_FULL_` prefix.
- [ ] Test that `--check-only` emits a JSON contract containing all artifact
  paths, log paths, marker group names, and an explicit `passed` field.
- [ ] Run the tests and confirm they fail before implementing the runner API.

Command:

```bash
pytest tests/test_run_qbox_apollo_fvp_full.py -q
```

## Task 2: Implement Apollo Full Artifact Resolver

**Files:**
- Modify `scripts/run/run_qbox_apollo_fvp_full.py`

- [ ] Add frozen dataclasses for firmware, boot, log, and result artifact
  contracts.
- [ ] Add default roots:
  `build/local-apollo-fvp`, `build/local-apollo-fvp/deploy`, and
  `build/tmp_baremetal/deploy/images/apollo-fvp`.
- [ ] Resolve these required files:
  `rse-rom-image.img`, `rse-flash-image.img`, `rse-otp-image.img`,
  `ap-flash-image.img`, `combined_provisioning_message.bin`, and
  `apollo-fvp-local-disk.img`.
- [ ] Resolve `bl2-apollo_fvp.elf` from local deploy first, then Yocto deploy.
- [ ] Add command-line overrides for every artifact path.
- [ ] Add `--check-only` so artifact and environment validation can run without
  launching QBox.
- [ ] Re-run unit tests and confirm they pass.

Commands:

```bash
pytest tests/test_run_qbox_apollo_fvp_full.py -q
python3 scripts/run/run_qbox_apollo_fvp_full.py --check-only
```

## Task 3: Add Apollo Full Lua Platform

**Files:**
- Create `tools/qbox/platforms/apollo-fvp/full.lua`

- [ ] Start from `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` to preserve
  the known-good RSE boot topology.
- [ ] Rename environment variables from `QBOX_RDASPEN_` to
  `QBOX_APOLLO_FULL_`.
- [ ] Keep RSE Cortex-M55, RSE-local memory/peripherals, AP flash, AP ATU,
  AP GIC, AP UART, AP DRAM, AP CPUs, SMD/SI control blocks, MHUv3 paths,
  HIPC/RPMsg service model, PFDI monitor, and file-backed console logging.
- [ ] Keep AP CPUs disabled unless the runner sets
  `QBOX_APOLLO_FULL_ENABLE_AP_CPUS=true`.
- [ ] Keep AP CPUs configured for firmware-chain boot:
  EL3 enabled, EL2 enabled, start-in-reset enabled, and reset vector at AP BL2.
- [ ] Do not modify `tools/qbox/platforms/apollo-fvp/conf.lua`.

Validation commands:

```bash
git -C tools/qbox diff --check
python3 scripts/run/run_qbox_apollo_fvp_full.py --check-only
```

## Task 4: Wire Build And Run Entrypoints

**Files:**
- Extend `local-build.sh`
- Modify `scripts/run/run_qbox_apollo_fvp_full.py`

- [ ] Reuse the required QBox target list from
  `scripts/run/run_qbox_fvp_rd_aspen_rse.py`.
- [ ] Build `platforms-vp`, `remote_cpu`, and required SystemC/TLM component
  targets before runtime unless `--skip-build` is set.
- [ ] Use `./local-build.sh qbox` to build the full-platform dependencies.
- [ ] Keep `--check-only` on the Python runner for preflight validation.
- [ ] Ensure per-run logs are file-backed:
  `qbox-platform.log`, `qbox-rse.log`, `qbox-scp.log`,
  `qbox-secure-console.log`, and `qbox-primary-console.log`.
- [ ] Write `summary.txt` and `result.json` for both check-only and runtime
  modes.

Commands:

```bash
./local-build.sh qbox
python3 scripts/run/run_qbox_apollo_fvp_full.py --check-only
```

## Task 5: Add Map And Artifact Preflight Validation

**Files:**
- Create `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- Modify `scripts/run/run_qbox_apollo_fvp_full.py`

- [ ] Add static checks for the RSE local view, AP host view, SMD window,
  SI access window, AP-RSE MHU windows, AP-SI MHU windows, and CL1 HIPC shared
  memory windows.
- [ ] Fail fast when required firmware artifacts are missing or empty.
- [ ] Include exact resolved paths and file sizes in `result.json`.
- [ ] Include the Safety Island integration mode in `result.json` as
  `service-model`.

Commands:

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/run/run_qbox_apollo_fvp_full.py --check-only
```

## Task 6: Run Bounded Full Boot

**Files:**
- Modify only if runtime evidence exposes a concrete implementation defect.

- [ ] Build local Apollo artifacts if they are stale:

```bash
./local-build.sh build
```

- [ ] Build QBox full-platform dependencies:

```bash
./local-build.sh qbox
```

- [ ] Run a bounded full boot:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --timeout 900 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-initial
```

- [ ] Inspect `result.json`, all UART logs, and `summary.txt`.
- [ ] Classify failures into one of these states:
  `missing-artifact`, `qbox-build-failed`, `rse-boot-blocked`,
  `ap-firmware-blocked`, `linux-boot-blocked`, `post-login-probe-blocked`,
  or `none`.
- [ ] Fix only the first confirmed blocker, then repeat the bounded run.

## Task 7: Compare Against FVP Evidence

**Files:**
- Modify `scripts/analyze/compare_fvp_qbox_rse_logs.py` only if the current comparison
  script cannot accept Apollo log paths.

- [ ] Run the Apollo FVP log capture script for the same local artifacts.
- [ ] Compare RSE boot, RSE-SCP handoff, AP firmware, Linux, and post-login
  marker groups against QBox logs.
- [ ] Save comparison output under the same run directory.
- [ ] Record missing markers in `result.json`.

Expected command shape:

```bash
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp-log-dir build/fvp-boot-logs/<apollo-run> \
  --qbox-log-dir build/qbox-apollo-fvp/full-initial \
  --out build/qbox-apollo-fvp/full-initial/comparison.json
```

## Task 8: Update Project Documentation

**Files:**
- Modify `tools/qbox/platforms/apollo-fvp/README.md`
- Modify `doc/qbox-fvp-emulation-project.md`
- Modify `AGENTS.md` only if the default QBox workflow changes

- [ ] Document the two Apollo QBox modes: direct Linux boot and full firmware
  boot.
- [ ] Document the full runner command, generated logs, artifact defaults, and
  result file format.
- [ ] Document that Stage 1 uses a Safety Island service model.
- [ ] Document the live Safety Island CPU dependency on Cortex-R82-compatible
  QEMU/QBox support.
- [ ] Add the latest validation command and result directory.

Validation commands:

```bash
git diff --check
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_full.py
pytest tests/test_run_qbox_apollo_fvp_full.py -q
```

## Task 9: Live Safety Island Follow-up

This task starts after Stage 1 full boot is stable.

- [ ] Inventory QBox/QEMU CPU support for Cortex-R82 or a documented
  R-profile approximation.
- [ ] Decide whether to add a Cortex-R82-compatible QEMU model or use an
  approximation for early bring-up.
- [ ] Add live SI CL1 Zephyr execution while preserving Stage 1 RPMsg/HIPC
  externally visible behavior.
- [ ] Add live SI CL0 SCP-Firmware execution after CL1 validates the CPU,
  interrupt, memory, and MHU plumbing.
- [ ] Add GDB target documentation for SI CL0 and CL1 once live execution is
  present.

## Review Checklist

- [ ] Direct Apollo Linux boot still works.
- [ ] Full Apollo check-only path resolves local build artifacts.
- [ ] Full Apollo platform uses Apollo env names and does not depend on
  `QBOX_RDASPEN_` variables.
- [ ] Per-subsystem logs are file-backed.
- [ ] RSE boot, AP firmware boot, Linux boot, and post-login probes are tracked
  as separate marker groups.
- [ ] Safety Island service-model scope is explicit in docs and `result.json`.
- [ ] Cortex-R82 live-CPU gap is documented as a fidelity limitation, not hidden
  as an implementation detail.

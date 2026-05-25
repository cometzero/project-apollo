# RSE QBox Current Status Report

Date: 2026-05-25

## Scope

This report summarizes the current `rse-qbox` implementation state for the
active Arm Zena CSS RD-Aspen QBox/FVP equivalence work.

Active baseline from `.config.yaml`:

- `MACHINE = "fvp-rd-aspen"`
- `RD_ASPEN_VARIANT = "cfg2"`
- `PC_CPUS_COUNT_DEFAULT = "4"`
- `ARM_FVP_EULA_ACCEPT = "1"`
- Architecture: baremetal, demos enabled

The workspace root is a kas-composed tree, not a single Git repository. Source
ownership is mainly under `tools/qbox/`, `arm-zena-css/`, and
`sw-ref-stack/`.

## High-Level Status

The RSE-oriented QBox path has reached a substantial functional milestone:

- RSE firmware boot, RSE/SCP handoff markers, measured boot markers, AP boot,
  Linux login, and post-login Linux driver probes have passed in the current
  evidence set.
- A file-backed FVP/QBox marker comparison has passed for the main boot marker
  set.
- The tracked primary-compute coverage audit passes for 19 tracked blocks.

This is not yet FVP-equivalent completion. The remaining gaps are concentrated
in secure-service fidelity, Secure FWU bank/persistence behavior, default-safe
ATU DMI, and replacing service/stub/static-map behavior with fuller hardware
models.

## Implemented Or Runtime-Proven Areas

### RSE-Oriented Platform And Automation

Implemented:

- RSE-oriented platform configuration:
  `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- RSE runner and debug flow:
  `scripts/run_qbox_fvp_rd_aspen_rse.py`
  `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- File-backed per-console logs and `result.json` artifacts.
- GDB bundle generation for QBox host, TF-M/RSE, AP TF-A/OP-TEE/U-Boot/Linux,
  Trusted Services SPs, SCP-Firmware symbols, and SI CL1 Zephyr symbols.

Important caveat: SCP-Firmware currently has source/symbol mapping only. The
active platform uses an SCP service model and does not instantiate a live SCP
CPU GDB target.

### RSE Firmware Boot Path

Implemented or modeled enough for current boot evidence:

- Cortex-M55 boot through QBox `RemoteCPU`.
- NVIC/SCS path inside the M-profile CPU process.
- RSE ROM, ITCM/DTCM aliases, VM, flash, OTP/provisioning image handling.
- RSE file-backed UART logging.
- RSE reset/system-control registers for the observed firmware path.
- RSE ATU translation and fault handling.
- RSE LCM/OTP access with per-run copied OTP writeback and lock-after-
  provision behavior.
- RSE KMU hardware-slot key export from OTP-backed material.
- RSE CC3XX functional crypto surface used by BL1/BL2:
  SHA-256, AES-CTR, AES-ECB, AES-CMAC, and selected PKA/modular arithmetic.
- DMA350 BL1 fill/copy path.
- Strata flash CFI model with read/status/program/erase handling, optional
  backing-file write-through, DMI ranges, and stats.

Evidence:

- `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/result.json`
  reports:
  - `passed: true`
  - `blocker: null`
  - `timed_out: false`
  - post-login probe complete
  - Linux-visible driver patterns true for `arm_si_rproc`, `hipc_ethsi1`,
    `rpmsg`, `smmu_v3`, and `virtio`

### AP/Linux Runtime Surface

Runtime-proven:

- AP firmware boot reaches Linux through the RSE-oriented path.
- Linux reaches login/root prompt in the V004 evidence run.
- Post-login probe completes.
- Driver probe evidence includes:
  - PL011 console
  - SMMUv3
  - virtio
  - remoteproc/RPMsg
  - `hipc_ethsi1`

Evidence:

- `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/`
- `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/coverage-audit.json`

Coverage audit summary:

- `full_coverage_passed: true`
- `implemented_blocks_passed: true`
- `rse_fidelity_labels_passed: true`
- tracked blocks: 19
- implemented failed: 0
- not emulated in this tracked set: 0

Static-map-only tracked blocks remain:

- `sram_scmi_shmem`
- `si_remoteproc_reserved_memory`

### FVP/QBox Marker Comparison

The file-backed V007 comparison passed:

- `build/qbox-fvp-rd-aspen/rse-v007-fvp-qbox-compare-20260525-v1/comparison.json`
  reports `passed: true`.

Fresh FVP verbose reference:

- `build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1/`
- FVP reaches:
  - `RSE to SCP SCMI power on AP succeeded`
  - `Jumping to the first image slot`
  - `Booting Linux on physical CPU`
  - `Linux version 6.18.5-rt3-yocto-preempt-rt`

## Current Fidelity Labels

Current RSE fidelity labels from the V004 runtime result:

| Block | Current label |
| --- | --- |
| `rse_cortex_m55_boot` | `functional-model` |
| `rse_boot_media` | `cfi-strata-flash-partial-model` |
| `rse_atu` | `translation-dmi-model` |
| `rse_cc3xx` | `hash-aes-cmac-modular-pka-model` |
| `rse_dma350` | `functional-fill-copy-model` |
| `rse_lcm` | `otp-backed-register-model` |
| `rse_kmu` | `touched-register-model` |
| `rse_integrity_checker` | `touched-status-model` |
| `rse_sysctrl` | `touched-register-model` |
| `host_si_scr` | `sid-system-cfg-register-model` |
| `rse_scp_endpoint` | `functional-model` |
| `rse_oriented_ap_boot` | `functional-model` |
| `mhuv3` | `temporary-stub` |
| `rse_sacfg` | `static-map-only` |
| `rse_nsacfg` | `static-map-only` |

The labels above are intentionally conservative. Passing Linux boot does not
mean full FVP equivalence for reset, power, diagnostic, error-injection, FWU,
secure-service, or complete IP register behavior.

## Not Yet Implemented Or Not Yet Verified

Open tasks from `doc/spec/rse-qbox/task.md`:

- T019X: Stabilize optional `rse_atu` translated DMI before enabling it by
  default.
- T061: Wire and validate AP secure-world SE-Proxy transport and RSE secure
  service semantics.
- T062: Validate Initial Attestation request path.
- T063: Validate Protected Storage and Internal Trusted Storage paths.
- T064: Validate UEFI variable storage through SMM Gateway and RSE Protected
  Storage beyond the current U-Boot enrollment evidence.
- T070: Model RSE flash A/B image banks.
- T071: Model AP flash A/B FIP banks.
- T072: Model FWU metadata and RSE private metadata storage. Current
  per-run initialization is bring-up plumbing, not full FWU metadata fidelity.
- T074: Verify RSE marker `[INF] Attempting to boot image 1`.
- T075: Verify TF-A marker `Booting with partition FIP_B`.
- T076: Verify writable flash state persists across reboot.
- V038: Investigate remaining Secure FWU bank-selection fidelity.

Additional open fidelity gaps:

- Replace service-modeled SCP with real SI/SCP execution or stronger
  FVP-equivalent evidence.
- Replace service-modeled SI CL1 RPMsg endpoint with real SI CL1 CPU/Zephyr
  data-plane behavior.
- Improve MHUv3 from compatibility/service model toward fuller TRM-equivalent
  PBX/MBX behavior.
- Extend `rse_sysctrl`, `rse_kmu`, `rse_integrity_checker`, PPU/SCR, SACFG,
  NSACFG, and static host windows beyond touched/static behavior.
- Validate PSCI secondary CPU behavior, reset lifecycle, system power/reset,
  FWU reboot flow, and post-reboot bank selection.

## Current Issues And Blockers

### 1. RSE TF-M PS/ITS Flash Writeback Cost

The main current pre-Linux runtime bottleneck is RSE TF-M secure-storage
writeback through the SystemC Strata CFI byte-program path.

Evidence:

- `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/`
- The GDB sample opened RSE/AP ports and reached U-Boot
  `EFI: MM partition ID 0x8006`, but did not reach `Linux version` within the
  bounded sample.
- AP sampled in SE-Proxy waiting on RSE MHU response.
- RSE/TF-M sampled inside ITS/PS flash writeback through
  `Driver_FLASH0_ProgramData()` and `cfi_strataflashj3_program()`.

Quantified flash stats from
`run/rse-strata-stats.json`:

- `program_ops = 246699`
- `read_status_cmds = 493397`
- `write_accesses = 1480192`
- `read_accesses = 776455`
- `backing_write_ops = 200603`

FVP comparison:

- `build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1/` reaches
  `Linux version` under the comparable short verbose reference run.
- Expected first-boot SE-Proxy secure-storage errors appear on FVP too and are
  not by themselves the QBox-specific failure cause.

Current conclusion:

- The remaining short-timeout pre-Linux gap is not AP release or GDB setup.
- The next implementation target is a faithful Strata buffered-program path or
  another semantics-preserving way to reduce firmware-visible CFI transaction
  cost.

### 2. TF-M Strata Write-Buffer Experiment Is Not Runtime-Proven

An experimental TF-M patch is present under `arm-zena-css`:

- `yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-fvp-rd-aspen-src.inc`
  includes `0086-rse-css-aspen-Use-CFI-write-buffer-for-Strata.patch`.
- The untracked patch file adds `nor_buffered_program()` and changes the
  Strata path to use buffered programming.
- Current patch content uses `MAX_PROGRAM_SIZE = 32`.

Known negative evidence from the earlier write-buffer attempt:

- QBox artifact:
  `build/qbox-fvp-rd-aspen/gdb-linux-marker-write-buffer-20260525-v1/`
  stops before `Linux version`.
  RSE is in BL1_1 `boot_platform_error_state + 24`, and AP remains at
  TF-A BL2 entry `0x82000`.
- FVP artifact:
  `build/fvp-boot-logs/write-buffer-tfm-20260525-v1/`
  reaches RSE/SCP handoff and TF-M runtime start, then fails with
  `Partition initialization FAILED in 0x31047cc5` after
  `Creating an empty ITS flash layout.`

Important current-state caveat:

- The patch has since been reduced to 32-byte chunks and TF-M
  `do_patch`, `do_compile`, and `do_deploy` logs show successful task
  completion.
- Full composed `firmware-fvp-rd-aspen` deploy and fresh FVP/QBox runtime
  validation for the 32-byte variant are still pending.

### 3. Secure-Service Post-Login Tests Still Fail

Current status:

- Base RSE-oriented Linux boot can pass.
- Secure-service userspace probes do not pass yet.

Observed failures:

- `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` time out or
  fail to open RPC sessions in QBox secure-service probe artifacts.
- FVP comparison completes IAT/ITS and progresses PS further in the same style
  of bounded probe.
- A prior post-login QBox artifact shows SE-Proxy panic in FWU discovery due
  to a null `update_agent` path.

Current conclusion:

- This is a separate issue from the pre-Linux Strata writeback cost.
- The AP-RSE MHU routing is no longer the only suspect; remaining work is
  secure-service semantics and Trusted Services/FWU provider initialization
  behavior.

### 4. Secure FWU Bank Selection And Persistence Are Open

Implemented FWU plumbing:

- Static FWU artifact inspection helper exists.
- Capsule-on-disk media is detected and validated.
- Runtime `--fwu-probe` can copy the capsule to the EFI update location and
  request reboot.
- AP QEMU reset wiring and secure MMIO attribute preservation were added.
- Strata flash supports per-run backing-file write-through.

Still missing:

- Clean proof of RSE image 1 boot marker.
- Clean proof of TF-A `FIP_B`.
- Clean proof of Trial State.
- Cross-run persisted-state proof using copied writable flash images.
- Full RSE/AP A/B bank and metadata behavior.

## Current Worktree State

`tools/qbox` has broad uncommitted implementation work:

- 40 tracked files modified.
- New untracked component/test trees include:
  - `systemc-components/host_ppu/`
  - `systemc-components/host_scr/`
  - `systemc-components/rse_atu/`
  - `systemc-components/rse_integrity_checker/`
  - `systemc-components/rse_kmu/`
  - `systemc-components/rse_sam/`
  - `systemc-components/strata_flash_j3/`
  - matching tests under `tests/components/`
  - Cortex-M55/AArch64 DMI tests under `tests/qbox/cpu/`

`arm-zena-css` has:

- modified TF-M RD-Aspen source include:
  `yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-fvp-rd-aspen-src.inc`
- untracked TF-M patch:
  `yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/files/tf-m/fvp-rd-aspen/0086-rse-css-aspen-Use-CFI-write-buffer-for-Strata.patch`

`sw-ref-stack` is currently clean.

## Evidence Commands Used For This Report

Commands run:

```bash
sed -n '1,140p' .config.yaml
git -C tools/qbox status --short
git -C arm-zena-css status --short
git -C sw-ref-stack status --short
rg -n "^- \\[ \\] (T019X|T061|T062|T063|T064|T070|T071|T072|T074|T075|T076)|^- \\[ \\] V038|^- \\[x\\] V004|^- \\[x\\] V007|^- \\[x\\] T060|^- \\[x\\] T073" doc/spec/rse-qbox/task.md
jq '{passed, blocker, timed_out, platform_returncode, post_login_complete: .post_login_probe.complete, driver_patterns: .post_login_probe.driver_patterns, fidelity_labels}' build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/result.json
jq '{full_coverage_passed, implemented_blocks_passed, rse_fidelity_labels_passed, counts, static_map_only: [.blocks[] | select(.status=="static_map_only") | .name], rse_fidelity_audit}' build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/coverage-audit.json
jq '{passed}' build/qbox-fvp-rd-aspen/rse-v007-fvp-qbox-compare-20260525-v1/comparison.json
sed -n '1,80p' build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/progress-report.md
cat build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/run/rse-strata-stats.json
sed -n '1,110p' build/qbox-fvp-rd-aspen/gdb-linux-marker-write-buffer-20260525-v1/progress-report.md
rg -n "Booting Linux|Linux version|RSE to SCP SCMI power on AP succeeded|Jumping to the first image slot|Partition initialization FAILED|Creating an empty ITS flash layout" build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1 build/fvp-boot-logs/write-buffer-tfm-20260525-v1
```

No new QBox/FVP runtime validation was launched while writing this report.

## Recommended Next Step

Do not treat the TF-M write-buffer patch as accepted yet. The next safe step is:

1. Regenerate the composed firmware image with the current 32-byte
   write-buffer patch.
2. Run a short FVP verbose check first.
3. Only if FVP passes the TF-M ITS initialization and reaches Linux markers,
   rerun the bounded QBox GDB/Linux-marker path.
4. If FVP still fails, revert or rework the TF-M patch before spending more
   time on QBox-side validation.

# Apollo FVP Yocto FVP/QBox Log Comparison

Date: 2026-06-29

## Scope

This report compares the `apollo-fvp` Yocto image boot logs from:

- FVP path: `./run_fvp.sh`
- QBox path: `./run_qbox_yocto.sh`

The newest `./run_fvp.sh` tmux artifact under
`build/fvp-tmux/apollo-fvp-20260629-234710/` did not contain a complete
U-Boot/Linux console capture: `uarts/u_boot_linux.log` was only 642 bytes.
For the detailed U-Boot/Linux comparison, this report therefore uses the
complete FVP log-backed boot run below, generated from the same Yocto
`nexios-image-apollo-fvp-20260629133020` deploy artifacts.

## Evidence Set

| Role | Artifact | Result | Notes |
| --- | --- | --- | --- |
| FVP baseline | `build/fvp-boot-logs/apollo-fvp-pc4-20260629-224322/` | Pass | Complete log-backed FVP boot. Login prompt and post-login root shell observed. |
| QBox latest failing run | `build/qbox-apollo-fvp/yocto-apollo-fvp-20260629-232339/` | Blocked | Booted into Linux but did not reach login. Runner exited with `child_failed:120`. |
| QBox latest passing run | `build/qbox-apollo-fvp/yocto-apollo-fvp-20260629-225639/` | Pass | Same Yocto rootfs image. Login and post-login probe succeeded. Used to classify common QBox differences. |
| FVP latest tmux run | `build/fvp-tmux/apollo-fvp-20260629-234710/` | Incomplete evidence | Primary U-Boot/Linux log was too short for full comparison. |

Input image evidence:

| Path | Value |
| --- | --- |
| Yocto fvpconf | `build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp-20260629133020.fvpconf` |
| Yocto rootfs | `build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp-20260629133020.wic` |
| Machine | `apollo-fvp` |
| Configured PC CPU count | `PC_CPUS_COUNT_DEFAULT = "4"` |

## 2026-06-30 Fix Verification

The sections below preserve the original 2026-06-29 comparison and root-cause
classification. The QBox-specific guest-visible errors called out there were
retested after the QBox platform and runner fixes with this artifact:

| Role | Artifact | Result | Notes |
| --- | --- | --- | --- |
| QBox fixed run | `build/qbox-apollo-fvp/yocto-apollo-fvp-fix-20260630-010029/` | Pass | `result.json` reports `verdict = pass`, `child_returncode = 0`, `ap_cpus = 4`, `expected_ap_cpus = 4`. |

Resolved differences:

| Area | Original QBox-only evidence | Fixed-run evidence |
| --- | --- | --- |
| U-Boot FWU / FF-A | `FWU_DISCOVER: FF-A error -125`, update-agent init failure | Absent. QBox now reports `FWU: ABI version 1.0 detected`, `FWU: System booting in Regular State`, and `FWU: ExitBootServices: Booting in regular state`, matching the FVP FWU state. |
| Secure FWU query | `psa_fwu_query` failure and secure partition panic | Absent. No `psa_fwu_query` or `SP panicked` lines are present in the fixed QBox run. |
| GIC SPI count | `GICv3: 512 SPIs implemented` | QBox now reports `GICv3: 960 SPIs implemented`, matching FVP. |
| SCMI protocol 19 | `SCMI protocol 19 not implemented` | Absent. SCMI Performance protocol `0x13` is advertised and provides CPU OPP/level responses. |
| SCMI cpufreq | CPU OPP registration failures and later notifier warning while exercising protocol 19 | Absent. No `failed to add opps`, `scmi-cpufreq`, or `Protocol:13 - Events Registration Failed` lines are present. |
| Console automation | U-Boot `Unknown command '[28'` / `Unknown command '89R'` | Absent. Terminal cursor-position response lines are filtered before UART injection. |
| QBox CPU count | Platform default printed `ap cpus: 16` for the Yocto profile | Fixed runner prints `ap cpus: 4`; `result.json` confirms `ap_cpus = 4`. |

Still different but not a fixed-run error:

| Area | FVP | QBox fixed run | Classification |
| --- | --- | --- | --- |
| GICv4.1 feature text | FVP prints DirectLPI/RVPEID and GICv4.1 mode lines. | QBox initializes GICv4 and enables GICv4 support, but does not print the same DirectLPI/GICv4.1 feature text. | Residual fidelity difference, not a boot or guest error in this evidence set. |
| SMMU capability surface | FVP reports 52-bit IAS/OAS and larger queues. | QBox still reports the smaller `mmu720ae` capability surface. | Residual model fidelity gap; no fixed-run boot blocker observed. |
| SMMGW / secure-storage / FF-A notification warnings | Present in FVP. | Present in QBox fixed run. | FVP-common/documented RD-Aspen warnings, not QBox-only failures. |

## Summary

| Domain | FVP Baseline | QBox Observation | Assessment |
| --- | --- | --- | --- |
| RSE / TF-M | BL1_1, BL1_2, BL2 validation, AP power-on, and first image jump all observed. | Same functional boot milestones observed. | No QBox-only RSE error found in compared logs. |
| Safety Island CL0 | SCP firmware initializes and completes module initialization. | Same major initialization markers observed. | No QBox-only CL0 error found in compared logs. |
| Safety Island CL1 | Zephyr boots and secondary CPU cores are reported. | Same major Zephyr markers observed. | No QBox-only CL1 error found in compared logs. |
| Secure console / OP-TEE | OP-TEE boots with known SMMGW and secure-storage warnings. | Adds firmware update query failure and secure partition panic. | QBox-specific secure-world difference; present even in the passing QBox run. |
| U-Boot FWU / FF-A | U-Boot discovers MM partition, detects FWU ABI, selects slot A, and exits boot services in regular state. | FWU discovery through FF-A fails, memory reclaim fails, and update-agent init fails. | QBox-specific U-Boot FF-A/FWU difference; present even in the passing QBox run. |
| Linux kernel | Linux boots, FF-A driver discovers firmware, GICv4.1/DirectLPI and 52-bit SMMU capability are reported. | Linux boots, FF-A driver also discovers firmware, but GIC/SMMU/SCMI capability differs materially. | QBox model exposes a different interrupt, SMMU, and SCMI capability surface. |
| User space | FVP baseline reaches login and root shell. | Latest QBox run did not reach login, but the previous QBox run did. | Latest failure is runtime/runner-blocking, not a universal QBox boot failure. |
| QBox platform log | Not applicable. | QBox emits address-map shadow warnings and reports `ap cpus: 16`. | QBox-only model diagnostics to track separately from guest logs. |

## QBox-Only Or Changed Errors

| Severity | Domain | QBox Evidence | FVP Baseline | Interpretation |
| --- | --- | --- | --- | --- |
| High | U-Boot FWU / FF-A | `FWU_DISCOVER: FF-A error -125` | FVP reports `FWU: ABI version 1.0 detected`. | QBox does not match FVP's U-Boot FWU discovery path through FF-A. |
| High | U-Boot FWU / FF-A | `FWU: FF-A memory reclaim failure (err: -13)` | No matching FVP error. | Secure-world FF-A memory sharing/reclaim behavior differs. |
| High | U-Boot FWU / FF-A | `FWU: Update agent init failed, ret = -125` | FVP selects slot A and continues regular FWU state. | U-Boot update-agent initialization fails only on QBox. |
| Medium | Secure console / SE proxy | `psa_fwu_query:62 failed to psa_call: -134` | No matching FVP error. | QBox secure partition path cannot query FWU state through PSA call. |
| Medium | Secure console / OP-TEE | `abort in User mode (TA will panic)` and `SP panicked with code 0xdeadbeef` | FVP does not show this panic. | QBox triggers a secure partition panic during secure-world service calls. |
| Medium | Linux interrupt model | QBox reports `GICv3: 512 SPIs implemented`. | FVP reports `GICv3: 960 SPIs implemented` and GICv4.1 features. | QBox interrupt-controller model is not exposing the same ITS/GIC capability set. |
| Medium | Linux SMMU model | QBox reports `ias 48-bit, oas 48-bit (features 0x00000304)`. | FVP reports `ias 52-bit, oas 52-bit (features 0x01fcdfcf)`. | QBox SMMU feature surface is substantially smaller than FVP. |
| Low | SCMI | QBox reports `SCMI protocol 19 not implemented`. | FVP does not report this line. | QBox SCMI server is intentionally or accidentally missing protocol 19. |
| Low | QBox runner / console automation | Latest QBox run shows `Unknown command '[28'` and `Unknown command '89R'` in U-Boot. | FVP and QBox pass runs also show some shell escape artifacts later. | Terminal status-response bytes can leak into the guest console and should be filtered by the runner. |
| High | Runtime result | Latest QBox run ends with `child_failed:120` before login. | FVP baseline reaches login/root shell. | Latest QBox run is blocked after Linux boot. A previous QBox run with the same image passed, so this is not deterministic image failure. |

## U-Boot And FF-A

| Checkpoint | FVP Baseline | QBox Latest Failing Run | QBox Passing Run |
| --- | --- | --- | --- |
| U-Boot starts | `U-Boot 2026.01-rc4 ... apollo_fvp` | Same U-Boot version banner observed. | Same U-Boot version banner observed. |
| EFI MM partition | `EFI: MM partition ID 0x8006` | `EFI: MM partition ID 0x8006` | `EFI: MM partition ID 0x8006` |
| FWU discovery | `FWU: ABI version 1.0 detected` | `FWU_DISCOVER: FF-A error -125` | `FWU_DISCOVER: FF-A error -125` |
| FWU state | `FWU: System booting in Regular State` | Update-agent initialization fails. | Update-agent initialization fails. |
| Boot slot | `auto-ad-nexios: selected slot A` | No equivalent successful FWU slot-selection path in the failing section. | No equivalent successful FWU slot-selection path in the failing section. |
| EFI runtime variables | No QBox-style error in compared FVP log. | `Can't populate EFI variables. No runtime variables will be available` | Same style of limitation observed. |
| Linux handoff | `Booting Linux...` | `Booting Linux...` | `Booting Linux...` |

The U-Boot FF-A/FWU difference is common to both the latest failing QBox run
and the latest passing QBox run. It should be treated as a real QBox/FVP
behavioral mismatch, even though it is not by itself sufficient to prevent all
QBox boots from reaching login.

## Secure Console And OP-TEE

| Checkpoint | FVP Baseline | QBox Observation | Assessment |
| --- | --- | --- | --- |
| OP-TEE boot | OP-TEE boots and prints the expected insecure-configuration warnings. | Same broad OP-TEE boot path observed. | Baseline OP-TEE startup is comparable. |
| SMMGW logging service | FVP shows logging service discovery failure and falls back to console log. | QBox also shows SMMGW direct-request errors. | Shared limitation or expected service absence. |
| Secure storage remove | FVP reports secure-storage IPC remove failures with `-140`. | QBox reports the same class of secure-storage IPC remove failure. | Shared or non-fatal warning. |
| FWU query | No matching FVP error. | QBox reports `psa_fwu_query` failure with `-134`. | QBox-specific secure-world/FWU issue. |
| Secure partition panic | No matching FVP panic. | QBox reports a user-mode data abort and SP panic `0xdeadbeef`. | QBox-specific secure partition failure; present even in the passing QBox run. |

## RSE And Safety Island

| Domain | FVP Markers | QBox Markers | Difference |
| --- | --- | --- | --- |
| RSE TF-M BL1/BL2 | `Starting TF-M BL1_1`, `Jumping to BL1_2`, BL2 validation success. | Same markers observed. | FVP capture repeats the BL1_1 banner more often, but QBox reaches the same milestones. |
| RSE AP power-on | `RSE to SCP SCMI power on AP succeeded` | Same marker observed. | No QBox-only error found. |
| RSE image handoff | `Jumping to the first image slot` | Same marker observed. | No QBox-only error found. |
| Safety Island CL0 | SCP firmware initializes and completes module initialization. | Same major markers observed. | No QBox-only error found. |
| Safety Island CL1 | Zephyr boots and reports secondary CPU cores. | Same major markers observed. | No QBox-only error found. |

Both FVP and QBox RSE logs include the same TF-M built-in key-loader platform
warnings. They do not appear to be a QBox-only regression in this evidence set.

## Linux Kernel Model Surface

| Area | FVP Baseline | QBox Observation | Impact |
| --- | --- | --- | --- |
| FF-A kernel driver | `ARM FF-A: Driver version 1.2`; firmware version 1.2 found; notification setup fails with `-95`. | Same kernel FF-A driver and firmware-version lines observed. | Kernel-level FF-A discovery is closer than U-Boot FWU behavior. |
| GIC SPIs | `GICv3: 960 SPIs implemented` | `GICv3: 512 SPIs implemented` | QBox interrupt topology is smaller than FVP. |
| GICv4 / DirectLPI | FVP reports DirectLPI, GICv4.1 mode, virtual CPU allocation, and GICv4 support. | QBox does not report the same GICv4/DirectLPI lines. | Potential functional gap for advanced ITS/vLPI behavior. |
| ITS collections | FVP allocates `32768 Interrupt Collections`. | QBox allocates `8192 Interrupt Collections`. | Capability and scale differ. |
| SMMU addressing | FVP reports 52-bit input/output address size and feature mask `0x01fcdfcf`. | QBox reports 48-bit input/output address size and feature mask `0x00000304`. | QBox SMMU model is less capable than FVP. |
| SMMU queues | FVP reports command/event queue sizes `262144` and `131072`. | QBox reports command/event queue sizes `256` and `256`. | Queue capacity differs materially. |
| SCMI identity | FVP reports `arm:arm` firmware version `0x2100000`. | QBox reports `QBox:RD-Aspen` firmware version `0x1`. | Expected identity difference, but useful for log comparisons. |
| SCMI protocol coverage | No `protocol 19 not implemented` in compared FVP log. | QBox reports `SCMI protocol 19 not implemented`. | Missing QBox SCMI protocol coverage. |
| Extra virtio disks | FVP comparison log shows zero-size `vdc`/`vdd` devices. | QBox latest failing run shows two 64 MiB virtio disks. | QBox runner/model exposes different block-device backing for extra disks. |

## Runtime Result Comparison

| Run | Linux Boot | Login Prompt | Post-Login Probe | Final Verdict |
| --- | --- | --- | --- | --- |
| FVP baseline `apollo-fvp-pc4-20260629-224322` | Yes | Yes | Yes, root shell reached. | Pass |
| QBox latest failing `yocto-apollo-fvp-20260629-232339` | Yes | No | Not sent. | Blocked, `child_failed:120` |
| QBox latest passing `yocto-apollo-fvp-20260629-225639` | Yes | Yes | Yes. | Pass |

The passing QBox post-login probe reported:

| Probe | Result |
| --- | --- |
| CPU possible/present/online | `0-3` |
| `/proc/cpuinfo` processor count | `4` |
| Safety Island CL1 remoteproc state | `attached` |
| `rpmsg_ns` module probe | `0` |
| `virtio_rpmsg_bus` module probe | `0` |
| `rpmsg_net` module probe | `0` |
| `ethsi1` link check | `0` |
| `systemctl --failed` | `0 loaded units listed` |

This confirms that the same QBox Yocto boot path can pass with the current
image, despite the persistent FF-A/FWU and secure-world differences above.

## QBox Platform Diagnostics

| Diagnostic | Evidence | Assessment |
| --- | --- | --- |
| AP CPU count in QBox platform | `ap cpus: 16` in `qbox-platform.log` | Guest Linux is still limited to 4 CPUs by the boot configuration/probe. The platform-side CPU-count reporting differs from the active guest CPU count. |
| Address-map shadow warnings | Several `addressMap: Region ... shadowed` warnings. | QBox-only model wiring diagnostics. They should be reviewed for accidental overlapping regions, but this evidence does not prove they caused the latest boot block. |
| SystemC/QBox platform identity | QBox reports SystemC 3.0.2 and Apollo QVP config. | Expected QBox-only runner output, not directly comparable to FVP guest UART logs. |

## Notes And Next Steps

1. The strongest QBox/FVP guest-visible mismatch is U-Boot FWU over FF-A:
   QBox fails `FWU_DISCOVER`, FF-A memory reclaim, and update-agent
   initialization while FVP completes FWU discovery and selects slot A.
2. The secure-console panic is also QBox-specific and appears in the passing
   QBox run, so it should be fixed or consciously documented as a non-fatal
   compatibility gap.
3. The Linux kernel exposes clear QBox model-surface differences in GIC,
   ITS/GICv4, SMMU, and SCMI. These are not necessarily boot blockers, but
   they are fidelity gaps relative to FVP.
4. The latest QBox failure is not deterministic for this image: an earlier
   run with the same Yocto rootfs reached login and passed the post-login
   probe.
5. Both FVP/QBox automation can leak terminal status-response bytes into the
   guest console. The QBox latest failing run leaked bytes into U-Boot before
   boot, so the runner should filter terminal responses before sending guest
   input.

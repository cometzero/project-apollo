# QBox Yocto Failure Root-Cause Analysis

Date: 2026-06-29

## Scope

This report analyzes the root causes behind the QBox-specific failures and log
differences observed while running the `apollo-fvp` Yocto image with:

- FVP path: `./run_fvp.sh`
- QBox path: `./run_qbox_yocto.sh`

It builds on the log comparison in
`doc/qbox-fvp-yocto-log-comparison-2026-06-29.md` and focuses on source and
documentation evidence.

## Evidence Set

| Role | Artifact | Result | Notes |
| --- | --- | --- | --- |
| FVP baseline | `build/fvp-boot-logs/apollo-fvp-pc4-20260629-224322/` | Pass | Complete log-backed FVP boot. Login prompt reached. |
| QBox passing run | `build/qbox-apollo-fvp/yocto-apollo-fvp-20260629-225639/` | Pass | Same Yocto rootfs image. Login and post-login probe completed. |
| QBox blocked run | `build/qbox-apollo-fvp/yocto-apollo-fvp-20260629-232339/` | Blocked | Linux boot marker reached, login prompt not reached. `qbox-run.status = 120`. |
| Active Yocto config | `build/conf/local.conf` | `apollo-fvp` | `PC_CPUS_COUNT_DEFAULT = "4"`, `RD_ASPEN_VARIANT = "cfg2"`. |

## 2026-06-30 Resolution Update

The original root-cause analysis below identified the QBox platform and runner
gaps from the 2026-06-29 logs. Those high-confidence causes were fixed and
validated with:

| Artifact | Result |
| --- | --- |
| `build/qbox-apollo-fvp/yocto-apollo-fvp-fix-20260630-010029/result.json` | `verdict = pass`, `child_returncode = 0` |
| `build/qbox-apollo-fvp/yocto-apollo-fvp-fix-20260630-010029/qbox-primary-console.log` | FWU ABI/regular-state path present; `GICv3: 960 SPIs implemented`; `smp: Brought up 1 node, 4 CPUs` |
| `build/qbox-apollo-fvp/yocto-apollo-fvp-fix-20260630-010029/qbox-secure-console.log` | No SE-Proxy FWU panic; only FVP-common SMMGW and first-boot secure-storage warnings remain |

Fix summary:

| Area | Root cause | Implemented fix | Fixed-run result |
| --- | --- | --- | --- |
| U-Boot FWU / FF-A | QBox RSE PSA FWU service returned unsupported for `TFM_FWU_QUERY`; the first implementation used the wrong 60-byte component-info ABI. Apollo TS/TF-M uses a 44-byte `psa_fwu_component_info_t`. | `mhu320ae` now models `TFM_FIRMWARE_UPDATE_SERVICE_HANDLE` / `TFM_FWU_QUERY` with the Apollo 44-byte FWU component-info layout and CFG2 flash locations. | `FWU_DISCOVER`, `FF-A error -125`, update-agent init failure, `psa_fwu_query`, and `SP panicked` are absent. |
| SCMI protocol 19 / cpufreq | QBox did not advertise or implement SCMI Performance protocol `0x13`, while the Apollo DT CPU nodes reference `firmware/scmi/protocol@13` clock domain `0`. A partial response with zero domains still caused event/cpufreq failures. | `mhu320ae` now advertises Base/Power/System/Performance and implements Performance v4 protocol attributes, one CPU performance domain, OPP description, limits, level set/get, and notification enable handling. | `SCMI protocol 19 not implemented`, `failed to add opps`, `scmi-cpufreq`, and `Protocol:13 - Events Registration Failed` are absent. |
| GIC SPI count | Apollo QBox AP GIC config exposed only 512 SPIs. | `ap_compute.lua` now sets AP GIC revision 4 and 960 SPIs. | QBox reports `GICv3: 960 SPIs implemented`, matching FVP for SPI count. |
| Tmux console injection | The primary tmux pane could feed terminal cursor-position responses back into U-Boot. | `run_qbox_apollo_fvp_full_tmux.sh` filters terminal CPR/DSR response lines before writing to the UART FIFO. | U-Boot `Unknown command '[28'` / `89R` artifacts are absent. |
| AP CPU count | `run_qbox_yocto.sh` left the platform default at 16 AP CPUs for a Yocto profile configured for 4. | The runner derives `QBOX_APOLLO_NUM_CPUS` from `build/conf/local.conf` and passes it through tmux. | Launch output and `result.json` both report 4 AP CPUs. |

Residual model gaps after the fix:

| Area | Status |
| --- | --- |
| GICv4.1 / DirectLPI text | QBox now initializes and enables GICv4, but it still does not print FVP's DirectLPI/GICv4.1 feature string. No fixed-run guest error was observed from this difference. |
| SMMU capability surface | The `systemc-mmu720ae` backend still advertises a smaller 48-bit/queue-size feature surface than FVP. This remains a fidelity gap outside the fixed boot blockers. |
| FVP-common warnings | `ARM FF-A: Notification setup failed -95`, SMMGW logging-service `-4`, and first-boot secure-storage `-140` are still present, but they are also present in the FVP baseline and are documented RD-Aspen limitations. |

## Root-Cause Summary

| Area | QBox symptom | Root cause | Confidence | Fix direction |
| --- | --- | --- | --- | --- |
| U-Boot FWU/FF-A | `FWU_DISCOVER: FF-A error -125`, `FWU: Update agent init failed` | The FF-A call reaches a QBox secure-world/FWU path that is not FVP-equivalent. U-Boot is only reporting the failed FF-A direct request; the failure originates below U-Boot in the TS SE-Proxy/RSE FWU service path. | High | Fix QBox secure FWU provider/RSE FWU service modeling before changing U-Boot. |
| SE-Proxy FWU panic | `psa_fwu_query ... -134`, OP-TEE SP panic `0xdeadbeef` | Existing GDB evidence maps the panic to Trusted Services FWU provider code calling `update_agent_discover(this_instance->update_agent, ...)` while `update_agent` is null. Current TS source has no null guard before dereferencing `update_agent->interface`. | High | Ensure SE-Proxy FWU provider has a valid update agent under QBox, or model the FWU service path correctly. |
| Secure-storage latency/timeouts | Runs can stall before login or secure-service tests can timeout | Prior QBox debug evidence shows AP SE-Proxy waiting on RSE Protected Storage/ITS flash operations, with MHU request/response pairing mostly intact. The bottleneck is TF-M PS/ITS flash workload on the QBox Strata CFI path, not a dead MHU route. | Medium | Continue optimizing or accurately shortcutting RSE PS/ITS flash storage while preserving semantics. |
| SCMI protocol 19 | `arm-scmi ... SCMI protocol 19 not implemented` | QBox `mhu320ae` SCMI responder implements only Base, Power Domain, System Power, and PFDI monitor. Protocol `0x13` is not implemented and the Base protocol list advertises only Base. | High | Add protocol `0x13` support or align advertised protocol list with FVP expectations. |
| GIC capability mismatch | QBox reports 512 SPIs; FVP reports 960 SPIs plus DirectLPI/GICv4 lines | Apollo QBox Lua config sets AP GIC `num_spi = 512`; the QEMU-backed GIC wrapper passes that to QEMU as `num-irq = p_num_spi + NUM_PPI`. | High | Raise QBox AP GIC SPI count and model/enable missing GICv4/DirectLPI behavior if fidelity requires it. |
| SMMU capability mismatch | QBox reports 48-bit IAS/OAS and queue size 256; FVP reports 52-bit and much larger queues | QBox defaults to `systemc-mmu720ae`; its ID registers expose only S1P/coherency/AArch64 translation, 48-bit output address size, and `IDR1` queue log2 size 8. | High | Extend `mmu720ae` feature/ID model or select a backend matching FVP capability. |
| Console command injection | QBox blocked run shows `Unknown command '[28'` and `Unknown command '89R'` in U-Boot | The tmux primary-console pane tails guest output to the real terminal and also reads stdin for UART input. U-Boot prints `ESC[6n`; the terminal answers with cursor position bytes, and the pane feeds those bytes back into the UART FIFO. | High | Filter terminal CPR/DSR escape responses in `run_qbox_apollo_fvp_full_tmux.sh` before writing to the UART FIFO. |
| AP CPU count mismatch | QBox platform log prints `ap cpus: 16`, guest probe reports 4 CPUs | QBox platform default is `QBOX_APOLLO_NUM_CPUS=16`; Yocto boot/probe limits the guest-visible CPUs to 4. | Medium | Align QBox platform CPU count with active Yocto `PC_CPUS_COUNT_DEFAULT` when running this profile. |

## U-Boot FWU/FF-A

### Observed Difference

| Run | Evidence |
| --- | --- |
| FVP | `terminal_ns_uart0_5004.log:20`: `FWU: ABI version 1.0 detected` |
| QBox pass | `qbox-primary-console.log:15`: `FWU_DISCOVER: FF-A error -125`; line 17 memory reclaim failure |
| QBox blocked | Same FWU discovery failure at `qbox-primary-console.log:15-17` |

The same FWU failure appears in both the passing and blocked QBox runs, so it
is a persistent fidelity gap, not the sole reason that every QBox run fails to
boot.

### Source Trace

U-Boot initializes the PSA FWU update agent in
`hsoc-stack/components/primary_compute/u-boot/lib/fwu_updates/fwu_arm_psa.c`.

The call chain is:

1. `efi_fill_image_desc_array()` calls `fwu_agent_init()` if the FWU agent is
   not initialized.
2. `fwu_agent_init()` finds the FF-A bus, discovers the Trusted Services FWU SP,
   shares a 4 MiB communication buffer, calls `fwu_discover()`, then reads the
   FWU directory.
3. `fwu_discover()` sets function ID `FWU_DISCOVER`.
4. `fwu_invoke_svc()` calls `ffa_sync_send_receive(g_dev, g_fwu_sp_id, ...)`.
5. If that FF-A direct request fails, U-Boot logs `<svc>: FF-A error <ret>`.

Relevant source evidence:

| File | Lines | Evidence |
| --- | --- | --- |
| `u-boot/lib/fwu_updates/fwu_arm_psa.c` | 306-315 | `FWU_DISCOVER` is sent via `ffa_sync_send_receive`; non-zero return is logged as `FF-A error`. |
| `u-boot/lib/fwu_updates/fwu_arm_psa.c` | 368-383 | `fwu_discover()` calls `fwu_invoke_svc()` and returns the FF-A error. |
| `u-boot/lib/fwu_updates/fwu_arm_psa.c` | 1051-1065 | The memory reclaim error is cleanup after the prior failure. |
| `u-boot/lib/fwu_updates/fwu_arm_psa.c` | 1286-1337 | `fwu_agent_init()` fails if `fwu_discover()` fails. |
| `u-boot/lib/fwu_updates/fwu_arm_psa.c` | 1372-1377 | The visible log `FWU: Update agent init failed` is produced here. |
| `u-boot/include/fwu_arm_psa.h` | 26-37, 61-63, 81-94 | 4 MiB FWU shared buffer, TS FWU service UUID, TS RPC IDs, and FWU ABI IDs. |

This means the U-Boot log is a symptom. U-Boot has reached the correct
high-level FWU code path, then the secure-world FWU request fails.

### Architecture Expectation

`arm-zena-css/documentation/design/secure_firmware_update.rst` says the
expected CFG2 Secure FWU path is:

1. U-Boot detects and authenticates the capsule.
2. U-Boot transfers image data to the Trusted Services SE-Proxy FWU proxy using
   the Platform Secure FWU ABI.
3. The Trusted Services FWU proxy forwards requests to RSE using the PSA FWU
   API.
4. The RSE FWU Secure Partition writes the update bank and updates FWU metadata.

The QBox failure is therefore in the modeled or connected equivalent of the
TS SE-Proxy FWU proxy/RSE FWU service path, not in U-Boot's FWU frontend.

## SE-Proxy FWU Panic

The QBox secure console reports:

| Run | Evidence |
| --- | --- |
| QBox pass | `qbox-secure-console.log:233`: `psa_fwu_query:62 failed to psa_call: -134`; line 257 SP panic `0xdeadbeef` |
| QBox blocked | Same `psa_fwu_query` and SP panic at `qbox-secure-console.log:233` and `:257` |
| FVP | No matching panic in the compared FVP secure console |

Trusted Services source confirms the fragile dereference:

| File | Lines | Evidence |
| --- | --- | --- |
| `trusted-services/components/service/fwu/common/update_agent_interface.c` | 10-15 | `update_agent_discover()` dereferences `update_agent->interface` without checking whether `update_agent` itself is null. |
| `trusted-services/components/service/fwu/provider/fwu_provider.c` | 99-107 | `discover_handler()` calls `update_agent_discover(this_instance->update_agent, ...)`. |

Existing project GDB evidence in `doc/qbox-fvp-rd-aspen-gdb-debug.md`
confirms the same failure mode:

| Lines | Evidence |
| --- | --- |
| 2916-2926 | Linux secure-service probe reaches userspace, then secure console shows SE-Proxy data abort and SP panic. |
| 2928-2932 | Fault address maps to `update_agent_discover()` line 12. |
| 2951-2958 | `0x16a4c` maps to `discover_handler()` line 106, and `this_instance->update_agent` is null. |
| 2961-2968 | FVP also has first-boot storage warnings but does not panic, so this is QBox-specific. |

The current QBox `-134` also aligns with the QBox model constants:
`tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h` defines
`PSA_ERROR_NOT_SUPPORTED = -134`. The current AP-RSE MHU configuration uses the
`rse-ps-proxy` protocol by default and the model handles Protected Storage and
Measured Boot requests, but unrecognized service handles or operations return
`PSA_ERROR_NOT_SUPPORTED`.

This supports the conclusion that QBox does not currently provide an
FVP-equivalent FWU provider/update-agent path to SE-Proxy.

## Expected Secure-World Logs That Are Not Root Causes

Some scary-looking logs are expected for RD-Aspen and should not be counted as
QBox failures by themselves.

| Log | Documentation | Classification |
| --- | --- | --- |
| `ARM FF-A: Notification setup failed -95, not enabled` | `arm-zena-css/documentation/releasenotes.rst:189-203` says OP-TEE v4.7 lacks FF-A notification pending and schedule receiver interrupts; notification setup is not mandatory and AP FF-A communication is not affected. | Expected limitation. |
| SMMGW logging service discovery `sp_msg_send_direct_req(): error -4` | `releasenotes.rst:206-222` says TS Logging Service is not enabled and SMM Gateway falls back to console log. | Expected limitation. |
| `secure_storage_ipc_remove ... -140` on first boot | `releasenotes.rst:275-297` says this is normal when first-boot SMM variable indexes do not yet exist. | Expected first-boot behavior. |

The QBox-specific secure-world problem is the FWU query failure plus SE-Proxy
panic, not the expected `-95`, `-4`, or first-boot `-140` logs.

## Secure Storage And No-Login Runs

The blocked QBox run reached Linux but not the login prompt:

| Evidence | Value |
| --- | --- |
| Parent status | `result.json`: `blocker = child_failed:120` |
| Child status | `rd-aspen-summary.txt`: `blocker = qbox_post_login_probe_not_reached` |
| Runtime elapsed | `rd-aspen-summary.txt`: `runtime_elapsed_s = 41.110` |
| Linux marker | `primary_linux_cpu` seen at 35.534 seconds |
| Login marker | `apollo-fvp login:` not seen |

This failure is not deterministic for the image: the earlier QBox run
`yocto-apollo-fvp-20260629-225639` reached login and passed the post-login
probe with the same Yocto rootfs.

For longer secure-service stalls, existing debug evidence points at RSE
Protected Storage and ITS flash workload:

| File | Lines | Evidence |
| --- | --- | --- |
| `doc/qbox-fvp-rd-aspen-gdb-debug.md` | 3278-3288 | AP sampled in SE-Proxy `secure_storage_ipc_set()` while RSE/TF-M is in ITS/PS flash writeback. |
| `doc/qbox-fvp-rd-aspen-gdb-debug.md` | 3290-3307 | Strata flash counters show hundreds of thousands of byte-program/status-poll operations. |
| `doc/qbox-fvp-rd-aspen-gdb-debug.md` | 3309-3313 | MHU trace found matched responses and one in-flight request, indicating slow flash work rather than dead MHU routing. |
| `doc/spec/rse-qbox/task.md` | 862-908 | T061 remains open above the AP-RSE MHU bridge: secure-service semantics, SE-Proxy panic, and PS/ITS flash work. |
| `doc/spec/rse-qbox/task.md` | 1048-1065 | UEFI variable storage remains open; FVP also lacks `uefi-test`, so image content and expected startup warnings are not QBox-only. |

So there are two separate issues:

1. The current blocked run has a short no-login timeout and console-injection
   evidence.
2. The broader secure-service path still has known FWU/PS/ITS fidelity and
   performance gaps.

## SCMI Protocol 19

QBox logs:

```text
arm-scmi arm-scmi.1.auto: SCMI protocol 19 not implemented
```

The source cause is direct:

| File | Lines | Evidence |
| --- | --- | --- |
| `tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h` | 82-85 | Only SCMI Base `0x10`, Power Domain `0x11`, System Power `0x12`, and PFDI Monitor `0x90` are declared. |
| Same file | 1008-1032 | Base `DISCOVER_LIST_PROTOCOLS` response advertises only Base. |
| Same file | 1163-1204 | `respond_scmi()` switches only on the implemented protocols; everything else returns `SCMI_ERR_SUPPORT`. |

SCMI protocol 19 is `0x13`, so QBox currently returns unsupported. This is a
QBox service-model coverage gap, not a Linux driver bug.

## GIC And SMMU Capability Mismatch

### GIC

| Run | Evidence |
| --- | --- |
| FVP | `terminal_ns_uart0_5004.log:123-127`: 960 SPIs, DirectLPI, GICv4 feature lines |
| QBox | `qbox-primary-console.log:218-221`: 512 SPIs, no DirectLPI/GICv4 lines |

The source cause for the SPI count is explicit:

| File | Lines | Evidence |
| --- | --- | --- |
| `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua` | 243-261 | AP GIC model is `arm_gicv3`, `has_lpi = true`, `num_spi = 512`. |
| `tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h` | 73-89 | Wrapper has `p_num_spi` and allocates `spi_in` from that value. |
| Same file | 104-112 | Wrapper passes `num-irq = p_num_spi + NUM_PPI`, revision, security, and LPI properties to QEMU. |

QBox is therefore configured to expose a smaller interrupt-controller surface
than FVP.

### SMMU

| Run | Evidence |
| --- | --- |
| FVP | `terminal_ns_uart0_5004.log:273-275`: 52-bit IAS/OAS, features `0x01fcdfcf`, cmdq 262144, evtq 131072 |
| QBox | `qbox-primary-console.log:355-357`: 48-bit IAS/OAS, features `0x00000304`, cmdq 256, evtq 256 |

The source cause is also explicit:

| File | Lines | Evidence |
| --- | --- | --- |
| `tools/qbox-platform/platforms/apollo/hw-block/config.lua` | 271-273 | Default SMMU backend is `systemc-mmu720ae`. |
| Same file | 637-651 | `ap_smmu_component()` instantiates `mmu720ae` for the default backend. |
| `tools/qbox-platform/systemc-components/mmu720ae/include/mmu720ae_core.h` | 94-109 | ID registers advertise a minimal feature set, queue log2 size 8, and `IDR5_OAS_48_BIT`. |

This explains the Linux SMMU log difference without requiring a guest-side
problem.

## Tmux Console Escape Injection

The blocked QBox run shows:

```text
=> [28;89R
Unknown command '[28' - try 'help'
Unknown command '89R' - try 'help'
```

The same primary log contains U-Boot's terminal status query:

```text
ESC 7 ESC [ r ESC [ 999 ; 999 H ESC [ 6 n ESC 8
```

The runner source explains how this can feed back into the guest:

| File | Lines | Evidence |
| --- | --- | --- |
| `scripts/run/run_qbox_apollo_fvp_full_tmux.sh` | 720 | The primary-console pane runs `tail -n +1 -F` on the guest console log, writing escape sequences to the real terminal. |
| Same file | 736-742 | The same pane reads stdin and writes each line to `primary-uart-input.fifo`. |
| Same file | 674-685 | `write_fifo_line()` writes unfiltered text to the UART FIFO. |

Therefore a terminal cursor-position response such as `ESC[28;89R` can be read
as local input and injected into U-Boot. This is a runner bug. It is separate
from the QBox firmware fidelity gaps, but it can disturb U-Boot automation and
should be fixed.

The non-interactive FVP log runner avoids this class of uncontrolled terminal
feedback by explicitly answering terminal status queries with a fixed response
in `scripts/run/runfvp_log_boot.py:139-197`.

## CPU Count Mismatch

The active Yocto config sets:

```text
PC_CPUS_COUNT_DEFAULT = "4"
```

QBox platform logs still print:

```text
ap cpus:      16
```

Source evidence:

| File | Lines | Evidence |
| --- | --- | --- |
| `tools/qbox-platform/platforms/apollo/hw-block/config.lua` | 476-478 | `AP_NUM_CPUS` defaults to `QBOX_APOLLO_NUM_CPUS=16`; `AP_GIC_NUM_CPUS = AP_NUM_CPUS`. |
| `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua` | 257-258 | AP GIC CPU and redistributor count follow `AP_GIC_NUM_CPUS`. |

The passing QBox post-login probe still reported `possible/present/online =
0-3`, so the guest-visible CPU count was limited to 4. The platform-side
default is still a fidelity/configuration mismatch for this profile.

## Current Classification

| Item | Classification | Reason |
| --- | --- | --- |
| U-Boot `FWU_DISCOVER -125` | QBox secure FWU fidelity gap | U-Boot calls FF-A correctly; FVP succeeds; QBox secure FWU path fails. |
| `FWU: FF-A memory reclaim failure` | Secondary symptom | It is cleanup after FWU direct-request failure. |
| `psa_fwu_query -134` | QBox secure-service gap | QBox model defines `-134` as not supported; current FWU provider path is not usable. |
| OP-TEE SP panic `0xdeadbeef` | QBox FWU provider bug/exposure | Existing GDB maps to null `update_agent` in TS FWU provider. |
| Linux FF-A notification `-95` | Not a QBox root cause | Documented RD-Aspen limitation. |
| SMMGW logging `-4` at startup | Not a QBox root cause by itself | Documented RD-Aspen limitation. |
| SE-Proxy PS remove `-140` at first boot | Not a QBox root cause by itself | Documented expected first-boot behavior. |
| SCMI protocol 19 unsupported | QBox service-model coverage gap | Protocol `0x13` is not implemented in `mhu320ae`. |
| GIC 512 SPIs | QBox model configuration gap | Lua config hardcodes 512 SPIs. |
| SMMU 48-bit/256 queues | QBox model implementation gap | `mmu720ae` ID registers expose smaller capability. |
| U-Boot `Unknown command '[28'` | Runner/tmux bug | Terminal CPR response is injected through the UART input FIFO. |
| Latest `child_failed:120` | Run-specific block | Same image previously passed; latest child saw Linux boot but no login in a short runtime window. |

## Recommended Next Work

1. Fix or instrument the QBox secure FWU path first. The highest-value probe is
   to run the current Yocto QBox image with the existing SE-Proxy FWU GDB trace
   and confirm whether the current `-134/-125` path still maps to null
   `update_agent`.
2. Decide the intended QBox secure-service architecture: either connect the
   real SE-Proxy FWU provider to a modeled RSE FWU service, or make the
   `rse-ps-proxy` service model cover the FWU PSA calls required by RD-Aspen.
3. Filter terminal status responses in the tmux primary console before writing
   to `primary-uart-input.fifo`.
4. Align AP GIC/SMMU advertised capabilities with FVP or document the
   intentional deviation in QBox platform README/status docs.
5. Add SCMI protocol `0x13` support or stop advertising/triggering it,
   depending on the required Linux driver behavior.
6. Bind `QBOX_APOLLO_NUM_CPUS` to the active Yocto CPU-count profile for
   `apollo-fvp` Yocto runs, so platform logs and guest CPU policy are aligned.

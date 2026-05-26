# RSE QBox Evidence Ledger

Created: 2026-05-20

## Purpose

This ledger is the baseline evidence surface for the RSE-QBox specification.
Implementation work should update this file before changing QBox behavior when
new RSE addresses, registers, firmware artifacts, log markers, or fidelity gaps
are discovered.

## Active Baseline

| Item | Current value |
| --- | --- |
| Machine | `fvp-rd-aspen` |
| Variant | `RD_ASPEN_VARIANT = "cfg2"` |
| Primary compute CPU count | `PC_CPUS_COUNT_DEFAULT = "4"` |
| Current QBox mode | primary-compute Linux direct boot |
| Target QBox mode | RSE-oriented firmware boot |
| QBox platform | `tools/qbox/platforms/fvp-rd-aspen/` |
| Cortex-M55 build target | `cpu_arm_cortexM55` |
| Remote Cortex-M55 target | `remote_cpu` |
| NVIC source directory | `tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/` |
| NVIC build target | `nvic_armv7m` |
| Cortex-M55 Lua `moduletype` | `cpu_arm_cortexM55` |
| Cortex-M55 QEMU target string | `AARCH64` |
| Active RSE skeleton CPU path | `rse_cpu_pass` using `RemotePass` and `RemoteCPU` |

## Firmware Artifacts

| Artifact | FVP role | Default local path |
| --- | --- | --- |
| `rse-rom-image.img` | RSE ROM raw image | `build/tmp_baremetal/deploy/images/fvp-rd-aspen/rse-rom-image.img` |
| `rse-flash-image.img` | RSE flash image and writeback target | `build/tmp_baremetal/deploy/images/fvp-rd-aspen/rse-flash-image.img` |
| `rse-otp-image.img` | RSE OTP/NVM image | `build/tmp_baremetal/deploy/images/fvp-rd-aspen/rse-otp-image.img` |
| `ap-flash-image.img` | AP secure flash image and writeback target | `build/tmp_baremetal/deploy/images/fvp-rd-aspen/ap-flash-image.img` |
| `combined_provisioning_message.bin` | RSE SRAM1 provisioning payload at offset `0x20000` | `build/tmp_baremetal/deploy/images/fvp-rd-aspen/combined_provisioning_message.bin` |

## FVP Parameters To Preserve

| Behavior | Source parameter |
| --- | --- |
| RSE ROM image | `css.smb.rseil.rse.rom.raw_image` |
| RSE flash input | `css.smb.rseil.rse_flashloader.fname` |
| RSE flash writeback | `css.smb.rseil.rse_flashloader.fnameWrite` |
| AP flash input | `ros.flash_loader.fname` |
| AP flash writeback | `ros.flash_loader.fnameWrite` |
| RSE OTP image | `css.smb.rseil.rse.lcm_nvm.raw_image` |
| RSE OTP file read | `css.smb.rseil.rse.lcm_nvm.read_from_file=1` |
| RSE OTP image use | `css.smb.rseil.rse.lcm_nvm.use_image_file=1` |
| provisioning payload | `css.smb.rseil.rse.sram1=<bundle>@0x20000` |
| RSE volatile memory width | `css.smb.rseil.VMADDRWIDTH=18` |
| reset syndrome | `css.smb.rseil.RESET_SYNDROME_INIT_VAL=0x80000000` |
| DMA boot enable | `css.smb.rseil.rse.sys_ctrl_regs.DMA_BOOT_EN_REG_RESET=1` |
| RSE CPU hold | `css.smb.hold_rse_cpu_in_reset=1` |

## Reviewed RSE Skeleton Constants

| Item | Value | Source |
| --- | --- | --- |
| RSE ROM secure base | `0x11000000` | TF-M `platform_base_address.h` |
| RSE ROM size | `0x00020000` | TF-M `platform_base_address.h` |
| RSE ITCM secure base | `0x10000000` | TF-M `platform_base_address.h` |
| RSE ITCM secure CPU0 alias | `0x1A000000` | TF-M `platform_base_address.h` |
| RSE ITCM non-secure base | `0x00000000` | TF-M `platform_base_address.h` |
| RSE ITCM non-secure CPU0 alias | `0x0A000000` | TF-M `platform_base_address.h` |
| RSE ITCM size | `0x00008000` | TF-M `platform_base_address.h` |
| RSE DTCM secure base | `0x30000000` | TF-M `platform_base_address.h` |
| RSE DTCM secure CPU0 alias | `0x34000000` | TF-M `platform_base_address.h` |
| RSE DTCM non-secure base | `0x20000000` | TF-M `platform_base_address.h` |
| RSE DTCM non-secure CPU0 alias | `0x24000000` | TF-M `platform_base_address.h` |
| RSE DTCM size | `0x00008000` | TF-M `platform_base_address.h` |
| RSE VM0 secure base | `0x31000000` | TF-M `platform_base_address.h` |
| RSE VM1 secure base | `0x31040000` | derived from VM0 plus `VMADDRWIDTH=18` |
| RSE provisioning load address | `0x31060000` | VM1 secure base plus FVP `@0x20000` |
| RSE host access NS window | `0x60000000..0x6fffffff` | TF-M `platform_base_address.h` |
| RSE host access S window | `0x70000000..0x7fffffff` | TF-M `platform_base_address.h` |
| RSE host UART NS alias | `0x6ff00000` | `HOST_ACCESS_BASE_NS + 0x0ff00000` |
| RSE host UART S alias | `0x7ff00000` | `HOST_ACCESS_BASE_S + 0x0ff00000` |
| KMU secure base | `0x5009E000` | TF-M `platform_base_address.h` |
| LCM secure base | `0x500a0000` | TF-M `platform_base_address.h` |
| OTP wrapper secure base | `0x58111000` | TF-M `platform_base_address.h` |
| RSE system-control base | `0x58021000` | TF-M `platform_base_address.h` |
| RSE boot flash secure base | `0xb0000000` | TF-M CSS-Aspen RSE expansion headers |
| RSE boot flash size | `0x04000000` | TF-M CSS-Aspen RSE memory-size headers |
| ATU secure base | `0x50150000` | TF-M `platform_base_address.h` |
| SIC MPC secure base | `0x50151000` | TF-M `platform_base_address.h` |
| CC3XX secure base | `0x50154000` | TF-M `platform_base_address.h` |
| DMA350 secure base | `0x50002000` | TF-M `platform_base_address.h` |
| System counter control base | `0x5015A000` | TF-M `platform_base_address.h` |
| System counter read base | `0x5015B000` | TF-M `platform_base_address.h` |
| Integrity checker base | `0x5015C000` | TF-M `platform_base_address.h` |
| TRAM base | `0x5015D000` | TF-M `startup_bl1_1_helpers.h` |

These constants are skeleton inputs. They do not by themselves prove that
generic `gs_memory` is a sufficient model for RSE flash, OTP, LCM, ATU, or CC3XX
behavior.

## Required MVP Markers

| Area | Required markers |
| --- | --- |
| RSE boot | `Starting TF-M BL1_1`, `Jumping to the first image slot` |
| RSE-SCP handoff | `Init SCMI comm to SCP succeeded`, `RSE to SCP SCMI power on AP succeeded`, `SCMI Comms subscribed to power state notifications` |
| measured boot | `BL1_2`, `BL2`, `SI_CL0`, `AP_BL2`, `RT_0`, `SECURE_RT_EL3`, `SECURE_RT_EL1_SPMD`, `BL_33` |
| AP release | AP primary core starts only after modeled RSE/SCP release evidence |
| Linux boot | primary console reaches the configured login or shell prompt |

## Deterministic Comparison Rules

Normalize these values before comparing FVP and QBox logs:

- timestamps,
- host-specific absolute paths,
- telnet or socket port numbers,
- run-directory names,
- copied writable image filenames.

Fail the MVP comparison for:

- missing required marker,
- required marker order violation,
- missing MHUv3 doorbell event evidence,
- missing SCMI AP power-on response,
- AP boot before modeled RSE/SCP release,
- Linux login missing from the RSE-oriented boot path.

## SCP/Safety Island Strategy

The MVP SCP strategy is `Protocol-correct SCP service model`.

This strategy is selected so RSE bring-up can progress without blocking on full
Safety Island CL0/SCP-firmware CPU execution. It is a `functional-model`
milestone only. Full RSE-SCP/FVP equivalence still requires real Safety Island
CL0/SCP execution or stronger evidence that the service model covers every
observable FVP behavior in the supported scenario.

| Strategy | Fidelity label | Notes |
| --- | --- | --- |
| Protocol-correct SCP service model | `functional-model` | Must decode SCMI requests from shared memory and deliver MHUv3 doorbells; not a fixed success stub. |
| Real Safety Island CL0/SCP execution | `fvp-equivalent` candidate | Required before claiming full RSE-SCP/FVP equivalence. |

## Current Known Gaps

| Gap | Current status | Required next step |
| --- | --- | --- |
| RSE Cortex-M55 boot | reset vector reached through `RemoteCPU`; previous CC3XX Data Abort, DMA erase/fill timeout, RSE system-control `reset_syndrome` fault, ATU register-programming gap, untyped KMU placeholder, `__cmsis_start` copy-table timeout, zeroed KCE_CM hardware-slot blocker, BL2 decrypt failure, BL1_2 signature-validation failure, initial BL2 host-window/PPU blockers, SI CL0 AES-KW unwrap failure, host ATU placeholder gap, RSE-SI MHUv3 init failure, AP reset-release blocker, AP-side RSE-COMMS MHUv3 channel-count failure, AP SDS warning, AP FW_CONFIG/HW_CONFIG/BL33 authentication failures, AP system timer fault, AP-SI SCMI MHU feature-register abort, and AP BL31 RAS system-register trap are removed. Current runtime evidence reaches SI CL0/CL1 load/key-hash/post-load, RSE-SCP SCMI init, AP BL2 load, AP ATU region programming, AP power-domain SCMI success, AP reset release, AP BL2 FW_CONFIG/HW_CONFIG/BL31/BL32/SPMD/BL33 measured boot, `BL2: Booting BL31`, BL31 runtime services, SCMI driver initialization, GICv3/PFDI initialization, Linux login, and file-backed post-login driver probes. | Continue secure-service userspace/RSE transport fidelity, PSCI secondary and reset behavior, FWU bank-selection persistence, real SI CL1/Zephyr data-plane fidelity, and default-safe DMI evidence. |
| RSE boot media | RSE ROM executes; RSE/AP secure flash is served by the `strata_flash_j3` SystemC/TLM component with read-array, read-ID/query/status, byte-program, block-erase, lock/unlock command handling, optional read-array DMI via `QBOX_RDASPEN_BOOT_FLASH_DMI=true`, and optional `backing_file` write-through for per-run FWU evidence; LCM reads and writes are backed by the active `rse-otp-image.img`; the runner initializes invalid per-run RSE FWU private metadata at flash offset `0x5000` to slot 0/READY without modifying deploy artifacts; the runner decompresses gzip-formatted `rse-flash-image.img` and `ap-flash-image.img` into per-run raw images before binding them to QBox; and RSE OTP/flash writeback is enabled only for per-run copied writable images | Prove full capsule application, bank-1 boot markers, cross-reboot persistence, full firmware-update A/B metadata behavior, and the remaining flash/NVM error paths. |
| RSE ATU | default `translation-model` with optional `translation-dmi-model`; ATUBC reset value, ATUBC page-size and supported-region-count decoding, TF-M region programming registers, secure/non-secure logical-window translation, TLM initiator forwarding, unmapped translation errors, disabled configured-region faults, end-span out-of-range faults, configurable output security-domain permission faults, ATUIS/ATUMA mismatch latching, ATURAV page-shift overflow rejection, translated DMI grants, positive-offset DMI range clamping, two's-complement negative add-values, and full-range DMI invalidation on mapping changes are modeled; DMI is currently gated by `QBOX_RDASPEN_ATU_DMI=true`. Current runtime evidence reaches SI CL0/CL1 image load, SI ATU region programming, SI CL0 release, RSE runtime measured boot through `BL_33`, and records no first failing register access with translated DMI enabled, but ATU DMI is not default-safe yet. | Complete remaining page-boundary semantics, richer fault status, default-safe DMI behavior, and deeper negative/fault injection checks without hiding flash/NVM or host-window side effects. |
| RSE LCM/OTP | `otp-backed-register-model`; lifecycle/status reset values, OTP image reads, OTP window writes, per-run file writeback, and lock-after-provision behavior are component-tested; a bounded runtime proves the copied OTP image changes without modifying the deploy OTP image | Implement fuller documented lifecycle transitions, DCU/lifecycle coupling, and failure/status behavior beyond the observed TF-M provisioning path. |
| RSE KMU | `touched-register-model`; KMUBC, OTP-backed hardware slot seeds, key-slot writes, completion bits, random-delay register reads, and destination-port export writes are modeled; latest trace shows non-zero KCE_CM words from `rse-otp-image.img` reach CC3XX `AES_KEY_0..7` | Add fuller error/status coverage, lock semantics, OTP/provisioning write behavior, and coupling with CC3XX/PKA key use. |
| RSE Integrity Checker | `touched-status-model`; component exposes ICBC, ICC, ICIS/ICIC, ICCVAL, and PID/CID values; runtime has not reached `0x5015C000` yet | Verify the firmware path reaches the model, then implement digest/check behavior or DMA/output side effects required by TF-M. |
| RSE CC3XX | `hash-aes-cmac-modular-pka-model`; early RNG/readiness, SHA-256 DMA hashing, SHA-256 multipart `HASH_H`/`HASH_CUR_LEN` state restore, DMA completion status, AES-CTR memory-to-memory, AES-ECB decrypt for AES-KW, AES-CMAC tag generation, PKA SRAM cursor access, ADD/SUB/AND/OR/XOR, status bit 8 comparison behavior, shifts, modular add/subtract, multiply low/high, division, modular multiplication/exponentiation/inverse, and reduction are modeled in component tests; BL1_1 validates BL1_2, BL1_2 decrypts and validates BL2, and BL2 now passes SI CL0 key hash validation. | Continue verifying later AP BL2 crypto/image paths before adding more CC3XX surface. |
| RSE DMA350 | `functional-fill-copy-model`; four channels are exposed through `DMASECINFO = 0x30`, `CH_CMD` polling completes, observed BL1_1 DTCM/ITCM fill commands issue initiator-backed writes, 1D copy commands update DONE status in component tests, `DMA_INFO.IIDR/AIDR` reset values let TF-M `dma350_init()` pass during `tfm_core_init()`, and opt-in trace filtering can isolate copy/fill operations. The active BL2 SI CL0 failure is not currently a DMA350 runtime path because `PLATFORM_HAS_BOOT_DMA:BOOL=OFF` | Implement remaining DMA350 trigger, interrupt, multi-dimensional transfer, and DMA ICS behavior. Revisit BL2 DMA copy only if a future generated image enables `PLATFORM_HAS_BOOT_DMA`. |
| RSE system control | `touched-register-model`; `reset_syndrome`, `reset_mask`, `cpuwait`, selected power/reset, and DMA boot registers exist; 2026-05-21 trace shows `reset_syndrome = 0x80000000`, `reset_mask = 0x0`, then `reset_mask = 0x100` write | Add real reset lifecycle, CPU hold/release side effects, SWRESET integration, DMA boot side effects, and broader register coverage from TF-M/FVP evidence. |
| Host PPU windows | `touched-status-model`; the new `host_ppu` component mirrors written `PWPR` policy values into `PWSR` power status so TF-M PPU polling can complete for the SI CL0 cluster/core windows | Replace with TRM-backed PPU power-state sequencing, transition status, interrupt/error behavior, and coupling to real SI CL0/CL1 reset/power state. |
| AP/SI host windows | `static-map-only` plus selected models; AP flash/raw-image and AP/SI SRAM/CUB/PIK/SCR/ATU/MHU windows are reachable through RSE ATU translation. Host SI/AP/SMD ATU windows are now `rse_atu` register models rather than plain memory, and selected host memories can opt into DMI with `QBOX_RDASPEN_HOST_MEMORY_DMI=true`. Most windows are still plain memory placeholders where side effects are unknown. | Replace static windows with modeled AP/SI devices where software-visible side effects matter after AP BL2 progress is understood, then PIK/SCR controls, ATU windows, and AP-RSE MHU behavior. |
| MHUv3 | RSE-SI, AP-RSE, and AP-SI SCMI paths use pair-isolated PBX/MBX `mhuv3_stub` frames with MHUv3 AIDR/IIDR, CCI-configurable channel count and feature/ID registers, per-channel set/status/mask/clear, peer PBX/MBX status propagation, ACK bit 1 signaling for the RSE-SI SCMI responder, and SCMI shared-memory responses for Base, Power Domain, and System Power protocols. The old direct-boot doorbell success reply is gated by `direct_boot_compat=false` by default and is only opted into by the primary-compute direct-boot Lua config. AP TF-A no longer reports `Host to RSE MHU driver initialization failed: -4`, and AP BL31 now reports `SCMI driver initialized` after reading `PLAT_CSS_MHU_BASE + 0x10` through the AP ATU-translated AP-SI SCMI MHU PBX frame. AP/SI CL1 resource-table seeding and RPMsg name-service are runtime-proven: `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/mhuv3-trace.log` records deferral until the Linux host kick, `rpmsg-ns-injected name=ethsi1`, a 1 ms SystemC signal delay, and `rpmsg-ns-signaled`; Linux logs `creating channel ethsi1`, binds `rpmsg_net`, and `ip link show ethsi1` returns 0. The low-level PBX/MBX register storage, channel decode, status/mask/control state, feature/ID registers, and combined interrupt status calculation are now split into the reusable `mhuv3_stub::mhuv3_frame_model` helper and directly unit-tested for both PBX and MBX modes. | Complete AP-RSE secure-service plus AP-SI/PFDI SCMI request/response semantics, replace the service-model SI CL1 RPMsg endpoint with a real SI CL1 CPU/Zephyr peer and packet data-plane behavior, and continue evolving the compatibility component toward a full TRM-equivalent MHUv3 IP. |
| RSE-SCP endpoint | MVP service model now decodes RSE BL2 SCMI shared-memory requests and proves `Init SCMI comm to SCP succeeded`; real SI/SCP execution remains open. | Continue from AP BL2 image-loading/progress to AP power-on SCMI command evidence and keep the real SI/SCP execution gap open. |
| RSE-oriented AP boot | Opt-in partial model. AP0 is reset-held until modeled RSE/SCP power-on release, then executes AP BL2, emits secure console output, authenticates and measures FW_CONFIG/HW_CONFIG/BL31/BL32/SPMD/BL33, boots BL31, initializes the BL31 SCMI driver, reaches Linux login, and supports a file-backed root login/post-login probe. Runtime `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/` records `passed=true`, `timed_out=false`, Linux login/root prompt, post-login probe completion, `remoteproc_state:si-cl1:attached`, `virtio6.ethsi1.-1.1024`, and `ethsi1_iplink_rc:0`. Secondary AP CPUs are visible to Linux/QEMU; PSCI and secondary behavior still need deeper equivalence checks. | Validate PSCI secondary behavior, secure-service userspace tests, AP/SI PFDI traffic, and real SI CL1/Zephyr RPMsg data-plane fidelity beyond service-model endpoint creation. |
| secure services | post-MVP | Validate after RSE-oriented boot works. |
| secure firmware update | post-MVP | Validate after writable flash and service paths work. |

## 2026-05-23 RSE Progress Evidence

| Evidence | Result |
| --- | --- |
| `cc3xx-tests` | Passed after adding AES ECB decrypt coverage for AES-KW use. |
| `rse_kmu-tests` | Passed after adding the key-only trace filter. |
| `rse_lcm-tests` | Passed after adding configured TCI `tp_mode` coverage. |
| `rse_atu-tests` | Passed after host-side ATU register-only use was enabled. |
| `mhuv3_stub-tests` | Passed; verifies RSE-BL2 Power Domain SCMI response and ACK bit 1 doorbell. |
| `strata_flash_j3-tests` | Passed; verifies byte-program status polling, read-array-only DMI behavior, and optional backing-file write-through for program/erase mutations. |
| `build/qbox-fvp-rd-aspen/rse-t019ai-lcm-tci-kmu-keytrace-20260523-v1/` | RSE BL2 loads SI CL0 image 3, matches the key hash, and enters SI CL0 post-load. |
| `build/qbox-fvp-rd-aspen/rse-t019aj-host-atu-regs-20260523-v2/` | Host SI ATU regions 0..16 are programmed, SI CL0 is released, and the next blocker becomes MHUv3 init error `0x60000001`. |
| `build/qbox-fvp-rd-aspen/rse-t019ak-mhuv3-scmi-20260523-v5/` | RSE-SI MHUv3/SCMI init succeeds and Power Domain protocol version `0x20000` is reported. |
| `build/qbox-fvp-rd-aspen/rse-t019al-dmi-mhuv3-scmi-20260523-v1/` | Optional boot-flash/host-memory DMI run reaches the same MHU/SCMI success point and times out later after AP BL2 slot-version output. |
| `build/qbox-fvp-rd-aspen/rse-t019ao-ap-cpus-primary-power-20260523-v1/` | AP0 reset release is observed after `RSE to SCP SCMI power on AP succeeded`; AP0 executes from `pc=0x82000` to AP BL2 PCs and prints the AP BL2 banner. The blocker changes to AP-side RSE-COMMS MHUv3 init `-4`. |
| `build/qbox-fvp-rd-aspen/rse-t019ap-ap-rse-mhu-20260523-v1/` | Multi-channel AP-RSE MHUv3 removes the AP-side MHU init `-4`; AP secure BL2 prints `WARNING: SDS init failed (-1), continuing measured boot` and loads image id 6 at `0x2010..0x24ce`, then the platform times out before later secure-world/Linux markers. |
| `build/qbox-fvp-rd-aspen/rse-t019aq-ap-rse-psa-reply-nodmi-20260523-v1/` | Minimal AP-RSE PSA success reply experiment still times out after AP image id 6. AP secure console reaches `Image id=6 loaded: 0x2010 - 0x24ce`; AP PC trace reaches `pc=0x826f4`, which maps to TF-A BL2 `plat_panic_handler`. |
| `build/qbox-fvp-rd-aspen/rse-t019ay-ap-ntfw-nvctr-20260523-v1/` | AP SDS and trusted/non-trusted NV counters are now FVP-aligned. AP BL2 loads and measures FW_CONFIG, HW_CONFIG, BL31, BL32/SPMD, TOS config, BL33 certs, and BL33. BL33 measurement matches the extracted BL33 SHA-256 `64d6bd3583fb54a7f7ae4655bef9f3e26e7ed4376db5b800a094ae37a5459660`. The next blocker is a BL31 EL3 abort at `far_el3 = 0x1a810040`, mapped to `arm_configure_sys_timer()`. |
| `build/qbox-fvp-rd-aspen/rse-t019az-ap-timer-20260523-v1/` | Adding the AP system timer model removes the `0x1a810040` abort. BL31 reaches `Initializing SCMI driver on channel 0`; the next blocker is an AP-SI SCMI MHU feature-register abort at `far_el3 = 0x40080010`, mapped to `plat_css_get_scmi_info()`. |
| `build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1/` | Adding AP ATU-translated AP-SI SCMI MHU PBX/MBX frames removes the `0x40080010` abort. BL31 prints `SCMI driver initialized`; the next blocker is `rdaspen_ras_init_per_cpu()` writing `ERRSELR_EL1` with `elr_el3 = 0x107b8`, `esr_el3 = 0x02000000`, `far_el3 = 0x0`. |

## 2026-05-24 GDB And DMI Evidence

| Evidence | Result |
| --- | --- |
| `build/fvp-boot-logs/rse-qbox-debug-telnet-20260524-v1/` | File-backed FVP comparison run passed in 14.474 seconds. The RSE UART log reaches SI CL1 pre/post-load, SI CL0 pre/post-load, SCMI-to-SCP init success, and AP power-domain handling without requiring a long wait. |
| `tools/qbox/systemc-components/reg_router/include/reg_router.h` | `reg_router` now forwards downstream DMI requests, clamps returned ranges to the mapped child range, and propagates downstream invalidations to upstream targets. |
| `tools/qbox/qemu-components/common/include/dmi-manager.h`, `tools/qbox/qemu-components/common/src/libqemu-cxx/memory.cc`, `tools/qemu/libqemu/exports.py` | QBox now marks libqemu RAM aliases read-only when the upstream DMI grant is not writable, avoiding writable aliases for flash-like regions. |
| `timeout 120 cmake --build tools/qbox/build --target qemu --parallel 8` | Passed; regenerated libqemu exports include `memory_region_set_readonly`. |
| `timeout 120 cmake --build tools/qbox/build --target gs_register-tests strata_flash_j3-tests --parallel 8` and `timeout 60 ctest --test-dir tools/qbox/build -R '^(gs_register-tests\|strata_flash_j3-tests)$' --output-on-failure` | Passed; `gs_register-tests` covers DMI forwarding through `reg_router`, and `strata_flash_j3-tests` still validates flash DMI behavior. |
| `timeout 120 cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed after the DMI/libqemu changes. |
| `build/qbox-fvp-rd-aspen/rse-t019ax-reg-router-dmi-20260524-v1/` | Short AP-enabled DMI runtime still times out, but RSE logs reach `BL2: SI CL1 pre load complete`. `result.json` records non-zero CL1 SRAM data, header sample matching flash offset `0x167000`, code sample matching `0x167400`, and mapped prefix match `0x14cfb`. AP/Linux login is not reached. |
| `build/qbox-fvp-rd-aspen/gdb-t019ay-host-all-20260524-v1/` | Reusable GDB debug bundle generated QBox host, TF-M/RSE, Linux/AP, SCP-Firmware symbol, and SI CL1 Zephyr symbol scripts. The run proves RSE GDB port `12340` and AP GDB port `12341` are reachable, captures QBox host thread/backtrace evidence, and records that SCP-Firmware has symbols/source mapping only because the current path uses an SCP service model rather than a live SCP CPU. |
| TF-M/RSE GDB probe | In the instrumented GDB run, TF-M/RSE is executing `cc3xx_lowlevel_hash_uninit()` at PC `0x1100b1e2` with the stack in `cc3xx_hash_update()` -> `hash_digit_array()` -> `mbedtls_lmots_calculate_public_key_candidate()` -> `mbedtls_lms_verify()` -> `bl1_2_validate_image()`. This identifies the GDB-observed progress point as LMS/LMOTS signature verification backed by CC3XX hash state traffic. |
| Linux/AP GDB probe | AP CPU0 is still at `pc = 0x82000`, `sp = 0x0`; AP CPU1-3 are halted at the same reset-vector area. Linux symbols do not match yet, so Linux has not started in the GDB-instrumented short run. |
| QBox host GDB probe | Host GDB captures SystemC in `sc_core::sc_start()`/`sc_simcontext::simulate()`, AP QEMU CPU threads in `QemuCpu::wait_for_work()` / `mttcg_cpu_thread_fn()`, QEMU iothreads, RPC server/client threads, and call_rcu threads. This gives a reusable host-side inspection path without changing `ptrace_scope`. |
| `mhuv3_stub` indexed seed fix | `mhuv3_stub` now keeps direct `std::vector<unsigned int>` presets for C++ tests and also consumes Lua loader indexed presets such as `doorbell_ack_seed_words.1` in numeric order during construction. This avoids the previous runtime gap where the Lua table did not populate the vector and no resource table was written. |
| `ctest --test-dir tools/qbox/build -R mhuv3_stub --output-on-failure` | Passed after switching the regression to indexed seed presets. The test verifies the RD-Aspen-like resource table seed has `num_of_vrings = 2` encoded as `0x00000200`, not the previous byte-swapped `0x00020000`. |
| `build/qbox-fvp-rd-aspen/rse-t019aw-rpmsg-seed-indexed-preset-20260524-v1/` | RSE-oriented runtime with `--post-login-probe` passed without timeout and proved resource-table seeding plus module-load success. It exposed the timing bug fixed by the later T019AV run: the first NS message arrived before the Linux `rpmsg_ns` endpoint existed, so `/sys/bus/rpmsg/devices` listed only `rpmsg_ctrl` and `rpmsg_ns`, and `ethsi1_iplink_rc:1`. |
| `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/` | RSE-oriented runtime with `--post-login-probe` passed without timeout. Evidence includes `rpmsg-ns-defer-until-host-kick`, `rpmsg-ns-injected name=ethsi1`, `rpmsg-ns-signaled`, Linux `virtio_rpmsg_bus virtio6: creating channel ethsi1`, `probe of virtio6.ethsi1.-1.1024 returned 0`, `/sys/bus/rpmsg/devices/virtio6.ethsi1.-1.1024`, `rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1`, and `ethsi1_iplink_rc:0`. |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | T045 adds CCI parameters for `channel_count`, `feat_spt0`, `feat_spt1`, `iidr`, and `aidr`; `DBCH_CFG0`, register decode, combined interrupt status, and compatibility notify-channel handling now follow the configured channel count while preserving the default 128-channel behavior. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Focused coverage instantiates a 4-channel PBX frame and verifies `DBCH_CFG0`, `CTRL_FEAT_SPT0`, `CTRL_FEAT_SPT1`, `CTRL_IIDR`, and `CTRL_AIDR` reflect CCI preset values. |
| `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 4` | Passed. |
| `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` | Passed. |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | T049 adds `direct_boot_compat`, defaulting false, and gates the legacy automatic doorbell success reply behind that opt-in parameter. |
| `tools/qbox/platforms/fvp-rd-aspen/conf.lua` | The primary-compute direct-boot MHU pair opts into `direct_boot_compat = true`; the RSE-oriented config does not. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Focused coverage verifies the opt-in compatibility reply still works and a strict default doorbell frame does not synthesize a reply. |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 4` | Passed. |
| `./scripts/validate_qbox_fvp_rd_aspen_map.py` | Passed and wrote `build/qbox-fvp-rd-aspen/map-validation.json`. |
| `build/qbox-fvp-rd-aspen/t049-direct-compat-smoke-20260524-v2/` | Short direct-boot smoke parsed the updated Lua config, booted Linux, reached `fvp-rd-aspen login:`, and recorded no kernel-panic/rootfs failure patterns. It intentionally stopped at the 45-second cap without post-login probing, so `passed=false` is expected for the full runner criteria. |
| `build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v1/` | Reusable GDB bundle generated all QBox host, TF-M/RSE, AP firmware/Linux, SCP-Firmware, and SI CL1 Zephyr scripts. Conservative debug-DMI run captures QBox/SystemC/QEMU host backtraces under GDB; RSE/TF-M is still in BL2 flash-copy progress and AP is still at `0x82000`. |
| `build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v2/` | Fast-runtime GDB bundle proves live Linux GDB attach through the AP target. `linux-later.txt` resolves CPU0 to `cpu_do_idle()`, CPU2 to `change_protection_range()`, and reports four AP CPU threads. `tfm-s-later.txt` resolves RSE runtime to `__tfm_arch_thread_fn_call_veneer()` / `psa_wait_thread_fn_call()`. SCP-Firmware and SI CL1 Zephyr symbol probes both load, but SCP has no live CPU target under the current service-model strategy. |

## 2026-05-25 T034 RSE ATU Fault Handling

T034 extends the `rse_atu` translation model from range translation into the
first modeled fault path:

- configured but disabled regions now reject matching accesses instead of
  falling through to a later or unmapped result;
- accesses that start inside an enabled region but extend past its end are
  rejected as out-of-range;
- ATUROBA AXNSE/AXPROT1 fields are decoded into secure, non-secure, root, or
  realm output domains and checked against the new
  `permitted_security_domains` CCI parameter, which defaults to all domains
  allowed to preserve the existing platform runtime path;
- translation faults latch `ATUIS` mismatch status and `ATUMA`, and trace logs
  include the fault reason.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` | Adds `translation_fault`, ATUROBA masking/domain decode, disabled/out-of-range/permission fault classification, ATUIS/ATUMA latching, and trace reason strings. |
| `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Adds focused regressions for disabled configured regions, accesses spanning past a region end, and a disallowed non-secure output domain. |
| `git -C tools/qbox ls-files --others --exclude-standard -- systemc-components/rse_atu/include/rse_atu.h tests/components/rse_atu/rse_atu-tests.cc` | Confirms these two files are currently in untracked QBox component/test directories, so generic `git diff --check` does not cover their contents. |
| `! rg -n "[ \t]+$" tools/qbox/systemc-components/rse_atu/include/rse_atu.h tools/qbox/tests/components/rse_atu/rse_atu-tests.cc doc/spec/rse-qbox/task.md doc/spec/rse-qbox/evidence.md doc/spec/rse-qbox/design.md doc/spec/rse-qbox/plan.md` | Passed; no trailing whitespace in the changed untracked source/test files or updated spec documents. |
| `cmake --build build --target rse_atu-tests --parallel 4` from `tools/qbox` | Passed. |
| `ctest --test-dir build -R '^rse_atu-tests$' --output-on-failure` from `tools/qbox` | Passed; `rse_atu-tests` completed successfully. |
| `git -C tools/qbox diff --check` | Passed. |
| `cmake --build build --target platforms-vp --parallel 4` from `tools/qbox` | Passed. |

## 2026-05-25 T034A RSE ATU Build-Config Page/Region Semantics

T034A aligns QBox ATU translation with the TF-M native ATU driver behavior:

- ATUBC[7:4] is decoded through explicit PS mask/offset constants when
  converting region page registers into byte ranges;
- ATUBC[2:0] now limits the number of regions scanned by the translation
  model, matching `atu_rse_get_supported_region_count()`;
- focused tests preset ATUBC to an 8 KiB page-size configuration and to an
  8-region configuration, proving both fields affect translation decisions.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` | Adds ATUBC PS/RC constants and `supported_region_count()`, then limits translation scanning to the configured supported region count. |
| `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Updates region programming helpers to use the model's ATUBC page size and adds CCI-preset tests for 8 KiB pages and 8 supported regions. |
| `! rg -n "[ \t]+$" tools/qbox/systemc-components/rse_atu/include/rse_atu.h tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Passed; no trailing whitespace in the changed source/test files. |
| `cmake --build build --target rse_atu-tests --parallel 4` from `tools/qbox` | Passed. |
| `ctest --test-dir build -R '^rse_atu-tests$' --output-on-failure` from `tools/qbox` | Passed; `rse_atu-tests` completed successfully. |
| `git -C tools/qbox diff --check` | Passed. |
| `cmake --build build --target platforms-vp --parallel 4` from `tools/qbox` | Passed. |

## 2026-05-26 TF-M Strata Write-Buffer Rejection

The TF-M-side Strata write-buffer experiment is rejected for now. It compiles,
but it is not FVP runtime-safe for RD-Aspen TF-M secure-storage initialization.

| Evidence | Result |
| --- | --- |
| `trusted-firmware-m:do_patch`, `do_compile`, `do_deploy` with 32-byte write-buffer polling fix | Passed, but runtime failed. |
| `build/fvp-boot-logs/write-buffer-poll-fix-fvp-critical-20260526-v1/` | FVP reaches `RSE to SCP SCMI power on AP succeeded` and TF-M runtime start, then fails after `Creating an empty ITS flash layout.` with `Partition initialization FAILED in 0x31047cc5`. |
| `trusted-firmware-m:do_patch`, `do_compile`, `do_deploy` with verify-and-byte-program fallback | Passed, but runtime failed at the same TF-M ITS point. |
| `build/fvp-boot-logs/write-buffer-verify-fallback-fvp-critical-20260526-v1/` | Same FVP failure: TF-M runtime reaches ITS layout creation, then `Partition initialization FAILED in 0x31047cc5`. |
| `arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-fvp-rd-aspen-src.inc` | The experimental `0086-rse-css-aspen-Use-CFI-write-buffer-for-Strata.patch` entry was removed. |
| `arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/files/tf-m/fvp-rd-aspen/0086-rse-css-aspen-Use-CFI-write-buffer-for-Strata.patch` | Deleted so the active TF-M build returns to the byte-program baseline. |
| `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/flash/strata/spi_strataflashj3_flash_lib.c` | After forced `do_patch`, source shows `MAX_PROGRAM_SIZE = 128` and no `nor_buffered_program()` path. |
| `trusted-firmware-m:do_patch`, `do_compile`, `do_deploy`, then `firmware-fvp-rd-aspen:do_deploy` after patch removal | Passed. Deploy images were refreshed at `2026-05-26 20:22:07` for `rse-rom-image.img`, `rse-flash-image.img`, `ap-flash-image.img`, and `rse-otp-image.img`. |
| `build/fvp-boot-logs/write-buffer-disabled-fvp-critical-20260526-v2/` | The previous TF-M ITS failure is gone. FVP reaches `Creating an empty ITS flash layout.`, `Creating an empty PS flash layout.`, measured boot through `BL_33`, `Booting Linux on physical CPU`, root filesystem mount, systemd startup, and secure console `tee_ta_close_session`. The run still reports `passed=false` because the script's `critical` mode requires a Linux login prompt that did not appear before the 150-second timeout. |

Conclusion: keep the TF-M byte-program baseline. Any Strata performance fix
must be done in QBox's SystemC/TLM flash model or in another semantics-preserving
host-side path, then checked against FVP logs.

## 2026-05-25 T034B/T037 RSE ATU Overflow, DMI, And SI Evidence

T034B closes two ATU correctness gaps found while validating translated DMI:

- ATURAV page offsets are rejected before `offset_pages << ATUBC.PS` can
  overflow the 64-bit translated address calculation;
- TF-M programs add-values as unsigned `physical - logical`, so lower physical
  mappings appear as two's-complement negative offsets. The model preserves
  that modulo behavior instead of rejecting all addition wrap;
- translated DMI now clamps positive-offset downstream grants whose start lies
  below the ATU offset, rejects invalid downstream ranges, and preserves the
  inverse range calculation for negative offsets.

The local Arm Zena CSS safety boot documentation states that Safety Island
verifies RSE-performed ATU configuration and halts immediately if an access
failure is detected. The current QBox run does not instantiate a live Safety
Island CL0 CPU, but it proves the current service-model boot path no longer
needs an ATU bypass: RSE BL2 programs SI ATU regions 0..16, releases SI CL0,
continues AP handoff, and reaches TF-M runtime measured-boot markers through
`BL_33` with `first_failing_register_access: none`.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` | Adds an `overflow` translation fault, guards ATURAV page-shift overflow, preserves two's-complement negative add-values, and hardens translated-DMI range conversion. |
| `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Adds raw offset-page programming plus regressions for page-shift overflow and DMI range clamping when a downstream grant starts below the translated offset. |
| `build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1/qbox-rse.log` | Records SI CL1 image 4 RAM load/key hash/post-load, SI CL0 image 3 RAM load/key hash, SI ATU regions 0..16, SI CL0 reset release/post-load, RSE-SCP SCMI init, AP BL2 load, AP ATU regions, AP power-on success, SCMI subscription, and measured boot through `BL_33`. |
| `build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1/result.json` | `marker_hits` are true for RSE boot, RSE-SCP handoff, and measured boot through `BL_33`; `linux_boot` is false because the short run times out before Linux login; `scp_service_model.live_scp_cpu_gdb` is false by design. |
| `arm-zena-css/documentation/design/safety_boot.rst` | Documents Safety Island ATU configuration verification and immediate boot halt on ATU access failure. |
| `arm-zena-css/documentation/design/components.rst` | Documents RSE/Safety Island/SMD ATUs and states that RSE owns ATU configurations. |
| `build/qbox-fvp-rd-aspen/gdb-debug-linux-sample-20260525-v1/` | Confirms the reusable GDB environment still attaches to TF-M/RSE, AP firmware/Linux target, SCP-Firmware symbols, and SI CL1 Zephyr symbols. The sampled AP target is still secure-world/U-Boot, so this run does not prove Linux kernel execution. |
| `build/qbox-fvp-rd-aspen/gdb-debug-env-current-20260525-v2/README.md` | Regenerated after the helper fix; the launch commands now reflect effective `QBOX_RDASPEN_ATU_DMI=true`, `QBOX_RDASPEN_HOST_MEMORY_DMI=true`, and `QBOX_RDASPEN_BOOT_FLASH_DMI=false` overrides. |

Conclusion: this closes T034B, T037, T019AD, T054, and T055 for the current
modeled/service-model boot path. It does not close full ATU fidelity,
default-safe ATU DMI, real Safety Island CL0/SCP CPU execution, secure-service
userspace tests, or FVP-vs-QBox comparison gates V004/V007.

## Source References

- `arm-zena-css/documentation/overview.rst`
- `arm-zena-css/documentation/design/components.rst`
- `arm-zena-css/documentation/design/boot_process.rst`
- `arm-zena-css/documentation/design/rse_image_encryption.rst`
- `arm-zena-css/documentation/design/secure_services.rst`
- `arm-zena-css/documentation/design/secure_firmware_update.rst`
- AP FIP certificate audit extracted from
  `build/tmp_baremetal/deploy/images/fvp-rd-aspen/fip_with_bl2.bin` shows the
  non-trusted firmware key/content certificate NV counter extension encodes
  `0x00df` (`223`), matching `NTFW_NVCTR_VAL`.
- `tools/qbox/platforms/fvp-rd-aspen/conf.lua` provides the direct QBox AP
  system timer model pattern using `qemu_hexagon_qtimer` at `0x1a810000` and
  `0x1a830000`.
- TF-A RD-Aspen BL31 defines `PLAT_CSS_MHU_BASE = 0x40080000`; the RSE boot log
  maps that AP logical range through AP ATU region 3 to
  `0x40000_3b080000`, which is now backed by the AP-SI SCMI MHU PBX model.
- `arm-zena-css/documentation/design/safety_boot.rst`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`
- `arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/files/tf-m/fvp-rd-aspen/0067-rse-css-aspen-Support-a-simple-memory-model-instead-.patch`
- `sw-ref-stack/test_automation/tests/test_bsp_demos/test_00_rse.py`
- `sw-ref-stack/test_automation/tests/test_bsp_demos/test_07_scmi_reboot.py`
- `sw-ref-stack/test_automation/tests/test_baremetal_demos/test_fwu.py`
- `arm-zena-css/yocto/meta-zena-css-bsp/lib/oeqa/runtime/cases/test_00_rse.py`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/partition/platform_base_address.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/device/include/platform_regs.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/bl1/boot_hal_bl1_1.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/device/source/atu_config_bl1.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/native_drivers/atu_rse_drv.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/native_drivers/atu_rse_lib.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/tfm_hal_platform.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/startup_bl1_1_helpers.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/cc3xx/low_level_driver/include/cc3xx_reg_defs.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/cc3xx/low_level_driver/src/cc3xx_aes.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/cc3xx/low_level_driver/src/cc3xx_dma.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/cc3xx/low_level_driver/src/cc3xx_kdf.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/bl1/cc3xx/cc3xx_rom_crypto.c`
- `build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/cc3xx/cc3xx_aes_external_key_loader.c`
- `build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/kmu/kmu_drv.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/bl1/bl1_2/main.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/bl2/ext/mcuboot/bl2_main.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2/boot_hal_bl2.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/host_drivers/ppu_drv.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/host_atu_base_address.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/CMakeCache.txt`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/bl2/src/flash_map.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/flash/strata/Driver_Flash_Strata.h`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/flash/strata/spi_strataflashj3_flash_lib.c`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/flash/cfi/cfi_drv.c`
- `arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/files/tf-m/fvp-rd-aspen/0063-rse-DMA-ICS-Write-LCM-seed-registers.patch`
- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/`
- `tools/qbox/platforms/fvp-rd-aspen/conf.lua`

## Review Follow-Up Notes

- The existing Cortex-M55 wrapper uses QEMU CPU type `cortex-m55-arm` through
  the local `aarch64` libqemu build.
- The NVIC CMake target is `nvic_armv7m`; using `armv7m_nvic` as a build
  target is incorrect even though that is the source directory name.
- The existing `mhuv3_stub` is compatibility debt for direct boot. RSE-oriented
  work should introduce a reusable MHUv3 PBX/MBX doorbell model and keep SCMI
  protocol responses in a separate SCP service model.
- Direct Lua instantiation of `cpu_arm_cortexM55` is syntactically viable.
  Use QEMU target string `AARCH64`, bind `rse_cpu.mem` to the RSE router, and
  map the internal NVIC at `0xE000E000`.
- The first RSE UART skeleton should use `char_backend_file` with explicit
  `read_file`, `write_file`, and `baudrate` parameters. Full fidelity still
  needs the RSE ATU path to host UART and other host windows.
- Direct Lua binding of `rse_cpu.nvic.mem` is not enough for `platforms-vp`
  because QBox name binding only processes immediate child bind parameters.
  The active skeleton now reuses the existing `RemoteCPU` wrapper through
  `RemotePass`, matching the `platforms/cortex-m55-remote` pattern where CPU
  memory accesses route through an internal router and the NVIC stays on the
  CPU-local `0xE000E000` system-control window.

## Validation Evidence

### 2026-05-20 RSE Helper And Build Smoke

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/compare_fvp_qbox_rse_logs.py` |
| QBox M-profile targets | pass | `cmake --build tools/qbox/build --target cpu_arm_cortexM55 nvic_armv7m --parallel 8` |
| Cortex-M55 smoke test | pass | `ctest --test-dir tools/qbox/build -R cortex_m55 --output-on-failure` |
| QBox platform runner | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 8` |
| QBox diff whitespace | pass | `git -C tools/qbox diff --check` |
| RSE helper smoke | expected fail | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --out-dir build/qbox-fvp-rd-aspen/rse-helper-smoke-v2` |
| Comparison helper smoke | expected fail | `python3 scripts/compare_fvp_qbox_rse_logs.py --fvp build/qbox-fvp-rd-aspen/rse-helper-smoke-v2 --qbox build/qbox-fvp-rd-aspen/rse-helper-smoke-v2 --output build/qbox-fvp-rd-aspen/rse-helper-smoke-v2/comparison.json` |

The RSE helper smoke wrote `result.json` and per-console placeholder logs under
`build/qbox-fvp-rd-aspen/rse-helper-smoke-v2/`. It correctly reported blocker
`rse_qbox_config_missing:/build/arm/arm-auto-solutions/tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`.
The default firmware artifacts, including `combined_provisioning_message.bin`,
were present. The comparison helper now reads run-directory `.log` files and
excludes generated summaries so marker names listed as `False` in summaries do
not produce false positives.

### 2026-05-20 RSE Skeleton Runtime Smoke

The native `$team` command could not be launched from this Codex/native
outside-tmux session because the local OMX hook rejects `omx team` outside tmux.
A read-only `qbox_dev` sub-agent review was used instead, and its findings were
applied to the runner and Lua skeleton.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/compare_fvp_qbox_rse_logs.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox RSE targets | pass | `cmake --build tools/qbox/build --target platforms-vp keep_alive router gs_memory loader char_backend_file char_backend_stdio uart-pl011 cpu_arm_cortexM55 nvic_armv7m remote_cpu --parallel 8` |
| RemotePass registration | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 8` after including `remote.h` in `platforms-vp` |
| RSE trace smoke | expected fail | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 5 --out-dir build/qbox-fvp-rd-aspen/rse-remote-cpu-trace-20260520-v3` |

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-remote-cpu-trace-20260520-v3/`

Runtime result:

- `passed: false`
- `blocker: rse_first_fault:0x501541c4`
- `platform_returncode: -15`
- `timed_out: true`
- reset vector evidence: SP `0x30005660`, PC `0x110004f5`
- first fatal access: write to `0x501541c4`, Data Abort
- source mapping: `0x501541c4 = CC3XX_BASE_S 0x50154000 + 0x1c4`

The earlier direct Lua CPU attempt reached the ROM reset vector but faulted on
the CPU-local NVIC/SCS window at `0xE000E008`. After switching to `RemoteCPU`,
the trace shows `NVIC: Bad read offset 0x8` and `NVIC: Bad write offset 0x8`,
but those accesses no longer cause the first fatal abort. The next blocker is
the unimplemented CC3XX/CRYPTOCELL register window. This 2026-05-20 blocker is
superseded by the 2026-05-21 evidence below, which removes the `0x501541c4`
Data Abort but still times out before RSE UART output.

### 2026-05-21 Early CC3XX And DMA350 Model Evidence

Implemented QBox components:

- `tools/qbox/systemc-components/cc3xx/`
- `tools/qbox/systemc-components/dma350/`

The CC3XX model is a limited early-boot functional model. It covers the TF-M
BL1_1 RNG startup path observed in `startup_bl1_1_helpers.h`, including
`rng_clk_enable`, `rng_sw_reset`, `sample_cnt1`, `rnd_source_enable`,
`rng_isr`, `rng_icr`, `rst_bits_counter`, deterministic EHR data, and selected
driver readiness/feature registers. It is not a full CRYPTOCELL model.

At this point in the timeline the DMA350 model was still a temporary
command-completion model. It exposed four channels through `DMASECINFO = 0x30`
and cleared channel `CH_CMD` writes immediately so BL1_1 STOP, CLEAR, and
ENABLE polling could progress. That limitation is superseded by the T019D fill
evidence below; full DMA350 trigger, interrupt, and DMA ICS behavior remains
open.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/compare_fvp_qbox_rse_logs.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox configure | pass | `cmake -S tools/qbox -B tools/qbox/build` |
| QBox RSE targets | pass | `cmake --build tools/qbox/build --target cc3xx dma350 platforms-vp --parallel 8` |
| RSE trace smoke | expected fail, no Data Abort | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 8 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v1` |
| CC3XX register trace | expected fail, RNG path progresses | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=1000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 6 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-trace-debug-20260521-v2` |
| Longer no-trace run | expected fail, no console markers | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-run-20260521-v1` |
| CC3XX/DMA350 unit regression | pass | `cmake --build tools/qbox/build --target cc3xx-tests dma350-tests --parallel 4 && ctest --test-dir tools/qbox/build -R 'cc3xx-tests|dma350-tests' --output-on-failure` |
| Task 2 CC3XX runtime regression | expected fail, no Data Abort | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=80 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 6 --out-dir build/qbox-fvp-rd-aspen/rse-task2-cc3xx-regression-20260521` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-cc3xx-trace-debug-20260521-v2/`
- `build/qbox-fvp-rd-aspen/rse-dma350-run-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-task2-cc3xx-regression-20260521/`

Runtime result:

- The previous `rse_first_fault:0x501541c4` Data Abort is removed.
- `first_failing_register_access` is now `null` when the trace has no
  exception or fault; the runner no longer reports the reset PC as a failing
  access.
- At this stage the blocker was `qbox_platform_timeout` with no RSE UART
  marker yet.
- CC3XX trace shows successful readback of `sample_cnt1 = 0x5dc`,
  `rnd_source_enable = 0x1`, `rng_isr = 0x1`, and deterministic EHR words.
- This result is superseded by the T019C trace below, which locates the
  no-console timeout in the BL1_1 DMA erase/fill path.

### 2026-05-21 T019C DTCM And DMA350 Trace Evidence

The T019C follow-up added the missing DTCM aliases used by the BL1_1 stack and
CC3XX DMA remap setup:

- secure DTCM: `0x30000000`
- secure CPU0 DTCM alias: `0x34000000`
- non-secure DTCM: `0x20000000`
- non-secure CPU0 DTCM alias: `0x24000000`
- DTCM size: `0x8000`

The DMA350 trace now shows BL1_1 discovering four channels and programming
channel erase/fill descriptors for DTCM and ITCM regions:

- `DMASECINFO` read value `0x30`, matching four channels.
- first fill destination range starts at `0x34000000`.
- second fill destination range starts at `0x1a000000`, the secure CPU0 ITCM
  alias.
- `CH_DESADDR`, `CH_XADDRINC`, `CH_XSIZE`, `CH_CTRL`, and `CH_CMD=ENABLE`
  are written for channels 0 through 3.

| Check | Result | Evidence |
| --- | --- | --- |
| Active config check | pass | `.config.yaml` records `MACHINE = "fvp-rd-aspen"`, `RD_ASPEN_VARIANT = "cfg2"`, `PC_CPUS_COUNT_DEFAULT = "4"` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox RSE targets | pass | `cmake --build tools/qbox/build --target dma350 dma350-tests platforms-vp --parallel 4` |
| CC3XX/DMA350 unit regression | pass | `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|dma350-tests' --output-on-failure` |
| DTCM/DMA350 register trace | expected fail, no Data Abort | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=120 QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=240 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v2` |
| PC trace | expected fail, no Data Abort | `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=80 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 12 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-qemu-trace-20260521-v2` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v2/`
- `build/qbox-fvp-rd-aspen/rse-dma350-qemu-trace-20260521-v2/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `first_failing_register_access: null`
- no RSE UART marker yet

PC trace source mapping:

- `0x1100082e`: `startup_dma_double_word_memset()`,
  `startup_bl1_1_helpers.h:166`
- `0x11000834`: `startup_dma_double_word_memset()`,
  `startup_bl1_1_helpers.h:169`
- later disassembly maps the next wait path to
  `wait_for_dma_operation_complete()` at `startup_bl1_1_helpers.h:192`
  and `erase_vm0_and_vm1()` in `startup_rse_bl1_1.c:240..246`

T019C is therefore closed as a location-identification task. The next
implementation task is T019D: replace the DMA350 command-completion temporary
stub with a minimal initiator-backed fill/data-movement model for this BL1_1
erase path before claiming progress to TF-M UART output.

### 2026-05-21 T019D DMA350 Fill Evidence

T019D replaced the DMA350 command-completion-only behavior with an
initiator-backed fill path for the observed BL1_1 erase sequence:

- `dma350` now exposes an optional initiator socket.
- `CH_CMD=ENABLE` reads `CH_DESADDR`, `CH_XSIZE`, `CH_XADDRINC`, and
  `CH_FILLVAL`.
- the observed one-dimensional 64-bit fill writes are issued through TLM
  writes to the RSE router.
- `CH_CMD` still auto-clears so BL1_1 polling semantics remain compatible.
- RSE ITCM aliases were added so the second BL1_1 fill at `0x1a000000`
  reaches real backing memory instead of an unmapped target.

This is not full DMA350 fidelity. The model still lacks copy transfers,
DMA ICS program execution, trigger inputs, status/fault registers, interrupts,
and security/attribute behavior.

| Check | Result | Evidence |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| DMA350 build | pass | `cmake --build tools/qbox/build --target dma350 dma350-tests --parallel 4` |
| CC3XX/DMA350 unit regression | pass | `ctest --test-dir tools/qbox/build -R 'dma350-tests|cc3xx-tests' --output-on-failure` |
| QBox platform runner | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 4` |
| DMA350 fill runtime trace | expected fail, blocker moved | `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=260 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-fill-20260521-v4` |
| Worker 1 focused verification | pass except expected short runtime timeout | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`; `git -C tools/qbox diff --check`; `cmake --build tools/qbox/build --target dma350 --parallel 4`; `cmake --build tools/qbox/build --target dma350-tests --parallel 4`; `cmake --build tools/qbox/build --target platforms-vp --parallel 4`; `ctest --test-dir tools/qbox/build -R 'cc3xx|dma350' --output-on-failure`; `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --qemu-trace --out-dir build/qbox-fvp-rd-aspen/worker-1-task5-rse-smoke-20260520T162759Z` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-dma350-fill-20260521-v4/`
- `build/qbox-fvp-rd-aspen/worker-1-task5-static-build-test-20260520T162738Z.log`
- `build/qbox-fvp-rd-aspen/worker-1-task5-rse-smoke-20260520T162759Z/`

Runtime result:

- `passed: false`
- `blocker: rse_first_fault:0x58021100`
- first fault source: `0x58021100 = RSE_SYSCTRL_BASE_S 0x58021000 +
  0x100`, `struct rse_sysctrl_t.reset_syndrome`
- trace evidence shows successful fill writes for:
  - DTCM CPU0 alias ranges `0x34000000..0x34007fff`
  - ITCM CPU0 alias ranges `0x1a000000..0x1a007fff`
- the shorter Worker 1 smoke also remains an expected runtime fail:
  `blocker: qbox_platform_timeout`, `timed_out: true`,
  `first_failing_register_access: null`, and
  `rse_dma350: functional-fill-model`. This smoke confirms the focused
  build/test path and runtime artifact generation, but the traced
  `rse-dma350-fill-20260521-v4` run remains the source for the
  `0x58021100` blocker location.

T019D is therefore closed as the minimal DMA350 fill/data-movement increment.
The follow-up T019E system-control register model is recorded below.

### 2026-05-21 T019E RSE System-Control Model Evidence

T019E added a narrow `rse_sysctrl` SystemC/TLM component and wired it into the
RSE local platform:

- `tools/qbox/systemc-components/rse_sysctrl/`
- `tools/qbox/tests/components/rse_sysctrl/`
- Lua instance `platform.rse_sysctrl` at `0x58021000`, size `0x1000`

The model is intentionally limited to the TF-M/FVP-touched register surface:
`reset_syndrome`, `reset_mask`, `swreset`, `gretreg`, `initsvtor0`,
`cpuwait`, `nmi_enable`, `pwrctrl`, `gretexreg`, `dma_boot_en`,
`dma_boot_addr`, and `lcm_dcu_force_dis`. It also implements simple
secure-debug set/clear register behavior for traceability. This is a
`touched-register-model`, not a full RSEIL system-control implementation.

Source evidence:

- FVP sets `RESET_SYNDROME_INIT_VAL=0x80000000` and
  `DMA_BOOT_EN_REG_RESET=1` in
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`.
- TF-M `platform_regs.h` places `reset_syndrome` at offset `0x100`,
  `reset_mask` at `0x104`, `swreset` at `0x108`, `cpuwait` at `0x120`,
  `dma_boot_en` at `0x254`, `dma_boot_addr` at `0x258`, and
  `lcm_dcu_force_dis` at `0x25c`.
- TF-M BL1_1 writes `rse_sysctrl->reset_mask |= (1U << 8U)` in
  `boot_hal_bl1_1.c`.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| RSE sysctrl build | pass | `cmake --build tools/qbox/build --target rse_sysctrl rse_sysctrl-tests --parallel 4` |
| CC3XX/DMA350/sysctrl unit regression | pass | `ctest --test-dir tools/qbox/build -R 'rse_sysctrl-tests|dma350-tests|cc3xx-tests' --output-on-failure` |
| QBox platform runner | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 4` |
| Sysctrl QEMU trace runtime | expected fail, previous fault removed | `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=260 QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v1` |
| Sysctrl no-trace runtime | expected fail, blocker moved | `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=220 QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v2` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v2/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `first_failing_register_access: null`
- `platform_returncode: -15`
- no RSE UART, RSE-SCP handoff, measured-boot, or Linux markers yet
- `fidelity_labels.rse_sysctrl = "touched-register-model"`

Key runtime evidence:

- QEMU trace no longer reports the previous `0x58021100` Data Abort; it shows
  the PMSA lookup for reading `0x58021100` as a mapped hit.
- `qbox-platform.log` shows:
  - `platform.rse_sysctrl read offset=0x100 len=0x4 value=0x80000000`
  - `platform.rse_sysctrl read offset=0x104 len=0x4 value=0x0`
  - `platform.rse_sysctrl write offset=0x104 len=0x4 value=0x100`

T019E is therefore closed as the minimal system-control register increment.
The follow-up T019F/T019G evidence below identifies the next post-`reset_mask`
location and adds the first ATU touched-register increment.

### 2026-05-21 T019F/T019G ATU And LCM Trace Evidence

T019F/T019G added a narrow ATU touched-register model and re-ran the RSE path
with system-control, ATU, and LCM tracing enabled:

- `tools/qbox/systemc-components/rse_atu/`
- `tools/qbox/tests/components/rse_atu/`
- Lua instance `platform.rse_atu_regs` at `0x50150000`, size `0x1000`
- non-secure host UART alias `0x6ff00000` wired to the RSE host UART PL011
- runner fidelity label `rse_atu = "touched-register-model"`

The model is intentionally limited. It provides `ATUBC = 0x000000c5`, writable
control/interrupt enable and region programming arrays, and clear-on-write
interrupt-clear behavior. It does not yet translate RSE ATU windows through a
TLM initiator socket and does not model disabled-region, out-of-range, DMI, or
permission faults.

| Check | Result | Evidence |
| --- | --- | --- |
| QBox configure | pass | `cmake --preset gcc` |
| RSE LCM build | pass | `cmake --build tools/qbox/build --target rse_lcm rse_lcm-tests --parallel 4` |
| RSE ATU build | pass | `cmake --build tools/qbox/build --target rse_atu rse_atu-tests --parallel 4` |
| RSE ATU/LCM unit regression | pass | `ctest --test-dir tools/qbox/build -R 'rse_atu-tests|rse_lcm-tests' --output-on-failure` |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| ATU/LCM runtime trace | expected fail, blocker narrowed | `QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=64 QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=128 QBOX_RDASPEN_LCM_TRACE=true QBOX_RDASPEN_LCM_TRACE_LIMIT=128 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-atu-trace-20260521-v1` |
| Runner required-target check | expected check-only blocker after successful target build | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --check-only --out-dir build/qbox-fvp-rd-aspen/rse-check-only-20260521-v1` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-atu-trace-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-check-only-20260521-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `first_failing_register_access: null`
- `platform_returncode: -15`
- `timed_out: true`
- RSE, SCP, secure-console, primary-console markers are still absent
- `fidelity_labels.rse_atu = "touched-register-model"`
- `fidelity_labels.rse_lcm = "otp-backed-register-model"`

The check-only artifact reports `blocker: check_only_no_runtime` after building
the runner's required QBox target list, including `rse_atu` and `rse_lcm`.
That artifact is build/preflight evidence only and is not runtime boot evidence.

Key runtime evidence from `qbox-platform.log`:

- system control still reaches:
  - `platform.rse_sysctrl read offset=0x100 len=0x4 value=0x80000000`
  - `platform.rse_sysctrl write offset=0x104 len=0x4 value=0x100`
- ATU initialization is now visible:
  - `platform.rse_atu_regs read offset=0x0 len=0x4 value=0xc5`
  - `platform.rse_atu_regs write offset=0x20 len=0x4 value=0x6ff00`
  - `platform.rse_atu_regs write offset=0xa0 len=0x4 value=0x6ff0f`
  - `platform.rse_atu_regs write offset=0x120 len=0x4 value=0x60400`
  - `platform.rse_atu_regs write offset=0x1a0 len=0x4 value=0x20`
  - `platform.rse_atu_regs write offset=0x4 len=0x4 value=0x1`
  - `platform.rse_atu_regs write offset=0x220 len=0x4 value=0xaaae`
- LCM/OTP reads follow ATU programming:
  - `platform.rse_lcm_regs read offset=0xc len=0x4 value=0x0`
  - `platform.rse_lcm_regs read offset=0x0 len=0x4 value=0xeeeea5a5`
  - `platform.rse_lcm_regs read offset=0x10f8 len=0x4 value=0x2b80278`
  - later reads continue through the OTP-backed window, including offsets
    `0x1530..0x16e0` within the trace limit.

T019F is therefore closed as a location-identification task: the previous
post-system-control uncertainty is now narrowed to the path after ATU
programming and LCM/OTP reads. T019G is closed as the minimal ATU
touched-register increment. The remaining work is still a blocker for RSE boot:
full ATU translation/fault behavior, LCM/OTP provisioning semantics, boot-media
write/lock behavior, and any later MPC or reset lifecycle side effects must be
modeled before the TF-M BL1_1 UART marker can be expected.

### 2026-05-21 T019H/T019I KMU And Integrity Checker Evidence

T019H/T019I added narrow RSE KMU and Integrity Checker components:

- `tools/qbox/systemc-components/rse_kmu/`
- `tools/qbox/tests/components/rse_kmu/`
- `tools/qbox/systemc-components/rse_integrity_checker/`
- `tools/qbox/tests/components/rse_integrity_checker/`
- Lua instance `platform.rse_kmu_regs` at `0x5009E000`, size `0x1000`
- Lua instance `platform.rse_integrity_checker_regs` at `0x5015C000`,
  size `0x1000`

The KMU model is a touched-register model. It implements the TF-M driver
layout for `KMUBC`, `KMUIS`, `KMUIE`, `KMUIC`, `KMUPRBGSI`, `KMUKSC`,
`KMUDKPA`, `KMUKSK`, `KMURD_8`, `KMURD_16`, `KMURD_32`, and PID/CID
registers. It models simple verify/export/invalidate completion bits but does
not yet perform destination-port key exports.

The Integrity Checker model is a touched-status model. It implements `ICBC`,
`ICC`, `ICIS`, `ICIE`, `ICAE`, `ICIC`, `ICDA`, `ICDL`, `ICEVA`, `ICCVA`,
`ICCVAL[8]`, and PID/CID registers. `ICC` start sets the done bit in `ICIS`,
but no digest computation or DMA/output side effect exists yet.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox configure | pass | `cmake --preset gcc` |
| KMU/Integrity Checker build | pass | `cmake --build tools/qbox/build --target rse_integrity_checker rse_integrity_checker-tests rse_kmu rse_kmu-tests --parallel 4` |
| RSE component regression | pass | `ctest --test-dir tools/qbox/build -R 'rse_(integrity_checker|kmu|atu|lcm)-tests' --output-on-failure` |
| QBox platform runner | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 4` |
| KMU/Integrity Checker runtime trace | expected fail, KMU reached | `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=256 QBOX_RDASPEN_INTEGRITY_CHECKER_TRACE=true QBOX_RDASPEN_INTEGRITY_CHECKER_TRACE_LIMIT=256 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-integrity-kmu-trace-20260521-v1` |
| KMU PC trace | expected fail, startup PC located | `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=512 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-kmu-pc-trace-20260521-v1` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-integrity-kmu-trace-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-kmu-pc-trace-20260521-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `first_failing_register_access: null`
- `platform_returncode: -15`
- `timed_out: true`
- no RSE UART, RSE-SCP handoff, measured-boot, or Linux markers yet
- `fidelity_labels.rse_kmu = "touched-register-model"`
- `fidelity_labels.rse_integrity_checker = "touched-status-model"`

Key runtime evidence:

- `qbox-platform.log` shows repeated
  `platform.rse_kmu_regs read offset=0x538 len=0x4 value=0x0`, matching
  `KMURD_32`.
- No `platform.rse_integrity_checker_regs` access is present in the runtime
  trace, so the Integrity Checker model is only build/unit evidence so far.
- `qemu-rse-trace.log` maps the timeout PC to `0x1100092e`.
  `llvm-addr2line` maps that address to `__cmsis_start` in
  `cmsis_gcc_m.h:64`; disassembly shows it is the BL1_1 C runtime copy-table
  loop immediately after `SystemInit()`.

T019H is closed as the minimal KMU register-surface increment. T019I is closed
for component implementation and registration, but runtime coverage remains
open because the firmware has not reached `0x5015C000`. T019J is closed as a
location-identification task. Later shared-memory and CC3XX hashing work
supersedes this copy-table blocker with the then-current BL2 decrypt blocker
recorded below.

### 2026-05-21 BL1_2 And CC3XX Crypto Progress Evidence

The follow-up implementation replaced the copy-table timeout with deeper RSE
boot progress:

- RSE volatile memories now use shared backing where required by the
  `RemoteCPU` split process, allowing BL1_1 C runtime data movement to become
  visible to the CPU path.
- `rse_sam` is wired at `0x5009F000`; the previous first fault at the SAM
  register window is removed.
- `cc3xx` now exposes an optional initiator socket and performs the observed
  SHA-256 DMA input path, updating `HASH_H[0..7]`.
- `cc3xx` sets the DMA completion interrupt bits required by the TF-M
  low-level driver polling loop.
- `cc3xx` has a focused AES-CTR memory-to-memory unit test using a published
  AES-128 CTR test vector. This proves the local AES counter path, but it does
  not yet prove the BL1_2 production key path.
- The RSE runner initializes invalid per-run RSE FWU private metadata at flash
  offset `0x5000` to slot 0/READY. It records the previous boot index and
  state bytes in `result.json` and does not modify the deploy
  `rse-flash-image.img`.

| Check | Result | Evidence |
| --- | --- | --- |
| Runner syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| FWU metadata preflight | expected check-only blocker after target build | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --check-only --out-dir build/qbox-fvp-rd-aspen/rse-fwu-metadata-check-20260521-v1` |
| CC3XX AES-CTR unit red/green | pass after implementation | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4`; `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure` |
| Focused RSE component regression | pass | `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|rse_sam-tests|rse_(integrity_checker|kmu|atu|lcm|sysctrl)-tests' --output-on-failure` |
| Platform build | pass | `cmake --build tools/qbox/build --target cc3xx-tests platforms-vp --parallel 4` |
| RSE BL1_2 runtime | expected fail, blocker moved | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-aes-20260521-v1` |
| CC3XX KDF trace | expected fail, KDF path identified | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=2500 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-aes-trace-20260521-v2` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-fwu-metadata-check-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-fwu-metadata-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-cc3xx-aes-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-cc3xx-aes-trace-20260521-v2/`

Runtime result from `rse-cc3xx-aes-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `first_failing_register_access: null`
- `platform_returncode: -15`
- `timed_out: false`
- RSE boot marker `Starting TF-M BL1_1` is present.
- Measured-boot string markers `BL1_2` and `BL2` are present, but this is not
  measured-boot success because later required markers are still absent.
- Linux and RSE-SCP handoff markers are absent.
- `rse_fwu_private_metadata.changed: true`
- previous per-run flash bytes at `0x5000` decoded as
  `previous_boot_index = 208`, `previous_fwu_states = [87, 133, 94, 27, 34]`
  and were rewritten in the run copy to `boot_index = 0` and all READY states.

RSE UART evidence:

```text
[INF] Noise Source config set to (0, 0x11)
[INF] [CC3XX] Init OK PIDR0: 0xc1
[INF] Starting TF-M BL1_1
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[ERR] BL2 image failed to decrypt
```

Key source/runtime diagnosis:

- Before the FWU private metadata initializer, BL1_2 printed
  `Attempting to boot image 208` and the PC trace looped in
  `bl1_image_get_flash_offset()` default panic handling.
- Initializing only the per-run writable flash copy moves BL1_2 to image slot
  0 and reaches BL2 decryption.
- The CC3XX trace shows AES-CMAC/KDF setup before decrypt:
  `AES_CONTROL = 0x201c`, `AES_CMAC_INIT = 0x1`, and DMA inputs from RSE DTCM.
- At this stage the trace did not show CC3XX `AES_KEY_0` writes from KMU
  export yet. This was superseded by the KMU export follow-up below.
- Local TF-M sources show BL1_2 derives the BL2 AES key through
  `cc3xx_lowlevel_kdf_cmac()` using `KMU_HW_SLOT_KCE_CM`, then decrypts BL2
  with AES-256 CTR.

The blocker at this stage was therefore no longer RSE startup/copy-table
execution. It was the missing KMU-to-CC3XX key export plus CC3XX
AES-CMAC/SP800-108 KDF behavior required before BL1_2 could decrypt BL2. This
diagnosis is superseded by the KMU export and AES-CMAC follow-up below.

### 2026-05-21 KMU Export And AES-CMAC Follow-Up Evidence

T019O/T019P added the first functional KMU export and AES-CMAC increment:

- `rse_kmu` now has an initiator socket. When firmware writes `KMUKSC.EK`,
  the model writes the selected slot words to the configured destination port
  and raises `KMUIS.KEC`.
- `fvp-rd-aspen-rse/conf.lua` binds `rse_kmu_regs.initiator_socket` to the
  RSE router so export writes can reach `rse_cc3xx` at `0x50154400`.
- `cc3xx` now accumulates CMAC DMA input in AES/CMAC mode and exposes the
  calculated tag through `AES_IV_0..3`, matching the TF-M low-level driver's
  `cmac_finish()` read path.

| Check | Result | Evidence |
| --- | --- | --- |
| KMU/CMAC focused build | pass | `cmake --build tools/qbox/build --target rse_kmu-tests cc3xx-tests --parallel 1` |
| KMU/CMAC focused unit regression | pass | `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|rse_kmu-tests' --output-on-failure` |
| Platform target build | pass | `cmake --build tools/qbox/build --target rse_kmu cc3xx platforms-vp --parallel 1` |
| RSE KMU/CMAC runtime | expected fail, blocker refined | `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=1024 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=5000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-cmac-20260521-v1` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-cc3xx-cmac-20260521-v1/`

Runtime result from `rse-cc3xx-cmac-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `first_failing_register_access: null`
- `timed_out: false`
- RSE UART still reaches BL1_1, BL1_2, and `Attempting to boot image 0`, then
  fails with `[ERR] BL2 image failed to decrypt`.

Key trace diagnosis:

- KMU export now reaches CC3XX key registers. The trace contains
  `rse_kmu_regs` slot/config writes followed by `rse_cc3xx write
  offset=0x400`, `0x404`, `0x408`, and `0x40c`.
- AES-CMAC is active. The trace shows `AES_CONTROL = 0x201c`,
  `AES_CMAC_INIT = 0x1`, `AES_REMAINING_BYTES` programming, DMA inputs from
  RSE DTCM, and non-zero reads from `AES_IV_0..3`.
- The same trace also shows the KDF root key load for `KMU_HW_SLOT_KCE_CM`
  exporting zero words into `AES_KEY_0..7` before CMAC. This means the current
  model can exercise export and CMAC, but it is deriving from zeroed hardware
  slot material rather than the provisioned FVP key hierarchy.
- TF-M's RD-Aspen configuration uses `CC3XX_CONFIG_AES_EXTERNAL_KEY_LOADER`;
  `set_key()` calls `kmu_export_key()` for hardware slots after checking locked
  key and export-config state. Therefore the next faithful model increment is
  OTP/provisioning-backed KMU hardware slot material, not a BL2-only decrypt
  shortcut.

The blocker after T019O/T019P is now classified as
`kmu_kce_cm_unprovisioned`: the KDF/CMAC path runs, but the root key material
does not match the generated RD-Aspen images. The MVP remains open until BL1_2
derives the same BL2 key as FVP and the AES-CTR decrypt magic check passes.

This classification is superseded by the OTP-backed KMU hardware-slot evidence
below. The KCE_CM material is no longer zero, but BL2 decrypt still fails.

### 2026-05-21 OTP-Backed KMU Hardware Slot Evidence

T019R/T019S added and validated the next KMU increment:

- `rse_kmu` has an `otp_image` CCI parameter.
- `fvp-rd-aspen-rse/conf.lua` passes the generated `rse-otp-image.img` path to
  the KMU model.
- On reset, the model loads LCM OTP hardware-key slots into KMU hardware slot
  word registers:
  - slot 1 HUK from OTP offset `0x00`
  - slot 2 GUK from OTP offset `0x20`
  - slot 3 KP_CM from OTP offset `0x40`
  - slot 4 KCE_CM from OTP offset `0x60`
  - slot 5 KP_DM from OTP offset `0x80`
  - slot 6 KCE_DM from OTP offset `0xa0`
- Slot 0 KRTL remains zero because the inspected LCM OTP hardware-key layout
  does not assign KRTL bytes in the generated image.

Source evidence:

- TF-M KMU hardware slot enum:
  `build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/drivers/kmu/kmu_drv.h`
- TF-M runtime secure image key setup:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/bl1/rse_kmu_keys.c`
- TF-M BL1 image encryption key mapping:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/bl1/cc3xx/cc3xx_rom_crypto.c`
- LCM OTP hardware-key offsets:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/common/lcm/lcm_otp_layout.h`
  and
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/platform/target/common/config/otp_layout.csv`
- Generated OTP input:
  `build/tmp_baremetal/deploy/images/fvp-rd-aspen/rse-otp-image.img`

The generated `rse-otp-image.img` contains KCE_CM at offset `0x60` with bytes:

```text
01 23 45 67 89 01 23 45 67 89 01 23 45 67 89 01
23 45 67 89 01 23 45 67 89 01 23 45 67 89 01 23
```

When exported to CC3XX through 32-bit little-endian register writes, the trace
shows those bytes as:

```text
AES_KEY_0..7 =
0x67452301 0x45230189 0x23018967 0x01896745
0x89674523 0x67452301 0x45230189 0x23018967
```

| Check | Result | Evidence |
| --- | --- | --- |
| KMU OTP unit build | pass | `cmake --build tools/qbox/build --target rse_kmu-tests --parallel 1` |
| KMU OTP unit regression | pass | `ctest --test-dir tools/qbox/build -R rse_kmu-tests --output-on-failure` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| Platform/KMU build | pass | `cmake --build tools/qbox/build --target rse_kmu platforms-vp --parallel 1` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| Runner syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| KCE_CM export runtime trace | expected fail, blocker moved | `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=2048 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=5000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-kce-cm-otp-20260521-v1` |
| KCE_CM no-trace runtime | expected fail, confirms UART blocker | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-kce-cm-otp-notrace-20260521-v1` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-kce-cm-otp-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-kce-cm-otp-notrace-20260521-v1/`

Runtime result from `rse-kce-cm-otp-notrace-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `first_failing_register_access: null`
- `timed_out: false`
- `platform_returncode: -15`
- RSE UART reaches BL1_1, BL1_2, and `Attempting to boot image 0`, then fails
  with `[ERR] BL2 image failed to decrypt`.
- RSE-SCP handoff, measured-boot completion, AP release, and Linux markers are
  still absent.

Blocker classification at this stage:

`cc3xx_kdf_ctr_fidelity_after_kce_cm`: KCE_CM is now sourced from the generated
OTP image and exported to CC3XX, but BL1_2 still fails the BL2 decrypt magic
check. The follow-up debug step was to compare the SP800-108 CMAC KDF
intermediate values and AES-CTR decrypt inputs/outputs with TF-M/FVP evidence,
including counter byte order, AES-256 key assembly, DMA completion/status
behavior, and any TF-M-touched CC3XX registers not yet modeled.

This classification is superseded by the raw flash-loader evidence below. The
KDF/AES-CTR path produces a valid BL2 decrypt result once QBox is given the
decompressed flash payload that FVP's flashloader presents to firmware.

### 2026-05-21 Raw RSE Flash Loader Follow-Up Evidence

T019T found that the generated deploy `rse-flash-image.img` is gzip-compressed:
its first bytes are `1f 8b 08`, while the decompressed payload is a
64 MiB flash image containing `bl2_signed.bin` at the expected boot-bank
offset. QBox was previously binding the compressed file directly to
`gs_memory`, unlike the FVP flashloader path that presents the uncompressed
flash contents to firmware. That made BL1_2 decrypt gzip bytes instead of the
BL2 image.

The RSE runner now detects gzip flash input and writes a per-run raw image:

- input: `writable-images/rse-flash-image.img`
- output: `writable-images/rse-flash-image.raw.img`
- state: `gzip_decompressed_for_qbox_raw_memory`
- compressed size: `1470386`
- raw size: `67108864`

The per-run FWU private metadata initializer runs on the raw image and leaves
the deploy artifact unchanged.

| Check | Result | Evidence |
| --- | --- | --- |
| Runner syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| Raw flash preflight | expected fail, no runtime | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-flash-prepare-check-20260521-v1` |
| Raw flash runtime | expected timeout, BL2 decrypt fixed | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-raw-flash-20260521-v1` |
| Raw flash QEMU trace | expected timeout, no exception | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 75 --out-dir build/qbox-fvp-rd-aspen/rse-raw-flash-qemu-trace-20260521-v1` |
| Raw flash long runtime | expected fail, blocker moved | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 600 --out-dir build/qbox-fvp-rd-aspen/rse-lmots-long-20260521-v1` |
| Raw flash classified runtime | expected fail, signature blocker classified | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-signature-fail-20260521-v1` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-flash-prepare-check-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-raw-flash-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-raw-flash-qemu-trace-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-lmots-long-20260521-v1/`
- `build/qbox-fvp-rd-aspen/rse-signature-fail-20260521-v1/`

Runtime result from `rse-raw-flash-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fail_patterns.[ERR]: false`
- `flash_image_preparation.state:
  gzip_decompressed_for_qbox_raw_memory`
- runtime `rse_flash` points to
  `writable-images/rse-flash-image.raw.img`

RSE UART evidence:

```text
[INF] Noise Source config set to (0, 0x11)
[INF] [CC3XX] Init OK PIDR0: 0xc1
[INF] Starting TF-M BL1_1
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
```

QEMU trace evidence from
`rse-raw-flash-qemu-trace-20260521-v1/qemu-rse-trace.log` reports no exception
or fault. Its tail remains in BL1_2 image-validation code mapped through
`build/bin/bl1_1.elf` debug information:

- `0x1100a3bc`: `hash_digit_array()`,
  `mbedtls/library/lmots.c:213`
- `0x1100a3da`: `hash_digit_array()`,
  `mbedtls/library/lmots.c:226`
- `0x1100a4ae`: `hash_digit_array()`,
  `mbedtls/library/lmots.c:287`
- `0x1100a590`: `mbedtls_lmots_calculate_public_key_candidate()`,
  `mbedtls/library/lmots.c:471`

Historical blocker classification before the CC3XX SHA-state fix:

`bl1_2_bl2_signature_validation_failed`: BL2 decrypt is now
successful, and the short trace showed the LMS/LMOTS verification loop was
executing without exception or Data Abort. The longer raw-flash runtime proves
that loop returns, but it returns failure before `BL2 image validated
successfully`, `Jumping to BL2`, or BL2's `Jumping to the first image slot`
marker.

Runtime result from `rse-signature-fail-20260521-v1/result.json`:

- `passed: false`
- `blocker: bl1_2_bl2_signature_validation_failed`
- `timed_out: false`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fail_patterns.[ERR]: true`
- `flash_image_preparation.state:
  gzip_decompressed_for_qbox_raw_memory`

RSE UART evidence from the long run:

```text
[INF] Noise Source config set to (0, 0x11)
[INF] [CC3XX] Init OK PIDR0: 0xc1
[INF] Starting TF-M BL1_1
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
[ERR] Signature validation failed
[ERR] BL2 image signature failed to validate
[ERR] BL2 image failed to validate
```

The TF-M source confirms the failing messages come from
`tfm/bl1/bl1_2/main.c`: `is_image_signature_valid()` reports `Signature
validation failed`, then `bl1_2_validate_image_at_addr()` reports `BL2 image
signature failed to validate`. The next debug step is to compare QBox and FVP
signature inputs: raw flash payload, protected image values, ROTPK/key
material, LMS/LMOTS verification behavior, PSA/CC3XX SHA behavior, and any
remaining boot-media side effect that can alter the validated bytes. The
follow-up evidence below supersedes this blocker: the missing behavior was
CC3XX SHA-256 multipart state restore through `HASH_H[0..7]` and
`HASH_CUR_LEN0/1`.

### 2026-05-21 CC3XX SHA State And BL2 Entry Evidence

Follow-up source inspection showed that TF-M's CC3XX PSA hash driver saves and
restores multipart hash state around LMS/LMOTS validation. The low-level driver
records `HASH_CUR_LEN0/1` and `HASH_H[0..7]`, then writes those registers back
before `psa_hash_finish()`. QBox previously computed SHA-256 digests but did
not expose the intermediate hash state through those registers, so BL1_2
signature validation consumed a reset SHA state after restore.

Implemented QBox coverage:

- `cc3xx` stores `HASH_CUR_LEN0/1` as DMA/software hash input accumulates.
- `cc3xx` writes intermediate and final SHA-256 words into `HASH_H[0..7]`.
- `cc3xx` accepts TF-M restore writes to `HASH_H[0..7]` and
  `HASH_CUR_LEN0/1`.
- `cc3xx-tests` adds a multipart SHA-256 restore regression that hashes one
  64-byte block, saves `HASH_H` and current length, restores the state, then
  finishes with `"abc"`.

| Check | Result | Evidence |
| --- | --- | --- |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| CC3XX focused build | pass | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4` |
| CC3XX focused regression | pass | `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure` |
| RSE no-trace runtime | expected timeout, BL2 reached | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-sha-state-20260521-v1` |
| RSE QEMU trace runtime | expected timeout, trace too slow for new blocker | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-bl2-qemu-trace-20260521-v1` |

Runtime result from `rse-cc3xx-sha-state-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fail_patterns.[ERR]: false`
- `flash_image_preparation.state:
  gzip_decompressed_for_qbox_raw_memory`

RSE UART evidence from `rse-cc3xx-sha-state-20260521-v1/qbox-rse.log`:

```text
[INF] Noise Source config set to (0, 0x11)
[INF] [CC3XX] Init OK PIDR0: 0xc1
[INF] Starting TF-M BL1_1
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
```

The `rse-bl2-qemu-trace-20260521-v1` trace was too slow to identify the new
timeout location. Within the 180-second trace window, RSE UART reached only
`BL2 image decrypted successfully`, and the QEMU trace tail remained inside
the LMS/LMOTS validation loop. It is retained only as evidence that the
signature-validation path was still executing under trace, not as source
mapping for the new BL2 timeout.

Current blocker classification:

`bl2_mcuboot_timeout_after_starting_bootloader`: BL1_2 now decrypts,
validates, and jumps to BL2. BL2 starts MCUboot and then times out with no
runner-detected `[ERR]` marker and no first failing register access. The next
debug path is BL2 image loading through the FVP-equivalent platform windows:
full RSE ATU translation, AP secure flash, AP shared SRAM, SI CL0/CL1 image
windows, and any boot-media side effects that BL2 expects before it can reach
`Jumping to the first image slot`.

### 2026-05-21 ATU Translation, Host Windows, And PPU Evidence

The BL2/MCUboot timeout after `Starting bootloader` was narrowed and moved by
three follow-up increments:

- RSE integration-layer registers at `0x58100000` were added so BL2 can finish
  early platform post-init and reach PSA Crypto initialization.
- The `rse_atu` component was upgraded from touched-register behavior to a
  target/initiator translation model for configured secure and non-secure
  windows.
- AP/SI host windows and a narrow `host_ppu` component were added so BL2 can
  access translated SI PIK/PPU registers and copy SI CL0 data into the
  translated SI CL0 SRAM window.

Implemented QBox coverage:

- `tools/qbox/systemc-components/rse_atu/` now exposes a translation initiator
  socket, forwards enabled-region accesses, grants translated DMI ranges for
  mapped host memory, invalidates DMI on mapping changes, and reports unmapped
  translation errors.
- `tools/qbox/systemc-components/host_ppu/` implements the touched `PWPR`,
  `PMER`, and `PWSR` surface. Writes to `PWPR` mirror the low policy bits into
  `PWSR` so the TF-M PPU polling loop can complete.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` now wires AP flash, the
  host router, ATU translation, RSE integration-layer registers, SI PIK/SCR,
  SI CL0/CL1 CUB windows, SI CL0 PPU subwindows, AP/SI SRAM windows, and
  RSE/AP mailbox windows used by the current BL2 path.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` now requires `host_ppu` and can
  classify first failing ATU translation errors from `qbox-platform.log` when
  QEMU tracing does not produce a CPU exception record.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox configure | pass | `cmake -S tools/qbox -B tools/qbox/build` |
| Host PPU build and platform build | pass | `cmake --build tools/qbox/build --target host_ppu-tests platforms-vp --parallel 4` |
| Host PPU component regression | pass | `ctest --test-dir tools/qbox/build -R host_ppu-tests --output-on-failure` |
| RSE integration-layer trace | expected fail, next blocker found | `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-integ-layer-20260521-v1` |
| RSE host-window trace | expected fail, PPU polling reached | `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=4096 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-host-windows-20260521-v1` |
| RSE host-PPU runtime | expected fail, blocker moved | `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=4096 QBOX_RDASPEN_HOST_PPU_TRACE=true QBOX_RDASPEN_HOST_PPU_TRACE_LIMIT=128 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-host-ppu-20260521-v2` |

Runtime result from `rse-host-ppu-20260521-v2/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_atu: translation-model`

RSE UART evidence from `rse-host-ppu-20260521-v2/qbox-rse.log`:

```text
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
[INF] BL2: SI LBIST happens here
[INF] BL2: SI CL1 not present, skip loading
[INF] BL2: SI CL0 pre load start
[INF] BL2: SI MBIST happens here
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
```

Translation and PPU evidence from `qbox-platform.log`:

- `rse-integ-layer-20260521-v1` first exposed the missing SI PIK host window:
  `translate_read logical=0x7540a000 physical=0x400002a600000 len=0x4
  status=error`.
- `rse-host-windows-20260521-v1` then translated SI PIK status reads
  successfully, but remained in a PPU status polling loop.
- `rse-host-ppu-20260521-v2` shows the SI CL0 cluster PPU accepting
  `PWPR = 0x8` and returning `PWSR = 0x8`, then shows many translated writes
  into SI CL0 SRAM, for example
  `translate_write logical=0x70084000 physical=0x4000120000000 len=0x4
  status=ok`.

Current blocker classification:

`bl2_si_cl0_slot_version_timeout`: BL2 now reaches PSA Crypto initialization,
SI LBIST/MBIST placeholders, SI CL0 pre-load completion, and MCUboot primary
and secondary slot version output. The next debug path is no longer initial
ATU translation or PPU polling; it is the post-version SI CL0 image
validation/loading path, including CC3XX use in BL2, AP/SI flash contents,
remaining host-window side effects, and ATU permission/page semantics.

### 2026-05-21 Optional ATU DMI And CC3XX PKA Evidence

Translated DMI support was added to the RSE ATU, but the first runtime
experiment was not a default-path improvement. At that point, the
host-PPU path in `rse-host-ppu-20260521-v2` reached SI CL0 pre-load
completion and primary/secondary slot version output, while the DMI experiment
stopped earlier after BL2 PSA Crypto initialization. The feature remains gated
behind `QBOX_RDASPEN_ATU_DMI=true` until it is stabilized. The active TF-M BL2
build has `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`, so this timeout was not caused by
BL2 DMA350 memcpy. Later evidence supersedes both this early DMI experiment
and the modular-PKA progress point: the current path reaches SI CL0 pre-load,
primary/secondary slot version output, and the image 3 RAM-load failure.

Implemented QBox coverage:

- `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` now translates
  downstream DMI ranges back to the ATU logical window and invalidates upstream
  DMI on mapping changes or downstream invalidation.
- `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` covers translated DMI
  grant behavior and unmapped DMI rejection without latching a translation
  fault.
- `tools/qbox/systemc-components/dma350/include/dma350.h` now covers the
  1D copy register path used by TF-M DMA350 code, even though the current BL2
  runtime image does not enable `PLATFORM_HAS_BOOT_DMA`.

| Check | Result | Evidence |
| --- | --- | --- |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| ATU/platform build | pass | `cmake --build tools/qbox/build --target rse_atu-tests platforms-vp --parallel 4` |
| CC3XX/DMA350/ATU regression | pass | `ctest --test-dir tools/qbox/build -R 'rse_atu-tests|dma350-tests|cc3xx-tests' --output-on-failure` |
| ATU DMI runtime | expected fail, opt-in regression | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-atu-dmi-20260521-v1` |
| CC3XX trace runtime | expected fail, PKA path captured | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-after-atu-dmi-20260521-v1` |

Runtime result from `rse-atu-dmi-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_atu: translation-model` in the generated artifact; the
  runner label now reports `translation-dmi-model` only when
  `QBOX_RDASPEN_ATU_DMI=true`.

RSE UART evidence from `rse-atu-dmi-20260521-v1/qbox-rse.log`:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
```

CC3XX trace evidence from
`rse-cc3xx-after-atu-dmi-20260521-v1/qbox-platform.log`:

- PKA readiness polling uses `PKA_PIPE_RDY` at `0x0b0` and `PKA_DONE` at
  `0x0b4`.
- PKA setup writes `OPCODE` at `0x080`, `PKA_STATUS` is read at `0x088`, and
  SRAM accesses use `PKA_SRAM_ADDR`/`WDATA`/`RDATA`/`RADDR` at
  `0x0d4`/`0x0d8`/`0x0dc`/`0x0e4`.
- The next implementation step is not another host-window stub. It is a
  CRYPTOCELL PKA model deep enough for TF-M EC-P256 verification.

Current blocker classification:

Historical default path before PKA-basic modeling:
`bl2_si_cl0_slot_version_timeout`. QBox reached BL2, PSA Crypto init, SI CL0
pre-load completion, and primary/secondary slot version output before timing
out.

Optional DMI path: `cc3xx_pka_alu_required`. The DMI branch reaches BL2 PSA
Crypto init and the CC3XX trace shows TF-M exercising the CRYPTOCELL PKA
programming model. This section is superseded by the PKA-basic evidence below,
which implements the first SRAM/ALU increment and moves the remaining
classification to `cc3xx_pka_ecp256_remaining`.

### 2026-05-21 CC3XX PKA Basic ALU Evidence

QBox now implements the first CRYPTOCELL PKA fidelity increment in the CC3XX
model. The implementation adds word-addressed PKA SRAM cursor access through
`PKA_SRAM_ADDR`/`PKA_SRAM_WDATA` and `PKA_SRAM_RADDR`/`PKA_SRAM_RDATA`, then
executes the basic ADD/SUB/AND/OR/XOR opcode family over mapped physical PKA
registers. This is still below full CRYPTOCELL fidelity because modular
multiply, modular inverse, modular exponentiation, reduction, division, shifts,
and EC point-operation behavior are not implemented.

Implemented QBox coverage:

- `tools/qbox/systemc-components/cc3xx/include/cc3xx.h` now has PKA SRAM
  state, read/write cursors, opcode decode, status updates, and basic ALU
  execution.
- `tools/qbox/tests/components/cc3xx/cc3xx-tests.cc` covers PKA SRAM streaming
  and the captured TF-M `0x210e10c0` ADD-immediate pattern.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` reported the CC3XX fidelity label as
  `hash-aes-cmac-basic-pka-model` for that increment; the later modular-PKA
  increment supersedes this label.

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| CC3XX component build | pass | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4` |
| CC3XX component regression | pass | `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure` |
| QBox targeted build and regression | pass | `cmake --build tools/qbox/build --target platforms-vp rse_atu-tests dma350-tests --parallel 4 && ctest --test-dir tools/qbox/build -R 'rse_atu-tests|dma350-tests|cc3xx-tests' --output-on-failure` |
| PKA-basic default runtime | expected fail, next crypto gap exposed | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-add-20260521-v1` |
| PKA-basic CC3XX trace runtime | expected fail, PKA ADD/SUB verified | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=2048 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-add-trace-20260521-v1` |

Runtime result from `rse-cc3xx-pka-add-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_cc3xx: functional-model` in that generated artifact;
  this historical artifact predates the explicit PKA fidelity labels.

RSE UART evidence from `rse-cc3xx-pka-add-20260521-v1/qbox-rse.log`:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
```

PKA trace evidence from
`rse-cc3xx-pka-add-trace-20260521-v1/qbox-platform.log`:

- `opcode=0x210e10c0` executes ADD-immediate on the mapped PKA register at
  SRAM word address `0x18`; the subsequent reads return `0x180b3de6`,
  `0x68c768bb`, `0x9ef06075`, `0x57e60e24` after the original first word
  `0x180b3de5`.
- `opcode=0x290e10c0` executes SUB-immediate on the same register; the
  subsequent reads return the original first word `0x180b3de5`.

Historical blocker classification for the basic-ALU increment:

`cc3xx_pka_ecp256_remaining`: basic PKA SRAM/ALU behavior now executes, but
BL2 still times out after PSA Crypto initialization. The next CC3XX increment
needs the modular PKA operations and status semantics used by TF-M EC-P256
verification, not another register-readiness shortcut.

### 2026-05-21 CC3XX PKA Modular Arithmetic Evidence

QBox now implements the next CRYPTOCELL PKA fidelity increment in the CC3XX
model. The implementation keeps the SRAM cursor and basic ALU behavior from the
previous increment, then adds the TF-M low-level driver semantics for:

- `PKA_STATUS` bit 8 `ALU_SIGN_OUT` for `cc3xx_lowlevel_pka_less_than()`.
- Shift opcodes `SHR0`, `SHR1`, `SHL0`, and `SHL1`, including TF-M's encoded
  immediate shift amount.
- `MODADD`, `MODSUB`, `MULLOW`, `MULHIGH`, `DIV`, `MODMUL`, `MODEXP`,
  `MODINV`, and `REDUCTION` over little-endian mapped PKA words.
- `DIV` quotient/result plus dividend-register remainder behavior matching the
  TF-M temporary-register wrapper.

Updated QBox coverage:

- `tools/qbox/systemc-components/cc3xx/include/cc3xx.h` uses
  `boost::multiprecision::cpp_int` for bounded unsigned PKA arithmetic while
  preserving the existing C++14/SystemC component shape.
- `tools/qbox/tests/components/cc3xx/cc3xx-tests.cc` now covers subtract
  status bit 8, shifts, modular add/sub/mul, multiply high/low, division
  quotient/remainder, reduction, modular exponentiation, and modular inverse.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` reports the CC3XX fidelity label as
  `hash-aes-cmac-modular-pka-model`.

| Check | Result | Evidence |
| --- | --- | --- |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| CC3XX component build | pass | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4` |
| CC3XX component regression | pass | `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure` |
| QBox targeted build | pass | `cmake --build tools/qbox/build --target platforms-vp rse_atu-tests dma350-tests cc3xx-tests --parallel 4` |
| QBox targeted regression | pass | `ctest --test-dir tools/qbox/build -R 'rse_atu-tests|dma350-tests|cc3xx-tests' --output-on-failure` |
| PKA-modular default runtime | expected fail, same EC-P256 timeout | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-mod-20260521-v1` |
| PKA-modular trace runtime | expected fail, early ADD/SUB trace plus updated fidelity label | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=20000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-mod-trace-20260521-v1` |

Runtime result from `rse-cc3xx-pka-mod-trace-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_cc3xx: hash-aes-cmac-modular-pka-model`

RSE UART evidence from `rse-cc3xx-pka-mod-trace-20260521-v1/qbox-rse.log`:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
```

Trace note:

- `QBOX_RDASPEN_CC3XX_TRACE_LIMIT=20000` is consumed before the EC-P256 timeout.
  The captured PKA opcode writes are still the early `0x210e10c0` ADD-immediate
  and `0x290e10c0` SUB-immediate sequence. This result is superseded by the
  later filtered PKA and PC-trace evidence: the current timeout maps to BL2
  `exception_handler()` and needs exception-cause capture before another broad
  CC3XX trace.

### 2026-05-21 CC3XX PKA Filtered Trace / T019AA Evidence

A focused CC3XX trace filter was added to avoid exhausting the trace budget on
unrelated CC3XX traffic while investigating the post-BL2 EC-P256 timeout.
`tools/qbox/systemc-components/cc3xx/include/cc3xx.h` now exposes a CCI
`trace_filter` parameter, and
`tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` maps
`QBOX_RDASPEN_CC3XX_TRACE_FILTER` into that parameter. Supported filters are
`all`, `pka`, `pka-opcode`, and `crypto`.

| Check | Result | Evidence |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| CC3XX component build | pass | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4` |
| CC3XX component regression | pass | `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure` |
| QBox platform build | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 4` |
| PKA-filtered runtime | expected fail, no late PKA traffic after PSA Crypto init | `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=pka QBOX_RDASPEN_CC3XX_TRACE_LIMIT=200000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-filter-trace-20260521-v1` |

Runtime result from
`rse-cc3xx-pka-filter-trace-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_cc3xx: hash-aes-cmac-modular-pka-model`

RSE UART evidence from
`rse-cc3xx-pka-filter-trace-20260521-v1/qbox-rse.log`:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
```

Filtered trace result:

- `qbox-platform.log` contains 523 lines, so the 200000-line trace budget was
  not consumed.
- The last captured PKA operations are the early BL2 PSA Crypto setup sequence:
  SRAM writes followed by opcode `0x210e10c0` and `PKA_SRAM_RDATA` reads.
- Because the run still reaches `PSA Crypto init done, sig_type: EC-P256`, the
  filtered trace refines T019AA: the remaining timeout is not explained by a
  stream of later PKA opcodes. The next probe should locate the current CPU
  execution site or capture non-PKA CC3XX/EC completion behavior before adding
  another CRYPTOCELL model increment.

### 2026-05-21 RSE PC Trace / BL2 Exception Handler Evidence

T019AA added a lightweight file-backed current-PC probe because full QEMU
instruction tracing is too slow for the post-BL2 timeout and the existing
register traces did not expose a first failing access.

Implemented probe surface:

- `tools/qemu/libqemu/wrappers/cpu.c` and `cpu.h` export
  `libqemu_cpu_get_pc()` through the generated libqemu export table.
- `tools/qbox/qemu-components/common/src/libqemu-cxx/cpu.cc` exposes
  `qemu::Cpu::get_pc()` and keeps `get_mem_io_pc()` for MMIO provenance.
- `tools/qbox/qemu-components/common/include/cpu.h` adds disabled-by-default
  `trace_pc`, `trace_pc_file`, `trace_pc_interval`, and `trace_pc_limit` CCI
  parameters. Samples are emitted at CPU loop sync boundaries.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` maps
  `QBOX_RDASPEN_RSE_PC_TRACE*` environment variables to the nested remote CPU.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` adds `--pc-trace`,
  `--pc-trace-interval`, and `--pc-trace-limit`, then records the parsed
  trace summary in `result.json` and `summary.txt`.

| Check | Result | Evidence |
| --- | --- | --- |
| Runner syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QEMU whitespace | pass | `git -C tools/qemu diff --check` |
| QBox/libqemu targeted build | pass | `cmake --build tools/qbox/build --target remote_cpu platforms-vp --parallel 4` |
| RSE PC trace runtime | expected timeout, PC mapped | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --pc-trace --pc-trace-interval 200 --pc-trace-limit 5000 --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-pc-trace-20260521-v2` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-pc-trace-20260521-v2/`

Runtime result from `rse-pc-trace-20260521-v2/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `rse_pc_trace.sample_count: 1479`
- `rse_pc_trace.last_sample.pc: 0x3101d80c`
- `rse_pc_trace.last_sample.sc_time: 299764378734 ns`
- `rse_pc_trace.tail_unique_pcs: ["0x3101d80c"]`

RSE UART evidence from `rse-pc-trace-20260521-v2/qbox-rse.log`:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] [CC3XX] Init OK PIDR0: 0x0
[INF] PSA Crypto init done, sig_type: EC-P256
```

PC source mapping:

```bash
llvm-addr2line \
  -e build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/bl2.elf \
  -f -C 0x3101d80c
```

```text
exception_handler
/usr/src/debug/trusted-firmware-m/2.2.2+git/platform/ext/target/arm/rse/common/device/source/startup_rse_bl.c:47
```

Disassembly around the mapped address:

```text
3101d80c <exception_handler>:
3101d80c: e7fe          b 0x3101d80c <exception_handler>

3101d80e <invalid_irq_handler>:
3101d80e: e7fe          b 0x3101d80e <invalid_irq_handler>
```

Blocker classification:

`bl2_exception_handler_after_psa_crypto`: the current timeout is no longer an
unlocated EC-P256/PKA arithmetic loop. After PSA Crypto initialization, the RSE
Cortex-M55 reaches BL2's default exception handler and spins there. The T019AB
exception-state probe below captures the active fault state and promotes the
next work item to a concrete host-window/ATU fault.

### 2026-05-21 RSE Exception State Trace / T019AB Evidence

T019AB extends the lightweight PC trace so that an Arm M-profile CPU sample can
also record exception and fault registers. This keeps the default runtime path
quiet while allowing file-backed post-mortem analysis when the PC lands in a
default exception handler.

Implemented probe surface:

- `tools/qemu/libqemu/wrappers/target/arm.c` and `arm.h` export
  `libqemu_cpu_arm_v7m_get_state()`, limited to Arm M-profile CPUs.
- `tools/qbox/qemu-components/common/include/libqemu-cxx/target/aarch64.h`
  and `src/libqemu-cxx/target/aarch64.cc` expose
  `qemu::CpuArm::get_v7m_state()`.
- `tools/qbox/qemu-components/common/include/cpu.h` adds disabled-by-default
  `trace_exception_state` sampling for xPSR, active exception, security state,
  general registers, CFSR/HFSR/DFSR/SFSR, BFAR/MMFAR/SFAR, vector bases, masks,
  and stack-limit state.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` maps
  `QBOX_RDASPEN_RSE_EXCEPTION_TRACE=true` to the nested remote CPU.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` adds `--exception-trace`, parses
  appended `key=value` fields, records `last_exception_state` in `result.json`,
  and classifies nonzero exception state before a generic timeout blocker.

| Check | Result | Evidence |
| --- | --- | --- |
| Runner syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QEMU whitespace | pass | `git -C tools/qemu diff --check` |
| QBox/libqemu targeted build | pass | `cmake --build tools/qbox/build --target remote_cpu platforms-vp --parallel 4` |
| RSE exception trace runtime | expected timeout, fault classified | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --exception-trace --pc-trace-interval 200 --pc-trace-limit 5000 --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-exception-trace-20260521-v2` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-exception-trace-20260521-v2/`

Runtime result from `rse-exception-trace-20260521-v2/result.json`:

- `passed: false`
- `blocker: bl2_exception_handler_after_psa_crypto`
- `timed_out: true`
- `rse_pc_trace.sample_count: 890`
- `rse_pc_trace.last_sample.pc: 0x3101d80c`
- `rse_pc_trace.tail_unique_pcs: ["0x3101d80c"]`
- `rse_pc_trace.last_exception_state.exception: 3`
- `rse_pc_trace.last_exception_state.exception_name: HardFault`
- `rse_pc_trace.last_exception_state.secure: 1`
- `rse_pc_trace.last_exception_state.xpsr: 0x1000003`
- `rse_pc_trace.last_exception_state.lr: 0xfffffff9`
- `rse_pc_trace.last_exception_state.hfsr: 0x40000000`
- `rse_pc_trace.last_exception_state.cfsr_ns: 0x8200`
- `rse_pc_trace.last_exception_state.cfsr_s: 0x0`
- `rse_pc_trace.last_exception_state.bfar: 0x7540a000`
- `rse_pc_trace.last_exception_state.vtor_s: 0x3101cd00`

Fault-state interpretation:

- `exception = 3` is HardFault.
- `HFSR = 0x40000000` is the FORCED bit, so a configurable fault escalated to
  HardFault.
- `CFSR_NS = 0x8200` decodes as BusFault `PRECISERR` plus `BFARVALID`.
- `BFAR = 0x7540a000` is therefore a valid precise fault address.
- `0x7540a000` lies in the RSE secure host-access logical window and matches
  the earlier ATU trace address that translated to the SI PIK host physical
  window at `0x400002a600000`.

First sampled transition into the exception handler:

```text
PREV: pc=0x31021764 exception=0 r5=0x500a22d0 r6=0x3100635c
CURR: pc=0x3101d80c exception=3 hfsr=0x40000000 cfsr_ns=0x8200 bfar=0x7540a000
```

Source mapping for the previous sampled PC and final handler PC:

```bash
llvm-addr2line \
  -e build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/bl2.elf \
  -f -C 0x31021764 0x3101d80c
```

```text
software_zero_count_compute
/usr/src/debug/trusted-firmware-m/2.2.2+git/platform/ext/target/arm/rse/common/rse_zero_count.c:60
exception_handler
/usr/src/debug/trusted-firmware-m/2.2.2+git/platform/ext/target/arm/rse/common/device/source/startup_rse_bl.c:47
```

Blocker classification:

At the T019AB checkpoint, `bl2_exception_handler_after_psa_crypto` had a
concrete fault signature: HardFault forced by a precise non-secure CFSR
BusFault at `0x7540a000`. T019AB is complete as an evidence task. The follow-up
implementation task was T019AC, which is resolved by the ATU range fix recorded
below.

## 2026-05-21 T019AC RSE ATU Region Range Fix

T019AC resolved the BL2 precise bus fault at RSE host-access logical address
`0x7540a000`.

Root cause:

- The `rse_atu` range check skipped regions only when `logical < start` or the
  access length exceeded `end - logical`.
- For an enabled lower region where `logical > end`, unsigned subtraction
  underflowed, so region 0 incorrectly matched the later SI PIK access.
- The bad match translated `0x7540a000` with region 0's offset pages
  `0x2000060400`, producing unmapped physical address `0x20000d580a000`.

Implementation:

- `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` now rejects
  `logical >= end` before computing `end - logical`.
- ATU translation tracing now includes the selected region and offset-page
  value, making future region-selection faults visible in file-backed logs.
- `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` adds high SI PIK
  translation coverage and a multi-region regression that verifies a lower
  enabled region is skipped when the access is above its end.

| Check | Result | Evidence |
| --- | --- | --- |
| QBox ATU/platform build | pass | `cmake --build tools/qbox/build --target rse_atu-tests platforms-vp --parallel 4` |
| RSE ATU component regression | pass | `ctest --test-dir tools/qbox/build -R rse_atu-tests --output-on-failure` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| RSE runtime re-check | expected timeout, earlier fault removed | `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=20000 QBOX_RDASPEN_HOST_PPU_TRACE=true QBOX_RDASPEN_HOST_PPU_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --exception-trace --pc-trace-interval 200 --pc-trace-limit 6000 --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4/`

Runtime result from `rse-t019ac-atu-host-trace-20260521-v4/result.json`:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `first_failing_register_access: null`
- `rse_pc_trace.last_exception_state.exception: 0`
- `rse_pc_trace.last_exception_state.exception_name: Thread`
- `rse_pc_trace.last_exception_state.hfsr: 0x0`
- `rse_pc_trace.last_exception_state.cfsr_ns: 0x0`
- `rse_pc_trace.last_exception_state.bfar: 0x0`
- `rse_pc_trace.tail_unique_pcs: ["0x31024c9c", "0x31023136"]`

Key runtime log evidence:

```text
platform.host_si_pik read offset=0x0 len=0x4 value=0x0
platform.rse_atu_regs translate_read logical=0x7540a000 physical=0x400002a600000 len=0x4 status=ok region=12 offset_pages=0x3ffffb51f6
platform.host_si_pik write offset=0x0 len=0x4 value=0x5
platform.rse_atu_regs translate_write logical=0x7540a000 physical=0x400002a600000 len=0x4 status=ok region=12 offset_pages=0x3ffffb51f6
```

```text
[INF] BL2: SI LBIST happens here
[INF] BL2: SI CL1 not present, skip loading
[INF] BL2: SI CL0 pre load start
[INF] BL2: SI MBIST happens here
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
```

Blocker classification:

The `0x7540a000` HardFault is resolved. The next artifact root below maps the
post-SI-CL0 slot-version timeout to the BL2 RSE flash read path and then uses
an opt-in translated-DMI run to expose an explicit SI CL0 image 3 RAM-load
failure.

### 2026-05-21 T019W SI CL0 RAM-Load Blocker Evidence

T019W turns the previous post-slot-version timeout into a specific BL2
image-loading blocker. The default non-DMI trace does not show an exception or
first failing translated register access; it is still executing in the RSE
flash read path while MCUboot copies image 3. The opt-in translated-DMI path
then reaches an explicit MCUboot error for the same image, so the next task is
the SI CL0 image load path rather than another generic ATU/PPU bring-up change.

Source mapping from
`build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4/`:

- `0x31024c9c` maps to `nor_cfi_reg_read()` in `cfi_drv.c:54`.
- `0x31023136` maps to `cfi_strataflashj3_read()` in
  `spi_strataflashj3_flash_lib.c:213`.
- The sampled register state includes destination `r11 = 0x70083c00` and flash
  base `r9 = 0xb0000000`, matching the later explicit MCUboot RAM-load
  failure.

TF-M/MCUboot source evidence:

- `RSE_FIRMWARE_SI_CL0_ID` is image ID 3 in
  `tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2_image_id.h`.
- `boot_load_image_to_sram()` calls `boot_copy_image_to_sram()` and logs
  `Image %d RAM loading to 0x%x is failed` when the flash-to-SRAM copy returns
  a non-zero status.
- `boot_copy_image_to_sram()` reads the active flash area into
  `IMAGE_RAM_BASE + img_dst` through `flash_area_read()`.
- For image 3, `boot_get_image_exec_ram_info()` sets the executable RAM range
  to `HOST_SI_CL0_IMG_HDR_BASE_S..HOST_SI_CL0_IMG_HDR_BASE_S +
  HOST_SI_CL0_ATU_SIZE`.
- `boot_platform_post_load_si_cl0()` would print
  `BL2: SI CL0 post load start`, but the latest logs do not reach that marker.

Opt-in DMI runtime evidence:

| Check | Result | Evidence |
| --- | --- | --- |
| ATU DMI runtime | expected fail, blocker made explicit | `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019w-atu-dmi-20260521-v1` |

Runtime result from `rse-t019w-atu-dmi-20260521-v1/result.json`:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `timed_out: false`
- `platform_returncode: -15`
- `fidelity_labels.rse_atu: translation-dmi-model`
- `first_failing_register_access: null`
- `fail_patterns.[ERR]: true`

RSE UART evidence:

```text
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 0 from flash
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 1 from flash
[INF] No slot to load for image 3
[ERR] Unable to find bootable image
```

Blocker classification:

`si_cl0_image3_ram_load_failed`: the next missing behavior is in the SI CL0
image 3 load path from RSE flash into the ATU-translated SI CL0 host SRAM
window. Candidate causes to investigate before adding more static placeholders
are flash/NVM read semantics, translated host-window writes, translated DMI
coherence, SI CL0 header/code window layout, and MCUboot validation or
flash-remove side effects. T019AE later rules out an active DMA350
`boot_dma_memcpy()` path for this generated TF-M image.

### 2026-05-21 T019AD Flash-To-Host-SRAM Copy Path Narrowing

T019AD narrows the image 3 failure away from late CC3XX DMA programming and
toward the RAM-load flow that starts with the flash-to-host-SRAM copy. The SI
CL0 image is encrypted and RAM-loaded, but the single MCUboot error log does
not by itself prove that the initial copy failed; the same log also covers
later encrypted-image setup and decrypt failures.

Source evidence:

- `mcuboot/boot/bootutil/src/ram_load.c`:
  `boot_decrypt_and_copy_image_to_sram()` first calls
  `flash_area_read(fap_src, 0, ram_dst, src_sz)`. If that returns non-zero,
  control goes directly to the `Image 3 RAM loading to 0x70083c00 is failed`
  log path.
- The same function also returns non-zero through the same top-level log path
  if `boot_enc_load()`, `boot_enc_set_key()`, or `boot_enc_decrypt()` fails
  after the initial copy. Therefore the current runtime log is insufficient to
  classify the failure as `flash_area_read()` without extra copy/decrypt
  evidence.
- `build/.../trusted-firmware-m/.../build/CMakeCache.txt` currently records
  `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`. Therefore the DMA branch in
  `tfm/bl2/src/flash_map.c` is not compiled for the active RD-Aspen TF-M
  image.
- `tfm/bl2/src/flash_map.c`: with boot DMA disabled, `flash_area_read()`
  reaches `DRV_FLASH_AREA(area)->ReadData(...)` for the aligned data items and
  copies into the same caller-provided destination pointer.
- `tfm/platform/ext/target/arm/drivers/flash/strata/Driver_Flash_Strata.h`:
  the active CMSIS flash driver converts item count to bytes, calls
  `cfi_strataflashj3_read(FLASH_DEV.dev, addr, data, cnt)`, and returns an
  ARM driver error only if the CFI/Strata helper fails.
- `tfm/platform/ext/target/arm/drivers/flash/strata/spi_strataflashj3_flash_lib.c`
  and `tfm/platform/ext/target/arm/drivers/flash/cfi/cfi_drv.c` show the
  byte-copy loop reading `nor_cfi_reg_read(base_addr + current_addr + counter)`
  and assigning each byte to `data[current_data_index]`.
- `tfm/platform/ext/target/arm/rse/common/bl2/boot_dma.c` would map
  `boot_dma_memcpy()` to `dma350_memcpy()` on DMA350 channel 0 with blocking
  completion, but that path is inactive for the current build.
- `tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2/flash_map_bl2.c`
  maps image ID 3 to `HOST_SI_CL0_IMG_HDR_BASE_S` and
  `HOST_SI_CL0_ATU_SIZE`, while `host_atu_base_address.h` maps the SI CL0
  header window to the end of SI CL0 SRAM and the code window to
  `HOST_SI_CL0_SRAM_PHYS_BASE`.

Runtime evidence:

| Check | Result | Evidence |
| --- | --- | --- |
| CC3XX host-window DMA trace | expected fail, no host-window CC3XX transfer before image 3 failure | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=dma QBOX_RDASPEN_CC3XX_TRACE_ADDRESS_MIN=1879048192 QBOX_RDASPEN_CC3XX_TRACE_LIMIT=20000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019ad-cc3xx-host-dma-dmi-20260521-v5` |
| Unfiltered DMA350 trace | stopped, not blocker evidence | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=50000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019ad-dma350-dmi-20260521-v1` |

The CC3XX trace run produced `result.json` with
`blocker: qbox_platform_failed:-15`, `timed_out: false`,
`first_failing_register_access: null`, `rse_atu: translation-dmi-model`, and
`rse_cc3xx: hash-aes-cmac-modular-pka-model`. Its RSE log reaches
`BL2: SI CL0 pre load complete`, prints primary/secondary slot versions, then
fails both image 3 slots with `Image 3 RAM loading to 0x70083c00 is failed`.
The platform log contains no CC3XX DMA trace for `0x70083c00`, so the current
failure is before CC3XX decrypt DMA for SI CL0 payload chunks.

The unfiltered DMA350 trace run reached only early BL1_1 fill operations and
then stalled after `BL2 image decrypted successfully`; it was terminated and
did not produce a `result.json`. It should not be used as blocker evidence
except as historical motivation for T019AE's filtered DMA350 trace. T019AE
supersedes the DMA350-copy hypothesis by proving `PLATFORM_HAS_BOOT_DMA` is
disabled in the active TF-M build.

Updated blocker classification:

`si_cl0_image3_ram_load_copy_or_validation_failed`: the next missing behavior
is still the SI CL0 image 3 load path, but the active generated image disables
`PLATFORM_HAS_BOOT_DMA`. The initial copy path is therefore
`flash_area_read()` -> CFI/Strata `ReadData()` ->
`cfi_strataflashj3_read()` -> `nor_cfi_reg_read()` while writing into the
ATU-translated `0x70083c00` host-window destination. The next narrow
implementation step is a CFI/Strata and ATU host-window copy trace that can
prove whether the failure happens during copy or later in MCUboot encrypted
image setup/decrypt/slot handling.

### 2026-05-21 T019AE DMA350-Inactive SI CL0 Copy Evidence

T019AE added focused DMA350 trace controls and used them to test the previous
DMA350-copy hypothesis. The result is a blocker reclassification, not an RSE
boot fix: the current generated TF-M build does not compile the BL2
`boot_dma_memcpy()` branch.

Source and runtime evidence:

- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/CMakeCache.txt`
  contains `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`.
- `flash_map.c` wraps the DMA copy path in `#ifdef PLATFORM_HAS_BOOT_DMA`, so
  the current build falls through to the CMSIS flash-driver path.
- `Driver_Flash_Strata.h` and `spi_strataflashj3_flash_lib.c` show that the
  active path converts CMSIS item counts to bytes, reads the CFI/Strata flash
  through `nor_cfi_reg_read()`, and stores bytes directly through the caller's
  destination pointer.
- The focused DMI run reached the same SI CL0 image 3 failure and produced no
  `rse_dma350` trace lines in `qbox-platform.log`.
- The same run shows ATU translated writes into the SI CL0 host window, for
  example `translate_write logical=0x70090000 ... status=ok region=11`.

Checks:

| Check | Result | Evidence |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| DMA350 focused build | pass | `cmake --build tools/qbox/build --target dma350-tests platforms-vp --parallel 4` |
| DMA350 focused regression | pass | `ctest --test-dir tools/qbox/build -R dma350-tests --output-on-failure` |
| Active TF-M boot-DMA setting | pass, DMA disabled | `rg -n "PLATFORM_HAS_BOOT_DMA" build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/CMakeCache.txt` |
| Filtered DMA350/ATU runtime | stopped after sufficient evidence, no `result.json` | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=20000 QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_FILTER=copy QBOX_RDASPEN_DMA350_TRACE_ADDRESS_MIN=1879048192 QBOX_RDASPEN_DMA350_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019ae-dma350-copy-dmi-20260521-v1` |

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019ae-dma350-copy-dmi-20260521-v1/`

Important log markers from `qbox-rse.log`:

```text
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] PSA Crypto init done, sig_type: EC-P256
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 0 from flash
```

Updated blocker classification:

`si_cl0_image3_cfi_copy_or_post_copy_validation_failed`: the next
implementation target is the CFI/Strata flash-driver byte-read and host-window
write path plus the immediately following MCUboot encrypted-image flow, not
DMA350. The investigation should first instrument the exact source offset,
destination writes, and DMI grants around `0xb0067000` and `0x70083c00`, then
decide whether the missing behavior belongs in the RSE boot flash model, ATU
translated write path, translated DMI invalidation/coherence, or MCUboot slot
erase/remove side effects.

### 2026-05-21 T019AF Strata Flash And ATU DMI Evidence

T019AF replaces the RSE boot-flash aperture in
`tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` with a dedicated
`strata_flash_j3` SystemC/TLM component instead of plain `gs_memory`. The
component implements the CFI/Strata commands exercised by the active TF-M
build: read-array, read-ID, query, read-status, clear-status, byte program,
block erase/ack, and lock/unlock command sequencing. It intentionally denies
DMI because CFI command state and program/erase side effects are visible.

Source review also confirmed that the active generated TF-M build is the FVP
variant:

- `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/CMakeCache.txt`
  records `TFM_PLATFORM_VARIANT:UNINITIALIZED=fvp` and
  `PLATFORM_HAS_STRATA_FLASH:BOOL=ON`.
- Patch `0067-rse-css-aspen-Support-a-simple-memory-model-instead-.patch`
  keeps Strata flash enabled for `TFM_PLATFORM_VARIANT=fvp` and only switches
  the CSS-Aspen flash driver to a simple memory model for the RTL variant.

Implementation evidence:

- `tools/qbox/systemc-components/strata_flash_j3/`
- `tools/qbox/tests/components/strata_flash_j3/`
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` now instantiates
  `rse_boot_flash` as `moduletype = "strata_flash_j3"`.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` now includes `strata_flash_j3` in the
  required QBox target list and reports `rse_boot_media:
  cfi-strata-flash-partial-model` when the RSE config uses the model.

Checks:

| Check | Result | Evidence |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/compare_fvp_qbox_rse_logs.py scripts/audit_qbox_fvp_rd_aspen_coverage.py` |
| Strata flash/platform build | pass | `cmake --build tools/qbox/build --target strata_flash_j3-tests platforms-vp --parallel 4` |
| Strata/ATU component regression | pass | `ctest --test-dir tools/qbox/build -R 'strata_flash_j3-tests|rse_atu-tests' --output-on-failure` |
| RSE runtime with Strata flash and ATU DMI | expected fail, same SI CL0 blocker | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_FILTER=dmi QBOX_RDASPEN_ATU_TRACE_ADDRESS_MIN=1879576576 QBOX_RDASPEN_ATU_TRACE_ADDRESS_MAX=1880096768 QBOX_RDASPEN_ATU_TRACE_LIMIT=256 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019af-strata-flash-20260521-v2` |
| Coverage audit | expected fail, RSE path not boot-complete | `python3 scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019af-strata-flash-20260521-v2/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019af-strata-flash-20260521-v2/qbox-rse.log --output build/qbox-fvp-rd-aspen/rse-t019af-strata-flash-20260521-v2/coverage-audit.json` |

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019af-strata-flash-20260521-v2/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `timed_out: false`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fidelity_labels.rse_boot_media: cfi-strata-flash-partial-model`
- `fidelity_labels.rse_atu: translation-dmi-model`
- `fail_patterns.[ERR]: true`

RSE UART evidence:

```text
[INF] BL2 image decrypted successfully
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] PSA Crypto init done, sig_type: EC-P256
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 0 from flash
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 1 from flash
[INF] No slot to load for image 3
[ERR] Unable to find bootable image
```

ATU DMI evidence from `qbox-platform.log`:

```text
platform.rse_atu_regs dmi logical=0x70084000 physical=0x4000120000000 len=0x4 status=ok reason=granted region=11 upstream=0x70084000-0x70183fff downstream=0x4000120000000-0x4000120ffffff
platform.rse_atu_regs dmi logical=0x700843fc physical=0x40001200003fc len=0x4 status=ok reason=granted region=11 upstream=0x70084000-0x70183fff downstream=0x4000120000000-0x4000120ffffff
```

Updated blocker classification:

`si_cl0_image3_post_strata_copy_or_validation_failed`: the boot-flash aperture
is no longer plain memory, ATU translated DMI for the SI CL0 SRAM window is
granted, and the runtime still fails at the same image 3 path. The next
narrow task is to prove the copied bytes in host SI CL0 SRAM at `0x70083c00`
and then split the remaining failure between `flash_area_read()` completion,
`boot_enc_load()`, key setup, decrypt, MCUboot slot removal/erase side effects,
and SI CL0 image layout assumptions.

### 2026-05-22 T019AG Host SI CL0 SRAM Copy Evidence

T019AG adds a runner-controlled, file-backed probe for the SI CL0 host SRAM
window. `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` now accepts
`QBOX_RDASPEN_HOST_SI_CL0_SRAM_MAP_FILE` and passes it to the existing
`gs_memory.map_file` parameter for `host_si_cl0_sram`. The runner creates a
zeroed 16 MiB `host-si-cl0-sram.bin` file per run, maps it into QBox, and
records host-SRAM samples and SI CL0 slot matches in `result.json`.

The same runtime still fails at SI CL0 image 3, but the failure is now split
away from the flash-to-host-window copy:

| Check | Result | Evidence |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/compare_fvp_qbox_rse_logs.py scripts/audit_qbox_fvp_rd_aspen_coverage.py` |
| Runner check-only probe | expected fail, evidence schema written | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-check-20260523-v2` |
| RSE runtime with file-backed host SI CL0 SRAM | expected fail, copy proven | `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1` |
| Post-run SRAM/flash analysis | pass | `build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1/si-cl0-sram-analysis.json` |
| Coverage audit | expected fail, RSE path not boot-complete | `python3 scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1/qbox-rse.log --output build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1/coverage-audit.json` |

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019ag-host-sram-map-20260522-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_failed:-15`
- `timed_out: false`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `fail_patterns.[ERR]: true`

RSE UART evidence:

```text
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 0 from flash
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 1 from flash
[INF] No slot to load for image 3
[ERR] Unable to find bootable image
```

Host-SRAM evidence from `result.json` and `si-cl0-sram-analysis.json`:

- `host-si-cl0-sram.bin` is 16 MiB and contains `745307` non-zero bytes after
  the run.
- The header window at file offset `0xffc00` corresponds to logical
  `0x70083c00` and matches RSE flash offset `0x67000`.
- The code window at file offset `0x0` corresponds to logical `0x70084000` and
  matches RSE flash offset `0x67400`.
- The reordered host-SRAM image matches the primary SI CL0 flash slot for
  `0xb6b1e` bytes.
- The primary SI CL0 MCUboot header reports `load_addr = 0x70083c00`,
  `header_size = 0x400`, `image_size = 0xb65b0`, `flags = 0x24`,
  `protected_tlv_size = 0x81`, unprotected TLV total `0xed`, and
  `boot_read_image_size = 0xb6b1e`.
- The expected AES-KW encryption TLV is present as type `0x31`, length `0x18`.

Updated blocker classification:

`si_cl0_image3_boot_enc_key_path_failed`: the CFI/Strata `flash_area_read()`
copy into the ATU-translated host SRAM window succeeds for the primary SI CL0
image, and the host-window header/code layout is correct. Because the copied
payload still matches encrypted flash and SRAM is not visibly decrypted, the
failure is before payload decrypt. The next narrow task is to distinguish
`boot_enc_load()` AES-KW key unwrap from the immediately following
`boot_enc_set_key()` AES-CTR key setup.

### 2026-05-23 T019AH SI CL0 boot_enc Trace Evidence

T019AH adds runner-controlled QEMU trace filtering and BL2 symbol-range
analysis for the MCUboot encrypted-image path. The runner now accepts
`--qemu-trace-events`, `--qemu-trace-filter`, and `--boot-enc-trace`.
`--boot-enc-trace` reads the active `bl2.map`, computes a `-dfilter` range for
the BL2 AES-KW/AES-CTR functions, and records `boot_enc_trace` in
`result.json`.

Source and symbol evidence:

- Active build config remains `.config.yaml` with `MACHINE = "fvp-rd-aspen"`,
  `RD_ASPEN_VARIANT = "cfg2"`, `PC_CPUS_COUNT_DEFAULT = "4"`, and
  `ARCHITECTURE_BAREMETAL: true`.
- `mcuboot_config.h` defines `MCUBOOT_ENCRYPT_KW`; `CMakeCache.txt` has
  `MCUBOOT_ENCRYPT_KW:BOOL=ON`.
- `bootutil/enc_key_public.h` gives the expected AES-KW TLV size:
  `BOOT_ENC_KEY_SIZE + 8 = 0x18`, matching the primary SI CL0 TLV `0x31/0x18`
  found in T019AG.
- `ram_load.c` calls `boot_enc_set_key()` only when `boot_enc_load()` returns
  `0`.
- `encrypted.c` shows `boot_enc_load()` reads the expected encryption TLV and
  returns `boot_decrypt_key(...)`; with `MCUBOOT_ENCRYPT_KW`,
  `boot_decrypt_key()` calls `key_unwrap()`, which calls
  `bootutil_aes_kw_unwrap()`.

Parsed BL2 symbol ranges from
`build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/bl2.map`:

| Symbol | Range |
| --- | --- |
| `bootutil_aes_kw_unwrap` | `0x3101eb24..0x3101eb84` |
| `boot_decrypt_key` | `0x3101ed1e..0x3101ed36` |
| `boot_enc_load` | `0x3101ed4a..0x3101ede6` |
| `boot_enc_set_key` | `0x3101ede6..0x3101ee0e` |
| `boot_enc_decrypt` | `0x3101ee20..0x3101eea4` |

Validation:

| Check | Result | Evidence |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| Runner check-only probe | expected fail, trace schema accepted | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --boot-enc-trace --out-dir build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-check-20260523-v1` |
| RSE runtime with boot_enc trace | expected fail, blocker classified | `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --boot-enc-trace --qemu-trace-events in_asm --out-dir build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2` |
| Coverage audit | expected fail, RSE path not boot-complete | `python3 scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/qbox-rse.log --output build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/coverage-audit.json` |

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/`

Runtime result:

- `passed: false`
- `blocker: si_cl0_boot_enc_load_decrypt_key_failed_before_set_key`
- `timed_out: false`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `qemu_trace_log: build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/qemu-rse-trace.log`

RSE UART evidence remains the same failure mode:

```text
[INF] BL2: SI CL0 pre load complete
[INF] Primary   slot: version=2.16.0+0
[INF] Secondary slot: version=2.16.0+0
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 0 from flash
[INF] Image 3 RAM loading to 0x70083c00 is failed.
[INF] Removing image 3 slot 1 from flash
[INF] No slot to load for image 3
[ERR] Unable to find bootable image
```

Boot-enc trace evidence from `result.json`:

- `classification: boot_enc_load_decrypt_key_failed_before_set_key`
- `trace_address_count: 31`
- `hit_counts.boot_enc_load: 12`
- `hit_counts.boot_decrypt_key: 3`
- `hit_counts.bootutil_aes_kw_unwrap: 4`
- `hit_counts.boot_enc_set_key: 0`
- `hit_counts.boot_enc_decrypt: 0`
- first hits: `boot_enc_load = 0x3101ed4a`,
  `boot_decrypt_key = 0x3101ed1e`, and
  `bootutil_aes_kw_unwrap = 0x3101eb24`.

Host-SRAM evidence is unchanged from T019AG: the primary SI CL0 header/code
copy is proven for `0xb6b1e` bytes, and the payload still matches encrypted
flash. Combining that with the boot-enc trace means the active failure is not
the host SRAM copy, `boot_enc_set_key()`, or payload AES-CTR decrypt. The next
narrow task is to debug the AES-KW unwrap input/key path: TLV bytes, image ID,
PSA unwrap-key selection, provisioning/OTP/KMU key material, and any CC3XX/PSA
backend side effect that differs from FVP.

### 2026-05-23 T019AN AP Handoff And MHU Pair Evidence

T019AN extends the RSE-oriented QBox platform from AP BL2 slot-version output
to the AP power-on SCMI handoff. The implementation keeps AP CPU execution
disabled by default while adding the host physical windows and pair-isolated
MHU plumbing needed by the firmware path:

- AP high physical windows for CSS counters/timers, SMCF SRAM, AP-RSE MHUv3
  PBX/MBX frames, and AP-RSE mailbox memory.
- Environment-gated AP CPU/GIC/UART wiring behind
  `QBOX_RDASPEN_ENABLE_AP_CPUS=true`.
- `mhuv3_stub` peer routing by `pair`, so the AP-RSE MBX frame does not replace
  the RSE-SI MBX used for SCMI ACK delivery.
- SCMI Power Domain state-set handling that can drive a reset-release signal
  when AP CPU reset wiring is enabled.

Validation:

| Check | Result | Evidence |
| --- | --- | --- |
| Lua/Python/QBox whitespace | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua && python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py && git -C tools/qbox diff --check` |
| QBox focused build | pass | `cmake --build tools/qbox/build --target mhuv3_stub-tests platforms-vp cpu_arm_cortexA720AE arm_gicv3 mhuv3_stub --parallel 8` |
| MHU pair/reset unit test | pass | `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` |
| Default RSE runtime, AP CPUs disabled | expected timeout after AP power-on handoff | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 600 --out-dir build/qbox-fvp-rd-aspen/rse-t019an-mhu-pair-map-default-20260523-v2` |
| AP CPU opt-in runtime | expected timeout, AP reset blocker captured | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --pc-trace --pc-trace-limit 256 --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-t019ao-ap-cpus-enabled-20260523-v1` |

Default runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019an-mhu-pair-map-default-20260523-v2/`

Default runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `marker_hits.rse_boot["Jumping to the first image slot"]: true`
- `marker_hits.rse_scp_handoff["Init SCMI comm to SCP succeeded"]: true`
- `marker_hits.rse_scp_handoff["RSE to SCP SCMI power on AP succeeded"]: true`

RSE UART evidence:

```text
[INF] Image 2 RAM loading to 0x70001c00 is succeeded.
[INF] Key hash matched for image 2 at slot 0
[INF] Image 2 loaded from the primary slot
[INF] BL2: AP BL2 post load start
[INF] BL2: AP ATU region 7: [0x40680000 - 0x406dffff]->[0x30000_1b600000 - 0x30000_1b65ffff]
[INF] BL2: AP ATU region 8: [0x40740000 - 0x40741fff]->[0x20000_60000000 - 0x20000_60001fff]
[INF] BL2: SMDEXP2SMD ATU region 0: [0xe0340000 - 0xe0341fff]->[0x20000_60002000 - 0x20000_60003fff]
[INF] BL2: AP BL2 post load complete
[INF] Image 0 RAM loading to 0x3103f800 is succeeded.
[INF] BL2: AP power domain id = 0.
[INF] BL2: AP power domain name = AP.
[INF] BL2: AP power domain attributes = 0x0.
[INF] BL2: AP power domain state = 0x20111.
[INF] BL2: RSE to SCP SCMI power on AP succeeded.
[INF] Bootloader chainload address offset: 0x27000
[INF] Image version: v2.2.2
[INF] Jumping to the first image slot
```

Updated blocker classification:

`ap_cpu_reset_and_secure_boot_not_yet_modeled`: the default RSE/SCP service
path now reaches the AP power-on handoff and RSE runtime chainload, but the
Primary Compute CPU execution path is still intentionally disabled by default.
When enabled, AP CPUs begin executing at `0x82000` before the modeled RSE/SCP
release point.

AP CPU opt-in artifact root:
`build/qbox-fvp-rd-aspen/rse-t019ao-ap-cpus-enabled-20260523-v1/`

AP CPU opt-in evidence:

- `qbox-platform.log` prints `ap cpus: 4`.
- `ap-pc-trace.log` records all four A720AE CPUs at `pc=0x82000` with
  `sc_time=0 s`.
- RSE still reaches BL2 and SI CL0 pre-load setup, but the short opt-in run
  times out before SCMI/AP power-on markers.
- Secure and primary AP console logs remain empty.

AP PC trace excerpt:

```text
platform.ap_cpu_0 pc_trace sample=1 seen=1 sc_time=0 s vclock_ns=169244629 pc=0x82000 mem_io_pc=0x0
platform.ap_cpu_1 pc_trace sample=1 seen=1 sc_time=0 s vclock_ns=169478731 pc=0x82000 mem_io_pc=0x0
platform.ap_cpu_2 pc_trace sample=1 seen=1 sc_time=0 s vclock_ns=169618965 pc=0x82000 mem_io_pc=0x0
platform.ap_cpu_3 pc_trace sample=1 seen=1 sc_time=0 s vclock_ns=169744341 pc=0x82000 mem_io_pc=0x0
```

Reset-hold semantics were completed by the follow-up AP primary-power run. The
next narrow task is now AP BL2 measured-boot/RSE secure-service response
semantics after image id 6, then EL3/secure-world entry, GIC/timer routing, AP
UART output, and Linux boot markers.

### 2026-05-23 T019AP AP-RSE Secure-Service Evidence

T019AP extends the AP-RSE MHUv3 compatibility path far enough for AP TF-A to
initialize its MHU sender. The AP-side `Host to RSE MHU driver initialization
failed: -4` message is removed, but the minimal AP-RSE PSA success reply is not
enough to satisfy AP BL2 measured boot.

Runtime artifact root:
`build/qbox-fvp-rd-aspen/rse-t019aq-ap-rse-psa-reply-nodmi-20260523-v1/`

Runtime command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build --pc-trace --pc-trace-limit 4096 --timeout 750 \
  --out-dir build/qbox-fvp-rd-aspen/rse-t019aq-ap-rse-psa-reply-nodmi-20260523-v1
```

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `first_failing_register_access: null`
- `marker_hits.rse_boot["Jumping to the first image slot"]: true`
- `marker_hits.rse_scp_handoff["RSE to SCP SCMI power on AP succeeded"]: true`

AP secure console:

```text
NOTICE:  BL2: v2.14.0(debug):sandbox/v2.14-33-gbacd68ff6d-dirty
INFO:    Booting with partition FIP_A
INFO:    Using crypto library 'mbed TLS'
WARNING: SDS init failed (-1), continuing measured boot
INFO:    Loading image id=6 at address 0x2010
INFO:    Image id=6 loaded: 0x2010 - 0x24ce
```

AP PC trace and source mapping:

```text
platform.ap_cpu_0 reset_trace event=reset-cb-release-done value=0 state=none
platform.ap_cpu_0 pc_trace sample=4 pc=0x918b4
platform.ap_cpu_0 pc_trace sample=5 pc=0x82310
platform.ap_cpu_0 pc_trace sample=6 pc=0x826f4
```

`llvm-addr2line -f -C -e
build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/2.14.0+git/deploy-trusted-firmware-a/bl2-rdaspen.elf
0x826f4` maps the last AP PC to `plat_panic_handler` in
`plat/common/aarch64/platform_helpers.S`.

Source path inspected:

- `plat/arm/board/automotive_rd/platform/rdaspen/rdaspen_measured_boot.c`
- `drivers/measured_boot/rse/rse_measured_boot.c`
- `lib/psa/measured_boot.c`
- `drivers/arm/rse/rse_comms.c`
- `drivers/arm/rse/rse_comms_protocol_embed.c`

Classification:

`ap_bl2_rse_measured_boot_service_semantics`: AP BL2 now reaches the first
measured-boot image load, but the QBox AP-RSE service response is only a
transport smoke path. It must implement the measured-boot service contract
around `RSE_MEASURED_BOOT_EXTEND` and related RSE secure services before EL3 or
Linux boot progress can be claimed.

Later 2026-05-23 runs supersede this blocker: AP SDS, AP trusted/non-trusted
NV counters, AP DRAM windows, AP system timer, and AP-SI SCMI MHU coverage now
advance the AP path into BL31.

### 2026-05-23 T019AQ AP BL31 Runtime Evidence

T019AQ extends the AP path from AP BL2 image id 6 into BL31. The key fixes are:

- AP shared-RAM SDS seed at `ARM_SHARED_RAM_BASE`.
- AP trusted/non-trusted NV counter seed values `31` and `223`.
- AP secure watchdog and DRAM windows required by TF-A image loading.
- AP memory-mapped timer model at `0x1a810000`/`0x1a830000`.
- AP-SI SCMI MHU PBX/MBX frames behind the AP ATU-translated host-physical
  windows for BL31 SCMI initialization.

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-t019ay-ap-ntfw-nvctr-20260523-v1/`
- `build/qbox-fvp-rd-aspen/rse-t019az-ap-timer-20260523-v1/`
- `build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1/`

Latest runtime command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build --exception-trace --pc-trace-limit 224 --timeout 420 \
  --out-dir build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1
```

Latest runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- `marker_hits.rse_boot["Jumping to the first image slot"]: true`
- `marker_hits.rse_scp_handoff["RSE to SCP SCMI power on AP succeeded"]: true`
- `marker_hits.measured_boot["SECURE_RT_EL3"]: true`
- `marker_hits.measured_boot["SECURE_RT_EL1_SPMD"]: true`
- `marker_hits.measured_boot["BL_33"]: true`

AP secure console progression:

```text
INFO:    SDS: Detected SDS Memory Region (3520 bytes)
INFO:    Image id=32 loaded: 0x2010 - 0x2150
INFO:     - sw_type     : FW_CONFIG
INFO:     - sw_type     : SECURE_RT_EL3
INFO:     - sw_type     : HW_CONFIG
INFO:     - sw_type     : SECURE_RT_EL1_SPMD
INFO:    Loading image id=11 at address 0xe0000000
INFO:    Image id=15 loaded: 0xe0000000 - 0xe0000449
INFO:    Image id=5 loaded: 0xe0000000 - 0xe00995f0
INFO:     - sw_type     : BL_33
NOTICE:  BL2: Booting BL31
NOTICE:  BL31: v2.14.0(debug):sandbox/v2.14-33-gbacd68ff6d-dirty
INFO:    Initializing SCMI driver on channel 0
INFO:    SCMI driver initialized
```

Current BL31 blocker:

```text
Unhandled Exception in EL3.
elr_el3        = 0x00000000000107b8
esr_el3        = 0x0000000002000000
far_el3        = 0x0000000000000000
```

`llvm-addr2line -f -C -e
build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/2.14.0+git/build/rdaspen/debug/bl31/bl31.elf
0x107b8` maps the current blocker to `write_errselr_el1` in
`include/arch/aarch64/arch_helpers.h:657`, called from
`rdaspen_ras_init_per_cpu()` in
`plat/arm/board/automotive_rd/platform/rdaspen/ras/rdaspen_ras.c`.

Classification:

`ap_bl31_ras_sysreg_semantics`: AP BL31 now reaches platform setup past SCMI
driver initialization. The active blocker is QEMU/libqemu CPU handling for
RD-Aspen RAS system registers (`ERRSELR_EL1`/`ERXCTLR_EL1` path), not AP BL2
measured boot, AP system timer, AP-SI SCMI MHU address decode, or AP reset
release.

Later 2026-05-24 evidence supersedes this blocker: QBox now reaches Linux
login through the RSE-oriented path.

### 2026-05-24 T019AU AP/SI MHU Map And Linux Login Evidence

T019AU fixes the Linux-visible AP/SI MHU map after a previous runtime reached
the kernel but died on the first AP-side MHUv3 register read. The faulting
kernel PC was `mhuv3_probe+0x60`, and the register read targeted the logical
`0x400b0000` AP MHU window. FVP ATU logs and generated firmware sources show
that the AP logical MHU region is translated before reaching SI-local MHU
registers:

| AP logical | Host physical | QBox object |
| --- | --- | --- |
| `0x40020000` | `0x400003b000000` | `host_ap_si_ns_scmi_mhu_pbx` |
| `0x40050000` | `0x400003b040000` | `host_ap_si_ns_scmi_mhu_mbx` |
| `0x40080000` | `0x400003b080000` | `host_ap_si_scmi_mhu_pbx` |
| `0x400b0000` | `0x400003b100000` | `host_ap_si_cl1_mhu_pbx` |
| `0x400e0000` | `0x400003b140000` | `host_ap_si_cl1_mhu_mbx` |
| `0x40110000` | `0x400003b380000` | `host_ap_si_pfdi_monitor_mhu_pbx` |

Source evidence:

- FVP ATU log:
  `build/fvp-boot-logs/rse-qbox-blocker-20260523-v1/terminal_uart_5000.log`
- TF-A platform definitions:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/2.14.0+git/git/plat/arm/board/automotive_rd/platform/rdaspen/include/platform_def.h`
- generated TF-A DT:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/2.14.0+git/build/rdaspen/debug/fdts/rdaspen_fvp.pre.dts`
- SI SCP MHU map:
  `build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/scp-firmware/2.16.0+git/git/product/automotive-rd/rdaspen/si0_ramfw/include/si0_mmap.h`

Implemented QBox coverage:

- Added the AP non-secure SCMI shared SRAM window at `0x00180000`.
- Added AP/SI non-secure SCMI PBX/MBX frames at host physical
  `0x400003b000000` and `0x400003b040000`, using the TF-A shared SRAM
  request/response offsets `0x00180000` and `0x00180100`.
- Moved/kept the secure AP/SI SCMI pair at `0x400003b080000` and
  `0x400003b0c0000`.
- Added the Linux SI CL1 remoteproc PBX/MBX frames at host physical
  `0x400003b100000` and `0x400003b140000`.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/validate_qbox_fvp_rd_aspen_map.py scripts/audit_qbox_fvp_rd_aspen_coverage.py` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| map validation | pass | `./scripts/validate_qbox_fvp_rd_aspen_map.py` |
| QBox platform build | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 8` |
| RSE runtime | expected strict-marker timeout, Linux login reached | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=4096 QBOX_RDASPEN_ATU_TRACE_FILTER=translation QBOX_RDASPEN_ATU_TRACE_ADDRESS_MIN=0x40000000 QBOX_RDASPEN_ATU_TRACE_ADDRESS_MAX=0x40140000 QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=4096 QBOX_RDASPEN_MHU_TRACE_FILE=build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/mhuv3-trace.log python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1` |
| coverage audit | expected fail, SI CL1 gap remains | `scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/qbox-primary-console.log --output build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/coverage-audit.json` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `interrupted: false`
- `platform_returncode: -15`
- `fail_patterns["Kernel panic"]: false`
- `fail_patterns["Unable to mount root fs"]: false`
- `marker_hits.rse_boot["Jumping to the first image slot"]: true`
- `marker_hits.rse_scp_handoff["RSE to SCP SCMI power on AP succeeded"]: true`
- `marker_hits.linux_boot["fvp-rd-aspen login:"]: true`

Key runtime evidence:

```text
platform.host_ap_atu translate_read logical=0x400b0000 physical=0x400003b100000 len=0x4 status=ok
platform.host_ap_atu translate_read logical=0x400e0000 physical=0x400003b140000 len=0x4 status=ok
platform.host_ap_atu translate_read logical=0x40020000 physical=0x400003b000000 len=0x4 status=ok
platform.host_ap_atu translate_read logical=0x40050000 physical=0x400003b040000 len=0x4 status=ok
probe of 400b0000.mhu returned 0
probe of 400e0000.mhu returned 0
probe of 40020000.mhu returned 0
probe of 40050000.mhu returned 0
arm-scmi arm-scmi.1.auto: Using scmi_mailbox_transport
arm-scmi arm-scmi.1.auto: SCMI Protocol v2.1 'QBox:RD-Aspen' Firmware version 0x1
arm-smmu-v3 1c0000000.iommu: ias 44-bit, oas 44-bit
Started Platform Fault Detection Application.
fvp-rd-aspen login:
```

Current blocker classification:

`si_cl1_remoteproc_rpmsg_gap`: the AP/SI MHU address-decode problem is fixed
and Linux reaches login, but QBox still does not model the full SI CL1 runtime
peer. The primary console reports `platform soc:si_remoteproc:si-cl1: probe
failed with error -19`, while the RSE log reports `BL2: SI CL1 not present,
skip loading`. The runner also still misses the FVP RSE runtime markers
`SCMI Comms subscribed to power state notifications` and `RT_0`.

### 2026-05-24 Post-Login Probe Infrastructure

The RSE runner now supports Linux post-login probes through a file-backed UART
input path:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --post-login-probe \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --timeout 900 \
  --out-dir build/qbox-fvp-rd-aspen/rse-post-login-<run-id>
```

Implementation notes:

- `scripts/run_qbox_fvp_rd_aspen_rse.py` creates
  `primary-uart-input.fifo` only when `--post-login-probe` is requested.
- The runner waits for `fvp-rd-aspen login:` in `qbox-primary-console.log`
  before sending `root`, then waits for the root prompt before sending driver
  and remoteproc/RPMsg probe commands.
- `char_backend_file` gained opt-in `poll_read` and `poll_interval_ms`
  parameters so a FIFO input file does not block the SystemC thread at time
  zero. The RSE primary UART enables this only when
  `QBOX_RDASPEN_PRIMARY_UART_READ_FILE` is not `/dev/null`.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox build | pass | `cmake --build tools/qbox/build --target char_backend_file platforms-vp --parallel 8` |
| runner injection smoke | pass | Python import smoke of `drive_post_login_probe()` wrote `root`, `echo __QBOX_PROBE_START__`, `modprobe -v arm_si_rproc timeout=500`, and `__QBOX_PROBE_DONE__` to a pipe. |
| 45s runtime smoke | expected timeout, no FIFO startup block | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 45 --out-dir build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| 120s runtime smoke | expected timeout, matches no-probe baseline | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v3 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| 120s baseline | expected timeout, same BL2 progress as probe run | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-baseline-after-fifo-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Runtime artifact roots:

- `build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v2/`
- `build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v3/`
- `build/qbox-fvp-rd-aspen/rse-baseline-after-fifo-20260524-v1/`

The 45s and 120s post-login runs intentionally do not prove Linux login; they
prove that the new FIFO path is nonblocking and that short timeouts classify
the state as `qbox_platform_timeout` with `post_login_probe.requested=true`.
The 120s post-login and 120s no-probe baseline both reach the same RSE marker
set (`BL1_2` and `BL2` true, AP/Linux not reached), so the probe input path is
not a new early-boot blocker. Full post-login driver evidence still requires a
longer run that reaches `fvp-rd-aspen login:` or the next SI CL1/RPMsg model
work to shorten the path.

### 2026-05-24 Post-Login Threaded FIFO Fix

Short timeout comparison showed that the first FIFO implementation still
perturbed long AP boot runs. With `poll_read=true`, `char_backend_file` used a
SystemC process that waited on simulation time between empty reads; with the
primary UART FIFO enabled, the AP path stalled around BL31/PFDI while an
otherwise identical no-probe run reached the Linux login prompt.

Comparison runs:

| Run | Result | Artifact |
| --- | --- | --- |
| post-login FIFO poll, 50 ms interval | expected timeout before Linux login; primary console remained empty while secure console stopped around BL31/PFDI | `build/qbox-fvp-rd-aspen/rse-post-login-poll50-20260524-v1/` |
| no post-login probe baseline | expected timeout after Linux login; primary console reached `fvp-rd-aspen login:` with systemd, virtio, SMMU, and `arm_si_rproc` evidence | `build/qbox-fvp-rd-aspen/rse-noprobe-compare-20260524-v1/` |

The fix moves `char_backend_file` `poll_read` input to a host-side reader
thread. The thread opens the FIFO with `O_NONBLOCK`, reads available bytes with
host wall-clock polling, and feeds `biflow_socket::enqueue()`, while the
SystemC receiver process returns immediately for poll mode. This keeps UART
input readiness from consuming SystemC simulation time. The RSE Lua platform
also exposes `QBOX_RDASPEN_PRIMARY_UART_POLL_INTERVAL_MS`, defaulting to
100 ms, for the primary UART file backend.

The runner was also adjusted so `__QBOX_PROBE_DONE__` is emitted immediately
after the short login, module, remoteproc, virtio, and network probes. This
keeps the proof useful with short timeouts before heavier diagnostic commands
such as full `dmesg` filtering finish. When the post-login probe has completed,
the runner no longer classifies the normal SIGTERM used for cleanup as a
`qbox_platform_failed:-15` blocker.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check -- systemc-components/backends/char_backend_file/include/char_backend_file.h platforms/fvp-rd-aspen-rse/conf.lua` |
| focused QBox build | pass | `timeout 120s cmake --build tools/qbox/build --target char_backend_file platforms-vp --parallel 8` |
| post-login threaded input runtime | login/probe complete, overall MVP still fails required marker checks | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 175s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 150 --post-login-probe --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-post-login-threaded-input-20260524-v3 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

`build/qbox-fvp-rd-aspen/rse-post-login-threaded-input-20260524-v3/result.json`
records:

- `blocker: null`, `timed_out: false`, and `platform_returncode: -15`
  because the runner terminated QBox after the proof marker was observed.
- `post_login_probe.complete: true`, `done_marker: true`, `sent_login: true`,
  and `sent_probe: true`.
- Driver/probe patterns all true: `arm_si_rproc`, `pl011_uart`, `rpmsg`,
  `smmu_v3`, and `virtio`.
- Probe command return codes all zero:
  `arm_si_rproc_modprobe_rc`, `rpmsg_ns_modprobe_rc`,
  `virtio_rpmsg_bus_modprobe_rc`, and `rpmsg_net_modprobe_rc`.
- Linux markers true for `fvp-rd-aspen login:` and `root@fvp-rd-aspen`.
- Required MVP markers are still incomplete for `AP_BL2`, `RT_0`, `SI_CL0`,
  and `SCMI Comms subscribed to power state notifications`, so the top-level
  result correctly remains `passed: false`.

The primary console log in that run shows `root` login, `__QBOX_PROBE_START__`,
Linux `6.18.5-rt3-yocto-preempt-rt`, attached `si-cl1` remoteproc state, zero
return codes for the RPMsg modules, virtio devices `virtio0..virtio5`, network
links `lo`, `eth0`, `ovs-system`, `ovsbr0`, `brsi1`, and
`__QBOX_PROBE_DONE__`.

### 2026-05-24 T019AV Host SCR And SI CL1 Load Evidence

The previous T019AV blocker had two parts:

- Linux-reaching QBox runs still lacked a live SI CL1 runtime/RPMsg peer.
- QBox RSE BL2 incorrectly printed `BL2: SI CL1 not present, skip loading`
  even though the active `.config.yaml` selects RD-Aspen CFG2.

Local TF-M source inspection identified the CFG2 presence check. In
`build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/git/tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2/boot_hal_bl2.c`,
`boot_platform_should_load_image()` calls `check_si_cl1_is_present()` for
`RSE_FIRMWARE_SI_CL1_ID`. That helper maps `HOST_SI_SCR_PHYS_BASE` through
RSE ATU and calls `scr_sid_is_cl1_present(&HOST_SI_SCR_DEV)`. The SCR driver
defines `sid_system_cfg` at offset `0x70`, with bit 0 named `cl1_present`, and
`cpuhalt`, `memprotctlr`, and `safectlr` at offsets `0x300`, `0x500`, and
`0x600` respectively.

QBox previously mapped `host_si_scr` as zero-initialized `gs_memory`, so the
CFG2 firmware read `cl1_present = 0`. QBox now uses a small SystemC/TLM
`host_scr` model for the SCR/SID window and sets `cl1_present = true` in the
RD-Aspen RSE Lua config.

Implemented QBox coverage:

- `tools/qbox/systemc-components/host_scr/` implements a 64 KiB SCR register
  window with read-only SID/system config registers and writable CPU halt,
  memory-protection, and safe-control registers.
- `tools/qbox/tests/components/host_scr/` covers configurable CL1-present
  reset value, writable control registers, and read-only system config.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` wires `host_si_scr` as
  `host_scr` and keeps `cl1_present = true`.
- `scripts/run_qbox_fvp_rd_aspen_rse.py` now records both CL0 and CL1 SI SRAM
  backing files and analyzes the CL1 primary flash slot at offset `0x167000`.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| QBox focused build | pass | `cmake --build tools/qbox/build --target host_scr host_scr-tests platforms-vp --parallel 8` |
| QBox component tests | pass | `ctest --test-dir tools/qbox/build -R '^(host_scr-tests|host_ppu-tests|mhuv3_stub-tests)$' --output-on-failure` |
| runner check-only | expected `check_only_no_runtime` | `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-t019av-cl1-sram-check-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| RSE runtime | expected strict-marker timeout, SI CL1 load reached | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-t019av-host-scr-cl1-sram-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-t019av-host-scr-cl1-sram-20260524-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `fidelity_labels.host_si_scr: sid-system-cfg-register-model`
- `host_si_cl1_sram.exists: true`
- `host_si_cl1_sram.size: 16777216`
- `host_si_cl1_sram.nonzero_bytes: 233297`

Key runtime evidence:

```text
[INF] BL2: SI CL1 pre load start
[INF] BL2: SI CL1 pre load complete
[INF] Primary   slot: version=4.1.0+0
[INF] Secondary slot: version=4.1.0+0
[INF] Image 4 RAM loading to 0x70185c00 is succeeded.
[INF] Key hash matched for image 4 at slot 0
[INF] Image 4 loaded from the primary slot
[INF] BL2: SI CL1 post load start
[INF] BL2: SI CL1 post load complete
```

The `--platform-param platform.host_si_scr.trace=true` diagnostic run
`build/qbox-fvp-rd-aspen/rse-t019av-host-scr-cl1-present-20260524-v1/`
records the firmware-visible SCR accesses:

```text
platform.host_si_scr read offset=0x70 len=0x4 value=0x1
platform.host_si_scr write offset=0x300 len=0x4 value=0x1
platform.host_si_scr write offset=0x300 len=0x4 value=0x101
platform.host_si_scr write offset=0x300 len=0x4 value=0x301
platform.host_si_scr write offset=0x300 len=0x4 value=0x701
platform.host_si_scr write offset=0x300 len=0x4 value=0xf01
platform.host_si_scr write offset=0x500 len=0x4 value=0x11
platform.host_si_scr write offset=0x600 len=0x4 value=0x1
```

Current blocker classification:

`si_cl1_runtime_rpmsg_gap`: the RSE-side CFG2 CL1 presence check and image
load path are now modeled, but QBox still lacks a real SI CL1 runtime peer.
The latest short timeout stops after SI CL0 slot-version output, before
AP/Linux. Earlier Linux-reaching evidence still needs to be re-run with this
SCR model and then extended beyond resource-table seeding to prove
`virtio_rpmsg_bus`/`rpmsg_net` and the FVP runtime markers
`SCMI Comms subscribed to power state notifications` and `RT_0`.

### 2026-05-24 T019AV RPMsg Name-Service Increment

The first SI CL1 RPMsg service-model increment is now implemented in QBox. It
does not instantiate a real SI CL1 CPU yet. It extends the existing AP/SI CL1
MHUv3 doorbell compatibility path so that, after the Linux remoteproc attach
doorbell, QBox can poll the Linux RX virtqueue and inject the OpenAMP-compatible
RPMsg name-service packet for the generated Zephyr CL1 endpoint.

Local source evidence used for this increment:

- `arm-zena-css/documentation/design/hipc.rst`: SI CL1 shared memory layout is
  resource table, vring0, vring1, and virtio buffer, each `128 KiB`.
- `tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts`:
  `si_cl1_rproc_rsctbl@0x00100000`, `si_cl1_vdev0vring0@0x00120000`,
  `si_cl1_vdev0vring1@0x00140000`, and
  `si_cl1_vdev0buffer@0x00160000`.
- `sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c`:
  Linux maps the loaded resource table, prepares the reserved vrings, and uses
  `vq0_rx` mailbox callbacks to call `rproc_vq_interrupt()`.
- `build/tmp_baremetal/work-shared/fvp-rd-aspen/kernel-source/drivers/rpmsg/virtio_rpmsg_bus.c`:
  Linux publishes RX buffers through the input virtqueue and expects inbound
  RPMsg packets in used descriptors before `rpmsg_recv_done()`.
- `build/tmp_baremetal/work-shared/fvp-rd-aspen/kernel-source/drivers/rpmsg/rpmsg_ns.c`:
  channel creation is driven by `struct rpmsg_ns_msg` delivered to
  `RPMSG_NS_ADDR = 53`.
- `arm-zena-css/components/safety_island/zephyr/src/overlays/hipc/fvp_rd_aspen_safety_island_c1.conf`:
  the generated CL1 endpoint advertises `CONFIG_VETH_NS_NAME="ethsi1"`.
- `arm-zena-css/components/safety_island/zephyr/src/drivers/ethernet/veth_rpmsg.c`:
  the Zephyr side creates an OpenAMP endpoint and uses the mailbox binding for
  attach, ack, and virtqueue notification channels.

QBox implementation details:

- `mhuv3_stub` now has optional CCI parameters `rpmsg_ns_enable`,
  `rpmsg_ns_name`, `rpmsg_ns_remote_addr`, `rpmsg_ns_vring_address`,
  `rpmsg_ns_vring_num`, `rpmsg_ns_vring_align`,
  `rpmsg_ns_signal_channel`, `rpmsg_ns_signal_value`,
  `rpmsg_ns_signal_delay_ns`, `rpmsg_ns_poll_period_ns`, and
  `rpmsg_ns_max_polls`.
- The implementation consumes one Linux-published RX descriptor from the split
  virtqueue, writes an RPMsg header plus `rpmsg_ns_msg`, updates the used ring,
  and signals the paired MBX doorbell channel.
- The later host-kick timing fix defers name-service injection at the attach
  ACK point and starts it when Linux notifies the remote RX virtqueue after
  creating the `rpmsg_ns` endpoint. The AP/SI CL1 config adds a 1 ms SystemC
  signal delay so Linux can leave probe context before the remote interrupt.
- The RSE Lua config enables this only for the AP/SI CL1 pair, with
  `rpmsg_ns_name = "ethsi1"`, vring0 at `0x00120000`, 32 descriptors, 16-byte
  alignment, `vq0_rx` notification value `0x1`, and
  `rpmsg_ns_signal_delay_ns = 1000000`.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| map validation | pass | `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` |
| MHU/RPMsg component build | pass | `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 8` |
| MHU/RPMsg component test | pass | `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` |
| platform build | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 8` |
| short RSE runtime | expected timeout before AP/Linux | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=4096 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --post-login-probe --out-dir build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-ns-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| host-kick runtime | pass | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=20000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --post-login-probe --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --out-dir build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1` |
| coverage audit | pass | `scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/qbox-primary-console.log --output build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/coverage-audit.json` |

Runtime artifact root:

- `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-ns-20260524-v2/`
- `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/`

Short runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- `timed_out: true`
- `platform_returncode: -15`
- latest RSE UART marker: `Primary   slot: version=2.16.0+0`
- `host_si_cl0_sram`: `host_window_contains_nonzero_runtime_data`
- `host_si_cl1_sram`: `host_window_contains_nonzero_runtime_data`
- `post_login_probe.sent_login: false`

Host-kick runtime result:

- `passed: true`
- `blocker: none`
- `timed_out: false`
- `post_login_probe.complete: true`
- return codes: `arm_si_rproc_modprobe_rc:0`, `rpmsg_ns_modprobe_rc:0`,
  `virtio_rpmsg_bus_modprobe_rc:0`, `rpmsg_net_modprobe_rc:0`,
  `ethsi1_iplink_rc:0`
- driver patterns: `arm_si_rproc`, `rpmsg`, `virtio`, `smmu_v3`, `pl011_uart`,
  and `hipc_ethsi1` all true
- coverage audit: `implemented_blocks_passed: true`,
  `full_coverage_passed: true`, `implemented_failed: 0`
- MHU trace: `rpmsg-ns-defer-until-host-kick`,
  `rpmsg-ns-injected name=ethsi1 remote_addr=0x400 vring=0x120000`,
  `rpmsg-ns-signal-delay delay_ns=1000000`, and `rpmsg-ns-signaled`
- Linux console: `virtio_rpmsg_bus virtio6: rpmsg host is online`,
  `virtio_rpmsg_bus virtio6: creating channel ethsi1`,
  `probe of virtio6.ethsi1.-1.1024 returned 0`,
  `rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1`, and `ethsi1_iplink_rc:0`

This closes the functional T019AV service-model requirement for a
Linux-visible SI CL1 RPMsg endpoint. Remaining fidelity work is to replace the
service-model endpoint with a real SI CL1 CPU/Zephyr peer and verify packet
data-plane behavior.

### 2026-05-24 GDB All-Target Debug Environment Evidence

The GDB helper now creates a file-backed debug bundle for the active
`fvp-rd-aspen` CFG2 setup:

- QBox host: `gdb/qbox-host-sample.gdb` launches `platforms-vp` under GDB;
  the helper sends `SIGINT` to the child GDB after the requested sample delay
  and records `info threads` plus `thread apply all bt`.
- TF-M/RSE: `gdb/tfm-rse-current.gdb` connects to
  `platform.rse_cpu_pass.cpu_0.gdb_port=12340`, loads BL1_1, and adds BL1_2
  and BL2 symbols at their ELF `.text` addresses.
- Linux/AP: `gdb/linux-ap.gdb` connects to
  `platform.ap_cpu_0.gdb_port=12341`; in this QEMU instance, `info threads`
  exposes CPU#0-CPU#3.
- SCP-Firmware: `gdb/scp-firmware-symbols.gdb` maps the
  `scp-firmware/2.16.0+git` source and symbols. This is symbol/source-only
  because the current QBox path uses an SCP service model rather than a live
  SCP CPU.
- SI CL1 Zephyr: `gdb/si-cl1-zephyr-symbols.gdb` maps the
  `zephyr-demos-cl1/4.1.0+git` source and symbols. This is symbol/source-only
  until a live SI CL1 CPU model is instantiated.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| GDB helper syntax | pass | `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` |
| all-target GDB probe | pass with expected early timeout/host attach policy | `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-all-targets-v3 --runner-timeout 45 --port-timeout 12 --gdb-timeout 10 --sample-delay 3 --host-sample --host-sample-seconds 8 --launch` |

Artifact root:

- `build/qbox-fvp-rd-aspen/gdb-debug-20260524-all-targets-v3/`

Probe result:

- `rse_port_listening: True`
- `tfm_initial_probe_rc: 0`
- `tfm_later_probe_rc: 0`
- `ap_port_listening: True`
- `linux_initial_probe_rc: 0`
- `linux_later_probe_rc: 0`
- `qbox_host_probe_rc: 1`, expected on this host because direct attach is
  blocked by `ptrace_scope`
- `host_gdb_sample_backtrace_captured: True`

Observed progress:

```text
TF-M/RSE later PC: 0x11007342 <nor_cfi_reg_read+2>
TF-M/RSE stack:
  Driver_FLASH0_ReadData
  bl1_image_copy_to_sram
  copy_and_decrypt_image
  bl1_2_validate_image
  main

AP/Linux GDB threads:
  CPU#0 [running] PC=0x82000 SP=0x0
  CPU#1 [halted ] PC=0x82000
  CPU#2 [halted ] PC=0x82000
  CPU#3 [halted ] PC=0x82000

QBox host sample:
  sc_core::sc_start()
  QemuCpu::wait_for_work()
  QemuCpu::prepare_run_cpu()
```

Interpretation:

The short GDB probe confirms the current early window is still in TF-M BL1_2
flash/image validation, before AP/Linux execution. The host sample confirms
the QBox process and AP QEMU TCG threads are observable under GDB without
changing system ptrace policy. SCP-Firmware and SI CL1 Zephyr are prepared for
symbol/source inspection, but they are not live GDB targets in the current
service-model configuration.

### 2026-05-24 StrataFlash DMI And Sample-Only GDB Progress Evidence

The StrataFlash J3 model now preserves the TLM DMI hint for read-array
transactions when `enable_dmi` is set and accepts QEMU map-time
`TLM_IGNORE_COMMAND` DMI queries in read-array mode. DMI remains read-only and
is rejected when the flash is in command/status mode. The goal is to avoid
forcing every TF-M BL2 image-load byte through `b_transport()` while still
invalidating DMI on command/program/erase writes.

The GDB helper also gained `--sample-only`, which waits until the requested
sample delay before attaching to live CPU GDB targets. This avoids perturbing
early TF-M execution with initial GDB probes when the immediate question is
"where is it now?"

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| StrataFlash DMI unit test | pass | `cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` |
| StrataFlash DMI ctest | pass | `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` |
| GDB helper syntax | pass | `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| short runtime | expected timeout before AP/Linux | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=4096 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 160 --post-login-probe --out-dir build/qbox-fvp-rd-aspen/rse-t019aw-flash-dmi-map-query-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| sample-only GDB probe | pass | `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --runner-timeout 170 --port-timeout 25 --gdb-timeout 15 --sample-delay 150 --out-dir build/qbox-fvp-rd-aspen/gdb-t019aw-sample-only-20260524-v1` |
| FVP file-backed verbose log smoke | pass | `python3 scripts/runfvp_log_boot.py --timeout 12 --require none --runfvp-verbose --out-dir build/fvp-boot-logs/rse-qbox-debug-telnet-20260524-v1` |

Artifact roots:

- `build/qbox-fvp-rd-aspen/rse-t019aw-flash-dmi-map-query-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t019aw-flash-dmi-map-query-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t019aw-sample-only-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-debug-env-20260524-v2/`
- `build/fvp-boot-logs/rse-qbox-debug-telnet-20260524-v1/`

Runtime result:

- `passed: false`
- `blocker: qbox_platform_timeout`
- RSE UART reaches `Starting bootloader`, `BL2: SI CL1 pre load complete`,
  `Primary   slot: version=4.1.0+0`, and `Secondary slot: version=4.1.0+0`
- `host_si_cl1_sram`: header and code prefix match the primary SI CL1 flash
  slot at `0x167000`/`0x167400`, but `copied_full_boot_image` remains false
- `host_si_cl0_sram`: `host_window_copy_not_observed`
- AP/Linux remains at the reset/vector placeholder and the post-login probe
  does not send login commands

Sample-only GDB result:

```text
TF-M/RSE later PC: 0x31024c9c <nor_cfi_reg_read+2>
TF-M/RSE stack:
  cfi_strataflashj3_read(... data=0x70185c00 ..., cnt=287277)
  Driver_FLASH0_ReadData
  flash_area_read
  boot_decrypt_and_copy_image_to_sram
  boot_load_image_to_sram
  boot_load_and_validate_images
  boot_go_for_image_id(image_id=4)
  main

AP/Linux:
  CPU#0 [running] PC=0x82000 SP=0x0
  CPU#1-CPU#3 [halted] PC=0x82000
```

FVP comparison smoke:

```text
FVP duration: 14.474s
RSE UART reaches:
  BL2: AP BL2 post load complete
  Image 0 RAM loading to 0x3103f800 is succeeded.
  BL2: AP power domain attributes = 0x40000000.
SI CL0/SCP reaches:
  [FWK] Module initialization complete!
  [SI0-PLATFORM] AP domain has been turned on, performing ATU cfg check
SI CL1 reaches:
  *** Booting Zephyr OS build v4.1.0 ***
  PFDI service ready (4 CPUs)
  Network interface configured
```

Interpretation:

The current forward-progress limit is TF-M BL2 loading SI CL1 image ID 4 from
the CFI/StrataFlash path into host SI CL1 SRAM. QBox host, TF-M/RSE, and
AP/Linux GDB paths are usable. SCP-Firmware symbols are available, but live SCP
GDB is not possible in the current `service-model` strategy because no SCP CPU
is instantiated yet. The FVP file-backed smoke also confirms CFG2 reaches real
SI CL1 Zephyr and SI CL0/SCP startup quickly, so the QBox gap is not expected
firmware latency. The next implementation step should either make the flash DMI
path effective for the QEMU read loop or add a TF-M/FVP-equivalent bulk read
path that preserves command-mode behavior while avoiding byte-by-byte SystemC
trips during RAM-load image copies.

### 2026-05-24 RSE Local Crypto And Boot-Flash Co-Location Evidence

GDB showed that short RSE-only QBox runs were spending most of their time in
software-visible but remote-RPC-heavy paths:

- before co-location, TF-M/RSE sampled in CC3XX-backed LMS/LMOTS hash
  validation (`cc3xx_lowlevel_hash_uninit()` and callers);
- after local KMU/CC3XX co-location, the sampled point moved to
  `cfi_strataflashj3_read()` while copying SI CL1 image ID 4 from RSE boot
  flash into host SI CL1 SRAM;
- after local boot-flash co-location, the sampled point moved again to
  `clear_safety_island_memory()` / `memset()` while clearing the
  ATU-translated SI CL0 host-SRAM window.

This increment first introduced these QBox Lua knobs as opt-in controls. The
later short-timeout validation in
`build/qbox-fvp-rd-aspen/rse-current-all-rse-dmi-20260524-v1/` supersedes that
initial policy by enabling the RSE-local crypto, RSE-local boot flash, and RSE
ITCM/DTCM/VM DMI controls by default:

- `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true`: instantiate `rse_kmu` and `cc3xx`
  inside `platform.rse_cpu_pass`, with a local crypto router and absolute
  address preservation so CPU accesses and KMU key-export writes both reach the
  same local CC3XX target.
- `QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true`: instantiate `strata_flash_j3`
  inside `platform.rse_cpu_pass`, while leaving the default main-process flash
  path unchanged when the knob is false.
- `QBOX_RDASPEN_RSE_REMOTE_QUANTUM_NS=<n>`: pass the Cortex-M55 remote
  platform quantum into the child process. A 50 ms quantum did not materially
  improve progress by itself.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check` |
| map validation | pass | `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` |
| default-path 20s regression | expected timeout, no failure patterns | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --out-dir build/qbox-fvp-rd-aspen/rse-default-regression-20s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| local crypto smoke | expected timeout, BL2 decrypt retained | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --out-dir build/qbox-fvp-rd-aspen/rse-local-crypto-smoke-20260524-v4 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| local crypto 60s | expected timeout, SI CL1 SRAM copy observed | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-local-crypto-60s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| local crypto plus local flash 60s | expected timeout, reaches SI CL0 pre-load | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-local-crypto-flash-60s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| local crypto plus local flash 90s | expected timeout, SI CL0 SRAM copy observed | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --out-dir build/qbox-fvp-rd-aspen/rse-local-crypto-flash-90s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| local crypto plus local flash GDB sample | pass | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --sample-delay 80 --runner-timeout 100 --port-timeout 10 --gdb-timeout 10 --out-dir build/qbox-fvp-rd-aspen/gdb-local-crypto-flash-80s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| short all-target GDB fault sample | pass, RSE HardFault identified | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --sample-delay 4 --runner-timeout 15 --port-timeout 8 --gdb-timeout 10 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-short-all-targets-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Artifact roots:

- `build/qbox-fvp-rd-aspen/rse-default-regression-20s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-local-crypto-smoke-20260524-v4/`
- `build/qbox-fvp-rd-aspen/rse-local-crypto-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-local-crypto-flash-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-local-crypto-flash-90s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-local-crypto-45s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-local-crypto-flash-80s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-short-all-targets-20260524-v2/`

Runtime deltas:

| Runtime | RSE UART / SRAM result |
| --- | --- |
| default 20s regression | reaches `BL2 image decrypted successfully`; no failure patterns; CL0/CL1 SRAM copy not observed |
| local crypto 60s | reaches `BL2: SI CL1 pre load complete`; `host_si_cl1_sram` records non-zero runtime data and primary-slot copy evidence |
| local crypto plus local boot flash 60s | reaches `Image 4 loaded from the primary slot`, `BL2: SI CL1 post load complete`, and `BL2: SI CL0 pre load start` |
| local crypto plus local boot flash 90s | reaches `BL2: SI CL0 pre load complete`; `host_si_cl0_sram` records non-zero runtime data, header match at flash offset `0x67000`, code match at `0x67400`, and mapped prefix `0xb40` |

GDB samples:

```text
local crypto, 45s:
  PC: 0x31023136 <cfi_strataflashj3_read+66>
  Stack:
    Driver_FLASH0_ReadData
    flash_area_read
    boot_decrypt_and_copy_image_to_sram
    boot_load_image_to_sram
    boot_go_for_image_id(image_id=4)

local crypto plus local boot flash, 80s:
  PC: 0x3101d160 <memset+42>
  Stack:
    clear_safety_island_memory
    boot_platform_pre_load_si_cl0
    boot_platform_pre_load
    main

short all-target fault sample, 4s:
  TF-M/RSE PC: 0x110004ec <exception_handler>
  TF-M/RSE SP: 0x300055d0
  Fault regs: CFSR=0x01001000, HFSR=0x40000000
  Stack sample: 0xa4093822 repeated at 0x300055d0..0x30005600
  AP/Linux: CPU#0 running at 0x82000, CPU#1-3 halted at 0x82000
  SCP-Firmware symbols: rdaspen-si0-bl2.elf entry 0x120000000
  QBox host: sc_core::sc_start plus QemuCpu::wait_for_work/prepare_run_cpu
```

Interpretation:

The co-location path does not change the modeled programming interface; it
reduces high-frequency RemotePass traffic for RSE-local CC3XX/KMU and
boot-flash accesses. The next bottleneck is ATU-translated host SRAM clearing
and later CL0 image copy through host-side windows. Moving ATU/host SRAM
locally needs more care than crypto/flash because SCR, PPU, MHU, AP, and SI
models must keep observing the same state. Do not make these local knobs
default until AP-enabled runs prove equivalent behavior. The later short
fault sample also shows a rebuilt early-BL1_1 regression before the RSE UART
banner: the active stack is overwritten with the CC3XX RNG fill pattern
`0xa4093822` while TF-M's TRAM-enabled startup runs
`startup_dma_double_word_memset(DTCM_CPU0_BASE_S, DTCM_SIZE, ...)`. That points
at QBox's RSE DTCM/ITCM CPU0 alias modeling around the DMA350/TRAM erase/fill
sequence, rather than a Linux or SCP execution failure.

### 2026-05-24 GDB Keepalive And LCM OTP Read-Verify Evidence

The GDB helper and RSE runner were updated for firmware-fatal debug sessions:

- `scripts/run_qbox_fvp_rd_aspen_rse.py` now accepts
  `--ignore-fail-patterns`, which records `[ERR]` matches but does not stop
  QBox before GDB probes can attach.
- `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` passes that option through and
  now captures TF-M/RSE general registers `r0..r12` plus `lr` in generated GDB
  scripts.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| Python syntax | pass | `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| map validation | pass | `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` |
| keepalive all-target GDB probe | pass, RSE/AP GDB probes completed | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_LCM_TRACE=true QBOX_RDASPEN_LCM_TRACE_LIMIT=140 python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --sample-delay 4 --runner-timeout 15 --port-timeout 8 --gdb-timeout 10 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-keepalive-regs-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| DTCM unified no-DMI comparison | expected timeout, same LCM decoded error | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_SPLIT_CPU0_DTCM_ALIAS=false QBOX_RDASPEN_LCM_TRACE=true QBOX_RDASPEN_LCM_TRACE_LIMIT=60 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 8 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-dtcm-unified-no-dmi-probe-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --qemu-trace --exception-trace --pc-trace --pc-trace-interval 1 --pc-trace-limit 160` |

Artifact roots:

- `build/qbox-fvp-rd-aspen/gdb-dtcm-no-dmi-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-dtcm-no-dmi-keepalive-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-keepalive-regs-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-dtcm-unified-no-dmi-probe-20260524-v1/`
- FVP comparison baseline:
  `build/fvp-boot-logs/rse-tcm-short-probe-20260524-v2/`

Latest GDB sample:

```text
TF-M/RSE:
  PC: 0x11006e24 <boot_platform_error_state+24>
  SP: 0x30005630
  LR: 0x11006e25
  r4: 0x95a5a5be
  CFSR/HFSR/SFSR: all zero
  Backtrace:
    boot_platform_error_state(error=2510661054)
    main() at bl1/bl1_1/main.c:139

Error decode:
  0x95a5a5be ^ 0xa5a5a5a5 = 0x3000001b
  0x3000001b = LCM_ERROR_OTP_READ_READ_VERIFY_FAIL

AP/Linux:
  CPU#0 running at PC 0x82000, SP 0x0
  CPU#1-3 halted at PC 0x82000
  Linux symbols do not match yet; AP has not booted.

SCP-Firmware:
  rdaspen-si0-bl2.elf symbols loaded, entry 0x120000000
  No live SCP CPU target in service-model mode.

QBox host:
  sc_core::sc_start() and QemuCpu::wait_for_work()/prepare_run_cpu()
  backtrace captured through the host-GDB wrapper.
```

Source mapping:

- `platform/ext/common/boot_hal_bl1_1.c` prints the fatal boot error and spins
  in `boot_platform_error_state()`.
- `platform/ext/target/arm/rse/common/bl1/boot_hal_bl1_1.c` calls
  `minimal_otp_init()` before later BL1_1 setup.
- `platform/ext/target/arm/rse/common/otp_lcm.c` selects
  `tfm_plat_otp_mini_init()` in SE lifecycle and loads OTP area metadata.
- `platform/ext/target/arm/drivers/lcm/lcm_drv.c` returns
  `LCM_ERROR_OTP_READ_READ_VERIFY_FAIL` when the LCM OTP double-read
  validation word does not match the buffered word.
- `lib/fih/src/fih.c` defines the FIH return mask `0xa5a5a5a5` used in the
  error decode above.

Interpretation:

The DTCM no-DMI path removes the previous early BL1_1 HardFault. Current
progress is now a normal TF-M fatal-error loop after `Starting TF-M BL1_1`,
with no Arm M-profile fault registers set. The active blocker is LCM OTP
read-verify fidelity around TF-M's mini OTP initialization. Linux/AP and
SCP-Firmware do not progress because RSE has not reached the RSE-SCP/AP
handoff. The FVP short baseline reaches BL1_2/BL2 and Safety Island image
loading in roughly 13 seconds, so this remains a QBox model gap.

### 2026-05-24 User Short All-Target GDB Probe

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| all-target GDB bundle/probe | pass, RSE/AP ports and symbol probes completed | `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-user-short-v1 --launch --runner-timeout 35 --port-timeout 10 --gdb-timeout 8 --sample-delay 3 --host-sample --host-sample-seconds 5 --ignore-fail-patterns` |
| Python syntax | pass | `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox whitespace | pass | `git -C tools/qbox diff --check -- platforms/fvp-rd-aspen-rse/conf.lua platforms/fvp-rd-aspen/README.md` |

Artifact root:

- `build/qbox-fvp-rd-aspen/gdb-debug-20260524-user-short-v1/`

Latest short GDB state:

```text
TF-M/RSE:
  initial PC: 0x110027f8 <atu_rse_set_start_logical_address+4>
  later PC: 0x11006e24 <boot_platform_error_state+24>
  later SP: 0x30005630
  decoded error: 0x95a5a5be ^ 0xa5a5a5a5 = 0x3000001b

AP/Linux:
  CPU#0 running at PC 0x82000, SP 0x0
  CPU#1-3 halted at PC 0x82000

SCP-Firmware:
  rdaspen-si0-bl2.elf symbols loaded, entry 0x120000000
  no live SCP CPU target in current service-model mode

QBox host:
  direct attach blocked by ptrace_scope
  host-GDB wrapper captured sc_core::sc_start()
  and QemuCpu::wait_for_work()/prepare_run_cpu() backtraces
```

Interpretation:

The file-backed GDB environment is usable for QBox host, TF-M/RSE, AP/Linux,
SCP-Firmware symbol/source inspection, and SI CL1 Zephyr symbol/source
inspection. Live SCP-Firmware stepping remains a platform-model gap: the
current QBox RSE path uses a service-model SCP endpoint and does not instantiate
an SCP CPU with a `gdb_port`. AP/Linux remains at the reset/holding address
because RSE stops in the BL1_1 fatal loop before RSE-SCP/AP handoff.

### 2026-05-24 BL1_2 Hash GDB And DTCM CPU0 Alias Evidence

Short GDB and runtime probes narrowed the post-LCM BL1_1 failure to the DTCM
CPU0 alias used by the CC3XX final hash DMA block.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| CC3XX focused build | pass | `cmake --build tools/qbox/build --target cc3xx-tests --parallel 8` |
| CC3XX focused tests | pass | `ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure` |
| platform build | pass | `cmake --build tools/qbox/build --target platforms-vp --parallel 8` |
| Lua syntax | pass | `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| map validation | pass | `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` |
| QBox whitespace | pass | `git -C tools/qbox diff --check -- platforms/fvp-rd-aspen-rse/conf.lua systemc-components/cc3xx/include/cc3xx.h tests/components/cc3xx/cc3xx-tests.cc platforms/fvp-rd-aspen/README.md` |
| hash DMA trace | expected timeout, hash DMA source captured | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=dma QBOX_RDASPEN_CC3XX_TRACE_LIMIT=2400 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-bl1-2-cc3xx-dma-trace-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| DTCM unified default runtime | expected timeout, reaches BL1_2 and BL2 decrypt failure | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 25 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-dtcm-unified-default-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| post-alias all-target GDB probe | pass, RSE/AP ports and symbol probes completed | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-post-alias-v1 --launch --runner-timeout 30 --port-timeout 8 --gdb-timeout 8 --sample-delay 4 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Artifact roots:

- `build/qbox-fvp-rd-aspen/rse-bl1-2-cc3xx-dma-trace-20260524-v2/`
- `build/qbox-fvp-rd-aspen/gdb-bl1-2-source-alias-compare-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-bl1-2-dtcm-alias-compare-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-dtcm-unified-default-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-debug-20260524-post-alias-v1/`

Observed state:

```text
CC3XX hash DMA:
  source 0x1a004000 length 0x1fc0
  source 0x34003820 length 0x40

GDB at bl1_1_validate_image_at_addr + 94:
  sha256(0x10004000..0x10006000) = 18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
  sha256(0x1a004000..0x1a006000) = 18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
  stored hash = 18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
  computed hash = b3c904a855b9d1e8ff160d56ad1fd93c797538e6a8b4c08fe33b74a6d1adf228

DTCM final-block aliases:
  0x30003820 = BL1_2 tail, 64 zero bytes
  0x34003820 = repeated 0xa4093822 TRAM-fill pattern
```

The component-level CC3XX regression for an 8192-byte TF-M-style hash update
plus final 64-byte `AUTO_HW_PADDING` block passes, and SHA-256 over the first
`0x1fc0` ITCM bytes plus the stale `0x34003820` block exactly equals the
incorrect GDB-computed hash. The root cause is therefore the split DTCM CPU0
alias backing store, not SHA-256 math or the ITCM/OTP image copy.

`QBOX_RDASPEN_RSE_SPLIT_CPU0_DTCM_ALIAS` now defaults to `false`. With the
unified DTCM alias default, a 25-second local-crypto/local-boot-flash run
progresses from the prior BL1_2 image-validation failure to:

```text
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[ERR] BL2 image failed to decrypt
```

The post-alias GDB bundle confirms QBox host, TF-M/RSE, AP/Linux, SCP-Firmware
symbol, and SI CL1 symbol debugging remain available. AP/Linux stays at
`0x82000`, and SCP-Firmware is still symbol-only because the current path uses
the SCP service model rather than a live SCP CPU.

### 2026-05-24 RSE VM DMI And Post-Decryption GDB Evidence

Short GDB/runtime probes narrowed the next post-alias failure to RSE VM0/VM1
DMI visibility. With VM DMI enabled before the DMI-manager access fix, GDB saw
the encrypted-image IV copied into VM0 as only the low byte `0x67` followed by
zero words, while the raw boot flash backing file contains the full IV bytes
`67 a4 79 10 ...`.

The focused byte-store class is now fixed. `QemuInstanceDmiManager::get_region`
was rebuilding a local `tlm_dmi` without preserving granted access. The newer
readonly guard then installed writeable QEMU DMI regions as read-only, so CPU
byte stores were dropped. Preserving `info.get_granted_access()` makes both the
plain and shared-memory byte-store tests pass with DMI enabled. An additional
shared-memory external-write test also passes: after the CPU installs a QEMU
DMI mapping, a SystemC-side write to the backing `gs_memory` is visible to CPU
loads.

That access fix was not sufficient for RemotePass, because the remote QEMU
process still received pointer-backed QEMU RAM aliases rather than aliases to
the same SystemC shared-memory file descriptor. The intermediate VM-DMI-on
sample reached TF-M BL1_2 AES decrypt, then the RSE UART still reported
`BL2 image failed to decrypt`. GDB captured the CPU in TF-M's VM ECC
read-modify-write helper:

```text
TF-M/RSE PC: 0x1100f750 <vm_partial_write_fix_apply+28>
Backtrace:
  vm_partial_write_fix_apply
  cc3xx_dma_platform_epilogue
  trigger_dma
  cc3xx_lowlevel_dma_buffered_input_data
  cc3xx_lowlevel_aes_update
  bl1_aes_256_ctr_decrypt
  copy_and_decrypt_image
  bl1_2_validate_image
  main
```

The follow-up fix exports `memory_region_init_ram_from_fd()` through libqemu
and passes shared-memory fd/offset metadata from SystemC memory services into
QEMU DMI aliases. With that fd-backed remote-DMI path,
`QBOX_RDASPEN_RSE_VM_DMI=true` now reaches `BL2 image decrypted successfully`
in both a short RSE runtime and the all-target AP-enabled GDB sample.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| focused build | pass | `cmake --build tools/qbox/build --target memory-tests aarch64-dmi-byte-store-test platforms-vp --parallel 8` |
| shared-memory fd unit test | pass | `ctest --test-dir tools/qbox/build -R '^memory-tests$' --output-on-failure` |
| DMI byte-store no-DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0` |
| DMI byte-store DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0` |
| shared-memory DMI byte-store build | pass | `cmake --build tools/qbox/build --target aarch64-shmem-dmi-byte-store-test --parallel 8` |
| shared-memory DMI byte-store DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0` |
| shared-memory DMI byte-store no-DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0` |
| CMake regeneration | pass | `cmake --preset gcc` |
| shared-memory external-write build | pass | `cmake --build tools/qbox/build --target aarch64-shmem-dmi-external-write-test --parallel 8` |
| shared-memory external-write DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-external-write-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0` |
| shared-memory external-write no-DMI control | pass | `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-external-write-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0` |
| earlier VM-DMI-on runtime | expected decrypt failure reproduced before fd-backed remote DMI | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-fd-fix-current-20260524-v1` |
| earlier VM-DMI-on GDB sample with effective env | pass, expected decrypt failure captured before fd-backed remote DMI | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 18 --port-timeout 8 --gdb-timeout 8 --sample-delay 10 --out-dir build/qbox-fvp-rd-aspen/gdb-vm-dmi-perm-fix-effective-env-20260524-v1` |
| remote Cortex-M55 DMI byte-store on/off | pass | `timeout 45s ctest --test-dir tools/qbox/build -R 'cortex_m55_remote_dmi_byte_store_(on|off)' --output-on-failure` |
| current VM-DMI-on runtime after fd-backed remote DMI | expected timeout, reaches BL2 decrypt success | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 18 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-remote-fd-fix-20260524-v1` |
| all-target VM-DMI-on GDB sample after fd-backed remote DMI | pass, RSE/AP ports and host sample captured | `QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 20 --port-timeout 5 --gdb-timeout 6 --sample-delay 12 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-rse-vm-dmi-remote-fd-fix-20260524-v4` |
| current VM-DMI-off runtime | expected timeout, reaches BL2 decrypt success | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-off-fd-fix-current-20260524-v1` |
| short VM-DMI-off runtime | expected timeout, reaches BL2 decrypt success | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| 60s VM-DMI-off runtime | expected timeout, no fatal logs; still before BL2 jump | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 60 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-60s-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| 28s all-target GDB sample | pass, post-decrypt BL1_2 LMS/LMOTS point captured | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 45 --port-timeout 8 --gdb-timeout 8 --sample-delay 28 --out-dir build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| GDB helper syntax | pass | `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py` |

Artifact roots:

- `build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-vm-dmi-fd-fix-current-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-vm-dmi-off-fd-fix-current-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-vm-dmi-perm-fix-effective-env-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-pc-trace-post-decrypt-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2/`
- `build/qbox-fvp-rd-aspen/rse-vm-dmi-remote-fd-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-rse-vm-dmi-remote-fd-fix-20260524-v4/`

Observed RSE UART:

```text
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
```

Earlier VM-DMI-on GDB sample after the DMI access fix but before fd-backed
remote DMI:

```text
Launch environment:
  QBOX_RDASPEN_RSE_VM_DMI=true

RSE UART:
  [INF] Starting TF-M BL1_2
  [INF] Attempting to boot image 0
  [ERR] BL2 image failed to decrypt

TF-M/RSE:
  PC 0x1100f750 <vm_partial_write_fix_apply+28>
  caller chain includes cc3xx_dma_platform_epilogue,
  cc3xx_lowlevel_aes_update, bl1_aes_256_ctr_decrypt,
  copy_and_decrypt_image, and bl1_2_validate_image

AP/Linux:
  CPU#0 remains at PC 0x82000, SP 0x0
```

Current VM-DMI-on all-target GDB sample after fd-backed remote DMI:

```text
Launch environment:
  QBOX_RDASPEN_ENABLE_AP_CPUS=true
  QBOX_RDASPEN_RSE_VM_DMI=true

RSE UART:
  [INF] Starting TF-M BL1_2
  [INF] Attempting to boot image 0
  [INF] BL2 image decrypted successfully

TF-M/RSE:
  PC 0x1100be44 <cc3xx_lowlevel_dma_buffered_input_data+4>
  caller chain includes cc3xx_lowlevel_hash_update,
  mbedtls_lmots_calculate_public_key_candidate,
  mbedtls_lms_verify, validate_image_signature,
  bl1_2_validate_image, and main

AP/Linux:
  CPU#0 running at PC 0x82000, SP 0x0
  CPU#1-3 halted at PC 0x82000

SCP-Firmware:
  symbols/source loaded from rdaspen-si0-bl2.elf, entry 0x120000000
  no live SCP CPU GDB port while using service-model strategy
```

28-second VM-DMI-off GDB sample:

```text
TF-M/RSE PC: 0x1100a42c <hash_digit_array+112>
Backtrace:
  hash_digit_array
  mbedtls_lmots_calculate_public_key_candidate
  mbedtls_lms_verify
  pq_crypto_verify
  validate_image_signature
  bl1_2_validate_image_at_addr
  bl1_2_validate_image
  main
Fault registers: CFSR/HFSR/SFSR all zero

AP/Linux:
  CPU#0 running at PC 0x82000, SP 0x0
  CPU#1-3 halted at PC 0x82000
```

The 60-second PC trace agrees with the GDB sample: RSE stays secure with
`VTOR_S=0x10004000`, fault registers stay zero, and samples remain in BL1_2
flash copy, CC3XX hash state handling, and LMS/LMOTS signature validation.
This is not a reset/fault loop. The next gap is performance/fidelity in the
post-decrypt image-signature path and subsequent AP/Linux handoff. The later
fd-backed RemotePass DMI validation removed the BL2 AES-decrypt blocker for RSE
VM DMI, and the short-timeout default run now enables RSE VM DMI together with
RSE-local crypto/boot-flash placement and RSE ITCM/DTCM DMI.

### 2026-05-24 Short-Timeout RSE DMI Defaults

The fd-backed RemotePass DMI fix makes RSE VM DMI safe enough to combine with
RSE ITCM/DTCM DMI and RSE-local placement for high-traffic devices. A
short-timeout comparison against the Arm FVP shows why this matters:

- FVP verbose run
  `build/fvp-boot-logs/rse-qbox-current-compare-20260524-v1/` completes in
  14.182 seconds and reaches RSE BL2 SI CL0 post-load, SCP boot, and SI CL1
  Zephyr boot logs.
- QBox without the RSE-local/TCM-DMI fast path can spend 120 seconds after
  `BL2 image decrypted successfully` without reaching BL2 image validation.
- QBox with RSE-local CC3XX/KMU, RSE-local boot flash, and RSE ITCM/DTCM/VM
  DMI reaches post-BL2 RSE progress inside the short timeout.

The RSE-local placement does not replace hardware behavior with a forced
success path; it moves the existing KMU, CC3XX, and Strata flash SystemC/TLM
models into the RSE `RemoteCPU` process to avoid high-frequency RPC/TLM
round-trips during TF-M LMS/LMOTS and flash-copy loops. The `false` overrides
remain available for regression debugging.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| FVP verbose baseline | pass, reaches SI CL0 post-load in 14.182s | `python3 scripts/runfvp_log_boot.py --timeout 12 --require none --runfvp-verbose --out-dir build/fvp-boot-logs/rse-qbox-current-compare-20260524-v1` |
| QBox AP path without RSE VM DMI | expected timeout, stalls after BL2 decrypt | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 130s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 120 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-ap-post-login-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox AP path with VM DMI only | expected timeout, still stalls after BL2 decrypt | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true timeout 130s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 120 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-ap-post-login-vm-dmi-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox RSE-only all-RSE-DMI fast path | expected timeout, reaches BL2 validation and SI CL1 pre-load | `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true timeout 45s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 35 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-all-rse-dmi-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox AP all-RSE-DMI fast path | expected timeout, reaches RSE runtime chainload and Linux systemd/driver logs | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true timeout 130s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-ap-all-rse-dmi-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox all-RSE-DMI without local placement | expected timeout, still stalls after BL2 decrypt | `QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true timeout 55s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 45 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-all-rse-dmi-no-local-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox current default RSE-only fast path | expected timeout, reaches BL2 validation, BL2 entry, SI CL1 pre-load, and slot-version output | `timeout 45s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 35 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-default-fast-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| QBox current default AP fast path | expected timeout, reaches RSE runtime chainload, AP0 reset release, Linux boot, PL011/SMMUv3/virtio/PFDI driver output, and systemd startup | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 130s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-current-default-ap-fast-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Key current-default AP-enabled QBox evidence from
`build/qbox-fvp-rd-aspen/rse-current-default-ap-fast-20260524-v1/`:

```text
[INF] BL2 image validated successfully
[INF] Jumping to BL2
[INF] Starting bootloader
[INF] BL2: SI CL1 pre load complete
[INF] Image 4 RAM loading to 0x70185c00 is succeeded.
[INF] BL2: SI CL0 post load complete
[INF] BL2: AP BL2 post load complete
[INF] RSE to SCP SCMI power on AP succeeded.
[INF] Jumping to the first image slot
Booting Linux on physical CPU 0x0000000000 [0x410fd890]
Serial: AMBA PL011 UART driver
arm-smmu-v3 1c0000000.iommu: ias 44-bit, oas 44-bit
probe of 30060000.virtio-net returned 0
pfdi_misc: loading out-of-tree module taints kernel.
systemd[1]: systemd 257.4 running in system mode
```

The same run still times out before the login prompt in the 120-second budget,
so it does not close the full post-login verification tasks. It does prove the
short-timeout path is no longer blocked at BL1_2 signature validation and that
Linux boot and early driver probing start with the faster RSE DMI/default
placement. The earlier all-env AP run
`build/qbox-fvp-rd-aspen/rse-current-ap-all-rse-dmi-20260524-v1/` additionally
showed SI CL1 remoteproc attach before its timeout; the current default AP
budget stops earlier, before the remoteproc attach marker.

### 2026-05-24 AP Firmware GDB Coverage

The RD-Aspen boot-process documentation states that the Primary Compute path is
AP BL2, AP BL31, AP BL32/OP-TEE, AP BL33/U-Boot, systemd-boot, then Linux. The
GDB helper now follows that structure by generating AP TF-A BL2/BL31, OP-TEE,
U-Boot, and Linux scripts in addition to the QBox host, TF-M/RSE,
SCP-Firmware, and SI CL1 Zephyr scripts.

Validation commands:

| Check | Result | Command |
| --- | --- | --- |
| AP firmware script generation | pass, generated `ap-tfa-bl2.gdb`, `ap-tfa-bl31.gdb`, `ap-optee-core.gdb`, and `ap-u-boot.gdb` | `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ap-symbols-smoke-20260524-v1` |
| AP firmware live probes | pass, all AP firmware/Linux probes attach and capture CPU state | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 70s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ap-firmware-probes-20260524-v1 --launch --sample-only --sample-delay 25 --runner-timeout 45 --port-timeout 15 --gdb-timeout 10 --ignore-fail-patterns` |
| AP later sample with host GDB | pass, captures TF-M/RSE, AP, SCP symbols, SI CL1 symbols, and QBox host backtrace | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 170s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ap-login-tail-20260524-v1 --launch --sample-only --sample-delay 105 --runner-timeout 125 --port-timeout 20 --gdb-timeout 12 --host-sample --host-sample-seconds 18 --ignore-fail-patterns` |
| FVP verbose AP timing comparison | expected timeout before Linux, reaches RSE AP power-on, RSE runtime, AP BL31, OP-TEE, and U-Boot | `timeout 45s python3 scripts/runfvp_log_boot.py --timeout 30 --require critical --no-login --runfvp-verbose --out-dir build/fvp-boot-logs/rse-qbox-ap-critical-compare-20260524-v1` |
| quiet-console rootfs runtime | expected timeout before login, rootfs boot entry patched in a sparse per-run WIC copy; logs preserved in slim artifact | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 140 --post-login-probe --ignore-fail-patterns --rootfs-bootargs-profile quiet-console --out-dir build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1 --rootfs build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen.wic` |
| AP PFDI/OP-TEE GDB snapshot | pass, captures RSE runtime, AP BL31 PFDI, AP OP-TEE, AP/Linux pre-Linux state, SCP symbols, and SI CL1 symbols | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1 --launch --sample-only --sample-delay 90 --runner-timeout 125 --port-timeout 18 --gdb-timeout 10 --ignore-fail-patterns` |
| QBox host GDB sample | pass, host-GDB wrapper captured QBox host, SystemC, RPC, QEMU iothread, call_rcu, worker, and AP CPU TCG threads | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1 --launch --sample-only --sample-delay 1 --runner-timeout 20 --port-timeout 8 --gdb-timeout 8 --host-sample --host-sample-seconds 6 --ignore-fail-patterns` |

Key GDB evidence from
`build/qbox-fvp-rd-aspen/gdb-ap-firmware-probes-20260524-v1/`:

```text
TF-M/RSE:
  PC 0x3101d160 <memset+42>
  memset(s=0x753a6000, c=0, n=160688)

AP TF-A BL2:
  CPU#0-3 at PC 0x82000 <bl2_entrypoint>, SP 0x0

SCP-Firmware:
  symbols/source loaded from rdaspen-si0-bl2.elf, entry 0x120000000
  no live SCP CPU target while using the service-model strategy
```

Key later AP sample from
`build/qbox-fvp-rd-aspen/gdb-ap-login-tail-20260524-v1/`:

```text
AP CPU#0 PC 0xfef5b8a4
Instruction sequence matches relocated U-Boot get_ticks + 0x8
CPU#1-3 halted at 0xf1d0
QBox host GDB captured platforms-vp, QEMU iothread, call_rcu, and AP CPU
threads; AP CPU worker threads are waiting/running through QemuCpu paths.
```

The GDB-enabled AP run is slower than the non-GDB short runtime: at the
105-second sample it is still in relocated U-Boot, while
`build/qbox-fvp-rd-aspen/rse-current-default-ap-fast-20260524-v1/` reaches
Linux/systemd in the 120-second budget. This means the current login gap should
continue to be diagnosed with file-backed runtime logs for AP/Linux progress
and with GDB for targeted firmware/CPU snapshots, not by treating the
GDB-enabled wall time as representative runtime performance.

Additional current AP firmware snapshot from
`build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1/`:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop in the RSE runtime image

AP TF-A BL31:
  CPU#0 pc 0xc350 <pfdi_cpu_self_test_result+68>
  Backtrace:
    pfdi_cpu_self_test_result ->
    plat_pfdi_pe_init -> std_svc_setup ->
    runtime_svc_init -> bl31_main
  CPU#1 was in psci_pwrdown_cpu_end_terminal()

AP OP-TEE:
  CPU#0 pc 0xffc161f0 <pl011_putc+24>
  Backtrace:
    pl011_putc -> trace_ext_puts -> trace_vprintf ->
    trace_printf -> boot_mem_release_unused ->
    init_primary -> boot_init_primary_early -> _start

AP/Linux:
  The Linux GDB script attaches to the AP GDB target, but the sampled PC is
  still secure-world firmware; Linux has not started in this GDB sample.
```

The accompanying secure console log reaches:

```text
PFDI: OoR tests on core 1 succeeded.
PFDI: OoR tests on core 2 succeeded.
PFDI: OoR tests on core 3 succeeded.
SPM Core setup done.
BL31: Initializing BL32
OP-TEE version: 4.7.0-73-g4936f0556-dev
Primary CPU initializing
```

The quiet-console runtime with a patched copy of
`baremetal-image-fvp-rd-aspen.wic` reached RSE AP power-on and AP BL31, then
timed out before login. Its large copied WIC was removed to recover disk space;
the preserved evidence is in
`build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1-slim/`
and includes `summary.txt`, `result.json`, UART logs, and patched `boot.conf`.

The current host-GDB sample in
`build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1/` records
`host_gdb_sample_backtrace_captured: True` and captures `platforms-vp`,
RPC server/client, QEMU iothread, call_rcu, worker, and `CPU 0..3/TCG`
threads. AP CPU worker frames include `QemuCpu::wait_for_work()` and
`QemuCpu::prepare_run_cpu()` through `cpu_arm_cortexA720AE.so`.

### 2026-05-24 Current GDB Short-Tail Update

Two short GDB bundles now capture both the firmware progress point and the
later Linux progress point with the current AP-enabled default environment:

| Check | Result | Command |
| --- | --- | --- |
| 75-second all-target snapshot | pass, captures RSE runtime WFE, AP BL31 PFDI, SCP/SI symbols, and QBox host backtrace | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 135s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-target-short-20260524-v1 --launch --sample-only --sample-delay 75 --runner-timeout 105 --port-timeout 10 --gdb-timeout 8 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| 112-second AP/Linux tail snapshot | pass, Linux GDB script resolves CPU#0 to `pl011_putc+32`, and primary UART shows early initcall plus 4 CPU bring-up | `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 155s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-current-ap-linux-tail-20260524-v1 --launch --sample-only --sample-delay 112 --runner-timeout 125 --port-timeout 10 --gdb-timeout 8 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |

Key current 75-second state:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop in the RSE runtime image

AP TF-A BL31:
  CPU#0 pc 0xc30c <pfdi_cpu_self_test_result>
  Backtrace:
    pfdi_cpu_self_test_result ->
    plat_pfdi_pe_init -> std_svc_setup ->
    runtime_svc_init -> bl31_main

QBox host:
  host_gdb_sample_backtrace_captured: True
  captures platforms-vp, SystemC sc_start, RPC server/client,
  QEMU iothread, call_rcu, worker, and AP CPU TCG threads
```

Key current 112-second Linux state:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop after AP handoff

AP/Linux:
  CPU#0 pc 0xffff80008090a368 <pl011_putc+32>
  Backtrace:
    pl011_putc -> uart_console_write

Primary UART:
  Linux entered early initcall processing, brought up CPU1-CPU3, and
  activated all 4 CPUs before the probe ended.
```

SCP-Firmware remains symbol/source-only in these bundles because the current
QBox RSE path uses the service-model SCP endpoint and does not instantiate a
live SCP CPU GDB port. The generated `gdb/scp-firmware-symbols.gdb` script
loads `rdaspen-si0-bl2.elf` and resolves its entry point to `0x120000000`.
The copied raw flash/disk/SRAM files from the two bundles were removed after
the GDB scripts, probe logs, UART logs, `debug-env.json`, and
`progress-report.md` were captured.

### 2026-05-24 Current All-Layer GDB Debug Bundle

Artifact:

- `build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260524-v1/`

Command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 112 \
  --runner-timeout 130 \
  --port-timeout 10 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 3 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

| Target | Evidence |
| --- | --- |
| QBox host | `host_gdb_sample_backtrace_captured: True`; host GDB captured `platforms-vp`, SystemC `sc_start`, RPC server/client, QEMU iothreads, `call_rcu`, worker, and AP CPU TCG threads. |
| TF-M/RSE | `probes/tfm-later.txt` captures PC `0x31063480`, a `wfe` loop in the RSE runtime image after AP handoff. |
| SCP-Firmware | `probes/scp-symbols.txt` loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; live SCP CPU GDB is not available with current `service-model` SCP strategy. |
| AP/Linux | `probes/linux-later.txt` resolves CPU#0 to `cpu_do_idle+8`, CPU#1 to `__slab_alloc.isra.0`, and CPU#2/3 to `cpu_do_idle`. |
| Primary UART | `run/qbox-primary-console.log` reaches SCMI Linux probe, rootfs mount, `/sbin/init`, `systemd 257.4`, EWAOL welcome banner, and hostname setup. |

The RSE UART still stops after:

```text
[INF] BL2: RSE to SCP SCMI power on AP succeeded.
[INF] Bootloader chainload address offset: 0x27000
[INF] Image version: v2.2.2
[INF] Jumping to the first image slot
```

The FVP-only RSE runtime measured-boot and SCMI Comms subscription markers are
still absent from QBox RSE UART. The next fidelity gap remains RSE runtime
SCMI/measurement behavior, not AP/Linux bring-up. The helper-terminated
sampling run does not preserve `run/result.json`; the durable evidence is
`progress-report.md`, `debug-env.json`, `gdb/`, `probes/`, `run/qbox-*.log`,
`run/mhuv3-trace.log`, and `host-gdb-run/qbox-platform.log`. Reproducible raw
flash/disk/SRAM copies from this bundle were removed after capture.

### 2026-05-24 CPU0 SECCTRL And TF-M Runtime GDB Evidence

The all-layer GDB probe originally reached PC `0x31063480`, but without
`tfm_s.elf` symbols that address was only visible as an anonymous WFE loop.
The same probe captured a precise RSE BusFault:

```text
CFSR = 0x00008200
HFSR = 0x40000000
BFAR = 0x50011000
```

Source mapping identifies `0x50011000` as `CPU0_SECCTRL_BASE_S` from TF-M
`platform_base_address.h`, and the stacked PC maps to `sau_and_idau_cfg()`.
QBox now exposes the CPU0 security, power-control, and identity register
windows, plus RSE SIC and VM/SIC MPC SIE identification fields. The VM0, VM1,
and SIC MPC windows seed `BLK_MAX`, `BLK_CFG`, and `PIDR0 = 0x65` so TF-M's
SIE MPC driver recognizes SIE300-like programming state.

| Evidence | Result |
| --- | --- |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after keeping the new register windows inline to avoid the Lua 200-local limit. |
| `build/qbox-fvp-rd-aspen/gdb-setup-regenerated-20260524-v3/` | GDB bundle regenerated; `gdb/tfm-s.gdb` and README attach commands now cover the TF-M runtime image and use `--no-copy-writable-flash` for debug-only setup. |
| `build/qbox-fvp-rd-aspen/gdb-runtime-cpu0secctrl-20260524-v1/` | Default-DMI-off sample proves the previous `CPU0_SECCTRL_BASE_S` BusFault is no longer the first blocker; the sampled RSE path is back in the BL2 Strata CFI read loop, AP remains at TF-A BL2 entry, and QBox host GDB captures SystemC/QEMU threads. |
| `build/qbox-fvp-rd-aspen/gdb-runtime-fast-after-cpu0secctrl-20260524-v1/` | Fast-DMI sample proves AP/Linux GDB resolves CPU#0 to `cpu_do_idle+8`, and primary UART reaches SCMI probe, rootfs mount, `/sbin/init`, `systemd 257.4`, EWAOL welcome, and hostname setup. |
| TF-M runtime GDB | `probes/tfm-s-later.txt` resolves PC `0x31063480` to `tfm_hal_system_halt+2`; backtrace is `tfm_hal_system_halt()` -> `tfm_core_panic()` -> `main()` at `secure_fw/spm/core/main.c:122`. Fault registers are all zero. |
| SCP-Firmware GDB | `probes/scp-symbols.txt` still loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; live SCP CPU GDB remains unavailable with the current service-model SCP strategy. |

The active RSE runtime blocker is therefore no longer the `0x50011000`
precise BusFault. It is now a clean TF-M SPM panic after `tfm_core_init()`
returns a non-success value (`r0 = 0xffffff03` at the halt sample). The next
debug split should step or instrument `tfm_core_init()` stages such as platform
HAL init, static boundary setup, service list loading, and isolation hardware
setup.

### 2026-05-24 TF-M Static-Boundary And Core-Init Split

The GDB helper now generates targeted TF-M branch-trace scripts for
static-boundary setup and `tfm_core_init()` in addition to QBox host,
TF-M/RSE current-PC, AP/Linux, SCP-Firmware symbol, and SI CL1 symbol probes.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-static-boundary-trace-20260524-v1/` | First split captured VM0/VM1 MPC reset values shifted one word early: `0x50083010 = 0x7`, `0x50083014 = 0x0`, and `0x50083fe0 = 0x0`, so TF-M's SIE MPC driver saw an unsupported hardware version. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | VM0/VM1 MPC and SIC MPC `load.data` keys were shifted so `BLK_MAX`, `BLK_CFG`, and `PIDR0` land at TF-M-visible offsets `+0x10`, `+0x14`, and `+0xfe0`. |
| `build/qbox-fvp-rd-aspen/gdb-static-boundary-success-after-mpc-load-fix-20260524-v1/` | Static-boundary trace reaches `TRACE mpc_init_cfg shared-return success pc=0x10000296` and `SUCCESS static-boundary return pc=0x100005da`; VM0 and VM1 expose `BLK_MAX = 0x1`, `BLK_CFG = 0x7`, and `PIDR0 = 0x65`. |
| `build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-mpc-load-fix-20260524-v1/` | After static-boundary setup succeeds, `tfm_core_init()` fails at `FAIL tfm_hal_platform_init dma-init branch pc=0x100006a2`. |
| `tools/qbox/systemc-components/dma350/include/dma350.h` | DMA350 now exposes TF-M-expected `DMA_INFO.IIDR = 0x3a00043b` at offset `0xfc8` and `DMA_INFO.AIDR = 0x00000000` at offset `0xfcc`. |
| `tools/qbox/tests/components/dma350/dma350-tests.cc` | Component coverage checks the new DMA350 reset identification registers. |
| `build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-dma-iidr-fix-20260524-v1/` | `tfm-core-init-trace.gdb` reaches `SUCCESS tfm_core_init common-return pc=0x10000048`; this supersedes the earlier `tfm_core_init()` non-success evidence. |
| `build/qbox-fvp-rd-aspen/gdb-host-and-live-sample-after-dma-iidr-fix-20260524-v1/` | QBox host GDB still captures SystemC/QEMU threads, TF-M/RSE and AP ports are reachable, SCP-Firmware symbols load at entry `0x120000000`, and the short AP sample is at AP BL2 entry because the sample delay is intentionally only 8 seconds. |

Current conclusion: TF-M now passes static-boundary setup, RSE platform HAL DMA
initialization, and the full `tfm_core_init()` common return. The next RSE
runtime blocker is a later secure partition panic:

```text
#0  tfm_hal_system_halt()
#1  tfm_spm_partition_psa_panic()
#2  tfm_arch_thread_fn_call(...)
```

SCP-Firmware remains symbol/source-only in QBox because the active RSE path
uses `scp-strategy=service-model`; live SCP CPU GDB requires replacing or
augmenting that strategy with an executable SCP CPU model. AP/Linux GDB
inspection is already available through the AP CPU0 GDB port. Use
`gdb-runtime-fast-after-cpu0secctrl-20260524-v1/` or a later sample delay for
Linux `cpu_do_idle` and systemd evidence; the after-DMA host sample is
deliberately early and catches AP TF-A BL2 entry.

### 2026-05-24 TF-M ITS/PS GDB Split And Boot-Flash DMI Update

The post-`tfm_core_init()` partition panic was split with targeted GDB scripts
for secure partition attribution, ITS initialization, and Protected Storage
initialization. This updates the current RSE blocker and the safe debug
environment:

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Generates and can run `tfm-partition-panic-trace.gdb`, `tfm-its-init-trace.gdb`, and `tfm-ps-init-trace.gdb` in addition to QBox host, TF-M current/runtime, AP firmware/Linux, SCP-Firmware symbol, and SI CL1 symbol scripts. |
| `build/qbox-fvp-rd-aspen/gdb-partition-panic-trace-20260524-v1/` | First partition panic was attributed to `TFM_SP_ITS`: `p_curr_thrd = 0x3101a114`, `pid = 0x101`, entry `0x31047cc5`, which maps to `tfm_its_entry` in `tfm_its_req_mngr.c:151`. |
| TF-M Strata source inspection | The generated `cfi_strataflashj3_erase()` path erases by programming `0xff` bytes rather than issuing a hardware block-erase command, so RD-Aspen RSE boot flash needs the compatibility erase behavior exposed as `program_ff_sets_bits=true`. |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | Adds `program_ff_sets_bits` while preserving default NOR `old & data` byte-program semantics for other users. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds focused coverage that optional `0xff` byte programming can restore bytes to erased state. |
| `build/qbox-fvp-rd-aspen/gdb-its-init-step-trace-strata-ff-compat-20260524-v5/` | With `QBOX_RDASPEN_BOOT_FLASH_DMI=true`, ITS still fails: initial `its_flash_fs_prepare()` returns `0xffffff7c`, and the wipe/status path returns `0xffffff6e`. Platform logs show reads but no useful flash command-write side effects. |
| `build/qbox-fvp-rd-aspen/rse-no-bootflash-dmi-its-probe-20260524-v1/` | With boot-flash DMI left disabled, ITS panic is removed and runtime progresses into later TF-M services. RSE UART reaches CC3XX init, measured boot extension logs, SCMI shared-memory initialization, PS encryption selection, and then a PS partition failure. |
| `build/qbox-fvp-rd-aspen/gdb-ps-init-trace-no-bootflash-dmi-20260524-v1/` | `tfm-ps-init-trace.gdb` hits `tfm_ps_init()`: `ps_system_wipe_all()` returns `0x0`, but both `ps_system_prepare()` calls return `0xffffff7c` (`PSA_ERROR_GENERIC_ERROR`), followed by `psa_panic` from `tfm_sp_ps_stack`. |
| AP/Linux GDB in the same bundle | AP GDB port is reachable and AP TF-A/OP-TEE/U-Boot/Linux scripts attach, but the sample is still secure-world/early firmware rather than Linux kernel execution. |
| SCP-Firmware GDB in the same bundle | SCP-Firmware symbols/source load at entry `0x120000000`; live SCP stepping remains unavailable while `scp-strategy=service-model` is active. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed. |
| `git -C tools/qbox diff --check` | Passed. |
| `cmake --build tools/qbox/build --target strata_flash_j3-tests platforms-vp --parallel 4` | Passed. |
| `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed. |

Safe storage-debug command shape:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_TRACE=true \
QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=2000 \
timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-ps-init-trace-<run-id> \
  --launch \
  --sample-only \
  --tfm-ps-init-trace \
  --runner-timeout 100 \
  --trace-timeout 130 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --ignore-fail-patterns
```

Current conclusion: boot-flash DMI is not safe for TF-M storage/partition
debugging and should remain disabled until command-state DMI invalidation and
write semantics are proven. The current TF-M runtime blocker is no longer ITS
flash erase/status. It is Protected Storage `ps_system_prepare()` returning
`PSA_ERROR_GENERIC_ERROR` after a successful wipe. The next investigation
should trace `ps_object_table_init()` and its crypto/key path, especially the
PS encryption setup and the earlier built-in key loader warning.

### 2026-05-24 SCMI Subscribe And NS Mailbox GDB Split

After the Protected Storage sector-erase fix, the next FVP/QBox log gap was
the RSE runtime marker `SCMI Comms subscribed to power state notifications`.
The TF-M source path is
`tfm-extras/partitions/scmi/scmi_comms.c`: TF-M sends System Power protocol
`0x12`, message `0x5` (`SYS_POWER_STATE_NOTIFY`) with a single
`notify_enable` word and expects a status-only success response.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | The System Power responder now reports `PROTOCOL_MESSAGE_ATTRIBUTES` support for `SYS_POWER_STATE_SET` and `SYS_POWER_STATE_NOTIFY`, and returns success for the notify subscription request. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Focused coverage now sends System Power `message_attributes(0x5)` and `state_notify(0x5)` through the shared-memory SCMI transport and checks status-only success. |
| `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 4` | Passed. |
| `ctest --test-dir tools/qbox/build -R mhuv3_stub --output-on-failure` | Passed. |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 4` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-ap-scmi-subscribe-20260524-v1/` | AP-enabled short runtime reached RSE measured boot through `RT_0`, AP secure measured-boot markers, SMMUv3/PFDI/virtio markers, and Linux remoteproc attach, but timed out before login and still lacked the RSE subscription UART line. |
| `build/qbox-fvp-rd-aspen/gdb-all-targets-after-scmi-patch-20260524-v1/` | GDB sample captured QBox host, TF-M/RSE, AP/Linux, TF-A, U-Boot, SCP-Firmware symbols, and SI CL1 symbols. TF-M was halted in `tfm_hal_system_halt+2`; AP/Linux and host-GDB probes remained reachable. |
| `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-scmi-notify-20260524-v2/run/mhuv3-trace.log` | The QBox MHU trace proves the subscribe request was accepted: `header=0x4805 protocol=0x12 msg=0x5`, `event=scmi-sys-power-state-notify notify_enable=1`, and `status=0x0 length=8`. |
| `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-scmi-notify-20260524-v2/probes/tfm-partition-panic-trace.txt` | The post-subscribe TF-M halt is a BusFault attributed to `TFM_NS_MAILBOX_AGENT`: `pid=0x106`, `entry=0x31045a0d`, `stack_size=0x1000`, `irqs=2`. The backtrace is `tfm_hal_system_halt()` -> `tfm_core_panic()` -> `C_BusFault_Handler()` -> `BusFault_Handler()`. |

Current conclusion: the SCMI subscription response model is no longer the
blocking gap. QBox returns the expected success response, but TF-M faults in
the NS mailbox agent before the successful subscription log is printed on the
RSE UART. The next implementation step is to model or correct the AP-RSE
mailbox/MMIO/interrupt path used by `ns_agent_mailbox_entry()` and its
`MAILBOX_IRQ` / `MAILBOX_IRQ_2` signals.

### 2026-05-24 RSE Local MHU And NS Mailbox GDB Progress

The next GDB split narrowed the `TFM_NS_MAILBOX_AGENT` BusFault to the local
MHUv3 driver initialization path, before IRQ enable or `psa_wait()`:

```text
#2  mhu_v3_x_driver_init(dev=0x3101999c <MHU0_SENDER_DEV_S>)
#4  mhu_init_sender(MHU0_SENDER_DEV_S)
#6  sfcp_hal_init()
#7  sfcp_init()
#10 ns_agent_mailbox_entry()
BFAR = 0x50160fcc
stacked pc = 0x3104c5b8 <mhu_v3_x_driver_init+16>
```

`0x50160fcc` is `MHU0_SENDER_BASE_S + CTRL_AIDR` from the TF-M CSS-Aspen
platform map. QBox previously exposed the host AP-RSE MHU frames at host
physical `0x300001b600000`, but it did not expose the RSE-local secure MHU0
and MHU2 frames at `0x50160000/0x50170000` and
`0x501a0000/0x501b0000`. The platform now maps these four local MHUv3 frames
with the existing `mhuv3_stub` component and separate local pairs so existing
host-side `ap_rse` pairing is not overwritten.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-trace-20260524-v1/probes/tfm-ns-mailbox-trace.txt` | Proved the first fault was `BFAR=0x50160fcc`, `CFSR=0x00008200`, in `mhu_v3_x_driver_init()` reading `CTRL_AIDR`. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Adds RSE-local secure MHU0/MHU2 sender and receiver frames at the TF-M-visible addresses. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after keeping the new address constants out of Lua's 200-local limit. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `git -C tools/qbox diff --check` | Passed. |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 4` | Passed. |
| `./scripts/validate_qbox_fvp_rd_aspen_map.py` | Passed and wrote `build/qbox-fvp-rd-aspen/map-validation.json`. |
| `build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-local-mhu-20260524-v1/` | The focused NS mailbox trace no longer reaches a fault handler; it times out after 105 seconds, while later TF-M sampling shows `__tfm_arch_thread_fn_call_veneer()` -> `psa_wait_thread_fn_call()`. |
| AP/Linux in the same bundle | `probes/linux-later.txt` resolves all four AP CPUs to the `cpu_do_idle()` path, and `run/qbox-primary-console.log` reaches `fvp-rd-aspen login:`. |
| RSE local MHU trace | `run/mhuv3-trace.log` records `platform.rse_mhu2_receiver_s` doorbell signals on the new `rse_ap_secure_local` pair, proving the new local frame is active. |
| `build/qbox-fvp-rd-aspen/gdb-host-sample-20260524-v1/` | Host-GDB sampling captures `platforms-vp`, SystemC `sc_start()`, RPC server/client threads, QEMU iothreads, `call_rcu`, workers, and AP CPU TCG threads without relying on ptrace attach. |
| SCP-Firmware GDB | `probes/scp-symbols.txt` continues to load `rdaspen-si0-bl2.elf` and resolve entry `0x120000000`; live SCP CPU stepping is still unavailable with `scp-strategy=service-model`. |

Current conclusion: the first NS mailbox initialization BusFault is fixed.
This is not yet a complete AP-RSE mailbox implementation. The RSE UART still
lacks the FVP marker `SCMI Comms subscribed to power state notifications`, and
the local RSE MHU frames are not yet functionally bridged to the host AP-RSE
request/response semantics. The next fidelity task is to connect the RSE
local MHU0/MHU2 model to the AP-visible MHU window and shared mailbox protocol
instead of treating the local sender/receiver as independent doorbell frames.

### 2026-05-24 AP-RSE Bridge/IRQ And Runtime Marker Closure

The secure AP-RSE mailbox path is now wired as two directional MHU bridge
pairs: AP secure PBX to RSE MHU2 receiver (`ap_s_to_rse`) and RSE MHU2 sender
to AP secure MBX (`rse_to_ap_s`). The RSE NVIC fan-out was expanded to the
TF-M-visible interrupt range and the relevant receiver frames are routed to
the generated CSS-Aspen IRQ numbers: CMU MHU0 receiver IRQ 41, CMU MHU2
receiver IRQ 45, and SI CL0-to-RSE receiver IRQ 139.

| Evidence | Result |
| --- | --- |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | AP/RSE secure MHU pairs are directional bridge pairs, RSE receiver IRQs route to TF-M IRQ 41/45/139, and `rse_cpu_pass` exposes 160 target signal sockets for the RSE NVIC. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Component coverage verifies AP-to-RSE and RSE-to-AP doorbell forwarding plus receiver clear propagation back to sender PBX status. |
| `build/qbox-fvp-rd-aspen/gdb-rse-mhu-irq-map-20260524-v1/run/mhuv3-trace.log` | AP writes reach `platform.rse_mhu2_receiver_s`, TF-M clears the receiver, and `platform.rse_mhu2_sender_s` signals the AP-visible secure mailbox. |
| `build/qbox-fvp-rd-aspen/gdb-rse-mhu-irq-map-20260524-v1/run/qbox-rse.log` | RSE runtime reaches `MeasuredBoot: ... RT_0`, `SCMI Comms subscribed to power state notifications`, and measurements for `FW_CONFIG`, `SECURE_RT_EL3`, `SECURE_RT_EL1_SPMD`, and `BL_33`. |
| `build/qbox-fvp-rd-aspen/rse-current-runtime-markers-postlogin-20260524-v1/result.json` | Current short-timeout run records all non-Linux marker groups true, including RSE boot, RSE/SCP handoff, and measured boot through `BL_33`; it times out at U-Boot before Linux login because the timeout was capped at 160 seconds. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | `result.json` now includes `scp_service_model`, explicitly recording the service-model strategy, endpoint fidelity, live-SCP-GDB availability, and remaining real-SCP execution gaps. |
| `build/qbox-fvp-rd-aspen/rse-post-login-threaded-input-20260524-v3/` | Separate login-focused evidence still proves Linux login/root prompt and post-login probe command completion with zero return codes for `arm_si_rproc`, `rpmsg_ns`, `virtio_rpmsg_bus`, and `rpmsg_net`. |

Current conclusion: T019BJ is closed for the TF-M NS mailbox initialization and
runtime subscription path, and T060 measured-boot marker validation is closed.
The remaining Safety Island fidelity gap is not the RSE runtime marker path;
it is the lack of a real SI CL1 runtime/RPMsg peer that proves a Linux-visible
`ethsi1` RPMsg channel beyond module-load and remoteproc-attach evidence.

### 2026-05-24 Current Short All-Target GDB Recheck

A current short all-target GDB probe was run with a 28-second sample delay and
90-second outer timeout to verify that the reusable debug environment is still
usable without waiting for full Linux login.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-current-short-all-targets-20260524-v1/` | Generated the per-run README, `debug-env.json`, GDB command scripts, probe logs, QBox runner logs, and host-GDB wrapper logs. |
| `debug-env.json` | `rse_port_listening`, `ap_port_listening`, TF-M, AP/Linux, TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 Zephyr symbol probes all completed with return code 0. |
| `probes/tfm-later.txt` | RSE/TF-M is live and sampled in TF-M BL2 at `memset+42`, clearing memory from the boot path. |
| `probes/ap-tfa-bl2-later.txt` | AP CPU0 is live and sampled at TF-A BL2 `bl2_entrypoint`; the Linux symbol script also attaches to the same AP GDB target but this early sample has not reached the kernel yet. |
| `probes/scp-symbols.txt` | SCP-Firmware symbols and source maps load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP CPU stepping remains unavailable in current `service-model` mode. |
| host GDB sample | QBox host/SystemC/QEMU thread backtraces were captured by launching `platforms-vp` under GDB; this avoids Linux `ptrace_scope` attach restrictions. |

Current conclusion: the GDB environment covers QBox host, TF-M/RSE, AP
firmware/Linux targets, SCP-Firmware symbols, and SI CL1 Zephyr symbols. The
SCP limitation is explicit and expected: the current QBox RSE configuration
uses a protocol service model, so there is no live SCP CPU GDB target until a
real SI CL0/SCP execution model is added.

### 2026-05-25 Secure Services / Protected Storage GDB Split

The AP boot path currently reaches U-Boot and stops before Linux while U-Boot
initializes authenticated UEFI variables through the SMM Gateway FF-A secure
partition. Local Zena documentation confirms this is the expected first-boot
path: U-Boot calls SMM Gateway, SMM Gateway calls SE-Proxy, and SE-Proxy
forwards the Protected Storage request to RSE over MHUv3. The visible
`Logging service discovery failed` and first-boot `secure_storage_ipc_remove`
errors are documented as non-fatal for this release, so GDB was used to trace
the next active request instead of treating those lines as blockers.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-sp-symbol-sample-20260525-v1/ap-smmgw-symbol-probe.txt` | AP CPU0 is inside the SE-Proxy secure partition, not Linux. The stack is `mhu_v3_x_doorbell_read()` -> `mhu_wait_data()` -> `rse_comms_platform_invoke()` -> `secure_storage_ipc_set()`, with `client_id=32774`, `uid=8`, `data_length=156`, and `create_flags=0`. |
| `build/qbox-fvp-rd-aspen/gdb-sp-symbol-sample-20260525-v1/run/mhuv3-trace.log` | AP-to-RSE Protected Storage transactions are actively flowing. The short run ended with the last request `0x80062401` lacking a response only because the runner timeout cut the sample shortly after the request; earlier storage writes take up to about 4.1 simulated seconds to respond. |
| `build/qbox-fvp-rd-aspen/gdb-rse-ap-secure-storage-hang-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is not halted in a panic. It is in `CMU_MHU2_Receiver_Handler()` -> `sfcp_interrupt_handler()` -> `mhu_receive_message()` -> `mhu_v3_x_doorbell_read()` while receiving AP transaction `0x80061501`. |
| `build/qbox-fvp-rd-aspen/gdb-rse-ap-secure-storage-hang-20260525-v1/run/mhuv3-trace.log` | The sampled request is a larger Protected Storage transfer: channel 0 length `0x3c`, transaction `0x80061501`, handle `0x40000101`, type/parameter word `0x30003e9`, UID word `0x8`, and data length word `0x368`. The sample intentionally terminated before the response. |
| `build/qbox-fvp-rd-aspen/gdb-rse-ap-secure-storage-hang-20260525-v1/probes/ap-secure-services-static-resolve.txt` | The AP PC `0x4005dcbc`, with SE-Proxy load base parsed from the secure console (`0x40033000 + .text 0x20`), resolves to `mhu_v3_x_doorbell_read+216` in `se-proxy_46bb39d1-b4d9-45b5-88ff-040027dab249`. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | The reusable GDB helper now records TS SP symbol paths and, during `--launch`, parses per-run OP-TEE secure-console load bases to generate `probes/ap-secure-services-later.gdb` / `.txt` for SE-Proxy and SMM Gateway. |
| `build/qbox-fvp-rd-aspen/gdb-setup-secure-sp-20260525-v1/` | Dry-run GDB bundle generation includes `ts_se_proxy`, `ts_smm_gateway`, their source maps, and README instructions for per-run AP secure partition symbol resolution. |

Current conclusion: the sampled point is no longer an unknown AP/Linux gap.
QBox has progressed into the U-Boot authenticated-variable provisioning path,
and both sides of the AP-RSE secure-service exchange are live. The next
runtime check should let the storage-safe path continue past the current
sample point and only classify a blocker if the same transaction remains
without a response after a short bounded wait beyond the observed 4-second
storage-write latency.

### 2026-05-25 Login/Post-Login And All-Target GDB Check

A bounded storage-safe runtime was allowed to continue past the earlier
SE-Proxy Protected Storage sample. It reached Linux login and completed the
post-login probe. A follow-up GDB bundle used the same writable flash and
post-login path while keeping the target attachable long enough to sample
QBox host, TF-M/RSE, AP/Linux, AP firmware symbol views, TS secure partitions,
SCP-Firmware symbols, and SI CL1 Zephyr symbols.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1/result.json` | `passed=true`, blocker `none`, RSE boot/SCP handoff/measured-boot markers true through `BL_33`, and Linux markers true for `fvp-rd-aspen login:` plus `root@fvp-rd-aspen`. |
| `build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1/qbox-primary-console.log` | Linux reaches multi-user mode, the FIFO post-login probe runs, `arm_si_rproc`, `rpmsg_ns`, `virtio_rpmsg_bus`, `rpmsg_net`, and `ethsi1` checks return 0, and `ethsi1` is `UP,LOWER_UP`. |
| `build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1/qbox-secure-console.log` | The earlier TS path still reports SE-Proxy panic/SMMGW busy and failed PK reads, but those no longer block AP Linux boot in this bounded run. This remains a secure-service fidelity gap, not a boot blocker. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `--keep-running-after-pass`, a debug-only option that keeps QBox attachable after the normal pass condition or post-login probe completion. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--post-login-probe`, `--keep-running-after-pass`, and `--copy-writable-flash` pass-throughs so GDB sessions can use the same writable-flash/login path as runtime validation. |
| `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/progress-report.md` | RSE/TF-M and AP/Linux GDB ports are reachable; QBox host backtraces were captured through the host-GDB launch path; SCP-Firmware and SI CL1 Zephyr symbol scripts load. |
| `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/probes/linux-later.txt` | AP/Linux CPU0 resolves to `d_alloc_parallel+336`; AP CPUs 1-3 resolve to `cpu_do_idle()`. |
| `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/probes/tfm-s-later.txt` | RSE runtime resolves to `__tfm_arch_thread_fn_call_veneer()` and `psa_wait_thread_fn_call()` on `idle_sp_stack`. |
| `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/run/post-login-probe-actions.log` | The main GDB run sent login attempts and the post-login probe; `complete=true`. |
| `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/run/qbox-primary-console.log` | Post-login console evidence includes `systemctl is-system-running` returning `running`, `systemctl --failed` listing zero units, interrupt evidence for GICv3/PL011/SMMUv3/virtio/RTC/MHU, and module evidence for `rpmsg_*` and `pfdi_misc`. |

Current conclusion: the previous secure-storage sample was a timeout artifact,
not a persistent hang. The QBox RSE-oriented path now reaches Linux login and
post-login driver evidence with storage-safe settings. The reusable GDB
environment covers all requested inspectable layers. The one explicit
limitation remains SCP-Firmware: the current path uses a SystemC service
model, so SCP-Firmware can be inspected with symbols/source but not live-stepped
until a real SCP CPU is modeled.

### 2026-05-25 V004 Full RSE Runtime Pass

V004 was rerun with build enabled, storage-safe boot-flash DMI disabled, AP
CPUs enabled, ATU/host-memory/RSE TCM/VM DMI enabled, MHU tracing enabled, and
the file-backed post-login probe enabled.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/summary.txt` | `passed: True`, blocker `none`, boot mode `rse-oriented`, SCP strategy `service-model`. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/result.json` | RSE boot, RSE/SCP handoff, measured boot through `BL_33`, and Linux login marker groups are all true. Fail patterns for kernel panic, missing rootfs/init, `[ERR]`, and `[ERROR]` are false. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/post-login-probe-actions.log` | The FIFO probe completed and `result.json` records successful return codes for `arm_si_rproc`, `rpmsg_ns`, `virtio_rpmsg_bus`, `rpmsg_net`, and `ethsi1`. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/qbox-primary-console.log` | Linux reaches multi-user mode, remoteproc attaches `si-cl1`, `virtio_rpmsg_bus` creates `ethsi1`, `ip link show ethsi1` returns 0, and the post-login probe reaches `__QBOX_PROBE_DONE__`. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/qbox-rse.log` | TF-M/RSE reaches BL1_1/BL1_2/BL2, SI CL0/CL1 loading, RSE-to-SCP SCMI AP power-on, runtime TF-M chainload, SCMI subscription, and measured-boot markers through `BL_33`. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/qbox-secure-console.log` | Secure-world continues to report SE-Proxy panic/SMM Gateway busy and PK-read failures. These remain secure-service fidelity gaps, but they do not block Linux boot in this run. |

Current conclusion: the full V004-style runtime no longer depends only on a
skip-build shortcut or a GDB helper. It rebuilds the QBox targets, boots the
RSE-oriented path to Linux, and collects driver evidence through the same
file-backed probe path. FVP-vs-QBox comparison V007 remains open.

### 2026-05-25 V007 FVP/QBox Log Comparison And V008 Direct Boot

The FVP side was rerun with the non-interactive, file-backed FVP helper and
short bounded timeout. The comparison helper was corrected to use the actual
RSE runtime ordering seen in both FVP and QBox:
`Starting TF-M BL1_1` -> `Init SCMI comm to SCP succeeded` ->
`RSE to SCP SCMI power on AP succeeded` -> `Jumping to the first image slot`
-> `SCMI Comms subscribed to power state notifications`.

| Evidence | Result |
| --- | --- |
| `build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1/summary.txt` | FVP verbose run passed in 249.492 seconds. It captured RSE, primary Linux, secure-world, SCP/SI CL0, and SI CL1 logs. |
| `build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1/result.json` | Required FVP console checks passed: RSE `Jumping to the first image slot` and AP power-on, primary Linux login, secure-world session close, SCP/SI CL0 module initialization and SSU, and SI CL1 secondary CPU evidence. |
| `scripts/compare_fvp_qbox_rse_logs.py` | Ordered marker list now matches the actual FVP/QBox runtime sequence, where `Jumping to the first image slot` is the runtime TF-M chainload point after RSE-to-SCP/AP power-on. |
| `build/qbox-fvp-rd-aspen/rse-v007-fvp-qbox-compare-20260525-v1/comparison.json` | `passed=true`; QBox has no missing markers from the FVP-observed RSE boot, RSE/SCP handoff, measured boot, or Linux marker groups, and `qbox_order_ok=true`. |
| `build/qbox-fvp-rd-aspen/direct-v008-primary-compute-20260525-v1/result.json` | Direct primary-compute boot remains available: `passed=true`, duration 27.914 seconds, `probe_complete=true`, Linux login/root prompt true, no kernel/rootfs/init failure patterns, and all tracked driver patterns true. |

Current conclusion: V004, V006, V007, and V008 are now evidence-backed. This
does not close the remaining fidelity work: secure services still report
SE-Proxy/SMM Gateway errors, SCP-Firmware is still symbol-only under the
service-model strategy, and real SI CL1/Zephyr packet data-plane fidelity is
not yet proven.

### 2026-05-25 T083 RSE Fidelity Coverage Audit

The primary-compute coverage audit now consumes RSE-oriented `result.json`
files. For RSE runs, it verifies the expected `fidelity_labels` key set,
reports missing and unexpected labels, records remaining debt labels, and
summarizes RSE marker groups. Direct primary-compute runs still pass with the
RSE audit marked skipped.

| Evidence | Result |
| --- | --- |
| `scripts/audit_qbox_fvp_rd_aspen_coverage.py` | Adds `rse_fidelity_audit`, `rse_fidelity_labels_passed`, expected RSE label checks, debt-label reporting, and RSE marker-group summary. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/coverage-audit.json` | `implemented_blocks_passed=true`, `rse_fidelity_labels_passed=true`, `missing_labels=[]`, and all RSE marker groups true. Debt labels remain explicit: `mhuv3=temporary-stub`, `rse_sacfg=static-map-only`, and `rse_nsacfg=static-map-only`. |
| `build/qbox-fvp-rd-aspen/direct-v008-primary-compute-20260525-v1/coverage-audit.json` | Direct primary-compute audit still passes; `rse_fidelity_audit.present=false` with reason `runtime_result_is_not_rse_oriented`. |
| `python3 -m py_compile scripts/audit_qbox_fvp_rd_aspen_coverage.py` | Passed. |

Current conclusion: T083 is closed for label-level RSE coverage accounting.
The audit intentionally records current fidelity debt rather than hiding it;
this is not a claim that MHUv3, SACFG, NSACFG, SCP execution, or secure
services are fully FVP-equivalent.

### 2026-05-25 Boot Media Task Reconciliation

The V004 runtime artifact and current RSE Lua configuration prove several
earlier boot-media tasks that were still listed as open.

| Task | Evidence |
| --- | --- |
| T020 read-only ROM | `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` loads `rse_rom` into `gs_memory` with `read_only = true`, `shared_memory = true`, and `load = {bin_file = rse_rom, offset = 0}`. V004 records the same deploy ROM path in `input_artifacts.rse_rom` and `runtime_artifacts.rse_rom`. |
| T021 per-run writable flash | `scripts/run_qbox_fvp_rd_aspen_rse.py` copies RSE/AP flash into each run's `writable-images/` directory and decompresses gzip deploy images into per-run raw images. V004 records `copied_writable_artifacts.rse_flash`, `copied_writable_artifacts.ap_flash`, and `flash_image_preparation.state = gzip_decompressed_for_qbox_raw_memory`. Cross-reboot persistence remains T076. |
| T023 provisioning bundle load | `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` loads `combined_provisioning_message.bin` into `rse_vm1` at `RSE_PROVISIONING_OFFSET = 0x00020000`; V004 records the bundle path in both input and runtime artifacts. |

Current conclusion: T020, T021, and T023 are closed. T022 was still open at
this reconciliation point and is closed by the focused OTP/NVM evidence below.
T024 and T025 are addressed by the focused evidence below.

### 2026-05-25 T024 RSE Parameterization

The FVP configuration in
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`
sets `css.smb.rseil.VMADDRWIDTH=18`,
`css.smb.rseil.RESET_SYNDROME_INIT_VAL=0x80000000`,
`css.smb.hold_rse_cpu_in_reset=1`, and
`css.smb.rseil.rse.sys_ctrl_regs.DMA_BOOT_EN_REG_RESET=1`.
The QBox RSE platform now exposes the matching runtime knobs while preserving
those defaults.

| Evidence | Result |
| --- | --- |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Adds `QBOX_RDASPEN_RSE_VMADDRWIDTH`, `QBOX_RDASPEN_RSE_RESET_SYNDROME`, `QBOX_RDASPEN_RSE_CPUWAIT`, `QBOX_RDASPEN_RSE_DMA_BOOT_EN`, and `QBOX_RDASPEN_RSE_DMA_BOOT_ADDR`. `VMADDRWIDTH=18` derives `RSE_VM_SIZE=0x40000` and keeps VM1 at `0x31040000`. |
| `tools/qbox/tests/components/rse_sysctrl/rse_sysctrl-tests.cc` | Adds CCI preset coverage proving `reset_syndrome`, `cpuwait`, `dma_boot_en`, and `dma_boot_addr` override the reset register values. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after keeping new values out of Lua 5.1's top-level local-variable limit. |
| `ctest --test-dir tools/qbox/build -R '^rse_sysctrl-tests$' --output-on-failure` | Passed. |
| `cmake --build tools/qbox/build --target rse_sysctrl rse_sysctrl-tests --parallel 8` | Passed. |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-t024-params-smoke-20260525-v3/qbox-platform.log` | Short smoke loads the Lua platform, prints `rse vmaddrwidth: 18` and `rse vm size: 0x40000`, reaches `SC_START`, and has no Lua syntax error. |
| `build/qbox-fvp-rd-aspen/rse-t024-params-smoke-20260525-v3/result.json` | Bounded 10-second smoke times out as expected, but has no first failing register access and reaches early RSE markers: `Starting TF-M BL1_1`, `BL1_2`, and `BL2`. |

Current conclusion: T024 is closed for QBox/FVP default parameter parity and
override coverage. T022 is closed by the later OTP/NVM write-lock evidence.

### 2026-05-25 T025 Boot-Media Unit Tests

Dedicated unit tests now cover the boot-media loading paths that were already
used by the RSE Lua platform and runtime runner.

| Evidence | Result |
| --- | --- |
| `tools/qbox/tests/components/memory/memory-tests.cc` | Adds `RseRomLoadIsReadableAndRejectsWrites`, proving loaded ROM bytes are readable and writes are rejected when `read_only` is set. Adds `RseProvisioningBundleLoadsAtConfiguredOffset`, proving the loader places provisioning bytes at a configured memory offset. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds `RseBootFlashLoaderPathLoadsImageBytes`, proving the `strata_flash_j3` loader path used by Lua `load = {bin_file = ...}` populates the flash array at an RSE boot-flash offset. |
| `tools/qbox/tests/components/rse_lcm/rse_lcm-tests.cc` | Adds `OtpImageParameterLoadsOtpWindow`, proving the `otp_image` CCI parameter loads file bytes into the LCM OTP window. |
| `cmake --build tools/qbox/build --target memory-tests strata_flash_j3-tests rse_lcm-tests --parallel 8` | Passed. |
| `ctest --test-dir tools/qbox/build -R '^(memory-tests\|strata_flash_j3-tests\|rse_lcm-tests)$' --output-on-failure` | Passed: all three focused test binaries passed. |

Current conclusion: T025 is closed for unit-level loading coverage. The later
T022 evidence closes OTP/NVM lock-after-provision and per-run persistent write
semantics.

### 2026-05-25 T022 OTP/NVM Writeback And Lock

The RSE LCM model now treats the TF-M-visible OTP window as an OTP/NVM window
instead of generic writable registers. Writes to `LCM_BASE_S + 0x1000` update
the in-memory OTP image, optionally flush the full configured OTP window back
to the active `otp_image`, and become ignored after the secure-provisioning
`SP_ENABLE` magic when `otp_lock_after_provision` is enabled. The runner only
enables OTP writeback for per-run copied writable OTP images, so deploy
artifacts are not modified by normal validation runs.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/rse_lcm/include/rse_lcm.h` | Adds OTP-window write routing, `otp_writeback`, `otp_lock_after_provision`, per-run file flush, and lock-after-secure-provisioning behavior. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Wires `QBOX_RDASPEN_RSE_OTP_WRITEBACK` and `QBOX_RDASPEN_RSE_OTP_LOCK_AFTER_PROVISION` into `rse_lcm_regs`. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Sets `QBOX_RDASPEN_RSE_OTP_WRITEBACK=true` for copied writable OTP runs and `false` when `--no-copy-writable-flash` uses deploy images directly. |
| `ctest --test-dir tools/qbox/build -R '^rse_lcm-tests$' --output-on-failure` | Passed. The focused tests cover OTP image loading, file writeback, and lock-after-provision behavior. |
| `build/qbox-fvp-rd-aspen/rse-t022-otp-check-20260525-v1/result.json` | Check-only preparation created per-run writable RSE/AP flash and RSE OTP images; the expected blocker is `check_only_no_runtime` because QBox is intentionally not launched. |
| `build/qbox-fvp-rd-aspen/rse-t022-otp-runtime-20260525-v1/result.json` | Expected short timeout after RSE runtime chainload; fail patterns are false, RSE boot/SCP handoff markers are true, and measured boot reaches `BL_33`. |
| OTP copy comparison | Deploy OTP SHA-256 is `6a022c3d...`; runtime copied OTP SHA-256 is `eee2e53b...`. The only byte differences are offsets `0x29a1`, `0x2a01`, and `0x2a61`, proving writeback affected the per-run copy. |

Current conclusion: T022 is closed for the modeled TF-M provisioning path:
read/write, per-run file-backed persistence, and lock-after-provision are
implemented and tested. Cross-reboot flash/OTP persistence remains tracked by
T076, and fuller LCM lifecycle/DCU/error semantics remain fidelity debt.

### 2026-05-25 T040-T042 MHUv3 Frame Split

The MHUv3 compatibility component now separates low-level PBX/MBX frame
register behavior from the higher-level SCMI, reset, direct-boot, and RPMsg
service-model hooks. The Lua-visible component remains `mhuv3_stub` for
platform compatibility, but the register-frame state is reusable and directly
unit-tested without instantiating a full SystemC component.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | Adds public `mhuv3_stub::mhuv3_frame_model`, which owns PBX/MBX register storage, channel decode, status/mask/control state, feature/ID registers, and combined interrupt status calculation. The wrapper keeps the SCMI, reset, direct-boot, and RPMsg behavior. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Adds `Mhuv3FrameModelTest.PbxAndMbxDoorbellRegistersAreReusable`, covering configured PBX feature/ID registers, status, interrupt status, interrupt enable, combined interrupt summary, MBX default masking, mask clear, and receiver clear behavior. |
| `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 4` | Passed. |
| `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` | Passed. |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 4` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-t040-mhu-frame-refactor-20260525-v2/result.json` | Expected short timeout with no fail patterns. RSE boot and RSE/SCP handoff markers are true, SCMI subscription is reached, and measured boot reaches `BL_33`. |

Current conclusion: T040-T042 are closed for the reusable PBX/MBX frame split.
This is not yet a claim of full Arm MHUv3 TRM equivalence. Secure-service
semantics, PFDI/AP-SI SCMI traffic, real SCP execution, and real SI CL1/Zephyr
packet data-plane behavior remain tracked as follow-up fidelity work.

### 2026-05-25 T065 Secure-Service Post-Login Probe

The RSE runner now has an opt-in `--secure-service-probe` mode layered on top
of the FIFO-backed Linux post-login probe. It keeps the normal boot pass
criteria unchanged, but records Trusted Services userspace-test binary
presence, bounded per-command return codes, a secure-service completion marker,
and secure-console failure classification in `result.json`.

| Evidence | Result |
| --- | --- |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `--secure-service-probe` and `--secure-service-probe-timeout`. When enabled, the runner checks `uefi-test`, `psa-iat-api-test`, `psa-its-api-test`, `psa-ps-api-test`, and `ts-service-test`, then runs bounded `ts-service-test -lg`, Initial Attestation, ITS, PS, and UEFI test commands. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/result.json` | Base RSE-oriented boot passed with Linux login/root prompt, all RSE boot/SCP/measured-boot markers true, post-login driver probes true, and no fail patterns. The secure-service probe completed and set `secure_service_probe.done_marker=true`. |
| Secure-service binary presence | `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` are present (`*_present_rc:0`). `ts-service-test` and `uefi-test` are absent from the current rootfs (`*_present_rc:1`, attempted execution rc 127). |
| Secure-service bounded command results | `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` each hit the 12-second command timeout (`rc:124`). |
| Secure-console failure classification | `observed_failures` records `se_proxy_error=true`, `smm_gateway_error=true`, and `uefi_variable_error=true`; raw logs include SE-Proxy PSA-call failures, SP busy responses, SMM Gateway PK-read failures, and U-Boot EFI variable enrollment failures. |

Current conclusion: T065 is closed because QBox now has repeatable,
file-backed post-login probes for secure-service userspace tests. T062, T063,
and T064 remain open: the probe proves the current failure modes instead of
claiming the secure services pass.

### 2026-05-25 T061-T064 Secure-Service Diagnostic Probe

A follow-up secure-service diagnostic run used the same post-login path with a
shorter per-command timeout and captured Linux FF-A/TEE discovery state before
running the PSA tests. This separates Linux device discovery from the remaining
SE-Proxy/RSE service-response failure.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-t061-secure-service-diag-20260525-v1/result.json` | Base RSE-oriented boot passed with Linux login/root prompt, all RSE boot/SCP/measured-boot markers true, post-login driver probes true, `passed=true`, `timed_out=false`, and `blocker=null`. |
| secure-service diagnostic marker | `secure_service_probe.diag_done_marker=true`; the diagnostic block ran before the bounded userspace tests. |
| Linux FF-A/TEE device discovery | `/dev/tee0`, `/dev/teepriv0`, `/sys/bus/arm_ffa/devices`, and `/sys/bus/tee/devices` all exist. FF-A devices `arm-ffa-1` through `arm-ffa-6` are visible; `arm-ffa-4` has SMM Gateway UUID `ed32d533-99e6-4209-9cc0-2d72cdd998a7`, while `arm-ffa-6` reports the zero UUID and its kernel probe returns 19. |
| kernel driver evidence | `qbox-primary-console.log` records OP-TEE revision 4.7, `optee: initialized driver`, `probe of arm-ffa-1 returned 0`, `probe of arm-ffa-5 returned 0`, and `probe of arm-ffa-6 returned 19`; `tstee_driver_init` still returns 0. |
| rootfs test binaries | `psa-iat-api-test`, `psa-its-api-test`, `psa-ps-api-test`, and `psa-crypto-api-test` are present. `ts-service-test` and `uefi-test` are absent from the current rootfs and return 127 when attempted. |
| PSA userspace tests | `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` each time out at the 6-second command cap with rc 124 after `libpsats` reports `Failed to open rpc session`. |
| secure-console failures | OP-TEE loads SE-Proxy SP UUID `46bb39d1-b4d9-45b5-88ff-040027dab249` and SMM Gateway SP UUID `ed32d533-99e6-4209-9cc0-2d72cdd998a7`, but secure logs still show SE-Proxy PSA-call failures, repeated `SP is busy`, SMM Gateway `sp_msg_send_direct_req(): error -4`, failed service discovery, and repeated `Failed to read PK`. |
| Arm reference expectation | `arm-zena-css/documentation/user_guide/reproduce.rst` documents `psa-ps-api-test`, `psa-its-api-test`, and `psa-iat-api-test` as Primary Compute tests that should complete with pass summaries on the reference platform. `arm-zena-css/documentation/design/secure_services.rst` describes the expected normal-world `libts`/`libpsats` to secure-world SP FF-A path and the SE-Proxy SP to RSE MHUv3 path. |

Current conclusion: Linux-side FF-A/TEE discovery is no longer the primary
unknown. The remaining T061-T063 blocker is the AP secure-world
SE-Proxy/libpsats RPC path to RSE services: the PSA binaries are present but
cannot open an RPC session before the bounded timeout. T064 has two distinct
gaps: current rootfs content lacks `uefi-test`, and SMM Gateway still fails
secure variable reads through the same busy SP/direct-request path.

### 2026-05-25 T061-T064 MHU Trace And FVP PSA Split

The secure-service diagnostic was rerun with MHU tracing enabled and a short
per-command userspace timeout. This checks whether the QBox failure is still a
doorbell bridge loss or has moved above the AP-RSE MHU transport.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-t061-secure-service-mhu-20260525-v1/result.json` | Base boot, Linux login, post-login driver probe, and secure-service diagnostic block completed: `passed=true`, `timed_out=false`, `blocker=null`, `secure_service_probe.diag_done_marker=true`, and `secure_service_probe.done_marker=true`. |
| `build/qbox-fvp-rd-aspen/rse-t061-secure-service-mhu-20260525-v1/mhuv3-analysis.txt` | `scripts/analyze_qbox_mhu_trace.py` paired AP secure-service request doorbells on `ap_s_to_rse` channel 1 with RSE responses on `rse_to_ap_s` channel 1. Requests/responses are `39/39`, `paired=39`, `missing=0`; the last request `0x80062701` is answered at line 13687 with latency `3387848373` ns. |
| QBox secure console delta | QBox still reports `E/SEPROXY: psa_fwu_query:62 failed to psa_call: -135`, an SE-Proxy SP panic with `0xdeadbeef`, a user-mode data abort at address `0x8`, repeated SMM Gateway direct-request failures, and repeated `Failed to read PK`. |
| QBox userspace delta | The PSA IAT/ITS/PS binaries are present, but each command times out after `libpsats` reports `Failed to open rpc session`. |
| FVP short PSA reference | `scripts/runfvp_log_boot.py` now supports repeated `--post-login-command` entries for file-backed FVP probes. `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/` ran FVP with `--runfvp-verbose`; IAT and ITS completed with rc 0 and pass summaries, while `uefi-test` was absent from the same rootfs. |
| FVP PS reference | `build/fvp-boot-logs/rse-secure-service-ps-probe-20260525-v1/` ran a PS-only FVP post-login probe. The command opened the RPC path and progressed through PS test 409 before the host-side post-login cap ended the run; it did not reproduce QBox's immediate RPC-session-open failure. |

Current conclusion: the AP-RSE secure MHU doorbell bridge is not the remaining
T061-T063 loss point in this trace. The next implementation split should focus
on the AP secure partition/FF-A RPC/session path and the SE-Proxy panic/data
abort state. The FVP baseline can show non-fatal early SMM Gateway discovery
errors, but it does not show the QBox SE-Proxy panic or userspace
`Failed to open rpc session` behavior for the IAT/ITS checks.

### 2026-05-25 Current GDB All-Target Smoke

A short, file-backed GDB smoke was run to confirm that the active debug
environment can inspect QBox host state, RSE/TF-M, AP firmware/Linux, and
SCP-Firmware symbol state without relying on tmux screen output.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v2/` | Fresh bounded recheck generated per-run README, `debug-env.json`, GDB command scripts, probe logs, QBox runner logs, and host-GDB wrapper logs. |
| Fresh GDB launch command | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 80 --port-timeout 5 --gdb-timeout 5 --sample-delay 65 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| Fresh `debug-env.json` probe result | RSE GDB port `12340` and AP/Linux GDB port `12341` opened; `tfm_later_probe_rc`, `tfm_s_later_probe_rc`, `linux_later_probe_rc`, AP firmware probes, `scp_symbol_probe_rc`, and `si_cl1_symbol_probe_rc` all returned 0; `host_gdb_sample_backtrace_captured=true`. |
| Fresh TF-M/RSE progress | `probes/tfm-later.txt` maps PC `0x3102849e` to TF-M BL2 `cc3xx_lowlevel_pka_and()` under `bootutil_img_validate()` and `boot_load_and_validate_images()`. The RSE UART had reached AP BL2 post-load, RSE-to-SCP SCMI power-on, and TF-M runtime image slot output. |
| Fresh AP/Linux progress | AP CPU0 is still at TF-A BL2 entry PC `0x82000`; the Linux symbol script attaches to the AP GDB target, but this short sample has not reached the kernel. |
| `build/qbox-fvp-rd-aspen/gdb-current-all-targets-20260525-v1/` | Generated per-run README, `debug-env.json`, GDB command scripts, probe logs, QBox runner logs, and host-GDB wrapper logs. |
| GDB launch command | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true timeout 140s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --sample-delay 35 --runner-timeout 80 --port-timeout 8 --gdb-timeout 6 --host-sample --host-sample-seconds 2 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-targets-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| `debug-env.json` probe result | RSE GDB port `12340` and AP/Linux GDB port `12341` opened; `tfm_later_probe_rc`, `tfm_s_later_probe_rc`, `linux_later_probe_rc`, AP firmware probes, `scp_symbol_probe_rc`, and `si_cl1_symbol_probe_rc` all returned 0; `host_gdb_sample_backtrace_captured=true`. |
| TF-M/RSE progress | `probes/tfm-later.txt` maps PC `0x3101d160` to TF-M BL2 `memset()` called by `clear_safety_island_memory()` for the SI CL0 SRAM window at `0x753a6000`. |
| AP/Linux progress | `probes/ap-tfa-bl2-later.txt` maps AP CPU0 PC `0x82000` to TF-A BL2 `bl2_entrypoint`; the Linux symbol script attaches to the AP GDB target, but this short sample has not reached the kernel. |
| SCP-Firmware progress | `probes/scp-symbols.txt` loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; live SCP CPU stepping remains unavailable with the current `scp-strategy=service-model`. |
| QBox host progress | Host GDB captured `platforms-vp`, SystemC `SC_START`, QEMU iothread/call_rcu threads, and AP CPU TCG threads through the host-GDB launch path. |

Current conclusion: the reusable GDB environment is operational for QBox host,
TF-M/RSE, and AP firmware/Linux inspection. SCP-Firmware debugging is limited
to source/symbol inspection until a real SCP CPU target replaces or augments
the current service model.

### 2026-05-25 User-Requested Short GDB Recheck

A follow-up short-timeout GDB run was executed to verify that the debug bundle
still supports QBox host, TF-M/RSE, AP firmware/Linux, SCP-Firmware, and SI CL1
inspection without tmux screen output.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1/` | Generated `README.md`, `debug-env.json`, `progress-report.md`, `gdb/*.gdb`, probe logs, runner logs, and host-GDB wrapper logs. |
| Launch command | `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 80 --port-timeout 5 --gdb-timeout 5 --sample-delay 45 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` |
| `debug-env.json` probe result | RSE/TF-M GDB port `12340` and AP/Linux GDB port `12341` opened; TF-M, AP/Linux, AP TF-A BL2/BL31, AP OP-TEE, AP U-Boot, SCP-Firmware symbol, and SI CL1 Zephyr symbol probes returned 0; host-GDB backtrace capture is true. |
| TF-M/RSE progress | `probes/tfm-later.txt` maps PC `0x31024c9c` to TF-M BL2 `nor_cfi_reg_read()` in `platform/ext/target/arm/drivers/flash/cfi/cfi_drv.c:54`. The RSE UART log had reached SI CL1/SI CL0 image load, SI ATU programming, RSE-to-SCP SCMI initialization, and AP BL2 slot reporting. |
| AP/Linux progress | AP CPU0 remains at TF-A BL2 entry PC `0x82000`; `probes/ap-tfa-bl2-later.txt` resolves it to `bl2_entrypoint`. The Linux script attaches to the AP GDB target, but this short sample has not reached the kernel. |
| QBox host progress | Host-GDB launch captured `platforms-vp`, SystemC `SC_START`, QEMU iothread/call_rcu threads, and AP CPU TCG threads. `host_gdb_sample_rc=1` is expected for the bounded interrupt/kill sample; `host_gdb_sample_backtrace_captured=true` is the pass criterion. |
| SCP-Firmware progress | `probes/scp-symbols.txt` loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; live SCP stepping remains unavailable while `scp-strategy=service-model` is active. |

Current conclusion: the requested GDB environment is ready for log-backed
inspection of QBox host, TF-M/RSE, and AP firmware/Linux. SCP-Firmware is
covered by symbol/source inspection today; live SCP GDB remains a real-SCP CPU
model task, not a missing GDB-script task.

### 2026-05-25 T061-T064 FWU/PS GDB Split

The GDB helper was extended with a focused `--tfm-fwu-query-trace` path and
secure-service probe pass-through so the same short, file-backed run can trace
early FWU query handling, later AP secure partition state, RSE/TF-M runtime
state, Linux/AP state, and MHUv3 request/response pairing.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--tfm-fwu-query-trace`, `--secure-service-probe`, and `--secure-service-probe-timeout`. Timed-out GDB probes now preserve partial stdout/stderr, and the FWU trace GDB script writes `probes/tfm-fwu-query-trace-gdb.log`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/progress-report.md` | RSE/TF-M port `12368` and AP/Linux port `12369` opened. TF-M initial, later, secure-runtime, AP/Linux, AP secure-service, AP TF-A/OP-TEE/U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned usable results; the FWU trace intentionally ended with rc 124 at the 120-second cap. |
| `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/probes/tfm-fwu-query-trace-gdb.log` | The focused trace hit `fwu_bootloader_init` at `pc=0x31044f90`; later FWU-query breakpoints did not fire before the short cap. |
| `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/probes/tfm-s-later.txt` | RSE/TF-M later state is in ITS flash writeback: `nor_send_cmd_byte()` -> `nor_byte_program()` -> `cfi_strataflashj3_program()` -> `its_flash_fs_dblock_compact_block()` -> `its_flash_fs_delete_idx()` -> `tfm_its_remove()` -> `tfm_internal_trusted_storage_service_sfn()`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/probes/ap-secure-services-later.txt` | AP SE-Proxy is waiting for an RSE Protected Storage SET response: `mhu_v3_x_doorbell_read()` -> `rse_comms_platform_invoke()` -> `__psa_call(... handle=1073742081, type=1001 ...)` -> `secure_storage_ipc_set(... data_length=655 ...)`. Handle `1073742081` is `0x40000101`, the TF-M Protected Storage service handle. |
| `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/mhuv3-analysis.txt` | AP secure-service requests/responses on channel 1 are `13/12`, paired `12`, missing `1`. The only missing request at the bounded sample point is `0x80060d01`, matching the in-flight AP SE-Proxy wait rather than a broad AP-RSE MHU bridge loss. |
| `build/qbox-fvp-rd-aspen/gdb-t061-host-sample-20260525-v1/host-gdb-run/qbox-platform.log` | The supported QBox host path launches `platforms-vp` under GDB and captures `SystemC : SC_START`, `sc_core::sc_start()`, RPC server/client threads, QEMU iothread/call_rcu threads, and AP CPU TCG threads. Direct host attach remains blocked by host ptrace/ioctl policy. |

Current conclusion: the secure-service gap is now narrowed to the AP secure
partition / TF-M SFCP / ITS-PS storage path. The v4 sample does not support a
claim that secure services pass, but it also does not point to a simple AP-RSE
doorbell bridge failure. SCP-Firmware remains symbol/source-only until the
service-model SCP strategy is replaced or augmented with a live SCP CPU model.

### 2026-05-25 T061 MHU Pair Isolation And Post-Fix GDB State

The FWU/SFCP trace was extended to inspect pointer-access deserialization and
ATU allocation. It found that the first SE-Proxy FWU query failed before ATU
allocation because a named MHU pair could fall back to the last global PBX/MBX
peer and pollute the AP-to-RSE channel status. The MHU model now allows global
fallback only for the legacy empty-pair case.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-t061-sfcp-atu-trace-20260525-v1/probes/tfm-fwu-query-trace-gdb.log` | `sfcp_protocol_pointer_access_deserialize_msg()` was hit with `msg_len=0x39` and returned `0xffffff79` (`-135`) before `comms_atu_alloc_region()` was reached. The captured words showed the request body was one byte longer than expected, matching the previous `psa_fwu_query: -135` symptom. |
| `build/qbox-fvp-rd-aspen/gdb-t061-sfcp-atu-trace-20260525-v1/run/mhuv3-trace.log` | The AP-SI/PFDI monitor PBX with pair `ap_si_pfdi_monitor` signaled the AP-to-RSE MBX pair `ap_s_to_rse` through the old global fallback, leaving channel 0 status polluted before the FWU request. |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | Named PBX/MBX lookup now returns no peer when a non-empty `pair` has no exact match. Only the legacy empty-pair configuration can use the global fallback. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Adds regression coverage proving an unpaired named PBX does not signal an unrelated MBX through the global fallback. |
| `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 8` and `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` | Passed after the MHU named-pair isolation fix. |
| `build/qbox-fvp-rd-aspen/rse-t061-mhu-pair-fix-20260525-v1/` | Short runtime no longer reports `E/SEPROXY: psa_fwu_query:62 failed to psa_call: -135`. It reaches U-Boot and later secure-service errors instead: SMM Gateway `sp_msg_send_direct_req(): error -4` and SE-Proxy `secure_storage_ipc_remove` PSA-call `-140`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/progress-report.md` | RSE/TF-M port `12382` and AP/Linux port `12383` opened; TF-M, AP/Linux, AP TF-A BL2/BL31, AP OP-TEE, AP U-Boot, SCP-Firmware symbol, and SI CL1 Zephyr symbol probes returned 0. |
| `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is in the ITS flash delete path: `nor_send_cmd_byte()` -> `cfi_strataflashj3_erase()` -> `its_flash_fs_file_delete()` -> `tfm_its_remove()`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/probes/ap-secure-services-later.txt` | AP SE-Proxy is waiting on RSE in `mhu_v3_x_doorbell_read()` below `secure_storage_ipc_set(uid=8, data_length=156)`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/run/mhuv3-analysis.txt` | AP secure-service channel-1 requests/responses are `17/16`, paired `16`, missing `1`; the only missing request is timeout-truncated in-flight transaction `0x80061101`. |
| `build/qbox-fvp-rd-aspen/gdb-user-linux-marker-current-20260525-v1/progress-report.md` | A user-requested short marker-gated run waited 120.038 seconds for `Linux version`; the marker was not reached, but RSE/TF-M, AP/Linux target, AP secure-service symbols, AP TF-A/OP-TEE/U-Boot symbol views, SCP-Firmware symbols, and SI CL1 symbol probes all returned 0. |
| `build/qbox-fvp-rd-aspen/gdb-user-linux-marker-current-20260525-v1/probes/ap-secure-services-later.txt` | At the 120-second cap AP CPU0 is in SE-Proxy `mhu_v3_x_doorbell_read()` below `secure_storage_ipc_set(client_id=32774, uid=7, data_length=2)`, waiting for the RSE secure-storage response. |
| `build/qbox-fvp-rd-aspen/gdb-user-linux-marker-current-20260525-v1/probes/tfm-s-later.txt` | At the same cap RSE/TF-M is in `nor_send_cmd_byte()` -> `cfi_strataflashj3_erase()` -> `its_flash_nor_erase()` -> `tfm_its_remove()`, showing the current short-timeout delay is PS/ITS flash erase/writeback, not a missing GDB target. |

Current conclusion: the original early FWU query `-135` caused by MHU named-pair
cross-talk was a QBox MHU pair isolation bug and is fixed. Later secure-service
artifacts are separate evidence: post-login
`rse-t065-secure-service-probe-20260525-v1` again reports FWU discovery
`-135`, but GDB maps that recurrence to the Trusted Services FWU provider
panicking after `psa_fwu_m_update_agent_init()` returned a null update agent.
The remaining secure-service blocker is therefore above basic AP-to-RSE
doorbell routing, in the AP secure partition / TF-M SFCP / ITS-PS storage and
FWU discovery path. SCP-Firmware is still symbol/source-only under the current
service-model strategy.

### 2026-05-25 T061-T064 Marker-Gated Secure Variable GDB Samples

The GDB helper now supports UART-marker-gated sampling with an optional
post-marker delay. This avoids relying on tmux screen state or long blind
sleeps when inspecting U-Boot secure-variable enrollment and AP/RSE
secure-storage traffic.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--sample-marker`, `--sample-marker-log`, and `--sample-marker-post-delay`. The progress report records the marker, marker log, marker hit status, post-delay, and total wait time. |
| `scripts/analyze_qbox_mhu_trace.py` | `sc_time` parsing now recognizes `ns`, `us`, `ms`, and `s` units before pairing request/response doorbells. This prevents microsecond trace lines from being treated as zero-time events. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/analyze_qbox_mhu_trace.py` | Passed after the helper and analyzer updates. |
| `build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1/terminal_sec_uart_5003.log` | The reference FVP also prints SMM Gateway logging-service discovery errors (`sp_msg_send_direct_req(): error -4`) and early SE-Proxy `secure_storage_ipc_remove` PSA-call `-140` messages, so those two log patterns alone are not QBox-specific blockers. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/progress-report.md` | The `Error: "db" not defined` marker was found after 196.064 seconds. RSE/TF-M, AP/Linux target, AP secure-service symbols, AP TF-A/OP-TEE/U-Boot symbol views, SCP-Firmware symbols, and SI CL1 symbols all returned usable probe results. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/run/qbox-primary-console.log` | U-Boot enrolls PK and KEK successfully, then reaches `Error: "db" not defined` and reads the `db` payload. The run did not reach `db key is enrolled successfully!` before the bounded GDB sample stopped the platform. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is in SFCP pointer-access deserialization and ATU mapping: `sfcp_protocol_pointer_access_deserialize_msg()` -> `comms_atu_alloc_region()` -> `setup_region_for_host_buf()` -> `atu_rse_map_addr_automatically()` -> `atu_rse_set_bus_attributes()`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/probes/ap-secure-services-later.txt` | AP SE-Proxy is waiting in `mhu_v3_x_doorbell_read()` below `secure_storage_ipc_remove()` with PSA call type `1004`, i.e. an in-flight secure-storage REMOVE transaction. |
| marker-run MHU analysis | AP secure-service channel-1 requests/responses are `105/104`, paired `104`, missing `1`; the only missing request is the bounded in-flight transaction `0x80066901`. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-postdelay-20260525-v1/progress-report.md` | The post-delay option was exercised with `--sample-marker-post-delay 25`, but this particular bounded run did not reach the `db` marker before the 300.104-second sample cap. It still proved AP secure-service, AP firmware, SCP-Firmware, and SI CL1 symbol probes attach at the earlier U-Boot FWU regular-state point. |
| `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-postdelay-20260525-v1/run/mhuv3-trace.log` | AP secure-service channel-1 requests/responses are `70/69`, paired `69`, missing `1`; the only missing request is the bounded in-flight transaction `0x80064601`. |
| `build/qbox-fvp-rd-aspen/gdb-t064-ps-object-trace-20260525-v1/probes/tfm-ps-object-table-trace.txt` | A bounded PS object-table trace timed out at the 230-second cap after proving TF-M PS initialization, object-table authentication, HUK/key-derivation traffic, and `Driver_FLASH0_EraseSector` calls at RSE flash offsets such as `0x3107000` and `0x300b000..0x3012000`. The heavy breakpoint trace did not reach the later `db` variable path before the cap, so it is PS/flash-init evidence rather than a `db` completion result. |
| `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/progress-report.md` | A marker-gated run waited 260.085 seconds for `2023 bytes read`; the marker was not reached before the cap, but all RSE/TF-M, AP secure-service, AP firmware/Linux, SCP-Firmware symbol, and SI CL1 symbol probes attached successfully. |
| `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/probes/ap-secure-services-later.txt` | AP SE-Proxy was sampled in `secure_storage_ipc_get_info()` with PSA call type `1003`, handle `0x40000101`, uid `7`, and was waiting for the MHU sender clear in `signal_and_wait_for_clear()` / `mhu_v3_x_doorbell_read()`. |
| `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M was sampled in `CMU_MHU2_Receiver_Handler()` while `sfcp_hal_receive_message()` was receiving the AP secure-service message, specifically in `mhu_v3_x_get_num_channel_implemented()` for the MHU2 receiver. |
| `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/run/mhuv3-analysis.txt` | AP secure-service requests/responses are `27/26`, paired `26`, missing `1`; the only missing bounded transaction is `0x80061b01`. The request payload decodes as Protected Storage `GET_INFO` (`type=1003`, control `0x10103eb`) for uid pointer `0xfffe0000`, not as the later `db` payload read. |
| `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/qbox-primary-console.log` | A non-GDB, file-backed run reaches `PK key is enrolled successfully!`, `KEK key is enrolled successfully!`, `db key is enrolled successfully!`, `dbx key is enrolled successfully!`, and `FWU: ExitBootServices: Booting in regular state` before the short Linux-login timeout. This proves the U-Boot secure-variable enrollment path can complete when the run is not held for GDB sampling. |
| `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/progress-report.md` | A later marker-gated GDB run waited 340.108 seconds for `FWU: ExitBootServices: Booting in regular state` and did not reach the marker. All live target probes still succeeded: RSE/TF-M, TF-M runtime, AP/Linux target, AP secure-service symbols, AP TF-A/OP-TEE/U-Boot symbol views, SCP-Firmware symbols, and SI CL1 symbols. |
| `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/probes/ap-secure-services-later.txt` | The GDB sample resolves AP CPU0 to SE-Proxy `mhu_v3_x_doorbell_read()` below `secure_storage_ipc_get_info()`, with PSA call type `1003`, handle `0x40000101`, and uid `6`; CPU1-3 are halted at the reset/PSCI holding address. |
| `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is in the CMU_MHU2 receive interrupt path at `mhu_v3_x_get_num_channel_implemented()` while `sfcp_hal_receive_message()` receives the AP secure-service message. |
| `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/run/mhuv3-analysis.txt` | AP secure-service requests/responses are `22/21`, paired `21`, missing `1`; the missing bounded request is `0x80061601`, whose payload is another Protected Storage `GET_INFO` (`type=1003`, control `0x10103eb`) for pointer `0xfffe0000`. |

Current conclusion: FVP evidence shows the early SMM Gateway `-4` and
SE-Proxy remove `-140` logs can be normal first-boot noise, while QBox now
progresses past PK/KEK enrollment and, without GDB sampling, completes `db`
and `dbx` enrollment before the Linux handoff. The remaining T061/T063 gap is
therefore not basic U-Boot variable enrollment or AP-RSE MHU doorbell routing;
it is the higher-level secure-service validation path where SE-Proxy/SMM
Gateway userspace tests still time out or lack image content. For GDB, the
current bounded samples show live in-flight Protected Storage GET_INFO
transactions and confirm that all debug targets are usable, but GDB sampling
can slow the secure-variable path enough that the same `ExitBootServices`
marker is not reached within a short cap.

### 2026-05-25 T070A-T073A FWU Bank And Capsule Preflight

The new FWU inspection helper records the static RD-Aspen CFG2 firmware-update
layout before attempting the destructive capsule/reboot flow. It uses the local
TF-M-derived slot offsets and the generated deploy images, but it does not
modify the deploy artifacts.

| Evidence | Result |
| --- | --- |
| `scripts/inspect_qbox_fvp_rd_aspen_fwu.py` | Adds a file-backed FWU inspection helper for RSE flash, AP flash, RSE private metadata, AP FWU metadata, VirtIO block 1, capsule image, and capsule manifest. |
| `python3 -m py_compile scripts/inspect_qbox_fvp_rd_aspen_fwu.py` | Passed. |
| `build/qbox-fvp-rd-aspen/fwu-inspect-20260525-v2/fwu-inspection.json` | Records gzip-decompressed raw RSE flash size `67108864` and AP flash size `134217728`, matching the expected 64 MiB and 128 MiB media sizes. |
| FWU bank inventory | Records populated primary slots and zeroed secondary slots for BL2, RSE runtime, SI CL0, AP FIP, and SI CL1. RSE runtime, SI CL0, and SI CL1 primary slots parse as valid MCUBoot images; AP FIP primary parses as a valid FIP with 15 ToC entries. |
| Metadata inventory | RSE private metadata replica `0x5000` has `boot_index=0` and five READY-state component bytes; replica `0x6000` is all-zero READY. AP FWU metadata replicas at `0x5000` and `0x6000` parse as version 2 with `active_index=0`, `previous_active_index=1`, `num_banks=2`, and `num_images=5`. |
| Capsule input media | VirtIO block 1 contains a FAT root-directory `fw.cap` entry of size `4516232`, matching `efi-capsule-update-image.img.uefi.capsule`; the manifest contains the five non-dummy CFG2 FWU components `BL2`, `TFM_S`, `SCP-FW`, `FIP`, and `SI-CL1`. |

Current conclusion: T070A-T073A are closed as FWU preflight evidence. The full
T070-T076 tasks remain open because QBox has not yet applied the capsule,
rebooted into bank 1, observed `Attempting to boot image 1`, observed
`Booting with partition FIP_B`, or proved writable flash state persistence
across reboot.

### 2026-05-25 T073B FWU Runtime Probe And GDB Prelogin Sample

The RSE runner now has a file-backed `--fwu-probe` mode for the documented
RD-Aspen capsule-on-disk sequence. It waits for Linux login through the same
FIFO-backed primary UART mechanism, then mounts `/dev/vda1` and `/dev/vdb1`,
copies `/mnt/fw.cap` into `/boot/EFI/UpdateCapsule/`, requests reboot, and
records the FWU log markers needed for the full T073-T076 validation.

| Evidence | Result |
| --- | --- |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `--fwu-probe`, FWU command injection, FWU return-code capture, and `post_login_probe.fwu_probe` marker evaluation for `FWU: Updating`, capsule application, RSE image 1, TF-A `FIP_B`, trial state, and regular state. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `git -C tools/qbox diff --check` and `./scripts/validate_qbox_fvp_rd_aspen_map.py` | Passed before runtime sampling. |
| `build/qbox-fvp-rd-aspen/rse-t073-fwu-capsule-probe-20260525-v1/result.json` | Short runtime was manually stopped after the logs stayed unchanged for roughly 180 seconds. It records `blocker=qbox_fwu_probe_incomplete`, `platform_returncode=-15`, RSE boot markers true, RSE/SCP handoff true, measured-boot markers through `BL_33` true, and Linux login markers false. |
| `rse-t073-fwu-capsule-probe-20260525-v1/post-login-probe-actions.log` | `fwu_requested: True`, but no login was sent and no probe commands were sent because `qbox-primary-console.log` stayed empty. |
| `rse-t073-fwu-capsule-probe-20260525-v1/qbox-secure-console.log` | AP secure firmware reached BL31 PFDI initialization, OP-TEE initialization, and Secure Partition loading up to SE Proxy mapping. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-prelogin-short-20260525-v1/progress-report.md` | A short GDB sample regenerated the all-target debug bundle. RSE/TF-M and AP/Linux ports opened, SCP-Firmware and SI CL1 symbols loaded, and host GDB captured QBox/SystemC/QEMU threads. |
| `gdb-fwu-prelogin-short-20260525-v1/probes/tfm-s-later.txt` | TF-M runtime was sampled at `__tfm_arch_thread_fn_call_veneer` (`pc=0x31042820`), confirming the RSE/TF-M target is live past measured boot. |
| `gdb-fwu-prelogin-short-20260525-v1/probes/ap-tfa-bl31-later.txt` | AP CPU0 was in TF-A BL31 `pfdi_cpu_self_test_result()` under `plat_pfdi_pe_init()` and `runtime_svc_init()`, while CPU1 was in the PSCI powerdown path and CPU2/CPU3 were still at `0x82000`. |
| `gdb-fwu-prelogin-short-20260525-v1/probes/ap-optee-core-later.txt` | OP-TEE symbol view sampled CPU0 in `fdt_get_property_namelen_()` while walking the secure DT; this confirms the AP target had not reached Linux yet in the short sample. |
| `gdb-fwu-prelogin-short-20260525-v1/probes/linux-later.txt` | The Linux symbol script attached to the AP GDB target, but CPU0 was still in pre-Linux firmware code and the kernel had not started. |
| `gdb-fwu-prelogin-short-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load and resolve entry `0x120000000`; live SCP stepping remains unavailable with `scp-strategy=service-model`. |

Current conclusion: the FWU runtime probe infrastructure is in place, but this
short run did not reach Linux login, so no capsule handoff was triggered and no
T073-T076 success claim is made. The GDB sample shows the bounded progress
point before Linux as AP secure firmware, specifically TF-A BL31 PFDI and
OP-TEE secure-DT traversal, with RSE/TF-M still live and attachable.

### 2026-05-25 Current GDB Environment And Progress Samples

The current GDB setup was regenerated and then exercised with short,
file-backed runs that avoid tmux screen inspection. A separate rootfs copy,
per-run RSE/AP flash copies, and `QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2223-:22`
were used to avoid image locks and SSH host-forward collisions with other
QBox runs.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-current-setup-20260525-v1/debug-env.json` | Generated GDB scripts and source maps for QBox host, TF-M BL1_1/BL1_2/BL2/runtime, AP TF-A/OP-TEE/U-Boot/Linux, SCP-Firmware, and SI CL1 Zephyr. |
| `build/qbox-fvp-rd-aspen/gdb-current-short-20260525-v4/progress-report.md` | RSE/TF-M port `12340` and AP/Linux port `12341` opened. TF-M, AP/Linux, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, SI CL1 symbol, and QBox host probes all ran. |
| `gdb-current-short-20260525-v4/probes/tfm-s-later.txt` | TF-M runtime sampled in ITS flash erase: `nor_send_cmd_byte()` -> `cfi_strataflashj3_erase()` -> `Driver_FLASH0_EraseSector()` -> `its_flash_nor_erase()` -> `tfm_its_init()`. |
| `gdb-current-short-20260525-v4/probes/ap-tfa-bl2-later.txt` | AP CPU0 sampled before Linux in TF-A BL2 `mhu_v3_x_doorbell_read()`; CPU1-CPU3 remained halted at the BL2 entry/holding point. |
| `gdb-current-short-20260525-v4/host-gdb-run/qbox-platform.log` | Host GDB captured SystemC/QEMU threads including `sc_core::sc_start()`, QEMU iothread, TCG CPU threads, and `QemuCpu::wait_for_work()`. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-20260525-v1/progress-report.md` | Waited up to 240.076 seconds for `Linux version`; marker was not reached, but AP/Linux target, AP secure-service symbols, AP firmware views, SCP-Firmware symbols, and SI CL1 symbols remained attachable. |
| `gdb-linux-marker-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 resolved to SE-Proxy `mhu_v3_x_doorbell_read()` with `channel=127`, matching an in-flight secure-storage wait before Linux. |
| `gdb-linux-marker-20260525-v1/probes/linux-later.txt` | Linux GDB script attached to the AP target, but PC was still secure partition address `0x4006bc90`; this proves target wiring, not kernel execution. |
| `gdb-linux-marker-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load with entry `0x120000000`; live SCP stepping remains unavailable under `scp-strategy=service-model`. |

Current conclusion: the GDB environment is ready for QBox host, TF-M/RSE, AP
firmware/Linux target state, AP secure-service symbol state, and SCP-Firmware
symbol inspection. The latest bounded progress point before Linux is the
secure-world storage path around SE-Proxy/MHU and TF-M ITS/PS flash handling;
Linux kernel execution was not reached within the 240-second marker cap.

### 2026-05-25 AP Reset GPIO Bridge For FWU Reboot

The RSE platform now instantiates QBox `reset_gpio` for the AP QEMU instance
and fans its QEMU reset output into all modeled AP CPU reset sockets. This is
intended to make guest-triggered AP system reset observable on the SystemC side
before the remaining Secure FWU bank-1 validation.

| Evidence | Result |
| --- | --- |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Adds `ap_reset_gpio` with `args={"&platform.ap_qemu_inst"}` and `reset_out` bound to `ap_cpu_0.reset` through `ap_cpu_3.reset` when AP CPUs are enabled. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `reset_gpio` to the required QBox target list so fresh runs build the dynamic module used by the platform. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after keeping the new bind-list helper out of the Lua main chunk local-variable limit. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/analyze_qbox_mhu_trace.py scripts/inspect_qbox_fvp_rd_aspen_fwu.py` | Passed. |
| `git -C tools/qbox diff --check` and `./scripts/validate_qbox_fvp_rd_aspen_map.py` | Passed. |
| `timeout 120s cmake --build tools/qbox/build --target reset_gpio platforms-vp --parallel 4` | Passed. |
| `timeout 90s ctest --test-dir tools/qbox/build -R '^reset-test-system:sync-pol=multithread:num-cpu=4:icount=false:threading=MULTI:accel=tcg$' --output-on-failure` | Passed in 0.58 seconds, covering the same multithread/MULTI/4-CPU reset coordination class used by the AP side. |
| `build/qbox-fvp-rd-aspen/rse-t074-reset-gpio-fwu-short-20260525-v2/result.json` | Short FWU run with `QBOX_RDASPEN_ENABLE_AP_CPUS=true` reached RSE boot, RSE/SCP handoff, measured boot through `BL_33`, TF-A BL31, OP-TEE/SP loading, and U-Boot console, then timed out before Linux login. No FWU commands were sent, so T074-T076 remain open. |

Current conclusion: AP reset bridging is wired and its focused QBox reset test
passes. The latest short FWU run did not regress early boot, but it did not
reach Linux login within 260 seconds and therefore did not exercise the new
guest reboot path.

### 2026-05-25 FWU Reboot And GDB Current-State Recheck

A follow-up FWU run used the same RSE-oriented runner with AP CPUs enabled,
ATU/host-memory/RSE DMI acceleration, MHU trace enabled, post-login probes, and
the FWU capsule probe. This run reached Linux login and copied the capsule to
the EFI update directory, then requested Linux reboot. The bounded run still
timed out before any second-boot FWU bank marker.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-t074-reset-gpio-fwu-probe-20260525-v3/result.json` | `blocker=qbox_fwu_probe_incomplete_timeout`; RSE boot, RSE/SCP handoff, measured boot through `BL_33`, Linux login, and root shell markers are true. |
| `rse-t074-reset-gpio-fwu-probe-20260525-v3/result.json` | Post-login driver patterns for `arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`, and `virtio` are true. |
| `rse-t074-reset-gpio-fwu-probe-20260525-v3/result.json` | FWU capsule probe started, mounted `/dev/vda1` and `/dev/vdb1`, copied `/mnt/fw.cap` to `/boot/EFI/UpdateCapsule/fw.cap`, and emitted `__QBOX_FWU_REBOOT_REQUESTED__`; all recorded FWU command return codes are `0`. |
| `rse-t074-reset-gpio-fwu-probe-20260525-v3/qbox-primary-console.log` | Linux reached shutdown and printed `systemd-shutdown[1]: Rebooting.` plus virtio, MHU, SCMI, RTC, and remoteproc shutdown messages. |
| `rse-t074-reset-gpio-fwu-probe-20260525-v3/qbox-primary-console.log` and `result.json` | No `QEMU resetting`, `SystemC resetting`, `[INF] Attempting to boot image 1`, `Booting with partition FIP_B`, or FWU bank-1 completion marker was observed before the timeout. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-virtio-sample-20260525-v2/progress-report.md` | Regenerated the GDB debug bundle and ran a bounded `Filesystem: FAT16` marker sample. RSE/TF-M port `12340`, AP/Linux port `12341`, SCP-Firmware symbol view, SI CL1 symbol view, AP firmware views, AP secure-service view, and QBox host GDB sample all returned usable probe results. |
| `gdb-fwu-virtio-sample-20260525-v2/probes/tfm-s-later.txt` | TF-M runtime sampled in `tfm_arch_thread_fn_call()` under `psa_wait_thread_fn_call()`, showing TF-M is alive and waiting for PSA signals rather than faulting. |
| `gdb-fwu-virtio-sample-20260525-v2/probes/linux-later.txt` | The AP/Linux GDB port is attachable, but CPU0 is still in pre-Linux secure-world address space at `pc=0xfef5b8a4`; CPU1-CPU3 are halted at PSCI/reset-holding code. |
| `gdb-fwu-virtio-sample-20260525-v2/probes/ap-secure-services-later.txt` | SE-Proxy and SMM Gateway symbols were loaded at OP-TEE-reported bases, but sampled PC `0xfef5b8a4` did not resolve into either SP image. |
| `gdb-fwu-virtio-sample-20260525-v2/run/qbox-secure-console.log` | The sampled run reached U-Boot early FWU/EFI setup and OP-TEE secure partition startup, then emitted repeated `E/SEPROXY: secure_storage_ipc_remove:115 ipc_remove: failed to psa_call: -140`. |
| `gdb-fwu-virtio-sample-20260525-v2/host-gdb-run/qbox-platform.log` | Host GDB captured SystemC/QEMU threads including `SC_START`, QEMU iothread, TCG CPU threads, and `QemuCpu::wait_for_work()`. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-virtio-sample-20260525-v1/result.json` | A concurrent first GDB attempt failed immediately with `qbox_platform_failed:1` / `Failed to get "write" lock` because the FWU runtime was still active. The retry was run after the active QBox process exited. |

Current conclusion: the file-backed GDB environment covers QBox host, TF-M/RSE,
AP firmware/Linux, AP secure services, SCP-Firmware symbols, and SI CL1 symbols.
SCP-Firmware remains symbol/source-only because the current RSE path uses the
SystemC/TLM service-model SCP endpoint rather than a live SCP CPU GDB target.
The FWU path now reaches Linux, proves driver probe coverage, copies the
capsule, and requests reboot. The remaining blocker is after Linux shutdown:
the modeled AP/QEMU reset does not yet produce a second RSE/AP boot with image
1/FIP_B bank markers inside the bounded run.

### 2026-05-25 FWU Shutdown GDB Root-Cause Sample

The GDB helper now passes the runner `--fwu-probe` option so the same
file-backed debug bundle can drive the capsule-on-disk reboot sequence and then
sample TF-M/RSE, AP firmware/Linux, AP secure services, SCP-Firmware symbols,
and SI CL1 symbols at a marker in the Linux shutdown log.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--fwu-probe` pass-through. It implies `--post-login-probe`, records `fwu_probe` in `debug-env.json`, includes the option in generated README commands, and lets marker-gated GDB sampling run after the FWU capsule copy and Linux reboot request. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed after the helper update. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-sample-20260525-v1/progress-report.md` | Waited for `systemd-shutdown[1]: Rebooting.` and found it after 296.611 seconds. RSE/TF-M, AP/Linux, AP secure-service, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned 0. |
| `gdb-fwu-shutdown-sample-20260525-v1/run/qbox-primary-console.log` | Linux copied the capsule, emitted `__QBOX_FWU_REBOOT_REQUESTED__`, reached `systemd-shutdown[1]: Rebooting.`, shut down virtio, MHU, SCMI, remoteproc, SMMU, watchdog, UART, timer, DSU PMU, and printed `reboot: Restarting system`. |
| `gdb-fwu-shutdown-sample-20260525-v1/run/qbox-secure-console.log` | Immediately after the Linux reboot path, TF-A BL31 asserted at `plat/common/plat_gicv3.c:279` in the secure SGI type check. The secure-console backtrace includes `plat_ic_raise_el3_sgi`, `psci_stop_other_cores`, `css_scp_system_off`, `psci_system_reset`, `psci_smc_handler`, and `sync_exception_handler`. |
| `gdb-fwu-shutdown-sample-20260525-v1/probes/ap-tfa-bl31-later.txt` | AP CPU0 is in BL31 `plat_panic_handler` at `pc=0x5680`, with the backtrace `plat_panic_handler()` -> `__assert()`. CPU1-CPU3 are still in Linux `ipi_handler()` addresses. |
| `gdb-fwu-shutdown-sample-20260525-v1/probes/linux-later.txt` | The Linux view confirms CPU0 has left the kernel address range and is at `pc=0x5680`; CPU1-CPU3 remain at `ipi_handler()`. This proves Linux reached PSCI reset, not merely userspace shutdown. |
| `aarch64-poky-linux-addr2line -e .../bl31.elf 0x5f54 0x4238 0xcffc 0xfd78 0x8818 0xfe90 0xf9c0 0x124a4 0x5db8` | Decoded the secure-console backtrace to `backtrace`, `__assert`, `plat_ic_raise_el3_sgi`, `psci_stop_other_cores`, `css_scp_system_off`, `psci_system_reset`, `psci_smc_handler`, `std_svc_smc_handler`, and `sync_exception_handler`. |
| `gdb-fwu-shutdown-sample-20260525-v1/probes/tfm-s-later.txt` | TF-M/RSE remains alive in `__tfm_arch_thread_fn_call_veneer()` below `psa_wait_thread_fn_call()`, so the sampled failure is on the AP BL31 PSCI reset side rather than an RSE runtime crash. |
| `gdb-fwu-shutdown-sample-20260525-v1/run/qbox-platform.log` | No `QEMU resetting` or `SystemC resetting` line appears before the bounded helper terminates the platform. The AP reset GPIO bridge is therefore not reached because BL31 panics before the SCMI system-reset command can complete. |

Current conclusion: the previous "no QEMU reset observed" symptom is now
attributed to an AP TF-A BL31 panic in the graceful-reset SGI path. Linux does
reach PSCI `SYSTEM_RESET`; BL31 then tries to stop other cores via
`CSS_CPU_PWR_DOWN_REQ_INTR` / `ARM_IRQ_SEC_SGI_7`, but
`plat_ic_get_interrupt_type()` does not report that SGI as `INTR_TYPE_EL3`.
The next fix should target the modeled AP GIC secure SGI behavior or the TF-A
GIC handoff assumptions, then rerun the same marker-gated FWU GDB sample for
`QEMU resetting`, image-1, and `FIP_B` evidence.

### 2026-05-25 AP GIC Secure SGI Retest

The QEMU-to-SystemC bridge now preserves QEMU `MemTxAttrs` on MMIO requests so
secure TF-A accesses can reach libqemu-backed devices as secure transactions
rather than default non-secure transactions. The RSE AP GIC is now configured
with QEMU GICv3 security extensions enabled, matching the RD-Aspen FVP
multi-view/secure-GIC expectation closely enough to protect EL3 SGI setup from
later non-secure Linux writes.

| Evidence | Result |
| --- | --- |
| `tools/qbox/qemu-components/common/include/tlm-extensions/qemu-memtx-attrs.h` | Adds a TLM extension carrying `qemu::MemoryRegionOps::MemTxAttrs` across QBox TLM transactions. |
| `tools/qbox/qemu-components/common/include/ports/initiator.h` | Attaches the QEMU `MemTxAttrs` to each QEMU-originated MMIO payload before dispatching into SystemC. |
| `tools/qbox/qemu-components/common/include/ports/target.h` | Reads the TLM extension and passes the preserved attributes into `AddressSpace::read/write()`. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Enables `ap_gic.has_security_extensions = true` for the RSE-oriented AP GICv3 instance. |
| `git -C tools/qbox diff --check`, `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`, `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`, and `./scripts/validate_qbox_fvp_rd_aspen_map.py` | Passed before the runtime retest. |
| `timeout 240s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed after the MemTxAttrs/GIC-security change. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-gic-secure-20260525-v2/run/qbox-primary-console.log` | Corrects the earlier short-run suspicion: with the secure-GIC change enabled, QBox still reaches Linux login. The run was killed before FWU completion, so it is only a non-regression point. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-gic-secure-20260525-v3/progress-report.md` | Marker-gated FWU GDB sample found `systemd-shutdown[1]: Rebooting.` after 334.619 seconds. RSE/TF-M, AP/Linux, AP secure-service, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned 0. |
| `gdb-fwu-shutdown-gic-secure-20260525-v3/run/qbox-primary-console.log` | Linux reached login, mounted the FWU media, copied `fw.cap`, emitted `__QBOX_FWU_REBOOT_REQUESTED__`, reached `systemd-shutdown[1]: Rebooting.`, and printed `reboot: Restarting system`. |
| `gdb-fwu-shutdown-gic-secure-20260525-v3/run/qbox-secure-console.log` | No `ASSERT: plat/common/plat_gicv3.c:279` appears after the Linux reboot path, unlike `gdb-fwu-shutdown-sample-20260525-v1`. |
| `gdb-fwu-shutdown-gic-secure-20260525-v3/probes/ap-tfa-bl31-later.txt` | AP CPU0-CPU3 sample in TF-A BL31 `psci_pwrdown_cpu_end_terminal()` at `lib/psci/psci_common.c:1315`, indicating the secure SGI was accepted and the secondary power-down path was entered rather than panicking in `plat_ic_raise_el3_sgi()`. |
| `gdb-fwu-shutdown-gic-secure-20260525-v3/run/mhuv3-trace.log` | Records the AP-SI SCMI System Power protocol request `protocol=0x12 msg=0x3` near the Linux reboot path, and the service model currently returns success without a modeled whole-system reset side effect. |
| `gdb-fwu-shutdown-gic-secure-20260525-v3/run/qbox-platform.log` | No `QEMU resetting` or `SystemC resetting` line appears within the 8-second post-marker sample window. |

Current conclusion: AP GIC secure SGI handling is no longer the immediate FWU
reboot blocker. The bounded GDB sample now stops after the SGI path, with AP
cores in the BL31 terminal powerdown WFI loop and the SCMI System Power request
visible in the MHU trace. The next fix should add a modeled SCMI System Power
reset side effect for the AP-SI SCMI service path, then rerun the same
marker-gated FWU sample for `QEMU resetting`, `[INF] Attempting to boot image
1`, and `Booting with partition FIP_B`.

### 2026-05-25 FWU Reset-State GDB Evidence

The GDB environment is now usable for the QBox host, TF-M/RSE, AP
firmware/Linux, AP secure-service symbol overlays, SCP-Firmware symbols, and
SI CL1 Zephyr symbols during the FWU reboot path. SCP-Firmware remains
symbol/source-only because the current RSE path uses the SystemC/TLM SCP
service model rather than a live SCP CPU.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/common/include/loader.h` | Adds `load_at_elaboration` and reset-triggered `load_all()` support so selected firmware state can be restored on reset without reloading at elaboration. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Adds an AP BL2 reset-only loader for `.data`, `.stacks`, `.bss`, and `.xlat`, and removes the broad `host_ap_shared_sram.reset` path that wiped AP BL2 text. |
| `tools/qbox/systemc-components/rse_kmu/include/rse_kmu.h` and `tools/qbox/systemc-components/cc3xx/include/cc3xx.h` | Add reset sockets and explicit `doreset(true)` register/state restoration for the RSE local KMU and CC3XX models; `rse_reset_gpio.reset_out` now binds to both reset inputs when local crypto is enabled. |
| `timeout 120s cmake --build tools/qbox/build --target rse_kmu-tests cc3xx-tests platforms-vp --parallel 8` and `timeout 100s ctest --test-dir tools/qbox/build -R '^(rse_kmu-tests\|cc3xx-tests\|loader-test\|mhuv3_stub-tests)$' --output-on-failure` | Passed after adding reset coverage for the loader, KMU, and CC3XX paths. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-system-reset-20260525-v5/progress-report.md` | The AP system-reset side effect reaches Linux login, copies the FWU capsule, requests reboot, finds `systemd-shutdown[1]: Rebooting.`, and samples all GDB views successfully. The broad AP shared-SRAM reset was removed because it wiped BL2 text and caused exception-vector execution instead of a valid second BL2. |
| `gdb-fwu-shutdown-system-reset-20260525-v5/run/qbox-secure-console.log` | With selective AP BL2 reset state, AP BL2 starts a second time and loads image IDs 6 and 32, but the RSE measured-boot service returns `PSA_ERROR_BAD_STATE (-137)` for FW_CONFIG slot 8, proving RSE runtime state also has to be reset. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-system-reset-20260525-v7/progress-report.md` | After adding RSE reset fanout and local KMU/CC3XX reset inputs, the run again reaches Linux login, driver evidence, FWU capsule copy, `__QBOX_FWU_REBOOT_REQUESTED__`, `systemd-shutdown[1]: Rebooting.`, and `reboot: Restarting system`. Marker wait was 546.662 seconds, post-marker delay was 90 seconds, and all GDB probes returned 0. |
| `gdb-fwu-shutdown-system-reset-20260525-v7/run/qbox-primary-console.log` | First-boot Linux driver evidence includes SMMU v3, virtio block/net/rng, SCMI v2.1, MHUv3, remoteproc attach, `virtio_rpmsg_bus`, `rpmsg_net`, and `ethsi1`. Shutdown logs show virtio, MHU, SCMI, remoteproc, SMMU, watchdog, UART, timer, DSU PMU, and platform shutdown callbacks before `reboot: Restarting system`. |
| `gdb-fwu-shutdown-system-reset-20260525-v7/run/qbox-secure-console.log` | The previous FW_CONFIG `PSA_ERROR_BAD_STATE (-137)` does not recur before the sample point. The second AP BL2 reaches image ID 6 and image ID 32 load plus FW_CONFIG measurement/locking. |
| `gdb-fwu-shutdown-system-reset-20260525-v7/probes/tfm-later.txt` | Reboot-after-reset samples RSE in BL1_1 `boot_platform_error_state()` at `pc=0x11006e24`; `fih_ret_decode_zero_equality(0x85a5a5a6)` maps to `0x20000003`, which is `KMU_ERROR_NULL_POINTER` with `TFM_UNIQUE_ERROR_CODES=1`. |
| `gdb-fwu-shutdown-system-reset-20260525-v7/probes/ap-tfa-bl2-later.txt` | AP CPU0 is in TF-A BL2 `mhu_v3_x_doorbell_read()` at `drivers/arm/mhu/mhu_v3_x.c:221`, waiting for an RSE-side response while CPU1-CPU3 remain halted at BL2 entry. |

Current conclusion: the debug environment is in place and gives actionable
post-reboot samples. The AP BL2 reset-state issue and the earlier
measured-boot `PSA_ERROR_BAD_STATE` blocker are no longer the first observed
failure. The remaining blocker is the RSE reset lifecycle: direct fanout of
RSE TCM/VM reset plus remote QEMU reset is not yet ordered as an atomic FVP
system reset, and the second RSE BL1_1 run enters `boot_platform_error_state`
with a KMU-class initialization error before TF-M runtime can answer the AP
BL2 MHU request. The next fix should introduce an ordered RSE reset sequencer
or equivalent reset-domain model so RSE CPU reset, TCM/VM clearing,
KMU/CC3XX reset, and BL1_1 data/stack reinitialization happen in the same
observable order as the FVP.

### 2026-05-25 PC-Domain Warm Reset Correction

The prior RSE reset-sequencer conclusion was corrected after re-reading the
Arm Zena CSS reset documentation. Primary Compute domain reset is a standalone
AP reset flow: Safety Island and RSE remain operational, SCP notifies RSE
Runtime to reset and reload AP BL2, RSE Runtime resets AP Peripheral SRAM and
reloads AP BL2, and SCP powers AP back on. QBox must therefore model AP reset,
AP BL2 reload, and AP SDS warm-reset syndrome update without resetting the RSE
CPU, TCM, VM windows, or RSE local crypto state.

| Evidence | Result |
| --- | --- |
| `arm-zena-css/documentation/design/boot_process.rst` | The "Primary Compute domain reset" section states that Safety Island and RSE remain operational, and that RSE Runtime resets AP Peripheral SRAM and reloads AP BL2 before SCP powers AP back on. |
| `arm-zena-css/documentation/design/components.rst` | The SCMI communication summary states that TF-A asks SCP-Firmware to initiate system reset, and SCP-Firmware notifies RSE of system power down/reset. |
| `build/tmp_baremetal/work/.../trusted-firmware-a/.../rdaspen_measured_boot.c` | AP BL2 skips measured boot when `SDS_RESET_SYNDROME_SYS_RESET_REQ_BIT` is set in the SDS reset syndrome; without that bit it tries to re-use locked measured-boot slots and can receive `PSA_ERROR_BAD_STATE (-137)`. |
| `build/tmp_baremetal/work/.../trusted-firmware-a/.../include/drivers/arm/css/sds.h` | Defines `SDS_RESET_SYNDROME_STRUCT_ID = 5`, `SDS_RESET_SYNDROME_OFFSET = 0`, and `SDS_RESET_SYNDROME_SYS_RESET_REQ_BIT = 1 << 3`. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Removes the temporary RSE reset fanout from AP system reset, keeps the reset side effect scoped to AP BL2 reload/AP SRAM reset/AP CPU reset, and writes `0x8` to the AP SDS reset-syndrome payload at `HOST_AP_SHARED_SRAM + 0x50` during the reset-only AP BL2 loader action. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua tools/qbox/tests/components/loader/conf-test.lua` and `git -C tools/qbox diff --check` | Passed after the PC-domain warm-reset correction. |
| `timeout 120s cmake --build tools/qbox/build --target loader-test mhuv3_stub-tests platforms-vp --parallel 8` and `timeout 100s ctest --test-dir tools/qbox/build -R '^(loader-test\|mhuv3_stub-tests)$' --output-on-failure` | Passed after the AP SDS warm-reset update. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8/progress-report.md` | Marker-gated FWU GDB sample found `systemd-shutdown[1]: Rebooting.` after 520.166 seconds with 70 seconds post-marker delay; RSE/TF-M, AP/Linux, AP secure-service, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned 0. |
| `gdb-fwu-warm-reset-sds-20260525-v8/run/qbox-secure-console.log` | First AP BL2 reports `SDS reset syndrome = 0x0`; second and third AP BL2 entries report `SDS reset syndrome = 0x8`, `Warm reset syndrome detected, measured boot will be skipped`, and `BL2: Booting BL31`. |
| `gdb-fwu-warm-reset-sds-20260525-v8/run/qbox-primary-console.log` | First boot reaches Linux `6.18.5-rt3-yocto-preempt-rt`, Linux login, FWU capsule probe, `__QBOX_FWU_REBOOT_REQUESTED__`, `systemd-shutdown[1]: Rebooting.`, `FWU: Updating 5 payload(s)`, and a later `FWU: System booting in Regular State`. |
| `rg -a -n "Measure and record failed\|Loading of FW_CONFIG failed\|boot_platform_error_state" build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8/run build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8/probes` | No matches. The earlier FW_CONFIG `-137` and RSE BL1_1 `boot_platform_error_state()` failures did not recur in the corrected PC-domain reset run. |
| `gdb-fwu-warm-reset-sds-20260525-v8/probes/tfm-s-later.txt` | TF-M/RSE samples in runtime flash access (`nor_send_cmd_byte`) rather than BL1_1 error state, showing RSE remained operational after AP reset. |

Current conclusion: the modeled FWU reboot path now follows the Arm Zena CSS
PC-domain reset contract more closely. The immediate reset-state blocker is
resolved: AP BL2 is reloaded, AP measured boot is skipped on warm reset via
the SDS reset-syndrome bit, RSE remains alive, and the previous `-137` and
RSE BL1_1 KMU error signatures are absent in the bounded v8 GDB run. Remaining
FWU fidelity work is to determine why the updated run still reports
`FWU: System booting in Regular State` rather than proving `Trial State` /
`FIP_B` acceptance markers after `FWU: Updating 5 payload(s)`.

### 2026-05-25 FWU Start/Staging GDB Trace

The debug helper now generates a targeted TF-M FWU start/staging GDB script in
addition to the existing QBox host, TF-M/RSE, AP TF-A/OP-TEE/U-Boot/Linux,
Trusted Services overlay, SCP-Firmware symbol, and SI CL1 symbol scripts.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--tfm-fwu-start-trace`, records `tfm_fwu_start_trace` in `debug-env.json`, includes `tfm-fwu-start-trace.gdb` in generated README/progress reports, and traces `tfm_fwu_start()`, `fwu_bootloader_get_image_info()`, `fwu_bootloader_staging_area_init()`, `flash_area_open()`, flash erase/write breakpoints where present, `Driver_FLASH0_EraseSector()`, `Driver_FLASH1_EraseSector()`, and `psa_panic()`. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Passed after adding the FWU start/staging trace mode. |
| `git -C tools/qbox diff --check` | Passed after the helper update; the active QBox tree was not modified by this trace helper change. |
| `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-start-trace-setup-20260525-v1` | Generated the full debug bundle including `gdb/tfm-fwu-start-trace.gdb`; setup-only generation completed successfully. |
| `QBOX_RDASPEN_MHU_TRACE=false QBOX_RDASPEN_NETDEV='type=user,hostfwd=tcp::2236-:22' timeout 760s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-start-trace-20260525-v1 --launch --sample-only --fwu-probe --keep-running-after-pass --ignore-fail-patterns --rse-port 12630 --ap-port 12631 --runner-timeout 640 --trace-timeout 620 --gdb-timeout 6 --port-timeout 8 --sample-delay 1 --tfm-fwu-start-trace` | Completed the bounded GDB trace run and wrote `progress-report.md`; the runner was intentionally terminated by the helper after the trace timeout, so no `run/result.json` exists for this run. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-start-trace-20260525-v1/progress-report.md` | RSE and AP GDB ports opened. `tfm_fwu_start_trace_rc: 124` records the bounded trace timeout. Later TF-M, TF-M runtime, AP/Linux, AP secure-service, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned 0. |
| `gdb-fwu-start-trace-20260525-v1/probes/tfm-fwu-start-trace-gdb.log` | Breakpoints were installed at `tfm_fwu_start`, `fwu_bootloader_get_image_info`, `fwu_bootloader_staging_area_init`, `flash_area_open`, `Driver_FLASH0_EraseSector`, `Driver_FLASH1_EraseSector`, and `psa_panic`; `flash_area_erase` and `flash_area_write` remained pending because those symbols are not exported in `tfm_s.elf`. |
| `gdb-fwu-start-trace-20260525-v1/run/qbox-primary-console.log` | Linux reached login, completed the post-login driver probe, copied `fw.cap` into `/boot/EFI/UpdateCapsule/`, emitted `__QBOX_FWU_REBOOT_REQUESTED__`, and reached `systemd-shutdown[1]: Rebooting.`. No second-boot `FWU: Updating`, `FWU_DENIED`, `Trial State`, or `FIP_B` marker appears before the helper terminates the run. |
| `gdb-fwu-start-trace-20260525-v1/probes/tfm-s-later.txt` | TF-M/RSE runtime sampled in `__tfm_arch_thread_fn_call_veneer()` under `psa_wait_thread_fn_call()`, confirming RSE remained alive and attachable after the first Linux boot while the FWU start breakpoint was not reached. |
| `gdb-fwu-start-trace-20260525-v1/probes/linux-later.txt` | Linux sampled in `cpu_do_idle()`, confirming the AP/Linux GDB target remained attachable after the first boot and post-login probe. |
| `gdb-fwu-start-trace-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols/source still load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP stepping remains unavailable with `scp-strategy=service-model`. |
| `timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260525-v1 --launch --sample-only --sample-delay 1 --host-sample --host-sample-seconds 2 --runner-timeout 35 --gdb-timeout 5 --port-timeout 5 --rse-port 12640 --ap-port 12641 --ignore-fail-patterns` | Captured a separate QBox host GDB sample. `progress-report.md` records `host_gdb_sample_backtrace_captured: True`. |
| `gdb-qbox-host-sample-20260525-v1/host-gdb-run/qbox-platform.log` | Host GDB backtrace includes `sc_core::sc_start()`, `sc_main()`, the QEMU iothread, call_rcu threads, four AP `CPU */TCG` threads, and `QemuCpu::wait_for_work()`. |

Current conclusion: the requested GDB environment is now prepared and
artifact-proven for QBox host, TF-M/RSE, AP firmware, Linux, Trusted Services
overlay symbols, SCP-Firmware symbols, and SI CL1 Zephyr symbols. Live
SCP-Firmware stepping is still a model gap because the current run uses the
SystemC/TLM SCP service model and does not instantiate a live SCP CPU
`gdb_port`. The latest FWU start trace shows the run reaches Linux reboot
request and shutdown, but not TF-M `tfm_fwu_start()` or second-boot capsule
application before the bounded trace expires.

### 2026-05-25 Fresh-Flash GDB Progress With Short Timeouts

After replacing the AP flash target with the same `strata_flash_j3`
SystemC/TLM model class used for RSE boot flash, the short-timeout debug pass
was rerun with fresh writable flash copies. The AP flash CFI model is needed
because TF-M `Driver_FLASH1` uses Strata/CFI command sequences for AP flash
FWU staging; a plain `gs_memory` target treats those commands as data.

| Evidence | Result |
| --- | --- |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | `host_ap_flash` now uses `strata_flash_j3` with tracing, optional read-array DMI, 128 MiB size, 4 KiB sector size, and the existing compatibility knobs for byte-programming `0xff`. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds pass-through `--rse-flash`, `--ap-flash`, `--rse-otp`, `--efi-capsule-disk`, `--fwu-system-running-timeout`, and `--trace-after-sample` so exact image sets and deferred TF-M FWU traces can be reproduced. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds bounded FWU `systemctl is-system-running --wait` control through `--fwu-system-running-timeout`, allowing FWU debug attempts to fail quickly when Linux login is not reached. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`, `git -C tools/qbox diff --check`, and `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Passed after the AP flash/GDB helper updates. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests platforms-vp --parallel 8` and `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; the focused Strata flash test still passes and `platforms-vp` rebuilt. |
| `build/qbox-fvp-rd-aspen/gdb-efi-mm-ap-flash-strata-20260525-v1/progress-report.md` | Marker-gated sample found `EFI: MM partition ID` after 131.540 seconds. RSE/TF-M, AP/Linux, AP secure-service overlay, AP TF-A/OP-TEE/U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes all returned 0. |
| `gdb-efi-mm-ap-flash-strata-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 resolves to Trusted Services SE-Proxy `secure_storage_ipc_set()` -> `__psa_call(type=1001)` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`, waiting for an RSE secure-storage response. |
| `gdb-efi-mm-ap-flash-strata-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M runtime resolves to `Driver_FLASH0_ProgramData()` below ITS/PS flash filesystem writes, so the AP wait is paired with active RSE secure-storage flash traffic. |
| `build/qbox-fvp-rd-aspen/login-ap-flash-strata-20260525-v1/summary.txt` | Non-GDB runtime with the same fresh writable image policy reaches `FWU: ABI version 1.0 detected`, U-Boot key enrollment, and then times out at 240 seconds before Linux login. |
| `build/qbox-fvp-rd-aspen/gdb-bootflow-ap-flash-strata-20260525-v1/progress-report.md` | A later bootflow-marker sample did not reach `Booting bootflow 'virtio-blk#1.bootdev.part_1' with script` by 220 seconds. The sampled AP state is still SE-Proxy secure-storage set, this time for `uid=9223372036854775810` and `data_length=2391`; RSE/TF-M is in `Driver_FLASH0_EraseSector()` via the CFI byte-program erase loop. |
| `build/qbox-fvp-rd-aspen/gdb-qbox-host-current-20260525-v1/progress-report.md` | Short QBox host GDB run records `host_gdb_sample_backtrace_captured: True`; host backtrace includes SystemC `SC_START`, QEMU iothreads, AP TCG CPU threads, and `QemuCpu::wait_for_work()`. |
| `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/summary.txt` and `qbox-primary-console.log` | Non-GDB evidence later proves the secure-variable path itself completes: PK, KEK, `db`, and `dbx` enrollment all succeed, and the primary console reaches `FWU: ExitBootServices: Booting in regular state` before the short Linux-login timeout. |
| `build/fvp-boot-logs/critical-verbose-rse-blocker-20260525-v1/summary.txt` | Verbose, file-backed FVP comparison with an 80-second critical-marker cap reaches RSE runtime, SCP initialization, AP secure console output, Linux driver probes, rootfs mount, and systemd startup. The AP login marker is still outside that short cap, but FVP is already past the secure-storage and TF-M runtime stages where QBox GDB sampling is slow. |

Current conclusion: all requested GDB views are usable with short caps. With a
fresh writable flash set, GDB samples can catch in-flight secure-storage
writeback latency: AP SE-Proxy waits on RSE over MHUv3 while TF-M ITS/PS
performs Strata CFI byte-program/erase traffic on RSE `Driver_FLASH0`.
However, the later non-GDB T064 run proves PK/KEK/db/dbx enrollment does
complete and reaches `ExitBootServices`, so this is no longer classified as a
functional U-Boot enrollment blocker. The next fidelity/performance fix should
avoid using long timeouts as the solution; it should improve the high-volume
flash/GDB debug path or use a faithful replay/reset mode that preserves
expected secure-storage state without hiding FWU flash side effects.

### 2026-05-25 T076A Flash Write-Through Prerequisite

The local Arm Zena CSS Secure FWU guide defines the expected post-capsule
sequence as U-Boot `FWU: Updating 5 payload(s)`, then RSE boot image 1, TF-A
`FIP_B`, and U-Boot `Trial State`. Existing QBox long-run evidence reached the
payload update log, but the copied raw flash files still looked like the
pre-update images when inspected afterward. The immediate prerequisite was to
make the Strata flash model write program/erase mutations back to the per-run
raw flash images used as FWU evidence.

| Evidence | Result |
| --- | --- |
| `arm-zena-css/documentation/design/secure_firmware_update.rst` and `arm-zena-css/documentation/user_guide/reproduce.rst` | Secure FWU writes new payloads to the update bank, updates metadata, then expects RSE image 1, TF-A `FIP_B`, and U-Boot `Trial State` on the next boot. |
| `build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8/run/qbox-primary-console.log` | The existing long-run sample reached `FWU: Updating 5 payload(s)` but later printed `FWU: System booting in Regular State`; no `Trial State`, `FIP_B`, or RSE image 1 marker appeared. |
| `build/qbox-fvp-rd-aspen/fwu-inspect-gdb-v8-current/summary.md` | Inspection of that run's copied raw flash images still showed secondary banks empty/zeroed, RSE private metadata `boot_index=0`, and AP FWU metadata `active_index=0`. |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | Adds optional `backing_file` write-through. Byte-program and sector-erase mutations now copy the affected range into a shared mmap of the configured raw image. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Binds RSE boot flash and AP secure flash `backing_file` to the active per-run raw image only when `QBOX_RDASPEN_FLASH_WRITEBACK=true`. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Sets `QBOX_RDASPEN_FLASH_WRITEBACK=true` for copied writable flash images and `false` for `--no-copy-writable-flash`, preserving deploy artifacts. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds focused backing-file coverage for byte-program and sector-erase persistence. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`, `git -C tools/qbox diff --check -- systemc-components/strata_flash_j3/include/strata_flash_j3.h tests/components/strata_flash_j3/strata_flash_j3-tests.cc platforms/fvp-rd-aspen-rse/conf.lua`, and `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed after the write-through update. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` and `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; all Strata flash component tests passed, including the new write-through cases. |
| `timeout 120s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed; the platform binary links with the updated flash component. |
| `build/qbox-fvp-rd-aspen/rse-t076-flash-writeback-smoke-20260525-v2/summary.txt` | Short 60-second runtime smoke starts the RSE platform with per-run raw RSE/AP flash paths and no `backing_file` errors. The run intentionally times out before full boot/FWU markers. |
| `build/qbox-fvp-rd-aspen/rse-t076-flash-writeback-fwu-probe-20260525-v1/result.json` | Short 180-second FWU probe starts with copied raw RSE/AP flash images and writeback enabled, but times out before Linux login. `post_login_probe.sent_login=false`, no FWU commands are sent, and no bank-1 markers are present. |
| `build/qbox-fvp-rd-aspen/fwu-inspect-t076-writeback-probe-v1/summary.md` | Post-run flash inspection remains at the initial state: secondary banks are empty/zeroed, RSE private metadata is `boot_index=0`, and AP FWU metadata is `active_index=0`. |
| `build/qbox-fvp-rd-aspen/gdb-t076-writeback-short-20260525-v1/progress-report.md` | Short-cap GDB sample attaches to RSE/TF-M and AP GDB targets, loads SCP-Firmware and SI CL1 symbols, and terminates the runner after sampling. |
| `gdb-t076-writeback-short-20260525-v1/probes/tfm-later.txt` | RSE BL2 samples in `nor_cfi_reg_read()` -> `cfi_strataflashj3_read()` -> `Driver_FLASH0_ReadData()` -> `boot_decrypt_and_copy_image_to_sram()` while loading image ID 3, the SI CL0 image. |
| `gdb-t076-writeback-short-20260525-v1/probes/ap-tfa-bl2-later.txt` | AP CPU0 remains at TF-A BL2 entry `0x82000` with other AP CPUs halted, so the short-cap blocker is before AP boot and before Linux/FWU capsule handling. |

Current conclusion: the file-backed flash persistence prerequisite for T076 is
implemented and component-tested. A short post-fix FWU probe did not reach
Linux login, so it did not exercise capsule application. GDB narrows the
short-cap blocker to first-boot RSE BL2 flash-read/copy latency while loading
SI CL0. T074-T076 and V038 remain open until a bounded full FWU run proves
capsule application, RSE image 1, TF-A `FIP_B`, U-Boot `Trial State`, and
persisted bank/metadata state together.

### 2026-05-25 Current All-Target GDB Snapshot

The GDB helper was rerun with short caps to keep the debug loop bounded while
checking the available QBox, TF-M/RSE, SCP-Firmware, and AP/Linux views. The
SCP-Firmware view remains symbol/source-only because the active platform does
not instantiate a live SCP CPU; the `--scp-strategy real-si-scp` runner option
is not consumed by the Lua platform yet.

| Evidence | Result |
| --- | --- |
| `which gdb-multiarch`, `which gdb`, and `test -x .../arm-none-eabi-gdb` | Host GDB, multi-arch GDB, and the Yocto-provided Arm embedded GDB are all available for the generated scripts. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Passed before the current debug run. |
| `build/qbox-fvp-rd-aspen/gdb-fast-linux-current-20260525-v1/progress-report.md` | Generated the reusable GDB bundle, opened RSE and AP GDB ports `12680`/`12681`, sampled after 112 seconds, loaded SCP-Firmware and SI CL1 symbols, and captured a QBox host GDB backtrace. |
| `gdb-fast-linux-current-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M runtime samples at `tfm_hal_system_halt+2` in `tfm_hal_platform_reset.c:57`, with backtrace `tfm_hal_system_halt()` -> `tfm_spm_partition_psa_panic()` -> `tfm_arch_thread_fn_call(...)`. |
| `gdb-fast-linux-current-20260525-v1/probes/ap-tfa-bl2-later.txt` | AP CPU0 is running TF-A BL2 at `mhu_v3_x_doorbell_read()` (`drivers/arm/mhu/mhu_v3_x.c:221`) while CPU1-CPU3 remain halted at `bl2_entrypoint`. |
| `gdb-fast-linux-current-20260525-v1/probes/linux-later.txt` | The Linux GDB script attaches successfully to the AP target, but the PC is still `0x838c0` in AP BL2 rather than a Linux kernel address. Current short-cap progress has not reached Linux. |
| `gdb-fast-linux-current-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols/source load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; no live SCP stepping is available in the current service-model path. |
| `gdb-fast-linux-current-20260525-v1/probes/qbox-host-launch.txt` and `host-gdb-run/qbox-platform.log` | Host GDB captures `sc_core::sc_start()`, `sc_main()`, QEMU iothread, RPC server/client, worker, `call_rcu`, and AP `CPU */TCG` threads. |
| `gdb-fast-linux-current-20260525-v1/run/qbox-rse.log` | RSE reaches BL1_1, BL1_2, BL2, SI CL1 load, SI CL0 load, AP BL2 load, RSE runtime chainload, then `Creating an empty ITS flash layout.` and `Partition initialization FAILED in 0x31047cc5`. |

Current conclusion: the debug environment is usable for QBox host, RSE/TF-M,
AP firmware/Linux target attachment, SCP-Firmware source inspection, and SI CL1
symbol inspection. In the current bounded run Linux has not started; AP CPU0
is blocked in TF-A BL2 waiting on the MHU/HSE path while RSE TF-M runtime has
entered a partition panic/halt. This is distinct from older Linux-login
evidence and should be treated as the current short-cap blocker.

### 2026-05-25 Range-Limited Flash DMI GDB Snapshot

The full-device boot-flash DMI experiment made first-boot image reads fast
enough for AP sampling, but it could hide Strata/CFI command writes from the
SystemC flash model and moved the run back into TF-M ITS initialization
failure. The follow-up change adds range-limited DMI so only immutable primary
image slots are exposed through read-only QEMU aliases while storage and FWU
sectors continue through `strata_flash_j3` command-state behavior.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | Adds `dmi_ranges`, parsed as comma-separated `start:size` or `start-end`, and grants DMI only when the read or QEMU map query falls wholly inside a configured range. Empty `dmi_ranges` preserves the previous full-device DMI behavior. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds focused tests for range-limited direct DMI windows and b_transport DMI hints. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Wires `QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES` into RSE boot flash instances and `QBOX_RDASPEN_AP_FLASH_DMI_RANGES` into AP flash, without changing defaults. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Records the two DMI range environment variables in generated debug metadata. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after using global Lua config values for the two range strings to stay below Lua's 200-local main-function limit. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Passed after the GDB helper metadata update. |
| `git -C tools/qbox diff --check -- systemc-components/strata_flash_j3/include/strata_flash_j3.h tests/components/strata_flash_j3/strata_flash_j3-tests.cc platforms/fvp-rd-aspen-rse/conf.lua` | Passed. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` and `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; all Strata flash tests passed including the new DMI range cases and the prior write-through cases. |
| `timeout 120s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed after the Lua/platform wiring. |
| `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES='0x7000:0x260000' QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_AP_FLASH_DMI_RANGES='0x7000:0x240000' timeout 220s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ranged-dmi-writeback-20260525-v1 --launch --sample-only --sample-delay 125 --runner-timeout 150 --trace-timeout 120 --gdb-timeout 6 --port-timeout 8 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --copy-writable-flash --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --rse-port 12690 --ap-port 12691` | Completed the bounded GDB sample and wrote `progress-report.md`; all target probes returned 0 and QBox host GDB captured a backtrace. |
| `gdb-ranged-dmi-writeback-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M runtime sampled in `nor_send_cmd_byte()` -> `nor_byte_program()` -> `cfi_strataflashj3_program()` -> `Driver_FLASH0_ProgramData()` below ITS flash filesystem writes. This shows storage writes are reaching the SystemC CFI model rather than being hidden by DMI. |
| `gdb-ranged-dmi-writeback-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 resolves to Trusted Services SE-Proxy `secure_storage_ipc_set()` -> `__psa_call(type=1001)` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`, waiting for the RSE secure-storage response. |
| `gdb-ranged-dmi-writeback-20260525-v1/run/qbox-secure-console.log` and `run/qbox-primary-console.log` | AP progressed through TF-A BL2/BL31, OP-TEE SP loading, and U-Boot. The primary console reached `EFI: MM partition ID 0x8006` before the bounded GDB helper terminated the run. |
| `gdb-ranged-dmi-setup-20260525-v1/debug-env.json` | Setup-only generation records `QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000` and `QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000` in `launch_env`, proving the debug bundle preserves the range configuration. |

Current conclusion: the range-limited DMI path resolves the immediate
short-cap performance/debug conflict. It reaches AP secure firmware and U-Boot
within 125 seconds while preserving RSE flash program/erase traffic for
storage sectors. The current sampled state is not a Linux failure; it is an
in-flight secure-storage transaction where AP SE-Proxy waits over MHUv3 and
RSE TF-M is programming ITS/PS flash data. Live SCP-Firmware stepping remains
unavailable because the active platform still uses the SCP service model;
SCP-Firmware source/symbol loading is available through the generated GDB
bundle.

### 2026-05-25 RSE ATU DMI Span And Offset Guards

The optional `rse_atu` translated DMI path now rejects downstream DMI grants
that include the requested address but do not cover the full requested
transaction span. This keeps the opt-in ATU DMI path from handing QEMU a DMI
pointer whose valid range is shorter than the TLM request being accelerated.
The same increment also makes two's-complement negative ATU add-values fail
closed when the logical address is smaller than the negative offset magnitude,
instead of wrapping to a high physical address.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/rse_atu/include/rse_atu.h` | `translation_get_direct_mem_ptr()` now computes `range_end(logical, len)` and requires the clipped upstream DMI grant to cover the full request span. `translate_range()` and DMI pointer rebasing now use `apply_region_offset()` so negative offsets underflowing below physical address zero return an `overflow` translation fault instead of wrapping. |
| `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Adds `RejectsTranslatedDmiWhenRequestSpansDownstreamGrant`, which simulates a downstream DMI target that grants only two bytes for a four-byte request and verifies the ATU denies DMI without latching a translation fault. |
| `tools/qbox/tests/components/rse_atu/rse_atu-tests.cc` | Adds `RejectsNegativeOffsetUnderflowAndLatchesMismatchStatus` and `RejectsNegativeOffsetUnderflowDmiWithoutLatchingMismatchStatus` for normal translated accesses and non-latching DMI probes. |
| `timeout 120s cmake --build tools/qbox/build --target rse_atu-tests --parallel 8` | Passed; rebuilt `rse_atu.so` and the focused component test binary. |
| `timeout 30s tools/qbox/build/tests/components/rse_atu/rse_atu-tests --gtest_filter=RseAtuTest.RejectsTranslatedDmiWhenRequestSpansDownstreamGrant` | Passed; the new regression fails closed on a too-short downstream DMI grant. |
| `timeout 30s tools/qbox/build/tests/components/rse_atu/rse_atu-tests --gtest_filter='RseAtuTest.RejectsNegativeOffsetUnderflow*'` | Passed; both negative-offset underflow regressions fail closed. |
| `timeout 60s ctest --test-dir tools/qbox/build -R '^rse_atu-tests$' --output-on-failure` | Passed; all `rse_atu-tests` cases, including the new span guard and prior translated-DMI cases, passed. |
| `timeout 120s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed; the platform binary links with the updated ATU component. |
| `git -C tools/qbox diff --check -- systemc-components/rse_atu/include/rse_atu.h tests/components/rse_atu/rse_atu-tests.cc` | Passed. |

Current conclusion: this is an incremental T019X stabilization fix for
translated DMI correctness. It does not by itself make
`QBOX_RDASPEN_ATU_DMI=true` a default-safe runtime policy; that still requires
full AP/Linux/FWU evidence showing DMI does not hide host-window or flash/NVM
side effects.

### 2026-05-25 T058 AP EL3/Secure-World Closure Audit

A user-requested short-timeout GDB pass rechecked QBox host, TF-M/RSE,
AP firmware/Linux, SCP-Firmware, and SI CL1 symbol inspection without relying
on tmux screen output. The goal of this audit was to verify whether the
previous AP EL3/secure-world blocker still applies to T058.

| Evidence | Result |
| --- | --- |
| `.config.yaml` | Active configuration is still `MACHINE = "fvp-rd-aspen"`, `RD_ASPEN_VARIANT = "cfg2"`, and `PC_CPUS_COUNT_DEFAULT = "4"`. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/result.json` | `passed=true`, `timed_out=false`, `blocker=null`; RSE boot, RSE/SCP handoff, measured boot through `BL_33`, Linux login, root prompt, and post-login driver probes are all true. |
| `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/qbox-secure-console.log` | AP secure firmware reaches TF-A BL2, loads FW_CONFIG/HW_CONFIG/BL31/BL32/SPMD/BL33, prints `BL2: Booting BL31`, initializes BL31 runtime services, SCMI, GICv3, and PFDI. |
| `build/qbox-fvp-rd-aspen/gdb-all-targets-current-dmi-20260525-v1/progress-report.md` | Bounded GDB bundle opened RSE/TF-M port `12340` and AP/Linux port `12341`; TF-M, AP/Linux, AP TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbol, and SI CL1 symbol probes returned 0; host-GDB backtrace capture is true. |
| `gdb-all-targets-current-dmi-20260525-v1/probes/ap-tfa-bl2-later.txt` | AP CPU0 samples in TF-A BL2 `mbedtls_internal_sha256_process+224` at PC `0x8ec00`, while secondary AP CPUs remain at `bl2_entrypoint`; this is an in-flight short sample, not the older BL31 RAS trap. |
| `gdb-all-targets-current-dmi-20260525-v1/probes/linux-later.txt` | The AP/Linux GDB target attaches successfully and reports the same AP CPU thread set; the 70-second bounded sample is before the Linux kernel marker, while longer runtime evidence above proves Linux login. |
| `gdb-all-targets-current-dmi-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware source/symbol loading works for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP CPU stepping remains unavailable under `scp-strategy=service-model`. |

Current conclusion: T058 is closed. The AP CPU EL3/secure-world configuration
no longer blocks TF-A boot, BL31 runtime initialization, or Linux login. The
remaining work is not AP EL3 enablement; it is secure-service transport and
userspace validation (T061-T064), FWU bank-selection/persistence (T070-T076,
V038), and replacing service-modeled SI/SCP endpoints where full FVP
equivalence requires live firmware behavior.

### 2026-05-25 Short GDB Environment Recheck

The user requested a short-timeout GDB setup and progress check for QBox,
TF-M, SCP-Firmware, and Linux. The existing helper was reused and lightly
extended so the progress report records whether the placeholder SCP GDB port is
actually listening; with the current `scp-strategy=service-model` it is not.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds explicit `scp_port_listening` reporting and keeps the generated SCP script symbol-only for `service-model`; the same script can attach to `--scp-strategy real-si-scp` once a live SCP CPU GDB port is wired. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Passed after the helper update. |
| `build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1/progress-report.md` | Generated QBox host, TF-M/RSE, AP firmware/Linux, SCP-Firmware, and SI CL1 GDB scripts; RSE/AP ports `12820`/`12821` listened, SCP placeholder port `12822` did not. Host GDB captured a QBox/SystemC/QEMU thread/backtrace sample. |
| `gdb-all-debug-short-20260525-v1/probes/tfm-later.txt` | At the 40-second sample RSE/TF-M is still in BL2 image 3 load: `nor_cfi_reg_read()` -> `cfi_strataflashj3_read()` -> `boot_decrypt_and_copy_image_to_sram()`. |
| `gdb-all-debug-short-20260525-v1/probes/linux-later.txt` | AP GDB attaches, but all AP CPUs are still at `0x82000`/AP BL2 reset-vector state, so Linux has not started in the 40-second sample. |
| `gdb-all-debug-short-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; no live SCP stepping is available under the active service model. |
| `build/qbox-fvp-rd-aspen/gdb-handoff-debug-short-20260525-v1/progress-report.md` | The RSE log marker `RSE to SCP SCMI power on AP succeeded` is reached after 76.025 seconds, then bounded GDB probes attach to RSE and AP. |
| `gdb-handoff-debug-short-20260525-v1/probes/ap-tfa-bl2-later.txt` | AP CPU0 is released and running TF-A BL2 at `mhu_v3_x_doorbell_read()`; CPU1-CPU3 remain halted at `bl2_entrypoint`. |
| `gdb-handoff-debug-short-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M runtime is in `nor_send_cmd_byte()` below `tfm_its_set()` / ITS flash filesystem metadata update, proving the short sample is inside secure-storage flash writeback. |
| `build/qbox-fvp-rd-aspen/gdb-user-linux-marker-current-20260525-v1/progress-report.md` | A longer 120.038-second Linux-marker GDB run did not reach `Linux version`; the sampled AP state is SE-Proxy `secure_storage_ipc_set(uid=7, data_length=2)` waiting on MHUv3 while RSE/TF-M is in `tfm_its_remove()`. |
| `build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/` | Non-GDB runtime reaches Linux login and runs the secure-service probe, but `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` all hit bounded rc 124 after `libpsats` reports `Failed to open rpc session`. |

Current conclusion: the GDB environment is usable and artifact-backed for QBox
host, TF-M/RSE, AP firmware/Linux target attachment, SCP-Firmware symbol
inspection, and SI CL1 symbol inspection. Under short caps, the current
progression is RSE BL2 image load, then RSE/SCP AP release, then AP secure
firmware / SE-Proxy secure-storage traffic before Linux. Linux itself is
reachable in non-GDB post-login runtime, but the GDB marker samples show the
current short-timeout bottleneck before the Linux marker, in secure-storage
transaction progress and RSE flash writeback. Live SCP-Firmware stepping
remains unavailable until the service-modeled SCP endpoint is replaced or
augmented with a real SI/SCP CPU model.

### 2026-05-25 Short GDB Follow-Up

The short-timeout GDB flow was rerun with explicit current artifacts so the
QBox host, TF-M/RSE, SCP-Firmware, and AP/Linux inspection points can be
rechecked without using tmux screen state.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-short-20260525-v1/progress-report.md` | With the helper's conservative defaults, RSE/AP GDB ports listened, SCP placeholder did not, and `Linux version` was not reached within the 130.040-second marker cap. RSE/TF-M was still in BL2 Strata flash image read; AP was still at the AP BL2 reset-vector view. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-dmi-short-20260525-v1/progress-report.md` | With `QBOX_RDASPEN_ATU_DMI=true`, `QBOX_RDASPEN_HOST_MEMORY_DMI=true`, and writable flash copies, RSE passed the AP power-on handoff and TF-M runtime reached flash writeback; the 130.036-second Linux marker cap still stopped before `Linux version`. AP GDB resolved the sampled secure-world PC through the SE-Proxy `mhu_v3_x_doorbell_read()` path. |
| `build/qbox-fvp-rd-aspen/gdb-real-scp-short-20260525-v1/progress-report.md` | A 35-second `--scp-strategy real-si-scp` check did not open the SCP GDB port and did not create an SCP console log; SCP-Firmware remains symbol/source-only in the current QBox platform. |
| `build/qbox-fvp-rd-aspen/gdb-qbox-host-short-20260525-v1/progress-report.md` | Host attach with `gdb -p` was blocked by the current ptrace/TTY context, but the host-GDB launch path captured SystemC/QBox/QEMU thread backtraces. The host sample shows `SC_START`, `sc_core::sc_start()`, QEMU iothreads, and AP CPU TCG threads in `QemuCpu::wait_for_work()`. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Progress/README wording now describes SCP debug by selected strategy and records that `scp_port_listening` is authoritative for live SCP CPU availability. |

Current conclusion: the reusable GDB environment is set up and verified for
all requested debug surfaces. QBox host and RSE/AP targets are live-debuggable;
Linux symbols and attach scripts are ready and proven by prior longer
post-login artifacts, but the short marker reruns stopped before the Linux
kernel banner. SCP-Firmware live stepping is still not available because no
SCP CPU GDB server is instantiated; only symbol/source inspection works today.

### 2026-05-25 Short Runtime Flash Persistence Recheck

The follow-up runtime checks used short caps and file-backed artifacts instead
of tmux screen state to separate GDB/debug setup from the current
secure-storage and FWU persistence behavior.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/writable-images/rse-flash-image.raw.img` | SHA-256 is `d25e0adaaf29ad47ca33dfbb125ddf33519d7767e3dfb521ad0bee180bb60de0`, identical to the decompressed deploy `rse-flash-image.img`. Although the same run's primary console shows PK/KEK/db/dbx enrollment and then in-run `already been enrolled` messages, this raw image is not valid cross-run persistence evidence. |
| `build/qbox-fvp-rd-aspen/rse-t061-reuse-enrolled-flash-secure-service-20260525-v1/` | Reusing the `rse-t064` raw image starts from missing variables again: `Error: "PK" not defined`, then PK/KEK enrollment. This is explained by the seed raw matching the deploy image, not by a proven current writeback failure. |
| `QBOX_RDASPEN_BOOT_FLASH_TRACE=true QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=2048 timeout 130s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 100 --out-dir build/qbox-fvp-rd-aspen/rse-t076-flash-trace-short-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --ignore-fail-patterns` | Expected timeout before U-Boot enrollment, but the RSE raw flash SHA changed to `2520bf69729f5e06f2668789d342c31dd55434ba545f772c9fece35ba1674b21`. The first differences versus the deploy-equivalent raw start at file offset `0x3007000`, proving the current RSE flash writeback path can mutate the per-run raw image under a short cap. |
| `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000 QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000 timeout 220s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 190 --out-dir build/qbox-fvp-rd-aspen/rse-t076-range-dmi-fresh-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --post-login-probe --secure-service-probe --secure-service-probe-timeout 8 --ignore-fail-patterns` | Expected timeout before Linux login. Primary console reaches `PK key is enrolled successfully!`, `KEK key is enrolled successfully!`, and then `Error: "db" not defined`. The RSE raw flash SHA changes to `6c2e9a3824a61c50146a55c62d3ddec56399a3beec28fc367164272ac57b3090`, while AP flash remains deploy-equivalent. |
| `build/qbox-fvp-rd-aspen/rse-t076-reuse-partial-flash-20260525-v1/` | Reusing a partially mutated raw image from an aborted run enters `FWU: Updating 5 payload(s)` and times out. This shows partial aborted flash state can drive FWU metadata/update paths, so it is not yet a valid pre-enrolled reusable seed. |

Current conclusion: the latest writeback plumbing is observable in the raw RSE
flash images, but T076 is still open. The project still needs a bounded
cross-run proof where a fully enrolled or FWU-updated raw image is reused and
the next run observes the expected persisted state without falling into an
aborted intermediate FWU state. Short caps currently stop in U-Boot
secure-variable enrollment or RSE TF-M ITS/PS flash writeback before Linux
login.

### 2026-05-25 User-Requested All-Target GDB Recheck

The latest GDB recheck used the existing helper rather than tmux screen state
to inspect the current short-timeout progress for QBox, TF-M/RSE,
SCP-Firmware, and AP/Linux.

| Evidence | Result |
| --- | --- |
| `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true timeout 105s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --sample-delay 35 --runner-timeout 55 --port-timeout 5 --gdb-timeout 5 --host-sample --host-sample-seconds 2 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/gdb-user-request-all-targets-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` | Completed and generated `README.md`, `debug-env.json`, `progress-report.md`, GDB command files, and probe logs. |
| `build/qbox-fvp-rd-aspen/gdb-user-request-all-targets-20260525-v1/progress-report.md` | RSE/TF-M GDB port `12340` and AP/Linux CPU0 GDB port `12341` listened. `scp_port_listening` is false under the current `scp-strategy=service-model`; SCP-Firmware symbol probing still returns 0. |
| `gdb-user-request-all-targets-20260525-v1/probes/tfm-later.txt` | At the 35-second sample, RSE/TF-M is in BL2 image loading: `nor_cfi_reg_read()` -> `cfi_strataflashj3_read()` -> `Driver_FLASH0_ReadData()` -> `boot_decrypt_and_copy_image_to_sram()`. |
| `gdb-user-request-all-targets-20260525-v1/probes/linux-later.txt` | AP/Linux GDB attaches and exposes CPU#0-CPU#3, but all AP CPUs are still at `0x82000`; the TF-A BL2 symbol script resolves CPU0 to `bl2_entrypoint()`. Linux has not started in this short sample. |
| `gdb-user-request-all-targets-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP CPU stepping remains unavailable because the current platform uses a service-model SCP endpoint. |
| `gdb-user-request-all-targets-20260525-v1/host-gdb-run/qbox-platform.log` | Host GDB captured `platforms-vp` thread/backtrace evidence including `sc_main()`, `sc_core::sc_start()`, QEMU iothreads, AP `CPU */TCG` threads, and `QemuCpu::wait_for_work()`. |

Current conclusion: the GDB environment is set up and reusable for the
requested debug surfaces. QBox host and RSE/AP CPU targets are live-debuggable,
Linux symbols and attach scripts are present but the latest short cap stopped
before the Linux kernel banner, and SCP-Firmware remains source/symbol-only
until the service-modeled SCP endpoint is replaced or augmented with a live
SCP CPU model.

### 2026-05-25 EFI Marker GDB Recheck And FWU Flash Inspection

The current FWU probe was bounded and stopped after the primary UART remained
at `EFI: MM partition ID 0x8006` with no further log or flash mtime progress.
Because the plain runtime was not started with QBox GDB ports and host
`gdb -p` is blocked by the current ptrace/TTY policy, the EFI marker was then
reproduced with the GDB helper and range-limited flash DMI.

| Evidence | Result |
| --- | --- |
| `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000 QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000 timeout 700s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 620 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --post-login-probe --fwu-probe --fwu-system-running-timeout 30 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-v038-current-fwu-range-dmi-20260525-v1` | Manually stopped after the UART/log artifacts stopped progressing. The primary console reached U-Boot and `EFI: MM partition ID 0x8006`; secure console booted `FIP_A` and reported early SE-Proxy/SMM Gateway secure-storage errors. Linux login and FWU capsule commands were not reached. |
| `build/qbox-fvp-rd-aspen/fwu-inspect-v038-current-range-dmi-20260525-v1/summary.md` | RSE/AP flash raw sizes and capsule disk presence are valid, but all secondary banks remain empty. RSE private metadata reports boot index 0 and states `[0, 0, 0, 0, 0]`; AP FWU metadata remains active bank 0. This is not valid Trial State, FIP_B, or T076 persistence evidence. |
| `gdb -p <running platforms-vp/remote_cpu>` | Attach failed with the current ptrace policy (`ptrace: Inappropriate ioctl for device`). The supported host-debug path remains runner-launched host GDB, not late attach to an already spawned process. |
| `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000 QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000 QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=6000 timeout 280s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-user-efi-current-20260525-v1 --launch --sample-only --sample-marker 'EFI: MM partition ID' --sample-marker-post-delay 15 --sample-delay 170 --runner-timeout 210 --trace-timeout 80 --gdb-timeout 6 --port-timeout 8 --host-sample --host-sample-seconds 2 --ignore-fail-patterns --copy-writable-flash --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` | Completed. The marker was found in the primary console after 101.526 seconds; RSE/AP GDB ports listened; all target probes returned 0; host-GDB captured a QBox/SystemC/QEMU backtrace. |
| `gdb-user-efi-current-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 is not in Linux. It is in Trusted Services SE-Proxy `secure_storage_ipc_remove()` -> `__psa_call(type=1004)` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`, waiting for the RSE secure-storage response. CPU1-CPU3 are halted. |
| `gdb-user-efi-current-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is in `tfm_its_remove()` below the ITS flash filesystem delete/compact path, writing through `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` -> `nor_send_cmd_byte()`. This confirms the current EFI-marker pause is inside RSE secure-storage flash writeback, not a Linux kernel hang. |
| `gdb-user-efi-current-20260525-v1/probes/linux-later.txt` | The AP/Linux GDB script attaches and exposes CPU#0-CPU#3, but the sampled PC is still the secure-service address `0x4008bc90`; Linux has not started at this marker. |
| `gdb-user-efi-current-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP stepping remains unavailable under the current service-model SCP endpoint. |

Current conclusion: the short-timeout GDB setup is effective for locating the
current pause. At the EFI marker, AP secure world is waiting for a
secure-storage REMOVE response while RSE/TF-M is actively compacting/deleting
ITS flash filesystem data through the SystemC Strata flash model. The next
V038/T076 work should focus on completing this secure-storage writeback path
fast enough to reach Linux/FWU under bounded runs, then rechecking clean
secondary bank population and bank-1 boot markers.

### 2026-05-25 Strata DMI Invalidation And EFI Marker Recheck

The follow-up change tightened Strata flash DMI invalidation and then reran the
same marker-gated GDB inspection with short timeouts and file-backed logs.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | Tracks whether a read-only DMI grant is active, invalidates it only once on a command-state write, and avoids repeated full-device invalidation for the following program-data write after DMI is already revoked. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds `ProgramSequenceInvalidatesActiveDmiOnlyOnce`, covering command invalidation, program-data write behavior, and DMI reacquisition. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` | Passed. |
| `timeout 30s tools/qbox/build/tests/components/strata_flash_j3/strata_flash_j3-tests --gtest_filter='StrataFlashJ3Test.ProgramSequenceInvalidatesActiveDmiOnlyOnce:StrataFlashJ3Test.*BackingFile:StrataFlashJ3Test.Dmi*'` | Passed; 5 focused Strata flash tests passed. |
| `timeout 30s tools/qbox/build/tests/components/strata_flash_j3/strata_flash_j3-tests` | Passed; all 18 Strata flash component tests passed. |
| `git -C tools/qbox diff --check -- systemc-components/strata_flash_j3/include/strata_flash_j3.h tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Passed. |
| `timeout 180s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed. |
| `build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1/progress-report.md` | Marker-gated GDB run reached `EFI: MM partition ID` after 113.028 seconds, opened RSE/AP GDB ports, and captured QBox host GDB backtraces. |
| `gdb-efi-after-dmi-inval-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 is still in SE-Proxy `secure_storage_ipc_remove()` -> `__psa_call(type=1004)` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`; CPU1-CPU3 remain halted. |
| `gdb-efi-after-dmi-inval-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M is still in `tfm_its_remove()` / ITS flash filesystem delete/compact, writing through `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` -> `nor_send_cmd_byte()`. |
| `gdb-efi-after-dmi-inval-20260525-v1/probes/linux-later.txt` | AP/Linux target attaches, but the sampled PC remains secure-service code; Linux has not started at this marker. |
| `gdb-efi-after-dmi-inval-20260525-v1/probes/scp-symbols.txt` | SCP-Firmware symbols load for `rdaspen-si0-bl2.elf`, entry `0x120000000`; live SCP stepping remains unavailable under the service-modeled SCP path. |
| `build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1/mhuv3-trace-summary.txt` | MHU trace pairing found 15 AP-to-RSE channel-1 secure doorbell requests with prefix `0x800`, 14 matched responses, and one in-flight missing response at the sample. Matched response latencies include 3.030, 3.935, 3.496, and 3.252 simulated seconds in the late secure-storage sequence. |
| `arm-zena-css/documentation/releasenotes.rst` | Documents the first-boot SE-Proxy `secure_storage_ipc_remove: ... -140` messages as expected `PSA_ERROR_DOES_NOT_EXIST` behavior before SMM Gateway creates missing variable indexes. |
| `build/fvp-boot-logs/critical-verbose-rse-blocker-20260525-v1/summary.txt` and console logs | FVP reaches the same EFI marker and expected `-140` secure-storage messages, then reaches `Linux version`, rootfs mount, and systemd startup within the short critical-marker window. |

Current conclusion: the Strata DMI invalidation cleanup is valid and tested,
but it does not materially improve the current EFI-marker stall. The bottleneck
remains RSE TF-M ITS/PS flash filesystem delete/compact/writeback through the
SystemC Strata CFI byte-program path. FVP evidence shows the expected first
boot `-140` messages are not sufficient to explain QBox staying before Linux
at the marker-gated sample.

### 2026-05-25 SE-Proxy FWU Discovery Panic Decode

The post-login secure-service probe artifact
`build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/` reaches
Linux login and validates the main Linux driver surface, but
`psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` all return
`124` after `libpsats` reports `Failed to open rpc session`.

The corresponding secure console loads SE-Proxy at `0x40031000` and then
prints a user-mode data abort at `0x400473d8`, `x0 = 0`, and
`SP panicked with code 0xdeadbeef`. Address decoding used both
`aarch64-poky-linux-addr2line` and `gdb-multiarch` against the SE-Proxy ELF:

| Address | Decode |
| --- | --- |
| `0x400473d8 - 0x40031000 = 0x163d8` | `update_agent_discover + 20`, `trusted-services/components/service/fwu/common/update_agent_interface.c:12` |
| `0x40047a4c - 0x40031000 = 0x16a4c` | `discover_handler + 72`, `trusted-services/components/service/fwu/provider/fwu_provider.c:106` |
| `0x4004ba70 - 0x40031000 = 0x1aa70` | `service_handler_invoke`, `trusted-services/components/service/common/provider/service_provider.h:31` |
| `0x4004bc58 - 0x40031000 = 0x1ac58` | `receive`, `trusted-services/components/service/common/provider/service_provider.c:64` |
| `0x40042280 - 0x40031000 = 0x11280` | `handle_service_interfaces`, `trusted-services/components/rpc/ts_rpc/endpoint/sp/ts_rpc_endpoint_sp.c:234` |
| `0x400428a4 - 0x40031000 = 0x118a4` | `sp_main`, `trusted-services/deployments/se-proxy/env/commonsp/se_proxy_sp.c:94` |

The confirming GDB command resolved `0x163d8` to
`update_agent_discover()` line 12, `if (!update_agent->interface->discover)`,
and `0x16a4c` to `discover_handler()` line 106, where
`this_instance->update_agent` is passed into `update_agent_discover()`. Given
`x0 = 0` in the OP-TEE abort register dump, the SE-Proxy FWU provider is
servicing discovery with a null `update_agent`.

FVP comparison:

| Evidence | Result |
| --- | --- |
| `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/terminal_sec_uart_5003.log` | FVP prints expected first-boot SE-Proxy secure-storage errors such as `-140`, `-133`, and `-135`, but no SE-Proxy panic. |
| `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/terminal_ns_uart0_5004.log` | `psa-iat-api-test` returns `0`; `psa-its-api-test` returns `0`. |
| `build/fvp-boot-logs/rse-secure-service-ps-probe-20260525-v1/terminal_ns_uart0_5004.log` | `psa-ps-api-test` progresses through PS test 409 in the bounded window. |

Current conclusion: QBox now has enough GDB/log evidence to split two issues.
Before Linux, marker-gated GDB still shows the EFI pause in RSE TF-M ITS/PS
Strata flash writeback. After Linux login, the secure-service user tests fail
because SE-Proxy has panicked in FWU discovery and remains busy to subsequent
SMM Gateway / libpsats RPC requests. The expected first-boot secure-storage
`-140` messages are present on both QBox and FVP; the QBox-specific blocker is
the null `update_agent` FWU discovery panic.

### 2026-05-25 Current Rebuild Short GDB Recheck

The current QBox `platforms-vp` binary was rebuilt before rerunning the
file-backed GDB sample so older pre-rebuild MHU evidence would not be mixed with
the current source tree.

| Evidence | Result |
| --- | --- |
| `cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed. |
| `build/qbox-fvp-rd-aspen/gdb-efi-marker-current-rebuilt-20260525-v3/progress-report.md` | Generated QBox host, TF-M/RSE, AP firmware/Linux, SCP-Firmware, Trusted Services, and Zephyr symbol scripts. RSE port `12340` and AP port `12341` were live; service-mode SCP remained symbol-only. |
| `debug_qbox_fvp_rd_aspen_rse_gdb.py --runner-timeout 140 --sample-delay 130 --port-timeout 8 --gdb-timeout 8 --sample-only --sample-marker 'EFI: MM partition ID'` | `sample_marker_found: False` after 130.039 seconds; runner terminated by timeout (`-15`). |
| `probes/tfm-later.txt` | RSE/TF-M was in BL2 `cfi_strataflashj3_read()` -> `Driver_FLASH0_ReadData()` -> `boot_decrypt_and_copy_image_to_sram()` while copying an image from flash. |
| `probes/linux-later.txt` and AP firmware probes | AP CPU0-CPU3 remained at `0x82000`; with TF-A BL2 symbols this is `bl2_entrypoint`, so Linux had not started. |
| `probes/scp-symbols.txt` | SCP-Firmware symbols loaded for `rdaspen-si0-bl2.elf`, entry `0x120000000`; no live SCP port is expected under `scp-strategy=service-model`. |
| `run/qbox-primary-console.log`, `run/qbox-secure-console.log`, and missing `run/mhuv3-trace.log` | No primary/secure-console output and no MHU trace were produced in this short window, consistent with execution still being before AP and secure-service MHU traffic. |

Current conclusion: with the current rebuilt QBox binary and short FVP-like
timeouts, the live progress point is earlier than the old post-login
SE-Proxy-panic artifact. The system is still in RSE TF-M BL2 flash image loading
before AP firmware execution. The SE-Proxy FWU null-`update_agent` panic remains
valid for the older post-login artifact, but it is not reached in the current
short rebuilt run.

### 2026-05-25 Current Range-Limited DMI GDB Recheck

The next short run reused the current rebuilt QBox binary and enabled the
storage-safe fast path: ATU DMI, host-memory DMI, RSE boot-flash DMI restricted
to `0x7000:0x260000`, and AP flash DMI restricted to `0x7000:0x240000`.

| Evidence | Result |
| --- | --- |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --range-limited-flash-dmi --copy-writable-flash --sample-marker 'Linux version' --sample-delay 140 --runner-timeout 160` | New helper option sets the range-limited DMI environment without requiring a long shell prefix. Setup-only artifact `gdb-range-dmi-setup-current-20260525-v1/debug-env.json` records `range_limited_flash_dmi=true`, `QBOX_RDASPEN_ATU_DMI=true`, `QBOX_RDASPEN_BOOT_FLASH_DMI=true`, `QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000`, `QBOX_RDASPEN_HOST_MEMORY_DMI=true`, and `QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000`. |
| `build/qbox-fvp-rd-aspen/gdb-efi-marker-range-dmi-option-current-20260525-v1/progress-report.md` | The new `--range-limited-flash-dmi` option was launched directly. It reached `EFI: MM partition ID` after 99.030 seconds, opened both RSE/AP GDB ports, and all target probes returned 0 except the expected live SCP port under `service-model`. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-current-20260525-v1/progress-report.md` | RSE and AP GDB ports opened on `12720`/`12721`; TF-M, AP/Linux, AP secure services, TF-A, OP-TEE, U-Boot, SCP symbols, and SI CL1 symbols all probed successfully. `Linux version` was not reached within 140.043 seconds. |
| `gdb-linux-marker-range-dmi-current-20260525-v1/run/qbox-rse.log` | RSE passed BL1_1, BL1_2, BL2, SI CL1, SI CL0, AP BL2, RSE runtime chainload, measured boot through `BL_33`, and entered TF-M runtime. |
| `gdb-linux-marker-range-dmi-current-20260525-v1/run/qbox-primary-console.log` | U-Boot reached `EFI: MM partition ID 0x8006`; Linux did not start before the sample cap. |
| `gdb-linux-marker-range-dmi-current-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 sampled in SE-Proxy `secure_storage_ipc_set()` -> `__psa_call(type=1001)` -> `rse_comms_platform_invoke()` -> `mhu_send_data(size=60)` -> `mhu_v3_x_doorbell_read(channel=127)`. |
| `gdb-linux-marker-range-dmi-current-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M sampled in `CMU_MHU2_Receiver_Handler()` -> `sfcp_interrupt_handler()` -> `sfcp_hal_receive_message()` -> `mhu_receive_message(total_message_size=60)` -> `mhu_v3_x_get_num_channel_implemented()`. |
| `scripts/analyze_qbox_mhu_trace.py gdb-linux-marker-range-dmi-current-20260525-v1/run/mhuv3-trace.log` | The AP-to-RSE channel-1 stream had 21 requests, 20 matched responses, and one in-flight request at the sample. The latest matched responses completed, so the sampled condition is slow secure-storage traffic rather than a dead MHU route. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-full-dmi-current-20260525-v1/progress-report.md` | Full-device boot-flash DMI remains unsafe: RSE/TF-M reports `Creating an empty ITS flash layout.` and `Partition initialization FAILED in 0x31047cc5`, then GDB samples `tfm_hal_system_halt()`. |
| `build/fvp-boot-logs/critical-verbose-rse-blocker-20260525-v1/terminal_ns_uart0_5004.log` | FVP reaches the same `EFI: MM partition ID`, PK/KEK enrollment, and `db` warning sequence, then reaches `Linux version`; QBox is therefore still behind FVP in the secure-storage writeback window. |

Current conclusion: range-limited flash DMI is the right reusable debug path
for short all-layer GDB samples. It moves the current rebuilt QBox run from
pre-AP TF-M BL2 image loading to the U-Boot/SE-Proxy secure-storage phase while
preserving the negative evidence that full-device boot-flash DMI corrupts TF-M
ITS initialization. The remaining pre-Linux gap is secure-storage writeback
latency through the RSE MHU/SFCP/TF-M path, not AP release or Linux GDB setup.

### 2026-05-25 Strata No-Op Writeback Recheck

The Strata flash backing-file path now skips writes when a byte-program
operation leaves the flash array unchanged. This is aimed at the TF-M
CSS-Aspen Strata erase/write sequence, where firmware repeatedly programs
`0xff` bytes through CFI byte-program commands after an erase-compatible sector
operation has already restored bytes to erased state.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | `program()` now computes the programmed value first, updates only bytes whose value changes, and calls `write_backing_range()` only for the changed subrange. No-op programs still set status ready and return to status mode. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds `NoopProgramSkipsBackingFileWrite`, which uses a deliberately short backing file and confirms programming `0xff` over an already-erased byte produces no backing range error. |
| `git -C tools/qbox diff --check -- systemc-components/strata_flash_j3/include/strata_flash_j3.h tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Passed. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py scripts/analyze_qbox_mhu_trace.py` | Passed. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` | Passed. |
| `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; all Strata flash component tests passed. |
| `timeout 180s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-noop-current-20260525-v1/progress-report.md` | Range-limited DMI run opened RSE/AP GDB ports on `12750`/`12751`, reached U-Boot `EFI: MM partition ID 0x8006`, but did not reach `Linux version` within 125.036 seconds. |
| `gdb-linux-marker-range-dmi-noop-current-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M sampled in `tfm_its_remove()` -> `its_flash_fs_file_delete()` -> `its_flash_fs_delete_idx()` -> `its_flash_fs_dblock_compact_block()` -> `its_flash_fs_block_to_block_move()` -> `its_flash_nor_write()` -> `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` -> `nor_byte_program()` -> `nor_send_cmd_byte()`. |
| `gdb-linux-marker-range-dmi-noop-current-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 sampled in SE-Proxy `secure_storage_ipc_set()` -> `__psa_call(type=1001)` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read(channel=127)`. |
| `gdb-linux-marker-range-dmi-noop-current-20260525-v1/mhu-summary.txt` | Analyzer reported 21 AP-to-RSE channel-1 requests, 20 matched responses, and one in-flight request at the sample. The analyzer returns non-zero for the missing in-flight pair, but the latest matched responses complete. |

Current conclusion: no-op backing-file suppression is correct and reduces host
writeback overhead, but it is not enough to reach Linux under the bounded GDB
sample. The remaining gap is the firmware-visible CFI byte-program transaction
count in TF-M ITS/PS flash compaction. A follow-up needs either a faithful
Strata buffered-program path that TF-M can use or another model-level
optimization that reduces the per-byte SystemC/QEMU transaction cost without
hiding command-state semantics from TF-M.

### 2026-05-25 Strata Flash Stats And Fresh FVP Reference

The current all-target GDB helper now has a `--flash-stats` option. It wires
RSE/AP `strata_flash_j3` stats files through the Lua platform using
`QBOX_RDASPEN_RSE_BOOT_FLASH_STATS_FILE`,
`QBOX_RDASPEN_AP_FLASH_STATS_FILE`, and
`QBOX_RDASPEN_FLASH_STATS_INTERVAL`.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h` | Adds optional `stats_file` and `stats_interval` CCI parameters plus counters for reads, writes, CFI command classes, program operations, no-op/changing program bytes, compatibility sector erases, and backing-file writes. |
| `tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc` | Adds stats-file tests for normal/no-op byte program counters and sector-erase compatibility counters. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Connects RSE boot-flash and AP flash stats parameters. The settings are globals to avoid this large Lua config's 200-local-variable limit. |
| `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` | Adds `--flash-stats` and `--flash-stats-interval`, records the effective stats environment in `debug-env.json`, and includes stats env lines in generated run instructions. |
| `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py scripts/analyze_qbox_mhu_trace.py` | Passed. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Passed after converting the new stats knobs from locals to the existing global-configuration pattern. |
| `rg -n '[ \t]+$' ...changed files...` and `git -C tools/qbox diff --check` | Passed. The `rg` no-match exit code is expected for no trailing whitespace. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` | Passed. |
| `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; `strata_flash_j3-tests` completed in 0.70 seconds. |
| `timeout 180s cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/progress-report.md` | GDB sample opened RSE/AP ports on `12780`/`12781`, reached U-Boot `EFI: MM partition ID 0x8006`, but did not reach `Linux version` within 125.037 seconds. |
| `gdb-linux-marker-range-dmi-flash-stats-20260525-v1/probes/ap-secure-services-later.txt` | AP CPU0 sampled in SE-Proxy `secure_storage_ipc_set()` waiting in `mhu_v3_x_doorbell_read(channel=127)` after `__psa_call(type=1001)`. |
| `gdb-linux-marker-range-dmi-flash-stats-20260525-v1/probes/tfm-s-later.txt` | RSE/TF-M sampled in `tfm_its_set()` / PS-backed ITS writeback, below `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` -> `nor_byte_program()` -> `nor_poll_dws_byte()`. |
| `gdb-linux-marker-range-dmi-flash-stats-20260525-v1/run/rse-strata-stats.json` | Quantifies the bottleneck: `program_ops=246699`, `read_status_cmds=493397`, `write_accesses=1480192`, `read_accesses=776455`, `compat_ff_sector_erase_ops=178`, and `backing_write_ops=200603` before the sample. |
| `gdb-linux-marker-range-dmi-flash-stats-20260525-v1/mhu-summary.txt` | Analyzer found 16 AP-to-RSE channel-1 requests, 15 matched responses, and one in-flight request; late matched responses include multi-second simulated-time secure-storage transactions. |
| `timeout 240s scripts/runfvp_log_boot.py --runfvp-verbose --timeout 180 --require critical --out-dir build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1` | FVP did not reach login before the 180-second cap, but it reached `Booting Linux on physical CPU` and `Linux version 6.18.5-rt3-yocto-preempt-rt`; QBox did not reach `Linux version` under its comparable marker cap. |
| `build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1/terminal_sec_uart_5003.log` | FVP shows the same expected first-boot SE-Proxy `secure_storage_ipc_remove: ... -140` messages and then continues to secondary CPU startup and `tee_ta_close_session`. |

Current conclusion: the QBox pre-Linux gap is now quantified. The RSE
secure-storage path is issuing hundreds of thousands of firmware-visible CFI
byte-program and status-poll transactions through the SystemC Strata flash
model. The expected first-boot `-140` secure-storage messages also appear on
FVP and are not the reason QBox remains before Linux. The next implementation
step should either add a faithful Strata buffered-program path and teach the
RD-Aspen TF-M Strata driver to use it, or reduce the QEMU/SystemC MMIO
transaction cost without bypassing CFI command-state semantics.

### 2026-05-26 Short Runtime Recheck

The current short-timeout evidence now separates fresh writable-flash behavior
from persisted deploy-flash behavior. This avoids treating a no-copy boot that
benefits from already-initialized flash state as proof that first-boot
writable flash is fast enough.

| Evidence | Result |
| --- | --- |
| `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; the focused Strata flash component test still succeeds with the current model. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-baseline-recheck-20260526-v1/progress-report.md` | Fresh writable-flash, range-limited-DMI GDB sample opened RSE/AP ports and host GDB captured QBox/SystemC/QEMU backtraces, but `Linux version` was not reached within 140.044 seconds. |
| `gdb-linux-marker-range-dmi-baseline-recheck-20260526-v1/probes/tfm-s-later.txt` | RSE/TF-M sampled in `tfm_its_remove()` -> `Driver_FLASH0_EraseSector()` -> `cfi_strataflashj3_erase()` -> `erase_block()` -> `nor_byte_program()` -> `nor_send_cmd_byte()`, confirming the first-boot ITS/PS erase/writeback hot path. |
| `gdb-linux-marker-range-dmi-baseline-recheck-20260526-v1/probes/ap-secure-services-later.txt` | AP SE-Proxy sampled in `secure_storage_ipc_set()` -> `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read(channel=127)`, so AP is waiting for RSE secure-storage service progress rather than blocked before secure-service dispatch. |
| `gdb-linux-marker-range-dmi-baseline-recheck-20260526-v1/run/rse-strata-stats.json` | Quantifies the fresh writable-flash bottleneck at the sample: `write_accesses=5200000`, `word_program_cmds=866667`, `program_ops=866667`, `compat_ff_sector_erase_ops=1098`, `sector_erase_bytes=4497408`, and `backing_write_ops=584661`. |
| `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-nocopy-passcheck-20260526-v1/progress-report.md` | No-copy range-limited-DMI GDB control opened RSE/AP ports and sampled after 100.032 seconds without reaching `Linux version`; TF-M was already in `psa_wait_thread_fn_call()` and Strata stats recorded `backing_write_ops=0`. |
| `build/qbox-fvp-rd-aspen/rse-runtime-nocopy-postlogin-20260526-v1/result.json` | Tight 210-second no-copy runtime reports `passed=true` with `timed_out=true`, no fatal fail patterns, RSE boot markers, RSE/SCP handoff markers, measured boot through `BL_33`, and Linux login marker present, but post-login commands were not sent before the cap. |
| `build/qbox-fvp-rd-aspen/rse-runtime-nocopy-postlogin-20260526-v2/result.json` | No-copy runtime with a 260-second runner cap reports `passed=true`, `timed_out=false`, Linux login and root prompt present, and post-login probe `complete=true` with `done_marker=true`. |
| `rse-runtime-nocopy-postlogin-20260526-v2/result.json` post-login probe | Driver-pattern checks are all true: `arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`, and `virtio`. Return codes include `arm_si_rproc_modprobe_rc=0`, `rpmsg_ns_modprobe_rc=0`, `virtio_rpmsg_bus_modprobe_rc=0`, `rpmsg_net_modprobe_rc=0`, and `ethsi1_iplink_rc=0`. |
| `rse-runtime-nocopy-postlogin-20260526-v2/qbox-primary-console.log` | Linux reaches `Linux version 6.18.5-rt3-yocto-preempt-rt`, `systemd 257.4`, SMMU v3 probe, virtio devices, SI remoteproc attach, `virtio_rpmsg_bus virtio6: rpmsg host is online`, `ethsi1`, multi-user, root shell, and the `__QBOX_PROBE_DONE__` marker. |
| `rse-runtime-nocopy-postlogin-20260526-v2/qbox-secure-console.log` | Secure world reaches SCMI driver initialization and logs SMM Gateway discovery fallback plus the expected first-boot SE-Proxy secure-storage `-140` remove-missing-object messages. No SE-Proxy panic appears in this bounded no-copy run. |
| `rse-runtime-nocopy-postlogin-20260526-v2/rse-strata-stats.json` | Even the no-copy login run executes a large RSE Strata program workload: `write_accesses=7200000`, `word_program_cmds=1200000`, `program_ops=1200000`, `compat_ff_sector_erase_ops=1298`, and `backing_write_ops=0`. |

Current conclusion: QBox currently reaches Linux login, root shell, and the
major Linux driver probes when it reuses the deploy flash state without
write-through copies, but the first-boot writable-flash path remains too slow
under the short FVP-like window. The limiting path is not AP release, Linux GDB
setup, basic AP-RSE MHU wiring, or the current Linux driver surface; it is the
firmware-visible TF-M ITS/PS CFI byte-program erase/writeback stream through
the SystemC Strata flash model. Secure-service userspace validation, FWU bank
selection, and cross-reboot writable-flash persistence remain open.

### 2026-05-26 Secure-Service CC3XX PKA Recheck

The current no-copy secure-service run reaches Linux and the post-login driver
surface, but the PSA userspace tests still time out. A focused CC3XX PKA trace
and TF-M source inspection narrow the post-login IAT timeout without treating
the earlier pre-Linux PKA traffic as proof of the later userspace path.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-pka-trace-20260526-v1/result.json` | No-copy runtime completes with `passed=true`, `timed_out=false`, Linux login/root markers, post-login probe `complete=true`, and driver-pattern checks true. Secure-service binaries `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` are present, but all return `124` under the 3-second per-command cap. |
| `rse-secure-service-cc3xx-pka-trace-20260526-v1/qbox-primary-console.log` | Linux reaches `Linux version 6.18.5-rt3-yocto-preempt-rt`; the secure-service diagnostic marker is printed; IAT times out before a test result, while ITS prints two `TEST RESULT: PASSED` lines before timing out. |
| `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=pka-opcode QBOX_RDASPEN_CC3XX_TRACE_LIMIT=20000 ... --secure-service-probe-timeout 3` | The trace reaches the configured CC3XX limit before the IAT userspace test, so this artifact proves heavy pre-Linux/RSE PKA traffic but does not capture the late IAT opcode stream. |
| `scripts/analyze_qbox_cc3xx_trace.py` | Adds a reusable CC3XX trace decoder for `qbox-platform.log`, including PKA opcode decoding, offset counts, first/last opcode windows, JSON output, and trace-limit detection. |
| `rse-secure-service-cc3xx-pka-trace-20260526-v1/cc3xx-pka-summary.txt` | Decodes `20000` CC3XX trace entries and reports `trace_limit_reached: True`, `pka_opcode_count: 8063`, with dominant ops `AND_TST0_CLR0=2317`, `MODMUL=2311`, `MODSUB_MODDEC_MODNEG=1676`, and `MODADD_MODINC=1150`. |
| `build/qbox-fvp-rd-aspen/gdb-secure-service-iat-sample-20260526-v1/probes/ap-secure-services-later.txt` | During IAT sampling the AP SE-Proxy side is waiting on the RSE response in `mhu_v3_x_doorbell_read(channel=127)` under `rse_comms_platform_invoke()`. |
| `gdb-secure-service-iat-sample-20260526-v1/probes/tfm-s-later.txt` | The RSE TF-M secure runtime is active in the IAT crypto path: `cc3xx_lowlevel_rng_get_random()` -> `cc3xx_lowlevel_pka_set_to_random_within_modulus()` -> `cc3xx_lowlevel_ecdsa_sign()` for `CC3XX_EC_CURVE_SECP_256_R1`. |
| TF-M CC3XX source inspection | `cc3xx_lowlevel_pka_set_to_random_within_modulus()` repeatedly calls DRBG random generation and accepts the candidate only when `cc3xx_lowlevel_pka_less_than(r0, CC3XX_PKA_REG_N)` observes `PKA_STATUS.ALU_SIGN_OUT`. The QBox CC3XX model implements that less-than status via the `SUB_DEC_NEG` borrow/sign path, so the current evidence does not indicate a missing basic compare bit. |
| FVP comparison artifacts `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/` | FVP completes `psa-iat-api-test` and `psa-its-api-test` with rc `0` under the same short cap, so the QBox gap is still real and local to the modeled RSE crypto/service path rather than image content for those two binaries. |

Current conclusion: the post-login secure-service gap is now split from the
first-boot Strata writeback gap. Basic AP-RSE MHU propagation and Linux driver
probing still work, but IAT remains bounded in RSE TF-M CC3XX-backed ECDSA/RNG
work while AP SE-Proxy waits for the response. The immediate next step is a
late-gated or much higher-limit CC3XX PKA trace, or a semantics-preserving
acceleration of the CC3XX PKA/ECDSA path, not another broad MHU wiring change.

### 2026-05-26 Late-Gated CC3XX Trace And Cache Recheck

The late trace gate now captures the userspace IAT/attestation PKA window
without spending the short runtime window on earlier boot-time CC3XX traffic.
The remaining secure-service gap is no longer classified as missing Linux
driver setup or basic AP-RSE MHU discovery.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/cc3xx/include/cc3xx.h` | Adds `trace_skip` and `m_trace_seen_count` so trace output can start after a configured number of matching CC3XX events. It also caches the PKA modulus value and invalidates that cache on PKA SRAM reset, direct PKA SRAM writes, PKA register-0 remap, and result writes overlapping the modulus register. |
| `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` | Wires `QBOX_RDASPEN_CC3XX_TRACE_SKIP` to both RSE CC3XX instances. The value is read directly at object construction so the Lua main chunk stays below the local-variable limit; `luac -p` passes. |
| `tools/qbox/tests/components/cc3xx/cc3xx-tests.cc` | Adds `PkaTraceSkipCanGateEarlyOpcodes` and `PkaModulusCacheInvalidatesOnModulusRewrite` focused regressions. |
| `timeout 120s cmake --build tools/qbox/build --target cc3xx-tests platforms-vp --parallel 8` | Passed after the trace-skip and modulus-cache changes. |
| `timeout 120s ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-skip-trace-20260526-v2/` | `QBOX_RDASPEN_CC3XX_TRACE_SKIP=20000` captured the next `12000` matching CC3XX trace events but timed out before Linux. The artifact proves the skip gate works and shows the next window is still pre-Linux secure-runtime measured-boot traffic, with `pka_opcode_count=5071`. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-skip-trace-20260526-v3/result.json` | With `QBOX_RDASPEN_CC3XX_TRACE_SKIP=80000` and `QBOX_RDASPEN_CC3XX_TRACE_LIMIT=4000`, QBox reaches Linux login/root and completes the post-login probe. Driver return codes remain good, including `arm_si_rproc_modprobe_rc=0`, `rpmsg_ns_modprobe_rc=0`, `virtio_rpmsg_bus_modprobe_rc=0`, `rpmsg_net_modprobe_rc=0`, and `ethsi1_iplink_rc=0`. Secure-service userspace tests still return `124` under the 3-second per-command cap. |
| `rse-secure-service-cc3xx-skip-trace-20260526-v3/cc3xx-pka-summary.txt` | Captures the late IAT/attestation PKA window: `trace_entries=4000`, `trace_limit_reached=True`, `pka_opcode_count=1681`, with `AND_TST0_CLR0=491`, `MODMUL=491`, `MODSUB_MODDEC_MODNEG=351`, `MODADD_MODINC=236`, `XOR_FLIP0_INVERT_COMPARE=89`, and `ADD_INC=23`. |
| `rse-secure-service-cc3xx-skip-trace-20260526-v3/qbox-rse.log` | The RSE log reaches TF-M runtime and repeatedly prints `[Attest] ... PSA_IOT_PROFILE_1` while the AP userspace IAT test is active, confirming the late trace is aligned with the attestation path rather than only early boot validation. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-cache-probe-20260526-v1/result.json` | No-trace cache recheck still reaches Linux/root/post-login and all Linux driver probes, but `psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` still return `124` with a 3-second per-command cap. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-cache-probe-15s-20260526-v1/qbox-primary-console.log` | Raising only the per-command cap to 15 seconds shows progress but not completion. IAT reaches checks 1..11 and logs `arm_tstee arm-ffa-4: invoke_func rpc status: -6`; ITS passes tests 401 and 402, reaches insufficient-space cleanup in test 403, then times out; PS passes test 401 before timing out. |

Current conclusion: the immediate post-login secure-service blocker is a
combination of slow or incomplete secure-service request completion and
AP-RSE service backpressure, with late CC3XX PKA/ECDSA traffic proven in the
IAT path. The cache optimization is safe and tested, but it is not sufficient
to match the FVP short-command behavior. V038/T061-T064/T076 remain open until
IAT/ITS/PS userspace tests complete with FVP-like short caps and fresh
writable-flash/FWU persistence are proven.

### 2026-05-26 AP/SI Synthetic MHU TXDone/PBX IRQ Recheck

The Linux `arm-mhuv3-mailbox` warning seen in the 15-second secure-service
cache probe was on the AP-to-SI CL1 service-model doorbell at AP logical
`0x400b0000`, not on the AP-to-RSE secure-service bridge. The service-modeled
AP/SI path injects a remoteproc/RPMsg name-service response without a real
remote MHU peer, so the model must synthesize both the sender-side transfer
completion and the PBX combined IRQ that Linux uses for interrupt-driven
`txdone_irq`.

| Evidence | Result |
| --- | --- |
| `tools/qbox/systemc-components/mhuv3_stub/include/mhuv3_stub.h` | Adds `complete_synthetic_postbox_transfer()` and calls it after AP/SI CL1 doorbell auto-ack and after RPMsg-NS scheduling. The helper now queues completion on a SystemC event with the `synthetic_txdone_delay_ns` CCI parameter, traces both `postbox-synthetic-tx-complete-scheduled` and `postbox-synthetic-tx-complete`, then clears the corresponding PBX doorbell status. Empty transfer-ack IRQ suppression is limited to the AP/SI CL1 doorbell pair so MBX startup clears do not create PBX IRQs without a Linux `pending_db`, while other doorbell users keep their previous ACK behavior. |
| `tools/qbox/tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Extends the AP/SI CL1 test to bind the SI CL1 PBX IRQ, enable PBX `DBCW_INT_EN`, assert an empty paired MBX clear does not raise PBX `DBCW_INT_ST`, assert PBX `DBCW_ST` remains set until the deferred completion fires, and assert `DBCW_INT_ST` plus the IRQ output toggle for both the `0x8` resource-table seed kick and the `0x1` RPMsg host kick. |
| `git -C tools/qbox diff --check -- systemc-components/mhuv3_stub/include/mhuv3_stub.h tests/components/mhuv3_stub/mhuv3_stub-tests.cc` | Passed. |
| `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 8` | Passed after adding the synthetic txdone/PBX IRQ regression. |
| `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` | Passed. |
| `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` and `cmake --build tools/qbox/build --target platforms-vp --parallel 8` | Passed, proving the Lua platform still parses and the rebuilt platform binary includes the MHU model update. |
| `git -C tools/qbox diff --check && timeout 180s cmake --build tools/qbox/build --target mhuv3_stub-tests platforms-vp --parallel 8 && timeout 60s ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure` | Passed after the final deferred-completion and AP/SI-only ACK suppression update. |
| `build/qbox-fvp-rd-aspen/rse-mhu-synthetic-txdone-postlogin-20260526-v1/result.json` | Earlier status-only txdone runtime reached Linux and the SI CL1 remoteproc/RPMsg/ethsi1 surface but timed out before the formal post-login probe. Its primary console did not contain the mailbox warning in that bounded window, but it did not exercise the later 20-second secure-service IAT window. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-txdone-20s-20260526-v1/result.json` | The next 20-second secure-service probe reached Linux, completed the driver module probes, started `psa-iat-api-test`, and then timed out. Driver return codes remained good, including `arm_si_rproc_modprobe_rc=0`, `virtio_rpmsg_bus_modprobe_rc=0`, `rpmsg_ns_modprobe_rc=0`, `rpmsg_net_modprobe_rc=0`, and `ethsi1_iplink_rc=0`. |
| `rse-secure-service-mhu-txdone-20s-20260526-v1/qbox-primary-console.log` | Reproduced `arm-mhuv3-mailbox 400b0000.mhu: Try increasing MBOX_TX_QUEUE_LEN` before and during the IAT run, followed by an RCU stall. This proved that status-only synthetic txdone was insufficient because the PBX combined IRQ was not delivered. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-irq-20s-20260526-v1/result.json` | Post-PBX-IRQ runtime timed out with `blocker=qbox_platform_timeout` before Linux login and before any post-login probe commands were sent. It is useful build/runtime smoke evidence but not acceptance proof for warning removal. |
| `rse-secure-service-mhu-pbx-irq-20s-20260526-v1/qbox-primary-console.log` | Reached U-Boot EFI handoff, including `EFI: MM partition ID 0x8006` and `Booting /\EFI\BOOT\BOOTAA64.EFI`, but did not reach `Linux version` before the cap. No mailbox-warning conclusion can be drawn from this artifact. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-deferred-txdone-20260527-v1/result.json` | Deferred synthetic txdone alone was runtime-safe: the run reached Linux, completed post-login probes, and kept SI CL1/RPMsg driver return codes at 0, but it still logged AP/SI PBX spurious IRQ and mailbox-queue warnings. This narrowed the remaining issue to empty ACK generation from AP/SI CL1 startup/cleanup clears. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-doorbell-ack-20260527-v1/result.json` and `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-ap-si-only-20260527-v1/result.json` | No-copy writable-flash reruns after earlier failed experiments timed out before Linux login, so they are not acceptance proof. They show that repeated shared-flash runtime experiments can contaminate the deploy-state path; use per-run writable flash copies when collecting this MHU evidence unless the shared deploy images are reset first. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/result.json` | Acceptance runtime. The run omits `--no-copy-writable-flash`, uses per-run writable flash copies, returns `passed=true`, `timed_out=false`, `blocker=null`, and completes the post-login probe. Driver patterns for `arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`, and `virtio` are true; return codes for `arm_si_rproc_modprobe`, `virtio_rpmsg_bus_modprobe`, `rpmsg_ns_modprobe`, `rpmsg_net_modprobe`, and `ethsi1_iplink` are 0. |
| `rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/qbox-primary-console.log` | Contains zero `Spurious IRQ on PBX channel`, zero `Try increasing MBOX_TX_QUEUE_LEN`, and zero RCU-stall reports while reaching Linux login and the secure-service probe window. |
| `rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/mhuv3-trace.log` | Records 32 exact `postbox-synthetic-tx-complete-scheduled` events and 32 matching exact `postbox-synthetic-tx-complete` events for the AP/SI CL1 service-modeled kicks, including the `0x8` resource-table seed, `0x1` RPMsg host kick, and repeated `0x2` notifications, with the configured 1000 ns delay. |

Current conclusion: the AP/SI CL1 sender-completion and PBX IRQ warning path is
fixed by deferred synthetic txdone plus AP/SI-only empty-ACK suppression, and it
now has both focused component coverage and a Linux/post-login copy-flash
runtime proof. The secure-service userspace binaries still return 124 under
the bounded 8-second probe, with `se_proxy_error` and `smm_gateway_error`
observed, so V038/T061-T064/T076 remain open for secure-service completion and
FWU persistence rather than for the AP/SI mailbox-warning path.

### 2026-05-27 Secure-Service 30-Second Probe Recheck

The Arm Zena CSS secure-services documentation describes the Primary Compute
path as Linux userspace `libts`/`libpsats` over FF-A into the SE-Proxy and SMM
Gateway secure partitions, with SE-Proxy forwarding RSE-backed services over
AP-to-RSE MHUv3. After the AP/SI CL1 MHU fix, QBox was rechecked with a
bounded but less aggressive 30-second per-command cap to distinguish missing
transport from slow secure-storage work.

| Evidence | Result |
| --- | --- |
| `arm-zena-css/documentation/design/secure_services.rst` | Documents that SE-Proxy receives Normal-world secure-service requests and forwards them to RSE runtime services over MHUv3; SMM Gateway stores UEFI variables through the RSE Protected Storage service via SE-Proxy. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-30s-notrace-20260527-v1/result.json` | `passed=true`, `timed_out=false`, `blocker=null`, post-login probe complete, and all Linux driver patterns true (`arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`, `virtio`). |
| `rse-secure-service-30s-notrace-20260527-v1/qbox-primary-console.log` | `psa-iat-api-test` prints the PSA Architecture Test Suite pass summary and returns `secure_psa_iat_api_test_rc:0`. This validates T062 on QBox. |
| `rse-secure-service-30s-notrace-20260527-v1/qbox-primary-console.log` | `psa-its-api-test` passes ITS tests 401 through 410, reports `TOTAL PASSED : 10`, `TOTAL FAILED : 0`, and returns `secure_psa_its_api_test_rc:0`. |
| `rse-secure-service-30s-notrace-20260527-v1/qbox-primary-console.log` | `psa-ps-api-test` passes PS tests 401 and 402, enters PS test 403 (`Insufficient space check`), then returns `secure_psa_ps_api_test_rc:124` at the 30-second cap. |
| `rse-secure-service-30s-notrace-20260527-v1/qbox-primary-console.log`, `qbox-secure-console.log`, `qbox-rse.log` | All contain zero `Spurious IRQ on PBX channel`, zero `Try increasing MBOX_TX_QUEUE_LEN`, and zero RCU-stall reports. |
| `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/terminal_ns_uart0_5004.log` | FVP comparison completes IAT and ITS with rc 0 under the 8-second cap. Its PS run reaches PS test 403 under that cap. |
| `build/fvp-boot-logs/rse-secure-service-ps-probe-20260525-v1/terminal_ns_uart0_5004.log` | The PS-only FVP probe progresses through PS test 409 before the host-side post-login cap, so QBox's remaining PS gap is still real even though IAT and ITS now pass. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-30s-probe-20260527-v1/result.json` | The same 30-second probe with `QBOX_RDASPEN_MHU_TRACE_LIMIT=60000` timed out before Linux. The MHU trace captured thousands of AP-RSE accesses, so high-volume MHU tracing is useful for protocol inspection but distorts bounded runtime pass/fail timing. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `--secure-service-probe-tests` so the existing secure-service diagnostic can run `all`, `none`, or selected tests such as `ps` without changing the default all-test behavior. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed after adding secure-service test selection. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-60s-20260527-v1/result.json` | PS-only QBox runtime with `--secure-service-probe-tests ps` and a 60-second command cap returns `passed=true`, `timed_out=false`, completes post-login driver checks, and records `secure_service_tests:ps`. The only secure-service command return code is `secure_psa_ps_api_test_rc=124`. |
| `rse-secure-service-ps-only-60s-20260527-v1/qbox-primary-console.log` | PS-only execution passes PS tests 401 and 402, enters PS test 403 (`Insufficient space check`), and then times out at 60 seconds. This proves the remaining PS gap is not caused by IAT or ITS running first. |

Current conclusion: AP secure-world SE-Proxy transport to RSE is now proven for
Initial Attestation and Internal Trusted Storage userspace validation. T062 is
complete, and the ITS half of T063 is complete. The remaining secure-services
gap is Protected Storage completion: QBox reaches PS test 403 with no AP/SI
mailbox or Linux RCU warnings, and a PS-only 60-second run confirms the same
loss point without IAT/ITS preconditioning. It does not yet match the FVP
PS-only reference that reaches test 409 within the bounded host window.
Continue with the TF-M ITS/PS flash filesystem and Strata flash writeback path
rather than basic FF-A discovery, AP-RSE MHU routing, or AP/SI mailbox IRQ
delivery.

### 2026-05-27 Writable Flash Padding And PS Stats Recheck

The first PS-only stats run uncovered a separate writeback correctness bug:
the per-run raw flash images copied from deploy artifacts were shorter than
the QBox Strata flash apertures. The RSE raw image was 5,033,984 bytes while
the modeled RSE boot flash is 64 MiB, so PS/FWU writes above the image payload
could update in-memory flash state but fell outside the backing file used for
persistence evidence.

| Evidence | Result |
| --- | --- |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-stats-20260527-v1/qbox-platform.log` | Reproduced `remote_platform.rse_boot_flash unable to range backing_file=...`; this explains why a stats/no-copy-style run could reach PS test 403 while still lacking valid writeback coverage over the full modeled flash aperture. |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Pads copied RSE/AP writable flash images to the QBox model sizes before enabling writeback: RSE to `0x04000000` and AP flash to `0x08000000`, using erased byte value `0xff`. The helper avoids modifying source deploy images when `--no-copy-writable-flash` is used. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| Helper-level import/padding smoke test | Passed; a short raw file was extended with `0xff` bytes and preserved its original prefix. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-padded-stats-20260527-v1/summary.txt` | Records RSE flash padding from 5,033,984 bytes to 67,108,864 bytes and AP flash padding from 4,771,840 bytes to 134,217,728 bytes, both with `pad_erased_value="0xff"`. |
| `rse-secure-service-ps-only-padded-stats-20260527-v1/qbox-platform.log` and console logs | Contain no `unable to ... backing_file`, no `Spurious IRQ on PBX channel`, no `Try increasing MBOX_TX_QUEUE_LEN`, and no RCU-stall reports in the checked logs. |
| `rse-secure-service-ps-only-padded-stats-20260527-v1/result.json` | Runtime returned `passed=true`, `timed_out=false`, `blocker=null`, completed the post-login probe, and kept driver patterns true for `arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`, and `virtio`. |
| `rse-secure-service-ps-only-padded-stats-20260527-v1/rse-strata-stats.json` | Captures the PS-only Strata workload after padding: `write_accesses=16750000`, `word_program_cmds=2791667`, `program_ops=2791667`, `program_changed_bytes=2261678`, `compat_ff_sector_erase_ops=2034`, `sector_erase_bytes=8331264`, `backing_write_ops=2263712`, and `backing_write_bytes=10592942`. |
| `rse-secure-service-ps-only-padded-stats-20260527-v1/qbox-primary-console.log` | PS still passes tests 401 and 402, enters PS test 403 (`Insufficient space check`), and returns `secure_psa_ps_api_test_rc=124` at the 60-second command cap. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-nocopy-stats-20260527-v1/summary.txt` | No-copy/writeback-off control keeps the deploy RSE/AP flash images unmodified and records `pad_state=skipped_source_not_copied` with required-but-skipped padding of 62,074,880 bytes for RSE flash and 129,445,888 bytes for AP flash. |
| `rse-secure-service-ps-only-nocopy-stats-20260527-v1/result.json` | Runtime returned `passed=true`, `timed_out=false`, `blocker=null`, completed the post-login probe, kept all checked driver patterns true, and recorded `secure_psa_ps_api_test_rc=124`. |
| `rse-secure-service-ps-only-nocopy-stats-20260527-v1/rse-strata-stats.json` | With file writeback disabled, PS still performs a large CFI workload: `write_accesses=15750000`, `word_program_cmds=2625000`, `program_ops=2625000`, `program_changed_bytes=2114082`, `compat_ff_sector_erase_ops=1962`, and `sector_erase_bytes=8036352`, while `backing_write_ops=0` and `backing_write_bytes=0`. |
| `rse-secure-service-ps-only-nocopy-stats-20260527-v1/qbox-platform.log` and console logs | Checked for `unable to ... backing_file`, `Spurious IRQ on PBX channel`, `Try increasing MBOX_TX_QUEUE_LEN`, and RCU-stall reports; none were found. The primary console still enters PS test 403 (`Insufficient space check`). |

Current conclusion: per-run writable flash now covers the full RSE/AP Strata
apertures used by the QBox platform, so future PS/FWU persistence evidence is
not limited by the short deploy image length. This does not close Protected
Storage completion: the padded PS-only run still times out in PS test 403, but
the no-copy control shows the same timeout with `backing_write_ops=0`. The
remaining gap is therefore the firmware-visible Protected Storage/Strata CFI
command workload and service completion, not host backing-file range coverage
or writeback cost.

### 2026-05-27 Focused PSA PS Test-List Runner

The PSA Architecture Test Suite wrapper supports `-t <test_list>`, so the QBox
runner now exposes a PS-specific filter for short Protected Storage debug
runs. This does not change default secure-service coverage; it only narrows
`psa-ps-api-test` when `--secure-service-probe-tests ps` is selected.

| Evidence | Result |
| --- | --- |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `--secure-service-ps-test-list`, validates entries such as `test_403;`, quotes the semicolon-bearing list, and emits `timeout <n>s psa-ps-api-test -t 'test_403;'` for PS-only secure-service probes. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| Helper-level import/command-generation check | Passed; `parse_psa_test_list('test_403;')` is accepted, `test_403` without the semicolon is rejected, and generated commands contain `psa-ps-api-test -t 'test_403;'`. |
| `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --help \| rg -n "secure-service-ps-test-list\|secure-service-probe-tests\|secure-service-probe-timeout"` | Passed and shows the new CLI option with the existing secure-service probe controls. |
| `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8` and `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure` | Passed; `strata_flash_j3-tests` completed successfully. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps403-filter-20260527-v1/result.json` | Stats-enabled no-copy run with `--secure-service-ps-test-list 'test_403;'` timed out before Linux login (`blocker=qbox_platform_timeout`, `platform_returncode=-15`), so it is not PS test 403 pass/fail evidence. |
| `rse-secure-service-ps403-filter-20260527-v1/rse-strata-stats.json` | At timeout the RSE boot-flash model already recorded `write_accesses=500000`, `word_program_cmds=83334`, `program_ops=83333`, `compat_ff_sector_erase_ops=317`, and `backing_write_ops=0`, reinforcing that short stats-enabled windows are dominated by pre-Linux Strata work. |

Current conclusion: the runner can now isolate PS test 403 without running
tests 401 and 402 first, but the first stats-enabled filtered attempt did not
reach the post-login probe. Use the new filter with stats disabled or a longer
host cap when collecting PS 403-specific pass/fail evidence. The open fidelity
gap remains Protected Storage completion through the firmware-visible Strata
CFI workload.

### 2026-05-27 AP Auto-Enable For Probe Runs

Post-login, secure-service, and FWU probes all require the Primary Compute AP
CPUs and Linux console. The runner now enables AP CPUs automatically for those
probe modes so short validation runs cannot accidentally launch an RSE-only
platform and then wait for a Linux login that can never appear.

| Evidence | Result |
| --- | --- |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `probe_requires_ap_cpus()` and sets `QBOX_RDASPEN_ENABLE_AP_CPUS=true` in `qbox_env()` for `--post-login-probe`, `--secure-service-probe`, and `--fwu-probe`. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| Helper-level import smoke | Passed; direct `qbox_env()` invocation with post-login and secure-service probes produced `QBOX_RDASPEN_ENABLE_AP_CPUS=true`. |
| `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-ap-auto-enable-smoke-20260527-v1/qbox-platform.log` | A 20-second runtime smoke launched without external AP env and logged `ap cpus:      4`. The run intentionally timed out before boot completion, so it is only AP auto-enable evidence. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps403-filter-nostats-ap-20260527-v1/result.json` | AP-enabled, no-copy, stats-disabled filtered PS 403 run timed out before Linux at U-Boot/SMM Gateway with `blocker=qbox_platform_timeout`; no login or PS command was sent. |
| `build/qbox-fvp-rd-aspen/rse-secure-service-ps403-filter-copyflash-20260527-v1/result.json` | AP-enabled, per-run copied flash filtered PS 403 run also timed out before Linux at U-Boot/SMM Gateway. This is pre-Linux secure-storage timing evidence, not a PS 403 pass/fail result. |

Current conclusion: probe runs are now guarded against an AP-disabled launch
configuration. The two filtered PS 403 attempts after this cleanup did not
reach Linux, while earlier unfiltered PS-only runs did reach test 403. Treat
this as additional evidence that U-Boot/SMM Gateway secure-storage timing and
the later PS flash workload both remain fidelity risks; do not count these
filtered attempts as PSA PS test results.

### 2026-05-27 Runner Elapsed-Time Metadata

Short QBox/FVP comparison runs now need exact host elapsed-time evidence
because small timeout changes can move a run from Linux login to the
U-Boot/SMM Gateway secure-storage window. The QBox RSE runner now records the
runtime duration and the original runner argv in generated artifacts.

| Evidence | Result |
| --- | --- |
| `scripts/run_qbox_fvp_rd_aspen_rse.py` | Adds `runtime_elapsed_s` to `result.json`, prints it in `summary.txt`, and records `runner_argv` so later artifact triage can recover the exact runner-level options rather than only the generated `platforms-vp` command. |
| `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py` | Passed. |
| `build/qbox-fvp-rd-aspen/rse-runner-elapsed-smoke-20260527-v1/result.json` | Three-second smoke run intentionally timed out with `blocker=qbox_platform_timeout` and records `runtime_elapsed_s=3.0408413260011002`; `runner_argv` contains `--timeout`. |
| `build/qbox-fvp-rd-aspen/rse-runner-elapsed-smoke-20260527-v1/summary.txt` | Prints `runtime_elapsed_s: 3.041`, proving the human-readable summary carries the same timing signal. |

Current conclusion: future PS/SMM Gateway rechecks can be judged with exact
runner-level timeout and elapsed-time metadata. This is diagnostic evidence;
it does not change QBox platform behavior or close the remaining Protected
Storage completion gap.

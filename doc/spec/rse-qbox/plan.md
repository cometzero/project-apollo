# RSE QBox Implementation Plan

Created: 2026-05-20

## Strategy

Implement RSE as a real QBox subsystem in staged increments. Each stage must
leave the existing primary-compute direct boot usable while adding a deeper
firmware-mediated boot path. The direct boot path remains a development and
regression aid; it is not the final fidelity target.

## Phase 0: Baseline And Evidence Capture

### Objectives

- Freeze the current FVP and QBox evidence for the active RD-Aspen CFG2 build.
- Create a source-of-truth ledger for RSE-visible addresses, IRQs, firmware
  artifacts, console markers, and expected test patterns.

### Work

1. Capture `.config.yaml` and generated deploy artifact paths.
2. Run or collect file-backed FVP boot logs with:
   `scripts/run/runfvp_log_boot.py`.
3. Record RSE console markers from:
   `sw-ref-stack/test_automation/tests/test_bsp_demos/test_00_rse.py`.
4. Record FVP image injection parameters from:
   `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`.
5. Record current QBox direct-boot component state from:
   `tools/qbox/platforms/fvp-rd-aspen/conf.lua`.

### Exit Criteria

- `doc/spec/rse-qbox/evidence.md` records the baseline RSE evidence table,
  FVP/QBox artifact paths, and required comparison markers.
- FVP reference logs are stored under `build/qbox-fvp-rd-aspen/` or another
  generated evidence directory.
- Current QBox direct-boot behavior is unchanged.

## Phase 1: RSE Boot Skeleton

### Objectives

- Add an optional RSE-oriented QBox mode.
- Boot a Cortex-M55 RSE execution context from generated RSE ROM/flash/OTP
  artifacts far enough to produce early TF-M logs.

### Work

1. Inspect and validate existing `cpu_arm_cortexM55` and `nvic_armv7m`
   build targets. The NVIC source directory is named `armv7m_nvic`, but the
   CMake build target is `nvic_armv7m`.
2. Instantiate the Cortex-M55 through the existing `RemoteCPU` wrapper because
   direct Lua nested binding of `rse_cpu.nvic.mem` does not bind the CPU-local
   NVIC/SCS socket in `platforms-vp`. Use:
   - `QemuInstance` target string `AARCH64`,
   - `RemotePass` from the generic `platforms-vp`,
   - `RemoteCPU` from `platforms/cortex-m55-remote`,
   - pass initiator sockets bound to the RSE local router target socket,
   - internal `cpu_0.cpu.nvic.mem` mapped at `0xE000E000` size `0x10000`.
3. Add an RSE local router, ROM, SRAM, OTP, flash, UART, and system-control
   placeholder components.
4. Add Lua configuration parameters for RSE image paths:
   - `QBOX_RDASPEN_RSE_ROM`
   - `QBOX_RDASPEN_RSE_FLASH`
   - `QBOX_RDASPEN_RSE_OTP`
   - `QBOX_RDASPEN_AP_FLASH`
   - `QBOX_RDASPEN_PROVISIONING_BUNDLE`
5. Use the reviewed initial skeleton addresses:
   - RSE ROM secure base `0x11000000`, size `0x20000`,
   - RSE boot flash secure base `0xB0000000`, size `64 MiB`,
   - RSE VM0 secure base `0x31000000`,
   - RSE VM1 secure base `0x31040000`,
   - provisioning bundle at `VM1_BASE_S + 0x20000 = 0x31060000`,
   - RSE host UART local aliases `0x6FF00000` and `0x7FF00000`.
6. Add a file-backed RSE console log path to the QBox run helper using
   `char_backend_file` with `read_file`, `write_file`, and `baudrate`
   parameters.
7. Preserve the existing direct Linux boot mode as default until the
   RSE-oriented mode can boot Linux.

### Exit Criteria

- The RSE subsystem builds.
- RSE mode emits an RSE UART log.
- The log reaches at least the TF-M BL1_1 startup marker or a documented,
  reproducible missing-register blocker.

### Current Phase 1 Result

The skeleton starts the generated RSE ROM through `RemoteCPU`. With the limited
CC3XX, DTCM/ITCM alias, DMA350, RSE system-control, ATU translation, LCM/OTP,
SAM, KMU, Integrity Checker, and host PPU models added on 2026-05-21, the
previous fatal `0xE000E008` NVIC/SCS path, the later `0x501541c4` CC3XX Data
Abort, the BL1_1 DMA erase/fill timeout, the `0x58021100` reset-syndrome
fault, the ATU/SAM register gaps, and the BL1_1 `__cmsis_start` copy-table
timeout are no longer the first blockers.

The latest modular-PKA RSE runtime emits TF-M UART markers through BL1_1,
BL1_2, BL2 validation, BL2 entry, and BL2 PSA Crypto initialization. KMU
destination-port export and CC3XX AES-CMAC behavior are implemented far enough
for focused component tests and runtime CMAC tags. The `rse_kmu` model also
seeds hardware slots from the LCM OTP hardware-key area in
`rse-otp-image.img`, and runtime trace evidence shows non-zero
`KMU_HW_SLOT_KCE_CM` words exported to CC3XX. The previous decrypt failure was
caused by passing QBox a gzip-compressed flashloader input; the runner now
creates a per-run raw flash image for `gs_memory`.

The previous post-decrypt BL1_2 image-signature validation failure was caused
by incomplete CC3XX SHA-256 multipart state save/restore. TF-M restores
`HASH_H[0..7]` and `HASH_CUR_LEN0/1` between PSA hash update and finish during
LMS/LMOTS validation; QBox now preserves those registers across
`HASH_OPERATION` boundaries. Historical host-PPU evidence reached SI CL0
pre-load completion and primary/secondary slot version output with an earlier,
less faithful PKA path. With the current modular-PKA CC3XX model, runtime
reaches `BL2 image validated successfully`, `Jumping to BL2`, BL2's
`Starting bootloader` marker, `PSA Crypto init done, sig_type: EC-P256`, SI
CL0 pre-load completion, and primary/secondary slot version output. A focused
`QBOX_RDASPEN_CC3XX_TRACE_FILTER=pka` run shows no later PKA traffic after the
early ADD/SUB setup sequence. The follow-up `0x7540a000` exception was traced
to RSE ATU range matching: an address above an enabled region's exclusive end
underflowed the access-length check and incorrectly used the lower region's
offset pages. The ATU model now rejects `logical >= region_end` before
translation arithmetic; runtime evidence translates `0x7540a000` through
region 12 to `0x400002a600000` and reaches `host_si_pik`.

The post-SI-CL0 slot-version timeout is now narrowed to SI CL0 image 3 loading.
Default-path PC sampling maps the tail to `nor_cfi_reg_read()` and
`cfi_strataflashj3_read()` while copying from RSE flash. An opt-in
`QBOX_RDASPEN_ATU_DMI=true` run reaches the explicit MCUboot failure
`Image 3 RAM loading to 0x70083c00 is failed`, removes both slots, and reports
`Unable to find bootable image`. A host-window-filtered CC3XX DMA trace shows
no CC3XX transfer programmed for `0x70083c00`, and T019AE shows the active
generated TF-M build has `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`, so the current
failing path is not DMA350 `boot_dma_memcpy()`.

T019AF replaced the RSE boot-flash aperture with a `strata_flash_j3`
CFI/Strata command model and retained the same SI CL0 image 3 failure. The
T019AG then adds a per-run file-backed `host_si_cl0_sram` probe. It proves the
primary SI CL0 image is copied into the ATU-translated host-window destination:
header sample `0xffc00` maps to logical `0x70083c00`, code sample `0x0` maps
to logical `0x70084000`, and the reordered SRAM image matches RSE flash offset
`0x67000` for `0xb6b1e` bytes, exactly the MCUboot `boot_read_image_size()`
result. The remaining failure is therefore not `flash_area_read()`, the
header/code host-window layout, or slot removal/erase. Because the copied
payload still matches encrypted flash and the AES-KW TLV is present, the next
implementation step is to distinguish `boot_enc_load()` key unwrap from
`boot_enc_set_key()` before payload decrypt. Do not claim progress to
`BL2: SI CL0 post load start` until that split is backed by file logs.

## Phase 2: Image-Backed ROM, Flash, OTP, And Provisioning

### Objectives

- Replace simple memory placeholders with FVP-compatible boot media semantics.
- Let TF-M read the same generated images as FVP.

### Work

1. Implement or reuse a file-backed memory component for read-only ROM.
2. Implement or reuse file-backed flash with explicit writable/writeback mode.
3. Implement OTP/NVM behavior:
   - image-backed initial state
   - provisioning writes
   - lock-after-provision behavior required by TF-M
4. Load `combined_provisioning_message.bin` at RSE SRAM offset `0x20000`.
5. Support `VMADDRWIDTH=18`, reset syndrome, and DMA boot enable values as
   CCI/Lua parameters.

### Exit Criteria

- TF-M reaches the first image slot on the RSE console.
- OTP and flash writes are visible in deterministic local output files.
- Re-running with preserved writable images produces stable behavior.

## Phase 2A: Early RSE Crypto And Protection Blocks

### Objectives

- Replace the current missing-register blocker with modeled early TF-M hardware
  blocks before claiming BL1_1 log progress.
- Keep placeholder `gs_memory` use documented as temporary compatibility debt.

### Work

1. Implement or integrate a CC3XX/CRYPTOCELL model for the touched register
   path starting at `0x50154000`, first observed at write offset `0x1c4`.
   A limited early RNG/readiness model now exists and must be expanded from
   trace evidence rather than treated as full CRYPTOCELL coverage.
2. Expand the current DMA350 fill model from BL1_1 erase support to real
   copy, trigger, status, interrupt, and DMA ICS semantics.
3. Expand the current touched-register RSE system-control model from
   `reset_syndrome`, `reset_mask`, CPU wait, selected power/reset, and DMA boot
   register read/write behavior into real reset lifecycle, CPU hold/release,
   SWRESET, and DMA boot side effects.
4. Expand the current ATU translation model into complete page-boundary,
   fault-status, Safety Island verification, and default-safe DMI behavior;
   keep the direct host-UART alias documented as a temporary compatibility
   path until host UART access is fully ATU-backed.
5. Model the SIC MPC window at `0x50151000` before allowing TF-M to rely on
   memory-protection behavior.
6. Keep trace-driven expansion: every new missing register must be added with
   source evidence from TF-M, Arm documentation, or an existing open-source
   implementation.
7. Complete the BL1_2 crypto/key and validation path:
   - keep KMU destination-port writes covered by component tests,
   - keep CC3XX AES-CMAC tag generation covered by component tests,
   - keep OTP-backed `KMU_HW_SLOT_KCE_CM` hardware-slot loading covered by
     component and runtime trace evidence,
   - preserve the raw-flash conversion needed for the QBox
     `strata_flash_j3` boot-flash model,
   - preserve and extend the existing AES-CTR DMA test coverage,
   - preserve CC3XX SHA-256 multipart `HASH_H` and `HASH_CUR_LEN` state
     restore coverage for LMS/LMOTS validation.

### Exit Criteria

- The RSE skeleton progresses beyond the previous `0x501541c4` abort,
  DMA350 erase/fill timeout, `0x58021100` system-control fault, the first
  ATU/SAM register-programming gaps, and BL1_2 BL2 decrypt failure.
- The post-decrypt BL1_2 signature-validation failure is resolved with
  CC3XX SHA-256 multipart state coverage; the later modular-PKA
  `0x7540a000` HardFault is traced to ATU region-range underflow and fixed; and
  the active runtime blocker is narrowed back to the post-SI-CL0 slot-version
  path with the current CC3XX model.
- Any temporary register placeholder is identified in `result.json` fidelity
  labels and in `evidence.md`.

## Phase 3: RSE ATU Model

### Objectives

- Implement RSE secure and non-secure access windows into system address space.
- Support TF-M ATU programming and safety boot verification.
- Replace the current touched-register-only `rse_atu` bring-up model with a
  translation-capable model.

### Work

1. Build a `rse_atu` SystemC component with target and initiator sockets.
2. Decode ATU programming registers touched by TF-M.
3. Translate local RSE windows:
   - `0x6000_0000..0x6fff_ffff` for non-secure system access
   - `0x7000_0000..0x7fff_ffff` for secure system access
4. Implement fault handling for disabled, unmapped, out-of-range, and
   permission-denied accesses.
5. Add component-level tests for translation, access faults, and DMI
   invalidation.

### Exit Criteria

- TF-M ATU initialization no longer requires compatibility bypasses.
- Safety Island ATU verification reaches the same pass/fail behavior as FVP
  for the supported CFG2 boot path.

### Current Phase 3 Status

The `rse_atu` component now covers the ATUBC reset value, region register
writes, enabled secure/non-secure host-window translation, TLM initiator
forwarding, unmapped translation errors, explicit end-bound rejection to avoid
unsigned range underflow, optional translated DMI, DMI invalidation, and
component coverage for translation/fault behavior. T034B adds ATURAV
page-shift overflow rejection and translated-DMI range conversion guards while
preserving TF-M two's-complement negative add-values. Runtime evidence now
shows the BL2 SI PIK access at `0x7540a000` translating through region 12 to
`0x400002a600000`; the 2026-05-25 translated-DMI run reaches SI ATU regions
0..16, SI CL0 release/post-load, RSE runtime measured boot through `BL_33`,
and `first_failing_register_access: none`. Translated DMI is still gated behind
`QBOX_RDASPEN_ATU_DMI=true`, so Phase 3 is functionally past the current
Safety Island ATU verification path but not full fidelity. Remaining ATU work
is full page-boundary semantics, rich fault status, default-safe DMI behavior,
and deeper negative/fault injection evidence.

## Phase 4: MHUv3 Real Doorbell Model

### Objectives

- Replace hardcoded SCMI responses with a reusable MHUv3 PBX/MBX model.
- Preserve software-visible MHUv3 programming behavior for AP-RSE, RSE-SCP,
  and AP-SI paths.

### Work

1. Split current `mhuv3_stub` into:
   - reusable `mhuv3` register/channel model
   - optional compatibility responder used only by direct-boot mode
2. Implement PBX/MBX register behavior:
   - feature and channel count registers
   - doorbell set/status/clear
   - interrupt mask/status behavior
   - channel-to-peer delivery
3. Model shared-memory ordering with TLM accesses and explicit barriers where
   required by firmware behavior.
4. Add unit/component tests for AP-to-RSE, RSE-to-SCP, and SCP-to-RSE
   doorbells. The first tests should cover PBX feature/channel registers,
   PBX set to peer MBX status delivery, MBX mask/set/clear interrupt
   behavior, MBX clear to PBX transfer-ack behavior, multi-pair isolation,
   invalid address/command handling, and byte-width access behavior.
5. Wire the RSE and SCP sides into the RD-Aspen Lua platform.

### Exit Criteria

- RSE and SCP exchange SCMI doorbells without hardcoded platform responses.
- RSE console reports SCMI initialization and AP power-on success.
- Existing direct boot validation still passes with its compatibility mode.

## Phase 5: SCP Strategy And RSE-Oriented AP/SI Handoff

### Objectives

- Let RSE BL2 load SI CL0, SI CL1, AP BL2, and RSE Runtime images.
- Move AP startup from direct loader to firmware-mediated release.
- Make the SCP/Safety Island strategy explicit before claiming RSE-SCP
  fidelity.

### Work

1. Choose and document the MVP SCP strategy:
   - protocol-correct SystemC/TLM SCP service model, or
   - real Safety Island CL0/SCP-firmware execution.
2. If using the SCP service model, implement it as a separate component,
   likely `scp_service_model`, that receives MHUv3 doorbells, reads SCMI
   shared memory through TLM, validates channel status, flags, length, header,
   protocol, message ID, and token, writes SCMI responses, rings the response
   doorbell, and drives AP release/reset state. Do not hardcode
   unconditional success paths.
3. Add AP secure SRAM and AP secure flash mappings required by AP BL2 loading.
4. Add SI CL0/CL1 memory windows and reset control surfaces touched by RSE BL2.
   T019AI and later evidence supersede the earlier SI CL0 AES-KW unwrap
   blocker: the current path loads SI CL0, AP BL2, RSE runtime, BL31, OP-TEE,
   Linux, and reaches the login prompt. The remaining Safety Island gap is now
   SI CL1 runtime/remoteproc/RPMsg behavior, not SI CL0 image 3 loading.
5. Implement or model RSE-to-SCP power-on protocol.
6. Rework AP CPU startup so AP primary core is held until RSE/SCP releases it.
7. Re-enable EL3/secure-world expectations as needed for TF-A BL2/BL31,
   OP-TEE, and U-Boot handoff.

### Exit Criteria

- AP boot starts because of RSE/SCP handoff, not direct QBox loader state.
- The run report identifies the SCP strategy and fidelity label.
- RSE logs contain `RSE to SCP SCMI power on AP succeeded`.
- Primary Compute reaches Linux login through the firmware-mediated path.

### Current Phase 5 Result

The 2026-05-24 runtime
`build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/` satisfies the
firmware-mediated AP release and Linux-login portion of Phase 5. Later
AP-RSE bridge/IRQ and marker-focused runs also satisfy the FVP RSE runtime
notification and measured-boot marker portion. It is not yet full MVP
acceptance because the SI CL1 runtime/RPMsg peer remains service-model or
module-load evidence rather than a Linux-visible `ethsi1` channel:

- QBox reaches `fvp-rd-aspen login:` on the primary console.
- RSE logs include `Init SCMI comm to SCP succeeded`,
  `RSE to SCP SCMI power on AP succeeded`, and
  `Jumping to the first image slot`.
- AP secure console reaches BL31, SCMI driver init, PFDI monitor init,
  OP-TEE/SPMC, and BL33 measured boot output.
- Linux probes SMMUv3 and AP/SI MHUv3 SCMI successfully.
- Current marker run records `SCMI Comms subscribed to power state
  notifications`, `RT_0`, and measurements through `BL_33`.
- Remaining blocker classification: `si_cl1_remoteproc_rpmsg_gap`.

## Phase 6: Measured Boot And Secure Services

### Objectives

- Support the secure-service path expected by RD-Aspen Linux and firmware.
- Validate measured boot, initial attestation, protected storage, and UEFI
  variable storage behavior.

### Work

1. Validate measured boot log markers for:
   `BL1_2`, `BL2`, `SI_CL0`, `AP_BL2`, `RT_0`, `SECURE_RT_EL3`,
   `SECURE_RT_EL1_SPMD`, and `BL_33`.
2. Wire AP secure world to RSE through MHUv3 for SE-Proxy and SMM Gateway.
3. Validate protected storage backing for UEFI variables.
4. Add post-login probes for secure-service userspace tests when available.

### Exit Criteria

- `test_00_rse.py` equivalent checks pass from QBox logs.
- Secure partition and secure-service tests have QBox evidence or explicit
  unsupported gaps.

## Phase 7: Secure Firmware Update

### Objectives

- Support RD-Aspen capsule update and A/B bank selection behavior.

### Work

1. Model RSE flash and AP flash A/B banks.
2. Model FWU metadata and RSE private metadata storage sufficiently for TF-M.
3. Validate capsule application from VirtIO block 1.
4. Check RSE and TF-A logs for new-bank boot markers.

### Exit Criteria

- QBox logs show RSE attempting to boot image bank 1 after capsule update.
- TF-A logs show booting with the expected FIP partition.
- Writable flash artifacts preserve update state across reboot.

## Validation Ladder

Run the narrowest applicable command first:

```bash
git -C tools/qbox diff --check
cmake --build tools/qbox/build --target cpu_arm_cortexM55 nvic_armv7m --parallel 8
ctest --test-dir tools/qbox/build -R cortex_m55 --output-on-failure
cmake --build tools/qbox/build --target mhuv3_stub --parallel 8
cmake --build tools/qbox/build --target platforms-vp char_backend_file uart-pl011 loader --parallel 8
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py --timeout 900 --out-dir build/qbox-fvp-rd-aspen/<run-id>
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py --skip-build --pc-trace --pc-trace-interval 200 --pc-trace-limit 5000 --timeout 300 --out-dir build/qbox-fvp-rd-aspen/<run-id>
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py --fvp build/qbox-fvp-rd-aspen/<fvp-run> --qbox build/qbox-fvp-rd-aspen/<run-id>
./scripts/test/validate_qbox_fvp_rd_aspen_map.py
python3 scripts/run/run_qbox_fvp_rd_aspen_linux.py --timeout 600 --post-login-probe
./scripts/test/audit_qbox_fvp_rd_aspen_coverage.py
```

The RSE-specific helper and comparison script are the first validation
entrypoints. A helper result with an explicit blocker is valid gap evidence,
not boot success. No direct-boot helper result may be used as evidence for
RSE-oriented boot success.

## FVP-QBox Comparison Table

The first comparison script shall normalize timestamps, host paths, telnet port
numbers, and run-directory names. It shall compare these deterministic markers:

| Area | Required markers |
| --- | --- |
| RSE boot | `Starting TF-M BL1_1`, `Jumping to the first image slot` |
| RSE-SCP handoff | `Init SCMI comm to SCP succeeded`, `RSE to SCP SCMI power on AP succeeded` |
| measured boot | `BL1_2`, `BL2`, `SI_CL0`, `AP_BL2`, `RT_0`, `SECURE_RT_EL3`, `SECURE_RT_EL1_SPMD`, `BL_33` |
| AP release | AP primary core starts only after RSE/SCP release evidence |
| Linux boot | primary console reaches configured login or shell prompt |
| reset/poweroff | SCMI reset and shutdown notification markers when those scenarios are run |

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| QBox `cpu_arm_cortexM55` cannot execute generated TF-M image directly | Blocks true RSE boot | Validate with minimal RSE ROM first; inspect QEMU M-profile machine requirements; consider remote CPU pattern |
| Direct M55 Lua wiring is syntactically valid but runtime boot is unproven | False skeleton confidence | Treat early runs as skeleton evidence only until TF-M markers appear |
| RSE host UART is accessed through ATU aliases | Missing console output | Map initial UART alias for skeleton, then replace with ATU-backed path |
| Generic memory loading hides OTP/flash semantics | Provisioning and FWU failures | Keep loader-based media as bring-up only; implement file-backed OTP/flash writeback before claiming boot-media fidelity |
| TF-M depends on undocumented FVP-specific RSEIL registers | Early boot stalls | Build a register touch trace and implement only touched registers first |
| MHUv3 model is too shallow | SCMI/secure services fail | Use TRM-backed register behavior and component tests before full boot |
| Current MHUv3 pairing uses static singleton behavior | Multiple MHU pairs interfere with each other | Add explicit CCI peer/pair binding and multi-pair isolation tests |
| SCMI response inside MHU `b_transport` is synchronous | Reentrancy and ordering bugs | Move protocol response behavior into `scp_service_model` and keep MHUv3 as doorbell state |
| MHU interrupt behavior is untested when unbound | False positive tests | Bind IRQ signals in component tests and assert deassertion after clear |
| AP direct boot assumptions hide firmware gaps | False confidence | Keep separate direct and RSE-oriented modes with separate validation reports |
| Secure storage/FWU writeback is nondeterministic | Hard-to-debug tests | Use per-run copied writable flash artifacts by default |
| Linux login can be reached while SI CL1 is absent | False MVP pass | Keep SI CL1 remoteproc/RPMsg as an explicit remaining acceptance check even after RSE runtime markers pass |

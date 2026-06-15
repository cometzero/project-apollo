# RSE QBox Specification

Created: 2026-05-20

## Feature Goal

Implement the Arm Zena CSS RD-Aspen Runtime Security Engine (RSE)
subsystem in QBox using SystemC/TLM and QEMU-backed CPU execution so that the
QBox virtual platform can follow the FVP RSE-oriented boot flow instead of
booting the primary compute only through direct Linux loading.

The implementation target is functional equivalence with the active
`fvp-rd-aspen` CFG2 configuration for the RSE-visible boot, security-service,
SCMI, and firmware-update behavior that the local Arm Zena CSS software stack
expects.

## Context

The current workspace baseline is:

- Machine: `fvp-rd-aspen`
- Variant: `RD_ASPEN_VARIANT = "cfg2"`
- Primary compute CPU count: `PC_CPUS_COUNT_DEFAULT = "4"`
- Direct-boot QBox platform: `tools/qbox/platforms/fvp-rd-aspen/`
- RSE-oriented QBox platform: `tools/qbox/platforms/fvp-rd-aspen-rse/`
- Current QBox boot mode: RSE-oriented functional-model bring-up, with
  primary-compute direct boot retained as compatibility coverage

The local documentation and configuration identify RSE as a Cortex-M55 based
Root of Trust running Trusted Firmware-M. It provides secure boot,
pre-SCP initialization, measured boot, attestation, protected storage,
firmware update, and MHUv3/SCMI communication with TF-A and SCP-firmware.

## Review Resolution Scope

The review feedback is handled by separating three evidence levels:

- `skeleton evidence`: QBox can launch an RSE-oriented entry point or report a
  precise missing-register/configuration blocker with file-backed logs and
  `result.json`.
- `MVP acceptance`: QBox boots through the RSE-oriented firmware path and
  reaches Linux login with the required RSE, SCMI, measured-boot, and AP
  release markers.
- `FVP equivalence`: QBox uses real or TRM-backed models for the RSE-visible
  blocks and passes FVP-vs-QBox comparison for the supported scenario.

The protocol-correct SCP service model is acceptable for MVP bring-up only as
`functional-model` evidence. It is not sufficient for an `fvp-equivalent`
claim unless later evidence proves the same observable behavior as real
Safety Island CL0/SCP execution.

As of the 2026-05-21 implementation pass, `skeleton evidence` also records
limited CC3XX, DTCM/ITCM alias, DMA350 fill, RSE system-control, ATU
translation, LCM/OTP, SAM, KMU, Integrity Checker, AP/SI host-window, and host
PPU models. These remove the previous CC3XX Data Abort, BL1_1 DMA erase/fill
timeout, `0x58021100` reset-syndrome fault, first ATU register-programming gap,
SAM register fault, untyped KMU placeholder, BL1_1 `__cmsis_start` copy-table
timeout, BL2 decrypt/validate blockers, first BL2 host-window gap, and SI CL0
PPU polling loop.

The historical host-PPU runtime evidence emitted TF-M UART markers through
BL1_1, BL1_2, BL2 PSA Crypto initialization, SI CL0 pre-load completion, and
primary/secondary slot version output. That evidence remains useful for
host-window and PPU coverage, but it predated the more faithful modular PKA
model and is no longer the current progress point. The current modular-PKA
runtime emits `Starting TF-M BL1_1`, `Jumping to BL1_2`,
`Starting TF-M BL1_2`, `Attempting to boot image 0`,
`BL2 image decrypted successfully`, `BL2 image validated successfully`,
`Jumping to BL2`, `Starting bootloader`, and
`PSA Crypto init done, sig_type: EC-P256`, then reaches SI CL0 pre-load
completion and primary/secondary slot version output with the current
modular-PKA model. A focused PKA trace shows no later PKA traffic after the
early BL2 PSA Crypto setup sequence. The later `0x7540a000` exception was
caused by RSE ATU region-range underflow: an access above an enabled region's
exclusive logical end incorrectly matched that lower region before region 12
could translate the SI PIK window. The ATU model now rejects
`logical >= region_end` before access-length arithmetic, and runtime trace
evidence shows `0x7540a000 -> 0x400002a600000` through region 12 with
`host_si_pik` reads/writes. KMU destination-port export and CC3XX AES-CMAC
behavior now have component coverage. The KMU model also loads the FVP-visible
hardware-slot key area from `rse-otp-image.img`, including
`KMU_HW_SLOT_KCE_CM`, and runtime trace evidence shows those non-zero key words
being exported into CC3XX `AES_KEY_0..7`. The previous BL2 decrypt blocker was
caused by giving QBox a gzip-compressed flashloader input instead of the raw
flash payload that FVP presents to firmware.

The previous post-decrypt BL1_2 image-signature validation failure was caused
by incomplete CC3XX SHA-256 multipart state save/restore. TF-M's PSA hash path
restores `HASH_H[0..7]` and `HASH_CUR_LEN0/1` between LMS/LMOTS update and
finish calls; QBox now preserves those registers. The post-SI-CL0
slot-version timeout is now narrowed to SI CL0 image 3 RAM loading. In the
default non-DMI path, PC sampling shows BL2 executing
`cfi_strataflashj3_read()`/`nor_cfi_reg_read()` while copying from the RSE
flash driver. In the opt-in `QBOX_RDASPEN_ATU_DMI=true` path, QBox progresses
past the timeout and MCUboot reports `Image 3 RAM loading to 0x70083c00 is
failed`, removes both slots, then reports `Unable to find bootable image`.
Image 3 is `RSE_FIRMWARE_SI_CL0_ID`. A follow-up CC3XX host-window DMA trace
shows no CC3XX transfer to `0x70083c00` before the failure, and TF-M source
mapping shows the active path starts in `flash_area_read()`. A filtered DMA350
run plus the generated TF-M `CMakeCache.txt` show
`PLATFORM_HAS_BOOT_DMA:BOOL=OFF`, so the current image does not compile the
DMA350 `boot_dma_memcpy()` branch for this read. QBox now models the RSE boot
flash aperture with `strata_flash_j3` rather than plain memory; the same
runtime still fails image 3. T019AG adds a file-backed host SI CL0 SRAM probe
and proves that the primary SI CL0 header at logical `0x70083c00` plus code at
`0x70084000` were copied from RSE flash offset `0x67000`; the copied prefix is
`0xb6b1e`, matching MCUboot's computed image size. The SRAM payload still
matches encrypted flash and the expected AES-KW TLV is present, so the failure
is no longer `flash_area_read()`, host-window layout, or slot removal/erase.
T019AH traces the BL2 encrypted-image path and shows `boot_enc_load()`,
`boot_decrypt_key()`, and `bootutil_aes_kw_unwrap()` execute, while
`boot_enc_set_key()` and `boot_enc_decrypt()` do not. That was the active
blocker for the SI CL0 loading phase.

Later implementation work supersedes the SI CL0, AP BL31, and RSE runtime
notification blockers. As of the 2026-05-24 T019BJ/T060 evidence, QBox boots
through the RSE-oriented path to the primary Linux login prompt in the
login-focused run, and the current marker-focused run records RSE/SCP
AP power-on, `RT_0`, `SCMI Comms subscribed to power state notifications`,
and measured-boot markers through `BL_33`. The latest T019AV runtime now also
proves the service-model SI CL1/RPMsg path through Linux `virtio6`, name-service
creation of `ethsi1`, `rpmsg_net` probe, and `ip link show ethsi1` success.
The remaining fidelity gap is the absence of a real SI CL1 CPU/Zephyr peer and
packet data-plane behavior behind that Linux-visible endpoint.

## User Value

QBox should become useful for validating the real RD-Aspen firmware and Linux
software stack without relying on Arm FVP for every iteration. The RSE
subsystem must therefore expose the same observable firmware behavior that the
FVP-based tests and boot logs expect.

## Primary User Stories

1. As a platform developer, I can boot QBox through the RSE-oriented firmware
   chain and observe RSE console logs equivalent to the FVP reference boot.
2. As a firmware developer, I can run TF-M RSE BL1/BL2/runtime images from the
   generated `rse-rom-image.img`, `rse-flash-image.img`, and
   `rse-otp-image.img` artifacts.
3. As a QBox developer, I can replace the current MHUv3 compatibility stubs
   with a reusable SystemC/TLM MHUv3 model that carries real doorbell and
   shared-memory interactions.
4. As a validation engineer, I can compare FVP and QBox logs for RSE boot,
   measured boot, SCMI AP power-on, SCMI reset/poweroff, and firmware-update
   bank selection.
5. As a maintainer, I can see which RSE blocks are `fvp-equivalent`,
   `functional-model`, `temporary-stub`, or `not-modeled`.

## Functional Requirements

### FR-001: RSE CPU And Reset

QBox shall instantiate a Cortex-M55 RSE execution context using the existing
QBox `cpu_arm_cortexM55` build target and the NVIC component under
`qemu-components/irq-ctrl/armv7m_nvic/` whose CMake target is `nvic_armv7m`.
The skeleton may use the existing `RemoteCPU` wrapper when direct Lua
instantiation cannot correctly bind the CPU-local NVIC/SCS window.

### FR-002: RSE Boot Media

QBox shall model the FVP boot media used by RD-Aspen:

- RSE ROM: `rse-rom-image.img`
- RSE flash: `rse-flash-image.img`, presented through a CFI/Strata-compatible
  command model for the FVP variant
- RSE OTP/NVM: `rse-otp-image.img`
- AP secure flash: `ap-flash-image.img`
- RSE provisioning bundle loaded into RSE SRAM at offset `0x20000`

The model shall support writeback behavior for flash/NVM paths when the FVP
configuration marks those images writable.

### FR-003: RSE Memory Map

QBox shall model RSE local ROM, SRAM, volatile memories, flash aperture, OTP,
system control registers, DMA350, CC3XX/CRYPTOCELL, SIC MPC, and ATU windows
needed by TF-M RSE firmware. The RSE ATU windows shall expose:

- non-secure system access window: `0x6000_0000..0x6fff_ffff`
- secure system access window: `0x7000_0000..0x7fff_ffff`

### FR-004: RSE ATU Behavior

QBox shall implement a SystemC/TLM ATU bridge with region programming,
enable/disable, base/limit translation, secure/non-secure separation, fault
status, and DMI invalidation behavior sufficient for TF-M RSE boot and safety
boot verification.

### FR-005: MHUv3 Doorbell Model

QBox shall replace hardcoded SCMI behavior in `mhuv3_stub` with an MHUv3
doorbell channel model. The model shall expose PBX and MBX programming frames,
interrupt status, masks, clear/set behavior, channel count configuration, and
TLM access semantics.

### FR-006: RSE-SCP SCMI Transport

QBox shall support the RSE-to-SCP SCMI path used to:

- confirm SCP-firmware booted
- power on AP primary core
- subscribe to system power state notifications
- receive system reset or poweroff notifications

For the first RSE-oriented boot milestone, this path may be implemented as a
protocol-correct SystemC/TLM SCP service model derived from local
SCP-firmware behavior, FVP logs, and Arm SCMI/MHUv3 documentation. It shall not
be a fixed "success" stub: it must consume shared-memory SCMI messages, deliver
and clear MHUv3 doorbells, update observable power/reset state, and emit
file-backed evidence. Full Safety Island CL0/CL1 CPU execution remains a later
fidelity milestone unless explicitly pulled into MVP scope.

### FR-007: AP-RSE Secure Services Transport

QBox shall support MHUv3 transport between Primary Compute secure world and
RSE for measured boot, attestation, protected storage, firmware update, and
SE-Proxy service calls.

### FR-008: RSE-Oriented Boot Flow

QBox shall support the RD-Aspen RSE-oriented boot sequence:

- RSE BL1_1 starts from ROM.
- RSE BL1_1 provisions data into OTP on first boot.
- RSE BL1_1 validates and jumps to RSE BL1_2.
- RSE BL1_2 loads, decrypts, validates, and jumps to RSE BL2.
- RSE BL2 loads SI CL0, SI CL1 for CFG2, AP BL2, and RSE runtime.
- RSE BL2 notifies SCP-firmware that AP may be powered on.
- RSE runtime provides measured boot and secure services.

### FR-009: Safety Island Boot Integration

QBox shall preserve RSE responsibility for starting Safety Island boot. Dummy
FVP-compatible LBIST/MBIST behavior may be used only where the Aspen FVP itself
uses dummy behavior, and the limitation shall be documented.

### FR-010: Secure Services

Post-MVP QBox shall expose the RSE runtime behavior needed by Primary Compute
secure services:

- PSA Crypto service path
- PSA Internal Trusted Storage
- PSA Protected Storage
- PSA Initial Attestation
- UEFI variable storage through SMM Gateway and SE-Proxy

### FR-011: Secure Firmware Update

Post-MVP QBox shall support RD-Aspen secure firmware update behavior enough to
validate capsule application, RSE flash/AP flash A/B bank selection, FWU
metadata, and RSE console evidence such as booting image bank 1.

### FR-012: Log-Based Verification

QBox shall write RSE, SCP/SI, Primary Compute secure console, and Primary
Compute Linux logs to files. Validation shall use log artifacts and JSON
reports, not tmux screen state.

### FR-013: Review-Gated Fidelity Reporting

Every RSE-oriented run report shall distinguish between:

- configuration/build blockers,
- missing-register or unimplemented-device blockers,
- marker failures after the platform starts,
- successful MVP boot evidence.

Placeholder logs and `check-only` runs may close skeleton tasks, but they shall
not be counted as RSE boot success.

## Non-Functional Requirements

- Preserve QBox C++14, SystemC/TLM-2.0, CCI, Lua, and CMake conventions.
- Prefer existing QBox/QEMU components before creating new components.
- Prefer official Arm documentation and TRMs for register-level behavior.
- Search open-source SystemC/TLM implementations before writing a new model.
- Do not copy code with incompatible licenses into QBox.
- Do not treat register-only compatibility stubs as final implementation.
- Keep FVP/QBox memory maps, IRQ lines, firmware artifacts, and runtime logs
  explicitly comparable.

## Success Criteria

### MVP Acceptance

The first implementation milestone is successful when:

1. QBox can launch an RSE-oriented boot mode.
2. RSE console logs include `Starting TF-M BL1_1`, `Jumping to the first image
   slot`, and `RSE to SCP SCMI power on AP succeeded`.
3. The measured boot log contains all expected RD-Aspen measured boot markers:
   `BL1_2`, `BL2`, `SI_CL0`, `AP_BL2`, `RT_0`, `SECURE_RT_EL3`,
   `SECURE_RT_EL1_SPMD`, and `BL_33`.
4. Primary Compute Linux reaches login through the firmware-mediated boot path.
5. FVP-vs-QBox comparison reports no unexplained differences for the required
   MVP marker table: RSE boot markers, MHUv3 doorbell flow, SCMI AP power-on,
   measured boot markers, AP release, and Linux login.
6. The report clearly states whether the RSE-SCP endpoint is backed by real
   Safety Island/SCP execution or by the protocol-correct SCP service model.

### Skeleton Acceptance

Before MVP acceptance, the first RSE skeleton milestone is considered useful
only when:

1. `scripts/run/run_qbox_fvp_rd_aspen_rse.py` records all input artifacts and
   copied writable images in `result.json`.
2. QBox either starts the RSE-oriented platform or reports a concrete blocker
   such as a missing Lua configuration, missing target, missing artifact, or
   first missing RSE register.
3. The run creates file-backed logs for RSE, SCP/SI, secure console, and
   primary console, even when some logs contain blocker placeholders.
4. The result does not claim `passed: true` unless the required MVP markers
   are present.
5. A trace-derived first failing access must include the reset SP/PC,
   access type, access address, exception, and trace log path when QEMU trace is
   enabled.
6. If RSE FWU private metadata is initialized for bring-up, the runner must do
   so only on the per-run writable flash copy and must record the previous and
   rewritten metadata state in `result.json`.
7. If QEMU trace is too slow or does not expose a first failing access, the
   runner may use file-backed RSE PC sampling, but the report must record the
   trace path, sample count, last sampled PC, and source mapping before
   reclassifying the blocker.
8. If the sampled PC maps to a default M-profile exception handler, the report
   must include captured exception state such as active exception, xPSR, LR,
   CFSR, HFSR, BFAR/MMFAR, security state, and the trace artifact path before
   assigning the next hardware-model task.
9. If BL2 encrypted-image tracing is enabled, the report must include the
   QEMU trace path, parsed BL2 symbol ranges, function hit counts, and a
   blocker classification that distinguishes `boot_enc_load()` key unwrap from
   `boot_enc_set_key()` and payload decrypt.

### Post-MVP Acceptance

Secure services are accepted only when QBox evidence covers Initial
Attestation, Protected Storage, Internal Trusted Storage, UEFI variable storage,
and SE-Proxy/SMM Gateway request paths.

Secure Firmware Update is accepted only when QBox evidence covers capsule
handoff, RSE/AP flash A/B bank metadata, reboot into the update bank, and
writeback persistence across reboot.

## Out Of Scope For First Delivery

- Formal safety qualification.
- Full cryptographic side-channel or hardware security modeling.
- Full performance/timing parity with FVP.
- Full Safety Island CL0/CL1 CPU execution if the protocol-correct SCP service
  model is selected for MVP.
- Secure Services and Secure Firmware Update acceptance, except for boot-path
  interfaces required by MVP.
- Modeling hardware that is not touched by the local RD-Aspen TF-M, TF-A,
  SCP-firmware, OP-TEE, U-Boot, Linux, or Zephyr stack.
- Claiming platform-wide 99 percent FVP equivalence from Linux boot alone.

## Evidence References

- `arm-zena-css/documentation/overview.rst`
- `arm-zena-css/documentation/design/components.rst`
- `arm-zena-css/documentation/design/boot_process.rst`
- `arm-zena-css/documentation/design/rse_image_encryption.rst`
- `arm-zena-css/documentation/design/secure_services.rst`
- `arm-zena-css/documentation/design/secure_firmware_update.rst`
- `arm-zena-css/documentation/design/safety_boot.rst`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`
- `sw-ref-stack/test_automation/tests/test_bsp_demos/test_00_rse.py`
- `sw-ref-stack/test_automation/tests/test_bsp_demos/test_07_scmi_reboot.py`
- `sw-ref-stack/test_automation/tests/test_baremetal_demos/test_fwu.py`
- `arm-zena-css/yocto/meta-zena-css-bsp/lib/oeqa/runtime/cases/test_00_rse.py`
- `tools/qbox/platforms/fvp-rd-aspen/conf.lua`
- `tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_m55/`
- `tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/`
- `tools/qbox/systemc-components/mhuv3_stub/`
- `tools/qbox/systemc-components/rse_atu/`
- `tools/qbox/systemc-components/host_ppu/`

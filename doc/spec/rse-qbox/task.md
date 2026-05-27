# RSE QBox Task List

Created: 2026-05-20

## Milestone 0: Evidence And Baseline

- [x] T001 Read `.config.yaml` and record current `MACHINE`,
      `RD_ASPEN_VARIANT`, and image paths in an evidence note.
- [x] T002 Capture or locate FVP RSE boot logs with
      `scripts/runfvp_log_boot.py`. The 2026-05-24 file-backed FVP run
      `build/fvp-boot-logs/rse-qbox-debug-telnet-20260524-v1/` completed in
      14.474 seconds and captured RSE, secure, primary, SI CL0, and SI CL1
      UART logs for QBox comparison.
- [x] T003 Record RSE boot, measured boot, reset, poweroff, and FWU log
      patterns from `sw-ref-stack/test_automation/`.
- [x] T004 Record FVP RSE image injection and writable flash parameters from
      `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`.
- [x] T005 Record current QBox direct-boot Lua objects, MHU stubs, and direct
      loader behavior from `tools/qbox/platforms/fvp-rd-aspen/conf.lua`.
- [x] T006 Create initial `doc/spec/rse-qbox/evidence.md`.
- [x] T007 Select MVP SCP strategy and record it in `evidence.md` before
      implementing RSE-SCP handoff.

## Milestone 1: RSE Boot Skeleton

- [x] T010 Build existing Cortex-M55 and NVIC QBox targets:
      `cpu_arm_cortexM55` and `nvic_armv7m`.
- [x] T011 Run or adapt the existing `platforms/cortex-m55-remote` smoke test.
- [x] T012 Add an RSE-oriented QBox run helper while keeping direct Linux
      boot separate.
- [x] T013 Add RSE image path parameters to Lua configuration.
- [x] T014 Instantiate RSE Cortex-M55, NVIC, local router, SRAM, ROM, flash,
      OTP, and UART in a separate Lua/C++ platform slice.
- [x] T015 Add file-backed RSE UART logging.
- [x] T016 Verify RSE mode starts and emits either TF-M logs or a precise
      missing-register blocker.
- [x] T017 Record reviewed Cortex-M55/RemoteCPU, internal NVIC,
      file-backed UART, and RSE skeleton address constraints in
      `design.md` and `evidence.md`.
- [x] T018 Switch RSE skeleton from direct nested Cortex-M55 Lua binding to
      `RemotePass`/`RemoteCPU` after trace evidence showed the direct
      `rse_cpu.nvic.mem` bind left the NVIC/SCS path as the first fatal blocker.
- [x] T019 Implement or integrate the next missing early RSE hardware block:
      a limited CC3XX/CRYPTOCELL SystemC/TLM model at `0x50154000`.
      Evidence from 2026-05-21 confirms the previous first fatal access write
      `0x501541c4` no longer Data Aborts.
- [x] T019B Add a limited DMA350 SystemC/TLM model for early BL1_1
      `DMASECINFO` and channel `CH_CMD` polling, and split the previously
      overlapping CC3XX/TRAM address range.
- [x] T019C Identify the next no-console timeout location after the CC3XX and
      DMA350 models with file-backed trace evidence. The 2026-05-21 traces map
      the stall to BL1_1 `startup_dma_double_word_memset()` /
      `wait_for_dma_operation_complete()` during DTCM and VM erase/fill.
- [x] T019D Replace the DMA350 command-completion stub with a minimal
      initiator-backed fill/data-movement model for the BL1_1 erase path.
      Evidence from 2026-05-21 shows DTCM and ITCM fills complete through
      DMA350 initiator writes and the next first fault moves to
      `RSE_SYSCTRL_BASE_S + 0x100` (`0x58021100`) reset-syndrome access.
- [x] T019E Add a touched-register RSE system-control model for
      `reset_syndrome`, `reset_mask`, `cpuwait`, and DMA boot configuration,
      then re-run the RSE trace to identify the next blocker. Evidence from
      2026-05-21 shows the previous `0x58021100` reset-syndrome Data Abort is
      removed; RSE now reads `reset_syndrome`, reads `reset_mask`, writes
      `reset_mask = 0x100`, and then times out without RSE UART markers.
- [x] T019F Identify the next post-system-control no-console blocker after
      the `reset_mask` write. Use trace/source mapping to separate missing
      boot-media/provisioning, LCM/OTP, ATU/MPC, and reset lifecycle effects
      before adding more compatibility registers. Evidence from 2026-05-21
      shows BL1_1 now reaches ATU programming and LCM/OTP reads, then still
      times out without RSE UART markers.
- [x] T019G Add a minimal RSE ATU touched-register model for early BL1_1
      programming and wire the non-secure host UART alias. This is not the
      full T030-T036 translation/fault model; evidence from 2026-05-21 shows
      ATUBC reads, region writes, `ATUC = 0x1`, and subsequent LCM reads.
- [x] T019H Add a minimal RSE KMU touched-register model and wire it at
      `0x5009E000`. Evidence from 2026-05-21 shows the runtime reaches
      `KMURD_32` reads at offset `0x538`; full KMU key export and destination
      port side effects remain open.
- [x] T019I Add a minimal RSE Integrity Checker touched-status model and
      runner fidelity label. Component tests pass, but runtime evidence has
      not reached the `0x5015C000` register window yet.
- [x] T019J Capture the next no-console PC trace after KMU bring-up. Evidence
      from 2026-05-21 maps the timeout to BL1_1 `__cmsis_start` at
      `0x1100092e`, inside the C runtime copy-table path after early platform
      initialization.
- [x] T019K Remove the BL1_1 copy-table timeout by making RSE volatile memory
      state visible across the `RemoteCPU` split process and by adding the next
      missing SAM register surface at `0x5009F000`. Evidence from 2026-05-21
      shows the previous `__cmsis_start` timeout and SAM fault are superseded
      by CC3XX DMA/hash progress.
- [x] T019L Expand the CC3XX model far enough for BL1_1 to validate BL1_2:
      DMA completion status, SHA-256 DMA input, `HASH_H` updates, and the
      initiator path through the RSE router. Evidence from 2026-05-21 shows
      RSE UART reaches `Starting TF-M BL1_1`, `Jumping to BL1_2`, and
      `Starting TF-M BL1_2`.
- [x] T019M Initialize invalid RSE FWU private metadata only in the per-run
      writable flash copy so BL1_2 selects image slot 0 instead of generated
      garbage slot 208. Evidence from 2026-05-21 records the previous bytes in
      `result.json` and preserves the deploy `rse-flash-image.img`.
- [x] T019N Add focused CC3XX AES-CTR memory-to-memory coverage and identify
      the next BL1_2 blocker. Evidence from 2026-05-21 shows the AES-CTR unit
      vector passes, but runtime still fails at `[ERR] BL2 image failed to
      decrypt` because KMU key export and CC3XX AES-CMAC/SP800-108 KDF are not
      modeled yet.
- [x] T019O Implement KMU destination-port key export for hardware slots such
      as `KMU_HW_SLOT_KCE_CM`, including TLM writes to the configured CC3XX
      export address and component coverage. Evidence from 2026-05-21 shows
      `rse_kmu-tests` verifies exported key words are written through the
      initiator socket to the destination port.
- [x] T019P Implement CC3XX AES-CMAC behavior required by
      `cc3xx_lowlevel_kdf_cmac()`. Evidence from 2026-05-21 shows the
      RFC 4493 AES-CMAC component vector passes and runtime traces expose
      non-zero tags through `AES_IV_0..3`.
- [x] T019Q Re-run the RSE path after KMU/CMAC work and determine the next
      blocker after BL2 decrypt, or record BL2 progress if decryption succeeds.
      Runtime still fails at `[ERR] BL2 image failed to decrypt`; the blocker
      moved to unprovisioned `KMU_HW_SLOT_KCE_CM` hardware-slot key material.
- [x] T019R Model the FVP-equivalent `KMU_HW_SLOT_KCE_CM` key material from
      OTP/provisioning evidence, avoiding a BL2-only shortcut. Evidence from
      2026-05-21 shows the KMU model loads hardware slots from the LCM OTP
      hardware-key area in `rse-otp-image.img`, including KCE_CM at offset
      `0x60`, and component coverage verifies slot 4 export.
- [x] T019S Re-run BL1_2 after KCE_CM provisioning and determine whether the
      next failure is AES-CTR DMA/endian behavior or post-BL2 hardware.
      Runtime still fails at `[ERR] BL2 image failed to decrypt`, but traces
      now show non-zero KCE_CM words exported into CC3XX `AES_KEY_0..7`.
- [x] T019T Compare and fix the BL1_2 BL2 decrypt production flow after
      OTP-backed KCE_CM export. Evidence from 2026-05-21 shows the remaining
      decrypt failure was caused by binding gzip-compressed `rse-flash-image.img`
      directly to QBox `gs_memory`; the runner now creates a per-run raw flash
      image for QBox, and runtime reaches `BL2 image decrypted successfully`.
- [x] T019U Fix the post-decrypt BL1_2 image-signature validation failure.
      Evidence from 2026-05-21 shows the root cause was incomplete CC3XX
      SHA-256 multipart state save/restore: TF-M restores `HASH_H[0..7]` and
      `HASH_CUR_LEN0/1` between PSA hash update and finish during LMS/LMOTS
      validation. QBox now preserves those registers across `HASH_OPERATION`
      boundaries. The focused CC3XX regression passes, and runtime reaches
      `BL2 image validated successfully`, `Jumping to BL2`, and
      `Starting bootloader`.
- [x] T019V Debug the BL2/MCUboot timeout after `Starting bootloader`.
      Evidence from 2026-05-21 shows the first post-BL2 blocker moved through
      three concrete gaps: missing RSE integration-layer registers at
      `0x58100000`, a missing ATU-translated SI PIK host window at physical
      `0x400002a600000`, and a PPU policy/status polling loop. QBox now has
      initiator-backed RSE ATU translation, static AP/SI host windows, and a
      narrow `host_ppu` model. Runtime reaches `PSA Crypto init done`,
      `BL2: SI CL0 pre load complete`, and primary/secondary slot version
      prints before timing out.
- [x] T019W Debug the post-SI-CL0 pre-load timeout after MCUboot slot version
      output. Current runtime evidence
      `build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4/`
      reaches `BL2: SI CL0 pre load complete` and primary/secondary slot
      version output with no active exception state or first failing translated
      register access, then times out in the BL2 CFI flash read path:
      `0x31024c9c` maps to `nor_cfi_reg_read()` in `cfi_drv.c:54`, and
      `0x31023136` maps to `cfi_strataflashj3_read()` in
      `spi_strataflashj3_flash_lib.c:213`. The opt-in DMI run
      `build/qbox-fvp-rd-aspen/rse-t019w-atu-dmi-20260521-v1/`
      progresses past the timeout and exposes the explicit MCUboot failure
      `Image 3 RAM loading to 0x70083c00 is failed`, then
      `Unable to find bootable image`.
- [ ] T019X Stabilize optional `rse_atu` translated DMI before enabling it by
      default. The first DMI experiment in
      `build/qbox-fvp-rd-aspen/rse-atu-dmi-20260521-v1/` stopped earlier,
      after `PSA Crypto init done`. The later DMI run
      `build/qbox-fvp-rd-aspen/rse-t019w-atu-dmi-20260521-v1/` now reaches
      the SI CL0 image 3 RAM-load failure, but DMI remains opt-in because the
      default path still needs equivalent behavior without hiding flash/NVM or
      host-window side effects. The 2026-05-24 DMI increment adds
      `reg_router` DMI forwarding/invalidation and read-only libqemu memory
      aliases for non-writable DMI grants. Focused tests and builds pass, and
      runtime `build/qbox-fvp-rd-aspen/rse-t019ax-reg-router-dmi-20260524-v1/`
      reaches the SI CL1 copy path with non-zero CL1 SRAM evidence, but the
      AP/Linux path still does not complete in that short DMI run.
- [x] T019XA Guard `rse_atu` translated DMI grants against partial
      downstream windows. `translation_get_direct_mem_ptr()` now rejects a DMI
      grant unless the translated upstream DMI range covers the entire
      requested transaction span, not only the first requested address. The
      focused `rse_atu-tests` regression
      `RejectsTranslatedDmiWhenRequestSpansDownstreamGrant` passes with the
      existing translated-DMI tests.
- [x] T019XB Guard `rse_atu` two's-complement negative offsets against
      physical-address underflow. Translations and DMI probes now reject
      negative add-value mappings when `logical < abs(offset)` instead of
      wrapping to a high physical address. Focused negative-offset underflow
      tests pass for both normal translation and non-latching DMI probes.
- [x] T019Y Implement the first CC3XX PKA fidelity increment for the optional
      DMI branch and future BL2 crypto paths. CC3XX trace evidence in
      `build/qbox-fvp-rd-aspen/rse-cc3xx-after-atu-dmi-20260521-v1/` shows
      TF-M using `OPCODE`, `PKA_STATUS`, `PKA_PIPE_RDY`, `PKA_DONE`, and
      `PKA_SRAM_*`. QBox now implements PKA SRAM word cursors and basic
      ADD/SUB/AND/OR/XOR opcode execution. Component tests cover the captured
      `0x210e10c0` ADD-immediate trace pattern, and runtime trace
      `build/qbox-fvp-rd-aspen/rse-cc3xx-pka-add-trace-20260521-v1/` confirms
      ADD/SUB immediate results are visible through `PKA_SRAM_RDATA`.
- [x] T019Z Implement the next CC3XX PKA modular arithmetic and status fidelity
      increment. QBox now models PKA `ALU_SIGN_OUT` status for TF-M
      comparisons, shift opcodes, modular add/subtract, multiply low/high,
      division quotient/remainder behavior, modular multiplication,
      exponentiation, inverse, and reduction. Component tests cover these
      opcode semantics, and runtime evidence
      `build/qbox-fvp-rd-aspen/rse-cc3xx-pka-mod-trace-20260521-v1/` still
      reaches `PSA Crypto init done, sig_type: EC-P256` without a first failing
      register access.
- [x] T019AA Add a current-PC probe for the remaining post-PSA-Crypto timeout
      after the modular PKA increment. Evidence from
      `build/qbox-fvp-rd-aspen/rse-pc-trace-20260521-v2/` records 1479
      Cortex-M55 PC samples and maps the stable tail PC `0x3101d80c` to BL2
      `exception_handler()` in `startup_rse_bl.c:47`. The timeout is therefore
      no longer classified as an unexplained EC-P256/PKA loop.
- [x] T019AB Capture the BL2 exception cause/state after PSA Crypto init.
      Evidence from
      `build/qbox-fvp-rd-aspen/rse-exception-trace-20260521-v2/` records
      890 Cortex-M55 PC/exception samples and shows a stable HardFault at
      BL2 `exception_handler()` with `HFSR = 0x40000000`,
      `CFSR_NS = 0x8200`, and `BFAR = 0x7540a000`. The transition sample maps
      the previous sampled PC `0x31021764` to `software_zero_count_compute()`
      in `rse_zero_count.c:60`.
- [x] T019AC Implement the missing QBox side effect for the BL2 precise bus
      fault at RSE host-access logical address `0x7540a000`. The root cause was
      an `rse_atu` range-check bug: when an enabled region's logical address was
      above the region end, unsigned `end - logical` underflow let region 0
      match before the later SI PIK region. QBox now checks `logical >= end`,
      traces the selected region/offset pages, and covers this with a
      multi-region SI PIK regression. Runtime evidence
      `build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4/` shows
      `0x7540a000` translating to `0x400002a600000` through region 12 and
      reaching the post-SI-CL0 slot-version path.
- [x] T019AD Fix or faithfully model the SI CL0 image 3 RAM-load path. The
      current generated TF-M build has `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`, so
      this path is served by the CMSIS CFI/Strata flash-driver read path into
      the ATU-translated host-window destination. Runtime
      `build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1/`
      records `Image 3 RAM loading to 0x70083c00 is succeeded`, key-hash
      match, `SI CL0 is released out of reset`, and `SI CL0 post load
      complete`.
- [x] T019AE Add filtered DMA350/ATU evidence for the SI CL0 image 3 copy path.
      QBox now exposes `QBOX_RDASPEN_DMA350_TRACE_FILTER` and
      `QBOX_RDASPEN_DMA350_TRACE_ADDRESS_MIN` so future DMA350 runs can focus
      on copy operations and host-window addresses. The 2026-05-21 filtered
      DMI run reached `BL2: SI CL0 pre load complete`, primary/secondary slot
      versions, and the image 3 RAM-load failure, but produced no
      `rse_dma350` trace lines. Combined with `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`,
      this closes the DMA350 investigation for the current generated TF-M
      image and reclassifies the next implementation step to the CFI/Strata,
      ATU host-window, and post-copy MCUboot split.
- [x] T019AF Trace and model the CFI/Strata and ATU host-window path for
      SI CL0 image 3. QBox now uses a `strata_flash_j3` SystemC/TLM component
      for the RSE boot flash instead of plain `gs_memory`, adds focused boot
      flash and ATU DMI trace controls, and verifies that CFI byte reads and
      translated ATU DMI grants reach the SI CL0 host-window copy phase. The
      explicit MCUboot failure remains unchanged after this model swap, so the
      next blocker is no longer classified as an unmodeled boot-flash aperture.
      The active path remains
      `flash_area_read()` -> `DRV_FLASH_AREA()->ReadData()` ->
      `cfi_strataflashj3_read()` -> `nor_cfi_reg_read()` while copying from
      RSE boot flash into logical `0x70083c00`, and then split copy failure
      from `boot_enc_load()`, key setup, decrypt, slot removal/erase, or SI CL0
      image layout assumptions.
- [x] T019AG Split the remaining SI CL0 image 3 failure after the Strata flash
      model. The RSE runner now maps `host_si_cl0_sram` to a per-run file and
      records header/code samples, slot matches, MCUboot image size, and TLV
      metadata. The 2026-05-22 run proves the primary SI CL0 image header at
      logical `0x70083c00` and code at `0x70084000` were copied from RSE flash
      offset `0x67000`; the mapped prefix match is `0xb6b1e`, exactly the
      `boot_read_image_size()` result. That closes the `flash_area_read()`,
      host-window layout, and slot-removal hypotheses for the primary failure.
      The payload still matches encrypted flash and `boot_enc_decrypt()` did
      not visibly modify SRAM, while the expected AES-KW TLV `0x31/0x18` is
      present. The remaining blocker is narrowed to `boot_enc_load()` key
      unwrap or the immediately following `boot_enc_set_key()` path.
- [x] T019AH Instrument the SI CL0 encrypted-image key path to distinguish
      `boot_enc_load()` AES-KW unwrap failure from `boot_enc_set_key()` AES-CTR
      key setup failure. Use CC3XX/AES trace, focused PC/source evidence, or a
      minimal firmware return-code probe; do not mask the failure by forcing
      encrypted-image success. The runner now supports `--qemu-trace-events`,
      `--qemu-trace-filter`, and `--boot-enc-trace`; the 2026-05-23 v2 runtime
      records `boot_enc_load`, `boot_decrypt_key`, and
      `bootutil_aes_kw_unwrap` hits but zero `boot_enc_set_key` or
      `boot_enc_decrypt` hits. The current blocker is therefore
      `si_cl0_boot_enc_load_decrypt_key_failed_before_set_key`.
- [x] T019AI Debug and model the SI CL0 AES-KW unwrap failure without forcing
      success. Compare the SI CL0 `IMAGE_TLV_ENC_KW` bytes, MCUboot image ID,
      PSA unwrap key selection, provisioning/OTP/KMU key material, and any
      CC3XX AES-KW/PSA backend behavior against local TF-M/FVP evidence before
      changing crypto or image-loading behavior. Evidence from 2026-05-23
      shows the remaining unwrap failure was removed by adding the missing
      CC3XX AES ECB decrypt path needed by the AES-KW primitive. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ai-lcm-tci-kmu-keytrace-20260523-v1/`
      reaches `Image 3 RAM loading to 0x70083c00 is succeeded`,
      `Key hash matched for image 3 at slot 0`, and
      `Image 3 loaded from the primary slot`.
- [x] T019AJ Align RSE LCM/KMU bring-up details with the generated RD-Aspen
      firmware path. QBox now exposes a KMU trace filter for hardware-key
      export evidence and sets the RSE LCM test-production mode to TCI
      (`0x111155AA`), matching the active TF-M build
      `RSE_TP_MODE:STRING=TCI`. Component tests cover the key trace filter and
      configured TCI `tp_mode`.
- [x] T019AK Replace the host-side SI/AP/SMD ATU placeholder memories with
      `rse_atu` register models. Evidence from
      `build/qbox-fvp-rd-aspen/rse-t019aj-host-atu-regs-20260523-v2/`
      shows BL2 programs SI ATU regions 0..16, releases SI CL0 from reset,
      completes SI CL0 post-load, and then reaches the next explicit blocker:
      RSE-to-SI MHUv3 driver init failed with `0x60000001`.
- [x] T019AL Add the first RSE-SI MHUv3 PBX/MBX + SCMI service increment.
      The RSE-SI MHU aperture is now split into PBX and MBX `mhuv3_stub`
      frames, exposes MHUv3 AIDR/IIDR/frame registers, signals ACK bit 1, and
      decodes the RSE BL2 SCMI shared-memory transport for Base, Power Domain,
      and System Power protocol requests. Component tests cover Power Domain
      protocol version, state set/get, and the ACK doorbell. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ak-mhuv3-scmi-20260523-v5/`
      reaches `Init SCMI comm to SCP succeeded` and
      `SCP ready. Power domain protocol version = 0x20000`, then times out
      later after AP BL2 slot-version output.
- [x] T019AM Debug the AP BL2 image-loading/progress blocker after the new
      MHU/SCMI success point. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019an-mhu-pair-map-default-20260523-v2/`
      proves the AP BL2 path now reaches `Image 2 RAM loading to 0x70001c00
      is succeeded`, AP ATU region programming, RSE runtime image 0 load,
      `RSE to SCP SCMI power on AP succeeded`, and
      `Jumping to the first image slot`. The remaining timeout is after RSE
      releases AP power, not in AP BL2 image loading.
- [x] T019AN Add AP handoff host windows and keep RSE-SI/AP-RSE MHU frame
      routing isolated. The RSE platform now exposes AP high physical windows
      for CSS counters/timers, SMCF SRAM, AP-RSE MHU frames, and AP-RSE
      mailbox memory. `mhuv3_stub` records MBX peers by `pair`, so adding the
      AP-RSE MBX no longer steals the RSE-SI SCMI ACK path. Component test
      `mhuv3_stub-tests` covers pair isolation and AP reset release signaling.
- [x] T019AO Stabilize AP CPU reset/EL3 bring-up behind
      `QBOX_RDASPEN_ENABLE_AP_CPUS=true`. The experimental AP CPU path wires
      A720AE CPUs, GICv3, timer PPIs, and AP UART backends. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ao-ap-cpus-reset-trace-20260523-v1/`
      proved the modeled RSE/SCP power-on path really releases AP0 reset.
      Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ao-ap-cpus-primary-power-20260523-v1/`
      then showed AP0 executing past `pc=0x82000` into AP BL2 after setting
      AP0 `start_powered_off = false` while keeping secondary CPUs powered
      off. The first AP BL2 blocker became AP-side RSE-COMMS MHUv3 init
      `-4`, not reset release.
- [x] T019AP Model the AP secure BL2 RSE/SDS/secure-service path after AP-RSE
      MHUv3 init succeeds. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ap-ap-rse-mhu-20260523-v1/` proves the
      multi-channel AP-RSE MHUv3 increment removes
      `Host to RSE MHU driver initialization failed: -4`; AP secure BL2 now
      prints the BL2 banner, warns `SDS init failed (-1), continuing measured
      boot`, and loads image id 6 at `0x2010..0x24ce`. The run still times out
      before later secure-world/Linux markers. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019aq-ap-rse-psa-reply-nodmi-20260523-v1/`
      adds a minimal AP-RSE PSA success reply but still times out after image
      id 6; AP PC trace reaches `0x826f4`, which maps to TF-A BL2
      `plat_panic_handler`. Follow-up runtimes seeded AP SDS, mapped AP
      secure-service/NV counter/DRAM windows, and verified AP BL2 now loads
      and measures FW_CONFIG, HW_CONFIG, BL31, BL32/SPMD, and BL33 before
      booting BL31. The old AP BL2 measured-boot/RSE secure-service panic is
      no longer the active blocker.
- [x] T019AQ Seed AP trusted/non-trusted NV counters and AP runtime memory
      windows from RD-Aspen TF-A/FIP evidence. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ay-ap-ntfw-nvctr-20260523-v1/`
      proves BL33 cert/content/image loading and measured boot. The extracted
      BL33 SHA-256
      `64d6bd3583fb54a7f7ae4655bef9f3e26e7ed4376db5b800a094ae37a5459660`
      matches the BL33 measurement in the AP secure console.
- [x] T019AR Add the AP system timer model required by BL31
      `arm_configure_sys_timer()`. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019az-ap-timer-20260523-v1/` removes the
      previous `far_el3 = 0x1a810040` abort and advances BL31 to SCMI driver
      initialization.
- [x] T019AS Add AP ATU-translated AP-SI SCMI MHU PBX/MBX frames. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1/`
      removes the previous `far_el3 = 0x40080010` abort in
      `plat_css_get_scmi_info()` and reaches `SCMI driver initialized`.
- [x] T019AT Model or configure AP CPU RAS system-register behavior for
      RD-Aspen BL31. The later AP runtime no longer stops at
      `rdaspen_ras_init_per_cpu()` writing `ERRSELR_EL1`; runtime
      `build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/`
      reaches BL31 runtime services, OP-TEE/SPMC output, Linux driver probes,
      and the primary console login prompt.
- [x] T019AU Align AP/SI MHUv3 host-physical windows with the FVP ATU map and
      Linux device tree. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019de-ap-mhu-map-20260524-v1/`
      proves AP ATU translations for logical `0x400b0000`, `0x400e0000`,
      `0x40020000`, and `0x40050000` reach host-physical
      `0x400003b100000`, `0x400003b140000`, `0x400003b000000`, and
      `0x400003b040000` respectively. Linux MHUv3 probes at those four
      addresses return 0, SCMI mailbox transport probes, SMMUv3 probes, PFDI
      starts, and the primary console reaches `fvp-rd-aspen login:`.
- [x] T019AV Model the remaining Safety Island CL1 runtime/RPMsg path and
      RSE runtime notification markers. The host SCR/SID path is now modeled:
      `host_si_scr` reports `sid_system_cfg.cl1_present = 1`, RSE BL2 no
      longer prints `SI CL1 not present, skip loading`, and runtime
      `build/qbox-fvp-rd-aspen/rse-t019av-host-scr-cl1-sram-20260524-v1/`
      reaches `BL2: SI CL1 pre load complete`,
      `Image 4 RAM loading to 0x70185c00 is succeeded`,
      `Image 4 loaded from the primary slot`, and
      `BL2: SI CL1 post load complete`. The CL1 SRAM backing file records
      non-zero runtime data. Later runtime evidence reaches the FVP RSE runtime
      markers `SCMI Comms subscribed to power state notifications` and `RT_0`.
      A first RPMsg service-model increment is present: `mhuv3_stub` can now
      consume a Linux RX virtqueue descriptor, write an RPMsg name-service
      message for the generated Zephyr CL1 endpoint `ethsi1`, update the used
      ring, and signal `vq0_rx`. Component test coverage passes in
      `mhuv3_stub-tests`. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019aw-rpmsg-seed-indexed-preset-20260524-v1/`
      proves the resource-table seed now reaches QBox memory
      (`doorbell-ack-seed-memory ... status=ok`), Linux registers
      `rproc-virtio ... virtio6 (type 7)`, and post-login probes show
      `remoteproc_state:si-cl1:attached`, `rpmsg_ns`, `virtio_rpmsg_bus`, and
      `rpmsg_net` module return code 0, but exposed a timing bug where the
      NS packet arrived before the Linux `rpmsg_ns` endpoint existed.
      Runtime
      `build/qbox-fvp-rd-aspen/rse-t019av-rpmsg-host-kick-20260524-v1/`
      fixes and proves the functional path: MHU trace records
      `rpmsg-ns-defer-until-host-kick`, `rpmsg-ns-injected name=ethsi1`,
      and `rpmsg-ns-signaled`; Linux logs
      `virtio_rpmsg_bus virtio6: creating channel ethsi1`,
      binds `virtio6.ethsi1.-1.1024`, and post-login probe reports
      `ethsi1_iplink_rc:0`. Remaining fidelity work is tracked separately:
      the current `ethsi1` endpoint is service-modeled, not a real SI CL1
      CPU/Zephyr peer with packet data-plane behavior. Later AP/SI MHU work
      now clears synthetic PBX doorbells and drives PBX transfer-ack IRQs for
      service-modeled auto-ack/RPMsg-NS traffic; see V038S. Runtime proof that
      this removes the Linux `Try increasing MBOX_TX_QUEUE_LEN` warning is in
      `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/`.
      That copy-flash run reaches Linux and the post-login probe with no
      `400b0000.mhu` spurious-PBX or mailbox queue warnings.
- [x] T019AW Establish reusable GDB inspection for QBox host, TF-M/RSE,
      SCP-Firmware symbols, and Linux/AP state. Script
      `scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py` creates per-run GDB
      scripts and source maps for QBox, TF-M, AP TF-A, AP OP-TEE, AP U-Boot,
      SCP-Firmware, Linux, and SI CL1 Zephyr. Runtime
      `build/qbox-fvp-rd-aspen/gdb-t019ay-host-all-20260524-v1/` proves the
      RSE and AP GDB ports are reachable, captures TF-M and Linux current-PC
      probes, captures a QBox host GDB thread/backtrace sample, and records the
      current SCP limitation: the QBox RSE path uses a service model and has
      SCP-Firmware symbols/source mapping but no live SCP CPU GDB port. The
      later AP firmware probe
      `build/qbox-fvp-rd-aspen/gdb-ap-firmware-probes-20260524-v1/` verifies
      the generated AP TF-A BL2/BL31, OP-TEE, U-Boot, and Linux scripts all
      attach and capture per-CPU state; the 25-second sample still has AP CPUs
      at `0x82000`/AP BL2 while RSE is clearing the SCMI shared-memory window.
      The current fast-runtime bundle
      `build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v2/` verifies
      the same environment after Linux has started: AP/Linux GDB resolves CPU0
      to `cpu_do_idle()`, CPU2 to `change_protection_range()`, TF-M/RSE GDB
      resolves the runtime to `__tfm_arch_thread_fn_call_veneer()` /
      `psa_wait_thread_fn_call()`, and SCP remains symbol-only under the
      service-model strategy. The companion host bundle
      `build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v1/` captures
      QBox/SystemC/QEMU thread backtraces by launching `platforms-vp` under
      GDB. A user-requested short-timeout recheck
      `build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1/` confirms the
      generated environment still covers QBox host, TF-M/RSE, AP firmware/Linux
      target attachment, SCP-Firmware symbols, and SI CL1 symbols. It also now
      records `scp_port_listening: False` for the active service-model path,
      making the live-SCP-GDB limitation explicit in `progress-report.md`. A
      follow-up handoff-gated bundle
      `build/qbox-fvp-rd-aspen/gdb-handoff-debug-short-20260525-v1/` reaches
      `RSE to SCP SCMI power on AP succeeded` after 76.025 seconds; AP CPU0 is
      then in TF-A BL2 `mhu_v3_x_doorbell_read()`, RSE/TF-M is in
      `nor_send_cmd_byte()` below ITS/PS flash writeback, and Linux has not
      started in that bounded sample.
- [x] T019AX Add initial opt-in RSE remote-process co-location for high-traffic
      RSE-local devices found by GDB. `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true`
      moves KMU and CC3XX into the RSE `RemoteCPU` process, and
      `QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true` moves the RSE
      `strata_flash_j3` boot-flash model into the same process. This was
      introduced as an opt-in path and is now defaulted by T019BC. Evidence from
      `build/qbox-fvp-rd-aspen/rse-local-crypto-flash-90s-20260524-v1/`
      reaches `BL2: SI CL0 pre load complete` and records non-zero SI CL0
      SRAM header/code data. GDB evidence from
      `build/qbox-fvp-rd-aspen/gdb-local-crypto-flash-80s-20260524-v1/`
      moves the sampled blocker from `cfi_strataflashj3_read()` to
      `clear_safety_island_memory()` / `memset()` through the ATU-translated
      host-SRAM path. The next optimization must preserve host SCR/PPU/MHU
      shared-state semantics before moving ATU/host SRAM locally.
- [x] T019AY Use short GDB/hash-DMA probes to isolate the BL1_1 BL1_2 hash
      regression and make the FVP-equivalent DTCM CPU0 alias default. GDB at
      `bl1_1_validate_image_at_addr + 94` showed the BL1_2 image at both
      `0x10004000` and `0x1a004000` matches the OTP hash
      `18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c`,
      while CC3XX computed
      `b3c904a855b9d1e8ff160d56ad1fd93c797538e6a8b4c08fe33b74a6d1adf228`.
      The corrected CC3XX `dma` trace showed TF-M programs the final hash
      block from `0x34003820`; GDB showed `0x30003820` contains the expected
      BL1_2 tail while `0x34003820` still contains the `0xa4093822` TRAM-fill
      pattern. `QBOX_RDASPEN_RSE_SPLIT_CPU0_DTCM_ALIAS` now defaults to
      `false`, and the default short local-crypto/local-flash run reaches
      `Jumping to BL1_2`, `Starting TF-M BL1_2`, and the next BL2 decrypt
      failure.
- [x] T019AZ Use short GDB and PC-trace probes to identify the current
      post-decrypt progress point. RSE VM0/VM1 DMI was disabled by default
      because GDB showed the encrypted-image IV copied into VM0 as only the
      low byte `0x67` plus zeros, while the raw boot flash contains the full
      `67 a4 79 10 ...` IV. With `QBOX_RDASPEN_RSE_VM_DMI=false`, short RSE
      logs reach `BL2 image decrypted successfully`. A 28-second all-target
      GDB sample at
      `build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2/`
      shows TF-M/RSE in BL1_2 LMS/LMOTS validation
      (`hash_digit_array()` -> `mbedtls_lms_verify()` ->
      `validate_image_signature()`), with fault registers clear. AP/Linux
      remains at `0x82000`, and SCP-Firmware remains symbol/source-only until
      a live SCP CPU model is wired.
- [x] T019BA Fix shared-memory fd reporting and add a focused QEMU DMI
      byte-store regression for the RSE VM DMI blocker. `map_mem_create(...,
      &fd)` now returns a non-negative fd when the mapping succeeds, and
      `memory-tests` covers that contract. The new
      `aarch64-dmi-byte-store-test` originally reproduced the byte-store
      visibility/aliasing class that corrupts the TF-M VM0 encrypted-image IV.
- [x] T019BB Fix QEMU DMI granted-access preservation and split the remaining
      VM-DMI blocker. `QemuInstanceDmiManager::get_region()` now preserves
      `tlm_dmi::get_granted_access()` when rebuilding the region descriptor,
      so writeable DMI regions are no longer installed as read-only QEMU RAM.
      The focused `aarch64-dmi-byte-store-test`, shared-memory byte-store
      test, and shared-memory external-write test all pass with DMI enabled.
      The follow-up fd-backed RemotePass work supersedes the intermediate
      VM-DMI decrypt failure.
- [x] T019BC Enable the validated RSE-local fast path for short-timeout
      iteration. libqemu now exposes fd-backed RAM initialization, QBox passes
      shared-memory fd/offset metadata into QEMU DMI aliases, and the remote
      Cortex-M55 DMI byte-store on/off tests pass. `QBOX_RDASPEN_RSE_VM_DMI`,
      `QBOX_RDASPEN_RSE_DTCM_DMI`, `QBOX_RDASPEN_RSE_ITCM_DMI`,
      `QBOX_RDASPEN_RSE_LOCAL_CRYPTO`, and
      `QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH` now default to `true`, with `false`
      env overrides retained for DMI and cross-process regression debugging.
      Environment-forced runtime evidence
      `build/qbox-fvp-rd-aspen/rse-current-all-rse-dmi-20260524-v1/`
      reaches `BL2 image validated successfully`, `Starting bootloader`, and
      SI CL1 pre-load in 35 seconds; AP-enabled evidence
      `build/qbox-fvp-rd-aspen/rse-current-ap-all-rse-dmi-20260524-v1/`
      reaches RSE runtime chainload and Linux systemd/driver probe output in
      120 seconds. Current-default validation
      `build/qbox-fvp-rd-aspen/rse-current-default-fast-20260524-v1/` reaches
      BL2 validation, BL2 entry, SI CL1 pre-load, and slot-version output with
      no fast-path environment overrides. Current-default AP validation
      `build/qbox-fvp-rd-aspen/rse-current-default-ap-fast-20260524-v1/`
      reaches RSE runtime chainload, Linux boot, PL011/SMMUv3/virtio/PFDI
      driver output, and systemd startup in 120 seconds, but not login.
- [x] T019BD Establish current AP firmware and host-GDB inspection points.
      The quiet-console rootfs profile patches a sparse per-run WIC copy with
      `console=ttyAMA0,115200` while removing the high-volume
      `earlycon`/`ignore_loglevel`/`initcall_debug` arguments from that copy.
      The 140-second quiet-console runtime still times out before login and
      its slim preserved evidence is
      `build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1-slim/`.
      GDB evidence
      `build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1/`
      captures the AP in secure-world firmware: BL31
      `pfdi_cpu_self_test_result()` / `plat_pfdi_pe_init()` and OP-TEE
      `pl011_putc()` / `boot_mem_release_unused()` / `init_primary()`.
      Linux symbols attach through the AP GDB target, but the sample is before
      Linux execution. The separate host sample
      `build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1/` captures
      QBox host, SystemC, RPC, QEMU iothread, call_rcu, worker, and AP CPU TCG
      threads.
- [x] T019BE Add TF-M runtime-symbol GDB coverage and remove the
      `CPU0_SECCTRL_BASE_S` RSE BusFault. The earlier all-layer GDB sample
      had PC `0x31063480`, `CFSR = 0x8200`, `HFSR = 0x40000000`, and
      `BFAR = 0x50011000`; TF-M maps that address to `CPU0_SECCTRL_BASE_S`
      and uses it in `sau_and_idau_cfg()` / MPC setup. QBox now exposes the
      CPU0 security, power-control, and identity windows, RSE SIC registers,
      and VM/SIC MPC SIE identification fields. The GDB helper now emits a
      dedicated `tfm_s.elf` runtime script. Post-fix evidence
      `build/qbox-fvp-rd-aspen/gdb-runtime-fast-after-cpu0secctrl-20260524-v1/`
      shows the previous fault registers are zero and TF-M stops through
      `tfm_core_panic()` -> `tfm_hal_system_halt()` after
      `tfm_core_init()` returns non-success (`r0 = 0xffffff03`). The same
      sample resolves AP/Linux CPU#0 to `cpu_do_idle+8` and primary UART
      reaches SCMI probe, `/sbin/init`, and `systemd 257.4`. SCP-Firmware
      remains symbol/source-only until a live SCP CPU model replaces the
      current service-model strategy.
- [x] T019BF Split `tfm_core_init()` with targeted GDB traces and fix the
      newly identified RSE MPC/DMA350 reset-value gaps. The helper now emits
      `tfm-static-boundary-trace.gdb` and `tfm-core-init-trace.gdb`.
      Static-boundary evidence first showed the VM0/VM1 MPC `PIDR0` and block
      registers shifted one word early in Lua `load.data`; after shifting
      those keys, GDB reaches `SUCCESS static-boundary return`. The next GDB
      split isolated `tfm_hal_platform_init()` failing at the DMA350 init
      branch; QBox now exposes `DMA_INFO.IIDR = 0x3a00043b` and
      `DMA_INFO.AIDR = 0x00000000`, with component-test coverage. Post-fix
      evidence
      `build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-dma-iidr-fix-20260524-v1/`
      reaches `SUCCESS tfm_core_init common-return pc=0x10000048`. The next
      blocker is a later `tfm_spm_partition_psa_panic()` path, not
      static-boundary, `CPU0_SECCTRL_BASE_S`, or DMA350 initialization.
- [x] T019BG Extend the reusable GDB environment to split TF-M secure
      partition panics. The helper now emits and can run
      `tfm-partition-panic-trace.gdb`, `tfm-its-init-trace.gdb`, and
      `tfm-ps-init-trace.gdb`. Evidence from
      `build/qbox-fvp-rd-aspen/gdb-partition-panic-trace-20260524-v1/`
      attributed the first post-core-init panic to `TFM_SP_ITS`, while the
      corrected no-boot-flash-DMI PS trace
      `build/qbox-fvp-rd-aspen/gdb-ps-init-trace-no-bootflash-dmi-20260524-v1/`
      shows ITS no longer panics and PS now fails in `tfm_ps_init()`.
- [x] T019BH Add the RD-Aspen RSE Strata flash compatibility erase behavior
      needed by the generated TF-M storage driver. The built
      `cfi_strataflashj3_erase()` path programs `0xff` bytes during sector
      erase, so QBox keeps default NOR `old & data` byte-program semantics but
      lets the RSE boot-flash instances opt into `program_ff_sets_bits=true`.
      `strata_flash_j3-tests` covers the optional behavior. Boot-flash DMI is
      now documented as unsafe for TF-M storage debug because the
      `QBOX_RDASPEN_BOOT_FLASH_DMI=true` ITS trace still failed while hiding
      command-write side effects.
- [x] T019BI Fix or faithfully model the TF-M Protected Storage prepare path.
      The PS object-table trace showed the failure was not the wipe path but
      the generated RD-Aspen Strata flash erase convention: TF-M programs a
      sector-aligned `0xff` byte for sector erase. QBox now exposes the
      opt-in `program_ff_erases_sector` behavior on the RD-Aspen RSE boot
      flash instances. Evidence
      `build/qbox-fvp-rd-aspen/gdb-ps-sector-erase-fix-20260524-v1/` proves
      `psa_its_set(uid=1)` returns success, the saved metadata is read back,
      `ps_set_active_object_table` sees `state0=0x2 state1=0x1`, and the run
      advances through RSE measured boot and AP Linux/systemd evidence.
- [x] T019BJ Fix or faithfully model the TF-M NS mailbox agent runtime path.
      After T019BI, the MHUv3 SCMI responder now handles System Power
      `SYS_POWER_STATE_NOTIFY` (`protocol=0x12`, `msg=0x5`) and the trace in
      `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-scmi-notify-20260524-v2/run/mhuv3-trace.log`
      shows `status=0x0`. A focused NS mailbox trace then showed the first
      BusFault happened inside `mhu_v3_x_driver_init()` while reading
      `MHU0_SENDER_BASE_S + CTRL_AIDR` at `0x50160fcc`; QBox had no RSE-local
      MHU0/MHU2 frames at `0x50160000/0x50170000` and
      `0x501a0000/0x501b0000`. QBox now maps these secure RSE local MHUv3
      sender/receiver frames with separate local pairs, and
      `build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-local-mhu-20260524-v1/`
      no longer hits the NS mailbox BusFault; TF-M samples in
      `psa_wait_thread_fn_call()`, Linux reaches serial login, and
      `mhuv3-trace.log` records RSE local MHU2 receiver doorbells. The later
      AP-RSE bridge/IRQ run
      `build/qbox-fvp-rd-aspen/gdb-rse-mhu-irq-map-20260524-v1/` pairs the
      AP-visible and RSE-local secure MHU paths as `ap_s_to_rse` and
      `rse_to_ap_s`, routes RSE MHU0/MHU2 receiver IRQs to TF-M IRQs 41/45,
      proves AP doorbells reach RSE and RSE replies reach the AP mailbox, and
      records the FVP runtime marker
      `SCMI Comms subscribed to power state notifications`. Current
      short-timeout runtime
      `build/qbox-fvp-rd-aspen/rse-current-runtime-markers-postlogin-20260524-v1/`
      repeats the subscription marker and measured-boot markers through
      `BL_33` before timing out at U-Boot.

## Milestone 2: Boot Media And NVM

- [x] T020 Implement read-only file-backed ROM behavior. The RSE Lua platform
      loads `QBOX_RDASPEN_RSE_ROM` into `rse_rom` as `gs_memory` with
      `read_only = true`, `shared_memory = true`, and `load = {bin_file =
      rse_rom, offset = 0}`. V004 records the deploy ROM in
      `input_artifacts.rse_rom` and `runtime_artifacts.rse_rom`.
- [x] T021 Implement writable file-backed flash behavior with per-run copied
      images. The runner copies RSE/AP flash into `writable-images/`,
      decompresses gzip deploy images into per-run raw images, and passes the
      raw files to the `strata_flash_j3` boot-flash model. V004 records
      `copied_writable_artifacts.rse_flash`, `copied_writable_artifacts.ap_flash`,
      and `flash_image_preparation.state =
      gzip_decompressed_for_qbox_raw_memory`. Cross-reboot persistence remains
      T076.
- [x] T022 Implement OTP/NVM read/write and lock-after-provision behavior.
      `rse_lcm` now routes TF-M-visible OTP window writes through OTP-specific
      semantics, optionally writes the updated OTP window back to the active
      `otp_image`, and locks later OTP writes after the secure-provisioning
      `SP_ENABLE` magic when `otp_lock_after_provision` is enabled. The RSE
      Lua platform exposes `QBOX_RDASPEN_RSE_OTP_WRITEBACK` and
      `QBOX_RDASPEN_RSE_OTP_LOCK_AFTER_PROVISION`; the runner enables
      writeback only for per-run copied writable OTP images. `rse_lcm-tests`
      verifies file writeback and lock-after-provision behavior, and the
      bounded runtime
      `build/qbox-fvp-rd-aspen/rse-t022-otp-runtime-20260525-v1/` records
      OTP writeback to the per-run copy while reaching RSE runtime chainload,
      SCMI subscription, and measured boot through `BL_33`.
- [x] T023 Load `combined_provisioning_message.bin` at RSE SRAM offset
      `0x20000`. The RSE Lua platform maps this through `rse_vm1` with
      `load = {bin_file = provisioning_bundle, offset =
      RSE_PROVISIONING_OFFSET}`, where `RSE_PROVISIONING_OFFSET = 0x00020000`.
      V004 records the bundle path in `input_artifacts.provisioning_bundle`
      and `runtime_artifacts.provisioning_bundle`.
- [x] T024 Add CCI/Lua parameters for `VMADDRWIDTH`, reset syndrome, DMA boot
      enable, and RSE CPU hold defaults. The RSE Lua platform now exposes
      `QBOX_RDASPEN_RSE_VMADDRWIDTH`, `QBOX_RDASPEN_RSE_RESET_SYNDROME`,
      `QBOX_RDASPEN_RSE_CPUWAIT`, `QBOX_RDASPEN_RSE_DMA_BOOT_EN`, and
      `QBOX_RDASPEN_RSE_DMA_BOOT_ADDR`, preserving the FVP defaults
      `VMADDRWIDTH=18`, reset syndrome `0x80000000`, CPUWAIT `0xf`, and
      DMA boot enable `1`. `rse_sysctrl-tests` verifies CCI override of the
      reset defaults, and
      `build/qbox-fvp-rd-aspen/rse-t024-params-smoke-20260525-v3/` verifies
      Lua parsing plus `rse vmaddrwidth: 18` / `rse vm size: 0x40000`.
- [x] T025 Add unit tests for ROM, flash, OTP, and provisioning bundle loading.
      `memory-tests` now verifies read-only ROM image loading and provisioning
      bundle offset loading, `strata_flash_j3-tests` verifies the loader path
      used by RSE boot flash, and `rse_lcm-tests` verifies OTP image loading
      into the LCM OTP window. The focused ctest run for
      `memory-tests|strata_flash_j3-tests|rse_lcm-tests` passed.
- [x] T026 Verify RSE reaches `Jumping to the first image slot`. Current
      QBox proof is
      `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/qbox-rse.log`;
      FVP comparison proof is
      `build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1/terminal_uart_5000.log`.
      Both reach this runtime TF-M chainload marker after RSE-to-SCP/AP
      power-on, matching the corrected V007 marker ordering.

## Milestone 3: RSE ATU

T019G added the first touched-register-only `rse_atu` bring-up component.
T019V upgraded it into an initiator-backed translation model for the TF-M BL2
host-window path. T034 adds first-pass translation fault handling. T034A uses
ATUBC page-size and region-count fields for translation decisions. T034B adds
ATURAV page-shift overflow rejection and translated-DMI range hardening while
preserving TF-M two's-complement negative add-values. Current runtime evidence
shows Safety Island ATU programming reaches SI CL0 release and measured-boot
markers with translated DMI enabled. Full ATU fidelity still needs
default-safe DMI evidence, remaining page-boundary/status semantics, and
richer fault status.

- [x] T030 Create `rse_atu` SystemC component with target and initiator
      sockets.
- [x] T031 Implement ATU registers touched by TF-M RSE boot.
- [x] T032 Implement non-secure window translation for
      `0x6000_0000..0x6fff_ffff`.
- [x] T033 Implement secure window translation for
      `0x7000_0000..0x7fff_ffff`.
- [x] T034 Implement disabled-region, out-of-range, and permission fault
      handling.
- [x] T034A Honor ATUBC page-size and supported-region count in translation.
- [x] T034B Reject ATURAV page-shift overflow and clamp translated-DMI ranges
      without breaking TF-M two's-complement negative add-values.
- [x] T035 Add DMI disable or invalidation on mapping updates.
- [x] T036 Add component tests for translation and fault behavior.
- [x] T037 Validate Safety Island ATU verification no longer needs bypasses.
      Runtime `build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1/`
      records SI ATU regions 0..16, SI CL0 reset release and post-load
      completion, measured-boot markers through `BL_33`, and
      `first_failing_register_access: none`.

## Milestone 4: MHUv3 Doorbell Model

- [x] T040 Split current `mhuv3_stub` hardcoded SCMI responder from register
      model behavior.
      `mhuv3_stub::mhuv3_frame_model` now owns the PBX/MBX register storage,
      channel decode, status/mask/control fields, feature/ID registers, and
      combined interrupt status calculation. The SCMI, RSE direct-boot, reset,
      and RPMsg service-model behavior remains layered in the `mhuv3_stub`
      wrapper.
- [x] T041 Implement reusable MHUv3 PBX frame model.
      The frame model is directly unit-tested as a PBX frame with configured
      channel count, feature/ID registers, doorbell status, interrupt status,
      interrupt enable, and combined interrupt summary behavior.
- [x] T042 Implement reusable MHUv3 MBX frame model.
      The same frame model is directly unit-tested as an MBX frame with default
      masked status, mask clear, combined interrupt summary, and receiver clear
      behavior.
- [x] T043 Implement doorbell status, set, clear, mask, and interrupt behavior.
      The low-level frame behavior is split into the reusable frame model while
      the Lua-visible compatibility component remains named `mhuv3_stub`; it
      implements the PBX set path, MBX status/mask/clear registers, and IRQ
      assertion/deassertion needed by the RSE BL2 SCMI path.
- [x] T044 Add peer binding between PBX and MBX frames.
      `mhuv3_stub` now uses a `pair` parameter to route PBX responses to the
      matching MBX frame instead of relying on one global MBX pointer.
- [x] T045 Add channel count and feature CCI parameters.
      `mhuv3_stub` now exposes `channel_count`, `feat_spt0`, `feat_spt1`,
      `iidr`, and `aidr` as CCI parameters. `DBCH_CFG0`, valid doorbell
      channel decoding, combined interrupt status, and the compatibility
      doorbell notify channel follow the configured channel count, with
      defaults preserving the previous 128-channel behavior. `mhuv3_stub-tests`
      verifies a 4-channel PBX instance with custom feature and ID register
      values.
- [x] T046 Add component tests for PBX-to-MBX delivery and interrupt clearing.
      `mhuv3_stub-tests` verifies the RSE-BL2 Power Domain transport response,
      ACK bit 1 delivery, fixed multi-channel MHUv3 discovery, AP-RSE
      PBX-to-MBX doorbell forwarding, receiver clear propagation back to the
      sender PBX status, and the AP/SI CL1 RPMsg name-service virtqueue
      injection used by the first T019AV service-model increment.
- [x] T047 Wire RSE-SCP MHUv3 and validate SCMI init logs.
      Runtime evidence from
      `build/qbox-fvp-rd-aspen/rse-t019ak-mhuv3-scmi-20260523-v5/`
      records `Init SCMI comm to SCP succeeded`.
- [x] T048 Wire AP-RSE MHUv3 and validate secure-service transport discovery.
      AP-RSE PBX/MBX frames are now wired and expose enough multi-channel
      doorbell behavior for AP TF-A `mhu_init_sender()` to pass. Follow-up AP
      SDS/NV counter/DRAM work proves AP BL2 now loads and measures runtime
      images through BL33 and boots BL31.
- [x] T048B Wire AP-SI SCMI MHUv3 frames behind the AP ATU-translated
      host-physical windows. Runtime
      `build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1/`
      records `SCMI driver initialized` in BL31 after the previous
      `PLAT_CSS_MHU_BASE + 0x10` abort is removed. Later V038S evidence
      extends the AP/SI CL1 doorbell service-model path by emulating remote
      transfer completion and PBX combined IRQ delivery for synthetic
      auto-ack/RPMsg-NS PBX writes.
- [x] T049 Keep direct-boot compatibility responder available only in direct
      mode. The legacy automatic doorbell success reply is now gated by the
      `direct_boot_compat` CCI parameter, which defaults to false. The direct
      primary-compute Lua config opts into this compatibility mode, while RSE
      MHU frames keep the default strict doorbell behavior unless explicitly
      configured otherwise. `mhuv3_stub-tests` covers both the opt-in
      compatibility reply and a strict doorbell frame that does not synthesize a
      reply.

## Milestone 5: SCP Strategy And RSE-SCP/AP Boot Handoff

- [x] T050 Decide MVP SCP strategy: protocol-correct SCP service model or real
      Safety Island CL0/SCP execution.
- [x] T051 If using service model, implement SCMI request decode from shared
      memory instead of fixed success responses.
- [x] T052 If using service model, emit fidelity label and remaining real-SCP
      gap into `result.json`. The runner now emits `scp_service_model` with
      the selected strategy, endpoint fidelity, live-SCP-GDB availability, and
      the remaining real-SCP execution gaps.
- [x] T053 Model AP secure flash and AP shared SRAM windows required by RSE BL2.
      Current implementation provides the initial AP flash/raw-image path and
      ATU-reachable AP/SI host windows needed for BL2 bring-up. Several windows
      are still static memory placeholders, so fidelity work remains open in
      T019W and later SCP/SI tasks.
- [x] T054 Model SI CL0 image loading path. Runtime
      `build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1/`
      records image 3 RAM load to `0x70083c00`, key-hash match, ATU region
      programming, SI CL0 reset release, and SI CL0 post-load completion.
- [x] T055 Model SI CL1 image loading path for CFG2. The same runtime records
      image 4 RAM load to `0x70185c00`, key-hash match, SI CL1 post-load
      completion, and non-zero host SI CL1 SRAM runtime data.
- [x] T056 Implement RSE-to-SCP AP power-on command path.
      `mhuv3_stub` decodes the SCMI Power Domain state-set request from shared
      memory and runtime evidence records `RSE to SCP SCMI power on AP
      succeeded`.
- [x] T057 Hold AP primary core in reset until the modeled handoff releases it.
      The opt-in AP CPU path now sets `start_in_reset = true` for all AP CPUs,
      keeps AP0 powered but reset-held, leaves secondary CPUs powered off for
      later PSCI, and releases AP0 only through the modeled RSE/SCP power-on
      reset signal.
- [x] T058 Revisit AP CPU EL3/secure-world configuration for TF-A boot.
      AP CPU EL3/secure-world boot is no longer blocked at the earlier BL31
      RAS/system-register path. Runtime
      `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/`
      reaches RSE/SCP handoff, AP BL2/BL31, measured boot through `BL_33`,
      Linux login, and post-login driver probes. The short current GDB bundle
      `build/qbox-fvp-rd-aspen/gdb-all-targets-current-dmi-20260525-v1/`
      confirms the AP GDB target is attachable, samples AP CPU0 in TF-A BL2
      SHA-256 image verification at PC `0x8ec00`, and shows the secure console
      has already reached `BL2: Booting BL31`, BL31 runtime services, SCMI,
      GICv3, and PFDI initialization. Secure-service fidelity remains open in
      T061-T064, and PSCI/FWU reboot behavior remains covered by later tasks.
- [x] T059 Verify RSE console reports
      `RSE to SCP SCMI power on AP succeeded`.
- [x] T059B Verify Primary Compute reaches Linux login through RSE-oriented
      boot. `build/qbox-fvp-rd-aspen/rse-post-login-threaded-input-20260524-v3/`
      reaches `fvp-rd-aspen login:`, logs in as `root`, reaches the root
      prompt, and completes the short post-login probe sequence. A later
      marker-focused current run
      `build/qbox-fvp-rd-aspen/rse-current-runtime-markers-postlogin-20260524-v1/`
      reaches RSE runtime measured boot and SCMI subscription markers but
      times out at U-Boot before Linux login because the timeout was kept
      short. Current proof
      `build/qbox-fvp-rd-aspen/rse-t019aw-rpmsg-seed-indexed-preset-20260524-v1/`
      again reaches Linux login/root prompt with `--post-login-probe` and no
      runner timeout.

## Milestone 6: Measured Boot And Secure Services

- [x] T060 Validate measured boot markers for `BL1_2`, `BL2`, `SI_CL0`,
      `AP_BL2`, `RT_0`, `SECURE_RT_EL3`, `SECURE_RT_EL1_SPMD`, and `BL_33`.
      Runtime
      `build/qbox-fvp-rd-aspen/rse-current-runtime-markers-postlogin-20260524-v1/`
      records all of these marker hits in `result.json`; `qbox-rse.log` also
      includes the runtime `RT_0`, `FW_CONFIG`, `SECURE_RT_EL3`,
      `SECURE_RT_EL1_SPMD`, and `BL_33` measurement lines.
- [ ] T061 Wire AP secure world SE-Proxy transport to RSE.
      Diagnostic runtime
      `build/qbox-fvp-rd-aspen/rse-t061-secure-service-diag-20260525-v1/`
      proves Linux FF-A/TEE discovery is present and the SE-Proxy/SMM Gateway
      SP images load, but secure-console logs still report SE-Proxy PSA-call
      failures, repeated `SP is busy`, and SMM Gateway direct-request errors.
      Follow-up MHU trace
      `build/qbox-fvp-rd-aspen/rse-t061-secure-service-mhu-20260525-v1/`
      pairs all AP secure-service request doorbells with RSE responses
      (`39/39`, missing `0`), so the remaining split is above the AP-RSE MHU
      doorbell bridge: AP secure partition FF-A/RPC session handling and the
      SE-Proxy SP panic/data-abort path. A focused FWU/PS GDB trace at
      `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/`
      shows the later sampled request as a Protected Storage SET
      (`handle=0x40000101`, type `1001`) with AP SE-Proxy waiting in
      `secure_storage_ipc_set()` while RSE/TF-M is inside ITS flash
      delete/compaction/writeback. The AP-RSE MHU trace pairs 12 of 13
      requests and leaves only the in-flight `0x80060d01` request unanswered
      at the bounded sample point, so T061 remains open at secure-service
      semantics rather than basic doorbell wiring. A later focused SFCP/FWU
      GDB trace
      `build/qbox-fvp-rd-aspen/gdb-t061-sfcp-atu-trace-20260525-v1/`
      identified one concrete transport bug below those semantics:
      `sfcp_protocol_pointer_access_deserialize_msg()` saw `msg_len=0x39` and
      returned `-135` before any `comms_atu_alloc_region()` call because an
      unrelated AP-SI/PFDI monitor PBX doorbell leaked into the AP-to-RSE MHU
      pair through the old named-pair fallback. `mhuv3_stub` now forbids
      global fallback for non-empty named pairs, and
      `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/`
      confirms the AP/RSE GDB ports still work after the fix. The initial
      boot-time `psa_fwu_query: -135` caused by cross-paired MHU status is
      gone in that short post-fix run; T061 remains open on later
      SE-Proxy/SMM Gateway secure-storage and secure-service paths where AP
      SE-Proxy waits in `secure_storage_ipc_set()` and RSE/TF-M is executing
      ITS flash erase or delete/writeback work. The newer post-login
      `rse-t065-secure-service-probe-20260525-v1` artifact shows a distinct
      FWU discovery failure returning `-135` again and then panicking because
      the Trusted Services FWU provider keeps a null `update_agent`; this
      current recurrence is tracked by V038K and must not be conflated with
      the earlier MHU named-pair isolation bug. Marker-gated GDB evidence at
      `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/`
      reaches U-Boot PK/KEK enrollment, then samples the `db` variable path:
      AP SE-Proxy is waiting in `secure_storage_ipc_remove()` with PSA call
      type `1004`, while RSE/TF-M is in SFCP pointer-access deserialization
      and `comms_atu_alloc_region()`. The AP secure-service MHU trace pairs
      104 of 105 channel-1 requests and leaves only the bounded in-flight
      transaction `0x80066901`, so the remaining task is secure-storage
      transaction semantics around UEFI `db`/`dbx`, not basic doorbell
      routing. A later short marker run
      `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/`
      did not reach `2023 bytes read` before the cap, but sampled an earlier
      Protected Storage GET_INFO request (`type=1003`, uid 7): AP SE-Proxy is
      waiting for the MHU sender clear while RSE/TF-M is in the CMU_MHU2
      receive interrupt path. This reinforces that the current evidence shows
      in-flight secure-storage traffic, not absent AP-RSE transport. A
      non-GDB runtime
      `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/` later proves
      PK, KEK, `db`, and `dbx` enrollment all succeed before
      `ExitBootServices`, while the marker-gated GDB run
      `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/`
      again samples an in-flight SE-Proxy Protected Storage GET_INFO request
      (`type=1003`, uid 6). T061 remains open for the post-login secure
      service validation path, not for U-Boot secure-variable enrollment. A
      user-requested short Linux-marker GDB run
      `build/qbox-fvp-rd-aspen/gdb-user-linux-marker-current-20260525-v1/`
      waited 120.038 seconds for `Linux version` and did not reach it; all
      live target probes still attached. The sampled state is AP SE-Proxy in
      `secure_storage_ipc_set(uid=7, data_length=2)` waiting on
      `mhu_v3_x_doorbell_read()`, while RSE/TF-M is erasing PS/ITS flash via
      `tfm_its_remove()`. This keeps the immediate short-timeout blocker in
      secure-storage transaction progress before Linux, not in GDB setup.
      V038S fixes a separate AP/SI CL1 synthetic-MHU txdone/IRQ issue for
      `400b0000.mhu`. The copy-flash runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/`
      reaches Linux, completes the post-login probe, and removes the AP/SI
      spurious-PBX and `MBOX_TX_QUEUE_LEN` warnings. The 30-second no-trace
      secure-service runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-30s-notrace-20260527-v1/`
      proves the AP secure-world SE-Proxy/RSE path now completes IAT and ITS
      userspace tests with rc 0. T061 remains open until the remaining
      Protected Storage test and FWU/UEFI storage paths complete.
- [x] T062 Validate Initial Attestation request path.
      Earlier QBox post-login secure-service probes timed out under shorter
      caps while secure-console logs reported SE-Proxy/SMM Gateway messages.
      The 2026-05-27 bounded no-trace runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-30s-notrace-20260527-v1/`
      now reaches Linux, completes the post-login probe, runs
      `psa-iat-api-test`, prints the PSA Architecture Test Suite pass summary,
      and records `secure_psa_iat_api_test_rc=0`. The reference FVP artifact
      `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/` also
      completes IAT with rc 0, so this path is no longer a QBox open item.
- [ ] T063 Validate Protected Storage and Internal Trusted Storage paths.
      The 2026-05-27 bounded no-trace runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-30s-notrace-20260527-v1/`
      completes `psa-its-api-test` with rc 0 and all ten ITS tests passing.
      It also proves that the previous immediate `libpsats` RPC-open failure
      is no longer the active blocker. Protected Storage remains open:
      `psa-ps-api-test` passes tests 401 and 402, enters test 403
      (`Insufficient space check`), then returns 124 at the 30-second command
      cap. FVP comparison completes `psa-its-api-test` with rc 0, and a
      PS-only FVP probe enters the PS test sequence through test 409 before
      the host-side post-login cap, confirming that FVP progresses further
      than QBox on the PS path. The runner now supports
      `--secure-service-probe-tests ps`, and the PS-only QBox runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-60s-20260527-v1/`
      still times out in PS test 403 after tests 401/402 pass. This confirms
      the remaining PS gap is not caused by the preceding IAT/ITS commands.
      The runner now also classifies requested secure-service non-zero return
      codes as `qbox_secure_service_probe_failed:*`, so a completed boot with
      `secure_psa_ps_api_test_rc=124` no longer appears as a passing
      secure-service validation artifact. V038AM adds structured
      secure-service progress extraction so future `result.json` files record
      whether focused PS test 403 reached `[Check 1]`, a specific
      insufficient-space UID, and the cleanup phase before timeout.
      V038U fixes a separate per-run writable-flash backing-size bug: the RSE
      and AP raw flash copies are now padded with erased `0xff` bytes to the
      QBox Strata device size before writeback is enabled. The padded
      PS-only runtime records no `backing_file` range errors and writes
      Strata stats, but `psa-ps-api-test` still returns 124 in PS test 403.
      A follow-up no-copy control run keeps deploy flash images unmodified,
      records `backing_write_ops=0`, and still times out in PS test 403,
      narrowing the remaining blocker away from host backing-file writeback
      and toward TF-M Protected Storage/Strata command workload completion.
      After deferred Strata backing-write fixes, a stats-disabled fresh
      writable-flash run
      `build/qbox-fvp-rd-aspen/rse-ps403-nostats-deferred-20260527-v1/`
      persisted UEFI variables and reached EFI boot before the short cap. Two
      second-boot runs from those persisted writable flash images reached
      Linux, root shell, SI/RPMsg/virtio/ethsi1 driver evidence, secure-service
      diagnostics, and focused PS test 403. The 185-second run timed out in
      `[Check 1] Overload storage space`; the 260-second run progressed to
      `UID 21 set failed due to insufficient space` and
      `Remove all registered UIDs`, then timed out with
      `qbox_secure_service_ps403_cleanup_timeout:uid_21`. This confirms the
      active T063 gap is PS403 cleanup/second-overload completion, not Linux
      driver setup, UEFI variable persistence, stats overhead, or raw
      backing-file coverage.
      The current GDB split narrows one QBox path to SE-Proxy
      `secure_storage_ipc_set()` waiting for an RSE PS SET response while
      RSE/TF-M executes `tfm_its_remove()` through flash filesystem
      compaction and `cfi_strataflashj3_program()`. Additional GDB evidence
      `build/qbox-fvp-rd-aspen/gdb-t064-ps-object-trace-20260525-v1/`
      proves PS object-table initialization, authentication, key derivation,
      and RSE flash erase calls, while
      `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/` samples
      a live Protected Storage GET_INFO transaction. ITS is now validated; the
      remaining T063 work is Protected Storage throughput/completion through
      the TF-M ITS/PS flash filesystem and Strata flash writeback path.
      A 2026-05-28 byte-scoped `0xff` program experiment was rejected. With
      RD-Aspen Strata sector promotion disabled, the persisted-flash second
      boot reached RSE BL_33 and U-Boot bootflow, but U-Boot reported
      `Cannot initialize UEFI sub-system, r = 7`, failed PK/KEK/db/dbx
      enrollment, fell back to network boot, and timed out before Linux. The
      platform keeps the sector-aligned `0xff` compatibility erase behavior
      because the active TF-M FVP Strata erase helper emits `0xff` byte
      programs and the restored setting reaches Linux, root shell, driver
      probes, secure-service diagnostics, and PS403 `[Check 1]` again in
      `build/qbox-fvp-rd-aspen/rse-strata-ff-sector-restored-secondboot-185s-20260528-v1/`.
      A 2026-05-28 marker recheck adds explicit PS403 result markers for
      `[Check 1]`, UID exhaustion, cleanup, and `[Check 2]`. The rebuilt QBox
      platform and runner smoke pass, and
      `build/qbox-fvp-rd-aspen/rse-ps403-progress-markers-185s-20260528-v2/`
      records Linux login/root shell, all post-login driver probes, secure
      diagnostics, `ps_test_403`, `ps_insufficient_space`, and
      `ps_check_1_overload` before timing out at
      `qbox_secure_service_ps403_timeout:check_1`. Full boot-flash DMI and a
      2048-byte CC3XX DMA chunk were both rejected: the former creates an empty
      ITS layout and fails partition initialization before Linux, while the
      latter invalidates the SI CL1 primary image. These rechecks keep T063
      focused on Protected Storage flash-filesystem throughput/completion
      rather than marker extraction, Linux driver probing, full flash DMI, or
      CC3XX chunk sizing.
      A 2026-05-28 clean persisted-flash recheck
      `build/qbox-fvp-rd-aspen/rse-ps403-deferflush0-240s-20260528-v1/`
      reached Linux login/root shell, all post-login driver probes,
      secure-service diagnostics, and PS403 `[Check 1]`, but still timed out
      without an insufficient-space UID. A dirty-flash baseline using the
      prior fastaccess run's writable images timed out before Linux and is not
      comparable clean-seed PS403 evidence. A temporary Strata 1-byte fast-path
      source experiment also regressed to pre-login timeout at 260 seconds, so
      it was reverted after focused tests and serialized `platforms-vp`
      rebuilds. T063 remains open on faithful PS/ITS compaction completion,
      not on these rejected shortcuts. V038AZ adds a persistent RSE flash
      storage-state inspector and compares FVP/QBox PS403 writable images
      against the deploy image baseline. The FVP PS403-pass image dirties all
      PS and ITS sectors, while the best QBox UID21 timeout image changes only
      `9` PS sectors and `1` ITS sector. This confirms the remaining gap is
      workload completion through the TF-M PS/ITS flash filesystem rather than
      marker extraction, Linux driver probing, or host backing-file writeback.
- [ ] T064 Validate UEFI variable storage through SMM Gateway and RSE Protected
      Storage.
      The secure-service probe records U-Boot/secure-console SMM Gateway
      failures and detects that `uefi-test` is absent from the current rootfs.
      This remains open for both runtime behavior and image content; the current
      diagnostic also shows SMM Gateway FF-A device discovery but repeated
      `sp_msg_send_direct_req(): error -4` and `Failed to read PK`. The FVP
      post-login probe also reports `uefi-test` absent from the active rootfs,
      so the image-content part is not QBox-specific. The FVP secure console
      also shows early SMM Gateway `-4` and SE-Proxy remove `-140` messages, so
      those startup logs are not sufficient by themselves to classify a QBox
      failure. Current non-GDB evidence
      `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/` proves U-Boot
      secure-variable enrollment for PK, KEK, `db`, and `dbx`, then reaches
      `FWU: ExitBootServices: Booting in regular state` before the short
      Linux-login timeout. Marker-gated GDB remains useful for source-level
      inspection but is not wall-time equivalent: the later
      `build/qbox-fvp-rd-aspen/gdb-exitbootservices-sample-20260525-v1/`
      sample did not reach `ExitBootServices` within 340.108 seconds and
      instead caught SE-Proxy in a Protected Storage GET_INFO transaction
      (`type=1003`, uid 6). T064 remains open only for the missing post-login
      `uefi-test` image content and deeper SMM Gateway validation beyond the
      U-Boot enrollment path.
- [x] T065 Add QBox post-login probes for secure-service userspace tests.
      `scripts/run_qbox_fvp_rd_aspen_rse.py --secure-service-probe` now extends
      the FIFO-backed post-login probe with bounded Trusted Services userspace
      checks. It records binary presence, per-command return codes, completion
      markers, and SE-Proxy/SMM Gateway/UEFI-variable failure detection in
      `result.json` without changing the base boot pass criteria.

## Milestone 7: Secure Firmware Update

- [x] T070A Add a static FWU bank, metadata, and capsule-media inspection
      helper. `scripts/inspect_qbox_fvp_rd_aspen_fwu.py` inspects the local
      RD-Aspen CFG2 deploy artifacts without mutating them and writes
      `fwu-inspection.json` plus `summary.md`.
- [x] T071A Record the current initial RSE/AP A/B bank state. The FWU
      inspection artifact
      `build/qbox-fvp-rd-aspen/fwu-inspect-20260525-v2/` records populated
      primary slots and zeroed secondary slots for BL2, RSE runtime, SI CL0,
      AP FIP, and SI CL1.
- [x] T072A Record the current FWU metadata baseline. The same inspection
      records RSE private metadata replicas at `0x5000` and `0x6000`, AP FWU
      metadata replicas at `0x5000` and `0x6000`, AP metadata version 2,
      active bank 0, previous bank 1, and five CFG2 FWU components.
- [x] T073A Validate the capsule-on-disk input media before runtime FWU. The
      inspection parses VirtIO block 1, finds root-directory `fw.cap`, verifies
      its size against `efi-capsule-update-image.img.uefi.capsule`, and records
      the manifest components `BL2`, `TFM_S`, `SCP-FW`, `FIP`, and `SI-CL1`.
- [x] T073B Add a file-backed runtime FWU probe entry point. The RSE runner
      now accepts `--fwu-probe`, injects the documented capsule-on-disk setup
      commands after Linux login, records FWU command return codes and bank-1
      log markers in `result.json`, and keeps full T073-T076 validation open
      until the capsule is actually applied and reboot persistence is proven.
- [ ] T070 Model RSE flash A/B image banks.
- [ ] T071 Model AP flash A/B FIP banks.
- [ ] T072 Model FWU metadata and RSE private metadata storage. The runner has
      a bring-up-only initializer for invalid RSE private metadata in per-run
      flash copies; this does not close the full FWU metadata model task.
- [x] T073 Validate capsule handoff from VirtIO block 1. The bounded
      `--fwu-probe` run
      `build/qbox-fvp-rd-aspen/rse-t073-fwu-capsule-probe-20260525-v2/`
      reached Linux login, mounted `/dev/vda1` and `/dev/vdb1`, verified
      `/mnt/fw.cap`, copied it into `/boot/EFI/UpdateCapsule/fw.cap`, synced,
      and requested reboot with all FWU probe command return codes equal to 0.
      The run timed out before capsule-application and bank-1 markers, so
      T074-T076 remain open.
- [x] T073C Wire AP QEMU system reset into modeled AP CPU reset sockets. The
      RSE platform now instantiates `reset_gpio` for `ap_qemu_inst` and binds
      its `reset_out` to `ap_cpu_0.reset` through `ap_cpu_3.reset`; the RSE
      runner also builds `reset_gpio` as a required target. Static checks,
      `reset_gpio platforms-vp` build, and the focused
      `reset-test-system:sync-pol=multithread:num-cpu=4:icount=false:threading=MULTI:accel=tcg`
      CTest pass. A 260-second FWU rerun reached U-Boot but not Linux login,
      so it did not yet exercise capsule reboot.
- [x] T073D Preserve QEMU secure MMIO attributes across QBox TLM and enable
      AP GICv3 security extensions for the RSE platform. The marker-gated FWU
      GDB sample
      `build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-gic-secure-20260525-v3/`
      reaches Linux reboot and no longer reproduces the previous BL31
      `plat_gicv3.c:279` secure-SGI assert. The next blocker is now after the
      SGI path: AP cores sample in BL31 `psci_pwrdown_cpu_end_terminal()`, and
      the AP-SI SCMI System Power `protocol=0x12 msg=0x3` request is visible
      without a modeled whole-system reset side effect.
- [ ] T074 Verify RSE log marker `[INF] Attempting to boot image 1`.
- [ ] T075 Verify TF-A log marker `Booting with partition FIP_B`.
- [x] T076A Add per-run flash write-through plumbing for FWU persistence
      evidence. `strata_flash_j3` now exposes an optional `backing_file`
      parameter and writes byte-program/block-erase mutations back to that
      file; `platforms/fvp-rd-aspen-rse/conf.lua` binds RSE/AP flash
      `backing_file` only when `QBOX_RDASPEN_FLASH_WRITEBACK=true`, and
      `scripts/run_qbox_fvp_rd_aspen_rse.py` enables that flag only for
      per-run copied writable flash images. V038U additionally pads those
      per-run RSE/AP writable flash copies to the full QBox Strata model sizes
      with erased `0xff` bytes, preventing PS/FWU writeback beyond the short
      deploy-image length from falling outside the backing file. This closes
      the model and runner plumbing
      prerequisite but does not close T076 until a full FWU reboot proves the
      bank-1 markers and persisted state together.
- [ ] T076 Verify writable flash state persists across reboot.
      Short 2026-05-25 rechecks prove current RSE flash writeback mutates the
      per-run raw image, but do not close this task. The earlier
      `rse-t064-db-nogdb-20260525-v1` raw image is deploy-equivalent despite
      in-run enrollment messages, so it is not valid cross-run persistence
      evidence. A partially mutated aborted image can also trigger
      `FWU: Updating 5 payload(s)` on reuse, which must be separated from a
      clean persisted-state acceptance run.

## Milestone 8: Automation And Reporting

- [x] T080 Add `scripts/run_qbox_fvp_rd_aspen_rse.py` with file-backed
      per-console logs.
- [x] T081 Add `result.json` output for RSE-oriented boot, including boot mode,
      SCP strategy, fidelity labels, input artifacts, copied writable artifacts,
      pass/fail markers, and first failing register access.
- [x] T082 Add `scripts/compare_fvp_qbox_rse_logs.py` with deterministic marker
      comparison and timestamp/path/port normalization.
- [x] T083 Extend `scripts/audit_qbox_fvp_rd_aspen_coverage.py` with RSE
      fidelity labels. The audit now reads RSE-oriented `result.json`, checks
      the expected RSE fidelity label set, reports missing/unexpected labels,
      records explicit debt labels, and keeps primary-compute-only runs as a
      skipped RSE audit. Validation passed for
      `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/coverage-audit.json`
      with no missing RSE labels and debt labels for `mhuv3`, `rse_sacfg`,
      and `rse_nsacfg`.
- [x] T084 Update `tools/qbox/platforms/fvp-rd-aspen/README.md` with RSE mode.
- [x] T085 Update `doc/qbox-fvp-emulation-project.md` with RSE status.

## Verification Checklist

- [x] V001 `git -C tools/qbox diff --check`
- [x] V002 `cmake --build tools/qbox/build --target cpu_arm_cortexM55 nvic_armv7m --parallel 8`
- [x] V003 `cmake --build tools/qbox/build --target platforms-vp --parallel 8`
- [x] V003B `cmake --build tools/qbox/build --target platforms-vp keep_alive router gs_memory loader char_backend_file char_backend_stdio uart-pl011 cpu_arm_cortexM55 nvic_armv7m remote_cpu --parallel 8`
- [x] V003C `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 5 --out-dir build/qbox-fvp-rd-aspen/rse-remote-cpu-trace-20260520-v3`
- [x] V003D `cmake --build tools/qbox/build --target cc3xx dma350 platforms-vp --parallel 8`
- [x] V003E `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 8 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v1`
- [x] V003F `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-run-20260521-v1`
- [x] V003G `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|dma350-tests' --output-on-failure`
- [x] V003H `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=120 QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=240 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-trace-20260521-v2`
- [x] V003I `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=80 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 12 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-qemu-trace-20260521-v2`
- [x] V003J `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003K `git -C tools/qbox diff --check`
- [x] V003L `cmake --build tools/qbox/build --target dma350 dma350-tests --parallel 4`
- [x] V003M `ctest --test-dir tools/qbox/build -R 'dma350-tests|cc3xx-tests' --output-on-failure`
- [x] V003N `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003O `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=260 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-dma350-fill-20260521-v4`
- [x] V003P `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --qemu-trace --out-dir build/qbox-fvp-rd-aspen/worker-1-task5-rse-smoke-20260520T162759Z`
- [x] V003Q `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003R `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003S `cmake --build tools/qbox/build --target rse_sysctrl rse_sysctrl-tests --parallel 4`
- [x] V003T `ctest --test-dir tools/qbox/build -R 'rse_sysctrl-tests|dma350-tests|cc3xx-tests' --output-on-failure`
- [x] V003U `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003V `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=260 QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 60 --out-dir build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v1`
- [x] V003W `QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_LIMIT=220 QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-sysctrl-20260521-v2`
- [x] V003X `cmake --preset gcc`
- [x] V003Y `cmake --build tools/qbox/build --target rse_lcm rse_lcm-tests --parallel 4`
- [x] V003Z `ctest --test-dir tools/qbox/build -R 'rse_lcm-tests' --output-on-failure`
- [x] V003AA `cmake --build tools/qbox/build --target rse_atu rse_atu-tests --parallel 4`
- [x] V003AB `ctest --test-dir tools/qbox/build -R 'rse_atu-tests|rse_lcm-tests' --output-on-failure`
- [x] V003AC `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003AD `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003AE `git -C tools/qbox diff --check`
- [x] V003AF `QBOX_RDASPEN_SYSCTRL_TRACE=true QBOX_RDASPEN_SYSCTRL_TRACE_LIMIT=64 QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=128 QBOX_RDASPEN_LCM_TRACE=true QBOX_RDASPEN_LCM_TRACE_LIMIT=128 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-atu-trace-20260521-v1`
- [x] V003AG `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --check-only --out-dir build/qbox-fvp-rd-aspen/rse-check-only-20260521-v1`
- [x] V003AH `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003AI `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003AJ `git -C tools/qbox diff --check`
- [x] V003AK `cmake --preset gcc`
- [x] V003AL `cmake --build tools/qbox/build --target rse_integrity_checker rse_integrity_checker-tests rse_kmu rse_kmu-tests --parallel 4`
- [x] V003AM `ctest --test-dir tools/qbox/build -R 'rse_(integrity_checker|kmu|atu|lcm)-tests' --output-on-failure`
- [x] V003AN `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003AO `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=256 QBOX_RDASPEN_INTEGRITY_CHECKER_TRACE=true QBOX_RDASPEN_INTEGRITY_CHECKER_TRACE_LIMIT=256 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-integrity-kmu-trace-20260521-v1`
- [x] V003AP `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=512 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=160 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-kmu-pc-trace-20260521-v1`
- [x] V003AQ `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --check-only --out-dir build/qbox-fvp-rd-aspen/rse-fwu-metadata-check-20260521-v1`
- [x] V003AR `xxd -g 1 -l 16 -s 0x5000 build/qbox-fvp-rd-aspen/rse-fwu-metadata-check-20260521-v1/writable-images/rse-flash-image.img`
- [x] V003AS `git -C tools/qbox diff --check`
- [x] V003AT `cmake --build tools/qbox/build --target rse_atu-tests platforms-vp --parallel 4`
- [x] V003AU `ctest --test-dir tools/qbox/build -R 'rse_atu-tests|dma350-tests|cc3xx-tests' --output-on-failure`
- [x] V003AV `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-atu-dmi-20260521-v1`
- [x] V003AW `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-after-atu-dmi-20260521-v1`
- [x] V003AS `xxd -g 1 -l 16 -s 0x5000 build/tmp_baremetal/deploy/images/fvp-rd-aspen/rse-flash-image.img`
- [x] V003AT `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4`
- [x] V003AU `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure`
- [x] V003AV `cmake --build tools/qbox/build --target cc3xx-tests platforms-vp --parallel 4`
- [x] V003AW `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|rse_sam-tests|rse_(integrity_checker|kmu|atu|lcm|sysctrl)-tests' --output-on-failure`
- [x] V003AX `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-aes-20260521-v1`
- [x] V003AY `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=2500 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-aes-trace-20260521-v2`
- [x] V003AZ `cmake --build tools/qbox/build --target rse_kmu-tests cc3xx-tests --parallel 1`
- [x] V003BA `ctest --test-dir tools/qbox/build -R 'cc3xx-tests|rse_kmu-tests' --output-on-failure`
- [x] V003BB `cmake --build tools/qbox/build --target rse_kmu cc3xx platforms-vp --parallel 1`
- [x] V003BC `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=1024 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=5000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-cmac-20260521-v1`
- [x] V003BD `cmake --build tools/qbox/build --target rse_kmu-tests --parallel 1`
- [x] V003BE `ctest --test-dir tools/qbox/build -R rse_kmu-tests --output-on-failure`
- [x] V003BF `cmake --build tools/qbox/build --target rse_kmu platforms-vp --parallel 1`
- [x] V003BG `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003BH `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003BI `QBOX_RDASPEN_KMU_TRACE=true QBOX_RDASPEN_KMU_TRACE_LIMIT=2048 QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_LIMIT=5000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-kce-cm-otp-20260521-v1`
- [x] V003BJ `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-kce-cm-otp-notrace-20260521-v1`
- [x] V003BK `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-flash-prepare-check-20260521-v1`
- [x] V003BL `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-raw-flash-20260521-v1`
- [x] V003BM `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 75 --out-dir build/qbox-fvp-rd-aspen/rse-raw-flash-qemu-trace-20260521-v1`
- [x] V003BN `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 600 --out-dir build/qbox-fvp-rd-aspen/rse-lmots-long-20260521-v1`
- [x] V003BO `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-signature-fail-20260521-v1`
- [x] V003BP `git -C tools/qbox diff --check`
- [x] V003BQ `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4`
- [x] V003BR `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure`
- [x] V003BS `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-sha-state-20260521-v1`
- [x] V003BT `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --qemu-trace --timeout 180 --out-dir build/qbox-fvp-rd-aspen/rse-bl2-qemu-trace-20260521-v1`
- [x] V003BU `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-atu-translation-20260521-v1`
- [x] V003BV `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=4096 QBOX_RDASPEN_HOST_PPU_TRACE=true QBOX_RDASPEN_HOST_PPU_TRACE_LIMIT=128 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-host-ppu-20260521-v2`
- [x] V003BW `cmake --build tools/qbox/build --target host_ppu-tests platforms-vp --parallel 4`
- [x] V003BX `ctest --test-dir tools/qbox/build -R host_ppu-tests --output-on-failure`
- [x] V003BY `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003BZ `git -C tools/qbox diff --check`
- [x] V003CA `cmake --build tools/qbox/build --target cc3xx-tests --parallel 4`
- [x] V003CB `ctest --test-dir tools/qbox/build -R cc3xx-tests --output-on-failure`
- [x] V003CC `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003CD `QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=pka QBOX_RDASPEN_CC3XX_TRACE_LIMIT=200000 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-cc3xx-pka-filter-trace-20260521-v1`
- [x] V003CE `QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=20000 QBOX_RDASPEN_HOST_PPU_TRACE=true QBOX_RDASPEN_HOST_PPU_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --exception-trace --pc-trace-interval 200 --pc-trace-limit 6000 --timeout 240 --out-dir build/qbox-fvp-rd-aspen/rse-t019ac-atu-host-trace-20260521-v4`
- [x] V003CF `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019w-atu-dmi-20260521-v1`
- [x] V003CG `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003CH `git -C tools/qbox diff --check`
- [x] V003CI `cmake --build tools/qbox/build --target dma350-tests platforms-vp --parallel 4`
- [x] V003CJ `ctest --test-dir tools/qbox/build -R dma350-tests --output-on-failure`
- [x] V003CK `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_ATU_TRACE=true QBOX_RDASPEN_ATU_TRACE_LIMIT=20000 QBOX_RDASPEN_DMA350_TRACE=true QBOX_RDASPEN_DMA350_TRACE_FILTER=copy QBOX_RDASPEN_DMA350_TRACE_ADDRESS_MIN=1879048192 QBOX_RDASPEN_DMA350_TRACE_LIMIT=512 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --out-dir build/qbox-fvp-rd-aspen/rse-t019ae-dma350-copy-dmi-20260521-v1`
- [x] V003CL `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003CM `git -C tools/qbox diff --check`
- [x] V003CN `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --boot-enc-trace --out-dir build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-check-20260523-v1`
- [x] V003CO `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 900 --boot-enc-trace --qemu-trace-events in_asm --out-dir build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2`
- [x] V003CP `python3 scripts/audit_qbox_fvp_rd_aspen_coverage.py --runtime-result build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/result.json --runtime-log build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/qbox-rse.log --output build/qbox-fvp-rd-aspen/rse-t019ah-boot-enc-trace-20260523-v2/coverage-audit.json`
- [x] V003CQ `cmake --build tools/qbox/build --target cc3xx-tests --parallel 8`
- [x] V003CR `ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure`
- [x] V003CS `cmake --build tools/qbox/build --target rse_kmu-tests rse_lcm-tests rse_atu-tests --parallel 8`
- [x] V003CT `ctest --test-dir tools/qbox/build -R '^(rse_kmu-tests|rse_lcm-tests|rse_atu-tests)$' --output-on-failure`
- [x] V003CU `cmake --build tools/qbox/build --target mhuv3_stub-tests strata_flash_j3-tests platforms-vp --parallel 8`
- [x] V003CV `ctest --test-dir tools/qbox/build -R '^(mhuv3_stub-tests|strata_flash_j3-tests)$' --output-on-failure`
- [x] V003CW `QBOX_RDASPEN_ATU_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 600 --out-dir build/qbox-fvp-rd-aspen/rse-t019ak-mhuv3-scmi-20260523-v5`
- [x] V003CX `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 600 --out-dir build/qbox-fvp-rd-aspen/rse-t019al-dmi-mhuv3-scmi-20260523-v1`
- [x] V003CY `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --pc-trace --pc-trace-limit 4096 --timeout 750 --out-dir build/qbox-fvp-rd-aspen/rse-t019aq-ap-rse-psa-reply-nodmi-20260523-v1`
- [x] V003CZ `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003DA `git -C tools/qbox diff --check`
- [x] V003DB `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --exception-trace --pc-trace-limit 192 --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-t019az-ap-timer-20260523-v1`
- [x] V003DC `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --exception-trace --pc-trace-limit 224 --timeout 420 --out-dir build/qbox-fvp-rd-aspen/rse-t019ba-ap-si-scmi-mhu-20260523-v1`
- [x] V003DD `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py && luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003DE `cmake --build tools/qbox/build --target char_backend_file platforms-vp --parallel 8`
- [x] V003DF Python import smoke for `drive_post_login_probe()` verifies
      `root`, `echo __QBOX_PROBE_START__`, `modprobe -v arm_si_rproc
      timeout=500`, and `__QBOX_PROBE_DONE__` are written after synthetic
      login/root prompts.
- [x] V003DG `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 45 --out-dir build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DH `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --post-login-probe --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-post-login-fifo-smoke-20260524-v3 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DI `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 120 --out-dir build/qbox-fvp-rd-aspen/rse-baseline-after-fifo-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DJ `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003DK `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003DL `git -C tools/qbox diff --check`
- [x] V003DM `cmake --build tools/qbox/build --target host_scr host_scr-tests platforms-vp --parallel 8`
- [x] V003DN `ctest --test-dir tools/qbox/build -R '^(host_scr-tests|host_ppu-tests|mhuv3_stub-tests)$' --output-on-failure`
- [x] V003DO `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-t019av-cl1-sram-check-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DP `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 300 --out-dir build/qbox-fvp-rd-aspen/rse-t019av-host-scr-cl1-sram-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DQ `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003DR `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-all-targets-v3 --runner-timeout 45 --port-timeout 12 --gdb-timeout 10 --sample-delay 3 --host-sample --host-sample-seconds 8 --launch`
- [x] V003DS `cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8`
- [x] V003DT `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure`
- [x] V003DU `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003DV `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=4096 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 160 --post-login-probe --out-dir build/qbox-fvp-rd-aspen/rse-t019aw-flash-dmi-map-query-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003DW `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --runner-timeout 170 --port-timeout 25 --gdb-timeout 15 --sample-delay 150 --out-dir build/qbox-fvp-rd-aspen/gdb-t019aw-sample-only-20260524-v1`
- [x] V003DX `python3 scripts/runfvp_log_boot.py --timeout 12 --require none --runfvp-verbose --out-dir build/fvp-boot-logs/rse-qbox-debug-telnet-20260524-v1`
- [x] V003DY `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003DZ `python3 scripts/validate_qbox_fvp_rd_aspen_map.py`
- [x] V003EA `git -C tools/qbox diff --check -- platforms/fvp-rd-aspen-rse/conf.lua systemc-components/cc3xx/include/cc3xx.h tests/components/cc3xx/cc3xx-tests.cc platforms/fvp-rd-aspen/README.md`
- [x] V003EB `cmake --build tools/qbox/build --target cc3xx-tests platforms-vp --parallel 8`
- [x] V003EC `ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure`
- [x] V003ED `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_CC3XX_TRACE=true QBOX_RDASPEN_CC3XX_TRACE_FILTER=dma QBOX_RDASPEN_CC3XX_TRACE_LIMIT=2400 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 20 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-bl1-2-cc3xx-dma-trace-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003EE `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 25 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-dtcm-unified-default-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003EF `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-post-alias-v1 --launch --runner-timeout 30 --port-timeout 8 --gdb-timeout 8 --sample-delay 4 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003EG `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003EH `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 45 --port-timeout 8 --gdb-timeout 8 --sample-delay 28 --out-dir build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
- [x] V003EI `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003EJ `cmake --build tools/qbox/build --target memory-tests aarch64-dmi-byte-store-test platforms-vp --parallel 8`
- [x] V003EK `ctest --test-dir tools/qbox/build -R '^memory-tests$' --output-on-failure`
- [x] V003EL `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0`
- [x] V003EM `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0`
- [x] V003EN `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-fd-fix-current-20260524-v1` expected failure at `BL2 image failed to decrypt`
- [x] V003EO `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=false python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 30 --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-off-fd-fix-current-20260524-v1` expected timeout after `BL2 image decrypted successfully`
- [x] V003EP `cmake --build tools/qbox/build --target aarch64-shmem-dmi-byte-store-test --parallel 8`
- [x] V003EQ `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0`
- [x] V003ER `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-byte-store-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0`
- [x] V003ES `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003ET `QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=false QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=false QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 18 --port-timeout 8 --gdb-timeout 8 --sample-delay 10 --out-dir build/qbox-fvp-rd-aspen/gdb-vm-dmi-perm-fix-effective-env-20260524-v1`
- [x] V003EU `cmake --preset gcc`
- [x] V003EV `cmake --build tools/qbox/build --target aarch64-shmem-dmi-external-write-test --parallel 8`
- [x] V003EW `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-external-write-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=true -p log_level=0`
- [x] V003EX `timeout 15s tools/qbox/build/tests/qbox/cpu/aarch64/aarch64-shmem-dmi-external-write-test -S tools/qbox/build/tests/qbox/cpu/aarch64 -B tools/qbox/build/tests/qbox/cpu/aarch64 -p test-bench.enable_dmi=false -p log_level=0`
- [x] V003EY `cmake --build tools/qbox/build --target remote_cpu cortex-m55-vp cortex-m55-dmi-byte-store-test --parallel 8`
- [x] V003EZ `timeout 45s ctest --test-dir tools/qbox/build -R 'cortex_m55_remote_dmi_byte_store_(on|off)' --output-on-failure`
- [x] V003FA `QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 18 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-vm-dmi-remote-fd-fix-20260524-v1` expected timeout after `BL2 image decrypted successfully`
- [x] V003FB `cmake --build tools/qbox/build --target arm_gicv3 arm_gicv3_its arm_smmuv3 cc3xx char_backend_file cpu_arm_cortexA720AE dma350 global_peripheral_initiator gs_memory host_ppu host_scr keep_alive mhuv3_stub pl031 qemu_gpex qemu_hexagon_qtimer router rse_atu rse_integrity_checker rse_kmu rse_lcm rse_sam rse_sysctrl sbsa_gwdt strata_flash_j3 virtio_mmio_blk virtio_mmio_net virtio_mmio_rng remote_cpu platforms-vp --parallel 8`
- [x] V003FC `QBOX_RDASPEN_RSE_VM_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 20 --port-timeout 5 --gdb-timeout 6 --sample-delay 12 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-rse-vm-dmi-remote-fd-fix-20260524-v4`
- [x] V003FD `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003FE `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FF `git -C tools/qbox diff --check`
- [x] V003FG `git -C tools/qemu diff --check`
- [x] V003FH `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 140 --post-login-probe --ignore-fail-patterns --rootfs-bootargs-profile quiet-console --out-dir build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1 --rootfs build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen.wic` expected timeout before login; slim logs preserved in `build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1-slim/`
- [x] V003FI `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1 --launch --sample-only --sample-delay 90 --runner-timeout 125 --port-timeout 18 --gdb-timeout 10 --ignore-fail-patterns`
- [x] V003FJ `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1 --launch --sample-only --sample-delay 1 --runner-timeout 20 --port-timeout 8 --gdb-timeout 8 --host-sample --host-sample-seconds 6 --ignore-fail-patterns`
- [x] V003FK `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003FL `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FM `git -C tools/qbox diff --check -- systemc-components/backends/char_backend_file/include/char_backend_file.h platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FN `timeout 120s cmake --build tools/qbox/build --target char_backend_file platforms-vp --parallel 8`
- [x] V003FO `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 175s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 150 --post-login-probe --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-post-login-threaded-input-20260524-v3 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` login/root/probe complete; top-level result remains `passed=false` because required measured-boot/RSE runtime markers are still incomplete.
- [x] V003FP `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260524-v1 --launch --sample-only --sample-delay 112 --runner-timeout 130 --port-timeout 10 --gdb-timeout 6 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` captured QBox host, TF-M/RSE, SCP symbol state, and AP/Linux GDB evidence; Linux reaches systemd while RSE runtime measured-boot/SCMI-Comms markers remain absent.
- [x] V003FQ `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003FR `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FS `git -C tools/qbox diff --check -- platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FT `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-setup-regenerated-20260524-v3`
- [x] V003FU `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-runtime-fast-after-cpu0secctrl-20260524-v1 --launch --sample-only --sample-delay 112 --runner-timeout 135 --port-timeout 10 --gdb-timeout 6 --ignore-fail-patterns` sampled TF-M runtime panic with clear fault registers and AP/Linux idle/systemd evidence; helper terminated QBox after probes.
- [x] V003FV `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003FW `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003FX `git -C tools/qbox diff --check -- platforms/fvp-rd-aspen-rse/conf.lua systemc-components/dma350/include/dma350.h tests/components/dma350/dma350-tests.cc`
- [x] V003FY `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-static-boundary-success-after-mpc-load-fix-20260524-v1 --launch --sample-only --tfm-static-boundary-trace --runner-timeout 75 --port-timeout 8 --gdb-timeout 6 --ignore-fail-patterns` reached static-boundary success with VM0/VM1 MPC `PIDR0 = 0x65`.
- [x] V003FZ `cmake --build tools/qbox/build --target dma350-tests --parallel 4`
- [x] V003GA `ctest --test-dir tools/qbox/build -R '^dma350-tests$' --output-on-failure`
- [x] V003GB `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003GC `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-dma-iidr-fix-20260524-v1 --launch --sample-only --tfm-core-init-trace --runner-timeout 75 --port-timeout 8 --gdb-timeout 6 --ignore-fail-patterns` reached `SUCCESS tfm_core_init common-return pc=0x10000048`.
- [x] V003GD `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-host-and-live-sample-after-dma-iidr-fix-20260524-v1 --launch --sample-only --host-sample --host-sample-seconds 3 --runner-timeout 75 --port-timeout 8 --gdb-timeout 6 --sample-delay 8 --ignore-fail-patterns` captured QBox host/SystemC/QEMU threads, TF-M/RSE and AP GDB probes, SCP-Firmware symbols, and SI CL1 symbols.
- [x] V003GE `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
- [x] V003GF `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-its-init-step-trace-strata-ff-compat-20260524-v5 --launch --sample-only --tfm-its-init-trace --runner-timeout 75 --trace-timeout 120 --port-timeout 8 --gdb-timeout 6 --ignore-fail-patterns` reproduced ITS storage failure with boot-flash DMI enabled.
- [x] V003GG `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_TRACE=true QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=2000 timeout 120s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --scp-strategy service-model --no-copy-writable-flash --out-dir build/qbox-fvp-rd-aspen/rse-no-bootflash-dmi-its-probe-20260524-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --ignore-fail-patterns` progressed beyond ITS and reached PS partition failure.
- [x] V003GH `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_TRACE=true QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=2000 timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-ps-init-trace-no-bootflash-dmi-20260524-v1 --launch --sample-only --tfm-ps-init-trace --runner-timeout 100 --trace-timeout 130 --port-timeout 8 --gdb-timeout 6 --ignore-fail-patterns` traced PS: `ps_system_wipe_all()` returned success, both `ps_system_prepare()` calls returned `PSA_ERROR_GENERIC_ERROR`, and the panic stack was `tfm_sp_ps_stack`.
- [x] V003GI `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- [x] V003GJ `git -C tools/qbox diff --check`
- [x] V003GK `cmake --build tools/qbox/build --target strata_flash_j3-tests platforms-vp --parallel 4`
- [x] V003GL `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure`
- [x] V003GM `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 4`
- [x] V003GN `ctest --test-dir tools/qbox/build -R mhuv3_stub --output-on-failure`
- [x] V003GO `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
- [x] V003GP `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 190s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 150 --post-login-probe --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --out-dir build/qbox-fvp-rd-aspen/rse-ap-scmi-subscribe-20260524-v1` reached Linux remoteproc attach and RSE measured boot through `RT_0`; timed out before login, and the RSE UART still lacked the subscription marker.
- [x] V003GQ `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 240s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --host-sample --host-sample-seconds 5 --ignore-fail-patterns --runner-timeout 130 --port-timeout 10 --gdb-timeout 10 --sample-delay 95 --out-dir build/qbox-fvp-rd-aspen/gdb-all-targets-after-scmi-patch-20260524-v1` captured TF-M halted in `tfm_hal_system_halt`, AP/Linux target state, SCP-Firmware symbols, SI CL1 symbols, and a QBox host GDB backtrace.
- [x] V003GR `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --tfm-partition-panic-trace --ignore-fail-patterns --runner-timeout 130 --port-timeout 10 --gdb-timeout 8 --trace-timeout 105 --sample-delay 5 --out-dir build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-scmi-notify-20260524-v2` attributed the post-subscribe TF-M BusFault to `TFM_NS_MAILBOX_AGENT` (`pid=0x106`, `entry=0x31045a0d`).
- [x] V003GS `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --tfm-ns-mailbox-trace --ignore-fail-patterns --runner-timeout 130 --port-timeout 10 --gdb-timeout 8 --trace-timeout 105 --sample-delay 5 --out-dir build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-trace-20260524-v1` captured the first NS mailbox BusFault at `BFAR=0x50160fcc`, `mhu_v3_x_driver_init+16`, proving missing RSE-local MHU0 sender MMIO.
- [x] V003GT `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua && python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py && git -C tools/qbox diff --check && cmake --build tools/qbox/build --target platforms-vp --parallel 4 && ./scripts/validate_qbox_fvp_rd_aspen_map.py` passed after adding RSE-local MHU0/MHU2 sender/receiver frames.
- [x] V003GU `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --tfm-ns-mailbox-trace --ignore-fail-patterns --runner-timeout 130 --port-timeout 10 --gdb-timeout 8 --trace-timeout 105 --sample-delay 5 --out-dir build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-local-mhu-20260524-v1` no longer hits the NS mailbox BusFault; TF-M runtime samples in `psa_wait_thread_fn_call()`, AP/Linux resolves to `cpu_do_idle()`, and primary UART reaches `fvp-rd-aspen login:`.
- [x] V003GV `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --host-sample --ignore-fail-patterns --runner-timeout 20 --port-timeout 5 --gdb-timeout 5 --sample-delay 3 --host-sample-seconds 3 --out-dir build/qbox-fvp-rd-aspen/gdb-host-sample-20260524-v1` captured QBox host/SystemC/QEMU thread backtraces by launching `platforms-vp` under GDB, avoiding host ptrace attach restrictions.
- [x] V003GW `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-current-short-all-targets-20260524-v1 --launch --sample-only --sample-delay 28 --runner-timeout 50 --port-timeout 8 --gdb-timeout 6 --host-sample --host-sample-seconds 2 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` verified the current GDB bundle with short timeouts: RSE/TF-M and AP GDB ports were reachable, TF-M/AP/Linux/TF-A/OP-TEE/U-Boot scripts attached, SCP-Firmware and SI CL1 symbols loaded, and QBox host/SystemC/QEMU backtraces were captured.
- [x] V003GX `timeout 240s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v1 --launch --sample-only --sample-delay 150 --runner-timeout 190 --port-timeout 5 --gdb-timeout 8 --host-sample --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` generated the reusable GDB bundle and captured QBox/SystemC/QEMU host backtraces. With conservative debug DMI defaults, RSE/TF-M was still in BL2 flash-copy progress and AP was still at `0x82000`.
- [x] V003GY `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 300s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-rse-ap-linux-20260524-v2 --launch --sample-only --sample-delay 190 --runner-timeout 235 --port-timeout 5 --gdb-timeout 8 --rse-port 12350 --ap-port 12351 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` verified live TF-M/RSE and AP/Linux GDB after Linux start: Linux CPU0 resolves to `cpu_do_idle()`, CPU2 to `change_protection_range()`, TF-M resolves to `__tfm_arch_thread_fn_call_veneer()` / `psa_wait_thread_fn_call()`, SCP-Firmware symbols load, and SI CL1 Zephyr symbols load.
- [x] V003GZ `git -C tools/qbox ls-files --others --exclude-standard -- systemc-components/rse_atu/include/rse_atu.h tests/components/rse_atu/rse_atu-tests.cc`
- [x] V003HA `! rg -n "[ \t]+$" tools/qbox/systemc-components/rse_atu/include/rse_atu.h tools/qbox/tests/components/rse_atu/rse_atu-tests.cc doc/spec/rse-qbox/task.md doc/spec/rse-qbox/evidence.md doc/spec/rse-qbox/design.md doc/spec/rse-qbox/plan.md`
- [x] V003HB `cmake --build build --target rse_atu-tests --parallel 4` from `tools/qbox`
- [x] V003HC `ctest --test-dir build -R '^rse_atu-tests$' --output-on-failure` from `tools/qbox`
- [x] V003HD `git -C tools/qbox diff --check`
- [x] V003HE `cmake --build build --target platforms-vp --parallel 4` from `tools/qbox`
- [x] V003HF `! rg -n "[ \t]+$" tools/qbox/systemc-components/rse_atu/include/rse_atu.h tools/qbox/tests/components/rse_atu/rse_atu-tests.cc`
- [x] V003HG `cmake --build build --target rse_atu-tests --parallel 4` from `tools/qbox`
- [x] V003HH `ctest --test-dir build -R '^rse_atu-tests$' --output-on-failure` from `tools/qbox`
- [x] V003HI `git -C tools/qbox diff --check`
- [x] V003HJ `cmake --build build --target platforms-vp --parallel 4` from `tools/qbox`
- [x] V003HK `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 110s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 85 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-atu-si-load-verify-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` expected timeout, but records SI CL0/CL1 image load, SI ATU regions, RSE runtime measured boot through `BL_33`, and no first failing register access.
- [x] V003HL `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 230s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 200 --port-timeout 8 --gdb-timeout 8 --sample-delay 155 --rse-port 12352 --ap-port 12353 --out-dir build/qbox-fvp-rd-aspen/gdb-debug-linux-sample-20260525-v1` captures live TF-M/RSE, AP firmware/Linux target, SCP-Firmware symbols, and SI CL1 Zephyr symbols; the sampled AP target is still in secure-world/U-Boot rather than Linux kernel execution.
- [x] V003HM `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-debug-env-current-20260525-v2 --runner-timeout 135 --sample-delay 105 --ignore-fail-patterns` regenerates the reusable GDB bundle, and `README.md` now reflects effective environment overrides.
- [x] V003HN `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003HO `! rg -n "[ \t]+$" scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003HP `build/qbox-fvp-rd-aspen/gdb-sp-symbol-sample-20260525-v1/ap-smmgw-symbol-probe.txt` loads SE-Proxy and SMM Gateway symbols into the AP GDB target and proves AP CPU0 is waiting in SE-Proxy `secure_storage_ipc_set(uid=8, data_length=156)` for an RSE Protected Storage response.
- [x] V003HQ `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 225s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-rse-ap-secure-storage-hang-20260525-v1 --launch --sample-only --sample-delay 165 --runner-timeout 185 --port-timeout 12 --gdb-timeout 8 --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` samples the RSE side in `CMU_MHU2_Receiver_Handler()` receiving AP transaction `0x80061501`, while the AP side is still in the SE-Proxy MHU receive path before Linux.
- [x] V003HR `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003HS `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-setup-secure-sp-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` regenerates the GDB environment with TS SP symbols/source maps and README guidance for per-run SE-Proxy/SMM Gateway load-base resolution.
- [x] V003HT `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
- [x] V003HU `python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-setup-login-keepalive-20260525-v1 --copy-writable-flash --post-login-probe --keep-running-after-pass --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` regenerates the GDB bundle with login keepalive and per-run writable-flash options.
- [x] V003HV `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=16000 timeout 285s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 245 --post-login-probe --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` passes with Linux login, post-login probe completion, RSE measured boot through `BL_33`, and no blocker.
- [x] V003HW `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=16000 timeout 340s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1 --launch --sample-only --sample-delay 220 --runner-timeout 260 --port-timeout 8 --gdb-timeout 8 --host-sample --host-sample-seconds 2 --post-login-probe --keep-running-after-pass --copy-writable-flash --ignore-fail-patterns --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` captures QBox host/SystemC/QEMU backtraces, live TF-M/RSE, AP/Linux, TS secure-partition symbol loading, SCP-Firmware symbols, and SI CL1 Zephyr symbols; main-run post-login probe completes.
- [x] V003HX `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py && luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua && git -C tools/qbox diff --check` passed after adding OTP writeback and lock-after-provision controls.
- [x] V003HY `cmake --build tools/qbox/build --target rse_lcm-tests platforms-vp --parallel 4` passed.
- [x] V003HZ `ctest --test-dir tools/qbox/build -R '^rse_lcm-tests$' --output-on-failure` passed, including OTP writeback and lock-after-provision cases.
- [x] V003IA `python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --check-only --out-dir build/qbox-fvp-rd-aspen/rse-t022-otp-check-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` prepared per-run writable RSE/AP flash and RSE OTP copies; it exits with the expected `check_only_no_runtime` blocker because QBox is not launched in check-only mode.
- [x] V003IB `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-t022-otp-runtime-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic` hits the expected short timeout after RSE runtime chainload, SCMI subscription, and measured boot through `BL_33`; the copied OTP image differs from deploy at offsets `0x29a1`, `0x2a01`, and `0x2a61`, proving file-backed OTP writeback affected only the per-run copy.
- [x] V003IC `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 4`
      passed after splitting the reusable MHUv3 frame model.
- [x] V003ID `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure`
      passed, including
      `Mhuv3FrameModelTest.PbxAndMbxDoorbellRegistersAreReusable`.
- [x] V003IE `cmake --build tools/qbox/build --target platforms-vp --parallel 4`
      passed after the MHUv3 frame split.
- [x] V003IF `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 90 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-t040-mhu-frame-refactor-20260525-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
      hit the expected short timeout with no fail patterns, RSE boot and
      RSE/SCP handoff markers true, SCMI subscription reached, and measured
      boot through `BL_33`.
- [x] V003IG `git -C tools/qbox diff --check`
      passed after the MHUv3 frame split and documentation updates.
- [x] V003IH `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`
      passed after adding the bounded secure-service post-login probe mode.
- [x] V003II `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true timeout 420s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 340 --post-login-probe --secure-service-probe --secure-service-probe-timeout 12 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
      passed the base RSE-oriented boot and post-login driver criteria, then
      completed the secure-service probe. It found `psa-iat-api-test`,
      `psa-its-api-test`, and `psa-ps-api-test`, but each timed out with rc
      124; `ts-service-test` and `uefi-test` were absent with rc 127 for
      attempted execution, and secure-console failure classification recorded
      SE-Proxy, SMM Gateway, and UEFI-variable errors.
- [x] V004 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=16000 timeout 960s python3 scripts/run_qbox_fvp_rd_aspen_rse.py --timeout 900 --post-login-probe --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
      rebuilt the required QBox targets, passed with blocker `none`, recorded
      all RSE boot/SCP handoff/measured-boot/Linux marker groups true, and
      completed the Linux post-login driver probe.
- [x] V005 RSE-only boot log reaches TF-M BL1_1 startup.
- [x] V006 Full RSE-oriented boot reaches Linux login. Current proof:
      `build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1/` and
      `build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/` plus
      `build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/`.
      This does not imply full MVP pass; V007 remains open.
- [x] V007 `timeout 360s python3 scripts/runfvp_log_boot.py --timeout 300 --require critical --runfvp-verbose --out-dir build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1`
      passed in 249.492 seconds, and
      `python3 scripts/compare_fvp_qbox_rse_logs.py --fvp build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1 --qbox build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1 --output build/qbox-fvp-rd-aspen/rse-v007-fvp-qbox-compare-20260525-v1/comparison.json`
      passed after aligning the ordered-marker check with the actual FVP/QBox
      RSE runtime sequence.
- [x] V008 `timeout 420s python3 scripts/run_qbox_fvp_rd_aspen_linux.py --skip-build --skip-dtb --no-copy-disk --timeout 360 --post-login-probe --out-dir build/qbox-fvp-rd-aspen/direct-v008-primary-compute-20260525-v1`
      passed in 27.914 seconds, proving the direct primary-compute boot path
      remains available with Linux login, root prompt, post-login probe
      completion, and all tracked driver patterns true.
- [x] V009 `python3 -m py_compile scripts/inspect_qbox_fvp_rd_aspen_fwu.py`
      passed after adding the FWU bank/metadata/capsule inspection helper.
- [x] V010 `python3 scripts/inspect_qbox_fvp_rd_aspen_fwu.py --out-dir build/qbox-fvp-rd-aspen/fwu-inspect-20260525-v2`
      generated `fwu-inspection.json` and `summary.md`. The JSON checks record
      matching raw RSE/AP flash sizes, `fw.cap` present on the capsule disk,
      capsule size matching the manifest image, and five non-dummy CFG2 FWU
      components.
- [x] V011 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 80 --port-timeout 5 --gdb-timeout 5 --sample-delay 65 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v2 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
      generated a fresh all-layer GDB bundle. RSE/TF-M and AP/Linux GDB ports
      opened, all short probe commands returned 0, QBox host backtrace capture
      completed, SCP-Firmware and SI CL1 Zephyr symbol scripts loaded, TF-M/RSE
      was sampled in BL2 image validation through the CC3XX ECDSA path, and AP
      was still at TF-A BL2 entry before Linux in this short sample.
- [x] V012 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --ignore-fail-patterns --runner-timeout 80 --port-timeout 5 --gdb-timeout 5 --sample-delay 45 --host-sample --host-sample-seconds 2 --out-dir build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic`
      regenerated and exercised the requested QBox/TF-M/SCP/Linux debug
      environment with shorter timing. RSE/TF-M and AP/Linux ports opened,
      all target probes returned 0, QBox host backtrace capture completed,
      TF-M/RSE sampled in BL2 `nor_cfi_reg_read()`, AP was still at TF-A BL2
      entry, and SCP-Firmware remained symbol/source-only under the current
      `scp-strategy=service-model` configuration.
- [x] V013 `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git -C tools/qbox diff --check`,
      `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 8`,
      and
      `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure`
      passed after adding the SFCP/FWU GDB trace detail and the MHU named-pair
      isolation fix.
- [x] V014 `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=8000 timeout 210s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --out-dir build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --rse-port 12382 --ap-port 12383 --runner-timeout 170 --port-timeout 12 --gdb-timeout 8 --sample-delay 120 --copy-writable-flash --ignore-fail-patterns`
      captured the current post-fix all-target state. RSE/TF-M and AP/Linux
      ports opened, AP TF-A/OP-TEE/U-Boot symbol views attached, SCP-Firmware
      and SI CL1 symbols loaded, TF-M/RSE sampled in `tfm_its_remove()` via
      the Strata flash erase path, AP SE-Proxy sampled in
      `secure_storage_ipc_set()` waiting on RSE, and the AP secure-service MHU
      trace paired 16 of 17 channel-1 requests with the single missing request
      being the timeout-truncated in-flight `0x80061101`.
- [x] V015 `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/analyze_qbox_mhu_trace.py` and the inline `parse_sc_time()` unit smoke passed after adding marker-gated GDB sampling and sc_time unit parsing.
- [x] V016 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=42000 timeout 400s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --out-dir build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-postdelay-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --rse-port 12390 --ap-port 12391 --runner-timeout 330 --port-timeout 10 --gdb-timeout 10 --sample-delay 300 --sample-marker 'Error: "db" not defined' --sample-marker-post-delay 25 --copy-writable-flash --ignore-fail-patterns`
      exercised the marker post-delay path. This bounded run did not reach the
      `db` marker before the 300.104-second cap, but AP secure-service, AP
      TF-A/OP-TEE/U-Boot, SCP-Firmware, and SI CL1 symbol probes attached at
      the earlier U-Boot FWU regular-state point, and MHU analysis paired 69
      of 70 AP secure-service channel-1 requests with the single missing
      request being the timeout-truncated in-flight `0x80064601`.
- [x] V017 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=60000 QBOX_RDASPEN_BOOT_FLASH_TRACE=true QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=4096 timeout 420s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --tfm-ps-object-table-trace --out-dir build/qbox-fvp-rd-aspen/gdb-t064-ps-object-trace-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --rse-port 12394 --ap-port 12395 --runner-timeout 360 --port-timeout 12 --gdb-timeout 12 --trace-timeout 230 --sample-delay 0 --copy-writable-flash --ignore-fail-patterns`
      captured PS object-table and RSE flash evidence. The trace intentionally
      timed out at the 230-second cap after hitting PS initialization,
      authentication, HUK/key-derivation, and multiple
      `Driver_FLASH0_EraseSector` calls. It did not reach the later `db`
      enrollment point, so it is PS/flash-init evidence, not a pass for T064.
- [x] V018 `QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=60000 timeout 360s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --out-dir build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --rse-port 12400 --ap-port 12401 --runner-timeout 300 --port-timeout 10 --gdb-timeout 12 --sample-delay 260 --sample-marker '2023 bytes read' --sample-marker-post-delay 30 --copy-writable-flash --ignore-fail-patterns`
      exercised the short marker wait requested by the user. The marker was
      not reached before the 260.085-second cap, but all GDB probes attached.
      AP SE-Proxy sampled a Protected Storage GET_INFO call (`type=1003`,
      uid 7) waiting for MHU sender clear, RSE/TF-M sampled the CMU_MHU2
      receive interrupt path, and MHU analysis paired 26 of 27 requests with
      only the bounded in-flight `0x80061b01` missing.
- [x] V019 `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`,
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/analyze_qbox_mhu_trace.py scripts/inspect_qbox_fvp_rd_aspen_fwu.py`,
      `git -C tools/qbox diff --check`,
      `./scripts/validate_qbox_fvp_rd_aspen_map.py`,
      `timeout 120s cmake --build tools/qbox/build --target reset_gpio platforms-vp --parallel 4`, and
      `timeout 90s ctest --test-dir tools/qbox/build -R '^reset-test-system:sync-pol=multithread:num-cpu=4:icount=false:threading=MULTI:accel=tcg$' --output-on-failure`
      passed after adding the AP `reset_gpio` bridge.
- [x] V020 `timeout 300s env QBOX_RDASPEN_ENABLE_AP_CPUS=true python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 260 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --post-login-probe --fwu-probe --out-dir build/qbox-fvp-rd-aspen/rse-t074-reset-gpio-fwu-short-20260525-v2`
      produced `blocker=qbox_fwu_probe_incomplete_timeout` after reaching RSE
      boot, RSE/SCP handoff, measured boot through `BL_33`, AP TF-A/OP-TEE,
      and U-Boot. Linux login was not reached, no FWU probe commands were
      sent, and T074-T076 remain open.
- [x] V021 `timeout 480s env QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=12000 QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2223-:22 python3 scripts/run_qbox_fvp_rd_aspen_rse.py --skip-build --timeout 420 --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic --post-login-probe --fwu-probe --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/rse-t074-reset-gpio-fwu-probe-20260525-v3`
      reached Linux login and root shell, proved the driver evidence patterns
      for `arm_si_rproc`, `hipc_ethsi1`, `pl011_uart`, `rpmsg`, `smmu_v3`,
      and `virtio`, copied `fw.cap` into `/boot/EFI/UpdateCapsule/`, and
      emitted `__QBOX_FWU_REBOOT_REQUESTED__`. The run timed out during or
      just after Linux shutdown with no `QEMU resetting`, image-1, or FIP_B
      marker, so T074-T076 remain open.
- [x] V022 `timeout 260s env QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=4000 python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --sample-marker 'Filesystem: FAT16' --sample-marker-post-delay 5 --sample-delay 180 --runner-timeout 220 --port-timeout 20 --gdb-timeout 8 --host-sample --host-sample-seconds 3 --ignore-fail-patterns --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-virtio-sample-20260525-v2`
      regenerated the GDB environment and attached to QBox host, TF-M/RSE,
      AP/Linux, AP firmware views, AP secure-service symbols, SCP-Firmware
      symbols, and SI CL1 symbols. The `Filesystem: FAT16` marker was not
      reached within 180.054 seconds; GDB sampled TF-M in
      `tfm_arch_thread_fn_call()` below `psa_wait_thread_fn_call()`, AP CPU0
      at pre-Linux secure-world PC `0xfef5b8a4`, and QBox host SystemC/QEMU
      threads in `SC_START`/QEMU wait paths.
- [x] V023 `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
      passed after adding `--fwu-probe` pass-through to the GDB helper. The
      option implies `--post-login-probe`, forwards the runner FWU capsule
      sequence, records `fwu_probe` in `debug-env.json`, and includes the
      option in generated README commands.
- [x] V024 `timeout 560s env QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=16000 QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2224-:22 python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --fwu-probe --sample-marker 'systemd-shutdown[1]: Rebooting.' --sample-marker-post-delay 5 --sample-delay 420 --runner-timeout 480 --port-timeout 20 --gdb-timeout 8 --ignore-fail-patterns --rse-port 12410 --ap-port 12411 --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-sample-20260525-v1`
      reached Linux FWU reboot request and marker-gated GDB sampling. All live
      target probes returned 0. The sampled root cause is AP TF-A BL31
      `ASSERT: plat/common/plat_gicv3.c:279` in
      `plat_ic_raise_el3_sgi()` below `psci_stop_other_cores()`,
      `css_scp_system_off()`, and `psci_system_reset()`. Linux reached PSCI
      reset, but no `QEMU resetting`, `SystemC resetting`, image-1, or FIP_B
      marker was observed because BL31 panicked before the modeled reset
      bridge.
- [x] V025 `git -C tools/qbox diff --check`
      passed after adding the QEMU MemTxAttrs TLM extension and enabling AP
      GICv3 security extensions.
- [x] V026 `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
      passed after setting `ap_gic.has_security_extensions = true`.
- [x] V027 `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`
      passed.
- [x] V028 `./scripts/validate_qbox_fvp_rd_aspen_map.py`
      passed and wrote `build/qbox-fvp-rd-aspen/map-validation.json`.
- [x] V029 `timeout 240s cmake --build tools/qbox/build --target platforms-vp --parallel 8`
      passed after the MemTxAttrs/GIC-security change.
- [x] V030 `timeout 540s env QBOX_RDASPEN_ENABLE_AP_CPUS=true QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_HOST_MEMORY_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=false QBOX_RDASPEN_RSE_DTCM_DMI=true QBOX_RDASPEN_RSE_ITCM_DMI=true QBOX_RDASPEN_RSE_VM_DMI=true QBOX_RDASPEN_MHU_TRACE=true QBOX_RDASPEN_MHU_TRACE_LIMIT=20000 QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2226-:22 python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --launch --sample-only --fwu-probe --sample-marker 'systemd-shutdown[1]: Rebooting.' --sample-marker-post-delay 8 --sample-delay 390 --runner-timeout 460 --port-timeout 20 --gdb-timeout 8 --ignore-fail-patterns --rse-port 12440 --ap-port 12441 --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-gic-secure-20260525-v3`
      reached Linux login, copied the FWU capsule, requested reboot, found
      `systemd-shutdown[1]: Rebooting.` after 334.619 seconds, and sampled all
      GDB views successfully. The previous BL31 `plat_gicv3.c:279` assert did
      not recur. AP CPUs now sample in BL31
      `psci_pwrdown_cpu_end_terminal()`, and the MHU trace records an AP-SI
      SCMI System Power request with no modeled `QEMU resetting` or
      `SystemC resetting` line in the 8-second post-marker window.
- [x] V031 `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua tools/qbox/tests/components/loader/conf-test.lua`,
      `git -C tools/qbox diff --check`,
      `python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py`,
      and `./scripts/validate_qbox_fvp_rd_aspen_map.py`
      passed after adding AP BL2 reset-state restoration and RSE KMU/CC3XX
      reset sockets.
- [x] V032 `timeout 120s cmake --build tools/qbox/build --target rse_kmu-tests cc3xx-tests loader-test mhuv3_stub-tests platforms-vp --parallel 8`
      passed.
- [x] V033 `timeout 100s ctest --test-dir tools/qbox/build -R '^(rse_kmu-tests|cc3xx-tests|loader-test|mhuv3_stub-tests)$' --output-on-failure`
      passed; reset regression coverage now includes loader reset-only load,
      RSE KMU register restoration, and CC3XX runtime-register restoration.
- [x] V034 `QBOX_RDASPEN_MHU_TRACE=false QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2233-:22 timeout 720s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-shutdown-system-reset-20260525-v7 --launch --sample-only --fwu-probe --keep-running-after-pass --ignore-fail-patterns --rse-port 12510 --ap-port 12511 --runner-timeout 650 --sample-delay 560 --sample-marker 'systemd-shutdown[1]: Rebooting.' --sample-marker-post-delay 90 --gdb-timeout 6 --port-timeout 8`
      reached Linux login, driver probe evidence, FWU capsule copy,
      `__QBOX_FWU_REBOOT_REQUESTED__`, `systemd-shutdown[1]: Rebooting.`, and
      `reboot: Restarting system`. All GDB probes returned 0. The second AP
      BL2 reaches FW_CONFIG image loading/measurement without the earlier
      `PSA_ERROR_BAD_STATE (-137)`, but RSE samples in BL1_1
      `boot_platform_error_state()` with decoded `0x20000003`
      (`KMU_ERROR_NULL_POINTER`), and AP BL2 waits in
      `mhu_v3_x_doorbell_read()`.
- [x] V035 Re-read `arm-zena-css/documentation/design/boot_process.rst` and
      `arm-zena-css/documentation/design/components.rst` before implementing
      the RSE reset-domain sequencer. The Arm Zena CSS Primary Compute domain
      reset flow keeps Safety Island and RSE operational; the correct QBox
      model is AP BL2 reload, AP SRAM reset, AP CPU reset, and AP SDS
      warm-reset syndrome update, not RSE CPU/TCM/VM reset fanout.
- [x] V036 `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua tools/qbox/tests/components/loader/conf-test.lua`,
      `git -C tools/qbox diff --check`,
      `timeout 120s cmake --build tools/qbox/build --target loader-test mhuv3_stub-tests platforms-vp --parallel 8`,
      and
      `timeout 100s ctest --test-dir tools/qbox/build -R '^(loader-test|mhuv3_stub-tests)$' --output-on-failure`
      passed after removing the temporary RSE reset fanout and adding the AP
      SDS reset-syndrome `SYS_RESET_REQ` write to the reset-only AP BL2
      loader.
- [x] V037 `QBOX_RDASPEN_MHU_TRACE=false QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2233-:22 timeout 700s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8 --launch --sample-only --fwu-probe --keep-running-after-pass --ignore-fail-patterns --rse-port 12510 --ap-port 12511 --runner-timeout 620 --sample-delay 540 --sample-marker 'systemd-shutdown[1]: Rebooting.' --sample-marker-post-delay 70 --gdb-timeout 6 --port-timeout 8`
      reached Linux login, copied the FWU capsule, requested reboot, found
      `systemd-shutdown[1]: Rebooting.` after 520.166 seconds, and sampled all
      GDB views successfully. The second and third AP BL2 entries report
      `SDS reset syndrome = 0x8`, `Warm reset syndrome detected, measured boot
      will be skipped`, and `BL2: Booting BL31`; no
      `Measure and record failed`, `Loading of FW_CONFIG failed`, or
      `boot_platform_error_state` signature appears in the v8 run/probe logs.
- [ ] V038 Investigate remaining Secure FWU bank-selection fidelity. The v8
      run proves `FWU: Updating 5 payload(s)` and subsequent AP warm boot, but
      the observed U-Boot FWU state is still `Regular State`; the next
      acceptance target is explicit `Trial State` and/or `FIP_B` evidence.
- [x] V038A Identify and fix the missing raw-flash persistence prerequisite.
      Inspection of
      `build/qbox-fvp-rd-aspen/gdb-fwu-warm-reset-sds-20260525-v8/run/writable-images/`
      after a run that logged `FWU: Updating 5 payload(s)` still showed
      secondary FWU banks empty and AP metadata `active_index=0`, proving the
      previous flash model did not persist program/erase mutations into the
      file-backed evidence images. `strata_flash_j3-tests` now verifies
      program and erase write-through, `platforms-vp` rebuilds, and the short
      `rse-t076-flash-writeback-smoke-20260525-v2` platform run starts with
      per-run raw flash paths and no `backing_file` errors before its expected
      60-second boot timeout.
- [x] V038B Rerun the FWU probe with a short post-writeback timeout. The
      180-second run
      `build/qbox-fvp-rd-aspen/rse-t076-flash-writeback-fwu-probe-20260525-v1/`
      starts with per-run raw flash writeback enabled but times out before
      Linux login, so no capsule commands are sent and the inspected FWU banks
      remain at the initial active-bank-0 state. This confirms the next V038
      step must improve or sample the first-boot path under short caps before
      attempting another long FWU acceptance run.
- [x] V038C Capture a short-cap GDB sample of the post-writeback first boot.
      `build/qbox-fvp-rd-aspen/gdb-t076-writeback-short-20260525-v1/`
      samples RSE/TF-M, AP/Linux/TF-A/OP-TEE/U-Boot symbol views,
      SCP-Firmware symbols, and SI CL1 Zephyr symbols. At 170 seconds RSE BL2
      is inside `boot_decrypt_and_copy_image_to_sram()` /
      `Driver_FLASH0_ReadData()` reading the SI CL0 image from Strata flash,
      while AP CPU0 is still at TF-A BL2 entry `0x82000`. This narrows the
      short-cap blocker to first-boot RSE BL2 flash-read/copy latency before
      any Linux/FWU capsule stage starts.
- [x] V038D Recheck the all-target GDB environment with short caps. `which
      gdb-multiarch`, `which gdb`, the Yocto `arm-none-eabi-gdb` executable
      check, and
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py`
      passed. `QBOX_RDASPEN_ATU_DMI=true QBOX_RDASPEN_BOOT_FLASH_DMI=true
      QBOX_RDASPEN_HOST_MEMORY_DMI=true timeout 190s python3
      scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py --out-dir
      build/qbox-fvp-rd-aspen/gdb-fast-linux-current-20260525-v1 --launch
      --sample-only --sample-delay 112 --runner-timeout 130 --trace-timeout
      120 --gdb-timeout 6 --port-timeout 8 --host-sample
      --host-sample-seconds 3 --ignore-fail-patterns --rootfs
      build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
      --rse-port 12680 --ap-port 12681` generated a reusable bundle and
      sampled QBox host, RSE/TF-M, AP firmware/Linux target attachment,
      SCP-Firmware symbols, and SI CL1 symbols. Current short-cap progress
      does not reach Linux: RSE TF-M runtime is in
      `tfm_hal_system_halt()` below `tfm_spm_partition_psa_panic()`, AP CPU0
      is in TF-A BL2 `mhu_v3_x_doorbell_read()`, and SCP-Firmware remains
      symbol/source-only because the active QBox platform uses the SCP
      service model rather than a live SCP CPU.
- [x] V038E Add range-limited Strata flash DMI for short GDB debug loops.
      `strata_flash_j3` now accepts `dmi_ranges` as comma-separated
      `start:size` or `start-end` ranges. The RSE platform wires
      `QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES` and
      `QBOX_RDASPEN_AP_FLASH_DMI_RANGES` so primary image slots can use
      read-only DMI while ITS/PS/FWU storage sectors still traverse CFI
      command-state writes. `strata_flash_j3-tests` covers range-limited DMI
      grants and read DMI hints. A short all-target GDB run with RSE range
      `0x7000:0x260000`, AP range `0x7000:0x240000`, copied writable flash,
      and 125-second sampling reached AP TF-A BL31, OP-TEE, U-Boot, and
      Trusted Services. The sampled AP state is SE-Proxy
      `secure_storage_ipc_set()` waiting for RSE over MHUv3, while RSE/TF-M is
      actively inside ITS flash filesystem writes through
      `Driver_FLASH0_ProgramData()` rather than the earlier partition panic.
- [x] V038F Re-run the requested short-timeout GDB inspection for QBox,
      TF-M/RSE, SCP-Firmware, and AP/Linux. Generated
      `gdb-linux-marker-short-20260525-v1`,
      `gdb-linux-marker-dmi-short-20260525-v1`,
      `gdb-real-scp-short-20260525-v1`, and
      `gdb-qbox-host-short-20260525-v1`. QBox host backtraces are captured
      through host-GDB launch; RSE/AP GDB ports attach; AP/Linux scripts are
      generated and attach to the AP target; 130-second Linux marker samples
      stop before `Linux version`, at U-Boot/SE-Proxy secure-service progress;
      `real-si-scp` does not expose a live SCP GDB port, so SCP-Firmware
      remains symbol/source-only in the current platform.
- [x] V038G Recheck flash persistence with short runtime caps. The
      deploy-equivalent SHA of
      `rse-t064-db-nogdb-20260525-v1/writable-images/rse-flash-image.raw.img`
      explains why reusing it started with missing PK/KEK variables again.
      Fresh current runs with writeback enabled do mutate the RSE raw flash:
      `rse-t076-flash-trace-short-20260525-v1` changes the first observed
      bytes around offset `0x3007000`, and
      `rse-t076-range-dmi-fresh-20260525-v1` reaches PK/KEK enrollment with
      RSE raw SHA
      `6c2e9a3824a61c50146a55c62d3ddec56399a3beec28fc367164272ac57b3090`.
      Reusing an aborted partial image can enter `FWU: Updating 5 payload(s)`,
      so V038/T076 still require a clean cross-run persisted-state proof.
- [x] V038H Re-run the user-requested all-target GDB inspection with short
      caps. `build/qbox-fvp-rd-aspen/gdb-user-request-all-targets-20260525-v1/`
      opens RSE/TF-M and AP/Linux GDB ports, captures QBox host
      SystemC/QEMU thread backtraces through the foreground host-GDB launch
      path, and loads SCP-Firmware symbols. At the 35-second sample RSE/TF-M
      is in BL2 Strata flash image read/decrypt; AP CPUs are still at
      `0x82000`/TF-A BL2 entry, so Linux has not started in the short cap.
      SCP-Firmware remains source/symbol-only because no live SCP CPU GDB
      server is instantiated under the current service-model platform.
- [x] V038I Reproduce the U-Boot EFI secure-storage pause with marker-gated
      GDB and inspect the corresponding FWU flash artifacts. The bounded
      runtime
      `build/qbox-fvp-rd-aspen/rse-v038-current-fwu-range-dmi-20260525-v1/`
      reached `EFI: MM partition ID 0x8006` but not Linux login or FWU
      capsule commands; `fwu-inspect-v038-current-range-dmi-20260525-v1`
      shows all secondary banks empty and AP FWU metadata still on active
      bank 0. A follow-up GDB run
      `build/qbox-fvp-rd-aspen/gdb-user-efi-current-20260525-v1/`
      found the EFI marker after 101.526 seconds, opened RSE/AP GDB ports,
      captured host QBox/SystemC/QEMU backtraces, and sampled AP CPU0 in
      SE-Proxy `secure_storage_ipc_remove()` waiting on MHUv3 while RSE/TF-M
      was in `tfm_its_remove()` / ITS flash filesystem compaction through
      `Driver_FLASH0_ProgramData()`. Linux has not started at this marker,
      and SCP-Firmware remains symbol-only under the service-model SCP path.
- [x] V038J Tighten Strata flash active-DMI invalidation and recheck the EFI
      marker. `strata_flash_j3` now records whether a direct-memory grant is
      active, invalidates it only once on a flash command-state write, and
      avoids another full-device invalidation for the following program-data
      write after DMI was already revoked. `strata_flash_j3-tests` adds
      `ProgramSequenceInvalidatesActiveDmiOnlyOnce`; the focused build, the
      focused Strata DMI/backing tests, the full Strata component test binary,
      `git diff --check`, and `platforms-vp` rebuild all passed. The follow-up
      marker-gated run
      `build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1/` reached
      `EFI: MM partition ID` after 113.028 seconds and still sampled AP CPU0
      in SE-Proxy `secure_storage_ipc_remove()` while RSE/TF-M was in
      `tfm_its_remove()` / ITS delete-compact writeback through
      `Driver_FLASH0_ProgramData()`. MHU trace pairing showed one in-flight
      AP-to-RSE request at the sample point. This closes only the DMI
      invalidation hygiene item; V038/T076 remain open because Linux/FWU
      progress did not improve.
- [x] V038K Decode the post-login SE-Proxy panic with GDB/symbol evidence.
      `build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/`
      reaches Linux login and driver probes, but the IAT/ITS/PS PSA user
      tests all time out opening RPC sessions. OP-TEE reports SE-Proxy loaded
      at `0x40031000`, then a user-mode data abort at `0x400473d8` with
      `x0 = 0`. `aarch64-poky-linux-addr2line` and `gdb-multiarch` decode
      the fault offset `0x163d8` to `update_agent_discover()` line 12 and the
      caller offset `0x16a4c` to `discover_handler()` line 106. This proves
      the post-login secure-service failure is a QBox-specific SE-Proxy FWU
      discovery null-`update_agent` panic. FVP comparison logs show the same
      expected first-boot secure-storage `-140/-133/-135` messages without
      panic, with IAT and ITS returning rc 0 and PS progressing through test
      409. The next implementation split is to fix the QBox condition that
      causes SE-Proxy FWU provider initialization/discovery to run with a
      null update agent, while separately continuing the pre-Linux TF-M
      Strata writeback performance work.
- [x] V038L Rebuild QBox and rerun a short all-layer GDB progress sample.
      `cmake --build tools/qbox/build --target platforms-vp --parallel 8`
      passed before the current probe. The rebuilt artifact
      `build/qbox-fvp-rd-aspen/gdb-efi-marker-current-rebuilt-20260525-v3/`
      generated QBox host, TF-M/RSE, AP firmware/Linux, SCP-Firmware, Trusted
      Services, and Zephyr GDB scripts. With
      `--runner-timeout 140 --sample-delay 130 --port-timeout 8
      --gdb-timeout 8`, the `EFI: MM partition ID` marker was not reached.
      RSE/TF-M sampled in BL2 `cfi_strataflashj3_read()` /
      `Driver_FLASH0_ReadData()` while loading an image from flash; AP CPU0-3
      remained at TF-A BL2 `0x82000` before Linux; SCP remained symbol-only
      under `scp-strategy=service-model`. This establishes the current rebuilt
      short-timeout progress point as pre-AP TF-M BL2 flash image loading.
- [x] V038M Add and verify a reusable range-limited flash-DMI GDB path. The
      GDB helper now has `--range-limited-flash-dmi`, which enables ATU DMI,
      host-memory DMI, RSE boot-flash DMI for `0x7000:0x260000`, and AP flash
      DMI for `0x7000:0x240000` without a long environment prefix. Setup-only
      evidence in
      `build/qbox-fvp-rd-aspen/gdb-range-dmi-setup-current-20260525-v1/`
      records the expected effective environment, and
      `gdb-efi-marker-range-dmi-option-current-20260525-v1/` proves the option
      works in a launched run by reaching `EFI: MM partition ID` after 99.030
      seconds with all non-SCP live target probes passing. The current short
      runtime
      artifact
      `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-current-20260525-v1/`
      opens RSE/AP GDB ports, reaches RSE runtime and U-Boot
      `EFI: MM partition ID 0x8006`, and samples AP SE-Proxy
      `secure_storage_ipc_set()` while RSE handles the MHU2/SFCP receive path.
      `Linux version` is still not reached in 140 seconds. The negative control
      `gdb-linux-marker-full-dmi-current-20260525-v1/` proves full-device
      boot-flash DMI is still unsafe because TF-M ITS initialization halts at
      `Partition initialization FAILED in 0x31047cc5`.
- [x] V038N Suppress no-op Strata flash backing-file writes and recheck the
      current GDB progress point. `strata_flash_j3::program()` now computes the
      resulting programmed byte value first, mutates only changed bytes, and
      writes back only the changed subrange. `strata_flash_j3-tests` adds
      `NoopProgramSkipsBackingFileWrite`, proving that programming `0xff` over
      an already erased byte does not touch a deliberately short backing file.
      `git diff --check`, `luac -p`, Python byte-compilation, focused Strata
      build/test, and `platforms-vp` rebuild all passed. The follow-up
      artifact
      `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-noop-current-20260525-v1/`
      used `--range-limited-flash-dmi --copy-writable-flash` with RSE/AP GDB
      ports `12750`/`12751`. It reached U-Boot `EFI: MM partition ID 0x8006`
      but not `Linux version` within 125.036 seconds. AP CPU0 sampled in
      SE-Proxy `secure_storage_ipc_set()` waiting on RSE MHU response, while
      RSE/TF-M sampled in `tfm_its_remove()` and ITS flash compact/writeback
      through `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()`
      -> `nor_byte_program()` -> `nor_send_cmd_byte()`. MHU trace pairing
      found 21 requests, 20 matched responses, and one in-flight request at the
      sample. This closes only the backing-file no-op optimization; V038/T076
      remain open because Linux/FWU progress still needs a faster or more
      faithful firmware-visible Strata program path.
- [x] V038O Add Strata flash stats to the all-target GDB workflow and compare
      with a fresh verbose FVP reference run. `strata_flash_j3` now has
      optional `stats_file` and `stats_interval` CCI parameters that count
      read/write accesses, CFI command classes, program operations, no-op
      bytes, compatibility sector erases, and backing-file writes.
      `strata_flash_j3-tests` covers normal/no-op program stats and
      sector-erase compatibility stats. The RSE Lua platform wires these
      params for RSE boot flash and AP flash, and
      `debug_qbox_fvp_rd_aspen_rse_gdb.py` adds `--flash-stats` plus
      `--flash-stats-interval`. Static checks, `luac -p`, Python
      byte-compilation, focused Strata build/test, ctest, and `platforms-vp`
      rebuild passed. The runtime artifact
      `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/`
      reached U-Boot `EFI: MM partition ID 0x8006` but not `Linux version`
      within 125.037 seconds. AP sampled in SE-Proxy
      `secure_storage_ipc_set()` waiting on MHU, while RSE/TF-M sampled in
      `tfm_its_set()` / ITS/PS flash writeback through
      `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` ->
      `nor_byte_program()` -> `nor_poll_dws_byte()`. The RSE stats snapshot
      records `program_ops=246699`, `read_status_cmds=493397`,
      `write_accesses=1480192`, and `read_accesses=776455`, quantifying the
      pre-Linux bottleneck. Fresh FVP verbose artifact
      `build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1/` reached
      `Booting Linux on physical CPU` and `Linux version`; it also shows the
      same expected SE-Proxy `-140` first-boot messages continuing normally.
      V038/T076 remain open; the next implementation target is a faithful
      Strata buffered-program path or another semantics-preserving way to
      reduce firmware-visible CFI transaction cost.
- [x] V038P Recheck the current short-timeout behavior with 2026-05-26 GDB and
      non-GDB evidence. Focused Strata flash component tests still pass with
      `ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$'
      --output-on-failure`. Fresh writable-flash GDB artifact
      `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-baseline-recheck-20260526-v1/`
      did not reach `Linux version` within 140.044 seconds; AP SE-Proxy was
      waiting in `secure_storage_ipc_set()` / `mhu_v3_x_doorbell_read()` while
      RSE/TF-M was in `tfm_its_remove()` -> `Driver_FLASH0_EraseSector()` ->
      `cfi_strataflashj3_erase()` -> `erase_block()` ->
      `nor_byte_program()` -> `nor_send_cmd_byte()`. The stats snapshot already
      recorded `program_ops=866667`, `word_program_cmds=866667`,
      `compat_ff_sector_erase_ops=1098`, and `backing_write_ops=584661`.
      A no-copy GDB control
      `gdb-linux-marker-range-dmi-nocopy-passcheck-20260526-v1/` sampled TF-M
      in `psa_wait_thread_fn_call()` and recorded no backing writes, but still
      did not reach `Linux version` within its 100.032-second cap. A regular
      no-copy runtime with a 260-second runner cap,
      `build/qbox-fvp-rd-aspen/rse-runtime-nocopy-postlogin-20260526-v2/`,
      reached `Linux version`, root shell, systemd multi-user, RSE/SCP handoff,
      measured-boot through `BL_33`, SMMU v3, virtio, SI remoteproc attach,
      RPMsg, and `ethsi1`; post-login probe completed with
      `arm_si_rproc_modprobe_rc=0`, RPMsg module rc values of 0,
      `ethsi1_iplink_rc=0`, and all driver-pattern checks true. This confirms
      QBox can reach Linux login and validate the current Linux driver surface
      with the persisted deploy flash state, while fresh writable flash still
      spends the short window in TF-M ITS/PS Strata byte-program
      erase/writeback. V038/T061-T064/T076 remain open because secure-service
      userspace command tests, FWU bank switching, and cross-reboot
      writable-flash persistence are still unproven.
- [x] V038Q Recheck the post-login secure-service CC3XX/PKA path with a
      no-copy runtime, focused CC3XX trace, and TF-M source comparison.
      Generated
      `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-pka-trace-20260526-v1/`
      with `QBOX_RDASPEN_CC3XX_TRACE=true`,
      `QBOX_RDASPEN_CC3XX_TRACE_FILTER=pka-opcode`, and
      `QBOX_RDASPEN_CC3XX_TRACE_LIMIT=20000`. The run reaches Linux login,
      root, the post-login probe, and the expected Linux driver surface, but
      the secure-service userspace tests remain bounded failures:
      `secure_psa_iat_api_test_rc=124`,
      `secure_psa_its_api_test_rc=124`, and
      `secure_psa_ps_api_test_rc=124`. Added
      `scripts/analyze_qbox_cc3xx_trace.py` and generated
      `cc3xx-pka-summary.txt` / `cc3xx-pka-summary.json`; the summary decodes
      `20000` CC3XX trace entries, reports `trace_limit_reached: True`, and
      counts `8063` PKA opcode writes before the limit is consumed. The
      dominant pre-Linux/RSE ops are `AND_TST0_CLR0=2317`, `MODMUL=2311`,
      `MODSUB_MODDEC_MODNEG=1676`, and `MODADD_MODINC=1150`. Because the trace
      limit is exhausted before IAT, this artifact proves heavy CC3XX PKA
      traffic but does not yet capture the late userspace IAT opcode stream.
      The current GDB artifact
      `gdb-secure-service-iat-sample-20260526-v1/` still maps AP SE-Proxy to
      `mhu_v3_x_doorbell_read(channel=127)` and RSE TF-M to
      `cc3xx_lowlevel_rng_get_random()` ->
      `cc3xx_lowlevel_pka_set_to_random_within_modulus()` ->
      `cc3xx_lowlevel_ecdsa_sign()` for `CC3XX_EC_CURVE_SECP_256_R1`. TF-M
      source inspection shows `set_to_random_within_modulus()` accepts random
      candidates through `cc3xx_lowlevel_pka_less_than()`, which depends on
      `SUB_DEC_NEG` setting `PKA_STATUS.ALU_SIGN_OUT`; the QBox CC3XX model
      already implements that status path. V038/T061-T064/T076 remain open.
      Next work should late-gate or increase the CC3XX trace enough to capture
      IAT directly, then either fix a specific PKA semantic mismatch or
      accelerate the CC3XX PKA/ECDSA path without bypassing the modeled
      programming interface.
- [x] V038R Add late-gated CC3XX trace control, capture the userspace IAT
      PKA window, and recheck the bounded secure-service behavior after a
      semantics-preserving CC3XX PKA cache increment. QBox now exposes
      `QBOX_RDASPEN_CC3XX_TRACE_SKIP` through the RSE Lua platform without
      adding another top-level Lua local, keeping `luac -p` valid. The focused
      `PkaTraceSkipCanGateEarlyOpcodes` regression verifies the skip gate, and
      `PkaModulusCacheInvalidatesOnModulusRewrite` verifies that caching the
      PKA modulus register preserves results when `N` is rewritten. Runtime
      artifact
      `build/qbox-fvp-rd-aspen/rse-secure-service-cc3xx-skip-trace-20260526-v3/`
      uses `QBOX_RDASPEN_CC3XX_TRACE_SKIP=80000` and
      `QBOX_RDASPEN_CC3XX_TRACE_LIMIT=4000`; it reaches Linux/root and the
      post-login probe, then captures late IAT/attestation PKA traffic with
      `trace_limit_reached: True`, `pka_opcode_count: 1681`, and dominant
      operations `AND_TST0_CLR0=491`, `MODMUL=491`,
      `MODSUB_MODDEC_MODNEG=351`, and `MODADD_MODINC=236`. The no-trace
      cache probe
      `rse-secure-service-cc3xx-cache-probe-20260526-v1/` still returns
      `124` for `psa-iat-api-test`, `psa-its-api-test`, and
      `psa-ps-api-test` with the 3-second cap. A 15-second cap run
      `rse-secure-service-cc3xx-cache-probe-15s-20260526-v1/` shows forward
      progress but still returns `124`: IAT reaches checks 1..11 and reports
      one `arm_tstee ... rpc status: -6`, ITS passes tests 401/402 and reaches
      the insufficient-space cleanup path, and PS passes test 401 before the
      cap. V038/T061-T064/T076 remain open; the next target is the
      secure-service completion path and AP-RSE MHU queue/backpressure plus
      remaining CC3XX/ECDSA latency, not basic boot or Linux driver wiring.
- [x] V038S Fix AP/SI CL1 synthetic-MHU txdone and PBX IRQ delivery.
      `mhuv3_stub` now clears the sender PBX status for synthetic AP/SI CL1
      service-model transfers after the configured doorbell auto-ack and after
      the RPMsg name-service packet is scheduled. It also drives the combined
      IRQ output for PBX frames, not just MBX frames. This matters because the
      Linux `arm_mhuv3` driver uses interrupt-driven `txdone_irq` when the PBX
      combined IRQ is present; status-only synthetic completion is not enough
      to drain the Linux mailbox queue. The fix now defers the synthetic PBX
      completion through a SystemC event and suppresses empty transfer-ack IRQs
      only for the AP/SI CL1 doorbell pair, so MBX startup clears no longer
      create PBX IRQs without a Linux `pending_db`. The focused
      `mhuv3_stub-tests` regression checks that empty MBX clears do not raise
      PBX transfer-ack status, that PBX `DBCW_ST` remains set until the
      deferred completion fires, and that `DBCW_INT_ST` plus the PBX IRQ assert
      for both the `0x8` resource-table seed kick and the later `0x1` RPMsg
      host kick. Static/build checks passed:
      `git -C tools/qbox diff --check -- systemc-components/mhuv3_stub/include/mhuv3_stub.h tests/components/mhuv3_stub/mhuv3_stub-tests.cc`,
      `cmake --build tools/qbox/build --target mhuv3_stub-tests --parallel 8`,
      `ctest --test-dir tools/qbox/build -R '^mhuv3_stub-tests$' --output-on-failure`,
      `luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`, and
      `cmake --build tools/qbox/build --target platforms-vp --parallel 8`.
      A pre-PBX-IRQ runtime,
      `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-txdone-20s-20260526-v1/`,
      reached Linux, started the secure-service IAT probe, and reproduced
      `arm-mhuv3-mailbox 400b0000.mhu: Try increasing MBOX_TX_QUEUE_LEN`.
      This proved that the earlier status-only sender-completion increment was
      insufficient. The post-PBX-IRQ runtime,
      `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-irq-20s-20260526-v1/`,
      reached U-Boot EFI handoff (`EFI: MM partition ID 0x8006` and
      `Booting /\EFI\BOOT\BOOTAA64.EFI`) but timed out before Linux login, so
      it did not prove warning removal. The 2026-05-27 copy-flash runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-mhu-pbx-ap-si-only-copyflash-20260527-v1/`
      is the acceptance evidence: it reaches Linux and the post-login probe,
      keeps SI CL1/RPMsg driver checks green, and contains zero
      `Spurious IRQ on PBX channel`, zero `Try increasing MBOX_TX_QUEUE_LEN`,
      and zero RCU-stall reports. V038, T061-T064, and T076 remain open for
      secure-service completion and FWU persistence, not for the AP/SI
      mailbox-warning path.
- [x] V038T Recheck secure-service IAT/ITS after AP/SI MHU fix without heavy
      tracing. Runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-30s-notrace-20260527-v1/`
      used per-run writable flash copies, AP CPUs, ATU DMI, host-memory DMI,
      boot-flash DMI disabled, and `--secure-service-probe-timeout 30`.
      It returned `passed=true`, `timed_out=false`, completed the post-login
      probe, and kept Linux driver checks green. `psa-iat-api-test` returned
      0 with one passed IAT suite; `psa-its-api-test` returned 0 with ten
      passed ITS tests; `psa-ps-api-test` still returned 124 after passing PS
      tests 401 and 402 and entering PS test 403. The primary, secure, and RSE
      logs contain zero `Spurious IRQ on PBX channel`, zero
      `Try increasing MBOX_TX_QUEUE_LEN`, and zero RCU-stall reports. The
      companion high-MHU-trace run
      `build/qbox-fvp-rd-aspen/rse-secure-service-30s-probe-20260527-v1/`
      timed out before Linux while logging thousands of AP-RSE MHU accesses,
      so high-volume MHU tracing is diagnostic only and should not be used for
      bounded secure-service pass/fail timing. The runner now also supports
      `--secure-service-probe-tests`, and PS-only runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-60s-20260527-v1/`
      confirms PS still times out in test 403 even without IAT/ITS running
      first. V038/T061/T063/T064/T076 remain open for PS completion, UEFI/FWU
      storage coverage, and persistence.
- [x] V038U Pad per-run writable flash images before Strata writeback and
      recheck PS-only stats. The pre-fix stats attempt
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-stats-20260527-v1/`
      reproduced PS test 403 timeout and logged
      `remote_platform.rse_boot_flash unable to range backing_file=...`
      because the copied RSE flash backing file was only 5,033,984 bytes while
      the modeled RSE flash device is 64 MiB. The runner now pads copied RSE
      flash to 67,108,864 bytes and copied AP flash to 134,217,728 bytes with
      erased `0xff` bytes before enabling writeback. Static validation passed
      with `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`, a
      helper-level import/padding smoke test, and `git diff --check --` for
      the runner. Runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-padded-stats-20260527-v1/`
      reports `passed=true`, `timed_out=false`, completed post-login driver
      checks, no backing-file range errors, and RSE Strata stats including
      `write_accesses=16750000`, `program_ops=2791667`,
      `compat_ff_sector_erase_ops=2034`, and
      `backing_write_ops=2263712`. PS still returns
      `secure_psa_ps_api_test_rc=124` in test 403, so V038/T061/T063/T064/T076
      remain open for Protected Storage completion and FWU/UEFI persistence
      semantics, not for backing-file coverage of the modeled flash aperture.
- [x] V038V Run a no-copy/writeback-off PS-only stats control. Runtime
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps-only-nocopy-stats-20260527-v1/`
      uses `--no-copy-writable-flash`, preserves the deploy RSE/AP flash image
      lengths, and reports `pad_state=skipped_source_not_copied`. It returns
      `passed=true`, `timed_out=false`, `blocker=null`, completes post-login
      driver checks, and records `secure_psa_ps_api_test_rc=124`. RSE Strata
      stats still show a large firmware-visible workload
      (`write_accesses=15750000`, `program_ops=2625000`,
      `compat_ff_sector_erase_ops=1962`) while `backing_write_ops=0` and
      `backing_write_bytes=0`. No `unable to ... backing_file`, AP/SI PBX
      warning, MBOX queue warning, or RCU-stall pattern was found in the
      checked logs. This confirms the current PS timeout is not caused by
      host file writeback cost or backing-file range errors.
- [x] V038W Add focused PSA PS test-list support for short PS debug runs. The
      runner now accepts `--secure-service-ps-test-list`, validates PSA
      Architecture Test Suite entries such as `test_403;`, and emits
      `psa-ps-api-test -t 'test_403;'` only when the selected secure-service
      test is `ps`. Validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`, help-output
      inspection, command-generation checks, `git diff --check --`, and the
      focused Strata component build/test:
      `timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8`
      plus
      `timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure`.
      A stats-enabled no-copy runtime,
      `build/qbox-fvp-rd-aspen/rse-secure-service-ps403-filter-20260527-v1/`,
      timed out before Linux login with `qbox_platform_timeout`, so it is not
      PS test 403 pass/fail evidence. It does show pre-Linux Strata work still
      dominates when stats collection is enabled in a short host window:
      `write_accesses=500000`, `program_ops=83333`,
      `compat_ff_sector_erase_ops=317`, and `backing_write_ops=0`.
- [x] V038X Auto-enable AP CPUs for post-login, secure-service, and FWU
      probes. These probes require Primary Compute Linux, so the runner now
      sets `QBOX_RDASPEN_ENABLE_AP_CPUS=true` inside the QBox runtime
      environment whenever `--post-login-probe`, `--secure-service-probe`, or
      `--fwu-probe` is requested. Validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`, a
      helper-level import smoke that checks `qbox_env()`, `git diff --check`,
      and a 20-second runtime smoke
      `build/qbox-fvp-rd-aspen/rse-ap-auto-enable-smoke-20260527-v1/` run
      without any external AP env. The smoke intentionally timed out early,
      but `qbox-platform.log` reports `ap cpus:      4`, proving the runner no
      longer creates invalid AP-disabled post-login probe runs. Two follow-up
      filtered PS 403 attempts,
      `rse-secure-service-ps403-filter-nostats-ap-20260527-v1/` and
      `rse-secure-service-ps403-filter-copyflash-20260527-v1/`, used AP CPUs
      but timed out before Linux at U-Boot/SMM Gateway, so they are
      pre-Linux secure-storage timing evidence rather than PS test 403
      pass/fail evidence.
- [x] V038Y Record runner elapsed time and original argv in QBox RSE
      `result.json`. The runner now reports `runtime_elapsed_s` and
      `runner_argv`, and `summary.txt` prints the elapsed runtime or `not_run`
      for check-only/preflight exits. This preserves the short-timeout
      workflow while making it possible to compare old and new probe artifacts
      without inferring host elapsed time from log mtimes. Validation passed
      with `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and a
      three-second smoke run
      `build/qbox-fvp-rd-aspen/rse-runner-elapsed-smoke-20260527-v1/` whose
      result records `timed_out=true`, `blocker=qbox_platform_timeout`,
      `runtime_elapsed_s=3.0408413260011002`, and a `runner_argv` containing
      `--timeout`.
- [x] V038Z Re-run focused PS 403 with elapsed metadata and a short 180-second
      cap. Runtime
      `build/qbox-fvp-rd-aspen/rse-ps403-filter-elapsed-20260527-v1/`
      records `runtime_elapsed_s=180.15632524300236`, `timed_out=true`, and
      `blocker=qbox_platform_timeout`. RSE markers through measured boot
      `BL_33` are present, AP U-Boot reaches PK/KEK/db/dbx enrollment and
      `** Booting bootflow 'virtio-blk#1.bootdev.part_1' with script`, but
      Linux login markers are false and no post-login probe commands were
      sent. Treat this as pre-Linux U-Boot/SMM Gateway secure-storage timing
      evidence, not as a PSA PS test 403 result.
- [x] V038AA Capture a fresh verbose FVP SMM Gateway reference for the same
      bounded comparison window. Runtime
      `build/fvp-boot-logs/rd-aspen-verbose-smmgw-20260527-v1/` was captured
      with `scripts/runfvp_log_boot.py --timeout 180 --require critical
      --no-login --runfvp-verbose`. The FVP summary reports `passed: False`
      only because `terminal_ns_uart0` did not reach the critical login/root
      marker in the bounded no-login run; the primary console still reaches
      `Booting /\EFI\BOOT\BOOTAA64.EFI`, `Booting Linux on physical CPU`, and
      `Linux version 6.18.5-rt3-yocto-preempt-rt`. The secure console contains
      the same early SMM Gateway `sp_msg_send_direct_req(): error -4` fallback
      and SE-Proxy `secure_storage_ipc_remove ... -140` messages as QBox, then
      logs `tee_ta_close_session`. This narrows the QBox
      `rse-ps403-filter-elapsed-20260527-v1` failure: those startup messages
      are benign reference-model behavior, while QBox still needs work in the
      pre-Linux U-Boot/SMM Gateway secure-storage timing path and the later PS
      test-403 Strata workload.
- [x] V038AB Recheck focused PS 403 with range-limited boot-flash DMI and add
      runner marker first-hit timing. Runtime
      `build/qbox-fvp-rd-aspen/rse-ps403-filter-ranged-dmi-20260527-v1/`
      used `QBOX_RDASPEN_BOOT_FLASH_DMI=true`,
      `QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000`, and
      `QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000`, but still timed out
      at `runtime_elapsed_s=120.13643014699846` before Linux or any
      secure-service command. The primary console reached
      `EFI: MM partition ID 0x8006` only. The runner now records
      `progress_marker_first_hits` for key RSE, measured-boot, EFI, Linux,
      login/root, SMM Gateway, SE-Proxy, and PS test-403 markers in
      `result.json` and `summary.txt`. Validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and the
      three-second smoke
      `build/qbox-fvp-rd-aspen/rse-progress-markers-smoke-20260527-v1/`,
      which records `rse_bl1_1` first hit at 0.503 seconds. This improves
      short-timeout judgment but does not close V038/T061/T063/T064/T076.
- [x] V038AC Re-run the focused PS 403/range-limited DMI case with marker
      timing enabled. Runtime
      `build/qbox-fvp-rd-aspen/rse-ps403-filter-marker-dmi-20260527-v1/`
      timed out at `runtime_elapsed_s=120.11020978200031` before Linux and
      before any secure-service command was sent. The marker timing records
      `rse_bl1_1` at 1.005 seconds, `rse_scp_power_on_ap` at 56.401 seconds,
      `rse_first_image_slot` at 56.501 seconds, `measured_boot_bl33` at
      63.933 seconds, `secure_smmgw_discovery_fallback` at 64.536 seconds,
      `primary_efi_mm_partition` at 64.939 seconds, and
      `secure_seproxy_remove_missing` at 65.040 seconds. No EFI boot or Linux
      marker appears by the 120-second cap. This narrows the fresh-flash
      pre-Linux timeout to the post-`EFI: MM partition ID 0x8006` SMM
      Gateway/secure-storage window.
- [x] V038AD Extend runner progress markers for the UEFI variable path. The
      runner now records first-hit timing for PK/KEK/db/dbx enrollment, FWU
      regular-state detection, and bootflow script handoff in addition to the
      existing RSE, EFI MM, EFI boot, Linux, SMM Gateway, SE-Proxy, and PS
      markers. Validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and
      `build/qbox-fvp-rd-aspen/rse-uefi-marker-smoke-20260527-v1/`, which
      still records marker timing in a three-second smoke window. This keeps
      future short SMM Gateway runs file-backed and avoids tmux-only progress
      inspection.
- [x] V038AE Add general-runner Strata flash stats for UEFI/PS debugging. The
      runner now accepts `--flash-stats` and `--flash-stats-interval`, wires
      the RSE/AP Strata stats environment variables, and records parsed
      `flash_stats` in `result.json` and `summary.txt`. Static validation
      passed with `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and help
      output inspection. The smoke
      `build/qbox-fvp-rd-aspen/rse-flash-stats-smoke-20260527-v1/` proves the
      result schema and configured paths even before flash command traffic.
      Runtime
      `build/qbox-fvp-rd-aspen/rse-uefi-marker-stats-180s-20260527-v1/`
      captured RSE Strata workload before Linux: `write_accesses=3100000`,
      `word_program_cmds=516667`, `program_ops=516667`,
      `compat_ff_sector_erase_ops=817`, `sector_erase_bytes=3346432`, and
      `backing_write_ops=307668`. The run did not reach PK enrollment before
      the 180-second cap because stats collection is diagnostic and can distort
      bounded timing. Treat marker-only runs as pass/fail timing evidence and
      stats runs as CFI workload evidence.
- [x] V038AF Validate UEFI variable persistence with a second boot and fix
      secure-service timeout classification. Runtime
      `build/qbox-fvp-rd-aspen/rse-uefi-persisted-secondboot-20260527-v1/`
      used the writable RSE flash from
      `rse-uefi-marker-180s-20260527-v1/` as its input. U-Boot reported
      `PK/KEK/db/dbx key has already been enrolled!`, then reached EFI boot at
      123.885 seconds, Linux at 132.154 seconds, login at 155.050 seconds,
      root shell at 160.737 seconds, and PS test 403 at 163.480 seconds. This
      proves the first-boot UEFI variable writes persist in the RSE Strata
      backing image and are consumed by the next boot. The runner also now
      reports missing secure-service and post-login done markers as explicit
      blockers instead of allowing Linux boot markers alone to pass a requested
      secure-service probe. Validation passed with `python3 -m py_compile`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and
      `build/qbox-fvp-rd-aspen/rse-uefi-persisted-secondboot-classify-20260527-v1/`,
      which returns `passed=false`, `timed_out=true`, and
      `blocker=qbox_secure_service_probe_incomplete_timeout` while still
      reaching Linux and PS test 403.
- [x] V038AG Split pre-login timeout classification from secure-service
      timeout classification. A 195-second PS-only rerun with persisted RSE
      flash,
      `build/qbox-fvp-rd-aspen/rse-uefi-persisted-secondboot-ps403-195s-20260527-v1/`,
      timed out before post-login probe injection, so it is not PS403
      completion evidence. The runner now reports
      `qbox_post_login_probe_not_reached_timeout` when `--post-login-probe`
      was requested but no probe command was sent. Validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` and
      `build/qbox-fvp-rd-aspen/rse-post-login-not-reached-classify-smoke-20260527-v1/`,
      which returns `passed=false`, `timed_out=true`,
      `blocker=qbox_post_login_probe_not_reached_timeout`, and
      `sent_probe=false`.
- [x] V038AH Classify PC-traced BL2 CFI/Strata flash I/O timeouts. Runtime
      `build/qbox-fvp-rd-aspen/rse-image-load-pc-trace-75s-20260527-v1/`
      timed out before AP/Linux with the RSE PC tail at `0x31023136` and
      `0x31024c9c`. `llvm-addr2line` resolves those addresses to
      `cfi_strataflashj3_read()` and `nor_cfi_reg_read()`, so the timeout is
      in firmware-visible Strata byte-read traffic while loading SI images.
      The runner now maps PC trace tail addresses through `bl2.map` and reports
      `rse_bl2_cfi_flash_io_timeout:<symbol>` for such timeout runs. Validation
      passed with `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py`,
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`, and
      `build/qbox-fvp-rd-aspen/rse-cfi-pc-classify-smoke-20260527-v1/`, which
      returns `blocker=rse_bl2_cfi_flash_io_timeout:nor_cfi_reg_read`.
- [x] V038AI Add Strata DMI stats and classify boot-flash DMI as diagnostic
      only. `strata_flash_j3` now records DMI hint/request/grant/reject and
      invalidation counters in stats and flushes stats from the DMI request
      path. Validation passed with `strata_flash_j3-tests`, `platforms-vp`,
      and runtime
      `build/qbox-fvp-rd-aspen/rse-dmi-stats-flush-20260527-v1/`. That run
      used range-limited RSE boot-flash DMI and produced
      `dmi_grants=1`, `write_accesses=0`, and `command_writes=0`, proving the
      direct mapping bypasses the CFI command-state model after the first
      grant. Keep `QBOX_RDASPEN_BOOT_FLASH_DMI=false` for storage, UEFI
      variable, and FWU evidence; future work should optimize the
      command-state Strata path rather than relying on boot-flash DMI.
- [x] V038AJ Recheck PS 403 after Strata stats hot-path optimization. QBox
      commit `941f28c42677` avoids per-access stats counter work when no stats
      file or interval is configured, and `strata_flash_j3-tests` passed. The
      first follow-up runtime,
      `build/qbox-fvp-rd-aspen/rse-ps403-after-stats-opt-20260527-v1/`,
      timed out before post-login probe injection and showed U-Boot FWU update
      interference, so it is not PS 403 evidence. The deploy-rootfs follow-up,
      `build/qbox-fvp-rd-aspen/rse-ps403-after-stats-opt-deployroot-20260527-v1/`,
      reached Linux, root shell, and PS test 403 at 165.932 seconds, then
      timed out with `qbox_secure_service_probe_incomplete_timeout` before the
      requested secure-service done marker. This proves the stats hot-path
      cleanup is useful but does not close T063; the remaining blocker is the
      firmware-visible Strata/Protected Storage test-403 workload.
- [x] V038AK Cache Strata hot-path CCI parameters and bound the post-change
      runtime check. QBox commit `bfedb120d87f` caches frequently read
      `strata_flash_j3` parameters for trace, DMI, program-FF compatibility,
      sector size, backing-file path, and stats enablement, while preserving
      runtime updates through CCI post-write callbacks. Validation passed with
      `git -C tools/qbox diff --check`, `strata_flash_j3-tests`,
      `platforms-vp`, and
      `build/qbox-fvp-rd-aspen/rse-strata-param-cache-smoke-20260527-v1/`.
      A 195-second PS403 follow-up,
      `build/qbox-fvp-rd-aspen/rse-ps403-after-param-cache-deployroot-20260527-v1/`,
      did not reach post-login probe injection: RSE reached measured boot
      `BL_33`, OP-TEE/SMM Gateway initialized on the secure console, but the
      primary console stayed empty and the runner reported
      `qbox_post_login_probe_not_reached_timeout`. Treat this as pre-login
      variability evidence, not PS403 completion evidence; T063 remains open.
- [x] V038AL Add AP PC-trace parsing to the RSE runner and recheck the
      pre-login timeout with a short diagnostic cap. The runner now records
      `ap_pc_trace` beside the existing `rse_pc_trace` in `result.json` and
      `summary.txt`, including per-component counts and each CPU's last
      sample. Static validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` and
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`. Runtime
      `build/qbox-fvp-rd-aspen/rse-ap-pc-trace-empty-primary-20260527-v1/`
      timed out at `runtime_elapsed_s=115.0855377820044` before login and
      post-login probe injection, so it is not PS403 evidence. It did not
      reproduce the prior empty-primary artifact: the primary console reached
      U-Boot, `EFI: MM partition ID 0x8006`, `FWU: System booting in Regular
      State`, PK/KEK/db/dbx already-enrolled output, and bootflow script
      handoff. AP PC trace records AP0 release from reset and later samples
      AP0 at EL0 `pc=0x4006fc90`, with AP1-AP3 parked powered off at
      `pc=0x82000`. Treat the latest bounded blocker as Linux-login-not-yet
      reached in the U-Boot/bootflow path, not as a reproduced AP
      reset-release or UART-backend failure. T063 remains open.
- [x] V038AM Add structured secure-service PS 403 progress parsing. The
      runner now records `secure_service_probe.progress` in `result.json`,
      including requested secure-service tests, the PS test-list filter, and
      PS test 403 state such as `checks_seen`, `insufficient_space_uid`,
      `remove_all_registered_uids`, and the last observed PS test line.
      Static validation passed with
      `python3 -m py_compile scripts/run_qbox_fvp_rd_aspen_rse.py` and
      `git diff --check -- scripts/run_qbox_fvp_rd_aspen_rse.py`. Existing
      artifact replay against
      `rse-secure-service-ps-only-padded-stats-20260527-v1` reports
      `checks_seen=[1]`, `insufficient_space_uid=20`, and cleanup started,
      while replay against
      `rse-ps403-after-stats-opt-deployroot-20260527-v1` reports
      `checks_seen=[1]` without UID exhaustion before the run-level timeout.
      This does not close T063; it makes short-timeout PS artifacts precise
      enough to compare without manual console-log inspection.
- [x] V038AN Classify PS 403 secure-service timeouts by progress stage.
      Runtime blocker selection now uses `secure_service_probe.progress` when
      the requested secure-service probe times out inside PS test 403. Existing
      artifact replay maps
      `rse-ps403-after-stats-opt-deployroot-20260527-v1` to
      `qbox_secure_service_ps403_timeout:check_1`, while the older padded
      PS-only log maps to
      `qbox_secure_service_ps403_cleanup_timeout:uid_20` and still reports
      `secure_psa_ps_api_test_rc=124` as a selected-test failure when the done
      marker is reached. This keeps future short-timeout blocker strings tied
      to the actual PSA PS phase.
- [x] V038AO Add secure-storage 403 comparison to the FVP/QBox log comparator.
      `scripts/compare_fvp_qbox_rse_logs.py` now accepts
      `--require-secure-storage` and emits a `storage_test_403` JSON payload
      with ITS/PS section progress, UID exhaustion, cleanup count, result, and
      FVP-vs-QBox stage delta. Existing boot marker comparison remains the
      default behavior unless the new option is requested. Validation passed
      with `python3 -m py_compile scripts/compare_fvp_qbox_rse_logs.py` and
      `git diff --check -- scripts/compare_fvp_qbox_rse_logs.py`. The
      FVP-vs-latest-QBox comparison intentionally exits 1 with
      `boot_passed=true`, `stage_delta.PS.fvp=completed`,
      `stage_delta.PS.qbox=check_1`, and
      `missing_in_qbox_from_fvp=["PS:test_403_completed"]`. The padded QBox
      comparison also exits 1 but reports `stage_delta.PS.qbox` as
      `cleanup_after_uid_20`, proving the older run got past UID exhaustion
      once and then stalled during cleanup/second-overload progress.
- [x] V038AP Defer Strata backing-file writes for writable flash runs. QBox
      commit `1936df34ab42` adds `strata_flash_j3.defer_backing_write`,
      coalesces dirty backing ranges, preserves logical write statistics, and
      enables the deferred mode for the RSE-oriented RSE/AP flash bindings.
      Validation passed with `git -C tools/qbox diff --check`, `luac -p`,
      `strata_flash_j3-tests`, and `platforms-vp`. A bounded PS403 writeback
      run,
      `build/qbox-fvp-rd-aspen/rse-ps403-deferred-backing-20260527-v1/`,
      reached U-Boot secure-variable enrollment but timed out before Linux
      login; it also exposed that destructor-only deferred flush is unsafe for
      timeout-style runs because the final stats had
      `backing_deferred_ranges=559634` and `backing_flush_ops=0`. T063 remains
      open and this is recorded as a writeback-overhead optimization plus a
      follow-up fix requirement, not as PS403 completion evidence.
- [x] V038AQ Add bounded flush for deferred Strata backing writes. QBox commit
      `d9bb9f0b558d` adds `defer_backing_flush_interval`, preserves the dirty
      range on failed flush attempts, avoids recursive close/flush, and covers
      interval-based persistence in `strata_flash_j3-tests`. Validation passed
      with focused Strata build/tests and `platforms-vp`. Short runtime
      artifacts `rse-deferred-backing-flush-20260527-v1..v4` remain timeout
      evidence only: they prove the platform still starts under short caps,
      but the exact dirty-range count before timeout varied and not every run
      wrote an RSE stats file before termination. The remaining T063 blocker is
      still Protected Storage PS403 throughput/completion, not backing-file
      range coverage.
- [x] V038AR Recheck persisted no-stats PS403 after deferred writeback. Fresh
      writable-flash runtime
      `build/qbox-fvp-rd-aspen/rse-ps403-nostats-deferred-20260527-v1/`
      ran with flash stats disabled and reached UEFI PK/KEK/db/dbx enrollment,
      bootflow script handoff, and EFI boot before timing out at 185.154
      seconds. Using that run's writable RSE/AP flash images as inputs,
      `rse-ps403-secondboot-nostats-20260527-v1` reached Linux, root shell,
      all expected driver patterns, secure-service diagnostics, and focused
      PS403 before timing out at `check_1`. A longer bounded second boot,
      `rse-ps403-secondboot-nostats-260s-20260527-v1`, reached
      `UID 21 set failed due to insufficient space` and
      `Remove all registered UIDs`, then timed out with
      `qbox_secure_service_ps403_cleanup_timeout:uid_21`. T063 remains open:
      QBox is now proven through Linux, driver probes, and PS403 UID
      exhaustion in a stats-disabled persisted run, but it still does not
      reach the FVP PS403 `TEST RESULT: PASSED` state.
- [x] V038AS Cache the Strata stats-enabled flag and recheck against bounded
      QBox/FVP runtime evidence. QBox commit `11d2928b777a` removes the
      per-access stats-parameter query from the Strata hot path while keeping
      stats behavior covered by `strata_flash_j3-tests`. Validation passed with
      `git -C tools/qbox diff --check`, focused Strata build/tests, and
      `platforms-vp`. The follow-up QBox runtime
      `build/qbox-fvp-rd-aspen/rse-ps403-after-stats-flag-cache-260s-20260527-v1/`
      timed out before Linux login with
      `qbox_post_login_probe_not_reached_timeout`, reaching bootflow script
      handoff at 253.675 seconds. This did not improve the previous best PS403
      state. The FVP verbose comparison
      `build/fvp-boot-logs/rse-verbose-critical-150s-20260527-v1/` reached RSE
      first image slot, RSE-to-SCP AP power-on, TF-M ITS/PS empty-layout
      creation, secure-world `tee_ta_close_session`, and primary Linux boot
      before the short login cap. T063 remains open and still points to QBox's
      firmware-visible TF-M Protected Storage/Strata command workload rather
      than startup SE-Proxy/SMM Gateway messages.
- [x] V038AT Optimize stats-disabled Strata hot paths without changing CFI
      command-state behavior. QBox now bypasses command-counter decoding when
      flash stats are disabled, uses a direct single-byte NOR program path for
      stats-disabled firmware byte writes, and copies read-array/status
      multi-byte reads in bulk. Validation passed with
      `git -C tools/qbox diff --check`, focused `strata_flash_j3-tests`,
      focused `ctest`, and `platforms-vp`. A persisted-flash PS403 rerun,
      `build/qbox-fvp-rd-aspen/rse-ps403-strata-hotpath-220s-20260527-v1/`,
      timed out at 220.065 seconds before Linux login and before post-login
      probe injection. It reached RSE first image slot, RSE-to-SCP AP power-on,
      measured boot through `BL_33`, and primary `EFI: MM partition ID 0x8006`,
      but it is not PS403 pass/fail evidence. The current best QBox PS403
      artifact remains `rse-ps403-secondboot-nostats-260s-20260527-v1`, which
      reached cleanup after UID 21 but still did not reach the FVP
      `TEST RESULT: PASSED` marker. T063 remains open.
- [x] V038AU Skip Strata backing writes for already-erased sectors. QBox now
      detects all-`0xff` sectors in `strata_flash_j3::erase_sector()` and
      returns ready/status state without writing the backing file when the
      sector contents are unchanged. Focused coverage adds
      `ErasedSectorSkipsBackingFileWrite`, using a deliberately too-small
      backing file to prove the no-op erase does not write out of range.
      Validation passed with `git -C tools/qbox diff --check`, focused
      `strata_flash_j3-tests`, focused `ctest`, and `platforms-vp`. A bounded
      persisted-flash PS403 rerun,
      `build/qbox-fvp-rd-aspen/rse-ps403-erased-sector-skip-240s-20260527-v1/`,
      reached RSE-to-SCP AP power-on, RSE first image slot, measured boot
      through `BL_33`, and primary `EFI: MM partition ID 0x8006`, but timed
      out before Linux login with `qbox_post_login_probe_not_reached_timeout`.
      This is pre-login regression evidence only; it does not supersede the
      previous best PS403 artifact. T063 remains open.
- [x] V038AV Cache Strata erased-sector state and bound the follow-up runtime
      evidence. QBox commit `1dfb07c84590` replaces the hot per-erase
      sector-wide all-`0xff` scan with a sector-erased map that is refreshed
      on image load, program, erase, and sector-size changes. Validation
      passed with `git -C tools/qbox diff --check`, focused
      `strata_flash_j3-tests`, focused `ctest`, and `platforms-vp`. Fresh
      and persisted-flash runtime rechecks
      `build/qbox-fvp-rd-aspen/rse-sector-cache-150s-20260528-v1/` and
      `build/qbox-fvp-rd-aspen/rse-sector-cache-secondboot-190s-20260528-v1/`
      both timed out before post-login probe injection. The persisted run
      reached AP BL2 pre-load completion and stalled while loading the AP BL2
      image from the Strata command-state path. A local no-stats access
      fast-path experiment also reached the same tail point in two 190-second
      rechecks and was reverted, so no ineffective source change is retained.
      T063 remains open and the next implementation target stays on reducing
      firmware-visible AP/RSE BL2 Strata image-read overhead without enabling
      diagnostic boot-flash DMI.
- [x] V038AW Bound CC3XX DMA burst size and classify short PC-trace timeouts.
      QBox now raises the CC3XX model's internal DMA processing chunk from
      256 bytes to 1024 bytes for AES, hash, and CMAC DMA paths, reducing TLM
      memory round trips while keeping the firmware-visible CC3XX register
      programming interface unchanged. Focused coverage adds an 8 KiB
      AES-CTR in-place regression. A 4096-byte local experiment was rejected
      because it caused SI CL1 image validation failure, so only the
      runtime-safe 1024-byte chunk is retained. Validation passed with
      `git -C tools/qbox diff --check`, focused `cc3xx-tests`, focused
      `ctest`, and `platforms-vp`. The RSE runner now classifies BL1_1 shared
      CC3XX/CFI PC-trace tails using `bl1_1.map`; existing 90-second traces
      replay to `rse_bl1_1_cc3xx_crypto_timeout:*`, and fresh runtime
      `build/qbox-fvp-rd-aspen/rse-cc3xx-dma1024-classify-45s-20260528-v1/`
      reports `rse_bl1_1_cfi_flash_io_timeout:nor_cfi_reg_read`. T063 remains
      open: this improves the modeled CC3XX DMA path and blocker precision,
      but does not yet move the best PS403 evidence beyond cleanup after
      UID 21.
- [x] V038AX Capture marker-gated GDB evidence for PS403 Check 1.
      The GDB helper now has explicit `--mhu-trace`, `--no-mhu-trace`, and
      `--mhu-trace-limit` controls so marker-gated samples can avoid heavy MHU
      logging when matching normal runner timing. A no-launch smoke verified
      the new metadata/env plumbing. Two control samples explain prior misses:
      MHU trace enabled kept the run in pre-login SE-Proxy/RSE MHU secure
      storage traffic at the 230-second cap, and the helper's console-probe
      rootfs default sent U-Boot into `FWU: Updating 5 payload(s)`. The
      corrected run
      `build/qbox-fvp-rd-aspen/gdb-ps403-check1-20260528-v4/` used the same
      baremetal rootfs as the PS403 runtime artifacts, disabled MHU trace,
      found `[Check 1] Overload storage space` after 174.053 seconds, and
      sampled RSE/TF-M 20 seconds later in `tfm_its_remove()` ->
      `its_flash_fs_delete_idx(del_file_idx=20)` ->
      `its_flash_fs_dblock_compact_block()` ->
      `its_flash_fs_block_to_block_move()` -> `its_flash_nor_write()` ->
      `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` ->
      `nor_byte_program()`. AP SE-Proxy was waiting for the RSE response
      through `rse_comms_platform_invoke()`, while Linux CPU0 was idle. T063
      remains open, now specifically on faithful acceleration of the
      firmware-visible TF-M PS/ITS Strata byte-program and compaction workload.
- [x] V038AY Recheck FVP PS403 login timing with file-backed logs.
      `scripts/runfvp_log_boot.py` now starts bounded root-login retries once
      Linux/systemd output appears, keeps retrying through late getty/login
      target output, and records `login_sent` plus `login_attempts` in the
      post-login result. The syntax check passed. A short verbose FVP run
      `build/fvp-boot-logs/rse-ps403-focused-login-retry-20260528-v1/` passed
      all boot-status consoles but did not reach the actual login prompt inside
      the 220-second script cap. It sent 24 root attempts and reached
      `Started Serial Getty on ttyAMA0` / `Reached target Login Prompts`, so the
      run is boot/login timing evidence, not PS403 pass/fail evidence. After
      that bounded run exhausted the previous retry budget, the helper retry
      cap was raised to 80 for future longer FVP comparisons. The FVP reference
      artifact
      `build/fvp-boot-logs/rse-secure-service-ps-probe-20260525-v1/` remains the
      PS403 reference because it reaches Check 1, UID 22 insufficient space,
      cleanup, Check 2, and `TEST RESULT: PASSED`. T063 remains open against the
      latest QBox fastaccess artifact
      `build/qbox-fvp-rd-aspen/rse-ps403-fastaccess-220s-20260528-v1/`, which
      reaches Linux, root, all driver probes, secure-service diagnostics, and
      PS403 `[Check 1]` before timing out.
- [x] V038AZ Add an RSE flash PS/ITS storage-state inspector and compare
      FVP/QBox PS403 artifacts. `scripts/inspect_rse_flash_storage.py` reads
      raw or gzip RSE flash images, normalizes them to the 64 MiB RD-Aspen RSE
      flash size, and reports dirty sector, dirty logical block, and baseline
      delta counts for the Protected Storage and Internal Trusted Storage
      partitions using the active TF-M layout constants. Validation passed with
      `python3 -m py_compile scripts/inspect_rse_flash_storage.py`. The report
      `build/qbox-fvp-rd-aspen/rse-storage-ps403-compare-20260528-v1/report.md`
      shows the FVP PS403-pass writable image has dirty state across all PS
      sectors (`256/256`) and ITS sectors (`64/64`), while the best QBox
      UID21-cleanup timeout image has dirty state in only `9` PS sectors and
      `1` ITS sector. T063 remains open, but now has persistent flash-state
      evidence matching the GDB finding that QBox is still executing the
      TF-M PS/ITS compaction and Strata byte-program workload rather than
      failing in Linux, driver probing, or backing-file persistence.

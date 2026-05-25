# RSE QBox Design

Created: 2026-05-20

## Architecture Overview

The RSE subsystem is added as a peer subsystem to the current QBox
primary-compute platform. It has its own Cortex-M55 execution context, local
address space, NVIC, boot media, UART, ATU, and MHUv3 endpoints. It connects to
the system address space through TLM sockets and uses QBox/QEMU components
where they already exist.

```text
        +-----------------------------+
        | QBox RD-Aspen Platform      |
        |                             |
        | +-------------------------+ |
        | | Primary Compute         | |
        | | Cortex-A720AE + GICv3   | |
        | | TF-A/OP-TEE/U-Boot/Linux| |
        | +-----------+-------------+ |
        |             | AP-RSE MHUv3  |
        | +-----------v-------------+ |
        | | RSE Subsystem           | |
        | | Cortex-M55 + NVIC       | |
        | | ROM/Flash/OTP/SRAM      | |
        | | ATU + System Control    | |
        | | TF-M BL1/BL2/Runtime    | |
        | +-----------+-------------+ |
        |             | RSE-SCP MHUv3 |
        | +-----------v-------------+ |
        | | SCP Service Model or    | |
        | | Safety Island / SCP     | |
        | +-------------------------+ |
        +-----------------------------+
```

## Component Inventory

| Component | Source/Pattern | Role |
| --- | --- | --- |
| RSE CPU | `tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_m55/` plus `platforms/cortex-m55-remote/RemoteCPU` | Execute Cortex-M55 TF-M RSE firmware |
| RSE NVIC | `tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/` | Deliver M-profile interrupts |
| RSE local router | `tools/qbox/systemc-components/router/` | Decode RSE local address space |
| RSE memories | `gs_memory` plus file-backed extensions | ROM, SRAM, and volatile memories |
| RSE boot flash | `tools/qbox/systemc-components/strata_flash_j3/` | CFI/Strata J3 command-state model for the FVP RSE boot-flash aperture; full writeback, protection, timing, and AP flash behavior remain open |
| RSE UART | existing PL011/backend pattern | File-backed RSE console logging |
| RSE ATU | `tools/qbox/systemc-components/rse_atu/` | Translation-capable RSE host-window model with target and initiator sockets, ATUBC page/region decoding, first-pass translation faults, ATURAV shift-overflow rejection, translated DMI range guards, and current SI ATU verification evidence; remaining page-boundary corner cases, richer fault status, and default-safe DMI evidence remain open |
| RSE CC3XX | `tools/qbox/systemc-components/cc3xx/` | Early TF-M RNG, SHA-256 DMA hashing, DMA completion, a tested AES-CTR memory path, and AES-CMAC tag generation; SP800-108 KDF/CTR production-flow fidelity and full CRYPTOCELL coverage remain open |
| RSE DMA350 | `tools/qbox/systemc-components/dma350/` | Early BL1_1 DMA channel command polling, observed 64-bit fill writes, and tested 1D copy commands through a TLM initiator; not a full DMA350 model |
| MHUv3 | replacement for `mhuv3_stub` | Doorbell transport for RSE/SCP/AP paths |
| System control | `tools/qbox/systemc-components/rse_sysctrl/` | Touched-register model for reset syndrome, reset mask, DMA boot, CPU wait, and selected power/reset visible state |
| LCM/OTP | `tools/qbox/systemc-components/rse_lcm/` | OTP-image-backed LCM/OTP reads and lifecycle/status reset values; full provisioning/write/lock behavior remains open |
| RSE KMU | `tools/qbox/systemc-components/rse_kmu/` | Early KMU build configuration, OTP-backed hardware key slots, key-slot state transitions, random-delay register surface, and destination-port key export |
| Integrity Checker | `tools/qbox/systemc-components/rse_integrity_checker/` | Early status/done model for the TF-M integrity-check register surface; runtime has not reached it yet |
| Host PPU | `tools/qbox/systemc-components/host_ppu/` | Narrow PPU policy/status model for SI CL0 cluster/core PPU polling during BL2 pre-load |
| Flash | `strata_flash_j3` for RSE boot flash plus remaining file-backed NVM work | FVP-compatible RSE/AP flash behavior |
| SCP service model | new SystemC/TLM model or real SI/SCP execution | Protocol-correct RSE-SCP SCMI endpoint for MVP |

## Evidence Ledger

The baseline evidence for this feature lives in
`doc/spec/rse-qbox/evidence.md`. That file owns artifact paths, FVP parameters,
log markers, current QBox gaps, and the selected SCP/Safety Island strategy for
each implementation milestone. Design changes should update the ledger before
changing code.

## Reviewed QBox Skeleton Binding

Static inspection first showed that `platforms-vp` can instantiate the existing
M-profile CPU from Lua, but runtime trace proved that direct nested binding of
`rse_cpu.nvic.mem` does not bind the CPU-local NVIC/SCS window through the
top-level container. The active skeleton therefore uses the existing
`platforms/cortex-m55-remote` pattern:

- `qemu_inst_mgr` with `moduletype = "QemuInstanceManager"`;
- `qemu_inst` with `moduletype = "QemuInstance"` and target string
  `AARCH64`;
- `rse_router` with `moduletype = "router"`;
- `rse_cpu_pass` with `moduletype = "RemotePass"`;
- `RemoteCPU` in the remote process, wrapping `cpu_arm_cortexM55`, its internal
  router, and its NVIC;
- pass initiator sockets bound to `&rse_router.target_socket`;
- remote `plugin_pass.target_socket_0` covering `0x00000000..0xDFFFDFFF` so
  normal RSE memory accesses reach the top-level RSE router;
- the `0xE000E000..0xE000FFFF` NVIC/SCS window kept CPU-local inside
  `RemoteCPU`;
- `init_svtor` and `init_nsvtor` pointed at RSE ROM secure base
  `0x11000000`.

The Cortex-M55 module library name matches its `moduletype`, so no
`dylib_path` is required. PL011 still needs `dylib_path = "uart-pl011"`
because its module type is `Pl011`.

`platforms-vp` now includes `remote.h` so `RemotePass` is registered in the
generic Lua platform executable. Without that include, the module factory tries
to load a non-existent `RemotePass.so`.

## Boot Media Design

The RSE-oriented QBox mode uses the same generated files as FVP:

| FVP Parameter | QBox Parameter | Artifact |
| --- | --- | --- |
| `css.smb.rseil.rse.rom.raw_image` | `QBOX_RDASPEN_RSE_ROM` | `rse-rom-image.img` |
| `css.smb.rseil.rse_flashloader.fname` | `QBOX_RDASPEN_RSE_FLASH` | `rse-flash-image.img` |
| `css.smb.rseil.rse.lcm_nvm.raw_image` | `QBOX_RDASPEN_RSE_OTP` | `rse-otp-image.img` |
| `ros.flash_loader.fname` | `QBOX_RDASPEN_AP_FLASH` | `ap-flash-image.img` |
| `FVP_DATA css.smb.rseil.rse.sram1@0x20000` | `QBOX_RDASPEN_PROVISIONING_BUNDLE` | `combined_provisioning_message.bin` |

Writable flash files should be copied into a per-run output directory by
default, matching the existing FVP log helper behavior. The original deploy
artifacts remain immutable inputs unless explicitly requested.

## Address Space Design

### RSE Local Address Space

The first implementation should model only regions touched by TF-M RSE boot,
then expand from trace evidence.

| Region | Initial address | Behavior |
| --- | --- | --- |
| ROM | `0x11000000`, size `0x20000` | read-only file-backed image |
| ITCM | `0x10000000`, CPU0 alias `0x1A000000`, size `0x8000` | volatile memory used by BL1_1 erase/fill |
| ITCM NS aliases | `0x00000000`, CPU0 alias `0x0A000000`, size `0x8000` | decoded aliases to the same ITCM backing store |
| DTCM | `0x30000000`, CPU0 alias `0x34000000`, size `0x8000` | volatile memory used by BL1_1 stack and CC3XX DMA remap |
| DTCM NS aliases | `0x20000000`, CPU0 alias `0x24000000`, size `0x8000` | decoded aliases to the same DTCM backing store |
| VM0 | `0x31000000`, size `0x40000` | volatile memory, matching `VMADDRWIDTH=18` |
| VM1 | `0x31040000`, size `0x40000` | provisioning bundle loaded at `0x31060000` |
| RSE flash aperture | `0xB0000000`, size `0x04000000` | `strata_flash_j3` CFI/Strata command model backed by the per-run raw `rse-flash-image.img` copy; full writeback/protection/timing still required |
| ATU | `0x50150000` | translation model for secure and non-secure host windows with disabled-region, out-of-range, output security-domain, page-shift overflow, and translated-DMI range handling; full page-boundary and richer status semantics still required |
| SIC MPC | `0x50151000` | system interconnect memory protection configuration |
| KMU | `0x5009E000` | touched-register model for KMUBC, KMUIS/KMUIC, PRBG seed input, slot configuration, key words, and random-delay reads |
| DMA350 | `0x50002000` | Early `DMASECINFO`, channel command polling, and BL1_1 fill writes |
| CC3XX | `0x50154000` | CRYPTOCELL register model; previous first blocker write `0x501541c4` now handled by limited RNG model |
| System counter control/read | `0x5015A000`, `0x5015B000` | placeholder until TF-M touched-register behavior is identified |
| Integrity checker | `0x5015C000` | touched-status model for ICBC, ICIS/ICIC, ICC start/done, ICCVAL, and PID/CID reset values |
| TRAM | `0x5015D000` | volatile memory for BL1_1 TRAM key writes |
| LCM registers | `0x500A0000` | OTP-backed register/lifecycle skeleton; trace now shows reads after ATU setup |
| OTP wrapper | `0x58111000` | placeholder for direct OTP wrapper semantics; current early reads are served through `rse_lcm` |
| RSE host UART alias | `0x6FF00000` NS, `0x7FF00000` S | initial file-backed UART skeleton before full ATU path |
| system control registers | `0x58021000` | touched-register model for `reset_syndrome`, `reset_mask`, `cpuwait`, DMA boot enable/address, and selected power/reset state |
| MHUv3 frames | touched-register model | PBX/MBX frames for AP-RSE and RSE-SCP paths |
| ATU non-secure window | `0x6000_0000..0x6fff_ffff` | translated host access through `rse_atu.translation_socket` |
| ATU secure window | `0x7000_0000..0x7fff_ffff` | translated host access through `rse_atu.translation_socket` |
| RSE integration layer | `0x58100000` | touched integration registers needed by BL2 platform post-init |
| SI PIK/SCR/PPU windows | translated host physical windows | static host windows plus `host_ppu` subwindows used by BL2 SI CL0 pre-load |

### ATU Behavior

The current `rse_atu` component is a translation bring-up model, not the final
ATU design. It has one target socket on the RSE local bus, one initiator socket
for translated host accesses, and implements the register surface observed in
BL1/BL2:

- `ATUBC = 0x000000c5`, which TF-M decodes as 4 KiB pages and 32 regions;
- ATUBC PS and RC fields drive page-size conversion and supported-region
  scanning, including tested 8 KiB page and 8-region configurations;
- control, interrupt enable, and interrupt clear registers;
- region start, end, translated-base, output-base, and attributes arrays;
- address translation for enabled regions in the secure and non-secure host
  windows;
- configured-but-disabled region rejection for accesses that match a programmed
  region;
- out-of-range rejection for accesses that start inside a region but extend
  past the programmed end;
- ATUROBA AXNSE/AXPROT1 output-domain decode with a CCI-configurable
  `permitted_security_domains` policy, defaulting to all domains allowed for
  current runtime compatibility;
- ATUIS/ATUMA mismatch latching and trace reason strings for translation
  faults;
- region range rejection for accesses below the start or at/above the exclusive
  end, avoiding unsigned `end - logical` underflow when lower enabled regions
  precede the matching region;
- ATURAV page-shift overflow rejection before byte-offset construction;
- TLM error responses for currently unmapped translated host targets;
- translated DMI grants for downstream memories, with positive-offset DMI range
  clamping, two's-complement negative add-value handling, and full-range DMI
  invalidation when ATU mappings change;
- optional trace parameters for file-backed runtime evidence.

The 2026-05-21 trace shows BL1_1 reading ATUBC, programming region 0 for the
non-secure host UART window, enabling the ATU, and then continuing into LCM/OTP
reads. Later 2026-05-21 traces show BL2 translating SI PIK reads and SI CL0
SRAM writes through host physical addresses such as `0x400002a600000` and
`0x4000120000000`.

Current 2026-05-25 runtime evidence records SI ATU regions 0..16, SI CL0
reset release/post-load, and measured-boot markers through `BL_33` with no
first failing register access. Full fidelity still requires remaining
page-boundary semantics, richer fault status, default-safe DMI evidence, and
deeper negative/fault verification.

## Early CC3XX And DMA350 State

The first concrete RSE device replacement is intentionally narrow. The CC3XX
model implements the BL1_1 RNG path that previously failed at
`CC3XX_BASE_S + 0x1c4`. It returns stable readiness for the early TF-M driver
checks and deterministic EHR words so firmware can progress through the startup
entropy fill path.

The model has since been expanded to cover the observed BL1_1/BL1_2 paths:
DMA completion bits, SHA-256 DMA input with `HASH_H[0..7]` updates, an
AES-CTR memory-to-memory path, and AES-CMAC tag generation with component test
coverage. It also preserves SHA-256 multipart state through `HASH_H[0..7]` and
`HASH_CUR_LEN0/1` register writes, matching the TF-M PSA hash restore path used
by LMS/LMOTS validation. This is still not full CRYPTOCELL coverage. Current
runtime evidence reaches BL1_2, decrypts BL2 successfully, validates BL2, jumps
to BL2, and prints `Starting bootloader` after `KMU_HW_SLOT_KCE_CM` is loaded
from the OTP hardware-key area and exported into CC3XX, provided the runner
gives QBox a raw decompressed flash image. Later ATU/host-window/PPU work moves
the remaining observed blocker to the post-SI-CL0 image-loading path. The
default path still has no first failing register access, but optional ATU DMI
exposes the explicit SI CL0 image 3 RAM-load error.

The DMA350 model returns four channels through `DMASECINFO = 0x30`, clears
channel command writes immediately, and executes the observed BL1_1
one-dimensional 64-bit fill path when firmware writes `CH_CMD=ENABLE`. The
fill path reads `CH_DESADDR`, `CH_XSIZE`, `CH_XADDRINC`, and `CH_FILLVAL`, then
uses a TLM initiator socket to write the target memory through the RSE router.
It also supports the current 1D copy programming model with source/destination
address, X-size high bits, contiguous/strided X increments, and DONE/ERR status
for component-level validation.

This is a `functional-fill-copy-model`, not full DMA350 fidelity. It still does
not execute DMA ICS programs, raise interrupts, model multi-dimensional
transfer behavior, or enforce security and transaction attribute behavior.
Those behaviors remain required before DMA350 can be treated as FVP-equivalent.

## Early RSE System-Control State

The RSE system-control model exists to remove the first post-DMA BL1_1 blocker
without pretending to cover the full RSEIL reset and lifecycle controller. It
is mapped at `0x58021000` and provides the TF-M-touched offsets from
`rse_sysctrl_t`:

- `reset_syndrome` at `0x100`, reset to the FVP-configured `0x80000000`;
- `reset_mask` at `0x104`;
- `swreset` at `0x108`, currently write-accepted without stopping the
  simulation;
- `gretreg`, `initsvtor0`, `cpuwait`, `nmi_enable`, `pwrctrl`, `gretexreg`;
- `dma_boot_en`, `dma_boot_addr`, and `lcm_dcu_force_dis`.

The 2026-05-21 runtime evidence shows the previous `0x58021100` abort is
removed. BL1_1 reads `reset_syndrome`, reads `reset_mask`, writes
`reset_mask = 0x100`, and then continues into ATU programming and LCM/OTP
reads. The model is therefore a `touched-register-model`. It still lacks real
reset lifecycle behavior, CPU hold/release side effects, SWRESET integration
with the platform, DMA boot side effects, lifecycle coupling, and interrupt
behavior.

## Early RSE ATU And LCM/OTP State

The current ATU and LCM models are only deep enough to replace the previous
post-system-control uncertainty with traceable register behavior:

- `rse_atu` exposes ATUBC, the region programming arrays touched by TF-M, and
  enabled-region translation through an initiator socket. Runtime evidence
  shows region 0 writes followed by `ATUC = 0x1`, later SI PIK reads, and SI
  CL0 SRAM writes through translated host physical addresses.
- The non-secure host UART alias at `0x6ff00000` is currently wired directly
  to the RSE host UART PL011 so early stdout can use the TF-M logical address
  while host UART fidelity remains under review.
- `rse_lcm` maps the LCM register window at `0x500a0000` and backs the observed
  OTP reads with `rse-otp-image.img`.
- Later traces progress past the early ATU/LCM-only blocker and now emit TF-M
  BL1_1/BL1_2 UART markers through `BL2 image decrypted successfully`.

This means the early ATU/LCM register surface is no longer the current first
runtime blocker. Full modeling still needs complete ATU page-size semantics,
richer ATU fault status, LCM lifecycle behavior, OTP provisioning/write/lock
semantics, MPC side effects, and any later reset lifecycle interactions before
FVP-equivalent claims.

## Early KMU And Integrity Checker State

The RSE KMU model is a touched-register increment based on the TF-M KMU driver
layout. It exposes `KMUBC = 0x003d0005`, seven hardware key slots with
`KMUKSC = 0x00d60100`, hardware export addresses at `0x50154400`, PRBG seed
input writes, key-slot register storage, key-slot verify/export/invalidate
completion bits, and read-only random-delay registers at `KMURD_8`,
`KMURD_16`, and `KMURD_32`. Hardware slots 1 through 6 are initialized from the
LCM OTP hardware-key area in `rse-otp-image.img`; slot 4
`KMU_HW_SLOT_KCE_CM` is loaded from offset `0x60` and exported through the
initiator socket when TF-M requests the external CC3XX key.

The RSE Integrity Checker model exposes the TF-M register surface with
`ICBC = 0x109`, interrupt status/clear, digest address/length, expected and
computed value registers, and PID/CID reset values. A write to `ICC` with the
start bit sets the done bit in `ICIS`. It is only a `touched-status-model`;
it does not yet compute digests or move data through a DMA/initiator path.

The earlier KMU random-delay and `__cmsis_start` blockers are superseded by
later shared-memory, SAM, CC3XX hashing, KMU export, CMAC, OTP-backed KCE_CM,
and raw flash-loader evidence. The current modular-PKA runtime reaches:

- `[INF] Starting TF-M BL1_1`
- `[INF] Jumping to BL1_2`
- `[INF] Starting TF-M BL1_2`
- `[INF] Attempting to boot image 0`
- `[INF] BL2 image decrypted successfully`
- `[INF] BL2 image validated successfully`
- `[INF] Jumping to BL2`
- `[INF] Starting bootloader`
- `[INF] PSA Crypto init done, sig_type: EC-P256`

Historical host-PPU evidence, captured before the current modular-PKA model,
also reached:

- `[INF] BL2: SI CL0 pre load complete`
- `[INF] Primary   slot: version=2.16.0+0`
- `[INF] Secondary slot: version=2.16.0+0`

The runner reaches image slot 0 by initializing invalid RSE FWU private
metadata only in the per-run writable flash copy. The original deploy flash
image remains immutable input evidence. The runner also decompresses
gzip-formatted RSE flash into a per-run raw image before binding it to
`gs_memory`, matching the FVP flashloader-visible payload rather than the
compressed transport file. The previous BL1_2 post-decrypt
signature-validation gap is now closed by CC3XX SHA-256 multipart state
restore support. The first BL2/MCUboot blockers after `Starting bootloader`
were RSE integration-layer registers, missing translated host windows, PPU
polling, and an RSE ATU region-range bug that let a lower enabled region match
accesses above its end. Those are modeled far enough that current runtime
evidence completes SI CL0 pre-load and prints primary/secondary slot versions.
The post-version timeout is now mapped to the BL2 CFI flash read path during
SI CL0 image 3 RAM loading. Default-path PC samples point at
`cfi_strataflashj3_read()`/`nor_cfi_reg_read()` while copying to the SI CL0
load address. With optional translated DMI enabled, the same phase reaches the
explicit MCUboot failure `Image 3 RAM loading to 0x70083c00 is failed`, removes
both slots, and stops before `BL2: SI CL0 post load start`. The latest
host-window-filtered CC3XX trace shows no CC3XX DMA for `0x70083c00`, so the
next design increment is the SI CL0 `flash_area_read()` path. The generated
TF-M build currently has `PLATFORM_HAS_BOOT_DMA:BOOL=OFF`, and the filtered
DMA350 trace records no image-load copy operation, so this is not an active
DMA350 `boot_dma_memcpy()` path. It is the CFI/Strata flash-driver
`ReadData()` byte-copy from RSE flash into the ATU-translated host SRAM
window. T019AG proves that copy for the primary SI CL0 image. T019AH then
traces the BL2 encrypted-image path and shows the failure is inside
`boot_enc_load()` after `boot_decrypt_key()`/`bootutil_aes_kw_unwrap()` is
reached, before `boot_enc_set_key()` or `boot_enc_decrypt()` executes. It is
not a broader static host-window expansion.

## MHUv3 Design

The MHUv3 model should be a reusable SystemC component, not an RD-Aspen-only
responder. The current direct-boot `mhuv3_stub` mixes MMIO register behavior,
SCMI shared-memory responses, and peer signaling in one compatibility
component. The RSE-oriented path must split those responsibilities before
using MHUv3 as evidence for firmware-mediated boot.

The reusable model should expose:

- PBX frame object
- MBX frame object
- channel count CCI parameters
- per-channel doorbell state
- interrupt mask, set, status, and clear semantics
- peer binding between PBX and MBX
- optional trace hooks for doorbell events

Direct-boot compatibility can be retained as an adapter layered above the real
doorbell model. That adapter may answer basic SCMI messages for existing Linux
direct boot tests, but it must be clearly named as compatibility support.
Current `mhuv3_stub` behavior keeps that adapter opt-in: `direct_boot_compat`
defaults to false, and the primary-compute direct-boot Lua config is the only
platform config that enables it.

The first component tests should prove PBX-to-MBX delivery, MBX-to-PBX
transfer acknowledgment, interrupt assertion/deassertion, mask behavior,
multi-pair isolation, and invalid access responses. Tests must bind IRQ
signals explicitly so unbound interrupt ports do not hide broken interrupt
behavior.

The AP/SI Linux-visible MHU windows must follow the FVP AP ATU programming and
the generated TF-A device tree, not the SI-local SCP addresses directly:

| AP logical | Host physical | QBox object | Linux role |
| --- | --- | --- | --- |
| `0x40020000` | `0x400003b000000` | `host_ap_si_ns_scmi_mhu_pbx` | non-secure SCMI TX, IRQ 112 |
| `0x40050000` | `0x400003b040000` | `host_ap_si_ns_scmi_mhu_mbx` | non-secure SCMI RX, IRQ 113 |
| `0x40080000` | `0x400003b080000` | `host_ap_si_scmi_mhu_pbx` | secure AP/SI SCMI TX |
| `0x400b0000` | `0x400003b100000` | `host_ap_si_cl1_mhu_pbx` | SI CL1 remoteproc TX, IRQ 120 |
| `0x400e0000` | `0x400003b140000` | `host_ap_si_cl1_mhu_mbx` | SI CL1 remoteproc RX, IRQ 121 |
| `0x40110000` | `0x400003b380000` | `host_ap_si_pfdi_monitor_mhu_pbx` | PFDI monitor SCMI |

The non-secure SCMI pair uses the TF-A shared SRAM window at `0x00180000`.
T019AU runtime evidence shows Linux MHUv3 probes at `0x400b0000`,
`0x400e0000`, `0x40020000`, and `0x40050000` all return 0 and the SCMI
mailbox transport probes. The remaining SI CL1 gap is therefore above basic
AP MHU address decode: QBox still lacks an SI CL1 runtime/RPMsg peer with the
FVP-visible behavior.

## SCP/Safety Island Strategy

The RSE-oriented MVP shall choose one of two explicit strategies:

| Strategy | Fidelity label | Use in MVP |
| --- | --- | --- |
| Protocol-correct SCP service model | `functional-model` | Preferred first step when real SI/SCP execution would block RSE bring-up |
| Real Safety Island CL0/SCP execution | `fvp-equivalent` candidate | Required before claiming full RSE-SCP/FVP equivalence |

The SCP service model is not allowed to be a one-shot success stub. It should
be a separate component from MHUv3 so MHU remains the doorbell transport and
the service model owns protocol decode. It must:

- receive MHUv3 doorbells from RSE,
- read SCMI messages from shared memory through TLM,
- validate channel status, flags, length, header, protocol, message ID, and
  token,
- write protocol-correct SCMI responses,
- ring the response doorbell,
- drive observable AP power/reset state,
- emit log/result evidence with the selected fidelity label.

If the SCP service model is used for MVP, the remaining gap to real SI/SCP
execution must remain open in `evidence.md` and `task.md`.

## Boot Flow Design

### RSE-Oriented Mode

1. Load RSE ROM, RSE flash, RSE OTP, AP secure flash, and provisioning bundle.
2. Start Cortex-M55 at the RSE reset vector.
3. Keep AP primary core held until RSE/SCP release it.
4. Let RSE BL1_1 provision OTP, validate BL1_2, and jump.
5. Let RSE BL1_2 load/decrypt/validate RSE BL2.
6. Let RSE BL2 load SI CL0, SI CL1, AP BL2, and RSE runtime.
7. Deliver RSE-SCP SCMI doorbells through MHUv3.
8. Release AP through the modeled power/reset path.
9. Continue AP firmware boot and Linux boot.

### Direct Mode

The current direct mode remains available:

- load kernel and DTB directly
- keep compatibility SCMI responder active if needed
- do not claim RSE coverage from direct mode

## Logging And Artifacts

Each run should produce:

- `qbox-rse.log`
- `qbox-scp.log`
- `qbox-secure-console.log`
- `qbox-primary-console.log`
- `result.json`
- optional `fvp-comparison.json`

RSE UART logging should use `char_backend_file` for the skeleton and set both
`read_file` and `write_file` explicitly. The backend socket is
`biflow_socket`, while PL011 exposes `backend_socket`.

The result JSON should include:

- command line
- input artifact paths
- copied writable artifact paths
- pass/fail patterns
- missing required markers
- first failing RSE register access if boot stalls
- optional RSE PC trace summary, including trace path, sample count, last PC,
  and tail unique PCs, when QEMU trace does not expose a first failing access
- boot mode: `direct` or `rse-oriented`
- SCP strategy: `service-model` or `real-si-scp`
- fidelity label for each RSE-related block

## Validation Patterns

Minimum RSE boot patterns:

- `Starting TF-M BL1_1`
- `Jumping to the first image slot`
- `SI CL0 is released out of reset`
- `Init SCMI comm to SCP succeeded`
- `RSE to SCP SCMI power on AP succeeded`
- `SCMI Comms subscribed to power state notifications`

Measured boot patterns:

- `BL1_2`
- `BL2`
- `SI_CL0`
- `AP_BL2`
- `RT_0`
- `SECURE_RT_EL3`
- `SECURE_RT_EL1_SPMD`
- `BL_33`

Reset/poweroff/FWU patterns:

- `[NOT][SCMI] Resetting system`
- `[INF] Starting TF-M BL1_1`
- `[NOT][SCMI] System shutdown complete`
- `[INF] Attempting to boot image 1`

## FVP Comparison Rules

FVP-vs-QBox comparison should normalize timestamps, host-specific paths, telnet
ports, and copied writable-image filenames before comparing logs. The first
automated comparison shall fail only on deterministic semantic differences:

- missing required boot markers,
- marker order violations,
- missing MHUv3 doorbell event evidence,
- missing SCMI AP power-on response,
- missing measured boot marker,
- AP boot before modeled RSE/SCP release,
- missing Linux login marker for MVP.

Secure services and firmware update markers are compared only for post-MVP
scenarios.

## Fidelity Labels

Every modeled RSE-related block should use the project labels:

- `fvp-equivalent`
- `functional-model`
- `static-map-only`
- `temporary-stub`
- `not-modeled`

The first design target is `functional-model` for Cortex-M55 execution,
boot media, ATU, and MHUv3. `fvp-equivalent` requires passing FVP-vs-QBox
comparisons for the supported boot scenario.

## Review Resolutions And Open Questions

Resolved by inspection:

1. Direct Lua instantiation of `cpu_arm_cortexM55` is syntactically supported
   by the QBox module factory and dynamic module registration.
2. The QEMU instance target string for Cortex-M55 in this repository is
   `AARCH64`, not `ARM`.
3. The direct CPU owns an internal child named `nvic`; Lua bindings should use
   `&rse_cpu.nvic.mem` and `&rse_cpu.nvic.irq_in_<n>`.
4. The MVP SCP strategy is the protocol-correct SCP service model, with the
   real Safety Island/SCP execution gap kept open.
5. The generated RD-Aspen RSE ROM reaches CC3XX initialization through
   `RemoteCPU`; the earlier `0x501541c4` Data Abort is now removed by the
   limited CC3XX model.
6. The generated RD-Aspen RSE ROM reaches the RSE system-control window after
   DMA350 fill writes. The earlier `0x58021100` reset-syndrome fault is now
   removed by the limited `rse_sysctrl` model.
7. The generated RD-Aspen RSE ROM reaches ATU programming and then LCM/OTP
   reads after the `reset_mask = 0x100` write. The `rse_atu` model now removes
   the immediate ATU register gap and translates enabled secure/non-secure
   host windows through a TLM initiator. The BL2 SI PIK access at logical
   `0x7540a000` now selects region 12 and reaches host physical
   `0x400002a600000`; first-pass disabled-region, out-of-range, and output
   security-domain fault handling is now modeled, and ATUBC PS/RC fields now
   drive page-size and supported-region decisions. The ATU model also rejects
   ATURAV page-shift overflow and hardens translated-DMI range conversion
   while preserving TF-M two's-complement negative add-values. Current runtime
   evidence reaches SI ATU regions 0..16, SI CL0 release, and measured boot
   through `BL_33`. Remaining gaps are full page-boundary semantics, rich fault
   status, default-safe DMI evidence, and deeper negative/fault verification.
8. The generated RD-Aspen RSE ROM reaches KMU random-delay reads after the
   early CC3XX path. The `rse_kmu` model now removes the untyped KMU
   placeholder, performs destination-port key export to CC3XX, and loads the
   hardware-slot key material from the LCM OTP hardware-key area.
9. The Integrity Checker has a touched-status model and component tests, but
   current runtime evidence does not reach its register window yet.
10. The generated RD-Aspen RSE ROM now emits BL1_1/BL1_2/BL2 UART markers
    through BL2 PSA Crypto initialization and SI CL0 pre-load with the current
    modular-PKA model. Current runtime evidence reaches primary/secondary
    slot-version output. The previous `__cmsis_start` timeout, BL2 decrypt
    failure, BL1_2 LMS/LMOTS signature-validation failure, initial BL2
    host-window gap, PPU polling loop, and `0x7540a000` HardFault are
    superseded.
11. Invalid generated RSE FWU private metadata at flash offset `0x5000` can
    be normalized to slot 0/READY for bring-up when, and only when, the runner
    uses a per-run writable flash copy.
12. The previous `0x7540a000` exception is now traced to RSE ATU range
    matching and fixed: the model rejects addresses at or above a region's
    exclusive logical end before access-length arithmetic, then translates the
    SI PIK access through region 12 to `0x400002a600000`.
13. The previous post-SI-CL0 slot-version timeout is now mapped to SI CL0 image
    3 RAM loading. Default-path PC samples sit in the RSE flash CFI read loop,
    and the opt-in translated-DMI path reports `Image 3 RAM loading to
    0x70083c00 is failed` followed by `Unable to find bootable image`.
14. The latest CC3XX host-window DMA trace shows no CC3XX transfer to
    `0x70083c00`; TF-M source shows the failing copy happens in
    `flash_area_read()` before encrypted payload decryption.
15. T019AE shows `PLATFORM_HAS_BOOT_DMA:BOOL=OFF` in the active TF-M
    `CMakeCache.txt`, so the BL2 SI CL0 image 3 copy does not use the DMA350
    `boot_dma_memcpy()` branch in this generated image.
16. T019AF replaces the RSE boot-flash aperture with `strata_flash_j3` and the
    same runtime still reaches the image 3 failure. The remaining design
    question is copied-data validity and MCUboot encrypted-image handling, not
    whether the boot-flash aperture is still plain memory.
17. T019AG proves copied-data validity with a per-run file-backed
    `host_si_cl0_sram` image. The primary SI CL0 header and code samples match
    RSE flash offsets `0x67000` and `0x67400`, and the reordered host-SRAM
    image matches the primary slot for `0xb6b1e` bytes. That value is the
    MCUboot `boot_read_image_size()` result for the encrypted RAM-load image.
    The AES-KW TLV `0x31/0x18` is present, but the SRAM payload still matches
    encrypted flash, so payload decrypt did not visibly run.
18. T019AH splits the encrypted-image key path with QEMU `in_asm` filtered to
    BL2 `boot_enc_*` symbols. The trace hits `boot_enc_load()`,
    `boot_decrypt_key()`, and `bootutil_aes_kw_unwrap()`, but never reaches
    `boot_enc_set_key()` or `boot_enc_decrypt()`. Because `ram_load.c` calls
    `boot_enc_set_key()` only when `boot_enc_load()` returns `0`, the
    historical blocker was
    `si_cl0_boot_enc_load_decrypt_key_failed_before_set_key`.
19. Later T019AI through T019AS work supersedes the SI CL0 and AP BL31
    blockers. The current RSE-oriented platform loads SI CL0, AP BL2, RSE
    runtime, BL31, OP-TEE/SPMC, and BL33 far enough for Linux to boot.
20. T019AU aligns the AP/SI MHU windows with the FVP ATU map and generated
    Linux DT. Runtime evidence reaches Linux login, and all AP/SI Linux MHUv3
    probes return 0.
21. QBox now loads the CFG2 SI CL1 image through the RSE BL2 path and later
    Linux/post-login evidence proves remoteproc attach plus RPMsg module
    loading. A real SI CL1 runtime/RPMsg peer is still not proven because the
    logs do not yet show a Linux-visible `ethsi1` RPMsg channel.
22. AP-RSE bridge/IRQ evidence now reaches the FVP RSE runtime markers
    `SCMI Comms subscribed to power state notifications` and measured-boot
    `RT_0`.

Still open:

1. Which SI CL1 firmware image/configuration evidence makes FVP load SI CL1,
   and which QBox model or firmware-load path should supply the matching
   remoteproc/RPMsg peer?
2. Which SI CL1 service model or executable Safety Island path should prove a
   Linux-visible `ethsi1` RPMsg channel without faking the channel in Linux?
3. Which remaining LCM, OTP, boot-media, MPC, DMA350, ATU translation, KMU,
   and RSEIL side effects are still temporary compatibility behavior rather
   than FVP-equivalent SystemC/TLM models?
4. Should the QBox boot-media model own gzip/raw flashloader conversion, or
   should the runner remain the compatibility boundary until a file-backed
   flash component replaces `gs_memory`?
5. Which MHUv3 register subset is sufficient for TF-M/SCP/AP firmware before
   full TRM coverage is implemented?
6. Which post-login probes should be promoted into the runner so driver
   readiness is checked from files rather than a terminal view?

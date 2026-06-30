# QBox Apollo FVP Full-System Design

Generated: 2026-06-03

Status: implemented and verified

Goal and final completion verification are defined in
`doc/qbox-apollo-fvp-full-system-goal-verification.md`. This design document
describes the platform shape; the goal-verification document is the review
contract for when the task can be called complete.

## Objective

Use the local Apollo boot artifacts to run a QBox emulation target that matches
the Apollo FVP system shape:

- RSE/System Management: Cortex-M55 running TF-M.
- Safety Island CL0: Cortex-R82AE-class system-management firmware running
  SCP-firmware.
- Safety Island CL1: Cortex-R82AE-class Zephyr/OpenAMP firmware.
- Primary Compute: Cortex-A720AE running TF-A, OP-TEE, U-Boot, and Linux.

The target is FVP-equivalent functional behavior for the local
`apollo-fvp` configuration, not only a Linux direct-boot shortcut.

## Completion Boundary

The full-system task has one final completion point:

```text
RSE TF-M -> SI CL0 SCP-firmware -> SI CL1 Zephyr -> AP TF-A/OP-TEE/U-Boot/Linux
```

All four domains must be live in the same QBox run for the final gate. AP Linux
login, RSE-first service-model boot, and isolated Safety Island firmware runs
are milestone evidence only. They are useful regression gates, but they do not
prove Apollo FVP equivalence.

Completion can be claimed only from the saved
`build/qbox-apollo-fvp/full-live-cl0-cl1/` evidence directory after
`scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final` writes a
passing `final-verification.json`. The final JSON must show:

- `completion_claim_allowed: true`
- `completion_ready: true`
- `overall_gates.G0..G5 == "pass"`
- RSE, SI CL0, SI CL1, AP firmware, Linux, post-login, map, interrupt, ATU,
  FVP-comparison, and hardware-coverage checks with no unclassified failure

Any missing live-domain marker, absent boot-critical hardware block,
unreviewed fidelity gap, or tmux-only observation is not a completion point and
must be reported as `blocked`, `fail`, or `not_run` in machine-readable output.

The verifier may also attach isolated milestone evidence, such as the current
QAP-FULL-020 CL1 Zephyr pass, under `milestone_evidence`. That evidence is
useful for review and regression tracking, but it does not advance the G0-G5
completion gates and cannot authorize a full-system completion claim.

## Evidence Inputs

The design is based on the current workspace state:

- `tools/qbox-platform/platforms/apollo/apollo-pc.lua` is the current Apollo
  primary-compute direct-boot platform.
- `scripts/run/run_qbox_apollo_fvp_linux.py` boots local `Image` and
  `initramfs.cpio.gz` directly and bypasses RSE, TF-A, OP-TEE, and U-Boot.
- `tools/qbox-platform/platforms/apollo/hw-block/rse.lua` contains the Apollo-owned
  RSE-first topology imported from the existing RD-Aspen RSE platform: RSE
  Cortex-M55, AP firmware chain, AP reset release, AP/RSE/SI MHUv3 paths,
  AP-SI HIPC/RPMsg service-model hooks, PFDI monitor plumbing, and
  file-backed multi-console logs.
- `scripts/run/run_qbox_fvp_rd_aspen_rse.py` already implements artifact
  preparation, per-run writable flash/OTP copies, flash decompression and
  padding, marker evaluation, post-login probes, FWU probes, and structured
  `result.json` output.
- `scripts/inspect/probe_qemu_cortex_r82.py --source-root .` currently passes source
  probes for the QEMU Cortex-R82 CPU model, EL2 MPU sysregs, 64-bit PMSAv8
  storage, and the QBox `cpu_arm_cortexR82` wrapper.
- `doc/arm_zena_css_dev_guide/`, `doc/arm-zena-css-hardware-blocks.md`, and
  `doc/safety-island-and-zephyr.md` describe the subsystem split, HIPC shared
  memory, MHUv3, PFDI, and Safety Island firmware expectations.
- `doc/qbox-apollo-fvp-map-analysis.md` normalizes the memory map,
  interrupt map, ATU windows, and hardware block coverage that must be reflected
  in the full-system QBox target.

## Local Artifact Contract

The full-system QBox runner should consume the local build deploy tree by
default:

| Role | Default path |
| --- | --- |
| RSE ROM | `build/local-apollo-fvp/deploy/firmware/rse-rom-image.img` |
| RSE flash | `build/local-apollo-fvp/deploy/firmware/rse-flash-image.img` |
| RSE OTP | `build/local-apollo-fvp/deploy/firmware/rse-otp-image.img` |
| AP flash | `build/local-apollo-fvp/deploy/firmware/ap-flash-image.img` |
| Provisioning bundle | `build/local-apollo-fvp/deploy/firmware/combined_provisioning_message.bin` |
| Root disk | `build/local-apollo-fvp/deploy/boot/apollo-fvp-local-disk.img` |
| AP DTB evidence | `build/local-apollo-fvp/deploy/boot/apollo-fvp.dtb` |
| RSE symbols | `build/local-apollo-fvp/debug/symbols.json` |
| SI CL0 image | `build/local-apollo-fvp/deploy/firmware/si0_ramfw.bin` |
| SI CL1 image | `build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.bin` |
| SI CL1 symbols | `build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.elf` |

The runner should accept explicit command-line overrides for every artifact so
local-build, Yocto deploy, archived FVP evidence, and experimental images can
be compared without editing Lua.

## Entry Points

Keep the existing fast direct-boot path unchanged:

```text
scripts/run/run_qbox_apollo_fvp_linux.py
./local-build.sh qbox
tools/qbox-platform/platforms/apollo/apollo-pc.lua
```

Add a separate full-system path:

```text
scripts/run/run_qbox_apollo_fvp_full.py
./local-build.sh qbox
scripts/test/validate_qbox_apollo_fvp_full_map.py
scripts/test/audit_qbox_apollo_fvp_full_coverage.py
scripts/test/verify_qbox_apollo_fvp_full_completion.py
tools/qbox-platform/platforms/apollo/apollo-qvp.lua
tools/qbox-platform/platforms/apollo/hw-block/rse.lua
tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua
tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua
tools/qbox-platform/platforms/apollo/hw-block/ros.lua
tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua
build/qbox-apollo-fvp/full-<run-id>/
```

The split is important because direct boot starts AP Linux through an AArch64
stub with EL3/EL2 disabled, while full-system boot starts from RSE and releases
AP CPU0 into AP BL2 with EL3/EL2 enabled.

## Memory, Interrupt, And ATU Design

The full-system target must model Zena CSS as multiple views of one system:
AP, RSE, SMD, Safety Island CL0, and Safety Island CL1. The programmer model
and local code show that these views are connected through ATUs rather than
simple static aliases.

Implementation rules:

- Keep a normalized memory and interrupt ledger for AP, RSE, SMD, SI CL0, and
  SI CL1. The ledger must cite the source file or generated artifact for every
  address range and interrupt.
- Keep AP GIC, RSE NVIC, SI CL0 GIC view, and SI CL1 GIC view interrupt
  numbers separate. The SI CL1 Zephyr DTS and the SI CL0 SCP-firmware IRQ
  header use different local views, so the validator must not collapse them
  into one global SPI namespace.
- Treat ATU and ATW behavior as boot-critical. RSE owns ATU configuration, and
  Safety Island CL0 uses ATW windows to reach AP GIC, AP shared SRAM, SMD
  timers, SYSTOP PIK, SMCF, SMD SRAM, and NI-710AE FMU regions.
- Default-closed ATU or access-protection behavior should fail visibly. Silent
  pass-through aliases are acceptable only as explicitly reported service-model
  debt.
- Record ATU translation hits, misses, seeded windows, and firmware-programmed
  windows in the full-system run output.

Minimum map coverage before live CL0/CL1 integration:

| View | Required coverage |
| --- | --- |
| AP | Shared SRAM, AP flash, DRAM, AP GIC/ITS, timers, UARTs, watchdogs, SMMU, AP-SI SCMI/HIPC MHUs, virtio, RTC, RAS/PMU interrupts, AP-to-SMD ATU window. |
| RSE | ROM, ITCM/DTCM aliases, VM0/VM1, boot flash, OTP/LCM, KMU, SAM, CC3XX, DMA350, MPC, RSE ATU, RSE MHU0/MHU2, RSE host UART, NVIC IRQs. |
| SMD | SMD SRAM, CSS control, SMDExp-to-SMD ATU, AP-to-SMD ATU, SMD timers/counters, SYSTOP/DBGTOP PPU, SMD UART/GPIO/SID, FMU, SMCF SRAM. |
| SI CL0 | CL0 SRAM, GIC view0, UART, timers/watchdogs, SSU, FMU0..4, MHU frames, CL1-to-CL0 MHU, AP/RSE MHU receivers, PIK/SCR, ATW IO/memory windows. |
| SI CL1 | Four Cortex-R82 CPUs, CL1 SRAM, CL1 GIC view, UART, timer PPIs, AP-SI HIPC MHU TX/RX, PFDI agent MHU, SCMI/PFDI shared memory. |

Hardware block coverage should be tracked as `live`, `service-modeled`,
`register-stub`, or `absent`. GIC multi-view routing, MHUv3, ATU, PFDI monitor,
FMU, SSU, SMCF, PPU/SCR, RGM, and RAS are not optional for equivalence, even if
some can initially remain service-modeled.

## Safety Island GIC Multiview Design

Use a hybrid model for the Safety Island GIC:

- A new SystemC/TLM `gicx00_multiview` controller models the firmware-visible
  GIC-720AE multiview control surface.
- Existing QEMU GICv3 backends keep standard distributor, redistributor, CPU
  interface, PPI, SPI, IRQ, and FIQ behavior.

This is preferred over a full SystemC GIC implementation for the first
full-system boot milestone. It also avoids carrying QEMU GIC patches until a
runtime failure proves that the hybrid model is insufficient.

Source evidence:

- `arm-zena-css/documentation/design/components.rst:110` describes the Safety
  Island GIC as a GIC-720AE with three programming views.
- `arm-zena-css/documentation/design/components.rst:113` assigns view-0 to SI
  CL0 SCP firmware boot-time configuration.
- `arm-zena-css/documentation/design/components.rst:116` assigns view-1 to the
  SI CL0 OS view.
- `arm-zena-css/documentation/design/components.rst:119` assigns view-2 to the
  SI CL1 OS view.
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:86`
  enables FVP `has_multiview_gic`.
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_gicx00_multiview.c`
  maps CL0 redistributor and CL0 SPIs to view-1, and CL1 redistributors and
  CL1 SPIs to view-2.
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/module/gicx00_multiview/include/internal/gicx00_multiview_reg.h`
  defines the firmware-visible `GICD_CFGID`, `GICD_IVIEWR`, `GICR_PWRR`, and
  `GICR_VIEWR` offsets.

Architecture:

```text
                       view-0 MMIO
                 0x3000_0000 distributor
                 0x3004_0000 redistributor 0
                 0x3006_0000 redistributor 1
                 0x3008_0000 redistributor 2
                 0x300a_0000 redistributor 3
                 0x300c_0000 redistributor 4
                              |
                              v
                  +------------------------+
external IRQ ---> | SystemC gicx00         | ---> view1 SPI ---> QEMU GICv3
sources           | multiview controller   |      CL0 backend     view-1 MMIO
                  |                        |      0x3010_0000
                  | - CFGID view bit       |      0x3014_0000
                  | - GICD_IVIEWR table    |
                  | - GICR_VIEWR table     |
                  | - SPI view routing     | ---> view2 SPI ---> QEMU GICv3
                  +------------------------+      CL1 backend     view-2 MMIO
                                                      0x3020_0000
                                                      0x3026_0000+
```

Use one QEMU GICv3 backend per live Safety Island OS view:

- `si_cl0_gic`: one Cortex-R82 CPU, view-1 distributor and redistributor
  window.
- `si_cl1_gic`: four Cortex-R82 CPUs, view-2 distributor and redistributor
  windows.

Do not attach both views to a single QEMU GICv3 device. QEMU's GIC CPU
interface state is tied to a concrete CPU/GIC device relationship, while Zena
CSS exposes one physical GIC through multiple programming views. The hybrid
model represents the visible views with separate QEMU backends and uses the
SystemC controller to apply the SCP-firmware configured routing.

The SystemC controller should expose these sockets:

```cpp
tlm_utils::simple_target_socket<gicx00_multiview> view0_dist;
sc_core::sc_vector<tlm_utils::simple_target_socket<gicx00_multiview>>
    view0_redist;
sc_core::sc_vector<TargetSignalSocket<bool>> spi_in;
sc_core::sc_vector<InitiatorSignalSocket<bool>> view1_spi_out;
sc_core::sc_vector<InitiatorSignalSocket<bool>> view2_spi_out;
```

Required register behavior is intentionally narrow and boot-focused:

| Region | Offset | Register | Required behavior |
| --- | ---: | --- | --- |
| GICD view-0 | `0x0000` | `GICD_CTLR` | Store/read 32-bit value. |
| GICD view-0 | `0xf000` | `GICD_CFGID` | Return `GICD_CFGID_VIEW` in bit 53 for 64-bit reads. |
| GICD view-0 | `0xf600 + 4 * n` | `GICD_IVIEWR(n)` | Store two-bit view per SPI interrupt. |
| GICR view-0 | `0x0024` | `GICR_PWRR` | Read as powered, accept writes, never trap firmware polling. |
| GICR view-0 | `0x002c` | `GICR_VIEWR` | Store redistributor view assignment. |

Map view-0 control accesses to the SystemC controller:

| Window | Target |
| ---: | --- |
| `0x30000000` | `gicx00_multiview.view0_dist` |
| `0x30040000` | `gicx00_multiview.view0_redist[0]` |
| `0x30060000` | `gicx00_multiview.view0_redist[1]` |
| `0x30080000` | `gicx00_multiview.view0_redist[2]` |
| `0x300a0000` | `gicx00_multiview.view0_redist[3]` |
| `0x300c0000` | `gicx00_multiview.view0_redist[4]` |

Map live OS views directly to QEMU GICv3 backends:

| Window | Target |
| ---: | --- |
| `0x30100000` | `si_cl0_gic.dist_iface` |
| `0x30140000` | `si_cl0_gic.redist_iface` |
| `0x30200000` | `si_cl1_gic.dist_iface` |
| `0x30260000` | `si_cl1_gic.redist_iface` region 0 |
| `0x30280000` | `si_cl1_gic.redist_iface` region 1 |
| `0x302a0000` | `si_cl1_gic.redist_iface` region 2 |
| `0x302c0000` | `si_cl1_gic.redist_iface` region 3 |

Route shared SI SPI sources through `gicx00_multiview.spi_in`. The controller
then drives exactly one of `view1_spi_out` or `view2_spi_out` according to the
firmware-programmed `GICD_IVIEWR` table. CPU-private timer PPIs stay directly
connected to each QEMU GICv3 backend because PPIs are not routed through
`GICD_IVIEWR`.

Track these fidelity gaps until runtime evidence says they matter or can be
closed:

- View-1 and view-2 are represented as separate QEMU GICv3 devices rather than
  multiple views over one shared physical GIC state.
- Shared pending/active state across views is approximated by SystemC SPI
  routing and per-view QEMU state.
- SGI cross-view behavior is not modeled by the first implementation.
- LPI/vLPI behavior remains whatever the existing QEMU GICv3 backend supports.
- Internal GIC-720AE safety and RAS error signaling is not modeled.

## Apollo AP GIC-720AE Boot-Visible Parity

The AP GIC/ITS path keeps QEMU responsible for the architected CPU interface,
distributor, redistributor, ITS, PPI, SPI, LPI, and vLPI-facing behavior. The
Apollo platform enables opt-in QEMU properties for the FVP-observed GICv4.1
feature reporting only on the AP GIC and AP ITS:

- `has_gicv4_1`, `has_direct_lpi`, `has_rvpeid`,
  `has_vpend_valid_dirty`, and `vpeid_bits` on `arm_gicv3`.
- `has_gicv4_1`, `gicv4_1_svpet`, and `gicv4_1_cte_size` on
  `arm_gicv3_its`.

`scripts/test/compare_qbox_fvp_gic_logs.py` is the GIC parity gate. Its
`--expect-fvp-parity` mode compares the current QBox primary-console log with
the Apollo FVP primary-console log and writes `gic-parity.json`. The required
boot-visible AP markers are:

| Marker | Required QBox evidence |
| --- | --- |
| SPI count | `GICv3: 960 SPIs implemented` |
| GICv3 DirectLPI | `GICv3 features: 16 PPIs, DirectLPI` |
| GICv4.1 DirectLPI/RVPEID | `GICv4 features: DirectLPI RVPEID Valid+Dirty` |
| ITS mode | `Using GICv4.1 mode` |
| ITS collections | `32768 Interrupt Collections` |
| VPE invalidation | `Using DirectLPI for VPE invalidation` |

These checks are based on the existing software contract only. QBox must not
change AP `TFA_PLATFORM = "apollo_fvp"`, RSE
`TFM_PLATFORM = "arm/rse/automotive_rd/apollo-fvp"`, SI CL1
`apollo_fvp_safety_island_c1`, Linux, U-Boot, OP-TEE, TF-M/RSE, or
SCP-firmware sources to hide a model gap. The SI multiview control path remains
anchored to SCP-firmware `config_gicx00_multiview.c`.

The AP `RGIC2LGIC_MESSREG` window is no longer a plain `gs_memory` block in the
full-system AP view. It is represented by the named `gic720ae_messreg`
SystemC/TLM sideband model, which preserves deterministic storage,
out-of-bounds errors, access-size checks, and `transport_dbg`. AXI5-Stream
timing, complete SPI Collator semantics, Wake Request, Q/P-channel, and FuSa
injection behavior remain deferred GIC-720AE fidelity work.

## Proposed Topology

```text
QBox top container
  host/SMD router
    AP flash, AP DRAM, shared SRAM, AP ATU
    AP GIC/ITS, timers, UARTs, virtio, SMMU, watchdog, RTC
    AP-RSE, RSE-SI, AP-SI MHUv3 windows
    host SCR, PPU, SYSTOP PIK, SMCF/PFDI support windows

  RSE domain
    RemoteCPU Cortex-M55
    NVIC/SCS, ROM, ITCM, DTCM, VM0/VM1
    Strata boot flash, LCM/OTP, DMA350, CC3XX, KMU, SAM, ATU
    RSE local MHU0/MHU2 and RSE host UART

  Primary Compute domain
    QemuInstance AARCH64
    4 x cpu_arm_cortexA720AE
    EL3 and EL2 enabled
    AP CPU0 reset-held until RSE/SI handoff releases it
    AP reset vector at AP BL2

  Safety Island CL0 domain
    Initial mode: SCMI/PFDI/AP-release service model
    Live mode: QemuInstance AARCH64 + cpu_arm_cortexR82 for SCP-firmware

  Safety Island CL1 domain
    Initial mode: HIPC/RPMsg service model for Linux probes
    Live mode: QemuInstance AARCH64 + cpu_arm_cortexR82 CPUs for Zephyr
```

Use the existing `fvp-rd-aspen-rse` topology as the first source of truth for
RSE and AP wiring. Add Apollo-specific artifact defaults, environment variable
names, and output paths instead of modifying the current direct-boot Lua.

## Safety Island Modes

Use a runtime mode switch so integration can progress without losing the known
service-model baseline:

```text
QBOX_APOLLO_FULL_SI_MODE=service-model|live-cl1|live-cl0-cl1
```

| Mode | Purpose | Expected fidelity |
| --- | --- | --- |
| `service-model` | Reuse existing SCMI, AP release, PFDI monitor, and CL1 RPMsg service behavior. | Functional full-system boot baseline with explicit SI CPU fidelity debt. |
| `live-cl1` | Run Zephyr CL1 on Cortex-R82 while CL0/SCP remains service-modeled. | Validates CL1 UART, GIC/timers, HIPC shared memory, MHU doorbells, RPMsg, and PFDI local service paths. |
| `live-cl0-cl1` | Run SCP-firmware CL0 and Zephyr CL1 on Cortex-R82. | Target FVP-equivalent Safety Island behavior for boot, AP release, SCMI, HIPC, PFDI, and logs. |

`service-model` should remain the default until live CL0 and CL1 reach the same
observable markers as the FVP logs.

## AP Source-View Routing

Live CL0/CL1 mode must preserve the AP source view separately from the
Safety Island CL0 source view. The AP CPUs, AP global peripheral initiator, and
AP GPEX bus master should enter an AP logical router first. Boot-critical AP
targets must be rebound into that AP view instead of relying on a broad
host-router passthrough:

- AP DRAM and AP firmware/runtime shared-memory windows.
- AP GIC distributor, redistributors, ITS, and SMMU.
- AP virtio block, net, and rng windows.
- AP RTC, watchdogs, UARTs, timers, and GPEX windows.

This prevents live SI CL0 GIC/CMN/management windows in the shared host router
from shadowing AP DRAM or AP virtio when AP-originated transactions are
decoded. Static validation must include AP-view router checks for these windows.
Runtime completion must also reject unexpected shadowed ranges. The only
accepted shadow exceptions are the intentional AP-view passthrough and
diagnostic ATU-check windows; all other shadows require a blocker or reviewed
fidelity-gap classification.

## Boot Sequence

1. The runner validates local artifacts and creates per-run writable copies of
   RSE flash, RSE OTP, AP flash, root disk, and shared-memory backing files.
2. QBox maps RSE local memory/peripherals, SMD/host windows, AP flash, AP DRAM,
   AP/SI/RSE MHU windows, Safety Island SRAM, AP root disk, UARTs, GICs, and
   timers.
3. RSE Cortex-M55 starts from `rse-rom-image.img` and runs TF-M BL1_1.
4. TF-M validates BL1_2 and BL2 using CC3XX, DMA350, LCM/OTP, KMU, and RSE
   Strata flash models.
5. RSE BL2 loads SI CL0 and SI CL1 images from RSE flash.
6. In `service-model`, SystemC/TLM service blocks respond to the SCMI and HIPC
   transactions needed for AP release and Linux probes.
7. In live SI modes, Cortex-R82 instances boot SCP-firmware and/or Zephyr and
   own the same MHU/shared-memory interactions.
8. RSE loads AP BL2 into AP flash/boot SRAM and requests AP power on through
   the SI/system-management path.
9. AP CPU0 is released to AP BL2. TF-A loads BL31, OP-TEE, and U-Boot from
   AP flash/FIP.
10. U-Boot boots the local Linux image/rootfs from the AP boot media.
11. The runner logs into Linux and validates remoteproc/RPMsg, PFDI, modules,
   interrupts, and service state.

## Log And Result Contract

Every full-system run should produce:

```text
build/qbox-apollo-fvp/full-<run-id>/result.json
build/qbox-apollo-fvp/full-<run-id>/summary.txt
build/qbox-apollo-fvp/full-<run-id>/qbox-platform.log
build/qbox-apollo-fvp/full-<run-id>/qbox-rse.log
build/qbox-apollo-fvp/full-<run-id>/qbox-safety-island-cl0.log
build/qbox-apollo-fvp/full-<run-id>/qbox-safety-island-cl1.log
build/qbox-apollo-fvp/full-<run-id>/qbox-secure-console.log
build/qbox-apollo-fvp/full-<run-id>/qbox-primary-console.log
```

The final completion check should additionally produce:

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

`result.json` should record:

- Resolved artifact paths and file sizes.
- Safety Island mode.
- QBox command and CCI parameters.
- Completion gate status for G0 through G5 as `pass`, `blocked`, `fail`, or
  `not_run`.
- Marker groups for RSE boot, SI CL0, SI CL1, AP firmware, Linux boot, and
  post-login probes.
- Platform observations, including `ap_cpus == 16` for full live runtime
  evidence. AP CPU count 0 is valid only for RSE-only diagnostics and must not
  satisfy G4/G5.
- Secure-console observations, including `ap_bl2_console == true`,
  `bl31_console == true`, and `optee_console == true`, so AP secure firmware
  execution is distinguished from RSE measured-boot evidence for those images.
- Primary-console observations, including `u_boot_console == true`, so U-Boot
  execution is distinguished from RSE measured-boot evidence for BL_33.
- First failing marker and blocker classification.
- Explicit fidelity gaps when `service-model` is used.
- Normalized memory map, interrupt map, ATU, MHU, and hardware block coverage
  summary or references to sidecar JSON reports.

`final-verification.json` is written by
`scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`. It is the
last gate before claiming completion and should record:

- `goal_definition` and `completion_policy`, so the saved evidence states what
  was being proven and what is not a completion point.
- `completion_claim_allowed: true`; this is the only machine-readable state
  that permits a final report to claim the full-system task is complete.
- `completion_ready: true`.
- `overall_gates.G0..G5 == "pass"`.
- Paths for the check-only, direct-boot, service-model, live-CL1, and
  live-CL0/CL1 evidence directories.
- Per-check pass/fail entries for `result.json`, subsystem logs, marker
  groups, FVP comparison, map comparison, and coverage audit artifacts.

## Validation Ladder

Use narrow checks before full runtime:

```bash
python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .
python3 scripts/run/run_qbox_apollo_fvp_full.py --check-only
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py --check memory,irq,atu
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py --check hardware-blocks
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-build/local-apollo-fvp/work/qbox-platform}"
cmake --build "${QBOX_PLATFORM_BUILD_DIR}" --target cpu_arm_cortexR82 remote_cpu platforms-vp --parallel 8
```

Runtime validation:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode service-model \
  --timeout 900 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-service-model
```

Live SI validation should start isolated, then integrate:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl1 \
  --timeout 600 \
  --out-dir build/qbox-apollo-fvp/full-live-cl1

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 1200 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1
```

FVP comparison remains mandatory before claiming equivalence:

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

python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

## Review Decisions

The following decisions should be reviewed before implementation:

1. Keep `service-model` as the default full-system mode until live SI reaches
   equivalent markers.
2. Model SI CL0 DCLS as one architectural Cortex-R82 CPU first, with DCLS
   safety fidelity tracked separately.
3. Add live CL1 before live CL0 if the goal is AP Linux HIPC/RPMsg evidence
   first; add live CL0 first if the goal is firmware-controlled AP release
   fidelity first.
4. Keep QBox full-system artifact variables Apollo-specific, for example
   `QBOX_APOLLO_FULL_RSE_FLASH`, to avoid collision with RD-Aspen RSE runners.
5. Make ATU a first-class modeled component. Service-model seeded windows are
   acceptable for the first boot milestone only if they are reported as such.
6. Treat MHUv3, GIC multi-view routing, PFDI, FMU, SMCF, PPU, SCR, SSU, and RAS
   details as fidelity debt unless verified against FVP logs and the local Zena
   CSS programmer model.

## Main Risks

- Cortex-R82 source probes pass, but live SCP-firmware and Zephyr execution
  still need isolated runtime proof.
- GIC-720AE behavior may require more than the current GICv3-compatible view
  once live Safety Island firmware handles timers and interrupts.
- ATU, ATW, and access-protection behavior crosses RSE, SMD, AP, and SI. Static
  aliases can make early boot pass while hiding the real firmware path.
- MHUv3 service-model behavior is currently boot-oriented. Full live CPU mode
  must preserve channel, interrupt, shared-memory, and doorbell behavior.
- AP release and reset ordering are cross-domain. Regressions can look like
  RSE, SI, TF-A, or U-Boot failures unless logs are grouped by subsystem.
- Full FVP equivalence includes diagnostics, error injection, PFDI, FMU, SSU,
  SMCF, RAS, power, and reset behavior beyond Linux login.

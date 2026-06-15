# QBox Apollo FVP Map Analysis

Generated: 2026-06-03

Status: review draft

## Scope

This note normalizes the Arm Zena CSS/RD-Aspen address and interrupt evidence
needed for an Apollo full-system QBox target. It is intentionally focused on
implementation review: which memory views, interrupt numbers, ATU windows, and
hardware blocks must be represented before QBox can claim FVP-equivalent boot
behavior.

## Evidence Sources

- Programmer model:
  `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- Zena CSS design notes:
  `arm-zena-css/documentation/design/components.rst`,
  `arm-zena-css/documentation/design/hipc.rst`,
  `arm-zena-css/documentation/design/fmu.rst`,
  `arm-zena-css/documentation/design/ssu.rst`,
  `arm-zena-css/documentation/design/smcf.rst`,
  `arm-zena-css/documentation/design/ras.rst`, and
  `arm-zena-css/documentation/design/platform_fault_detection_interface.rst`
- Current QBox RD-Aspen RSE topology:
  `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- Current QBox Apollo direct-boot AP device tree:
  `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts`
- Current QBox RD-Aspen AP device tree:
  `tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts`
- Apollo-owned Safety Island CL0 firmware map and IRQ definitions:
  `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_mmap.h`,
  `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_irq.h`
- Apollo-owned Safety Island CL1 Zephyr board:
  `hsoc-stack/components/system_mgmt/zephyrproject/safety_island/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts`

## Address-Space Model

Arm Zena CSS is not one flat 32-bit map. The programmer model and design notes
describe a 52-bit system-wide address space, with AP, SMD, RSE, and Safety
Island regions. Domain-local CPUs see smaller local maps. ATUs translate
between those local views and the system-wide view.

The important implementation consequence is that QBox must model views:

- AP view: Linux/TF-A/U-Boot addresses and AP GIC interrupts.
- RSE local view: Cortex-M55 TF-M addresses, NVIC interrupts, RSE ATU data
  windows, and local secure/non-secure aliases.
- SMD/system-wide view: shared SRAM, CSS control, SMD timers, SYSTOP/DBGTOP,
  FMU, SMCF, and ATU control registers.
- Safety Island local view: CL0 SCP-firmware and CL1 Zephyr local addresses,
  SI GIC views, MHU frames, FMU/SSU/SMCF, and SI ATW windows.

## Normalized Memory Map

| Domain | Important ranges | QBox implication |
| --- | --- | --- |
| AP shared SRAM | Programmer model reserves `0x00000000..0x07ffffff`; current QBox RSE topology actively uses a boot/SDS/SCMI subset near `0x00000000`, AP BL2 at `0x00082000`, and BL2 header SRAM at `0x00100000`. | Keep the full reserved range in the map ledger, but validate the modeled subset and all shared-memory offsets used by TF-M, TF-A, SCP-firmware, and Linux. |
| AP peripherals | UART `0x1a400000`, secure UART `0x1a410000`, watchdog `0x1a420000/0x1a430000`, secure watchdog `0x1a460000/0x1a470000`, system timers `0x1a810000..0x1a830000`, SID `0x1a4a0000`, FMU AP region `0x1d000000..0x1defffff`. | Full-system AP boot must use the FVP/RD-Aspen device tree map, not only the smaller direct-boot Apollo DTS. |
| AP interrupt controller | AP GIC at `0x20800000`, redist at `0x20880000`, legacy aliases at `0x20000000` and `0x200c0000`; ITS is present in the direct DTS at `0x20840000`. | QBox needs active redistributor regions for `PC_CPUS_COUNT_DEFAULT=4` and must preserve aliases used by firmware. |
| AP DRAM | Low DRAM starts at `0x80000000`; AP 9.1.1 high DRAM starts at `0x08_8000_0000` / `0x880000000`. | QBox direct AP and full-system paths now use `0x880000000` for high DRAM with the current 2 GiB backing; keep placement artifact-validated instead of hard-coding from one Lua file. |
| AP SMD access window | Programmer model exposes an AP window at `0x40000000..0x4fffffff`; current QBox RSE topology has an AP logical ATU window at `0x40000000` and a host AP ATU register block at system address `0x20000d0080000`. | This must be an ATU-backed translation, not a static memory alias. |
| RSE local memory | ROM `0x11000000`, ITCM/DTCM aliases around `0x00000000/0x10000000/0x20000000/0x30000000`, VM0/VM1, boot flash at `0xb0000000`. | Boot from TF-M BL1_1 and preserve secure/non-secure alias behavior. |
| RSE secure peripherals | RSE ATU `0x50150000`, MHU0 `0x50160000/0x50170000`, MHU2 `0x501a0000/0x501b0000`, CC3XX, DMA350, KMU, SAM, LCM, MPC, OTP wrapper, system control, and integration layer. | TF-M secure boot needs enough behavior for image authentication, flash/OTP access, MHU signaling, and ATU programming. |
| RSE ATU data windows | Non-secure data window `0x60000000..0x6fffffff`; secure data window `0x70000000..0x7fffffff`. | Route translated accesses into SMD/AP/SI targets and log unmapped translations. |
| SMD system-wide map | SMD SRAM near `0x02_0000_6000_0000`; CSS control near `0x02_0000_d000_0000`; SMDExp-to-SMD ATU `0x02_0000_d007_0000`; AP-to-SMD ATU `0x02_0000_d008_0000`; timers, counters, SYSTOP/DBGTOP PPU, SMD UART/GPIO/SID, FMU, SMCF SRAM. | Add a first-class SMD router/address decoder in the full-system platform. Static stubs are acceptable only when the firmware-visible register behavior is not exercised. |
| Safety Island CL0 | SRAM at `0x120000000`; GIC view0 around `0x30000000`; UART `0x2a400000`; SSU `0x2a500000`; FMU0..4 `0x2a510000..0x2a550000`; timers `0x2a6f0000/0x2a720000`; MHU window `0x38000000`; RSE shared SRAM `0x40000000`; shared bank1 `0x48000000`. | Live CL0 SCP-firmware needs the CL0 local view and its SI ATW windows before it can own AP release, SCMI, PFDI monitor, FMU, and SSU flows. |
| Safety Island CL1 | Zephyr sees CL1 SRAM at `0x140000000`, GIC at `0x30200000`, UART `0x2a410000`, PFDI MHU TX at `0x39200000`, HIPC MHU TX/RX at `0x39000000/0x39040000`, and SCMI/PFDI shared memory at `0x48000000`. | Live CL1 needs a separate GIC view and four Cortex-R82 CPUs for the Zephyr SMP path. |
| Safety Island ATW | SCP-firmware defines ATW IO at `0x80000000`, ATW memory at `0xe0000000`, and windows for CMN, cluster utility, SMD expansion, SYSTOP PIK, SID, CSS timers, NI-710AE FMUs, AP GIC, AP shared SRAM, SMCF, and SMD SRAM. | Model SI ATU/ATW programming and target routing; this is required for CL0 to inspect AP/SMD state and manage platform services. |

## AP 9.1.1 Coverage Status

After T6-T10, Apollo QBox has explicit AP 9.1.1 coverage for the selected P1
map gaps, but this is not full FVP-equivalent AP memory-map parity.

| AP 9.1.1 row | Current QBox coverage | Status |
| --- | --- | --- |
| High DRAM | Direct `ram_1`, full-system `host_ap_dram2`, and direct DTS high-memory cells are migrated to `0x08_8000_0000` / `0x880000000` with 2 GiB backing. | `partial`, because the programmer-model high DRAM row is larger than the current QBox backing. |
| AP SID | `ap_sid` uses `host_scr` at `0x1a4a0000..0x1a4affff` and is bound into the AP logical view. | `covered` for the SID register profile exposed by `host_scr`. |
| AP secure watchdog control/refresh | `ap_secure_wdog` and `ap_secure_wdog_refresh` are separate 64 KiB `gs_memory` windows at `0x1a460000..0x1a46ffff` and `0x1a470000..0x1a47ffff`, both bound into the AP logical view. | `explicit_placeholder`; decode is preserved, but watchdog side effects, interrupt/reset behavior, and access-control fidelity remain deferred. |
| AP secure timer frame | `ap_secure_timer_frame` is a narrow `gs_memory` window at `0x1a820000..0x1a82ffff`. | `explicit_placeholder`; it does not implement full secure generic timer side effects or interrupt behavior. |
| RGIC2LGIC_MESSREG | `ap_rgic2lgic_messreg` is a 64 KiB `gs_memory` window at `0x5fff0000..0x5fffffff`. | `explicit_placeholder`; remote/local GIC message-register semantics remain deferred. |
| APP subsystem FMU | `ap_cl0_ni710ae_fmu..ap_cl3_ni710ae_fmu` use `zena_fmu` for firmware-derived NI-710AE cluster FMU subwindows under `0x1d000000..0x1defffff`. | `partial_model`; unimplemented aggregate/reserved space is not claimed as a full model. |

Deferred parity epics remain for System NoC GPV, CMN GPV, PCIe memory and
PCIe CTRL/PHY, debug memory map, memory-controller control, AP Memory
Expansion, STM, and cluster-management ranges. Do not report these placeholders
or gaps as FVP-equivalent full models.

## Normalized Interrupt Map

The interrupt map has multiple views. QBox should keep AP GIC SPI/PPI numbers,
RSE NVIC IRQ numbers, SI CL0 GIC view numbers, and SI CL1 Zephyr view numbers
separate, then generate a normalized report.

| Domain | Interrupts that must be represented |
| --- | --- |
| AP | Generic timer PPIs 13/14/11/10, GIC maintenance PPI 9, DSU PMU SPI 216, UART SPI 52, watchdog SPI 50, system timer SPI 49, RAS FFH SPI 57, SMMU SPI 65, AP-SI SCMI MHU SPIs 112/113, AP-SI HIPC MHU SPIs 120/121, virtio SPIs 257/258/259/260/261/263, RTC SPI 268. |
| RSE | MHU0 receiver NVIC IRQ 41, MHU2 receiver NVIC IRQ 45, SI CL0 to RSE receiver NVIC IRQ 139, plus SCS/NVIC architectural interrupt behavior. |
| SI CL0 SCP-firmware | System timer 34, watchdog 37, UART 40, AP2SI0 NS MHU 97, AP2SI0 domain1 secure MHU 99, AP2SI0 domain3/PFDI monitor MHU 103, RSE2SI0 MHU 105, CL1-to-CL0 MHU 107, FMU critical/non-critical 128/129, SMCF SMD MGI 288/289, AP error cluster SPIs 325/327/329/331, AP MGI SPIs 359..366. |
| SI CL1 Zephyr local DTS | Timer PPIs 13/4/11/3, UART SPI 7, PFDI agent MHU SPI 50, HIPC MHU TX/RX SPIs 40/41. |
| SI CL1 SCP header names | The CL0 firmware IRQ header names CL1 timer 33, watchdog 36, UART 39, CL1-PC MHU 72/73, and CL1-CL0 MHU 82. |

The two SI CL1 views above are not contradictory by themselves. They show that
the full-system design must understand SI GIC multi-view routing instead of
assuming one global SPI namespace for both CL0 SCP-firmware and CL1 Zephyr.

## ATU Requirements

ATU must be a first-class QBox feature for this platform.

- Ownership: the Zena CSS design notes state that ATU configuration is owned by
  RSE. QBox should allow TF-M/SCP-firmware writes to configure translations,
  while service-model mode may seed the minimum FVP-equivalent configuration.
- Views: RSE, SMD, and Safety Island have separate ATU/ATW register blocks and
  data windows. AP also has an AP-to-SMD window.
- Policy: default-closed or unmapped windows should fail visibly. Silent
  pass-through aliases hide boot bugs.
- Traceability: retain `QBOX_RDASPEN_ATU_TRACE` style controls for Apollo full
  mode and record translation hits/misses in `result.json` or a sidecar log.
- DMI: keep direct-memory-interface acceleration optional and disabled for
  bring-up until the translation model is proven.

## Hardware Block Coverage

| Block group | Required behavior for full-system boot | Fidelity gap if missing |
| --- | --- | --- |
| GIC-720AE and GICv3 views | AP redistributors, SI CL0 view, SI CL1 view, timer PPIs, MHU SPIs, FMU/SMCF/RAS SPIs. | Live SI firmware can boot with wrong interrupts or fail after early UART output. |
| MHUv3 | AP-RSE, RSE-SI, AP-SI SCMI, AP-SI HIPC, CL1-CL0 PFDI monitor channels, doorbell flags, interrupt completion. | SCMI, HIPC/RPMsg, AP release, PFDI monitor, and RSE handoff fail or only work through service shims. |
| ATU/APU/address routers | RSE secure/non-secure data windows, AP-to-SMD, SMDExp-to-SMD, SI ATW IO/memory windows, access control failures. | CL0 cannot manage AP/SMD state and TF-M/SCP-firmware code paths see unrealistic memory behavior. |
| Boot security blocks | RSE flash, OTP/LCM, KMU, SAM, CC3XX, DMA350, MPC, RSE system control. | TF-M secure boot only works through unrealistic bypasses. |
| Timers, watchdogs, UARTs | AP, RSE, SI CL0, and SI CL1 console/timer/watchdog behavior. | Logs and firmware scheduling become unreliable; timeout analysis is ambiguous. |
| Power/reset/control | RGM, PPU, SCR, SYSTOP/DBGTOP PIK, AP reset release, cluster utility windows. | Full-system boot degenerates into manual AP release rather than FVP-equivalent management. |
| Safety/diagnostics | FMU, SSU, SMCF, SBISTC, RAS FFH/ERI paths, PFDI AP and SI flows. | Linux login may pass while safety firmware and diagnostics are not FVP-equivalent. |
| AP platform I/O | SMMU, ITS, virtio block/net/rng, RTC, root disk, AP UART. | Linux probes differ from FVP or existing direct boot. |

## Design Updates Required

1. Add a generated or maintained normalized map ledger for AP, RSE, SMD, SI
   CL0, and SI CL1. A future implementation can use JSON or Python data, but
   it must preserve source evidence for each entry.
2. Extend `scripts/test/validate_qbox_apollo_fvp_full_map.py` to check memory,
   interrupt, ATU, and hardware block coverage across Lua, DTS, SCP headers,
   Zephyr DTS, and FVP evidence.
3. Record the active map/IRQ/ATU coverage in every full-system `result.json`.
4. Treat ATU, GIC multi-view routing, MHUv3 doorbells, and PFDI monitor
   channels as boot-critical, not optional polish.
5. Keep service-model mode honest by reporting exactly which blocks are
   service-modeled, stubbed, or live SystemC/QEMU-backed models.

## Open Review Questions

- Should the first implementation seed ATU windows from the FVP evidence in
  service-model mode, then transition to firmware-programmed windows as live CL0
  and RSE mature?
- Should the SI CL0 DCLS pair remain one architectural Cortex-R82 CPU until
  interrupt and MHU fidelity is proven, or should DCLS lock-step behavior be
  represented earlier?
- Should the map validator be source-of-truth for Lua generation, or only an
  audit gate after hand-written Lua changes?

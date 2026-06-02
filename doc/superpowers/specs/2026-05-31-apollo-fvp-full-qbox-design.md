# Apollo FVP Full QBox Design

## Purpose

Design a QBox configuration that grows the current Apollo primary-compute
direct-boot platform into a full Apollo FVP, matching the active Aspen CSS
hardware shape closely enough to boot the RSE firmware chain, release the
primary compute domain, and validate Safety Island-visible services.

The design keeps the existing direct Linux boot path as a fast primary-compute
test target. Full-firmware validation is a separate platform entrypoint because
it needs different CPU reset behavior, RSE-local memory maps, mailbox routing,
and file-backed logs for several subsystems.

## Evidence Inputs

- Current direct Apollo primary-compute QBox platform:
  `tools/qbox/platforms/apollo-fvp/conf.lua`
- Existing RSE-oriented RD-Aspen QBox platform:
  `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- Existing RSE runner and marker parser:
  `scripts/run_qbox_fvp_rd_aspen_rse.py`
- Local Apollo artifacts:
  `build/local-apollo-fvp/deploy/`
- Yocto Apollo machine and component overrides:
  `hsoc-stack/yocto/meta-hsoc-apollo-bsp/conf/machine/apollo-fvp.conf`
  and Apollo-specific recipe includes under
  `hsoc-stack/yocto/meta-hsoc-apollo-bsp/recipes-*`
- Hardware and boot-flow notes:
  `doc/arm-zena-css-hardware-blocks.md`
  and `doc/arm_zena_css_dev_guide/`

## Current State

`tools/qbox/platforms/apollo-fvp/conf.lua` is a direct-boot primary-compute
platform. It loads a Linux `Image`, DTB, optional initramfs, and an AArch64 boot
stub into AP DRAM, then starts Cortex-A720AE CPUs with EL3 and EL2 disabled.
That is useful for Linux driver iteration, but it intentionally bypasses RSE,
TF-A, OP-TEE, U-Boot, and firmware-controlled AP release.

`tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` already models the pieces that
the full Apollo platform needs:

- RSE Cortex-M55 remote CPU, NVIC, ROM, TCMs, VM windows, flash, OTP, DMA350,
  CC3XX, KMU, LCM, SAM, ATU, system-control, timers, and MHU routing.
- AP flash, AP BL2 reset address, AP ATU, AP GIC, AP UART, AP DRAM, AP CPUs
  with EL3 and EL2 enabled, and reset release driven by modeled firmware
  handoff.
- RSE-to-SI and AP-to-SI MHUv3 paths, AP-SI HIPC/RPMsg service-model support,
  PFDI monitor plumbing, host PPU, SCR, SYSTOP PIK, timers, and SMCF SRAM.
- File-backed logs for RSE, SCP/service model, secure console, primary console,
  and platform logs.

The Apollo local build currently produces the firmware inputs needed by the
RSE-oriented path:

```text
build/local-apollo-fvp/deploy/firmware/rse-rom-image.img
build/local-apollo-fvp/deploy/firmware/rse-flash-image.img
build/local-apollo-fvp/deploy/firmware/rse-otp-image.img
build/local-apollo-fvp/deploy/firmware/ap-flash-image.img
build/local-apollo-fvp/deploy/firmware/combined_provisioning_message.bin
build/local-apollo-fvp/deploy/boot/apollo-fvp-local-disk.img
```

The local build deploy directory does not currently expose the AP BL2 ELF under
the same name used by the existing RD-Aspen RSE QBox path. The Yocto deploy
tree has `build/tmp_baremetal/deploy/images/apollo-fvp/bl2-apollo_fvp.elf`.
The full Apollo runner must either locate that fallback or the local build must
deploy the ELF as `build/local-apollo-fvp/deploy/firmware/bl2-apollo_fvp.elf`.

## Design Options

| Option | Description | Result |
| --- | --- | --- |
| Apollo full platform derived from `fvp-rd-aspen-rse` | Create an Apollo-namespaced full-firmware QBox platform from the existing RSE-oriented RD-Aspen platform, with Apollo artifact resolution and run scripts. | Recommended. It reuses the only QBox path that already models RSE boot, AP reset release, AP firmware execution, and SI service-model protocols. |
| Extend current `apollo-fvp/conf.lua` in place | Add RSE, SI, TF-A, and reset-release logic to the direct-boot platform. | Rejected for first implementation. The direct platform starts AP Linux through a boot stub with EL3/EL2 disabled, so converting it in place would mix two incompatible boot contracts. |
| Implement live Safety Island CPU domains first | Add real SI CL0/CL1 execution before integrating the full RSE/AP platform. | Deferred. Apollo/RD-Aspen SI firmware targets Cortex-R82-class CPUs, while the current QBox/QEMU CPU inventory does not provide a Cortex-R82 model. |

## Recommended Architecture

Create a new full-firmware Apollo QBox platform and runner:

```text
scripts/run_qbox_apollo_fvp_full.py
scripts/build_qbox_apollo_fvp_full.sh
tools/qbox/platforms/apollo-fvp/full.lua
build/qbox-apollo-fvp/full-<run-id>/
```

Keep the existing direct-boot path unchanged:

```text
scripts/run_qbox_apollo_fvp_linux.py
scripts/build_qbox_apollo_fvp_linux.sh
tools/qbox/platforms/apollo-fvp/conf.lua
```

The two entrypoints serve different validation targets:

- `apollo-fvp/conf.lua`: primary-compute Linux bring-up without firmware-chain
  fidelity.
- `apollo-fvp/full.lua`: RSE-first boot, AP BL2 release, TF-A, OP-TEE, U-Boot,
  Linux, and SI service checks.

## Full Platform Topology

```text
RSE domain
  RemoteCPU Cortex-M55
  NVIC/SCS
  ROM, ITCM, DTCM, VM0, VM1
  boot flash, OTP/LCM, DMA350, CC3XX, KMU, SAM, ATU
  RSE MHU endpoints

Host/SMD domain
  AP flash and AP BL2 reset window
  AP DRAM and shared SRAM
  AP ATU, GIC, UART, timers, virtio, root disk
  SYSTOP, PIK, SCR, PPU, SMCF SRAM
  SI CL0 service model for SCMI, PFDI, and AP release
  SI CL1 HIPC/RPMsg service model for Linux post-login probes

Primary compute domain
  Cortex-A720AE CPUs
  EL3 and EL2 enabled
  start in reset
  reset vector at AP BL2 physical base

Log outputs
  qbox-platform.log
  qbox-rse.log
  qbox-scp.log
  qbox-secure-console.log
  qbox-primary-console.log
  result.json
```

## Artifact Contract

Use an Apollo-specific environment prefix for the full platform so it cannot
conflict with the direct-boot variables:

| Environment variable | Default source |
| --- | --- |
| `QBOX_APOLLO_FULL_RSE_ROM` | `build/local-apollo-fvp/deploy/firmware/rse-rom-image.img` |
| `QBOX_APOLLO_FULL_RSE_FLASH` | `build/local-apollo-fvp/deploy/firmware/rse-flash-image.img` |
| `QBOX_APOLLO_FULL_RSE_OTP` | `build/local-apollo-fvp/deploy/firmware/rse-otp-image.img` |
| `QBOX_APOLLO_FULL_AP_FLASH` | `build/local-apollo-fvp/deploy/firmware/ap-flash-image.img` |
| `QBOX_APOLLO_FULL_AP_BL2_ELF` | local deploy ELF if present, otherwise Yocto deploy fallback |
| `QBOX_APOLLO_FULL_ROOTFS` | `build/local-apollo-fvp/deploy/boot/apollo-fvp-local-disk.img` |
| `QBOX_APOLLO_FULL_PROVISIONING` | `build/local-apollo-fvp/deploy/firmware/combined_provisioning_message.bin` |
| `QBOX_APOLLO_FULL_ENABLE_AP_CPUS` | controlled by the runner |
| `QBOX_APOLLO_FULL_PLATFORM_LOG` | per-run output directory |
| `QBOX_APOLLO_FULL_RSE_LOG` | per-run output directory |
| `QBOX_APOLLO_FULL_SCP_LOG` | per-run output directory |
| `QBOX_APOLLO_FULL_SECURE_CONSOLE_LOG` | per-run output directory |
| `QBOX_APOLLO_FULL_PRIMARY_CONSOLE_LOG` | per-run output directory |

The runner should also accept explicit command-line overrides for every
artifact. This is required for comparing local-build artifacts, Yocto deploy
artifacts, and archived FVP/QBox evidence.

## Safety Island Strategy

### Stage 1: Protocol-correct service model

Use the existing RD-Aspen RSE QBox Safety Island service-model blocks as the
first Apollo integration step. This keeps AP/RSE firmware boot behavior
exercised while avoiding a premature dependency on a Cortex-R82 model.

Stage 1 must cover:

- RSE-SI CL0 SCMI MHU traffic needed by the RSE boot flow.
- SI-mediated AP power/reset release.
- AP-SI SCMI communication required by Linux.
- SI CL1 HIPC/RPMsg service markers required by Linux post-login probes.
- PFDI monitor MHU traffic where the existing model already supports it.

The result is a functional full-platform boot target with explicit fidelity
debt: SI CL0 and SI CL1 firmware are represented by SystemC/TLM service models,
not live R-profile CPUs.

### Stage 2: Live SI CL1 Zephyr execution

Add live SI CL1 execution only after choosing a CPU model strategy. The current
source evidence shows SI CL1 firmware is built for the RD-Aspen/Apollo Safety
Island board, and the DTS describes CL1 CPUs, GIC, PL011, SRAM, MHUv3, SCMI
shared memory, and PFDI. The missing piece is a Cortex-R82-compatible execution
model in the current QBox/QEMU tree.

Two implementation choices are valid:

- Add or import a Cortex-R82-compatible QEMU model.
- Use a clearly documented R-profile approximation for bring-up only, if the
  instruction set and exception model are sufficient for the selected firmware.

The first choice is higher fidelity. The second choice may be useful for early
interface validation but cannot be labeled FVP-equivalent.

### Stage 3: Live SI CL0 SCP-Firmware execution

Move SI CL0 from service model to live SCP-Firmware after Stage 2 proves the CPU
and interrupt model can run Safety Island firmware. This stage must preserve the
same MHU/SCMI/RPMsg/PFDI observable behavior already validated in Stage 1.

## Boot Sequence

1. QBox maps RSE ROM, RSE flash, RSE OTP, AP flash, AP BL2 ELF symbols, rootfs,
   AP DRAM, shared SRAM, AP/SI/RSE MHU windows, ATUs, GIC, UARTs, and timers.
2. RSE Cortex-M55 starts from ROM and runs TF-M BL1_1.
3. RSE validates and loads BL1_2, then BL2, using CC3XX, DMA350, LCM/OTP, KMU,
   boot flash, and protected storage paths already modeled by the RD-Aspen RSE
   platform.
4. RSE BL2 loads SI CL0 payloads into modeled SI memory and uses the SI service
   model for SCMI and AP release handoff.
5. RSE loads AP BL2 and RSE runtime images.
6. The service model releases AP CPU0 from reset at the AP BL2 physical base.
7. AP BL2 loads BL31, OP-TEE, and U-Boot from AP flash.
8. U-Boot boots Linux from the rootfs/boot artifacts selected by the runner.
9. Linux post-login probes validate AP-SI remoteproc/RPMsg/PFDI-visible
   behavior.

## Validation Markers

The Apollo full runner should inherit the marker grouping style from
`scripts/run_qbox_fvp_rd_aspen_rse.py`:

- `rse_boot`: BL1_1, BL1_2, BL2, secure provisioning, TF-M runtime markers.
- `rse_scp_handoff`: SI CL0 load, RSE-SCP SCMI init, AP BL2 load, AP reset
  release.
- `measured_boot`: AP BL2, BL31, OP-TEE, U-Boot measured boot markers.
- `linux_boot`: kernel boot, systemd/login prompt, root shell readiness.
- `post_login`: module load state, remoteproc/RPMsg state, PFDI-visible state,
  and service-specific probes.

Each run must write:

```text
build/qbox-apollo-fvp/full-<run-id>/result.json
build/qbox-apollo-fvp/full-<run-id>/summary.txt
build/qbox-apollo-fvp/full-<run-id>/qbox-platform.log
build/qbox-apollo-fvp/full-<run-id>/qbox-rse.log
build/qbox-apollo-fvp/full-<run-id>/qbox-scp.log
build/qbox-apollo-fvp/full-<run-id>/qbox-secure-console.log
build/qbox-apollo-fvp/full-<run-id>/qbox-primary-console.log
```

## Acceptance Criteria

Stage 1 is complete when:

- `scripts/run_qbox_apollo_fvp_full.py --check-only` verifies every required
  artifact and writes the resolved artifact contract to `result.json`.
- QBox builds all full-platform target dependencies without missing components.
- A bounded RSE-first run reaches RSE boot, RSE-SCP handoff, measured boot,
  AP Linux login, and post-login service probes using Apollo artifacts.
- The final report states the Safety Island service-model fidelity gap and the
  Cortex-R82 live-CPU dependency.
- Direct Linux boot through `scripts/run_qbox_apollo_fvp_linux.py` remains
  available and unchanged.

Stage 2 and Stage 3 are complete only when live SI CL1 and SI CL0 firmware
execution replaces the service model while preserving the Stage 1 observable
protocol behavior.

## Risks And Decisions

- Cortex-R82 support is the main fidelity risk for live Safety Island CPUs.
  The current QBox/QEMU CPU inventory has R5/R52 and M-profile/A-profile models,
  but no R82 model.
- The AP BL2 ELF deployment gap must be closed before the runner can be fully
  local-build-only.
- The initial implementation should avoid refactoring the RD-Aspen RSE platform
  into shared libraries until the Apollo full path boots. Copying the working
  topology first keeps the behavioral delta small.
- Map validation must cover AP, SMD, SI, and RSE windows because the full path
  spans both the RSE 32-bit local view and the host/SMD 52-bit view.

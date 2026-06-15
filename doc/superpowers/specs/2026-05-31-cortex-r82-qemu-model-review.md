# Cortex-R82 QEMU Model Review

## Purpose

Review how to add a Cortex-R82 CPU model to the local QEMU/libqemu tree so
QBox can move Apollo FVP Safety Island CL0/CL1 from service-model behavior to
live firmware execution.

## Conclusion

Adding `-cpu cortex-r82` is not just a named-CPU registration task. Cortex-R82
is an Armv8-R AArch64 CPU, while the existing local QEMU R-profile model is
centered on Cortex-R52 in `target/arm/tcg/cpu32.c`. The Apollo Safety Island
firmware uses AArch64 EL2 and Armv8-R MPU/PMSA system registers early in reset,
so the practical minimum is:

1. Register an AArch64 Cortex-R82 CPU model.
2. Advertise Armv8-R AArch64/PMSA capability in the ID registers.
3. Add AArch64 EL2 MPU system registers used by SCP-Firmware.
4. Extend or add PMSAv8-R address translation for 64-bit addresses.
5. Add QBox CPU dynamic modules and a remote Safety Island CPU wrapper.

The recommended first implementation is a boot-oriented Cortex-R82 model that
supports the Apollo Safety Island firmware's observable architectural needs.
Microarchitectural fidelity, cache/ECC/RAS detail, CTI/ETM, and performance
behavior should remain explicit follow-up work.

## Evidence

### Local QEMU State

Local QEMU is:

```text
tools/qemu: libqemu-v11.0-v0.5-3-g3bb3280554c1
```

Relevant files:

- `tools/qemu/target/arm/tcg/cpu32.c`
  - Implements and registers `cortex-r5`, `cortex-r5f`, and `cortex-r52`.
  - `cortex_r52_initfn()` sets `ARM_FEATURE_V8`, `ARM_FEATURE_EL2`,
    `ARM_FEATURE_PMSA`, `ARM_FEATURE_NEON`, generic timer support, and
    PMSAv8-R region counts.
- `tools/qemu/target/arm/tcg/cpu64.c`
  - Registers AArch64 named CPUs such as `cortex-a720ae`, `neoverse-n1`, and
    `neoverse-n2`.
  - Does not register `cortex-r82`.
- `tools/qemu/target/arm/helper.c`
  - Contains PMSAv8-R register state and handlers for AArch32 coprocessor
    encodings such as `PRBAR`, `PRLAR`, `PRSELR`, `HPRBAR`, `HPRLAR`,
    `MPUIR`, and `HMPUIR`.
  - Does not currently expose the AArch64 system-register names used by
    Apollo SCP-Firmware, such as `PRBAR_EL2`, `PRLAR_EL2`, `PRSELR_EL2`, and
    `MPUIR_EL2`.
- `tools/qemu/target/arm/ptw.c`
  - Has a PMSAv8 lookup path, but the current helper signature and logging use
    32-bit addresses. Apollo Safety Island memory maps include addresses above
    4 GiB, so the implementation must be audited before claiming Cortex-R82
    fidelity.

### Local QBox State

Local QBox is:

```text
tools/qbox: v7.1.4-31-ge1cf64d4de89
```

Relevant files:

- `tools/qbox/qemu-components/cpu_arm/CMakeLists.txt`
  - Adds dynamic modules for Cortex-A/M/R models up to `cpu_arm_cortex_r52`.
- `tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r52/include/cortex-r52.h`
  - Wraps QEMU CPU type `cortex-r52-arm`.
- `tools/qbox/platforms/cortex-m55-remote/src/remote_cpu.h`
  - Shows the existing remote CPU wrapper pattern used by the RSE Cortex-M55.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
  - Uses `RemoteCPU` for the RSE Cortex-M55 and service-model behavior for
    Safety Island.

### Apollo Safety Island Firmware Needs

Relevant files:

- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/Toolchain-GNU.cmake`
  - Sets `SCP_AARCH64_PROCESSOR_TARGET` to `cortex-r82`.
- `hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/CMakeLists.txt`
  - Does not define `ARMV8A64_EL3_SUPPORT` when the target is `cortex-r82`.
    This matches the Zena documentation: Cortex-R82AE Safety Island runs with
    EL2 as the highest exception level, not EL3.
- `hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_crt0.S`
  - Starts at EL2 for Cortex-R82.
  - Reads `ID_AA64MMFR0_EL1` and checks MSA fields.
  - Writes `MAIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, `PRLAR_EL2`, and
    `SCTLR_EL2`.
- `hsoc-stack/components/system_mgmt/scp-firmware/module/armv8r_mpu/src/mod_armv8r_mpu.c`
  - Reads `MPUIR_EL2`.
  - Programs `MAIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, `PRLAR_EL2`, and
    `SCTLR_EL2`.
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_armv8r_mpu.c`
  - Programs Safety Island memory regions through 64-bit PRBAR/PRLAR values.

### External Reference Points

- Arm Cortex-R82 public datasheet describes Cortex-R82 as Armv8-R AArch64 with
  A64 instruction support, secure-state operation at EL0 to EL2, GICv3.2 CPU
  interface, generic timer, optional TCMs, MPU, MMU, RAS, PMU, and debug/trace
  features.
- QEMU's public Arm documentation says R-profile TCG support is limited, while
  the current QEMU MPS3 documentation also documents the existing Cortex-R52
  board coverage. The local fork already includes Cortex-R52 CPU support, but
  not Cortex-R82.

## Implementation Strategy

### Stage 0: Baseline Probe

Establish the current absence of Cortex-R82:

```bash
rg -n "cortex-r82|Cortex-R82|R82" tools/qemu/target/arm tools/qbox/qemu-components
rg -n "cortex-r52|pmsav8r|PRBAR|PRLAR|MPUIR" tools/qemu/target/arm
```

After a local QEMU build exists, also probe the CPU list:

```bash
tools/qbox/build/_deps/libqemu-build/qemu-prefix/bin/qemu-system-aarch64 -cpu help
```

Expected current result: no `cortex-r82` CPU type.

### Stage 1: Add AArch64 CPU Registration

Add a new Cortex-R82 init function in:

```text
tools/qemu/target/arm/tcg/cpu64.c
```

The first model should:

- Register `.name = "cortex-r82"` in `aarch64_cpus[]`.
- Set `dtb_compatible = "arm,cortex-r82"`.
- Set Arm features required by the firmware:
  `ARM_FEATURE_V8`, `ARM_FEATURE_AARCH64`, `ARM_FEATURE_EL2`,
  `ARM_FEATURE_PMSA`, `ARM_FEATURE_NEON`, `ARM_FEATURE_GENERIC_TIMER`, and
  PMU if the register set is exposed.
- Avoid `ARM_FEATURE_EL3` because the Apollo SCP-Firmware Cortex-R82 path does
  not expect EL3.
- Set region counts for EL2/EL1 MPU support. Start with the minimum region
  count required by `config_armv8r_mpu.c`, then align with the TRM/FVP value.
- Set `ID_AA64MMFR0_EL1` MSA and MSA fraction fields to nonzero values that
  match Armv8-R64 PMSA support.
- Set a provisional MIDR only after confirming the exact implementer, part,
  variant, and revision values from Arm/FVP evidence. The Arm part number for
  Cortex-R82 is commonly reported as `0xd15`, but the full MIDR value should be
  evidence-backed.

This stage only proves that QEMU recognizes the named CPU. It is not enough to
run Apollo Safety Island firmware.

### Stage 2: Add AArch64 Armv8-R MPU System Registers

Extend the existing PMSAv8-R register handling in:

```text
tools/qemu/target/arm/helper.c
```

The Apollo firmware requires at least:

```text
MPUIR_EL2
PRSELR_EL2
PRBAR_EL2
PRLAR_EL2
MAIR_EL2
SCTLR_EL2
ID_AA64MMFR0_EL1
```

`MAIR_EL2`, `SCTLR_EL2`, and `ID_AA64MMFR0_EL1` already exist as general
AArch64 registers, but the PMSA-related values must be correct for R82.
`MPUIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, and `PRLAR_EL2` need AArch64
system-register definitions that read/write the same underlying PMSAv8-R state
currently used by the AArch32 `HMPUIR`, `HPRSELR`, `HPRBAR`, and `HPRLAR`
handlers.

Keep this mapping narrow:

- EL2 aliases should use the `hpr*` state because the firmware runs at EL2.
- Implement only the EL2 registers needed by the Apollo firmware first.
- Add EL1 aliases later when CL1 Zephyr or another payload proves they are
  needed.

### Stage 3: Fix 64-bit PMSA Address Handling

Audit and extend PMSAv8-R translation in:

```text
tools/qemu/target/arm/ptw.c
tools/qemu/target/arm/cpu.h
```

Current PMSAv8 lookup code uses 32-bit address variables in key places. That is
acceptable for Cortex-R52-style 32-bit R-profile use, but not enough for an
Armv8-R AArch64 Cortex-R82 model when Safety Island maps use 64-bit PRBAR and
PRLAR values.

Required behavior:

- Store PRBAR/PRLAR values as 64-bit architectural values.
- Compare 64-bit guest physical addresses against 64-bit MPU regions.
- Preserve subpage behavior when a region covers only part of a QEMU page.
- Preserve EL2 region selection through `PRSELR_EL2`.
- Invalidate TLBs when MPU region registers or `SCTLR_EL2.M` change.
- Keep the old Cortex-R52 behavior unchanged.

This is the highest-risk part of the CPU model. It should be developed with
focused tests before running full Apollo firmware.

### Stage 4: Add QEMU CPU Tests

Add tests that run against the built `qemu-system-aarch64`:

```text
tools/qemu/tests/qtest/
```

or a local project-level script under:

```text
scripts/
```

Minimum checks:

- `-cpu help` lists `cortex-r82`.
- QMP `query-cpu-model-expansion` expands `cortex-r82`.
- A tiny AArch64 EL2 payload can:
  - read `CurrentEL` and observe EL2,
  - read `ID_AA64MMFR0_EL1` and see MSA support,
  - read `MPUIR_EL2`,
  - write `MAIR_EL2`,
  - write `PRSELR_EL2`, `PRBAR_EL2`, `PRLAR_EL2`,
  - enable `SCTLR_EL2.M`,
  - execute, read, and write inside allowed regions.

Add one negative test after the positive path is stable:

- Access outside enabled MPU regions should fault.

### Stage 5: Add QBox CPU Dynamic Module

Add a QBox wrapper matching the existing style:

```text
tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/
tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/CMakeLists.txt
tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h
tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/src/cortex-r82.cc
```

Then update:

```text
tools/qbox/qemu-components/cpu_arm/CMakeLists.txt
```

The wrapper should mirror `cpu_arm_cortex_r52` first, but construct QEMU CPU
type:

```text
cortex-r82-arm
```

Initial parameters:

- `rvbar`
- `cntfrq_hz`
- `start_powered_off`
- `gdb_port`
- IRQ/FIQ signal sockets
- generic timer output sockets

Avoid PSCI parameters for the Safety Island first path unless the firmware
actually uses PSCI. Safety Island reset/power state should be driven by the
modeled Apollo/SI control path.

### Stage 6: Add Safety Island Remote CPU Wrapper

Do not reuse the existing `RemoteCPU` class directly because it hardcodes a
Cortex-M55 member. Add a Safety Island-specific wrapper such as:

```text
tools/qbox/platforms/apollo-fvp/src/remote_cortex_r82.h
tools/qbox/platforms/apollo-fvp/src/remote_cortex_r82.cc
```

or add a generic templated remote CPU wrapper only if the local QBox style makes
that simple.

The wrapper must expose:

- CPU TLM initiator socket into the Safety Island local router.
- IRQ/FIQ inputs from GIC-720AE or the temporary GIC model.
- GDB port parameter.
- Reset vector parameter.
- File-backed console/debug integration through the platform, not through the
  CPU wrapper.

### Stage 7: Integrate Into Apollo Full Platform

After the CPU smoke tests pass, wire live Safety Island execution into:

```text
tools/qbox/platforms/apollo-fvp/full.lua
scripts/run/run_qbox_apollo_fvp_full.py
```

Start with SI CL0 SCP-Firmware before SI CL1 Zephyr:

- SI CL0 is system-management critical and already built as `si0_ramfw.bin`.
- RSE BL2 already loads SI CL0 images.
- SI CL0 owns the SCMI/PFDI/system-management interactions currently modeled by
  service components.

Keep a runtime switch:

```text
QBOX_APOLLO_FULL_SI_MODE=service-model|live-r82
```

This lets the existing service-model boot remain the regression baseline while
the live R82 path matures.

## Recommended Work Breakdown

1. `feat(qemu): register cortex-r82 shell`
   - Add named CPU registration and a minimal QEMU CPU-list test.
   - Acceptance: `qemu-system-aarch64 -cpu help` lists `cortex-r82`.

2. `feat(qemu): add R82 EL2 MPU registers`
   - Add AArch64 `MPUIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, and `PRLAR_EL2`.
   - Acceptance: EL2 payload can read/write the registers without undefined
     exceptions.

3. `feat(qemu): support AArch64 PMSAv8-R regions`
   - Extend 64-bit PRBAR/PRLAR lookup and invalidation.
   - Acceptance: positive and negative MPU-region payload tests pass.

4. `feat(qbox): add Cortex-R82 CPU wrapper`
   - Add `cpu_arm_cortexR82` dynamic module.
   - Acceptance: QBox loads the module and creates a CPU object.

5. `feat(apollo): add live SI R82 mode`
   - Add Apollo Safety Island wrapper and platform switch.
   - Acceptance: SI CL0 reaches early SCP-Firmware log markers under QBox.

6. `test(apollo): boot live SI firmware path`
   - Integrate with the full Apollo runner.
   - Acceptance: RSE + live SI CL0 + AP handoff progress at least to the
     current service-model handoff marker group, then broaden to CL1/Zephyr.

## Risks

- **AArch64 PMSA support is the main implementation risk.** QEMU already has
  some PMSAv8-R state, but the current visible support is oriented around
  AArch32 encodings and 32-bit address lookup.
- **Exact Cortex-R82 ID registers require Arm/FVP evidence.** A provisional CPU
  can boot firmware, but upstream-quality modeling should not guess MIDR and ID
  registers.
- **Safety Island interrupt modeling is separate from the CPU model.** A live
  Cortex-R82 CPU still needs a compatible GIC-720AE/GICv3 view, MHU interrupts,
  timers, UART, ATU windows, and reset/power control.
- **Service-model behavior must remain available.** It is the regression
  baseline for full Apollo boot while the live CPU path is incomplete.

## Validation Commands

Static and build:

```bash
git -C tools/qemu diff --check
git -C tools/qbox diff --check
cmake --preset gcc -DLIBQEMU_TARGETS=aarch64
cmake --build --preset gcc --target qemu --parallel
cmake --build --preset gcc --target cpu_arm_cortexR82 --parallel
```

CPU model probes:

```bash
tools/qbox/build/_deps/libqemu-build/qemu-prefix/bin/qemu-system-aarch64 -cpu help
python3 scripts/inspect/probe_qemu_cortex_r82.py
```

Apollo integration:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-r82 \
  --timeout 900 \
  --out-dir build/qbox-apollo-fvp/full-live-r82
```

## Recommendation

Proceed only after adding a small QEMU-side EL2 MPU payload test. Without that
test, failures in Apollo full boot will be difficult to separate into CPU
model, GIC, MHU, memory-map, or firmware issues.

For the immediate Apollo full-platform work, keep the Safety Island
service-model path as the default. Add Cortex-R82 behind an explicit
`live-r82` switch and promote it only after SI CL0 firmware reaches stable log
markers.

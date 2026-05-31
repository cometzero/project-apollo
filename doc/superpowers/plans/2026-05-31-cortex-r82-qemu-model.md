# Cortex-R82 QEMU/QBox Implementation Plan

## Scope

Implement the first boot-oriented Cortex-R82 support needed by the Apollo FVP
Safety Island path in QBox. The change is deliberately limited to the local
QEMU/libqemu model and the QBox CPU wrapper. Apollo platform wiring remains a
separate integration step after the CPU model can be built and discovered.

## Success Criteria

1. The local QEMU source advertises a `cortex-r82` AArch64 TCG CPU.
2. The CPU exposes EL2, PMSA, AArch64, generic timer, PMU, and AdvSIMD feature
   state needed by the current Apollo Safety Island firmware build.
3. AArch64 EL2 MPU registers used by the firmware are implemented:
   `MPUIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, and `PRLAR_EL2`.
4. PMSAv8-R RBAR/RLAR storage and lookup preserve 64-bit physical addresses.
5. QBox has a `cpu_arm_cortexR82` dynamic module using the QEMU
   `cortex-r82-arm` type.
6. Source probes, Python tests, diff checks, and the targeted QBox module build
   provide concrete verification.

## Implementation Steps

1. Add a source probe and pytest coverage.
   - Create `scripts/probe_qemu_cortex_r82.py`.
   - Verify QEMU CPU registration, EL2 MPU sysregs, 64-bit PMSAv8-R storage,
     and QBox wrapper registration.
   - Optionally verify `qemu-system-aarch64 -cpu help` when a binary path is
     supplied.

2. Add the QEMU Cortex-R82 CPU model.
   - Add `aarch64_cortex_r82_initfn()` in
     `tools/qemu/target/arm/tcg/cpu64.c`.
   - Register `cortex-r82` in `aarch64_cpus[]`.
   - Model this as an AArch64 Armv8-R EL2/PMSA CPU with no EL3.

3. Add AArch64 EL2 PMSAv8-R sysregs.
   - Add AA64 aliases for `MPUIR_EL2`, `PRSELR_EL2`, `PRBAR_EL2`, and
     `PRLAR_EL2` in `tools/qemu/target/arm/helper.c`.
   - Reuse existing PMSAv8-R selected-region behavior where possible.

4. Preserve 64-bit PMSAv8-R region addresses.
   - Change PMSAv8 RBAR/RLAR backing storage to `uint64_t`.
   - Update allocation, migration metadata, helper reads/writes, and
     `pmsav8_mpu_lookup()` address math.
   - Keep AArch32 register accesses compatible through existing lower-width
     access paths.

5. Add the QBox Cortex-R82 wrapper.
   - Add `tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/`.
   - Mirror the Cortex-R52 signal/timer surface and use the QEMU
     `cortex-r82-arm` CPU type.
   - Register the new component in `cpu_arm/CMakeLists.txt`.

6. Verify.
   - Run `python3 -m py_compile scripts/probe_qemu_cortex_r82.py`.
   - Run `pytest tests/test_probe_qemu_cortex_r82.py -q`.
   - Run `scripts/probe_qemu_cortex_r82.py --source-root .`.
   - Run `git -C tools/qemu diff --check` and
     `git -C tools/qbox diff --check`.
   - Build `cmake --build tools/qbox/build --target cpu_arm_cortexR82`.

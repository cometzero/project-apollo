# MMU-720AE SystemC Component Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

작성일: 2026-06-08

상태: 구현 진행 중

**Goal:** QEMU `arm_smmuv3` backend를 대체할 수 있는 FVP-parity
MMU-720AE SystemC/TLM component를 구현한다.

**Architecture:** `mmu720ae` top module은 SMMUv3 TCU register frame, five
Apollo TBU ingress sockets, queue engine, table walker, TLB/uTLB, IRQ/MSI,
RAS/PMU state를 SystemC/TLM으로 제공한다. QEMU backend는 A/B 비교용으로
유지하고, 최종 Apollo path는 opt-in 검증 후 SystemC model을 default로 전환한다.

현재 진행 상태:

- Phase 1/2의 CMake, component skeleton, register-bank boot surface가
  구현되었다.
- Phase 3은 Linux probe에 필요한 CMDQ producer/consumer mirror까지만
  구현되었고, guest-memory queue fetch와 EVTQ/PRIQ record engine은 미완료다.
- Phase 5의 TBU socket surface는 존재한다. `SMMUEN` clear 상태에서는 bypass하고,
  enabled 상태에서는 table walker 미구현으로 인한 silent bypass를 막는다.
- Phase 7/8의 platform wiring과 Apollo full-system boot regression은
  `systemc-mmu720ae` default backend로 검증되었다.
- Phase 4/6/8의 translation, RAS/PMU/SMD_CSR, FVP parity comparison은 미완료다.

최신 진행과 gap은 `doc/qbox-mmu720ae-traceability-matrix.md`를 기준으로 한다.

**Tech Stack:** C++14, SystemC/TLM-2.0, QBox dynamic modules, CCI parameters,
Lua platform config, CMake/CTest, Python runtime validators, Arm MMU-720AE TRM
109745, Arm SMMUv3 Architecture Specification IHI 0070.

---

## 구현 순서

### Phase 0: Baseline and Evidence Lock

Files:

- Read: `doc/arm_zena_css_dev_guide/92-useful-resources.md`
- Read: `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- Read: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- Read: `tools/qbox/qemu-components/arm_smmuv3/include/arm-smmuv3.h`
- Read: `tools/qbox/platforms/fvp-rd-aspen/conf.lua`
- Read: `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- Read: `hsoc-stack/components/primary_compute/linux/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c`

Steps:

- [ ] Record current dirty state without modifying unrelated nested repos.
- [ ] Capture current QEMU-backed direct boot and full-system SMMU evidence.
- [ ] Capture FVP boot SMMU evidence with Linux dmesg, `/proc/interrupts`,
  `/sys/kernel/iommu_groups`, and available SMMU driver tracepoints.
- [ ] Create a traceability matrix from MMU-720AE TRM, SMMUv3 spec, Zena CSS
  docs, Linux driver expectations, QBox tests, and FVP runtime observations.

Commands:

```bash
git status --short
git -C tools/qbox status --short
python3 scripts/run_qbox_fvp_rd_aspen_linux.py \
  --timeout 600 --post-login-probe \
  --out-dir build/qbox-fvp-rd-aspen/mmu720ae-baseline-qemu
python3 scripts/run_qbox_apollo_fvp_full.py \
  --timeout 900 --out-dir build/qbox-apollo-fvp/mmu720ae-baseline-full
```

Expected:

- QEMU-backed run evidence exists.
- Any current boot blocker is recorded separately from SMMU implementation
  scope.
- Traceability matrix names every feature bit that the profile will expose.

### Phase 1: Test Scaffolding Before Model Code

Files:

- Create: `tools/qbox/tests/components/mmu720ae/CMakeLists.txt`
- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-register-tests.cc`
- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-queue-tests.cc`
- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-translation-tests.cc`
- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-tbu-tests.cc`
- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-dmi-tests.cc`
- Modify: `tools/qbox/tests/components/CMakeLists.txt`

Steps:

- [ ] Add failing reset/ID register tests using profile values from Phase 0.
- [ ] Add failing `CR0` write and `CR0ACK` sync tests.
- [ ] Add failing command queue `CMD_SYNC` and TLBI tests.
- [ ] Add failing stage 1, stage 2, bypass, abort, bad STE, bad CD tests.
- [ ] Add failing TBU SID fallback and SID extension tests.
- [ ] Add failing DMI grant and stale-DMI invalidation tests.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae-register-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae' --output-on-failure
```

Expected:

- Tests configure and build after skeleton target exists.
- Before implementation, behavior tests fail for missing model or missing
  semantics, not because of CMake wiring errors.

### Phase 2: Component Skeleton and Register Bank

Files:

- Create: `tools/qbox/systemc-components/mmu720ae/CMakeLists.txt`
- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae.h`
- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h`
- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_regs.h`
- Create: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae.cc`
- Create: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_core.cc`
- Modify: `tools/qbox/systemc-components/CMakeLists.txt`

Steps:

- [ ] Add `gs_create_dymod(mmu720ae)` target.
- [ ] Expose `mem` and `reg_socket` target sockets, `irq_combined`, `reset`,
  `ptw_socket`, and `downstream_socket`.
- [ ] Add profile CCI parameters and strict unsupported-feature check.
- [ ] Implement register read/write decode table for the Phase 0 profile.
- [ ] Implement reset values and write masks.
- [ ] Implement `CR0`, `CR0ACK`, queue enable, SMMU enable, and disable
  side effects required by Linux probe.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae --parallel 8
cmake --build tools/qbox/build --target mmu720ae-register-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-register-tests' --output-on-failure
git -C tools/qbox diff --check
```

Expected:

- `mmu720ae` builds without QEMU target dependencies.
- Register tests pass.

### Phase 3: Queue Engine

Files:

- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_queue.h`
- Create: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_queue.cc`
- Modify: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h`
- Modify: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_core.cc`
- Modify: `tools/qbox/tests/components/mmu720ae/mmu720ae-queue-tests.cc`

Steps:

- [ ] Implement guest-memory queue fetch through `ptw_socket`.
- [ ] Implement CMDQ producer/consumer handling.
- [ ] Implement `CMD_SYNC`, config cache invalidation, TLB invalidation, and
  illegal command handling.
- [ ] Implement EVTQ and PRIQ record write helpers.
- [ ] Implement queue overflow and error status.
- [ ] Raise/deassert combined IRQ based on queue and global error status.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae-queue-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-queue-tests' --output-on-failure
```

Expected:

- Queue tests pass, including `CMD_SYNC` completion and event IRQ assertion.

### Phase 4: Table Walker and Translation Core

Files:

- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_table_walker.h`
- Create: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_table_walker.cc`
- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_tlb.h`
- Modify: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h`
- Modify: `tools/qbox/tests/components/mmu720ae/mmu720ae-translation-tests.cc`

Steps:

- [ ] Implement STE decode for valid, bypass, abort, S1, S2, and nested paths.
- [ ] Implement CD decode for S1 translation.
- [ ] Implement AArch64 stage 1 descriptor walk.
- [ ] Implement AArch64 stage 2 descriptor walk.
- [ ] Implement permission, access flag, output address size, and granule
  checks.
- [ ] Generate SMMUv3 event records for bad STE, bad CD, translation fault,
  permission fault, and unsupported attribute.
- [ ] Add TLB cache lookup and invalidation hooks.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae-translation-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-translation-tests' --output-on-failure
```

Expected:

- Translation tests pass for bypass, stage 1, stage 2, nested, abort, and
  negative fault cases.

### Phase 5: TBU Ingress and DMI

Files:

- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_tbu.h`
- Create: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_tbu.cc`
- Create: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_trace.h`
- Modify: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae.h`
- Modify: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae.cc`
- Modify: `tools/qbox/tests/components/mmu720ae/mmu720ae-tbu-tests.cc`
- Modify: `tools/qbox/tests/components/mmu720ae/mmu720ae-dmi-tests.cc`

Steps:

- [ ] Add five Apollo TBU target sockets.
- [ ] Add request attribute extension parser and default SID fallback.
- [ ] Forward translated payloads through `downstream_socket`.
- [ ] Preserve byte enables, streaming width, debug access semantics, and TLM
  response status.
- [ ] Implement translated DMI grant with SID/SSID/security/generation key.
- [ ] Invalidate DMI on TLBI, STE/CD change, reset, SMMU disable, and fault
  recovery.
- [ ] Record TBU hit/miss/fault and fallback-SID stats.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae-tbu-tests mmu720ae-dmi-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-(tbu|dmi)-tests' --output-on-failure
```

Expected:

- TBU and DMI tests pass.
- No translated DMI survives invalidation.

### Phase 6: RAS, PMU, and Zena CSS Sideband

Files:

- Create: `tools/qbox/tests/components/mmu720ae/mmu720ae-ras-pmu-tests.cc`
- Modify: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h`
- Modify: `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_core.cc`
- Modify: `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_trace.h`
- Modify: `tools/qbox/tests/components/mmu720ae/CMakeLists.txt`

Steps:

- [ ] Implement SMMU PMU interrupt status and clear behavior required by Zena
  CSS IO_REGBANK.
- [ ] Implement TCU edge-triggered interrupt status.
- [ ] Implement SMMU/TBU RAS ERI/FHI/CRI status and check-signal view.
- [ ] Implement SMD_CSR sideband state for `IO_MMU_CFG`, `IO_TBU_NS_SID`,
  `IO_TBU_S_SID`, `IO_TCU_SID`, and `IO_TCU_SID_CHK`.
- [ ] Connect SMD_CSR SID high-bit configuration to TBU default SID mapping.

Commands:

```bash
cmake --build tools/qbox/build --target mmu720ae-ras-pmu-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-ras-pmu-tests' --output-on-failure
```

Expected:

- RAS/PMU/SMD_CSR tests pass.

### Phase 7: Platform Opt-In Wiring

Files:

- Modify: `tools/qbox/platforms/fvp-rd-aspen/conf.lua`
- Modify: `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- Modify: `tools/qbox/platforms/apollo/apollo-qvp.lua`
- Modify: `scripts/validate_qbox_fvp_rd_aspen_map.py`
- Modify: `scripts/run_qbox_fvp_rd_aspen_linux.py`
- Modify: `scripts/run_qbox_fvp_rd_aspen_rse.py`
- Modify: `scripts/run_qbox_apollo_fvp_full.py`
- Modify: `tools/qbox/platforms/fvp-rd-aspen/README.md`

Steps:

- [ ] Add `QBOX_RDASPEN_SMMU_BACKEND=qemu-arm-smmuv3|systemc-mmu720ae`.
- [x] Forward the same backend selector through Apollo full-system runner
  options.
- [x] Keep QEMU backend as fallback during transition.
- [ ] Add runner options `--smmu-backend qemu-arm-smmuv3|systemc-mmu720ae`.
- [ ] Record backend selection and MMU-720AE stats path in `result.json`.
- [ ] Update map validators to accept both backend names during transition.

Commands:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_linux.py \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py \
  scripts/validate_qbox_fvp_rd_aspen_map.py
cmake --build tools/qbox/build --target platforms-vp mmu720ae --parallel 8
python3 scripts/validate_qbox_fvp_rd_aspen_map.py
```

Expected:

- SystemC backend can elaborate.
- QEMU backend remains selectable as a fallback.
- Current default path is `systemc-mmu720ae` after boot-regression validation;
  FVP-parity completion remains gated by Phase 8 comparison and synthetic
  DMA/fault work.

### Phase 8: Runtime and FVP Parity Validation

Files:

- Create: `scripts/compare_fvp_qbox_smmu.py`
- Modify: `scripts/run_qbox_fvp_rd_aspen_linux.py`
- Modify: `scripts/run_qbox_apollo_fvp_full.py`
- Modify: `doc/qbox-fvp-emulation-project.md`
- Modify: `doc/apollo-qbox-hardware-ko.md`

Steps:

- [ ] Add SMMU post-login probes for dmesg, sysfs IOMMU groups, interrupts,
  DMA/IOMMU debugfs when enabled, and fault injection output.
- [ ] Add FVP/QBox SMMU comparison report generator.
- [ ] Run direct Linux boot with QEMU backend and SystemC backend.
- [ ] Run Apollo full boot with QEMU backend and SystemC backend.
- [ ] Compare SMMU register trace, driver output, interrupt status, and
  synthetic DMA results.
- [x] Keep SystemC backend as current boot-validated default while recording all
  remaining FVP parity gaps.

Commands:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_linux.py \
  --smmu-backend systemc-mmu720ae \
  --timeout 600 --post-login-probe \
  --out-dir build/qbox-fvp-rd-aspen/mmu720ae-systemc-direct

python3 scripts/run_qbox_apollo_fvp_full.py \
  --smmu-backend systemc-mmu720ae \
  --timeout 900 \
  --out-dir build/qbox-apollo-fvp/mmu720ae-systemc-full

python3 scripts/compare_fvp_qbox_smmu.py \
  --fvp build/local-apollo-fvp/fvp-boot/result.json \
  --qbox build/qbox-apollo-fvp/mmu720ae-systemc-full/result.json \
  --out build/qbox-apollo-fvp/mmu720ae-systemc-full/smmu-fvp-compare.json
```

Expected:

- Direct and full runs preserve existing boot markers.
- SMMU comparison report passes all mandatory checks.

## Completion Gate

Implementation is complete only when:

- `ctest --test-dir tools/qbox/build -R 'mmu720ae' --output-on-failure` passes.
- `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` passes.
- Direct Linux boot with `--smmu-backend systemc-mmu720ae` passes.
- Full Apollo boot with `--smmu-backend systemc-mmu720ae` passes or only shows
  blockers proven unrelated to SMMU.
- FVP/QBox SMMU comparison report has no mandatory mismatch.
- `doc/qbox-fvp-emulation-project.md` and `doc/apollo-qbox-hardware-ko.md`
  record the backend change and remaining fidelity gaps.

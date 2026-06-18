# Apollo QBox Full Model Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

작성일: 2026-06-14

**Goal:** Apollo QBox full-system에서 safety/security/control side effect가
필요한 `gs_memory`/stub IP를 full SystemC/TLM model로 승격한다.

**Architecture:** 기존 RSE-first Apollo QVP topology와 QEMU CPU/GIC/virtio
backend는 유지한다. `zena_fmu`, `zena_ssu`, `rse_protection_ctrl`,
후속 `host_apu_filter`, `host_rgm`, `host_pik`, `host_io_regbank`를 작은
SystemC component로 추가하고 Lua에서 boot-critical placeholder window를
단계적으로 교체한다.

**Tech Stack:** C++14, SystemC/TLM-2.0, QBox dynamic modules, QEMU/libqemu
wrappers, Lua platform config, CMake/CTest, Python QBox runners and coverage
audits, Arm Zena CSS developer guide.

---

## Task Board

| ID | Task | 완료 기준 |
| --- | --- | --- |
| MODEL-000 | Baseline ledger | placeholder/memory-backed/full-required 분류 파일 생성 |
| MODEL-010 | FMU/SSU tests | failing component tests 추가 |
| MODEL-020 | `zena_fmu` | FMU unit tests pass |
| MODEL-030 | `zena_ssu` | SSU unit tests pass |
| MODEL-040 | CL0 Lua wiring | live CL0 boot regression pass |
| MODEL-050 | RSE protection | secure/non-secure access tests pass |
| MODEL-060 | APU/ATU coverage gate | `rse_atu` permission/error tests and backend audit pass |
| MODEL-070 | RGM/PIK/counter | reset/power polling tests pass |
| MODEL-080 | AP secure watchdog | secure watchdog regression pass |
| MODEL-090 | Coverage/verifier update | unclassified placeholder causes fail |
| MODEL-100 | Runtime/FVP validation | full-system and comparison gates pass |
| MODEL-110 | Future parity backlog split | GIC/RAS/AP16/RoS/debug scope가 별도 epic으로 분리됨 |

## Requirement Traceability

| Requirement | Primary tasks | Verification |
| --- | --- | --- |
| FR-001 FMU model | MODEL-010, MODEL-020, MODEL-040, MODEL-090 | V1, V2, V3, V4 |
| FR-002 SSU model | MODEL-010, MODEL-030, MODEL-040, MODEL-090 | V1, V2, V3, V4 |
| FR-003 RSE protection model | MODEL-050, MODEL-090 | V1, V3, V4 |
| FR-004 NI-710AE APU/ATU error model | MODEL-060, MODEL-090 | V1, V2, V3, V4 |
| FR-005 System management control model | MODEL-070, MODEL-090 | V1, V2, V3 |
| FR-006 AP secure watchdog | MODEL-080, MODEL-090 | V2, V3, V4 |
| FR-007 GIC/RAS/AP topology | MODEL-000, MODEL-090, MODEL-110 | V2, V5 |
| FR-008 RoS/I/O/debug extension | MODEL-000, MODEL-090, MODEL-110 | V2, V5 |

## MODEL-000: Baseline Ledger

Files:

- Create: `doc/apollo-qbox-full-model/coverage-ledger.md`
- Modify: `doc/apollo-qbox-hardware-ko.md`

Steps:

- [ ] Record every Apollo `gs_memory` instance from `tools/qbox-platform/platforms/apollo/hw-block/`.
- [ ] Classify each entry as `memory-backing`, `accepted-placeholder`, or
  `full-model-required`.
- [ ] Add a source column with Zena CSS guide, Apollo QBox doc, or Lua path.
- [ ] Mark P0 items: `si_cl0_fmu`, `si_cl0_ssu`,
  `rse_nsacfg_regs`, `rse_sacfg_regs`, `rse_mpc_vm0_regs`,
  `rse_mpc_vm1_regs`, `rse_sic_regs`, `rse_mpc_sic_regs`.

Commands:

```bash
rg -n 'moduletype\\s*=\\s*"gs_memory"|modeled\\s*=\\s*false' \
  tools/qbox-platform/platforms/apollo
git diff --check
```

Expected:

- Ledger has no unclassified Apollo placeholder.
- No code behavior changes.

## MODEL-010: FMU/SSU Test Scaffolding

Files:

- Create: `tools/qbox/tests/components/zena_fmu/CMakeLists.txt`
- Create: `tools/qbox/tests/components/zena_fmu/zena_fmu-tests.cc`
- Create: `tools/qbox/tests/components/zena_ssu/CMakeLists.txt`
- Create: `tools/qbox/tests/components/zena_ssu/zena_ssu-tests.cc`
- Modify: `tools/qbox/tests/components/CMakeLists.txt`

Required test cases:

- FMU reset reads return documented PID/CID and zero status.
- FMU `ERR<n>CTLR` preserves RW bits and ignores RO bits.
- FMU `ERR<n>STATUS` implements W1C clear.
- FMU software injection sets `ERR<n>STATUS.V` and group status.
- FMU critical and non-critical interrupt outputs assert/deassert.
- SSU reset starts in `TEST` state.
- SSU `ERR_CTRL.CR_EN` and `ERR_CTRL.NCR_EN` gate input reporting.
- SSU FMU critical input moves `SYS_STATUS` to `ERRC`.
- SSU FMU non-critical input moves `SYS_STATUS` to `ERRN`.

Commands:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target zena_fmu-tests --parallel 8
cmake --build build/local-apollo-fvp/work/qbox-platform --target zena_ssu-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'zena_(fmu|ssu)' --output-on-failure
```

Expected:

- Before MODEL-020/MODEL-030 implementation, tests build only after component
  skeleton exists and fail on missing semantics.
- After MODEL-020/MODEL-030, all tests pass.

## MODEL-020: `zena_fmu` Component

Files:

- Create: `tools/qbox/systemc-components/zena_fmu/CMakeLists.txt`
- Create: `tools/qbox/systemc-components/zena_fmu/include/zena_fmu.h`
- Create: `tools/qbox/systemc-components/zena_fmu/src/zena_fmu.cc`
- Modify: `tools/qbox/systemc-components/CMakeLists.txt`

Implementation requirements:

- Provide `target_socket`.
- Provide `critical_irq` and `non_critical_irq` outputs.
- Provide CCI parameters: `record_count`, `critical_mask`,
  `non_critical_mask`, `pidr0`, `pidr1`, `pidr2`, `pidr3`.
- Implement offsets from the FMU summary:
  `ERR<n>FR`, `ERR<n>CTLR`, `ERR<n>STATUS`, `ERRIMPDEF<n>`,
  `SYS_KEY`, `ERRGSR_L/H`, PID/CID.
- Reject unsupported access sizes with TLM error response.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target zena_fmu zena_fmu-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'zena_fmu' --output-on-failure
git -C tools/qbox diff --check
```

## MODEL-030: `zena_ssu` Component

Files:

- Create: `tools/qbox/systemc-components/zena_ssu/CMakeLists.txt`
- Create: `tools/qbox/systemc-components/zena_ssu/include/zena_ssu.h`
- Create: `tools/qbox/systemc-components/zena_ssu/src/zena_ssu.cc`
- Modify: `tools/qbox/systemc-components/CMakeLists.txt`

Implementation requirements:

- Provide `target_socket`.
- Provide `critical_in` and `non_critical_in` inputs.
- Provide `safety_status_out` or equivalent observable output.
- Implement `ERR_FR`, `ERR_CTRL`, `ERR_STATUS`, `ERR_IMPDEF`,
  `SYS_KEY`, `SYS_STATUS`, `SYS_CTRL`, `STATUS_DETAIL`, PID/CID.
- Expose state changes to QBox logs at low volume.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target zena_ssu zena_ssu-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'zena_ssu' --output-on-failure
git -C tools/qbox diff --check
```

## MODEL-040: Safety Island CL0 Lua Wiring

Files:

- Modify: `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- Modify: `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`

Steps:

- [ ] Replace `si_cl0_ssu` `gs_memory` with `zena_ssu`.
- [ ] Replace `si_cl0_fmu` `gs_memory` with `zena_fmu`.
- [ ] Wire FMU critical/non-critical outputs to CL0 GIC SPIs used by SCP.
- [ ] Wire FMU outputs to SSU inputs.
- [ ] Record `fmu_backend=systemc-zena_fmu` and
  `ssu_backend=systemc-zena_ssu` in coverage output.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target platforms-vp --parallel 8
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/fmu-ssu-live-cl0-cl1
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/fmu-ssu-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/fmu-ssu-live-cl0-cl1/coverage-audit.json
```

Expected:

- RSE, SI CL0, SI CL1, AP firmware, Linux, and post-login markers pass.
- Coverage no longer reports FMU/SSU as `gs_memory`.

## MODEL-050: RSE Protection Model

Files:

- Create: `tools/qbox/systemc-components/rse_protection_ctrl/CMakeLists.txt`
- Create: `tools/qbox/systemc-components/rse_protection_ctrl/include/rse_protection_ctrl.h`
- Create: `tools/qbox/systemc-components/rse_protection_ctrl/src/rse_protection_ctrl.cc`
- Create: `tools/qbox/tests/components/rse_protection_ctrl/rse_protection_ctrl-tests.cc`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`

Required behavior:

- MPC reset values match current seeded `BLK_MAX`, `BLK_CFG`, PIDR values.
- Secure alias and non-secure alias return different access results where
  configured.
- Locked regions ignore writes.
- Illegal non-secure write produces configured error response.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target rse_protection_ctrl rse_protection_ctrl-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'rse_protection_ctrl' --output-on-failure
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/rse-protection-live-cl0-cl1
```

## MODEL-060: APU/ATU Coverage Gate

Files:

- Modify: `tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`

Required behavior:

- `rse_atu` remains the first-wave AP/SI/SMD expansion ATU backend.
- Existing `rse_atu` tests cover allowed translation, blocked access, and
  mismatch/error latch behavior.
- Coverage audit fails if `host_si_atu`, `host_ap_atu`, or
  `host_smdexp2smd_atu` no longer use `rse_atu`.
- Strict NI-710AE APU requester policy is deferred to follow-up
  `host_apu_filter`.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target rse_atu rse_atu-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'rse_atu' --output-on-failure
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --output build/qbox-apollo-fvp/full-model-first-wave-coverage.json
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/apu-filter-live-cl0-cl1
```

## MODEL-070: RGM/PIK/Counter Control Models

Files:

- Create: `tools/qbox/systemc-components/host_rgm/`
- Create: `tools/qbox/systemc-components/host_pik/`
- Extend: `tools/qbox/systemc-components/host_gtimer/`
- Create: `tools/qbox/tests/components/host_rgm/host_rgm-tests.cc`
- Create: `tools/qbox/tests/components/host_pik/host_pik-tests.cc`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`

Required behavior:

- RGM control/status/syndrome registers expose reset cause and mask behavior.
- PIK status registers satisfy SCP polling and emit reset/power event metadata.
- CSS counter/timer windows use `host_gtimer` or a narrow counter model instead
  of writable memory.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target host_rgm host_pik host_rgm-tests host_pik-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'host_(rgm|pik)' --output-on-failure
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/rgm-pik-live-cl0-cl1
```

## MODEL-080: AP Secure Watchdog

Files:

- Extend: `tools/qbox/qemu-components/sbsa_gwdt/`
- Or create: `tools/qbox/systemc-components/host_secure_wdog/`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`

Decision:

- Prefer extending the existing `sbsa_gwdt` wrapper if it can expose separate
  secure control/refresh frames without breaking the non-secure watchdog.
- Use `host_secure_wdog` only if the QEMU wrapper cannot represent the secure
  frame split cleanly.

Verification:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target platforms-vp --parallel 8
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/secure-watchdog-live-cl0-cl1
```

## MODEL-090: Coverage And Verifier Updates

Files:

- Modify: `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`
- Modify: `scripts/test/verify_qbox_apollo_fvp_full_completion.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`
- Modify: `doc/qbox-apollo-fvp-full-system-goal-verification.md`

Required behavior:

- `full-model-required` item still backed by `gs_memory` fails coverage.
- `memory-backing` item backed by `gs_memory` passes coverage.
- `accepted-placeholder` item passes only with documented reason and owner.
- `result.json` records FMU, SSU, RSE protection, APU, RGM, PIK, secure
  watchdog backend labels.

Verification:

```bash
python3 -m py_compile scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  scripts/test/verify_qbox_apollo_fvp_full_completion.py
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-model-coverage-check/coverage-audit.json
```

## MODEL-100: Runtime And FVP Validation

Files:

- No source file changes unless validation exposes a defect.

Commands:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --timeout 1200 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/full-model-final
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-model-final/result.json \
  --output build/qbox-apollo-fvp/full-model-final/coverage-audit.json
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --run-dir build/qbox-apollo-fvp/full-model-final
```

Expected:

- Full-system QBox pass remains true.
- Coverage has no unclassified placeholder.
- Negative tests for FMU/SSU and RSE access-control pass.
- FVP comparison reports only reviewed intentional gaps.

## MODEL-110: Future Parity Backlog Split

Files:

- Create: `doc/apollo-qbox-full-model/future-parity-backlog-ko.md`
- Modify: `doc/apollo-qbox-hardware-ko.md`

Scope:

- GIC-720AE full multiview parity beyond the current QEMU GICv3 +
  `gicx00_multiview` hybrid.
- AP 16-core live topology, 16 GIC redistributor frames, PFDI per-core channel
  scaling, and AP cluster RAS/PMU/MPAM surfaces.
- RAS FFH/CPER buffer functional model and Linux/firmware notification path.
- RoS System Registers, Virtio P9, VSI, RoS UART, TRNG, nvCounter, Ethernet,
  RoS/SMD flash, IO_REGBANK, PCIe PHY/controller, and CoreSight ROM/debug
  surfaces.

Required decision before implementation:

- Either mark the above as separate follow-up epics, or explicitly include a
  subset in the current full-model implementation wave.

Verification:

```bash
git diff --check
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-model-future-backlog/coverage-audit.json
```

Expected:

- No FR-007/FR-008 item remains silently implied.
- Coverage reports each P2/P3 item as `accepted-placeholder`,
  `unsupported-gap`, or linked follow-up scope.

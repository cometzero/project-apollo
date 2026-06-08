# QBox MMU-720AE SystemC Component Tasks and Verification Criteria

작성일: 2026-06-08

상태: 구현 진행 중

이 문서는 `doc/qbox-mmu720ae-systemc-spec-ko.md`,
`doc/qbox-mmu720ae-systemc-design-ko.md`,
`doc/qbox-mmu720ae-systemc-plan-ko.md`의 task backlog와 검증 기준이다.
구현 시 `superpowers:subagent-driven-development` 방식으로 task 단위
implementer, spec reviewer, quality reviewer를 분리한다.

현재 구현은 boot-regression 기준으로 `systemc-mmu720ae`를 기본 backend로
전환한 상태다. 다만 FVP parity 완료 조건은 아직 만족하지 못했다. 각 task의
상세 진행 상태와 runtime evidence는
`doc/qbox-mmu720ae-traceability-matrix.md`에서 추적한다.

## Task Board

| ID | Task | Dependencies | 완료 기준 |
| --- | --- | --- | --- |
| MMU720-SYS-001 | Baseline evidence lock | 없음 | QEMU-backed SMMU direct/full evidence와 FVP evidence가 저장됨 |
| MMU720-SYS-002 | TRM/spec traceability matrix | 001 | Exposed feature, register, reset, side effect, test mapping 완료 |
| MMU720-SYS-010 | Test/CMake scaffolding | 002 | 부분 완료: register/queue/TBU tests target 생성 |
| MMU720-SYS-020 | Component skeleton | 010 | 완료: `mmu720ae` dynamic module build |
| MMU720-SYS-030 | TCU register bank | 020 | 부분 완료: ID/reset/CR0ACK/register tests pass |
| MMU720-SYS-040 | Command/event/PRI queue engine | 030 | 부분 완료: CMDQ probe behavior, EVTQ translation fault record, IRQ clear, global-error clear tests pass |
| MMU720-SYS-050 | STE/CD/table walker | 040 | 미완료: translation tests and walker missing |
| MMU720-SYS-060 | TBU ingress path | 050 | 부분 완료: disabled bypass, enabled no-silent-bypass, SID extension/default SID fallback tests pass |
| MMU720-SYS-070 | DMI and cache invalidation | 060 | Stale-DMI-negative tests pass |
| MMU720-SYS-080 | RAS/PMU/SMD_CSR sideband | 070 | RAS/PMU/SID/uTLB tests pass |
| MMU720-SYS-090 | Platform wiring/default switch | 080 | 완료: direct/full platforms use SystemC backend by default, QEMU fallback selectable |
| MMU720-SYS-100 | Direct Linux runtime | 090 | 부분 완료: Linux `arm-smmu-v3` probe and login observed; full post-login optional driver set incomplete |
| MMU720-SYS-110 | Synthetic DMA/fault runtime | 100 | Bypass/translate/fault/permission/DMI negative cases pass |
| MMU720-SYS-120 | Full Apollo runtime | 110 | 진행 중: 이전 SystemC boot regression pass 존재, 최신 current build는 full-system handoff blocked |
| MMU720-SYS-130 | FVP parity comparison | 120 | Mandatory register/driver/fault/IRQ comparison pass |
| MMU720-SYS-140 | Documentation closure | 130 | Roadmap, hardware docs, README, runbook updated |
| MMU720-SYS-150 | Default backend switch | 140 | 완료 as boot-validated default; FVP parity still tracked as remaining work |

## Detailed Tasks

### MMU720-SYS-001: Baseline Evidence Lock

Commands:

```bash
git status --short
git -C tools/qbox status --short
python3 scripts/run_qbox_fvp_rd_aspen_linux.py \
  --timeout 600 --post-login-probe \
  --out-dir build/qbox-fvp-rd-aspen/mmu720ae-baseline-qemu
python3 scripts/run_qbox_apollo_fvp_full.py \
  --timeout 900 \
  --out-dir build/qbox-apollo-fvp/mmu720ae-baseline-full
```

Review:

- Baseline result JSON exists.
- UART logs exist.
- SMMU-related dmesg/probe output is captured.
- Existing boot blockers are classified as SMMU-related or unrelated.

### MMU720-SYS-002: TRM/spec Traceability Matrix

Create:

- `doc/qbox-mmu720ae-traceability-matrix.md`

Required columns:

| Column | Meaning |
| --- | --- |
| Source | MMU-720AE TRM 109745, SMMUv3 IHI 0070, Zena CSS guide, Linux driver, FVP trace |
| Feature/Register | Register, feature bit, queue record, event code, transaction behavior |
| Reset/Profile Value | Apollo cfg2 value |
| Implementation File | Planned source file |
| Unit Test | Planned test name |
| Runtime Evidence | Direct/full/FVP comparison artifact |

Review:

- Every ID register bit exposed by `zena-css-cfg2` has implementation and test
  rows.
- Any unsupported feature is disabled in profile values.
- No exposed feature lacks a runtime or unit-test row.

### MMU720-SYS-010: Test/CMake Scaffolding

Files:

- `tools/qbox/tests/components/mmu720ae/CMakeLists.txt`
- `tools/qbox/tests/components/mmu720ae/mmu720ae-register-tests.cc`
- `tools/qbox/tests/components/mmu720ae/mmu720ae-queue-tests.cc`
- `tools/qbox/tests/components/mmu720ae/mmu720ae-translation-tests.cc`
- `tools/qbox/tests/components/mmu720ae/mmu720ae-tbu-tests.cc`
- `tools/qbox/tests/components/mmu720ae/mmu720ae-dmi-tests.cc`
- `tools/qbox/tests/components/CMakeLists.txt`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-register-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae' --output-on-failure
```

Expected:

- Build target exists after skeleton.
- Behavior tests fail before implementation and pass after corresponding tasks.

### MMU720-SYS-020: Component Skeleton

Files:

- `tools/qbox/systemc-components/mmu720ae/CMakeLists.txt`
- `tools/qbox/systemc-components/mmu720ae/include/mmu720ae.h`
- `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h`
- `tools/qbox/systemc-components/mmu720ae/src/mmu720ae.cc`
- `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_core.cc`
- `tools/qbox/systemc-components/CMakeLists.txt`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae --parallel 8
git -C tools/qbox diff --check
```

Review fail conditions:

- Any QEMU header included from `mmu720ae_core.h`.
- Socket direction differs from design.
- Module type is not `mmu720ae`.

### MMU720-SYS-030: TCU Register Bank

Minimum tests:

- `ResetProfileMatchesZenaCssCfg2`
- `IdRegistersExposeOnlyImplementedFeatures`
- `Cr0WriteUpdatesCr0Ack`
- `QueueEnableRequiresValidQueueBase`
- `UnsupportedFeatureExposureAbortsElaboration`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-register-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-register-tests' --output-on-failure
```

Review fail conditions:

- Linux probe succeeds because unsupported feature bits are hidden by
  hard-coded driver-specific behavior.
- Register reset values are not traceable to the matrix.

### MMU720-SYS-040: Queue Engine

Minimum tests:

- `CmdSyncCompletesAndAdvancesConsumer`
- `TlbiInvalidatesMatchingTlbEntries`
- `IllegalCommandRaisesGlobalError`
- `EventQueueWritesFaultRecord`
- `CombinedIrqAssertsUntilStatusCleared`
- `PriQueueDisabledWhenProfileDisablesPri`

Current covered tests:

- `CmdqProducerAdvancesConsumerForSyncCompletion`
- `GerrornWriteClearsGlobalErrorBits`
- `EnabledSmmuWritesTranslationFaultEventRecord`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-queue-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-queue-tests' --output-on-failure
```

Review fail conditions:

- Queue completion is driven by host sleep.
- Event/fault is log-only and does not update queue/status.

### MMU720-SYS-050: STE/CD/Table Walker

Minimum tests:

- `BypassSteForwardsIova`
- `AbortSteGeneratesBadSteEvent`
- `Stage1TranslationUsesContextDescriptor`
- `Stage2TranslationAppliesOutputAddressSize`
- `NestedTranslationChainsStage1AndStage2`
- `PermissionFaultWritesEvent`
- `BadCdWritesEvent`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-translation-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-translation-tests' --output-on-failure
```

Review fail conditions:

- Page-table walk reads are not visible through `ptw_socket`.
- Fault result is returned as a generic TLM decode error instead of SMMU event
  when the requester transaction was valid.

### MMU720-SYS-060: TBU Ingress

Minimum tests:

- `TbuAce1UsesSidExtension`
- `TbuAce2UsesProfileDefaultSidWhenMissingExtension`
- `TbuLti00RecordsSecureAttribute`
- `TranslatedWriteReachesDownstreamAddress`
- `PermissionFaultDoesNotReachDownstream`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-tbu-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-tbu-tests' --output-on-failure
```

Review fail conditions:

- All requesters share one hidden SID.
- Missing SID extension is not recorded in stats.

Current covered tests:

- `DisabledSmmuBypassesRequesterTraffic`
- `EnabledSmmuDoesNotSilentlyBypassWithoutWalker`
- `Ace1UsesSidExtensionForFaultEvent`
- `Ace2SocketUsesDefaultSidForFaultEvent`

### MMU720-SYS-070: DMI and Cache Invalidation

Minimum tests:

- `DmiGrantUsesTranslatedRange`
- `DmiGrantIsKeyedBySidAndSsid`
- `TlbiInvalidatesGrantedDmi`
- `SteChangeInvalidatesGrantedDmi`
- `SmmuDisableInvalidatesAllDmi`
- `StaleDmiNegativeCaseCannotWriteOldPhysicalAddress`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-dmi-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-dmi-tests' --output-on-failure
```

Review fail conditions:

- DMI is granted for the downstream physical address without retaining the
  original IOVA key.
- DMI invalidation does not reach upstream requester sockets.

### MMU720-SYS-080: RAS/PMU/SMD_CSR Sideband

Minimum tests:

- `SmdCsrResetValuesMatchZenaCssGuide`
- `SmdCsrSidHighBitsAffectDefaultTbuSid`
- `SmmuPmuInterruptStatusMirrorsCoreState`
- `RasCriticalErrorStatusMirrorsTcuAndTbuState`
- `TcuEdgeTriggeredInterruptClearsOnStatusWrite`

Verification:

```bash
cmake --build tools/qbox/build --target mmu720ae-ras-pmu-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'mmu720ae-ras-pmu-tests' --output-on-failure
```

Review fail conditions:

- SMD_CSR state is duplicated outside `mmu720ae_core`.
- RAS/PMU status can diverge between AP register view and sideband view.

### MMU720-SYS-090: Platform Opt-In Wiring

Verification:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_linux.py \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py \
  scripts/validate_qbox_fvp_rd_aspen_map.py
cmake --build tools/qbox/build --target platforms-vp mmu720ae --parallel 8
QBOX_RDASPEN_SMMU_BACKEND=systemc-mmu720ae \
  python3 scripts/validate_qbox_fvp_rd_aspen_map.py
```

Review fail conditions:

- Boot-regression default switch is presented as FVP-level parity.
- `result.json` does not record backend selection.

### MMU720-SYS-100: Direct Linux Runtime

Command:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_linux.py \
  --smmu-backend systemc-mmu720ae \
  --timeout 600 --post-login-probe \
  --out-dir build/qbox-fvp-rd-aspen/mmu720ae-systemc-direct
```

Pass criteria:

- Linux reaches login.
- `arm-smmu-v3` driver probe appears in dmesg.
- No `failed to enable SMMU interface`, `failed to setup irqs`, or
  `unknown/unsupported TT endianness` appears.
- `/proc/interrupts` shows the SMMU/combined IRQ when fault tests trigger it.
- `result.json` records `smmu_backend = systemc-mmu720ae`.

### MMU720-SYS-110: Synthetic DMA and Fault Runtime

Pass criteria:

- Bypass STE forwards untranslated IOVA only when bypass is programmed.
- Stage 1 translation writes expected physical memory.
- Stage 2 translation writes expected physical memory.
- Abort STE blocks downstream access and writes event record.
- Permission fault blocks downstream access and writes event record.
- TLBI invalidates translation and DMI.
- MSI/IRQ behavior matches selected profile.

The synthetic requester can be a QBox component test first and a Linux-visible
test driver later. Completion requires at least one SystemC/TLM test and one
booted Linux post-login proof.

### MMU720-SYS-120: Full Apollo Runtime

Command:

```bash
python3 scripts/run_qbox_apollo_fvp_full.py \
  --smmu-backend systemc-mmu720ae \
  --timeout 900 \
  --out-dir build/qbox-apollo-fvp/mmu720ae-systemc-full
```

Pass criteria:

- RSE boot markers remain present.
- Safety Island CL0 markers remain present.
- Safety Island CL1 Zephyr markers remain present.
- TF-A BL2/BL31, U-Boot, and Linux markers remain present.
- Any failure is proven unrelated to SMMU by logs and comparison with QEMU
  SMMU backend.

Current evidence:

- Previous SystemC backend pass:
  `build/qbox-apollo-fvp/default-accel-runtime-20260609-004435/result.json`.
- Current build SystemC backend retries:
  `build/qbox-apollo-fvp/mmu720ae-sid-runtime-20260609-005248/`,
  `build/qbox-apollo-fvp/mmu720ae-sid-runtime-retry-20260609-005628/`,
  `build/qbox-apollo-fvp/mmu720ae-sid-runtime-retry2-20260609-010410/`.
  All are blocked at `si_cl1:cpu0_oor` with SI CL1, secure console, and
  primary console logs at 0 bytes.
- Current build QEMU SMMU fallback pass:
  `build/qbox-apollo-fvp/mmu720ae-qemu-backend-compare-20260609-010054/result.json`.
- Current build direct AP-only SystemC pass:
  `build/qbox-fvp-rd-aspen/mmu720ae-sid-direct-20260609-010221/result.json`.

Next debug target:

- Full-system AP power/reset handoff with SystemC backend. AP PC trace with
  tracing enabled showed `ap_cpu_0` only at start-of-simulation hold-reset, but
  AP trace itself perturbs both SystemC and QEMU backend runs, so use it only
  as a debugging hint, not as a pass/fail gate.

### MMU720-SYS-130: FVP Parity Comparison

Create:

- `scripts/compare_fvp_qbox_smmu.py`

Command:

```bash
python3 scripts/compare_fvp_qbox_smmu.py \
  --fvp build/local-apollo-fvp/fvp-boot/result.json \
  --qbox build/qbox-apollo-fvp/mmu720ae-systemc-full/result.json \
  --out build/qbox-apollo-fvp/mmu720ae-systemc-full/smmu-fvp-compare.json
```

Mandatory checks:

- DTS base, size, interrupt, compatible match.
- Linux driver feature summary matches FVP.
- Queue enable sequence reaches same observable state.
- SMMU interrupt behavior matches fault injection.
- `/sys/kernel/iommu_groups` and device attachment behavior match configured
  FVP device set.
- Synthetic fault event class and recovery behavior match FVP.

### MMU720-SYS-140: Documentation Closure

Modify:

- `doc/qbox-fvp-emulation-project.md`
- `doc/apollo-qbox-hardware-ko.md`
- `tools/qbox/platforms/fvp-rd-aspen/README.md`
- `doc/qbox-apollo-fvp-full-system-runbook-ko.md`

Pass criteria:

- Documentation states whether default backend is QEMU or SystemC.
- Remaining unsupported features are listed as disabled or fidelity gaps.
- Latest verification artifact paths are recorded.

### MMU720-SYS-150: Default Backend Switch

Completed as a boot-regression default switch before full FVP parity. This is
allowed only with explicit documentation that FVP-level parity remains open.

Pass criteria:

- `QBOX_RDASPEN_SMMU_BACKEND` default becomes `systemc-mmu720ae`.
- Apollo full-system runner default becomes `systemc-mmu720ae`.
- QEMU backend remains selectable as `qemu-arm-smmuv3`.
- Validators expect SystemC backend by default and allow QEMU backend only when
  explicitly selected.

## Verification Criteria Summary

| Gate | Command or Artifact | Required Result |
| --- | --- | --- |
| V0 Docs | `rg -n "TO[D]O|TB[D]|[s]tub-only|[b]ypass-only" doc/qbox-mmu720ae-systemc-*.md` | No placeholder or register-bypass shortcut completion language |
| V1 Build | `cmake --build tools/qbox/build --target mmu720ae --parallel 8` | Pass |
| V2 Unit | `ctest --test-dir tools/qbox/build -R 'mmu720ae' --output-on-failure` | Pass |
| V3 Static | `git -C tools/qbox diff --check` | Pass |
| V4 Map | `python3 scripts/validate_qbox_fvp_rd_aspen_map.py` | Pass for selected backend |
| V5 Direct Runtime | `run_qbox_fvp_rd_aspen_linux.py --smmu-backend systemc-mmu720ae --post-login-probe` | Login, SMMU probe, no driver enable failure |
| V6 DMA/Fault | Synthetic SystemC and Linux post-login tests | Translation and negative fault behavior pass |
| V7 Full Runtime | `run_qbox_apollo_fvp_full.py --smmu-backend systemc-mmu720ae` | Existing full-system markers preserved |
| V8 FVP Compare | `scripts/compare_fvp_qbox_smmu.py` | No mandatory mismatch |
| V9 Docs Closure | Updated roadmap/runbook/hardware docs | Backend status and gaps recorded |

## Implementation Review Checklist

- [ ] Register values are traceable to MMU-720AE TRM, SMMUv3 spec, Zena CSS
  guide, or FVP trace.
- [ ] Unsupported features are not exposed through ID registers.
- [ ] Queue completion is simulation-event driven.
- [ ] Faults update SMMU-visible status and event queue.
- [ ] TBU path carries SID/SSID/security attributes.
- [ ] DMI is keyed by translation context and invalidated on every relevant
  command or state change.
- [ ] Runtime evidence is file-backed and not tmux-only.
- [ ] FVP comparison is performed before claiming FVP-level parity.

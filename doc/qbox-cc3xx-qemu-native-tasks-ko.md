# QBox CC3XX QEMU-Native Backend Tasks

작성일: 2026-06-04

상태: 구현 및 검증 완료

이 문서는 `doc/qbox-cc3xx-qemu-native-spec-ko.md`와
`doc/qbox-cc3xx-qemu-native-design-ko.md`의 구현 task backlog다. 구현 시
`superpowers:subagent-driven-development` 방식으로 task 단위 implementer,
spec reviewer, quality reviewer를 분리한다.

## Task Board

| ID | Task | Dependencies | 완료 기준 |
| --- | --- | --- | --- |
| CC3XX-QEMU-001 | Baseline evidence lock | 없음 | 기존 `cc3xx-tests`, baseline timing artifact, dirty state 기록 |
| CC3XX-QEMU-010 | `cc3xx_core` API skeleton | 001 | core header가 SystemC/TLM/CCI/QEMU include 없이 빌드 |
| CC3XX-QEMU-020 | SystemC wrapper migration | 010 | 기존 `cc3xx-tests` 통과 |
| CC3XX-QEMU-030 | Core-only tests | 020 | reset/HASH/AES/CMAC/PKA/DMA/status tests 통과 |
| CC3XX-QEMU-040 | `qemu_cc3xx` skeleton | 030 | `qemu_cc3xx` build target 생성 및 build pass |
| CC3XX-QEMU-050 | QEMU MemoryRegionOps access | 040 | read/write callback이 core로 들어가고 qemu test pass |
| CC3XX-QEMU-060 | DMA adapter | 050 | QEMU AddressSpace first, TLM fallback stats 기록 |
| CC3XX-QEMU-070 | Lua backend selection | 060 | `QBOX_RDASPEN_CC3XX_BACKEND`로 backend 선택 |
| CC3XX-QEMU-080 | Runner options | 070 | `--cc3xx-qemu-native-backend`와 result label 기록 |
| CC3XX-QEMU-090 | RSE runtime validation | 080 | marker parity와 10% 이상 성능 개선 |
| CC3XX-QEMU-100 | Full-system regression | 090 | full live run에서 blocker 없음 |
| CC3XX-QEMU-110 | Documentation closure | 100 | README/runbook/fidelity notes 갱신 |

현재 상태:

| ID | 상태 | 근거 |
| --- | --- | --- |
| 001-080 | 완료 | `qemu_cc3xx`, `cc3xx_core-tests`, runner/Lua/tmux option 구현 |
| 090 | 완료 | `build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-001939/rse/result.json` |
| 100 | 완료 | `build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/result.json` |
| 110 | 완료 | runbook/README/spec/design/plan/tasks 갱신 |

## Detailed Tasks

### CC3XX-QEMU-001: Baseline Evidence Lock

Files:

- Read: `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`
- Read: `tools/qbox/tests/components/cc3xx/cc3xx-tests.cc`
- Read: `build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604/result.json`
- Read: `build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604/result.json`

Steps:

- [x] `git status --short`와 `git -C tools/qbox status --short`를 기록한다.
- [x] `cc3xx-tests`를 실행한다.
- [x] baseline과 local-MMIO timing을 `analyze_qbox_rse_boot_timing.py`로 다시
  요약한다.
- [x] 이후 구현 report에서 이 값을 regression 기준으로 사용한다.

Commands:

```bash
git status --short
git -C tools/qbox status --short
ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure
python3 scripts/analyze_qbox_rse_boot_timing.py \
  build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604/result.json \
  build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604/result.json
```

### CC3XX-QEMU-010: `cc3xx_core` API Skeleton

Files:

- Create: `tools/qbox/systemc-components/cc3xx/include/cc3xx_core.h`
- Modify: `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`

Required shape:

```cpp
namespace qbox {
namespace cc3xx {

struct memory_if {
    virtual ~memory_if() = default;
    virtual bool read(uint64_t address, uint8_t* data, uint32_t len) = 0;
    virtual bool write(uint64_t address, const uint8_t* data, uint32_t len) = 0;
};

class core {
public:
    explicit core(std::string name);
    void set_memory(memory_if* memory);
    void reset(bool count_stats);
    access_result read(uint64_t offset, uint8_t* data, uint32_t len,
                       bool debug);
    access_result write(uint64_t offset, const uint8_t* data, uint32_t len,
                        bool debug);
};

} // namespace cc3xx
} // namespace qbox
```

Review checks:

- [x] `cc3xx_core.h`에 `<systemc>`, `<tlm>`, `<cci_configuration>`,
  `<qemu-instance.h>` include가 없다.
- [x] register constants와 side-effect helpers가 wrapper가 아닌 core에 있다.
- [x] stats counters는 core에 있고 file path/open error handling은 wrapper에 있다.

### CC3XX-QEMU-020: SystemC Wrapper Migration

Files:

- Modify: `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`
- Modify: `tools/qbox/systemc-components/cc3xx/src/cc3xx.cc` only if module
  registration changes

Steps:

- [x] `cc3xx` wrapper에 `qbox::cc3xx::core m_core`를 추가한다.
- [x] wrapper-local `systemc_memory_if`가 `initiator_socket->b_transport()`로
  DMA read/write를 구현한다.
- [x] `b_transport()`와 `transport_dbg()`가 TLM response를 core result로부터
  변환한다.
- [x] `doreset(true)`가 `m_core.reset(true)`와 stats-file flush를 수행한다.

Commands:

```bash
cmake --build tools/qbox/build --target cc3xx-tests --parallel 8
ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure
```

### CC3XX-QEMU-030: Core-only Tests

Files:

- Create: `tools/qbox/tests/components/cc3xx/cc3xx_core-tests.cc`
- Modify: `tools/qbox/tests/components/cc3xx/CMakeLists.txt`

Minimum tests:

- [x] `ResetInitializesReadableStatus`
- [x] `UnsupportedAddressReturnsAddressError`
- [x] `DebugReadDoesNotAdvancePkaReadCursor`
- [x] `HashStateRestoreMatchesSystemCFixture`
- [x] `AesCtrDmaUsesMemoryInterface`
- [x] `AesEcbDecryptUsesMemoryInterface`
- [x] `CmacFinishWritesExpectedTag`
- [x] `HostRgfIcrClearsInterruptBits`
- [x] `StatsHistogramCountsRegisterAccesses`

Commands:

```bash
cmake --build tools/qbox/build --target cc3xx_core-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'cc3xx_core-tests' --output-on-failure
```

### CC3XX-QEMU-040: `qemu_cc3xx` Skeleton

Files:

- Create: `tools/qbox/qemu-components/cc3xx_native/CMakeLists.txt`
- Create: `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
- Create: `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc`
- Modify: `tools/qbox/qemu-components/CMakeLists.txt`

Implementation requirements:

- [x] module type is `qemu_cc3xx`.
- [x] constructor accepts `sc_core::sc_object*` and resolves `QemuInstance`.
- [x] creates `qemu::MemoryRegionOps` read/write callbacks.
- [x] creates `qemu::MemoryRegion` size `0x2000`.
- [x] exposes `QemuTargetSocket<> target_socket` via `init_with_mr()`.
- [x] exposes `initiator_socket` for DMA fallback.
- [x] exposes the same trace/stats parameter surface as `cc3xx` and connects it
  to core trace/stats config.

Commands:

```bash
cmake --build tools/qbox/build --target qemu_cc3xx --parallel 8
```

### CC3XX-QEMU-050: QEMU MemoryRegionOps Access

Files:

- Modify: `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
- Modify: `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc`
- Create: `tools/qbox/tests/components/cc3xx/qemu_cc3xx-tests.cc`
- Modify: `tools/qbox/tests/components/cc3xx/CMakeLists.txt`

Steps:

- [x] qemu read callback maps `(addr, size, attrs)` to `core.read()`.
- [x] qemu write callback maps `(addr, data, size, attrs)` to `core.write()`.
- [ ] little-endian data packing is tested for 1/2/4/8 byte accesses.
- [x] unsupported offset returns decode/error status.
- [x] `qemu_cc3xx-tests` links the QEMU wrapper, shared `cc3xx_core`, and the
  existing component test helpers without duplicating register semantics.

후속 test debt: 현재 `qemu_cc3xx-tests`는 build/link smoke 수준이다. 실제
QEMU `MemoryRegionOps` read/write packing은 RSE runtime evidence로 보완했지만,
unit/integration test에서 직접 검증하는 작업은 별도 task로 남긴다.

Commands:

```bash
cmake --build tools/qbox/build --target qemu_cc3xx-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'qemu_cc3xx-tests' --output-on-failure
```

### CC3XX-QEMU-060: DMA Adapter

Files:

- Modify: `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
- Modify: `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc`

Steps:

- [x] `qemu_dma_memory_if` uses `AddressSpace::read/write()` first.
- [x] fallback path uses controlled SystemC handoff, not direct unsafe recursion.
- [x] stats include qemu DMA reads/writes and fallback DMA reads/writes.
- [x] RSE BL1_2 HASH DMA path still produces same SHA result.

### CC3XX-QEMU-070: Lua Backend Selection

Files:

- Modify: `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`

Steps:

- [x] Add `cc3xx_backend = getenv_or("QBOX_RDASPEN_CC3XX_BACKEND", "systemc")`.
- [x] Assert allowed values are `systemc` and `qemu-native`.
- [x] Existing `rse_cc3xx` SystemC block is active only for `systemc`.
- [x] New `rse_cc3xx_native` block is active only for `qemu-native`.
- [x] `remote_crypto_router` remains present for local crypto.
- [x] KMU `initiator_socket` still binds to the CC3XX route.

### CC3XX-QEMU-080: Runner Options

Files:

- Modify: `scripts/run_qbox_fvp_rd_aspen_rse.py`
- Modify: `scripts/run_qbox_apollo_fvp_full.py`
- Modify: `scripts/run_qbox_apollo_fvp_full_tmux.sh`

Steps:

- [x] Add `--cc3xx-qemu-native-backend`.
- [x] Set `QBOX_RDASPEN_CC3XX_BACKEND=qemu-native` when enabled.
- [x] Record selection in `result.json`.
- [x] Add `qemu-native` fidelity label.
- [x] Forward option from full-system and tmux wrappers.

Commands:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py
```

### CC3XX-QEMU-090: RSE Runtime Validation

Files:

- Generated: `build/qbox-apollo-fvp/cc3xx-qemu-backend-<run-id>/`

Commands:

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
E=build/qbox-apollo-fvp/cc3xx-qemu-backend-${RUN_ID}

python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build --cc3xx-stats --cc3xx-stats-interval 65536 \
  --timeout 230 --ignore-fail-patterns \
  --out-dir ${E}/rse-systemc-baseline

python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build --cc3xx-stats --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --timeout 230 --ignore-fail-patterns \
  --out-dir ${E}/rse-local-mmio

python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build --cc3xx-stats --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend \
  --timeout 230 --ignore-fail-patterns \
  --out-dir ${E}/rse-qemu-native

python3 scripts/analyze_qbox_rse_boot_timing.py --markdown \
  ${E}/rse-systemc-baseline/result.json \
  ${E}/rse-local-mmio/result.json \
  ${E}/rse-qemu-native/result.json \
  --output ${E}/rse-boot-timing.md
```

Pass criteria:

- [x] `rse_bl2_decrypted` marker seen.
- [x] `rse_bl2_validated` marker seen.
- [x] `rse_jump_bl2` marker seen.
- [x] `rse_image_4_loaded` marker seen.
- [x] `rse-systemc-baseline`, `rse-local-mmio`, `rse-qemu-native` 모두
  `rse-cc3xx-stats.json`을 남긴다.
- [x] validation delta is at least 10% lower than local-MMIO fastpath.

### CC3XX-QEMU-100: Full-System Regression

Commands:

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
E=build/qbox-apollo-fvp/cc3xx-qemu-backend-${RUN_ID}

python3 scripts/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --skip-build --timeout 2400 \
  --rootfs-bootargs-profile none --post-login-probe \
  --cc3xx-stats --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend \
  --out-dir ${E}/full-live-cl0-cl1
```

Pass criteria:

- [ ] `passed == true`.
- [ ] `blocker == null`.
- [ ] RSE, SI CL0, SI CL1, AP firmware, U-Boot, Linux marker groups pass.
- [ ] `fidelity_labels.rse_cc3xx` contains `qemu-native`.

검증 결과:

```text
build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/result.json
passed: true
blocker: null
post_login_probe.complete: true
```

### CC3XX-QEMU-110: Documentation Closure

Files:

- Modify: `doc/qbox-rse-boot-slow-path-analysis-ko.md`
- Modify: `tools/qbox/platforms/fvp-rd-aspen/README.md`
- Modify as needed: `doc/qbox-fvp-emulation-project.md`

Steps:

- [x] Describe backend selection and default behavior.
- [x] Record performance result table.
- [x] Record fidelity gaps and when to disable QEMU-native backend.
- [x] Add reproduction commands.

## Final Verification Bundle

The implementation is review-ready only when the final report points to:

```text
build/qbox-apollo-fvp/cc3xx-qemu-backend-<run-id>/
  rse-systemc-baseline/result.json
  rse-local-mmio/result.json
  rse-qemu-native/result.json
  rse-qemu-native/rse-cc3xx-stats.json
  rse-boot-timing.md
  full-live-cl0-cl1/result.json
  full-live-cl0-cl1/rd-aspen-result.json
  full-live-cl0-cl1/coverage-audit.json
```

최종 구현 검증 bundle은 다음 경로에 있다.

```text
build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-001939/rse/
build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/
build/qbox-apollo-fvp/direct-guardrail-20260605-004025/
```

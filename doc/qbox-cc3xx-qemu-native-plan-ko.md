# QBox CC3XX QEMU-Native Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task by
> task in the current session. Steps use checkbox (`- [ ]`) syntax for
> tracking.

작성일: 2026-06-04

상태: 구현 및 검증 완료

**Goal:** `cc3xx_core`를 분리하고 QEMU-native CC3XX backend를 opt-in으로
추가해 RSE BL1_2 BL2 validation 시간을 줄인다.

**Architecture:** 기존 SystemC `cc3xx`와 새 `qemu_cc3xx`가 같은
`cc3xx_core`를 공유한다. CPU MMIO hot path는 QEMU `MemoryRegionOps`로
처리하고, DMA는 QEMU `AddressSpace` first, 제한된 TLM fallback 구조를 쓴다.

**Tech Stack:** C++14, SystemC/TLM-2.0, QBox qemu-components, libqemu-cxx,
Lua platform config, CMake/CTest, Python QBox runners.

---

## 구현 순서

### Phase 0: Baseline 고정

- [x] 기존 dirty state를 확인하고 unrelated 변경을 건드리지 않는다.
- [x] 현재 RSE SystemC baseline, local-MMIO fastpath 결과를 보존한다.
- [x] `cc3xx-tests` 현재 pass 여부를 확인한다.

검증:

```bash
git status --short
git -C tools/qbox status --short
ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure
python3 scripts/analyze_qbox_rse_boot_timing.py \
  build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604/result.json \
  build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604/result.json
```

### Phase 1: `cc3xx_core` 분리

Files:

- Create: `tools/qbox/systemc-components/cc3xx/include/cc3xx_core.h`
- Modify: `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`
- Modify: `tools/qbox/systemc-components/cc3xx/CMakeLists.txt` only if the
  split requires a non-header source file
- Test: `tools/qbox/tests/components/cc3xx/cc3xx-tests.cc`

Steps:

- [x] `cc3xx.h`의 private register constants, state, stats, PKA/SHA/AES/CMAC
  helpers, `write32()`, `access()`를 `qbox::cc3xx::core`로 이동한다.
- [x] `mem_read()`/`mem_write()`를 `memory_if` callback으로 바꾼다.
- [x] CCI params, TLM sockets, reset socket, stats-file open/write error
  reporting은 SystemC wrapper에 남긴다.
- [x] `cc3xx` wrapper가 TLM payload를 core `read/write`로 변환하게 한다.
- [x] 기존 `cc3xx-tests`가 source 변경 없이 통과해야 한다.

검증:

```bash
cmake --build tools/qbox/build --target cc3xx-tests --parallel 8
ctest --test-dir tools/qbox/build -R '^cc3xx-tests$' --output-on-failure
git -C tools/qbox diff --check
```

### Phase 2: Core-only Tests 추가

Files:

- Create: `tools/qbox/tests/components/cc3xx/cc3xx_core-tests.cc`
- Modify: `tools/qbox/tests/components/cc3xx/CMakeLists.txt`

Test coverage:

- reset/RNG readiness
- unsupported address and unsupported command
- aligned 32-bit write side effects vs byte/halfword raw writes
- PKA SRAM read cursor debug/non-debug behavior
- HASH state restore and final block
- AES CTR in-place DMA
- AES ECB decrypt path
- CMAC finish path
- `HOST_RGF_IRR`/`HOST_RGF_ICR` clear semantics
- stats histogram update

검증:

```bash
cmake --build tools/qbox/build --target cc3xx_core-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'cc3xx_core-tests' --output-on-failure
```

### Phase 3: QEMU-native Wrapper Skeleton

Files:

- Create: `tools/qbox/qemu-components/cc3xx_native/CMakeLists.txt`
- Create: `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
- Create: `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc`
- Modify: `tools/qbox/qemu-components/CMakeLists.txt`

Steps:

- [x] `qemu_cc3xx(sc_module_name, sc_object*)` constructor에서
  `QemuInstance&`를 받는다.
- [x] `qemu::MemoryRegion`과 `MemoryRegionOps`를 만들고 read/write callback을
  등록한다.
- [x] `QemuTargetSocket::init_with_mr()`로 SystemC/TLM target view를 노출한다.
- [x] window size는 `0x2000`으로 제한한다.
- [x] unsupported access는 QEMU `MemTxDecodeError` 또는 `MemTxError`로
  명확히 반환한다.
- [x] 기존 `cc3xx`와 같은 trace/stats parameter surface를 노출하고 core
  trace/stats config로 연결한다.

검증:

```bash
cmake --build tools/qbox/build --target qemu_cc3xx --parallel 8
```

### Phase 4: QEMU DMA Adapter

Files:

- Modify: `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
- Modify: `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc`

Steps:

- [x] QEMU `AddressSpace::read/write()` 기반 `memory_if`를 구현한다.
- [x] 실패 시 제한된 TLM fallback을 추가한다.
- [x] fallback 횟수와 byte 수를 stats에 기록한다.
- [x] QEMU iothread/SystemC thread ownership 전환을 명시한다.

검증:

```bash
cmake --build tools/qbox/build --target qemu_cc3xx cc3xx-tests --parallel 8
ctest --test-dir tools/qbox/build -R 'cc3xx' --output-on-failure
```

### Phase 5: Platform/Runner Opt-In

Files:

- Modify: `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- Modify: `scripts/run_qbox_fvp_rd_aspen_rse.py`
- Modify: `scripts/run_qbox_apollo_fvp_full.py`
- Modify: `scripts/run_qbox_apollo_fvp_full_tmux.sh`
- Modify: `tools/qbox/platforms/fvp-rd-aspen/README.md`

Steps:

- [x] Lua에 `QBOX_RDASPEN_CC3XX_BACKEND=systemc|qemu-native`를 추가한다.
- [x] default는 `systemc`로 둔다.
- [x] runner에 `--cc3xx-qemu-native-backend`를 추가한다.
- [x] `result.json`에 backend selection과 fidelity label을 기록한다.
- [x] tmux runner에도 같은 옵션을 pass-through한다.

검증:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py
cmake --build tools/qbox/build --target platforms-vp remote_cpu --parallel 8
```

### Phase 6: RSE Runtime 성능 검증

Run bundle:

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

Pass 기준:

- `rse_bl2_decrypted`, `rse_bl2_validated`, `rse_jump_bl2`,
  `rse_image_4_loaded` marker가 유지된다. 완료.
- `rse-cc3xx-stats.json`이 존재한다. 완료.
- QEMU-native validation delta가 local-MMIO run보다 10% 이상 낮다. 완료:
  151.321초에서 133.339초로 감소.
- stats counter가 SystemC backend와 같은 operation class를 보여준다.

### Phase 7: Full-System Regression

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
E=build/qbox-apollo-fvp/cc3xx-qemu-backend-${RUN_ID}

python3 scripts/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --skip-build --timeout 2400 \
  --rootfs-bootargs-profile none --post-login-probe \
  --cc3xx-stats --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend \
  --out-dir ${E}/full-live-cl0-cl1

python3 scripts/audit_qbox_fvp_rd_aspen_coverage.py \
  --runtime-result ${E}/full-live-cl0-cl1/rd-aspen-result.json \
  --runtime-log ${E}/full-live-cl0-cl1/qbox-platform.log \
  --output ${E}/full-live-cl0-cl1/coverage-audit.json
```

Pass 기준:

- full run `passed == true`, `blocker == null`.
- backend label이 `qemu-native`를 기록한다.
- RSE, SI CL0, SI CL1, AP firmware, U-Boot, Linux marker가 유지된다.

상태: `build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full`에서
`passed == true`, `blocker == null`, post-login probe 완료. Coverage audit은
`coverage-audit.json`을 생성했지만 일부 runtime-evidence 항목 부족으로 exit 1을
반환한다.

### Phase 8: Review Closure

- [x] Spec compliance review를 수행한다.
- [x] Code quality review를 수행한다.
- [x] `git diff --check`와 relevant tests를 다시 실행한다.
- [ ] docs/runbook에 새 backend 사용법과 fidelity gap을 업데이트한다.

## 리뷰 계획

리뷰는 두 단계로 진행한다.

1. **Spec compliance review**
   - `cc3xx_core` dependency boundary 확인
   - opt-in backend 확인
   - secure boot skip 없음 확인
   - RSE window `0x50154000:0x2000` 확인
   - runtime evidence bundle 확인
2. **Code quality review**
   - duplicated register semantics 없음 확인
   - QEMU/SystemC ownership 전환 안전성 확인
   - unsupported access response와 stats error path 확인
   - tests가 wrapper별 edge case를 실제로 검증하는지 확인

## Blocker 처리

| Blocker | 대응 |
| --- | --- |
| QemuMrHint alias가 설치되지 않음 | direct root subregion API를 별도 task로 추가한다. |
| QEMU AddressSpace DMA가 일부 RSE window를 못 읽음 | 해당 window만 TLM fallback으로 분류하고 fallback stats를 기록한다. |
| local-MMIO 대비 10% 개선 미달 | remaining overhead를 stats로 재분석하고 LMOTS hash coalescing을 다음 plan으로 분리한다. |
| full-system regression | SystemC default backend로 guardrail을 재실행해 backend-specific 문제인지 분리한다. |

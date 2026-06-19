# QBox Platform Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `tools/qbox` upstream diff 중 Apollo/RD-Aspen/RSE 의미가 강한 변경을 `tools/qbox-platform`으로 이동하고, QBox core에는 재사용 가능한 generic hook, DMI, RemotePass, libqemu bridge만 남긴다.

**Architecture:** QBox core는 platform-neutral CPU/PC event hook, DMI/file-backed memory, MemTxAttrs, reset/load/remote transport를 제공한다. `qbox-platform`은 RSE BL1/BL2 semantic acceleration, RSE crypto/image helper, Apollo fastpath policy, FVP aperture policy, Apollo/RD-Aspen remote CPU wrapper를 소유한다.

**Tech Stack:** C++14, SystemC/TLM-2.0, CCI, Lua platform config, CMake, libqemu/QEMU, GoogleTest/CTest, project scripts under `scripts/`.

---

## 배경

기준 분석 문서는 `doc/qbox-upstream-diff-analysis-ko.md`이다. 해당 문서에서 `git -C tools/qbox diff 5a78034faf26 --stat` 기준 50개 변경 파일을 조사했고, 다음 항목을 `qbox-platform` 분리 후보로 판정했다.

| 우선순위 | 현재 위치 | 분리 대상 | 목표 위치 |
| --- | --- | --- | --- |
| 1 | `tools/qbox/qemu-components/common/include/cpu.h` | RSE/BL2 semantic acceleration, LMS/P-256/MCUboot image 처리, RSE delay/load/hash/signature hook | `tools/qbox-platform/qemu-components/rse_cpu_accel/` |
| 2 | `tools/qbox/qemu-components/common/include/rse_lms_accel.h` | RSE LMS helper | `tools/qbox-platform/qemu-components/rse_cpu_accel/include/` |
| 3 | `tools/qbox/qemu-components/common/include/rse_mcuboot_image.h` | MCUboot image/TLV helper | `tools/qbox-platform/qemu-components/rse_cpu_accel/include/` |
| 4 | `tools/qbox/qemu-components/common/include/rse_p256_ecdsa.h` | RSE BL2 P-256 ECDSA helper | `tools/qbox-platform/qemu-components/rse_cpu_accel/include/` |
| 5 | `tools/qbox/qemu-components/common/include/cc3xx_core.h` | CC3XX register/crypto core duplicate ownership | `tools/qbox-platform/systemc-components/cc3xx/include/cc3xx_core.h` |
| 6 | `tools/qbox/qemu-components/common/include/ports/initiator.h` | env 기반 Apollo/RSE fastpath policy와 direct-file alias policy | generic API는 core 유지, policy는 `tools/qbox-platform/platforms/*`와 runner로 이동 |
| 7 | `tools/qbox/qemu-components/common/include/ports/target.h`, `tools/qbox/systemc-components/uart/uart-pl011/include/uart-pl011.h` | FVP-style wide aperture mirror policy | core에는 opt-in parameter, Apollo/RD-Aspen Lua에서 enable |
| 8 | `tools/qbox/platforms/cortex-m55-remote/*` | Apollo 검증에 묶인 remote M55 wrapper와 tests | generic sample은 core 유지, Apollo/RSE wrapper와 tests는 `tools/qbox-platform` |

## 원칙

- QBox core에는 `rse`, `bl2`, `mcuboot`, `lms`, `p256`, `cc3xx` 같은 Apollo/RSE 전용 이름이 새로 남지 않아야 한다.
- Runtime behavior는 단계별로 유지한다. 한 단계가 끝날 때마다 RSE 단독 또는 Apollo full-system boot evidence를 남긴다.
- cross-repository move는 소유 repo별로 처리한다. `tools/qbox`에서 삭제되는 파일과 `tools/qbox-platform`에 추가되는 파일은 각각 해당 submodule Git 상태에서 확인한다.
- `qbox-platform`이 QBox core internals를 무단 복사하지 않도록, core에는 필요한 최소 generic interface만 추가한다.
- 성능 옵션 기본값은 현재 Apollo 실행 경로와 동일하게 유지한다. 기능 분리 후에도 RSE 첫 부팅 시간이 악화되면 해당 단계는 되돌리지 않고 profile로 원인을 분리한다.

## 리뷰 결과 반영 사항

| 관점 | 검토 결과 | 계획 반영 |
| --- | --- | --- |
| Architect | `QemuCpu`에 RSE 구현을 남기지 않는 방향은 맞지만, observer ownership/lifetime 계약이 명확해야 한다. | Milestone 2에 non-owning observer 등록/해제 계약과 wrapper-owned `RseCpuAccel` lifetime을 추가했다. |
| Architect | 기존 `remote_cpu` executable/module 이름을 재사용하면 core sample과 Apollo wrapper가 충돌할 수 있다. | Apollo/RD-Aspen 전용 executable은 `apollo_rse_remote_cpu`, module은 `ApolloRseRemoteCPU`로 고정했다. |
| SW | `cpu.h`가 이미 과대해졌으므로 새 RSE logic은 header-only로 옮기면 안 된다. | Milestone 2에 `rse_cpu_accel.cc`, `rse_cpu_accel_profile.cc` source ownership과 namespace 규칙을 추가했다. |
| SW | 현재 `tools/qbox-platform/CMakeLists.txt`에는 `add_subdirectory(cortex-m55-remote)` 형태의 경로가 들어갈 수 있으나 실제 platform layout과 맞지 않을 수 있다. | Milestone 2에 `add_subdirectory(platforms/cortex-m55-remote)`로 경로를 명시하고 dangling CMake path 검사를 추가했다. |
| HW | FVP-style aperture mirror를 read/write 모두에 default 적용하면 실제 register side effect와 다를 수 있다. | Milestone 5를 read-only peripheral-ID mirror 우선으로 바꾸고 write mirror는 증거가 있는 장치에만 opt-in하도록 수정했다. |
| HW | BL2/RSE symbol address는 firmware revision에 따라 바뀔 수 있다. | Milestone 2에 acceleration enable 전 ELF symbol/default address 검증과 mismatch fallback 기준을 추가했다. |
| Test | 단순 grep만으로는 core 경계 회귀를 충분히 막지 못한다. | Milestone 7에 boundary audit 금지 패턴과 core/qbox-platform CTest 범위를 확대했다. |
| Test | 성능 fastpath 이동은 boot 성공뿐 아니라 profile counter와 SRAM backing mode로 확인해야 한다. | Milestone 4/7에 `check_qbox_sram_dmi_fastpath.py`, profile counter, direct-file alias negative check를 acceptance에 포함했다. |

## 완료 기준

- `tools/qbox/qemu-components/common/include/cpu.h`에서 RSE/BL2/LMS/P-256/MCUboot semantic acceleration 코드가 제거된다.
- `tools/qbox/qemu-components/common/include/cc3xx_core.h`, `rse_lms_accel.h`, `rse_mcuboot_image.h`, `rse_p256_ecdsa.h`가 없어지고, 동일 기능은 `tools/qbox-platform`에서만 빌드된다.
- QBox core에 남는 CPU 변경은 PC-entry callback, CPU state access, guest memory access helper, observer registration 같은 generic hook뿐이다.
- `tools/qbox`에는 `QBOX_RDASPEN_RSE_*`, `QBOX_APOLLO_FULL_*`, RSE BL2 symbol name, MCUboot helper, CC3XX model implementation이 남지 않는다.
- `python3 scripts/test/audit_qbox_core_boundary.py`가 통과한다.
- `./local-build.sh qbox`가 `build/local-apollo-fvp/work/qbox-platform` 아래에서 성공한다.
- `ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'cc3xx|rse_lms|rse_mcuboot|rse_p256|cortex_m55_remote_dmi' --output-on-failure`가 성공한다.
- `python3 scripts/run/run_qbox_apollo_fvp_full.py --si-mode live-cl0-cl1 --timeout 600 --post-login-probe`가 성공하거나, 실패 시 분리와 무관한 기존 runtime blocker로 분류된 evidence를 남긴다.

## Milestone 0: 기준선 고정

- [ ] 현재 상태를 기록한다.
  ```bash
  git status --short
  git -C tools/qbox status --short
  git -C tools/qbox-platform status --short
  git -C tools/qbox diff 5a78034faf26 --stat
  ```
- [ ] 현재 QBox platform build 기준선을 확보한다.
  ```bash
  ./local-build.sh qbox
  ```
- [ ] 현재 Apollo/QBox map 및 core boundary 검사 결과를 저장한다.
  ```bash
  python3 scripts/test/audit_qbox_core_boundary.py --json \
    > build/qbox-apollo-fvp/qbox-core-boundary-before.json
  python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
    --out build/qbox-apollo-fvp/full-map-before.json
  ```
- [ ] 현재 RSE/full-system boot 기준선을 확보한다.
  ```bash
  python3 scripts/run/run_qbox_apollo_fvp_full.py \
    --si-mode live-cl0-cl1 \
    --timeout 600 \
    --post-login-probe \
    --out-dir build/qbox-apollo-fvp/full-before-platform-separation
  ```

## Milestone 1: RSE helper와 CC3XX core 소유권 정리

- [ ] `qbox-platform`에 RSE CPU acceleration helper target을 만든다.
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/CMakeLists.txt`
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/include/rse_lms_accel.h`
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/include/rse_mcuboot_image.h`
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/include/rse_p256_ecdsa.h`
  - 수정: `tools/qbox-platform/qemu-components/CMakeLists.txt`
- [ ] `tools/qbox-platform/tests/components/cc3xx/CMakeLists.txt`에서 RSE helper tests의 include path를 `QBOX_CORE_SOURCE_DIR`가 아니라 `QBOX_PLATFORM_SOURCE_DIR/qemu-components/rse_cpu_accel/include`로 변경한다.
- [ ] `cc3xx_core`의 canonical location을 `tools/qbox-platform/systemc-components/cc3xx/include/cc3xx_core.h`로 확정한다.
  - 수정: `tools/qbox-platform/qemu-components/cc3xx_native/include/qemu_cc3xx.h`
  - 수정: `tools/qbox-platform/systemc-components/cc3xx/include/cc3xx.h`
  - 수정: `tools/qbox-platform/tests/components/cc3xx/cc3xx_core-tests.cc`
- [ ] QBox core에서 helper 파일을 삭제한다.
  - 삭제: `tools/qbox/qemu-components/common/include/rse_lms_accel.h`
  - 삭제: `tools/qbox/qemu-components/common/include/rse_mcuboot_image.h`
  - 삭제: `tools/qbox/qemu-components/common/include/rse_p256_ecdsa.h`
  - 삭제 대기: `tools/qbox/qemu-components/common/include/cc3xx_core.h`
- [ ] 이 단계에서는 `cpu.h`가 아직 RSE helper를 include할 수 있으므로 `cc3xx_core.h` 삭제는 Milestone 2 이후에 수행한다.
- [ ] 검증한다.
  ```bash
  cmake --build build/local-apollo-fvp/work/qbox-platform \
    --target cc3xx_core-tests rse_lms_accel-tests \
             rse_mcuboot_image-tests rse_p256_ecdsa-tests \
    --parallel 8
  ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
    -R 'cc3xx_core|rse_lms|rse_mcuboot|rse_p256' \
    --output-on-failure
  ```

## Milestone 2: QemuCpu generic hook와 RSE CPU acceleration 분리

- [ ] QBox core에 platform-neutral PC-entry observer interface를 추가한다.
  - 추가: `tools/qbox/qemu-components/common/include/cpu-pc-entry-observer.h`
  - 수정: `tools/qbox/qemu-components/common/include/cpu.h`
- [ ] interface는 RSE 이름을 포함하지 않는다. 최소 API는 다음 의미를 가진다.
  ```cpp
  class QemuCpuPcEntryObserver {
  public:
      virtual ~QemuCpuPcEntryObserver() = default;
      virtual bool enabled() const = 0;
      virtual void configure_pc_watches(qemu::Cpu& cpu) = 0;
      virtual bool on_pc_entry(uint64_t pc) = 0;
      virtual void write_profile_json(std::ostream& os) const = 0;
  };
  ```
- [ ] observer ownership/lifetime 계약을 `cpu-pc-entry-observer.h` 주석과 `QemuCpu` API에 고정한다.
  ```cpp
  void register_pc_entry_observer(QemuCpuPcEntryObserver& observer);
  void unregister_pc_entry_observer(QemuCpuPcEntryObserver& observer);
  ```
  `QemuCpu`는 observer를 소유하지 않는다. `ApolloRseRemoteCPU`가 `RseCpuAccel`을 멤버로 소유하고, CPU보다 먼저 observer를 등록하며 destructor에서 해제한다.
- [ ] `QemuCpu`에는 observer vector와 no-op default만 둔다.
  - 유지: `trace_pc`, `trace_exception_state`, `reset_power_on`, generic `hotpath_memcpy/memset` 중 platform-neutral로 볼 수 있는 부분
  - 제거: `p_lms_accel`, `p_bl2_*`, RSE BL2 state offset, MCUboot/P-256/LMS helper include, RSE-specific profile counters
- [ ] guest memory/state 접근이 observer에 필요하면 RSE 이름 없는 context object로 노출한다.
  - 추가: `tools/qbox/qemu-components/common/include/cpu-semantic-context.h`
  - API 의미: `read_guest`, `write_guest`, `read_arm_v7m_state`, `advance_pc_or_return`, `install_direct_file_aliases`
- [ ] `qbox-platform`에 RSE implementation target을 만든다.
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/include/rse_cpu_accel.h`
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/src/rse_cpu_accel.cc`
  - 추가: `tools/qbox-platform/qemu-components/rse_cpu_accel/src/rse_cpu_accel_profile.cc`
  - 수정: `tools/qbox-platform/qemu-components/rse_cpu_accel/CMakeLists.txt`
- [ ] RSE implementation은 `namespace qbox::platform::rse_cpu_accel`에 둔다. `cpu.h`가 include하지 않도록 public API는 `QemuCpuPcEntryObserver`와 `QemuCpuSemanticContext`만 사용한다.
- [ ] RSE acceleration CCI parameter를 `rse_cpu_accel` target 쪽으로 이동한다.
  - `hotpath_accel`
  - `lms_accel`
  - `bl2_load_profile`
  - `bl2_load_accel`
  - `bl2_boot_enc_accel`
  - `bl2_img_hash_accel`
  - `bl2_verify_sig_accel`
  - `bl2_delay_accel`
  - `direct_file_aliases`
- [ ] remote M55 wrapper를 `qbox-platform`에 추가하고, Apollo/RD-Aspen Lua가 이 wrapper를 사용하게 한다.
  - 추가: `tools/qbox-platform/platforms/cortex-m55-remote/CMakeLists.txt`
  - 추가: `tools/qbox-platform/platforms/cortex-m55-remote/src/apollo_rse_remote_cpu.h`
  - 추가: `tools/qbox-platform/platforms/cortex-m55-remote/src/apollo_rse_remote_cpu.cc`
  - 수정: `tools/qbox-platform/CMakeLists.txt`
  - 수정: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
  - 수정: `tools/qbox-platform/platforms/fvp-rd-aspen-rse/conf.lua`
- [ ] 새 remote wrapper는 core `RemotePass` transport와 generic `cpu_arm_cortexM55`를 재사용하되, observer 등록과 RSE CCI parameter 해석만 `qbox-platform`에서 담당한다.
- [ ] `remote_cpu_exec` 기본값은 `build/local-apollo-fvp/work/qbox-platform/apollo_rse_remote_cpu`로 바꾼다.
- [ ] `tools/qbox-platform/CMakeLists.txt`에는 `add_subdirectory(platforms/cortex-m55-remote)`만 남긴다. `add_subdirectory(cortex-m55-remote)`처럼 존재하지 않는 top-level path는 제거한다.
- [ ] RSE acceleration이 켜진 경우 runner는 BL2/BL1_2 ELF symbol 주소와 Lua/env default 주소를 비교한다.
  - 수정: `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
  - 수정: `scripts/run/run_qbox_apollo_fvp_full.py`
  - mismatch 시 기본 동작: 해당 acceleration만 disable하고 `result.json`에 `rse_accel_symbol_mismatch`를 기록한다.
- [ ] `tools/qbox/platforms/cortex-m55-remote/src/remote_cpu.h`에는 Apollo/RSE parameter를 남기지 않는다.
- [ ] 검증한다.
  ```bash
  cmake --build build/local-apollo-fvp/work/qbox-platform \
    --target rse_cpu_accel apollo_rse_remote_cpu platforms-vp \
    --parallel 8
  rg -n 'rse_lms_accel|rse_mcuboot|rse_p256|bl2_|lms_accel|mcuboot|p256|cc3xx_core' \
    tools/qbox/qemu-components/common/include/cpu.h
  ```
  위 `rg` 명령은 결과가 없어야 한다.

## Milestone 3: `cc3xx_core.h` core 제거

- [ ] `cpu.h`가 `cc3xx_core.h`를 include하지 않는 것을 확인한 뒤 core copy를 삭제한다.
  - 삭제: `tools/qbox/qemu-components/common/include/cc3xx_core.h`
- [ ] `qbox-platform` CC3XX target만 `cc3xx_core`를 include하도록 CMake include path를 정리한다.
  - 수정: `tools/qbox-platform/systemc-components/cc3xx/CMakeLists.txt`
  - 수정: `tools/qbox-platform/qemu-components/cc3xx_native/CMakeLists.txt`
  - 수정: `tools/qbox-platform/tests/components/cc3xx/CMakeLists.txt`
- [ ] core boundary grep을 실행한다.
  ```bash
  rg -n 'cc3xx|CC3XX|rse_lms|rse_mcuboot|rse_p256' tools/qbox \
    -g '!tests/**' \
    -g '!build/**'
  ```
  허용 결과는 generic 문서나 제거 예정 sample 언급뿐이어야 한다.

## Milestone 4: MMIO fastpath/direct-file alias policy 분리

- [ ] `tools/qbox/qemu-components/common/include/ports/initiator.h`에는 generic API만 남긴다.
  - 유지: DMI region, fd-backed DMI, read-only DMI write fallback, MemTxAttrs 전달
  - 유지: 명시적으로 호출되는 `install_direct_file_aliases(spec, priority)`
  - 제거 또는 rename: `QBOX_MMIO_READ_FASTPATH`, `QBOX_MMIO_DIRECT_FASTPATH_RANGES` 환경변수 직접 해석
- [ ] direct-file alias와 MMIO read fastpath는 platform이 명시적으로 opt-in한 범위에만 적용한다. QBox core는 env를 읽지 않고 CCI/API 호출로 전달된 range만 설치한다.
- [ ] Apollo/RD-Aspen runner가 fastpath env를 해석해 Lua/CCI parameter로 넘기게 한다.
  - 수정: `scripts/run/run_qbox_apollo_fvp_full.py`
  - 수정: `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
  - 수정: `scripts/run/run_qbox_apollo_fvp_full_tmux.sh`
- [ ] Apollo/RD-Aspen Lua에서 RSE direct alias policy를 명시한다.
  - 수정: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
  - 수정: `tools/qbox-platform/platforms/fvp-rd-aspen-rse/conf.lua`
- [ ] 기존 fastpath performance evidence를 비교한다.
  ```bash
  python3 scripts/run/run_qbox_apollo_fvp_full.py \
    --si-mode live-cl0-cl1 \
    --timeout 600 \
    --post-login-probe \
    --out-dir build/qbox-apollo-fvp/full-after-fastpath-policy-move
  python3 scripts/test/check_qbox_sram_dmi_fastpath.py \
    build/qbox-apollo-fvp/full-after-fastpath-policy-move/result.json
  ```
- [ ] negative fastpath evidence를 확인한다.
  - 기본 `--qbox-performance-preset` 경로에서 `rse_direct_file_aliases_summary.enabled`는 `false`여야 한다.
  - `host_sram_backing.*.mode`는 `shared_memory`여야 한다.
  - `stats.*.direct_file_alias_hits`는 모두 `0`이어야 한다.

## Milestone 5: FVP aperture mirror policy를 opt-in으로 변경

- [ ] `QemuTargetSocket`의 4KiB mirror fallback을 parameter화한다.
  - 수정: `tools/qbox/qemu-components/common/include/ports/target.h`
  - 신규 CCI parameter 이름: `mirror_4k_aperture = false`
  - 기본 동작: mirror off
  - opt-in 1단계: read-only mirror. write mirror는 별도 `mirror_4k_writes = false` parameter가 true일 때만 허용
- [ ] PL011 ID register mirror를 parameter화한다.
  - 수정: `tools/qbox/systemc-components/uart/uart-pl011/include/uart-pl011.h`
  - 신규 CCI parameter 이름: `id_register_mirror_mask = 0`
  - `id_register_mirror_mask`는 PL011 peripheral ID/PrimeCell ID read에만 적용하고 일반 data/control register write에는 적용하지 않는다.
- [ ] Apollo/RD-Aspen Lua에서 FVP-compatible aperture가 필요한 PL011/target에만 opt-in한다.
  - 수정: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
  - 수정: `tools/qbox-platform/platforms/apollo/hw-block/primary_compute.lua`
  - 수정: `tools/qbox-platform/platforms/fvp-rd-aspen/conf.lua`
  - 수정: `tools/qbox-platform/platforms/fvp-rd-aspen-rse/conf.lua`
- [ ] core unit test와 Apollo map validator를 같이 실행한다.
  ```bash
  cmake --build build/local-apollo-fvp/work/qbox-platform \
    --target uart-pl011 platforms-vp \
    --parallel 8
  python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
    --out build/qbox-apollo-fvp/full-map-after-aperture-policy.json
  ```
- [ ] aperture negative test를 추가한다.
  - 추가: `tools/qbox-platform/tests/components/uart/pl011-aperture-tests.cc`
  - 검증: high-offset peripheral ID read는 opt-in 시 성공, high-offset data/control write는 opt-in 없이 address error 또는 no mirror
  - 실행:
    ```bash
    cmake --build build/local-apollo-fvp/work/qbox-platform \
      --target pl011-aperture-tests \
      --parallel 8
    ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
      -R 'pl011-aperture' \
      --output-on-failure
    ```

## Milestone 6: cortex-m55 remote sample 경계 정리

- [ ] core `platforms/cortex-m55-remote`를 generic example로 되돌린다.
  - 유지: `RemotePass`, `remote_cpu` sample, generic Cortex-M55 smoke platform
  - 제거: Apollo/RSE CCI parameter, Apollo-specific test fixture, Apollo validation naming
- [ ] Apollo/RSE remote CPU test는 `qbox-platform`에서 소유한다.
  - 유지/수정: `tools/qbox-platform/tests/platforms/cortex-m55-remote/CMakeLists.txt`
  - 유지/수정: `tools/qbox-platform/tests/platforms/cortex-m55-remote/cortex-m55-dmi.lua`
  - 유지/수정: `tools/qbox-platform/tests/platforms/cortex-m55-remote/cortex_m55_dmi.py`
- [ ] `qbox-platform` aggregate target이 Apollo remote CPU executable/module을 포함하도록 유지한다.
  - 수정: `tools/qbox-platform/CMakeLists.txt`
  - `QBOX_APOLLO_REQUIRED_TARGETS`에 `apollo_rse_remote_cpu`를 추가하고, core sample target `remote_cpu`는 generic sample 검증이 필요한 경우에만 남긴다.
- [ ] 검증한다.
  ```bash
  cmake --build build/local-apollo-fvp/work/qbox-platform \
    --target apollo_fvp_full_system \
    --parallel 8
  ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
    -R 'cortex_m55_remote_dmi' \
    --output-on-failure
  ```

## Milestone 7: 문서와 자동 검사 갱신

- [ ] core/platform boundary audit에 새 금지 패턴을 추가한다.
  - 수정: `scripts/test/audit_qbox_core_boundary.py`
  - 추가 금지 패턴: `rse_lms_accel`, `rse_mcuboot_image`, `rse_p256_ecdsa`, `bl2_.*accel`, `QBOX_RDASPEN_RSE_.*ACCEL` in `tools/qbox`
  - 추가 금지 경로: `tools/qbox/qemu-components/common/include/cc3xx_core.h`, `tools/qbox/qemu-components/common/include/rse_lms_accel.h`, `tools/qbox/qemu-components/common/include/rse_mcuboot_image.h`, `tools/qbox/qemu-components/common/include/rse_p256_ecdsa.h`
- [ ] 문서를 갱신한다.
  - 수정: `doc/source-structure-ko.md`
  - 수정: `doc/apollo-qbox-hardware-ko.md`
  - 수정: `doc/qbox-rse-boot-slow-path-analysis-ko.md`
  - 수정: `tools/qbox-platform/README.md`
  - 수정: `doc/qbox-upstream-diff-analysis-ko.md`
- [ ] `doc/qbox-upstream-diff-analysis-ko.md`의 Platform 분리 후보 상태를 `planned`에서 `moved` 또는 `core-genericized`로 업데이트한다.
- [ ] 최종 검증 명령을 실행한다.
  ```bash
  git -C tools/qbox diff --check
  git -C tools/qbox-platform diff --check
  python3 -m py_compile scripts/run/run_qbox_apollo_fvp_full.py \
    scripts/run/run_qbox_fvp_rd_aspen_rse.py \
    scripts/test/audit_qbox_core_boundary.py
  python3 scripts/test/audit_qbox_core_boundary.py
  python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
    --out build/qbox-apollo-fvp/full-map-after-platform-separation.json
  ./local-build.sh qbox
  ctest --test-dir build/local-apollo-fvp/work/qbox-platform/qbox-core \
    -R 'dmi|loader|memory|remote|uart|cortex-m55' \
    --output-on-failure
  ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
    -R 'cc3xx|rse_lms|rse_mcuboot|rse_p256|cortex_m55_remote_dmi|pl011-aperture' \
    --output-on-failure
  python3 scripts/run/run_qbox_apollo_fvp_full.py \
    --si-mode live-cl0-cl1 \
    --timeout 600 \
    --post-login-probe \
    --out-dir build/qbox-apollo-fvp/full-after-platform-separation
  ```

## 위험과 대응

| 위험 | 영향 | 대응 |
| --- | --- | --- |
| RSE acceleration을 CPU core에서 빼면서 PC-entry hook timing이 달라짐 | RSE 첫 부팅 성능 저하 또는 TF-M BL2 handoff 실패 | Milestone 2에서 RSE boot before/after result를 비교하고, observer callback은 기존 `m_cpu.set_pc_entry_callback()` 호출 지점과 동일한 simulation phase에서 등록 |
| `cc3xx_core` include path 변경으로 SystemC/QEMU wrapper 중 하나가 다른 header를 참조 | SystemC/QEMU CC3XX 동작 drift | `cc3xx_core-tests`, `cc3xx-tests`, `qemu_cc3xx-tests`를 같은 build dir에서 함께 실행 |
| direct-file alias policy 이동 후 RSE SRAM fastpath가 비활성화됨 | RSE boot time 증가 | `check_qbox_sram_dmi_fastpath.py`와 runtime result의 `rse_direct_file_aliases_summary`를 acceptance criterion에 포함 |
| PL011/target mirror를 default-off로 바꾸며 FVP aperture read가 깨짐 | UART/virtio/AP boot probe 실패 | Apollo/RD-Aspen Lua에서 필요한 장치만 opt-in하고 `validate_qbox_apollo_fvp_full_map.py`로 aperture coverage 확인 |
| core `remote_cpu` sample과 Apollo remote CPU executable 이름 충돌 | dynamic module load 실패 | Apollo 전용 wrapper는 `apollo_rse_remote_cpu` target과 `ApolloRseRemoteCPU` moduletype을 사용하고, legacy `RemoteCPU`는 core sample에만 유지 |
| BL2 symbol 주소 drift | acceleration이 잘못된 함수 entry에서 실행되어 boot corruption 발생 | runner에서 ELF-derived symbol/default address mismatch를 검출하고 해당 acceleration을 자동 disable |
| CMake path drift | `tools/qbox-platform/CMakeLists.txt`가 존재하지 않는 subdirectory를 참조해 clean build 실패 | `add_subdirectory(platforms/cortex-m55-remote)`만 허용하고 `cmake --build ... --target apollo_fvp_full_system`로 clean path 검증 |

## 구현 순서 요약

1. RSE helper와 `cc3xx_core` include ownership을 `qbox-platform`으로 먼저 이동한다.
2. QBox core에 generic PC-entry observer/context만 추가한다.
3. RSE BL2/LMS/P-256/MCUboot acceleration 구현을 `qbox-platform/qemu-components/rse_cpu_accel`로 옮긴다.
4. Apollo/RD-Aspen RSE remote CPU wrapper를 `qbox-platform`에서 소유하게 한다.
5. MMIO fastpath/direct alias env policy를 runner/Lua 쪽으로 옮긴다.
6. FVP aperture mirror 동작을 default-off core parameter와 platform opt-in으로 바꾼다.
7. core boundary audit, QBox platform build, component tests, Apollo full-system boot로 검증한다.

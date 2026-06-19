# QBox Upstream Diff 분석

작성일: 2026-06-19

## 범위

이 문서는 `tools/qbox` 저장소의 upstream 기준 변경 사항을 파일별로
정리한다. 기준 커밋과 확인 명령은 다음과 같다.

```bash
git -C tools/qbox diff 5a78034faf26 --stat
git -C tools/qbox diff --name-status 5a78034faf26
```

현재 diff 규모는 다음과 같다.

```text
46 files changed, 4625 insertions(+), 140 deletions(-)
```

분석 관점은 세 가지다.

- 변경 요약: 해당 파일에서 무엇이 바뀌었는가.
- 사용처: 변경된 기능이 어디에서 호출되거나 어떤 테스트/플랫폼 설정이
  소비하는가.
- 목적/소유권: 왜 필요한 변경인지, QBox core에 남기는 것이 맞는지,
  `qbox-platform`으로 분리하는 것이 나은지.

## 전체 결론

변경의 큰 축은 다음과 같다.

| 축 | 주요 파일 | 목적 | 소유권 판단 |
| --- | --- | --- | --- |
| Local QEMU/libqemu 개발 지원 | `CMakeLists.txt`, `cmake/boilerplate.cmake` | `tools/qemu` 같은 로컬 source tree를 FetchContent 대신 사용하고, dependency checkout을 안정화 | QBox core 유지 |
| DMI/shared-memory/file-backed memory 정합성 | `dmi-manager.h`, `ports/initiator.h`, `memory_services.*`, `gs_memory.h`, `remote.h`, DMI tests | QEMU DMI alias, shared memory fd, file-backed DMI, read-only DMI write fallback 지원 | 대부분 QBox core 유지 |
| Generic CPU 관측 hook | `cpu.h`, `cpu-pc-entry-observer.h`, `cpu-semantic-context.h` | CPU PC-entry watch와 register/memory 접근을 외부 observer가 사용할 수 있게 함 | QBox core 유지. RSE semantic acceleration은 `qbox-platform`으로 분리 |
| FVP-style aperture/debug 지원 | `ports/target.h`, `uart-pl011.h`, `virtio-mmio.h` | 넓은 MMIO window의 ID read, virtio trace, MemTxAttrs 전달 | QBox core에 opt-in parameter로 유지하고 platform Lua에서만 활성화 |
| 회귀 테스트 | `tests/components/*`, `tests/qbox/cpu/*` | DMI byte-store, read-only fallback, shmem/file DMI, reset-time loader 검증 | QBox core test 유지 |

분리 구현 후 `qemu-components/common/include/cpu.h`에는 일반 CPU trace,
reset, memory/register access, PC-entry observer dispatch만 남긴다. RSE BL2
semantic acceleration, MCUboot/LMS/P-256 helper, CC3XX core 의존성은
`tools/qbox-platform`의 RSE CPU wrapper와 CC3XX component 소유로 이동했다.

## 파일별 상세 분석

| 파일 | 변경 요약 | 사용처 | 목적/소유권 판단 |
| --- | --- | --- | --- |
| `.gitignore` | `.cache/` 무시 추가 | QBox build/dependency 도구 캐시가 Git 상태에 노출되지 않도록 사용 | Git hygiene 변경. QBox core 유지 |
| `CMakeLists.txt` | `QEMU_SOURCE_DIR` cache option 추가, `FETCHCONTENT_SOURCE_DIR_QEMU`, `FETCHCONTENT_SOURCE_DIR_LIBQEMU`에 로컬 QEMU source override 연결 | `tools/qbox-platform/CMakeLists.txt`와 `scripts/build/local_build_common.sh`가 `QBOX_QEMU_SOURCE_DIR`/`QEMU_SOURCE_DIR`로 로컬 `tools/qemu`를 넘김 | 로컬 libqemu/QEMU 개발에 필요한 공통 build hook. QBox core 유지 |
| `cmake/boilerplate.cmake` | SystemC CCI/SCP FetchContent `GIT_SHALLOW`을 `False`로 변경 | QBox dependency bootstrap에서 CCI/SCP checkout 시 적용 | 고정 revision checkout, patch/debug, submodule 상태 확인 안정화. QBox core 유지 |
| `platforms/cortex-m55-remote/CMakeLists.txt` | EOF newline 정리 | `cortex-m55-vp`, `remote_cpu` example platform build file | 실질 동작 변경 없음. 장기적으로 `cortex-m55-remote` example 전체는 platform/example 분리 후보 |
| `platforms/cortex-m55-remote/src/remote_cpu.cc` | `keep_alive` module 생성 및 `name_bind()` 추가 | `remote_cpu` executable 내부 RemotePlatform | remote-only CPU process가 조기 종료되지 않도록 유지. `cortex-m55-remote` platform 특화 성격이라 장기적으로 `qbox-platform` 후보 |
| `platforms/src/main.cc` | `<remote.h>` include 추가 | `platforms-vp` 공통 entrypoint build | 직접 symbol 사용은 보이지 않아 remote 관련 전이 include/build 의존 보강으로 보임. 필요성 재확인 대상, 현상 유지 시 QBox core |
| `qemu-components/common/include/cpu.h` | PC trace, PC-entry observer dispatch, reset power-on, Arm state 접근, guest memory read/write helper 추가 | generic CPU observer와 `tools/qbox-platform/qemu-components/rse_cpu_accel/`의 Apollo RSE wrapper | CPU 관측과 semantic context는 공통 hook으로 QBox core 유지. RSE/BL2 semantic acceleration 자체는 core에서 제거됨 |
| `qemu-components/common/include/dmi-manager.h` | fd offset 기반 DMI region, read-only DMI region, read-only alias write callback, alias installed state clear 추가 | `ports/initiator.h`가 shared-memory/file DMI alias를 QEMU MemoryRegion으로 설치할 때 사용 | DMI 정합성 공통 기능. read-only flash-like DMI write side effect 보존. QBox core 유지 |
| `qemu-components/common/include/internals.h` | bool-return callback dispatcher와 CPU PC-entry callback registry 추가 | `callbacks.cc`의 `generic_cpu_pc_entry_cb`, `cpu.cc`의 PC watch API, `cpu.h` observer dispatch | QEMU CPU PC watch를 C++ callback으로 연결하는 공통 wrapper. QBox core 유지 가능 |
| `qemu-components/common/include/libqemu-cxx/libqemu-cxx.h` | `MemoryRegion::init_ram_ptr(..., fd_offset)`, `set_readonly`, CPU run-state/PC/mem-IO-PC/PC-entry-watch API 선언 | `dmi-manager.h`, `memory.cc`, `cpu.h`, `callbacks.cc`, `cpu.cc` | libqemu export를 C++ wrapper로 노출하는 공통 기능. QBox core 유지 |
| `qemu-components/common/include/libqemu-cxx/target/aarch64.h` | Arm V7M/AArch64 state enum, power state, power-on-reset, V7M/AArch64 state accessor 추가 | generic CPU semantic context, AP/AArch64 PC trace, reset power-on | wrapper 자체는 generic. QBox core 유지 |
| `qemu-components/common/include/ports/initiator.h` | QEMU initiator socket에 profile JSON, address bucket profile, explicit MMIO read/direct fastpath API, shared-memory fd offset DMI, read-only write fallback, direct file alias, QEMU MemTxAttrs 전달 추가 | `QemuCpu::socket`, DMI manager, generic CPU semantic context, DMI CPU tests, platform Lua의 opt-in fastpath 설정 | DMI/fd/attrs/profile과 explicit fastpath API는 core. env 기반 policy는 제거되어 platform runner/Lua가 소유 |
| `qemu-components/common/include/ports/target.h` | QEMU target bridge trace, MemTxAttrs 수신, opt-in 4KiB mirror fallback, virtio register name tracing 추가 | `QemuTargetSocket`, `virtio-mmio.h`의 `socket.set_trace()`, Apollo/RD-Aspen Lua의 `mirror_4k_aperture` 설정 | trace/attrs와 opt-in mirror mechanism은 core. 활성화 policy는 platform Lua가 소유 |
| `qemu-components/common/include/tlm-extensions/qemu-memtx-attrs.h` | QEMU `MemTxAttrs`를 TLM payload extension으로 전달하는 class 추가 | `ports/initiator.h`에서 extension 생성, `ports/target.h`에서 extension 수신 | secure/debug/user memory attribute 보존용 공통 bridge. QBox core 유지 |
| `qemu-components/common/include/virtio/virtio-mmio.h` | trace CCI/env parameters, `ioeventfd` parameter, virtio MMIO socket trace 설정 추가 | Apollo/FVP primary compute의 virtio blk/net/rng, runner env `QBOX_VIRTIO_MMIO_TRACE*` | virtio bring-up/queue 디버깅과 eventfd 제어. QBox core 유지 가능 |
| `qemu-components/common/src/libqemu-cxx/callbacks.cc` | PC-entry callback bridge 추가, `Cpu::set_pc_entry_callback()`, `clear_pc_entry_callback()` 구현 | `cpu.h`가 generic observer dispatch를 등록할 때 사용 | QEMU PC watch callback을 C++로 연결. QBox core 유지 |
| `qemu-components/common/src/libqemu-cxx/cpu.cc` | run state, current PC, mem IO PC, PC watch add/clear/count/stat API 구현 | `cpu.h` PC trace, PC-entry observer, reset/debug sampling | CPU introspection 공통 wrapper. QBox core 유지 |
| `qemu-components/common/src/libqemu-cxx/memory.cc` | fd-backed RAM init, fd offset 전달, readonly setter 구현 | `dmi-manager.h`, `ports/initiator.h` direct/shared DMI | shared-memory/file-backed DMI를 QEMU MemoryRegion으로 정확히 매핑. QBox core 유지 |
| `qemu-components/common/src/libqemu-cxx/target/aarch64.cc` | Arm power state, V7M/AArch64 state wrapper 구현 | `cpu.h` reset power-on, generic CPU semantic context, PC trace | wrapper는 generic. QBox core 유지 |
| `qemu-components/cpu_arm/cpu_arm_cortex_m55/CMakeLists.txt` | EOF newline 정리 | `cpu_arm_cortexM55` dynamic module include dirs | 동작 변경 없음. QBox core 유지 |
| `systemc-components/CMakeLists.txt` | trailing blank line 제거 | SystemC component top-level CMake | 동작 변경 없음. QBox core 유지 |
| `systemc-components/backends/char_backend_file/include/char_backend_file.h` | `poll_read`, nonblocking input file open, polling thread, clean shutdown 추가 | Apollo/RD-Aspen Lua의 UART file backend에서 `poll_read` 설정 | tmux/log file UART 입력이 EOF에서 닫히지 않고 계속 입력을 받을 수 있게 함. QBox core backend 기능 |
| `systemc-components/common/include/loader.h` | `load_at_elaboration` CCI param 추가, `load_all()` 분리, reset signal에서 load 수행 | Apollo/RD-Aspen RSE/SI Lua의 `load_at_elaboration = false`, loader tests | reset 시점 image loading 지원. QBox core 유지 |
| `systemc-components/common/include/memory_services.h` | shared-memory fd lookup, fd offset lookup, file mapping cache API 추가 | `memory_services.cc`, `remote.h`, `gs_memory.h`, `ports/initiator.h` | shmem/file-backed DMI backing store 공유. QBox core 유지 |
| `systemc-components/common/include/remote.h` | opt-in DMI cache, file-backed DMI RPC serialization, RemotePass profile JSON, DMI invalidation cache clean 추가 | `remote_cpu`, remote component tests, runner env `QBOX_REMOTEPASS_PROFILE_DIR` | remote process 사이 DMI pointer를 shmem/file로 재구성하고 성능 profile을 남김. QBox core 유지 |
| `systemc-components/common/include/tlm-extensions/shmem_extension.h` | `FileDMIExtension` 추가 | `gs_memory.h`가 map-file memory에 extension 부착, `remote.h`가 RPC로 전달 | file-backed DMI metadata 전달. QBox core 유지 |
| `systemc-components/common/src/memory_services.cc` | `map_file_join()`, file map cleanup, shmem fd 보존, `map_mem_create(..., fd)`, `get_shmem_fd_offset_for_ptr()` 구현 | `remote.h`, `ports/initiator.h`, memory tests | shared-memory/file-backed DMI alias를 프로세스 사이에서 재사용. QBox core 유지 |
| `systemc-components/gs_memory/include/gs_memory.h` | map-file memory block에 `FileDMIExtension` 부착 | remote/file-DMI tests, `remote.h` DMI RPC | `map_file` 기반 memory도 remote process에서 같은 backing file을 join 가능하게 함. QBox core 유지 |
| `systemc-components/reg_router/include/reg_router.h` | DMI forwarding, DMI range clipping, invalidate forwarding 추가 | `tests/components/gs_register/gs_register-tests.cc`, register/memory target routing | router 뒤 target도 DMI를 제공하도록 해 CPU fast path와 DMI tests를 통과. QBox core 유지 |
| `systemc-components/uart/uart-pl011/include/uart-pl011.h` | PL011 ID register mirror mask CCI parameter 추가 | FVP-style oversized PL011 aperture에서 Apollo/RD-Aspen Lua가 `id_register_mirror_mask`로 AMBA peripheral ID mirror를 opt-in | generic PL011에는 기본 비활성. QBox core에 opt-in 기능으로 유지 |
| `tests/components/gs_register/gs_register-tests.cc` | `reg_router` DMI forwarding 검증 추가 | `reg_router.h` 변경 검증 | DMI start/end remap과 read/write grant 보장. QBox core test 유지 |
| `tests/components/loader/conf-test.lua` | `LoadOnResetOnly` test config 추가, `load_at_elaboration=false` 설정 | `loader-test.cc` | reset-triggered loader 동작 검증. QBox core test 유지 |
| `tests/components/loader/loader-test.cc` | reset 전에는 data 미로드, reset 후 data 로드 확인 | `loader.h`의 `load_at_elaboration` 변경 검증 | reset-only load semantics 회귀 방지. QBox core test 유지 |
| `tests/components/memory/memory-tests.cc` | ROM write reject, provisioning bundle offset load, shared-memory fd 반환 테스트 추가 | `gs_memory.h`, `memory_services.cc` | RSE 용례에서 발견된 memory contract를 generic test로 고정. test 이름의 `Rse*`는 장기적으로 generic 이름으로 정리 가능 |
| `tests/components/remote/remote-tests.cc` | temporary map file 생성 후 remote `mem3.map_file`로 DMI roundtrip 검증 | `remote.h`, `FileDMIExtension`, `MemoryServices::map_file_join()` | remote file-backed DMI 경로 검증. QBox core test 유지 |
| `tests/qbox/cpu/CMakeLists.txt` | `cortex-m55` CPU test subdir 등록 | `tests/qbox/cpu/cortex-m55/CMakeLists.txt` | M-profile DMI 회귀 테스트 활성화. QBox core test 유지 |
| `tests/qbox/cpu/aarch64/CMakeLists.txt` | AArch64 DMI byte-store/read-only/shared-memory/external-write tests 등록 | 신규 AArch64 DMI test files | QEMU AArch64 CPU DMI correctness 회귀 테스트. QBox core test 유지 |
| `tests/qbox/cpu/aarch64/dmi-byte-store-test.cc` | A53 firmware가 DMI install 후 `strb/ldrb` byte pattern 검증 | `CpuTesterDmi`, `qbox_add_cpu_test(aarch64-dmi-byte-store-test, ...)` | QEMU DMI alias가 byte lane을 잃지 않는지 검증. QBox core test 유지 |
| `tests/qbox/cpu/aarch64/dmi-readonly-write-fallback-test.cc` | read-only DMI grant 상태에서 guest write가 TLM callback으로 fallback되고 stale read가 무효화되는지 검증 | `CpuTesterDmi::disable_dmi_write*`, callback read override | flash-like read-DMI/write-side-effect device contract 검증. QBox core test 유지 |
| `tests/qbox/cpu/aarch64/shmem-dmi-byte-store-test.cc` | shmem-backed `gs_memory` DMI에서 A53 byte-store pattern 검증 | `gs_memory` `p_shmem`, DMI manager fd-backed region | shared-memory DMI alias correctness 검증. QBox core test 유지 |
| `tests/qbox/cpu/aarch64/shmem-dmi-external-write-test.cc` | CPU가 DMI alias 설치 후 SystemC side direct write를 관측하는지 검증 | `gs_memory::write_bytes()`, A53 polling firmware | DMA/peripheral write visibility 회귀 검증. QBox core test 유지 |
| `tests/qbox/cpu/cortex-m55/CMakeLists.txt` | optional `arm-none-eabi-gcc/objcopy`로 M55 firmware build, `cortex-m55-dmi-byte-store-test` 등록 | M55 assembly/linker/test fixture | M-profile CPU DMI 회귀 테스트. QBox core test 유지 |
| `tests/qbox/cpu/cortex-m55/cortex-m55-dmi-byte-store-test.cc` | Cortex-M55가 shmem DMI byte-store pattern을 실행하고 결과 MMIO를 확인 | `cpu_arm_cortexM55`, `gs_memory`, vector table init | RSE-like M-profile DMI path 검증. QBox core test 유지 |
| `tests/qbox/cpu/cortex-m55/cortex-m55-dmi-byte-store.S` | M55 bare-metal smoke firmware 추가. 첫 read로 DMI 설치 후 byte store/read pattern 검증 | `tests/qbox/cpu/cortex-m55/CMakeLists.txt`에서 firmware binary로 빌드 | CPU-executed M-profile DMI fixture. QBox core test 유지 |
| `tests/qbox/cpu/cortex-m55/cortex-m55-dmi-byte-store.ld` | M55 test firmware linker script 추가 | 위 assembly firmware link | vector table/text를 deterministic ROM layout으로 배치. QBox core test 유지 |
| `tests/qbox/include/test/tester/dmi.h` | DMI buffer를 4KiB/page aligned로 확장, read-only/write-hint toggle, callback-read value mode, byte accessor 추가 | AArch64 DMI byte/read-only fallback tests | page/fd-aligned DMI와 read-only fallback test를 지원하는 공통 test helper. QBox core test 유지 |

## Platform 분리 구현 결과

2026-06-19 구현에서 다음 항목을 `tools/qbox-platform`으로 이동하거나
platform opt-in 형태로 정리했다.

| 항목 | 처리 결과 | 검증 관점 |
| --- | --- | --- |
| RSE/BL2 semantic acceleration | `qbox-platform/qemu-components/rse_cpu_accel/`로 이동. QBox core `cpu.h`는 `QemuCpuPcEntryObserver`와 `QemuCpuSemanticContext` hook만 제공 | `rg`로 QBox core의 `cc3xx_core`, `rse_lms_accel`, `rse_mcuboot_image`, `rse_p256_ecdsa`, BL2 accel 문자열 제거 확인 |
| MCUboot/LMS/P-256 helper | `qbox-platform/qemu-components/rse_cpu_accel/include/`로 이동 | `ctest`의 `rse_lms_accel-tests`, `rse_mcuboot_image-tests`, `rse_p256_ecdsa-tests` 통과 |
| CC3XX core | `qbox-platform/systemc-components/cc3xx/include/cc3xx_core.h` 소유로 정리 | `cc3xx_core-tests`와 Apollo full-system boot 통과 |
| RSE remote CPU executable | `qbox-platform/platforms/cortex-m55-remote/apollo_rse_remote_cpu`로 분리 | runner가 `apollo_rse_remote_cpu`를 우선 선택하고 boot log에서 `ApolloRseRemoteCPU.so` load failure가 사라짐 |
| MMIO read/direct fastpath policy | QBox core의 env 직접 parsing 제거. `ports/initiator.h`는 explicit API만 제공하고 Apollo/RD-Aspen Lua가 `QBOX_RDASPEN_RSE_MMIO_*`를 읽어 opt-in | QBox core boundary audit와 full-system boot 통과 |
| 4KiB aperture mirror와 PL011 ID mirror | core mechanism은 CCI parameter로 유지하고 기본값은 비활성. Apollo/RD-Aspen Lua에서만 `mirror_4k_aperture`, `id_register_mirror_mask`를 설정 | `pl011-aperture-tests`와 Apollo full-system boot 통과 |

이미 `platforms/cortex-m55-remote/tests/*`에 있던 Apollo validation 성격의
remote DMI byte-store test는 `tools/qbox-platform/tests/platforms/cortex-m55-remote/`
로 이동되어, 현재 upstream diff에는 남아 있지 않다.

## 잔여 후보

현재 QBox core에 남은 변경 중 추가 검토할 후보는 다음 정도다.

| 우선순위 | 후보 | 이유 | 제안 |
| --- | --- | --- | --- |
| 1 | `platforms/cortex-m55-remote/*` | upstream example 성격과 Apollo RemotePass 검증 요구가 일부 섞여 있음 | generic example은 QBox core에 남기고 Apollo-specific executable/test는 `qbox-platform`에 유지 |
| 2 | `ports/initiator.h`의 direct file alias API | RSE boot acceleration에서 주로 사용하지만 DMI/file-backed memory generic 기능과 맞닿아 있음 | core API는 유지하되 platform policy/env parsing은 계속 `qbox-platform`에 둠 |
| 3 | `ports/target.h`의 aperture mirror mechanism | FVP-style wide aperture 대응이지만 모든 device에 기본 적용되면 위험함 | 현재처럼 default-off CCI parameter로 유지하고 platform Lua에서만 활성화 |

## 구현 검증 결과

이번 분리 구현은 다음 명령으로 검증했다.

```bash
python3 -m py_compile \
  scripts/test/audit_qbox_core_boundary.py \
  scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run/run_qbox_apollo_fvp_full.py
python3 scripts/test/audit_qbox_core_boundary.py --json
./local-build.sh qbox
ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
  -R 'cc3xx_core|rse_lms|rse_mcuboot|rse_p256|pl011-aperture|cortex_m55_remote_dmi' \
  --output-on-failure
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-fvp/full-map-after-platform-separation.json
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 180 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-after-platform-separation-retry
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-after-platform-separation-retry/result.json \
  --output build/qbox-apollo-fvp/full-coverage-audit-after-platform-separation.json
```

검증 결과는 다음과 같다.

- QBox core boundary audit: pass.
- qbox-platform targeted CTest: 7/7 pass.
- Apollo full-system QBox boot: pass, blocker none.
- RSE start to Linux login prompt: 47.308초.
- Coverage audit: pass, runtime result와 필수 hardware block marker 통과.

## 검증 포인트

이 문서의 coverage는 다음 조건으로 확인한다.

- `git -C tools/qbox diff --name-only 5a78034faf26`의 46개 파일이 모두
  `파일별 상세 분석` 표에 존재해야 한다.
- 신규 파일(`A`)은 목적과 등록/호출 지점이 표에 있어야 한다.
- RSE/Apollo 전용 성격이 강한 파일은 `Platform 분리 구현 결과` 또는
  `잔여 후보`에 별도 표시해야 한다.

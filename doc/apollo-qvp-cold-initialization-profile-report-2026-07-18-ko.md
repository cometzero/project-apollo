# Apollo QVP cold initialization 구현 및 검증 보고서

- 작성일: 2026-07-18
- 대상: `apollo-qvp`, cfg2, Primary Compute 4 CPU
- 종료점: `FWU: System booting in Regular State`
- 최종 판정: 완료
- architecture decision: `QEMU_LOCAL_CFI + DEFERRED_DIRTY_SECTOR`

## 1. 결과 요약

RSE Protected Storage/ITS cold 초기화의 주 병목은 firmware 알고리즘이 아니라
RSE QEMU CPU와 SystemC Strata flash 사이의 접근별 thread handoff였다. 주소 필터를
적용한 cold profile에서 SystemC flash 277만 건에 대한
`do_regular_access()` 누적 시간이 25.274초였고, 이 중 `run_on_sysc()`가
21.680초였다. SystemC backing write/flush는 각각 약 0.028초여서 주 병목이
아니었다.

최종 구현은 하나의 QEMU `cfi.pflash01` MemoryRegion을 RSE Cortex-M55의 CPU 전용
주소 공간과 외부 TLM target socket에 동시에 노출한다. RSE CPU의 CFI 접근은 같은
QEMU instance 안에서 처리되고, 외부 initiator도 동일 storage와 CFI 상태 머신을
관찰한다. Apollo에 필요한 `0xff` program 호환 erase, I/O-only dispatch, dirty-sector
writeback을 모두 opt-in property로 추가해 generic QEMU 기본 동작은 바꾸지 않았다.

local cold의 RSE runtime handoff부터 FWU Regular State까지는 32.792초에서
6.940초로 25.852초, 약 78.8% 줄었다. 전체 runner 시간은 52.993초에서
30.458초로 줄었다. 성능 수치는 합격 기준이 아니라 병목 제거 관찰값이다.

## 2. 확정 원인

### 2.1 H1: QEMU/SystemC 왕복

확정했다.

| 관찰값 | SystemC-Strata cold | reuse |
|---|---:|---:|
| flash total access | 2,778,624 | 41,472 |
| filtered regular wall time | 25.274초 | 0.453초 |
| filtered `run_on_sysc` wall time | 21.680초 | 0.365초 |
| RSE handoff -> FWU | 32.792초 | 2.916초 |

`do_regular_access()`가 cold 추가 비용의 50% decision gate를 넘었으므로
QEMU-local CFI를 선택했다.

### 2.2 H3: backing write

SystemC-Strata에서는 반증됐지만 QEMU-local prototype에서 다시 유의미해졌다.
초기 QEMU-local CFI는 byte program마다 512-byte `blk_pwrite()`를 실행해
310,333회, 161,055,232 byte, 4.663초를 소비했다. 이는 QEMU-local cold 추가
구간의 10% decision gate를 넘었다.

dirty 512-byte sector를 bitmap으로 모으고 연속 sector를 extent로 합친 최종
구현 결과는 다음과 같다.

| 관찰값 | 동기 write | 최종 deferred write |
|---|---:|---:|
| backing write op | 310,333 | 271 |
| backing write byte | 161,055,232 | 2,733,568 |
| backing write wall time | 4.663초 | 0.010초 |
| 종료 시 pending dirty sector | 0 | 0 |

flush 경계는 update-count interval, 25ms real-time timer, reset, migration
pre-save/post-load, object 종료다. 첫 timer 없는 prototype은 pass 직후 96개 dirty
sector가 남아 PS hash가 달라졌고 즉시 폐기했다. 최종 timer-flush 결과에서만
default 전환을 승인했다.

### 2.3 H2/H4/H5

- H2 guest PS/flash loop는 실제 firmware 동작이므로 유지했다. H1 제거 후 선택한
  경계 비용이 충분히 줄어 별도 firmware 변경을 하지 않았다.
- H4 MHU scheduling은 P1에서 추가 분석하지 않았다. flash 왕복만으로 decision
  threshold가 결정됐고 live AP/RSE doorbell 경로가 기능 검증을 통과했다.
- H5 aggregate profile 결과와 clean/default runtime의 기능 marker가 일치했다.
  원인 확정 뒤 해당 일회성 계측 코드는 최종 소스에서 제거했다.

## 3. 구현 내용

### 3.1 QBox core

- QEMU device MemoryRegion을 특정 `QemuCpu`의 private initiator root에 overlap
  mapping하는 API를 추가했다.
- `pflash_cfi` wrapper에 local address/CPU, CFI compatibility, I/O-only,
  dirty-sector writeback property를 추가했다.
- QEMU-local MemoryRegion의 TLM target export를 유지했다.

원인 분석에 사용한 `QemuInitiatorSocket` wall-time/address profile과 전용 unit
test는 architecture decision 이후 제거했다. 따라서 QBox core의 최종 diff에는
CPU-local MemoryRegion mapping과 필요한 pflash wrapper 연결만 남는다.

초기 prototype은 QEMU global system memory에 flash를 map해 Cortex-M55가
`0xB0005000`에서 precise BusFault를 냈다. GDB로 CFSR `0x8200`, BFAR
`0xb0005000`을 확인한 뒤 RSE CPU 전용 주소 공간
`platform.rse_cpu_pass.cpu_0.cpu`에 mapping해 수정했다.

### 3.2 QEMU

- `program-ff-erases-sector`: Apollo Strata 호환 erase, 기본 off
- `io-mode-only`: command마다 ROMD topology를 재구성하지 않고 callback I/O 유지,
  기본 off
- `defer-backing-write`: dirty-sector extent writeback, 기본 off
- `defer-backing-flush-interval`과 `defer-backing-flush-delay-ms`
- migration pre-save와 post-load backing 동기화

CFI access/program/erase/backing JSON과 wall-time counter는 검증 완료 후 제거했다.
최종 QEMU 변경에는 CFI 동작과 writeback에 필요한 상태만 남는다.

I/O-only를 적용하기 전 QEMU-local prototype은 ROMD 전환 비용 때문에
RSE handoff에서 BL33까지 36.081초가 걸렸다. I/O-only 적용 후 같은 구간은
3.719초로 줄었고, 최종 deferred version은 2.311초였다.

### 3.3 Apollo qbox-platform

- `QBOX_RDASPEN_RSE_FLASH_BACKEND` selector를 추가했다.
- 최종 기본값은 `qemu-cfi-local`이다.
- `systemc-strata`는 명시적 rollback/debug backend로 유지한다.
- QEMU CFI ID는 `0x89/0x18`, size는 64MiB, sector는 4KiB이며 RSE secure base
  `0xB0000000`에 map한다.
- SystemC Strata에 임시로 추가했던 wall-time과 unique dirty-sector 계측은 원인
  확정 후 제거해 기존 component 구현으로 복원했다.

### 3.4 runner와 state 계약

- 새 erased state는 `--rse-flash-state`, `--reset-rse-flash-state`,
  `--uboot-only` 조합으로 재현한다. 일회성 `--cold-init-profile` convenience
  option은 최종 runner에서 제거했다.
- source SHA-256, storage compatibility fingerprint, PS/ITS 전후 SHA-256을
  `result.json`에 기록한다.
- local QBox와 FVP가 같은 canonical marker key를 사용한다.
- `--rse-flash-backend systemc-strata`로 즉시 rollback할 수 있다.

## 4. local 검증

### 4.1 cold/reuse 결과

| backend/run | 전체 | handoff -> BL33 | BL33 -> FWU | handoff -> FWU | 판정 |
|---|---:|---:|---:|---:|---|
| SystemC cold | 52.993초 | 8.642초 | 24.150초 | 32.792초 | pass |
| SystemC reuse | 22.814초 | 1.407초 | 1.509초 | 2.916초 | pass |
| QEMU-local cold | 30.458초 | 2.311초 | 4.629초 | 6.940초 | pass |
| QEMU-local reuse | 23.117초 | 1.106초 | 1.510초 | 2.616초 | pass |

local cold의 PS/ITS 최종 SHA-256은 SystemC와 QEMU-local에서 각각 다음 값으로
일치했다.

- PS: `57cbdf3f410c54e9b6a41e85e28601a8c4a1cde13fccb4534575c2681bb44acd`
- ITS: `7acc7ee8aacff75f0d522414c5e98218353e397a558ee33578eca73b81faf649`

QEMU-local reuse는 두 영역 모두 before/after hash가 같고
`storage_preserved=true`다.

### 4.2 local 증거

- `build/qbox-apollo-qvp/local-cold-live-p1-20260718-1315/`
- `build/qbox-apollo-qvp/local-reuse-live-p1-20260718-continue/`
- `build/qbox-apollo-qvp/local-cold-qemu-cfi-v6-timer-flush-20260718/`
- `build/qbox-apollo-qvp/local-reuse-qemu-cfi-v6-timer-flush-20260718/`
- `build/qbox-apollo-qvp/local-default-backend-smoke-20260718/`
- `build/qbox-apollo-qvp/local-default-backend-cleanup-smoke-20260718/`

마지막 항목은 backend 옵션을 생략한 최종 스모크다. 결과 JSON에서
`rse_flash_backend=qemu-cfi-local`, `action=reused`,
`storage_preserved=true`이고 PS/ITS before/after hash가 같다.
마지막 cleanup 스모크는 임시 profile/stats 코드를 제거하고 QEMU native provider와
QBox를 다시 빌드한 뒤 실행했으며 같은 조건으로 통과했다. 해당 `result.json`에는
제거한 `flash_stats` 필드가 없다.

## 5. Yocto 검증

`./yocto_build.sh --machine apollo-qvp --keep-conf`는 7,293 tasks를 모두
완료했다. Yocto-owned QEMU와 QBox provider를 사용한 결과는 다음과 같다.

| run | 전체 | handoff -> BL33 | BL33 -> FWU | handoff -> FWU | state |
|---|---:|---:|---:|---:|---|
| cold | 28.144초 | 2.010초 | 4.629초 | 6.639초 | reset |
| reuse | 22.716초 | 1.106초 | 1.510초 | 2.616초 | reused |

Yocto PS hash는 image identity에 따라 local과 다르지만 cold/reuse 사이에서
`48ecad538c21e90a5e0808bc591ad4fde925ded5158a51d7a68941e129c24a7d`로
보존됐다. ITS hash도 local과 같은 `7acc7e...f649`로 보존됐다.

증거:

- `build/qbox-apollo-qvp/yocto-cold-qemu-cfi-v6-20260718/`
- `build/qbox-apollo-qvp/yocto-reuse-qemu-cfi-v6-20260718/`
- `build/qbox-apollo-qvp/yocto-default-backend-smoke-20260718/`

Yocto provider를 기본값 전환 뒤 다시 설치한 다음 backend 옵션 없이 실행한 마지막
스모크도 `qemu-cfi-local`, `action=reused`, `storage_preserved=true`, PS/ITS
무변경으로 통과했다.

## 6. FVP 비교

같은 2026-07-18 Yocto deploy image를 FVP에서 70초 이상 관찰했다. 전체 FVP
result는 pass이고 error term은 없었다. 다음 순서가 QBox와 일치한다.

```text
FW_CONFIG
SECURE_RT_EL3
HW_CONFIG
SECURE_RT_EL1_SPMD
BL_33
EFI: MM partition ID 0x8006
FWU: ABI version 1.0 detected
FWU: System booting in Regular State
```

FVP marker는 RSE handoff 12.282초, BL33 14.145초, MM partition 18.990초,
FWU Regular 23.094초에 관찰됐다. emulator 간 절대 시간은 합격 조건으로 사용하지
않았다.

증거:

- `build/fvp-boot-logs/apollo-qvp-cold-reference-20260718/result.json`
- 같은 디렉터리의 subsystem UART log

## 7. 실행한 핵심 검증

```bash
/home/cometzero/.local/bin/python3.12 -m pytest -q \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_run_qbox_local_sh.py \
  tests/test_run_qbox_yocto_sh.py \
  tests/test_runfvp_log_boot.py

./local_build.sh qbox
source layers/poky/oe-init-build-env build
bitbake qbox-libqemu-native -c compile -f
bitbake qbox-apollo-qvp-native -c compile -f
./yocto_build.sh --machine apollo-qvp --keep-conf
```

- Python runner: 107 passed (계측 전용 2건 제거 후 최종 기준)
- Strata component: 33 passed
- 임시 QEMU initiator profile test: 1 passed 후 계측 코드와 함께 제거
- `validate_qbox_apollo_fvp_full_map.py`: pass
- `audit_qbox_core_boundary.py`: pass
- QEMU native/provider compile: pass
- QBox local/Yocto provider build: pass
- local cold/reuse: pass/pass
- Yocto cold/reuse: pass/pass
- local/Yocto default-backend reuse smoke: pass/pass
- local cleanup default-backend reuse smoke: pass
- FVP same-image reference: pass

## 8. 남은 제한과 분리 부채

- 16 CPU는 범위 밖이며 기본 4 CPU만 검증했다.
- abrupt host power loss나 `SIGKILL`의 25ms writeback window는 별도 crash-durability
  시험 대상이다. 정상 runner 종료, reset, migration 경계와 이번 cold/reuse에서는
  cleanup 전 임시 통계로 pending dirty sector가 0임을 확인했다.
- 기존 Apollo topology test 26건 중 3건은 cold 변경과 무관한 baseline 계약
  불일치로 실패한다. 대상은 AP-RSE carveout backing-size 두 항목과
  `host_ap_bl2_header_sram.reset` 기대값 한 항목이다. full-map validator와 QBox core
  boundary audit는 통과했으며 이 보고서에서 해당 선행 architecture 부채를 수정하지
  않았다.
- component인 TF-A, TF-M, U-Boot, OP-TEE, Trusted Services 소스는 수정하지 않았다.

## 9. 결론

계획의 H1과 QEMU-local H3 decision gate를 모두 적용했고, component 우회 없이 live
AP/RSE MHU, measured boot, SMM Gateway `0x8006`, PS/ITS persistence를 유지했다.
선택한 병목 경계의 비용이 줄고 local/Yocto/FVP 기능 gate가 통과했으므로
`qemu-cfi-local`을 Apollo QVP 4-CPU 기본 RSE boot-flash backend로 채택한다.
`systemc-strata`는 비교와 rollback을 위해 계속 지원한다.

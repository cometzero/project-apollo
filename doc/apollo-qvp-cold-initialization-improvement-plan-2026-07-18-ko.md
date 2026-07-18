# Apollo QVP cold initialization 개선 계획

- 작성일: 2026-07-18
- 상태: 구현·local/Yocto/FVP 검증 완료
- 대상: `apollo-qvp`, cfg2, Primary Compute 4 CPU
- 측정 종료점: `FWU: System booting in Regular State`
- 구현 경계: `qbox`, `qbox-platform`, 필요 시 로컬 `qemu`

> 최종 cleanup에서 P0/P1의 일회성 profile option과 계측 코드는 제거했다. 현재
> cold 재현은 `--uboot-only`, `--rse-flash-state`,
> `--reset-rse-flash-state` 조합을 사용한다.

## 1. 목적

erased PS/ITS를 사용하는 첫 부팅에서 RSE Protected Storage 초기화와 UEFI
non-volatile 변수 생성 때문에 늘어난 host 실행 시간을 줄인다. 정상적으로 보존된
PS/ITS를 재사용하는 두 번째 부팅은 별도 문제로 취급하며, cold 개선 때문에 live
firmware 경로와 저장소 의미가 바뀌지 않게 한다.

이 문서는 다음 질문에 답하기 위한 실행 계획이다.

1. cold 비용이 TF-A, U-Boot, RSE TF-M, MHU, QEMU/SystemC, backing write 중
   어디에서 발생하는가?
2. firmware 소스를 최종 수정하지 않고 어느 virtual-platform 경계에서 비용을
   줄일 수 있는가?
3. FVP와 같은 observable behavior를 유지했는지 최소 비용으로 어떻게 검증할
   것인가?

## 2. 범위와 불변 조건

### 2.1 포함 범위

- 4 CPU Apollo QVP만 사용한다. 16 CPU는 다루지 않는다.
- RSE runtime handoff 이후 TF-A measured boot부터 U-Boot FWU Regular State까지를
  cold initialization 범위로 본다.
- local QBox image로 먼저 구현·검증하고 같은 변경을 Yocto QBox provider로
  검증한다.
- FVP는 동일 image의 기능 순서와 요청 결과를 확인하는 reference로 사용한다.

### 2.2 제외 범위

- Linux 진입 이후 부팅 시간
- synthetic PS response를 기본 경로로 복구하는 방법
- 미리 생성한 UEFI 변수를 image에 주입하는 방법
- TF-A, TF-M, U-Boot, OP-TEE 또는 Trusted Services 알고리즘의 제품 변경
- 절대 시간이나 CPU 성능 수치를 pass/fail 조건으로 추가하는 일

component 소스에는 분석용 로그를 임시로 추가할 수 있지만 최종 image를 만들기
전에 모두 제거한다.

### 2.3 fidelity 불변 조건

- `QBOX_RDASPEN_RSE_PS_PROXY=false`인 live AP/RSE MHU 경로를 유지한다.
- TF-A measured-boot slot 8~12와 요청 순서를 유지한다.
- U-Boot가 실제 SMM Gateway partition `0x8006`을 동기 호출하게 한다.
- Trusted Services의 index A/B 전환, RSE PS SET/REMOVE, TF-M flash layout을
  우회하지 않는다.
- cold 후 생성된 PS/ITS가 다음 부팅에서 같은 내용으로 재사용되어야 한다.
- CFI status, program, erase, reset, backing persistence와 외부 initiator 관찰 결과를
  보존한다.

## 3. 현재 증거로 확정된 사실

### 3.1 회귀가 아니라 fidelity 경로 활성화

QBox platform commit `326740463f11`(`fix(apollo): route live firmware peers`)은
AP/RSE 기본 protocol을 `rse-ps-proxy`에서 `doorbell-bridge`로 변경했다.
동일한 현재 firmware와 빈 state에서 route만 바꾼 A/B 결과는 다음과 같다.

| route | BL33 marker -> FWU Regular | 해석 |
|---|---:|---|
| live RSE PS | 26.266초 | 실제 RSE TF-M PS 실행 |
| synthetic proxy | 1.006초 | PS 실행 우회 |

따라서 최근 느려진 이유는 firmware 회귀가 아니라 이전에 보이지 않던 실제 cold
PS 작업이 QBox에서 실행되기 시작했기 때문이다. proxy는 원인 분리용 A/B로만
사용하고 개선안으로 사용하지 않는다.

증거:

- `build/qbox-apollo-qvp/storage-preserve-local-cold-20260718/`
- `build/qbox-apollo-qvp/cold-ab-proxy-20260718/`

### 3.2 cold 비용은 두 구간에 존재

Yocto의 같은 4 CPU image를 headless, U-Boot-only 조건으로 실행한 host monotonic
marker를 비교했다.

| 구간 | cold `created` | reuse `reused` | cold 추가 비용 |
|---|---:|---:|---:|
| RSE runtime handoff -> TF-A `BL_33` 요청 직전 log marker | 9.845초 | 1.407초 | 8.438초 |
| TF-A `BL_33` log marker -> U-Boot FWU Regular | 26.566초 | 1.610초 | 24.956초 |
| RSE runtime handoff -> FWU Regular | 36.410초 | 3.017초 | 33.393초 |

RSE 시작부터 runtime handoff까지는 cold 16.167초, reuse 16.267초로 사실상 같다.
병목은 RSE boot 자체가 아니라 runtime PS service가 AP 요청을 처리하기 시작한 뒤에
국한된다.

현재 TF-A 구현은 `log_measurement()`를 출력한 다음 blocking `psa_call()`을
호출한다. 따라서 첫 구간에는 BL33 이전 measured-boot 요청들이 포함되고, 두 번째
구간에는 BL33 PSA 호출, 남은 TF-A handoff, U-Boot UEFI/FWU가 함께 포함된다. 기존
marker만으로 TF-A와 U-Boot의 경계를 정확히 나눌 수 없으므로 P0에서 호출 전·후
timestamp marker를 별도로 추가한다.

`result.json`의 `primary_login_prompt` label은 현재 Linux login prompt라는 오래된
표현을 쓰지만 실제 marker는 `FWU: System booting in Regular State`이다. 후속 계측
문서와 JSON schema에서는 `fwu_regular_state`로 명확히 바꾼다.

증거:

- `build/qbox-apollo-qvp/yocto-cold-flash-stats-20260718/result.json`
- `build/qbox-apollo-qvp/yocto-reuse-flash-stats-20260718/result.json`

### 3.3 FVP 로그가 제공하는 것과 제공하지 않는 것

FVP `u_boot_linux.log`에서도 다음 기능 순서는 QBox와 같다.

```text
Disk virtio-blk#3 not ready
Disk virtio-blk#4 not ready
EFI: MM partition ID 0x8006
FWU: ABI version 1.0 detected
FWU: System booting in Regular State
```

현재 FVP UART 파일에는 각 행의 host monotonic timestamp가 없으므로 기존 파일만으로
FVP cold wall time이나 요청별 시간을 수치 비교할 수는 없다. FVP는 현재 기능 순서
증거이고, 성능 비교에는 timestamp 수집 보완이 필요하다.

참조 로그:

- `build/fvp-tmux/apollo-qvp-20260717-223809/uarts/u_boot_linux.log`
- `build/fvp-tmux/apollo-qvp-20260717-091507/uarts/u_boot_linux.log`

### 3.4 Arm Zena CSS architecture 정합성

Arm Zena CSS 개발 가이드도 live service 경로를 유지해야 한다는 결론을 뒷받침한다.

- RSE는 host boot measurement를 수집하는 Root of Trust이며, RSE runtime은 Primary
  Compute가 기동된 뒤 사용할 security service를 제공한다.
- AP Domain 0과 RSE 사이에는 secure/non-secure MHU send/receive frame이 명시되어
  있다. 따라서 measured boot와 UEFI persistent service를 synthetic proxy로
  우회하는 것은 최종 architecture가 될 수 없다.
- 개선 대상은 firmware가 기대하는 RSE·MHU·persistent storage 흐름이 아니라 이를
  실행하는 QEMU/SystemC 경계와 flash backend의 host 비용이다.

참조:

- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md:11`
- `doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md:135`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:364`

## 4. 코드 경로 분석

### 4.1 TF-A measured boot 구간

Apollo TF-A BL2는 FW_CONFIG, HW_CONFIG, BL31, BL32, BL33의 다섯 image를 slot
8~12에 측정한다.

```text
plat_mboot_measure_image()
  -> rse_mboot_measure_and_record()
     -> image hash
     -> rse_measured_boot_extend_measurement()
        -> blocking psa_call(RSE_MEASURED_BOOT_EXTEND)
        -> AP/RSE MHU
        -> RSE TF-M Measured Boot partition
        -> RSE PS
```

관련 코드:

- `hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/
  automotive_rd/platform/apollo_qvp/apollo_qvp_measured_boot.c:27`
- `hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/
  measured_boot/rse/rse_measured_boot.c:62`
- `hsoc-stack/components/primary_compute/trusted-firmware-a/lib/psa/
  measured_boot.c:65`

secure-console과 RSE 로그에는 cold/reuse 모두 `FW_CONFIG`, `SECURE_RT_EL3`,
`HW_CONFIG`, `SECURE_RT_EL1_SPMD`, `BL_33` 요청이 같은 순서로 보인다. cold에서만
이 구간이 약 8.44초 늘므로 measured-boot hash 자체뿐 아니라 첫 PS layout 생성과
각 slot의 persistent record가 계측 대상이다.

### 4.2 U-Boot UEFI/FWU 구간

U-Boot `efi_variable_tee`는 shared buffer 복사 후 SMM Gateway에 blocking FF-A direct
request를 보낸다. `EFI: MM partition ID 0x8006` 다음의 긴 구간은 이 동기 호출 안에서
발생한다.

```text
U-Boot efi_set_variable_int()
  -> ffa_mm_communicate()
     -> ffa_notify_mm_sp()
        -> ffa_sync_send_receive(0x8006)
        -> SMM Gateway / UEFI variable store
        -> SE-Proxy / AP-RSE MHU
        -> RSE TF-M PS
```

관련 코드:

- `hsoc-stack/components/primary_compute/u-boot/lib/efi_loader/
  efi_variable_tee.c:184`
- `hsoc-stack/components/primary_compute/u-boot/lib/efi_loader/
  efi_variable_tee.c:284`

이전 임시 계측에서 cold variable 요청은 `Boot0000`, `BootOrder`, `Boot0001`,
`BootOrder` 갱신, `PlatformLang` 순으로 처리됐고 대부분의 시간이 각 blocking FF-A
호출 안에 있었다. shared-buffer copy와 cache maintenance는 주 병목이 아니었다.

### 4.3 Trusted Services 요청 증폭

Yocto가 checkout한 SMM Gateway의 `uefi_variable_store_set_variable()`은 NV create나
update일 때 변수 data보다 index를 먼저 저장한다.

```text
one UEFI SetVariable
  -> sync_variable_index()
     -> REMOVE(next A/B index UID)
     -> SET(next A/B index UID, serialized index)
  -> store_variable_data()
     -> SET(variable UID, payload)
```

관련 코드:

- `build/tmp_baremetal/work/cortexa720-poky-linux/ts-sp-smm-gateway/
  1.3.0+git/git/trusted-services/components/service/uefi/smm_variable/
  backend/uefi_variable_store.c:228`
- 같은 파일의 `sync_variable_index():777`
- 같은 파일의 `store_variable_data():1602`

따라서 U-Boot variable 5건을 MHU request 5건으로 가정하면 안 된다. index A/B의
REMOVE/SET과 payload SET을 별도로 세어야 한다. 이 소스는 generated Yocto checkout
이므로 최종 구현 대상이 아니라 임시 분석 지점이다.

### 4.4 TF-M PS/ITS flash 특성

Apollo RSE flash는 64 MiB이고 signed image 뒤에 PS 1 MiB와 ITS 256 KiB가 놓인다.
PS/ITS program unit은 모두 1 byte이며 PS logical block은 4개의 4 KiB sector로
구성된다.

- `rse_memory_sizes.h:40`: image 48 MiB
- `rse_memory_sizes.h:42`: PS 1 MiB
- `rse_memory_sizes.h:44`: ITS 256 KiB
- `flash_layout.h:196`: PS offset
- `flash_layout.h:200`: PS sectors per block 4
- `flash_layout.h:202`: PS program unit 1
- `flash_layout.h:223`: ITS program unit 1

현재 Strata 통계에서 write-buffer command는 0회이고 모든 변경이 byte word-program
sequence로 수행된다. 한 byte 변경마다 program command, data write, status read,
clear status, read-array 복귀가 반복되므로 flash payload보다 MMIO 수가 훨씬 커진다.

### 4.5 QEMU/SystemC hot path

RSE CPU의 일반 MMIO 한 건은 QBox core의 `QemuInitiatorSocket::qemu_io_access()`에서
새 TLM payload와 extension을 만들고 `do_regular_access()`로 진행한다.
`do_regular_access()`는 매 접근마다 다음을 수행한다.

1. QEMU iothread lock 해제
2. `run_on_sysc()`로 SystemC thread에서 `b_transport()` 실행
3. QEMU iothread lock 재획득
4. DMI hint 확인과 local time 반영

관련 코드:

- `hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h:658`
- `hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h:704`

현재 cold 한 번의 flash access는 2,778,000회다. 정확한 wall-time 비중은 아직
계측하지 않았지만, 이 횟수만으로도 가장 먼저 분리 측정할 경계다. 쓰기 가능한 CFI
range는 command state 때문에 DMI로 단순 치환할 수 없다.

### 4.6 Strata model과 backing write

현재 `strata_flash_j3::b_transport()`는 simulated program delay를 추가하지 않고
즉시 access를 처리한다. Linux backing file은 `mmap(MAP_SHARED)` 후 `memcpy()`로
갱신하며 각 flush에 `msync()`나 `fsync()`를 호출하지 않는다.

현재 dirty tracker는 여러 sparse write를 하나의 min/max 범위로 합친다. cold에서
실제 changed/deferred bytes 약 400 KiB가 누적 flush range 52 MiB가 됐다. 이는
개선 가능한 write amplification이지만, 52 MiB 메모리 복사만으로 33초 전체를
설명할 수는 없다. backing coalescing을 주 병목으로 단정했던 기존 우선순위는
철회한다.

관련 코드:

- `strata_flash_j3.h:637`: min/max dirty tracking
- `strata_flash_j3.h:655`: deferred flush
- `strata_flash_j3.h:710`: `mmap` backing `memcpy`
- `strata_flash_j3.h:779`: program semantics
- `strata_flash_j3.h:1465`: zero-delay `b_transport`

### 4.7 기존 QEMU CFI model 재사용 가능성

QBox core에는 이미 QEMU `cfi.pflash01`/`cfi.pflash02`를 감싸는 `pflash_cfi`가 있다.
현재 wrapper는 QEMU device의 MemoryRegion을 `QemuTargetSocket`으로 SystemC에
export하지만, 같은 QEMU instance의 RSE CPU address space에 직접 local-map하는
option은 없다.

- `hsoc-stack/tools/qbox/qemu-components/pflash_cfi/include/pflash_cfi.h:17`
- `hsoc-stack/tools/qbox/qemu-components/common/include/ports/target.h:97`
- `hsoc-stack/tools/qemu/hw/block/pflash_cfi01.c:385`
- `hsoc-stack/tools/qemu/hw/block/pflash_cfi01.c:457`

QEMU pflash는 CFI status/program/erase/write-buffer를 구현하므로 local execution의
출발점으로 적합하지만 바로 교체할 수는 없다.

- 현재 Apollo Strata는 sector-aligned single-byte `0xff` program을 sector erase로
  해석하는 compatibility 동작을 사용한다.
- QEMU pflash는 program마다 backing을 512-byte sector로 넓혀 `blk_pwrite()`한다.
- 외부 AP/RSE ATU initiator도 RSE CPU와 같은 flash state를 봐야 한다.

따라서 QEMU pflash는 기능 A/B prototype을 먼저 만들고 이 세 차이를 해결한 뒤에만
기본 backend 후보가 된다.

## 5. cold/reuse flash 통계 해석

| 항목 | cold | reuse | 배수/차이 |
|---|---:|---:|---:|
| total accesses | 2,778,000 | 41,900 | 약 66배 |
| write accesses | 1,872,070 | 15,360 | 약 122배 |
| word-program commands | 312,012 | 2,560 | 약 122배 |
| changed bytes | 155,665 | 0 | cold only |
| no-op program bytes | 155,737 | 2,550 | cold에서 대량 발생 |
| sector erase | 610 | 10 | 61배 |
| backing write calls | 155,727 | 0 | cold only |
| backing logical bytes | 409,617 | 0 | cold only |
| deferred flushes | 152 | 0 | cold only |
| 누적 flush range | 52,352,888 | 0 | min/max amplification |

증거:

- `build/qbox-apollo-qvp/yocto-cold-flash-stats-20260718/
  rse-strata-stats.json`
- `build/qbox-apollo-qvp/yocto-reuse-flash-stats-20260718/
  rse-strata-stats.json`

통계가 지지하는 결론은 “cold가 flash command-heavy”라는 점까지다. 아래 비용의
비율은 아직 측정되지 않았다.

- RSE guest instruction 실행
- QEMU/SystemC thread handoff와 BQL 처리
- CFI state-machine 처리
- MHU request scheduling
- host backing copy/write

## 6. 가설과 우선순위

| 순위 | 가설 | 현재 근거 | 확정에 필요한 계측 |
|---|---|---|---|
| H1 | QEMU/SystemC 왕복이 지배 | 278만 access, 매 접근 lock/thread handoff | address-filtered `qemu_io_access` wall time |
| H2 | TF-M PS/flash guest loop가 지배 | 1-byte unit, 31만 program sequence | RSE PC sample과 symbol별 host time |
| H3 | backing write가 유의미 | 15만 dirty call, 52 MiB range | writeback on/off 및 flush 함수 wall time |
| H4 | FF-A/MHU scheduling이 유의미 | 모든 요청이 blocking | request별 transport와 RSE service time 분리 |
| H5 | stats/trace observer effect | 수백만 counter update 가능 | stats on/off cold A/B |

H1과 H2가 현재의 최우선 후보다. H3는 낮은 위험의 개선점이지만 측정 전에는
주 병목으로 취급하지 않는다. H4는 service 실행 시간을 제외한 순수 transport
wait가 큰 경우에만 수정한다.

## 7. 구현 전 계측 계획

### P0. 재현 계약과 결과 schema 고정

소유: top-level `scripts/`, `tests/`, `doc/`

1. `--cold-init-profile` runner option을 추가한다.
2. 매 실행마다 새 erased state를 만들고 source SHA-256, storage compatibility
   fingerprint, PS/ITS 시작·종료 hash를 `result.json`에 기록한다.
3. marker 이름을 다음처럼 고정한다.
   - `rse_runtime_handoff`
   - `tf_a_mboot_fw_config` ... `tf_a_mboot_bl33`
   - `uboot_mm_partition`
   - `uboot_variable_<name>`
   - `fwu_regular_state`
4. tmux 전역 환경을 사용하지 않는 headless runner에서만 성능 계측을 수행한다.
5. FVP runner도 같은 marker에 host monotonic timestamp를 붙인 sidecar JSON을
   생성한다. firmware UART text는 변경하지 않는다.

완료 조건은 cold/reuse/FVP 결과에서 같은 marker schema를 읽을 수 있는 것이다.

### P1. QBox-owned aggregate 계측

소유: `qbox`, `qbox-platform`

UART byte log 대신 종료 시 JSON aggregate만 기록한다.

1. `QemuInitiatorSocket`
   - RSE flash address filter
   - read/write 횟수와 bytes
   - `do_regular_access()` 전체 wall time
   - `run_on_sysc()` 대기+실행 wall time
   - BQL unlock/relock 전후 wall time
2. `strata_flash_j3`
   - `access`, `program`, `erase_sector`, `flush_deferred_backing` wall time
   - PS/ITS/image range별 command count
   - unique dirty sector와 min/max flush range를 동시에 기록
3. `mhu320ae`
   - AP notify, RSE IRQ, response, AP completion의 request sequence와 timestamp
   - request payload 전체를 출력하지 않고 service handle/function/size만 기록
4. `RseCpuAccel`
   - 기존 PC profile을 cold 구간에만 활성화
   - `symbols.json`을 이용해 TF-M PS, flash driver, MHU dispatch symbol별 sample을 집계

계측은 CCI parameter로 기본 off이며 통계 미사용 fast path를 바꾸지 않는다.

### P2. 임시 firmware phase marker

소유: 분석 중 component, 최종 diff 0

P1만으로 service 내부 구간이 분리되지 않을 때만 다음 로그를 임시 추가한다.

- TF-A: 각 sw_type의 hash 시작/끝과 `psa_call()` 시작/끝
- U-Boot: variable name/data size와 `ffa_sync_send_receive()` 시작/끝
- SMM Gateway: index dump, REMOVE, index SET, payload SET 시작/끝
- TF-M: PS init, filesystem scan/create, SET/REMOVE, flash program/erase 시작/끝

각 marker는 request당 한 줄만 출력한다. 결과를 수집한 뒤 component submodule을
원상태로 만들고 clean image에서 최종 검증한다.

## 8. 원인 분리 A/B 계획

모든 A/B는 같은 image/OTP와 서로 다른 새 erased state를 사용한다.

| 실험 | 바꾸는 항목 | 확인할 비용 | 최종 설정 사용 여부 |
|---|---|---|---|
| A0 | profile off/on | observer effect | off가 기본 |
| A1 | backing writeback on/off | persistence host 비용 | off는 진단 전용 |
| A2 | live/proxy | 실제 PS 전체 비용 상한 | proxy는 진단 전용 |
| A3 | Strata SystemC/QEMU-local CFI | QEMU/SystemC 경계 비용 | 기능 동등 시 후보 |
| A4 | MHU quantum 한 항목씩 변경 | 순수 scheduling 비용 | 결과에 따라 결정 |

판단 규칙은 다음과 같다.

1. RSE flash `do_regular_access()` 누적 wall time이 cold 추가 비용의 50% 이상이면
   QEMU-local CFI를 첫 구현으로 선택한다.
2. backing 함수 누적 wall time이 10% 이상이거나 A1이 유의미한 차이를 보이면
   dirty-sector coalescing을 구현한다.
3. MHU notify-to-dispatch와 response-to-completion의 합이 service 실행을 제외한
   cold 추가 비용의 20% 이상일 때만 scheduling을 수정한다.
4. RSE PC profile에서 PS/flash guest code가 지배하지만 local CFI 후에도 개선되지
   않으면 component 변경 없이 가능한 한계를 fidelity debt로 기록하고 upstream
   firmware 최적화 제안은 별도 문서로 분리한다.

이 수치는 최종 성능 합격 기준이 아니라 구현 대상을 고르는 decision gate다.

## 9. 원인별 구현 설계

### 9.1 H1 채택 시: QEMU-local CFI 단일 상태 모델

최우선 architecture 후보다. SystemC CFI access를 shortcut하는 대신 기존 open-source
QEMU pflash를 같은 RSE QEMU instance 안에 놓는다.

```text
RSE QEMU CPU
  -> QEMU local MemoryRegion (cfi.pflash01)
                          ^
AP/RSE external initiator |
  -> SystemC router -> QemuTargetSocket
```

두 경로가 같은 QEMU MemoryRegion과 backing을 사용하므로 flash 내용을 복제하지
않는다.

구현 단계:

1. QBox `pflash_cfi`에 optional `local_address`를 추가한다.
   - default는 disabled로 기존 platform 동작을 보존한다.
   - 같은 QEMU system memory에 device MMIO region을 map한다.
   - `QemuTargetSocket` export는 유지해 외부 initiator가 같은 region을 dispatch한다.
2. Apollo `rse.lua`에 실험 backend selector를 추가한다.
   - 기본 전환 전까지 `systemc-strata`가 default다.
   - `qemu-cfi-local`은 RSE CPU local map과 system-router export를 함께 만든다.
   - overlapping route와 이중 storage object가 생기지 않게 platform map validator를
     추가한다.
3. 로컬 QEMU `pflash_cfi01`에 Apollo에 필요한 optional compatibility를 추가한다.
   - sector-aligned single-byte `0xff` program의 sector erase 해석
   - property default off
   - program/status/read-array/erase sequence counter
4. QEMU block writeback 비용이 다시 지배할 때만 deferred dirty-sector writeback을
   추가한다.
   - guest-visible storage는 program 즉시 변경
   - disk write만 dirty-sector bitmap으로 지연
   - orderly stop, reset 전, snapshot/migration 경계에서 flush
   - current Strata보다 약한 crash durability가 되지 않게 명시적으로 비교
5. QEMU CFI ID/query table과 current Strata/FVP-visible 값이 다르면 Apollo parameter로
   맞추되 generic QEMU default는 바꾸지 않는다.

초기에 고려했지만 선택하지 않는 방식:

- `do_regular_access()`를 무조건 `do_direct_access()`로 변경: SystemC kernel 밖에서
  target을 호출하므로 wait/event/thread-safety 계약을 깨뜨릴 수 있다.
- CFI polling 결과를 QBox에서 합성: command ordering과 다른 initiator의 관찰을
  깨뜨린다.
- TF-M 함수 PC를 hook해 flash loop 전체를 건너뛰기: firmware implementation에
  종속되고 실제 hardware transaction을 없애므로 fidelity 목표에 맞지 않는다.

### 9.2 H3 채택 시: Strata dirty-sector coalescing

QEMU-local CFI 전환 여부와 독립적으로 적용할 수 있는 낮은 위험의 개선이다.

1. 단일 min/max dirty range를 4 KiB sector bitmap으로 교체한다.
2. flush 시 연속된 dirty sector만 extent로 합쳐 `memcpy()`한다.
3. `logical_changed_bytes`, `unique_dirty_bytes`, `host_copied_bytes`를 분리해 기록한다.
4. sparse write, adjacent write, erase, destructor flush, backing reload unit test를
   추가한다.

단, P1/A1에서 backing 비용이 작으면 이 단계는 성능 작업이 아니라 별도 maintenance
debt로 남기고 cold critical path보다 뒤로 미룬다.

### 9.3 H4 채택 시: MHU scheduling 조정

1. request sequence별 AP notify, RSE IRQ dispatch, response IRQ, AP completion을
   분리한다.
2. RSE service 실행 중 시간은 scheduling 비용에서 제외한다.
3. 순수 transport wait만 클 때 request/response 구간의 temporal quantum을 조정한다.
4. doorbell commit-on-notify, mailbox visibility, combined IRQ ordering을 그대로
   유지한다.
5. synthetic completion이나 service proxy는 사용하지 않는다.

## 10. 저장소별 구현 순서

### 단계 1: 계측 기반 마련

- top-level: runner option, marker schema, 결과 JSON, tests
- qbox: address-filtered initiator wall-time stats
- qbox-platform: Strata/MHU aggregate stats, RSE PC symbol aggregation
- component: 필요할 때만 임시 phase marker

산출물:

- `doc/apollo-qvp-cold-initialization-profile-report-<date>-ko.md`
- cold/reuse/FVP `result.json`
- boundary별 wall-time 합계와 PC hotspot

### 단계 2: architecture decision

P1/P2/A0~A4 결과를 이 문서의 decision gate에 대입한다. 결과 보고서에 다음 중 하나를
명시한다.

- `QEMU_LOCAL_CFI`
- `STRATA_DIRTY_SECTOR`
- `MHU_SCHEDULING`
- 둘 이상의 단계적 조합
- `FIRMWARE_DOMINANT_NO_SAFE_VP_FIX`

### 단계 3: 선택 구현

- QEMU-local CFI이면 qbox -> qemu -> qbox-platform 순으로 atomic하게 구현한다.
- Strata writeback이면 qbox-platform component와 unit test만 수정한다.
- MHU이면 qbox-platform MHU와 관련 unit test만 수정한다.
- component 임시 로그는 이 단계 시작 전에 제거한다.

### 단계 4: local 검증

1. 관련 C++ unit test
2. `git diff --check`
3. `./local_build.sh qbox`
4. 새 erased state로 4 CPU cold U-Boot-only 1회
5. 같은 state로 reuse U-Boot-only 1회

### 단계 5: Yocto 검증

1. active config 재확인
2. `source layers/poky/oe-init-build-env build`
3. 변경 provider의 targeted compile
   - qbox/qbox-platform: `bitbake qbox-apollo-qvp-native -c compile`
   - qemu 변경 포함 시: `bitbake qbox-libqemu-native -c compile`
4. `./yocto_build.sh`가 만든 같은 Apollo QVP image 사용
5. 새 erased state cold 1회, 같은 state reuse 1회

### 단계 6: FVP 비교와 clean 검증

1. 동일 Yocto image를 `run_fvp.sh --machine apollo-qvp`로 실행한다.
2. measured-boot sw_type 순서와 UEFI/FWU marker를 비교한다.
3. 모든 component 임시 변경이 없는지 recursive submodule status로 확인한다.
4. 계측 기본 off의 clean QBox image로 cold/reuse를 최종 1회씩 수행한다.

## 11. 최소 검증 기준

### 11.1 기능 gate

- `passed=true`, `blocker=null`
- live AP/RSE route 사용, proxy 비활성
- `EFI: MM partition ID 0x8006`
- `FWU: ABI version 1.0 detected`
- `FWU: System booting in Regular State`
- TF-A measured-boot slot/sw_type 순서 일치
- cold state action `created`, 다음 실행 `reused`
- cold 후 reuse에서 PS/ITS hash 보존
- CFI command/status/erase unit test 통과
- component submodule diff 없음

### 11.2 성능 관찰값

절대 합격 시간을 두지 않는다. 다음 값만 단계 전후 보고한다.

- RSE runtime handoff -> BL33
- BL33 -> FWU Regular
- flash MMIO 횟수와 `do_regular_access()` 누적 wall time
- Strata/QEMU CFI program·erase와 backing wall time
- MHU 순수 transport wall time
- RSE PS/flash symbol PC sample 비율

선택한 병목 경계의 비용이 줄지 않으면 기능이 통과해도 성능 개선은 실패로 기록하고
기본 backend로 전환하지 않는다.

## 12. 중단·rollback 조건

- QEMU-local CFI에서 PS/ITS hash나 UEFI 변수 순서가 달라짐
- 외부 initiator와 RSE CPU가 서로 다른 flash 내용을 관찰함
- reset 후 CFI mode/status가 current model 또는 FVP와 달라짐
- backing state가 orderly stop 후 보존되지 않음
- 임시 component 계측 없이는 동작하지 않음
- direct SystemC 호출처럼 thread-safety 계약을 검증할 수 없는 shortcut이 필요함

이 경우 실험 backend는 default로 전환하지 않고 `systemc-strata`로 rollback한다.

## 13. 예상 결론과 첫 실행 항목

현재 증거만으로 확정할 수 있는 첫 작업은 최적화 코드가 아니라 P0/P1 계측이다.
다만 278만 회의 lock/thread handoff와 기존 QEMU CFI wrapper의 존재를 고려하면
최우선 구현 후보는 **동일 QEMU MemoryRegion을 local CPU와 외부 TLM 양쪽에 노출하는
QEMU-local CFI 단일 상태 모델**이다.

실제 구현은 다음 순서로 시작한다.

1. cold marker schema와 FVP timestamp sidecar
2. RSE flash `QemuInitiatorSocket` wall-time aggregate
3. Strata access/backing wall-time aggregate
4. RSE PC profile symbol 집계
5. decision gate 검토
6. 선택된 backend prototype과 기능 검증

이 순서는 잘못된 병목을 먼저 최적화하는 일을 막으면서 component 소스 변경 없이
QBox/FVP fidelity를 유지하는 가장 짧은 경로다.

## 14. 실행 결과

2026-07-18에 이 계획을 완료했다.

- P0 marker/state/hash schema: 완료
- P1 QEMU initiator와 Strata aggregate profile: 완료 후 최종 소스에서 제거
- decision: `QEMU_LOCAL_CFI + DEFERRED_DIRTY_SECTOR`
- QEMU-local single MemoryRegion: 완료
- Cortex-M55 private CPU address-space mapping: 완료
- Apollo CFI `0xff` compatibility erase: 완료
- ROMD topology churn 제거용 opt-in I/O-only mode: 완료
- dirty-sector extent writeback과 timer/reset/migration flush: 완료
- local cold/reuse: pass/pass
- Yocto provider/image cold/reuse: pass/pass
- backend 옵션을 생략한 local/Yocto reuse smoke: pass/pass (`qemu-cfi-local`)
- 임시 계측 제거 후 local default-backend reuse smoke: pass
- 동일 Yocto image FVP marker 비교: pass
- component source 최종 변경: 없음
- 최종 cleanup: QBox initiator profile, QEMU CFI JSON 통계, Strata wall-time/unique
  dirty 통계와 runner profile option 제거

SystemC cold의 RSE handoff -> FWU 32.792초는 최종 QEMU-local cold에서
6.940초로 줄었다. PS/ITS cold hash는 backend 간 일치했고 reuse에서 보존됐다.
최종 구현, 명령, 수치와 남은 제한은
`doc/apollo-qvp-cold-initialization-profile-report-2026-07-18-ko.md`에 기록했다.

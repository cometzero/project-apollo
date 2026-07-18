# Apollo QVP U-Boot FWU 구간 지연 분석 및 수정 계획

## 1. 목적과 범위

이 문서는 `run_qbox_local.sh`와 `run_qbox_yocto.sh`로 Apollo QVP를 실행할 때
U-Boot 콘솔에서 관찰되는 다음 구간의 지연을 분석하고 수정하는 계획을 정의한다.

```text
Disk virtio-blk#3 not ready
Disk virtio-blk#4 not ready
EFI: MM partition ID 0x8006
<긴 대기>
FWU: ABI version 1.0 detected
FWU: System booting in Regular State
```

측정 범위는 U-Boot의 `FWU: System booting in Regular State`까지다. Linux 부팅과
로그인 시간은 분석 및 검증 기준에 포함하지 않는다. AP CPU는 현재 활성 구성인
4 CPU, QEMU TCG는 `MULTI`를 사용한다.

## 2. 결론

지연의 주원인은 virtio disk 탐색이나 FWU agent 초기화가 아니다. 매 실행마다
pristine RSE flash를 새 run directory로 복사하면서 RSE Protected Storage 상태를
초기화하기 때문에, U-Boot가 다음 비휘발성 UEFI 변수를 매번 다시 생성하는 것이
원인이다.

- `Boot0000`
- `BootOrder`
- `Boot0001`
- `BootOrder` 갱신
- `PlatformLang`

각 `SET_VARIABLE`은 FF-A direct request로 SMM Gateway에 전달되고, secure service
경로를 거쳐 RSE TF-M Protected Storage의 실제 flash 쓰기로 끝난다. QBox의 4 CPU
TCG 실행에서는 이 동기 쓰기들이 합산되어 약 20~30초의 host wall time을 만든다.

한 번 부팅하여 UEFI 변수가 생성된 RSE flash를 다음 실행에서 재사용하면 해당
쓰기들이 사라지고 `EFI: MM partition ID 0x8006`에서 FWU agent 시작까지의 시간이
29.011초에서 1.009초로 감소했다. 따라서 secure service를 우회하거나 U-Boot/TF-M을
변경하는 대신, QBox 실행 간 RSE 비휘발성 상태를 안전하게 보존하는 것이 우선
수정 방향이다.

## 3. 정량 증거

### 3.1 비계측 기준

| 이미지/실행 | EFI MM | FWU ABI 또는 Regular | 차이 |
|---|---:|---:|---:|
| local pristine flash | 31.251초 | 56.317초 | 25.067초 |
| Yocto pristine flash | 31.921초 | 56.933초 | 25.012초 |

`Disk virtio-blk#3 not ready`에서 `Disk virtio-blk#4 not ready`까지는 7ms,
두 번째 disk 메시지에서 EFI MM 메시지까지는 6ms였다. 따라서 화면상 바로 앞에
보이는 disk 메시지는 지연 원인이 아니다.

### 3.2 U-Boot 임시 계측

임시 계측은 분석용으로만 U-Boot에 추가했으며 최종 검증 전에 제거한다.
`copy`와 `invalidate_dcache_all()`은 각 요청에서 대체로 1ms 미만이었고,
대부분의 시간은 blocking `ffa_notify_mm_sp()` 내부에서 소비됐다.

| 순서 | 변수 | `ffa_notify_mm_sp()` guest time |
|---:|---|---:|
| 27 | `Boot0000` | 1.820초 |
| 30 | `BootOrder` | 2.653초 |
| 34 | `Boot0001` | 3.700초 |
| 38 | `BootOrder` | 1.665초 |
| 44 | `PlatformLang` | 4.213초 |

FWU agent의 partition discovery, service discovery, memory share, memory retrieve,
`FWU_DISCOVER`, directory read는 약 0.1~0.2초 범위였다. 따라서 이 구간을
“FWU agent가 25초 걸린다”라고 해석하면 안 된다.

### 3.3 동일 RSE flash 재사용 실험

| 항목 | pristine flash | 초기화된 flash 재사용 |
|---|---:|---:|
| EFI MM host marker | 31.872초 | 26.539초 |
| FWU agent host marker | 60.882초 | 27.549초 |
| EFI MM → FWU agent | 29.011초 | 1.009초 |
| `Boot####`/`BootOrder`/`PlatformLang` 신규 SET | 있음 | 없음 |
| 최종 U-Boot pass marker | 통과 | 통과 |

원본 RSE flash와 첫 부팅 후 writable RSE flash의 SHA-256도 서로 달랐다. 즉
Protected Storage 변경은 QBox가 사용하는 file-backed flash에 실제로 반영된다.
문제는 다음 실행이 그 변경된 파일을 사용하지 않고 다시 pristine image에서
시작한다는 점이다.

증거 디렉터리:

- `build/qbox-apollo-fvp/debug-uboot-only-local-20260717-231045/`
- `build/qbox-apollo-fvp/debug-uboot-only-yocto-20260717-231347/`
- `build/qbox-apollo-fvp/debug-smm-set-instrumented-local-20260717-2349/`
- `build/qbox-apollo-fvp/debug-smm-persisted-rse-local-20260718-0025/`

## 4. 실제 호출 구조

`trusted-firmware-a -> trusted-firmware-m`의 직접 함수 호출 구조는 아니다. TF-A
BL31의 SPMD는 FF-A 메시지를 라우팅하고, 실제 variable service는 OP-TEE SPMC가
호스팅하는 SMM Gateway와 SE-Proxy를 거친다.

```text
U-Boot efi_variable_tee
  -> FF-A direct request, destination 0x8006
  -> TF-A BL31 SPMD
  -> OP-TEE SPMC
  -> SMM Gateway SP
  -> UEFI variable store
  -> SE-Proxy SP 0x8004
  -> MHUv3 RSE communication
  -> RSE TF-M Protected Storage
  -> RSE Strata flash PS/ITS window
```

SMM Gateway의 non-volatile SET은 variable index 동기화와 실제 variable data 저장을
수행하므로 U-Boot의 SET 1회가 RSE Protected Storage의 REMOVE/SET 여러 회로
증폭될 수 있다. QBox는 이미 `--rse-fast-boot-sram-dmi`를 통해 storage window
direct-MMIO fast path를 사용한다. 이 fast path는 Strata CFI 모델과 저장 semantics를
유지하면서 QEMU/SystemC thread crossing을 줄이지만, pristine flash에서 반복되는
실제 non-volatile 쓰기 자체를 없애지는 않는다.

## 5. 수정 설계

### 5.1 설계 원칙

- U-Boot, TF-A, OP-TEE, TF-M, SE-Proxy 소스는 변경하지 않는다.
- SMM Gateway, FF-A, MHUv3, RSE Protected Storage 경로를 우회하지 않는다.
- AP flash와 OTP의 기존 per-run 복사 정책은 유지한다.
- local 이미지와 Yocto 이미지의 RSE 상태를 서로 섞지 않는다.
- 입력 RSE flash가 재빌드되어도 저장소 ABI와 device identity가 호환되면 PS/ITS만
  보존하고 새 firmware 영역을 사용한다.
- 저장소 ABI 또는 OTP identity가 바뀌면 이전 PS/ITS를 재사용하지 않는다.
- 회귀/디버깅을 위해 명시적인 초기화 및 ephemeral 실행 경로를 제공한다.

### 5.2 compatibility-aware persistent RSE flash state

low-level QBox runner에 persistent RSE flash state 파일을 선택하는 옵션을 추가한다.

1. pristine RSE flash의 SHA-256과 크기를 source provenance로 기록한다.
2. Apollo QVP 저장소 호환성 descriptor를 생성한다. descriptor에는 schema ID,
   flash image/PS/ITS offset과 size, RSE OTP SHA-256을 포함한다.
3. state와 sidecar metadata가 없으면 pristine flash를 64 MiB로 확장해 생성한다.
4. source hash/size와 compatibility fingerprint가 모두 같으면 기존 state를 그대로
   재사용한다(`reused`).
5. source만 바뀌고 fingerprint가 같으면 새 source로 임시 state를 만든 뒤 정확한
   PS/ITS 구간만 이전 state에서 복사하고 atomic replace한다
   (`storage-preserved`).
6. 명시적 reset, OTP 변경, layout/schema 변경, 구형 metadata는 pristine source로
   다시 초기화한다(`reset` 또는 `refreshed`).
7. state 파일은 QBox가 직접 쓰도록 하되 AP flash와 OTP는 기존처럼 run directory
   사본을 사용한다.
8. atomic replace와 non-blocking file lock을 사용하여 중단 또는 동시 실행 때문에
   state가 섞이지 않도록 한다.

Apollo QVP cfg2의 보존 구간은 firmware source가 아니라 TF-M layout을 기준으로 한다.

| 구간 | offset | size |
|---|---:|---:|
| RSE firmware image | `0x00000000` | `0x03000000` |
| Protected Storage | `0x03000000` | `0x00100000` |
| Internal Trusted Storage | `0x03100000` | `0x00040000` |
| 보존 합계 | `0x03000000` | `0x00140000` |

이 값은
`platform/ext/target/arm/rse/automotive_rd/apollo-qvp/rse_memory_sizes.h`와
`flash_layout.h`의 `RSE_FLASH_*` 정의에 맞춘 것이다. 이전 runner 값은 PS와 ITS
크기가 서로 바뀌어 있었으므로 source 변경 시 잘못된 1.0625 MiB를 보존할 위험이
있었다.

기본 state namespace는 다음처럼 분리한다.

```text
build/qbox-apollo-fvp/state/local-apollo-qvp/rse-flash-image.img
build/qbox-apollo-fvp/state/yocto-apollo-qvp/rse-flash-image.img
```

`run_qbox_local.sh`와 `run_qbox_yocto.sh`는 기본적으로 각자의 state 경로를 넘긴다.
직접 Python runner를 사용하는 자동화는 옵션을 명시하지 않는 한 기존 per-run
ephemeral 동작을 유지하여 재현성을 보존한다.

### 5.3 사용자 제어

- `--rse-state-dir DIR`: persistent state 위치 지정
- `--reset-rse-state`: 현재 이미지에서 state를 다시 생성
- `--no-persistent-rse-state`: 기존 per-run pristine 복사 방식 사용

실행 출력과 `result.json`에는 state 경로, source hash, 재사용/생성/갱신/reset 여부를
남긴다.

## 6. 구현 단계

1. low-level runner에 state 준비 함수, lock, metadata, 결과 보고를 추가한다.
2. Apollo full-system wrapper가 state 관련 옵션을 전달하도록 한다.
3. local/Yocto shell entrypoint에 기본 state namespace와 사용자 옵션을 추가한다.
4. 상태 생성, 재사용, compatible source 병합, incompatible identity refresh, reset,
   ephemeral 동작을 단위 테스트한다.
5. 임시 U-Boot/runner 계측을 제거하고 clean firmware를 재빌드한다.
6. local cold/reuse와 Yocto reuse를 U-Boot pass marker까지만 검증한다.

## 7. 최소 검증 기준

### 7.1 정적 및 단위 검증

```bash
python3 -m py_compile \
  scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run/run_qbox_apollo_fvp_full.py
python3 -m pytest -q \
  tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_local_sh.py \
  tests/test_run_qbox_yocto_sh.py
git diff --check
```

### 7.2 local runtime

- clean `./local_build.sh u-boot tf-a flash-images --no-package --jobs 8` 성공
- reset/cold 실행에서 `FWU: System booting in Regular State` 도달
- 같은 state를 재사용한 실행에서 동일 marker 도달
- reuse 실행의 EFI MM → FWU Regular 구간이 5초 이하
- `EFI-DIAG`, `FWU-DIAG`, `RSE-DIAG`가 최종 로그에 없음

### 7.3 Yocto runtime

- 기존 Apollo QVP Yocto image와 QBox provider를 사용
- `run_qbox_yocto.sh` headless/exit-after-pass 경로로 U-Boot Regular State 도달
- 같은 Yocto state를 재사용한 실행에서 EFI MM → FWU Regular 구간 5초 이하
- Linux 부팅 완료와 로그인 시간은 판정하지 않음

## 8. 제외 사항과 남은 부채

- 신규 build 또는 명시적 reset 후 첫 부팅의 Protected Storage 쓰기 비용은 남는다.
  이는 실제 초기화 작업이며 무조건 생략해서는 안 된다.
- FVP보다 첫 쓰기 자체가 과도하게 느린지 정밀 비교하려면 SMM Gateway index sync,
  SE-Proxy MHU wait, RSE TF-M PS handler, Strata erase/program에 각각 timestamp를
  추가해야 한다. 이번 수정은 반복 실행에서 불필요하게 같은 초기화를 되풀이하는
  문제를 우선 해결한다.
- 16 CPU 및 Linux 이후 성능은 현재 범위에 포함하지 않는다.

## 9. 구현 및 검증 결과

### 9.1 구현 결과

구현은 component 소스를 변경하지 않고 top-level QBox 실행 계층에만 반영했다.

- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
  - source provenance와 storage compatibility fingerprint 기반 persistent RSE flash
    생성·재사용·병합·갱신·reset
  - Apollo QVP PS 1 MiB, ITS 256 KiB layout 반영
  - state lock과 atomic image/metadata 갱신
  - `result.json`/`summary.txt` 상태 보고
- `scripts/run/run_qbox_apollo_fvp_full.py`
  - state 옵션 전달 및 상위 결과 승격
  - `--uboot-only` 검증 scope 추가
- `run_qbox_local.sh`
  - 기본 local state namespace 및 reset/ephemeral/U-Boot-only 옵션
- `run_qbox_yocto.sh`
  - 기본 Yocto state namespace 및 동일 사용자 옵션
- 관련 테스트 4개 파일
  - state 생성·재사용·reset·source 변경·동시 사용 차단
  - full wrapper 전달과 local/Yocto shell 계약

분석에 사용한 U-Boot `EFI-DIAG`/`FWU-DIAG`와 runner marker는 모두 제거했다.
`hsoc-stack/components/primary_compute/u-boot` 작업 트리는 원래 commit과 동일하다.

### 9.2 정적·빌드 검증

```text
python3 -m py_compile ...                         PASS
bash -n run_qbox_local.sh run_qbox_yocto.sh     PASS
/usr/bin/python3 -m pytest -q <관련 4개 파일>   95 passed
git diff --check                                 PASS
./local_build.sh u-boot tf-a flash-images \
  --no-package --jobs 8                          PASS
```

clean firmware 재빌드 시간은 U-Boot 2초, TF-A 8초, flash-images 35초였다.

### 9.3 local runtime 결과

| 실행 | state action | EFI MM | FWU Regular | 차이 | 판정 |
|---|---|---:|---:|---:|---|
| cold/reset | `reset` | 39.015초 | 72.663초 | 33.648초 | U-Boot 도달 |
| reuse | `reused` | 27.446초 | 27.849초 | 0.403초 | PASS |
| 최종 `--uboot-only` | `reused` | 27.419초 | 27.923초 | 0.504초 | PASS |

최종 증거:

- `build/qbox-apollo-fvp/uboot-state-fix-local-cold-20260718/`
- `build/qbox-apollo-fvp/uboot-state-fix-local-reuse-20260718/`
- `build/qbox-apollo-fvp/uboot-state-fix-local-final-20260718/`

### 9.4 Yocto runtime 결과

| 실행 | state action | EFI MM | FWU Regular | 차이 | 판정 |
|---|---|---:|---:|---:|---|
| cold/reset | `reset` | 37.796초 | 71.132초 | 33.337초 | U-Boot 도달 |
| reuse `--uboot-only` | `reused` | 26.419초 | 26.922초 | 0.503초 | PASS |

Yocto cold run은 요청 범위인 U-Boot에는 정상 도달했으나, 당시 기존 full-system
runner가 그 이후 CL1 `RPMSG Endpoint: ATTACHED`까지 기다려 overall result가
timeout으로 기록됐다. 이를 계기로 `--uboot-only` scope를 추가했고, 동일 Yocto
state 재사용 최종 실행은 `passed=true`, `blocker=null`,
`validation_scope=uboot-only`로 완료됐다.

최종 증거:

- `build/qbox-apollo-fvp/uboot-state-fix-yocto-cold-20260718/`
- `build/qbox-apollo-fvp/uboot-state-fix-yocto-reuse-20260718/`

### 9.5 최종 판정

- local과 Yocto 모두 reuse 구간이 5초 기준보다 충분히 짧다.
- secure service/FF-A/MHU/RSE PS 경로를 우회하지 않았다.
- source image가 변경되어도 layout/schema/OTP가 호환되면 새 firmware와 기존
  PS/ITS가 병합되고, 비호환일 때만 state가 갱신된다.
- final local/Yocto 로그에서 `EFI-DIAG`, `FWU-DIAG`, `RSE-DIAG`는 검출되지 않았다.
- 이번 범위의 blocker는 없다.

## 10. 후속 1~3 수정 결과

### 10.1 PS/ITS layout 수정

runner의 보존 범위를 TF-M Apollo QVP 정의와 동일하게 수정했다.

- PS: 64 KiB가 아니라 1 MiB
- ITS: 1 MiB가 아니라 256 KiB
- 보존 범위: `0x03000000..0x0313ffff`, 총 1.25 MiB

정적 테스트는 runner 상수가 TF-M header와 같은 범위를 덮고 state 최소 크기를
넘지 않는지 확인한다.

### 10.2 top-level state 보고 수정

tmux keep-running wrapper는 child가 실제 persistent state를 사용해도 상위
`result.json`에 `ephemeral`로 기록했다. low-level runner가 output directory에
`rse-flash-state.json`을 atomic write하고, 상위 wrapper가 이를 읽어
`result.json`과 `summary.txt`에 승격하도록 수정했다.

실제 local/Yocto cold 결과에서 모두 `enabled=true`, `action=created`가 기록됐고,
재사용 결과에서는 `reused`, source 변경 결과에서는 `storage-preserved`가 기록됐다.

### 10.3 compatible rebuild 상태 보존

source 전체 hash는 저장소 호환성을 뜻하지 않는다. firmware 코드 한 바이트만
바뀌어도 hash가 달라지지만 PS/ITS on-flash ABI와 device identity는 그대로일 수
있다. 따라서 source provenance와 storage compatibility를 분리했다.

local source의 firmware 유효 영역 밖 padding을 1바이트 변경해 재빌드를 모사한
결과는 다음과 같다.

| 항목 | 결과 |
|---|---|
| source SHA-256 전 | `169d7d51...f343eb5d` |
| source SHA-256 후 | `2751b58a...38b4324c` |
| state action | `storage-preserved` |
| PS/ITS SHA-256 전/후 | `7d1e9f0e...92881d77` / 동일 |
| U-Boot FWU Regular | PASS |
| BL33 -> FWU Regular | 1.811초 |

구형 metadata에는 fingerprint가 없으므로 처음 한 번은 보수적으로 refresh한다.
향후 TF-M PS/ITS format을 바꿀 때는 `RSE_STORAGE_SCHEMA_ID`를 함께 올려야 한다.

증거:

- `build/qbox-apollo-qvp/storage-preserve-local-cold-20260718/`
- `build/qbox-apollo-qvp/storage-preserve-local-rebuilt-20260718/`
- `build/qbox-apollo-qvp/storage-preserve-yocto-cold-20260718/`
- `build/qbox-apollo-qvp/storage-preserve-yocto-reuse-20260718/`

## 11. 최근 대규모 작업 이후 느려진 이유

### 11.1 회귀 지점

QBox platform commit `326740463f116489e0c8f08469423edc28db56ad`
(`fix(apollo): route live firmware peers`, 2026-07-17 22:53 KST)이 다음 기본값을
바꿨다.

```text
QBOX_RDASPEN_RSE_PS_PROXY: true -> false
```

변경 전에는 AP secure MHU 요청을 `rse-ps-proxy`가 synthetic response로 처리했다.
변경 후에는 `doorbell-bridge`, 실제 AP/RSE mailbox, RSE TF-M runtime, Protected
Storage, Strata flash까지 요청이 전달된다. 같은 commit에서 mailbox DMI를 끄고
notify 시 doorbell commit을 활성화해 live peer의 ordering도 맞췄다.

따라서 이는 U-Boot나 TF-M이 갑자기 느려진 단순 software 회귀가 아니다. 최근
fidelity 구현으로 이전에 우회되던 실제 cold initialization 경로가 활성화되면서
QBox의 성능 부채가 보이기 시작한 것이다. 같은 현재 firmware와 빈 state에서
proxy 설정만 바꾼 A/B가 이를 직접 재현한다.

| 동일 현재 image, 빈 state | BL33 -> FWU Regular | state |
|---|---:|---|
| 기본 live RSE PS (`false`) | 26.266초 | `created` |
| 이전 synthetic proxy (`true`) | 1.006초 | `created` |

proxy를 다시 기본 경로로 사용하는 것은 해결책이 아니다. FVP 수준 fidelity를
잃으므로 앞으로도 진단용 A/B에만 사용한다.

증거:

- live: `build/qbox-apollo-qvp/storage-preserve-local-cold-20260718/`
- proxy: `build/qbox-apollo-qvp/cold-ab-proxy-20260718/`

## 12. 실제 cold initialization 후속 계획

실제 cold initialization은 TF-A measured boot와 U-Boot UEFI variable 저장이 같은
RSE PS/flash 경로를 사용하므로 이 문서의 persistent-state 수정과 분리해 관리한다.
코드 경계, cold/reuse 통계, FVP 계측 공백, decision gate, QEMU-local CFI 설계와
단계별 검증은 다음 별도 문서에 정리했다.

- [Apollo QVP cold initialization 개선 계획](./apollo-qvp-cold-initialization-improvement-plan-2026-07-18-ko.md)

핵심 변경점은 backing range를 주 병목으로 미리 가정하지 않는 것이다. 우선
278만 회의 RSE flash MMIO에 대한 QEMU/SystemC thread handoff wall time, RSE guest
PC hotspot, backing write, MHU scheduling을 각각 계측한 뒤 결과에 따라 구현 backend를
선택한다. 현재 최우선 architecture 후보는 기존 QEMU pflash와 QBox wrapper를
확장해 RSE CPU local access와 외부 TLM access가 하나의 flash state를 공유하는
QEMU-local CFI 모델이다.

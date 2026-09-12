# Apollo QVP x2 PCIe NVMe SSD

## 모델과 연결

QBox의 기존 `nvme` wrapper와 QEMU native NVMe controller를 재사용한다.
새 NVMe command set이나 NAND 모델을 만들지 않는다. backing raw image가 SSD의
namespace 데이터를 저장하며 Linux는 upstream `nvme` driver로 접근한다.

SSD는 port-group 3, root `0000:00:04.0` 아래에 연결한다. 이 포트는 x2 고정이므로
다른 x2 포트(group 2)의 x1+x1 bifurcation과 관계없이 폭을 유지한다.
Apollo NVMe도 `x_speed="32"`, `x_width="2"`로 설정한다. QEMU NVMe의
`x-speed`/`x-width` property가 native PCIe helper를 통해 capability와 link 상태를 구성한다.
일반 QEMU/QBox NVMe의 기본값은 이전 Gen1 x1을 유지하고 Apollo에서만 명시적으로 선택한다.
PCI BAR와 MSI-X는 Linux가 할당하며 NVMe용 DT node나 별도 고정 IRQ를 추가하지 않는다.
PCI DMA는 기존 GPEX requester ID → SystemC SMMUv3 경로를 사용하고 MSI-X는 ITS로 전달한다.

| 설정 | 용도 |
| --- | --- |
| `QBOX_APOLLO_NVME_IMAGE` | 기존 raw 이미지의 절대 경로. 설정한 경우만 SSD 연결 |
| `QBOX_APOLLO_NVME_SERIAL` | serial, 기본 `APOLLO-NVME-SSD` |
| QBox `nvme.image_path` | 기존 이미지 파일. 생성·truncate하지 않음 |
| QBox `nvme.blob_file` | 기존 사용자를 위한 호환 alias |

실제 block device, 없는 파일, 옵션 파싱이 모호한 파일명은 거부한다.
NVMe와 PCI NIC/legacy IRQ test profile은 같은 슬롯 구성을 공유할 수 없어 동시 사용을 거부한다.
이미지는 read/write로 연결되며 `--copy-disks` 대상이 아니다. 이 옵션은 기존 boot disk만 복사한다.

## 빌드와 전용 이미지 생성

```bash
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp

mkdir -p build/nvme
nvme_test_dir=$(mktemp -d "$PWD/build/nvme/ssd.XXXXXX")
qemu-img create -f raw "$nvme_test_dir/ssd.raw" 256M
export QBOX_APOLLO_NVME_IMAGE="$nvme_test_dir/ssd.raw"
export QBOX_APOLLO_NVME_SERIAL=APOLLO-NVME-TEST
```

`write-read` 테스트는 해당 SSD의 일부 내용을 덮어쓴다. 기존 사용자 데이터가 있는
이미지를 사용하지 않는다. 전용 serial, 256MiB 크기, root port, NVMe driver/class,
namespace와 block device identity를 확인하고 partition·mount·swap·holder가 있으면 거부한다.

```bash
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/nvme/write-run --timeout 600 --keep-running-after-pass

timeout 600 ssh -o BatchMode=yes -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null -p 8022 root@127.0.0.1 sh -s write-read \
  < scripts/test/test_apollo_nvme.sh
```

이전 테스트의 QBox 프로세스만 종료하고, 같은 NVMe 이미지로 **새 QBox 프로세스**를
시작한다. 출력 디렉터리는 새 경로를 사용하며 기존 증거를 덮어쓰지 않는다.

```bash
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/nvme/verify-run --timeout 600 --keep-running-after-pass

timeout 600 ssh -o BatchMode=yes -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null -p 8022 root@127.0.0.1 sh -s verify-only \
  < scripts/test/test_apollo_nvme.sh
```

## 데이터 검증

스크립트 기본 모드는 `verify-only`이며 쓰기는 `write-read`를 명시해야 한다.
sector와 offset에 따라 달라지는 deterministic pattern을 만들어 SHA-256을 비교한다.
기존 BSP BusyBox `dd`에는 direct I/O 기능이 없어 coreutils의 `dd.coreutils`를 사용한다.
페이지 캐시를 우회하는 O_DIRECT와 fsync를 사용하며, block I/O 통계와 MSI-X 증가도 확인한다.

| 테스트 | 디스크 offset | 크기 | 요청 단위 |
| --- | --- | --- | --- |
| `page_4k` | 4MiB | 4KiB | 4KiB × 1 |
| `unaligned_8704` | 1MiB + 512 bytes | 8,704 bytes | 8,704 bytes × 1 |
| `large_4m` | 32MiB | 4MiB | 128KiB × 32 |

모든 쓰기는 처음 64MiB 안의 세 영역으로 제한한다. 두 번째 부팅은 pattern을 다시
생성해 동일 데이터인지 확인한다. 실제 전송 분할은 Linux/NVMe의 한도에 따르며
이 테스트만으로 특정 PRP/SGL 분할 형식을 단정하지 않는다.

## 변경 위치

- QBox: `qemu-components/nvme/include/nvme.h`, 해당 CMake include 경로.
- SystemC: `systemc-components/smmuv3/include/smmuv3.h`의 range TLBI와
  `tests/components/smmuv3/smmuv3-tests.cc` 회귀 검사.
- Platform: `platforms/apollo/hw-block/ap_compute.lua`, aggregate CMake와 README.
- Linux: `apollo_qvp_defconfig`에 `CONFIG_BLK_DEV_NVME=y`; NVME_CORE는 Kconfig가 선택한다.
- BSP: direct I/O 도구를 위해 `coreutils` 추가.
- Root: `scripts/test/test_apollo_nvme.sh`, PCI profile 검사와 runner의 NVMe 환경/이미지 기록.

## 검증 결과와 한계

검증일: 2026-09-12. `apollo-qvp` cfg2, AP 4 CPU, `systemc-mmu720ae` backend.
최종 근거는 `build/nvme/` 아래에 보존한다.

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| Linux NVMe 활성화 compile | PASS, 818 tasks | `kernel-compile.log` |
| coreutils 포함 BSP 재빌드 | PASS, 5793 tasks | `bsp-final.log` |
| SMMU 수정 반영 최종 BSP | PASS | `bsp-smmu.log` |
| QBox-platform/core recipe tests | 각각 60/60 PASS, 6.57초 / 18.86초 | `provider-check-qualified.log` |
| SMMUv3 단독 전체 tests | 156/156 PASS | `smmuv3-range/full.log` |
| Host profile/runner tests | 28/28 PASS | `host-tests.log` |
| NVMe write-read | 3/3 hash 일치, direct I/O PASS | `write-fixed/nvme-test.log` |
| 새 QBox 프로세스 verify-only | 3/3 hash 일치, write I/O 0 | `verify-fixed/nvme-test.log` |
| Host raw 데이터 | 세 영역 모두 guest 기대 hash와 일치 | `write-fixed/host-region-hashes.txt` |
| 재시작 전후 SSD 전체 hash | 동일 | `verify-fixed/host-image-check.log` |
| RC–EP 회귀 | 재실행 boot PASS, Linux 6/6 PASS, MSI 0→47, cleanup PASS | `ep-regression-retry/endpoint-test.log` |

Linux는 `nvme0` / `nvme0n1`, PCI `0000:04:00.0`, class `0x010802`, driver `nvme`,
IOMMU group 5로 인식했다. namespace는 256MiB, logical block size 512 bytes다.
`write-read`의 block 통계는 read 34 / write 37 I/O, 각 8,217 sectors였고 MSI-X는
41→112(+71)였다. 새 프로세스의 `verify-only`는 read 34 / write 0 I/O,
8,217 read sectors, MSI-X 41→75(+34)를 기록했다.

사용한 SSD는 `build/nvme/ssd.1oB6Mk/ssd.raw`이며 시험 데이터를 포함한 상태로 남긴다.
`before.sha256`, `after-write.sha256`은 해당 디렉터리에 있다.
모델/Lua hash는 `model-artifacts.sha256`, boot image hash는 각 run의
`initial-state.json`, NVMe 파일 경로/크기와 환경은 `result.json`에 기록된다.
시험 종료 후 이 작업의 QBox 프로세스만 종료했으며 SSD 이미지는 보존했다.

위 초기 검증에서는 root port는 Gen5 x2였지만 NVMe의 reported link는
Gen1 x1이었다. 이는 Gen5 설정 추가 전의 기록이며, 현재 설정의 검증은 아래 절과 구분한다.
Linux의 `Ignoring bogus Namespace Identifiers` 메시지도 native QEMU identity 처리로
남아 있으며 namespace 인식이나 데이터 검증 실패는 발생하지 않았다.

전체 플랫폼 coverage audit는 `ap_9_1_1_memory_map=not_available`, `gate:G1=not_run`으로
실패했다(`full-coverage-audit.json`). NVMe 기능 검증을 전체 플랫폼/FVP parity PASS로
확대하지 않는다. 최종 빌드의 forced-task taint 경고 5개는 실패와 별도로 기록했다.

### 발견한 실패와 원인

- 추가 RC–EP 회귀의 첫 `ep-regression` 부팅은 RSE BL2가 SCP 준비를 기다리다
  `SCP is not ready. Abort`로 중단됐고 RunOnSysc 예외가 기록됐다.
  Linux/NVMe 시험 전의 실패이며, 이 부팅 문제는 본 작업에서 수정하지 않았다.
  새 `ep-regression-retry` 부팅과 6개 endpoint 테스트는 모두 통과했다.
- 최초 BSP 실행 `build/nvme/bsp-build.log`는 실행 중 coreutils를 image recipe에
  추가하여 basehash/taskhash mismatch가 발생했다. 메타데이터를 고정한
  `bsp-final.log` 재실행은 오류 없이 완료했다. 모델 오류로 분류하지 않는다.
- 최초 NVMe 실행 `write-run/nvme-test.log`와 재실행은 4KiB 검사는 통과했지만
  8,704-byte read의 SHA-256이 불일치했다. 이 실패를 timeout/skip으로 제외하지 않았다.
- `write-run/mismatch.expected`와 `mismatch.actual`을 보존했다. 처음 4,096 bytes는
  같고 이후 4,608 bytes는 0이었다. 반면 host raw image의 같은 영역은 기대 hash와 일치했다.
- SMMUv3 range TLBI 처리에서 `NUM`을 무시하는 문제가 발견됐다.
  Linux는 word0의 NUM[16:12], SCALE[24:20]으로 `(NUM+1)<<SCALE`개의 granule을 지정한다.
  기존 모델은 NUM=2, SCALE=0의 3-page 무효화에서도 첫 page만 제거했다.
  TG도 word1[11:10] 대신 word0에서 읽고 있었다.

NH_VA, NH_VAA, S2_IPA의 범위를 공통 interval-overlap 방식으로 처리하도록 수정했다.
NUM+1이 3처럼 2의 거듭제곱이 아닌 경우도 정확한 범위를 제거한다.
SCALE mask도 4bit에서 명세의 5bit로 수정했다. 관련 회귀 8/8 및 전체 SMMUv3
156/156이 통과했다(`build/nvme/smmuv3-range/focused.log`, `full.log`).
SCALE 상위 비트의 수정 전 실패는 `scale-red.log`에 보존했다.
3-page 수정 전 IOTLB 잔여 2개 실패도 실행으로 확인했으나 별도 RED 파일은 저장하지 않았다.

WRITE의 device-read-only mapping이 READ의 device-write mapping으로 교체될 때
마지막 두 page의 이전 IOTLB permission이 남아 DMA writeback이 거부됐다.
QEMU bounce-buffer unmap은 MemTxResult를 상위 NVMe completion으로 반환하지 않아
I/O 완료만으로는 이 데이터 손상을 발견할 수 없었다. 체크섬 검증이 필요한 이유다.
정상 I/O 외의 잘못된 DMA 주소에 대한 NVMe CQE error propagation은 이 검증의 보장 범위가 아니다.

이 모델은 NVMe protocol, queue, PCI DMA/IRQ와 저장 데이터의 기능 검증용이다.
NAND wear/FTL, SSD 전력·열·실제 지연시간, PHY 신호와 실효 Gen5 대역폭은 검증하지 않는다.
Root port의 Gen5 x2 최대 capability와 native endpoint의 reported link 상태는 구분한다.

## NVMe Gen5 x2 설정 검증

QEMU `hw/nvme/ctrl.c`, `hw/nvme/nvme.h`의 link property와 QBox NVMe wrapper를
연결하고 Apollo Lua에서 32GT/s x2를 선택한다. Guest 검증은 root와 endpoint 모두의
maximum/current speed와 width를 필수 검사한다. 실제 PHY 신호나 Gen5 실효 대역폭을
모델링하는 변경은 아니다.

검증 결과(`build/nvme-gen5/`):

| 대상 | maximum | current |
| --- | --- | --- |
| Root `0000:00:04.0` | 32.0GT/s x2 | 32.0GT/s x2 |
| NVMe `0000:04:00.0` | 32.0GT/s x2 | 32.0GT/s x2 |

- `./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`: PASS, 5793 tasks.
- Provider tests: platform 60/60 (6.68초), core 60/60 (18.80초); host tests 28/28 PASS.
- `runtime/result.json`: BSP boot PASS.
- `runtime/nvme-test.log`: `verify-only` PASS, 4KiB/8,704B/4MiB SHA-256 일치.
- Read I/O 34, 8,217 sectors, write I/O 0, MSI-X 41→75(+34).
- `image-unchanged.log`: 기존 SSD 전체 hash 불변. 이미지 쓰기 없이 검증했다.
- `model-artifacts.sha256`: 검증한 NVMe module/libqemu/Lua hash.
- Map/boundary audit, shellcheck 및 diff-check PASS. 전체 플랫폼 coverage audit는
  이전과 동일하게 `ap_9_1_1_memory_map=not_available`, `gate:G1=not_run`이다.

재현 시 위 실행 명령을 사용하되 출력 디렉터리를 `build/nvme-gen5/runtime` 같은
새 경로로 지정하고 `test_apollo_nvme.sh verify-only`를 실행한다.
검증 종료 후 이 실행의 QBox 프로세스만 종료했다. 상세 로그는 `bsp-build.log`,
`provider-check.log`, `host-tests.log` 및 `runtime/`에 보존했다.

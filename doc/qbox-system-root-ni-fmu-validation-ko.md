# System FMU·Root FMU·NI-710AE FMU 조사와 추가 구현

2026-10-24. 대상은 `MACHINE=apollo-qvp`, `DISTRO=auto-ad-nexios`,
`TMPDIR=build/tmp_baremetal`의 QBox/SystemC 모델과 QVP SCP 소비자다.
기존 GIC/MHU AE 변경을 보존한 후속 작업이며, 증거는
[`fmu-hierarchy-20261024`](../build/qbox-apollo-qvp/fmu-hierarchy-20261024/)에 보관한다.

## 근거와 소유 경계

- System FMU: [Zena CSS Software Developer Guide 110125_0001_01](https://developer.arm.com/documentation/110125/0001),
  [로컬 9.5.1절](arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md#programmer-s-model-for-zena-css-register-descriptions-for-safety-island-fault-management-unit-register-summary).
  Tables 9-879–9-886의 register/KEY/오류 종류와 9.1의 주소 배치를 사용한다.
- Root: [Arm Zena CSS FMU 설계](https://arm-zena-css.docs.arm.com/en/latest/design/fmu.html)와
  [읽기 전용 로컬 원본](../arm-zena-css/documentation/design/fmu.rst).
  **Root FMU는 별도 종류의 IP가 아니라 System FMU0**다.
- NI: [NI-710AE TRM 102756_0001_04, Issue 04](https://documentation-service.arm.com/static/65eb9b4fa97073311e21862a).
  다운로드 원본·텍스트·SHA-256은 증거 디렉터리의 `trm/`에 있다.
- 현재 소스와 실제 Lua 구성으로 연결을 확인했다. codebase index는
  2026-09-30 세대로 System FMU 변경과 분리된 Lua 파일을 완전히 반영하지 않아
  이번 변경 판단에 직접 소스 검사를 사용했다.

System/Root는 [zena_fmu.h](../hsoc-stack/tools/qbox-platform/systemc-components/zena_fmu/include/zena_fmu.h),
NI는 [zena_ni710ae_fmu.h](../hsoc-stack/tools/qbox-platform/systemc-components/zena_ni710ae_fmu/include/zena_ni710ae_fmu.h)가
소유한다. 펌웨어는 [QVP FMU 모듈](../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/fmu/)에 있다.
독립 common/FVP FMU 구현에 QVP 정책을 일괄 적용하지 않는다.

## 조사 결과와 수정 범위

| ID | 발견 사항 | 필요한 동작 |
| --- | --- | --- |
| SYS01 | ERRFR가 모두 0이고 IRQ enable 조합이 실제 source 종류와 불일치 | critical/uncorrected/corrected 입력 분류에 맞는 FR, CTLR RES0 및 FI·UE/CFI 조건 |
| SYS02 | IE[13:9]를 같은 오류로 처리하고 DE를 무시 | 외부 입력/입력 parity와 internal383의 APB parity/sequence/access 원인을 분리 |
| SYS03 | Root의 ED가 꺼져도 child 상태를 latch | child→root detection enable, level 유지와 ACK 재assert |
| SYS04 | hardware 입력의 counter/threshold 처리 누락 | CNT 포화, threshold 경계의 critical upgrade 및 상태 보존 |
| SYS05 | SYS_KEY·정렬·접근 폭·strobe·security 검사 부족 | 실패한 보호 write도 KEY 소비, 잘못된 KEY의 INC_SEQ, APB access 오류 |
| NI01 | KEY가 무시되고 transport 검사가 부족 | TRM의 one-shot KEY, Secure 접근, 정렬·폭·strobe 검사 |
| NI02 | 새 오류가 이전 STATUS를 덮어씀 | CI/UE/CE 집계, syndrome 우선순위·overflow·조건부 W1C |
| NI03 | ERI/FHI/CRI가 구분되지 않고 parent에 MMIO 오류를 재주입 | CTLR0의 독립 출력 enable과 세 level의 assert/deassert 전달 |
| NI04 | SMEN이 모든 node에 공유되고 주입 대상 선택이 불명확 | SMINFO로 선택한 실제 node의 enable·주입·discovery |
| NI05 | reset 및 실제 검출 입력 경로 부재 | cold/functional/record reset 경계와 typed detector 입력 |
| SW01 | System/NI/GIC/MHU 원인과 root IRQ criticality를 같은 값으로 취급 | parent에서 upgrade된 noncritical 원인도 올바르게 탐색 |
| SW02 | 한 NI record의 여러 parent 출력이 별도 fault처럼 남고 ancestor 중복 ACK가 새 오류를 지울 수 있음 | 한 snapshot을 한 번 통지하고 대응 parent latch를 한 번만 ACK |
| SW03 | 먼저 예약된 NC drain이 새 NI 오류의 FHI를 처리하면서 critical ERI 통지까지 제거 | 새 snapshot을 처리할 때 실제 Root critical pending을 우선하고 IRQ 재활성화 상태를 보존 |
| INT01 | SBIST producer가 외부 record에 internal 원인 IE9를 사용 | IE13 사용 및 기존 DE/CNT/THR 보존 |

`system-before-tests.log`는 기존 7개 case PASS와 새 4개 case FAIL을 보존한다.
기능 수정 전에 FR/CTLR, IE/DE, Root ED, 잘못된 strobe/KEY 처리의 결함을
실제로 재현한 기록이다. 뒤의 수정 후 결과와 혼동하지 않는다.

System의 IC는 주입 source를 clear하는 pulse이며 STATUS ACK의 대체가 아니다.
IC만 쓰면 기록된 V/IERR가 남고, STATUS W1C가 별도로 필요하다. W1C 때 실제
입력 level이 유지되면 다시 기록하지만 동일 event의 CNT를 다시 올리지는 않는다.
THR 설명의 `이벤트 전 COUNT >= THRESHOLD`를 기준으로 다음 오류를 승격한다.
같은 표 UE 행의 반대 비교 표현과 모순되므로 선택한 해석과 경계 시험을
`system/implementation-notes.md`에 명시했다.

NI의 한 record는 여러 class flag와 하나의 우선순위 syndrome을 갖는다.
CE 뒤 UE가 오면 더 높은 오류 원인을 보존하고 OF를 세우며, 버린 syndrome을
숨겨진 queue에서 다시 만들어 통지하지 않는다. 한 snapshot의 ACK와 통지를
한 번 처리하고 그 snapshot이 올린 ERI/FHI/CRI의 부모 latch를 정리한다.
부모에서 critical로 승격된 NI 오류는 leaf의 CI가 0일 수 있다.
System/NI STATUS에는 origin을 구별하는 INJ bit가 없으므로 firmware의
`fault.injected=false`를 hardware-origin 증거로 사용하지 않는다.
System driver의 `sm_idx`는 IERR bitmap이고 NI driver의 `sm_idx`는 mechanism
번호다. 진단은 각 driver의 표현을 기준으로 원인을 확인한다.

KEY는 암호화 키가 아니라 보호 register의 쓰기 허용 상태다.
System과 NI의 계약은 동일하지 않다. System은 Secure 32-bit 값 전체가
`0x000000be`여야 하며 실패한 보호 write도 one-shot 권한을 소비한다.
NI는 Secure 32-bit KEY의 하위 byte `0xbe`로 다음 write를 허용하며,
같은 64-bit register의 반대쪽 half를 연속해서 쓰는 경우 두 half에 한 번의
KEY를 사용할 수 있다. NI의 Non-secure 접근은 기존 unlock 상태를 바꾸지 않는다.
두 모델 모두 정렬·폭·strobe를 검사하고 반복된 full byte-enable을 허용한다.

## 활성 계층과 입력 정책

한 `si_cl0_fmu` instance가 64 KB bank 다섯 개를 제공한다. bank0은 Root,
bank1/2는 CSS 외부 입력, bank3은 SI cluster, bank4는 나머지 SI 입력이다.
Root의 critical/noncritical 출력은 SI0 GIC INTID128/129와 SSU로 연결된다.
Root의 child summary record는 각각 `(0,1)`, `(2,3)`, `(4,5)`, `(6,7)`이다.

명시적인 `critical_records`로 확인된 critical 입력 위치를 구성한다.
모든 384개 입력의 물리 pin·CORRECTED 설정을 확인했다는 의미는 아니다.
기존 NCI APU permission-denied→Root record0의 기능 시험 경로는 유지한다.
정책상 접근 거부를 NI parity/ECC 검출로 바꾸지 않는다.

| NI instance | FMU self-record | System bank | ERI / FHI / CRI record |
| --- | --- | --- | --- |
| AP cluster0 | 11 | 1 | 1 / 2 / 3 |
| AP cluster1 | 11 | 1 | 16 / 17 / 18 |
| AP cluster2 | 11 | 1 | 31 / 32 / 33 |
| AP cluster3 | 11 | 1 | 46 / 47 / 48 |
| System control | 20 | 1 | 66 / 67 / 68 |
| SMD | 23 | 1 | 165 / 166 / 167 |

ERI/CRI 번호는 기존 Apollo/RD-Aspen firmware configuration에 근거한다.
가운데 FHI 번호는 이번 **QVP의 명시적 연결 계약**이며, 공개 자료만으로
실제 CSSFAULT pin 배치를 확정하지 못했다. 모델과 firmware가 같은 계약을
사용하는지 실행으로 확인하고, 물리 연결 확정과 구별한다.

NI는 `si_cl0_fmu.device_fault_socket`으로 실제 level 변화를 보낸다.
Root 전체 reset은 leaf 여섯 개를 먼저 reset한 뒤 System FMU를 reset한다.
NI의 별도 functional/record reset은 부품 수준의 인터페이스이며, 제품의
독립 clock/reset controller에 모두 배선했다는 뜻은 아니다.

기본 `critical_vector=0`을 사용한다. 공개 근거가 없는 synthesis 값을
시험 기대치에 맞추어 만들지 않는다. NI SM criticality는 build-time 설정이고,
System FMU의 threshold upgrade는 별도 단계다. 현재 구성에서 실제로 식별한
FMU self-node만 광고하며, 비어 있는 discovery slot에 가상의 node를 생성하지 않는다.

## 실행과 판정

공유 BitBake는 순차로 실행한다. native suite는 실제 provider의
`qbox_platform_unit_tests` 목록에 등록하며, 단순히 미사용 CMake 목록에
디렉터리를 추가한 것만으로 실행됐다고 보지 않는다.

| 검사 | 상태 / 증거 |
| --- | --- |
| 수정 전 System FMU 회귀 | 4개 FAIL 재현, `system-before-tests.log` |
| Lua AP4/AP16 및 Linux 구성 | 29 PASS, `lua-tests-1.log` |
| 주소·IRQ 등 정적 계약 | 95/95 PASS, `full-map-1.json` |
| System/Root 및 GIC/MHU leaf native | `system-leaf-tests-3.log` 2/2 PASS; IC/STATUS 분리 포함 |
| NI 및 GIC source→leaf→parent | `ni-tests-2.log` 2/2 PASS |
| SBIST 및 APU→FMU→SSU 경로 | `system-tests-2.log`의 해당 suite PASS |
| SCP host 최종 | 7 suite / 72 case PASS, `software/guest1-fix-tests-3.log` |
| Provider 회귀·설치 | 74/74 CTest PASS, `provider-do_check-1.log`; `provider-install-1.log` |
| SCP target 빌드·배포 | PASS, 통지 순서 수정 후 `scp-deploy-2.log` |
| 전체 시스템 1차 | `guest-1/ae-result.json`: SSU 1/1 PASS; FMU 개별 16 PASS·2 FAIL·2 미관측 |
| 전체 시스템 최종 | `guest-2/ae-result.json` PASS: AP4·SI1 R82 4개, SSU 1/1, FMU 개별 20/20, AE 3/3, 계층 진단 2/2 |
| 기존 MHU 경로 회귀 | 실제 RAM fault 3/3, 오류 전후 FCE 왕복 총 8회, local RAS CE/UC ACK 및 payload 보존 |
| 동시 Linux SCMI 요청 | 42회, read 오류 0, timeout 등 경고 증분 0 |

설치된 Apollo platform의 소스 파일 124개가 현재 checkout과 일치하며,
모델·runtime library·배포 SI0 firmware·소스·build configuration의 SHA-256은
각 실행의 `implementation-manifest-guest-N.json`에 고정했다. SCP target ELF의 FMU
dispatcher context는 488 bytes이며, 이미지 크기는 `scp-image-size.json`에 있다.
최종 실행 후 runtime artifact 13개, build configuration 3개와 각 nested
repository의 manifest 소스가 실행 전 hash와 일치했다. 새 fatal/exception/
PFDI timeout은 없었고, 해당 실행 token의 남은 process도 없다.
최종 기계 판독 결과는
[`verification-summary.json`](../build/qbox-apollo-qvp/fmu-hierarchy-20261024/verification-summary.json)이다.

`guest-2`에서 확인한 핵심 marker는 다음과 같다. NI의 `0x6e000d01`은
V/UE/OF/MV가 1, CE가 2, IERR가 13이며 CI는 0이다. 이 기록을 System parent가
승격한 결과로 C 통지했고, 남은 CE syndrome을 별도 오류로 재생하지 않았다.

```text
FMU_HIERARCHY_PASS case=0 notifications=4 critical=2 noncritical=2 gsr=0
FMU_HIERARCHY_PENDING case=1 ni_status=0x6e000d01 syndrome=13
FMU_HIERARCHY_PASS case=1 notifications=2 critical=1 noncritical=1 gsr=0
```

재현은 workspace root에서 다음 순서로 실행한다. 마지막 harness의 출력
디렉터리는 기존 실행 기록을 덮어쓰지 않는 새 이름을 지정한다.

```sh
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
./yocto_build.sh scp-firmware -c deploy
python3 build/qbox-apollo-qvp/fmu-hierarchy-20261024/guest-check.py guest-repeat-1
```

`test fmu_hierarchy`는 두 case로 구성한다. 첫 case는 Root 직접 오류 두 개와
System1/2 오류를 동시에 만들고 Root에서 승격된 System1 NC leaf를 포함해
4개 identity를 한 번씩 통지해야 한다. 둘째는 NI0의 CE14+UE13와 NI1의 CE14를
동시에 만든다. NI0은 CI=0이어도 System ERI threshold로 C 통지되어야 하며,
같은 snapshot의 ERI/FHI를 중복 통지하지 않아야 한다. 두 case 모두 최종
GSR=0, IRQ unmasked, `last_error=0`을 5 simulated seconds 내에 요구한다.

수정 전 결함 재현 로그 외에도 초기 CMake target 등록 오류
(`ni-sbist-build-1.log`), GIC fixture의 Root critical profile 누락
(`system-tests-2.log`), SCP host target/fixture 오류를 보존했다.
각 오류의 수정 후 결과는 위 표와 `software/notes.md`에 기록한다.

`guest-1`에서 NI1과 system-control NI의 SM2가 기대한 C 대신 NC로 통지됐다.
이전 IRQ에서 예약된 NC drain이 새 NI snapshot의 FHI를 먼저 처리하면서
승격된 ERI까지 ACK하는 순서 문제가 원인이다. 동일 경로의 host FAIL은
`software/guest1-repro-tests.log`에 보존했다. 수정은 새 snapshot 전 Root C를
우선하고, 대기하는 NC IRQ를 C 처리 후 재활성화한다. ACK/queue 실패의
명시적 `recover()` 정책과 진행 중 통지 재시도는 유지한다.

첫 실패 실행의 Unity 요약은 `20 Tests 2 Failures`지만 개별 결과는
16 PASS·2 FAIL이며 CL2/SMB 두 case는 나타나지 않았다. 18 PASS로 산술
추정하지 않는다. 후속 harness는 서로 다른 FMU 20개 개별 PASS까지 요구한다.
수정 후 `guest-2`는 이 20개를 모두 확인했다. 첫 FAIL 실행을 단순 재시도
성공으로 대체하지 않고 실패·host 재현·수정 후 실행을 함께 보존한다.

기존 post-login의 `si_cl1_rsctbl_dd_rc=1`은 `/dev/mem`으로 SI1 resource table을
읽는 별도 경로의 제한으로 남는다. arm_si_rproc/rpmsg/hipc_ethsi1/virtio/
PL011/SMMUv3/DSU PMU/PFDI 8개 driver marker와 systemd failed-unit=0은 확인했지만,
이 결과를 모든 post-login 선택 기능이나 전체 제품 qualification의 PASS로 확대하지 않는다.

## 남은 경계

- 모든 System FMU 입력의 물리 critical/corrected pin 배치와 모든 외부 fault
  producer를 연결한 모델은 아니다. 확인한 경로와 재사용 가능한 입력 계약을 구분한다.
- NI의 실제 ECC/parity/DCLS/CRC 회로, PING 전달 지연과 전체 interconnect node
  topology는 이 functional FMU의 register/오류 주입 성공으로 입증되지 않는다.
- NI의 외부 `secure_access` override는 연결하지 않았으며 현재 FMU는 Secure
  접근 계약을 사용한다. reset의 물리 clock-cycle 요건도 모델링하지 않는다.
- firmware의 C 우선 처리는 초기화된 QVP처럼 Root critical reporting과
  해당 CPU IRQ가 활성인 구성을 전제로 한다. 외부에서 CTLR.CI를 끄고 C
  STATUS만 남긴 경우 gate 복원 또는 C 상태 정리 후 `recover(false)`가 필요하다.
- 세 SI interconnect FMU 주소 `0x32000000`, `0x32010000`, `0x32030000`의
  별도 NI FMU instance와 모든 SoC NI instance는 아직 활성 구성에 없다.
- AP16은 Lua/static 구성 검사 범위다. 실제 부팅·firmware 진단 결과는 실행한
  AP4 구성에 한정하며 ASIL coverage, FVP 또는 실리콘 timing 동등성을 주장하지 않는다.

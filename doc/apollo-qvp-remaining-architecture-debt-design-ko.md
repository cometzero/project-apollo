# Apollo QVP 잔여 아키텍처 부채 설계

- 상태: 아키텍처 리뷰 반영, A4 구현 및 반복 검증 완료
- 기준일: 2026-07-15, 구현 검증 2026-07-16
- 대상: `apollo-qvp`, RD-Aspen CFG2, 4 CPU 기본 구성
- 기준 구현: QBox/SystemC/TLM/QEMU Apollo full-system machine

## 1. 목적과 완료 범위

이 문서는 A3 local-view 분리 이후 남은 **구조적 아키텍처 부채**를 닫기 위한
설계를 정의한다. 이번 변경의 완료 범위는 다음과 같다.

1. AP, SMD, RSE, SI CL0, SI CL1 주소 view를 실제 router 계층으로 분리한다.
2. AP와 SI의 전체 주소 공간을 `system_router`로 전달하던 1:1 broad bridge를
   제거한다.
3. RSE가 구성하는 SI/AP/SMDEXP ATU를 실제 transaction 경로에 둔다.
4. SMD high-nibble 영역을 `smd_router`가 소유하고, system fabric은 NCI decode
   경로로만 SMD에 접근한다.
5. GPEX DMA를 MMU-720AE TBU 경로로 연결하고 TBU port별 StreamID를 보존한다.
6. 공유 메모리와 GIC는 중복 placeholder가 아니라 canonical owner를 향하는
   명시적 bridge로 접근한다.
7. 미매핑, reset-state ATU, 경계 초과 접근은 `DECERR`에 대응하는
   `TLM_ADDRESS_ERROR_RESPONSE`로 종료한다.
8. SMD가 먼저 초기화하는 AP/SI SCMI 공유 SRAM은 AP reset fan-out에서 제외해
   producer/consumer 사이의 mailbox 상태를 보존한다.
9. requester가 SI0 transport 초기화보다 먼저 게시한 유효한 secure mailbox는
   completer 초기화가 덮어쓰지 않으며, SI0가 이를 소비할 때까지 requester가
   상태와 payload를 소유한다.

완전한 MMU-720AE page-table walk, 모든 APU 권한 레지스터, cycle-accurate NCI,
DCLS lockstep, 모든 FMU/RAS side effect는 구조 폐쇄와 구분되는 기능 충실도
부채다. 이들을 임의 register stub으로 채우지 않는다.

## 2. 근거

### 2.1 Arm Zena CSS / RD-Aspen 하드웨어 근거

다음 자료를 구현 전에 대조했다.

- `doc/arm_zena_css_dev_guide/02-block-diagram-for-zena-css.md`
- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `arm-zena-css/documentation/images/aspen_high_level_arch.png`
- `arm-zena-css/documentation/images/aspen_system_management_block.png`
- `arm-zena-css/documentation/images/aspen_compute_complex.png`
- `arm-zena-css/documentation/design/hipc.rst`

블록 다이어그램은 RSE와 Safety Island가 각각 NCI를 통해 system fabric에
접속하고, SMD peripheral/SRAM이 독립 SMD 영역에 있음을 보여 준다. AP I/O
경로에는 TCU/TBU와 ITS가 존재한다. Programmer's model은 system address의
상위 nibble로 AP/SMD/RSE/SI 영역을 분리하고, 미매핑 interconnect 접근은
decode error가 되어야 함을 정의한다.

### 2.2 실행 증거

기존 local QVP RSE 로그
`build/qbox-apollo-qvp/local-20260715-1540/qbox-rse.log`에서 TF-M BL2가
다음 실제 설정을 수행함을 확인했다.

- SI ATU region 0–16: `0x8000_0000`–`0xe033_ffff`
- AP ATU region 0–8: `0x4000_0000`–`0x4074_1fff`
- SMDEXP2SMD ATU region 0: `0xe034_0000`–`0xe034_1fff`

따라서 firmware probe를 통과시키기 위한 local `gs_memory` 창 대신 이미 있는
`rse_atu` 모델을 실제 경로에 연결할 수 있다.

## 3. AS-IS 구조 부채

| ID | 현재 상태 | 위험 |
|---|---|---|
| D-01 | AP 52-bit 전역 1:1 bridge | AP가 ATU를 우회해 system target에 접근 가능 |
| D-02 | SI CL0/CL1 40-bit 전역 1:1 bridge | reset default-deny와 domain isolation이 성립하지 않음 |
| D-03 | `smd_router`가 contract-only | SMD owner와 decode boundary가 runtime에 없음 |
| D-04 | SI/SMDEXP ATU register만 존재 | firmware가 ATU를 설정해도 transaction 결과가 바뀌지 않음 |
| D-05 | SI ATW별 local placeholder | 동일 hardware state가 AP/SI/system view마다 중복됨 |
| D-06 | GPEX DMA가 AP router 직결 | TBU/StreamID 및 SMMU fault attribution을 우회함 |
| D-07 | CL1 HIPC를 ATU default-deny로 기술 | 실제 정적 512 KiB shared-memory wiring과 불일치 |
| D-08 | reset deny 음성 시험 부족 | 정상 boot만으로 policy 우회를 탐지할 수 없음 |
| D-09 | secure transport 일부만 pending mailbox를 보존 | SI CL1 PFDI가 SI0 init보다 먼저 요청하면 doorbell만 남고 payload가 삭제됨 |

## 4. 목표 topology

```text
                             +-------------------------+
 AP CPU/loader ------------->| ap_router               |
                             | AP local target         |
 GPEX DMA -> MMU TBU LTI00 ->| SMMU downstream        |
                             +-----+-----------+-------+
                                   |           |
                         AP ATU only|           | explicit FMU alias
                                   v           v
                            +-------------------------+
 RSE ATU ------------------>| system_router           |
 SI ATU ------------------->| 52-bit top-level decode |
                            +---+----------+----------+
                                |          |
                 0x2 prefix NCI |          | explicit AP shared/GIC window
                                v          v
                         +------------+  +-----------+
                         | smd_router |  | ap_router |
                         | SMD owner  |  | canonical |
                         +------------+  +-----------+

 SI CL0 CPU -> si_cl0_router -> SI ATU / SMDEXP2SMD ATU -> system_router
 SI CL1 CPU -> si_cl1_router -> static SCMI/HIPC paths only
 RSE CPU    -> rse_router    -> RSE ATU -> system_router
```

router에 target이 없는 접근은 다음 router로 자동 전달하지 않는다. 오직 표에
선언된 bridge나 ATU target socket만 다음 domain으로 진행한다.

## 5. 설계 결정

### AD-01. SMD runtime 계층

`fabric.create()`에서 `smd_router`를 생성한다. `system_router`에는
`0x2_0000_0000_0000/4`만 받는 `system_to_smd_nci` decode bridge를 둔다.
bridge는 주소를 변경하지 않고 `smd_router`로 전달한다. SMD 내부에서 다시
미매핑된 주소는 decode error가 된다. 이는 전체 system 범위를 전달하는 broad
bridge가 아니라 architecture에 정의된 상위 nibble domain decode다.

다음 canonical target은 `smd_router`가 소유한다.

- AP ATU와 SMDEXP2SMD ATU register bank
- CSS counter control/read/sync frames
- SYSTOP PIK와 SYS0 PPU
- SMCF SMD/SMDEXP SRAM 및 MGI
- SMD expansion PLL와 system ID
- AP cluster NI-710AE FMU/system-control/SMD windows

### AD-02. AP cross-domain 경로

`ap_system_bridge`를 삭제한다. AP local target은 `ap_router`에 유지한다.
AP→SMD 접근은 `host_ap_atu.translation_socket`만 수신하며, ATU가 활성화한
region만 system address로 변환한다. ATU reset 상태와 region 밖 접근은
address error다.

AP local FMU alias는 각각 canonical SMD FMU target으로 향하는 좁은 고정
bridge다. 이 경로는 hardware local decode의 명시적 alias이며 전체 system
접근 권한을 만들지 않는다.

### AD-03. SI CL0 ATU 경로

`si_cl0_system_bridge`와 `si_cl0_atu_check_*` placeholder를 삭제한다.
`host_si_atu.translation_socket`은 `0x8000_0000`–`0xe033_ffff`를 받고,
initiator는 `system_router`로 연결한다. 각 target은 firmware가 기록한 physical
address에 한 번만 배치한다.

`host_smdexp2smd_atu.translation_socket`은 `0xe034_0000`–`0xe034_1fff`를
받아 SMD SRAM expansion으로 변환한다. main SI ATU와 decode 범위가 겹치지
않는다.

### AD-04. SI CL1과 HIPC

`si_cl1_system_bridge`를 삭제한다. CL1은 local peripheral/SRAM, CL0와의 SCMI
shared memory, AP와의 HIPC shared memory만 사용한다. `hipc.rst`의 512 KiB
고정 shared-memory 정의에 따라 CL0/CL1 HIPC bridge는 reset부터 정적 허용한다.
이를 RSE가 ATU를 설정하기 전까지 닫힌 경로로 기술하지 않는다.

CL0가 사용하는 `0xe013_0000` ATW 전체는 SI ATU region 14를 거쳐 AP canonical
SRAM으로 간다. CL1의 동일 logical address는 별도 정적 HIPC bridge다.

### AD-05. canonical owner

| 자원 | canonical owner/router | 다른 view |
|---|---|---|
| AP shared SRAM | `ap_router` | system→AP 명시 창, SI ATU region 13 |
| AP HIPC SRAM | `ap_router` | SI ATU region 14, CL1 고정 HIPC bridge |
| AP GIC | `ap_router` | system→AP GIC 창, SI ATU region 12 |
| CSS timer | `smd_router` | AP/SI ATU 변환 |
| SMCF SRAM | `smd_router` | AP/SI/SMDEXP ATU 변환 |
| AP NI-710AE FMU | `smd_router` | AP fixed alias, SI ATU regions 6–9 |

중복 `gs_memory`는 제거한다. 아직 기능 모델이 없는 NI system-control window는
주소 응답만 제공하는 제한 모델로 남기되, 실제 ATU 뒤의 physical target에 한
번만 존재하고 잔여 기능 부채로 표시한다.

### AD-06. GPEX/SMMU/QEMU 경계

SystemC MMU backend에서는 GPEX `bus_master`를
`ap_smmu_0.tbu_lti00_socket`에 연결한다. LTI00 port의 CCI 기본 SID를 GPEX
requester identity로 사용한다. MMU downstream과 page-table walk socket은
`ap_router`로 연결한다. payload에 명시적
`request_attrs_extension.sid_valid`가 있으면 기존 MMU 규칙대로 그것이 port
기본값보다 우선한다.

QEMU `arm-smmuv3` backend는 GPEX와 같은 QEMU instance 안에서 requester를
연결하는 기존 QEMU-owned 경계를 유지한다. 두 backend를 동시에 직렬 연결하지
않는다.

### AD-07. 오류와 debug/DMI 의미

- normal transport와 debug transport는 동일 ATU region/permission 판정을 한다.
- 정책/translation 경로는 DMI를 기본 비활성화한다.
- DMI를 허용하는 ATU 구성에서는 grant를 logical window로 clip하고 주소를
  역변환한다.
- 미매핑, disabled region, transaction이 region 끝을 넘는 경우 address error다.
- SMMU disabled 상태는 architected bypass이고, enabled 상태에서 아직 지원하지
  않는 translation은 SID가 기록된 fault로 종료한다.

### AD-08. APU 모델 경계

`rse_protection_ctrl`은 RSE register bank의 lock, read-only field,
non-secure-write deny를 모델링하지만 pass-through APU는 아니다. 이번 변경은
ATU allow-list와 explicit bridge 목록을 실제 최소 권한 경계로 사용한다.
문서에 없는 새 APU register model을 추측해 추가하지 않는다. 공식 register
contract가 확보되면 transaction attribute를 소비하는 별도 APU stage로
확장한다.

### AD-09. reset-held CPU의 simulated-time 격리

구현 후 반복 부팅에서 reset-held AP CPU의 timehandler가 SystemC global suspend
owner가 되고 전체 simulated time이 정지하는 결함이 확인됐다. reset이 assert된
CPU는 실행 가능한 guest time budget이 없으므로 다음 lifecycle contract를
적용한다.

- reset-held CPU는 quantum keeper를 시작하거나 suspending channel owner가 되지
  않는다.
- reset release는 target vCPU의 tracked async job에서 QEMU power/soft-stop,
  architectural reset과 deadline 상태를 정리한 뒤 완료한다.
- SystemC reset caller는 release completion을 확인한 뒤 CPU를 runnable로 본다.
- simulation start 전 도착한 reset signal도 잃지 않고 initial reset state에
  반영한다.
- QEMU GPIO state 변경은 BQL 아래 수행하며 IRQ/FIQ/VIRQ/VFIQ는 Cortex-R82의
  external wake event에 포함한다.

이 결정은 global quantum이나 MTTCG 동기화 의미를 완화하지 않는다. 실행할 수
없는 reset-held participant만 시간 동기화 집합에서 제외하고 release 뒤 원래
정책으로 복귀시킨다.

### AD-10. SMD 소유 SCMI 공유 SRAM의 reset 경계

AP non-secure MHU shared SRAM `host_ap_mhu_ns_shared_sram`은 AP 주소 view에
배치되지만 lifecycle owner는 SMD다. SI CL0의 SCP-firmware가 AP reset release
전에 SI ATU region 14를 통해 `0xe01b_0000 -> 0x0018_0000`으로 접근해 SCMI
channel의 free 상태를 초기화한다. 따라서 AP reset은 AP BL2 loader, header SRAM,
reset GPIO만 초기화하며 이 mailbox backing을 지우지 않는다.

- address/software contract에 `owner=smd`,
  `reset_policy=preserve_on_ap_reset`을 함께 기록한다.
- AP reset fan-out에는 `host_ap_mhu_ns_shared_sram.reset`을 bind하지 않는다.
- 보존 정책은 모든 공유 RAM에 적용하는 일반 규칙이 아니다. reset을 발생시키는
  domain과 초기화 owner가 다르고, producer가 reset 전에 유효 상태를 게시하는
  이 channel에만 적용한다.
- SI ATU translation 성공과 Linux SCMI protocol probe를 함께 확인해 주소 routing
  결함과 reset-order 결함을 분리한다.

이 정책이 없으면 SI0가 기록한 free bit가 AP reset에서 0으로 지워져 Linux의
`shmem_tx_prepare()` warning과 secondary SCMI timeout으로 나타난다. 보존 후에는
FVP와 같은 SCMI v2.0 firmware probe가 성립해야 한다.

### AD-11. 모델 CPU 수와 guest bootargs 일치

full-system runner가 선택한 AP CPU 수는 Lua topology, result provenance와 guest
`maxcpus=`에 동일하게 반영한다. local rootfs를 patch하는 경우 기존
`maxcpus=`를 제거한 뒤 resolved CPU 수를 정확히 한 번 추가한다. active 기본은
4이며 `QBOX_APOLLO_NUM_CPUS` override도 같은 값으로 전파한다. Yocto WIC의
`rootfs-bootargs-profile=none`처럼 boot entry를 수정하지 않는 경로는 image의
bootargs를 보존한다. 16-core direct-boot 실험 기본값과 full-system 4-core
기준선을 혼동하지 않는다.

### AD-12. secure mailbox의 startup 소유권

PFDI/SCMI requester가 shared mailbox의 유효한 BUSY 상태와 payload를 게시한 뒤
doorbell을 보냈다면, completer transport가 아직 초기화되지 않았더라도 해당
message의 소유권은 SI0가 소비하거나 명시적으로 오류 응답을 게시할 때까지
requester에 있다. SI0 transport 초기화는 이를 빈 mailbox로 재초기화해서는 안
된다.

- `TRANSPORT_CH_SEC_MBX_INIT`를 사용하는 AP PFDI, SI CL1 PFDI, RSE SCMI,
  PSCI와 secure completer channel은 모두
  `MOD_TRANSPORT_POLICY_PRESERVE_PENDING_MAILBOX`를 적용한다.
- status가 유효한 pending request가 아니면 기존처럼 mailbox를 초기화한다.
- doorbell pending 여부만 보존하는 것으로는 충분하지 않다. status, flags,
  length와 payload가 같은 shared backing에서 함께 보존돼야 한다.
- verbose `live-trace`나 global quantum 변경은 실행 순서를 바꿔 결함을 숨길 수
  있으므로 해결책으로 사용하지 않는다. 기본 trace-off scheduling에서 반복
  검증한다.

이 불변식이 없으면 CL1의 첫 PFDI `PROTOCOL_VERSION` 요청이 SI0 transport init
전에 도착한 경우 init이 BUSY/request를 FREE로 덮어쓴다. MHU doorbell은 남지만
payload가 없어 CL1은 timeout한다. 공통 secure init policy로 보존 범위를
정렬하면 초기화 순서와 무관하게 첫 요청을 정상 소비할 수 있다.

## 6. reset 및 boot 순서

1. 모든 `rse_atu` region은 reset 시 disabled다.
2. RSE BL2가 SI/AP/SMDEXP ATU region을 기록하고 read-back한다.
3. SI CL0 release 후 ATU 경유 CMN, cluster PPU, SMD timer/FMU/GIC 접근이
   성공한다.
4. SI CL1 또는 AP requester가 SI0 transport init보다 먼저 유효한 secure request를
   게시해도 SI0 init은 그 mailbox를 보존한다.
5. SI CL0가 AP/SI SCMI shared SRAM을 초기화한 뒤 AP reset을 release한다.
6. AP reset은 SMD-owned SCMI mailbox 상태를 보존한다.
7. AP Linux가 보존된 channel로 SCMI v2.0 server를 probe한다.
8. AP GPEX DMA는 SMMU TBU port를 통과한다.

ATU가 구성되기 전 동일 logical 주소를 읽으면 local placeholder가 대신 응답해서는
안 된다.

## 7. 검증 가능한 수용 조건

- contract phase가 `A4_policy_routing`이고 broad compatibility debt가 비어 있다.
- 세 broad bridge 이름이 Lua source와 생성 topology에 없다.
- `smd_router`와 `system_to_smd_nci`가 runtime CCI graph에 존재한다.
- SI/AP/SMDEXP ATU reset-state normal/debug/DMI 음성 시험이 통과한다.
- GPEX SystemC backend 경로가 `tbu_lti00_socket`을 경유한다.
- topology/map validator와 component test가 통과한다.
- `./local_build.sh qbox`가 성공한다.
- local-build image로 full-system QBox boot와 coverage audit가 성공한다.
- `./yocto_build.sh`가 생성한 `nexios-image`로 같은 QBox boot marker를 확인한다.
- start-in-reset release test를 50회 반복하고 local full-system 5회, Yocto
  full-system 3회에서 simulated-time 정지 없이 login과 coverage audit를
  확인한다.
- local rootfs의 `maxcpus`가 resolved AP CPU 수와 일치하고 Linux가 정확히 그
  수의 CPU만 online한다.
- SI ATU region 14 translation과 AP reset 뒤 mailbox 상태가 보존되며 Linux
  log에 FVP와 동일한 SCMI v2.0 server marker가 있고 `shmem_tx_prepare` warning과
  해당 response timeout이 없다.
- SI CL1 PFDI 요청이 SI0 transport init보다 먼저 도착해도 첫
  `PROTOCOL_VERSION` 응답과 `PFDI service ready (4 CPUs)`가 trace 없이
  반복 관찰된다. transport 전체 unit suite와 local/Yocto image를 각각 3회 이상
  실행해 간헐 timeout이 없어야 한다.
- 동일 artifact의 FVP 비교가 가능하지 않으면 성공으로 대체하지 않고 명시적
  blocker로 기록한다.

## 8. 구조 폐쇄 후 남는 기능 충실도 부채

| 부채 | 구조 폐쇄와 분리하는 이유 | 후속 완료 증거 |
|---|---|---|
| MMU-720AE table walk | 현재 enabled translation은 fault 모델 | 실제 IOVA map/unmap 및 EVTQ/IRQ |
| 완전한 APU 권한표 | 공식 programming model과 attribute 매핑 필요 | secure/domain별 allow/deny matrix |
| PCIe MSI→ITS→LPI | DMA address routing과 다른 signal path | guest MSI와 LPI affinity |
| DCLS/RAS/FMUs | timing/fault side effect 모델 | fault injection과 safety reaction |
| NCI/CMN 성능 | functional decode와 cycle model은 별도 | latency/bandwidth/ordering suite |
| 16 CPU 성능 | 기본 4 CPU 기능 폐쇄와 별도 | 4/16 CPU wall-time/RSS 기준 |

## 9. 구현 결과

2026-07-16 최종 source와 생성 contract는 다음 설계 조건을 만족한다.

- migration phase: `A4_policy_routing`
- `forbid_broad_passthrough=true`
- compatibility debt: 빈 목록
- `smd_router`, `system_to_smd_nci`, SI/AP/SMDEXP ATU data path: runtime 구성
- GPEX SystemC backend: MMU-720AE LTI00 TBU 경유
- reset-state ATU normal/debug/DMI: default-deny unit test 통과
- QBox platform component test: 33/33 통과
- reset release 회귀: 50/50 통과
- local image full boot/coverage: 5/5 통과
- Yocto `nexios-image` full boot/coverage: 3/3 통과
- post-review local acceptance: CPU 수/`maxcpus` 정합 1회와 SMD-owned SCMI
  reset 보존 1회 모두 full boot 및 49/49 coverage 통과
- secure pending-mailbox 최종 acceptance: SCP module unit 77/77, trace-off local
  3/3 및 새 Yocto image 3/3 full boot, 각 49/49 coverage 통과
- SCMI focused differential: QVP와 기존 FVP log 모두
  `SCMI Protocol v2.0 'arm:arm' Firmware version 0x2100000` 관찰

상세 command와 artifact는
[2026-07-16 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)에
기록한다. 8장의 항목은 구조 폐쇄 뒤에도 의도적으로 열린 기능 충실도 부채다.

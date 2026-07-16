# Apollo QVP 잔여 아키텍처 리뷰

- 리뷰 일자: 2026-07-15
- 대상 설계: `apollo-qvp-remaining-architecture-debt-design-ko.md`
- 결과: 조건부 승인 후 수정 반영, 2026-07-16 구현 후 재리뷰 승인

## 1. 리뷰 방식

Arm Zena CSS/RD-Aspen block diagram, programmer's model, firmware boot log와
현재 QBox Lua/SystemC/QEMU wiring을 대조했다. 리뷰 관점은 다음 네 가지다.

- QBox/SystemC: socket cardinality, router ownership, TLM error/DMI 의미
- system hardware: NCI 계층, address view, ATU 소유권, HIPC 실제 연결
- system software: TF-M/SCP/TF-A/Zephyr/Linux가 관찰하는 boot·ABI
- QEMU: QEMU instance 경계, GPEX/SMMU, CPU/GIC와 TLM 연결

## 2. 관점별 판정

### 2.1 QBox/SystemC 관점

**판정: 수정 후 승인.**

- `smd_router`를 실제 생성하고 상위 nibble decode를 별도 router에서 끝내는
  구조는 QBox router convention과 맞는다.
- 전체 범위 1:1 bridge는 local target 충돌을 가릴 뿐 아니라 socket graph만
  보고 policy를 검증할 수 없으므로 제거해야 한다.
- 기존 `rse_atu`는 normal/debug/DMI, region 경계, output security-domain과
  invalidation을 이미 다루므로 새 ATU stub보다 재사용이 옳다.
- `rse_protection_ctrl`을 APU pass-through 모델로 간주하면 안 된다. register
  model과 transaction filter를 문서에서 분리하도록 수정했다.
- 한 router target socket은 한 번만 bind하고, cross-view 접근은 `addrtr` 또는
  ATU initiator를 사용하도록 결정했다.

### 2.2 system hardware 관점

**판정: 수정 후 승인.**

- `aspen_system_management_block.png`의 RSE/SI/SMD NCI 구조는
  `system_router` 하나에 모든 target을 놓는 구조를 지지하지 않는다.
- system address 상위 nibble `0010`은 SMD이므로 `0x2` prefix decode는 broad
  compatibility bridge와 성격이 다르다. SMD 내부 미매핑 접근은 반드시
  `smd_router`에서 DECERR가 되어야 한다.
- SI ATW가 firmware에서 실제 programming되므로 logical placeholder를 제거하고
  physical target에 연결해야 한다.
- 초안의 CL1 HIPC `deny_until_rse_programmed` 가정은 `hipc.rst`의 정적 512 KiB
  shared-memory 구성과 맞지 않았다. CL1 HIPC를 `static_allow_list`로 수정했다.
- SI CL0의 `0xe013_0000`은 CL1 정적 경로와 달리 SI ATU region 14를 통과한다.

### 2.3 system software 관점

**판정: 승인.**

- TF-M BL2가 출력한 SI/AP/SMDEXP ATU region과 설계의 logical/physical 창이
  일치한다.
- reset 시 placeholder가 응답하지 않으므로 firmware의 ATU programming과
  read-back이 실제 boot 선행 조건이 된다.
- SCP가 접근하는 CMN, PPU, counter, FMU, AP GIC 주소는 firmware가 기록한
  translation을 따라 canonical target으로 도달한다.
- TF-A/U-Boot/Linux가 사용하는 AP shared SRAM과 CL1 HIPC backing은 하나로
  유지되어 resource table, vring, SDS가 view마다 갈라지지 않는다.
- Linux ABI 완료는 정상 boot marker뿐 아니라 SMMU fault, HIPC/RPMsg, SCMI의
  오류 경로로 별도 검증해야 한다.

### 2.4 QEMU 관점

**판정: 수정 후 승인.**

- QEMU `qemu_gpex` DMA를 SystemC MMU TBU에 연결하는 것은 같은 QEMU instance의
  CPU MMIO path와 DMA path를 구분하는 올바른 경계다.
- 별도 requester wrapper를 새로 만드는 초안은 단일 GPEX requester에 과도하다.
  기존 MMU-720AE가 TBU port별 기본 SID와 explicit extension 우선 규칙을 이미
  구현하므로 LTI00 port identity를 사용하도록 단순화했다.
- QEMU `arm-smmuv3` backend는 GPEX를 constructor argument로 소유하므로
  SystemC MMU와 직렬 연결하면 이중 translation 위험이 있다. backend별 wiring을
  분기한다.
- AP GIC canonical QEMU device로 향하는 좁은 system→AP 창을 사용하면 SI용
  독립 register shadow보다 interrupt-controller state가 일관된다.

## 3. 주요 리뷰 지적과 반영

| ID | 심각도 | 지적 | 반영 |
|---|---|---|---|
| R-01 | P0 | broad bridge가 default-deny를 무효화 | 세 bridge 완전 제거 |
| R-02 | P0 | ATU register와 data path 분리 | SI/AP/SMDEXP translation socket 실경로 연결 |
| R-03 | P0 | SMD router contract/runtime 불일치 | `smd_router`와 prefix NCI 생성 |
| R-04 | P1 | CL1 HIPC reset policy 근거 오류 | 정적 allow-list로 수정 |
| R-05 | P1 | `rse_protection_ctrl`을 APU로 과대 해석 | register model로 범위 제한 |
| R-06 | P1 | 새 SID wrapper가 불필요하게 복잡 | 기존 TBU LTI00 기본 SID 사용 |
| R-07 | P1 | AP/SI view마다 GIC/SRAM shadow | canonical owner와 좁은 bridge 사용 |
| R-08 | P1 | full MMU/APU까지 완료로 오해 가능 | 기능 충실도 부채 표로 분리 |
| R-09 | P0 | reset-held CPU가 SystemC suspend owner가 됨 | reset 동안 QK 제외, target-vCPU release completion 적용 |
| R-10 | P1 | local bootargs가 4-CPU topology에서 `maxcpus=16`을 제거만 함 | resolved CPU 수를 rootfs patch에 전달하고 4/8 override test 추가 |
| R-11 | P0 | AP reset이 SMD가 초기화한 SCMI shared SRAM을 지움 | SMD ownership과 `preserve_on_ap_reset` 계약, AP reset fan-out 제외 |
| R-12 | P0 | SI CL1 PFDI 요청이 SI0 transport init보다 먼저 도착하면 공통 secure init이 BUSY/payload를 지움 | 모든 secure completer channel에 pending-mailbox 보존 정책 적용 |

## 4. 구현 전 위험 검토

| 위험 | 탐지 | 완화 |
|---|---|---|
| ATU physical address 오기 | RSE firmware trace와 static table 비교 | region별 source/target assertion |
| Lua socket 미바인딩/중복 바인딩 | `platforms-vp` 구성 및 CCI elaboration | target별 cardinality 검사 |
| boot 초기에 필요한 고정 경로 제거 | 최초 실패 domain UART log | RSE→SI→AP 순서로 log triage |
| GPEX가 SMMU enabled 후 모두 fault | MMU EVTQ/IRQ 및 guest log | disabled architected bypass 보존, table walk는 잔여 부채 |
| HIPC backing 분리 | resource table/rpmsg marker | AP/CL1/CL0가 같은 target을 사용 |
| AP reset이 선행 SCMI 상태 삭제 | Linux `shmem_tx_prepare` warning/timeout | SMD-owned mailbox를 AP reset에서 보존하고 FVP marker 비교 |
| trace에 따라 첫 PFDI 요청 성공 여부가 달라짐 | CL1 `PROTOCOL_VERSION` timeout과 SI0 transport init 순서 | trace/quantum을 원인에서 배제하고 유효한 pending request를 공통 secure init에서 보존 |
| QEMU SMMU 이중 연결 | backend별 topology assertion | SystemC/QEMU wiring 상호 배타화 |

## 5. 리뷰 결론

구조 폐쇄의 최소 단위는 **router 계층 + 실제 ATU data path + canonical owner +
GPEX TBU route + 음성 시험**이다. 완전한 APU나 MMU 기능을 근거 없이 추가하는
것은 승인하지 않는다. 위 수정이 설계 문서에 반영되었으므로 구현을 진행한다.

## 6. 2026-07-16 구현 후 재리뷰

### 6.1 QBox/SystemC

**판정: A4 구조 승인.**

- 생성 contract와 runtime source에서 broad bridge 세 개가 사라졌고
  `compatibility_debt`가 비어 있다.
- `smd_router`, high-nibble NCI decode, SI/AP/SMDEXP ATU translation socket과
  GPEX LTI00 TBU path가 실제 graph에 존재한다.
- GIC frame tail, host timer frame, PPU reset sequence, MHU combined IRQ와
  ATU reset default-deny를 component test로 고정했다.
- 반복 부팅에서 드러난 reset-held CPU quantum keeper 교착은 generic quantum
  정책을 바꾸지 않고 reset lifecycle 경계에서 수정했다. 대상 test 50회와
  local/Yocto full boot 8회가 통과했다.

### 6.2 system hardware

**판정: 주소·제어 구조 승인, safety 기능 부채 유지.**

- AP/SMD/RSE/SI view와 canonical backing은 Arm Zena CSS block diagram의 NCI
  계층 및 firmware ATU programming 순서와 일치한다.
- AP/SI MHU endpoint 방향과 absolute INTID→QBox SPI index를 분리했고 GIC
  multi-view control frame과 functional view를 contract에 구분했다.
- SI ATU region 14가 `0xe01b_0000`을 canonical AP MHU SRAM `0x0018_0000`으로
  정상 변환함을 trace로 확인했다. 이 SRAM의 lifecycle owner는 AP가 아니라
  SI0 초기화를 조정하는 SMD이므로 AP reset fan-out에서 제외한 것이 타당하다.
- 완전한 NI-710AE APU register/permission, MMU walk, DCLS, FMU/SSU/RAS timing은
  이번 구조 승인 범위가 아니다.

### 6.3 system software

**판정: 정상 boot 계약 승인, error ABI 조건부.**

- SCP transport consumer/MHU 초기화 순서와 pending mailbox 보존, TF-M BL2의
  bounded SCMI polling을 반영했다.
- RSE, live SI0/SI1, TF-A, OP-TEE, U-Boot와 Linux login marker가 local 5회,
  Yocto 3회에서 반복 관찰됐다.
- 구현 후 품질 리뷰에서 local rootfs의 `maxcpus`를 resolved 4 CPU와 정렬했고,
  Linux는 CPU 4–15 PSCI 실패 없이 정확히 4 CPU를 online했다.
- AP reset 뒤 SI0가 게시한 mailbox free 상태가 유지되어 QVP Linux에서도 기존
  FVP log와 같은 `SCMI Protocol v2.0 'arm:arm'` marker가 관찰됐다. 수정 전의
  `shmem_tx_prepare` warning과 해당 SCMI response timeout은 재현되지 않았다.
- 최종 Yocto 재검증에서 trace-off 첫 PFDI `PROTOCOL_VERSION` timeout을
  재현했다. `--live-trace`는 통과했고 1 ms global quantum도 두 번 중 한 번
  실패해 timing knob가 근본 수정이 아님을 확인했다. 원인은 RSE channel에만
  있던 pending-mailbox 보존 정책이 AP/CL1 PFDI가 사용하는 공통 secure init에는
  없었던 것이다. 공통 정책 수정 뒤 SCP module unit 77/77, trace-off local 3/3,
  새 Yocto image 3/3과 각 49/49 coverage가 통과했다.
- malformed, denied, peer-offline, timeout 및 recovery path는 별도 A7 완료
  조건으로 남는다.

### 6.4 QEMU

**판정: MTTCG reset lifecycle 수정 승인.**

- target-vCPU exclusive context의 reset release와 stale `exit_request`, BQL
  GPIO write, pre-start reset replay 및 QK start/stop 순서를 함께 검토했다.
- reset-held CPU가 SystemC suspend owner가 되지 않는 invariant와 release 후
  wake/time-sync 복귀가 회귀 test에 포함됐다.
- KVM backend와 16 CPU stress/performance는 이번 TCG CFG2 검증 밖이다.

### 6.5 최종 결론

`A4_policy_routing`의 구조 폐쇄는 승인한다. local 및 Yocto 정상 부팅과
coverage는 구현 회귀 안전성을 충족한다. 다만 이를 완전한 APU/SMMU, safety
fault side effect 또는 FVP functional parity 승인으로 확대하지 않는다. 상세
증거와 잔여 항목은
[2026-07-16 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)에
기록한다.

## 7. 최종 구현 품질 재리뷰

전문 agent surface에 project 등록 `agent_type`을 지정할 수 없으므로, project
leader가 같은 변경 집합을 다음 다섯 lane으로 직접 재검토했다.

| lane | 판정 | 확인 내용 |
| --- | --- | --- |
| 목표·제약 | 통과 | A4 default-deny, canonical owner, SMD reset ownership, active 4-CPU/CFG2/Yocto 계약을 유지했고 OP-TEE 사용자 변경은 범위 밖으로 보존 |
| QA·회귀 | 통과 | targeted Python 64개, QBox component 33/33, reset 50/50, SCP module 77/77, 기준 local 5회·Yocto 3회와 최종 trace-off local/Yocto 각 3회 및 각 49항목 coverage |
| 코드 품질 | 통과 | broad bridge/ATU-check shadow 예외를 제거하고 stale warning을 실패로 처리, CPU 수는 단일 resolved 값에서 전달, reset policy는 address/software contract에 명시 |
| 보안 | 통과 | default-deny와 owner 경계를 약화하지 않았고 신규 secret·외부 dependency·권한 확대가 없음; debug/DMI 전체 capability matrix는 잔여 부채 |
| context/FVP | 통과 | Arm Zena CSS block diagram·programmer model·SCMI/PFDI/HIPC 문서와 FVP Linux SCMI log를 대조해 reset owner와 mailbox startup 소유권을 수정 |

최종 판정은 **승인**이다. 이 승인은 A4 policy-routing과 정상 boot/reset/SCMI
계약에 한정한다. 동일 hash 전체 FVP/QVP differential, KVM/16 CPU matrix,
malformed/error ABI 및 safety fault injection은 기존 잔여 gate를 유지한다.

# Apollo QBox Full Model Promotion Goal / PRD

작성일: 2026-06-14

## 목표

Apollo QBox full-system 모델에서 boot를 통과시키기 위해 남겨 둔
`gs_memory`/stub register window 중 safety, security, reset, power,
access-control, interrupt side effect가 필요한 IP를 full behavioral model로
승격한다.

최종 목표는 현재 `apollo-fvp` cfg2 software stack이 QBox에서 부팅되는 것에
그치지 않고, Arm Zena CSS FVP와 비교 가능한 fault handling, access
permission, reset/power sequencing, safety diagnostic behavior를 제공하는
것이다.

## 문제 정의

현재 Apollo QBox full-system은 RSE, Safety Island CL0/CL1, Primary Compute를
동시에 부팅할 수 있다. 그러나 일부 hardware window는 `gs_memory`로 열려
있어 firmware access가 실패하지 않는 대신 다음 동작이 모델링되지 않는다.

- FMU/SSU fault record, group status, critical/non-critical interrupt
- RSE SACFG/NSACFG/MPC/SIC secure/non-secure access control
- NI-710AE APU default-block policy와 ATU/NoC error response
- RGM, PIK, CSS counter/timer, SYSTOP/DBGTOP power/reset side effect
- AP secure watchdog refresh/control behavior
- RAS FFH, CPER, safety escalation path
- FVP RoS peripheral/debug surface 일부

이 상태에서는 positive boot evidence가 실제 FVP parity를 의미하지 않는다.
특히 negative safety/security test에서 QBox가 잘못 pass할 수 있다.

## 사용자와 이해관계자

| 사용자 | 필요 |
| --- | --- |
| QBox platform 개발자 | IP별 구현 범위, register behavior, Lua wiring, test gate |
| Firmware 개발자 | RSE/SCP/TF-A/OP-TEE/U-Boot failure path 재현성 |
| Linux/driver 개발자 | MHU, PFDI, RAS, watchdog, SMMU/I/O interrupt 관찰 가능성 |
| 검증 담당자 | FVP 대비 coverage, negative test, evidence bundle |
| 리뷰어 | `gs_memory` 유지/승격 근거와 남은 fidelity debt 추적 |

## 목표 범위

### 포함

- SI CL0 FMU/SSU SystemC model 구현과 Lua replacement
- RSE security/protection register model 구현
- SMD/NI-710AE APU access filter와 ATU error record 확장
- RGM/PIK/CSS counter/timer register model 확장
- AP secure watchdog full model 적용
- GIC/RAS/AP topology fidelity gap을 검증 가능한 backlog로 정리
- RoS/I/O/debug block의 구현 필요성을 SystemReady/debug parity 기준으로 분리
- component tests, platform map validation, live full-system boot, FVP comparison,
  negative fault test gate 정의

### 제외

- Secure boot 검증 shortcut 또는 known-good image bypass
- 모든 `gs_memory` 제거
- DRAM/SRAM/TCM/vring/shared-memory를 register model로 변환
- FVP 내부 구현 복제 없이 관찰 불가능한 micro-architecture 모델링
- AP 16-core 확장을 P0 safety/security 모델보다 먼저 수행
- CoreSight full trace capture를 정상 boot acceptance gate로 요구

## Acceptance Boundary

완료 주장은 다음 조건이 모두 충족될 때만 가능하다.

| ID | 조건 |
| --- | --- |
| AC-PRD-001 | `doc/apollo-qbox-hardware-ko.md`의 placeholder/fidelity debt 목록이 구현 결과와 함께 갱신된다. |
| AC-PRD-002 | P0 모델인 FMU/SSU와 RSE protection model의 unit/component tests가 pass한다. |
| AC-PRD-003 | Apollo full-system `live-cl0-cl1` boot가 기존 pass 상태를 유지한다. |
| AC-PRD-004 | Negative fault/access-control test가 QBox에서 의도한 fault, interrupt, RAZ/WI, DECERR/SLVERR 결과를 관찰한다. |
| AC-PRD-005 | FVP comparison에서 지원되는 marker와 의도적으로 남긴 gap이 machine-readable output으로 분리된다. |
| AC-PRD-006 | 남은 `gs_memory`는 `memory-backing`, `accepted-placeholder`, `unsupported-gap` 중 하나로 분류된다. |

## Milestones

| Milestone | 산출물 | 완료 기준 |
| --- | --- | --- |
| M0 Baseline lock | coverage ledger와 현 상태 report | 현재 boot, placeholder, missing IP 목록 고정 |
| M1 Safety model | `zena_fmu`, `zena_ssu` | FMU/SSU unit tests와 CL0 boot regression pass |
| M2 Security/access model | RSE protection + APU/access filter | secure/non-secure negative tests pass |
| M3 System management model | RGM/PIK/counter/watchdog | reset/power/watchdog regression과 SCMI path pass |
| M4 Interrupt/RAS parity | GIC/RAS/FFH coverage | fault injection이 GIC/RAS/PFDI 경로로 관찰됨 |
| M5 Peripheral/debug parity | RoS/I/O/CoreSight 선택 구현 | SystemReady/debugger 목표 test가 요구할 때 pass |

## 성공 지표

- 기존 full-system boot time과 pass marker가 regression되지 않는다.
- `gs_memory` register placeholder 수가 감소하고, 남은 항목의 분류가 명확하다.
- safety/security negative tests가 silent pass가 아니라 관찰 가능한 fault로 끝난다.
- FVP와 QBox의 차이가 `not-modeled`, `service-modeled`, `full-modeled`로
  기록된다.

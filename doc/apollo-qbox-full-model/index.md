# Apollo QBox Full Model 승격 문서

작성일: 2026-06-14

이 문서 세트는 `doc/apollo-qbox-hardware-ko.md`의 `gs_memory` 및
placeholder 분석을 바탕으로, Apollo QBox를 boot-compatible 모델에서
FVP-equivalent 모델로 단계적으로 끌어올리기 위한 구현 계약이다.

## 문서 구성

| 문서 | 목적 |
| --- | --- |
| [Goal / PRD](goal-prd-ko.md) | 목표, 비목표, acceptance boundary, milestone 정의 |
| [Spec](spec-ko.md) | 기능/비기능 요구사항, 모델 승격 기준, IP별 요구사항 |
| [Design / Architecture](design-architecture-ko.md) | SystemC/QEMU/Lua 구조, 모델 경계, fault/reset/access-control 흐름 |
| [Implementation Tasks](implementation-tasks-ko.md) | 구현 순서, 파일 단위 작업, 검증 명령, commit 단위 |
| [Verification / Test](verification-test-ko.md) | component, platform, runtime, FVP comparison, negative fault 검증 기준 |
| [Coverage Ledger](coverage-ledger.md) | Apollo QVP placeholder 분류와 first wave backend gate |
| [Review Notes](review-notes-ko.md) | 문서 리뷰 결과, 수정사항, 구현 전 owner decision 요청 |
| [Decision Record](decision-record-ko.md) | 확정된 구현 wave, runtime policy, follow-up epic 분리 기준 |
| [First Wave Status](first-wave-status-ko.md) | 권장 결정 채택 이후 구현/검증 evidence와 runtime gate 결과 |

## 범위 결정

모든 `gs_memory`를 full model로 바꾸는 것이 목표가 아니다. DRAM, SRAM,
TCM, vring, SCMI shared memory, firmware image load area처럼 저장공간 자체가
본질인 영역은 계속 memory model로 유지한다. 승격 대상은 다음 성질을 가진
register/IP window이다.

- firmware가 status bit, W1C bit, key sequence, reset value를 관찰한다.
- write가 interrupt, reset, power state, fault state, access permission을
  바꾼다.
- 잘못된 접근이 RAZ/WI, DECERR, SLVERR, fault record 같은 관찰 가능한
  결과를 만들어야 한다.
- FVP와 QBox의 차이가 safety, security, PFDI, RAS, SCMI power/reset,
  Linux driver probe 결과를 바꿀 수 있다.

## 우선순위

| Priority | 영역 | 이유 |
| --- | --- | --- |
| P0 | SI CL0 FMU/SSU | safety fault aggregation과 external safety state의 중심이며 현재 `gs_memory` placeholder |
| P0 | RSE SACFG/NSACFG/MPC/SIC | secure/non-secure 접근제어와 boot chain 신뢰성의 핵심 |
| P1 | NI-710AE APU, ATU error record, SMD access filter | Zena CSS programmer model의 default-block access 정책을 QBox에서 검증 가능하게 함 |
| P1 | RGM, SYSTOP/DBGTOP PIK, CSS counters/timers | reset/power sequencing과 SCMI power/reset runtime fidelity 개선 |
| P2 | AP secure watchdog, RAS FFH, AP cluster AE/control | secure-world error path, RAS/PFDI negative test fidelity 개선 |
| P2 | GIC-720AE multiview parity와 AP 16-core topology | FVP 구조 parity 확장. 현재 cfg2 4-core boot gate 이후 수행 |
| P3 | RoS/I/O/debug coverage | SystemReady, board peripheral, CoreSight/debugger parity 목표에서 수행 |

## 확정 결정

구현 착수 전 owner decision은 [Decision Record](decision-record-ko.md)에
확정했다. 첫 구현 wave는 `MODEL-000`부터 `MODEL-060`까지 진행하고,
APU/ATU denied access는 runtime observe/report mode로 시작한다. GIC/RAS/AP
16-core 및 RoS/debug parity는 별도 후속 epic으로 분리한다.

현재 first-wave 구현 및 검증 상태는
[First Wave Status](first-wave-status-ko.md)에 기록한다. 이 상태 문서는
component/backend 검증 통과 결과와 full-system runtime gate evidence를
구분한다.

## 주요 근거

- `doc/apollo-qbox-hardware-ko.md`
- `doc/apollo-fvp-hardware-analysis-ko.md`
- `doc/arm-zena-css-hardware-blocks.md`
- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `tools/qbox/platforms/apollo/hw-block/`
- `tools/qbox/systemc-components/`

# Apollo QBox Full Model Promotion Review Notes

작성일: 2026-06-14

## 리뷰 범위

검토한 문서:

- `doc/apollo-qbox-full-model/index.md`
- `doc/apollo-qbox-full-model/goal-prd-ko.md`
- `doc/apollo-qbox-full-model/spec-ko.md`
- `doc/apollo-qbox-full-model/design-architecture-ko.md`
- `doc/apollo-qbox-full-model/implementation-tasks-ko.md`
- `doc/apollo-qbox-full-model/verification-test-ko.md`

검토 기준:

- `doc/apollo-qbox-hardware-ko.md`의 placeholder/fidelity debt 분석과 일치하는가
- `doc/apollo-fvp-hardware-analysis-ko.md`와 Zena CSS guide의 block/IP 목록을
  빠뜨리지 않는가
- spec 요구사항이 implementation task와 verification gate로 추적되는가
- 구현 전 owner decision이 필요한 범위가 명시되어 있는가

## 리뷰 결과

| 항목 | 결과 |
| --- | --- |
| 목표/비목표 | 적합. 모든 `gs_memory` 제거가 아니라 side-effect register/IP 승격으로 범위가 고정되어 있음 |
| P0/P1 우선순위 | 적합. FMU/SSU, RSE protection, APU/ATU, RGM/PIK가 먼저 배치됨 |
| memory 유지 기준 | 적합. DRAM/SRAM/TCM/vring/SCMI shmem은 `memory-backing`으로 유지 |
| task 검증성 | 보완 완료. FR별 task/verification traceability table 추가 |
| 분류 용어 | 보완 완료. `unsupported-gap`을 spec classification에 추가 |
| P2/P3 범위 | owner decision 필요. FR-007/FR-008은 현재 implementation wave에 넣으면 범위가 크게 커짐 |

## 리뷰 중 수정한 사항

- `spec-ko.md`에 `unsupported-gap` 분류를 추가했다.
- `implementation-tasks-ko.md`에 requirement traceability table을 추가했다.
- `implementation-tasks-ko.md`에 `MODEL-110 Future parity backlog split`을
  추가해 GIC/RAS/AP16/RoS/debug 범위가 암묵적으로 남지 않게 했다.
- `index.md`에 review notes 링크와 구현 전 결정 필요 항목을 추가했다.

## 구현 전 결정 요청

### D1. 첫 구현 wave 범위

권장: `MODEL-000`부터 `MODEL-060`까지 먼저 진행한다.

포함:

- coverage ledger
- FMU/SSU component와 CL0 Lua wiring
- RSE protection model
- APU/ATU access filter의 component-level strict test와 runtime observe-mode

보류:

- RGM/PIK/counter
- AP secure watchdog
- GIC/RAS/AP16
- RoS/I/O/debug

이유: FMU/SSU와 RSE/access-control이 현재 `gs_memory` debt 중 safety/security
impact가 가장 크고, 같은 PR에서 GIC/RAS/RoS까지 포함하면 검증 표면이 너무
넓어진다.

### D2. APU/ATU denied access runtime 정책

권장: component tests에서는 strict deny를 검증하고, full-system runtime에서는
첫 wave 동안 observe/report mode로 시작한다.

선택지:

- Strict from start: FVP default-block에 더 가깝지만 boot regression 원인 분리가
  어려울 수 있다.
- Observe first: boot 안정성을 유지하면서 어떤 접근이 차단 대상인지 기록하고,
  두 번째 wave에서 strict로 전환한다.

### D3. FR-007/FR-008 처리

권장: GIC/RAS/AP 16-core와 RoS/I/O/debug parity는 별도 follow-up epic으로
분리한다.

이유:

- 현재 `apollo-fvp` configured AP CPU count는 4이고, QBox full-system boot
  gate도 4-core 경로를 기준으로 검증되어 있다.
- RAS FFH/CPER, full GIC-720AE, CoreSight/RoS peripheral parity는 각각 독립
  설계/검증 문서가 필요한 크기다.

### D4. Component granularity

권장: 작은 component를 유지한다.

- `zena_fmu`
- `zena_ssu`
- `rse_protection_ctrl`
- `host_apu_filter`
- `host_rgm`
- `host_pik`

공통 W1C/PID/CID/error-record helper만 shared common code로 뺀다. 하나의
대형 `zena_system_mgmt` model로 합치면 초기 wiring은 쉬워도 review와
negative test isolation이 나빠진다.

### D5. TRM/source 기준

권장: 현재 repo-local Zena CSS guide와 기존 QBox/Firmware code를 기준으로
구현하고, 외부/라이선스 TRM이 필요한 register는 `unsupported-gap`으로 남긴다.

이유: 문서화된 local guide는 현재 repository에서 재현 가능한 근거다. 별도
TRM 기반 구현은 문서 버전과 접근 권한을 명시한 뒤 진행해야 review가 가능하다.

# Apollo QBox Full Model Promotion Decision Record

작성일: 2026-06-14

## 결정 상태

`review-notes-ko.md`의 권장안을 그대로 채택한다. 이 문서는 구현자가 따라야
하는 확정 decision record이다.

## 확정 결정

| ID | 결정 | 구현 영향 |
| --- | --- | --- |
| D1 | 첫 구현 wave는 `MODEL-000`부터 `MODEL-060`까지로 제한한다. | coverage ledger, FMU/SSU, CL0 wiring, RSE protection, 기존 `rse_atu` 기반 APU/ATU coverage gate까지만 첫 wave에 포함 |
| D2 | APU/ATU denied access는 기존 `rse_atu`의 translation/error path를 component evidence로 사용하고, full-system runtime에서는 observe/report mode로 시작한다. | boot regression을 줄이면서 차단 대상 접근을 evidence로 수집한 뒤 후속 wave에서 strict APU filter 전환 |
| D3 | FR-007 GIC/RAS/AP topology와 FR-008 RoS/I/O/debug extension은 별도 follow-up epic으로 분리한다. | 첫 wave completion gate에서 GIC/RAS/AP16/RoS/debug full parity를 요구하지 않음 |
| D4 | 모델은 작은 SystemC component 단위로 유지하고 공통 register/error-record helper만 공유한다. | `zena_fmu`, `zena_ssu`, `rse_protection_ctrl`, 후속 `host_apu_filter`, `host_rgm`, `host_pik`를 독립 구현 |
| D5 | repo-local Zena CSS guide와 현재 QBox/Firmware code를 구현 기준으로 삼고, 외부/라이선스 TRM이 필요한 register는 `unsupported-gap`으로 남긴다. | 재현 가능한 local evidence를 우선하고 TRM-dependent gap은 명시적으로 추적 |

## First Wave Scope

첫 구현 wave에 포함되는 작업:

- `MODEL-000`: baseline coverage ledger 작성
- `MODEL-010`: FMU/SSU test scaffolding
- `MODEL-020`: `zena_fmu` component
- `MODEL-030`: `zena_ssu` component
- `MODEL-040`: Safety Island CL0 Lua wiring
- `MODEL-050`: RSE protection model
- `MODEL-060`: 기존 `rse_atu` 기반 APU/ATU coverage gate

첫 구현 wave에서 제외되는 작업:

- `MODEL-070`: RGM/PIK/counter control models
- `MODEL-080`: AP secure watchdog
- `MODEL-110`: GIC/RAS/AP16/RoS/I/O/debug future parity backlog 구현

단, `MODEL-090` coverage/verifier update는 첫 wave 산출물을 검증하기 위해
필요한 최소 범위만 포함한다. P2/P3 항목은 `accepted-placeholder` 또는
`unsupported-gap`으로 분류하고 후속 epic으로 연결한다.

## APU/ATU Runtime Policy

첫 wave의 runtime 정책:

- component/unit tests: denied access는 strict error response를 검증한다.
- full-system runtime: denied access 후보를 observe/report mode로 기록한다.
- coverage output: observe/report mode임을 명시한다.
- 후속 strict 전환 조건: full-system boot에서 필요한 허용 window가 ledger로
  고정되고, deny 후보가 intentional fault test로 분리된 뒤 전환한다.

## Follow-Up Epic 분리 기준

다음 항목은 첫 wave 구현 완료 조건이 아니다. 별도 spec/design/task 문서가
있을 때만 구현에 착수한다.

- Full GIC-720AE multiview parity
- AP 16-core live topology와 16 redistributor frame parity
- RAS FFH/CPER functional model
- AP cluster RAS/PMU/MPAM/FHI/ERI 확대
- RoS System Registers, Virtio P9, VSI, RoS UART, TRNG, nvCounter, Ethernet
- SMD/RoS flash 추가 parity
- IO_REGBANK, PCIe PHY/controller config
- CoreSight ROM table, CTI, ETF, ATF, STM, CATU

## Verification Contract

첫 wave 완료 주장은 다음 evidence가 모두 있어야 한다.

- `git diff --check`와 `git -C tools/qbox diff --check` 통과
- FMU/SSU component tests 통과
- RSE protection component tests 통과
- 기존 `rse_atu` component tests와 APU/ATU backend coverage gate 통과
- Apollo full-system `live-cl0-cl1` boot regression 통과
- coverage audit에서 P0/P1 항목의 unclassified placeholder가 없음
- P2/P3 항목은 `accepted-placeholder`, `unsupported-gap`, 또는 follow-up epic
  링크로 분류됨

## 문서 소유권

이 decision record가 `review-notes-ko.md`보다 우선한다. 이후 구현 중
결정이 바뀌면 이 파일을 먼저 갱신하고, 관련 spec/task/verification 문서를
따라서 갱신한다.

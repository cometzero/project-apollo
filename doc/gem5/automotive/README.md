# Automotive SoC에서 Apollo gem5 활용

조사 기준일: **2026-10-26**. 현재 Apollo checkout, 기존 benchmark 기록,
gem5·Arm·Autoware·MLCommons 공식 자료 및 원저자 논문을 기준으로 작성했다.
이번 작업은 조사와 문서 작성이며 새 build, simulation 또는 Orin 측정을 수행하지 않았다.

**2026-10-28 추가:** SoC 설계 전 cache/CPU/NoC/DRAM 사양을 선정하기 위한
[Requirement](soc-spec/requirement.md)부터 [Verification](soc-spec/verification.md)까지의
문서 5개를 추가했다. 작성 당시 새 campaign은 `NOT_RUN`이었다. 이후 실행 상태는
[진행 기록](soc-spec/campaign-20261028.md)을 따른다. 제품 성능 목표와 비용 자료는 아직 `TBD`다.

Apollo gem5의 우선 활용 대상은 **자율주행 workload가 공유하는 cache·interconnect·DRAM의
병목과 간섭을 분리하고, software 배치 및 architecture 변경의 효과를 비교하는 것**이다.
현재 Cortex-A720AE proxy의 DMIPS를 실물 수치에 맞추는 작업만으로 이 목적을 달성할 수는 없다.
실험에 필요한 경로가 모델링되어 있는지, 입력과 ROI가 대표성이 있는지, hardware와
어떤 범위에서 일치하는지부터 확인해야 한다.

Arm은 Zena CSS를 16 Cortex-A720AE cores, Cortex-R82AE Safety Island,
CMN S3AE 및 accelerator 통합을 포함하는 automotive compute subsystem으로 설명한다.
Apollo gem5가 그 모든 IP의 timing과 safety 동작을 구현했다는 뜻은 아니다.
[Arm Zena CSS 발표](https://newsroom.arm.com/news/arm-unveils-zena-css)

## 문서 구성

| 문서 | 답하는 질문 |
|---|---|
| [성과·남은 이슈·후속 작업 인계 (2026-11-01)](soc-spec/handoff-20261101.md) | 무엇을 달성했고 무엇이 미완료이며 어디서 재개하는가? |
| [현재 구성과 지원 경계](capabilities.md) | Apollo에서 무엇을 실행할 수 있고 어떤 경로가 빠져 있는가? |
| [활용 시나리오와 추진 순서](use-cases.md) | 어떤 engineering 결정을 위해 gem5를 사용해야 하는가? |
| [Workload 선정](workloads.md) | Autoware, MLPerf Automotive, microbenchmark를 어떻게 조합하는가? |
| [실험 및 측정 절차](experiments.md) | 기존 launcher·checkpoint·ROI를 이용해 어떻게 비교하는가? |
| [조사 출처](sources.md) | 공개 자료가 뒷받침하는 범위와 로컬 구현 근거는 무엇인가? |
| [SoC 사양 탐색 — Requirement](soc-spec/requirement.md) | 어떤 결정과 입력이 필요하고 무엇을 만족해야 하는가? |
| [추가 논문 검토와 목표 보강](soc-spec/literature-methodology-20261030.md) | Baseline 대비 경향과 후보 순위를 어떤 근거로 신뢰할 수 있는가? |
| [SoC 사양 탐색 — Plan](soc-spec/plan.md) | 기존 evidence부터 후보 사양 선정까지 어떤 순서로 진행하는가? |
| [SoC 사양 탐색 — Design](soc-spec/design.md) | Candidate, workload, clock/DRAM, ROI와 evidence를 어떻게 연결하는가? |
| [SoC 사양 탐색 — Implementation](soc-spec/implementation.md) | 기존 구현을 어떻게 재사용하고 어느 repository를 보강하는가? |
| [SoC 사양 탐색 — Verification](soc-spec/verification.md) | 요구사항별 검증과 사양 판정의 근거는 무엇인가? |

기본 build, boot, source 구조는 [상위 기술 문서](../README.md)를 따른다.
이 문서 모음은 그 실행 기반으로 수행할 automotive 연구와 실무 실험을 다룬다.

## SoC 사양 선정을 위한 실행 순서

1. **Target와 baseline:** 제품 목표·scenario의 미정 항목을 식별하고 기존 evidence와
   현재 profile/image/snapshot의 재사용 가능성을 확인한다.
2. **Memory 병목과 대표 kernel:** CPU/cache/CHI/DRAM 공급·처리 한계를 구분하고,
   source/input이 고정된 image preprocessing 호출에 correctness와 ROI를 확보한다.
3. **사양 후보와 동시 부하:** Cache/clock/channel 민감도와 interaction으로 후보를
   줄인 뒤 foreground/background 및 필요한 외부 IP traffic를 비교한다.
4. **불확실성과 비용:** Model 가정 변화, target 여유, IP/물리설계 자료를 결합해
   최소 충족안/여유안/제외안 또는 미확정 사유를 남긴다.

이 순서는 **2026-10-28 사양 선정 목적의 계획**이며 새 실험의 완료 보고가 아니다.
구체적인 단계와 종료 조건은 [Plan](soc-spec/plan.md)을 따른다. 기존
[활용 시나리오](use-cases.md)와 [Workload 후보](workloads.md)는 확장 가능한 조사 목록이다.

## 결과를 어디까지 사용할 수 있는가

| 환경 | 이 프로젝트에서의 주된 역할 | 추가 근거가 필요한 주장 |
|---|---|---|
| QBox / FVP | boot, driver, firmware handoff, register/IRQ와 software 통합 | silicon cycle timing 및 실제 worst-case latency |
| gem5 | 명시한 timing 가정에서 cache·fabric·memory·CPU 상호작용과 설계 대안 비교 | 실물 A720AE 성능, production NPU 처리량, 온도·전력의 절대값 |
| Orin hardware | benchmark 구현 검증, 실제 contention·cache·memory 특성 관찰 | 다른 CPU·SoC인 A720AE/Zena의 parameter 및 결과로 직접 전용 |
| 대상 SoC hardware / 검증된 IP model | 대상 platform의 calibration 및 독립 validation | 관찰하지 않은 모든 workload·상태에 대한 일반화 |

`SOURCE_AVAILABLE`은 소스가 존재함, `RECORDED_PASS`는 링크한 과거 실행의 한정된 성공,
`NOT_RUN`은 새 제안 또는 미검증 경로, `UNSUPPORTED`는 현재 명시적 지원 제약을 뜻한다.
문서의 정적 검사 성공은 이 중 어느 runtime 상태도 변경하지 않는다.

상대 비교도 자동으로 유효해지지 않는다. 예를 들어 CPU request-generation이 부정확하면
channel 수 증가의 효과가 왜곡될 수 있다. 모델 가정과 workload를 바꿔도 결론이 유지되는지
확인하고, 범위를 넘는 결과는 가설로 남긴다. 관찰된 최대 latency는 WCET 증명이 아니며,
이 문서와 실험은 ISO 26262 qualification 또는 freedom-from-interference 입증 자료를
완성한 것으로 취급하지 않는다.

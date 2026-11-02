# Apollo SoC 사양 탐색: 추가 논문 검토와 목표 보강

검토일: 2026-10-30. 이 문서는 방법론 검토이며 새 simulation/HW 측정 결과가 아니다.
[Requirement](requirement.md), [Plan](plan.md), [Verification](verification.md)의 후속 campaign에 적용한다.
기존 campaign의 입력, 5% gate, 결과 및 traceability ID는 소급 변경하지 않는다.

## 1. 목표와 증거 수준

목표는 **명시한 baseline 대비 사양 변경 효과와 원인을 측정하고, 모델 가정의 불확실성에도
유지되는 후보를 찾는 것**이다. A720AE의 절대 DMIPS나 실물 SoC 성능 일치를 완료 기준으로
삼지 않는다. 상대 성능도 모델 오류가 상쇄된다는 보장은 없으므로 robustness 검증이 필요하다.

- Measurement validity: output, ROI, clock/config, counter 의미가 유효한가?
- Numerical stability: warmup/측정 길이와 입력·배치 변화에서 결과가 안정적인가?
- Model credibility: 주장하는 현상과 병목을 모델이 표현하고 reference로 확인했는가?
- Decision robustness: 불확실한 가정에서도 후보의 이득과 순위가 유지되는가?
- Product adequacy: 실제 target와 비용을 만족하는가? 현재 target 미정이므로 UNDECIDED다.

첫 두 항목 통과를 silicon accuracy로 표현하지 않는다. Orin은 workload/계측 비교 장비다.
Orin reference model 없이 Orin 측정만 수행한 것을 gem5 calibration으로 부르지 않는다.

## 2. 추가로 검토한 연구

### L1 — At the Locus of Performance (ACM TACO, 2023)

[저자 기관의 원문 PDF](https://research.chalmers.se/publication/539317/file/539317_Fulltext.pdf),
§5.1–5.2, Table 2, Figures 7–8을 확인했다. A64FX baseline에서 core 수 변경과 cache
변경을 분리한 중간 configuration을 둔다. STREAM의 working set을 변화시켜 cache 단계와
bandwidth를 점검하고, application kernel에서 cache latency/capacity/bandwidth 민감도를
각각 분석한다. 축소 kernel의 작은 memory footprint 때문에 일부 cache 변화가 드러나지
않는다는 한계도 설명한다. 이는 HPC 및 가상 LARC 연구이며 자동차 SoC 검증 결과가 아니다.

**적용:** Cache 용량만 변경하지 말고 latency/bank/처리량 조건을 기록한다. 축소 workload가
cache 안에 들어가면서 원래 병목을 없애지 않았는지 검증한다. CPU 수 증가와 cache 증가를
분리한 control을 둔다. 논문의 speedup 수치를 Apollo 예상치로 가져오지 않는다.

### L2 — Validation of the gem5 Simulator for x86 Architectures (PMBS, 2019)

[학회 원문 PDF](https://sc19.supercomputing.org/proceedings/workshops/workshop_files/ws_pmbss111s2-file1.pdf),
Introduction 및 validation methodology를 확인했다. Intel Core i7-4770과 hardware counter를
대조하여 오류 원인을 수정한다. 저자들은 해당 검증의 absolute mean error가 136%에서
6% 미만으로 감소했다고 보고한다. 이 수치는 해당 x86 모델·시험의 결과이며 A720AE나
LPDDR5X에 적용할 허용 오차가 아니다.

**적용:** 하나의 runtime 점수에 맞추는 대신 instruction/cycle/cache 등 의미가 대응되는
counter로 원인을 확인한다. Calibration용 microbenchmark와 독립 validation kernel을
분리한다. Simulator revision이 바뀌면 영향 있는 baseline 검증을 재실행한다.

### L3 — Simulating DRAM controllers for future system architecture exploration (ISPASS, 2014)

[저자 소속 기관의 논문 초록](https://pure.psu.edu/en/publications/simulating-dram-controllers-for-future-system-architecture-explor/)
을 확인했다. Full-system interaction을 위한 event-based DRAM controller와 다른 DRAM
simulator의 비교를 다룬다. 초록은 DDR3/LPDDR3/WideIO를 언급한다. 이번에는 원문 전체의
오차 표와 세부 조건을 검토하지 않았으므로 정량 정확도 근거로 쓰지 않는다.

**적용:** DRAM device peak뿐 아니라 controller queue/scheduling과 CPU 공급량을 구분한다.
Native generator의 backend 시험과 CPU 경유 workload를 함께 해석한다. 옛 LPDDR3 검증을
현재 LPDDR5X proxy 검증으로 대체하지 않는다.

### 기존 검토와 연결

[DATE 2021 memory calibration 원문](https://past.date-conference.com/proceedings-archive/2021/pdf/1584.pdf)은
microbenchmark 보정과 application validation을 분리하는 근거다.
[gem5-Aladdin 연구](https://research.nvidia.com/index.php/publication/2016-10_co-designing-accelerators-and-soc-interfaces-using-gem5-aladdin)는
accelerator 단독 처리량 외 data movement/coherence와 SoC interaction을 다루는 근거다.
위 연구들의 구성·정량 정확도를 Apollo에 직접 전이하지 않는다.

GemStone ISPASS 2018도 추가 조사했지만 기관 repository는 engine에서 auth_required로
종료했고 다른 저자 페이지는 본문 대신 form 오류를 반환했다. HTTP/engine 성공만으로
내용 확보를 인정하지 않았으며, 이번 변경의 상세 근거로 사용하지 않았다.

## 3. 후속 campaign의 실험 설계

| 순서 | 실행과 산출물 | 판단 기준 |
|---|---|---|
| 1 | 기존 결과의 validity/stability/fidelity 한계를 분리한 inventory | 기존 FAIL을 PASS로 바꾸지 않음 |
| 2 | Orin reference 측정: working-set sweep, dependent/random access, streaming, workers scaling | 동일 workload 의미, affinity/clock/PMU 제약 기록; A720AE calibration 주장 금지 |
| 3 | Baseline + cache/CPU/fabric/DRAM 단일 변경과 사전 지정 interaction | 동일 input/software/ROI; effect size와 병목 counter 동시 보고 |
| 4 | Shortlist 최대 2개 + baseline의 uncertainty control | CPU 요청 능력, cache latency/resource 등 가정별 순위 유지 여부 |
| 5 | 독립 kernel 또는 다른 memory footprint, foreground/background 조건 | calibration workload에만 맞춘 효과와 scenario 의존성 구분 |
| 6 | Decision record | robust/conditional/inconclusive 탐색 결론; 제품 판정은 별도 |

불확실성 범위는 vendor 정보, Orin reference 또는 공개 자료의 출처와 함께 정한다.
근거 없는 ±20%를 HW uncertainty로 제시하지 않는다. 근거가 없으면 가설적 stress range로
명명하고 실제 HW를 포괄한다는 주장을 하지 않는다. 상한·하한 corner 몇 개의 결과는
전 구간 최적성 증명이 아니며 rank reversal이 발견되면 필요한 범위만 추가 분석한다.

Latency speedup은 T_baseline/T_candidate, throughput gain은
Q_candidate/Q_baseline−1로 계산한다. Baseline과 후보는 같은 uncertainty 조건에서 짝지어
비교한다. 관측 변동 범위와 모델 가정 범위는 분리하며 deterministic 반복으로 통계적
confidence interval을 만들지 않는다. 입력/배치 반복의 sample 수와 범위를 함께 보고한다.

## 4. 실행 비용과 종료 정책

새 campaign은 시작 전에 최대 run 수, host 시간 예산, warmup/length 단계, tolerance,
최소 의미 있는 effect와 중단 조건을 manifest에 고정한다. 예산의 숫자가 빠졌으면 장시간
queue를 시작하지 않는다. 예산은 pilot 시간과 현재 resource로 산정하며 임의 시간 보장은 없다.
예산 소진 시 미수행은 NOT_RUN, 미수렴 판단은 INCONCLUSIVE로 남기고 완료로 위장하지 않는다.

Primary performance metric과 explanatory counter를 사전에 분류한다. Primary가 안정적이고
counter가 불안정하면 관측된 성능과 원인 설명의 신뢰도를 따로 보고한다. Steady-state를
입증하지 못한 결과를 steady-state PASS로 승격하지 않는다. 기존 campaign의 모든 gate는
그대로 보존하며 이 분리는 다음 contract부터 적용한다.

단일 image kernel은 전체 Autonomous Driving workload가 아니다. 축소 입력은 working set,
MPKI, DRAM bytes/output, parallel scaling을 원래 조건과 대조한 뒤 사용한다. 검증되지 않은
GPU/NPU traffic는 synthetic envelope로 남기며 CPU background로 대체 검증하지 않는다.

## 5. 문서와 검증 연결

| 기존 요구사항 | 보강 내용 | 후속 검증 evidence |
|---|---|---|
| REQ-DSE-002/008 | workload 의미 및 독립 validation 구분 | source/input/ROI와 calibration/validation 목록 |
| REQ-DSE-004/005/006/007 | cache 비용, CPU 공급량, fabric/controller uncertainty | 가정 출처, effective config, control 결과 |
| REQ-DSE-009/010 | effect 원인과 rank robustness | paired effect, counter, reversal 및 한계 |
| REQ-DSE-014/016 | 증거 수준·예산·제품 판단 분리 | 실행 상태와 decision record |

추가 방법론의 실행 상태는 NOT_RUN이다. 기존 41-ID 검증 범위를 축소하거나 이 문서 작성으로
완료하지 않는다. 기존 도구가 새 evidence를 지원하는지 확인한 뒤 필요한 최소 확장만 한다.

## 6. 접근 evidence

insane-search engine의 JSON/trace는
`build/qbox-apollo-qvp/gem5/literature-20261030/`에 보존했다.
L1/L2는 PDF text, L3는 기관 초록이다. 검색 snippet은 원문 검토를 대신하지 않는다.

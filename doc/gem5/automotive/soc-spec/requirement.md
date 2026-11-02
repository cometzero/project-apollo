# Apollo gem5 SoC 사양 탐색 — Requirement

작성일: **2026-10-28**. 상태: **Draft / 사양 탐색 요구사항**.
이 문서는 새로운 benchmark 실행이나 제품 사양 확정 결과가 아니다.

문서 순서: **Requirement** → [Plan](plan.md) → [Design](design.md) →
[Implementation](implementation.md) → [Verification](verification.md).
[Automotive 문서 목록](../README.md)으로 돌아간다.

## 2026-10-30 목표 보강

현재 완료 목표는 baseline 대비 효과·병목·후보 순위의 robustness를 명시한 범위에서 설명하는 것이다. Silicon 절대 성능 일치는 별도 reference HW/IP validation이 필요한 후속 목표다. Measurement validity, numerical stability, model credibility, decision robustness, product adequacy를 구분한다. 기존 REQ-DSE-009/010/014/016의 해석을 보강하며 제품 target 미정은 계속 UNDECIDED다.
세부 근거와 실행 정책은 [추가 논문 검토](literature-methodology-20261030.md)를 따른다.

## 1. 목적과 의사결정 범위

SoC 설계 전에 representative workload의 요구 성능을 만족하는 CPU, L2/L3/SLC,
NoC, DRAM 후보를 비교한다. 결과는 **최소 충족안, 여유 확보안, 비용 대비 효과가
작은 안**과 각 판단의 근거다. gem5의 성능 추정에 IP 공급사·물리설계의 구현 비용과
제약을 결합하며, 모델에서 좋은 결과가 나온 조합을 곧바로 제작 가능한 사양으로
간주하지 않는다.

1차 범위는 현재 AP Linux 경로의 memory 병목 분석과 사양 민감도다. 이후 고정된
image preprocessing kernel, 동시 CPU workload, 근거 있는 외부 IP traffic를 추가한다.
기존 [workload 후보](../workloads.md)의 point-cloud/NDT/MPC는 후속 후보로 유지한다.
특정 kernel 하나가 전체 Autonomous Driving workload를 대표한다고 가정하지 않는다.

포함하지 않는 판정은 silicon 성능 보증, RTL/PHY sign-off, WCET 증명, ISO 26262
qualification, 실제 NPU/GPU inference 성능, 미보정 전력·온도 절대값이다.
Orin은 workload와 계측 검증용 비교 장비이며 A720AE의 정답 모델이 아니다.

## 2. 요구사항의 입력과 미확정 항목

아래 값은 제품 요구사항이 제공되지 않았으므로 **TBD**다. 임의의 FPS, deadline,
전력 예산을 제품 목표로 만들지 않는다. 민감도 탐색은 시작할 수 있지만 해당 값이
필요한 사양 충족 판정은 `UNDECIDED`로 남긴다.
2026-10-28 사용자는 **제품 목표 미정 — 탐색 결과로 진행**을 확인했다.

| 입력 | 기록할 내용 | 주 담당 | 미확정 시 가능한 작업 |
|---|---|---|---|
| Application target | 기능별 throughput, latency의 시작·끝, 단위, deadline | System/application 담당 | 고정 입력의 상대 비교 |
| 실행 시나리오 | 해상도/point 수, rate, burst, 동시 기능, 배치, 입력 분포 | Application 담당 | 명시한 synthetic scenario 비교 |
| Resident memory 예산 | OS/reserved/CMA, model/map, 동시 frame/buffer, 중복 계상 없는 transient peak와 여유 | System/application 담당 | Bandwidth 탐색; 제품 DRAM capacity 충족 판정은 보류 |
| 정확도 | reference output, integer 일치 또는 floating-point tolerance | Algorithm 담당 | correctness fixture 준비 |
| 구현 가능한 사양 | IP version, 제공 cache/clock/core 옵션, 지원 memory part | SoC/IP 담당 | proxy parameter 민감도 |
| 비용·제약 | area, power, voltage/OPP, thermal, pin/package, 가격 | IP/물리설계 담당 | 성능만 비교; PPA 최적안 판정 보류 |
| 보정·불확실성 | IP model/RTL/대상 hardware 근거, 오차 범위 | Model 담당 | 가정 범위를 표시한 robustness 비교 |
| 여유와 표본 정책 | scenario별 margin, sample count, quantile, convergence 기준 | System/성능 담당 | 관측값 및 sample 수 보고 |

Target의 최소 record는 `target_id`, version, required scenario, metric, statistic,
comparator(`<=` 또는 `>=`), limit, unit, sample/arrival 정의, 최소 표본·confidence 정책,
margin, 근거, 담당이다. `kernel latency`, `request latency`, `sensor-to-actuator latency`를
서로 대체하지 않는다. Latency의 mean/p99/observed maximum도 서로 다른 statistic이다.

<a id="target-rules"></a>
### Target와 여유율 판정

정의한 단위로 환산한 statistic을 `x`, nominal limit를 `T`, 추가 여유율을 `m`으로 둔다.
값은 finite여야 하며 latency/throughput 측정값은 음수가 될 수 없다. 아래 비율 계산에서는
`T > 0`이어야 한다. `m`은 무차원 비율로
고정한다. 이미 여유가 포함된 limit라면 그 근거를 기록하고 `m = 0`으로 두어 중복 적용하지
않는다. 아래 식은 제안하는 campaign 계약이며 현재 launcher의 구현이 아니다.

- Latency 등 upper bound: `0 <= m < 1`, `x <= T * (1 - m)`이면 `MEETS`.
- Throughput 등 lower bound: `m >= 0`, `x >= T * (1 + m)`이면 `MEETS`.
- 유효한 필수 측정값이 정의한 comparator를 만족하지 못하면 `DOES_NOT_MEET`; 경계와 같으면 충족한다.
- Target/sample 정책 누락, 단위·statistic 불일치, 부족한 표본, invalid/timeout 측정은
  `UNDECIDED`다. Timeout을 deadline miss나 무한 latency sample로 대체하지 않는다.
- Deadline-miss count처럼 nominal limit가 0인 지표는 비율 headroom을 계산하지 않는다.
  별도 absolute rule과 margin 의미를 사전에 정의하고, 없으면 `UNDECIDED`로 둔다.

예를 들어 **계약 설명용 수치**로 latency 20 ms에 여유율 0.1이면 18 ms 이하,
throughput 30 frame/s에 여유율 0.1이면 33 frame/s 이상이 충족 조건이다. 실제 제품 목표가
아니다. Capacity는 동시 resident peak와 reserved 영역·여유의 예산이 있어야 평가할 수
있다. 2-GiB aperture에서 작은 kernel이 실행된 사실은 제품 capacity 충족 근거가 아니다.

## 3. 요구사항 목록

각 ID는 [Verification의 traceability matrix](verification.md#traceability)에서
design, implementation, test case로 연결된다. 아래 요구사항은 향후 campaign의 계약이며
현재 도구가 모두 구현했다는 뜻이 아니다.

| ID | 요구사항 | 수용 기준 |
|---|---|---|
| REQ-DSE-001 | 사양 결론은 version이 있는 target과 필수 scenario에 연결되어야 한다. | Comparator/statistic/sample/margin 규칙으로 판정; 누락 시 `UNDECIDED`; capacity는 resident 예산 필요 |
| REQ-DSE-002 | Hardware 비교 중 선언한 변화 외 workload 의미와 software를 고정해야 한다. | Source/ELF/compiler/flags/input/affinity/ROI 및 frame 재사용 정책 보존; output 검증 통과 |
| REQ-DSE-003 | 모든 실행의 effective configuration과 입력을 재현할 수 있어야 한다. | root/nested revision·dirty diff, binary/image/config/input hash, 명령, seed, resolved 값 보존 |
| REQ-DSE-004 | Cache 후보는 용량과 timing/resource 조건을 함께 기술해야 한다. | L2 per-core, L3 per-cluster, SLC total/per-home 구분; latency/assoc/bank/TBE/policy 변경 확인 |
| REQ-DSE-005 | CPU 수와 worker 수를 구분하고 CPU 공급 능력의 불확실성을 다뤄야 한다. | machine topology, active workers, affinity, O3 실행 확인; CPU IP 성능으로의 해석 한계 명시 |
| REQ-DSE-006 | Clock/NoC 후보는 실제 domain과 transport parameter에 적용되어야 한다. | instantiated clock·width·buffer·latency 및 변경 영향 확인; CDC/SerDes 미검증 조건은 제한 표시 |
| REQ-DSE-007 | DRAM 후보는 DMC, device geometry, timing, 주소 배치를 일관되게 정의해야 한다. | channel 수/폭, rate, rank/bank/row, refresh, scheduling, aperture 대조; unsupported 조합 거부 |
| REQ-DSE-008 | 성능은 측정 경로에 맞는 timing window와 byte/count 정의로 계산해야 한다. | CPU guest는 checksum·O3 전환·scenario별 준비 상태·exact ROI 확인; steady-state는 실제 warmup, cold-start는 정의한 cold 상태 근거 필요; native generator는 timing mode의 supply/measurement/drain 확인; Atomic/host time 사용 금지 |
| REQ-DSE-009 | CPU/cache/fabric/DRAM 병목은 관측 counter와 통제된 비교로 설명해야 한다. | 가설마다 반증 가능한 case와 counter 근거 기록; 다른 경로의 GB/s 차이를 fabric 손실로 단정하지 않음 |
| REQ-DSE-010 | 핵심 결과의 scenario별 안정성과 model 가정 민감도를 확인해야 한다. | Steady-state의 warmup/측정 길이를 별도 평가; cold-start는 정의한 초기 상태를 반복 재현; 사전 tolerance/sample 정책 충족; 불안정한 결론 보류 |
| REQ-DSE-011 | 단독 및 동시 workload의 성능을 구분해야 한다. | foreground 결과·release/start/finish와 background completed work 보존; sample 부족 시 tail 보장 금지 |
| REQ-DSE-012 | 외부 IP traffic는 연결 위치와 대표성 근거를 가져야 한다. | rate/burst/outstanding/주소/일관성/시간 패턴 기록; DRAM 직결 결과를 SLC 간섭으로 해석하지 않음 |
| REQ-DSE-013 | IP/물리설계 비용과 성능 evidence를 분리하고 함께 평가해야 한다. | area/power/clock/pin/package 근거 version 보존; 비용 누락 시 최저 비용·PPA 최적 결론 금지 |
| REQ-DSE-014 | 실행 상태, 수치 유효성, 제품 target 충족 판정을 분리해야 한다. | `FAIL`, `ERROR`, `TIMEOUT`, `SKIP`, `UNSUPPORTED`, `NOT_RUN` 보존; exit 0만으로 성능 PASS 금지 |
| REQ-DSE-015 | 기존 artifact와 snapshot을 안전하게 재사용하고 필요한 단계만 다시 실행해야 한다. | contract 검사 통과, 기존 결과 비덮어쓰기, 변경된 image/model에 맞는 snapshot, 영향 기반 build |
| REQ-DSE-016 | 후보 선정은 재현 가능한 decision record로 남겨야 한다. | target coverage, 사양, 성능, 비용, margin, 불확실성, 제외 이유, 미해결 항목 연결 |

## 4. 공통 지표 정의

| 지표 | 정의와 주의점 |
|---|---|
| ROI seconds | `(end_tick - begin_tick) / simFreq`; host elapsed와 별도 |
| Useful GB/s | 알고리즘이 정의한 useful bytes / ROI seconds / 10^9 |
| DRAM GB/s | 같은 ROI의 native DRAM read+write bytes / ROI seconds / 10^9 |
| Frame throughput | 완료한 유효 frame 수 / 정의된 simulated interval; single-frame 역수와 구분 |
| Slowdown | 같은 입력·clock·ROI 정의에서 동시 실행 latency / 단독 latency |
| Latency headroom | `1 - observed_latency / limit`; limit가 확정된 경우만 계산 |
| Throughput headroom | `observed_throughput / target - 1`; target가 확정된 경우만 계산 |

Read/copy/triad는 array당 64 MiB 조건에서 총 working set이 각각 64/128/192 MiB다.
Write allocation, writeback, page-table와 OS traffic 때문에 useful bytes와 DRAM bytes는
같지 않을 수 있다. Channel 평균의 단순 평균과 request-weighted 평균을 구분한다.
Clock이 다른 후보는 각 domain의 cycle과 ns를 함께 기록하며 하나의 CPU cycle로
모든 component latency를 표현하지 않는다.

## 5. 결론의 등급

| Decision label | 필요한 evidence |
|---|---|
| `EXPLORATORY` | 입력과 가정을 기록한 상대 비교; 미정 target 또는 미검증 대표성 존재 |
| `CONDITIONAL` | 명시한 target/scenario는 평가했지만 model/traffic/cost 근거에 중요한 제한 존재 |
| `MODEL_FEASIBLE` | 정의한 target·여유·robustness 조건을 모델 범위에서 충족하고 필수 evidence 완비 |
| `MODEL_INFEASIBLE` | 유효한 측정으로 최소 하나의 필수 target가 `DOES_NOT_MEET`; 해당 model/scenario에서 후보 제외 근거 |
| `UNDECIDED` | target/evidence 누락, 후보 순위 불안정, 비용/구현 가능성 미확인 등으로 해당 결정 보류 |

필수 scenario별 target 결과를 먼저 보존한다. 하나라도 유효한 `DOES_NOT_MEET`가 있으면
그 범위의 candidate는 `MODEL_INFEASIBLE`이며, 아직 측정하지 않은 target까지 실패한
것은 아니다. 알려진 불충족이 없더라도 필수 target가 `UNDECIDED`이면 충족 결론은 보류한다.
모든 필수 target가 `MEETS`인 경우에만 evidence/robustness 수준에 따라 `CONDITIONAL`
또는 `MODEL_FEASIBLE`을 검토한다. 제품 판정 없이 수행하는 민감도 보고서는
`EXPLORATORY`이며 target 충족란을 대신하지 않는다. 비용 누락 시 성능의 target 결과는
유지할 수 있지만 최소 비용안 선정은 별도 `UNDECIDED`다.

`MODEL_FEASIBLE`은 silicon 승인 상태가 아니다. 한정된 scenario에서의 관측 maximum을
WCET로 승격하지 않는다. 모델 오차에 관한 보편적인 ±% 수치는 사용하지 않는다.

## 6. 근거

- [현재 Apollo 지원 경계](../capabilities.md), [기존 측정 계약](../../benchmark-guide.md).
- [gem5 architecture 연구 기능](https://www.gem5.org/about/): gem5 일반 기능이며 Apollo의 통합 검증과 구분한다.
- [Memory component validation 연구](https://arch.cs.ucdavis.edu/memory/2022/12/13/validating-memory.html): component별 validation 필요성의 참고이며 해당 연구의 오차를 Apollo 오차로 전용하지 않는다.

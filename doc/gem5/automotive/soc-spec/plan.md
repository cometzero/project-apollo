# Apollo gem5 SoC 사양 탐색 — Plan

작성일: **2026-10-28**. 상태: **계획 고정 / exploratory campaign 진행 중**.
[현재 진행 기록](campaign-20261028.md). 제품 목표는 미정으로 진행한다는 사용자 확인을 받았다.
[Requirement](requirement.md) → **Plan** → [Design](design.md) →
[Implementation](implementation.md) → [Verification](verification.md).

## 2026-10-30 후속 계획 보강

아래 P0–P6와 진행 중인 campaign의 고정 contract는 유지한다. 후속 campaign은 기존 evidence 정리 → Orin 계측/reference 확인 → paired baseline screening → 최대 2개 후보의 uncertainty/interaction 검증 → 독립 workload/동시 부하 → decision record 순서로 진행한다. 시작 전에 run 수·host 시간 예산과 중단 조건을 숫자로 고정한다. 기존 결과의 실패 기준을 소급 완화하지 않는다.
세부 근거와 실행 정책은 [추가 논문 검토](literature-methodology-20261030.md)를 따른다.

## 1. 추진 원칙

목표는 요구 성능을 만족하는 hardware 사양 조합을 좁히는 것이다. Microbenchmark로
모델을 점검하고, 대표 kernel과 동시 workload에서 후보를 평가한 뒤 구현 비용과
결합한다. Hardware sweep 중 algorithm/compiler 최적화를 섞지 않는다. Software A/B가
필요하면 별도 experiment ID로 분리하고 새 software baseline에서 관련 후보를 재평가한다.

1차 완료 단위는 **P0–P2: 재사용 가능한 baseline, 신뢰할 수 있는 ROI, memory 병목 보고서**다.
다음 완료 단위는 **P3–P4: 대표 kernel과 사양 shortlist**이며, 최종은 **P5–P6: 동시
workload·불확실성·비용을 포함한 decision record**다. 이번 문서 작성으로 이 단계들을
실행 완료로 표시하지 않는다.

## 2. 단계와 종료 조건

| 단계 | 작업 | 선행 조건 | 산출물과 종료 조건 |
|---|---|---|---|
| P0 | Target/scenario·resident memory 예산 정리, 기존 evidence inventory | 없음 | Comparator/statistic/margin 및 TBD 식별; 재사용/재집계/재실행 목록; 탐색과 제품 판정 범위 구분 |
| P1 | Baseline provenance, config/clock mapping, checkpoint와 ROI 검증 | P0 | 입력 contract와 effective 값 일치; 정상 restore→O3→ROI; pilot 비용 기록 |
| P2 | 기존 cache/read/copy/triad 분석, 누락 scaling·interleave·backend case 실행 | P1 | 주요 병목 가설의 지지/기각/미해결 근거; warmup/측정 길이 수렴을 별도 확인 |
| P3 | 고정 image preprocessing kernel과 정확도/ROI fixture 구성 | P0, P1 | Guest output 검증; image 내 executable 확인; kernel-only 측정 성립 |
| P4 | 구현 가능한 cache/CPU/NoC/DRAM 후보 screening 및 interaction 비교 | P2, P3 | 잠정 사양 후보 shortlist; 변경 parameter와 효과·불확실성 연결 |
| P5 | Foreground/background, cluster 배치, 필요 시 외부 IP traffic envelope | P4 | 단독 대비 slowdown과 completed traffic; sample 수와 대표성의 한계 기록 |
| P6 | Robustness, target margin, 외부 비용 자료 결합 | P4, P5 | 최소 충족안/여유안/제외안 또는 `UNDECIDED`와 부족 근거 |

P0에서 target가 미정이어도 P1–P4의 탐색은 가능하다. 단, 미정 target를 만족했다고
판정할 수 없다. P3의 source/fixture 준비는 P2 장시간 simulation과 병행할 수 있지만,
동일 build input 변경·BitBake 실행은 직렬화한다.

## 3. 최초 측정 범위

Baseline campaign은 **16-core machine, 2 GiB RAM, 16 × x16 channels,
8533 MT/s proxy, 64-B stripe, 고정 CPU/Ruby/mesh clock**으로 시작한다. 기본 launcher는
4 CPUs이므로 실행에서 `--cpus 16`을 명시한다. Effective profile은 실제 run에서 보존한다.

| 순서 | 조건 | 목적과 재사용 규칙 |
|---|---|---|
| A | 기존 cache/16-core/interleave/Orin-informed 결과 재집계 | 원본 hash와 exact ROI를 확인; 다른 revision을 한 campaign 결과처럼 합치지 않음 |
| B | 64 MiB read, 16 workers, measured 2 passes | 현재 baseline pilot; compatibility 및 host 비용 확인 |
| C | 동일 machine에서 workers 1/4/8/16 | Fixed-total-work scaling; CPU 공급량과 cache/cluster 배치 효과를 함께 관찰; B와 중복 조건 재사용 |
| D | 16 workers, stripe 64/512/1024 B | 총 6개의 고유 read 조건(C+D); stripe별 matching snapshot |
| E | Copy/triad, array당 64 MiB, 16 workers | 기존 유효 결과 우선; 비교 가능한 baseline이 없을 때 추가 |
| F | 핵심 조건의 warmup 길이 비교 후 measured 2→4 passes, 필요하면 8 | Warmup 고정 상태의 측정 길이 수렴과 startup 영향을 구분; 아래 tolerance 적용 |
| G | Native direct/fanout/single diagnostic 중 가설에 필요한 case | Linux와 timing/geometry fingerprint 비교 후 경로별 별도 해석 |

원본 조건을 시간 절약 목적으로 임의 축소하지 않는다. 위 2-pass는 이번 계획의 명시적
baseline이며 과거 1-pass 결과는 별도 조건으로 보존한다. 기존 read/copy/triad의
instruction mix 차이도 함께 분석한다. Six read cases를 수행했다고 CPU/NoC/DRAM의
모든 상호작용을 검증한 것은 아니다.

총 64 MiB를 분할하면 worker당 범위는 1/4/8/16 workers에서 각각 64/16/8/4 MiB다.
기본 affinity `0..workers-1`은 사용하는 cluster와 cache도 바꾸므로 순수 core 공급량만의
효과라고 해석하지 않는다. 실제 cache miss와 DRAM bytes로 설명하고 원인 분리가 필요하면
worker당 working set 고정 또는 cluster 배치 비교를 별도 case로 추가한다.

## 4. 사양 탐색 순서

1. 공급사에서 구현 가능하다고 확인한 선택지와 단순 proxy 실험 선택지를 구분한다.
   Cache의 per-core/per-cluster/total 단위와 clock domain을 명확히 한다.
2. L2, L3, SLC, CPU clock/core count, NoC clock/width, DRAM channel별로 먼저
   한 항목씩 바꾸어 workload의 민감도와 saturation을 확인한다.
3. 단독 효과 크기로 조합을 걸러내기 전에 `CPU clock×NoC clock`, `SLC×DRAM`처럼
   architecture상 결합된 항목의 baseline/low/high 중 작은 pair 실험을 사전 지정한다.
   단독 효과가 작아도 함께 바꿀 때 효과가 생길 수 있다. 이후 관측된 병목과 영향도에 따라
   `L2×L3` 등 필요한 조합을 추가한다. 효과가 없다는 결론도 현재 workload/범위에 한정한다.
4. DRAM rate/x32/다른 capacity와 현재 미지원 CPU topology는 필요성이 확인된 경우에만
   [Implementation](implementation.md)의 선행 변경·검증을 수행한다.
5. 잠정 후보 2–3개를 대표 scenario와 동시 부하에서 상세 비교한다. 모든 parameter의
   Cartesian product를 생성하지 않는다. Shortlist 밖 후보의 제외 이유도 보존한다.
   P5에서 target 미충족, 병목 이동 또는 순위 역전이 관찰되면 P4로 돌아가 제외했던
   SLC/NoC/DRAM 후보 등을 재진입시켜 평가한다. 단독 실행만으로 최종 제외하지 않는다.

P3의 첫 workload는 CPU image preprocessing 한 개다. 기존 구현을 먼저 조사해 source와
license를 고정하고 color conversion 또는 normalization 중 정확도 검사가 명확한 호출을
선택한다. 실제 입력 크기는 P0에서 정한다. Synthetic image라면 그 사실을 표시한다.
Frame 재사용/교체, buffer pool과 arrival/queue/drop 정책을 고정하고, 같은 frame만 반복해
얻은 warm-cache 결과를 실제 연속 frame 처리 성능으로 일반화하지 않는다. 다른 representative
scenario의 coverage가 없으면 전체 SoC 사양 결론은 그 범위만큼 제한한다.
기능 요구가 point-cloud 중심이면 근거를 남겨 kernel 선택을 바꾸되, 결과를 합치지 않는다.

## 5. 실행 비용과 측정 정책

Pilot에서 boot/restore, Atomic 초기화, O3 warmup, ROI, 종료의 host 시간을 가능한
로그 경계로 분리한다. 경계가 없으면 추정값과 근거를 표시하고 정확한 단계별 측정으로
포장하지 않는다. 남은 비용은 고정 overhead와 관측된 작업량별 속도로 범위를 추정하며
cache/queue 상태가 달라지면 갱신한다. 사전에 수 시간·수일 완료를 보장하지 않는다.

- 초기에는 simulation 한 개로 resource 사용량을 확인한다. 병렬 수는 RSS/CPU 여유로
  정하며 host elapsed를 simulated 성능 지표로 쓰지 않는다.
- 측정 길이 비교 전에 핵심 후보에서 measured passes를 고정하고 warmup 1→2 passes 등
  사전 정의한 비교로 startup 영향을 확인한다. Steady-state 의도인데 warmup 제어가 없거나
  안정성을 확인하지 못하면 해당 결과는 exploratory다. Cold-start가 target이면 cold 상태를
  별도 정의하고 warmup을 수행한 결과와 분리한다. 기존 fixed-warmup workload가 cold-start를
  지원한다고 가정하지 않으며 필요한 fixture/collector 확장을 선행한다. Cold-start sample은
  매번 같은 초기 상태를 재현하고 반복 pass로 cache를 데운 결과와 합치지 않는다.
- 측정 길이 수렴의 **초기 제안 기준**은 2→4 passes에서 정규화된 주요 지표 변화 ≤5%다.
  대상은 useful GB/s, dependent-load ns/load, DRAM bytes/useful bytes 중 해당 workload에
  적용되는 지표다. Raw bytes나 총 ROI 시간을 그대로 비교하지 않는다. `M2 > 0`일 때
  `abs(M4 - M2) / abs(M2) <= 0.05`로 판정한다. 기준값이 0이면 상대 변화는 N/A이며,
  별도 사전 절대 tolerance가 없으면 수렴 판정을 보류한다. 이는 hardware 정확도나 제품
  허용 오차가 아니다. Campaign 시작 시 기준과 변경 이유를 기록하며 결과를 본 뒤
  합격하도록 기준을 완화하지 않는다.
- 5%를 넘으면 8 passes 또는 warmup 원인을 조사한다. 고정된 warmup 1 pass가 부족하면
  workload 옵션을 추가하고 관련 image/snapshot을 갱신한다.
- timeout은 실행 실패 원인 분석에 사용한다. Timeout 결과를 낮은 성능값이나 정상
  sample로 처리하지 않는다. 동일 실패를 입력 변경 없이 반복 실행하지 않는다.

## 6. 산출물과 작업 소유권

Tracked 문서는 이 디렉터리와 기존 [실험 가이드](../experiments.md)에 둔다. Generated
evidence는 새 `build/qbox-apollo-qvp/gem5/soc-spec-<timestamp>/` 아래에 둔다.
Campaign/decision artifact 구조는 [Design](design.md#artifacts)을 따른다.

Root는 launcher/collector/문서를, gem5 submodule은 model/parameter/native workload를,
owned Yocto layer는 package/image를 소유한다. 다른 repository의 미관련 변경을 건드리지
않으며 이 계획은 commit/push를 포함하지 않는다.

## 7. 위험 발생 시 분기

| 관찰 | 다음 행동 |
|---|---|
| Snapshot contract 불일치 | 보존된 matching inputs 확인 또는 fresh snapshot; metadata 수정으로 우회 금지 |
| Config 변경이 기대와 다르게 전파됨 | 성능 sweep 중단, source→SimObject 경로 수정 및 directed test |
| Counter 부족/의미 불명확 | 기존 stats를 확인하고 필요한 counter만 추가; 큰 trace는 한정 ROI에서 사용 |
| CPU 공급량 가정에 따라 DRAM 후보 순위 역전 | CPU model uncertainty를 결과에 포함; target IP 근거 보강 |
| 외부 IP traffic 근거 없음 | AP-only 또는 synthetic 조건부 결과로 제한 |
| NPU-enabled traffic 후보에서 checkpoint 필요 | 현재 save/restore가 금지됨; fresh boot 또는 별도 serialization/drain/restore 지원·검증 계획 |
| PPA/제품 target 누락 | 성능 비교는 보고하되 최종 사양 선정은 `UNDECIDED` |
| 동시 resident peak/reserved memory 근거 없음 | Bandwidth 후보 비교는 계속하되 제품 DRAM capacity 충족은 `UNDECIDED` |

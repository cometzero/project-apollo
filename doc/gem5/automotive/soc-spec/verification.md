# Apollo gem5 SoC 사양 탐색 — Verification

작성일: **2026-10-28**. 상태: **검증 명세 / 새 campaign 진행 중**.
[Requirement](requirement.md) → [Plan](plan.md) → [Design](design.md) →
[Implementation](implementation.md) → **Verification**.

## 2026-10-30 검증 해석 보강

기존 gate와 traceability는 유지한다. 후속 검증에서는 calibration/validation workload 분리, 같은 uncertainty 조건의 baseline/candidate pairing, rank reversal, 축소 workload의 footprint 변화, 사전 실행 예산을 확인한다. Counter 불안정과 primary metric 안정성은 사전에 정한 별도 판단으로 보고하며 미입증 steady-state를 PASS로 취급하지 않는다. 문서 보강은 runtime 검증 통과가 아니다.
세부 근거와 실행 정책은 [추가 논문 검토](literature-methodology-20261030.md)를 따른다.

## 1. Evidence 수준과 상태

| 수준 | 확인하는 것 | 이 수준만으로 주장할 수 없는 것 |
|---|---|---|
| Documentation/static | Source 경로, 링크, 요구사항 추적, 구현/계획 구분 | Build/boot/성능 PASS |
| Host unit/fixture | Parameter 검증, parser, identity, 실패 처리 | Native timing, guest 동작 |
| Build/package | 컴파일, ABI, dependency, image 포함 | Runtime correctness |
| Directed model | 특정 cache/clock/link/DRAM 입력에 대한 동작 | 전체 application timing/실물 일치 |
| Guest runtime/measurement | Output, O3 ROI, counter, scenario 실행 | 대상 silicon 성능 보증 |
| External correlation | 별도 IP/RTL/hardware 근거와 명시한 범위의 비교 | 다른 CPU/IP 또는 미검증 scenario로 일반화 |

Campaign record에서 실행 상태는 `PASS/FAIL/ERROR/TIMEOUT/SKIP/UNSUPPORTED/NOT_RUN`,
수치 유효성은 `VALID/INVALID/NOT_EVALUATED`, target 결과는
`MEETS/DOES_NOT_MEET/UNDECIDED`로 분리한다. 이는 campaign report의 계약이며 기존
launcher의 status 문자열을 변경 완료했다는 뜻은 아니다. 원래 `result.json`의 status도
그대로 보존하고 명시적으로 매핑한다. `SKIP`에는 사유와 target coverage 손실을 남긴다.

Target 판정은 [Requirement의 comparator/statistic/margin 규칙](requirement.md#target-rules)을
사용한다. 실행 `PASS`여도 sample 정책을 충족하지 못하면 target는 `UNDECIDED`다.
유효한 필수 target 하나가 `DOES_NOT_MEET`이면 그 model/scenario의 candidate는
`MODEL_INFEASIBLE`로 기록하고, 나머지 target의 미측정 상태를 숨기지 않는다.

## 2. 검증 case

아래 Expected 결과는 수용 기준이며 관측 결과가 아니다. 현재 완료한 검사와 남은
case는 [진행 기록](campaign-20261028.md)에 연결한다. Documentation 검사는 마지막 절에
별도로 기록한다. 일부 fixture 통과를 해당 VER ID 전체 완료로 해석하지 않는다.

| ID | 입력·절차 | Expected result / evidence |
|---|---|---|
| VER-DSE-001 | Target/scenario, comparator/statistic/margin 경계값·잘못된 단위·표본 부족·T=0 정책 검사 | 동일 경계값 충족; 유효한 값이 comparator를 만족하지 못하면 `DOES_NOT_MEET`; 누락/불일치/표본 부족은 `UNDECIDED`; 제품 용량은 resident 예산 필요 |
| VER-DSE-002 | Workload/input/ELF/compiler identity를 고정하고 output oracle로 host/guest 검사 | 유효 output; input hash 또는 tolerance 위반 시 해당 measurement 무효 |
| VER-DSE-003 | Host port/run 경로만 바꾼 config와 clock/defaults/custom module/image 변경 config 비교; NPU-enabled checkpoint 요청 | Raw hash 보존·허용 필드만 정규화한 identity 재현; 실제 parameter 변경/stale snapshot 검출; 현재 NPU checkpoint 거부 |
| VER-DSE-004 | L2/L3/SLC 후보를 생성하고 size/assoc/bank/TBE/latency/DTB 대조 | 요청값 적용; SLC total/per-home 또는 cache geometry 불일치 거부 |
| VER-DSE-005 | 16-core에서 workers 1/4/8/16 및 지원 machine topology 실행 | Affinity/O3 실행, worker당 working set·cluster·cache 이용 확인; worker scaling을 순수 core 수 효과로 보고하지 않음 |
| VER-DSE-006 | CPU/Ruby/mesh clock을 각각 변경해 instantiated domain과 directed timing 확인 | 의도한 domain 변화, 간접 변화 기록; CDC/width/framing 미검증 조건을 명시 |
| VER-DSE-007 | DRAM 후보의 width/rate/geometry/timing·주소 trace·coverage와 제품 resident memory 예산 확인 | 일관된 구성만 허용; unsupported 조합 거부; 작은 aperture 실행만으로 제품 capacity 충족 판정 금지 |
| VER-DSE-008 | Native traffic의 supply 종료·drain 및 bytes accounting 검사 | Generated/completed/serviced 차이를 설명; Linux 경로와 backend 성능을 분리 |
| VER-DSE-009 | 정상 restore→O3→scenario 준비→ROI, checksum/marker 누락 및 cold 상태 미입증 fixture | Steady-state warmup 또는 cold-start 초기 상태와 exact stats 확인; 누락/중복/순서 오류·timeout은 무효 |
| VER-DSE-010 | ROI 중간 dump/exit dump, counter 누락/NaN, byte 정의 불일치 주입 | 중복 합산·0 대체 방지; application별 expected coverage 적용 |
| VER-DSE-011 | Steady-state에서 warmup/측정 길이를 각각 고정한 비교; cold-start는 초기 상태 재현 반복; 0 기준값 fixture 포함 | Warmup/측정 길이 검증 분리; cold sample에 hot 반복 pass 혼입 금지; 정규화된 지표와 초기 상태 근거 확인 |
| VER-DSE-012 | 병목 가설별 한 변수 변경과 사전 지정 coupled pair 수행 | 단독 효과가 작은 항목의 동시 변경 효과도 검사; counter/성능 변화로 지지·기각·미해결 구분 |
| VER-DSE-013 | Foreground 단독/동시, frame 재사용/교체, 같은/다른 cluster 배치 실행 | Output, 단일 ROI, 공통 timebase·arrival/queue/drop 정책, completed work 확인; 순위/병목 변화 시 제외 후보 재평가 |
| VER-DSE-014 | 근거 있는 burst/rate/phase와 연결 위치로 외부 IP traffic 실행 | 경로/traffic/maintenance 확인; DRAM 직결을 SLC 실험으로 분류하지 않음 |
| VER-DSE-015 | CPU 공급량/cache latency/NoC/DMC 불확실성 범위에서 shortlist 재평가 | 순위·headroom 변화 기록; 불안정한 후보 결정은 조건부/보류 |
| VER-DSE-016 | PPA 자료와 target를 연결하고 비용 근거/목적함수를 제거한 report 생성 | 자료 조건·version 표시; 누락 상태에서 단일 최소 비용/PPA 최적 판정 금지 |
| VER-DSE-017 | 같은 evidence로 report 재생성, 유효 불충족·invalid·미측정 target가 섞인 case 포함 | 모든 필수 target/candidate coverage와 제외 이유 보존; `MODEL_INFEASIBLE`/`UNDECIDED`/조건부 충족 구분 |

### Directed test의 해석

Cache size가 커지면 모든 workload가 빨라진다거나 clock을 두 배로 하면 성능이 두 배라는
단조성 검사를 합격 기준으로 만들지 않는다. Controlled cache-hit 접근, request 수,
link packet/byte, 주소 범위처럼 기대 동작이 정의된 fixture로 설정 적용을 확인한다.
Application 성능은 별도 관찰한다. Stall·latency counter의 clock 단위도 대조한다.

Clock domain 간 비율 변경은 deadlock/ordering/동일시간 event 동작과 latency를 함께
확인한다. RTL과 동일한 CDC 구현을 검증하지 않았다면 그 fidelity gap을 남긴다.
Cache/NoC/DRAM interaction 비교에서는 collateral parameter 변경을 반드시 기록한다.

### ROI와 수렴

Steady-state의 warmup은 실제 loop 실행이어야 한다. `gem5-control run`의 phase 이름만으로
warmup 완료를 판정하지 않는다. Cold-start는 O3 전환 후 정의한 cold 상태의 근거와 ROI를
검증하며 warmup을 생략했다는 사실만으로 인정하지 않는다. ROI가 끝나기 전 worker 실패나 timeout이면 부분 counter를
완료 성능으로 집계하지 않는다. Copy/triad의 cache dirty data와 drain 범위도 명시한다.

Steady-state의 warmup 길이는 measured length와 별도로 바꾸어 확인한다. Measured passes를 늘려 비슷한
평균이 나왔다는 사실만으로 warmup 충분성을 인정하지 않는다. 동일 frame/buffer 반복과
실제 frame 교체의 cache residency를 구분하고 required scenario의 누락을 coverage에 남긴다.

Plan의 5%는 useful GB/s, ns/load, DRAM bytes/useful bytes처럼 정규화된 지표의 수렴
제안이며 hardware 정확도 수치가 아니다. Pass 증가에 따른 raw bytes 증가에는 적용하지
않는다. 기준값이 양수일 때 `abs(M4 - M2) / abs(M2)`를 사용하고, 0일 때는 N/A와
사전에 정한 absolute tolerance 정책을 확인한다. 정책이 없으면 수렴 판정을 보류한다.
Tolerance를 만족하더라도 반복된 deterministic seed만으로 실제 workload variance를
설명하지 않는다. Input, page placement, release phase 등의 변동 조건을 별도 관리한다.
Tail 지표는 sample count, quantile 방법, confidence 근거가 있어야 하며 부족하면
sample 목록/median/observed maximum만 보고한다. Observed maximum은 WCET가 아니다.

<a id="traceability"></a>
## 3. 요구사항 추적

Design/Implementation ID의 정의는 각각 [Design](design.md),
[Implementation](implementation.md)에 있다. 모든 REQ ID는 최소 한 개의 검증 case에
연결된다. 다수 요구사항에 걸친 case는 evidence 하나로 연결하되 판정을 분리한다.
아래 단계는 확인할 시점이며 최초 통과만으로 요구사항 전체를 완료 처리하지 않는다.
Identity/config/ROI/output 규칙은 후속 candidate와 run마다 적용하고 최종 완료는 해당
campaign의 모든 필수 case와 연결 검증을 마친 뒤 판단한다.

| Requirement | Design | Implementation | Verification | 확인 단계 |
|---|---|---|---|---|
| REQ-DSE-001 | DES-DSE-01, DES-DSE-06 | IMP-DSE-01, IMP-DSE-08 | VER-DSE-001, VER-DSE-017 | P0, P6 |
| REQ-DSE-002 | DES-DSE-01, DES-DSE-04 | IMP-DSE-04 | VER-DSE-002 | P3 |
| REQ-DSE-003 | DES-DSE-01, DES-DSE-07 | IMP-DSE-01 | VER-DSE-003 | P1 |
| REQ-DSE-004 | DES-DSE-02 | IMP-DSE-02 | VER-DSE-004 | P4 |
| REQ-DSE-005 | DES-DSE-02, DES-DSE-04 | IMP-DSE-02, IMP-DSE-05, IMP-DSE-06 | VER-DSE-005, VER-DSE-015 | P2, P4, P5, P6 |
| REQ-DSE-006 | DES-DSE-02 | IMP-DSE-02 | VER-DSE-006 | P4 |
| REQ-DSE-007 | DES-DSE-02 | IMP-DSE-06 | VER-DSE-007, VER-DSE-008 | P4 |
| REQ-DSE-008 | DES-DSE-03, DES-DSE-05 | IMP-DSE-03, IMP-DSE-04 | VER-DSE-008, VER-DSE-009, VER-DSE-010 | P1, P2, P3 |
| REQ-DSE-009 | DES-DSE-05 | IMP-DSE-03 | VER-DSE-008, VER-DSE-012 | P2 |
| REQ-DSE-010 | DES-DSE-05, DES-DSE-06 | IMP-DSE-03, IMP-DSE-08 | VER-DSE-011, VER-DSE-015 | P2, P6 |
| REQ-DSE-011 | DES-DSE-04 | IMP-DSE-05 | VER-DSE-013 | P5 |
| REQ-DSE-012 | DES-DSE-04 | IMP-DSE-07 | VER-DSE-014 | P5 |
| REQ-DSE-013 | DES-DSE-06 | IMP-DSE-08 | VER-DSE-016 | P6 |
| REQ-DSE-014 | DES-DSE-05, DES-DSE-07 | IMP-DSE-03, IMP-DSE-08 | VER-DSE-009, VER-DSE-010, VER-DSE-017 | P1, P6 |
| REQ-DSE-015 | DES-DSE-03, DES-DSE-07 | IMP-DSE-01 | VER-DSE-003, VER-DSE-009 | P1 |
| REQ-DSE-016 | DES-DSE-06, DES-DSE-07 | IMP-DSE-08 | VER-DSE-016, VER-DSE-017 | P6 |

## 4. 기존 검증 도구의 재사용

아래는 **구현 변경 시 선택할 기존 검사 예시**다. 이번 문서 작성에서는 실행하지 않았다.
Repository root 기준이며 unrelated suite 전체를 선행 필수로 돌리지 않는다.

```sh
python3 -m unittest discover -s scripts/gem5 -p 'test_run_linux.py'
python3 -m unittest discover -s scripts/gem5 -p 'test_benchmark.py'
python3 hsoc-stack/tools/gem5/tests/zena_cmn/test_parameters.py
```

그 외 기존 `test_address_map.py`, `test_roi_control.py`, `test_checkpoint.py`,
`test_backend_drain.py`, `test_memory_convergence.py`는 gem5의
`tests/zena_cmn/`에 있다. 해당 source와 실행 의존성을 확인해 변경된 consumer에 맞게
선택한다. Native directed 시험과 실제 Linux restore/O3 시험을 host unittest로 대체하지 않는다.
Effective configuration은 기존 `scripts/zena_cmn/verify_config.py`와
`tests/zena_cmn/test_verify_config.py`를 재사용한다. 해당 run과 matching `--gem5`를
지정하고 과거 run의 결과를 보존하도록 별도 `--output` 경로를 사용한다. Canonical identity
검사에는 port/path 변화만 무시되고 실제 timing/config/input 변화는 검출되는 음성 case를 둔다.

Fresh build/boot 절차는 [Build guide](../../build-guide.md),
[Run guide](../../run-guide.md), [기존 실험 명령](../experiments.md)을 따른다.
사양 후보마다 snapshot provenance를 검사하며 compatibility 우회 명령을 제공하지 않는다.
Orin 검증은 선택한 workload의 정확도/계측/경향 확인으로 범위를 한정한다.

## 5. Evidence 판정 record

각 test record에 case ID, 연결 REQ, command, inputs/config hash, 예상 결과, 실제 결과,
상태, evidence path, 미해결 제한을 둔다. Host seconds와 simulated seconds를 분리한다.
같은 counter를 여러 ROI에 중복 집계하거나 실패 case를 comparison에서 숨기지 않는다.

| 판정 시점 | 필수 확인 |
|---|---|
| P1 종료 | Current input/contract, effective config, 실제 restore/O3/ROI와 output |
| P2 종료 | Counter 의미와 path, 가설 검증, warmup/측정 길이 수렴 분리, 누락 case 목록 |
| P4 종료 | Product 가능 옵션과 proxy 옵션 구분, 대표 kernel correctness, 후보 interaction |
| P6 종료 | Target/comparator/statistic/sample/margin 확정, 필수 scenario·resident 예산, robustness, 비용 목적/근거, 추적성 |

필수 input가 없는 P6에서는 `UNDECIDED` 보고서가 올바른 결과다. 결과를 만들어내기 위해
임의 target를 채우거나 모델을 목표 점수에 맞춰 tuning하지 않는다.

## 6. 문서 작성 및 review의 확인 범위

최초 작성 시 5개 문서와 상위 index 2개의 local link 108개, table 21개, REQ 16개,
DES 7개, IMP 8개, VER 17개 정의와 matrix coverage, fence/whitespace 정적 검사가
통과했다. 이는 최초 작성본에 대한 기록이며 변경 후 개수와 hash는 별도 review 결과를 따른다.

Generated 정적 검사 기록은
`build/qbox-apollo-qvp/gem5/soc-spec-docs-20261028/validation.json`이다.
내용 review에서 native window/O3 ROI 구분, 동시 부하에 따른 후보 재진입,
정규화된 수렴 지표와 0 분모 정책을 보완했다.

후속 review에서는 target/margin 및 불충족 판정, resident capacity 예산, coupled pair
선정, fixed-total-work scaling, warmup/frame 대표성, NPU checkpoint 제약,
canonical identity와 기존 config verifier 재사용을 수정했다. Review 전 문서와 수정 내역,
최종 정적 검사·문서 hash는
`build/qbox-apollo-qvp/gem5/soc-spec-review-20261028T005531Z/`에 보존한다.
현재 구현의 설명은 source inspection 근거이며 위 VER case의 실행 evidence가 아니다.

**최초 문서 작성/review 시점**에는 host tests, Yocto build, native simulation,
Linux boot/restore, Orin 실행, 제품 판정이 모두 `NOT_RUN`이었다. 후속 구현의 evidence는
진행 기록에서 별도로 관리하며 과거 `RECORDED_PASS`의 상태를 변경하지 않는다.

2026-10-31 실제 적용과 host/native 결과는 [P5/P6 검증 보강](verification-20261031.md)을 따른다. P5 guest queue와 전체 completion audit은 별도다.

### P5 background 조건별 수렴 입력 준비 (2026-10-31)

`V/p5-bg-convergence/`에 CPU1 및 CPU4 background 각각의 warmup2/frames4와
warmup4/frames8 endpoint 4개를 별도 campaign으로 준비했다. 기준은 완료된
각 배치의 warmup4/frames4 raw 결과이며, solo 수렴을 background 수렴으로
대체하지 않는다. `preparation-check.json`은 기존 anchor 2개의 fresh validity,
새 command의 변경 범위·shell syntax·typed workload 옵션·기록된 snapshot 필드·
frozen input hash를 검사한 static PASS다. 새 restore/ROI/수렴 결과는 **NOT_RUN**이다.

각 endpoint는 최대 1 run/7,800 host seconds, command timeout 7,200 seconds이며
전체 최대 4 runs/31,200 host seconds, global native 동시 상한 2를 유지한다.
각 배치의 warmup2→4에서 기존 세 normalized metric과 arithmetic mean이 모두
5% 기준을 통과한 경우에만 해당 frames4→8을 실행한다. 실패 시 원본 결과와
미실행 endpoint를 보존하며 tolerance를 완화하지 않는다. 상세 조건은
`entry-policy.json`에 기록했다. Run-to-run repeatability와 제품 적합성은
각각 `NOT_EVALUATED`, `UNDECIDED`다.

### Host 재부팅 후 중단 case 복구 (2026-11-01)

기존 `apollo-gem5-p5-frames8-20261031` 및 `apollo-gem5-p5-nominees-20261031`
service는 00:07:32–33에 중지됐으며, 재개 시 host uptime과 process 부재를 확인했다.
Frames8 및 channels8 BG1은 ROI 종료 기록이 있지만 최종 `result.json`과
verifier/정상 종료 기록이 없어 **INTERRUPTED_NO_TERMINAL_RESULT**로 보존한다.
Systemd의 종료 상태만으로 benchmark PASS를 부여하지 않는다.

`V/recovery-20261101/recovery-review.json`과 `prior-services.log`에 근거를 저장했다.
Source/input pins를 다시 확인하고 기존 command에서 output 경로만 변경했다.
완료된 channels8 solo는 fresh raw validity를 확인해 재사용한다. Frames8 1개와
nominees 잔여 5개(BG1/BG4 및 mesh1GHz solo/BG1/BG4)는 새 case ID·출력 경로로
실행한다. 각 command 7,200초, policy budget은 각각 7,800초/36,000초이며
동시 native 상한은 2다. 실패 시 중단하고 자동 retry하지 않는다.

새 service는 `apollo-gem5-frames8-recovery-20261101`과
`apollo-gem5-nominees-recovery-20261101`이다. 시작과 실제 native process를 확인했지만
새 guest-runtime·수렴 결과는 아직 **RUNNING / NOT_EVALUATED**다. SSH 연결 종료에는
user service와 `Linger=yes`로 독립되지만 host reboot 후 중간 O3 실행을 이어가는 기능은 없다.


### Frames8 recovery 완료 및 held-out 시작 (2026-11-01)

`verification-20261031/recovery-20261101/frames8/length-completed-review.json`에서
launch/config verification PASS 및 frames 4→8의 네 가지 5% convergence gate PASS를 확인했다.
Mean kernel time은 2425984→2421236 ns/frame (−0.196%), median frame latency는
2412048→2412528 ns (+0.020%), FPS는 412.1787→412.9830 (+0.195%),
DRAM/useful ratio는 1.643375→1.6202413 (−1.408%)다. 기존 warmup 2→4 PASS와
함께 해당 baseline solo 조건의 안정성 근거이며, 다른 workload 또는 silicon 검증으로 확대하지 않는다.

Orin SSH 접속을 `agx-orin-devkit-001`에서 확인했다. 완료된 Orin 측정은 재실행하지 않았다.
Held-out pool1의 frozen input 검사를 `heldout-pool1/prelaunch-20261101.json`에 PASS로
기록하고 `apollo-gem5-heldout-pool1-20261101.service`로 1회 측정을 시작했다
(invocation `a0c868bc6a664f19bc2a2658ce5e089a`). 결과는 아직 RUNNING이며
같은 kernel의 footprint transfer 검증이다. Independent kernel validation과
제품 적합성 판정은 각각 NOT_ESTABLISHED, UNDECIDED로 유지한다.

# P5/P6 검증 보강 적용 — 2026-10-31

상태: **host/native 검증 완료, P5 guest campaign 진행**. 전체 P0–P6 완료가 아니다.

## 적용 내용과 소유권

- Root `scripts/gem5/image_summary.py`: background finish가 마지막 foreground frame finish보다
  이르면 거부한다. Timer granularity로 같은 tick인 경우는 허용한다. Regression fixture 추가.
- gem5 submodule `scripts/zena_cmn/verify_config.py`: HNF SLC associativity/tag·data latency/
  bank/resource stalls, Garnet network/credit child latency와 clock binding, netif clock,
  private sequencer clock binding 검사를 추가했다. Mutation tests를 함께 적용했다.
- Root `test_tmux.py`: fixture profile을 YAML mapping으로 만들고 fake executable에 launcher의
  native provenance query 응답을 추가했다. 실제 tmux UART/echo/F12 종료를 검사한다.
  Fake oracle은 UI fixture 전용이며 native model 검증 증거가 아니다.

기존 미커밋 변경을 보존했으며 commit/push하지 않았다. Source218의 변경6개와 새 host 도구를
새 validation revision으로 기록했다. Native import/model dependency165개는 기존 baseline
launch의 SHA256과 모두 동일했다. Guest source/image/native/model 변경이 없어 rebuild 대신
기존 binary의 실제 native oracle과 matching snapshot을 사용한다. 이전 freeze manifest를
수정하지 않으며 old runner의 source mismatch를 우회하지 않는다.

## 완료한 검사

Evidence: `build/qbox-apollo-qvp/gem5/verification-20261031/`.

| 검사 | 결과 | 범위 |
|---|---|---|
| Root test discovery | 113 PASS | Host functional/collector/launcher 및 real tmux with fake simulator |
| Native config mutation | 31개 중 28 PASS, 3 SKIP | 실제 native oracle; NPU/SCMI/Simple-network 미선택 profile SKIP |
| Native positive config | 6 PASS | baseline/CPU1GHz/mesh1GHz/SLC8MiB/channels8/NoC16B의 기존 actual config·DTB |
| Native model source identity | 165/165 일치 | Host 검증 수정은 model closure에 포함되지 않음 |
| Cache 완료 raw 재검증 | 4 VALID | 32/128/1024/8192KiB, passes2/warmup1 |

전체 root test 첫 실행은 tmux fixture 오류로 실패했다. 유효 YAML로 바꾼 후에도 native
provenance 응답이 없어 실패했고, 두 원인을 수정한 마지막 전체113 tests가 통과했다.
실패 log와 pane capture를 함께 보존했다. Native positive config PASS를 새 P6 uncertainty
workload 실행 PASS로 바꾸지 않는다.

## 완료 cache 결과

| Working set | gem5 ns/dependent-load |
|---|---:|
| 32 KiB | 2.542480 |
| 128 KiB | 13.684326 |
| 1 MiB | 24.995880 |
| 8 MiB | 121.795343 |

32KiB는 기존 실행을 수정 collector로 검토했고 나머지3개는 새 policy queue의 실행 결과다.
세 run은 약599.08 host seconds에 정상 종료했다. ROI·checksum·config·dependency가 유효한
결과이며 추가 warmup/length 수렴 완료를 의미하지 않는다. [Orin reference](orin-reference-20261030.md)의
짧은8MiB 조건과 수치가 비슷해도 A720AE silicon calibration 근거로 취급하지 않는다.

## 새 P5 campaign

Service `apollo-gem5-p5-envcapture-20261031.service`가 matching snapshot에서 실행한다.
최대4 run, 전체21600 host seconds, command별7200초, 동시1개, first nonPASS stop이다.
Systemd 상한21720초는 cleanup 여유이며 controller 예산은21600초다. Linger=yes로 SSH와
독립 실행한다. 예산/실패 뒤 남은 sample은 NOT_RUN이며 자동 retry하지 않는다.

| 조건 | Foreground / background |
|---|---|
| solo | CPU0, pool2, background 없음 |
| bg1 | CPU0, pool2, CPU1 read16MiB worker1개 |
| bg4 | CPU0, pool2, CPU4 read16MiB worker1개 |
| pool1 | CPU0, pool1, background 없음 |

공통640×480/frames4/warmup4 유지. Before/after IRQ affinity와 housekeeping 관련 정보를
기존 v2 command file로 기록한다. `verify-p5.py`가 native config와 capture protocol을 검사하고
부분·미지원 항목은 별도 environment JSON으로 보존한다. Protocol PASS와 environment policy,
정확한 ROI IRQ routing, isolation 보장을 구분한다. 각 scenario의 수렴은 별도 후속 gate다.

`policy.json`, `campaign.json`, `validation-revision.json`과233개 pin을 보존한다.
CLI output의 policy/campaign SHA는 파일 bytes hash이며 execution START의 hash는 canonical
JSON hash다. 두 표현을 같은 값으로 비교하지 않는다. 변경 금지 대상은 policy의 pins다.

## 남은 필수 작업

P2 read warmup/length 후속, P5 실제 환경/동시 workload 결과 및 scenario별 안정성,
P6 uncertainty 후보 실행과 decision record, 독립 workload 검증 범위 연결, 전체41-ID 및
unnumbered command/artifact completion audit이 남아 있다. 제품 목표/PPA/resident memory
입력 미정은 UNDECIDED를 유지하며 이 때문에 가능한 모델 탐색을 생략하지 않는다.

## Orin 연결 재확인 및 P6 첫 config probe

Orin SSH/passwordless sudo 정상, CPU0–11 online, MAXN 및 기존 ROS service2개 active를
재확인했다. 이번 확인에서 remote 설정 변경이나 benchmark 재실행은 하지 않았다.
`orin-connectivity.json`에 기록했다.

P6 L2 data latency +2 profile은 실제 native로 1 tick instantiate 후 config/DTB verifier PASS다.
`p6-config-only-v2/ap16-u-l2-data-plus2/verification-native-env.json` 참조.
실행 자체는 max-ticks=1에 따른 exit2/INCOMPLETE이며 boot/performance PASS가 아니다.
첫 port0 시도는 Terminal assertion, 첫 verifier는 native 환경 미설정으로 실패했고
각 로그를 보존했다. 유효 port와 metadata의 child environment로 검사했다. 나머지4 profile은 NOT_RUN.

## P2 후속 준비와 P5 verifier 환경 확인

`p2-read-followup/check.json`은 새 single-run policy와 pinned inputs 검사 PASS다.
`anchor-review.json`에서 기존 warmup2 read run의 dependency-bound readiness와 VALID를
재확인했다(useful 38.677699 GB/s). 예정 run은 동일64MiB/16 workers/measured2, warmup4다.
Command21600초, 전체22200초로 제한하며 자동 measured4 실행은 하지 않는다. 먼저
기존5% gate를 적용한다. Runtime 결과는 별도 기록한다.

P5 coordinator의 `/proc` 환경만 보고 native verifier 환경이 누락됐다고 진단한 것은
오류였다. 실제 immutable `verification_argv`에는 처음부터 `/usr/bin/env`로
PYTHONHOME/LD_LIBRARY_PATH가 명시돼 있었다. Campaign SHA `b6efd5a2…`와 policy SHA
`2d0243cd…`는 초기값과 같고 실제 첫 run의 native verifier도 PASS다. P5 verifier 실패나
복구 실행은 발생하지 않았다. `p5-verifier-environment-followup.json`은 철회된 초기 진단이며
`p5-solo-completed-review.json`의 correction으로 대체한다. 별도의 P6 manual probe에서
환경 누락으로 실패한 사실은 유지하되 P5 service에 일반화하지 않는다.

## 후속 진행

P6 5개 profile 모두 실제 native config/DTB verifier PASS. `p6-config-summary.json`에
개별 증거를 연결했다. L2/L3/SLC data latency, router/link latency 및 Hynix DRAM
profile의 1-tick instantiate 결과이며 guest 성능·boot PASS가 아니다. 앞 절의 나머지
4 profile NOT_RUN은 이 결과로 갱신한다. Full control workload 실행은 shortlist 선정
후 robustness-policy의 조건에 따른다. Baseline-only 보류를 control PASS로 표시하지 않는다.

P2 service `apollo-gem5-p2-read-warmup-20261031.service` 실행을 확인했다. P5와 합쳐
native2개이며 SSH 독립 실행한다. Warmup4 채택이나 measured4 후속은 자동 승인하지 않는다.

기존 P4 interaction helper의 --check는 host verifier 변경을 old source freeze 위반으로
거부했다(`p4-interaction-check.log`). 이전 manifest를 수정하거나 guard를 우회하지 않는다.
새 validation revision에서 동일 arithmetic mean 기반 집계를 재현할 필요가 있다.
남은 deliverable은 hypothesis support/refute/unresolved 종합표, shortlist/exclusion/re-entry,
P5 scenario 안정성, 독립 validation 역할과 raw evidence, comparison/decision artifact 및
전체41-ID/unnumbered completion audit다. 제품 목표 미정은 이 작업의 생략 근거가 아니다.

## P4 interaction 재집계 완료

새 host revision의 `review-p4-current-v2.py`로19개 raw record의 readiness, workload,
model source identity, 실제 config delta 및 warmup/length gate를 다시 검사했다.
`p4-current-result-v2.json`은 helper/campaign/policy/6 followup plan/6 comparison receipt의
15개 hash binding을 포함한다. 기존 freeze를 수정하거나 그 guard를 우회한 실행이 아니다.
초기 재집계와 보강 revision의 interaction 결과는 동일하다.

| Interaction | Mean y00 / y10 / y01 / y11 (ms/frame) | Additive interaction | 판정 |
|---|---|---:|---|
| CPU2→1GHz × mesh2→1GHz | 2.422902 / 3.070182 / 3.159182 / 3.758082 | −0.048380 ms, baseline 대비 −1.9968% | PASS: 4 corners의 warmup/length 모두 PASS |
| SLC4→8MiB × channels16→8 | 2.422902 / 1.232560 / 2.456406 / 1.231340 | −0.034724 ms, baseline 대비 −1.4332% | NOT_ACCEPTED: SLC 단독/결합 warmup FAIL, length NOT_RUN |

값은 validated frame duration의 arithmetic mean이다. CPU/mesh 축소의 결합 지연은
각 단독 변화의 단순 합보다 작았다. 이것은 해당 workload/model에서 관측한 interaction이며
통계적 유의성이나 silicon 인과관계를 입증하지 않는다. SLC의 큰 관측 개선도 수렴 실패가
있으므로 accepted shortlist 근거로 승격하지 않는다. Eight-channel 관측 mean 변화 약1.38%는
제품 동등성 또는 유의성 판정이 아니다. 최종 shortlist에는 P5 및 별도 validation이 남아 있다.

재현 명령: `/usr/bin/python3 -E -B build/qbox-apollo-qvp/gem5/verification-20261031/review-p4-current-v2.py`.
Output은 exclusive create이므로 재검토 시 기존 결과를 덮어쓰지 않고 새 revision/path를 사용한다.

## P5 비교 후보 지명 — 최종 선정 아님

`nominate-screening.py`가11개 P4 candidate의 receipt-bound inventory/run/config/artifact를
다시 확인했다. Recovery 경로의 L3 결과도 receipt가 지정한 실제 경로로 확인했다.
기존 P4 aggregate의 baseline을 사용하고 profile/input/instantiated config delta를
승인 receipt와 비교했다. `screening-nomination.json`이 결과다.

| Candidate | Mean ms/frame | DRAM bytes/frame | Convergence evidence |
|---|---:|---:|---|
| ap4-topology | 2.418690 | 7394912 | NOT_ESTABLISHED |
| ap16-channels-8 | 2.456406 | 7444976 | PASS |
| ap16-cpu-1ghz | 3.070182 | 7557104 | PASS |
| ap16-cpu-1ghz-mesh-1ghz | 3.758082 | 7497056 | PASS |
| ap16-l2-1m | 2.410920 | 7001120 | NOT_ESTABLISHED |
| ap16-l3-8m | 1.218956 | 28720 | FAIL_REPORTED_NOT_RECOMPUTED |
| ap16-mesh-1ghz | 3.159182 | 7428384 | PASS |
| ap16-noc-width-16b | 2.620926 | 7433808 | NOT_ESTABLISHED |
| ap16-ruby-1ghz | 2.536186 | 7416416 | NOT_ESTABLISHED |
| ap16-slc-8m-channels-8 | 1.231340 | 5504 | FAIL |
| ap16-slc-8m | 1.232560 | 23312 | FAIL |

`ap16-channels-8`을 provisional A로 지명한다. Converged AP16 대안 중 mean이 가장 작고,
baseline 대비 약1.38% 느린 관측값과 절반 channel/controller 구성을 비교할 수 있다.
이는 PPA 절감량이나 제품 허용 지연을 뜻하지 않는다. `ap16-mesh-1ghz`는 나머지 converged
후보 중 DRAM bytes/frame이 가장 적고 A보다 적으므로 provisional challenger B다.
Baseline보다 solo mean이 약30.39% 느리며, 최종 B 유지에는 P5의 W 또는 rank reversal
조건이 필요하다. 모든 scenario에서 열등하거나 유리하다고 미리 판단하지 않는다.

L2/NoC width/Ruby clock은 candidate convergence가 미확립되어 보류한다. L3는 별도
terminal review의 실패를 보존했으며 이번에 convergence를 재계산하지 않았다.
SLC와 결합안은 재계산된 실패를 보존한다. AP4는 topology 확인용이라 AP16 shortlist에서
제외한다. 큰 cache의 관측 개선을 수렴 실패에도 불구하고 성능 우위로 승인하지 않는다.

`p5-nominees/`에 A/B 각각 solo/bg1/bg4 총6개 조건을 준비했고 policy/pins check PASS다.
최대6 run/43200 host seconds, command7200초이며 **PREPARED / NOT_RUN**이다.
현재 baseline P5 raw/protocol/environment와 실패 원인을 먼저 검토하며 자동 시작하지 않는다.
Native verifier metadata 환경은 새 argv에 명시했고 기존 실행 policy는 수정하지 않았다.
P5 새 scenario의 수렴과 독립 validation, 선정 후 P6 control은 여전히 남아 있다.
`final_selected_design_ids=[]`와 제품 `UNDECIDED`를 유지한다.

## Held-out footprint와 memory inventory

결과를 보기 전에 pool1을 held-out footprint로 선언했다(`heldout-pool1/role.json`).
Baseline pool1 output 부재를 확인했으며 channels8 pool1 1개를 추가 준비했다.
Policy check PASS, runtime NOT_RUN이다. Pool2의9,216,000B에서 pool1의4,608,000B로
allocation이 줄지만 warmup4의 총 준비 작업량도 달라지므로 순수 cache capacity 효과로
해석하지 않는다. Nominal 비교가 끝나도 scenario별 수렴 없이는 robustness를 승인하지 않는다.
Calibration은 수행하지 않았으며 `PASS_DISTINCT_KERNELS`도 부여하지 않는다.

현재 collector로 memory9개 VALID, measured4/warmup2 NOT_RUN을 확인했다.
[가설별 evidence 표](hypothesis-status-20261031.md)에 SUPPORT/REFUTE/UNRESOLVED와
남은 검증을 정리했다. Local file link 검사는 기존10문서92개 target에서 누락0개였다.
Anchor/web/render 검사를 수행했다는 의미는 아니다.

[41개 항목 중간 completion audit](completion-audit-20261031.md)를 갱신했다. 전체 완료 승인이 아니며 번호 밖 산출물도 함께 추적한다.

최신 검사: 12문서 local link96개와 anchor link6개에서 누락0개를 확인했다(`doc-links-anchors.json`). Heading slug는 local approximation이며 web/render 검사는 포함하지 않는다. P5 첫 run은 ROI end tick709748283500을 기록했지만 guest 결과/after capture/terminal acceptance는 아직 대기 상태다.

## P5 solo terminal 검증 완료

첫 envcapture2 solo run은 guest output/checksum, 정상 exit, native config, capture protocol
및 dependency-bound raw 검사 PASS다. Host3855.59초(약64.26분), arithmetic mean과 세부
raw binding은 `p5-solo-completed-review.json`에 있다. Environment supplemental evidence는
INCOMPLETE, policy validation은 NOT_EVALUATED이며 이를 isolation PASS로 올리지 않는다.
Queue는 기존 policy 그대로 CPU1 background 조건으로 진행했다. Solo 한 run의 VALID는
새 envcapture regime의 warmup/length 수렴이나 동시 workload 완료를 뜻하지 않는다.

## Env-captured solo convergence 준비

`p5-solo-convergence/`에 새 solo anchor(f4/wu4)와 비교할 f4/wu2 및 f8/wu4 endpoint를
준비했다. Before/after capture script는 동일하고 benchmark invocation의 해당 숫자만
변경했다. Shell syntax 및 두 정책의 source/input pin 검사 PASS, runtime NOT_RUN이다.

첫 warmup2 endpoint 완료 후 normalized latency/throughput/DRAM ratio와 arithmetic mean을
기존5% 기준으로 비교한다. 모든 gate가 PASS일 때만 frames8 endpoint를 실행한다.
별도 single-run policy이며 자동 scheduling은 하지 않는다. Endpoint당 command7200초,
전체7800초 상한은 실제 solo3855.59초 관측에 기반하며 완료시간을 보장하지 않는다.
기존 no-envcapture baseline 수렴을 새 regime에 대입하지 않는다. 현재 BG1/P2 두 native를
유지하며 새 실행은 available slot 및 terminal 결과를 확인한 후에만 진행한다.

준비된 nominee6개, heldout1개, solo convergence의 anchor+endpoint3개에 대해
`check-prepared-cases.py`를 실행했다. Launcher argparse, 실제 guest invocation과 workload
contract, 기록된 snapshot CPU/channel/interleave/profile hash, native metadata와 verify argv
환경을 대조하여10개 정의 모두 PASS다(`prepared-cases-check.json`). Native process 없이
수행한 정적 검사이며 full model contract/restore/runtime 승인으로 사용하지 않는다.

## Solo 환경 evidence의 해석

완료 solo의 before/after 모두 CPU0–15 online, isolated CPU 목록은 비어 있고,
default IRQ affinity와 global unbound workqueue mask는 `ffff`였다.
`sched_rt_runtime_us=950000`, `/sys/devices/system/cpu/nohz_full`은 MISSING_OR_UNSUPPORTED다.
Pinned kernel의 `NR_CPUS=512`는 compile-time 상한이며 simulated online CPU가512개라는
뜻이 아니다. `NO_HZ_FULL=n`을 함께 기록한다. Numeric Linux IRQ directory16개를 before/after
동일하게 열거했지만 각 IRQ의 user-routability, exact ROI routing, 개별 workqueue/kthread
실행 위치를 입증하지 않는다. Sequential pre/post capture는 atomic snapshot도 아니다.
따라서 solo VALID는 일반 Linux 환경의 synthetic kernel 관측값이며 IRQ/housekeeping
isolation 또는 realtime 보장의 PASS가 아니다. 다음 BG 비교에서도 이 경계를 유지한다.


## Orin cache measured-length 후속 검증

[Orin reference 추가 결과](orin-reference-20261030.md#2026-10-31-추가-measured-length-검증):
8MiB/warmup4/CPU0, passes256→512 각3회 checksum PASS. Median75.505630→75.000171ns/load,
변화−0.6694%로 사전5% median gate PASS. Source hash 및 clock/service 복원 비교 PASS.
전체 steady-state/PMU/gem5 수렴 판정은 별도이며 기존 P2/P5 gate를 대체하지 않는다.
Evidence는 `build/qbox-apollo-qvp/gem5/orin-length-20261031/`에 별도 보존했다.


## P2 read warmup2→4 완료 및 measured-length 후속

`V/p2-read-followup/completed-review.json`에서 두 raw run을 현재 `inspect_run`/
`case_ready`와 typed workload contract로 재검증했다. 양쪽 VALID, native config PASS이며
canonical profile/config 및 model dependency 동일성 확인 후 사전5% gate를 평가했다.

| Metric | Warmup2 | Warmup4 | 변화 | Gate |
|---|---:|---:|---:|---|
| Useful GB/s | 38.677699 | 37.472453 | −3.1161% | PASS |
| DRAM GB/s | 39.071586 | 37.699362 | −3.5121% | PASS |
| DRAM/useful ratio | 1.010184 | 1.006055 | −0.4087% | PASS |

기존 warmup1→2 FAIL은 보존한다. 이 PASS로 warmup4를 새 기본값으로 채택하지 않고,
계획대로 warmup2에서 measured passes2→4를 비교한다. 새 endpoint는
`V/p2-read-length/`에 고정했으며 policy check PASS 후
`apollo-gem5-p2-read-length-20261031.service`로 시작했다. 이전 P2 native 종료 확인 후
실행했으므로 P5와 합쳐 native 최대2개를 유지한다. 이 endpoint의 완료·수렴 판정은
아직 NOT_RUN이며 전체 steady-state 검증 완료로 해석하지 않는다.


## P5 baseline CPU1 background 완료

`V/p5-bg1-completed-review.json`은 solo/BG1 raw를 `inspect_run`/`case_ready`와
각 typed workload contract로 재검증한 결과다. 양쪽 VALID, native config 및 capture
protocol PASS, BG1 launch/verify exit0이다. 동일 profile/config/model에서 CPU1의
read16MiB worker1개만 추가된 선언 조건을 확인했다. 다음 CPU4 BG case는 기존 queue가
자동으로 이어 실행한다.

| 지표 | Solo | CPU1 BG | 상대 변화 |
|---|---:|---:|---:|
| Mean kernel ns/frame | 2425984 | 2478652 | +2.1710% |
| Median frame latency ns | 2412048 | 2472500 | +2.5063% |
| Observed max frame latency ns | 2472048 | 2520776 | +1.9712% |
| Foreground frame/s | 412.178727 | 403.412222 | −2.1269% |
| Aggregate DRAM GB/s | 3.117894 | 4.967287 | +59.3155% |

출력1843200개 element 검증 mismatch0, hash `d22a30a02c070a81` 일치.
BG completed4582 chunks/18767872 useful bytes이며 finish92167385는 마지막
foreground finish92167130 이후다. Timestamp 단위는 CNTVCT125MHz tick이다.
DRAM 값은 foreground/background를 합친 traffic이며 BG 단독 bandwidth가 아니다.

전후 IRQ 수집 COMPLETE, 일반 환경 수집 PARTIAL(nohz_full 미노출), online0–15,
`environment_policy_validation=NOT_EVALUATED`, supplemental evidence INCOMPLETE를
유지한다. Sequential pre/post capture는 ROI 중 IRQ isolation의 증명이 아니다.
4frames의 observed max를 p99/WCET로 해석하지 않으며, 새 envcapture scenario의
warmup/length 수렴이 남아 있어 안정적인 slowdown이나 최종 P5 acceptance를 주장하지 않는다.
비교 specification은 완료 후 evidence 검토용으로 기록했으며 사전 통계 검정으로 표시하지 않는다.

## CPU4 background 완료 및 pool1 시작

`ap16-baseline-image-f4-pool2-wu4-cpu0-bg4-read16m-schema3-envcapture2`가
launch/verify exit 0으로 완료됐다. `p5-bg4-completed-review.json`은 solo/CPU1/CPU4
세 raw run을 새로 inspect하여 `case_ready`와 비교 입력 계약을 확인한 evidence다.
CPU1→CPU4 비교에서는 `background_cpus.0`만 workload 변경으로 허용했다.
비교 specification은 완료 후 evidence review이며 preregistered statistical test가 아니다.

| 지표 | Solo | CPU1 background | CPU4 background |
|---|---:|---:|---:|
| Mean kernel ns/frame | 2,425,984 | 2,478,652 | 2,466,058 |
| Median frame latency ns | 2,412,048 | 2,472,500 | 2,455,808 |
| Observed max frame latency ns | 2,472,048 | 2,520,776 | 2,512,560 |
| Foreground frame/s | 412.178727 | 403.412222 | 405.483105 |
| Aggregate DRAM GB/s | 3.117894 | 4.967287 | 5.121168 |

CPU4 mean은 solo 대비 +1.651866%다. Output 1,843,200 elements를 검증했고
mismatch 0, hash `d22a30a02c070a81`이다. CPU4 background의 finish tick
92,135,532가 마지막 foreground finish tick 92,135,136 이상으로 finish guard를 통과했다.
Guest workload exit 0, IRQ capture 전후 exit 0, protocol PASS를 확인했다.
일반 환경 수집은 `nohz_full` 부재로 전후 PARTIAL이며 environment policy는
NOT_EVALUATED, scenario convergence는 NOT_ESTABLISHED, product는 UNDECIDED다.
4 frames의 observed max를 p99/WCET로 해석하거나 CPU placement 우열을 확정하지 않는다.
DRAM 수치는 foreground와 background의 합계다.

기존 serial queue는 다음 `ap16-baseline-image-f4-pool1-wu4-cpu0-schema3-envcapture2`를
시작했다. Pool1 결과와 별도 convergence gate는 아직 확보하지 않았다.

## P2 read measured passes2→4 완료

`p2-read-length/completed-review.json`은 두 case를 현재 collector로 다시 읽고
저장된 config report의 artifact binding, typed workload contract 및 model provenance를
검사한 결과다. 두 case 모두 `case_ready=True`, `VALID`다. Native와 verifier는
exit0이며 guest `APOLLO_WORKLOAD_EXIT=0`, PSCI power-off를 확인했다.

| 정규화 metric | passes2 / warmup2 | passes4 / warmup2 | 상대 변화 | 5% gate |
|---|---:|---:|---:|---|
| Useful GB/s | 38.677699 | 38.717779 | +0.104% | PASS |
| DRAM GB/s | 39.071586 | 39.034376 | −0.095% | PASS |
| DRAM/useful ratio | 1.010184 | 1.008177 | −0.199% | PASS |

Profile/config/model은 같고 workload 변경은 passes2→4 하나뿐이다. 이전 warmup2→4
세 metric PASS와 함께 baseline read16/64MiB/64-B stripe의 passes2/warmup2
조건을 유지할 근거가 된다. Warmup1→2 FAIL은 보존한다. 이 gate는 다른 memory
조건의 안정성, 실제 DRAM peak, silicon calibration을 입증하지 않는다.

## P5 pool1 완료 및 solo warmup gate 시작

`p5-pool1-completed-review.json`: native/verifier exit0, typed workload contract,
config binding, model provenance와 `case_ready=True`를 확인했다. 640×480, frames4,
pool1, warmup4, CPU0 solo이며 working set 4,608,000 B다. Median frame latency
1,169,664 ns, observed max 1,235,088 ns, throughput 844.804369 frame/s, aggregate
DRAM bandwidth 0.075223 GB/s다. IRQ capture 전후 COMPLETE, protocol PASS이며
일반 환경 PARTIAL 및 environment policy NOT_EVALUATED는 유지한다. Pool1 numerical
stability는 아직 NOT_ESTABLISHED이며 pool2 대비 개선을 안정된 capacity 효과로 확정하지 않는다.

기존 P5 queue 네 case 모두 execution PASS 후, 준비된
`p5-solo-convergence/warmup2-policy.json`의 hash/schema check를 재실행했다.
`apollo-gem5-p5-warmup2-20261031.service`로 warmup2 endpoint를 시작했다.
Invocation ID `3fb08a255c56463fb441fa2dfe599d1e`; 한 case, command7200s,
policy7800s, systemd7920s 상한이다. 기존 warmup4와 모든 declared normalized metric
및 arithmetic mean의 5% gate를 확인한 뒤에만 frames8 endpoint를 실행한다.

## P5 provisional nominees queue 시작

Baseline 네 case를 현재 `inspect_run`으로 재검토해 모두 case_ready=True 및
capture protocol PASS를 확인했다. Entry review는 `p5-nominees/entry-review.json`,
재실행한 policy check는 `p5-nominees/entry-check.json`이다. IRQ layout은 COMPLETE지만
supplemental INCOMPLETE/environment policy NOT_EVALUATED는 유지한다. 이 상태의
탐색 비교를 수행하며 isolation acceptance나 최종 설계 선정으로 승격하지 않는다.

`apollo-gem5-p5-nominees-20261031.service`를 시작했다. Invocation ID는
`1954b33565a44b5aa5a6494c793e8599`다. 사전 준비된 순서대로 channels8의
solo/BG1/BG4, mesh1GHz의 solo/BG1/BG4를 직렬 실행한다. Max6 cases,
command7200s, policy43200s, systemd43320s이며 첫 execution/verification non-PASS에서
중단한다. Global native 상한2는 별도 image warmup endpoint와 합산한다.
B는 P5 W/rank criterion 검토 전까지 provisional이고 final_selected_design_ids는 빈 값이다.

## P5 envcapture solo warmup2→4 수렴 PASS

Warmup2 native/verifier exit0, PSCI power-off 및 output mismatch0을 확인했다.
두 endpoint의 raw/config/provenance와 typed workload를 다시 검증하여 case_ready=True를
확인했다. 변경은 warmup_passes2→4 및 대응 readfile뿐이며 profile/config/model은 같다.
기존 `run-remaining-v4.py`의 mean_kernel_ns/convergence_gate 계산 함수만 재사용했고
historical freeze runner를 실행하지 않았다. Evidence는
`p5-solo-convergence/warmup-completed-review.json`이다.

| Metric | Warmup2 | Warmup4 | 상대 변화 | 5% gate |
|---|---:|---:|---:|---|
| Mean kernel ns/frame | 2,429,512 | 2,425,984 | −0.145% | PASS |
| Median frame latency ns | 2,411,056 | 2,412,048 | +0.041% | PASS |
| Frame/s | 411.578527 | 412.178727 | +0.146% | PASS |
| DRAM/useful ratio | 1.604528 | 1.643375 | +2.421% | PASS |

모든 warmup gate PASS 후 준비된 frames8 policy check를 재실행하고
`apollo-gem5-p5-frames8-20261031.service`를 시작했다. Invocation ID
`6487c91b2fbe4c8abbf8284d657daec3`, command7200s/policy7800s/systemd7920s다.
Frames4→8 gate는 아직 RUNNING이며 BG/held-out/다른 후보 조건의 수렴으로 전이하지 않는다.
Environment policy NOT_EVALUATED와 제품 UNDECIDED는 유지한다.

## P5 channels8 solo 완료

Native/verifier exit0, 두 case의 fresh case_ready/typed workload/config binding PASS를
확인했다. `p5-channels8-solo-completed-review.json`은 기존
`image-channels8-reviewed-comparison.json`에 묶인 profile/config delta와 새 pair의
실제 delta가 값까지 정확히 같음을 검사한다. Workload/readfile은 동일하며 profile
차이는 memory.channels16→8이다. 이 fresh-pair 검토는 posthoc evidence review이며
preregistered statistical test가 아니다.

| Metric | Baseline16 | Channels8 | 상대 변화 |
|---|---:|---:|---:|
| Mean kernel ns/frame | 2,425,984 | 2,459,686 | +1.389% |
| Median frame latency ns | 2,412,048 | 2,445,780 | +1.398% |
| Observed max frame latency ns | 2,472,048 | 2,511,064 | +1.578% |
| Throughput frame/s | 412.178727 | 406.532820 | −1.370% |
| DRAM GB/s | 3.117894 | 3.075396 | −1.363% |

Output mismatch0, hash d22a30a02c070a81, IRQ capture COMPLETE, protocol PASS다.
Environment policy NOT_EVALUATED, 새 envcapture candidate 수렴 NOT_ESTABLISHED,
final_selected_design_ids=[]와 제품 UNDECIDED는 유지한다. BG와 held-out 결과가
없는 solo 관측값으로 8-channel 채택이나 PPA 이득을 확정하지 않는다.


## Held-out pool1 수렴 endpoint 준비 (2026-11-01)

`V/pool1-convergence/`에 baseline·channels8 각각 warmup2/frames8 endpoint4개를
준비했다. 기존 pool1 command에서 warmup4→2 또는 frames4→8 하나만 변경한다.
각 run은7200초, policy7800초, 총4회31200초 상한이며 global native2개 제한을 유지한다.
Policy schema, pinned input hash, shell syntax PASS이며 restore/runtime은 NOT_RUN이다.
각 설계의 원래 frames4/warmup4 anchor가 raw/config/protocol 검증을 통과해야 진입한다.
해당 설계의 warmup2→4 normalized3 metrics와 arithmetic mean이 모두5% 이내일 때만
frames4→8을 실행한다. 실패 기준 완화나 자동 재시도는 없다. 같은 kernel의 footprint
transfer 검증이며 independent-kernel validation이나 repeatability 검증이 아니다.


## Channels8 + CPU1 background recovery 완료 (2026-11-01)

`V/recovery-20261101/nominees/bg1-completed-review.json`에 terminal launch/verify PASS
후 fresh raw/config/model-source/workload-contract 검증 및 비교를 보존했다.
Mean kernel time은2509772 ns/frame으로, 같은 CPU1 background의16-channel
2478652 ns 대비 +1.256%,8-channel solo2459686 ns 대비 +2.036%다.
Median frame latency2528328 ns, observed max2572176 ns, throughput398.4105 frame/s,
aggregate DRAM4.852102 GB/s다. 기존 config/workload delta 계약을 적용한 posthoc 비교이며
새로운 통계 검정이나 scenario convergence PASS가 아니다. Capture protocol은 PASS,
environment policy는 NOT_EVALUATED, 제품 판정은 UNDECIDED를 유지한다.
동일 queue는 channels8 + CPU4 background recovery로 진행했다.


## Held-out pool1 완료 및 BG1 warmup 시작 (2026-11-01)

`V/heldout-pool1/completed-review.json`: launch/verifier PASS 후 네 raw record를
fresh inspect하여 channel-only delta와 workload contract를 확인했다. Pool1의
mean kernel time은 baseline1183624 ns,channels8 1182020 ns로 ratio0.99864484
(−0.136%)다. Pool2의 ratio1.01389209(+1.389%)와 관측 부호가 다르지만
pool1 양 설계의 convergence와 repeatability가 미확립이므로 robust rank reversal
또는 제품 우위로 해석하지 않는다. 같은 kernel의 footprint transfer이며
independent-kernel validation은 NOT_ESTABLISHED, environment policy는 NOT_EVALUATED다.
처음 비교 집계에서 standalone saved record에 없는 `id`를 읽어 KeyError가 발생했고
출력 파일 작성 전 중단됐다. Campaign/role ID와 run 경로로 reference를 연결해 수정했다.

빈 실행 슬롯에 `apollo-gem5-bg1-warmup2-20261101.service`를 시작했다
(invocation `7befb2ed57ad4b4a83243e2130bf87f9`).
`V/p5-bg-convergence/bg1-warmup2-prelaunch-20261101.json`의 입력 검사 PASS 후 실행했으며
ledger는 `bg1-warmup2-execution/execution.jsonl`이다. Global native2 제한을 유지한다.


## Channels8 + CPU4 background recovery 완료 (2026-11-01)

`V/recovery-20261101/nominees/bg4-completed-review.json`: launch/verifier PASS 후
fresh raw/config/model-source/workload contract와 channel-only/workload delta를
검증했다. Mean kernel time2504008 ns/frame은 같은 CPU4 background의16-channel
2466058 ns보다 +1.539%,8-channel solo2459686 ns보다 +1.802%다.
Median frame latency2503380 ns, observed max2557368 ns, throughput399.3253 frame/s,
aggregate DRAM5.002294 GB/s다. Posthoc comparison이며 scenario convergence는
NOT_ESTABLISHED, environment policy는 NOT_EVALUATED, 제품 판정은 UNDECIDED다.
Queue는 mesh1GHz solo recovery로 전진했다. CPU1 baseline warmup2는 별도 service에서
ROI 종료·guest mismatch0 확인 후 사후 환경 수집 중이며 terminal verifier를 기다린다.


## Baseline CPU1 background warmup 수렴 PASS (2026-11-01)

`V/p5-bg-convergence/bg1-warmup-completed-review.json`: warmup2 endpoint의
launch/verifier PASS 뒤 fresh raw/config/model-source 및 workload 비교를 수행했다.
Warmup2→4에서 mean kernel time2486966→2478652 ns(−0.334%), median frame
2475668→2472500 ns(−0.128%), FPS402.06048→403.41222(+0.336%),
DRAM/useful ratio2.6659514→2.6769167(+0.411%)로 네5% gate 모두 PASS다.
동일 CPU1 background 조건의 warmup 안정성만 확립했으며 length/repeatability 및
다른 placement/후보로 전이하지 않는다. Environment policy는 NOT_EVALUATED다.

이 결과와 fresh input pin 검사 PASS를 근거로 frames4→8 endpoint를
`apollo-gem5-bg1-frames8-20261101.service`에서 시작했다
(invocation `cdf50ea2b3ce4a3bb70597651ad02e90`). Ledger는
`V/p5-bg-convergence/bg1-frames8-execution/execution.jsonl`이며,
command7200초/policy7800초/global native2 제한을 유지한다.


## P5 환경 evidence의 요구 범위와 판정 경계 (2026-11-01)

[DES-DSE-04](design.md)의 원문 요구는 Linux housekeeping/IRQ 배치를 기록하는 것이다.
REQ-DSE-011과 VER-DSE-013은 foreground/background의 완료 work, timebase, ROI와
동시성 및 scenario 구분을 요구한다. 별도의 isolated CPU/NO_HZ_FULL 정책을 제품 목표로
정의하지 않았다. 따라서 환경 policy의 NOT_EVALUATED는 사실 그대로 보존하되, 미정인
isolation 보장을 새 합격 조건으로 발명하지 않는다. 기존 output/overlap/config/수렴
gate는 계속 적용하며 이것으로 다른 미완료 요구를 완료 처리하지 않는다.

현재 capture는 online CPU0–15, isolated mask, kernel cmdline, scheduler RT budget,
pre/post interrupt counters와 exposed IRQ affinity, unbound workqueue mask를 보존한다.
Pinned kernel의 CONFIG_NO_HZ_FULL=n 때문에 nohz_full interface의 미지원 상태가 기록되어
base capture PARTIAL/facts_complete=false가 유지된다. 이를 COMPLETE로 수정하지 않는다.
IRQ capture protocol PASS도 정확한 ROI routing, 모든 kthread의 housekeeping 배치,
interrupt-free execution 또는 WCET 보장이 아니다. 결과 해석은 이 관측 환경으로 한정한다.

### 2026-11-01 Mesh 1GHz solo recovery 완료

`verification-20261031/recovery-20261101/nominees/mesh-solo-completed-review.json`에
현재 raw output, config verification, model source closure 및 typed workload contract를
다시 검사한 baseline/mesh pair를 기록했다. Launcher와 verifier는 모두 exit 0이다.
Effective config 차이는 `system.ruby.network.clk_domain.clock.0: 500 → 1000`,
profile 차이는 `cmn.mesh.clock: 2GHz → 1GHz`뿐이며 기존 mesh-only receipt의
expected delta와 일치한다. Workload 차이는 없다.

- Mean kernel latency: 2,425,984 → 3,160,246 ns/frame (**+30.2666%**).
- Median frame latency: 2,412,048 → 3,146,380 ns (**+30.4443%**).
- Foreground throughput: 412.1787 → 316.4140 frame/s (**−23.2338%**).
- Aggregate DRAM throughput: 3.11789 → 2.34593 GB/s.
- DRAM/useful ratio: 1.643375 → 1.610726.

이는 완료된 pair의 posthoc model observation이다. 해당 P5 scenario의 convergence는
`NOT_ESTABLISHED`, product decision은 `UNDECIDED`이며 silicon 성능 일치를 뜻하지 않는다.
IRQ capture는 before/after exit 0이고 일반 환경 capture는 미지원 항목으로 `PARTIAL`이다.
Environment policy 판정은 `NOT_EVALUATED`로 유지한다.
Queue는 같은 mesh profile의 CPU1 background case로 진행했으며,
baseline CPU1 background 8-frame length 검증은 별도 service에서 ROI 실행 중이다.

### 2026-11-01 Baseline CPU1 background length convergence 완료

`verification-20261031/p5-bg-convergence/bg1-length-completed-review.json`에서
fresh raw/config/model closure 및 typed workload contract를 검사했다.
Launcher/verifier exit 0이며 config/profile 차이 없이 frames만 4→8로 변경됐다.
사전 선언한 5% 기준으로 mean kernel latency 2,478,652→2,511,897 ns/frame
(+1.3413%), median latency 2,472,500→2,475,596 ns (+0.1252%),
FPS 403.4122→398.0722 (−1.3237%), DRAM/useful ratio 2.676917→2.769260
(+3.4496%)가 모두 PASS다. 기존 같은 scenario의 warmup2→4 PASS와 함께
baseline CPU1 background의 두 convergence edge를 확보했다.
이는 repeatability, 다른 placement/candidate 또는 silicon validation으로 확장하지 않는다.

Fresh CPU4 anchor contract와 input policy pin 검사를 통과한 뒤
`apollo-gem5-bg4-warmup2-20261101.service`를 시작했다
(invocation `84e0ac8f29f54a1ca5d38dadfcb7ea87`).
Evidence는 `p5-bg-convergence/bg4-warmup2-prelaunch-20261101.json` 및
`bg4-warmup2-execution/execution.jsonl`이다. CPU4 length 실행은 자체 warmup gate가
PASS일 때만 진행한다. Mesh CPU1 background ROI 실행과 합쳐 native max2를 유지한다.


### 2026-11-01 Mesh 1GHz CPU1 background recovery 완료

`verification-20261031/recovery-20261101/nominees/mesh-bg1-completed-review.json`에
fresh raw/config/model closure 및 typed workload contract를 검사한 matched pair를 보존했다.
동일 CPU1 background에서 mesh clock만 2→1GHz로 변경되며, instantiated network
clock의 500→1000 tick 차이와 profile delta가 기존 mesh-only expected delta와 일치한다.

- Mean kernel latency: 2,478,652 → 3,306,232 ns/frame (+33.3883%).
- Median frame latency: 2,472,500 → 3,298,036 ns (+33.3887%).
- Foreground throughput: 403.4122 → 302.4309 frame/s (−25.0318%).
- Aggregate DRAM throughput: 4.96729 → 3.64580 GB/s (−26.6038%).
- DRAM/useful ratio: 2.676917 → 2.621021 (−2.0881%).

Comparison PASS는 입력·결과의 유효성을 뜻한다. 이 후보 scenario의 convergence는
NOT_ESTABLISHED이며 product decision은 UNDECIDED다. Aggregate DRAM throughput 감소를
DRAM peak bandwidth 감소로 해석하지 않는다. Foreground와 background의 발행 속도도
mesh 변경에 영향을 받는 CPU-driven workload다. Silicon 성능 일치 근거가 아니다.
Nominees queue는 CPU4 background로 진행했고 baseline CPU4 warmup2 검증도 실행 중이다.


### 2026-11-01 Baseline CPU4 warmup 검증 완료

`verification-20261031/p5-bg-convergence/bg4-warmup-completed-review.json`에 fresh raw/config/model 및
workload contract 검증을 보존했다. Launcher와 verifier exit 0이며 warmup_passes만
2→4로 변경되었다. 사전 선언한 5% 기준에서 다음 네 metric이 모두 PASS다.

| Metric | Warmup2 | Warmup4 | 변화 |
|---|---:|---:|---:|
| Mean kernel latency (ns/frame) | 2,469,868 | 2,466,058 | −0.1543% |
| Median latency (ns) | 2,457,696 | 2,455,808 | −0.0768% |
| Foreground throughput (frame/s) | 404.8531 | 405.4831 | +0.1556% |
| DRAM/useful ratio | 2.755396 | 2.749944 | −0.1978% |

이 결과는 baseline CPU4 background의 warmup edge에 한정한다. Length convergence는
NOT_RUN이며 사용자의 현재 두 결과만 검증 요청에 따라 frames8은 시작하지 않았다.
IRQ capture protocol은 PASS이나 일반 환경 capture PARTIAL과 policy NOT_EVALUATED는 유지한다.
Baseline service는 terminal PASS, mesh CPU4 service는 아직 실행 중이다.


### 최종 마무리 — 2026-11-02 00:01 KST

사용자의 20분 마무리 제한에 따라 남은 mesh CPU4 service를 timer로 중단했다.
Service inactive/dead 및 PID 90682 소멸을 확인했다. Baseline CPU4는 앞서 terminal PASS와
warmup 네 gate PASS를 확인했다. 추가 실행이나 재시작은 하지 않았다.

Mesh CPU4는 warmup tick 693832872000, ROI begin 739445889000,
ROI end 752700896000까지 기록했지만 최종 result.json과 verifier 완료가 없다.
따라서 **INCOMPLETE_USER_TIME_LIMIT**이며 benchmark FAIL 또는 PASS로 분류하지 않는다.
성능 비교 수치를 확정하지 않는다. Systemd의 Result=success는 stop 동작의 상태일 뿐
benchmark 성공을 뜻하지 않는다.

Evidence: `V/recovery-20261101/nominees/mesh-bg4-user-time-limit-review.json`.
Raw UART/ROI/stats 존재 여부와 SHA256, 마지막 ledger를 보존했다. 기존 output은 덮어쓰지 않았다.
재실행 시 새 output directory와 당시 입력 호환성을 확인해야 한다.

이번 세션은 여기서 마무리한다. 전체 P0–P6는 미완료이며 위 후속 항목을 다음 작업으로 남긴다.
Commit/push 및 별도 archive 복사는 하지 않았다. 문서 local file links 105개와
`git diff --check`는 PASS이며 runtime 성공을 대신하지 않는다.

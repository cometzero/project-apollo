# 변경 계획 구현 및 검증 — 2026-10-30

## 구현 범위

[soc_spec_policy.py](../../../../scripts/gem5/soc_spec_policy.py)는 기존 collector를 재사용해
숫자 실행 예산, immutable output, source/input pin, serial/no-retry 실행과 paired assessment를
추가한다. [Implementation](implementation.md#2026-10-30--bounded-policy와-paired-assessment)의
CLI와 schema를 따른다. 원본 campaign의 판정은 소급 변경하지 않는다.

Primary metric의 warmup/length 수렴, explanatory counter, 모델 신뢰성, 독립 validation,
제품 판정을 분리한다. Uncertainty 좌표는 resolved profile/config와 대조한다. 같은 좌표를
서로 다른 조건으로 중복 등록하거나, workload/input 변경을 hardware 효과로 비교하는 것을
거부한다. 조건 간 design delta/software/workload가 다르면 robustness는 INCONCLUSIVE다.

## 실제 artifact 재집계

`build/qbox-apollo-qvp/gem5/literature-implementation-20261030/assessment-v3.json`은
기존 raw evidence를 재검사한 post-hoc 분석이다. 새로운 simulation sample이 아니다.

| CPU clock | Fabric 2 GHz median latency | Fabric 1 GHz median latency | Latency 증가 |
|---|---:|---:|---:|
| 2 GHz | 2,411,412 ns | 3,144,012 ns | 약 30.4% |
| 1 GHz | 3,070,372 ns | 3,757,796 ns | 약 22.4% |

두 CPU 공급 조건에서 fabric clock 감소의 불리한 방향은 유지되지만 영향 크기는 다르다.
해당 640×480 image kernel/pool2 조건의 결과이며 전체 automotive workload로 일반화하지
않는다. 분석의 gain은 T_baseline/T_candidate−1이므로 위 latency 증가율과 숫자가 다르다.
독립 validation과 model credibility는 NOT_ESTABLISHED, 제품 판정은 UNDECIDED다.

첫 재집계는 기존 비교 선언에 effective network clock path가 빠져 UNDECIDED였다.
Post-hoc campaign-v2에 `system.ruby.network.clk_domain.clock.0` 변경을 명시하고 재검사했다.
원본 campaign과 첫 거부 결과를 보존했다.

## 실제 실행에서 확인한 collector 수정

기존 P4 continuation은 CPU1/mesh1/combined/channel8 수렴 통과 후 SLC8+channel8의
DRAM/useful ratio 수렴 실패로 종료했다. 두 마지막 candidate의 terminal review를 완료했다.
이후 P2 memory-followup1을 최대6 run/24시간 systemd service로 실행했으나 첫 cache32
실행의 collector에서 종료 marker 오류를 발견해 queue가 중단했다.

내장 `benchmark.c`의 cache/dram 경로는 checked result를 출력한 뒤 직접 m5 exit한다.
따라서 shell completion marker가 없는 것이 정상이다. `soc_spec.py`는 이 두 경로에서
기존 raw result/checksum/host=false/ROI/normal process completion 검증을 사용하도록 수정했다.
그 외 workload는 shell exit marker를 계속 요구한다. Guest/image/native 변경은 없다.
기존 실패 artifact는 유지하고 수정 collector의 별도 review에서 cache32가 VALID임을 확인했다.
측정값은 **2.54248046875 ns/dependent-load**이며 HW latency 일치 주장이 아니다.

나머지 cache128/1024/8192 KiB는 새 `cache-policy.json`에 original passes2/warmup1을
유지해 등록했다. 최대3 run/3600초, 각 command1200초, source/input224개 pin,
first nonPASS stop이며 실행 결과는 `cache-execution/`에 남긴다.
Service: `apollo-gem5-policy-cache-20261030.service`. 실행 상태는 artifact/service에서 확인한다.
이 문서는 시작을 기록하며 완료 PASS를 미리 선언하지 않는다.

## 검증과 남은 범위

Host regression: `test_soc_spec*.py` **49 PASS**. Timeout/first failure 이후 NOT_RUN,
기존 output·pin 변조 거부, uncertainty mismatch, sign reversal, primary/counter 분리,
내장 guest direct-exit 및 다른 workload의 missing marker 거부를 포함한다.

Orin SSH는 `No route to host`로 실패했다. 새 reference/calibration 측정은 NOT_RUN이며
원격 설정을 바꾸지 않았다. P5/P6, 독립 workload validation, 새로운 uncertainty corner의
guest 실행 및 전체 41-ID audit은 미완료다. 이번 구현을 전체 P0–P6 완료로 해석하지 않는다.

후속: Orin 재접속 후 [2026-10-30 reference 측정](orin-reference-20261030.md)을 수행했다. 기존 접속 실패 기록은 보존하며, 새 54회 측정 및 설정 복원은 PASS다. PMU/model calibration은 별도다.

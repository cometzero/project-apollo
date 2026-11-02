# 병목 가설의 현재 evidence — 2026-10-31

상태: **interim / 전체 완료 아님**. 제품 `UNDECIDED`, silicon 보정 미수행.
현재 source의 `soc_spec.py report`로 recovery campaign의 memory case를 재집계했다.
기존 9개 raw 측정과 추가 warmup4 및 measured4/warmup2 측정은 VALID이다. Current host policy의
source 변경 없이 수집했다. Validity가 numerical stability나 hardware credibility를 뜻하지 않는다.

## Memory 관측값

| 조건 | Useful GB/s | Raw 상태 |
|---|---:|---|
| read-w16-p2-wu1-s64-schema3 | 40.904856 | VALID |
| read-w1-p2-wu1-s64 | 3.765120 | VALID |
| read-w4-p2-wu1-s64 | 13.026127 | VALID |
| read-w8-p2-wu1-s64 | 23.137202 | VALID |
| read-w16-p2-wu1-s512 | 34.496958 | VALID |
| read-w16-p2-wu1-s1024 | 33.105921 | VALID |
| copy-w16-p2-wu1-s64 | 21.894869 | VALID |
| triad-w16-p2-wu1-s64 | 32.598437 | VALID |
| read-w16-p2-wu2-s64 | 38.677699 | VALID |
| read-w16-p2-wu4-s64-20261031 | 37.472453 | VALID |
| read-w16-p4-wu2-s64-20261031 | 38.717779 | VALID |

Read/copy/triad는 useful-byte 정의와 instruction mix가 다르므로 이 표를 같은 작업의
순위로 해석하지 않는다. Warmup1/2의 read useful bandwidth 차이는 기존5% 기준을
벗어났다. 추가 warmup2→4 비교에서는 useful GB/s −3.116%, DRAM GB/s −3.512%,
DRAM/useful ratio −0.409%로 세 지표 모두 5% gate를 통과했다. 이를 근거로 warmup2를
유지한 measured passes2→4 검증도 완료했다. Useful GB/s +0.104%, DRAM GB/s −0.095%,
DRAM/useful ratio −0.199%로 세 지표 모두 5% gate PASS다. 이 read 조건의
warmup·length 안정성 근거이며 다른 worker/stripe/kernel 조건으로 전이하지 않는다.

## 가설별 판정

| 가설 | 현재 판정 | 근거와 한계 / 다음 확인 |
|---|---|---|
| 이 read에서 worker 수 증가가 공급량을 늘린다 | 관측 범위에서 SUPPORT | workers1/4/8/16에서3.77/13.03/23.14/40.90GB/s. 총64MiB 고정이라 worker당 footprint·cluster/cache 사용도 함께 변함. 순수 core scalability 증거가 아님 |
| 이 read에서64-B stripe가512/1024-B보다 유리하다 | 관측 범위에서 SUPPORT, 안정성 보류 | 같은16 workers에서40.90/34.50/33.11GB/s. 보편적인 최적 interleave 또는 DRAM peak 성능으로 일반화하지 않음 |
| image 성능은 CPU와 mesh clock에 독립적으로 비례한다 | 단순 독립 가정 REFUTE | 검증된 four-corner arithmetic mean의 additive interaction −48,380ns. CPU/private controller와 mesh의 실제 domain 범위를 유지한 모델 결과 |
| 큰 L3/SLC의 solo 개선은 안정된 cache-size 이득이다 | UNRESOLVED | 관측 mean은 크게 감소하지만 warmup gate FAIL. SLC×channels interaction도 NOT_ACCEPTED. 실패한 sample을 낮은 점수나 합격 후보로 치환하지 않음 |
| image pool2에서8채널은16채널을 대체할 수 있다 | 제품 판정 UNDECIDED | 기존 converged solo mean은 약1.38% 느림. 새 envcapture solo도 mean +1.389%, throughput −1.370%이며 channel-only config delta 일치. 같은 CPU1 background에서도 mean +1.256%이며 channel-only config delta 검증 PASS. 같은 CPU4 background도 mean +1.539%로 관측됨. 후보 scenario 수렴·PPA·제품 margin 검증은 남으며 held-out 결과는 아래와 같이 별도 해석 |
| 후보 순위가 작은 footprint에서도 유지된다 | NOT_ESTABLISHED | Pool1 두 설계 VALID: channels8/baseline mean ratio0.998645, pool2 ratio1.013892와 관측 부호가 바뀜. 작은 차이이며 pool1 수렴·repeatability 미확립으로 robust reversal 판단 불가. 사전 선언한 same-kernel footprint 검증이며 independent-kernel validation 아님 |
| CPU1 background가 CPU0 image 처리에 간섭한다 | 관측 범위에서 SUPPORT, 안정성 보류 | 새 envcapture2 solo 대비 mean kernel latency +2.171%, median frame latency +2.506%. Background가 마지막 foreground frame 종료까지 실행된 것을 확인. Baseline의 warmup·length gate는 PASS. 반복 측정과 environment policy 판정은 미완료 |
| CPU4 background가 CPU0 image 처리에 간섭한다 | 관측 범위에서 SUPPORT, 안정성 보류 | 새 envcapture2 solo 대비 mean kernel latency +1.652%. CPU4의 background worker 1개이며 마지막 foreground 종료까지 실행됨. CPU1 대비 mean은 작지만 반복·scenario convergence 없이 placement 순위를 확정하지 않음 |
| CPU background가 외부 accelerator/DMA traffic을 대표한다 | UNSUPPORTED | P5는 CPU background 실험. 외부 IP는 trigger/연결/traffic 근거가 없어 CONDITIONAL_NOT_TRIGGERED |

## 재현과 범위

Evidence root는 `build/qbox-apollo-qvp/gem5/verification-20261031/`이다.
`memory-inventory-campaign.json`은 original recovery case의 absolute run/report 경로를
고정하고, `memory-inventory`는 raw inventory, `memory-inventory-summary.json`은 그 hash와
표의 값을 보존한다. 재집계는 다음 command에 새 output 경로를 지정한다.

```sh
/usr/bin/python3 -E -B scripts/gem5/soc_spec.py report \
  build/qbox-apollo-qvp/gem5/verification-20261031/memory-inventory-campaign.json \
  --output /tmp/apollo-memory-review-new.json
```

기존 output을 덮어쓰지 않는다. P4 interaction은 `p4-current-result-v2.json`, 후보 지명은
`screening-nomination.json`, held-out 역할은 `heldout-pool1/role.json`에 있다.
추가 warmup gate는 `p2-read-followup/completed-review.json`, length gate는
`p2-read-length/completed-review.json`, CPU1 background 비교는
`p5-bg1-completed-review.json`, CPU4 비교는 `p5-bg4-completed-review.json`에 보존했다. 기존 memory inventory를 덮어쓰지 않았다.
CPU1 비교의 PASS는 입력·결과 비교의 유효성이고 numerical stability 판정이 아니다.
Channels8 새 solo 비교는 `p5-channels8-solo-completed-review.json`에 보존했다.
Channels8 CPU1 background는 `recovery-20261101/nominees/bg1-completed-review.json`에 보존했다.
동일 background의16-channel 대비 mean +1.256%,8-channel solo 대비 +2.036%이며
posthoc 비교다. Numerical stability와 environment policy 판정은 아직 미완료다.
새 baseline image의 warmup2→4 네 metric은 PASS이며
`p5-solo-convergence/warmup-completed-review.json`을 따른다. Frames4→8도 네 metric 모두 PASS다
(`recovery-20261101/frames8/length-completed-review.json`). Mean kernel time −0.196%,
median frame latency +0.020%, FPS +0.195%, DRAM/useful ratio −1.408%다.
Baseline solo와 CPU1 background의 두 convergence gate를 완료했다. CPU4·후보·held-out 조건은 별도 검증이 필요하다.
Aggregate DRAM bandwidth에는 foreground와 background가 모두 포함된다.
상세 실행 상태는 [검증 기록](verification-20261031.md)을 따른다. 최종 decision record와
전체 requirement completion audit는 아직 완료하지 않았다.

Channels8 CPU4 background의 fresh comparison은 `recovery-20261101/nominees/bg4-completed-review.json`에 보존했다. Scenario convergence 미완료로 CPU1/CPU4 placement 우위를 확정하지 않는다.

Baseline CPU1 background의 warmup2→4 네 metric gate는 PASS
(`p5-bg-convergence/bg1-warmup-completed-review.json`). Frames4→8도 네 metric PASS다
(`p5-bg-convergence/bg1-length-completed-review.json`): mean +1.3413%, median +0.1252%,
FPS −1.3237%, DRAM/useful ratio +3.4496%.
해당 warmup 안정성을 후보8-channel·CPU4 placement·pool1 조건으로 전이하지 않는다.


Mesh 2→1GHz의 fresh matched comparison은 solo mean +30.2666%, CPU1 background
mean +33.3883%를 보였다. 각각 `recovery-20261101/nominees/mesh-solo-completed-review.json`과
`mesh-bg1-completed-review.json`에 보존했다. 해당 후보 scenario convergence는 미확립이며
이 두 관측치만으로 interaction이나 robust ranking을 확정하지 않는다.

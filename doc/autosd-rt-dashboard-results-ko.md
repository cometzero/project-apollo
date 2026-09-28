# RT 관찰 기준 및 대시보드 결과 표시

## 기존 초과 원인

대시보드의 04(PREEMPT_RT), 05(Timerlat), 06(OS noise)는 기존 1000µs 예시 기준을 사용했다.
이는 차량 요구사항에서 도출한 deadline이 아니며, TCG 호스트 스케줄링 및 계측 조건에 영향을 받는다.

| 기존 실행 | 단계 | 최대 지연 (µs) | 기존 기준 (µs) | 측정/지연 판정 |
| --- | --- | ---: | ---: | --- |
| `d434bfc1d2b84364b0c7fdde767f4154` | R01 SCHED_OTHER | 4817.272 | 1000 | 측정 PASS / EXCEEDED |
| `9424be40cb664f8592c234ac5611dc12` | R03 QM 부하 | 1456.008 | 1000 | 측정 PASS / EXCEEDED |

R01은 일반 스케줄러 비교용 baseline이며 RT 스케줄러 합격 여부의 gate로 사용할 수 없다.
R05는 의도적인 지연 주입으로 초과 검출 여부를 확인하는 단계이므로 성능 결과와 합산하지 않는다.

## 변경한 기준

- TCG 실험의 잠정 관찰 기준: **5000µs**. 소수 관찰값으로 정한 운영용 기준이며 통계적으로 검증된 budget이 아니다.
- 04 전체 판정은 R02/R03/R04/R06의 실제 초과 여부를 반영한다. R01 원시 통계와 초과 횟수는 보존한다.
- R01 단독 결과는 `BASELINE_OBSERVATION`, R05 단독 결과는 검출 성공 시 `DETECTION_PASS`.
- 측정 오류·잘못된 정책·mlock 실패·부하 정리 실패·실험 전후 정상 상태 실패는 계속 FAIL 처리한다.
- 실험 CLI의 QBox/hardware 기본 예시 1000µs는 변경하지 않는다. 대시보드는 QBox에도
  기능 관찰용 5000µs를 명시적으로 전달한다. 실제 타깃에는 요구사항으로 정한 값을 `--threshold-us`로 지정해야 한다.
- 05의 5000µs는 Thread trace 중지 기준, 06은 sample trace 중지 기준이다. trace 수집 PASS와 지연 초과 여부는 별개다.
- 과거 실행 결과를 새 기준으로 재채점하지 않는다. 결과에 당시 threshold/플랫폼/판정 정책을 저장한다.

이 해석은 [Linux Timerlat 문서](https://docs.kernel.org/tools/rtla/rtla-timerlat-hist.html)의 `-T`와
[OS noise 문서](https://docs.kernel.org/tools/rtla/rtla-osnoise-hist.html)의 `-s` 의미에 따른다.
AutoSD의 CPU tuning 문서도 환경에 맞춘 검증을 요구한다. 이 변경은 RT throttling,
IRQ priority, CPU affinity 또는 커널 설정을 완화하지 않는다.

## 화면 사용법

1. 04 전체 또는 개별 단계, 05, 06 중 하나를 실행한다.
2. 완료되면 결과 영역이 해당 작업으로 자동 전환된다. Feature 카드의 **결과 보기**로도 이동할 수 있다.
3. 표에서 측정 상태와 지연 판정을 별도로 확인한다. min/mean/max/P99, 표본 수, 실행 기준, 초과 횟수를 제공한다.
4. 04 막대 그래프는 최대 지연과 실행 당시 기준선을 표시한다. R05 합성 지연은 구분한다.
5. 05 Timerlat은 IRQ/Thread/User별 **histogram**으로 표시한다. X=latency(µs), Y=표본 수.
   새 측정은 기준/100을 올림한 bin 폭과 100개 bin을 사용한다(5000µs 기준이면 50µs/bin).
   범위 밖 표본은 독립된 `over` 막대로 표시하며 임의의 지연 위치에 배치하지 않는다.
6. 06 OS noise는 **시간별 latency X/Y 차트**다. X=첫 수집 이벤트 이후 초, Y=noise duration(µs).
   점/선은 CPU별 시간 구간의 최대값이며 세로선은 최소–최대다. 빈 구간은 연결하지 않는다.
   실제 이벤트 timestamp를 사용하며 histogram에서 시간 순서를 추정하지 않는다.
   Y축은 관측 범위에 맞춘다. 실행 기준이 범위를 벗어나면 차트를 압축하지 않고 숫자로 안내한다.
7. 과거 결과는 선택 목록에서 확인한다. 시간 데이터가 없는 기존 OS noise는 재측정 안내를 표시한다.
   새 측정 완료 전에는 수동 선택을 유지한다. 브라우저를 새로고침하면 새 차트가 적용된다.

OS noise는 RTLA와 동시에 독립 tracefs instance의 `osnoise:sample_threshold` 이벤트를
수집한다. 커널 이벤트의 start(ns)를 상대 초로, duration(ns)를 µs로 변환한다.
커널 sampling threshold에서 생성된 이벤트이며, 주기적인 지연 0 표본이 아니다.
CPU당 4 MiB ring, 최대 16 MiB 원본, 최대 5000개 대표점으로 제한한다.
대표점은 전체 보존 시간 구간의 CPU별 peak이며 실제 시각·최솟값·표본 수를 보존한다.
화면에서는 이를 최대 240개 시간 구간/CPU로 집계하고 손실·잘림과 축약 여부를 명시한다.
추가 계측 부하가 있으므로 이전 histogram-only 실행과 동일 조건의 성능 결과로 간주하지 않는다.
원본 `osnoise-samples.txt`와 JSON은 작업의 evidence archive에 포함된다.

RTLA `over`는 histogram 범위를 벗어난 표본 수이며 threshold 초과 횟수가 아니다.
RTLA는 P99를 제공하지 않으므로 이를 추정하지 않는다. 무표본 통계는 `—`로 표시한다.
기존 trace 결과에는 통계가 없을 수 있으며, 새 실행부터 구조화된 통계를 저장한다.
ALL 요약의 중복 표본은 합산하지 않는다.

## 검증

회귀 테스트는 실측값과 판정의 분리, baseline/합성 제외, 실제 RT 초과 유지,
RTLA histogram 형식/단위/합계 검증, 최신 완료 결과 자동 선택과 수동 선택 보존을 포함한다.
Python AutoSD 테스트 256개 및 UI 테스트 22개 PASS. 실제 브라우저에서 세 측정의
자동 선택과 표/SVG를 확인했고, 390px 화면에서 문서 폭 초과 없이 표 내부 스크롤을 유지했다.
RTLA의 전체 trace 초과를 모든 행에 복제하지 않고 각 열의 최대값/기준 비교로 표시한다.
2026-09-27 실제 VM 검증:

| 실행 | 결과 | 근거 |
| --- | --- | --- |
| 04 새 TCG 기준 | PASS | `3da9bcb0fda640619e49971d1d586fab`, 기준 5000µs |
| R01/R02/R03/R04 최대 | 4207.280 / 676.912 / 851.872 / 680.384µs | 실제 probe JSON |
| R05 주입 검출 | DETECTION_PASS | 최대 11520.456µs, 성능 gate 제외 |
| R06 cyclictest | PASS | 최대 698µs, 5000 samples |
| 04 완료 자동 표시 | PASS | 결과 선택 `job:3da9…`, 6행 표와 SVG 그래프 확인 |
| 05 통계 수집/표시 | PASS | `6a2c267e5c584982a1494b31377ec110`, IRQ/Thread/User 각 2343 samples |
| 06 통계 수집/표시 | PASS | `7857f2751ef64dbf9cd256bd924846b2`, 64668 samples, 최대 537µs |

05·06 통계 표시 검증은 재시작 전 서버의 기존 **1000µs** 중지 기준으로 실행했다.
IRQ/Thread/User 최대는 324/804/1034µs, 수집 PASS / 전체 trace EXCEEDED였다.
05·06 새 5000µs 실행 인자는 서버 재시작 후 적용되었다. 기존 결과를 변경하지 않는다.
증거는 `build/autosd/dashboard/20260927-161222-530e591a/<job-id>/`에 보존한다.
이후 QBox AP direct에서 04·05·06을 5000µs로 실행해 수집/표시를 검증했다.
최초 trace 초기화 timeout과 수정 후 재검증 결과는
[QBox AP domain 검증 기록](autosd-qbox-dashboard-ko.md)에 별도 기록한다.

## Histogram / 시간축 차트 검증 (2026-09-27)

현재 QBox AP direct VM에서 서버/VM 재시작 없이 새 guest 수집기를 업로드해 실행했다.

| 작업 | 실제 결과 |
| --- | --- |
| Timerlat `a8583667b04d43acbe83e2f8302023c6` | PASS; 50µs × 100 bin, IRQ/Thread/User 각 4949 samples, over=0, histogram SVG 3개 |
| OS noise `e957dd3975ba41e4ac6bd169c53fec28` | PASS; 4.926809초 구간, 실제 이벤트 14397개 = histogram 표본 수, 유실/잘림 없음 |
| OS noise 축약/표시 | 전체 구간의 대표 peak 553개 → 화면 구간 77개; 원시 최대 약 518µs, Y축 0–600µs |
| trace 정리 | 설정 복구, 소유 instance 제거 확인 |
| 기존 OS noise 결과 | 시간 데이터 없음/재측정 안내; 가짜 시간축 미생성 |
| 브라우저 | 완료 결과 자동 선택, Timerlat 3개 histogram / OS noise X/Y SVG 확인; 390px에서 문서 폭 초과 없이 차트 내부 스크롤 |
| 회귀 검사 | Python 336 PASS, UI 28 PASS, JS syntax 및 diff whitespace 검사 PASS |

작업 증거: `build/autosd/dashboard/20260927-215600-63498895/<job-id>/guest/`.
원본 시간 데이터는 OS noise의 `evidence.tar.gz` 안 `osnoise-samples.txt`에 있다.
스크린샷: `build/autosd/dashboard/timerlat-histogram.png`,
`timerlat-histogram-mobile.png`, `osnoise-time-latency.png`.

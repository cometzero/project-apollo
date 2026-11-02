# Orin reference 재측정 — 2026-10-30

상태: 기본 48회 + 원인 분리 6회, **54회 실행/checksum 검증 PASS**.
이는 workload와 계측 reference이며 A720AE model calibration 또는 silicon 일치 검증이 아니다.

## 입력과 환경

- Jetson AGX Orin, 12 CPUs online, Linux 5.10.120-tegra, Ubuntu 20.04.6.
- MAXN 상태에서 기존 clock 설정 저장 → jetson_clocks 고정 → 측정 → 원래 설정 복원.
- 실행 중이던 `dal-e_ros_can_bridge.service`, `dal-e_state_manager.service`를 중지하고 복원.
  전후 clock 설정 및 service 상태 비교가 모두 일치했고 tegrastats monitor 종료도 확인했다.
- 현재 checkout의 `benchmark.c`, `image_bench.c`, `memory_bench.c`, `common.h`를 복사해
  source SHA256 일치 확인. GCC 9.4.0, `-std=c11 -O2 -Wall -Wextra -Werror -pthread -I.`.
- `--host`의 CLOCK_MONOTONIC_RAW 내부 ROI 사용. Cache/image foreground는 CPU0.
  Memory는 workers1/4/8/12, read NEON, array64MiB, passes2/warmup1이다.
- Yocto guest와 source 의미는 맞췄지만 compiler/binary/OS/CPU/cache/DRAM은 동일하지 않다.
  `perf` 실행파일이 없어 PMU counter 비교는 NOT_RUN이다.
- 조건당 독립 실행3회. 아래 숫자는 세 실행의 대표값에 대한 median이며 신뢰구간이 아니다.

## Cache와 측정 길이

| Working set | Matched: passes2/warmup1, ns/load | Longer: passes256/warmup4, ns/load |
|---|---:|---:|
| 32 KiB | 1.875 | 1.7180 |
| 128 KiB | 5.6719 | 5.3809 |
| 1 MiB | 7.9658 | 8.0369 |
| 8 MiB | 126.1693 | 74.5272 |

32/128KiB/1MiB/8MiB를 각각 특정 cache level의 순수 hit latency라고 단정하지 않는다.
128KiB long 조건은 5.2828–9.1570 ns/load로 반복 간 변동이 컸다. Median 하나만 보고
안정적이라 판단하지 않는다. 작은 working set의 짧은 ROI에는 timer/barrier overhead도 포함된다.

8MiB에서 두 factor를 분리한 추가6회 결과:

| Passes | Warmup | Median ns/load | 실행3회 min–max |
|---:|---:|---:|---:|
| 2 | 1 | 126.1693 | 124.6403–131.2634 |
| 2 | 4 | 85.2281 | 75.8311–94.8699 |
| 256 | 1 | 75.8066 | 75.2613–77.7835 |
| 256 | 4 | 74.5272 | 73.4007–76.7946 |

추가 controls는 별도 clock 설정/복원 batch에서 실행했다. 큰 차이를 단일 원인에 모두
할당하지 않는다. 다만 같은 passes2에서 warmup 변경, 같은 warmup에서 passes 변경 모두
영향이 관측됐다. Passes256에서 warmup1/4의 median 차이는 약1.7%지만, measured256→512
비교는 하지 않았으므로 완전한 steady-state 수렴 PASS가 아니다.

**후속 gem5 정책:** 기존 passes2/warmup1 결과는 그대로 보존한다. 8MiB의 짧은 결과만으로
cache/DRAM 대표 latency를 확정하지 않는다. 별도 pilot 예산에서 warmup과 측정 길이를
각각 변화시킨 뒤 채택 여부를 결정한다. Orin의 256passes를 비용 검토 없이 gem5에 복제하지 않는다.

## Memory 및 독립 image kernel

| Read workers | Useful GB/s median |
|---:|---:|
| 1 | 13.128 |
| 4 | 21.626 |
| 8 | 42.492 |
| 12 | 62.535 |

이는 해당 NEON/read/working-set/affinity의 달성값이며 Orin DMC 최대 bandwidth가 아니다.
전체64MiB를 worker별로 나누므로 core 공급량과 per-worker footprint 효과가 함께 바뀐다.

| Image 조건 (640×480, warmup4) | Median frame latency |
|---|---:|
| frames4, pool2 | 0.852240 ms |
| frames8, pool2 | 0.838336 ms |
| frames128, pool2 | 0.838144 ms |
| frames128, pool16 | 0.840432 ms |

Image는 cache/read와 다른 kernel의 reference 검사다. 출력 원소 검증은 모두 PASS이고
pool2 output hash는 gem5의 `d22a30a02c070a81`과 일치했다. 작은 frame sample의 observed
maximum을 p99/WCET로 해석하지 않는다. 이 자료로 gem5의 A720AE 절대 속도를 보정하지 않는다.

## Evidence와 실행 중 오류

Local: `build/qbox-apollo-qvp/gem5/orin-reference-20261030/`.
`raw-r2/`는 기본48회, `raw-controls/`는 추가6회다. 각 디렉터리에 source/binary hash,
실행 argv/raw log, compiler, hardware before/fixed/after, clock/service 복원 evidence가 있다.
`summary.json`, `controls-summary.json`에 반복별 범위를 집계했다.

첫 시도는 memory result에 없는 `host` 필드를 수집기가 요구해 중단했다. Memory의 host
증거는 `CMN_HOST_ROI`에 있으므로 해당 marker의 host/clock을 검사하도록 수정했다.
Benchmark source는 변경하지 않았고 첫 시도도 설정 복원을 완료했다. 첫 시도 결과와 로그는
`raw-first-attempt/`에 보존했으며 최종54회 집계에 섞지 않았다.

제품 목표/모델 credibility/PMU 기반 원인 분리/전체 P5–P6 완료 판정은 여전히 미확정이다.


## 2026-10-31 추가 measured-length 검증

Orin 재접속 후 8MiB cache, CPU0, warmup4에서 passes256/512를 각각3회
교대로 실행했다. 기존 source와 GCC/O2 build 절차를 재사용하고 source SHA256 일치를
확인했다. 실행 전 5% median 변화 기준을 `predeclared-policy.json`에 고정했다.

| Passes | Median ns/load | 실행3회 min–max ns/load |
|---:|---:|---:|
| 256 | 75.505630 | 73.484419–78.077252 |
| 512 | 75.000171 | 74.088964–79.374962 |

Median 변화율은 **−0.6694%**, 측정 길이 gate **PASS**다. 6회 checksum PASS,
benchmark batch23.34s이며 clock 및 기존 service 상태 복원 비교도 PASS다.
현재 active였던 ROS CAN bridge를 복원했고, inactive service를 새로 활성화하지 않았다.

이 gate는 같은 batch의 median에 한정한다. 반복 범위가 겹치며 변동도 남아 있으므로
개별 실행 안정성·통계적 동등성·warmup 수렴 또는 gem5 수렴을 증명하지 않는다.
이전 warmup1/4 비교는 다른 batch이며 함께 묶어 전체 steady-state PASS로 승격하지 않는다.
PMU는 여전히 NOT_RUN이고 A720AE model calibration은 수행하지 않았다.

Evidence: `build/qbox-apollo-qvp/gem5/orin-length-20261031/summary.json`,
`predeclared-policy.json`, `raw/results.jsonl`, `raw/manifest.json`,
`raw/clocks-{before,after}.conf`, `raw/ros-{before,after}.txt`.
기존54회 기록은 변경하지 않고 이번6회를 별도로 보존했다.

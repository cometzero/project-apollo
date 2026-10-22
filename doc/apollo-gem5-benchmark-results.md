# Apollo gem5 Linux cache benchmark

상태: **PASS**. 최종 v4 이미지·snapshot에서 세 도구의 O3 측정을 완료했다.

## 실행 조건

- MACHINE `apollo-qvp`, DISTRO `auto-ad-nexios`, Linux 6.18.5-rt3.
- AP-only gem5, 4 CPUs, A720AE documented O3 proxy, CPU0 affinity.
- Atomic boot checkpoint를 복원한 뒤 O3로 전환한다.
- L1D 64KiB/core, L2 512KiB/core, DSU L3 4MiB, SLC proxy 총4MiB,
  LPDDR5X 16channels. 실리콘 보정 또는 물리 하드웨어 검증 결과가 아니다.
- 도구 출력의 내부 측정 시간과 gem5 전체 명령 ROI를 구분한다.
  후자에는 fork/exec, 커널 처리, 할당·초기화, 보정과 실제 시험이 포함된다.
- lmbench와 tinymembench는 반복1회로, 반복 간 분산을 검증한 결과가 아니다.

| 도구 | 명령 | 조건 |
|---|---|---|
| modified lmbench | `lat_mem_rd -N 1 -E 200 1 64` | 512B~1MiB 21크기, stride64B, 표본 목표200µs |
| tinymembench | `tinymembench --bandwidth-size-kib 16 --latency-size-kib 1024 --duration-ms 1 --repeats 1 --latency-count 16384` | bandwidth 버퍼16KiB, latency1KiB~1MiB |
| STREAM-derived | `stream-gem5-cache` | 65536 doubles ×3 =1.5MiB, 10회, 첫 회 제외 최선값 |

`-E`는 lat_mem_rd 전용 확장이다. 지정하지 않으면 원본100ms 목표와 보정
동작을 유지한다. 지정하면 ENOUGH를 같은 값으로 설정해 긴 interval 탐색을
생략하며 timer/loop overhead 실측은 유지한다. 원본 기본 조건 점수와 구분한다.

## 측정 결과 (2026-10-22)

세 실행 모두 **PASS**: snapshot 복원, CPU0 고정, O3 전환, 정상 종료,
ROI tick/statistics 일치를 확인했다. STREAM은 자체 numerical validation도 통과했다.
최종 이미지 빌드는 4,167 tasks 성공(4,137 재사용), 기존 kernel forced-task
경고2개였다. 옵션 회귀42개·결과 수집기4개·control4개 검사를 통과했다.

| 단계 | 호스트 시간 | 전체 명령 ROI guest 시간 |
| --- | --- | --- |
| snapshot 저장 | 1682.36s | — |
| lmbench | 844.50s | 46.222ms |
| tinymembench | 1567.75s | 48.972ms |
| stream | 484.55s | 8.357ms |

세 측정은 독립 프로세스로 병렬 실행했다. 위 호스트 시간은 성능 점수의 분모가 아니다.

### 지연 비교

| Working set | lmbench 절대 ns/load | tinymembench single 추가 ns |
| --- | --- | --- |
| 16KiB | 2.493 | 0.2 |
| 32KiB | 2.598 | 0.6 |
| 64KiB | 7.131 | 1.3 |
| 128KiB | 12.976 | 6.4 |
| 256KiB | 12.988 | 9.5 |
| 512KiB | 16.159 | 14.2 |
| 1024KiB | 23.415 | 20.9 |

lmbench는 32KiB 2.598ns에서 1MiB 23.415ns로
약 9.01배 증가했다. 128~256KiB는 약13ns,
768KiB~1MiB는 약23.4ns다. tinymembench도 working set 증가에 따라
추가 지연이 커지는 경향을 보인다. 두 지연값은 정의가 다르므로 직접 빼거나
같은 척도의 순위로 비교하지 않는다.

설정상 L1D는64KiB지만 lmbench는48KiB부터 증가했다. 이 단일 실행만으로
원인을 특정하거나 캐시 용량을32KiB라고 역추정할 수 없다. 주소 배치·set conflict,
커널/코드 작업 집합 등의 영향을 분리하려면 추가 시험이 필요하다.

### 대역폭 비교

| 도구/커널 | 도구 출력 GB/s | 논리적 read+write GB/s | Working set |
| --- | --- | --- | --- |
| tinymembench libc memcpy | 18.1087 | 36.2174 | source16KiB + destination16KiB |
| tinymembench NEON LD1/ST1 copy | 21.3199 | 42.6398 | source16KiB + destination16KiB |
| STREAM Copy | 10.5977 | 10.5977 | 배열 합계1.5MiB |
| STREAM Scale | 10.7008 | 10.7008 | 배열 합계1.5MiB |
| STREAM Add | 10.6233 | 10.6233 | 배열 합계1.5MiB |
| STREAM Triad | 10.5553 | 10.5553 | 배열 합계1.5MiB |

tinymembench NEON LD1/ST1 copy는 같은16KiB 버퍼 조건의 libc memcpy보다
약 17.7% 높았다.
이는 단일 반복 결과이며 일반적인 구현 우열을 보장하지 않는다.
STREAM은 훨씬 큰 working set이므로 두 도구의 대역폭 차이를 도구 성능 순위로
해석하지 않는다. read+write 환산은 유효 payload 기준이며 coherence·writeback·
임시 버퍼 등을 포함한 실제 버스 트래픽이 아니다.

STREAM의 timer quantum은1µs이고 네 kernel의 최소 시간은
98~149µs로
20tick 기준을 모두 충족했다. tinymembench latency는16384회 접근으로
1µs timer의 양자화가 접근당 약0.061ns이며, 출력은0.1ns 단위다.
단일 반복·baseline 차감·스케줄링 등 추가 오차를 없애는 것은 아니다.

### 전체 명령 캐시 통계

다음 비율은 각 레벨의 hits/(hits+misses)이며 계층마다 분모가 다르다.
초기화·보정·커널 처리도 포함하므로 시험 커널만의 hit ratio로 사용하지 않는다.

| 도구 | L1 hit | L2 hit | L3 hit | SLC proxy hit |
| --- | --- | --- | --- | --- |
| lmbench | 91.23% | 60.20% | 86.14% | 30.30% |
| tinymembench | 98.56% | 26.60% | 22.68% | 46.19% |
| stream | 18.51% | 2.14% | 91.81% | 43.91% |

## 전체 출력 표

### lmbench

| Working set KiB | 절대 ns/load |
| --- | --- |
| 0.5 | 2.498 |
| 1.0 | 2.498 |
| 2.0 | 2.498 |
| 3.0 | 2.556 |
| 4.0 | 2.498 |
| 6.0 | 2.498 |
| 8.0 | 2.49 |
| 12.0 | 2.49 |
| 16.0 | 2.493 |
| 24.0 | 2.495 |
| 32.0 | 2.598 |
| 48.0 | 6.855 |
| 64.0 | 7.131 |
| 96.0 | 9.512 |
| 128.0 | 12.976 |
| 192.0 | 13.024 |
| 256.0 | 12.988 |
| 384.0 | 13.75 |
| 512.0 | 16.159 |
| 768.0 | 23.415 |
| 1024.0 | 23.415 |

### tinymembench bandwidth

| 구현 | MB/s |
| --- | --- |
| C copy backwards | 14887.8 |
| C copy backwards (32 byte blocks) | 20190.7 |
| C copy backwards (64 byte blocks) | 20190.7 |
| C copy | 15872.7 |
| C copy prefetched (32 bytes step) | 15887.0 |
| C copy prefetched (64 bytes step) | 15887.0 |
| C 2-pass copy | 7503.3 |
| C 2-pass copy prefetched (32 bytes step) | 7556.6 |
| C 2-pass copy prefetched (64 bytes step) | 7442.9 |
| C fill | 31883.2 |
| C fill (shuffle within 16 byte blocks) | 21092.9 |
| C fill (shuffle within 32 byte blocks) | 21092.9 |
| C fill (shuffle within 64 byte blocks) | 31753.7 |
| standard memcpy | 18108.7 |
| standard memset | 31554.2 |
| NEON LDP/STP copy | 15887.0 |
| NEON LDP/STP copy pldl2strm (32 bytes step) | 15577.2 |
| NEON LDP/STP copy pldl2strm (64 bytes step) | 15901.4 |
| NEON LDP/STP copy pldl1keep (32 bytes step) | 15887.0 |
| NEON LDP/STP copy pldl1keep (64 bytes step) | 15962.8 |
| NEON LD1/ST1 copy | 21319.9 |
| NEON STP fill | 31977.4 |
| NEON STNP fill | 31999.3 |
| ARM LDP/STP copy | 15887.0 |
| ARM STP fill | 17956.2 |
| ARM STNP fill | 18118.1 |

### tinymembench latency

| Working set KiB | Single 추가 ns | Dual 추가 ns |
| --- | --- | --- |
| 1 | 0.0 | 0.3 |
| 2 | 0.0 | 0.4 |
| 4 | 0.0 | 0.4 |
| 8 | 0.1 | 0.4 |
| 16 | 0.2 | 0.3 |
| 32 | 0.6 | 0.4 |
| 64 | 1.3 | 0.4 |
| 128 | 6.4 | 8.6 |
| 256 | 9.5 | 11.4 |
| 512 | 14.2 | 13.5 |
| 1024 | 20.9 | 20.4 |

## 재현

```sh
./yocto_build.sh --gem5 --keep-conf
./run_gem5_linux.sh --headless \
  --checkpoint build/qbox-apollo-qvp/gem5/linux-benchmarks-v4-snapshot

./run_gem5_linux.sh --headless \
  --resume build/qbox-apollo-qvp/gem5/linux-benchmarks-v4-snapshot \
  --workload command \
  --command 'gem5-control run lat_mem_rd -N 1 -E 200 1 64'
```

이미 존재하는 checkpoint 디렉터리는 덮어쓰지 않는다. 재생성 시 새 경로를
선택한다. 같은 방식으로 다른 두 명령을 `gem5-control run` 뒤에 지정한다.
최종 이미지 또는 모델 설정을 바꾸면 기존 snapshot과의 해시 검증이 실패한다.

## 해석 기준

- lmbench는 의존적인 pointer chase의 **절대 ns/load**를 출력한다.
- tinymembench latency는 baseline을 차감한 **추가 지연**이다. 0.0은
  실제 무지연이 아니라 차감·clamp·타이머 양자화의 결과일 수 있다.
- tinymembench Copy는 복사한 바이트만 세고 STREAM Copy는 읽기+쓰기를
  합산한다. 단위를 맞추려면 전자의 copy 대역폭을2배 해야 한다.
- 양쪽 bandwidth의 working set과 구현이 다르므로 도구 간 수치를 CPU의
  성능 순위로 해석하지 않는다. STREAM 축소판은 공식 DRAM STREAM 점수가 아니다.
- STREAM은 종료 코드 외에 `Solution Validates:`와 유한한 양수 결과를
  확인한다. 1µs timer 기준 표본20tick 미만은 LOW_RESOLUTION으로 표시한다.
- 전체 ROI cache hit ratio는 시험 커널만의 hit ratio가 아니다.

## 증거

`build/qbox-apollo-qvp/gem5/` 아래:

- `benchmarks-v4-image-build.log`, `benchmarks-v4-image-inspection.json`
- `benchmarks-v4-checkpoint-save/`, `linux-benchmarks-v4-snapshot/`
- `benchmarks-v4-{lmbench,tinymembench,stream}/`: UART, platform log,
  `launch.json`, `result.json`, `m5out/roi-events.json`, `stats.txt`, `config.json`
- `scripts/gem5/summarize_tools.py`가 측정 조건, 출력 완전성, ROI tick 일치를 검증한다.

앞선 v3에서는 STREAM과 tinymembench가 완료됐다. 원본 lmbench 실행은
사용자가 측정 시간 옵션 추가를 선택하여 중단했으며 성공 측정으로 집계하지 않는다.

최종 통합 증거: `build/qbox-apollo-qvp/gem5/benchmarks-v4-verification.json`.
각 도구의 `measurement.json`과 `benchmarks-v4-*.csv`에 전체 수치를 저장했다.

이미지: `/build/arm/arm-auto-solutions/build/tmp_baremetal/deploy/images/apollo-qvp/nexios-gem5-initramfs-apollo-qvp-20261022031446.cpio.gz`

이미지 SHA256: `2e29bebd1186c7788917c211159e5b93899abc02e314d58be512e77d7f5872d8`

# Jetson AGX Orin에서 benchmark 정합성 확인

시험일: **2026-10-23**. 접속 대상은 `ssh orin`이다.

판정은 **benchmark 실행·checksum·ROI 계측 PASS**다. 기존 gem5 initramfs의
lmbench, tinymembench, STREAM executable과 runtime library를 그대로 실행했고,
내장 benchmark에는 hardware timer와 host 전용 12-worker 지원을 추가했다.
Orin의 실제 silicon에서 측정한 결과지만 Apollo/Thor model calibration 완료를 뜻하지 않는다.

## 1. Hardware와 gem5 조건

| 항목 | 측정한 Orin | 기존 gem5 interleave 시험 |
|---|---|---|
| Board / SoC | Jetson AGX Orin Developer Kit / Tegra234 | Apollo AP-only proxy |
| CPU | Cortex-A78AE, 12 cores | A720AE proxy, 16 O3 cores |
| Cluster 구성 | 4 cores × 3; CPU 0–3 / 4–7 / 8–11 | 4 cores × 4 |
| CPU clock | 고정 조건 2.2016 GHz | 2 GHz |
| L1I / L1D | core당 각각 64 KiB | core당 각각 64 KiB |
| Private L2 | core당 256 KiB | core당 512 KiB |
| Shared L3 | cluster당 2 MiB, 합계 6 MiB | cluster당 4 MiB, 합계 16 MiB |
| Memory | 64 GB 제품, OS 표시 약 61 GiB | 2 GiB aperture |
| DRAM 공개 사양 | 256-bit LPDDR5, 최대 204.8 GB/s | 16 × x16-bit LPDDR5X-8533 proxy |
| EMC clock 표시 | 고정 조건 3199 MHz | native DRAM timing parameter |
| Prefetch | hardware 상태를 변경하거나 비활성화하지 않음 | profile에서 disabled |
| OS | Ubuntu 20.04.6, Linux 5.10.120-tegra | 전용 Yocto initramfs |
| BSP | L4T R35.4.1 | `apollo-qvp` / `auto-ad-nexios` |

CPU/cache/clock/OS는 보드에서 직접 확인했다. L4T package는 설치되어 있으나
`nvidia-jetpack` metapackage는 조회되지 않아 설치된 SDK 전체를 특정 JetPack 버전으로
단정하지 않는다. DRAM 폭과 최대 bandwidth는
[NVIDIA 공개 사양](https://www.nvidia.com/en-au/autonomous-machines/embedded-systems/jetson-orin/)이다.
EMC clock 표시와 DRAM data rate를 동일한 숫자로 해석하지 않는다.

Orin의 physical channel selector, address swizzle, MC 내부 arbitration은 이번 시험에서
읽거나 변경하지 않았다. gem5의 64/512/1024 B interleave를 Orin에 적용한 시험은 아니다.

## 2. 환경 통제와 복원

처음 보드는 MAXN mode 0, `schedutil`, CPU min/max 729.6/2201.6 MHz,
EMC DVFS 상태였다. 이를 먼저 측정하고, `jetson_clocks --store`로 저장한 뒤
고정 clock 조건을 측정했다. 고정 조건에서는 CPU min=max 2201.6 MHz,
EMC `FreqOverride=1`, current=3199 MHz와 CPU idle-state disable을 확인했다.
이는 NVIDIA의 [clock 설정 절차](https://docs.nvidia.com/jetson/archives/r35.4.1/DeveloperGuide/text/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html)를 사용한다.

사용자 승인 후 다음 두 service를 `systemctl stop`으로 중지해 child process와
자동 재시작을 함께 제어했다. service enable 설정은 바꾸지 않았다.

- `dal-e_ros_can_bridge.service`
- `dal-e_state_manager.service`

최종 측정의 inventory에서 두 service는 `inactive/dead`, 관련 ROS process는 없었다.
GNOME 등 나머지 OS service는 유지했다. 측정 종료 후 두 service를 다시 시작했으며
모두 `active`를 확인했다. Clock 설정도 복원 후 다시 저장하여 전후 파일의 byte 단위
일치를 검사했다. 종료 오류나 signal에도 복원하도록 shell trap을 사용했다.

CPU 온도는 ROS 중지 campaign에서 42.75–44.218 °C였다. 모든 thermal throttle
counter를 조사한 것은 아니므로 이 온도만으로 throttling 부재를 보증하지 않는다.
기본 telemetry는 일반 사용자로 실행되어 EMC가 0%로 표시됐으므로 EMC 이용률 계산에는
사용하지 않았다. 이후 `sudo tegrastats`의 짧은 load probe에서 EMC와 frequency가
읽힘을 확인했다. 이 probe는 DVFS/ROS 복원 후의 별도 관찰이며 본 측정의 DRAM byte
counter가 아니다. [Tegrastats 지표 정의](https://docs.nvidia.com/jetson/archives/r35.4.1/DeveloperGuide/text/AT/JetsonLinuxDevelopmentTools/TegrastatsUtility.html)

## 3. Binary와 ROI 정합성

기준 image는 기존 gem5 interleave 시험에 사용한 다음 파일이다.

```text
nexios-gem5-initramfs-apollo-qvp-20261022102228.cpio.gz
SHA256 dbf3202551898871dee98ca7cf7649c2d87ddce3fd433e6d390813716ada0ae4
```

Image에서 직접 추출한 `lat_mem_rd`, `tinymembench`, `stream-gem5-cache`,
`stream.stream`과 `ld-linux-aarch64.so.1`, `libc.so.6`, `libm.so.6`를 전용
directory에서 실행했다. Remote copy의 SHA256도 대조했다. Ubuntu system library는
교체하지 않았다. 동일 ELF/runtime을 사용해도 CPU HWCAP에 따른 libc dispatch와
hardware 실행 경로는 달라질 수 있다.

기존 image의 `apollo-memory-bench --host`는 1/4/8 workers에서 checksum과 warmup
checksum 모두 PASS였다. 기존 `--host`는 m5 pseudo instruction만 건너뛰고 시간은
측정하지 않으므로 아래 두 가지를 보완했다.

- `workloads/zena_cmn/common.h`: ROI ID 0의 시작·종료에서
  `CLOCK_MONOTONIC_RAW`를 측정하고 `CMN_HOST_ROI` JSON을 출력한다.
  switch marker 및 다른 nonzero marker는 host timer를 시작하지 않는다.
- `memory_bench.c`: `--host --workers 12`를 허용한다. 16-double 단위로 분할하여
  총 64 MiB를 빠짐없이 읽으며 NEON loop의 정렬을 유지한다. 기존 1/4/8/16-worker
  분할은 유지하고 non-host 12 workers는 거부한다.

Hardware 측정용 두 내장 executable은 **동일 Yocto target compiler와 recipe flags**로
별도 directory에 static build했다. 이번 작업에서 Yocto deploy image, firmware,
gem5 native executable 또는 기존 snapshot은 재생성하지 않았다.

ROI는 초기화와 warmup 후부터 마지막 worker completion까지다. Multicore barrier와
OS scheduling 영향은 포함되지만 malloc/init/thread 생성과 teardown, 결과 출력은
제외한다. Hardware `useful GB/s = useful_bytes / elapsed_ns`이며 cache pointer chase는
`elapsed_ns / dependent_loads`다. Hardware에서 Atomic/O3 전환은 수행하지 않는다.
기존 progress 문자열의 `atomic`은 source상 초기화 위치를 뜻하며 hardware CPU mode가 아니다.

## 4. 64 MiB multicore read

NEON read, total 64 MiB, main-thread first touch, warmup 1 pass, phase spreading off다.
기본 affinity는 worker 0부터 CPU 0, 1, … 순서다. 아래는 **ROS 중지 + 고정 clock**에서
독립 실행 5회의 median이다. 1-pass의 checksum과 warmup checksum은 모두 8,388,608이다.

| Workers | CPU affinity | Measured 1 pass | Measured 8 passes | 1-pass 실행 간 CV |
|---|---|---:|---:|---:|
| 1 | 0 | 13.027 GB/s | 13.124 GB/s | 0.21% |
| 4 | 0–3 | 21.453 GB/s | 21.517 GB/s | 0.20% |
| 8 | 0–7 | 41.978 GB/s | 42.668 GB/s | 0.42% |
| 12 | 0–11 | 61.637 GB/s | 63.734 GB/s | 0.18% |

1/8-pass 비교는 이번 두 반복량에 대한 관찰이다. 장시간 sustained bandwidth의 완전한
수렴 검증으로 확대하지 않는다. 12 cores에서 16 threads를 oversubscribe하는 시험은 하지 않았다.

기존 gem5는 16 cores / 1 pass에서 64 B stripe 43.506 GB/s,
512 B 32.625 GB/s, 1024 B 31.976 GB/s였다. CPU 수, cache, prefetch, memory timing과
fabric이 다르므로 Orin의 12-core 61.637 GB/s와의 비율을 model 오차율로 사용하지 않는다.

### CPU affinity를 바꾼 추가 비교

동일 code·64 MiB·8 passes·고정 clock·ROS 중지 조건에서 5회씩 측정했다.

| Workers | CPU affinity | 사용 cluster | Useful bandwidth median |
|---|---|---:|---:|
| 4 | `0-3` | 1 | 21.512 GB/s |
| 4 | `0,1,4,8` | 3 | **43.348 GB/s** |
| 8 | `0-7` | 2 | 42.773 GB/s |
| 8 | `0-2,4-6,8-9` | 3 | **57.043 GB/s** |

Worker 수만 같아도 CPU 배치에 따라 결과가 크게 달라졌다. 이 관찰은 cluster 공유
경로의 영향을 시사하지만 L3/NoC/MC 중 단일 bottleneck을 PMU로 특정한 것은 아니다.
Core scaling 시험에는 worker 수와 함께 **affinity 및 사용 cluster 수**를 기록해야 한다.

DVFS 상태의 ROS 중지 8-worker 1-pass 결과는 8.13–28.28 GB/s로 넓게 분산됐고,
고정 clock에서는 41.63–42.01 GB/s였다. CPU/EMC/idle 설정이 함께 달라졌으므로 특정
clock 하나의 영향으로 분리하지 않는다. 고정 clock의 ROS 실행/중지 12-worker 1-pass
median은 각각 61.423/61.637 GB/s였다. 이 값만으로 모든 ROS 부하가 무해하다고 일반화하지 않는다.

## 5. 현재 lmbench·tinymembench·STREAM 조건

모두 CPU 0에 pin하고 아래 명령을 독립적으로 5회 실행했다. `gem5-control run`은
hardware에서 사용하지 않는다. 이 표의 gem5 수치는 보존된 v4의 단일 실행,
Orin 수치는 ROS 중지·고정 clock에서 5회 median이다.

```sh
lat_mem_rd -N 1 -E 200 1 64
tinymembench --bandwidth-size-kib 16 --latency-size-kib 1024 \
  --duration-ms 1 --repeats 1 --latency-count 16384
stream-gem5-cache
```

| 항목 | gem5 v4 | Orin | 의미 |
|---|---:|---:|---|
| lmbench 32 KiB | 2.598 ns | 1.816 ns | stride 64 dependent-load timing |
| lmbench 1 MiB | 23.415 ns | 2.134 ns | prefetch 영향을 통제하지 않은 조건 |
| tinymembench 1 MiB single | 20.9 ns | 13.0 ns | baseline을 뺀 추가 latency |
| tinymembench standard memcpy | 18.109 GB/s | 62.299 GB/s | source/destination 각 16 KiB, copied bytes |
| tinymembench NEON LD1/ST1 copy | 21.320 GB/s | 59.582 GB/s | 같은 copied-byte 정의 |
| STREAM Copy | 10.598 GB/s | 37.590 GB/s | 1.5 MiB 총 working set, read+write bytes |
| STREAM Scale | 10.701 GB/s | 37.590 GB/s | 같은 조건 |
| STREAM Add | 10.623 GB/s | 36.650 GB/s | 같은 조건 |
| STREAM Triad | 10.555 GB/s | 30.262 GB/s | 같은 조건 |

STREAM numerical validation은 모두 PASS이고 최소 표본 시간이 기존 collector의
20 timer-tick 기준을 충족했다. 다만 Triad의 실행 간 CV는 약 9.31%, Add는 약 10.70%였다.
Tinymembench는 Orin에서 `MADV_NOHUGEPAGE`와 `MADV_HUGEPAGE` 두 section을 출력했으며
위 1 MiB median은 두 section 모두 13.0 ns다. Advice가 실제 huge-page backing을
보장하는 것은 아니며 `/proc/PID/smaps`로 backing을 확인하지는 않았다.

Tiny copy와 STREAM의 서로 다른 byte 정의를 섞지 않는다. 이 working set의 결과는
cache 성능이며 LPDDR5의 총 bandwidth로 표시하지 않는다.

## 6. Latency benchmark 해석에서 확인한 문제

고정 stride의 lmbench는 Orin에서 1 MiB까지 약 2 ns를 보였다. 표본 목표를
200 µs에서 20 ms로 늘리고 최대 64 MiB까지 측정해도 1 MiB 2.101 ns,
64 MiB 4.839 ns였다. 따라서 짧은 표본 시간만으로 차이를 설명할 수 없다.

기존 `apollo-bench --mode cache`의 shuffled pointer chain은 다음과 같았다.
표본 길이를 늘려 약 0.5–1 million dependent loads를 측정한 5회 median이다.

| Working set | Passes | Orin random pointer-chase |
|---|---:|---:|
| 32 KiB | 1024 | 1.722 ns/load |
| 64 KiB | 1024 | 1.774 ns/load |
| 128 KiB | 512 | 5.749 ns/load |
| 256 KiB | 256 | 7.305 ns/load |
| 512 KiB | 128 | 8.326 ns/load |
| 1 MiB | 64 | 7.962 ns/load |
| 4 MiB | 16 | 19.504 ns/load |
| 16 MiB | 4 | 183.943 ns/load |
| 64 MiB | 1 | 212.612 ns/load |

Cache 경계 부근은 분산이 크다. 예를 들어 4 MiB는 17.17–26.12 ns 범위다.
큰 random working set에는 TLB/page-walk 비용도 포함될 수 있으므로 마지막 행을
순수 DRAM device latency라고 부르지 않는다.

두 접근 패턴의 차이는 fixed-stride prefetch 영향을 의심할 근거다.
[lmbench upstream manual](https://lmbench.sourceforge.net/man/lat_mem_rd.8.html)도 이 영향을
명시한다. 이번 시험은 hardware prefetch를 끈 대조 실험이 아니므로 기여도를 확정하지 않는다.
Prefetch가 꺼진 gem5 profile을 보정할 때 stride-64 lmbench 값만 목표로 삼으면 안 된다.

추가로 기존 image의 원본 `stream.stream`도 CPU 0에서 실행했다. 배열당 10,000,000
doubles, 합계 약 228.9 MiB이며 Copy/Scale/Add/Triad median은 각각
20.197/19.943/16.715/16.742 GB/s, numerical validation PASS였다.
OpenMP 없는 single-thread 실행으로, 12-core read 결과와 byte 수·kernel이 다르다.

## 7. 재현

보드에 보존한 bundle은 `/home/hyundai/apollo-gem5-validation-20261023/bundle`이다.
다음 명령 자체는 clock이나 ROS 상태를 바꾸지 않는다. 동일 성능 조건의 재현에는
앞 절의 service/clock 저장·설정·복원 절차가 필요하다.

```sh
ssh orin
cd /home/hyundai/apollo-gem5-validation-20261023/bundle

./host/bin/apollo-memory-bench --host --workers 12 --mode read \
  --kernel neon --array-mib 64 --passes 8 --initialize-before-switch

taskset -c 0,1,4,8 ./host/bin/apollo-memory-bench --host --workers 4 \
  --mode read --kernel neon --array-mib 64 --passes 8 --initialize-before-switch

taskset -c 0 ./image/lib/ld-linux-aarch64.so.1 --library-path ./image/lib \
  ./image/bin/lat_mem_rd -N 1 -E 200 1 64
taskset -c 0 ./image/lib/ld-linux-aarch64.so.1 --library-path ./image/lib \
  ./image/bin/tinymembench --bandwidth-size-kib 16 --latency-size-kib 1024 \
  --duration-ms 1 --repeats 1 --latency-count 16384
taskset -c 0 ./image/lib/ld-linux-aarch64.so.1 --library-path ./image/lib \
  ./image/bin/stream-gem5-cache
```

## 8. Evidence와 검증 범위

Local evidence: `build/qbox-apollo-qvp/gem5/orin-validation-20261023/`.

| 경로 | 내용 |
|---|---|
| `image-manifest.json` | 기존 CPIO 및 추출 executable/library SHA256 |
| `host-build.json`, `bundle/host/src/` | 실제 compiler command, source·binary hash |
| `remote/hardware-*.json` | 최초 ROS 실행 campaign의 hardware inventory |
| `remote/ros-stopped/hardware-*.json` | 최종 ROS 중지·고정 clock·복원 상태 |
| `remote/ros-stopped/results-fixed/` | 최종 123 commands의 raw log와 `runs.json` |
| `remote/ros-stopped/results-dvfs/` | DVFS 비교 20 commands |
| `remote/topology/results-topology/` | affinity 비교 20 commands |
| `remote/*/clocks-*.conf`, `ros-*.txt` | clock 파일 동일성, service 중지·복원 증거 |
| `summary.json`, `topology-summary.json` | median/min/max/CV와 기존 gem5 수치 |
| `run-remote.sh`, `run-ros-stopped.sh`, `run-topology.sh` | 실제 사용한 환경 제어 절차 |
| `bundle/measure.py`, `bundle/topology.py`, `analyze.py` | 실행·checksum assert·집계 코드 |
| `tegrastats-root-load-probe.log` | 별도 root telemetry 접근 확인 |

ROS 실행/중지 두 campaign 각각 143 commands, 추가 affinity 20 commands 모두
exit/checksum 또는 tool parser 검사를 통과했다. STREAM은 numerical validation도
확인했다. Host-mode AArch64/QEMU 회귀 7개와 root benchmark/tool collector 회귀
8개가 PASS했다. QEMU timing은 hardware 결과에 사용하지 않았다.

Source 변경 후 compiler가 basic block을 재배치해 기존 linear objdump 순서 검사가
실패했다. 실제 non-host branch 경로의 네 `DSB SY`를 확인하도록 test를 고쳤고,
각 barrier를 제거하면 실패하는 negative check를 추가했다. Production marker의
serialization 결함은 발견하지 않았다.

후속 model 정합성 작업은 random pointer chase, prefetch 조건, cluster affinity,
core별 request concurrency를 분리해 비교하는 순서가 적절하다. 이번 작업은 Orin
memory-controller channel별 byte counter, DRAM PHY timing, 실제 interleave selector,
Apollo/Thor silicon calibration을 검증하지 않았다.

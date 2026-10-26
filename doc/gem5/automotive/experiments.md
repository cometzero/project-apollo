# Automotive SoC 실험 실행 가이드

이 문서는 Apollo AP model에서 **재현 가능한 상대 비교**를 수행하는 절차다.
현재 model의 절대 DMIPS, latency, bandwidth를 Cortex-A720AE 또는 차량용 SoC의
보증 성능으로 사용하지 않는다. 아래 명령은 2026-10-26의 launcher와 workload
source에서 지원 여부를 확인한 **실행 예제**이며, 이번 문서 작성에서 새로 실행한
benchmark 결과가 아니다. 기존 완료 결과는 각각의 보고서에 연결한다.

## 1. 실험 순서와 판정 범위

| 단계 | 질문 | 현재 사용 가능한 경로 | 결과의 범위 |
|---|---|---|---|
| E0 | 같은 입력으로 boot/restore되는가? | diskless initramfs checkpoint | FS 실행 재현성 |
| E1 | working set 증가 시 어떤 cache가 miss하는가? | `--workload cache` | CPU0 dependent-load loop와 실제 cache counters |
| E2 | CPU 공급량과 interleave가 bandwidth에 미치는 영향은? | `dram-multicore`, workers 1/4/8/16 | Linux + O3 + cache + CHI + DRAM 경로 |
| E3 | DRAM backend와 공급 경로 중 어디서 제한되는가? | native saturation diagnostics | 해당 generator/fabric/backend 경로 |
| E4 | background traffic가 critical task의 deadline에 미치는 영향은? | 신규 동시 실행 harness 필요 | 구현·검증 전 `NOT_RUN` |

E1–E3가 E4의 원인 분석 도구다. E2의 평균 bandwidth가 높다는 사실만으로
control-loop deadline이나 mixed-criticality isolation을 판단하지 않는다.

## 2. 입력 고정과 checkpoint 준비

Repository root에서 실행한다. 먼저 [build 가이드](../build-guide.md)에 따라
`apollo-qvp`의 native binary, Linux kernel, PSCI firmware, 전용 initramfs를 준비한다.
아래 첫 두 명령은 build나 simulation을 시작하지 않는다.

```sh
./run_gem5_linux.sh --help
./run_gem5_linux.sh --dry-run --cpus 16 --channels 16 --interleave-bytes 64
```

기본 profile은 `a720ae_documented.yaml`이며 `default.yaml`과 CLI override를 합친다.
현재 launcher는 CPUs **4 또는 16**, channels **4/8/16**, interleave **64/512/1024 B**를
허용한다. CPU count를 임의 값으로 바꾸는 것은 firmware/DTB 지원 범위까지 확장하는
별도 작업이다. 기본 memory capacity는 2 GiB이며 다음 예제는 이를 유지한다.

다음은 이후 예제에서 공유하는 campaign과 16-core/64-B checkpoint 생성 명령이다.
새 디렉터리만 만들며 기존 snapshot은 삭제하거나 덮어쓰지 않는다.

```sh
set -eu
campaign="build/qbox-apollo-qvp/gem5/automotive-$(date +%Y%m%d-%H%M%S)"
mkdir "$campaign"
./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
  --interleave-bytes 64 --checkpoint "$campaign/snapshot-64" \
  --out-dir "$campaign/save-64" --timeout 86400
```

Parent directory가 아직 없으면 먼저 `mkdir -p build/qbox-apollo-qvp/gem5`로 만든다.
`result.json`의 `CHECKPOINT_SAVED`와 snapshot의 `apollo-checkpoint.json`에서
`COMPLETE`를 확인한다. Checkpoint는 initramfs boot 후 **Atomic → O3 switch 이전**에
저장된다. 저장된 cache warmup 상태를 재사용하는 snapshot이 아니다.

Launcher compatibility contract는 gem5 binary/kernel/firmware/profile hash,
initramfs hash, configuration Python hash, CPUs/channels/interleave/bootargs 및
power 설정을 대조한다. Native binary, profile 또는 CPU count를 바꾸면 새 snapshot을
만든다. Base profile 등 의존 파일까지 포함한 전체 provenance는 Git revision과
실제 `resolved-profile.json`/`config.json`으로 추가 확인한다. 자동 contract만으로 모든
외부 입력 변경이 포착된다고 가정하지 않는다. 자세한 규칙은 [run 가이드](../run-guide.md)다.

`--timeout`은 **host seconds**, `--max-ticks`는 **absolute simulation tick 상한**이다.
Restore 시 누적 tick도 고려해야 하며 어느 값도 benchmark 성능의 분모로 쓰지 않는다.
긴 copy/triad 실행은 기본 host timeout 7200초를 넘을 수 있다.

## 3. E1: cache 용량과 dependent-load latency

`cache` workload는 CPU0에 pin한 shuffled pointer chain이다. Allocation/초기화를
Atomic에서 하고 O3로 전환한 다음 1 pass warmup, measured passes를 수행한다.
64 B line마다 한 개의 dependent pointer를 읽으므로 working set 자체를 latency의
분모로 쓰지 않는다. 아래 세 조건은 각각 **65,536 dependent loads**다.

```sh
for pair in '32 128' '512 8' '1024 4'; do
  set -- $pair
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes 64 --resume "$campaign/snapshot-64" \
    --workload cache --size-kib "$1" --passes "$2" \
    --out-dir "$campaign/cache-${1}k" --timeout 86400
done
```

Working set을 64/128/256/2048/4096 KiB 등으로 확장해 knee를 찾는다. Capacity만 보고
“L2/L3 latency”라는 label을 붙이지 않고 동일 ROI의 L1/L2/DSU L3/SLC demand hit/miss를
대조한다. 특히 4 MiB 근방은 짧은 실행의 변화가 컸으므로 기존 Orin 비교에서는
16 passes, 1,048,576 loads를 사용했다. [Orin 기반 재측정](../orin-informed-benchmark-results.md)의
조건을 기준으로 load 수를 늘려 convergence를 확인한다.

기존 tool의 교차 검증도 가능하다. 다음은 gem5 실행 시간을 줄인 **기존 축소 조건**이다.
원본 기본 조건의 점수나 충분히 수렴한 latency라고 표현하지 않는다.

```sh
./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
  --interleave-bytes 64 --resume "$campaign/snapshot-64" \
  --workload command --command 'gem5-control run lat_mem_rd -N 1 -E 200 1 64' \
  --out-dir "$campaign/lmbench-short" --timeout 86400
```

`gem5-control run`은 child의 fork/exec부터 종료까지 감싸며 내부 loop 전용 ROI와 다르다.
자체 switch/ROI marker를 가진 `apollo-bench`, `apollo-memory-bench`, `dhry-gem5`에는
이 wrapper를 중첩하지 않는다. 한 번 restore한 실행에서 marker가 있는 benchmark들을
연속 호출하지 않고 각각 새로 restore한다. tinymembench/STREAM 옵션과 측정 정의는
[benchmark 가이드](../benchmark-guide.md)를 따른다.

## 4. E2: 2 GiB RAM, 64 MiB array, 16-channel 실험

첫 비교는 동일 16-core machine에서 workers만 늘린다. 이는 CPU 수를 바꾸는 실험과
다르며 snapshot을 공유할 수 있다. CPU affinity는 `0..workers-1`이다.

```sh
for workers in 1 4 8 16; do
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes 64 --resume "$campaign/snapshot-64" \
    --workload dram-multicore --memory-mode read --workers "$workers" \
    --size-kib 65536 --passes 2 \
    --out-dir "$campaign/read-w$workers" --timeout 86400
done
for mode in copy triad; do
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes 64 --resume "$campaign/snapshot-64" \
    --workload dram-multicore --memory-mode "$mode" --workers 16 \
    --size-kib 65536 --passes 2 \
    --out-dir "$campaign/$mode-w16" --timeout 86400
done
```

`--size-kib`는 **array 하나의 크기**다. Worker 전체가 각 array를 분할하므로
16 workers에서 worker당 **array별 4 MiB**이고, 16 × 64 MiB allocation이 아니다.

| Mode | 총 working set | Pass당 application useful bytes | 실행 kernel |
|---|---:|---:|---|
| read | 64 MiB | 64 MiB | NEON read + reduction |
| copy | 128 MiB | 128 MiB | C copy loop |
| triad | 192 MiB | 192 MiB | C `a = b + 3*c` loop |

Copy/triad의 `scalar` 설정은 C loop를 선택한다는 뜻이며 compiler auto-vectorization을
금지하지 않는다. Triad는 프로젝트 workload이고 공식 STREAM executable 점수와 다르다.
O3 warmup 1 pass 후 collective barrier와 DSB를 거쳐 측정한다. Barrier와 일부 OS
activity는 ROI에 포함된다. DSB를 dirty cache 전체 flush나 physical PHY completion으로
해석하지 않는다. Multicore `--passes`는 1/2/4/8, size는 1 MiB 단위다.

다음으로 stripe만 512/1024 B로 바꾸어 별도 snapshot을 만들고 같은 read를 반복한다.

```sh
for stripe in 512 1024; do
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes "$stripe" --checkpoint "$campaign/snapshot-$stripe" \
    --out-dir "$campaign/save-$stripe" --timeout 86400
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes "$stripe" --resume "$campaign/snapshot-$stripe" \
    --workload dram-multicore --memory-mode read --workers 16 \
    --size-kib 65536 --passes 2 \
    --out-dir "$campaign/read-w16-stripe$stripe" --timeout 86400
done
```

| Stripe | Channel selector | 전체 16 channels 순환 |
|---|---|---:|
| 64 B | `(PA >> 6) & 15` | 1 KiB |
| 512 B | `(PA >> 9) & 15` | 8 KiB |
| 1024 B | `(PA >> 10) & 15` | 16 KiB |

Home selector는 세 경우 모두 `(PA >> 6) & 7`이다. 따라서 Home/channel 상관관계도
함께 달라진다. 64 MiB 접근으로 모든 channel을 사용할 수 있지만 Linux physical-page
배치와 실제 channel별 bytes를 확인해야 한다. 누적 bytes가 균등해도 순간 queue 분포와
동시 사용률이 같지는 않다. [기존 16-core 결과](../interleave-16core-results.md)의
64 B 우세는 해당 model/workload의 관측값이며 모든 automotive workload의 최적값이 아니다.

## 5. E3: native DRAM 공급량과 CPU 공급량 분리

CPU read가 theoretical bandwidth에 미달하면 CPU를 보정하기 전에 native backend의
공급·서비스 한계를 분리한다. 기존 `run_saturation.py`는 Linux를 boot하지 않으며
`direct`/`fanout`/`single` 경로, read/write mix, fabric width, outstanding requests를
비교한다. 아래는 배포된 native binary가 있는 경우 실행 가능한 기존 case다.

```sh
python3 hsoc-stack/tools/gem5/scripts/zena_cmn/run_saturation.py \
  --gem5 build/tmp_baremetal/deploy/gem5-native/gem5.opt \
  --suite backend --case direct-r100-w32-us40 \
  --output "$campaign/backend-direct-read" --timeout 1200
```

다른 deploy directory를 사용하면 앞의 `--dry-run`에 표시된 gem5 경로를 넣는다.
이 diagnostic은 내부에서 `a720ae_npu_v01_async.yaml`을 읽고 경로별 override를 적용한다.
FS와 같은 controller라고 가정하지 말고 실제 DRAM timing/geometry/clock fingerprint를
대조한 뒤 비교한다. Case 이름의 `w32`는 fabric width이고 DRAM channel 수가 아니다.

`direct`는 CPU/cache/CHI를 통과하지 않는다. `fanout`/`single`도 그 diagnostic의
synthetic 공급 경로이며 실제 camera DMA나 GPU driver의 실행 결과가 아니다. Supply 종료와
drain 검증, generated/completed traffic, serviced bytes를 확인하고 ROI 중 bandwidth와
drain을 포함한 transaction 완료 시간을 구분한다. 기존 backend/interleave 결과의 범위는
[16-core 보고서](../interleave-16core-results.md)에 설명되어 있다.

## 6. E4: critical task + background traffic — 신규 harness 제안

현재 AP launcher에는 `--background-load`, camera DMA, MPAM partition 또는 CARLA 연동
옵션이 없다. 다음은 **설계 절차**이며 그대로 실행하는 CLI가 아니다.

1. Critical kernel을 고정 core/affinity에 두고 input, period, deadline, working set을 정한다.
2. Background kernel은 별도 core에서 read/write/copy, random/sequential, burst length와
   duty cycle을 제어한다. 여러 프로세스가 각각 global CPU-switch marker를 호출하지 않도록
   coordinator 하나가 switch, warmup, start/end barrier와 ROI를 소유한다.
3. Cache interference는 shared-cache placement를, memory interference는 동일 DRAM 경로를
   확인한다. Cache를 우회하는 generator만으로 cache interference를 검증하지 않는다.
4. 각 job의 release/start/finish/deadline tick, background completed bytes를 기록한다.
   동일 input의 단독 실행과 동시 실행을 비교해 slowdown과 deadline misses를 계산한다.
5. Offered load를 여러 단계로 증가시키고 평균뿐 아니라 tail latency, queue occupancy,
   read/write turnaround, channel imbalance를 함께 기록한다.

초기 목적은 “64 MiB sequential read의 최고 GB/s”에서 “주기적인 critical task가
background load를 견디는 범위”로 확장하는 것이다. Arrival timing과 outstanding depth를
정하지 않은 무제한 traffic는 worst-case stress 조건으로 분리한다. 실제 차량 pipeline의
traffic envelope와 같다고 주장하려면 hardware trace 또는 workload trace 근거가 필요하다.
NPU proxy나 standalone SI CL1의 결과만으로 AP와 SI가 통합 실행한 contention을 주장하지 않는다.

## 7. 측정·통계·acceptance 규칙

| 항목 | 기록/판정 |
|---|---|
| Provenance | root/nested Git SHA와 dirty 상태, compiler/flags, image/binary hash, profile, CLI, affinity |
| ROI integrity | 순서가 `warmup → roi_begin → roi_end`, 정확한 begin/end tick, checksum, 정상 workload exit |
| O3 실행 | 요청한 모든 worker의 O3 committed instructions가 양수 |
| Channel coverage | 요청 channel 전부 read traffic, copy/triad는 write traffic도 확인 |
| Useful bandwidth | application이 정의한 bytes / ROI simulated seconds / `10^9` |
| DRAM bandwidth | 같은 ROI의 `dramBytesRead + dramBytesWritten` / simulated seconds / `10^9` |
| Cache latency | ROI simulated time / dependent loads; cache hit/miss와 함께 기록 |
| Tail latency | job/sample 정의, count, elapsed simulated time, quantile 방식, confidence, workload phase |
| Status | `PASS`, `FAIL`, `TIMEOUT`, `NOT_RUN`을 보존하고 실패 실행을 성능 평균에서 숨기지 않음 |

Useful bytes와 DRAM bytes는 cache hit, write allocation, writeback, page-table/OS traffic
때문에 다르다. Channel별 평균 latency의 산술평균은 request 수로 가중한 global 평균과
다르다. Read/write mix와 분모를 맞추지 않은 수치끼리 비교하지 않는다.

각 configuration은 독립 restore로 반복하되 deterministic model의 같은 seed 재실행만으로
실제 workload variance를 추정하지 않는다. 우선 passes 1/2/4/8로 측정 구간을 늘려
warmup·barrier 비중과 sustained throughput의 수렴을 확인한다. Fixed 1-pass warmup도
보편적인 steady state 보장이 아니므로 필요하면 workload에 warmup 제어를 추가한다.
실제 phase 변화는 input/placement/arrival seed를 명시하여 별도 반복한다.

p99는 sample 100개에서 tail이 사실상 한두 observation에 좌우되므로 32개 realtime job
같은 짧은 probe로 안정적인 p99를 주장하지 않는다. 원하는 confidence와 오차에 맞춰
sample count를 사전 결정하고, 상관된 연속 job에는 block 단위 분석을 사용한다.
표본이 부족하면 개별 값·median·observed maximum과 count를 보고한다.
Observed maximum은 WCET 증명이 아니며 timing model의 calibration 없이 safety deadline
보증에 사용하지 않는다.

Authoritative artifacts는 run의 `launch.json`, `result.json`,
`m5out/system.platform.terminal`, `m5out/roi-events.json`, `m5out/roi-summary.json`,
`m5out/stats.txt`, `m5out/config.json`, `m5out/resolved-profile.json`이다.
`scripts/gem5/benchmark.py`는 ROI에 정확히 맞는 statistics를 선택한다. 중간 `SIGUSR1`
dump와 종료 dump를 단순 합산하면 중복된다. Online power 사용 시 additive counters는
검증된 연속 epoch만 합치고 latency/rate/histogram은 임의 합산하지 않는다.
`summarize_tools.py`의 기존 축소 tool parser를 임의 옵션에 범용으로 적용하지 않는다.

## 8. 구현 근거

- [AP launcher와 checkpoint contract](../../../scripts/gem5/run_linux.py)
- [Single-core benchmark](../../../scripts/gem5/benchmark.c), [ROI collector](../../../scripts/gem5/benchmark.py)
- [Multicore workload](../../../hsoc-stack/tools/gem5/workloads/zena_cmn/memory_bench.c)
- [기본 parameter](../../../hsoc-stack/tools/gem5/configs/zena_cmn/profiles/default.yaml), [기본 AP profile](../../../hsoc-stack/tools/gem5/configs/zena_cmn/profiles/a720ae_documented.yaml)
- [Native saturation runner](../../../hsoc-stack/tools/gem5/scripts/zena_cmn/run_saturation.py), [실제 공급 경로](../../../hsoc-stack/tools/gem5/tests/zena_cmn/directed/memory_saturation.py)
- [Finite backend traffic/drain probe](../../../hsoc-stack/tools/gem5/tests/zena_cmn/directed/lpddr5x_backend_traffic.py)
- [기존 Orin 측정 조건](../orin-validation-results.md), [Orin bandwidth 검증](../orin-bandwidth-tuning.md)

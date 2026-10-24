# Benchmark 실행과 결과 해석

[문서 목차](README.md) · [실행 절차](run-guide.md) · [검증 기준](validation.md)

## 1. 측정 경로 선택

현재 세 가지 경로가 있다. 같은 O3 model을 쓰더라도 **측정 구간과 분모가 다르다**.

| 경로 | 실행 방식 | ROI | 주 용도 |
|---|---|---|---|
| 내장 `apollo-bench` | `--workload cache` / `dram` | O3 warmup 후 반복 loop | cache latency, 유효 read bandwidth의 통제된 비교 |
| Multicore `apollo-memory-bench` | `--workload dram-multicore` | pinned worker 전체의 O3 warmup 후 read/copy/triad loop | CPU/CMN/DRAM 경로의 16-core 비교 |
| 기존 tool | `--workload command --command 'gem5-control run …'` | fork/exec부터 child 종료까지 | 실제 Linux executable의 output과 전체 실행 통계 분석 |

`--workload command`는 command 실행 성공만 판단한다. 임의 command를 자동으로 O3로
전환하거나 그 결과를 benchmark 점수로 검증하지 않는다. O3 측정에는 `gem5-control run`이
필요하고, 도구별 결과 검증에는 별도의 `summarize_tools.py`가 필요하다.

## 2. CPU switch와 ROI

![Guest marker와 ROI statistics 순서](diagrams/04-roi-sequence.drawio.svg)

[control.c](../../scripts/gem5/control.c)의 `run_command()`는 CPU0 affinity를 설정하고
`m5_work_begin(0x5a535743, 0)`을 호출한다. Python의
[RoiControl.handle()](../../hsoc-stack/tools/gem5/configs/zena_cmn/roi_control.py)는 모든
boot CPU를 대응하는 `roi_cpu`로 전환하고 phase를 `warmup`으로 바꾼다.
그 뒤 `m5_work_begin(0, 0)`에서 `m5.stats.reset()`, `m5_work_end(0, 0)`에서
`m5.stats.dump()`를 수행한다. guest 쪽 marker 주변에는 `DSB SY`가 있다.

`gem5-control run`의 `warmup` phase는 **phase 이름**이다. tool을 미리 반복 실행하는
별도 warmup은 없다. fork/exec, dynamic loader, allocation, page fault, kernel,
calibration 및 tool 내부 시험이 모두 whole-command ROI에 포함된다. CPU0 pin은
child가 상속하지만 다른 CPU의 Linux activity까지 중지시키지는 않는다.

반면 [benchmark.c](../../scripts/gem5/benchmark.c)는 buffer 초기화를 Atomic 구간에서
끝내고, O3 switch 후 실제 workload 1회 warmup을 수행한 뒤 ROI를 시작한다.
marker 안쪽 barrier의 비용도 측정에 포함된다. 두 경로의 hit ratio를 동일한 의미로
나란히 놓으면 안 된다.

## 3. 내장 cache / DRAM benchmark

| 항목 | `cache` | `dram` |
|---|---|---|
| 기본 working set | 32KiB | 65536KiB = 64MiB |
| 접근 | 64-byte node의 deterministic shuffled pointer chain | 4개의 독립 accumulator로 순차 uint64 read |
| CPU | CPU0 단일 thread | CPU0 단일 thread |
| Warmup | O3에서 전체 chain 1회 | O3에서 전체 array 1회 |
| 기본 반복 | 2 passes | 2 passes |
| 정확성 | 한 바퀴 후 원래 pointer로 복귀 | 값이 1인 배열의 합계 |
| 보고값 | `ns_per_dependent_load` | `useful_GB_per_second` |

```sh
./run_gem5_linux.sh --headless --workload cache --size-kib 32 --passes 2
./run_gem5_linux.sh --headless --workload dram --size-kib 65536 --passes 2
```

`--passes`는 1..1024, `--size-kib`는 1..262144 범위다. 실제 시간은 working set,
profile, host load에 크게 좌우된다. DRAM 시험은 기본 host timeout 7200초 안에 끝나지
않을 수 있다. `--timeout`은 host wall-clock deadline, `--max-ticks`는 simulator의
절대 tick 상한이다. snapshot에서 복원한 tick보다 큰 상한을 사용해야 한다.

cache의 한 node는 64 bytes이지만 dependent load는 pointer 8 bytes를 읽는다.
`useful_bytes`를 cache line 크기나 실제 interconnect traffic으로 바꾸어 해석하지 않는다.
DRAM 유효 대역폭 역시 read payload 기준이며 DRAM bus utilization과 같지 않다.

계산식은 [benchmark.py](../../scripts/gem5/benchmark.py)의 `summarize()`를 따른다.

```text
ROI seconds = (roi_end.tick - roi_begin.tick) / simFreq
ns / dependent load = ROI seconds × 1e9 / dependent_loads
useful GB/s = useful_bytes / ROI seconds / 1e9
cache hit ratio = hits / (hits + misses)  [각 level별 분모]
```

`host=true`인 기능 시험, checksum 불일치, marker 누락, ROI와 stats tick 불일치는 거부한다.
Host에서 같은 C program이 실행됐다는 사실만으로 gem5 timing 결과를 만들지 않는다.

## 4. initramfs의 benchmark package

| Tool | 기본 조건 | simulation용 조정 |
|---|---|---|
| lmbench `lat_mem_rd` | upstream 목표 100ms 및 기본 calibration | 기존 `-N`·크기·stride에 `-E USEC` 추가 |
| tinymembench | bandwidth 32MiB, latency 64MiB, 500ms, repeats 10, latency count 10M | runtime CLI 추가 |
| `stream` | 배열당 10M doubles, 3 arrays, 10 iterations, single thread | upstream default 유지 |
| `stream-gem5-cache` | 배열당 65536 doubles, 합계 1.5MiB, 10 iterations | 별도 executable, cache 측정용 |

[lmbench recipe append](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/lmbench/lmbench_%.bbappend),
[tinymembench recipe append](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/tinymembench/tinymembench_%.bbappend),
[STREAM recipe](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/stream/stream_5.10.bb),
[STREAM variant](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/stream/stream-gem5-cache_5.10.bb)가 소유한다.

### lmbench

```sh
lat_mem_rd -N 1 -E 200 1 64
```

`-N 1`은 반복 1회, `1`은 최대 working set 1MiB, `64`는 stride 64 bytes다.
512B부터 1MiB까지 21개 크기를 측정한다. `-E 200`은 sample 목표 200µs이며,
수십 시간의 simulation을 피하기 위해 추가한 확장이다. 지정한 ENOUGH override로
interval 탐색을 생략하지만 timer/loop overhead의 실측 보정은 유지한다.
`-E`를 생략하면 upstream 기본 동작을 유지한다. 출력의 `modified lmbench` marker를
보존하고 표준 upstream 조건 점수와 구분한다. `-E` 허용 범위는 200..INT_MAX µs다.

### tinymembench

```sh
tinymembench --bandwidth-size-kib 16 --latency-size-kib 1024 \
  --duration-ms 1 --repeats 1 --latency-count 16384
```

| Option | 의미 |
|---|---|
| `--bandwidth-size-kib` | bandwidth source/destination buffer의 기본 크기 |
| `--latency-size-kib` | latency working set 상한 |
| `--duration-ms` | bandwidth trial의 목표 시간 |
| `--repeats` | bandwidth·latency 반복 횟수 |
| `--latency-count` | latency 측정 접근 수 |
| `--help` | 허용 범위와 기본값 출력 |

latency count는 내부 unrolling과 맞는 배수여야 하며 작은 값·overflow·잘못된 정렬은
parser가 거부한다. 시간 축소는 `--duration-ms`만으로 충분하지 않다. latency의 실행량은
`--latency-count`와 working set도 함께 결정한다. 이 실행에는 별도 numerical checksum이
없으므로 출력 완전성 검사가 모든 memory 연산의 수치 정합성을 입증하지는 않는다.

### STREAM

```sh
stream-gem5-cache
```

별도 binary의 array 크기는 recipe에서 compile-time으로 정한다. launcher의 `--size-kib`는
STREAM에 전달되지 않는다. `stream`은 원본 기본 크기이므로 혼동하지 않는다.
정상 출력의 `Solution Validates:`를 확인하고 Copy/Scale/Add/Triad 네 결과를 보존한다.
첫 iteration을 제외한 best time을 사용하므로 단일 latency sample과 통계 의미가 다르다.

## 5. snapshot에서 세 도구 재현

먼저 [Run guide](run-guide.md)에 따라 **현재 image로 새 snapshot을 만든다**.
이미 검증된 로컬 snapshot은 다음 경로지만, 다른 checkout이나 deploy image에서 동일하다고
가정하지 않는다. `run_linux.py`가 hash 불일치 시 거부한다.

```sh
snapshot=build/qbox-apollo-qvp/gem5/linux-benchmarks-v4-snapshot
campaign=build/qbox-apollo-qvp/gem5/benchmarks-$(date +%Y%m%d-%H%M%S)
mkdir -p "$campaign"

./run_gem5_linux.sh --headless --resume "$snapshot" \
  --out-dir "$campaign/lmbench" --workload command \
  --command 'gem5-control run lat_mem_rd -N 1 -E 200 1 64'

./run_gem5_linux.sh --headless --resume "$snapshot" \
  --out-dir "$campaign/tinymembench" --workload command \
  --command 'gem5-control run tinymembench --bandwidth-size-kib 16 --latency-size-kib 1024 --duration-ms 1 --repeats 1 --latency-count 16384'

./run_gem5_linux.sh --headless --resume "$snapshot" \
  --out-dir "$campaign/stream" --workload command \
  --command 'gem5-control run stream-gem5-cache'

for tool in lmbench tinymembench stream; do
  python3 scripts/gem5/summarize_tools.py "$campaign/$tool" "$tool" \
    > "$campaign/$tool/measurement.json"
done
```

각 simulation은 새로운 output directory를 사용한다. 현재 ROI controller는 한 실행에서
중복 CPU switch를 거부하므로 세 `gem5-control run`을 하나의 shell script에서 연속 호출하지
않는다. 각 tool을 동일한 snapshot에서 독립적으로 복원하는 방식이 재현에 적합하다.

[summarize_tools.py](../../scripts/gem5/summarize_tools.py)는 위 **특정 축소 조건**을 검증하는
collector다. 임의 설정의 범용 parser가 아니다. 설정을 바꿨다면 parser의 expected settings,
tests와 보고서 조건도 함께 바꿔야 하며, 검증을 통과시키려고 UART marker만 수정하지 않는다.

## 6. v4 결과와 비교 원칙

2026-10-22에 보존한 결과는 다음과 같다. 이번 문서 작성에서는 세 output directory를
collector로 다시 분석해 PASS를 확인했다. 자세한 표는
[고정 측정 보고서](../apollo-gem5-benchmark-results.md)에 있다.

| 항목 | 결과 | 의미 |
|---|---|---|
| lmbench 32KiB / 1MiB | 2.598 / 23.415 ns/load | dependent-load 절대 latency |
| tinymembench 1MiB single | 20.9ns | baseline을 뺀 추가 latency |
| tinymembench libc memcpy | 18.1087 GB/s | 16KiB buffer, copied bytes 기준 |
| STREAM Copy / Triad | 10.5977 / 10.5553 GB/s | 총 1.5MiB arrays, 논리적 read+write 기준 |

lmbench와 tinymembench latency는 같은 정의가 아니므로 직접 빼서 비교하지 않는다.
tinymembench copy를 read+write payload로 표현하려면 2배가 되지만, 그러더라도
STREAM과 working set·instruction mix·cache residency가 달라 성능 순위를 매길 수 없다.
모든 수치는 uncalibrated model 결과이며 STREAM 축소판은 공식 DRAM 점수가 아니다.

### 오차와 해석 제약

- lmbench·tinymembench는 반복 1회여서 variance를 추정하지 못한다.
- STREAM은 1µs timer에서 최소 98~149µs kernel time을 기록했다. collector는 20 timer ticks
  미만을 `LOW_RESOLUTION`으로 표시한다.
- tinymembench latency count 16384에서는 1µs의 양자화가 접근당 약 0.061ns다.
  baseline 차감·clamp 때문에 0.0ns 출력이 실제 무지연을 의미하지 않는다.
- whole-command cache ratio는 allocation·calibration·kernel을 포함한다. 각 cache level의
  분모가 다르므로 hit ratio를 단순 합산하지 않는다.
- Host runtime을 GB/s 계산에 쓰지 않는다. CPU별 guest activity·address layout·cache
  conflict·compiler 설정이 바뀌면 동일 capacity에서도 결과가 달라질 수 있다.

## 7. Cache / DRAM 실험 확장 시 보존할 것

Profile, CPU/channel count, binary·kernel·initramfs hash, 명령, snapshot provenance,
`launch.json`, `m5out/config.json`, `roi-events.json`, `stats.txt`, `uart.log`를 함께 보존한다.
CPU frequency나 cache size 비교는 한 변수씩 바꾸고 snapshot을 해당 설정으로 다시 만든다.
DRAM을 비교하려면 LLC/SLC에 머무는 축소 STREAM 결과로 대체하지 말고, working set과
실제 `dramBytesRead` 등 memory-controller traffic을 확인한다. 여러 CPU의 확장성이나
NUMA/thermal/power 특성은 현재 세 단일-thread 실행에서 검증되지 않았다.

## 8. 16-core DRAM interleave 비교

`gem5-apollo-guest`가 기존 `workloads/zena_cmn/memory_bench.c`를 static AArch64
`/usr/bin/apollo-memory-bench`로 빌드한다. Launcher의 `dram-multicore`는 기본적으로 NEON read를
사용한다. `--size-kib 65536`은 **worker 전체가 나누어 읽는 64 MiB**이며,
16 workers이면 각 CPU가 disjoint 4 MiB를 읽는다. CPU 0..15에 pin하고 allocation과
초기화를 Atomic에서 끝낸 뒤 모든 CPU를 O3로 바꾼다. O3에서 한 번 warmup하고,
collective barrier/DSB를 거쳐 ROI를 시작한다. 측정 pass가 끝나면 모든 worker의
memory completion을 확인한 뒤 ROI를 닫는다. Barrier와 일부 Linux activity는 ROI에
포함되며 dirty cache flush나 physical DRAM PHY completion을 모델링하는 것은 아니다.

`--workers` 기본값은 `--cpus`이며 1/4/8/16 중 CPU 수 이하를 선택한다.
이 workload의 `--passes`는 1/2/4/8, `--size-kib`는 1 MiB 단위다.
자체 switch/ROI marker가 있으므로 `gem5-control run`으로 중첩해서 감싸지 않는다.

`--memory-mode read|copy|triad`로 기존 guest kernel을 선택한다. 기본값은 `read`다.
이 옵션은 `--workload dram-multicore`에서만 허용된다. `--size-kib`는 **array 하나의
크기**이며 worker 전체가 각 array를 분할한다.

| Memory mode | Guest kernel | `--size-kib 65536`의 총 working set | Pass당 useful bytes |
|---|---|---:|---:|
| `read` | NEON read + reduction | 64 MiB | 64 MiB |
| `copy` | `b[j] = a[j]` | 128 MiB | 128 MiB |
| `triad` | `a[j] = b[j] + 3*c[j]` | 192 MiB | 192 MiB |

Copy/triad의 guest option 이름 `scalar`는 명시적 NEON read를 사용하지 않는 C loop를
뜻한다. Compiler auto-vectorization을 금지하지 않는다. Triad는 upstream STREAM과
같은 연산을 사용하는 프로젝트 workload이며 공식 STREAM 점수와 구분한다.
배열 검증과 모든 worker의 O3 실행 외에 모든 DRAM channel의 read traffic을 검사하고,
copy/triad는 write traffic도 요구한다. Application useful bytes와 실제 DRAM burst
bytes는 별도로 보고한다. DSB만으로 dirty cache가 모두 DRAM에 기록되지는 않는다.

2 GiB RAM과 16 × x16-bit channel을 유지하고 **channel stripe만** 변경한다.
Home-node stripe는 64 B, Home 수는 8로 유지한다.

| `--interleave-bytes` | Channel selector | 전체 channel 순환 | 4 KiB physical page가 걸치는 channel |
|---|---|---|---|
| 64 (기존 기본값) | `(PA >> 6) & 15` | 1 KiB | 16 |
| 512 | `(PA >> 9) & 15` | 8 KiB | 8 |
| 1024 | `(PA >> 10) & 15` | 16 KiB | 4 |

64 MiB 전체 순회에서는 세 설정 모두 16 channels를 사용할 수 있다. 512/1024 B에서는
Linux physical-page 배치도 분산에 영향을 주므로 실제 ROI의 channel별 read bytes를
검사한다. Address mapping과 Home/channel 상관관계가 함께 달라지는 sensitivity 시험이며
Thor의 비공개 address swizzle 또는 실제 silicon 성능을 재현한다고 해석하지 않는다.

```sh
./yocto_build.sh --gem5 --keep-conf
campaign=build/qbox-apollo-qvp/gem5/my-interleave
mkdir -p "$campaign"
for stripe in 64 512 1024; do
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes "$stripe" --checkpoint "$campaign/snapshot-$stripe" \
    --out-dir "$campaign/save-$stripe" --timeout 86400 || break
  ./run_gem5_linux.sh --headless --cpus 16 --channels 16 \
    --interleave-bytes "$stripe" --resume "$campaign/snapshot-$stripe" \
    --workload dram-multicore --workers 16 --size-kib 65536 --passes 1 \
    --out-dir "$campaign/read-$stripe" --timeout 86400 || break
done
```

각 stripe의 snapshot을 별도로 생성한다. Interleave 또는 CPU 수가 다른 snapshot의
재사용은 compatibility 검사에서 거부한다. `result.json`은 checksum/warmup checksum,
요청 worker 수, 모든 worker의 O3 committed instructions와 모든 channel의 read traffic을
검증한다. 상세 native counter는 `m5out/roi-summary.json`에 보존한다.

단일 pass는 설정 비교의 첫 관측값이다. Sustained bandwidth나 최고 성능을 주장하려면
동일 working set에서 passes 1/2/4 등으로 수렴 여부와 실제 DRAM traffic을 확인해야 한다.

완료한 세 설정의 build, snapshot, 16-core ROI 결과와 재실행 경로는
[Interleave 시험 보고서](interleave-16core-results.md)에 정리했다.

## 9. Orin hardware에서 같은 workload 실행

내장 `apollo-bench`, `apollo-memory-bench`의 `--host`는 gem5 pseudo instruction을
실행하지 않는다. 현재 source는 ROI ID 0에 `CLOCK_MONOTONIC_RAW` timer를 사용하고
`CMN_HOST_ROI` JSON의 `elapsed_ns`를 출력한다. Host 전용 `--workers 12`도 지원하며
total working set을 NEON iteration 단위로 나누어 끝부분을 누락하지 않는다.
Gem5 launcher의 CPU/worker choices와 non-host 12-worker 제한은 유지한다.

Host affinity는 process의 allowed CPU set에서 처음 N개 CPU다. `taskset`으로 이를
제한하면 같은 worker 수로 cluster 배치를 비교할 수 있다. Host timer가 없는 과거
image executable은 checksum 확인에 사용할 수 있지만 shell 전체 실행 시간을 ROI로
사용하지 않는다. 새 host 기능을 image에 넣으려면 guest recipe/image를 다시 빌드한다.

Orin 시험은 기존 image의 lmbench/tinymembench/STREAM binary와 library를 그대로
사용했다. 내장 benchmark만 동일 Yocto compiler로 별도 build했고, deploy image나
snapshot을 덮어쓰지 않았다. Board 준비·측정 결과·실행 명령·artifact 경로는
[Orin 검증 보고서](orin-validation-results.md)를 따른다.

고정 clock, prefetch 조건, cluster별 affinity, working set, 반복량과 byte 정의를
맞춰 비교한다. Hardware에서 `gem5-control run`을 실행하지 않는다. 특히 stride-64
lmbench는 hardware prefetch에 민감하므로 random pointer chase와 함께 판단한다.

공개 Orin memory benchmark와 비교하려면 single-thread/cache용 STREAM에 더해
OpenMP DRAM 조건을 측정한다. 실제 Orin에서 12 threads와 명시적 affinity로
Copy 약 82 GB/s, Triad 약 73 GB/s를 확인했다. `spread`만으로 cluster별 부하가
균등해지는 것은 아니다. Native/Yocto compiler, 큰 working set, 기존 Apollo
copy/triad와의 교차 시험 및 재현 명령은
[Orin bandwidth 개선 보고서](orin-bandwidth-tuning.md)를 따른다.

## 10. Orin 측정에 맞춘 gem5 재측정

Cache latency는 `--workload cache`의 shuffled pointer chain을 사용하고,
working set뿐 아니라 dependent-load 수와 실제 L1/L2/L3/SLC demand hit/miss를 기록한다.
Fixed-stride lmbench 결과 하나를 L3 hit latency로 간주하지 않는다.
32 KiB–1 MiB sweep은 65,536 loads를 시작 조건으로 사용할 수 있지만,
Orin의 4 MiB 시험은 짧은 ROI에서 분산이 커 16 passes / 1,048,576 loads로 늘렸다.

Single-core collector도 요청 mode/size/passes/checksum을 대조하고 정확한 ROI
begin/end tick에 맞는 statistics block 하나만 사용한다. 중간 SIGUSR1 dump와 exit
dump는 합산하지 않으며, 일치하는 ROI가 없거나 중복되면 결과를 거부한다.
Multicore 결과에는 전체 core/DSU/Home의 cache counters도 포함한다. 이 counter에는
benchmark 이외의 OS traffic이 포함될 수 있다.

Memory 재측정은 read/copy/triad, array당 64 MiB, 16 workers, warmup 1 pass와
measurement 2 passes를 사용한다. Orin은 12 workers로 같은 byte/반복 조건을
측정하므로 CPU·cache·DRAM이 같은 플랫폼이라고 해석하지 않는다.
Copy/triad는 기본 host timeout 7,200초를 넘길 수 있으므로 재현 명령은
`--timeout 86400`을 명시한다. ROI 이후의 전체 출력 배열 검증과 정상 종료까지 기다린다.
L2 prefetch `off`/`stride`는 지원되는 별도 profile로 A/B 측정하며 기본 profile을
임의로 바꾸지 않는다. Profile이 다르면 별도 snapshot을 생성한다.

구현, 완료한 실행 및 남은 검증 상태는
[Orin 기반 재측정 보고서](orin-informed-benchmark-results.md)에 기록한다.

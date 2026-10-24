# Orin 측정에 기반한 gem5 benchmark 개선과 재측정

작업일: 2026-10-23–24 (KST). **구현과 재측정 완료**.
Host regression **26/26 PASS**, gem5 cache 9개·memory 4개 조건 **13/13 PASS**,
Orin matching measurement **55/55 PASS**다. Prefetch용 fresh boot/snapshot도 검증했다.
13개 결과를 collector로 재집계하여 ROI, 성능 값과 counter를 포함한 전체
`measurement`가 각 run의 `result.json`과 일치함을 확인했다.

## 변경 범위

Orin에서 확인한 kernel별 byte 정의, thread concurrency, prefetch 민감도와 짧은 ROI의
분산을 benchmark 실행·검증 방법에 반영한다. Apollo의 CPU/cache/DRAM timing을
Orin 숫자에 맞춰 조정하는 작업은 아니다.

- Launcher에 `--memory-mode read|copy|triad`를 추가하고 기존 initramfs의
  `apollo-memory-bench`에 연결했다. Array당 64 MiB이면 총 working set은
  각각 64/128/192 MiB다. 기존 read 기본 동작을 유지한다.
- Collector는 mode/kernel/working set/passes/checksum을 요청과 대조한다.
  모든 worker의 O3 committed instructions, channel별 read traffic을 검사하며
  copy/triad는 모든 channel의 write traffic도 검사한다.
- Multicore 결과에 전체 L1D/L2/DSU L3/Home SLC demand hit/miss를 추가했다.
- Single-core cache/DRAM collector는 정확한 ROI tick에 일치하는 block 하나만
  선택하여 중간 diagnostic dump와 simulator exit dump의 혼입을 막는다.
- Guest C source, recipe/image, native executable, model timing의 변경 없이
  기존 지원 기능을 사용했다. 지원되던 stride prefetch profile은 별도 A/B 입력이다.

소유 파일은 root repository의 `scripts/gem5/run_linux.py`, `benchmark.py`와 두 test다.
전체 `scripts/gem5/test_*.py` **26/26 PASS**. 기존 64-B interleave read 결과를 새
collector로 재분석해 **43.50572484999476 GB/s**와 ROI/DRAM 값의 일치를 확인했다.
원본 evidence의 hash도 유지되었다.

## 고정 입력과 snapshot

Baseline은 기존 16-core / 16-channel / 64-B stripe snapshot을 사용한다.
현재 deploy symlink의 kernel이 이전 측정 이후 변경되어 처음 compatibility 검사가
실패했다. 보존된 `save-64/m5out/kernel-image.elf`의 단일 PT_LOAD에서 원본 arm64
Image payload를 추출하고 snapshot의 SHA256과 byte 단위 일치를 검증했다.
복구한 Image를 명시적으로 전달하여 기존 snapshot contract 검사를 통과했다.
호환성 검사를 우회하거나 snapshot metadata를 수정하지 않았다.

```text
Kernel SHA256: a0fc4d6cb075520a5b75e608600de49a93a547029b625fad91cf86293b9b537f
Native SHA256: 35fb63bbe291a95d317493dca47cf668ddab6964650d2ec7b2dd4ab0f422af5e
Image: nexios-gem5-initramfs-apollo-qvp-20261022102228.cpio.gz
Image SHA256: dbf3202551898871dee98ca7cf7649c2d87ddce3fd433e6d390813716ada0ae4
```

Prefetch-on은 별도의 fresh boot/snapshot을 사용한다. 두 effective profile의 차이는
`cache.l2.prefetch: off → stride` 한 항목이고 native config의 16개 L2 모두에서
`use_prefetcher`가 false/true로 바뀜을 확인했다. Arm의 실제 prefetch algorithm과
같은 모델이라는 의미는 아니다. 초기 deploy kernel을 선택했던 중단 시도도 보존한다.

## 측정 조건

| 항목 | gem5 | Orin matching measurement |
|---|---|---|
| CPU | A720AE proxy 16 cores, 2 GHz, 4 clusters | A78AE 12 cores, 고정 설정 2.2016 GHz, 3 clusters |
| Cache worker | CPU 0 | CPU 0 |
| Memory workers | CPU 0–15, 4/4/4/4 | CPU 0–11, 4/4/4 |
| Memory | 2 GiB, 16 × x16 LPDDR5X proxy, stripe 64 B | AGX Orin 64 GB LPDDR5 |
| Cache pattern | 64-B node shuffled pointer chase | 같은 workload loop의 host 실행 |
| Cache ≤1 MiB | 32/64/128/256/512/1024 KiB, 각각 65,536 loads | 같은 크기·반복 수, 독립 5회 |
| Cache 4 MiB | 16 passes, 1,048,576 loads | 같은 크기·반복 수, 독립 5회 |
| Memory pattern | NEON read / C copy / C triad | 같은 kernel 종류 |
| Memory working set | Array당 64 MiB, measured 2 passes | 같은 조건, 독립 5회 |
| Warmup | O3에서 1 pass, 측정 제외 | Hardware에서 1 pass, 측정 제외 |
| Time | Exact simulated ROI ticks | CLOCK_MONOTONIC_RAW ROI |

Guest와 Orin executable은 같은 ELF가 아니다. Orin에는 host timer와 12-worker 지원이
들어간 기존 host build를 사용하며, workload loop와 working set/반복 수/byte 정의를
맞췄다. 두 memory executable은 Yocto GCC 14.3.0으로 같은 주요 tuning 옵션을 사용했다.
보존된 ELF를 disassemble하여 read/copy/triad **hot loop의 instruction words가 각각
byte 단위로 동일**함을 확인했다. Timer, partition setup, barrier, OS 실행까지 같은
instruction stream이라는 뜻은 아니다.

| Memory kernel | 실제 hot loop | 해석 |
|---|---|---|
| Read | 128 B당 4 × `LDP Q`, 8 × `FADD V.2D`; 제어 포함 16 instructions | 독립 accumulator 8개를 사용하는 NEON reduction |
| Copy | 8 B element당 `LDR D` + `STR D`; 제어 포함 5 instructions | Scalar copy; `memcpy` 대체나 SIMD 변환 없음 |
| Triad | 8 B element당 2 loads, `FMUL D`, `FADD D`, store; 제어 포함 8 instructions | Scalar 연산; SIMD/FMA 변환 없음 |

Mode 사이의 bandwidth 차이는 read/write traffic뿐 아니라 instruction mix와 CPU issue
효율도 포함한다. Copy/triad를 최적화된 SIMD STREAM 점수나 DRAM 최대 성능으로 해석하지 않는다.

4 MiB / 1-pass 실행도 `SHORT_ROI` 진단으로 보존한다. Orin에서 이 조건은
median 42.342 ns/load, CV 33.34%였고 16 passes에서는 21.481 ns/load,
CV 9.62%였다. 긴 조건도 분산이 있으므로 하나의 정확한 silicon latency로 취급하지 않는다.
Orin 55회는 모두 PASS이고 clock/ROS 복원도 확인했다. 상세 원본은 아래 evidence에 있다.

## 실행 결과

### Cache: baseline 완료

Gem5는 조건별 독립 restore 1회, Orin은 독립 5회 median이다. 표의 hit 판정은
gem5 native counter 관찰이며 hardware PMU를 측정한 결과가 아니다.

| Working set | Passes | gem5 ns/load | Orin median ns/load | gem5에서 관찰한 경로 |
|---|---:|---:|---:|---|
| 32 KiB | 128 | 2.369 | 1.727 | L1D demand hit 100% |
| 64 KiB | 64 | 3.609 | 1.789 | L1D hit 88.79%, miss는 L2 hit |
| 128 KiB | 32 | 13.325 | 5.290 | L2 demand hit 100% |
| 256 KiB | 16 | 13.415 | 7.396 | L2 demand hit 100% |
| 512 KiB | 8 | 15.134 | 8.294 | L2 hit 91.90%, 하위 cache/DRAM 혼합 |
| 1 MiB | 4 | 24.477 | 7.949 | L3 demand hit 약 100% |
| 4 MiB | 16 | 25.901 | 21.481 | L3 hit 95.46%, SLC/DRAM 혼합 |

64 KiB와 512 KiB는 model cache 용량과 같은 경계 크기여서 순수 hit latency로
이름 붙이지 않는다. 각 level의 hit fraction은 해당 level에 도달한 demand를 분모로
하므로 서로 더할 수 없다. L2/L3 경로의 model latency가 Orin보다 길다는 관찰은
남아 있으며, benchmark 변경으로 model timing을 보정했다고 주장하지 않는다.

Pointer-chase의 ns/load에는 address translation과 loop/OS 비용도 포함된다.
Native config는 L1 DTLB 64 entries, shared L2 TLB 1,280 entries다. 1 MiB ROI에서는
DTLB read 65,537회 중 miss가 49,128회였고, 이 요청은 모두 L2 TLB에서 hit했다.
따라서 24.477 ns를 순수 L3 cache array latency로 해석할 수 없다. 반면 128 KiB는
DTLB read miss가 0인데도 13.325 ns/load이므로 해당 경로의 차이를 TLB miss만으로
설명할 수도 없다. Orin의 TLB/cache PMU counter는 이번 측정에 포함하지 않았다.

4 MiB의 짧은 model ROI는 26.441 ns/load였고 긴 조건은 25.901 ns/load였다.
긴 실행의 ROI는 27.1592855 ms, DRAM read는 927,808 B다. 이 run에는 실제 ROI
도중 SIGUSR1 dump를 삽입했다. Collector는 중간 dump와 exit dump를 제외하고
**stats block index 1**의 정확한 begin/end를 선택했으며 checksum/요청 조건 PASS였다.

### Memory 및 prefetch A/B

Prefetch snapshot은 **CHECKPOINT_SAVED**, 해당 snapshot에서 1 MiB cache restore는
**PASS**다. Random pointer-chase는 off/on 모두 **24.476547 ns/load**이고 ROI ticks,
L1/L2/L3 demand counter, DRAM read 64 B까지 동일했다. 이 패턴에서 stride prefetch의
효과는 관찰되지 않았다. 이 결과를 순차 read로 일반화하지 않는다.

| Mode | gem5 유효 GB/s | gem5 DRAM GB/s | Orin 유효 GB/s median | 상태 |
|---|---:|---:|---:|---|
| Read, prefetch off | 41.600 | 41.984 | 61.988 | PASS |
| Read, prefetch stride | 41.782 | 42.158 | 61.988 | PASS |
| Copy | 23.521 | 35.469 | 77.884 | PASS |
| Triad | 32.812 | 43.905 | 71.235 | PASS |

Baseline read의 ROI는 **3.226420 ms**, useful bytes는 134,217,728 B다.
DRAM read 135,110,016 B, write 347,264 B이며 OS traffic도 포함한다.
16개 channel의 read는 각각 8,427,392–8,451,328 B로 모두 사용되었고,
16개 worker 모두 O3 committed instructions가 1,080,027–1,124,432개였다.
여러 diagnostic dump를 제외한 **stats block index 6**으로 집계했다.

이전 같은 입력의 1-pass read는 43.505725 GB/s였고 이번 2-pass는
41.599583 GB/s로 **4.38% 낮다**. 1-pass 값을 그대로 재사용하지 않고 반복 수를
맞춰 다시 측정할 필요가 있음을 보여 준다. 두 조건만으로 반복 수에 따른 완전한
수렴을 확인한 것은 아니다. Orin 비교 값도 같은 2-pass 조건의 median이다.

Stride prefetch-on read는 **41.782484 GB/s**, baseline 대비 **+0.44%**다.
ROI는 3.2122965 ms이며 native `pfIssued=294465`, `pfUseful=286134`를 확인했다.
L2 demand hit fraction은 0.1365%에서 13.3584%로 증가했지만 유효 bandwidth 증가는
작았다. DRAM read도 135,110,016 B에서 135,088,896 B로 거의 같다. 순차 stream에
필요한 데이터를 미리 가져오는 동작이 DRAM의 전체 read 양을 크게 줄이는 것은 아니다.
이 한 조건의 결과를 prefetch 일반 효과나 Arm hardware algorithm의 효과로 확장하지 않는다.
단순 prefetch-on만으로 Orin과의 성능 차이가 해소되었다고 볼 수 없다.

Copy도 출력 배열 검증, guest exit 0, simulator exit 0, collector 검사를 모두
통과했다. ROI는 **11.4123825 ms**, useful bytes는 268,435,456 B다.
DRAM read 269,928,448 B와 write 134,857,728 B가 관찰되었으며,
16개 channel 각각에 read 16,860,992–16,876,928 B와
write 8,416,512–8,441,664 B가 있다. Application byte 수와 DRAM byte 수는
다른 지표이므로 두 bandwidth를 구분한다. DRAM counter에는 OS traffic이 포함되고,
ROI 종료 시 cache에 남은 모든 dirty line을 강제로 drain한 값은 아니다.

Triad도 출력 배열 검증과 정상 종료를 포함해 PASS다. ROI는 **12.2714515 ms**,
useful bytes는 402,653,184 B다. DRAM read 404,142,976 B,
write 134,629,888 B를 관찰했다. 16개 channel 각각에
read 25,252,608–25,264,640 B와 write 8,404,864–8,423,168 B가 있고,
16개 worker의 O3 committed instructions는 각각 8,415,465–8,448,172개다.
여러 중간 dump와 exit dump를 제외한 **stats block index 10**을 사용했다.

Baseline의 DRAM read+write byte 수는 application useful bytes의
Read **1.009배**, Copy **1.508배**, Triad **1.338배**다. 따라서 Copy의
23.521 GB/s를 DRAM traffic 전체의 bandwidth로 취급하면 안 된다.
이번 보강으로 kernel별 byte 정의와 실제 memory traffic을 함께 비교할 수 있다.

이 host에서 launcher가 기록한 실행 시간은 Read 약 **1.87시간**, Copy
**4.81시간**, Triad **5.69시간**이었다. Restore, warmup, ROI와 검증·종료 비용을
포함하는 운영 참고 값이며, 위 성능 값의 분모는 각 simulated ROI 시간이다.

### 결과 해석과 후속 우선순위

- 이번 개선은 read/copy/triad 실행 경로, 충분한 cache 반복 수, 정확한 ROI 선택,
  checksum·worker·channel 검증을 갖춘 측정 방법이다. 기존 model timing은 유지했다.
- Orin의 유효 bandwidth 순서는 Copy > Triad > Read이고, 이 model에서는
  Read > Triad > Copy다. CPU 수와 architecture, cache, memory 구성이 다르므로
  이 차이를 benchmark 오류나 DRAM timing 하나의 문제로 단정할 수 없다.
- Stride prefetch는 실제로 동작했지만 read 증가율은 +0.44%였다. Prefetch를 켜는
  것만으로 hardware와의 차이를 해소하지 못했다.
- Cache timing을 보정하려면 다음에는 Orin의 cache/TLB PMU와 더 긴 반복 측정을
  확보하고 model의 translation, cache hit, fabric 경로를 나누어 비교해야 한다.
  최대 streaming bandwidth가 목표라면 현재 scalar copy/triad와 구분되는 SIMD
  variant를 양쪽에서 같은 machine code로 검증하는 것이 다음 단계다.

## 재현

Repository root에서 실행한다. 아래 명령은 이번 campaign의 고정 입력을 사용하며
기존 snapshot의 contract와 일치해야 한다. 다른 native binary/profile/image로
재빌드했다면 해당 입력으로 새 snapshot을 생성한다.

```bash
evidence=build/qbox-apollo-qvp/gem5/orin-informed-20261023
snapshot=build/qbox-apollo-qvp/gem5/interleave-16core-20261022/snapshot-64
rerun="$evidence/rerun-$(date +%Y%m%d-%H%M%S)"
common=(--headless --cpus 16 --channels 16 --interleave-bytes 64
  --kernel "$evidence/Image-baseline"
  --initrd build/tmp_baremetal/deploy/images/apollo-qvp/nexios-gem5-initramfs-apollo-qvp-20261022102228.cpio.gz
  --timeout 86400)

# Cache: 크기별 65,536 loads, 4 MiB는 1,048,576 loads.
for size in 32 64 128 256 512 1024 4096; do
  passes=$((4096 / size))
  if [ "$size" = 4096 ]; then passes=16; fi
  ./run_gem5_linux.sh "${common[@]}" --resume "$snapshot" \
    --workload cache --size-kib "$size" --passes "$passes" \
    --out-dir "$rerun/cache-${size}KiB"
done

# Memory: array당 64 MiB, 16 workers, warmup 1회 + 측정 2회.
for mode in read copy triad; do
  ./run_gem5_linux.sh "${common[@]}" --resume "$snapshot" \
    --workload dram-multicore --memory-mode "$mode" --workers 16 \
    --size-kib 65536 --passes 2 --out-dir "$rerun/memory-$mode"
done
```

Prefetch 비교는 `--profile`에 `a720ae_prefetch_diagnostic.yaml`을, `--resume`에
이번 campaign의 `snapshot-prefetch-matched`를 함께 지정한다. 정확한 전체 인자는
각 `*-command.json`과 run directory의 `launch.json`에 보존한다. 기본 timeout
7,200초를 넘길 수 있어 이번 campaign은 memory 측정에 86,400초를 지정했다.
Copy/triad는 ROI 종료 후 전체 출력 배열의 정합성 검사까지 완료해야 PASS가 된다.
Host 실행 시간은 성능 분모로 사용하지 않는다.

## Evidence

Campaign:
[`build/qbox-apollo-qvp/gem5/orin-informed-20261023/`](../../build/qbox-apollo-qvp/gem5/orin-informed-20261023/).

| Artifact | 내용 |
|---|---|
| `comparison.json`, `comparison.csv`, `reanalysis.json` | 13개 model 결과와 Orin 비교; 전체 measurement 재집계 일치 |
| `final-verification.json` | 최종 입력 hash, source 기록, 문서 검사와 실행 종료 확인 |
| `baseline-inputs.json`, `kernel-recovery.json` | 입력 contract와 원본 kernel 복구 검증 |
| `profile-delta.json` | Prefetch profile의 effective parameter 차이 |
| `prefetch-snapshot-contract.json` | 두 snapshot의 입력 contract 비교; profile hash만 다름 |
| `compiler-loop-comparison.md` | Guest/Orin compiler 근거, hot loop byte 동등성, 재현 명령 |
| `cache-translation-counters.json` | Cache ROI의 CPU0 DTLB/L2 TLB/page-walk counter; OS 접근 포함 |
| `host-tests.log`, `verification.json` | 26 host tests |
| `read-64-collector-equivalence.json` | 기존 성능 값 및 원본 artifact 보존 확인 |
| `read-convergence.json` | 실제 2-pass PASS, 16-worker/channel 검증, 기존 1-pass와 차이 |
| `read-prefetch-comparison.json` | Prefetch off/on의 실제 ROI, cache/prefetch counter, bandwidth 비교 |
| `orin-matched/summary.json`, `orin-matched/README.md` | Orin 55회 원본·집계·복원 |
| `cache-off-*/`, `memory-off-*/` | Baseline FS run, UART, config, ROI, stats |
| `save-prefetch-matched/`, `snapshot-prefetch-matched/` | Prefetch snapshot 저장 |
| `cache-prefetch-*/`, `memory-prefetch-*/` | Prefetch A/B run |
| `run-*-campaign.py`, `run-cache-baseline.py` | 실제 campaign command orchestration |
| `run-triad-rescheduled.py`, `scheduler-reschedule.json` | Host 자원이 확보된 뒤 triad의 대기를 해제한 실행 기록; 기존 native run은 계속 실행 |
| `memory-off-execution.json`, `memory-read-copy-execution.json`, `triad-rescheduled-execution.json` | 세 memory run의 실제 launcher exit 0 및 정상 완료 기록 |

대기 중이던 triad를 별도로 시작한 뒤, 기존 read/copy launcher의 exit 0을 확인하고
중복 triad가 대기하던 scheduler만 종료했다. `scheduler-reschedule.json`의 shell
exit 143은 이 정리 작업의 예상 결과이며, 세 benchmark의 launcher/simulator는
모두 exit 0이다.

Hardware 성능과 model 성능은 구분한다. CPU 수, cache capacity, prefetch, DRAM과
fabric이 다르므로 상대 차이를 calibration 오차율이나 silicon 정확도로 표시하지 않는다.

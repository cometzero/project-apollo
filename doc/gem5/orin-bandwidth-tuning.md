# Orin 공개 Memory Benchmark 재현과 측정 조건 개선

시험일: **2026-10-23**. 대상: `ssh orin`, Jetson AGX Orin Developer Kit **64 GB**.

기존 single-thread STREAM의 약 20 GB/s는 이 보드의 multicore memory bandwidth를
대표하지 못했다. 동일한 upstream C source에 OpenMP를 활성화하고 12 cores를
사용하자 **Copy 81.930 GB/s, Triad 72.508 GB/s**를 측정했다. `-O2` OpenMP에서도
Copy **82.514 GB/s**가 나왔다. 공개 NVIDIA forum의 64 GB 보드 Copy 72 GB/s를
충족하고, 논문의 CPU 결과와 비슷한 수준이다. DRAM timing이나 channel 설정을
변경해서 얻은 수치가 아니다.

이번 결과는 **37조건 × 독립 실행 5회 = 185회 PASS**다. 공개 자료 조사,
native/Yocto compiler build, hardware 실행, numerical validation, clock/ROS 복원을
완료했다. Production recipe, deploy image, snapshot과 gem5 model parameter는
이번 조사에서 변경하지 않았다.

## 1. 공개 실측값과 비교 대상

검색 확인일은 시험일과 같다. 아래 bandwidth는 별도 표시가 없으면 decimal GB/s다.

| 공개 자료 | Hardware / benchmark | 실측값 | 확인 가능한 조건과 한계 |
|---|---|---|---|
| NVIDIA forum, 2025-04~06 | AGX Orin 32 GB / C STREAM Copy | 사용자 약 54.5, NVIDIA 재시험 약 55 | 사용자 명령은 `-O3 -fopenmp -march=native -DNTIMES=20`, 8 threads, MAXN, `jetson_clocks`; 정확한 compiler/revision/affinity는 없음 |
| 같은 thread, NVIDIA 담당자 | **AGX Orin 64 GB** / C STREAM Copy | **72** | 담당자가 64 GB 제품임을 확인; 담당자 측 thread 수와 실제 clock은 별도로 명시하지 않음 |
| PMBS 2022 논문 | 12-core Orin / Fortran BabelStream OpenMP | Copy **81.836**, Mul 81.734, Add 74.681, Triad **74.573**, Dot 64.838 | GCC 12.2, `-O3 -mcpu=cortex-a78ae`, array당 2²⁷ doubles; 정확한 측정 SHA와 power/clock 조건은 확인되지 않음 |

근거: NVIDIA forum의 [실행 명령](https://forums.developer.nvidia.com/t/jetson-agx-orin-32gb-measured-memory-bandwidth-much-lower-than-theoretical-spec/331766/10),
[72 GB/s 결과](https://forums.developer.nvidia.com/t/jetson-agx-orin-32gb-measured-memory-bandwidth-much-lower-than-theoretical-spec/331766/12),
[64 GB 제품 확인](https://forums.developer.nvidia.com/t/jetson-agx-orin-32gb-measured-memory-bandwidth-much-lower-than-theoretical-spec/331766/16),
[32 GB 재시험](https://forums.developer.nvidia.com/t/jetson-agx-orin-32gb-measured-memory-bandwidth-much-lower-than-theoretical-spec/331766/23).
논문은 [Benchmarking Fortran DO CONCURRENT on CPUs and GPUs Using BabelStream](https://research-information.bris.ac.uk/ws/files/335746139/ws_pmbsf108s1_file1.pdf)의
Table VIII–X, XVII와 Figure 5다. DOI: `10.1109/PMBS56514.2022.00013`.

같은 forum의 CUDA D2D **151.7 GB/s**는 GPU buffer copy 사례다. NVIDIA 담당자도
해당 CUDA sample을 정밀 performance app으로 취급하지 말라고 설명했다.
이를 CPU STREAM의 합격 목표로 사용하지 않는다. Orin의 **204.8 GB/s**도 shared
DRAM의 theoretical bandwidth이며 CPU application의 달성 보장치가 아니다.
[Forum 설명](https://forums.developer.nvidia.com/t/jetson-agx-orin-32gb-measured-memory-bandwidth-much-lower-than-theoretical-spec/331766)

## 2. 실제 시험 환경과 계측

| 항목 | 이번 시험 |
|---|---|
| CPU / cluster | Cortex-A78AE 12 cores; CPU 0–3 / 4–7 / 8–11 |
| Cache | L1I/L1D 각각 64 KiB/core, L2 256 KiB/core, L3 2 MiB/cluster |
| OS / BSP | Ubuntu 20.04.6, Linux 5.10.120-tegra, L4T R35.4.1 |
| Power / clock | 기존 MAXN mode 0 유지; `jetson_clocks`로 CPU min=max 2.2016 GHz, EMC 3199 MHz 설정 |
| Background | 승인된 두 ROS service를 중지; 나머지 desktop/OS service 유지 |
| Compiler | native GCC/gfortran 9.4.0; 별도 Yocto GCC 14.3.0 A78-tuned C build |
| Page / prefetch | 기존 THP `always` 유지, hardware prefetch 설정 변경 없음 |
| Telemetry | `sudo tegrastats --interval 100`; campaign 전체 관찰, 개별 ROI counter는 아님 |

CPU/sysfs topology, compiler version, 명령, binary hash, raw output을 보존했다.
두 긴 campaign의 CPU 온도는 각각 42.843–50.375 °C, 45.406–53.218 °C였다.
Root telemetry가 보고한 EMC frequency는 모두 3199 MHz다. EMC 사용률은 campaign에서
최대 35%였지만 이를 `35% × 204.8 GB/s`로 변환하거나 physical DRAM byte 수로
해석하지 않는다. 짧은 추가 copy/triad 시험은 telemetry 4 samples뿐이다.
모든 throttle counter나 benchmark별 huge-page backing은 조사하지 않았다.

각 campaign은 `jetson_clocks --store`로 원래 설정을 저장하고 종료 trap에서 복원했다.
복원 후 다시 저장한 설정 파일이 원본과 byte 단위로 일치했다. 시작 전 active였던
`dal-e_ros_can_bridge.service`, `dal-e_state_manager.service`는 모두 다시 `active`가
되었고, 이번에 생성한 telemetry process도 종료했다. Service enable 상태는 유지했다.

수치의 정의는 다음과 같다.

- C STREAM: unmodified upstream 5.10, 20 iterations. 첫 iteration을 제외한
  **최소 시간으로 계산된 프로그램의 Best Rate를 독립 5회 실행한 median**이다.
- Fortran BabelStream: 100 iterations, 같은 방식의 5회 median이다.
- Apollo workload: `CLOCK_MONOTONIC_RAW`로 측정한 **전체 8-pass ROI의 useful bytes/time**.
  Init와 warmup은 제외하고 worker barrier와 OS scheduling 영향은 포함한다.
- STREAM Copy/Scale은 double당 16 B, Add/Triad는 24 B다. Copy 82 GB/s는
  payload 복사량으로는 약 41 GB/s이며, read+write를 합한 수치다. Write allocation,
  cache eviction 등을 포함하는 실제 MC bus traffic과 일치한다고 가정하지 않는다.

이는 [STREAM byte 정의 및 실행 규칙](https://www.cs.virginia.edu/stream/ref.html)을 따른다.
이번 C STREAM의 가장 짧은 측정 sample도 1.919 ms로, 관찰된 timer granularity
1 µs의 20배보다 충분히 길었다. 합계 228.9 MiB 조건은 array당 76.3 MiB로
Orin의 합계 L3 6 MiB보다 충분히 크다. 기존 1.5 MiB `stream-gem5-cache`는 별도의
cache 시험이며 이 DRAM 비교에 포함하지 않았다.

## 3. C STREAM: 무엇이 성능을 바꾸었는가

배열은 각각 10,000,000 doubles, 합계 240,000,000 B = 약 228.9 MiB다.
아래는 native GCC 9.4 결과다. `-march=native`는 이 compiler에서
`-march=armv8-a`, `-mcpu=generic`, `-mtune=generic`으로 해석되었다.

| Compile / thread 조건 | Copy | Scale | Add | Triad |
|---|---:|---:|---:|---:|
| `-O2`, serial, CPU 0 | 20.037 | 19.982 | 16.765 | 16.769 |
| `-O3 -fopenmp`, 8 threads, affinity 미지정 | 73.528 | 73.024 | 65.918 | 65.345 |
| `-O3 -fopenmp`, 12 threads, close | **81.930** | 82.141 | 73.194 | **72.508** |
| `-O2 -fopenmp`, 12 threads, close | **82.514** | 83.025 | 74.236 | **72.992** |

단위: GB/s, 독립 5회 median. 12-thread `-O3` Copy 범위는
81.255–82.010 GB/s, sample CV 0.38%다. `-O2` Copy는 82.010–82.646 GB/s,
CV 0.30%였다. `-O3`만 적용한 serial Copy는 20.172 GB/s이므로
주요 개선은 **OpenMP를 통한 concurrency**다. 이 source에서는 `-O3`가 `-O2`보다
항상 빠르지 않았다. 12-thread `-O2` Copy는 serial `-O2`의 약 **4.12배**다.

Upstream의 Best Rate와 sustained average를 구분해야 한다. 12-thread `-O3`에서
각 실행의 평균 iteration 시간으로 환산한 bandwidth의 median은 Copy **78.278**,
Triad **69.105 GB/s**다. `summary.csv`에 best/average 기반 수치를 함께 남겼다.

### 8 threads의 affinity

다음은 같은 `-O3` binary다. 배치는 `OMP_DISPLAY_AFFINITY=TRUE`로 확인했다.

| 설정 | 실제 CPU 목록 | Cluster별 threads | Copy | Triad |
|---|---|---|---:|---:|
| `OMP_PLACES=cores`, close | 0–7 | 4 / 4 / 0 | 55.572 | 49.190 |
| `OMP_PLACES=cores`, spread | 0,2,4,6,8,9,10,11 | 2 / 2 / 4 | 55.306 | 49.231 |
| 명시적 places, close | 0,1,2,4,5,6,8,9 | **3 / 3 / 2** | **73.159** | **64.952** |
| binding 미지정 | scheduler 선택, 고정 목록 없음 | 실행 중 배치 미추적 | 73.528 | 65.345 |

명시적 배치는 `spread`보다 Copy가 **32.3%** 높았다. OpenMP `spread`는 CPU place
분산 규칙이며 L3 cluster별 작업량 균등화를 보장하지 않는다. 같은 크기의 array
partition을 worker마다 주면 cluster에 4 workers가 몰린 경우 해당 cluster의
완료 시간이 전체 barrier를 제한할 수 있다. 결과는 이 설명과 일치하지만
L3/NoC/MC 중 특정 회로를 PMU로 bottleneck이라고 확정한 것은 아니다.

4-thread `-O3`에서도 CPU 0–3 close는 Copy 27.991 GB/s,
CPU 0,3,6,9 spread는 55.766 GB/s였다. **Thread 수만 적고 affinity를 생략하면
재현 조건이 충분하지 않다.** 이번 보드의 최대 CPU throughput 기준에는
12 threads를 CPU 0–11에 고정하는 설정이 단순하고 재현 가능하다.

### Working set과 compiler 교차 확인

| 조건 | Working set 합계 | Copy | Triad |
|---|---:|---:|---:|
| GCC 9.4, `-O3`, 12 close | 228.9 MiB | 81.930 | 72.508 |
| Yocto GCC 14.3, `-O3 -mcpu=cortex-a78`, 12 close | 228.9 MiB | 82.181 | 72.461 |
| GCC 9.4, `-O3`, 12 close | **3 GiB** | 79.681 | 71.837 |
| Yocto GCC 14.3, A78 tuning, 12 close | **3 GiB** | 79.469 | 71.848 |

3 GiB 조건은 array당 134,217,728 doubles다. 크기를 늘려도 약 80/72 GB/s가
유지되므로 228.9 MiB 결과를 단순한 cache-resident 효과로 설명하기 어렵다.
Compiler upgrade/A78 tuning만으로 큰 추가 향상은 관찰하지 못했다.

Yocto binary는 해당 sysroot의 loader, libc, libm, libgomp 등과 private directory에서
실행했다. Ubuntu system library는 교체하지 않았다. 첫 시도에서는 glibc compatibility
library 누락으로 host `libpthread.so.0`가 섞여 `GLIBC_PRIVATE` symbol 오류가 발생했다.
같은 sysroot의 libpthread/libdl/librt를 포함해 해결했고, 실패 로그도 보존했다.

## 4. 논문의 Fortran BabelStream 교차 확인

논문의 `fortran-ports` branch는 검색 시점에 삭제되어 있었다. 저자 fork의 보존
branch `fortran-ports-with-scripts`, commit
[`87eb07e4a8c3e8d6247ab5f72e14bf90002733ce`](https://github.com/jeffhammond/BabelStream/tree/87eb07e4a8c3e8d6247ab5f72e14bf90002733ce)를 사용했다.
2022-11-09 revision이며 **논문 측정 당시 정확한 SHA임을 확인한 것은 아니다**.
원본 Fortran source 세 파일은 수정하지 않았다.

Native gfortran 9.4, `-std=f2018 -O3 -march=armv8.2-a -mtune=cortex-a76 -fopenmp`,
REAL64, 12 threads, close/cores, array당 2²⁷ elements, 100 iterations로 실행했다.
GCC 9.4는 A78AE tuning을 지원하지 않아 호환 옵션을 사용했다.
측정 배열은 3 GiB이며 source가 검증 배열 3 GiB를 추가로 할당한다.

| Kernel | 논문 GCC 12.2 | 이번 GCC 9.4 median | 이번 범위 | 논문 대비 |
|---|---:|---:|---:|---:|
| Copy | 81.836 | **79.803** | 79.697–79.839 | −2.48% |
| Mul | 81.734 | 79.816 | 79.778–79.819 | −2.35% |
| Add | 74.681 | 71.845 | 71.825–71.900 | −3.80% |
| Triad | 74.573 | **71.857** | 71.806–71.961 | −3.64% |
| Dot | 64.838 | 61.236 | 61.204–61.278 | −5.56% |

정확한 toolchain/OS/source/clock 동등성을 확보한 재현은 아니지만, CPU memory
성능 범위가 유사함을 확인했다. Source의 array·Dot validation을 실행했고, 실패 시
exit 0일 수도 있으므로 종료 코드와 함께 `Validation failed` 부재, 다섯 결과 행,
array 크기, 반복 수, thread affinity를 검사했다.

## 5. 기존 Apollo benchmark도 보강 가능한가

기존 host binary 그대로 12 workers / 8 passes / warmup 1회로 시험했다.
`--mode copy`, `--mode stream`은 C loop이며 표의 `scalar`는 source option 이름이다.
Compiler의 auto-vectorization까지 금지한다는 뜻은 아니다.

| 기존 workload | Array당 크기 / 총 working set | Useful bandwidth median | 5회 범위 |
|---|---|---:|---:|
| NEON read, phase off | 64 MiB / 64 MiB | 59.426 | 54.611–64.093 |
| NEON read, phase on | 64 MiB / 64 MiB | **64.037** | 63.691–64.486 |
| NEON read, phase off / on | 256 MiB / 256 MiB | 61.882 / 61.928 | 56.868–62.009 / 61.582–61.957 |
| NEON read, phase off / on | 512 MiB / 512 MiB | 61.029 / 60.408 | 59.328–61.593 / 59.125–61.426 |
| `--mode copy --kernel scalar` | 64 MiB / 128 MiB | **78.127** | 63.238–78.848 |
| `--mode stream --kernel scalar` | 64 MiB / 192 MiB | **70.862** | 67.346–71.088 |

모든 checksum/array validation은 PASS다. Copy의 실행 간 CV는 8.96%이며
낮은 sample도 삭제하지 않았다. 이는 전체 8-pass ROI 평균이므로 STREAM의
best iteration 수치와 통계가 다르다.

`--channel-phase-spread`는 worker별 virtual 시작 주소를 64 B씩 이동한다.
Orin의 physical channel selector를 확인하거나 바꾼 시험이 아니다. 이번 64 MiB
phase-off 결과는 CV 7.90%로 분산이 컸고, [직전 시험](orin-validation-results.md)의
같은 off 조건 median은 63.734 GB/s였다. 큰 working set에서 일관된 향상이 없으므로
phase-on을 일반적인 hardware bandwidth 개선책으로 단정하지 않는다.

NEON read는 8개 accumulator에 floating-point 합산을 수행한다. STREAM Copy의
read+write byte 정의와도 다르다. Read가 약 64 GB/s이고 Copy가 약 80 GB/s라는
사실만으로 read benchmark가 잘못되었다고 판단하지 않는다. 공개 Copy/Triad와
비교할 때는 **같은 kernel과 byte 정의**를 선택해야 한다.

## 6. 현재 설정에 적용할 권고

| 우선순위 | 보강할 항목 | 근거 / 적용 범위 |
|---|---|---|
| 1 | Hardware DRAM 기준은 upstream STREAM OpenMP, 12 threads, 명시적 affinity로 측정 | 이번 보드에서 약 82/73 GB/s 확인 |
| 2 | 기존 read 외에 copy/triad도 함께 측정 | 기존 Apollo binary도 약 78/71 GB/s 확인; kernel별 한계 분리 |
| 3 | MAXN 확인, clock 고정, background 통제와 복원, root telemetry 보존 | thread/clock/page 상태가 benchmark 입력의 일부 |
| 4 | Cache용 축소 STREAM과 DRAM용 working set을 분리 | 1.5 MiB cache 점수를 LPDDR bandwidth로 표시하지 않음 |
| 5 | 5회 이상 반복, 최소 시간 기반 점수와 전체 ROI 평균·분산 동시 기록 | outlier를 지워 최고 수치만 제시하지 않음 |
| 6 | gem5에서 같은 kernel, compiler, working set, ROI 조건을 먼저 맞춤 | hardware 숫자에 맞추려고 DRAM timing/queue를 임의 조정하지 않음 |

기존 [STREAM recipe](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/stream/stream_5.10.bb)는
`STREAM_CPPFLAGS`를 compile/link command에 이미 전달한다. 별도의 STREAM source
patch 없이 다음 opt-in 설정이 가능하다.

```bitbake
STREAM_CPPFLAGS:pn-stream = "-O3 -fopenmp -DNTIMES=20"
```

이번에는 OpenMP·반복 수 조건을 native/Yocto compiler별 artifact로 build하여
Orin에서 검증했다. Orin 전용 A78 tuning을 Apollo guest의 기본 CPU flag로 바꾸지는 않는다.
위 override를 넣은 **BitBake image/package 빌드나 gem5 부팅은 수행하지 않았다**.
Image 통합 시 `libgomp` runtime 포함과 thread 수를 확인해야 한다. 기존 recipe의
single-thread 기본값과 `stream-gem5-cache`를 이번 hardware 조사에서 덮어쓰지 않았다.

2 GiB gem5 guest에는 논문의 **측정 배열 3 GiB** 조건이 들어가지 않는다.
Orin과 공통 DRAM 조건을 새로 만들 때는 예를 들어 array당 2²⁴ doubles
(128 MiB, 총 384 MiB)를 선택하고 같은 크기를 양쪽에서 실행할 수 있다.
이는 후속 시험 제안이며 이번 실행 결과가 아니다. Relevant LLC/SLC 용량과 실제
ROI의 channel별 DRAM bytes를 함께 확인한다.

Gem5 측 후속 A/B에서는 [현재 L2 설정](model-design.md)의
`cache.l2.prefetch: 'off'`와 지원되는 `'stride'`를 먼저 구분할 수 있다.
Orin에서는 hardware prefetch를 비활성화하지 않았으므로 접근 패턴별 비교가 필요하다.
이어 CPU LQ/SQ, Ruby data sequencer outstanding, cache TBE, channel queue의
실제 stall/occupancy를 확인한 뒤 한 항목씩 검토한다. 이 sensitivity 시험은 이번에
실행하지 않았으며 gem5의 stride prefetcher가 Arm hardware algorithm과 같다는 뜻도 아니다.

현재 Apollo는 A720AE proxy 16 cores, L3/SLC, LPDDR5X profile이고 Orin은 A78AE
12 cores/LPDDR5다. Launcher/firmware도 현재 4/16 CPUs만 지원하므로 `--cpus 12`로
Orin 구성을 즉시 복제할 수 없다. 이번 결과는 **benchmark 방법과 hardware reference의
확인**이며 Apollo model calibration 완료를 뜻하지 않는다. DRAM controller 자체의
최대 처리량은 CPU benchmark와 별도로 synthetic traffic 또는 GPU/DMA 경로에서
평가할 수 있지만, 이번에 그 경로를 시험하지는 않았다.

## 7. 재현 명령과 evidence

보드에 보존한 campaign:

```text
/home/hyundai/apollo-orin-bandwidth-tuning-20261023/
```

다음 명령은 binary를 실행하며 clock/ROS 상태는 직접 변경하지 않는다.
동일 조건 재현에는 2절의 저장·설정·복원이 필요하다.

```sh
ssh orin
cd /home/hyundai/apollo-orin-bandwidth-tuning-20261023/attempt-2/bundle

# Upstream source 그대로, 원래 10M doubles/array
gcc -O3 -fopenmp -march=native -DNTIMES=20 stream.c -o stream-omp
OMP_NUM_THREADS=12 OMP_DYNAMIC=FALSE OMP_PROC_BIND=close \
  OMP_PLACES=cores OMP_DISPLAY_AFFINITY=TRUE ./stream-omp

# 8 threads를 세 cluster에 3/3/2로 배치
OMP_NUM_THREADS=8 OMP_DYNAMIC=FALSE OMP_PROC_BIND=close \
  OMP_PLACES='{0},{1},{2},{4},{5},{6},{8},{9}' \
  OMP_DISPLAY_AFFINITY=TRUE ./stream-omp

cd ../../followup-2/package
OMP_NUM_THREADS=12 OMP_DYNAMIC=FALSE OMP_PROC_BIND=close OMP_PLACES=cores \
  ./build-orin/BabelStream.gcc.OpenMP -s 134217728 -n 100 --csv

cd ../../modes
./bundle/apollo-memory-bench --host --workers 12 --mode stream \
  --kernel scalar --array-mib 64 --passes 8 --initialize-before-switch
```

Local evidence는
[`build/qbox-apollo-qvp/gem5/orin-bandwidth-tuning-20261023/`](../../build/qbox-apollo-qvp/gem5/orin-bandwidth-tuning-20261023/)다.

| Artifact | 내용 |
|---|---|
| `source-manifest.json`, `yocto-build.json` | C source SHA, cross compiler command / binary provenance |
| `babelstream-reference/package/` | 고정 Fortran source, LICENSE, build script, revision 및 SHA |
| `remote/attempt-2/results/` | 25 STREAM 조건 × 5회, raw log와 `runs.json`, native build command |
| `remote/followup-2/results/` | 8-thread 균형 배치 3조건, NEON 6조건, BabelStream 1조건 × 5회 |
| `remote/modes/results/` | 기존 Apollo copy/triad 2조건 × 5회 |
| 각 remote campaign의 `hardware-*.json`, `clocks-*.conf`, `ros-*.txt`, `tegrastats-root.log` | 환경·telemetry·복원 증거 |
| `summary.json`, `summary.csv`, `summarize.py` | 185회 집계, median/min/max/sample CV, 복원·행 수 assertion |
| `artifact-sha256.json`, `remote/compiler-native-options.txt` | 회수한 source/binary/runtime/log hash와 GCC native target 해석 |
| `run-stream-matrix-2.sh`, `run-followup-2.sh`, `run-modes.sh` | clock/ROS lifecycle 및 실패 시 복원 script |

C source SHA256:
`a52bae5e175bea3f7832112af9c085adab47117f7d2ce219165379849231692b`.
기존 Apollo host binary SHA256:
`0adea2e2295862aacaf559f015d77cb2901193af51aa30e8fca8a479782f61b0`.

집계에서 제외한 준비 실패도 보존했다. `remote/` 최상위 첫 STREAM 시도는 앞서
설명한 private runtime 오류다. `remote/followup/` 첫 추가 시도는 collector가 정상
출력의 `avg error less than`을 오류로 오인한 assertion 실패다. 검사를 실제
validation failure 문구로 제한하고 새 directory에서 전 조건을 다시 실행했다.
두 실패 시도에서도 clock과 ROS 복원을 확인했다. 최종 185회 결과에 실패한 준비
시도의 수치를 섞지 않았다.

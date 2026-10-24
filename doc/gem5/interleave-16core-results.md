# DRAM interleave와 16-core workload 검증

시험 시작일: 2026-10-22. 모든 수치는 Apollo AP-only **uncalibrated gem5 model**의
결과다. Thor physical memory controller, PHY 또는 silicon bandwidth 검증은 아니다.

## 조건과 구현

| 항목 | 조건 |
|---|---|
| Linux RAM | 2 GiB, PA `0x80000000..0xffffffff` |
| CPU | Cortex-A720AE proxy 16 cores, 4 clusters, 2 GHz |
| Boot / ROI CPU | AtomicSimpleCPU / O3 |
| Memory | LPDDR5X-8533 proxy, 16 channels × x16-bit |
| Channel stripe | 64 B baseline, 512 B, 1024 B |
| Home mapping | 8 Home nodes, 64 B stripe 유지 |
| Linux workload | NEON read, 총 64 MiB, 16 pinned workers, worker당 4 MiB |
| 반복 | O3 warmup 1 pass + measured 1 pass |
| Allocation / init | Atomic 구간, CPU switch 이전 |
| Profile | `a720ae_documented.yaml`, NPU disabled |

Channel selector는 64/512/1024 B 순서로 `(PA >> 6/9/10) & 15`다.
Home selector는 세 조건 모두 `(PA >> 6) & 7`이다. RAM capacity, DRAM timing,
device width, burst length는 변경하지 않았다. 512/1024 B에서 Home과 channel의
선택 관계가 달라지므로 CPU/CMN 경로 변화까지 포함하는 비교다.

변경한 소유 경계:

- gem5 repository: address mapping, parameter validation, `run_fs.py`,
  native configuration verifier, backend traffic tests, 기존 `memory_bench.c`.
- meta-hsoc-auto-solutions: `gem5-apollo-guest.bb`에서 static
  `apollo-memory-bench` compile/install/deploy.
- root: `run_gem5_linux.sh`의 Python launcher에 `--interleave-bytes`,
  `--workload dram-multicore`, `--workers` 연결과 결과 collector.

Workload는 실제 warmup checksum을 검증해 compiler가 read warmup을 제거하지 못하게
한다. 각 worker의 `DSB SY`, collective barrier, CPU0의 단일 marker로 ROI를 구분한다.
Thread teardown은 ROI 종료 후 수행한다. DSB가 dirty cache 전체를 DRAM으로 flush하는
것은 아니며, 본 실험은 read workload다.

## Build와 기능 검사

```sh
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j2 \
  ./yocto_build.sh --gem5 --keep-conf
```

`apollo-qvp` / `auto-ad-nexios` / `tmp_baremetal` 기존 설정을 유지했다.
4,167 tasks 성공, 4,133 tasks 재사용. 기존 kernel forced `do_compile` taint 관련
warning이 남아 있으므로 pristine kernel 재빌드라고 주장하지 않는다.

Image: `nexios-gem5-initramfs-apollo-qvp-20261022102228.cpio.gz`

```text
SHA256 dbf3202551898871dee98ca7cf7649c2d87ddce3fd433e6d390813716ada0ae4
```

CPIO에서 benchmark executable을 직접 추출해 AArch64 ELF와 실행 권한을 확인했다.
추출한 `apollo-memory-bench`의 QEMU user-mode 기능 검사에서 64 MiB / 16 workers /
NEON / 1 pass의 checksum과 warmup checksum이 모두 **8,388,608**로 일치했다.
이 결과는 workload 기능 검사이며 memory timing 결과가 아니다.

| 검사 | 결과 |
|---|---|
| Root launcher/collector/control/tmux regression | 25 PASS |
| Initramfs / Yocto selector regression | 7 PASS |
| AArch64 memory workload regression | 5 PASS |
| Parameter tests | 17 PASS |
| Native AddrRange / CPU / backend tests | 10 PASS |
| Backend drain accounting tests | 9 PASS |
| 실제 512-B FS config를 사용한 mutation tests | 19 PASS, NPU 전용 2 SKIP |
| 세 stripe의 실제 config/DTB 검증 | 모두 PASS; 16 private L2 / 4 shared L3 |

## Native DRAM backend 시험

각 channel에 동일한 local sequential stream을 직접 공급했다. 공급 중단 후 native
drain이 완료되고 generated/completed packet 및 DRAM serviced bytes가 일치함을
확인했다. 세 조건에서 DRAM parameter fingerprint가 같고 실제 AddrRange mask는
각 stripe에 맞게 달랐다.

| Channel stripe | ROI | DRAM read bytes | DRAM bandwidth | Channel 분포 | Drain |
|---|---:|---:|---:|---|---|
| 64 B | 20 µs | 5,116,928 | 255.8464 GB/s | 16 channels 동일 | PASS |
| 512 B | 20 µs | 5,116,928 | 255.8464 GB/s | 16 channels 동일 | PASS |
| 1024 B | 20 µs | 5,116,928 | 255.8464 GB/s | 16 channels 동일 | PASS |

각 channel의 ROI read는 319,808 bytes다. 동일한 local traffic을 직접 주입하므로 세
수치가 같은 것이 정상이다. 이 시험은 CPU/cache/CHI를 거치지 않으며 아래 Linux
workload의 bandwidth나 interleave 우열을 대신하지 않는다.

Yocto build 후 최종 `gem5.opt`로 세 조건을 다시 실행해 같은 결과를 확인했다.

## Linux snapshot 및 16-core ROI

세 설정 모두 16-core Linux boot와 snapshot 저장에 성공했다. 저장 tick은 모두
`618635810000`으로 같으며 kernel/image/CPU 구성도 동일하다. Interleave 값이 각
snapshot의 launcher 및 model compatibility contract에 포함되어 있다.

| Stripe | initramfs READY (host) | Snapshot 저장 완료 (host) | 상태 |
|---|---:|---:|---|
| 64 B | 1886.49 s | 1911.47 s | CHECKPOINT_SAVED |
| 512 B | 1906.73 s | 1932.22 s | CHECKPOINT_SAVED |
| 1024 B | 1929.52 s | 1955.64 s | CHECKPOINT_SAVED |

세 simulation을 병렬 실행한 host 시간이다. 이 시간으로 DRAM 성능을 비교하지 않는다.

각 snapshot에서 독립적으로 복원한 세 실행 모두 **PASS**다. Guest checksum과
warmup checksum은 모두 **8,388,608**, `APOLLO_WORKLOAD_EXIT=0`, simulator exit code는
0이며 timeout 없이 PSCI system-off로 종료됐다. 최종 ROI에서 **16 O3 cores 모두의
committed instructions**와 **16 DRAM channels 모두의 read traffic**을 확인했다.

| Stripe | ROI simulated time | Useful read | DRAM read + write | 64 B 대비 useful 변화 | 상태 |
|---|---:|---:|---:|---:|---|
| 64 B | 1.542530 ms | **43.5057 GB/s** | 43.7974 GB/s | 기준 | PASS |
| 512 B | 2.056958 ms | 32.6253 GB/s | 32.9579 GB/s | −25.01% | PASS |
| 1024 B | 2.098695 ms | 31.9765 GB/s | 32.3154 GB/s | −26.50% | PASS |

Useful bandwidth는 `64 × 2^20 bytes / ROI seconds / 10^9`다. DRAM bandwidth는
동일 ROI의 native DRAM read/write burst bytes 합계로 계산한다. Guest의 page-table,
barrier 및 Linux activity도 ROI에 포함되므로 두 byte 수는 정확히 같지 않다.

| Stripe | DRAM read bytes 합계 | DRAM write bytes 합계 | Channel당 read 최소 / 최대 |
|---|---:|---:|---:|
| 64 B | 67,425,408 | 133,376 | 4,206,656 / 4,217,600 |
| 512 B | 67,649,024 | 143,936 | 4,219,776 / 4,242,624 |
| 1024 B | 67,655,872 | 164,224 | 4,212,672 / 4,249,536 |

따라서 2 GiB RAM에서 총 64 MiB를 읽는 이번 workload는 **세 stripe 모두 16 channels에
거의 균등한 누적 read traffic**을 발생시켰다. 누적 분포만으로 매 순간의 channel
동시 사용률이나 queue imbalance까지 같다고 판단하지 않는다.

| Stripe | Read row-hit | Queue latency | Memory access latency | Bus utilization |
|---|---:|---:|---:|---:|
| 64 B | 0.00% | 37.62 ns | 64.49 ns | 16.04% |
| 512 B | 55.62% | 92.23 ns | 119.10 ns | 12.07% |
| 1024 B | 61.84% | 101.20 ns | 128.07 ns | 11.83% |

이 표는 native DRAM의 `readRowHitRate`, `avgQLat`, `avgMemAccLat`, `busUtil`에 대한
**16개 channel 평균값의 산술평균**이다. Request 수로 가중한 global 평균은 아니다.
이번 모델과 workload에서는 큰 stripe가 row locality를 높였지만 queue 대기도 증가했고
유효 bandwidth는 감소했다. Home/channel 선택 관계와 시간별 traffic 분포가 함께
달라지므로, 특정 channel camping이나 CMN bottleneck을 단일 원인으로 단정하려면
별도 address/time trace가 필요하다. 현재 기본값 **64 B를 유지**하고 512/1024 B는
비교 옵션으로 제공한다.

Restore부터 guest 종료까지 host 시간은 각각 4,384.90 / 4,587.50 / 4,383.46 s였다.
Atomic 초기화, O3 warmup, ROI 및 종료 처리가 포함되고 세 simulation을 병렬 실행했으므로
이 시간을 bandwidth 분모로 사용하지 않는다.

진행 확인에 native `SIGUSR1` statistics dump를 warmup과 ROI 중간에 사용했다.
이 signal은 statistics reset을 수행하지 않는다. Collector는 ROI begin/end tick과
일치하는 block을 선택하므로 중간 dump나 최종 exit dump를 성능 계산에 더하지 않는다.
선택된 ROI block index는 64/512/1024 B 순서로 3/4/4이며 각 tick과 counter는
`comparison.json` 및 각 실행의 `m5out/roi-summary.json`에 보존했다.

## 재현과 evidence

실행 명령과 ROI 의미는 [Benchmark guide](benchmark-guide.md#8-16-core-dram-interleave-비교)를 따른다.

현재 build artifact와 64-B snapshot을 사용하는 16-core 재실행 예:

```sh
./run_gem5_linux.sh --cpus 16 --channels 16 --interleave-bytes 64 \
  --resume build/qbox-apollo-qvp/gem5/interleave-16core-20261022/snapshot-64 \
  --workload dram-multicore --workers 16 --size-kib 65536 --passes 1 \
  --out-dir build/qbox-apollo-qvp/gem5/interleave-16core-rerun-64 \
  --timeout 86400
```

기본 tmux UART/platform log 화면으로 실행하며 F12로 종료한다. 자동 실행은
`--headless`를 추가한다. `--out-dir`은 새 경로를 사용하고, 512/1024 B를 시험할 때는
`--interleave-bytes`와 `snapshot-N`을 함께 변경한다. 바이너리·image·configuration이
바뀌면 compatibility 검사를 우회하지 말고 matching artifact나 새 snapshot을 사용한다.

기본 evidence directory는 `build/qbox-apollo-qvp/gem5/`다.

| 경로 | 증거 |
|---|---|
| `interleave-16core-20261022/backend-verification.json` | 최종 native 바이너리의 세 backend 측정과 drain accounting |
| `interleave-16core-20261022/backend-{64,512,1024}/` | backend config/traffic manifest/stats/log |
| `interleave-16core-20261022/campaign.json` | CPU/workload/stripe 조건, source와 configuration hash |
| `interleave-16core-20261022/source-*.patch` | 시험 시 owning repository의 tracked diff |
| `interleave-16core-20261022/image-build.log` | Yocto build |
| `interleave-16core-20261022/image-inspection.json` | 실제 CPIO executable/hash |
| `interleave-16core-20261022/image-functional.log` | image 내 workload 기능 검사 |
| `interleave-16core-20261022/snapshot-verification.json` | 세 snapshot의 완료 상태, tick, hash contract |
| `interleave-16core-20261022/comparison.json` | 최종 세 ROI의 bandwidth, latency, core/channel 분포 비교 |
| `interleave-16core-20261022/final-verification.json` | 최종 artifact와 snapshot compatibility 재확인 |
| `interleave-16core-20261022/warmup-progress*.json`, `roi-progress*.json` | 중간 진행 상태; 성능 비교값 아님 |
| `interleave-16core-20261022/save-N/` | 최초 boot, config/DTB 검증, checkpoint save |
| `interleave-16core-20261022/snapshot-N/` | stripe N의 snapshot과 compatibility contract |
| `interleave-16core-20261022/read-N/` | snapshot restore, UART, ROI events/stats/summary |

단일 pass로 통계적 variance나 sustained bandwidth 수렴을 입증하지 않는다.
Hardware 유효 최고 성능으로 해석하려면 별도 calibration과 traffic/MLP/queue 분석,
반복 수렴 시험이 필요하다.

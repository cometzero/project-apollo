# Apollo SI CL1 benchmark 결과

검증일: 2026-10-24. [구성 및 재현 가이드](si-cl1-zephyr-guide.md).
Evidence: `build/qbox-apollo-qvp/gem5/si-cl1-integration-20261024/final-report/`.
Minor 1 GHz, SRAM 20 ns, TCM 1 ns, 4 PE, counter 100 MHz 조건이다.

Backend: `gem5`, 기능: **PASS**, 주기 작업 deadline: **PASS**.

측정값은 guest counter 기준이다. QEMU 값은 기능 검사이며, gem5 값도 실물 보정 전 모델값이다.

| 대상 | 동작 | working set (KiB) | 시간 (µs) | 유효 GB/s | ns/access |
|---|---|---:|---:|---:|---:|
| TCM | read | 16 | 41.490 | 3.159 | 2.532 |
| TCM | write | 16 | 164.010 | 0.799 | 10.010 |
| TCM | chase | 16 | 10.300 | 0.795 | 10.059 |
| L1 | read | 16 | 48.280 | 2.715 | 2.947 |
| L1 | write | 16 | 164.000 | 0.799 | 10.010 |
| L1 | chase | 16 | 10.290 | 0.796 | 10.049 |
| L2 | read | 256 | 1147.330 | 1.828 | 4.377 |
| L2 | write | 256 | 2621.620 | 0.800 | 10.001 |
| L2 | chase | 256 | 245.800 | 0.533 | 15.002 |
| SRAM_NC | read | 256 | 5571.030 | 0.376 | 21.252 |
| SRAM_NC | write | 256 | 5242.860 | 0.400 | 20.000 |
| SRAM_NC | chase | 256 | 655.440 | 0.200 | 40.005 |

chase의 GB/s는 실제 SRAM bus traffic이 아니라 8-byte 종속 load의 유효 처리량이다.

| 조건 | 경계 | samples | min (ns) | mean (ns) | p95 (ns) | max (ns) |
|---|---|---:|---:|---:|---:|---:|
| idle/cpu0 | timer_to_isr | 16 | 360.0 | 363.1 | 400.0 | 400.0 |
| idle/cpu0 | isr_to_thread | 16 | 14580.0 | 16274.4 | 18540.0 | 18540.0 |
| loaded/cpu0 | timer_to_isr | 8 | 340.0 | 351.2 | 360.0 | 360.0 |
| loaded/cpu0 | isr_to_thread | 8 | 12350.0 | 22127.5 | 53110.0 | 53110.0 |
| loaded/cpu1 | timer_to_isr | 8 | 350.0 | 357.5 | 400.0 | 400.0 |
| loaded/cpu1 | isr_to_thread | 8 | 12340.0 | 27221.2 | 63580.0 | 63580.0 |
| loaded/cpu2 | timer_to_isr | 8 | 350.0 | 356.2 | 400.0 | 400.0 |
| loaded/cpu2 | isr_to_thread | 8 | 12380.0 | 26098.8 | 43210.0 | 43210.0 |
| loaded/cpu3 | timer_to_isr | 8 | 340.0 | 355.0 | 390.0 | 390.0 |
| loaded/cpu3 | isr_to_thread | 8 | 14410.0 | 26777.5 | 68210.0 | 68210.0 |

p95는 nearest-rank 방식이다. 조건별 8/16 samples의 관찰 최대값은 WCET 보증이 아니다.

| CPU | priority | period (µs) | deadline (µs) | releases | misses | skipped | max response (µs) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 250 | 250 | 8 | 0 | 0 | 54.18 |
| 1 | 2 | 500 | 500 | 8 | 0 | 0 | 64.65 |
| 2 | 3 | 1000 | 1000 | 8 | 0 | 0 | 44.27 |
| 3 | 4 | 2000 | 2000 | 8 | 0 | 0 | 69.38 |

Serial SHA256: `afbdd9657002a4a4296c64a8b197b8e990891118e59b87cda8168851ce24b0ac`.

CPU: `minor`, host time: 151.43 s.
ELF SHA256: `e94f0a067c3d711194bc18aa04d8afef52cab55a98db1addc7d50305f1dc42b5`.
gem5 SHA256: `68a4cbd6579644fe32f59086b67dad406dfaae3d47d2cff6ac26d7a5c0f797dc`.

Deterministic ROI replay 및 12개 메모리 경로: **PASS**. TCM/NC byte 오차 허용은 1%, cache hit 판정은 99% 이상이다. 구간별 counter와 경로 검사는 metrics.json에 보존했다.

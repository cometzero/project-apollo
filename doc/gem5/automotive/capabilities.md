# 현재 Apollo gem5 구성과 지원 경계

기준일: **2026-10-26**. 아래는 현재 source contract와 기존 보고서의 증거를 구분한 inventory다.
실행마다 `m5out/config.json`, profile, binary hash로 effective configuration을 확인한다.
상위 설명은 [Model design](../model-design.md), 실행은 [Run guide](../run-guide.md)를 참조한다.

## AP CPU, cache, fabric, memory

| 영역 | 현재 구성 | 의미 있는 실험 | 해석 한계 |
|---|---|---|---|
| CPU | root launcher 4/16 cores, Atomic boot → O3 ROI | affinity, multicore scaling, CPU stall 원인, compiler A/B | generic `ArmO3CPU` 기반 A720AE proxy |
| Cache | core별 L1I/L1D 64 KiB, L2 512 KiB, cluster별 DSU L3 4 MiB | working set, shared-data placement, prefetch, cache/queue sensitivity | cache 용량이 같아도 실물 hit latency·replacement·prefetch와 동일하지 않음 |
| Fabric | Ruby CHI/Garnet, 6×4 mesh, 8 HNF, SLC 합계 4 MiB | home 분포, link/router contention, topology sensitivity | CMN-S3AE 물리 구현 및 모든 CHI 속성을 재현하지 않음 |
| DRAM | 2 GiB, 4/8/16 channels, channel당 16-bit, 8533 MT/s | channel/interleave/queue/read-write mix 비교 | LPDDR5X timing proxy, silicon DMC/PHY 재현 아님 |
| Address interleave | stripe 64/512/1024 B, XOR 없음 | sequential/strided 주소의 channel balance | Linux VA 연속성이 PA 연속성을 보장하지 않음 |

Root launcher의 허용값은 [run_linux.py](../../../scripts/gem5/run_linux.py),
고정 geometry와 profile validation은
[parameters.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/parameters.py)에 있다.
하위 `run_fs.py`가 8 cores를 허용하더라도 root launcher의 지원 범위는 4/16이다.
현재 capacity validator는 2 GiB 고정이므로 512 MiB 구성을 이미 지원한다고 쓰지 않는다.

[cpu_profile.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/cpu_profile.py)와
[a720ae_fu.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/a720ae_fu.py)는
generic O3 위에 queue와 일부 FP/SIMD timing을 지정한다. 공개된 A720AE timing 일부를
사용한 것과 전체 microarchitecture가 재현된 것은 다르다.
gem5 공식 O3 문서도 이를 범용 Out-of-Order CPU model로 설명한다.
[gem5 O3CPU](https://www.gem5.org/documentation/general_docs/cpu_models/O3CPU)

### 16 channels가 뜻하는 것

[memory_backend.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/memory_backend.py)는
channel마다 `MemCtrl + DRAMInterface`를 만든다. 16 channels이면 aggregate data width는
256-bit이고, 이 parameter의 raw transfer ceiling은 다음과 같다.

```text
8533e6 transfers/s × (16 bits / 8) × 16 channels = 273.056 GB/s
channel = (physical_address >> log2(stripe_bytes)) & (channels - 1)
```

식은 decimal GB/s다. Refresh, turnaround, command 제약, row locality, queueing,
CPU/cache/CHI overhead를 반영한 application bandwidth가 아니다.
주소 선택식은 [address_map.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/address_map.py)의
`striped_ranges`를 따른다. 64 B stripe에서는 1 KiB마다 16-channel 선택이 한 번 순환한다.
8 HNF의 home 선택과 16-channel 선택은 별개이고, 두 mapping의 상관관계도 실험 대상이다.

2 GiB / 16 channels의 logical aperture는 channel당 128 MiB다.
이 설정은 실제 DRAM package·die·rank 배치, shared DMC scheduler 또는 PHY 개수를
그대로 나타내지 않는다. `preserve_device_geometry` 경로에도 exposed capacity와 native
row count의 관계가 제한 사항으로 기록되어 있다. 작은 memory로 stripe 접근은 시험할 수
있지만 대용량 부품의 row/rank/bank 충돌이나 refresh 특성이 모두 보존된다고 가정하지 않는다.

## 추가 모델과 통합 상태

| 기능 | 현재 상태 | 사용할 수 있는 범위 / 선행 작업 |
|---|---|---|
| Channel-local traffic generator | `SOURCE_AVAILABLE`, 기존 실행 `RECORDED_PASS` | CPU·CHI를 우회해 controller/DRAM 서비스 능력을 측정 |
| L2 prefetch off/stride, cache/mesh parameter | `SOURCE_AVAILABLE` | profile에서 지원하는 범위의 sensitivity; 변경별 config 확인·snapshot 재생성 |
| Generic memory QoS framework | 기반 source 존재, 현 AP 정책 미연결 | 기본 1 priority, NULL policy; request 분류·정책·계측 연결 필요 |
| MPAM/PARTID/PMG, cache partition, bandwidth reservation | 현재 AP config에 통합 확인 안 됨 | architecture 및 register/OS 연결부터 별도 구현·검증 |
| NpuV01 + SMMUv3 | opt-in model source 존재, 기본 off | 아래 Apollo integration 제약 해소 후 DMA/compute overlap 및 contention 연구 |
| Synthetic SCMI/DVFS, online power/RC | source 및 범위별 기존 실행 기록 있음 | control/accounting·정책 실험; electrical calibration은 별도 |
| SI CL1 Zephyr | 별도 process의 standalone model 및 기존 benchmark 있음 | memory/IRQ/realtime latency 분해 |
| AP + SI CL1 단일 process | `UNSUPPORTED` | VMSA/PMSA system-register metadata가 process-global인 제약 |
| AP boot checkpoint | diskless Atomic, CPU switch 이전, NPU off | 입력 contract가 같은 반복 시험의 boot 비용 절감 |
| AP O3 hot checkpoint / NPU-on AP snapshot | 현재 launcher policy에서 `UNSUPPORTED` | native serialization 코드 유무와 launcher qualification을 구분 |

Traffic fixture는
[lpddr5x_backend_traffic.py](../../../hsoc-stack/tools/gem5/tests/zena_cmn/directed/lpddr5x_backend_traffic.py),
판정은 [check_backend_traffic.py](../../../hsoc-stack/tools/gem5/tests/zena_cmn/check_backend_traffic.py)다.
Channel마다 `PyTrafficGen`을 연결하므로 CHI injection/snoop 병목까지 검증하지 않는다.
CHI/Garnet에서는 protocol과 network parameter를 조절할 수 있지만 이 연구 모델의
지원 범위와 실제 IP 사양은 별도다.
[gem5 CHI](https://www.gem5.org/documentation/general_docs/ruby/CHI/),
[Garnet](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)

QoS 판단 근거는 [memory backend](../../../hsoc-stack/tools/gem5/configs/zena_cmn/memory_backend.py),
[MemCtrl](../../../hsoc-stack/tools/gem5/src/mem/MemCtrl.py),
[QoSMemCtrl](../../../hsoc-stack/tools/gem5/src/mem/qos/QoSMemCtrl.py)다.
Class가 QoS 기반을 상속한다는 사실로 MPAM이나 temporal isolation 지원을 주장할 수 없다.

### NPU는 source 존재와 Apollo 실행 준비를 구분한다

[npu_v01.py](../../../hsoc-stack/tools/gem5/configs/zena_cmn/npu_v01.py),
[NPU model contract](../../../hsoc-stack/tools/gem5/docs/zena_cmn/npu_model.md)에
FUNC_OPS 제어 엔진, INT8 tile 연산, SRAM, DMA credits, completion/fault IRQ 모델이 있다.
실제 RV32/RVV firmware execution 또는 production GPU/NPU의 완성된 모델은 아니다.

Payload는 SMMU → noncoherent ingress → shared native DRAM을 사용하고,
page-table/maintenance traffic에는 coherent CHI RNI 경로가 있다.
모든 payload가 CPU와 같은 cache-coherent 경로를 통과한다고 가정하면 안 된다.
CPU buffer ownership·cache maintenance·IOMMU translation/fault 검사를 먼저 수행해야 한다.

[run_npu.py](../../../hsoc-stack/tools/gem5/scripts/zena_cmn/run_npu.py)와
[run_roofline.py](../../../hsoc-stack/tools/gem5/scripts/zena_cmn/run_roofline.py)는
`run_smoke.py`를 통해 `/srv/oss_contrib`의 sibling layout을 전제로 한다.
현재 checkout에는 그에 대응하는 `hsoc-stack/tools/scripts`, `linux`, `npu_apps`가 없다.
Apollo launcher, Yocto package, artifact 경로와 collector를 이식한 뒤 검증해야 하며,
그 이전에는 Apollo에서 바로 실행 가능한 benchmark로 제시하지 않는다.
Roofline runner의 `MODEL_ONLY` 판정도 qualified hardware bandwidth roof를 뜻하지 않는다.

### Power와 Safety Island

[Power guide](../power-model-guide.md)에 기록된 OPP, transition latency, coefficients 및
thermal RC는 synthetic/assumed 값이다. Control path와 ROI energy accounting을 시험할 수
있지만 실제 SoC watt·junction temperature로 사용하려면 측정 기반 계수가 필요하다.
80°C hot-start feedback 검사는 workload가 실제로 그 온도까지 가열됐다는 증거가 아니다.
gem5 자체도 power/thermal **계산 기반**을 제공하며, 제품 계수를 제공하는 것은 아니다.
[gem5 Power and Thermal Model](https://www.gem5.org/documentation/general_docs/thermal_model)

SI CL1은 [standalone guide](../si-cl1-zephyr-guide.md)의 Minor 기반 in-order proxy다.
AP와 SI의 실행 결과를 더해 integrated shared-fabric latency로 만들 수 없다.
동시 실행, shared memory, interrupt/time synchronization 모델이 별도로 필요하다.

## 기존 증거가 말해 주는 것

| 기록 | 확인된 결과 | 아직 말할 수 없는 것 |
|---|---|---|
| [Interleave / AP16](../interleave-16core-results.md) | 64 MiB read의 64/512/1024 B stripe useful BW: 43.5057/32.6253/31.9765 GB/s; 16 cores·16 channels 활동 확인 | 모든 input에서 64 B가 최적이라는 일반화 |
| 같은 보고서의 channel-local fixture | 세 stripe 모두 255.8464 GB/s | Linux workload가 해당 bandwidth에 도달한다는 주장 |
| [Orin-informed 측정](../orin-informed-benchmark-results.md) | cache 9 + memory 4 조건의 checksum·ROI·traffic 수집 | A720AE timing을 Orin에 calibration했다는 주장 |
| [BTI decode 수정](../dhrystone-bti-fix.md) | 같은 O2 workload의 score가 40.6574% 상승; 잘못된 serialization 제거 | 실제 A720AE가 40.6574% 빨라졌다는 주장 |
| [SI CL1 결과](../si-cl1-benchmark-results.md) | 짧은 memory·IRQ·periodic job 실행 및 ROI replay | 실제 R82AE WCET 또는 AP 간섭을 포함한 deadline 보장 |

위 수치는 링크한 기존 실행 기록의 인용이다. 이번 문서 작업에서 다시 측정하지 않았다.

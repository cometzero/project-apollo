# 조사 출처와 적용 범위

조사·접근 기준일: **2026-10-26**. 공식 프로젝트 문서, 공급사 공개 자료 및 원저자 논문을
사용했다. `latest` 문서와 website 내용은 바뀔 수 있으므로 실제 구현 시 source release와
commit을 고정한다. 아래 자료는 Apollo의 build/runtime 완료 증거를 대신하지 않는다.

## 공개 1차 자료

| 자료 | 이 문서에서 사용한 근거 | 이 자료만으로 주장하지 않는 내용 |
|---|---|---|
| [Arm Zena CSS 발표, 2025-06-04](https://newsroom.arm.com/news/arm-unveils-zena-css) | 16 A720AE, R82AE Safety Island, CMN S3AE, accelerator 통합의 제품 구성 맥락 | Apollo gem5의 동등한 timing/safety 구현 |
| [gem5 O3CPU](https://www.gem5.org/documentation/general_docs/cpu_models/O3CPU) | 범용 Out-of-Order CPU model과 실행 구조 | Cortex-A720AE microarchitecture 완전 재현 |
| [gem5 CHI](https://www.gem5.org/documentation/general_docs/ruby/CHI/) | configurable coherence hierarchy와 design exploration 기반 | 모든 CHI 속성 및 CMN-S3AE physical implementation |
| [gem5 Garnet](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/) | router/link/VC 기반 network model | production NoC의 floorplan·전기적 timing |
| [gem5 ComplexGeneratorCore](https://www.gem5.org/documentation/general_docs/stdlib_api/gem5.components.processors.complex_generator_core.html) | rate·address·read percentage 등을 제어하는 synthetic traffic | 실제 sensor/GPU가 같은 request stream을 만든다는 주장 |
| [gem5 Power and Thermal Model](https://www.gem5.org/documentation/general_docs/thermal_model) | power expression과 RC thermal infrastructure | Apollo coefficient와 thermal boundary의 hardware calibration |
| [MemGuard, RTAS 2013, 원저자 PDF](https://www.ittc.ku.edu/~heechul/papers/memguard-rtas13.pdf) | multicore memory interference와 bandwidth reservation 연구 | MemGuard/MPAM이 현재 Apollo에 통합됨 |
| [RT-Bench, RTNS 2022](https://arxiv.org/abs/2203.11423) | periodic job·deadline·memory footprint 중심 benchmark 설계 | 해당 framework가 현재 initramfs에 설치됨 |
| [Autoware Open AD Kit components](https://autowarefoundation.github.io/openadkit/components/) | AD 기능 분해와 CPU/CUDA execution path 구분 | 전체 component가 gem5에서 실행 가능함 |
| [Autoware pointcloud preprocessor](https://autowarefoundation.github.io/autoware_universe/latest/sensing/autoware_pointcloud_preprocessor/) | filter/concatenate와 standalone core 호출·계측 후보 | Apollo용 recipe·실행 결과가 이미 존재함 |
| [Autoware NDT scan matcher](https://autowarefoundation.github.io/autoware_core/latest/localization/autoware_ndt_scan_matcher/) | pose·iteration·score를 함께 검사하는 localization workload | 모든 입력의 convergence 또는 deadline 보장 |
| [Autoware MPC lateral controller](https://autowarefoundation.github.io/autoware_universe/latest/control/autoware_mpc_lateral_controller/) | QP solver를 사용하는 CPU control kernel | kernel 성능만으로 차량 안정성 입증 |
| [CAVBench 원 논문, 2018](https://arxiv.org/abs/1810.06659) | AD application마다 다른 compute intensity/locality/bandwidth 특성 | 2018년 결과를 최신 AD stack의 대표 수치로 사용 |
| [MLPerf Automotive reference documentation](https://docs.mlcommons.org/mlperf_automotive/index_gh/) | 조사 시점 v0.5 model/dataset와 reference implementation | 축소 CPU kernel을 official result로 표시 |
| [MLPerf Automotive benchmark](https://mlcommons.org/benchmarks/mlperf-automotive/) | Single/Constant Stream, latency·query 조건 | 짧은 gem5 ROI로 official tail metric 충족 |
| [CARLA synchrony/time-step](https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/) | synchronous world와 fixed-step 시간 계약 | Apollo gem5 bridge 또는 closed-loop validation 완료 |

공개 benchmark를 이식할 때 license, dataset 사용 조건, release별 rules도 함께 확인한다.
문서의 제안 workload 크기·period·완료 gate는 프로젝트 설계안이며 위 자료의 규정값으로
제시하지 않는다. MLPerf에 관한 규정값은 [Workloads](workloads.md)의 해당 문맥과 출처를 따른다.

## 현재 프로젝트의 구현 근거

| 질문 | Source / 기존 문서 |
|---|---|
| Launcher·artifact·snapshot 계약 | [run_linux.py](../../../scripts/gem5/run_linux.py), [Run guide](../run-guide.md) |
| CPU model·memory geometry·address mapping | [Model design](../model-design.md), [Capabilities의 source 링크](capabilities.md) |
| 기존 microbenchmark와 ROI | [Benchmark guide](../benchmark-guide.md), [Experiments](experiments.md) |
| 16-core/interleave 및 direct DRAM 결과 | [Interleave / 16-core](../interleave-16core-results.md) |
| Orin 비교와 bandwidth 방법 보강 | [Orin validation](../orin-validation-results.md), [Bandwidth tuning](../orin-bandwidth-tuning.md), [Orin-informed gem5](../orin-informed-benchmark-results.md) |
| ISA/timing artifact의 영향 | [Dhrystone BTI fix](../dhrystone-bti-fix.md) |
| NPU 기능과 integration 경계 | [NPU model](../../../hsoc-stack/tools/gem5/docs/zena_cmn/npu_model.md), [Capabilities](capabilities.md) |
| Power/thermal의 기능과 가정 | [Power guide](../power-model-guide.md) |
| SI CL1 범위와 결과 | [SI CL1 guide](../si-cl1-zephyr-guide.md), [SI benchmark](../si-cl1-benchmark-results.md) |

이전 보고서의 `PASS`를 재인용할 때는 해당 날짜·binary·profile·input 범위를 유지한다.
이 문서 작성 시 수행한 정적 검사와 과거 simulation 성공을 하나의 새로운 실행 결과로
합치지 않는다. 실제 experiment는 root/nested Git SHA뿐 아니라 dirty diff와 artifact hash도
보존해야 현재 checkout의 변경 사항까지 재현할 수 있다.

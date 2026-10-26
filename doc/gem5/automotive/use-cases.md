# Automotive 활용 시나리오와 추진 순서

기준일: **2026-10-26**. 아래 우선순위와 gate는 현재 Apollo model을 고려한 프로젝트 제안이다.
공개 자료의 기능 설명을 현재 구현으로 간주하지 않으며, 구현 상태는
[Capabilities](capabilities.md), 실행 절차는 [Experiments](experiments.md)를 따른다.

## 1. Engineering 질문에서 실험을 시작한다

| 우선순위 | 결정하려는 사항 | 실험과 주요 지표 | 기대 산출물 / 현재 준비 수준 |
|---|---|---|---|
| P0 | DRAM이 부족한가, request 공급이 부족한가? | generator/CPU read-write, offered load, serviced BW, queue latency | memory service curve; 기존 runner 재사용 |
| P0 | frame 처리 중 어디에서 시간을 쓰는가? | 실제 kernel ROI의 cycles, cache miss, stall, bytes/frame | 병목 분해; 실제 kernel port 필요 |
| P0 | 16 cores에 task를 어떻게 배치할 것인가? | 단독/동시 실행, 동일/상이 DSU cluster, response time·slowdown | affinity 권고와 간섭 구간; coordinator 필요 |
| P1 | cache·prefetch·interleave 변경의 이득은? | 같은 입력의 parameter sweep, traffic amplification, tail latency | workload별 설계 trade-off; 기존 model 활용 |
| P1 | deadline을 지키면서 전력을 줄일 수 있는가? | DVFS 정책, transition 포함 latency, modeled energy/job | 정책 비교; synthetic power 경계 유지 |
| P1 | Safety Island의 latency는 어디서 생기는가? | standalone IRQ→handler→job, memory placement | SI 내부 분해; 기존 benchmark 확장 |
| P2 | accelerator가 CPU를 얼마나 방해하는가? | NPU/DMA와 CPU 공동 실행, buffer ownership, backpressure | memory/IO interface 요구사항; Apollo port 필요 |
| P2 | QoS/partition 정책은 간섭을 줄이는가? | request classification·budget·queue 정책 A/B | 정책의 모델 내 효과; MPAM/QoS 연결 필요 |
| P3 | sensor-to-actuator deadline을 만족하는가? | node pipeline, queue age, drop, synchronized world feedback | 통합 latency 가설; ROS 2/accelerator/시간 연계 필요 |

## 2. Memory subsystem을 세 단계로 나눈다

자율주행에서는 CPU task와 accelerator/sensor 부하의 합계가 memory를 공유한다.
최고 GB/s 하나보다 **부하가 증가할 때 critical request의 지연이 어디서 급증하는지**가
유용하다. Multicore memory interference가 실행 시간의 변동을 만드는 문제와 bandwidth
reservation 접근은 MemGuard의 hardware 연구에서도 다뤄졌다. 그 연구는 실험의 근거이며,
현재 Apollo에 MemGuard 또는 동일한 보장 정책이 설치되었다는 뜻은 아니다.
[MemGuard, RTAS 2013](https://www.ittc.ku.edu/~heechul/papers/memguard-rtas13.pdf)

| 단계 | 공급자와 포함 경로 | 구분하려는 원인 |
|---|---|---|
| A. Backend capacity | channel-local generator → MemCtrl → DRAM | read/write mix, bank/row/refresh, controller queue와 service ceiling |
| B. CPU-to-memory delivery | O3 → cache → DSU/SLC → CHI/Garnet → DRAM | MLP, prefetch, CPU issue, cache misses, injection 및 fabric 제한 |
| C. Application coexistence | 실제 foreground + background + 해당 memory 경로 | burst 정렬, data sharing, OS scheduling, interference와 tail |

gem5의 traffic generator는 rate, block size, address range, read percentage 등을
지정할 수 있다. Apollo의 기존 fixture를 재사용하고, 필요하면 offered load를 단계적으로
바꾸는 campaign을 추가한다. 요구 rate뿐 아니라 실제 issued/completed rate와 backpressure를
측정해야 한다.
[gem5 ComplexGeneratorCore](https://www.gem5.org/documentation/general_docs/stdlib_api/gem5.components.processors.complex_generator_core.html)

각 단계에서 sequential/random, stride, outstanding depth, read/write ratio, burst와
idle interval을 구분한다. 포화 이후 throughput이 거의 같아도 latency가 계속 증가할 수
있다. 평균 latency와 tail을 따로 보고, backend를 우회하거나 home mapping을 바꾼 실험은
동일한 시스템 경로로 합쳐 해석하지 않는다.

64 B interleave가 기존 streaming에서 빨랐다는 결과는 다른 frame access, read/write mix,
HNF mapping에서도 검증할 **후보**다. Channel 증가 시 총 data width까지 바뀌는 현재 모델의
sweep은 고정 pin budget에서 DMC 구조만 바꾸는 실험과 다르다. 둘의 비교 질문을 구분한다.

## 3. Cache·CMN 설계와 software 배치

CPU 수를 늘리면 application throughput과 single-frame latency가 같은 비율로 좋아지지
않는다. 다음 비교를 하나씩 수행해 원인을 설명할 수 있어야 한다.

- **Locality:** 같은 cloud/map tile을 사용하는 threads를 같은 DSU cluster에 배치했을 때
  shared-cache hit 증가와 capacity contention 중 어느 쪽이 큰지 비교한다.
- **Data sharing:** frame별 독립 병렬화와 한 frame 내부 병렬화를 비교한다. Cache-line
  sharing, false sharing, snoop/transfer, barrier 비용을 함께 본다.
- **Prefetch:** sequential preprocessing의 이득과 random localization의 불필요한 traffic을
  비교한다. Prefetch on으로 전체 GB/s만 증가하고 foreground가 느려지면 개선이 아니다.
- **Capacity/latency:** cache 크기만 바꾸는 이상화 실험과 크기·latency를 함께 바꾸는
  실현 가능한 후보 실험을 구분한다. 크고 빠른 cache를 비용 없이 만드는 결론을 피한다.
- **Fabric:** link width/latency, VC, placement를 바꿔 queue와 hop 민감도를 본다.
  관측된 경로의 근거는 CHI/Garnet counters이며 CMN-S3AE layout sign-off 자료가 아니다.

현재 CHI model과 configurable Garnet가 이런 탐색의 기반을 제공한다.
구현된 message/queue의 의미를 확인하고 사용하지 않은 counter를 실물 성능 지표로
치환하지 않는다.
[gem5 CHI](https://www.gem5.org/documentation/general_docs/ruby/CHI/),
[gem5 Garnet](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)

Software 최적화는 output correctness를 유지하면서 AoS/SoA, buffer reuse, copy 제거,
tiling, thread 수, SIMD/compiler 경로를 바꾸는 방식이 적절하다. 이 중 source가 실제로
지원하는 선택만 비교한다. Cache-resident integer loop인 Dhrystone은 decoder/pipeline
회귀 진단에 유용하지만 이 전체 workload 구성을 대표하지 않는다.

## 4. Mixed-criticality와 deadline 간섭

첫 시험은 periodic foreground 하나와 통제된 background 하나면 충분하다.
`response_time = finish_tick - release_tick`,
`dispatch_delay = start_tick - release_tick`를 따로 기록하고,
단독 대비 동시 실행 slowdown을 계산한다. 모델에서 같은 값이 반복돼도 다양한 sensor
입력·arrival phase를 탐색한 것은 아니다.

RT-Bench는 periodic 실행, deadline, memory footprint와 일관된 측정 인터페이스를
갖춘 framework의 연구 사례다. 이를 이식하거나 그 설계 원칙을 적용한 작은 harness를
추가할 수 있다. 현재 initramfs에 RT-Bench가 들어 있다는 의미는 아니다.
[RT-Bench, RTNS 2022](https://arxiv.org/abs/2203.11423)

초기 정책은 affinity와 background load 제한부터 비교한다. 이후 QoS를 추가하려면
CPU/device request identity가 어느 queue까지 전달되는지, arbitration과 backpressure가
어디서 적용되는지, starvation과 budget overrun을 어떻게 검출하는지 정의한다.
Linux priority 변경만으로 DRAM priority가 생기는 것은 아니다. MPAM을 평가하려면
PARTID/PMG 전달, register interface, cache/memory resource control, OS 연결 및 negative
test가 필요하다. 현재 모델의 default single-priority memory path로는 이 기능을 검증할 수 없다.

산출물은 workload envelope별 interference matrix와 허용 load 후보이다.
일부 실행의 deadline miss=0을 모든 상태의 WCET 또는 freedom-from-interference 증명으로
확장하지 않는다. SI CL1의 standalone IRQ benchmark도 AP-generated traffic를 동시에
받은 결과와 구분한다.

## 5. Accelerator·power·system-level 확장

### Accelerator는 interface부터 검증한다

Apollo에 존재하는 NpuV01을 재사용하면 synthetic compute/DMA overlap, SRAM tiling,
outstanding depth, CPU와 DRAM 경쟁을 연구할 수 있다. 우선 runner와 guest package를
이식하고, checksum, buffer ownership, SMMU mapping/fault, completion IRQ와 traffic
경로를 검증한다. 그 다음 hardware trace 또는 calibrated timing으로 비교 범위를 넓힌다.

Roofline은 operation count와 **같은 memory level에서 측정한 bytes**로 intensity를
정의하고, 같은 execution path의 compute/memory roof와 비교할 때 유용하다.
INT8 MAC, scalar operation, FP operation의 count 규칙을 섞지 않는다. DRAM generator의
ceiling을 cache-resident CPU kernel의 attainable roof로 바로 사용하지 않는다.
Production GPU/NPU의 TOPS, TensorRT latency, 전체 AD frame rate는 현재 proxy로 확정할 수 없다.

### Power는 latency와 energy를 같이 본다

SCMI/DVFS를 사용하는 periodic workload에서 OPP, transition, idle 구간이 deadline에
주는 영향을 측정하고 energy/job 또는 energy/frame을 비교한다. CPU clock과 memory/fabric
clock이 독립인 현재 model에서는 memory-bound task의 주파수 효과가 compute-bound task와
달라질 수 있다. Online stats reset에 맞는 epoch accounting을 유지한다.

이 단계의 energy와 thermal 결과는 [Power guide](../power-model-guide.md)의
synthetic coefficient/assumed RC 조건부 결과다. 실제 rail power, leakage, voltage,
ambient·cooling boundary, thermal time constant가 확보되기 전에는 실물 소비전력·온도를
예측했다고 표시하지 않는다. Orin의 board power를 A720AE event coefficient로 복사하지 않는다.

### 통합·fault·virtualization은 별도 범위다

현재 AP/SI 분리 실행으로 AP↔SI shared-fabric/IRQ latency를 검증할 수 없다. 그 결합에는
주소·time·interrupt 모델 통합과 별도 qualification이 필요하다. ECC error injection,
fault containment, watchdog, hypervisor/guest 간 간섭도 해당 hardware/software 경로를
모델링하고 stimulus·detection·recovery를 관측한 뒤에만 지원 항목으로 올린다.
지금은 구체적인 제품 요구가 생겼을 때 추진할 확장 항목이다.

ROS 2 queue·executor까지 포함한 replay는 kernel 다음 단계다. Closed-loop driving에서는
sensor capture, computation, actuation, world time을 연결해야 하며, 방법과 제약은
[Workloads](workloads.md)에 정리했다. 동기화하지 않은 host wall time을 차량 시간으로
사용하지 않는다.

## 6. Calibration과 validation 절차

Calibration은 parameter 추정이고, validation은 **추정에 쓰지 않은 조건에서의 검사**다.
상용 CPU의 비공개 구조를 DMIPS 하나에 맞춰 조정하면 여러 잘못된 parameter 조합이
같은 점수를 낼 수 있다. 다음 단계로 오차의 위치를 좁힌다.

1. **기능:** 동일 binary/input의 output, instruction support, fault/ordering 확인.
   최근 [BTI 수정](../dhrystone-bti-fix.md)처럼 model artifact가 성능을 크게 바꿀 수 있다.
2. **CPU:** dependency-chain latency와 independent-chain throughput, branch,
   load/store·forwarding, integer/SIMD, MLP를 분리한다. ISA·compiler·ABI를 기록한다.
3. **Hierarchy:** cache capacity knee와 실제 hit/miss, random/streaming, worker count,
   read/write mix를 비교한다. 평균뿐 아니라 request-level 또는 job-level 분포를 본다.
4. **Application:** calibration에 사용하지 않은 frame/map/point density 및 병행 workload로
   absolute error와 relative ranking을 평가한다.
5. **불확실성:** 비공개 latency/queue 값을 합리적 범위로 sweep하고 결론의 민감도를 보고한다.
   순위가 뒤집히면 해당 설계 선택은 아직 결정할 근거가 부족하다.

Orin은 동일 benchmark의 ABI·correctness·memory saturation 방법을 검증하고 비교 패턴을
얻는 데 유용하다. A78AE와 A720AE, cache topology, memory controller, clock/power policy가
다르므로 Orin 수치가 A720AE target parameter는 아니다. 실물 A720AE 또는 검증된 IP 자료가
없으면 결론을 `MODEL_ONLY`와 가정 범위로 한정한다.

허용 오차는 사용 목적에 맞춰 실험 전에 정한다. 예를 들어 후보 간 이득이 5%인데 model
가정 변경으로 20% 흔들린다면 선택 근거가 약하다. 이 숫자는 판정 방법을 설명하는 예시이며
Apollo에 설정된 acceptance threshold가 아니다.

## 7. 단계별 완료 gate

| 단계 | 수행 범위 | 다음 단계로 넘어갈 증거 |
|---|---|---|
| G0 Baseline | 현재 artifact와 source를 고정하고 기존 cache/DRAM 조건 재현 | checksum, exact ROI, 모든 대상 worker/channel 활동, provenance |
| G1 Service curve | backend 공급량과 CPU delivery 비교, 간단한 parameter sweep | offered/completed load, latency·traffic 분해, 수렴성, 모델 경로 식별 |
| G2 Real kernel | pointcloud 1개와 NDT 1개, Yocto package·input·ROI | hardware correctness, guest correctness, output quality 유지, 입력별 측정 |
| G3 Coexistence | periodic coordinator, 16-core affinity와 background sweep | release/start/finish 기록, overlap 확인, slowdown·drop·miss와 sample 수 |
| G4 Policy | cache/placement/DVFS 및 필요 시 QoS 구현 | 동일 input의 trade-off, 계측 일관성, 가정 변화에 대한 결론 안정성 |
| G5 Extended system | NPU/DMA 또는 ROS 2/AP–SI 등 필요한 경로부터 확장 | 통합 기능 검사 후 해당 경로의 timing validation; 미구현 항목 유지 |

G0의 과거 개별 실행 기록은 있지만, 이 표 전체가 완료되었다는 뜻은 아니다.
새 campaign 결과는 `build/qbox-apollo-qvp/gem5/`에 보존하고, 문서에는 config·입력·ROI·
correctness·runtime 상태와 해석 범위를 함께 남긴다. 장시간 simulation의 전체 조합을
먼저 돌리기보다 짧은 pilot으로 비용과 counter를 확인한 후, 결정을 바꿀 가능성이 있는
조건을 우선 확장한다.

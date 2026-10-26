# Automotive workload 선정과 ROI 설계

[Automotive 문서 목차](README.md) · [기존 benchmark guide](../benchmark-guide.md)

조사 기준일: **2026-10-26**. 이 문서는 공개 workload를 Apollo gem5에 적용하는
실험 설계다. 아래 Autoware kernel, ROS 2 pipeline, MLPerf, CARLA 연계는 모두
**`NOT_RUN`**이며, 현재 initramfs에 해당 package가 설치되었다는 뜻이 아니다.
기존 cache/DRAM benchmark 실행 경로와 새로운 application port를 구분한다.

## 1. 어떤 workload부터 추가할 것인가

우선순위는 **pointcloud preprocessing → NDT localization → periodic control와
memory co-runner → 짧은 node pipeline**이다. 이 순서면 기존 CPU/cache/DRAM
실험을 실제 Automotive software의 latency와 연결할 수 있다. 전체 AD stack을
한 번 실행하는 것보다, 입력·출력·ROI가 명확한 kernel을 먼저 검증하는 편이
어느 구조 변경이 효과를 냈는지 판단하기 쉽다. 이는 본 프로젝트를 위한 제안이다.

Autoware의 공식 Open AD Kit는 sensing/perception, localization/mapping,
planning/control 등을 독립적인 component로 나누며 CPU 경로와 CUDA 경로도
구분한다. 따라서 source package 이름만으로 실행 자원을 추정하지 말고 실제
implementation과 execution provider를 고정해야 한다.
[Autoware Open AD Kit components](https://autowarefoundation.github.io/openadkit/components/)

| 단계 | 답할 수 있는 질문 | 필요한 추가 작업 | 이 문서의 상태 |
|---|---|---|---|
| 기존 microbenchmark | working set, core 수, interleave 변경에 따른 모델의 latency/bandwidth 변화 | 기존 실행·결과 계약 사용 | 기존 지원 경로; 본 작업에서 재실행 안 함 |
| 실제 algorithm kernel | data layout, cache, memory contention이 알고리즘 한 단계에 주는 영향 | source 고정, AArch64 recipe, 입력 fixture, output 검사, ROI 추가 | `NOT_RUN` |
| ROS 2 node/process pipeline | executor, copy, queue, scheduling을 포함한 completion latency | ROS 2/runtime/image 구성, timestamp와 message 추적 | `NOT_RUN` |
| Closed-loop driving | 계산 지연으로 다음 sensor 입력과 차량 상태가 달라지는 영향 | world simulator와 시간 동기화, vehicle model, feedback 연결 | `NOT_RUN` |

## 2. 우선 도입할 CPU workload

다음 표의 입력 크기와 실험 변수는 **제안값 또는 선택 항목**이다. 차량의 실제
sensor specification이나 현재 Apollo image의 기본값을 의미하지 않는다.
각 kernel은 가능하면 원본 알고리즘을 사용하고, simulator용 변경은 입력 공급과
ROI 계측으로 제한한다. 코드나 입력을 줄였으면 별도 workload ID를 부여한다.

| Workload | 입력과 ROI | 변화시킬 조건 | 성능과 함께 확인할 결과 |
|---|---|---|---|
| Pointcloud concatenate / transform | sensor별 point 배열, extrinsic transform, twist를 준비한 뒤 cloud 결합 함수 | point 수, AoS/SoA를 실제 지원하는 구현, worker 수, cloud copy 유무 | ns/point, cycles/frame, 유효 point 수, 좌표 오차, output checksum |
| Crop / voxel downsample / outlier filter | 동일한 pointcloud와 filter parameter를 사용한 filter 호출 | point 밀도, voxel 크기, 입력 분포, cache 크기 | frame latency, output point 수·분포, DRAM bytes/frame, retained geometry |
| NDT scan matching | 고정 map tile, sensor cloud, initial pose로 한 frame alignment | map working set, thread 수, initial pose 난이도, 허용 iteration | pose 오차, convergence status, iteration 수, latency, cache misses |
| Image preprocessing | 실제 frame의 resize / color conversion / normalization | resolution, stride, alignment, SIMD 경로, batch | pixel/tensor 오차, cycles/pixel, read/write traffic, frame latency |
| Tracking / association 또는 collision checking | 고정 detection/object/trajectory 배열 | object 수, association 밀도, candidate 수 | association/판정 결과, branch behavior, cycles/frame |
| Planning kernel | 고정 ego state, reference path, obstacle 입력으로 한 계획 갱신 | candidate 수, horizon, solver tolerance | constraint 만족, 경로/목적함수 오차, iteration, latency |
| MPC control kernel | reference trajectory, odometry, steering state로 한 control update | prediction horizon, solver, warm start, period | solver status, steering command 오차, response latency, deadline misses |

### 2.1 Pointcloud는 가장 작은 실제 application 시작점이다

Autoware의 `autoware_pointcloud_preprocessor`는 crop, distortion correction,
downsampling, concatenation 등을 제공한다. 조사 시점 공식 문서에는 ROS node와
executor 없이 `concatenate_core`를 호출하는 `concatenate_without_ros_node`
예제가 있다. 기본 입력은 source cloud 3개, cloud당 40,000 points이며
`combine_pointclouds()`만 측정하고 입력 생성은 제외한다. 이 예제를 먼저
AArch64 standalone harness로 옮기는 방식을 권한다. **현재 프로젝트에 port한
상태는 아니다.**
[Autoware pointcloud preprocessor](https://autowarefoundation.github.io/autoware_universe/latest/sensing/autoware_pointcloud_preprocessor/)

동일 입력을 반복하는 cache-resident 시험과 여러 frame을 순회하는 streaming
시험을 분리한다. 같은 frame을 계속 재사용한 수치를 실제 sensor stream의
DRAM 요구량으로 사용하면 안 된다. 출력 point 수와 좌표를 검증하고,
allocator·temporary buffer·copy 횟수를 기록한다. `latest` 문서는 변하므로
port할 때 이 예제가 존재하는 source commit을 고정한다.

### 2.2 NDT는 latency와 localization 품질을 함께 측정한다

공식 `autoware_ndt_scan_matcher`는 pointcloud를 이용한 pose estimation과
initial pose estimation을 제공하고, execution time·iteration 수·scan matching
score를 별도로 출력한다. 이 구조를 활용해 알고리즘 종료 조건과 timing을 함께
검증할 수 있다.
[Autoware NDT scan matcher](https://autowarefoundation.github.io/autoware_core/latest/localization/autoware_ndt_scan_matcher/)

첫 시험은 map build/load와 allocation을 ROI 밖에 두고 단일 alignment를 측정한다.
그다음 map tile 교체를 포함한 별도 ROI를 만든다. 이 둘을 합치면 cache 구조의
효과와 map loading 비용을 분리하기 어렵다. iteration cap을 줄여 빨라졌지만
pose가 수렴하지 않은 결과는 성능 개선으로 인정하지 않는다. pose가 잘 맞는
frame뿐 아니라 초기 오차가 큰 frame도 별도 input class로 보존한다.

### 2.3 MPC와 planning은 deadline 민감도를 평가한다

Autoware의 MPC lateral controller는 linear MPC의 optimization을 QP로 만들며,
Eigen 기반 solver와 OSQP 경로를 문서화한다. trajectory와 현재 vehicle state를
주고 계산 결과를 검사할 수 있는 CPU workload 후보이다.
[Autoware MPC lateral controller](https://autowarefoundation.github.io/autoware_universe/latest/control/autoware_mpc_lateral_controller/)

MPC의 내부 numerical solve 시간과 periodic thread의 release부터 completion까지
걸리는 시간을 따로 측정한다. 후자는 scheduler delay, preemption, shared-memory
contention을 포함해야 한다. 예를 들어 10ms 또는 20ms period를 쓰는 실험을
설계할 수 있지만, 해당 값은 차량 요구사항에서 정할 값이며 여기서 제품 deadline으로
선언하지 않는다. 고정된 frame의 빠른 solve가 전체 주행 안정성을 입증하지도 않는다.

## 3. CPU·GPU·NPU를 구분하는 실험

CPU가 실행하는 preprocessing/postprocessing, accelerator의 inference, buffer
전송 및 synchronization을 독립적인 구간으로 나누어야 한다. 현재 Apollo AP
gem5 결과에서 CUDA/TensorRT 또는 실물 NPU inference latency를 직접 얻었다고
해석할 근거는 없다. Open AD Kit가 CUDA component를 제공한다는 사실도 해당
component가 현재 gem5 image에서 동작한다는 증거가 아니다.

| 방식 | 얻을 수 있는 정보 | 주장할 수 없는 내용 |
|---|---|---|
| 동일 DNN의 CPU implementation 실행 | 선택한 CPU library·datatype의 비용과 cache/DRAM 민감도 | GPU/NPU에서 같은 latency, TOPS 효율, energy가 나옴 |
| 실제 accelerator 실행에서 추출한 traffic replay | 가정한 burst·read/write·timing 아래 memory subsystem 경쟁 | 새로운 memory 구조에서 accelerator가 동일 순서·속도로 요청함 |
| 주기적인 synthetic memory co-runner | 일정 부하가 CPU task에 주는 간섭 범위 | 특정 DNN의 layer별 execution 또는 device driver 재현 |
| 기능·timing 검증된 accelerator model 연계 | 모델이 지원하는 protocol, workload, calibration 범위의 비교 | 검증하지 않은 operator·precision·device까지의 정확성 |

Traffic replay를 추가할 때는 bytes 합계뿐 아니라 issue time, transaction size,
outstanding 수, read/write 비율, address locality, coherency, completion dependency를
기록한다. 고정 timestamp trace는 memory가 느려져도 원래 속도로 요청을 넣을 수
있으므로, backpressure와 dependent request를 표현하는 방식이 필요하다.
이 부분은 향후 구현 설계이며 **`NOT_RUN`**이다.

학술적 근거로 CAVBench는 6개 application과 4개 dataset을 이용해 operation
intensity·memory bandwidth·locality가 workload마다 다름을 보고했다. 따라서
한 integer benchmark나 평균 bandwidth 하나를 AD stack의 대표 점수로 삼기보다,
서로 다른 access pattern과 병행 부하를 선정하는 접근이 타당하다. 이는 2018년의
해당 연구 결과이며 최신 Autoware 전체가 같은 특성을 가진다는 뜻은 아니다.
[CAVBench 원 논문](https://arxiv.org/abs/1810.06659)

## 4. MLPerf Automotive를 어떻게 활용할 것인가

조사 시점 공식 공개 페이지의 MLPerf Automotive v0.5는 SSD 기반 2D detection,
DeepLabV3+ segmentation, BEVFormer-tiny 기반 3D detection을 제시한다.
dataset은 Cognata와 nuScenes이며, 공식 reference implementation과 release를
고정하여 재현해야 한다.
[MLPerf Automotive reference documentation](https://docs.mlcommons.org/mlperf_automotive/index_gh/)

공식 benchmark의 핵심은 latency다. Single Stream은 이전 query 완료 후 다음
query를 보내며, Constant Stream은 일정 rate로 요청한다. 공개 v0.5 표의 metric은
모두 p99.9 latency이고 각각 6,636 queries와 100,000 queries를 제시한다.
정해진 model/dataset/quality target 및 해당 release의 rules를 함께 만족해야 한다.
[MLPerf Automotive scenarios와 metrics](https://mlcommons.org/benchmarks/mlperf-automotive/)

Apollo에서는 다음 순서로 활용하는 것을 제안한다.

1. Orin 등의 실물 환경에서 사용 가능한 official implementation, accuracy check,
   execution provider를 먼저 확인한다. 구현 가능성이 검증되기 전에는 결과를 예고하지 않는다.
2. CPU preprocessing/postprocessing 또는 memory-intensive operator를 추출하여
   동일 입력·output tolerance로 gem5와 실물에서 실행한다.
3. input 수를 줄인 gem5 실험에는 `MLPerf-derived kernel / NOT official result`로
   표시한다. 짧은 kernel ROI의 latency를 official query latency로 비교하지 않는다.
4. 실제 accelerator의 traffic을 확보하면 위 3절의 replay/co-runner 비교를 추가한다.

현재 initramfs에서 full MLPerf Automotive benchmark를 실행한 결과는 없다.
몇 frame의 축소 실험으로 p99.9를 보고하거나 quality target을 생략한 결과를
공식 MLPerf 점수로 표시하지 않는다. `MLPerf Inference`의 Automotive workload와
`MLPerf Automotive` suite도 이름만으로 동일한 release·task로 취급하지 않는다.

## 5. 16-core mixed workload 설계

기존 multicore memory benchmark를 바탕으로 application과 co-runner를 결합할 수
있으나, 아래 조합과 coordinator는 아직 구현하지 않은 **`NOT_RUN`** 제안이다.
16개 core를 모두 같은 loop로 채우는 시험과 여러 주기·우선순위를 가진 AD task
조합은 서로 다른 질문에 답한다.

| 단계 | Foreground | Background | 평가 질문 |
|---|---|---|---|
| A | CPU0에서 NDT 또는 pointcloud kernel | 없음 | 단독 실행 baseline과 output correctness |
| B | 같은 foreground, 같은 affinity | 나머지 core 중 1/3/7/15개에서 read/copy/triad | 간섭 증가에 따른 latency와 DRAM traffic 변화 |
| C | periodic MPC와 pointcloud를 서로 다른 core에 배치 | 제한한 수의 memory worker | foreground deadline miss와 co-runner 처리량 간 관계 |
| D | 독립 frame 병렬 처리 또는 kernel 내부 thread 병렬화 | 선택한 background 유지 | throughput 증가, frame latency, coherence 비용의 관계 |

Foreground와 background는 같은 simulated-time 구간에 겹쳐야 한다. background
준비 완료 barrier 이후 ROI를 시작하고 종료 때까지의 실제 실행 시간을 기록한다.
CPU0에 pin하는 기존 command wrapper를 그대로 쓰면 여러 process가 CPU0에 모일 수
있으므로 worker별 affinity를 명시하는 coordinator가 필요하다. 해당 wrapper의
기존 동작은 [benchmark guide의 CPU switch와 ROI](../benchmark-guide.md#2-cpu-switch와-roi)를 따른다.

16-core 시험에서도 Linux housekeeping·IRQ·background runnable task를 기록한다.
foreground와 background의 core 집합을 명확히 구분하고, 총 core 수가 16을
초과하지 않게 구성한다. 일반 priority와 RT priority는 별도 실험으로 다루며
RT 설정 자체가 bounded latency를 보장한다고 가정하지 않는다.

## 6. 입력·ROI·결과를 재현 가능하게 만드는 계약

| 항목 | 반드시 보존할 정보 |
|---|---|
| Source/build | upstream commit, local patch, compiler/linker version, flags, ABI, library version, executable hash |
| Input | dataset/license, file hash, frame ID, point/image/object 수, sensor timestamp, map tile, random seed |
| Algorithm | datatype, tolerance, iteration limit, solver, CPU execution path, thread 수, affinity |
| Platform | effective profile, CPU/cache/memory/core 구성, kernel·initramfs hash, snapshot compatibility |
| ROI | 시작/종료 의미, initialization·allocation·page fault 포함 여부, warmup 수, simulated tick 범위 |
| Correctness | output hash 또는 numeric tolerance, convergence/quality, 실패·drop·timeout 수 |
| Measurement | per-frame latency, instruction/cycle, cache/DRAM traffic, host seconds, sample 수와 distribution |

Application port에는 두 ROI를 두는 편이 유용하다. `kernel ROI`는 준비된 입력에
대한 함수 호출을 측정하고, `request ROI`는 요청 도착부터 output 생성까지의 queue,
scheduler, copy 비용을 포함한다. kernel latency를 request latency나 sensor-to-actuator
latency로 이름만 바꾸어 보고하지 않는다.

Atomic boot snapshot에서 restore한 후 O3로 전환하고 해당 kernel의 실제 warmup을
수행한다. warmup을 표시한 phase 이름만으로 cache가 준비되었다고 간주하지 않는다.
현재 whole-command wrapper는 fork/exec 등의 비용도 포함하므로, 짧은 kernel은
guest 내부 marker를 추가하는 편이 적합하다. 상세 동작은
[기존 ROI 계약](../benchmark-guide.md#2-cpu-switch와-roi)을 따른다.

Latency는 simulated-time 기준으로 산출하고 host wall time은 실험 비용으로 별도
보관한다. average뿐 아니라 sample 수, median, observed maximum을 남긴다.
p95/p99를 쓸 때는 표본 수와 frame 선택 방법을 같이 제시한다. 소수의 frame에
대해 계산한 tail percentile은 차량의 tail latency 보장이 아니며, 관측 maximum도
WCET bound가 아니다. deadline miss rate는 정한 release schedule·deadline·입력
조건에서만 유효하다.

## 7. ROS 2와 CARLA는 별도의 통합 단계다

Standalone kernel 다음에 짧은 ROS 2 pipeline을 구성하면 message copy, allocator,
executor, queue depth의 영향을 평가할 수 있다. 단, 이를 위해 ROS 2 및 의존 library의
Yocto recipe/image 통합과 input replay가 필요하다. 현재 benchmark initramfs에
full Autoware/ROS 2/CARLA가 준비되어 있다고 가정하지 않는다.

Autoware pointcloud 문서는 외부 subscriber를 추가한 계측이 큰 message의
intra-process pipeline에 영향을 줄 수 있다고 설명한다. 따라서 pipeline 내부의
경량 timestamp를 먼저 활용하고 profiler/logging on/off의 영향을 별도로 측정한다.
[Autoware pipeline latency 계측](https://autowarefoundation.github.io/autoware_universe/latest/sensing/autoware_pointcloud_preprocessor/#measuring-the-performance)

CARLA는 synchronous mode에서 client tick을 기다릴 수 있고 fixed time-step으로
world를 진행할 수 있다. 이 기능은 느린 architecture simulator와의 연계 설계에
참고할 수 있으나, 현재 Apollo gem5와 연결된 기능은 아니다.
[CARLA synchrony와 time-step](https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/)

첫 단계는 실물 또는 world simulator에서 얻은 sensor 데이터를 고정 replay하는
open-loop 시험이다. 이 방식은 같은 입력에 대한 architecture 비교에 적합하지만,
계산 지연이나 다른 control output이 다음 sensor 입력을 바꾸는 효과는 포함하지 않는다.
Closed-loop 단계에서는 world time, sensor capture time, gem5 simulated time,
actuation time을 연결해야 한다. Host 실행이 느리다는 이유로 vehicle time을
임의로 늘리면 deadline 평가가 달라진다. 별도 bridge와 시간 계약을 검증한 뒤에만
closed-loop 결과라고 표시한다.

## 8. 첫 구현 범위와 완료 기준

첫 구현은 **pointcloud standalone kernel 1개와 NDT alignment 1개**가 적절하다.
각각 동일 source/input의 Orin correctness 결과, Yocto package, initramfs 포함 확인,
snapshot restore 후 O3 ROI, output 검증, 단독/간섭 실행 결과를 갖추면 다음 단계로
진행한다. kernel마다 실물과 gem5의 absolute latency 차이와 architecture 변경에
대한 상대 변화량을 함께 보고한다. Orin은 비교 대상의 하나이며 A720AE silicon
calibration을 대신하지 않는다.

완료 전까지는 integration status를 `NOT_RUN`으로 유지한다. Source compile만
성공하면 `BUILD_PASS`, guest 출력만 확인하면 `FUNCTIONAL_PASS`, 유효 ROI와
correctness를 함께 확인하면 해당 조건의 `MODEL_MEASUREMENT_PASS`처럼 근거를
명시한다. 이 표기는 실험의 범위를 설명하는 것으로 Automotive qualification,
전체 AD stack 성능, safety 또는 실물 A720AE timing 인증을 의미하지 않는다.

# Apollo gem5 SoC 사양 탐색 — Design

작성일: **2026-10-28**. 상태: **설계 / 구현·검증 진행 중**.
[현재 파일과 evidence](campaign-20261028.md)를 설계의 완료 여부와 구분한다.
[Requirement](requirement.md) → [Plan](plan.md) → **Design** →
[Implementation](implementation.md) → [Verification](verification.md).

## 1. 현재 기준과 설계 경계

Source 확인 기준: root `fd97f9a08f37`, gem5 `11f529d6c3ea`,
`meta-hsoc-auto-solutions` `3e444601b314`. 이는 문서 작성 당시 source revision이며
현재 deploy binary/image와 같은 revision임을 증명하지 않는다.

현재 연결은 AP CPU의 private L1/L2, cluster DSU L3, Ruby CHI/Garnet,
HNF SLC proxy, SNF, native MemCtrl/DRAMInterface다. CPU 경유 timing은 O3 ROI에서
측정하고 Atomic boot는 준비에 사용한다. 새로운 generic simulation framework를 만들지
않고 기존 launcher, profile, snapshot, collector를 재사용한다.

| 현재 contract | 설계에 미치는 영향 | Source |
|---|---|---|
| Root launcher CPU 4/16, worker 1/4/8/16 | 8 workers는 8-core SoC가 아님; 하위 `run_fs.py`의 8-core parser만으로 root 지원을 주장하지 않음 | [run_linux.py](../../../../scripts/gem5/run_linux.py) |
| L2 512 KiB/core, L3 4 MiB/cluster, active SLC 4 MiB total | `default.yaml`의 SLC 8 MiB를 active 값으로 오인하지 않음 | [active profile](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/profiles/a720ae_documented.yaml), [defaults](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/profiles/default.yaml) |
| CPU/Ruby/mesh clock 각각 parameter 존재 | 개별 domain 적용/latency cycle 기준을 검증해야 함 | [run_fs.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/run_fs.py), [builder](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/ruby_system_builder.py) |
| 2 GiB, x16, 8533 MT/s 고정; channels 4/8/16 | Rate/width/capacity sweep은 추가 구현 대상 | [parameters.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/parameters.py) |
| HNF 8개, Home selector 64-B 단위 | SLC total과 per-home 크기의 일관성 필요; channel mapping과 상관관계 존재 | [address_map.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/address_map.py) |
| Diskless Atomic pre-switch, NPU disabled checkpoint | NPU-enabled save/restore도 거부; O3 warm cache를 보존한 공통 snapshot으로 후보를 바꿔 실행하지 않음 | [checkpoint.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/checkpoint.py) |

## 2. DES-DSE-01 — Campaign 입력과 identity

Campaign은 version이 있는 target/scenario, software baseline, candidate, 실행 계획을
연결한다. 기존 `launch.json`을 대체하지 않고 그 파일과 native artifact를 참조한다.
아래는 artifact의 필드 계약이다. 실행 가능한 offline report 입력 예제는
[soc_spec.example.json](../../../../scripts/gem5/soc_spec.example.json)이며 simulation config와 별개다.

| Record | 필수 필드 |
|---|---|
| Campaign | ID, 목적, source revisions/dirty patches, target IDs, model qualification, 상태 |
| Workload | source/ELF/input hash, compiler/flags, kernel 의미, output oracle/tolerance, ROI 경계 |
| Scenario | 입력 크기·rate, frame/buffer 재사용, arrival/queue/drop 정책, resident peak, affinity/배치, foreground/background, seed, sample 정책 |
| Candidate | profile 및 dependencies, raw/canonical config hash와 정규화 규칙, IP 제공 옵션 여부, uncertainty 범위, 비용 참조 |
| Case | 위 ID들, 정확한 command, snapshot identity, expected result, timeout, output directory |
| Result | 실행 상태, 수치 유효성, target 판정, ROI/counters/output, elapsed host time, limitations |

Run ID는 candidate/workload/scenario/repeat를 구분한다. CPU model이나 clock, cache,
DRAM 설정의 변경을 workload 옵션 변경과 혼동하지 않는다. Compare 단계는 유지해야 할
필드의 차이를 검사하고 experiment에서 선언한 변화만 허용한다.

Raw `config.json` hash는 원본 artifact 식별용이다. Host UART port와 output 경로는
매번 달라지므로 candidate 비교용 canonical hash와 분리한다. 기존
[check_memory_convergence.py](../../../../hsoc-stack/tools/gem5/scripts/zena_cmn/check_memory_convergence.py)의
run 경로/terminal port 정규화 방식을 재사용하되 허용한 필드와 규칙 version을 기록한다.
Clock, guest 주소/배치, topology, timing, cache policy 등 simulation 의미를 바꾸는 값은
정규화로 제거하지 않는다. Input 경로를 치환해도 실제 file content hash는 별도로 보존한다.

## 3. DES-DSE-02 — Hardware 후보의 모델링

### Cache

L2는 core당, L3는 cluster당, SLC는 total과 HNF당 크기를 동시에 기록한다. 크기뿐 아니라
assoc, replacement/inclusion policy, tag/data latency, bank 수, request TBE, prefetch를
명시한다. 현재 bank/resource-stall 설정은 물리 SRAM macro의 port/pipeline을 완전히
대신하지 않으므로 실현 가능성은 외부 자료로 확인한다.

Capacity만 바꾸는 case는 `capacity_only_sensitivity`로 표시한다. 제품 후보 비교는
공급사가 제공하거나 근거를 제시한 size/latency/bandwidth 조합을 사용한다. Cache ID/DTB,
native cache size와 OS-visible topology가 일치하는지도 확인한다.

### CPU 및 NoC clock

`cpu.clock`은 CPU domain, `ruby.clock`은 Ruby와 system clock 구성,
`cmn.mesh.clock`은 network domain에 연결된다. 현재 memory controller의 상속 clock 등
간접 영향도 `config.json`에서 추적한다. `ruby.clock` 변화는 순수 NoC clock 변화로
이름 붙이지 않는다. Cache controller latency가 어느 domain의 cycle인지 기록한다.

현재 CHI private L1/L2 controller와 sequencer는 CPU clock을 상속하지만,
`RubyCache`의 bank resource는 `CacheMemory::setRubySystem()`에서 Ruby clock period를
사용한다. [CacheMemory.cc](../../../../hsoc-stack/tools/gem5/src/mem/ruby/structures/CacheMemory.cc)와
[BankedArray.cc](../../../../hsoc-stack/tools/gem5/src/mem/ruby/structures/BankedArray.cc)의
resource arbitration 경로는 baseline의 `resourceStalls=true`에서 활성화된다.
따라서 CPU 1/2 GHz 비교는 controller action과 bank 점유 시간이 다른 timebase를 쓰는
현재 모델의 operating-point 민감도다. Private cache 전체의 물리 frequency scaling이나
독립 IPC 보정으로 해석하지 않는다. 실제 stall 발생량과 영향은 해당 ROI에서 별도 확인한다.

Garnet의 flit width, CHI data channel width, packet framing, link/router latency,
VC/buffer 수를 구분한다. 서로 다른 clock/width를 허용했다는 사실만으로 CDC/SerDes나
CMN의 실제 physical channel을 모델링했다고 주장하지 않는다. 필요한 bridge timing의
지원 여부와 directed traffic를 검증하기 전 해당 비교는 `CONDITIONAL`이다.
설정만 만든 상태는 `NOT_RUN`이며, transport 오류나 무효 counter가 있는 실행은
`INVALID`다. `CONDITIONAL`이라는 label로 실행·계측 오류를 유효 결과로 승격하지 않는다.
`integrated_private_pipeline`의 Simple-network diagnostic은 동일 clocks를 요구하며
Garnet 성능 결과와 같은 계열로 섞지 않는다.

### DRAM 및 DMC

현재 backend는 channel당 native MemCtrl 하나와 DRAMInterface 하나를 생성한다.
이는 실제 SoC에서 DMC IP block 하나가 몇 개의 subchannel을 갖는지까지 규정하지 않는다.
X32 후보는 실제 vendor channel/subchannel 정의에 맞춰 controller 연결을 설계해야 하며,
두 x16 controller를 무조건 하나의 x32 DMC와 동일하게 취급하지 않는다.

각 후보에 다음을 포함한다: part/class, device width, devices/rank, ranks/channel,
bank group/bank, row/burst, data/command clock 관계, refresh/timing, scheduler/page policy,
queue depth, address mapping, exposed capacity, controller/PHY 추가 지연의 근거.
MT/s label만 바꾸거나 모든 DRAM timing을 같은 비율로 축소하지 않는다.

2 GiB는 작은 simulation aperture이지 실제 memory part의 전체 density라는 뜻이 아니다.
현재 synthetic density 조정과 `preserve_device_geometry` 모드 모두 주소 decoder가 보는
범위를 기록한다. 작은 aperture의 row/bank locality를 대용량 제품 구성과 동일하다고
가정하지 않는다. Backend의 `part_provenance`와 timing fingerprint를 함께 보존한다.
[memory_backend.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/memory_backend.py)

## 4. DES-DSE-03 — 실행 lifecycle와 snapshot

1. Target/scenario 및 candidate를 고정하고 resolved parameter와 native config를 대조한다.
2. Snapshot 지원 candidate에서는 input/geometry/clock contract가 유효한 Atomic snapshot을 준비한다.
3. Restore 또는 지원된 fresh boot 후 allocation/initialization과 O3 switch를 수행한다.
   Steady-state는 실제 workload warmup을, cold-start는 사전 정의한 초기 상태의 검증을 수행한다.
4. 하나의 coordinator가 ROI begin/end를 소유하고 worker를 동기화한다.
5. Output correctness와 정상 종료를 검사한 뒤 exact ROI stats를 선택한다.
6. 수치 유효성과 target 충족을 별도 판정하고 evidence를 보존한다.

Launcher contract schema 3은 native/kernel/firmware/profile/initrd와 구성 Python,
`default.yaml`, native interpreter의 FS import closure(CHI/topology/PyYAML 포함)를 검사한다.
`launch.json`의 `model_sources_schema=1`과 `model_sources_sha256`도 같은 source map을
기록하며 inventory가 파일과 native manifest를 대조한다. 이전 schema 1/2 metadata를
변환해 재사용하지 않는다. 기존 map 없는 측정은 raw validity와 별개로
`HISTORICAL_LIMITED`이며 새 비교의 준비 조건을 충족하지 않는다. 전체 host shared library나
외부 서비스를 포괄하는 hermetic 실행 보장은 아니다. Contract가 같아도 실제 restore
runtime 검증은 별개이며, `M5_OVERRIDE_PY_SOURCE=true/yes`의 checkpoint는 거부한다.

같은 candidate에서 workers/passes만 바꾸는 경우 지원되는 계약 안에서 snapshot을
공유한다. Candidate의 topology/cache/clock/DRAM을 바꾼 경우 fresh snapshot을 기본으로
한다. Marker를 자체 호출하는 workload에 `gem5-control run`을 중첩하지 않는다.

현재 `npu.enabled`이면 checkpoint save/restore는 거부된다. 기존 NPU 모델로 외부 traffic를
만드는 경로는 fresh boot 비용을 계획에 포함하거나 serialization, in-flight drain,
restore를 별도 구현·검증한 뒤 사용한다. 새 device/traffic source를 추가했다고 기존
snapshot 지원을 자동 상속하지 않는다.

위 lifecycle은 CPU guest 경로다. Native generator는 CPU switch 없이 timing mode에서
동작한다. Supply 시작/종료, 측정 window, drain 완료 시점을 별도로 기록하며 window 내
service rate와 drain을 포함한 전체 transaction 완료율을 구분한다.

## 5. DES-DSE-04 — Workload와 외부 traffic

첫 kernel은 source/license/input을 고정한 image preprocessing 호출이다. Correctness
fixture와 host 실행을 먼저 확인하고 guest 함수 단위 ROI를 추가한다. 전체 ROS 2,
camera capture, CUDA/TensorRT 실행을 함께 이식하는 범위는 아니다.

Input hash와 함께 frame 순서, reuse distance, buffer pool, cold/steady-state 조건을
명시한다. 같은 frame 재실행은 별도 hot-cache scenario다. 실제 frame 교체가 있는 target에
해당 결과를 그대로 적용하지 않는다. Arrival가 periodic/open-loop인지 completion 후
다음 요청을 내는 closed-loop인지, queue depth와 drop/backpressure 정책도 구분한다.
Cold-start는 단순 warmup 생략으로 인정하지 않으며 O3 전환/준비 코드가 바꾼 cache·TLB 등
관심 상태의 근거를 남긴다. 기존 collector의 `warmup` phase 이름과 실제 loop 수행 여부는
분리해 해석하고, fixed-warmup executable을 cold-start 지원으로 간주하지 않는다.
Release/start/finish는 동일한 simulated timebase로 기록하고, CPU clock 변경 시 timestamp
환산이 바뀌지 않는지 확인한다.

동시 실행은 foreground와 background를 별도 core에 pin하며 coordinator가 release,
start barrier와 ROI를 관리한다. Existing memory worker의 `0..workers-1` 배치만으로
임의 cluster 배치를 지원한다고 가정하지 않는다. 동일/다른 cluster 실험에는 affinity
확장과 worker별 실행 검증이 필요하다. Linux housekeeping/IRQ 배치도 기록한다.

| Traffic 목적 | 필요한 연결 | 평가할 수 없는 것 |
|---|---|---|
| DRAM backend ceiling | Channel-local MemCtrl 입력 | CPU/cache/CHI 또는 SLC 간섭 |
| CPU cache/NoC 간섭 | CPU worker 또는 해당 coherent 경로 | 실제 GPU/NPU 내부 연산 성능 |
| 비일관성 외부 IP의 DRAM 경합 | 실제 설계에 대응하는 shared DMC 경로 | SLC를 통과하지 않으면 SLC 용량 효과 |
| 외부 IP의 SLC 재사용 | 실제 allocation/coherence 경로와 cache maintenance | 근거 없는 coherent/noncoherent 등가성 |

Traffic envelope에는 bytes/frame, frame rate, read/write mix, burst size, inter-arrival,
outstanding, 주소/locality, phase, coherency, cacheability를 둔다. Rate뿐 아니라 burst와
phase overlap을 비교한다. 기존 NPU source 존재만으로 Apollo camera/ISP/GPU traffic
통합이 완료된 것으로 표시하지 않는다.

## 6. DES-DSE-05 — 계측과 분석

`scripts/gem5/benchmark.py`의 exact ROI 선택과 mode/worker/channel 검증을 재사용한다.
Microbenchmark용 channel-all-active 조건을 모든 application에 강제하지 않는다.
Cache-resident kernel의 DRAM traffic 0이나 특정 channel 사용은 합법적일 수 있으므로
workload별 expected coverage를 둔다.

Counter inventory는 CPU committed instructions/cycles·stall, cache demand hit/miss와
resource stall, NoC packet/flit/queue/link 지표, DRAM bytes/queue/service/row-hit/refresh를
대상으로 한다. 모든 항목이 현재 collector에 있다는 뜻은 아니다. Version별 native stat
이름·단위·분모를 확인하고 누락을 0으로 대체하지 않는다. 필요한 항목만 parser에 추가한다.

Rate/latency/histogram은 additive counter와 달리 단순 합산하지 않는다. Online power
epoch를 쓰는 경우 기존 additive accounting 제약을 따른다. 초기 DSE baseline에서는
DVFS/online power를 끄고 고정 clock으로 비교해 ROI 해석을 단순하게 한다.

## 7. DES-DSE-06 — Candidate 평가

먼저 [target 판정 규칙](requirement.md#target-rules)에 따라 comparator/statistic/sample/margin을
적용하고 필수 scenario별 성능 충족과 evidence를 검사한다. 다음으로 performance,
area/power/cost 등 알려진 축에서 다른 후보보다 불리한 후보를 식별한다. 비용 자료가
없는 경우 성능 관점 shortlist까지만 만들고 PPA Pareto optimum이라 부르지 않는다.
단독 실행의 shortlist는 잠정 상태다. 동시 workload에서 target 미충족, 병목 이동,
순위 역전이 발생하면 이전 제외 후보를 재평가한다.

유효한 필수 target 불충족은 `MODEL_INFEASIBLE`, target/표본/evidence 누락은
`UNDECIDED`로 구분한다. 최소 충족안은 사전에 정한 비용 목적함수/우선순위와 자료 범위에서
선택한다. Area·power·가격이 서로 충돌하고 우선순위가 없으면 단일 최적값 대신 비지배
후보 집합을 제시한다. 성능 target가 모두 충족해도 비용 누락을 숨기지 않는다.

불확실한 CPU request-generation, cache latency, NoC delay, DMC timing 등의 근거 있는
범위를 바꿔 candidate 순위를 점검한다. 근거 없는 범위는 가정임을 표시한다. 순위가
바뀌거나 target margin이 사라지면 추가 근거가 필요한 결정을 명시한다.
Area/power는 외부 estimate의 process/voltage/frequency/조건을 맞춰 비교한다.

<a id="artifacts"></a>
## 8. DES-DSE-07 — Evidence와 decision record

다음은 campaign 구조다. 실제 생성된 파일과 검증 상태는 진행 기록을 따른다.

```text
build/qbox-apollo-qvp/gem5/soc-spec-<timestamp>/
  campaign.json              # targets, identity, candidate/workload/scenario 목록
  inventory.json             # 과거 결과의 재사용 가능성 및 이유
  cases.csv                  # 실행 계획과 실행/수치/target 상태
  source-<repository>.patch  # dirty 상태가 있으면 보존
  snapshots/<candidate>/     # 기존 launcher의 snapshot artifacts
  runs/<case>/               # launch/result/UART 및 m5out 원본
  comparison.json            # 동일 조건 검사, 지표, 가설별 분석
  decision.md                # 사양 후보, 근거, margin, 제외/보류 이유
```

기존 run의 authoritative artifact는 `launch.json`, `result.json`,
`m5out/config.json`, `m5out/resolved-profile.json`, `m5out/roi-events.json`,
`m5out/stats.txt`, `m5out/roi-summary.json`, `m5out/system.platform.terminal`,
backend fingerprint/part provenance를 담는 `m5out/manifest.json`이다.
기존 effective-config verifier로 생성한 `config-verification.json` 또는 명시한 별도 output도
연결한다. Verifier에는 해당 run과 matching native binary를 사용한다.
실제로 생성되지 않은 optional artifact는 누락 이유를 기록한다. 새 manifest가 기존
parser/launcher에 구현되기 전에는 이 계약을 명시적으로 채운 수동 inventory로 시작한다.

Decision record에는 candidate별 사양, target coverage, measurement status,
model qualification, 비용 자료, confidence 한계, 남은 검증, 선택/제외 이유를 연결한다.
Tracked 결과 보고서는 원본 evidence 경로와 hash를 참조하며 대용량 로그를 commit하지 않는다.

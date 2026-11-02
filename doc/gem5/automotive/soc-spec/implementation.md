# Apollo gem5 SoC 사양 탐색 — Implementation

작성일: **2026-10-28**. 상태: **구현·빌드 완료 항목 검증 중 / campaign 진행 중**.
아래 완료 조건은 유지한다. 실제 파일·빌드·실행 상태는
[진행 기록](campaign-20261028.md)에서 항목별로 구분한다.
[Requirement](requirement.md) → [Plan](plan.md) → [Design](design.md) →
**Implementation** → [Verification](verification.md).

## 1. 현재 재사용할 구현

| 구성 | 현재 구현과 재사용 범위 | 제약 |
|---|---|---|
| AP launcher | [run_linux.py](../../../../scripts/gem5/run_linux.py): 입력 해석, checkpoint/resume, UART/tmux, workload 실행 | Root CPU 4/16; command-file은 shell text 전달이며 임의 binary/data 배포 기능이 아님 |
| ROI collector | [benchmark.py](../../../../scripts/gem5/benchmark.py): exact ROI, checksum, mode, O3 worker, channel 검증 | Scenario/target/PPA 판정은 없음; application에 microbenchmark 조건을 그대로 적용하면 안 됨 |
| Guest workload | [benchmark.c](../../../../scripts/gem5/benchmark.c), [memory_bench.c](../../../../hsoc-stack/tools/gem5/workloads/zena_cmn/memory_bench.c) | Atomic 초기화, O3 warmup, 자체 marker; 기본 affinity와 1-pass warmup |
| Profile validation | [parameters.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/parameters.py) | 고정 geometry/rate와 cluster/home 일관성 제약 존재 |
| Effective-config 검증 | [verify_config.py](../../../../hsoc-stack/tools/gem5/scripts/zena_cmn/verify_config.py), [test_verify_config.py](../../../../hsoc-stack/tools/gem5/tests/zena_cmn/test_verify_config.py) | Clock/cache/topology/native memory oracle/DTB 대조; matching native binary 지정 및 새 후보 coverage 확인 필요 |
| Cache/NoC 구성 | [cluster_rnf.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/cluster_rnf.py), [ruby_system_builder.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/ruby_system_builder.py), [chi_topology.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/chi_topology.py) | Hardware-specific timing/CDC/physical topology 검증과 별개 |
| DRAM backend | [memory_backend.py](../../../../hsoc-stack/tools/gem5/configs/zena_cmn/memory_backend.py) | Channel당 MemCtrl; native timing fingerprint; target DMC/PHY 미검증 |
| Native diagnostic | [run_saturation.py](../../../../hsoc-stack/tools/gem5/scripts/zena_cmn/run_saturation.py), [summarize_saturation.py](../../../../hsoc-stack/tools/gem5/scripts/zena_cmn/summarize_saturation.py) | Linux 경로와 분리; profile/geometry/traffic 조건 확인 후 대조 |
| 수렴 분석 | [check_memory_convergence.py](../../../../hsoc-stack/tools/gem5/scripts/zena_cmn/check_memory_convergence.py) | 기존 4-worker/16-MiB 지정 case용; AP16/64-MiB campaign에 그대로 적용 불가 |
| Yocto guest/image | [gem5-apollo-guest.bb](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-devtools/gem5/gem5-apollo-guest.bb), [nexios-gem5-initramfs.bb](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-gem5-initramfs.bb) | 배포 binary 갱신만으로 initramfs 내 binary가 바뀌지는 않음 |

기존 runtime 성공 기록은 [interleave 결과](../../interleave-16core-results.md)와
[Orin-informed 결과](../../orin-informed-benchmark-results.md)에 한정한다. 이번에는
해당 evidence와 새 campaign은 native/image identity가 다르므로 합쳐서 비교하지 않는다.
재집계 결과와 current binary 실행은 진행 기록을 따른다.

## 2. 추가 구현 작업과 완료 조건

### IMP-DSE-01 — Inventory와 campaign identity

P0/P1에서 먼저 기존 run의 manifest, config, stats를 읽어 재사용 가능성을 정리한다.
`launch.json`과 기존 hash 함수를 재사용하고 [Design의 artifact 계약](design.md#artifacts)에
따라 target/scenario와 candidate identity를 기록한다. 초기 case 수가 적으면 수동 manifest로
시작하며 범용 scheduler/database/dashboard를 만들지 않는다.

Raw artifact hash와 candidate 비교용 canonical hash를 구분한다. 기존
`check_memory_convergence.py`의 run 경로/host UART port 정규화를 재사용하고 허용 필드와
version을 기록한다. 서로 다른 port/path의 같은 사양은 같은 canonical identity여야 하며,
clock/cache/주소 배치 또는 input 내용 변경은 계속 검출해야 한다.

Defaults/custom module 등 실제 dependency가 snapshot contract에 빠져 있으면 root
`run_linux.py`의 contract 생성과 관련 host test를 함께 수정한다. 기존 snapshot을 단순히
새 schema에 맞춰 metadata만 고쳐 승인하지 않는다. Version 변경을 명시하고 matching
과거 실행 경로 또는 fresh snapshot을 사용한다.

완료 조건: 같은 입력의 identity 재현, 누락/변경 dependency 검출, 기존 evidence
비덮어쓰기, target 미정 상태의 올바른 기록. 신규 로직이 있으면 fixture 기반 음성 시험을 추가한다.

### IMP-DSE-02 — Parameter와 effective config 대조

Root의 candidate 선택은 기존 `--profile`, `--cpus`, `--channels`,
`--interleave-bytes`를 사용한다. 새로운 CLI alias를 무조건 추가하지 않는다.
기존 `scripts/zena_cmn/verify_config.py`와 `test_verify_config.py`를 먼저 재사용하고
새 후보에 부족한 검증만 추가한다. 해당 run과 matching binary를 `--gem5`로 지정하고
과거 evidence 재검사 시 `--output`을 새 경로로 지정하여 기존 결과를 보존한다.
Native memory oracle도 같은 binary로 실행하며 config 검증 결과와 `m5out/manifest.json`을
campaign evidence에 연결한다.
Gem5 `parameters.py` → CPU/cache builder → Ruby/NoC → DRAM → DTB의 consumer를
추적하고 요청값과 instantiated 값이 다른 경우 실행 전 또는 분석 전에 실패시킨다.

Cache size와 latency/bank/TBE/policy를 묶어 후보로 기록한다. Clock sweep은 CPU,
Ruby/system, mesh domain의 실제 소비자를 확인하고 필요 시 bridge timing과 config
검증을 보강한다. Simple diagnostic의 제약을 풀어 Garnet과 동등하다고 취급하지 않는다.

완료 조건: 허용 후보의 적용 값 확인, 잘못된 SLC total/cluster/clock 조합 거부,
변경하지 않기로 한 parameter의 불변성 확인. Clock 차이가 있는 directed run은 별도 필요하다.

### IMP-DSE-03 — Counter/비교 분석 보강

우선 기존 `roi-summary.json`과 raw `stats.txt`에서 필요한 counter를 찾는다.
Root `benchmark.py` 및 gem5 `scripts/zena_cmn`의 기존 parser/analysis 함수를 재사용한다.
부족한 counter만 추가하며 stat 이름/단위/분모를 test fixture에 고정한다.

Compare는 동일 workload·input·ROI 정의·software baseline과 선언한 hardware 변화인지
검사한다. Worker count, per-array working set, measured passes, warmup count가 다르면
표시하거나 해당 비교를 거부한다. Mode별 useful bytes와 DRAM bytes는 별도 집계한다.
Native backend와 Linux FS는 동등한 path로 합치지 않는다.

Pass 수렴은 useful GB/s, ns/load, DRAM bytes/useful bytes 등 정규화된 값으로 계산한다.
Raw bytes 증가를 수렴 실패로 판단하지 않으며 기준값 0과 사전 tolerance 누락을 처리한다.
Warmup 길이와 measured length 비교를 분리하고, 고정 총 working set에서 workers를 바꿀 때
worker당 크기·cluster·cache 이용 변화도 보고한다. 순수 CPU 공급량 변화로 자동 분류하지 않는다.

완료 조건: 중간 dump/exit dump 혼입 방지, counter 누락/NaN 거부, 가중 평균과
additive/nonadditive 지표 구분, 무효 sample의 평균 포함 방지, 주요 가설별 counter 연결.

### IMP-DSE-04 — Representative kernel의 Yocto 배포와 ROI

Image preprocessing의 기존 source와 license, reference output을 고정한다. 선택한
호출에 host timer와 gem5 marker를 최소한으로 연결하고 initialization/allocation,
warmup, measured loop, output validation 경계를 분리한다. Fixture는 크기·분포·seed를
명시한다. Floating-point 허용 오차는 algorithm 계약에서 정한다.
Frame 순서/reuse/buffer pool과 cold/steady-state 조건을 fixture에 포함한다. Warmup
길이를 확인할 수 없으면 measured passes 증가만으로 warmup 검증을 대신하지 않는다.
Cold-start는 별도 fixture/초기 상태 검증과 scenario-aware collector가 필요하다.
기존 fixed-warmup 경로의 marker만 유지한 채 warmup을 생략해 지원을 주장하지 않는다.

외부 application source이면 owned Yocto layer에 별도 target recipe를 둔다. 프로젝트의
작은 자체 fixture이면 기존 guest package 재사용 가능성을 먼저 검토한다. 최종 선택과
source 소유권을 기록한다. 실제 ELF와 fixture가 `nexios-gem5-initramfs`에 들어간 뒤
새 snapshot에서 실행한다. 원본 algorithm을 바꾸면 별도 workload version을 부여한다.

완료 조건: host/guest output 검사, package manifest와 CPIO 내용 확인, 실제 O3 loop
ROI 확인. `gem5-control run`의 fork/exec 포함 결과를 kernel-only latency로 보고하지 않는다.

### IMP-DSE-05 — Foreground/background coordinator

단독 kernel 측정이 성립한 후 추가한다. Coordinator 하나가 global CPU switch와
warmup/start/end를 소유한다. Worker별 affinity, 준비 barrier, completed work와
foreground release/start/finish를 기록한다. 같은 cluster/다른 cluster 배치에 필요한
최소 affinity 옵션만 추가하고 기존 memory benchmark 기본값을 유지한다.

Foreground가 종료했는데 background가 완료되지 않은 경우 drain/종료 정책을 명확히
한다. Barrier deadlock과 조기 종료를 유효 측정으로 처리하지 않는다. RT scheduling은
별도 명시한 scenario에서만 사용하며 Linux housekeeping/IRQ 조건을 보존한다.
Arrival 방식, queue/drop/backpressure 정책을 고정하고 release/start/finish에 동일한
simulated timebase를 사용한다. 적은 sample로 target percentile 충족을 판정하지 않는다.

완료 조건: 단독/동시 output 일치, 요청한 core 배치, 단일 ROI ownership, background가
실제로 실행되었다는 counter, timestamp 순서, timeout/worker 실패 전파 확인.

### IMP-DSE-06 — 필요한 DRAM/CPU 후보 확장

현재 지원하는 cache/channel/clock 탐색으로 요구를 판단할 수 없을 때 수행한다.
DRAM은 `parameters.py`, `memory_backend.py`, `address_map.py`, custom DRAMInterface,
검증 fixture와 collector를 함께 검토한다. X32나 다른 MT/s는 validation 제한만 풀지
않고 device composition, tCK/timing/refresh, burst, DMC 연결과 주소 범위를 검증한다.

Capacity 변경은 `src/dev/arm/ZenaCSS.py`, FS memory range, DTB, firmware/image load
address와 reserved range까지 검토한다. 8-core 등 새 root topology는 launcher parser,
PSCI firmware build/deploy, Linux DTB/affinity, profile, snapshot, tests가 함께 필요하다.
하위 parser 지원만으로 배포 경로를 우회하지 않는다.

제품 capacity 선정에는 OS/reserved/CMA, model/map, 동시 buffer와 transient peak의
resident 예산을 요구한다. 작은 aperture에서의 성공은 bandwidth 실험 근거로 한정하며
전체 제품의 memory 용량 요구 충족으로 변환하지 않는다.

완료 조건: geometry/address/channel coverage와 부정 입력 거부, native traffic, 필요한
Linux fresh boot 및 O3 ROI, model provenance. 실제 DMC block 수의 해석을 별도 기록한다.

### IMP-DSE-07 — 외부 IP traffic envelope

Vendor/실측/명시적 가정에서 rate, burst, outstanding, locality, coherency와 연결 위치를
정한다. 기존 native generator를 재사용할 수 있는지 확인한 후 필요한 경로만 연결한다.
DRAM 직결과 SLC/CHI 경유를 구분하고 AP와 동일 backend를 의도치 않게 중복 생성하지 않는다.

현재 `npu.enabled` 경로는 checkpoint save/restore가 금지된다. 그 경로를 재사용하면
fresh boot를 선택하거나 serialization/in-flight drain/restore 지원을 별도 작업으로
구현·검증한다. 기존 metadata를 수정해 지원되는 snapshot처럼 처리하지 않는다.

완료 조건: offered/generated/completed bytes, queue/drain, cacheability/maintenance,
접근 주소와 연결 경로 확인. 제품 pipeline trace가 없으면 synthetic scope를 유지한다.
상세 camera/NPU model이나 full AD stack을 선행 필수 작업으로 추가하지 않는다.

### IMP-DSE-08 — 사양 decision report

Target와 measurement를 결합하되 실행 상태·수치 유효성·target 판정을 분리한다.
Comparator/statistic/sample/margin은 Requirement의 식을 사용한다. Target 누락,
표본 부족 또는 unit/ROI 불일치는 `UNDECIDED`, 유효한 필수 target 불충족은
`DOES_NOT_MEET` 및 candidate의 `MODEL_INFEASIBLE`로 구분한다. 외부 PPA 자료의 source,
조건, version을 연결하고 미보정 power 결과를 실제 비용으로 사용하지 않는다.

완료 조건: 모든 candidate의 포함/제외 이유, target coverage, headroom, robustness,
비용 자료 유무와 최종 label을 재집계할 수 있다. 부족한 입력이 있는 결론을 자동으로
`MODEL_FEASIBLE`로 승격하지 않는다.
동시 workload에서 단독 실행의 후보 순위나 병목이 달라지면 제외 후보의 재평가를 기록한다.
사전 지정한 coupled-parameter pair는 단독 효과가 작다는 이유만으로 제외하지 않는다.
비용 목적함수/우선순위가 미정이면 비지배 후보 집합을 보고하고 단일 최저 비용안을 만들지 않는다.

## 3. 변경별 build/검증 경로

| 변경 | 필요한 수행 단계 | 검증 범위 |
|---|---|---|
| 문서만 | Link/source/traceability/Markdown 검사 | Static documentation; runtime 불변 |
| Host collector/launcher | 관련 host test와 기존 fixture 재집계 | 기존 결과 보존 및 malformed input 검출 |
| Profile/Python 구성 | 해당 validation test, native config 확인, 필요한 directed traffic/FS run | Native rebuild가 필요한 SimObject 변경인지 구분 |
| C++/SLICC/SimObject/ISA | Yocto `gem5-native` rebuild, 영향받는 directed test와 FS/O3 회귀 | Build 성공만으로 runtime 완료 처리 금지 |
| Guest kernel/fixture | Target recipe→package→initramfs→fresh snapshot→guest ROI | CPIO 내 실제 binary/input hash와 output 검사 |
| DTB/firmware/memory map | 해당 guest/native artifact와 image, fresh boot/restore | Load range, CPU online, channel 접근과 ROI |

Build를 실행할 때 active `build/conf/{local.conf,bblayers.conf,templateconf.cfg}`와
effective BitBake 변수를 다시 확인한다. 기본적인 경로는 `./yocto_build.sh --gem5 --keep-conf`
이며 기존 conf를 유지한다. Shared BitBake를 직렬화하고 실행 중 source를 바꾸지 않는다.
최초 문서 작성에서는 실행하지 않았으며, 후속 구현 작업의 build 결과는 진행 기록에 남긴다.

## 4. 변경 전 확인할 consumer

최소 영향 경로는 **source → recipe → deploy/package → image → snapshot → launcher →
ROI collector → 비교 보고서**다. Root tooling, gem5 model, Yocto metadata의 repository
ownership을 지킨다. Externalsrc 밖 source를 recipe에서 참조하면 task checksum 반영도
확인한다. 새 code branch/parser에는 유효/무효 입력 test를 붙이고 documentation-only
변경에는 runtime test를 추가하지 않는다.

최초 작성 시 backlog는 **NOT_IMPLEMENTED_AS_CAMPAIGN**이었다. 후속 구현에서는
각 IMP ID에 파일/검증 evidence를 연결하고 실행하지 않은 항목은 `NOT_RUN`으로 유지한다.

## 5. 추가된 실행 경로

- [soc_spec.py](../../../../scripts/gem5/soc_spec.py)는 기존 run을 읽는
  `inventory`와 명시적 campaign JSON의 `report`를 제공한다. 실행 scheduler는 포함하지 않는다.
- [image_bench.c](../../../../scripts/gem5/image_bench.c)는 자체 BSD-3-Clause fixture다.
  RGB uint8 HWC → float CHW normalization과 foreground/background coordinator를 구현하며,
  기존 `gem5-apollo-guest` package에 `apollo-image-bench`로 포함한다.
- [image_summary.py](../../../../scripts/gem5/image_summary.py)는 final buffer pool 전체를
  독립 output hash와 대조하고, frame/CNTVCT·O3 ROI·affinity·background 완료량을 검증한다.
  `--workload command`의 `APOLLO_IMAGE_RESULT`를 launcher가 이 collector로 전달한다.
- 기존 cache/memory workload의 `--warmup-passes 1|2|4|8`은 O3 warmup loop 수를
  바꾼다. `--passes`의 measured work와 별개이며 기본 warmup 1은 유지한다.
- Snapshot launcher contract schema 3은 defaults와 native FS import closure의 hash를
  검사한다. CHI/topology/PyYAML을 포함하며 독립 DRAM/controller 기본값을 먼저 확정한 뒤
  import만 수행한다. `launch.json`에도 공통 model source map을 기록하고 inventory가
  native manifest/verifier와 교차 검증한다. Schema 1/2 metadata는 변환하지 않는다.
  Map 없는 기존 raw measurement는 `HISTORICAL_LIMITED`로 보존한다.

## 2026-10-30 — Bounded policy와 paired assessment

새 [soc_spec_policy.py](../../../../scripts/gem5/soc_spec_policy.py)는 기존 `soc_spec.py`의
raw inventory, provenance 검사와 comparison을 재사용한다. 기존 frozen runner/source는
변경하지 않는다. Policy schema 1은 campaign 경로/hash, 숫자 budget, 실행 case ID,
uncertainty 조건별 comparison 및 convergence reference를 받는다.

- `check`: policy 구조, 계획한 run 수, 실행 시 source/input pins 확인. Runtime PASS가 아니다.
- `run`: 기존 case의 `argv` → `verification_argv`를 직렬 실행한다. `max_runs`와 전체
  `host_seconds`, case timeout을 적용한다. 기존 run/verifier output을 거부하고 새 ledger에
  명령/종료 상태를 기록한다. Timeout 시 자신이 만든 process group만 종료하며 retry하지 않는다.
  남은 case는 NOT_RUN, 유효 raw evidence 없는 exit 0은 ERROR다.
- `assess`: 저장된 raw artifacts를 다시 검사한다. 같은 effective uncertainty coordinate의
  baseline/candidate만 비교하고 lower-is-better는 baseline/candidate−1, higher는
  candidate/baseline−1로 gain을 계산한다. Primary metric의 warmup/length gate와
  explanatory counter 상태를 분리하되 과거 gate 파일은 변경하지 않는다.

`ROBUST_IN_TESTED_CONDITIONS`는 명시한 조건에서 최소 gain을 유지했다는 의미다.
Missing condition, primary gate 미확보는 INCONCLUSIVE다. Model credibility와 제품 판정은
자동 승인하지 않는다. Calibration/validation case가 중복되면 거부하며, 서로 다른 kernel의
유효 raw evidence가 있어야 `PASS_DISTINCT_KERNELS`를 기록한다. 이는 HW calibration 인증이 아니다.

```sh
python3 scripts/gem5/soc_spec_policy.py check POLICY.json --output check.json
python3 scripts/gem5/soc_spec_policy.py assess POLICY.json --output assessment.json
# execute 목록과 pins, 숫자 예산이 고정된 새로운 campaign에만 사용
python3 scripts/gem5/soc_spec_policy.py run POLICY.json --output NEW_EXECUTION_DIR
```

Policy의 `budget`은 `max_runs`, `host_seconds`, `basis`가 필요하다. `pins`는 campaign
디렉터리 기준 source/input 파일 경로와 SHA256 map이며 run에서 필수다. `execute`는
campaign case ID 목록이다. `assessments` 항목은 `id`, `metric`, `direction`(higher/lower),
`min_gain`, `basis`, `required_conditions`, `pairs`다. 각 pair는 `condition`, `comparison`,
`coordinates`(예: `profile.cpu.clock: 2GHz`), `baseline_stability`, `candidate_stability`를
갖는다. Stability 목록은 해당 case를 포함하는 warmup 및 length comparison ID다.
같은 coordinate를 다른 condition 이름으로 중복 등록할 수 없다.

Actual reanalysis 입력은 `build/qbox-apollo-qvp/gem5/literature-implementation-20261030/`
아래에 보존한다. 이는 과거 결과의 post-hoc 재집계이며 사전 등록된 새 실험으로 표시하지 않는다.
Orin 독립 validation, 새로운 uncertainty workload 실행 및 기존 P5/P6 전체 완료와는 별개다.

실제 실행에서 발견한 collector 수정과 재집계 evidence는 [2026-10-30 구현 검증](implementation-20261030.md)에 기록했다.

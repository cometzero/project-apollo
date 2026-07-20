# Apollo QVP 16코어 4클러스터 구현·검증 완료 보고서

- 완료일: 2026-07-20
- 대상: `apollo-qvp`, RD-Aspen cfg2, Yocto `nexios-image`
- 기준: Arm `FVP_Zena_CSS_Cfg2`
- QBox 모드: TCG, `live-cl0-cl1`
- 결과: 선택형 16 CPU/4 cluster 지원 완료, 기본값 4 CPU 복원

## 1. 완료 판정

동일한 16 CPU Yocto image가 FVP와 QBox에서 CPU0~CPU15를 online하고 4개
cluster, 16개 GIC redistributor, SI0 PFDI 16-core monitoring과 대표 CPU
hotplug를 통과했다. QBox에서 누락됐던 SI0 PPU/reset fan-out과 A720AE DSU PMU
programming bank를 QBox Platform/QEMU에서 보강했다. Component source는 변경하지
않았다.

배포 기본값은 4 CPU/1 cluster다. 16 CPU는 image build option이며, image에 기록된
CPU 수를 QBox가 자동으로 따른다.

## 2. 구현 내용

### 2.1 CPU 수 artifact 계약

- `meta-hsoc-auto-solutions`의 기본값은
  `PC_CPUS_COUNT_DEFAULT ??= "4"`다.
- 16 CPU build에서는 `PC_CPUS_COUNT_DEFAULT=16`을 BitBake 환경으로 전달한다.
- `nexios-image.bbappend`는 effective `PC_CPUS_COUNT`를 qboxconf의
  `QBOX_APOLLO_NUM_CPUS`로 전달한다.
- `run_qbox_yocto.sh`의 선택 순서는 explicit environment, qboxconf,
  `build/conf/local.conf`, fallback 4다.
- qboxconf parser는 CPU 수를 decimal `1..16`으로 검증한다.

16 CPU build 명령은 다음과 같다.

```bash
export BB_ENV_PASSTHROUGH_ADDITIONS="${BB_ENV_PASSTHROUGH_ADDITIONS:-} PC_CPUS_COUNT_DEFAULT"
export PC_CPUS_COUNT_DEFAULT=16
./yocto_build.sh
```

검증 종료 뒤 일반 환경에서 `bitbake -e nexios-image`로 다음을 확인했다.

```text
BAREMETAL_IMAGE_NUM_CPUS="4"
PC_CPUS_COUNT="4"
PC_CPUS_COUNT_DEFAULT="4"
QBOX_APOLLO_NUM_CPUS="4"
```

같은 명령에 `PC_CPUS_COUNT_DEFAULT=16`을 passthrough하면 네 값이 모두 16이다.

### 2.2 4×4 AP power/reset topology

`qbox-platform`은 다음 불변조건을 사용한다.

```text
cpu_index = cluster * 4 + core
MPIDR affinity = cluster * 0x10000 + core * 0x100
```

SI0의 4개 cluster PPU와 16개 core PPU가 활성 CPU reset input에 연결되고,
system-reset target도 선택된 CPU 수에서 동적으로 생성된다. CPU0 cold boot 경로는
유지하고 CPU1~CPU15는 기존 PSCI→SCMI→SCP-firmware→PPU 흐름으로 release한다.

### 2.3 A720AE DSU PMU

기존 QEMU bank는 Linux의 undefined system-register trap만 막고 counter 수를 0으로
보고했다. 이를 MPIDR Aff2별로 공유하는 6-counter stateful bank로 바꿨다.
`CLUSTERPMCR`, enable, overflow, selector, interrupt enable, event type/counter와
cycle counter의 read/write state를 유지하며 Linux가 event `0x2a`, `0x2b`를
schedule할 수 있다.

FVP와 QBox 모두 이번 `sleep` 기반 probe에서 네 DSU source의 두 event를 정상
schedule하고 count 0, return code 0을 보였다. 따라서 상수 no-counter stub는
제거됐지만 실제 cache/memory transaction에 따른 증가와 overflow SPI 216~219
발생은 남은 fidelity debt다.

## 3. Build와 정적 검증

### 3.1 Yocto image

```bash
./yocto_build.sh
```

결과는 7,293 tasks 전부 성공, error 0이었다. effective configuration은 TF-A
`PLATFORM_CORE_COUNT=16`, SCP-firmware
`SCP_PC_CONFIGURED_CORES_COUNT=16`, image `BAREMETAL_IMAGE_NUM_CPUS=16`이었다.

Artifact manifest는
`build/apollo-qvp-16core/artifact-manifest.json`에 있다. 핵심 결과는 다음과 같다.

- DT CPU nodes 16, `cpu-map` 4 clusters × 4 cores
- L3 cache 4개, 각 4 MiB
- `arm,dsu-pmu` node 4개
- GICR 16 frames, `0x2088_0000`부터 `0x20c4_0000`, stride `0x40000`
- UKI command line `maxcpus=16`
- qboxconf `QBOX_APOLLO_NUM_CPUS=16`

QEMU 변경 뒤 provider 재검증도 수행했다.

```bash
source layers/poky/oe-init-build-env build
bitbake qbox-libqemu-native qbox-apollo-qvp-native
```

1,059 tasks 전부 성공했고 error는 없었다.

### 3.2 QBox local build와 targeted test

```bash
./local_build.sh qbox
/usr/bin/python3 -m pytest -q \
  tests/test_run_qbox_yocto_sh.py \
  tests/test_validate_qbox_apollo_topology.py \
  tests/test_run_test_manifest.py \
  tests/test_run_qbox_fvp_rd_aspen_rse.py
```

local QBox build가 성공했고 targeted suite는 79 tests가 통과했다. DSU test는
수정 전 six-counter assertion 실패를 확인한 뒤 수정 후 통과했다. 또한 RSE runner의
DSU source 검사가 지원 glob 하나가 없을 때 false-negative가 되던 문제를 고치고
회귀 test를 추가했다.

최종 diff review에서 최초 DSU owner 선택이 `Aff0`만 제거해 Apollo의
`Aff2=cluster / Aff1=core` topology에서 CPU별 state가 되는 결함을 발견했다.
Aff0와 Aff1을 모두 제거하고 candidate도 같은 mask로 비교하도록 수정했다. 강화한
test는 수정 전 실패, 수정 후 통과했고 최종 관련 suite는 135 tests가 통과했다.

## 4. FVP와 QBox 런타임 결과

| 항목 | FVP | QBox | 판정 |
| --- | --- | --- | --- |
| Linux SMP | `16 CPUs` | `16 CPUs` | 일치 |
| possible/present/online | `0-15` | `0-15` | 일치 |
| topology | 4 clusters × 4 cores | 4 clusters × 4 cores | 일치 |
| GICR | CPU0~15 exact affinity | CPU0~15 exact affinity | 일치 |
| PFDI | AP 4×4 online monitoring | AP 4×4 online monitoring | 일치 |
| hotplug | CPU1/4/8/12 off/on | CPU1/4/8/12 off/on | 일치 |
| DSU sources | `arm_dsu_0..3` | `arm_dsu_0..3` | 일치 |
| DSU event 0x2a/0x2b | count 0, rc 0 | count 0, rc 0 | 일치 |

### 4.1 FVP evidence

- 기본 16 CPU 부팅·hotplug:
  `build/apollo-qvp-16core/fvp-20260720-222319/`
- DSU perf:
  `build/apollo-qvp-16core/fvp-dsu-perf-interactive-20260720-230740/`
- Linux log marker:
  `smp: Brought up 1 node, 16 CPUs`
- hotplug 후 최종 상태: `online_final=0-15`

FVP host에는 pwndbg가 설치한 Python 3.13 library와 launcher prefix 충돌이 있어
runtime-only fvpconf의 `env.PYTHONHOME=/usr`로 host environment를 정렬했다. Yocto
image와 component source에는 영향을 주지 않는다.

### 4.2 QBox evidence

- 기본 16 CPU 부팅:
  `build/apollo-qvp-16core/qbox-20260720-223427/`
- representative hotplug:
  `build/apollo-qvp-16core/qbox-hotplug-20260720-223720/`
- DSU 최종 parity:
  `build/apollo-qvp-16core/qbox-dsu-pmu-final-20260720-232627/`
- Aff2 공유 수정 후 최종 provider/runtime:
  `build/apollo-qvp-16core/final-provider-build.log`,
  `build/apollo-qvp-16core/qbox-final-aff2-20260720/`
- 각 QBox `result.json`: `passed=true`, `verdict=pass`, `blocker=null`
- full coverage 및 AP map audit: pass

추가 측정 실행 한 번은 TF-A PFDI core 7 handoff에서 정지했으나 즉시 재시도와
최종 DSU run은 통과했다. 재현되지 않은 단발성 관찰로 기록하며 이번 완료의
blocker로 분류하지 않는다.

Aff2 수정 후 최종 run도 16 CPU, 16 GICR, 4 DSU source와 SI0 AP 4×4 PFDI
monitoring을 통과했다. 이 run에서 AP Linux PFDI module이 CPU0 diagnostic 실행
timeout을 한 번 출력했지만 이어진 `pfdi-cli --result 0..3`은 모두 정상이고 SI0/SI1
timeout signature와 completion gate는 모두 정상이다. 과거 2026-07-18 run에서 한
번 관찰된 비결정적 AP-side warning이며, 16-core power/PFDI monitoring 실패로
분류하지 않는다.

Target image에는 `taskset` utility가 없어 CPU별 userspace pinning probe는 실행하지
못했다. 대신 모든 CPU의 GICR bring-up, per-CPU timer interrupt, 4×4 topology와
서로 다른 네 cluster 대표 CPU hotplug로 16 CPU lifecycle을 검증했다.

## 5. Component no-touch 확인

구현 전 revision은
`build/apollo-qvp-16core/baseline/component-revisions.tsv`에 기록했다. 종료 시 다음
repository의 HEAD와 clean status를 다시 비교했다.

- Linux, U-Boot, TF-A, OP-TEE
- TF-M, SCP-firmware
- Zephyr, `zephyr_hsoc_src`

최종 비교 결과 8개 repository가 모두 baseline과 같은 HEAD였고 working tree도
clean이었다.

모든 기능 변경은 top-level workflow/test, `qbox-platform`, QEMU와
`meta-hsoc-auto-solutions`에만 있다. QBox core source 변경은 필요하지 않았다.

## 6. 저장공간과 정리

최종 문서화 시점의 `/build` 여유 공간은 약 47 GiB였다. Yocto/local build 결과를
건드릴 필요가 없었고, 이번 판정 근거인 runtime evidence도 보존했다. 용량 부족
조건이 발생하지 않아 과거 실행 디렉터리를 임의 삭제하지 않았다. 디버깅을 위한
source logging 변경은 남기지 않았고 session journal만 최종 검증 뒤 제거한다.

## 7. 남은 fidelity debt

1. DSU event counter를 실제 modeled cache/memory transaction에 연결한다.
2. counter overflow와 cluster별 SPI 216~219 발생·clear를 구현한다.
3. 16 CPU fault/reset 동시성 stress와 KVM backend는 별도 extended validation이다.
4. FVP/QBox 공통 probe의 자동 JSON comparator는 후속 자동화 항목이다.

이 부채는 이번에 요구한 16 CPU 부팅, topology, GIC/timer, PFDI, hotplug와 FVP가
보인 최소 DSU 결과를 막지 않는다.

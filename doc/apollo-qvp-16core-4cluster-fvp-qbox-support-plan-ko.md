# Apollo QVP 16코어 4클러스터 FVP/QBox 지원 계획

- 작성일: 2026-07-20
- 대상: `apollo-qvp`, RD-Aspen cfg2, Yocto `nexios-image`
- 목표 토폴로지: 4 clusters × 4 Cortex-A720AE = 16 AP cores
- 기준 모델: `FVP_Zena_CSS_Cfg2`
- QBox 실행 모드: TCG, `live-cl0-cl1`, 동일 Yocto 산출물
- 소스 변경 제한: `hsoc-stack/components/` 변경 금지

## 현재 상태

| 단계 | 상태 |
| --- | --- |
| 하드웨어/FVP/Yocto/QBox 소스 분석 | 완료 |
| 상세 설계와 구현·검증 계획 | 완료 |
| Yocto 16코어 profile 구현 | 완료 |
| FVP 기준 검증 | 완료 |
| QBox 구현과 local build 검증 | 완료 |
| 동일 Yocto image QBox 검증 | 완료 |
| FVP/QBox parity 완료 보고 | 완료 |

### 2026-07-20 구현 결과

- 배포 기본값은 요청대로 4코어/1클러스터로 유지했다.
- 16코어 이미지는 `PC_CPUS_COUNT_DEFAULT=16` 환경 override로 선택한다.
- image의 `.qboxconf`가 `QBOX_APOLLO_NUM_CPUS`를 전달하므로 같은 image를
  QBox에서 실행하면 별도 runtime override 없이 동일한 CPU 수를 선택한다.
- QBox의 SI0 PPU/reset 배선을 4클러스터 × 4코어로 일반화했고 CPU0~CPU15의
  PSCI/SCMI bring-up과 대표 hotplug를 확인했다.
- QEMU A720AE DSU PMU를 6-counter cluster-shared stateful register bank로
  전환했다. FVP와 QBox 모두 `arm_dsu_0..3`에서 event `0x2a`, `0x2b`를
  schedule하고 0을 반환했다.
- FVP와 QBox에서 16 CPU, 4 cluster, 16 GICR, PFDI 16-core monitoring과
  CPU1/4/8/12 offline/online을 확인했다.
- Linux, U-Boot, TF-A, OP-TEE, TF-M, SCP-firmware와 Zephyr component source는
  수정하지 않았다.

세부 명령, 로그와 남은 fidelity debt는
[완료 보고서](apollo-qvp-16core-4cluster-completion-report-ko.md)에 기록한다.

## 1. 결론과 권장 방향

Arm Zena CSS의 Primary Compute 하드웨어 기준은 4개 Processor Block이며, 각
Processor Block은 Cortex-A720AE 4개와 DSU-120AE 1개를 가진다. 따라서 전체
토폴로지는 16코어, 4 DSU cluster, cluster당 4 MB L3 cache다.

Apollo FVP는 실행 모델 자체에 16코어 하드웨어가 이미 포함되어 있다. 현재
4코어 동작은 FVP instance 수가 4라서가 아니라 Yocto의
`PC_CPUS_COUNT_DEFAULT = "4"`가 TF-A, SCP-firmware, DT와 Linux `maxcpus`를
4로 구성하기 때문이다. 실제 배포된 `.fvpconf`에도 CPU 수를 바꾸는 FVP
parameter는 없다.

계획 수립 당시 QBox full-system은 CPU/GIC 생성 코드가
`QBOX_APOLLO_NUM_CPUS=1..16`을 받을 수 있고 16개 GIC redistributor address
footprint도 갖고 있었지만, 다음 항목은 16코어 full-system 동작으로 증명되지
않았다. 위 완료 결과와 완료 보고서가 이 목록을 폐쇄한다.

1. full-system 기본값과 산출물 계약이 여전히 4코어다.
2. live SI0의 AP core PPU reset 출력은 cluster 0의 CPU0~CPU3에만 연결된다.
3. CPU4~CPU15의 PSCI→SCMI→SCP→PPU→CPU reset release가 검증되지 않았다.
4. 16개 functional redistributor와 per-core PPI/IRQ 전달이 런타임으로 검증되지
   않았다.
5. A720AE QEMU 모델의 DSU PMU system register는 undefined trap 방지용
   `N=0` no-counter bank다. FVP의 `test_20_aspen_ap_dsu`와 동일한 PMU 기능
   결과를 제공하지 못한다.
6. 16코어 PFDI online/OoR monitoring, CPU hotplug와 reset lifecycle evidence가
   없다.

권장 구현 순서는 다음과 같다.

1. Yocto CPU 수를 16으로 바꾸고 산출물에 CPU 수를 기록한다.
2. 같은 산출물을 FVP에서 먼저 부팅하여 기준 로그와 기능 결과를 만든다.
3. QBox의 16코어 topology, GIC와 live SI0 PPU reset 배선을 수정한다.
4. `local_build.sh qbox`로 QBox 변경을 먼저 빌드·정적 검증한다.
5. FVP에서 사용한 동일 Yocto 산출물을 QBox에서 부팅한다.
6. 16코어, 4클러스터, PFDI, GIC/timer, hotplug와 DSU 기능을 비교한다.
7. FVP 기준에서 남은 차이를 QBox/QEMU/qbox-platform에서 폐쇄한 뒤 결과 문서를
   갱신한다.

에뮬레이터 특성상 boot time, 처리량, host CPU 사용량과 RSS는 pass/fail 기준에
포함하지 않는다. timeout은 무한 대기 방지를 위한 실행 상한일 뿐 성능 기준이
아니다.

## 2. 범위와 비범위

### 2.1 필수 범위

- `apollo-qvp` Yocto의 `PC_CPUS_COUNT=16`
- TF-A power-domain tree 4 clusters × 4 cores
- MPIDR affinity `Aff2=cluster`, `Aff1=core`, `Aff0=thread(0)`
- Linux DT의 16 CPU nodes와 4개 `cpu-map` cluster
- 4개 DSU L3 topology와 DSU PMU programming model
- AP GIC distributor, ITS와 16개 functional redistributor
- CPU별 generic timer PPI와 PMU PPI
- PSCI CPU_ON/OFF와 SCMI power-domain ID 0~15
- SI0의 4 cluster PPU와 16 core PPU programming path
- AP PFDI monitor 16-core online/OoR path
- 같은 Yocto firmware/rootfs/DT를 사용한 FVP/QBox 비교
- RSE, SI CL0, SI CL1, TF-A와 Primary Compute 로그 보존

### 2.2 비범위

- KVM backend
- 16코어 성능 또는 host resource pass/fail 기준
- CHI/CMN cycle accuracy와 cache contention 성능
- 실리콘과 동일한 analog, PHY, DCLS diagnostic coverage 수치
- `hsoc-stack/components/`의 TF-A, SCP-firmware, Linux, U-Boot, OP-TEE,
  TF-M 또는 Zephyr 소스 수정

Component는 같은 소스 revision을 16코어 build parameter로 다시 빌드한다. build
parameter 변경은 허용하지만 component working tree patch는 허용하지 않는다.

## 3. 확인한 하드웨어 계약

분석 기준은 현재 checkout의 Arm Zena CSS `v2.2`
(`bf34d9e71f674e11beea3b8e84ea54486f555d2a`)다. 구현 시에는 다음 문서 식별자와
URL을 evidence manifest에도 기록한다.

| 문서 | 버전/식별자 | 위치 또는 URL |
| --- | --- | --- |
| Arm Zena CSS Developer Guide | checkout `v2.2` | `doc/arm_zena_css_dev_guide/` |
| Arm Zena CSS source documentation | checkout `v2.2` | `arm-zena-css/documentation/` |
| DSU-120AE TRM | Arm 문서 `107721` | <https://developer.arm.com/documentation/107721> |
| RD-Aspen FVP model/config | Zena CSS `v2.2`, cfg2 | `arm-zena-css/yocto/meta-zena-css-bsp/` |

DSU PMU 구현을 시작하기 전에 Arm portal에서 사용 가능한 `107721`의 정확한 문서
revision을 확인해 완료 보고서에 고정한다. FVP 관찰값만으로 register semantics를
추정하지 않는다.

### 3.1 Primary Compute

| 항목 | Arm Zena CSS 계약 | 소스 근거 |
| --- | --- | --- |
| Processor Block | 4개 | `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md:9` |
| CPU | Cortex-A720AE 16개 | 같은 파일 `:9` |
| cluster 구성 | cluster당 CPU 4개 + DSU-120AE 1개 | `arm-zena-css/documentation/design/components.rst:202-209` |
| L3 | DSU cluster당 4 MB shared L3 | `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md:9` |
| interrupt | GIC-720AE distributor, redistributor, ITS | 같은 파일 `:9` 및 `components.rst:211` |
| power/performance | DSU cluster 하나가 SCMI performance domain 하나 | `arm-zena-css/documentation/design/power_and_performance_control.rst:129-130` |

### 3.2 MPIDR와 Linux CPU 번호

RD-Aspen/Apollo DT는 cluster를 Aff2, cluster 내부 core를 Aff1에 배치한다.

| Cluster | Linux CPU | MPIDR affinity 값 |
| --- | --- | --- |
| 0 | CPU0~CPU3 | `0x00000`, `0x00100`, `0x00200`, `0x00300` |
| 1 | CPU4~CPU7 | `0x10000`, `0x10100`, `0x10200`, `0x10300` |
| 2 | CPU8~CPU11 | `0x20000`, `0x20100`, `0x20200`, `0x20300` |
| 3 | CPU12~CPU15 | `0x30000`, `0x30100`, `0x30200`, `0x30300` |

근거는 TF-A `fdts/rdaspen-defs.dtsi:12-39,210-220`과 Linux
`arch/arm64/boot/dts/arm/apollo-qvp.dtsi:52-80,82-202`다. QBox의 현재
`mp_affinity()`도 `cluster * 0x10000 + core * 0x100`으로 같은 형식을 사용한다.

### 3.3 GIC와 interrupt

- PPI는 모든 AP core에 개별 존재한다.
- SPI는 모든 AP core가 공유한다.
- QBox canonical GIC view는 GICD `0x2080_0000`, GICR
  `0x2088_0000`, CPU당 `0x40000` 간격이다.
- 16개 GICR frame의 전체 크기는 `0x0040_0000`이다.
- DSU PMU SPI는 cluster 0~3에 각각 216~219다.
- SI0가 보는 AP cluster/core PPU interrupt와 fault route도 4×4 구조다.

근거는 Programmer's Model의 AP PPI/SPI 정의
(`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:1320-1356`)와
TF-A `apollo_qvp/include/platform_def.h:153-173`, DT의 DSU PMU nodes
(`apollo-qvp.dtsi:636-657`)다.

### 3.4 Power와 reset 흐름

16코어 secondary bring-up의 기준 경로는 다음과 같다.

```text
Linux CPU bring-up
  -> TF-A PSCI CPU_ON(MPIDR)
  -> SCMI power-domain request(domain 0..15)
  -> SI CL0 SCP-firmware power-domain module
  -> cluster/core PPU register programming
  -> QBox PPU model
  -> target Cortex-A720AE reset release
  -> GICR wake/initialization
  -> secondary CPU enters TF-A/Linux
```

TF-A의 Apollo QVP topology는 16개 SCMI domain mapping을 이미 조건부로 정의한다
(`apollo_qvp_topology.c:26-73`). SCP-firmware의 Apollo QVP platform은 4 clusters,
cluster당 4 cores와 20개 AP PPU element를 이미 생성한다
(`platform_core.h:16-44`, `config_ppu_v1.c:164-260`). 따라서 component 소스
변경 없이 `PLATFORM_CORE_COUNT=16`과 기존 PPU register programming을 사용할 수
있다.

## 4. Yocto와 FVP의 현재 구성 경로

### 4.1 CPU 수 전파

```text
PC_CPUS_COUNT_DEFAULT=16  # 16코어 검증 시 명시하는 선택 옵션
  -> PC_CPUS_COUNT=16
     +-> TF-A: PLATFORM_CORE_COUNT=16
     +-> SCP-firmware: SCP_PC_CONFIGURED_CORES_COUNT=16
     +-> nexios-image: BAREMETAL_IMAGE_NUM_CPUS=16
     |                 -> kernel cmdline maxcpus=16
     +-> OEQA: expected CPU/cluster count=16/4
     +-> QBox qboxconf/runtime CPU count=16   [이번 계획에서 artifact 계약으로 보강]
```

현재 source route는 다음과 같다.

- 최대 cluster/core 수:
  `arm-zena-css/.../conf/machine/fvp-rd-aspen.conf:19-23`
- TF-A build argument:
  `trusted-firmware-a-fvp-rd-aspen.inc:123-125`
- SCP build argument:
  `scp-firmware-fvp-rd-aspen.inc:135-140`
- Linux `maxcpus`와 hotplug expected count:
  `hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-image.bb:22-31`

### 4.2 FVP 모델 구성

`apollo-qvp.conf`는 RD-Aspen machine을 상속하고 cfg2에서
`FVP_Zena_CSS_Cfg2`를 사용한다. 현재 배포된
`nexios-image-apollo-qvp.fvpconf`는 firmware, flash, WIC, UART, GIC multiview와
DRAM parameter를 포함하지만 CPU 수 parameter는 포함하지 않는다. 즉 FVP
하드웨어 footprint는 16코어이고, guest-visible/active core 수는 firmware와 DT,
`maxcpus`가 선택한다.

### 4.3 이미 존재하는 FVP CPU/DSU 테스트

- `test_30_configurable_pc_cores.py`
  - kernel log의 `smp: Brought up 1 node, 16 CPUs`
  - DT CPU node 수 16
  - `nproc --all` 결과 16
- `test_20_aspen_ap_dsu.py`
  - 4개 DSU cluster 계산
  - CPU별 L3 `4096K`
  - cluster별 `shared_cpu_list`
  - `arm_dsu_0..3`의 event `0x2A`, `0x2B` `perf stat`

이 테스트를 FVP reference에 먼저 실행하고, 같은 명령을 QBox에서도 실행하는
것을 parity 기준으로 사용한다. FVP 전용 test harness에 QBox를 억지로 연결하지
않고 공통 probe script가 같은 guest command와 판정을 수행하게 한다.

## 5. 계획 수립 당시 QBox 16코어 준비 상태와 gap

| 영역 | 현재 상태 | 16코어 판단 | 필요한 조치 |
| --- | --- | --- | --- |
| CPU instance | `AP_NUM_CPUS=1..16`, CPU loop 존재 | 정적 준비 | default/artifact 값을 16으로 정렬하고 runtime 증명 |
| MPIDR | Aff2 cluster, Aff1 core | 준비 | 16개 affinity unit test 추가 |
| GIC | `num_cpus=AP_NUM_CPUS`, active GICR loop | 정적 준비 | 16개 frame을 모두 functional owner로 검증 |
| GIC multiview | 16-frame view0 footprint | 부분 준비 | CPU15 `Last`, affinity와 backend route 검증 |
| CPU timer/PPI | CPU loop로 PPI 23/25/26/27/29/30 연결 | 정적 준비 | CPU0~15 interrupt 증가와 wake 검증 |
| live SI0 core PPU | cluster 0 CPU0~3만 reset output 연결 | 미완료 | 4×4 PPU를 linear CPU index로 연결 |
| system reset | cluster 0 core PPU만 reset target에 포함 | 미완료 | 활성 4 cluster/16 core PPU를 생성식으로 포함 |
| SCMI service model | CPU1~N reset loop | 16 준비 | live SI0와 구분하여 회귀만 유지 |
| SCP power domains | component가 4×4 생성 | 준비 | component 변경 없이 실제 live firmware로 검증 |
| PFDI | firmware table은 AP 16 core를 정의 | 미검증 | 16 online/OoR, timeout/error 로그 검증 |
| L3 topology | DT가 4 MB L3 ×4 기술 | 정적 준비 | sysfs shared list 비교 |
| DSU PMU | QEMU A720AE가 `N=0` no-counter bank 제공 | FVP 불일치 | cluster-shared functional subset 구현 |
| runner | local.conf의 default를 읽고 없으면 4 | 취약 | qboxconf의 CPU 수를 artifact 기준으로 사용 |
| evidence | 16코어 full-system result 없음 | 미완료 | FVP/QBox 공통 JSON과 로그 생성 |

## 6. 목표 QBox 구조

### 6.1 CPU 수의 단일 기준

Yocto image가 CPU 수의 source of truth다.

1. image metadata에서 `QBOX_APOLLO_NUM_CPUS="${PC_CPUS_COUNT}"`를 생성한다.
2. `.qboxconf`의 검증된 `env` 항목에 CPU 수를 기록한다.
3. `run_qbox_yocto.sh`의 우선순위는 다음과 같이 한다.
   - 사용자가 명시한 `QBOX_APOLLO_NUM_CPUS`
   - 선택한 `.qboxconf`의 CPU 수
   - active `build/conf/local.conf`
   - 최후 fallback
4. runtime `result.json`에는 artifact CPU 수, requested CPU 수, modeled CPU 수,
   DT CPU 수와 Linux online CPU 수를 각각 기록한다.
5. 다섯 값이 모두 16이 아니면 pass하지 않는다.

`qboxboot.bbclass`에는 이미 `QBOX_ENV_PASSTHROUGH`로 선택된 값을 `.qboxconf`의
`env` object에 기록하는 기능이 있다. 따라서 새 metadata format을 추가하지 않고
image bbappend에서 `QBOX_APOLLO_NUM_CPUS = "${PC_CPUS_COUNT}"`를 정의하고 해당 변수
하나만 passthrough한다. Host reader는 임의의 `env` 전체를 shell에 export하지 않고
`env.QBOX_APOLLO_NUM_CPUS`만 allowlist로 읽어 numeric `1..16`을 검증한다.

이 방식은 오래된 local.conf와 새 image를 섞었을 때 잘못된 CPU 수로 실행하는
문제를 방지한다.

### 6.2 CPU와 GIC topology

QBox Lua에 다음 명시적 topology helper를 둔다.

```text
AP_CORES_PER_CLUSTER = 4
cluster(cpu_index)   = floor(cpu_index / 4)
core(cpu_index)      = cpu_index % 4
mpidr(cpu_index)     = cluster << 16 | core << 8
```

- CPU0만 boot CPU다.
- CPU1~CPU15는 powered-off/reset-held 상태에서 시작한다.
- GIC `num_cpus=16`, `redist_region={1 × 16}`으로 구성한다.
- GICR canonical frame은 CPU0~CPU15 모두 QEMU GIC가 소유한다.
- view0은 같은 canonical backend로 변환하며 별도 GIC state를 만들지 않는다.
- GICR affinity는 CPU MPIDR과 일치하고 `Last`는 마지막 유효 frame에서만 보인다.

### 6.3 live SI0 PPU/reset 연결

현재 cluster 0에 제한된 reset binding을 다음 규칙으로 일반화한다.

```text
cpu_index = cluster * AP_CORES_PER_CLUSTER + core

if cpu_index < AP_NUM_CPUS:
    AP core PPU(cluster, core).power_on_reset -> ap_cpu_cpu_index.reset
else:
    inactive PPU는 CPU reset target에 연결하지 않음
```

- CPU0의 cold boot `power_on_load` 경로는 유지한다.
- CPU1~CPU15는 SCP-firmware가 해당 core PPU를 ON으로 전환할 때 release한다.
- AP system reset은 활성 cluster/core PPU와 모든 AP CPU reset을 일관되게 초기화한다.
- 한 CPU reset input에 서로 독립된 출력이 중복 연결되는지 먼저 검사한다.
- 중복 driver가 실제로 존재할 때만 `system_reset OR cluster_off OR core_off`를
  계산하는 작은 reset combiner를 추가한다. 필요성이 확인되기 전에는 새 component를
  만들지 않는다.

### 6.4 DSU PMU

계획 수립 당시 QEMU A720AE의 `CLUSTERPM*` register bank는 Linux bind 시
undefined sysreg trap을 피하지만 counter 수를 0으로 보고했다. 구현 후에는
Aff2 기준 cluster-shared 6-counter state와 아래 programming register가 존재한다.

최종 목표는 다음과 같다.

- Aff2 기준 4개 cluster-shared DSU PMU state
- `CLUSTERPMCR`, counter enable/disable, selector, event type, event counter,
  cycle counter와 event capability register의 stateful 동작
- 최소 FVP test event `0x2A`(L3 refill), `0x2B`(L3 access) 지원
- 같은 cluster의 4개 CPU가 같은 PMU state를 관찰
- reset/hotplug 뒤 register state와 counter ownership 보존 규칙 명시
- overflow를 지원하는 경우 cluster별 SPI 216~219 route

구현은 상수 read-only stub가 아니라 enable, overflow, selector, event type,
event counter와 cycle counter의 read/write state를 유지한다. 다만 이번 최소 검증의
FVP도 `sleep` workload에서 event `0x2A`, `0x2B`를 0으로 계수했으므로 QBox도 같은
관찰 결과를 제공한다. 실제 DSU/cache transaction 기반 증가와 overflow SPI
216~219 발생은 남은 fidelity debt다.

QEMU 변경을 최소화하기 위해 먼저 현재 A720AE custom path 안에서 해결하고,
QBox core에는 공용 API가 반드시 필요한 경우에만 좁은 hook을 추가한다. 독립
`a720ae-dsu` QOM/QBox component가 필요하다는 근거가 나오면 4개 instance를
qbox-platform에서 생성하고 CPU affinity로 연결한다.

## 7. 단계별 구현 계획

### Stage 0. 기준 고정과 no-touch guard

### 변경

- 구현 시작 시 다음 component repository의 HEAD와 working-tree status를 기록한다.
  - Linux
  - U-Boot
  - TF-A
  - OP-TEE
  - TF-M
  - SCP-firmware
  - Zephyr 및 `zephyr_hsoc_src`
- 허용 변경 root를 top-level, `hsoc-stack/tools/qbox`,
  `hsoc-stack/tools/qbox-platform`, `hsoc-stack/tools/qemu`, Yocto project layer로
  제한한다.
- `build/apollo-qvp-16core/baseline/component-revisions.tsv`를 생성한다.

### 완료 조건

- component working tree가 시작 시 clean이다.
- 종료 시 같은 HEAD이고 `git diff --quiet`다.
- 기존 사용자 변경이 있으면 해당 repository를 수정 대상에서 제외하고 상태를
  evidence에 보존한다.

### Stage 1. Yocto 16코어 profile과 artifact 계약

### 변경 후보

- `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/local.conf.sample`
  - 기본값은 `PC_CPUS_COUNT_DEFAULT ??= "4"`
  - 16코어 검증은 외부에서 `PC_CPUS_COUNT_DEFAULT=16`을 전달
- active `build/conf/local.conf`
  - 실제 검증 build도 16으로 설정
- `hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-image.bbappend`
  - `QBOX_APOLLO_NUM_CPUS = "${PC_CPUS_COUNT}"`
  - `QBOX_ENV_PASSTHROUGH`에 `QBOX_APOLLO_NUM_CPUS`만 추가
- `hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass`
  - 기존 `env` 생성 기능을 그대로 사용하며 변경은 필요할 때만 수행
- `scripts/run/qbox_qboxconf_common.sh`
  - `env.QBOX_APOLLO_NUM_CPUS` allowlist와 numeric `1..16` schema 검증
- `run_qbox_yocto.sh`
  - explicit env > qboxconf > local.conf 순서

### 정적 확인

```bash
source layers/poky/oe-init-build-env build
bitbake -e nexios-image | rg '^(MACHINE|RD_ASPEN_VARIANT|PC_CPUS_COUNT|PC_CPUS_COUNT_DEFAULT|BAREMETAL_IMAGE_NUM_CPUS)='
bitbake -e trusted-firmware-a | rg 'PLATFORM_CORE_COUNT=16'
bitbake -e scp-firmware | rg 'SCP_PC_CONFIGURED_CORES_COUNT=16'
```

### build

```bash
./yocto_build.sh
```

필요하면 문제 위치를 줄이기 위해 TF-A, SCP-firmware와 image를 targeted build한
뒤 전체 `yocto_build.sh`를 실행한다.

### 산출물 검사

- deploy DTB CPU node 16개
- `cpu-map` cluster 4개, cluster당 core 4개
- MPIDR 값이 3.2 표와 일치
- DSU L3 node 4개, 각 4 MB
- DSU PMU node 4개, CPU phandle grouping 4개씩
- GICR region이 16 frame을 수용
- kernel cmdline `maxcpus=16`
- `.qboxconf` CPU count 16
- `.fvpconf`와 `.qboxconf`가 같은 deploy artifact 이름을 참조

### 완료 조건

- component source diff 없이 16코어 image build 성공
- configuration manifest의 모든 CPU count가 16

### Stage 2. FVP 16코어 기준 실행과 로그 추출

### 실행

```bash
./run_fvp.sh \
  --machine apollo-qvp \
  --no-attach \
  --out-dir build/apollo-qvp-16core/fvp
```

FVP flash writeback은 pristine deploy image에서 만든 run 전용 copy를 사용한다.
기존 persistent FVP/QBox state와 섞지 않는다. 부팅 후 공통 probe를 SSH 또는
Primary Console에서 실행하고 완료 후 tmux/FVP를 정상 종료한다.

### 추출 로그

- `rse.log`
- `safety_island_cl0.log`
- `safety_island_cl1.log`
- `tf-a.log`
- `primary_compute.log`
- FVP stdout/command line
- `probe.json`, `artifact-manifest.json`, `summary.txt`

### 필수 probe

```bash
cat /sys/devices/system/cpu/possible
cat /sys/devices/system/cpu/present
cat /sys/devices/system/cpu/online
nproc --all
find /sys/firmware/devicetree/base/cpus -maxdepth 1 -name 'cpu@*' | wc -l
lscpu --extended=CPU,ONLINE,SOCKET,CLUSTER,CORE,NODE
```

추가로 다음을 실행한다.

- CPU0~CPU15 각각에 `taskset -c N`으로 짧은 checksum workload 실행
- cluster 대표 secondary CPU 1, 4, 8, 12의 offline→online
- `/proc/interrupts`의 per-CPU arch timer delta
- L3 `size`와 `shared_cpu_list`
- `arm_dsu_0..3` event `0x2A`, `0x2B` `perf stat`
- SI0 로그의 AP core 0~15 PFDI online/OoR 상태

### 완료 조건

- TF-A/Linux가 16 CPU를 bring up
- 4 cluster topology와 DSU test 통과
- PFDI, PSCI, GIC 또는 kernel error 없음
- FVP 결과가 이후 QBox 비교의 immutable baseline이 됨

FVP가 16코어에서도 실패하면 QBox 구현을 진행하지 않고 먼저 Yocto artifact 또는
component build configuration 문제로 분류한다. component source를 patch해서
우회하지 않는다.

### Stage 3. QBox 16코어 topology와 reset 구현

### qbox-platform 변경

1. `platforms/apollo/hw-block/config.lua`
   - full-system fallback을 active 16코어 profile과 정렬
   - cores-per-cluster, cluster/core/index helper를 명시
   - 16코어 MPIDR와 count invariant assert
   - AP system reset target을 활성 cluster/core 전체에서 생성
2. `platforms/apollo/hw-block/ap_compute.lua`
   - 기존 CPU/GIC loop를 16코어로 regression-test
   - 16 CPU, 16 GICR, CPU별 IRQ/FIQ/virtual IRQ와 timer PPI binding 확인
3. `platforms/apollo/hw-block/si_cl0.lua`
   - 4×4 PPU의 linear CPU index 계산
   - CPU0 boot release는 유지
   - CPU1~15 core PPU reset release 연결
   - inactive topology일 때 존재하지 않는 CPU target을 만들지 않음
4. `platforms/apollo/hw-block/system_mgmt.lua`
   - service-model 1..N loop 회귀 유지
   - live SI0에서는 실제 PPU owner가 reset을 제어함을 assertion/evidence로 고정
5. runner/validator
   - result에 artifact/requested/modeled/DT/online CPU count 기록
   - 16개 CPU affinity, GICR, PPU target uniqueness 검사

### QBox core/QEMU 변경 원칙

- 16 CPU object 생성과 GIC가 현재 generic 구현으로 동작하면 QBox core와 QEMU를
  수정하지 않는다.
- CPU reset completion, MTTCG/WFI 또는 GIC 내부 제한이 실제 실패로 확인될 때만
  최소 변경한다.
- DSU PMU는 Stage 6의 확인된 별도 fidelity gap으로 다룬다.

### 완료 조건

- generated Lua topology에 CPU0~15가 정확히 한 번씩 존재
- 각 core PPU가 올바른 CPU reset 하나에 연결
- MPIDR와 GICR affinity가 DT와 일치
- missing/duplicate binding 없음

### Stage 4. QBox local build와 정적 검증

### build

```bash
./local_build.sh qbox
```

### 최소 정적/targeted 검증

```bash
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qemu diff --check
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
python3 -m pytest -q \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_yocto_sh.py
```

추가 targeted test는 다음만 필수다.

- 16 CPU Lua elaboration
- expected MPIDR 16개
- GIC `num_cpus=16`, GICR count 16
- PPU reset target CPU0~15 set equality
- qboxconf CPU count precedence
- invalid CPU count 0/17 reject

### 완료 조건

- local QBox build 성공
- 16코어 topology unit/static test 통과
- component source diff 없음

### Stage 5. 동일 Yocto image의 QBox full-system 부팅

### 실행

```bash
QBOX_APOLLO_NUM_CPUS=16 \
./run_qbox_yocto.sh \
  --machine apollo-qvp \
  --si-mode live-cl0-cl1 \
  --headless \
  --exit-after-pass \
  --no-persistent-rse-state \
  --out-dir build/apollo-qvp-16core/qbox
```

명시적 env 없이도 `.qboxconf`에서 16이 선택되는 두 번째 dry-run 또는 smoke를
실행해 artifact contract를 검증한다. 위 명시적 env run은 모델 자체 문제와
metadata 전달 문제를 분리하기 위한 첫 진단 run이다.

### 관찰 순서

1. RSE와 SI CL0 boot
2. SCP-firmware의 16 AP power-domain/PPU 초기화
3. TF-A CPU0 진입
4. CPU1~15 PSCI/SCMI CPU_ON
5. GICR CPU0~15 초기화
6. Linux 16 CPU online
7. AP PFDI 16 core 정상 상태
8. login 후 공통 probe

### 실패 분류

| 최초 실패 | 우선 조사 영역 |
| --- | --- |
| CPU4가 시작되지 않음 | cluster1 PPU base, core PPU→CPU4 reset binding, SCMI domain 4 |
| CPU8/12 경계에서 실패 | Aff2 MPIDR, cluster index, PPU stride, TF-A power tree |
| GICR 탐색 실패 | active GICR count/route, affinity, `Last`, multiview translation |
| secondary WFI 고착 | reset-held QK, target-vCPU reset completion, timer/SGI wake |
| PFDI timeout | MHU requester identity, 16 channel/table count, QBox scheduling hold |
| Linux 16 node/4 online | DT와 `maxcpus`, modeled CPU 수 불일치 |

### 완료 조건

- FVP와 같은 artifact로 login 도달
- 16 CPU online, 4 cluster topology
- CPU0~15 workload 성공
- representative hotplug 성공
- PFDI timeout/error 없음
- kernel panic, RCU stall, GICR error와 PSCI CPU_ON failure 없음

### Stage 6. DSU와 16코어 기능 parity 폐쇄

### 6.1 먼저 현재 결과 확인

QBox에서 FVP와 동일한 L3/sysfs와 `perf stat` command를 실행한다. L3 topology는
DT로 통과할 가능성이 높지만, 현재 QEMU `CLUSTERPMCR.N=0` 때문에 DSU event는
실패할 것으로 예상한다. 실제 실패 signature를 evidence로 남긴 뒤 DSU 변경을
시작한다.

### 6.2 DSU PMU 구현

- QEMU A720AE custom DSU register bank를 stateful cluster-shared 모델로 전환
- cluster selection은 MPIDR Aff2를 사용
- event capability에 `0x2A`, `0x2B`를 정확히 노출
- counter enable/select/read/write/reset 동작 구현
- 지원 event의 counter source를 virtual time과 memory transaction hook에 연결
- 필요 시 cluster별 SPI 216~219 출력 추가
- reset, CPU hotplug와 4 CPU 동시 access race test 추가

### 6.3 기능 test

- 기존 FVP DSU 테스트와 같은 command 통과
- 같은 cluster의 다른 CPU에서 counter state 공유 확인
- 다른 cluster counter 독립성 확인
- 4 cluster에서 각각 event 실행
- CPU hotplug 후 PMU가 잘못된 CPU affinity에 남지 않음

### 완료 조건

- FVP와 같은 `perf stat` event scheduling/read probe 통과
- no-counter compatibility stub가 남지 않음
- 실제 traffic counter 증가와 overflow IRQ는 별도 fidelity debt로 명시되며 이번
  최소 검증의 FVP 관찰 결과에는 영향 없음

### Stage 7. FVP/QBox 비교, 문서화와 최종 gate

### 공통 evidence schema

```json
{
  "machine": "apollo-qvp",
  "variant": "cfg2",
  "requested_cpus": 16,
  "modeled_cpus": 16,
  "dt_cpus": 16,
  "online_cpus": "0-15",
  "clusters": 4,
  "cores_per_cluster": 4,
  "mpidr": [],
  "gicr_frames": 16,
  "dsu_clusters": 4,
  "pfdi_online_cpus": 16,
  "artifact_hashes": {},
  "component_revisions": {},
  "tests": {}
}
```

### 비교 항목

| 항목 | FVP/QBox 동일 판정 |
| --- | --- |
| artifact | firmware/DT/kernel/rootfs identity가 동일 |
| boot domains | RSE, SI0, SI1, TF-A, Linux 필수 marker 모두 존재 |
| CPU | DT/modeled/online/count가 모두 16 |
| topology | 4 cluster × 4 core와 MPIDR mapping 동일 |
| GIC | 16 GICR, timer PPI와 representative SPI delivery 성공 |
| power | CPU1,4,8,12 offline/online 성공, PSCI/SCMI error 없음 |
| PFDI | AP core 0~15 정상, timeout/force-error 없음 |
| DSU | L3 grouping과 필수 PMU event 4 cluster 모두 성공 |
| logs | QBox에만 존재하는 fatal/error signature 없음 |

timestamp, host path, MAC 주소와 emulator banner처럼 기능에 영향이 없는 차이는
normalization한다. error를 지우기 위해 broad regex로 필터하지 않는다.

### 문서 갱신

- 이 문서에 stage별 상태와 evidence path 추가
- `doc/apollo-qvp-machine-architecture-ko.md`
  - active 16-core topology, GIC ownership, PPU/reset invariant 갱신
- `doc/qbox-fvp-emulation-project.md`
  - 16-core status와 남은 fidelity debt 갱신
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`
  - 16-core Yocto 실행 방법과 artifact CPU 수 계약 갱신
- 별도 완료 보고서
  - `doc/apollo-qvp-16core-4cluster-completion-report-ko.md`

## 8. 최소 검증 gate

빠른 구현과 검증을 위해 다음 gate만 필수로 한다. 성능 benchmark, soak와 exhaustive
fault matrix는 수행하지 않는다.

| Gate | 필수 결과 |
| --- | --- |
| G0 config | BitBake effective CPU count 16, component source clean |
| G1 artifact | DT 16 CPUs/4 clusters, `maxcpus=16`, qboxconf CPU 16 |
| G2 FVP | login, 16 CPU, topology, workload, representative hotplug, DSU, PFDI |
| G3 QBox build | `local_build.sh qbox`, focused static/unit test pass |
| G4 QBox boot | same image login, 16 CPU online, no fatal error |
| G5 core function | CPU0~15 taskset, GIC timer, CPU1/4/8/12 hotplug |
| G6 fidelity | PFDI 16, DSU L3/PMU 4 cluster, FVP/QBox comparator pass |
| G7 no-touch | 모든 component HEAD/status가 baseline과 동일 |

### 즉시 실패 pattern

- `CPU.*failed to come online`
- `psci:.*failed`, `SCMI.*timeout`
- `GICR.*failed`, `redistributor.*not found`
- `rcu: INFO: rcu_.*stall`
- kernel panic, synchronous abort, undefined sysreg trap
- AP core PFDI timeout 또는 예상하지 않은 force-error
- CPU count 16/cluster count 4 불일치
- component source diff 발생

## 9. 변경 소유권

| 변경 | owning repository |
| --- | --- |
| Yocto 16-core default와 qboxconf metadata | top-level/`meta-hsoc-auto-solutions` |
| Apollo Lua topology, PPU/reset, GIC wiring | `hsoc-stack/tools/qbox-platform` |
| generic reset/CPU lifecycle helper가 실제 필요할 때 | `hsoc-stack/tools/qbox` |
| A720AE DSU PMU system register/shared state | `hsoc-stack/tools/qemu` |
| runner, probe, comparator와 top-level docs | top-level repository |
| TF-A/SCP/Linux/U-Boot/OP-TEE/TF-M/Zephyr | 변경 금지 |

QBox와 QEMU 변경은 Apollo 요구를 이유로 unrelated code를 정리하지 않고, 기존
upstream 대비 diff를 최소화한다.

## 10. 구현 중단과 rollback 기준

1. FVP 16코어가 동일 Yocto image로 먼저 통과하지 않으면 QBox 변경을 중단한다.
2. component source 수정이 필요해 보이면 우회 patch를 만들지 않고 원인을
   architecture/configuration gap으로 보고한다.
3. 16 CPU를 위해 GIC state를 두 군데 복제해야 하는 설계가 나오면 구현을 중단하고
   canonical owner를 다시 검토한다.
4. firmware timeout 증가만으로 통과하는 변경은 허용하지 않는다. QBox scheduling,
   reset 또는 MHU 원인을 수정한다.
5. 4코어 regression이 발생하면 configurable 1..16 contract가 깨진 것이므로 16코어
   완료로 판정하지 않는다.

최종 source default는 4코어로 복원하고 16코어는 build profile에서 선택한다.
따라서 일반 `yocto_build.sh`와 QBox full-system은 4코어이며, 16코어는
`PC_CPUS_COUNT_DEFAULT=16`으로 image를 만들고 artifact의 `.qboxconf`가 QBox
runtime 수를 16으로 전달한다.

## 11. 권장 atomic commit 경계

1. `feat(yocto): enable Apollo 16-core profile`
2. `feat(apollo): wire four-cluster CPU power`
3. `test(apollo): cover 16-core topology`
4. `feat(qemu): model A720AE DSU PMU`
5. `test(apollo): compare FVP and QBox SMP`
6. `docs(apollo): report 16-core parity`

각 commit은 Conventional Commits, English message와 `git commit -s`를 사용한다.
Component submodule pointer는 component 소스가 바뀌지 않으므로 변경하지 않는다.

## 12. 최종 완료 정의

다음 조건을 모두 만족해야 “Apollo QVP 16코어 4클러스터를 QBox가 FVP와 동등하게
지원한다”고 판정한다.

1. Yocto `PC_CPUS_COUNT=16` image가 component source patch 없이 빌드된다.
2. 해당 image가 FVP에서 16 CPU/4 cluster로 부팅하고 필수 probe를 통과한다.
3. 동일 artifact가 QBox `live-cl0-cl1`에서 16 CPU/4 cluster로 부팅한다.
4. CPU0~15 실행, representative hotplug, GIC/timer와 PSCI/SCMI가 동작한다.
5. SI0 PFDI가 AP core 0~15를 정상 감시하고 timeout/error가 없다.
6. 4개 DSU의 L3 topology와 필수 PMU event가 FVP/QBox에서 모두 통과한다.
7. FVP/QBox 로그 비교에서 QBox 고유 fatal/error가 없다.
8. QBox/QEMU/qbox-platform과 project metadata만 변경됐고 component HEAD와 source
   tree는 시작 시점과 동일하다.
9. 성능 수치 없이 기능 evidence와 명시적 남은 fidelity gap을 완료 보고서에
   기록한다.

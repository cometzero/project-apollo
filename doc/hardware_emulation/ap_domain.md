# AP Domain: Saturn Apollo QVP와 SoC Hardware 비교

작성 기준: 2026-10-28, `apollo-qvp` / Saturn-V full-system 구성.

Apollo QVP의 AP Domain은 firmware와 OS가 사용하는 CPU instruction, register,
address map, interrupt, timer 및 DMA translation을 중심으로 구성한 functional
emulation이다. 실제 Zena CSS의 CPU pipeline, Cache hierarchy, CHI fabric,
DRAM controller/PHY를 cycle 단위로 재현하는 모델은 아니다. 따라서 같은
software가 동작하거나 같은 register 값을 읽는 것과 실제 SoC의 성능·지연·
fault coverage가 같은 것은 구분해야 한다.

이 문서는 CPU, DSU, Cache, GIC-720AE, Timer, Counter, SRAM, DRAM,
CMN-S3AE Bus, MMU-720AE를 다룬다. RSE와 Safety Island는 AP와 연결되는
Counter, address view, interrupt 경계만 설명한다. 각 domain의 상세 문서는
별도로 추가한다.

## 1. 비교 기준과 근거

### 1.1 Hardware, reference software, QVP의 구분

| 비교 대상 | 이 문서에서 사용하는 근거 | 해석 범위 |
| --- | --- | --- |
| Zena CSS Hardware 구성 | Software Developer Guide `110125_0001_01_en`, r0p1, §1·§5·§9 | 선택된 CPU/Cache/mesh 구성과 address/interrupt map |
| 개별 Arm IP | Cortex-A720AE, DSU-120AE, GIC-720AE, CMN S3(AE), MMU-720AE TRM | IP의 기능과 interface; IP의 최대 구성은 Zena CSS의 선택 구성과 다를 수 있음 |
| RD-Aspen reference software | `arm-zena-css/documentation/` 및 해당 firmware/DT | firmware가 기대하는 programming model; 실제 silicon 측정값은 아님 |
| Saturn Apollo QVP | 실제 Lua 생성 경로, `qemu-components`, `systemc-components`, QEMU backend | 현재 checkout에 연결된 모델의 동작과 한계 |
| Saturn board 실물 | `board/saturn-v.lua`의 schematic parity가 `UNVERIFIED` | schematic/BOM, DDR 실장량 및 실제 SoC revision의 일치 여부는 미확인 |

Hardware baseline은 [Zena CSS product highlights][zena-highlights],
[functional blocks][zena-blocks], [AP memory/interrupt map][zena-map]이다.
Reference stack은 [Primary Compute 설명][arm-components]을 함께 참조한다.
예를 들어 reference stack의 DSU L3 **최대 32 MB**라는 IP 설명과 Zena CSS의
**cluster당 4 MB** 선택값을 같은 값으로 취급하지 않는다.

### 1.2 Source snapshot

작성 시작 시 root와 아래 nested repository의 tracked worktree 변경은 없었다.
문서의 경로와 symbol은 다음 revision을 기준으로 한다.

| Repository | HEAD |
| --- | --- |
| root | `84377083fa5c4c5def9b671a51f405e74a63f4b9` |
| `hsoc-stack/tools/qbox-platform` | `e301c1a17e0afed0638da5ea36a6505fd1775199` |
| `hsoc-stack/tools/qbox` | `5fc8c389f5f3d5a3c7bb92d60efa2ce826ec3d51` |
| `hsoc-stack/tools/qemu` | `f4abc1001d0d76322005ba5fcbff08e8592c25c9` |
| `arm-zena-css` | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |

Reusable component는 `qbox/{qemu-components,systemc-components}`에,
Apollo overlay는 `qbox-platform/{qemu-components,systemc-components}`에
속한다. A720AE wrapper와 Counter mirror도 Apollo overlay에 있다.
Codebase index의 새 `soc/` 경로 coverage가 불완전하여, 이 문서는 직접 읽은
source와 실제 Lua binding을 근거로 작성했다.

### 1.3 실행 구성과 기본값

| 계층 | 확인한 값 | 주의점 |
| --- | --- | --- |
| `build/conf/local.conf` | `MACHINE ??= "apollo-qvp"`, `PC_CPUS_COUNT_DEFAULT ??= "4"` | 로컬 설정 파일 값; 이번 작업에서 `bitbake -e`는 실행하지 않음 |
| `build/conf/templateconf.cfg` | `meta-hsoc-auto-solutions/conf/templates/apollo-qvp` | template 경로 |
| `build/conf/bblayers.conf` | Zena BSP/SI 및 owned `meta-hsoc-{bsp,auto-solutions}` 포함 | build 입력을 확인한 것이며 배포 binary 일치 검증은 아님 |
| [SoC 기본 config][soc-config] | AP enabled, `AP_NUM_CPUS=16` | standalone SoC API 기본값 |
| [VP execution policy][vp-execution] | 환경 미설정 시 AP disabled; enable 시 기본 4 cores | bare Lua 호출과 launcher를 구분해야 함 |
| [full-system runner][full-runner] / [Yocto launcher][yocto-launcher] | runner 기본 expected AP=4; launcher는 환경/config 값을 해석 | `QBOX_APOLLO_NUM_CPUS`와 실제 DT/firmware CPU 구성이 맞아야 함 |
| [VP model policy][vp-models] | `systemc-mmu720ae`, host memory DMI 기본 false | runner override와 실행 결과를 따로 기록해야 함 |

이 문서에서 **16-core 지원**은 모델이 구성할 수 있는 topology를 뜻한다.
현재 로컬 기본값의 **4-core 실행 구성**이나 이번 작업의 runtime 실행 결과를
16-core로 바꾸어 해석하지 않는다. 이번 문서 작성 중 QBox/FVP는 실행하지 않았다.

## 2. QBox 구성과 component 경계

### 2.1 생성 경로

| 순서 | Source | 역할 |
| --- | --- | --- |
| 1 | [apollo-qvp-saturn-v.lua][entry] | Saturn full-system entrypoint |
| 2 | [vp/options.lua][vp-options] | SoC 기본값 위에 environment·execution·model policy 적용 |
| 3 | [vp/profiles/full-system.lua][full-profile] | domain 구성, Saturn board 연결, VP backend와 diagnostics 구성 |
| 4 | [vp/composition.lua][composition], [soc/apollo.lua][soc] | domain별 hardware 생성 및 연결 |
| 5 | [soc/hw-block/ap_compute/ap_compute.lua][ap-assembly] | CPU, memory, interconnect, system, safety, peripheral assembly |
| 6 | [board/saturn-v.lua][board] | 외부 board population 연결; AP CPU/DSU 구현 자체는 SoC 계층 소유 |

### 2.2 실제 transaction 경로

| 경로 | QVP의 연결 | Hardware와 비교할 때의 의미 |
| --- | --- | --- |
| CPU instruction 실행 | `cpu_arm_cortexA720AE` → QEMU `cortex-a720ae` / TCG | SystemC wrapper가 CPU pipeline을 구현하는 것은 아님 |
| CPU load/store | QEMU CPU memory interface → TLM `ap_router` → address view/router → target | CPU MMU translation 이후 physical transaction; CMN CHI packet 경로는 아님 |
| SRAM/DRAM | router → `gs_memory`; 설정과 허가에 따라 DMI 가능 | host-backed memory에 접근; Cache/DDR timing을 통과하지 않음 |
| PCIe DMA, 기본 backend | bus master → `smmuv3_tbu` → `smmuv3` translation → `ap_router` | CPU MMU와 별개인 I/O translation 경로 |
| CMN 초기화 | CMN GPV access → `host_cmn_cyprus` | discovery/config register 접근; 모든 AP data traffic이 이 모델을 통과하지 않음 |
| AP interrupt | device SPI / per-core PPI → `gicx00_multiview`의 QEMU GIC backend → CPU | logical interrupt routing과 CPU interface 동작 |
| 시간 | CSS `arm_system_counter` → QEMU instance별 bridge → CPU/MMIO timer | shared counter 상태를 simulation clock domain에 전달 |

경로 근거: [AP CPU wiring][ap-cpu], [AP interconnect][ap-interconnect],
[AP memory][ap-memory], [AP system][ap-system], [AP PCIe][ap-pcie].

### 2.3 전체 비교 요약

| 항목 | Hardware와 유사한 부분 | 주요 차이 |
| --- | --- | --- |
| CPU | AArch64 실행, exception/translation, CPU 식별, SMP affinity | A720AE pipeline·IPC·speculation·physical DCLS 미재현 |
| DSU | cluster grouping, 일부 PMU register 및 power/reset 제어 경계 | DSU coherency engine·L3 data path·lockstep comparator 없음 |
| Cache | L1/L2 ID 값과 software-visible maintenance 경로 | L1/L2/L3/SLC의 line/state/latency 모델 없음 |
| GIC-720AE | GIC interrupt, ITS, view filtering, 일부 power/RAS register | 분산 HW interface·physical safety 회로·전 구간 safety 배선과 차이 |
| Timer | CPU PPI timer와 MMIO SPI timer, compare/enable/IRQ | real clock jitter·interrupt latency·WCET 재현 불가 |
| Counter | 125 MHz 기준 shared count 및 제어 상태 전달 | physical clock distribution 대신 simulation snapshot/clock 변환 |
| SRAM | boot/shared memory 주소와 read/write | 물리 macro·ECC·retention 대신 host memory, 일부 주소만 구현 |
| DRAM | low/high memory window와 read/write | DMC·DDR PHY·training·refresh·channel timing 없음 |
| CMN-S3AE | GPV discovery와 firmware 초기화 register | CHI coherency·mesh arbitration·SLC·bandwidth 모델 없음 |
| MMU-720AE | 기본 SystemC SMMUv3 translation, queue, fault와 DMA 경로 | 실제 TCU/TBU 수·DTI/LTI signal·AE safety·성능과 차이 |

아래의 “구현”은 source에서 확인한 동작이다. 해당 software 시나리오를 이번에
실행하여 `PASS`로 판정했다는 뜻은 아니다.

## 3. CPU — Cortex-A720AE

### Hardware

Zena CSS는 4 Processor Blocks에 총 16 Cortex-A720AE cores를 배치한다.
각 block은 4 cores와 DSU-120AE로 구성된다. Cortex-A720AE TRM r0p1의
§1.1은 Armv9.2-A, AArch64 execution, EL0–EL3, 48-bit address 및
128-bit SVE/SVE2를 설명한다. 이는 Hardware IP의 기준이며 QVP의 feature
전체 적합성 선언은 아니다. [Cortex-A720AE TRM][a720-trm]

### QVP 구현

| 계층 | Source / symbol | 동작 |
| --- | --- | --- |
| Lua | [cpu.lua][ap-cpu], `cpu.define()` | `cpu_arm_cortexA720AE`, EL2/EL3, core별 GIC/Timer/RAS 연결 |
| QBox wrapper | [cortex-a720ae.h][a720-wrapper], `QemuCpuArm` 생성 | QEMU `cortex-a720ae-arm` CPU 생성과 property 전달 |
| QEMU | [cpu64.c][qemu-cpu64], `aarch64_a720ae_initfn()` | `aarch64_a710_initfn()`을 재사용하고 MIDR·일부 ID field·DSU register 추가 |

CPU의 MP affinity는 `floor(i / 4) * 0x10000 + (i % 4) * 0x100`이다.
즉 cluster는 Aff2, core는 Aff1로 구분한다. 하나의 AP `QemuInstance` 안에
설정된 CPU 수만큼 생성하며 CPU0 외 secondary CPU는 powered-off로 시작한다.
모든 CPU에는 초기 reset이 걸리고 platform reset/power 경로에서 해제된다.
최종 CPU `mem` binding은 [interconnect.lua][ap-interconnect]에서
`ap_router`로 연결한다.

### 유사점과 차이

Instruction 실행, exception level, architectural register, CPU-side MMU와
SMP boot를 통해 TF-A/U-Boot/Linux의 기능을 개발할 수 있는 구조다. 그러나
현재 QEMU CPU 정의는 A710 기반 기능 모델에 A720AE 식별 및 compatibility를
추가한 구현이다. MIDR `0x410FD890`은 모델이 보고하는 **r0p0 식별값**이며,
참조한 TRM r0p1이나 Saturn 실물 revision과 같다는 뜻은 아니다.

Out-of-order pipeline, branch predictor, speculative cache traffic,
instruction별 cycle/IPC, 전력·thermal·physical DCLS comparator를 재현하지
않는다. CPU clock/SCMI 값과 guest benchmark wall time을 실제 A720AE 성능으로
환산할 근거도 없다. CPU RAS register와 fault injection은 별도 기능 모델이며
실제 core 내부 오류 검출 회로의 coverage를 증명하지 않는다.

## 4. DSU — DSU-120AE

### Hardware

DSU-120AE는 cluster 내부 coherency, shared L3, snoop filtering, power
management 등을 담당한다. Zena CSS 선택 구성은 **4 MB L3/cluster**와
**Mixed-configuration의 fixed Hybrid-mode**이다. Hybrid-mode에서는 cores는
독립 실행하고 DSU shared logic은 Lock-Step으로 동작한다.
[Zena functional blocks][zena-blocks], [DSU Hybrid-mode][dsu-hybrid]

### QVP 구현과 차이

| 기능 | 현재 대응 구현 | Hardware 대비 한계 |
| --- | --- | --- |
| Cluster grouping | CPU MPIDR affinity, firmware/DT topology | 독립된 DSU coherency data-path instance가 아님 |
| Cluster PMU | [cpu64.c][qemu-cpu64]의 `a720ae_dsu_pmu` register/state | Aff2 기준 shared state와 6 event counters; 실제 L3 hit/miss에 의한 증가 경로는 확인되지 않음 |
| Cluster power register | 같은 파일의 `CLUSTERPWRCTLR_EL1` 등 | 일부 register는 constant/readback compatibility |
| Core/cluster PPU | [SI CL0 power.lua][si-power]의 `host_ppu`와 CPU/GIC 연결 | software-visible power/reset handshake 모델; physical retention·clock gating·DSU drain timing과 다름 |
| Coherency/L3/Lock-Step | 실행 memory의 기능적 공유 및 별도 compatibility 모델 | DSU SCU, snoop transaction, L3 data/tag RAM, duplicate logic 비교 회로 없음 |

DSU 기능이 단일 `dsu120ae` SystemC instance로 구현된 구조는 아니다.
Cluster 관련 register, PPU, CPU grouping이 여러 component에 분산되어 있다.
따라서 DSU PMU driver가 probe되거나 register read/write가 가능해도 실제
cluster Cache bandwidth·contention·hit rate 측정으로 해석할 수 없다.
[DSU TRM 개요][dsu-overview], [DSU L3][dsu-l3]

## 5. Cache — L1, L2, L3, SLC

| 계층 | Zena CSS Hardware 선택값 | QVP의 대응 | 차이 |
| --- | --- | --- | --- |
| L1 instruction | core당 64 KB | inherited `CCSIDR`가 64 KiB, 4-way, 64-byte line 보고 | 실제 instruction cache line/tag/miss 모델 없음 |
| L1 data | core당 64 KB | inherited `CCSIDR`가 64 KiB, 4-way, 64-byte line 보고 | dirty/eviction/snoop에 따른 traffic 모델 없음 |
| L2 | core당 512 KB | inherited `CCSIDR`가 512 KiB, 8-way, 64-byte line 보고 | 실제 private L2 data path·replacement·latency 모델 없음 |
| L3 | DSU cluster당 4 MB | cluster topology/일부 DSU register | 4 MB shared Cache data array와 coherency engine 없음 |
| SLC | CMN 전체 4 MB | CMN discovery/config register | HN cache slice, snoop filter의 data/state/timing 없음 |

Hardware 값은 [Zena product highlights][zena-highlights], QEMU ID 값은
[cpu64.c][qemu-cpu64]의 A710 초기화와 A720AE override에서 확인했다.
Cortex-A720AE TRM의 Table 6-1·7-1·8-1은 해당 L1/L2 크기를 허용하는 IP
configuration을 설명한다. QVP의 ID 값이 유효한 선택값이라는 점과 Cache가
실제로 simulation된다는 점은 별개다. [Cortex-A720AE TRM][a720-trm]

QEMU의 translated code cache와 software TLB는 host 실행 및 address
translation을 위한 내부 자료구조다. 이를 guest의 L1/L2 Cache로 보아서는
안 된다. Cache maintenance instruction과 barrier의 architectural 처리도
실제 dirty line writeback, DSU snoop, CMN CHI ordering latency를 측정하는
모델은 아니다.

특히 host-backed memory에서 정상 동작한 shared-buffer/DMA code라도 실제
non-coherent device의 cache clean/invalidate 누락을 발견하지 못할 수 있다.
MPAM cache partitioning, cache interference, DDR bandwidth, WCET 평가는
별도의 Cache/coherency/timing 모델 또는 Hardware evidence가 필요하다.

## 6. GIC-720AE

### Hardware와 현재 배치

GIC-720AE는 Distributor, Redistributor, CPU/cluster interface 및 ITS로
interrupt를 처리한다. TRM의 최대 SPI/view/ITS 수와 Apollo 선택값은
구분한다. [GIC components][gic-components], [GIC features][gic-features]

| 항목 | 현재 AP QVP 값 | 주소/번호의 의미 |
| --- | --- | --- |
| GIC revision | 4, GICv4.1 관련 기능 enabled | 설정 및 backend 기능; 전체 virtualization qualification 아님 |
| SPI 수 | 960 | SPI index 0–959 = architectural INTID 32–991 |
| CPU/Redistributor | `AP_GIC_NUM_CPUS`, 최대 16 slots | active CPU 수와 aperture slot 수 구분 |
| 관리 View0 Distributor | `0x20000000`, size `0x80000` | management programming view |
| 관리 View0 Redistributor | `0x20080000`, stride `0x40000` | 최대 16 slots |
| AP View1 Distributor | `0x20800000`, size `0x40000` | AP-visible view |
| AP ITS | `0x20840000`, size `0x40000` | 하나의 활성 ITS |
| AP View1 Redistributor | `0x20880000`, stride `0x40000` | CPU별 Redistributor |
| RGIC2LGIC_MESSREG | `0x5FFF0000`, size `0x10000` | remote-message register window |

구성은 [AP system.lua][ap-system]의 `ap_gic`와 ITS 정의에 있다.
Internal backend 주소 `0x60000000`/`0x61000000`은 private SystemC
`ap_gic_backend_router`의 Distributor/Redistributor decode 주소다.
별도 QEMU instance나 AP global MMIO 주소를 뜻하지 않는다.

### SystemC와 QEMU의 역할

| 계층 | 담당 동작 | Source |
| --- | --- | --- |
| SystemC `gicx00_multiview` | view/owner 검사, AE register, error containment, private backend 접근 | [gicx00_multiview.h][gic-view] |
| QBox `arm_gicv3` wrapper | QEMU `arm-gicv3` 생성, SPI/PPI/CPU/ITS 연결 | [arm_gicv3.h][gic-wrapper] |
| QEMU GIC | pending/active/priority/routing, CPU interface | [arm_gicv3.c][gic-qemu], [arm_gicv3_cpuif.c][gic-cpuif] |
| QEMU ITS | command queue, LPI 및 virtual interrupt 관련 처리 | [arm_gicv3_its.c][gic-its] |
| AE RAS helper | logical diagnostic RAM, error record, ERRINS | [gic720ae_ras.h][gic-ras] |

현재 ITS에는 `VMAPP`, `VMOVP` 등의 처리도 있으므로 GICv4.1을 단순 ID bit
노출로만 설명하는 것도 부정확하다. 다만 모든 virtualization 시나리오의
Hardware 동등성을 이 source 조사로 판정하지 않는다. Multi-view wrapper는
TCG backend를 요구하며 KVM/WHpx와 동일하게 사용할 수 있는 경로가 아니다.

### 유사점과 남는 차이

SGI/PPI/SPI/LPI와 CPU interrupt delivery, view 분리, WAKER/PWRR 관련
software 동작을 구성한다. AP core PPU의 wakeup 입력은 GIC의
`wake_request_out_<n>`과 연결된다. 이는 logical wakeup 경로이며 실제
clock/power domain의 P/Q-channel timing을 재현하지 않는다.
[SI CL0 power wiring][si-power], [GICR_WAKER TRM][gic-waker],
[GICR_PWRR TRM][gic-pwrr]

현재 RAS helper는 64 error records와 35 logical RAM
(Distributor 16, GCI 16, ITS 3)을 다룬다. Physical ECC RAM은 없으며 scrub
completion은 synchronous이다. ERRINS가 있다고 실제 ECC/CRC/lockstep
circuit의 검출율을 측정할 수 있는 것은 아니다.

또한 현재 Lua의 `fmu_error_socket` 연결은 **SI GIC wrapper** 쪽이다.
AP local GICT/RAS 구현을 AP GIC 오류가 SI FMU hierarchy 전체로 전달되는
증거로 확대하면 안 된다. [SI safety wiring][si-safety]

`gic720ae_messreg`는 register storage/readback 모델이며 cross-chip IRQ
transport output이 없다. 따라서 remote-message window의 존재가 multichip
interrupt network 구현을 뜻하지 않는다. [gic720ae_messreg.h][gic-messreg]

## 7. Timer — CPU Generic Timer와 MMIO Generic Timer

Timer는 counter 값을 compare하여 interrupt를 발생시키는 기능이다.
CPU 내부 system-register Timer와 Peripheral Block의 MMIO Timer는 주소,
접근 방법, IRQ가 다르다. 두 종류 모두 현재 기준 주파수는 **125 MHz**다.

### 7.1 CPU Generic Timer

| Timer output | AP GIC architectural INTID | QVP 연결 |
| --- | --- | --- |
| Non-secure physical | 30, PPI | core별 `irq_timer_phys_out` |
| Virtual | 27, PPI | core별 `irq_timer_virt_out` |
| Hypervisor physical | 26, PPI | core별 `irq_timer_hyp_out` |
| Secure physical | 29, PPI | core별 `irq_timer_sec_out` |

[cpu.lua][ap-cpu]와 CPU wrapper가 각 CPU의 QEMU native Generic Timer를
사용한다. 하나의 SystemC timer로 모든 CPU tick을 대체하는 구조가 아니다.
Hardware PPI map의 INTID 19/20/28 timer output은 해당 Lua에서 연결하지
않으므로 모든 architected Timer IRQ가 배선되었다고 해석하지 않는다.
[Zena §9.2.1.1][zena-map]

### 7.2 MMIO Generic Timer

| Frame | AP 주소 | 크기 | IRQ |
| --- | --- | --- | --- |
| CNTCTL | `0x1A810000` | 64 KiB | control frame |
| Secure frame 1 | `0x1A820000` | 64 KiB | SPI index 48 = INTID 80 |
| Non-secure frame 0 | `0x1A830000` | 64 KiB | SPI index 49 = INTID 81 |

[AP system.lua][ap-system]의 `qemu_arm_arch_timer_mmio`가
[QBox timer wrapper][mmio-wrapper]를 통해 QEMU
[`arm_arch_timer_mmio`][mmio-qemu]를 생성한다. Compare/enable/mask에 따라
IRQ를 갱신하고 QEMU virtual-clock deadline을 예약한다. Secure/Non-secure
frame 번호는 주소 순서와 다르다. Arm reference stack도 NS frame을 1에서
0으로 고친 [TF-A patch][timer-patch]를 포함한다.

### 7.3 Hardware와 다른 점

Software의 Timer programming, timeout, interrupt handler 기능을 검토할 수
있는 구조지만 실제 timer clock distribution, comparator propagation,
interrupt latency, CPU wake latency의 cycle 정합성을 제공하지 않는다.

현재 MMIO backend의 read/write callback은 `MemTxAttrs`를 받지 않으며
`CNTACR`/`CNTPL0ACR`는 저장/readback한다. 따라서 frame 이름이 Secure라고
해서 device 자체에서 Secure/Non-secure와 privilege access를 모두 강제한다고
단정할 수 없다. 전체 fabric protection은 별도 검증 대상이다. Architectural
compare/control 의미는 [CNTP_CTL_EL0][cntp-ctl], [CNTP_CVAL_EL0][cntp-cval]을
기준으로 한다.

## 8. Counter — CSS System Counter

### Hardware와 QVP의 공통 목적

System Counter는 여러 CPU와 peripheral Timer가 공통 timebase를 사용하도록
하는 free-running count source다. CPU의 `CNTPCT`/`CNTVCT` 접근, MMIO
counter frame, counter 제어·동기화 register를 구분해야 한다.

QVP는 [System Management system.lua][smd-system]의
`css_system_counter`(`arm_system_counter`)를 공통 source로 사용한다.
Input/reported frequency는 125 MHz, 초기 increment는 1이다.

| CSS window | Global 주소 | QVP component |
| --- | --- | --- |
| Counter control | `0x20000D0100000` | `host_gtimer`, 64 KiB |
| Counter read | `0x20000D0110000` | `host_gtimer`, 64 KiB |
| Counter sync | `0x20000D0120000` | `host_gtimer`, 64 KiB |

이 주소는 SMD/global view이며 AP가 곧바로 쓰는 per-core system register
주소가 아니다. 접근 domain의 router/ATU mapping을 적용해야 한다.
Hardware 대응은 [Zena §9 memory map 및 Generic Timer Synchronization][zena-map]이다.

### 실제 시간 전달 방식

| 단계 | Source | 처리 |
| --- | --- | --- |
| CSS source | [arm_system_counter.cc][counter-source] | SystemC timestamp와 anchor, enable/debug, 8.24 increment로 count 계산 |
| Control/read/sync window | [host_gtimer.cc][host-gtimer] | CNTCR/count/CNTFID0/scaling 및 register 접근 |
| AP CPU mirror | [qemu_arm_counter_mirror.cc][counter-mirror], `effective_frequency()` 및 snapshot publish | 초기 상태와 상태 변경 시 QEMU에 count/anchor/running/frequency 전달 |
| AP MMIO mirror | `qemu_arm_mmio_counter_mirror`, [AP system.lua][ap-system] | 같은 CSS source를 MMIO Timer에 연결 |
| QEMU count 진행 | [target/arm/helper.c][qemu-helper], [MMIO timer backend][mmio-qemu] | snapshot 이후 QEMU virtual clock 경과분으로 count를 진행시키고 deadline 계산 |

매 CPU `CNT*` read마다 SystemC TLM transaction이 발생하는 구조는 아니다.
공통 source의 상태를 mirror하고 각 QEMU clock에서 진행시킨다. 이는
multi-domain timebase의 기능적 일관성을 위한 구현이며 physical counter
distribution의 skew/jitter를 모델링하는 방법은 아니다.

### 차이와 제한

Counter source는 fractional increment를 표현하지만 QEMU mirror의 effective
frequency는 integer 및 `uint32` 범위 제약을 가진다. 모든 fractional scaling
설정이 손실 없이 전달된다고 가정하면 안 된다.

Sync frame에는 register storage/ID 처리가 있으나 실제 multichip offset
estimation, link delay, retry를 포함한 synchronization FSM은 확인되지 않는다.
`CNTCR.FCREQ/CNTSR`를 포함한 모든 frequency-mode handshake의 완전성도 이
문서에서 보증하지 않는다. Counter resolution/increment의 architectural
기준은 [Arm ARM I2.2.1][counter-resolution]이다.

## 9. SRAM

### Hardware address aperture와 QVP backing

[Zena Table 9-3][zena-map]의 Shared SRAM 주소 영역은
`0x00000000–0x07FFFFFF`, **128 MB aperture**다. 이 주소 예약 크기가
물리 SRAM macro 용량 또는 QVP backing 크기를 뜻하지는 않는다.

현재 AP QVP는 아래 네 `gs_memory` object로 **연속 2 MiB**를 backing한다.

| AP base | Size | Object / 목적 |
| --- | --- | --- |
| `0x00000000` | 1 MiB | `host_ap_shared_sram` |
| `0x00100000` | 512 KiB | `host_ap_bl2_header_sram`, boot/header 영역 |
| `0x00180000` | 4 KiB | `host_ap_mhu_ns_shared_sram`, mailbox shared buffer |
| `0x00181000` | 508 KiB | `host_ap_peripheral_ns_sram_tail` |

정의는 [memory.lua][ap-memory]와 [boot.lua][ap-boot]에 나뉜다.
Shared SRAM window 전체가 RAM으로 존재한다고 가정해서는 안 된다.

### 유사점과 차이

Firmware image/data, boot header, shared buffer를 같은 address contract로
읽고 쓸 수 있다. 실제 저장소는 [gs_memory.h][gs-memory]의 host memory와
`memcpy` 기반 read/write다. Bounds, byte-enable, read-only 설정을 처리하고
TLM response를 반환한다.

SRAM macro의 banking, port arbitration, ECC syndrome, retention voltage,
power-loss behavior는 이 memory 모델에 없다. Secure/Non-secure partition
정책도 `gs_memory`의 이름만으로 보장되지 않으며 upstream protection/routing
및 firmware 설정을 함께 검증해야 한다.

`gs_memory`의 `b_transport()`는 `p_latency`를 delay에 더하고 DMI에도 같은
latency를 제공한다. Component 기본값은 **10 ns**이고 이 Lua에서는 별도
override하지 않는다. 이는 고정 transaction annotation이며 실제 SRAM access
cycle이나 host wall-clock delay 측정값이 아니다.

## 10. DRAM

### 현재 QVP memory map

AP CPU enabled 구성에서 [memory.lua][ap-memory]가 다음 backing을 생성한다.

| AP base | Size | Object | 용도 |
| --- | --- | --- | --- |
| `0x80000000` | `0x7F000000` = 2032 MiB | `host_ap_dram1` | low DRAM |
| `0xFFA00000` | 1 MiB | `host_ap_cper` | CPER backing |
| `0xFFBF0000` | 8 KiB | `host_ap_ffa_mm_comm_buffer` | FF-A communication buffer |
| `0xFFC00000` | `0x003E0000` | `host_ap_spmc_sdram` | SPMC backing |
| `0x20000000000` | 2 GiB | `host_ap_dram2` | high DRAM |

Low aperture 전체가 단일 2 GiB RAM은 아니다. 일반 DRAM1, 별도 reserved
backing 및 그 사이의 미할당 범위를 구분해야 한다. Guest가 사용할 수 있는
RAM은 추가로 DT와 reserved-memory, firmware carveout의 영향을 받는다.

Hardware guide의 Table 9-3은 low DRAM `0x80000000–0xFFFFFFFF`와
`0x880000000–0xDFFFFFFFF` 영역을, Table 9-4는
`0x20000000000–0xBFFFFFFFFFFF`의 190 TB high address aperture를 설명한다.
QVP는 이 모든 영역을 채우지 않는다. 특히 **190 TB는 address aperture이며
Saturn의 실장 DDR 용량이 아니다**. [Zena memory map][zena-map]

### Hardware와 다른 점

DRAM도 SRAM과 같은 `gs_memory`를 사용한다. 따라서 data 저장, loader와 CPU/DMA
접근 및 address boundary 검토에는 사용할 수 있으나 DDR bank/row hit,
channel interleave, refresh, controller scheduling, training, PHY calibration,
ECC scrub의 실제 동작과 timing을 제공하지 않는다. DMC control address가
존재하거나 firmware 초기화가 진행되는 것만으로 DMC/PHY model이 있다고
판정할 수 없다.

메모리의 기본 10 ns annotation은 DRAM speed grade 또는 measured latency가
아니다. `host_memory_dmi`가 허용되고 경로의 protection/translation component가
grant하면 DMI로 host memory에 접근할 수 있다. CPER object는 별도
`dmi_allow` override가 없어 component 기본값을 따른다. DMI는 실행 경로의
최적화이며 실제 Cache coherence나 DDR channel을 의미하지 않는다.

## 11. CMN-S3AE Bus — GPV 모델과 data path

### Hardware

Zena CSS의 CMN S3(AE)는 **6 × 4 mesh와 4 MB SLC**를 가진 coherent
interconnect다. Processor, I/O 및 memory interface를 연결하고 CHI/AXI/APB
접근과 CML_SMP 확장을 지원한다. [Zena highlights][zena-highlights],
[functional blocks][zena-blocks]

CMN TRM의 RN-F는 coherent requester, HN-F/HN-S는 coherency와
snoop filter/SLC, SBSX는 CHI에서 memory-side ACE-Lite로 연결하는 역할을
설명한다. 따라서 CMN은 단순 MMIO address decoder보다 넓은 기능을 갖는다.
여기서 참조한 r2p5는 IP 설명용이며 RD-Aspen의 synthesis revision을
단정하는 근거로 사용하지 않는다. [CMN TRM System component selection][cmn-trm]

### QVP 구현

| 항목 | 현재 구현 | Source |
| --- | --- | --- |
| CMN GPV | `0x100000000`, size 1 GiB | [SI CL0 interconnect.lua][si-interconnect] |
| Instance | `si_cl0_cmn_cyprus`, `host_cmn_cyprus`, revision 3 | 동일 Lua |
| Discovery topology | 24 XP와 CFGM/child/HN-S/RN-SAM node 정보 | [host_cmn_cyprus.h][cmn-model], `topology()` 및 seed 처리 |
| Register access | sparse byte storage read/write, 일부 초기 status | 같은 component의 transport |
| 실제 AP data transfer | `ap_router`, `system_router`, `addrtr`, target memory/device | [AP interconnect][ap-interconnect], [router.h][router] |

`si_cl0_`라는 instance 이름은 SCP가 초기화하는 구성 위치를 반영한다.
이를 SI 내부 전용 CMN 또는 AP data traffic을 처리하는 CHI switch라고
해석하면 안 된다. 이 CMN component에는 **target socket만 있고 data를
forward하는 initiator socket이 없다**. Transport는 delay를 사용하지 않고
DMI도 제공하지 않는다.

### 유사점과 차이

Firmware가 GPV를 enumerate하고 node/config register를 초기화할 수 있다는
점은 Hardware programming model과 유사하다. 그러나 GPV에 쓴 RN-SAM 설정이
실제 mesh routing/arbitration을 재구성하는 CHI data-plane 모델은 아니다.

실제 AP access는 TLM router의 address decode, offset 적용, target forwarding
및 가능한 DMI로 처리한다. CHI flit/credit, RN/HN snoop coherency,
SLC fill/evict, mesh hop, QoS contention, congestion 및 CML multichip traffic은
이 경로에 없다. 따라서 **24 XP discovery가 성공했다는 것은 24-XP mesh의
functional coherency나 bandwidth가 구현되었다는 증거가 아니다**.

## 12. MMU-720AE — device SMMU

### 12.1 Hardware 역할

MMU-720AE는 CPU 내부 MMU와 별개로 외부 I/O requester의 address translation과
isolation을 담당한다. Zena I/O Block에는 TCU와 distributed TBU가 있으며
register map에는 `TBULTI00/01/02`, `TBUACE1/2`가 나타난다. TCU/TBU 자체
영역은 I/O Block 128 MiB 중 32 MiB다. [Zena §9.1.6, §9.3.3.1][zena-map]

MMU-720AE TRM의 TCU MSI interface는 AXI5-Stream 기반의 64-bit data와
valid/ready 및 response handshake를 가진다. 아래 QVP의 MSI/IRQ는 이
signal-level interface의 physical timing 구현과 다르다.
[MMU-720AE TRM, TCU MSI interface signals][mmu-trm]

### 12.2 현재 기본 backend의 정확한 구성

**선택 문자열 `systemc-mmu720ae`와 생성되는 module 이름은 다르다.**
현재 [AP system.lua][ap-system]는 reusable SystemC **`smmuv3`와
`smmuv3_tbu`**를 생성한다. `qbox-platform/systemc-components/mmu720ae/`의
legacy component를 이 경로에서 생성하는 것은 아니다. 따라서 과거 문서의
“enabled translation/page-table walker 미구현” 설명을 현재 기본 backend에
그대로 적용하면 안 된다.

| 설정 | 값 / 연결 | 해석 |
| --- | --- | --- |
| TCU instance | `ap_smmu_0`, `moduletype="smmuv3"` | reusable SystemC implementation |
| TBU instance | `ap_smmu_lti00`, `moduletype="smmuv3_tbu"` | 활성 TBU 1개 |
| MMIO | base `0x1C0000000`, size `0x08000000` | 128 MiB socket decode window; 전체 I/O Block 구현 면적을 뜻하지 않음 |
| `pamax`, `sidsize` | 52, 32 | QVP model parameter |
| `iidr`, `ato` | `0x720AE000`, false | QVP 설정값; silicon ID/모든 optional feature의 동일성 보증 아님 |
| Event IRQ | `irq_eventq → ap_gic.spi_in_65` | SPI index 65 = architectural INTID 97 |
| StreamID 선택 | valid RequestContext requester ID 우선, 없으면 `0x40` | 실제 RID propagation 여부가 isolation에 중요 |
| Page-table/queue memory | `ap_router` | memory-backed STE/CD/table/queue 접근 |

Reference DT의 `arm,smmu-v3`, 같은 base/size, `combined` interrupt SPI 65와
`msi-parent`는 [Arm TF-A SMMU DT patch][smmu-dt-patch]에서 확인할 수 있다.
다만 현재 SystemC Lua는 `irq_eventq`만 해당 SPI에 연결한다. 이 연결을
Hardware의 PMU/RAS/GERROR/Secure interrupt 전체를 합친 배선이라고
표현해서는 안 된다.

### 12.3 Translation 기능과 경로

[smmuv3.h][smmuv3]의 `smmuv3_translate()`, `find_ste()`, `read_cd()`,
`smmuv3_ptw64()`는 ABORT/BYPASS, Stage 1, Stage 2, Nested translation을
처리한다. TBU는 translation과 permission을 검사한 뒤 address를 바꾸어
downstream으로 전달한다. CMDQ/EVTQ 처리와 fault record 경로도 존재한다.
다만 `CR0.SMMUEN=0` 또는 `STE_CONFIG_BYPASS`이면 identity mapping을
사용하므로 TBU를 경유하는 것만으로 isolation이 보장되지는 않는다.
실제 translation/isolation은 SMMU enable과 STE/CD 설정에 달린다.

| Traffic | 현재 배선 | 주의점 |
| --- | --- | --- |
| PCIe Root Complex bus master | `ap_gpex_0.bus_master → ap_smmu_lti00.upstream_socket → ap_router` | 기본 DMA translation 경로 |
| AP CPU memory | CPU `mem → ap_router` | CPU MMU 사용; 이 SMMU를 통과하지 않음 |
| PCIe EPC local master | `local_master → ap_router` | 별도 direct 경로; 모든 DMA가 SMMU 보호를 받는 것은 아님 |
| Legacy PCIe IRQ test profile | RID propagation을 끄고 고정 SID 사용 | production path와 test profile을 구분 |

배선 근거는 [AP interconnect][ap-interconnect], [AP PCIe][ap-pcie],
[VP PCIe policy][vp-pcie]다. DMI 요청도 translation/permission을 검사하고
translated page와 downstream grant 경계로 잘라 IOVA 기준으로 반환한다.
Downstream invalidation은 IOVA로 역변환한다. 그러므로 DMI 사용을 곧바로
SMMU bypass라고 할 수는 없다.

### 12.4 차이와 fallback

실제 Hardware의 다수 TBU와 DTI/LTI interconnect, pipeline/cache timing,
AE ECC/lockstep 회로를 단일 TBU translation 경로와 동일시할 수 없다.
`CMD_STALL_TERM` 및 Secure queue PREFETCH의 consume-only 처리처럼
command별 제한도 있다. IDR의 ATS/PRI/MSI advertise와 관련 코드 존재만으로
모든 requester/queue/interrupt 조합의 qualification을 선언하지 않는다.
또한 현재 `find_ste()`와 translation enable 판단은 일반 `STRTAB_BASE/CFG`와
`CR0`를 사용한다. Secure register/IRQ 및 IOTLB regime 구분이 존재한다는
사실만으로 독립 Secure stream-table translation의 동등성을 주장하지 않는다.

`QBOX_RDASPEN_SMMU_BACKEND=qemu-arm-smmuv3`를 선택하면
[QBox arm_smmuv3 wrapper][smmu-qemu-wrapper]와 QEMU device를 사용한다.
현재 Lua fallback은 `stage="1"`, `irq_out_0` 연결이며 PCI bus를 QEMU
SMMU에 붙인다. 기본 SystemC backend와 동일 implementation·feature 범위의
대체물로 가정하면 안 된다.

## 13. 검증 범위와 활용 기준

### 13.1 이 문서에서 수행한 확인

| 확인 항목 | 상태 | 의미 |
| --- | --- | --- |
| Canonical entrypoint → Lua → wrapper/backend 추적 | `STATIC_REVIEW` | 현재 연결된 구현과 미사용 legacy component 구분 |
| Address/IRQ/frequency/topology 대조 | `STATIC_REVIEW` | source와 Zena guide/TRM의 해당 범위 비교 |
| Markdown local link와 수치 일관성 확인 | `PASS` | 문서 구조 검증; hardware test 결과 아님 |
| BitBake datastore / provider build | `NOT_RUN` | config 파일만 확인 |
| Component test / QEMU qtest | `NOT_RUN` | 아래 test source를 참조했으나 재실행하지 않음 |
| QBox boot / guest driver traffic / IRQ | `NOT_RUN` | 이번 문서의 current-runtime PASS 주장 없음 |
| FVP differential / Saturn Hardware 측정 | `NOT_RUN` | FVP 또는 silicon 동등성 판정 없음 |

관련 검증 source는 다음과 같다. Test가 있다는 사실과 그 test를 현재
revision에서 실행하여 통과했다는 사실은 구분한다.

| 대상 | 기존 test source | 추가 runtime evidence가 필요한 내용 |
| --- | --- | --- |
| CPU/cluster 구성 | [Apollo SoC layout tests][soc-tests] | 4/16-core SMP boot, affinity, secondary on/off |
| GIC/ITS | [QEMU GIC qtest runner][gic-tests] | SPI/PPI/LPI, affinity, virtual interrupt, reset/wakeup |
| Counter/Timer | [host_gtimer tests][timer-tests], [AP timer wake test][timer-wake-test] | count 진행/변경/disable, CPU별 timer IRQ와 wakeup |
| SRAM/DRAM | `gs_memory` bounds/transport 구현과 실제 address map | 경계 access, reserved-memory, cross-domain visibility, protection |
| CMN GPV | [host_cmn_cyprus tests][cmn-tests] | SCP discovery/config path; CHI coherence test로 확대 불가 |
| SMMU | [reusable smmuv3 tests][smmu-tests] | requester RID, S1/S2/nested DMA, permission fault, queue/IRQ, DMI invalidation |

SMMU test source에는 `LinearStreamTable_S1_4KPage`,
`RequestContextSelectsStreamId`, `S2Only_4KPage`, `Nested_S1S2_4KPage` 등이
있다. 구형 `mmu720ae` component test 통과를 현재 `smmuv3` backend 검증으로
대체하지 않는다. Boot/login만으로도 위 driver traffic이 검증되지는 않는다.

### 13.2 이 구성으로 판단할 수 있는 것

| 사용 목적 | 판단 |
| --- | --- |
| Firmware register sequence, boot handoff, OS/driver 기능 개발 | 구현된 interface 범위에서 사용 가능; 실제 guest traffic으로 확인 필요 |
| Address/IRQ/StreamID 연결 오류와 translation fault 검토 | 해당 경로를 활성화한 focused test에 적합 |
| Cache miss rate, DSU/SLC interference, CMN bandwidth, DDR latency | 현재 AP QVP 모델의 성능 예측 범위 밖 |
| Physical ECC/lockstep 진단율, real-time WCET, thermal/power 및 DDR calibration | 현재 AP QVP 모델의 검증 범위 밖 |
| Saturn 실물과 전체 register/feature parity | board 정보, IP revision 및 추가 Hardware/FVP evidence 없이는 미확정 |

## 14. TRM 참조 범위

| 문서 | 판본 / 실제 참조 부분 | 적용 범위 |
| --- | --- | --- |
| [Zena CSS Software Developer Guide][zena-front] | `110125_0001_01_en`, r0p1; §1, §5, §9 | 선택된 Hardware 구성, memory/interrupt map |
| [Cortex-A720AE TRM][a720-trm] | `102828_0001_03_en`, r0p1; §1.1, Table 6-1/7-1/8-1 | CPU architecture와 L1/L2 구성; QEMU MIDR r0p0와 구분 |
| [DSU-120AE TRM][dsu-trm] | `107721_0001_05_en`, r0p1; overview, Hybrid-mode, L3 | DSU 구조·Cache·DCLS 의미 |
| [GIC-720AE TRM][gic-trm] | `102666/0201`, r2p1, Issue 0201-12; components/features, WAKER/PWRR | GIC 기능과 software interface; local 수집본의 일부 하위 본문은 불완전 |
| [CMN S3(AE) TRM][cmn-trm] | `107858/0205`, r2p5; System component selection | RN/HN/SLC/SBSX 역할; Zena의 실제 mesh 값은 Zena guide 사용 |
| [MMU-720AE TRM][mmu-trm] | `109745/r0p1`; TCU MSI interface signals | MSI signal contract; 전체 MMU TRM register compliance audit는 미수행 |
| [Arm ARM, Counter resolution/increment][counter-resolution] | DDI0487/MC, I2.2.1 및 CNTP register 설명 | Timer/Counter의 architectural 의미 |

CMN/MMU의 위 online 절은 Arm 공식 문서의 indexed 본문을 확인했다.
전체 TRM 모든 절을 확보하여 대조한 것은 아니다. SRAM macro와 DDR
controller/PHY의 Saturn-specific TRM·실장 configuration도 확인되지 않았으므로
해당 부분의 비교는 Zena address contract와 현재 memory model로 한정한다.

[zena-highlights]: ../arm_zena_css_dev_guide/01-zena-css-product-highlights.md
[zena-blocks]: ../arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md
[zena-map]: ../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md
[arm-components]: ../../arm-zena-css/documentation/design/components.rst
[entry]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua
[soc-config]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/config.lua
[vp-execution]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/execution.lua
[vp-models]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua
[vp-options]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options.lua
[full-profile]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua
[composition]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/composition.lua
[soc]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/apollo.lua
[board]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua
[ap-assembly]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/ap_compute.lua
[ap-cpu]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua
[ap-memory]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua
[ap-interconnect]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua
[ap-system]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua
[ap-pcie]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/pcie.lua
[full-runner]: ../../scripts/run/run_qbox_apollo_fvp_full.py
[yocto-launcher]: ../../run_qbox_yocto.sh
[zena-front]: ../arm_zena_css_dev_guide/00-front-matter.md
[a720-trm]: https://documentation-service.arm.com/static/6835f2073f2acc596c2d96be
[a720-wrapper]: ../../hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_a720ae/include/cortex-a720ae.h
[qemu-cpu64]: ../../hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c
[dsu-trm]: ../dsu-120ae/0001-Arm-DynamIQ-Shared-Unit-120AE-Technical-Reference-Manual.md
[dsu-overview]: ../dsu-120ae/0002-The-DynamIQ-Shared-Unit-120AE.md
[dsu-hybrid]: ../dsu-120ae/0011-Hybrid-mode-Mixed-configuration-with-cores-split-and-DSU-logic-locked.md
[dsu-l3]: ../dsu-120ae/0102-L3-cache.md
[si-power]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua
[gic-trm]: ../gic-720ae/0001-Arm-CoreLink-GIC-720AE-Generic-Interrupt-Controller-Technical-Reference-Manual.md
[gic-components]: ../gic-720ae/0004-Components-in-GIC-720AE.md
[gic-features]: ../gic-720ae/0017-Features.md
[gic-view]: ../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h
[gic-wrapper]: ../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h
[gic-qemu]: ../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3.c
[gic-cpuif]: ../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_cpuif.c
[gic-its]: ../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_its.c
[gic-ras]: ../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gic720ae_ras.h
[gic-waker]: ../gic-720ae/0127-GICR_WAKER-Power-Management-Control-Register.md
[gic-pwrr]: ../gic-720ae/0131-GICR_PWRR-Power-Register.md
[si-safety]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua
[gic-messreg]: ../../hsoc-stack/tools/qbox-platform/systemc-components/gic720ae_messreg/include/gic720ae_messreg.h
[mmio-wrapper]: ../../hsoc-stack/tools/qbox/qemu-components/timer/qemu_arm_arch_timer_mmio/include/qemu_arm_arch_timer_mmio.h
[mmio-qemu]: ../../hsoc-stack/tools/qemu/hw/timer/arm_arch_timer_mmio.c
[timer-patch]: ../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-a/files/fvp-rd-aspen/0029-fix-rdaspen-Use-the-correct-timer-frame.patch
[cntp-ctl]: ../arm_architecture_reference_manual/5366-D24.10.22-CNTP_CTL_EL0-Counter-timer-Physical-Timer-Control-Register.md
[cntp-cval]: ../arm_architecture_reference_manual/5367-D24.10.23-CNTP_CVAL_EL0-Counter-timer-Physical-Timer-CompareValue-Register.md
[smd-system]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/system.lua
[counter-source]: ../../hsoc-stack/tools/qbox-platform/systemc-components/arm_system_counter/src/arm_system_counter.cc
[host-gtimer]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/src/host_gtimer.cc
[counter-mirror]: ../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_arm_counter_mirror/src/qemu_arm_counter_mirror.cc
[qemu-helper]: ../../hsoc-stack/tools/qemu/target/arm/helper.c
[counter-resolution]: ../arm_architecture_reference_manual/7168-I2.2.1-Control-of-counter-resolution-and-increment.md
[ap-boot]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/boot.lua
[gs-memory]: ../../hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h
[cmn-trm]: https://support.arm.com/documentation/107858/0205/About-CMN-S3-AE-/Configurable-options/System-component-selection
[si-interconnect]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/interconnect.lua
[cmn-model]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h
[router]: ../../hsoc-stack/tools/qbox/systemc-components/router/include/router.h
[mmu-trm]: https://support.arm.com/documentation/109745/r0p1/Signal-descriptions/TCU-signals/TCU-Message-Signaled-Interrupt-interface-signals
[smmu-dt-patch]: ../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-a/files/fvp-rd-aspen/0040-feat-rdaspen-add-SMMU-node-to-device-tree.patch
[smmuv3]: ../../hsoc-stack/tools/qbox/systemc-components/smmuv3/include/smmuv3.h
[vp-pcie]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/pcie.lua
[smmu-qemu-wrapper]: ../../hsoc-stack/tools/qbox-platform/qemu-components/arm_smmuv3/include/arm-smmuv3.h
[soc-tests]: ../../tests/test_apollo_soc_layout.py
[gic-tests]: ../../scripts/build/run_qemu_gic720ae_qtests.sh
[timer-tests]: ../../hsoc-stack/tools/qbox-platform/tests/components/host_gtimer/host_gtimer-tests.cc
[timer-wake-test]: ../../hsoc-stack/tools/qbox-platform/tests/platforms/apollo-fourcpu-timer-wake-test.cc
[cmn-tests]: ../../hsoc-stack/tools/qbox-platform/tests/components/host_cmn_cyprus/host_cmn_cyprus-tests.cc
[smmu-tests]: ../../hsoc-stack/tools/qbox/tests/components/smmuv3/smmuv3-tests.cc

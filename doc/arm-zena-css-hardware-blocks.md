# Arm Zena CSS Hardware Blocks

Generated: 2026-05-17

## 범위

이 문서는 현재 checkout의 Arm Zena CSS/RD-Aspen FVP를 기준으로
hardware block을 정리한다. 공개 Arm 제품 페이지의 Zena CSS 설명은 제품
레벨의 방향성을 보여 주지만, 실제로 이 workspace에서 빌드/검증할 수 있는
대상은 `arm-zena-css` 저장소와 현재 kas 설정의 RD-Aspen FVP 모델이다.

현재 생성된 kas 설정은 `MACHINE = "fvp-rd-aspen"`,
`RD_ASPEN_VARIANT = "cfg2"`, baremetal architecture, demo use case를 선택한다
(`.config.yaml:15`, `.config.yaml:16`, `.config.yaml:20`,
`.config.yaml:26`, `.config.yaml:29`). 따라서 아래 표는 CFG2 기준으로
작성했다.

## 요약

Arm Zena CSS는 Primary Compute, System Management Block, Safety Island,
RSE, System Management Domain, 그리고 safety/diagnostics hardware로 나눠
보는 것이 가장 명확하다. Arm 공식 개요는 RD-Aspen이라는 이름이 Arm Zena
CSS의 historical name이라고 설명하고, platform CPU IP를 Primary Compute
`Cortex-A720AE`, Safety Island `Cortex-R82AE`, RSE `Cortex-M55`로
정리한다 (`arm-zena-css/documentation/overview.rst:28`,
`arm-zena-css/documentation/overview.rst:137`,
`arm-zena-css/documentation/overview.rst:138`,
`arm-zena-css/documentation/overview.rst:139`).

제품 레벨 공개 자료는 Zena CSS를 Cortex-A 계열 application processors,
Cortex-R 기반 Safety Island, security enclave, system IP가 결합된
pre-integrated compute subsystem으로 설명한다. 단, 이 문서는 제품 페이지의
선택형 IP를 모두 구현 대상으로 간주하지 않고, repository-local RD-Aspen/FVP
증거를 우선한다.

## 블록 관계

```text
Primary Compute
  Cortex-A720AE clusters + DSU-120AE + AP GIC-720AE
  Linux / Xen / TF-A / OP-TEE / U-Boot / systemd-boot
        | SCMI, PSCI, FF-A, secure services, device tree
        v
System Management Block
  RSE: Cortex-M55 Root of Trust, TF-M, secure boot, ATU windows
  SMD: shared peripherals, SRAM, interconnect, MHUv3, ATU
  Safety Island CL0: Cortex-R82AE lock-step pair, SCP-firmware
  Safety Island CL1: Cortex-R82AE 4-core SMP, Zephyr on CFG2
        | MHUv3 + shared SRAM / RPMsg
        v
Safety and diagnostics
  FMU, SSU, SBISTC, SMCF, RAS FFH, PFDI, GIC multiple views
```

## 주요 Hardware Block

| Block | Hardware/IP | 주요 역할 | Software/firmware owner | 근거 |
| --- | --- | --- | --- | --- |
| Primary Compute | Four processor clusters, each with four Cortex-A720AE cores and DSU-120AE | Linux/Xen 같은 rich OS 실행, AP secure/non-secure firmware 실행 | TF-A, OP-TEE, U-Boot, systemd-boot, Linux/Xen | `arm-zena-css/documentation/design/components.rst:202`, `arm-zena-css/documentation/design/components.rst:203`, `arm-zena-css/documentation/design/components.rst:204` |
| Current PC CPU default | `PC_CLUSTER_COUNT_MAX = 4`, `PC_CPUS_PER_CLUSTER_MAX = 4`, current default `PC_CPUS_COUNT_DEFAULT = 4` | 모델은 최대 4x4 구조를 표현하지만 현재 generated config는 기본 4 CPUs를 선택 | kas/BitBake machine config | `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:19`, `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:20`, `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:22`, `.config.yaml:17`, `.config.yaml:24` |
| DSU-120AE | Up to 32 MiB L3 cache, snoop filtering, bus protection, DCLS, PPUs | Core coherency, cluster-level safety/power support | Hardware controlled through platform firmware and OS power paths | `arm-zena-css/documentation/design/components.rst:206`, `arm-zena-css/documentation/design/components.rst:207`, `arm-zena-css/documentation/design/components.rst:208` |
| AP Interrupt Block | GIC-720AE adjacent to Primary Compute | AP interrupt controller | TF-A/Linux/Xen | `arm-zena-css/documentation/design/components.rst:211` |
| RSE | Cortex-M55 based Runtime Security Engine | Root of Trust, secure boot, pre-SCP initialization, secure services | Trusted Firmware-M | `arm-zena-css/documentation/design/components.rst:40`, `arm-zena-css/documentation/design/components.rst:41`, `arm-zena-css/documentation/overview.rst:113`, `arm-zena-css/documentation/overview.rst:114` |
| RSE ATU windows | Non-secure and secure data access windows at `0x6000_0000..0x7fff_ffff` | RSE local access into system address space | TF-M / RSE platform code | `arm-zena-css/documentation/design/components.rst:55`, `arm-zena-css/documentation/design/components.rst:65`, `arm-zena-css/documentation/design/components.rst:67`, `arm-zena-css/documentation/design/components.rst:68`, `arm-zena-css/documentation/design/components.rst:70` |
| Safety Island block | Cortex-R82AE clusters | Real-time/safety domain, system-management execution domain | SCP-firmware on CL0; Zephyr on CL1 in CFG2 | `arm-zena-css/documentation/design/components.rst:75`, `arm-zena-css/documentation/design/components.rst:76`, `arm-zena-css/documentation/design/components.rst:77`, `arm-zena-css/documentation/overview.rst:116`, `arm-zena-css/documentation/overview.rst:118` |
| Safety Island CFG2 topology | CL0 dual lock-step pair, CL1 four SMP cores | CL0 runs system control; CL1 enables extra RTOS workload and HIPC/PFDI demos | SCP-firmware and Zephyr | `arm-zena-css/documentation/design/components.rst:79`, `arm-zena-css/documentation/design/components.rst:80`, `arm-zena-css/documentation/design/components.rst:81`, `arm-zena-css/documentation/design/components.rst:82`, `arm-zena-css/documentation/design/components.rst:148`, `arm-zena-css/documentation/design/components.rst:150` |
| Safety Island GIC | GIC-720AE with multiple views | Mixed-criticality interrupt isolation between SI CL0 and CL1 | SCP-firmware configures views; SI OS instances consume them | `arm-zena-css/documentation/design/components.rst:84`, `arm-zena-css/documentation/design/components.rst:113`, `arm-zena-css/documentation/design/components.rst:117`, `arm-zena-css/documentation/design/components.rst:119`, `arm-zena-css/documentation/design/components.rst:122` |
| System Management Domain | Shared peripherals, SRAM, interconnect | Connects AP, RSE, and SI blocks | RSE/SCP/TF-A platform firmware | `arm-zena-css/documentation/design/components.rst:156`, `arm-zena-css/documentation/design/components.rst:159`, `arm-zena-css/documentation/design/components.rst:160` |
| MHUv3 communication | Doorbell transport plus shared memory | RSE, TF-A, and SCP-firmware SCMI communication; AP-SI HIPC signaling | TF-M, TF-A, SCP-firmware, Linux remoteproc/RPMsg, Zephyr OpenAMP | `arm-zena-css/documentation/design/components.rst:165`, `arm-zena-css/documentation/design/components.rst:166`, `arm-zena-css/documentation/design/components.rst:170`, `arm-zena-css/documentation/design/hipc.rst:17`, `arm-zena-css/documentation/design/hipc.rst:20` |
| Address spaces and ATUs | AP, SMD, RSE, Safety Island address regions; ATUs in RSE, SI, SMD | Region-local access to 52-bit system-wide address space | RSE owns ATU configuration | `arm-zena-css/documentation/design/components.rst:366`, `arm-zena-css/documentation/design/components.rst:370`, `arm-zena-css/documentation/design/components.rst:371`, `arm-zena-css/documentation/design/components.rst:375`, `arm-zena-css/documentation/design/components.rst:397` |
| Device tree hardware description | `HW_CONFIG` in TF-A FIP | Static description of CPUs, memory, and devices for U-Boot/Linux | TF-A produces; U-Boot/Linux consume | `arm-zena-css/documentation/design/components.rst:218`, `arm-zena-css/documentation/design/components.rst:219`, `arm-zena-css/documentation/design/components.rst:220`, `arm-zena-css/documentation/design/components.rst:240` |

## Safety, Diagnostics, And Monitoring Blocks

| Block | Hardware/IP | 역할 | Evidence |
| --- | --- | --- | --- |
| FMU | System FMUs, GIC FMU, MHU FMU, NI-710AE FMU | Internal/upstream fault aggregation, critical/non-critical signaling, firmware-visible fault records | `arm-zena-css/documentation/design/fmu.rst:17`, `arm-zena-css/documentation/design/fmu.rst:19`, `arm-zena-css/documentation/design/fmu.rst:26`, `arm-zena-css/documentation/design/fmu.rst:36`, `arm-zena-css/documentation/design/fmu.rst:210`, `arm-zena-css/documentation/design/fmu.rst:245` |
| SSU | Safety Status Unit in Safety Island | Root FMU의 `CR_ERR`/`NCR_ERR`를 외부 safety management 상태로 변환 | `arm-zena-css/documentation/design/ssu.rst:17`, `arm-zena-css/documentation/design/ssu.rst:18`, `arm-zena-css/documentation/design/ssu.rst:19`, `arm-zena-css/documentation/design/ssu.rst:35`, `arm-zena-css/documentation/design/ssu.rst:37` |
| SBISTC | Software Built-In Self-Test Controller | STL, hardware, processor 사이의 interface; watchdog과 memory-mapped registers로 core fault/lockup 감지 | `arm-zena-css/documentation/design/sbistc.rst:17`, `arm-zena-css/documentation/design/sbistc.rst:18`, `arm-zena-css/documentation/design/sbistc.rst:21`, `arm-zena-css/documentation/design/sbistc.rst:35`, `arm-zena-css/documentation/design/sbistc.rst:78`, `arm-zena-css/documentation/design/sbistc.rst:80` |
| SMCF | MGI/MLI monitor framework | Sensors, activity counters, system data sampling; SMD Expansion MGI + per-AP-cluster DSU MGIs in RD-Aspen FVP | `arm-zena-css/documentation/design/smcf.rst:16`, `arm-zena-css/documentation/design/smcf.rst:27`, `arm-zena-css/documentation/design/smcf.rst:28`, `arm-zena-css/documentation/design/smcf.rst:46`, `arm-zena-css/documentation/design/smcf.rst:49`, `arm-zena-css/documentation/design/smcf.rst:59` |
| RAS FFH | Cortex-A720AE RAS error records, FHI/ERI paths | Primary Compute CPU RAS, CPER generation, Linux/rasdaemon logging, SI-side uncorrected error handling | `arm-zena-css/documentation/design/ras.rst:49`, `arm-zena-css/documentation/design/ras.rst:55`, `arm-zena-css/documentation/design/ras.rst:107`, `arm-zena-css/documentation/design/ras.rst:112`, `arm-zena-css/documentation/design/ras.rst:131`, `arm-zena-css/documentation/design/ras.rst:139`, `arm-zena-css/documentation/design/ras.rst:185` |
| PFDI | Platform Fault Detection Interface | Firmware test libraries를 등록해 hardware fault detection/reporting 수행 | `arm-zena-css/documentation/overview.rst:224`, `arm-zena-css/documentation/overview.rst:227`, `arm-zena-css/documentation/overview.rst:229`, `arm-zena-css/documentation/overview.rst:232`, `arm-zena-css/documentation/releasenotes.rst:34`, `arm-zena-css/documentation/releasenotes.rst:35` |
| Power/performance control | PPU, SCMI power/performance protocols, DVFS path | CPU/cluster idle state, per-DSU-cluster performance domain, frequency/voltage scaling | `arm-zena-css/documentation/design/power_and_performance_control.rst:30`, `arm-zena-css/documentation/design/power_and_performance_control.rst:47`, `arm-zena-css/documentation/design/power_and_performance_control.rst:49`, `arm-zena-css/documentation/design/power_and_performance_control.rst:75`, `arm-zena-css/documentation/design/power_and_performance_control.rst:76`, `arm-zena-css/documentation/design/power_and_performance_control.rst:129` |

## HIPC And Safety Island CL1 Details

CFG2에서 Zephyr는 Safety Island Cluster 1에 배치되고, HIPC는 Primary
Compute와 SI CL1 사이에 구현된다 (`arm-zena-css/documentation/design/hipc.rst:23`,
`arm-zena-css/documentation/design/hipc.rst:26`,
`arm-zena-css/documentation/design/hipc.rst:27`). 통신은 Linux
remoteproc/RPMsg와 Zephyr OpenAMP/RPMsg를 맞물리게 하며, MHUv3는
signaling, shared SRAM은 data exchange를 담당한다
(`arm-zena-css/documentation/design/hipc.rst:50`,
`arm-zena-css/documentation/design/hipc.rst:57`,
`arm-zena-css/documentation/design/hipc.rst:87`,
`arm-zena-css/documentation/design/hipc.rst:89`).

공유 메모리는 512 KiB로 설명되며 resource table, Vring 0, Vring 1,
RPMsg Virtio Buffer로 나뉜다
(`arm-zena-css/documentation/design/hipc.rst:87`,
`arm-zena-css/documentation/design/hipc.rst:89`,
`arm-zena-css/documentation/design/hipc.rst:90`,
`arm-zena-css/documentation/design/hipc.rst:91`). Zephyr board DTS는
CL1에 4개 CPU node, GICv3, PL011 UART, SRAM, MHUv3 TX/RX mailbox,
SCMI shared memory, PFDI agent를 둔다
(`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:18`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:30`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:48`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:87`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:100`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:109`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:145`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:154`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts:164`).

## FVP-visible Blocks In This Workspace

The current machine configuration uses the Cfg2 FVP executable
`FVP_Zena_CSS_Cfg2` and adds a Safety Island CL1 console
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc:15`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc:17`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc:18`).

FVP launch parameters map RSE ROM/flash, AP flash, the root disk, Virtio
networking, Virtio RNG, DRAM, and console UARTs
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:27`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:35`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:39`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:42`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:43`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:44`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:48`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:49`).
The same file enables the GIC multiple-views feature and adds a PCIe AHCI
device for a specific GICv4.1 vLPI test path
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:56`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:57`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:58`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:86`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:88`).

The BSP runtime test device list currently covers `rtc`, `watchdog`,
`networking`, `virtiorng`, and `cpu_hotplug`
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:117`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:119`).

## 제품 자료와 RD-Aspen Checkout 차이

Arm product/news material describes Zena CSS as a pre-integrated automotive
compute subsystem with Cortex-A application processors, a Cortex-R Safety
Island, a security/root-of-trust block, coherency/system IP, and optional
accelerator/ISP/GPU integration. This is useful for understanding product
positioning, but the actionable implementation evidence in this workspace is
the RD-Aspen/FVP stack above.

For repo work, use the local evidence first:

- Platform and hardware overview:
  `arm-zena-css/documentation/overview.rst`
- Hardware/software block design:
  `arm-zena-css/documentation/design/components.rst`
- Safety diagnostics:
  `arm-zena-css/documentation/design/fmu.rst`,
  `arm-zena-css/documentation/design/ssu.rst`,
  `arm-zena-css/documentation/design/sbistc.rst`,
  `arm-zena-css/documentation/design/smcf.rst`,
  `arm-zena-css/documentation/design/ras.rst`,
  `arm-zena-css/documentation/design/platform_fault_detection_interface.rst`
- Communication:
  `arm-zena-css/documentation/design/hipc.rst`
- FVP/model knobs:
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf`,
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc`,
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc`

## Official References Checked

- Arm Zena CSS v2.2 overview:
  <https://arm-zena-css.docs.arm.com/en/v2.2/overview.html>
- Arm Zena CSS v2.2 components:
  <https://arm-zena-css.docs.arm.com/en/v2.2/design/components.html>
- Arm Zena CSS product page:
  <https://www.arm.com/products/autonomous-machines/zena-compute-subsystems>
- Arm Zena CSS launch/news page:
  <https://newsroom.arm.com/news/arm-unveils-zena-css>

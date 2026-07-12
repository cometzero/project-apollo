# Arm Zena CSS FVP와 Apollo QVP 하드웨어 비교

작성 기준일: 2026-07-11

이 문서는 Arm Zena CSS RD-Aspen CFG2 FVP와 현재 Apollo QVP(QBox)의
하드웨어 구성을 비교한다. 각 subsystem의 IP, 메모리 맵, IRQ, QBox Lua
인스턴스, 실제 SystemC/QEMU 모듈과 구현 수준을 함께 추적한다.

## 비교 기준과 범례

### 소스 기준

| 구분 | 기준 |
| --- | --- |
| FVP 하드웨어 계약 | `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`, `09-programmers-model-for-zena-css.md`, `arm-zena-css/documentation/design/components.rst` |
| FVP 소프트웨어 관찰점 | TF-A/Linux/Zephyr DTS, RD-Aspen machine/FVP 설정 |
| QBox 구성 | `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`와 `hw-block/*.lua` |
| QBox 구현 | `hsoc-stack/tools/qbox-platform/systemc-components/`, `qemu-components/`, `hsoc-stack/tools/qbox/` |
| 분석 revision | arm-zena-css `bf34d9e71f67`, qbox-platform `29a4fbc21e76`, qbox `5b44f50ff3d8`, qemu `ca30c1782ea0` |

FVP 표의 주소는 Zena CSS programmer's model의 architectural address다.
QBox 표는 활성 full-system Lua가 생성하는 주소를 우선한다. Direct AP
(`apollo-pc.lua`)와 isolated SI CL1(`apollo-si-cl1.lua`)은 별도
실행 경로이므로 full-system 구현 상태에 합산하지 않는다.

### 구현 상태

| 상태 | 의미 |
| --- | --- |
| **동작 모델** | CPU 실행, 저장소, interrupt delivery 또는 peripheral 동작을 실제 SystemC/QEMU 모델이 수행한다. |
| **부분 모델** | 부팅에 필요한 기능이나 register subset은 동작하지만 전체 safety, coherency, access-control 또는 오류 의미는 구현하지 않는다. |
| **서비스 모델** | 실제 IP 동작 일부를 SCMI, reset, PFDI, RPMsg 같은 상위 서비스 hook으로 재현한다. |
| **placeholder/stub** | 주소 decode나 저장 공간만 제공한다. IP side effect, IRQ, reset 동작은 없다. |
| **미구현** | 활성 Apollo QVP Lua에 대응 인스턴스가 없다. |
| **해당 없음** | FVP 편의 장치이거나 비교 대상 실리콘 IP가 아니어서 동일 IP 대응이 필요하지 않다. |

### 구성값을 해석할 때의 주의점

| 항목 | FVP/Zena CSS | 활성 Yocto QVP | QBox full-system |
| --- | --- | --- | --- |
| AP 최대 토폴로지 | 4 cluster x 4 Cortex-A720AE = 16 cores | `PC_CPUS_COUNT_DEFAULT = "4"` | `QBOX_APOLLO_NUM_CPUS` 기본 16, 1..16 선택 |
| SI 구성 | CFG2: CL0 DCLS cluster + CL1 4-core SMP | CFG2 | CL0/CL1 live mode 선택 가능 |
| 비교 원칙 | 하드웨어 최대치와 FVP 모델 계약 | 이미지가 실제 활성화한 값 | Lua/runtime이 생성한 값 |

따라서 “Apollo는 4코어”와 “Apollo는 16코어”는 서로 다른 관찰점을
가리킨다. 최종 런타임 비교에서는 사용한 DTB와 `result.json`의 CPU 수를
함께 기록해야 한다.

## 전체 구성 요약

| Subsystem | FVP 주요 하드웨어 | Apollo QVP 주요 모듈 | 종합 상태 |
| --- | --- | --- | --- |
| Primary Compute | Cortex-A720AE, DSU-120AE, GIC-720AE, MMU-720AE, generic timer | `cpu_arm_cortexA720AE`, `arm_gicv3`, `arm_gicv3_its`, `mmu720ae`/`arm_smmuv3`, `qemu_arm_arch_timer_mmio` | CPU/IRQ/timer 동작, DSU/safety/SMMU는 부분 |
| Safety Island CL0 | Cortex-R82AE DCLS, GIC view, SSU/FMU, timer, PPU, NoC GPV | `cpu_arm_cortexR82`, `arm_gicv3`, `gicx00_multiview`, `zena_ssu`, `zena_fmu`, `host_gtimer`, `host_ppu` | 부팅 경로 동작, DCLS와 interconnect 의미는 부분 |
| Safety Island CL1 | Cortex-R82AE 4-core SMP, GIC view2, PL011, MHUv3 | `cpu_arm_cortexR82` x4, `arm_gicv3`, `Pl011`, `mhu320ae` | Zephyr 실행 경로 동작, shared GIC view 의미는 부분 |
| RSE | Cortex-M55 DCLS, TCM/VM, DMA-350, KMU/LCM/SAM, ATU, CC3XX, MHUv3 | `ApolloRseCPU`, `dma350`, `rse_kmu`, `rse_lcm`, `rse_sam`, `rse_atu`, `cc3xx`/`qemu_cc3xx`, `mhu320ae` | 보안 부팅 subset 동작, DCLS/OTP/TRAM/timer는 gap |
| CSS/System Management | NI-710AE 52-bit map, RGM, ATU, REFCLK, PPU, shared SRAM | `router`, `addrtr`, `rse_atu`, `host_gtimer`, `host_ppu`, `gs_memory` | routing/service subset, APU/RGM/PIK는 부분 또는 placeholder |
| Interconnect/I/O | CMN S3(AE), NI-710AE, MMU-720AE, PCIe | `host_cmn_cyprus`, `host_ni710ae_nci`, `mmu720ae`, `qemu_gpex` | discovery/decode 중심, full coherency/APU는 미구현 |

## Primary Compute

### FVP 메모리 맵 요약

| 범위 | FVP 하드웨어 |
| --- | --- |
| `0x0000_0000-0x07ff_ffff` | 128 MiB shared SRAM |
| `0x1000_0000-0x13ff_ffff` | System NoC0-3 NI-710AE GPV |
| `0x1a40_0000-0x1a4a_ffff` | NS/S UART, NS/S watchdog, System ID |
| `0x1a81_0000-0x1a83_ffff` | AP REFCLK generic timer control, secure/non-secure frames |
| `0x1d00_0000-0x1def_ffff` | AP FMU region |
| `0x2000_0000-0x27ff_ffff` | GIC-720AE architectural window |
| `0x3000_0000-0x3fff_ffff` | AP expansion, FVP VirtIO/RTC |
| `0x8000_0000-0xfeff_ffff` | low DRAM |
| `0x1_0000_0000-0x1_3fff_ffff` | CMN S3(AE) GPV |
| `0x1_4000_0000-0x1_7fff_ffff` | cluster management/utility regions |
| `0x1_c000_0000-0x2_1fff_ffff` | MMU-720AE, NI-710AE GPV, PCIe control/PHY |
| `0x200_0000_0000-...` | high DRAM |

근거: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:75-164`.

### IP별 비교

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| Cortex-A720AE cores | 최대 16 cores, timer PPI 10/11/12/13/14 | `ap_cpu_0..N` | `cpu_arm_cortexA720AE` | 부분 모델 | CPU/EL2/EL3/PSCI 경로는 동작한다. PPI 12 wiring과 CPU safety 기능은 별도 확인이 필요하다. | `components.rst:198-211`; `ap_compute.lua:508-550` |
| DSU-120AE | cluster당 4 cores, 최대 32 MiB L3 | 전용 인스턴스 없음 | QEMU ARMCPU/host memory path | 부분 모델 | cache coherency, snoop filter, DCLS, DSU PPU를 별도 DSU 모델로 재현하지 않는다. | `components.rst:202-209` |
| GIC-720AE distributor/redistributor | GICD `0x2080_0000`, GICR `0x2088_0000`부터 16 frames | `ap_gic` | `arm_gicv3` | 부분 모델 | GICv4.1/DirectLPI 설정과 IRQ 전달은 동작한다. GIC-720AE safety/multichip 의미는 제한적이다. | `ap_compute.lua:243-268,480-505` |
| GIC ITS | `0x2084_0000/0x40000` | `ap_gic_its` | `arm_gicv3_its` | 동작 모델 | ITS/MSI parent를 QEMU 모델로 제공한다. | `ap_compute.lua:270-281` |
| AP REFCLK MMIO generic timer | control `0x1a81_0000`, S `0x1a82_0000` SPI 48, NS `0x1a83_0000` SPI 49 | `ap_timer_mem` | `qemu_arm_arch_timer_mmio` | 동작 모델 | 125 MHz, 2 frames로 FVP topology를 직접 모델링한다. | `ap_compute.lua:347-368` |
| CPU internal generic timers | per-core PPI | `ap_cpu_N` signal sockets | QEMU ARMCPU timers | 동작 모델 | platform MMIO timer와 분리되어 있다. PPI 12는 명시적 Lua binding이 보이지 않는다. | `ap_compute.lua:515-525` |
| MMU-720AE TCU/TBU | `0x1_c000_0000/0x0800_0000`, combined SPI 65 | `ap_smmu_0` | `mmu720ae` 또는 `arm_smmuv3` | 부분 모델 | backend 선택형이다. Full TBU parity, RAS와 모든 queue/table-walk 의미는 구현 수준이 다르다. | `config.lua:586-613` |
| AP NS UART | `0x1a40_0000`, SPI 52 | `ap_primary_uart` | `Pl011` | 동작 모델 | file backend를 통해 interactive UART를 제공한다. | `ap_compute.lua:312-345` |
| AP secure UART | `0x1a41_0000`, SPI 53 | `ap_secure_uart` | `Pl011` | 동작 모델 | FVP secure console 주소와 IRQ를 보존한다. | `ap_compute.lua:303-333` |
| AP NS SBSA watchdog | control `0x1a42_0000`, refresh `0x1a43_0000`, SPI 50 | `ap_watchdog_0` | `sbsa_gwdt` | 동작 모델 | QEMU-backed watchdog이다. | `ap_compute.lua:285-301` |
| AP secure watchdog | control `0x1a46_0000`, refresh `0x1a47_0000` | `ap_secure_wdog`, `ap_secure_wdog_refresh` | `gs_memory` | placeholder/stub | decode만 보존한다. watchdog IRQ/reset side effect가 없다. | `ap_compute.lua:370-394` |
| System ID | `0x1a4a_0000` | `ap_sid` | `host_scr` | 부분 모델 | ID와 component registers subset을 제공한다. | `ap_compute.lua:396-416` |
| RGIC2LGIC message registers | `0x5fff_0000` | `ap_rgic2lgic_messreg` | `gic720ae_messreg` | 부분 모델 | 과거 memory placeholder가 아니라 현재 named register model이다. | `ap_compute.lua:418-427` |
| AP cluster FMUs | `0x1d00_0000-0x1d3f_ffff` | `ap_cl0..3_ni710ae_fmu` | `zena_fmu` | 부분 모델 | 각 1 MiB aperture 중 active 0x50000 register banks만 모델링한다. | `ap_compute.lua:429-478` |
| Shared SRAM/DRAM | shared SRAM, low/high DRAM windows | `host_ap_shared_sram`, `host_ap_dram1/2` | `gs_memory` | 동작 모델 | storage와 DMI는 동작한다. memory controller/PHY timing은 모델링하지 않는다. | `ap_compute.lua:65-79,198-241` |
| AP flash | platform flash window | `host_ap_flash` | `strata_flash_j3` | 부분 모델 | CFI/J3 command subset과 backing file을 제공한다. | `ap_compute.lua:142-164` |
| PCIe root complex | ECAM/MMIO/CTRL/PHY regions | `ap_gpex_0` | `qemu_gpex` | 부분 모델 | QEMU generic PCIe host bridge다. Zena CSS PCIe PHY/controller register fidelity는 없다. | `ap_compute.lua:35-63` |
| CMN S3(AE) | `0x1_0000_0000/1 GiB` GPV | `si_cl0_cmn_cyprus` | `host_cmn_cyprus` | 부분 모델 | discovery/register compatibility 중심이다. CHI coherency mesh 전체 모델은 아니다. | `si_cl0.lua:208-220` |
| NI-710AE | System NoC GPV와 I/O NCI | `si_cl0_ni710ae_*_nci` | `host_ni710ae_nci` | 부분 모델 | GPV/register discovery를 제공한다. full NoC/APU enforcement는 없다. | `si_cl0.lua:394-429` |

## Safety Island CL0

### FVP 메모리 맵 요약

| 범위 | FVP 하드웨어 |
| --- | --- |
| `0x1_1000_0000`, `0x1_1010_0000` | CL0 ITCM/DTCM, 각 32 KiB populated |
| `0x1_2000_0000-0x1_207f_ffff` | CL0 LLRAM 8 MiB |
| `0x2800_0000-0x281f_ffff` | CL0 Utility Bus |
| `0x2a00_0000-0x2a31_ffff` | primary/secondary/MHU interconnect GPVs |
| `0x2a40_0000` | CL0 UART |
| `0x2a50_0000-0x2a55_ffff` | SSU와 FMU0-4 |
| `0x2a60_0000-0x2a72_ffff` | PIK, SCR, timer, watchdog |
| `0x3000_0000-0x307f_ffff` | SI GIC-720AE programming views |
| `0x3810_0000-0x3815_ffff` | CL0-RSE MHU sender/receiver |

근거: `09-programmers-model-for-zena-css.md:1018-1308`.

### IP별 비교

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| Cortex-R82AE DCLS CL0 | LLRAM `0x1_2000_0000`, timer PPIs | `si_cl0_cpu_0` | `cpu_arm_cortexR82` | 부분 모델 | 한 CPU 실행 경로로 SCP-firmware를 부팅한다. DCLS pair/compare/fault injection은 없다. | `si_cl0.lua:775-823` |
| CL0 SRAM | `0x1_2000_0000/8 MiB` | `si_cl0_sram`, `host_si_cl0_sram` | `gs_memory` | 동작 모델 | local/host view 저장소를 제공한다. | `si_cl0.lua:3-18,279-288` |
| SI GIC view0/1 | `0x3000_0000` 계열 | `si_gic_multiview`, `si_cl0_gic` | `gicx00_multiview`, `arm_gicv3` | 부분 모델 | view register와 CL0 interrupt delivery를 결합한다. 하나의 완전한 shared GIC-720AE 모델은 아니다. | `si_cl0.lua:222-277,735-752` |
| CL0 UART | `0x2a40_0000`, SPI 8/INTID 40 | `si_cl0_uart` | `Pl011` | 동작 모델 | file UART backend에 연결한다. | `si_cl0.lua:754-773` |
| CL0 timer/counter | `0x2a6f_0000`, `0x2a72_0000`, timer SPI 2 | `si_cl0_timer_cntctl`, `si_cl0_timer_cntbase` | `host_gtimer` | 부분 모델 | counter/control frame subset을 제공한다. | `si_cl0.lua:341-364` |
| CL0 watchdog | `0x2a70_0000`, `0x2a71_0000`, SPI 5 | 대응 인스턴스 없음 | - | 미구현 | watchdog refresh/IRQ/reset을 QBox full-system이 직접 모델링하지 않는다. | `09-programmers-model-for-zena-css.md:1227-1230` |
| Safety Status Unit | `0x2a50_0000/4 KiB` | `si_cl0_ssu` | `zena_ssu` | 부분 모델 | FMU signal 수집과 상태 subset을 제공한다. | `si_cl0.lua:366-392` |
| Safety Island FMU | `0x2a51_0000-0x2a55_ffff` | `si_cl0_fmu` | `zena_fmu` | 부분 모델 | root FMU 경로 중심이며 모든 FMU instance/fault semantics를 복제하지 않는다. | `si_cl0.lua:378-392` |
| NI-710AE GPVs | `0x2a00_0000`, `0x2a20_0000`, `0x2a30_0000` | `si_cl0_ni710ae_primary/secondary/mhu_nci` | `host_ni710ae_nci` | 부분 모델 | register discovery만 제공한다. | `si_cl0.lua:394-429` |
| PPU/PIK | Utility/CSS/SI PPU windows | `host_si_cl0_clus_ppu`, `host_si_cl0_core0_ppu`, `si_cl0_*_ppu` | `host_ppu` | 부분 모델 | power policy와 reset/load handoff를 모델링한다. 모든 PPU policy/interrupt는 아니다. | `si_cl0.lua:31-59,623-733` |
| PLL/SCR/System ID | ATW/SMD mapped windows | `si_cl0_pll`, `si_cl0_scr`, `si_cl0_system_id` | `host_system_pll`, `host_scr` | 부분 모델 | boot에 필요한 lock/ID/register subset이다. | `si_cl0.lua:321-339,444-454,601-621` |
| CMN/SMCF monitoring | mapped GPV/MGI windows | `si_cl0_cmn_cyprus`, `si_cl0_smcf_*` | `host_cmn_cyprus`, `host_smcf_mgi` | 부분 모델 | monitor/discovery register 수준이다. | `si_cl0.lua:208-220,505-563` |
| ATW/control apertures | 여러 `0xc...`, `0xd...`, `0xe...` windows | `si_cl0_atu_check_*`, `si_cl0_smd_expansion_window` 등 | `gs_memory` | placeholder/stub | 접근 가능성과 decode를 보존하지만 register side effect는 없다. | `si_cl0.lua:165-182,290-304,431-442,565-599` |
| CL0-RSE/AP MHUv3 | `0x3810_0000` 계열과 SPP MHU windows | `host_rse_si_mhu_*`, `host_ap_si_*mhu_*` | `mhu320ae` | 서비스 모델 | doorbell/register subset과 SCMI power/reset 서비스를 함께 제공한다. | `system_mgmt.lua:82-127,166-263` |

## Safety Island CL1

### FVP 메모리 맵 요약

| 범위 | FVP 하드웨어 |
| --- | --- |
| `0x1_4000_0000/8 MiB` | CL1 LLRAM/Zephyr SRAM |
| `0x3020_0000` | GIC view2 distributor |
| `0x3026_0000-0x302d_ffff` | 4 redistributor frames |
| `0x2a41_0000` | CL1 PL011 UART |
| `0x3900_0000/0x30000` | CL1-to-AP MHU sender |
| `0x3904_0000/0x30000` | AP-to-CL1 MHU receiver |
| `0x3920_0000/0x20000` | CL1-to-CL0/PFDI MHU |
| `0x4800_0000/4 KiB` | SCMI shared memory |

CL1은 CFG2 전용이다. 근거:
`arm-zena-css/documentation/design/components.rst:79-84,145-154`와
FVP SI CL1 Zephyr DTS.

### IP별 비교

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| Cortex-R82AE 4-core SMP | MPID `0x10000..0x10300`, timer PPIs 3/4/11/13 | `si_cl1_cpu_0..3` | `cpu_arm_cortexR82` | 동작 모델 | 4 CPU와 per-core timer IRQ를 QEMU ARMCPU로 실행한다. cluster safety 기능은 부분이다. | `si_cl1.lua:266-310` |
| CL1 LLRAM | `0x1_4000_0000/8 MiB` | `si_cl1_sram`, `host_si_cl1_sram` | `gs_memory` | 동작 모델 | Zephyr image와 host view를 제공한다. | `si_cl1.lua:3-18,135-145` |
| GIC-720AE view2 | GICD `0x3020_0000`, GICR `0x3026_0000+` | `si_cl1_gic` | `arm_gicv3` | 부분 모델 | CL1 interrupt delivery는 동작한다. shared view ownership은 CL0 multiview 모델과 분리되어 있다. | `si_cl1.lua:158-170,294-310` |
| CL1 UART | `0x2a41_0000`, SPI 7 | `si_cl1_uart` | `Pl011` | 동작 모델 | file backend console이다. | `si_cl1.lua:172-192` |
| CL1-AP HIPC MHU | TX `0x3900_0000` SPI 40, RX `0x3904_0000` SPI 41 | `si_cl1_hipc_mhu_pbx/mbx` | `mhu320ae` | 부분 모델 | doorbell/HIPC path를 제공한다. | `si_cl1.lua:194-231` |
| CL1 PFDI MHU | `0x3920_0000`, SPI 50 | `si_cl1_pfdi_mhu_pbx` | `mhu320ae` | 서비스 모델 | SCMI/PFDI channel behavior를 포함한다. | `si_cl1.lua:233-257` |
| SCMI shared SRAM | `0x4800_0000/4 KiB` | `si_cl1_scmi_shmem` | `gs_memory` | 동작 모델 | MHU transport의 shared memory다. | `si_cl1.lua:147-156` |
| CL1 PPU | SI host CUB/PPU windows | `host_si_cl1_clus_ppu`, `si_cl1_core*_ppu` | `host_ppu` | 부분 모델 | reset/load ordering을 지원한다. | `si_cl1.lua:20-44`; `si_cl0.lua:637-664` |

## RSE

### FVP 메모리 맵 요약

| 범위 | FVP 하드웨어 |
| --- | --- |
| `0x1000_0000-0x10ff_ffff` | secure ITCM architectural window |
| `0x3000_0000-0x30ff_ffff` | secure DTCM architectural window |
| `0x3100_0000-0x33ff_ffff` | volatile SRAM banks |
| `0x4000_0000-0x4fff_ffff` | non-secure peripheral aliases |
| `0x5000_0000-0x5027_ffff` | secure peripherals, KMU/LCM/SAM/ATU/MHU |
| `0x5800_0000-0x5804_1fff` | timers와 watchdog |
| `0x6000_0000-0x6fff_ffff` | ATU non-secure host window |
| `0x7000_0000-0x7fff_ffff` | ATU secure host window |

근거: `09-programmers-model-for-zena-css.md:487-710`.

### IP별 비교

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| Cortex-M55 DCLS RSE | 32-bit RSE map/NVIC | `rse_cpu_pass.cpu_0` | `ApolloRseCPU` | 부분 모델 | CPU/NVIC/remote bridge로 TF-M을 실행한다. DCLS pair/compare는 모델링하지 않는다. | `rse.lua:573-643,691-760` |
| RSE ROM/ITCM/DTCM/VM | `0x1000_0000`, `0x3000_0000`, `0x3100_0000+` | `rse_rom`, `rse_itcm`, `rse_dtcm`, `rse_vm0/1` | `gs_memory` | 동작 모델 | 실제 populated memory를 저장소로 제공한다. | `rse.lua:22-143` |
| Boot flash | QBox `0xb000_0000/64 MiB` | `rse_boot_flash` | `strata_flash_j3` | 부분 모델 | FVP image 저장을 CFI/J3 subset으로 제공한다. | `rse.lua:145-167` |
| DMA-350 | S `0x5000_2000`, NS alias, IRQ 24-26 | `rse_dma350` | `dma350` | 부분 모델 | initiator DMA subset이 동작한다. | `rse.lua:237-250` |
| KMU | `0x5009_e000`, IRQ 20 | `rse_kmu_regs` | `rse_kmu` | 부분 모델 | key slot/export와 crypto 연결 subset이다. | `rse.lua:262-278,669-685` |
| SAM | `0x5009_f000`, IRQ 32/33 | `rse_sam_regs` | `rse_sam` | 부분 모델 | alarm/status register subset이다. | `rse.lua:300-311` |
| LCM | `0x500a_0000` | `rse_lcm_regs` | `rse_lcm` | 부분 모델 | lifecycle/OTP writeback subset이다. | `rse.lua:280-298` |
| ATU | `0x5015_0000`; S/NS windows `0x7000_0000`/`0x6000_0000` | `rse_atu_regs` | `rse_atu` | 부분 모델 | address translation과 host initiator path를 제공한다. 전체 APU/security policy는 아니다. | `rse.lua:339-368` |
| CC3XX CryptoCell | `0x5015_4000/8 KiB` | `rse_cc3xx` | `cc3xx` 또는 `qemu_cc3xx` | 부분 모델 | SystemC 또는 native QEMU backend를 선택한다. secure boot에 필요한 crypto subset 중심이다. | `config.lua:380-404`; `rse.lua:393-395,687-689` |
| Protection controls | SACFG/NSACFG/MPC/SIC windows | `rse_*_regs` | `rse_protection_ctrl` | 부분 모델 | register/protection subset이다. | `rse.lua:227-235,252-260,313-337,370-391` |
| System counters | `0x5015_a000`, `0x5015_b000` | `rse_syscntr_cntrl_regs`, `rse_syscntr_read_regs` | `host_gtimer` | 부분 모델 | control/read frame subset이다. | `rse.lua:397-417` |
| Integrity checker | `0x5015_c000` | `rse_integrity_checker_regs` | `rse_integrity_checker` | 부분 모델 | expected register/response subset을 제공한다. | `rse.lua:419-430` |
| MHUv3 | `0x5016_0000-0x5027_ffff`, NVIC 40-57 | `rse_mhu0/2_*_s` | `mhu320ae` | 부분 모델 | selected RSE/AP/SI channels를 제공한다. MHU1/3-8 전체가 독립 model instance로 존재하지 않는다. | `rse.lua:443-517` |
| RSE system control | `0x5802_1000` | `rse_sysctrl` | `rse_sysctrl` | 부분 모델 | boot/reset register subset이다. | `rse.lua:519-533` |
| OTP wrapper | QBox `0x5811_1000` | `rse_otp_wrapper` | `gs_memory` | placeholder/stub | OTP image storage만 제공한다. | `rse.lua:169-180` |
| CPU security/power/identity regs | `0x5001_1000`, `0x5001_2000`, `0x5001_f000` | `rse_cpu0_*_regs` | `gs_memory` | placeholder/stub | register side effect가 없다. | `rse.lua:182-225` |
| TRAM/integration registers | `0x5015_d000`, `0x5810_0000` | `rse_tram`, `rse_integ_layer_regs` | `gs_memory` | placeholder/stub | address window만 제공한다. | `rse.lua:432-441,535-544` |
| RSE secure timers/watchdog | `0x5800_0000-0x5800_3fff`, `0x5804_0000/0x5804_1000` | 대응 인스턴스 없음 | - | 미구현 | active RSE Lua에 dedicated timer/watchdog module이 없다. | `09-programmers-model-for-zena-css.md:700-706` |

## CSS/System Management

### FVP 52-bit 메모리 맵 요약

| 범위 | FVP 하드웨어 |
| --- | --- |
| `0x00_0000_0000_0000...` | AP physical view |
| `0x01_0000_0000_0000...` | AP TCU view |
| `0x02_0000_6000_0000/1 MiB` | SMD shared SRAM |
| `0x02_0000_d000_0000/128 MiB` | CSS Control |
| `0x03_0000_0000_0000...` | RSE view |
| `0x04_0000_0000_0000...` | Safety Island view |

NI-710AE APU는 기본적으로 RSE 외 접근을 차단한다. 근거:
`09-programmers-model-for-zena-css.md:247-303`.

### IP별 비교

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| SMD 52-bit routing | AP/RSE/SI top-nibble views | `host_router`, `ap_view_router`, 여러 `addrtr` | `router`, `addrtr` | 부분 모델 | address decode와 alias를 제공한다. NI-710AE APU default-deny 전체 정책은 없다. | `fabric.lua`; `ap_compute.lua:555-654` |
| SMD shared SRAM | `0x02_0000_6000_0000/1 MiB` | `host_smcf_sram` | `gs_memory` | 부분 모델 | QBox가 같은 base에서 제공하는 storage는 8 KiB(`0x2000`)뿐이다. 나머지 1016 KiB와 다른 subsystem view의 alias coherence는 구현 근거가 없다. | `config.lua:530-531`; `system_mgmt.lua:410-419` |
| Reset Generation Manager | `0x02_0000_d001_0000` | 전용 RGM 인스턴스 없음 | `reset_gpio`, `host_ppu`, MHU reset hooks | 서비스 모델 | reset 결과는 재현하지만 RGM register/syndrome/mask 계약은 미구현이다. | `system_mgmt.lua:208-263`; `ap_compute.lua:20-25` |
| SMD/AP/SI ATUs | `d007_0000-d009_ffff`와 host views | `host_si_atu`, `host_ap_atu`, `host_smdexp2smd_atu` | `rse_atu` | 부분 모델 | address translation subset이다. APU/filter/error-record 전체는 없다. | `system_mgmt.lua:66-80,141-164,350-364` |
| REFCLK counter/control/sync | `d010_0000-d012_ffff` | `host_css_counters_timers*` | `host_gtimer` | 부분 모델 | control/read/sync frame을 나눠 제공한다. | `system_mgmt.lua:377-408` |
| SYSTOP Power Integration | `d020_0000` | `host_systop_pik`, SI/AP PPU instances | `gs_memory`, `host_ppu` | placeholder/stub / 부분 모델 | SYSTOP PIK register window는 memory placeholder다. 필요한 power/reset 결과만 PPU/service hook로 분산해 재현한다. | `system_mgmt.lua:366-375`; `si_cl0.lua:623-733` |
| DBGTOP Power Integration | `d021_0000` | 대응 인스턴스 없음 | - | 미구현 | DBGTOP register window와 독립 power-policy/IRQ 동작을 활성 QVP Lua가 제공하지 않는다. | `09-programmers-model-for-zena-css.md:298` |
| SMD UART | `d030_0000`, AP/RSE/SI IRQ views | 대응 인스턴스 없음 | - | 미구현 | AP/SI/RSE 개별 UART는 있으나 SMD UART architectural window는 없다. | `09-programmers-model-for-zena-css.md:300` |
| SMD GPIO | `d031_0000` | 대응 인스턴스 없음 | - | 미구현 | GPIO register/IRQ가 없다. | `09-programmers-model-for-zena-css.md:301` |
| SMD System ID | `d040_0000` | 직접 대응 없음 | - | 미구현 | AP/SI local `host_scr`과 동일 주소 공간이 아니다. | `09-programmers-model-for-zena-css.md:303` |
| Cross-domain MHUv3 | AP/RSE/SI MHU windows | `host_*_mhu_pbx/mbx` | `mhu320ae` | 서비스 모델 | register/doorbell과 SCMI, reset, PFDI, RPMsg helper를 함께 제공한다. | `system_mgmt.lua:82-348,421-503` |

## Interconnect 및 주변장치

| FVP IP/하드웨어 | FVP 주소/IRQ | QBox Lua 인스턴스 | QBox 구현 모듈 | 구현 상태 | 비교/차이 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| CMN S3(AE) mesh | `0x1_0000_0000/1 GiB`, fault/PMU SPIs | `si_cl0_cmn_cyprus` | `host_cmn_cyprus` | 부분 모델 | programmer view와 boot discovery 중심이다. CHI timing/coherency fabric은 host router가 대체한다. | `si_cl0.lua:208-220` |
| NI-710AE System/I/O NoC | GPV/NCI windows, AP/SI consolidated IRQs | `si_cl0_ni710ae_*_nci` | `host_ni710ae_nci` | 부분 모델 | NCI register subset이다. routing은 QBox `router`가 수행한다. | `si_cl0.lua:394-429` |
| MMU-720AE | `0x1_c000_0000/128 MiB` | `ap_smmu_0` | `mmu720ae` 또는 `arm_smmuv3` | 부분 모델 | backend별 capability와 table-walk/fault fidelity가 다르다. | `config.lua:586-613` |
| PCIe ECAM/MMIO | FVP ECAM0-4와 MMIOH windows | `ap_gpex_0` | `qemu_gpex` | 부분 모델 | generic QEMU GPEX이며 Zena CSS controller/PHY programming model은 없다. | `ap_compute.lua:35-63` |
| AP VirtIO block | `0x3002_0000-0x3005_ffff`, SPI 257-260 | `ap_virtioblk_0..3` | `virtio_mmio_blk` | 동작 모델 | FVP/QVP 편의 장치이며 실리콘 IP 대응은 해당 없음이다. | `ros.lua:4-70` |
| AP VirtIO network | `0x3006_0000`, SPI 261 | `ap_virtionet_0` | `virtio_mmio_net` | 동작 모델 | FVP/QVP synthetic device다. | `ros.lua:72-87` |
| AP VirtIO RNG | `0x3008_0000`, SPI 263 | `ap_virtiorng_0` | `virtio_mmio_rng` | 동작 모델 | FVP/QVP synthetic device다. | `ros.lua:89-103` |
| PL031 RTC | `0x300d_0000`, SPI 268 | `ap_rtc_0` | `pl031` | 동작 모델 | QEMU PL031을 사용한다. | `ros.lua:105-115` |
| FVP RoS system/P9/VSI/UART slots | `0x3000_0000`, `0x3001_0000`, `0x3009_0000+` | `ros.peripherals` metadata only | 없음 | 미구현 | Lua가 `modeled=false`로 명시한다. | `ros.lua:119-148` |

## Fidelity gap

### 우선순위가 높은 차이

1. **CPU 토폴로지 관찰점**
   - Zena CSS 최대 16 cores, 활성 Yocto QVP 기본 4, QBox runtime 기본 16을
     구분해야 한다.
2. **DSU/DCLS와 safety semantics**
   - AP DSU-120AE, SI CL0/RSE DCLS compare와 fault injection은 dedicated
     model이 없다.
3. **AP timer PPI 12**
   - FVP/Linux DTS는 PPI 12를 포함하지만 `ap_compute.lua`에는 명시적
     PPI 12 signal binding이 보이지 않는다.
4. **SMMU fidelity**
   - 두 backend 모두 boot-critical subset은 제공한다. MMU-720AE TBU,
     RAS, queue, translation fault와 table walk는 backend별 재검증이 필요하다.
5. **Interconnect fidelity**
   - `host_cmn_cyprus`와 `host_ni710ae_nci`는 register/discovery
     compatibility model이다. full coherent NoC와 APU access control model은
     아니다.
6. **MHUv3 service hooks**
   - `mhu320ae`는 hardware doorbell 외에 SCMI reset/power, PFDI, RPMsg
     helper를 포함한다. 이를 register-faithful hardware model과 구분해야 한다.
7. **Memory-backed register windows**
   - AP secure watchdog, RSE OTP/TRAM/CPU control, SYSTOP PIK와 여러
     ATW/control aperture는 `gs_memory` placeholder/stub다.
8. **명시적 미구현 IP**
   - SI CL0 watchdog, RSE timers/watchdog, SMD UART/GPIO/System ID,
     DBGTOP Power Integration, 일부 RoS peripheral은 활성 QVP에 대응
     모델이 없다.
9. **SMD shared SRAM coverage**
   - FVP 계약은 1 MiB지만 QBox `host_smcf_sram`은 8 KiB만 제공한다.
     나머지 1016 KiB와 AP/RSE/SI alias 간 동일 backing/coherence는
     검증되지 않았다.

### 런타임에서 다시 확인할 항목

- 사용한 DTB의 AP CPU 수, GIC redistributor 수와 disabled/enabled device
  node 상태.
- 선택된 SMMU와 CC3XX backend.
- IRQ trigger/polarity와 signal source/sink.
- MHU channel별 hardware doorbell과 service-modeled side effect.
- placeholder window 접근이 부팅 성공을 위해 필요한지 여부.
- FVP/QBox 양쪽 로그에서 firmware, driver probe, fault path가 같은지 여부.

## 결론

Apollo QVP는 RSE, SI CL0, SI CL1과 Primary Compute를 하나의 QBox
full-system으로 구성하며 CPU 실행, GIC, UART, DRAM/SRAM, AP timer,
watchdog, VirtIO, 일부 security/safety IP를 실제 SystemC/QEMU 모델로
제공한다.

그러나 “주소가 존재한다”는 사실은 “IP가 구현됐다”는 뜻이 아니다.
특히 interconnect, access control, DCLS, SMMU safety, RGM, PPU policy,
watchdog과 RSE 보안 register 일부는 부분 모델, 서비스 모델 또는
placeholder/stub다. FVP 동등성은 boot pass뿐 아니라 memory map, IRQ,
device tree, 오류 동작과 negative test를 함께 확인해야 한다.

## 근거 파일

- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `arm-zena-css/documentation/design/components.rst`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf`
- `build/conf/local.conf`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua`
- `hsoc-stack/tools/qbox-platform/systemc-components/`
- `hsoc-stack/tools/qbox-platform/qemu-components/`

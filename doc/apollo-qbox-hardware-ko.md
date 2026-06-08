# Apollo QBox 하드웨어 에뮬레이션 분석

작성일: 2026-06-08

이 문서는 `doc/apollo-fvp-hardware-analysis-ko.md`의 Apollo FVP 하드웨어
분석을 기준으로, 현재 QBox/QEMU가 각 하드웨어 IP를 어떤 모듈로
에뮬레이션하는지 정리한다. 초점은 주소 맵 자체보다 `FVP IP block -> QBox
Lua instance -> QBox/SystemC/QEMU module -> backend source`의 대응 관계이다.

## 분석 기준

주요 근거는 다음 파일이다.

| 구분 | 파일 |
| --- | --- |
| FVP 하드웨어 기준 | `doc/apollo-fvp-hardware-analysis-ko.md` |
| Apollo QBox direct boot | `tools/qbox/platforms/apollo-fvp/conf.lua`, `tools/qbox/platforms/apollo-fvp/apollo-fvp-primary-compute.dts` |
| Apollo QBox full-system wrapper | `tools/qbox/platforms/apollo-fvp/full.lua` |
| SI CL1 isolated boot | `tools/qbox/platforms/apollo-fvp/si-cl1.lua` |
| RSE-first base topology | `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua` |
| QBox SystemC modules | `tools/qbox/systemc-components/` |
| QBox QEMU modules | `tools/qbox/qemu-components/` |
| QEMU backend source | `tools/qemu/` |
| Full-system 설계/맵 | `doc/qbox-apollo-fvp-full-system-design.md`, `doc/qbox-apollo-fvp-map-analysis.md` |

## 실행 경로

현재 Apollo QBox에는 세 가지 실행 경로가 있다. 각 경로는 목적과 fidelity
수준이 다르므로 문서와 검증에서 분리해서 봐야 한다.

| 경로 | Lua entry | 목적 | 하드웨어 범위 |
| --- | --- | --- | --- |
| Primary Compute direct boot | `tools/qbox/platforms/apollo-fvp/conf.lua` | Linux kernel/initramfs를 직접 부팅하는 빠른 AP 검증 | AP CPU 4개, AP GIC/ITS, UART, watchdog, RTC, virtio, reserved memory |
| SI CL1 isolated | `tools/qbox/platforms/apollo-fvp/si-cl1.lua` | Zephyr CL1 단독 부팅과 UART/MHU/PFDI bring-up | CL1 Cortex-R82 4개, CL1 GIC, UART, HIPC/PFDI MHU, SRAM |
| Full-system | `tools/qbox/platforms/apollo-fvp/full.lua` | RSE-first topology 위에 live CL0/CL1/AP를 통합 | RSE TF-M, AP firmware chain, SI CL0 SCP, SI CL1 Zephyr, service/live 혼합 모델 |

`full.lua`는 `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`를 `dofile()`로
가져온 뒤 Apollo-specific AP view router, live SI CL0, live SI CL1 구성을
추가한다. 따라서 현재 full-system의 RSE/AP base model은 RD-Aspen RSE-first
topology를 재사용하고, Apollo wrapper가 Safety Island live 모델과 AP view
분리를 덧씌우는 구조이다.

## 에뮬레이션 레이어

QBox 구현은 한 종류의 backend만 쓰지 않는다. 현재 Apollo FVP 하드웨어는
다음 레이어 조합으로 표현된다.

| 레이어 | 대표 모듈 | 역할 |
| --- | --- | --- |
| Lua platform wiring | `router`, `addrtr`, `loader`, `gs_memory`, `char_backend_file` | 주소 decode, alias, image load, log backend |
| QEMU-backed CPU/IP | `cpu_arm_cortexA720AE`, `cpu_arm_cortexR82`, `arm_gicv3`, `arm_gicv3_its`, `arm_smmuv3`, `virtio_mmio_*`, `pl031`, `sbsa_gwdt` | QEMU/libqemu device model을 SystemC socket으로 노출 |
| SystemC/TLM behavioral model | `rse_atu`, `mhu320ae`, `cc3xx`, `dma350`, `strata_flash_j3`, `rse_lcm`, `host_ppu`, `gicx00_multiview` | FVP-visible register, translation, mailbox, flash, safety/control behavior |
| QEMU-native fast backend | `qemu_cc3xx` | `cc3xx_core`를 QEMU MemoryRegionOps fast path로 실행 |
| Remote CPU bridge | `RemotePass`, `RemoteCPU`, `remote_cpu` | RSE Cortex-M55 실행과 SystemC host platform 연결 |
| Placeholder/memory-backed model | `gs_memory` | 아직 full behavioral model이 없는 register window 보존 |

## Primary Compute Block

### CPU

| FVP IP | QBox instance | Module | Backend/source |
| --- | --- | --- | --- |
| Cortex-A720AE AP cores | direct boot: `cpu_0..cpu_3` | `cpu_arm_cortexA720AE` | `tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_a720ae/`, QEMU CPU type `cortex-a720ae-arm` |
| Cortex-A720AE AP cores | full-system: `ap_cpu_0..ap_cpu_3` | `cpu_arm_cortexA720AE` | same |

Direct boot는 EL3/EL2를 끄고 AArch64 boot stub으로 Linux를 직접 시작한다.
Full-system은 AP BL2 entry로 진입해야 하므로 `has_el3=true`,
`has_el2=true`, `rvbar=HOST_AP_BL2_PHYS_BASE`를 사용한다. AP CPU 수는 현재
QBox 경로에서 4개로 구성되어 있으며, FVP 기준의 16개 AP core 전체를 모두
live CPU로 올리는 단계는 아니다.

### AP 메모리와 boot artifact

| FVP 영역 | QBox instance | Module | 비고 |
| --- | --- | --- | --- |
| Low DRAM `0x80000000` | direct: `ram_0`, full: `host_ap_dram1` | `gs_memory` | local Image/rootfs 또는 AP firmware runtime memory |
| High DRAM | direct: `ram_1`, full: `host_ap_dram2` | `gs_memory` | FVP DT와 맞춘 high memory |
| AP shared SRAM | `host_ap_shared_sram` | `gs_memory` | SDS, SCMI payload, reset syndrome seed |
| AP SCMI shared memory | direct: `sram_0`, full: `host_ap_mhu_ns_shared_sram` | `gs_memory` | `0x00180000` 4 KiB |
| SI CL1 remoteproc carveouts | direct: `si_cl1_rproc_rsctbl_0`, `si_cl1_vdev0vring*_0`, `si_cl1_vdev0buffer_0` | `gs_memory` | AP-visible HIPC reserved memory |
| AP flash/FIP | `host_ap_flash` | `strata_flash_j3` | AP secure flash image, writeback/DMI 옵션 지원 |
| Trusted NV counter | `host_ap_trusted_nvctr` | `gs_memory` | TF-A certificate counter seed |

`loader`는 direct boot에서는 kernel, DTB, initramfs, boot stub을 로드하고,
full-system에서는 AP BL2 reset loader와 RSE/SI image loader가 역할을
분담한다.

### AP Interrupt/I/O

| FVP IP | QBox instance | Module | QEMU backend |
| --- | --- | --- | --- |
| GIC-720AE AP GIC view | direct: `gic_0`, full: `ap_gic` | `arm_gicv3` | `tools/qemu/hw/intc/arm_gicv3*.c` |
| ITS | direct: `its_0`, full: `ap_gic_its` | `arm_gicv3_its` | `tools/qemu/hw/intc/arm_gicv3_its*.c` |
| SMMUv3 | full: `ap_smmu_0` | `arm_smmuv3` | `tools/qemu/hw/arm/smmuv3*.c` |
| PL011 primary UART | direct: `pl011_uart_0`, full: `ap_primary_uart` | `Pl011` with `uart-pl011` dylib | QBox SystemC PL011 wrapper |
| PL011 secure UART | `ap_secure_uart` | `Pl011` | secure console file backend |
| SBSA watchdog | direct: `watchdog_0`, full: `ap_watchdog_0` | `sbsa_gwdt` | `tools/qemu/hw/watchdog/sbsa_gwdt.c` |
| Secure watchdog placeholder | `ap_secure_wdog` | `gs_memory` | secure-world error path access 보존 |
| Memory-mapped timer | full: `ap_timer_mem` | `qemu_hexagon_qtimer` | QEMU-backed timer component |
| RTC | direct: `rtc_0`, full: `ap_rtc_0` | `pl031` | `tools/qemu/hw/rtc/pl031` equivalent wrapper |
| Virtio block | direct: `virtioblk_0..3`, full: `ap_virtioblk_0..3` | `virtio_mmio_blk` | `tools/qemu/hw/block/virtio-blk.c`, `tools/qemu/hw/virtio/virtio-mmio.c` |
| Virtio net | direct: `virtionet0_0`, full: `ap_virtionet_0` | `virtio_mmio_net` | `tools/qemu/hw/net/virtio-net.c` |
| Virtio rng | direct: `virtiorng_0`, full: `ap_virtiorng_0` | `virtio_mmio_rng` | `tools/qemu/hw/virtio/virtio-rng.c` |

Direct boot DTS는 AP 4-core subset만 기술하고, full-system 경로는
RSE-first topology의 AP GIC, SMMU, virtio, UART, watchdog, RTC, AP-SI MHU
구성을 사용한다.

## RSE Block

### RSE CPU와 memory view

| FVP IP | QBox instance | Module | 비고 |
| --- | --- | --- | --- |
| Cortex-M55 RSE core | `rse_cpu_pass.cpu_0` | `RemoteCPU` via `RemotePass` | `tools/qbox/build/remote_cpu`와 별도 QEMU instance 사용 |
| RSE NVIC | nested `cpu.nvic` | QEMU Cortex-M/NVIC path | `RemoteCPU` 설정의 `nvic` block에서 `num_irq=160` |
| RSE ROM | `rse_rom` | `gs_memory` | read-only, `rse-rom-image.img` load |
| ITCM/DTCM aliases | `rse_itcm`, `rse_dtcm`, optional `*_cpu0` | `gs_memory` | secure/non-secure/CPU0 alias 지원 |
| VM0/VM1 | `rse_vm0`, `rse_vm1` | `gs_memory` | VM1은 provisioning bundle load |
| RSE boot flash | `rse_boot_flash` | `strata_flash_j3` | local or remote CPU process 배치 가능 |

RSE CPU 자체는 platform Lua에서 `cpu_arm_cortexM55` instance로 직접 보이지
않고 `RemoteCPU`/`RemotePass` 구조 안에 들어간다. QEMU component로
`cpu_arm_cortexM55`는 존재하지만, Apollo RSE-first topology는 remote CPU
helper를 통해 RSE 실행과 host SystemC model을 연결한다.

### RSE security/peripheral IP

| FVP IP | QBox instance | Module | 모델 수준 |
| --- | --- | --- | --- |
| DMA350 | `rse_dma350` | `dma350` | SystemC DMA model, RSE router initiator 사용 |
| CC3XX | `rse_cc3xx` | `cc3xx` 또는 `qemu_cc3xx` | `QBOX_RDASPEN_CC3XX_BACKEND=systemc/qemu-native` |
| CC3XX core logic | internal | `qbox::cc3xx::core` | SystemC와 QEMU-native backend가 공유 |
| KMU | `rse_kmu_regs` | `rse_kmu` | OTP hardware key load, export write 처리 |
| LCM/OTP | `rse_lcm_regs` | `rse_lcm` | OTP image load/writeback/lock, LCS transition |
| SAM | `rse_sam_regs` | `rse_sam` | touched/status register behavior |
| RSE ATU | `rse_atu_regs` | `rse_atu` | secure/non-secure host window translation |
| Integrity checker | `rse_integrity_checker_regs` | `rse_integrity_checker` | build config/status model |
| System control | `rse_sysctrl` | `rse_sysctrl` | reset syndrome, CPUWAIT, DMA boot registers |
| SACFG/NSACFG/MPC/SIC/TRAM/counters | `rse_*_regs`, `rse_tram` | `gs_memory` | firmware-visible register window 보존 |
| RSE host UART | `rse_host_uart0_s` | `Pl011` | RSE UART file-backed log |

CC3XX는 성능상 중요한 예외이다. 기본은 SystemC `cc3xx`이지만,
`qemu_cc3xx`는 같은 `cc3xx_core`를 QEMU MemoryRegionOps로 직접 호출해
SystemC scheduler bridge 비용을 줄인다. 이는 secure boot 검증을 우회하지
않는 fast backend로 분류된다.

### RSE MHU와 AP/SI handoff

| 통신 경로 | QBox instance | Module | 프로토콜 |
| --- | --- | --- | --- |
| RSE local MHU0 sender/receiver | `rse_mhu0_sender_s`, `rse_mhu0_receiver_s` | `mhu320ae` | doorbell |
| RSE local MHU2 sender/receiver | `rse_mhu2_sender_s`, `rse_mhu2_receiver_s` | `mhu320ae` | doorbell-bridge |
| RSE <-> SI CL0 host MHU | `host_rse_si_mhu_pbx`, `host_rse_si_mhu_mbx` | `mhu320ae` | SCMI, `rse-bl2` transport |
| AP secure <-> RSE MHU | `host_ap_rse_mhu_pbx`, `host_ap_rse_mhu_mbx` | `mhu320ae` | doorbell-bridge |
| AP/RSE mailbox SRAM | `host_ap_rse_mailbox` | `gs_memory` | MHU pointer-access window |

`mhu320ae`는 MHU-320AE/MHUv3-compatible SystemC component다. 현재 설정에서
SCMI service-model, doorbell bridge, RPMsg namespace seed, PFDI monitor
shared-memory 초기화, reset pulse 같은 platform service 기능을 함께 갖는다.

## Safety Island CL0 Block

`full.lua`에서 `QBOX_APOLLO_FULL_SI_MODE=live-cl0-cl1` 또는 live CL0 옵션이
켜지면 SI CL0 block이 추가된다.

### CL0 CPU/GIC/UART

| FVP IP | QBox instance | Module | 비고 |
| --- | --- | --- | --- |
| Cortex-R82AE CL0 | `si_cl0_cpu_0` | `cpu_arm_cortexR82` | 1개 architectural CPU로 CL0 DCLS 대표 |
| SI CL0 GIC view 1 | `si_cl0_gic` | `arm_gicv3` | `0x30100000` distributor, `0x30140000` redistributor |
| GIC multiview control view 0 | `si_gic_multiview` | `gicx00_multiview` | SCP boot-time view0 register surface |
| AP GIC multiview control | `ap_gic_multiview` | `gicx00_multiview` | CL0 ATW AP GIC programming view |
| CL0 UART | `si_cl0_uart` | `Pl011` | `char_backend_file`로 CL0 UART log 저장 |
| CL0 image loader | `si_cl0_loader` | `loader` | `si0_ramfw.bin` load |

`gicx00_multiview`는 full GIC backend가 아니라 firmware-visible multiview
control surface이다. 실제 interrupt delivery는 CL0/CL1/AP 각각의
`arm_gicv3` QEMU backend가 담당한다.

### CL0 system management IP

| FVP IP/Window | QBox instance | Module | 모델 수준 |
| --- | --- | --- | --- |
| CL0 SRAM | `si_cl0_sram` | `gs_memory` | live SCP RAM |
| RSE/SCP shared SRAM | `si_cl0_rse_shared_sram` | `gs_memory` | CL0 local `0x40000000` view |
| SCR/System ID | `si_cl0_scr`, `si_cl0_system_id` | `host_scr` | CL1 present bit, ID/PID/CID reset values |
| Generic timers/counters | `si_cl0_timer_cntctl`, `si_cl0_timer_cntbase`, `si_cl0_refclk_cntcontrol` | `host_gtimer` | counter/control register behavior |
| SSU | `si_cl0_ssu` | `gs_memory` | register window placeholder |
| FMU | `si_cl0_fmu` | `gs_memory` | FMU window placeholder |
| NI-710AE NCI | `si_cl0_ni710ae_primary_nci`, `*_secondary_nci`, `*_mhu_nci` | `host_ni710ae_nci` | topology/build register model |
| CMN S3(AE) ATW0 | `si_cl0_cmn_cyprus` | `host_cmn_cyprus` | CMN GPV touched/status model |
| PLL | `si_cl0_pll` | `host_system_pll` | lock bit behavior |
| SMCF MGI | `si_cl0_smcf_smd_mgi`, `si_cl0_smcf_ap_cluster_mgi_*` | `host_smcf_mgi` | monitor group interface model |
| PPU | `si_cl0_sys0_ppu`, `si_cl1_cluster_ppu`, `si_cl1_core*_ppu`, `si_cl0_ap_cluster*_ppu`, `si_cl0_ap_cluster*_core*_ppu` | `host_ppu` | power-status/polling model |
| ATW check windows | `si_cl0_atu_check_*` | `gs_memory` | firmware access coverage window |
| SMD/AP SRAM windows | `si_cl0_ap_peripheral_*_sram`, `si_cl0_smd_shared_sram`, `si_cl0_smd_exp_mgi_sram` | `gs_memory` | shared data windows |

CL0 live model은 현재 실제 SCP-firmware가 진행하는 polling과 register writes를
통과시키기 위해 필요한 최소 behavior를 SystemC 모델로 추가한 상태이다.
FMU/SSU 같은 safety block은 아직 full fault propagation 모델이라기보다
firmware-visible window를 보존하는 쪽에 가깝다.

## Safety Island CL1 Block

CL1은 full-system과 isolated 경로 모두 4-core live Zephyr 대상으로
구성된다.

| FVP IP | QBox instance | Module | 비고 |
| --- | --- | --- | --- |
| Cortex-R82AE CL1 cores | `si_cl1_cpu_0..3` | `cpu_arm_cortexR82` | 4-core SMP |
| CL1 SRAM | `si_cl1_sram` | `gs_memory` | Zephyr image load/execution |
| CL1 SCMI/PFDI shmem | `si_cl1_scmi_shmem` | `gs_memory` | `0x48000000` |
| CL1 HIPC shared RAM | isolated: `si_cl1_shared_ram`, full: `host_ap_bl2_header_sram` alias | `gs_memory` | resource table/vring/RPMsg buffer |
| CL1 GIC view 2 | `si_cl1_gic` | `arm_gicv3` | GICD `0x30200000`, 4 redistributors |
| CL1 UART | `si_cl1_uart` | `Pl011` | Zephyr console file log |
| CL1 HIPC PBX/MBX | `si_cl1_hipc_mhu_pbx`, `si_cl1_hipc_mhu_mbx` | `mhu320ae` | doorbell 또는 doorbell-bridge |
| CL1 PFDI MHU | `si_cl1_pfdi_mhu_pbx` | `mhu320ae` | SCMI `pfdi-monitor` transport |
| CL1 image loader | `si_cl1_loader` | `loader` | `zephyr-demos-cl1.bin` load |
| CL1 reset fanout | `apollo_si_cl1_reset_fanout` | `reset_fanout` | live CL0가 CL1/AP reset release 연동 |

Isolated 경로는 `router` 하나에 CL1 local view를 붙인다. Full-system 경로는
RSE-first `host_router`를 임시 merged bus로 사용하면서, AP broad window보다
CL1 narrow window가 우선하도록 decode priority를 조정한다.

## Interconnect, ATU, Address View

| FVP block | QBox instance/module | 설명 |
| --- | --- | --- |
| AP logical view | `ap_view_router`, `ap_view_passthrough` / `router`, `addrtr` | AP CPU access를 host_router에서 분리해 AP local address conflict를 줄임 |
| RSE host windows | `rse_atu_regs` / `rse_atu` | RSE secure/non-secure host access window translation |
| SI ATU | `host_si_atu` / `rse_atu` | SI host-side ATU register block 모델 |
| AP-to-SMD ATU | `host_ap_atu` / `rse_atu` | AP logical `0x40000000` window translation |
| SMDExp-to-SMD ATU | `host_smdexp2smd_atu` / `rse_atu` | SMD expansion translation register block |
| CMN S3(AE) | `si_cl0_cmn_cyprus` / `host_cmn_cyprus` | SI CL0 ATW0 CMN GPV 접근 모델 |
| NI-710AE | `host_ni710ae_nci`, `si_cl0_ni710ae_*` | NCI topology/register model |
| Broad unmapped/device windows | `gs_memory` catch-all/fallback | bring-up용 placeholder, fidelity debt로 분류 |

ATU는 full-system에서 boot-critical이다. RSE TF-M, SI CL0 SCP-firmware, AP
Linux/TF-A가 서로 다른 local view를 사용하기 때문이다. 현재 QBox는
`rse_atu`를 여러 instance로 재사용해 RSE/SI/AP/SMD translation register
surface를 표현한다.

## Interrupt Block

| FVP IP | QBox module | 적용 영역 |
| --- | --- | --- |
| AP GICv3/GIC-720AE AP view | `arm_gicv3`, `arm_gicv3_its` | AP Linux/TF-A interrupt delivery |
| SI CL0 GIC view 1 | `arm_gicv3` | SCP-firmware runtime interrupt delivery |
| SI CL1 GIC view 2 | `arm_gicv3` | Zephyr SMP interrupt delivery |
| GIC multiview control surface | `gicx00_multiview` | SCP가 접근하는 view0/multiview registers |
| AP timer PPIs | `cpu_arm_cortexA720AE` timer outputs -> `arm_gicv3.ppi_in_cpu_*` | architectural timer |
| SI timer PPIs | `cpu_arm_cortexR82` timer outputs -> `arm_gicv3.ppi_in_cpu_*` | CL0/CL1 timers |
| MHU SPIs | `mhu320ae.irq` -> `arm_gicv3.spi_in_*` | SCMI/HIPC/PFDI doorbells |

QBox는 현재 GIC-720AE를 하나의 monolithic model로 구현하지 않는다. QEMU
GICv3 backend를 AP, SI CL0, SI CL1에 각각 두고, SystemC
`gicx00_multiview`가 firmware-visible multiview register surface를 제공하는
hybrid 구조를 사용한다.

## I/O Block

| FVP IP | QBox module | Backend/source | 상태 |
| --- | --- | --- | --- |
| SMMUv3 | `arm_smmuv3` | QEMU `arm-smmuv3` | full-system AP path에서 QEMU-backed |
| ITS | `arm_gicv3_its` | QEMU `arm-gicv3-its` | AP GIC와 연결 |
| Virtio block/net/rng | `virtio_mmio_blk`, `virtio_mmio_net`, `virtio_mmio_rng` | QEMU virtio device + virtio-mmio transport | Linux direct/full AP I/O |
| PCIe host placeholder | `qemu_gpex` | QEMU GPEX | SMMU primary bus host, AP full path |
| RTC | `pl031` | QEMU PL031 wrapper | AP Linux RTC |
| Watchdog | `sbsa_gwdt` | QEMU SBSA watchdog wrapper | AP watchdog |
| UART | `Pl011` | QBox SystemC UART PL011 + file/stdio backend | AP/RSE/SI logs |

Direct boot 경로는 Linux bring-up을 빠르게 검증하기 위해 I/O를 AP DTS에 맞춰
구성한다. Full-system 경로는 firmware chain과 SI 통신까지 고려해 AP-SI,
AP-RSE, RSE-SI MHU와 shared memory를 더 많이 포함한다.

## System Management Block

| FVP 기능 | QBox instance/module | 설명 |
| --- | --- | --- |
| RGM/reset release | `reset_gpio`, `reset_fanout`, `host_ppu`, `mhu320ae` reset hooks | AP/CL1 reset pulse와 power domain reset 연결 |
| SMD SRAM | `host_rse_si_ssram`, `host_smcf_sram`, `si_cl0_smd_shared_sram` | SCMI/SMCF/shared payload backing memory |
| SCMI | `mhu320ae` protocol `scmi` | RSE-SI, AP-SI, PFDI monitor service-model transport |
| PFDI monitor | `host_ap_si_pfdi_monitor_mhu_pbx`, `si_cl1_pfdi_mhu_pbx` | AP 16 channels, CL1 4 channels shared-memory SCMI |
| SMCF | `host_smcf_mgi`, `gs_memory` SMCF SRAM | monitor group interface register model |
| FMU/SSU | `gs_memory` windows | register access placeholder; full fault semantics pending |
| Power/clock | `host_ppu`, `host_system_pll`, `host_gtimer` | polling/status-friendly control models |
| SCR/System ID | `host_scr` | CL1 presence, ID/PID/CID values |

System management은 현재 “모든 IP를 full semantic model로 구현”한 상태가
아니라, boot-critical path에 대해 behavioral model과 service-model을 혼합한
상태이다. 문서나 검증에서 이 영역은 `live`, `service-modeled`,
`register-stub`, `memory-placeholder`를 구분해야 한다.

## Peripheral Block

| 도메인 | FVP peripheral | QBox module |
| --- | --- | --- |
| AP | UART, watchdog, RTC, timer, virtio | `Pl011`, `sbsa_gwdt`, `pl031`, `qemu_hexagon_qtimer`, `virtio_mmio_*` |
| RSE | UART, boot flash, DMA350, CC3XX, KMU, LCM, SAM, ATU, MHU | `Pl011`, `strata_flash_j3`, `dma350`, `cc3xx`/`qemu_cc3xx`, `rse_kmu`, `rse_lcm`, `rse_sam`, `rse_atu`, `mhu320ae` |
| SI CL0 | UART, GIC, timers, SCR, NI-710AE, CMN, PPU, SMCF, SSU/FMU | `Pl011`, `arm_gicv3`, `gicx00_multiview`, `host_gtimer`, `host_scr`, `host_ni710ae_nci`, `host_cmn_cyprus`, `host_ppu`, `host_smcf_mgi`, `gs_memory` |
| SI CL1 | UART, GIC, HIPC/PFDI MHU, SCMI shmem, SRAM | `Pl011`, `arm_gicv3`, `mhu320ae`, `gs_memory` |

## 모듈 상태 분류

| 분류 | 모듈 |
| --- | --- |
| QEMU-backed live model | `cpu_arm_cortexA720AE`, `cpu_arm_cortexR82`, `arm_gicv3`, `arm_gicv3_its`, `arm_smmuv3`, `virtio_mmio_blk`, `virtio_mmio_net`, `virtio_mmio_rng`, `pl031`, `sbsa_gwdt`, `qemu_gpex` |
| SystemC behavioral model | `rse_atu`, `mhu320ae`, `cc3xx`, `dma350`, `strata_flash_j3`, `rse_kmu`, `rse_lcm`, `rse_sam`, `rse_sysctrl`, `rse_integrity_checker`, `host_gtimer`, `host_ppu`, `host_scr`, `host_cmn_cyprus`, `host_ni710ae_nci`, `host_smcf_mgi`, `host_system_pll`, `gicx00_multiview` |
| QEMU-native fast path | `qemu_cc3xx` |
| Remote bridge | `RemotePass`, `RemoteCPU`, `remote_cpu` |
| Infrastructure | `router`, `addrtr`, `loader`, `gs_memory`, `char_backend_file`, `char_backend_stdio`, `global_peripheral_initiator`, `reset_fanout`, `reset_gpio`, `keep_alive`, `QemuInstance`, `QemuInstanceManager` |
| Placeholder/fidelity debt | SSU/FMU windows as `gs_memory`, broad fallback windows, selected AP/SI cluster control windows as `gs_memory`, secure watchdog placeholder |

## FVP 대비 주요 차이와 주의점

1. AP는 현재 QBox에서 기본 4-core live 구성이다. FVP 하드웨어 기준은
   4 clusters x 4 cores, 총 16 Cortex-A720AE이다.
2. SI CL0 DCLS는 하나의 `cpu_arm_cortexR82` live CPU로 대표된다. lock-step
   비교 자체는 모델링하지 않는다.
3. GIC-720AE multiview는 QEMU GICv3 backend와 SystemC
   `gicx00_multiview` control surface 조합이다. FVP의 물리 GIC와 1:1
   구조는 아니다.
4. `mhu320ae`는 boot/service integration을 많이 수행한다. 단순 register
   sink로 오해하면 안 되지만, full MHU-320AE architectural model parity는
   아직 남아 있다.
5. `gs_memory`로 처리되는 windows는 firmware access를 막지 않기 위한
   placeholder일 수 있다. fault propagation, access permission, side effect가
   필요한 IP는 추후 full model로 승격해야 한다.
6. `qemu_cc3xx`는 성능 최적화 backend이고 secure boot 검증 bypass가 아니다.
   negative secure boot/FWU/storage fidelity 검증에서는 DMI/fast alias 옵션을
   분리해서 기록해야 한다.

## 구현/검증 시 체크리스트

- Lua platform에서 IP가 어떤 source view에 물려 있는지 먼저 확인한다:
  direct AP `router`, full-system `host_router`, RSE `rse_router`, CL1 isolated
  `router`.
- AP/SI/RSE가 같은 주소를 다르게 보는 경우 `addrtr`, ATU, alias, decode
  priority를 함께 확인한다.
- MHU 문제는 `pair`, `frame`, `protocol`, `irq`, `tx_shmem/rx_shmem`,
  `initiator_socket`까지 함께 봐야 한다.
- GIC 문제는 AP GIC, SI CL0 GIC, SI CL1 GIC, `gicx00_multiview`를 분리해서
  봐야 한다.
- `gs_memory`로 통과 중인 block은 full fidelity가 필요한지 별도 검토한다.
- 문서/리포트에서 각 block 상태를 `QEMU-backed`, `SystemC behavioral`,
  `service-modeled`, `memory-placeholder`, `absent` 중 하나로 표시한다.

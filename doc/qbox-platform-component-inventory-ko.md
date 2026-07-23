# QBox Platform Component Inventory

작성일: 2026-06-30

이 문서는 `tools/qbox-platform/qemu-components/`와
`tools/qbox-platform/systemc-components/`에 있는 Apollo/RD-Aspen overlay
컴포넌트가 어떤 하드웨어 IP 또는 compatibility surface를 모델로 하는지,
그리고 Apollo QBox platform에서 어느 영역에 어떤 목적으로 사용되는지
정리한다.

범위는 `tools/qbox-platform` 소유 컴포넌트다. `tools/qbox` core에서 제공하는
공통 QEMU/SystemC 컴포넌트, 예를 들어 `arm_gicv3`, `arm_gicv3_its`,
`Pl011`, `virtio_mmio_blk`, `virtio_mmio_net`, `pl031`,
`cpu_arm_cortexM55`, `gs_memory`, `loader`, `router`는 이 문서의 주 대상이
아니다.

분석 기준은 소스 정적 분석이다. 주요 근거 파일은 다음이다.

- `tools/qbox-platform/qemu-components/CMakeLists.txt`
- `tools/qbox-platform/systemc-components/CMakeLists.txt`
- `tools/qbox-platform/platforms/apollo/apollo-qvp.lua`
- `tools/qbox-platform/platforms/apollo/hw-block/*.lua`
- 각 컴포넌트의 `include/*.h`, `src/*.cc`, `CMakeLists.txt`

## 전체 요약

| 분류 | 수량 | 성격 |
| --- | ---: | --- |
| `qemu-components` dynamic module | 6 | QEMU device/CPU 또는 QEMU MemoryRegion 기반 wrapper |
| `qemu-components` static library | 1 | Apollo RSE CPU wrapper에 링크되는 semantic acceleration helper |
| `systemc-components` dynamic module | 25 | SystemC/TLM register model, LT functional model, stub, signal fanout |

현재 Apollo full-system QVP의 중요한 선택 지점은 두 가지다.

| 항목 | 기본값 | 대체값 | 설정 |
| --- | --- | --- | --- |
| RSE CC3XX | `cc3xx` SystemC/TLM | `qemu_cc3xx` QEMU-native backend | `QBOX_RDASPEN_CC3XX_BACKEND=systemc|qemu-native` |
| AP SMMU | `mmu720ae` SystemC/TLM | `arm_smmuv3` QEMU device wrapper | `QBOX_RDASPEN_SMMU_BACKEND=systemc-mmu720ae|qemu-arm-smmuv3` |

## QEMU Components

`qemu-components`는 QBox의 `QemuInstance`와 연결되어 QEMU device, QEMU CPU,
QEMU `MemoryRegionOps` 경로를 노출한다. Apollo full-system에서는 주로 AP와
Safety Island live CPU, optional SMMU/CC3XX backend, RoS virtio RNG에 쓰인다.

| Component | 모델 대상 IP/기능 | 구현 형태 | Apollo 사용 영역 | 목적 |
| --- | --- | --- | --- | --- |
| `arm_smmuv3` | Arm SMMUv3 QEMU device | `QemuDevice`, QEMU device type `arm-smmuv3` | AP I/O SMMU optional backend. `ap_smmu_component()`에서 `QBOX_RDASPEN_SMMU_BACKEND=qemu-arm-smmuv3`일 때 사용 | Linux-visible SMMUv3 register/device behavior를 QEMU 구현으로 제공하고, SystemC `mmu720ae`와 비교/fallback 기준으로 사용 |
| `qemu_cc3xx` | RSE CC3XX/CryptoCell register model의 QEMU-native backend | `sc_module` + QEMU `MemoryRegionOps`; 내부 core는 SystemC `cc3xx`와 공유 | RSE local crypto path optional backend. `QBOX_RDASPEN_CC3XX_BACKEND=qemu-native`일 때 `rse_cc3xx_component()`가 선택 | RSE TF-M/BL2 crypto MMIO hot path를 QEMU callback으로 처리해 성능을 개선하면서 CC3XX register/DMA side effect는 공유 core로 유지 |
| `rse_cpu_accel` | RSE TF-M BL2/MCUboot semantic acceleration | static library, `QemuCpuPcEntryObserver` | `platforms/apollo/rse-cpu/ApolloRseCPU`에 링크됨. Lua module로 직접 생성되지는 않음 | RSE Cortex-M55 실행 중 특정 PC entry를 관찰해 BL2 image load, hash, signature, LMS/P-256, delay hot path를 가속 |
| `cpu_arm_cortexA720AE` | Arm Cortex-A720AE AP CPU | `QemuCpuArm`, QEMU CPU type `cortex-a720ae-arm` | `ap_compute.lua`의 AP CPU cluster | Apollo Primary Compute firmware/Linux 실행, EL2/EL3, PSCI, reset vector, timer/PMU/GIC signal 연결 |
| `cpu_arm_cortexR82` | Arm Cortex-R82 Safety Island CPU | `QemuCpuArm`, QEMU CPU type `cortex-r82-arm` | live SI CL0, live SI CL1 | SCP-firmware 또는 Zephyr 실행용 Safety Island CPU backend |
| `sbsa_gwdt` | Arm SBSA Generic Watchdog | `QemuDevice`, QEMU device type `sbsa_gwdt` | AP full-system path | AP firmware/Linux watchdog register window와 watchdog IRQ 제공 |
| `virtio_mmio_rng` | virtio-mmio RNG device | `QemuVirtioMMIO`, QEMU device type `virtio-rng-device` | `ros.lua`의 AP-visible RoS RNG | Linux/guest entropy source 제공 |

### QEMU Component Notes

- `arm_smmuv3`는 `stage` CCI parameter를 QEMU device property로 전달하고,
  optional PCI host가 있으면 `primary-bus`와 `smmu_per_bus`를 설정한다.
- `qemu_cc3xx`는 QEMU object model의 독립 device라기보다 QBox qemu-component다.
  MMIO register access는 QEMU `MemoryRegionOps` callback으로 들어오고, DMA는
  QEMU address space 우선, TLM fallback 경로를 가진다.
- `rse_cpu_accel`은 fidelity model이라기보다 성능/반복시간 개선용 semantic
  accelerator다. 실제 RSE CPU wrapper는
  `tools/qbox-platform/platforms/apollo/rse-cpu/`의 `ApolloRseCPU` shared
  library가 맡는다.

## SystemC Components

`systemc-components`는 대부분 QBox Lua에서 `moduletype`으로 생성되는
SystemC/TLM dynamic module이다. 일부는 실제 IP의 제한된 functional model이고,
일부는 firmware bring-up을 위한 register-compatible stub이다.

| Component | 모델 대상 IP/영역 | 구현 수준 | Apollo 사용 영역 | 목적 |
| --- | --- | --- | --- | --- |
| `cc3xx` | Arm CC3XX/CryptoCell RSE crypto block | SystemC/TLM functional model | RSE local crypto default backend | TF-M BL1/BL2의 RNG, AES, HASH, CMAC, PKA, DMA side effect 처리 |
| `dma350` | Arm DMA-350 | SystemC/TLM LT functional model | RSE local DMA | RSE BL1/BL2의 memory fill/copy DMA sequence를 수행하고 done/error status 제공 |
| `gic720ae_messreg` | GIC-720AE RGIC-to-LGIC message register sideband | Register storage model | AP compute `ap_rgic2lgic_messreg` | AP GIC-720AE 관련 message register window 접근을 받아 Linux/FVP-visible map을 맞춤 |
| `gicx00_multiview` | GICx00/GIC-720AE multi-view register sideband | Register model | live SI CL0의 SI/AP GIC multiview window | GICD `CFGID`, `IVIEWR`, GICR `VIEWR/FLUSHR/PWRR` 등 view programming surface 제공 |
| `host_cmn_cyprus` | Arm CMN Cyprus host discovery/register surface | Topology/discovery register model | live SI CL0 `si_cl0_cmn_cyprus` | CMN HN-S/RN-SAM node discovery와 RNSAM status/config readback 제공 |
| `host_gtimer` | Arm Generic Timer control/count frame | Register/counter model | live SI CL0 timer control/base/refclk windows | SCP-firmware timer discovery 및 counter/frequency readback 제공 |
| `host_ni710ae_nci` | Arm NI-710AE NCI discovery/APU windows | Topology/register model | live SI CL0 primary, secondary, MHU NCI windows | NI-710AE component/APU discovery와 APU control/IIDR access 제공 |
| `host_ppu` | Host-visible PPU-style power policy unit | Register + reset/load signal model | SI cluster/core/system PPU, host SI PIK, CL1 cluster PPU | Power status readback, power-on transition, reset/load signal generation |
| `host_scr` | Host system control/SID/SCR register blocks | Register model | AP SID, SI CL0 SCR/system ID, host SI SCR | System ID, SoC/chip ID, CL configuration, CPUHALT/mem/safety control compatibility |
| `host_smcf_mgi` | SMCF MGI monitor group interface | Register model | live SI CL0 SMCF monitor/group interface | Monitor request/status, mode request/status, data-valid and feature registers 제공 |
| `host_system_pll` | System PLL control/status window | Register model | live SI CL0 PLL | PLL programming write를 받아 lock bit를 set해 firmware polling을 통과 |
| `mhu320ae` | Arm CoreLink MHU-320AE / MHU Architecture v3 doorbell PBX/MBX | SystemC/TLM functional subset | RSE local MHU0/MHU2, AP/RSE, RSE/SI, AP/SI SCMI, AP/SI CL1 HIPC, PFDI monitor, live CL1 | Doorbell frame, IRQ, SCMI shared-memory service, PFDI monitor, AP reset/power SCMI, RPMsg namespace seed, RSE PS proxy path 제공 |
| `mmu720ae` | Arm MMU-720AE / SMMUv3-compatible AP I/O MMU | SystemC/TLM functional subset | AP SMMU default backend | SMMUv3 register/queue/IRQ surface 제공. SMMU enabled 상태의 silent bypass를 막고 translation fault/event를 기록 |
| `ras_ffh_stub` | RAS Firmware First Handling IRQ surface | Stub | 현재 Apollo Lua 직접 사용 없음 | RAS FFH interrupt-only placeholder |
| `reset_fanout` | Reset signal fanout helper | Pure SystemC signal utility | System-management reset distribution | 하나의 reset input을 여러 reset output으로 전달하고 delta/timing ordering을 안정화 |
| `rse_atu` | RSE Address Translation Unit | SystemC/TLM register + address translation model | RSE local ATU, host SI/AP/SMD ATU windows | RSE/host logical address를 physical target으로 변환하고 unmapped/permission/overflow fault를 관찰 가능하게 함 |
| `rse_integrity_checker` | RSE Integrity Checker | Register model | RSE local integrity checker | TF-M integrity-check programming, start/done status, PID/CID readback 제공 |
| `rse_kmu` | RSE Key Management Unit | Register model + OTP key load/export side effect | RSE local KMU | OTP image에서 hardware key slot을 로드하고 KMU status/key export path를 제공 |
| `rse_lcm` | RSE Lifecycle Manager and OTP window | Register + OTP image model | RSE local LCM/OTP | Lifecycle state, TP/SP enable, OTP read/writeback, provisioning 이후 OTP lock behavior 제공 |
| `rse_protection_ctrl` | RSE SACFG/NSACFG/MPC/SIC-style protection controller | Register model | RSE NSACFG, SACFG, VM MPC, SIC, MPC-SIC windows | lock, non-secure write denial, protection status/PID/CID compatibility 제공 |
| `rse_sam` | RSE SAM register block | Register model | RSE local SAM | SAM build config, event/status clear, VM/error response registers 제공 |
| `rse_sysctrl` | RSE System Control | Register model | RSE local SYSCTRL | reset syndrome, CPUWAIT, DMA boot enable/address, secure debug set/clear 등 boot-critical register 제공 |
| `strata_flash_j3` | Intel/Numonyx StrataFlash J3 CFI NOR | SystemC/TLM flash functional model | RSE boot flash and AP boot flash | read-array, read-id/query/status, word program, write-buffer program, block erase, lock, backing file/DMI/writeback 제공 |
| `zena_fmu` | Zena/AE Fault Management Unit | Register + IRQ/status model | AP NI-710AE FMUs, SI CL0 FMU | RAS error records, SYS_KEY unlock, critical/non-critical IRQ and SSU signal generation |
| `zena_ssu` | Zena Safety Status Unit | Register + safety-status signal model | live SI CL0 SSU | critical/non-critical fault input을 safety status로 반영하고 SSU status/control register 제공 |

## Apollo Platform Usage by Domain

| Domain | 주요 컴포넌트 | 목적 |
| --- | --- | --- |
| RSE/System Management | `ApolloRseCPU`, `rse_cpu_accel`, `cc3xx`/`qemu_cc3xx`, `dma350`, `rse_kmu`, `rse_lcm`, `rse_sam`, `rse_sysctrl`, `rse_atu`, `rse_protection_ctrl`, `rse_integrity_checker`, `strata_flash_j3`, `mhu320ae` | TF-M boot, secure provisioning, crypto/DMA, ATU setup, AP/SI handoff, secure-service mailbox |
| AP/Primary Compute | `cpu_arm_cortexA720AE`, `mmu720ae`/`arm_smmuv3`, `sbsa_gwdt`, `strata_flash_j3`, `host_scr`, `gic720ae_messreg`, `zena_fmu` | TF-A/OP-TEE/U-Boot/Linux 실행, AP flash, AP SMMU, watchdog, GIC-720AE sideband, safety/fault surfaces |
| RoS | `virtio_mmio_rng` | AP-visible virtio RNG; block/net/RTC는 QBox core component 사용 |
| Safety Island CL0 | `cpu_arm_cortexR82`, `host_cmn_cyprus`, `gicx00_multiview`, `host_gtimer`, `host_ni710ae_nci`, `host_ppu`, `host_scr`, `host_smcf_mgi`, `host_system_pll`, `zena_fmu`, `zena_ssu` | SCP-firmware live 실행, SI GIC view programming, timer/discovery/safety/control register compatibility |
| Safety Island CL1 | `cpu_arm_cortexR82`, `mhu320ae`, `host_ppu` | Zephyr live 실행, HIPC/RPMsg, PFDI monitor, CL1 cluster power/reset surface |
| Cross-domain messaging | `mhu320ae`, `rse_atu`, `reset_fanout` | AP/RSE/SI SCMI, AP/SI CL1 HIPC, AP logical MHU aliases, reset/power fanout |

## Conditional and Unused Surfaces

| Component | 상태 | 비고 |
| --- | --- | --- |
| `cc3xx` | Apollo 기본값 | `QBOX_RDASPEN_CC3XX_BACKEND`가 없으면 RSE crypto backend로 사용 |
| `qemu_cc3xx` | opt-in | `QBOX_RDASPEN_CC3XX_BACKEND=qemu-native`일 때 사용 |
| `mmu720ae` | Apollo 기본값 | `QBOX_RDASPEN_SMMU_BACKEND`가 없으면 AP SMMU backend로 사용 |
| `arm_smmuv3` | opt-in | `QBOX_RDASPEN_SMMU_BACKEND=qemu-arm-smmuv3`일 때 사용 |
| `ras_ffh_stub` | Apollo Lua 직접 사용 없음 | RAS FFH IRQ placeholder로 빌드됨 |

## Fidelity 관점의 해석

| 수준 | 해당 컴포넌트 예 | 해석 |
| --- | --- | --- |
| QEMU-backed architectural model | `cpu_arm_cortexA720AE`, `cpu_arm_cortexR82`, `arm_smmuv3`, `sbsa_gwdt`, `virtio_mmio_rng` | QEMU가 이미 제공하는 CPU/device 모델을 QBox socket과 CCI parameter로 감싼 형태 |
| SystemC functional model | `strata_flash_j3`, `cc3xx`, `dma350`, `mhu320ae`, `rse_atu`, `mmu720ae` | boot-critical register behavior와 일부 data movement/translation/interrupt side effect를 구현 |
| SystemC register compatibility model | `host_*`, `rse_*`, `gic720ae_messreg`, `gicx00_multiview`, `zena_fmu`, `zena_ssu` | firmware/driver가 접근하는 register subset, ID/discovery/status/clear/lock 동작을 구현 |
| Temporary or compatibility stub | `ras_ffh_stub` | RAS FFH IRQ placeholder. Apollo QVP 주경로의 MHU는 현재 `mhu320ae`가 담당 |

이 표의 목적은 구현 현황을 과장하지 않는 것이다. 예를 들어 `mmu720ae`는
MMU-720AE/SMMUv3 register와 queue/event 일부를 모델링하지만 전체 table walk와
완전한 TBU translation parity는 아직 별도 fidelity 과제다. `mhu320ae`도
MHU-320AE의 doorbell PBX/MBX와 Apollo boot service hook 중심의 functional
subset이며, TRM 전체의 RAS/FMU/FIFO/Fast-channel parity를 의미하지 않는다.

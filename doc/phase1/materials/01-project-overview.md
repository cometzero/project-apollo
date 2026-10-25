# 01. Project Overview — Compute, Control, Trust의 결합

[전체 목차](README.md) · [다음 장: Source Architecture](02-project-source-architecture.md)

Apollo는 Cortex-A720AE의 application 실행, Cortex-R82 기반 Safety Island의 제어·진단, Cortex-M55 RSE의 boot·secure service를 연결한다. QBox는 이 구조를 SystemC/TLM/QEMU로 실행하고 Arm Zena CSS / RD-Aspen reference는 hardware와 software interface의 기준을 제공한다.

## 1. 이 장을 읽는 순서

| 순서 | 상세 문서 | 읽고 나서 설명할 수 있는 것 |
|---|---|---|
| 01.1 | [Hardware 구성과 Domain ownership](01-overview/01-hardware-and-domains.md) | Compute Complex·SMB와 AP/RSE/CL0/CL1의 책임, logical PE와 physical topology |
| 01.2 | [Software stack과 실행 profile](01-overview/02-software-and-profiles.md) | privilege·lifetime, secure service, baremetal/Xen/full-system/standalone 구분 |
| 01.3 | [Address view와 System lifecycle](01-overview/03-address-and-lifecycle.md) | local/global/shared backing, boot→runtime→fault, source→artifact→consumer |

먼저 CPU block과 software 실행 주체를 맞춘다. 다음으로 하나의 shared buffer가 각 CPU에서 어떻게 보이는지 확인한다. 마지막으로 Linux의 요청이 SCP resource operation 또는 RSE secure service로 이어지는 경로를 따라간다. Source 파일은 [02장](02-project-source-architecture.md), 조립 과정은 [03장](03-project-build-architecture.md), 실제 object 연결은 [04장](04-qbox-runtime-and-lua.md)에서 확장한다.

## 2. Domain별로 기억할 책임

| Domain | 실행 software | 대표 책임 | 다른 Domain과의 접점 |
|---|---|---|---|
| AP | TF-A, OP-TEE, U-Boot, Linux | application·OS·AP secure partition | PSCI/SCMI, FF-A/PSA proxy, RPMsg |
| RSE | TF-M boot/runtime | 신뢰 시작, image 인증·적재, secure service | MHU/PSA, SCMI, reload ACK |
| SI CL0 | SCP-firmware | power/reset/performance, fault monitor | SCMI server, PPU, FMU/SSU |
| SI CL1 | Zephyr SMP | 독립 RTOS workload·PFDI | HIPC/RPMsg, core별 report |

SMD는 별도 CPU가 아니라 shared peripheral·SRAM·control의 address domain이다. Firmware domain 수와 QemuInstance 수, Linux VM 수는 서로 다른 값이다. 상세 구성과 현재 population은 01.1에서 확인한다.

## 3. 처음 등장하는 용어의 기준

| 용어 | 이 project에서의 뜻 |
|---|---|
| Zena CSS / RD-Aspen | Arm reference design의 현재/역사적 명칭 |
| QVP / QBox | 구성된 Virtual Platform / 이를 실행하는 co-simulation framework |
| AP / Primary Compute | application processor subsystem |
| SMB / SMD | RSE·SI 등을 포함한 management block / shared system-management address domain |
| RSE / RoT | secure runtime subsystem / 신뢰의 시작점 |
| ATU / APU | address translation / access permission 관련 기능 |
| PPU | power-state programming/control interface |
| GIC / NVIC | A/R-profile / M-profile interrupt controller |
| PBX / MBX | MHU의 송신 / 수신 programming view |
| FIP / UKI / WIC | AP firmware package / kernel·initramfs·DTB 등 UEFI boot bundle / disk image |
| SPMD / SPMC / SP | secure partition dispatcher / manager / partition |
| HIPC / RPMsg | heterogeneous IPC solution / shared-memory messaging protocol |

## 4. 기술 주제별 상세 학습 경로

| 기술 주제 | Arm reference의 설명 | 이 자료의 상세 장 |
|---|---|---|
| Domain/IP/topology | [Components](../../../arm-zena-css/documentation/design/components.rst) | [04](04-qbox-runtime-and-lua.md), [05](05-fvp-qbox-comparison.md) |
| Yocto layer·target | [Integration](../../../arm-zena-css/documentation/design/integration.rst), [Reproduce](../../../arm-zena-css/documentation/user_guide/reproduce.rst) | [02](02-project-source-architecture.md), [03](03-project-build-architecture.md) |
| Image layout·CoT·boot | [Boot process](../../../arm-zena-css/documentation/design/boot_process.rst) | [03](03-project-build-architecture.md), [06](06-component-software-architecture.md) |
| FF-A/PSA/UEFI variable | [Secure services](../../../arm-zena-css/documentation/design/secure_services.rst) | [06](06-component-software-architecture.md) |
| Firmware update/encryption | [Secure FWU](../../../arm-zena-css/documentation/design/secure_firmware_update.rst), [Image encryption](../../../arm-zena-css/documentation/design/rse_image_encryption.rst) | [03](03-project-build-architecture.md), [06](06-component-software-architecture.md) |
| HIPC/RPMsg/network | [HIPC](../../../arm-zena-css/documentation/design/hipc.rst) | [06](06-component-software-architecture.md), [07](07-system-software-core.md) |
| PSCI/SCMI/PPU/DVFS | [Power and performance](../../../arm-zena-css/documentation/design/power_and_performance_control.rst) | [07](07-system-software-core.md) |
| PFDI/FMU/SSU/RAS | [PFDI](../../../arm-zena-css/documentation/design/platform_fault_detection_interface.rst), [FMU](../../../arm-zena-css/documentation/design/fmu.rst), [SSU](../../../arm-zena-css/documentation/design/ssu.rst), [RAS](../../../arm-zena-css/documentation/design/ras.rst) | [07](07-system-software-core.md) |
| Self-test/monitor | [SBISTC](../../../arm-zena-css/documentation/design/sbistc.rst), [TFP](../../../arm-zena-css/documentation/design/tfp.rst), [SMCF](../../../arm-zena-css/documentation/design/smcf.rst), [Safety boot](../../../arm-zena-css/documentation/design/safety_boot.rst) | [07](07-system-software-core.md) |

기준일은 2026-10-25이다. Source/config와 reference를 대조한 문서이며 runtime qualification 결과는 [SOURCES.md](SOURCES.md)에 기록한 별도 evidence 범위를 따른다.

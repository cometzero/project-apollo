# Apollo FVP 하드웨어 분석

작성일: 2026-06-08

이 문서는 `apollo-fvp` 머신을 기준으로 Arm Zena CSS RD-Aspen CFG2
구성을 코드와 문서에서 추적한 하드웨어 분석 결과이다. 목적은 Yocto/FVP
부팅, local build, QBox full-system 모델링, 디버깅에서 공통으로 참조할
수 있는 코어 구성, IP 블록, 메모리 맵, 인터럽트 맵, 도메인 간 통신
경로를 정리하는 것이다.

## 분석 기준

현재 `apollo-fvp`는 RD-Aspen CFG2와 같은 하드웨어 구성을 기반으로 하며,
향후 Apollo 전용 포팅 레이어에서 차이가 생길 수 있다. 따라서 이 문서는
현재 checkout의 Apollo 전용 소스와 RD-Aspen/Zena CSS 공통 문서를 함께
근거로 사용한다.

주요 근거는 다음 파일들이다.

| 영역 | 주요 근거 |
| --- | --- |
| Zena CSS 구조/메모리 맵 | `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`, `doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md`, `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md` |
| RD-Aspen 설계 설명 | `arm-zena-css/documentation/design/components.rst`, `arm-zena-css/documentation/design/hipc.rst`, `arm-zena-css/documentation/design/platform_fault_detection_interface.rst`, `arm-zena-css/documentation/design/fmu.rst`, `arm-zena-css/documentation/design/ssu.rst` |
| RSE/TF-M | `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/partition/`, `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-fvp/` |
| Safety Island CL0/SCP | `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/` |
| Safety Island CL1/Zephyr | `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_fvp_safety_island_c1/`, `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/overlays/`, `arm-zena-css/components/safety_island/zephyr/src/` |
| Primary Compute DT | `hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dts`, `hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dtsi`, `hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp.dtsi`, `hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp-defs.dtsi` |
| Linux 드라이버 | `sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c`, `sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src/rpmsg_net.c`, `sw-ref-stack/components/primary_compute/linux_drivers/pfdi_misc_mod/src/pfdi_misc.c`, `hsoc-stack/components/primary_compute/linux/drivers/mailbox/arm_mhuv3.c` |

## 전체 하드웨어 구성

Apollo FVP는 크게 네 개의 실행 도메인과 시스템 관리/인터커넥트 도메인으로
나뉜다.

| 도메인 | 코어 | 주요 펌웨어/OS | 역할 |
| --- | --- | --- | --- |
| RSE | Cortex-M55 DCLS | TF-M BL1_1, BL1_2, BL2, RSE runtime | Root of Trust, 보안 부팅, 이미지 검증, ATU 설정, RSE/SI/AP handoff |
| Safety Island CL0 | Cortex-R82AE DCLS | SCP-firmware SI0 RAMFW | 전원/클럭/리셋 관리, CMN/GIC/NI-710AE 초기화, SCMI 서버, PFDI monitor, FMU/SSU 처리 |
| Safety Island CL1 | Cortex-R82AE 4-core SMP | Zephyr | 안전 애플리케이션, PFDI agent, HIPC/RPMsg 네트워크, CL0와의 안전 서비스 통신 |
| Primary Compute | 4 clusters x 4 Cortex-A720AE | TF-A BL2/BL31, OP-TEE, U-Boot, Linux | 일반 목적 AArch64 컴퓨트, Linux 장치 드라이버, SI remoteproc/RPMsg, PFDI SMC 클라이언트 |
| SMD/Interconnect | 전용 관리 IP | RSE와 SCP가 설정 | SMD SRAM, MHUv3, NI-710AE, ATU, RGM, counters, system peripherals |

부팅 순서는 RSE가 가장 먼저 시작하고, RSE BL2가 SI CL0 이미지를 Safety
Island LLRAM에 적재해 CL0를 reset release한다. 이후 SI CL0가 PC
self-test, CMN S3(AE), GIC-720AE, peripheral 초기화를 수행하고, RSE가 AP
BL2, RSE runtime, NI-710AE APUs 설정을 마친 뒤 Primary Compute가
부팅된다. CFG2에서는 SI CL1 Zephyr 이미지도 flash layout과 RSE ATU
설정에 포함되어 CL1 Safety Island 기능이 활성화된다.

## 주소 공간 관점

Zena CSS는 여러 도메인이 서로 다른 local view와 ATU window로 같은 시스템
자원에 접근한다. 포팅과 디버깅에서는 다음 주소 기준을 구분해야 한다.

| 기준 | 의미 |
| --- | --- |
| AP view | Linux/TF-A device tree에서 보이는 Primary Compute 주소 |
| RSE local view | Cortex-M55/TF-M이 직접 사용하는 32-bit local 주소 |
| RSE host ATU view | RSE가 AP/SI/SMD host 물리 주소를 접근하기 위해 여는 window |
| SI CL0 local view | SCP-firmware가 사용하는 Safety Island CL0 주소 |
| SI CL1 local view | Zephyr가 사용하는 Safety Island CL1 주소 |
| SMD 52-bit system view | 상위 nibble로 AP/SMD/RSE/SI 접근 도메인을 구분하는 system management 주소 |

### AP System Memory Map

`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`의 AP system
memory map과 Apollo Linux/TF-A DTS를 기준으로 한 주요 영역은 다음과 같다.

| AP 주소 | 크기 | 블록 | 코드/문서 근거 |
| --- | ---: | --- | --- |
| `0x00_2000_0000` - `0x00_27FF_FFFF` | 128 MiB | AP GIC-720AE region | Zena CSS programmer model |
| `0x00_3000_0000` - `0x00_3FFF_FFFF` | 256 MiB | AP memory expansion, virtio-mmio 일부 | Zena CSS programmer model, Linux DTS |
| `0x00_4000_0000` - `0x00_4FFF_FFFF` | 256 MiB | AP에서 SMD 접근용 ATU window | Zena CSS programmer model, SCP ATW 설정 |
| `0x00_5FFF_0000` - `0x00_5FFF_FFFF` | 64 KiB | RGIC2LGIC message registers | Zena CSS programmer model |
| `0x00_6000_0000` - `0x00_7FFF_FFFF` | 512 MiB | PCIe/NI-710AE memory space 1 | Zena CSS programmer model |
| `0x00_8000_0000` - `0x00_FFFF_FFFF` | 2 GiB | DRAM bank 0 | Linux/TF-A DTS |
| `0x01_0000_0000` - `0x01_3FFF_FFFF` | 1 GiB | CMN GPV | Zena CSS programmer model, SCP ATW |
| `0x01_4000_0000` - `0x01_7FFF_FFFF` | 1 GiB | Cluster management domain | Zena CSS programmer model |
| `0x01_8000_0000` - `0x01_BFFF_FFFF` | 1 GiB | Memory controller control | Zena CSS programmer model |
| `0x01_C000_0000` - `0x02_1FFF_FFFF` | 1.5 GiB | SMMU, NI-710AE GPV, PCIe control/PHY | Zena CSS programmer model, TF-A DTS |
| `0x08_0000_0000` - `0x08_7FFF_FFFF` | 2 GiB | Debug memory map | Zena CSS programmer model |
| `0x08_8000_0000` - `0x0D_FFFF_FFFF` | 22 GiB | DRAM extension | Zena CSS programmer model |

Apollo Linux DTS에서 실제 노출되는 DRAM은 `0x80000000` 기준 bank와
`0x200_00000000` 기준 추가 bank로 표현된다. 이 값은 FVP/TF-A가 넘기는
runtime DTB의 기준이므로 QBox가 Linux까지 부팅하려면 최소한 이 DTB에서
사용하는 DRAM, GIC, UART, watchdog, MHU, reserved-memory 영역을 맞춰야 한다.

### System Management 52-bit Map

System Management Domain은 상위 주소 nibble로 대상 도메인을 구분한다.
이 구분은 RSE/SI/SMD ATU와 NI-710AE APU 설정에서 중요하다.

| 52-bit 주소 영역 | 대상 | 비고 |
| --- | --- | --- |
| `0x00_0000_0000_0000` - `0x00_FFFF_FFFF_FFFF` | AP access | AP global address space |
| `0x01_0000_0000_0000` - `0x01_FFFF_FFFF_FFFF` | AP through TCU | I/O virtualization 경로 |
| `0x02_0000_6000_0000` - `0x02_0000_600F_FFFF` | SMD SRAM | 1 MiB shared management SRAM |
| `0x02_0000_D000_0000` - `0x02_0000_D7FF_FFFF` | CSS control | RGM, ATU, counters, PIK, UART/GPIO, FMU, I/O register description |
| `0x02_0000_D800_0000` - `0x02_0000_E7FF_FFFF` | System control expansion | SMD expansion |
| `0x03_0000_0000_0000` - `0x03_0000_FFFF_FFFF` | RSE access | RSE system view |
| `0x04_0000_0000_0000` - `0x04_0000_FFFF_FFFF` | Safety Island access | SI system view |

CSS control 영역의 중요한 하위 블록은 다음과 같다.

| 주소 | 블록 |
| --- | --- |
| `0x02_0000_D001_0000` | Reset Generation Manager |
| `0x02_0000_D007_0000` | SMD expansion to SMD ATU |
| `0x02_0000_D008_0000` | AP to SMD ATU |
| `0x02_0000_D009_0000` | Cluster management to SMD ATU |
| `0x02_0000_D010_0000` | REFCLK counter control |
| `0x02_0000_D011_0000` | REFCLK counter read |
| `0x02_0000_D020_0000` | SYSTOP PIK |
| `0x02_0000_D021_0000` | DBGTOP PIK |
| `0x02_0000_D030_0000` | SMD UART |
| `0x02_0000_D031_0000` | SMD GPIO |
| `0x02_0000_D040_0000` | System ID |
| `0x02_0000_D200_0000` 이후 | Cluster/System/GIC/SMD/Peripheral/I/O FMU regions |
| `0x02_0000_D301_0000` | I/O block register description |
| `0x02_0000_D302_0000` | SMD NoC config |
| `0x02_0000_D306_0000` | SMD AHB2AXI NoC config |

## RSE Block

### 코어와 역할

RSE는 Cortex-M55 primary core와 redundant Cortex-M55 core가 DCLS로 구성된
Root of Trust 도메인이다. TF-M 포트는 BL1_1, BL1_2, BL2, secure runtime,
non-secure runtime, RSE communication partition을 포함한다. Apollo FVP
부팅에서 RSE는 다음을 담당한다.

- RSE critical subsystem 초기화와 OTP/flash 기반 boot chain 진행
- SI CL0, SI CL1, AP BL2/FIP 이미지 적재와 인증
- AP/SI/SMD 접근을 위한 RSE ATU region 설정
- NI-710AE APU와 host 접근 권한 설정의 초기 root 역할
- RSE/SI/AP 사이 MHU/SCMI 초기 handoff
- CC3XX, KMU, LCM, OTP 등 보안 IP를 통한 RoT 서비스 제공

### RSE Local Memory Map

TF-M 공통 RSE `platform_base_address.h`와 Apollo FVP memory size header의
주요 local view는 다음과 같다.

| RSE local 주소 | 크기/범위 | 블록 |
| --- | ---: | --- |
| `0x00000000` | implementation-defined | Non-secure ITCM alias |
| `0x10000000` | implementation-defined | Secure ITCM |
| `0x11000000` | ROM | Secure boot ROM |
| `0x20000000` | implementation-defined | Non-secure DTCM alias |
| `0x30000000` | implementation-defined | Secure DTCM |
| `0x21000000` | 256 KiB | VM0 non-secure SRAM alias |
| `0x21040000` | 256 KiB | VM1 non-secure SRAM alias |
| `0x31000000` | 256 KiB | VM0 secure SRAM |
| `0x31040000` | 256 KiB | VM1 secure SRAM |
| `0x50002000` | register block | DMA350 |
| `0x50080000` | register block | RSE SACFG |
| `0x50083000` | register block | MPC VM0 |
| `0x50084000` | register block | MPC VM1 |
| `0x5009E000` | register block | KMU |
| `0x500A0000` | register block | LCM |
| `0x50140000` | register block | SIC |
| `0x50150000` | register block | RSE ATU |
| `0x50154000` | register block | CC3XX |
| `0x5015A000` - `0x5015D000` | register blocks | counters, integrity checker, TRAM |
| `0x50160000` - `0x50270000` | multiple frames | MHU sender/receiver frames |
| `0x58000000` - `0x58003000` | register blocks | RSE system timers |
| `0x58020000` - `0x58029000` | register blocks | sysinfo, system control, PPUs |
| `0x5802E000` - `0x58041000` | register blocks | watchdog and timers |
| `0x58110000` - `0x58112000` | register blocks | ILCU, OTP, DCSU |
| `0x60000000` - `0x6FFFFFFF` | 256 MiB | Host non-secure data access ATU window |
| `0x70000000` - `0x7FFFFFFF` | 256 MiB | Host secure data access ATU window |
| `0xE0305000` | register block | RSE debug UART non-secure alias |
| `0xF0305000` | register block | RSE debug UART secure alias |

VM0/VM1은 Apollo FVP에서 각각 256 KiB이고, 총 RSE SRAM window는 512 KiB로
구성된다. RSE flash layout은 BL2, secure runtime, SI CL0 image, SI CL1
image, AP BL2/FIP primary/secondary slots를 포함한다.

### RSE Host ATU Mapping

Apollo FVP TF-M 포트의 `host_atu_base_address.h`는 RSE가 다른 도메인에
접근하기 위한 logical window와 host physical target을 정의한다. 핵심
mapping은 다음과 같다.

| 용도 | 대상 host 주소 | 의미 |
| --- | --- | --- |
| AP BL2 적재 | AP shared SRAM + `0x82000` | RSE가 AP BL2 image를 AP boot SRAM에 배치 |
| SI CL0 image 적재 | SI CL0 SRAM base | RSE가 SI CL0 firmware를 LLRAM/SRAM에 배치 |
| SI CL1 image 적재 | SI CL1 SRAM base | CFG2 Zephyr image 적재 |
| SI CL0 CUB | SI CL0 cluster utility base | SI CL0 release/reset/control |
| AP secure flash | AP memory expansion + flash offset | AP FIP/BL2 image 접근 |
| RSE to SI MHU | `0x04_0000_03C0_0000` 근방 | RSE-SI MHU frame window |
| RSE to SI shared SRAM | `0x04_0000_0400_0000` | RSE/SCP shared SRAM |
| SI ATU | `0x04_0000_0310_0000` | Safety Island ATU control |
| AP to SMD ATU | `0x02_0000_D008_0000` | AP에서 SMD 접근 window 설정 |
| AP-RSE mailbox | `0x0000_FFFC_0000` | AP/RSE mailbox |
| SMD expansion to SMD ATU | `0x02_0000_D007_0000` | SMD expansion ATU |
| SYSTOP PIK | `0x02_0000_D020_0000` | AP/system power integration |

이 구조 때문에 RSE 부팅 성능이나 QBox fidelity 문제를 분석할 때 단순 local
register access와 host ATU access를 분리해서 봐야 한다. 예를 들어 CC3XX는
RSE local `0x50154000` register block이고, SI/AP 이미지 적재는 ATU를 통한
host memory write 경로이다.

## Safety Island CL0 Block

### 코어와 역할

Safety Island CL0는 Cortex-R82AE DCLS 기반 관리 cluster이며 SCP-firmware
SI0 RAMFW가 실행된다. RD-Aspen CFG2에서 CL0는 전체 Zena CSS system
management의 실행 주체이다.

주요 책임은 다음과 같다.

- SI CL0 자체 boot/runtime 초기화
- PC self-test와 Primary Compute release 지원
- CMN S3(AE), GIC-720AE, NI-710AE, ATW/ATU window 설정
- AP/SI/RSE 사이 SCMI 서비스와 MHUv3 doorbell 처리
- AP cluster/core power management, PSCI 연계
- PFDI monitor로 AP 16 cores와 SI CL1 4 cores heartbeat 감시
- FMU tree, SSU, fault event 처리
- UART, timers, watchdog, counters 등 SI peripheral 관리

### SI CL0 Memory Map

SCP-firmware Apollo FVP `si0_mmap.h`가 CL0 local view의 중심 근거이다.

| SI CL0 주소 | 크기 | 블록 |
| --- | ---: | --- |
| `0x1_2000_0000` | 512 KiB | SI0 ITC RAM |
| `0x1_2008_0000` | 512 KiB | SI0 DTC RAM |
| `0x3000_0000` | 4 MiB | Safety Island GIC window |
| `0x3000_0000` | register block | GICD view 0 |
| `0x3008_0000` | register block | GICR view 0 |
| `0x3010_0000` | register block | GICD view 1 |
| `0x3018_0000` | register block | GICR view 1 |
| `0x2880_0000` | 8 MiB | SI CL1 Cluster Utility Block |
| `0x2A00_0000` | 16 MiB | SI peripheral base |
| `0x2A40_0000` | register block | SI0 UART |
| `0x2A50_0000` | register block | SSU |
| `0x2A51_0000` - `0x2A55_0000` | register blocks | SI FMU0-4 |
| `0x2A6F_0000` | register block | REFCLK counter control |
| `0x2A72_0000` | register block | timer/counter |
| `0x3200_0000` | register block | Device FMU base |
| `0x3202_0000` | register block | GIC FMU |
| `0x3800_0000` | register blocks | MHU frame space |
| `0x3820_0000` / `0x3824_0000` | register blocks | CL1 to CL0 MHU frames in CFG2 |
| `0x4000_0000` | 8 MiB | RSE/SCP shared SRAM group 0 |
| `0x4800_0000` | 8 MiB | RSE/SCP shared SRAM bank 1 |
| `0x8000_0000` | 1536 MiB | SI ATW I/O window |
| `0xE000_0000` 이후 | 512 MiB | SI ATW memory window |

### SI CL0 ATW Windows

SI CL0는 ATW window를 통해 AP/SMD/cluster management 영역에 접근한다.
SCP-firmware의 `si0_mmap.h`는 다음 경로를 정의한다.

| Window | 대상 |
| --- | --- |
| ATW0 | CMN GPV 1 GiB |
| ATW1 | Cluster utility 256 MiB |
| ATW2 | SMD expansion 128 KiB |
| ATW3 | SYSTOP PIK 64 KiB |
| ATW4 | System ID 64 KiB |
| ATW5 | counters/timers 192 KiB |
| ATW6-ATW9 | AP cluster NI-710AE regions |
| ATW10 | system control NI-710AE region |
| ATW11 | AP GIC 128 MiB |
| ATW12 | SMB NI-710AE region |
| Memory windows | AP peripheral SRAM secure/non-secure, SMCF MGI, SMD SRAM, SMCF expansion SRAM |

`config_ni_710ae.c`는 이 window들이 어떤 APU region과 연결되는지 정의한다.
특히 primary NI-710AE APU는 SCR, expansion QSPI, GPIO, ATU PCMA/PCPA,
local SRAM group0, I/O expansion, CL0 TCM, CL0 LLRAM 접근 권한을 구성하고,
MHU NCI는 RSE MHU space를 별도 region으로 둔다.

### SI CL0 MHU, SCMI, PFDI

`config_mhu3.c`와 `config_scmi.c` 기준 통신 경로는 다음과 같다.

| 경로 | 용도 |
| --- | --- |
| RSE <-> SI CL0 | boot confirmation, RSE/SCP SCMI, RSE handoff |
| AP domain 1 <-> SI CL0 | PSCI/power management |
| AP domain 3 <-> SI CL0 | PFDI monitor heartbeat for AP cores |
| AP non-secure <-> SI CL0 | SCMI performance/OSPM |
| SI CL1 <-> SI CL0 | CL1 PFDI monitor heartbeat and safety coordination |

PFDI monitor는 SI CL0에 배치되고, AP cluster 0-3의 core 0-3 총 16 cores와
SI CL1 core 0-3 총 4 cores를 감시한다. 각 agent는 전용 MHU channel과
shared memory payload를 사용한다. 따라서 QBox/FVP에서 SI CL0 boot log의
PFDI timeout은 보통 AP 또는 SI CL1 agent의 MHU doorbell, shared memory,
SCMI protocol, 또는 해당 agent 서비스가 올라오지 않은 상태를 의미한다.

## Safety Island CL1 Block

### 코어와 역할

Safety Island CL1은 CFG2에서 활성화되는 4-core Cortex-R82AE SMP cluster이며
Zephyr가 실행된다. 현재 Apollo FVP 소스는 Apollo 전용 Zephyr board/overlay
이름으로 `apollo_fvp_safety_island_c1`을 사용한다. 공통 Safety Island
driver, library, subsystem, sample app source는
`arm-zena-css/components/safety_island/zephyr/src/`에서 공유하고, Apollo
board와 overlay는 `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/`
에서 관리한다.

CL1의 주요 기능은 다음과 같다.

- Zephyr SMP 기반 Safety Island application 실행
- PFDI agent 실행과 SI CL0 PFDI monitor heartbeat 송신
- HIPC/RPMsg/VirtIO 기반 Primary Compute Linux와의 데이터 교환
- `ethsi1` RPMsg network endpoint 제공
- MHUv3 doorbell 기반 attach/detach, vring kick, ack 처리

### SI CL1 Zephyr DTS Memory Map

Zephyr board DTS와 overlay에서 보이는 주요 주소는 다음과 같다.

| CL1 local 주소 | 크기 | 블록 |
| --- | ---: | --- |
| CPU `reg = 0x10000` | core node | Cortex-R82AE core 0 |
| CPU `reg = 0x10100` | core node | Cortex-R82AE core 1 |
| CPU `reg = 0x10200` | core node | Cortex-R82AE core 2 |
| CPU `reg = 0x10300` | core node | Cortex-R82AE core 3 |
| `0x3020_0000` | register block | SI GICD view 2 |
| `0x3026_0000`, `0x3028_0000`, `0x302A_0000`, `0x302C_0000` | GICR frames | CL1 per-core redistributors |
| `0x2A41_0000` | register block | CL1 UART |
| `0x1_4000_0000` | 8 MiB | CL1 SRAM |
| `0x4800_0000` | 4 KiB | SCMI shared memory |
| `0x3920_0000` | register block | PFDI agent MHU TX |
| `0x3900_0000` | register block | CL1 to PC MHU TX |
| `0x3904_0000` | register block | PC to CL1 MHU RX |
| `0x0800_0000` | 128 MiB | device region 0 |
| `0x2A00_0000` | 352 MiB | device region 1 |

### HIPC Shared Memory

HIPC overlay는 PC와 SI CL1 사이 RPMsg/VirtIO shared memory를 다음처럼
분할한다.

| 주소 | 크기 | 용도 |
| --- | ---: | --- |
| `0xE013_0000` | 128 KiB | resource table |
| `0xE015_0000` | 128 KiB | vring0 |
| `0xE017_0000` | 128 KiB | vring1 |
| `0xE019_0000` | 128 KiB | RPMsg virtio buffer |
| 전체 `0xE013_0000`부터 | 512 KiB | PC/SI CL1 HIPC shared RAM |

Zephyr overlay는 `busaddr_delta = 0xE0030000`을 사용해 CL1 view와 PC
remoteproc view 사이 주소 변환을 설명한다. Linux `arm_si_rproc` 드라이버는
device tree의 `ranges`를 읽고 `pa - bus_addr + dev_addr` 형태로 carveout
주소를 변환한다. 따라서 QBox에서 HIPC를 재현하려면 MHU만 맞추는 것으로는
부족하고 reserved-memory, ranges, resource table, vring buffer 주소 변환이
동시에 맞아야 한다.

## Processor Block

Primary Compute는 4개의 Processor Block으로 구성되며, 각 block은 4개의
Cortex-A720AE core와 DSU-120AE cluster를 포함한다. 전체는 16개의 AP core로
구성된다.

### AP CPU Topology

Linux/TF-A Apollo DTS는 다음 구성을 노출한다.

| Cluster | CPU 수 | CPU compatible | L2 | Shared L3 |
| --- | ---: | --- | ---: | ---: |
| Cluster 0 | 4 | `arm,cortex-a720ae` | core당 512 KiB | 4 MiB |
| Cluster 1 | 4 | `arm,cortex-a720ae` | core당 512 KiB | 4 MiB |
| Cluster 2 | 4 | `arm,cortex-a720ae` | core당 512 KiB | 4 MiB |
| Cluster 3 | 4 | `arm,cortex-a720ae` | core당 512 KiB | 4 MiB |

TF-A `apollo_fvp-defs.dtsi`는 CPU macro로 MPID, cache, L3, SCMI DVFS phandle을
정의한다. Linux `apollo-fvp.dtsi`는 CPU map을 실제 node로 펼친다. AP core
bring-up은 PSCI를 사용하며, secondary core release는 TF-A와 SI CL0 SCP
SCMI/PSCI 경로를 거친다.

### Cluster Management Domain

Cluster management domain은 AP 주소 `0x01_4000_0000` 이후에 cluster별
64 MiB window로 배치된다.

| AP 주소 | 대상 |
| --- | --- |
| `0x01_4000_0000` - `0x01_43FF_FFFF` | Cluster 0 shared peripheral |
| `0x01_4400_0000` - `0x01_47FF_FFFF` | Cluster 1 shared peripheral |
| `0x01_4800_0000` - `0x01_4BFF_FFFF` | Cluster 2 shared peripheral |
| `0x01_4C00_0000` - `0x01_4FFF_FFFF` | Cluster 3 shared peripheral |

각 cluster window의 주요 offset은 cluster control `0x01000000`, MPAM
`0x01010000`, RAS `0x01020000`, cluster PPU `0x01030000`, AMU `0x01040000`,
AE control `0x01050000`, core별 PPU `0x01080000`/`0x01180000`/`0x01280000`/
`0x01380000`, RVBAR control `0x02000000`이다.

## Interrupt Block

### GIC-720AE 구성

Zena CSS interrupt block은 GIC-720AE Distributor, Redistributor, ITS를
포함한다. AP DTS는 GICv3 compatible로 GICD/GICR/ITS를 기술한다.

| AP 주소 | 블록 |
| --- | --- |
| `0x2080_0000` | AP GIC Distributor |
| `0x2084_0000` | GIC ITS |
| `0x2088_0000`부터 per-core frames | 16개 GIC Redistributor frames |

Apollo Linux DTS에는 GIC-A720AE multiview 동작 때문에 `GICR_TYPER.Last`를
신뢰하지 않고 16개 per-core GICR frame을 각각 기술한다는 주석이 있다. 이
정보는 QBox에서 AP GIC를 단일 contiguous redistributor bank로 단순화하면
Linux GIC probe가 다른 결과를 볼 수 있음을 의미한다.

Safety Island GIC는 multiview 구조이다.

| View | 사용자 | 근거 |
| --- | --- | --- |
| View 0 | SI CL0 SCP boot/config path | RD-Aspen design, SCP GIC multiview config |
| View 1 | SI CL0 OS/runtime 및 AP-visible programming | SCP GIC multiview config |
| View 2 | SI CL1 Zephyr | Zephyr DTS, SCP GIC multiview config |

### AP Interrupt Map

Apollo Linux/TF-A DTS와 SCP GIC config에서 확인되는 AP 쪽 주요 SPI/PPI는
다음과 같다.

| Interrupt | 대상 |
| --- | --- |
| PPI 13/14/11/10/12 | Armv8 architectural timer |
| SPI 49 | memory-mapped timer frame |
| SPI 50 | AP watchdog |
| SPI 52 | AP PL011 UART |
| SPI 65 | SMMUv3 |
| SPI 112 | AP to SI0 SCMI MHU TX |
| SPI 113 | SI0 to AP SCMI MHU RX |
| SPI 120 | AP to SI1 HIPC MHU TX |
| SPI 121 | SI1 to AP HIPC MHU RX |
| SPI 216-219 | DSU PMU per cluster |
| SPI 257-263 | virtio-mmio devices |
| SPI 268 | PL031 RTC |

### Safety Island Interrupt Map

SCP-firmware `si0_irq.h`와 Zephyr DTS 기준 주요 SI interrupts는 다음과
같다.

| 도메인 | Interrupt | 대상 |
| --- | --- | --- |
| SI CL0 | 34 | CL0 timer |
| SI CL0 | 37 | CL0 watchdog |
| SI CL0 | 40 | CL0 UART |
| SI CL0 | 97 | AP to SI0 non-secure MHU |
| SI CL0 | 99 | AP domain 1 MHU |
| SI CL0 | 103 | AP domain 3 MHU |
| SI CL0 | 105 | RSE to SI0 MHU |
| SI CL0 | 107 | CL1 to CL0 MHU |
| SI CL0 | 128/129 | FMU critical/non-critical |
| SI CL1 | 33 | CL1 timer |
| SI CL1 | 36 | CL1 watchdog |
| SI CL1 | 39 | CL1 UART |
| SI CL1 | 40/41 | CL1/PC HIPC MHU |
| SI CL1 | 50 | PFDI agent MHU TX |
| SI CL1 | 72/73 | PC/SI1 MHU as seen by SCP config |
| SI CL1 | 82 | CL1/CL0 MHU |

Linux MHUv3 binding은 `#mbox-cells = <3>`를 사용하며 extension, channel,
doorbell 정보를 DT cell로 전달한다. Apollo DT는 이 binding을 통해 SCMI와
SI remoteproc mailbox를 모두 구성한다.

## Interconnect Block

Interconnect block은 CMN S3(AE), NI-710AE, ATU/ATW, SMMU/TCU/TBU 경로를
포함한다.

### CMN S3(AE)

CMN S3(AE)는 Primary Compute cluster, external memory, I/O expansion,
SMCF, management paths를 연결하는 coherent mesh이다. SI CL0 SCP는 부팅
중 CMN 초기화를 수행한다. SCP ATW0는 CMN GPV 1 GiB 영역을 접근하도록
정의되어 있고, SI CL0가 CMN/system control register를 programming한다.

### NI-710AE

NI-710AE는 SMD, AP cluster, I/O, MHU, Safety Island memory paths의 접근
제어와 expansion 경로를 담당한다. SCP `config_ni_710ae.c`에서 확인되는
중요한 특성은 다음과 같다.

- secondary ASNI는 RSE가 local SRAM group0에 secure read/write로 접근할 수
  있도록 region을 둔다.
- primary NI-710AE는 SCR, expansion QSPI, GPIO, ATU PCMA/PCPA, local SRAM
  group0, I/O expansion, CL0 TCM, CL0 LLRAM region을 갖는다.
- MHU NCI는 RSE MHU space를 별도 APU region으로 둔다.
- CL1 유무에 따라 primary/secondary/MHU NCI periphbase 구성이 달라진다.

### ATU/ATW 설계 관점

RSE, SI, SMD에는 각각 ATU/ATW가 존재한다. RD-Aspen design 문서는 전체 ATU
구성을 RSE가 소유한다고 설명한다. 실제 코드도 RSE TF-M 포트가 AP/SI/SMD
host physical target과 logical window를 관리하고, SI CL0 SCP는 runtime
system management를 위해 자체 ATW aliases를 사용한다.

QBox 구현 관점에서는 다음을 구분해야 한다.

- RSE가 image load를 위해 수행하는 large sequential host memory write
- RSE/SI가 MHU/SCMI shared memory를 위해 수행하는 small register/shared
  SRAM access
- SI CL0가 CMN/GIC/NI-710AE를 초기화하기 위해 수행하는 ATW register access
- Linux가 AP view에서 MHU, GIC, SMMU, virtio, reserved memory를 접근하는
  normal device access

## I/O Block

I/O block은 SMMU/TCU/TBU, ITS, PCIe/virtio-like I/O, AP peripheral buses를
포함한다. 현재 Apollo FVP Linux DTS에서 실제 Linux boot에 필요한 주요 I/O
device는 다음과 같다.

| AP 주소 | Interrupt | Device | 비고 |
| --- | --- | --- | --- |
| `0x1A40_0000` | SPI 52 | PL011 UART | Linux console 후보 |
| `0x1A42_0000` / `0x1A43_0000` | SPI 50 | ARM SBSA watchdog | refresh/control frames |
| `0x1A81_0000` | SPI 49 | memory-mapped timer | AP timer frame |
| `0x1C000_0000` | SPI 65 | SMMUv3 | TF-A DTS 기준 |
| `0x2080_0000` | PPI 9 maint | GICv3 | GICD/GICR/ITS |
| `0x3002_0000` - `0x3008_0000` | SPI 257-263 | virtio-mmio | block/net/rng 등 FVP devices |
| `0x300D_0000` | SPI 268 | PL031 RTC | Linux RTC |
| `0x4002_0000` / `0x4005_0000` | SPI 112/113 | AP-SI0 SCMI MHU | SCMI performance/power |
| `0x400B_0000` / `0x400E_0000` | SPI 120/121 | AP-SI1 HIPC MHU | remoteproc/RPMsg |

SMMUv3는 TF-A DTS에 명시되어 있지만, 현 local boot path에서 핵심 부팅
성공은 GIC, UART, timer, watchdog, MHU, virtio, reserved-memory의 정합성에
더 직접적으로 의존한다. 다만 I/O virtualization fidelity를 높이려면 SMMU,
ITS, TBU/TCU 쪽도 AP DT와 일치하게 모델링해야 한다.

## System Management Block

System Management Block은 RSE, Safety Island, System Management Domain을
묶는 상위 기능 블록이다. SMD에는 NI-710AE, peripherals, SRAM, expansion
interface가 있고 SCMI service의 기반이 된다. 기본 control plane은 SI CL0가
담당하지만 root 권한과 초기 secure configuration은 RSE boot chain에 있다.

주요 IP와 소프트웨어 책임은 다음과 같다.

| IP/기능 | 주 소프트웨어 | 설명 |
| --- | --- | --- |
| RGM | RSE, SCP | reset sequencing과 domain reset control |
| SMD SRAM | RSE, SCP, TF-A/Linux | SCMI, mailbox payload, boot handoff |
| MHUv3 | RSE, SCP, Zephyr, Linux | RSE-SI, AP-SI0 SCMI, AP-SI1 HIPC, PFDI doorbells |
| SCMI | SCP server, TF-A/Linux clients, RSE peer | power, performance, reset, PFDI monitor 관련 protocol |
| PFDI monitor | SI CL0 SCP | AP/SI CL1 agent watchdog |
| PFDI agent | SI CL1 Zephyr, AP Linux/firmware | SI CL0 monitor로 heartbeat와 test result 전달 |
| FMU | SCP | critical/non-critical fault collection and event propagation |
| SSU | SCP | external safety manager로 safety status 전달 |
| Counters/timers | RSE, SCP, Linux | watchdog, timestamp, periodic monitoring |

PFDI의 AP Linux 쪽은 `pfdi_misc` driver가 SMC function IDs
`0xC40002D0`부터 `0xC40002D7`까지를 사용한다. 이 driver는 per-CPU misc
device `cpu/<n>/pfdi`를 만들고, CPU hotplug state와 per-CPU worker를 통해
각 CPU에서 PFDI SMC를 수행한다. 따라서 AP PFDI failure는 Linux driver만의
문제가 아니라 TF-A/firmware SMC service, SI CL0 PFDI monitor, AP-SI MHU
경로가 함께 동작해야 해결된다.

## Peripheral Block

Zena CSS Peripheral Block은 watchdog, generic timers, secure/non-secure
UART, AP boot RAM, scratch RAM 등을 포함한다. Apollo FVP에서는 각 도메인이
다음 주변장치 set을 가진다.

### RSE Peripherals

| Peripheral | 주소/근거 | 용도 |
| --- | --- | --- |
| DMA350 | `0x50002000` | secure data movement |
| CC3XX | `0x50154000` | crypto/root-of-trust operation |
| KMU | `0x5009E000` | key management |
| LCM | `0x500A0000` | lifecycle management |
| OTP wrapper | `0x58111000` 근방 | OTP emulation/boot data |
| MHU frames | `0x50160000` - `0x50270000` | RSE communication |
| RSE timers/watchdogs | `0x58000000` 이후 | timestamp, watchdog |
| RSE debug UART | `0xE0305000`/`0xF0305000` | secure/non-secure debug output |

### SI CL0 Peripherals

| Peripheral | 주소 | 용도 |
| --- | --- | --- |
| PL011 UART | `0x2A400000` | SCP console |
| Generic timer/counter | `0x2A6F0000`, `0x2A720000` | SCP scheduler, timeout |
| Watchdog | SCP IRQ map 기준 | safety supervision |
| MHUv3 frames | `0x38000000` 이후 | RSE/AP/SI CL1 통신 |
| FMU0-4 | `0x2A510000` - `0x2A550000` | fault management |
| SSU | `0x2A500000` | safety status unit |
| GIC view 0/1 | `0x30000000` 이후 | CL0 interrupt routing |
| NI-710AE config | SCP `config_ni_710ae.c` | access protection, NoC setup |

### SI CL1 Peripherals

| Peripheral | 주소 | 용도 |
| --- | --- | --- |
| PL011 UART | `0x2A410000` | Zephyr console |
| GIC view 2 | `0x30200000` / `0x30260000` 이후 | CL1 SMP interrupt routing |
| MHU PC TX/RX | `0x39000000` / `0x39040000` | HIPC/RPMsg |
| MHU PFDI TX | `0x39200000` | CL1 PFDI agent heartbeat |
| SCMI shared memory | `0x48000000` | CL1/CL0 PFDI payload |
| HIPC shared RAM | `0xE0130000` 이후 | resource table, vrings, RPMsg buffers |

### Primary Compute Peripherals

| Peripheral | 주소 | Linux/TF-A 사용 |
| --- | --- | --- |
| PL011 UART | `0x1A400000` | console |
| SBSA watchdog | `0x1A420000`/`0x1A430000` | watchdog service |
| memory timer | `0x1A810000` | timer frame |
| GIC/ITS | `0x20800000`/`0x20840000` | interrupt controller/MSI |
| PL031 RTC | `0x300D0000` | wall clock |
| virtio-mmio | `0x30020000` - `0x30080000` | block/net/rng/etc |
| AP-SI0 MHU | `0x40020000`/`0x40050000` | SCMI |
| AP-SI1 MHU | `0x400B0000`/`0x400E0000` | remoteproc/RPMsg |

## Component별 소프트웨어 의존성

### TF-M/RSE

TF-M Apollo FVP 포트는 RSE memory sizes, host AP/SI/SMD maps, flash layout,
ATU region IDs를 Apollo 전용 파일로 분리한다. RSE가 정상 부팅되지 않으면
SI CL0, SI CL1, AP 모두 image handoff를 받지 못한다. RSE 분석 시 우선순위는
BL1_1/BL1_2/BL2 log, CC3XX/OTP/flash access, ATU setup, MHU setup 순서가
된다.

### SCP-firmware/SI CL0

SCP-firmware Apollo FVP 포트는 hardware topology와 runtime management
정의를 대부분 `si0_ramfw`에 둔다. `platform_core.h`는 AP 4 clusters x 4
cores와 SI CL1 4 cores를 정의하고, `config_gicx00_multiview.c`는 SI/AP
interrupt view mapping을 지연/즉시 설정으로 나눈다. `config_scmi.c`와
`config_mhu3.c`는 AP, RSE, SI CL1의 SCMI/PFDI mailbox topology를 결정한다.

### Zephyr/SI CL1

Zephyr Safety Island CL1은 board DTS, defconfig, HIPC overlay, PFDI agent
overlay가 함께 맞아야 한다. HIPC는 `resource table`, `vring0`, `vring1`,
`buffer` 네 영역이 128 KiB씩 배치된다는 Linux/Zephyr 양쪽 계약을 갖고,
PFDI는 CL1 core별 doorbell과 shared memory를 사용한다.

### TF-A/U-Boot/Linux/Primary Compute

TF-A는 Apollo FVP DT를 생성/전달하고 PSCI, BL31, OP-TEE, U-Boot handoff를
담당한다. U-Boot Apollo DTS는 minimal model/compatible만 두고 TF-A가 넘긴
FDT를 사용한다. Linux DTS는 AP-visible 하드웨어 계약의 중심이며, SI CL1
remoteproc와 SCMI/MHU, GIC multiview workaround, reserved memory를 직접
기술한다.

### Linux out-of-tree drivers

`arm_si_rproc` driver는 SI CL1을 Linux remote processor로 등록하지만,
SI CL1 자체를 Linux가 부팅시키는 구조가 아니다. 초기 상태는 detached이고,
MHU attach/ack와 resource table을 통해 이미 실행 중인 CL1 Zephyr와
연결한다.

`rpmsg_net` driver는 RPMsg endpoint 이름 `ethsi0`, `ethsi1`, `ethsi2`를
network device 이름으로 사용한다. 현재 CL1 HIPC 경로에서는 `ethsi1`이 주요
관찰 대상이다.

`pfdi_misc` driver는 per-CPU misc device와 SMC call을 통해 AP core별 PFDI
test/control interface를 제공한다. 이 드라이버는 firmware PFDI version
1.0과 feature support를 초기화 시점에 검증한다.

## Block별 QBox 모델링 체크포인트

| 블록 | 최소 기능 | fidelity 위험 |
| --- | --- | --- |
| RSE | Cortex-M55 실행, TF-M image, CC3XX/OTP/flash, ATU, MHU, timers | CC3XX polling/write latency, ATU bulk copy, reset sequencing |
| SI CL0 | Cortex-R82AE 또는 service-mode SCP, GIC multiview, MHU/SCMI, PFDI monitor | PFDI timeout, SCMI power domain mismatch, FMU/SSU event 누락 |
| SI CL1 | 4-core Cortex-R82AE Zephyr, UART, GIC view2, MHU, shared memory | SMP/timer/GIC view mismatch, HIPC 주소 변환 불일치 |
| AP processor | 16 Cortex-A720AE view, PSCI, GICR frames, timers | QEMU CPU model 차이, redistributor Last bit 처리 |
| Interconnect | AP/SI/RSE/SMD address translation, NI-710AE access windows | register-only stub로 인한 권한/ordering 차이 |
| Interrupt | AP GICv3, SI GIC multiview, MHU doorbells | view별 SPI routing 오류, PPI/SPI polarity 오류 |
| I/O | UART, watchdog, RTC, virtio, SMMU placeholder/real model | Linux driver probe 순서와 interrupt delivery 차이 |
| System management | SCMI, RGM, SMD SRAM, counters, PFDI, FMU/SSU | boot handoff와 runtime service를 분리하지 못하는 문제 |

## 분석 결과 요약

1. Apollo FVP의 현재 하드웨어 기준은 RD-Aspen CFG2이며, AP 16 cores,
   SI CL0 DCLS, SI CL1 4-core SMP, RSE Cortex-M55 DCLS 구성이 동시에
   활성화된다.
2. RSE는 단순 security firmware가 아니라 ATU owner, image loader,
   SI/AP handoff owner이다. RSE memory map과 host ATU map은 full-system
   에뮬레이션의 기준점이다.
3. SI CL0는 system management runtime의 중심이다. CMN/GIC/NI-710AE,
   SCMI, PFDI monitor, FMU, SSU가 모두 SCP-firmware 설정에 묶여 있다.
4. SI CL1은 Zephyr SMP와 HIPC/RPMsg/PFDI agent를 포함한다. Linux의
   `si-rproc`은 CL1을 직접 부팅하지 않고 이미 실행 중인 CL1에 attach한다.
5. AP Linux device tree는 GIC multiview, MHUv3, SI CL1 reserved memory,
   virtio-mmio, watchdog, UART, RTC, timer를 부팅 계약으로 사용한다.
6. Interconnect/interrupt는 문서상 block 이름보다 코드상 ATU, ATW,
   MHU, GIC view, NI-710AE APU region의 조합으로 검증해야 한다.

## 추후 확인 항목

- Runtime boot artifact의 최종 DTB를 decompile해 source DTS와 실제 전달
  DTB의 차이를 비교해야 한다.
- SMMU/ITS/PCIe 쪽은 현재 Linux 부팅 최소 경로보다 낮은 우선순위였으므로,
  I/O fidelity 목표가 올라가면 별도 register-level 분석이 필요하다.
- FMU/SSU는 SCP config와 문서상 구조를 정리했지만, fault injection과
  interrupt propagation은 runtime 로그와 함께 추가 검증해야 한다.
- Apollo 전용 포팅 레이어가 더 분리되면 이 문서의
  `apollo_fvp_safety_island_c1` board/overlay 근거와 공통 Safety Island
  source 근거를 함께 갱신해야 한다.

# 현재 소스와 공개 레퍼런스 조사

상위 문서: [통합 계획](README.md). 조사일: 2026-10-04. 제조사 공식 문서와 현재 소스를 근거로 하며, 공개되지 않은 schematic·safety manual·register 설정은 추정으로 채우지 않았다.

## 1. 현재 Apollo QVP 기준점

저장소별 branch/SHA와 기존 dirty 상태는 [analysis-inputs.json](analysis-inputs.json)에 있다. `build/conf/local.conf`의 `MACHINE ??= "apollo-qvp"`, `TMPDIR`, `templateconf.cfg`, `bblayers.conf`를 읽었다. BitBake 환경을 평가하거나 provider를 재빌드하지 않았으므로 설치된 binary가 이 소스와 일치한다고 판정하지 않는다.

| 조사 항목 | 현재 소스에서 확인한 사실 | 설계 영향 |
|---|---|---|
| 구성 entry | [apollo-qvp-saturn-v.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua) 9–25행이 SoC와 AP/SI board를 조합한다. [saturn-v.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua) 3행은 실물 schematic parity를 `UNVERIFIED`로 표시한다. | vMCU는 board population으로 추가한다. |
| 기존 QemuInstance | [RSE](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/qemu.lua), [AP](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap/execution.lua), [SI CL0](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si/cl0-qemu.lua), [SI CL1](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si/cl1-qemu.lua): `qemu_inst`, `ap_qemu_inst`, `si_cl0_qemu_inst`, `si_cl1_qemu_inst` | vMCU firmware backend는 다섯 번째 독립 instance가 된다. |
| 실행 시간 | [vp/qvp.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/qvp.lua), 각 domain 실행 설정: 기본 quantum 10 ms, `multithread-freerunning`/`quantum_keeper` | SIL Kit step만 줄여서는 deterministic deadline을 보장할 수 없다. |
| Arm CPU 후보 | [cpu_arm/CMakeLists.txt](../../hsoc-stack/tools/qbox/qemu-components/cpu_arm/CMakeLists.txt) 5–8행의 Cortex-M7/M55/R5/R52 wrapper | generic Arm firmware 시험 가능성을 제공한다. 완성 MCU board 지원은 별도다. |
| vendor MCU 공백 | [libqemu target_info.h](../../hsoc-stack/tools/qbox/qemu-components/common/include/libqemu-cxx/target_info.h)에는 TriCore/RH850 target이 없다. QEMU [triboard.c](../../hsoc-stack/tools/qemu/hw/tricore/triboard.c) 67–83행은 TC277 D-step이며 [tc27x_soc.c](../../hsoc-stack/tools/qemu/hw/tricore/tc27x_soc.c)는 CPU와 memory 중심이다. 조사한 target/hw/wrapper 범위에 TC397/RH850 통합이 없다. | TC277 또는 ISA 지원을 TC397 peripheral/binary 호환으로 확대하지 않는다. |
| AP UART | [ros/io_peri.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) 83–100행 DW UART 4개, [vp/ros/loopback.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ros/loopback.lua) 7–12행 0↔1, 2↔3 연결 | 전용 profile에서 pair 한 쪽을 vMCU로 연결할 수 있다. 기존 loopback 회귀를 분리한다. |
| SI UART | [SI CL0](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/io_peri.lua), [SI CL1](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/io_peri.lua)의 PL011은 console 연결 | SI 독립 제어용 UART는 신규 QVP extension으로 계획한다. |
| SPI | [dw-apb-ssi.h](../../hsoc-stack/tools/qbox/systemc-components/spi/dw-apb-ssi/include/dw-apb-ssi.h) 79–91행에 외부 SPI socket이 없다. [dw-apb-ssi.cc](../../hsoc-stack/tools/qbox/systemc-components/spi/dw-apb-ssi/src/dw-apb-ssi.cc) 381–404행은 SRL bit에 따른 TX→RX loopback | 외부 SPI bus, CS, mode, slave, DMA 상호작용이 신규 작업이다. |
| Ethernet | [vp/ros/virtio.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ros/virtio.lua) 106–118행 `virtio_mmio_net`, [artifacts.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/artifacts.lua) 기본 user network/SSH forwarding | AP 관리 기능 prototype에는 쓸 수 있다. automotive MAC·SI 통신으로 인정하지 않는다. |
| AP↔SI | [ap_si_mailbox.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua)의 MHU/SCMI 및 CL1 mailbox | 외부 MCU는 SI service를 통해 내부 상태를 받는다. |
| CAN/SIL Kit | Apollo Lua와 조사한 QBox/QBox-platform component 등록에서 CAN controller/bus 및 SIL Kit 연결을 확인하지 못했다. | 신규 controller/frontend, bridge, firmware driver를 계획한다. 다른 외부 layer 전체의 부재를 단정하는 결과는 아니다. |

후속 [TC397 QEMU 조사](tc397-qemu.md)에서 공개 `linumiz/qemu-tricore` fork의 TC397B machine을 확인했다. 위 표의 vendor MCU 공백은 **조사 기준 HEAD의 상태**다. 이후 현재 QEMU working tree에 [TC397 최소 모델](tc397-minimal-implementation.md)을 추가했으며 QBox/libqemu wrapper는 후속 작업으로 남는다. 독립 machine 실행과 내부 libqemu 통합을 나눠 평가한다.

Arm wrapper가 사용하는 `AARCH64` libqemu target은 library 선택 이름이다. Cortex-M guest가 AArch64 ISA로 실행된다는 뜻이 아니다. ISA/ABI, interrupt controller, firmware image format을 실제 backend와 맞춰야 한다.

### 1.1 PMIC와 reset의 현재 경계

| 근거 | 확인 내용 |
|---|---|
| [board/hw-block/tps6594.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/hw-block/tps6594.lua) 18–30행 | TPS6594 하나, I2C base `0x48`, `int_n → si_cl0_pmic_gpio.gpio_in_0`. |
| [si-cl0-pmic-host.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/extensions/si-cl0-pmic-host.lua) 1–14행 | I2C `0x2a800000`, GPIO `0x2a810000`은 QVP extension. `int_n`은 GPIO에서 읽을 수 있으나 AP/SI GIC IRQ 경로는 없다. I2C polled transport와 지속 fault 감시 service는 별개다. |
| [tps6594.h](../../hsoc-stack/tools/qbox/systemc-components/i2c/tps6594/include/tps6594.h) 83–102행 및 [tps6594.cc](../../hsoc-stack/tools/qbox/systemc-components/i2c/tps6594/src/tps6594.cc) 89–90, 169–185, 342–352행 | rail enabled/voltage 출력이 있지만 미연결 출력은 stub 처리된다. 현재 Apollo Lua에서 rail 출력 binding이 없다. public interface에 외부 enable/reset/PGOOD/watchdog 핀도 없다. |
| [SCP config_tps6594.c](../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_tps6594.c) 29–36행 및 [mod_tps6594.c](../../hsoc-stack/components/system_mgmt/scp-firmware/module/tps6594/src/mod_tps6594.c) 351–392행 | 기본 register configuration과 GPIO self-test는 false. probe/status 확인과 preserve 정책으로 시작한다. |
| [SI CL0 safety.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua), [zena_reset_ctrl.h](../../hsoc-stack/tools/qbox-platform/systemc-components/zena_reset_ctrl/include/zena_reset_ctrl.h) 214–228, 282–297행 | SSU fault/watchdog/power 원인을 AP reset에 합친다. 외부 board reset 입력은 신규 설계가 필요하다. |
| [reset_targets.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/reset_targets.lua) 13–61, 77–150행 | AP cold reset 대상과 Apollo 전체 reset fanout이 구분된다. |

따라서 **PMIC 레지스터를 바꾸면 현재 Apollo 전원이 실제로 꺼진다**거나, `int_n` 연결만으로 firmware IRQ 처리가 검증되었다고 말할 수 없다. 기능 모델의 rail 출력과 reset/power domain coupling을 추가해야 한다. SCP의 [TPS6594 설명](../../hsoc-stack/components/system_mgmt/scp-firmware/module/tps6594/README.md)과 기본 설정은 startup 상태 읽기와 fault API를 제공하지만 지속 GPIO 감시 loop를 확립하지 않는다. 주기 polling 또는 IRQ fault-monitor service는 신규 구현·검증 대상이다.

로컬 Arm 문서의 [기능 블록](../arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md)은 SI CL0의 power-management 역할을 설명한다. [부팅 흐름](../arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md), [기존 SoC/VP/board 분리](../soc_plan/README.md)를 함께 적용한다. 외부 vMCU를 추가해도 RSE→SI→AP firmware handoff를 우회하지 않는다.

## 2. NVIDIA DRIVE 레퍼런스

| 플랫폼/문서 | 확인된 사실 | Apollo에 적용할 원칙 |
|---|---|---|
| Orin, DRIVE OS 6.0.9.1 [MCU Setup and Usage](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html) | DRIVE AGX Orin에 Infineon AURIX **TC397X B-Step**, Vector MCU firmware를 명시한다. | 외부 MCU는 별도 firmware/boot/debug lifecycle을 가진다. |
| [DRIVE AGX Thor Development Platform](https://developer.download.nvidia.com/drive/docs/nvidia-drive-agx-thor-platform-for-developers.pdf), Dec. 2025, PDF p.6 | Safety MCU는 **Renesas U2A16**. | 사용자 예시를 MCU 제품 수준으로 구체화할 수 있다. |
| Thor, DriveOS 7.0.3 [Flashing Renesas](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/getting-started/flashing_aurix_from_thor.html) | P3960 예시와 `RH850-U2A16` firmware 명칭, AFW/NFW 구분을 확인한다. | firmware/toolchain·license를 구현 전에 결정한다. |
| Orin [SoC to Microcontroller Communications](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_soc_to_microcontroller_communications.html) | Ethernet/VLAN 관리, power/reset/boot-chain, shutdown GPIO handshake와 wake 경로가 있다. | packet 관리와 독립 전원 신호를 분리한다. |
| Thor [SoC to MCU Communication](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/embedded-software-components/Micro_Controller_Unit_MCU/soc_to_mcu_communication.html) | UDP/VLAN 공통 관리, GPIO boot 선택, `IST_DONE_N` 종료 완료와 timeout 후 rail-off를 기술한다. | 종료 요청·완료·timeout·실제 rail 상태를 구분한다. 문서의 20초를 Apollo 안전 deadline으로 복사하지 않는다. |
| Orin [Failover Handler on MCU](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_sw_modules/mcu_failover_handler_on_mcu.html) | SOC_ERROR toggle/stuck-at 감시, MCU가 SPI2 initiator로 FSI failure status와 seed/key를 주기적으로 교환한다. | 기존 SI CL0 PFDI 상태와 독립 SOC_ERROR toggle을 관찰한다. |
| Thor [FSI Runtime Environment](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/core-concepts/fsi_runtime_env.html) | MCU가 SPI master이고, FSI가 SPI interrupt를 통해 MCU 데이터를 수신한다. | 현재 Apollo DW SSI master/loopback과 방향·구현이 다르다. |
| Orin [CAN Driver](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/sys_components/CANDriver1.html) | CCPLEX CAN 2개, FSI CAN 2개 및 safety MCU를 포함한 P3710 DevKit CAN 6개. FSI CAN은 Linux에 보이지 않는다. | 모든 CAN이 외부 MCU를 반드시 통과한다는 일반화는 피한다. Apollo gateway는 선택한 제어 정책이다. |
| Thor [RH850 Console](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/embedded-software-components/Micro_Controller_Unit_MCU/rh850_console.html) | CAN, power/reset, fan/thermal/ADC, rail fault, PMIC SPI read/write, key/door event 시험을 제공한다. | board supervisor 범위를 구체화할 참고다. 정확한 PMIC 부품·모든 regulator ownership은 이 문서만으로 확정할 수 없다. |

이 구성은 인용한 DRIVE AGX 개발 플랫폼의 reference이며, 모든 Orin/Thor 제품·Jetson·양산 보드의 고정 구성을 뜻하지 않는다. 공통 구조는 **SoC 내부 safety domain과 외부 MCU가 협력하고, 관리·주기 감시·비상 신호를 나누는 것**이다. NVIDIA의 protocol binary format, 안전 시간, PMIC NVM/rail sequence를 Apollo 호환 사양으로 채택하는 계획은 아니다.

## 3. MCU 자체 감시와 PMIC 근거

[Infineon TC3xx functional safety 개요](https://documentation.infineon.com/aurixtc3xx/docs/ztz1745575952703)는 external watchdog/voltage monitoring과 외부 error signaling을 설명한다. TLF35584를 예로 든 독립 감시 경로는 vMCU 자체가 실패했을 때의 처리를 설계하는 근거다. 해당 부품이 NVIDIA 또는 Saturn-V에 장착되었다는 근거는 아니다.

[TI TPS6594-Q1 제품 설명](https://www.ti.com/product/TPS6594-Q1)과 [datasheet Rev. B](https://www.ti.com/lit/ds/symlink/tps6594-q1.pdf)는 rail monitoring, watchdog, SoC/MCU ESM, interrupt 및 PFSM 기반 동작을 설명한다. 현재 QBox 모델의 이름이 같아도 이 모든 기능을 구현한 것은 아니다. 특히 fault→EN_DRV/reset/rail 전이와 analog voltage monitoring은 소스·traffic 검증 범위를 따로 표시해야 한다.

## 4. SIL Kit 근거

조사 시 공식 문서 표시 버전은 **5.0.7**이다. 실제 도입 버전은 구현 시작 시 core·adapter·compiler·API 호환 조합을 pin하고 checksum으로 기록한다. `latest` 다운로드나 configure 중 자동 fetch에 의존하지 않는다.

| 공식 자료 | 이 계획에서 사용한 범위 |
|---|---|
| [Overview](https://vectorgrp.github.io/sil-kit-docs/index.html), [C/C++ API](https://vectorgrp.github.io/sil-kit-docs/api/api.html) | participant, CAN/Ethernet/PubSub/RPC 서비스와 C/C++ 통합 경계 |
| [CAN Service](https://vectorgrp.github.io/sil-kit-docs/api/services/can.html) | CAN frame/DLC/flags, Tx acknowledgement, simple simulation의 한계 |
| [Time Synchronization](https://vectorgrp.github.io/sil-kit-docs/api/services/timesync.html), [Simulation Concepts](https://vectorgrp.github.io/sil-kit-docs/simulation/simulation.html) | lifecycle, step 완료, timestamp와 동기 진행 조건 |
| [Custom Network Simulator](https://vectorgrp.github.io/sil-kit-docs/api/netsim.html) | detailed simulation은 별도 구현이며 API는 experimental |
| [QEMU Adapter README](https://raw.githubusercontent.com/vectorgrp/sil-kit-adapters-qemu/main/README.md) | socket Ethernet/chardev와 QMP 예제. QBox의 libqemu에 자동 장착되는 plugin은 아님 |
| [vCAN Adapter README](https://raw.githubusercontent.com/vectorgrp/sil-kit-adapters-vcan/main/README.md) | Linux SocketCAN/vcan과 SIL Kit CAN network 연결 |

이 조사로 확인한 것은 API와 연결 방식이다. 이 workspace에서 SIL Kit을 build하거나 QBox와 통신시킨 실행 결과는 아직 없다.

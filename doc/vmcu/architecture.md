# 통합 구조와 인터페이스

상위 문서: [통합 계획](README.md). 이하 객체명·파일명·protocol은 별도 표시가 없으면 **신규 제안**이다. 현재 구현의 UART/GPIO 배치와 wire format은 [SI CL0 Safety Channel](si0-safety-channel.md)을 따른다. [TC397 최소 모델](tc397-minimal-implementation.md)과 [Zephyr 도입 기록](zephyr-implementation.md)은 이전 단계의 근거다.

## 1. 외부 vMCU와 내부 Safety Island의 역할

| 영역 | 책임 | 독립성 요구 |
|---|---|---|
| Apollo AP/Linux | AD workload, application health, 정상 종료, 차량 데이터 소비 | AP hang을 vMCU가 검출할 수 있어야 한다. |
| Apollo SI CL0/SCP | 기존 PFDI AP 감시와 5초 vMCU 보고, SoC 내부 power/reset, TPS6594 접근 | AP reset 동안 가능한 범위에서 계속 동작한다. SoC 전체 전원 소실 시 생존한다고 가정하지 않는다. |
| Apollo SI CL1/Zephyr | 내부 safety application, fault 집계·상태 보고의 후보 | 기존 HIPC/OpenAMP 경로는 SoC 내부 통신으로 유지한다. |
| RSE | 기존 secure boot와 신뢰 경계 | vMCU가 임의 boot 주소·서명 우회를 지정하지 못한다. |
| 외부 vMCU | 차량 CAN gateway, ignition/wake, SoC health 감시, board recovery policy | AP·SI reset과 별도 reset, SRAM, firmware, timer/watchdog를 가진다. |
| 보드 전원 supervisor | power-good, enable/reset sequencing, vMCU 자체 실패 시 출력 제한 | 최종 cold-off를 요구한다면 vMCU/SoC 실패와 독립적으로 작동할 경로가 필요하다. |

동일 QBox 프로세스에 존재하더라도 vMCU를 Apollo의 `host_router`에 직접 연결해 내부 SRAM과 PMIC MMIO를 읽게 하지 않는다. 실제 보드에 해당 bus가 없으면 모델에도 공개하지 않는다. 상태는 정의된 통신 채널과 fault 신호로 전달한다.

## 2. QemuInstance 선택

| 방식 | 장점 | 비용·제한 | 결정 |
|---|---|---|---|
| SystemC `vmcu_functional` | 현재 QBox 시간·GPIO·bus와 연결하기 쉽고 고장 시나리오를 빨리 정의할 수 있다. | 펌웨어 명령 실행·RTOS scheduling·MCU register 호환을 검증하지 못한다. | 미채택. 현재 실제 TC397 Zephyr firmware를 사용한다. |
| QBox 내부 별도 `vmcu_qemu_inst` | 기존 SystemC 모델과 같은 시간축에서 MCU firmware/driver/IRQ를 시험할 수 있다. | CPU 외에도 interrupt controller, timer, flash/SRAM, reset, UART/SPI/CAN 모델이 필요하다. 프로세스 crash 격리는 없다. | TC397 독립 실행 검증 후 통합 비용과 시간 요구를 보고 결정한다. |
| 외부 QEMU 또는 상용 MCU simulator | 기존 MCU 모델을 재사용하고 프로세스 실패를 격리할 수 있다. | IPC, 시간 동기, signal serialization, license/CI 재현성 비용이 추가된다. | 현재 QEMU로 이식한 TC397의 **실행 경로로 채택**했다. RH850는 별도 모델 확보가 필요하다. |
| Apollo SI CL1에 vMCU 기능 합치기 | 기존 Zephyr firmware를 재사용하기 쉽다. | 외부 보드 감독자의 전원·reset 독립성을 잃는다. | 내부 safety 서비스로만 활용하고 외부 vMCU를 대체하지 않는다. |

**QBox 내부 통합을 선택하면 독립 QemuInstance만으로 충분하지 않다.** MCU 전용 router와 메모리·주변장치, load image, local reset fanout을 묶어야 한다. Apollo `system_reset`이 MCU까지 전파되면 요구한 독립성이 깨진다. 반대로 vMCU reset 시 CAN Tx queue와 미완료 command는 폐기하고, 차량 출력 허가를 기본 차단 상태로 돌려야 한다.

후속 조사와 사용자 요청에 따라 **현재 QEMU에 TC397 최소 모델을 이식하고 bare-metal firmware를 먼저 검증**한다. [최소 구현](tc397-minimal-implementation.md) 이후 Zephyr `qemu_tc3x` app/shell까지 구현했다. [TC397 상세 조사](tc397-qemu.md)의 단일 CPU·CAN/QSPI 공백·reset/IRQ 검토 조건을 적용한다. 기존 QBox Arm M-profile 기반 generic MCU는 대안으로 유지한다. 명령어·ABI가 다른 TC397/RH850 binary를 Arm 모델에서 실행할 수는 없다. MCU를 추가하려고 Apollo의 R82AE 또는 RSE M55 역할을 변경하지 않는다.

펌웨어의 `board_io`, `soc_link`, `vehicle_can`, `health_monitor`, `power_policy`를 HAL 경계로 나눈다. 정상 정책은 MCU firmware에서 실행하고, QBox test controller가 heartbeat를 대신 생성하거나 CAN payload를 firmware 몰래 재작성하지 않는다. 기능 모델은 동일한 외부 protocol test vector를 사용하는 참조 구현으로 남긴다.

## 3. 링크 선정

NVIDIA 레퍼런스는 [조사 문서](references.md)의 관리 Ethernet, safety SPI, 독립 GPIO 분리를 참고한다. Apollo에 같은 핀이 존재한다고 가정하지 않는다.

| 링크 | 용도와 방향 | QVP 1차 구현 | 목표/제약 |
|---|---|---|---|
| SoC↔vMCU Ethernet/UDP | AP↔MCU 관리, 상태, 진단, CAN payload 전달 | 기존 AP VirtIO network를 이용한 기능 실험은 가능하나 전용 management network 분리와 상대 endpoint가 필요하다. | 보드 Ethernet MAC/switch/VLAN을 확정한 후 재배치한다. VirtIO 성공은 실물 Ethernet driver 검증이 아니다. |
| SoC↔vMCU SPI | 주기 상태·fault detail, 짧고 제한된 frame | 현재 DW SSI는 **내부 SRL loopback만 구현**하고 외부 SPI socket이 없다. 먼저 bus/CS/mode/transaction을 구현한 후 Apollo master↔vMCU slave를 시험한다. | NVIDIA처럼 MCU master/SoC slave를 원하면 Apollo slave controller 지원도 필요하다. master끼리 연결하지 않는다. |
| SoC↔vMCU UART | 초기 health/command protocol, bring-up | AP 기능 시험은 기존 DW UART pair loopback을 opt-in으로 대체한다. SI CL0 PFDI 보고는 **PL011 0x2a820000 / INTID41 ↔ ASCLIN2**를 사용한다. 기존 SI PL011 console은 유지한다. | byte socket은 baud/FIFO/IRQ/overrun 검증을 대신하지 않는다. QVP extension을 실물 SI 핀으로 주장하지 않는다. |
| 독립 GPIO | `SOC_ERROR`, `SOC_PWR_REQ`, `IST_DONE_N`, `SOC_RESET_N`, `MCU_SOC_WAKE` | SI PL061 0x2a830000 ↔ TC397 PORT0, GPIO 전용 transport와 reset arbiter | 핀 이름은 제안이다. 실제 SSI/UART data가 끊겨도 fault·reset이 전달되어야 한다. |
| vMCU↔Vehicle CAN/CAN FD | 차량 상태 수신, 허용된 command/health/진단 송신 | frame endpoint↔SIL Kit CAN service, traffic generator/receiver | 1개 logical channel로 시작한다. 차체·섀시·진단 channel 분리는 요구된 bus topology가 있을 때 추가한다. |
| vMCU↔보드 PMIC | 전원 정책, fault와 reset | 기존 PMIC는 SI CL0 proxy로 관리, vMCU에 direct I2C master를 추가하지 않는다. | 독립 power supervisor 또는 명시적 PMIC ownership 이전은 별도 단계다. |

한 profile에서 UART와 SPI를 동시에 mandatory heartbeat로 만들지 않는다. 초기에는 UART만 지원하고, 향후 선택 옵션 예시인 `soc-link=spi`는 외부 SPI 구현·검증 이후 제공한다. 관리 Ethernet은 선택 기능으로 추가한다. GPIO fault는 data channel과 독립적으로 유지한다. prototype의 AP master SPI를 reference의 MCU master SPI와 같은 배선으로 설명하지 않는다.

### 3.1 향후 CAN·전원 protocol 확장 제안

현재 UART는 [28-byte Safety 계약](si0-safety-channel.md#uart-계약)을 사용한다. 아래 메시지와 framing 대안은 CAN/전원 기능을 추가할 때의 검토 항목이다.

첫 protocol은 고정 header와 길이 제한을 둔다. `version`, `message_type`, `length`, `sender_id`, `boot_epoch`, `sequence`, `payload`, `crc`를 명시하고, byte order·CRC polynomial·최대 payload·sequence wrap 규칙은 구현 전 protocol 파일에서 고정한다. UART는 COBS 등 명시적 framing과 delimiter를 사용하고, SPI는 CS transaction 경계 및 response 지연을 정의한다. C 구조체를 그대로 전송하지 않는다.

| 메시지 | 의미 | 수신 규칙 |
|---|---|---|
| `HELLO / CAPABILITIES` | boot epoch, protocol version, 지원 명령 협상 | reset 뒤 새 세션이 성립하기 전 actuation/전원 변경 요청을 허용하지 않는다. |
| `HEALTH` | workload progress, safety state, last fault, counter | 새 epoch/sequence와 유효한 CRC를 검사한다. 재전송·중복 frame으로 watchdog을 갱신하지 않는다. |
| `POWER_REQUEST / ACK / RESULT` | on/off/reset 요청과 실제 결과 | request ID별 멱등 처리. ACK는 접수일 뿐 동작 완료가 아니다. |
| `FAULT / FAULT_ACK` | fault code, source, latched 상태 | ACK로 fault 조건을 지우지 않는다. clear는 원인 해소와 별도 절차가 필요하다. |
| `VEHICLE_RX / VEHICLE_TX` | CAN channel, ID, flags, DLC, payload | 허용 ID·방향·주기·유효 시간 검사. raw CAN↔SoC 무제한 tunnel은 기본 비활성이다. |

CRC는 우발적 손상 검출이며 인증이 아니다. reset/power/update 명령은 허용 주체와 상태를 검사한다. 외부 차량·원격 simulator까지 신뢰 경계를 넓힐 때는 key/session·재전송 방지·인증을 추가 설계한다. 신뢰된 시험용 SIL Kit RPC를 제품의 인증 경로로 간주하지 않는다.

### 3.2 CAN controller와 CAN network 경계

SIL Kit이 제공하는 것은 CAN frame 서비스다. MCU driver가 접근할 CAN register/FIFO/filter/IRQ는 MCU device model이 제공해야 한다. 초기 기능 모델은 register 호환을 주장하지 않는 frame port를 사용한다. generic MCU firmware는 작은 QVP 전용 CAN controller/HAL로 시작할 수 있지만 vendor driver 호환과 분리해 표시한다. 실제 MCU가 정해지면 해당 controller(TRM 기반)의 Tx/Rx FIFO, filter, interrupt clear, error state, reset semantics를 모델링한다.

Tx 완료는 세 단계로 기록한다: controller queue 접수, simulated bus 전송 완료, 수신 ECU application 처리. 첫 단계에서 완료 IRQ를 발생시키거나 SIL Kit의 positive acknowledgement를 수신 application 응답으로 해석하지 않는다. FD DLC 9~15를 byte 수 9~15로 잘못 처리하지 않도록 ID·flags·DLC↔length 변환을 양방향 검증한다.

## 4. 소스 배치와 Lua 계약

다음은 **목표 경로**이며 현재 존재하는 API가 아니다. 기능이 생기는 단계에만 파일을 추가한다.

| 소유 저장소 | 제안 위치 | 책임 |
|---|---|---|
| `qbox-platform` | `platforms/apollo/board/saturn-v.lua`, `board/hw-block/vmcu.lua` | vMCU 보드 장착 여부, 외부 bus·신호 연결 |
| `qbox-platform` | `platforms/apollo/vp/vmcu.lua` | backend 선택, QemuInstance, firmware loader, quantum, debug |
| `qbox-platform` | `systemc-components/vmcu_functional/`, `board_power_supervisor/` | reference endpoint, 보드 power/reset 동작 |
| `qbox` 또는 우선 `qbox-platform` | `systemc-components/silkit_bridge/` | 범용 frame/time bridge. 처음에는 overlay에서 검증하고 범용 API가 안정되면 core로 이동 |
| `qemu` / `qbox-platform/qemu-components` | 선택 MCU controller / wrapper | register·IRQ device 구현 / SystemC 연결 |
| `cometzero/zephyr_vmcu_src` submodule | `zephyrproject/zephyr_vmcu_src/` | 현재 독립 MCU Zephyr firmware. 초기 `vmcu-firmware/`는 Zephyr 전환 후 제거 |
| `meta-hsoc-bsp`, `meta-hsoc-auto-solutions` | native SIL Kit/bridge, MCU firmware 및 profile metadata | 버전·checksum·license·설치 경로·이미지 manifest |
| root `scripts/test`, `tests`, `doc/vmcu` | runner, protocol/scenario test, 계획·검증 기록 | 전체 조합 및 근거 |

기존 `platform.ap_qemu_inst`, `platform.si_cl0_*`, `platform.board_tps6594` 등의 객체 경로를 보존하고 신규 객체에 `vmcu_`/`board_` prefix를 쓴다. `soc/`에 외부 MCU를 넣거나 기존 SoC 주소 map에 MCU SRAM을 끼워 넣지 않는다. `dofile()`은 현재 파일 기준 literal 경로와 기존 `define/connect` 규칙을 따른다. 옵션 예시 `vmcu_backend=off|functional|qemu|external`는 아직 구현된 CCI/CLI가 아니다.

초기 default는 `off`로 유지하고 기존 Saturn-V profile 회귀를 보장한다. profile이 SPI/UART loopback과 vMCU 연결을 동시에 요구하거나 PMIC writer가 둘이면 실행 전에 configuration error로 거부한다. Linux DT 변경이 필요한 경우 이미 분리된 SoC/QVP/board DT 소유권을 따르고, MCU 추가를 이유로 기존 주소·IRQ를 재할당하지 않는다.

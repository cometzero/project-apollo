# 제어·안전 시나리오와 PMIC 관리

상위 문서: [통합 계획](README.md). 이하 상태·signal·timeout은 Apollo용 제안이며 실물 safety requirement나 인증 결과가 아니다. 현재 구현은 [SI CL0 Safety Channel](si0-safety-channel.md)을 따른다. [CAN과 제어 서비스](can-and-services.md)에 구현한 CAN/PMIC 조회/AP-only power 경계를 기록한다. 아래 전체 SoC rail 시나리오는 후속 목표다.

## 1. 제어 책임과 우선순위

목표 설계에서 vMCU는 차량 CAN 입력을 검증하고 Apollo의 운용 상태를 감독한다. AP watchdog 실패와 SI fault, PMIC fault, 통신 단절은 서로 다른 원인으로 보존한다. Linux userspace의 단순 주기 송신만으로 application progress를 판단하지 않는다. 현재 AP 감시의 원천은 SI CL0의 기존 PFDI다. 별도 AP heartbeat나 합성 workload counter를 추가하지 않는다. AD task 의미 수준의 checkpoint는 향후 요구가 정해질 때 별도로 검토한다.

명령 충돌은 `latched critical fault > 긴급 출력 제한 > 정상 종료 > reset/recovery > 정상 구동 요청` 순으로 처리한다. power request에는 request ID와 deadline이 있고, 같은 요청의 재전송은 rail toggle을 반복하지 않는다. 원인이 계속 남아 있는 fault를 ACK만으로 clear하지 않는다.

| 관찰/제어 | 실행 주체 | 완료 증거 |
|---|---|---|
| AP PFDI health | 기존 AP PFDI → SI CL0 monitor → 5초 Safety UART → vMCU | 실제 코어별 active/online/fault/off, boot epoch/sequence/수신 시각 |
| SI health와 내부 fault | SI CL1/CL0 → 전용 상태 채널 + 독립 fault GPIO | SI 보고와 fault pin 전이를 각각 기록 |
| 차량 CAN Tx 허가 | vMCU policy + controller/transceiver enable 모델 | 허용 ID·주기·freshness, 실제 Tx/Rx trace |
| SoC 내부 AP reset | SI CL0/기존 reset controller, vMCU는 요청 | AP reset assertion, 지정 device 초기화, 재부팅 epoch |
| 외부 SoC reset | 신규 board reset arbiter/supervisor | Apollo reset fanout의 assertion/deassertion; vMCU는 계속 동작 |
| rail 제어 | 기존 PMIC register writer는 SI CL0 | I2C transaction + rail readback; 실제 domain 전이는 별도 증거 |
| vMCU hang 처리 | 독립 supervisor/watchdog | watchdog 만료 후 MCU reset 또는 출력 허가 차단 |

차량 actuator를 직접 구동하는 기능은 이 계획의 기본 범위에 포함하지 않는다. vMCU는 **AD command 전송을 제한하고 별도 차량 안전 controller에 safe-state 요청**을 보낸다. 브레이크·조향·차량 정지 방식은 차량 hazard analysis가 정한다. 이동 중 heartbeat 실패를 이유로 즉시 SoC 전원을 끄는 정책을 기본값으로 두지 않는다.

## 2. 목표 전원 상태 머신 (후속 구현)

| 상태 | 진입 조건 | 허용 동작과 다음 상태 |
|---|---|---|
| `OFF` | SoC supply off, vMCU/AON만 유지 | ignition/wake와 fault latch 확인 후 `POWERING` |
| `POWERING` | 전원 요청 승인 | sequencer에 enable 요청, power-good 대기; 실패 시 reset 유지 및 `FAULT_LATCHED` |
| `BOOT_WAIT` | power-good 안정 후 reset 해제 | RSE/SI/AP boot milestone과 session 협상; timeout은 제한된 recovery |
| `RUN` | SI health 및 필요한 AP service ready | CAN gateway, heartbeat, thermal/power 상태 감시 |
| `DEGRADED` | AP workload/통신 단절, noncritical fault | command 제한, SI 확인, 차량 안전 controller 통보; 정책에 따라 `RECOVERY` 또는 `SHUTDOWN_WAIT` |
| `SHUTDOWN_WAIT` | 승인된 종료 또는 차량 상태 전이 | Linux 종료와 GPIO 완료 대기; deadline 뒤 강제 조치는 원인·차량 상태 정책에 따름 |
| `RECOVERY` | 허용된 reset/restart | 대상 reset, 새 epoch 협상, retry limit 검사; 성공 시 `BOOT_WAIT`, 반복 실패 시 `FAULT_LATCHED` |
| `FAULT_LATCHED` | critical fault, power-good 실패, retry 소진 | 안전 출력 유지, 진단 기록, 명시적 복구 조건 전까지 자동 power toggle 금지 |

`OFF`는 SIL Kit participant 종료를 뜻하지 않는다. vMCU, board supervisor, 차량 network는 유지하고 Apollo domain만 정지한다. vMCU도 전원 상실하는 전체 bench-off는 별도 시나리오다.

## 3. Heartbeat와 시간 계약

SI CL0가 기존 PFDI로 AP를 감시하고 종합 결과를 5초마다 vMCU에 보고한다.
AP 관리 UART의 ping/status는 Safety 판정과 분리한다. 기존 PFDI timeout은
유지하며 vMCU의 유효한 보고 15초 누락은 `LINK_TIMEOUT`, 실제 PFDI 실패는
`PFDI_FAULT`, READY 상태에서 SOC_ERROR edge 1.5초 정지는 `SOC_ERROR_STUCK`이다.
합성 `WORKLOAD_STALLED` 판정은 현재 앱에서 제거했다.

- SI는 자체 timer, vMCU는 STM/Zephyr uptime을 사용한다. sender timestamp를
  서로 동기된 시각으로 취급하지 않는다. 5초/15초/1.5초는 QVP 기능 계약이다.
- CRC 오류, 잘못된 mask/flags, 동일 epoch의 stale sequence와 직전 retired epoch는 deadline을 갱신하지 않는다.
- PFDI fault는 명시적인 restart 준비까지 latch한다. 단순 RPC ACK나 정상 보고만으로 clear하지 않는다.
- 보고 off/on은 정기/상태 전이 보고를 제어하는 진단용이며 PFDI 감시와 GPIO toggle은 계속된다. `monitor off`는 콘솔 출력만 끈다.
- GPIO transport의 host 100 ms snapshot/1초 lease는 연결 관리용이다. firmware heartbeat나 물리 FTTI가 아니다.
- MCU 단독 reset은 SESSION_QUERY와 새 CAN cookie로 재협상한다. 독립 supervisor/watchdog와 공통 virtual-time pause 정책은 후속 범위다.

## 4. Reset 범위와 전기적 의미

| 요청 | reset/유지 대상 | 계획상의 경계 |
|---|---|---|
| AP warm/recovery reset | 정의된 AP CPU·주변장치; SI/RSE/vMCU 유지 여부를 기존 contract에 맞춤 | 현재 AP reset 구현의 retention semantics부터 확인한다. 이름만으로 warm retention을 약속하지 않는다. |
| Apollo 전체 reset | RSE/SI/AP 및 지정 controller | 기존 `reset_targets.lua` 목록을 재사용하되 vMCU/board supervisor 제외 |
| SoC cold power-cycle | Apollo non-retained state, bus master, peripheral state, 필요 memory | power-off isolation, DMA 차단, retention 초기화 및 loader 재시작을 추가 구현해야 한다. |
| vMCU reset | MCU CPU/SRAM policy/CAN queue/로컬 peripherals | Apollo를 자동으로 함께 reset하지 않는다. 출력은 안전 기본값, 재협상 필수 |
| 시험 인프라 stop | QBox/SIL Kit lifecycle | 실제 board reset·PMIC 전원 전이로 집계하지 않는다. |

새 `SOC_RESET_N`을 이미 구동 중인 reset port에 두 번째 driver로 연결하지 않는다. board 요청과 내부 reset 원인을 arbiter에서 합쳐 단일 출력으로 만들고 active-high/low 변환, 최소 assertion 시간, power-good 대기, reset-cause latch를 정의한다. reset 중 DMA/IRQ/event가 이전 epoch로 유입되지 않게 queue를 폐기하거나 명시적으로 drain한다.

## 5. PMIC 소유권: 단계 A를 기본으로 채택

### 5.1 단계 A — SI CL0 단일 owner + vMCU 감독

현재 TPS6594와 `0x48` I2C bus를 유지한다. SI CL0가 기존 PMIC API로 rail 설정과 live fault 상태를 조회하고 vMCU에 응답한다. vMCU에는 이 조회와 AP 복구/종료/전원 상태 명령을 제공한다. generic register read/write를 외부 MCU에 무제한 proxy하지 않는다. 전압·enable 설정은 보존하며 PMIC rail 기반 전원 차단은 미구현이다.

| 자원 | 단일 writer | vMCU의 권한 |
|---|---|---|
| 기존 TPS6594 register/rail 설정 | SI CL0 SCP | 승인된 정책 요청, read-only 상태 수신 |
| SoC 내부 PPU/SCMI | 기존 SI CL0 framework | SI service를 통한 상태/복구 요청 |
| 보드 supply gate·외부 reset | 신규 board supervisor가 신호를 구동, vMCU가 정책 요청 | bounded reset, power-cycle 요청; 자체 fault interlock이 우선 |
| MCU AON supply와 watchdog | 독립 전원/supervisor 모델 | MCU가 자신을 무조건 정상 처리하는 bypass 금지 |

PMIC `int_n`은 현재 SI CL0 GPIO 입력으로 관찰 가능하지만 GIC IRQ 경로는 없다. I2C의 polling 전송 설정은 지속 fault 감시 loop를 의미하지 않는다. **SI의 주기 polling 또는 IRQ fault-monitor service를 신규 구현**하고 vMCU 상태 메시지에 반영한다. 독립 검출이 필요하면 board-level fault fanout/buffer도 명시적으로 모델링한다. 기존 입력을 다른 owner로 옮겨 SI가 fault를 잃게 하지 않는다. `int_n`은 fault 알림이며 power-good 신호와 동일하지 않다.

이 단계에서 SI가 응답하지 않으면 PMIC proxy도 동작하지 않는다. 그러므로 vMCU의 강제 복구 능력을 주장하려면 **SI software와 별개인 board reset/supply-enable 경로**가 필요하다. 아직 이 경로가 없으면 해당 시험은 `UNSUPPORTED`다.

### 5.2 단계 B — 보드 전원 트리 모델 추가

추상 power domain을 `AON_VMCU`, `SOC_MANAGEMENT`, `SOC_AP`, `BOARD_IO`로 나눠 시험할 수 있다. 이는 실제 Saturn-V rail map이 아니다. 현재 TPS6594의 BUCK/LDO 번호를 추측으로 domain에 배정하지 말고 board manifest에 rail→consumer mapping과 retention 정책을 넣는다.

필수 모델은 enable, power-good, reset output, latched fault, restart cause, off-state access isolation이다. PMIC의 rail output을 consumer power state와 연결하고, domain off 시 CPU 진행·DMA/IRQ·MMIO 응답을 어떻게 제한할지 정한다. 단순 CPU pause와 register enable bit 변경만으로 cold-off 완료를 선언하지 않는다.

vMCU가 SoC rail을 끈 뒤에도 실행할 수 있도록 AON supply를 분리한다. SI CL0가 자기 전원을 제거한 뒤 다음 power-on까지 책임지는 순환 의존은 허용하지 않는다. register-level PMIC 모델과 추상 board supervisor가 같은 전원을 각각 독립적으로 결정하지 않도록 한 상태 machine이 최종 enable/reset을 소유한다.

### 5.3 단계 C — PMIC owner를 vMCU로 이전하는 대안

실물 회로도가 vMCU direct I2C/SPI ownership을 요구할 때만 채택한다. 전환 시 SCP의 직접 PMIC driver 경로를 제거/비활성화하고, boot 시 power-ready 의존을 supervisor handshake로 바꾼다. SI가 PMIC ACK를 기다리는데 MCU firmware는 SI boot를 기다리는 deadlock을 방지한다.

두 master가 필요하면 실제 bus mux/arbitration, owner grant, timeout, recovery와 lock handoff를 모델링해야 한다. 현재 I2C bus에 initiator 두 개를 연결하는 것만으로 multi-master ownership이 구현되지는 않는다. 단계 A와 C를 동시에 활성화하지 않는다.

## 6. 전원 시퀀스와 고장 처리

| 순서 | 정상 기동 | 정상 종료 |
|---|---|---|
| 1 | AON MCU/supervisor 기동, fault latch와 ignition 확인 | 차량 상태 확인, 신규 AD command 차단, 종료 request ID 발행 |
| 2 | AON supervisor supply gate 또는 PMIC NVM/autonomous startup으로 초기 rail enable, Apollo reset 유지 | AP workload 정지와 filesystem flush, SI 상태 기록 |
| 3 | power-good 안정 확인 후 Apollo reset 해제 | `SHUTDOWN_DONE` 및 request 결과 대기 |
| 4 | 기존 RSE/SI/AP boot와 PMIC preserve probe 수행 | supervisor가 reset assert, 지정 domain off |
| 5 | 새 epoch·health 협상 후 RUN 허용 | power-good 저하 확인, AON/vMCU 유지, OFF 상태 기록 |

초기 rail enable은 아직 reset 상태인 SI의 I2C write에 의존하지 않는다. SI는 전원·reset 해제 이후 기존 `policy=preserve` probe를 수행한다. 진단을 위해 임의 전압을 쓰거나 기본 enable 값을 실제 Apollo 동작 전압으로 해석하지 않는다. rail 번호·전압·delay는 실제 PMIC variant/NVM과 보드 전원 사양 확보 후 설정한다.

| 고장 | 요구 반응 | 복구 조건 |
|---|---|---|
| AP heartbeat만 중단 | command 제한, SI health 확인, 허용된 AP reset | AP 새 epoch 및 정상 progress 회복 |
| SI/통신 모두 중단 | 독립 fault GPIO 확인, board reset escalation | 제한된 retry 후에도 실패하면 latch |
| PMIC read NACK/timeout | boot 허가 중단, 원인 기록; 무한 재시도 금지 | bus 복구와 유효 status 확인 |
| power-good 미발생/저하 | reset 유지/재assert 및 domain policy 적용 | 안정 상태와 fault 원인 해소 |
| CAN stale/bus-off | 해당 channel의 command 제한, 진단 | controller/network recovery contract 충족 |
| vMCU hang | 외부 watchdog가 출력 허가 차단 또는 MCU reset | MCU self-test/세션 재설정 후에만 재허가 |
| shutdown ACK만 수신, 완료 없음 | ACK를 완료로 취급하지 않고 deadline 처리 | 강제 reset/off 여부는 차량·전원 정책으로 결정 |

CAN transport 단절 시 기능적 bus-off와 명시적 controller restart는 구현했다. 실제 CAN 오류 누적·중재 timing, PMIC watchdog/ESM/PFSM, 전압 ramp/전류·열 특성은 현재 모델로 검증된 항목이 아니다. 필요한 기능 모델과 독립 근거를 추가하기 전까지 `UNSUPPORTED` 또는 `UNVERIFIED`로 남긴다. 이 계획의 safe-state label은 ISO 26262 ASIL 달성이나 FVP/RTL/실차 parity를 뜻하지 않는다.

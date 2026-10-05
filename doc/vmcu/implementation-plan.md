# 구현 순서와 검증 계획

상위 문서: [통합 계획](README.md). P-MIN과 Zephyr app/shell 구현을 완료했다.
P0/P1에는 AP 관리 UART에 더해 **기존 SI CL0 PFDI 결과의 5초 Safety UART와
독립 GPIO/reset arbiter**를 구현했다. 현재 계약과 검증 범위는
[SI CL0 Safety Channel](si0-safety-channel.md)을 따른다. P2 차량 CAN/SIL Kit, P3 MCU CAN driver와 단독 reset 재협상, P4 중 PMIC 조회와 AP-only 종료·wake/복구를 구현했다. 현재 결과는 [CAN과 제어 서비스](can-and-services.md)를 따른다. P4의 PMIC rail 기반 cold-off와 P5 정밀화는 PLANNED다.

## 1. 순서와 완료 조건

| 단계 | 구현 범위 | 선행 조건 | 완료 증거 |
|---|---|---|---|
| P-MIN 최소 MCU | 현재 QEMU에 TC397 CPU0·memory·IR·STM·ASCLIN, 독립 bare-metal probe | 공개 fork pinned source, TriCore GCC | 현재 source 빌드, ELF boot, timer ISR, UART RX/WAIT·TX, mask/priority, reset 후 반복, 기존 ISA 회귀 |
| P0 계약 고정 | board/vMCU 역할, UART protocol, signal polarity, reset scope, PMIC owner, fixture 시간값 | 현재 source map | 충돌 없는 manifest, protocol test vector, 기존 profile의 topology 차이 설명 |
| P1 board 연결·제어 | TC397 firmware backend, AP UART opt-in 연결, SI control UART extension, GPIO fault/reset arbiter | P0, 신규 SI 주소/IRQ map review | AP health stall와 SI health 분리, GPIO stuck/drop, AP reset 동안 vMCU counter 지속 |
| P2 차량 SIL 기능 | CAN frame endpoint와 SIL Kit bridge, restbus, trace | P1, core/adapter 버전 pin | 양방향 CAN/FD frame, filter·DLC·queue 오류, gateway allowlist, disconnect 처리 |
| P3 MCU firmware | 최소 TC397 기반 RTOS 평가, Zephyr/toolchain pin, UART HAL, 필요한 CAN frontend | P-MIN, protocol fixture | RTOS의 UART·timer ISR, 후속 CAN MMIO→IRQ→ISR, reset 후 재협상 |
| P4 보드 전원 | PMIC proxy, AON supervisor, rail→domain mapping, off-state isolation, power-good/reset sequencing | P1, board manifest; 실물 mapping은 회로도 필요 | AP reset/SoC reset/cold-off 분리 증거, vMCU AON 유지, NACK/PGOOD fault 및 반복 recovery 제한 |
| P5 정밀화 | TriCore libqemu 내부 통합 평가, SPI 외부 bus/slave, virtual-time profile, detailed CAN | 외부 PoC 결과 및 해당 모델/TRM | 각 기능의 driver traffic·시간 오차·고장 주입 결과; 미지원 항목 보존 |

P2와 P3는 P1 계약 이후 병렬 개발이 가능하지만 shared BitBake build는 직렬 실행한다. AP-only power-off는 실제 AP core power-domain OFF 확인을 요구한다. PMIC rail/SoC 전체 cold-off는 별도 미지원으로 남긴다. P5의 SPI는 현재 loopback에 socket 한 줄을 추가하는 작업이 아니며 CS/mode/full-duplex/시간·DMA·slave 역할의 별도 모델 설계가 필요하다.

## 2. 1차 구현의 구체적 선택

- 현재 구현 backend는 별도 process의 TC397 firmware이며 Lua profile 기본값은 `off`이며 interactive BSP launcher가 자동 활성화한다. 공개 TC397 최소 모델을 확보했으므로 중복 SystemC heartbeat 모델 대신 실제 firmware와 공유 codec/policy unit test를 사용한다. 추가 기능 모델은 필요한 단계에서 도입한다.
- AP 제어 bring-up은 기존 UART byte 경로를 opt-in으로 사용하고, SI 감독 채널은 QVP PL011 `0x2a820000`/INTID41, 독립 PL061 `0x2a830000`/INTID42를 사용한다. 기존 PFDI 감시기를 재사용하며 보고 주기는 5초다.
- vMCU↔차량은 CAN 프레임부터 SIL Kit에 연결한다. 실제 MCU M_CAN driver와 native SIL Kit participant의 왕복을 검증한다. host SocketCAN adapter는 필수 의존성이 아니다.
- 기존 PMIC owner는 SI CL0로 유지한다. 초기 정상 boot의 preserve probe를 회귀 검사하고, rail voltage 재설정은 포함하지 않는다.
- AP reset 요청부터 구현하되 기존 controller에 board request를 중재한다. Apollo 전체 reset과 cold power-cycle은 domain coverage가 갖춰진 다음 활성화한다.
- firmware backend는 공개 fork의 최소 기능을 현재 QEMU에 이식한 TC397 독립 실행을 사용한다. 현재 기본 firmware는 독립 upstream Zephyr의 app/shell이며 bare-metal probe는 모델 회귀 시험으로 유지한다. AUTOSAR/vendor firmware는 후속이다. generic Arm은 대안으로 유지한다. TC397 machine 존재와 vendor binary 호환은 별도이며, 현재 RH850 backend는 없다.

## 3. 검증 매트릭스

| ID | 자극 | 필수 관찰/합격 조건 | 실패·미지원 구분 |
|---|---|---|---|
| BASE-01 | vMCU off, 기존 Saturn-V 실행 | 기존 map/부팅/PMIC probe와 loopback 회귀 결과 유지 | 이전 소스의 PASS를 재사용하지 않음 |
| BOOT-01 | ignition→power-on→boot | reset 순서, power-ready, RSE/SI/AP milestone, epoch 협상 | 모델 없는 rail 전이는 `UNSUPPORTED` |
| HB-01 | 기존 AP PFDI agent 정지 | 기존 SI PFDI online timeout → fault snapshot → MCU DEGRADED, SI/MCU 생존 | AP 합성 counter를 실제 health로 대체하지 않음; CAN 출력 제어는 후속 |
| HB-02 | SI health 단절·GPIO fault | AP 관리 UART와 무관하게 fault 검출, 원인 보존 | UART drop과 MCU/SoC crash 구분 |
| LINK-01 | CRC 오류·중복·순서 역전·이전 epoch frame | watchdog 갱신 안 됨, 요청 중복 실행 없음 | 정상 stale frame을 새 session으로 수용하면 FAIL |
| RESET-01 | AP reset | vMCU timer/CAN/supervisor 지속, AP epoch만 변경 | vMCU가 함께 reset되면 FAIL |
| RESET-02 | Apollo 전체 reset | RSE/SI/AP 재부팅, vMCU는 생존, queue stale frame 차단 | 프로세스 재시작으로 대체하면 `NOT_COMPARABLE` |
| MCU-01 | MCU CPU stall/reset | 독립 watchdog가 출력 제한, 재부팅 후 재협상 | QBox 전체 pause로 대체 불가 |
| CAN-01 | classic/FD·표준/확장 ID 양방향 traffic | payload/DLC/flags 보존, Tx 완료와 Rx IRQ/ISR 관찰 | frame-only backend는 driver 항목 `SKIP` |
| CAN-02 | overload/filter/금지 ID·stale command | bounded queue, overrun 기록, 금지 traffic 차단 | silent drop·무제한 queue는 FAIL |
| CAN-03 | arbitration/error/bus-off/recovery | 상세 모델에서 지정 상태 전이·복구 관찰 | simple CAN/vcan만 있으면 `UNSUPPORTED` |
| PMIC-01 | 정상 boot | 기존 read-only preserve 정책, expected probe, SI owner 유지 | readback만으로 power 기능 PASS 금지 |
| PMIC-02 | I2C NACK/timeout, fault 알림 | boot gate·latched 원인, 무한 retry 없음 | polling과 IRQ delivery 결과 별도 |
| POWER-01 | shutdown→rail-off→wake | GPIO 완료, PGOOD, reset, CPU/DMA 정지·retention 초기화·재부팅 | register enable bit만 바뀌면 FAIL 또는 미구현 |
| POWER-02 | SI hang 상태에서 board reset/off | 독립 supervisor가 동작, AON MCU 생존 | SI proxy만 있으면 `UNSUPPORTED` |
| TIME-01 | 동일 seed/입력 3회 반복 | causal event 순서 동일, 시간 오차가 설정 bound 이하 | wall-clock log만 있으면 `NOT_COMPARABLE` |
| HOST-01 | adapter/participant crash | bounded shutdown와 증거 보존, infrastructure failure 분류 | guest watchdog PASS로 집계하지 않음 |

runtime 증거는 `build/qbox-apollo-qvp/vmcu-<timestamp>/` 아래에 모은다. 제안 artifact는 `manifest.json`(SHA/config/firmware hash/version), `events.jsonl`(simulation time/domain/epoch/cause), `can-trace`, UART·firmware logs, reset/rail trace, `results.json`이다. 각 결과는 `PASS`, `FAIL`, `SKIP`, `UNSUPPORTED`, `NOT_COMPARABLE`과 이유를 가진다. `PLANNED`는 실행하지 않은 계획 상태다.

event timeline에서 최소한 `fault 발생 → 검출 → policy 결정 → reset/출력 → 상대 관측`을 연결한다. API return이나 console 문자열 하나만으로 전체 시나리오를 PASS 처리하지 않는다. CAN/PMIC device reset 후 outstanding callback, DMA, interrupt가 재진입하는 경우도 확인한다.

## 4. 기존 검증·빌드 경로 활용

현재 script를 먼저 재사용한다. 실제 옵션은 해당 시점 `--help`와 code를 확인하고 신규 scenario만 추가한다.

| 현재 파일 | 활용 |
|---|---|
| [validate_qbox_apollo_fvp_full_map.py](../../scripts/test/validate_qbox_apollo_fvp_full_map.py) | QVP SI UART extension, board object 추가 시 주소·기존 map 회귀 |
| [verify_qbox_si_pmic.py](../../scripts/test/verify_qbox_si_pmic.py), [guest helper](../../scripts/test/verify_qbox_si_pmic_guest.sh) | PMIC 기본 probe/readback 판정과 신규 power evidence 분리 |
| [test_qbox_si_pmic_validation.py](../../tests/test_qbox_si_pmic_validation.py) | log parser 및 판정 회귀 |
| [run_qbox_apollo_fvp_full.py](../../scripts/run/run_qbox_apollo_fvp_full.py) | canonical full-system runner, 실제 지원 옵션에 scenario 추가 |
| [yocto_build.sh](../../yocto_build.sh) | 좁은 native component build와 최종 이미지 build |

구현 후 관련 component test부터 실행하고, `qbox-apollo-qvp-native` 및 firmware/provider의 실제 task·deploy 경로를 확인한다. native build 성공과 target MCU firmware 실행을 구분한다. `./run_qbox_yocto.sh`의 boot/login만으로 post-login qualification을 대신하지 않으며 canonical runner의 `--conf`와 해당 시점의 qualification 옵션을 사용한다.

TC397 최소 모델, MCU protocol, full-system AP UART heartbeat의 build/guest runtime를 실행했다. 결과 범위는 위 구현 문서로 제한하며 기존 전체 qualification의 잔여 실패를 새 기능 때문에 사라진 것으로 처리하지 않는다. `qbox-platform/platforms/apollo/README.md`와 root `doc/qbox-fvp-emulation-project.md`에도 연결 방식과 한계를 반영한다.

## 5. 설계 검토 시 닫아야 할 항목

| 항목 | 기본 결정 | 외부 자료가 필요한 부분 |
|---|---|---|
| 실물 MCU | TC397 fork 우선 PoC, generic Arm 대안 | 정확한 part/revision, TRM, vendor firmware/license와 미구현 peripheral |
| board wiring | UART QVP extension + 독립 signal | 실물 SPI role/pinmux, Ethernet switch/VLAN, CAN transceiver, reset polarity |
| power tree | SI CL0 PMIC owner 유지 | AON supply, rail→consumer, PMIC variant/NVM, min pulse/ramp/PGOOD |
| 안전 정책 | 출력 제한과 제한된 recovery fixture | 차량 상태별 safe action, FTTI, reset/off 허용 조건 |
| 차량 통신 | 단일 CAN network fixture | DBC/ARXML, ID 소유권, 진단/update, E2E·인증 요구 |
| 시간 정확도 | 비동기 traffic와 동기 deadline 분리 | 허용 오차, 상세 CAN simulator, FVP/HIL 비교 요구 |

위 항목이 미정이어도 P0~P3의 기능 계약과 가상 firmware 검증은 가능하다. 실물 회로·전원·safety parity에 관한 결론은 해당 자료와 검증이 확보될 때까지 보류한다.

# TC397 master SPI와 Apollo GPIO 요청: 조사 및 결정

조사일: 2026-10-15. 상태: **설계 결정 / 구현 및 통합 검증 중**.
사용자 요구는 TC397이 SPI master이며 Apollo가 GPIO를 토글하여 통신을
요청하는 것이다. 이 문서는 기존 Apollo-master PoC 제안을 대체한다.
조사 당시 실행 경로는 UART/GPIO/CAN이었다. 후속 SPI 구현과 실제 검증 상태는
[SPI 구현 기록](spi-implementation.md)에 분리하여 기록한다.
실행 단계와 검증 조건은 [직접 socket SPI 구현 계획](spi-implementation-plan.md)을 따른다.

## 1. 결정

**첫 구현은 QBox–TC397 QEMU 간 직접 socket을 사용하는 트랜잭션 수준 SPI
bus로 한다. SIL Kit SPI adapter는 초기 필수 경로에 넣지 않는다.**

- TC397 QSPI가 SCLK/CS와 모든 SPI 전송을 소유한다.
- Apollo는 slave TX 데이터를 준비하고 전용 `SOC_SPI_REQ`를 토글한다.
- 안전 채널의 slave 소유자는 SI CL0를 권장한다. AP-only OFF/reset에서도
  유지되어야 하므로 기존 AP DW SSI를 그대로 사용하지 않는다.
- slave IP/register 계약, SI MMIO/IRQ, board pin 번호는 구현 전 고정한다.
  현재 실물 대응은 `UNVERIFIED`이며 임의 주소를 실물 사양으로 선언하지 않는다.
- 외부 프레임은 loopback TCP 전용 endpoint로 운반한다. UART 및 GPIO와
  endpoint를 분리하고 기존 supervisor의 동적 포트·수명 관리 패턴을 재사용한다.
- CAN은 기존 SIL Kit 경로를 유지한다. SPI 모델은 transport와 분리하되,
  아직 필요하지 않은 복수 backend/plugin framework는 만들지 않는다.

## 2. SIL Kit 조사 결과

공식 문서가 표시한 SIL Kit 버전은 5.0.7이다. QEMU adapter는 조사 시점
`main`의 `172d6444614f976c3551dd7664a891311cc9d338`을 확인했다.

| 근거 | 확인 결과 | 판단 |
|---|---|---|
| [공식 서비스 목록](https://vectorgrp.github.io/sil-kit-docs/api/api.html) | CAN/LIN/FlexRay/Ethernet 및 generic Pub/Sub/RPC | SPI controller API는 목록에 없음 |
| [Network Simulator](https://vectorgrp.github.io/sil-kit-docs/api/netsim.html) | `SimulatedNetworkType`은 Undefined/CAN/LIN/Ethernet/FlexRay | SPI를 enum 하나로 선택할 수 없음 |
| [QEMU adapter 예제](https://github.com/vectorgrp/sil-kit-adapters-qemu/blob/172d6444614f976c3551dd7664a891311cc9d338/chardev/README.md) | SPI라는 표현을 쓰지만 예제 device는 `isa-serial`, guest는 `ttyS1` | SPI controller/CS/full-duplex 모델의 증거가 아님 |
| [QEMU adapter 코드](https://github.com/vectorgrp/sil-kit-adapters-qemu/blob/172d6444614f976c3551dd7664a891311cc9d338/adapter/SilKitAdapterQemu.cpp) | `SocketToBytesPubSubAdapter` 생성 | byte transport이며 SPI 의미는 양쪽 모델이 구현해야 함 |
| [RPC API](https://vectorgrp.github.io/sil-kit-docs/api/services/rpc.html) | 비동기 Call, 나중의 SubmitResult, timeout | custom SPI 요청/응답 transport 후보. SPI 버스 의미는 제공하지 않음 |

따라서 “공식 SPI bus adapter를 붙이면 된다”는 결론은 성립하지 않는다.
SIL Kit을 쓰더라도 controller, CS 수명, MISO 준비 시점, FIFO/IRQ, reset과
stale completion 처리는 직접 구현해야 한다.

| 기준 | 직접 SPI socket — 채택 | SIL Kit custom SPI adapter — 보류 |
|---|---|---|
| controller 구현량 | QSPI master와 SI slave 필요 | 동일하게 필요 |
| 연결 구조 | 두 emulator의 전용 endpoint | 양쪽 adapter와 participant/registry 관리 추가 |
| SPI 의미 | 프로젝트 transaction 계약 | 같은 계약을 RPC/PubSub에 정의 |
| 적용 이점 | 현재 1:1 보드 내부 링크에 적합 | 외부 SIL 도구/분산 participant가 직접 SPI에 참여할 때 유용 |
| 시간 보장 | 별도 동기화 필요 | SIL Kit 사용만으로 QEMU/SystemC 시간이 동기화되지 않음 |

외부 simulator 또는 CANoe가 SPI endpoint 자체에 참여해야 하는 요구가 생기면
동일 계약을 SIL Kit RPC로 운반하는 adapter를 재검토한다. 이 경우에도 timeout
뒤 원격 실행 여부 불명확, 중복 호출, endpoint cardinality를 별도로 처리한다.
비교는 기능·코드 구조 조사이며 latency/throughput 측정 결과가 아니다.

## 3. 현재 소스의 공백

조사한 checkout: QEMU `6e1b44ec5d6e`, QBox `4661b9abb234`,
qbox-platform `e0ec5c2c253f`. 세 저장소에 조사 당시 local 변경은 없었다.

| 영역 | 현재 소스 | 필요한 변경 |
|---|---|---|
| TC397 machine | [tc397.c](../../hsoc-stack/tools/qemu/hw/tricore/tc397.c): ASCLIN 3개, PORT0, M_CAN, STM | QSPI master MMIO/FIFO/CS/IRQ와 device wiring |
| TC397 GPIO | [tricore_port.c](../../hsoc-stack/tools/qemu/hw/gpio/tricore_port.c): GP8 수신을 PORT IN에 반영 | 요청 pin 입력. 현재 machine에 ERU→CPU IRQ 연결은 없음 |
| MCU firmware | [drivers](../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/drivers) | Zephyr QSPI driver, 요청 감지, protocol worker |
| QBox DW SSI | [header](../../hsoc-stack/tools/qbox/systemc-components/spi/dw-apb-ssi/include/dw-apb-ssi.h), [source](../../hsoc-stack/tools/qbox/systemc-components/spi/dw-apb-ssi/src/dw-apb-ssi.cc) | 현재 MMIO/FIFO/내부 SRL loopback. 외부 slave bus ingress가 없음 |
| Apollo AP driver | [spi-dw-core.c](../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw-core.c) | `spi_alloc_host()` 경로이며 기존 driver를 slave로 선언할 수 없음 |
| GPIO bridge | [vmcu_gpio_bridge.h](../../hsoc-stack/tools/qbox-platform/systemc-components/vmcu_gpio_bridge/include/vmcu_gpio_bridge.h) | SoC mask `0x07` 고정. 새 요청 pin/mask/binding/호환성 검사 필요 |
| QEMU SSI | [ssi.h](../../hsoc-stack/tools/qemu/include/hw/ssi/ssi.h), [ssi.c](../../hsoc-stack/tools/qemu/hw/ssi/ssi.c) | `ssi_transfer()`가 즉시 반환. 원격 응답을 기다리는 blocking call로 감싸지 않음 |

SI memory map의 Local QSPI Flash 영역은 외부 MCU용 slave라는 근거가 아니다.
slave는 AP peripheral을 SI 주소에 단순 alias하는 대신 SI 수명·IRQ·reset을
갖는 기능 모델로 정의한다. IP 선택은 별도 register 계약 검토가 필요하다.

Infineon [TC3xx QSPI 설명](https://documentation.infineon.com/aurixtc3xx/docs/isf1702560910053)은
master/slave, full-duplex, TX/RX FIFO와 interrupt를 명시한다. `Q`는 Queued이며
이번 기본 연결은 SCLK/MOSI/MISO/CS의 single-data-line SPI다. TC397 register
구현 시 해당 derivative의 UM/address/SRC를 확인하고 지원하지 않는 mode는
명시적으로 제한한다. 이 일반 설명만으로 TC397 pin 번호를 고정하지 않는다.

## 4. GPIO 요청 계약

짧은 high→low pulse 대신 **acknowledgement까지 유지하는 toggle bit**를 사용한다.
현재 GPIO bridge는 최종 level과 100ms 반복 snapshot을 운반하므로 짧은 pulse나
연속 두 번의 toggle을 MCU가 관찰한다는 보장이 없다.

1. SI firmware가 TX frame을 준비·publish하고 pending sequence를 기록한다.
2. `SOC_SPI_REQ` level을 한 번 반전하고 ACK까지 그대로 유지한다.
3. TC397 firmware가 이전에 처리한 level과 다른 값을 감지하면 전송을 시작한다.
4. TC397이 CS를 assert하고 clock을 발생시켜 Apollo frame을 읽는다.
5. 수신·CRC·sequence 확인 후 후속 SPI transaction으로 ACK(sequence)를 보낸다.
6. SI가 ACK를 처리한 뒤 다음 pending frame에 대해 다시 toggle한다.

pending 중에는 다시 toggle하지 않는다. 추가 요청은 bounded queue에 보관하고
overflow를 노출한다. 초기 기능 PoC는 PORT IN polling으로 요청을 감지한다.
interrupt 기반 처리는 실제 TC397 ERU/SRC 경로와 firmware driver를 구현한 뒤
별도 검증한다. 기존 PORT 입력 수신을 interrupt 검증으로 분류하지 않는다.

요청 pin은 기존 SOC_ERROR/reset/wake와 별도로 배정한다. PL061/PORT0의 빈 pin은
후보일 뿐 현재 bridge가 이를 지원하지 않으며 실물 pinmux 대응도 미확정이다.

MCU 재시작/재연결 때는 최초 관측 level을 새 요청으로 무조건 처리하거나 무시하지
않는다. MCU master가 명시적으로 SYNC/상태 조회하여 SI epoch, pending sequence와
ACK cursor를 복구한다. timeout은 toggle을 반복하는 대신 상태 조회/동일 sequence
확인으로 처리하며 같은 업무 명령을 두 번 실행하지 않는다.

## 5. SPI bus와 firmware protocol

SPI 요청은 TC397→QBox, 완료/MISO는 QBox→TC397이다. Apollo→MCU 데이터도
TC397이 clock을 발생시킬 때만 이동한다. GPIO는 데이터가 있다는 알림이다.

전용 socket record는 version/length, connection epoch, transaction ID,
CS 및 BEGIN/CONTINUE/END, CPOL/CPHA, word width/bit order, SCLK 설정,
bounded MOSI words를 포함한다. 응답에는 동일 ID, MISO words와 transport 결과를
담는다. 정확한 byte layout은 구현 전 codec/vector로 고정한다.

- 하나의 CS 구간을 여러 bounded chunk로 나눌 수 있게 한다. TCP recv 경계는
  transaction/CS 경계가 아니다. 첫 profile은 1 master/1 slave/1 CS로 제한한다.
- firmware의 TX FIFO에 이미 준비된 데이터가 MISO로 나간다. 전체 명령을 받은 뒤
  계산한 결과를 같은 transaction의 앞부분으로 소급하여 반환하지 않는다.
- RX command에 대한 application reply는 다음 transaction에서 읽는다. GPIO 요청은
  reply 준비 후에만 발생한다. 초기 transfer 크기는 양쪽이 사전 준비할 수 있는
  FIFO 용량과 protocol framing에서 정하고, 무제한 host buffer로 FIFO를 숨기지 않는다.
- remote socket 완료와 guest protocol ACK는 별개다. SPI 자체에는 CAN ACK 같은
  bus ACK가 없다. 연결 단절은 harness/transport fault이며 성공 완료로 대체하지 않는다.
- mode/CS/length 오류, RX overflow, TX underrun의 guest 동작은 선택한 controller
  계약을 따른다. mode mismatch를 실제 bit corruption 재현이라고 주장하지 않는다.
- GPIO와 SPI는 별도 socket이므로 cross-socket 순서를 가정하지 않는다. SI가 TX
  준비를 완료한 후 request level을 갱신하고 epoch/sequence로 reset 경쟁을 판별한다.

QEMU MMIO handler는 FIFO에 넣고 반환한다. 전송 상태 머신이 요청을 발행하고,
QEMU owner context의 비동기 완료에서 RX FIFO/상태/IRQ를 갱신한다. QBox도 수신
payload를 소유 queue로 옮긴 뒤 SystemC 문맥에서 slave FIFO를 처리한다.
socket thread가 직접 SystemC `wait()` 또는 QEMU register를 호출하지 않는다.
QEMU BQL/SystemC 실행 thread에서 peer 응답을 blocking wait하지 않는다.

한 번에 한 remote chunk를 진행하는 bounded 설계로 시작한다. reset/disconnect는
generation을 바꾸고 outstanding chunk와 CS를 취소하며 늦은 완료를 폐기한다.
wire transfer는 중복 실행하지 않는다. 재시도 가능한 application 명령은 별도
sequence/cache 계약으로 다룬다.

시간은 비동기 기능 수준이다. SCLK 기반 nominal duration을 모델링하더라도 host
왕복 시간이 물리 clock stretching으로 바뀌는 것은 아니다. 독립 emulator clock에서
연속 SCLK, setup/hold, 정확한 IRQ latency/FTTI는 `UNVERIFIED`다. 단일 SSI API의
동기 반환을 보존하려고 전체 emulator를 멈추는 방식은 채택하지 않는다.

## 6. 구현 순서와 통과 조건

| 순서 | 책임 저장소/영역 | 필요한 검증 |
|---|---|---|
| 1 | root 계약, QEMU/QBox controller 명세 | SI slave IP/register/주소/IRQ/reset, TC397 QSPI instance/SRC, 요청 pin과 지원 mode 고정 |
| 2 | QEMU `hw/ssi` 및 `hw/tricore` | guest MMIO로 QSPI FIFO/CS/RX/TX/IRQ/reset, remote timeout/late completion |
| 3 | QBox reusable SPI component, qbox-platform SI extension | slave preload/clocked RX/TX/FIFO 오류/CS 유지, SI 수명, 기존 AP SSI 회귀 |
| 4 | GPIO bridge, TC397 PORT, SCP/Zephyr | preload→toggle→MCU 감지→SPI read→ACK, pending 중 추가 요청, 재연결/MCU reset 복구 |
| 5 | supervisor, Yocto, 검증기 | per-run endpoint/cleanup, 필수 peer 실패 처리, firmware/provider 배포 |
| 6 | full-system guest traffic | UART와 동일 PFDI/RPC 의미, AP OFF 중 SPI 유지, AP reset과 SI reset 구분, CAN/UART/GPIO 회귀 |

필수 fault case: CS 중 reset, stale completion, 분할/합쳐진 socket frame, 잘못된
길이/CS/mode, FIFO overflow/underrun, ACK 전 중복 요청, MCU-only reset,
SPI/GPIO 한쪽 단절, peer pause, queue 포화. UART safety를 SPI로 전환하는 profile은
검증 후 추가하고 두 채널을 동시에 필수 heartbeat로 만들지 않는다.

이번 변경은 조사·문서 정리뿐이다. 소스 경로/문서 링크/공백을 검사하며 새 모델,
driver, 빌드, runtime 시험, 성능 비교는 수행하지 않았다.

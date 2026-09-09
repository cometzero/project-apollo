# Apollo QVP Board 구성과 Transactor 설계

작성일: 2026-09-08

실제 board component 구현과 시험 명령은 [PCA9539 검증](pca9539.md)을 참조한다.
PMIC 추가 구성은 [TPS6594-Q1 검증](tps6594.md)을 참조한다.
AP pin bank와 pinmux 구성은 [HSOC GPIO / pinctrl](hsoc-gpio.md)을 참조한다.

이 문서는 Apollo QVP/QBox의 SoC port에 board-level component를 연결하고,
Linux의 GPIO·I2C·SPI·UART 제어가 해당 component의 동작으로 전달되도록
구성하는 방법을 제안한다. 개별 부품의 register 사양보다 모델의 책임,
인터페이스, 배선, 실행 순서에 초점을 둔다.

아래 설계는 구현 제안이다. `soc_ports`, `i2c_bus`, frontend/backend 등의
이름은 논리적 구분을 설명하기 위한 것이며, 모두 현재 제공되는 API나
구현된 component를 의미하지는 않는다.

## 1. 기본 구성 원칙

**SoC는 controller와 외부 port를 제공하고, board는 배선을 정의하며,
component는 입력에 따른 자신의 동작을 책임진다.**

| 계층 | 책임 | 포함할 내용 |
| --- | --- | --- |
| SoC | CPU에서 접근하는 하드웨어 | GPIO/I2C/SPI/UART controller, MMIO, GIC 연결 |
| Board | 부품 배치와 배선 | bus 연결, 장치 주소, GPIO pin 연결, pull-up/down, reset net |
| Component | 부품 고유 동작 | register, 상태 머신, reset 효과, IRQ 출력 |
| Test harness | 자극과 관찰 | Linux 명령, 외부 입력 주입, 결과 검사 |

Board의 I2C 장치에 AP MMIO 주소를 별도로 할당하지 않는다. I2C 장치는
bus segment와 I2C 주소, SPI 장치는 bus와 CS, GPIO 입력은 연결된 net으로
식별한다. CPU가 접근하는 MMIO는 SoC controller의 책임이다.

현재 [ros.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua)는
controller 생성과 EEPROM 연결, UART pair 연결을 함께 처리한다. 첫 단계는
이러한 외부 연결을 board 구성으로 옮기는 것이다. 기존
`platform.ap_dw_i2c_0` 등의 CCI 경로는 유지하면서, Lua의 작은 `soc_ports`
인터페이스를 통해 board가 연결 대상을 받도록 구성할 수 있다.

## 2. Control이 전달되는 경로

I2C GPIO expander가 다른 장치의 reset을 제어하는 경우의 경로는 다음과 같다.

1. Linux가 SoC I2C controller의 MMIO register에 쓴다.
2. Controller 모델이 I2C transaction을 발생시킨다.
3. I2C bus가 expander를 선택해 transaction을 전달한다.
4. Expander 모델이 register write를 해석하고 GPIO 출력을 변경한다.
5. Board의 GPIO 연결이 대상 component의 reset 입력으로 전달한다.
6. 대상 모델이 reset 상태로 전환한다.
7. 이후 대상에 대한 I2C 요청은 변경된 상태에 따라 처리된다.

Board manager가 이 순서를 대신 실행하거나 Linux의 의도를 추측해서 대상
장치를 직접 초기화하지 않는다. 실제 controller·bus·신호 경로를 통해
동작이 이어져야 driver의 제어 순서를 검증할 수 있다.

## 3. 인터페이스별 구성

### I2C

현재 [DWC I2C 구현](../../hsoc-stack/tools/qbox/systemc-components/i2c/include/dw-apb-i2c.h)은
controller와 EEPROM을 직접 연결한다. TLM payload 주소는 I2C 장치 주소이고,
데이터는 바이트 단위로 전달된다.

여러 board 장치를 연결하려면 controller와 target 사이에 공유 bus 모델을
두는 것이 좋다. Bus의 책임은 다음과 같다.

- START/address 단계에서 target 선택 및 transaction 상태 유지
- repeated START와 STOP 처리
- 미연결·응답 불가 장치의 NACK 전달
- 동일 bus segment의 주소 충돌 검사
- controller abort에 따른 진행 중 transaction 정리

장치 내부 register 주소와 데이터의 해석은 target 모델이 수행한다. Bus가
부품별 register 폭이나 의미를 알도록 만들지 않는다. ACK/NACK의 프로토콜
표현은 인터페이스가 처리하되, 현재 장치 상태에서 응답할 수 있는지는 장치
모델이 결정한다.

`dw_i2c_extension`은 여러 controller와 target을 연결할 때 controller에
종속되지 않는 공통 transaction 계약으로 분리하는 것이 좋다. START,
address, repeated START, STOP, abort의 의미를 명시하고, 동적 주소 변경은
진행 중 transaction의 target 선택을 깨뜨리지 않도록 처리한다.

초기 범위는 단일 controller와 여러 target으로 제한할 수 있다.
Multi-controller arbitration이나 SCL/SDA 전기적 동작은 검증 필요성이
생겼을 때 확장한다.

### GPIO

단일 push-pull 출력에서 단일 입력으로 연결하는 reset/enable은 기존
`InitiatorSignalSocket<bool>`과 `TargetSignalSocket<bool>`을 재사용한다.

방향 전환이나 open-drain까지 다루려면 출력값과 구동 상태를 구분해야 한다.

- 출력 HIGH/LOW
- 입력 모드에 따른 출력 구동 해제
- open-drain의 LOW 구동과 release
- pull-up/down에 의해 결정되는 실제 입력 level

입력 모드를 단순 LOW로 취급하면 reset이나 interrupt가 잘못 동작한다.
필요한 net에 output-enable과 level resolution을 추가하고, polarity 변환은
한 경계에서만 수행한다. 단순 일대일 신호에 불필요한 resolver를 추가할
필요는 없다.

현재 [PL061 wrapper](../../hsoc-stack/tools/qbox/qemu-components/gpio/qemu_pl061/include/qemu_pl061.h)는
GPIO 입력·출력 소켓을 제공한다. 일반적인 board pad 연결에는 GPIO 방향
변경의 전달 경로도 확인·보완해야 한다. 또한 Linux에서 접근 가능한 GPIO와
AP 전용 GPIO는 구분하고, SMD/RSE 등 다른 domain과의 소유권을 확인해야 한다.

### SPI와 UART

SPI 외부 장치를 위해서는 CS 선택과 양방향 frame 전송을 지원하는
인터페이스가 필요하다. 현재 SSI의 내부 loopback 기능만으로 외부 target
연결을 대신할 수는 없다.

UART는 기존 `biflow_socket`을 재사용하고, 현재의 pair 연결을 board 배선으로
옮기는 방식으로 시작할 수 있다.

## 4. Reset과 실행 컨텍스트

대상 component가 reset에 따른 상태 전이를 소유한다.

| 입력/상태 | 모델의 처리 |
| --- | --- |
| Reset assert | 진행 중 작업 취소, volatile 상태 초기화, IRQ 정리 |
| Reset release | 준비 지연 시작 |
| 준비 완료 | 정상 통신 허용 |
| 준비 전 접근 | 장치의 인터페이스 계약에 따른 응답 |

지연은 SystemC event/process로 처리한다. Reset 전에 예약된 작업이 나중에
실행되지 않도록 event 취소 또는 generation 검사를 적용한다. 비휘발성
내용의 유지 여부는 해당 장치 모델의 책임이다.

현재 [TargetSignalSocket](../../hsoc-stack/tools/qbox/systemc-components/common/include/ports/target-signal-socket.h)의
callback은 동일한 값의 write에도 호출된다. Edge가 중요한 모델은 이전
상태를 비교하거나 반복 호출에 안전하게 구현해야 한다.

SoC warm reset과 board power-on reset도 구분한다. 외부 장치는 실제 reset
배선과 전원 상태에 따라 동작해야 하며, SoC reset을 모든 board 장치에
무조건 fanout하지 않는다.

QEMU와 SystemC 사이에는 기존
[QemuInitiatorSignalSocket](../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-initiator-signal-socket.h)
등을 재사용한다. 이 계층이 실행 컨텍스트 전환과 QEMU lock 처리를 담당한다.
Board 모델이 임의의 host thread에서 QEMU 내부 GPIO를 직접 조작하도록
구성하지 않는다.

## 5. Xtor/Transactor와의 관계

Xtor는 주로 인터페이스를 통해 transaction을 주고받도록 하는 부분을
가리킨다. Device model은 장치 고유의 상태와 동작을 소유한다. 제공되는
패키지에 따라 두 역할이 함께 묶일 수 있으므로, 이름보다 실제 API와 책임을
기준으로 구분해야 한다.

Synopsys 공개 자료에서는 다음 두 구성을 확인할 수 있다.

- 순수 VDK: I2C controller에 device TLM을 연결하거나 generic I2C device의
  read/write API·callback을 통해 C/C++ 또는 스크립트로 동작을 구현한다.
  [VDK I2C 구성 설명](https://www.synopsys.com/articles/vdk-fast-track.html)
- ZeBu/HAPS hybrid: C/C++ transaction API와 하드웨어 측 BFM을 연결하며,
  데이터 교환과 동기화를 담당하는 transactor를 사용한다.
  [ZeBu 설명](https://www.synopsys.com/blogs/chip-design/interface-protocol-validation-zebu-solutions.html),
  [Hybrid prototyping 설명](https://www.synopsys.com/content/dam/synopsys/verification/prototyping/datasheets/hybrid-prototyping-brochure.pdf)

아래 표는 Synopsys 제품 API의 일대일 대응이 아니라, 역할에 따른 비교다.

| 역할 | Xtor 관점 | QBox 구성 제안 |
| --- | --- | --- |
| CPU의 controller 제어 | Controller 모델 또는 RTL | DW controller, PL061 모델 |
| 프로토콜 요청 전달 | Protocol frontend/Xtor | 공통 I2C/SPI 인터페이스 |
| 다른 실행 환경 연결 | Adapter/Xtor의 변환·동기화 | QEMU ↔ SystemC bridge |
| 주소 선택과 연결 | Bus/hub/interconnect | I2C bus, CS 연결, GPIO net |
| 장치 고유 동작 | Device model/backend | Register와 상태 머신 |
| 부품 배치·배선 | Platform assembly | Board Lua 구성 |

따라서 앞선 구현 방식과 Xtor는 경쟁하는 대안이 아니다. 공통 인터페이스를
직접 연결하고, 표현이나 실행 환경이 달라지는 경계에 Xtor를 두면 된다.
이미 호환되는 QBox 소켓 사이에 이름만 Xtor인 추가 계층을 만들 필요는 없다.

### 여러 frontend가 하나의 장치 상태를 공유

I2C와 GPIO로 제어되는 장치는 다음과 같이 구성하는 것이 좋다.

- I2C frontend: transaction 전달과 프로토콜 응답 표현
- GPIO frontend: pin level과 구동 상태 전달
- Device behavior: register, reset/power 상태, 준비 시간, IRQ 조건

**I2C frontend와 GPIO frontend가 각각 독립적인 reset 상태를 갖지 않도록
한다.** 둘 모두 하나의 device state machine으로 연결되어야 GPIO reset이
이후 I2C 응답에 반영된다.

이 역할을 반드시 별도 클래스나 shared library로 나눌 필요는 없다. 처음에는
하나의 `sc_module` 안에서 책임을 구분하고, 실제 재사용이 생겼을 때 추출한다.

Script backend도 초기 프로토타이핑에 사용할 수 있다. 다만 현재 QBox에
Virtualizer와 동일한 scripting API가 제공된다는 의미는 아니다. Reset,
interrupt, 시간 의존성이 커지면 SystemC backend가 적절하고, 외부 simulator나
RTL을 붙일 때는 해당 경계에 adapter와 동기화를 추가한다.

## 6. Lua·CCI·Linux DT의 역할

| 수단 | 책임 |
| --- | --- |
| Lua | 객체 생성과 배선 |
| CCI | 주소 strap, 초기 상태, 지연 등 구성값 |
| Component 내부 상태 | Guest register write와 pin 입력으로 변하는 상태 |
| Linux DT | Driver binding과 bus·GPIO 제어 관계의 소프트웨어 기술 |

Linux DT의 GPIO phandle만 작성한다고 QBox 신호가 연결되는 것은 아니다.
Lua 배선과 DTS가 같은 board 연결을 나타내도록 하고, bus/address/pin/polarity
일치 검사를 추가한다. 여러 board가 생기기 전부터 별도 구성 생성기를 만들
필요는 없다.

## 7. 권장 초기 구현과 검증

첫 범위는 I2C bus 하나, GPIO expander 하나, reset 입력을 가진 I2C target
하나로 한다. Linux가 expander를 통해 reset을 제어하는 경로를 검증한다.

1. 같은 버스의 두 장치를 주소로 구분해 접근한다.
2. Expander 출력으로 대상의 reset을 assert/deassert한다.
3. Reset 및 준비 상태에 따라 대상의 통신 응답이 달라지는지 확인한다.
4. Reset 중 예약된 작업이나 오래된 IRQ가 뒤늦게 발생하지 않는지 확인한다.
5. 필요한 경우 GPIO 입력 방향, pull 상태, IRQ 복귀 경로를 검증한다.
6. Lua 배선과 Linux DT의 연결 관계가 일치하는지 검사한다.

영상 등의 데이터 경로는 별도의 데이터 인터페이스로 확장하되, stream
enable이나 reset에 따른 동작은 같은 device state machine에 연결한다.

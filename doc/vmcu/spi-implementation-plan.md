# 직접 socket SPI bus 구현 계획

작성: 2026-10-15. 상태: **IMPLEMENTED — SPI 기능 PASS, AP DMA 회귀 FAIL**.
상위 결정: [TC397-master SPI 선정](spi-master-decision.md).
아래 내용은 구현 전 계획이다. 최종 모델·옵션·계획 조정과 시험 결과는
[SPI 구현 기록](spi-implementation.md)을 기준으로 한다.

## 1. 목표와 완료 정의

TC397 QSPI master와 Apollo SI CL0 SPI slave를 직접 loopback TCP로 연결한다.
SI firmware가 데이터를 준비한 뒤 `SOC_SPI_REQ` GPIO를 토글하면 TC397 firmware가
이를 감지하고 실제 QSPI MMIO/FIFO 경로로 통신한다. SI의 기존 PFDI 보고 및
제어 서비스를 이 링크로 실행하고 AP OFF/reset 중에도 유지하는 것이 완료 목표다.

최종 성공 증거는 실제 guest의 요청→GPIO→QSPI 전송→slave 처리→응답→ACK다.
host가 firmware 대신 메시지를 만들거나 소켓 echo가 성공한 것으로 대체하지 않는다.

첫 범위는 1 master/1 slave/1 CS, 4-wire SPI, 8-bit/MSB-first/mode 0, PIO와
controller IRQ다. TC397 GPIO 요청 감지는 polling으로 시작한다. 다른 mode/word
길이, DMA, ERU GPIO interrupt, 다중 slave, bit-level timing은 후속 범위이며
지원하지 않는 설정은 명시적으로 검출한다. 최초 검증 SCLK는 1 MHz 설정을
시험값으로 사용하되 보드 사양 또는 실시간 성능 보장으로 취급하지 않는다.

AP DW UART2↔ASCLIN0 관리, ASCLIN1 shell, 차량 CAN/SIL Kit, PMIC의 SI 단독
소유권을 유지한다. SPI profile에서 SI 안전 UART만 SPI로 대체한다. UART와 SPI를
동시에 독립적인 필수 safety source로 동작시키거나 실패 시 조용히 fallback하지 않는다.

## 2. 현재 기준점과 책임

현재 로컬 build 입력은 `apollo-qvp`, `cfg2`, AP 4코어이며 template은
`meta-hsoc-auto-solutions/conf/templates/apollo-qvp`다. 이는 설정 파일 확인이며
배포 binary 일치 검증은 아니다. 구현 시작 시 root/nested Git 상태, 실제 provider,
firmware hash와 build 입력을 다시 기록한다. 공유 BitBake 실행은 직렬화한다.

| 소유 저장소/영역 | 구현 책임과 주요 파일 |
|---|---|
| `hsoc-stack/tools/qemu` | 신규 `hw/ssi/tc397_qspi.c`와 header, `hw/tricore/tc397.c`, Kconfig/Meson, QSPI qtest. 기존 `hw/gpio/tricore_port.c`의 입력/재연결 계약 점검 |
| `hsoc-stack/tools/qbox` | `systemc-components/spi/dw-apb-ssi/`의 재사용 가능한 slave 기능을 우선 검토. SPI bus ingress와 component test, C++14 유지 |
| `hsoc-stack/tools/qbox-platform` | `vp/extensions/si-cl0-vmcu.lua`, `vp/options/vmcu.lua`, GPIO bridge, SI reset/IRQ wiring, 빌드 등록과 Lua descriptor test |
| `hsoc-stack/components/system_mgmt/scp-firmware` | `apollo-qvp/module/vmcu_safety`, `si0_ramfw/config_vmcu_safety.c`, 신규 slave driver/module, PFDI/RPC 정책과 링크 처리 분리 |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src` | 신규 QSPI driver/binding, DTS/Kconfig/CMake, `src/main.c`의 링크 worker, 기존 `lib/safety.c`/CAN 제어 경로 재사용 |
| owned Yocto layers | `qemu-apollo-native.bb`, `qbox-apollo-qvp-native.bb`, `zephyr-vmcu.bb`, SCP append, 필요한 firmware 선택/배포 manifest |
| root | `scripts/run/qbox_tc397.py`, `run_qbox_yocto.sh`, board session/tmux/dashboard 인자 전달, protocol vectors, 집중/전체 검증기와 문서 |

경로는 각 소유 Git 저장소 안에서 변경한다. `arm-zena-css`와 외부 layer는 수정하지
않는다. 기존 코드 이동 시 RPC 검증·timeout·중복 처리·PMIC 권한을 그대로 유지한다.

## 3. P0 — controller 및 wire 계약 고정

모델 작성 전에 다음 표를 소스와 TC397 derivative 문서로 완성한다. 추정 MMIO/IRQ를
실물 사양처럼 사용하지 않는다. 결과는 이 문서의 구현 상태와 별도 protocol 문서에
반영한다. 이 단계의 확인은 구현 작업의 일부이며 추가 사용자 승인 단계가 아니다.

| 항목 | 기본 방향 | P0 완료 조건 |
|---|---|---|
| Apollo slave | SI CL0에 별도 인스턴스. 기존 DW SSI의 slave 기능 확장 우선 | 해당 IP의 slave register/FIFO/CS/underrun/reset 근거 확보, 재사용 가능 판정. 맞지 않으면 명시적인 QVP extension controller 계약을 먼저 작성 |
| SI map/IRQ/reset | AP SSI 주소 재사용·alias 금지 | SI router decode 충돌 없음, GIC INTID와 SPI index 구분, AP reset fanout 제외/전체 reset 포함 |
| TC397 QSPI | 사용하지 않는 QSPI instance 하나를 master로 모델링 | TC397 MMIO, clock/reset, BACON/ECON/DATAENTRY/RXEXIT, FIFO depth, SRC TX/RX/error 번호와 priority 확정 |
| 요청 GPIO | 기존 signal과 독립된 미사용 PL061/PORT pin | 양쪽 방향·pull·mask·reset level 확정. 핀 0..4 기존 계약 보존 |
| polling | 기존 Zephyr link worker의 bounded polling | 요청 level 관찰과 단일 전송 scheduling, polling 주기와 guest 시간 기준 기록 |
| buffer/전송 크기 | 실제 FIFO depth와 서비스 방식에 맞춤 | preloaded MISO 소진과 RX overflow가 모델에 드러남. host buffer로 FIFO 용량을 늘리지 않음 |

wire v1은 little endian 명시 직렬화로 정의하고 C struct를 그대로 전송하지 않는다.
다음 필드는 초기 설계 입력이며 **offset/크기/최대 길이/오류 코드는 P0에서 고정**한다.

| record | 내용 |
|---|---|
| HELLO/READY | magic/version, 최대 record/chunk 크기, 지원 SPI 설정, 양쪽 connection generation |
| TRANSFER | record length, generation, transfer ID, CS, BEGIN/CONTINUE/END, mode/bit order/word width, SCLK, word count와 MOSI |
| COMPLETE | 같은 generation/ID, 전송 결과, 실제 처리 word 수, MISO |
| CANCEL/RESET | 취소 대상 generation/ID 및 원인. 단절 자체로도 outstanding 작업 취소 |

첫 버전의 outstanding chunk는 1개다. record/chunk 상한은 고정 상수와 test vector로
관리한다. TCP 분할/병합 수신을 처리하고 길이를 검증한 후 buffer에 복사한다.
partial send는 pending buffer를 유지하며 재접속 시 이전 partial record를 폐기한다.
미정의 flag, 불일치 word count, CS 없이 CONTINUE, 중복/역순 ID를 거부한다.

bus COMPLETE는 firmware ACK가 아니다. TCP 성공도 SPI 처리 성공이 아니다.
동일 wire transfer를 재실행하여 FIFO를 두 번 pop/push하지 않는다. timeout 이후
결과가 불명확하면 session을 복구하며, 업무 명령의 재시도는 application sequence로
중복 실행을 막는다. transport fault를 CAN bus-off 등의 다른 bus 상태로 표현하지 않는다.

검증: Python 기준 codec과 C/C++ 양단이 동일 golden vectors를 통과한다. controller
선정 근거와 MMIO/IRQ/reset 표가 완성되지 않으면 P1/P2를 완료 처리하지 않는다.

## 4. P1 — TC397 QSPI master와 비동기 socket

1. QSPI register decode, FIFO, 상태/오류 clear, CS 수명, SRC interrupt를 구현한다.
   register write는 FIFO에 적재하고 반환하며 CPU/BQL에서 원격 응답을 기다리지 않는다.
2. controller 전송 상태는 `IDLE → PENDING → COMPLETE/FAULT`로 관리한다.
   guest가 설정한 전송 순서에서 MOSI를 꺼내 전용 chardev로 발행한다.
3. QEMU owner context에서 응답을 검증하고 RX FIFO, busy/completion, IRQ를 갱신한다.
   reset 또는 disconnect 이후 늦은 완료는 generation으로 폐기한다.
4. `ssi_transfer()`의 즉시 반환 계약은 변경하지 않는다. remote path는 비동기
   controller 전송 경로로 구현하며 다른 QEMU SSI controller에 전역 변경을 가하지 않는다.
5. disconnect 중인 controller가 guest에 무한 busy로 남지 않게 종료/오류 계약을
   구현한다. 어떤 guest status로 노출할지는 P0에서 확인한 hardware 계약을 따른다.

검증은 QEMU qtest와 작은 TC397 guest로 수행한다. TX/RX 데이터, FIFO threshold,
IRQ mask/clear, CS 유지·해제, unsupported mode, peer 없음, partial send, RX
overflow, transfer 중 reset, 늦은 응답을 검사한다. 상대는 protocol fixture이며
이 단계는 Apollo firmware와의 통합 증거가 아니다.

## 5. P2 — Apollo SI SPI slave와 QBox 연결

1. 확정한 slave controller를 SI CL0 router/GIC/reset 수명에 연결한다. AP CPU가
   꺼져도 존재해야 하며 기존 AP DW SSI 4개의 descriptor와 loopback은 보존한다.
2. slave TX FIFO는 SI MMIO write로 채운다. 원격 clock 요청마다 기존 TX 데이터를
   MISO로 꺼내고 MOSI를 RX FIFO에 넣는다. hardware 정의의 IRQ/overrun/underrun을
   갱신한다. firmware가 새 데이터를 만들 때까지 무한히 기다려 underrun을 숨기지 않는다.
3. BEGIN/CONTINUE/END로 CS 수명을 관리한다. packet 수신 완료를 CS deassert로
   해석하지 않는다. word 또는 작은 chunk 단위의 진행점을 두어 FIFO/IRQ가 관측되게 한다.
4. socket callback은 소유 payload를 bounded queue로 넘기고 async ingress로
   SystemC owner에서 처리한다. callback에서 `wait()`나 guest MMIO를 호출하지 않는다.
5. nominal SCLK duration과 host transport 지연을 별도로 기록한다. 두 emulator의
   독립 시간축은 유지하며 엄밀한 cross-process clock/FTTI 보장은 하지 않는다.

검증: SystemC component test로 preload/full-duplex/FIFO/CS/error/reset을 확인한다.
이어서 QEMU fixture↔실제 QBox slave와 QSPI master↔실제 QBox slave를 순차 연결한다.
측정 가능한 항목은 data/ordering/guest-visible IRQ이며 물리 timing 증거와 구분한다.

## 6. P3 — GPIO 요청과 양쪽 firmware

GPIO bridge의 기존 mask `0x07`을 새 pin까지 확장하고 Lua binding, GPIO 기본값,
SCP direction 설정, TC397 PORT 입력, descriptor test를 함께 갱신한다. 이전 peer가
확장 mask를 지원하지 않는 경우 fail-fast 또는 명시적 legacy profile로 처리한다.
기존 GP8 packet 크기를 늘릴 필요는 없지만 capability/version 호환 계약은 고정한다.

SI의 전송 상태는 `IDLE → DATA_READY → WAIT_ACK → IDLE`다.

1. SI가 frame과 pending sequence를 고정하고 TX 데이터를 준비한다.
2. `SOC_SPI_REQ`를 반전한 뒤 ACK까지 유지한다. 추가 요청은 bounded queue에
   보관한다. 포화는 오류로 기록하고 무제한 buffer나 silent drop으로 바꾸지 않는다.
3. MCU가 PORT IN 변화를 감지하면 QSPI read를 실행한다. 최초 polling 방식은
   GPIO interrupt 지원으로 보고하지 않는다.
4. MCU는 frame CRC/epoch/sequence를 검사하고 다음 transaction에서 ACK를 보낸다.
   잘못된 frame은 ACK하지 않으며 제한된 recovery와 fault 상태로 전환한다.
5. SI는 일치하는 ACK만 수용하고 다음 pending frame을 준비한 후 다시 토글한다.

MCU→SI 명령은 master가 MOSI로 보낸다. SI firmware가 이를 처리한 응답은 다음
transaction에서 읽는다. 명령 처리 결과를 같은 transfer의 과거 MISO로 반환하지 않는다.
기존 28-byte protocol의 CRC/epoch/sequence와 operation 의미는 최대한 재사용하되,
bus frame/idle filler와 application 메시지를 분리한다. SPI ACK, SYNC, pending 상태
조회가 기존 enum/ABI를 깨뜨리지 않도록 version과 golden vectors로 검증한다.

한 frame이 controller FIFO보다 큰 경우 chunk 크기/서비스 진행점을 P0에서 정한다.
CS를 유지한 chunk 사이 지연을 실제 연속 clock이라고 주장하지 않으며 slave FIFO가
작다는 이유로 완성된 application frame을 host 측에서 몰래 주입하지 않는다.

재시작은 GPIO 첫 level만으로 판단하지 않는다. MCU master가 SYNC하여 SI epoch,
pending sequence와 ACK cursor를 읽고 재개한다. GPIO 수신과 SPI 수신 사이에는
전역 순서가 없으므로 데이터 준비 완료를 먼저 보장하고 상태 조회로 경쟁을 해소한다.

검증: native 정책 시험과 실제 SCP/Zephyr driver를 사용해 정상 요청, ACK 유실,
중복 ACK, pending 중 추가 요청, stale epoch, MCU reset, SI reset, GPIO 단절,
queue 포화, 양방향 command/reply를 확인한다. reboot 직후 임의 reset/power 명령이
재실행되지 않아야 한다.

## 7. P4 — 빌드·런처·관측 연결

초기 SPI profile은 기본 UART profile과 구별해서 빌드한다. 계획 변수
`VMCU_SAFETY_TRANSPORT=uart|spi`를 owned Yocto metadata에서 두 firmware에
같이 전달하고 deploy manifest에 기록한다. 정확한 recipe 전달 방식은 해당
recipe의 현재 CMake/Kconfig 관례에 맞춘다. 기본값은 uart다.

SPI용 별도 build directory를 사용하거나 공유 build가 idle일 때만 입력을 변경한다.
SCP 변경은 서명된 SI/RSE boot artifact까지 다시 배포하고 Zephyr ELF만 교체한
혼합 구성을 금지한다. firmware 선택 정보가 없는 오래된 manifest는 UART만 허용한다.

계획 CLI `--vmcu-link uart|spi`는 이미 배포된 호환 artifact를 선택·검증한다.
옵션 하나가 firmware를 자동 재빌드하거나 런타임에 임의로 운용 모드를 바꾸지 않는다.

- TC397을 `-S`로 생성하고 SPI chardev를 loopback `port=0`으로 연다.
- supervisor가 QMP로 실제 endpoint를 찾고 계획 환경변수
  `QBOX_APOLLO_VMCU_SPI_ENDPOINT`로 QBox에 전달한다.
- SPI endpoint는 기존 AP UART/safety UART/GPIO/CAN endpoint와 달라야 한다.
- 기존 console/CAN readiness와 수명을 보존하고 양쪽 SPI HELLO/READY 후 guest
  traffic을 시작한다. 초기 SYNC가 연결 지연을 처리하며 open socket만으로 READY를
  선언하지 않는다. 연결 deadline과 종료 시 owned process cleanup을 검사한다.
- SPI를 요청했는데 binary/firmware/peer가 없으면 명확히 실패한다. UART로
  조용히 대체하지 않는다. `--no-vmcu`와 SPI 필수 profile의 충돌도 거부한다.
- tmux/board session/dashboard를 지나는 인자와 manifest/topology를 함께 갱신한다.
  새 UI 화면은 만들지 않고 현재 topology와 상태 출력에 실제 링크를 반영한다.

관측 항목: controller TX/RX/IRQ/error, CS 구간, wire generation/ID, 요청 toggle,
application sequence/ACK, stale/drop/timeout, queue high-water mark. host monotonic,
QEMU virtual time, SystemC time, guest uptime은 서로 다른 필드로 기록한다.
guest safety deadline을 host wall clock으로 조용히 바꾸지 않는다.

## 8. P5 — 기존 safety/service 전환 및 전체 검증

새 SPI 기능을 PFDI 정책과 동시에 처음 디버깅하지 않는다. P3까지 통신을 검증한
후 SCP와 MCU의 transport 선택만 SPI로 전환한다. 기존 PFDI snapshot, 5초 보고,
상태 변화 보고, 15초 freshness 및 GPIO SOC_ERROR 정책을 재사용한다.
timeout 원인이 SPI transport인지 PFDI fault인지 결과에서 구분한다.

| 시험 | 통과 증거 |
|---|---|
| boot/SYNC/초기 요청 | 양쪽 epoch와 pending/ACK 일치, 정상 데이터 및 실제 controller IRQ |
| SI safety 보고 | sequence 증가, source=SI0_PFDI, UART 경로 없이 SPI 수신 |
| SI RPC | ping/status, PMIC read-only rail/fault, duplicate/stale 거부 |
| AP 관리 | ASCLIN0↔DW UART2 관리 유지, SPI safety와 독립 |
| PFDI fault | 실제 AP agent 정지→SI fault→GPIO 요청→SPI fault 보고. 일반 runner의 의도된 FAIL 보존 |
| AP recover/off/wake | 기존 SI/RSE 경로와 Linux 재부팅 확인, AP OFF 동안 SI SPI/RPC와 MCU 생존 |
| reset 범위 | AP reset은 SPI session 유지, SI/MCU reset은 해당 session 재협상과 stale 완료 폐기 |
| 고장 | SPI/GPIO 각각 단절, peer pause, CS 중 reset, ACK 유실, malformed record, FIFO/queue 포화 |
| 회귀 | 기본 UART, `--no-vmcu`, CAN/SIL Kit, PMIC preserve, 기존 AP SSI loopback/IRQ/DMA 동작 |

생성 증거는 `build/qbox-apollo-qvp/vmcu-spi/<run-id>/`에 둔다. manifest에 명령,
MACHINE/provider/commit/dirty 상태, binary/ELF/boot artifact hash, transport 버전,
mode와 GPIO mapping을 기록한다. 결과는 PASS/FAIL/SKIP/UNSUPPORTED를 구분한다.

검사 순서는 codec/policy → QEMU qtest/guest → SystemC component/Lua → paired
model → SCP/Zephyr guest → 전체 BSP다. 관련 provider `do_check`를 통과하고,
이미지 반영은 `./yocto_build.sh --bsp`의 대응 build configuration에서 수행한다.
map 변경 후 `scripts/test/validate_qbox_apollo_fvp_full_map.py`를 실행한다.

전체 전용 검증기는 기존 `verify_qbox_vmcu_services.py`/`verify_qbox_zephyr_vmcu.py`
패턴을 재사용하되 SPI 전송과 firmware ACK를 실제 로그/카운터로 판정한다.
boot/login 성공만으로 SPI 통과를 선언하지 않는다. 전체 post-login qualification은
별도 canonical runner로 수행하고 그 결과를 SPI 시나리오 결과와 섞지 않는다.

## 9. 의존 순서와 완료 체크리스트

P0 계약 확정 → P1/P2 개별 모델 → paired 모델 → P3 firmware/GPIO →
P4 배포·런처 → P5 전체 서비스 검증 순서다. P1/P2는 동일 wire 계약이 고정된
뒤 독립 개발할 수 있지만 shared build와 최종 integration은 직렬 수행한다.
소요 기간은 P0의 slave IP 재사용 판정과 QSPI register 범위 확인 뒤 산정한다.

- [x] P0 구현 계약: QVP slave register/TX_COMMIT, TC397 QSPI0/SRC,
  SI map/reset, GPIO5, 64-byte wire 및 28-byte ACK/SYNC 계약 확정.
  계획에서 조정한 사항은 [구현 기록](spi-implementation.md)을 따른다.
- [x] P1 집중 검증: 배포 QEMU의 비동기 QSPI FIFO/IRQ, split record,
  malformed CRC, duplicate, peer timeout/disconnect/reconnect, stale completion,
  reset/CANCEL, FIFO overflow 시험 PASS.
- [x] P2 집중·통합 검증: slave/GPIO component 및 TX_COMMIT 시험 PASS.
  실제 배포 QEMU와 Zephyr guest의 IRQ/CRC/ACK 및 지연 GPIO 시험 PASS.
  전체 BSP에서 실제 QSPI↔QBox slave↔SCP 통신 확인.
- [x] P3 정상 경로: GPIO toggle→read→ACK, 양방향 RPC, MCU reset 후
  session 복구, AP recovery/off/wake 중 SI 통신 유지 PASS.
- [ ] P3 전체 고장 경로: native/model에서 확인한 범위를 제외한
  전체 BSP의 SPI/GPIO 단절·ACK 유실·SI reset·queue 포화 조합은 미완료.
- [x] P4 정상 SPI profile: BSP 빌드, 배포 provider/firmware 선택,
  firmware handshake readiness와 정상 기능 실행 후 소유 process cleanup PASS.
- [x] P5 정상 서비스: safety/PFDI 상태 보고, AP UART, PMIC 읽기,
  CAN classic/extended/FD64, MCU reset, AP recovery 및 off/wake 2회 PASS.
- [x] P5 실제 PFDI fault 주입, SPI report-off/on timeout 및 기본 UART 서비스 회귀:
  `services-fault-retry`, `report-off-final`, `services-uart-retry` PASS.
- [ ] P5 AP SSI/DMA 회귀: vMCU 없는 Linux 부팅은 확인했으나 전체 SSI suite
  DMA timeout이 발생했다. bounded fixture도 SPI1 64byte에서
  `arm-dma350` re-entrant IO 차단/IRQ read abort로 FAIL이다.
  4099byte 및 뒤의 UART 시험은 미실행이다.
- [x] 최종 문서 대조: platform README, emulation project 및 vMCU 기록에
  구현 계약과 PASS/FAIL/미검증 범위를 구분했다.

2026-10-15 현재 정상 전체 기능 증거는
`build/qbox-apollo-qvp/vmcu-spi/services-normal-final/vmcu-services-result.json`
의 PASS다. 최초 부팅과 AP recovery 및 off/wake 2회를 포함해 Linux 준비 marker를
총 4회 확인했다. 초기 연결 전 retry 224회는 startup baseline으로 보존하고,
정상 검증 구간에서는 증가하지 않았다. MCU reset 후 최종 SPI counter는
frames=69, ACK=69, IRQ=4900, GPIO request=69, failures=0이다.

최신 SCP host 실행 결과는
`build/qbox-apollo-qvp/vmcu-spi/scp-tests/native-final.log`에 기록했다.
core만 OFF이고 cluster가 SLEEP이면 완료를 보류하는 제어 시험, 명시적
core+cluster OFF 이후 composite ON 요청, ACK mismatch/duplicate/stale,
SYNC의 command cursor 보존, report-off 중 반복 SYNC, bounded/wrapped queue,
PFDI 정책 및 RSE deadline 시험이 PASS다. Host MMIO fixture는 실제 FIFO/IRQ
증거를 대신하지 않는다. 모델 고장 시험 증거는
`integration/qspi-faults.log`, `component/faults-ctest.log`,
`component/tx-commit-ctest.log`이며, 전체 시스템의 모든 고장 조합을 증명하지 않는다.

ERU interrupt, DMA 확장, physical timing, 동기화된 FTTI 및 실물 pinmux/전원 parity는
초기 완료 조건에 포함하지 않으며 지원으로 표기하지 않는다. 보고를 꺼 둔 상태의
MCU 재시작은 기존 UART와 마찬가지로 SI epoch 발견이 제한된다.

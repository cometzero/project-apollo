# Apollo QVP I2C byte/event implementation

2026-09-17 작업. 설계 입력은
[구현 계획서](../apollo_qvp_i2c_byte_event_implementation_plan.md)다.
`/tmp/cmux-drop-67a0fa89-2509-4a2a-8142-bc026ae4ea88.md`와 동일한 내용임을 확인했다.
계획서의 모든 acceptance 항목을 완료했다는 의미는 아니다.

## Source mapping 및 board profile

| 역할 | 실제 소스 / 계약 |
| --- | --- |
| Controller | `hsoc-stack/tools/qbox/systemc-components/i2c/{include,src}/dw-apb-i2c.*`, `dw_apb_i2c`, 16-byte TX/RX FIFO |
| MMIO / engine | `b_transport`, `write_register`, `transfer_thread`, `execute_command`; QEMU MMIO bridge에서 FIFO에 command를 넣고 SystemC thread가 전송 |
| IRQ / reset | `update_irq`/`drive_irq`, `reset_controller`; 기존 AP GIC SPI320–325 및 reset fanout 유지 |
| Protocol | `systemc-components/i2c/include/i2c-transaction.h`, `dw_i2c_extension` |
| Bus | `systemc-components/i2c/i2c-bus/`, `i2c_bus`; I2C0 `board_i2c0` |
| Targets | `dw_i2c_eeprom`, `pca9539`, `tps6594`; CPU MMIO와 별도 socket 경로 |
| Wiring | `hsoc-stack/tools/qbox-platform/platforms/apollo/board/{pca9539,tps6594}.lua` |
| Linux | `hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-qvp-board.dtsi`; 기존 DesignWare, at24, TPS6594 MFD/regulator/pinctrl/RTC drivers |
| Registration / tests | QBox `systemc-components/i2c` 및 `tests/components/i2c/CMakeLists.txt` |
| Build | `build/conf/local.conf` 기본은 apollo-fvp이므로 명령에 `--machine apollo-qvp --keep-conf` 지정; `tmp_baremetal` 사용 |

| I2C0 device | Address | Board signal / profile |
| --- | --- | --- |
| TPS6594 primary | 0x48–0x4c | INT_N → SMD GPIO2 |
| TPS6594 additional 1 | 0x58–0x5c | INT_N → SMD GPIO3 |
| TPS6594 additional 2 | 0x60–0x64 | INT_N → SMD GPIO4 |
| TPS6594 additional 3 | 0x68–0x6c | INT_N → SMD GPIO5 |
| EEPROM ×3 | 0x50, 0x51, 0x52 | AT24C02 profile, each 256 bytes, 8-byte pages, 8-bit pointer, write busy 5 ms |
| PCA9539 | 0x74 | 기존 SMD GPIO0 reset / GPIO1 interrupt |

PMIC 주소는 QVP 검증 보드 설정이며 실제 부품의 address strap 지원 주장과 구분한다.
각 PMIC에서 BUCK1–5는 900000 µV, LDO1–4는 1800000 µV의 DT 제약을 갖는다.
각각 별도의 `regulator-output` consumer가 있어 총 36개 rail을 Linux API로
활성화·전압 읽기·비활성화할 수 있다. 이 consumer는 SoC 전원 domain에 연결되지 않은 시험용 부하다.
GPIO offset 0→1 및 8→9 loopback은 네 PMIC 각각 독립적이다.

## 구현된 protocol과 모델링 한계

- 기존 TLM byte payload와 `restart`/`stop` 플래그를 유지하면서
  discover, START, RESTART, address, read ACK/NACK, STOP, CANCEL event를 추가했다.
  Bus는 simulation 시작 시 side-effect-free discover로 주소표를 만들고
  중복 주소와 PMIC page alias 충돌을 거부한다. Data는 선택한 target에만 전달한다.
- START/RESTART/STOP/CANCEL은 모든 target에 전달한다. 없는 주소로 전환한 뒤에도
  STOP이 이전 target에 전달된다. CANCEL은 STOP이 아니며 미완료 EEPROM page를 폐기한다.
- Controller는 다음 command까지 read 응답을 보류해 FIFO starvation 이후에도
  ACK 또는 RESTART 직전 NACK을 선택한다. Reset/disable/abort는 generation을
  변경해 이전 command의 완료를 폐기하고 bus session을 취소한다.
- EEPROM은 8/16-bit pointer, page wrap, STOP commit, write protection,
  독립 busy 시간을 지원한다. Controller reset은 이미 기록한 내용과 busy 시간을 지우지 않는다.
  실제 보드는 기존 AT24C02를 유지한다. 16-bit pointer는 host fixture에서 별도 검증한다.
- `platform.board_i2c0.trace=true`로 event trace를 활성화할 수 있다.
  기본은 비활성이다. NACK은 기존 TLM response mapping을 유지하며 controller가
  address/data abort로 변환한다. 계획서가 제안한 별도 protocol-result 구조체로
  모든 transport error를 재분류한 구현은 아니다.
- 전송 시간은 기존 `transfer_latency` 기반 byte 단위 추상화다. HCNT/LCNT 기반
  SCL bit timing, electrical stretching, pin waveform, multi-controller arbitration,
  10-bit 주소, bus-clear 및 오류 주입 framework는 이번 완료 범위가 아니다.
  Target access latency의 세부 side-effect 시점은 기존 annotated-delay 방식이다.
- PMIC 전압은 기능적 signal 값이다. Analog regulation, PFSM 전원 sequence,
  SPMI 동기화, physical power-off/retention, 실제 TPS6594 NVM/address strap parity를
  검증하지 않았다. 상세 범위는 [기존 PMIC 문서](tps6594.md)를 따른다.

## 재현

```sh
./yocto_build.sh --machine apollo-qvp --keep-conf virtual/kernel -c compile
./yocto_build.sh --machine apollo-qvp --keep-conf qbox-apollo-qvp-native -c compile
./yocto_build.sh --machine apollo-qvp --keep-conf qbox-apollo-qvp-native -c check
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp
./run_qbox_yocto.sh --bsp --headless --keep-running-after-pass --multi-session \
  --copy-disks --no-persistent-rse-state --timeout 600 \
  --out-dir build/qbox-apollo-qvp/i2c-multi-20260917/runtime-fixed \
  -- --platform-param platform.board_i2c0.trace=true
./scripts/run/ssh_run.sh scripts/test/verify_qbox_tps6594.sh
./scripts/run/ssh_run.sh scripts/test/verify_qbox_i2c_multi_slave.sh
```

EEPROM 시험은 세 worker를 barrier로 동시에 시작하고, 장치별로 다른
256-byte pattern을 8회 쓰고 읽는다. 각 전송은 FIFO와 EEPROM page보다 길다.
Linux adapter lock에 의해 실제 bus access는 직렬화된다. 완료 후 모든 장치를
다시 읽어 target 격리를 확인하고 원본 내용을 복원·비교한다. 복원 실패 시
FAIL과 backup 경로를 출력하고 backup을 보존한다.

PMIC 시험은 네 driver binding, 36개 rail, 각 GPIO loopback high/low,
primary PMIC RTC tick 및 alarm IRQ 두 차례를 확인한다. 변경한 regulator
상태를 복원한다. RTC 시간과 alarm은 전용 시험 guest에서 변경한다.
GPIO 11개 모두의 외부 pin 동작이나 추가 PMIC 세 개의 RTC IRQ 시험과는 구분한다.

## 검증 결과

산출물 경로: `build/qbox-apollo-qvp/i2c-multi-20260917/`.

| 검사 | 결과 | 증거 |
| --- | --- | --- |
| 기존 I2C/PCA9539/TPS6594 baseline | 3 suites PASS | `baseline-ctest.log` |
| Kernel/DTB compile | PASS | `kernel-compile.log` |
| Lua board 및 SSH wrapper pytest | 2 PASS | `board-pytest.log` |
| 기존 memory/IRQ/reset/timer/ATU map 검사 | 95/95 PASS | `map-result.json` |
| 최종 host tests | 20 tests / 3 suites PASS | `i2c-ctest-abort-hold.log` |
| 최종 provider platform gate | 61/61 PASS | `provider-platform-tests.log` |
| 최종 provider I2C core gate | 3/3 suites PASS | `provider-core-tests.log` |
| 최종 BSP image build | PASS | `bsp-build-abort-fixed.log` |
| 최종 QBox BSP boot | PASS (boot gate) | `runtime-fixed/result.json` |
| Guest PMIC | 4개, 36 rails, 8 GPIO high/low checks, RTC alarm 2회 PASS | `guest-pmic-fixed.log` |
| Guest PCA9539 회귀 | reset/NACK, GPIO, IRQ, EEPROM 보존 PASS | `guest-pca9539-fixed.log` |
| Guest I2C1–5 direct-target 회귀 | 5개 write/read/restore PASS | `guest-direct-i2c.log` |
| Guest EEPROM 동시 전송 | 24/24 PASS, 격리·복원 각각 3/3 PASS | `guest-eeprom-fixed.log` |
| EEPROM trace: 잘린 page write | 0건, busy address NACK 143건 관측 | `trace-summary-fixed.json` |

Host 범위는 DW I2C 12개, PCA9539 3개, TPS6594 5개다. 16-bit address
상위 바이트 격리, page wrap, busy 중 다른 target 접근 및 복구, 미완료
page의 controller reset 취소, FIFO starvation과 read→RESTART ACK/NACK
순서, 실패한 address 뒤 STOP broadcast, PMIC 전체 GPIO 11개의 입출력과
regulator 9개 signal 출력을 포함한다. Startup duplicate-address rejection은
구현됐으나 전용 실패 시험은 수행하지 않았다. EEPROM write protection 역시
구현됐으나 전용 시험은 수행하지 않았다.

첫 compile의 잘못된 controller CCI field와 bus include 경로 누락을 수정했다.
첫 host 실행의 busy 시간 변환 및 GPIO test fixture 충돌도 수정했다.
초기 실패 로그(`provider-compile*.log`, `i2c-ctest.log`)는 보존한다.

최종 BSP에서는 임시 `i2c-check.conf`를 BitBake `-R`로 전달해
`QBOX_CORE_TEST_DIRS:pn-qbox-apollo-qvp-native = "components/i2c"`를 선택했다.
Provider platform gate는 유지하며, 다른 core suite는 이번 실행 범위에서 제외했다.
기본 build/conf 설정이나 recipe의 영구 test policy는 변경하지 않았다.


### Guest에서 발견한 TX abort 결함

첫 PMIC guest 시험은 36개 rail, 네 GPIO loopback, primary RTC alarm을
통과했으나 EEPROM 동시 시험은 실제 데이터 불일치로 실패했다.
`guest-eeprom-concurrent.log`와 진단 재실행 `guest-eeprom-diagnostic.log`를
보존했다. 진단 실행은 256-byte read 전체를 받았지만 비교가 실패했으며,
원본 내용 복원은 세 장치 모두 PASS였다. 실패한 expected/actual 파일은
`guest-eeprom-failure.tar.gz`에 보존한다.

Trace에서 busy NACK 뒤 실패한 page write의 남은 바이트가 controller에
다시 들어가고, busy가 끝나자 4/5/6-byte suffix가 새로운 write로 실행됐다.
예를 들어 0x52의 202.517648413 s 전송은 정상적인 pointer+8-byte page 대신
`79 2c 3d 4e`를 보내 잘못된 위치에 기록했다. 원인은 TX_ABRT latch가
유지되는 동안에도 `IC_DATA_CMD`가 command를 받아들인 동작이었다.
TX_ABRT를 clear할 때까지 TX FIFO를 reset 상태로 유지하는 회귀 테스트와
수정을 추가했다. 결정적 회귀 시험을 포함한 host 20개, provider platform
61개 및 core 3개 suite가 통과했다. 수정 후 같은 guest 시험은 24회 전부
통과했고, trace의 잘린 page write도 기존 두 실패 실행의 8건에서 0건으로
바뀌었다. 세 EEPROM의 정상 page write는 각각 288회(8회 전체 쓰기 및
원본 복원), 매번 pointer+8 byte였다. 5 ms busy 설정에서 address NACK 143건을 관측했고, Linux DesignWare/at24의
정상 재시도 경로를 통과했다.


최종 요약은 `validation-summary.json`, 실행한 provider module/Lua/DTB/kernel/
WIC의 SHA-256은 `artifact-sha256.json`, 수정 소스의 revision 및 hash는
`source-state-final.json`에 있다. 최초 실패 provider hash는
`artifact-sha256.initial.json`으로 보존한다. `runtime/result.json`은 초기
boot 성공만 나타내며 그 실행의 EEPROM qualification은 FAIL이다.
`runtime-fixed/result.json`과 `guest-*-fixed.log`가 최종 실행 증거다.
Root launcher의 shared post-login probe는 비활성이고, 위 guest scripts를
SSH로 별도 실행해 판정했다. 전체 Apollo/FVP coverage PASS를 뜻하지 않는다.

추가 direct-target 회귀 스크립트는 증거 디렉터리의 `guest-direct-i2c.sh`다.
기존 I2C1–5에서 8-byte 쓰기/읽기 후 원본을 복원·비교했다.
`trace-summary-fixed.json`의 분석기는 이번 at24 256-byte 시험에서 허용되는
pointer-only 및 pointer+8-byte 전송을 검사하며 범용 I2C protocol validator는 아니다.

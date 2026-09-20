# TPS6594: SI CL0 SCP ownership

## 현재 구성: PMIC 1개, 기본값 보존

SI CL0 전용 I2C에 `0x48` PMIC 하나만 연결한다. `0x58`, `0x60`,
`0x68` 모델은 생성하지 않는다. PL061 fault 입력도 GPIO 0 하나만 사용한다.
Controller `0x2a800000`, fault GPIO `0x2a810000`, 10 µs byte latency와
100 ns slave latency는 유지한다. Linux는 PMIC를 소유하지 않으며
TPS6594 RTC 미사용 / PL031 사용 정책은 그대로다.

SCP는 power module 초기화 전에 controller를 준비하고 `DEV_REV`를
한 번 읽어 응답을 확인한다. PMIC data register에는 쓰지 않는다.
전압·enable·GPIO·IRQ mask·latched status·RTC 값을 그대로 보존하며,
정상 boot에서 전압 readback과 GPIO self-test는 **SKIP**이다.
이전 216 I2C transaction에서 **1 read transaction**으로 줄였다.
Register pointer를 전송하는 I2C write phase와 controller MMIO 설정은
여전히 필요하지만 PMIC 설정 register write는 0회다.

| Rail | 새 QBox 프로세스의 기본 selector 전압 | Enable |
| --- | --- | --- |
| BUCK1–5 | 300 mV | disabled |
| LDO1–3 | 600 mV | disabled |
| LDO4 | 1.2 V | disabled |

위 전압은 selector 설정값이며 rail이 실제로 켜져 있다는 뜻이 아니다.
SoC reset에는 PMIC가 reset되지 않으므로 이전 runtime에서 변경한 값도
보존한다. 기본값으로 강제 복원하는 register write는 하지 않는다.
현재 power-domain은 기존 mock PSU를 사용하므로 이 설정이 물리 보드의
전원 시퀀스를 대신하지 않는다.

SCP board config는 `configure_registers=false`, `gpio_self_test=false`다.
Runtime voltage/enable/GPIO/fault API와 명시적으로 활성화하는 진단용
전체 초기화 경로는 유지한다. Timeout 100 ms는 오류 한도이며 정상
STOP 확인 시 즉시 반환한다. NACK/timeout이면 power 초기화로 진행하지 않는다.

현재 검증 도구와 로그는
`build/qbox-apollo-qvp/si-cl0-pmic-minimal-20260920/`에 보관한다.
`scripts/test/verify_qbox_si_pmic.py`는 단일 PMIC의 보존 정책과 SKIP marker를
검증하며, 과거 4개 PMIC 결과를 현재 구성의 PASS로 인정하지 않는다.

### 단일 PMIC 검증 결과

`apollo-qvp`, BSP initramfs, AP 4 CPU, PFDI 활성화로 실행했다.

| 항목 | 이전 4개 / 전체 초기화 | 현재 1개 / 기본값 보존 |
| --- | --- | --- |
| I2C transaction | 216 | 1 (DEV_REV read) |
| PMIC 구간 host 관측 | 2.173137 s | 0.013929 s (약 14 ms) |
| SCP counter 경과 | 2.182536 s | 0.022207 s (약 22 ms) |
| Rail 설정 / GPIO self-test | 수행 | SKIP |

현재 host 시간은 console begin→complete를 1 ms 주기로 관측한 단일 실행이고,
이전 실행은 5 ms 주기였다. SCP counter와 host clock은 별개다.
약 99%의 구간 감소는 PMIC 수와 수행 작업을 줄인 결과이며 동일한 전체
검증을 더 빠르게 수행했다는 뜻은 아니다. 전체 Linux ready 시간은 이번에
53.74초로, PMIC 구간과 전체 부팅 성능을 구분해야 한다.

- BSP build 5793 tasks PASS; QBox `do_check` PASS. 기존 forced-run taint
  경고 5개가 남아 있다 (`bsp-build.log`).
- Native policy 검사 PASS: read 1/write 0, 임의 retained register 256 byte
  보존, probe 오류 전파 (`test-tps6594.log`).
- Root pytest 33 PASS, full-map 정적 검사 95/95 PASS.
- 실제 SCP `count=1`, `policy=preserve`, `probe=PASS`, `rail_config=SKIP`,
  `gpio_test=SKIP`, PMIC complete 이후 power-ready 확인.
- Linux PL031 1개 유지, Linux TPS6594 client/regulator/child 부재 확인.
- AP EEPROM 3개 각각 8×256-byte 동시 요청·readback·원본 복원과 PCA9539
  회귀 검증 PASS. PMIC GPIO 검증과 PCA9539 검증은 별개다.
- `final/qualification.json` PASS, guest/EEPROM/PCA9539 exit status 모두 0.
  배포 firmware/DTB SHA-256은 `artifacts.json`에 기록했다.
- 단일 PMIC 주소를 `0x70`으로 옮기는 오류 주입에서 `0x48` probe가
  address NACK (`abort=0x1`, `FWK_E_DEVICE`)로 실패하고 power 초기화에
  진입하지 않음을 확인했다 (`nack/qualification.json`: PASS).

재현 시 workspace root에서 실행한다. 측정 harness는 SSH port 8022가
해당 QBox 세션에 할당된 환경을 사용하며 실행마다 새 directory 이름이 필요하다.

```sh
python3 build/qbox-apollo-qvp/si-cl0-pmic-minimal-20260920/run_measurement.py rerun
python3 scripts/test/verify_qbox_si_pmic.py \
  --scp-log build/qbox-apollo-qvp/si-cl0-pmic-minimal-20260920/rerun/runtime/qbox-safety-island-cl0.log \
  --guest-log build/qbox-apollo-qvp/si-cl0-pmic-minimal-20260920/rerun/guest.log \
  --eeprom-log build/qbox-apollo-qvp/si-cl0-pmic-minimal-20260920/rerun/eeprom.log
```

## 이전 4개 PMIC 구성 기록

**아래 내용은 단일 PMIC 최소 초기화로 변경하기 전의 구현·측정 기록이다.
4개 PMIC, 900/1800 mV 설정, GPIO self-test, 216 transaction은 현재 기본
부팅 경로에 적용되지 않는다. 아래 과거 로그는 당시의 판정 결과다.**

Apollo QVP의 TPS6594 4개는 SI CL0 SCP firmware가 소유한다. Linux는
PMIC를 probe하지 않으며 RTC는 기존 PL031을 사용한다. TPS6594 RTC는
SCP 이관 대상에 포함하지 않는다.

## 연결과 소유권

| 대상 | SI CL0 주소/연결 |
| --- | --- |
| DW APB I2C controller | `0x2a800000`, 64 KiB |
| PMIC INT_N 입력 PL061 | `0x2a810000`, 64 KiB, GPIO 0–3 |
| I2C PMIC 주소 | `0x48`, `0x58`, `0x60`, `0x68` |
| 각 PMIC page alias | base부터 base + 4 |
| GPIO loopback | 각 PMIC의 0→1, 8→9 |

이 MMIO 영역은 QVP 전용 확장이며 RD-Aspen 물리 I2C IP 배치의
동등성을 주장하지 않는다. SI CL0 router를 통해 접근하며 Linux/AP
I2C0의 EEPROM 3개와 PCA9539는 기존 연결을 유지한다.

Controller와 IRQ 입력 GPIO는 system reset 대상이며 AP cold reset으로
재설정하지 않는다. PMIC 모델은 외부 reset 입력이 없어 SoC reset 동안
register/rail 상태를 유지한다. PMIC power-on reset은 새 QBox 프로세스에서
발생한다. SCP 초기화는 기존 enable 상태를 보존하는 방향으로 수행한다.

## 초기화와 성능 계약

QVP 빌드는 `SCP_APOLLO_QVP_PMIC=ON`을 사용한다. 다른 플랫폼에는
이 옵션을 적용하지 않는다. PMIC 초기화는 MPU와 초기 I/O 준비 후,
PPU/power 관련 module 초기화 전에 완료되어야 한다. 실패하면 power
초기화로 진행하지 않는다.

SCP는 최대 15 data byte의 FIFO burst와 bounded polling으로 register write 및
repeated-start read를 수행한다. 프레임워크 timer/IRQ가 준비되기 전이므로
`CNTPCT_EL0/CNTFRQ_EL0`로 deadline을 계산한다. 전송별 timeout은 100 ms이며
고정 sleep이 아니다. STOP 확인 즉시 반환한다. QVP의 10 ms quantum 때문에
완료된 9-byte read도 CPU counter 기준 12.355 ms로 관측되어 10 ms 한도를
초과했다. RX drain 이후 및 timeout 판정 직전에 완료 상태를 다시 확인한다.
Timeout 발생 후 controller를 실패 상태로 고정하여 아직 실행 중일 수 있는
이전 command와 후속 전송이 섞이지 않도록 한다.

각 rail의 전압 설정은 이전 Linux
구성과 동일하게 BUCK1–5 900 mV, LDO1–4 1800 mV다.
BUCK VSEL에 따라 활성 VOUT1/VOUT2 bank를 설정하고 비활성 bank와
rail enable 상태를 보존한다. 따라서 전압 설정 완료는 모든 rail의 enable을
의미하지 않는다. 현재 QBox power-on profile의 rail은 disabled다.
Linux regmap IRQ가 rail IRQ 등록 때 반복하던 ACK 대신, PMIC 초기화에서
필요한 non-RTC mask/status bank를 한 번씩 처리한다. Controller의
10 µs byte latency 및 slave의 100 ns latency는 유지한다.

GPIO 11개는 input으로 초기화한다. QVP 전용 검증에서 임시 push-pull 출력의
walking-one/all-low 패턴과 GPIO 0→1, 8→9 input loopback을 검사한 뒤
방향·latch를 복원하고 테스트가 만든 GPIO interrupt leaf를 지운다.
Open-drain 기본값으로는 pull-up이 없는 핀의 High 검증이 불가능하므로
테스트 동안만 push-pull을 사용한다. 실제 부하가 연결된 물리 보드에 이
검증 절차를 그대로 적용하면 안 된다.

초기 설정은 chip당 17 I2C transaction, GPIO 검증·정리는 37 transaction으로
총 4개에 216 transaction이다. SCP module API는 voltage, enable,
GPIO direction/read/write 및 non-RTC live fault snapshot을 제공한다.
호출은 firmware thread에서 직렬화해야 한다. Fault IRQ는 초기화 때 mask하며
비동기 fault handler와 PL061 IRQ→GIC 연결은 구현하지 않았다.

이 변경은 초기화와 driver ownership을 옮긴다. PMIC rail 출력과
CPU 전원망의 물리 연결 또는 기존 mock PSU를 실제 전원 도메인에 매핑하는
추가 계약은 제공하지 않는다. RTC, CRC-enabled I2C 및 물리 hardware
timing parity는 검증 범위 밖이다.

## 구현 파일

- SCP `module/tps6594/`: register 정책, DesignWare FIFO transport, module API.
- SCP `product/automotive-rd/apollo-qvp/si0_ramfw/config_tps6594.c`:
  주소·전압·timeout·counter 설정. `Firmware.cmake`에서 `ppu-v1` 앞에 삽입한다.
- QBox platform `platforms/apollo/{board/tps6594.lua,hw-block/si_cl0.lua}`:
  SI controller, PMIC bus, fault GPIO와 loopback 연결.
- Linux `arch/arm64/boot/dts/arm/apollo-qvp-board.dtsi`:
  PMIC 4개와 regulator-output consumer 36개 제거. Linux driver 수정 없음.
- BSP `recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc`:
  QVP에만 PMIC module 활성화.

## 2026-09-20 검증

`apollo-qvp`, cfg2, AP CPU 4개, PFDI 활성화 및 BSP initramfs로 확인했다.
원본 로그·측정 도구·JSON 판정은 workspace의
`build/qbox-apollo-qvp/si-cl0-pmic-20260920/`에 보관한다.

| 검사 | 결과 / 증거 |
| --- | --- |
| 정상 PMIC 초기화 | PASS: 주소 4개, rail 36개 selector readback, GPIO 44개 walking pattern, chip별 loopback 2쌍 |
| power 초기화 순서 | PASS: 모든 `ready/check` → `complete` → `power-ready` |
| Linux 소유권 / RTC | PASS: TPS6594 client/regulator/child 없음, PL031 1개 유지 |
| AP I2C 회귀 | PASS: EEPROM 3 client 각각 8×256-byte write/read, 원본 복원; PCA9539 테스트 |
| 4번째 PMIC NACK | PASS: 앞의 3개 성공, `0x68`에서 abort source `0x1`, `FWK_E_DEVICE`; power 진입 없음 (`nack/`) |
| 1초 byte 지연 주입 | PASS: 102110 µs에 `FWK_E_TIMEOUT`; power 진입 없음 (`timeout-quoted/`) |
| Native 정책 검사 | PASS: selector 경계·VSEL·reserved/enable/RTC 보존·GPIO bank·17개 init transaction별 오류 전파 (`test-tps6594.log`) |
| Root focused pytest | PASS: 21 tests; marker 누락·중복·순서·실패를 정상 결과로 인정하지 않음 |
| 기존 full-map 정적 검사 | PASS: 95/95 (`full-map.json`); runtime 증거와 구분 |
| 최종 BSP 빌드 | PASS: 5793 tasks (`bsp-final-build.log`); 기존 forced-run taint 경고 5개 |

`gpio-fixed/measurement.json`에서 begin→complete의 host 관측 시간은
**2.168725초**, SCP counter 시간은 **2.178592초**였다. Console을 5 ms 주기로
관측한 단일 실행이며 로그 출력과 GPIO self-test도 포함한다. 전체 launcher→
Linux ready 시간 51.84초와 PMIC 구간은 별개다. 이관 전 27.68초 host 측정은
Linux BUCK1 probe부터 네 번째 RTC probe까지의 범위였으므로 두 값을 동일
작업의 정밀 speedup으로 해석하지 않는다. 새 경로에는 TPS6594 RTC가 없다.

최종 BSP 재생성 후 `final/`에서 같은 검증을 다시 통과했다. Host PMIC 구간은
**2.173137초**, SCP counter는 **2.182536초**, Linux ready까지는 52.98초였다.
`final/qualification.json`은 PASS이고 guest/EEPROM/PCA9539의 exit status는
모두 0이다. 펌웨어·DTB 배포 파일의 SHA-256은 `artifacts.json`에 기록했다.

Timeout 실험의 최초 `timeout/`은 CCI string quoting 오류로 시작되지 않았으며
driver 검증 결과가 아니다. 수정한 `timeout-quoted/`만 timeout 근거다.
`candidate/`, `diagnostic/`, `completion/`은 완료 상태 처리 및 open-drain
테스트 문제를 수정하기 전의 실패 로그로 남겨 두었다.

재현 명령은 다음과 같다. Firmware 변경 시 SCP와 RSE firmware bundle을
함께 갱신해야 한다.

```sh
source layers/poky/oe-init-build-env build
MACHINE=apollo-qvp bitbake nexios-bsp-initramfs
# workspace root로 돌아온 후, 각 실행 이름은 새 directory여야 한다.
cd ..
python3 build/qbox-apollo-qvp/si-cl0-pmic-20260920/run_measurement.py rerun
python3 build/qbox-apollo-qvp/si-cl0-pmic-20260920/run_measurement.py rerun-nack --fault
python3 build/qbox-apollo-qvp/si-cl0-pmic-20260920/run_measurement.py rerun-timeout --timeout-fault
python3 scripts/test/verify_qbox_si_pmic.py \
  --scp-log build/qbox-apollo-qvp/si-cl0-pmic-20260920/rerun/runtime/qbox-safety-island-cl0.log \
  --guest-log build/qbox-apollo-qvp/si-cl0-pmic-20260920/rerun/guest.log \
  --eeprom-log build/qbox-apollo-qvp/si-cl0-pmic-20260920/rerun/eeprom.log
python3 -m pytest -q tests/test_qbox_si_pmic_validation.py tests/test_qbox_pca9539_board.py
```

측정 harness는 evidence directory의 로컬 실행 도구이고 SSH port 8022를
사용한다. 동시에 다른 QBox 세션이 있을 때는 해당 세션의 실제 SSH port로
조정해야 한다. 재사용 가능한 guest 검사와 로그 판정기는 `scripts/test/`에 있다.

이전 Linux/SCP 이관 전 결과는 [기존 PMIC 검증](tps6594.md)과
[부팅 병목 분석](tps6594-bottleneck-analysis.md)에 보관한다.

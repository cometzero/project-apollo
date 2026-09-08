# HSOC PERI0 / PERI1 pin controllers

Implementation contract for Apollo QVP. This is an HSOC QVP extension, not
an assertion of an existing Arm FVP register interface.

## Topology and register interface

`pinctrl_peri0` uses AP MMIO `0x301e0000`, size `0x10000`. Banks 0–5 have
eight pins each; banks 6–13 have one pin each: 56 pins and 14 bank IRQ
outputs. Bank N uses GIC SPI `334 + N` (architectural INTID `366 + N`).
Physical pin IDs are `bank * 8 + offset`; nonexistent offsets remain holes.

`pinctrl_peri1` uses AP MMIO `0x301f0000`, size `0x10000`. Banks 0–3 have
eight pins each and banks 4–7 have one pin each: 36 pins and 8 bank IRQs.
PERI1 bank N uses GIC SPI `348 + N` (INTID `380 + N`). Both controllers
use the same register ABI and independent state. GPIO line names are
`gp_peri0_0`–`gp_peri0_55` and `gp_peri1_0`–`gp_peri1_35`.

All registers are aligned 32-bit little-endian words. Unsupported offsets,
invalid mux values and invalid electrical settings are rejected.

| Global offset | Meaning |
| --- | --- |
| 0x00 | ID, read-only `0x48535043` |
| 0x04 | Version, read-only `0x00010000` |
| 0x08 | Number of banks, read-only |
| 0x0c | Number of implemented pins, read-only |

Bank N starts at `0x1000 + N * 0x1000`. The first page holds global
registers; bank0 is at `base + 0x1000`, bank13 at `base + 0xe000`.

| Bank offset | Meaning |
| --- | --- |
| 0x00 | Number of pins, read-only |
| 0x04 | Resolved digital input values, read-only |
| 0x08 | GPIO output latch, read/write |
| 0x0c | GPIO output set, write-one-to-set |
| 0x10 | GPIO output clear, write-one-to-clear |
| 0x14 | Per-pin IRQ enable bitmap |
| 0x18 | Pending IRQ bitmap, write-one-to-clear acknowledge |
| 0x1c | Rising-edge IRQ selection bitmap |
| 0x20 | Falling-edge IRQ selection bitmap |
| 0x24 | Active-high level IRQ selection bitmap |
| 0x28 | Active-low level IRQ selection bitmap |
| 0x40 + pin * 4 | Pin configuration |

Pin configuration bits 2:0 select mux: 0=GPIO input, 1=GPIO output,
2/3/4=alternate functions. Bit 4 stores slew-rate (0=slow, 1=fast).
Bits 15:8 store drive strength in mA: 2, 4, 8, 12, or 16. Reset is GPIO
input, slow slew, 4 mA. Output latches and IRQ configuration reset to zero.
Drive and slew are digital configuration metadata, without analog waveform
simulation. GPIO interrupts are sampled in GPIO input mode; level requests
remain pending while the selected level is present, including after ack.

## Peripheral assignment

All current DWC peripheral groups use function 2. Functions 3 and 4 are
available alternate selectors, with no additional peripheral assignment in
this board profile. AP PL011 boot/debug consoles retain their existing path.

| Peripheral | Controller | Bank/pins |
| --- | --- | --- |
| I2C0–3 SDA/SCL | PERI0 | bank0: pairs 0/1, 2/3, 4/5, 6/7 |
| I2C4–5 SDA/SCL | PERI0 | bank1: pairs 0/1, 2/3 |
| SPI0–1 SCLK/MOSI/MISO/CS0 | PERI0 | bank2: 0–3, 4–7 |
| SPI2–3 SCLK/MOSI/MISO/CS0 | PERI1 | bank0: 0–3, 4–7 |
| UART0–1 TX/RX | PERI0 | bank4: pairs 0/1, 2/3 |
| UART2–3 TX/RX | PERI1 | bank1: pairs 0/1, 2/3 |
| GPIO test loopbacks | PERI0 | bank1 4→5, bank1 6→7; bank6 0→bank7 0; bank12 0→bank13 0 |
| GPIO test loopbacks | PERI1 | bank3 0→1; bank6 0→bank7 0 |

The instance CCI `peripheral_routes` lists `id:bank:first:count` entries,
separated by semicolons. IDs 0–5 denote I2C0–5, 6–9 denote SPI0–3, and
10–13 denote UART0–3. An explicit list disables omitted routes. An empty
list retains the original PERI0 mapping for compatibility. Each peripheral's
enable input is bound to exactly one controller.

The existing DWC models exchange I2C transactions, SPI words, and UART bytes.
Mux selection gates these functional paths; this interface does not serialize
SDA/SCL or UART waveforms. SPI currently uses the SSI model's behavioral
loopback. Function selection must affect traffic and cannot be readback-only.

Linux enumerates the banks and peripheral states from `pinctrl.dtsi` using
`hsoc,peri0-pinctrl` or `hsoc,peri1-pinctrl`. Child GPIO banks expose their own GPIO/IRQ domains.
`pinmux` entries use `HSOC_PINMUX(bank, pin, function)`, encoded as
`((bank * 8 + pin) << 8) | function`. Standard `drive-strength` and
`slew-rate` properties configure pin electrical metadata.

## Validation

구현 파일:

- [SystemC model](../../hsoc-stack/tools/qbox-platform/systemc-components/hsoc_pinctrl/include/hsoc_pinctrl.h)
- [Linux driver](../../hsoc-stack/components/primary_compute/linux/drivers/pinctrl/pinctrl-hsoc.c)
- [pinctrl.dtsi](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/pinctrl.dtsi)
- [DT pinmux constants](../../hsoc-stack/components/primary_compute/linux/include/dt-bindings/pinctrl/hsoc.h)
- [SoC wiring](../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/pinctrl.lua)
- [Board loopbacks](../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/peri0-loopback.lua)

`CONFIG_PINCTRL_HSOC=y`를 QVP defconfig에 추가했다. 기존 DWC model의
`pinmux_enable` 입력을 연결했으며, 이 입력이 연결되지 않은 다른 플랫폼은
기존 동작을 유지한다. BSP에는 MMIO 확인용 `devmem2`를 추가했다.

기본 pinctrl state는 각 I2C/SPI/UART node의 `pinctrl-0`에서 참조한다.
I2C/UART는 4 mA·slew 0, SPI는 8 mA·slew 1로 설정된다. 예를 들어
I2C0 state의 pinmux 값은 다음과 같다.

```dts
pinmux = <HSOC_PINMUX(0, 0, 2) HSOC_PINMUX(0, 1, 2)>;
drive-strength = <4>;
slew-rate = <0>;
```

재현은 workspace root에서 실행한다.

```bash
./yocto_build.sh --keep-conf --bsp
./run_qbox_yocto.sh --bsp --headless --keep-running-after-pass \
  --timeout 600 --copy-disks --no-persistent-rse-state \
  --out-dir build/qbox-apollo-qvp/hsoc-pinctrl-runtime
```

Linux BSP shell이 준비되면 다른 터미널에서:

```bash
./scripts/run/ssh_run.sh scripts/test/verify_qbox_hsoc_pinctrl.sh
./scripts/run/ssh_run.sh scripts/test/verify_qbox_hsoc_peripherals.sh
```

전용 시험 guest에서 실행한다. 첫 스크립트는 I2C5의 mux register를
일시 변경하고 원복하며 GPIO line을 요청한다. 두 번째 스크립트는 DWC UART
termios를 시험용으로 설정하고 SPI 시험 모듈을 load/unload한다.

PERI0 최초 구성의 2026-09-08 결과 기준 경로는
`build/qbox-apollo-qvp/hsoc-pinctrl-20260908/`다. 아래 표와 IRQ 관측값은
SPI/UART를 PERI1으로 이동하기 전의 검증 기록이다.

| 검사 | 결과 | 증거 |
| --- | --- | --- |
| HSOC SystemC MMIO/GPIO/IRQ/mux/config/reset | PASS | `pinctrl-model-tests.log` |
| DWC I2C/SSI/UART 및 PCA9539/TPS6594 CTest | 5 targets PASS | `dwc-gating-tests.log` |
| Provider CTest | 46/46 PASS | `provider-tests-final.log` |
| Kernel/DTB 및 최종 BSP | PASS | `bsp-gpio-fix-build.log` |
| QBox BSP boot | `passed=true` | `runtime-fixed/result.json` |
| GPIO·IRQ·DT 설정·I2C mux | PASS | `guest-pinctrl-irq-fix.log` |
| SPI/UART traffic | PASS | `guest-peripherals-final.log` |
| PCA9539/EEPROM 및 TPS6594 | PASS | `pca9539-regression.log`, `tps6594-regression.log` |

Linux에서 14개 GPIO bank와 56핀을 확인했다. 6개 EEPROM read가 성공했고,
I2C5 SDA mux를 0/3/4로 변경하면 I/O error가 발생하며 2로 복구하면
read가 다시 성공했다. GPIO loopback 네 연결 모두 high/low를 확인했다.
각 bank의 rising/falling 이벤트와 ack는 다음과 같이 관측했다.

| Bank/pin | Linux IRQ (이번 실행) | Counter | Ack 후 pending |
| --- | --- | --- | --- |
| bank1 pin5 | 151 | 5 → 7 | 0 |
| bank7 pin0 | 152 | 0 → 2 | 0 |
| bank13 pin0 | 153 | 0 → 2 | 0 |

IRQ 번호는 고정하지 않고 실행 시 탐색한다. GPIO IRQ 항목은 `gpiomon`이
닫히면 사라지므로 counter는 monitor가 살아 있는 동안 읽는다.
Level-high/low 동작과 reset 중 write 억제, 잘못된 MMIO 접근은 SystemC
시험에서 검증했다. Linux GPIO IRQ 시험은 rising/falling에 한정했다.

UART 두 pair는 양방향으로 각각 32바이트를 교환했다. SPI 네 controller는
`spi-loopback-test run_only_test=0 run_only_iter_len=16 loopback=1 loop_req=1`
로 실제 메시지를 실행했고 모두 bind에 성공했다. 대용량 SPI stress는 이번
검증에 포함하지 않았다. SPI는 현재 SSI model의 word-echo backend를
검증하며, bit-level pad나 실제 silicon의 internal-loopback 격리를 검증한
것은 아니다.

초기 kernel compile의 API/header 오류와 GPIO optional pinconf 반환 코드,
provider/GPIO 등록 순서를 수정한 후 재빌드했다. 초기 시험 실패 로그도
보존했다. 최종 정적 검사에서 map parser pytest 3개, ShellCheck,
`git diff --check`, full-map validator 및 core boundary audit가 통과했다.

DT schema 실행은 host 도구 부재로 미검증이다. 전체 coverage audit는
`ap_9_1_1_memory_map: not_available`, `G1: not_run`으로 FAIL이며
`full-coverage-audit.json`에 기록했다. 위 PASS는 구현한 HSOC pinctrl과
실행한 회귀 범위다. 함수 3/4의 추가 peripheral 배선, analog slew/drive,
bit-level serial waveform 및 전체 FVP 동등성은 검증 범위 밖이다.

### PERI1 추가 및 SPI2/3, UART2/3 이동 검증

2026-09-08 증거 경로는 `build/qbox-apollo-qvp/hsoc-peri1-20260908/`다.
`./yocto_build.sh --keep-conf --bsp`로 최종 배선을 포함해 재빌드했다.
Provider 검증용 `QBOX_APOLLO_RUN_UNIT_TESTS = "1"`은 빌드 후 원복했다.

| 검사 | 결과 | 증거 |
| --- | --- | --- |
| 최종 BSP 빌드 | PASS, 5577 tasks, 기존 tainted-task 경고 4개 | `bsp-build-final.log` |
| Provider CTest | 46/46 PASS | `provider-tests-final.log` |
| QBox BSP boot | `passed=true` | `runtime-final/result.json` |
| PERI0/PERI1 GPIO, IRQ, mux/config, EEPROM | PASS | `guest-pinctrl.log`, `guest-pinctrl-final.log` |
| SPI0–3 16-byte loopback, UART 두 pair 양방향 32-byte | PASS | `guest-peripherals.log` |
| PCA9539 및 TPS6594 회귀 | PASS | `pca9539-regression.log`, `tps6594-regression.log` |

PERI1의 8개 GPIO bank/36핀과 MMIO pin count를 확인했다. SPI2/3은
`0x301f1040..0x301f105c`, UART2/3은 `0x301f2040..0x301f204c`에서
mux 2와 DTS의 drive/slew 설정을 확인했다. 기존 PERI0의 해당 핀은
GPIO input으로 남는다. PERI1 bank3 pin0→1과 bank6→7 연결에서
high/low가 일치했고, bank3/7 IRQ는 각각 counter 0→2 및 pending 0으로
rising/falling 전달과 ack를 확인했다. PERI0 bank1/7/13 IRQ도 통과했다.
최초 실행의 PCA9539 unbind/rebind와 겹친 `gpiodetect` 경고를 분리하기
위해 회귀 시험 종료 후 pinctrl 스크립트를 단독 재실행했다. 재실행에서도
PASS이며 PERI1 bank3/7 counter는 각각 3→5, pending은 0이었다.

정적 검사 명령은 `python3 -m pytest -q tests/test_apollo_ap_map_modular_lua.py`
(3 PASS), 두 guest 스크립트의 `shellcheck`, 소유 repository의
`git diff --check`, `validate_qbox_apollo_fvp_full_map.py`,
`audit_qbox_core_boundary.py`다. 전체 coverage audit의 기존
`ap_9_1_1_memory_map: not_available`, `G1: not_run`은 여전히 FAIL이다
(`full-coverage-audit.json`). DT schema, 대용량 SPI stress 및 위의
analog/bit-level/FVP 동등성 제한은 이번에도 검증 범위 밖이다.

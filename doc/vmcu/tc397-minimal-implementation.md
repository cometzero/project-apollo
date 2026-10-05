# 현재 QEMU의 TC397 최소 구현·검증 계획

기준: 2026-10-04. 소유 저장소는 `hsoc-stack/tools/qemu`, 기존 HEAD는 `52c63bb0e10ed1e2709d0aaccc071270418154fc`다. 공개 fork 조사 이후 사용자가 현재 QEMU에 최소 기능을 추가하도록 요청했으므로, 외부 binary 평가에서 **현재 source의 standalone TC397 machine 구현**으로 진행한다. [기존 조사](tc397-qemu.md)는 구현 전의 근거와 공백 기록이다.

후속으로 ASCLIN1과 실제 Zephyr app/shell을 추가했다. 아래 표·시험은 초기 최소 모델 기준이며 최신 UART 매핑·빌드·실행은 [Zephyr 구현 문서](zephyr-implementation.md)를 참조한다.

## 1. 최소 범위

| 항목 | 이번 범위 | 제외/한계 |
|---|---|---|
| CPU | CPU0 하나, TriCore 1.6.2 기반 `tc397` model, interrupt 진입/복귀·WAIT | SMP/AMP, lockstep, MPU와 전체 trap qualification |
| Memory/boot | PFLASH0 3 MiB, DSPR0 240 KiB, PSPR0 64 KiB 및 alias; 직접 ELF boot | flash erase/program, BootROM/UCB/BMHD/HSM, vendor boot chain |
| Timer | STM0, 50 MHz virtual clock, compare interrupt | 실제 oscillator/PLL, clock·power mode parity |
| Interrupt | CPU0 SRC routing, highest-priority 선택, pending clear/ack | 다중 CPU/DMA TOS |
| UART | ASCLIN0 chardev, Tx/Rx와 interrupt | wire bit timing, LIN/SPI mode, QEMU 전용 가상 DMA |
| Reset | QEMU machine reset 후 peripheral 초기화·ELF entry 재시작 | SCU software-reset register, watchdog 만료, PMIC power-cycle |
| 외부 연결 | 독립 `qemu-system-tricore` executable | QBox wrapper/libqemu target, Apollo board wiring, SIL Kit |
| 기타 peripheral | 미구현 주소는 정상 hardware로 가장하지 않음 | SFR catch-all, CAN/QSPI/I2C/Ethernet/PORT/SMU/PMIC 없음 |

현재 `tc37x`, TC277 및 `tricore_testboard`의 기존 동작은 보존한다. 새 interrupt/WAIT 기능은 TC397 CPU에 한정한다. TC4x ISA·주변장치와 외부 fork 전체를 가져오지 않는다. 기존 AArch64 source 및 Yocto provider 설정을 변경하지 않는다.

### 주소와 연결

| 블록 | 주소/크기 | 연결 |
|---|---|---|
| DSPR0 | `0x70000000`, 240 KiB | local alias `0xd0000000` |
| PSPR0 | `0x70100000`, 64 KiB | local alias `0xc0000000` |
| PFLASH0 | `0x80000000`, 3 MiB ROM | uncached alias `0xa0000000`; ELF loader만 초기 적재 |
| ASCLIN0 | `0xf0000600`, `0x100` | SRC TX/RX/error = `0x14/0x15/0x16` |
| STM0 | `0xf0001000`, `0x100` | SRC SR0/SR1 = `0xc0/0xc1`, 고정 50 MHz |
| IR INT/SRC | `0xf0037000`/`0xf0038000` | 256 SRC; CPU0 priority 입력과 acknowledge 출력 |

SRC index는 register byte offset이 아니다. byte offset은 `index × 4`다. ASCLIN과 STM은 32-bit MMIO 접근을 지원한다. UART는 16-byte FIFO와 chardev backpressure를 제공하지만 UART baud·flow control timing은 구현하지 않는다. STM의 비교 기능은 CMPxEN이 켜진 동안 수행하는 최소 모델이다. register access protection, KRST 및 migration/snapshot은 미지원이다. CPU NMI 경로는 board에 연결하지 않았으며, NMI·CSA 고갈·중첩 IRQ·interrupt stack 전환은 이번 기능 시험의 PASS에 포함하지 않는다.

## 2. 구현 순서와 책임

1. `target/tricore/`: 기존 context-save/restore를 재사용하고 TC397의 interrupt·WAIT·reset 상태를 추가한다. CPU와 IRQ controller는 GPIO로 연결하여 target 코드가 특정 board를 직접 참조하지 않게 한다.
2. `hw/intc`, `hw/timer`, `hw/char`: 최소 IR/STM/ASCLIN 모델과 Kconfig/Meson 등록을 추가한다. reset과 pending/overflow를 명시적으로 처리한다.
3. `hw/tricore/tc397.c`: 단일 machine이 CPU·memory·controller를 구성한다. 주소와 IRQ source ID를 고정하고 직접 ELF entry를 reset 시 복구한다.
4. `tests/tcg/tricore/tc397/`: 독립 bare-metal 검증 firmware를 둔다. test startup이 CSA/BIV/ISP를 초기화하며 모델이 firmware 주소를 강제로 설정하지 않는다.
5. root `scripts/test/verify_qemu_tc397.py`: 실제 serial·QMP traffic을 주고 제한 시간 내 결과를 수집한다.

외부 reference의 clock 주석과 실제 값 차이, IRQ priority 비교 누락, software reset 출력 미연결, register catch-all을 그대로 가져오지 않는다. 재사용한 source에는 원저작권과 pinned revision을 남긴다.

## 3. 빌드·부팅·기능 검증 단계

| 단계 | 검사 | 완료 기준 |
|---|---|---|
| BUILD | 현재 QEMU source에서 `tricore-softmmu` 독립 빌드 | 생성한 executable의 TC397 machine/CPU 등록, compiler 오류 없음 |
| BOOT | 로컬 compiler로 만든 bare-metal ELF 실행 | guest가 ASCLIN MMIO를 통해 boot marker 출력 |
| TIMER | STM compare → SRC → CPU vector → ISR | 실제 interrupt 횟수 증가, acknowledge 이후 재발생 제어 |
| IRQ | disable/enable, 여러 pending priority, interrupt 복귀 | mask 동안 ISR 미진입, highest-priority 순서, 올바른 복귀 |
| UART | host→ASCLIN RX→guest 처리→TX | 양방향 payload 일치, RX IRQ와 register 상태 확인 |
| RESET | QMP machine reset | 이전 pending/FIFO 상태 제거, guest 초기화와 boot 재실행 |
| REGRESSION | 기존 `tricore_testboard` ISA/context tests | 기존 TriCore CPU의 연산·CSA tests 유지 |

부팅의 의미는 **자체 bare-metal firmware의 직접 ELF 부팅**이다. Zephyr/AUTOSAR 또는 실제 TC397 boot chain PASS가 아니다. QMP reset은 SCU watchdog/PMIC reset 검증과 구분한다.

빌드는 `build/qbox-apollo-qvp/tc397-minimal/`에서 수행한다. 기존 `build/conf`는 `apollo-qvp`이고 공유 BitBake task는 사용하지 않는다. TriCore compiler는 QEMU가 참조하는 고정 버전을 별도 generated 경로에 두며 system 설치를 대체하지 않는다. CPU·주변장치 build가 완료되면 검증 firmware와 runner로 결과를 생성한다.

## 4. 재현 명령

root에서 다음처럼 standalone build를 만든다. host GCC, Ninja, Python venv, GLib/Pixman 개발 파일이 필요하다. 이 checkout의 `configure`는 host Meson을 직접 찾으므로 bundled wheel로 빌드 전용 Meson 1.10.0을 준비한다. system package와 기존 Yocto build 환경을 바꾸지 않는다.

```sh
repo_root="$PWD"
tc397_out="$repo_root/build/qbox-apollo-qvp/tc397-minimal"
mkdir -p "$tc397_out/qemu-build"
python3 -m venv "$tc397_out/host-tools"
"$tc397_out/host-tools/bin/python" -m pip install --no-index \
  "$repo_root/hsoc-stack/tools/qemu/python/wheels/meson-1.10.0-py3-none-any.whl"
cd "$tc397_out/qemu-build"
PATH="$tc397_out/host-tools/bin:$PATH" \
  "$repo_root/hsoc-stack/tools/qemu/configure" \
  --target-list=tricore-softmmu --without-default-features --enable-tcg \
  --disable-tools --disable-docs --disable-guest-agent --disable-plugins \
  --disable-fdt --disable-werror > ../configure.log 2>&1
ninja -j4 qemu-system-tricore > ../build.log 2>&1
cd "$repo_root"
```

기존 downstream의 `DRAGON` Kconfig 기본값은 모든 TCG target에서 Arm-compatible semihosting을 선택해 TriCore link 오류를 냈다. 이를 `configs/devices/tricore-softmmu/default.mak`에서만 `CONFIG_DRAGON=n`으로 제외했다. 다른 target의 설정은 유지한다.

TriCore compiler는 QEMU의 [Docker recipe](../../hsoc-stack/tools/qemu/tests/docker/dockerfiles/debian-tricore-cross.docker)가 지정하는 GCC 9.4.0이다. archive SHA256은 `06d49e5cbae46e6e523ffc8cedb948f3bfc7411e890c33209d9480dca20c13ef`다. compiler를 `$tc397_out/toolchain/bin/tricore-gcc`에 준비한 뒤 실행한다.

```sh
mkdir -p "$tc397_out/toolchain"
curl -fL --retry 2 \
  https://github.com/bkoppelmann/package_940/releases/download/tricore-toolchain-9.40/tricore-toolchain-9.4.0.tar.gz \
  -o "$tc397_out/toolchain/tricore-toolchain-9.4.0.tar.gz"
printf '%s  %s\n' \
  06d49e5cbae46e6e523ffc8cedb948f3bfc7411e890c33209d9480dca20c13ef \
  "$tc397_out/toolchain/tricore-toolchain-9.4.0.tar.gz" | sha256sum -c -
tar -xzf "$tc397_out/toolchain/tricore-toolchain-9.4.0.tar.gz" \
  -C "$tc397_out/toolchain"
python3 scripts/test/verify_qemu_tc397.py \
  --qemu build/qbox-apollo-qvp/tc397-minimal/qemu-build/qemu-system-tricore \
  --cc build/qbox-apollo-qvp/tc397-minimal/toolchain/bin/tricore-gcc
```

[runner](../../scripts/test/verify_qemu_tc397.py)는 firmware를 빌드하고 별도 Unix UART/QMP socket을 생성한다. guest 단계별 timeout을 두고 정상 완료 또는 오류 이후 자신이 시작한 QEMU를 종료한다. 기존 QBox session을 종료하지 않는다. [validation/result.json](../../build/qbox-apollo-qvp/tc397-minimal/validation/result.json)에 executable·ELF·source hash, 실제 명령, cycle별 결과와 미지원 범위를 기록한다.

기존 TriCore 회귀 시험은 QEMU가 생성한 test Makefile에 로컬 toolchain만 지정해 재현한다. Docker image를 새로 빌드할 필요가 없다.

```sh
make -C "$tc397_out/qemu-build/tests/tcg/tricore-softmmu" -j4 \
  CC="$tc397_out/toolchain/bin/tricore-gcc" \
  AS="$tc397_out/toolchain/bin/tricore-as" \
  LD="$tc397_out/toolchain/bin/tricore-ld" all
make -C "$tc397_out/qemu-build/tests/tcg/tricore-softmmu" \
  QEMU="$tc397_out/qemu-build/qemu-system-tricore" \
  TIMEOUT=10 run
```

## 5. 결과 기록 및 후속 단계

2026-10-04 현재 working tree를 위 명령으로 빌드하고 실행했다. 기본 reset PC `0xa0000000`과 다른 **ELF entry `0xa0000100`**을 사용했다.

| 항목 | 결과 | 실행 증거 |
|---|---|---|
| QEMU 빌드 | **PASS** | `configure.log`, `build.log`; 새 machine/CPU 등록, 현재 source에서 link 완료 |
| firmware 빌드 | **PASS** | GCC 9.4.0, `-mtc162 -Wall -Wextra -Werror`; `validation/firmware-build.log` |
| cold boot | **PASS, 21/21** | `validation/result.json`, `serial.log`; CPU/주변장치 reset 상태, DSPR/PSPR/flash alias, flash write 보호 |
| IRQ | **PASS** | global mask, SRC disable/re-enable, CCPN threshold, PIPN read-only, zero priority 차단, 동시 pending 우선순위 |
| STM0 | **PASS** | counter 증가, compare0→SRC→CPU→guest ISR 5회, disable 후 ISR 증가 없음 |
| ASCLIN0 | **PASS** | host가 `V` 전송, RX IRQ에 의한 WAIT 복귀, guest TX echo를 host가 수신 |
| QMP reset | **PASS, 21/21** | QMP RESET event, 비기본 ELF entry 복원, CPU CSFR/주변장치 reset 상태 및 전체 suite 재실행 |
| 기존 TriCore 회귀 | **PASS, 21/21** | `tcg-result.json`, `tcg-run.log`; `tricore_testboard -cpu tc37x`, 기존 19개 assembly 및 2개 C boot/CSA 시험 |
| Apollo QBox/Zephyr/vendor firmware | **SKIP** | 이번 변경에서 실행하지 않음 |
| CAN/SPI/PMIC/SCU/watchdog/안전·시간 parity | **UNSUPPORTED** | 최소 모델 범위 밖 |

21개/cycle은 19개 guest assertion과 boot marker·host echo 검사다. UART TX는 데이터 전달을 검증했으며 TX/error IRQ·FIFO 경계와 STM compare1의 전수 검증은 수행하지 않았다. CPU NMI/FCU/FCD·중첩 IRQ, 실제 silicon reset register 전체값과 물리 시간 정확도 역시 미검증이다. QEMU stderr인 `validation/qemu.log`는 비어 있다.

실행한 QEMU SHA256은 `4351f338794c092d68119f7387371862a434aa936e49d007d2a1a471ff9ab062`, firmware SHA256은 `9e62930dbe841eac091e9dab8123e47258265afe60938d8c3e2ecf50612b0c49`다. 상세 source·runner hash와 명령은 JSON에 보관한다. 이 hash는 미커밋 working tree에서 생성한 artifact 기준이며 source HEAD만으로 동일 binary를 식별하지 않는다.

첫 runtime의 board RAM owner 타입 오류는 보드 RAM/ROM 등록의 owner를 `NULL`로 수정하여 해결했다. 실패 로그는 `validation-first/`에 보존했다. 소스 공백 검사와 checkpatch를 수행했으며 새 board 파일의 LGPL 계열 라이선스 선택에 대한 checkpatch 권고 1건을 남긴다. 기존 LGPL reference에서 유래했으므로 원저작권과 라이선스 계열을 유지했다.

이번 결과는 standalone firmware 개발용 최소 기능의 실행 증거다. 단계별 구현·빌드·부팅·기능 검증 계획 P-MIN은 완료이며, 다음 단계는 아래 순서다.

1. **P0/P1 UART 계약과 bridge:** console과 binary protocol 분리, heartbeat sequence/epoch/timeout 및 AP UART 연결은 [후속 구현](uart-heartbeat-implementation.md)에서 완료했다. AP helper 재시작 중 MCU의 counter 지속도 확인했다. Apollo 하드웨어 reset 중 동작 검증은 남아 있다.
2. **P3 RTOS 평가:** pinned Zephyr/toolchain을 별도로 준비하고 현재 최소 모델에서 필요한 register만 추가한다. 기존 Apollo Zephyr tree를 TriCore 지원본으로 임의 교체하지 않는다.
3. **vMCU 제어:** MCU watchdog·PORT/GPIO·reset arbiter를 구현한 뒤 hang/reset 시험을 추가한다. SCU software reset 및 watchdog expiry는 QMP reset과 별도 통과 조건이다.
4. **P2 차량 CAN:** MCMCAN register/IRQ/driver 경로와 SIL Kit frame bridge를 각각 검증한다. host gateway만 통과하면 CAN driver PASS를 부여하지 않는다.
5. **P4/P5 보드 전원·시간축:** SI CL0 PMIC owner/proxy 계약과 AON supervisor를 구현하고, TriCore libqemu/QBox instance 및 SIL Kit 시간 동기화를 평가한다. 기존 [전원 계획](control-and-power.md)의 권한·rail·reset 범위를 유지한다.

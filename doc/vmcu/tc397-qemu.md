# TC397 QEMU 재사용 조사와 도입안

조사일: 2026-10-04. 상위 문서: [vMCU 통합 계획](README.md).

**후속 변경:** 이 문서는 이식 전 조사 기록이다. 이후 사용자 요청으로 현재 `hsoc-stack/tools/qemu`에 TC397 최소 모델을 추가했다. 현재 구현·빌드·부팅·기능 결과는 [최소 구현 문서](tc397-minimal-implementation.md)를 기준으로 한다. 아래의 “현재 source” 비교는 명시된 기존 HEAD의 상태이며 새 working-tree 구현을 포함하지 않는다.

## 1. 판단

**TC397 QEMU 구성을 재사용하는 방향이 타당하다. 외부 QEMU로 먼저 검증할 우선 후보로 `linumiz/qemu-tricore`를 선정한다.** 이 fork에는 `KIT_AURIX_TC397B_TRB` machine과 TC39x 메모리·주변장치 구성이 있으며, Zephyr 공식 `qemu_tc3x` 문서도 해당 fork를 안내한다. [Zephyr 공식 문서](https://docs.zephyrproject.org/latest/boards/qemu/tricore/doc/index.html), [fork v1.0.0](https://github.com/linumiz/qemu-tricore/releases/tag/v1.0.0)

앞선 계획은 Apollo checkout의 TC277/TriCore 지원과 QBox 연결만 확인했다. **조사 기준 HEAD에는 TC397이 없었지만 공개 TC397 모델을 활용할 수 있다.** generic Arm MCU를 새로 조합하기 전에 이 모델로 TriCore firmware·timer IRQ·UART를 평가하는 편이 사용자 목표에 더 가깝다.

단, 이 모델은 완성된 automotive vMCU가 아니다. TC397 전체 주변장치, 6-core 동작, lockstep·SMU·watchdog 안전 동작, 기존 NVIDIA/Vector AUTOSAR firmware 호환을 즉시 제공하지 않는다. 도입 결과는 다음처럼 구분한다.

| 목표 | 판단 |
|---|---|
| TC397 계열 ISA/메모리에서 작은 firmware와 RTOS 실행 | **유망한 재사용 후보**. 공개 Zephyr 실행 사례가 있으나 우리 firmware의 실행 검증은 아직 필요 |
| Apollo와 UART로 heartbeat/관리 protocol 연결 | **우선 PoC로 권장**. ASCLIN chardev를 재사용하고 QBox 측 socket adapter 필요 |
| TC397 CAN driver로 실제 controller IRQ 처리 | **추가 구현 필요**. 조사한 TC397 composition에 MCMCAN 없음 |
| QBox Lua에서 TC397 QemuInstance 즉시 추가 | **현재 불가**. TriCore libqemu build/target/wrapper 및 machine ownership 통합 필요 |
| NVIDIA DRIVE의 TC397 firmware를 그대로 실행 | **미검증**. 동일 part 이름은 보드·주변장치·boot·MCAL 호환의 증거가 아님 |

## 2. 네 가지 QEMU를 구분해야 한다

| 대상 | 확인한 상태 | 적용 의미 |
|---|---|---|
| 현재 Apollo QEMU source | SHA `52c63bb0e10ed1e2709d0aaccc071270418154fc`, `VERSION=10.2.92`; TC277/testboard, `tc37x` ISA 1.6.2 CPU | TC397 board는 없고 CPU interrupt execution도 미구현 |
| host `/usr/bin/qemu-system-tricore` | 직접 실행한 버전 8.2.2; TC277/testboard만 나열 | host 명령을 그대로 실행해도 TC397이 나오지 않음 |
| QEMU upstream | 조사한 master의 TriCore machine 목록은 TC277/testboard 중심 | upstream TriCore 지원과 아래 fork의 TC397 지원을 구분 |
| Linumiz fork v1.0.0 | release 2026-04-17, commit `9e888198363d89048baf3776b7784f2680703609`; TC397 machine 제공 | 신규 평가 대상. 기존 Apollo/libqemu tree를 교체하지 않고 별도로 pin |

조사 기준 HEAD의 `target/tricore/cpu.c`는 interrupt execution을 구현하지 않았다. 이후 추가한 `tc397` CPU 기능과 기존 `tc37x`를 구별해야 한다. [TC277 board](../../hsoc-stack/tools/qemu/hw/tricore/triboard.c)도 TC397 설정이 아니다. [upstream machine 목록](https://raw.githubusercontent.com/qemu/qemu/2a0ac9c8ac2d303ca515dc819043409aef18cab5/hw/tricore/meson.build)은 해당 SHA로 확인했다.

fork release 설명의 base는 QEMU `v11.0.0-rc4`이며, 실제 배포 binary와 source `VERSION` 출력은 **10.2.94**였다. 이 차이를 오류로 단정하지 않고 재현성 정보로 모두 보존한다. release 이름만으로 버전을 비교하지 않는다. 배포 archive의 SHA256은 `6d75f626a70eb9ea2cae3516b4a34e19e7c7e1fb111d0e126f78c0fdbc55f797`이다.

## 3. 기존 모델에서 가져올 수 있는 것

| 블록 | fork source 확인 | 활용과 제한 |
|---|---|---|
| Machine/CPU | `triboard.c`: TC397B machine, `max_cpus=1`; `tc39xb_soc.c`: `tc3x` CPU 하나 | CPU0 firmware 실행 기반. CPU1~5 memory region이 있어도 multi-core 실행이 되는 것은 아님 |
| 메모리 | DSPR/PSPR, flash 영역, LMU, local/cached/uncached alias | firmware linker layout 검토에 활용. flash가 RAM backing이므로 erase/program/보호 기능 검증은 아님 |
| Interrupt Router | SRC/ISP 연결, CPU IRQ/NMI 진입과 context 처리 | 현재 Apollo TriCore의 interrupt 공백을 메울 후보. 중첩·동시 pending·CSA 소진을 별도 시험 |
| STM timer | STM0→IR→CPU 연결, `fstm=50 MHz` | tick/timeout 기반. 코드 주석의 100 MHz보다 실제 clock 값과 DTS를 기준으로 맞춤 |
| ASCLIN0 UART | `serial_hd(0)` chardev, RX/TX/error IRQ 연결 | UART transport 후보. source의 instant-TX 방식은 wire baud timing과 다름 |
| SCU | clock/status, sleep 및 일부 reset/watchdog register 접근 | board 전원·실제 watchdog 만료 기능과 구분 |
| SFR catch-all | 미구현 SFR 공간에 register 값을 저장하고 읽어주는 fallback | register readback 성공이 해당 hardware 기능의 존재를 뜻하지 않음 |

근거: [TC39x SoC composition](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/tricore/tc39xb_soc.c), [machine 정의](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/tricore/triboard.c), [interrupt 진입](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/target/tricore/cpu_helper.c), [ASCLIN](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/char/tricore_asclin.c), [SCU](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/tricore/tricore_scu.c), [SFR fallback](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/tricore/tricore_sfr.c).

조사한 TC397 composition에는 **MCMCAN, QSPI, I2C, Ethernet MAC, 실제 PORT/pinmux, SMU/FSP 및 외부 PMIC**가 연결되어 있지 않다. 따라서 이 주소에서 값을 읽고 쓰는 firmware가 진행되더라도 CAN frame, SPI transaction, GPIO edge가 발생하는지 별도로 확인해야 한다. SFR fallback은 미구현 peripheral 접근을 드러내지 않을 수 있으므로 필요한 register 범위를 추적하고 미지원 접근을 qualification 실패로 분류한다.

Zephyr 공식 문서도 SMP/AMP/MPU 미지원을 명시한다. lockstep·ECC fault reaction이나 보호 격리를 이 모델로 검증했다고 주장하지 않는다. 공개 sample 실행 보고와 현재 프로젝트의 traffic PASS도 구별한다.

### 3.1 수용 전에 점검할 source 위험

- Interrupt Router의 `irq_evaluate()`는 같은 TOS에 대해 발견한 pending source를 계속 대입한다. priority 비교가 없어 동시 interrupt 우선순위를 먼저 확인해야 한다. timer 하나만 동작하는 시험으로 CAN+UART+timer 부하를 승인하지 않는다. [IR source](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/hw/intc/tricore_ir.c)
- SCU의 software reset request는 `reset_line`을 올리지만 TC397 composition에서 이 출력을 reset consumer에 연결하는 경로를 확인하지 못했다. MCU firmware reset과 QMP `system_reset`을 같은 검증으로 취급하지 않는다.
- CPU reset에는 BIV/FCX/ISP 값을 강제로 쓰는 코드 뒤에 `cpu_state_reset()`이 호출된다. 최종 reset 상태와 firmware의 CSA·vector 초기화를 확인해야 한다. 주석의 값을 실제 reset 보장값으로 인용하지 않는다. [CPU source](https://raw.githubusercontent.com/linumiz/qemu-tricore/v1.0.0/target/tricore/cpu.c)
- ASCLIN은 즉시 전송과 가상 helper 경로를 포함한다. standard ASCLIN register를 사용하는 firmware 경로와 QEMU 전용 fast path를 구분한다.

이는 source에서 발견한 점검 항목이며 이번 조사에서 guest traffic으로 재현한 결함 목록은 아니다.

## 4. 권장 도입: 독립 실행 PoC 후 QBox 내부 통합 판단

### 4.1 첫 단계 — 기존 TC397 machine을 그대로 실행

Apollo QBox 옆에 **별도 `qemu-system-tricore` process**를 둔다. 이때 기존 TC397 machine이 CPU·memory·IR·STM·ASCLIN을 생성한다. Apollo 내부 RSE/SI firmware와 libqemu build는 유지한다.

| 경로 | 초기 방식 | 후속 작업 |
|---|---|---|
| TC397↔Apollo 상태 통신 | TC397 ASCLIN0 chardev↔Unix/TCP socket↔QBox UART byte adapter | 양방향 framing·epoch·timeout; AP reset 동안 MCU 지속 실행 확인 |
| TC397↔Vehicle CAN | 우선 firmware 수준 message↔host CAN/SIL Kit gateway로 protocol fixture | TC397 MCMCAN model/IRQ와 실제 driver 경로 구현 뒤 controller 검증 |
| fault/reset GPIO | 별도 board signal adapter와 explicit signal protocol | TC397 PORT register→signal 및 Apollo reset arbiter 연결 |
| PMIC | 기존 SI CL0 소유권 유지; UART로 상태/정책 요청 | TC397 direct I2C/SPI PMIC owner 이전은 해당 controller와 실물 wiring 확정 후 |
| 시간 | 초기 비동기 기능 통신, 각 시각·왕복 지연 기록 | deadline 검증은 QEMU/SystemC/SIL Kit 진행 상한을 묶은 이후 |

단일 ASCLIN0를 console과 binary protocol이 동시에 사용하면 데이터가 섞인다. control mode에서는 console/shell 출력을 끄거나 다른 debug 경로로 옮긴다. 두 번째 UART를 임의로 사용할 수 있다고 가정하지 않는다. UART를 통해 CAN payload를 host가 전송하는 초기 fixture는 **TC397 CAN driver 검증이 아니다**.

SIL Kit QEMU chardev adapter를 활용해 외부 연결을 시험할 수 있지만, 이 방식만으로 TC397의 CAN/QSPI/PMIC peripheral이 생기지는 않는다. 기존 [SIL Kit 계획](sil-kit.md)의 thread·time·CAN evidence 경계를 유지한다.

### 4.2 다음 단계 — QBox 안의 TriCore libqemu

현재 [QemuInstance](../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h)는 `-M none -m 0` 기반으로 QBox가 객체를 조합한다. 일반 QEMU executable의 `-machine KIT_AURIX_TC397B_TRB`와 소유권이 다르므로 Lua 인자 한 줄 추가로 완료할 수 없다.

| 소유 위치 | 필요한 작업 |
|---|---|
| QEMU `target/tricore`, `hw/tricore`, `hw/{char,timer,intc}` | CPU context/interrupt 변경을 포함한 의존성 묶음 이식. board 파일만 가져오지 않음 |
| [qbox-libqemu-native.bb](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-libqemu-native.bb) | 현재 `aarch64`에 `tricore` target/package/sysroot 검사 추가 |
| QEMU [qemu.cmake](../../hsoc-stack/tools/qemu/qemu.cmake), [meson.build](../../hsoc-stack/tools/qemu/meson.build) | `libqemu-system-tricore.so` 생성 및 symbol/ABI 검증 |
| QBox [target_info.h](../../hsoc-stack/tools/qbox/qemu-components/common/include/libqemu-cxx/target_info.h), QemuInstance target 변환 | `TRICORE` target, library 선택, CPU wrapper 추가 |
| QBox/QBox-platform 신규 TriCore wrapper | CPU 진행·reset·interrupt·CSA/boot state 중 generic QOM으로 부족한 API만 추가 |
| Apollo board/vp 구성 | MCU local router/memory/firmware와 board UART/GPIO/CAN 연결, Apollo reset fanout에서 제외 |

내부 통합 시에는 **TC397 SoC 전체를 감싸는 wrapper**와 **CPU/주변장치를 개별 wrapper로 조합하는 방식** 중 하나를 택한다. 먼저 전자를 평가하면 기존 memory map과 IRQ wiring 재사용이 쉽다. 다만 현재 `-M none` 방식 안에서 SoC 생성·CPU thread 등록·SystemC 시간 연동이 가능한지 작은 prototype으로 확인해야 한다. 두 방식을 섞어 CPU·RAM·timer를 중복 생성하지 않는다.

외부 fork로 활성 Apollo QEMU 전체를 교체하지 않는다. 비교용 checkout에서 필요한 commit 집합과 API 차이를 검토하고, AArch64 regression을 유지하며 TriCore target만 추가하는 방향을 우선한다. 이식 범위가 크면 외부 process backend를 계속 사용하는 것도 유효하다.

## 5. Firmware와 toolchain

새 vMCU firmware의 첫 후보는 **Zephyr `qemu_tc3x`**다. 공식 board 설정의 machine 이름, linker memory, STM clock을 pin한 QEMU와 맞춘다. 이번에 확인한 Zephyr main SHA는 `894020886d647a5f9b8a58bdf2cb8c211a62716b`이다. [board 설정](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/894020886d647a5f9b8a58bdf2cb8c211a62716b/boards/qemu/tricore/board.cmake), [DTS](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/894020886d647a5f9b8a58bdf2cb8c211a62716b/dts/tricore/qemu/tc3x.dtsi)

현재 Apollo SI용 Zephyr source는 4.1.0이며 조사한 checkout에는 `arch/tricore`와 `boards/qemu/tricore`가 없다. 기존 SI 전체를 새 Zephyr로 올리는 대신 vMCU 전용 version/toolchain/build directory를 별도로 둔다. TriCore compiler·ABI·newlib/picolibc·linker script·startup/CSA 설정까지 manifest로 고정한다. 이번에는 TriCore compiler를 설치하거나 firmware를 빌드하지 않았다.

기존 AUTOSAR/Vector image 재사용은 요구하는 MCAL, multicore boot, watchdog/ENDINIT, SMU, flash/UCB/BMHD/HSM, board peripheral 의존성 목록부터 확인한다. ELF loading 성공과 vendor boot chain 재현을 구분한다. firmware의 사용권과 재배포 조건도 QEMU의 source license와 별도다.

## 6. 이번 조사에서 실행한 확인과 다음 통과 조건

배포 archive를 `build/qbox-apollo-qvp/vmcu-tc397-research/`에 받아 별도 경로에서 실행했다. host QEMU나 Apollo library를 교체하지 않았다.

| 확인 | 결과 | 증거 한계 |
|---|---|---|
| 배포 binary `--version` | PASS, 10.2.94 | firmware 실행 아님 |
| `-machine help` | PASS, TC397B machine 존재 | peripheral traffic 아님 |
| `-cpu help` | PASS, `tc2x`, `tc3x`, `tc4x` | multi-core 지원 아님 |
| TC397 `-S` + QMP | PASS, `prelaunch`, `running=false`, CPU0 `tc3x-tricore-cpu` 확인 후 정상 종료 | **machine 생성만 확인. guest 명령·Zephyr boot·IRQ·UART traffic은 미실행** |

상세 command/출력은 [binary-probe.json](../../build/qbox-apollo-qvp/vmcu-tc397-research/binary-probe.json)에 있다. 이 경로는 generated evidence이며 Git에 포함하지 않는다. source snapshot·release metadata·archive checksum도 같은 디렉터리에 보존했다.

실제 도입의 순서는 다음과 같다.

1. **TC-1:** 고정한 compiler와 Zephyr로 hello-world 및 sleep/tick firmware 실행. ELF entry/reset-vector 계약 확인.
2. **TC-2:** STM interrupt, context switch, WAIT wake, 중첩·동시 pending IRQ, CSA exhaustion 시험.
3. **TC-3:** ASCLIN 양방향 CRC/sequence/timeout, console 분리, host disconnect/overflow 시험.
4. **TC-4:** Apollo와 외부-process heartbeat 연결. AP만 정지/reset하고 MCU counter·차량 fixture 지속 관찰.
5. **TC-5:** MCU software reset/watchdog·GPIO와 MCMCAN을 필요한 범위로 구현. CAN Tx/Rx FIFO→IRQ→ISR 증거 확보.
6. **TC-6:** 앞 단계가 통과하면 QBox 내부 TriCore libqemu와 virtual-time profile의 비용을 비교해 채택 결정.

따라서 계획의 MCU 우선 평가 순서는 **TC397 fork 독립 실행 → UART 기반 감독 PoC → 필요한 CAN/reset 기능 보강 → QBox 내부 통합 판단**으로 바꾼다. generic Arm backend는 TriCore toolchain/모델 제약으로 목표 시험이 막힐 때의 대안으로 유지한다.

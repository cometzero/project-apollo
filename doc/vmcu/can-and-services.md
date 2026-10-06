# TC397 CAN/SIL Kit와 Apollo 제어 서비스

2026-10-05 구현 기록. 기존 [SI CL0 PFDI Safety Channel](si0-safety-channel.md)의
5초 정기 보고와 독립 GPIO를 유지하면서 차량 CAN, PMIC 조회, AP 복구·종료·wake,
vMCU 단독 reset 재협상을 추가했다. 아래 전원 종료 범위는 **AP 코어 OFF와
SYSTOP/SI/RSE 유지**다. PMIC rail 차단과 SoC cold power cycle은 아직 지원하지 않는다.

## 실행

```sh
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp --sil-kit
```

TC397 QEMU·Zephyr firmware·SIL Kit SDK/registry/participant는 위 `--bsp`에서 함께 빌드한다.
SIL Kit만 갱신할 때는 `./yocto_build.sh vmcu-silkit-native`를 사용한다.
현재 경로는 [Yocto 통합 안내](zephyr-implementation.md#현재-빌드-경로-yocto-통합)를 따른다.
`--sil-kit`는 별도 registry와 `TC397CanBridge`/`VehicleRestbus`를 시작한다.
외부 registry는 `--sil-kit-registry silkit://HOST:PORT`로 지정한다. 두 participant가
준비되고 QEMU CAN endpoint와 연결된 다음 TC397 CPU를 시작한다. 필수 process
실패는 launcher 실패로 기록하며, launcher가 만든 process만 정리한다.
기본 registry는 실행마다 분리한다. 외부 registry를 지정하면 그 registry의
`VehicleCAN` 네트워크에 참여하므로 시험용 ID를 다른 보드와 공유하게 된다.
네트워크를 별도로 선택하는 수동 실행은 [native participant 안내](../../scripts/silkit/README.md)를 따른다.

기본 restbus는 수신을 기록한다. 차량에서 AP 복구·종료·wake 시험을 하려면
`--sil-kit-allow-actuation`을 명시한다. 이 옵션은 host 시험 도구의 오조작 방지이며
보안 인증이 아니다. 현재 네트워크는 신뢰하는 로컬 SIL 시험망을 전제로 한다.
DBC/ARXML 대신 아래의 공개된 시험용 메시지를 사용한다.

실행 output directory의 `vehicle-can.in` FIFO가 restbus 입력이다.
`tc397-uart-input.fifo`는 Zephyr shell 입력이다. tmux TC397 창에서도 같은 shell을 사용한다.

```sh
printf 'command 1 0\n' > "$OUT_DIR/vehicle-can.in"
printf 'vmcu-cli pmic rail 0\n' > "$OUT_DIR/tc397-uart-input.fifo"
```

| Zephyr shell | 동작 |
|---|---|
| `vmcu-cli status` | SI PFDI 종합 상태/5초 보고/고장 원인 |
| `vmcu-cli apollo ping`, `safety ping` | 독립 AP/SI UART 관리 응답 |
| `vmcu-cli pmic rail 0` | BUCK1부터 rail index 0..8의 enable·설정 전압 |
| `vmcu-cli pmic fault 0` | TPS6594 live STAT index 0..10, 비파괴 조회 |
| `vmcu-cli recover start`, `recover status` | SI에서 AP 복구 요청/진행 상태 |
| `vmcu-cli power off`, `power on`, `power status` | graceful AP-only 종료/GPIO wake/진행 상태 |
| `vmcu-cli can status` | driver state, RX/TX completion/error/drop counter |
| `vmcu-cli can trace on`, `can trace off` | 수신 frame 진단 출력 |
| `vmcu-cli can send 0x123 0 0001020304050607` | classic CAN 송신 |
| `vmcu-cli can restart` | stop/start로 transport fault의 bus-off 복구 |

CAN 송신 flags는 IDE=1, FDF=4, BRS=8이다. FD extended+BRS는 13이며 payload
길이는 CAN DLC로 정확히 표현 가능한 길이여야 한다. 상태 로그는 변화 시에만 출력한다.

## 실제 데이터 경로와 소유권

| 경계 | 구현 |
|---|---|
| Zephyr app → CAN driver | `zephyr_vmcu_src/src/vehicle_can.c`, Zephyr `can_send()`/RX callback |
| TC397 driver frontend | `zephyr_vmcu_src/drivers/can_tc397.c`, upstream `can_mcan.c` 재사용 |
| CAN0 node0 | QEMU `hw/net/can/tc397_can.c`, MRAM `0xf0200000` 32 KiB, core `0xf0208200` |
| RX/TX interrupt | SRC_CAN0INT0/1 `0xf00385b0/5b4`, source 364/365, CPU priority 13/14 |
| M_CAN → host | 선택적 `tc397-can.chardev`, 92-byte CAN1/CRC32/epoch/token |
| 차량 네트워크 | `scripts/silkit/participant.cpp`, 실제 SIL Kit 5.0.7 CAN Service |
| 실행 수명 | `scripts/run/qbox_tc397.py`, `scripts/run/qbox_silkit.py` |
| AP/SI 제어 | ASCLIN0/AP DW UART2, ASCLIN2/SI PL011, 기존 PORT0/GPIO |

TC397은 계속 별도 QEMU process다. CAN endpoint는 UART byte를 CAN으로 해석하는
shim이 아니다. 실제 firmware의 MRAM/filter/FIFO/Tx request와 RX/TX IRQ를 거친다.
TC3xx에는 generic M_CAN ILS/ILE이 없으므로 frontend가 GRINT1/2와 IE로 변환한다.
Zephyr IRQ table의 크기는 CPU priority 256개가 아니라 SRC index를 포함하도록 512다.

SIL Kit callback은 payload를 bounded queue의 소유 메모리로 복사한다. callback
thread에서 QEMU MMIO/SystemC 객체를 직접 접근하지 않는다. QEMU TX 성공은 실제
`AddFrameTransmitHandler` 결과를 받은 경우에만 완료한다. 통신 단절/실패/ACK timeout은
TX 성공으로 대체하지 않고 QEMU의 기능적 bus-off와 실패 callback으로 전달한다.

이 transport bus-off는 CAN 물리 error confinement의 TEC 누적을 재현한 결과가 아니다.
SIL Kit simple CAN의 성공 callback도 전기적 ACK slot 또는 수신 app의 처리 완료와
다르다. [공식 CAN Service](https://vectorgrp.github.io/sil-kit-docs/api/services/can.html).
프로세스들은 autonomous lifecycle과 비동기 시간을 사용한다. 결정적 bus 중재,
bit timing, transceiver, 공통 virtual time/FTTI는 미지원이다.

## 차량 메시지 계약

Network `VehicleCAN`, MCU controller `VMCU_CAN0`. 모든 다중 byte 값은 little endian.
ID는 standard 11-bit, 메시지는 CAN FD이며 BRS는 명령 수신에서 선택 사항이다.

| ID/길이 | payload |
|---|---|
| `0x510`, 32 byte, 5초/상태 변화 | 0:version=1, 1:safety state, 2:fault, 3:GPIO; 4:SI epoch, 8:MCU cookie, 12:보고 sequence; 16/18/20/22:active/online/fault/off 각 LE16; 24:last command sequence; 28:policy flags(bit0=session ready) |
| `0x600`, 24 byte | 0:version=1, 1:op, 2..3:0; 4:SI epoch, 8:cookie, 12:command sequence, 16:arg, 20:0 |
| `0x601`, 24 byte | 0:version=1, 1:op, 2:result, 3:state; 4:SI epoch, 8:cookie, 12:command sequence, 16:value, 20:0 |

차량 op: 1=상태, 2=AP ping, 3=PMIC rail, 4=PMIC fault, 5=AP recover,
6=graceful AP off, 7=AP on/wake. Result: 0=OK, 1=UNSUPPORTED, 2=INVALID,
3=STALE, 4=I/O 오류, 5=현재 이용 불가. OK는 해당 요청의 응답이며, 복구 완료와
Linux/PFDI 정상 복귀는 후속 상태로 확인한다.

명령은 ID/FD/길이/예약 byte/op/arg를 검사한다. SI epoch와 MCU cookie가 같고
sequence가 증가해야 실행한다. 정확히 같은 마지막 요청은 캐시 응답만 재전송하고,
내용이 바뀐 중복이나 stale 요청은 실행하지 않는다. 명령 처리/실제 UART 전송 직전에도
SI epoch와 Safety UART freshness를 확인한다. vehicle actuator용 출력 ID는 정의하지
않았으므로 고장 발생 시 브레이크·조향을 자동 제어하지 않는다.

MCU cookie는 재부팅 후 SI의 SESSION_QUERY(op7, seq0)로 마지막 transaction을
조회한 뒤 새 PING transaction을 실행해 얻는다. SI cache를 지우거나 이전 sequence를
다시 허용하지 않는다. AP 관리도 매 요청 전에 cursor를 조회해 vMCU-only reset 후
재연결한다. SI epoch 변경 시 CAN cookie/cache를 폐기한다. SI는 READY/FAULT/ALL_OFF 변경 시에도 즉시 보고한다. 정기 5초 deadline은 이동하지 않으며, 의도된 AP 종료/복구에서 SOC_ERROR가 멈춘 이유를 다음 정기 보고까지 기다리지 않고 vMCU에 전달한다.

## PMIC와 AP 전원·복구

TPS6594 `0x48`의 소유자는 계속 SI CL0다. vMCU가 I2C의 두 번째 master가 되지 않는다.
SI framework thread에서 기존 `mod_pmic_api`/TPS6594 driver를 사용한다.
Rail 응답의 bit31은 enable, 하위31bit는 설정 전압(uV)이다. 측정 전압/PGOOD가 아니다.
Fault 응답은 11개 live STAT byte이며 latched IRQ를 읽어 지우지 않는다. 부팅 시
`policy=preserve`, `probe=PASS`를 유지하고 rail 설정을 쓰지 않는다.

SI UART op8/9는 PMIC 조회, op10/11은 복구 요청/상태, op12/13은 종료 arm/전원 상태다.
복구 상태: 0=IDLE, 1=PENDING, 2=OFF, 3=RELOAD, 4=BOOT, 5=COMPLETE, 6=FAILED.
전원 상태: 0=RUN, 1=ARMED, 2=QUIESCING, 3=AP_OFF, 4=WAKING, 5=FAILED.

1. vMCU가 SI 종료 arm(30초)을 확인한 뒤 AP peer에 종료 요청을 보낸다.
2. AP는 응답 UART drain, `sync()` 후 kernel poweroff/PSCI를 호출한다.
3. SI는 arm된 trusted AP SCMI shutdown을 AP 코어 OFF 요청으로 처리한다.
   RSE shutdown notification과 SYS 전체 종료는 발생시키지 않는다.
4. 실제 모든 AP core power-domain OFF를 확인한 뒤에만 IST_DONE_N을 low로 한다.
   SOC_PWR_REQ는 arm/종료/OFF 동안 high다. SI/MCU와 CAN 보고는 계속 실행한다.
5. AP_OFF에서 MCU_SOC_WAKE rising edge가 기존 RSE BL2 reload → PFDI/context 재준비
   → boot core release → watchdog 재설정 경로를 실행한다.

AP 응답 timeout은 실행 여부가 불명확하므로 SI arm을 즉시 취소하지 않는다.
SI arm/종료/복구에는 각각 30/10/30초 제한이 있고 실패 상태를 노출한다. 제한 시간 이후 RSE 응답과 오래된 watchdog rearm callback은 AP 부팅/성공 판정을 되살리지 않는다. 복구 중 실패는 재시도를 제한하며 모든 FAILED가 즉시 재시도 가능한 상태는 아니다. 일반 unarmed
shutdown 동작은 그대로다. 복구 COMPLETE는 firmware handoff 완료다. Linux boot와
새 PFDI online 성공은 별도 확인해야 한다. 자동 무한 reset/retry는 하지 않는다.

Safety UART, AP 제어, RSE 응답 polling은 이벤트 처리 후 10ms one-shot을 다시
예약한다. 지연된 polling의 과거 tick을 따라잡지 않는다. 기존 periodic 방식에서
확인한 AP 종료 poll 지연과 timeout을 해소하기 위한 변경이며, 공유 timer 동작과
위 deadline은 변경하지 않았다. 5초 정기 보고와 상태 변화 즉시 보고도 유지한다.

## 검증

재현 명령:

```sh
# Yocto native QEMU는 manifest의 실행 파일과 라이브러리 경로를 함께 사용한다.
provider=build/tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json
qemu=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["tricore_executable"])' "$provider")
libs=$(python3 -c 'import json,sys; print(":".join(json.load(open(sys.argv[1]))["library_path"]))' "$provider")
LD_LIBRARY_PATH="$libs" python3 scripts/test/verify_tc397_silkit.py --qemu "$qemu" --out-dir build/qbox-apollo-qvp/vmcu-can/retest
python3 scripts/test/verify_qbox_vmcu_services.py --out-dir build/qbox-apollo-qvp/vmcu-services/retest
# 실제 AP PFDI agent 정지 → CAN 고장 보고 → 명시적 AP 복구
python3 scripts/test/verify_qbox_vmcu_services.py --inject-pfdi-timeout --out-dir build/qbox-apollo-qvp/vmcu-services/fault-retest
```

2026-10-06 Yocto 통합 검증 (증거: `build/qbox-apollo-qvp/`):

| 검증 | 결과와 증거 |
|---|---|
| SDK/registry/participant native 빌드 및 CAN wire CTest | PASS: `silkit-yocto-native.log` |
| 일반 `./yocto_build.sh --bsp` | PASS: 5,912 tasks, `silkit-yocto-bsp-final.log` |
| Provider/launcher/lifecycle/dashboard 회귀 | PASS: 104 tests, `silkit-yocto-tests.log` |
| Yocto 배포 QEMU·Zephyr·SIL Kit CAN 검증 | PASS: 9 checks, `silkit-yocto-can/result.json` |
| Apollo 전체 연동: PMIC 조회·vMCU reset·CAN AP 복구·종료/wake 1회 | PASS: `silkit-yocto-services/vmcu-services-result.json` |

SDK의 utility 심볼 분리 함수가 `SILKIT_PACKAGE_SYMBOLS=OFF`를 따르도록
레시피 패치를 적용했다. 최초 native 빌드의 already-stripped 경고 3개는
최종 빌드에서 해소됐다. 최종 BSP 경고 5개는 기존 kernel/QBox/image task의
forced-run taint이며 SIL Kit 경고는 없다. 런타임 CAN 시험은 manifest가 지정한
Yocto registry·participant·shared library를 사용했다.

2026-10-05 실행 결과:

| 검증 | 결과와 증거 |
|---|---|
| QEMU M_CAN register/FIFO/filter/IRQ/CRC/ACK/timeout/reset | [27개 PASS](../../build/qbox-apollo-qvp/vmcu-can/qemu/qtest-final/result.json), 기존 [TC397 guest](../../build/qbox-apollo-qvp/vmcu-can/qemu/minimal-regression/result.json)·[UART/GPIO 33개](../../build/qbox-apollo-qvp/vmcu-can/qemu/peripheral-regression/result.json) 회귀 PASS |
| 실제 Zephyr M_CAN ↔ SIL Kit | [9개 PASS](../../build/qbox-apollo-qvp/vmcu-services/can-shell-serialized/result.json): classic 8 byte, extended FD64/BRS, RX/TX IRQ callback, 단절 bus-off와 controller restart |
| SI native 정책 | [4개 묶음 PASS](../../build/qbox-apollo-qvp/vmcu-si0/scp-one-shot-tests/test.log): PFDI snapshot, UART/PMIC, AP control, RSE polling. 늦은 ACK·deadline·generation·queue 실패 포함 |
| UART/CAN app 정책 | [protocol/RPC, safety 9그룹, CAN policy 5그룹, AP PTY PASS](../../build/qbox-apollo-qvp/vmcu-services/host-tests.log) |
| Launcher·판정 회귀 | [pytest 87개 PASS](../../build/qbox-apollo-qvp/vmcu-services/launcher-regression.log) |
| Build | [Zephyr PASS](../../build/qbox-apollo-qvp/vmcu-services/zephyr-final-build.log), [BSP 5865 task 성공](../../build/qbox-apollo-qvp/vmcu-services/yocto-bsp-one-shot-build.log), QBox provider check 66+63 PASS |
| 전체 보드 정상 제어 | [PASS, 167.6초](../../build/qbox-apollo-qvp/vmcu-services/full-system-sixth/vmcu-services-result.json): CAN/FD 왕복, PMIC rail 9개·STAT 11개 조회, vMCU reset/cookie 재협상, AP 복구와 종료·wake 2회 |
| 실제 PFDI 고장·복구 | [PASS, 199.0초](../../build/qbox-apollo-qvp/vmcu-services/full-system-pfdi-fault/vmcu-services-result.json): AP agent SIGSTOP → SI fault mask `0x000f` → CAN 고장 보고 → 명시적 AP 복구 → 종료·wake 1회 |
| SIL Kit 없는 기본 실행 | [PASS](../../build/qbox-apollo-qvp/vmcu-services/safety-default-regression/vmcu-result.json): 조용한 shell, AP 관리 종료 후에도 SI 보고 5.00/5.02/5.02초, UART timeout·재개, GPIO/reset 중 SI 생존 |

세 번의 종료·wake는 동일 QBox/TC397 process를 유지했다. SI가 실제 AP core power
domain OFF를 확인한 후 GPIO 완료를 표시했고, AP OFF 중에도 SI ping/CAN 보고가
계속됐다. wake 후 Linux BSP marker, 새 PFDI RUN, AP UART ping을 각각 확인했다.
SIL Kit 송신 callback만으로 이 application 왕복을 PASS 처리하지 않았다.

기존 실패 실행도 보존했다. `full-system-first`는 잘못된 process 수 가정,
`second/third`는 QEMU chardev 시도 로그의 EAGAIN 중복 byte 문제,
`fourth/fifth`는 SI polling 지연으로 인한 AP 종료 timeout을 기록한다. 수신 socket에서
실제 전달된 console byte만 기록하고 one-shot polling으로 수정한 뒤 정상/고장 경로를
다시 실행했다. 고장 주입 실행의 일반 runner 결과는 의도된
`si_error:pfdi_monitor_timeout` FAIL을 유지하며 전용 검증기만 예상 고장과 복구를
PASS로 판정한다. 이전 SI PFDI 고장 검증 기록을 덮어쓰지 않는다.

이 시험은 위 기능 경로의 검증이며 전체 post-login qualification, 물리 전원 또는
차량 안전 인증 결과가 아니다.

현재 소스·repository 상태, build/conf, QEMU/Zephyr/native participant와
SI ELF·signed image·RSE flash·BSP 이미지 SHA256은
[manifest.json](../../build/qbox-apollo-qvp/vmcu-services/manifest.json)에 기록했다.

후속 범위: SoC 전체 cold-off, PMIC rail→domain/PGOOD/retention, 독립 always-on
watchdog, SPI/Ethernet 보드 링크, vendor AUTOSAR binary, CAN detailed network,
DBC/ARXML·진단/보안 인증 및 차량 안전 정책.

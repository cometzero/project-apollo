# SI CL0 PFDI–vMCU Safety Channel

기준: 2026-10-05. **기존 SI CL0 PFDI 감시 결과를 vMCU에 5초마다 보고한다.**
AP에 별도 heartbeat/workload 감시기를 추가하지 않는다. `vmcu-ap`의 이전 합성
HEALTH 생성은 제거했으며 AP UART는 ping/status와 승인된 graceful shutdown 관리 채널로 사용한다. 추가 CAN/PMIC/AP 전원 서비스는 [구현 기록](can-and-services.md)을 따른다.

## 현재 연결

| 용도 | Apollo 측 | TC397 측 | 전송 경로 |
|---|---|---|---|
| AP 관리 | DW UART2 `0x301c0000`, INTID 364 | ASCLIN0 `0xf0000600`, serial0 | 별도 localhost TCP byte stream |
| Safety Channel | SI CL0 PL011 `0x2a820000`, INTID 41 | ASCLIN2 `0xf0000800`, serial2 | 별도 localhost TCP byte stream |
| 독립 GPIO | SI CL0 PL061 `0x2a830000`, INTID 42 | PORT0 `0xf003a000` | GPIO 전용 GP8 transport + SystemC signal |
| MCU console | host tmux `tc397` pane | ASCLIN1 `0xf0000700`, serial1 | Unix socket / 입력 FIFO |

SI UART/GPIO 주소와 interrupt는 **QVP 추가 장치 배치**다. RD-Aspen/실물 Saturn-V의
물리 핀이나 TRM의 기본 장치로 주장하지 않는다. 기존 SI console `0x2a400000`,
PMIC I2C `0x2a800000`, PMIC fault GPIO `0x2a810000`과 분리한다.
`--no-vmcu`에서도 새 SI 장치는 존재하며 UART는 sink에 연결되고 reset 입력은
비활성 pull 상태다. AP UART2/3 loopback과 기존 부팅 경로는 유지한다.

실행 소유권은 기존과 같다. QBox는 Apollo/RSE/SI를 실행하고 별도 TriCore QEMU가
TC397 Zephyr를 실행한다. supervisor가 세 endpoint를 QMP로 조회하여
`QBOX_APOLLO_VMCU_UART_ENDPOINT`, `QBOX_APOLLO_VMCU_SAFETY_ENDPOINT`,
`QBOX_APOLLO_VMCU_GPIO_ENDPOINT`를 전달한다. shell 문자열과 GPIO 메시지는
Safety UART frame에 섞이지 않는다.

## 기존 PFDI 재사용과 시간

기존 AP TF-A/Linux PFDI → SCMI PFDI protocol `0x90` → SI CL0
`scmi_pfdi_monitor` → `pfdi_monitor` 경로를 유지한다. 새 `vmcu_safety` SCP
module이 read-only status API로 이 결과를 읽는다. AP 코어 개수는
`PC_CONFIGURED_CORES_COUNT`를 사용한다. 현재 실행 구성은 4코어이며 16비트
bitmap의 나머지 비트는 0이다. 존재하지 않는 코어를 fault로 만들지 않는다.

| 시간 | 의미 |
|---|---|
| 5,000 ms | SI CL0의 정기 PFDI snapshot 송신 주기; 최초 보고는 즉시 가능 |
| 15,000 ms | vMCU에서 유효한 Safety 보고 3회 누락에 해당하는 link timeout |
| 500 ms | 실제 PFDI READY일 때만 SI가 SOC_ERROR 출력을 반전하는 주기 |
| 1,500 ms | vMCU가 READY 전환 후 새 GPIO edge를 기다리는 시간 및 edge 정지 판정 |
| 기존 PFDI 10/180/60 s | OoR/boot/online 감시 설정; 이번 변경에서 단축하지 않음 |

PFDI failure status의 32비트 값을 event에 보존한다. 이전 `params[0]` 경로의
상위 비트 잘림을 수정했다. timeout/실패는 명시적인 `prepare_restart`까지 latch하여
코어가 OFF가 되거나 다음 정상 응답이 와도 이전 fault를 숨기지 않는다.

MCU 상태는 WAIT(보고 전), BOOT(PFDI 대기/첫 GPIO edge 대기), RUN,
OFF(실제 감시 코어 모두 OFF), DEGRADED로 구분한다. UART timeout, PFDI fault,
SOC_ERROR 정지를 구별한다. AP 관리 peer의 종료나 AP HEALTH frame은 이 판정의
입력이 아니다. fault에 따른 자동 reset/power-off 정책은 추가하지 않았다.

SCP는 SI timer, MCU는 STM/Zephyr uptime을 사용한다. 서로 다른 emulator의
시간을 물리 FTTI/WCET나 lock-step 시간 동기화로 해석하지 않는다.

## UART 계약

기존 28-byte LE frame/CRC32-IEEE를 사용한다. `[0:2]=a5 5a`, version=1,
type `[3]`, length `[4:6]=28`, sender `[6]`, flags `[7]`, epoch `[8:12]`,
sequence `[12:16]`, progress `[16:20]`, argument `[20:24]`, CRC `[24:28]`이다.
CRC 범위는 앞 24 bytes다.

- `SAFETY_HEALTH=7`, sender `SI0=3`. flags는 READY=1, FAULT=2, ALL_OFF=4.
- progress 하위 16비트는 active/monitored, 상위는 online mask.
- argument 하위 16비트는 latched fault, 상위는 powered-off mask.
- pending은 `monitored & ~online`이다. READY는 active가 존재하고 전부 online이며 fault가 없을 때만 설정한다.
- 비정상 mask/flag 조합, CRC 오류, 동일 epoch의 stale/중복 sequence를 버린다.
- SI epoch는 boot timer에서 얻은 비영(非零) 식별자다. 대소 비교하지 않는다.
  다른 epoch 수신 시 직전 epoch를 retired로 보관하여 지연된 직전 세션 frame을 거부한다.
  다중 재부팅을 거친 replay 방어/인증은 현재 프로토콜의 보장 범위가 아니다.
- COMMAND=5, sender MCU=2; REPLY=6, sender SI0=3. epoch, transaction, operation을 검증한다.
  ping=1, status=2(추가 fresh snapshot), report on/off=3, GPIO read=6과 [추가 op7..13](can-and-services.md)을 지원한다.
  동일 요청 재전송은 cached reply, 변조된 중복은 INVALID, 과거 transaction은 STALE이다.
- RPC 응답은 Safety deadline을 갱신하지 않는다. 명시적인 status snapshot은 실제 상태 보고다.
  READY/FAULT/ALL_OFF 변경은 5초 정기 deadline을 바꾸지 않고 즉시 추가 보고한다. `heartbeat off`는 정기/전이 보고를 함께 멈추며 PFDI와 SOC_ERROR 감시는 계속된다.

UART 처리량과 TX queue를 제한하여 느린 peer가 PFDI event loop를 막지 않도록 한다.
TC397 단독 재시작 후 SESSION_QUERY(op7, sequence0)로 SI/AP의 마지막 transaction을 조회해 다음 번호를 사용한다. 캐시를 초기화하지 않으며, 새 SI PING transaction을 차량 CAN session cookie로 사용한다. AP GPIO reset은 SI epoch를 바꾸지 않는다.

## NVIDIA Orin 사례와 GPIO 매핑

NVIDIA DRIVE OS의 공개 [MCU failover 문서](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_sw_modules/mcu_failover_handler_on_mcu.html)는
SOC_ERROR toggle 감시와 MCU–FSI SPI2 상태 통신을 설명한다. Apollo는 이 역할을
참고하되 현재 Safety 전송은 UART를 사용한다. Orin SPI wire protocol 호환 구현이 아니다.

[SoC–MCU 통신 문서](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_soc_to_microcontroller_communications.html)는
Ethernet/VLAN 기반 관리 통신, SC7 진입의 SOC_PWR_REQ, AURIX_SOC_WAKE wake,
safe-shutdown의 IST_DONE_N을 설명한다. 공개 [Orin power management](https://developer.nvidia.com/docs/drive/drive-os/6.0.9.1/public/drive-os-linux-sdk/common/topics/mcu_sw_modules/mcu_orin_power_management.html)는
종료 handshake를 기다린 뒤 전원 제어하는 흐름을 설명한다. 그 문서의 종료 timeout을
Apollo 5초 보고 주기나 물리 안전 deadline으로 전용하지 않는다.

| bit / TC397 pin | Apollo 이름 | 방향 | 기본값·구현 효과 |
|---|---|---|---|
| 0 / P00.0 | SOC_ERROR | SI → MCU | LOW; 실제 PFDI READY일 때만 toggle. vMCU edge watchdog 입력 |
| 1 / P00.1 | SOC_PWR_REQ | SI → MCU | 기본 LOW. AP 종료 arm/QUIESCING/OFF에서 HIGH |
| 2 / P00.2 | IST_DONE_N | SI → MCU | 기본 HIGH. 실제 AP core OFF 확인 뒤 LOW |
| 3 / P00.3 | SOC_RESET_N | MCU → SI 및 board reset controller | HIGH 비활성. CLI assert/release가 기존 AP cold-reset fanout에 OR 연결 |
| 4 / P00.4 | MCU_SOC_WAKE | MCU → SI | 기본 LOW. AP_OFF에서 rising edge가 SI/RSE AP 재부팅을 요청; SC7 exit는 미구현 |

같은 bit 번호를 SI PL061에 사용한다. SoC output mask는 `0x07`, MCU output mask는
`0x18`이다. MCU는 reset 출력 latch를 HIGH로 쓴 뒤 IOCR output을 활성화한다.
`SOC_RESET_N` 이름, polarity와 AP-only reset 범위는 **Apollo QVP 선택**이며 위 공개
NVIDIA 문서만으로 확인되지 않는 실물 reset net/ball 번호를 추정한 것이 아니다.

현재 SOC_ERROR의 원천은 PFDI다. 모든 SSU/PMIC fault를 합친 완전한 SoC error
출력이라고 주장하지 않는다. reset은 AP CPU/peripheral의 기존 reset 경로이며
SI CL0/CL1·RSE·PMIC·vMCU의 전원 차단이나 전체 보드 cold boot가 아니다.

GP8 frame은 `G P 1 direction LE16(level) LE16(drive-mask)` 8 bytes다. O는
MCU→QBox, I는 QBox→MCU다. UART와 독립된 socket이다. host 100 ms snapshot은
재연결을 위한 level 재전송이며 SOC_ERROR edge를 생성하지 않는다. QBox는 수신
1초 정지 시 MCU drive를 해제하고 RESET_N pull-up/WAKE pull-down으로 돌아간다.
이 transport lease는 전기적 disconnect·배선 지연 모델이나 firmware heartbeat가 아니다.

## CLI와 재현

```sh
scripts/build/build_vmcu_zephyr.sh
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp
./run_qbox_yocto.sh --bsp
```

현재 QEMU source에서 ASCLIN2/PORT0를 포함해 TC397 binary도 재빌드해야 한다.
`tc397` pane에서 실행한다.

```text
vmcu-cli status
vmcu-cli safety ping
vmcu-cli safety status
vmcu-cli safety gpio
vmcu-cli apollo ping
vmcu-cli gpio status
vmcu-cli gpio wake on
vmcu-cli gpio wake off
vmcu-cli heartbeat off
vmcu-cli heartbeat on
vmcu-cli gpio reset assert
vmcu-cli gpio reset release
```

`status`는 local PFDI mask/sequence/report age/GPIO edge count를 출력한다.
평상시 로그는 상태가 변할 때만 나온다. `workload`는 UNSUPPORTED다.
reset 명령은 실행 중인 AP를 실제로 reset하므로 필요할 때만 실행한다.

PMIC는 기존 SI CL0가 단독으로 소유한다. TPS6594 `0x48`의 기본 read-only probe와
rail 설정 보존 정책을 유지한다. vMCU PMIC 조회 proxy와 AP-only 종료·wake를 추가했다. rail gating, SC7 및 SoC 전체 cold-off sequencer는 별도 구현 대상이다. 이 문서의 기존 GPIO 검증은 물리 전원 시퀀스 검증이 아니다.

## 구현 소유권·검증

- SCP: `apollo-qvp/module/{pfdi_monitor,vmcu_safety}`와 `si0_ramfw/config_*`.
- QBox overlay: `vp/extensions/si-cl0-vmcu.lua`, `vmcu_gpio_bridge`, `zena_reset_ctrl`.
- QEMU: `hw/tricore/`의 ASCLIN2와 PORT0 및 GP8 chardev.
- root: `zephyr_vmcu_src/{src/main.c,lib/safety.c}`, supervisor, full-system 검증기.

생성 증거는 `build/qbox-apollo-qvp/vmcu-si0-safety/`에 보관한다. 개별 model 증거는
`vmcu-safety/qemu-port/`, `vmcu-safety/qbox/`, SCP/AP native 증거는 `vmcu-si0/`다.
기존 AP 합성 workload 검증은 과거 결과로 남기고 현재 SI0 safety 통과 근거로 사용하지 않는다.

| 검사 | 결과 | 증거 (`build/qbox-apollo-qvp/` 아래) |
|---|---|---|
| 현재 QEMU build + 기존 guest cold/reset | PASS, 21 + 21 | `vmcu-safety/qemu-port/minimal-regression/result.json` |
| 3 UART RX/TX/SRC, GPIO MMIO/fragment/reconnect/backpressure | PASS, 33 | `vmcu-safety/qemu-port/peripherals-backpressure/result.json` |
| QBox GPIO/reset/Lua 집중 시험 | PASS, 3 | `vmcu-safety/qbox/final-ctest.log` |
| SCP snapshot/32-bit fault/4·16코어/OFF→ON freshness/5초 frame/RPC | PASS, 2 suite | `vmcu-si0/scp-tests/test.log` |
| Zephyr app build | PASS | `vmcu-si0-safety/zephyr-build-final.log` |
| MCU safety policy / AP management PTY | PASS, ASan/UBSan 포함 | `vmcu-safety/native/`, `vmcu-si0/ap-management-sanitized.log`, `vmcu-si0-safety/native-test.log` |
| 최종 Yocto BSP 및 서명 SI0/RSE image | PASS, 5,865 tasks, 5,804 reusable | `vmcu-si0-safety/yocto-build-final.log` |
| QBox provider 필수 CTest | PASS, 66 + 63 | `vmcu-si0-safety/qbox-provider-check.log` |
| 런처/UKI/검증기 pytest | PASS, 85 | `vmcu-si0-safety/focused-pytest-final.log` |
| 정상 full Saturn-V / 실제 tmux shell | PASS, 21 checks, 98.6 s | [normal-system/vmcu-result.json](../../build/qbox-apollo-qvp/vmcu-si0-safety/normal-system/vmcu-result.json) |
| 실제 AP PFDI agent STOP/CONT 고장 주입 | PASS, 22 checks, 178.7 s | [fault-injection/vmcu-result.json](../../build/qbox-apollo-qvp/vmcu-si0-safety/fault-injection/vmcu-result.json) |
| headless `--no-vmcu` boot 및 PMIC preserve | PASS, peer/companion 없음 | [default-off/vmcu-off-result.json](../../build/qbox-apollo-qvp/vmcu-si0-safety/default-off/vmcu-off-result.json) |

정상 실행에서 `monitored=online=0x000f`, `pfdi_fault=0`을 확인했다. AP 관리
service를 종료한 뒤에도 SI report sequence와 SOC_ERROR edge count가 증가했고,
MCU에서 측정한 report 간격은 5,000~5,020 ms였다. 보고 off는 LINK_TIMEOUT,
on은 RUN 복귀로 이어졌다. wake를 변경한 뒤 SI GPIO read RPC에서 해당 bit를 확인했다.

고장 주입은 기존 `pfdi-sample-app`에 SIGSTOP을 보내 수행했다. SI 로그의 AP
코어 0~3 timeout과 MCU `pfdi_fault=0x000f`를 함께 관측했다. SIGCONT 후에도
fault가 latch되어 있었다. reset assert/release에서 SI가 읽은 GPIO는 각각
`0x04`/`0x0c`였고 SI UART RPC는 계속 응답했다. AP reset fanout 자체의 OR 동작은
model unit test로 확인했다. 이 초기 시험에서는 AP 재부팅·재로그인 recovery를
검증하지 않았다. 이후 SI의 RSE reload 기반 AP 복구·종료·wake 검증은
[CAN과 제어 서비스](can-and-services.md)에 별도 기록한다.
모든 시험의 소유 process cleanup은 잔여 PID·강제 종료 없이 PASS였다.

고장 주입 실행의 일반 runner `result.json`은 의도대로
`passed=false`, `blocker=si_error:pfdi_monitor_timeout`을 유지한다. 전용 검증기는
명시적 주입, 실제 MCU fault 검출, 정상 boot marker, 다른 오류 부재가 모두
확인될 때만 해당 시나리오를 PASS로 분류한다. 다른 오류를 허용하지 않는 9개
검증기 시험도 포함했다. 최초 `full-system/`은 일반 boot PASS를 요구하여 FAIL한
기록이며 덮어쓰지 않았다. 정상 실행의 일반 runner는 `passed=true`다.
이 launcher 기반 시험은 전체 post-login qualification을 대신하지 않는다.

```sh
# 출력 디렉터리는 실행마다 새 경로를 사용한다.
python3 scripts/test/verify_qbox_zephyr_vmcu.py --out-dir build/qbox-apollo-qvp/my-vmcu-normal
python3 scripts/test/verify_qbox_zephyr_vmcu.py --inject-pfdi-timeout --out-dir build/qbox-apollo-qvp/my-vmcu-fault
```

소스·nested repository 상태와 QEMU/ELF/서명 SI0/RSE flash/BSP 이미지 hash는
[manifest.json](../../build/qbox-apollo-qvp/vmcu-si0-safety/manifest.json)에 기록한다.

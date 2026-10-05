# Apollo–TC397 UART heartbeat 구현과 검증

> 이전 AP heartbeat 단계의 기록이다. 현재 AP 관리·SI CL0 PFDI Safety 채널은
> [SI CL0 Safety Channel](si0-safety-channel.md)을 따른다.
> 초기 `vmcu-firmware/` 소스는 2026-10-05 제거했다. 현재 빌드·실행은
> [Zephyr 구현 문서](zephyr-implementation.md)를 따른다. 아래 시험 결과는 당시 기록이다.

기준: 2026-10-04. [TC397 최소 모델](tc397-minimal-implementation.md)의 다음 단계인 **P0 통신 계약과 P1의 AP UART 연결**을 구현한다. TC397은 독립 QEMU process이며, heartbeat 판정은 MCU firmware에서 실행한다. SI 감독 채널·GPIO·CAN·PMIC·AP 하드웨어 reset은 이 단계에 포함하지 않는다.

## 1. 실제 연결과 소유권

| 영역 | 구현 |
|---|---|
| Apollo guest | Linux DW UART2, `0x301c0000`, SPI 332 / INTID 364. `/sys/class/tty/ttyS*/device`의 주소로 실제 tty를 찾는다. |
| QBox | 기존 `char_backend_socket`, TCP client `127.0.0.1:PORT`. UART2의 `backend_socket`과 연결한다. |
| TC397 | standalone `KIT_AURIX_TC397B_TRB`, ASCLIN0 TCP server, 실제 TriCore firmware의 UART RX/STM ISR |
| 당시 MCU firmware/AP helper | root 소유 `vmcu-firmware/` bare-metal component(제거됨). 현재 구현은 [Zephyr vMCU](../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/README.md)에 있다. |
| QBox 설정 | `qbox-platform/platforms/apollo/vp/options/vmcu.lua`, `vp/backends/vmcu.lua`; `QBOX_APOLLO_VMCU_UART_ENDPOINT=127.0.0.1:PORT`로 opt-in |

Lua의 기본값은 off다. root `--bsp` tmux launcher는 아래 5절처럼 자동 활성화한다. PL011 부팅 console과 DW UART0↔1/DMA 연결은 유지한다. opt-in 때만 기존 UART2↔3 loopback을 해제하고 UART3을 입력 없는 `/dev/null` 출력 backend에 연결한다. `read_file=/dev/null`은 EOF byte를 주입할 수 있으므로 사용하지 않는다. 잘못된 endpoint, AP CPU 비활성, UART backend 중복 연결은 configuration error다. 주소·IRQ·Linux DT 변경은 없다.

`char_backend_socket`을 native provider의 필수 module에 추가했다. 기존 backend는 연결 전 TX를 버리며 host thread에서 약 100 ms 간격으로 RX를 전달한다. TCP 입력 queue의 대량 traffic/상한과 재연결은 이번 qualification 대상이 아니다. AP UART reset이 TCP ingress를 자동 폐기하지 않으므로 protocol의 epoch 검사가 필요하다.

## 2. 고정 wire 계약

모든 frame은 28 byte, 정수는 little endian이다. C 구조체를 직접 전송하지 않는다. shared C codec과 별도의 Python `struct`/CRC 구현으로 송수신을 검사한다.

| byte | 필드 |
|---|---|
| 0–1 | magic `a5 5a` |
| 2–3 | version `1`, type: HELLO=1 / HELLO_ACK=2 / HEALTH=3 / STATUS=4 |
| 4–7 | length `28`(16-bit), sender AP=1 / MCU=2, flags |
| 8–11 | AP session epoch, 0 제외. 협상 전 MCU STATUS만 0 |
| 12–15 | sequence |
| 16–19 | workload progress |
| 20–23 | argument: MCU STATUS에서는 monotonic uptime(ms) |
| 24–27 | CRC32/IEEE reflected, 앞 24 byte 대상, 초기값/xorout `ffffffff` |

수신기는 고정 크기 buffer로 magic·length·version·CRC를 검사하고 손상된 stream에서 다시 frame을 찾는다. packet 분할·연속 전달을 지원한다. CRC는 인증 수단이 아니다. 현재 protocol은 전원 변경·reset 명령을 제공하지 않는다.

epoch와 sequence는 32-bit serial arithmetic으로 비교하며 앞으로의 차이가 `1..0x7fffffff`인 값만 새 값이다. 최초 HELLO 또는 더 새로운 epoch의 HELLO가 세션을 만든다. 같은 epoch의 HELLO 재전송에는 ACK만 보내며 health deadline을 갱신하지 않는다. 이전 epoch의 HELLO/HEALTH 및 중복·역순 sequence는 정상 진행으로 세지 않는다. AP helper는 `--epoch`를 명시적으로 받는 시험용 endpoint다. 실제 제품의 지속 boot counter·신뢰·인증 정책은 별도다.

## 3. MCU 정책과 검증 범위

초기 WAIT, 세션 협상 후 SYNC, 연속 정상 progress 3회 후 RUN, timeout 후 DEGRADED다. 복구에도 연속 정상 progress 3회가 필요하다. STATUS flags 하위 nibble은 상태(WAIT=0/SYNC=1/RUN=2/DEGRADED=3), 상위 nibble은 fault(NONE=0/LINK_TIMEOUT=1/WORKLOAD_STALLED=2)다.

fixture의 STATUS/HEALTH 주기는 100 ms, timeout은 1000 ms다. MCU의 STM 기반 시간이 판정 기준이다. 새 sequence지만 progress가 같은 HEALTH는 링크 수신 시간만 갱신한다. 따라서 정상 통신 위의 workload 정지와 전체 링크 단절을 구별할 수 있다. CRC 오류·중복·이전 epoch는 두 deadline 모두 갱신하지 않는다.

이는 서로 다른 simulator의 비동기 기능 시험이다. host timeout은 시험을 종료하는 상한이며 차량 FTTI 검증값이 아니다. AP helper의 progress는 시험 입력이며 AD application의 실제 진행을 연결한 결과가 아니다. DEGRADED는 보고 상태로만 구현하며 차량 출력·전원·reset을 구동하지 않는다.

## 4. 이전 시험 재현 범위

초기 bare-metal 소스는 현재 빌드·launcher·Yocto recipe에서 사용하지 않아 제거했다.
기존 `build/qbox-apollo-qvp/vmcu-link/`의 산출물과 시험 증거는 보존한다.
과거 AP heartbeat 전용 시험기와 해당 단위 테스트도 현재 Zephyr firmware와
호환되지 않아 함께 제거했다. 아래 결과는 보존된 당시 증거이며 현재 재현 절차가 아니다.
현재 firmware 빌드와 검증은 [Zephyr 구현 문서](zephyr-implementation.md) 및
`scripts/test/verify_qbox_zephyr_vmcu.py`를 사용한다.

## 5. BSP tmux에서 함께 실행

현재 기본 firmware는 [Zephyr vMCU app](zephyr-implementation.md)이다.
`./run_qbox_yocto.sh --bsp`는 ASCLIN1의 실제 Zephyr shell을 `tc397` pane에
연결하고 BSP의 AP peer를 자동 시작한다. firmware 기본 경로는
`build/qbox-apollo-qvp/zephyr-vmcu/app/zephyr/zephyr.elf`다.
`vmcu-cli status`, `vmcu-cli heartbeat off/on`, `vmcu-cli workload stall/run`을
해당 pane에서 입력한다. 정상 상태에서 주기 STATUS를 출력하지 않는다.

`--no-vmcu`, `--no-attach`, `--multi-session`, F12 종료와 실행별 TCP port는
유지한다. `QBOX_TC397_QEMU`, `QBOX_TC397_FIRMWARE`로 호환 artifact를 선택한다.
headless/product는 companion을 자동 시작하지 않는다. 외부
`QBOX_APOLLO_VMCU_UART_ENDPOINT` 지정 시 launcher의 추가 MCU/pane을 생략한다.

| 실행 디렉터리의 파일 | 현재 내용 |
|---|---|
| `tc397-uart.log` | 실제 ASCLIN1 Zephyr shell 출력 |
| `tc397-uart-input.fifo` | shell 입력 byte 경로 |
| `tc397-link-tx.bin` | ASCLIN0 binary TX; AP→MCU RX는 제외 |
| `tc397-supervisor.log` | host process 시작/종료 기록 |
| `tc397-qemu.log` | QEMU stdout/stderr |
| `tc397-status.json` | 명령, endpoint, PID, console byte counts, cleanup |

아래 검증 표는 이전 bare-metal firmware와 host decoder를 사용한 당시의 기록이다.
해당 raw log/manifest는 보존하며 최신 Zephyr 동작의 근거와 구분한다.
이전의 AP tty 개방 전 STATUS backlog는 Zephyr app에서 HELLO 이전/주기 STATUS
송신을 제거하여 방지한다.

## 6. 증거와 다음 단계

다음은 당시 bare-metal source에서 실제 실행한 결과다. artifact root는 `build/qbox-apollo-qvp/vmcu-link/`다.

| 단계 | 결과 | 증거 |
|---|---|---|
| 기존 TC397 최소 모델 재검증 | **PASS: cold 21 + reset 21 + ISA/CSA 21** | `../tc397-minimal/revalidation-20261004T110237Z/result.json` |
| MCU/AP helper 빌드 | **PASS** | TriCore GCC 9.4.0, static AArch64 GCC; `firmware/`, 증분 확인 `firmware-build.log` |
| Host codec/policy | **PASS** | `firmware-build.log`: CRC 기준값, parser 경계, deadline·epoch/sequence/ms wrap |
| Python decoder/runner 검사 | **PASS: 10 + 2** | `decoder-check/pytest.log`, `qbox-runner-tests.log` |
| 실제 TC397 protocol | **PASS: 17** | [standalone-final/result.json](../../build/qbox-apollo-qvp/vmcu-link/standalone-final/result.json), `frames.jsonl`, raw UART·QMP logs |
| QBox native compile/install | **PASS** | `qbox-native-provider.log`; 새 `char_backend_socket.so` sysroot 배치 |
| Recipe `do_check` | **PASS: platform 65 + core 63** | `qbox-{platform,core}-unit-tests.log` |
| Full Saturn-V BSP + TC397 | **PASS: 11** | [qbox-first/result.json](../../build/qbox-apollo-qvp/vmcu-link/qbox-first/result.json), primary console·`mcu-status.jsonl` |
| vMCU off 기본 Saturn-V BSP 부팅 | **PASS** | [default-off/result.json](../../build/qbox-apollo-qvp/vmcu-link/default-off/result.json), `default-off-launcher.log` |

Full-system 시험에서는 실제 UART2 IRQ(INTID 364)가 **10→181**로 증가했다. 첫 세션(epoch 101)에서 RUN→WORKLOAD_STALLED→RUN→LINK_TIMEOUT→RUN을 확인했다. AP helper 재시작 뒤 epoch 102로 재협상했고 MCU의 uptime은 **62,910→64,221 ms**, TX sequence는 **625→639**로 계속 증가했다. 이전 epoch의 HEALTH만 보내면 timeout이 발생했으며 정상 입력으로 다시 복구했다. 전체 runner는 약 68초에 종료했고, 자신이 시작한 Apollo/TC397 process의 잔여 PID가 없음을 확인했다.

같은 full-system 로그에서 SI CL0의 TPS6594 `policy=preserve`, `probe=PASS`, `rail_config=SKIP`, `gpio_test=SKIP`와 SI CL1 RPMsg attach를 확인했다. 이는 기존 부팅과 read-only PMIC 경로의 유지 근거이며 **vMCU의 PMIC 제어 시험은 아니다**. 표준 full-system runner의 `passed=true`는 post-login 전체 qualification을 끈 이 시험의 boot gate 기준이다.

### BSP tmux launcher 후속 검증

자동 실행·pane·종료 처리는 `build/qbox-apollo-qvp/tc397-tmux/`에 별도로 기록한다.

| 항목 | 결과 | 증거 |
|---|---|---|
| 실행기·companion 회귀 | **PASS: 73** | `tests-final.log`; 기존 headless/debug 경로, 인자 전달, 4/5개 로그 영역 resize, 실패·signal·자식 정리 |
| 기본 배치 provider의 BSP + TC397 부팅 | **PASS** | `runtime-cleanup/result.json`; 별도 `--conf` 없이 실제 root launcher 실행 |
| 같은 tmux 화면의 UART 로그 | **PASS** | `runtime-final/panes.txt`, `tc397-pane-final.txt`; 기존 7개 + TC397 1개 pane |
| AP helper 실제 UART 통신 | **PASS** | `runtime-final/traffic-result.json`; epoch 601/602, RUN·timeout, UART2 IRQ **64→203** |
| 실행 중 실제 F12 입력 | **PASS** | `runtime-cleanup/f12-result.json`, `tmux-attach.raw`; PTY의 tmux client에 F12 입력 |
| 종료 시 부팅 결과·process 정리 | **PASS** | companion `INTERRUPTED`는 요청한 종료; 두 cleanup 모두 PASS, forced signal·잔여 PID 없음, tmux session 제거 |
| runner 정상 종료 후 MCU 정리 | **PASS** | `runtime/tc397-status.json`: EXITED, 두 cleanup PASS |

초기 시험의 AP helper 10초 제한 실패는 `runtime/traffic-first-result.json`에
보존했다. F12가 모든 자식에 동시에 신호를 보낼 때 결과 기록이 중단된 문제는
companion부터 정상 종료를 요청한 뒤 필요할 때만 tree signal로 전환하도록
수정했다. 해당 초기 결과는 `runtime-final/result.json`의 FAIL로 남기며,
수정 후 F12 통과 근거는 `runtime-cleanup/`이다. shell syntax·공백 검사는
통과했고 ShellCheck에는 기존 HEAD에도 있던 debug 변수 SC2034 경고 2개가 남는다.

실행한 firmware SHA256은 `f1fdf12cf309ae1468265d61835308d58a78eb11748195c9e5ecaa50ee1cd7dc`, AP helper는 `10943a09bd0450e3ed618a5a08158e063775bb2e4ba8330c33b8a07dd59defb9`다. QEMU·QBox·socket module·qboxconf hash와 실제 명령은 각 result와 [manifest.json](../../build/qbox-apollo-qvp/vmcu-link/manifest.json)에 보존한다. source는 미커밋 working tree 기준이므로 HEAD와 변경 파일 hash를 함께 확인해야 한다.

AP helper 재시작은 **AP 하드웨어 reset이 아니다**. P0의 UART 계약과 P1의 AP UART 연결은 완료했으며, P0/P1 전체 완료를 뜻하지 않는다. 남은 단계는 SI health 별도 경로, GPIO fault/reset arbiter와 실제 AP reset 시험, RTOS, CAN/SIL Kit, PMIC proxy/전원 sequencer, 시간 동기화다. 차량 안전 정책과 실물 보드 배선이 필요한 항목은 기존 문서의 `UNVERIFIED` 경계를 유지한다.

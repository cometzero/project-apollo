# TC397 Zephyr vMCU application — 도입 당시 검증 기록

> 현재 구성은 [SI CL0 Safety Channel](si0-safety-channel.md)을 따른다.
> 아래 AP heartbeat/workload와 두 UART 구성 및 수치는 이전 단계의 기록이다.
> 현재 AP는 ping/status만 제공하며 ASCLIN2의 SI CL0 PFDI 보고와 PORT0 GPIO를 사용한다.

기준: 2026-10-04. [이전 bare-metal UART 구성](uart-heartbeat-implementation.md)을
실제 Zephyr application과 shell로 전환한다. 제어 범위는 상태 조회와
heartbeat/workload 제어다. AP hardware reset·CAN·PMIC는 별도 단계다.

## 1. 소유권과 실행 구성

| 영역 | 현재 구성 |
|---|---|
| vMCU overlay/application | [zephyr_vmcu_src](https://github.com/cometzero/zephyr_vmcu_src), 동일 workspace 경로의 독립 Git submodule |
| Zephyr kernel | build 아래 독립 checkout; `west.yml`의 SHA 고정 |
| 기존 Safety Island | 기존 Zephyr 4.1과 `zephyr_hsoc_src` 유지 |
| MCU machine | 현재 `hsoc-stack/tools/qemu`의 `KIT_AURIX_TC397B_TRB`, CPU0 |
| AP peer | BSP의 `vmcu-ap` service, sysfs 주소로 DW UART2 탐색 |
| tmux launcher | `run_qbox_yocto.sh --bsp`, TC397 ELF 자동 시작 |

기존 SI Zephyr 4.1에는 TriCore architecture가 없다. vMCU는 native TriCore 지원이
있는 upstream revision `894020886d647a5f9b8a58bdf2cb8c211a62716b`를 별도로
사용한다. 해당 board는 `qemu_tc3x`이며 STM timer와 polling ASCLIN driver를
그대로 사용한다. [공식 board 문서](https://docs.zephyrproject.org/latest/boards/qemu/tricore/doc/index.html)

기존 TriCore GCC 9.4의 binutils 2.20은 linker script의 `ALIGN_WITH_INPUT`을
처리하지 못했다. vMCU 빌드는 GCC 11.3.1을 포함한 별도 archive를 고정한다.
배포 tag `v11.3.0`과 compiler가 보고하는 버전은 구분한다. archive SHA256은
`4d2a82c0bd2a65657e9f5212c75c6d9e5fab325d24baf632ff19b5214a332858`이다.
[toolchain 배포](https://github.com/linumiz/aurix-gcc-toolchain/releases/tag/v11.3.0)

## 2. Console과 제어 UART 분리

| 경로 | 매핑과 동작 |
|---|---|
| AP 제어 | ASCLIN0 `0xf0000600` / QEMU serial0 ↔ TCP ↔ Apollo UART2 `0x301c0000` |
| Zephyr shell | ASCLIN1 `0xf0000700` / QEMU serial1 ↔ local Unix socket ↔ tmux console FIFO |
| ASCLIN1 IRQ | SRC TX/RX/ERR indices `0x17/0x18/0x19`; Zephyr native driver는 polling 사용 |
| 시간 | STM0 50 MHz → 실제 Zephyr kernel tick/uptime/scheduling |

ASCLIN1 주소와 SRC 배치는 [Infineon iLLD register 정의](https://raw.githubusercontent.com/Infineon/illd_release_tc3x/ac8fb805633894b89819b953516b4e94387056fd/src/BaseSw/Infra/Sfr/TC39xB/IfxSrc_reg.h)를
따른다. STM의 TIM0SV/CAPSV는 같은 counter snapshot에서 읽도록 정리했다.
새 UART의 RX/TX FIFO와 interrupt source는 ASCLIN0과 별개다. pin mux·baud timing·
전기적 동작이나 실물 보드 배선의 일치를 뜻하지 않는다.

호스트가 binary STATUS를 텍스트로 반복 변환하던 경로를 제거했다.
`tc397-uart.log`는 Zephyr가 ASCLIN1으로 출력한 실제 콘솔이다. 입력은
`tc397-uart-input.fifo`에서 console socket으로 전달하며 host 입력 buffer는
4096 bytes로 제한한다. MCU 상태 판정은 Zephyr app에서 수행한다.

## 3. App과 UART 계약

Zephyr link thread가 ASCLIN0 RX, codec, session freshness, deadline과 RPC TX를
담당한다. shell thread는 bounded message queue와 semaphore로 요청·응답을
전달한다. console과 link의 UART가 다르므로 shell 문자열이 protocol에 섞이지
않는다. 기본 콘솔 출력은 초기 상태 및 상태 변화뿐이다.

기존 28-byte little-endian frame과 CRC32/IEEE를 유지한다. HELLO/ACK/HEALTH/STATUS
외에 COMMAND=5, REPLY=6을 추가한다. COMMAND/REPLY의 `sequence`는 transaction,
`progress`는 operation, `argument`는 값 또는 AP 상태 bits다. epoch가 일치해야
하며, reply는 outstanding transaction과 operation이 모두 맞아야 완료된다.
RPC 자체는 heartbeat deadline을 갱신하지 않는다.

| 명령 | 효과 |
|---|---|
| `vmcu-cli status` | MCU의 local state/fault/epoch/sequence/progress/uptime |
| `vmcu-cli apollo ping`, `apollo status` | 실제 AP UART service 응답 확인 |
| `vmcu-cli heartbeat off/on` | AP peer의 HEALTH 송신 중지/재개; link timeout·복구 검증 |
| `vmcu-cli workload stall/run` | HEALTH는 유지하고 시험 progress만 정지/재개 |
| `vmcu-cli monitor off/on` | 상태 변화 알림 출력만 제어; 감시는 계속 실행 |

heartbeat period 100 ms, deadline 1000 ms, 정상 진행 3회 후 RUN이라는 기능 시험
정책을 유지한다. session 협상 전에는 STATUS를 주기 전송하지 않으며, 협상 후에도
정기 STATUS 대신 상태 변화와 명령 응답만 전송한다. 이전 구현에서 AP tty가
열리기 전 STATUS가 쌓이던 원인을 제거한다.

AP service의 progress는 실제 AD workload가 아닌 시험용 counter다. FTTI,
physical timing, SIL Kit 시간 동기화 또는 안전 등급 검증으로 사용하지 않는다.

## 4. 빌드·실행·검증

```sh
scripts/build/build_vmcu_zephyr.sh --bootstrap
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp
```

QEMU의 ASCLIN1 추가가 반영된 binary가 필요하다. 기존 native build는
[최소 모델 문서](tc397-minimal-implementation.md)의 configure 경로를 사용한다.
firmware는 `build/qbox-apollo-qvp/zephyr-vmcu/app/zephyr/zephyr.elf`이며
`QBOX_TC397_FIRMWARE`로 경로를 바꿀 수 있다. launcher는 빌드를 자동 실행하지
않는다. AP service는 BSP init에서 background로 시작하며 `/run/vmcu-ap.log`,
`/run/vmcu-ap.pid`를 사용한다. init의 STARTED는 peer handshake 통과와 구분한다.

AP peer 자동 시작은 guest command line의 정확한 `apollo.vmcu=1` token으로
제한한다. runtime은 MCU endpoint가 있고 BSP 이미지인 경우에만 실행용 WIC
사본을 만들고, A/B UKI의 `.cmdline` padding에 이 인자를 추가한다. kernel,
initrd, DTB section과 배포 원본은 유지하며 각 hash와 FAT readback 결과를 기록한다.
서명된 UKI나 padding이 부족한 입력은 명시적으로 실패한다. `--no-vmcu`와
기본 headless 실행에서는 이 인자를 추가하지 않아 AP peer가 UART2를 점유하지 않는다.

```sh
python3 scripts/test/verify_qbox_zephyr_vmcu.py \
  --out-dir build/qbox-apollo-qvp/vmcu-zephyr/full-system
```

검증기는 실제 tmux `tc397` pane에 명령을 입력한다. Zephyr boot, BSP peer 자동
기동, RPC 응답, heartbeat/workload fault와 recovery, 조용한 정상 console,
monitor 출력 설정 및 session cleanup을 검사한다. 세션과 복사 disk는 실행별로
분리한다. 상세 실행 결과는 아래에 기록한다.

## 5. 실행 결과

현재 working tree에서 아래를 실행했다. 전체 증거는
[manifest.json](../../build/qbox-apollo-qvp/vmcu-zephyr/manifest.json)에 연결한다.

| 검사 | 결과 | 증거 |
|---|---|---|
| 현재 QEMU build 및 최소 guest 회귀 | PASS: cold 21 + QMP reset 21 | `vmcu-zephyr/qemu-port/minimal-regression/result.json` |
| 두 ASCLIN의 실제 RX/TX·SRC·FIFO 분리 | PASS: 3 | `vmcu-zephyr/qemu-port/dual-uart-result.json` |
| Zephyr kernel/shell/timer bringup | PASS: 5, uptime 20→330 ms | `zephyr-vmcu/bringup-result.json` |
| 최종 Zephyr app build | PASS, ROM 67,760 B / RAM 41,952 B | `vmcu-zephyr/app-build-final.log` |
| codec/policy/RPC + native PTY peer | PASS, ASan/UBSan 포함 | `zephyr-vmcu/host{,-sanitized}-test.log` |
| 실제 TC397 + native AP peer | PASS: 8 | `vmcu-zephyr/standalone-rpc-final/result.json` |
| Yocto BSP image | PASS: 5,865 tasks, 최종 5,825 reusable | `vmcu-zephyr/yocto-bsp-final.log` |
| QBox provider 필수 CTest | PASS: 65 + 63 | Yocto `qbox-apollo-qvp-native/1.0/temp/log.do_check` |
| launcher·UKI·runtime·protocol 관련 pytest | PASS: 115 | `vmcu-zephyr/focused-pytest-final.log` |
| Full Saturn-V + 실제 tmux shell 명령 | PASS: 16, 약 85.5 s | [vmcu-result.json](../../build/qbox-apollo-qvp/vmcu-zephyr/full-system/vmcu-result.json) |
| headless `--no-vmcu` BSP 부팅 | PASS, peer 시작 없음 | [vmcu-off-result.json](../../build/qbox-apollo-qvp/vmcu-zephyr/default-off/vmcu-off-result.json) |

표의 짧은 경로는 `build/qbox-apollo-qvp/` 아래다. 실제 tmux 화면은
[tc397-pane.txt](../../build/qbox-apollo-qvp/vmcu-zephyr/full-system/tc397-pane.txt),
원본 MCU 콘솔은 같은 디렉터리의 `tc397-uart.log`에 보존한다.
Full-system 시험은 `vmcu-cli`를 실제 pane에 입력하여 AP UART RPC와
RUN→LINK_TIMEOUT→RUN, RUN→WORKLOAD_STALLED→RUN을 확인했다.
`monitor off`에서도 local status는 WORKLOAD_STALLED를 보고하며 출력만 억제한다.
정상 상태의 2초 구간에는 추가 console byte가 없었다. 종료 후 Apollo/TC397
소유 process의 잔여 PID와 강제 종료가 없고 두 cleanup receipt 모두 PASS다.

최종 firmware SHA256은
`0342f5f3b4e154cc483c42d5b54e10da94fd0d1e6aaea50a69bd91e3e3dacc45`다.
BSP kernel command line에서 `apollo.vmcu=1`, init에서 service STARTED를 확인하고
실제 RPC로 준비 상태를 검증했다. 꺼진 실행은 boot argument·peer·companion이
모두 없었다. 전체 post-login qualification은 이 시험에서 실행하지 않았다.

초기 standalone quiet 시험은 UART 줄 출력이 끝나기 전에 비교해 FAIL이었다.
검증기를 newline까지 기다리도록 수정한 최종 결과가 위 PASS이며 초기 기록도
보존한다. launcher crash 시험도 socket EOF가 waitpid보다 먼저 관찰되는 경우를
허용하도록 수정했으며 process 정리·무관한 process 생존 검사는 유지했다.

추가 BSP workflow 검사에서는 25 PASS / 1 FAIL이었다. FAIL은 기존
`test_qvp_pfdi_agent_enables_tx_completion_irq`가 `SRC_URI` 전체 문자열을
고정한 것과 현재 HEAD의 추가 patch 항목이 일치하지 않는 문제다. 해당 BSP
source는 이 작업에서 변경하지 않았고 실패를 숨기거나 테스트를 완화하지 않았다.
`vmcu-zephyr/runtime-bsp-regression-final.log`에 보존한다. 해당 검사를 실행하려면
기존 runtime import 규칙에 따라 `PYTHONPATH=scripts/run`을 설정한다.

## 6. 현재 한계

TC397만 QMP reset하고 AP service를 유지하는 독립 reset 시나리오는 지원하지
않는다. MCU transaction counter가 초기화되면 peer의 중복 방지 상태와 맞지 않아
RPC가 STALE로 거절될 수 있다. 현재 launcher는 QBox와 TC397을 함께 시작·종료한다.
MCU 단독 재기동을 추가하려면 양방향 boot identity/session 재협상을 먼저 구현한다.
이전 bare-metal의 QMP reset 자체 통과와 이 프로토콜 제약은 별개다.

# TC397 Zephyr vMCU application — 도입 당시 검증 기록

> 현재 구성은 [SI CL0 Safety Channel](si0-safety-channel.md)을 따른다.
> 아래 AP heartbeat/workload와 두 UART 구성 및 수치는 이전 단계의 기록이다.
> 현재 AP는 ping/status만 제공하며 ASCLIN2의 SI CL0 PFDI 보고와 PORT0 GPIO를 사용한다.

## 현재 빌드 경로 (Yocto 통합)

```sh
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp
# firmware만 갱신할 때
./yocto_build.sh --keep-conf zephyr-vmcu
```

`meta-hsoc-auto-solutions`의 `zephyr-vmcu` 레시피는 기존
`hsoc-stack/components/system_mgmt/zephyrproject/zephyr`의 Zephyr 4.1.0과
`zephyr_vmcu_src` overlay를 사용한다. `zephyr_hsoc_src`와 같은 module 방식으로
architecture/board/SoC/DTS roots를 등록한다. 별도의 upstream Zephyr checkout,
로컬 Python venv 또는 수동 QEMU 빌드는 필요하지 않다.

공유 Zephyr 4.1.0에는 TriCore 지원이 없으므로 overlay에 upstream revision
`894020886d647a5f9b8a58bdf2cb8c211a62716b`의 architecture, board, SoC 및
UART/interrupt/STM 지원을 backport했다. STM tick accounting과 CAN API는
4.1 계약에 맞췄다. Architecture dispatch·compiler/linker·shell ABI 연결은
`compat/zephyr-4.1.patch`로 처리하며, 레시피가 만든 `${WORKDIR}/zephyr` 복사본에만
적용한다. 공유 Zephyr checkout과 Safety Island의 빌드 원본은 수정하지 않는다.
원본·라이선스와 변경 범위는
[overlay 호환성 기록](../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/compat/README.md)에 명시한다.

`tricore-toolchain-native`는 GCC 11.3.1이 포함된 `v11.3.0` 배포의
`aurixgcc_03-2026_Linux_x86-x64.zip`을 고정 SHA256으로 가져와 native sysroot에
설치한다. Compiler 자체를 소스에서 재빌드하는 구성은 아니다. SHA256은
`4d2a82c0bd2a65657e9f5212c75c6d9e5fab325d24baf632ff19b5214a332858`이다.
`qemu-apollo-native`는 기존 `hsoc-stack/tools/qemu`에서 AArch64와 TriCore를 빌드한다.
`nexios-bsp-initramfs`의 `apollo-qvp` 의존성으로 firmware와 QEMU가 함께 배포된다.

배포 ELF는 `build/tmp_baremetal/deploy/images/apollo-qvp/zephyr-vmcu-tc397.elf`,
QEMU는 `build/tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json`의
`tricore_executable`로 선택한다. `--deploy-dir`은 firmware와 인접 provider manifest
탐색에 함께 적용하며, `QBOX_TC397_QEMU`/`QBOX_TC397_FIRMWARE` override도 유지한다.
`scripts/build/build_vmcu_zephyr.sh`는 `zephyr-vmcu` Yocto target의 호환 진입점이다.

### Yocto 통합 검증 (2026-10-06)

| 검사 | 결과 | 증거 (`build/qbox-apollo-qvp/` 기준) |
|---|---|---|
| `qemu-apollo-native tricore-toolchain-native` | PASS: 594 tasks | `vmcu-yocto-providers.log` |
| `zephyr-vmcu` firmware 빌드·배포 | PASS: 909 tasks | `vmcu-yocto-firmware.log` |
| 배포 QEMU + 배포 toolchain으로 TC397 최소 모델 회귀 | PASS: cold boot 21 + QMP reset 21 | `vmcu-yocto-tc397-model/result.json` |
| 일반 `./yocto_build.sh --bsp`, overlay 수정 후 재빌드 포함 | PASS: 각 5,892 tasks | `vmcu-yocto-bsp.log`, `vmcu-yocto-bsp-final.log` |
| 관련 회귀 tests | PASS: 104 | `vmcu-yocto-tests.log` |
| 배포 QEMU·Zephyr ELF + 실제 SIL Kit CAN 연동 | PASS: 9 checks | `vmcu-yocto-silkit-final/result.json` |
| Yocto firmware를 사용한 Apollo 전체 연동 | PASS: 부팅·AP/SI UART·5초 보고·timeout 복구·GPIO | `vmcu-yocto-runtime-final/vmcu-result.json` |

BSP 빌드에는 기존 forced-task taint 경고 5건이 있었으며 task 실패는 없었다.
최종 빌드는 `prj.conf` 수정만으로 firmware가 다시 빌드·배포되는 것도 확인했다.
SIL Kit 검증은 실제 registry/participant와 Classic CAN, extended CAN FD 64-byte/BRS,
RX/TX IRQ callback, 단절 시 BUS-OFF 및 controller restart 복구를 확인했다.

초기 실패 기록도 보존한다. `vmcu-yocto-silkit/result.json`에서는 긴 FD shell 명령이
64-byte RX ring에서 잘렸다. `CONFIG_SHELL_BACKEND_SERIAL_RX_RING_BUFFER_SIZE`를
256으로 늘려 재빌드한 최종 ELF로 위 9 checks가 통과했다.
`vmcu-yocto-runtime`의 초기 주기 검사는 SI의 즉시 상태 보고와 다음 정기 보고 간
3,500 ms를 정기 주기로 판정해 실패했다. 검증기가 report sequence 두 번을 기다린 후
측정하도록 수정했으며, 정기 보고 허용 범위 4,000–8,000 ms는 유지했다.
최종 재검증은 PASS다. AP 관리 서비스 중단 중에도 SI PFDI 보고가 유지됐고,
Safety UART timeout·재개 및 wake/reset GPIO 왕복을 확인했다.
물리 timing, 실제 PMIC rail 차단과 SoC cold power cycle은 검증 범위가 아니다.

TC397 최소 모델 회귀는 별도의 freestanding 시험 firmware로 CPU·memory·STM·IRQ·UART를
확인한다. 이 결과를 Zephyr app 또는 Apollo 전체 연동 통과로 해석하지 않는다.

아래의 독립 checkout·로컬 빌드 명령과 수치는 **도입 당시의 기록**이며,
현재 빌드 방법과 검증 결과는 위 절을 사용한다.

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

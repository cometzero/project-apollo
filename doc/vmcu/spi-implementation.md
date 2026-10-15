# TC397 master / SI CL0 slave 직접 SPI 구현

2026-10-15 구현 기록. [계획](spi-implementation-plan.md)과
[선정 근거](spi-master-decision.md)를 따른다. 구현·집중 시험을 완료했고,
배포 BSP 빌드와 전체 기능 결과는 아래 검증 절에서 별도로 기록한다.

## 연결과 선택

TC397 QSPI0 master ↔ 전용 TCP ↔ QBox `vmcu_spi_slave` ↔ SI CL0 SCP firmware다.
SI PL061 pin5 → TC397 PORT0 pin5가 `SOC_SPI_REQ`다. SI는 frame을 준비한 후
level을 반전하고 해당 frame의 firmware ACK까지 유지한다. MCU는 입력을 polling한다.
기존 pin0..4와 AP 관리 UART, MCU console, CAN/SIL Kit 연결은 유지한다.

```sh
./yocto_build.sh --keep-conf --bsp
./run_qbox_yocto.sh --bsp --vmcu-link spi
# 차량 CAN도 함께 검증할 때:
./run_qbox_yocto.sh --bsp --vmcu-link spi --sil-kit
```

기본은 `--vmcu-link uart`다. SPI 선택은 BSP companion이 있는 tmux 또는 dashboard
실행에서 지원한다. 일반 headless root launcher는 기존대로 companion을 만들지 않는다.
전용 기능 검증기가 tmux session/FIFO와 소유 process 정리를 관리한다.

Yocto는 `zephyr-vmcu-tc397.elf`와 `zephyr-vmcu-tc397-spi.elf`를 함께 빌드한다.
SPI ELF는 `CONFIG_VMCU_SAFETY_SPI=y`다. 각 ELF의 `.json` sidecar에는 transport와
SHA256이 들어가며 launcher가 불일치를 거부한다. 기존 metadata 없는 UART ELF는
호환성을 위해 허용하되 SPI에는 manifest를 요구한다.

계획의 양쪽 firmware build-time selector 대신 **SCP는 명시적 QVP capability를
읽어 선택**한다. slave는 항상 매핑되고 `0x28`은 SPI endpoint가 설정된 경우에만
1이다. 따라서 같은 서명 SI/RSE image로 두 profile을 실행할 수 있다. SPI 선택 후
오류가 나도 UART로 fallback하지 않는다. MCU는 별도 ELF로 선택한다.

## Controller와 wire 계약

| 항목 | 구현 |
|---|---|
| TC397 QSPI0 | MMIO `0xf0001c00`, FIFO4, TX/RX/error SRC `0x3c/0x3d/0x3e` |
| supported profile | master, CS0, mode0, 8-bit/MSB-first, 초기 driver 설정 1MHz |
| MCU driver | Zephyr SPI API, RX/error IRQ, 하나의 연속된 full-duplex buffer |
| Apollo slave | **QVP 전용** MMIO `0x2a840000`, INTID43/SPI11, TX/RX FIFO64 |
| reset scope | AP reset과 독립. 전체/SI 해당 reset은 slave state를 reset |
| GPIO | pin5 retained toggle, 확장 SoC mask `0x27`, MCU drive mask는 `0x18` 유지 |
| endpoint | QEMU server `tc397-qspi.chardev=tc397spi`, QBox client `QBOX_APOLLO_VMCU_SPI_ENDPOINT` |

Apollo block은 검증되지 않은 DW SSI slave register를 가장하지 않는 명시적 QVP
장치다. RD-Aspen silicon map/pinmux 또는 vendor binary 호환을 주장하지 않는다.
TC397 QSPI register subset의 근거는 소스에 고정한 Infineon TC39xB iLLD다.

wire record는 64byte다: `SPI1` magic, type/result/flags/count 각1byte,
LE64 connection generation, LE32 ID, LE32 SCLK, CS/mode/bits/reserved 각1byte,
32byte data와 LE32 CRC32/IEEE. 마지막 CRC는 앞60byte에 적용한다.
HELLO1/READY2/TRANSFER3/COMPLETE4/CANCEL5, BEGIN1/END2를 사용한다.
현재 QSPI 모델은 byte별 비동기 요청으로 실제 FIFO4를 보존한다.

COMPLETE result3은 slave TX underrun의 `0xff` filler이며 MOSI는 수신된다.
result4는 RX overflow로 MOSI 손실을 나타내므로 성공으로 처리하지 않는다.
SPI의 full-duplex 특성상 command 전송 중 수신된 유효 SI frame도 처리·ACK한다.
이 경우 해당 retained GPIO toggle을 관찰한 뒤 ACK한다. GPIO 전달이 늦어도
두 요청의 toggle이 합쳐져 사라지지 않도록 하며, 1초 안에 관찰하지 못하면
ACK하지 않고 링크 복구로 전환한다.
wire completion, slave IRQ, firmware 처리 완료/ACK는 서로 다른 사건이다.

QBox socket은 SPI에 한해 bounded256byte write queue와1ms host poll을 사용한다.
부분 송신은 남은 bytes를 보관하고 재접속에 이전 송신을 이어 붙이지 않는다.
QEMU BQL/SystemC owner에서 blocking socket 응답 대기를 하지 않는다.

TX DATA 쓰기는 FIFO에 staging하고 `TX_COMMIT(0x24)`에 게시할 byte 수를 쓴다.
CS BEGIN에서 읽을 수 있는 게시량을 고정하므로, commit 전 시작한 거래는
진행 중 commit이 발생해도 해당 CS 동안 idle만 반환한다. 다음 CS부터 완성된
데이터가 보인다. 이는 QVP 전용 controller 계약이며 SPI bus에 앱의28byte
frame 크기를 하드코딩하지 않는다. SCP는 commit 후 GPIO를 토글한다.

slave reset은 이미 보낸 COMPLETE 뒤에 CANCEL을 순서대로 보내고 local
FIFO/CS/ingress를 초기화한다. master는 진행 중 거래를 오류로 종료하고 새
generation으로 HELLO한다. reset 전에 전달된 byte를 되돌리지는 않는다.

## Firmware 계약

기존28byte 메시지와 PFDI/RPC 정책을 재사용한다. 추가 type8은 ACK이며
SI epoch, 대상 sequence, progress=대상 frame type을 담는다. type9 SYNC는
MCU sender와 나머지0인 요청으로 FIFO를 재준비하고 retained queue head를 다시
전송한다. SYNC는 command replay cache/transaction cursor를 지우지 않는다.

SCP는 최초 SYNC 이후부터 GPIO 요청을 발행한다. MCU 재시작/오류 때 SYNC로
복구하며 SI epoch가 바뀌면 기존 safety/CAN session 정책을 따른다. 초기 연결
retry와 안정 상태 이후 오류는 검증 결과에서 구분한다. safety 데이터의 source는
계속 SI PFDI이며 host adapter가 health frame을 만들어 주지 않는다.

report-off 상태의 SYNC는 새 health를 생성하지 않는다. 보고가 꺼진 채 MCU까지
재시작하면 session epoch를 다시 발견하는 경로는 미지원이다(UART도 같은 제한).
이 시험 범위는 보고 중지/재개와 정상 보고 중 MCU 재시작을 각각 검증한다.

진단 명령은 `vmcu-cli spi status`다. frames/ack/irq/req/failures를 출력한다.
SCP의 `[VMCU_SPI] READY/ACK/SYNC`와 MCU `VMCU_SPI rx=...`를 비교할 수 있다.
supervisor는 SPI profile에서 실제 frame/ACK 로그를 확인해야 `spi_ready=true`로
기록하며180 host초 안에 handshake가 없거나 그 전에 QBox가 정상 종료하면 실패한다.

## 검증

현재 증거 디렉터리는 `build/qbox-apollo-qvp/vmcu-spi/`다.
실행별 FAIL도 보존하고 최종 결과와 혼합하지 않는다.

초기 통합에서 발견한 경계 문제:

- FIFO preload 도중 master BEGIN: TX_COMMIT/BEGIN budget으로 부분 frame 노출을
  차단하고 제어된 interleaving 시험으로 확인했다.
- command MISO 수신 뒤 너무 이른 ACK: retained GPIO를 관찰한 뒤 ACK하도록
  수정했다. 150ms GPIO 지연 fixture에서 기존 ELF FAIL, 수정 ELF PASS를 보존했다.
- AP 복구: UART와 SPI 모두 RSE reload 이후 CPU0 ON MMIO가 나오지 않았다.
  `services-normal`, `services-uart-control`, `services-uart-reset-trace`는 이
  실패 증거다. 코어만 OFF로 요청하는 Apollo firmware 경로의 부모 cluster
  상태 문제를 수정했다. core+cluster OFF를 요청하고 실제 OFF 완료 후
  RSE reload하도록 변경했으며 `services-normal-final`에서 AP 복구와 off/wake
  두 회, 총 네 번의 Linux 부팅을 확인했다.

| 범위 | 현재 결과/증거 |
|---|---|
| QBox FIFO/CS/GPIO/socket partial write | PASS, `component/ctest.log`, `component/lua-config.log` |
| QEMU MMIO/async/reset/FIFO | 배포 binary PASS, `integration/deployed-qspi.log` (CANCEL/late completion 포함) |
| Zephyr 실제 SPI driver/IRQ/GPIO/ACK | 배포 ELF + host SI fixture PASS, `integration/deployed-spi-guest-final.log`; Apollo peer 통합은 별도 |
| SCP native policy | snapshot/safety/SPI/control/RSE PASS, `scp-tests/` |
| root launcher/dashboard/evidence | 104 PASS, `integration/pytest-final.log` |
| full-map static | `integration/full-map.json` — runtime 증거 아님 |
| Yocto BSP | PASS 5904 tasks, `integration/yocto-bsp-runtime-fixes.log`; 기존 forced-task taint 경고 5개 |
| native 회귀 | platform 69 + selected core 63 PASS, `integration/qbox-*-unit-tests.*` |
| SPI 전체 정상 서비스 | PASS, `services-normal-final/vmcu-services-result.json`: PMIC/CAN/MCU reset/AP recovery/off-wake 2회 |
| 보고 중지/재개·GPIO | PASS, `report-off-final/vmcu-result.json`: 5초 보고/AP 관리 중단 독립성/LINK_TIMEOUT 복구/AP reset 중 SI 생존; SPI 진단 출력 때문에 quiet-console 항목은 SKIP |
| 실제 PFDI fault + 복구 | PASS, `services-fault-retry/vmcu-services-result.json`: AP agent STOP→4-core fault→SPI→CAN, AP recovery/off-wake 2회 |
| 기본 UART 회귀 | PASS, `services-uart-retry/vmcu-services-result.json`: PMIC/CAN/MCU reset/AP recovery/off-wake 1회 |
| vMCU 없는 부팅/AP 회귀 | Linux 부팅 PASS; AP SSI/DMA 회귀 FAIL, `no-vmcu-dma-retry/` 및 `no-vmcu-dwc-final/` |
| QSPI fault | 배포 QEMU PASS, `integration/qspi-faults.log`: watchdog/error IRQ/CRC/disconnect/stale generation |
| slave fault | native PASS, `component/faults-ctest.log`: CRC/type/count/FIFO overflow/ingress bound/GPIO lease |

전체 서비스 검증 명령:

```sh
python3 scripts/test/verify_qbox_vmcu_services.py --vmcu-link spi \
  --out-dir build/qbox-apollo-qvp/vmcu-spi/services-normal
python3 scripts/test/verify_qbox_vmcu_services.py --vmcu-link spi \
  --inject-pfdi-timeout --power-cycles 2 \
  --out-dir build/qbox-apollo-qvp/vmcu-spi/services-fault
```

미지원(TC397 직접 SPI 경로): DMA, ERU GPIO interrupt, 다른 SPI mode/word format, multi-CS,
SCLK waveform/연속 clock timing, cross-process virtual-time 동기화/FTTI,
실물 pinmux/전기적 timing. SPI1 transport watchdog의 host time과 guest safety
deadline을 동일 시간으로 해석하지 않는다.

ACK 유실은 SCP native queue-retention/SYNC/replay/ACK 검증 수준이며, 양쪽 guest
사이에서 ACK를 유실시키는 전체 통합 시험은 아직 수행하지 않았다.

`services-fault-final`과 `services-uart-final`은 SPI 초기화 전 simulation
16~17초의 RunOnSysc unknown exception으로 초기 부팅 FAIL이다. 원본 예외가 로그에 없어 원인 미확정이며
동일 배포 이미지 재실행 `services-fault-retry`는 전체 PASS했다.
UART에서도 재현돼 SPI 선택에 한정된 현상은 아니다. 실패 기록은
삭제하지 않았으며 이를 무결점 반복 부팅의 증거로 해석하지 않는다.

별도 host GDB `catch throw` 부팅 3회(`exception-probe/aggregate.json`)는
모두 Linux 준비까지 PASS했고 예외를 재현하지 못했다. 따라서 간헐 RunOnSysc
예외 원인은 여전히 UNVERIFIED다.

AP 회귀 상세: 제한 시험의 memcpy/memset 각5회와 IRQ 증가, 6개 I2C PIO,
SPI0 64byte 정렬16조합은 PASS했다. SPI1 64byte 시험 중 `d350_irq()`의
CH_STATUS(0x1004) 읽기에서 synchronous external abort/kernel panic이 났고
host는 `Blocked re-entrant IO ... arm-dma350`을 기록했다. 4099byte와 뒤의
UART 시험은 실행되지 않았다. 전체 DWC suite도 SPI0/1 DMA timeout을 관찰해
중단했다. 이 결과로 AP DMA 회귀 전체를 PASS 처리하지 않는다.

AP DMA 소스 분석: 기존 QEMU `hw/dma/arm-dma350.c`의 `dma350_tick()`이
service 전체에 `mem_reentrancy_guard.engaged_in_io`를 유지하는 동안, QBox
`qemu-components/qemu_dma350/include/qemu_dma350.h`의 ACK callback이 BQL을 풀고 SystemC 작업을 예약한다.
그 틈의 AP IRQ register read는 QEMU memory guard에 의해 ACCESS_ERROR로
거부될 수 있으며 관찰한 0x1004 abort와 일치한다. 이 DMA model/wrapper는
이번 SPI 변경 대상 파일이 아니다. guard의 올바른 범위/lock 규칙 수정은
별도 회귀 과제로 남겼으며, guard를 일괄 비활성화하지 않았다.

후속 최소 수정 후보는 기존 `qemu-initiator-signal-socket.h` 규칙처럼 ACK
callback에서 BQL을 유지하고 `run_on_sysc(..., false, true)`로 반드시 enqueue하는
것이다. 아직 적용/검증하지 않았고 DMA memory transport 경로도 따로 확인해야 한다.

전체 판정은 `integration/validation-summary.json`의 **PARTIAL_PASS**다.
최종 source/artifact hash는 `integration/final-{source,artifact}-manifest.json`에 있다.

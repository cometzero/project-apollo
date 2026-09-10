# Apollo QVP DMA-350 구현 및 검증

Linux SPI/DMAengine 설정부터 SystemC worker, RAM/FIFO TLM 접근, handshake,
공유 IRQ 및 UART partial RX까지의 실제 경로는
[SystemC DMA 동작과 PlantUML sequence](systemc-dma-sequence.md)에 정리했다.

현재 구성은 **SPI0/1, UART0/1의 TX/RX 전용 8채널**이다.
I2C 및 SPI2/3, UART2/3은 DMA에 연결하지 않는다.
현재 후속 검증 구성은 `IRQ_COMB_NONSEC`를 GIC SPI 279(INTID 311) 하나에 연결한다.
아래의 초기 공유형 변경 설명과 runtime-3 결과는 변경 이력으로 보존하며,
현재 전용 구성의 검증 근거와 구분한다.

## 기준과 적용 범위

기준은 이 디렉터리의 Arm CoreLink DMA-350 TRM r0p0,
문서 102482/0000, release 0000-04 (2023-01-18)이다.
주요 근거는 [기본 명령](0054-DMAC-operation-basic-commands.md),
[trigger 신호](0037-Trigger-input-interface-signals.md),
[flow control](0067-Trigger-input-flow-control-mode.md),
[CH_CMD](0115-CH_CMD.md), [CH_CTRL](0118-CH_CTRL.md),
[source trigger 설정](0134-CH_SRCTRIGINCFG.md)이다.

기존 RSE용 DMA 모델을 비동기 엔진으로 개선하고 AP 인스턴스를 추가했다.
Linux DMAengine을 통해 memory copy/fill과 기존 DesignWare 주변장치의
FIFO DMA를 수행한다. Linux 드라이버가 probe되는 것만으로 DMA 성공을
판정하지 않는다. 게스트 데이터 비교, DMA IRQ 증가, 실제 DMA master의
MMIO 전송 trace를 함께 검사한다.

## AP 배치와 연결

RoS AP memory map의 DMA 영역을 사용한다. 베이스는 `0x31000000`, 예약
크기는 64 KiB이며 구현 레지스터 창은 8 KiB이다. 물리 채널은 8개,
외부 trigger 입력은 8개다. 현재는 채널별 IRQ 대신 `IRQ_COMB_NONSEC`를
GIC SPI 279(INTID 311)에 연결한다. INTID 311은 DMA 예약 범위 303–313에서
QVP용으로 선택한 번호이며, FVP의 개별 combined pin 번호를 확인한 결과는 아니다.
기존 채널별 INTID 303–310 연결은 이번 구성에서 사용하지 않는다.
Secure combined 및 security violation IRQ는 구현/검증 범위 밖이다.

| 주변장치 | TX 채널/request | RX 채널/request | FIFO 주소 |
|---|---|---|---|
| SPI0 | 0 | 1 | 0x30160060 |
| SPI1 | 2 | 3 | 0x30170060 |
| UART0 | 4 | 5 | 0x301a0000 |
| UART1 | 6 | 7 | 0x301b0000 |

각 request 번호와 물리 채널 번호는 동일하고, 다른 peripheral로 채널을
동적 재배정하지 않는다. generic DMA-350 모델의 TRM trigger selector를
없애는 것이 아니라 AP 배선과 Linux의 할당 정책을 고정한 것이다.
SystemC의 단일 worker가 여러 채널을 순회하는 실행 방식은 유지한다.
각 채널의 주소/count/trigger/IRQ 상태는 독립적이며, 이 시뮬레이션 실행 분할을
Linux 물리 채널의 동적 공유와 혼동하면 안 된다.

DMA master는 AP router에 연결되어 CPU와 같은 AP 주소 공간을 사용한다.
AP cold reset fanout에도 연결한다. Lua의 packed signal 자동 연결은
기존 bool 방식과 동일하게 uint32_t socket 바인딩을 지원하도록 확장했다.

## SystemC 동작

- MMIO 콜백은 기다리지 않는다. 단일 `SC_THREAD`가 채널별 상태를 처리하고
  bounded burst 단위로 round-robin 실행한다. TLM 응답 지연은 worker에서
  소비한다. 기본 `burst_bytes=256`, `burst_latency=1ns`는 기능 모델의
  실행 분할 기준이며 실리콘 성능 수치가 아니다.
- IRQ/ACK socket 쓰기는 단일 `SC_METHOD`에 모아 delta event로 전달한다.
  CPU MMIO와 DMA worker가 같은 signal을 직접 쓰는 다중 writer 오류를 막는다.
- source/destination 주소 상위 word, 최대 128-bit 전송 폭, signed/zero
  increment, live 주소와 residue, 1D CONTINUE/FILL 및 기본 WRAP을 처리한다.
- ENABLE/CLEAR/STOP/PAUSE/RESUME/DISABLE, pending/IRQ W1C, ERRINFO를
  worker 상태 전이와 맞춘다. reset은 진행 중 작업과 IRQ를 취소한다.
- 외부 trigger는 active bit 2와 type bits 1:0을 묶은 uint32_t 신호다.
  request → ACK → request 해제 → ACK 해제의 4-phase handshake를 사용한다.
  FIFO bus 응답 전에는 ACK하지 않는다. DMAC-flow 모드와 LAST를 사용하는
  peripheral-flow 모드를 구분한다. DWC 연결은 SINGLE 요청을 사용한다.
- I2C TX는 READ/STOP/RESTART 비트를 보존하는 16-bit DATA_CMD, RX는 8-bit다.
  SPI는 설정된 8/16/32-bit DR 폭을 사용한다. FIFO threshold와 DMA enable이
  request를 제어하므로 요청이 없을 때 FIFO를 임의로 읽고 쓰지 않는다.
- UART RX는 FIFO threshold 아래의 tail을 유지한다. Linux 8250의
  RX timeout → DMA pause/residue 확인 → PIO tail 처리와 공존해야 하므로
  모든 수신 byte에 무조건 DMA request를 발생시키지 않는다.

## Linux 및 소스 소유권

| 저장소 / 파일 | 변경 내용 |
|---|---|
| qbox-platform `systemc-components/dma350/` | 비동기 DMA 엔진, register/trigger/IRQ |
| qbox-platform `platforms/apollo/hw-block/ros.lua` | AP DMA 인스턴스, reset, router, 전용 8개 request/ACK 연결 |
| qbox `systemc-components/common/include/dma-trigger.h` | 공통 4-phase handshake |
| qbox `systemc-components/{i2c,spi,uart}/` | FIFO DMA 요청과 ACK |
| Linux `drivers/dma/arm-dma350.c` | DMAengine slave SG, OF 요청 할당, pause/residue/terminate |
| Linux `drivers/i2c/busses/i2c-designware-*` | 8 command 이상 DMA, 작은 전송 PIO 유지 |
| Linux `arch/arm64/boot/dts/arm/apollo-qvp.dts` | controller 및 SPI0/1, UART0/1의 tx/rx dmas |
| Linux `arch/arm64/configs/apollo_qvp_defconfig` | DMA-350, dmatest, DesignWare SPI DMA |
| meta-hsoc-auto-solutions `recipes-core/images/nexios-bsp-initramfs.bb` | QVP BSP에 dmatest 모듈 포함 |

Linux 채널과 물리 채널을 1:1로 고정한다. DT의 `#dma-cells = <1>`은
전용 채널 번호이며 해당 HW request 번호와 같다. 별도 memory virtual pool은 없다.
하드웨어 command-link 대신 소프트웨어 SG chaining을 사용한다.
SINGLE handshake와 FIFO tail을 맞추기 위해 slave max_burst는 1이다.
기존 DesignWare SPI DMA 및 8250 DMA 코드를 사용하며 별도 SPI/UART Linux
드라이버를 만들지 않았다.

채널별 virt-dma queue는 유지하되 물리 채널 간 동적 스케줄러는 제거한다.
STOP 완료 전에는 descriptor를 해제하지 않으며 지연된 STOP은 STOPPED IRQ
또는 synchronize 재시도로 마무리한다. 재사용 가능한 I2C DMA 구현은
보존하지만 현재 AP DT에는 dmas가 없으므로 해당 포트들은 PIO를 사용한다.

## 전용 채널 전환과 upstream 대비 최소 변경 원칙

비교 기준은 로컬 커널에 포함된 최초 upstream 드라이버 커밋
`5d099706449d54b4693a1c6bb7c2251072234508`
(`dmaengine: Add Arm DMA-350 driver`)이다. 해당 파일 blob은
`9efe2ca7d5ec97c6dc270c09e07d68eec8d8431e`이며, 작업 전 Linux HEAD의
파일 blob과 동일함을 확인했다. 원 커밋 설명도 basic mem-to-mem 지원이며
peripheral/SG는 향후 확장 대상으로 명시한다. 이는 최신 원격 upstream을
새로 동기화했다는 의미가 아니다.

전용 채널 전환에서는 원래 드라이버의 `dma_chan ↔ MMIO bank/IRQ` 1:1
구조로 돌아간다. 동적 physical allocation, controller-wide pending list,
추가 memory virtual pool, owner handoff를 위한 global lock은 필요 없으므로
제거한다. 기존 virt-dma의 **동일 채널 내 descriptor queue**는 유지한다.
이 queue는 주변장치 간 물리 채널 공유와 다른 개념이다.

최소 변경의 경계는 다음과 같다.

- 유지할 추가 기능: OF channel lookup, slave config/SG, FIFO 고정 주소,
  source/destination trigger 설정. 없으면 기존 SPI/8250 DMA client를 연결할 수 없다.
- 유지할 정확성 수정: source trigger bit 25, 비동기 PAUSE/STOP 완료 확인,
  residue 및 descriptor/IRQ 수명 처리. 작은 diff를 위해 잘못된 동작으로 되돌리지 않는다.
- 제거할 구조: 36개 virtual channel, 물리 채널 allocator와 pending scheduler,
  동적 `serving` owner, 공유를 위해 추가했던 global locking.
- 별도 변경하지 않을 부분: 범용 DMA-350 TRM selector 및 reusable I2C/DWC 모델의
  DMA 기능. AP의 I2C DT와 배선에서 DMA를 제외하여 PIO로 운용한다.

8개 전용 채널을 peripheral client가 모두 점유한 동안에는 dmatest가 사용할
별도 채널이 없다. 재현 스크립트는 UART를 열기 전에 아직 미점유된 채널로
memory self-test를 수행하고 해제한다. peripheral DMA 중 다른 채널을 빌리거나
request를 바꾸는 scheduler는 사용하지 않는다.
DMAengine capability는 controller 단위이므로 generic memory client가
peripheral보다 먼저 미점유 채널을 확보할 수는 있다. 따라서 memory test와
peripheral 최초 open/probe를 동시에 실행하지 않는다. 전용 연결은 물리 채널과
request의 고정 대응을 의미하며, generic memory API를 별도 장치로 격리한 것은 아니다.

전용 구현 1차의 파일은 1048행이며 기준 대비 `+565/-177`, 순증 388행이었다.
초기 공유형 1194행보다 146행 줄었다. 변경량에는 기존 register programming
코드를 SG용 공통 함수로 옮긴 행도 포함된다. 최소 diff를 지향하되 slave DMA가
없던 upstream 코드에 필요한 기능까지 생략하지는 않았다.

| 영역 | 전용 구현에서의 처리 | 초기 공유형과의 차이 |
|---|---|---|
| 채널 자료구조 | 원래 `d350.channels[]`, `d350_chan.base/irq` 유지 | `d350_phy`, `serving`, `pending_node`, 별도 배열 제거 |
| 전송 queue | 원래 채널별 `vchan_issue_pending()`/`vchan_next_desc()` 사용 | `get_phy/alloc_phy/release_phy` 및 WAITING 상태 제거 |
| IRQ 수명 | 원래 client allocation의 `request_irq(..., IRQF_SHARED)` / free의 `free_irq()` 유지 | probe-time physical IRQ 방식 제거 |
| Lock | 채널의 기존 `vc.lock` 사용 | controller global lock 제거; IRQ status 읽기도 vc.lock 안에 배치 |
| Capability | 채널별 width와 trigger 지원 검사 | 공통 최소 width 대신 실제 전용 채널 width 사용 |
| OF | cell의 채널 번호가 곧 request 번호 | 요청별 virtual slot 대신 기존 물리 채널 반환 |
| Slave DMA | config, 방향별 FIFO/trigger, mapped SG 명령 추가 유지 | 기존 SPI/8250 client 호환에 필요한 부분 |
| Memory DMA | memcpy/memset 및 upstream alignment 계산 유지 | 배열 descriptor 형식 및 길이 검사만 필요한 범위로 적용 |
| 비동기 제어 | PAUSE/RESUME poll, STOP pending 및 synchronize 유지 | 채널 handoff 없이 해당 채널의 descriptor 수명만 관리 |

IRQ 상태를 lock 밖에서 읽는 원래 순서도 그대로 유지하지 않았다.
같은 채널이라도 다른 CPU의 terminate/restart와 겹치면 이전 DONE을 새
descriptor 완료로 해석할 수 있기 때문이다. 이처럼 구조 단순화와 무관한
정확성 수정은 남겼다. 현재 전용 정책은 request 수가 물리 채널 수보다 큰
구성을 probe에서 거절하며, AP는 둘 다 8개다.

여전히 미지원/미검증인 범위는 hardware command-link/cyclic DMA,
peripheral-flow LAST의 Linux 통합, 강제 STOP 실패, active hot-unbind다.
STOP synchronize의 전체 재시도 상한이 없는 기존 한계도 그대로 남아 있다.

## Upstream ANYCH 선적용과 동일 IRQ 배열 (최신)

Upstream의 [643c1e1ae3eb](https://github.com/torvalds/linux/commit/643c1e1ae3eb3cd9be31e83c2240e41849a6cb56)
(`dmaengine: arm-dma350: enable ANYCH interrupt for shared IRQ wiring`)를
로컬 기능 변경보다 먼저 cherry-pick했다. 원본은 probe에서
`DMANSECCTRL + NSEC_CTRL`의 `INTREN_ANYCHINTR_EN`을 RMW하는 9행 패치다.
최신 kernel 전체나 allocator API 변경은 가져오지 않았다.

로컬 cherry-pick ID는 `a78ef8fd26d3`이며 원본과 stable patch-id
`dbacb0919f4d08d441164fba8ab28844cd373c4c`가 일치한다.
Upstream author, 메시지, 기존 sign-off/review trailer 및 cherry-pick 출처를
보존했다. Upstream의 긴 제목은 원문 그대로 두었고, 로컬 Conventional Commit
8개의 메시지 규칙과 sign-off는 별도로 검증했다.

정리 순서는 다음과 같다. 기존 7개 기능별 commit은 합치지 않고 유지했으며,
미커밋 combined IRQ 변경만 하나로 보관한 후 재적용했다.

```text
6ff44c9184f5  기존 공개 기준
a78ef8fd26d3  upstream ANYCH enable
4235d92f5497  source trigger bit 수정
acda1d110db7  memory length 검사
d6f8d67a829f  coherency 저장
ae2c275c1f6f  pause/resume poll
aeccd14664a5  slave DMA/SG
85de041e274a  I2C DMA client
8385c3199cd4  Apollo DMA DT/config
41b96d0832e8  DT의 동일 IRQ 8회 지정
```

최종 commit `41b96d0832e8`은 **DTS만 변경**한다. IRQ는 아래처럼 채널별
항목을 유지하면서 모두 같은 GIC SPI 번호를 지정한다.

```dts
interrupts = <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>,
             <GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>;
```

`interrupt-names`는 없다. `combined-irq` lookup/분기/별도 register 정의와
조건부 ANYCH write는 제거했다. Driver와 binding은 최종 commit의 부모와
동일하며, 기존 `platform_get_irq(pdev, i)`와 `IRQF_SHARED`가 같은 물리 IRQ를
처리한다. 따라서 실제 GIC 선은 여전히 하나이고 DT resource 항목만 8개다.
기존 `IRQ_COMB_NONSEC` SystemC 출력과 GIC INTID 311 연결은 유지한다.

Linux의 원 branch `apollo-fvp-linux-6.18-rt`에 반영했고 push는 하지 않았다.
다른 저장소의 커밋은 재작성하지 않았다. 다음 복구 참조도 남겨 두었다.

- `backup/20260910-dma350-anych-old-series`: 기존 7개 commit의 HEAD.
- `backup/20260910-dma350-anych-combined-wip`: 미커밋 변경 보관 snapshot.
- `backup/20260910-dma350-anych-final-with-name`: 이름 기반 중간 구현.

### Upstream-first 최종 검증

최종 branch HEAD `41b96d0832e8`에서 `./yocto_build.sh --keep-conf --bsp`를
실행했다. 5577 tasks 전체 성공(5495 reused, 기존 taint 경고 5개)이며
`build/dma350/upstream-anych-shared-bsp-build.log`에 보존했다.
Provider unit은 qbox-platform 58/58(5.42초), qbox 60/60(18.73초) PASS다.
일반 도구 회귀는 pytest 13/13, shellcheck, Lua 문법 및 diff-check PASS다.

런타임 증거는 `build/dma350/upstream-anych-shared-runtime-1/`에 있다.
게스트는 DT `interrupts`의 크기가 96 byte인지 확인하고, 12-byte specifier
8개를 각각 추출하여 모두 동일한지 비교한다. `interrupt-names` 부재도 확인한다.
SPI/UART를 모두 연 뒤에는 `/proc/interrupts`에 DMA IRQ가 한 줄이며
GIC hwirq 311과 8개 채널 이름이 모두 있는지 검사한다.

| 항목 | 결과 |
|---|---|
| BSP 부팅 및 공유 IRQ topology | PASS, specifier 8개/물리 IRQ 1개 |
| memcpy/memset | 각각 5회 PASS |
| SPI0/1 | 64/4099-byte loopback PASS, 각 TX/RX DMA 66544 byte |
| UART0↔1 | 양방향 17/128/512/4099-byte PASS, 각 TX DMA 4756 byte |
| UART RX | DMA 1819/225 byte 관측, PIO 혼용 |
| multi-entry SG | `sg_len=2` event 2개 관측 |
| I2C0–5 및 SPI2/3 PIO | 데이터 비교 PASS, 제외 FIFO DMA 접근 없음 |
| DMA trace | 328 operations 중 memory 10개, validator PASS |
| 최종 register | NSEC_CTRL=1, NSEC_CHINTRSTATUS0=0, NSEC_STATUS=0 |
| IRQ idle 확인 | 1초 간격 counter 140→140 |

게스트 marker는 다음과 같다.

```text
APOLLO_DMA350|interrupt=shared|specifiers=8|lines=1|hwirq=311|status=PASS
```

`guest-validation.log`, `dma-trace.log`, `dma-validation.json`,
`sg-kprobe.trace`, `combined-registers.log`, `irq-idle.log`,
`guest-artifacts.tar.gz`에 원시 자료를 보존했다.
Source hash는 `build/dma350/upstream-anych-shared-source.sha256`과 일치한다.
EEPROM 복구와 probe 제거 후 테스트 VM을 종료했다.
전체 플랫폼 coverage는 기존의 G1/AP memory-map 증거 미수집으로 FAIL이며,
이번 DMA 경로 PASS와 구분한다. Linux는 clean이고, 최상위 gitlink 및 다른
저장소의 미커밋 문서/모델/테스트 변경은 별도로 남겨 두었다.

## Atomic commit 기준과 IRQ_COMB_NONSEC 후속 구성 (이력)

기존 구현은 20개 atomic commit으로 저장했다. Linux 7개, QBox core 4개,
QBox platform 4개, BSP layer 1개, 최상위 저장소 4개다. 모든 메시지와
`Signed-off-by`를 검증했으며 push는 수행하지 않았다.

| Linux commit | 분리한 변경 |
|---|---|
| 67a8b68fb7b6 | source trigger bit 25 수정 |
| 3aa79ae70f75 | memory transfer 길이 검사 |
| e3bf924458f4 | 채널별 coherency 저장 |
| 89a4f4bfe239 | PAUSE/RESUME 상태 poll |
| 489cfe9634cc | slave SG/전용 채널/OF 및 연결된 수명 처리 |
| 30e645916066 | DesignWare I2C DMA client |
| e6fe92b84025 | Apollo QVP DT/defconfig 활성화 |

최상위 기준은 `cbeaea95ddb1`이다. 이 기준의 Linux 최종 tree는 커밋 전
검증한 tree와 동일하며 기존 코드를 수정하여 커밋을 만든 것이 아니다.
아래 combined IRQ 변경은 당시 별도 미커밋 검증 변경이었다.
이후 Linux 변경은 위 upstream-first series로 정리했으며, 다른 저장소의
후속 미커밋 변경은 별도로 유지했다.

### IRQ 결합 방식

TRM [interrupt operation](0102-Interrupt-operation.md),
[NSEC_CHINTRSTATUS0](0154-NSEC_CHINTRSTATUS0.md),
[NSEC_STATUS](0155-NSEC_STATUS.md), [NSEC_CTRL](0156-NSEC_CTRL.md)을 기준으로 한다.

| Register/output | 현재 처리 |
|---|---|
| NSEC_CHINTRSTATUS0, offset 0x200 | Non-secure 채널의 interrupt flag를 bit별로 집계 |
| NSEC_STATUS, offset 0x208, bit 0 | pending이 있고 global gate가 켜졌을 때 INTR_ANYCHINTR=1 |
| NSEC_CTRL, offset 0x20c, bit 0 | INTREN_ANYCHINTR로 combined channel IRQ 허용 |
| irq_comb_nonsec | 위 combined 상태를 level signal로 출력 |

SystemC의 기존 per-channel IRQ는 유지하고 optional combined output을 추가했다.
출력은 기존 단일 `SC_METHOD`에서만 갱신한다. 최신 Linux DT는
`<GIC_SPI 279 IRQ_TYPE_LEVEL_HIGH>`를 채널 수에 맞춰 8회 나열한다.
`interrupt-names`는 지정하지 않는다. 기존 `platform_get_irq(pdev, i)`가
각 항목에서 동일 IRQ 번호를 얻으므로 이름 조회나 별도 분기가 필요 없다.
NSEC_CTRL bit 0은 아래의 upstream ANYCH 패치가 probe에서 RMW로 활성화한다.

기존 `request_irq(..., IRQF_SHARED, ..., dch)` 및 `d350_irq()`를 그대로 사용한다.
GIC IRQ 선은 하나지만 Linux에는 채널별 action 8개가 등록된다.
각 action은 자기 채널 상태만 검사/clear한다. 별도 controller ISR이나
새로운 dispatcher 자료구조를 추가하지 않았다. 서로 다른 IRQ 번호를 지정하면
기존 채널별 IRQ 방식으로 동작한다. 로컬 shared-IRQ driver 분기와 binding
변경은 제거했으며, 공유 IRQ 활성화 코드는 upstream의 9행 패치만 사용한다.

### 검증 범위와 제한

SystemC unit은 두 채널 동시 pending, 초기 global gate 차단/활성화,
한 채널만 clear했을 때 line 유지, 모두 clear 시 deassert,
완료 전 channel mask, read-only summary/status, error 및 reset을 검사한다.
Provider `do_check`는 qbox-platform 58/58(5.73초), core 60/60(23.48초) PASS다.
`combined-provider-do-check.log`에 보존했다.

최신 게스트 스크립트는 DT의 IRQ specifier 8개가 모두 동일하고 이름 속성이
없는지 확인한 다음, SPI0/1과
UART0/1을 모두 확보한 시점의 `/proc/interrupts`를 저장한다.
DMA 관련 IRQ가 정확히 한 줄이며 GIC hwirq 311과 8개 채널 이름이 있는지
검사하고, data/IRQ counter/DMA FIFO trace 검증을 수행한다.
기존 `sg_len=2` kprobe 검증도 병행한다.

현재 model은 모든 채널을 Non-secure로 취급한다. TrustZone attribution,
global all-idle/stopped/paused IRQ 및 Secure violation IRQ는 범위 밖이다.
NSEC_CTRL은 bit 0만 지원하며 NSEC_STATUS의 해당 bit는 read-only다.
따라서 이번 검증은 채널 IRQ 결합 경로의 검증이지 모든 DMA unit IRQ의 구현을
뜻하지 않는다. Binding YAML 구문 검사는 통과했지만 host의 `dtschema` 모듈
부재로 당시 `dt-doc-validate`는 수행하지 못했다. 최신 구성은 해당 custom
binding 변경을 원복하여 기존 binding을 그대로 사용한다.

### 초기 이름 기반 단일 IRQ 런타임 결과 (이력)

`./yocto_build.sh --keep-conf --bsp`는 5577 tasks 전체 성공
(5495 reused, 기존 taint 경고 5개)했다. `build/dma350/combined-bsp-build.log`와
`combined-provider-do-check.log`에 빌드 및 unit 결과를 보존했다.

새 BSP를 [재현 방법](#재현-방법)의 trace 환경으로 실행하고,
`build/dma350/combined-runtime-1/`에 검증 자료를 저장했다.
`dma-validation.json`은 PASS이며 AP DMA operation 347개 중 memory
operation은 10개다. Source hash는 `build/dma350/combined-source.sha256`에
저장했고 실행 후 일치 여부를 확인했다.

| 항목 | 관측 결과 |
|---|---|
| BSP boot | PASS |
| IRQ 연결 | Linux IRQ 39 한 줄, GIC hwirq 311, 채널 action 8개 |
| memory DMA | memcpy/memset 각 5회 PASS |
| SPI0/1 | 64/4099-byte loopback PASS; 각 TX/RX DMA 66544 byte |
| UART0↔1 | 양방향 17/128/512/4099-byte PASS; 각 TX DMA 4756 byte |
| UART RX | DMA 196/175 byte, 나머지는 PIO 혼용 |
| multi-entry SG | `sg_len=2` kprobe event 2개 관측 |
| I2C0–5 및 SPI2/3 PIO | 데이터 비교 PASS; 해당 FIFO DMA 접근 없음 |
| 전송 후 IRQ | pending/status 0, 1초 간격 IRQ counter 141→141 |
| Python 판정기/주소 map 회귀 | 12/12 PASS, 채널별 IRQ를 combined 증거로 인정하지 않는 negative test 포함 |

UART를 모두 연 상태의 실제 `/proc/interrupts` 기록은 다음과 같다.
Linux IRQ 번호와 CPU별 counter는 실행마다 바뀔 수 있으며,
고정 검증 대상은 hwirq 311과 단일 행 및 채널 이름이다.

```text
39: 128 0 0 0 GICv3 311 Level dma0chan1, dma0chan0, dma0chan3, dma0chan2, dma0chan5, dma0chan4, dma0chan7, dma0chan6
```

전송 종료 후 게스트에서 다음 read-only 확인도 수행했다.

```sh
devmem2 0x3100020c w  # NSEC_CTRL: 0x00000001
devmem2 0x31000200 w  # NSEC_CHINTRSTATUS0: 0x00000000
devmem2 0x31000208 w  # NSEC_STATUS: 0x00000000
```

원시 자료는 `guest-validation.log`, `dma-trace.log`, `sg-kprobe.trace`,
`combined-registers.log`, `irq-idle.log`, `guest-artifacts.tar.gz`다.
테스트 후 EEPROM을 복구하고 임시 probe와 테스트 VM을 정리했다.
전체 플랫폼 coverage audit는 이전과 같이 G1 미실행과 AP memory-map
증거 부재로 FAIL이다. 이는 단일 DMA IRQ 경로의 PASS와 구분한다.
채널별 legacy Linux DT를 다시 부팅하는 별도 비교 실행은 하지 않았으며,
기존 model 채널별 IRQ unit과 RSE/BSP 부팅 회귀는 통과했다.

## 단일 free 복원 및 pause/probe 재검토 (이전 단계)

명시적으로 요청한 변경은 다음과 같이 적용했다.

- `d350_desc_free()`를 upstream과 동일한 `kfree(to_d350_desc(vd));`로 복원했다.
- SG 준비 시 `kcalloc(sg_len, sizeof(*desc), GFP_NOWAIT)`로 원래 descriptor 타입의
  배열 전체를 한 번 할당한다. 각 `next`는 같은 allocation 내부의 다음 항목을
  가리킨다. head만 virt-dma에 등록하므로 완료/오류/STOP 후 원본 free 한 번으로
  전체를 해제한다. 준비 중 실패도 allocation 시작 주소를 한 번만 해제한다.
- memcpy의 `cmd[11] = 0;`, memset의 `cmd[9] = 0;`을 원본대로 복원했다.
  Slave의 `cmd[11]`은 실제 trigger 설정이므로 변경하지 않았다.

각 SG 항목별로 별도 할당하던 이전 단계와 구분해야 한다. 배열의 중간 항목은
단독으로 free하지 않는다. `kcalloc()`의 크기 곱 overflow 검사와 zero 초기화를
사용하고, SG 총 byte 수의 overflow 검사도 유지한다.

### d350_pause 검토 결론

HW 상태 확인은 유지가 필요하다. [CH_STATUS](0116-CH_STATUS.md)의
`STAT_PAUSED`는 실제 pause 성공, `STAT_RESUMEWAIT`는 SW resume 대기를 뜻한다.
`serial8250_rx_dma_flush()`는 `dmaengine_pause()` 직후 residue를 읽어 TTY에
데이터를 넘기고 `terminate_async()`를 호출한다. PAUSE write 직후 software
status만 DMA_PAUSED로 바꾸면 DMA가 아직 buffer를 갱신하는 시점과 겹칠 수 있다.

반면 1us poll 간격/1000us 상한은 TRM에 정해진 상수가 아니라 현재 driver의
bounded wait 정책이다. 실제 하드웨어에서의 적절한 상한은 별도 검증 대상이다.
`&& dch->desc`는 lock 아래 `DMA_IN_PROGRESS` 또는 `DMA_PAUSED`의 active
descriptor invariant와 중복이므로 pause/resume에서 제거 가능한 조건이다.
이번 요청의 pause/probe 부분은 검토 범위로 처리하여 추가 수정하지 않았다.
PAUSE timeout fault injection은 미검증이며, 8250 client가 pause 반환값을
확인하지 않는 점도 남은 제한이다.

### Probe 변경별 재검토

| 변경 | 판단 |
|---|---|
| MEM_TO_DEV/DEV_TO_MEM, DMA_SLAVE 및 config/prep_slave_sg 등록 | SPI/8250 DMA client 연결에 필요 |
| min_burst/max_burst=1 | 현재 SINGLE 요청과 SPI FIFO threshold에 맞는 정책 |
| max_sg_burst=1 | HW 자동 SG 없이 SW가 재설정하므로 필요한 capability 설명 |
| request 번호 배정 및 OF xlate/controller 등록·실패 unwind | DT의 전용 채널 연결에 필요 |
| 채널의 trigger/selector 기능 검사 | 실제 사용하는 기능의 가용성 검사로 유지 가능 |
| dch->coherent 저장 | 원본의 미대입 필드를 보완하여 memory transaction 속성에 반영 |
| HAS_CMDLINK 필수 gate 제거 | 직접 MMIO programming 및 SW SG에는 HW command fetch가 필요하지 않음 |
| nreq > nchan이면 controller 전체 probe 실패 | 불필요한 제한으로 제거 권고. Trigger 수와 물리 채널 수는 다를 수 있고, 사용하지 않는 trigger가 추가되어도 문제없음 |
| nreq 읽기를 allocation 앞으로 이동 | 위 거절 검사에 동반된 재배치; 해당 검사 제거 시 원래 위치로 복원 가능 |
| dma_set_mask_and_coherent 반환값 미검사 | 원본부터 있는 코드로 이번에 변경하지 않음; 실패 환경 검증을 완료한 것은 아님 |

`nreq > nchan` 조건을 없애더라도 xlate의 `channel < nchan` 및
`channel < nreq` 검사가 이미 유효 범위를 제한한다. 현재 AP는 8/8이므로
해당 거절 조건은 실행되지 않는다. 이 절의 제거 권고는 **검토 결과이며
아직 적용하지 않은 항목**이다. 그 외 probe를 원본으로 모두 돌리면 slave
등록이나 OF 연결까지 없어지므로 현재 DMA 구성이 동작하지 않는다.

### 단일 allocation 구현 검증

`./yocto_build.sh --keep-conf --bsp`: PASS, 5577 tasks 중 5501 reused,
기존 taint 경고 5개. 로그는 `build/dma350/single-free-bsp-build.log`다.
Strict checkpatch는 `single-free-checkpatch.log`에 0 errors/0 warnings/0 checks로
기록했으며, pytest 판정기/주소 map 테스트 11개와 diff-check도 통과했다.

`build/dma350/single-free-runtime-1/`에서 BSP 부팅 및 DMA validator PASS를
확인했다. memcpy/memset 각 5회, SPI0/1 64/4099-byte loopback,
UART0↔1 17/128/512/4099-byte 양방향 비교, I2C0–5 및 SPI2/3 PIO가 통과했다.
AP trace 388개에서 전용 channel/request/FIFO 대응을 확인했다.
SPI의 4096+3-byte 경계와 UART의 `sg_len=2` kprobe event 2개도 확인하여
단일 allocation의 내부 descriptor 연결을 실제로 실행했다.
각 UART TX는 DMA 4756 byte, RX DMA는 164/204 byte이며 나머지는 PIO 혼용이다.

자료는 `guest-validation.log`, `dma-trace.log`, `dma-validation.json`,
`sg-kprobe.trace`, `guest-artifacts.tar.gz`에 보존했다.
`build/dma350/single-free-source.sha256`과 실행 후 source hash가 일치한다.
EEPROM 복구, 원시 자료 회수, 임시 probe 제거 후 테스트 VM을 종료했다.
전체 플랫폼 coverage는 기존과 같이 G1 및 AP memory-map 증거 부재로 FAIL이며
DMA 전용 결과와 구분한다. 메모리 할당 실패/중간 취소/reuse에 대한 강제 오류
주입은 이번 정상 데이터 시험에 포함하지 않았다.

## 원본 descriptor 및 burst 설정 재검토 (이전 단계)

### MAXBURSTLEN=0 강제는 제거

`TRANSCFG_DEVICE`의 `FIELD_PREP(CH_CFG_MAXBURSTLEN, 0)`을 upstream의
`0xf`로 복원했다. 앞선 변경은 SINGLE 요청 정책과 AXI burst 상한을
동일시한 과도한 제한이었다. `0xf`는 최대 16 beat를 허용한다는 뜻이지,
모든 전송을 반드시 16 beat로 실행하라는 뜻이 아니다.

근거는 [CH_SRCTRANSCFG](0125-CH_SRCTRANSCFG.md),
[CH_DESTRANSCFG](0126-CH_DESTRANSCFG.md),
[FIXED/INCR burst](0024-Burst-type-FIXED-INCR-only.md) 및
[trigger flow control](0067-Trigger-input-flow-control-mode.md)이다.
FIFO는 주소 증가 0인 FIXED 접근이고, 외부 요청이 허용하는 transfer 수는
trigger handshake로 제한한다. AXI burst 상한과 별개다.

| 설정 | 현재 값 | 의미 |
|---|---|---|
| CH_*TRANSCFG.MAXBURSTLEN | 0xf | AXI 최대 burst 길이 hint, 최대 16 beat |
| DMAengine min_burst/max_burst | 1/1 | 현재 DWC SINGLE 요청에 맞춘 client FIFO threshold 정책 |
| DMAengine max_sg_burst | 1 | SW 재설정 없이 실행하는 SG 항목 수; 현재 hardware command-link 미사용 |

`max_sg_burst=0`은 unlimited 의미이므로 software IRQ chaining 구현에
적합하지 않다. 이전 `U16_MAX` 값도 HW 자동 SG 능력을 과장했다.
`spi-dw-dma.c`는 이 값이 1이면 TX/RX SG 경계를 맞춰 순서대로 제출한다.
이 처리는 비결정적인 IRQ 지연에 따른 RX FIFO overflow를 피하는 기존
Linux client 동작이며 QBox 전용 우회 코드가 아니다.

현재 SystemC는 `burst_bytes` 실행 단위와 trigger 요청 수로 TLM 접근을
분할한다. 실제 AXI burst cycle/attribute 전체를 모델링하지 않으므로,
이번 기능 검증을 실리콘 AXI burst 길이 검증으로 해석하지 않는다.

### d350_cmd와 d350_alloc_desc 제거

두 요소는 SG 명령을 배열로 보관하기 위해 추가한 설계였으며 필수는 아니었다.
원래 `d350_desc`의 `vd`, `command[16]`, `xsize`, `xsizehi`, `tsz`를 복원하고
`next` 포인터만 추가했다. memcpy/memset은 원래처럼
`kzalloc(sizeof(*desc), GFP_NOWAIT)`로 직접 할당한다.

Slave SG는 같은 descriptor를 항목별로 할당해 연결한다. 첫 descriptor만
virt-dma의 cookie/callback을 소유하고, `dch->cmd`가 현재 명령을 가리킨다.
중간 명령 DONE에서는 다음 항목으로 이동하며 마지막에서만 완료를 통지한다.
residue는 현재 HW 잔여량과 후속 항목 길이의 합이다. 할당 실패와 최종 free는
전체 연결을 해제하고, STOP 완료 전에는 head와 tail을 모두 보존한다.
재사용 시에는 current pointer를 head로 되돌린다.

원본 구조 재사용의 대가로 tail에도 사용하지 않는 `virt_dma_desc` 공간이
포함된다. 현재 짧은 SG에 대해 원본과의 차이를 줄이는 선택이며, 별도 compact
command 배열을 다시 도입해 메모리 최적화를 수행한 것은 아니다.

### cmd 배열 항목별 확인

memcpy/memset의 값과 배치는 upstream으로 복원했다.
`kzalloc`으로 0이 되는 `cmd[11] = 0`(memcpy), `cmd[9] = 0`(memset)은 쓰지 않는다.
`LINK_LINKADDR` header는 유지하여 해당 0 값을 HW LINKADDR에 기록한다.
소프트웨어의 `desc->next`를 HW LINKADDR로 넘기지 않는다.

| 항목 | memcpy | memset | 새 slave command |
|---|---|---|---|
| cmd[0] | 원본 register header | 원본 register header | source/destination trigger-config 선택 추가 |
| cmd[1] | 원본 CONTINUE/TRANSIZE/DONETYPE | 원본 FILL/TRANSIZE/DONETYPE | FIFO 방향에 따라 source bit25 또는 destination bit26 |
| 주소 | cmd[2:3] SRC, cmd[4:5] DST | cmd[2:3] DST | cmd[2:3] SRC, cmd[4:5] DST |
| XSIZE/HI | cmd[6:7], 원본 xsize 필드 | cmd[4:5], 원본 xsize 필드 | cmd[6:7], 양쪽 transfer 개수 |
| TRANSCFG | cmd[8:9] WB/NC | cmd[6] WB/NC | cmd[8:9], memory WB/NC와 FIFO Device |
| 증가량 | cmd[10], 양쪽 1 | cmd[7], destination 1 | cmd[10], memory만 1, FIFO 0 |
| FILLVAL | 없음 | cmd[8], 원본 byte 복제 | 없음 |
| trigger 설정 | 없음 | 없음 | cmd[11], HW type/mode/전용 request 번호; 필요한 실제 값 |
| LINKADDR | cmd[11], 암묵적 0 | cmd[9], 암묵적 0 | cmd[12], 암묵적 0 |

배열 구조와 무관한 길이 검사는 유지했다. 0 길이나 `U32_MAX` 초과 memory
요청을 거절하여 현재 byte residue 표현 범위를 벗어나지 않도록 한다.
구조 원복을 이유로 검증된 입력 검사까지 삭제하지 않았다.

### QBox 대응 변경의 재분류

삭제/복원한 부분은 MAXBURSTLEN 강제, 별도 command/allocator 구조,
width clamp, 불필요한 resource allocation guard와 불완전한 remove 후처리 loop다.
반면 source-trigger bit25 수정, slave API/OF 연결, PAUSE 완료 확인,
STOP 이후 descriptor 수명, IRQ status/descriptor의 동일 lock 처리는 유지했다.
8250의 `pause → residue → terminate_async`와 DMAengine의 synchronize 계약에
필요하며 단순히 QBox를 통과시키기 위한 성공 강제 처리가 아니다.
active hot-unbind, 영구 STOP 실패 및 실리콘 AXI timing 검증은 여전히 범위 밖이다.

upstream 대비 diff는 직전 `+441/-103`에서 `+384/-60`으로 줄었다.
앞의 최소화 단계별 수치는 각 당시의 기록이며 현재 원본 descriptor 구현과 구분한다.

### 원본 descriptor 구현 재검증

최종 빌드는 `./yocto_build.sh --keep-conf --bsp`로 수행했다.
`build/dma350/original-desc-bsp-build-2.log`에 5577 tasks 전체 성공
(5501 reused, 기존 taint 경고 5개)을 기록했다. 최종 source hash는
`original-desc-source-2.sha256`이며 실행 후 동일함을 확인했다.
`original-desc-checkpatch-2.log`의 strict checkpatch는 **0 errors,
0 warnings, 0 checks**다.

게스트 검증은 `build/dma350/original-desc-runtime-1/`에 보존했다.

| 검증 | 결과 |
|---|---|
| BSP 부팅, 8개 전용 채널 | PASS |
| memcpy/memset | 각각 5회 PASS, memory operation 10개 |
| SPI0/1 | 64-byte kmalloc 및 4099-byte vmalloc loopback PASS |
| SPI SG 경계 | 각 TX/RX에서 4096+3-byte 완료 명령 확인; 각 방향 누계 66544 byte |
| UART0↔1 | 양방향 17/128/512/4099-byte 비교 PASS; 각 TX DMA 4756 byte |
| UART RX | DMA 1591/144 byte 관측, 나머지는 PIO 혼용 |
| 실제 multi-entry SG | `d350_prep_slave_sg`의 `count=2` kprobe event 2개 관측 |
| I2C0–5, SPI2/3 PIO | 비교 PASS, 제외된 FIFO의 AP DMA 접근 없음 |
| 전체 AP trace | 334 operations, channel/request/FIFO 검증 PASS |
| 판정기/주소 map 테스트 | pytest 11/11 PASS, SG 단일 명령을 다중 SG 증거로 인정하지 않는 negative test 포함 |

SPI는 `max_sg_burst=1` 때문에 기존 client가 TX/RX 페이지 경계를 맞춰
단일 항목씩 제출한다. 따라서 SPI의 4096+3 trace만으로 provider 내부의
linked descriptor chain이 실행됐다고 주장하지 않는다. UART는 두 포트를
테스트 내내 열어 TX ring 위치를 유지하고 wrap을 유발했다. 아래 kprobe로
실제 `sg_len=2` 진입을 별도 확인했다. 이것과 UART 데이터 비교가
원본 descriptor chain의 런타임 증거다.

게스트에서 다음과 같이 전용 tracing instance를 설정한 뒤, 호스트에서
기존 `ssh_run.sh scripts/test/verify_qbox_dma350.sh`를 실행했다.
이름이 같은 기존 event/instance가 있으면 덮어쓰지 말고 다른 이름을 사용한다.

```sh
[ -d /sys/kernel/tracing/events ] || mount -t tracefs tracefs /sys/kernel/tracing
[ ! -e /sys/kernel/tracing/events/qbox_dma350/sg ] || exit 1
printf '%s\n' 'p:qbox_dma350/sg d350_prep_slave_sg count=$arg3:u32' >> /sys/kernel/tracing/kprobe_events
mkdir /sys/kernel/tracing/instances/qbox_dma350_sg
printf '%s\n' 'count > 1' > /sys/kernel/tracing/instances/qbox_dma350_sg/events/qbox_dma350/sg/filter
echo 1 > /sys/kernel/tracing/instances/qbox_dma350_sg/events/qbox_dma350/sg/enable
```

테스트 뒤 instance의 `trace`를 호스트 `sg-kprobe.trace`로 회수했다.
관측 내용은 `d350_prep_slave_sg+0x0/0x320 ... count=2` 두 줄이며,
특정 프로세스 ID나 함수 크기 값은 다음 빌드에서도 같다고 가정하지 않는다.
사용한 probe와 instance만 다음 명령으로 정리했다.

```sh
echo 0 > /sys/kernel/tracing/instances/qbox_dma350_sg/events/qbox_dma350/sg/enable
rmdir /sys/kernel/tracing/instances/qbox_dma350_sg
printf '%s\n' '-:qbox_dma350/sg' >> /sys/kernel/tracing/kprobe_events
```

`guest-validation.log`, `dma-trace.log`, `dma-validation.json`,
`sg-probe-setup.log`, `sg-kprobe.trace`, `guest-artifacts.tar.gz`가 증거다.
EEPROM 복구·원시 자료 회수·probe 정리 후 테스트 VM을 종료했다.
별도 전체 플랫폼 coverage audit는 G1 미실행 및 AP memory-map 증거 부재로
FAIL이며 DMA 전용 결과와 구분한다. SG 할당 실패/중간 오류/중간 STOP의
fault injection과 descriptor reuse 반복 시험은 소스 검토 범위이며 이번
정상 전송 시험만으로 해당 모든 경로를 검증했다고 주장하지 않는다.

## Upstream diff 추가 축소 (이전 단계)

전용 채널 동작을 바꾸지 않고 upstream과 비교할 때 불필요하게 보이던
코드 이동과 helper 분리를 줄였다. 기준은 앞서 명시한 동일 upstream blob이다.

| 지표 | 전용 구현 1차 | 추가 정리 후 |
|---|---|---|
| 추가/삭제 행 | +565/-177 | +441/-103 |
| 추가+삭제 합계 | 742 | 544 |
| 순증 | 388 | 338 |
| 파일 전체 | 1048행 | 998행 |

변경량 합계는 198행(약 27%) 줄었다. 기능 삭제 대신 다음을 정리했다.

- `d350_chan`의 기존 MMIO/IRQ/feature 멤버 배치와 channel-local `coherent`를
  복원했다. coherence 값은 probe에서 명시적으로 대입하므로 초기화 수정은 유지한다.
- 이를 위해 추가했던 controller backpointer와 global coherent helper를 제거했다.
- 한 곳에서만 호출하던 memcpy command builder와 terminated-descriptor 수집
  helper는 기존 호출 함수 안으로 합쳤다.
- MMIO programming 코드를 원래 `start_next` 부근으로 되돌리고 기존
  `dch->base` 표현을 유지했다. SG 재사용에 필요한 `d350_program_cmd()`는 남겼다.
- 사용하지 않는 `start_next`의 bool 반환을 upstream의 void로 되돌리고,
  `tx_status` 분기 형태·loop 변수·기존 주석 배치를 복원했다.
- DMA bus-width enum은 byte 수 자체이므로 switch 변환 대신 기존
  `is_power_of_2()`와 채널 폭 상한 검사를 쓴다. config와 command 작성 양쪽에서
  검사하여 0/비거듭제곱/지원 폭 초과를 계속 거절한다.
- unsigned 32-bit SG 길이의 `> U32_MAX` 비교, `nreq <= nchan <= 64` 검사로
  이미 배제되는 selector 초과 검사, 쓰지 않는 새 상수와 불필요한 중괄호를 제거했다.

Slave SG, OF lookup, 전용 request 매핑, PAUSE/RESUME 완료 확인,
STOP descriptor 수명, IRQ lock 및 오류 결과 처리는 유지했다.
정리 전 검증된 파일은 `build/dma350/minimize-before-driver.c`에 보존하여
단순 upstream 비교 외에도 전후 동작 경로를 확인했다.

### 추가 정리 후 재검증

새 파일로 `./yocto_build.sh --keep-conf --bsp`를 다시 실행했다.
5577개 task 중 5501개가 재사용됐으며 전체 성공했다.
`build/dma350/minimize-bsp-build.log`에 결과와 기존 forced-task taint
경고 5개를 보존했다. 이번 변경은 Linux와 DTS 정리이므로 QBox C++ unit
suite를 새로 실행한 것으로 계산하지 않는다.

같은 [재현 방법](#재현-방법)으로 새 BSP를 부팅한 뒤
`verify_qbox_dma350.sh`와 host trace validator를 실행했다.
최신 자료는 `build/dma350/minimize-runtime-1/`에 있다.

- BSP 부팅 및 8개 전용 채널 확인: PASS.
- memcpy/memset 각 5회: PASS, memory operation 10개.
- SPI0/1의 64/4099-byte DMA loopback: PASS, 각 TX/RX 누계 66544 byte.
- UART0↔1의 양방향 17/128/512/4099-byte 비교: PASS.
  각 TX DMA 4756 byte, RX DMA는 각각 261/278 byte이며 PIO 혼용이다.
- I2C0–5 EEPROM 128-byte PIO 및 SPI2/3 PIO loopback: PASS.
- AP operation 330개에서 전용 channel/request/FIFO 대응 확인: PASS.
  제외한 peripheral의 DMA FIFO 접근은 발견되지 않았다.
- pytest 판정기/주소 map 회귀 10개: PASS.
- `git diff --check`와 일반 checkpatch: PASS, errors/warnings 0.
  `--strict`는 alignment 등 check 9개가 남아 있으며
  `build/dma350/minimize-checkpatch-strict.log`에 기록했다.

`guest-validation.log`, `dma-trace.log`, `dma-validation.json`,
`guest-artifacts.tar.gz`가 실제 판정 및 원시 자료다.
`build/dma350/minimize-source.sha256`의 driver/DT/Lua 해시가 실행 후에도
같음을 확인했다. EEPROM 복구와 자료 회수 후 테스트 VM을 종료했다.
전체 플랫폼 coverage audit는 기존과 같이 G1 미실행 및 AP memory-map
증거 부재로 FAIL이며, DMA 전용 PASS와 구분한다.

## DTS 공백 복원

전용 채널 전환 중 불필요하게 제거된 I2C0–5와 SPI2/3의 자식 node 앞
빈 줄 8곳을 원래대로 복원했다. `apollo-qvp.dts`의 upstream 대비 diff는
이제 **23행 추가, 삭제 0행**이다. DMA controller node와 SPI0/1,
UART0/1의 `dmas`/`dma-names` 외에는 기존 내용을 변경하지 않는다.

## 전용 8채널 1차 검증 결과 (2026-09-10 KST)

현재 구성의 증거는 `build/dma350/dedicated-runtime-1/`이다.
`dma-validation.json`은 PASS이며 298개 AP operation 중 memory copy/fill은
10개다. validator는 데이터 성공 marker뿐 아니라 **FIFO 주소, request 번호,
물리 channel 번호의 일치**를 확인한다. I2C 및 SPI2/3, UART2/3 FIFO를 DMA가
접근하면 trigger 사용 여부와 무관하게 실패 처리한다.

| 검증 | 결과 |
|---|---|
| Provider compile | PASS, `dedicated-provider-compile.log` |
| Provider do_check | qbox-platform 58/58 PASS (5.51초), core 60/60 PASS (18.71초) |
| BSP 재빌드 | PASS, 5577 tasks 중 5497 reused; forced-task taint 경고 5개 |
| BSP 부팅 | PASS, `8 dedicated channels, 8 requests` 및 BSP ready 확인 |
| DMAengine memory | 미점유 `dma0chan4`에서 memcpy/memset 각 5회, 실패 0 |
| SPI0/1 DMA | 64/4099-byte loopback PASS, 각 포트 TX/RX 66544 byte trace |
| UART0↔1 DMA/PIO | 양방향 17/128/512/4099-byte 비교 PASS, 각 TX DMA 4756 byte |
| UART0/1 RX DMA | 각각 263/254 byte trace 확인; 나머지는 PIO 경로 |
| I2C0–5 PIO | EEPROM 128-byte write/read PASS, 전송 중 DMA IRQ 증가 0 |
| SPI2/3 PIO | 64/4099-byte loopback PASS, 해당 FIFO의 AP DMA trace 없음 |
| UART2/3 제외 | 게스트 DT dmas 부재 확인; 이번 실행에서 통신 부하를 가하지 않음 |
| 판정기/주소 map 회귀 | pytest 10/10 PASS; 잘못된 채널/PIO FIFO DMA 접근을 거절하는 negative test 포함 |
| Static | shellcheck, map validator, core boundary audit, diff-check PASS |

원시 자료는 `guest-validation.log`, `dma-trace.log`,
`guest-artifacts.tar.gz`에 보존했다. 빌드 로그는
`build/dma350/dedicated-bsp-build.log`, unit task 로그는
`dedicated-provider-do-check.log`이다. driver/DT/Lua의 source SHA-256을
`dedicated-source.sha256`에 저장하고 실행 후 동일함을 확인했다.
EEPROM 복구와 게스트 원시 자료 회수 후 테스트 VM을 종료했다.

검토 시 발견한 전체 범위 한계는 숨기지 않는다. `checkpatch --strict`는
오류 0, 스타일 경고 2, alignment 등 check 9개이며 `dedicated-checkpatch.log`에
남겼다. 전체 플랫폼 coverage audit는 G1 미실행과 AP memory-map 증거 부재로
FAIL이다. 이번 DMA 전용 PASS를 전체 플랫폼 qualification PASS로 확대하지 않는다.
새 구성에서는 동적 채널 공유를 검증할 필요가 없지만, 모든 endpoint의 동시
최대 부하, 오류 주입 및 영구 STOP 실패까지 검증한 것은 아니다.

## 초기 공유형 arm-dma350.c 변경 상세와 변경량의 이유 (이력)

이 절의 1–16항은 최초 구현에서 패치가 커진 이유에 대한 요청으로 작성한
**공유형 구현의 기록**이다. 이후 사용자가 전용 채널 구성을 지정하여
virtual/physical 분리 및 동적 scheduler를 제거했다. 현재 동작 설명으로
7–9항의 공유 구조나 36개 채널 수를 사용하면 안 된다.

### 비교 기준 및 결론

2026-09-10에 Linux HEAD `6ff44c9184f57e8faf89b7aca1f3535a3e8e4313`의
`drivers/dma/arm-dma350.c`와 작업 트리를 비교했다. 파일은 660행에서
1194행으로 늘었다. `git diff --numstat` 기준 추가 743행, 삭제 209행,
순증 534행이다. 아래 설명은 이 비교에 대한 것이며, 최신 upstream 전체에
대한 평가나 각 변경이 모두 새 버그 수정이라는 뜻은 아니다.
아래 명령은 실행 시점의 작업 트리를 비교한다. 이후 정리된 현재 파일에서
초기 공유형의 1194행 diff를 그대로 재생하는 명령은 아니다.

```bash
git -C hsoc-stack/components/primary_compute/linux diff \
  6ff44c9184f57e8faf89b7aca1f3535a3e8e4313 -- drivers/dma/arm-dma350.c
git -C hsoc-stack/components/primary_compute/linux diff --numstat \
  6ff44c9184f57e8faf89b7aca1f3535a3e8e4313 -- drivers/dma/arm-dma350.c
```

변경량의 가장 큰 원인은 **memory DMA 전용 드라이버를 peripheral DMA
provider로 확장하면서, 고정 물리 채널 구조를 요청별 virtual channel
구조로 전환한 것**이다. 기존 드라이버에는 memcpy/memset, pause/resume,
residue, IRQ, virt-dma queue가 이미 있었다. 그러나 `DMA_SLAVE`,
`device_config`, `device_prep_slave_sg`, OF DMA controller 등록은 없었다.
DT에 `dmas`만 추가하거나 SystemC FIFO 신호만 연결해서는 이 빈 API를
채울 수 없다.

또한 기존 레지스터 programming 본체가 `d350_start_next()`에서
`d350_program_cmd()`로 이동했다. 따라서 diff의 추가/삭제 행수를 모두
새 알고리즘의 양으로 해석하면 과장된다. memcpy/memset의 주소 상위 word,
전송 폭 선택, FILL byte 복제 및 기본 residue 읽기도 기존 기능을 유지했다.

변경은 다음 네 종류로 구분한다.

| 분류 | 내용 | 필수성 |
|---|---|---|
| Peripheral 기능 추가 | slave config, FIFO 고정 주소, HW trigger, SG, OF xlate | 기존 I2C/SPI/UART DMA client 연결에 필요 |
| 채널 구조 변경 | request virtual channel과 물리 채널 분리, pending queue | 28개 요청을 8개 물리 채널로 서비스하기 위해 선택한 정책 |
| 정확성/수명 보강 | source trigger bit, pause 확인, STOP 완료, IRQ 소유권 | 비동기 DMA의 register/API 계약을 지키기 위한 변경 |
| 구현 범위 선택/정리 | software SG, single-beat slave burst, helper 추출 | 전체 TRM 요구가 아닌 현재 구현 전략 |

### 1. Register 정의와 헤더

대상: 파일 상단 `CH_CTRL_*`, `CH_TRIGIN_*`, `CH_STAT_INTR_STOPPED`,
`CH_INTREN_STOPPED`, `TRANSCFG_*`, `D350_STATE_POLL_US`.

- `CH_CTRL_USESRCTRIGIN`을 bit 26에서 **bit 25**로 수정했다.
  bit 26은 destination trigger다. RX에서 source FIFO 요청을 사용하려면
  두 비트를 구분해야 한다. 기존 memory copy/fill은 외부 trigger를
  쓰지 않아 이 잘못된 정의가 활성 경로에 나타나지 않았다.
  근거: [CH_CTRL](0118-CH_CTRL.md).
- trigger selector `[7:0]`, type `[9:8]`, mode `[11:10]`, block size
  `[23:16]`를 정의했다. 단순 memcpy에는 필요 없던 주변장치 요청 설정이다.
- STOPPED interrupt bit 3을 추가했다. 동기 poll 안에서 STOP이 끝나지
  않아도 IRQ 경로로 채널 정리를 완료하기 위해서다.
- `TRANSCFG_DEVICE`의 MAXBURSTLEN을 0으로 바꾸고 OR 식을 괄호로 묶었다.
  NC/WB의 burst 설정은 유지했다. FIFO 쪽 single-beat 제한과 memory 쪽
  속성 설정은 별개다.
- `of_dma.h`, `scatterlist.h`, `iopoll.h`, `delay.h`, `log2.h`는 각각
  OF 등록, mapped SG, 상태 poll, 재시도 sleep, 폭 계산 때문에 추가됐다.
  `D350_STATE_POLL_US=1000`은 poll 1회의 상한이지 실리콘 DMA 완료 시간이나
  전체 synchronize 상한이 아니다.

### 2. Descriptor를 단일 command에서 command 배열로 변경

대상: `struct d350_cmd`, `struct d350_desc`, `d350_alloc_desc()`.

기존 descriptor는 `command[16]`, xsize/xsizehi, tsz 한 벌만 보관했다.
이제 `cmds[]`에 각 mapped SG element의 command, byte 수, 전송 폭을
보관한다. descriptor에는 `total_bytes`, `num_cmds`, `cmd_idx`를 둔다.
이는 서로 떨어진 DMA 주소들을 하나의 client transaction/cookie로
완료시키기 위한 변경이다. SG 한 항목만 사용하는 I2C도 같은 경로를 쓴다.

`struct_size()`와 `GFP_NOWAIT`로 필요한 크기만 할당한다. 항목 수는
1–65535, 총 byte 수는 `U32_MAX` 이내로 제한한다. 실패 시 NULL을 반환하고
부분 준비 descriptor를 해제한다. 이 상한은 현재 자료형/구현의 제한이며
DMA-350이 처리할 수 있는 모든 전송 형태의 상한을 뜻하지 않는다.

### 3. memcpy/memset 유지 및 공통화

대상: `d350_build_memcpy_cmd()`, `d350_prep_memcpy()`,
`d350_prep_memset()`, `d350_memory_transcfg()`.

기존 memory 기능은 command 배열의 첫 항목으로 변환했다. 0-byte 및
`U32_MAX` 초과 요청은 거절한다. 폭은 길이와 주소 정렬 및 모든 물리 채널이
공통 지원하는 최대 transfer width 상한을 이용해 선택한다. 주소 상위 32-bit programming과
memset의 `(u8)value * 0x01010101`은 새 기능이 아니라 기존 동작이다.

coherency 판단을 `dmac->coherent`에 저장하고 모든 command builder가
이를 사용한다. 기준 코드의 `dch->coherent`는 command 작성에 사용되지만
probe에서 대입되지 않았다. 이번 변경은 device DMA attribute가 memory
transaction 설정에도 반영되도록 한다. QVP data 비교는 통과했지만 실제
비일관성 cache/DMA 환경에서 WB/NC 속성의 정확성을 검증한 것은 아니다.

기존 command의 마지막 `LINK_LINKADDR`와 0 주소 항목은 제거했다.
현재 경로는 레지스터로 명령을 직접 시작하며 후속 SG도 CPU가 작성한다.
하드웨어가 메모리에서 command chain을 fetch하도록 구현한 것이 아니다.

### 4. Slave configuration과 폭/정렬 검사

대상: `d350_buswidth_bytes()`, `d350_config()`.

`dmaengine_slave_config()`를 받아 FIFO 주소, 방향, 폭, flow-control
정보를 virtual channel의 `cfg`에 저장한다. MEM_TO_DEV 또는 DEV_TO_MEM만
받으며 1/2/4/8/16-byte 폭 중 controller 한계를 넘지 않는 값만 허용한다.
`d350_build_slave_cmd()`는 mapped memory 주소와 길이의 폭 정렬을 검사한다.

I2C는 TX 2-byte DATA_CMD, RX 1-byte로 설정한다. UART는 양방향 1-byte다.
SPI는 기존 client가 frame 폭에 맞춘 설정을 전달한다. 주변장치 주소를
드라이버 안에 hardcode하지 않으므로 DMA core는 I2C/SPI/UART 종류를 모른다.
검사 범위는 방향/폭/memory 정렬 중심이며 모든 slave configuration 조합의
검증을 의미하지 않는다. 일반 client의 임의 FIFO 주소/폭 조합은 별도 검증이 필요하다.

### 5. Peripheral command 작성

대상: `d350_build_slave_cmd()`.

| 설정 | MEM_TO_DEV (TX) | DEV_TO_MEM (RX) |
|---|---|---|
| source | mapped memory | cfg.src_addr FIFO |
| destination | cfg.dst_addr FIFO | mapped memory |
| 주소 증가 | source만 1 | destination만 1 |
| 외부 요청 | destination trigger, bit 26 | source trigger, bit 25 |
| FIFO transaction | Device | Device |
| memory transaction | coherency에 따른 WB/NC | coherency에 따른 WB/NC |

`CH_XSIZE/HI`는 byte 수가 아니라 `len >> tsz` 전송 개수로 작성한다.
`XTYPE=CONTINUE`, `DONETYPE=CMD`로 한 명령 완료 IRQ를 받는다.
trigger `TYPE=2`는 **HW trigger 선택**이며 signal의 SINGLE/BLOCK type과는
다른 필드다. `SEL`은 virtual channel에 고정된 request 번호다.
`BLKSIZE=0`은 기본 한 transfer를 뜻한다.

`cfg.device_fc=false`이면 MODE=2(DMAC flow), true이면 MODE=3(peripheral
flow)를 사용한다. 현재 DWC client 검증은 길이를 DMAC가 정하는 MODE=2다.
MODE=3 설정 코드는 있지만 Linux client + LAST 종료 시험은 수행하지 않았다.
근거: [CH_SRCTRIGINCFG](0134-CH_SRCTRIGINCFG.md),
[CH_DESTRIGINCFG](0135-CH_DESTRIGINCFG.md).

### 6. Slave SG API와 software chaining

대상: `d350_prep_slave_sg()`, `d350_program_cmd()`, `d350_irq()`.

`sg_dma_address()`와 `sg_dma_len()`으로 client가 이미 DMA mapping한 목록을
읽는다. DMA provider가 client buffer를 직접 map/unmap하거나 데이터 복사를
대신하지 않는다. 각 SG entry에 명령 하나를 만들고, command DONE IRQ에서
`cmd_idx`를 증가시켜 다음 명령을 작성한다. 마지막 명령에서만
`vchan_cookie_complete()`로 client 완료를 전달한다.

기존 SPI DMA는 `prep_slave_sg()`를 직접 호출한다. I2C와 UART RX의
`prep_slave_single()`도 DMAengine helper를 통해 이 callback으로 들어온다.
UART TX의 ring-buffer SG도 같은 방식이다.

이 구현은 hardware command-link가 없는 모델에서도 mapped SG를 지원하는
선택이다. 매 SG 경계에서 IRQ/CPU 개입이 필요하므로 hardware linked-list와
성능 특성이 같지 않다. cyclic DMA, 무한 streaming, descriptor prefetch는
추가하지 않았다. 4099-byte 전송 성공만으로 모든 multi-entry SG 경계와
정렬 조합이 검증됐다고 판단하지 않는다.

### 7. 물리 채널과 virtual channel 분리

대상: `struct d350_phy`, `struct d350_chan`, `struct d350`, `d350_probe()`.

기존에는 Linux 채널 하나가 MMIO base와 IRQ 하나를 영구 소유했다.
그러나 현재 보드는 TX/RX 합계 28개 요청과 물리 채널 8개를 가진다.
I2C/SPI driver는 probe 때 DMA channel을 확보하고 보관하므로 요청 시점에
물리 채널까지 고정 배정하면 일부 포트가 모든 물리 자원을 점유할 수 있다.

`d350_phy`는 MMIO/IRQ/지원 기능과 현재 `serving` owner를 가진다.
`d350_chan`은 client queue/cookie/config/request를 보유하고 실행 때만
`phy`를 얻는다. request 0–27용 virtual channel과 request=-1인 8개
추가 slot을 생성한다. 총 36개는 동시에 실행 가능한 엔진 개수가 아니다.

추가 8개 slot은 memory 요청을 위한 여유지만 memory 전용 격리 pool은
아니다. 한 `dma_device`의 capability를 공유하므로 generic memory 요청이
아직 점유되지 않은 request slot을 얻을 수도 있다. 실제 dmatest는
`dma0chan20`을 잠시 사용한 뒤 해제했다. 엄격한 memory/slave allocation
격리 및 다른 probe 순서는 별도 보강/검증 대상이다.

### 8. 물리 채널 배정과 대기열

대상: `d350_get_phy()`, `d350_alloc_phy_and_start()`,
`d350_release_phy()`, `d350_issue_pending()`, `d350_start_next()`.

issue_pending에서 실행할 descriptor가 있으면 빈 물리 채널을 찾는다.
없으면 virtual channel을 `WAITING`으로 표시하고 `pending`에 한 번만
추가한다. 물리 채널을 해제할 때 대기열을 확인하고 다음 요청을 시작한다.
`pending_node`의 중복 삽입과 이미 취소된 대기 요청의 시작을 방지한다.

대기열은 FIFO지만 현재 owner의 다음 descriptor를 먼저 실행할 수 있으므로
전체 client에 대한 엄격한 round-robin/공정성 보장은 아니다. 이는 SystemC
모델이 활성 물리 채널의 burst를 번갈아 처리하는 정책과도 별개다.
RX가 요청을 기다리는 동안에는 물리 채널을 유지하며 선점하지 않는다.
8개 초과 장기 동시 전송/기아 방지는 이번 순차 포트 시험 범위 밖이다.

기존 레지스터 작성 루프는 `d350_program_cmd()`로 분리했다.
`d350_start_next()`는 먼저 `vchan_next_desc()`의 NULL 여부를 검사하고
그 뒤 descriptor를 변환한다. 새로운 명령 시작 때 DONE/ERR interrupt를
재설정하여 앞선 STOP 경로의 interrupt 설정이 이어지지 않게 한다.

### 9. Locking과 IRQ owner 일관성

대상: issue/allocate/release/terminate/synchronize/IRQ 경로.

전체 물리 채널의 owner와 pending queue는 `dmac->lock`으로 보호하고,
개별 descriptor와 cookie/state는 `dch->vc.lock`으로 보호한다.
둘 다 필요한 경로는 항상 `dmac->lock → vc.lock` 순서로 잡는다.
IRQ는 controller lock 아래서 상태를 읽고 `phy->serving`을 찾는다.
이 순서는 상태 읽기와 채널 재배정 사이에 owner가 바뀌는 경쟁을 막기 위한 것이다.

pause/resume/tx_status는 해당 vc.lock만 잡고 controller lock을 나중에
요청하지 않는다. release는 controller lock 아래 다음 대기 vc.lock을 잡는다.
DMA 완료 callback은 기존 virt-dma tasklet 경로를 사용한다.
새 callback framework나 SystemC 전용 Linux lock은 추가하지 않았다.

이 구조에 대한 코드 검토와 정상 SMP 게스트 실행은 수행했지만,
lockdep 기반 모든 interleaving/장시간 contention 증명은 아니다.

### 10. PAUSE/RESUME 완료 확인

대상: `d350_pause()`, `d350_resume()`.

기준 코드는 명령을 쓰자마자 software status를 PAUSED 또는 IN_PROGRESS로
바꿨다. 이제 PAUSE는 `PAUSED && RESUMEWAIT`, RESUME은 두 상태 해제를
atomic poll로 확인하고 성공한 경우만 software 상태를 갱신한다.
poll은 1us 간격, 회당 최대 1000us이며 실패를 caller에 반환한다.

이 변경은 단순 지연 추가가 아니다. `serial8250_rx_dma_flush()`는
pause 직후 `__dma_rx_complete()`에서 residue를 읽어 `rx_size - residue`
byte를 TTY로 넘긴다. 비동기 모델에서 PAUSE를 쓴 것과 실제 정지는 다르므로
둘을 구분해야 한다. 정상 UART flush는 검증했지만 pause/resume timeout
fault injection과 resume 단독 경로의 모든 조건은 검증하지 않았다.

### 11. Residue를 descriptor 전체의 남은 byte로 확장

대상: `d350_get_residue()`, `d350_tx_status()`.

기존 HI→LO→HI 읽기와 최대 3회 재시도는 유지했다. 현재 command의
destination 잔여 transfer 수에 `1 << tsz`를 곱하고, 아직 시작하지 않은
후속 SG command의 byte 수를 더한다. 대기 descriptor는 `total_bytes`를
반환하고 활성 descriptor/phy가 없으면 저장된 residue를 사용한다.

이 값은 UART RX partial completion과 error callback에 필요하다.
`DMA_RESIDUE_GRANULARITY_BURST` 선언은 기존부터 있었으며 이번에 처음
추가한 것이 아니다. byte 단위 반환과 모든 시점의 원자적 snapshot 보장은
다르므로, 안정된 UART 수신 byte 산정은 위 PAUSE 확인과 함께 해석해야 한다.

### 12. STOP과 descriptor 수명 분리

대상: `d350_stop_phy()`, `d350_collect_terminated()`,
`d350_finish_terminate()`, `d350_terminate_all()`, `d350_synchronize()`.

기준 코드는 STOP write 후 descriptor를 종료 목록으로 옮겼으며,
synchronize는 virt-dma callback 정리만 기다렸다. 비동기 worker는 STOP을
다음 실행 지점에서 처리하므로 즉시 buffer/채널을 재사용하면 아직 수행 중인
전송과 겹칠 수 있다.

1. pending 요청을 제거하고 descriptor를 종료 목록으로 수집한다.
2. STOPPED/DONE/ERR interrupt를 허용하고 STOP을 쓴다.
3. `CH_CMD.ENABLE`이 해제될 때까지 atomic poll한다. 소프트웨어 flag만으로
   정지를 판정하지 않는다.
4. poll 안에 끝나면 pending interrupt를 clear하고 active owner를 정리한다.
5. 끝나지 않으면 `stopping=true`를 유지하고 descriptor/phy 소유권을 보존한다.
   이후 IRQ에서 ENABLE 해제를 확인해 종료를 마무리한다.
6. `d350_synchronize()`는 STOP이 끝난 뒤 `vchan_synchronize()`를 호출한다.
   caller는 이 뒤에 buffer를 해제할 수 있다.

`terminate_async()`가 atomic context에서 호출될 수 있고, buffer 해제 전에
synchronize가 필요하다는 계약은 로컬 `include/linux/dmaengine.h`에 있다.
UART flush의 async 취소와 I2C/SPI 오류 정리의 sync 취소 모두 이 경로에 도달한다.
지연 STOP 중 새로 queue된 요청은 정지가 확인된 뒤에만 시작한다.
단, DMAengine 계약상 `terminate_async()`와 `synchronize()` 사이에
`dma_async_issue_pending()`을 호출한 경우 synchronize 동작은 정의되지 않는다.
드라이버의 재시작 처리와 client가 따라야 하는 API 호출 순서를 혼동하면 안 된다.

중요한 한계: synchronize의 바깥 재시도에는 **전체 timeout이 없다**.
매 회 poll 뒤 필요하면 `usleep_range(100, 200)`하지만, 하드웨어가 영구적으로
정지하지 않으면 계속 기다린다. 조기 buffer 해제는 피하되 영구 고장 복구를
완성한 것은 아니다. 현재 정상 정지와 UART partial RX는 검증했지만 강제
STOP 지연/영구 정지 실패는 시험하지 않았다.

### 13. IRQ 완료/오류/정지 처리

대상: `d350_irq()`.

- IRQ data를 virtual channel에서 물리 채널로 변경했다. 물리 IRQ가 발생하면
  현재 owner를 찾고, owner/descriptor가 없으면 상태만 clear한다.
  기존처럼 handler 입구에서 active descriptor를 무조건 참조하지 않는다.
- CH_STATUS 전체가 0인지 보는 대신 STOPPED/DONE/ERR interrupt source만
  검사한다. 상태 bit만으로 client 완료를 만들지 않는다.
- stopping 경로는 descriptor 완료 callback 대신 STOP 완료를 처리한다.
- DONE은 SG 다음 명령 또는 최종 cookie 완료로 나눈다. 완료 descriptor를
  active pointer에서 분리한 뒤 다음 작업 또는 물리 채널 반환을 진행한다.
- ERR은 read/write/aborted 결과와 잔여 byte를 저장하고 cookie를 완료한 뒤
  다음 queue 처리 또는 채널 반환을 진행한다. **ERRINFO/residue를 W1C 전에
  읽는 순서와 read/write error 분류 자체는 기준 코드에도 있었다.**
  이번 변경은 이를 새 ownership/SG 경로에서 유지하고 수명/lock을 보강한 것이다.

정상 IRQ, 연속 transfer와 UART STOP trace는 확인했다. Linux callback까지
연결한 AXI read/write error 주입 및 stale IRQ 경쟁 재현은 별도 미검증이다.
SystemC 단위시험의 error 검증을 Linux IRQ handler fault 검증으로 대체하지 않는다.

### 14. Probe, OF provider, resource 해제

대상: `d350_probe()`, `d350_of_xlate()`, `d350_alloc_chan_resources()`,
`d350_free_chan_resources()`, `d350_remove()`.

- `dma_set_mask_and_coherent()` 실패를 확인한다. request 수가 8-bit selector의
  범위를 넘는 구성은 거절한다. controller/물리/virtual 배열을 나누어 할당한다.
- `DMA_MEM_TO_DEV`, `DMA_DEV_TO_MEM`, `DMA_SLAVE` 및 slave callbacks를
  등록한다. 물리 채널의 trigger 기능을 읽고 사용 가능한 채널이 있는지 확인한다.
  전체 채널이 WRAP을 지원할 때만 DMA_MEMSET을 노출하는 방침은 유지한다.
- 과거 HAS_CMDLINK가 없으면 채널을 건너뛰던 조건을 제거했다. 현재 명령은
  CPU가 직접 register에 쓰므로 hardware command fetch가 필수 기능은 아니다.
- IRQ는 client 채널 할당 때 `request_irq/free_irq`하는 대신 probe 때
  물리 채널별 `devm_request_irq`로 확보한다. 현재 AP는 채널별 전용 IRQ이며
  새 경로는 `IRQF_SHARED`를 사용하지 않는다.
- `of_dma_controller_register()`와 `d350_of_xlate()`를 추가한다.
  `#dma-cells=1`의 값은 물리 채널 번호가 아닌 request 번호다. 잘못된
  cell 개수/범위는 NULL로 거절하고 `dma_get_slave_channel()`로 확보한다.
- allocation은 지연 STOP 중인 채널을 `-EBUSY`로 거절한다. free는
  terminate → synchronize → virt-dma resource 해제 순서다.
- OF 등록 실패 때 DMA device 등록을 되돌린다. remove는 OF provider 제거,
  DMA device 해제, IRQ mask/STOP, tasklet 종료를 수행한다. 이 remove 경로는
  STOP 완료를 별도로 poll하지 않으므로 실행 중 hot-unbind 안전성 검증을
  완료했다고 주장하지 않는다. 실제 사용은 built-in controller다.

### 15. Single-beat 정책과 SystemC 특수 처리의 경계

`dma.min_burst=max_burst=1`은 현재 DWC SINGLE request 모델과 맞춘 정책이다.
기존 `dw_spi_dma_maxburst_init()`는 DMA capability로 RX threshold를 계산한다.
max_burst=1이면 RX threshold가 0이 되어 마지막 한 FIFO element도 요청한다.
큰 burst를 광고하면서 model이 SINGLE만 요청하면 짧은 tail이 threshold
아래에 남아 완료를 기다릴 수 있다. 따라서 SPI driver를 우회 수정하지 않고
provider capability와 모델이 실제 지원하는 범위를 일치시켰다.

이는 성능 최적화가 아니며 모든 DMA-350 하드웨어의 필수 제한도 아니다.
BLOCK/LAST와 FIFO tail을 함께 확장하고 검증하면 burst 정책도 확대할 수 있다.
현재 cfg의 maxburst 값을 임의 크기의 block 요청으로 변환하지 않는다.

드라이버에는 QBox monitor 호출, host 주소 직접 접근, 강제 callback 성공,
CPU memcpy를 DMA로 가장하는 경로를 추가하지 않았다. TRM MMIO와 DMAengine
계약을 통해 동작한다. 다만 software chaining, single-beat, polling 정책은
현재 QVP에서 검증한 구현 선택이므로 실리콘 성능/범용성까지 보장하지 않는다.

### 16. 변경별 검증 증거와 남은 시험

아래는 기존 `runtime-3` 자료를 다시 확인한 분류다. 이 문서 보강 때 빌드나
게스트 시험을 새로 실행하지 않았다.

| 변경 묶음 | 확보한 증거 | 확보하지 않은 증거 |
|---|---|---|
| memcpy/memset 재구성 | dmatest 각 5회, copy/fill trace 10건 | 4 GiB 근처 크기, 모든 정렬/폭 |
| OF/request 할당 | 14개 포트 TX/RX 정상 사용, 8 physical/28 request probe | 잘못된 DT, 다른 probe 순서, memory/slave allocation 격리 |
| FIFO/trigger/slave SG | I2C 6개, SPI 4개, UART 4개 정확한 FIFO/request TX/RX trace | 모든 multi-entry SG 분할, Linux peripheral-flow/LAST |
| PAUSE/residue/정상 STOP | UART 4방향 short/long 비교, partial RX DMA trace | PAUSE 실패, 장기 RESUME, 강제 STOP timeout |
| scheduler/lock/IRQ | 정상 게스트 다중 CPU 실행, 연속 transfer, 코드 검토 | 8개 초과 동시 장기 workload, 공정성, lockdep/fault stress |
| error/synchronize/resource | 코드 검토 및 정상 종료 경로 | AXI 오류 callback, 영구 STOP 실패, active hot-unbind |
| feature/mask/coherency | 현재 homogeneous AP 구성의 build/probe/data PASS | heterogeneous 물리 채널, DMA mask 실패, 실제 cache snoop |

추가로 주의할 일반화 범위가 있다. 초기 물리 할당은 trigger 지원을 검사하지만
대기열 handoff는 같은 capability를 다시 검사하지 않는다. 현재 AP의 8개
채널은 동일 구성이다. 서로 다른 기능의 물리 채널 혼합 구성까지 지원한다고
해석하면 안 된다. 14개 포트 순차 시험과 이기종/과부하 시험은 다르다.

코드 근거: [DMA provider](../../hsoc-stack/components/primary_compute/linux/drivers/dma/arm-dma350.c),
[SPI DMA client](../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw-dma.c),
[8250 DMA client](../../hsoc-stack/components/primary_compute/linux/drivers/tty/serial/8250/8250_dma.c),
[I2C client](../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-master.c),
[DMAengine API 계약](../../hsoc-stack/components/primary_compute/linux/include/linux/dmaengine.h).

## 재현 방법

전용 테스트 게스트를 사용한다. EEPROM 앞 128 byte는 백업 후 복구하지만
테스트 도중 강제 종료/VM 손실은 복구를 보장하지 않는다. UART와 SPI loopback
포트는 이 테스트가 단독 사용해야 한다.

```bash
./yocto_build.sh --keep-conf --bsp
QBOX_RDASPEN_DMA350_TRACE=true \
QBOX_RDASPEN_DMA350_TRACE_LIMIT=20000 \
QBOX_RDASPEN_DMA350_TRACE_FILTER=operation \
./run_qbox_yocto.sh --bsp --headless --multi-session --copy-disks \
  --no-persistent-rse-state --keep-running-after-pass --timeout 600 \
  --out-dir build/dma350/runtime
```

다른 터미널에서 BSP ready 직후, 위 runner의 timeout 전에 수행한다.
`--keep-running-after-pass`는 timeout 후에도 VM을 남길 수 있지만, 종료된
runner는 stdout/stderr를 더 이상 수집하지 않는다. VM 생존과 trace 수집기
생존은 다르다.

```bash
stat -c %s build/dma350/runtime/qbox-platform.log > build/dma350/runtime/offset
./scripts/run/ssh_run.sh scripts/test/verify_qbox_dma350.sh \
  > build/dma350/runtime/guest-validation.log 2>&1
tail -c +$(( $(< build/dma350/runtime/offset) + 1 )) \
  build/dma350/runtime/qbox-platform.log > build/dma350/runtime/dma-trace.log
python3 scripts/test/validate_qbox_dma350.py \
  --guest-log build/dma350/runtime/guest-validation.log \
  --qbox-log build/dma350/runtime/dma-trace.log \
  --output build/dma350/runtime/dma-validation.json
python3 -m pytest -q tests/test_qbox_dma350_validation.py tests/test_dwc_ap_map_audit.py
```

## 초기 공유형 검증 결과 (2026-09-10 KST, 이력)

최종 증거는 `build/dma350/runtime-3/`에 보존했다.
`dma-validation.json`은 PASS, AP trace 912건 중 memory copy/fill 10건이며
모든 14개 포트의 올바른 FIFO 주소 및 request 번호에서 TX/RX를 확인했다.
`guest-validation.log`, `dma-trace.log`, `guest-artifacts.tar.gz`에 각각
판정, host 전송, 게스트 원시 데이터/커널 로그를 남겼다. byte 집계에는
EEPROM 백업/복구 및 SPI 모듈의 반복 전송도 포함되므로 payload 길이와 다르다.

| 검증 | 결과 |
|---|---|
| BSP `./yocto_build.sh --keep-conf --bsp` | PASS, 5577 tasks; forced-task taint 경고 5개 |
| recipe `do_check`, qbox-platform | 58/58 PASS, 6.56초 |
| recipe `do_check`, 선택된 qbox core | 60/60 PASS, 18.69초; 기존 slow/flaky 제외 정책 유지 |
| DMA 엔진 + I2C/SPI/UART 결합 + UART 집중 CTest | 5/5 PASS, 0.05초 |
| Python 증거 판정기/주소 map 회귀 | 7/7 PASS |
| memory DMA | memcpy 5회 + memset 5회, 실패 0; IRQ 0→5→10 |
| I2C0–5 EEPROM | 각 128-byte write/read 비교 PASS; 18-byte TX page command 및 RX DMA 확인 |
| SPI0–3 loopback | 각 64/4099-byte 비교 PASS; 각 TX/RX DMA 누계 66544 byte |
| UART0↔1, UART2↔3 | 양방향 17/128/512/4099-byte 비교 PASS |
| RSE/SI/AP BSP 부팅 | PASS; 기존 RSE DMA 사용 부팅 경로 유지 |

UART 각 포트의 TX DMA는 4756 byte다. RX DMA 누계는 포트 순서대로
282/219/451/271 byte이며 나머지는 timeout/PIO 경로가 처리했다.
따라서 이 결과는 양방향 DMA 사용과 전체 데이터 정합성의 증거이지,
UART RX 전량 DMA 또는 실리콘 throughput의 증거는 아니다.
SPI timeout margin은 테스트 동안 30000ms로 늘리고 종료 시 복구했다.

`build/dma350/provider-do-check.log`, `unit-5.log`, `bsp-build.log`에
빌드/단위시험 로그를 보존했다. static map 및 QBox core boundary audit,
shellcheck, 변경 저장소의 `git diff --check`도 통과했다.
최초 결합 시험에서 발견한 socket 미연결, 다중 signal writer,
SystemC 종료/재시작 문제는 수정 후 위 CTest로 재검증했다.
runtime-1은 게스트 데이터 시험은 성공했지만 수집기가 먼저 종료되어
AP trace가 누락되었으므로 최종 DMA 판정에는 사용하지 않았다.
runtime-2는 부팅 확인용이며, 최종 증거는 수집기 생존 중 시험한 runtime-3이다.

전체 플랫폼 coverage audit도 별도로 실행했다.
`runtime-3/full-coverage-audit.json`은 `ap_9_1_1_memory_map: not_available`,
`gate:G1: not_run` 때문에 FAIL이다. 이번 BSP launcher 실행은 해당 전체
플랫폼 증거를 수집하지 않았으며, DMA 전용 PASS를 전체 플랫폼 qualification
PASS로 확대하지 않는다. 테스트 VM은 원시 자료를 회수한 뒤 종료했다.

## I2S 추가에 따른 인스턴스 분리

[TRM configurable options](0012-Configurable-options.md)의 `NUM_CHANNELS` 범위는
1–8이다. I2S 초기 통합에서 10채널로 늘린 구성은 허용 범위를 벗어나므로 제거했다.
모델은 최대 8채널을 강제하고 9채널 거부 테스트를 포함한다.

AP의 두 인스턴스는 QBox 이름과 DT label 모두 `dma350_0`, `dma350_1`이다.

| 인스턴스 | MMIO | SPI / INTID | 구성 |
| --- | --- | --- | --- |
| dma350_0 | 0x31000000 | 279 / 311 | 8채널, 기존 SPI0/1 및 UART0/1 전용 배선 유지 |
| dma350_1 | 0x31010000 | 358 / 390 | 8채널, 0/1=I2S0 TX/RX, 2/3=I2S1 TX/RX, 4–7 미연결 |

각 controller는 독립적인 shared non-secure IRQ를 사용한다.
이전 로그의 `ap_dma350`은 현재 `dma350_0`에 해당하며, 기존 로그를 읽는 검증기는
두 이름을 지원한다. 현재 I2S 구성과 양방향 검증은
[DW_apb_i2s 문서](../dwc/dw-apb-i2s.md)에 기록한다.

## 구현 한계

2D/template, 하드웨어 command-link fetch, autorestart, AXI-Stream,
software/internal/output trigger, security attribution, 실시간 AXI arbitration과
cache coherency 타이밍은 구현/검증 범위 밖이다. 기본 1D WRAP 지원은 모든
2D WRAP 또는 template 조합 지원을 의미하지 않는다. AP DMA 두 node의
`dma-coherent;`는 hardware coherency 통합 근거가 없어 제거했고, 해당 binding
허용 변경도 원복했다. 현재는 non-coherent DMA 구성이며, QVP의 TLM memory
접근과 데이터 비교 결과는 실제 cache snoop 모델의 증거가 아니다.
UART sub-threshold RX tail은 의도적으로 PIO다.
강제 STOP timeout의 Linux 지연 정리 경로는 코드 리뷰 대상이지만 게스트
fault injection으로 재현하지 않았다. FVP와의 동등성 시험은 수행하지 않았다.

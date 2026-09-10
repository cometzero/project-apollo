# Apollo QVP DW_apb_i2s 구현과 검증

## 구성과 소유권

참조 자료는 로컬 `DesignWare_DW_apb_i2s_databook.md`(DW_apb_i2s 1.11a,
2018-07, `/build/arm/trm/`)이다. AP expansion 영역과 기존 Apollo QVP의
MMIO/IRQ/pinmux 배치를 대조해 다음 두 인스턴스를 할당했다.

| 인스턴스 | MMIO / 크기 | GIC SPI / INTID | PERI0 bank3 / function | 역할 | DMA-350 |
| --- | --- | --- | --- | --- | --- |
| `ap_dw_i2s_0` | `0x30200000` / 64 KiB | 356 / 388 | pin0 SCLK, pin1 WS, pin2 SDOUT, pin3 SDIN / 2 | master, TX+RX | `dma350_1` TX 0 / RX 1 |
| `ap_dw_i2s_1` | `0x30210000` / 64 KiB | 357 / 389 | pin4 SCLK, pin5 WS, pin6 SDOUT, pin7 SDIN / 2 | slave, TX+RX | `dma350_1` TX 2 / RX 3 |

[DMA-350 configurable options](../dma-350/0012-Configurable-options.md)는
`NUM_CHANNELS`를 **1–8**로 정의한다. 초기 10채널 구성은 잘못됐으며 제거했다.
모델도 9개 이상을 거부하고 이를 unit test로 검사한다.

| DMA 인스턴스 / DT label | MMIO / 크기 | SPI / INTID | 채널 수 | 배선 |
| --- | --- | --- | --- | --- |
| `dma350_0` | `0x31000000` / 64 KiB | 279 / 311 | 8 | SPI0/1 TX/RX 0–3, UART0/1 TX/RX 4–7 |
| `dma350_1` | `0x31010000` / 64 KiB | 358 / 390 | 8 | I2S0 TX/RX 0/1, I2S1 TX/RX 2/3, 4–7 미연결 |

`qbox-platform/systemc-components/dw-apb-i2s/`가 모델을 소유하고,
`platforms/apollo/hw-block/ros.lua`가 AP router, IRQ, audio link, DMA를 연결한다.
`pinctrl.lua`의 route 14/15에 맞춰 `hsoc_gpio::NUM_PERIPHERALS`를 16으로 늘렸다.
두 DMA는 별개의 register/FIFO/trigger 상태와 AP router initiator를 사용한다.
각 DMA DT에는 해당 controller의 shared IRQ를 8개 채널에 동일하게 제공한다.

`apollo-qvp.dts`가 장치의 reg/interrupts/clock/pinctrl/DMA를 선언하고,
`pinctrl.dtsi`가 두 pin group을 정의한다. 기존 Linux
`sound/soc/dwc/dwc-i2s.c`와 `dwc-pcm.c`/DMAengine PCM을 사용한다.
포트별 `simple-audio-card`는 같은 CPU DAI를 공유하는 두 link를 갖는다.
DIT link는 playback PCM, DIR link는 capture PCM을 제공한다. 두 포트 모두
양방향을 사용할 수 있고, 기본 clock master/slave 역할은 data 방향과 무관하다.
DIT/DIR은 ASoC endpoint이며 실제 SPDIF 변환기를 모델링하지 않는다.
두 `audio_socket`은 양방향으로 연결되어 I2S0→I2S1, I2S1→I2S0를 전달한다.

## SystemC 동작과 모델 범위

하나의 stereo 채널과 16-frame TX/RX FIFO를 구현한다. APB register 접근은
32-bit이며, DMA data register에는 16-bit lower-lane 접근도 허용한다.
Linux의 S16_LE DMA slave width를 해당 data port에 연결하기 위한 처리이다.
control register의 subword 접근은 거부한다.

- IER, IRER/ITER, RER/TER, CER로 block/channel/clock을 제어한다.
- RXDA/TXFE와 FIFO overrun 상태, IMR, ROR/TOR read-clear를 구현한다.
- RXFFR/TXFFR와 개별 FIFO flush는 block/channel disable 조건을 따른다.
- 기본 모델(`functional_pacing=false`)에서 빈 master TX는 활성 clock마다
  zero frame을 보내며, full RX FIFO는 overrun을 기록한다. 비활성 RX는 버린다.
- DMA는 `TXDMA=0x1c8`, `RXDMA=0x1c0`, DMACR TX/RX enable과
  QBox 공통 request/ACK handshake를 사용한다. 실제 memory 접근은
  DMA-350 initiator가 AP router를 통해 수행한다.
- TX/RX DMA handshake reset은 방향별로 분리한다. IRER/RER 또는 ITER/TER를
  끄거나 한쪽 DMACR bit를 변경해도 반대 방향의 outstanding request는 유지한다.

audio link는 stereo sample frame을 전달하는 transaction-level 모델이다.
SCLK/WS의 각 bit edge나 전기적 pad 특성은 재현하지 않는다. Pinmux는
peripheral-enable gate로 적용한다. 기본 frame period는 20,833 ns(약 48 kHz)이며
CCI `frame_period_ns`로 설정한다. 가변 sample-rate clock synthesis, TDM,
다중 stereo lane 및 codec의 analog 동작은 이 검증 범위 밖이다.

### Apollo QVP의 명시적 기능 검증 모드

Apollo Lua는 두 I2S에 `functional_pacing=true`를 설정한다. TX에 data가
없으면 기다리고, active RX FIFO가 가득 차면 하나의 stereo frame transaction을
재시도한다. TX는 성공하기 전까지 FIFO front를 제거하지 않는다. 동기식
8-byte TLM 전달을 사용하므로 TX/RX 각각 16-frame FIFO 이외의 audio backlog는 없다.
초기 biflow credit 실험의 무제한 송신 queue는 사용하지 않는다.

이는 **실제 I2S wire의 backpressure가 아니라 QBox 기능 검증용 pacing**이다.
ALSA의 설정 rate는 48 kHz지만 실제 frame 간격, underrun deadline,
overrun 발생률을 검증하는 모드는 아니다. 기본 모델의 timed 동작과 단위 테스트는
계속 제공한다. Linux runtime PASS는 이 기능 검증 모드에 한정한다.

기존 4-CPU `MULTI`/`multithread-freerunning` 설정에서는 timed 모드로 전송할 때
8번째 payload frame 뒤 zero가 삽입됐다. 10 ms quantum을 10 µs로 줄인 실행도
RX overrun과 payload 실패가 남았다. AP bounded quantum, SINGLE 및 COROUTINE,
build-only MCIPS plugin을 사용한 실행은 부팅 진행 문제가 있어 대안으로 검증되지
않았다. 증거는 `build/i2s/pio-trm`, `pio-quantum`, `pio-sync`, `pio-single`,
`pio-tlm`, `pio-mcips`에 남긴다. 이 관측만으로 모든 동기화 실패의 내부 원인을
확정하지 않는다. timed Linux 검증을 위해서는 AP 시간 동기화 경로의 별도 개선이 필요하다.

## Linux cyclic 구현

`arm-dma350.c`는 기존 slave command 생성과 software command chain을 재사용한다.
`device_prep_dma_cyclic`가 buffer를 period로 나누고, 각 DONE IRQ에서 다음
period를 설정하며 마지막 period 다음에는 첫 command로 돌아간다.
`vchan_cyclic_callback()`이 ALSA에 period 완료를 알린다. descriptor cookie는
매 period에 complete하지 않고 terminate 때까지 유지한다. residue는 현재
command의 남은 전송량과 뒤따르는 period 길이의 합으로 buffer 내 위치를 제공한다.

이는 DMA-350 hardware command-link ring이 아니라 IRQ 기반 software rearm이다.
period 사이 IRQ latency가 FIFO에 영향을 줄 수 있으므로 실제 sample 연속성 검사가
필요하다. 기존 memcpy/memset/slave-SG 경로는 유지한다.

`dwc-i2s.c`는 DT에 `dmas`가 있으면 IRQ 유무와 무관하게 DMAengine PCM을
선택한다. DMA 사용 중 FIFO-service IRQ는 mask하고 overrun IRQ만 허용한다.
binding은 IRQ와 DMA를 함께 선언할 수 있도록 `oneOf`를 `anyOf`로 바꿨다.
두 포트 모두 `dma-names = "tx", "rx"`를 사용하므로 초기 RX-only 허용 확장은
제거했고, `dmas`/`dma-names` 형식은 upstream 정의를 유지한다. dtschema 2026.6의
`dt-doc-validate` 및 생성 DTB에 대한 `dt-validate` 검사를 통과했다
(`build/i2s/dt-doc-validate.log`, `dt-validate.log`).

## 검증 방법

`i2s-loopback` Yocto 패키지가 ALSA 검증기를 제공한다. BSP에서 다음과 같이 실행한다.

```sh
./yocto_build.sh --keep-conf --bsp
./run_qbox_yocto.sh --bsp
./scripts/run/ssh_run.sh scripts/test/verify_qbox_i2s.sh
```

기본 DT는 DMA이다. PIO를 재현하려면 `apollo-qvp.dts`의 두 I2S node에서
`dmas`와 `dma-names`를 제거하고 `./yocto_build.sh --keep-conf --bsp`로
**UKI/WIC까지 재빌드**한 뒤 부팅한다. 초기 PIO 검증은 이 상태의 image로
수행했고, 이후 DMA property를 추가한 image로 cyclic을 검증했다.
PIO 검증 뒤 네 property를 복원하고 BSP를 재빌드하면 기본 DMA 구성으로 돌아온다.
별도의 kernel driver patch나 config 변경은 필요 없다.

`--ap-dtb`에 PIO DTB를 지정하는 것만으로는 이 BSP의 Linux DT가 바뀌지 않는다.
UKI가 자체 `.dtb` section을 가지고 있으며 `auto-ad-nexios-uki-ab.bbclass`가
`--devicetree`로 이를 구성하기 때문이다. 실제 override 실행에서도 live DT의
`dmas`가 남아 있음을 확인했다(`build/i2s/pio-current/mode-check.log`).
guest wrapper가 출력하는 live DT mode를 반드시 확인한다.

DMA trace가 필요하면 launcher 끝에 다음 인수를 추가한다.

```sh
-- --platform-param platform.dma350_1.trace=true \
   --platform-param platform.dma350_1.trace_filter=operation \
   --platform-param platform.dma350_1.trace_limit=4096
```

검증기는 하나의 프로세스에서 두 PCM을 준비하고, TX buffer를 미리 채운 뒤
capture와 playback을 차례로 start한다. nonblocking ALSA read/write로
buffer를 소비·보충하며, S16_LE/48 kHz/stereo 65,536 frames(256 KiB)를
모두 비교한다. buffer는 16,384 frames, period는 1,024 frames이므로
4 buffer 분량과 64 period를 검증한다. 시작 전의 zero idle frame만 구분하며,
payload 내부의 zero 삽입, 누락, 순서 변경은 실패한다. timeout과 ALSA 오류도
실패이며 부분 prefix 일치만으로 PASS하지 않는다.

## 현재 8+8채널·양방향 구성 검증

`build/i2s-duplex/bsp-build.log`에서 BSP 5,775 tasks가 성공했다.
platform 60/60(9채널 거부 포함), core 60/60, Python map/trace 검증 15/15가
통과했다. DMA-350/I2S/simple-card 생성 DTB와 schema 검사도 진단 없이 통과했다.
이 당시 DMA DT에는 `dma-coherent;`가 있었으나, CPU cache coherency를 보장하는
통합 근거가 없어 현재는 두 DMA node에서 제거했다. 이를 허용하려던 DMA-350
binding 변경도 원복했다. driver의 `device_get_dma_attr()` 기반 WB/NC 선택은
그대로 사용하며, 현재 AP 구성은 non-coherent DMA로 취급한다.
아래 기존 runtime 결과는 변경 전 기록이며 non-coherent 재검증과 구분한다.

`build/i2s-duplex/runtime/duplex.log`의 관측은 다음과 같다.

| 검사 | 결과 |
| --- | --- |
| DMA 채널 열거 | `31000000`, `31010000` 각각 8채널 |
| I2S0 | playback `hw:0,0`, capture `hw:0,1` |
| I2S1 | playback `hw:1,0`, capture `hw:1,1` |
| I2S0 → I2S1 | 65,536 frames / 262,144 bytes 전체 일치 |
| I2S1 → I2S0 | 65,536 frames / 262,144 bytes 전체 일치 |
| 두 방향 동시 실행 | 양쪽 각각 262,144 bytes 전체 일치 |
| I2S 시험 중 IRQ | `dma350_1` INTID390: 0→394, `dma350_0` INTID311: 0 유지, I2S IRQ: 0 유지 |

각 방향의 sample pattern은 playback PCM 이름에서 다른 seed를 얻어 생성한다.
동시 실행에서 한쪽 stream의 종료가 반대 방향 전송을 깨뜨리지 않음도 확인했다.
모든 검증은 위에서 설명한 QVP `functional_pacing=true` 범위이며 timed FIFO
deadline 검증으로 확대하지 않는다.

`runtime/trace-check.json`은 `dma350_1` 채널 0–3의 실제 FIFO 주소, trigger ID,
4 KiB period, 16-period ring 주소 반복을 검사했다. 각 채널에서 128개의 DONE
period(524,288 bytes), 두 번의 4-buffer 전송을 확인했다. FIFO 주소는 순서대로
`0x302001c8`, `0x302001c0`, `0x302101c8`, `0x302101c0`이다.

`runtime/memcpy.log`에서는 두 controller의 7번 채널로 dmatest를 각각 2회 실행해
모두 통과했다. 4–7번 채널은 I2S request에 연결하지 않았지만 일반 memory DMA에는
사용 가능하다. 이미지·DTB·모델 hash는 `runtime/artifacts.sha256`에 보존했다.

### dma-coherent 제거 후 재검증

`build/i2s-noncoherent/bsp-build.log`에서 BSP 5,775 tasks가 성공했고,
`dt-validate.log`의 DMA-350 schema 검사도 진단 없이 통과했다. DMA binding은
저장소 기준 원본과 동일하다. 두 DMA node 및 상위 `soc`에는 `dma-coherent`가 없다.

`runtime/duplex.log`는 순방향, 역방향, 동시 양방향 각각 262,144 bytes 전체
일치와 `I2S_DRIVER_TEST_PASS mode=dma`를 기록한다. `runtime/memcpy.log`는
`dma0chan7`, `dma1chan7`에서 각각 `2 tests, 0 failures`를 기록한다.

`runtime/attributes.log`에서는 I2S DMA의 memory 측 transaction register와
두 controller의 memcpy SRC/DST register 총 8개를 읽었다. 모두 `0x000F0244`로,
하위 memory attribute가 NC(`0x44`)임을 assert했다. 이는 driver의 non-coherent
분기 선택과 기능 검증이며 실제 CPU cache/snoop 동작을 검증한 것은 아니다.

## 이전 구성의 진행 결과와 실패 분석

아래 `build/i2s/` 결과는 **수정 전 단방향·10채널 구성의 이력**이다.
실제 data 비교 로그는 보존하지만 올바른 DMA-350 토폴로지의 검증으로 취급하지 않는다.
현재 8+8채널·양방향 구성의 검증은 `build/i2s-duplex/`에 기록한다.

- 초기 shell `aplay`/`arecord` 검증은 BusyBox 옵션 오류, orphan recorder,
  별도 프로세스 시작 순서와 blocking read timeout 문제를 포함했다.
- Linux `pcm_lib.c::wait_for_avail()`의 `-EIO`는 timeout이다.
  이 오류만으로 XRUN이나 QBox interrupt 처리량 부족을 단정할 수 없다.
- 단일 프로세스 PIO 검증은 8,192 frames 및 65,536 frames 전체 비교를 통과했다.
  근거: `build/i2s/pio-coordinated/alsa-coordinated.log`, `alsa-stream.log`.
  이때 사용한 초기 모델은 active RX credit을 포함하므로,
  최종 모델에서는 backpressure 제거 후 재검증이 필요하다.
- 모델의 집중 테스트는 FIFO/IRQ/disable/flush/idle/drop,
  16-bit DMA data-port 및 request/ACK 동작을 검사한다. 기능 검증 모드에서는
  RX FIFO 16개를 채우고 17번째 frame을 재시도한 후 이전 frame 순서와
  마지막 frame의 무손실 전달을 확인한다.
  request/ACK 반복 단위 테스트 자체는 Linux DMA cyclic 검증이 아니다.

### 최종 PIO 결과

`build/i2s/pio-functional/alsa-stream-120s.log`에서
`I2S_DRIVER_TEST_PASS mode=pio`를 확인했다. 65,536 frames / 262,144 bytes가
모두 일치했고 leading idle은 0이었다. IRQ counter는 TX 9,741→17,939
(+8,198), RX 6,104→14,296(+8,192)였다. 사용한 DT에는 두 I2S의 `dmas`가 없다.
PIO WIC, DTB, 검증기, 모델 SO의 SHA-256은 같은 디렉터리의 `artifacts.sha256`에 있다.

30초 제한의 첫 실행은 48,824 frames까지 비교한 뒤 timeout됐다.
전송 조건·데이터량은 유지하고 검증기 제한만 120초로 늘렸다.
standalone 실행에 대한 host 측 제한은 `timeout 180`을 권장한다.

### 빌드 회귀 기록

`provider-functional.log`의 compile/check/install/populate_sysroot가 통과했다.
최종 BSP 갱신 중 별도 core 테스트
`aarch64-single-tcg-five-cpu-shutdown-test`,
`aarch64-managed-timer-wfi-baseline`가 각각 30초 timeout됐다
(`core-timeout-during-bsp.log`). 이 실행에서도 I2S를 포함한 platform 59개는
통과했다. 두 core 테스트의 source는 이 작업에서 수정하지 않았고,
PIO VM 종료 후 동일 BSP 명령을 재실행했다. 재실행 성공은 간헐적 실패의 수정 증거가 아니다.

`final-bsp-build-retry.log`에서 5,775 tasks가 성공했다. 최종 provider check는
platform 59/59(5.65초), core 60/60(19.17초)이다.
각 로그는 `build/i2s/platform-tests-final.log`, `core-tests-final.log`에 보존했다.
AP map pytest 2/2, full-map validator, core boundary audit, shell syntax,
owning repository별 `git diff --check`도 통과했다.

### 최종 DMA cyclic 결과

`build/i2s/dma-functional/alsa-stream.log`와 `alsa-restart.log`의 두 실행 모두
`I2S_DRIVER_TEST_PASS mode=dma` 및 **65,536 frames / 262,144 bytes 전체 일치**를
기록했다. 첫 실행 이후 drop/close하고 다시 open/start한 재시작도 통과했다.

| 항목 | 관측 |
| --- | --- |
| DMA TX | channel 8, destination trigger 8, destination `0x302001c8` |
| DMA RX | channel 9, source trigger 9, source `0x302101c0` |
| period | 각 4,096 bytes, 각 buffer에 16 periods |
| 순환 | 실행마다 64 periods, buffer 주소 4회 반복 |
| 두 실행 합계 | 채널별 128 DONE periods / 524,288 bytes, STOP 2회 |
| IRQ | DMA shared INTID311: 0→64→149, I2S INTID388/389: 계속 0 |
| PCM | S16_LE, stereo, ALSA 설정 48 kHz, leading idle 0 |

`qbox-platform.log`의 실제 DMA 완료 trace를 파싱해 FIFO 주소, trigger,
period 길이와 16-period 주소 반복을 assert한 결과는 `dma-trace-check.json`이다.
IRQ는 두 채널의 완료를 함께 처리할 수 있으므로 IRQ 횟수를 period 수와 동일시하지 않는다.
trace에 error completion은 없으며, 마지막 partial period는 사용자의 stream drop에 따라
STOP 처리됐다. 사용 artifact hash는 `artifacts.sha256`에 있다.

같은 guest에서 기존 DMA memcpy도 검사했다.

```sh
modprobe dmatest channel=dma0chan6 iterations=2 timeout=5000 run=1 wait=1
```

`memcpy-regression.log`는 `summary 2 tests, 0 failures`를 기록한다.
이 검사는 memcpy 회귀 확인이며 모든 SPI/UART DMA 조합 재검증을 뜻하지 않는다.

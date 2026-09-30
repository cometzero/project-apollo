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


## Standalone system QEMU 검증 (2026-09-30)

`run_qemu_linux.sh --bsp`의 `apollo-qvp`에도 DMA-350 두 개와
DW_apb_i2s 두 개를 등록했다. QBox SystemC의 register/FIFO/trigger 동작을
QEMU SysBus 모델로 포팅했으며, 기존 Linux driver와 현재 `apollo-qvp.dts`의
주소·IRQ·DMA request ID·ASoC link를 그대로 사용한다. SystemC library를
system QEMU에 로드하는 방식은 아니다. 모델 소유 파일은 QEMU repository의
`hw/dma/arm-dma350.c`, `hw/audio/dw-apb-i2s.c`, `hw/arm/apollo-qvp.c`이다.

```sh
./yocto_build.sh --keep-conf qemu-apollo-native
./run_qemu_linux.sh --bsp                 # 기본 DMA
./run_qemu_linux.sh --bsp --i2s-mode pio   # Linux PIO
python3 scripts/test/verify_qemu_i2s.py   # 두 모드 자동 검증
```

PIO 옵션은 QEMU가 생성하는 DT의 `dmas`와 `dma-names`만 제외한다.
두 DMA controller와 I2S register map은 유지된다. 외부 `--dtb`와 PIO 옵션을
함께 지정하면 실패시켜, 모드 선택이 무시되는 일을 방지한다. 직접 Image/initrd
부팅이므로 QBox UKI의 embedded DT override 제한은 이 경로에 적용되지 않는다.

최종 evidence:
`build/qbox-apollo-qvp/qemu-i2s-peer-fixed-20260930/`.
각 mode의 `live.dtb`, `live.dts`, `linux-uart.log`, `launch.json`,
`dma-result.json`/`pio-result.json` 및 aggregate `result.json`을 보존한다.
검증기는 기존 `scripts/test/verify_qbox_i2s.sh`와 BSP의 `i2s-loopback`을 사용했다.
Linux source/DT/image 수정이나 loopback payload 변경은 하지 않았다.

| 검사 | 결과 | 관측 |
| --- | --- | --- |
| DMA 0→1 / 1→0 / 동시 양방향 | PASS 4/4 | 각 65,536 frames / 262,144 bytes 전체 비교 |
| PIO 0→1 / 1→0 / 동시 양방향 | PASS 4/4 | 각 65,536 frames / 262,144 bytes 전체 비교 |
| DMA IRQ | PASS | INTID 390 +195 |
| PIO IRQ | PASS | INTID 388 +25,762, INTID 389 +25,705 |
| live DT DMA/PIO 선택 | PASS | 두 I2S node의 dmas 유무 확인 |
| 장치 register/traffic | PASS 28/28 | FIFO overflow/flush/read-clear, 양방향 frame 전달, DMA copy/hash/error/STOP/GIC IRQ/self-target bus error |
| launcher/검증기 focused pytest | PASS 49 | 잘못된 PCM/IRQ/echo 결과의 PASS 방지 포함 |
| 전체 BSP selftest | FAIL | DSU cache/PMU, watchdog, remoteproc, RPMsg, PFDI 미구현 범위 유지 |

장치 검사는 `scripts/test/verify_qemu_audio_models.py`로 실행하며, 배포된 QEMU에
provider manifest의 `library_path`를 적용한 최종 결과는
`build/qbox-apollo-qvp/qemu-i2s-models-provider-20260930/result.json`이다.
ALSA와 장치 검사가 사용한 배포 binary의 SHA256은
`04a3ebe225f2c3d0c633cd3da9565a23dbfcc3ae204e2b70d6af9550572ed179`이다.

최초 실행 `qemu-i2s-20260930/`의 DMA/PIO FAIL도 유지한다. 원인은
두 번째 I2S의 QOM parenting 전에 첫 peer link를 설정해 NULL link가 된 것이다.
두 장치를 먼저 parenting한 뒤 연결하도록 수정했으며, 양방향 실제 FIFO frame
검사가 이 오류를 회귀 검출한다. DMA의 active CH_INTREN 쓰기도 지원해 STOP IRQ를
검증했고, DMA가 자기 MMIO를 쓰는 경우 QEMU reentrancy guard로 bus error를 낸다.

이 결과는 S16_LE stereo 48 kHz 기능 검증이다. QBox처럼 functional pacing으로
빈 TX를 기다리고 full RX에 backpressure를 적용한다. 물리 I2S clock/underrun
정확도, analog codec, hardware command-link, security attribution, migration,
FVP/RTL parity는 검증하지 않았다. standalone machine의 DMA0에는 SPI/UART
request가 연결되지 않으며 pinmux는 고정 audio route이다.


### 실제 aplay / arecord WAV 비교 (2026-09-30)

`i2s-loopback` 외에 BSP에 설치된 `aplay`와 `arecord`를 실행했다.
48,000 Hz, S16_LE stereo, 96,000 frames(2초)의 서로 다른 좌우 채널 tone을
`source.wav`로 생성했다. DMA와 PIO 각각 I2S0→I2S1 및 I2S1→I2S0를
순차 실행했으며 **4/4 PASS**이다. 네 녹음 모두 PCM뿐 아니라 WAV header를
포함한 전체 **384,044 bytes가 원본과 완전히 동일**했다.
원본 변경, 녹음 offset 정렬, 앞뒤 sample 제거는 하지 않았다.

```sh
python3 scripts/test/verify_qemu_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/qemu-i2s-wav-new
```

각 방향에서 실제로 실행한 ALSA 명령은 다음과 같다. `$tx`와 `$rx`는
`aplay -l`/`arecord -l`에서 MMIO 주소로 찾은 서로 반대편 hw PCM이다.

```sh
arecord -N -D "$rx" -t wav -f S16_LE -r 48000 -c 2 \
  --period-size=1024 --buffer-size=16384 -s 96000 capture.wav &
sleep 0.2
aplay -D "$tx" --period-size=4096 --buffer-size=16384 source.wav
wait
```

자동화에서는 두 명령 각각 `timeout 60`으로 제한하며, exit code 0,
live DT의 DMA/PIO 선택, 실제 IRQ 증가와 전체 PCM 일치를 함께 검사한다.
QEMU user network의 guest 주소를 설정하고, 임시 localhost HTTP server에서
원본 WAV를 가져온 뒤 녹음은 UART base64로 회수한다. Model, kernel 및 BSP
image는 앞선 loopback 검증과 동일하며 변경하지 않았다.

증거: `build/qbox-apollo-qvp/qemu-i2s-wav-period-20260930/` 아래
`source.wav`, `{dma,pio}/{forward,reverse}.wav`, mode별 guest script/UART 로그,
`result.json`. 원본과 네 녹음의 공통 WAV SHA256:
`b682b891ba07d1c7e594992780a7b2268d0b23d67ad3e0df0d7086af238cc7d8`.
DMA INTID 390은 +194, PIO INTID 388/389는 각각 +61,351/+24,913이었다.

재현 시 다음 조건에 주의한다. 초기 실패 결과도 `qemu-i2s-wav-*`에 보존했다.

- 현재 배포된 `aplay`에는 `--drain-timeout` 확장 옵션이 없어 사용하지 않는다.
- 송신 전에 clock이 없는 동안 blocking capture는 PCM wait timeout이 발생했다.
  `arecord -N`으로 수신을 먼저 대기시킨다.
- 2,048-frame ALSA buffer에서는 capture overrun이 발생했다. PASS 설정은
  16,384-frame buffer이다. 이는 작은 버퍼의 실시간 처리 능력을 검증하지 않는다.
- PIO의 최소 capture period는 1,024 frames이다. playback/capture period를
  모두 1,024로 설정하면 `arecord`가 마지막 전체 chunk를 채우지 못해
  95,232 frames를 저장한 뒤 timeout했다. 저장된 prefix는 원본과 동일했다.
  `arecord`는 최종 요청이 768 frames여도 1,024 frames를 읽는다.
  playback period 4,096은 `aplay`의 표준 EOF 무음 채움으로 마지막 capture
  chunk까지 공급한다. 녹음 파일은 `-s 96000`에 따라 원본 길이 그대로이며,
  이 결과로 EOF의 물리 FIFO drain 동등성을 주장하지 않는다.

### QBox direct Linux BSP 검사 (2026-09-30)

`./run_qbox_linux.sh --bsp`의 기본 4-CPU `apollo-qvp-linux.lua`에서
SystemC DMA-350/DW_apb_i2s를 검사했다. DMA는 배포 DT를 사용하고, PIO는
두 I2S node의 `dmas`/`dma-names`만 제거한 DT 복사본으로 부팅했다.
QBox 실행 파일, 두 model library, kernel 및 initramfs의 hash는 모든
검사 실행에서 동일했다. 이번 검사에서 모델이나 Linux는 수정하지 않았다.

| 검사 | 결과 | 관측 |
| --- | --- | --- |
| DMA-350 두 controller memcpy/memset | PASS | DMA/PIO DT 각각 20회, 64 KiB test buffer, 데이터 검증 및 IRQ 증가 |
| I2S DMA 단독 0→1 / 1→0 | PASS 2/2 | 각 65,536 frames 전체 비교 |
| I2S DMA 동시 양방향 | **FAIL** | 두 프로세스 모두 7,741/65,536 frames에서 timeout |
| I2S PIO 단독 및 동시 양방향 | PASS 4/4 | 각 65,536 frames 전체 비교 및 IRQ 증가 |
| aplay/arecord WAV, DMA/PIO 순차 양방향 | PASS 4/4 | 48 kHz S16_LE stereo, 96,000 frames, WAV 전체 384,044 bytes 동일 |
| 전체 BSP selftest | FAIL | AP-only profile의 PFDI misc 실패; audio 검사와 별도 |

DMA 동시 양방향 timeout 당시 capture/playback 상태는 모두 RUNNING이었다.
원인은 아직 확정하지 않았으며, 전체 audio qualification은 **FAIL**로 유지한다.
단독 방향 WAV 성공이 동시 양방향 DMA 성공을 의미하지 않는다.

재현 자동화는 실제 launcher를 실행하고 UART 로그, 실행 명령, DT,
artifact hash, 원본 및 녹음 WAV를 보존한다.

```sh
python3 scripts/test/verify_qbox_linux_audio.py \
  --out-dir build/qbox-apollo-qvp/qbox-linux-audio-new
```

`scripts/test/verify_dma350_memory.sh`는 각 controller의 사용하지 않는
channel에서 dmatest memcpy/memset을 각각 5회 실행한다. PIO DT에서는
channel 할당 전 IRQ action이 없을 수 있어 초기 IRQ count를 0으로 허용하고,
검사 후에는 실제 IRQ 등록과 증가를 요구한다. 최초 helper의 이 조건 오류를
수정한 뒤 PIO memory 검사를 재실행해 통과했다.

PIO WAV의 최초 blocking `aplay` 실행은 EIO로 실패했다. `aplay -N`으로
재실행한 두 방향은 모두 정상 종료하고 전체 파일 비교를 통과했다.
최종 자동화는 `aplay -N`/`arecord -N`, playback/capture period
4,096/1,024 frames 및 buffer 16,384 frames를 사용한다. DMA WAV의 기록된
PASS는 blocking `aplay` 실행 결과이다. WAV 원본 및 녹음의 공통 SHA256은
위 standalone QEMU 검사와 동일하다. 녹음 정렬이나 sample 제거는 하지 않았다.

통합 결과: `build/qbox-apollo-qvp/qbox-linux-audio-summary-20260930.json`.
원본 실패 로그도 다음 evidence directory에 보존한다.

- `qbox-linux-audio-20260930/`: 최초 DMA/PIO 전체 검사.
- `qbox-linux-memory-pio-20260930/`: 수정한 helper로 PIO memory 재검사.
- `qbox-linux-wav-pio-nonblock-20260930/`: nonblocking PIO WAV 재검사.

위 경로는 모두 `build/qbox-apollo-qvp/` 아래이다. 이는 functional pacing
검사이며 물리 I2S timing이나 FVP/RTL 동등성 검증은 아니다.

### QBox qemu-components 전환 및 재검사 (2026-09-30)

`apollo-qvp-linux.lua`의 두 DMA/I2S를 `qemu_dma350` 및
`qemu_dw_apb_i2s`로 교체했다. standalone QEMU에서 검증한 동일한
`arm-dma350`/`dw-apb-i2s` 구현을 AP libqemu instance에서 사용한다.
전체 firmware profile은 기존 SystemC 모델을 유지한다.

I2S peer 및 DMA1 request/ack는 QEMU 내부에서 직접 연결한다. DMA0의
SystemC SPI/UART 연결은 정수 GPIO bridge로 유지한다. request의 ACTIVE와
type 비트가 boolean 변환으로 손실되지 않도록 libqemu-cxx에 정수 GPIO API를
추가했고, 기존 boolean API 동작도 회귀 검사했다. DMA 메모리 접근은 기존
AP global peripheral initiator와 router를 사용한다. MMIO/IRQ 및 guest
kernel/initramfs는 유지했다. Native I2S는 고정 경로이며 pinmux gating은
지원하지 않아 Linux profile의 해당 두 pinmux output 연결을 제거했다.

```sh
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
python3 scripts/test/verify_qbox_linux_audio.py \
  --out-dir build/qbox-apollo-qvp/qbox-qemu-components-audio-new
```

| 검사 | 결과 | 관측 |
| --- | --- | --- |
| DMA350 두 controller memcpy/memset | PASS | DMA/PIO DT 각각 20회, 64 KiB test buffer 및 IRQ 증가 |
| DMA 단독 및 동시 양방향 PCM | PASS 4/4 | 각 65,536 frames / 262,144 bytes 전체 비교, INTID 390 +215 |
| PIO 단독 및 동시 양방향 PCM | PASS 4/4 | 동일 크기 비교, INTID 388/389 +43,175/+25,288 |
| aplay/arecord WAV, DMA/PIO 순차 양방향 | PASS 4/4 | 48 kHz stereo S16_LE 2초, header 포함 384,044 bytes 원본과 동일 |
| provider do_check | PASS | platform 64개, core 61개; 정수 GPIO 및 boolean 호환성 검사 포함 |
| Python focused 검사 및 full-map 검사 | PASS | Python 42개, static map 검사 통과 |
| 전체 BSP selftest | FAIL | 기존 AP-only PFDI misc 실패 유지 |

앞선 SystemC 구성의 DMA 동시 양방향 timeout은 이번 native QEMU 구성에서
발생하지 않았다. 이것만으로 기존 SystemC 실패의 원인이 확정된 것은 아니다.
이번 WAV 검사는 `aplay -N`/`arecord -N`을 사용했으며, 앞 절과 같은 period와
buffer 조건이다. 녹음 파일의 offset 조정이나 sample 제거는 하지 않았다.

증거는 `build/qbox-apollo-qvp/qbox-qemu-components-audio-20260930/`의
`result.json`, mode별 UART/launcher 로그, 원본·녹음 WAV 및 artifact hash이다.
`loaded-audio-libraries.txt`에는 실행 중 `/proc/PID/maps`에서 확인한
두 native wrapper 및 libqemu 경로를 보존했다. audio 결과는 **PASS**이며,
물리 timing, FVP/RTL 동등성, pinmux gating 및 SPI/UART DMA traffic의
추가 qualification을 의미하지 않는다.

최종 Lua 배포 재검사 중 기존 `uart-biflow-backend-socket-test`에서
segfault가 한 차례 발생했다. 독립 5회 반복은 모두 통과했으며, 실패 로그는
`build/qbox-apollo-qvp/qemu-components-qbox-final-deploy.log`, 재검사는
`qemu-components-uart-recheck.log`에 보존했다. 오디오 guest 검사와 별도의
간헐적 core-test 실패이며 원인은 확정하지 않았다.
전체 recipe 재실행은 64/61 검사와 최종 배포까지 통과했다
(`qemu-components-qbox-final-retry.log`). 배포 후 모든 runtime artifact hash가
검사 시점과 동일하고 설치된 Lua가 검증한 source와 일치함을 확인했다.

### QEMU DMA + SystemC I2S 혼합 검사 (2026-09-30)

현재 `apollo-qvp-linux.lua`는 두 DMA350만 `qemu_dma350`로 교체하고,
I2S는 공통 profile의 SystemC `dw_apb_i2s`, audio socket 및 pinmux 연결을
유지한다. DMA1 request/ack도 DMA0과 동일한 정수 GPIO bridge를 통과한다.
모델 C/C++ 구현, kernel 및 initramfs는 앞선 검사에서 변경하지 않았다.

| 검사 | 결과 | 관측 |
| --- | --- | --- |
| 두 DMA350 memcpy/memset | PASS | DMA/PIO DT 각각 20회 및 IRQ 증가 |
| I2S DMA loopback | FAIL | 첫 방향 실행 중 `d350_get_residue()`에서 kernel panic; 나머지 방향 미실행 |
| I2S PIO 단독·동시 양방향 | PASS 4/4 | 각 65,536 frames 전체 비교 |
| DMA WAV 별도 부팅 검사 | FAIL | 첫 방향에서 동일 kernel panic 재현; reverse 미실행 |
| PIO WAV 양방향 | FAIL 2/2 | playback=0, capture=124(timeout); 93,184 / 94,192 frames만 저장 |

PIO 녹음의 저장된 PCM prefix는 원본과 동일하지만, 요청한 96,000 frames에
미달하므로 완전한 WAV 일치로 판정하지 않는다. `aplay -N`/`arecord -N`,
period 4,096/1,024, buffer 16,384 및 60초 command timeout은 이전과 동일하다.

DMA loopback에서는 QEMU가 `arm-dma350` offset `0x1020`의 reentrant IO를
차단한 뒤 Linux에 synchronous external abort가 발생했다. WAV 별도 부팅에서도
offset `0x1324` 경고와 같은 residue 함수의 panic을 관측했다. 소스상
`dma350_tick()`은 service 동안 `mem_reentrancy_guard`를 유지하며, QBox의
SystemC 전송은 QEMU iothread lock을 풀고 대기한다. 이 구간에 CPU residue
읽기가 겹치는 것으로 추정하지만, guard 제거 등 모델 수정은 이번 비교 검사에
적용하지 않았다. 현재 혼합 구성의 전체 판정은 **FAIL**이다.

재현:

```sh
python3 scripts/test/verify_qbox_linux_audio.py \
  --out-dir build/qbox-apollo-qvp/qbox-mixed-audio-new
python3 scripts/test/verify_qbox_linux_audio.py --mode dma --tests wav \
  --out-dir build/qbox-apollo-qvp/qbox-mixed-wav-dma-new
```

증거는 `build/qbox-apollo-qvp/qbox-mixed-audio-20260930/`와
`qbox-mixed-wav-dma-20260930/`의 result JSON, UART/QBox 로그 및 녹음 WAV이다.
첫 실행의 DMA panic은 수동으로 launcher를 중단했고, 검증기에 panic 감지를
추가한 뒤 별도 WAV 실행은 즉시 종료했다. Launcher login PASS와 audio 판정은
별개이며, 미실행 WAV 방향은 비교 자료가 없는 상태이다. 실제 로드된
`qemu_dma350.so`와 `dw-apb-i2s.so` 경로도 보존했다.

### Native QEMU DMA/I2S full-system 검사 (2026-09-30)

현재 두 entrypoint는 `common.use_qemu_audio()`로 AP의 두 DMA350과 두 I2S를
모두 QEMU component로 구성한다. Full-system은 `enable_ap_router()` 이후
교체하므로 기존 MMIO address-view/IRQ/reset 연결을 유지한다. RSE boot DMA는
별도 모델이며 변경하지 않았다. DMA0의 SPI/UART 정수 GPIO bridge와 native
I2S/DMA1 내부 request/ack 연결은 앞선 AP-only native 구성과 같다.
Native I2S의 고정 audio route에는 pinmux gating이 없다.

이번 검사는 실제 `run_qbox_yocto.sh --bsp --headless`를 호출하며
RSE/SCP/Safety Island CL1/TF-A/U-Boot를 거쳐 BSP UKI를 부팅했다.
AP-only Linux loader나 domain mock을 사용하지 않았다. 기본 4 AP CPU,
multithread-freerunning/quantum_keeper 및 10 ms quantum을 유지했다.

```sh
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
python3 scripts/test/verify_qbox_full_audio.py \
  --out-dir build/qbox-apollo-qvp/qbox-full-native-audio-new
```

PIO는 private WIC의 unsigned A/B UKI `.dtb`에서 두 I2S의 `dmas` 및
`dma-names`만 제거한다. 배포 원본 WIC를 보존하고, 나머지 UKI section hash가
그대로인지 검사한다. kernel/initramfs는 앞선 AP-only PASS 이미지와 같으며,
guest live DT에서 DMA/PIO 선택을 다시 확인한다.

| full-system 검사 | 결과 | 관측 |
| --- | --- | --- |
| BSP 자체 검사 | PASS 22/22, 두 부팅 모두 | PFDI, remoteproc, RPMsg 항목 포함 |
| 두 DMA350 memcpy/memset | PASS | DMA/PIO DT 각각 20회; data 및 IRQ 증가 확인 |
| DMA PCM 단독·동시 양방향 | FAIL 0/4 | capture/playback `Broken pipe`, DMA INTID 390 +100 |
| PIO PCM 단독 양방향 | PASS 2/2 | 각 65,536 frames 전체 비교 |
| PIO PCM 동시 양방향 | FAIL 1/2 | 0→1 playback `Broken pipe`; 1→0 PASS |
| DMA WAV 순차 양방향 | FAIL 2/2 | playback=0, capture=124; 74,596 / 48,216 frames, 저장된 내용도 원본과 불일치 |
| PIO WAV 순차 양방향 | PASS 2/2 | 48 kHz S16_LE stereo, 96,000 frames, WAV 전체 384,044 bytes 원본과 동일 |
| 빌드·단위·정적 검사 | PASS | provider platform/core 64/61개, Lua 9개, full-map 검사 |

전체 audio 판정은 **FAIL**이다. 이번 full-system에서는 혼합 구성의 kernel
panic 대신 ALSA XRUN 및 capture timeout을 관측했다. AP-only native PASS를
full-system PASS로 확대하지 않는다. 추가 firmware domain 및 interrupt 경로는
AP-only와 다르지만 XRUN 원인은 아직 확정하지 않았다. BSP 자체 검사의 PASS도
post-login 전체 platform qualification이나 FVP/RTL timing 동등성을 뜻하지 않는다.

증거: `build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/`의
`result.json`, mode별 domain/UART 로그, `disk-preparation.json`, WAV 및 설치된
provider/model/Lua hash. PIO 녹음의 SHA256은
`b682b891ba07d1c7e594992780a7b2268d0b23d67ad3e0df0d7086af238cc7d8`이다.

최초 `qbox-full-native-audio-20260930/` 실행은 launcher가 boot PASS 후 runtime을
분리하면서 검증기 감독이 먼저 종료됐고 PIO는 HTTP 전송에도 실패했다.
이 실행은 최종 qualification으로 사용하지 않는다. 하네스에
`--foreground-runtime`, bounded download retry 및 종료 처리를 적용한 위
재실행을 최종 결과로 사용한다. PCM 검사는 첫 실패 뒤에도 나머지 방향을 실행한다.

### Full-system 검사 후 AP-only 재검사 (2026-09-30)

모델이나 설정을 추가 변경하지 않고 현재 all-native 구성을
`run_qbox_linux.sh --bsp`로 재검사했다. 결과는 **audio PASS**이다.

| 검사 | 결과 |
| --- | --- |
| 두 DMA350 memcpy/memset | DMA/PIO DT 각각 20회 PASS |
| DMA PCM 단독·동시 양방향 | 4/4 PASS, 각 65,536 frames 전체 비교 |
| PIO PCM 단독·동시 양방향 | 4/4 PASS, 각 65,536 frames 전체 비교 |
| 48 kHz WAV DMA/PIO 양방향 | 4/4 PASS, 각 384,044 bytes 전체 원본 일치 |

직전 full-system 실행과 QBox 실행 파일, 두 wrapper, libqemu, kernel 및
initramfs의 SHA256이 모두 같음을 확인했다. 이 재검사는 AP-only PASS와
full-system FAIL 차이를 재확인하며, 그 원인을 확정하지는 않는다.
AP-only의 별도 BSP PFDI 실패는 유지된다.

```sh
python3 scripts/test/verify_qbox_linux_audio.py \
  --out-dir build/qbox-apollo-qvp/qbox-ap-only-native-retest-new
```

증거: `build/qbox-apollo-qvp/qbox-ap-only-native-retest-20260930/result.json`,
`full-system-comparison.json`, mode별 UART 로그와 원본·녹음 WAV.

# Apollo QVP DW_apb_i2s 구현과 검증

기본 시간 모드를 유지하는 해결 방향과 최신 실패 재현은
[기본 QK 소형 링 조사](i2s-default-qk-investigation-20260916.md)에 기록한다.
2026-09-16 초기 PIO 대조 검사는 기본 QK에서 양방향 실패했다. 후속 QK 수정과
명시적 PIO 대기시간 5000 ms 및 ALSA drain timeout 반영 후 8192-frame WAV는
양방향 전체 일치했다. 이후 PIO stream-lock 수정, IRQ CPU0/1 분산 및
aplay/arecord CPU2 배치 조건에서 8192 frames 양방향 각 5회(10/10),
196608 frames와 196625-frame odd tail 각각 양방향 전체 일치를 확인했다.
기본 IRQ 배치의 반복 실패는 남아 있다. DMA는 hardware command-link와
선택적 DONEPAUSE, wait 5000 ms, IRQ CPU0/apps CPU2 조건에서 양방향 긴 WAV,
20회 반복 및 odd tail 전체 일치와 SPI/UART/memory DMA 회귀를 통과했다.
수동 pause/resume의 별도 FIFO flush 문제도 수정했으며, TX 단독/양쪽 pause
및 paused STOP을 양방향에서 통과했다. PIO odd-tail의 간헐적 FAIL은
명시적 `pio_fifo_empty_irq=Y` 경로로 재검증해 8209 frames 양방향 총 30회와
196625 frames 양방향 모두 전체 일치를 확인했다. 기본 false인 옵션을 끈
경로의 실패 이력은 유지한다. 최종 기본 DMA 이미지 복원과 재검증도 완료했다.
최종 실행 조건과 결과 표는
[freerunning 기능 검증 요약](i2s-freerunning-validation.md)을 참조한다.
기존
functional pacing의 데이터 무결성 결과를 물리적인 48 kHz 성능과 구분한다.
명령·live DT·중간 실패·최근 결과는 위 문서를 참조한다.

후속 2-period XRUN 조사, DMA MMIO 시간 처리 수정 및 실제 Linux 회귀 결과는
[소형 cyclic ring 후속 조사](i2s-xrun-followup-20260915.md)에 기록한다.
2026-09-16 최종 실제 QBox/Linux 검증에서는 all-domain MCIPS/100 µs,
일반 blocking I/O, S16_LE stereo 48 kHz, period 1024/buffer 2048 조건으로
양방향 각 10회(총 20회) 모두 PCM/hash 일치, zero/XRUN 0을 확인했다.
196625-frame 비정렬 끝부분도 양방향 모두 통과했다. SPI/UART/memory DMA
회귀와 실제 copy/set을 구분한 residue polled 20회도 통과했다.
기본 QK 시간 설정은 변경하지 않았으며, 별도 `-N` 소형 ring stress는
최종 빌드에서도 FAIL이다. 이 제한과 중간 실패를 일반 blocking PASS와
구분해야 한다. 상세 명령·산출물·판정은 위 후속 문서에 기록했다.

## 2026-09-15 WAV 마지막 period 누락 수정

아래의 초기 WAV 실패를 재현하고 Linux 드라이버와 SystemC 모델의 종료 경로를
수정했다. DMA-350의 residue를 오디오 전송 완료로 바꾸거나 WAV를 padding/
잘라내기하여 통과시키는 변경은 하지 않았다.

### 원인과 변경

1. **DMA 완료는 직렬 전송 완료가 아니다.** `snd_dmaengine_pcm_pointer()`는
   DMA residue로 진행량을 계산한다. TXDMA에 쓴 데이터가 I2S FIFO에 남아
   있어도 ALSA DRAINING은 STOP에 도달한다. 기존 `dw_i2s_trigger()`는 바로
   ITER를 끄고 마지막 active stream이면 IER도 껐다. Databook §2.2의 IER
   disable은 FIFO를 비우므로 미전송 샘플이 사라진다.
2. **프레임 몇 개의 유실이 파일에서는 한 period 부족으로 나타난다.** 실패
   trace에서 TX channel 0은 192 periods를 완료했지만 RX channel 3은
   191 periods + 4088/4096 bytes에서 멈췄다. stereo S16_LE 두 프레임이
   부족해 `arecord`가 마지막 1024-frame read를 반환하지 못했다. 파일의
   앞 195584 frames는 원본과 정확히 일치했다.
3. **Linux 수정:** DMA 모드의 stop 순서를 DMA component→DAI로 변경하고,
   playback의 `STOP && DRAINING`에 한해 I2S DMA 요청을 끈 후 FIFO depth
   + serializer 한 프레임의 시간을 기다리고 ITER/IER를 끈다. 현재
   16-frame FIFO/48 kHz에서는 355 μs이다. atomic trigger에서 sleep하지
   않고 1 ms 이하 `udelay()` 청크를 사용한다. PIO/JH7110 및 capture,
   drop/pause/suspend는 이 drain 대기 대상이 아니다. `terminate_async()`를
   완전한 DMA synchronize라고 간주하지 않으며 I2S 요청도 차단한다.
4. **SystemC 수정:** `dw_apb_i2s::b_transport()`가 입력 TLM delay를 소비한
   후 레지스터를 읽거나 쓰도록 했다. QBox QEMU initiator는 CPU local time을
   delay로 전달하는데, 기존 모델은 레지스터를 즉시 변경하고 지연만 반환했다.
   따라서 CPU의 drain 대기가 serializer의 SystemC 시간에 반영되기 전에
   STOP이 실행될 수 있었다. Linux 수정만으로 기본 버퍼 10회는 통과했으나
   동시 양방향에서 마지막 period 누락이 다시 발생하여 충분하지 않았다.
5. **회귀 테스트:** 8개 stereo frames를 FIFO에 채운 뒤 미래 시각의 ITER
   STOP을 전달하는 `DelayedStopPreservesSerializedFrames`를 추가했다.
   기존 모델은 수신 데이터가 0으로 FAIL, delay 처리 수정 후 PASS했다.
   이는 FIFO를 STOP 이후 억지로 전송하거나 무시하는 모델 변경이 아니다.

### 재현 도구와 판정

`scripts/test/validate_qbox_i2s_wav.py`는 실제 부팅된 Linux에 SSH로 접속해
`aplay`/`arecord`를 실행한다. 기본값은 S16_LE stereo 48 kHz,
196608 frames(192 periods), period 1024 / buffer 2048이며 양방향 5회씩이다.
일반 blocking I/O가 기본이고 `--nonblock`은 별도 stress 조건이다.
아래 초기 EOF 검사의 큰 버퍼 조건은 `--buffer 16384`로 명시한다.
매 실행의 WAV/로그를 독립 디렉터리에 저장하고 PCM 길이, 전 바이트,
zero-frame 수, period별 일치 및 SHA-256을 비교한다. 종료 코드 또는 파일
복사가 실패해도 FAIL이다. 테스트 결과는 `results.json`에 누적한다.

```sh
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/i2s-drain-fix/final-repeat --rounds 5 --buffer 16384
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/i2s-drain-fix/final-two-period \
  --rounds 3 --buffer 2048 --nonblock
```

소형 버퍼에서 blocking `arecord`를 먼저 시작하면 데이터가 없는 동안
`sound/core/pcm_lib.c::wait_for_avail()`의 최소 100 ms 제한으로 EIO가 날 수
있다. 이는 EOF 유실과 별도이다. 실패 산출물은 `after-two-period*`에
보존했다. `--nonblock`은 ALSA-utils의 기존 `-N` 옵션으로 EAGAIN/poll을
사용하며, 시험 전체의 `timeout 45`와 정확한 프레임 수 판정은 유지한다.
입력 데이터가 부족한 것을 정상 종료나 PASS로 바꾸지는 않는다.

증거 루트는 `build/i2s-drain-fix/`이다. `before/`와 `before-repeat/`는
원래 모델/커널, `after/`와 `after-repeat/`는 Linux 수정만 적용한 중간
시험이다. `after-duplex-isolated-*`에서 중간 수정의 재실패를 보존했다.
`after-duplex-*`(isolated 제외)는 소형 버퍼 시험과 장치 점유가 겹친
잘못된 실행이므로 duplex qualification에 사용하지 않는다.

빌드는 기존 build/conf를 유지하고 명시적으로 Apollo QVP를 선택했다.
공유 BitBake 빌드는 직렬 실행했다.

```sh
./yocto_build.sh --machine apollo-qvp --keep-conf virtual/kernel -c compile
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp
./yocto_build.sh --machine apollo-qvp --keep-conf qbox-apollo-qvp-native -c populate_sysroot
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state \
  --out-dir build/i2s-drain-fix/final-runtime --timeout 1200 \
  --keep-running-after-pass -- \
  --platform-param platform.dma350_1.trace=true \
  --platform-param platform.dma350_1.trace_filter=operation \
  --platform-param platform.dma350_1.trace_limit=20000
```

실행 커널의 `/sys/kernel/notes`와 빌드한 vmlinux의 `.notes`는 byte 단위로
일치했다. 실행 프로세스의 module maps를 보존했고, 배포/빌드
`dw-apb-i2s.so`의 build-id는 모두
`caee551139fce103a052c1caca14cc30feb95812`이다. strip 때문에 두 파일의
전체 SHA-256은 다르며 동일 바이너리 파일이라고 주장하지 않는다.
최종 provider `do_check`는 platform 60개(5.40초), 선택 core 60개(18.79초)
모두 통과했다. 그 외 기존 제외 suite까지 실행한 것은 아니다.

최종 수정 커널+모델의 실제 Linux 결과:

| 조건 | 방향/횟수 | 결과 | 증거 |
| --- | --- | --- | --- |
| blocking, buffer 16384 | 각 방향 5회 | 10/10 PASS | `final-repeat/results.json` |
| 동시 duplex blocking, buffer 16384 | 각 방향 3회 | 5/6 PASS, 1회 시작 시 capture 0 frames/EIO | `final-duplex-{0to1,1to0}/results.json` |
| 동시 duplex `-N`, buffer 16384 | 각 방향 3회 | 6/6 PASS | `final-duplex-nonblock-{0to1,1to0}/results.json` |
| `-N`, buffer 2048 (2 periods) | 각 방향 3회 | 5/6 PASS, 1회 capture overrun | `final-two-period/results.json` |

PASS한 각 WAV는 196608 frames/192 periods 전부 일치했고 zero frame은 0,
aplay/arecord 종료 코드는 모두 0이다. 동시 blocking의 실패는 기록에서
제외하지 않는다. 비차단 I/O는 데이터 없는 capture 시작 구간의 kernel
blocking-read timeout을 피하기 위한 것이며, 종료 시 실제 프레임 부족은
계속 FAIL 판정한다. 따라서 모든 blocking 실행의 안정성을 주장하지 않는다.

소형 버퍼 실패(`final-two-period/02-0to1`)는 capture 로그에
`overrun!!!`, `state: XRUN`, `avail=2050`으로 기록되었다. 2048-frame
ring을 소비하는 속도보다 DMA가 앞섰으며, 첫 mismatch는 frame 175125였다.
이는 EOF의 마지막 두 프레임 유실과 달리 전송 도중 발생한 ALSA ring
overrun이다. arecord의 자동 복구 후에도 원본과 일치하지 않아 FAIL로
유지했다(194092 frames, zero 8, capture timeout 124). **2-period ring의
무손실 동작은 미달성**이다. 현재 4-CPU freerunning 구성에서 재현 가능한
사용 조건으로 period 1024 / buffer 16384 및 `--nonblock`을 권장한다.
모델이 ALSA ring을 몰래 늘리거나 overrun을 숨기도록 수정하지 않았다.

마지막으로 `scripts/run/ssh_run.sh scripts/test/verify_qbox_i2s.sh`를 같은
부팅에서 실행했다. 기존 Linux `i2s-loopback`의 양방향 및 동시 duplex
4개 stream 모두 각각 65536 frames 전체 일치, leading idle 0으로 PASS했다.
DMA 모드 및 DMA350 두 instance의 8-channel/non-coherent 구성도 통과했다.
로그는 `final-linux-regression.log`이다. WAV comparator의 원본 일치,
tail loss/중간 zero/다른 rate 거부 pytest 2개 및 Linux checkpatch
(0 errors/0 warnings)도 통과했다.
시험 후 이번 runner에 SIGINT를 보내 종료했다. 따라서 launcher의 최종
`result.json`은 `child_failed:130`이며 full-platform qualification PASS가
아니다. 여기의 I2S 판정은 실제 SSH 명령 종료 코드, WAV 비교와 DMA/IRQ
로그를 근거로 한다. 기존 검증기 실행 중 DMA350_1 IRQ는 8735→9127로
증가했다. 다른 subsystem의 전체 post-login 검증을 수행했다고 주장하지 않는다.

동시 duplex 재현 명령(다른 I2S 시험이 없는 상태에서 실행):

```sh
python3 scripts/test/validate_qbox_i2s_wav.py --nonblock \
  --out-dir build/i2s-drain-fix/final-duplex-nonblock-0to1 \
  --rounds 3 --direction 0to1 &
forward=$!
python3 scripts/test/validate_qbox_i2s_wav.py --nonblock \
  --out-dir build/i2s-drain-fix/final-duplex-nonblock-1to0 \
  --rounds 3 --direction 1to0 &
reverse=$!
wait "$forward"
wait "$reverse"
```

### 범위와 한계

검증은 Apollo의 `functional_pacing=true`, S16_LE stereo 48 kHz에 한한다.
모델의 `frame_period_ns`는 ALSA가 광고하는 임의 rate와 자동 연동되지 않는다.
고정 drain 시간은 clock이 동작하고 RX가 진행한다는 전제이며, 임의의 수신
정지/무한 backpressure까지 보장하지 않는다. IRQ-off drain 비용 및 timed
FIFO deadline, 물리 I2S timing은 별도 qualification 대상이다.

## 2026-09-15 aplay/arecord WAV 검증

QBox BSP를 새로 부팅하고 Linux SSH에서 ALSA-utils 1.2.13의 실제
`aplay`와 `arecord`를 별도 프로세스로 실행했다. 전용 i2s-loopback 검증기를
사용한 앞선 결과와 구분한다. 현재 모델의 functional_pacing=true는 유지했다.

네 PCM의 `--dump-hw-params`는 S16_LE/S24_LE/S32_LE, stereo,
8000~192000 Hz를 광고했다. 이번 데이터 검증은 **S16_LE, 48000 Hz,
stereo**만 수행했다. 광고된 다른 format/rate의 정상 동작이나 실제 wire
타이밍까지 확인한 것은 아니다. PCM frame은 2채널×16bit=4 bytes이다.

각 방향에 다른 비영 random pattern을 넣은 WAV를 생성했다.
196608 frames=786432 PCM bytes=192 periods=4.096초(설정 rate 기준)이며,
period 1024 / buffer 16384 frames를 사용했다. Capture RUNNING을 확인한 후
playback을 시작했다. WAV 헤더 차이를 제외하고 PCM 길이, 모든 프레임,
period별 zero-frame 수와 SHA-256을 호스트 Python wave 모듈로 비교했다.
offset 정렬, 앞/뒤 잘라내기 또는 짧은 prefix만으로 PASS하는 처리는 없다.

| 실행 | 방향 | 캡처 frames | aplay/arecord exit | 결과 |
| --- | --- | --- | --- | --- |
| 1 | I2S0→I2S1 | 195584 / 196608 | 0 / 1 | FAIL: 마지막 1024 frames 부족, arecord Input/output error |
| 1 | I2S1→I2S0 | 196608 / 196608 | 0 / 0 | PCM 전체 일치 |
| 2, 동일 조건 | I2S0→I2S1 | 196608 / 196608 | 0 / 0 | PCM 전체 일치 |
| 2, 동일 조건 | I2S1→I2S0 | 196608 / 196608 | 0 / 0 | PCM 전체 일치 |

모든 녹음에서 실제 기록된 PCM은 해당 원본 prefix와 정확히 일치했고,
zero frame은 0개였다. 따라서 초기 1~2 period 이후 전부 0으로 바뀌는 현상은
관측되지 않았다. 하지만 **종료 부근 마지막 period 누락이 1회 발생했으므로
aplay/arecord 경로의 안정성 검증은 FAIL**이다. 두 번째 실행 성공을 수정의
증거로 취급하지 않는다. EOF/drain/STOP과 capture 완료 사이의 경합은 후속
조사 대상이며, 이번 시험만으로 내부 원인을 확정하지 않았다. 모델/드라이버는
수정하지 않았다.

게스트 명령(역방향은 playback hw:1,0 / capture hw:0,1):

```sh
arecord -D hw:1,1 --dump-hw-params -v -t wav -f S16_LE -r 48000 -c 2 \
  --period-size=1024 --buffer-size=16384 -s 196608 0to1-capture.wav &
# /proc/asound/card1/pcm1c/sub0/status의 RUNNING 확인 후
aplay -D hw:0,0 --dump-hw-params -v --period-size=1024 --buffer-size=16384 0to1.wav
```

증거 디렉터리: `build/i2s-wav-20260915/`.
원본 WAV, 두 번째 capture WAV와 comparison.json, 명령별 로그를 보존했다.
첫 실행의 실패 WAV와 로그/비교 결과는 `trial1/`에 별도로 보존했다.
`wav_data.py`는 생성/비교 코드, `guest-test.sh`는 실제 실행 절차다.
`runtime/`에 부팅 로그가 있다. 배포 디스크 복사본으로 실행했고 시험 후
이번 runner만 종료했다.

## 2026-09-15 cyclic 재검증

현재 배포 BSP로 재부팅하여 I2S0→I2S1, I2S1→I2S0 모두 확인했다.
**처음 1~2 period 이후 capture가 전부 0으로 바뀌는 현상은 재현되지 않았다.**
이는 현재 Apollo의 `functional_pacing=true` 구성 결과이며, timed mode의
FIFO underrun/overrun deadline 검증은 아니다.

| 시험 | 방향 | period / buffer (frames) | 결과 |
| --- | --- | --- | --- |
| 배포 i2s-loopback | 0→1, 1→0 각각 | 1024 / 16384 | 각각 65536 frames 전체 일치 |
| 배포 i2s-loopback 동시 duplex | 두 방향 동시 | 1024 / 16384 | 양쪽 각각 65536 frames 전체 일치 |
| period 진단용 검증기 | 0→1, 1→0 각각 | 1024 / 16384 | 각각 period 1~64 전체 일치 |
| 작은 cyclic ring 진단 | 0→1, 1→0 각각 | 1024 / 2048 | 각각 period 1~64 전체 일치, 32 buffer 분량 |

형식은 S16_LE / stereo / 48 kHz, 각 실행은 262144 bytes다.
검증기는 payload 전체를 프레임별로 비교한다. 첫 payload 전 idle zero만
건너뛰며 payload 시작 후 zero/누락/순서 변경은 즉시 실패한다.
이번 모든 실행의 leading idle은 0이었다. 진단용 복사본에는 1024프레임마다
비교 완료 로그를 추가했고, 작은 ring 바이너리는 BUFFER만 2048로 바꿨다.
드라이버, 모델, 레시피 및 배포 검증기 소스는 수정하지 않았다.

DMA trace의 관측:

- `dma350_1` 채널 0~3 각각 256 DONE periods, period당 4096 bytes.
- 각 채널의 4회 stream은 순서대로 16/16/16/2-period 주소 ring을 사용했다.
  마지막 2-period ring도 첫 두 period에 멈추지 않고 64 periods 완료했다.
- FIFO 주소와 trigger는 위 토폴로지에 일치했다. error completion은 없었다.
  stream 종료 시 partial STOP은 정상이며, 이미 완료된 경계에서는 STOP trace가
  생략될 수 있어 STOP 개수만으로 실행 횟수를 계산하지 않았다.
- INTID390은 0→398(기본 시험)→693(추가 시험), INTID311과 I2S IRQ는 0 유지.
  shared IRQ 횟수를 DMA period 개수와 동일시하지 않는다.
- live DT에서 두 DMA는 각각 8채널, non-coherent이고 두 I2S에 dmas가 존재했다.
  Linux는 6.18.5-rt3-yocto-preempt-rt였다.

재현 및 증거는 `build/i2s-cyclic-recheck-20260915/`에 보존했다.

```sh
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state \
  --out-dir build/i2s-cyclic-recheck-20260915/runtime \
  --timeout 600 --keep-running-after-pass -- \
  --platform-param platform.dma350_1.trace=true \
  --platform-param platform.dma350_1.trace_filter=operation \
  --platform-param platform.dma350_1.trace_limit=4096
./scripts/run/ssh_run.sh scripts/test/verify_qbox_i2s.sh
# 진단 바이너리를 guest /tmp에 복사한 뒤:
./scripts/run/ssh_run.sh build/i2s-cyclic-recheck-20260915/period-tests.sh
python3 build/i2s-cyclic-recheck-20260915/analyze.py
```

`baseline.log`, `period-tests.log`, `summary.json`에 payload/period 결과,
`runtime/qbox-platform.log`에 실제 DMA trace가 있다. `artifacts.sha256`에는
사용 WIC, DMA/I2S 모델 및 진단 바이너리 해시를 기록했다. 진단 C 소스도 같은
디렉터리에 있다. 현재 배포 이미지는 20260912102855 qboxconf를 사용했다.
기존 build/conf의 기본 MACHINE은 apollo-fvp이므로 QVP를 명시해 실행했다.
배포 디스크는 복사하여 사용했고, 검증 종료 후 이번에 띄운 runner만 중지했다.

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

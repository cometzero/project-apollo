# I2S 소형 cyclic ring XRUN 후속 조사 (2026-09-15)

## 최신 검증 결과 (2026-09-16)

**실제 QBox/Linux의 일반 blocking WAV 전송은 양방향 각 10회, 총
20/20 PASS이다.** 디버거 없는 새 `reset-held-mcips/` 부팅에서 AP 4 CPUs,
all-domain MCIPS/100 µs, S16_LE stereo 48 kHz, period 1024/buffer 2048로
검증했다. RT 우선순위·CPU affinity·buffer 확대는 사용하지 않았다.

| 방향 | 반복 | 파일당 PCM | zero/XRUN | 케이스 시간 합산 |
| --- | --- | --- | --- | --- |
| I2S0 → I2S1 | 10/10 PASS | 196608 frames, 192 periods 전체 일치 | 0/0 | 270.347 s |
| I2S1 → I2S0 | 10/10 PASS | 196608 frames, 192 periods 전체 일치 | 0/0 | 270.877 s |

총 3932160 frames/3840 periods이며 PCM SHA256도 모두 일치했다.
케이스 시간 합산은 541.224 s(초기 SSH 준비 제외), 개별 26.642~27.372 s이다.
ALSA의 실제 negotiated geometry/avail_min도 요청값과 일치했다.
DMA350_1 HWIRQ 390은 0→5810으로 증가했고 검사 후 PCM 4개가 모두
closed였다. IRQ coalescing이 있으므로 IRQ 수를 period 수로 간주하지 않는다.

증거 루트는 `build/qbox-apollo-qvp/i2s-final/`이며 `reset-held-wav/results.json`,
각 WAV/ALSA 로그, `reset-held-preflight.log`, `reset-held-wav-after.log`에 있다.
커널 notes SHA256은 빌드 산출물과 일치한다. 최종 provider는 platform
61/61(6.72 s), selected core 62/62(19.34 s) PASS이며 설치 바이너리 해시는
`reset-held-artifacts.sha256`에 기록했다.

같은 부팅에서 추가로 확인한 결과:

- SPI0/1 DMA loopback, SPI2/3 PIO, UART0↔1, I2C0~5 EEPROM PIO,
  memcpy/memset 및 HWIRQ 311 공유 연결: PASS, host 49.90 s
  (`reset-held-dma-regression.log`). SPI timeout margin은 30000 ms로 검사 후 복구했다.
- Residue polled 검사: 64 KiB/2 MiB × memcpy/memset × 5회, 20/20 PASS,
  host 9.59 s (`reset-held-residue-verified.log`). 인자 순서가 잘못된 이전
  `reset-held-residue-regression.log`는 memset 근거에서 제외했다.
- DMA 회귀 후 196625-frame WAV(192 periods + 17 frames): 양방향 2/2 PASS,
  모든 PCM/hash 일치, zero/XRUN 0, 합산 54.661 s
  (`reset-held-wav-odd-tail/results.json`).

아래는 수정·실패·재시도의 시간순 기록이다. 일반 blocking의 최종 PASS를
별도 `-N` 소형 ring stress, 기본 QK 구성 또는 물리 실시간 보장으로 확대하지
않는다. 기존 실패 WAV와 QK post-sc_stop 종료 timeout도 삭제하거나 PASS로
바꾸지 않았다. 프로젝트의 기본 시간 설정은 변경하지 않았다.

최종 빌드의 `-N` 경계 검사도 FAIL이다. 16384-frame WAV, 동일
1024/2048 geometry, guest timeout 3 s에서 0→1은 12265 frames/zero 10/
RX overrun 2회, 1→0은 14348 frames/zero 27/TX underrun·RX overrun 각 1회였다
(`reset-held-wav-nonblock-boundary/results.json`, 합산 42.179 s).
이 결과를 일반 blocking의 PASS에 합치거나 timeout만 제거해 통과시키지
않는다. 앞서 trace로 확인한 partial I/O/fixed poll threshold 제한은 남아 있다.
동일한 16384-frame source WAV와 geometry/timeout의 blocking 대조군은
양방향 2/2 PASS, zero/XRUN 0, 합산 9.709 s였다
(`reset-held-wav-blocking-control/results.json`). `-N` 실패 이후에도 같은
VM에서 정상 blocking 전송이 가능했다.
최종 health 검사에서는 PCM 4개가 모두 closed, dmatest/spi_loopback_test
모듈이 제거되고 SPI timeout margin이 복구됐으며 SSH가 정상 응답했다
(`reset-held-final-health.log`).
짧은 blocking 대조군 이후에도 장치/module 정리를 재확인한 뒤
이번 검증용 VM 두 프로세스만 TERM으로 종료했다
(`reset-held-final-cleanup.log`). WAV·로그·바이너리 해시는 보존했다.

또한 최종 host boot log에는 85.509580 ms의 CCI originator/hierarchy 진단
1건이 남아 있다. 이후 부팅·트래픽은 위와 같이 통과했지만, 전체 플랫폼
로그가 무오류라는 판정은 아니다. QK teardown, 기본 QK 소형 ring,
CCI 초기화 진단은 이번 blocking I2S PASS와 별도 제한으로 유지한다.

## 범위

앞선 [EOF 수정과 WAV 검증](dw-apb-i2s.md)에 남았던 2-period ring의
중간 프레임 누락과 blocking capture 시작 EIO를 조사한다. 실제 Apollo QVP
Linux에서 ALSA-utils `aplay`/`arecord`를 사용하며, 모델 단위 테스트와 구분한다.
commit/push 또는 기존 외부 layer 변경은 수행하지 않는다.

증거 루트: `build/qbox-apollo-qvp/i2s-xrun/`.
S16_LE stereo 48 kHz, period 1024 / buffer 2048 frames,
WAV당 196608 frames(192 periods, ring 96회 분량)가 기본 비교 조건이다.
FIFO의 `functional_pacing=true`는 유지한다. silence padding, frame 정렬,
실패 제외 또는 buffer 확대를 PASS 조건으로 사용하지 않는다.

## 재현

기존 EOF 수정 커널/I2S 모델, AP 4 CPUs/MULTI/freerunning,
global quantum 10 ms로 새로 부팅했다. DMA operation trace를 끈 상태에서도
다음과 같이 실패하여 단순한 verbose DMA trace 부하 문제로 보지 않는다.

| 방향 | 결과 | 관측 |
| --- | --- | --- |
| 0→1 | PASS | 196608 frames 모두 일치 |
| 1→0 | FAIL | 189440 frames, 첫 mismatch 113667, playback underrun 1회 및 capture overrun 3회 |

근거: `baseline-two-period/results.json`, 각 case의 PCM 로그/WAV.
실패 재현 후 남은 반복을 중단했으므로 계획한 10회를 모두 수행한 것이 아니다.
`baseline/`에 부팅 로그가 있다. 기본 kernel/BSP를 다시 빌드하거나 buffer
크기를 변경한 비교가 아니다.

## 시간 경로 검토

- I2S의 serializer는 `dw-apb-i2s.cc::tx_thread()`에서 SystemC의
  `frame_period_ns`(20833 ns)를 기다린다.
- AP generic counter는 QEMU `target/arm/helper.c::gt_get_countervalue()`에서
  `QEMU_CLOCK_VIRTUAL`을 읽는다. 일반 TCG/비-icount/비-MCIPS 구성에서는
  `tcg_get_virtual_clock()` → `cpu_get_clock()` → host monotonic clock 경로다.
- QBox `cpu.h`는 이 QEMU clock을 quantum keeper에 샘플링한다. Freerunning도
  실행 중인 keeper의 샘플 시각보다 SystemC가 앞서지 못하도록 한다.
  `multithread-quantum`은 반대 방향인 CPU의 선행도 제한한다.
- CPU의 quantum 대기는 VM clock 자체를 멈추지 않는다. 따라서 quantum을
  100 μs로 줄이는 것만으로 live QEMU clock과 SystemC의 차이가 항상
  100 μs 이내가 된다고 주장할 수 없다. 이 경로는 bursty 실행 가능성의
  설명이지, 그 자체로 해당 XRUN의 원인을 확정하는 측정은 아니다.

비교용 boot에 다음 두 override를 적용했다:

```text
--platform-param platform.ap_qemu_inst.sync_policy=multithread-quantum
--platform-param platform.quantum_ns=100000
```

`bounded/` 실행은 360초 동안 AP primary console이 비어 있었고 Linux SSH에
도달하지 못했다. 최종 runner blocker는 `child_keep_running_timeout`,
SI CL1 로그에는 PFDI monitor timeout이 기록되었다. **부팅 FAIL/오디오 미실행**으로
분류하며, 원인이 규명된 대체 runtime profile로 채택하지 않는다.

## DMA-350 MMIO 시간 처리 수정

`dma350::access()`는 입력 delay를 무시하고 register를 즉시 읽거나 썼다.
CH_CMD enable은 asynchronous worker를 시작하므로, CPU local time을
annotated delay로 전달하는 QBox initiator와 조합하면 미래의 command가
SystemC의 현재 시점에 실행될 수 있었다. 반대로 미래 시점의 status read가
과거 snapshot을 반환할 수 있었다. I2S FIFO STOP에 적용한 시간 처리가
DMA register 경로에도 필요했다.

`dma350::b_transport()`에 nonzero 입력 delay를 소비하고 0으로 돌리는
6줄을 추가했다. 이후 기존 validation/access를 수행한다. `transport_dbg()`는
변경하지 않아 debugger 접근은 기다리지 않으며 channel command를 실행하지 않는다.
DMA ring 크기, Linux arm-dma350 driver, rate 및 IRQ 연결은 변경하지 않았다.

추가 단위 테스트는 +10 ns ENABLE, +12 ns status read를 동시 발행한다.
5 ns에는 memory write/IRQ/command가 아직 없어야 하고, 이후 정상 전송과
DONE snapshot이 보여야 한다. 수정 전에는 timing/state assertion 10개가
실패했고 수정 후 DMA 관련 CTest 2개가 통과했다. debug command의
nonblocking/no-execution 특성도 검사했다.
증거: `dma350-timing-{before,after}-{build,test}.log`.

## 검사기 강화

`scripts/test/validate_qbox_i2s_wav.py`는 WAV가 우연히 일치하더라도
`overrun!!!`, `underrun!!!`, `state: XRUN`, PCM read/write error가 로그에
남으면 FAIL로 판정한다. 자동 XRUN recovery를 정상 무손실 전송으로 세지 않는다.
이 조건의 pytest 회귀 테스트를 추가했다.

Blocking capture는 상대 TX가 아직 시작되지 않아 입력 데이터가 없는 경우
`wait_for_avail()`의 최소 100 ms 제한에 도달할 수 있다. 기존 `--nonblock`
옵션은 ALSA-utils의 EAGAIN/poll 경로로 이 시작 대기를 처리하며, 전체 실행
제한과 정확한 프레임 수 검사는 그대로 유지한다. kernel의 timeout을 무조건
늘리거나 EIO를 무시하도록 수정하지 않는다.

## 수정 후 실제 Linux 회귀와 실패 분석

`dma-fixed/`는 수정한 DMA 모델로 재부팅한 guest다. SSH port는 8023이며,
kernel notes는 앞선 EOF 수정 kernel과 일치한다. `dma-fixed-module-maps.txt`와
`dma-fixed-module-sha256.txt`에 실행 모듈의 경로와 hash를 기록했다.

| 실행 디렉터리 | 조건 | 결과 |
| --- | --- | --- |
| `dma-fixed-default-buffer/` | 16384-frame buffer, 양방향 2 rounds | **4/4 PASS**, 각 196608 frames/192 periods 일치, zero frame/XRUN 없음 |
| `dma-fixed-two-period/` | 2048-frame buffer | 첫 완료 case FAIL, 183296 frames, 첫 mismatch 4128 |
| `dma-fixed-rt-clean/` | 2048-frame buffer, SCHED_FIFO 40 | FAIL, 135184 frames, 첫 mismatch 2048 |
| `avail-one/` | 2048-frame buffer, avail_min 1 frame | FAIL, 76900 frames, 첫 mismatch 2048 |
| `avail-half-period/` | 2048-frame buffer, avail_min 512 frames | FAIL, 78848 frames, 첫 mismatch 1509 |
| `pcm-traced/` | 2048-frame buffer, kprobe 진단 | FAIL, 190719 frames, 첫 mismatch 2099 |

모두 nonblocking PCM I/O다. 작은 buffer의 실패를 큰 buffer PASS로 대체하지 않는다.
`dma-fixed-two-period/`는 첫 완료 실패 이후 중단했으며 미수집 case는 검증 횟수에
포함하지 않는다. `dma-fixed-rt/`는 이전 capture와 중첩된 무효 trial이다.
이후 검사기에 PCM closed 상태 검사를 추가했고 `dma-fixed-rt-clean/`에서 독점 실행했다.
RT 진단의 `chrt`는 동일 Yocto util-linux 빌드 산출물을 임시 guest에 복사했다.
현재 BSP가 이를 기본 제공한다는 뜻은 아니다. RT 우선순위나 작은 avail_min을
해결책으로 채택하지 않았다.

### PCM pointer 추적

현재 kernel의 DWARF offset(`pcm-offsets.log`)으로 `snd_pcm_update_hw_ptr0`,
`snd_dmaengine_pcm_pointer`, `snd_pcm_update_state`, `__snd_pcm_xrun`에
전용 trace instance의 kprobe를 설정했다. 진단 이후 tracing/event를 껐다.
`pcm-trace.log`, `pcm-trace-live.log`는 실제 pointer 상태를 기록한다.
추적 부하가 있으므로 이 case는 성능 qualification이 아니다.

- 첫 playback IRQ 시 `hw_ptr=1024`, `appl_ptr=2099`였다. 앞선 partial write
  때문에 free space가 973 frames로 기본 `avail_min=1024`보다 작았다.
  다음 IRQ 후 pointer가 2144까지 진행하여 2099를 초과했고 underrun이 발생했다.
  첫 capture mismatch 위치 2099와 일치한다. 다만 avail_min을 낮춘 두 비교도
  실패하므로 이것만을 전체 XRUN의 단일 원인으로 단정하지 않는다.
- capture 실패 예에서는 base가 108544로 유지된 채 `hw_ptr=109691`,
  `appl_ptr=107520`이 되어 차이가 **2171 > 2048**이었다. 이 사례는 ALSA의
  가짜 wrap 한 번만으로 설명되는 것이 아니라 실제 ring 서비스 지연이다.
- callback/pointer 처리 사이에 여러 ms의 지연이 관측된다. QEMU clock과
  SystemC 시간의 관계 및 guest scheduling을 추가 검토해야 한다.

### 다른 DMA 사용자 회귀

`dma-fixed-peripheral-regression.log`의 `verify_qbox_dma350.sh`는 result=0이다.
8 dedicated channels/shared IRQ topology, memcpy/memset 각각 5회,
SPI0/1 DMA 및 SPI2/3 PIO의 64/4099-byte 전송, UART0↔1의
17/128/512/4099-byte 전송을 통과했다. I2C0~5 PIO EEPROM도 검사하고 복원했다.
SPI timeout margin은 30000 ms다.

`dma-fixed-peripheral-analysis.json`은 guest 결과와 QBox DMA operation trace를
대조하여 PASS를 기록한다. 총 333 operations 중 memory 10개,
SPI0/1의 각 TX/RX 66544 bytes가 확인되었다. UART의 짧은 tail은 기존 PIO
경로이므로 DMA byte 수만으로 전체 전송량을 판단하지 않는다.

provider `populate_sysroot`는 성공했고(`provider-build.log`), recipe check는
platform 60/60(5.46초), selected core 60/60(18.67초)였다(`provider-check.log`).
이 결과는 DMA MMIO 시간 처리 수정의 회귀 근거이지 2-period XRUN 해결 증거가 아니다.

## Freerunning quantum 비교

`free-100us/`는 sync policy를 모두 기존 freerunning으로 유지하고
`--platform-param platform.quantum_ns=100000`만 변경했다. Linux/SSH 부팅은
성공했지만 `free-100us-two-period/results.json`의 첫 0→1 case는 FAIL이다.
121930 frames, 첫 mismatch 5120, zero frames 797 및 양쪽 XRUN이 기록되었다.
실패 후 반복을 중단했다. 이 override는 기본 플랫폼에 반영하지 않았다.

AP만 `time_sync_strategy=mcips`, `tcg_mode=MULTI`, quantum 100 μs로 바꾼
`mcips-100us/`도 비교했다. 설치 provider에는 없는 `libidlinker.so`를 동일
Yocto libqemu build의 `qemu-prefix/lib`에서 `LD_LIBRARY_PATH`로 제공한
진단 전용 구성이다. 실제 process maps에서 이 라이브러리의 load를 확인했다.
약 150초 관찰 동안 AP console은 0 bytes였고 Linux에 도달하지 못해 수동
중단했다(설정한 360초 timeout까지 기다린 결과가 아님). RSE는 BL_33 측정,
SI CL1은 40 ms 부근의 PFDI/network 초기화 로그까지 있었다.
**부팅 미완료/오디오 미실행**이며 MCIPS를 정상 대체 profile로 채택하지 않는다.

### 재현 명령

기본 runtime은 다음과 같이 띄웠다. launcher에 표시되는 실제 SSH port를
검사기에 전달해야 한다. 다른 VM/PCM 테스트와 겹치지 않게 실행한다.

```sh
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state \
  --out-dir build/qbox-apollo-qvp/i2s-xrun/REPRO \
  --timeout 900 --keep-running-after-pass

python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-xrun/REPRO-wav \
  --port 8022 --buffer 2048 --rounds 5 --fail-fast
```

16384-frame 회귀는 `--buffer 16384 --rounds 2`를 사용했다.
검사기의 기본은 nonblocking이며 blocking 진단은 `--blocking`으로 지정한다.
timeout/중단된 launcher의 자식 VM이 남을 수 있으므로 종료 후 해당 runner의
정확한 자식 PID와 SSH listen port가 사라졌는지도 확인했다.

## 현재 판정과 남은 작업

- **수정/검증 완료:** DMA MMIO annotated-time ordering 결함, 대응 단위 테스트,
  provider check 및 memory/SPI/UART 회귀. EOF 수정 후 큰 buffer WAV도
  실제 Linux 양방향 4/4로 재확인했다.
- **미해결:** 2048-frame ring의 중간 XRUN/프레임 누락. FIFO 전체가 1~2 periods
  이후 영구적으로 0이 되는 현상과 동일시하지 않는다. 실패 WAV의 zero 수와
  첫 mismatch를 그대로 보존했다.
- **시작 대기:** nonblocking capture로 상대 TX의 시작을 기다리도록 검사기를
  기본 설정했다. 이는 no-data blocking timeout에 대한 테스트 절차 선택이며
  kernel blocking EIO 동작 자체를 수정한 것은 아니다.
- 다음 구현 대상은 AP/QEMU clock과 SystemC 진행의 동기화 및 period IRQ부터
  실제 userspace 서비스까지의 지연이다. 작은 ring 실패를 이유로 residue를
  허위 보고하거나 DMA를 ALSA appl_ptr에 종속시키는 모델은 적용하지 않았다.
  MCIPS/bounded의 부팅 미완료도 먼저 분리 진단해야 한다.

검사기 pytest 3/3 및 root/platform/Linux의 `git diff --check`가 통과했다.
이번 단계에서 추가 Linux driver 변경, commit, push는 하지 않았다.

## 추가 조사: MMIO dispatch와 period 서비스

후속 실행 증거는 `build/qbox-apollo-qvp/i2s-service/`에 저장한다.
기존 kernel/이미지와 기본 freerunning/10 ms quantum을 유지했다.

### 서로 다른 PCM I/O 모드

검사기에 `--blocking-playback`을 추가하여 capture는 nonblocking으로 시작하되
playback은 blocking write를 사용하도록 분리했다. `mixed-io/`의 첫 0→1은
playback XRUN 없이 capture overrun으로 FAIL(182272 frames, 첫 mismatch
4587)했다. 다음 `mixed-io-traced/`는 trace 설정 실패로 실제 추적은 없었으며,
playback underrun/EIO도 발생했다. 즉 첫 case의 playback 오류 부재를
일반적인 해결로 주장하지 않는다. 이 옵션은 진단용이며 기본값을 바꾸지 않았다.

### 실제 period 서비스 추적

`scripts/test/trace_qbox_i2s_period.sh`는 guest에 별도 trace instance와 고유
kprobe group을 생성하고 종료 시 자기 event/instance만 제거한다.
최적화된 kernel에서 `d350_program_cmd.isra.0`도 찾아 사용하며, 이 함수의
변경될 수 있는 인자 ABI는 해석하지 않고 진입/반환 시간만 기록한다.
`analyze_qbox_i2s_period.py`는 PID별로 entry/exit를 짝짓고 불완전한 쌍도
명시한다. 시간 분석은 WAV PASS 판정과 독립이다.

`baseline-period-trace2.log`는 859/859 entries를 수집했다. 같은 실행의
`mixed-io-traced2/`는 FAIL이며 추적 부하를 포함한 진단 결과다.

| 구간 | 표본 수 | median | p95 | max |
| --- | --- | --- | --- | --- |
| `d350_irq` 진입→반환 | 268 | 0.362 ms | 15.325 ms | 38.937 ms |
| `d350_program_cmd` 진입→반환 | 111 | 0.307 ms | 0.665 ms | 40.671 ms |

IRQ 함수 호출에는 shared line의 비활성 channel 검사도 포함된다.
program 호출 111회와 callback 101회만으로 callback 누락 수를 계산하지 않는다.
초기 설정/stop/error도 있으므로 channel별 완료와 대조해야 한다.
그럼에도 1024/48000 = 21.333 ms의 한 period보다 긴 서비스 지연이 실측되었다.

소스상 cyclic은 hardware command-link가 아니라 매 period의 software rearm이다.
`d350_irq`는 `vc.lock`을 잡고 ACK, next command 선택 및 약 13회 register
write를 수행한다. callback tasklet과 tx_status도 같은 lock을 잡으므로
새 command와 이전 XSIZE가 섞인 snapshot은 확인되지 않았다. 반면 callback은
이 MMIO 설정이 끝날 때까지 기다려야 한다. 이 단계에서는 driver를 변경하지 않았다.

### QBox core 시간 전달 수정

`QemuInitiatorSocket::do_regular_access()`는 QEMU thread에서 얻은 상대 delay를
`run_on_sysc` queue에 그대로 넘겼다. dispatch까지 SystemC 시간이 진행하면
delay를 소비하는 target이 이미 지난 시간까지 다시 기다릴 수 있었다.
반환 이후 keeper에 offset을 반영하는 경로에도 같은 timestamp 문제가 있었다.

실제 경로에서 사용하는 `gs::timed_dispatch` helper로 다음 순서를 보장한다.

1. 기존 CPU-thread 시간 샘플은 유지한다. QEMU icount는 `current_cpu`가 있는
   thread에서 실행 instruction 수를 먼저 반영해야 한다.
2. SystemC callback 안에서 상대 delay를 다시 얻은 후 `b_transport`를 호출한다.
3. callback이 반환하기 전에 남은 delay를 keeper에 반영한다.

이는 원래 요청의 절대 시각을 보존하는 API가 아니라 **실제 처리 시점의
virtual clock**을 샘플링하는 방식이다. debug/direct 접근은 변경하지 않았다.
현재 non-CPU initiator의 기존 local-time 구현을 별도로 고치는 범위도 아니다.

`timed_dispatch_test`는 dispatch 전 5 ns와 반환 후 7 ns의 kernel 진행을
주입하고 wait하는 target과 delay만 annotate하는 target을 모두 검사한다.
수정 전 12개 assertion FAIL, 수정 후 새 테스트와 keeper 회귀 4/4 PASS(1.05초).
로그는 앞선 증거 루트 `i2s-xrun/timed-dispatch-{before,after}-{build,test}.log`다.
이 단위 테스트 결과만으로 Linux XRUN이 해결되었다고 판정하지 않는다.

### 수정한 provider의 Linux 결과

`provider-build.log`의 905 tasks가 성공했다. `provider-check.log`는
platform 60/60(6.51초), selected core 61/61(18.79초)이며 새 timing test도
포함된다. `dispatch-fixed/`로 새로 부팅했고 kernel notes는 이전 실행과
일치한다. 실행 모듈 maps/hash와 DTB/WIC/AP flash hash를 같은 증거 루트의
`dispatch-fixed-module-*`, `guest-artifacts.sha256`에 저장했다.

| 실행 | 2048-frame buffer 결과 |
| --- | --- |
| `dispatch-fixed-two-period/` | 0→1 FAIL, 188416 frames, 첫 mismatch 2096, 양쪽 XRUN |
| `dispatch-fixed-mixed/` | blocking TX/nonblocking RX, 0→1 FAIL, 193536 frames, 첫 mismatch 1171, capture overrun 1회 |
| `dispatch-fixed-mixed-half/` | 위 조건에 avail_min 512, 0→1 FAIL, 193536 frames, 첫 mismatch 22528, capture overrun 1회 |
| `dispatch-fixed-traced/` | blocking TX/nonblocking RX, 1→0 FAIL, 191286 frames, 첫 mismatch 68928, capture overrun 2회 |

모두 첫 완료 실패 후 멈춘 실행이며 요청한 반복 횟수를 완료하지 않았다.
앞 세 실행에는 kprobe를 켜지 않았다. 마지막 실행은 별도 trace instance로
측정했고 종료 시 instance/event가 제거되었다.

`fixed-period-trace.log`와 `fixed-period-summary.json`의 관측은 다음과 같다.

| 구간 | 표본 수 | median | p95 | max |
| --- | --- | --- | --- | --- |
| IRQ 진입→반환 | 940 | 0.636 ms | 1.538 ms | 5.498 ms |
| 주기 재설정 진입→반환 | 385 | 0.248 ms | 0.624 ms | 6.804 ms |

entry/exit의 unmatched 수는 모두 0이다. 수정 전 실행과 방향/진행 길이가
다르며 두 trace 모두 instrumentation 부하를 포함한다. 이 수치를 엄밀한
동일 조건 A/B 성능 향상률로 환산하지 않는다. 수정 후 관측된 긴 꼬리 지연은
줄었지만 작은 ring XRUN이 없어졌다는 뜻은 아니다.

`dispatch-fixed-mixed-one/`에서 blocking playback + avail_min 1 frame도
추가 확인했다. 0→1의 capture overrun 3회로 FAIL(189440 frames, 첫 mismatch
16797)했다. 따라서 작은 poll 임계값을 일반적인 해결책으로 채택하지 않는다.

반면 `dispatch-fixed-default-buffer/`의 16384-frame buffer / 1024-frame
period는 **양방향 3 rounds, 6/6 PASS**다. 매 case 196608 frames / 192 periods의
PCM 전체와 hash가 일치했고 zero frames/XRUN/PCM 오류가 없다. 추적은 끈
실행이며, 큰 buffer PASS와 작은 buffer FAIL을 서로 대체하지 않는다.

현재 추가 수정의 확정 범위는 QBox MMIO dispatch의 stale offset 결함이다.
2048-frame ring의 무손실 동작은 아직 완료되지 않았다. 나머지 과제는
period callback→userspace 소비 지연 및 시간원 간 관계의 분리 검증이다.
host-clock 기반 freerunning을 사용하면서 모든 host scheduling 조건의
real-time deadline을 보장한다고 주장하지 않는다. buffer/period 제한을
driver에 추가하거나 XRUN을 무시하는 변경은 하지 않았다.

### 공통 MMIO 변경의 peripheral 회귀

같은 guest에서 다음을 순차 수행했다. I2S test와 겹치지 않았고,
`dma350_0` operation trace만 활성화했다(I2S의 `_1` trace는 비활성).

```sh
QBOX_SSH_PORT=8022 timeout 420 ./scripts/run/ssh_run.sh \
  scripts/test/verify_qbox_dma350.sh
python3 scripts/test/validate_qbox_dma350.py \
  --guest-log build/qbox-apollo-qvp/i2s-service/peripheral-regression.log \
  --qbox-log build/qbox-apollo-qvp/i2s-service/dispatch-fixed/qbox-platform.log \
  --output build/qbox-apollo-qvp/i2s-service/peripheral-analysis.json
```

guest result=0, trace 비교 PASS(errors 없음)다. memory operations 10회,
SPI0/1의 각 TX/RX 66544 bytes 및 UART0↔1의
17/128/512/4099-byte 통신이 검증되었다. UART tail의 일부 PIO 처리는 유지된다.
I2C0~5 EEPROM PIO(복원 포함), SPI2/3 PIO, shared IRQ 검사도 PASS다.
SPI는 기존 30000 ms timeout margin을 유지했다.

root Python tests는 5/5, shell syntax 및 소유 repository별 diff whitespace
검사도 PASS다. 검증 VM은 종료했고, 이번 후속 단계에 kernel 변경이나
commit/push는 추가하지 않았다. launcher의 login 결과는 전체 플랫폼
post-login qualification과 구분하며 여기의 PASS는 위 명시한 검사에 한정한다.

## 추가 수정: 짧은 DMA count의 residue 조회

다음 단계의 증거 루트는 `build/qbox-apollo-qvp/i2s-final/`이다.
`full-pcm-trace.log`의 8788/8788 entries를 DMA-350 operation trace와
대조했다. 최초 capture XRUN에서 `hw_ptr=10240`, `appl_ptr=8192`였다.
처리된 IRQ/rearm 9회와 아직 IRQ 처리 전인 완료 period 1회, 모델의
4096-byte RX 완료 10회가 모두 일치한다. 이 실패는 가짜 ALSA wrap이나
descriptor 주소 오류가 아니라 실제 unread ring이 가득 찬 경우다.
세부 계산은 `full-pcm-findings.md`, `full-pcm-analysis.json`에 보존했다.

이때 이전 application chunk의 64-frame tail을 읽는 pointer 조회에
10.444 ms가 걸리고, 이어지는 새 chunk의 pointer 조회에 15.560 ms가
걸렸다. 그 사이 소비한 것은 64 frames뿐이었다. 각 조회는
`d350_get_residue()`에서 XSIZEHI/XSIZE/XSIZEHI를 읽으며 대부분의 시간을
보냈다. 단순히 IRQ callback이 누락됐다는 설명과는 다르다.

Linux `arm-dma350.c`의 수정은 다음 한 가지 최적화다.

- 현재 command의 `xsizehi == 0`이면 XSIZE만 한 번 읽는다.
- 큰 count는 기존 high/low/high 일관성 검사와 재시도를 그대로 사용한다.

TRM의 [XSIZE](../dma-350/0123-CH_XSIZE.md),
[XSIZEHI](../dma-350/0124-CH_XSIZEHI.md)는 단순한 상·하위 count이다.
현재 driver의 finite 1D command는 count가 감소하며, CH_LINKADDR는 0이고
`vc.lock`이 다음 software command 재설정을 막는다. 따라서 초기 상위
count가 0이면 조회 중 다시 증가할 수 없다. 0을 65536으로 해석하는 특수
encoding도 아니다. 이 조건을 이용한 일반적인 MMIO 감소이며 QBox 전용
분기, cached/fabricated residue, period 정렬 강제 또는 XRUN 무시는 없다.
앞선 I2S EOF 수정도 보존했다.

`checkpatch` 오류/경고 0 및 diff whitespace 검사를 통과했다.
2 MiB transfer의 polled dmatest를 별도로 실행하여 큰 count 경로도 검사한다.
128-bit transfer라면 count=131072로 high=2이며, 단순 callback 완료만 확인하는
test와 달리 `polled=1`은 실행 중 `device_tx_status`를 호출한다.

실제 새 kernel의 `/sys/kernel/notes`와 빌드한 vmlinux의 `.notes`를
비교해 일치를 확인했다. `scripts/test/verify_qbox_dma350_residue.sh`로
64 KiB/2 MiB, 두 mode 각각 5회를 실행했으나, 후속 검토에서 최초 스크립트가
channel을 type보다 먼저 지정해 **mode 1도 실제로는 copy0**를 실행했음을
확인했다. `i2s-final/short-residue-polled.log`는 memset 근거로 사용하지 않는다.
모델 trace에도
channel 4 XSIZEHI (`0x1424`)의 nonzero read가 있어 큰 count 조회 경로를
실행했음을 확인했지만, 이는 당시 memcpy 경로의 증거이다.
최종 스크립트는 type/size/polled 설정 후 channel을 지정하고 실제
`copy0`/`set0` summary 및 sysfs 설정을 검사한다. 이 수정 후 실제 새 QVP에서
64 KiB/2 MiB × memcpy/memset × 5회, 총 20/20 PASS를 확인했다
(`i2s-final/reset-held-residue-verified.log`, host 9.59 s).

그러나 이 최적화만으로 2-period WAV 문제는 해결되지 않았다.
`short-residue-mixed-one/`은 190464 frames만 캡처했고 첫 불일치는
92179번 frame이었다. capture overrun 1회가 기록됐다. CPU/IRQ를 CPU0에
고정한 `short-residue-cpu0/`도 FAIL이므로 affinity는 해결책으로 채택하지
않았다. IRQ affinity는 원래 `0-3`으로 복구했다.

## 추가 원인: timed MMIO job의 전역 suspend 우회

실제 provider의 SystemC `sc_simcontext::next_time()`은
`m_unsuspendable > 0`이면 다른 initiator가 설정한 suspend barrier도
무시하고 timed event를 진행한다. 기존 `runonsysc::jobs_handler()`는
job 전체를 `sc_unsuspendable()`로 감쌌다. 따라서 target이
`b_transport()`에서 annotated delay를 기다리는 동안 I2S는 진행하지만
다른 CPU의 시간 제한은 보호되지 않는 경로가 있었다.

QBox core에 job별 `Suspension::Respect` 정책을 추가하고 regular QEMU
MMIO만 opt-in했다. control/debug 등의 기존 job 기본 동작과 deferred IRQ의
zero-time drain은 유지했다. 단위 테스트는 다른 initiator의 barrier가
유효한 동안 100 ns target wait가 완료되지 않는지 검사한다.
수정 전 FAIL, 수정 후 새 테스트 및 keeper/timed-dispatch 회귀 5/5 PASS다.
로그는 `i2s-final/runonsysc-{before,after}-{build,test}.log`에 있다.
이 결과는 단위 수준이며, 이 수정의 실제 Linux WAV 효과는 별도 runtime
검증 결과로 판단해야 한다.

Yocto provider 재빌드/배포는 905 tasks 성공, platform 60/60 (6.69 s),
선택 core 62/62 (19.31 s) PASS였다. `respect-suspension-build.log`,
`respect-suspension-provider-check.log`에 기록했다.

하지만 기본 10 ms quantum의 실제 WAV는 3072 frames 이후 playback
`EIO`로 중단됐다 (`respect-mixed-one/`). `respect-pcm-trace.log`에서는
각 MMIO 약 10–20 ms, DMA command 재설정 약 150 ms가 관찰됐다.
Linux `wait_for_avail()`의 작은 buffer 기본 대기는 최소 100 ms이다.
Respect 정책은 이전의 전역 barrier 우회를 막지만, 다른 keeper의
`deadline_timer_cb`가 clock을 갱신하는 coarse cadence를 노출한다.
이 결과를 runtime 수정 완료로 분류하지 않는다.

모든 instance에 적용되는 global quantum을 100 us로 낮춘
`respect-100us-wav/`에서는 195584 frames (191 periods)가 정확히 일치했고
XRUN은 없었지만, 마지막 chunk가 완성되지 않아 arecord가 timeout했다.
이는 파일에 기록된 단위이며 실제로 1024 frames 전부가 전송되지 않았다고
단정할 수 없다. 함수 추적을 켠 `respect-100us-traced-wav/`는 instrumentation
지연으로 중간 XRUN을 보였고, DMA register trace만 켠
`respect-100us-dmaonly-wav/`도 27648 frames 후 playback EIO와 capture XRUN이
발생했다. 따라서 100 us 구성 역시 안정적인 해결책으로 채택하지 않았다.

`respect-10us/`는 global quantum 10 us, trace 없는 구성이다.
RSE와 TF-A를 거쳐 U-Boot의 `EFI: MM partition ID 0x8006`까지 진행했지만
Linux/SSH에 도달하지 못한 상태에서 해당 검증 VM을 종료했다. SI의 AP
PFDI timeout 경고도 보존했다. 이 구성은 오디오 미실행이며, quantum을
더 작게 만드는 것만으로 해결됐다고 판단하지 않는다.

## MCIPS 후속 확인

`respect-mcips-debug/`, `mcips-pending-debug/`는 AP만 MCIPS로 바꾼
혼합 clock 구성의 bounded host GDB 관찰이다. 배포/빌드 host ELF의
Build ID를 확인한 뒤 연결했다. 두 번째 세션에서 실제 `platform.ap_cpu_0`의
BL2 `mhu_v3_x_doorbell_read()`가 AP↔RSE MHU `0x40681fe0`를 반복 읽는
것을 확인했다. Pending/INCOMPLETE → 완료/OK → 다음 read가 관찰됐고
MCIPS clock도 23.100 → 23.177 → 23.265 s로 진행했다. 따라서 이 snapshot을
영구적인 MMIO deadlock 또는 async notification 손실의 증거로 쓰지 않는다.
RSE 응답 polling과 혼합 wallclock/instruction-clock domain의 느린 진행은
남아 있는 별도 문제다. GDB detach 후 해당 VM과 남은 child를 종료했다.

별도의 실제 AArch64 CPU 단위 재현에서는 quantum 100 us에 대해
target이 400 us를 기다리면 CPU와 target이 모두 완료하지 못하는 경로를
확인했다 (`mcips-mmio-before-test.log`). 이는 위 boot snapshot과 구분되는
동기식 timed TLM/MCIPS window 문제다. 단순히 모든 SystemC barrier를
무시하는 방식 대신, MMIO 대기 중인 CPU의 instruction-clock 실행 상태를
명시적으로 관리하는 수정과 회귀 테스트를 진행한다.

또한 QEMU CMake wrapper는 `libidlinker`를 Windows에만 설치하고 있었다.
POSIX libdir에도 설치하도록 바꾸고 native recipe의 필수 산출물 검사에
추가했다. MCIPS 실행이 임시 build-tree `LD_LIBRARY_PATH`에 의존하지 않도록
하기 위한 설치 수정이며, 실제 설치 및 runtime 확인은 별도로 수행한다.

MCIPS 동기식 MMIO 수정은 다음 상태 전이를 사용한다.

- QEMU thread/BQL: 공용 I/O lock을 기다리기 **전** 현재 instruction count를
  반영하고 해당 CPU를 `TLM_WAIT`로 둔다. 대기 CPU는 active/slowest CPU
  선택에서 제외한다. 다른 CPU가 없으면 해당 instance의 window만 연다.
- SystemC target 완료: 반환 annotated delay까지 포함한 완료 시점으로
  `TLM_READY`와 window를 복원한다. future를 깨우기 전에 복원하므로 host
  thread 복귀가 늦어도 장치 시간이 무제한 앞서지 않는다. 여기서는 QEMU
  resume API를 호출하지 않는다.
- QEMU thread/BQL 복귀: `RUNNING`으로 되돌리고 필요한 MCIPS pause를 해제한다.
  일반 halt/reset/debug 동작이나 ALSA pointer에 오디오 전용 처리를 넣지 않는다.

실제 AArch64 CPU 테스트에서 1/2 CPU × target wait/annotated-only의 4가지가
각각 통과했다. quantum 100 us, target delay 400 us이며 CPU host return을
20 ms 늦춰도 completion-to-resume은 예약한 quantum 이내였다.
다음 MMIO가 annotated completion보다 일찍 발생하지 않는지도 검사했다.
단순 target 완료뿐 아니라 CPU의 두 번째 store를 확인한다.

단, 반복 검사 전체는 PASS가 아니다. 앞선 18회는 process exit 0이었지만
19번째 2-CPU/wait 실행은 모든 전송·CPU 재개 assertion을 통과한 뒤
`sc_stop` 이후 종료가 멈춰 outer timeout exit 124였다.
`mcips-mmio-repeat-summary.log`와 `mcips-mmio-repeat-5-2cpu-false.log`에
실패를 보존했다. 이 MCIPS 검사들은 기존 `QBOX_ENABLE_MCIPS_TESTS` opt-in
아래에 두고, 기본 native selected suite에 추가하지 않았다. 실행 중 동작과
프로세스 종료 안정성은 구분한다.

### 최종 provider 빌드와 RSE 인스턴스 확인

MCIPS CPU handoff에서 instruction counter를 두 번 읽던 부분은 한 번의
snapshot으로 바꿨다. 두 read 사이에 실행된 instruction을 중복 반영할 수
있기 때문이다. 수정 후 실제 CPU 4가지 조합은 모두 process exit 0이었다
(`mcips-mmio-snapshot-summary.log`). 앞선 teardown timeout 기록은 유지한다.
최종 native provider 빌드에서는 platform 60/60, 선택 core 62/62가 통과했다
(`mcips-snapshot-provider-check.log`). POSIX `libidlinker.so` 설치도 확인했다.

`all-mcips-pre-snapshot/`, `all-mcips/`, `all-mcips-debug/`는 이름과 달리
모든 CPU에 MCIPS가 적용된 검사가 아니었다. 실제 RSE CPU는 outer
`platform.qemu_inst`가 아니라 `platform.rse_cpu_pass.qemu_inst` 소속이다.
GDB에서 `platform.rse_cpu_pass.cpu_0.cpu`의 Quantum keeper가 남아 있음을
확인했다. 따라서 이 실행의 AP 부팅 지연을 전체 MCIPS 구성의 실패 증거로
사용하지 않는다. `nested-all-mcips/`에서는 nested instance의
`time_sync_strategy=mcips`, `tcg_mode=MULTI`까지 명시했고, monitor에서 해당
plugin과 CPU 1개가 실제 등록된 것을 확인했다. Linux 및 WAV 결과는 별도
검증 대상이며 인스턴스 설정 확인만으로 오디오 PASS를 판단하지 않는다.

`nested-all-mcips/`는 RSE에서 BL33 측정까지 진행했으나 AP 보조 CPU1의
power ON/OFF 검사 뒤 진행이 느려졌다. SI0 로그의 OFF 시점은 약 443.554 ms,
monitor의 CPU1은 RUNNING, instruction delta 0, CPU time 443.651 ms로
남았다. 다른 CPU들은 약 447 ms에서 PAUSED였고 watchdog 수준으로만
시간이 진행했다 (`mcips-stalled-status.json`). Linux 오디오는 미실행이다.

확인한 소스 경로는 QEMU sleep loop의 idle 알림과 MCIPS pause의 중첩이다.
QEMU는 sleep loop 진입 시 idle callback을 한 번 호출한다. MCIPS PAUSED
상태에서는 이를 무시한다. 이후 scheduler pause가 해제되어도 WFI/halt가
남으면 같은 sleep loop에 머물러 idle callback이 다시 오지 않는다.
MCIPS에서는 실제로 쉬는 CPU가 RUNNING으로 남아 다른 CPU의 진행을 막을
수 있다. MCIPS CPU에도 기존 libqemu end-of-loop callback을 등록하여,
vCPU thread/BQL 안에서 실행 불가능 상태를 idle로 재확인하도록 수정했다.
QEMU ABI, CPU 전원 상태 또는 Linux 드라이버로 우회하지 않는다. 이 변경의
회귀 검사와 최종 WAV 검증은 별도로 수행한다.

`mcips-pause-wfi-test.cc`는 2개 AArch64 CPU, quantum 100 ns에서 CPU1이
128 NOP와 WFI를 포함하는 TB를 실행하도록 구성한다. 기존 경로(callback
비활성 진단)는 374 ns에서 CPU0 진행이 멈추고 host watchdog으로 exit 1,
수정 경로는 약 10.179 us에서 CPU0가 완료되어 exit 0이었다
(`mcips-pause-wfi-128-summary.log`). 최초 새 callback에서는 진행 완료 후
종료 시 detached window 갱신 abort 134도 관찰했다. callback을 기존
`LibQemuPlugin::dispatch_userdata`의 in-flight drain에 포함시켜 shutdown이
window를 해제하기 전에 완료를 기다리도록 보완했다. 이후 WFI 검사 10/10,
timed-MMIO 4/4가 모두 exit 0이었다 (`mcips-pause-wfi-bridge-summary.log`,
`mcips-mmio-bridge-summary.log`). 초기 실패 로그를 삭제하거나 PASS로
재분류하지 않았다.

2026-09-16 00:00 KST에 idle 보정까지 포함한 native provider의 빌드·설치를
완료했다. Yocto 905 tasks 중 900 cached, 전체 성공이며 platform 60/60
(6.59 s), 선택 core 62/62 (19.40 s)였다. 로그는
`mcips-idle-provider-build.log`, `mcips-idle-provider-check.log`, 주요 artifact
해시는 `mcips-idle-artifacts.sha256`에 보존했다. 실제 부팅 재검사는
`idle-fixed-mcips/`에서 수행한다.

### 전체 MCIPS 부팅에서 확인한 PPU OFF 순서 문제

`idle-fixed-mcips/`에서 AP1은 실제 IDLE로 유지되고 시간이 약 3 s까지
진행했다. 그러나 보안 콘솔은 BL31 PFDI의 `OoR tests on core 1 succeeded`
이후 멈췄다. `idle-fixed-debug/host-gdb.log`의 guest stack은 AP0가
`plat_pfdi_pe_init` → `wait_cpu_off` → `udelay`를 반복함을 보인다. 두 관찰에서
타이머와 delay 시작값이 바뀌었으므로 timer freeze가 아니다. AP1은
halted=1, stopped=false, PC=0x82000으로 reset 상태였고, RSE는 PSA wait
경로였다. RSE의 마지막 BL33 측정 로그를 실행 중 crypto 작업으로 해석했던
추정은 폐기한다. CPU1 software affinity 값 자체는 이 GDB에서 확인하지
못했으며 ON으로 직접 읽었다고 주장하지 않는다.

소스상 TF-A `lib/psci/psci_off.c`는 `pwr_domain_off()`를 호출한 **뒤**
affinity OFF와 cache 정리를 수행하고 WFI로 간다. 기존 `host_ppu`는 OFF
요청 즉시 AP CPU reset을 assert하므로 이 마무리 명령을 중단할 수 있었다.
SCP의 AP core power-domain 요청은 강제 asynchronous이며 SCMI 응답을 먼저
보낸 후 PPU 상태를 polling한다. 따라서 PWPR write는 즉시 반환하되 실제
PWSR OFF/reset은 CPU standby까지 미루는 것이 필요하다.

AP core PPU에 opt-in `power_off_wait_for_standby`와 CPU `standby_wfi`
연결을 추가하는 수정은 이 순서를 보완한다. OFF 요청 중에는 PWPR=OFF,
PWSR=ON을 유지하고 architectural standby 확인 후 OFF/reset을 완료한다.
일반 cold reset은 계속 즉시 처리하며, 취소된 OFF 요청이나 reset 이전
pending 요청은 나중의 standby에 의해 완료되면 안 된다. 이는 functional
power-down handshake이며 PPU 전체 Q/P-channel 또는 물리 전력 timing
모델의 완전한 구현을 의미하지 않는다. TF-A firmware는 변경하지 않는다.

진단상 주의: 현재 monitor의 `/transport_dbg/<addr>/<name>` 구현은 addr를
사용하지 않고 offset 0을 읽는다. 따라서 이 API로 제안했던 DMA/affinity의
비영점 offset 조회는 증거로 사용하지 않는다. 해당 monitor는 이번 변경
범위에서 수정하지 않았다.

PPU 기존/새 standby 단위 테스트는 3/3 통과했다
(`standby-ppu-final.log`). 첫 새 테스트는 기본 power-on delay 1 ns와
`sc_start(1 ns)`의 경계에서 아직 완료되지 않은 상태를 검사했다. Apollo와
같이 power-on delay 0으로 명시하여 OFF handshake 검사를 분리했다.

실제 CPU standby 검사에서는 MCIPS의 WFI 상태가 0x08, QK의 WFI 상태가
0x0c였다. QK가 `sync_with_kernel()`에서 사용하는 soft-stopped bit는
architectural WFI를 부정하지 않는다. 이 bit만 standby 제외 mask에서
제거하며, reset/init/external halt는 별도 상태로, stop/stopped 및 pending
work/IRQ는 계속 검사한다. 초기 QK 실패를 단순한 관찰 순서 문제로 봤던
추정은 실제 0x0c 확인으로 정정했다.

QK 검사에는 기능 assertion 통과 후 process 종료 timeout 124가 남았다.
재부팅 WFI 이후로 종료 위치를 옮긴 경우도 발생했으므로 단순히 MMIO 안의
`sc_stop()`만이 원인이라고 단정하지 않는다. 해당 검사는 불안정한 opt-in
진단으로 유지하고, 기본 selected suite의 PASS에 포함시키지 않는다.
`standby-repeat-summary.log` 등 초기 실패 기록은 보존한다.
후속 bounded parent-GDB에서는 CPU thread가 이미 종료된 뒤 QEMU iothread가
`qemu_cleanup` → `vm_shutdown` → `pause_all_vcpus`의 condition wait에 남고,
main이 LibQemu destructor에서 iothread join을 기다리는 것을 확인했다
(`standby-qk-shutdown-parent-gdb.log`). 이 snapshot에 진행 중인 SystemC/TLM
transport는 없었다. QEMU teardown 수정으로 범위를 확대하지 않는다.

최종 좁은 검사는 MCIPS standby 5/5, timed-MMIO 4/4, pause/WFI 1/1 모두
exit 0, PPU 3/3 PASS였다. CPU standby의 IRQ wakeup, external halt,
reset/reboot를 검사하며 scheduler pause를 standby로 오인하지 않는지도
확인한다. 로그는 `standby-mcips-final-1.log`부터 `standby-mcips-final-5.log` 등 검사
산출물에 보존한다. Lua·RSE/CL1 isolation·SRAM retention 관련 기존 Python
검사 22개도 통과했다 (`standby-root-regression.log`, 1.30 s). 정적 full-map
검사도 PASS이며 이 결과는 실제 Linux 부팅/오디오 통과와 구분한다.
각 process exit는 `standby-final-exit-summary.log`, CPU 신호 계약과
재현 명령은 `cpu-standby-wfi-proof.md`에 별도로 기록했다.

00:38 KST의 standby 수정 provider 빌드·설치도 성공했다. platform 61/61
(6.60 s), 선택 core 62/62 (19.41 s), 전체 Yocto 905 tasks 성공이다
(`standby-provider-build.log`, `standby-provider-check.log`). 실제 실행은
`standby-fixed-mcips/`, 주요 CPU/PPU module 포함 해시는
`standby-fixed-artifacts.sha256`에 보존한다.

### Standby 수정 후 실제 부팅 재검사

`standby-fixed-mcips/`에서는 PFDI core 1~3 검사, OP-TEE normal-world
handoff, U-Boot와 Linux 4 CPU 부팅을 통과하고 initramfs selftest와 DHCP까지
진행했다. 이전 core 1 OFF 이후 정지는 재현되지 않았다. 단, launcher의
600초 제한을 넘겨 `result.json`은 `child_keep_running_timeout` 실패이다.
계속 실행 중인 VM의 뒤늦은 부팅 진행을 launcher PASS로 바꾸지 않는다.
PPU trace limit에 도달해 OFF handshake의 해당 trace는 없으므로 실제 순서의
직접 증거는 standby 단위 테스트와 구분한다.

이 실행은 모든 실제 CPU instance를 MCIPS 1 GIPS, quantum 100 us로 설정했다.
RSE CPU가 시간을 진행시키는 동안 AP/SI0는 quota pause로 기다린다. 네트워크
초기화 이후에는 `/init`의 RSA SSH host-key 생성이 남아 있다. RSE의 기존
`psa_wait` PC만으로 busy-loop/IRQ storm을 단정할 수 없으며, 실제 TF-M idle
thread에는 `DSB; WFI`가 존재한다.

추가로 MCIPS quota가 quantum의 ns 값을 instruction 개수로 사용하는 기존
제약을 확인했다. 이는 1 GIPS에서만 같은 시간 폭이며, 다른 instruction
rate의 timing 정확성을 이 검사로 보장하지 않는다. 따라서 이 실행 중
instruction rate를 변경하거나 timer를 우회하지 않았다.

WAV runner의 `--host-timeout`은 이제 setup SSH와 SCP에도 적용한다. 실행
중 host timeout이면 `host_timeout_guest_cleanup_required` 실패와 guest
경로를 남기고 즉시 종료하며, 이전 PCM process가 살아 있을 수 있으므로
다음 case를 겹쳐 시작하지 않는다. case별 실제 elapsed time도 기록한다.
해당 timeout 증거 보존 검사 포함 Python 검사 6/6 PASS (0.27 s).

01시 재검사에서 SSH 및 `NEXIOS_BSP_INITRAMFS_READY`를 확인했다. 두 I2S
카드와 양쪽 TX/RX PCM node를 확인한 뒤 실제 `aplay`/`arecord`를 수행했다.

- `standby-fixed-wav/`: 1024/2048 frame, S16_LE/48 kHz/stereo, capture
  nonblocking, playback blocking, `avail-min-frames=1`. **FAIL**: 첫 불일치
  6,160 frame, 캡처 XRUN 9회, zero frame 0. 반복 XRUN 확인 후 해당 guest
  작업 경로를 확인하여 PID 241/246만 TERM 종료했다. 종료 시 캡처 88,202
  frame이며, 중단된 전체 frame 수는 자연 종료 검사의 결과가 아니다.
  원본 로그·중단 명령·PCM 파일과 JSON을 보존한다. elapsed 390.82 s.
- `standby-mcips-default-traced/`: 같은 ring/format에 ALSA 기본 avail_min을
  사용한 16,384 frame 진단은 **PASS**: 16 period 전체 PCM SHA-256 일치,
  zero/XRUN 0, 양 process exit 0, elapsed 117.86 s. trace를 켠 짧은 실행이므로
  192-period 반복/최종 timing qualification을 대체하지 않는다.

검증기는 양쪽 verbose log에서 실제 negotiated format/rate/channels와
period/buffer 크기도 읽는다. ALSA의 `*_size_near()`가 다른 ring 크기를
선택하거나 setup 증거가 없으면 실패한다. 요청값 2048/실제값 4096을
거부하는 회귀 검사도 추가했다. `--guest-timeout`은 게스트 clock 기준
deadline이며 기본 45 s, `--host-timeout`과 별개로 기록한다.

### Cortex-M idle 동작 수정

libqemu의 기존 commit `d238858bff60a`는 M-profile event register를 항상
`arm_cpu_has_work()`의 wake 조건으로 포함했다. WFI도 이 조건을 사용하므로
SVC/exception return/SEV 이후 인터럽트가 없어도 halt하지 않는 문제가 있다.
또한 M-profile WFE helper가 MTTCG의 `CF_PARALLEL` 조건에 의해 호출되지
않았다. 실제 Cortex-M55/NVIC와 별도 Thumb firmware에서 두 실패를 재현했다.

QEMU `target/arm`에서 WFI/WFE wait-kind를 구분하고, event는 WFE일 때만
wake 조건으로 사용한다. WFI가 event register 자체를 지우지는 않는다.
M-profile WFE는 MTTCG에서도 helper를 호출하며 A/R 정책은 유지한다.
wait-kind는 reset 영역 및 optional migration subsection에 포함한다.
TF-M firmware, timer 주파수, audio pointer는 변경하지 않는다.

실제 M55 회귀 5/5와 기존 AArch64 timed-MMIO 4/4는 모두 exit 0이다.
증거·명령·이전 실패·SO 해시는 `m55-wfx-proof.md`와 관련 로그에 남겼다.
전체 WFE corner case를 수정한 것은 아니다. 이미 sleep한 WFE가 event로
깨어난 이후의 기존 event 소비 시점은 그대로이며, 회귀 firmware는 추가
WFE로 이를 소비한다. reset/migration runtime 검증도 별도 범위이다.

기존 VM의 짧은 진단 trace는 694/694 entries를 수집했다
(`standby-mcips-pcm-trace.log`). SSH trace cleanup이 아직 끝나지 않은 상태에서
새 libqemu 설치를 위해 해당 VM을 TERM 종료했다. 이 trace는 데이터 수집
증거이며 trace process 정상 종료 PASS로 취급하지 않는다. PCM process는
그 전에 양쪽 모두 `closed`임을 확인했다.

### WFI 수정 provider의 실제 Linux 결과

`m55-wfx-provider-build.log`: Yocto 905 tasks 중 896 cached, 전체 성공.
platform 61/61 (6.53 s), selected core 62/62 (19.40 s). 설치 산출물 해시는
`m55-wfx-artifacts.sha256`, check 로그는 `m55-wfx-provider-check.log`에 있다.
`m55-wfx-mcips/`는 약 3분 내 Linux/SSH 준비에 도달했으며 launcher
`passed=true`, `verdict=pass`이다. RSE 실제 CPU가 IDLE 상태로 바뀐 것도
monitor에서 확인했다. post-login qualification을 자동 수행한 것은 아니다.
guest `/sys/kernel/notes` SHA-256은 기존 빌드 notes와 일치했다
(`m55-wfx-guest-preflight.log`).

| 실행 | 실제 결과 |
| --- | --- |
| `m55-wfx-wav-blocking/` 0→1 | 196,608 frame/192 period 전체 WAV·PCM hash 일치, zero/XRUN 0, aplay/arecord exit 0. 다중 SCP 수집이 멈춰 전체 runner는 copy 실패로 유지. 단일 SCP 재수집 성공 로그 별도 보존 |
| `m55-wfx-wav-repeat/` 첫 case | TX 시작 전 blocking arecord가 no-data EIO, `WAV_CAPTURE_NOT_RUNNING`. 데이터 전송 PASS가 아님 |
| `m55-wfx-wav-nonblock/` 첫 case | 기본 avail_min, N capture/blocking playback. TX 정상 종료, RX XRUN 3회. 189,440 frame, 첫 불일치 9,231, zero 0. **FAIL** |

모든 case의 실제 negotiated ring은 1024/2048 frame이었다. nonblocking
캡처의 중간 hw_ptr 33,691은 XRUN 재시작 이후의 위치다. 이를 TX가 그
프레임에서 오류 종료한 것으로 처음 해석했으나, 최종 TX exit/log로 정정했다.

수집기는 `[ac]*` 단일 remote glob으로 capture.wav와 aplay/arecord log를
한 SCP session에서 가져온다. host source.wav는 덮어쓰지 않는다. 초기
준비 확인은 builtin read와 1 ms yield로 바꾸어 외부 grep 반복을 제거했다.
8개 Python 검사 PASS. `avail_min=1`은 기본값과 다르지만 유효한 stress
조건이며, 기존 XRUN을 무효 검사로 분류하지 않는다. ALSA-utils와 kernel은
실제 반환/복사한 frame 수만큼 포인터를 갱신한다. partial-read 재진입마다
HW pointer/DMA MMIO가 발생하는 차이는 있으나 이것만으로 원인을 확정하지
않는다.

후속 상세 trace 준비는 `ring_buffer_resize+0x6d8`에 대기했다. 실제 vmlinux
대조 결과 per-CPU `update_pages_work`의 `wait_for_completion()` 구간이며
메모리 할당 대기가 아니다. 대상 CPU는 기존 stack만으로 특정할 수 없다.
`m55-wfx-trace-setup-stack.log`에 보존했다. 이후 VM의 900 s 실행 수명이
끝나 연결이 종료되어 `m55-wfx-full-pcm-trace.log`는 유효한 수집 결과가 아니다.

### Pending IRQ wake의 시간 진행 재현

실제 A53이 WFI로 idle한 뒤 native IRQ를 입력하고, BQL을 가진 host thread가
20 ms 후 CPU 재개를 허용하는 독립 회귀에서 SystemC 시간이 약 747 ms
진행했다. 설정 quantum은 100 us였다. 추가 3회도 710.975/741.832/762.350 ms
진행하여 모두 정상 process exit 1의 **FAIL**이었다
(`mcips-irq-wake-before.log` 및 repeat 로그).
따라서 idle sync window 해제 이후 IRQ가 들어왔지만 native vCPU resume
callback 이전인 구간의 시간 제한이 빠진 결함은 오디오와 독립적으로
재현됐다. Linux frame-loss 해결 판정은 해당 수정 후 실제 traffic을 다시
수행해야 한다.

실패 WAV를 frame 단위로 정렬한 결과, XRUN에 해당하는 누락 구간 외에
2 frame 및 5 frame의 치환 구간이 있었다. 7 frame 모두 좌우 샘플이 정확히
원본의 **+2048 frame** 위치와 일치한다. 예를 들어 원본 25,689 frame 대신
27,737 frame, 원본 115,804 frame 대신 117,852 frame이 캡처됐다.
이는 임의 bit 오류/채널 혼선이 아니라 한 ring 뒤 데이터로 덮인 패턴이다.
`m55-wfx-nonblock-frame-gaps.json`,
`m55-wfx-nonblock-replaced-frames.jsonl`에 실제 위치와 샘플을 보존했다.
IRQ wake 수정이 이 현상을 없애는지는 후속 실제 WAV 검사로 판단한다.

### Pending IRQ wake 수정과 집중 회귀

MCIPS에 `WAKE_PENDING` 상태를 추가했다. IDLE CPU에 native kick이 전달되면
그 시각에 sync window를 예약하고, 실제 vCPU resume 또는 no-work idle
acknowledgement까지 유지한다. 반복 kick은 최초 제한 시각을 뒤로 미루지
않는다. QEMU의 LIBQEMU kick callback은 halt condition broadcast보다 먼저
실행하여 CPU acknowledgement와 reservation의 순서를 보장한다.
callback은 기존 PluginHandle drain에 참여하며, 초기화 전 CPU slot을
접근하지 않도록 per-vCPU initialized 검사도 수행한다.

최종 회귀는 IRQ 주입 자체를 SystemC process의 동일 timestamp에서 수행한다.
동일 binary에서 이전 kick 동작을 선택하면 IRQ/no-work kick 후 각각
1,530,682/1,587,402 us 진행하여 실패한다. 수정 후 1 CPU와 2 CPU 각각
5회, 총 **10/10 PASS**이며 두 구간 모두 정확히 100 us 이내이다.
2 CPU 검사는 peer의 실제 10M instruction 진행도 확인한다. 기존 timed-MMIO
4/4, M55 WFI/WFE 1/1, pause/WFI 1/1도 정상 exit 0으로 통과했다.
초기 foreign-thread timestamp 측정의 125/122 us 실패 로그는 유지하고,
assertion을 완화하지 않은 최종 SC timestamp 기준 검사와 구분한다.

재현 명령과 상세 계약은 generated evidence의 `mcips-irq-wake-proof.md`,
각 process exit와 소요 시간은 `mcips-irq-wake-exits.json`에 보존했다.
이는 generic scheduling 결함의 집중 회귀 결과이며 Linux WAV 반복 검증을
대신하지 않는다. 설치 빌드는 `irq-wake-provider-build.log`로 진행한다.

해당 설치 빌드는 905 tasks 중 896 cached, 전체 성공했다. platform 61/61
(6.60 s), selected core 62/62 (19.41 s)이다. 경고 1건은 과거 forced
`do_check`의 taint 안내이며 테스트 실패가 아니다. 해시와 check 로그는
`irq-wake-artifacts.sha256`, `irq-wake-provider-check.log`에 보존했다.

첫 전체 부팅 `irq-wake-mcips/`는 AP 초기 상태에서 진행하지 못했다.
SI0의 AP power-on 뒤 AP 전체가 MCIPS IDLE로 남고 secondary PFDI timeout이
발생했다. 약 5분 관찰 후 해당 VM만 TERM 종료했다. 원인은 이 snapshot만으로
확정하지 않는다 (`irq-wake-boot-stall-status.json`).

같은 설정의 `irq-wake-debug/` 재실행은 U-Boot까지 진행했다. 이때 host GDB를
한 차례 정지/분리했으므로 무개입 부팅 검증과 구분한다. 이후 Linux ITS 초기화
중 SC time 3.959164197 s에서 정지했다. monitor에서 AP CPU2는
`WAKE_PENDING`이지만 실제 instruction counter가 11 billion 이상으로
증가하는 상태였다. 연속 snapshot
`irq-wake-debug-pending-running-{1,2}.json`에 보존했다.

이는 native resume notification이 없는 실제 실행 경로를 pending 상태 처리에
포함하지 못한 결함의 증거다. QEMU는 sleep loop에서 실제 잠든 경우에만
resume callback을 발행한다. reset/work 처리 등으로 sleep 없이 실행을
재개하면 기존 quota callback은 RUNNING 이외 상태를 무시하여 instruction
counter만 증가하고 시간 제한은 해제되지 않는다. 이 실행은 WAV 테스트까지
도달하지 않았으며 **FAIL**이다. 실제 TB quota 도달을 실행의 근거로 pending
상태를 정상 retirement 경로에 연결하는 후속 수정과 회귀를 진행한다.

독립 실제 A53 회귀에서도 resume notification 하나만 생략하고 DMI RAM을
polling하면 같은 상태가 재현됐다. `mcips-missed-resume-before.log`에는
SC 1419 us, native state 0x20 (실행 중), PC 0x14, pending 상태의
160,266,403 instruction delta가 기록됐다. watchdog이 기능 실패를
기록했으며 종료도 완료되지 않아 최종 shell exit는 124이다. 이를 정상
종료의 FAIL로 바꾸어 기록하지 않는다. 별도 long-idle/reset 20 rounds는
기존 코드에서 완료되어 첫 AP 초기 정지의 독립 재현 증거로 사용할 수 없다.

후속 수정은 기존 quota callback에서 WAKE_PENDING도 받아들이고, mutex
내에서 실제 TB 실행이 확인된 상태를 RUNNING으로 전환한 뒤 기존 delta
retirement를 수행한다. 예약 시각을 현재 host 시각으로 옮기지 않으며
IDLE/PAUSED/TLM 상태 처리와 native pause 호출 문맥은 변경하지 않는다.

동일 알림 누락 회귀는 수정 후 5/5 정상 exit 0으로 통과했다. reset 해제
20회(초기 실행을 포함한 21 rounds), 일반 IRQ 1/2 CPU, timed-MMIO 4종,
M55 WFI/WFE, pause/WFI도 모두 exit 0이다. 상세 재현과 종료 코드는
`mcips-missed-resume-proof.md`, `mcips-missed-resume-exits.json`에 있다.
이를 반영하는 설치 빌드는 `quota-wake-provider-build.log`이다.

이 빌드의 첫 `do_check`는 platform 61/61, core 61/62로 실패했다.
`aarch64-managed-timer-wfi-baseline`에서 `Simulation stopped by user` 이후
30 s timeout이 발생했다 (`quota-wake-provider-check-failed.log`). 같은
A53/quantum_keeper 테스트를 변경 없이 반복한 결과 5/5 PASS, 각각 약
2.52 s, 총 12.59 s였다 (`quota-wake-unit-baseline-repeat5.log`). 최초
실패를 삭제하지 않으며 간헐적인 post-sc_stop 종료 문제로 남긴다. 현재
로그만으로 정확한 종료 대기 지점은 확정할 수 없어 제외/timeout 증가/코드
변경을 적용하지 않았다.

입력을 바꾸지 않은 provider 재실행은 platform 61/61 (5.61 s), core
62/62 (19.11 s), 설치까지 성공했다. 905 tasks 중 902 cached였다.
`quota-wake-provider-retry.log`, `quota-wake-provider-check.log`,
`quota-wake-artifacts.sha256`에 결과와 설치 산출물을 보존했다.

`quota-wake-mcips/`의 무개입 일반 부팅은 AP PFDI, Linux, network/dropbear,
`NEXIOS_BSP_INITRAMFS_READY`까지 진행했다. 그러나 첫 SSH는 banner timeout으로
실패했다. 이후 SC 8.291118958 s에서 진행이 멈춘 것을 확인했다.
`quota-wake-login-stall.json`에서 AP CPU0~2는 PAUSED, active CPU3는
RUNNING이나 instruction delta 0이며 진행하지 않았다. 앞선 executing-pending
현상과는 상태가 다르다. launcher login PASS가 SSH/오디오 qualification을
보장하지 않는 실제 사례이며 WAV 검사는 아직 시작하지 않았다.
해당 VM을 종료하고 `quota-wake-debug/`에서 native stop/halt 상태와 대기
thread를 관찰하기 위한 별도 debugger 실행을 시작했다.

`quota-wake-debug/` 재실행은 SSH까지 진행했다. 초기 debugger의 solib 처리
오류를 바로잡은 뒤, 오디오 검사 중 첫 정지 snapshot까지 debugger로
멈추거나 guest 상태를 바꾸지 않았다. kernel notes SHA도 일치하고 두 I2S
카드와 모든 PCM의 초기 closed 상태를 확인했다
(`quota-wake-debug-preflight.log`).

`quota-wake-debug-wav-blocking/` 첫 0→1은 196608 frame/192 period 전체
PCM hash 일치, zero/XRUN 0, 실제 1024/2048 geometry, process/copy exit 0,
27.320 s로 통과했다. 그러나 다음 1→0에서 SSH가 응답하지 않았고 monitor의
AP CPU1/2는 IDLE인데 instruction delta가 각각 수 billion으로 증가했다.
`quota-wake-debug-idle-running-{1,2}.json`에 연속 상태를 저장한 뒤 host
GDB로 정지하여 분석했다. 1→0은 host timeout 180 s로 실패했다
(case elapsed 181.717 s, `host_timeout_guest_cleanup_required`). 정지 후
debugger 개입이 있으므로 이 timeout의 시간 자체는 무개입 성능 지표가
아니다. 양방향 반복 전체 결과는 **FAIL**, 이후 cases는 수행하지 않았다.

같은 정지 상태의 host GDB에서도 AP CPU들이 실제 TCG 실행 중이며
native `halted=0`, `stop=false`, `stopped=false`인데 MCIPS active CPU가
없는 것을 확인했다. 따라서 monitor의 비동기 snapshot 차이만으로 생긴
표시 문제는 아니다. 기존 sleep-loop resume notification만으로 실행 상태를
추적하지 않고, 실제 native execution-entry에서 MCIPS를 동기화하는 후속
수정이 필요하다. 이때 IDLE은 window/base를 재연결하고, WAKE_PENDING은
이미 예약한 시각을 유지해야 하므로 단순히 두 상태를 RUNNING으로 바꾸는
quota fallback만으로 대체하지 않는다.

동일 ELF 대조 결과 AP CPU1/2의 PC 0x11034, CPU3의 PC 0x1101c는 BL31
`scmi_send_sync_command` 내부이다. CPU1/2/3의 실제 instruction delta는
각각 약 5.29G/2.41G/526M인데 plugin은 IDLE이었다. CPU0는 실제 stopped
상태였다. 이는 Linux 실행 중 CPU idle/power 전환의 firmware 경로도
관련됨을 보여준다. SI0의 native 상태는 해당 snapshot에 포함하지 못했으므로
SCMI 상대방이 응답하지 않는 구체적 이유까지 이 자료만으로 단정하지 않는다.
snapshot을 마친 뒤 이 실패 VM만 종료했다.

### Native execution-entry lifecycle 보완

libqemu에 전용 per-CPU execution-entry callback을 추가했다. MTTCG/RR 모두
BQL을 가진 상태에서 실제 TCG 진입 직전에 호출하고, callback 이후
`cpu_can_run()`을 다시 검사한다. QBox MCIPS는 이를 기존 resume 상태
전환에 연결한다. 기존 plugin의 paired idle/resume 알림은 바꾸지 않는다.
callback 등록 해제와 plugin drain을 기존 lifetime 정리에 포함했다.
새 export가 있으므로 새 QBox와 이전 libqemu를 혼용하지 않는다.

실제 A53의 queued IRQ/work 경로에서 paired resume notification 하나를
테스트 조건으로 생략하고 DMI memory를 polling하는 회귀를 추가했다.
동일 binary에서 execution-entry callback만 비활성화하면 IDLE/active=-1,
delta 2,850,715로 실패하고 exit 1이다. callback 활성화 시 5/5 정상
exit 0이며 실제 실행 시간 계산이 재개된다. 불필요한 kick 억제로 후속
검사를 방해했던 초기 테스트 로그도 별도로 남겼다. 자연 발생 결함의
근거는 앞선 live GDB이고, 이 회귀는 명시적 알림 누락 계약을 고정한다.

기존 pending-quota fallback도 entry callback을 비활성화한 상태에서
통과했다. IRQ, reset, timed-MMIO, M55, pause/WFI와 RR 5 CPU shutdown을
포함한 집중 검사 12/12 PASS, 약 7.20 s이다. 종료 코드는
`exec-entry-exits.log`, 실제 GDB 근거는 `exec-entry-live-proof.md`에 있다.
이 조합의 설치 빌드는 `exec-entry-provider-build.log`로 진행한다.
초기 RUNNING/delta=0 정지의 native stop 경쟁 가설은 이 snapshot으로
확정되지 않았으며, 별도 해결됐다고 주장하지 않는다.

### Execution-entry 수정 provider의 실제 Linux 검사

`exec-entry-provider-build.log`: 905 tasks 중 896 cached, 전체 성공.
platform 61/61 (6.73 s), selected core 62/62 (19.31 s).
`exec-entry-provider-check.log`, `exec-entry-artifacts.sha256`에 보존했다.
`exec-entry-mcips/`는 debugger 없이 일반 launcher로 부팅했고 SSH도
성공했다. kernel notes SHA는 기존 빌드와 일치한다
(`exec-entry-guest-preflight.log`). timing override는 앞선 all-domain
MCIPS/100 us/각 CPU 1GIPS 조건 그대로이며, CPU 수·DMA ring은 늘리지 않았다.

`exec-entry-wav-blocking/`: S16_LE stereo 48 kHz, period 1024/buffer 2048,
196608 frames를 방향별 3회씩, **6/6 PASS**. 모든 case에서 전체 PCM hash와
192 period가 일치하고 zero/XRUN 0, aplay/arecord/SCP exit 0이다.
각 case wall time은 28.303/27.830/93.046/27.616/27.844/27.702 s이다.
93.046 s case는 PCM 양쪽이 exit 0으로 끝난 뒤 SCP 수집이 지연됐다.
이때 별도 SSH가 응답하는 것을 확인했고 최종 수집도 정상 완료했다.
지연 원인은 확정하지 않으며 오디오 실행 시간으로 취급하지 않는다.

DMA350_1 shared HWIRQ 390은 초기 0에서 이 batch 뒤 1743으로 증가했다
(`exec-entry-blocking-after.log`). shared IRQ의 coalescing 때문에 handler
횟수를 TX/RX period callback 개수와 동일하다고 가정하지 않는다.
nonblocking 모드 및 추가 DMA 회귀는 별도 검사로 이어서 수행한다.

### Nonblocking partial I/O의 별도 XRUN 조건

`exec-entry-wav-nonblock/`의 첫 0→1은 192515 frame, 최초 불일치 4112,
zero 38, TX underrun 2/RX overrun 2로 **FAIL**이다. VM/CPU 시간 정지는
없었다. 이 실패를 blocking의 정상 결과로 덮어쓰지 않는다.

`exec-entry-pcm-trace.log`는 1055줄을 수집하고 정상 exit 0으로 정리했다.
계측한 16384-frame 전송은 캡처 14351, 최초 불일치 1043, zero 45로
실패했다. 실제 pointer와 wakeup 순서는 다음과 같다(단위: frame).

| 경로 | Partial I/O 이후 | 첫 IRQ의 실제 가용량 | 다음 IRQ 이후 |
| --- | --- | --- | --- |
| TX | 16을 일부 쓰고 appl=2064 | hw=1039 → 빈 공간 1023 < avail_min 1024 | hw=2060에야 write 재개, 재조회 hw=2068 > appl → underrun |
| RX | 19를 일부 읽고 appl=1043 | hw=2064 → 읽을 양 1021 < avail_min 1024 | hw=3088에야 wake, 재조회 hw=3097 → 2054 > buffer 2048 → overrun |

Trace TX 54–55/65/111–121, RX 97–101/132/186–195행이 근거다.
RX 최초 불일치 1043은 XRUN 전에 소비한 누적 frame 수와 일치한다.
RX hw 2064→3088→3097에서 base=2048은 그대로여서, 이 초기 실패를
잘못된 DMA ring wrap으로 설명할 근거는 없다.

로컬 alsa-utils 1.2.13의 `pcm_write()/pcm_read()`는 nonblocking partial
I/O 뒤 `snd_pcm_wait()`를 호출하지만 고정 avail_min을 잔여 요청량에
맞춰 낮추지 않는다. kernel blocking 경로는 반대로 `twake=min(remaining,
avail_min)`으로 기다릴 수 있다. 따라서 이 검사에서는 nonblocking이
거의 한 period의 공간/데이터를 두고도 다음 period까지 기다린 뒤,
몇 frame의 여유만 남은 상태로 깨어나는 실제 경로가 확인됐다.

`--avail-min-frames 1` 비교 역시 FAIL이다(194560 frame, 최초 불일치 1039,
zero 26, TX/RX XRUN 각 1). **실제 avail_min은 양쪽 모두 1024**였다.
alsa-lib 1.2.13 `src/pcm/pcm.c::snd_pcm_sw_params_set_avail_min()`은
period보다 작은 요청을 period_size로 올린다. 따라서 이 실행은 1-frame
wakeup을 검증한 것이 아니다. 상세 자료는
`exec-entry-nonblock-phase-analysis.md`에 있으며 모든 실패 WAV를 보존한다.

사용자가 요청한 일반 `aplay`/`arecord`와 맞추어 검증기의 기본을 blocking,
period 1024/buffer 2048로 정정했다. 기존 기본 `-N`은 캡처 시작 대기를 위해
검증기에 도입했던 별도 동작이었다. `--nonblock`은 명시적 stress 검사로
유지하고 실패를 정상 처리하지 않는다. 실제 negotiated avail_min도 PASS
조건에 포함해 요청값을 적용값으로 오인하지 않도록 했다. ring 확대,
DMA 포인터 조작, silence 삽입, ALSA 라이브러리 clamp 제거는 하지 않았다.
검증기/trace 분석 Python 테스트 8/8 PASS이며 변경된 기본 명령으로
실제 WAV 양방향 반복을 다시 수행한다.

변경된 기본 명령의 `final-wav-default/`는 첫 3개 case가 PASS
(27.542/27.457/27.594 s)였으나 두 번째 1→0에서 host timeout 180 s로
실패했다(case elapsed 181.808 s). monitor에서 AP 전체가 IDLE/delta 0,
마지막 CPU time 160~165 s에 남았고 SI0도 약 160 s에서 IDLE였다.
SI1/SystemC 시간은 계속 진행했다 (`exec-entry-late-idle-stall.json`).
이 실패는 nonblocking poll threshold 문제와 별개다. 앞선 9개 blocking
전송 PASS만으로 장시간 수정 완료를 주장하지 않는다. 해당 VM을 종료하고
`exec-entry-debug/`에서 AP/SI0 native stop/halt 상태를 유지 관찰하는
추가 재현을 시작했다. 아직 SPI/UART/memory DMA의 최종 회귀는 실행하지 않았다.

### Native pause/resume 경쟁 및 standby 재진입

독립 실제 A53 instruction loop(no WFI)에서 native pause/resume API를
번갈아 호출한 결과, 마지막 resume 뒤에도 `stop=0, stopped=1, halted=0,
workqueue=0`인 상태를 두 번 재현했다. 각각 110272/86496 rounds,
약 619053/521397 us 시점이며 flags=0x46이었다
(`mcips-native-pause-race-{1,2}.log`). 기능 실패를 검출한 뒤 종료도
15 s timeout이므로 정상 exit 실패와 구분한다. 같은 API 호출 각각을
BQL로 직렬화한 대조군은 200000 rounds, 약 1163102 us, flags=0,
정상 exit 0으로 완료했다 (`mcips-native-pause-race-serialized.log`).
이는 native API 경쟁의 독립 증거이며 그 자체로 live MCIPS 상태까지
측정한 것은 아니다.

기존 request_pause/resume은 BQL 없이 stop/stopped를 변경하지만 native
stop acknowledgment는 BQL 아래 `stop=false; stopped=true`를 기록한다.
그 사이 resume이 두 flag를 지우면 뒤의 stopped=true가 재개를 덮어쓸 수
있다. MCIPS mutex 내부에서 BQL을 새로 잡으면 기존 역방향 callback과
교착될 수 있어, 수정은 pause/resume 모두 동일 native CPU work queue에
넣고 BQL 아래 순서대로 적용하는 방식으로 진행한다. direct fast path로
요청 순서가 역전되는 것도 피한다.

별도로 `exec-entry-debug/qbox-platform.log`의 504.138345 ms에서 AP CPU1
`publish_standby`의 W536 immediate self-notification ignored 경고가 있었다.
standby high 발행→PPU reset→request_standby(false)가 같은 SystemC
process로 재진입하면 즉시 self-notify가 무시된다. 하강 요청은 저장되지만
발행되지 않은 채 남을 수 있으므로 `notify(SC_ZERO_TIME)`으로 다음 delta에
발행하도록 보완한다. 기존 async_event overload가 외부 thread의 안전한
전달도 처리한다. 실제 CPU standby callback 내부에서 reset을 동기적으로
assert하는 집중 회귀를 추가하며, 이 경고를 앞선 late stall의 유일 원인으로
단정하지 않는다.

후속 실제 VM `exec-entry-debug/`에서도 blocking WAV 8회 PASS 후 다음
source SCP가 180 s timeout으로 실패했다 (`late-idle-debug-wav.log`).
정지 상태의 GDB에서 AP2는 `stop=0, stopped=1, halted=0, work=null`,
IRQ `0x2` pending이었다. 따라서 독립 테스트에서 검출한 lost-resume
증상과 일치하는 상태가 전체 VM에서도 확인됐다. 상세 native 상태와
stack은 `exec-entry-debug/host-gdb.log`에 보존했다.

양 API를 동일 native work queue로 직렬화한 후 상태 검사는 5회 모두
200000 rounds를 통과했다 (총 1000000 rounds). 정상 process 종료는
4/5이며, 4회차의 검사 완료 후 QK teardown timeout 15 s는 별도 실패다.
`mcips-native-pause-race-results.md` 및 `*-fixed-{1..5}.log`에 실제 신규
libqemu 로딩 경로, SHA256, 종료 상태를 함께 기록했다.

standby reset-feedback 회귀는 기존 immediate notify에서 W536 후
출력이 high로 남아 exit 1, delta notify에서는 같은 시각의 다음 delta에
low를 발행하고 두 번째 boot/WFI까지 5/5 정상 종료했다
(`standby-feedback-before.log`, `standby-feedback-after-{1..5}.log`).
이 결과는 최종 provider 설치 및 Linux 반복 검증과 구분한다.

WAV 검증기는 setup/upload/download timeout에도 기존 PASS 목록 뒤에
명시적 FAIL과 guest directory를 기록한 뒤 중단하도록 보완했다.
전송 timeout으로 중단된 반복을 전체 PASS로 해석하면 안 된다.
관련 Python 회귀는 10/10 PASS이다.

### 재현 시 사용 중인 명시적 시간 구성

주의: native queue 도입 직후 집중 검사 14개 중 reset-wake가 실패했다.
추가 반복에서도 재현됐고, 진단은 `reset=1, stage=2`인 동안 guest가
초기 boot MMIO(value 1)를 다시 실행했음을 보여줬다
(`native-pause-reset-mmio-before-epoch.log`). 이전에 예약된 scheduler
resume이 architectural reset hold를 해제한 것이므로 테스트를 제외하지
않고 native reset 경계를 보완했다.

libqemu CPU별 reset epoch는 assertion/release 경계마다 갱신한다.
reset 중 생성되거나 이전 epoch에서 생성된 pause/resume은 무효화한다.
유효한 even epoch의 하위 bit에 operation을 넣어 별도 heap payload 없이
CPU work queue에 전달한다. reset export는 필요할 때 BQL을 획득하여
epoch/CPU 상태 변경을 직렬화한다. 최종 reset 검사는 21개 구간(0~20)을
5회 모두 정상 종료했고, 관련 IRQ/MMIO/exec-entry/standby/M55 12개도
모두 정상 종료했다 (`native-pause-final-gate-exits.log`, 첫 reset 별도 log).
RR 5-CPU 종료 검사도 exit 0이다 (`native-pause-final-rr-shutdown.log`).
최종 native stress는 5회 × 200000 rounds 상태 검사 PASS이나 정상 종료는
3/5이고, 1·3회차 QK post-sc_stop timeout은 남았다
(`mcips-native-pause-race-epoch-{1..5}.log`). 실제 Linux 최종 결과는 아직
대기 중이며, 중간 실패나 종료 제한을 전체 PASS로 취급하지 않는다.

아래는 조사용 all-domain MCIPS/100 µs 구성이다. 프로젝트의 기본 QK
설정을 변경하지 않았으며, 이 조건의 결과를 기본 QK의 소형 ring 보장으로
확장하지 않는다. instruction rate는 기존 1 GIPS를 유지한다.

```sh
QBOX_APOLLO_MONITOR=true QBOX_APOLLO_MONITOR_PORT=18081 \
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state \
  --out-dir build/qbox-apollo-qvp/i2s-final/new-run \
  --timeout 3600 --keep-running-after-pass -- \
  --platform-param platform.quantum_ns=100000 \
  --platform-param platform.ap_qemu_inst.time_sync_strategy=mcips \
  --platform-param platform.qemu_inst.time_sync_strategy=mcips \
  --platform-param platform.qemu_inst.tcg_mode=MULTI \
  --platform-param platform.rse_cpu_pass.qemu_inst.time_sync_strategy=mcips \
  --platform-param platform.rse_cpu_pass.qemu_inst.tcg_mode=MULTI \
  --platform-param platform.si_cl0_qemu_inst.time_sync_strategy=mcips \
  --platform-param platform.si_cl0_qemu_inst.tcg_mode=MULTI \
  --platform-param platform.si_cl1_qemu_inst.time_sync_strategy=mcips

python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/new-wav \
  --rounds 10 --guest-timeout 20 --host-timeout 180 --fail-fast
```

기존 실행의 output directory를 재사용하지 않는다. launcher의 login PASS와
실제 WAV 비교 PASS는 별도 증거이며, 디버거 없는 최종 반복이 필요하다.

## 최종 reset 상태 전달 보완

`reset-epoch-provider-build.log`의 unit tests는 통과했지만 첫 전체 부팅
`reset-epoch-mcips/`는 약 194 ms부터 AP 보조 CPU의 RUNNING/delta 0이
남아 진행하지 못했다. native reset gate가 scheduler resume을 올바르게
거부했는데 MCIPS는 reset과 scheduler PAUSED를 구분하지 못한 문제였다.
실제 2-CPU 테스트에서도 reset-held peer를 active RUNNING으로 선택해
200.010 µs에서 멈췄다 (`reset-held-peer-before3.log`, exit 1).

QBox의 공통 `reset_cpu()` 경로에서 MCIPS에 architectural reset 상태를
전달한다. reset-held CPU는 초기화·kick·resume 시 clock 선택에서 제외한다.
native async-safe reset이 CPU를 정지시킨 뒤 hold를 확정하며, 비동기 reset
해제는 enqueue 전에 WAKE_PENDING 구간을 예약한다. native reset epoch는
그대로 유지하므로 예약만으로 guest instruction을 실행하거나 진행량을
만들지 않는다. 이 release 예약이 없던 중간 반복 실패도 보존했다.

- Held peer 제외 후 10 ms 진행, 해제 뒤 peer 실행: PASS.
- BQL/native release를 host 20 ms 지연: SystemC 진행은 정확히 100 µs,
  5/5 정상 종료 (`reset-held-delayed-peer-after-*.log`).
- Reset 반복 및 IRQ/MMIO/exec-entry/standby/M55 최종 gate: 16/16 exit 0
  (`reset-held-final-native-pause-final-gate-exits.log`).
- Guest GDB는 board reset을 latch하지 않고 기존 VM pause를 사용한다.
  native scheduler resume도 VM runstate를 존중한다. 실제 RSP T05 응답과
  continue 후 IRQ 검사/정상 종료를 확인했다 (`reset-held-guest-gdb-window.log`).
  기존 attach 전 autostart까지 정지시킨다는 보장이나 모든 GDB single-step
  조합의 검증은 아니다.

전체 근거는 `reset-held-mcips-final-proof.md`에 있다. 최종 전체 부팅은
이전 정지 지점을 넘어 Linux login에 성공했고, 위의 순차 양방향 20회 및
다른 DMA 장치 회귀까지 같은 VM에서 완료했다.

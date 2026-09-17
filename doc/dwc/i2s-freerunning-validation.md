# I2S PIO/DMA freerunning 기능 검증

## 범위와 현재 상태

Apollo QVP의 기본 all-domain QK / `multithread-freerunning` / 10 ms를
유지한다. MCIPS 전환, PCM 데이터 건너뛰기, 비교 전 alignment 보정,
버퍼 확대 또는 XRUN 복구로 성공을 만들지 않는다.

PIO 수정 경로와 최종 기본 DMA 이미지의 실제 Linux 기능 검증을 완료했다.
기존 커널의 WAV 검사는 PIO 38건, DMA 24건 모두 전체 PCM 일치로 통과했다.
ALSA core 원복 이후 검증은 아래의 「ALSA core 변경 제거」 절을 참조한다.
아래 PASS는 명시된 기능적 pacing 조건에 해당하며 옵션을 끈 경로까지
포함하지 않는다. 기본 시간 모드는 변경하지 않았다.

검증 대상은 S16_LE, stereo, 48000 Hz, period 1024 / buffer 2048이다.
실제 `aplay`와 `arecord`로 전송하고 전체 PCM 및 SHA-256을 비교한다.
다른 sample format이나 실제 선로의 연속 48 kHz 타이밍까지 검증한 것은 아니다.

## 수정 내용

- PIO FIFO 처리와 PCM pointer 갱신을 stream lock 아래에서 처리한다.
- 드라이버의 기존 ALSA `substream->wait_time` 설정은 R/W 대기에만 사용한다.
  종료는 `aplay --drain-timeout=5000`의 bounded nonblocking drain으로
  기다린다. ALSA core의 drain timeout 변경은 제거했다.
  실제 XRUN이나 데이터 불일치는 계속 실패다.
- 선택적 `pio_fifo_empty_irq`는 비활성 채널 설정 단계에서 최저 TX threshold를
  설정한다. PIO drain 시 IRQ를 막고 TXFE를 bounded poll한 뒤 serializer의
  잔여 시간을 기다린다. timeout은 오류다. 고정 시간만 기다리던 경로의
  간헐적 마지막 period 부족을 해결하기 위한 경로다.
- DMA350은 실제 hardware command-link cyclic descriptor를 사용한다.
  controller의 `cyclic_done_pause` DT 속성은 각 period 후 DONEPAUSE로 정지하고,
  virt-dma의 client callback이 반환된 후 RESUME한다.
  동명의 module parameter는 제거했으며 QVP의 두 controller에 DT 속성을 선언했다.
- I2S PAUSE는 stream의 FIFO 소유권을 유지한다. 마지막 stream의 PAUSE에서
  IER를 끄면 FIFO가 flush되므로 실제 STOP과 구분한다.
- keep-running launcher의 로그 수집 프로세스 수명을 수정했다. launcher가
  반환한 뒤에도 VM의 전송 trace를 수집하며, runtime timeout은 유지한다.

## 재현 조건

`./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`로 빌드한다.
`build/conf`의 FVP 기본값을 QVP로 영구 변경하지 않는다.
PIO 이미지는 I2S0/1의 `dmas`와 `dma-names`만 임시 제거해 빌드하고 WIC/DTB를
별도 보존한 뒤 소스를 복구한다. UKI에도 DT가 들어가므로 launcher의
`--ap-dtb`만 바꾸는 것으로 PIO 전환을 입증할 수 없다. guest live DT를 확인한다.
정상 소스의 I2S0/1에는 TX/RX DMA 속성을 모두 유지한다.

검증용으로 보존한 입력 및 SHA-256 manifest는
`build/qbox-apollo-qvp/i2s-final/` 아래에 있다. 부팅에는 해당 WIC와 DTB를
명시하고 `--multi-session --copy-disks --no-persistent-rse-state`를 사용한다.
긴 검사는 `--timeout 1800 --keep-running-after-pass`로 실행한다.

게스트의 PIO 조건:

```sh
echo Y > /sys/module/designware_i2s/parameters/pio_fifo_empty_irq
echo 5000 > /sys/module/designware_i2s/parameters/pio_wait_time_ms
echo 0 > /proc/irq/65/smp_affinity_list
echo 1 > /proc/irq/66/smp_affinity_list
```

게스트의 DMA 조건:

```sh
echo 5000 > /sys/module/designware_i2s/parameters/dma_wait_time_ms
echo 0 > /proc/irq/40/smp_affinity_list
```

IRQ 번호는 검증 이미지의 번호다. 적용 전에 `/proc/interrupts`에서 PIO의
`30200000.i2s`/`30210000.i2s` 및 DMA350_1 채널에 해당하는지 확인한다.
옵션은 PCM open/descriptor 준비 전에 설정한다. 기본 모듈 값과 기본 IRQ
affinity는 바꾸지 않았으며 사용자 앱은 normal scheduling으로 CPU2에 배치한다.

호스트의 WAV 검사 예:

```sh
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/new-odd-repeat \
  --rounds 15 --frames 8209 --cpu 2 --guest-timeout 90 --host-timeout 180
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/new-long-odd \
  --rounds 1 --frames 196625 --cpu 2 --guest-timeout 180 --host-timeout 240
```

항상 새 output directory를 사용한다. 각 case의 source/capture WAV,
명령, ALSA 설정, 앱 로그와 전체 결과 JSON을 보존한다.
현재 WAV runner는 기본으로 `--drain-timeout-ms 5000`을 적용한다.
새 alsa-utils가 필요하며, 이전 바이너리/기존 blocking drain을 시험할 때만
`--drain-timeout-ms 0`을 명시한다. `aplay -N`만으로는 종료 drain을
nonblocking으로 바꿀 수 없다.

## 남는 제한

I2S의 기존 `functional_pacing`은 TX-empty 대기 및 RX-full 재시도를 사용한다.
물리적 I2S에는 없는 수신측 backpressure를 포함하므로 기능적 데이터 무결성
결과이지 물리적 FIFO deadline/연속 오디오 PASS가 아니다.
DONEPAUSE callback 완료도 userspace refill 완료 자체를 보장하지 않는다.
quirk 적용 전 autonomous DMA와 기존 고정 지연 PIO drain의 실패 이력은 유지한다.
PIO driver는 ALSA pause capability를 광고하지 않으며 PIO pause 지원을 추가하지 않았다.

## 최종 증거

모든 경로는 `build/qbox-apollo-qvp/i2s-final/` 기준이다. PIO/DMA guest의
kernel notes SHA-256은 동일하다:
`2b29a4d278f1cb6b338805658e3e5ce53cc5284fdead88322a02be9f38bcae3a`.

| 검사 | 증거 | 결과 |
|---|---|---|
| PIO 8209 frames, 양방향 각 15회 | `pio-empty-threshold-odd-repeat/results.json` | 30/30 PASS |
| PIO 196625 frames, 양방향 | `pio-empty-threshold-long-odd/results.json` | 2/2 PASS |
| PIO 정렬된 8192 frames, 양방향 각 3회 | `final-pio-aligned-wav/results.json` | 6/6 PASS |
| DMA 8209 frames, 양방향 각 10회 | `final-dma-odd-repeat/results.json` | 20/20 PASS |
| DMA 196625 frames, 양방향 | `final-dma-long-odd/results.json` | 2/2 PASS |
| DMA TX 단독/양쪽 pause-resume, 양방향 | `final-dma-pause-{tx,both}-*.log` | 4/4 PASS, 각각 16384 frames |
| DMA paused STOP/close, 양방향 | `final-dma-pause-drop-*.log` | 2/2 PASS, 취소 수명 검사 |
| DMA STOP 이후 8192 frames 재시작 | `final-dma-after-drop/results.json` | 2/2 PASS |
| SPI/UART/memory DMA, shared IRQ, I2C PIO | `final-dma-regression.json` | PASS, 실제 model trace 대조 |
| 64 KiB/2 MiB polled copy/set | `final-dma-residue.log` | 20 tests PASS |
| 호스트 검증 도구 | `final-host-tests.log` | 16 PASS |

기본 DMA BSP 최종 빌드는 `final-dma-image-build-retry.log`의 5793 tasks
성공이다. provider `log.do_check.1190323`에서 platform 61/61, core 63/63이
통과했다. 바로 전 빌드는 core timer-WFI baseline의 간헐적 종료 timeout으로
실패했으며, 별도 3회 및 전체 재시도는 통과했다. 이 종료 문제 자체가 수정됐다고
주장하지 않으며 상세 실패 로그를 보존했다.

기본 source/deploy는 I2S 양쪽의 TX/RX DMA 구성이다. PIO 입력은 별도로 보존한다.
`{pio-empty-threshold,final-dma}-artifacts.sha256`은 WIC/DTB hash,
`final-runtime-source.sha256`은 실행 파일 및 관련 driver source hash다.
검증 VM은 종료했다. 최종 deploy WIC/DTB가 보존한 DMA 입력과 동일함을
`cmp`로 확인했다. source DTS에도 임시 PIO 변경이 남아 있지 않다.

실패 이력, 원인 분석, 각 실행의 정확한 로그와 hash는
[상세 조사 기록](i2s-default-qk-investigation-20260916.md)을 참조한다.

## ALSA core 변경 제거 (2026-09-17)

`sound/core/pcm_native.c`의 drain timeout 확장과 `include/sound/pcm.h`의
설명 변경을 모두 원복했다. 다음 명령은 출력 없이 성공한다.

```sh
git -C hsoc-stack/components/primary_compute/linux diff --exit-code \
  927bee1972e2^ -- sound/core include/sound/pcm.h
```

기존 ALSA의 `substream->wait_time`은 PCM R/W 대기에만 적용된다. 이를
설정하는 PIO/DMA 드라이버 옵션은 유지하며, DMA 옵션 설명에서 drain을
제거했다. core drain은 원래대로 `max(100, buffer_size * 1100 / rate)` ms를
사용한다. 2048-frame/48 kHz 조건에서는 100 ms다.

소유 product layer의 `recipes-multimedia/alsa/alsa-utils_%.bbappend`는
`apollo-qvp`에만 aplay 패치를 적용한다. 새 `--drain-timeout=5000`은
drain 시점에 nonblocking으로 전환하고, `-EAGAIN`이면 실제 PCM 상태를
확인하며 1 ms 간격으로 재시도한다. `SETUP` 도달/성공 반환을 완료로
처리하고, 다른 상태·ALSA 오류·게스트 CLOCK_MONOTONIC 기준 제한시간 초과는
진단과 실패 종료코드를 반환한다. 실패 시 stream을 drop하여 정리한다.
XRUN recovery나 전송 데이터 보정은 수행하지 않는다.

이 옵션을 생략하면 기존 aplay 동작을 유지한다. aplay 1.2.13의 `-N`은
종료 시 blocking drain으로 다시 전환하므로 대체 옵션이 아니다.
`sound/core`를 수정하지 않고 드라이버의 wait_time만 설정하는 것도 drain
timeout을 늘리지 못한다. 일반 앱 전체의 blocking drain 동작 개선은 이번
변경 범위가 아니며, 해당 앱은 별도 nonblocking drain 처리가 필요하다.

WAV runner의 기본값은 `--drain-timeout-ms 5000`이며 실제 aplay 옵션으로
전달한다. 0을 주면 기존 blocking drain 경로를 선택한다. 결과 JSON에
선택한 timeout을 기록하고 drain 오류를 명시적으로 FAIL로 판정한다.

### core 원복 후 실제 QBox/Linux 결과

증거 기준 경로는 `build/qbox-apollo-qvp/i2s-core-free/`다. 기존 기본
all-domain QK / freerunning / 10 ms, functional pacing, S16_LE stereo
48 kHz, period 1024 / buffer 2048, 위의 R/W wait 및 IRQ/app affinity를
유지했다. R/W는 blocking이며 drain만 nonblocking이다.

| 검사 | 증거 디렉터리 | 결과 |
|---|---|---|
| DMA 8209 frames, 양방향 각 3회 | `dma-odd` | 6/6 전체 PCM/hash 일치 |
| DMA 196625 frames, 양방향 | `dma-long` | 2/2 전체 PCM/hash 일치 |
| DMA 1 ms drain 제한 부정 검사 | `dma-timeout-negative` | 예상 FAIL 검출: aplay timeout/exit 1, capture 7168/8209 frames |
| 위 실패 이후 DMA 8192 frames 재시작, 양방향 | `dma-restart` | 2/2 전체 PCM/hash 일치 |
| PIO 8209 frames, 양방향 각 3회 | `pio-odd` | 6/6 전체 PCM/hash 일치 |
| PIO 196625 frames, 양방향 | `pio-long` | 2/2 전체 PCM/hash 일치 |
| 최종 복구 DMA 배포 이미지 8209 frames, 양방향 | `final-dma-wav` | 2/2 전체 PCM/hash 일치 |

정상 전송 총 20건은 zero frame, PCM mismatch, XRUN 없이 통과했다.
부정 검사는 정상 전송 PASS 수에 포함하지 않는다. 두 guest의 최종 dmesg에
BUG/Oops/WARNING/RCU stall/PIO drain threshold timeout은 없었다.
PIO live DT에는 I2S dmas가 없고 DMA guest에는 있으며, 실제 IRQ 카운터를
`{dma,pio}-preflight.log`, `dma-live-dt.log`, `{dma,pio}-guest-final.log`에
보존했다. DMA preflight의 첫 DT 조회는 잘못된 경로로 실패했으며, 이어서
`dma-live-dt.log`에서 실제 경로와 속성을 확인했다.

양쪽 kernel notes SHA-256:
`91a837a6acd37b502c94d4dd2128770cb5400d47ca9bd672247a6eaf8f3d233e`.
guest aplay SHA-256:
`175f725cd6ea65dee457ab73630dbadd45f6895140023acf323bc6a58befbad9`.
WIC/DTB는 `{dma,pio}-inputs/`와 `{dma,pio}-artifacts.sha256`에 보존했다.
`alsa-build.log`, `dma-image-build.log`, `pio-image-build.log`는 모두 성공했고,
호스트 WAV 검증 도구 테스트 8개도 통과했다. 최종 기본 DMA 배포 복구 빌드는
`final-dma-image-build.log`에서 5793 tasks가 성공했다.
소스 DTS는 원래 DMA 구성으로 복구했다. 빌드 경고 5건은 기존 forced-task
taint 알림이며 이번 변경의 컴파일/패키징 경고가 아니다.
최종 배포 WIC는 재생성으로 파일 해시가 달라져 실제 재부팅 후 양방향을
다시 검사했다. kernel notes/aplay 해시는 이전 검증과 동일하다.
배포 해시는 `final-deploy.sha256`, live DT/실행 파일 확인은
`final-dma-preflight.log`, 결과는 `final-dma-wav/results.json`에 보존했다.
검증용 VM들은 종료했다.

이번 재검증은 core 원복과 aplay drain 대체에 집중했다. 이전 pause/resume,
SPI/UART/memory DMA 회귀 횟수를 이번 실행의 결과로 합산하지 않는다.
기존 functional pacing의 물리적 연속 오디오 제한은 그대로다.

## Apollo QVP DONEPAUSE 기본 quirk (2026-09-17)

이 절은 이전 machine quirk 검증 이력이다. 현재는 아래의 DT 속성 방식으로
대체했으며 `arm,apollo-qvp` compatible 검사를 사용하지 않는다.

`cyclic_done_pause` module parameter를 제거했다. DMA350 probe에서 루트 DT의
`arm,apollo-qvp` compatible을 확인하여 각 채널에 quirk를 저장한다.
command-link 지원 및 `DMA_PREP_INTERRUPT` cyclic 전송에서만 DONEPAUSE를
사용한다. 두 DMA 인스턴스에 동일하게 적용되지만 memcpy/memset/slave SG에는
적용하지 않는다. 다른 machine에는 자동 pacing을 적용하지 않는다.
새 DT 속성이나 binding 변경은 없으며, 기존 R/W wait와 IRQ/app affinity,
bounded userspace drain 조건은 그대로다.

실제 증거는 `build/qbox-apollo-qvp/i2s-donepause-quirk/`에 있다.
`preflight.log`에서 module parameter 경로 부재와 31000000/31010000 두
controller의 `Enabling Apollo QVP cyclic DONEPAUSE quirk` 로그를 확인했다.
DONEPAUSE sysfs 쓰기 없이 다음 검사를 수행했다.

| 검사 | 증거 | 결과 |
|---|---|---|
| I2S 8209 frames, 양방향 각 3회 | `odd/results.json` | 6/6 전체 PCM/hash 일치 |
| I2S 196625 frames, 양방향 | `long/results.json` | 2/2 전체 PCM/hash 일치 |
| SPI 2포트, UART 양방향, memory copy/set, shared IRQ, I2C PIO | `regression.log`, `regression.json` | PASS, 실제 모델 343 operations 대조 |

`image-build.log`에서 5793 tasks가 성공했고 driver diff checkpatch는
오류/경고 0이다. kernel notes SHA-256은
`4f041f323e7d779c8f7267346810113bb91659f1e80bf3e9affe5da0825ce631`이며
배포 WIC/DTB와 driver source 해시는 `artifacts.sha256`에 보존했다.
회귀 trace는 환경변수 대신 실행 인자
`--platform-param platform.dma350_0.trace=true`와
`--platform-param platform.dma350_0.trace_filter=operation`으로 활성화했다.
다른 machine의 미적용은 코드 분기 검토 결과이며 FVP를 재부팅한 결과는 아니다.
이전 core 원복 검증과 이번 quirk 검증 횟수는 별도로 기록한다.

## Controller DT 속성으로 선택 (2026-09-17)

machine-compatible quirk를 제거하고 각 DMA350 controller 노드에서
`cyclic_done_pause;` boolean 속성을 읽도록 변경했다. 현재 Apollo QVP의
`dma350_0`와 `dma350_1` 양쪽에 선언한다. 속성이 없으면 autonomous cyclic이며
플랫폼 이름과 무관하다. module parameter는 없고, 적용 범위는 기존처럼
command-link 지원 채널의 `DMA_PREP_INTERRUPT` cyclic 전송에 한정한다.

```dts
&dma350_0 {
    cyclic_done_pause;
};

&dma350_1 {
    cyclic_done_pause;
};
```

실제 속성은 `apollo-qvp.dts`의 각 controller 선언에 직접 넣었고,
`arm,dma-350.yaml`에 선택적 boolean으로 정의했다. false를 나타내려면 속성을
생략한다. `<0>`을 쓰는 방식은 boolean 속성을 끄는 방법이 아니다.

증거는 `build/qbox-apollo-qvp/i2s-donepause-dt/` 아래에 보존한다.
`schema.log`는 바인딩 검사, `dtb-schema.log`는 빌드된 DTB의 DMA350 schema
검사 결과이며 둘 다 성공했다. 호스트의 기존 dt-doc-validate는 dtschema
모듈이 없어 `uvx --from dtschema`의 격리된 환경으로 실행했다.
`image-build.log`는 5793 tasks 성공, driver checkpatch는 오류/경고 0이다.
binding과 driver를 함께 검사하면 binding을 별도 커밋으로 분리하라는
checkpatch 경고가 나오므로 향후 커밋 시 분리한다.

`preflight.log`에서 두 controller의 live DT 속성과
`Enabling DT cyclic DONEPAUSE pacing` 로그, module parameter 부재를 확인했다.
kernel notes SHA-256은
`fbb505f3e4cf96df8656068c5692f72803284ca83599bd3516ba63a26671f416`이다.
배포 WIC/DTB 및 driver source 해시는 `artifacts.sha256`에 있다.
기존 freerunning, R/W wait, IRQ/app affinity, userspace drain 조건을 유지한다.

| DT 선택 이후 실제 WAV 검사 | 증거 | 결과 |
|---|---|---|
| 8209 frames, 양방향 각 2회 | `odd/results.json` | 4/4 전체 PCM/hash 일치 |
| 196625 frames, 양방향 | `long/results.json` | 2/2 전체 PCM/hash 일치 |

총 6건 모두 zero frame/PCM mismatch/XRUN 없이 통과했다. 일반 DMA 회귀는
직전 machine quirk 단계의 결과이며 이번 DT 선택 변경 후 다시 합산하지 않는다.
검증 VM은 종료했다. DT 속성 부재 시 비활성화는 boolean 읽기 코드와 optional
schema로 확인했으며 별도 속성 제거 이미지를 부팅하지는 않았다.

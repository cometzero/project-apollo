# I2S PIO/DMA freerunning 기능 검증

## 범위와 현재 상태

Apollo QVP의 기본 all-domain QK / `multithread-freerunning` / 10 ms를
유지한다. MCIPS 전환, PCM 데이터 건너뛰기, 비교 전 alignment 보정,
버퍼 확대 또는 XRUN 복구로 성공을 만들지 않는다.

PIO 수정 경로와 최종 기본 DMA 이미지의 실제 Linux 기능 검증을 완료했다.
최종 커널의 WAV 검사는 PIO 38건, DMA 24건 모두 전체 PCM 일치로 통과했다.
아래 PASS는 명시된 기능적 pacing 조건에 해당하며 옵션을 끈 경로까지
포함하지 않는다. 기본 시간 모드는 변경하지 않았다.

검증 대상은 S16_LE, stereo, 48000 Hz, period 1024 / buffer 2048이다.
실제 `aplay`와 `arecord`로 전송하고 전체 PCM 및 SHA-256을 비교한다.
다른 sample format이나 실제 선로의 연속 48 kHz 타이밍까지 검증한 것은 아니다.

## 수정 내용

- PIO FIFO 처리와 PCM pointer 갱신을 stream lock 아래에서 처리한다.
- 명시적 PCM wait override와 drain wait 반영으로 느린 MMIO 환경의 시작 및
  종료 대기를 허용한다. 실제 XRUN이나 데이터 불일치는 계속 실패다.
- 선택적 `pio_fifo_empty_irq`는 비활성 채널 설정 단계에서 최저 TX threshold를
  설정한다. PIO drain 시 IRQ를 막고 TXFE를 bounded poll한 뒤 serializer의
  잔여 시간을 기다린다. timeout은 오류다. 고정 시간만 기다리던 경로의
  간헐적 마지막 period 부족을 해결하기 위한 경로다.
- DMA350은 실제 hardware command-link cyclic descriptor를 사용한다.
  선택적 `cyclic_done_pause`는 각 period 후 실제 DONEPAUSE 기능으로 정지하고,
  virt-dma의 client callback이 반환된 후 RESUME한다.
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
echo Y > /sys/module/arm_dma350/parameters/cyclic_done_pause
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

## 남는 제한

I2S의 기존 `functional_pacing`은 TX-empty 대기 및 RX-full 재시도를 사용한다.
물리적 I2S에는 없는 수신측 backpressure를 포함하므로 기능적 데이터 무결성
결과이지 물리적 FIFO deadline/연속 오디오 PASS가 아니다.
DONEPAUSE callback 완료도 userspace refill 완료 자체를 보장하지 않는다.
옵션을 끈 autonomous DMA와 기존 고정 지연 PIO drain의 실패 이력은 유지한다.
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

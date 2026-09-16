# 기본 QK 모드의 I2S 소형 DMA 링 조사

## 결론과 범위

2026-09-16 기본 `quantum_keeper` / `multithread-freerunning`, global quantum
10 ms를 유지하며 실제 QBox/Linux 재현과 수정을 진행 중이다.
초기 양방향 WAV는 FAIL이었다. 최신 PIO 8192-frame 검사는 양방향 PASS이나,
긴 전송·반복·DMA 검증이 남아 있어 전체 기본 모드 해결은 아직 아니다.
초기 재현 이후 QK 전송 상태·공통 epoch·절대시각 publication을 수정했고,
DMA command-link 및 PIO 진단 대기시간 변경도 검증 중이다.
아래 실행 절은 초기 설치 빌드의 기록이며, 후속 변경과 검증 경계는
문서 뒤쪽에 시간순으로 추가했다. 단위 테스트 PASS는 통신 PASS가 아니다.

## 실행과 결과

`build/conf/local.conf`와 template은 apollo-fvp이므로 launcher에
`--machine apollo-qvp`를 명시해 기존 QVP 배포 산출물을 사용했다.
이미지/provider 재빌드는 하지 않았다.

```sh
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state \
  --out-dir build/qbox-apollo-qvp/i2s-final/default-qk-recheck \
  --timeout 900 --keep-running-after-pass

python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/default-qk-recheck-wav \
  --rounds 1 --guest-timeout 20 --host-timeout 180
```

일반 blocking `aplay`/`arecord`, S16_LE stereo 48 kHz,
period 1024/buffer 2048, avail_min 1024, source 196608 frames이다.
RT priority/CPU affinity/MCIPS override는 사용하지 않았다.

| 방향 | 실제 협상 형식 | 캡처 frames | 결과 | host 경과 |
|---|---|---:|---|---:|
| I2S0 → I2S1 | 요청과 일치 | 0 | RX EIO, TX 반복 XRUN | 22.661 s |
| I2S1 → I2S0 | 요청과 일치 | 0 | RX EIO, TX 반복 XRUN | 22.414 s |

이는 캡처 파일에 기록된 frames이며 실제 wire 전송량이 0이라는 뜻은 아니다.
WAV/ALSA 로그와 `results.json`은 위 output directory에 보존했다.

별도 0→1 재현에 `scripts/test/trace_qbox_i2s_period.sh`를 30 guest seconds
병행했다. `default-qk-traced-wav/`도 캡처 0/EIO/XRUN으로 FAIL이다.
`default-qk-active-trace.log`를 기존 분석기로 분석한 결과:

| 구간 | 표본 | 중앙값 | p95 | 최대 |
|---|---:|---:|---:|---:|
| d350_program_cmd | 60 | 117.8775 ms | 131.427 ms | 135.871 ms |
| d350_irq handler | 234 | 19.7785 ms | 141.697 ms | 152.420 ms |

callback 32개, unmatched entry/exit 0이다. IRQ 값은 handler 내부 시간이지
IRQ assertion부터 Linux 진입까지의 latency가 아니다. kprobe 오버헤드가
포함되며, 추적 없는 재현도 실패했지만 이 수치 자체는 계측 조건의 결과다.
먼저 시도한 `default-qk-period-trace.log`는 트래픽과 겹치지 않아 event 0이며
타이밍 증거로 사용하지 않는다. 종료 시 4개 PCM이 모두 closed임을 확인했다.

## 소스로 좁힌 원인 후보

소유 저장소 기준 경로:

- `qbox-platform/platforms/apollo/hw-block/fabric.lua`: global quantum 10 ms.
- `qbox/qemu-components/common/include/cpu.h`: `deadline_timer_cb()`가
  keeper 시각을 갱신하고 `rearm_deadline_timer()`는 다음 global quantum에
  갱신을 예약한다. `QuantumKeeperSync`에는 MCIPS와 달리 transport
  begin/complete/end 상태 처리가 없다.
- `qbox/systemc-components/common/src/libgssync/qkmultithread.cc`:
  `timehandler()`는 캐시된 keeper 시각까지 SystemC가 도달하면 suspend한다.
- `qbox/qemu-components/common/include/ports/initiator.h`: regular MMIO는
  `Suspension::Respect`로 다른 initiator의 barrier를 준수한다.
- `qbox/systemc-components/common/include/timed_dispatch.h`: dispatch 때
  시각을 다시 샘플링하므로 큐 대기 중 진행한 virtual clock도 서비스 시각에
  반영된다. wall-clock 기반 QK에서는 이 경로의 지연 증폭을 조사해야 한다.

다른 CPU/domain의 오래된 keeper bound 때문에 개별 timed MMIO가 다음
10 ms 갱신을 기다리는 경로가 있다. 레지스터 접근이 많은 DMA 재설정에서
지연이 누적된다는 가설은 이번 80~136 ms 측정 및 이전 조사와 부합한다.
다만 enqueue/service/completion과 각 keeper bound를 함께 계측하지 않았으므로
해당 메커니즘이 전체 지연의 원인이라고 확정하지 않는다.

## 기본 설정을 유지하는 수정 방향

1. 두 keeper의 최소 재현 테스트를 만든다. A는 연속 timed MMIO,
   B는 MMIO 없는 실행 또는 instance I/O lock 대기 상태로 구성한다.
   request, enqueue, service, completion, native resume 시각과 각 keeper
   bound를 기록해 10 ms 갱신 의존성을 분리한다.
2. QK에 실행 중 / I/O lock 대기 / target wait / 완료 후 재개 상태를
   명시하고, barrier가 stale bound에 막힐 때 필요한 clock progress를
   즉시 전달한다. outstanding TLM은 요청·target delay·완료 경계를 지키며,
   완료 전에 CPU가 실행한 것으로 간주해서는 안 된다.
3. 실제 clock이 아직 진행하지 않았다면 native kick/progress notification으로
   후속 갱신을 요청한다. busy polling 대신 기존 deadline timer를 fallback으로
   유지한다. 같은 instance와 다른 domain, SINGLE/MULTI 모두 검사한다.
4. 기본 quantum 그대로 양방향 WAV 각 10회와 비정렬 끝부분을 재검증하고,
   SPI/UART/memory DMA, reset/WFI/IRQ 및 종료 회귀를 수행한다.

단순히 모든 keeper를 wall clock으로 올리거나 transport 동안 stop하는 것은
미완료 전송의 시간 경계를 훼손할 수 있다. `Suspension::Ignore` 복구도
전역 barrier 우회를 재발시킨다. quantum 축소, buffer 확대, IRQ affinity는
이 기본 모드 수정의 완료 기준으로 사용하지 않는다.

wall-clock freerunning은 host 부하의 영향을 받으므로 위 수정이 성공하더라도
임의의 host 부하에서 소형 링의 실시간 deadline을 보장한다는 뜻은 아니다.
검증된 MCIPS 실행은 [이전 조사](i2s-xrun-followup-20260915.md)에 별도로 남긴다.

## PIO 대조 검사: 실제 Linux에서도 FAIL

사용자 요청에 따라 같은 날 DMA를 제거한 PIO 대조 검사를 수행했다.
기본 QK/freerunning/10 ms, AP 4 CPU 및 기존 `functional_pacing=true`는
그대로 유지했다. 두 I2S node의 `dmas`/`dma-names` 네 property만 임시 제거해
`./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`로 UKI/WIC까지 빌드했다.
별도 driver 수정이나 PIO 전용 동기화 override는 없다.

`dwc-i2s.c`의 probe는 IRQ가 있고 `dmas`가 없으면 `dw_pcm_register()`와
`use_pio=true`를 선택한다. 빌드 config의 `CONFIG_SND_DESIGNWARE_I2S=y`,
`CONFIG_SND_DESIGNWARE_PCM=y` 및 **실제 guest DT에서 양쪽 DMA property 부재**를
확인했다. 드라이버는 `designware-i2s`, 양쪽 TX/RX PCM 모두 등록됐다.
kernel notes SHA-256은 이전 DMA 검사와 같은
`87ff9ed48a4c18e7663125ca1d7e915cafc577162c9f539d06851595cd3cc68b`이다.

증거 root는 `build/qbox-apollo-qvp/i2s-final/`이다.

| 검사 | period / buffer | 결과 |
|---|---|---|
| 첫 부팅 0→1 | 1024 / 2048 | 2.759 s, aplay/arecord EIO, 캡처 0 frames |
| 같은 VM 후속 1→0 | 1024 / 2048 | host 180 s timeout, RCU stall, 캡처 회수 불가 |
| 새 부팅에서 1→0만 실행 | 1024 / 2048 | 2.907 s, aplay/arecord EIO, 캡처 0 frames |
| 새 VM의 큰 버퍼 대조 1→0 | 1024 / 16384 | 3.122 s, aplay/arecord EIO, 캡처 0 frames |

모두 일반 blocking WAV, S16_LE stereo 48 kHz, source 196608 frames,
avail_min 1024이다. 로그를 회수한 세 검사 모두 실제 협상 형식이 요청과 일치했다.
첫 VM의 두 번째 검사는 host timeout 때문에 실제 형식/PCM 데이터를 판정하지 않는다.
캡처 0 frames는 파일에 기록된 데이터량이며 wire에서 한 frame도 전송되지
않았다는 판정은 아니다. PIO 모드에서는 cyclic DMA 검증을 주장하지 않는다.

새 VM의 작은 버퍼 검사 전 I2S IRQ는 양쪽 0이었다. 검사 후 TX인 I2S1의
HWIRQ 389는 1, RX인 I2S0의 HWIRQ 388은 0이었다. 네 PCM은 모두 closed였다.
이는 반복적인 PIO FIFO 서비스가 진행되지 않았다는 단서다. 첫 VM의 RCU
stall에는 `aplay`와 `dw_i2s_trigger` → `snd_pcm_do_start` 경로가 나타났지만,
이 stack 하나로 deadlock 원인을 확정하지 않는다.

주요 산출물:

- `default-qk-pio/`, `default-qk-pio-reverse/`: 독립 부팅/serial 로그와 PIO WIC 사본.
- `default-qk-pio/apollo-qvp-pio.dtb`: 복원 전 PIO DTB 보존본.
- `default-qk-pio-artifacts.sha256`: 빌드된 DTB/WIC/platforms-vp hash.
- `default-qk-pio-preflight.log`, `default-qk-pio-reverse-preflight.log`:
  live DT, driver/ALSA 장치, 초기 IRQ 증거.
- `default-qk-pio-wav/`, `default-qk-pio-reverse-wav/`,
  `default-qk-pio-large-wav/`: 명령, WAV, ALSA 로그, `results.json`.
- `default-qk-pio-reverse-after.log`, `default-qk-pio-final-cleanup.log`:
  IRQ와 PCM closed 확인. 테스트용 VM 두 개는 검사 후 종료했다.

재현은 앞 절의 launcher를 PIO 이미지 배포 후 사용한다. 새 VM 반대 방향 명령:

```sh
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/default-qk-pio-reverse-wav \
  --rounds 1 --direction 1to0 --guest-timeout 20 --host-timeout 60
```

첫 PIO 이미지 빌드는 core의 `aarch64-managed-timer-wfi-baseline`,
`aarch64-managed-uart-fifo-quiescent`가 `Simulation stopped` 후 각각 30 s
종료 timeout으로 실패했다 (`log.do_check.503191`, `default-qk-pio-build.log`).
설정 변경/제외 없이 재실행하여 platform 61/61 (5.57 s), core 62/62 (19.14 s),
전체 5793 tasks 성공을 확인했다 (`default-qk-pio-build-retry.log`).
재실행 성공을 간헐적 종료 문제의 수정으로 간주하지 않는다.

PIO 실패까지 확인했으므로 DMA-350 cyclic/residue만을 원인으로 한정할 수 없다.
다음 분석은 PIO의 첫 TX IRQ, FIFO fill, RX IRQ, trigger 완료 시각을 QK
MMIO 경계와 함께 추적하는 것이 우선이다. 이전 PIO PASS는 다른 시점/조건의
이력이며 이번 최신 기본 모드의 PASS 근거로 사용하지 않는다.

검사 후 DTS 네 property를 복원했고 해당 파일의 Git diff가 없음을 확인했다.
`default-qk-pio-restore-dma-build.log`에서 5793 tasks 전체 성공을 확인했다.
복원된 A/B UKI의 `.dtb`를 각각 추출해 두 I2S 모두 원래 TX/RX DMA channel
0/1 및 2/3을 참조하는 것도 확인했다 (`restored-dma-uki-{a,b}.dtb`).
기본 DMA 이미지 복원은 빌드/UKI 확인이며 이 단계에서 DMA runtime을 재검증한
것은 아니다. PIO WIC 사본과 실패 증거는 보존했다.

## 후속 수정 진행 중: 완료 판정 아님

사용자 요청에 따라 기본 freerunning에서 PIO와 DMA 모두 정상화하는 작업을
진행 중이다. 위 FAIL 결과는 그대로 유지하며 다음 변경의 실제 Linux 효과는
별도 재검증해야 한다.

- QBox CPU가 instance I/O lock을 기다리기 전에 절대 MMIO 요청 시각을
  저장하도록 변경했다. `timed_dispatch`는 서비스 시각의 wall clock을 다시
  샘플링하지 않고 `max(request - SystemC now, 0)`을 전달한다. 큐에서 기다린
  시간이 이미 발행된 요청을 계속 미래로 옮기지 않도록 하는 수정이다.
  target 완료 시각 전달은 callback 내부에 유지한다.
- 요청 20 ns, 서비스 대기 중 clock 50 ns인 경우 요청 시각 유지 및 늦은
  서비스의 zero delay를 검사했다. wait-consuming/annotated target 검사도
  함께 통과했다 (`qk-issue-time-unit-test.log`). 이는 stale peer keeper의
  barrier 문제까지 해결했다는 뜻은 아니다.
- PIO에 기본값 0인 진단용 `pio_wait_time_ms`를 추가했다. PCM open 시
  최대 5000 ms로 제한하며 기본 ALSA 동작은 유지한다. timeout을 늘린
  결과만으로 전송 PASS를 선언하지 않는다.
- DMA-350 모델과 Linux driver에 hardware command-link cyclic 경로를
  추가했다. 상세 변경과 남은 검증은
  [hardware command-link cyclic](../dma-350/hardware-command-link-cyclic.md)에
  기록한다. 아직 Linux 실제 cyclic PASS는 확인 전이다.
- 기존 period trace 도구에 `pio` 모드를 추가했다. `i2s_irq_handler`와
  `dw_pcm_tx_16`의 구간을 구분한다. 관련 Python 검사 10개 PASS이다.

이번 단계의 전체 provider 빌드 로그는
`build/qbox-apollo-qvp/i2s-final/qk-issue-time-provider-build.log`이다.
최종 완료 기준은 기본 설정 그대로 실제 Linux 양방향 PIO/DMA WAV 비교,
반복 start/stop, 비정렬 마지막 period, 관련 DMA 회귀까지 통과하는 것이다.

### Demand-progress 경로 연결 및 단위 검사

요청 시각 고정만 적용한 PIO의 후속 검사도 FAIL이다.
`qk-issue-time-pio-ready-wav/results.json`은 0→1 캡처 0 frames,
TX/RX EIO, 2.700 s를 기록한다. trace 준비 완료 후 트래픽을 시작한
`qk-issue-time-pio-ready-trace.log`의 표본 1개에서 IRQ handler는
223.321 ms, `dw_pcm_tx_16`은 121.079 ms였다. 이는 kprobe 포함 구간이며
IRQ assertion latency나 일반적인 지연 분포로 해석하지 않는다.

후속 수정은 non-icount freerunning에 한정하여 실행 중 keeper의 시각을
필요 시 갱신한다. CPU의 MMIO begin, I/O lock wait/acquire, SystemC target
service, completion, native resume 경로를 keeper 상태와 연결했다.
PENDING/READY에서는 시간 경계를 유지하고 WAIT_IO/SERVICING에서는 lock
owner/target이 진행하도록 허용한다. 기본 quantum과 MCIPS 설정은 바꾸지 않았다.

`qk-demand-unit-test.log`에서 `qkmulti-freerunning_test`와
`timed_dispatch_test`가 2/2 PASS (0.55 s)이다. 검사에는 stale peer 갱신,
pending 동안 deadline 갱신 차단, enqueue gap, I/O lock 대기와 target delay,
완료 후 native handoff, stop/reset 후 stale token 무효화가 포함된다.
단위 검사 결과이며 실제 Linux PIO/DMA 해결 판정은 아직 아니다.

전체 provider의 최초 빌드는 CPU에서 protected `p_icount`에 직접 접근하여
실패했다 (`qk-demand-provider-build.log`). 읽기 전용 `uses_icount()`로
수정한 재빌드는 성공했다 (`qk-demand-provider-build-retry.log`):
platform 61/61 PASS (6.55 s), core 63/63 PASS (19.33 s).

그러나 새 provider와 기존 PIO WIC/DTB를 사용한 `qk-demand-pio/` 실행은
Linux까지 도달하지 않았다. TF-A PFDI의 core 1 OoR 성공 이후 후속 로그가
없었고, 실행 약 5분 시점에 진단 재실행을 위해 종료했다. 900초 launcher
timeout 판정은 아니며, PIO 트래픽도 수행하지 않았다. 따라서 이 변경의
전체 플랫폼 부팅 회귀는 미해결이다. host GDB attach는 ptrace 제한으로
실패했고 `qk-demand-pio-debug/`에 GDB 부모 실행으로 thread stack을
수집하는 진단을 시작했다. 이 진단 역시 통신 PASS 증거가 아니다.

`qk-demand-pio-debug2/qbox-platform.log`에 GDB 부모 실행으로 180초
시점의 native thread stack을 확보했다. AP CPU0은 `timed_dispatch` 완료
대기, SystemC는 이벤트 처리 중이었다. 해당 실행은 아직 BL2 단계였으므로
일반 실행의 PFDI 정지 원인을 이 snapshot 하나로 확정하지 않는다.
CCI broker 오류 때문에 진단용으로만 fail-pattern 종료를 무시했으며,
정상 부팅/통신 PASS에는 사용하지 않는다.

monitor 관찰과 코드 검토에서 demand refresh가 실제 요청 유무와 관계없이
매 시간 경계마다 live clock을 재샘플링하는 것을 확인했다. 이 경로를
MMIO begin이 다른 freerunning keeper에 보내는 일회성 progress 요청으로
제한했다. 무요청 재갱신 방지 검사를 추가한
`qk-demand-pulse-unit-test.log`는 2/2 PASS이다. 이 수정의 provider 및
실제 부팅/PIO 효과는 아직 검증 중이다. monitor 자료는
`qk-demand-monitor-{status,time}.json`에 보존했다.

후속 read-only 검토에서 두 한계를 확인했다. CPU의 service hook이 모든
regular MMIO의 incoming delay를 먼저 `wait()`하므로, 기존 loosely-timed
부팅/제어 target까지 전역 keeper에 동기화하는 범위 확대가 있었다.
또한 request 20 ns에 peer clock 10 ns인 경우 일회성 pulse가 10 ns 갱신에
소비되어 다음 periodic deadline을 기다릴 수 있다. 현재 100 ns peer /
10 ns request 단위 검사만으로 이 조건을 검증했다고 할 수 없다.
부팅 실패의 확정 원인은 아니며, target delay contract 보존과
outstanding-request 목표 시각 기반 갱신을 별도로 검사해야 한다.

TF-A `drivers/arm/pfdi/pfdi_mod.c`에서 core 성공 로그 다음 단계는
`wait_cpu_off()`이다. 따라서 같은 지점 재현 시 PSCI OFF 완료와 QK
halt/reset 상태를 함께 추적해야 하며, 성공 로그 하나만으로 다음 core의
CPU_ON 요청이 발행됐다고 해석하지 않는다.

### LT service contract 복원 대조

`qk-demand-pulse-provider-build.log`의 recipe 검사는 platform 61/61
(6.53 s), core 63/63 (19.33 s) PASS였다. 그러나
`qk-demand-pulse-pio/` 부팅은 RSE SCMI protocol 조회 재시도 이후 종료했고
Linux 검증에 도달하지 못했다.

이후 service hook의 일괄 `wait(delay)`를 제거하고 incoming delay를
target에 유지했다. SERVICING은 SystemC callback이 request를 소유한
상태이며, target이 annotation을 소비하거나 반환할 수 있도록 했다.
`qk-lt-service-unit-test.log`는 2/2 PASS (0.55 s)이다.
Yocto의 기존 CMake build에서 `apollo_fvp_full_system` target을 증분 빌드해
`--qbox-build-dir`로 명시한 비교 실행(`qk-lt-service-pio/`)은
PFDI core 1~3 및 Linux 로그인/SSH까지 통과했다. binary hash와 실제
loaded maps는 `qk-lt-service-artifacts.sha256`,
`qk-lt-service-loaded-maps.txt`에 보존했다. 이는 설치 recipe 재검증을
대체하지 않으며, 기존 PIO WIC/DTB를 그대로 사용한 대조이다.

PIO 실제 양방향 WAV는 `qk-lt-service-pio-wav/results.json`에 기록했으며
아직 FAIL이다. live DT에는 두 I2S 모두 DMA property가 없었다.
추적 준비 후 수행한 0→1 추가 검사도 캡처 0/EIO였다.
`qk-lt-service-pio-trace.log`의 표본 1개에서 IRQ handler 480.926 ms,
FIFO 쓰기 281.153 ms가 관측됐다. kprobe 포함 구간이며 IRQ assertion
latency나 일반적인 지연 분포는 아니다.

다음 수정은 목표 시각이 있는 peer progress 요청과 별도 QEMU virtual
timer wakeup이다. clock이 목표보다 뒤라면 해당 시각에서 재샘플링하여
기존 10 ms deadline 의존성을 줄이는 방식이며, 아직 runtime 검증 전이다.

### 인스턴스별 virtual clock epoch 차이 확인

목표 시각 wakeup 버전(`qk-deadline-pio/`)도 부팅은 통과했지만,
`qk-deadline-pio-wav/results.json`의 양방향 검사 모두 캡처 0/EIO로
실패했다 (0→1 3.456 s, 1→0 3.194 s). 이에 monitor에 source clock,
request phase, 미충족 goal 개수의 읽기 전용 진단 필드를 추가했다.

`qk-clock-observation-early.json`의 원본 source clock은 AP0
33863974010 ns, SI CL1 CPU0 33852056428 ns로 약 11.918 ms 차이였다.
같은 AP instance의 CPU들은 근접한 시각을 보였다. QEMU 소스에서도
각 instance의 `finish_qemu_init()` → `qmp_cont()` → `cpu_enable_ticks()`가
서로 다른 host 시점에 독립 `cpu_clock_offset`을 정하는 경로를 확인했다.
이 raw VIRTUAL clock들을 공통 절대 시각처럼 QK에서 비교하는 것은
잘못된 교차-domain 지연을 만들 수 있다.

동일 snapshot의 SI CL0에는 이미 완료된 LT 전송의 progress goal이
396641개 남아 있었다. 이를 요청자별 현재 목표 하나로 제한하고 native
전송 완료 시 취소하도록 변경했으며, 교체/취소 회귀 검사를 추가했다.

후속 수정은 common shared library의 host/SC epoch를 기준으로 instance별
고정 affine offset을 설정한다. 첫 VM-running callback에서 vCPU resume
전에 offset을 게시하며, 이후 pause/resume에는 다시 계산하지 않는다.
QK에 전달하는 clock과 요청 시각만 정규화하고, 전용 wakeup timer에는
역변환한 raw deadline을 전달한다. guest timer 값과 기존 raw 10 ms
periodic deadline은 변경하지 않는다. 빌드/실제 PIO 결과는 아직 확인 전이다.

### 공통 epoch 적용 후 PIO 재측정

후속 `qk-shared-epoch-runtime-build.log`의 증분 runtime build는 133/133,
`qk-shared-epoch-unit-test.log`의 선택 CTest는 2/2 PASS (0.55 s)였다.
`qk-shared-epoch-pio/`는 해당 build tree를 명시하여 실제 Linux까지 부팅했다.
전체 recipe 재검증 및 최신 Linux DMA driver 검증을 대체하지 않는다.

`qk-shared-epoch-pio-wav/results.json`의 양방향 WAV는 여전히 FAIL이다.
0→1 3.298 s, 1→0 2.097 s 후 각각 캡처 0 frames/EIO였다.
이후 추적 준비 메시지를 확인한 뒤 0→1 검사를 두 번 더 실행했다.

| 증거 파일 (공통 경로 `build/qbox-apollo-qvp/i2s-final/`) | IRQ 횟수 / 중앙값 | TX FIFO 함수 횟수 / 중앙값 | period callback |
|---|---:|---:|---:|
| `qk-shared-epoch-pio-trace2.log` | 58 / 1.7475 ms | 58 / 0.926 ms | 0 |
| `qk-shared-epoch-pio-trace3.log` | 66 / 1.431 ms | 65 / 0.795 ms | 0 |

두 trace의 entry/exit는 모두 대응한다. trace3에는 RX FIFO 함수도 추가했으나
호출이 없었다. 대응 WAV 검사 `qk-shared-epoch-pio-traced-wav{2,3}/`도
캡처 0/EIO로 실패했다. TX 함수는 한 번에 8 frames를 처리하므로 65회는
520 frames로 첫 1024-frame period에도 못 미친다. 이는 함수 호출 기준
PCM 처리량이며 wire 수신 성공량이 아니다.

Linux `sound/core/pcm_lib.c::wait_for_avail()`은 이 buffer/rate 조건에서
기본 100 ms를 기다린다. 첫 period 완료 전에 timeout될 수 있는 처리속도이나,
RX 함수가 아예 없는 이유는 시작/종료 시각을 추가 추적하여 구분해야 한다.
IRQ 내부 시간에는 kprobe 비용이 포함되며 IRQ assertion latency는 아니다.

현재 Apollo Lua는 이미 `functional_pacing=true`이다. 이는 빈 TX FIFO 대기 및
가득 찬 RX FIFO에 대한 재시도를 제공하는 기능 모드로, 엄격한 I2S wire timing
검증과 구분해야 한다. 이 모드에서도 실패했으므로 FIFO 확대나 무손실 모드
도입만으로 해결했다고 주장할 수 없다.

### PIO START/STOP 추적으로 확인한 비중첩 구간

`qk-shared-epoch-pio-trace4.log`에는 DAI trigger entry/exit를 추가했다.
guest timestamp 기준 capture START 완료 674.047173 s, STOP 진입
674.152999 s, playback START 진입 674.201734 s였다. 캡처가 약
105.826 ms 대기 후 종료한 뒤 48.735 ms가 더 지나서 재생을 시작했다.
따라서 이 실행에서는 두 stream이 겹치지 않았으며 RX 함수 호출 0의
직접 원인이 확인됐다. 이는 TX의 느린 period 진행과 별개의 문제다.
`qk-shared-epoch-pio-traced-wav4/results.json`은 캡처 0/EIO FAIL이다.

기존 PIO 진단 timeout parameter를 포함한 새 커널로 시작 지연을 분리하는
검증이 필요하다. timeout 확대만으로 48 kHz 처리 능력을 검증하거나,
기능 pacing 모드의 성공을 엄격한 serializer timing 성공으로 바꾸어
해석하지 않는다.

추가 코드 검토에서는 native clock에서 SC 시각을 뺀 뒤 `set()` 내부에서
다시 SC 시각을 더하는 이중 샘플링 경쟁을 수정했다. non-icount freerunning만
절대시각 publication을 사용하고, pending/service/ready 단계의 시각은
동결한다. peer progress 목표도 실제 pinned bound와 같게 했다.
`qk-absolute-publication-unit-test.log`는 5/5 PASS (4 ms)이며,
이 변경의 CPU 통합 빌드/실제 Linux 효과는 별도 검증 대상이다.

### 새 커널과 provider 전체 빌드

`./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`를 두 I2S의
DMA property만 임시 제거한 상태로 실행했다. `pio-new-kernel-image-build.log`는
5793 task 전체 성공이다. provider recipe 검사도 platform 61/61 (6.68 s),
core 63/63 (19.44 s) PASS였다. 이 커널에는 PIO 진단 대기시간과 DMA
hardware command-link 변경이 포함된다. PIO에서는 후자를 사용하지 않는다.

WIC/DTB는 `qk-absolute-pio-inputs/`, 해시는
`qk-absolute-pio-artifacts.sha256`에 보존했다. 빌드 완료 후 소스 DTS의
네 DMA property는 원래대로 복원했다. 새 PIO 실제 부팅은
`qk-absolute-pio/`에서 진행하며, 위 빌드 결과는 통신 PASS가 아니다.

### PIO 첫 진행 성공과 drain timeout 분리

새 kernel notes SHA-256은
`8d06b478a027f29662e36787df66e9b77cb5256b5e80f3c0b41a923b957440ec`이다.
실제 DT의 DMA 속성 부재를 확인하고
`/sys/module/designware_i2s/parameters/pio_wait_time_ms`를 0에서 5000으로
설정했다 (`qk-absolute-pio-preflight.log`). 이는 기본값 변경이 아닌
제한된 진단 override이며, 모델의 기존 functional pacing은 유지했다.

`qk-absolute-pio-wait5s-short/results.json`에서 8192 frames 요청에 대해
양방향 모두 6144 frames, 6 periods가 정확히 일치했다. 캡처된 영역에는
zero frame과 mismatch가 없으나 마지막 2048 frames를 확보하지 못했으므로
**두 검사 모두 FAIL**이다. aplay 오류 로그는 없고 arecord는 EIO였다.

`qk-absolute-pio-tail-trace.log`의 추가 0→1 재현에서 TX/RX FIFO 함수가
각각 795회(6360 frames), callback이 각각 6회 발생했다. 마지막 TX
callback은 154.640710 s, playback STOP은 154.750030 s로 약 109 ms
차이다. capture STOP은 159.782236 s였다. entry/exit 불일치는 없다.

`snd_pcm_drain()`은 R/W 경로와 달리 `substream->wait_time`을 무시하고
이 buffer/rate 조건에서 100 ms timeout을 사용한다. 약 0.5 s의 실제
period 처리시간보다 짧아 tail 전송 중 종료되는 경로와 일치한다.
aplay 종료 코드 0만으로 drain 성공을 판정하지 않는다.

수정은 `sound/core/pcm_native.c`에서 선택된 linked-group stream의
`wait_time`을 lock 안에서 복사하고, 기존 drain timeout과 큰 값을 사용하는
것이다. 0/짧은 override는 기존 timeout을 줄이지 않으며,
`no_period_wakeup` 무한 대기는 유지한다. `include/sound/pcm.h`의 필드
설명도 함께 수정했다. `pio-drain-timeout-image-build.log`에서 PIO 커널
재빌드 중이며, 수정 후 실제 WAV 결과는 아직 확인 전이다.

### drain 수정 후 PIO 8-period 전체 비교

`pio-drain-timeout-image-build.log`의 5793 task가 모두 성공했다. WIC/DTB는
`pio-drain-inputs/`, 해시는 `pio-drain-artifacts.sha256`에 보존했다.
소스 DTS의 DMA property는 빌드 후 복원했다. 실제 부팅 `pio-drain/`의
kernel notes SHA-256은
`1bc8c8526dee9904d58261a97940ad420de3ef76e216480d38739a11fdcf43a9`이다.
live DT에서 PIO 구성을 확인하고 `pio_wait_time_ms=5000`을 설정했다.

`pio-drain-short/results.json`은 **양방향 PASS**다. 각 방향 8192 frames,
8 periods 전체 PCM 및 SHA-256이 일치했고 zero frame, XRUN, EIO가 없었다.
host 경과는 0→1 5.219 s, 1→0 5.254 s다. 협상은 S16_LE stereo 48 kHz,
period 1024/buffer 2048, 일반 blocking aplay/arecord이며 RT priority나
CPU affinity override는 없다. 시간 모드는 기본 freerunning/10 ms다.

기존 functional pacing 및 명시적 5초 대기시간을 사용한 **데이터 무결성**
결과이며, 물리적인 48 kHz 실시간 처리 성능을 입증하지 않는다. 기본값 0의
100 ms 대기를 유지한 PIO가 통과했다는 의미도 아니다. 긴 파일, 반복,
불완전 마지막 period 및 DMA는 추가 검사 대상이다.

### 긴 PIO 전송: 잔여 tail 및 RCU 경고

`pio-drain-long/results.json`은 양방향 FAIL이다. 각 196608 frames 중
195584 frames(191 periods)가 정확히 일치했고 zero/mismatch는 없었지만,
마지막 period를 확보하지 못해 capture EIO가 발생했다. 이는 짧은 8-period
PASS를 일반화할 수 없음을 보여준다. `pio-drain/qbox-primary-console.log`에는
CPU0 I2S IRQ thread 실행 중 RCU rcuc starvation 경고도 기록됐다.
`pio-drain-rcu-scheduler.log`의 RT budget은 950000/1000000 us,
I2S IRQ affinity는 둘 다 0-3, RCU thread priority는 1이다.

후속 driver 수정은 PIO playback DRAINING STOP에도 기존 full-FIFO+serializer
대기를 적용한다. 대기 전 PIO TX IRQ를 mask하고, DMA handshake 비활성화는
DMA 경로에만 유지한다. JH7110 및 비-drain STOP 경로는 변경하지 않는다.
PIO 역시 FIFO 쓰기 시점에 PCM pointer가 움직이므로 wire 완료와 구분한다.
단, functional pacing에서 RX FIFO full로 serializer가 정지할 수 있으므로
이 고정 시간 대기만으로 모든 tail을 보장한다고 주장하지 않는다.

IRQ handler는 PIO가 지원하는 stereo pair 하나만 조회하고, sampled ISR에
오류가 있을 때만 해당 TOR/ROR를 읽어 clear하도록 했다. FIFO 처리량이나
가짜 PCM 진행량을 늘리지 않고 불필요한 MMIO 왕복만 줄인다. RCU 구간에
sleep/yield를 삽입하거나 stall timeout을 변경하지 않았다. checkpatch는
오류/경고 0이며 `pio-fifo-drain-image-build.log`에서 재빌드 중이다.

### IRQ 분산 대조: 긴 PIO 양방향 전체 일치

`pio-fifo-drain-image-build.log`의 5793 task가 모두 성공했고,
`pio-fifo-drain/`에서 실제 Linux를 부팅했다. kernel notes SHA-256은
`813fadb11587580a9c206fab774ca4e2ac45eb8f0d3908eb4717ae7ce90b6980`이다.
WIC/DTB는 `pio-fifo-drain-inputs/`, 해시는
`pio-fifo-drain-artifacts.sha256`에 보존했다. 소스 DTS는 DMA로 복원했다.

최적화와 고정 FIFO drain만 적용한 `pio-fifo-drain-long/results.json`은
여전히 양방향 195584/196608 frames로 FAIL이며 RCU 경고도 있었다.
이 실행에서 확인한 두 I2S IRQ는 65/66이고, 모두 실제 CPU0에서 처리됐다.
다음 **진단용 런타임 IRQ 분산**을 적용했다. IRQ 번호는 해당 이미지에서
확인한 값이며 다른 이미지에서 하드코딩하여 재사용하면 안 된다.

```sh
echo 0 > /proc/irq/65/smp_affinity_list
echo 1 > /proc/irq/66/smp_affinity_list
cat /proc/irq/65/effective_affinity_list /proc/irq/66/effective_affinity_list
```

`pio-fifo-drain-irqspread-long/results.json`은 **양방향 PASS**다.
각 196608 frames, 192 periods 전체 PCM/hash가 일치했고 zero frame,
XRUN/EIO는 없었다. host 경과는 0→1 46.260 s, 1→0 50.239 s였다.
이후 serial log에 이전 두 RCU 경고 외의 새 경고는 추가되지 않았다.
`pio-fifo-drain-irqspread-{preflight,after-long}.log`에 IRQ와 kernel log를
보존했다. PIO 대기시간은 5000 ms, 기존 functional pacing은 그대로이며,
모든 CPU domain의 기본 freerunning/10 ms는 변경하지 않았다.

이는 **IRQ 분산을 적용한 조건부 PASS**다. 기본 IRQ 배치에서도 긴 전송이
정상이라는 의미는 아니다. Linux `Documentation/RCU/stallwarn.rst`의
PREEMPT_RT 고우선순위 task/IRQ에 의한 RCU thread starvation 설명과
이번 경고가 부합한다. 기본 보드 정책 적용 여부는 별도로 결정해야 한다.

추가 drain 설계 검토에서 TFCR을 실행 중 0으로 바꿔 FIFO-empty를 poll하는
방안도 고려했으나 적용하지 않았다. 제공된 DW_apb_i2s databook의 TXCHET
설명은 trigger level 변경 전에 TX channel 비활성화를 요구하므로,
현재 모델이 쓰기를 허용한다는 이유만으로 해당 시퀀스를 도입하면 안 된다.

### 반복 START에서 확인한 RT priority inversion

IRQ 분산 후 `pio-fifo-drain-irqspread-odd/results.json`의 양방향
196625-frame 비교도 전체 일치했다. 그러나
`pio-fifo-drain-irqspread-repeat/results.json`은 첫 3회 양방향(6 cases)
PASS 후 4회차 0→1에서 host 180 s timeout으로 종료했다. 이후 케이스는
실행하지 않았다. **IRQ 분산만으로 안정화됐다는 판정은 철회한다.**

serial log는 START 중인 aplay의 `dw_i2s_trigger+0x434`에서 RCU reader가
선점된 상태를 기록했다. 해당 이미지 vmlinux의 심볼/역어셈블 결과,
`dw_i2s_trigger=ffff800080c3a910`, PC `ffff800080c3ad44`는 CER에 1을
쓴 직후다. 즉 IRQ는 활성화됐지만 trigger 반환과 ALSA RUNNING 게시가
아직 끝나지 않은 지점이다. 기존 PIO IRQ는 stream lock 없이
`snd_pcm_running()`을 검사하여 이때 FIFO를 처리하지 않고 반환한다.
level IRQ가 유지되면 높은 우선순위 IRQ thread가 START 태스크를 계속
밀어낼 수 있다. stream lock이 IRQ를 실제로 차단한다고 가정한 초기 검토는
PREEMPT_RT의 sleeping spinlock 동작을 충분히 고려하지 못했다.

`dw_pcm_transfer()`는 RCU pointer의 NULL 검사 후 PCM stream lock을
획득하고 RUNNING 검사, FIFO 전송, pointer 갱신을 수행하도록 수정했다.
callback은 `snd_pcm_period_elapsed_under_stream_lock()`으로 바꾸어
재귀 lock을 피한다. RT spinlock의 PI로 START owner가 RUNNING 게시를
마칠 수 있으며 STOP과 FIFO 접근도 직렬화된다. close의
`synchronize_rcu()` 수명 보호는 유지한다. 현재 atomic PCM 전제이며,
nonatomic PCM 지원을 새로 주장하지 않는다.

checkpatch는 오류/경고 0이다. timeout된 guest는 종료했고
`pio-stream-lock-image-build.log`에서 새 PIO 이미지를 빌드 중이다.
이번 수정의 실제 반복/긴 전송 결과는 아직 확인 전이다.

### Stream lock 적용 후 반복 검사와 userspace starvation

`pio-stream-lock-image-build.log`에서 5793 task가 성공했다. 실제 부팅한
커널 notes SHA-256은
`b9f7bc2bd98ec20997848e3f7d3233df187c76528bbc6971c711a0730def3ad6`이다.
기본 IRQ 배치 반복은 6/10, IRQ 분산 반복은 8/10 PASS였으며 START hang은
재현되지 않았지만 XRUN이 남았다. 각각 `pio-stream-lock-repeat/results.json`,
`pio-stream-lock-irqspread-repeat/results.json`에 결과를 보존했다.

`pio-stream-lock-pointers.log`에서 첫 callback 후 497.426873 s에
hw_ptr=1024/appl_ptr=2048, 다음 callback 후 497.658759 s에
hw_ptr=2048/appl_ptr=2048이었다. 그 사이 application refill이 없었고
497.658842 s에 XRUN이 발생했다. 따라서 이 사례는 가짜 pointer wrap이
아니라 실제 application buffer 소진이다. aplay는 IRQ와 같은 CPU1에서
497.665431 s에 실행을 재개했다.

IRQ0/1을 CPU0/1에 배치하고 정상 SCHED_OTHER aplay/arecord를 CPU2에
배치한 `pio-stream-lock-isolated-repeat/results.json`은 **10/10 PASS**다.
각 방향 5회, 매회 8192 frames 전체 PCM/hash가 일치하고 XRUN/zero frame이
없었다. 실행 명령은 다음과 같다 (경로는 프로젝트 root 기준).

```sh
python3 scripts/test/validate_qbox_i2s_wav.py \
  --out-dir build/qbox-apollo-qvp/i2s-final/pio-stream-lock-isolated-repeat \
  --rounds 5 --frames 8192 --cpu 2 --guest-timeout 90 --host-timeout 180
```

조건은 기존 functional pacing, PIO wait 5000 ms, period 1024/buffer 2048,
S16_LE stereo 48 kHz, 모든 domain의 freerunning/QK 10 ms다. guest의 taskset은
동일 Yocto build의 util-linux 2.40.4 산출물을 임시 복사했다. 기본 이미지에
포함된 도구라고 가정하면 안 된다. CPU affinity는 검증 조건이며 기본 보드
정책을 변경하지 않았다. 긴 전송과 odd tail 및 DMA의 완료 판정은 별도다.

PIO trace callback probe도 현재 driver가 호출하는
`snd_pcm_period_elapsed_under_stream_lock`으로 변경했다. 예전 외부 wrapper만
probe하면 callback 0으로 오판할 수 있다. 관련 Python 검사 11개와 shell
syntax 검사가 통과했다.

동일 조건의 `pio-stream-lock-isolated-long/results.json`도 양방향 PASS다.
각 196608 frames/192 periods 전체 PCM/hash가 일치했고 zero frame 및
aplay/arecord 오류가 없었다. host 경과는 0→1 49.822 s, 1→0 49.154 s다.
명령은 위 명령의 `--rounds 1 --frames 196608 --guest-timeout 180
--host-timeout 240`을 사용했다. 이 결과는 CPU 배치를 분리한 조건이며,
기본 affinity에 대한 앞선 실패를 대체하지 않는다.

`pio-stream-lock-isolated-odd/results.json`은 196625 frames
(192 full periods + 17 frames)도 양방향 전체 일치, zero/XRUN/EIO 없이 PASS다.
host 경과는 48.759 s 및 47.096 s였다. 명령의 frames만 196625로 변경했다.
최종 guest dmesg/interrupts는 `pio-stream-lock-isolated-final-guest.log`에
보존했다. 이 검증용 VM을 종료한 뒤 DMA property가 있는 정상 DTS로
`dma-command-link-image-build.log`의 BSP 빌드를 시작했다. affinity 명령을
재현할 수 있도록 QVP BSP 패키지에 `util-linux-taskset`을 추가했으며,
기본 affinity나 시간 정책을 변경하지 않았다.

DMA BSP 빌드는 5793 task 모두 성공했다 (5716 task 재실행 불필요).
manifest에 `util-linux-taskset 2.40.4`가 포함됨을 확인했다. 저장한 입력은
`dma-command-link-inputs/`, 해시는 `dma-command-link-artifacts.sha256`이다.
`dma-command-link/`에서 기본 freerunning으로 실제 부팅을 시작했으며 두
DMA 인스턴스에 `trace=true`, `trace_filter=operation`, `trace_limit=10000`을
설정했다. 이는 빌드/부팅 시작 기록이지 DMA 통신 PASS가 아니다.

### Hardware command-link 첫 실제 DMA 검사: FAIL

`dma-command-link-preflight.log`에서 동일 kernel notes hash, 두 I2S의
live DT `dmas`, taskset 설치를 확인했다. 기본 affinity와 기본 wait_time을
유지하고 `--rounds 1 --frames 8192 --guest-timeout 90 --host-timeout 180`으로
검사한 `dma-command-link-short/results.json`은 양방향 FAIL이다. 캡처는
모두 0 frames/EIO이며 playback XRUN도 발생했다. host 경과는 141.060 s와
172.304 s다. 성공적인 linked-done trace는 아직 없다.

실제 serial log에 PFDI timeout과 `d350_irq` 경로의 RCU starvation이 있다.
monitor의 `dma-command-link-stall-qk*.json`에서 SystemC 시간보다 native
source time이 수십 초 앞서고 AP CPU가 SERVICING/WAIT_IO 상태인 것을
확인했다. 시뮬레이션 시간은 계속 진행했으므로 완전한 deadlock으로 단정하지
않는다. `dma-command-link-model-snapshot.json`은 trace 활성화도 확인한다.
검사가 종료된 뒤 해당 VM을 종료하고, 같은 이미지로
`dma-command-link-mmio/`에 전체 DMA MMIO trace를 켠 진단 부팅을 시작했다.
이 결과는 command-link의 정상 동작 또는 근본 원인 확정을 뜻하지 않는다.

추가 진단 `dma-command-link-mmio/`는 launcher가 SSH 8023을 선택했다.
8022 접속 시도는 연결 실패였으며 통신 검사 결과로 간주하지 않는다.
8023의 preflight에서 IRQ40(dma1chan0~3)을 확인해 CPU0에 배치하고,
`--port 8023 --direction 0to1 --cpu 2 --frames 8192 --rounds 1
--guest-timeout 60 --host-timeout 120`으로 실행했다.
`dma-command-link-mmio-isolated/results.json`은
`host_timeout_guest_cleanup_required` FAIL이다 (120.741 s).
전체 MMIO trace에는 부팅 시 probe/INTREN 설정만 있고 시험의 CH_CMD ENABLE은
아직 관측되지 않았다. 따라서 command-link fetch/전송 오류가 확인됐다고
판정하지 않는다. 다음 분석 대상은 START 이전 Linux 경로와 QBox의
native/SystemC 시간 차이다. 최종 QK snapshot은
`dma-command-link-mmio-final-qk.json`이며 timeout된 검증 VM은 종료했다.

### Linux 함수 trace로 앞선 시작 전 정체 추정 정정

`dma-start-probe/`의 실제 Linux에서 kprobe entry/return을 수집했다.
`dma-start-functions.log`에서 capture의 descriptor allocation은
264.991165→264.991651 s, `d350_program_cmd`는
264.992278→264.993242 s에 반환했다. START도 264.994884 s에 끝났다.
따라서 allocation 또는 command 설정에 도달하지 못했다는 추정은 이 실행에
해당하지 않는다. capture STOP은 265.109192 s, playback open은
265.211201 s다. 즉 기본 100 ms 대기로 capture가 먼저 종료돼 두 stream이
겹치지 않았다. `dma-start-probe-wav/results.json`은 0 frames/EIO, XRUN FAIL이다.

별도로 `--keep-running-after-pass` 반환 후 Python runtime logger가 사라지고
새 session으로 시작한 QBox만 남는 수명 문제가 확인됐다. QBox stderr는
사라진 reader의 pipe를 계속 참조했다. 따라서 부팅 이후 모델 로그 부재를
MMIO 부재로 해석하면 안 된다. 앞 절의 CH_CMD ENABLE 미관측은 **로그 수집
한계**이며, DMA 시작 전 정체가 입증됐다는 의미를 철회한다.

수정은 두 부분으로 분리한다. keep-running의 Python child도 별도 session으로
유지하여 로그 수집을 보존하고, DW I2S DMA 경로에 `dma_wait_time_ms`를
추가한다. 기본 0은 그대로이며 명시적인 값만 최대 5000 ms로 제한해 ALSA의
기존 wait_time 및 앞서 수정한 drain 경로에 전달한다. 진짜 XRUN을 무시하거나
가짜 PCM 진행을 만들지 않는다. `dma-wait-image-build.log`에서 재빌드 중이다.

keep-running child의 `start_new_session=True` 수정은
`tests/test_qbox_keep_running_lifecycle.py`로 검사했다. launcher 종료 및 기존
process-group 정리 후에도 실제 subprocess logger가 marker를 기록하는 검사,
동기 실행 유지, timeout의 TERM→KILL 경로를 포함한다. 인접 검사와 합쳐
42 PASS이며 `keep-running-lifecycle-tests-python-module.log`에 기록했다.
runtime timeout 자체는 변경하지 않았으므로 긴 guest 검사는 충분한
`--timeout`을 명시해야 한다. Linux driver diff의 checkpatch는 오류/경고 0이다.

### DMA wait override 재검사와 autonomous ring 과진행

`dma-wait-image-build.log`의 5793 task가 모두 성공했다. 저장한 입력은
`dma-wait-inputs/`, 해시는 `dma-wait-artifacts.sha256`이며 실제 kernel notes는
`ce4fb217fd0a8d4ab939b8482bdab1ca984d6ed36d8ceccf4c8bcf7037e4c329`다.
live DT의 DMA 속성을 확인하고 `dma_wait_time_ms=5000`, DMA IRQ40→CPU0,
aplay/arecord→CPU2로 검사했다. 수정 launcher의 runtime logger는 launcher
반환 후에도 별도 session으로 살아 있고 실제 전송 trace를 계속 기록했다.

`dma-wait-short/results.json`은 0→1 0 frames/EIO/XRUN (98.002 s),
1→0 host timeout (180.719 s)으로 FAIL이다. 그러나 이번에는
`dma-wait/qbox-platform.log`에 실제 채널0/3 및2/1의 linked-done이 기록된다.
전체 로그에 6497 linked-done이 있어, 8192 frames 요구에 비해 autonomous
ring이 Linux 서비스 없이 지나치게 많이 진행한 것이 드러났다. 이 로그를
무손실 통신 PASS로 해석하지 않는다. 종료 후 해당 검증 VM은 정리했다.

TRM의 DONEPAUSEEN을 사용하는 선택적 `cyclic_done_pause` driver 경로를
추가했다 (기본 false, 준비한 descriptor별 고정). 실제 완료마다 PAUSED와
RESUMEWAIT를 확인하고 기존 virt-dma tasklet에서 client callback을 실행한 뒤
RESUME한다. 수동 pause, callback 전 사용자 resume, terminate/error 및
descriptor reuse를 구분한다. callback 소비를 제한할 뿐 userspace refill까지
보장하지 않으며, physical continuous audio timing 검증과도 다르다.

SystemC의 기존 Linux descriptor 형식 TX/RX 검사에 DONEPAUSE 변형을 추가해
DONE acknowledge 후에도 새 peripheral request가 ring을 진행시키지 않고,
RESUME 이후에만 진행하는 것을 확인했다. 큰 XSIZEHI 경계도 함께 검사한다.
`dma-donepause-expanded-tests.log`: 관련 5 tests PASS (0.05 s).
`dma-donepause-image-build.log`에서 통합 BSP를 빌드 중이며 새 driver 경로의
실제 Linux 통신 결과는 아직 미확인이다.

### DONEPAUSE 실제 Linux WAV 검사 결과

후속 통합 BSP 빌드는 5793 tasks 성공이다. 위의 빌드 중/미확인 상태는
이 결과로 갱신한다. 부팅 입력은 `dma-donepause-inputs/`, 해시는
`dma-donepause-artifacts.sha256`이며 kernel notes SHA-256은
`e9deac13c2c1c24a56f3fd3d07f6f1b4c7167d16f6b51bb3509816225376e06a`다.
provider do_check는 platform 61 tests (5.66 s), core 63 tests (22.67 s) PASS다.

실제 QBox Linux에서 두 I2S의 live DT `dmas`를 확인했다. 모든 CPU 도메인의
기본 freerunning/QK 10 ms를 유지하고 다음 실행 조건을 명시적으로 적용했다.
모듈 옵션 및 CPU affinity의 기본값을 변경한 결과가 아니다.

```sh
echo Y > /sys/module/arm_dma350/parameters/cyclic_done_pause
echo 5000 > /sys/module/designware_i2s/parameters/dma_wait_time_ms
echo 0 > /proc/irq/40/smp_affinity_list
```

IRQ 번호 40은 이 부팅의 DMA350_1 IRQ이며 다른 이미지에서는
`/proc/interrupts`로 확인해야 한다. WAV runner의 `--cpu 2`로 두 앱을
CPU2에서 실행했다. S16_LE/stereo/48000 Hz, period 1024/buffer 2048이며
실제 `aplay`/`arecord`의 전체 PCM 및 SHA-256을 비교했다. prefix 건너뛰기,
zero 제거, XRUN 복구를 성공으로 처리하지 않는다.

| Evidence directory | 검사 | 결과 |
|---|---|---|
| `dma-donepause-short/` | 양방향 각각 8192 frames | 2/2 PASS |
| `dma-donepause-long/` | 양방향 각각 196608 frames, 192 periods | 2/2 PASS |
| `dma-donepause-repeat/` | 양방향 각각 10회, 회당 8192 frames | 20/20 PASS |
| `dma-donepause-odd/` | 양방향 각각 196625 frames, 마지막 17 frames 포함 | 2/2 PASS |

각 디렉토리의 `results.json`에 전체 PCM 일치, zero frames 0 및 XRUN 없음이
기록되어 있다. 긴 검사 host 경과는 16.701 s / 17.400 s다. 실제 DMA350_1의
채널0/3 및2/1 linked 전송도 `dma-donepause/qbox-platform.log`에서 확인했다.

이는 DONEPAUSE와 기존 I2S `functional_pacing`을 이용한 **조건부 데이터
무결성 PASS**다. autonomous cyclic 옵션을 끈 앞선 FAIL을 대체하거나
물리적 연속 48 kHz 타이밍 PASS를 뜻하지 않는다. callback 반환은 userspace
refill 완료를 보장하지 않으므로 부하 조건까지 일반화하지 않는다. 홀수 길이,
pause/resume 및 다른 DMA 주변장치 회귀 검사는 별도로 기록한다.

### DMA 회귀와 수동 pause의 별도 결함

같은 부팅에서 `verify_qbox_dma350.sh`를 실행하고 guest 결과와 실제 model
trace를 `validate_qbox_dma350.py`로 대조했다.
`dma-donepause-regression.json`: PASS, errors 없음, memory 10 operations,
전체 334 operations. SPI0/1의 64/4099-byte DMA와 SG, UART0/1 양방향,
memory copy/fill, shared IRQ 및 I2C PIO 검사가 통과했다.
`dma-donepause-residue.log`의 polled copy/set 각 64 KiB/2 MiB, 총 20 tests도
PASS다. `dma-donepause-final-guest.log`에 RCU stall/BUG/Oops/WARNING은 없다.

추가한 `scripts/test/i2s_pcm_pause.c`는 실제 ALSA의 pause capability와
PAUSED/RUNNING 상태를 검사하고 16384 frames를 정확히 비교한다. 기존
Yocto sysroot/toolchain으로 `-Wall -Wextra -Werror` 교차 빌드했다.
`dma-donepause-pause-tx-0to1.log`는 TX pause/resume 후 frame 2064 불일치로
**FAIL**이다. 일반 WAV 전송 PASS와 구분한다.

원인 경로는 DW I2S trigger의 PAUSE_PUSH가 `dev->active`를 감소시키고
마지막 stream이면 `i2s_stop()`에서 IER=0을 쓰는 것이다. 제공된 databook
5.1.1 IER는 이 동작이 모든 FIFO를 flush한다고 명시한다. SystemC의 FIFO
flush를 제거하지 않고, driver가 paused stream도 active ownership에 포함해
global disable을 피하도록 수정했다. PAUSE_RELEASE는 중복 증가하지 않고,
실제 STOP/SUSPEND는 기존대로 감소한다. 다른 stream의 STOP도 paused
stream의 FIFO를 flush하지 않아야 한다.

검증 VM을 종료한 뒤 `./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`로
재빌드를 시작했다 (`dma-pause-preserve-image-build.log`). 이 수정의 runtime
효과는 아직 미검증이며, pause/release와 pause/STOP의 수명 검사가 남아 있다.

### FIFO 보존 수정 후 실제 pause/resume 재검사

후속 빌드는 5793 tasks 모두 성공(5717 재실행 불필요)했다. 새 입력은
`dma-pause-preserve-inputs/`, 해시는 `dma-pause-preserve-artifacts.sha256`이다.
실제 부팅 kernel notes SHA-256은
`e9493c78cd7652331bb32da7d8e961aea98de42f946655b92f11ec8fdc3a7a59`이며
동일한 DONEPAUSE/wait/affinity 조건을 유지했다.

첫 재검사에서 이전 frame 2064 불일치는 사라졌다. 다만 도구가 nonblocking
drain의 `-EAGAIN`만 보고 계속 기다렸다. 실제 `/proc/asound` snapshot에서는
playback SETUP, TX/RX 모두 hw_ptr=appl_ptr=16384였다. 이를 PASS로 바꾸지
않고 해당 실행을 종료하고 로그를 보존했다. 도구를 수정해 EAGAIN일 때
실제 SETUP 상태도 확인하도록 했다. 전체 frame 비교와 timeout은 유지한다.

수정 도구 `pause-test-v2`를 동일 Yocto sysroot로 교차 빌드한 뒤 실행한
`dma-pause-preserve-v2-{tx,both}-{0to1,1to0}.log` 네 건은 모두 PASS다.
각각 16384 frames 전체 일치, 실제 PAUSED/RUNNING 전환 및 drain/close를
확인했다. TX 단독 pause와 TX/RX 동시 pause 모두 양방향에서 통과했다.
일반 WAV 및 PIO 최종 이미지 회귀와 paused 상태에서 STOP하는 수명 검사는
이 결과와 별도로 수행해야 한다.

동일 커널의 `dma-pause-preserve-wav/results.json`은 196625-frame WAV
양방향 모두 전체 PCM 일치, zero frames 0으로 PASS다. 호스트 검증 도구의
focused pytest 16개도 PASS (`pause-preserve-host-tests.log`)다.
PIO 최종 이미지와 paused STOP 검증은 아직 남아 있다.

후속 `pause-test-v3`는 `drop` 모드를 추가해 최소 2048 frames를 정확히 비교한
뒤 TX/RX를 PAUSED로 전환하고, resume 없이 각각 drop/SETUP/close를 확인한다.
전체 파일 비교가 아닌 의도적 취소 수명 검사이며 별도
`I2S_PAUSED_STOP_PASS` marker를 사용한다.
`dma-pause-preserve-drop-{0to1,1to0}.log` 양방향 모두 PASS다.
기존 `tx`/`both` 모드의 전체 비교 조건은 변경하지 않았다.

paused STOP 이후 재사용 검사 `dma-pause-preserve-repeat/results.json`도
8192 frames 양방향 각 5회, 총 10/10 PASS다. 이후 guest dmesg/IRQ를
`dma-pause-preserve-final-guest.log`에 보존하고 해당 VM을 종료했다.
최종 PIO 대조를 위해 DTS의 I2S 두 node에서만 `dmas`/`dma-names` 네 속성을
임시 제거하고 BSP 빌드를 시작했다 (`pio-pause-preserve-image-build.log`).
기본 DMA 연결 구성을 바꾸려는 변경이 아니며 빌드 완료 후 복구한다.

### 최종 커널의 PIO 대조

`pio-pause-preserve-image-build.log`: 5793 tasks 모두 성공(5711 재실행 불필요).
PIO WIC/DTB는 `pio-pause-preserve-inputs/`에 보존하고 해시를
`pio-pause-preserve-artifacts.sha256`에 기록했다. 이후 소스 DTS의 네 DMA
속성을 복구했으며 해당 파일의 Git diff가 비어 있음을 확인했다.

실제 PIO 부팅의 kernel notes SHA-256도
`e9493c78cd7652331bb32da7d8e961aea98de42f946655b92f11ec8fdc3a7a59`로
DMA 검사와 동일하다. live DT에서 두 I2S의 `dmas` 부재와 IRQ65/66을 확인하고
PIO wait 5000 ms, IRQ CPU0/1, 앱 CPU2 조건을 적용했다.
`pio-pause-preserve-repeat/results.json`: 양방향 각 5회, 8192 frames,
총 10/10 전체 PCM 일치 PASS다. 긴 odd-tail 검사는 별도 실행 중이다.
PIO driver는 pause capability를 광고하지 않으므로 PIO pause 지원 PASS를
주장하지 않는다. DMA에서 검증한 pause 기능과 구분한다.

`pio-pause-preserve-long-odd/results.json`은 **부분 FAIL**이다. 196625 frames의
0→1은 앞 196608 frames가 정확히 일치하지만 마지막 17 frames를 받지 못하고
arecord EIO로 종료했다 (62.320 s). 1→0은 전체 일치 PASS (48.816 s)다.
따라서 앞선 PIO odd-tail PASS를 최종 커널의 안정성 보장으로 일반화할 수 없다.
TX FIFO drain/RX 마지막 period 처리 문제를 구분하기 위해 8209-frame
양방향 반복 검사를 `pio-pause-preserve-odd-repeat/`에서 추가 실행한다.
최종 PIO 검증이 완료되지 않았으므로 목표 완료로 판단하지 않는다.

`pio-pause-preserve-odd-repeat/results.json`: 8209 frames 양방향 총 10회 중
8 PASS, 2 FAIL이다. 실패는 iteration 2의 1→0 및 iteration 5의 0→1이며
둘 다 앞 8192 frames까지 정확히 일치하고 arecord EIO로 마지막 부분을
반환하지 못했다. WAV runner에 playback 종료 직후 capture PCM status를
기록하도록 추가했다 (판정/데이터/동기화 조건은 그대로). 관련 pytest 8개
PASS이며 `pio-odd-tail-status/`에서 후속 pointer snapshot을 수집 중이다.

### 마지막 PIO period의 부족량 확인과 threshold 진단

첫 status 수집 10회는 모두 PASS였다. 추가 반복
`pio-odd-tail-status-repeat/02-1to0/ssh.log`에서는 playback 종료 직후
capture RUNNING, hw_ptr=9208, appl_ptr=8208, avail=1000을 확인했다.
8209-frame 파일의 마지막 period까지 aplay가 전송하는 길이는 9216 frames다.
실제 ALSA utils 소스에서 `pcm_write()`는 마지막 부분을 period까지 silence로
채우고, `pcm_read()`도 마지막 17 frames를 period 단위로 읽은 뒤 필요한
길이만 파일에 반환한다. 따라서 마지막 period의 8-frame 부족으로 전체
17-frame 파일 조각이 반환되지 않는 경우를 확인한 것이다. 단순히 원본의
마지막 17개 모두가 wire에서 사라졌다고 단정하지 않는다.

고정 FIFO drain 시간 이후에도 RX 서비스 지연으로 TX FIFO가 남는 가설을
검증하기 위해 default false인 `pio_fifo_empty_irq` 옵션을 추가했다.
채널이 비활성인 기존 hw configuration 단계에서 TFCR=0을 선택하며,
PIO DRAINING STOP에서 IRQ를 막은 뒤 실제 TXFE를 최대 10 ms bounded poll하고
최저 threshold와 serializer를 위해 2-frame 시간을 추가로 기다린다.
timeout은 명시적 오류이며 숨기지 않는다. 원래 PIO threshold와 DMA 경로는
기본값에서 그대로다. TFCR는 동작 중에 재설정하지 않는다.

이는 아직 검증 전 진단 구현이다. 모델의 FIFO flush나 실제 데이터는 바꾸지
않는다. 기존 timed PIO보다 낮은 TX watermark는 CPU 서비스 여유를 줄이므로
물리적 연속 오디오의 일반적인 성능 개선으로 주장하지 않는다.
driver diff checkpatch: 0 errors / 0 warnings.

기존 경로의 추가 반복은 최종 30회 중 25 PASS / 5 FAIL이다.
iteration 2/7의 1→0 및 iteration 12의 0→1 실패 snapshot 모두
hw_ptr=9208, appl_ptr=8208로 같은 부족량을 보였다. 해당 VM의 최종 로그는
`pio-pause-preserve-final-guest.log`에 보존하고 종료했다.
PIO DT 임시 구성을 다시 적용한 뒤 `pio-empty-threshold-image-build.log`로
진단 옵션이 포함된 BSP 빌드를 시작했다. 완료 후 입력을 보존하고 소스 DTS의
DMA 속성을 복구해야 한다. 아직 새 옵션의 runtime PASS를 주장하지 않는다.

### PIO lowest-threshold 경로의 실제 부팅

`pio-empty-threshold-image-build.log`: 5793 tasks 모두 성공, 5711 재실행 불필요.
provider `log.do_check.1115935`: platform 61/61 (5.66 s), core 63/63
(19.30 s) PASS다. WIC/DTB 입력은 `pio-empty-threshold-inputs/`, 해시는
`pio-empty-threshold-artifacts.sha256`에 보존했다. 소스 DTS의 DMA 속성은
복구했고 해당 파일의 Git diff가 비어 있음을 확인했다.

실제 kernel notes SHA-256은
`2b29a4d278f1cb6b338805658e3e5ce53cc5284fdead88322a02be9f38bcae3a`다.
live DT에서 I2S 두 node의 `dmas` 부재를 확인했고 아래 조건으로 검사한다.

```sh
echo Y > /sys/module/designware_i2s/parameters/pio_fifo_empty_irq
echo 5000 > /sys/module/designware_i2s/parameters/pio_wait_time_ms
echo 0 > /proc/irq/65/smp_affinity_list
echo 1 > /proc/irq/66/smp_affinity_list
```

IRQ 번호는 이 부팅에 해당한다. 앱은 CPU2, normal scheduling이며 all-domain
freerunning/QK 10 ms는 유지했다. `pio-empty-threshold-odd-repeat/`에
8209 frames 양방향 각각 15회 검사를 진행 중이다. 원래 파일을 잘라내거나
추가 padding하여 통과시키지 않으며, 기존 aplay/arecord 동작 그대로다.

`pio-empty-threshold-odd-repeat/results.json`은 최종 **30/30 PASS**다.
같은 8209 frames/period 1024/buffer 2048 및 CPU 배치에서 기존 경로의
25/30과 비교된다. 각 case의 전체 PCM/hash 일치, zero frames 0, PCM 오류
없음을 검사했다. `pio-empty-threshold-long-odd/`에서 196625-frame 양방향
검사를 추가 실행 중이며, 이 긴 검사 결과는 아직 미확인이다.

후속 `pio-empty-threshold-long-odd/results.json`은 양방향 모두
196625 frames 전체 일치, zero frames 0, PCM 오류 없음으로 PASS다.
host 경과는 51.373 s / 52.535 s다. `pio-empty-threshold-final-guest.log`에서
drain threshold timeout, overrun, RCU stall, BUG/Oops/WARNING은 없었다.
따라서 최저 TX threshold와 실제 threshold 확인을 사용한 명시적 PIO 경로는
짧은 odd-tail 반복 30회와 긴 odd-tail 양방향 검사를 통과했다. 원래 경로의
간헐적 FAIL 이력은 유지하며, 옵션을 끈 경로까지 고쳐졌다고 주장하지 않는다.

### 기본 DMA 이미지 복원 빌드의 간헐적 core test 실패

`final-dma-image-build.log`는 provider do_check의
`aarch64-managed-timer-wfi-baseline`이 `Simulation stopped` 후 30 s timeout으로
실패했다 (`log.do_check.1161512`). 앞선 동일 유형의 종료 문제와 구분 없이
성공으로 처리하지 않는다. 별도 `ctest --repeat until-fail:3` 재검사는
세 번 모두 2.52 s PASS였다 (`final-dma-timer-baseline-recheck.log`).
test 제외나 설정 변경 없이 동일 BSP 빌드를 `final-dma-image-build-retry.log`로
재실행한다. 재시도 성공이 간헐적 QBox 종료 문제 자체의 수정을 뜻하지 않는다.

재시도는 5793 tasks 모두 성공(5764 재실행 불필요)했다.
provider `log.do_check.1190323`: platform 61/61 (5.53 s), core 63/63
(19.08 s) PASS다. 기본 DMA WIC/DTB를 `final-dma-inputs/`에 보존하고
`final-dma-artifacts.sha256`에 hash를 기록했다.

실제 최종 DMA 부팅의 kernel notes는 PIO와 동일한
`2b29a4d278f1cb6b338805658e3e5ce53cc5284fdead88322a02be9f38bcae3a`다.
두 I2S의 live DT `dmas`가 존재하고 `pio_fifo_empty_irq`의 기본 N을 확인했다.
기존 조건대로 DONEPAUSE=Y, DMA wait=5000, DMA350_1 IRQ CPU0/apps CPU2로
최종 DMA 검사를 진행한다. 원래 source DT의 TX/RX DMA 연결을 유지했다.

최종 DMA의 `final-dma-odd-repeat/results.json`은 8209 frames 양방향 각
10회, 총 20/20 PASS다. `final-dma-long-odd/results.json`도 196625 frames
양방향 전체 PCM/hash 일치, zero frames 0, PCM 오류 없음으로 PASS다.
`final-dma-pause-{tx,both,drop}-{0to1,1to0}.log`는 TX 단독/양쪽 pause-resume
각 16384 frames 전체 일치 4건, paused STOP/close 2건 모두 PASS다.
다른 DMA 주변장치 회귀는 `final-dma-regression.log`에서 실행 중이다.

최종 `final-dma-regression.json`은 PASS (errors 없음, memory 10 operations,
전체 357 operations)다. SPI0/1, UART0/1 양방향, memory copy/fill 및 shared
IRQ를 guest 비교와 실제 model trace로 확인했다. `final-dma-residue.log`는
64 KiB/2 MiB의 polled copy/set 총 20 tests PASS다.
paused STOP 및 주변장치 회귀 후 `final-dma-after-drop/results.json`의
8192-frame WAV도 양방향 전체 일치 PASS다. `final-dma-guest.log`에서
RCU stall/BUG/Oops/WARNING/overrun/drain threshold timeout은 없었다.
검증 VM은 종료했으며, 기본 deploy WIC/DTB는 DMA 구성으로 복원돼 있다.
PIO의 정렬 길이 종료를 마지막 대조하기 위해 이미 검증한 PIO 입력을
`final-pio-aligned/`에서 별도로 부팅한다. rebuild나 기본 산출물 교체는 없다.

마지막 `final-pio-aligned-wav/results.json`은 8192 frames 양방향 각 3회,
총 6/6 전체 PCM 일치 PASS다. 같은 kernel notes와 live PIO DT를 다시 확인했고,
최저 threshold/wait/affinity 조건도 동일하다. 최종 guest log에 drain timeout,
overrun, RCU stall/BUG/Oops/WARNING은 없었다. 해당 검증 VM은 종료했다.
기본 deploy WIC/DTB가 `final-dma-inputs/`의 검증한 DMA 입력과 byte-for-byte
동일함을 확인했으며 source DTS의 임시 PIO 변경도 없다.

**결론:** 명시적 기능 pacing 조건에서 최종 커널의 PIO WAV 38건, DMA WAV
24건, DMA pause/resume 및 paused STOP, SPI/UART/memory/residue 회귀를
검증했다. 기본 freerunning/QK 모드는 유지한다. 옵션을 끈 경로 및 물리적
연속 48 kHz 타이밍의 제한은 위 실패 기록과 별도로 남는다.
재현 조건과 최종 결과 표는 [요약 문서](i2s-freerunning-validation.md)에 정리했다.

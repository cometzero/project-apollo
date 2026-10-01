# 구현 및 실험 기록

> **코드 정리 후 상태:** 아래 실험 수치와 명령은 정리 전 artifact의 기록이다.
> 계측, IRQ cache, scheduling/반복 실행/UKI 교체 도구는 live source에서 제거하고
> [패치](patches/README.md)로 보관했다. 해당 실험 명령은 패치 재적용·재빌드가 필요하다.
> 현재 남긴 코드와 검증 범위는 [코드 정리 기록](05-code-cleanup.md)을 따른다.


작성일: 2026-10-01. **구현·대조 실험 결과: 기본 full DMA는 FAIL, 명시적 CFS scheduling 조건에서는 반복 PASS이다.**

증거 root: [dma-i2s-implementation-20261001](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/).
freerunning, quantum_keeper, 10ms quantum, AP 4 CPU, full firmware domain 및 I2S frame period는 유지한다.

## 최종 관측 요약

| 구성 | 반복 | Memory | PCM | WAV 전체 일치 | 판정 |
|---|---:|---:|---:|---:|---|
| Full DMA 기본 정책 | 1 | 20/20 | 0/4 | 0/2 | FAIL |
| Full DMA: IRQ OTHER + audio nice −10 | 3 | 60/60 | 12/12 | 6/6 | DIAGNOSTIC PASS |
| Full PIO 기본 정책 | 3 | 60/60 | 12/12 | 6/6 | 해당 반복 PASS |
| AP DMA 기본 정책 | 3 | 60/60 | 12/12 | 6/6 | 해당 반복 PASS |
| AP PIO 기본 정책 | 3 | 60/60 | 11/12 | 6/6 | 간헐적 PCM FAIL |

Full DMA 성공 조건은 [선택적 guest script](patches/05-audio-experiment-tools.patch)로
적용한다. 같은 부팅의 3회 반복이며 각 WAV는 48kHz S16_LE stereo,
96000 frames 및 원본 전체 파일과 동일하다. 성공한 full 부팅은 BSP 22/22이고
CFS 후보에서는 PFDI timeout/RCU stall이 관측되지 않았다. 모든 full domain과
freerunning을 유지했다. 기본 정책 해결, PFDI의 모든 deadline 검증, cold/warm
각 10회 gate, physical/FVP parity는 달성했다고 주장하지 않는다.


## 계측 전 재현

| 실행 | DMA memory / PCM / WAV | PIO memory / PCM / WAV | 관측 |
|---|---|---|---|
| [Full baseline-2](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/baseline-full-2/result.json) | PASS / 4/4 / 0/2 | PASS / 4/4 / 2/2 | DMA WAV 양방향 XRUN 및 capture timeout |
| [AP baseline-1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/baseline-ap-1/result.json) | PASS / 4/4 / 2/2 | PASS / 3/4 / 미완료 | PIO 동시 정방향 EPIPE, 이후 WAV start에서 aplay RCU stall |

첫 `baseline-full-1`은 `--timeout 1800`을 float `1800.0`으로 전달하여 runner argparse가 거부했다. 부팅 전 도구 오류이며 hardware FAIL과 분리한다. Full verifier의 timeout type을 runner 계약과 동일한 int로 수정했다.

기존 성공은 반복 안정성을 보장하지 않는다. 이번 재현에서는 full DMA PCM이 통과했지만 WAV가 실패했고, AP-only에서도 PIO 실패가 나타났다. Profile 하나만으로 원인을 단정하지 않는다.

## 추가한 진단 경로

- QEMU native model: 기본 OFF인 `QEMU_AUDIO_TELEMETRY=1` 또는 qdev `telemetry=true`. DMA channel별 commands/DONE/beat/residue 및 DONE→ENABLE 지연, I2S frame/FIFO/callback lateness를 bounded summary로 기록한다. 기능·clock 정책은 바꾸지 않는다.
- QBox bridge: `QBOX_INITIATOR_TELEMETRY_DIR` 및 socket filter. CPU/global root별 DMI/MMIO alias와 regular TLM fallback, transport/BQL/recursive-lock 지연을 JSONL로 기록한다. DMI hit rate를 추정하지 않는다.
- 두 verifier: `--diagnostics`, `--pcm-binary`, `--kprobes`, 진단 전용 `--disable-cpu-idle`. private trace instance 및 guest manifest를 bounded archive로 회수한다. `aplay`가 XRUN 후 exit 0을 반환하더라도 결과는 FAIL이다.
- PCM checker: `I2S_LOOPBACK_DIAGNOSTICS=1`에서 오류 직후 ALSA status와 procfs hw_ptr/appl_ptr를 추가 출력한다. sample 비교/period/buffer/recovery 정책은 유지한다.
- [trace summary 도구](patches/05-audio-experiment-tools.patch): native event와 bridge checkpoint, guest의 첫 XRUN 및 inferred-wrap 사건을 요약한다.

배포 kernel은 PREEMPT_RT/HZ250, FTRACE/KPROBE_EVENTS, verbose ALSA procfs를 제공하지만 SND_DEBUG는 꺼져 있다. ALSA tracepoint 대신 **일치하는 Image/vmlinux에서 추출한 offset**의 선택적 kprobe를 사용한다. 정의 파일의 Image SHA256과 실제 kernel이 다르면 verifier가 거부한다. Offset의 근거는 [audio-kprobes-evidence.json](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/audio-kprobes-evidence.json)에 보관한다.

## 첫 XRUN 계측 결과

[trace-full-dma-2 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/trace-full-dma-2/dma/guest-trace-analysis.md)에서 capture `hw_ptr=18432`, `appl_ptr=2048`, buffer=16384였다. Native I2S는 RX 18448 frames 중 FIFO에 16 frames가 남아 RAM 전달량 18432와 일치한다. `alsa_wrap`은 0회다. 이 사건은 실제 capture overrun이며 시간 기반 가짜 wrap으로 설명되지 않는다.

START 복귀부터 첫 XRUN까지 502.757ms 중 application은 runnable 상태로 368.705ms(73.34%) 동안 CPU 밖에 있었다. CPU2는 이 구간에 idle에 들어가지 않았다. CPU0–3의 deep idle usage도 실행 전후 모두 0이다. 오디오 task로 필터한 trace이므로 비오디오 task 사이의 전환은 일부 없으며, 이 시간을 특정 task 하나의 독점으로 단정하지 않는다.

DMA global address space는 RAM alias 3개와 native I2S MMIO alias 2개를 사용했다. Regular fallback은 초기 4건뿐이었다. 따라서 DMA RAM/오디오 MMIO에 추가 DMI를 적용하는 P1/P2는 현재 원인의 해결책으로 채택하지 않는다. AP CPU의 다른 MMIO 비용과 BQL 지연은 별도이다.

첫 `trace-full-dma-1`의 guest archive는 BusyBox `wget --post-file`의 `strlen()` 처리로 gzip 첫 NUL에서 잘렸다(3 bytes). native/PCM 로그는 유효하지만 guest trace는 **NOT_COLLECTED**로 정정했다. ASCII base64 전송과 서버의 tar 검증을 추가한 두 번째 실행은 정상 회수했다.

## PIO 수정과 1차 회귀

`dw_pcm_transfer()`가 PCM stream lock을 취한 뒤 RUNNING 확인/FIFO 서비스를 수행하고, 같은 lock에서 `snd_pcm_period_elapsed_under_stream_lock()`을 호출하도록 변경했다. PREEMPT_RT의 threaded IRQ가 START 상태 전환을 선점한 상태에서 FIFO를 서비스하지 못하는 경쟁을 방지한다. 기존 RCU 수명 계약과 기본 nonatomic 정책은 유지한다.

kernel deploy 빌드가 통과했다. 수정 Image SHA256은 `9a75d661e1d0ee3c9e4b1858d008d6100f530f8c2d5e00d2d265a522e6318328`이다. Full에서는 기존 unsigned BSP WIC의 private copy 양 slot `.linux`를 교체했다. PIO 선택에는 `.dtb`의 DMA 속성 제거도 필요하며, 이 두 section 외 내용과 원본 WIC는 보존했다.

| 실행 | 결과 |
|---|---|
| [PIO AP 1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pio-lock-ap-1/result.json) | DMA memory PASS, PCM 4/4 PASS, WAV 2/2 byte-identical PASS |
| [PIO full 1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pio-lock-full-1/result.json) | DMA memory PASS, 동시 PCM 중 XRUN 잔존, WAV 2/2 PASS; 전체 FAIL |

WAV harness는 recorder의 RUNNING 상태를 bounded wait로 확인하며 양쪽 ALSA 명령에 `--fatal-errors`를 사용한다. 실패 후 자동 recovery로 sample 손실을 숨기지 않는다. 기존 sample 수, period/buffer, 48kHz S16_LE stereo 조건은 유지한다.

## 시간 및 PFDI 경로의 해석

Guest CNT counter와 native audio timer는 steady state에서 같은 AP QEMU virtual clock을 사용한다. SystemC/host clock이 항상 분리돼 drift한다는 설명은 맞지 않는다. Counter mirror anchor가 바뀌는 경로는 별도로 확인한다. 기존 `apollo_timer_snapshot`의 synchronize 호출은 counter anchor에 영향을 주므로 이번 순수 계측에 사용하지 않는다.

Full에는 AP-only와 달리 실제 PFDI EL3/SCMI/SI CL0 경로가 활성화돼 있다. Sample app은 CPU0–3의 test 0..40을 60ms 주기로 요청하며 각 worker는 FIFO99이다. Kernel worker의 동기 SMC는 TF-A의 post-run SCMI 보고에서 응답까지 polling한다. AP-only SMC stub은 PFDI를 지원하지 않아 module 초기화가 실패한다. 기존 `pidof`만 보는 PFDI service PASS는 실제 검사 성공을 뜻하지 않는다.

PFDI app의 blocking timerfd 및 kernel completion wait도 존재하므로 FIFO99라는 사실만으로 전체 지연을 설명할 수 없다. Worker를 SCHED_OTHER로 바꾼 대조군도 실패했다. PFDI 함수 전체 시간과 실제 SMC entry/return 지연을 분리한다. PFDI 중단, CPU coverage 축소 또는 freerunning 변경으로 성공 판정을 만들지 않는다.

이번 `no_period_wakeup=0`인 ALSA period callback 경로의 시간 기반 wrap 보정은 단순 sample-rate 저하만으로 실행되지 않는다. 함수 인자 `in_interrupt=1`, expected pointer보다 작은 현재 pointer, 44 ticks 이상 지난 update가 함께 필요하다(HZ250, buffer_jiffies=85). 이 인자는 hardirq context를 뜻하지 않는다. 별도의 `no_period_wakeup` 보정 경로와 구분하며, 해당 분기의 kprobe와 실제 DMA 완료량을 대조한다.

PREEMPT_RT의 spinlock/IRQ 의미는 [Linux locking 문서](https://docs.kernel.org/locking/locktypes.html), stream lock 안의 period callback 계약은 [ALSA driver API](https://docs.kernel.org/6.17/sound/kernel-api/alsa-driver-api.html)를 참고하며 실제 적용은 현재 kernel 소스를 기준으로 한다.


## P4 대조군 결과

아래 처음 세 실행은 기존 BSP UKI kernel을 사용하고, 결합 대조군은 수정 kernel을 사용한다. PFDI config 및 주기,
각 CPU 검사 범위와 full domain은 유지한다. 변경한 guest scheduling 값은
suite 종료 후 복원하며 별도 `DIAGNOSTIC` 결과로 기록한다.

| 실행 | 변경 | PCM | WAV 정방향 / 역방향 | 판정 |
|---|---|---|---|---|
| [pfdi-other-full-dma-1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pfdi-other-full-dma-1/result.json) | PFDI worker FIFO99 → OTHER0, 계측 ON | 2/4 | FAIL 1024 / 7168 frames | 우선순위 변경만으로 해결 안 됨; 4 worker FIFO99 복원 확인 |
| [affinity-full-dma-1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/affinity-full-dma-1/result.json) | DMA0/I2S0 IRQ CPU1, DMA1/I2S1 IRQ CPU2, suite CPU3 | 0/4 | FAIL 6144 / 16400 frames | CPU 배치만으로 해결 안 됨 |
| [affinity-fifo40-full-dma-1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/affinity-fifo40-full-dma-1/result.json) | 위 배치 + suite FIFO40 | 3/4 | FAIL 28688 / 24580 frames | 순차 PCM 성공, 동시 PCM 및 WAV 실패; 채택 안 함 |
| [pfdi-other-affinity-rr40-full-dma-1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pfdi-other-affinity-rr40-full-dma-1/result.json) | 수정 kernel, PFDI OTHER0 + 위 배치 + suite RR40, 계측 OFF | 1/4 | FAIL 20480 / 20496 frames | 결합 정책도 실패; 원래 scheduling/affinity 복원 |

WAV 합격은 96000 frames 및 원본과 전체 파일 일치이며 표의 부분 frame은
실패 지점의 증거이다. 서로 다른 부팅과 계측 조건의 단일 실행이므로
2/4→3/4 차이를 정량적인 개선 효과로 주장하지 않는다. PFDI를 중지하거나
주기/coverage를 줄이는 변경은 하지 않았다.

### PFDI 함수 elapsed와 SMC 지연 구분

[pfdi-residency 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pfdi-smc-full-dma-1/dma/pfdi-residency.md)의
CPU0 함수 scope 444.970ms 중 443.965ms는 off-CPU였고 resident 상한은
1.005ms였다. 두 번째 366.170ms도 off-CPU 364.926ms / resident 상한
1.244ms이다. 특히 SMC 결과 저장 뒤 `complete()`가 RT99 app을 깨우면서
긴 tail이 발생했다. 따라서 이 두 값을 EL3/SCMI 응답 지연으로 해석하면
안 된다. CPU3의 188.652ms는 off-CPU 137.415ms / resident 상한
51.237ms이며, 이것 역시 host stall·IRQ 등을 포함할 수 있다.

후속 probe는 정확한 `pfdi_misc.ko`의 SMCCC call 직전/직후(+96/+100),
completion 전후(+128/+132)를 사용한다. 근거와 module SHA256은
[probe evidence](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pfdi-callsite-probes-evidence.json)에
있다. Image hash만으로 외부 module을 식별할 수 없어 guest module SHA도
검증했다. 순수 EL3 시간은 이 bracket만으로 확정할 수 없다.

### 모든 scheduler 전환을 수집한 첫 XRUN

[SMC/scheduler 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/smc-allsched-full-dma-1/dma/scheduler-smc-analysis.md)에서
첫 capture XRUN은 `hw_ptr=27648`, `appl_ptr=11264`, buffer=16384이며
wrap probe는 0회다. START부터 XRUN까지 770.657ms 중 runnable 대기는
472.647ms였다. 동일 CPU의 연속 sched-switch로 귀속 가능한 454.816ms는
PFDI RT app 170.445ms, CFS PFDI workers 131.355ms, ktimers 96.809ms,
ksoftirqd 52.895ms 등이 차지했다. Migration에 걸친 17.831ms는 별도이다.
trace 손실은 없었다. 이 결과는 PFDI app의 우선순위만으로 문제를 설명하지
못하며, IRQ/timer/CFS worker를 포함한 서비스 여유를 조사해야 함을 보여 준다.

실제 SMC bracket의 최대 elapsed 52.111ms는 off-CPU 26.284ms를 제외하면
resident 상한 25.827ms이다. 전체 표본의 최대 resident 상한은 27.121ms다.
이는 host stall/IRQ 시간을 포함하므로 순수 firmware 실행 시간으로 단정할
수 없다. DMA/DMI 결함이나 수백 ms의 단일 SMC blocking이라는 가설을
확정하지 않는다.

## 검증 도구 계약

- `--repeat N`은 같은 guest 부팅에서 suite 전체를 반복하고 iteration별
  PCM/IRQ/전체 WAV를 독립 판정한다. `--fail-fast`로 누락된 반복은 PASS가
  되지 않는다. Cold boot 반복은 verifier를 별도 output으로 다시 실행한다.
- `--kernel Image`는 full의 private unsigned UKI 양 slot에서 `.linux`만
  교체하고 나머지 section 및 원본 WIC가 보존됐는지 확인한다. PIO의 별도
  `.dtb` 변경은 kernel 교체 전에 수행한다. 현재 deploy
  Image는 PIO 수정본이지만 **BSP WIC의 내장 kernel은 아직 이전 버전**이다.
  이번 수정 kernel 실험은 모두 해당 옵션을 명시했다.
- `--experiment-script`는 guest setup/cleanup을 제공하는 진단 전용 경로다.
  setup·suite·cleanup의 최초 실패를 보존하며 custom cleanup은 한 번만
  실행한다. 우선순위나 affinity를 바꾸면 기본 설정 qualification으로
  승격하지 않는다.
- WAV는 요청한 DMA/PIO mode marker, 명령 exit status, frame/format,
  원본 PCM 및 **전체 WAV byte**가 모두 일치해야 한다. XRUN 메시지가 있으면
  명령이 exit 0이어도 FAIL이다. Recorder RUNNING 확인 후 playback을 시작한다.
- 실제 실행 중인 QBox `/proc/<pid>/maps`의 inode/device를 확인하여 로드된
  libqemu 및 module을 hash로 연결한다. 진단 archive는 base64 decoding 및
  tar member/size 검증을 통과해야 COLLECTED이다.

## 빌드 및 모델 검증

- `qbox-apollo-qvp-native`, `i2s-loopback` populate_sysroot 성공. QBox 빌드의
  관련 check 64 + 61 = 125 PASS.
- `virtual/kernel -c deploy` 성공(972 tasks); Linux PIO patch checkpatch
  0 errors / 0 warnings.
- `qemu-apollo-native -c populate_sysroot` 성공(485 tasks).
- 새 standalone QEMU에서 [계측 OFF](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/models-telemetry-off-2/result.json)와
  [계측 ON](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/models-telemetry-on/result.json)
  register/IRQ/FIFO/DMA 검증 각각 28/28 PASS. 이 결과는 full guest audio
  안정성이나 physical timing parity를 뜻하지 않는다.
- Root 검증 도구 [focused tests](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/focused-pytest-final-3.log) 193/193 PASS. 정상 종료뿐 아니라 trace
  전송 손상, UKI 보존, 실패 cleanup, 누락/중복/mode 불일치와 반복 실패를 검사한다.

첫 standalone 실행 `models-telemetry-off`는 host libslirp ABI가 맞지 않아
부팅 전에 실패했다. Recipe native sysroot의 `LD_LIBRARY_PATH`로 실행한
`models-telemetry-off-2`가 유효한 결과이며 초기 실패를 지우지 않았다.


## 수정 kernel의 기본 설정 반복 결과

[Full warm3](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pio-lock-full-warm3/result.json)는
진단·priority·affinity 변경 없이 수정 Image로 DMA/PIO 각각 별도 full boot,
같은 부팅 안에서 전체 suite를 3회 수행했다. 각 회차 메모리 검사는 두
controller의 memcpy/memset 각각 5회(합계 20회)이다.

| Profile/mode | Memory | PCM | 48kHz WAV 전체 일치 | 회차별 결과 |
|---|---|---|---|---|
| Full DMA | 60/60 PASS | 0/12 | 0/6 | FAIL / FAIL / FAIL |
| Full PIO | 60/60 PASS | 11/12 | 6/6 | PASS / PASS / FAIL |
| AP-only DMA | 60/60 PASS | 11/12 | 5/6 | PASS / PASS / FAIL |
| AP-only PIO | 60/60 PASS | 12/12 | 6/6 | PASS / PASS / PASS |

[AP-only warm3](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/pio-lock-ap-warm3/result.json)도 같은 수정 kernel과 기본 설정이다. AP-only DMA의 세 번째 회차에서 동시 PCM 한 방향과 정방향 WAV capture가 실패했다. Full PIO의 세 번째 동시 전송 한 방향에서 playback EPIPE가 남았다. 모든 성공
WAV는 96000 frames이며 원본 전체 파일 SHA256은
`b682b891ba07d1c7e594992780a7b2268d0b23d67ad3e0df0d7086af238cc7d8`이다.
PIO START stall이 이 실행에서 재현되지 않은 것과 전체 audio 안정성 합격은
구분한다. 두 mode 모두 full BSP selftest 결과도 개별 console에 보관했다.

## QSP Full/AP 대조와 첫 playback XRUN

[Full QSP2](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/qsp-full-dma-2/result.json)와
[AP QSP1](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/qsp-ap-dma-1/result.json)은
같은 수정 Image에 native/guest 진단과 host QSP를 켠 DMA PCM 실험이다.
두 실행 모두 **FAIL**이며 PCM 성공 marker는 0개다. Memory/WAV는 이 실행의
검사 대상이 아니었다. 첫 정방향에서 `playback write: Broken pipe`,
`received=0`, `written=16384`가 발생했다. 이 대조만으로 full 또는 PFDI에만
발생하는 결함으로 분류할 수 없다. 계측 부하가 없는 warm3 결과와도 구분한다.

| 첫 PCM 관측 | Full QSP2 | AP QSP1 |
|---|---:|---:|
| capture START → 첫 playback XRUN | 498.306ms | 453.921ms |
| XRUN hw_ptr / appl_ptr / buffer | 16384 / 16384 / 16384 | 16384 / 16384 / 16384 |
| inferred-wrap probe | 0회 | 0회 |
| 완료된 ALSA xfer | preload 16384 frames 1회 | preload 16384 frames 1회 |
| 첫 native stop의 TX / RX frames | 16384 / 16384 | 16384 / 16384 |
| 첫 native stop의 TX / RX FIFO | 0 / 0 | 0 / 0 |
| application runnable off-CPU | 460.518ms | 414.098ms |
| 마지막 연속 runnable 대기 | 428.169ms | 394.693ms |

[비교 원본](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/qsp-full-dma-2/dma/ap-full-first-xrun-comparison.json)에
trace line과 native stop counter를 보존했다. Full native TX/RX 근거는
`qbox-platform.log:79,81`, AP는 `qbox.log:52,54`다. TX frame counter는
수락된 nonempty FIFO를 pop한 횟수이며 timer tick 수가 아니다.
**정확한 XRUN probe instruction에서 native counter를 동시에 읽은 것은 아니다.**
첫 PCM stop에서 실제 16384-frame 전달량과 빈 FIFO를 확인한 것이다.
이 일치와 wrap 0회는 initial-buffer 소모에 따른 underrun을 뒷받침하며,
이번 실패를 시간 기반 가짜 wrap으로 설명할 근거는 없다.

### application 대기와 실제 IRQ thread

[Full 첫 XRUN 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/qsp-full-dma-2/dma/first-xrun-analysis.md)의
guest trace는 10480 events이며 CPU0–3의 overrun/dropped는 모두 0이다.
초기 preload는 2.434ms에 16384 frames를 반환했고 sched-out은 없었다.
그 뒤 첫 XRUN까지 추가 read/write xfer entry가 없다. Playback post-start
복귀 후 245us 만에 app이 R+ 상태로 선점됐고, 428.169ms 동안 다시
sched-in되지 못했다. 따라서 이 구간은 application sleep이나 긴 ALSA
xfer 내부 blocking으로 분류하지 않는다.

Full START→XRUN 구간에서 app의 sched-resident 상한은 37.788ms,
runnable 대기는 460.518ms, sleep은 0이다. CPU0의 해당 scheduler 연쇄는
끊기지 않았으며, 대기 중 current task가 모두 필터에 포함된 IRQ thread여서
그들의 전환을 빠짐없이 다음과 같이 귀속할 수 있다.

| IRQ40 thread | internal priority | app 대기 중 current(ms) | d350_irq 결과 | handler 총 / 최대(ms) |
|---|---:|---:|---|---:|
| ch0 / PID119 | 49 | 84.257 | HANDLED 15회 | 6.119 / 0.980 |
| ch1 / PID120 | 49 | 4.330 | NONE 15회 | 1.572 / 0.708 |
| ch2 / PID122 | 49 | 3.298 | NONE 15회 | 1.259 / 0.408 |
| ch3 / PID123 | 49 | 368.633 | HANDLED 15회 | 99.210 / 27.053 |

Guest current 시간은 host CPU가 실제로 계산한 시간이 아니다. Host BQL
획득 대기, vCPU 정지 및 IRQ 처리도 포함될 수 있다. 특히 ch3의 368.633ms
전체를 d350_irq 내부 99.210ms나 DMA register write만으로 설명하지 않는다.
IRQ wake→handler entry는 60개 표본에서 중앙값 2.0615ms, 최대 30.182ms다.
가장 가까운 이전 handled IRQ-end→같은 PID의 period entry 간격은 중앙값
29.336ms, 최대 30.983ms였다. Callback coalescing이 가능하므로 이를 DMA
DONE과의 일대일 대응으로 보장하지 않는다. Playback period callback의
최장 elapsed 32.846ms 중 31.284ms는 off-CPU였다.

DMA350은 channel resource별 `request_irq(..., IRQF_SHARED)`를 사용한다.
PREEMPT_RT는 primary를 무조건 IRQ_WAKE_THREAD를 반환하는 기본 handler로
바꿔 inactive channel도 깨운다. 이번에는 전체 8 channel 중 할당된 4개
action이 IRQ40을 공유했다. Inactive ch1/ch2 thread의 관측 비용은 합계
7.628ms, app 대기의 1.656%다. [status-only primary filter 후보](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/shared-dma-irq-filter-candidate.md)는
불필요한 wake를 줄일 수 있지만 이 수치만으로 전체 starvation 해결을
보장하지 않는다. 명시적 threaded IRQ로 바꾸면 forced-thread wrapper의
BH 처리와 period tasklet 실행 문맥도 달라지므로 별도 검증이 필요하다.

### QSP가 측정한 범위와 native IRQ cache의 경계

[QSP callsite 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/qsp-callsite-analysis.md)의
reset→off 창은 Full 4.037318s, AP 2.976683s다. 시작 marker는 ALSA START
이전의 IRQ/card 출력도 포함하므로 전체 창을 정상 PCM 재생 시간으로
해석하지 않는다. 마지막 두 snapshot 사이의 값은 다음과 같다.

| lock acquisition callsite | Full 0.413611s 구간의 elapsed 합(s) | AP 0.411436s 구간의 elapsed 합(s) |
|---|---:|---:|
| CPU interrupt 확인 `cpu-exec.c:804` | 0.52334 | 0.28011 |
| ARM_CP_IO 64-bit read `op_helper.c:1064` | 0.35389 | 0.55529 |
| 외부 I/O wrapper `iothread.c:27` | 0.20032 | 0.06917 |

QSP는 **여러 host thread의 mutex 획득 호출 elapsed를 합산**한다.
Host scheduling 지연도 포함되며 mutex hold time, 단일 CPU 정지 시간,
각 획득의 futex blocking 시간을 측정하는 것은 아니다. 겹친 대기 때문에
합계가 wall interval보다 클 수 있다. Snapshot은 reset 이후 누적값이므로
서로 더하지 않고 차이를 사용한다. ARM_CP_IO read를 counter read 하나로,
CPU interrupt 확인 횟수를 실제 IRQ 전달 횟수로 환산하지 않는다.
이 결과는 후반의 BQL 획득 경쟁을 뒷받침하지만 lock 보유자와 원인 방향까지
확정하지 못한다.

Native model의 같은 level `qemu_set_irq()` 호출이 매번 SystemC event를
만든다는 설명도 맞지 않는다. 기존 [GpioProxy::event()](../../hsoc-stack/tools/qbox/qemu-components/common/include/libqemu-cxx/libqemu-cxx.h)는
raw level/boolean level 변화를 확인한 뒤 callback을 호출하여 **SystemC
notification 전에 같은 level을 이미 걸러 낸다**. 따라서
[P3 native IRQ cache 후보](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-irq-cache-candidate/README.md)는
그보다 앞의 model/proxy 호출 비용을 줄이는 후보이다. 이미 필터된 downstream
notification을 제거하는 효과나 XRUN 해결을 주장할 수 없다. 후보의 counter
감소, 모델 기능 검사, 실제 PCM/WAV 및 반복 안정성은 각각 별도 판정한다.

### RT throttling 및 probe 검증 경계

[RT bandwidth 분석](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/smc-allsched-full-dma-1/dma/rt-bandwidth-analysis.md)은
원본 Image에 대응하는 보존 vmlinux와 수정 vmlinux 모두를 확인했다.
`update_curr_rt()`에는 `update_curr_common()` 호출만 있고 RT bandwidth
계상/제한 경로가 없다. 현재 `.config`는 `CONFIG_RT_GROUP_SCHED=n`이며
해당 소스의 `rt_rq_throttled()`는 false를 반환한다.
`sched_rt_runtime_us=950000`이 표시되거나 긴 runnable 대기가 있다는 사실만으로
이 guest의 RT bandwidth throttling을 원인으로 삼을 수 없다. 이 배제는
guest의 해당 기전에 한정하며 host scheduler/cgroup 제한은 별도 미계측이다.

수정 kernel용 ALSA offset/분기/레지스터는 새 Image/vmlinux에서 다시 검증했다.
그러나 QSP 두 실행의 12개 probe 중 `dma_rearm_begin/end` 2개는
**NOT_COLLECTED**였다. GDB의 원래 함수명 `d350_program_cmd`와 달리 실제
ELF/kallsyms 이름은 `d350_program_cmd.isra.0`이기 때문이다.
[v2 정의](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/audio-kprobes-9a75d661-v2.events)와
[v2 근거](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/audio-kprobes-9a75d661-v2-evidence.json)는
이 이름을 반영했다. 실제 최적화 ABI는 `x0=command descriptor`,
`x1=MMIO base`이며 x0을 channel pointer로 해석하지 않는다. v2의 guest 등록과
재시작 duration은 이 QSP 실행으로 검증되지 않았고, 아래 P3 trace에서 후속 검증했다. 첫 XRUN의 traceoff로
마지막 period return이 없는 것과 등록 실패도 구분한다.

## P3 IRQ 출력 cache 구현 및 검증

DMA350 channel별/combined IRQ와 I2S regular IRQ의 마지막 출력 level을
cache하여 같은 값의 `qemu_set_irq()` 호출을 생략했다. 최초/reset에서는
cache를 -1로 만들어 low 출력을 강제로 전달한다. Callback 재진입에 대비해
cache를 실제 출력 전에 갱신한다. DMA REQ/ACK, FIFO, timer, frame pacing은
변경하지 않았다. [후보 patch와 전후 snapshot](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-irq-cache-candidate/README.md)을
남겨 계측 코드와 이 변경을 따로 되돌릴 수 있다.

[빌드](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/build-p3-irq-cache.log)는
915 tasks 성공이며 QBox 관련 check 64+61개가 통과했다.
[모델 OFF](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-models-off/result.json)와
[ON](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-models-on/result.json)은
각각 44/44 PASS다. 기존 28개에 I2S IRQ assert/disable, 두 장치의 reset
후 clear 및 재assert, DMA combined mask에 의한 deassert 16개를 추가했다.

첫 [full DMA 기본 설정 실행](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-full-dma-1/result.json)은
memory 20/20 PASS, PCM 0/4, WAV 0/2로 **FAIL**이다. WAV는 양방향 모두
XRUN으로 recorder가 첫 data write 전에 종료하여 0-frame WAV만 회수했다.
단일 실행 및 host scheduling 변동을 고려하면 변경 전보다 좋아졌거나
나빠졌다는 통계적 결론은 내리지 않는다. 이 변경은 아직 full audio 해법이 아니다.

[첫 PIO warm3 부팅](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-full-pio-warm3/early-boot-failure.json)은
RSE BL2 `Read back AP state failed`에서 종료했다. AP Linux와 audio suite는
실행되지 않았으므로 **BOOT_FAIL / audio NOT_RUN**이다. Runner가 자체
종료했으며 외부 signal은 보내지 않았다. 이 기록도 성공한 재시도와 함께 보존한다.

### P3 계측 및 v2 probe 실제 검증

[P3 trace](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-trace-full-dma-1/result.json)는
기본 scheduling/affinity에 계측을 켠 실행이며 PCM 1/4로 FAIL이다.
[IRQ cache counters](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-trace-full-dma-1/irq-cache-analysis.json)는
297행이 모두 유효했고 cap/회귀/불변식 오류가 없었다. 관측 DMA 모델 1개와
I2S 2개의 마지막 counter는 evaluation 14,938,814 = 실제 출력 1,129 +
생략 14,937,685였다. Native object `/qbox-arm-dma350[0]`의 숫자를 Linux
controller 주소/번호로 그대로 해석하지 않는다. 로그가 없는 다른 DMA를
0회로 계산하지도 않는다. 이 값은 호출 제거를 입증하며 speedup이나
SystemC notification 감소를 측정한 값은 아니다.

[Rearm probe 검증](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-trace-full-dma-1/dma/rearm-probe-validation.md)은
12/12 등록과 entry/return 69/69 완전짝(START 2, IRQ 안 67)을 확인했다.
Rearm 함수 elapsed 중앙값 0.112ms, 최대 24.928ms이다. IRQ 내부 67쌍에서
rearm-return→IRQ-return 구간 합 496.266ms가 rearm 함수 내부 합 114.806ms보다
컸다. 이 scope의 guest sched-out은 0이지만 host BQL/probe/IRQ 비용을
포함할 수 있어 순수 연산 시간으로 단정하지 않는다. 첫 capture XRUN은
hw_ptr 34816 / appl_ptr 18432 / buffer 16384, wrap probe 0회다.
첫 XRUN의 traceoff로 잘린 capture xfer/period return은 미완료로 유지했다.
Native DONE→다음 command enable 최대 2.521s는 오류 후 활동 및 시험 사이
공백을 포함할 수 있어 순수 IRQ 지연으로 사용하지 않는다.

### P3 후보의 계측 OFF 반복 회귀

| Profile/mode | Warm 반복 | Memory | PCM | WAV 전체 byte 일치 | 결과 |
|---|---:|---:|---:|---:|---|
| Full DMA | 1 | 20/20 | 0/4 | 0/2 | FAIL |
| Full PIO | 3 | 60/60 | 12/12 | 6/6 | PASS / PASS / PASS |
| AP-only DMA | 3 | 60/60 | 12/12 | 6/6 | PASS / PASS / PASS |
| AP-only PIO | 3 | 60/60 | 11/12 | 6/6 | PASS / FAIL / PASS |

[Full PIO 재시도](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-full-pio-warm3-2/result.json)와
[AP-only 반복](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/p3-ap-warm3/result.json)은
수정 kernel, IRQ cache 모델, 기본 scheduling/affinity, 계측 OFF 조건이다.
AP PIO 두 번째 회차의 동시 PCM에서 playback EPIPE가 남았다. 성공 WAV는
모두 96000 frames, 앞서 기록한 원본 SHA256과 전체 파일이 일치한다.
이전 후보에서도 간헐적 XRUN이 존재했으므로 부팅별 차이를 IRQ cache의
통계적 효과나 새로운 원인으로 단정하지 않는다. **Full DMA 해결 및 모든
profile의 반복 안정성은 아직 확보하지 못했다.**

## RR60 대조군: 오디오 PASS와 시스템 실패를 분리

[RR60 단일 실행](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/rr60-full-dma-1/result.json)은
suite wrapper를 OTHER0→RR60으로 바꿨다. 자식 PCM/WAV뿐 아니라 memory 검사와
보조 명령도 이 정책을 상속한다. IRQ RT50, PFDI app FIFO99, affinity,
검사 주기/범위, clock 및 버퍼는 유지했다. 원래 OTHER0 복원도 확인했다.

| 실행 | Audio 결과 | Audio 구간 이후 PFDI timeout / RCU stall 로그 | 전체 판단 |
|---|---|---:|---|
| Full DMA RR60 1회 | memory 20/20, PCM 4/4, WAV 2/2 | 5 / 1 | FAIL, 채택 안 함 |
| Full DMA RR60 warm3 | memory 60/60, PCM 12/12, WAV 6/6 | 2 / 2 | FAIL, 채택 안 함 |
| Full PIO RR60 warm3 | memory 60/60, PCM 12/12, WAV 6/6 | 0 / 3 | FAIL, 채택 안 함 |

[반복 실행 원본](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/rr60-full-warm3/result.json)의
당시 verifier는 PFDI/RCU 실패를 판정하지 않아 PASS를 기록했다. 이 원본을
고치지 않고 [단일 실행 health 검토](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/rr60-full-dma-1/guest-health-review.json)와
[반복 health 검토](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/rr60-full-warm3/guest-health-review.json)를
추가하여 전체 FAIL을 명시했다. 원본 result/console/parser SHA256도 연결한다.
표의 값은 로그 match 수이며 unique 사건 수를 보장하지 않는다.

이 대조는 작업의 실행 기회가 오디오 실패에 영향을 준다는 증거다. 하지만
오디오를 통과시키면서 PFDI/RCU가 실패하므로 full system 해법이 아니다.
PFDI app FIFO99는 실제 SMC 실행 worker의 정책이 아니다. 현재 모듈은
CPU별 전용 `kthread_create_worker_on_cpu()`를 만들며 driver의 RT 승격이
없어 해당 worker는 SCHED_NORMAL이다. IRQ RT50이 유일한 원인이라거나
RR60이 모든 timeout의 직접 원인이라는 결론도 이 비교만으로 확정하지 않는다.

[RR60 재현 script](patches/05-audio-experiment-tools.patch)는 **실패 대조군 재현용**으로
남긴다. 새 [guest health 판정](../../scripts/test/qbox_audio_health.py)은 suite
시작 후 PFDI timeout 또는 RCU stall이 있으면 audio sample 비교가 모두
맞아도 최종 FAIL로 처리하고 `audio_status`를 별도로 보존한다. 실패 로그가
없다는 표시는 `NO_FAILURE_OBSERVED`이며 PFDI deadline/liveness PASS는 아니다.
이전 AP-only console에는 suite 시작 DT marker가 없어 이 parser의 자동
재평가 범위는 NOT_RUN이다. 새 AP verifier는 실제 DT mode 확인과 marker를
추가했다. [새 경로의 AP PCM 실행](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/health-ap-pcm-1/result.json)은 DMA/PIO 각각 4/4 PASS,
health는 NO_FAILURE_OBSERVED였고 실제 DT marker를 확인했다. 이 실행은
memory/WAV를 다시 검사하지 않았다. 기존 AP audio 결과와 수동으로 확인한 초기 RCU stall 기록은 유지한다.

## DMA IRQ thread OTHER 대조군

[첫 부팅](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/irq-other-full-dma-1/early-boot-failure.json)은
RSE BL2의 `SCP is not ready`에서 끝나 audio/정책 setup은 NOT_RUN이다.
[두 번째 실행](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/irq-other-full-dma-2/result.json)은
INTID390의 기존 audio IRQ thread 4개만 FIFO50→OTHER0으로 바꾸었다.
PID starttime/comm, channel action set, 변경 전후 policy를 검증했고
시험 후 4개 모두 FIFO50으로 복원했다. Audio application과 PFDI의 정책,
affinity 및 hardware 조건은 유지했다.

메모리 20/20, PCM 4/4, 정방향 WAV 96000 frames와 전체 byte 일치는
PASS였으나 역방향은 59392 frames에서 capture overrun으로 FAIL이다.
PFDI timeout·RCU stall 로그는 관측되지 않았다. 이 단일 실행도 해법으로
채택하지 않으며, 관측된 실패 없음은 PFDI 모든 deadline 성공 증거가 아니다.

## DMA IRQ OTHER + audio nice −10 후보

[첫 실행](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/irq-other-nice10-full-dma-1/result.json)은
full BSP 22/22, DMA memory 20/20, PCM 4/4, WAV 2/2 전체 일치로 PASS였다.
PFDI timeout/RCU stall은 NO_FAILURE_OBSERVED이며, positive deadline/liveness
qualification을 뜻하지 않는다. Kernel은 앞의 PIO 수정 Image와 동일하다.

[별도 부팅의 warm3](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/irq-other-nice10-full-dma-warm3/result.json)도
3/3 PASS였다. Memory 60/60, PCM 12/12, WAV 6/6이며 모두 96000 frames와
원본 전체 WAV SHA256이 일치했다. 이 부팅도 BSP 22/22, PFDI/RCU 실패 로그
0건, IRQ/PATH/wrapper cleanup PASS였다. 첫 단일 실행과 이 반복 실행은
같은 snapshot의 script를 사용하며 root 재현 script SHA256도 일치한다:
`8b70484e302ede914073c5d47f758d7617e8f84df486c17678a9247ec23bf4d8`.


[재현 script](patches/05-audio-experiment-tools.patch)는 기존 audio DMA IRQ
4개만 OTHER0으로 두고 `i2s-loopback`, `aplay`, `arecord` 명령만 SCHED_OTHER
nice −10으로 실행한다. Suite/helper/PFDI 정책과 CPU affinity는 유지한다.
각 프로그램의 원본 경로/SHA256, 실행 직전 nice/policy/PID/starttime을
확인한다. `arecord`의 argv[0] 의미를 보존하기 위해 resolved target 대신
원래 invocation 경로를 exec한다. 종료 후 원래 PATH, IRQ FIFO50 및 임시
wrapper 제거를 확인했다. 프로세스 종료로 개별 nice 변경도 사라진다.

이는 **DMA 모드 전용 scheduling 진단**이다. PIO DT에는 audio DMA IRQ
4개가 할당되지 않을 수 있어 같은 script를 PIO에 적용하지 않는다. PIO는
앞의 기본 설정 warm3 결과로 구분한다. Freerunning, quantum, frame pacing,
period/buffer 및 모든 full domain은 변경하지 않았다. 기본 정책 full DMA
실패는 여전히 남아 있으며 조건부 반복 PASS로 기본 지원을 선언하지 않는다.

## 적용 및 보류 판단

| 계획 | 이번 적용/검증 | 결론 |
|---|---|---|
| P0 | native/bridge bounded counters, 첫 XRUN trace, kernel/module/runtime hash | 구현. OFF/ON 모델 검사 통과, full 첫 XRUN 원인 분류 가능 |
| P1 RAM DMI | DMA global root 및 AP CPU alias 관측 | 기존 direct path 확인. 추가 RAM alias 변경 보류 |
| P2 native MMIO | I2S0/1 MMIO alias 및 warm fallback 확인 | 기존 alias 사용. FIFO를 RAM DMI로 바꾸지 않음 |
| P3 DMA 비용 | regular IRQ 동일 level 출력 cache 구현; reset/재assert 포함 모델 44/44 OFF·ON PASS | 중복 native 호출 제거 후보. 첫 full DMA PCM/WAV FAIL로 전체 해결 효과 미확인 |
| P4 scheduling | PFDI OTHER, affinity, FIFO40/RR60, IRQ OTHER, IRQ OTHER + audio nice −10 | 마지막 CFS 후보 full DMA warm3 PASS. 명시적 진단 조건으로만 제공; RR60은 PFDI/RCU 실패로 제외 |
| P5 idle | trace 및 실행 전후 state usage | 첫 실패 동안 해당 CPU idle 없음, deep state 사용 0. idle-disable 해법 채택 안 함 |
| P6 userspace | recorder readiness, fatal XRUN, 정확한 반복 비교 | 검증 강화. PCM TX/RX poll 개선 및 buffer 확대는 아직 미적용 |
| P7 pointer/driver | inferred-wrap probe, 실제 RX frames 대조, PIO START 분석 | 가짜 DMA wrap 근거 없음. PIO stream lock 수정·빌드·회귀 수행 |

남은 DMA 조사에서는 v2 재시작 probe의 실제 등록을 확인하여 이미 수집한
wakeup→threaded IRQ→period 구간에서 ENABLE 재설정 비용을 더 나눈다.
현재 `irq_handler_entry/exit`는 hardirq wrapper이므로 threaded handler 전체
실행 시간으로 해석하지 않는다. 실제 원본/수정 kernel binary에는 RT bandwidth 제한 경로가 없음을
[확인했다](../../build/qbox-apollo-qvp/dma-i2s-implementation-20261001/smc-allsched-full-dma-1/dma/rt-bandwidth-analysis.md).
따라서 `sched_rt_runtime_us=950000`만으로 throttling을 원인으로 삼지 않는다.
Timer/softirq 실행 구간과 host BQL 대기를 함께 기록한 뒤 원인이 확인된 scheduling/lock 경로만 수정한다.

다음 host 조사 후보는 DMA의 1µs timer 재예약이 실행 중인 I/O thread에도
빈 `notify_event_cb` BH를 예약하는 경로다. 다만 실제 I2S FIFO/ACK BH와
이미 만료된 timer도 같은 iteration을 요구하므로, 현재 QSP만으로 해당
알림 제거 효과를 입증하지 못했다. 먼저 **빈 notify BH만 처리한 iteration**
횟수와 실제 I/O thread의 자기 알림을 분리해야 한다. `qemu_in_main_thread()`는
BQL을 가진 vCPU도 참이므로 OS thread 판별로 사용하면 안 된다. 이 경로의
BQL 해제, timer deadline 또는 BH 예약을 임의로 바꾸는 수정은 하지 않았다.


PCM checker는 RX를 매회 1024 frames만 읽고 TX에는 남은 전체를 nonblocking
write로 요청한다. 한 번의 write는 현재 avail만 소모하므로 전체 전송 완료까지
blocking하는 것은 아니다. 제한된 RX/TX 교대 및 ALSA poll은 후보지만,
`aplay`/`arecord`는 별도 process여서 이 비대칭이 WAV 실패 전체를 설명하지
못한다. PFDI 주기·검사 범위를 줄이거나 ring을 키운 결과로 최종 합격을
대체하지 않는다. 기본 설정이 실패하는 동안 cold/warm 10회 합격 gate는
충족되지 않은 상태로 남긴다.

## 재현 명령

공유 BitBake와 timing 시험은 병행하지 않는다. 기존 output을 덮어쓰지 않고
아래 경로의 마지막 숫자를 바꿔 실행한다. 명령은 workspace root 기준이다.

```bash
# 동일한 기본 full 설정에서 수정 kernel, DMA/PIO 각 3회 warm 시험
python3 scripts/test/verify_qbox_full_audio.py \
  --kernel build/tmp_baremetal/deploy/images/apollo-qvp/Image \
  --mode both --tests all --repeat 3 \
  --out-dir build/qbox-apollo-qvp/audio-full-repeat-1

# DMA scheduling 대조군: 기본 설정과 별도의 DIAGNOSTIC 결과
# util-linux의 target chrt를 사용한다(native host chrt가 아님).
python3 scripts/test/verify_qbox_full_audio.py \
  --kernel build/tmp_baremetal/deploy/images/apollo-qvp/Image \
  --mode dma --tests all --repeat 3 \
  --experiment-script scripts/test/qbox_audio_dma_cfs.sh \
  --chrt-binary build/tmp_baremetal/work/cortexa720-poky-linux/util-linux/2.40.4/image/usr/bin/chrt \
  --out-dir build/qbox-apollo-qvp/audio-full-dma-cfs-1

# AP-only 회귀
python3 scripts/test/verify_qbox_linux_audio.py \
  --kernel build/tmp_baremetal/deploy/images/apollo-qvp/Image \
  --mode both --tests all --repeat 3 \
  --out-dir build/qbox-apollo-qvp/audio-ap-repeat-1
```

`--diagnostics`만 추가하면 bounded native/guest trace를 수집한다. kprobe는
현재 kernel/module에 맞게 검증한 정의만 `--kprobes`로 지정한다. 증거 root의
`audio-kprobes.events`는 **이전 kernel hash 전용**이므로 수정 Image와 함께
사용하면 의도적으로 거부된다. 진단 활성화에 따른 실행 순서·부하 변화는
별도 결과로 취급한다.

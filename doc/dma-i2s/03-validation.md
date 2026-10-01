# 실험 순서와 합격 기준

이 문서의 명령은 향후 구현 검증을 위한 절차이다. 2026-10-01 계획 작성에서는 기존 artifact와 소스만 조사했으며 새로운 boot/runtime 시험은 수행하지 않았다.

## 1. Baseline 고정

| 보관 항목 | 확인 방법 / 목적 |
|---|---|
| Source | root/QBox/qbox-platform/QEMU/Linux/Yocto HEAD와 관련 dirty diff를 각각 기록 |
| Build | `build/conf/{local.conf,bblayers.conf,templateconf.cfg}`에서 effective machine/provider 확인; `apollo-qvp` deploy 및 사용한 `.qboxconf` 보관 |
| Runtime binary | `platforms-vp`, 실제 `/proc/<pid>/maps`의 libqemu/audio modules, 각 SHA256 |
| Platform | AP-only source Lua와 full provider-installed Lua, `hw-block/` 포함 hash 목록; source만 수정하고 installed copy로 실행하는 실수 방지 |
| Firmware/artifacts | kernel/initrd, full WIC와 UKI A/B `.linux/.initrd/.dtb/.cmdline` hash, 실제 guest `/proc/cmdline`과 live DT |
| Execution | 도메인별 CCI accel/tcg_mode/sync_policy/time_sync_strategy/icount/quantum의 effective 값과 모든 override |
| Full topology | AP 4 CPU, RSE/SCP/Zephyr/secure boot marker 및 domain 로그 유지 |
| Host | CPU topology, QBox thread ID/역할/affinity, scheduling policy, cgroup CPU 제한, 메모리 여유와 동시 작업 |
| Guest | IRQ 번호와 affinity, idle usage, audio negotiated hw/sw params, kernel config/trace event 제공 여부 |

AP `MULTI`, 현재 각 domain의 `multithread-freerunning`, `quantum_keeper`, 10ms quantum을 유지한다. 현재 icount/clock 설정을 그대로 기록하고 변경하지 않는다. 실행 중 추가 firmware domain을 멈추지 않는다. DMI ON은 기록하되 그 자체를 direct-access 성공 지표로 사용하지 않는다.

기존 artifact를 덮어쓰지 않는다. full harness는 private WIC 및 unsigned UKI DT section을 사용해 DMA/PIO를 분리한다. 원본 WIC/UKI hash와 나머지 section이 보존되는지 확인한다. shared BitBake가 실행 중일 때 입력을 바꾸지 않는다.

## 2. 기존 verifier로 재현

workspace root에서 실행한다. 아래 두 suite는 같은 host에서 **순서대로** 실행하여 비교한다. 각 verifier의 새 `--out-dir`는 사전에 존재하면 안 된다.

```bash
run_stamp=$(date +%Y%m%d-%H%M%S)
audio_evidence="build/qbox-apollo-qvp/dma-i2s-plan-${run_stamp}"

python3 scripts/test/verify_qbox_linux_audio.py \
    --mode both --tests all --timeout 900 \
    --out-dir "${audio_evidence}/ap-baseline"

python3 scripts/test/verify_qbox_full_audio.py \
    --mode both --tests all --timeout 1800 \
    --out-dir "${audio_evidence}/full-baseline"
```

[AP verifier][ap-verifier]는 `run_qbox_linux.sh --bsp`, [full verifier][full-verifier]는 `run_qbox_yocto.sh --bsp --headless ... -- --foreground-runtime`를 호출한다. full launcher의 boot/login PASS 자체는 audio PASS가 아니다. test server와 foreground runtime이 마지막 `QBOX_AUDIO_DONE=<rc>` 및 WAV 수집까지 살아 있어야 한다.

현재 full의 expected baseline은 FAIL이다. nonzero 종료를 무시해 PASS로 바꾸지 말고 UART/JSON을 보관한다. 재현되지 않는다면 우선 host 부하와 hash/effective config를 비교하고, 실패를 만들기 위해 임의로 설정을 바꾸지 않는다.

빠른 원인 분리 단계에는 `--mode dma`/`--mode pio` 또는 `--tests memory`/`--tests wav`를 사용할 수 있다. 이 결과는 부분 검증이며 최종에는 반드시 `--mode both --tests all`을 사용한다. 기존 suite의 WAV는 mode별 두 단독 방향이고, 동시 양방향은 PCM checker가 담당한다. WAV 동시 duplex를 추가하면 별도 확장 case로 명시한다.

## 3. P0 계측 계약

다음은 **추가 구현할 산출물/필드**이며 현재 verifier에 이미 있다는 뜻이 아니다.

| 산출물 | 최소 내용 |
|---|---|
| `run-manifest.json` | profile/mode/run ID, source/binary/DT hash, effective CCI, topology, host/guest scheduling, test params |
| `trace-summary.json` | 아래 각 metric의 count, bytes, median/p95/p99/max 및 수집 clock, 계측 drop 수 |
| `trace-events.*` | bounded 사건 기록; monotonic sequence, instance/master/channel/period ID, event type, 해당 context에서 읽은 clock |
| `first-xrun.json` | 첫 실패 방향, errno/state, ALSA hw_ptr/appl_ptr/avail/delay, DMA current command/residue, 직전 IRQ·idle·frame 상태 |
| `comparison.json` | baseline 대비 변경 변수, config 불변 검사, 실제 통과 건수, byte 비교, 계측 ON/OFF 차이 |

| 계측 범위 | 핵심 metric | 판별 목적 |
|---|---|---|
| DMI/AddressSpace | CPU별/global별 RAM alias interval, grant/deny/invalidate, native DMA RAM bytes와 fallback bytes | RAM DMI가 실제 어느 master에 적용됐는지 |
| Native MMIO | CPU→DMA/I2S, DMA→I2S MR alias 및 fallback count | same-instance MMIO bridge 비용 |
| QBox transport | recursive IO lock wait, BQL 재획득, `run_on_sysc` 왕복 시간 | host lock/SystemC 대기 분리 |
| I2S | scheduled deadline/actual callback, accepted frames, TX-empty/RX-full 체류, FIFO 수위 | clock 진행과 실제 sample 진행 구분 |
| DMA | request/ack 전이, beat, period DONE, IRQ line assert/deassert, CH_CMD 재활성화 | trigger stall, IRQ 서비스, software rearm |
| Guest IRQ | IRQ entry/exit, 실제 callback, handler의 CH_CMD write, pending/active 정보 | IRQ가 일부 도착하는 것과 deadline 충족 구분 |
| ALSA | hw_ptr/appl_ptr, avail/delay/state, residue, period event, XRUN | 실제 application 지연과 pointer 도약 구분 |
| Scheduling/idle | host 및 guest wakeup→run, vCPU progress, idle entry/exit/usage | full의 추가 load/idle/secure path 영향 |

guest에서는 제공되는 경우 `snd_pcm:hwptr`, `snd_pcm:xrun`, `snd_pcm:hw_ptr_error`, `irq:irq_handler_entry`, `irq:irq_handler_exit`, `sched:sched_switch`, `sched:sched_wakeup`, `power:cpu_idle`을 사용한다. 먼저 `available_events`와 kernel config를 확인한다. 빠진 event는 `NOT_COLLECTED`로 표시하고 필요한 최소 계측만 추가한다. trace buffer overflow 또는 sample drop이 있으면 해당 구간의 지연 상한은 확정하지 않는다.

서로 다른 instance의 QEMU clock끼리 같은 시간축이라고 가정하지 않는다. host/API clock과 SystemC 시각을 안전한 thread context에서 수집하고 cross-stamp/sequence로 연결한다. 모델 callback 기록을 위해 잘못된 thread에서 SystemC kernel API를 호출하지 않는다. 21.333ms/341.333ms는 **명목 audio period/ring 시간**이므로 host 시간 측정과 곧바로 대조해 deadline 위반으로 선언하지 않는다. 실제 frame counter와 ring 여유에서 소비 가능한 시간을 계산한다.

첫 XRUN 이후의 오류/timeout은 결과 보존용이다. 원인 분석에서는 **첫 실패 직전**의 pointer, frame, period ID를 우선한다. 성공한 case도 같은 metric으로 비교하여 정상적인 wrap을 오류로 오판하지 않는다.

## 4. 원인 분리 실험표

먼저 계측 OFF baseline 3회, 최소 계측 ON 비교를 수행한다. 같은 QBox process에서의 반복을 지원하려면 harness 확장이 필요하며, cold boot와 warm alias 상태의 case를 명시적으로 구분한다. 현재 기본 verifier는 mode별 새 boot이므로 이를 warm 재시험이라고 부르지 않는다.

| ID | 한 번에 바꿀 변수 | 유지할 것 | 결과에 따른 다음 단계 |
|---|---|---|---|
| E0 | AP-only ↔ full profile | 같은 binary/kernel/initrd/audio params, 기본 host 상태 | 차이가 재현되는지 확인; baseline 자체가 바뀌면 hash부터 조사 |
| E1 | 진단 계측 OFF ↔ ON | runtime 구성 전부 | 결과가 크게 달라지면 trace 경량화; 계측 교란 기록 |
| E2 | host thread affinity/CPU 여유 | full topology, guest affinity, clocks | runqueue/lock 지연과 실패가 함께 줄면 P4 |
| E3 | guest process 또는 IRQ affinity 하나 | host 배치, idle, buffer | handler/rearm/app service 지연으로 세분화 |
| E4 | idle-state 사용만 제한 | GIC security, 모든 firmware, freerunning | 효과가 있으면 P5; 기본 idle 복구 전 최종 PASS 불가 |
| E5 | 확인된 RAM DMI 문제의 수정 한 건 | MMIO alias/model/driver 그대로 | fallback 감소 및 정확성 확인 후 P1 채택/기각 |
| E6 | 확인된 same-instance MMIO alias 수정 | RAM DMI와 timer 동작 그대로 | bridge 감소, DMA/PIO 모두 검증 후 P2 |
| E7 | RAM 접근 또는 callback 최적화 한 건 | handshake/FIFO/48k frame period/quantum | tail latency 개선 여부, residue/IRQ 회귀 없으면 P3 |
| E8 | buffer 또는 period 또는 wait 방식 하나 | 다른 test parameter 전부 | 지연 민감도 확인; P6 결과는 baseline과 별도 |
| E9 | 증명된 residue/IRQ/driver 오류 수정 | test params 및 runtime 설정 | frame↔pointer 일치 확인 후 P7a |

선택 순서는 E0/E1 이후 E2~E4로 낮은 비용의 원인을 분리하고, 관측된 병목에 따라 E5~E9를 선택한다. 모든 대안을 반드시 구현하는 계획은 아니다. RAM/MMIO가 이미 direct이고 대기 시간이 작으면 DMI 변경을 중단한다. pointer 오류가 확인되면 성능 최적화보다 정확성 수정을 우선한다.

가설을 채택하려면 실패 직전의 시간적 상관관계뿐 아니라 한 변수의 A/B 반복, 원복 시 재현 여부도 보관한다. 효과 없는 실험은 `NO_EFFECT`, 증거 부족은 `INCONCLUSIVE`, 지원되지 않는 계측은 `NOT_COLLECTED`로 남긴다.

## 5. 최종 합격 기준

| Gate | 합격 조건 |
|---|---|
| 구성 | 기준 freerunning/time_sync/quantum/TCG/clock 설정 불변; AP 4 CPU와 모든 full firmware domain 유지 |
| Backend | 실제 로드된 DMA350/I2S 모두 native qemu-components; 같은 AP instance의 peer/handshake |
| DMA memory | DMA/PIO boot 각각 controller 2개 × memcpy/memset × 5회 = 20 tests; data 비교와 IRQ 증가 PASS |
| DMA PCM | 단독 0→1, 1→0 및 동시 두 방향 각각 65,536 frames sequence PASS: 4/4 |
| PIO PCM | 같은 4/4, INTID388/389 활성 traffic 확인 |
| WAV | DMA 2/2 + PIO 2/2: 96,000 frames, source와 params/PCM/전체 384,044bytes 동일, 재생/녹음 exit 0 |
| XRUN/안정성 | 예상치 못한 underrun/overrun/EPIPE 0, timeout 0, panic/hang 0, trace sample 손실 여부 별도 명시 |
| Full 회귀 | BSP selftests 각 boot 22/22, RSE/SCP/Zephyr 및 관련 PFDI/RPMsg 동작 회귀 없음 |
| AP-only 회귀 | audio 전체 PASS; 기존 `pfdi_misc` FAIL은 audio 결과와 분리하여 그대로 보고 |
| 반복성 | 먼저 수정 후보별 3회; 최종 후보는 cold boot suite 10회 및 명시적 warm stream 반복 10회에서 실패 0 |

반복 수는 이번 개선의 기능적 수용 기준이며 안정성의 통계적 보장이나 physical real-time qualification이 아니다. 실패가 한 번이라도 있으면 첫 실패의 증거를 남기고 원인을 조사한다. 평균 점수나 성공 case만 골라 전체 PASS로 바꾸지 않는다.

기존 result JSON의 PASS 조건 외에 raw aplay/arecord 로그에서 XRUN이 없는지도 확인한다. 단일 WAV 성공이나 DMA memory 성공으로 전체를 대신하지 않는다. 길이를 맞추기 위한 trim, silence 제거, 시작 offset 검색 후 비교는 진단에만 쓰고 최종 exact 비교에 적용하지 않는다.

## 6. 구현 단계의 리뷰와 결과 보관

각 변경은 소유 repository에서 작은 단위로 만들고, 관련 모델/transport focused test를 먼저 실행한 뒤 runtime gate를 수행한다. DMI 수정은 invalidation/권한/경계, MMIO 수정은 side effect/width/IRQ, DMA 수정은 handshake/residue/stop/reset 검증이 선행한다. build만 통과한 상태는 `BUILD_PASS / RUNTIME_PENDING`이다.

생성 로그와 trace는 `build/qbox-apollo-qvp/<새 run-id>/`에 보관한다. 최종 결과에는 선택한 대안, 채택/기각 근거, exact hash, 실행 명령, config diff, 전체 case 결과, 첫 실패 또는 무실패 반복 횟수를 기록한다. 기능/지원 상태가 바뀌면 [platform README][platform-readme], [QBox/FVP 현황][project-doc], [I2S 문서][i2s-doc]를 함께 갱신한다.

최종적으로 기본 full에서 해결되지 않고 affinity나 idle disable 또는 buffer 변경에 의존하면 그 조건과 한계를 명시한다. 이를 기본 full 구성의 무조건 PASS로 승격하지 않는다.

[ap-verifier]: ../../scripts/test/verify_qbox_linux_audio.py
[full-verifier]: ../../scripts/test/verify_qbox_full_audio.py
[platform-readme]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/README.md
[project-doc]: ../qbox-fvp-emulation-project.md
[i2s-doc]: ../dwc/dw-apb-i2s.md

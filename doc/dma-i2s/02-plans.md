# Freerunning을 유지하는 대안별 계획

모든 계획은 [고정 조건](README.md#변경하지-않을-조건)을 따른다. 아래 변경은 아직 구현하지 않았다. 여러 최적화를 한꺼번에 적용하지 않고, P0 결과에 따라 한 가지 원인 후보씩 확인한다. **DMI 활성화, 메모리 시험 PASS, 평균 처리량 개선만으로 full audio 해결을 선언하지 않는다.**

## 우선순위와 소유 저장소

| 계획 | 적용 조건 | 주된 소유 경계 | 비용/위험 |
|---|---|---|---|
| P0 통계 및 첫 XRUN 계측 | 모든 대안의 선행 단계 | QEMU, QBox, root test tooling | 중간; 계측 부하 관리 |
| P1 DMA/CPU RAM DMI coverage | RAM TLM fallback이 반복되거나 alias 범위가 잘못됨 | QBox core, 필요 시 platform memory wiring | 중간; 주소/권한/invalidation |
| P2 Native MMIO alias | 같은 instance MMIO가 계속 SystemC를 왕복 | QBox core / qbox-platform wrapper | 중간; register side effect/route 보존 |
| P3 DMA 작업 비용 최적화 | direct path인데 timer/BH/beat 처리 비용이 지배적 | QEMU native DMA/I2S | 중간~높음; handshake/residue 공정성 |
| P4 CPU/IRQ 서비스 여유 | host 또는 guest wakeup/scheduling 지연이 큼 | root runner; 필요 시 QBox lock 경로 | 진단 낮음, lock 수정 높음 |
| P5 CPU idle/secure IRQ wakeup | idle 진입과 첫 실패의 시간적 상관관계 | Linux/firmware/QBox 중 확인된 소유자 | 진단 낮음, 실제 수정 범위 미정 |
| P6 ALSA userspace 서비스 | hw 진행은 정상이나 appl_ptr 갱신이 늦음 | Yocto i2s-loopback recipe, root tests | 낮음~중간; 시험 조건 완화 위험 |
| P7 Residue/driver 또는 command-link | pointer/period 계약 오류가 입증됨 | Linux DMA driver + QEMU | 오류 수정 중간, command-link 신규 구현 높음 |

`arm-zena-css/` reference는 수정하지 않는다. 일반 transport 수정은 `hsoc-stack/tools/qbox/`, Apollo 구성/wrapper는 `hsoc-stack/tools/qbox-platform/`, native 모델은 `hsoc-stack/tools/qemu/`가 소유한다. Linux 또는 Yocto 수정이 필요하면 각각의 owning repository에서 다룬다. 빌드가 필요한 단계에서는 provider와 deploy hash를 확인하고 공유 BitBake 실행을 직렬화한다.

## P0. 첫 XRUN까지의 시간과 경로를 기록

**목표:** RAM/CPU/MMIO 비용, interrupt service 지연, 실제 ring 고갈, pointer accounting 중 어디에서 최초 차이가 생기는지 판별한다.

1. AP-only/full 각각 DMA/PIO baseline을 동일 입력으로 반복한다. host 부하와 topology, 각 domain의 effective CCI 설정, DTB/UKI/kernel/module hash를 manifest에 보관한다.
2. QEMU의 I2S callback 예정/실행 시각, frame counter, TX-empty/RX-full 체류 시간, FIFO high-water, DMA channel별 beat/period/IRQ/rearm counter를 추가한다.
3. QBox CPU별 root와 global root를 나누어 DMI grant/alias 범위, RAM/MMIO fallback count/bytes, invalidation, recursive IO lock/BQL wait 및 `run_on_sysc` 지연을 수집한다.
4. guest IRQ handler 진입/종료, 실제 cyclic callback, CH_CMD 재활성화, ALSA hw_ptr/appl_ptr, wakeup→run, idle entry/exit를 첫 XRUN 전후와 연결한다. 동기 IRQ인지 threaded IRQ인지 실제 kernel 실행을 확인한다.
5. host monotonic, AP `QEMU_CLOCK_VIRTUAL`, SystemC timestamp를 각 유효한 thread context에서 샘플링하고 sequence/period ID로 연결한다. 서로 다른 clock의 절대값을 그대로 빼지 않는다.

기본값은 계측 OFF이며 case별 고정 크기 ring buffer와 요약 histogram을 사용한다. sample/beat마다 `printf`, UART dump, global DEBUG를 켜지 않는다. thread-safe counter 비용도 측정하고 계측 ON/OFF 실행을 비교한다. DMI fast path는 TLM callback을 호출하지 않으므로 **TLM 로그가 없다는 이유로 hit=100%로 계산하지 않는다**. 실제 AddressSpace mapping과 native 전송 counter를 함께 대조한다.

완료 산출물은 `trace-summary.json`, bounded trace, `first-xrun.json`, 실행 manifest와 비교표이다. 구체적 필드와 판별 순서는 [검증 계획](03-validation.md)에 정의한다. 이 단계만으로 full PASS가 되더라도 계측에 의한 실행 순서 변화인지 확인한다.

## P1. RAM DMI와 DMA global address space의 coverage 개선

**시작 조건:** warm 상태에서 DMA RAM 접근이 여전히 TLM fallback을 반복하거나 CPU/global root 중 일부에 RAM alias가 없다는 P0 증거가 있다.

대상은 [QBox initiator][initiator]의 `check_dmi_hint_locked()`, `init_global()`, [global peripheral initiator][global], [gs_memory][memory] 및 [router][router]이다.

1. DMA source/destination address, alias interval, access 권한 및 requester context를 대조한다. `m_requester_id_from_qemu`처럼 hint 적용을 제한하는 조건이 실제 활성화됐는지 조사하고, 보호 목적을 유지한다.
2. 최초 regular access 후 global alias가 설치되는지 확인한다. CPU warmup이나 `transport_dbg` 읽기로 DMA alias가 생겼다고 가정하지 않는다.
3. fallback이 확인된 순수 AP DRAM 구간에 대해 기존 hint 경로의 누락/범위 clipping부터 수정한다. 이후에도 필요할 때만 elaboration 이후의 명시적 global RAM alias 사전 등록을 비교한다. 사전 등록에 부작용 있는 MMIO 읽기를 사용하지 않는다.
4. router의 주소 변환, 우선순위 hole clipping, RO/RW, backing pointer lifetime, CPU/DMA에서 같은 storage를 보는 조건을 유지한다. 전체 64bit 주소 공간이나 secure/ATU window를 일괄 RAM으로 등록하지 않는다.
5. global invalidation callback의 no-op을 포함해 stale alias 제거/동시 접근 안전성을 먼저 검증한다. 변경 가능한 mapping은 검증 전 최적화 대상에서 제외한다.

검사는 경계 전후 접근, read-only, DMI 거절/fallback, 접근 중 reset/stop, alias 삭제 후 재접근, CPU-write→DMA-read 및 DMA-write→CPU-read를 포함한다. cache coherency의 물리적 fidelity를 추가로 주장하는 시험은 아니다.

**진행 기준:** 확인된 steady-state RAM fallback과 tail latency가 줄고 결과 byte가 보존된다. 기존 alias가 정상이고 RAM fallback이 거의 없다면 P1은 보류한다. RAM 경로를 더 빠르게 해도 userspace/IRQ가 따라오지 못하면 XRUN이 악화할 수 있으므로 P4/P7 계측을 함께 본다.

## P2. Same-instance native MMIO alias 경로 보장

**시작 조건:** DMA→I2S FIFO 또는 CPU→DMA/I2S register 접근이 warm 상태에서도 반복적으로 QBox/SystemC bridge를 통과한다.

[target.h][target]의 `QemuMrHintTlmExtension`과 [initiator.h][initiator]의 `check_qemu_mr_hint()`는 이미 같은 QEMU instance의 native MemoryRegion alias를 지원한다. 이 기존 경로를 우선 사용한다.

1. CPU memory root와 DMA global root에서 각각 I2S0/1과 DMA0/1 MR alias 설치 여부를 기록한다. 다른 root의 성공을 대신 사용하지 않는다.
2. hint가 사라지거나 주소 offset/instance 판정에 실패하는 원인을 수정한다. 기존 alias가 존재하면 중복 등록하지 않고 address overlap/우선순위를 확인한다.
3. lazy 설치만으로 부족할 때 wrapper의 realize 이후 실제 device MR를 정적 주소에 연결하는 명시적 alias를 검토한다. CPU root와 global root, target route, reset/unrealize 수명주기 모두 포함한다.
4. native MMIO callback, read/write width, FIFO pop/push, IRQ와 DMA request/ack side effect를 그대로 실행한다. SystemC router가 맡는 permission/instrumentation이 있다면 이를 우회하지 않도록 허용 구간을 제한한다.

**I2S FIFO/control을 RAM DMI 포인터로 바꾸지 않는다.** 같은 instance MR alias는 MMIO handler를 유지하는 방식이며 RAM pointer 접근과 다르다. cross-instance alias도 허용하지 않는다.

검사는 16/32bit 접근 계약, FIFO 좌우 순서, empty/full 상태, IRQ assert/deassert, 정수 four-phase DMA handshake, 동시 양방향, stop/start/reset, PIO 회귀를 포함한다. 완료 기준은 warm MMIO bridge crossing의 제거 또는 감소와 full/단독 회귀 통과이다. 이미 alias가 정상이라면 P2로 얻을 이득은 작다.

## P3. Native DMA의 bounded 작업 및 RAM 접근 최적화

**시작 조건:** DMI/MMIO mapping이 정상이며 host profile에서 beat별 AddressSpace 처리 또는 timer/BH 비용이 지배적이다.

대상은 [arm-dma350.c][dma]의 `dma350_schedule()` 및 channel step, [dw-apb-i2s.c][i2s]의 request/ack/BH 경로이다. 다음 실험은 분리한다.

- **P3a RAM 측 접근 비용:** native QEMU의 `address_space_map/unmap` 또는 이 checkout이 제공하는 memory cache API를 검토한다. 이미 존재하는 RAM mapping의 연속 구간만 재사용한다. short map, 권한, region 경계, dirty/writeback, invalidation 및 unmap 수명을 준수하고 실패 시 기존 AddressSpace API로 fallback한다. I2S peripheral register에는 매 beat MMIO를 유지한다. register width, signed increment, wrap, residual count, error가 발생하는 beat 위치도 보존한다.
- **P3b Callback 작업 분배:** 불필요한 재스케줄과 반복 lookup이 실제 hot spot인 경우에만 제거한다. 여러 channel의 준비된 작업을 bounded budget으로 처리하고 다른 AP device/BQL 사용자를 굶기지 않는다. DMA의 request→ack→request release→ack release 순서와 I2S frame deadline을 유지한다.

I2S single-transfer request는 한 번에 한 beat를 허용한다. request가 허용하지 않은 뒤따르는 sample을 미리 읽거나, FIFO를 한꺼번에 drain/fill하거나, 처리량을 높이려고 ack 단계를 생략하지 않는다. 따라서 audio 경로의 RAM batching 이득은 memory memcpy보다 작을 수 있다. 1µs DMA timer나 20,833ns I2S frame period를 늘려 시험을 통과시키는 방안도 사용하지 않는다.

단위 검증은 active DMA 중 stop/reset/error, wrap/경계, 다른 채널 동시 진행, 정확한 IRQ/residue, 빌드한 모델의 기존 QEMU/qbox-platform focused tests를 포함한다. 평균 성능뿐 아니라 최대 callback 점유 시간과 IRQ service tail latency가 악화하지 않아야 한다. 최종 판정은 full PCM/WAV 및 AP-only 회귀이다.

## P4. Host/guest scheduling 및 IRQ/재설정 service 보강

**시작 조건:** frame/DMA 진행은 정상인데 AP CPU, IRQ handler 또는 userspace가 늦게 실행되는 증거가 있다.

1. host thread별 CPU 사용, runqueue 대기, context switch, affinity, cgroup 제한과 BQL/recursive IO lock 시간을 기록한다. QBox 하나의 PID만 보고 모든 vCPU가 같은 방식으로 실행된다고 가정하지 않는다.
2. full의 AP vCPU, AP I/O, SystemC, RSE/SI thread에 필요한 host CPU 여유를 유지하며 affinity만 독립 비교한다. 다른 domain을 정지하거나 CPU 수를 줄이지 않는다. 기본은 일반 scheduling class이며 무조건적인 `SCHED_FIFO` 우선순위 상승은 피한다.
3. guest audio process와 INTID388/389/390의 실제 Linux IRQ affinity를 각각 별도 실험한다. 현재 관측은 CPU0의 IRQ count 증가까지이며 affinity mask/priority는 미수집 상태이다. CPU0 집중을 완화할 때 capture/playback/DMA IRQ 관계와 PIO 동시 case를 함께 확인한다.
4. SystemC rendezvous 전후 lock 대기가 지배적이면 QBox transport의 lock scope를 분석한다. BQL 해제/재획득, recursive IO guard, callback lifetime 및 QEMU thread-safety 계약을 보존한 작은 수정만 수행한다. arbitrary thread에서 MMIO를 실행하는 우회는 금지한다.

IRQ→handler→CH_CMD와 wakeup→userspace-run 분포가 개선되고 baseline 조건이 통과하면 효과가 있다. affinity가 있어야만 통과하는 경우 필요한 host core/배치 조건을 명시한 **조건부 지원**으로 기록하고 일반 설정에서도 반복 결과를 남긴다. 호스트 여유 부족과 장치 결함을 같은 원인으로 취급하지 않는다.

## P5. CPU idle 및 secure interrupt 복귀 경로 진단

AP-only가 제거한 `cpu-idle-states`를 full은 유지하므로 독립적인 차이이다. **실제 idle state usage/time 및 IRQ wakeup 지연이 먼저 필요하다.**

1. 동일 full boot에서 각 CPU의 idle state 사용량과 첫 XRUN 직전 idle entry/exit, timer/IRQ pending 상태를 수집한다.
2. 원본 이미지 대신 private test UKI/DT 또는 guest의 가역적인 idle-state disable을 사용해 해당 변수 하나만 비교한다. `cpuidle.off=1`을 사용한다면 진단용 bootargs 변경으로 기록한다. freerunning/time_sync/quantum/GIC security/full domain은 유지한다.
3. idle을 막을 때 재현성이 바뀌면 PSCI 호출/복귀, WFI wakeup, GIC pending/active/EOI, secure→non-secure 전달을 좁혀 조사한다. 모든 IRQ가 오지 않는 오류와 특정 시점 지연을 구분한다.
4. 근거에 따라 실제 소유자(Linux driver, TF-A/PSCI, QBox/QEMU wakeup)에 수정한다. 기본 full idle 설정을 복구한 후 다시 검증한다.

idle 미사용 또는 실험 효과가 없으면 P5를 종료한다. `cpuidle.off=1`에서만 통과하면 **DIAGNOSTIC_PASS**이며 기본 full 해결로 판정하지 않는다. full GIC security를 AP-only처럼 끄는 것은 최종 대안에서 제외한다.

## P6. Userspace wakeup 및 ALSA buffer 민감도

**시작 조건:** device frame/residue/IRQ accounting이 일치하고 ALSA application service 지연이 남는다.

1. 동일 16,384-frame ring에서 기존 EAGAIN+100µs sleep loop와 ALSA poll descriptor/`snd_pcm_wait()` 기반 대기를 비교한다. capture/playback service 분리도 독립 실험하되 start 순서와 preload, sample sequence를 유지한다.
2. ring 16,384→32,768 frames, period 1,024→2,048 등의 변화는 한 변수씩 진단한다. 실제 negotiated ALSA params를 저장하고 변경한 test 결과는 baseline과 분리한다. larger buffer로 통과하면 허용 지연 증가 효과인지 trace로 확인한다.
3. PCM checker만 바꾸어 통과해도 기존 `aplay -N`/`arecord -N` WAV 실패는 남은 요구사항이다. 두 경로 모두 검증한다.

최종 합격은 기존 period/ring 조건의 전체 suite로 한다. `snd_pcm_recover()`로 XRUN을 숨기거나 timeout 증가, silence 삽입, prefix/hash 부분 비교로 실패를 없애지 않는다. userspace 개선이 필요하면 recipe가 소유한 소스 및 root verifier를 구분하여 수정하고, rootfs 재빌드/UKI 내부 hash를 다시 기록한다.

## P7. Residue/period 오류 수정과 장기 command-link 대안

**P7a는 정확성 수정:** [Linux DMA driver][driver]의 `d350_get_residue()`, `d350_program_cmd()`, IRQ 처리와 [ALSA PCM][pcm]의 실제 hw_ptr 진행을 연결한다. CH_XSIZE/XSIZEHI, DONE clear, descriptor 교체, 다음 CH_CMD write 사이에 sample 수와 맞지 않는 위치 도약/중복 callback/잘못된 residue가 있으면 해당 race를 수정한다. 단순히 EPIPE가 사라지도록 residue를 고정하거나 callback을 누락시키지 않는다.

검사는 period 경계 직전/직후 pointer 읽기, ring wrap, 지연된 IRQ, simultaneous duplex, stop/restart, pause/resume와 short/partial transfer를 포함한다. frame counter와 pointer가 일치하고 변형한 지연 조건에서도 회귀가 없어야 한다. controller 일반 계약으로 고치며 platform-name 기반 driver 분기를 추가하지 않는다.

**P7b는 장기 기능 확장:** IRQ별 software rearm이 한계라는 증거가 남으면 native DMA350의 hardware command-link와 Linux cyclic 사용을 함께 검토할 수 있다. 현재 모델에는 없는 기능이므로 단순 DT flag로 활성화할 수 없다. 공식 DMA350 register/command 계약과 기존 reference model을 대조하고 capability discovery, descriptor fetch/ownership, loop 및 DONEPAUSE, IRQ 정책, reset/error/residue까지 설계한다.

P7b는 IRQ 재설정 의존성을 줄일 수 있지만 userspace service 부족을 해결하지 않으며 capture가 더 빨리 ring을 덮게 만들 수도 있다. 과거 `cyclic_done_pause` 설정을 복구하는 것만으로 해결된다고 가정하지 않는다. 작은 P1~P7a 대안의 결과를 보고 별도 기능 작업으로 결정한다.

## 공통 정확성 기준과 참고 문서

QEMU는 RAM과 MMIO, alias, AddressSpace를 구분하며, mapping 및 owner 수명주기를 지켜야 한다. device DMA 최적화는 CPU 가상주소 load/store helper로 우회하지 않고 device address-space 계약을 유지한다. [QEMU memory API](https://www.qemu.org/docs/master/devel/memory.html), [QEMU load/store API](https://www.qemu.org/docs/master/devel/loads-stores.html)를 설계 기준으로 사용하되 실제 사용 가능한 함수는 이 checkout에서 확인한다.

TLM DMI는 허용 범위/권한과 invalidation을 포함하는 계약이다. SystemC의 coroutine 기반 설명만으로 QBox의 host 다중 thread 접근이 안전하다고 가정하지 않는다. [TLM-2.0 LRM, DMI 절](https://www.accellera.org/images/downloads/standards/systemc/TLM_2_0_LRM.pdf)을 참고한다. ALSA의 underrun/overrun은 스트림 상태 오류이므로 복구 성공과 무손실 녹음을 구분한다. [ALSA PCM API](https://www.alsa-project.org/alsa-doc/alsa-lib/pcm.html)를 참고한다.

[initiator]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h
[global]: ../../hsoc-stack/tools/qbox/qemu-components/global_peripheral_initiator/include/global_peripheral_initiator.h
[memory]: ../../hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h
[router]: ../../hsoc-stack/tools/qbox/systemc-components/router/include/router.h
[target]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/target.h
[dma]: ../../hsoc-stack/tools/qemu/hw/dma/arm-dma350.c
[i2s]: ../../hsoc-stack/tools/qemu/hw/audio/dw-apb-i2s.c
[driver]: ../../hsoc-stack/components/primary_compute/linux/drivers/dma/arm-dma350.c
[pcm]: ../../hsoc-stack/components/primary_compute/linux/sound/core/pcm_lib.c

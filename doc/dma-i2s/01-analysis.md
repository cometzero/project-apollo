# 구성 차이와 실패 분석

## 1. 비교 기준과 증거

이번 분석은 2026-09-30에 보존한 두 실행의 JSON, UART 로그, WAV, DTB와 2026-10-01 checkout의 소스를 사용한다.

현재 native 모델은 기능 검증용이다. DMA의 command-link/security attribution/bus timing 및 native I2S pinmux gating은 구현 범위 밖이다. full firmware가 실행된다는 사실만으로 이 기능들의 지원이나 물리 timing parity를 주장하지 않는다.

- AP-only: [qbox-ap-only-native-retest-20260930/result.json][ap-result]
- Full: [qbox-full-native-audio-foreground-20260930/result.json][full-result]
- 같은 바이너리 여부: [full-system-comparison.json][comparison]
- 실제 로드된 full audio 라이브러리: [loaded-audio-libraries.txt][loaded]
- 입력 WIC/UKI section 검증: [disk-preparation.json][disk]
- 결과·원본 파일 hash와 조사 시점 HEAD: [evidence.json](evidence.json)

Git HEAD는 **조사 시점 소스 식별자**이다. 바이너리의 빌드 commit을 역으로 증명하지는 않는다. 두 실행의 바이너리 동등성은 기록된 SHA256으로 비교했다. 재실험할 때에는 실제 로드 경로와 hash를 다시 저장해야 한다.

| 시험 항목 | AP-only | Full | 해석 |
|---|---:|---:|---|
| DMA350 memory, DMA boot | 20/20 PASS | 20/20 PASS | 2 controller × memcpy/memset × 각 5회 |
| DMA350 memory, PIO boot | 20/20 PASS | 20/20 PASS | audio가 PIO여도 DMA controller는 별도 시험 |
| DMA PCM | 4/4 PASS | 0/4 FAIL | 단독 0→1, 1→0 및 동시 양방향 |
| PIO PCM | 4/4 PASS | 3/4 PASS | full 동시 0→1만 playback EPIPE |
| DMA WAV | 2/2 PASS | 0/2 FAIL | full capture timeout, PCM 내용도 불일치 |
| PIO WAV | 2/2 PASS | 2/2 PASS | 양방향 전체 파일 동일 |
| DMA PCM INTID 390 증가 | +218 | +100 | IRQ는 도착하지만 지연/누락 여부는 알 수 없음 |
| PIO PCM INTID 388 / 389 증가 | +24,618 / +40,883 | +37,842 / +24,604 | 서로 다른 완료량이므로 단순 수치 비교로 효율 판단 불가 |
| BSP selftests | `pfdi_misc` FAIL | 각 boot 22/22 PASS | AP-only audio PASS와 full-domain qualification은 별개 |

메모리 시험은 64KiB test buffer 안의 random transfer를 사용한다. 고정 64KiB memcpy 성능 시험이 아니며, 각 로그의 KB/s 차이를 원인 근거로 사용하지 않는다. IRQ 번호는 Linux virtual IRQ가 아닌 GIC **INTID**이다. SPI 인덱스는 INTID−32로, audio DMA1은 SPI358/INTID390, I2S0/1은 SPI356/357 및 INTID388/389이다.

Full DMA PCM의 오류는 [UART][full-dma-log] 616–622행, PIO 방향별 결과는 [PIO UART][full-pio-log] 616–622행에 있다. DMA WAV는 같은 DMA 로그 733, 5983행에서 양방향 모두 `playback=0 capture=124`이고 underrun/overrun도 기록된다. 124는 녹음의 60초 timeout 결과이다. 로그 9420–9421행의 `WAV_DONE=1`, `QBOX_AUDIO_DONE=1`은 실패 상태로 suite가 끝났음을 보여 준다. JSON의 `guest_completed:false`는 성공 마커가 없다는 뜻이며 **guest hang 판정이 아니다**.

원본 WAV는 48,000Hz, stereo, 16bit, 96,000 frames이며 전체 384,044bytes이다. SHA256은 `b682b891ba07d1c7e594992780a7b2268d0b23d67ad3e0df0d7086af238cc7d8`이다.

| Full 녹음 | 저장된 frames | PCM 최초 불일치 frame, 0부터 계산 | 판정 |
|---|---:|---:|---|
| DMA 0→1 | 74,596 | 0 | 길이 부족과 sample 불일치 |
| DMA 1→0 | 48,216 | 11,264 | 첫 11,264 frames 이후 불일치 |
| PIO 0→1 | 96,000 | 없음 | 전체 WAV byte 동일 |
| PIO 1→0 | 96,000 | 없음 | 전체 WAV byte 동일 |

WAV header/padding 차이만의 문제가 아니다. 반면 PCM sequence checker는 초기 zero frame을 제한적으로 건너뛴다. 따라서 PCM PASS만으로 WAV의 시작 sample까지 완전 동일하다고 주장하지 않는다.

이전 `qbox-full-native-audio-20260930` 실행은 launcher/HTTP server 수명 문제로 시험이 불완전했다. 위 `foreground` 실행을 최종 비교 기준으로 삼는다. SystemC-only 및 QEMU DMA + SystemC I2S 혼합 실행에서 관측된 timeout/재진입 panic도 이번 all-native full의 XRUN과 구분한다.

## 2. 동일한 부분과 실제 차이

| 항목 | AP-only Linux QBox | Full QBox | 근거/의미 |
|---|---|---|---|
| QBox/libqemu 및 두 audio module | 같은 SHA256 | 같은 SHA256 | [동등성 증거][comparison] |
| Linux Image/initrd | 같은 SHA256 | UKI 내부 section hash도 동일 | [AP 결과][ap-result], [UKI 증거][disk] |
| Audio DT | DMA/I2S 주소, IRQ, request 동일 | 동일 | 준비된 [AP DTB][ap-dtb], 추출한 [full DTB][full-dtb] |
| Audio wrapper | `common.use_qemu_audio()` | 같은 함수 | [common Lua][common] 24–55행 |
| I2S peer와 DMA1 handshake | AP QEMU instance 내부 연결 | 동일 | [I2S wrapper][wrapper] 77–114행; 정수 request/ack 보존 |
| AP CPU 수 | 4 | 4 | UART boot 결과 |
| AP execution | TCG MULTI, freerunning, quantum_keeper | 동일 | [AP 정의][ap-compute] 1–12, 287–296행; [full runner][full-runner] 162–182행 |
| SystemC quantum | 10ms | 10ms | [Linux Lua][linux-lua] 20행; [fabric][fabric] 5–10행 |
| Host RAM DMI | `true` | `true` | [AP launch][ap-launch] 41행; [full runtime][full-runtime] 827행 |
| Flash/ATU DMI | direct boot에는 해당 firmware 경로 불필요 | `--range-limited-flash-dmi` 사용 | [runtime 구성][runtime-src] 3143–3148행에서 host/ATU DMI 설정 |
| Boot/domains | direct Linux, 다른 도메인 mock | RSE, SCP, Zephyr, TF-A/U-Boot 및 secure boot 경로 | [profile 구성][full-lua] 43–55행 |
| GIC security | `DS=1`, `SCR_EL3.FIQ=0` | `DS=0`, `SCR_EL3.FIQ=1` | AP UART 77행, full UART 121행 |
| PSCI/CPU idle | SMC stub; `cpu-idle-states` 및 `cpu-map` 제거 | secure firmware 경로, idle DT 유지 | [Linux Lua][linux-lua] 70–79행; [DT 준비][prepare] 82–98행 |
| Bootargs | direct `rdinit=/init`, console | `cpuidle.governor=menu maxcpus=4 mem=4064M` 등 | AP UART 45행, full UART 89행 |
| Linux architected timer | 125MHz physical timer | 같은 표기 | AP UART 90행, full UART 134행; 실제 drift 측정은 아님 |

같은 kernel/initrd라고 해서 firmware, DT 전체, 메모리 배치와 IRQ/idle 경로까지 같지는 않다. 현재 DT에는 양쪽 모두 `cyclic_done_pause`가 없다. 이전 command-link/DONEPAUSE 정책의 성공 사례를 현재 드라이버와 native 모델에 그대로 적용할 수 없다.

## 3. DMA와 DMI 경로

Full의 global peripheral initiator는 [ap_compute.lua][ap-compute] 1145–1148행에서 `ap_router.target_socket`에 연결된다. DRAM도 1183–1187행, audio MMIO도 1209–1210행 및 [ros.lua][ros] 426–441행에서 AP router에 연결된다. AP-only는 [Linux Lua][linux-lua] 88–100행의 binding 치환으로 같은 local decode를 사용한다. **Full audio DMA가 매 beat마다 별도 ATU/system_router를 더 거친다는 설명은 현재 경로와 맞지 않는다.**

| 단계 | 현재 구현 | 조사할 지점 |
|---|---|---|
| Native DMA beat | [arm-dma350.c][dma-model] 274–296행의 `address_space_read/write`, `MEMTXATTRS_UNSPECIFIED` | RAM/MMIO 주소별 호출량과 지연 |
| Global QEMU memory miss | [initiator.h][initiator] 903–932행의 `init_global()` IO bridge | 어느 initiator root가 alias를 갖는가 |
| Regular TLM fallback | 같은 파일 660–692행: BQL release → `run_on_sysc(b_transport)` → BQL reacquire → hint 처리 | recursive IO lock/BQL 대기, SystemC rendezvous 지연 |
| RAM direct path | DMI hint로 해당 root에 RAM alias 설치 | 최초 miss 이후에도 fallback이 반복되는가 |
| Native MMIO direct path | [target.h][target] 159행의 `QemuMrHint`; initiator 635–658행에서 same-instance MR alias | DMA→I2S와 CPU→DMA/I2S 양쪽 alias 여부 |

CPU socket은 `socket.init(..., "memory")`로 별도 root를 사용한다([cpu.h][cpu] 995행, initiator 816–833행). DMA는 global address-space root를 사용하므로 **CPU DMI 성공은 DMA DMI 적중 증거가 아니다**. 정상 native DMA는 debug 접근이 아니다. `transport_dbg`를 이용한 사전 읽기는 regular 경로의 DMI/MR hint 설치를 대신하지 못한다.

Global initiator는 local time으로 SystemC timestamp를 반환하고 `set_local_time()`을 무시한다([global initiator][global] 28–29행). CPU initiator는 별도의 virtual-time/quantum 경로를 사용한다([cpu.h][cpu] 1276–1292행). 이 차이는 경로 설명이며 XRUN의 확정 원인은 아니다.

DMI 확대에는 수명주기 검증도 필요하다. `invalidate_direct_mem_ptr` 처리 말미는 async callback을 예약하지만(initiator 1092–1095행), global initiator의 `initiator_async_run()` 및 `initiator_tlb_flush_all_cpus()`는 현재 no-op이다(global 61–62행). 정적 DRAM에서 이번 실패를 유발했다는 증거는 없으나, 동적 alias/ATU/권한 변경으로 최적화를 확장하기 전에 해결해야 할 검증 항목이다.

## 4. Freerunning, frame 진행과 Linux cyclic 처리

I2S와 DMA timer는 모두 **같은 AP instance의 `QEMU_CLOCK_VIRTUAL`**을 사용한다. I2S는 `now + 20,833ns`, DMA는 `now + 1,000ns`로 재예약한다([I2S][i2s-model] 131–141, 619행; [DMA][dma-model] 51–55, 493행). 늦어진 tick을 한꺼번에 따라잡는 catch-up loop는 없다.

현재 quantum_keeper 구성에서 icount가 꺼지고 MCIPS time callback이 사용되지 않으면 QEMU virtual clock은 [TCG clock][tcg-clock] 203–234행 → [cpu timer][cpu-timer] 74–100행의 host monotonic 기반 VM clock이다. SystemC timestamp와 동일하지 않다. [freerunning keeper][freerun] 15–28행은 다른 CPU thread의 `sync()`에서 notification만 보내며 `need_sync()`는 false를 반환한다. CPU 실행, SystemC transport 및 timer callback에 공통 barrier가 있다고 가정하면 안 된다.

따라서 full의 추가 도메인/secure 경로가 CPU 또는 BQL service를 늦출 가능성은 있다. 다만 실제 callback 지연은 frame 진행을 느리게 할 수도 있으므로 **“full의 DMA/I2S 시간이 더 빨리 흐른다”는 결론도 미확인**이다. host, AP virtual, SystemC 세 시각과 실제 frame 진행량을 함께 측정해야 한다.

I2S `functional_pacing`은 상대 RX FIFO 16개가 찼을 때 TX frame을 유지하고 재시도한다([I2S][i2s-model] 515–543행). TX FIFO가 비면 timer를 중단한다. 이 장치에는 ALSA `appl_ptr` 또는 software ring의 빈 공간 정보가 없다. FIFO 보호가 userspace playback underrun/capture overrun을 방지하지는 않는다.

현재 [Linux DMA driver][dma-driver] 443–470행은 period별 software descriptor chain을 만들고, 809–821행은 DONE IRQ마다 cyclic callback을 예약하고 다음 command를 MMIO로 다시 설정한다. Native DMA 모델은 hardware command-link를 구현하지 않는다. `vchan_cyclic_callback()` 호출과 실제 ALSA period callback 실행 시점도 구분해서 측정해야 한다.

| 계약 | 값 / 의미 |
|---|---|
| PCM | 48kHz, S16_LE stereo, 65,536 frames/case |
| PCM period | 1,024 frames = 명목 21.333ms |
| PCM ring | 16,384 frames = 명목 341.333ms |
| WAV | 96,000 frames, capture period 1,024 / playback period 4,096, ring 16,384 |
| 이상적 sample payload | 한 방향 192,000B/s; playback RAM read + capture RAM write 합계 384,000B/s |
| Native DMA single-transfer 부하 | 2-byte sample beat 기준 한 loopback의 TX+RX 합계 192,000beat/s, 동시 양방향 384,000beat/s |

위 시간/처리량은 sample rate에서 계산한 명목값이다. 실제 host deadline이나 측정 throughput이 아니다. payload 대역폭보다 작은 beat마다의 호출·handshake·IRQ 비용이 중요할 수 있다.

[PCM checker][pcm-test] 70–111행은 playback preload, capture 먼저 start, nonblocking read/write와 EAGAIN 시 100µs sleep을 사용한다. [ALSA DMA pointer][pcm-dma] 251–270행은 residue로 위치를 계산하며, [pcm_lib.c][pcm-lib] 209–225행은 XRUN을 `-EPIPE`로 보고한다. 같은 파일 343–357행에는 늦어진 callback의 wrap 판단도 있다. 따라서 sample 진행, residue, callback, hw_ptr/appl_ptr를 대응시켜 실제 ring 부족과 pointer accounting 오류를 분리해야 한다.

## 5. 원인 후보와 판별 조건

| 우선 조사 | 현재 지지 근거 | 미확인 사항 / 반증 기준 |
|---|---|---|
| IRQ/period 재설정 및 userspace 서비스 지연 | DMA software cyclic, full EPIPE, PIO 동시 case도 실패 | IRQ→handler→CH_CMD 및 wakeup→run 지연 미측정. 정상 latency인데 pointer가 도약하면 driver/model 쪽으로 이동 |
| CPU idle/secure wakeup 차이 | AP-only는 idle DT 제거, full은 유지; GIC/PSCI 경로 차이 | 실제 idle usage/exit latency 없음. idle 미사용 또는 실패와 무상관이면 우선순위 낮춤 |
| RAM/MMIO bridge 비용과 DMI/alias coverage 차이 | global/CPU root가 다르고 fallback이 SystemC로 건너감 | 두 실행 모두 DMI ON. steady-state direct path와 낮은 lock wait가 확인되면 DMI 원인 가설 약화 |
| Native timer/BH/handshake 비용 | 많은 single-transfer callbacks; full 추가 실행 도메인 | profiling 없음. lateness/frame rate 측정 없이 timer 과속/CPU starvation으로 단정 불가 |
| Residue/IRQ accounting 또는 공유 상태 오류 | 같은 기능이 full의 다른 interleaving에서만 실패할 수 있음 | single/full DMA 메모리 PASS로 배제 불가. pointer와 실제 sample/frame counter 불일치가 필요 |

PIO 단독 및 WAV 통과는 MMIO 연결과 기본 sample 경로가 작동함을 보여 준다. PIO 동시 실패는 DMA 전용 최적화만으로 전체 해결을 보장할 수 없다는 근거이다. Full의 총 경과시간은 firmware boot와 녹음 timeout을 포함하므로 AP-only와 throughput을 비교하는 지표로 사용하지 않는다.

[ap-result]: ../../build/qbox-apollo-qvp/qbox-ap-only-native-retest-20260930/result.json
[full-result]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/result.json
[comparison]: ../../build/qbox-apollo-qvp/qbox-ap-only-native-retest-20260930/full-system-comparison.json
[loaded]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/dma/loaded-audio-libraries.txt
[disk]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/dma/disk-preparation.json
[ap-dtb]: ../../build/qbox-apollo-qvp/qbox-ap-only-native-retest-20260930/dma/linux-boot/linux.dtb
[full-dtb]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/dma/a.dtb
[full-dma-log]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/dma/qbox-primary-console.log
[full-pio-log]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/pio/qbox-primary-console.log
[common]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-common.lua
[wrapper]: ../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_dw_apb_i2s/include/qemu_dw_apb_i2s.h
[ap-compute]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
[full-runner]: ../../scripts/run/run_qbox_apollo_fvp_full.py
[linux-lua]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-linux.lua
[fabric]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua
[ap-launch]: ../../build/qbox-apollo-qvp/qbox-ap-only-native-retest-20260930/dma/launch.json
[full-runtime]: ../../build/qbox-apollo-qvp/qbox-full-native-audio-foreground-20260930/dma/rd-aspen-result.json
[runtime-src]: ../../scripts/run/qbox_apollo_runtime.py
[full-lua]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua
[prepare]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py
[ros]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua
[dma-model]: ../../hsoc-stack/tools/qemu/hw/dma/arm-dma350.c
[i2s-model]: ../../hsoc-stack/tools/qemu/hw/audio/dw-apb-i2s.c
[initiator]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h
[target]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/target.h
[cpu]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h
[global]: ../../hsoc-stack/tools/qbox/qemu-components/global_peripheral_initiator/include/global_peripheral_initiator.h
[tcg-clock]: ../../hsoc-stack/tools/qemu/accel/tcg/tcg-accel-ops.c
[cpu-timer]: ../../hsoc-stack/tools/qemu/system/cpu-timers.c
[freerun]: ../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h
[dma-driver]: ../../hsoc-stack/components/primary_compute/linux/drivers/dma/arm-dma350.c
[pcm-test]: ../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-test/i2s-loopback/files/i2s_loopback.c
[pcm-dma]: ../../hsoc-stack/components/primary_compute/linux/sound/core/pcm_dmaengine.c
[pcm-lib]: ../../hsoc-stack/components/primary_compute/linux/sound/core/pcm_lib.c

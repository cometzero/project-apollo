# DMA-350 hardware command-link cyclic 구현

## 상태와 목적

현재는 DMA controller 노드의 boolean `cyclic_done_pause` DT 속성으로
DONEPAUSE callback pacing을 선택한다. Apollo QVP의 두 controller에 선언했다.
`cyclic_done_pause` module parameter는 제거했다. 적용 범위는 command-link
지원 채널의 `DMA_PREP_INTERRUPT` cyclic 전송이며, 속성이 없는 controller와 일반
memcpy/memset/slave SG 전송은 기존 동작을 유지한다.
아래의 선택적 활성화와 autonomous 실패 기록은 기본 적용 전 이력이다.
이전 machine quirk 적용 후 Linux I2S 양방향 8/8 WAV와 SPI/UART/memory DMA 회귀가
통과했다. 자세한 입력/로그는
[QVP quirk 검증](../dwc/i2s-freerunning-validation.md)의 마지막 절을 참조한다.

2026-09-16 현재 **autonomous cyclic은 기본 freerunning에서 FAIL**이다.
선택적 DONEPAUSE와 명시적 wait/affinity를 적용한 hardware-linked cyclic은
실제 Linux 양방향 긴 WAV/반복/odd tail에서 조건부 PASS다. 수동 pause에서
발견한 별도 FIFO flush 문제는 DAI driver에서 수정했고 pause/resume 및
paused STOP도 양방향 PASS다. 아래는 초기 실패 이력이다.
BSP 빌드 및 DMA DT 부팅은
성공했지만 첫 양방향 WAV 검사는 캡처 0/EIO와 XRUN으로 실패했다. 추가 MMIO
진단은 host timeout이 발생했다. 후속 Linux kprobe에서는 command 설정과
START 반환을 확인했으며, 모델 로그 부재는 keep-running logger 수명 문제로
판명돼 시작 전 정체라는 추정을 철회했다. capture가 기본 100 ms 대기로
먼저 종료한 뒤 playback이 시작되는 경우도 확인했다. 따라서 실패 원인을
command-link 자체로 확정하지 않는다.
최신 증거와 실행 조건은
[기본 QK 조사](../dwc/i2s-default-qk-investigation-20260916.md)의
hardware command-link 첫 실제 DMA 검사 절을 참조한다.
기본 QK/freerunning 설정에서의 PIO 및 DMA 문제 전체가 해결됐다는 의미가 아니다.
기존 MCIPS 조건의 WAV PASS를 이 구현의 검증 결과로 사용하지 않는다.

기존 cyclic 경로는 period 완료 IRQ마다 CPU가 다음 DMA command의 레지스터를
다시 설정했다. MMIO 지연이 크면 다음 period의 시작까지 지연된다.
이번 변경은 DMA-350의 실제 command-link 기능으로 다음 command를 메모리에서
직접 읽도록 한다. 속성이 없는 controller의 autonomous 경로에는 추가 정지가 없으며,
QVP callback pacing은 아래에 설명한 실제 DONEPAUSE 기능을 사용한다.
QBox 전용 완료 횟수 레지스터를 만들지 않는다.

근거는 [Command linking](0086-Command-linking.md),
[Command structure](0087-Command-structure.md),
[Loading commands](0088-Loading-commands.md)이다.
첫 command는 레지스터로 설정하고, 이후 command는 LINKADDR로 찾는다.
마지막 descriptor도 LINKADDREN을 유지하고 첫 descriptor를 가리켜 순환한다.

## Linux 변경과 필요성

대상은
`hsoc-stack/components/primary_compute/linux/drivers/dma/arm-dma350.c`다.
아래는 이번 command-link 변경의 범위이며, 이미 존재하던 slave/cyclic 지원이나
이전 XSIZE residue 최적화를 이번 변경으로 분류하지 않는다.

| 변경 위치 | 변경 내용 | 필요한 이유 / 유지한 기존 경로 |
|---|---|---|
| `d350_chan`, probe | `HAS_CMDLINK` 읽기 및 보관 | 지원 채널만 hardware ring 사용. 미지원은 기존 IRQ 기반 software cyclic 유지 |
| `d350_desc` | hardware command 주소·CPU 매핑·크기, PCM 버퍼 주소·크기, 진행 주소 레지스터 보관 | CPU descriptor의 포인터나 가상 주소를 DMA에 전달하지 않고 별도 DMA 주소 사용 |
| `d350_prep_dma_cyclic()` | coherent DMA 메모리 할당, little-endian command 복사, 순환 LINKADDR/HI 설정 | DMA가 CPU IRQ 서비스 없이 다음 period를 읽도록 구성 |
| `d350_start_next()` | 첫 enable 전에 `dma_wmb()` | coherent allocation도 CPU store 순서까지 보장하지는 않으므로 descriptor 공개 순서 보장 |
| `d350_irq()` | hardware ring은 status acknowledge와 cyclic callback만 수행 | 이미 실행 중인 다음 command를 CPU가 다시 설정하거나 중복 enable하지 않음 |
| `d350_get_residue()` | memory-side 진행 주소로 ring residue 계산 | IRQ가 합쳐질 수 있으므로 software period index를 실제 위치로 간주하지 않음 |
| `d350_desc_free()` | 추가 DMA allocation 반환 | descriptor 수명 종료 시 DMA ring 누수 방지. 기존 CPU descriptor 배열도 그대로 해제 |

기존 CPU `command[16]`, slave command 생성 함수, linked CPU descriptor 배열은
유지했다. memcpy, memset, slave SG를 hardware command-link로 바꾸지 않았다.
allocation 실패 시 cyclic 준비는 실패를 반환한다. 실패를 숨기기 위해 자동으로
software cyclic으로 전환하지 않는다. 재사용 가능한 descriptor의 hardware ring은
그 descriptor와 같은 수명을 갖고, 새 전송 시작 시 첫 command가 다시 설정된다.

## Descriptor 메모리 형식

한 period당 16개의 32비트 little-endian word, 64바이트 stride를 할당한다.
이번 slave command에는 14개 word가 유효하며 마지막 두 word는 padding이다.
DMA가 해석하는 길이는 stride가 아니라 header의 register bitmap으로 결정된다.

| Word | 내용 |
|---:|---|
| 0 | Header: CTRL, SRCADDR/HI, DESADDR/HI, XSIZE/HI, SRCTRANSCFG, DESTRANSCFG, XADDRINC, 해당 trigger, LINKADDR/HI |
| 1 | CTRL: 기존 transfer width, CONTINUE, DONETYPE_CMD, 해당 peripheral trigger 사용 |
| 2–3 | SRCADDR, SRCADDRHI |
| 4–5 | DESADDR, DESADDRHI |
| 6–7 | XSIZE, XSIZEHI |
| 8–9 | SRCTRANSCFG, DESTRANSCFG |
| 10 | XADDRINC: 메모리 쪽 증가, peripheral FIFO 주소 고정 |
| 11 | RX는 SRCTRIGINCFG, TX는 DESTRIGINCFG |
| 12 | 다음 descriptor 주소 하위 32비트 OR LINKADDREN |
| 13 | 다음 descriptor 주소 상위 32비트 |
| 14–15 | Padding, hardware header에서 참조하지 않음 |

Header bit 19 또는 20 중 하나만 선택하므로 양방향 모두 word 11이 trigger다.
LINKADDR/HI는 header bit 30/31이다. `REGCLEAR`와 `INTREN` 갱신 bit는 설정하지
않으므로 초기 설정한 IRQ enable이 다음 command에도 유지된다.
REGRELOADTYPE은 0이며 매 descriptor에서 다음 period의 주소와 크기를 제공한다.
첫 period도 같은 내용의 descriptor를 갖지만 첫 실행은 기존 MMIO 설정을 사용한다.

## Non-coherent controller와 DMA allocation

`dma_alloc_coherent()`는 Linux DMA API가 CPU와 장치 양쪽에서 사용할 수 있는
일관된 descriptor 메모리 및 DMA 주소를 제공한다는 뜻이다. 실제 DMA controller가
cache-coherent transaction을 생성한다는 뜻은 아니다. non-coherent 플랫폼에서는
architecture DMA 구현이 적절한 CPU 매핑 등으로 이 계약을 제공한다.

따라서 DT에 `dma-coherent`를 추가하지 않는다. 기존 `CH_LINKATTR` 선택을 유지하며
non-coherent 장치는 NC/outer-shareable 속성을 사용한다. descriptor를 준비한 뒤
`dma_wmb()`와 enable write 순서를 지킨다. coherent allocation에 별도 streaming
`dma_map_single()`/`dma_sync_single_*()`를 중복 적용하지 않는다.
PCM 데이터 버퍼 자체의 DMA 매핑 계약은 기존 ALSA/DMAengine 경로와 별개로 유지된다.

QBox의 TLM 기능 모델이 속성값을 보관·전달하는 것만으로 실제 cache coherence나
메모리 ordering의 물리적 동등성을 검증했다고 주장하지 않는다.

## Residue, IRQ 합쳐짐 및 한계

Playback은 SRCADDR, capture는 DESADDR의 하위 32비트를 한 번 읽는다.
버퍼 시작 주소 하위 32비트를 unsigned subtraction하여 ring 내 위치를 구한다.
버퍼 길이를 U32_MAX 이하로 제한하므로 4 GiB 경계를 가로지르는 버퍼도 이 차이
계산으로 표현할 수 있다. 위치가 유효 범위를 벗어나면 이전 residue를 유지한다.

이 방식은 LINKADDR와 XSIZE를 따로 읽는 사이 다음 command가 로드되어 서로 다른
period의 값을 조합하는 문제를 피한다. 다만
[SRCADDR](0119-CH_SRCADDR.md)와 [DESADDR](0121-CH_DESADDR.md)는 TRM상 다음
실제 접근 주소에 대한 **approximate hint**다. 버스트·prefetch·진행 중 transaction
영향이 있으며 오디오 wire 전송 완료 시점이나 sample 단위 물리적 정확도를 의미하지 않는다.

DONE interrupt는 sticky bit이지 완료 횟수 counter가 아니다. IRQ마다 한 번
`vchan_cyclic_callback()`을 호출하고 ALSA가 실제 residue로 pointer를 갱신한다.
그 사이 여러 period가 완료되어도 CPU가 다음 period를 시작하는 작업은 필요 없다.
하지만 IRQ/ALSA 서비스 없이 전체 ring을 한 바퀴 이상 돌면 residue와 sticky bit만으로
놓친 바퀴 수를 복원할 수 없다. 기존 DMAengine cyclic 서비스 deadline은 여전히 필요하다.
이 구현이 QK의 과도한 MMIO 지연이나 임의 host 부하의 XRUN을 단독 해결하지 않는다.

## Pause, terminate와 descriptor 수명

기존 PAUSE/RESUME 경로를 유지한다. TRM에 따라 현재 command를 pause하고 resume하면
해당 command와 이후 link 처리가 계속된다. DT 속성이 없는 controller에서는
CPU callback을 기다리기 위한 DONEPAUSE를 추가하지 않는다.

probe에서 `of_property_read_bool(dev->of_node, "cyclic_done_pause")`를 읽어
각 채널에 저장한다. 플랫폼 compatible 검사는 없다. 속성은
`Documentation/devicetree/bindings/dma/arm,dma-350.yaml`에 boolean으로 정의했다.
hardware command-link와 `DMA_PREP_INTERRUPT`를 사용하는 cyclic descriptor를
준비할 때만 적용하며 각 command의 CTRL bit24 DONEPAUSEEN을
설정한다. 이는 TRM의 실제 pause 기능이며 가상의 완료 counter나 FIFO 확대가
아니다. IRQ에서 PAUSED/RESUMEWAIT를 bounded 확인하고 DONE을 acknowledge한 뒤,
기존 virt-dma tasklet이 원래 client callback을 실행한다. callback이 돌아온 후
active descriptor/cookie와 상태를 확인하여 RESUMECMD를 쓴다.

사용자 pause 상태에서도 완료한 callback의 pending은 해제하되 자동 재개하지
않는다. IRQ 전에 사용자 resume이 호출되면 sticky DONE을 검사해 callback보다
먼저 재개하지 않는다. terminate/error 완료에서는 원래 callback을 복원하여
descriptor reuse 시 callback을 중복 포장하지 않는다. pause-ready timeout은
명시적인 DMA_ERROR이며 STOP을 시도하고 IRQ를 mask/ack하되, controller가
아직 접근할 수 있는 ring을 조기에 해제하지 않는다. 기존 client의
terminate/synchronize 계약을 유지한다.

이 quirk는 **callback 처리 완료까지의 기능적 pacing**이다. 사용자 프로세스의
PCM refill 완료까지 보장하지 않으며, pause 중 기존 I2S functional pacing에
의존하므로 물리적 연속 48 kHz 타이밍을 검증한 것으로 간주하면 안 된다.
2026-09-16 관련 SystemC TX/RX pause/ack/resume 검사 5개가 PASS다.
실제 Linux에서도 명시적 DONEPAUSE/wait/affinity 조건으로 양방향 긴 WAV,
반복 20회 및 홀수 길이 WAV가 전체 PCM 일치로 PASS했다. 조건과 산출물은
[실행 기록](../dwc/i2s-default-qk-investigation-20260916.md)의
"DONEPAUSE 실제 Linux WAV 검사 결과" 절을 참조한다.

STOP과 기존 `d350_terminate_all()`/`d350_synchronize()` 경로를 유지한다.
즉시 STOP 확인이 끝나지 않으면 `stopping` 상태로 지연 완료를 기다리고, hardware가
quiescent해진 뒤 terminated descriptor를 해제한다. 진행 중 descriptor fetch가 있는 동안
DMA 메모리를 먼저 해제해서는 안 된다. `d350_desc_free()`가 추가 allocation을 반환하는
것은 이 기존 수명 규칙 아래에서만 안전하다. 오류 완료 경로 역시 장치가 더 이상
descriptor를 fetch하지 않는다는 controller의 오류 정지 계약에 의존한다.

## 검증 범위와 남은 항목

- Linux 변경의 `git diff --check`: PASS.
- 해당 driver diff의 `checkpatch`: 0 errors / 0 warnings.
- component test 소스:
  `hsoc-stack/tools/qbox-platform/tests/components/dma350/dma350-tests.cc`.
  high-address descriptor fetch, REGCLEAR, peripheral 순환 link와 sticky DONE,
  pause/resume, disable, DONEPAUSE, fetch 오류, 지연 fetch 중 STOP/reset 시나리오가 있다.
  이 절의 test 목록은 **소스에 존재하는 검사항목**이며 실행 PASS를 대신하지 않는다.
- Linux에서 생성한 정확한 14-word/64-byte descriptor 형식의 TX/RX 반복 및 wrap,
  큰 XSIZEHI count 및 DONEPAUSE 변형: focused model test PASS.
- provider/kernel 빌드 및 해당 산출물로 실제 QBox/Linux I2S 양방향 WAV 비교:
  명시적 DONEPAUSE 조건에서는 **PASS**, autonomous cyclic에서는 **FAIL**.
  PIO의 별도 조건부 PASS 및 정확한 실행 조건은 위 실행 기록을 참조한다.
- stop/start, 비정렬 끝부분, 전체 PCM 일치, zero frame/누락/XRUN,
  기존 SPI/UART/memory DMA 회귀를 통과해야 목표 완료를 판단한다.

실행 후에는 실제 명령·로그 경로·산출물 식별값·PASS/FAIL을 이 문서 또는 연결된
검증 문서에 추가해야 한다. 단순 빌드 성공은 runtime PASS가 아니다.

# Apollo QVP full QBox DMA350 / I2S 개선 계획

> **코드 정리 후 상태:** 아래 실험 수치와 명령은 정리 전 artifact의 기록이다.
> 계측, IRQ cache, scheduling/반복 실행/UKI 교체 도구는 live source에서 제거하고
> [패치](patches/README.md)로 보관했다. 해당 실험 명령은 패치 재적용·재빌드가 필요하다.
> 현재 남긴 코드와 검증 범위는 [코드 정리 기록](05-code-cleanup.md)을 따른다.


작성일: 2026-10-01. 대상은 **DMA350과 DW_apb_i2s를 모두 qemu-components로 사용하는 두 QBox profile**이다. standalone system QEMU, SystemC I2S 혼합 구성의 결과는 이번 비교에 포함하지 않는다.

후속 구현·실험은 [구현 및 실험 기록](04-implementation-results.md)에 누적한다. 아래 01~03 및 evidence.json은 계획 수립 당시의 기준이며, 이후 재시험에서는 AP-only PIO 실패도 관측됐다.

**실패 지점은 지속적인 ALSA 스트림 처리 중의 XRUN이며, 기본 정책의 full audio는 아직 FAIL이다.** 계획 당시 동일 artifact로 AP-only가 통과하고 full이 실패했다. 후속 PIO stream lock 및 native IRQ cache 후보의 계측 OFF 3회 반복에서는 full PIO와 AP-only DMA가 통과했지만, AP-only PIO에 간헐적 PCM XRUN이 남았고 full DMA는 PCM/WAV에 실패했다. 후보 전 반복 결과도 별도로 보존한다. DMA 메모리 검사는 모두 통과했다. 상세 수치와 구현은 [후속 실험 기록](04-implementation-results.md)을 기준으로 한다.

추가 CFS 대조군에서는 **audio DMA IRQ 4개를 SCHED_OTHER, 오디오 명령만 nice −10**으로 설정하여 full DMA memory 60/60, PCM 12/12, WAV 6/6을 같은 부팅의 3회 반복에서 통과했다. PFDI timeout·RCU stall은 관측되지 않았다. [재현 script](patches/05-audio-experiment-tools.patch)는 선택적으로 적용하고 복원하며 기본 정책을 바꾸지 않는다. 이 결과는 조건부 기능 PASS이고 기본 full DMA 해결 및 cold/warm 각 10회 최종 gate와 구분한다.

두 구성 모두 host-memory DMI가 켜져 있고 audio DMA와 RAM은 AP router에 직접 연결된다. 따라서 DMI enable 누락이나 full의 추가 ATU 경유를 원인으로 단정할 수 없다. 실제 CPU/DMA별 DMI 사용, native MMIO alias, DMA period IRQ와 재설정 지연, ALSA pointer 및 CPU idle 복귀를 함께 측정해야 한다.

## 문서 구성

| 문서 | 내용 |
|---|---|
| [구성 차이와 실패 분석](01-analysis.md) | 재현 증거, 동일한 부분과 차이, 현재 데이터 경로, 확정 사실과 가설 |
| [대안별 구현 계획](02-plans.md) | freerunning을 유지하는 P0~P7 계획, 적용 조건·수정 위치·위험·완료 기준 |
| [실험 순서와 합격 기준](03-validation.md) | 실행 명령, 계측 계약, 독립 변수 실험, DMA/PIO 및 WAV 회귀 검사 |
| [증거 스냅샷](evidence.json) | 기존 실행 결과 요약, WAV 직접 비교, 증거 파일 hash, 조사 시점 Git HEAD |
| [구현 및 실험 기록](04-implementation-results.md) | 후속 수정, 계측 결과, 수정 전후 실행과 남은 실패 |
| [코드 정리 및 패치 보관](05-code-cleanup.md) | 필수 수정, 제거한 실험 코드, 재적용 절차 및 정리 후 검증 |
| [구현 증거 인덱스](implementation-evidence.json) | 후속 실행별 판정, 원본 result 경로와 SHA256 |

## 변경하지 않을 조건

- 현재 `multithread-freerunning`, `quantum_keeper`, 10,000,000ns quantum과 각 도메인의 TCG mode를 유지한다. AP는 `MULTI`이다. icount 도입, 강제 lockstep/barrier, global time 동기화 변경은 대안에서 제외한다.
- full의 RSE, SI CL0/SCP, SI CL1/Zephyr, AP secure firmware 및 4개 AP CPU를 유지한다. 도메인을 mock으로 바꾸거나 GIC security를 꺼서 얻은 결과는 full 합격으로 인정하지 않는다.
- I2S `functional_pacing=true`, frame period 20,833ns를 유지한다. sample drop/반복, 숨은 무제한 버퍼, XRUN 복구 후 성공 처리, 녹음 prefix만 비교하는 방식은 사용하지 않는다.
- 현재 48kHz S16_LE stereo, 기존 PCM period/buffer와 WAV 전체 파일 비교를 최종 기준으로 유지한다. 물리 I2S/RTL/FVP timing parity는 이 기능 검증의 범위 밖이다.

## 권장 진행 순서

1. **P0 계측**으로 DMI/alias 상태와 첫 XRUN 직전의 시간을 확보한다. 기존 로그로는 특정 원인을 선정할 수 없다.
2. full을 그대로 유지한 **P4 host/guest scheduling 실험**과 **P5 idle/IRQ wakeup 진단**을 각각 독립적으로 수행한다. 이는 빠른 원인 분리 단계이다.
3. RAM fallback이 많으면 **P1 DMI**, native MMIO fallback이 많으면 **P2 same-instance MemoryRegion alias**를 우선한다. 이미 direct path라면 해당 최적화는 보류한다.
4. native callback/메모리 처리 비용이 지배적이면 **P3 bounded DMA 최적화**를 적용한다. pointer/driver 오류는 **P7**에서 별도로 수정한다.
5. **P6 userspace/buffer 실험**은 지연 민감도와 서비스 방식을 확인한다. buffer 확대만으로 최종 합격을 대체하지 않는다.

완료 조건은 full의 기존 설정에서 DMA350 memory, DMA/PIO PCM 각 4/4, WAV 모드별 양방향 2/2의 전체 byte 일치, 예상치 못한 XRUN 0건, full BSP 22/22 및 AP-only audio 회귀 통과이다. 계획 수립 시점에는 모델 수정이나 새 runtime 시험을 수행하지 않았으며, 후속 구현 결과와 구분한다.

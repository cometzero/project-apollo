# 07. System SW Core Architecture

[전체 목차](README.md) · [이전 장: Component SW](06-component-software-architecture.md)

Interrupt는 실행을 깨우고 Mailbox는 Domain을 연결하며 Timer는 deadline을 만들고 Watchdog은 복구를 시작한다. 이 기반 위에서 power·diagnostics·fault reporting이 동작한다. 각 상세 문서는 model→Lua wiring→firmware/driver→service의 경계를 따라간다.

## 1. 네 가지 기능을 한 번에 읽기

| 기능 | HW/model이 제공하는 것 | SW가 추가하는 것 | 관찰해야 할 완료 조건 |
|---|---|---|---|
| Interrupt | pending, routing, priority, CPU exception | ISR 등록, source clear, deferred work | 원하는 ISR·service가 실제 실행 |
| Mailbox | doorbell/FCE 상태와 peer IRQ | buffer ownership, protocol, timeout, retry | response 또는 endpoint의 protocol-level 완료 |
| Timer | count, comparator, expiry IRQ | timeout queue, scheduler, callback | deadline에 해당 작업 수행 |
| Watchdog | feeding 감시, WS0/WS1 | recovery policy, image reload, reset sequence | 새 boot와 요구 service 복귀 |

**공통 tracing 순서:** source register/상태 → Lua 연결 → interrupt controller → ISR → 상위 service. Model이 존재하는지와 최종 consumer가 사용하는지는 다른 질문이다.

## 2. 주제별 상세 문서

| 순서 | 문서 |
|---|---|
| 07.1 | [Interrupt와 GIC — source에서 ISR까지](07-system/01-interrupt-and-gic.md) |
| 07.2 | [Mailbox와 IPC — notification, payload, completion](07-system/02-mailbox-and-ipc.md) |
| 07.3 | [Timer와 deadline — count에서 callback까지](07-system/03-timer-and-deadlines.md) |
| 07.4 | [Watchdog과 AP recovery — WS1에서 service 복귀까지](07-system/04-watchdog-and-recovery.md) |
| 07.5 | [Power와 performance — PSCI, SCMI, PPU, DVFS](07-system/05-power-and-performance.md) |
| 07.6 | [PFDI와 core별 monitoring](07-system/06-pfdi-and-monitoring.md) |
| 07.7 | [FMU·SSU·RAS — fault identity에서 OS 기록까지](07-system/07-fmu-ssu-and-ras.md) |
| 07.8 | [SMCF — sampling control과 data delivery](07-system/08-smcf-sampling.md) |

01→04는 core mechanism과 완료 조건, 05→08은 이를 사용하는 platform service 순서다. Mailbox·Timer를 먼저 이해하면 SCP의 power와 fault state machine에서 event·alarm이 필요한 이유를 읽기 쉽다.

<a id="gic-mechanism"></a>
<a id="mailbox-worked-example"></a>
<a id="timer-worked-example"></a>
<a id="reset-mechanism"></a>
<a id="power-mechanism"></a>
<a id="safety-mechanism"></a>

기존 anchor의 상세 내용: [GIC](07-system/01-interrupt-and-gic.md#gic-mechanism), [SCMI worked example](07-system/02-mailbox-and-ipc.md#mailbox-worked-example), [Timer 계산](07-system/03-timer-and-deadlines.md#timer-worked-example), [AP reset](07-system/04-watchdog-and-recovery.md#reset-mechanism), [Power](07-system/05-power-and-performance.md), [PFDI](07-system/06-pfdi-and-monitoring.md).

## 3. Safety architecture: test·감시·fault 수집·상태 보고

Safety 경로는 앞의 네 core 기능을 함께 사용한다. PFDI가 CPU test를 호출하고, SCMI가 결과를 전달하며, timer가 report deadline을 감시한다. FMU는 fault source를 모아 interrupt를 발생시키고, SCP는 원인을 해석하여 SSU 상태와 recovery policy를 제어한다.

| 계층 | 답해야 하는 질문 | 주요 주체 |
|---|---|---|
| Test execution | 어떤 test를 어느 CPU에서 실행했는가 | AP TF-A / CL1 Zephyr PFDI |
| Liveness monitoring | 해당 CPU가 정해진 시간 안에 결과를 보고했는가 | CL0 `pfdi_monitor` |
| Fault aggregation | 어느 block의 어떤 fault가 발생했는가 | device FMU → System FMU tree |
| System status | 외부에 어떤 safety 상태를 알릴 것인가 | SCP policy + SSU |
| Error diagnosis | syndrome·CPER·trace에 어떤 원인이 남는가 | RAS handler, Linux, rasdaemon |

## 4. 세미나용 검증 체크포인트

| Evidence tier | 예 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|---|
| Source/config | Lua bind, DTS, Kconfig, module list | 의도된 구성·선택 경로 | 실제 IRQ·driver 실행 |
| Host/model test | MHU register, watchdog expiry test | 지정 model contract | full-system service 복구 |
| Guest runtime | named marker, ISR count, RPMsg 왕복 | 실행한 구성의 해당 시나리오 | 모든 구성·실리콘 parity |
| Cross-platform comparison | matching image로 FVP/QVP 비교 | 비교한 observable behavior | physical timing·안전 qualification |

발표자가 던질 질문은 다음과 같다.

1. Interrupt가 오지 않으면 source pending, mask, route, ISR 중 어디까지 확인했는가?
2. Mailbox ACK가 왔을 때 protocol response까지 완료되었는가?
3. Timer 오류에서 count rate와 comparator deadline을 각각 확인했는가?
4. Watchdog reset 후 새 boot ID와 service 정상 복귀까지 확인했는가?
5. Power request의 protocol 응답과 대상 CPU/cluster의 실제 상태 전환을 구분했는가?
6. Fault ACK 이전에 leaf identity와 syndrome을 보존하고 SSU·OS 소비 경로까지 확인했는가?

이번 문서 작업에서는 새 build/runtime 시험을 실행하지 않았다. 실제 검증은 canonical runner와 retained evidence를 사용하고, 미연결 watchdog 출력·physical timing·coherence·silicon safety 범위는 별도로 남긴다.

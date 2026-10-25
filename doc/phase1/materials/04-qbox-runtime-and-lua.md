# 04. QBox 실행 구조와 Apollo QVP Lua

> **발표 목표:** launcher의 입력이 실행 가능한 platform으로 조립되고, guest의 MMIO·IRQ와 시간이 진행되는 경계를 설명한다.
> Source 기준: 2026-10-25 checkout. 문서 작성·분할 과정에서는 build/runtime을 실행하지 않았다.

[전체 목차](README.md) · [이전: Build Architecture](03-project-build-architecture.md) · [다음: FVP 비교](05-fvp-qbox-comparison.md)

QBox는 QEMU CPU와 SystemC 모델을 연결하는 framework이고, Apollo QVP는 그 위에 조립한 platform이다.
이 장은 실행 명령 한 줄을 **입력 선택 → object 생성 → Lua composition → transaction 실행**으로 나누어 읽는다.
각 subchapter는 목적과 구성부터 시작해 실제 함수·interface, 실패 진단까지 이어진다.

![Launcher에서 QBox와 guest domain까지](diagrams/04-qbox-runtime.drawio.svg)

[draw.io 편집 원본](diagrams/04-qbox-runtime.drawio) · [기존 HTML 보기](diagrams/04-qbox-runtime.html)

## 학습 순서

| 순서 | Subchapter | 답할 질문 | 중심 source / 그림 |
|---|---|---|---|
| 04.1 | [Launcher와 runtime process](04-qbox/01-launcher-runtime.md) | 어떤 provider·image·Lua를 선택하고 어떻게 결과를 남기는가? | shell, full runner, runtime child / 실행 구조 |
| 04.2 | [QemuInstance와 object 생성](04-qbox/02-qemu-instance-construction.md) | Lua table이 언제 SystemC module과 QOM object가 되는가? | ModuleFactory, QemuInstance, QemuDevice / domain 배치 |
| 04.3 | [Lua composition과 boot/reset](04-qbox/03-lua-composition.md) | SoC·VP·Board는 무엇을 정의·수정하며 CPU를 언제 release하는가? | ctx/platform, full-system profile / composition·boot |
| 04.4 | [Address와 time transport](04-qbox/04-address-time-transport.md) | MMIO 한 건은 어느 주소·thread·target을 지나고 IRQ와 DMI는 어떻게 다른가? | router, addrtr, initiator, QK / fabric·MMIO·time |

처음 읽을 때는 위 순서를 따른다.
실행 실패를 조사할 때는 04.1의 process/결과 경계에서 시작하고,
Lua descriptor 오류는 04.2~04.3, MMIO·IRQ·timer 문제는 04.4로 이동한다.

## 이 장의 핵심 구분

| 구분 | 현재 구조 | 다음에 확인할 것 |
|---|---|---|
| Host와 guest | launcher/runner의 준비 순서와 RSE-first firmware boot 순서는 다름 | 선택 input, domain UART, release owner |
| Domain과 instance | AP·RSE·SI CL0·SI CL1 4개 firmware domain, 기본 QemuInstance 5개 | RSE CPU/helper 분리와 instance별 device |
| Source와 설치본 | launcher의 기본 Lua는 `.qboxconf`가 가리키는 installed provider | 실제 config path와 provider identity |
| Definition과 최종 연결 | AP `mem.bind`는 define 이후 connect 단계에서 AP router로 바뀜 | composition 마지막 descriptor |
| Transport와 notification | MMIO completion, device IRQ, DMA initiator는 별도 경로 | target response, signal/GIC, memory payload |
| 기능과 시간 | freerunning·DMI는 실행 정책과 최적화이며 silicon timing 보장이 아님 | guest contract와 model fidelity 범위 |

Full-system은 RSE·SCP·Zephyr·AP firmware chain을 함께 실행한다.
AP-only direct Linux profile과 boot/login launcher의 검증 범위는 각각 다르다.
Source에 구현이 있다는 사실, 과거 runtime 기록, 이번 문서의 source 확인을 같은 PASS로 합치지 않는다.

## 발표에서 따라갈 한 가지 사례

AP가 PFDI MHU의 `0x4011100c`에 32-bit 값을 쓴다고 가정한다.
04.1에서는 이 AP를 실행한 provider와 image를 찾고, 04.2에서는 CPU wrapper의 memory initiator를 찾는다.
04.3에서는 `ap_router`로 확정되는 binding을 읽고,
04.4에서는 `addrtr`를 거쳐 `0x400003b38100c`, 최종 register offset `0x100c`가 되는 과정을 계산한다.
이후 receiver IRQ와 firmware ACK는 MMIO 반환과 별도로 추적한다.

연결해서 읽기: [Source Architecture](02-project-source-architecture.md),
[Build Architecture](03-project-build-architecture.md),
[Component SW Architecture](06-component-software-architecture.md),
[System SW Core](07-system-software-core.md).

주요 source: [canonical runner](../../../scripts/run/run_qbox_apollo_fvp_full.py),
[runtime child 구현](../../../scripts/run/qbox_apollo_runtime.py),
[Apollo full-system profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua),
[현재 platform README](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/README.md).

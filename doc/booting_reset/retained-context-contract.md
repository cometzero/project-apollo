# Domain-off retained context 계약

2026-09-15. 대상은 apollo-fvp AP domain 및 SI CL1이다.
이 문서는 구현 완료 보고가 아니라 현재 배치와 필요한 복구 순서를 구분한다.

## 설계 입력

사용자가 확정한 조건: Always-on power domain 메모리와 DRAM에 더해 **AP SRAM도
전원 차단 중 내용을 보존한다**. Firmware가 매핑한 AP secure SRAM 1 MiB와 nonsecure SRAM 1 MiB를
포함하며 BL31 code/data/BSS, BL2 reset entry, mailbox와 SCMI shared memory가
이 계약의 대상이다. CL1 LLRAM의 retention을 추가로 가정하지 않는다.
내용 보존과 전원 OFF 중 버스 접근 가능 여부는 다르므로 CL0의 AP SRAM 접근은
SYS0 OFF 전에 quiesce하고 실제 ON 이후에만 재개한다.
검증은 PPU OFF→ON과 기존 실행 context 복귀를 모두 요구한다.

## 현재 실행 이미지

| 항목 | 현재 주소/영역 | 필요한 조치 |
| --- | --- | --- |
| AP BL31 code/data/BSS | AP SRAM `[0x4000, 0x33000)` | AP SRAM retention으로 보존; OFF 전 cache/context 정리 필요 |
| AP warm entry | `0x4160` | 그 주소의 코드가 유효해진 뒤 진입 |
| AP trusted mailbox | AP SRAM `0x1ff8` | 내용 보존 후 기존 warm entry 사용 |
| AP 초기 RVBAR | AP SRAM `0x82000` | BL2 코드는 보존; RVBAR register retention은 별도 확인 |
| CL1 Zephyr RAM | `[0x140000000, 0x140800000)` | 동적 stack/heap을 포함한 live-state 보존 범위 정의 |
| CL1 HIPC SHRAM | CL1 view `[0xe0130000, 0xe01b0000)` | AP shared SRAM alias이며 DRAM retention pool이 아님 |
| SMD SRAM | global `[0x2000060000000, 0x2000060100000)` | 기존 SMCF 사용 영역과 분리한 명시적 partition 필요 |

근거는 `build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-a/`
아래 `bl31.map`과 `apollo_fvp_safety_island_c1-zephyr/zephyr-demos-cl1/`
아래 `zephyr.map`, `zephyr.dts`이다. QVP map과 혼용하지 않는다.

TF-A의 기존 `ARM_BL31_IN_DRAM=1` 경로는 현재 설정에서
`[0xff000000, 0xff0fc000)`를 선택하며 SPMC base `0xffc00000`과 겹치지 않는다.
그러나 이 옵션만으로 SRAM의 BL2 reset stub, mailbox 및 SCMI channel은
복원되지 않는다. 옵션은 아직 적용하지 않았다.

SMD SRAM은 기존 SMCF buffer가 있는 메모리다. AP의 기존 alias
`[0x40740000, 0x40742000)`를 resume stub로 덮어쓰면 안 된다. 새 partition과
ATU mapping을 정의하고 instruction fetch를 검증해야 한다. CL0 cold-start의
전체 SMD SRAM clear를 warm-resume 경로에서 재실행해서도 안 된다.

## 구현 순서와 검증 경계

1. AP는 기존 SRAM retention을 사용하며 별도 DRAM relocation/snapshot을 하지 않는다.
   추가 저장이 필요한 domain은 보존 DRAM/AON partition을 firmware와 OS 모두에서 예약한다. 다른 서비스의
   buffer 또는 OS가 할당 가능한 DRAM을 임의 snapshot pool로 사용하지 않는다.
2. Suspend 요청자가 wake deadline/source를 CL0에 위임한다. CL0 timer IRQ34는
   이미 timer driver가 소유하므로 기존 ISR을 덮어쓰지 않고 별도 alarm을 사용한다.
   AP RTC IRQ300이 CL0 wake로 전달된다는 가정은 하지 않는다.
3. CPU/device와 coherent traffic을 quiesce하고 context를 보존 영역에 저장한다.
   CL1은 R82 PWRDN/WFI handshake가 필요하며 debugger execution gating은 대체가 아니다.
4. Last-core OFF를 확인하고 retained SRAM의 최종 context 저장 상태를
   확정한 뒤 domain OFF를 요청한다. Software state만으로 OFF를 판정하지 않는다.
5. AON wake에서 domain ON, CMN/ATU 및 메모리 접근 복원, retained SRAM 유효성
   확인, RVBAR 설정 확인, CPU release 순서를 지킨다. SRAM retention만으로
   GIC/CMN/CPU register retention을 가정하지 않는다.
6. CPU/GIC/device context를 복원한다. AON counter는 과거 값으로 되돌리지 않는다.
   저장한 timer deadline이 이미 지났으면 OS timer 규칙에 따라 만료를 처리한다.
7. CPU register·stack·메모리 sentinel, 실제 IRQ, timer와 반복 cycle을 검증한다.
   Cold reboot, 단순 shell return, debugger snapshot 복원은 context resume PASS가 아니다.

GIC quiesce에서는 CPU interface disable과 Redistributor sleep을 구분해야 한다.
Per-core `GICR_WAKER.ProcessorSleep` 설정 및 `ChildrenAsleep` 확인이 필요하며,
전체 GIC의 Sleep 요청은 모든 Redistributor가 잠든 상태를 요구한다. CL0가 살아
있는 CL1 단독 power-off에서 전체 GIC Sleep을 사용하면 안 된다.
[Arm GIC-720AE power management](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Other-power-management),
[GICv3/v4 overview](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/GICv3_v4_overview.pdf?revision=65f91645-cd52-4795-952b-f01095ff5ef8).

현재 완료/실패 증거는 [구현 상태](suspend-resume-implementation-status.md)에 기록한다.

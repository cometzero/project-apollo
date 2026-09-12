# Apollo timer 하드웨어 구성

조사일: 2026-09-11. [소프트웨어 구성](software.md),
[실행 결과와 재현 명령](test-results-2026-09-11.md)을 함께 참조한다.

아래는 9월 11일 조사 기준이다. 이후 SysTick 추가와 SI CL1 125MHz 정렬은
[9월 12일 구현·검증 문서](implementation-2026-09-12.md)에 기록한다.

기준 문서는 Arm Zena CSS Software Developer Guide r0p1,
`110125_0001_01_en`, 2026-01-27 발행본이다.
[문서 정보](../arm_zena_css_dev_guide/00-front-matter.md)와
[programmer model](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md)을
기준으로 하드웨어 사양과 FVP/QVP 모델을 구분했다.

## Counter와 timer의 관계

System Counter는 공통 시간을 나타내는 64-bit count를 만든다.
Timer는 해당 count와 자신의 compare 값을 비교하여 interrupt를 발생시킨다.
Timer의 enable이 0이어도 counter 자체는 계속 증가할 수 있다.

AP와 Safety Island는 CSS REFCLK System Counter를 공유한다.
각 CPU와 MMIO timer frame은 comparator, enable, mask 및 IRQ 상태를 따로 갖는다.
RSE는 하드웨어상 별도 Local System Counter(LSC)를 가지며,
TIMER0~3에 `CNTVALUEB`를 공급한다. M55 내부 SysTick은 이 네 timer와 별개다.
CL0/CL1은 Cortex-R82AE 계열이며 M-profile core가 아니다.

## 코어와 서브시스템

아래 PPI는 GIC INTID로 표기한다. DT의 `GIC_PPI n`은 INTID `16+n`이다.
SPI는 peripheral 번호이며 GIC INTID는 `32+SPI`다.
RSE IRQ 번호는 NVIC 외부 IRQ 번호로 GIC 번호와 관계없다.

| 영역 | 하드웨어 구성 | 주소와 interrupt |
| --- | --- | --- |
| CSS/SMD | REFCLK counter control/read, multichip sync | Control `0x020000D0100000`, Read `0x020000D0110000`, Sync `0x020000D0120000` |
| AP Cortex-A720AE | 각 PE별 Generic Timer; 공통 physical counter | PPI 19/20/26/27/28/29/30. 실제 OS가 선택하는 timer는 실행 모드에 따라 다름 |
| AP REFCLK MMIO | control과 secure/NS timer frame | Control `0x1A810000`; secure frame 1 `0x1A820000`, SPI48; NS frame 0 `0x1A830000`, SPI49 |
| SI CL0 Cortex-R82AE | primary와 redundant DCLS core, architectural timer 및 MMIO timer | PPI20/27/29; CNTCTL `0x2A6F0000`, CNTBase `0x2A720000`, INTID34 (SPI2) |
| SI CL1 Cortex-R82AE | 현 하드웨어 guide에는 없는 CFG2 FVP 확장, 4 cores | FVP/QVP DT timer INTID29/20/27/19. CL0의 하드웨어 표를 그대로 적용할 수 없음 |
| RSE Cortex-M55 | primary와 redundant DCLS, software-visible CPU 1개 | banked secure/NS SysTick, `0xE000E010`부터 CTRL/LOAD/VAL/CALIB, exception 15 (`SysTick_IRQn=-1`) |
| RSE LSC | TIMER0~3의 counter source | Secure control `0x5015A000`, read `0x5015B000` |
| RSE TIMER0~3 | timestamp comparator 4개 | Secure `0x58000000 + N*0x1000`, NS alias `0x48000000 + N*0x1000`; NVIC IRQ3/4/5/27 |
| RSE SOC_TIMER0/1 | AON system timestamp timer 2개 | Secure `0x50158000/0x50159000`, NS `0x40158000/0x40159000`; IRQ59/60 |
| RSE SLOWCLK timer | AON low-frequency timer | Secure `0x5802F000`, NS `0x4802F000`; IRQ2 |

하드웨어 guide의 주요 근거는 programmer model의 AP 주소표(102~112행),
CSS counter 표(280~295행), RSE 주소표(615~706행), SI 주소표(1227~1230행),
AP IRQ 표(1330~1418행), RSE IRQ 표(1505~1576행), SI IRQ 표(1634~1661행),
RSE timer 및 LSC 설명(14940~15043행)이다.
[FVP 구성 차이](../arm_zena_css_dev_guide/08-fixed-virtual-platform.md)도 참조한다.

## Clock, reset 및 watchdog

CSS REFCLK의 현재 FVP/QVP 실효 count rate는 125MHz다.
RSE CPU SYSCLK, peripheral clock, SysTick clock, timestamp counter clock은
서로 다른 항목이다. TF-M의 CPU clock 기본값 100MHz나 TIMER0 테스트의 32MHz
상수를 timestamp counter의 실제 속도로 해석해서는 안 된다.
RSE LSC의 실제 입력 clock 배선과 SOC_TIMER0/1 count source는 이 로컬 guide만으로
확정하지 않았다.

TIMER0~2는 `nWARMRESETSYS_RSS`, TIMER3/SOC_TIMER0/1/LSC는
`nWARMRESETAON` 영역이다. 따라서 warm reset이 모든 timer와 공통 counter를
동시에 0으로 만드는 것은 아니다.
CSS Generic Timer Synchronization block은 primary/secondary chip 사이의
동기화를 담당한다. 각 코어에 별도 시간을 생성하는 timer가 아니다.

Watchdog도 counter를 사용하지만 주기적 OS tick과 용도가 다르다.
AP watchdog, SI watchdog(`0x2A700000/0x2A710000`, INTID37/SPI5),
RSE timestamp watchdog 및 SLOWCLK watchdog(`0x5802E000`, NMI)을
일반 timer와 구분해야 한다. 이번 테스트는 watchdog reset을 유발하지 않았다.

## 현재 FVP와 QVP의 차이

| 항목 | FVP | QVP |
| --- | --- | --- |
| CSS/AP/SI count | REFCLK 기반 | SystemC `arm_system_counter`를 QEMU CPU/MMIO timer에 mirror |
| RSE TIMER0~3 | 실행 검사에서 125MHz count, 각 comparator/IRQ 동작 | `qemu_sse_timer` 4개, comparator/IRQ 동작 |
| RSE count source | 과거 Iris 조사에서는 CSS alias, 독립 LSC window 미제공 | 현재 기본 `QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR=true`: CSS 125MHz 공유. false일 때 local counter 경로 선택 |
| M55 SysTick | reload register write/read 검사 PASS | CPU+NVIC wrapper에 SysTick device/clock 연결 없음. reload write/read FAIL |
| SI CL1 | CFG2 FVP 확장 | 4 cores 및 architectural timer; 100MHz 설정과 125MHz mirror 관계는 별도 검증 결과 참조 |
| SOC_TIMER0/1, SLOWCLK | 과거 instance 조사에서 SOC_TIMER0/1 미제공, SLOWCLK timer/watchdog 존재 | Apollo 구성에서 기능 모델 미확인. 이번 runtime 검사 대상 아님 |

과거 FVP instance 조사 결과는
[기존 FVP 분석](../arm-zena-css-fvp-timer-counter-analysis-ko.md)에 있으며,
이번에는 모든 instance 존재 여부를 재측정하지 않았다.
2026-07 문서의 QVP 독립 RSE counter 설명은 현재 기본 설정과 다르다.
현재 설정은 FVP 호환성을 위한 CSS mirror이며 하드웨어의 독립 LSC를 재현하지 않는다.

QVP의 직접 근거:

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua`: RSE mirror 기본값.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua`: 네 timer, aliases, reset/IRQ 연결.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/rse-cpu/src/apollo_rse_cpu.h`: M55 wrapper.
- `hsoc-stack/tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_m55/include/cortex-m55.h`: CPU와 NVIC 생성.
- `hsoc-stack/tools/qemu/hw/intc/armv7m_nvic.c`: SysTick MMIO를 제외한 NVIC SCS 구현.
- `hsoc-stack/tools/qemu/hw/arm/armv7m.c`: 완전한 ARMv7M container의 SysTick 생성·clock·IRQ 연결 비교 기준.

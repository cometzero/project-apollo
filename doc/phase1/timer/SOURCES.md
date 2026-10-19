# Apollo Timer SW Implementation Report — Source References

[Apollo Timer SW Implementation Report](README.md) · [Timer / Counter Map](TIMER-MAP.md) · [draw.io 원본](apollo-timer-architecture.drawio)

## 소스 기준 이력

아래 revision 표는 2026-10-16의 조사 기준이다. 당시 checkout과 canonical `apollo-qvp-saturn-v.lua` full-system 구성을 확인했다. `build/conf/local.conf`에는 `MACHINE ??= "apollo-qvp"`, `RD_ASPEN_VARIANT = "cfg2"`, `PC_CPUS_COUNT_DEFAULT ??= "4"`, `TMPDIR = "${TOPDIR}/tmp_baremetal"`가 있다. BitBake를 실행해 최종 변수·산출물 설정을 다시 평가하지 않았다.

행 번호는 조사 시점의 위치이며 파일 링크는 repository 상대 경로다. 실행 결과는 본문 5장에서 관리한다.

| Checkout | HEAD (12자리) | Checkout | HEAD (12자리) |
|---|---|---|---|
| root | `a37dcba0d32d` | arm-zena-css | `bf34d9e71f67` |
| QBox | `b8a0499359ba` | qbox-platform | `17ac742e2257` |
| QEMU | `2d83203dc366` | Linux | `728c53f73006` |
| TF-A | `532c9e6dc679` | U-Boot | `312634600420` |
| OP-TEE | `a2a275865d65` | SCP | `b17d6d0873b9` |
| TF-M | `94c5d43ae48c` | Zephyr | `992228a26f3f` |
| zephyr_hsoc_src | `35fde511340d` | meta-hsoc-bsp | `c691b907bcff` |

<a id="hardware"></a>

## HW 계약 · register 의미

| ID | 근거 | 확인 내용 |
|---|---|---|
| H1 | [Zena programmer's model](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 9297–9327행 | chip 간 counter sync handshake·timeout·network delay·status |
| H2 | [같은 문서](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 14942–14946·15016–15043행 | RSE TIMER0–3, PPC, PD_AON, SYS/RSS·AON reset, LSC CNTVALUEB |
| H3 | [Timestamp timers](../../corstone-reference-system-architecture/0071-Timestamp-based-timers.md), [Timer operation](../../corstone-reference-system-architecture/0241-System-Timer-operation.md) | comparator·TVAL·AIVAL·mask·IRQ clear |
| H4 | [Counter scaling](../../corstone-reference-system-architecture/0239-CNTSCR0-CNTSCR1-Counter-Scaling-registers.md) | 8.24 scaling, SCEN, HWCLKSW 의존 |
| H5 | [CNTCTLBase](../../arm_architecture_reference_manual/7172-I2.3.1-The-CNTCTLBase-frame.md), [CNTBaseN](../../arm_architecture_reference_manual/7173-I2.3.2-The-CNTBaseN-and-CNTEL0BaseN-frames.md) | counter control과 timer frame control의 구분 |
| H6 | [Arm Generic Timer](https://documentation-service.arm.com/static/6294c39db334256d9ea8ae53?token=) §3–6 | 공통 counter·PE별 comparator·CNTFRQ·virtual offset 개념 |
| H7 | [Arm AArch64 Programmer's Guide: Generic Timer](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/Generic%20Timer.pdf?revision=c710e7a7-9f52-4901-8c9d-91b19f44f9c7) §2–3, pp.6–9 | 웹 검색·본문·구성도 확인. System Counter의 count 배포와 per-core timer/comparator 구조를 `01-hardware`에 반영 |

Corstone 일반 문서의 power domain을 Zena에 그대로 적용하지 않았다. Zena의 TIMER0–3는 모두 PD_AON이며 reset domain만 갈린다. SoC 통합 계약에는 H2를 우선한다.

<a id="ap-hardware"></a>

## AP Domain Hardware Architecture 추가 근거

| 대상 | 근거 | 확인 내용 |
|---|---|---|
| System Counter | [Arm ARM D12.1.2](../../arm_architecture_reference_manual/3433-D12.1.2-The-system-counter.md), P2 | Counter 폭·입력 clock·실효 rate; Armv8.6 이후 1GHz 계약과 QVP 초기 125MHz 구분 |
| CPU timer bank / PPI | [Arm ARM D12.2.4](../../arm_architecture_reference_manual/3438-D12.2.4-Timers.md), P3·P7 | PE별 comparator·physical/virtual bank; 현재 AP Lua는 출력 4개 연결 |
| Frequency / control | [CNTFRQ_EL0](../../arm_architecture_reference_manual/5345-D24.10.1-CNTFRQ_EL0-Counter-timer-Frequency-Register.md), [CNTP_CTL_EL0](../../arm_architecture_reference_manual/5366-D24.10.22-CNTP_CTL_EL0-Counter-timer-Physical-Timer-Control-Register.md) | Frequency metadata, ENABLE/IMASK/ISTATUS |
| Deadline registers | [CNTP_CVAL_EL0](../../arm_architecture_reference_manual/5367-D24.10.23-CNTP_CVAL_EL0-Counter-timer-Physical-Timer-CompareValue-Register.md), [CNTP_TVAL_EL0](../../arm_architecture_reference_manual/5368-D24.10.24-CNTP_TVAL_EL0-Counter-timer-Physical-Timer-TimerValue-Register.md) | 64-bit compare와 32-bit signed relative value |
| MMIO architecture | H5의 CNTCTLBase·CNTBaseN 표 | 표준 offset·접근 제어·optional virtual/EL0 frame |
| MMIO model | [Register 정의](../../../hsoc-stack/tools/qemu/include/hw/timer/arm_arch_timer_mmio.h) 14–31행, M5 | CNTTID가 frame 수 반환, 0x00C frame ID, physical comparator, control 저장과 강제의 차이 |
| AP DT / IRQ | A1의 `timer@1a810000`, `timer` node; P3의 AP CPU/system Lua | NS frame0 SPI49; CPU PPI 4개 연결, DTS의 다섯 번째 PPI12/INTID28은 AP Lua 배선 없음 |

추가 챕터는 위 로컬 Arm 문서와 현재 Lua·DTS·QEMU 소스를 대조했다. Register readback·IRQ 발생 시험은 수행하지 않았다.

<a id="zena-system-counter"></a>

## Zena CSS System Counter HW 구조

| 근거 | 확인 내용 |
|---|---|
| [Zena programmer's model](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) SMD map, 293–294행 | REFCLK CNTControlBase·CNTRead 주소, 각 64KiB, Secure/APU gating과 부트 기본 RSE 접근 |
| [SCP timer 설정](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gtimer.c) 일반 platform 분기 | 그림의 REFCLK 125MHz 표기; FPGA 분기와 구분 |
| [Arm ARM D12.1.2](../../arm_architecture_reference_manual/3433-D12.1.2-The-system-counter.md), H5·H6 | 64-bit Counter, 입력 clock과 effective frequency의 차이, control/read 및 timer 소비 인터페이스 |

`01b-ap-counter`는 QBox 객체도를 대체한 HW 기능 블록도다. AP CPU-local/MMIO timer의 count 소비를 표시하며, 내부 배포 배선·pipeline·latency의 RTL 상세도는 아니다. 125MHz×8은 Arm architecture의 설명 예이며 FVP/QVP 실측값으로 사용하지 않는다.

<a id="si-hardware"></a>

## Safety Island Domain Hardware Architecture 추가 근거

2026-10-19에 SI CL0·CL1의 Lua 배선과 register handler를 대조했다. CPU 수는 현재 QVP 구성 기준이며, SW driver 상세는 기존 SCP·Zephyr 근거 절에서 별도로 다룬다.

| 대상 | 근거 | 확인 내용 |
|---|---|---|
| SI interrupt 계약 | [Zena programmer's model](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md), Table 9-38 | INTID20 CNTHPS, INTID27 CNTV, INTID29 CNTPS, INTID19 reserved, CL0 MMIO INTID34 |
| CPU timer 연결 | P4·P5·P6·P7 | CL0 ×1 / CL1 ×4, PPI27/20/19/29의 현재 source, CNTHPS index5 미노출과 CNTPS 접근 제약 |
| CL0 MMIO | [CL0 system Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua), [host_gtimer 정의](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/include/host_gtimer.h), M2 | CNTCTL 0x2A6F0000 / CNTBase 0x2A720000, frame별 64KiB, count·frequency·CVAL·CTL 처리, TVAL 저장만 수행 |
| CSS 접근 경로 | [SCP SI map](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h), P2·S2·S3 | SI ATW5의 CSS counter window, 공통 Counter의 초기값·제어·64-bit CNTINCR 쓰기 제약 |
| 만료 event | M2·M3·M4 | CL0 MMIO의 SystemC wait/rearm·IRQ level, CPU mirror snapshot과 QEMU timer 만료 |
| View·FMU | [Automotive Enhanced 근거](../interrupt/SOURCES.md#automotive-enhanced) | CL0 View1 / CL1 View2, INTID34의 View1 할당, 별도 QEMU GIC backend, SI GIC FMU·root FMU·SSU 연결 |

Timer 문서에는 SI HW·MMIO·Counter·QVP 및 AP HW·MMIO·Counter·QVP 다이어그램을 포함한다. AP Multiview·FMU와 SI Automotive Enhanced 도면은 Interrupt 문서로 이동했다. 각 SVG에 편집 가능한 diagram XML을 포함한다. SI PPI19/20 배선과 TRM의 차이는 본문 표에서 구분한다. 새 boot·IRQ·fault injection 시험은 수행하지 않았다.

<a id="timer-interrupt-flow"></a>

## Generic Timer interrupt Flow 근거

| 단계 | 소스 | 확인 내용 |
|---|---|---|
| 01–03 | H6·H7, P3 | Counter/comparator, CPU별 timer PPI와 AP GIC 연결 |
| 04–05·09 | [GICv3 driver](../../../hsoc-stack/components/primary_compute/linux/drivers/irqchip/irq-gic-v3.c) 719–750·846–878·904–925행 | IAR acknowledge, EOImode1의 early priority drop, mode별 deactivate |
| 05·09 | [per-CPU IRQ 처리](../../../hsoc-stack/components/primary_compute/linux/kernel/irq/chip.c) 897–929행 | Timer action 호출 뒤 irq_eoi 수행 |
| 06–08 | [Generic Timer driver](../../../hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c) 564–591·616–645행 | ISTATUS 확인·IMASK 설정, event_handler, CVAL/CTL rearm |

Flow는 EL1 virtual timer의 일반 Linux 경로를 설명한다. 현재 부팅에서의 timer 선택·EOImode·IRQ 발생은 측정하지 않았다.

<a id="reference"></a>

## Arm reference design · FVP 비교

| ID | 근거 | 확인 내용 / 범위 |
|---|---|---|
| F1 | [design/components.rst](../../../arm-zena-css/documentation/design/components.rst) 334–351행 | TF-A 제공 DT의 U-Boot/Linux 소비; U-Boot event-stream udelay |
| F2 | [power_and_performance_control.rst](../../../arm-zena-css/documentation/design/power_and_performance_control.rst) 80–101행 | timer wakeup의 SW power-management 맥락; QVP wakeup 실증은 아님 |
| F3 | [FVP 설명](../../arm_zena_css_dev_guide/08-fixed-virtual-platform.md) 20–58행 | Cfg1/Cfg2, A720AE/R82AE/M55, Cfg2 CL1의 물리 TRM 범위 차이 |
| F4 | [FVP machine include](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc) 16–18·54·67–70행 | FVP provider; RSE DISABLE_GATING; LCM NV counter persistence |
| F5 | [Apollo FVP machine](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-fvp.conf) 5–11행 | Arm RD-Aspen machine 설정 상속 |

F4의 NV counters는 보안 NVM counter이며 Generic Timer와 다르다. 조사한 machine conf/inc에서 timer frequency override는 찾지 못했다. FVP 실행 parameter dump·내부 clock 구현·IRQ 지연 비교는 하지 않았다.

<a id="platform"></a>

## Platform 조립 · CPU · IRQ · reset

| ID | 근거 | 확인 내용 |
|---|---|---|
| P1 | [canonical entry](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full-system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua) | 최종 Lua descriptor 평가의 진입점 |
| P2 | [CSS system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/system.lua) 13–14·65–114행 | 125MHz·increment1·CSS control/read/sync 생성 |
| P3 | [AP CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua) 1–75행, [AP system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) 142–179행 | A720AE, per-CPU PPI, AP frame 번호·주소·SPI·mirror |
| P4 | [CL0 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua) 1–62행, [CL0 system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua) 122–151행 | R82 timer outputs, 별도 CNTCTL storage/CNTBase 모델 |
| P5 | [CL1 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua) 1–74행 | R82 ×4와 CPU mirror/PPI |
| P6 | [R82 wrapper](../../../hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h) 63·118–121행, [QEMU R82](../../../hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c) 1720–1750행 | cortex-r82-arm, EL3 없음, wrapper 출력0–3 노출 |
| P7 | [timer indices](../../../hsoc-stack/tools/qemu/target/arm/gtimer.h) 12–20행, [CNTPS access](../../../hsoc-stack/tools/qemu/target/arm/helper.c) 1270·10517행 | SI CNTPS 접근 제한; CNTHPS index5는 wrapper 미노출 |
| P8 | [RSE CPU/LSC](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua) 23–68행, [RSE system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 119–191·287–329행 | LSC·TIMER0–3·SysTick·reset fanout |
| P9 | [PPC routing](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua) 310–347행, [LocalPass](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua) 117–129행 | S/NS alias, PPC policy, Container socket |
| P10 | [VP options](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua) 110–116행, [SoC defaults](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/config.lua) 22–25행 | full-system mirror=true, standalone 기본값과 구분 |
| P11 | [fabric reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) 13–55·71–134행, [NVIC wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h) 147–199·232–241행 | reset fanout 소비자; SysTick clock/reset |

<a id="models"></a>

## QBox / QEMU 구현

| ID | 근거 | 확인 내용 |
|---|---|---|
| M1 | [arm_system_counter.cc](../../../hsoc-stack/tools/qbox-platform/systemc-components/arm_system_counter/src/arm_system_counter.cc) 40–64·102–175·300–341행 | SystemC anchor, 64.24 상태, materialize, generation, reset |
| M2 | [host_gtimer.cc](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/src/host_gtimer.cc) 42–55·123–157·181–265·313–342행 | 32-bit CNTINCR, wide write no-op, CL0 TVAL 저장만, event wait, sync storage |
| M3 | [ARM mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_arm_counter_mirror/src/qemu_arm_counter_mirror.cc) 38–62·82–147행, [CPU wrapper](../../../hsoc-stack/tools/qbox/qemu-components/common/include/arm.h) 32행 | effective Hz 정수/범위 검사, state event publication, QEMU lock |
| M4 | [QEMU ARM helper](../../../hsoc-stack/tools/qemu/target/arm/helper.c) 1107·1349–1421·1549–1675행 | CNTFRQ와 mirror rate 분리; count 외삽; CVAL/TVAL; callback·IRQ·rearm |
| M5 | [AP MMIO timer](../../../hsoc-stack/tools/qemu/hw/timer/arm_arch_timer_mmio.c) 37–101·148–194·254–321·412행 | frame별 comparator, TVAL, IRQ, CNTACR 저장만, virtual compare 없음, reset |
| M6 | [SSE mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_sse_counter/src/qemu_sse_counter.cc) 20–44·113–134행, [SSE timer wrapper](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_sse_timer/src/qemu_sse_timer.cc) 39–52행 | LSC CLK/count snapshot, same-instance QOM counter link |
| M7 | [sse-counter.c](../../../hsoc-stack/tools/qemu/hw/timer/sse-counter.c) 114–174·213–279·390–402행 | 8.24 local scaling, HWCLKSW=0, debug halt 미구현, consumer notify |
| M8 | [sse-timer.c](../../../hsoc-stack/tools/qemu/hw/timer/sse-timer.c) 127–217·275–347·392행 | normal compare, AIVAL W0C, 현재 count 기준 rearm, disable/reset 경계 |
| M9 | [CPU initiator](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h) 133·798·828행, [NI bridge](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_ni710ae_nci/include/host_ni710ae_nci.h) 636행 | max access8, data_length 보존; SCP 8-byte store 경로 |
| M10 | [watchdog](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_watchdog/include/zena_watchdog.h) 54–63행, [PL031](../../../hsoc-stack/tools/qemu/hw/rtc/pl031.c) 62·198–204행, [RTC clock](../../../hsoc-stack/tools/qemu/system/rtc.c) 145행 | CSS와 독립적인 watchdog/RTC 시간 기준 |

현재 SSE AIVAL disable은 IRQ를 낮추지만 예약 event를 즉시 삭제하지 않는다. AIVAL callback은 ENABLE 재검사 없이 rearm할 수 있다. Reset은 event 삭제·register clear를 하지만 명시적 IRQ deassert가 없다. 이는 **M8 코드 경계**이며, 실제 reset 시 guest 장애를 재현했다는 주장은 아니다.

| 시간축 근거 | 확인 내용 |
|---|---|
| [runner defaults](../../../scripts/run/run_qbox_apollo_fvp_full.py) 163행, [VP quantum](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/qvp.lua) 8행 | quantum_keeper / freerunning; quantum=10ms |
| [QemuInstance](../../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h) 260·369·391행 | icount=false 기본; mcips time callback은 별도 선택 |
| [QEMU virtual clock](../../../hsoc-stack/tools/qemu/util/qemu-timer.c) 657행, [TCG clock](../../../hsoc-stack/tools/qemu/accel/tcg/tcg-accel-ops.c) 203행, [CPU clock](../../../hsoc-stack/tools/qemu/system/cpu-timers.c) 74–125행 | virtual clock → 비-icount host elapsed time |
| [CPU/QK 연결](../../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h) 400–466·705·1276·1388행, [freerunning QK](../../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h) 15행 | guest timer와 budget timer 구분; 10ms는 skew 상한 아님 |

<a id="software-overview"></a>

## Software Overview · Scheduler 연계

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| Linux tick | [tick-common.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/tick-common.c), [tick-sched.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/tick-sched.c), [timer.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/timer.c) `update_process_times()` | Tick 처리에서 accounting·local timer·`sched_tick()` 호출 |
| Linux sleep wakeup | [hrtimer.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/hrtimer.c) `hrtimer_wakeup()` | 만료된 sleep timer가 `wake_up_process()` 호출; 즉시 Task 실행·context switch 보장과 구분 |
| Zephyr timeout / time slice | [timeout.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeout.c) `sys_clock_announce()`, [sched.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/sched.c) | Timeout callback·다음 timeout 설정, 조건부 `z_time_slice()`, Ready 상태·reschedule 경로 |
| Timer driver와 Domain 차이 | [AP](#ap-software), [SCP](#scp), [Zephyr](#zephyr), [TF-M](#tfm) | OS timer와 SCP alarm·TF-M polling/시험의 적용 범위 구분 |

`08a-software-overview`는 별도 native draw.io 페이지이며 SVG에 편집 데이터를 포함한다. Linux·Zephyr의 공통 계층을 표현한 개념도로, 각 함수의 일대일 호출 graph 또는 runtime scheduling trace가 아니다. Scheduling latency·Job deadline 충족 여부는 측정하지 않았다.

<a id="ap-software"></a>

## AP Software

| ID | 근거 | 확인 내용 |
|---|---|---|
| A1 | [Apollo DTS](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi) 645·815행 | CPU timer와 MMIO timer node 분리 |
| A2 | [Linux arm_arch_timer.c](../../../hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c) 564·616·674·858·911·1012·1091행 | ISR mask, CVAL write, clocksource/clockevent 선택, per-CPU IRQ |
| A3 | [clockevents.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/clockevents.c) 303행, [tick-oneshot.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/tick-oneshot.c) 23·124행, [hrtimer.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/hrtimer.c) 1873행 | expiry→cycles, highres handler, callback·rearm |
| A4 | [tick-sched.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/tick-sched.c) 253·969·1051·1570행 | scheduler tick·NOHZ·next deadline |
| A5 | [TF-A platform_def.h](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/include/platform_def.h) 42·316행, [PSCI setup](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/lib/psci/psci_setup.c) 311행 | 125MHz metadata·CNTFRQ write |
| A6 | [TF-A BL31 setup](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_bl31_setup.c) 152행, [generic delay](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/delay_timer/generic_delay_timer.c) 40–65행 | CNTPCT 기반 polling delay |
| A7 | [U-Boot defconfig](../../../hsoc-stack/components/primary_compute/u-boot/configs/apollo_qvp_defconfig) 3행, [ARMv8 Kconfig](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/Kconfig) 202행, [generic_timer.c](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/generic_timer.c) 19·84·115·122행 | counter read·frequency; EL2 이상 event stream/WFE와 tail polling |
| A8 | [OP-TEE config](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-automotive_rd/conf.mk) 29·39행, [secure time](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/kernel/tee_time_arm_cntpct.c) 16–46행 | S-EL1 CNTPCT time 사용 |
| A9 | [OP-TEE generic timer](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/kernel/generic_timer.c) 10–63행, [automotive main](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-automotive_rd/main.c), [vexpress caller](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-vexpress/main.c) 311행 | callout capability와 Apollo 초기화 호출 부재 구분 |

<a id="ap-software-detail"></a>

## AP Software 상세 — Linux·TF-A·U-Boot

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| Linux 등록·선택 | A1·A2의 `arch_timer_of_init`, `arch_timer_select_ppi`, `arch_timer_register`, `arch_timer_starting_cpu`, `arch_counter_register` | DT 탐색, HYP/virtual/NS physical 선택, CPU별 IRQ와 clockevent, clocksource·sched_clock 등록 |
| Linux DT 초기화 도면 | [ARM64 time_init](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/time.c), A1·A2 | `08b-linux-dt-init`·`08b-linux-init-sequence`: timer_probe/TIMER_OF_DECLARE, positional IRQ mapping, CNTFRQ fallback, C3STOP, IRQ·CPUHP·clocksource 등록 순서; 최종 boot DT와 runtime 선택은 미검증 |
| Linux 만료 처리 | A2의 `set_next_event`, `timer_handler`, A3·A4, [Scheduler 연계](#software-overview) | CVAL/CTL 프로그램, ISTATUS·IMASK, event_handler, hrtimer wakeup와 scheduler tick |
| TF-A delay | A5·A6, [delay_timer.c](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/delay_timer/delay_timer.c) | BL31 delay ops 등록, PSCI CNTFRQ metadata, CNTPCT 기반 delay·timeout |
| U-Boot API | A7, [lib/time.c](../../../hsoc-stack/components/primary_compute/u-boot/lib/time.c) | get_timer·udelay 공통 계층, Counter/frequency read, 조건부 event stream 설정·WFE·복원·tail polling |

`08b-linux-software`·`08c-tfa-software`·`08d-uboot-software`는 각각 별도 native draw.io 페이지다. Linux 그림은 공통 책임·처리 경로를 나타내며 모든 Kernel 설정의 단일 호출 순서를 뜻하지 않는다. 최종 U-Boot `.config`, 부팅 EL, Linux timer 선택·highres/NOHZ 상태·timer IRQ 발생은 이번 문서 작업에서 실행 검증하지 않았다.

<a id="optee-software-detail"></a>

## OP-TEE Software 상세

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| Platform/time source | A8 | ARM64·CNTPCT source 강제 설정, S-EL1 SPMC 기본값, seconds/millis 환산 |
| TA API / syscall | [tee_api.c](../../../hsoc-stack/components/primary_compute/optee_os/lib/libutee/tee_api.c) `TEE_GetSystemTime`·`TEE_Wait`, [tee_svc.c](../../../hsoc-stack/components/primary_compute/optee_os/core/tee/tee_svc.c) `syscall_get_time`·`syscall_wait` | SYSTEM/REE/TA persistent time 분기, 시작 시간 유지·현재 시간 재조회, cancellation 우선 확인, TA wrapper의 오류별 panic 처리 |
| RPC wait | [tee_time.c](../../../hsoc-stack/components/primary_compute/optee_os/core/kernel/tee_time.c) `tee_time_wait` | OPTEE_RPC_CMD_SUSPEND 요청; Generic Timer callout과 다른 경로 |
| Callout driver / 빌드 | A9, [kernel/sub.mk](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/kernel/sub.mk), [callout.c](../../../hsoc-stack/components/primary_compute/optee_os/core/kernel/callout.c) | ARM64 빌드 포함, CNTPS/CNTP 분기, IRQ 등록·service 초기화, callback·다음 timeout |

`timer_init_callout_service`의 C/H 참조를 검색하여 선언·정의와 `plat-vexpress` 호출을 확인했다. `plat-automotive_rd`의 초기화 호출은 찾지 못했다. `08e-optee-software`는 확인된 시간 조회·RPC 경로와 초기화 미확인 callout HW를 실선·점선으로 구분한다. `08e-optee-time-sequence`는 SYSTEM time 조회·환산·사용자 복사를, `08e-optee-wait-sequence`는 cancellation·경과 시간 확인 및 RPC 반복 대기를 나타낸다. TA 실행·RPC wakeup·secure timer IRQ는 이번 작업에서 시험하지 않았다.

<a id="scp"></a>

## SI CL0 / SCP

| ID | 근거 | 확인 내용 |
|---|---|---|
| S1 | [SCP recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc) 5행, [base recipe](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware/scp-firmware-fvp-rd-aspen.inc) 141행, [variant](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/apollo_fvp_variant.cmake) 21행 | apollo-qvp / cfg2→fvp / non-RTL config 경로 |
| S2 | [Firmware.cmake](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake) 15·127행, [config_gtimer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gtimer.c) 21–66행 | aarch64, gtimer/timer modules, 125MHz·CNTINCR 요청값8 |
| S3 | [fwk_module.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_module.c) 352·399·434행, [mod_gtimer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c) 294–339·374행 | element start→control init; `uintptr_t` 64-bit store |
| S4 | [config_timer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_timer.c) 22행, [mod_gtimer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c) 32·59·83–165·385행 | INTID34, stable count read, CVAL 최소2000 ticks, frequency 환산 |
| S5 | [mod_timer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/timer/src/mod_timer.c) 78·151·175·252·468·534–575·701행 | alarm queue, polling delay, ISR callback, periodic rearm |
| S6 | [arch_exceptions.S](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.S) 160행, [arch_gic.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_gic.c) 77–109행 | FIQ·IAR0·ISR dispatch·EOIR0 |

S3의 **요청값8**과 모델의 **적용된 increment**는 다르다. AArch64 `uintptr_t` store→M9의 8-byte transport→M2의 wide implementation-defined write no-op이 현재 정적 경로다. `write32(CNTINCR,8)`을 별도로 수행했을 때의 1GHz 계산과 구분한다.

<a id="scp-software-detail"></a>

## SCP Software 상세 — Timer HAL · Alarm

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| Driver 초기화 | S2·S3·S4의 `gtimer_start`·`gtimer_control_init`·`set_timer` | Counter 초기화, 64-bit CNTINCR 쓰기, CVAL 최소 2000-tick 보정, count read |
| HAL/API·queue | S5의 `delay`·`wait`·`alarm_start`·`_insert_alarm_ctx_into_active_queue` | Polling API, ISR 문맥의 start 거부, deadline 정렬·queue head 프로그램 |
| ISR·periodic | S5의 `timer_start`·`timer_isr`, S6 | INTID34 등록, FIQ/IAR0 dispatch, disable·pending clear·callback 직접 호출, 이전 deadline 기반 재삽입·EOIR0 |
| Alarm ID 할당 | [si0_cfgd_timer.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_cfgd_timer.h), [config_timer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_timer.c) | Client용 sub-element ID와 조건부 구성; runtime 사용 증거와 구분 |

`08f-scp-software`는 CL0 계층 구조, `08f-scp-init`은 init/bind/start, `08f-scp-alarm-sequence`는 등록·FIQ·callback·rearm을 나타내는 별도 native draw.io 페이지다. Init의 gtimer → timer start 순서는 S2의 Firmware.cmake module 목록을 따른다. Polling API의 `delay`는 count >= deadline, `wait`는 count > deadline에서 조건을 재확인한다. Callback은 ISR 안에서 실행되며 event queue로 자동 이관되지 않는다는 소스 계약을 표시했다. Alarm 주입·FIQ 관찰·callback 지연 측정은 수행하지 않았다.

<a id="zephyr"></a>

## SI CL1 / Zephyr

| ID | 근거 | 확인 내용 |
|---|---|---|
| Z1 | [CL1 recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc) 5–11행, [board defconfig](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1_defconfig) 16–41행 | QVP board,125MHz,100 ticks/s,tickless,SMP4 |
| Z2 | [ARM64 timer.h](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/timer.h) 22–74행, [reset.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/reset.c) 33·146행 | CNTV virtual timer, CNTFRQ 초기화, CNTVOFF=0 |
| Z3 | [arm_arch_timer.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/timer/arm_arch_timer.c) 19·65–141·184–229행 | tickless CVAL, ISR mask, announce, busy wait, SMP timer init |
| Z4 | [timeout.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeout.c) 143·219–261행, [sched.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/sched.c) 611행 | timeout callback/rearm, thread wake |
| Z5 | [ISR wrapper](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/isr_wrapper.S) 62·105·143행, [GIC driver](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c) 285행 | ISR table·EOIR1·scheduler return |

<a id="zephyr-software-detail"></a>

## Zephyr Software 상세 — CL1 Timer / Scheduler

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| 초기화·HW | Z1·Z2·Z3·Z5 | 보드 설정, CNTV helper, PRE_KERNEL_2 초기화, secondary CPU timer, GIC dispatch |
| Timekeeping | [kernel.h](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/kernel.h), Z3·Z4 | uptime tick 환산, cycle 조회, elapsed tick·announce |
| Timer API | [timer.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timer.c) | start, periodic 재등록, status 갱신, ISR expiry callback |
| Sleep / Scheduler | Z4의 sched.c·timeout.c | z_tick_sleep, thread timeout 등록·context switch, 만료 처리·다음 timeout 설정 |

`08g-zephyr-software`·`08g-zephyr-init`·`08g-zephyr-timeout-sequence`는 CL1 전용 native draw.io 페이지다. 보드 기본값과 최종 build 설정을 구분하며 PPI 발생·callback 지연·SMP 실행은 검증하지 않았다.

<a id="tfm"></a>

## RSE / TF-M

| ID | 근거 | 확인 내용 |
|---|---|---|
| R1 | [SCMI HAL](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/scmi/scmi_hal.c) 229–252행 | BL2 count read,125MHz 환산값, comparator/IRQ 재설정 안 함 |
| R2 | [systimer driver](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/drivers/timer/armv8m/systimer_armv8-m_drv.c) 63–150·248–279행 | high-low-high read, CNTFRQ metadata, AIVAL W0C |
| R3 | [TF-M interrupt](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/tfm_interrupts.c) 29–46행, [test hook](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/plat_test.c) 13–32행 | TIMER0→SPM; AIVAL test start/clear/stop |
| R4 | [common CMake](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/CMakeLists.txt) 254–256행, [Apollo config](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/config.cmake) 25행 | test hook 조건; APOLLO_TIMER_TEST 기본 OFF |
| R5 | [timer self-test](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/timer_self_test.c) 21·43–79행, [startup](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/startup_rse.c) 85·173행 | SysTick100MHz polling 시험; 기본 weak handler |
| R6 | [device_cfg.h](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/config/device_cfg.h) 94행 | generic test timer default32MHz는 QVP 실제 rate의 증거가 아님 |

<a id="validation"></a>

## Timer 관찰 도구

[apollo_timer_snapshot](../../../hsoc-stack/tools/qbox-platform/qemu-components/apollo_timer_snapshot/src/apollo_timer_snapshot.cc)은 capture 전에 mirror `synchronize()`를 호출한다. 결과의 counter equality는 독립 guest 동시-read나 자연 drift 측정값이 아니다.

[FVP probe](../../../scripts/test/probe_rse_timers_iris.py)와 [QVP probe](../../../scripts/test/probe_rse_timers_gdb.py)는 register·pending 상태 관찰 도구다. Firmware API·ISR 시험 결과와 구분한다.

<a id="rse-hardware"></a>

## RSE Domain Hardware Architecture 추가 근거

2026-10-19 정적 조사. Zena 통합 사양을 주소·IRQ·power/reset의 기준으로 사용하고, Corstone Timer IP 및 M55 SysTick 계약과 Apollo 모델 구현을 구분했다.

| 대상 | 근거 | 확인 내용 |
|---|---|---|
| Zena RSE 주소·IRQ | [Zena programmer’s model](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md), RSE Peripheral/AON map 및 Table 9-36 | TIMER0–3 S/NS alias, LSC Control/Read, SOC_TIMER0/1, SLOWCLK Timer; IRQn2/3/4/5/27/59/60 |
| Zena LSC·reset | 같은 문서 §9.4.3·9.4.9 | LSC→TIMER0–3 CNTVALUEB; TIMER0–3 모두 PD_AON; TIMER0–2 SYS/RSS reset, TIMER3·SOC_TIMER0/1 AON reset |
| 접근 보호 | 같은 문서 PERIPHNSPPC0·PERIPHSPPPC0·PERIPHNSPPPC0와 expansion PPC 표 | TIMER0–3 security/privilege bit 0/1/2/5; LSC Control S_PPC / Read S 주소 속성 |
| Timestamp IP | [Timestamp timers](../../corstone-reference-system-architecture/0071-Timestamp-based-timers.md), [Timer operation](../../corstone-reference-system-architecture/0241-System-Timer-operation.md), [AIVAL control](../../corstone-reference-system-architecture/0252-CNTP_AIVAL_CTL-AutoIncrValue-Control-register.md) | 64-bit timestamp, CVAL/TVAL, AIVAL reload, CLR write-zero-clear; 일반 Corstone power map은 Zena에 그대로 적용하지 않음 |
| LSC IP | [Counter overview](../../corstone-reference-system-architecture/0228-System-Counter-overview.md), [Control register summary](../../corstone-reference-system-architecture/0231-CNTControlBase-registers-summary.md), [Read register summary](../../corstone-reference-system-architecture/0232-CNTReadBase-registers-summary.md), [Scaling](../../corstone-reference-system-architecture/0239-CNTSCR0-CNTSCR1-Counter-Scaling-registers.md) | 64-bit count·fractional scaling, CNTCR/CNTCV/CNTSCR; HW clock 입력과 QVP mirror 구분 |
| SysTick | [Arm Cortex-M55 Devices Generic User Guide](https://documentation-service.arm.com/static/6622c155fabc8c11c7b534b4), [Arm Cortex-M55 product support](https://support.arm.com/compute-ip/cortex-m55), [NVIC wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h) | 24-bit down-counter, S/NS SysTick, 내부 exception; QVP CPU clock 100MHz |
| SLOWCLK Timer | [SLOWCLK AON Timers](../../corstone-reference-system-architecture/0072-SLOWCLK-AON-Timers.md), [CMSDK timer register 구현](../../../hsoc-stack/tools/qemu/hw/timer/cmsdk-apb-timer.c) | 32-bit counter·AON clock/reset·CTRL/VALUE/RELOAD/INTSTATUS; 모델 소스 존재가 Apollo instance 활성화를 의미하지 않음 |
| QVP 구성 | [RSE CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua), [RSE system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua), [PPC](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua), [LocalPass](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua) | instance, timer IRQ, LSC clock/mirror, S/NS routing, reset fanout |
| QVP Timer backend | [SSE counter](../../../hsoc-stack/tools/qemu/hw/timer/sse-counter.c), [SSE timer](../../../hsoc-stack/tools/qemu/hw/timer/sse-timer.c), [Counter mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_sse_counter/src/qemu_sse_counter.cc) | count/clock publication, register map, AIVAL event와 reset 제약 |

`01rse-a-hardware`부터 `01rse-e-qvp`까지 5장의 전용 draw.io 도면을 추가했다. SOC_TIMER0/1의 timestamp 입력과 실물 LSC clock 주파수는 확정하지 않았다. Apollo Lua에서 SOC_TIMER0/1·SLOWCLK Timer의 전용 instance·배선을 확인하지 못했으며, 새 부팅·IRQ·AIVAL·reset·저전력 wake 시험은 수행하지 않았다.

<a id="linux-timekeeping"></a>

## Linux Timekeeping API 근거

| 소스 | 확인 내용 |
|---|---|
| [posix-timers.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/posix-timers.c) | clock_gettime syscall, clockid별 연산, monotonic/realtime 조회와 사용자 공간 반환 |
| [timekeeping.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/timekeeping.c) | ktime_get/ktime_get_ts64, clocksource read, cycle 차이·mult/shift 환산, seqcount retry |
| [timekeeping.h](../../../hsoc-stack/components/primary_compute/linux/include/linux/timekeeping.h) | monotonic/realtime/boottime/raw API 구분 |
| [arm_arch_timer.c](../../../hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c) | arch_counter_register의 CNTPCT/CNTVCT 함수 선택과 clocksource 등록 |
| [ARM64 vDSO](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/include/asm/vdso/gettimeofday.h), [공통 vDSO](../../../hsoc-stack/components/primary_compute/linux/lib/vdso/gettimeofday.c) | CNTVCT 직접 조회, 공유 시간 정보·sequence 검사, syscall fallback |

`08b-linux-timekeeping`과 `08b-linux-vdso-layers`는 syscall 성공 경로와 vDSO 대안, 사용자 공간 실행과 Kernel의 공유 시간 정보 제공을 구분한다. 실제 vDSO 사용 여부, 시간 보정 상태, QVP 시간 정확도는 이번에 측정하지 않았다.

<a id="linux-timer-api"></a>

## Linux Timer / Sleep API 근거

| 소스 | 확인 내용 |
|---|---|
| [posix-timers.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/posix-timers.c) | clock_nanosleep syscall·clock별 nsleep, POSIX timer 연산 |
| [hrtimer.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/hrtimer.c) | hrtimer_nanosleep/do_nanosleep, Task 상태 설정·queue 등록·schedule 순서, hrtimer_interrupt, hrtimer_wakeup/wake_up_process |
| [tick-oneshot.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/tick-oneshot.c), [clockevents.c](../../../hsoc-stack/components/primary_compute/linux/kernel/time/clockevents.c) | tick_program_event, clockevents_program_event, 시간 간격→cycle 환산·set_next_event |
| [arm_arch_timer.c](../../../hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c) | CVAL/CTL 설정, ISTATUS·mask, event_handler 호출 |
| [timerfd.c](../../../hsoc-stack/components/primary_compute/linux/fs/timerfd.c) | timerfd_tmrproc/timerfd_triggered, 만료 횟수·wait queue·EPOLLIN 통보 |

`08b-linux-timer-api`와 `08b-linux-timer-api-sequence`는 Highres·CPU-local timer와 정상 sleep 만료를 대표한다. Lowres·alarm clock·CPU-time timer·signal 중단 경로를 전체 구현으로 확장 해석하지 않는다. 실제 timer 선택·callback 문맥·wakeup latency는 측정하지 않았다.

<a id="tfa-timer-detail"></a>

## TF-A Timer Architecture 상세 근거

| 소스 | 확인 내용 |
|---|---|
| [Apollo BL31 setup](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_bl31_setup.c) | bl31_platform_setup의 generic_delay_timer_init 호출 |
| [Apollo platform](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_plat.c), [platform_def.h](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/include/platform_def.h) | plat_get_syscnt_freq2 → SYS_COUNTER_FREQ_IN_TICKS=125000000 |
| [Generic delay timer](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/delay_timer/generic_delay_timer.c) | mult/div 축약·ops 등록, ~CNTPCT low32, CNTFRQ 기반 timeout 변환·strict greater-than 비교 |
| [Delay framework](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/delay_timer/delay_timer.c), [API header](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/include/drivers/delay_timer.h) | udelay/mdelay busy wait, rounding+1 tick, 범위 assert, timeout callback dispatch |
| [PSCI setup](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/lib/psci/psci_setup.c) | psci_arch_setup의 CNTFRQ write; ops 초기화와 별도 CPU 설정 |

`08c-tfa-software`는 계층도로 재작성했고, `08c-tfa-init`·`08c-tfa-delay-sequence`를 추가했다. 이 경로에 Timer comparator·IRQ 예약이 없다는 정적 확인이며, TF-A 전체의 interrupt 미사용을 주장하지 않는다. 실제 부팅·delay/timeout 시간 정확도는 측정하지 않았다.

<a id="uboot-timer-detail"></a>

## U-Boot Timer Architecture 상세 근거

| 소스 | 확인 내용 |
|---|---|
| [Apollo defconfig](../../../hsoc-stack/components/primary_compute/u-boot/configs/apollo_qvp_defconfig), [ARMv8 Kconfig](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/Kconfig), [ARMv8 Makefile](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/Makefile) | VEXPRESS64 선택, event-stream 기본 y, SYS_ARCH_TIMER의 generic_timer.o 선택 |
| [board_f.c](../../../hsoc-stack/components/primary_compute/u-boot/common/board_f.c), [start.S](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/start.S) | timer_init 호출·조건부 highest-EL CNTFRQ 설정 |
| [generic_timer.c](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/cpu/armv8/generic_timer.c) | CNTPCT/CNTFRQ, frequency workaround, timer_get_boot_us, CNTHCTL 저장·event enable·WFE·복원·tail polling |
| [lib/time.c](../../../hsoc-stack/components/primary_compute/u-boot/lib/time.c) | weak timer_init, 시간 환산, usec_to_tick, udelay 구간 분할, weak polling·UTHREAD 분기 |
| [cyclic.c](../../../hsoc-stack/components/primary_compute/u-boot/common/cyclic.c) | schedule의 watchdog·cyclic·uthread 서비스; Linux Scheduler와 구분 |

`08d-uboot-software`를 계층도로 재작성하고 `08d-uboot-init`·`08d-uboot-delay-sequence`를 추가했다. 소스·defconfig/Kconfig 기본값을 설명하며 최종 빌드 설정·실행 EL·WFE/event 발생·지연 시간 정확도는 이번에 측정하지 않았다.

<a id="tfm-software-detail"></a>

## TF-M Software 상세 — RSE Timer / SPM

| 대상 | 소스 | 확인 내용 |
|---|---|---|
| BL2 timeout | R1, [scmi_comms.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/scmi_comms.c) `transport_exchange` | 125MHz 환산·elapsed subtraction·doorbell polling |
| Driver / init | R2·R3·R4·R6 | 안정된 64-bit read, metadata 설정, AIVAL 제어, NVIC disable 초기화, 조건부 test hook |
| SPM dispatch | [interrupt.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/spm/core/interrupt.c) `spm_handle_interrupt` | SLIH/FLIH 분기, signal 및 backend별 scheduling |
| IRQ 완료 | [psa_irq_api.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/spm/core/psa_irq_api.c) `tfm_spm_partition_psa_eoi` | SLIH signal 해제·pending clear·IRQ enable; source clear와 별도 |
| Self-test | R5, Apollo config.cmake | 기본 OFF, SysTick COUNTFLAG polling, TIMER0–3 ISTATUS/NVIC pending 관찰; ISR 시험과 구분 |

`08h-tfm-software`·`08h-tfm-poll-sequence`·`08h-tfm-test-sequence`는 RSE 전용 native draw.io 페이지다. BL2와 조건부 Secure test 경로를 구분한다. 실제 test 활성화·IRQ·주기는 미검증이다.

## QVP 구현 Sequence 보강

- `03a-counter-propagation`: [CPU/AP MMIO mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_arm_counter_mirror/src/qemu_arm_counter_mirror.cc)의 초기 publish·state_changed_event·snapshot_at·target 전달 경로.
- `03b-timer-expiry`: [host_gtimer](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/src/host_gtimer.cc)의 IRQ 갱신·wait/rearm과 [QEMU ARM helper](../../../hsoc-stack/tools/qemu/target/arm/helper.c)의 `gt_recalc_timer`·QEMUTimer 예약 경로 비교.
- `06-mmio-frames`는 2장 HW 요약으로 이동했다. 새 도면은 정적 구현 설명이며 runtime 동기화·IRQ latency 검증 결과가 아니다.

## Domain SW 검증 항목의 실행 경로

- TF-A·U-Boot: 각 Software 상세 절의 init·delay·time API symbol을 기존 AP 실행에서 관찰한다.
- SCP: [debugger_cli](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/debugger_cli/src/mod_debugger_cli.c)의 periodic `alarm_callback`·Ctrl-E event 경로.
- Zephyr: [uptime shell](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/subsys/shell/modules/kernel_service/uptime.c), Z3의 driver init·ISR·SMP 초기화.
- TF-M: R5의 firmware self-test와 [stage validator](../../../scripts/test/validate_tfm_timer_stages.py). Validator 단위 시험의 synthetic log를 실제 firmware PASS로 사용하지 않는다.

- U-Boot console 시험: [cmd/sleep.c](../../../hsoc-stack/components/primary_compute/u-boot/cmd/sleep.c)의 `get_timer`·`udelay(100)` 반복.
- Zephyr shell 전제: [kernel_service/Kconfig](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/subsys/shell/modules/kernel_service/Kconfig)의 `CONFIG_KERNEL_SHELL`.

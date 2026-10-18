# Timer Architecture — 근거와 검증 범위

[세미나 문서](README.md) · [Timer / Counter Map](TIMER-MAP.md) · [draw.io 원본](apollo-timer-architecture.drawio)

## 조사 기준

2026-10-16의 checkout과 canonical `apollo-qvp-saturn-v.lua` full-system 구성을 확인했다. `build/conf/local.conf`에는 `MACHINE ??= "apollo-qvp"`, `RD_ASPEN_VARIANT = "cfg2"`, `PC_CPUS_COUNT_DEFAULT ??= "4"`, `TMPDIR = "${TOPDIR}/tmp_baremetal"`가 있다. BitBake를 실행해 최종 변수·산출물 설정을 다시 평가하지 않았다.

문서의 근거 수준은 **설계 계약 / 현재 구현 / 선택된 정적 구성 / 실행 증거**로 구분한다. 앞의 세 수준을 조사했으며 이번 작업의 runtime PASS 주장은 없다. 행 번호는 조사 시점의 위치이며 파일 링크는 repository 상대 경로다.

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

Corstone 일반 문서의 power domain을 Zena에 그대로 적용하지 않았다. Zena의 TIMER0–3는 모두 PD_AON이며 reset domain만 갈린다. SoC 통합 계약에는 H2를 우선한다.

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

<a id="zephyr"></a>

## SI CL1 / Zephyr

| ID | 근거 | 확인 내용 |
|---|---|---|
| Z1 | [CL1 recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc) 5–11행, [board defconfig](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1_defconfig) 16–41행 | QVP board,125MHz,100 ticks/s,tickless,SMP4 |
| Z2 | [ARM64 timer.h](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/timer.h) 22–74행, [reset.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/reset.c) 33·146행 | CNTV virtual timer, CNTFRQ 초기화, CNTVOFF=0 |
| Z3 | [arm_arch_timer.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/timer/arm_arch_timer.c) 19·65–141·184–229행 | tickless CVAL, ISR mask, announce, busy wait, SMP timer init |
| Z4 | [timeout.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeout.c) 143·219–261행, [sched.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/sched.c) 611행 | timeout callback/rearm, thread wake |
| Z5 | [ISR wrapper](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/isr_wrapper.S) 62·105·143행, [GIC driver](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c) 285행 | ISR table·EOIR1·scheduler return |

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

## 검증 결과와 한계

| 검증 | 결과 |
|---|---|
| draw.io 원본 | 11 pages, 408 mxCells. White theme, native image shape 없음 |
| 편집 가능한 SVG | 11개 export 성공. embedded XML과 원본 도형·연결 구조 일치 |
| 실제 렌더링 | draw.io Desktop에서 11개 page를 PNG로 export하고 전부 육안 확인. Chrome에서 SVG 11개 렌더링 및 크기 확인; frequency·Linux·SI sequence 추가 육안 확인 |
| Markdown 참조 | 로컬 링크 189개, 누락 0개. 줄 끝 공백 0개 |
| Diagram validator | strict 검사 13개 record, hard failure 0개. 원본 book의 두 링크는 자동 검사에서 viewer-required이며, 위 Desktop 렌더링·육안 확인으로 별도 검증 |
| 소스 대조 | CPU 종류·PPI/SPI, CNTINCR 쓰기 폭, counter mirror, SSE AIVAL/reset, subsystem ISR 순서와 소비 경로 확인 |

실행 검증은 수행하지 않았다: boot 후 CNTFRQ/CNTINCR, 선택된 Linux timer, IRQ count, deadline 지연, drift, reset·idle wakeup, FVP 동등성. 소스의 known gap을 문서에 반영했으며 소스 수정이나 firmware rebuild는 하지 않았다.

[apollo_timer_snapshot](../../../hsoc-stack/tools/qbox-platform/qemu-components/apollo_timer_snapshot/src/apollo_timer_snapshot.cc) 172·227·264행은 capture 전에 mirror `synchronize()`를 호출한다. 결과의 counter equality는 독립 guest 동시-read/자연 drift 측정이 아니다. 기존 [FVP probe](../../../scripts/test/probe_rse_timers_iris.py), [QVP probe](../../../scripts/test/probe_rse_timers_gdb.py)는 후속 실행 도구이며 이번에 실행하지 않았다.

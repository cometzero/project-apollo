# Apollo QVP Timer / Counter Map

[세미나 문서로 돌아가기](README.md)

## 범위와 읽는 법

canonical full-system Lua의 **최종 descriptor를 정적으로 평가한 구성 지도**다. AP 4 CPU, SI CL0 1 CPU, CL1 4 CPU와 기본 RSE CSS mirror를 기준으로 한다. 빌드·부팅·timer IRQ 주입을 수행하지 않았으며, 실제 guest ISR 실행이나 boot 후 register 값을 입증하지 않는다.

| 표기 | 의미 |
|---|---|
| `platform.` 생략 | 아래 객체의 공통 CCI 접두사 |
| CPU generic timer | CPU system register로 접근하는 comparator; 별도 MMIO frame와 구분 |
| CSS counter control | 공유 counter의 상태·rate를 제어하는 frame |
| timer CNTCTL | MMIO timer frame의 접근·구성을 관리하는 frame; CSS counter control과 다름 |
| PPI 번호 | architectural INTID; DTS `GIC_PPI` offset은 INTID−16 |
| SPI 번호 | socket offset; architectural INTID=socket+32 |
| RSE IRQn | NVIC external 번호; exception vector=IRQn+16, GIC INTID 아님 |

구성 근거: [canonical entry](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full-system profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua), [RSE options](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua) 110–116행. standalone `soc/config.lua`의 mirror=false와 full-system 기본 true를 혼동하지 않는다.

## 공유 counter와 실제 rate

`css_system_counter`는 SystemC 객체다. AP CPU·AP MMIO timer·CL0 CPU 및 MMIO timer·CL1 CPU·기본 RSE LSC가 이 source를 참조한다. QEMU timer는 각자의 QemuInstance 안에 있으며 mirror가 count/running/rate를 전달한다.

| 구분 | 초기 구성 | 변경 의미 |
|---|---|---|
| 입력 주파수 | 125 MHz | CSS source의 `input_frequency_hz` |
| 증가량 | integer increment=1 | 8.24 증가량으로 count 진행률 결정 |
| 실효 rate | 초기 125 MHz | input × increment_8_24 ÷ 2²⁴ |
| 보고 주파수 | CSS reported frequency=125 MHz | 실효 rate와 별도 상태 |
| CPU CNTFRQ / AP MMIO cntfrq | 초기 125 MHz | mirror의 실효 rate 변경과 별개 |
| CNTINCR 32-bit write | 값8 | 모델이 증가량8을 적용하면 실효1 GHz |
| 현재 SCP 일반 분기 | CNTINCR 값8, `uintptr_t` store | AArch64 64-bit 요청; 아래 no-op 경로와 구분 |

현재 SCP 일반 분기의 설정값은 REFCLK=125 MHz, CNTINCR=8이지만 `gtimer_control_init()`은 `volatile uintptr_t *`로 저장한다. 현재 QBox 경로는 AArch64의 8-byte 요청을 보존하며, `host_gtimer`는 control offset0xC0–0xF8의 정렬된 8-byte write를 **OK 응답 후 no-op**으로 처리한다. 따라서 이 SCP 경로를 32-bit CNTINCR write와 동일시하여 1 GHz 전환으로 설명하면 안 된다. 실제 boot의 최종 register 값은 미측정이다. [ABI·transport 근거 M9/S3](SOURCES.md#models).

근거: [SCP gtimer driver](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c) 294–312행, [host_gtimer access](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/src/host_gtimer.cc) 55–64·330–334행.

CPU mirror setter는 anchor/count/running/frequency/generation을 갱신하고 timer를 재계산한다. CPU CNTFRQ register는 이 함수에서 쓰지 않는다. AP MMIO mirror 역시 `mirror_frequency_hz`를 변경하며 `cntfrq`와 구분한다.

근거: [CSS 초기값](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/system.lua) 13–14·65–73행, [SCP config_gtimer](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gtimer.c) 21–59행, [CPU mirror setter](../../../hsoc-stack/tools/qemu/target/arm/helper.c) 1403–1421행, [MMIO mirror setter](../../../hsoc-stack/tools/qemu/hw/timer/arm_arch_timer_mmio.c) 86–101행.

## CPU system-register timer · PPI

각 CPU의 timer comparator와 PPI 입력은 독립적이다. counter source 공유가 comparator나 interrupt pending 상태 공유를 뜻하지 않는다.

| Domain / CPU | QemuInstance | secure / physical / virtual / hypervisor PPI INTID | DTS PPI offset |
|---|---|---|---|
| `ap_cpu_0..3` | `ap_qemu_inst` | 29 / 30 / 27 / 26 | 13 / 14 / 11 / 10 |
| `si_cl0_cpu_0` | `si_cl0_qemu_inst` | 29 / 20 / 27 / 19 | 13 / 4 / 11 / 3 |
| `si_cl1_cpu_0..3` | `si_cl1_qemu_inst` | 29 / 20 / 27 / 19 | 13 / 4 / 11 / 3 |

SI의 Cortex-R82 wrapper는 QEMU timer 출력 index0–3을 배선한다. 위 표의 secure29는 핀 이름이며, EL3 없는 현재 R82 guest에서 `CNTPS_*` 정상 접근은 불가하다. `CNTHPS_*` comparator는 별도 index5에 구현되지만 wrapper가 노출하지 않아 PPI20의 source가 아니다.

근거: [R82 wrapper](../../../hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h) 63·118–121행, [QEMU timer index](../../../hsoc-stack/tools/qemu/target/arm/gtimer.h) 12–19행, [접근 조건](../../../hsoc-stack/tools/qemu/target/arm/helper.c) 1270–1337행.

`ap_cpu_counter_mirror_N`, `si_cl0_cpu_counter_mirror`, `si_cl1_cpu_counter_mirror_N`가 각 CPU와 CSS counter를 연결한다. CL1 전용 MMIO timer object는 현재 구성에 없다.

근거: [AP CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua) 1–6·25–75행, [CL0 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua) 28–62행, [CL1 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua) 1–8·28–74행.

SI TRM [Table 9-38 전사본](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 1645–1655행은 INTID16–19를 reserved, INTID20을 CNTHPSIRQ로 기재한다. 현재 SI 모델의 hyp19 / phys20 배선·라벨을 하드웨어와 일치한다고 표현하면 안 된다.

## CSS · AP · CL0 MMIO frames

| 객체 / 역할 | 주소 · 크기 | model / owner | IRQ · 연결 |
|---|---|---|---|
| `css_system_counter` | 직접 MMIO 없음 | SystemC `arm_system_counter` | 공유 상태 source; 자체 IRQ 없음 |
| `host_css_counters_timers` | SMD physical 0x20000D0100000 · 64 KiB | SystemC `host_gtimer`, counter_control | CSS control |
| `host_css_counters_timers_read` | 0x20000D0110000 · 64 KiB | SystemC `host_gtimer`, counter_read | CSS count read |
| `host_css_counters_timers_sync` | 0x20000D0120000 · 64 KiB | SystemC `host_gtimer`, sync_frame | IRQ bind 없음 |
| `ap_timer_mem` CNTCTL | 0x1A810000 · 64 KiB | `qemu_arm_arch_timer_mmio` / `ap_qemu_inst` | frame0·1 관리 |
| AP secure frame1 | 0x1A820000 · 64 KiB | 같은 `ap_timer_mem` | irq_1 → AP SPI48 → INTID80 |
| AP nonsecure frame0 | 0x1A830000 · 64 KiB | 같은 `ap_timer_mem` | irq_0 → AP SPI49 → INTID81 |
| `si_cl0_timer_cntctl` | 0x2A6F0000 · 64 KiB | SystemC `host_gtimer` | timer CNTCTL; IRQ 없음 |
| `si_cl0_timer_cntbase` | 0x2A720000 · 64 KiB | SystemC `host_gtimer`, counter_base | CL0 SPI2 → INTID34 |

AP MMIO의 frame 번호와 주소 순서는 반대다: 낮은 주소가 frame1(S), 높은 주소가 frame0(NS)이다. `ap_timer_counter_mirror`가 CSS 상태를 AP MMIO model로 전달한다.

CSS의 표기 주소는 SMD physical 주소다. SCP는 SI ATW5 window를 거쳐 CSS control/read에 접근하므로 이 주소를 그대로 SI local address로 사용하면 안 된다. CL0의 CNTCTL 0x2A6F0000은 CSS control frame의 다른 이름이 아니다.

근거: [CSS frames](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/system.lua) 75–114행, [AP MMIO frames](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) 142–179행, [CL0 MMIO frames](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua) 37–42·123–151행, [SCP address mapping](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h) 106·205행.

## RSE LSC · SSE TIMER0–3

모든 SSE timer는 `rse_cpu_pass.qemu_inst`에 속한다. 아래 S/NS 주소는 각각 같은 timer로 이어지는 PPC 접근 경로이며 timer를 두 개씩 생성하는 것이 아니다.

| 객체 / frame | Secure 주소 | Nonsecure 주소 | IRQ / 연결 |
|---|---:|---:|---|
| LSC control | 0x5015A000 | 별도 alias 미기재 | Container target_socket0 → LocalPass → counter.control |
| LSC status | 0x5015B000 | 별도 alias 미기재 | Container target_socket1 → LocalPass → counter.status |
| `rse_timer_0` | 0x58000000 | 0x48000000 | NVIC IRQ3; PPC policy mask1 |
| `rse_timer_1` | 0x58001000 | 0x48001000 | NVIC IRQ4; PPC policy mask2 |
| `rse_timer_2` | 0x58002000 | 0x48002000 | NVIC IRQ5; PPC policy mask4 |
| `rse_timer_3` | 0x58003000 | 0x48003000 | NVIC IRQ27; PPC policy mask32 |

각 MMIO 창은 4 KiB다. TIMER0–3의 `qemu_sse_timer`는 모두 `rse_lsc_counter`를 link한다. timer MMIO는 PPC → Container target_socket2..5 → LocalPass → timer.socket을 통과한다.

| RSE 선택 | source / 주파수 |
|---|---|
| 기본 mirror=true | `qemu_sse_counter_mirror` → CSS shared source; 초기 LSC clock125 MHz |
| mirror state 변경 | clock source에 CSS effective rate 전달 + SSE count/running snapshot 갱신 |
| mirror=false 대안 | local `arm_system_counter`; `RSE_LSC_INPUT_HZ`, increment1, enabled=true |

mirror=true에서는 환경변수 `QBOX_APOLLO_RSE_LSC_INPUT_HZ` 대신 초기125 MHz를 사용한다. 이후 CSS effective rate 변화가 RSE LSC clock으로 전달될 수 있다.

근거: [LSC control/status](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua) 2–4·23–40행, [LocalPass](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua) 117–129행, [SSE counter/timers](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 119–191행, [PPC routing](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua) 310–347행, [SSE mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_sse_counter/src/qemu_sse_counter.cc) 113–134행.

## SysTick · watchdog · RTC 경계

이들은 CSS counter의 comparator 목록에 합치지 않는다.

| 모델 | 주소 / 시간 기준 | IRQ · 주의 |
|---|---|---|
| RSE S/NS SysTick | SCS 0xE000E000의 offset0x10; cpuclk100 MHz | NVIC systick-trigger0/1; external IRQn 아님 |
| AP NS watchdog | control/refresh 0x1A420000 / 0x1A430000;125 MHz | WS0 AP82; WS1 AP83 + CL0 321 |
| AP secure watchdog | 0x1A460000 / 0x1A470000;125 MHz | WS0 AP79; WS1 host reset controller |
| CL0 watchdog | 0x2A700000 / 0x2A710000;125 MHz | WS0 CL0 37; WS1 host reset controller |
| RSE NS watchdog | 0x48040000 / 0x48041000;32 MHz | WS0 IRQ1; WS1 IRQ0, UART와 직접 공유 |
| RSE secure watchdog | 0x58040000 / 0x58041000;32 MHz | WS0·WS1 bind 없음 |
| AP PL031 RTC | 0x300D0000; QEMU rtc_clock, 1초 단위 | AP SPI268 → INTID300; CSS mirror 아님 |

SysTick은 외부 refclk가 연결되지 않아 QEMU가 cpuclk를 선택한다. watchdog은 `sc_time_stamp × clock_frequency`로 자체 count를 계산하므로 CSS CNTINCR 변경이 rate를 바꾸지 않는다. RTC의 QEMU 기본 clock은 HOST이며 실행 옵션 변경 여부를 별도로 확인해야 한다.

근거: [RSE SysTick](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua) 61–68행, [SysTick wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h) 147–199행, [watchdog clock](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_watchdog/include/zena_watchdog.h) 54–63행, [RTC 구성](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua), [PL031](../../../hsoc-stack/tools/qemu/hw/rtc/pl031.c) 198–204행, [RTC clock 기본값](../../../hsoc-stack/tools/qemu/system/rtc.c) 145행.

## Reset · retention의 확인 범위

| 경로 | 명시된 timer 관련 대상 | 한계 |
|---|---|---|
| AP cold reset | AP S/NS watchdog을 먼저 reset, 이후 AP reset GPIO | CSS counter/AP MMIO/RTC의 명시적 reset bind는 이 목록에 없음 |
| Apollo system reset | RSE S/NS watchdog, CL0 watchdog, RSE SYS/RSS, SI QemuInstance | SystemC CSS counter 자체 reset bind 없음 |
| RSE SYS/RSS fanout | CPU/NVIC와 TIMER0·1·2 | TIMER3 제외 |
| RSE AON fanout | TIMER3; mirror=false이면 local counter도 포함 | canonical Lua에서 fanout reset_in의 source bind 미확인 |
| NVIC cold reset | NVIC와 S/NS SysTick | SSE LSC/TIMER reset과 별도 |

reset wire가 없다는 정적 사실은 모든 CPU/instance reset에서 상태 유지가 검증됐다는 뜻이 아니다. 특히 AON fanout의 존재만으로 TIMER3 AON reset 실행을 주장할 수 없다.

근거: [fabric reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) 13–55·71–134행, [RSE reset domains](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 287–329행, [NVIC cold_reset](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h) 232–237행.

## Mirror 구현의 제한

mirror는 서로 다른 QemuInstance에 상태를 전달한다. source 변경 시 publish하고 각 QEMU는 자신의 virtual clock에서 anchor 이후 count를 계산한다. 따라서 동일 counter source는 물리 clock tree나 cycle 정확도를 입증하지 않는다.

현재 wrapper는 effective frequency가 정수 Hz이고 uint32 범위에 들어오는지 검사한다. SystemC source가 표현할 수 있는 모든 fractional scaling을 QEMU mirror가 지원한다고 일반화하면 안 된다.

근거: [ARM mirror](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_arm_counter_mirror/src/qemu_arm_counter_mirror.cc) 38–62·82–99행, [QEMU count 계산](../../../hsoc-stack/tools/qemu/target/arm/helper.c) 1350–1372행.

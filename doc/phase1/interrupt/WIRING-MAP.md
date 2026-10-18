# Apollo QVP Interrupt Wiring Map

[세미나 문서로 돌아가기](README.md)

이 문서는 canonical full-system Lua의 **최종 descriptor를 정적으로 평가한 배선 지도**다. IRQ 발생, guest ISR 실행, 동시에 발생한 interrupt의 처리 결과를 입증하지 않는다.
AP 4 CPU·CL0 1 CPU·CL1 4 CPU, runner 기본 native CC3XX 및 VP audio backend를 반영했다. SPI 배선은 **AP 68 + CL0 41 + CL1 4 = 113개**이며 아래 범위 표로 압축했다. 동일 source의 다른 controller 연결은 각각 센다.

## 번호를 읽는 규칙

| 표기 | 의미 | 예 |
|---|---|---|
| SPI socket `spi_in_N` | SPI 입력 offset | AP I2C0 socket320 |
| Architectural INTID | SPI offset + 32 | I2C0 INTID352 |
| DTS `GIC_SPI N` | INTID가 아닌 SPI offset | `<GIC_SPI 320 ...>` |
| PPI socket `ppi_in_cpu_C_N` | N 자체가 INTID | AP virtual timer N=27 |
| DTS `GIC_PPI P` | PPI offset; INTID=P+16 | virtual timer offset11 |
| NVIC `irq_in_N` | external IRQn=N; exception vector=N+16 | RSE IRQ139 → vector155 |
| Linux virq | 커널이 할당하는 논리 번호 | 위 값과 별도로 확인 |

근거: [GIC wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h) 205–216행, [NVIC wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h) 116·222행. NVIC IRQ를 GIC INTID로 바꾸지 않는다.

## Controller · CPU · MMIO

아래 객체 이름에는 `platform.` 접두사가 생략돼 있다. AP·CL0·CL1 GIC는 각 domain의 QemuInstance에 속한다.

| Domain | 실제 controller / CPU | GICD / GICR · 구성 |
|---|---|---|
| AP | `ap_gic` → `ap_cpu_0..3` | 0x20800000 / 0x20880000, R stride0x40000; SPI960, revision4 |
| AP view | `ap_gic_multiview` → `ap_router` | view0 0x20000000 / 0x20080000을 backend 주소로 변환; 16 view 영역 ≠ 활성 CPU16 |
| AP ITS | `ap_gic_its` | 0x20840000; `ap_qemu_inst`, `ap_gic`에 귀속 |
| CL0 | `si_cl0_gic` → `si_cl0_cpu_0` | 0x30100000 / 0x30140000; alias 0x30000000 / 0x30040000; SPI384 |
| CL1 | `si_cl1_gic` → `si_cl1_cpu_0..3` | 0x30200000 / 0x30260000, R stride0x20000; SPI128 |
| RSE | `rse_cpu_pass.cpu_0.cpu.nvic` | M55 local NVIC, external IRQ160; GIC distributor 없음 |

근거: [AP system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) 205–302행, [CL0 system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua) 58–97행, [CL1 system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/system.lua) 17–43행, [RSE CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua).

GIC의 `irq_out_N / fiq_out_N / virq_out_N / vfiq_out_N`은 해당 CPU의 `irq_in / fiq_in / virq_in / vfiq_in`으로 연결된다. Multiview의 관리 범위 960과 실제 CL0 backend의 `num_spi=384`를 구분한다.

## AP SPI 전체 배선 — 68개

| 객체 / 출력 | SPI socket | INTID | 구성 소스 |
|---|---:|---:|---|
| `ap_secure_wdog.ws0` | 47 | 79 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| `ap_timer_mem.irq_1 / irq_0` | 48 / 49 | 80 / 81 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| `ap_watchdog_0.ws0` / NS WS1 fanout | 50 / 51 | 82 / 83 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| `ap_primary_uart / ap_secure_uart.irq` | 52 / 53 | 84 / 85 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/io_peri.lua) |
| `ap_smmu_0.irq_eventq` | 65 | 97 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| AP↔CL0 NS SCMI PBX / MBX | 112 / 113 | 144 / 145 | [system_mgmt](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua) |
| AP↔CL0 secure SCMI PBX / MBX | 114 / 115 | 146 / 147 | [system_mgmt](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua) |
| AP↔CL0 PFDI PBX / MBX | 118 / 119 | 150 / 151 | [system_mgmt](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua) |
| AP↔CL1 HIPC PBX / MBX | 120 / 121 | 152 / 153 | [system_mgmt](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua) |
| `host_smd_gpio.irq` | 193 | 225 | [system_mgmt](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/io_peri.lua) |
| `ap_virtioblk_0..3.irq_out` | 257–260 | 289–292 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/io_peri.lua) |
| `ap_virtionet_0 / ap_virtiorng_0.irq_out` | 261 / 263 | 293 / 295 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/io_peri.lua) |
| `ap_rtc_0.irq_out` | 268 | 300 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |
| `dma350_0 / dma350_1.irq_comb_nonsec` | 279 / 358 | 311 / 390 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/dma.lua) |
| `ap_gpex_0.irq_out_0..3` | 300–303 | 332–335 | [ap_compute](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/pcie.lua) |
| `ap_dw_i2c_0..5.irq` | 320–325 | 352–357 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |
| `ap_dw_ssi_0..3.irq` | 326–329 | 358–361 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |
| `ap_dw_uart_0..3.irq` | 330–333 | 362–365 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |
| `pinctrl_peri0.irq_0..13` | 334–347 | 366–379 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/pinctrl.lua) |
| `pinctrl_peri1.irq_0..7` | 348–355 | 380–387 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/pinctrl.lua) |
| `ap_dw_i2s_0 / 1.irq` | 356 / 357 | 388 / 389 | [ros](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |

[VP audio](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/backends/audio.lua)가 AP DMA/I2S를 `qemu_dma350` / `qemu_dw_apb_i2s`로 교체하면서 위 IRQ bind를 보존한다. 초기 SoC의 SystemC descriptor만으로 최종 모델을 판단하면 안 된다.

PCIe INTx는 위 4개 선이며 endpoint의 pin routing은 PCI swizzle/DT interrupt-map을 거친다. MSI/MSI-X는 ITS MMIO → LPI message 경로로, SPI 선을 추가하지 않는다. DeviceID/EventID/LPI 번호는 OS 설정을 확인해야 하며 이번 정적 표에서는 고정하지 않는다.

## Safety Island SPI 전체 배선 — CL0 41개 · CL1 4개

| Domain / 객체·역할 | SPI socket | INTID | 구성 소스 |
|---|---:|---:|---|
| CL0 system timer / watchdog WS0 | 2 / 5 | 34 / 37 | [system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua) |
| CL0 UART | 8 | 40 | [io_peri](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/io_peri.lua) |
| CL0 vMCU UART / GPIO / SPI | 9 / 10 / 11 | 41 / 42 / 43 | [si-cl0-vmcu](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/extensions/si-cl0-vmcu.lua) |
| CL0 AP NS SCMI PBX / MBX | 64 / 65 | 96 / 97 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua) |
| CL0 AP secure SCMI PBX / MBX | 66 / 67 | 98 / 99 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua) |
| CL0 AP PFDI PBX / MBX | 70 / 71 | 102 / 103 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua) |
| CL0 RSE receiver / CL1 PFDI receiver | 73 / 75 | 105 / 107 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua) |
| CL0 FMU critical / noncritical | 96 / 97 | 128 / 129 | [safety](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua) |
| CL0 AP cluster PPU0..3 | 228,233,238,243 | 260,265,270,275 | [power](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua) |
| CL0 AP core PPU0..15 | 229–232,234–237,239–242,244–247 | 261–264,266–269,271–274,276–279 | [power](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua) |
| CL0 AP NS watchdog WS1 fanout | 289 | 321 | [system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| CL0 AP RAS cluster0..3 | 293,295,297,299 | 325,327,329,331 | [safety](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua) |
| CL1 UART | 7 | 39 | [io_peri](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/io_peri.lua) |
| CL1 HIPC PBX / MBX | 40 / 41 | 72 / 73 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua) |
| CL1 PFDI sender PBX ACK | 50 | 82 | [mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua) |

AP CPU4 구성에서도 PPU는 16-core topology object를 유지한다. vMCU 레지스터·IRQ도 `--no-vmcu`와 무관하게 존재하며, 외부 endpoint 옵션은 UART/SPI/GPIO backend 연결을 결정한다. IRQ 배선 존재가 외부 TC397 트래픽 발생을 뜻하지 않는다.

## CPU별 PPI · SGI

| Domain | CPU 수 | secure / physical / virtual / hypervisor timer INTID | 해당 DTS PPI offset | 추가 PPI |
|---|---:|---|---|---|
| AP | 4 | 29 / 30 / 27 / 26 | 13 / 14 / 11 / 10 | maintenance25, PMU23, RAS17 |
| CL0 | 1 | 29 / 20 / 27 / 19 | 13 / 4 / 11 / 3 | 현재 timer 4개 |
| CL1 | 4 | 29 / 20 / 27 / 19 | 13 / 4 / 11 / 3 | 현재 timer 4개 |

각 CPU마다 독립 입력이다. 근거: [AP CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua), [CL0 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua), [CL1 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua).

SI TRM [Table 9-38 전사본](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 1645–1655행은 INTID16–19를 reserved, INTID20을 CNTHPSIRQ로 기재한다. 따라서 모델의 hyp19 / phys20 배선·라벨은 하드웨어와의 차이로 남겨야 한다. CL1 DTS와 모델 번호가 맞는 것만으로 TRM 일치를 주장할 수 없다.

SGI0–15는 각 GIC 내부의 CPU 요청 경로다. 외부 IP→SGI Lua wire나 실제 IPI 실행 여부는 이 표의 대상이 아니다.

## RSE NVIC — external source 11개

| Source / 출력 | IRQn | 배선·제약 |
|---|---:|---|
| `rse_host_uart0_s.irq` | 0 | 아래 watchdog WS1과 동일 sink |
| `rse_watchdog_ns.ws0 / ws1` | 1 / 0 | IRQ0는 NMI가 아님 |
| RSE GPIO → `rse_gpio_irq_or` | 34 | 명시적 OR 후 단일 NVIC 입력 |
| `rse_mhu0_receiver_s / rse_mhu2_receiver_s` | 41 / 45 | 서로 다른 mailbox pair |
| `host_rse_si_mhu_mbx` | 139 | CL0→RSE receiver |
| local SSE timer0 / 1 / 2 / 3 | 3 / 4 / 5 / 27 | NVIC 내부 SysTick과 별개 |

근거: [RSE IO](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/io_peri.lua), [RSE system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua), [RSE CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua), [RSE interconnect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua).

외부 source는 `rse_cpu_pass.target_signal_socket_N` → LocalPass `initiator_signal_socket_N` → `cpu_0.cpu.nvic.irq_in_N`으로 중계한다. Local SSE timer는 같은 CPU instance의 NVIC에 직접 연결된다. 중계 포트160개는 활성 source160개를 뜻하지 않는다.

**공유 IRQ0 주의:** UART와 watchdog WS1은 OR 없이 같은 sink에 직접 bind된다. [Container/LocalPass](../../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h) 1114–1117·1168–1172행은 값을 그대로 전달하고, [TargetSignalSocket](../../../hsoc-stack/tools/qbox/systemc-components/common/include/ports/target-signal-socket.h) 143–151행은 단일 값을 덮어쓴다. 한 source의 deassert가 다른 source의 assert를 가릴 가능성이 있다(정적 추론; 동시 발생 runtime 미검증).

## MHU: 송신 ACK와 상대편 수신 IRQ

PBX의 IRQ는 **송신측 로컬 ACK**, MBX의 IRQ는 **수신측 알림**이다. 표의 AP/CL0/CL1 번호는 INTID, RSE 번호는 NVIC IRQn이다.

| 데이터 방향 / pair | 송신 PBX ACK | 수신 MBX IRQ |
|---|---|---|
| AP→CL0 NS / secure / PFDI | AP 144 / 146 / 150 | CL0 97 / 99 / 103 |
| CL0→AP NS / secure / PFDI | CL0 96 / 98 / 102 | AP 145 / 147 / 151 |
| AP→CL1 / `apollo_ap_to_si_cl1` | AP `host_ap_si_cl1_mhu_pbx`:152 | CL1 `si_cl1_hipc_mhu_mbx`:73 |
| CL1→AP / `apollo_si_cl1_to_ap` | CL1 `si_cl1_hipc_mhu_pbx`:72 | AP `host_ap_si_cl1_mhu_mbx`:153 |
| RSE→CL0 / `rse_to_si_cl0` | `host_rse_si_mhu_pbx`: 미연결 | CL0 `si_cl0_rse_mhu_mbx`:105 |
| CL0→RSE / `si_cl0_to_rse` | `si_cl0_rse_mhu_pbx`: 미연결 | RSE `host_rse_si_mhu_mbx`:139 |
| AP→RSE / `ap_s_to_rse` | `host_ap_rse_mhu_pbx`: 미연결 | RSE `rse_mhu2_receiver_s`:45 |
| RSE→AP / `rse_to_ap_s` | 별도 송신 경로 | AP `host_ap_rse_mhu_mbx`: 미연결 |
| CL1→CL0 PFDI / `apollo_si_cl1_pfdi` | CL1 `si_cl1_pfdi_mhu_pbx`:82 | CL0 `si_cl0_pfdi_mhu_mbx`:107 |

근거: [AP↔SI](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua), [AP↔RSE](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_rse_mailbox.lua), [CL0 mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua), [CL1 mailbox](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua). RSE IRQ41의 pair=`rse_ap_monitor_local`은 AP→RSE secure pair와 다르다.

## 미배선 · extension 경계

| 대상 | 존재하는 연결 | 없는 연결 / 해석 |
|---|---|---|
| PMIC `board_tps6594.int_n` | →`si_cl0_pmic_gpio.gpio_in_0` | GPIO parent IRQ→GIC 없음 |
| SI PMIC host `si_cl0_dw_i2c_0` | MMIO/I2C transport | I2C IRQ→GIC 없음; polling boot transport |
| AP PCA9539 | →`host_smd_gpio.gpio_in_1`→AP INTID225 | PMIC 경로와 혼동 금지 |
| native `rse_cc3xx` | crypto MMIO | 최종 IRQ bind 없음 |
| SystemC `rse_dma350` | DMA MMIO/data | `irq_comb_nonsec` bind 없음 |
| `si_cl1_pfdi_reply_mhu_mbx` | 별도 reply pair | IRQ bind 없음 |

근거: [PMIC host extension](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/extensions/si-cl0-pmic-host.lua), [RSE security](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua), [RSE IO](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/io_peri.lua). PMIC/GPIO 주소·host glue는 QVP extension이며 물리 SI IRQ 할당으로 일반화하지 않는다.

## Reset · wake는 IRQ와 별도 제어선

| 경로 | 의미 |
|---|---|
| `ap_gic.wake_request_out_N` → AP core PPU `wakeup` | GIC wake 요청 |
| CPU `powerdown_wfi_out` → PPU `powerdown` | CPU 저전력 상태 통지 |
| PPU `power_on_reset` → CPU `reset` | core reset; CPU0은 host reset controller와 연동 |
| AP cold reset → WS1 clear → reset GPIO / AP release | watchdog source 정리 후 reset 제어 |
| RSE NVIC cold-reset adapter | NVIC 초기화; 모든 reset 순서 검증을 뜻하지 않음 |

근거: [PPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua) 223–240행, [fabric reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua), [reset adapters](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/reset-adapters.lua), [CL1 reset finalization](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/reset.lua).

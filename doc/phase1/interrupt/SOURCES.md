# Apollo Interrupt SW Implementation Report — Source References

[본문](README.md) · [배선표](WIRING-MAP.md)

<a id="s1"></a>
## S1. Arm HW · FVP 참조

| 읽은 근거 | 반영 내용 |
|---|---|
| [design/components.rst](../../../arm-zena-css/documentation/design/components.rst) | Cfg2의 CL1·SCP·GIC View0/1/2 책임 |
| [SI GIC Multiple Views 원본 도면](../../../arm-zena-css/documentation/images/si_gic_multiple_view.svg) | configuration access와 runtime IRQ 경로의 구분 |
| [System Management Block](../../../arm-zena-css/documentation/images/aspen_system_management_block.png) | RSE·SI·AP domain 경계 |
| [Zena CSS guide §9.2](../../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) | AP SPI의 CHIP_START_INTID=32, AP/SI PPI, RSE external IRQ map |
| [Zena CSS guide 8장](../../arm_zena_css_dev_guide/08-fixed-virtual-platform.md) | FVP의 구성·모델링 범위; 실물 CSS와 구분 |
| [Arm GIC-720AE TRM, Issue09](https://documentation-service.arm.com/static/679b9c8f27eda361ad4ee88f) §2.1·3.2·4.5 | GICD/GCI의 물리 기능 분담, GICR page, multiview ownership |
| [Arm GICv3/v4 Software Overview](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/GICv3_v4_overview.pdf?revision=65f91645-cd52-4795-952b-f01095ff5ef8) §4·6 | INTID·group, priority drop와 deactivate 구분 |

FVP 비교표는 참조 설계·문서와 QVP 구현을 대조한 것이다. 동일 이미지의 FVP/QVP 실행 비교나 물리 timing·FuSa parity 결과가 아니다. 특히 기본 SI 표의 PPI19/20 표기와 현재 Cfg2 QVP 배선을 구분했다.

<a id="s2"></a>
## S2. 최종 Platform · CPU · Wiring

| 소스 | 확인 지점 |
|---|---|
| [canonical entry](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full-system profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua) | SoC 생성 후 VP·board·audio 최종 구성 |
| [AP system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) | GIC·ITS·multiview properties와 주소 |
| [CL0 system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua), [CL1 system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/system.lua) | 별도 GIC backend, View0 alias/관리 창 |
| [AP CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua), [CL0 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua), [CL1 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua) | GIC CPU 출력, per-CPU PPI |
| [RSE CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua), [RSE system](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua), [interconnect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua) | NVIC 소유 instance, local timer direct bind, 외부 IRQ 중계 |
| [VP audio](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/backends/audio.lua) | AP DMA/I2S native model 교체 후 IRQ 보존 |

IP별 상세 소스·정확한 socket/INTID·조건은 [WIRING-MAP](WIRING-MAP.md)에 연결했다. 전체 SPI113은 **source-output 배선 수**이며 지원 INTID 개수, enable된 IRQ 개수, 검증 완료 IRQ 개수와 다르다.

<a id="s3"></a>
## S3. QBox · QEMU Controller · Wake/Reset

| 소스 | 함수·책임 |
|---|---|
| [arm_gicv3.h](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h) | QOM property·CPU ownership 검증·SPI/PPI GPIO binding |
| [qemu-initiator-signal-socket.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-initiator-signal-socket.h) | `event_cb`: 같은 instance direct / 다른 경로 queue |
| [qemu-target-signal-socket.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-target-signal-socket.h) | target BQL → GPIO set |
| [dw-apb-i2c.cc](../../../hsoc-stack/tools/qbox/systemc-components/i2c/src/dw-apb-i2c.cc) | `raw_interrupts`, `update_irq`, `SC_METHOD(drive_irq)` |
| [arm_gicv3_ext_range.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_ext_range.c), [arm_gicv3_dist.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_dist.c) | GPIO→INTID, level/edge source 상태 |
| [arm_gicv3.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3.c), [arm_gicv3_cpuif.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_cpuif.c) | HPPI 선택, IRQ/FIQ/wake, IAR·EOIR·DIR·SGI |
| [arm_gicv3_redist.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_redist.c) | SGI/PPI/LPI, WAKER, 즉시 ChildrenAsleep 반영 |
| [gicx00_multiview.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h) | IVIEWR/VIEWR/CTL shadow, 주소 변환, 선택적 injection mux |
| [PPU wiring](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua), [fabric reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) | AP wake_request, WFI, instance와 overlay reset 분리 |
| [runtime injection wiring](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/test-wiring/runtime-injection.lua), [injection implementation](../../../hsoc-stack/tools/qbox-platform/systemc-components/apollo_runtime_injection/src/apollo_runtime_injection.cc) | owner 검사 후 실제 CL0/CL1 `runtime_set_spi` sink |

`gicx00_multiview` 클래스의 CTLR 합성·ownership mask 기능과 **현재 SI에서 연결된 경로**를 구분했다. 현재 SI의 backend_socket과 SPI mux 출력은 미연결이다. `gic720ae_messreg`는 byte-array register 모델이며 GIC safety 오류 검출 엔진으로 해석하지 않았다.

<a id="s4"></a>
## S4. AP Linux · TF-A · OP-TEE

| 소스 | 확인 지점 |
|---|---|
| [ARM64 entry-common.c](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/entry-common.c) | EL0/EL1 IRQ → `handle_arch_irq` |
| [irq-gic-v3.c](../../../hsoc-stack/components/primary_compute/linux/drivers/irqchip/irq-gic-v3.c) | `gic_handle_irq`, irq_domain, early EOIR / late DIR 선택, IRQ chip flags |
| [irq/chip.c](../../../hsoc-stack/components/primary_compute/linux/kernel/irq/chip.c), [irq/manage.c](../../../hsoc-stack/components/primary_compute/linux/kernel/irq/manage.c) | fasteoi·oneshot·forced-threading 조건 |
| [i2c-designware-master.c](../../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-master.c) | 원인별 read-to-clear, TX_ABRT_SOURCE 선저장, FIFO service, ISR 내부 completion |
| [TF-A recipe](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-a/trusted-firmware-a-fvp-rd-aspen.inc), [Apollo machine](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf) | `spmd`, `SPM_AT_SEL2=0` 선택 |
| [plat_gicv3.c](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/common/plat_gicv3.c), [spmd_main.c](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/services/std_svc/spmd/spmd_main.c) | security group·EL 라우팅, G1S→SPMD→FFA_INTERRUPT |
| [EL3 EHF](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/bl31/ehf.c), [Apollo platform.mk](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/platform.mk) | EL3 exception handling 활성 선택, G0 dispatch / handler 완료 책임 |
| [OP-TEE conf.mk](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-automotive_rd/conf.mk), [arm.mk](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/arm.mk) | S-EL1 SPMC·GICv3·native IRQ 선택 |
| [thread_a64.S](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/kernel/thread_a64.S), [gic.c](../../../hsoc-stack/components/primary_compute/optee_os/core/drivers/gic.c) | native IRQ→IAR1→handler→EOIR1, foreign FIQ 분리 |

현재 Linux의 EOImode·PREEMPT_RT·forced-threading 실행값은 측정하지 않았다. 본문 I2C sequence는 비-threaded ISR 예이며, forced-threaded path의 controller EOI와 device handler 순서는 별도로 설명했다.

<a id="s5"></a>
## S5. SI CL0 SCP-firmware

| 소스 | 확인 지점 |
|---|---|
| [mod_gicx00.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gicx00/src/mod_gicx00.c) | DS=1·Group0·IGRPEN0 초기화 |
| [arch_exceptions.S](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.S), [arch_gic.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_gic.c) | FIQ vector→`fiq_handler`→`irq_global`→IAR0/callback/EOIR0 |
| [mod_mhu3.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/mhu3/src/mod_mhu3.c) | ISR 등록, `MDBCW_CLR` W1C 이후 transport 통지 |
| [mod_transport.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/transport/src/mod_transport.c), [mod_scmi.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/scmi/src/mod_scmi.c) | 검증·복사, ISR 내 `fwk_put_event`, 이후 `scmi_process_event` |
| [fwk_core.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_core.c) | ISR 밖의 framework event queue 처리 |

<a id="s6"></a>
## S6. SI CL1 Zephyr · MHU · OpenAMP

| 소스 | 확인 지점 |
|---|---|
| [isr_wrapper.S](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/isr_wrapper.S), [intc_gicv3.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c) | IAR1→ISR table→DSB/EOIR1 |
| [MHUv3 driver 원본](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/mbox/mbox_mhuv3.c) | IRQ_CONNECT, callback 이후 `rx_complete` |
| [veth_rpmsg.c 원본](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/ethernet/veth_rpmsg.c) | RPMsg endpoint 등록·network 소비자 |
| [Apollo CL1 recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc) | 원본을 WORKDIR/apollo-safety-island로 복사 후 configure 전 패치 |
| [veth 적용 패치](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch) | callback의 atomic pending event / work submit; workqueue의 attach·detach·normal kick |
| [MHU model](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h) | paired frame의 SET/CLEAR/MASK·receiver IRQ·sender ACK |

수신 callback 이벤트는 bitset으로 합쳐질 수 있다. IRQ 1회와 packet 1개를 1:1로 해석하지 않는다.

<a id="s7"></a>
## S7. RSE TF-M · M55 NVIC

| 소스 | 확인 지점 |
|---|---|
| [NVIC QEMU](../../../hsoc-stack/tools/qemu/hw/intc/armv7m_nvic.c), [M55 wrapper](../../../hsoc-stack/tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_m55/include/cortex-m55.h) | external IRQ +16, acknowledge·complete, 내부 NVIC/CPU 연결 |
| [target_cfg.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/target_cfg.c) | ITNS 기본 NS, MPC/PPC/SAM Secure target |
| [startup_rse.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/startup_rse.c), [platform_irq.h](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/include/platform_irq.h) | IRQ 번호·vector handler |
| [tfm_interrupts.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/tfm_interrupts.c) | mailbox Secure target·priority, receive 이후 `spm_handle_interrupt` |
| [Apollo mailbox manifest](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/manifest/ns_agent_mailbox.yaml), [SCMI manifest](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/manifest/scmi_comms.yaml) | SLIH·partition IRQ 할당 |
| [SPM interrupt.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/spm/core/interrupt.c), [psa_irq_api.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/spm/core/psa_irq_api.c) | SLIH disable/signal/schedule, psa_eoi pending clear·enable |
| [ns_agent_mailbox.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/partitions/ns_agent_mailbox/ns_agent_mailbox.c) | psa_wait→psa_eoi→RPC 처리 순서 |
| [sfcp_interrupt_handler.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_core/sfcp_interrupt_handler.c), [sfcp_link_hal.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_core/sfcp_link_hal.c) | message 수신과 MHU channel ACK |

<a id="s8"></a>
## S8. ITS · LPI · 구현 한계

| 소스 | 확인 지점 |
|---|---|
| [ITS wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3_its/include/arm_gicv3_its.h) | `parent-gicv3` 연결 |
| [arm_gicv3_its.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_its.c) | TRANSLATER의 requester_id/EventID, command queue, ITT/Collection lookup, VLPI command |
| [arm_gicv3_redist.c](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_redist.c) | LPI property/pending table, EnableLPIs 조건 |
| [PCIe wiring](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/pcie.lua) | INTx4개와 별도 MSI message 경로 |

QEMU에는 GICv4/v4.1·DirectLPI·VLPI 코드가 존재한다. 반면 현재 wrapper의 ESPI/EPPI 수는 기본값0이며 QEMU가 1-of-N SPI routing을 지원한다고 광고하지 않는다.

<a id="automotive-enhanced"></a>

## Automotive Enhanced — Multiview / FMU

[Arm v2.1 공식 SI Multiview SVG](https://arm-auto-solutions.docs.arm.com/en/v2.1/_images/si_gic_multiple_view.svg)를 내려받아 렌더링한 뒤 driver–view의 CFG/IRQ 경로 배치를 참고했다. AP 그림은 SCP의 View0 관리와 단일 실행 View1을 표시하며 SI View2를 포함하지 않는다. FMU는 별도 페이지로 분리했다. AP FMU 그림은 GIC-720AE TRM Figure 6-2를 기준으로 Distributor 내부 FMU, AXI5-Stream 보고, block type별 OR 오류 wire, Secure APB5 및 CRI/ERI 구조를 표시한다.

2026-10-19에 아래 설계·정적 구성을 추가 확인했다. GIC의 view, timer frame, NoC FMU와 GIC 내부 FMU를 구분했다.

| 대상 | 근거 | 확인 내용 |
|---|---|---|
| GIC HW 계약 | [Arm GIC-720AE TRM, 102666_0100_09_en](https://documentation-service.arm.com/static/679b9c8f27eda361ad4ee88f), GICD_IVIEWR·GICR_VIEWR 및 §6.1, pp.330–331 | View 할당 register, GIC FMU의 오류 수집·APB 접근·fault injection·critical/non-critical 출력 |
| SI view 소유 | [Arm components 설계](../../../arm-zena-css/documentation/design/components.rst) 110–128행, [canonical SI diagram](../../../arm-zena-css/documentation/images/si_gic_multiple_view.svg) | View0 관리, CL0 View1, CL1 View2 |
| AP/SI view 설정 | [SCP multiview config](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gicx00_multiview.c) 14·35–153행 | AP의 16개 Redistributor descriptor 모두 View1; NS MMIO timer INTID81 → View1; AP 설정은 CMN 이후 |
| AP view 구현 | [AP system Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua), [multiview 모델](../../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h) | View0 주소, View1 backend 주소, backend_socket 연결, view register 상태 |
| AP 실행 주소 | [TF-A platform_def.h](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/include/platform_def.h) 153–154행, [Timer AP Software 근거 A1](../timer/SOURCES.md#ap-software) | GICD 0x20800000 / GICR 0x20880000. 일부 매크로의 VIEW0 명칭보다 주소와 SCP 할당표를 기준으로 분류 |
| SI QVP 차이 | [SI CL0 system Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua), [SI CL1 system Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/system.lua) | 별도 GIC backend; SI multiview 관리 모델은 backend_socket 미연결 |
| AP NoC FMU | [AP safety Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/safety.lua), [NI-710AE FMU 모델](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_ni710ae_fmu/include/zena_ni710ae_fmu.h) | AP cluster0–3 FMU 주소·parent record·fault_socket, 주입 오류의 상위 record 전달 |
| SI 오류 수집 | [SI CL0 safety Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua), [SCP FMU driver](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/fmu/src/mod_fmu.c) 75–189행 | SI GIC FMU와 root FMU의 구분; INTID128/129, leaf record 탐색·acknowledge |

AP GIC 내부 FMU의 전용 instance·오류 입력 배선은 조사한 AP/SoC Lua에서 확인하지 못했다.


<a id="uboot-interrupt"></a>
## U-Boot / Domain Initialization

| 소스 | 반영 내용 |
|---|---|
| [U-Boot interrupts_64.c](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/lib/interrupts_64.c) | Generic interrupt_init·enable_interrupts 및 do_irq/do_fiq panic 경로 |
| [U-Boot ARM library Makefile](../../../hsoc-stack/components/primary_compute/u-boot/arch/arm/lib/Makefile) | ARM64 interrupts_64.o 선택 |
| [TF-A BL31 setup](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_bl31_setup.c) | Platform 초기화·조건부 EHF handler 등록 |
| [OP-TEE platform main.c](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-automotive_rd/main.c) | RD-Aspen primary GIC 초기화 |
| [Zephyr GICv3](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c) | PRE_KERNEL_1·Redistributor·secondary CPU interface 초기화 |
| [TF-M mailbox signal template](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/partitions/ns_agent_mailbox/ns_agent_mailbox_signal_utils.h.template) | Manifest signal별 psa_irq_enable 생성 |


## Domain Hardware / Register Interface

| 소스 | 반영 내용 |
|---|---|
| [Timer Hardware Architecture](../timer/README.md#2-hardware-architecture) | Domain별 구성·Hardware/Register/Interrupt map·QVP 구현의 문서 형식 |
| [GIC common register definitions](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/include/drivers/arm/gic_common.h) | GICD control·enable register offset |
| [GICv3 register definitions](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/include/drivers/arm/gicv3.h) | IROUTER·GICR WAKER·SGI frame register 배치 |
| [Domain별 전체 배선](WIRING-MAP.md) | AP·SI·RSE source 번호·controller base·현재 QVP 배선 |

Hardware 도면은 AP 16 PE, SI 단일 GIC Multiview, RSE NVIC 구조로 분리했다. QVP 기본 AP4와 SI의 별도 backend는 각 Domain의 QVP 구현 항목에 표시한다.

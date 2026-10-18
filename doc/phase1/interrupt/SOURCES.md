# Interrupt Architecture — 조사 근거와 검증 범위

[세미나 본문](README.md) · [배선표](WIRING-MAP.md)

**조사일: 2026-10-16.** 아래는 현재 checkout과 최종 Lua descriptor에 대한 정적 조사다. 과거 실행 이력을 이번 Phase1 완료의 신규 IRQ 검증 결과로 재사용하지 않았다.

| 저장소 | 조사 시 HEAD |
|---|---|
| `.` | `a37dcba0d32d` |
| `arm-zena-css` | `bf34d9e71f67` |
| `hsoc-stack/tools/qbox` | `b8a0499359ba` |
| `hsoc-stack/tools/qbox-platform` | `17ac742e2257` |
| `hsoc-stack/tools/qemu` | `2d83203dc366` |
| `hsoc-stack/components/primary_compute/linux` | `728c53f73006` |
| `hsoc-stack/components/primary_compute/trusted-firmware-a` | `532c9e6dc679` |
| `hsoc-stack/components/primary_compute/optee_os` | `a2a275865d65` |
| `hsoc-stack/components/system_mgmt/scp-firmware` | `b17d6d0873b9` |
| `hsoc-stack/components/system_mgmt/trusted-firmware-m` | `94c5d43ae48c` |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr` | `992228a26f3f` |
| `hsoc-stack/yocto/meta-hsoc-bsp` | `c691b907bcff` |

현재 [local.conf](../../../build/conf/local.conf)의 `MACHINE=apollo-qvp`, `RD_ASPEN_VARIANT=cfg2`, 기본 AP4를 확인했다. 아래의 “현재 구성”은 **source/metadata 선택**이며 BitBake 최종 변수, 실행 중인 ELF·DTB·`.config`의 재확인 결과는 아니다.

Codebase index는 관계 탐색에만 사용했다. Platform index는 2026-09-30 기준이고 최신 Lua 경로에 gap이 있어, 최종 배선은 직접 소스와 기존 [descriptor evaluator](../../../scripts/test/apollo_lua_descriptor.py)의 sandbox 평가로 확인했다. QBox를 실행하지 않고 full-system composition과 audio·crypto 선택을 적용했다.

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

수신 callback 이벤트는 bitset으로 합쳐질 수 있다. IRQ 1회와 packet 1개를 1:1로 해석하지 않는다. Fetched OpenAMP 내부의 모든 호출과 현재 실행 중인 vring 상태까지 검증하지는 않았다.

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

QEMU에는 GICv4/v4.1·DirectLPI·VLPI 코드가 존재한다. 반면 현재 wrapper의 ESPI/EPPI 수는 기본값0이며 QEMU가 1-of-N SPI routing을 지원한다고 광고하지 않는다. “전부 미구현”과 “물리 GIC-720AE 전체 검증 완료” 어느 쪽으로도 단정하지 않았다.

## 문서 검증

- 도면 12장의 native XML ID·연결·white theme와 SVG 내 편집 정보 일치를 확인했다(364 cells).
- draw.io Desktop CLI로 원본 book 12개 page를 렌더링·시각 검토하고, Chrome에서도 SVG 12개를 열어 확인했다.
- Markdown diagram validator와 로컬 링크·anchor·공백 검사를 수행했다.
- Validator의 raw draw.io `viewer_required` 1건은 위 Desktop의 전체 page 렌더링·시각 검토로 별도 확인했다.

| 항목 | 결과 |
|---|---|
| Source/metadata/최종 Lua 교차 조사 | 완료 |
| Diagram XML·export·viewer | 12/12 일치·렌더링·시각 검토 완료 |
| Markdown 링크·diagram validator | 로컬 링크181개 정상; diagram13건 hard failure0 |
| 신규 빌드·부팅·IRQ traffic·latency 측정 | 미실행 |

문서는 source-backed architecture 산출물이다. 실제 ISR 수행·IRQ storm 회복·동시 IRQ0 처리·FVP parity·하드웨어 안전성은 별도 실행 근거가 필요하다.

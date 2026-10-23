# Zephyr Source Reference

[Implementation Report](README.md) · [Draw.io](apollo-zephyr-architecture.drawio)

본문의 소스·설정 연결을 위한 인덱스다. 실행 검증 결과는 보고서 8장에서 관리한다.

## Kernel and configuration

| 항목 | Source |
|---|---|
| Workspace integration | [hsoc-stack/components/system_mgmt/zephyrproject/README.md](../../../hsoc-stack/components/system_mgmt/zephyrproject/README.md) |
| Zephyr version | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/VERSION](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/VERSION) |
| Apollo board configuration | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1_defconfig](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1_defconfig) |
| Apollo board DTS | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts) |
| ARM64 entry / primary voting | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/reset.S](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/reset.S) |
| AArch64 image header | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/header.S](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/header.S) |
| C runtime / architecture initialization | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/prep_c.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/prep_c.c) |
| Kernel init levels / main thread | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/init.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/init.c) |
| SMP / CPU parameters / SGIs | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/smp.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/arch/arm64/core/smp.c) |
| Image CRC / simulated CPU PM | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/soc/arm/fvp_aemv8r/aarch64/soc.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/soc/arm/fvp_aemv8r/aarch64/soc.c) |
| Linker / boot params / CRC section | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/scripts/linker.ld](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/scripts/linker.ld) |
| CRC binary patcher | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/scripts/image_crc_patcher.py](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/scripts/image_crc_patcher.py) |
| Scheduler | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/sched.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/sched.c) |
| Time slicing | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeslicing.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeslicing.c) |
| Timeout queue | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeout.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timeout.c) |
| Timer callback context | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timer.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/timer.c) |
| Workqueue | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/work.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/kernel/work.c) |

## Boot ownership and firmware packaging

| 항목 | Source |
|---|---|
| Arm boot design | [arm-zena-css/documentation/design/boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) |
| RSE CL1 load hooks | [hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/boot_hal_bl2.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/boot_hal_bl2.c) |
| RSE / CL1 memory views | [hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/host_si_memory_map.h](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/host_si_memory_map.h) |
| SCP CL1 core power-on | [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/safety_island_platform/src/mod_safety_island_platform.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/safety_island_platform/src/mod_safety_island_platform.c) |
| QVP raw loader | [hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/boot.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/boot.lua) |
| QVP loader trigger | [hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/si_cl1.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/si_cl1.lua) |
| Zephyr externalsrc / module copy / patch | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc) |
| QVP board / feature config selection | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc) |
| ELF / binary install and deploy | [layers/meta-zephyr/meta-zephyr-core/recipes-kernel/zephyr-kernel/zephyr-image.inc](../../../layers/meta-zephyr/meta-zephyr-core/recipes-kernel/zephyr-kernel/zephyr-image.inc) |
| Apollo firmware composition | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-common.inc) |
| CL1 signing input and flash composition | [arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/firmware-fvp-rd-aspen.bb](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/firmware-fvp-rd-aspen.bb) |
| RSE flash slot layout | [arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/firmware.cfg](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/firmware.cfg) |
| MCUboot image signing | [layers/meta-arm/meta-arm/classes/tfm_sign_image.bbclass](../../../layers/meta-arm/meta-arm/classes/tfm_sign_image.bbclass) |

## BSP / runtime services

| 항목 | Source |
|---|---|
| GICv3 driver | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/interrupt_controller/intc_gicv3.c) |
| Virtual timer register selection | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/timer.h](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/arch/arm64/timer.h) |
| Generic timer / clock interrupt | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/timer/arm_arch_timer.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/timer/arm_arch_timer.c) |
| PL011 driver | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/serial/uart_pl011.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/serial/uart_pl011.c) |
| Sample main | [arm-zena-css/components/safety_island/zephyr/src/apps/sample/src/main.c](../../../arm-zena-css/components/safety_island/zephyr/src/apps/sample/src/main.c) |
| MHUv3 controller | [arm-zena-css/components/safety_island/zephyr/src/drivers/mbox/mbox_mhuv3.c](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/mbox/mbox_mhuv3.c) |
| Veth / OpenAMP / shared-memory lifecycle | [arm-zena-css/components/safety_island/zephyr/src/drivers/ethernet/veth_rpmsg.c](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/ethernet/veth_rpmsg.c) |
| Apollo HIPC reattach patch | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch) |
| Board network setup | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/si_net_init.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/si_net_init.c) |
| Timer frequency check | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/si_timer_init.c](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/si_timer_init.c) |
| PFDI management workers | [arm-zena-css/components/safety_island/zephyr/src/subsys/pfdi/pfdi_mgmt.c](../../../arm-zena-css/components/safety_island/zephyr/src/subsys/pfdi/pfdi_mgmt.c) |
| PFDI agent / SCMI message completion | [arm-zena-css/components/safety_island/zephyr/src/drivers/pfdi_agent/pfdi_agent.c](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/pfdi_agent/pfdi_agent.c) |
| PFDI weak backend | [arm-zena-css/components/safety_island/zephyr/src/lib/pfdi/pfdi_weak_cpu_tests.c](../../../arm-zena-css/components/safety_island/zephyr/src/lib/pfdi/pfdi_weak_cpu_tests.c) |
| PFDI TX IRQ hook | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/pfdi-tx-irq/pfdi_agent_tx_irq.c](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/pfdi-tx-irq/pfdi_agent_tx_irq.c) |
| Kernel shell build condition | [hsoc-stack/components/system_mgmt/zephyrproject/zephyr/subsys/shell/modules/CMakeLists.txt](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/subsys/shell/modules/CMakeLists.txt) |

## Existing verification entrypoints

| 항목 | Source |
|---|---|
| QVP CL1 shell probe | [scripts/run/qbox_validation/reuse_bsp.py](../../../scripts/run/qbox_validation/reuse_bsp.py) |
| QVP PFDI / CL0 checks | [scripts/run/qbox_validation/reuse_si.py](../../../scripts/run/qbox_validation/reuse_si.py) |
| PFDI command catalog | [scripts/run/qbox_si_cl1_pfdi_catalog.py](../../../scripts/run/qbox_si_cl1_pfdi_catalog.py) |
| PFDI result evaluation | [scripts/run/qbox_si_cl1_pfdi_probe.py](../../../scripts/run/qbox_si_cl1_pfdi_probe.py) |
| Validation mapping | [scripts/validation/validation/arm-zena-css-v2.2-non-xen.yaml](../../../scripts/validation/validation/arm-zena-css-v2.2-non-xen.yaml) |
| HIPC profile backend restrictions | [scripts/validation/profiles/hipc.yaml](../../../scripts/validation/profiles/hipc.yaml) |
| HIPC OEQA cases | [hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_31_si_cl1_hipc.py](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_31_si_cl1_hipc.py) |

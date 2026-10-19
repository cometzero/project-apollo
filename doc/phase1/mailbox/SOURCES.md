# Mailbox Source Reference

[보고서 본문](README.md) · [주소·채널표](MAILBOX-MAP.md) · [draw.io 원본](apollo-mailbox-architecture.drawio)

<a id="hardware"></a>

## HW 계약

| ID | 근거 | 확인 내용 |
|---|---|---|
| H1 | [Zena SI memory map](../../../doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 1084–1117·1280–1302행; [IRQ numbering](../../../doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 1354–1371·1431–1440·1679–1690행 | AP/SI/RSE address view; AP SPI와 SI INTID 표의 번호 공간 구분 |
| H2 | [HIPC design](../../../arm-zena-css/documentation/design/hipc.rst) 17–27·87–98·114–154·207–212행 | Cfg2 AP–CL1, 512KiB, 독립 boot/DETACHED, 두 vring 방향 |
| H3 | [Arm MHUv3 driver](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/mbox/mbox_mhuv3.c) 21–151·355–368·413–469·523–598행 | DBE windows/flags, PBX/MBX register, transfer ACK, flattened ID |
| H4 | [PFDI dedicated MHU rationale](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-a/files/fvp-rd-aspen/0046-fix-rdaspen-use-a-different-MHUv3-device-for-PFDI-mo.patch) 7–10행; [Cfg2 guide boundary](../../../doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md) 32행 | 16 DBCH 제약으로 PSCI/PFDI 분리; CL1은 Cfg2 DTS/firmware로 보완 |

공식 [Arm MHU-320AE TRM r0p1](https://documentation-service.arm.com/static/666872a5d72aaf32efecd88b)의 §2·§5.1에서 단방향 PBX/MBX, DBE의 32 flags, configurable extensions를 대조했다. 이를 FVP 내부 구현이나 실측 register 값으로 간주하지 않는다.

<a id="reference"></a>

## Arm 설계 문서와 원본 도면

| ID | 근거 | 확인 내용 |
|---|---|---|
| F1 | [HIPC 원본 도면](../../../arm-zena-css/documentation/images/hipc_baremetal_design.svg); [설계 설명](../../../arm-zena-css/documentation/design/hipc.rst) 30–154행 | Linux remoteproc/mailbox, Zephyr OpenAMP/veth, shared memory 경계 |
| F2 | [SCMI 원본 도면](../../../arm-zena-css/documentation/images/scmi_comm_rse_tfa_scp.svg); [설계 설명](../../../arm-zena-css/documentation/design/components.rst) 159–190행 | RSE boot readiness, AP TF-A runtime power, SCP notification |
| F3 | [Secure Services 원본 도면](../../../arm-zena-css/documentation/images/primary_compute_secure_services.svg); [설계 설명](../../../arm-zena-css/documentation/design/secure_services.rst) 119–144행 | FF-A 구간과 SE-Proxy→MHUv3→RSE 구간 분리; U-Boot SMM 경로 |
| F4 | [PFDI design](../../../arm-zena-css/documentation/design/platform_fault_detection_interface.rst) 303–320행; [FMU design](../../../arm-zena-css/documentation/design/fmu.rst) 26–40·241–243행; [validation](../../../arm-zena-css/documentation/design/validation.rst) 737–783행 | CPU별 SCMI0x90; communication IRQ와 fault IRQ 분리; 시험 정의와 수행 결과 구분 |

<a id="platform"></a>

## QVP Lua: 주소·pair·IRQ·메모리

| ID | 근거 | 확인 내용 |
|---|---|---|
| P1 | [AP/SI MHU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua) 2–31·35–213행; [SI0 MHU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/mailbox.lua) 1–36·47–283행 | NS D0 / Secure D1 / AP PFDI D3 / HIPC frames 및 GIC wiring |
| P2 | [CL1 MHU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua) 1–17·28–130행; [CL1 interconnect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/interconnect.lua) 1–39행 | HIPC/PFDI32 DBCH, requester hold, CL1 shared alias |
| P3 | [AP/RSE MHU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_rse_mailbox.lua) 2–53행; [RSE/SI MHU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/rse_si_mailbox.lua) 2–51행; [RSE local](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 195–277행 | AP-S MHU2 stream; AP IRQ 미연결; RSE MHU0 local non-bridge; RSE IRQ45/139 |
| P4 | [Global fabric](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/interconnect.lua) 34–61행; [AP router](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua) 11–17·35–75·129–133행; [ATU map](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/css-aspen/device/host_device_definition.c) 221–269행 | AP ATU aliases와 extended system address; PFDI static bridge 우선 경로 |
| P5 | [Full reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) 13–37·72–135행; [RSE local reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 287–328행; [HIPC retention policy](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/boot.lua) 100–103행; [gs_memory reset](../../../hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h) 92–101행 | AP-facing10개/전체30개 frame reset, RSE local 경계, HIPC init_mem=false 보존 |
| P6 | [Linux-direct profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/linux-direct.lua) 1–9·119–125행; [Domain mocks](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/mocks/domains.lua) 15–83행; [SI0 FMU mapping](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua) 94–135행 | SCMI BASE only / HIPC stub / PSA unsupported; 별도 FMU 노드를 자율 MHU fault 검출로 취급하지 않음 |
| P7 | [AP memory](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua) 1–46행; [System memory](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/memory.lua) 2–52행; [CL1 memory](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/memory.lua) 3–9·64–76행; [SI0 memory aliases](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h) 83–108·164–170·236–307행 | Canonical backing과 guest alias, secure/NS SCMI·PFDI·HIPC·RSE shared areas |

<a id="models"></a>

## SystemC / QEMU bridge 구현

| ID | 근거 | 확인 내용 |
|---|---|---|
| M1 | [mhu320ae](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h) 41–78·198–268·330–365·1709–1771·2121–2181·2816–2977행 | register/SET/CLR/ACK/combined IRQ, pair lookup, access width·DMI·delay 한계 |
| M2 | [MHU reset/event](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h) 903–985·1010–1062·3100–3115행 | reset-held write, peer reset, zero-time assert와 동기 deassert, TLM callback |
| M3 | [QBox initiator](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h) 660–669·714–758행; [QEMU signal target](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-target-signal-socket.h) 28–49행 | MMIO thread 전환/lock, TLM requester/security attrs, IRQ GPIO target lock |
| M4 | [Requester hold / synthetic](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h) 2037–2116·2182–2260·3078행; [Platform explanation](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/README.md) 716–724행 | CL1 PFDI 실제 requester vCPU,10µs FREE 확인; synthetic1000ns와 full latency 분리 |

<a id="linux"></a>

## AP Linux / HIPC driver

| ID | 근거 | 확인 내용 |
|---|---|---|
| L1 | [SoC DT](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi) 540–588·625–642·746–810행; [Board DT](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts) 6–8·291–322행; [Defconfig](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig) 244·354–358행 | active DT include, SCMI/7 HIPC channels, memory regions, driver selection |
| L2 | [arm_mhuv3](../../../hsoc-stack/components/primary_compute/linux/drivers/mailbox/arm_mhuv3.c) 370–481·575–703·874–969행 | pending flags, mask, per-flag demux, callback 후 CLR / PBX ACK |
| L3 | [SCMI mailbox transport](../../../hsoc-stack/components/primary_compute/linux/drivers/firmware/arm_scmi/transports/mailbox.c) 46–77·207–240·273–368행; [SCMI shmem](../../../hsoc-stack/components/primary_compute/linux/drivers/firmware/arm_scmi/shmem.c) 19–36·90–145·163–191행 | tx_prepare, chan_lock, 늦은 A2P IRQ 방어, FREE/header/token/response |
| L4 | [Kernel recipe input](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc) 14–53행 | externalsrc + defconfig; 기존 kmeta feature 이름만 보고 최종 driver 선택 판단하지 않음 |
| L5 | [arm_si_rproc](../../../sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c) 197–224·360–402·532–610행; [rpmsg_net](../../../sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src/rpmsg_net.c) 27–42·47–78·95–119행; [Remoteproc recipe](../../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod/arm-si-rproc-mod.bb); [RPMsg recipe](../../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod/rpmsg-net-mod.bb) | DETACHED attach, 별도 SW ACK, callback/workqueue, packet→RPMsg→netif_rx |

Linux mailbox의 client/controller 분리와 IRQ·polling 완료 모델은 [공식 mailbox framework 문서](https://www.kernel.org/doc/html/latest/driver-api/mailbox.html)에서도 대조했다. Apollo의 구체적 완료 순서는 위 checkout 소스를 기준으로 한다.

<a id="ap"></a>

## AP TF-A / Secure Services

| ID | 근거 | 확인 내용 |
|---|---|---|
| A1 | [TF-A platform SCMI](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_bl31_setup.c) 31–68·103–113·193–203행; [SCMI synchronous transport](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/arm/css/scmi/scmi_common.c) 27–87행; [SCMI shared layout](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/include/plat/arm/css/common/css_def.h) 72–78행 | D1/D3,40B per-core slot, lock/BUSY/dmbst/SET/dmbsy/FREE/dmbld |
| A2 | [QVP machine](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf) 8–12행; [Inherited machine](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf) 30–32·71–72행; [OP-TEE SP selection](../../../layers/meta-arm/meta-arm/recipes-security/optee/optee-os-ts.inc) 45–49행; [SE-Proxy recipe](../../../layers/meta-arm/meta-arm/recipes-security/trusted-services/ts-sp-se-proxy_git.bb) 3–10행 | SE-Proxy/SMM Gateway 선택, OP-TEE 관리 SP와 MHU client 역할 분리; SP binary 실행 미확인 |
| A3 | [AP RSE init](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_rse_comms.c) 13–22행; [RSE PSA client](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/arm/rse/rse_comms.c) 27–145행; [MHUv3 wrapper](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/arm/mhu/mhu_wrapper_v3_x.c) 297–455행; [TF-A build](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/platform.mk) 49–56·196–205행 | PSA serialize, embed/pointer 선택, batch word stream·polling, BL2 measured-boot 조건부 consumer |

<a id="scp"></a>

## SI CL0 / SCP-firmware

| ID | 근거 | 확인 내용 |
|---|---|---|
| S1 | [MHU config](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_mhu3.c) 27–129행; [Transport config](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c) 41–224·488–511행; [IRQ enum](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_irq.h) 18–22행; [Firmware selection](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake) 21–49·124–155행 | physical channel/flag와 logical sub-element, transport NONE warmACK, QVP product의 fvp variant 이름 |
| S2 | [mhu3 driver](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/mhu3/src/mod_mhu3.c) 90–159·186–245·612–642행; [SCMI event](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/scmi/src/mod_scmi.c) 247–255행 | ISR flag CLR가 transport dispatch보다 먼저; SCMI framework event |
| S3 | [transport](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/transport/src/mod_transport.c) 225–334·625–823행; [MPU config](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_armv8r_mpu.c) 18–21·65–125행; [QVP fast-channel policy](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc) 10행 | ownership/readiness/internal copy/barrier/FREE/optional IRQ; Normal-NC payload, Device MHU; perf fast-channel OFF |

<a id="zephyr"></a>

## SI CL1 / Zephyr

| ID | 근거 | 확인 내용 |
|---|---|---|
| Z1 | [QVP board DTS](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts) 118–132·148–203행; [QVP defconfig](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1_defconfig) 60–61·101–117·142–162행; [QVP recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc) 5–16행; [Module copy recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc) 39–52·92–114행 | HIPC/PFDI defaults, inherited overlay 제거, reference module copy+patch |
| Z2 | [MHUv3 driver](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/mbox/mbox_mhuv3.c) 457–467·523–598·1154–1194행; [veth driver](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/ethernet/veth_rpmsg.c) 115–123·275–303·361–415·496–521행; [Owned reattach patch](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch) | callback 후 CLR, atomic event/workqueue, resource republish/fence/softwareACK, 후속 endpoint/ready |
| Z3 | [PFDI agent](../../../arm-zena-css/components/safety_island/zephyr/src/drivers/pfdi_agent/pfdi_agent.c) 100–117·361–421·475–505행; [TX ACK IRQ init](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/pfdi-tx-irq/pfdi_agent_tx_irq.c) 35–58행 | per-core lock/FREE/BUSY/barrier/token, HW ACK IRQ와 SCMI response polling 분리 |

<a id="rse"></a>

## RSE TF-M / BL2

| ID | 근거 | 확인 내용 |
|---|---|---|
| R1 | [BL2 readiness](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/boot_hal_bl2.c) 476–512행; [SCMI polling](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/scmi_comms.c) 88–124·161–239행; [SCMI HAL](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/scmi/scmi_hal.c) 41–58·77–159·258–272·338–346행; [TFM IRQ](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/tfm_interrupts.c) 215–233행 | BL2 polling/runtime signal, SCMI pages/notify, reload bit3 ACK의 payload-free 처리 |
| R2 | [SFCP link HAL](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_core/sfcp_link_hal.c) 14–15·279–314·411–451·553–628·677–739행; [SFCP IRQ handler](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_core/sfcp_interrupt_handler.c) 119–175·215–241행; [NS mailbox agent](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/partitions/ns_agent_mailbox/ns_agent_mailbox.c) 33–58행 | DBCH data framing/clear polling, IRQ 수거→queue→low-priority agent |
| R3 | [PSA handler](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_psa/sfcp_psa_handler/sfcp_psa_handler.c) 48–113·177–281행; [Pointer access](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sfcp/sfcp_psa/sfcp_psa_protocol/sfcp_psa_protocol_pointer_access.c) 46–123행; [Permissions](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/sfcp/sfcp_permissions_hal.c) 80–102행; [AP allowed memory](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/host_ap_memory_map.h) 16–28행; [SFCP selection](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/config.cmake) 277–294행 | PSA request queue, dispatch/reply, node2 allowed SRAM/carveout, legacy compatibility |

<a id="validation"></a>

## Test and Verification Sources

| 경로 | 제공 기능 |
|---|---|
| [Validation matrix](../../../qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml) | cpufreq·HIPC·Trusted Services의 profile/assertion 정의 |
| [CPUfreq profile](../../../scripts/run/qbox_validation/reuse_cpufreq.py) | SCMI performance consumer 검증 |
| [HIPC profile](../../../qa-tests/profiles/hipc.yaml) | DT·memory·양방향 packet·boundary traffic |
| [Trusted Services profile](../../../scripts/run/qbox_validation/reuse_trusted_services.py) | PSA suite 실행·PASS/FAIL/SKIP 집계 |
| [Domain debugger](../../../scripts/debug) | TF-A·SCP·Zephyr·TF-M 함수와 IRQ 경로 관찰 |

실행 여부와 결과는 [보고서 5장](README.md#validation)에 기록한다.

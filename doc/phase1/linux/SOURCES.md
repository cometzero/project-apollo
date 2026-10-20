# Linux Source Reference

[Implementation Report](README.md) · [Draw.io](apollo-linux-architecture.drawio)

본문의 소스·설정 연결을 위한 인덱스다. 실행 검증 결과는 보고서 8장에서 관리한다.

## Kernel source and boot

| 항목 | Source |
|---|---|
| Kernel version | [hsoc-stack/components/primary_compute/linux/Makefile](../../../hsoc-stack/components/primary_compute/linux/Makefile) |
| Apollo defconfig | [hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig) |
| ARM64 boot ABI | [hsoc-stack/components/primary_compute/linux/Documentation/arch/arm64/booting.rst](../../../hsoc-stack/components/primary_compute/linux/Documentation/arch/arm64/booting.rst) |
| ARM64 entry | [hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/head.S](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/head.S) |
| Architecture setup | [hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/setup.c](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/setup.c) |
| Kernel initialization / PID 1 | [hsoc-stack/components/primary_compute/linux/init/main.c](../../../hsoc-stack/components/primary_compute/linux/init/main.c) |
| Initramfs unpack | [hsoc-stack/components/primary_compute/linux/init/initramfs.c](../../../hsoc-stack/components/primary_compute/linux/init/initramfs.c) |
| SMP / PSCI | [hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/psci.c](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/kernel/psci.c) |

## PREEMPT_RT

| 항목 | Source |
|---|---|
| RT execution context | [hsoc-stack/components/primary_compute/linux/Documentation/core-api/real-time/differences.rst](../../../hsoc-stack/components/primary_compute/linux/Documentation/core-api/real-time/differences.rst) |
| RT locking contracts | [hsoc-stack/components/primary_compute/linux/Documentation/locking/locktypes.rst](../../../hsoc-stack/components/primary_compute/linux/Documentation/locking/locktypes.rst) |
| Forced IRQ threading | [hsoc-stack/components/primary_compute/linux/kernel/irq/manage.c](../../../hsoc-stack/components/primary_compute/linux/kernel/irq/manage.c) |
| Timer / softirq threads | [hsoc-stack/components/primary_compute/linux/kernel/softirq.c](../../../hsoc-stack/components/primary_compute/linux/kernel/softirq.c) |
| RT scheduler | [hsoc-stack/components/primary_compute/linux/kernel/sched/rt.c](../../../hsoc-stack/components/primary_compute/linux/kernel/sched/rt.c) |

## BSP / Driver integration

| 항목 | Source |
|---|---|
| Board DTS | [hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts) |
| Machine DTSI | [hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp.dtsi](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp.dtsi) |
| SoC DTSI | [hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi) |
| GICv3 driver | [hsoc-stack/components/primary_compute/linux/drivers/irqchip/irq-gic-v3.c](../../../hsoc-stack/components/primary_compute/linux/drivers/irqchip/irq-gic-v3.c) |
| Architectural timer driver | [hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c](../../../hsoc-stack/components/primary_compute/linux/drivers/clocksource/arm_arch_timer.c) |
| SBSA watchdog driver | [hsoc-stack/components/primary_compute/linux/drivers/watchdog/sbsa_gwdt.c](../../../hsoc-stack/components/primary_compute/linux/drivers/watchdog/sbsa_gwdt.c) |
| MHUv3 mailbox driver | [hsoc-stack/components/primary_compute/linux/drivers/mailbox/arm_mhuv3.c](../../../hsoc-stack/components/primary_compute/linux/drivers/mailbox/arm_mhuv3.c) |
| SCMI stack | [hsoc-stack/components/primary_compute/linux/drivers/firmware/arm_scmi](../../../hsoc-stack/components/primary_compute/linux/drivers/firmware/arm_scmi) |
| HIPC remoteproc attach | [sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c](../../../sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c) |
| RPMsg netdev | [sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src/rpmsg_net.c](../../../sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src/rpmsg_net.c) |

## Yocto build / boot integration

| 항목 | Source |
|---|---|
| Kernel provider / rootfs policy | [hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/auto-ad-nexios.conf](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/auto-ad-nexios.conf) |
| Kernel externalsrc / config | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc) |
| Kernel machine integration | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-qvp.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-qvp.inc) |
| External module signing | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/module-signing/apollo-external-module-signing.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/module-signing/apollo-external-module-signing.inc) |
| U-Boot boot command | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg) |
| U-Boot systemd-boot script | [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/auto-ad-nexios-systemd-boot.cmd](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/auto-ad-nexios-systemd-boot.cmd) |
| UKI A/B composition | [hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass) |
| Arm reference boot flow | [arm-zena-css/documentation/design/boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) |

## Initramfs / systemd

| 항목 | Source |
|---|---|
| BSP image recipe | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-bsp-initramfs.bb](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-bsp-initramfs.bb) |
| BSP init | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-bsp-init/init](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-bsp-init/init) |
| BSP selftest | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-bsp-init/nexios-bsp-selftest](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-bsp-init/nexios-bsp-selftest) |
| Product image | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-image.bbappend](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-image.bbappend) |
| Product initramfs | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-initramfs-image.bb](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-initramfs-image.bb) |
| Dm-verity early userspace | [layers/meta-security/recipes-core/initrdscripts/initramfs-framework-dm/dmverity](../../../layers/meta-security/recipes-core/initrdscripts/initramfs-framework-dm/dmverity) |
| Initramfs switch_root | [layers/poky/meta/recipes-core/initrdscripts/initramfs-framework/finish](../../../layers/poky/meta/recipes-core/initrdscripts/initramfs-framework/finish) |
| Overlay preinit | [layers/poky/meta/files/overlayfs-etc-preinit.sh.in](../../../layers/poky/meta/files/overlayfs-etc-preinit.sh.in) |
| Storage mount units / ordering | [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/auto-ad-nexios-storage/files](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/auto-ad-nexios-storage/files) |

## Existing verification

| 항목 | Source |
|---|---|
| QVP reuse validation profiles | [scripts/run/qbox_validation](../../../scripts/run/qbox_validation) |
| Non-Xen validation matrix | [qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml](../../../qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml) |
| Runtime OEQA cases | [hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases) |
| AutoSD RT tooling | [autosd/customization/rt](../../../autosd/customization/rt) |

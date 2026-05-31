# Arm Zena CSS Software Developer Guide

This directory contains a Markdown conversion of:

- `arm_zena_compute_subsystem_software_developer_guide_110125_0001_01_en.pdf`
- Document ID: `110125_0001_01_en`
- Issue: `01`
- Product revision: `r0p1`

Figures are rendered into [`assets/`](assets/) and linked from the
chapter files at the original figure captions.

## Chapter Files

- [Front matter](00-front-matter.md)
- [1. Zena CSS product highlights](01-zena-css-product-highlights.md#1-zena-css-product-highlights)
- [2. Block diagram for Zena CSS](02-block-diagram-for-zena-css.md#2-block-diagram-for-zena-css)
- [3. Documentation for Zena CSS](03-documentation-for-zena-css.md#3-documentation-for-zena-css)
- [4. Compliance of Zena CSS](04-compliance-of-zena-css.md#4-compliance-of-zena-css)
- [5. Functional blocks in Zena CSS](05-functional-blocks-in-zena-css.md#5-functional-blocks-in-zena-css)
- [5.1 ROM tables](05-functional-blocks-in-zena-css.md#5-1-rom-tables)
- [5.1.1 Debug port debug ROM with granular power requester](05-functional-blocks-in-zena-css.md#5-1-1-debug-port-debug-rom-with-granular-power-requester)
- [5.1.2 AP DBGROM ROM table](05-functional-blocks-in-zena-css.md#5-1-2-ap-dbgrom-rom-table)
- [5.1.3 APP DBGROM ROM table](05-functional-blocks-in-zena-css.md#5-1-3-app-dbgrom-rom-table)
- [5.1.4 Cluster DBG ROM table](05-functional-blocks-in-zena-css.md#5-1-4-cluster-dbg-rom-table)
- [5.1.5 Cluster Debug Block ROM (GPR ROM) ROM table](05-functional-blocks-in-zena-css.md#5-1-5-cluster-debug-block-rom-gpr-rom-rom-table)
- [5.1.6 RSE ROM table](05-functional-blocks-in-zena-css.md#5-1-6-rse-rom-table)
- [5.1.7 Safety Island ROM table](05-functional-blocks-in-zena-css.md#5-1-7-safety-island-rom-table)
- [6. Boot flow of Zena CSS](06-boot-flow-of-zena-css.md#6-boot-flow-of-zena-css)
- [6.1 Main boot sequence](06-boot-flow-of-zena-css.md#6-1-main-boot-sequence)
- [6.2 Selecting and updating firmware images](06-boot-flow-of-zena-css.md#6-2-selecting-and-updating-firmware-images)
- [7. Zena CSS software reference stack](07-zena-css-software-reference-stack.md#7-zena-css-software-reference-stack)
- [8. Fixed Virtual Platform](08-fixed-virtual-platform.md#8-fixed-virtual-platform)
- [8.1 About the FVP](08-fixed-virtual-platform.md#8-1-about-the-fvp)
- [8.2 FVP peripherals](08-fixed-virtual-platform.md#8-2-fvp-peripherals)
- [9. Programmer's model for Zena CSS](09-programmers-model-for-zena-css.md#9-programmer-s-model-for-zena-css)
- [9.1 Memory maps](09-programmers-model-for-zena-css.md#9-1-memory-maps)
- [9.1.1 AP system memory map](09-programmers-model-for-zena-css.md#9-1-1-ap-system-memory-map)
- [9.1.2 Cluster management domain memory map](09-programmers-model-for-zena-css.md#9-1-2-cluster-management-domain-memory-map)
- [9.1.3 Memory controller control memory map](09-programmers-model-for-zena-css.md#9-1-3-memory-controller-control-memory-map)
- [9.1.4 System management memory map](09-programmers-model-for-zena-css.md#9-1-4-system-management-memory-map)
- [9.1.5 PCIe MMIO memory map](09-programmers-model-for-zena-css.md#9-1-5-pcie-mmio-memory-map)
- [9.1.6 I/O Block configuration space memory map](09-programmers-model-for-zena-css.md#9-1-6-i-o-block-configuration-space-memory-map)
- [9.1.7 Debug memory map](09-programmers-model-for-zena-css.md#9-1-7-debug-memory-map)
- [9.1.8 RSE memory map](09-programmers-model-for-zena-css.md#9-1-8-rse-memory-map)
- [9.1.9 Safety Island memory map](09-programmers-model-for-zena-css.md#9-1-9-safety-island-memory-map)
- [9.2 Interrupt maps](09-programmers-model-for-zena-css.md#9-2-interrupt-maps)
- [9.2.1 AP interrupt map](09-programmers-model-for-zena-css.md#9-2-1-ap-interrupt-map)
- [9.2.2 Interrupt map for RSE](09-programmers-model-for-zena-css.md#9-2-2-interrupt-map-for-rse)
- [9.2.3 RSE expansion interrupt map](09-programmers-model-for-zena-css.md#9-2-3-rse-expansion-interrupt-map)
- [9.2.4 SI interrupt map](09-programmers-model-for-zena-css.md#9-2-4-si-interrupt-map)
- [9.2.5 SI expansion interrupt map](09-programmers-model-for-zena-css.md#9-2-5-si-expansion-interrupt-map)
- [9.3 Register descriptions for the Primary Compute subsystem](09-programmers-model-for-zena-css.md#9-3-register-descriptions-for-the-primary-compute-subsystem)
- [9.3.1 ATU_F1 registers summary](09-programmers-model-for-zena-css.md#9-3-1-atu-f1-registers-summary)
- [9.3.2 DBGTOP_PIK registers summary](09-programmers-model-for-zena-css.md#9-3-2-dbgtop-pik-registers-summary)
- [9.3.3 IO_REGBANK registers summary](09-programmers-model-for-zena-css.md#9-3-3-io-regbank-registers-summary)
- [9.3.4 CSS_RGM registers summary](09-programmers-model-for-zena-css.md#9-3-4-css-rgm-registers-summary)
- [9.3.5 SMD_CSR registers summary](09-programmers-model-for-zena-css.md#9-3-5-smd-csr-registers-summary)
- [9.3.6 E_CPU_CSR registers summary](09-programmers-model-for-zena-css.md#9-3-6-e-cpu-csr-registers-summary)
- [9.3.7 System_Generic_Timer_Synchronization registers summary](09-programmers-model-for-zena-css.md#9-3-7-system-generic-timer-synchronization-registers-summary)
- [9.3.8 System_ID registers summary](09-programmers-model-for-zena-css.md#9-3-8-system-id-registers-summary)
- [9.3.9 SYSTOP_PIK registers summary](09-programmers-model-for-zena-css.md#9-3-9-systop-pik-registers-summary)
- [9.4 Register descriptions for RSE](09-programmers-model-for-zena-css.md#9-4-register-descriptions-for-rse)
- [9.4.1 RSE Secure Access Configuration register summary](09-programmers-model-for-zena-css.md#9-4-1-rse-secure-access-configuration-register-summary)
- [9.4.2 RSE Non-secure Access Configuration register summary](09-programmers-model-for-zena-css.md#9-4-2-rse-non-secure-access-configuration-register-summary)
- [9.4.3 RSE Timestamp Timers register summary](09-programmers-model-for-zena-css.md#9-4-3-rse-timestamp-timers-register-summary)
- [9.4.4 RSE Timestamp Watchdogs Generic Watchdog Control Frame register summary](09-programmers-model-for-zena-css.md#9-4-4-rse-timestamp-watchdogs-generic-watchdog-control-frame-register-summary)
- [9.4.5 RSE Timestamp Watchdogs Generic Watchdog Refresh Frame register summary](09-programmers-model-for-zena-css.md#9-4-5-rse-timestamp-watchdogs-generic-watchdog-refresh-frame-register-summary)
- [9.4.6 RSE GPIO register summary](09-programmers-model-for-zena-css.md#9-4-6-rse-gpio-register-summary)
- [9.4.7 RSE DMA register summary](09-programmers-model-for-zena-css.md#9-4-7-rse-dma-register-summary)
- [9.4.8 RSE SDC-600 Internal register summary](09-programmers-model-for-zena-css.md#9-4-8-rse-sdc-600-internal-register-summary)
- [9.4.9 RSE Local System Counter register summary](09-programmers-model-for-zena-css.md#9-4-9-rse-local-system-counter-register-summary)
- [9.4.10 RSE CPU0_IDENTITY register summary](09-programmers-model-for-zena-css.md#9-4-10-rse-cpu0-identity-register-summary)
- [9.4.11 RSE CPU0 SECCTRL register summary](09-programmers-model-for-zena-css.md#9-4-11-rse-cpu0-secctrl-register-summary)
- [9.4.12 RSE System Information register summary](09-programmers-model-for-zena-css.md#9-4-12-rse-system-information-register-summary)
- [9.4.13 RSE System Control register summary](09-programmers-model-for-zena-css.md#9-4-13-rse-system-control-register-summary)
- [9.4.14 RSE Processor Private Peripheral Bus region](09-programmers-model-for-zena-css.md#9-4-14-rse-processor-private-peripheral-bus-region)
- [9.4.15 RSE Integration layer registers](09-programmers-model-for-zena-css.md#9-4-15-rse-integration-layer-registers)
- [9.5 Register descriptions for Safety Island](09-programmers-model-for-zena-css.md#9-5-register-descriptions-for-safety-island)
- [9.5.1 Fault Management Unit register summary](09-programmers-model-for-zena-css.md#9-5-1-fault-management-unit-register-summary)
- [9.5.2 System Control register summary](09-programmers-model-for-zena-css.md#9-5-2-system-control-register-summary)
- [9.5.3 Safety Status Unit register summary](09-programmers-model-for-zena-css.md#9-5-3-safety-status-unit-register-summary)
- [Proprietary notice](90-proprietary-notice.md#proprietary-notice)
- [Product and document information](91-product-and-document-information.md#product-and-document-information)
- [Product status](91-product-and-document-information.md#product-status)
- [Revision history](91-product-and-document-information.md#revision-history)
- [Conventions](91-product-and-document-information.md#conventions)
- [Useful resources](92-useful-resources.md#useful-resources)

## Figure Assets

- Total rendered figure assets: 313
- Naming pattern: `assets/figure-<chapter>-<number>-<caption>.png`

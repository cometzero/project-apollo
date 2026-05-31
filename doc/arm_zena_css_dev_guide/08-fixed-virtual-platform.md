<a id="fixed-virtual-platform"></a>

# 8 Fixed Virtual Platform

A Fixed Virtual Platform (FVP) enables the development of software without the requirement for the prototype hardware. Arm FVP models use binary translation technology to deliver fast simulations of the Arm-based system.

The Zena CSS FVP drives system architecture and software standardization. It enables efficient software and firmware development reducing the amount of work that is required to bring up a complete system.

You can download the Zena CSS FVPs from the [Automotive FVPs page](https://developer.arm.com/Tools%20and%20Software/Fixed%20Virtual%20Platforms/Automotive%20FVPs/).

The FVP is used with the [Zena CSS software reference stack](07-zena-css-software-reference-stack.md#zena-css-software-reference-stack).

> **Note**
>
> For details on compatibility between reference software and FVP versions, see the [Software Reference Stack Release Notes](https://arm-auto-solutions.docs.arm.com/en/latest/releasenotes.html).

<a id="fixed-virtual-platform-about-the-fvp"></a>

## 8.1 About the FVP

There are two Zena CSS FVP models.

**Table 8-1: Zena CSS FVP models**

| FVP model | Description |
| --- | --- |
| FVP_Zena_CSS_Cfg1 | Single-cluster Safety Island |
| FVP_Zena_CSS_Cfg2 | Dual-cluster Safety Island |

> **Note**
>
> FVP_Zena_CSS_Cfg2 includes a second cluster of Cortex-R82AE CPU cores within the Safety Island for additional real-time processing performance. This second cluster is not present in the current Zena CSS configurations. Therefore, the registers and interrupts for a second Safety Island cluster are not included in this document.

The FVP models the following IP components:

- Arm® Cortex®-A720AE cores
- Arm® Neoverse® CMN S3(AE) Coherent Mesh Network interconnect
- Arm® CoreLink™ NI-710AE Network-on-Chip Interconnect
- Arm® CoreLink™ GIC-720AE Generic Interrupt Controller
- Arm® CoreLink™ MMU-720AE System Memory Management Unit
- The Safety Island is based on the Arm® Cortex®-R82AE, and also includes:
    - Arm® CoreLink™ NI-710AE Network-on-Chip Interconnect
    - Arm® CoreLink™ GIC-720AE Generic Interrupt Controller
    - Arm® MHU-320AE Message Handling Unit
    - Arm® DMA-350 Direct Memory Access Controller
- The Runtime Security Engine (RSE) is based on the Arm® Cortex®-M55 processor, and also includes:
    - Arm® DMA-350 Direct Memory Access Controller
    - Arm® CoreLink™ SIE-300 AXI5 System IP for Embedded
- On-Chip ROM, RAM, and other peripherals
- Clock generators

The FVP does not model every component that Zena CSS contains. For example, the FVP does not model the following:

- Arm® CoreSight™ System-on-Chip SoC-600
- Arm® CoreSight™ STM-500 System Trace Macrocell
- Arm® CoreSight™ SDC-600 Secure Debug Channel
- Arm® CoreSight™ ELA-600 Embedded Logic Analyzer

<a id="fixed-virtual-platform-fvp-peripherals"></a>

## 8.2 FVP peripherals

The Zena CSS Reference Design Fixed Virtual Platform (FVP) includes the three main parts of a system.

These are:

- Compute Subsystem (CSS), also called the reference subsystem
- System on Chip (SoC), which contains the CSS
- Board, which contains the SoC

The FVP Rest of the System (RoS) includes components that are outside the Zena CSS Reference Design subsystem. The RoS includes the other SoC and board components that are required to run software, but which are not a part of the CSS. RoS components connect to the CSS through its expansion interfaces.

The Zena CSS RoS components include peripherals required by the software. These peripherals simulate those components that might be integrated into a compute subsystem in an SoC design or that are present on the board where the SoC is mounted.

The RoS peripheral area in the Zena CSS memory map uses an expansion AMBA AXI region. The reference design does not define this mapping.

The following table shows the FVP RoS peripherals.

**Table 8-2: FVP RoS peripherals**

| Name | FVP-assigned base address | Size | Description |
| --- | --- | --- | --- |
| System Registers | 0x00_3000_0000 | 64 KB | General purpose registers |
| Virtio P9 | 0x00_3001_0000 | 64 KB | VirtIO P9 server |
| Virtio Block 0 | 0x00_3002_0000 | 64 KB | VirtIO Block Device 0 |
| Virtio Block 1 | 0x00_3003_0000 | 64 KB | VirtIO Block Device 1 |
| Virtio Block 2 | 0x00_3004_0000 | 64 KB | VirtIO Block Device 2 |
| Virtio Block 3 | 0x00_3005_0000 | 64 KB | VirtIO Block Device 3 |
| Virtio Net Device | 0x00_3006_0000 | 64 KB | VirtIO Net device over MMIO transport 0 |
| Reserved | 0x00_3007_0000 | 64 KB | Reserved |
| Virtio RNG | 0x00_3008_0000 | 64 KB | VirtIO Random Number Generator |
| VSI 0 | 0x00_3009_0000 | 64 KB | Arm VHT virtual stream interface 0 |
| VSI 1 | 0x00_300A_0000 | 64 KB | Arm VHT virtual stream interface 1 |
| Reserved | 0x00_300B_0000 | 128 KB | Reserved |
| RTC | 0x00_300D_0000 | 64 KB | Arm PrimeCell Real-Time Clock (PL031) |
| UART 0 | 0x00_300E_0000 | 64 KB | Arm PrimeCell UART (PL011) |
| UART 1 | 0x00_300F_0000 | 64 KB | Arm PrimeCell UART (PL011) |
| Reserved | 0x00_3010_0000 | 15 MB | Reserved |
| DMA-350 | 0x00_3100_0000 | 64 KB | General purpose registers DMA |
| Reserved | 0x00_3101_0000 | 64 KB | Reserved |
| Reserved | 0x00_3102_0000 | 64 KB | Reserved |
| Reserved | 0x00_3103_0000 | 64 KB | Reserved |
| Reserved | 0x00_3104_0000 | 15.75 MB | Reserved |
| TRNG | 0x00_3200_0000 | 64 KB | True Random Number Generator (TRNG) |
| Reserved | 0x00_3201_0000 | 64 KB | Reserved |
| Reserved | 0x00_3202_0000 | 64 KB | Reserved |
| nvCounter | 0x00_3203_0000 | 64 KB | Trusted Non-volatile counters |
| Reserved | 0x00_3204_0000 | 31.87 MB | Reserved |
| Ethernet | 0x00_3400_0000 | 64 MB | Non-PCIe Ethernet controller (SMSC 91C111) |
| Intel Stratta Flash | 0x00_3800_0000 | 128 MB | Flash memory |
| RoS PLL Control | 0x02_0000_D800_0000 | 64 KB | Set of PLL control registers (set freq, status) |
| RoS Clock Control | 0x02_0000_D801_0000 | 64 KB | Clock control (including source selection, dividers, status) |
| Reserved | 0x02_0000_D802_0000 | 127.875 MB | Reserved |
| SMD Flash | 0x02_0000_E000_0000 | 128 MB | Flash memory |
| PCIe Config | 0x100_0000_0000 | 1.25 GB | ECAM0/1/2/3/4 PCIe NI-710AE Memory space2 |
| Non PCIe devices | 0x001_C000_0000 | 56 MB | Non-PCIe devices connected to IOMACRO |

The following table shows the interrupt map for the FVP RoS peripherals.

**Table 8-3: Interrupt map for FVP RoS peripherals**

| Interrupt ID | Source |
| --- | --- |
| 288 | Virtio P9 |
| 289 | Virtio Block 0 |
| 290 | Virtio Block 1 |
| 291 | Virtio Block 2 |
| 292 | Virtio Block 3 |
| 293 | Virtio Net 0 |
| 295 | Virtio RNG |
| 296 | VSI 0 |
| 297 | VSI 1 |
| 300 | PL031 (RTC) |
| 301 | PL011 (UART) 0 |
| 302 | PL011 (UART) 1 |
| 303-313 | DMA-350 |
| 314 | SMSC91c111 |
| 315 | TRNG |

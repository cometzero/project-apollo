<a id="functional-blocks-in-zena-css"></a>

# 5 Functional blocks in Zena CSS

The Zena CSS design is partitioned into functional blocks that include Arm IP and the supporting logic around them.

The following functional blocks in Zena CSS are shown in the [block diagram for Zena CSS](02-block-diagram-for-zena-css.md#block-diagram-for-zena-css).

Processor Block The Zena CSS design has 4 Processor Blocks and a total of 16 Cortex-A720AE cores across all 4 Processor Blocks. Each Processor Block includes: 4 Arm® Cortex®-A720AE CPU cores 1 DynamIQ Shared Unit (DSU) cluster with: Mixed-configuration, fixed in Hybrid-mode Arm® DynamIQ™ Shared Unit-120AE (DSU-120AE) with a 4 MB shared L3 cache Example Arm® System Monitoring Control Framework (SMCF): Group interface for automated sensor and monitor management and data collection Integrated Generic Interrupt Controller (GIC) Cluster Interface (GCI) Interconnect Block Arm® Neoverse® CMN S3(AE) Coherent Mesh Network is a mesh-based coherent interconnect supporting the AMBA® 5 CHI, AXI, and APB protocols. The Coherent Mesh Link Symmetric Multi-Processor (CML_SMP) interface provides multichip support, while the AMBA CHI to ACE5-Lite bridge (SBSX) supports connectivity to External Memory (DRAM) through the Memory Interface Expansion. Arm® CoreLink™ NI-710AE Network-on-Chip Interconnect connects to external I/O controllers and provides expansion interfaces for CMN S3(AE). Interrupt Block Includes distributed Arm® CoreLink™ GIC-720AE Generic Interrupt Controller components for handling interrupts in the system. The GIC-720AE components include the GIC Distributor and Redistributor, and Interrupt Translation Service (ITS). Supports multichip interrupt communication across chips I/O Block Includes distributed Translation Buffer Unit (TBU) and Translation Control Unit (TCU) components, which provide I/O virtualization for external I/O requesters Includes GIC components like the ITS for I/O event distribution to the DSU cluster interfaces System Management Block Includes the RSE Block, Safety Island Block, and System Management Domain The System Management Domain contains NI-710AE, peripherals, SRAM, and an expansion interface for system management functions, including System Control Management Interface (SCMI) services. By default, Cluster 0 of the Safety Island controls the System Management Domain. Safety Island Cluster 0 is responsible for power management functionality

RSE Block The Runtime Security Engine (RSE) Block provides an isolated execution environment for security-sensitive processes and data. The RSE provides a low-cost and high-efficiency implementation of a Root of Trust. The RSE enables the following runtime services: Relocates security domain services away from the host system Reduces the exposure of root secrets from the host system, minimizing the security attack surface Captures boot measurements for the host system and other trusted subsystems, for example, the Safety Island Includes 1 cluster with a primary Arm® Cortex®-M55 processor core and an extra, redundant Cortex-M55 core configured in Dual-Core LockStep (DCLS)

Safety Island Block The Safety Island provides the following essential safety-related services for Zena CSS: Executes safety-critical tasks with ISO 26262 ASIL D diagnostic capability Ensures timeliness and logic correctness of applications, using monitoring features Manages fault signals from various Automotive Enhanced (AE) IP components in the system Performs System Management for Zena CSS, including the SCMI Includes 1 cluster with a primary Arm® Cortex®-R82AE core and an extra redundant Cortex-R82AE core in Dual-Core LockStep (DCLS) Debug Block Supports CoreSight debug and trace for cores within the Processor Block, System Management Block, CMN S3(AE) mesh, and other system IP Includes components from CoreSight™ SoC-600, SDC-600 and STM-500 Reset Generation Manager Manages all reset signals across Zena CSS Ensures the correct sequencing of resets to prevent race conditions Peripheral Block Zena CSS supports connecting multiple peripherals using the main CMN S3(AE) interconnect. The Peripheral Block includes: Watchdog timers Secure and Non-secure generic timers Secure and Non-secure UARTs that are available for the Cortex-A720AE cores AP boot RAM and scratch RAM for Secure and Non-secure accesses

<a id="functional-blocks-in-zena-css-rom-tables"></a>

## 5.1 ROM tables

The ROM tables hold the locations of debug components. Debuggers can use the tables to determine which components are implemented.

External debuggers connected via the subsystem debug port can read out the ROM contents via the debug and trace AMBA APB Access Port (APB-AP), but the ROM can also be accessed via self-hosted debug.

The ROM table structure points to the external debug view of CoreSight components, not the self-hosted debug view.

Each ROM_ENTRY<x> value is a pointer to a CoreSight component. The value of each entry is as follows: ROM_ENTRY = (((Address of component - Address of ROM table) & 0xFFFFFFFFFFFFF000) | 0x3)

The following sections list the types of debug components that can be accessed for each ROM table.

The ROM tables are implemented according to the [Arm® CoreSight™ Architecture Specification v3.0](https://developer.arm.com/documentation/ihi0029/f) and the [Arm® Debug Interface Architecture Specification ADIv6.0](https://developer.arm.com/documentation/ihi0074).

<a id="functional-blocks-in-zena-css-rom-tables-debug-port-debug-rom-with-granular-power-requester"></a>

### 5.1.1 Debug port debug ROM with granular power requester

The table for the Debug Port (DP) debug ROM with Granular Power Requester (GPR) lists the locations of the following debug components for Zena CSS.

**Table 5-1: DP debug ROM with GPR**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| ROM_ENTRY0 | 0x000 | Debug AON block SDC-600 | 0x00010003 |
| ROM_ENTRY1 | 0x004 | Debug AON block RSE AHBAPL lower 4 KB | 0x00020003 |
| ROM_ENTRY2 | 0x008 | Debug AON block CTI | 0x00030003 |
| ROM_ENTRY3 | 0x00C | Debug AON block SMB ATF | 0x00040003 |
| ROM_ENTRY4 | 0x010 | Debug AON block TPIU | 0x00050003 |
| ROM_ENTRY5 | 0x014 | Debug AON block Safety Island APB-AP | 0x00060003 |
| ROM_ENTRY6 | 0x018 | AP APBIC ROM table | 0x00800007 |
| ROM_ENTRY7 | 0x01C | Debug AON block System Replicator | 0x00080003 |
| ROM_ENTRY8 | 0x020 | Debug AON block TPIU-HSSTP Replicator | 0x00090003 |
| ROM_ENTRY9 | 0x024 | Debug AON block HSSTP Embedded Trace Streamer (ETS) | 0x000A0003 |
| - | 0x028 | End of ROM table entries | 0x0 |
| - | ... | ... | ... |
| - | 0xFE0 | PIDR0 | Depends on CSS top level port DAP_TPARTNO and DAP_DESIGNER |
| - | 0xFE4 | PIDR1 | Depends on CSS top level port DAP_TPARTNO and DAP_DESIGNER |
| - | 0xFE8 | PIDR2 | Depends on CSS top level port DAP_TPARTNO and DAP_DESIGNER |
| - | 0xFEC | PIDR3 | Depends on CSS top level port DAP_TPARTNO and DAP_DESIGNER |
| - | 0xFF0 | CIDR0 | 0x0000000D |
| - | 0xFF4 | CIDR1 | 0x00000090 |
| - | 0xFF8 | CIDR2 | 0x00000005 |
| - | 0xFFC | CIDR3 | 0x000000B1 |

<a id="functional-blocks-in-zena-css-rom-tables-ap-dbgrom-rom-table"></a>

### 5.1.2 AP DBGROM ROM table

The following table specifies the AP DBGROM ROM entries in the System Debug Domain.

**Table 5-2: AP debug ROM table**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| ROM_ENTRY0 | 0x000 | AP AXI-AP | 0x10003 |
| ROM_ENTRY1 | 0x004 | APP APB-AP | 0x20003 |
| ROM_ENTRY2 | 0x008 | Clusters APB-AP | 0x30003 |
| - | 0x028 | End of ROM table entries | 0x0 |
| - | ... | ... | ... |
| - | 0xFE0 | PIDR0 | 0xA9 |
| - | 0xFE4 | PIDR1 | 0xB7 |
| - | 0xFE8 | PIDR2 | 0x0B |
| - | 0xFEC | PIDR3 | 0x0 |
| - | 0xFF0 | CIDR0 | 0x0000000D |
| - | 0xFF4 | CIDR1 | 0x00000090 |
| - | 0xFF8 | CIDR2 | 0x00000005 |
| - | 0xFFC | CIDR3 | 0x000000B1 |

<a id="functional-blocks-in-zena-css-rom-tables-app-dbgrom-rom-table"></a>

### 5.1.3 APP DBGROM ROM table

The following table specifies the APP DBGROM ROM entries in the System Debug Domain.

**Table 5-3: APP debug ROM table**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| ROM_ENTRY0 | 0x000 | Debug Block STM | 0x10003 |
| ROM_ENTRY1 | 0x004 | Debug Block CMN ATF | 0x20003 |
| ROM_ENTRY2 | 0x008 | Debug Block CMN ETF | 0x30003 |
| ROM_ENTRY3 | 0x00C | Debug Block System ATF | 0x40003 |
| ROM_ENTRY4 | 0x010 | Debug Block CTI0 | 0x50003 |
| ROM_ENTRY5 | 0x014 | Debug Block CTI1 | 0x60003 |
| ROM_ENTRY6 | 0x018 | Debug Block ETR | 0x70003 |
| ROM_ENTRY7 | 0x01C | Debug Block TCU ATF | 0x80003 |
| ROM_ENTRY8 | 0x020 | Debug Block APP Expansion ATF | 0x90003 |
| ROM_ENTRY9 | 0x024 | Debug Block STM ETF | 0xa0003 |
| ROM_ENTRY10 | 0x028 | Debug Block AON trace ETF | 0xb0003 |
| ROM_ENTRY11 | 0x02C | Debug Block STM ETR | 0xc0003 |
| ROM_ENTRY12 | 0x030 | Debug Block System CATU | 0xd0003 |
| ROM_ENTRY13 | 0x034 | Debug Block STM CATU | 0xe0003 |
| ROM_ENTRY14 | 0x038 | Debug Block APP Replicator | 0xf0003 |
| ROM_ENTRY15 | 0x03C | Debug Block Expansion ETF | 0x100003 |
| ROM_ENTRY16 | 0x040 | Debug Block TCU ETF | 0x110003 |
| ROM_ENTRY17 | 0x044 | Debug Block System ETF | 0x120003 |
| ROM_ENTRY18 | 0x048 | Debug Block TCU ELA | 0x130003 |
| ROM_ENTRY19 | 0x04C | Debug Expansion | 0x1000003 |
| ROM_ENTRY20 | 0x050 | End of ROM table entries | 0x0 |
| - | ... | ... | ... |
| - | 0xFE0 | PIDR0 | 0xAA |
| - | 0xFE4 | PIDR1 | 0xB7 |
| - | 0xFE8 | PIDR2 | 0x0B |
| - | 0xFEC | PIDR3 | 0x0 |
| - | 0xFF0 | CIDR0 | 0x0000000D |
| - | 0xFF4 | CIDR1 | 0x00000090 |
| - | 0xFF8 | CIDR2 | 0x00000005 |
| - | 0xFFC | CIDR3 | 0x000000B1 |

<a id="functional-blocks-in-zena-css-rom-tables-cluster-dbg-rom-table"></a>

### 5.1.4 Cluster DBG ROM table

The following table specifies the Cluster DBG ROM entries in the AP Debug Domain.

**Table 5-4: Cluster DBG ROM table**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| ROM_ENTRY0 | 0x000 | Cluster0 ETF | 0x10003 |
| ROM_ENTRY1 | 0x004 | Cluster1 ETF | 0x20003 |
| ROM_ENTRY2 | 0x008 | Cluster2 ETF | 0x30003 |
| ROM_ENTRY3 | 0x00C | Cluster3 ETF | 0x40003 |
| ROM_ENTRY4 | 0x010 | Cluster ATF | 0x50003 |
| ROM_ENTRY5 | 0x014 | Cluster0 CPU DBG | 0x800003 |
| ROM_ENTRY6 | 0x018 | Cluster1 CPU DBG | 0x1000003 |
| ROM_ENTRY7 | 0x01C | Cluster2 CPU DBG | 0x1800003 |
| ROM_ENTRY8 | 0x020 | Cluster3 CPU DBG | 0x2000003 |
| ROM_ENTRY9 | 0x24 | End of ROM table entries | 0x0 |
| - | ... | ... | ... |
| - | 0xFE0 | PIDR0 | 0xAA |
| - | 0xFE4 | PIDR1 | 0xB7 |
| - | 0xFE8 | PIDR2 | 0x0B |
| - | 0xFEC | PIDR3 | 0x0 |
| - | 0xFF0 | CIDR0 | 0x0000000D |
| - | 0xFF4 | CIDR1 | 0x00000090 |
| - | 0xFF8 | CIDR2 | 0x00000005 |
| - | 0xFFC | CIDR3 | 0x000000B1 |

<a id="functional-blocks-in-zena-css-rom-tables-cluster-debug-block-rom-gpr-rom-rom-table"></a>

### 5.1.5 Cluster Debug Block ROM (GPR ROM) ROM table

The DSU-120AE ROM table contains a list of components. Debuggers can use the Granular Power Requester (GPR) ROM table to determine which CoreSight components are implemented.

For full details about the DSU-120AE ROM table, see the DebugBlock ROM table section in the [Arm® DynamIQ™ Shared Unit-120AE Technical Reference Manual](https://developer.arm.com/documentation/107721).

<a id="functional-blocks-in-zena-css-rom-tables-rse-rom-table"></a>

### 5.1.6 RSE ROM table

The following table lists the debug components in the RSE.

**Table 5-5: RSE debug ROM components**

| Parameter | Value |
| --- | --- |
| FF_SYNC_DEPTH | 2 |
| NUM_ENTRIES | 2 + DBG_EXP_EN |
| TIE_OFF_PRESENT | 0 |

The following table specifies the ROM entries in the RSE.

**Table 5-6: RSE ROM table**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| - | 0xFE0 | PIDR0 | 0xE4 |
| - | 0xFE4 | PIDR1 | 0xB7 |
| - | 0xFE8 | PIDR2 | 0xB |
| - | 0xFEC | PIDR3 | 0x0 |
| - | 0xFF0 | CIDR0 | 0xD |
| - | 0xFF4 | CIDR1 | 0x90 |
| - | 0xFF8 | CIDR2 | 0x5 |
| - | 0xFFC | CIDR3 | 0xB1 |
| ROM_ENTRY0 | 0x004 | RSE CTI | 0x00001003 |
| ROM_ENTRY1 | 0x008 | RSE Debug expansion interface | 0x00010003 |
| ROM_ENTRY2 | 0x00C | <END> | 0x0 |

<a id="functional-blocks-in-zena-css-rom-tables-safety-island-rom-table"></a>

### 5.1.7 Safety Island ROM table

The Safety Island ROM table is used to identify the Safety Island system and indicate the locations of CoreSight debug components for an external debugger.

The ROM table is accessed through the APB Interconnect. The APB-AP base address points to the start of the Safety Island ROM table.

The following table specifies the ROM entries in the Safety Island.

**Table 5-7: Safety Island ROM table**

| Name | Offset | Peripheral | Value |
| --- | --- | --- | --- |
| ROM_ENTRY0 | 0x0 | CTI | 0x0000_1003 |
| ROM_ENTRY1 | 0x4 | Funnel | 0x0000_2003 |
| ROM_ENTRY2 | 0x8 | CL0 (Cortex-R82AE Cluster 0 Debug Block) | 0x0400_0003 |
| ROM_ENTRY3 | 0x10 | <End Marker> | 0x0000_0000 |
| ROM_ENTRY4 | 0xFD0 | PIDR4:<br>SIZE[3:0] = 0x0<br>JEP106 continuation code[3:0] = 0x4 | 0x0000_0004 |
| ROM_ENTRY5 | 0xFE0 | PIDR0:<br>Part no[7:0] = 0x3D | 0x0000_003D |
| ROM_ENTRY6 | 0xFE4 | PIDR1:<br>JEP106 ID code[3:0] = 0xB<br>Part no[11:8] = 0x7 | 0x0000_00B7 |
| ROM_ENTRY7 | 0xFE8 | PIDR2:<br>Revision no[3:0] = 0x0 JEDEC = 0x1<br>JEP106 ID code[6:4] = 0x3 | 0x0000_000B |
| ROM_ENTRY8 | 0xFEC | PIDR3:<br>REVAND no = 0x0<br>customer no = 0x0 | 0x0000_0000 |
| ROM_ENTRY9 | 0xFF0 | CIDR0: PRMBL_0[7:0] = 0x0D | 0x0000_000D |
| ROM_ENTRY10 | 0xFF4 | CIDR1: CLASS[3:0] = 0x9<br>PRMBL_1[3:0] = 0x0 | 0x0000_0090 |
| ROM_ENTRY11 | 0xFF8 | CIDR2: PRMBL_2[7:0] = 0x05 | 0x0000_0005 |
| ROM_ENTRY12 | 0xFFC | CIDR3: PRMBL_3[7:0] = 0xB1 | 0x0000_00B1 |

**Table 5-8: Safety Island external debugger memory map**

| Start address | End address | Size | Peripheral |
| --- | --- | --- | --- |
| 0x0000_0000 | 0x0000_1FFF | 8 KB | APB-AP |
| 0x0000_2000 | 0x0000_3FFF | 8 KB | AXI-AP |

**Table 5-9: Safety Island self-hosted debugging memory map**

| Start address | End address | Size | Peripheral |
| --- | --- | --- | --- |
| 0x04_0000_0000 | 0x04_0000_0FFF | 4 KB | Safety Island ROM Table |
| 0x04_0000_1000 | 0x04_0000_1FFF | 4 KB | CTI |
| 0x04_0000_2000 | 0x04_0000_2FFF | 4 KB | Funnel |
| 0x04_0400_0000 | 0x04_04FF_FFFF | 16 MB | CL0 DebugBlock |
| 0x04_0500_0000 | 0x05_FFFF_FFFF | ~8 GB | Reserved |

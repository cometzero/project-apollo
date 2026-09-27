# Functional Description

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description>

### Functional Description

The following sections provides more details on the functionality of the system.

- **[Clocking infrastructure](/documentation/102803/0000/Functional-Description/Clocking-infrastructure?lang=en)**
   CRSAS Ma1 provides several input clocks into the system. These are as follows:
- **[Reset infrastructure](/documentation/102803/0000/Functional-Description/Reset-infrastructure?lang=en)**
   CRSAS Ma1 defines the following system level reset scopes, namely:
- **[CPU](/documentation/102803/0000/Functional-Description/CPU?lang=en)**
   CRSAS Ma1 supports one to four ARMv8-M MVE processor cores. Each processor can support different static configurations except that the following that must be adhered to:
- **[System interconnect infrastructure](/documentation/102803/0000/Functional-Description/System-interconnect-infrastructure?lang=en)**
   The system interconnect infrastructure provides a bus infrastructure that transfers memory mapped access from bus managers to subordinates in the system. CRSAS Ma1 defines two key interconnects that form the System Interconnect and they are:
- **[Volatile Memory](/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en)**
   CRSAS Ma1 can support 0 to 4 volatile memory banks, VM<x>. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.
- **[Timers and Watchdogs](/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs?lang=en)**
   CRSAS Ma1 supports two main classes of timers and watchdogs: Timestamp based Timers and SLOWCLK AON based timers.
- **[Message Handling Unit](/documentation/102803/0000/Functional-Description/Message-Handling-Unit?lang=en)**
   When NUMCPU > 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD\_SYS power domain and are reset using the nWARMRESETSYS.
- **[Power Policy Units](/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en)**
   CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm® Power Policy Unit Architecture Specification and Arm® CoreLink™ PCK-600 Power Control Kit Technical Reference Manual.
- **[Peripheral Protection Controllers](/documentation/102803/0000/Functional-Description/Peripheral-Protection-Controllers?lang=en)**
   Peripheral Protection Controllers in the system enable the software to control whether a peripheral is accessible to the Secure or Non-secure world, and to control privileged access or unprivileged access. PPC protected peripherals can raise interrupt on security violation and response with bus error or RAZ/WI depending on the global [SECRESPCFG](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECRESPCFG?lang=en "The Security Violation Response Configuration Register is used to define the response to an access that causes security violation on the Bus Fabric.") configuration.
- **[Memory Protection Controllers](/documentation/102803/0000/Functional-Description/Memory-Protection-Controllers?lang=en)**
   Memory Protection Controllers (MPCs) in the system partitions memory into pages and allows software to define if each region is Secure or Non-secure.
- **[Manager Security Controllers](/documentation/102803/0000/Functional-Description/Manager-Security-Controllers?lang=en)**
   Manager Security Controllers (MSC) in the system transform memory transactions issued by non-CPU managers, that does not support Arm TrustZone for Armv8-M, into memory transactions suitable to Arm TrustZone for Armv8-M systems.
- **[CryptoCell](/documentation/102803/0000/Functional-Description/CryptoCell?lang=en)**
   CRSAS Ma1 supports two possible cryptographic configurations:
- **[Debug Infrastructure](/documentation/102803/0000/Functional-Description/Debug-Infrastructure?lang=en)**
   CRSAS Ma1 supports two possible configurations that define the extent of its debug system infrastructure. These are as follows:
- **[System and Security Control](/documentation/102803/0000/Functional-Description/System-and-Security-Control?lang=en)**
   CRSAS Ma1 provides several registers in the system to allow various features of the system to be discovered, configured and controlled. These registers are grouped into four register blocks:
- **[Power Control Infrastructure](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure?lang=en)**
   CRSAS Ma1 supports three possible power infrastructure levels:
- **[DMA](/documentation/102803/0000/Functional-Description/DMA?lang=en)**
   The CRSAS Ma1 supports an optional DMA-350.
- **[NPU](/documentation/102803/0000/Functional-Description/NPU?lang=en)**
   The CRSAS Ma1 supports a configurable number of Ethos-U55 NPU cores. If implemented, each NPU can support a different static configuration except that the following that must be adhered to:

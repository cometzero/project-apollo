# Memory Protection Controllers

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Memory-Protection-Controllers>

### Memory Protection Controllers

Memory Protection Controllers (MPCs) in the system partitions memory into pages and allows software to define if each region is Secure or Non-secure.

For more information, see Arm® CoreLink™ SIE-200 System IP for Embedded Technical Reference Manual and Arm® CoreLink™ SIE-300 AXI5 System IP for Embedded Technical Reference Manual. In CRSAS Ma1, each memory page that is protected by the MPC is aliased to two memory areas, one Secure, and another Non-secure. Depending on the security attribute defined for that page in the MPC by software, the page either only exists in the Secure region or the Non-secure region.

MPC protected memory pages can raise interrupt on security violation and response with bus error or RAZ/WI depending on the MPC or the [SECRESPCFG](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECRESPCFG?lang=en "The Security Violation Response Configuration Register is used to define the response to an access that causes security violation on the Bus Fabric.") register settings. The combined interrupt status of internal and external MPCs is available in the [SECMPCINTSTAT](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECMPCINTSTAT?lang=en "The interrupt signals from all Memory Protection Controllers (MPC), both within the CRSAS Ma1 and in the Expansion logic, are merged and sent to the CPUs on a single Interrupt signal. The Secure MPC Interrupt Status Register therefore provides Secure software with the ability to check which one of the MPCs is causing the interrupt. Once the source of the interrupt is identified, you must use the MPC register interface to clear the interrupt.") register.

A single MPC is provided for each [Volatile Memory](/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en "CRSAS Ma1 can support 0 to 4 volatile memory banks, VM<x>. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.") bank and each is mapped into main memory as defined in [Peripheral Region](/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en "The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:").

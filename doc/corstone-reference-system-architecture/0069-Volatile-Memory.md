# Volatile Memory

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Volatile-Memory>

### Volatile Memory

CRSAS Ma1 can support 0 to 4 volatile memory banks, VM<x>. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.

Each volatile memory (VM) can support a configurable amount of SRAM memory, but must obey the following:

- The size of each is powers of two.
- The size of each bank is defined using the VMADDRWIDTH configuration option and is equal to 2VMADDRWIDTH bytes.
- The total memory size of all volatile memory banks that exist within the system combined is less than 16Mbytes.
- All volatile memory forms a contiguous area of memory and is mapped to a starting address of 0x2100\_0000, which is also aliased to a starting address of 0x3100\_0000.

All VM<x> must support Exclusive Accesses from the processors and external managers.

Each VM<x> has a Memory Protection Controller (MPC) associated with it that provides the ability to map segments of each memory to Secure world or Non-secure world. For more information on MPC, see Arm® CoreLink™ SIE-200 System IP for Embedded Technical Reference Manual and Arm® CoreLink™ SIE-300 AXI5 System IP for Embedded Technical Reference Manual. CRSAS Ma1 requires that all VMs use the same MPC block size as defined by the configuration VMMPCBLKSIZE. In addition, the cfg\_init\_value input pin of each MPC must be set to 0b0 so that out of reset, all memory locations are mapped to the Secure world by default.

CRSAS Ma1 supports a power domain for each bank, PD\_VMR<x>. Each power domain only contains the actual volatile memory of the memory bank with all other logic of the memory banks, including the MPC, residing in PD\_SYS. Therefore any power gating or retention only refers to the memory itself. For more information on power control of PD\_VMR<x> see [BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-SYS-power-modes?lang=en "The following figure shows the power modes that BR_SYS supports. Because PD_SYS is merged with PD_CPU0 when PILEVEL = 0, BR_SYS has a power mode transition diagram like BR_CPU<n> when PILEVEL = 1.").

All VM<x>s run on SYSSYSCLK.

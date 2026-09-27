# Programmers model

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model>

### Programmers model

This section describes the functions and programmers model of CRSAS Ma1.

- **[System Memory Map overview](/documentation/102803/0000/Programmers-model/System-Memory-Map-overview?lang=en)**
   The High Level System Address Map table shows the high-level view of the memory map defined by CRSAS Ma1. This memory map is divided into Secure and Non-secure regions. The memory alternates between Secure and Non-secure regions on 256Mbyte regions, with only a few address areas exempted from security mapping because they are related to debug functionality.
- **[CPU TCM memories](/documentation/102803/0000/Programmers-model/CPU-TCM-memories?lang=en)**
   The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:
- **[Volatile Memory Region](/documentation/102803/0000/Programmers-model/Volatile-Memory-Region?lang=en)**
   CRSAS Ma1 supports up to four internal Volatile Memory (VM) Banks. While these are typically implemented as SRAMs, actual memories used are IMPLEMENTATION DEFINED.
- **[Peripheral Region](/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en)**
   The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:
- **[CPU Private Region](/documentation/102803/0000/Programmers-model/CPU-Private-Region?lang=en)**
   Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:
- **[System Control Peripheral Region](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en)**
   The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD\_AON domain or in the PD\_MGMT domain if PILEVEL = 2. There are four regions in total as follows:
- **[CPU Private Peripheral Bus region](/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region?lang=en)**
   Each CPU, as defined by the ARMv8-M architecture specification, hosts a local Private Peripheral Bus Region (PPB) at address 0xE000\_0000 to 0xE00F\_FFFF. This region is typically for integration with CoreSight debug and trace components that is normally local to each CPU and is not intended for general peripheral usage.
- **[Debug System Access Region](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region?lang=en)**
   CRSAS Ma1 supports two key configuration options for the debug system:

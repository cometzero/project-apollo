# CPU<n> External Peripheral interface EPPB

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/CPU-n--External-Peripheral-interface-EPPB>

### CPU<n> External Peripheral interface EPPB

Each CPU<n> in the system provides an interface that allows users to add peripherals to the External PPB region that are private to each processor.

This is either one 32-bit AMBA 4 APB interface for a Cortex-M55, or two 32-bit AMBA 4 APB interfaces for a Cortex-M85. These are typically used for integration with additional CoreSight debug and trace components if necessary. Only data accesses are allowed on each of these interfaces privately from each processor at address 0xE0004\_0000 to 0xE00F\_FFFF. Some of these regions are already used by peripherals like EWIC or reserved and others are available for integration of additional components.

Cortex-M55
:   If ; n>TYPE is Cortex-M55, each interface that is associated to CPU< n> resides in the PD\_CPU< n> power domain, the
    CPUCPU<n>CLK clock domain and the
    nCOLDRESETCPU<n> reset domain.

Cortex-M85
:   If ; n>TYPE is Cortex-M85, each interface that is associated with CPU< n> core PPB resides in the PD\_CPU< n> power domain, the
    CPUCPU<n>CLK clock domain and the
    nCOLDRESETCPU<n> reset domain. Each interface that is associated with CPU< n> Debug PPB resides in the PD\_DEBUG power domain, the
    DEBUGCPU<n>CLK clock domain and the
    nCOLDRESETDEBUGCPU<n> reset domain.

For more information and for the address mapping, see [CPU Private Peripheral Bus region](/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region?lang=en "Each CPU, as defined by the ARMv8-M architecture specification, hosts a local Private Peripheral Bus Region (PPB) at address E000_0000 to E00F_FFFF. This region is typically for integration with CoreSight debug and trace components that is normally local to each CPU and is not intended for general peripheral usage."), Arm® Cortex®-M55 Processor Technical Reference Manual or Arm® Cortex®-M85 Processor Technical Reference Manual.

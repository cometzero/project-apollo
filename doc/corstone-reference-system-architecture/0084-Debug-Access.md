# Debug Access

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration/Debug-Access>

### Debug Access

The CoreSight SoC-600 based debug infrastructure provides a single APB4 Debug Access Interface for an expansion Debug Access Port (DAP) to connect to minimum of two and up to five Memory Access Ports (MEM-AP), along with a Debug ROM table with the following purpose:

- One MEM-AP is used for accessing the Shared Debug System infrastructure components, including debug expansion logic on the Debug APB Expansion Interface.
- One MEM-AP for each processor in the system that provides access to each CPU<n> Debug System’s Access Interface.
- A Debug System ROM table provides information about the preceding MEM-APs.

System interconnect access to these is also provided, but access is gated using the SYSDSSACCEN<n> and SYSDSSACCENX Debug Access Control signals to control which of the processors in the system or an IMPLEMENTATION DEFINED manager or group of managers are allowed access to the preceding components. These are mapped to address 0xE010\_0000 to 0xE01F\_FFFF in the Non-secure world, and to 0xF010\_0000 to 0xF01F\_FFFF in the Secure world. The PERIPHNSPPC0.NS\_SYSDSS register then determines which of the two regions is accessible and the PERIPHSPPPC0.SP\_SYSDSS determines the privilege level.

### CPU Debug Access

To provide Debug access to each CPU core, CRSAS Ma1 provides a MEM-AP accessible through the Debug Access Interface. From this MEM-AP, a Class 0x9 Debug ROM table is provided to do the following:

- Points to the CPU<n> ROM Table that is private to each CPU at PPB address region at 0xE00F\_F000. This ROM table provides Granular Power Requestor (GPR) function as well to allow the debugger to wake CPU<n>.
- Optionally, it also points to another ROM table CPU<n> MCU ROM table added by the system integrator that resides on the PPB address region and on the EPPB expansion bus at address CPU<n>MCUROMADDR. The existence of the pointer to the CPU<n> MCU ROM is CFG\_DEF.

All access from the MEM-AP that does not access the ROM table is be forwarded to the CPU’s Debug Access Interface, and it is IMPLEMENTATION DEFINED if those access goes through power and/or clock crossing bridge.

> ### Note
>
> Accessibility through the processor’s Debug Access Interface depends on Debug Authentication signals, DBGEN and SPIDEN, and DAUTHCTRL.UIDEN register in the CPU core. For more information, see Arm® Cortex®-M55 Processor Technical Reference Manual or Arm® Cortex®-M85 Processor Technical Reference Manual.

### Shared Debug System Access

CRSAS Ma1 provides a MEM-AP that is accessible through the Debug Access Interface to provide access to the Shared Debug System. This Shared Debug System provides the following:

- Shared Debug System CoreSight ROM that describes all debug components in the Shared Debug System accessible through this MEM-AP. This ROM table includes an entry pointing to an external CoreSight ROM table at address 0x0008\_0000 through the Debug APB Expansion Interface that defines what a system integrator has added as expansion.
- A Trace Funnel to funnel all trace data sources together.
- A Replicator and an Embedded Trace Buffer (ETB) to allow trace data to be either forwarded to a TPIU in the expansion logic, or to be temporarily stored in the ETB so that software or the debugger through the Debug Access Interface can read them.
- A Cross Trigger Matrix and a Cross Trigger Interface that support triggers to and from:

  - DMA, Timers, and Watchdogs in the system,
  - Triggers from the processor cores,
  - Triggers from the expansion system.
- The Debug APB Expansion Interface to add Debug components to the system. This allows a system integrator to extend the Shared Debug System in accordance with the needs of the SoC.

For example, in

- In [Full Debug Configuration](/documentation/102803/0000/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration?lang=en "When HASCSS = 1 and DEBUGLEVEL > 0, the system contains a CoreSight SoC-600 based debug infrastructure. This infrastructure provides the following functionality:") the Debug Expansion adds the following to complete the debug solution as a standalone microcontroller:

  - A Debug Access Port (DAP) to allow an external debugger to access the platform.
  - An Access Control Gate, controlled using DAPDSSACCEN Debug Authentication Access Control signal.
  - A Cross Trigger Interface (CTI) to provide triggers to and from the TPIU.
  - A Trace Port Interface Unit (TPIU), to output trace data.
  - A Secure Debug Channel APBCOM, to provide an interface for Secure communications between the debugger and the Secure firmware in the system through which Secure debug certificates can be injected to the platform.
  - Debug Timestamp generator.

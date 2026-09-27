# System timestamp interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/System-timestamp-interface>

### System timestamp interface

CRSAS Ma1 provides a system timestamp input from an expansion timestamp counter. This timestamp is expected to be driven by a timestamp generator in the subsystem expansion. This resides in the PD\_AON power domain and nWARMRESETAON reset domain.

The system timestamp interface has the following properties:

- Name: CNTVALUE<G/B>[{23-63}:0]
- Description: Timestamp input value. This value can either be:

  - Gray coded. In this case, the signal name ends with ‘G’ and is asynchronous.
  - Binary coded. In this case, the signal name ends with ‘B’ and is synchronous to CNTCLK.
- Width: 24-64 bit, IMPL\_DEF
- Direction: Input
- Clock domain: CNTCLK or is asynchronous

When HASCSS = 1, we recommend that the expansion system uses the CTI triggers to implement timestamp halting. See sections [Cross Trigger Interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Cross-Trigger-Interface?lang=en "When DEBUGLEVEL > 0 and HASCSS > 0, CRSAS Ma1 includes a shared Cross Trigger Interface (CTI) module. Some trigger signals to and from the CTI are used within the system, while a number is made available to system expansion. The following table lists the trigger signals that are available for system expansion.") and [Cross Trigger](/documentation/102803/0000/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration/Cross-Trigger?lang=en "The Shared Debug System implements a Cross Trigger Matrix (CTM) and a single Cross Trigger Interface (CTI). These together allow DMA, timers, and watchdog timers in the CRSAS Ma1 subsystem to be halted and restarted using trigger sources from any of the CPU cores and also from trigger sources external to the subsystem through the Cross Trigger Channel Interface.") for more information on the CTI interface.

When HASCSS = 0, a Debug System does not exist to provide these control signals. Therefore, the system integrator has to depend on the CPU<n>HALTED signals to halt the system timestamp generator.

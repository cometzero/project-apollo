# Debug Timestamp interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Timestamp-interface>

### Debug Timestamp interface

When DEBUGLEVEL = 2, CRSAS Ma1 provides one or more 64-bit timestamp input or inputs. This timestamp is expected to be driven by a timestamp generator in the subsystem expansion. Depending on HASCSS configuration, the interface or interfaces are as follows:

- When HASCSS = 0 where there can only be one CPU, the processor’s debug global timestamp input, TSVALUEB[63:0], is provided as an expansion interface, CPU0TSVALUEB[63:0]. This is expected to be driven by a global timestamp generator. For more information on these interfaces, see Arm® Cortex®-M55 Processor Technical Reference Manual or Arm® Cortex®-M85 Processor Technical Reference Manual.

  This interface resides in the PD\_DEBUG power domain and resides in the DEBUGCPU0CLK clock domain and nCOLDRESETDEBUGCPU0 reset domain.
- When HASCSS = 1, a single TSVALUE<B/G> is provided and is used to generate all debug timestamps input to all processors within the system. It resides in the PD\_DEBUG power domain. The Timestamp input value TSVALUE<B/G> width is IMPLEMENTATION DEFINED, and it can either be:

  - Gray coded. In this case, the signal name ends with ‘G’ and is asynchronous.
  - Binary coded. In this case, the signal name ends with ‘B’ and is synchronous to DEBUGDEBUGCLK and is on the nCOLDRESETDEBUG reset domain.

For both configurations of HASCSS, each processor’s TSCLKCHANGE input is provided as an expansion interface as CPU<n>TSCLKCHANGE to allow the CPUs to be notified of a change in timestamp clock ratio. Each interface that is associated with CPU<n> resides in their respective DEBUGCPU<n>CLK clock domain and nCOLDRESETDEBUGCPU<n> reset domain.

When DEBUGLEVEL < 2, this timestamp interface might not exist. If they do exist, they are tied or unused.

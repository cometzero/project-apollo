# Debug Access interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Access-interface>

### Debug Access interface

When DEBUGLEVEL > 0, CRSAS Ma1 provides interfaces for debug access from an external Debug Access Port or an external debug infrastructure. Depending on the HASCSS configuration, the interface or interfaces provide the following:

- When HASCSS = 0, where there can only be one CPU, the CPU Debug D-AHB access is provided as an expansion interface. This allows the SoC integrator to drive the interface using a suitable CoreSight MEM-AP and provides debug access to the processor. For more information on the processor’s D-AHB interface, see Arm® Cortex®-M55 Processor Technical Reference Manual and Arm® Cortex®-M85 Processor Technical Reference Manual.

  The interface is in PD\_CPU0 power domain and resides in the CPUCPU0CLK clock domain and nCOLDRESETCPU0 reset domain for Cortex-M55 or nCOLDRESETDEBUGCPU0 and DEBUGCPU0CLK for Cortex-M85.
- When HASCSS = 1, a single Debug Access Interface is provided as an expansion subordinate interface. This interface is an APB4 subordinate interface and provides an additional DPABORT input signal to allow an external DAP to signal a transaction abort. This interface resides in the DEBUGDEBUGCLK clock domain and nCOLDRESETDEBUG reset domain.

When DEBUGLEVEL = 0, these interfaces might not exist. If they do exist, they are tied or unused.

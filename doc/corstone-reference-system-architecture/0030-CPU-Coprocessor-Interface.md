# CPU Coprocessor Interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/CPU-Coprocessor-Interface>

### CPU Coprocessor Interface

Each CPU core of the subsystem can be configured to have a coprocessor interface. If a CPU<n> coprocessor interface exists, then HASCPU<n>CPIF = 1.

These interfaces reside in their respective CPU’s PD\_CPU<n> power domain, CPUCPU<n>CLK clock domain and nWARMRESETCPU<n> reset domain. Note that because of the actual CPU implementation, the reset can be a special output that is dependent at least on nWARMRESETCPU<n>.

For more information on the coprocessor and related interfaces, see Arm® Cortex®-M55 Processor Integration and Implementation Manual or Arm® Cortex®-M85 Processor Integration and Implementation Manual.

# CPU Custom Datapath Extension interface

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/CPU/CPU-Custom-Datapath-Extension-interface>

### CPU Custom Datapath Extension interface

If supported by the CPU core, each CPU core of the subsystem can be configured to have a Custom Datapath Extension interface. The method to determine if this interface is present is IMPLEMENTATION DEFINED.

If a CPU<n> Custom Datapath Extension interface exists, then the protocol of this interface is IMPLEMENTATION DEFINED.

These interfaces reside in their respective processors’ PD\_CPU<n> power domain, CPUCPU<n>CLK clock domain and nWARMRESETCPU<n> reset domain.

> ### Note
>
> Depending on the actual CPU implementation, the reset can be a special output that is dependent at least on nWARMRESETCPU<n>.

For more information on the Custom Datapath Extensions and related interfaces, see Arm® Cortex®-M55 Processor Integration and Implementation Manual or Arm® Cortex®-M85 Processor Integration and Implementation Manual.

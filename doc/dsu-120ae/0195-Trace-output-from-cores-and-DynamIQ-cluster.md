# Trace output from cores and DynamIQ cluster

Source: <https://developer.arm.com/documentation/107721/0001/Debug/Trace-output-from-cores-and-DynamIQ-cluster>

### Trace output from cores and DynamIQ cluster

Each core in the cluster includes an Embedded Trace Extension (ETE) that generates trace. The trace from all the cores is funneled in the cluster down to a single AMBA 5 ATB-C interface, which is 32-bits wide in small clusters and 64-bits wide in larger clusters.

> ### Note
>
> Optionally, the
> cores and cluster can also include instances of the ELA-600, if this IP has been licensed.

The ELA-600 instances are always configured to generate Advanced Trace Bus (ATB) trace. The trace from the Embedded Logic Analyzer (ELA) instances is funneled to the same ATB trace interface as the ETE trace.

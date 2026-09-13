# Utility bus

Source: <https://developer.arm.com/documentation/107721/0001/Utility-bus>

### Utility bus

The utility bus provides access to control registers for various system components in the DynamIQ Shared Unit-120AE (DSU-120AE) and the cores within the DSU-120AE DynamIQ™ cluster. The utility bus is implemented as a 64-bit AMBA AXI5 subordinate port, and the control registers are memory-mapped onto the utility bus.

The utility bus provides access to the following system functions:

- Power Policy Unit (PPU) registers for the cluster and each of the cores
- Cluster control registers, including the L3 cache power-related monitors
- Reliability, Availability, and Serviceability (RAS) registers for the cores and cluster
- Memory Partitioning and Monitoring (MPAM) registers for the cluster
- Activity Monitor Unit (AMU) registers in the cores and cluster
- Maximum Power Mitigation Mechanism (MPMM) registers in the cores and cluster

> ### Note
>
> Information about the PPU registers for the
> cores in the cluster is provided in this document. For information on all the other
> core registers accessible from the utility bus, see your
> core Technical Reference Manual (TRM).

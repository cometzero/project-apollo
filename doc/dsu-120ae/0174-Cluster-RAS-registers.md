# Cluster RAS registers

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Cluster-RAS-registers>

### Cluster RAS registers

The cluster Reliability, Availability, and Serviceability (RAS) registers are treated as a separate node in the memory-mapped view. The cluster RAS registers are accessible either from memory-mapped accesses on the utility bus or from System register accesses from the cores. You must access the cluster RAS registers from the Secure address space.

> ### Note
>
> - The cluster RAS registers are treated as RAZ/WI if either:
>   - The register is marked as Reserved.
>   - The register is accessed in the wrong Security state.
> - Any address that is not documented is treated as RAZ/WI.

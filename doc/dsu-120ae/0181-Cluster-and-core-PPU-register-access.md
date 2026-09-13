# Cluster and core PPU register access

Source: <https://developer.arm.com/documentation/107721/0001/Utility-bus/Utility-bus-accesses/Cluster-and-core-PPU-register-access>

### Cluster and core PPU register access

The Power Policy Unit (PPU) registers for each core and cluster are still accessible when the cluster is powered off.

If a core is not powered on, then any access to a core register (not including the PPU registers) is treated as RAZ/WI. Similarly, if the cluster is powered off, then any access to a cluster register (not including the PPU registers) is treated as RAZ/WI.

> ### Note
>
> - The PPUs for the cluster and each of the cores are still accessible when the cluster is powered off.
> - The PPU registers for a core are still accessible when that core is powered off.

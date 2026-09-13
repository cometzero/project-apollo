# Integration of the cores in the cluster

Source: <https://developer.arm.com/documentation/107721/0001/Technical-overview/-DynamIQ-cluster-components/Integration-of-the-cores-in-the-cluster>

### Integration of the cores in the cluster

When you implement a DSU-120AE DynamIQ™ cluster, all interfacing between the cores, complexes, and the DynamIQ Shared Unit-120AE (DSU-120AE) is implemented automatically. All the external signal inputs and outputs pass through the DSU-120AE. The DSU-120AE buffers and resynchronizes many of these signals to allow cores and complexes to be clocked at different speeds.

The memory interfacing of each core is internally connected to the DSU-120AE L3 memory system. Where necessary, the DSU-120AE implements additional buffering to compensate for different clock rates of the core and DSU-120AE L3 memory system.

Each core has an external clock interface, which is routed through the DSU-120AE to the respective core.

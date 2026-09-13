# Memory retention mode (MEM_RET)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Memory-retention-mode--MEM-RET-->

### Memory retention mode (MEM\_RET)

In Memory retention mode, the L3 cache RAMs are placed in retention while the DynamIQ™ cluster shared logic and the cores are powered down.

It is quicker for the cluster to enter and exit Memory retention mode as compared with going from Off to On mode or On to Off mode. This is because the L3 cache RAMs do not need to be cleaned, and in some circumstances the data reloaded as well.

> ### Note
>
> The DynamIQ Shared Unit-120AE (
> DSU-120AE) remains coherent when in Memory retention mode. Any snoop arriving is stalled while the
> DSU-120AE automatically requests the cluster Power Policy Unit (PPU) to bring the cluster to an On mode to process the snoop. Although it is possible for components of the system to access the L3 cache RAMs while in retention, it comes at considerable time cost as the
> DSU-120AE must be powered up to service the access. Therefore, when using this mode,
> Arm® strongly recommends that no other external coherent agents are active, for example
> cores external to the cluster, or other coherent devices.

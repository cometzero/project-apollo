# L3 cache partitioning

Source: <https://developer.arm.com/documentation/107721/0001/L3-cache/L3-cache-partitioning>

### L3 cache partitioning

The L3 cache supports a partitioning scheme that alters the cache allocation and victim selection policy to prevent processes from using the entire L3 cache to the disadvantage of other processes.

Each transaction that is sent from the cores to the DynamIQ Shared Unit-120AE (DSU-120AE) is given a partition ID by the cores. The core software is responsible for determining the ID value for different transactions. The L3 cache partitioning control registers can be programmed to associate a partition ID value with a particular group of cache ways. Consequently, each transaction is only permitted to allocate into the L3 cache in one of the cache ways in the group defined by the partition ID of the transaction.

Cache partitioning is intended for specialized software where there are distinct classes of processes running with different cache accessing patterns. For example, two processes A and B run on separate cores in the same cluster and therefore share the L3 cache. If process A is more data-intensive than process B, then process A can cause all the cache lines that process B allocates to be evicted. Evicting these allocated cache lines can reduce the performance of process B.

The DSU-120AE uses the Memory System Resource Partitioning and Monitoring (MPAM) architecture extension to control the partitioning of the L3 cache. For more information on the MPAM controls used and the structure of the MPAM partition ID (MPAM ID) for the DSU-120AE, see [Memory System Resource Partitioning and Monitoring control](/documentation/107721/0001/L3-cache/Memory-System-Resource-Partitioning-and-Monitoring-control?lang=en "The DSU-120AE uses the Memory system resource Partitioning And Monitoring (MPAM) architecture extension to control L3 cache partitioning and bandwidth partitioning.").

When the `L3_MPAM_STORAGE` parameter is enabled, then the L3 cache stores the MPAM ID information, which is retrieved on evictions.

> ### Note
>
> Storing the MPAM ID value in the L3 cache is typically only required if there is a downstream cache, such as a system cache, that also provides MPAM support. If the system only requires valid MPAM ID values for read transactions, then this MPAM ID storage is not required.

If the MPAM IDs are not being stored, then any L3 evictions use the MPAM ID of the transaction that causes the eviction.

> ### Note
>
> If a transaction is mapped to a partition for which the MPAMCFG\_CPBM setting has no portions set, then this transaction is not allocated into the L3 cache.

The partitioning of the L3 cache is done by groups of cache ways, and for the DSU-120AE each group contains two ways, so a maximum of 8 partitions are supported. When programming the partitioning, the groups of L3 cache way pairs are referred to as portions.

> ### Note
>
> - The portions referred to when programming MPAM partitions are different from the L3 cache power portions. The term power portion is used to identify the L3 cache ways that are powered up and powered down for power-saving purposes.
> - The cache sizes that are not a power of two (1.5MB, 3MB, 6MB, and 12MB) support fewer portions than other cache sizes, because they have fewer available ways than the other cache sizes.
> - If some cache ways are powered down (for more details, see [L3 cache RAM powerdown](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown?lang=en "The L3 cache RAMs typically contribute to a large proportion of the total leakage power, particularly for large cache sizes. Therefore, it is beneficial to power down the RAMs when only some of the L3 cache is required, but it also results in reducing cache capacity. Parts of the L3 cache RAM can be independently powered down to reduce RAM leakage power when not in use. L3 cache powerdown is controlled by the cluster Power Policy Unit (PPU).")) then the number of ways are halved in each L3 cache partition portion. This reduction in cache ways can degrade the performance, when there are insufficient ways available to a process. Therefore, Arm recommends that caution is used when powering down cache ways while using cache partitioning.

One advantage of MPAM being an architectural extension is that it defines a generic mechanism to partition the L3 cache and can therefore be easily interacted with and configured by standard software.

Cache partitioning allows you to split the L3 cache into up to 8 separate partitions. You can overlap the cache portions defined for each partition. For instance, you might assign:

- Portions 0 to 3 (cache ways 0 to 7) to partition 0 (MPAM PARTID 0)
- Portions 0 to 7 (cache ways 0 to 15) to partition 1 (MPAM PARTID 1)

This would mean that while the processes assigned to partition 1 could use all the ways, the processes assigned to partition 0 could only use half of the ways.

The Secure and Non-secure states have separate control registers for programming the cache portions (cache ways) that are assigned to each partition ID. The Secure state partition control register, MPAMCFG\_CPBM\_s, has an additional non-architectural control bit that allows the Secure state partitioning programming to override the Non-secure state partitioning programming. The MPAMCFG\_CPBM\_s register is used to program the cache portions that can be used by each of the different Secure state partition ID values.

When the MPAMCFG\_CPBM\_s.S\_EXCL is set to 1, then any of the cache portions (and therefore the cache ways) used for a Secure partition ID are only permitted to allocate transactions from the Secure state. Therefore, if any of the Non-secure state partition IDs have been programmed to use these cache portions (that are marked as Exclusive for the Secure state), then Non-secure state transactions are not permitted to allocate into these L3 cache portions.

### Related information

- [L3 cache RAM powerdown](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown?lang=en "The L3 cache RAMs typically contribute to a large proportion of the total leakage power, particularly for large cache sizes. Therefore, it is beneficial to power down the RAMs when only some of the L3 cache is required, but it also results in reducing cache capacity. Parts of the L3 cache RAM can be independently powered down to reduce RAM leakage power when not in use. L3 cache powerdown is controlled by the cluster Power Policy Unit (PPU).")
- [L3 cache](/documentation/107721/0001/L3-cache?lang=en "All the cores and complexes in the DSU-120AE DynamIQ cluster share the L3 cache.")

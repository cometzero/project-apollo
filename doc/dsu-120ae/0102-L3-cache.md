# L3 cache

Source: <https://developer.arm.com/documentation/107721/0001/L3-cache>

### L3 cache

All the cores and complexes in the DSU-120AE DynamIQ™ cluster share the L3 cache.

The shared L3 cache of the DSU-120AE (applies to non-Direct cores) provides the following functionality:

- A dynamically optimized cache allocation policy, which is typically exclusive. This cache allocation policy means that in normal use, a line is either in the cache of one or more cores (or complexes) or in the L3 cache, but not in both caches. Only Cacheable, shareable memory locations are allocated in the L3 cache. Non-shareable memory locations are not allocated in the L3 cache.
- Groups of cache ways can be partitioned and assigned to processes[1](/documentation/107721/0001/L3-cache?lang=en#fntarg_1) by the Memory System Resource Partitioning and Monitoring (MPAM) architecture extension. Cache partitioning ensures that each process does not dominate the use of the cache to disadvantage other processes.
- Support for stashing requests from the ACP and CHI interfaces. These stashing requests can also target any of the L2 caches of cores or complexes within the cluster.
- Error Correcting Code (ECC) protection is provided on the cache data and tag RAMs.
- The cache can be implemented with up to eight cache slices, depending on the specified L3 cache size. Cache slices can increase the bandwidth of the L3 cache and improve the physical floorplan. Each cache slice consists of data, tag, victim, and snoop filter RAMs and associated logic.

> ### Note
>
> On powerdown, the
> DSU-120AE automatically performs cache cleaning, eliminating the need for software-controlled cache cleaning.

### Related information

- [L3 cache allocation policy](/documentation/107721/0001/L3-cache/L3-cache-allocation-policy?lang=en "The DSU-120AE L3 cache only caches Cacheable, shareable memory locations. Non-shareable memory locations do not allocate into the L3 cache. In configurations with both the Accelerator Coherency Port (ACP) and the 64-bit AXI5 peripheral port, memory in the peripheral port address range is not accessible to ACP and will not be allocated to the L3 cache.")
- [Available number of cache ways](/documentation/107721/0001/L3-cache/Available-number-of-cache-ways?lang=en "The available number of cache ways in each cache slice depend on the L3 cache size that you choose to implement.")
- [L3 cache partitioning](/documentation/107721/0001/L3-cache/L3-cache-partitioning?lang=en "The L3 cache supports a partitioning scheme that alters the cache allocation and victim selection policy to prevent processes from using the entire L3 cache to the disadvantage of other processes.")
- [Cache slices and power portions](/documentation/107721/0001/L3-cache/Cache-slices-and-power-portions?lang=en "The L3 cache of the DynamIQ Shared Unit-120AE (DSU-120AE) can be divided up into identical slices, up to a limit of eight slices, each containing between 256KB and 4MB of the cache. A cache slice consists of the data, tag, victim, and snoop filter RAMs and associated logic. A power portion is a further subdivision of RAM in a cache slice.")

[1](/documentation/107721/0001/L3-cache?lang=en#fnsrc_1) A process is an instance of a computer program.

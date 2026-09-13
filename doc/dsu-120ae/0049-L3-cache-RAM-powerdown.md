# L3 cache RAM powerdown

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown>

### L3 cache RAM powerdown

The L3 cache RAMs typically contribute to a large proportion of the total leakage power, particularly for large cache sizes. Therefore, it is beneficial to power down the RAMs when only some of the L3 cache is required, but it also results in reducing cache capacity. Parts of the L3 cache RAM can be independently powered down to reduce RAM leakage power when not in use. L3 cache powerdown is controlled by the cluster Power Policy Unit (PPU).

The L3 cache RAM powerdown feature allows the RAMs to be powered down in groups of ways, giving options of 100%, 50%, or 0% of the L3 cache capacity. When a workload is making light use of the L3 cache, then this can be detected and the L3 cache capacity reduced without significant impact on the performance. For example, this can occur when the L3 cache has a relatively small memory footprint that mostly fits within the L2 cache.

Powering down a group of ways involves first cleaning and invalidating the cache lines that are held in those ways. This takes time and consumes dynamic power. Therefore, the decision to power down these ways should balance these costs against the power saved during the time spent in the lower power mode.

> ### Note
>
> Cleaning and invalidating the L3 cache lines is performed by hardware in the background and does not prevent the
> cores from executing instructions.

L3 cache RAM powerdown can be used, irrespective of the number of cores that are powered on or active.

There are three methods to control the cache portions (SFONLY, ½ RAM, and FULL RAM operating modes) which can be based on cache performance. See the following sections in order of preference:

- [Setting automatic L3 cache power portion control](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Setting-automatic-L3-cache-power-portion-control?lang=en "The DSU-120AE contains hardware to automatically schedule L3 cache power portion requests based on hit and miss counts. The cluster uses the L3 cache hit and miss rates to try to balance the leakage savings from powering down the cache with the energy cost of DRAM accesses.")
- [Setting CLUSTERPWRCTLR\_EL1.PRTNRQ power portion control](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Setting-CLUSTERPWRCTLR-EL1-PRTNRQ-power-portion-control?lang=en "Software running on the core can program CLUSTERPWRCTLR_EL1.PRTNRQ to directly control the L3 cache power portion power requests.")
- [L3 RAM power control using PPU static transactions](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/L3-RAM-power-control-using-PPU-static-transactions?lang=en "You can use a System Control Processor (SCP) to program the cluster Power Policy Unit (PPU) explicitly through the utility bus to control powerup and powerdown of parts of L3 cache RAMs, by setting operating and power modes.")

> ### Note
>
> For information on operating modes, see
> [Cluster operating modes](/documentation/107721/0001/Power-management/Cluster-operating-modes?lang=en "An operating mode is a component-specific configuration of the power modes. For the DynamIQ Shared Unit-120AE (DSU-120AE), the operating modes differ in the number of slices that are active, and in the amount of L3 cache RAM that is active. The cluster Power Policy Unit (PPU) provides programming access to control the operating modes and the power modes. The DSU-120AE supports several operating modes to control two groups of modes. One mode from each group can be combined together in any combination.").

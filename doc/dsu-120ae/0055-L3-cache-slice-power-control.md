# L3 cache slice power control

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-slice-powerdown/L3-cache-slice-power-control>

### L3 cache slice power control

The DSU-120AE contains hardware to automatically schedule L3 cache slice powerdown and powerup requests. The cluster provides a number of configurable mechanisms to determine when the L3 cache slices need to be powered. If any enabled mechanism determines that more slices need to be powered up, the cluster automatically requests this power transition. If all enabled mechanisms determine that fewer slices are required, and this remains the case for a configurable period of time, the cluster automatically requests this power transition.

### Enable automatic L3 cache slice power control

This generates automatic cache power portion requests that are translated to an internal PACTIVE indicator between the cluster and the cluster PPU. The cluster PPU responds accordingly to these requests.

- The System Control Processor (SCP) programs the cluster Power Policy Unit (PPU) for dynamic transitions.
- Software running on the core programs the IMP\_CLUSTERPWRCTLR\_EL1 to configure the automatic powerdown mechanisms. The controls for the diffent mechanims are in the following register fields. See [IMP\_CLUSTERPWRCTLR\_EL1, Cluster Power Control Register](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRCTLR-EL1--Cluster-Power-Control-Register?lang=en "This register controls power features of the cluster.") for more information.
  - SLCRQ. You can use this field to program a minimum number of L3 cache slices that should be kept on.
  - SLCPRTN. This field enables a mechanism that keeps L3 cache slices powered on if the "automatic L3 cache power portion control" mechanism determines that all their L3 cache is useful. The mechanism can also power up more L3 cache slices based on the value of IMP\_CLUSTERL3UPTH2\_EL1 / CLUSTERL3UPTH2. See [Setting automatic L3 cache power portion control](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Setting-automatic-L3-cache-power-portion-control?lang=en "The DSU-120AE contains hardware to automatically schedule L3 cache power portion requests based on hit and miss counts. The cluster uses the L3 cache hit and miss rates to try to balance the leakage savings from powering down the cache with the energy cost of DRAM accesses.") for how to program this register.
  - SLCBW. This mechanism ensures that more slices are powered up if the current number of slices cannot provide the required bandwidth. You can use this field to control the sensitivity of this mechanism or disable it.
  - SLCSF. This mechanism ensures that the number of slices powered up is sufficient to provide a large enough snoop filter for the powered on cores' caches. You can use this field to disable the mechanism, however having enough snoop filter capacity is important for performance.
  - HSLCMASK, OSLCMASK, HSLCCNT, OSLCCNT. You can use these fields to guarantee a minimum slice operating mode when a certain number of specific cores is on.
- Software running on the core sets IMP\_CLUSTERPWRCTLR\_EL1.AUTOSLC to a non-zero value. Alternatively the SCP can program the CLUSTERPWRCTLR register through the utility bus.

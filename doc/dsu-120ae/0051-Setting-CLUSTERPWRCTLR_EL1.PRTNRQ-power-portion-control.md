# Setting CLUSTERPWRCTLR_EL1.PRTNRQ power portion control

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Setting-CLUSTERPWRCTLR-EL1-PRTNRQ-power-portion-control>

### Setting CLUSTERPWRCTLR\_EL1.PRTNRQ power portion control

Software running on the core can program CLUSTERPWRCTLR\_EL1.PRTNRQ to directly control the L3 cache power portion power requests.

### About this task

To enable CLUSTERPWRCTLR\_EL1.PRTNRQ L3 cache power portion control:

### Procedure

1. The System Control Processor (SCP) programs the Power Policy Units (PPUs) for dynamic operating mode transitions.
2. Software running on the core sets CLUSTERPWRCTLR\_EL1.AUTOPRTN = 0.
3. Software running on the core sets the cache power portion requests by programming the CLUSTERPWRCTLR\_EL1.PRTNRQ.

   To assist firmware in calculating L3 cache requirements, the cluster L3 cache hit and miss performance counters (IMP\_CLUSTERL3HIT\_EL1, IMP\_CLUSTERL3MISS\_EL1) are directly accessible from the
   cores.

### Results

This generates automatic cache
power portion requests that are translated to an internal PACTIVE indicator between the cluster and the cluster PPU. The cluster PPU responds accordingly to these requests.

# Setting automatic L3 cache power portion control

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Setting-automatic-L3-cache-power-portion-control>

### Setting automatic L3 cache power portion control

The DSU-120AE contains hardware to automatically schedule L3 cache power portion requests based on hit and miss counts. The cluster uses the L3 cache hit and miss rates to try to balance the leakage savings from powering down the cache with the energy cost of DRAM accesses.

### About this task

To enable automatic L3 cache power portion control:

### Procedure

1. The System Control Processor (SCP) programs the Power Policy Units (PPUs) for dynamic transitions.
2. Software running on the core sets the threshold registers. Alternatively the SCP can program the threshold registers through the utility bus.

   The threshold registers (AArch64 and External versions) are:

   - IMP\_CLUSTERL3DNTH0\_EL1, CLUSTERL3DNTH0
   - IMP\_CLUSTERL3DNTH1\_EL1, CLUSTERL3DNTH1
   - IMP\_CLUSTERL3UPTH0\_EL1, CLUSTERL3UPTH0
   - IMP\_CLUSTERL3UPTH1\_EL1, CLUSTERL3UPTH1
   - IMP\_CLUSTERL3UPTH2\_EL1, CLUSTERL3UPTH2
     > ### Note
     >
     > This register is only for use in conjunction with automated slice powerdown. See
     > [Automated slice powerdown](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-slice-powerdown/Automated-slice-powerdown?lang=en "This feature provides more hardware automation of the slice powerdown decision.").

   See [Calculating values for threshold registers](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Calculating-values-for-threshold-registers?lang=en "The DSU-120AE has hardware to automatically monitor the cache hit and miss rates and to schedule L3 cache power portion power requests based on these metrics. To use this hardware, Arm recommends suitable values are programmed into the threshold registers.") for information about calculating suitable values for these registers.
3. Software running on the core sets IMP\_CLUSTERPWRCTLR\_EL1.AUTOPRTN to a nonzero value. Alternatively the SCP can program the CLUSTERPWRCTLR register through the utility bus.

### Results

This generates automatic cache
power portion requests that are translated to an internal PACTIVE indicator between the cluster and the cluster PPU. The cluster PPU responds accordingly to these requests.

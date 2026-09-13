# Calculating values for threshold registers

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown/Calculating-values-for-threshold-registers>

### Calculating values for threshold registers

The DSU-120AE has hardware to automatically monitor the cache hit and miss rates and to schedule L3 cache power portion power requests based on these metrics. To use this hardware, Arm recommends suitable values are programmed into the threshold registers.

When an access misses in the cache, then it must access DRAM through the system interconnect to fetch the data. The energy cost of this DRAM access is much greater than the energy cost of an L3 access. Therefore, it is more energy-efficient for an access to hit in the L3 cache. However, the L3 RAMs consume leakage power even when the L3 is not accessed. Some workloads do not cache well and therefore have a high L3 miss rate. Other workloads might fit mostly in L1 and L2 caches, and therefore make very few L3 accesses. In both cases, the cost of the L3 leakage power might be greater than the cost of any additional DRAM accesses.

The hardware periodically calculates the hit and miss rates, based on the setting in the IMP\_CLUSTERPWRCTLR\_EL1.AUTOPRTN register. The period is configurable and depends on the frequency implemented for the architectural generic timer in the system. Setting a shorter time period allows better responsiveness to changing workloads. However, if it is too short then the cost of frequently resizing the cache might be too high.

The hardware contains internal copies of the IMP\_CLUSTERL3HIT\_EL1 and IMP\_CLUSTERL3MISS\_EL1 registers that count the same events. At the end of each time period, the value in these internal counter registers are compared against the values programmed in the threshold registers:

- IMP\_CLUSTERL3DNTH0\_EL1, CLUSTERL3DNTH0
- IMP\_CLUSTERL3DNTH1\_EL1, CLUSTERL3DNTH1
- IMP\_CLUSTERL3UPTH0\_EL1, CLUSTERL3UPTH0
- IMP\_CLUSTERL3UPTH1\_EL1, CLUSTERL3UPTH1
- IMP\_CLUSTERL3UPTH2\_EL1, CLUSTERL3UPTH2

After the calculations are complete, the internal version of the IMP\_CLUSTERL3HIT\_EL1 and IMP\_CLUSTERL3MISS\_EL1 registers are reset to zero. Depending on the number of L3 cache ways powered up, and the values in the hit and miss registers, and threshold registers, the following happens:

- If all L3 cache ways are powered up, then when IMP\_CLUSTERL3HIT\_EL1 is less than IMP\_CLUSTERL3DNTH0\_EL1, the cluster signals to the cluster Power Policy Unit (PPU) that it should request a power down of half of the ways of the L3 cache.
- - If half of the L3 cache ways are powered, then:

    - When IMP\_CLUSTERL3HIT\_EL1 is less than IMP\_CLUSTERL3DNTH1\_EL1 and IMP\_CLUSTERL3MISS\_EL1 is less than IMP\_CLUSTERL3UPTH1\_EL1, the cluster signals to the cluster PPU that it should request a power down of all the L3 cache ways.
    - When IMP\_CLUSTERL3MISS\_EL1 is greater than IMP\_CLUSTERL3UPTH1\_EL1 and IMP\_CLUSTERL3HIT\_EL1 is greater than IMP\_CLUSTERL3DNTH1\_EL1, the cluster signals to the cluster PPU that it should request a power up of all the L3 cache ways.
  - If no L3 cache ways are powered, then when IMP\_CLUSTERL3MISS\_EL1 is greater than IMP\_CLUSTERL3UPTH0\_EL1, the cluster requests to the cluster PPU to power up half the ways of the L3 cache.

Arm strongly recommends that the threshold registers are programmed before enabling the automatic control. The optimum values to program the threshold registers depend on the system characteristics. The recommended set of values shown below and are based on having no system cache. Therefore, every L3 miss requires a DRAM access. These values require the following information:

L is the leakage power (in mW) of all the L3 cache RAMs
:   This is the L3 tag RAMs and the L3 data RAMs for all ways.

D is the energy (in mJ) required to read 1MB of data from DRAM
:   While the interconnect will use some energy to transport the request to the DRAM controller, this is typically small compared to the energy used in the DRAM. Therefore,
    Arm recommends that this value uses just the energy consumed by the DRAM itself. If the DRAM datasheet gives the energy required for a single access, then this value must be multiplied by the number of accesses required to read 1MB of data.

T is the time period (in seconds) that is programmed into the IMP\_CLUSTERPWRCTLR\_EL1.AUTOPRTN register
:   ```
    IMP_CLUSTERL3DNTH0_EL1 = 12288 * T * L / D
    IMP_CLUSTERL3DNTH1_EL1 = 4096 * T * L / D
    IMP_CLUSTERL3UPTH0_EL1 = 4096 * T * L / D
    IMP_CLUSTERL3UPTH1_EL1 = 4096 * T * L / D
    IMP_CLUSTERL3UPTH2_EL1 = 24576 * T * L / D
    ```

# Power management in the DSU-120AE

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Power-management-in-the-DSU-120AE-->

### Power management in the DSU-120AE

The DynamIQ Shared Unit-120AE (DSU-120AE) provides various mechanisms to control both dynamic and static power dissipation. These mechanisms are associated with a set of power domains, power modes, and operational modes. Some of these mechanisms are brought under software control using Power Policy Units (PPUs).

The power management techniques employed by the DSU-120AE and cores in the cluster include:

- Internal core clock gating where different internal parts of the core are clock idle
- Per-core-pair Dynamic Voltage and Frequency Scaling (DVFS)

- Powerdown of components of the cluster which can include:

  - Cores
  - All the L3 cache or parts of the L3 cache. See [L3 cache RAM powerdown](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-powerdown?lang=en "The L3 cache RAMs typically contribute to a large proportion of the total leakage power, particularly for large cache sizes. Therefore, it is beneficial to power down the RAMs when only some of the L3 cache is required, but it also results in reducing cache capacity. Parts of the L3 cache RAM can be independently powered down to reduce RAM leakage power when not in use. L3 cache powerdown is controlled by the cluster Power Policy Unit (PPU).") and [L3 cache slice powerdown](/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-slice-powerdown?lang=en "In addition to powering down the L3 cache RAMs, you can gain further leakage savings by powering down some of the L3 cache slice control logic as well. Control of powering up or powering down L3 cache slices is performed by the cluster Power Policy Unit (PPU).").
- Retention which is a low-power mode that retains the register and RAM state. Retention can be applied to the following components of the cluster:
  - Cache RAMs in the cores
  - All of the L3 cache or parts of the L3 cache

> ### Note
>
> - The DSU-120AE power domain architecture, power modes, and operational modes, are based on the Arm Power Control System Architecture, see [Arm® Power Control System Architecture](https://developer.arm.com/documentation/den0050/latest/).
> - This chapter does not describe how to use the PPUs for the cluster or the cores, see instead [Power and reset control with Power Policy Units](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units?lang=en "This chapter describes how to control the power mode and reset behavior for the DSU-120AE DynamIQ cluster, cores, and complexes using the Power Policy Units (PPUs).").

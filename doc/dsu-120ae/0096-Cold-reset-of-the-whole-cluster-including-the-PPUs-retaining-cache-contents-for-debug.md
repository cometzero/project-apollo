# Cold reset of the whole cluster, including the PPUs, retaining cache contents for debug

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Cold-reset-of-the-whole-cluster--including-the-PPUs--retaining-cache-contents-for-debug>

### Cold reset of the whole cluster, including the PPUs, retaining cache contents for debug

To provide a Cold reset to the whole cluster, including the Power Policy Units (PPUs) but retaining all cache contents for debug, use the following method.

### About this task

> ### Note
>
> - This method is only suitable for configurations with the `PPU_RST_STATE` configuration parameter set to FALSE. For more information on the build-time configuration parameters, see section hayden.yaml configuration parameters in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
> - Because this method resets the PPUs, the Power Control State Machine (PCSM) interfaces are also reset to the Off power mode. Therefore, you must ensure that your implemented PCSM logic must be aware of this sequence and not remove power during this period.
> - Because the WARM\_RST and DBG\_RECOV power modes do not wait for transactions to reach a quiescent state before entry, the cluster might be in any power state. Any external component that is communicating with the power domains being reset, for example the system interconnect, must also be reset to ensure any outstanding transactions are terminated. If there is a power transition or a clock gating transition in progress at the time, then the transition might depend on other transactions completing. Therefore, this can prevent the completion of the power or clock transition which in turn can prevent the entry into WARM\_RST or DBG\_RECOV mode.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

### Procedure

1. Ensure that the cluster is in On mode and the cores are either in On mode, Off mode, or Emulated off mode. Read the PPU\_PWSR for the cluster to determine the current cluster operating mode.
2. Drive the signal nRESET LOW for a minimum of ten PPUCLK cycles.
3. For each of the cores, either leave them in the OFF power mode, or change them to DBG\_RECOV power mode by writing to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x0000000A.
4. Write to the cluster PPU\_PWPR, address 0x030000, value 0x0000000A. This sets the cluster to the DBG\_RECOV power mode.
5. Write to the cluster PPU\_PWPR, address 0x030000, value 0x000<p>0008, where <p> is the operating mode value read in step 1. This sets the cluster to the ON power mode.
6. For each core, write to the core PPU\_PWPR register, for core <y>, address 0x<y>80000, value 0x00000008. This puts each core back to the ON power mode.

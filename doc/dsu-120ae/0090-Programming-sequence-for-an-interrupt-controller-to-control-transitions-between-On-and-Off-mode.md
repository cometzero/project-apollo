# Programming sequence for an interrupt controller to control transitions between On and Off mode

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-for-an-interrupt-controller-to-control-transitions-between-On-and-Off-mode>

### Programming sequence for an interrupt controller to control transitions between On and Off mode

Use the following steps to program the Power Policy Units (PPUs) for the DSU-120AE DynamIQ™ cluster and each of the cores to power up the cluster and cores when the signal  COREWAKEREQUEST[<y>] is asserted, and to power down automatically when software has finished running on the cores.

### About this task

This task is using the PPU dynamic policy to request automatic transitions.

> ### Note
>
> - In this task, <y> is the core instance number.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

### Procedure

1. Write to the cluster PPU\_PWPR register, address 0x030000, value 0x01000100.

   This sets the dynamic power mode policy and the dynamic operating mode policy, with a minimum power mode of Off.
2. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x00000100.

   This sets the dynamic power mode policy, with a minimum power mode of Off.
3. To power up or power down core <y>.

   - To power up core <y>, assert the COREWAKEREQUEST[<y>] signal.
   - To power down core <y>:
     - Software on the core sets the IMP\_CPUPWRCTLR\_EL1.CORE\_PWRDN\_EN bit to 1, then executes a `WFI` instruction.
     - After all cores are powered down, the cluster powers down automatically, unless the IMP\_CLUSTERPWRDN\_EL1.PWRDN=1 or IMP\_CLUSTERPWRDN\_EL1.MEMRET=1.
   > ### Note
   >
   > - The signal COREWAKEREQUEST[<y>] is level sensitive.
   > - The upper limit for the range of power modes is On. The upper limit for the range of cluster operating modes is All slices mode and all RAM instances are active.

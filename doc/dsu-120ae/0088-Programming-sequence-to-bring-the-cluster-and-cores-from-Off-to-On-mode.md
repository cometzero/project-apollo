# Programming sequence to bring the cluster and cores from Off to On mode

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-to-bring-the-cluster-and-cores-from-Off-to-On-mode>

### Programming sequence to bring the cluster and cores from Off to On mode

Use the following steps, to program the Power Policy Unit (PPU) for the DSU-120AE DynamIQ™ cluster and each of the cores to request a change of PPU mode from Off mode to On mode.

### About this task

This task is using the PPU static policy to request a single mode transition. You can use it as a simple example for initial powerup or debug. However, for normal use cases, see [Programming sequence for an interrupt controller to control transitions between On and Off mode](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-for-an-interrupt-controller-to-control-transitions-between-On-and-Off-mode?lang=en "Use the following steps to program the Power Policy Units (PPUs) for the DSU-120AE DynamIQ cluster and each of the cores to power up the cluster and cores when the signal COREWAKEREQUEST[<y>] is asserted, and to power down automatically when software has finished running on the cores.").

> ### Note
>
> - Steps 2 and 4 are only required if you need to know when the power transition has completed. Otherwise they can be omitted.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.
> - This example programs the cluster power mode before the core power mode. It is possible to program the core power mode before the cluster power mode. However, the power mode transition of the core will not happen, and the cores will not reach the On power mode, until after the cluster has reached the On power mode.
> - In this task, <y> is the core instance number.

### Procedure

1. Write to the cluster register PPU\_PWPR, address 0x030000, value 0x00070008.

   This sets the static power mode policy to ON and the static operating mode policy to ALL SLICE FULL RAM.
2. Poll the cluster PPU\_PWSR register, address 0x030008, until the value read matches the value written to the PPU\_PWPR register.
3. Write to the core PPU\_PWPR register, for core <y>, address 0x<y>80000, value 0x00000008. This sets the static power mode policy to ON.
4. Poll the core PPU\_PWSR register for core <y>, address 0x<y>80008, until the value read matches the value written to the PPU\_PWPR register.

# Programming sequence to bring the cluster and cores from On to Off mode

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-to-bring-the-cluster-and-cores-from-On-to-Off-mode>

### Programming sequence to bring the cluster and cores from On to Off mode

Use the following steps, to program the Power Policy Unit (PPU) for the DSU-120AE DynamIQ™ cluster and each of the cores to request a change of PPU mode from On to Off.

### About this task

This task is using the PPU static policy to request a single mode transition.

> ### Note
>
> - In this task, <y> is the core instance number.
> - Steps 3 and 5 are only required if you must know when the power transition has completed. Otherwise they can be omitted.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

### Procedure

1. Ensure your software running on the core sets the IMP\_CPUPWRCTLR\_EL1.CORE\_PWRDN\_EN bit to 1, then executes a `WFI` instruction.

   If the component programming the PPU needs to know when the software has completed this step, it can read the PPU\_DISR.PWR\_DEVACTIVE\_STATUS field, or set the interrupt to occur when this action takes place. This field reads zero when the
   core is ready to powerdown.
2. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x00000000.

   This sets the static power mode policy to OFF.
3. Poll the core PPU\_PWSR register for core <y>, address 0x<y>80008, until the value read matches the value written to the PPU\_PWPR register.
4. Write to the cluster PPU\_PWPR register, address 0x030000, value 0x00000000.

   This sets the static power mode policy to OFF.
5. Poll the cluster PPU\_PWSR register, address 0x030008, until the value read matches the value written to the PPU\_PWPR register.

# Core software initiated Cold or Warm reset of the cluster, excluding the PPUs

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Core-software-initiated-Cold-or-Warm-reset-of-the-cluster--excluding-the-PPUs>

### Core software initiated Cold or Warm reset of the cluster, excluding the PPUs

To reset the cores and cluster, not including the Power Policy Units (PPUs), follow the sequence below. For a Cold reset program, the PPUs to Off power mode. For a Warm reset, program the PPUs to Emulated Off power mode.

### About this task

For the Cold reset case, power is also removed from the cluster during this sequence.

> ### Note
>
> If the
> DSU-120AE is configured for
> Lock-configuration or
> Mixed-configuration (including
> Split-mode) then each time before writing to a PPU register, you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address
> 0x050060, value
> 0x0000\_0000\_0000\_00BA. If the
> DSU-120AE is configured for
> Split-configuration, then this step is not-required.

### Procedure

1. Use software running on each core to set the IMP\_CPUPWRCTLR\_EL1.CORE\_PWRDN\_EN bit.
2. Use software running on each core to execute a `WFI` instruction.
3. Program the Power Policy Unit (PPU) for each core to Off mode (Cold reset) or Emulated off mode (Warm reset).
4. Program the PPU for the cluster to Off power mode or Emulated off mode.

   > ### Note
   >
   > The cluster Off mode can only be entered if the
   > cores are in Off mode.
5. Program the PPU for the cluster to On power mode.
6. For each of the cores, program their corresponding PPU to On power mode.

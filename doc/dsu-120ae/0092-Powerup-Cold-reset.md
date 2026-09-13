# Powerup (Cold) reset

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Powerup--Cold--reset>

### Powerup (Cold) reset

This reset must be done the first time that the cluster is powered up. It resets parts of the DynamIQ Shared Unit-120AE (DSU-120AE) including the Power Policy Units (PPUs).

### Procedure

1. Assert the nRESET signal for a minimum of ten PPUCLK cycles.
2. Deassert the nRESET signal.
3. Program the PPU for the cluster to On power mode, see [Programming sequence to bring the cluster and cores from Off to On mode](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-to-bring-the-cluster-and-cores-from-Off-to-On-mode?lang=en "Use the following steps, to program the Power Policy Unit (PPU) for the DSU-120AE DynamIQ cluster and each of the cores to request a change of PPU mode from Off mode to On mode.").
4. Program the PPU for each required core to On power mode, see [Programming sequence to bring the cluster and cores from Off to On mode](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Programming-sequences-for-the-cluster-and-the-core/Programming-sequence-to-bring-the-cluster-and-cores-from-Off-to-On-mode?lang=en "Use the following steps, to program the Power Policy Unit (PPU) for the DSU-120AE DynamIQ cluster and each of the cores to request a change of PPU mode from Off mode to On mode.").

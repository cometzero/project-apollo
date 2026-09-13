# Core software initiated Warm reset of an individual core

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Core-software-initiated-Warm-reset-of-an-individual-core>

### Core software initiated Warm reset of an individual core

Software running on a core in the cluster can use the Reset Management Register (RMR) to program a core to Warm reset. This mechanism was provided to switch between execution states, however all cores in this generation only support a single execution state, AArch64. Therefore, Arm recommends that this mechanism is not used as it may be removed in future generations.

### About this task

The core RMR register bit field RR (RMR.RR) can be used by software to request a Warm reset of a core independent of the Power Policy Unit (PPU) control. However, an interrupt, debug access, or an Error Correcting Code (ECC) error detected during the automatic cache clean triggered by the reset request can prevent the Warm reset from being asserted.

If software requires the use of RMR.RR then the following actions must be taken to ensure the reset completes:

### Procedure

1. Ensure that ECC fault detection is disabled before writing to the RMR.RR register bit field.
2. The core software must use the following the code sequence to guarantee the request for Warm reset.

   ```
   ; In addition, interrupts and debug requests for the PE should be disabled
   ; in the system before running this sequence to ensure the WFI suspends execution,
         MOV Wy, #3 ; y is any register
         DSB ; ensure all stores etc are complete
         MSR RMR_ELx, Wy ; request the reset
         ISB ; synchronize change to the RMR
   Loop
         WFI ; enter a quiescent state
         B Loop
   ```

   See [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487/latest/), Issue K, section D 1.5.2 Reset types, Rule: RSGXSW for more information.

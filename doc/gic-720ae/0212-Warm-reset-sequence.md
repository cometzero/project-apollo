# Warm reset sequence

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Resets/Warm-reset-sequence>

### Warm reset sequence

Follow these steps to initiate a Warm reset of the GIC.

### About this task

A Warm reset is a reset that occurs after the component has already been operating for some time. A Warm reset preserves the state of the PMU and the FMU error records, in both the functional and FuSa GIC address maps. This state preservation is accomplished by not toggling the
dbg\_reset\_n signals.
 Before resetting a GIC block, the quiescing procedure must be followed for the block being reset. This procedure ensures that the reset can be performed cleanly.

### Procedure

1. Assert the reset\_n and reset\_n\_chk signals simultaneously.

   The resynchronized reset signals,
   reset\_n\_pri and
   reset\_n\_sec, assert asynchronously at the same time.
2. Keep the resets asserted for at least 3 cycles more than the number of stages in the reset synchronizer.

   Step result: This reset assertion duration guarantees a reset flush through the non-resettable flops.
3. Release the resets.

   When either the
   reset\_n or
   reset\_n\_chk signal deasserts, the
   reset\_n\_pri signal deasserts synchronously, followed by the
   reset\_n\_sec signal two
   clk cycles later.

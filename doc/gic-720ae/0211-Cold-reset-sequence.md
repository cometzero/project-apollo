# Cold reset sequence

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Resets/Cold-reset-sequence>

### Cold reset sequence

Follow these steps to initiate a Cold reset of the GIC.

### Procedure

1. Assert either reset\_n and reset\_n\_chk, or dbg\_reset\_n and dbg\_reset\_n\_chk signals simultaneously.

   - The post-synchronizer reset signals, reset\_n\_pri and reset\_n\_sec, assert asynchronously at the same time.
2. Keep the resets asserted for at least 3 cycles more than the number of stages in the reset synchronizer.

   Step result: This reset assertion guarantees a reset flush through the non-resettable flops.
3. Release the resets.

   When either:
   - The reset\_n or reset\_n\_chk signal deasserts, the reset\_n\_pri signal deasserts synchronously, followed by the reset\_n\_sec signal two clk cycles later. reset\_n and reset\_n\_chk signals deassert at the same time.
   - The dbg\_reset\_n or dbg\_reset\_n\_chk signal deasserts, the dbg\_reset\_n\_pri signal deasserts synchronously, followed by the dbg\_reset\_n\_sec signal two clk cycles later. dbg\_reset\_n and dbg\_reset\_n\_chk signals deassert at the same time.

# Cold reset sequence

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Resets/Cold-reset-sequence>

### Cold reset sequence

Follow these steps to initiate a Cold reset of MHU-320AE.

### Procedure

1. Assert reset\_n and reset\_n\_chk simultaneously.

   The post-synchronizer reset signals, reset\_n\_pri and reset\_n\_sec, assert asynchronously at the same time.
2. Keep the resets asserted for at least 3 cycles more than the number of stages in the reset synchronizer. This reset assertion guarantees a reset flush through the non-resettable flops.
3. Release the resets.

   When the reset\_n or reset\_n\_chk signal deasserts, the reset\_n\_pri signal deasserts synchronously, followed by the reset\_n\_sec signal two clk cycles later. reset\_n and reset\_n\_chk signals deassert at the same time. .

# System Timer operation

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-Timer-overview/System-Timer-operation>

### System Timer operation

The primary function of the System Timer is to generate an interrupt output that is based on the Timer configuration and interrupt mask setting.

The timers can be programmed to count:

- Up to a threshold, by programming a CompareValue (CNTP\_CVAL).
- Down from a programmed value, by programming a TimerValue (CNTP\_TVAL).

The basic function of the System Timer is:

`TimerCondMet = Counter[63:0] – CompareValue[63:0] >= 0`

An alternative 32‑bit view, called TimerValue, can be used to set the CompareValue as follows:

`CompareValue = (Counter[63:0] + SignExtend(TimerValue)[63:0]`

Reading the TimerValue gives the count down value:

`TimerValue = (CompareValue[31:0] – Counter [31:0]`

The auto‑increment feature allows generation of Timer interrupt at regular intervals without the need for reprogramming the Timer after each interrupt and re-enabling the timer logic.

The Automatic Increment timer view operates as a 64‑bit up‑counter. An AutoIncrValue Reload register is programmed with a 32‑bit offset. If the EN bit of the AutoIncrValue Control register is set, the offset value is zero‑extended, summed with the count value, and loaded into the AutoIncrValue register, performed automatically by hardware.

The operation of auto‑increment is as follows:

`AutoIncrValue = (ZeroExtend(Reload[31:0])[63:0] + Counter[63:0])`

where:

`TimerCondMet TRUE` : If the timer condition is met.

`TimerCondMet FALSE` : Otherwise.

When the timer condition is met:

- An interrupt is generated, if the interrupt is not masked in the timer control register, and remains asserted until software clears it by writing to the CLR bit of the AutoIncrValue Control register, CNTP\_AIVAL\_CTL).
- The CLR bit in the AutoIncrValue Control register is set to 1 and it remains 1 until software clears it by writing ‘0’.
- The AutoIncrValue register is reloaded with the new value.

When the auto‑increment feature is enabled, the operation of normal timer, using the compare value or timer value registers, is disabled. This is to ensure that when the interrupt is generated, the cause of interrupt is unambiguous to the user.

The auto-increment timer starts counting only when both the Timer is enabled (CNTP\_CTL.ENABLE=1) and auto‑increment mode is enabled by setting CNTP\_AIVAL\_CTL.EN=1. When both are enabled, the Timer starts counting down until the AIVAL\_RELOAD period is reached.

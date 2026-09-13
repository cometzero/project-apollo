# ​0x4012, TRCEXTOUT2, Trace unit external output 2

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4012--TRCEXTOUT2--Trace-unit-external-output-2>

##### `0x4012`, TRCEXTOUT2, Trace unit external output 2

The counter counts each event signaled by the trace unit on external event 2.

It is IMPLEMENTATION DEFINED whether this event is available as an external input to the ETE.

PMCEID0\_EL0[50] reads as 1 if this event is implemented and 0 otherwise.

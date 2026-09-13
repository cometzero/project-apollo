# ​0x4010, TRCEXTOUT0, Trace unit external output 0

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4010--TRCEXTOUT0--Trace-unit-external-output-0>

##### `0x4010`, TRCEXTOUT0, Trace unit external output 0

The counter counts each event signaled by the trace unit on external event 0.

It is IMPLEMENTATION DEFINED whether this event is available as an external input to the ETE.

PMCEID0\_EL0[48] reads as 1 if this event is implemented and 0 otherwise.

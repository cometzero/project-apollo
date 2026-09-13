# ​0x400E, TRB_TRIG, Trace buffer Trigger Event

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x400E--TRB-TRIG--Trace-buffer-Trigger-Event>

##### `0x400E`, TRB\_TRIG, Trace buffer Trigger Event

The counter counts each trace buffer Trigger Event.

It is IMPLEMENTATION DEFINED whether this event can be counted by the PMU.

PMCEID0\_EL0[46] reads as 1 if this event is implemented and can be counted by the PMU, and 0 otherwise.

# ​0x400C, TRB_WRAP, Trace buffer current write pointer wrapped

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x400C--TRB-WRAP--Trace-buffer-current-write-pointer-wrapped>

##### `0x400C`, TRB\_WRAP, Trace buffer current write pointer wrapped

The counter counts each write made by the Trace Buffer Unit to the trace buffer that causes the trace buffer current write pointer to wrap to the trace buffer base pointer.

PMCEID0\_EL0[44] reads as 1 if this event is implemented and 0 otherwise.

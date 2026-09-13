# ​0x0083, EXC_PABORT, Exception taken, Instruction Abort

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0083--EXC-PABORT--Exception-taken--Instruction-Abort>

##### `0x0083`, EXC\_PABORT, Exception taken, Instruction Abort

The counter counts each Instruction Abort exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

It is IMPLEMENTATION SPECIFIC whether the counter counts each entry to Debug state due to a Breakpoint debug event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

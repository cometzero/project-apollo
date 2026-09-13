# ​0x0084, EXC_DABORT, Exception taken, Data Abort or SError

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0084--EXC-DABORT--Exception-taken--Data-Abort-or-SError>

##### `0x0084`, EXC\_DABORT, Exception taken, Data Abort or SError

The counter counts each Guarded control stack Data Check Exception, Data Abort, SError interrupt, or virtual SError interrupt exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

It is IMPLEMENTATION SPECIFIC whether the counter counts each entry to Debug state due to a Watchpoint debug event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

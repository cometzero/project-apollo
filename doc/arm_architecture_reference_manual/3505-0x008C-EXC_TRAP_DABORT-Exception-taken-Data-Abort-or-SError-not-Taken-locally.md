# ​0x008C, EXC_TRAP_DABORT, Exception taken, Data Abort or SError not Taken locally

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x008C--EXC-TRAP-DABORT--Exception-taken--Data-Abort-or-SError-not-Taken-locally>

##### `0x008C`, EXC\_TRAP\_DABORT, Exception taken, Data Abort or SError not Taken locally

The counter counts each Guarded control stack Data Check Exception, Data Abort, SError interrupt, or virtual SError interrupt exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken), that is not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

# ​0x0082, EXC_SVC, Exception taken, Supervisor Call

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0082--EXC-SVC--Exception-taken--Supervisor-Call>

##### `0x0082`, EXC\_SVC, Exception taken, Supervisor Call

The counter counts each Supervisor Call exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

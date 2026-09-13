# ​0x0087, EXC_FIQ, Exception taken, FIQ

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0087--EXC-FIQ--Exception-taken--FIQ>

##### `0x0087`, EXC\_FIQ, Exception taken, FIQ

The counter counts each FIQ or virtual FIQ exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

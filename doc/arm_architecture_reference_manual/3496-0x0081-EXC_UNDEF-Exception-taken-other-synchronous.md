# ​0x0081, EXC_UNDEF, Exception taken, other synchronous

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0081--EXC-UNDEF--Exception-taken--other-synchronous>

##### `0x0081`, EXC\_UNDEF, Exception taken, other synchronous

The counter counts each exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) and is not counted as any of the following:

- Exception taken, Supervisor Call (EXC\_SVC).
- Exception taken, Secure Monitor Call (EXC\_SMC).
- Exception taken, Hypervisor Call (EXC\_HVC).
- Exception taken, IRQ (EXC\_IRQ).
- Exception taken, FIQ (EXC\_FIQ).

It is IMPLEMENTATION SPECIFIC whether the counter counts each entry to Debug state not counted by either of the following:

- Exception taken, Instruction Abort (EXC\_PABORT).
- Exception taken, Data Abort or SError (EXC\_DABORT).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

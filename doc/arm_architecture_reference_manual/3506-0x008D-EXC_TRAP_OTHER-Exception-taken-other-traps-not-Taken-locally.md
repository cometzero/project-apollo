# ​0x008D, EXC_TRAP_OTHER, Exception taken, other traps not Taken locally

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x008D--EXC-TRAP-OTHER--Exception-taken--other-traps-not-Taken-locally>

##### `0x008D`, EXC\_TRAP\_OTHER, Exception taken, other traps not Taken locally

The counter counts each exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) and not counted as any of the following:

- Exception taken, Secure Monitor Call (EXC\_SMC).
- Exception taken, Hypervisor Call (EXC\_HVC).
- Exception taken, Instruction Abort not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) (EXC\_TRAP\_PABORT).
- Exception taken, Data Abort or SError not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) (EXC\_TRAP\_DABORT).
- Exception taken, IRQ not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) (EXC\_TRAP\_IRQ).
- Exception taken, FIQ not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj) (EXC\_TRAP\_FIQ).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

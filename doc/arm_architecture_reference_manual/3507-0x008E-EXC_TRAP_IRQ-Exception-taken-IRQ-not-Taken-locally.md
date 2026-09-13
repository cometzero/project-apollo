# ​0x008E, EXC_TRAP_IRQ, Exception taken, IRQ not Taken locally

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x008E--EXC-TRAP-IRQ--Exception-taken--IRQ-not-Taken-locally>

##### `0x008E`, EXC\_TRAP\_IRQ, Exception taken, IRQ not Taken locally

The counter counts each IRQ or virtual IRQ exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken) that is not [Taken locally](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cbadbfcj).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

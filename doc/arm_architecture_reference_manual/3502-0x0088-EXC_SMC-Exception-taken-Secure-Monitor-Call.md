# ​0x0088, EXC_SMC, Exception taken, Secure Monitor Call

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0088--EXC-SMC--Exception-taken--Secure-Monitor-Call>

##### `0x0088`, EXC\_SMC, Exception taken, Secure Monitor Call

The counter counts each Secure Monitor Call exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken).

The counter does not count SMC instructions that generate other exceptions, including Trap exceptions and Undefined Instruction exceptions.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

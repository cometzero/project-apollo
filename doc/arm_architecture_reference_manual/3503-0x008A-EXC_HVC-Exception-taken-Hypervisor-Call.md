# ​0x008A, EXC_HVC, Exception taken, Hypervisor Call

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x008A--EXC-HVC--Exception-taken--Hypervisor-Call>

##### `0x008A`, EXC\_HVC, Exception taken, Hypervisor Call

The counter counts each Hypervisor Call exception counted by [EXC\_TAKEN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken?lang=en#event_exc_taken).

The counter does not count HVC instructions that are UNDEFINED.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

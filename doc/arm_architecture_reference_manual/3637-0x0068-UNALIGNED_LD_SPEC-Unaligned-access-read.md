# ​0x0068, UNALIGNED_LD_SPEC, Unaligned access, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0068--UNALIGNED-LD-SPEC--Unaligned-access--read>

##### `0x0068`, UNALIGNED\_LD\_SPEC, Unaligned access, read

The counter counts each unaligned access counted by [UNALIGNED\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006A--UNALIGNED-LDST-SPEC--Unaligned-access?lang=en#event_unaligned_ldst_spec) that is a [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega).

The unaligned access is counted even if it is subsequently transformed into multiple aligned accesses.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

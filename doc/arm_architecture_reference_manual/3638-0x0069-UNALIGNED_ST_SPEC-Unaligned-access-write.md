# ​0x0069, UNALIGNED_ST_SPEC, Unaligned access, write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0069--UNALIGNED-ST-SPEC--Unaligned-access--write>

##### `0x0069`, UNALIGNED\_ST\_SPEC, Unaligned access, write

The counter counts each unaligned access counted by [UNALIGNED\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006A--UNALIGNED-LDST-SPEC--Unaligned-access?lang=en#event_unaligned_ldst_spec) that is a [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

The unaligned access is counted even if it is subsequently transformed into multiple aligned accesses.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

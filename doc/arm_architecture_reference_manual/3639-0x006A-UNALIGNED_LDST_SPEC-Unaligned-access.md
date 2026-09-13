# ​0x006A, UNALIGNED_LDST_SPEC, Unaligned access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006A--UNALIGNED-LDST-SPEC--Unaligned-access>

##### `0x006A`, UNALIGNED\_LDST\_SPEC, Unaligned access

The counter counts each access counted by [MEM\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0013--MEM-ACCESS--Data-memory-access?lang=en#event_mem_access) that is an unaligned [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or unaligned [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

The unaligned access is counted even if it is subsequently transformed into multiple aligned accesses.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

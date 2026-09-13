# ​0x0091, RC_ST_SPEC, Release consistency operation speculatively executed, Store-Release

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0091--RC-ST-SPEC--Release-consistency-operation-speculatively-executed--Store-Release>

##### `0x0091`, RC\_ST\_SPEC, Release consistency operation speculatively executed, Store-Release

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) with release semantics.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

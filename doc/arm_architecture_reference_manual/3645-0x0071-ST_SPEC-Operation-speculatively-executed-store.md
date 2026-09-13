# ​0x0071, ST_SPEC, Operation speculatively executed, store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0071--ST-SPEC--Operation-speculatively-executed--store>

##### `0x0071`, ST\_SPEC, Operation speculatively executed, store

The counter counts each operation counted by [LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0072--LDST-SPEC--Operation-speculatively-executed--load-or-store?lang=en#event_ldst_spec) that is a store operation.

Operations due to [Memory-writing instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) are counted as store operations.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.

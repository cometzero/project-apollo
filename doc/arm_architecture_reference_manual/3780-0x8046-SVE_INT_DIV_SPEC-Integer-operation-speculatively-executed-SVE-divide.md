# ​0x8046, SVE_INT_DIV_SPEC, Integer operation speculatively executed, SVE divide

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8046--SVE-INT-DIV-SPEC--Integer-operation-speculatively-executed--SVE-divide>

##### `0x8046`, SVE\_INT\_DIV\_SPEC, Integer operation speculatively executed, SVE divide

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer divide operation counted by [INT\_DIV\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8044--INT-DIV-SPEC--Integer-operation-speculatively-executed--divide?lang=en#event_int_div_spec) due to any of the following instructions:

- SVE: SDIV, SDIVR, UDIV, or UDIVR.

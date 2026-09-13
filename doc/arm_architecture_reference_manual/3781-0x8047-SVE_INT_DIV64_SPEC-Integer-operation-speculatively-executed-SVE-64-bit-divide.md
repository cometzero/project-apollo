# ​0x8047, SVE_INT_DIV64_SPEC, Integer operation speculatively executed, SVE 64-bit divide

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8047--SVE-INT-DIV64-SPEC--Integer-operation-speculatively-executed--SVE-64-bit-divide>

##### `0x8047`, SVE\_INT\_DIV64\_SPEC, Integer operation speculatively executed, SVE 64-bit divide

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer 64-bit divide operation counted by [INT\_DIV64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8045--INT-DIV64-SPEC--Integer-operation-speculatively-executed--64-bit-divide?lang=en#event_int_div64_spec) due to any of the following instructions:

- SVE: SDIV, SDIVR, UDIV, or UDIVR.

The counter only counts operations with 64-bit operands or vector elements.

# ​0x8045, INT_DIV64_SPEC, Integer operation speculatively executed, 64-bit divide

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8045--INT-DIV64-SPEC--Integer-operation-speculatively-executed--64-bit-divide>

##### `0x8045`, INT\_DIV64\_SPEC, Integer operation speculatively executed, 64-bit divide

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer divide operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to any of the following A64 instructions:

- Scalar: SDIV or UDIV.
- SVE: SDIV, SDIVR, UDIV, or UDIVR.

The counter only counts operations with 64-bit operands or vector elements.

# ​0x8089, BASE_LD_REG_SPEC, Operation speculatively executed, general-purpose register load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8089--BASE-LD-REG-SPEC--Operation-speculatively-executed--general-purpose-register-load>

##### `0x8089`, BASE\_LD\_REG\_SPEC, Operation speculatively executed, general-purpose register load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [BASE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8088--BASE-LDST-REG-SPEC--Operation-speculatively-executed--general-purpose-register-load--store--or-prefetch?lang=en#event_base_ldst_reg_spec) due to a general-purpose register load instruction.

It is IMPLEMENTATION DEFINED which load operations are counted in AArch32 state.

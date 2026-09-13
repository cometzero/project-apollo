# ​0x808B, BASE_PRF_SPEC, Operation speculatively executed, general-purpose register prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808B--BASE-PRF-SPEC--Operation-speculatively-executed--general-purpose-register-prefetch>

##### `0x808B`, BASE\_PRF\_SPEC, Operation speculatively executed, general-purpose register prefetch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) prefetch operation counted by [BASE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8088--BASE-LDST-REG-SPEC--Operation-speculatively-executed--general-purpose-register-load--store--or-prefetch?lang=en#event_base_ldst_reg_spec) due to any of the following A64 instructions:

- Scalar: PRFM, PRFUM, or RPRFM.

It is IMPLEMENTATION DEFINED which prefetch operations are counted in AArch32 state.

# ​0x8088, BASE_LDST_REG_SPEC, Operation speculatively executed, general-purpose register load, store, or prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8088--BASE-LDST-REG-SPEC--Operation-speculatively-executed--general-purpose-register-load--store--or-prefetch>

##### `0x8088`, BASE\_LDST\_REG\_SPEC, Operation speculatively executed, general-purpose register load, store, or prefetch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from or writes to memory due to a general-purpose register load, store, or prefetch instruction.

It is IMPLEMENTATION DEFINED which load, store, and prefetch operations are counted in AArch32 state.

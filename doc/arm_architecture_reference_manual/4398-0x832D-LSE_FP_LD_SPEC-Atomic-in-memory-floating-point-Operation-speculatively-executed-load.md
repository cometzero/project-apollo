# ​0x832D, LSE_FP_LD_SPEC, Atomic in-memory floating-point Operation speculatively executed, load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x832D--LSE-FP-LD-SPEC--Atomic-in-memory-floating-point-Operation-speculatively-executed--load>

##### `0x832D`, LSE\_FP\_LD\_SPEC, Atomic in-memory floating-point Operation speculatively executed, load

The counter counts each in-memory floating-point operation counted by [LSE\_FP\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x832F--LSE-FP-LDST-SPEC--Atomic-in-memory-floating-point-Operation-speculatively-executed--load-or-store?lang=en#event_lse_fp_ldst_spec) that atomically loads a value from memory, operates on that value, stores the result of the operation to memory, and writes the initially loaded value to a destination register.

This includes operations with acquire, release, and neither release nor acquire semantics.

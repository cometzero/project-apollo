# ​0x832F, LSE_FP_LDST_SPEC, Atomic in-memory floating-point Operation speculatively executed, load or store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x832F--LSE-FP-LDST-SPEC--Atomic-in-memory-floating-point-Operation-speculatively-executed--load-or-store>

##### `0x832F`, LSE\_FP\_LDST\_SPEC, Atomic in-memory floating-point Operation speculatively executed, load or store

The counter counts each in-memory floating-point operation counted by [LSE\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8177--LSE-LDST-SPEC--Atomic-memory-Operation-speculatively-executed--load-or-store?lang=en#event_lse_ldst_spec) that atomically loads a value from memory, operates on the value, and stores the result of the operation to memory.

This includes operations with acquire, release, and neither release nor acquire semantics.

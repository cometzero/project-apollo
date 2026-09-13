# ​0x8379, SE_INT_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing>

##### `0x8379`, SE\_INT\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer data-processing operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8041--ASE-INT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD?lang=en#event_ase_int_spec), [SVE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8042--SVE-INT-SPEC--Integer-operation-speculatively-executed--SVE?lang=en#event_sve_int_spec), or [SME\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8378--SME-INT-SPEC--Operation-speculatively-executed--SME-integer--data-processing?lang=en#event_sme_int_spec).

It is IMPLEMENTATION DEFINED which integer data-processing operations are counted in AArch32 state.

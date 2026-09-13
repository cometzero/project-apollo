# ​0x836D, SE_INT64_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 64-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x836D--SE-INT64-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-64-bit-integer--data-processing>

##### `0x836D`, SE\_INT64\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 64-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 64-bit integer data-processing operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_INT64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80ED--ASE-INT64-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-64-bit?lang=en#event_ase_int64_spec), [SVE\_INT64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80EE--SVE-INT64-SPEC--Integer-operation-speculatively-executed--SVE-64-bit?lang=en#event_sve_int64_spec), or [SME\_INT64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x836C--SME-INT64-SPEC--Operation-speculatively-executed--SME-64-bit-integer--data-processing?lang=en#event_sme_int64_spec).

It is IMPLEMENTATION DEFINED which 64-bit integer data-processing operations are counted in AArch32 state.

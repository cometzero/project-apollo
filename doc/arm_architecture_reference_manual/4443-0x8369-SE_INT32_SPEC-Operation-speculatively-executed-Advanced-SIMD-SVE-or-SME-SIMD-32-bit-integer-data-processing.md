# ​0x8369, SE_INT32_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 32-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8369--SE-INT32-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-32-bit-integer--data-processing>

##### `0x8369`, SE\_INT32\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 32-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 32-bit integer data-processing operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_INT32\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80E9--ASE-INT32-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-32-bit?lang=en#event_ase_int32_spec), [SVE\_INT32\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80EA--SVE-INT32-SPEC--Integer-operation-speculatively-executed--SVE-32-bit?lang=en#event_sve_int32_spec), or [SME\_INT32\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8368--SME-INT32-SPEC--Operation-speculatively-executed--SME-32-bit-integer--data-processing?lang=en#event_sme_int32_spec).

It is IMPLEMENTATION DEFINED which 32-bit integer data-processing operations are counted in AArch32 state.

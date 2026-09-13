# ​0x8361, SE_INT8_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 8-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8361--SE-INT8-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-8-bit-integer--data-processing>

##### `0x8361`, SE\_INT8\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 8-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 8-bit integer data-processing operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_INT8\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80E1--ASE-INT8-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-8-bit?lang=en#event_ase_int8_spec), [SVE\_INT8\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80E2--SVE-INT8-SPEC--Integer-operation-speculatively-executed--SVE-8-bit?lang=en#event_sve_int8_spec), or [SME\_INT8\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8360--SME-INT8-SPEC--Operation-speculatively-executed--SME-8-bit-integer--data-processing?lang=en#event_sme_int8_spec).

It is IMPLEMENTATION DEFINED which 8-bit integer data-processing operations are counted in AArch32 state.

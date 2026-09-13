# ​0x8365, SE_INT16_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 16-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8365--SE-INT16-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-16-bit-integer--data-processing>

##### `0x8365`, SE\_INT16\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD 16-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 16-bit integer data-processing operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_INT16\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80E5--ASE-INT16-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-16-bit?lang=en#event_ase_int16_spec), [SVE\_INT16\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80E6--SVE-INT16-SPEC--Integer-operation-speculatively-executed--SVE-16-bit?lang=en#event_sve_int16_spec), or [SME\_INT16\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8364--SME-INT16-SPEC--Operation-speculatively-executed--SME-16-bit-integer--data-processing?lang=en#event_sme_int16_spec).

It is IMPLEMENTATION DEFINED which 16-bit integer data-processing operations are counted in AArch32 state.

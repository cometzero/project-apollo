# ​0x805D, ASE_INT_VREDUCE_SPEC, Integer operation speculatively executed, Advanced SIMD reduction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805D--ASE-INT-VREDUCE-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-reduction>

##### `0x805D`, ASE\_INT\_VREDUCE\_SPEC, Integer operation speculatively executed, Advanced SIMD reduction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) across-vector and pairwise integer reduction operation counted by [ASE\_SVE\_INT\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805F--ASE-SVE-INT-VREDUCE-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-reduction?lang=en#event_ase_sve_int_vreduce_spec) due to any of the following A64 instructions:

- Advanced SIMD: ADDP, ADDV, SADALP, SADDLP, SADDLV, SMAXP, SMAXV, SMINP, SMINV, UADALP, UADDLP, UADDLV, UMAXP, UMAXV, UMINP, or UMINV.

It is IMPLEMENTATION DEFINED which across-vector and pairwise integer reduction operations are counted in AArch32 state.

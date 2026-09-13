# ​0x805E, SVE_INT_VREDUCE_SPEC, Integer operation speculatively executed, SVE reduction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805E--SVE-INT-VREDUCE-SPEC--Integer-operation-speculatively-executed--SVE-reduction>

##### `0x805E`, SVE\_INT\_VREDUCE\_SPEC, Integer operation speculatively executed, SVE reduction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) across-vector and pairwise integer reduction operation counted by [ASE\_SVE\_INT\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805F--ASE-SVE-INT-VREDUCE-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-reduction?lang=en#event_ase_sve_int_vreduce_spec) due to any of the following instructions:

- SVE: ANDV, EORV, ORV, SADDV, SMAXV, SMINV, UADDV, UMAXV, or UMINV.
- SVE2: ADDP, ADDQV, ANDQV, EORQV, ORQV, SADALP, SMAXP, SMAXQV, SMINP, SMINQV, UADALP, UMAXP, UMAXQV, UMINP, or UMINQV.

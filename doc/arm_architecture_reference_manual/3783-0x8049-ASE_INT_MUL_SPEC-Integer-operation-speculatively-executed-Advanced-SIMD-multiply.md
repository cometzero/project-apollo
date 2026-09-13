# ​0x8049, ASE_INT_MUL_SPEC, Integer operation speculatively executed, Advanced SIMD multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8049--ASE-INT-MUL-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-multiply>

##### `0x8049`, ASE\_INT\_MUL\_SPEC, Integer operation speculatively executed, Advanced SIMD multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer multiply or multiply-accumulate operation counted by [ASE\_SVE\_INT\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804B--ASE-SVE-INT-MUL-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-multiply?lang=en#event_ase_sve_int_mul_spec) due to any of the following A64 instructions:

- Advanced SIMD: MLA, MLS, MUL, PMUL, PMULL, PMULL2, SMLAL, SMLAL2, SMLSL, SMLSL2, SMULL, SMULL2, SQDMLAL, SQDMLAL2, SQDMLSL, SQDMLSL2, SQDMULH, SQDMULL, SQDMULL2, SQRDMULH, UMLAL, UMLAL2, UMLSL, UMLSL2, UMULL, or UMULL2.
- When FEAT\_RDM is implemented, Advanced SIMD: SQRDMLAH or SQRDMLSH.

It is IMPLEMENTATION DEFINED which integer multiply or multiply-accumulate operations are counted in AArch32 state.

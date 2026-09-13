# ​0x80FD, ASE_INT_MMLA_SPEC, Integer operation speculatively executed, Advanced SIMD matrix multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FD--ASE-INT-MMLA-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-matrix-multiply>

##### `0x80FD`, ASE\_INT\_MMLA\_SPEC, Integer operation speculatively executed, Advanced SIMD matrix multiply

The counter counts each integer matrix multiply operation counted by [ASE\_SVE\_INT\_MMLA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FF--ASE-SVE-INT-MMLA-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-matrix-multiply?lang=en#event_ase_sve_int_mmla_spec) due to any of the following A64 instructions:

- When FEAT\_I8MM is implemented, Advanced SIMD: SMMLA (vector), UMMLA (vector), or USMMLA (vector).

It is IMPLEMENTATION DEFINED which integer matrix multiply operations are counted in AArch32 state.

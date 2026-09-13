# ​0x80FF, ASE_SVE_INT_MMLA_SPEC, Integer operation speculatively executed, Advanced SIMD or SVE matrix multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FF--ASE-SVE-INT-MMLA-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-matrix-multiply>

##### `0x80FF`, ASE\_SVE\_INT\_MMLA\_SPEC, Integer operation speculatively executed, Advanced SIMD or SVE matrix multiply

The counter counts each integer matrix multiply operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to any of the following A64 instructions:

- When FEAT\_I8MM is implemented, Advanced SIMD: SMMLA (vector), UMMLA (vector), or USMMLA (vector).
- SVE: SMMLA, UMMLA, or USMMLA.

It is IMPLEMENTATION DEFINED which integer matrix multiply operations are counted in AArch32 state.

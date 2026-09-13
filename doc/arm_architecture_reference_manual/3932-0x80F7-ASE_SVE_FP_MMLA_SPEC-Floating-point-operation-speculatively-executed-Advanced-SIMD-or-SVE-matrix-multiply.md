# ​0x80F7, ASE_SVE_FP_MMLA_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE matrix multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F7--ASE-SVE-FP-MMLA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-matrix-multiply>

##### `0x80F7`, ASE\_SVE\_FP\_MMLA\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE matrix multiply

The counter counts each floating-point matrix multiply operation counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) due to any of the following A64 instructions:

- When FEAT\_BF16 is implemented, Advanced SIMD: BFMMLA.
- When FEAT\_F8F16MM is implemented, Advanced SIMD: FMMLA (8-bit floating-point to half-precision) or FMMLA (8-bit floating-point to single-precision).
- SVE: BFMMLA (widening) or FMMLA (non-widening).
- SVE2: FMMLA.

It is IMPLEMENTATION DEFINED which floating-point matrix multiply operations are counted in AArch32 state.

# ​0x80F5, ASE_FP_MMLA_SPEC, Floating-point operation speculatively executed, Advanced SIMD matrix multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F5--ASE-FP-MMLA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-matrix-multiply>

##### `0x80F5`, ASE\_FP\_MMLA\_SPEC, Floating-point operation speculatively executed, Advanced SIMD matrix multiply

The counter counts each floating-point matrix multiply operation counted by [ASE\_SVE\_FP\_MMLA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F7--ASE-SVE-FP-MMLA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-matrix-multiply?lang=en#event_ase_sve_fp_mmla_spec) due to any of the following A64 instructions:

- When FEAT\_BF16 is implemented, Advanced SIMD: BFMMLA.
- When FEAT\_F8F16MM is implemented, Advanced SIMD: FMMLA (8-bit floating-point to half-precision) or FMMLA (8-bit floating-point to single-precision).

It is IMPLEMENTATION DEFINED which floating-point matrix multiply operations are counted in AArch32 state.

# ​0x80F1, ASE_FP_DOT_SPEC, Floating-point operation speculatively executed, Advanced SIMD dot-product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F1--ASE-FP-DOT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-dot-product>

##### `0x80F1`, ASE\_FP\_DOT\_SPEC, Floating-point operation speculatively executed, Advanced SIMD dot-product

The counter counts each dot-product operation counted by [ASE\_SVE\_FP\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F3--ASE-SVE-FP-DOT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-dot-product?lang=en#event_ase_sve_fp_dot_spec) due to any of the following A64 instructions:

- When FEAT\_BF16 is implemented, Advanced SIMD: BFDOT.
- When FEAT\_FP8DOT2 is implemented, Advanced SIMD: FDOT (2-way, by element) or FDOT (2-way, vector).
- When FEAT\_FP8DOT4 is implemented, Advanced SIMD: FDOT (4-way, by element) or FDOT (4-way, vector).

It is IMPLEMENTATION DEFINED which dot-product operations are counted in AArch32 state.

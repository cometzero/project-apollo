# ​0x8375, SE_FP_DOT_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD floating-point dot product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8375--SE-FP-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point-dot-product>

##### `0x8375`, SE\_FP\_DOT\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD floating-point dot product

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point dot product operation counted by [SE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8353--SE-FP-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point--data-processing?lang=en#event_se_fp_spec) due to any of the following A64 instructions:

- When FEAT\_BF16 is implemented, Advanced SIMD: BFDOT.
- When FEAT\_FP8DOT2 is implemented, Advanced SIMD: FDOT (8-bit floating-point to half-precision, by element) or FDOT (8-bit floating-point to half-precision, vector).
- When FEAT\_FP8DOT4 is implemented, Advanced SIMD: FDOT (8-bit floating-point to single-precision, by element) or FDOT (8-bit floating-point to single-precision, vector).
- SVE: BFDOT.
- SVE2: FDOT.
- SME2: BFDOT, BFVDOT, FDOT, FVDOT, FVDOTB, or FVDOTT.

That is, each operation counted by [ASE\_FP\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F1--ASE-FP-DOT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-dot-product?lang=en#event_ase_fp_dot_spec), [SVE\_FP\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F2--SVE-FP-DOT-SPEC--Floating-point-operation-speculatively-executed--SVE-dot-product?lang=en#event_sve_fp_dot_spec), or [SME\_FP\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8374--SME-FP-DOT-SPEC--Operation-speculatively-executed--SME-floating-point-dot-product?lang=en#event_sme_fp_dot_spec).

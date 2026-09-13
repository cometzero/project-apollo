# ​0x80F6, SVE_FP_MMLA_SPEC, Floating-point operation speculatively executed, SVE matrix multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F6--SVE-FP-MMLA-SPEC--Floating-point-operation-speculatively-executed--SVE-matrix-multiply>

##### `0x80F6`, SVE\_FP\_MMLA\_SPEC, Floating-point operation speculatively executed, SVE matrix multiply

The counter counts each floating-point matrix multiply operation counted by [ASE\_SVE\_FP\_MMLA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F7--ASE-SVE-FP-MMLA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-matrix-multiply?lang=en#event_ase_sve_fp_mmla_spec) due to any of the following instructions:

- SVE: BFMMLA (widening) or FMMLA (non-widening).
- SVE2: FMMLA.

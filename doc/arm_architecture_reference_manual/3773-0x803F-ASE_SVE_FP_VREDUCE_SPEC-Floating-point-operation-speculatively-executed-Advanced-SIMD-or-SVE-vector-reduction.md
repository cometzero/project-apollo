# ​0x803F, ASE_SVE_FP_VREDUCE_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE vector reduction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803F--ASE-SVE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-vector-reduction>

##### `0x803F`, ASE\_SVE\_FP\_VREDUCE\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE vector reduction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point reduction operation counted by [ASE\_SVE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8013--ASE-SVE-FP-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_fp_spec) due to any of the following A64 instructions:

- Advanced SIMD: FADDP, FMAXNMP, FMAXNMV, FMAXP, FMAXV, FMINNMP, FMINNMV, FMINP, or FMINV.
- SVE: FADDV, FMAXNMV, FMAXV, FMINNMV, or FMINV.
- SVE2: FADDP, FADDQV, FMAXNMP, FMAXNMQV, FMAXP, FMAXQV, FMINNMP, FMINNMQV, FMINP, or FMINQV.

It is IMPLEMENTATION DEFINED which floating-point reduction operations are counted in AArch32 state.

# ​0x8431, ASE_FP_VREDUCE_SPEC, Floating-point operation speculatively executed, Advanced SIMD pairwise or reduction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8431--ASE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-pairwise-or-reduction>

##### `0x8431`, ASE\_FP\_VREDUCE\_SPEC, Floating-point operation speculatively executed, Advanced SIMD pairwise or reduction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point treewise reduction or pairwise operation counted by [ASE\_SVE\_FP\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803F--ASE-SVE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-vector-reduction?lang=en#event_ase_sve_fp_vreduce_spec) due to any of the following A64 instructions:

- Advanced SIMD: FADDP, FMAXNMP, FMAXNMV, FMAXP, FMAXV, FMINNMP, FMINNMV, FMINP, or FMINV.

> #### Note
>
> Treewise reduction instructions might be executed and counted as multiple pairwise operations.

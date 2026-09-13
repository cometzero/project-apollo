# ​0x803E, SVE_FP_VREDUCE_SPEC, Floating-point operation speculatively executed, SVE pairwise or reduction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803E--SVE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--SVE-pairwise-or-reduction>

##### `0x803E`, SVE\_FP\_VREDUCE\_SPEC, Floating-point operation speculatively executed, SVE pairwise or reduction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point treewise reduction or pairwise operations counted by [ASE\_SVE\_FP\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803F--ASE-SVE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-vector-reduction?lang=en#event_ase_sve_fp_vreduce_spec) due to any of the following instructions:

- SVE: FADDV, FMAXNMV, FMAXV, FMINNMV, or FMINV.
- SVE2: FADDP, FADDQV, FMAXNMP, FMAXNMQV, FMAXP, FMAXQV, FMINNMP, FMINNMQV, FMINP, or FMINQV.

> #### Note
>
> Treewise reduction instructions might be executed and counted as multiple pairwise operations.

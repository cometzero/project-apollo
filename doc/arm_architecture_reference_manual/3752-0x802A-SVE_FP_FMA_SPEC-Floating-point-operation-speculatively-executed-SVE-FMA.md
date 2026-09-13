# ​0x802A, SVE_FP_FMA_SPEC, Floating-point operation speculatively executed, SVE FMA

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802A--SVE-FP-FMA-SPEC--Floating-point-operation-speculatively-executed--SVE-FMA>

##### `0x802A`, SVE\_FP\_FMA\_SPEC, Floating-point operation speculatively executed, SVE FMA

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point fused multiply-add or multiply-subtract operation counted by [ASE\_SVE\_FP\_FMA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802B--ASE-SVE-FP-FMA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-FMA?lang=en#event_ase_sve_fp_fma_spec) due to any of the following instructions:

- SVE: BFMLALB, BFMLALT, FCMLA, FMAD, FMLA, FMLS, FMSB, FNMAD, FNMLA, FNMLS, FNMSB, or FTMAD.
- SVE2: BFMLA, BFMLS, BFMLSLB, BFMLSLT, FMLALB, FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT, FMLALT, FMLSLB, or FMLSLT.

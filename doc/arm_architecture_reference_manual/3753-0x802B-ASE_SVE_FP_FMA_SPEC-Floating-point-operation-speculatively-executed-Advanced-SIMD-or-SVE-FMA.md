# ​0x802B, ASE_SVE_FP_FMA_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE FMA

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802B--ASE-SVE-FP-FMA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-FMA>

##### `0x802B`, ASE\_SVE\_FP\_FMA\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE FMA

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point fused multiply-add or multiply-subtract operation counted by [FP\_FMA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8028--FP-FMA-SPEC--Floating-point-operation-speculatively-executed--FMA?lang=en#event_fp_fma_spec) due to any of the following A64 instructions:

- Advanced SIMD: FMLA or FMLS.
- When FEAT\_BF16 is implemented, Advanced SIMD: BFMLALB or BFMLALT.
- When FEAT\_FCMA is implemented, Advanced SIMD: FCMLA.
- When FEAT\_FP8FMA is implemented, Advanced SIMD: FMLALB, FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT, or FMLALT.
- When FEAT\_FHM is implemented, Advanced SIMD: FMLAL, FMLAL2, FMLSL, or FMLSL2.
- SVE: BFMLALB, BFMLALT, FCMLA, FMAD, FMLA, FMLS, FMSB, FNMAD, FNMLA, FNMLS, FNMSB, or FTMAD.
- SVE2: BFMLA, BFMLS, BFMLSLB, BFMLSLT, FMLALB, FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT, FMLALT, FMLSLB, or FMLSLT.

It is IMPLEMENTATION DEFINED which floating-point fused multiply-add or multiply-subtract operations are counted in AArch32 state.

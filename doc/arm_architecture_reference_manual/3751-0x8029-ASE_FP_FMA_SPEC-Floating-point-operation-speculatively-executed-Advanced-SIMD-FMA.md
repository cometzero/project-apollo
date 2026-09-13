# ​0x8029, ASE_FP_FMA_SPEC, Floating-point operation speculatively executed, Advanced SIMD FMA

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8029--ASE-FP-FMA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-FMA>

##### `0x8029`, ASE\_FP\_FMA\_SPEC, Floating-point operation speculatively executed, Advanced SIMD FMA

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point fused multiply-add or multiply-subtract operation counted by [ASE\_SVE\_FP\_FMA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802B--ASE-SVE-FP-FMA-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-FMA?lang=en#event_ase_sve_fp_fma_spec) due to any of the following A64 instructions:

- Advanced SIMD: FMLA or FMLS.
- When FEAT\_BF16 is implemented, Advanced SIMD: BFMLALB or BFMLALT.
- When FEAT\_FCMA is implemented, Advanced SIMD: FCMLA.
- When FEAT\_FP8FMA is implemented, Advanced SIMD: FMLALB, FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT, or FMLALT.
- When FEAT\_FHM is implemented, Advanced SIMD: FMLAL, FMLAL2, FMLSL, or FMLSL2.

It is IMPLEMENTATION DEFINED which floating-point fused multiply-add or multiply-subtract operations are counted in AArch32 state.
